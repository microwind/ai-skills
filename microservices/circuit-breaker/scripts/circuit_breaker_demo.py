#!/usr/bin/env python3
"""
熔断器模式演示 - 实现微服务熔断机制
"""

import time
import random
from enum import Enum
from typing import Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 关闭状态，正常工作
    OPEN = "open"          # 打开状态，熔断中
    HALF_OPEN = "half_open" # 半开状态，尝试恢复

@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5        # 失败阈值
    timeout: float = 60.0             # 熔断超时时间（秒）
    expected_exception: type = Exception  # 预期异常类型
    recovery_timeout: float = 10.0     # 恢复超时时间

class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0
        
    def __call__(self, func: Callable) -> Callable:
        """装饰器实现"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """调用受保护的方法"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.config.timeout
    
    def _on_success(self):
        """成功处理"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # 连续3次成功后关闭熔断器
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """失败处理"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN

class RemoteService:
    """模拟远程服务"""
    
    def __init__(self, service_name: str, failure_rate: float = 0.3):
        self.service_name = service_name
        self.failure_rate = failure_rate
        self.request_count = 0
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=3,
            timeout=30.0,
            expected_exception=Exception
        ))
    
    def request_data(self, data: str) -> str:
        """请求数据"""
        return self.circuit_breaker.call(self._request_data_internal, data)
    
    def _request_data_internal(self, data: str) -> str:
        """内部请求数据实现"""
        self.request_count += 1
        
        # 模拟网络延迟
        time.sleep(random.uniform(0.1, 0.5))
        
        # 模拟服务失败
        if random.random() < self.failure_rate:
            raise Exception(f"Service {self.service_name} temporarily unavailable")
        
        return f"Processed: {data} by {self.service_name}"

class ServiceRegistry:
    """服务注册表"""
    
    def __init__(self):
        self.services = {}
    
    def register_service(self, name: str, service: RemoteService):
        """注册服务"""
        self.services[name] = service
    
    def get_service(self, name: str) -> RemoteService:
        """获取服务"""
        return self.services.get(name)

class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, service_registry: ServiceRegistry):
        self.service_registry = service_registry
        self.current_index = 0
    
    def round_robin_request(self, service_name: str, data: str) -> str:
        """轮询请求"""
        service = self.service_registry.get_service(service_name)
        if not service:
            raise Exception(f"Service {service_name} not found")
        
        try:
            return service.request_data(data)
        except Exception as e:
            print(f"Service {service_name} failed: {e}")
            raise

class MonitoringService:
    """监控服务"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'circuit_breaker_trips': 0
        }
    
    def record_request(self, success: bool):
        """记录请求"""
        self.metrics['total_requests'] += 1
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
    
    def record_circuit_breaker_trip(self):
        """记录熔断器触发"""
        self.metrics['circuit_breaker_trips'] += 1
    
    def get_metrics(self) -> dict:
        """获取指标"""
        return self.metrics.copy()

def demonstrate_circuit_breaker():
    """演示熔断器功能"""
    print("🔌 熔断器模式演示")
    print("=" * 50)
    
    # 创建服务
    service = RemoteService("user-service", failure_rate=0.4)
    
    # 创建监控服务
    monitoring = MonitoringService()
    
    print("\n📊 测试熔断器行为:")
    print("-" * 30)
    
    # 测试正常状态
    print("\n1. 正常状态测试:")
    for i in range(5):
        try:
            result = service.request_data(f"request_{i}")
            print(f"  请求 {i+1}: ✅ {result}")
            monitoring.record_request(True)
        except Exception as e:
            print(f"  请求 {i+1}: ❌ {e}")
            monitoring.record_request(False)
    
    # 模拟连续失败
    print("\n2. 模拟连续失败:")
    service.failure_rate = 0.8  # 提高失败率
    
    for i in range(5):
        try:
            result = service.request_data(f"request_{i}")
            print(f"  请求 {i+1}: ✅ {result}")
            monitoring.record_request(True)
        except Exception as e:
            print(f"  请求 {i+1}: ❌ {e}")
            monitoring.record_request(False)
    
    # 测试熔断状态
    print("\n3. 测试熔断状态:")
    for i in range(3):
        try:
            result = service.request_data(f"request_{i}")
            print(f"  请求 {i+1}: ✅ {result}")
            monitoring.record_request(True)
        except Exception as e:
            print(f"  请求 {i+1}: ❌ {e}")
            monitoring.record_request(False)
    
    # 等待熔断器恢复
    print("\n4. 等待熔断器恢复...")
    time.sleep(2)
    service.failure_rate = 0.2  # 降低失败率
    
    # 测试恢复
    print("\n5. 测试熔断器恢复:")
    for i in range(5):
        try:
            result = service.request_data(f"request_{i}")
            print(f"  请求 {i+1}: ✅ {result}")
            monitoring.record_request(True)
        except Exception as e:
            print(f"  请求 {i+1}: ❌ {e}")
            monitoring.record_request(False)
    
    # 显示统计信息
    print("\n📈 监控指标:")
    metrics = monitoring.get_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")

def demonstrate_advanced_circuit_breaker():
    """演示高级熔断器功能"""
    print("\n🔧 高级熔断器演示")
    print("=" * 50)
    
    # 创建多个服务
    services = {
        'user-service': RemoteService('user-service', failure_rate=0.3),
        'order-service': RemoteService('order-service', failure_rate=0.2),
        'payment-service': RemoteService('payment-service', failure_rate=0.4)
    }
    
    # 创建服务注册表
    registry = ServiceRegistry()
    for name, service in services.items():
        registry.register_service(name, service)
    
    # 创建负载均衡器
    load_balancer = LoadBalancer(registry)
    
    print("\n🔄 负载均衡测试:")
    
    # 模拟多个请求
    services_list = ['user-service', 'order-service', 'payment-service']
    
    for i in range(10):
        service_name = services_list[i % len(services_list)]
        try:
            result = load_balancer.round_robin_request(service_name, f"order_{i}")
            print(f"  请求 {i+1}: ✅ {service_name} - {result}")
        except Exception as e:
            print(f"  请求 {i+1}: ❌ {service_name} - {e}")

def main():
    """主函数"""
    print("🔌 微服务熔断器模式演示")
    print("=" * 60)
    
    try:
        demonstrate_circuit_breaker()
        demonstrate_advanced_circuit_breaker()
        
        print("\n✅ 熔断器演示完成!")
        print("\n📚 关键概念:")
        print("  - 熔断器状态: CLOSED, OPEN, HALF_OPEN")
        print("  - 失败阈值和超时机制")
        print("  - 自动恢复和半开状态测试")
        print("  - 负载均衡和服务降级")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    main()
