#!/usr/bin/env python3
"""
微服务间通信演示 - 实现多种通信模式
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import threading
import queue

class CommunicationType(Enum):
    """通信类型"""
    SYNC = "sync"
    ASYNC = "async"
    EVENT_DRIVEN = "event_driven"
    REQUEST_REPLY = "request_reply"

class MessagePriority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Message:
    """消息数据结构"""
    id: str
    sender: str
    receiver: str
    content: Any
    timestamp: float
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp
        return data

@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    host: str
    port: int
    protocol: str = "http"
    health_check_url: str = "/health"
    endpoints: List[str] = None

class CommunicationProtocol(ABC):
    """通信协议抽象基类"""
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """发送消息"""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[Message]:
        """接收消息"""
        pass

class HTTPCommunication(CommunicationProtocol):
    """HTTP通信协议"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.message_queue = queue.Queue()
    
    def register_service(self, service_info: ServiceInfo):
        """注册服务"""
        self.services[service_info.name] = service_info
    
    async def send_message(self, message: Message) -> bool:
        """发送HTTP消息"""
        try:
            # 模拟HTTP请求
            print(f"📤 HTTP发送: {message.sender} -> {message.receiver}")
            print(f"   消息ID: {message.id}")
            print(f"   内容: {message.content}")
            
            # 模拟网络延迟
            await asyncio.sleep(0.1)
            
            # 模拟成功发送
            self.message_queue.put(message)
            return True
        except Exception as e:
            print(f"❌ HTTP发送失败: {e}")
            return False
    
    async def receive_message(self) -> Optional[Message]:
        """接收HTTP消息"""
        try:
            if not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                print(f"📥 HTTP接收: {message.receiver} <- {message.sender}")
                return message
            return None
        except queue.Empty:
            return None

class MessageQueueCommunication(CommunicationProtocol):
    """消息队列通信协议"""
    
    def __init__(self):
        self.exchanges: Dict[str, queue.Queue] = {}
        self.bindings: Dict[str, List[str]] = {}
    
    def create_exchange(self, exchange_name: str):
        """创建交换机"""
        if exchange_name not in self.exchanges:
            self.exchanges[exchange_name] = queue.Queue()
    
    def bind_queue(self, queue_name: str, exchange_name: str):
        """绑定队列到交换机"""
        if exchange_name not in self.bindings:
            self.bindings[exchange_name] = []
        if queue_name not in self.bindings[exchange_name]:
            self.bindings[exchange_name].append(queue_name)
    
    async def send_message(self, message: Message) -> bool:
        """发送消息到队列"""
        try:
            exchange_name = f"{message.receiver}_exchange"
            self.create_exchange(exchange_name)
            
            print(f"📤 队列发送: {message.sender} -> {exchange_name}")
            print(f"   消息ID: {message.id}")
            print(f"   优先级: {message.priority.name}")
            
            # 根据优先级排序
            messages = []
            while not self.exchanges[exchange_name].empty():
                try:
                    msg = self.exchanges[exchange_name].get_nowait()
                    messages.append(msg)
                except queue.Empty:
                    break
            
            # 插入新消息并按优先级排序
            messages.append(message)
            messages.sort(key=lambda x: x.priority.value, reverse=True)
            
            # 重新放回队列
            for msg in messages:
                self.exchanges[exchange_name].put(msg)
            
            return True
        except Exception as e:
            print(f"❌ 队列发送失败: {e}")
            return False
    
    async def receive_message(self, exchange_name: str) -> Optional[Message]:
        """从队列接收消息"""
        try:
            if exchange_name in self.exchanges:
                message = self.exchanges[exchange_name].get_nowait()
                print(f"📥 队列接收: {exchange_name}")
                return message
            return None
        except queue.Empty:
            return None

