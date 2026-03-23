# 服务通信参考文档

## 服务通信概述

### 什么是服务通信
服务通信是微服务架构中服务之间交换信息和协调工作的机制。它包括同步通信（如REST API、gRPC）和异步通信（如消息队列、事件驱动）两种主要模式。

### 通信模式分类

#### 同步通信
- **REST API**: 基于HTTP协议的轻量级通信方式
- **gRPC**: 基于HTTP/2的高性能RPC框架
- **WebSocket**: 支持双向实时通信的协议
- **GraphQL**: 灵活的API查询语言

#### 异步通信
- **消息队列**: 可靠的消息传递机制
- **事件驱动**: 基于事件的松耦合通信
- **发布订阅**: 一对多的消息分发模式
- **流处理**: 实时数据流处理

## REST API通信

### REST API设计原则

#### 资源导向设计
```python
# 用户服务REST API示例
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound, BadRequest

app = Flask(__name__)
api = Api(app)

# 用户数据模型
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

# 模拟数据库
users_db = {
    1: User(1, 'John Doe', 'john@example.com'),
    2: User(2, 'Jane Smith', 'jane@example.com'),
    3: User(3, 'Bob Johnson', 'bob@example.com')
}

# 用户资源
class UserResource(Resource):
    def get(self, user_id):
        """获取单个用户"""
        if user_id not in users_db:
            raise NotFound(f"用户 {user_id} 不存在")
        
        user = users_db[user_id]
        return {
            'success': True,
            'data': user.to_dict(),
            'message': '用户获取成功'
        }
    
    def put(self, user_id):
        """更新用户"""
        if user_id not in users_db:
            raise NotFound(f"用户 {user_id} 不存在")
        
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        user = users_db[user_id]
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        
        return {
            'success': True,
            'data': user.to_dict(),
            'message': '用户更新成功'
        }
    
    def delete(self, user_id):
        """删除用户"""
        if user_id not in users_db:
            raise NotFound(f"用户 {user_id} 不存在")
        
        del users_db[user_id]
        
        return {
            'success': True,
            'message': '用户删除成功'
        }

# 用户集合资源
class UserListResource(Resource):
    def get(self):
        """获取用户列表"""
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        # 搜索过滤
        filtered_users = []
        for user in users_db.values():
            if search.lower() in user.name.lower() or search.lower() in user.email.lower():
                filtered_users.append(user)
        
        # 分页
        total = len(filtered_users)
        start = (page - 1) * per_page
        end = start + per_page
        users_page = filtered_users[start:end]
        
        return {
            'success': True,
            'data': {
                'users': [user.to_dict() for user in users_page],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            },
            'message': '用户列表获取成功'
        }
    
    def post(self):
        """创建用户"""
        data = request.get_json()
        if not data:
            raise BadRequest("请求体不能为空")
        
        # 验证必填字段
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"字段 {field} 是必填的")
        
        # 生成新ID
        new_id = max(users_db.keys()) + 1 if users_db else 1
        
        # 创建用户
        user = User(new_id, data['name'], data['email'])
        users_db[new_id] = user
        
        return {
            'success': True,
            'data': user.to_dict(),
            'message': '用户创建成功'
        }, 201

# 注册路由
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')

# 错误处理
@app.errorhandler(NotFound)
def handle_not_found(error):
    return jsonify({
        'success': False,
        'error': 'NOT_FOUND',
        'message': str(error)
    }), 404

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    return jsonify({
        'success': False,
        'error': 'BAD_REQUEST',
        'message': str(error)
    }), 400

@app.errorhandler(Exception)
def handle_exception(error):
    return jsonify({
        'success': False,
        'error': 'INTERNAL_SERVER_ERROR',
        'message': '服务器内部错误'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
```

#### HTTP状态码最佳实践
```python
# HTTP状态码使用指南
class HTTPStatusCodes:
    # 成功状态码 (2xx)
    OK = 200                    # 请求成功
    CREATED = 201              # 资源创建成功
    ACCEPTED = 202              # 请求已接受，正在处理
    NO_CONTENT = 204           # 请求成功，无返回内容
    
    # 重定向状态码 (3xx)
    MOVED_PERMANENTLY = 301     # 永久重定向
    FOUND = 302                 # 临时重定向
    NOT_MODIFIED = 304          # 资源未修改
    
    # 客户端错误 (4xx)
    BAD_REQUEST = 400           # 请求错误
    UNAUTHORIZED = 401          # 未授权
    FORBIDDEN = 403             # 禁止访问
    NOT_FOUND = 404             # 资源不存在
    METHOD_NOT_ALLOWED = 405    # 方法不允许
    CONFLICT = 409              # 资源冲突
    UNPROCESSABLE_ENTITY = 422  # 请求格式正确但语义错误
    TOO_MANY_REQUESTS = 429     # 请求过多
    
    # 服务端错误 (5xx)
    INTERNAL_SERVER_ERROR = 500 # 服务器内部错误
    BAD_GATEWAY = 502           # 网关错误
    SERVICE_UNAVAILABLE = 503   # 服务不可用
    GATEWAY_TIMEOUT = 504       # 网关超时

# 状态码使用示例
def create_user(data):
    try:
        # 验证数据
        if not validate_user_data(data):
            return {
                'success': False,
                'error': 'VALIDATION_ERROR',
                'message': '用户数据验证失败'
            }, HTTPStatusCodes.UNPROCESSABLE_ENTITY
        
        # 检查用户是否已存在
        if user_exists(data['email']):
            return {
                'success': False,
                'error': 'USER_EXISTS',
                'message': '用户已存在'
            }, HTTPStatusCodes.CONFLICT
        
        # 创建用户
        user = save_user(data)
        
        return {
            'success': True,
            'data': user.to_dict(),
            'message': '用户创建成功'
        }, HTTPStatusCodes.CREATED
        
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        return {
            'success': False,
            'error': 'INTERNAL_ERROR',
            'message': '服务器内部错误'
        }, HTTPStatusCodes.INTERNAL_SERVER_ERROR
```

### API版本控制

