#!/usr/bin/env python3
"""
API网关设计 - 路由配置和负载均衡示例
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"

@dataclass
class ServiceEndpoint:
    host: str
    port: int
    weight: int = 1
    connections: int = 0
    healthy: bool = True

@dataclass
class RouteRule:
    path: str
    method: str
    service_name: str
    auth_required: bool = False
    rate_limit: Optional[int] = None

class APIGateway:
    def __init__(self):
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.routes: List[RouteRule] = []
        self.load_balancing_strategy = LoadBalancingStrategy.ROUND_ROBIN
        self.request_count = {}
        
    def register_service(self, service_name: str, endpoints: List[ServiceEndpoint]):
        """注册服务实例"""
        self.services[service_name] = endpoints
        self.request_count[service_name] = 0
        
    def add_route(self, route: RouteRule):
        """添加路由规则"""
        self.routes.append(route)
        
    def find_route(self, path: str, method: str) -> Optional[RouteRule]:
        """查找匹配的路由"""
        for route in self.routes:
            if path.startswith(route.path) and route.method.upper() == method.upper():
                return route
        return None
        
    def select_endpoint(self, service_name: str) -> Optional[ServiceEndpoint]:
        """根据负载均衡策略选择端点"""
        endpoints = self.services.get(service_name, [])
        healthy_endpoints = [ep for ep in endpoints if ep.healthy]
        
        if not healthy_endpoints:
            return None
            
        if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return healthy_endpoints[self.request_count[service_name] % len(healthy_endpoints)]
        elif self.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(healthy_endpoints, service_name)
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(healthy_endpoints, key=lambda x: x.connections)
        elif self.load_balancing_strategy == LoadBalancingStrategy.IP_HASH:
            return healthy_endpoints[hash("client_ip") % len(healthy_endpoints)]
            
    def _weighted_round_robin(self, endpoints: List[ServiceEndpoint], service_name: str) -> ServiceEndpoint:
        """加权轮询算法"""
        total_weight = sum(ep.weight for ep in endpoints)
        weight_index = self.request_count[service_name] % total_weight
        
        current_weight = 0
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if weight_index < current_weight:
                return endpoint
                
        return endpoints[0]
        
    def route_request(self, path: str, method: str, headers: Dict = None) -> Dict:
        """路由请求"""
        route = self.find_route(path, method)
        if not route:
            return {"error": "Route not found", "status_code": 404}
            
        # 检查认证
        if route.auth_required and not self._authenticate(headers):
            return {"error": "Authentication required", "status_code": 401}
            
        # 选择服务端点
        endpoint = self.select_endpoint(route.service_name)
        if not endpoint:
            return {"error": "Service unavailable", "status_code": 503}
            
        # 更新请求计数
        self.request_count[route.service_name] += 1
        endpoint.connections += 1
        
        try:
            # 模拟请求转发
            response = {
                "service": route.service_name,
                "endpoint": f"{endpoint.host}:{endpoint.port}",
                "path": path,
                "method": method,
                "load_balancing": self.load_balancing_strategy.value
            }
            
            endpoint.connections -= 1
            return response
            
        except Exception as e:
            endpoint.healthy = False
            endpoint.connections -= 1
            return {"error": f"Service error: {str(e)}", "status_code": 502}
            
    def _authenticate(self, headers: Dict = None) -> bool:
        """简单的认证检查"""
        if not headers:
            return False
        token = headers.get("Authorization")
        return token is not None and token.startswith("Bearer ")

def main():
    """演示API网关功能"""
    gateway = APIGateway()
    
    # 注册服务
    user_service_endpoints = [
        ServiceEndpoint("user-service-1", 8001, weight=2),
        ServiceEndpoint("user-service-2", 8002, weight=1),
        ServiceEndpoint("user-service-3", 8003, weight=1)
    ]
    
    order_service_endpoints = [
        ServiceEndpoint("order-service-1", 9001),
        ServiceEndpoint("order-service-2", 9002)
    ]
    
    gateway.register_service("user-service", user_service_endpoints)
    gateway.register_service("order-service", order_service_endpoints)
    
    # 添加路由规则
    gateway.add_route(RouteRule("/api/users", "GET", "user-service"))
    gateway.add_route(RouteRule("/api/users", "POST", "user-service", auth_required=True))
    gateway.add_route(RouteRule("/api/orders", "GET", "order-service", auth_required=True))
    gateway.add_route(RouteRule("/api/orders", "POST", "order-service", auth_required=True))
    
    # 测试请求路由
    test_requests = [
        ("/api/users", "GET", {}),
        ("/api/users", "POST", {"Authorization": "Bearer token123"}),
        ("/api/orders", "GET", {"Authorization": "Bearer token123"}),
        ("/api/orders", "POST", {}),
        ("/api/invalid", "GET", {})
    ]
    
    print("API网关路由演示:")
    print("=" * 50)
    
    for path, method, headers in test_requests:
        response = gateway.route_request(path, method, headers)
        print(f"\n请求: {method} {path}")
        if "error" in response:
            print(f"错误: {response['error']} (状态码: {response['status_code']})")
        else:
            print(f"路由到: {response['endpoint']}")
            print(f"负载均衡策略: {response['load_balancing']}")
    
    # 测试不同负载均衡策略
    print(f"\n\n负载均衡策略测试:")
    print("=" * 50)
    
    strategies = [
        LoadBalancingStrategy.ROUND_ROBIN,
        LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
        LoadBalancingStrategy.LEAST_CONNECTIONS
    ]
    
    for strategy in strategies:
        gateway.load_balancing_strategy = strategy
        gateway.request_count = {k: 0 for k in gateway.request_count}
        
        print(f"\n策略: {strategy.value}")
        for i in range(5):
            response = gateway.route_request("/api/users", "GET", {})
            if "error" not in response:
                print(f"  请求 {i+1}: {response['endpoint']}")

if __name__ == '__main__':
    main()