class EventDrivenCommunication(CommunicationProtocol):
    """事件驱动通信协议"""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[callable]] = {}
        self.event_history: List[Message] = []
    
    def subscribe(self, event_type: str, handler: callable):
        """订阅事件"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def publish_event(self, message: Message) -> bool:
        """发布事件"""
        try:
            print(f"📢 事件发布: {message.sender} 发布 {message.content.get('event_type', 'unknown')}")
            print(f"   事件ID: {message.id}")
            print(f"   数据: {message.content}")
            
            # 记录事件历史
            self.event_history.append(message)
            
            # 通知订阅者
            event_type = message.content.get('event_type', 'default')
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        print(f"❌ 事件处理器错误: {e}")
            
            return True
        except Exception as e:
            print(f"❌ 事件发布失败: {e}")
            return False
    
    async def send_message(self, message: Message) -> bool:
        """发送事件消息"""
        return await self.publish_event(message)
    
    async def receive_message(self) -> Optional[Message]:
        """接收事件消息"""
        return None

class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.health_status: Dict[str, bool] = {}
    
    def register(self, service_info: ServiceInfo):
        """注册服务"""
        self.services[service_info.name] = service_info
        self.health_status[service_info.name] = True
        print(f"✅ 服务注册: {service_info.name} at {service_info.host}:{service_info.port}")
    
    def deregister(self, service_name: str):
        """注销服务"""
        if service_name in self.services:
            del self.services[service_name]
            del self.health_status[service_name]
            print(f"❌ 服务注销: {service_name}")
    
    def discover(self, service_name: str) -> Optional[ServiceInfo]:
        """发现服务"""
        return self.services.get(service_name)
    
    def list_services(self) -> List[str]:
        """列出所有服务"""
        return list(self.services.keys())
    
    async def health_check(self):
        """健康检查"""
        for service_name, service_info in self.services.items():
            try:
                # 模拟健康检查
                await asyncio.sleep(0.01)
                self.health_status[service_name] = True
            except:
                self.health_status[service_name] = False

class APIGateway:
    """API网关"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.routes: Dict[str, str] = {}
        self.rate_limits: Dict[str, int] = {}
    
    def add_route(self, path: str, service_name: str):
        """添加路由"""
        self.routes[path] = service_name
        print(f"🛣️  路由添加: {path} -> {service_name}")
    
    async def route_request(self, path: str, request_data: dict) -> Optional[Any]:
        """路由请求"""
        if path not in self.routes:
            return {"error": "Route not found"}
        
        service_name = self.routes[path]
        service_info = self.service_registry.discover(service_name)
        
        if not service_info:
            return {"error": f"Service {service_name} not available"}
        
        # 检查速率限制
        if self._check_rate_limit(service_name):
            return {"error": "Rate limit exceeded"}
        
        print(f"🚀 网关路由: {path} -> {service_name}")
        
        # 模拟请求转发
        await asyncio.sleep(0.05)
        
        return {
            "service": service_name,
            "data": request_data,
            "timestamp": time.time()
        }
    
    def _check_rate_limit(self, service_name: str) -> bool:
        """检查速率限制"""
        current_time = time.time()
        if service_name not in self.rate_limits:
            self.rate_limits[service_name] = 0
        
        # 简单的速率限制：每秒最多10个请求
        if current_time - self.rate_limits.get(f"{service_name}_last", 0) > 1:
            self.rate_limits[service_name] = 0
        
        self.rate_limits[service_name] += 1
        self.rate_limits[f"{service_name}_last"] = current_time
        
        return self.rate_limits[service_name] > 10

class MicroService:
    """微服务基类"""
    
    def __init__(self, name: str, communication: CommunicationProtocol):
        self.name = name
        self.communication = communication
        self.message_handlers: Dict[str, callable] = {}
        self.running = False
    
    def register_handler(self, message_type: str, handler: callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, receiver: str, content: Any, priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """发送消息"""
        message = Message(
            id=str(uuid.uuid4()),
            sender=self.name,
            receiver=receiver,
            content=content,
            timestamp=time.time(),
            priority=priority
        )
        return await self.communication.send_message(message)
    
    async def start(self):
        """启动服务"""
        self.running = True
        print(f"🚀 服务启动: {self.name}")
        
        while self.running:
            try:
                message = await self.communication.receive_message()
                if message and message.receiver == self.name:
                    await self.handle_message(message)
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ 服务错误: {e}")
    
    async def handle_message(self, message: Message):
        """处理消息"""
        message_type = type(message.content).__name__
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](message)
            except Exception as e:
                print(f"❌ 消息处理错误: {e}")
        else:
            print(f"⚠️  未知消息类型: {message_type}")
    
    def stop(self):
        """停止服务"""
        self.running = False
        print(f"⏹️  服务停止: {self.name}")

async def demonstrate_sync_communication():
    """演示同步通信"""
    print("\n🔄 同步通信演示")
    print("=" * 50)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 创建API网关
    gateway = APIGateway(registry)
    
    # 注册服务
    registry.register(ServiceInfo("user-service", "localhost", 8001))
    registry.register(ServiceInfo("order-service", "localhost", 8002))
    registry.register(ServiceInfo("payment-service", "localhost", 8003))
    
    # 配置路由
    gateway.add_route("/api/users", "user-service")
    gateway.add_route("/api/orders", "order-service")
    gateway.add_route("/api/payments", "payment-service")
    
    # 模拟请求
    requests = [
        ("/api/users", {"action": "get_user", "user_id": 123}),
        ("/api/orders", {"action": "create_order", "user_id": 123}),
        ("/api/payments", {"action": "process_payment", "order_id": 456})
    ]
    
    for path, data in requests:
        response = await gateway.route_request(path, data)
        print(f"📨 请求: {path}")
        print(f"📬 响应: {response}")
        print()

