---
name: NoSQL数据库应用
description: "当设计NoSQL数据库时，选择合适的数据库类型，设计数据模型，优化查询性能。处理分布式事务，实现数据一致性，和扩展性设计。"
license: MIT
---

# NoSQL数据库应用技能

## 概述
NoSQL数据库是处理大规模数据、高并发访问、灵活数据结构的重要解决方案。不当的NoSQL设计会导致性能问题、数据不一致、扩展困难。

**核心原则**: 好的NoSQL设计应该数据模型合理、查询高效、扩展性强、一致性可控。坏的NoSQL设计会查询缓慢、数据冗余、扩展困难。

## 何时使用

**始终:**
- 处理大规模数据时
- 需要高并发访问时
- 数据结构不固定时
- 需要水平扩展时
- 快速迭代开发时
- 地理分布部署时

**触发短语:**
- "NoSQL数据库设计"
- "MongoDB数据模型"
- "Redis缓存策略"
- "Cassandra集群配置"
- "Elasticsearch搜索优化"
- "分布式数据库选择"

## NoSQL数据库类型

### 文档数据库
- MongoDB
- CouchDB
- Amazon DocumentDB
- Azure Cosmos DB

### 键值数据库
- Redis
- DynamoDB
- Riak
- Aerospike

### 列族数据库
- Cassandra
- HBase
- Bigtable
- ScyllaDB

### 图数据库
- Neo4j
- Amazon Neptune
- ArangoDB
- OrientDB

### 搜索数据库
- Elasticsearch
- Solr
- OpenSearch
- Typesense

## 常见NoSQL问题

### 数据模型设计不当
```
问题:
文档数据库中过度嵌套，导致查询性能差

错误示例:
- 文档深度超过5层
- 数组元素过多
- 频繁更新的嵌套字段
- 缺少合理的索引设计

解决方案:
1. 合理设计文档结构
2. 控制嵌套深度
3. 使用引用代替嵌套
4. 优化索引策略
```

### 查询性能问题
```
问题:
NoSQL数据库查询性能差，响应时间长

错误示例:
- 缺少合适的索引
- 全表扫描查询
- 复杂聚合查询
- 不当的分页实现

解决方案:
1. 设计合理的索引
2. 优化查询语句
3. 使用聚合管道
4. 实现高效分页
```

### 数据一致性问题
```
问题:
分布式环境下数据一致性难以保证

错误示例:
- 缺少一致性策略
- 事务处理不当
- 缓存与数据库不一致
- 并发更新冲突

解决方案:
1. 选择合适的一致性级别
2. 实现分布式事务
3. 设计缓存更新策略
4. 处理并发冲突
```

### 扩展性问题
```
问题:
数据库扩展困难，无法应对增长

错误示例:
- 分片策略不当
- 热点数据集中
- 跨分片查询过多
- 负载不均衡

解决方案:
1. 合理设计分片键
2. 实现数据分片
3. 优化跨分片查询
4. 实现负载均衡
```

## 代码实现示例

