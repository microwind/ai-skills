# GraphQL API参考文档

## GraphQL API概述

### 什么是GraphQL API
GraphQL是一种用于API的查询语言和运行时环境，由Facebook开发并于2015年开源。它提供了一种更高效、强大和灵活的替代REST API的方式，允许客户端精确地请求所需的数据，减少了过度获取和不足获取的问题。该技能涵盖了Schema设计、解析器实现、查询优化、安全防护、订阅支持等功能，帮助开发者构建现代化、高性能的GraphQL API服务。

### 主要功能
- **灵活查询**: 客户端可以精确指定需要的数据字段，避免过度获取
- **类型系统**: 强类型系统提供API文档和验证能力
- **实时订阅**: 支持WebSocket等实时数据推送
- **性能优化**: 内置查询复杂度分析、数据加载器、缓存等优化机制
- **安全防护**: 提供认证授权、输入验证、频率限制等安全功能

## GraphQL引擎核心

### GraphQL服务器
```python
# graphql_server.py
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import jwt
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor

# GraphQL相关库
try:
    import graphql
    from graphql import (
        GraphQLSchema, GraphQLObjectType, GraphQLField,
        GraphQLArgument, GraphQLNonNull, GraphQLList,
        GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean,
        GraphQLID, GraphQLInterfaceType, GraphQLUnionType,
        GraphQLScalarType, GraphQLResolveInfo, validate,
        execute, parse, build_schema
    )
    from graphql.execution.utils import default_field_resolver
    from graphql.error import GraphQLSyntaxError, GraphQLError
except ImportError:
    print("需要安装GraphQL库: pip install graphql-core")
    exit(1)

class QueryComplexity(Enum):
    LOW = 1
    MEDIUM = 5
    HIGH = 10
    VERY_HIGH = 20

@dataclass
class GraphQLConfig:
    # 基础配置
    debug: bool = False
    introspection: bool = True
    playground: bool = True
    
    # 性能配置
    max_complexity: int = 100
    max_depth: int = 10
    enable_query_cache: bool = True
    cache_ttl: int = 300
    
    # 安全配置
    enable_auth: bool = True
    auth_header: str = "Authorization"
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # 限制配置
    enable_rate_limit: bool = True
    rate_limit_per_minute: int = 60
    enable_query_whitelist: bool = False
    query_whitelist: List[str] = field(default_factory=list)
    
    # 监控配置
    enable_metrics: bool = True
    metrics_interval: int = 60
    enable_query_logging: bool = True

@dataclass
class QueryContext:
    user_id: Optional[str] = None
    user_roles: List[str] = field(default_factory=list)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = field(default_factory=time.time)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class QueryMetrics:
    query_hash: str
    query_string: str
    execution_time: float
    complexity_score: int
    depth: int
    user_id: Optional[str]
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)

class DataLoader:
    """数据加载器"""
    
    def __init__(self, batch_load_fn: Callable, max_batch_size: int = 50, cache: bool = True):
        self.batch_load_fn = batch_load_fn
        self.max_batch_size = max_batch_size
        self.cache = {} if cache else None
        self.queue = []
        self.dispatch_timer = None
        self.dispatch_lock = threading.Lock()
    
    def load(self, key: Any) -> Any:
        """加载单个数据"""
        if self.cache is not None and key in self.cache:
            return self.cache[key]
        
        promise = asyncio.Future() if asyncio.get_event_loop().is_running() else None
        self.queue.append((key, promise))
        
        if self.dispatch_timer is None:
            self.dispatch_timer = threading.Timer(0.01, self._dispatch)
            self.dispatch_timer.start()
        
        return promise if promise else self._load_sync(key)
    
    def load_many(self, keys: List[Any]) -> List[Any]:
        """批量加载数据"""
        if self.cache is not None:
            cached = [self.cache.get(key) for key in keys]
            if all(cached):
                return cached
        
        promises = []
        for key in keys:
            promise = asyncio.Future() if asyncio.get_event_loop().is_running() else None
            self.queue.append((key, promise))
            promises.append(promise)
        
        if self.dispatch_timer is None:
            self.dispatch_timer = threading.Timer(0.01, self._dispatch)
            self.dispatch_timer.start()
        
        return promises if any(promises) else [self._load_sync(key) for key in keys]
    
    def _dispatch(self):
        """分批处理"""
        with self.dispatch_lock:
            if not self.queue:
                self.dispatch_timer = None
                return
            
            batch = self.queue[:self.max_batch_size]
            self.queue = self.queue[self.max_batch_size:]
            self.dispatch_timer = None
            
            if self.queue:
                self.dispatch_timer = threading.Timer(0.01, self._dispatch)
                self.dispatch_timer.start()
        
        keys = [key for key, _ in batch]
        promises = [promise for _, promise in batch if promise is not None]
        
        try:
            if asyncio.get_event_loop().is_running():
                # 异步处理
                asyncio.create_task(self._dispatch_async(keys, promises))
            else:
                # 同步处理
                results = self.batch_load_fn(keys)
                self._resolve_batch(batch, results)
        except Exception as e:
            self._reject_batch(batch, e)
    
    async def _dispatch_async(self, keys: List[Any], promises: List):
        """异步分派处理"""
        try:
            if asyncio.iscoroutinefunction(self.batch_load_fn):
                results = await self.batch_load_fn(keys)
            else:
                results = self.batch_load_fn(keys)
            self._resolve_batch([(key, promise) for key, promise in zip(keys, promises)], results)
        except Exception as e:
            self._reject_batch([(key, promise) for key, promise in zip(keys, promises)], e)
    
    def _load_sync(self, key: Any) -> Any:
        """同步加载"""
        try:
            result = self.batch_load_fn([key])
            if self.cache is not None:
                self.cache[key] = result[0]
            return result[0]
        except Exception as e:
            raise e
    
    def _resolve_batch(self, batch: List, results: List):
        """解析批量结果"""
        for (key, promise), result in zip(batch, results):
            if self.cache is not None:
                self.cache[key] = result
            
            if promise is not None and asyncio.get_event_loop().is_running():
                if promise.done():
                    continue
                promise.set_result(result)
    
    def _reject_batch(self, batch: List, error: Exception):
        """拒绝批量结果"""
        for key, promise in batch:
            if promise is not None and asyncio.get_event_loop().is_running():
                if promise.done():
                    continue
                promise.set_exception(error)

class QueryComplexityAnalyzer:
    """查询复杂度分析器"""
    
    def __init__(self, max_complexity: int = 100):
        self.max_complexity = max_complexity
        self.field_complexity = {
            GraphQLString: 1,
            GraphQLInt: 1,
            GraphQLFloat: 1,
            GraphQLBoolean: 1,
            GraphQLID: 1,
        }
    
    def analyze(self, document: Any, schema: GraphQLSchema) -> int:
        """分析查询复杂度"""
        complexity = 0
        
        for definition in document.definitions:
            if hasattr(definition, 'selection_set'):
                complexity += self._analyze_selection_set(
                    definition.selection_set, 
                    schema, 
                    0
                )
        
        return complexity
    
    def _analyze_selection_set(self, selection_set: Any, schema: GraphQLSchema, depth: int) -> int:
        """分析选择集复杂度"""
        complexity = 0
        
        for selection in selection_set.selections:
            if hasattr(selection, 'field'):
                complexity += self._analyze_field(selection.field, schema, depth)
        
        return complexity
    
    def _analyze_field(self, field: Any, schema: GraphQLSchema, depth: int) -> int:
        """分析字段复杂度"""
        field_name = field.name.value
        
        # 获取字段类型
        parent_type = self._get_parent_type(field, schema)
        if parent_type and field_name in parent_type.fields:
            field_def = parent_type.fields[field_name]
            field_type = field_def.type
            
            # 计算基础复杂度
            base_complexity = self._get_type_complexity(field_type)
            
            # 计算嵌套复杂度
            nested_complexity = 0
            if hasattr(field, 'selection_set') and field.selection_set:
                nested_complexity = self._analyze_selection_set(
                    field.selection_set, 
                    schema, 
                    depth + 1
                )
            
            # 计算列表复杂度
            list_multiplier = 1
            if isinstance(field_type, GraphQLList):
                list_multiplier = 10  # 假设列表平均有10个元素
            
            return (base_complexity + nested_complexity) * list_multiplier
        
        return 1
    
    def _get_type_complexity(self, field_type: Any) -> int:
        """获取类型复杂度"""
        if isinstance(field_type, GraphQLNonNull):
            return self._get_type_complexity(field_type.of_type)
        elif isinstance(field_type, GraphQLList):
            return self._get_type_complexity(field_type.of_type)
        elif isinstance(field_type, (GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID)):
            return self.field_complexity.get(field_type, 1)
        elif isinstance(field_type, GraphQLObjectType):
            return 1
        else:
            return 1
    
    def _get_parent_type(self, field: Any, schema: GraphQLSchema) -> Optional[GraphQLObjectType]:
        """获取父类型"""
        # 这里需要根据查询上下文确定父类型
        # 简化实现，实际需要更复杂的逻辑
        return schema.query_type

class GraphQLAuthMiddleware:
    """GraphQL认证中间件"""
    
    def __init__(self, config: GraphQLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self, request_headers: Dict[str, str]) -> Optional[QueryContext]:
        """认证请求"""
        if not self.config.enable_auth:
            return QueryContext()
        
        auth_header = request_headers.get(self.config.auth_header)
        if not auth_header:
            return None
        
        try:
            # 提取Bearer token
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
            
            # 验证JWT
            payload = jwt.decode(
                token, 
                self.config.jwt_secret, 
                algorithms=[self.config.jwt_algorithm]
            )
            
            return QueryContext(
                user_id=payload.get('user_id'),
                user_roles=payload.get('roles', []),
                ip_address=request_headers.get('X-Forwarded-For'),
                user_agent=request_headers.get('User-Agent')
            )
        
        except jwt.ExpiredSignatureError:
            self.logger.warning("JWT token已过期")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"无效的JWT token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"认证失败: {e}")
            return None

class GraphQLRateLimitMiddleware:
    """GraphQL频率限制中间件"""
    
    def __init__(self, config: GraphQLConfig):
        self.config = config
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def check_rate_limit(self, context: QueryContext) -> bool:
        """检查频率限制"""
        if not self.config.enable_rate_limit:
            return True
        
        identifier = context.user_id or context.ip_address
        if not identifier:
            return True
        
        current_time = time.time()
        
        with self.lock:
            # 清理过期请求
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < 60  # 1分钟内
            ]
            
            # 检查请求数量
            if len(self.requests[identifier]) >= self.config.rate_limit_per_minute:
                self.logger.warning(f"频率限制触发: {identifier}")
                return False
            
            # 记录当前请求
            self.requests[identifier].append(current_time)
        
        return True

class GraphQLServer:
    """GraphQL服务器"""
    
    def __init__(self, config: GraphQLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.schema: Optional[GraphQLSchema] = None
        self.auth_middleware = GraphQLAuthMiddleware(config)
        self.rate_limit_middleware = GraphQLRateLimitMiddleware(config)
        self.complexity_analyzer = QueryComplexityAnalyzer(config.max_complexity)
        self.metrics: List[QueryMetrics] = []
        self.query_cache: Dict[str, Any] = {}
        self.data_loaders: Dict[str, DataLoader] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def set_schema(self, schema: GraphQLSchema):
        """设置GraphQL Schema"""
        self.schema = schema
        self.logger.info("GraphQL Schema已设置")
    
    def execute_query(self, query: str, variables: Dict[str, Any] = None, 
                    context: Optional[QueryContext] = None,
                    headers: Dict[str, str] = None) -> Dict[str, Any]:
        """执行GraphQL查询"""
        start_time = time.time()
        
        try:
            # 认证
            if context is None:
                context = self.auth_middleware.authenticate(headers or {})
                if context is None:
                    return {
                        'errors': [{'message': '认证失败'}],
                        'data': None
                    }
            
            # 频率限制
            if not self.rate_limit_middleware.check_rate_limit(context):
                return {
                    'errors': [{'message': '请求过于频繁'}],
                    'data': None
                }
            
            # 解析查询
            try:
                document = parse(query)
            except GraphQLSyntaxError as e:
                return {
                    'errors': [{'message': f'查询语法错误: {str(e)}'}],
                    'data': None
                }
            
            # 验证查询
            validation_errors = validate(self.schema, document)
            if validation_errors:
                return {
                    'errors': [{'message': f'验证错误: {error.message}'} for error in validation_errors],
                    'data': None
                }
            
            # 复杂度分析
            complexity = self.complexity_analyzer.analyze(document, self.schema)
            if complexity > self.config.max_complexity:
                return {
                    'errors': [{'message': f'查询复杂度过高: {complexity} > {self.config.max_complexity}'}],
                    'data': None
                }
            
            # 查询缓存
            query_hash = hashlib.md5(query.encode()).hexdigest()
            cache_key = f"{query_hash}:{json.dumps(variables or {}, sort_keys=True)}"
            
            if self.config.enable_query_cache and cache_key in self.query_cache:
                cached_result = self.query_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.config.cache_ttl:
                    self.logger.info(f"查询缓存命中: {query_hash}")
                    return cached_result['result']
            
            # 执行查询
            result = execute(
                self.schema,
                document,
                variable_values=variables,
                context_value=context,
                middleware=self._get_middleware()
            )
            
            # 处理结果
            execution_time = time.time() - start_time
            result_dict = {
                'data': result.data,
                'errors': [error.formatted for error in result.errors] if result.errors else None,
                'extensions': {
                    'complexity': complexity,
                    'executionTime': execution_time
                }
            }
            
            # 缓存结果
            if self.config.enable_query_cache:
                self.query_cache[cache_key] = {
                    'result': result_dict,
                    'timestamp': time.time()
                }
            
            # 记录指标
            if self.config.enable_metrics:
                self._record_metrics(query, execution_time, complexity, context, result.errors)
            
            return result_dict
        
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            return {
                'errors': [{'message': f'服务器错误: {str(e)}'}],
                'data': None
            }
    
    def _get_middleware(self) -> List[Callable]:
        """获取中间件"""
        middleware = []
        
        # 添加自定义中间件
        if self.config.enable_metrics:
            middleware.append(self._metrics_middleware)
        
        return middleware
    
    def _metrics_middleware(self, next, root, info: GraphQLResolveInfo, **args):
        """指标中间件"""
        start_time = time.time()
        
        try:
            result = next(root, info, **args)
            execution_time = time.time() - start_time
            
            # 记录字段级指标
            if self.config.enable_query_logging:
                self.logger.debug(f"字段执行: {info.field_name}, 耗时: {execution_time:.3f}s")
            
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"字段执行失败: {info.field_name}, 耗时: {execution_time:.3f}s, 错误: {e}")
            raise
    
    def _record_metrics(self, query: str, execution_time: float, 
                       complexity: int, context: QueryContext, errors: List):
        """记录查询指标"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        metric = QueryMetrics(
            query_hash=query_hash,
            query_string=query,
            execution_time=execution_time,
            complexity_score=complexity,
            depth=self._calculate_query_depth(query),
            user_id=context.user_id,
            errors=[str(error) for error in errors] if errors else []
        )
        
        self.metrics.append(metric)
        
        # 限制指标数量
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-5000:]
    
    def _calculate_query_depth(self, query: str) -> int:
        """计算查询深度"""
        try:
            document = parse(query)
            return self._calculate_depth_recursive(document.definitions, 0)
        except:
            return 0
    
    def _calculate_depth_recursive(self, definitions: List, current_depth: int) -> int:
        """递归计算深度"""
        max_depth = current_depth
        
        for definition in definitions:
            if hasattr(definition, 'selection_set'):
                depth = self._calculate_depth_recursive(
                    definition.selection_set.selections, 
                    current_depth + 1
                )
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def get_data_loader(self, name: str, batch_load_fn: Callable) -> DataLoader:
        """获取数据加载器"""
        if name not in self.data_loaders:
            self.data_loaders[name] = DataLoader(batch_load_fn)
        return self.data_loaders[name]
    
    def get_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取查询指标"""
        return [asdict(metric) for metric in self.metrics[-limit:]]
    
    def clear_cache(self):
        """清空缓存"""
        self.query_cache.clear()
        self.logger.info("查询缓存已清空")

# 示例Schema定义
def create_sample_schema() -> GraphQLSchema:
    """创建示例Schema"""
    
    # 定义数据加载器
    user_loader = DataLoader(load_users_batch)
    post_loader = DataLoader(load_posts_batch)
    
    # 定义标量类型
    DateTime = GraphQLScalarType(
        name="DateTime",
        serialize=lambda value: value.isoformat() if isinstance(value, datetime) else value,
        parse_value=lambda value: datetime.fromisoformat(value) if isinstance(value, str) else value,
        parse_literal=lambda ast: datetime.fromisoformat(ast.value) if hasattr(ast, 'value') else None
    )
    
    # 定义对象类型
    UserType = GraphQLObjectType(
        name="User",
        fields=lambda: {
            'id': GraphQLField(GraphQLNonNull(GraphQLID)),
            'name': GraphQLField(GraphQLNonNull(GraphQLString)),
            'email': GraphQLField(GraphQLString),
            'createdAt': GraphQLField(DateTime),
            'posts': GraphQLField(
                GraphQLList(PostType),
                resolve=lambda user, info, **args: 
                    post_loader.load_many([post['id'] for post in get_user_posts(user['id'])])
            )
        }
    )
    
    PostType = GraphQLObjectType(
        name="Post",
        fields=lambda: {
            'id': GraphQLField(GraphQLNonNull(GraphQLID)),
            'title': GraphQLField(GraphQLNonNull(GraphQLString)),
            'content': GraphQLField(GraphQLString),
            'author': GraphQLField(
                UserType,
                resolve=lambda post, info, **args: user_loader.load(post['author_id'])
            ),
            'createdAt': GraphQLField(DateTime)
        }
    )
    
    # 定义查询类型
    QueryType = GraphQLObjectType(
        name="Query",
        fields=lambda: {
            'user': GraphQLField(
                UserType,
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=lambda root, info, id: user_loader.load(id)
            ),
            'users': GraphQLField(
                GraphQLList(UserType),
                resolve=lambda root, info: user_loader.load_many(get_all_user_ids())
            ),
            'post': GraphQLField(
                PostType,
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=lambda root, info, id: post_loader.load(id)
            ),
            'posts': GraphQLField(
                GraphQLList(PostType),
                resolve=lambda root, info: post_loader.load_many(get_all_post_ids())
            )
        }
    )
    
    # 定义变更类型
    MutationType = GraphQLObjectType(
        name="Mutation",
        fields=lambda: {
            'createUser': GraphQLField(
                UserType,
                args={
                    'name': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'email': GraphQLArgument(GraphQLNonNull(GraphQLString))
                },
                resolve=lambda root, info, name, email: create_user(name, email)
            ),
            'createPost': GraphQLField(
                PostType,
                args={
                    'title': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'content': GraphQLArgument(GraphQLString),
                    'authorId': GraphQLArgument(GraphQLNonNull(GraphQLID))
                },
                resolve=lambda root, info, title, content, authorId: create_post(title, content, authorId)
            )
        }
    )
    
    # 定义订阅类型
    SubscriptionType = GraphQLObjectType(
        name="Subscription",
        fields=lambda: {
            'postCreated': GraphQLField(
                PostType,
                resolve=lambda post, info: post
            )
        }
    )
    
    return GraphQLSchema(
        query=QueryType,
        mutation=MutationType,
        subscription=SubscriptionType
    )

# 示例数据加载函数
def load_users_batch(user_ids: List[str]) -> List[Dict[str, Any]]:
    """批量加载用户数据"""
    # 模拟数据库查询
    users = []
    for user_id in user_ids:
        users.append({
            'id': user_id,
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com',
            'createdAt': datetime.now()
        })
    return users

def load_posts_batch(post_ids: List[str]) -> List[Dict[str, Any]]:
    """批量加载文章数据"""
    posts = []
    for post_id in post_ids:
        posts.append({
            'id': post_id,
            'title': f'Post {post_id}',
            'content': f'Content of post {post_id}',
            'author_id': '1',
            'createdAt': datetime.now()
        })
    return posts

# 示例数据操作函数
def get_all_user_ids() -> List[str]:
    """获取所有用户ID"""
    return ['1', '2', '3']

def get_all_post_ids() -> List[str]:
    """获取所有文章ID"""
    return ['1', '2', '3', '4', '5']

def get_user_posts(user_id: str) -> List[Dict[str, Any]]:
    """获取用户文章"""
    return [
        {'id': '1', 'title': 'Post 1'},
        {'id': '2', 'title': 'Post 2'}
    ]

def create_user(name: str, email: str) -> Dict[str, Any]:
    """创建用户"""
    user_id = str(int(time.time()))
    return {
        'id': user_id,
        'name': name,
        'email': email,
        'createdAt': datetime.now()
    }

def create_post(title: str, content: str, author_id: str) -> Dict[str, Any]:
    """创建文章"""
    post_id = str(int(time.time()))
    return {
        'id': post_id,
        'title': title,
        'content': content,
        'author_id': author_id,
        'createdAt': datetime.now()
    }

# 使用示例
# 配置GraphQL服务器
config = GraphQLConfig(
    debug=True,
    introspection=True,
    playground=True,
    max_complexity=50,
    max_depth=5,
    enable_query_cache=True,
    cache_ttl=300,
    enable_auth=True,
    jwt_secret="your-secret-key",
    jwt_algorithm="HS256",
    jwt_expiration=3600,
    enable_rate_limit=True,
    rate_limit_per_minute=60,
    enable_metrics=True,
    metrics_interval=60,
    enable_query_logging=True
)

# 创建服务器
server = GraphQLServer(config)

# 设置Schema
schema = create_sample_schema()
server.set_schema(schema)

# 测试查询
test_query = """
query GetUser($userId: ID!) {
    user(id: $userId) {
        id
        name
        email
        posts {
            id
            title
            content
        }
    }
}
"""

variables = {"userId": "1"}

# 模拟认证头
headers = {"Authorization": "Bearer valid.jwt.token"}

# 执行查询
result = server.execute_query(test_query, variables, headers=headers)

print("GraphQL查询结果:")
print(json.dumps(result, indent=2, default=str))

# 获取指标
metrics = server.get_metrics(limit=10)
print(f"\n查询指标: {len(metrics)} 条记录")

# 测试变更
mutation_query = """
mutation CreateUser($name: String!, $email: String!) {
    createUser(name: $name, email: $email) {
        id
        name
        email
    }
}
"""

mutation_variables = {"name": "New User", "email": "newuser@example.com"}
mutation_result = server.execute_query(mutation_query, mutation_variables, headers=headers)

print("\nGraphQL变更结果:")
print(json.dumps(mutation_result, indent=2, default=str))
```