#### URL路径版本控制
```python
# URL路径版本控制示例
from flask import Blueprint

# v1 API
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/users', methods=['GET'])
def get_users_v1():
    return jsonify({
        'version': 'v1',
        'data': get_users_data_v1()
    })

# v2 API
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

@api_v2.route('/users', methods=['GET'])
def get_users_v2():
    return jsonify({
        'version': 'v2',
        'data': get_users_data_v2(),
        'metadata': {
            'total_count': len(get_all_users()),
            'page': 1,
            'per_page': 10
        }
    })

# 注册蓝图
app.register_blueprint(api_v1)
app.register_blueprint(api_v2)
```

#### Header版本控制
```python
# Header版本控制示例
from flask import request

@app.route('/api/users')
def get_users():
    # 从Header获取版本
    version = request.headers.get('API-Version', 'v1')
    
    if version == 'v1':
        return jsonify(get_users_v1())
    elif version == 'v2':
        return jsonify(get_users_v2())
    else:
        return jsonify({
            'error': 'UNSUPPORTED_VERSION',
            'message': f'版本 {version} 不支持'
        }), 400
```

## gRPC通信

### Protocol Buffers定义

#### 服务定义示例
```protobuf
// user_service.proto
syntax = "proto3";

package user;

// 用户服务定义
service UserService {
  // 获取用户信息
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  
  // 创建用户
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  
  // 更新用户
  rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
  
  // 删除用户
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
  
  // 获取用户列表（服务端流）
  rpc ListUsers(ListUsersRequest) returns (stream ListUsersResponse);
  
  // 批量创建用户（客户端流）
  rpc BatchCreateUsers(stream CreateUserRequest) returns (BatchCreateUsersResponse);
  
  // 双向流聊天
  rpc UserChat(stream UserChatRequest) returns (stream UserChatResponse);
}

// 用户消息
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
  string phone = 4;
  repeated Address addresses = 5;
  map<string, string> metadata = 6;
}

// 地址消息
message Address {
  string street = 1;
  string city = 2;
  string state = 3;
  string zip_code = 4;
  string country = 5;
}

// 请求消息
message GetUserRequest {
  int32 user_id = 1;
  bool include_addresses = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
  string phone = 3;
  repeated Address addresses = 4;
  map<string, string> metadata = 5;
}

message UpdateUserRequest {
  int32 user_id = 1;
  string name = 2;
  string email = 3;
  string phone = 4;
  repeated Address addresses = 5;
  map<string, string> metadata = 6;
}

message DeleteUserRequest {
  int32 user_id = 1;
}

message ListUsersRequest {
  int32 page = 1;
  int32 per_page = 2;
  string search = 3;
  repeated string tags = 4;
}

message UserChatRequest {
  string message = 1;
  int64 timestamp = 2;
}

// 响应消息
message GetUserResponse {
  User user = 1;
  string message = 2;
}

message CreateUserResponse {
  User user = 1;
  string message = 2;
}

message UpdateUserResponse {
  User user = 1;
  string message = 2;
}

message DeleteUserResponse {
  bool success = 1;
  string message = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total_count = 2;
  int32 current_page = 3;
  int32 per_page = 4;
}

message BatchCreateUsersResponse {
  repeated User users = 1;
  int32 success_count = 2;
  int32 failure_count = 3;
  repeated string errors = 4;
}

message UserChatResponse {
  string message = 1;
  int64 timestamp = 2;
  string sender = 3;
}
```

### gRPC服务实现

#### Python gRPC服务端
```python
# user_service_server.py
import grpc
from concurrent import futures
import time
from generated import user_service_pb2
from generated import user_service_pb2_grpc

class UserServiceImpl(user_service_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def GetUser(self, request, context):
        """获取用户信息"""
        user_id = request.user_id
        
        if user_id not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"用户 {user_id} 不存在")
            return user_service_pb2.GetUserResponse()
        
        user = self.users[user_id]
        
        # 如果不需要地址信息，清空地址
        if not request.include_addresses:
            user.addresses.clear()
        
        return user_service_pb2.GetUserResponse(
            user=user,
            message="用户获取成功"
        )
    
    def CreateUser(self, request, context):
        """创建用户"""
        user = user_service_pb2.User(
            id=self.next_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            addresses=request.addresses,
            metadata=request.metadata
        )
        
        self.users[self.next_id] = user
        self.next_id += 1
        
        return user_service_pb2.CreateUserResponse(
            user=user,
            message="用户创建成功"
        )
    
    def UpdateUser(self, request, context):
        """更新用户"""
        user_id = request.user_id
        
        if user_id not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"用户 {user_id} 不存在")
            return user_service_pb2.UpdateUserResponse()
        
        user = self.users[user_id]
        
        # 更新字段
        if request.name:
            user.name = request.name
        if request.email:
            user.email = request.email
        if request.phone:
            user.phone = request.phone
        if request.addresses:
            user.addresses[:] = request.addresses
        if request.metadata:
            user.metadata.update(request.metadata)
        
        return user_service_pb2.UpdateUserResponse(
            user=user,
            message="用户更新成功"
        )
    
    def DeleteUser(self, request, context):
        """删除用户"""
        user_id = request.user_id
        
        if user_id not in self.users:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"用户 {user_id} 不存在")
            return user_service_pb2.DeleteUserResponse()
        
        del self.users[user_id]
        
        return user_service_pb2.DeleteUserResponse(
            success=True,
            message="用户删除成功"
        )
    
    def ListUsers(self, request, context):
        """获取用户列表（服务端流）"""
        page = request.page if request.page > 0 else 1
        per_page = request.per_page if request.per_page > 0 else 10
        search = request.search.lower()
        tags = request.tags
        
        # 过滤用户
        filtered_users = []
        for user in self.users.values():
            # 搜索过滤
            if search:
                if search not in user.name.lower() and search not in user.email.lower():
                    continue
            
            # 标签过滤
            if tags:
                user_tags = user.metadata.get('tags', '').split(',')
                if not any(tag in user_tags for tag in tags):
                    continue
            
            filtered_users.append(user)
        
        # 分页
        total_count = len(filtered_users)
        start = (page - 1) * per_page
        end = start + per_page
        users_page = filtered_users[start:end]
        
        # 流式返回
        yield user_service_pb2.ListUsersResponse(
            users=users_page,
            total_count=total_count,
            current_page=page,
            per_page=per_page
        )
    
    def BatchCreateUsers(self, request_iterator, context):
        """批量创建用户（客户端流）"""
        created_users = []
        errors = []
        
        for request in request_iterator:
            try:
                user = user_service_pb2.User(
                    id=self.next_id,
                    name=request.name,
                    email=request.email,
                    phone=request.phone,
                    addresses=request.addresses,
                    metadata=request.metadata
                )
                
                self.users[self.next_id] = user
                created_users.append(user)
                self.next_id += 1
                
            except Exception as e:
                errors.append(f"创建用户失败: {str(e)}")
        
        return user_service_pb2.BatchCreateUsersResponse(
            users=created_users,
            success_count=len(created_users),
            failure_count=len(errors),
            errors=errors
        )
    
    def UserChat(self, request_iterator, context):
        """双向流聊天"""
        for request in request_iterator:
            # 处理消息
            response_message = f"收到消息: {request.message}"
            
            # 返回响应
            yield user_service_pb2.UserChatResponse(
                message=response_message,
                timestamp=int(time.time()),
                sender="server"
            )

def serve():
    """启动gRPC服务"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 添加服务
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceImpl(), server
    )
    
    # 添加监听端口
    server.add_insecure_port('[::]:50051')
    
    # 启动服务
    print("gRPC服务启动，监听端口 50051")
    server.start()
    
    try:
        while True:
            time.sleep(86400)  # 一天
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
```

