---
name: RESTful API设计
description: "当设计RESTful API时，分析资源模型，优化接口设计，解决性能问题。验证API架构，设计版本控制，和最佳实践。"
license: MIT
---

# RESTful API设计技能

## 概述
RESTful API是现代Web服务的核心架构。不当的API设计会导致性能问题、安全漏洞和维护困难。需要系统化的API设计方法和规范。

**核心原则**: 好的RESTful API应该资源导向、状态清晰、版本可控、易于扩展。坏的RESTful API会导致接口混乱、性能下降、安全风险。

## 何时使用

**始终:**
- 设计新API接口时
- 重构现有API时
- 实现微服务架构时
- 构建Web应用后端时
- 开发移动应用API时
- 创建第三方集成接口时

**触发短语:**
- "API设计"
- "RESTful架构"
- "接口规范"
- "API版本控制"
- "资源建模"
- "HTTP状态码"

## API设计功能

### 资源建模
- 实体识别与抽象
- 资源关系设计
- URL路径规划
- 资源层次结构
- 子资源管理

### HTTP方法设计
- GET查询操作
- POST创建操作
- PUT更新操作
- DELETE删除操作
- PATCH部分更新

### 状态码规范
- 成功状态码(2xx)
- 客户端错误(4xx)
- 服务器错误(5xx)
- 自定义状态码
- 错误信息格式

### 版本控制策略
- URL路径版本控制
- 请求头版本控制
- 查询参数版本控制
- 向后兼容性
- 版本迁移策略

## 常见API设计问题

### 资源命名不规范
```
问题:
API端点命名不符合REST规范，导致接口混乱

错误示例:
- 使用动词而非名词: /getUser, /createUser
- 命名不一致: /users, /user_list
- 复数形式错误: /user, /userss
- 层级过深: /api/v1/users/1/posts/1/comments/1

解决方案:
1. 使用名词表示资源
2. 保持命名一致性
3. 使用正确的复数形式
4. 限制资源层级深度
```

### HTTP方法滥用
```
问题:
不正确使用HTTP方法，违反REST原则

错误示例:
- GET用于创建资源
- POST用于查询操作
- PUT用于部分更新
- 所有操作都用POST

解决方案:
1. GET用于查询和获取
2. POST用于创建资源
3. PUT用于完整更新
4. PATCH用于部分更新
5. DELETE用于删除资源
```

### 状态码使用不当
```
问题:
HTTP状态码使用不规范，影响客户端处理

错误示例:
- 所有响应都返回200
- 错误时返回404而非400
- 成功时返回201而非200
- 缺少适当的错误信息

解决方案:
1. 200表示成功请求
2. 201表示资源创建成功
3. 400表示客户端错误
4. 404表示资源不存在
5. 500表示服务器错误
```

### 缺少版本控制
```
问题:
API缺少版本控制，导致升级困难

错误示例:
- 直接修改现有接口
- 强制客户端升级
- 不兼容的变更
- 缺少版本规划

解决方案:
1. 实施URL路径版本控制
2. 保持向后兼容性
3. 提前通知版本废弃
4. 制定版本迁移计划
```

## 代码实现示例