## 参考资源

### GraphQL官方资源
- [GraphQL官方文档](https://graphql.org/)
- [GraphQL规范](https://spec.graphql.org/)
- [GraphQL最佳实践](https://graphql.org/learn/best-practices/)
- [GraphQL安全指南](https://graphql.org/learn/thinking-in-graphs/)

### Python GraphQL库
- [Graphene-Python](https://graphene-python.org/)
- [Ariadne](https://ariadnegraphql.org/)
- [Strawberry](https://strawberry-graphql.github.io/)
- [GraphQL-Core](https://github.com/graphql-python/graphql-core)

### 性能优化
- [DataLoader规范](https://github.com/graphql/graphql-js/blob/main/src/utilities/DataLoader.js)
- [查询复杂度分析](https://github.com/ivome/graphql-query-complexity)
- [GraphQL缓存策略](https://www.apollographql.com/docs/react/caching/)
- [查询优化技巧](https://www.howtographql.com/advanced/)

### 安全防护
- [GraphQL安全最佳实践](https://owasp.org/www-project-graphql-security/)
- [认证授权指南](https://www.apollographql.com/docs/react/security/authentication)
- [输入验证](https://graphql.org/learn/validating-queries/)
- [频率限制](https://www.apollographql.com/docs/apollo-server/performance/rate-limiting/)

### 监控调试
- [Apollo Studio](https://www.apollographql.com/docs/studio/)
- [GraphQL Playground](https://github.com/prisma-labs/graphql-playground)
- [查询分析工具](https://github.com/apollographql/apollo-tooling)
- [性能监控](https://www.apollographql.com/docs/apollo-server/monitoring/)