#### Python gRPC客户端
```python
# user_service_client.py
import grpc
from generated import user_service_pb2
from generated import user_service_pb2_grpc

class UserServiceClient:
    def __init__(self, server_address='localhost:50051'):
        self.channel = grpc.insecure_channel(server_address)
        self.stub = user_service_pb2_grpc.UserServiceStub(self.channel)
    
    def get_user(self, user_id, include_addresses=False):
        """获取用户信息"""
        try:
            request = user_service_pb2.GetUserRequest(
                user_id=user_id,
                include_addresses=include_addresses
            )
            response = self.stub.GetUser(request)
            return response
        except grpc.RpcError as e:
            print(f"获取用户失败: {e.code()} - {e.details()}")
            return None
    
    def create_user(self, name, email, phone="", addresses=None, metadata=None):
        """创建用户"""
        try:
            request = user_service_pb2.CreateUserRequest(
                name=name,
                email=email,
                phone=phone,
                addresses=addresses or [],
                metadata=metadata or {}
            )
            response = self.stub.CreateUser(request)
            return response
        except grpc.RpcError as e:
            print(f"创建用户失败: {e.code()} - {e.details()}")
            return None
    
    def update_user(self, user_id, **kwargs):
        """更新用户"""
        try:
            request = user_service_pb2.UpdateUserRequest(
                user_id=user_id,
                **kwargs
            )
            response = self.stub.UpdateUser(request)
            return response
        except grpc.RpcError as e:
            print(f"更新用户失败: {e.code()} - {e.details()}")
            return None
    
    def delete_user(self, user_id):
        """删除用户"""
        try:
            request = user_service_pb2.DeleteUserRequest(user_id=user_id)
            response = self.stub.DeleteUser(request)
            return response
        except grpc.RpcError as e:
            print(f"删除用户失败: {e.code()} - {e.details()}")
            return None
    
    def list_users(self, page=1, per_page=10, search="", tags=None):
        """获取用户列表"""
        try:
            request = user_service_pb2.ListUsersRequest(
                page=page,
                per_page=per_page,
                search=search,
                tags=tags or []
            )
            
            users = []
            for response in self.stub.ListUsers(request):
                users.extend(response.users)
                print(f"收到第 {response.current_page} 页，共 {response.total_count} 个用户")
            
            return users
        except grpc.RpcError as e:
            print(f"获取用户列表失败: {e.code()} - {e.details()}")
            return []
    
    def batch_create_users(self, users_data):
        """批量创建用户"""
        try:
            def generate_requests():
                for user_data in users_data:
                    yield user_service_pb2.CreateUserRequest(**user_data)
            
            response = self.stub.BatchCreateUsers(generate_requests())
            return response
        except grpc.RpcError as e:
            print(f"批量创建用户失败: {e.code()} - {e.details()}")
            return None
    
    def user_chat(self, messages):
        """双向流聊天"""
        try:
            def generate_requests():
                for message in messages:
                    yield user_service_pb2.UserChatRequest(
                        message=message,
                        timestamp=int(time.time())
                    )
            
            responses = self.stub.UserChat(generate_requests())
            for response in responses:
                print(f"服务器响应: {response.message}")
        except grpc.RpcError as e:
            print(f"聊天失败: {e.code()} - {e.details()}")
    
    def close(self):
        """关闭连接"""
        self.channel.close()

# 使用示例
def main():
    client = UserServiceClient()
    
    try:
        # 创建用户
        print("创建用户...")
        create_response = client.create_user(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            metadata={"department": "engineering", "role": "developer"}
        )
        
        if create_response:
            print(f"创建用户成功: {create_response.user}")
            user_id = create_response.user.id
        else:
            return
        
        # 获取用户
        print("\n获取用户...")
        get_response = client.get_user(user_id, include_addresses=True)
        if get_response:
            print(f"用户信息: {get_response.user}")
        
        # 更新用户
        print("\n更新用户...")
        update_response = client.update_user(
            user_id=user_id,
            phone="987-654-3210",
            metadata={"department": "engineering", "role": "senior_developer"}
        )
        if update_response:
            print(f"更新用户成功: {update_response.user}")
        
        # 获取用户列表
        print("\n获取用户列表...")
        users = client.list_users(page=1, per_page=5)
        print(f"用户列表: {users}")
        
        # 批量创建用户
        print("\n批量创建用户...")
        batch_data = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"}
        ]
        batch_response = client.batch_create_users(batch_data)
        if batch_response:
            print(f"批量创建成功: {batch_response.success_count} 个用户")
        
        # 双向流聊天
        print("\n双向流聊天...")
        chat_messages = ["Hello", "How are you?", "Goodbye"]
        client.user_chat(chat_messages)
        
    finally:
        client.close()

if __name__ == '__main__':
    main()
```

## 消息队列通信

### RabbitMQ实现