### RESTful API框架
```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class HTTPStatus(Enum):
    """HTTP状态码"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500

@dataclass
class APIResponse:
    """API响应格式"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class ValidationError(Exception):
    """验证错误"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class APIError(Exception):
    """API错误"""
    def __init__(self, message: str, status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class BaseModel(db.Model):
    """基础模型"""
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Post(BaseModel):
    """文章模型"""
    __tablename__ = 'posts'
    
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class RequestValidator:
    """请求验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_user_data(data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """验证用户数据"""
        errors = []
        
        if not is_update or 'name' in data:
            name = data.get('name', '').strip()
            if not name:
                errors.append('Name is required')
            elif len(name) < 2:
                errors.append('Name must be at least 2 characters')
            elif len(name) > 100:
                errors.append('Name must be less than 100 characters')
        
        if not is_update or 'email' in data:
            email = data.get('email', '').strip()
            if not email:
                errors.append('Email is required')
            elif not RequestValidator.validate_email(email):
                errors.append('Invalid email format')
        
        if errors:
            raise ValidationError('; '.join(errors))
        
        return data
    
    @staticmethod
    def validate_post_data(data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """验证文章数据"""
        errors = []
        
        if not is_update or 'title' in data:
            title = data.get('title', '').strip()
            if not title:
                errors.append('Title is required')
            elif len(title) < 3:
                errors.append('Title must be at least 3 characters')
            elif len(title) > 200:
                errors.append('Title must be less than 200 characters')
        
        if not is_update or 'content' in data:
            content = data.get('content', '').strip()
            if not content:
                errors.append('Content is required')
            elif len(content) < 10:
                errors.append('Content must be at least 10 characters')
        
        if errors:
            raise ValidationError('; '.join(errors))
        
        return data

class PaginationHelper:
    """分页助手"""
    
    @staticmethod
    def get_pagination_params() -> Dict[str, int]:
        """获取分页参数"""
        page = max(1, request.args.get('page', 1, type=int))
        limit = min(100, max(1, request.args.get('limit', 20, type=int)))
        offset = (page - 1) * limit
        
        return {'page': page, 'limit': limit, 'offset': offset}
    
    @staticmethod
    def create_pagination_response(items: List[Any], total: int, page: int, limit: int) -> Dict[str, Any]:
        """创建分页响应"""
        total_pages = (total + limit - 1) // limit
        
        return {
            'items': items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }

class APIController:
    """API控制器基类"""
    
    def create_response(self, data: Any = None, error: str = None, 
                       message: str = None, status_code: int = HTTPStatus.OK.value,
                       meta: Dict[str, Any] = None) -> tuple:
        """创建统一响应"""
        response = APIResponse(
            success=error is None,
            data=data,
            error=error,
            message=message,
            meta=meta
        )
        
        return jsonify(response.__dict__), status_code
    
    def handle_validation_error(self, error: ValidationError) -> tuple:
        """处理验证错误"""
        return self.create_response(
            error=error.message,
            status_code=HTTPStatus.BAD_REQUEST.value
        )
    
    def handle_not_found(self, resource: str = 'Resource') -> tuple:
        """处理资源未找到"""
        return self.create_response(
            error=f'{resource} not found',
            status_code=HTTPStatus.NOT_FOUND.value
        )
    
    def handle_conflict(self, message: str) -> tuple:
        """处理冲突错误"""
        return self.create_response(
            error=message,
            status_code=HTTPStatus.CONFLICT.value
        )
    
    def handle_server_error(self, error: Exception) -> tuple:
        """处理服务器错误"""
        app.logger.error(f'Server error: {str(error)}')
        return self.create_response(
            error='Internal server error',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value
        )

class UserController(APIController):
    """用户控制器"""
    
    def __init__(self):
        self.validator = RequestValidator()
    
    def get_users(self):
        """获取用户列表"""
        try:
            pagination = PaginationHelper.get_pagination_params()
            
            query = User.query
            # 应用过滤
            if 'search' in request.args:
                search = request.args['search']
                query = query.filter(User.name.contains(search) | User.email.contains(search))
            
            # 应用排序
            sort_by = request.args.get('sort_by', 'created_at')
            sort_order = request.args.get('sort_order', 'desc')
            if hasattr(User, sort_by):
                if sort_order == 'desc':
                    query = query.order_by(getattr(User, sort_by).desc())
                else:
                    query = query.order_by(getattr(User, sort_by).asc())
            
            total = query.count()
            users = query.offset(pagination['offset']).limit(pagination['limit']).all()
            
            result = PaginationHelper.create_pagination_response(
                [user.to_dict() for user in users],
                total,
                pagination['page'],
                pagination['limit']
            )
            
            return self.create_response(data=result)
            
        except Exception as e:
            return self.handle_server_error(e)
    
    def get_user(self, user_id: str):
        """获取单个用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return self.handle_not_found('User')
            
            return self.create_response(data=user.to_dict())
            
        except Exception as e:
            return self.handle_server_error(e)
    
    def create_user(self):
        """创建用户"""
        try:
            data = request.get_json()
            if not data:
                return self.create_response(
                    error='Request body is required',
                    status_code=HTTPStatus.BAD_REQUEST.value
                )
            
            validated_data = self.validator.validate_user_data(data)
            
            # 检查邮箱是否已存在
            if User.query.filter_by(email=validated_data['email']).first():
                return self.handle_conflict('Email already exists')
            
            user = User(
                name=validated_data['name'],
                email=validated_data['email'],
                password_hash='hashed_password'  # 实际应用中应该使用bcrypt等
            )
            
            db.session.add(user)
            db.session.commit()
            
            return self.create_response(
                data=user.to_dict(),
                message='User created successfully',
                status_code=HTTPStatus.CREATED.value
            )
            
        except ValidationError as e:
            return self.handle_validation_error(e)
        except Exception as e:
            db.session.rollback()
            return self.handle_server_error(e)
    
    def update_user(self, user_id: str):
        """更新用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return self.handle_not_found('User')
            
            data = request.get_json()
            if not data:
                return self.create_response(
                    error='Request body is required',
                    status_code=HTTPStatus.BAD_REQUEST.value
                )
            
            validated_data = self.validator.validate_user_data(data, is_update=True)
            
            # 检查邮箱是否已被其他用户使用
            if 'email' in validated_data:
                existing_user = User.query.filter(
                    User.email == validated_data['email'],
                    User.id != user_id
                ).first()
                if existing_user:
                    return self.handle_conflict('Email already exists')
            
            # 更新用户信息
            for key, value in validated_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return self.create_response(
                data=user.to_dict(),
                message='User updated successfully'
            )
            
        except ValidationError as e:
            return self.handle_validation_error(e)
        except Exception as e:
            db.session.rollback()
            return self.handle_server_error(e)
    
    def delete_user(self, user_id: str):
        """删除用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return self.handle_not_found('User')
            
            db.session.delete(user)
            db.session.commit()
            
            return self.create_response(
                data={'deleted': user.to_dict()},
                message='User deleted successfully',
                status_code=HTTPStatus.NO_CONTENT.value
            )
            
        except Exception as e:
            db.session.rollback()
            return self.handle_server_error(e)

class PostController(APIController):
    """文章控制器"""
    
    def __init__(self):
        self.validator = RequestValidator()
    
    def get_posts(self):
        """获取文章列表"""
        try:
            pagination = PaginationHelper.get_pagination_params()
            
            query = Post.query
            # 应用过滤
            if 'author_id' in request.args:
                query = query.filter(Post.author_id == request.args['author_id'])
            
            if 'is_published' in request.args:
                query = query.filter(Post.is_published == request.args['is_published'].lower() == 'true')
            
            if 'search' in request.args:
                search = request.args['search']
                query = query.filter(Post.title.contains(search) | Post.content.contains(search))
            
            # 应用排序
            sort_by = request.args.get('sort_by', 'created_at')
            sort_order = request.args.get('sort_order', 'desc')
            if hasattr(Post, sort_by):
                if sort_order == 'desc':
                    query = query.order_by(getattr(Post, sort_by).desc())
                else:
                    query = query.order_by(getattr(Post, sort_by).asc())
            
            total = query.count()
            posts = query.offset(pagination['offset']).limit(pagination['limit']).all()
            
            result = PaginationHelper.create_pagination_response(
                [post.to_dict() for post in posts],
                total,
                pagination['page'],
                pagination['limit']
            )
            
            return self.create_response(data=result)
            
        except Exception as e:
            return self.handle_server_error(e)
    
    def get_post(self, post_id: str):
        """获取单个文章"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return self.handle_not_found('Post')
            
            return self.create_response(data=post.to_dict())
            
        except Exception as e:
            return self.handle_server_error(e)
    
    def create_post(self):
        """创建文章"""
        try:
            data = request.get_json()
            if not data:
                return self.create_response(
                    error='Request body is required',
                    status_code=HTTPStatus.BAD_REQUEST.value
                )
            
            validated_data = self.validator.validate_post_data(data)
            
            # 验证作者是否存在
            author_id = validated_data.get('author_id')
            if not User.query.get(author_id):
                return self.handle_not_found('Author')
            
            post = Post(
                title=validated_data['title'],
                content=validated_data['content'],
                author_id=author_id,
                is_published=validated_data.get('is_published', False)
            )
            
            db.session.add(post)
            db.session.commit()
            
            return self.create_response(
                data=post.to_dict(),
                message='Post created successfully',
                status_code=HTTPStatus.CREATED.value
            )
            
        except ValidationError as e:
            return self.handle_validation_error(e)
        except Exception as e:
            db.session.rollback()
            return self.handle_server_error(e)

# 路由定义
user_controller = UserController()
post_controller = PostController()

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return user_controller.get_users()

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    return user_controller.create_user()

@app.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    return user_controller.get_user(user_id)

@app.route('/api/v1/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    return user_controller.update_user(user_id)

@app.route('/api/v1/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    return user_controller.delete_user(user_id)

@app.route('/api/v1/posts', methods=['GET'])
def get_posts():
    return post_controller.get_posts()

@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    return post_controller.create_post()

@app.route('/api/v1/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    return post_controller.get_post(post_id)

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return APIController().create_response(
        error='Endpoint not found',
        status_code=HTTPStatus.NOT_FOUND.value
    )

@app.errorhandler(405)
def method_not_allowed(error):
    return APIController().create_response(
        error='Method not allowed',
        status_code=405
    )

@app.errorhandler(500)
def internal_error(error):
    return APIController().handle_server_error(error)

# 使用示例
def main():
    print("=== RESTful API设计器 ===")
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    print("API服务器已启动")
    print("可用的端点:")
    print("GET    /api/v1/users          - 获取用户列表")
    print("POST   /api/v1/users          - 创建用户")
    print("GET    /api/v1/users/<id>     - 获取用户详情")
    print("PUT    /api/v1/users/<id>     - 更新用户")
    print("DELETE /api/v1/users/<id>     - 删除用户")
    print("GET    /api/v1/posts          - 获取文章列表")
    print("POST   /api/v1/posts          - 创建文章")
    print("GET    /api/v1/posts/<id>     - 获取文章详情")
    
    # 示例请求
    print("\n示例请求:")
    print("curl -X GET http://localhost:5000/api/v1/users")
    print("curl -X POST http://localhost:5000/api/v1/users -H 'Content-Type: application/json' -d '{\"name\":\"John\",\"email\":\"john@example.com\"}'")

if __name__ == '__main__':
    main()
    app.run(debug=True)
```

