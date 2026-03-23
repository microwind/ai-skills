# RESTful API设计参考文档

## RESTful API设计概述

### 什么是RESTful API
RESTful API是一种基于REST（Representational State Transfer）架构风格的Web服务API设计方法，通过使用HTTP协议的标准方法（GET、POST、PUT、DELETE等）来操作资源，实现统一接口、无状态、可缓存、分层系统的设计原则。该技能涵盖了资源设计、端点设计、数据格式、安全认证、性能优化、文档生成等功能，帮助开发者构建标准、高效、可维护的RESTful API服务。

### 主要功能
- **资源建模**: 提供实体资源、集合资源、资源关系等完整资源建模能力
- **端点设计**: 支持标准CRUD操作、自定义操作、版本控制等端点设计
- **数据格式**: 支持JSON、XML、表单等多种数据格式和验证规则
- **安全认证**: 提供API Key、JWT、OAuth 2.0等多种认证授权方式
- **性能优化**: 包含缓存策略、分页配置、响应优化等性能优化功能

## RESTful API设计核心

### API设计器
```python
# restful_api_designer.py
import json
import re
import uuid
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
import base64
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor

class HTTPMethod(Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class HTTPStatus(Enum):
    """HTTP状态码枚举"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

class DataType(Enum):
    """数据类型枚举"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    OBJECT = "object"
    ARRAY = "array"

class RelationType(Enum):
    """关系类型枚举"""
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"

@dataclass
class ResourceField:
    """资源字段"""
    name: str
    data_type: DataType
    required: bool = False
    default: Any = None
    description: str = ""
    validation_rules: List[str] = field(default_factory=list)
    read_only: bool = False
    write_only: bool = False

@dataclass
class ResourceDefinition:
    """资源定义"""
    name: str
    description: str = ""
    fields: List[ResourceField] = field(default_factory=list)
    relationships: Dict[str, 'ResourceRelationship'] = field(default_factory=dict)
    endpoints: List['EndpointDefinition'] = field(default_factory=list)
    custom_operations: List['CustomOperation'] = field(default_factory=list)

@dataclass
class ResourceRelationship:
    """资源关系"""
    target_resource: str
    relation_type: RelationType
    foreign_key: Optional[str] = None
    join_table: Optional[str] = None
    cascade_delete: bool = False
    cascade_update: bool = False

@dataclass
class EndpointDefinition:
    """端点定义"""
    path: str
    method: HTTPMethod
    description: str = ""
    parameters: List[ResourceField] = field(default_factory=list)
    request_body: Optional[ResourceDefinition] = None
    response_body: Optional[ResourceDefinition] = None
    status_codes: Dict[HTTPStatus, str] = field(default_factory=dict)
    authentication_required: bool = True
    authorization_required: bool = False
    rate_limit: Optional[int] = None

@dataclass
class CustomOperation:
    """自定义操作"""
    name: str
    path: str
    method: HTTPMethod
    description: str = ""
    parameters: List[ResourceField] = field(default_factory=list)
    request_body: Optional[ResourceDefinition] = None
    response_body: Optional[ResourceDefinition] = None
    status_codes: Dict[HTTPStatus, str] = field(default_factory=dict)

@dataclass
class APIConfiguration:
    """API配置"""
    # 基础配置
    api_name: str = "My API"
    api_version: str = "v1"
    base_url: str = "https://api.example.com"
    description: str = ""
    
    # 版本控制
    version_strategy: str = "url_path"  # url_path, query_param, header
    version_header: str = "Accept"
    
    # 数据格式
    default_content_type: str = "application/json"
    supported_content_types: List[str] = field(default_factory=lambda: ["application/json"])
    date_format: str = "ISO8601"
    
    # 认证配置
    authentication_type: str = "jwt"  # none, api_key, jwt, oauth
    api_key_header: str = "X-API-Key"
    jwt_header: str = "Authorization"
    jwt_prefix: str = "Bearer"
    
    # 安全配置
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    
    # 性能配置
    enable_caching: bool = False
    cache_ttl: int = 300  # 5分钟
    enable_compression: bool = True
    compression_threshold: int = 1024  # 1KB
    
    # 分页配置
    default_page_size: int = 20
    max_page_size: int = 100
    pagination_type: str = "offset"  # offset, cursor, time_based
    
    # 监控配置
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_metrics: bool = False
    metrics_interval: int = 60

class ResourceValidator:
    """资源验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_resource(self, resource: ResourceDefinition) -> List[str]:
        """验证资源定义"""
        errors = []
        
        # 验证资源名称
        if not resource.name:
            errors.append("资源名称不能为空")
        elif not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', resource.name):
            errors.append("资源名称只能包含字母、数字、下划线和连字符，且必须以字母开头")
        
        # 验证字段
        field_names = set()
        for field in resource.fields:
            if field.name in field_names:
                errors.append(f"字段名重复: {field.name}")
            field_names.add(field.name)
            
            # 验证字段名称
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', field.name):
                errors.append(f"字段名格式错误: {field.name}")
        
        # 验证关系
        for rel_name, relationship in resource.relationships.items():
            if not relationship.target_resource:
                errors.append(f"关系 {rel_name} 缺少目标资源")
            
            if relationship.relation_type == RelationType.ONE_TO_MANY and not relationship.foreign_key:
                errors.append(f"一对多关系 {rel_name} 需要外键字段")
            
            if relationship.relation_type == RelationType.MANY_TO_MANY and not relationship.join_table:
                errors.append(f"多对多关系 {rel_name} 需要中间表")
        
        # 验证端点
        endpoint_paths = set()
        for endpoint in resource.endpoints:
            if endpoint.path in endpoint_paths:
                errors.append(f"端点路径重复: {endpoint.path}")
            endpoint_paths.add(endpoint.path)
            
            # 验证路径格式
            if not endpoint.path.startswith('/'):
                errors.append(f"端点路径必须以/开头: {endpoint.path}")
        
        return errors
    
    def validate_endpoint(self, endpoint: EndpointDefinition) -> List[str]:
        """验证端点定义"""
        errors = []
        
        # 验证路径
        if not endpoint.path:
            errors.append("端点路径不能为空")
        elif not endpoint.path.startswith('/'):
            errors.append("端点路径必须以/开头")
        
        # 验证方法
        if not isinstance(endpoint.method, HTTPMethod):
            errors.append("端点方法必须是有效的HTTP方法")
        
        # 验证状态码
        valid_status_codes = {
            HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT,
            HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN,
            HTTPStatus.NOT_FOUND, HTTPStatus.METHOD_NOT_ALLOWED, HTTPStatus.UNPROCESSABLE_ENTITY,
            HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.SERVICE_UNAVAILABLE
        }
        
        for status_code in endpoint.status_codes:
            if status_code not in valid_status_codes:
                errors.append(f"无效的状态码: {status_code}")
        
        return errors

class URLGenerator:
    """URL生成器"""
    
    def __init__(self, config: APIConfiguration):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_resource_url(self, resource_name: str, resource_id: Optional[str] = None) -> str:
        """生成资源URL"""
        base_path = f"/{self.config.api_version}/{resource_name}"
        
        if resource_id:
            return f"{base_path}/{resource_id}"
        
        return base_path
    
    def generate_relationship_url(self, resource_name: str, resource_id: str, 
                                  relationship_name: str) -> str:
        """生成关系URL"""
        return f"/{self.config.api_version}/{resource_name}/{resource_id}/{relationship_name}"
    
    def generate_custom_operation_url(self, resource_name: str, resource_id: str,
                                      operation_path: str) -> str:
        """生成自定义操作URL"""
        return f"/{self.config.api_version}/{resource_name}/{resource_id}/{operation_path}"
    
    def generate_full_url(self, path: str) -> str:
        """生成完整URL"""
        return urljoin(self.config.base_url, path.lstrip('/'))

class ResponseGenerator:
    """响应生成器"""
    
    def __init__(self, config: APIConfiguration):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_success_response(self, data: Any, status_code: HTTPStatus = HTTPStatus.OK,
                                   message: str = "Success") -> Dict[str, Any]:
        """生成成功响应"""
        response = {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        if status_code == HTTPStatus.CREATED:
            response["message"] = "Resource created successfully"
        elif status_code == HTTPStatus.NO_CONTENT:
            response["message"] = "Resource deleted successfully"
        
        return response
    
    def generate_error_response(self, error_code: str, error_message: str,
                                status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
                                details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成错误响应"""
        response = {
            "status": "error",
            "error": error_code,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            response["details"] = details
        
        return response
    
    def generate_validation_error_response(self, validation_errors: List[str]) -> Dict[str, Any]:
        """生成验证错误响应"""
        return self.generate_error_response(
            error_code="VALIDATION_ERROR",
            error_message="Validation failed",
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            details={"errors": validation_errors}
        )
    
    def generate_paginated_response(self, data: List[Any], page: int, page_size: int,
                                    total_count: int) -> Dict[str, Any]:
        """生成分页响应"""
        total_pages = (total_count + page_size - 1) // page_size
        
        pagination = {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        return self.generate_success_response({
            "items": data,
            "pagination": pagination
        })

class AuthenticationManager:
    """认证管理器"""
    
    def __init__(self, config: APIConfiguration):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_keys = set()
        self.jwt_secret = "your-secret-key"
    
    def add_api_key(self, api_key: str):
        """添加API密钥"""
        self.api_keys.add(api_key)
    
    def remove_api_key(self, api_key: str):
        """移除API密钥"""
        self.api_keys.discard(api_key)
    
    def authenticate_request(self, headers: Dict[str, str]) -> tuple[bool, Optional[str]]:
        """认证请求"""
        if self.config.authentication_type == "none":
            return True, None
        
        if self.config.authentication_type == "api_key":
            return self._authenticate_api_key(headers)
        elif self.config.authentication_type == "jwt":
            return self._authenticate_jwt(headers)
        elif self.config.authentication_type == "oauth":
            return self._authenticate_oauth(headers)
        
        return False, "Unsupported authentication type"
    
    def _authenticate_api_key(self, headers: Dict[str, str]) -> tuple[bool, Optional[str]]:
        """API密钥认证"""
        api_key = headers.get(self.config.api_key_header)
        
        if not api_key:
            return False, "API key missing"
        
        if api_key not in self.api_keys:
            return False, "Invalid API key"
        
        return True, None
    
    def _authenticate_jwt(self, headers: Dict[str, str]) -> tuple[bool, Optional[str]]:
        """JWT认证"""
        auth_header = headers.get(self.config.jwt_header)
        
        if not auth_header:
            return False, "Authorization header missing"
        
        if not auth_header.startswith(f"{self.config.jwt_prefix} "):
            return False, "Invalid authorization header format"
        
        token = auth_header[len(f"{self.config.jwt_prefix} "):]
        
        try:
            import jwt
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return True, None
        except jwt.ExpiredSignatureError:
            return False, "Token expired"
        except jwt.InvalidTokenError:
            return False, "Invalid token"
    
    def _authenticate_oauth(self, headers: Dict[str, str]) -> tuple[bool, Optional[str]]:
        """OAuth认证"""
        # 简化实现，实际应该验证OAuth令牌
        auth_header = headers.get("Authorization")
        
        if not auth_header:
            return False, "Authorization header missing"
        
        return True, None

class RateLimiter:
    """频率限制器"""
    
    def __init__(self, config: APIConfiguration):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.request_counts = defaultdict(list)
        self.lock = threading.Lock()
    
    def check_rate_limit(self, client_id: str, limit: int, window: int = 60) -> bool:
        """检查频率限制"""
        current_time = time.time()
        
        with self.lock:
            # 清理过期记录
            self.request_counts[client_id] = [
                req_time for req_time in self.request_counts[client_id]
                if current_time - req_time < window
            ]
            
            # 检查是否超过限制
            if len(self.request_counts[client_id]) >= limit:
                return False
            
            # 记录当前请求
            self.request_counts[client_id].append(current_time)
            return True
    
    def get_remaining_requests(self, client_id: str, limit: int, window: int = 60) -> int:
        """获取剩余请求数"""
        current_time = time.time()
        
        with self.lock:
            # 清理过期记录
            self.request_counts[client_id] = [
                req_time for req_time in self.request_counts[client_id]
                if current_time - req_time < window
            ]
            
            return max(0, limit - len(self.request_counts[client_id]))

class RESTfulAPIDesigner:
    """RESTful API设计器"""
    
    def __init__(self, config: APIConfiguration):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.resources: Dict[str, ResourceDefinition] = {}
        self.validator = ResourceValidator()
        self.url_generator = URLGenerator(config)
        self.response_generator = ResponseGenerator(config)
        self.auth_manager = AuthenticationManager(config)
        self.rate_limiter = RateLimiter(config)
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def add_resource(self, resource: ResourceDefinition) -> List[str]:
        """添加资源"""
        errors = self.validator.validate_resource(resource)
        
        if errors:
            return errors
        
        self.resources[resource.name] = resource
        self.logger.info(f"资源添加成功: {resource.name}")
        return []
    
    def remove_resource(self, resource_name: str) -> bool:
        """移除资源"""
        if resource_name in self.resources:
            del self.resources[resource_name]
            self.logger.info(f"资源移除成功: {resource_name}")
            return True
        return False
    
    def get_resource(self, resource_name: str) -> Optional[ResourceDefinition]:
        """获取资源"""
        return self.resources.get(resource_name)
    
    def list_resources(self) -> List[str]:
        """列出所有资源"""
        return list(self.resources.keys())
    
    def generate_crud_endpoints(self, resource: ResourceDefinition) -> List[EndpointDefinition]:
        """生成CRUD端点"""
        endpoints = []
        
        # 获取资源集合
        endpoints.append(EndpointDefinition(
            path=f"/{resource.name}",
            method=HTTPMethod.GET,
            description=f"获取{resource.name}列表",
            response_body=resource,
            status_codes={
                HTTPStatus.OK: "成功获取资源列表"
            }
        ))
        
        # 创建资源
        endpoints.append(EndpointDefinition(
            path=f"/{resource.name}",
            method=HTTPMethod.POST,
            description=f"创建{resource.name}",
            request_body=resource,
            response_body=resource,
            status_codes={
                HTTPStatus.CREATED: "资源创建成功",
                HTTPStatus.BAD_REQUEST: "请求参数错误",
                HTTPStatus.UNPROCESSABLE_ENTITY: "数据验证失败"
            }
        ))
        
        # 获取单个资源
        endpoints.append(EndpointDefinition(
            path=f"/{resource.name}/{{id}}",
            method=HTTPMethod.GET,
            description=f"获取单个{resource.name}",
            response_body=resource,
            status_codes={
                HTTPStatus.OK: "成功获取资源",
                HTTPStatus.NOT_FOUND: "资源不存在"
            }
        ))
        
        # 更新资源
        endpoints.append(EndpointDefinition(
            path=f"/{resource.name}/{{id}}",
            method=HTTPMethod.PUT,
            description=f"更新{resource.name}",
            request_body=resource,
            response_body=resource,
            status_codes={
                HTTPStatus.OK: "资源更新成功",
                HTTPStatus.BAD_REQUEST: "请求参数错误",
                HTTPStatus.NOT_FOUND: "资源不存在",
                HTTPStatus.UNPROCESSABLE_ENTITY: "数据验证失败"
            }
        ))
        
        # 部分更新资源
        endpoints.append(EndpointDefinition(
            path=f"/{resource.name}/{{id}}",
            method=HTTPMethod.PATCH,
            description=f"部分更新{resource.name}",
            request_body=resource,
            response_body=resource,
            status_codes={
                HTTPStatus.OK: "资源更新成功",
                HTTPStatus.BAD_REQUEST: "请求参数错误",
                HTTPStatus.NOT_FOUND: "资源不存在",
                HTTPStatus.UNPROCESSABLE_ENTITY: "数据验证失败"
            }
        ))
        
        # 删除资源
        endpoints.append(EndpointDefinition(
            path=f"/{resource.name}/{{id}}",
            method=HTTPMethod.DELETE,
            description=f"删除{resource.name}",
            status_codes={
                HTTPStatus.NO_CONTENT: "资源删除成功",
                HTTPStatus.NOT_FOUND: "资源不存在"
            }
        ))
        
        return endpoints
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """生成OpenAPI规范"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.config.api_name,
                "version": self.config.api_version,
                "description": self.config.description
            },
            "servers": [
                {
                    "url": self.config.base_url,
                    "description": "API服务器"
                }
            ],
            "paths": {}
        }
        
        # 生成路径
        for resource_name, resource in self.resources.items():
            resource_paths = self._generate_resource_paths(resource)
            spec["paths"].update(resource_paths)
        
        # 生成组件
        spec["components"] = {
            "schemas": self._generate_schemas(),
            "securitySchemes": self._generate_security_schemes()
        }
        
        return spec
    
    def _generate_resource_paths(self, resource: ResourceDefinition) -> Dict[str, Any]:
        """生成资源路径"""
        paths = {}
        
        for endpoint in resource.endpoints:
            path_key = endpoint.path.replace("{id}", f"{resource.name}_id")
            
            if path_key not in paths:
                paths[path_key] = {}
            
            operation = {
                "summary": endpoint.description,
                "description": endpoint.description,
                "responses": {}
            }
            
            # 添加响应
            for status_code, description in endpoint.status_codes.items():
                operation["responses"][status_code.value] = {
                    "description": description,
                    "content": {
                        self.config.default_content_type: {
                            "schema": {"$ref": f"#/components/schemas/{resource.name}"}
                        }
                    }
                }
            
            # 添加请求体
            if endpoint.request_body:
                operation["requestBody"] = {
                    "content": {
                        self.config.default_content_type: {
                            "schema": {"$ref": f"#/components/schemas/{resource.name}"}
                        }
                    }
                }
            
            # 添加参数
            if endpoint.parameters:
                operation["parameters"] = []
                for param in endpoint.parameters:
                    operation["parameters"].append({
                        "name": param.name,
                        "in": "query",
                        "required": param.required,
                        "schema": {
                            "type": param.data_type.value
                        }
                    })
            
            # 添加安全要求
            if endpoint.authentication_required:
                operation["security"] = [{}]
                if self.config.authentication_type == "api_key":
                    operation["security"][0]["ApiKeyAuth"] = []
                elif self.config.authentication_type == "jwt":
                    operation["security"][0]["BearerAuth"] = []
            
            paths[path_key][endpoint.method.value.lower()] = operation
        
        return paths
    
    def _generate_schemas(self) -> Dict[str, Any]:
        """生成数据模型"""
        schemas = {}
        
        for resource_name, resource in self.resources.items():
            schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for field in resource.fields:
                prop_schema = {
                    "type": field.data_type.value
                }
                
                if field.description:
                    prop_schema["description"] = field.description
                
                if field.default is not None:
                    prop_schema["default"] = field.default
                
                schema["properties"][field.name] = prop_schema
                
                if field.required:
                    schema["required"].append(field.name)
            
            schemas[resource_name] = schema
        
        return schemas
    
    def _generate_security_schemes(self) -> Dict[str, Any]:
        """生成安全方案"""
        schemes = {}
        
        if self.config.authentication_type == "api_key":
            schemes["ApiKeyAuth"] = {
                "type": "apiKey",
                "in": "header",
                "name": self.config.api_key_header
            }
        elif self.config.authentication_type == "jwt":
            schemes["BearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        
        return schemes
    
    def validate_request_data(self, resource_name: str, data: Dict[str, Any]) -> List[str]:
        """验证请求数据"""
        resource = self.resources.get(resource_name)
        
        if not resource:
            return [f"资源不存在: {resource_name}"]
        
        errors = []
        
        # 验证必填字段
        for field in resource.fields:
            if field.required and field.name not in data:
                errors.append(f"缺少必填字段: {field.name}")
        
        # 验证字段类型
        for field_name, field_value in data.items():
            field = next((f for f in resource.fields if f.name == field_name), None)
            
            if field:
                if not self._validate_field_type(field_value, field.data_type):
                    errors.append(f"字段类型错误: {field_name}")
        
        return errors
    
    def _validate_field_type(self, value: Any, data_type: DataType) -> bool:
        """验证字段类型"""
        if data_type == DataType.STRING:
            return isinstance(value, str)
        elif data_type == DataType.INTEGER:
            return isinstance(value, int)
        elif data_type == DataType.FLOAT:
            return isinstance(value, (int, float))
        elif data_type == DataType.BOOLEAN:
            return isinstance(value, bool)
        elif data_type == DataType.ARRAY:
            return isinstance(value, list)
        elif data_type == DataType.OBJECT:
            return isinstance(value, dict)
        
        return True

# 使用示例
# 配置API
config = APIConfiguration(
    api_name="User Management API",
    api_version="v1",
    base_url="https://api.example.com",
    description="用户管理API",
    authentication_type="jwt",
    enable_cors=True,
    cors_origins=["*"],
    enable_caching=True,
    cache_ttl=300,
    default_page_size=20,
    max_page_size=100
)

# 创建API设计器
designer = RESTfulAPIDesigner(config)

# 定义用户资源
user_resource = ResourceDefinition(
    name="users",
    description="用户资源",
    fields=[
        ResourceField(
            name="id",
            data_type=DataType.INTEGER,
            required=False,
            read_only=True,
            description="用户ID"
        ),
        ResourceField(
            name="username",
            data_type=DataType.STRING,
            required=True,
            description="用户名"
        ),
        ResourceField(
            name="email",
            data_type=DataType.STRING,
            required=True,
            description="邮箱地址"
        ),
        ResourceField(
            name="password",
            data_type=DataType.STRING,
            required=True,
            write_only=True,
            description="密码"
        ),
        ResourceField(
            name="created_at",
            data_type=DataType.DATETIME,
            required=False,
            read_only=True,
            description="创建时间"
        )
    ]
)

# 添加资源
errors = designer.add_resource(user_resource)
if errors:
    print(f"添加资源失败: {errors}")
else:
    print("资源添加成功")

# 生成CRUD端点
crud_endpoints = designer.generate_crud_endpoints(user_resource)
user_resource.endpoints = crud_endpoints

# 生成OpenAPI规范
openapi_spec = designer.generate_openapi_spec()
print(f"\nOpenAPI规范:")
print(json.dumps(openapi_spec, indent=2, ensure_ascii=False))

# 验证请求数据
test_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secret123"
}

validation_errors = designer.validate_request_data("users", test_data)
if validation_errors:
    print(f"\n数据验证失败: {validation_errors}")
else:
    print("\n数据验证成功")

# 生成示例响应
success_response = designer.response_generator.generate_success_response(
    data={"id": 1, "username": "john_doe", "email": "john@example.com"},
    status_code=HTTPStatus.CREATED
)

print(f"\n成功响应示例:")
print(json.dumps(success_response, indent=2, ensure_ascii=False))

# 测试认证
auth_result, error_message = designer.auth_manager.authenticate_request({
    "Authorization": "Bearer valid.jwt.token"
})

print(f"\n认证结果: {auth_result}")
if error_message:
    print(f"认证错误: {error_message}")

# 测试频率限制
client_id = "192.168.1.100"
for i in range(5):
    can_request = designer.rate_limiter.check_rate_limit(client_id, limit=10)
    remaining = designer.rate_limiter.get_remaining_requests(client_id, limit=10)
    print(f"请求 {i+1}: {'允许' if can_request else '拒绝'}, 剩余: {remaining}")

print(f"\n资源列表: {designer.list_resources()}")
```

## 参考资源

### RESTful设计原则
- [REST架构风格](https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm)
- [RESTful API设计指南](https://restfulapi.net/)
- [HTTP状态码规范](https://httpstatuses.com/)
- [REST API最佳实践](https://www.moesif.com/blog/technical/rest-api-best-practices/)

### API设计工具
- [OpenAPI规范](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Postman API设计](https://www.postman.com/api-design/)
- [API Blueprint](https://apiblueprint.org/)

### 认证授权
- [OAuth 2.0规范](https://tools.ietf.org/html/rfc6749)
- [JWT规范](https://tools.ietf.org/html/rfc7519)
- [API Key最佳实践](https://cloud.google.com/endpoints/docs/openapi/when-why-api-key)
- [CORS安全指南](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

### 性能优化
- [HTTP缓存机制](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [API分页策略](https://www.moesif.com/blog/technical/api-design/REST-API-Design-Pagination/)
- [API压缩优化](https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/compression)
- [CDN最佳实践](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/)