### MongoDB文档设计器
```python
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

class DocumentType(Enum):
    """文档类型"""
    USER = "user"
    PRODUCT = "product"
    ORDER = "order"
    LOG = "log"
    CONFIG = "config"

class IndexType(Enum):
    """索引类型"""
    SINGLE = "single"
    COMPOUND = "compound"
    TEXT = "text"
    HASHED = "hashed"
    GEOSPATIAL = "geospatial"

@dataclass
class FieldDefinition:
    """字段定义"""
    name: str
    data_type: str
    required: bool = False
    index: bool = False
    unique: bool = False
    default: Any = None
    validation: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IndexDefinition:
    """索引定义"""
    name: str
    fields: List[str]
    index_type: IndexType
    unique: bool = False
    sparse: bool = False
    expire_after: Optional[int] = None

@dataclass
class DocumentSchema:
    """文档模式"""
    collection_name: str
    document_type: DocumentType
    fields: List[FieldDefinition]
    indexes: List[IndexDefinition] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)

class MongoDBDocumentDesigner:
    def __init__(self):
        self.schemas: Dict[str, DocumentSchema] = {}
        self.design_patterns = {
            'embedding': self._design_embedding_pattern,
            'referencing': self._design_referencing_pattern,
            'bucket': self._design_bucket_pattern,
            'schema_versioning': self._design_schema_versioning_pattern,
        }
    
    def create_schema(self, schema: DocumentSchema) -> bool:
        """创建文档模式"""
        try:
            # 验证模式定义
            validation_result = self._validate_schema(schema)
            if not validation_result['valid']:
                print(f"模式验证失败: {validation_result['errors']}")
                return False
            
            # 保存模式
            self.schemas[schema.collection_name] = schema
            
            # 生成索引创建语句
            index_commands = self._generate_index_commands(schema)
            
            # 生成验证规则
            validation_command = self._generate_validation_command(schema)
            
            print(f"成功创建模式: {schema.collection_name}")
            print(f"索引命令: {json.dumps(index_commands, indent=2, ensure_ascii=False)}")
            print(f"验证规则: {validation_command}")
            
            return True
            
        except Exception as e:
            print(f"创建模式失败: {e}")
            return False
    
    def design_user_schema(self) -> DocumentSchema:
        """设计用户文档模式"""
        fields = [
            FieldDefinition(
                name="_id",
                data_type="ObjectId",
                required=True
            ),
            FieldDefinition(
                name="username",
                data_type="string",
                required=True,
                unique=True,
                index=True,
                validation={"minLength": 3, "maxLength": 50}
            ),
            FieldDefinition(
                name="email",
                data_type="string",
                required=True,
                unique=True,
                index=True,
                validation={"pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"}
            ),
            FieldDefinition(
                name="profile",
                data_type="object",
                required=False,
                default={}
            ),
            FieldDefinition(
                name="preferences",
                data_type="object",
                required=False,
                default={}
            ),
            FieldDefinition(
                name="created_at",
                data_type="date",
                required=True,
                default=datetime.now
            ),
            FieldDefinition(
                name="updated_at",
                data_type="date",
                required=True,
                default=datetime.now
            ),
            FieldDefinition(
                name="status",
                data_type="string",
                required=True,
                default="active",
                index=True,
                validation={"enum": ["active", "inactive", "suspended"]}
            )
        ]
        
        indexes = [
            IndexDefinition(
                name="idx_username",
                fields=["username"],
                index_type=IndexType.SINGLE,
                unique=True
            ),
            IndexDefinition(
                name="idx_email",
                fields=["email"],
                index_type=IndexType.SINGLE,
                unique=True
            ),
            IndexDefinition(
                name="idx_status_created",
                fields=["status", "created_at"],
                index_type=IndexType.COMPOUND
            )
        ]
        
        return DocumentSchema(
            collection_name="users",
            document_type=DocumentType.USER,
            fields=fields,
            indexes=indexes
        )
    
    def design_order_schema(self) -> DocumentSchema:
        """设计订单文档模式"""
        fields = [
            FieldDefinition(
                name="_id",
                data_type="ObjectId",
                required=True
            ),
            FieldDefinition(
                name="order_number",
                data_type="string",
                required=True,
                unique=True,
                index=True
            ),
            FieldDefinition(
                name="user_id",
                data_type="ObjectId",
                required=True,
                index=True
            ),
            FieldDefinition(
                name="items",
                data_type="array",
                required=True,
                validation={"minItems": 1}
            ),
            FieldDefinition(
                name="total_amount",
                data_type="decimal",
                required=True,
                validation={"minimum": 0}
            ),
            FieldDefinition(
                name="status",
                data_type="string",
                required=True,
                index=True,
                validation={"enum": ["pending", "confirmed", "shipped", "delivered", "cancelled"]}
            ),
            FieldDefinition(
                name="shipping_address",
                data_type="object",
                required=True
            ),
            FieldDefinition(
                name="payment_info",
                data_type="object",
                required=False
            ),
            FieldDefinition(
                name="created_at",
                data_type="date",
                required=True,
                default=datetime.now
            ),
            FieldDefinition(
                name="updated_at",
                data_type="date",
                required=True,
                default=datetime.now
            )
        ]
        
        indexes = [
            IndexDefinition(
                name="idx_order_number",
                fields=["order_number"],
                index_type=IndexType.SINGLE,
                unique=True
            ),
            IndexDefinition(
                name="idx_user_id",
                fields=["user_id"],
                index_type=IndexType.SINGLE
            ),
            IndexDefinition(
                name="idx_status_created",
                fields=["status", "created_at"],
                index_type=IndexType.COMPOUND
            ),
            IndexDefinition(
                name="idx_user_status",
                fields=["user_id", "status"],
                index_type=IndexType.COMPOUND
            )
        ]
        
        return DocumentSchema(
            collection_name="orders",
            document_type=DocumentType.ORDER,
            fields=fields,
            indexes=indexes
        )
    
    def optimize_document_structure(self, collection_name: str, query_patterns: List[str]) -> Dict[str, Any]:
        """优化文档结构"""
        if collection_name not in self.schemas:
            return {"error": "集合不存在"}
        
        schema = self.schemas[collection_name]
        optimizations = []
        
        # 分析查询模式
        for pattern in query_patterns:
            optimization = self._analyze_query_pattern(schema, pattern)
            optimizations.append(optimization)
        
        # 生成优化建议
        recommendations = self._generate_optimization_recommendations(schema, optimizations)
        
        return {
            "collection_name": collection_name,
            "query_patterns": query_patterns,
            "optimizations": optimizations,
            "recommendations": recommendations
        }
    
    def _validate_schema(self, schema: DocumentSchema) -> Dict[str, Any]:
        """验证模式定义"""
        errors = []
        warnings = []
        
        # 检查必需字段
        if not schema.fields:
            errors.append("至少需要一个字段")
        
        # 检查字段定义
        field_names = [field.name for field in schema.fields]
        if "_id" not in field_names:
            warnings.append("建议包含_id字段")
        
        # 检查索引定义
        for index in schema.indexes:
            for field in index.fields:
                if field not in field_names:
                    errors.append(f"索引字段 {field} 不存在")
        
        # 检查唯一索引
        unique_fields = []
        for index in schema.indexes:
            if index.unique and len(index.fields) == 1:
                unique_fields.append(index.fields[0])
        
        for field in schema.fields:
            if field.unique and field.name not in unique_fields:
                warnings.append(f"字段 {field.name} 标记为唯一但未创建唯一索引")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _generate_index_commands(self, schema: DocumentSchema) -> List[Dict[str, Any]]:
        """生成索引创建命令"""
        commands = []
        
        for index in schema.indexes:
            command = {
                "createIndexes": schema.collection_name,
                "indexes": [
                    {
                        "name": index.name,
                        "key": self._build_index_key(index),
                        "unique": index.unique,
                        "sparse": index.sparse
                    }
                ]
            }
            
            if index.expire_after:
                command["indexes"][0]["expireAfterSeconds"] = index.expire_after
            
            commands.append(command)
        
        return commands
    
    def _build_index_key(self, index: IndexDefinition) -> Dict[str, int]:
        """构建索引键"""
        key = {}
        for field in index.fields:
            if index.index_type == IndexType.TEXT:
                key[field] = "text"
            elif index.index_type == IndexType.GEOSPATIAL:
                key[field] = "2dsphere"
            elif index.index_type == IndexType.HASHED:
                key[field] = "hashed"
            else:
                key[field] = 1
        
        return key
    
    def _generate_validation_command(self, schema: DocumentSchema) -> str:
        """生成验证规则命令"""
        if not schema.validation_rules:
            return "无验证规则"
        
        validation_json = json.dumps(schema.validation_rules, ensure_ascii=False)
        return f'{{ "$jsonSchema": {validation_json} }}'
    
    def _analyze_query_pattern(self, schema: DocumentSchema, pattern: str) -> Dict[str, Any]:
        """分析查询模式"""
        analysis = {
            "pattern": pattern,
            "recommendations": []
        }
        
        # 简单的查询模式分析
        if "find(" in pattern:
            # 提取查询字段
            fields = self._extract_query_fields(pattern)
            
            for field in fields:
                if field in [f.name for f in schema.fields]:
                    # 检查是否有索引
                    has_index = any(field in index.fields for index in schema.indexes)
                    if not has_index:
                        analysis["recommendations"].append(f"建议为字段 {field} 创建索引")
        
        return analysis
    
    def _extract_query_fields(self, query: str) -> List[str]:
        """提取查询字段"""
        # 简化的字段提取逻辑
        fields = []
        
        # 匹配 {field: value} 模式
        matches = re.findall(r'(\w+)\s*:', query)
        fields.extend(matches)
        
        return list(set(fields))
    
    def _generate_optimization_recommendations(self, schema: DocumentSchema, optimizations: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 收集所有建议
        for optimization in optimizations:
            recommendations.extend(optimization["recommendations"])
        
        # 去重并排序
        recommendations = list(set(recommendations))
        recommendations.sort()
        
        return recommendations
    
    def _design_embedding_pattern(self, parent_collection: str, child_collection: str) -> Dict[str, Any]:
        """设计嵌入模式"""
        return {
            "pattern": "embedding",
            "description": "将子文档嵌入到父文档中",
            "use_case": "一对少关系，子文档较小且经常一起访问",
            "advantages": ["读取性能好", "原子操作", "减少查询次数"],
            "disadvantages": ["文档大小限制", "更新复杂", "数据冗余"]
        }
    
    def _design_referencing_pattern(self, parent_collection: str, child_collection: str) -> Dict[str, Any]:
        """设计引用模式"""
        return {
            "pattern": "referencing",
            "description": "使用引用关联不同集合的文档",
            "use_case": "一对多关系，子文档较大或独立访问",
            "advantages": ["文档大小小", "数据一致性", "灵活性好"],
            "disadvantages": ["需要多次查询", "复杂事务", "性能开销"]
        }
    
    def _design_bucket_pattern(self, collection: str) -> Dict[str, Any]:
        """设计桶模式"""
        return {
            "pattern": "bucket",
            "description": "将相关数据分组到桶中",
            "use_case": "时间序列数据、日志数据、IoT数据",
            "advantages": ["减少文档数量", "提高查询效率", "便于聚合"],
            "disadvantages": ["更新复杂", "桶大小管理", "查询复杂性"]
        }
    
    def _design_schema_versioning_pattern(self, collection: str) -> Dict[str, Any]:
        """设计模式版本控制"""
        return {
            "pattern": "schema_versioning",
            "description": "为文档添加版本字段支持模式演进",
            "use_case": "应用演进、数据迁移、向后兼容",
            "advantages": ["平滑升级", "数据迁移", "版本控制"],
            "disadvantages": ["复杂性增加", "存储开销", "查询复杂性"]
        }

# 使用示例
def main():
    print("=== MongoDB文档设计器 ===")
    
    # 创建设计器
    designer = MongoDBDocumentDesigner()
    
    # 设计用户模式
    user_schema = designer.design_user_schema()
    designer.create_schema(user_schema)
    
    # 设计订单模式
    order_schema = designer.design_order_schema()
    designer.create_schema(order_schema)
    
    # 优化文档结构
    print("\n=== 文档结构优化 ===")
    query_patterns = [
        "db.users.find({status: 'active'})",
        "db.orders.find({user_id: ObjectId('...'), status: 'pending'})",
        "db.orders.find({'created_at': {$gte: ISODate('...')}})"
    ]
    
    optimization = designer.optimize_document_structure("users", query_patterns)
    print(f"优化结果: {json.dumps(optimization, indent=2, ensure_ascii=False)}")
    
    # 设计模式
    print("\n=== 设计模式 ===")
    patterns = [
        designer._design_embedding_pattern("users", "addresses"),
        designer._design_referencing_pattern("users", "orders"),
        designer._design_bucket_pattern("logs"),
        designer._design_schema_versioning_pattern("users")
    ]
    
    for pattern in patterns:
        print(f"\n{pattern['pattern'].upper()} 模式:")
        print(f"描述: {pattern['description']}")
        print(f"使用场景: {pattern['use_case']}")
        print(f"优点: {', '.join(pattern['advantages'])}")
        print(f"缺点: {', '.join(pattern['disadvantages'])}")

if __name__ == '__main__':
    main()
```