#### 生产者实现
```python
# rabbitmq_producer.py
import pika
import json
import time
from typing import Dict, Any

class RabbitMQProducer:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.connection = None
        self.channel = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password
    
    def connect(self):
        """连接到RabbitMQ"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        print("连接到RabbitMQ成功")
    
    def declare_queue(self, queue_name: str, durable: bool = True):
        """声明队列"""
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=False,
            auto_delete=False
        )
        print(f"声明队列: {queue_name}")
    
    def declare_exchange(self, exchange_name: str, exchange_type: str = 'direct'):
        """声明交换机"""
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        print(f"声明交换机: {exchange_name} (类型: {exchange_type})")
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        """绑定队列到交换机"""
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        print(f"绑定队列 {queue_name} 到交换机 {exchange_name} (路由键: {routing_key})")
    
    def publish_message(self, exchange_name: str, routing_key: str, message: Dict[str, Any], 
                       persistent: bool = True):
        """发布消息"""
        message_json = json.dumps(message, ensure_ascii=False)
        
        properties = pika.BasicProperties(
            delivery_mode=2 if persistent else 1,  # 2: 持久化, 1: 非持久化
            content_type='application/json',
            content_encoding='utf-8',
            timestamp=time.time(),
            message_id=str(int(time.time() * 1000))
        )
        
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message_json.encode('utf-8'),
            properties=properties
        )
        
        print(f"发布消息到 {exchange_name}/{routing_key}: {message_json}")
    
    def publish_batch_messages(self, exchange_name: str, routing_key: str, 
                              messages: list, persistent: bool = True):
        """批量发布消息"""
        for message in messages:
            self.publish_message(exchange_name, routing_key, message, persistent)
    
    def close(self):
        """关闭连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("RabbitMQ连接已关闭")

# 使用示例
def main():
    producer = RabbitMQProducer()
    
    try:
        # 连接到RabbitMQ
        producer.connect()
        
        # 声明交换机
        producer.declare_exchange('user_events', 'topic')
        
        # 声明队列
        producer.declare_queue('user_created_queue')
        producer.declare_queue('user_updated_queue')
        producer.declare_queue('user_deleted_queue')
        
        # 绑定队列
        producer.bind_queue('user_created_queue', 'user_events', 'user.created')
        producer.bind_queue('user_updated_queue', 'user_events', 'user.updated')
        producer.bind_queue('user_deleted_queue', 'user_events', 'user.deleted')
        
        # 发布用户创建事件
        user_created_event = {
            'event_type': 'user.created',
            'event_id': 'evt_123',
            'timestamp': time.time(),
            'data': {
                'user_id': 123,
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        
        producer.publish_message('user_events', 'user.created', user_created_event)
        
        # 发布用户更新事件
        user_updated_event = {
            'event_type': 'user.updated',
            'event_id': 'evt_124',
            'timestamp': time.time(),
            'data': {
                'user_id': 123,
                'name': 'John Smith',
                'email': 'john.smith@example.com'
            }
        }
        
        producer.publish_message('user_events', 'user.updated', user_updated_event)
        
        # 批量发布消息
        batch_events = [
            {
                'event_type': 'user.created',
                'event_id': f'evt_{i}',
                'timestamp': time.time(),
                'data': {
                    'user_id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com'
                }
            }
            for i in range(100, 105)
        ]
        
        producer.publish_batch_messages('user_events', 'user.created', batch_events)
        
        # 等待消息确认
        time.sleep(2)
        
    except Exception as e:
        print(f"生产者错误: {e}")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
```

#### 消费者实现
```python
# rabbitmq_consumer.py
import pika
import json
import time
from typing import Callable, Dict, Any

class RabbitMQConsumer:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.connection = None
        self.channel = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.message_handlers = {}
    
    def connect(self):
        """连接到RabbitMQ"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        print("连接到RabbitMQ成功")
    
    def setup_queue(self, queue_name: str, durable: bool = True):
        """设置队列"""
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=False,
            auto_delete=False
        )
        print(f"设置队列: {queue_name}")
    
    def setup_exchange(self, exchange_name: str, exchange_type: str = 'direct'):
        """设置交换机"""
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        print(f"设置交换机: {exchange_name} (类型: {exchange_type})")
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        """绑定队列到交换机"""
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        print(f"绑定队列 {queue_name} 到交换机 {exchange_name} (路由键: {routing_key})")
    
    def register_handler(self, routing_key: str, handler: Callable[[Dict[str, Any]], None]):
        """注册消息处理器"""
        self.message_handlers[routing_key] = handler
        print(f"注册消息处理器: {routing_key}")
    
    def message_callback(self, ch, method, properties, body):
        """消息回调函数"""
        try:
            # 解析消息
            message = json.loads(body.decode('utf-8'))
            routing_key = method.routing_key
            
            print(f"收到消息: {routing_key} - {message}")
            
            # 处理消息
            if routing_key in self.message_handlers:
                handler = self.message_handlers[routing_key]
                handler(message)
            else:
                print(f"未找到处理器: {routing_key}")
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"消息确认: {method.delivery_tag}")
            
        except json.JSONDecodeError as e:
            print(f"消息解析失败: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print(f"消息处理失败: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self, queue_name: str, prefetch_count: int = 1):
        """开始消费消息"""
        # 设置预取数量
        self.channel.basic_qos(prefetch_count=prefetch_count)
        
        # 设置消费者
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.message_callback,
            auto_ack=False
        )
        
        print(f"开始消费队列: {queue_name}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("停止消费")
            self.channel.stop_consuming()
    
    def close(self):
        """关闭连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("RabbitMQ连接已关闭")

# 消息处理器示例
def handle_user_created(message: Dict[str, Any]):
    """处理用户创建事件"""
    print(f"处理用户创建事件: {message}")
    user_data = message.get('data', {})
    
    # 业务逻辑：发送欢迎邮件
    print(f"发送欢迎邮件给 {user_data.get('name')} ({user_data.get('email')})")
    
    # 业务逻辑：创建用户档案
    print(f"创建用户档案: {user_data.get('user_id')}")

def handle_user_updated(message: Dict[str, Any]):
    """处理用户更新事件"""
    print(f"处理用户更新事件: {message}")
    user_data = message.get('data', {})
    
    # 业务逻辑：更新缓存
    print(f"更新用户缓存: {user_data.get('user_id')}")
    
    # 业务逻辑：发送通知
    print(f"发送更新通知给 {user_data.get('name')}")

def handle_user_deleted(message: Dict[str, Any]):
    """处理用户删除事件"""
    print(f"处理用户删除事件: {message}")
    user_data = message.get('data', {})
    
    # 业务逻辑：清理相关数据
    print(f"清理用户相关数据: {user_data.get('user_id')}")
    
    # 业务逻辑：归档用户数据
    print(f"归档用户数据: {user_data.get('user_id')}")

# 使用示例
def main():
    consumer = RabbitMQConsumer()
    
    try:
        # 连接到RabbitMQ
        consumer.connect()
        
        # 设置交换机
        consumer.setup_exchange('user_events', 'topic')
        
        # 设置队列
        consumer.setup_queue('user_created_queue')
        consumer.setup_queue('user_updated_queue')
        consumer.setup_queue('user_deleted_queue')
        
        # 绑定队列
        consumer.bind_queue('user_created_queue', 'user_events', 'user.created')
        consumer.bind_queue('user_updated_queue', 'user_events', 'user.updated')
        consumer.bind_queue('user_deleted_queue', 'user_events', 'user.deleted')
        
        # 注册消息处理器
        consumer.register_handler('user.created', handle_user_created)
        consumer.register_handler('user.updated', handle_user_updated)
        consumer.register_handler('user.deleted', handle_user_deleted)
        
        # 开始消费消息
        consumer.start_consuming('user_created_queue')
        
    except Exception as e:
        print(f"消费者错误: {e}")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
```