### API文档生成器
```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

class HTTPMethod(Enum):
    """HTTP方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class ParameterType(Enum):
    """参数类型"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

@dataclass
class APIParameter:
    """API参数"""
    name: str
    type: ParameterType
    required: bool = False
    description: str = ""
    default_value: Any = None
    example: Any = None

@dataclass
class APIResponse:
    """API响应"""
    status_code: int
    description: str
    schema: Optional[Dict[str, Any]] = None
    example: Optional[Dict[str, Any]] = None

@dataclass
class APIEndpoint:
    """API端点"""
    path: str
    method: HTTPMethod
    summary: str
    description: str
    parameters: List[APIParameter]
    responses: List[APIResponse]
    tags: List[str]

class APIDocumentationGenerator:
    def __init__(self):
        self.endpoints: List[APIEndpoint] = []
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.info = {
            "title": "API Documentation",
            "version": "1.0.0",
            "description": "RESTful API documentation"
        }
    
    def add_endpoint(self, endpoint: APIEndpoint):
        """添加API端点"""
        self.endpoints.append(endpoint)
    
    def add_schema(self, name: str, schema: Dict[str, Any]):
        """添加数据模型"""
        self.schemas[name] = schema
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """生成OpenAPI规范"""
        spec = {
            "openapi": "3.0.0",
            "info": self.info,
            "paths": {},
            "components": {
                "schemas": self.schemas
            }
        }
        
        # 按路径分组端点
        paths = {}
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            operation = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": [],
                "responses": {}
            }
            
            # 添加参数
            for param in endpoint.parameters:
                param_spec = {
                    "name": param.name,
                    "in": "query" if endpoint.method in [HTTPMethod.GET] else "body",
                    "required": param.required,
                    "schema": {
                        "type": param.type.value
                    }
                }
                
                if param.description:
                    param_spec["description"] = param.description
                
                if param.default_value is not None:
                    param_spec["schema"]["default"] = param.default_value
                
                if param.example is not None:
                    param_spec["example"] = param.example
                
                operation["parameters"].append(param_spec)
            
            # 添加响应
            for response in endpoint.responses:
                response_spec = {
                    "description": response.description
                }
                
                if response.schema:
                    response_spec["content"] = {
                        "application/json": {
                            "schema": response.schema
                        }
                    }
                
                if response.example:
                    if "content" not in response_spec:
                        response_spec["content"] = {"application/json": {}}
                    response_spec["content"]["application/json"]["example"] = response.example
                
                operation["responses"][str(response.status_code)] = response_spec
            
            paths[endpoint.path][endpoint.method.value.lower()] = operation
        
        spec["paths"] = paths
        return spec
    
    def generate_markdown_docs(self) -> str:
        """生成Markdown文档"""
        lines = [
            f"# {self.info['title']}",
            "",
            self.info['description'],
            f"Version: {self.info['version']}",
            "",
            "## 目录",
            ""
        ]
        
        # 生成目录
        tags = set()
        for endpoint in self.endpoints:
            tags.update(endpoint.tags)
        
        for tag in sorted(tags):
            lines.append(f"- [{tag}](#{tag.lower().replace(' ', '-')})")
        
        lines.extend(["", "---", ""])
        
        # 按标签分组生成文档
        for tag in sorted(tags):
            lines.append(f"## {tag}")
            lines.append("")
            
            tag_endpoints = [ep for ep in self.endpoints if tag in ep.tags]
            
            for endpoint in tag_endpoints:
                lines.extend([
                    f"### {endpoint.method.value} {endpoint.path}",
                    "",
                    f"**描述**: {endpoint.description}",
                    ""
                ])
                
                if endpoint.parameters:
                    lines.append("**参数**:")
                    for param in endpoint.parameters:
                        required_str = " (必需)" if param.required else " (可选)"
                        lines.append(f"- `{param.name}`: {param.type.value}{required_str}")
                        if param.description:
                            lines.append(f"  - {param.description}")
                        if param.default_value is not None:
                            lines.append(f"  - 默认值: `{param.default_value}`")
                    lines.append("")
                
                lines.append("**响应**:")
                for response in endpoint.responses:
                    lines.append(f"- `{response.status_code}`: {response.description}")
                lines.append("")
                
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)

# 使用示例
def main():
    print("=== API文档生成器 ===")
    
    # 创建文档生成器
    doc_gen = APIDocumentationGenerator()
    
    # 添加数据模型
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid"},
            "name": {"type": "string", "minLength": 2, "maxLength": 100},
            "email": {"type": "string", "format": "email"},
            "is_active": {"type": "boolean"},
            "created_at": {"type": "string", "format": "date-time"}
        },
        "required": ["name", "email"]
    }
    
    doc_gen.add_schema("User", user_schema)
    
    # 添加API端点
    get_users_endpoint = APIEndpoint(
        path="/api/v1/users",
        method=HTTPMethod.GET,
        summary="获取用户列表",
        description="获取所有用户的列表，支持分页、搜索和排序",
        parameters=[
            APIParameter("page", ParameterType.INTEGER, False, "页码", 1, 1),
            APIParameter("limit", ParameterType.INTEGER, False, "每页数量", 20, 20),
            APIParameter("search", ParameterType.STRING, False, "搜索关键词"),
            APIParameter("sort_by", ParameterType.STRING, False, "排序字段", "created_at"),
            APIParameter("sort_order", ParameterType.STRING, False, "排序方向", "desc")
        ],
        responses=[
            APIResponse(200, "成功获取用户列表", {"items": {"type": "array", "items": {"$ref": "#/components/schemas/User"}}}),
            APIResponse(400, "请求参数错误"),
            APIResponse(500, "服务器内部错误")
        ],
        tags=["用户管理"]
    )
    
    create_user_endpoint = APIEndpoint(
        path="/api/v1/users",
        method=HTTPMethod.POST,
        summary="创建用户",
        description="创建新的用户账户",
        parameters=[
            APIParameter("name", ParameterType.STRING, True, "用户姓名", example="John Doe"),
            APIParameter("email", ParameterType.STRING, True, "邮箱地址", example="john@example.com"),
            APIParameter("password", ParameterType.STRING, True, "密码")
        ],
        responses=[
            APIResponse(201, "用户创建成功", {"$ref": "#/components/schemas/User"}),
            APIResponse(400, "请求参数错误"),
            APIResponse(409, "邮箱已存在"),
            APIResponse(500, "服务器内部错误")
        ],
        tags=["用户管理"]
    )
    
    doc_gen.add_endpoint(get_users_endpoint)
    doc_gen.add_endpoint(create_user_endpoint)
    
    # 生成OpenAPI规范
    openapi_spec = doc_gen.generate_openapi_spec()
    
    print("=== OpenAPI规范 ===")
    print(json.dumps(openapi_spec, indent=2, ensure_ascii=False))
    
    # 生成Markdown文档
    markdown_docs = doc_gen.generate_markdown_docs()
    
    print("\n=== Markdown文档 ===")
    print(markdown_docs[:1000] + "..." if len(markdown_docs) > 1000 else markdown_docs)

if __name__ == '__main__':
    main()
```