### Redis缓存管理器
```python
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import redis
from datetime import datetime, timedelta

class CacheStrategy(Enum):
    """缓存策略"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"

class DataType(Enum):
    """数据类型"""
    STRING = "string"
    HASH = "hash"
    LIST = "list"
    SET = "set"
    ZSET = "zset"

@dataclass
class CacheConfig:
    """缓存配置"""
    key_prefix: str
    default_ttl: int
    max_memory: str
    eviction_policy: str
    data_type: DataType
    compression: bool = False
    serialization: str = "json"

@dataclass
class CacheMetrics:
    """缓存指标"""
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0
    memory_usage: int = 0
    key_count: int = 0
    avg_ttl: float = 0.0

class RedisCacheManager:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.configs: Dict[str, CacheConfig] = {}
        self.metrics: Dict[str, CacheMetrics] = {}
    
    def add_cache_config(self, config_name: str, config: CacheConfig) -> bool:
        """添加缓存配置"""
        try:
            self.configs[config_name] = config
            self.metrics[config_name] = CacheMetrics()
            
            # 设置Redis配置
            self.redis_client.config_set('maxmemory', config.max_memory)
            self.redis_client.config_set('maxmemory-policy', config.eviction_policy)
            
            print(f"成功添加缓存配置: {config_name}")
            return True
            
        except Exception as e:
            print(f"添加缓存配置失败: {e}")
            return False
    
    def set_cache(self, config_name: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        if config_name not in self.configs:
            print(f"缓存配置不存在: {config_name}")
            return False
        
        try:
            config = self.configs[config_name]
            full_key = f"{config.key_prefix}:{key}"
            
            # 序列化数据
            serialized_value = self._serialize_value(value, config.serialization)
            
            # 压缩数据
            if config.compression:
                serialized_value = self._compress_data(serialized_value)
            
            # 设置缓存
            if ttl is None:
                ttl = config.default_ttl
            
            result = self.redis_client.setex(full_key, ttl, serialized_value)
            
            # 更新指标
            self._update_metrics(config_name, 'set')
            
            return result
            
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    def get_cache(self, config_name: str, key: str) -> Optional[Any]:
        """获取缓存"""
        if config_name not in self.configs:
            print(f"缓存配置不存在: {config_name}")
            return None
        
        try:
            config = self.configs[config_name]
            full_key = f"{config.key_prefix}:{key}"
            
            # 获取缓存
            cached_value = self.redis_client.get(full_key)
            
            if cached_value is None:
                self._update_metrics(config_name, 'miss')
                return None
            
            # 解压缩数据
            if config.compression:
                cached_value = self._decompress_data(cached_value)
            
            # 反序列化数据
            value = self._deserialize_value(cached_value, config.serialization)
            
            # 更新指标
            self._update_metrics(config_name, 'hit')
            
            return value
            
        except Exception as e:
            print(f"获取缓存失败: {e}")
            self._update_metrics(config_name, 'miss')
            return None
    
    def delete_cache(self, config_name: str, key: str) -> bool:
        """删除缓存"""
        if config_name not in self.configs:
            print(f"缓存配置不存在: {config_name}")
            return False
        
        try:
            config = self.configs[config_name]
            full_key = f"{config.key_prefix}:{key}"
            
            result = self.redis_client.delete(full_key)
            
            # 更新指标
            self._update_metrics(config_name, 'delete')
            
            return result > 0
            
        except Exception as e:
            print(f"删除缓存失败: {e}")
            return False
    
    def invalidate_pattern(self, config_name: str, pattern: str) -> int:
        """按模式失效缓存"""
        if config_name not in self.configs:
            print(f"缓存配置不存在: {config_name}")
            return 0
        
        try:
            config = self.configs[config_name]
            full_pattern = f"{config.key_prefix}:{pattern}"
            
            # 获取匹配的键
            keys = self.redis_client.keys(full_pattern)
            
            if not keys:
                return 0
            
            # 删除键
            deleted_count = self.redis_client.delete(*keys)
            
            # 更新指标
            self._update_metrics(config_name, 'invalidate', deleted_count)
            
            return deleted_count
            
        except Exception as e:
            print(f"模式失效失败: {e}")
            return 0
    
    def get_cache_metrics(self, config_name: str) -> Optional[CacheMetrics]:
        """获取缓存指标"""
        if config_name not in self.metrics:
            return None
        
        # 计算命中率
        metrics = self.metrics[config_name]
        total_requests = metrics.hits + metrics.misses
        if total_requests > 0:
            metrics.hit_rate = metrics.hits / total_requests
        
        # 获取Redis信息
        try:
            info = self.redis_client.info()
            metrics.memory_usage = info.get('used_memory', 0)
            metrics.key_count = info.get('db0', {}).get('keys', 0)
            
            # 计算平均TTL
            config = self.configs[config_name]
            keys = self.redis_client.keys(f"{config.key_prefix}:*")
            if keys:
                total_ttl = 0
                count = 0
                for key in keys[:100]:  # 采样前100个键
                    ttl = self.redis_client.ttl(key)
                    if ttl > 0:
                        total_ttl += ttl
                        count += 1
                
                if count > 0:
                    metrics.avg_ttl = total_ttl / count
            
        except Exception as e:
            print(f"获取Redis信息失败: {e}")
        
        return metrics
    
    def implement_cache_warming(self, config_name: str, data_loader: callable, keys: List[str]) -> Dict[str, Any]:
        """实现缓存预热"""
        if config_name not in self.configs:
            return {"error": "缓存配置不存在"}
        
        results = {
            "success_count": 0,
            "failed_count": 0,
            "errors": []
        }
        
        for key in keys:
            try:
                # 加载数据
                data = data_loader(key)
                
                if data is not None:
                    # 设置缓存
                    success = self.set_cache(config_name, key, data)
                    if success:
                        results["success_count"] += 1
                    else:
                        results["failed_count"] += 1
                        results["errors"].append(f"设置缓存失败: {key}")
                else:
                    results["failed_count"] += 1
                    results["errors"].append(f"数据加载失败: {key}")
                    
            except Exception as e:
                results["failed_count"] += 1
                results["errors"].append(f"处理键失败 {key}: {e}")
        
        return results
    
    def implement_cache_aside_pattern(self, config_name: str, key: str, data_loader: callable) -> Any:
        """实现Cache-Aside模式"""
        # 尝试从缓存获取
        cached_data = self.get_cache(config_name, key)
        
        if cached_data is not None:
            return cached_data
        
        # 从数据源加载
        data = data_loader(key)
        
        if data is not None:
            # 写入缓存
            self.set_cache(config_name, key, data)
        
        return data
    
    def _serialize_value(self, value: Any, serialization: str) -> str:
        """序列化数据"""
        if serialization == "json":
            return json.dumps(value, ensure_ascii=False, default=str)
        elif serialization == "pickle":
            import pickle
            return pickle.dumps(value).hex()
        else:
            return str(value)
    
    def _deserialize_value(self, value: str, serialization: str) -> Any:
        """反序列化数据"""
        if serialization == "json":
            return json.loads(value)
        elif serialization == "pickle":
            import pickle
            return pickle.loads(bytes.fromhex(value))
        else:
            return value
    
    def _compress_data(self, data: str) -> str:
        """压缩数据"""
        import zlib
        compressed = zlib.compress(data.encode('utf-8'))
        return compressed.hex()
    
    def _decompress_data(self, compressed_data: str) -> str:
        """解压缩数据"""
        import zlib
        compressed = bytes.fromhex(compressed_data)
        decompressed = zlib.decompress(compressed)
        return decompressed.decode('utf-8')
    
    def _update_metrics(self, config_name: str, operation: str, count: int = 1):
        """更新指标"""
        if config_name not in self.metrics:
            return
        
        metrics = self.metrics[config_name]
        
        if operation == 'hit':
            metrics.hits += count
        elif operation == 'miss':
            metrics.misses += count
        elif operation == 'set':
            # 设置操作不影响命中率指标
            pass
        elif operation == 'delete':
            # 删除操作不影响命中率指标
            pass
        elif operation == 'invalidate':
            # 失效操作不影响命中率指标
            pass

# 使用示例
def main():
    print("=== Redis缓存管理器 ===")
    
    # 创建缓存管理器
    cache_manager = RedisCacheManager()
    
    # 添加缓存配置
    user_cache_config = CacheConfig(
        key_prefix="user",
        default_ttl=3600,
        max_memory="100mb",
        eviction_policy="allkeys-lru",
        data_type=DataType.HASH,
        compression=True,
        serialization="json"
    )
    
    cache_manager.add_cache_config("users", user_cache_config)
    
    # 设置缓存
    user_data = {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile": {
            "age": 30,
            "city": "北京"
        }
    }
    
    cache_manager.set_cache("users", "1", user_data)
    cache_manager.set_cache("users", "2", {"id": 2, "username": "jane_doe"})
    
    # 获取缓存
    print("\n获取缓存:")
    cached_user = cache_manager.get_cache("users", "1")
    print(f"用户1: {cached_user}")
    
    cached_user2 = cache_manager.get_cache("users", "2")
    print(f"用户2: {cached_user2}")
    
    # 不存在的键
    non_existent = cache_manager.get_cache("users", "999")
    print(f"用户999: {non_existent}")
    
    # 获取指标
    print("\n缓存指标:")
    metrics = cache_manager.get_cache_metrics("users")
    if metrics:
        print(f"命中率: {metrics.hit_rate:.2%}")
        print(f"命中次数: {metrics.hits}")
        print(f"未命中次数: {metrics.misses}")
        print(f"内存使用: {metrics.memory_usage} bytes")
        print(f"键数量: {metrics.key_count}")
        print(f"平均TTL: {metrics.avg_ttl:.1f} 秒")
    
    # 模拟数据加载器
    def load_user_data(user_id: str):
        users = {
            "1": {"id": 1, "username": "john_doe", "email": "john@example.com"},
            "2": {"id": 2, "username": "jane_doe", "email": "jane@example.com"},
            "3": {"id": 3, "username": "bob_smith", "email": "bob@example.com"}
        }
        return users.get(user_id)
    
    # Cache-Aside模式
    print("\n=== Cache-Aside模式 ===")
    user_data = cache_manager.implement_cache_aside_pattern("users", "3", load_user_data)
    print(f"用户3: {user_data}")
    
    # 缓存预热
    print("\n=== 缓存预热 ===")
    warmup_keys = ["1", "2", "3", "4", "5"]
    warmup_results = cache_manager.implement_cache_warming("users", load_user_data, warmup_keys)
    print(f"预热结果: {warmup_results}")
    
    # 模式失效
    print("\n=== 模式失效 ===")
    invalidated_count = cache_manager.invalidate_pattern("users", "*")
    print(f"失效的缓存数量: {invalidated_count}")

if __name__ == '__main__':
    main()
```