### Kafka实现

#### Kafka生产者
```python
# kafka_producer.py
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
from typing import Dict, Any

class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.producer = None
        self.bootstrap_servers = bootstrap_servers
    
    def connect(self):
        """连接到Kafka"""
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # 等待所有副本确认
            retries=3,  # 重试次数
            retry_backoff_ms=100,  # 重试间隔
            batch_size=16384,  # 批量大小
            linger_ms=10,  # 等待时间
            buffer_memory=33554432,  # 缓冲区大小
            compression_type='gzip'  # 压缩类型
        )
        print("连接到Kafka成功")
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """发送消息"""
        try:
            # 添加元数据
            message['timestamp'] = time.time()
            message['producer_id'] = 'producer_1'
            
            # 发送消息
            future = self.producer.send(
                topic=topic,
                key=key,
                value=message
            )
            
            # 等待发送完成
            record_metadata = future.get(timeout=10)
            
            print(f"消息发送成功: {record_metadata.topic}:{record_metadata.partition}:{record_metadata.offset}")
            
            return record_metadata
            
        except KafkaError as e:
            print(f"消息发送失败: {e}")
            return None
        except Exception as e:
            print(f"发送消息异常: {e}")
            return None
    
    def send_batch_messages(self, topic: str, messages: list, key_prefix: str = None):
        """批量发送消息"""
        results = []
        
        for i, message in enumerate(messages):
            key = f"{key_prefix}_{i}" if key_prefix else None
            result = self.send_message(topic, message, key)
            results.append(result)
        
        # 等待所有消息发送完成
        self.producer.flush()
        
        return results
    
    def close(self):
        """关闭生产者"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("Kafka生产者已关闭")

# 使用示例
def main():
    producer = KafkaProducerWrapper()
    
    try:
        # 连接到Kafka
        producer.connect()
        
        # 发送用户事件
        user_events = [
            {
                'event_type': 'user.created',
                'event_id': 'evt_001',
                'data': {
                    'user_id': 1,
                    'name': 'Alice',
                    'email': 'alice@example.com'
                }
            },
            {
                'event_type': 'user.updated',
                'event_id': 'evt_002',
                'data': {
                    'user_id': 1,
                    'name': 'Alice Smith',
                    'email': 'alice.smith@example.com'
                }
            },
            {
                'event_type': 'user.deleted',
                'event_id': 'evt_003',
                'data': {
                    'user_id': 1
                }
            }
        ]
        
        # 发送单个消息
        for event in user_events:
            producer.send_message('user_events', event, key=str(event['data']['user_id']))
        
        # 批量发送消息
        batch_events = [
            {
                'event_type': 'user.created',
                'event_id': f'evt_{i}',
                'data': {
                    'user_id': i,
                    'name': f'User {i}',
                    'email': f'user{i}@example.com'
                }
            }
            for i in range(100, 110)
        ]
        
        producer.send_batch_messages('user_events', batch_events, 'batch_user')
        
    except Exception as e:
        print(f"生产者错误: {e}")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
```

#### Kafka消费者
```python
# kafka_consumer.py
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import time
from typing import Callable, Dict, Any

class KafkaConsumerWrapper:
    def __init__(self, bootstrap_servers=['localhost:9092'], group_id='user_events_group'):
        self.consumer = None
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.message_handlers = {}
    
    def connect(self, topics: list):
        """连接到Kafka并订阅主题"""
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',  # 从最早的消息开始
            enable_auto_commit=True,  # 自动提交偏移量
            auto_commit_interval_ms=1000,  # 自动提交间隔
            session_timeout_ms=30000,  # 会话超时
            heartbeat_interval_ms=3000,  # 心跳间隔
            max_poll_records=100,  # 最大拉取记录数
            max_poll_interval_ms=300000,  # 最大拉取间隔
            consumer_timeout_ms=1000  # 消费者超时
        )
        print(f"连接到Kafka成功，订阅主题: {topics}")
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """注册事件处理器"""
        self.message_handlers[event_type] = handler
        print(f"注册事件处理器: {event_type}")
    
    def process_message(self, message):
        """处理消息"""
        try:
            topic = message.topic
            partition = message.partition
            offset = message.offset
            key = message.key
            value = message.value
            
            print(f"收到消息: {topic}:{partition}:{offset} - Key: {key}, Value: {value}")
            
            # 获取事件类型
            event_type = value.get('event_type')
            
            if event_type in self.message_handlers:
                handler = self.message_handlers[event_type]
                handler(value)
            else:
                print(f"未找到处理器: {event_type}")
            
        except Exception as e:
            print(f"处理消息失败: {e}")
    
    def start_consuming(self):
        """开始消费消息"""
        print("开始消费消息...")
        
        try:
            for message in self.consumer:
                self.process_message(message)
                
        except KeyboardInterrupt:
            print("停止消费")
        except KafkaError as e:
            print(f"Kafka错误: {e}")
        except Exception as e:
            print(f"消费异常: {e}")
    
    def close(self):
        """关闭消费者"""
        if self.consumer:
            self.consumer.close()
            print("Kafka消费者已关闭")

# 事件处理器示例
def handle_user_created(event: Dict[str, Any]):
    """处理用户创建事件"""
    print(f"处理用户创建事件: {event}")
    user_data = event.get('data', {})
    
    # 业务逻辑
    print(f"创建用户档案: {user_data.get('user_id')} - {user_data.get('name')}")

def handle_user_updated(event: Dict[str, Any]):
    """处理用户更新事件"""
    print(f"处理用户更新事件: {event}")
    user_data = event.get('data', {})
    
    # 业务逻辑
    print(f"更新用户档案: {user_data.get('user_id')} - {user_data.get('name')}")

def handle_user_deleted(event: Dict[str, Any]):
    """处理用户删除事件"""
    print(f"处理用户删除事件: {event}")
    user_data = event.get('data', {})
    
    # 业务逻辑
    print(f"删除用户档案: {user_data.get('user_id')}")

# 使用示例
def main():
    consumer = KafkaConsumerWrapper()
    
    try:
        # 连接到Kafka
        consumer.connect(['user_events'])
        
        # 注册事件处理器
        consumer.register_handler('user.created', handle_user_created)
        consumer.register_handler('user.updated', handle_user_updated)
        consumer.register_handler('user.deleted', handle_user_deleted)
        
        # 开始消费消息
        consumer.start_consuming()
        
    except Exception as e:
        print(f"消费者错误: {e}")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()
```