## RESTful API设计最佳实践

### 资源设计原则
1. **名词导向**: 使用名词而非动词表示资源
2. **复数形式**: 使用复数形式表示资源集合
3. **层级关系**: 合理设计资源层级关系
4. **一致性**: 保持命名和结构的一致性
5. **可预测性**: 使API行为可预测

### HTTP方法使用
1. **GET**: 安全且幂等的查询操作
2. **POST**: 非幂等的创建操作
3. **PUT**: 幂等的完整更新操作
4. **PATCH**: 非幂等的部分更新操作
5. **DELETE**: 幂等的删除操作

### 状态码规范
1. **2xx成功**: 表示请求成功处理
2. **3xx重定向**: 表示需要进一步操作
3. **4xx客户端错误**: 表示客户端请求错误
4. **5xx服务器错误**: 表示服务器处理错误
5. **自定义状态码**: 谨慎使用自定义状态码

### 版本控制策略
1. **URL版本控制**: `/api/v1/users`
2. **请求头版本控制**: `Accept: application/vnd.api+json;version=1`
3. **查询参数版本控制**: `?version=1`
4. **向后兼容**: 保持旧版本的兼容性
5. **废弃通知**: 提前通知版本废弃

## 相关技能

- **api-validator** - API验证
- **error-handling-logging** - 错误处理与日志
- **database-query-analyzer** - 数据库查询分析
- **graphql-api** - GraphQL API开发
