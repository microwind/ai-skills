#!/usr/bin/env python3
"""
服务发现与治理演示 - 实现服务注册、发现和负载均衡
"""

import asyncio
import json
import time
import random
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable, Set
from enum import Enum
from datetime import datetime, timedelta
import uuid

class ServiceStatus(Enum):
    """服务状态"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"

@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    name: str
    host: str
    port: int
    status: ServiceStatus
    weight: int = 1
    metadata: Dict = None
    registered_at: float = None
    last_heartbeat: float = None
    health_check_url: str = "/health"
    connections: int = 0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.registered_at is None:
            self.registered_at = time.time()
        if self.last_heartbeat is None:
            self.last_heartbeat = time.time()
    
    @property
    def address(self) -> str:
        """获取服务地址"""
        return f"{self.host}:{self.port}"
    
    def is_healthy(self) -> bool:
        """检查服务是否健康"""
        return (self.status == ServiceStatus.RUNNING and 
                time.time() - self.last_heartbeat < 30)  # 30秒内有心跳

@dataclass
class ServiceConfig:
    """服务配置"""
    name: str
    host: str
    port: int
    health_check_interval: int = 10
    health_check_timeout: int = 5
    health_check_path: str = "/health"
    weight: int = 1
    metadata: Dict = None

class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.check_results: Dict[str, bool] = {}
    
    async def check_health(self, instance: ServiceInstance) -> bool:
        """检查服务健康状态"""
        try:
            # 模拟HTTP健康检查
            health_url = f"http://{instance.address}{instance.health_check_url}"
            
            print(f"💓 健康检查: {instance.name} -> {health_url}")
            
            # 模拟网络请求
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            # 模拟健康检查结果（90%概率健康）
            is_healthy = random.random() > 0.1
            
            self.check_results[instance.id] = is_healthy
            
            if is_healthy:
                print(f"✅ 健康检查通过: {instance.name}")
                instance.status = ServiceStatus.RUNNING
            else:
                print(f"❌ 健康检查失败: {instance.name}")
                instance.status = ServiceStatus.UNHEALTHY
            
            return is_healthy
            
        except Exception as e:
            print(f"❌ 健康检查异常: {instance.name} - {e}")
            instance.status = ServiceStatus.UNHEALTHY
            return False

class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.health_checker = HealthChecker()
        self.running = False
        self.heartbeat_task = None
        self.cleanup_task = None
        self.listeners: List[Callable] = []
    
    def register_listener(self, listener: Callable):
        """注册事件监听器"""
        self.listeners.append(listener)
    
    def notify_listeners(self, event_type: str, data: dict):
        """通知监听器"""
        for listener in self.listeners:
            try:
                listener(event_type, data)
            except Exception as e:
                print(f"❌ 监听器通知失败: {e}")
    
    def register_service(self, config: ServiceConfig) -> ServiceInstance:
        """注册服务"""
        instance = ServiceInstance(
            id=str(uuid.uuid4()),
            name=config.name,
            host=config.host,
            port=config.port,
            status=ServiceStatus.STARTING,
            weight=config.weight,
            metadata=config.metadata or {},
            health_check_url=config.health_check_path
        )
        
        if config.name not in self.services:
            self.services[config.name] = []
        
        self.services[config.name].append(instance)
        
        print(f"✅ 服务注册: {config.name} -> {instance.address}")
        
        # 通知监听器
        self.notify_listeners("service_registered", {
            "service": config.name,
            "instance": instance
        })
        
        return instance
    
    def deregister_service(self, service_name: str, instance_id: str) -> bool:
        """注销服务"""
        if service_name in self.services:
            instances = self.services[service_name]
            for i, instance in enumerate(instances):
                if instance.id == instance_id:
                    instance.status = ServiceStatus.STOPPED
                    instances.pop(i)
                    
                    print(f"❌ 服务注销: {service_name} ({instance.address})")
                    
                    # 通知监听器
                    self.notify_listeners("service_deregistered", {
                        "service": service_name,
                        "instance": instance
                    })
                    
                    return True
        return False
    
    def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """发现服务"""
        if service_name in self.services:
            # 只返回健康的服务实例
            healthy_instances = [
                instance for instance in self.services[service_name]
                if instance.is_healthy()
            ]
            return healthy_instances
        return []
    
    def get_service_by_id(self, service_name: str, instance_id: str) -> Optional[ServiceInstance]:
        """根据ID获取服务实例"""
        if service_name in self.services:
            for instance in self.services[service_name]:
                if instance.id == instance_id:
                    return instance
        return None
    
    def update_heartbeat(self, service_name: str, instance_id: str) -> bool:
        """更新心跳"""
        instance = self.get_service_by_id(service_name, instance_id)
        if instance:
            instance.last_heartbeat = time.time()
            if instance.status == ServiceStatus.STARTING:
                instance.status = ServiceStatus.RUNNING
            return True
        return False
    
    def list_services(self) -> Dict[str, List[ServiceInstance]]:
        """列出所有服务"""
        return self.services.copy()
    
    async def start_health_check(self):
        """启动健康检查"""
        self.running = True
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        print("🏥 健康检查服务启动")
    
    async def stop_health_check(self):
        """停止健康检查"""
        self.running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        print("🏥 健康检查服务停止")
    
    async def _heartbeat_loop(self):
        """心跳检查循环"""
        while self.running:
            try:
                # 检查所有服务的健康状态
                for service_name, instances in self.services.items():
                    for instance in instances:
                        await self.health_checker.check_health(instance)
                
                await asyncio.sleep(10)  # 每10秒检查一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ 心跳检查错误: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                current_time = time.time()
                
                # 清理超时的服务实例
                for service_name, instances in list(self.services.items()):
                    for instance in instances[:]:
                        if current_time - instance.last_heartbeat > 60:  # 60秒无心跳
                            self.deregister_service(service_name, instance.id)
                
                await asyncio.sleep(30)  # 每30秒清理一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ 清理循环错误: {e}")
                await asyncio.sleep(10)

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.round_robin_counters: Dict[str, int] = {}
    
    def select_instance(self, instances: List[ServiceInstance], service_name: str) -> Optional[ServiceInstance]:
        """选择服务实例"""
        if not instances:
            return None
        
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(instances, service_name)
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_select(instances)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(instances, service_name)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(instances)
        
        return instances[0]
    
    def _round_robin_select(self, instances: List[ServiceInstance], service_name: str) -> ServiceInstance:
        """轮询选择"""
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(instances)
        self.round_robin_counters[service_name] += 1
        
        return instances[index]
    
    def _random_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """随机选择"""
        return random.choice(instances)
    
    def _weighted_round_robin_select(self, instances: List[ServiceInstance], service_name: str) -> ServiceInstance:
        """加权轮询选择"""
        # 创建加权列表
        weighted_instances = []
        for instance in instances:
            weighted_instances.extend([instance] * instance.weight)
        
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(weighted_instances)
        self.round_robin_counters[service_name] += 1
        
        return weighted_instances[index]
    
    def _least_connections_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """最少连接选择"""
        return min(instances, key=lambda x: x.connections)

class ServiceClient:
    """服务客户端"""
    
    def __init__(self, registry: ServiceRegistry, load_balancer: LoadBalancer):
        self.registry = registry
        self.load_balancer = load_balancer
    
    async def call_service(self, service_name: str, request_data: dict) -> Optional[dict]:
        """调用服务"""
        # 发现服务实例
        instances = self.registry.discover_services(service_name)
        
        if not instances:
            print(f"❌ 没有可用的服务实例: {service_name}")
            return None
        
        # 负载均衡选择实例
        instance = self.load_balancer.select_instance(instances, service_name)
        
        if not instance:
            print(f"❌ 负载均衡失败: {service_name}")
            return None
        
        # 增加连接计数
        instance.connections += 1
        
        try:
            print(f"🚀 调用服务: {service_name} -> {instance.address}")
            print(f"   请求数据: {request_data}")
            
            # 模拟网络请求
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            # 模拟请求响应
            response = {
                "service": service_name,
                "instance": instance.address,
                "request_id": str(uuid.uuid4()),
                "data": request_data,
                "timestamp": time.time()
            }
            
            print(f"✅ 服务响应: {service_name}")
            return response
            
        except Exception as e:
            print(f"❌ 服务调用失败: {service_name} - {e}")
            return None
        finally:
            # 减少连接计数
            instance.connections -= 1

class ServiceAgent:
    """服务代理"""
    
    def __init__(self, config: ServiceConfig, registry: ServiceRegistry):
        self.config = config
        self.registry = registry
        self.instance: Optional[ServiceInstance] = None
        self.running = False
        self.heartbeat_task = None
    
    async def start(self):
        """启动服务代理"""
        # 注册服务
        self.instance = self.registry.register_service(self.config)
        
        self.running = True
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        print(f"🚀 服务代理启动: {self.config.name}")
    
    async def stop(self):
        """停止服务代理"""
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        if self.instance:
            self.registry.deregister_service(self.config.name, self.instance.id)
        
        print(f"⏹️  服务代理停止: {self.config.name}")
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.running and self.instance:
            try:
                # 发送心跳
                success = self.registry.update_heartbeat(self.config.name, self.instance.id)
                
                if success:
                    print(f"💓 心跳发送: {self.config.name}")
                else:
                    print(f"❌ 心跳失败: {self.config.name}")
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ 心跳循环错误: {e}")
                await asyncio.sleep(5)

async def demonstrate_service_registration():
    """演示服务注册"""
    print("\n📝 服务注册演示")
    print("=" * 50)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 启动健康检查
    await registry.start_health_check()
    
    # 创建服务配置
    services_config = [
        ServiceConfig("user-service", "192.168.1.10", 8001, weight=2),
        ServiceConfig("user-service", "192.168.1.11", 8002, weight=1),
        ServiceConfig("order-service", "192.168.1.20", 8003),
        ServiceConfig("order-service", "192.168.1.21", 8004),
        ServiceConfig("payment-service", "192.168.1.30", 8005),
    ]
    
    # 创建服务代理
    agents = []
    for config in services_config:
        agent = ServiceAgent(config, registry)
        await agent.start()
        agents.append(agent)
    
    # 等待服务注册完成
    await asyncio.sleep(2)
    
    # 显示注册的服务
    print("\n📋 已注册服务:")
    for service_name, instances in registry.list_services().items():
        print(f"\n{service_name}:")
        for instance in instances:
            status = "🟢" if instance.is_healthy() else "🔴"
            print(f"  {status} {instance.address} (权重: {instance.weight})")
    
    # 停止服务代理
    for agent in agents:
        await agent.stop()
    
    # 停止健康检查
    await registry.stop_health_check()

async def demonstrate_service_discovery():
    """演示服务发现"""
    print("\n🔍 服务发现演示")
    print("=" * 50)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 注册服务
    services = [
        ServiceConfig("user-service", "192.168.1.10", 8001),
        ServiceConfig("order-service", "192.168.1.20", 8002),
        ServiceConfig("payment-service", "192.168.1.30", 8003),
    ]
    
    for config in services:
        registry.register_service(config)
    
    # 创建服务客户端
    load_balancer = LoadBalancer(LoadBalanceStrategy.ROUND_ROBIN)
    client = ServiceClient(registry, load_balancer)
    
    # 模拟服务调用
    requests = [
        ("user-service", {"action": "get_user", "user_id": 123}),
        ("order-service", {"action": "create_order", "user_id": 123}),
        ("payment-service", {"action": "process_payment", "amount": 100.0}),
        ("user-service", {"action": "update_user", "user_id": 123}),
        ("order-service", {"action": "get_order", "order_id": 456}),
    ]
    
    for service_name, request_data in requests:
        response = await client.call_service(service_name, request_data)
        if response:
            print(f"📨 调用成功: {service_name}")
        else:
            print(f"❌ 调用失败: {service_name}")
        await asyncio.sleep(0.1)

async def demonstrate_load_balancing():
    """演示负载均衡"""
    print("\n⚖️  负载均衡演示")
    print("=" * 50)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 注册多个用户服务实例
    user_services = [
        ServiceConfig("user-service", "192.168.1.10", 8001, weight=3),
        ServiceConfig("user-service", "192.168.1.11", 8002, weight=2),
        ServiceConfig("user-service", "192.168.1.12", 8003, weight=1),
    ]
    
    for config in user_services:
        registry.register_service(config)
    
    # 测试不同的负载均衡策略
    strategies = [
        LoadBalanceStrategy.ROUND_ROBIN,
        LoadBalanceStrategy.RANDOM,
        LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN,
        LoadBalanceStrategy.LEAST_CONNECTIONS,
    ]
    
    for strategy in strategies:
        print(f"\n🔄 测试策略: {strategy.value}")
        load_balancer = LoadBalancer(strategy)
        client = ServiceClient(registry, load_balancer)
        
        # 发送多个请求
        request_counts = {}
        for i in range(10):
            response = await client.call_service("user-service", {"action": "get_user", "user_id": i})
            if response:
                instance_address = response["instance"]
                request_counts[instance_address] = request_counts.get(instance_address, 0) + 1
        
        # 显示请求分布
        print("📊 请求分布:")
        for address, count in request_counts.items():
            print(f"  {address}: {count} 次")

async def demonstrate_health_monitoring():
    """演示健康监控"""
    print("\n🏥 健康监控演示")
    print("=" * 50)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 启动健康检查
    await registry.start_health_check()
    
    # 注册服务
    services = [
        ServiceConfig("user-service", "192.168.1.10", 8001),
        ServiceConfig("order-service", "192.168.1.20", 8002),
        ServiceConfig("payment-service", "192.168.1.30", 8003),
    ]
    
    agents = []
    for config in services:
        agent = ServiceAgent(config, registry)
        await agent.start()
        agents.append(agent)
    
    # 监控服务状态
    print("\n📊 监控服务状态 (30秒):")
    for i in range(6):
        await asyncio.sleep(5)
        print(f"\n--- 第 {i+1} 次检查 ---")
        
        for service_name, instances in registry.list_services().items():
            healthy_count = sum(1 for instance in instances if instance.is_healthy())
            total_count = len(instances)
            print(f"{service_name}: {healthy_count}/{total_count} 健康")
    
    # 停止服务
    for agent in agents:
        await agent.stop()
    
    await registry.stop_health_check()

async def main():
    """主函数"""
    print("🔍 微服务发现与治理演示")
    print("=" * 60)
    
    try:
        await demonstrate_service_registration()
        await demonstrate_service_discovery()
        await demonstrate_load_balancing()
        await demonstrate_health_monitoring()
        
        print("\n✅ 服务发现演示完成!")
        print("\n📚 关键概念:")
        print("  - 服务注册: 服务实例注册到注册中心")
        print("  - 服务发现: 客户端发现可用服务实例")
        print("  - 负载均衡: 在多个实例间分配请求")
        print("  - 健康检查: 监控服务实例健康状态")
        print("  - 心跳机制: 服务实例定期发送心跳")
        print("  - 服务治理: 服务生命周期管理")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