## WebSocket通信

### WebSocket服务端实现

#### Python WebSocket服务端
```python
# websocket_server.py
import asyncio
import websockets
import json
import time
from typing import Dict, Set, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.client_info: Dict[str, Dict[str, Any]] = {}
        self.message_handlers = {}
    
    async def register_client(self, websocket, path):
        """注册客户端"""
        client_id = f"client_{int(time.time() * 1000)}_{len(self.clients)}"
        
        self.clients[client_id] = websocket
        self.client_info[client_id] = {
            'connected_at': time.time(),
            'path': path,
            'last_ping': time.time(),
            'room': None
        }
        
        logger.info(f"客户端注册: {client_id} - {path}")
        
        try:
            # 发送欢迎消息
            await self.send_to_client(client_id, {
                'type': 'welcome',
                'client_id': client_id,
                'message': '连接成功'
            })
            
            # 处理消息
            async for message in websocket:
                await self.handle_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端断开连接: {client_id}")
        except Exception as e:
            logger.error(f"客户端处理错误: {e}")
        finally:
            await self.unregister_client(client_id)
    
    async def unregister_client(self, client_id: str):
        """注销客户端"""
        if client_id in self.clients:
            # 离开房间
            room = self.client_info[client_id].get('room')
            if room and room in self.rooms:
                self.rooms[room].discard(client_id)
                if not self.rooms[room]:
                    del self.rooms[room]
            
            # 清理客户端信息
            del self.clients[client_id]
            del self.client_info[client_id]
            
            logger.info(f"客户端注销: {client_id}")
    
    async def handle_message(self, client_id: str, message: str):
        """处理客户端消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            logger.info(f"收到消息: {client_id} - {message_type}")
            
            # 更新最后心跳时间
            self.client_info[client_id]['last_ping'] = time.time()
            
            # 根据消息类型处理
            if message_type == 'ping':
                await self.handle_ping(client_id, data)
            elif message_type == 'join_room':
                await self.handle_join_room(client_id, data)
            elif message_type == 'leave_room':
                await self.handle_leave_room(client_id, data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(client_id, data)
            elif message_type == 'private_message':
                await self.handle_private_message(client_id, data)
            elif message_type in self.message_handlers:
                await self.message_handlers[message_type](client_id, data)
            else:
                await self.send_to_client(client_id, {
                    'type': 'error',
                    'message': f'未知消息类型: {message_type}'
                })
                
        except json.JSONDecodeError:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '消息格式错误'
            })
        except Exception as e:
            logger.error(f"处理消息错误: {e}")
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '消息处理失败'
            })
    
    async def handle_ping(self, client_id: str, data: Dict[str, Any]):
        """处理心跳"""
        await self.send_to_client(client_id, {
            'type': 'pong',
            'timestamp': time.time()
        })
    
    async def handle_join_room(self, client_id: str, data: Dict[str, Any]):
        """处理加入房间"""
        room = data.get('room')
        if not room:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '房间名不能为空'
            })
            return
        
        # 离开当前房间
        current_room = self.client_info[client_id].get('room')
        if current_room and current_room in self.rooms:
            self.rooms[current_room].discard(client_id)
            if not self.rooms[current_room]:
                del self.rooms[current_room]
        
        # 加入新房间
        if room not in self.rooms:
            self.rooms[room] = set()
        
        self.rooms[room].add(client_id)
        self.client_info[client_id]['room'] = room
        
        # 通知客户端
        await self.send_to_client(client_id, {
            'type': 'room_joined',
            'room': room,
            'member_count': len(self.rooms[room])
        })
        
        # 广播给房间其他成员
        await self.broadcast_to_room(room, {
            'type': 'user_joined',
            'client_id': client_id,
            'member_count': len(self.rooms[room])
        }, exclude_client=client_id)
        
        logger.info(f"客户端 {client_id} 加入房间: {room}")
    
    async def handle_leave_room(self, client_id: str, data: Dict[str, Any]):
        """处理离开房间"""
        current_room = self.client_info[client_id].get('room')
        if not current_room:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '您不在任何房间中'
            })
            return
        
        # 离开房间
        self.rooms[current_room].discard(client_id)
        if not self.rooms[current_room]:
            del self.rooms[current_room]
        
        self.client_info[client_id]['room'] = None
        
        # 通知客户端
        await self.send_to_client(client_id, {
            'type': 'room_left',
            'room': current_room
        })
        
        # 广播给房间其他成员
        if current_room in self.rooms:
            await self.broadcast_to_room(current_room, {
                'type': 'user_left',
                'client_id': client_id,
                'member_count': len(self.rooms[current_room])
            }, exclude_client=client_id)
        
        logger.info(f"客户端 {client_id} 离开房间: {current_room}")
    
    async def handle_chat_message(self, client_id: str, data: Dict[str, Any]):
        """处理聊天消息"""
        message = data.get('message')
        room = self.client_info[client_id].get('room')
        
        if not message:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '消息内容不能为空'
            })
            return
        
        if not room:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '请先加入房间'
            })
            return
        
        # 构建聊天消息
        chat_message = {
            'type': 'chat_message',
            'client_id': client_id,
            'message': message,
            'timestamp': time.time(),
            'room': room
        }
        
        # 广播给房间所有成员
        await self.broadcast_to_room(room, chat_message)
        
        logger.info(f"聊天消息: {client_id} -> {room}: {message}")
    
    async def handle_private_message(self, client_id: str, data: Dict[str, Any]):
        """处理私聊消息"""
        target_client_id = data.get('target_client_id')
        message = data.get('message')
        
        if not target_client_id or not message:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '目标客户端ID和消息内容不能为空'
            })
            return
        
        if target_client_id not in self.clients:
            await self.send_to_client(client_id, {
                'type': 'error',
                'message': '目标客户端不存在'
            })
            return
        
        # 构建私聊消息
        private_message = {
            'type': 'private_message',
            'from_client_id': client_id,
            'to_client_id': target_client_id,
            'message': message,
            'timestamp': time.time()
        }
        
        # 发送给目标客户端
        await self.send_to_client(target_client_id, private_message)
        
        # 发送确认给发送者
        await self.send_to_client(client_id, {
            'type': 'private_message_sent',
            'to_client_id': target_client_id,
            'timestamp': time.time()
        })
        
        logger.info(f"私聊消息: {client_id} -> {target_client_id}: {message}")
    
    async def send_to_client(self, client_id: str, data: Dict[str, Any]):
        """发送消息给指定客户端"""
        if client_id in self.clients:
            try:
                message = json.dumps(data, ensure_ascii=False)
                await self.clients[client_id].send(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"客户端 {client_id} 连接已关闭")
                await self.unregister_client(client_id)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
    
    async def broadcast_to_room(self, room: str, data: Dict[str, Any], exclude_client: str = None):
        """广播消息给房间所有客户端"""
        if room not in self.rooms:
            return
        
        message = json.dumps(data, ensure_ascii=False)
        disconnected_clients = []
        
        for client_id in self.rooms[room]:
            if exclude_client and client_id == exclude_client:
                continue
            
            try:
                await self.clients[client_id].send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
        
        # 清理断开连接的客户端
        for client_id in disconnected_clients:
            await self.unregister_client(client_id)
    
    async def broadcast_to_all(self, data: Dict[str, Any]):
        """广播消息给所有客户端"""
        message = json.dumps(data, ensure_ascii=False)
        disconnected_clients = []
        
        for client_id, websocket in self.clients.items():
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
        
        # 清理断开连接的客户端
        for client_id in disconnected_clients:
            await self.unregister_client(client_id)
    
    def register_message_handler(self, message_type: str, handler):
        """注册自定义消息处理器"""
        self.message_handlers[message_type] = handler
    
    async def start_server(self):
        """启动服务器"""
        logger.info(f"启动WebSocket服务器: {self.host}:{self.port}")
        
        async with websockets.serve(self.register_client, self.host, self.port):
            await asyncio.Future()  # 保持服务器运行
    
    def run(self):
        """运行服务器"""
        asyncio.run(self.start_server())

# 使用示例
async def custom_message_handler(client_id: str, data: Dict[str, Any]):
    """自定义消息处理器示例"""
    print(f"处理自定义消息: {client_id} - {data}")
    
    # 处理自定义逻辑
    response = {
        'type': 'custom_response',
        'original_data': data,
        'processed_at': time.time()
    }
    
    # 发送响应
    await server.send_to_client(client_id, response)

# 创建服务器实例
server = WebSocketServer()

# 注册自定义消息处理器
server.register_message_handler('custom_message', custom_message_handler)

# 启动服务器
if __name__ == '__main__':
    server.run()
```