async def demonstrate_async_communication():
    """演示异步通信"""
    print("\n⚡ 异步通信演示")
    print("=" * 50)
    
    # 创建消息队列通信
    mq_comm = MessageQueueCommunication()
    
    # 创建服务
    user_service = MicroService("user-service", mq_comm)
    order_service = MicroService("order-service", mq_comm)
    
    # 注册消息处理器
    async def handle_user_request(message: Message):
        print(f"👤 用户服务处理: {message.content}")
        await asyncio.sleep(0.1)  # 模拟处理时间
    
    async def handle_order_request(message: Message):
        print(f"📦 订单服务处理: {message.content}")
        await asyncio.sleep(0.2)  # 模拟处理时间
    
    user_service.register_handler("dict", handle_user_request)
    order_service.register_handler("dict", handle_order_request)
    
    # 启动服务
    user_task = asyncio.create_task(user_service.start())
    order_task = asyncio.create_task(order_service.start())
    
    # 发送消息
    await user_service.send_message("order-service", {"action": "get_user_info", "user_id": 123})
    await order_service.send_message("user-service", {"action": "create_order", "user_id": 123})
    
    # 等待处理
    await asyncio.sleep(1)
    
    # 停止服务
    user_service.stop()
    order_service.stop()
    
    # 等待任务完成
    await user_task
    await order_task

async def demonstrate_event_driven_communication():
    """演示事件驱动通信"""
    print("\n🎯 事件驱动通信演示")
    print("=" * 50)
    
    # 创建事件驱动通信
    event_comm = EventDrivenCommunication()
    
    # 订阅事件
    async def handle_user_created(message: Message):
        print(f"👤 用户创建事件: {message.content}")
        # 触发后续事件
        await event_comm.send_message("", {
            "event_type": "send_welcome_email",
            "user_id": message.content["user_id"]
        })
    
    async def handle_send_welcome_email(message: Message):
        print(f"📧 发送欢迎邮件: {message.content}")
    
    async def handle_order_created(message: Message):
        print(f"📦 订单创建事件: {message.content}")
        # 触发库存检查
        await event_comm.send_message("", {
            "event_type": "check_inventory",
            "product_id": message.content["product_id"]
        })
    
    event_comm.subscribe("user_created", handle_user_created)
    event_comm.subscribe("send_welcome_email", handle_send_welcome_email)
    event_comm.subscribe("order_created", handle_order_created)
    
    # 发布事件
    await event_comm.send_message("", {
        "event_type": "user_created",
        "user_id": 123,
        "username": "john_doe"
    })
    
    await event_comm.send_message("", {
        "event_type": "order_created",
        "order_id": 456,
        "user_id": 123,
        "product_id": 789
    })
    
    # 等待事件处理
    await asyncio.sleep(0.5)

async def demonstrate_service_discovery():
    """演示服务发现"""
    print("\n🔍 服务发现演示")
    print("=" * 50)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 注册多个服务
    services = [
        ServiceInfo("user-service", "192.168.1.10", 8001),
        ServiceInfo("order-service", "192.168.1.11", 8002),
        ServiceInfo("payment-service", "192.168.1.12", 8003),
        ServiceInfo("notification-service", "192.168.1.13", 8004)
    ]
    
    for service in services:
        registry.register(service)
    
    # 显示所有服务
    print("📋 已注册服务:")
    for service_name in registry.list_services():
        service_info = registry.discover(service_name)
        print(f"  - {service_name}: {service_info.host}:{service_info.port}")
    
    # 模拟服务发现
    print("\n🔍 服务发现测试:")
    test_services = ["user-service", "order-service", "unknown-service"]
    
    for service_name in test_services:
        service_info = registry.discover(service_name)
        if service_info:
            print(f"✅ 发现服务: {service_name} -> {service_info.host}:{service_info.port}")
        else:
            print(f"❌ 服务未找到: {service_name}")
    
    # 健康检查
    print("\n💓 健康检查:")
    await registry.health_check()
    
    for service_name, is_healthy in registry.health_status.items():
        status = "✅ 健康" if is_healthy else "❌ 不健康"
        print(f"  {service_name}: {status}")

async def main():
    """主函数"""
    print("🌐 微服务间通信演示")
    print("=" * 60)
    
    try:
        await demonstrate_sync_communication()
        await demonstrate_async_communication()
        await demonstrate_event_driven_communication()
        await demonstrate_service_discovery()
        
        print("\n✅ 服务通信演示完成!")
        print("\n📚 关键概念:")
        print("  - 同步通信: HTTP/REST API")
        print("  - 异步通信: 消息队列")
        print("  - 事件驱动: 发布/订阅模式")
        print("  - 服务发现: 服务注册与查找")
        print("  - API网关: 统一入口和路由")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