## NoSQL数据库最佳实践

### 数据模型设计
1. **选择合适的数据类型**: 根据应用场景选择文档、键值、列族或图数据库
2. **设计合理的文档结构**: 平衡嵌入和引用，控制文档大小
3. **优化查询模式**: 根据查询需求设计数据结构
4. **实现版本控制**: 支持数据模式演进
5. **考虑数据一致性**: 选择合适的一致性级别

### 性能优化
1. **索引策略**: 设计合理的单字段和复合索引
2. **查询优化**: 避免全表扫描，优化聚合查询
3. **分片策略**: 合理设计分片键，避免热点
4. **缓存策略**: 实现多级缓存，提高读取性能
5. **连接池管理**: 优化数据库连接使用

### 扩展性设计
1. **水平扩展**: 设计支持分片的架构
2. **负载均衡**: 实现读写分离和负载分发
3. **数据分片**: 选择合适的分片策略
4. **集群管理**: 实现高可用和故障转移
5. **监控告警**: 实时监控系统状态

### 数据一致性
1. **一致性级别**: 根据业务需求选择一致性级别
2. **分布式事务**: 实现跨节点事务处理
3. **冲突解决**: 处理并发更新冲突
4. **数据同步**: 实现数据同步机制
5. **备份恢复**: 制定数据备份策略

## 相关技能

- **sql-optimization** - SQL优化
- **backup-recovery** - 备份与恢复
- **migration-validator** - 迁移验证
- **transaction-management** - 事务管理