### WebSocket客户端实现

#### Python WebSocket客户端
```python
# websocket_client.py
import asyncio
import websockets
import json
import time
from typing import Dict, Any

class WebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self.websocket = None
        self.client_id = None
        self.message_handlers = {}
        self.running = False
    
    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.running = True
            print(f"连接到WebSocket服务器: {self.url}")
            
            # 启动消息接收任务
            asyncio.create_task(self.receive_messages())
            
        except Exception as e:
            print(f"连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开连接"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("WebSocket连接已关闭")
    
    async def receive_messages(self):
        """接收消息"""
        try:
            while self.running:
                message = await self.websocket.recv()
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")
        except Exception as e:
            print(f"接收消息错误: {e}")
    
    async def handle_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            print(f"收到消息: {message_type} - {data}")
            
            # 处理特殊消息类型
            if message_type == 'welcome':
                self.client_id = data.get('client_id')
                print(f"客户端ID: {self.client_id}")
            elif message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            
        except json.JSONDecodeError:
            print(f"消息格式错误: {message}")
        except Exception as e:
            print(f"处理消息错误: {e}")
    
    async def send_message(self, data: Dict[str, Any]):
        """发送消息"""
        if self.websocket:
            try:
                message = json.dumps(data, ensure_ascii=False)
                await self.websocket.send(message)
                print(f"发送消息: {data.get('type')}")
            except Exception as e:
                print(f"发送消息失败: {e}")
    
    async def ping(self):
        """发送心跳"""
        await self.send_message({
            'type': 'ping',
            'timestamp': time.time()
        })
    
    async def join_room(self, room: str):
        """加入房间"""
        await self.send_message({
            'type': 'join_room',
            'room': room
        })
    
    async def leave_room(self):
        """离开房间"""
        await self.send_message({
            'type': 'leave_room'
        })
    
    async def send_chat_message(self, message: str):
        """发送聊天消息"""
        await self.send_message({
            'type': 'chat_message',
            'message': message
        })
    
    async def send_private_message(self, target_client_id: str, message: str):
        """发送私聊消息"""
        await self.send_message({
            'type': 'private_message',
            'target_client_id': target_client_id,
            'message': message
        })
    
    def register_message_handler(self, message_type: str, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler

# 消息处理器示例
async def handle_chat_message(data: Dict[str, Any]):
    """处理聊天消息"""
    client_id = data.get('client_id')
    message = data.get('message')
    timestamp = data.get('timestamp')
    
    print(f"[聊天] {client_id}: {message} ({time.ctime(timestamp)})")

async def handle_user_joined(data: Dict[str, Any]):
    """处理用户加入"""
    client_id = data.get('client_id')
    member_count = data.get('member_count')
    
    print(f"[系统] 用户 {client_id} 加入房间，当前人数: {member_count}")

async def handle_user_left(data: Dict[str, Any]):
    """处理用户离开"""
    client_id = data.get('client_id')
    member_count = data.get('member_count')
    
    print(f"[系统] 用户 {client_id} 离开房间，当前人数: {member_count}")

async def handle_private_message(data: Dict[str, Any]):
    """处理私聊消息"""
    from_client_id = data.get('from_client_id')
    message = data.get('message')
    timestamp = data.get('timestamp')
    
    print(f"[私聊] {from_client_id}: {message} ({time.ctime(timestamp)})")

# 使用示例
async def main():
    client = WebSocketClient("ws://localhost:8765")
    
    # 注册消息处理器
    client.register_message_handler('chat_message', handle_chat_message)
    client.register_message_handler('user_joined', handle_user_joined)
    client.register_message_handler('user_left', handle_user_left)
    client.register_message_handler('private_message', handle_private_message)
    
    try:
        # 连接到服务器
        await client.connect()
        
        # 等待连接建立
        await asyncio.sleep(1)
        
        # 加入房间
        await client.join_room("general")
        
        # 发送聊天消息
        await client.send_chat_message("Hello, everyone!")
        
        # 模拟交互
        for i in range(5):
            await asyncio.sleep(2)
            await client.send_chat_message(f"Message {i+1}")
        
        # 发送心跳
        await client.ping()
        
        # 保持连接
        await asyncio.sleep(10)
        
    except KeyboardInterrupt:
        print("用户中断")
    except Exception as e:
        print(f"客户端错误: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
```

## 服务通信最佳实践

### 通信协议选择指南

#### 协议对比表
| 协议 | 适用场景 | 优点 | 缺点 | 性能 |
|------|----------|------|------|------|
| REST/HTTP | 外部API、简单CRUD | 简单易用、广泛支持 | 性能较低、无状态 | 中等 |
| gRPC | 内部服务、高性能需求 | 高性能、类型安全 | 复杂度高、需要IDL | 高 |
| WebSocket | 实时通信、双向流 | 实时性好、双向通信 | 连接管理复杂 | 高 |
| 消息队列 | 异步处理、解耦 | 可靠性高、解耦 | 延迟较高、复杂 | 中等 |

#### 选择决策树
```python
def choose_communication_protocol(requirements):
    """通信协议选择决策树"""
    
    # 实时性要求
    if requirements.get('real_time', False):
        if requirements.get('bidirectional', False):
            return 'WebSocket'
        else:
            return 'Server-Sent Events'
    
    # 性能要求
    if requirements.get('high_performance', False):
        if requirements.get('internal_service', False):
            return 'gRPC'
        else:
            return 'REST/HTTP'
    
    # 可靠性要求
    if requirements.get('high_reliability', False):
        if requirements.get('asynchronous', False):
            return 'Message Queue'
        else:
            return 'REST/HTTP'
    
    # 默认选择
    return 'REST/HTTP'

# 使用示例
requirements = {
    'real_time': False,
    'high_performance': True,
    'internal_service': True,
    'asynchronous': False
}

protocol = choose_communication_protocol(requirements)
print(f"推荐协议: {protocol}")
```

### 错误处理和重试策略

#### 指数退避重试
```python
import time
import random
from typing import Callable, Any

class RetryHandler:
    def __init__(self, max_retries=3, base_delay=1, max_delay=60, backoff_factor=2):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
    
    def retry_with_exponential_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """指数退避重试"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    print(f"重试失败，已达最大重试次数: {self.max_retries}")
                    raise last_exception
                
                # 计算延迟时间
                delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)
                # 添加随机抖动
                jitter = random.uniform(0, delay * 0.1)
                total_delay = delay + jitter
                
                print(f"重试 {attempt + 1}/{self.max_retries}，延迟 {total_delay:.2f}s: {e}")
                time.sleep(total_delay)
        
        raise last_exception

# 使用示例
def unreliable_service_call():
    """模拟不可靠的服务调用"""
    if random.random() < 0.7:  # 70%失败率
        raise Exception("服务调用失败")
    return "成功响应"

retry_handler = RetryHandler(max_retries=5, base_delay=0.5)

try:
    result = retry_handler.retry_with_exponential_backoff(unreliable_service_call)
    print(f"调用成功: {result}")
except Exception as e:
    print(f"最终失败: {e}")
```

### 熔断器模式实现
```python
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过熔断器调用函数"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("熔断器开启，拒绝调用")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# 使用示例
@CircuitBreaker(failure_threshold=3, recovery_timeout=30)
def service_call():
    """服务调用"""
    if random.random() < 0.5:
        raise Exception("服务调用失败")
    return "成功响应"

# 测试熔断器
for i in range(10):
    try:
        result = service_call()
        print(f"调用 {i+1}: {result}")
    except Exception as e:
        print(f"调用 {i+1}: {e}")
    
    time.sleep(1)
```

## 参考资源

### 官方文档
- [REST API Design Guide](https://restfulapi.net/)
- [gRPC Documentation](https://grpc.io/docs/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

### 实现框架
- [Flask-RESTful](https://flask-restful.readthedocs.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [WebSockets in Python](https://websockets.readthedocs.io/)
- [Kafka Python Client](https://pypi.org/project/kafka-python/)

### 设计模式
- [Microservices Communication Patterns](https://microservices.io/patterns/communication/)
- [API Design Patterns](https://apisyouwonthate.com/)
- [Message Queue Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)

### 性能优化
- [HTTP/2 Performance](https://http2.github.io/faq/)
- [gRPC Performance Best Practices](https://grpc.io/docs/guides/performance/)
- [Message Queue Performance Tuning](https://www.confluent.io/blog/kafka-performance-tuning/)
