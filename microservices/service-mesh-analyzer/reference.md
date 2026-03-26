# 服务网格分析器参考文档

## 服务网格分析器概述

### 什么是服务网格分析器
服务网格分析器是一种专门用于分析、监控和管理微服务架构中服务网格的工具。它通过收集和分析服务网格中的流量数据、性能指标、安全事件等信息，提供全面的可视化和分析能力。服务网格分析器支持主流的服务网格平台如Istio、Linkerd、Consul Connect等，能够帮助运维人员深入了解服务间的通信模式、识别性能瓶颈、发现安全威胁，并提供优化建议。

### 主要功能
- **流量分析**: 分析服务间的流量模式、通信路径和流量分布
- **性能监控**: 监控服务响应时间、吞吐量、错误率等关键性能指标
- **安全分析**: 分析安全策略执行情况、检测安全威胁和异常访问
- **故障诊断**: 识别服务故障、网络问题和资源瓶颈
- **可视化展示**: 提供服务拓扑图、流量图和性能仪表板
- **自动化优化**: 基于分析结果提供自动化优化建议和配置调整

## 服务网格分析器核心

### 网格连接器
```python
# service_mesh_analyzer.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import datetime
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import math
import requests
import kubernetes
from kubernetes import client, config
import prometheus_client
import grafana_api
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

class MeshType(Enum):
    """服务网格类型枚举"""
    ISTIO = "istio"
    LINKERD = "linkerd"
    CONSUL_CONNECT = "consul_connect"
    CUSTOM = "custom"

class AnalysisType(Enum):
    """分析类型枚举"""
    TRAFFIC = "traffic"
    PERFORMANCE = "performance"
    SECURITY = "security"
    FAULT = "fault"
    CUSTOM = "custom"

class AlertLevel(Enum):
    """告警级别枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class MeshCluster:
    """网格集群"""
    cluster_id: str
    name: str
    type: MeshType
    endpoint: str
    namespace: str
    credentials: Dict[str, Any]
    status: str = "active"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceInfo:
    """服务信息"""
    service_id: str
    name: str
    namespace: str
    version: str
    labels: Dict[str, str]
    endpoints: List[str]
    mesh_type: MeshType
    status: str = "running"

@dataclass
class TrafficMetrics:
    """流量指标"""
    metrics_id: str
    source_service: str
    destination_service: str
    request_count: int
    response_time: float
    error_rate: float
    throughput: float
    timestamp: datetime
    protocol: str = "http"

@dataclass
class SecurityEvent:
    """安全事件"""
    event_id: str
    event_type: str
    source_service: str
    destination_service: str
    severity: AlertLevel
    description: str
    timestamp: datetime
    details: Dict[str, Any]

@dataclass
class PerformanceMetrics:
    """性能指标"""
    metrics_id: str
    service_name: str
    cpu_usage: float
    memory_usage: float
    network_io: float
    disk_io: float
    response_time_p50: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    timestamp: datetime

class KubernetesConnector:
    """Kubernetes连接器"""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.kubeconfig_path = kubeconfig_path
        self.api_client = None
        self.core_v1 = None
        self.apps_v1 = None
        self.custom_api = None
    
    def connect(self):
        """连接Kubernetes集群"""
        try:
            if self.kubeconfig_path:
                config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                config.load_incluster_config()
            
            self.api_client = client.ApiClient()
            self.core_v1 = client.CoreV1Api(self.api_client)
            self.apps_v1 = client.AppsV1Api(self.api_client)
            self.custom_api = client.CustomObjectsApi(self.api_client)
            
            self.logger.info("Kubernetes连接成功")
        
        except Exception as e:
            self.logger.error(f"Kubernetes连接失败: {e}")
            raise
    
    def get_namespaces(self) -> List[str]:
        """获取命名空间列表"""
        try:
            namespaces = []
            ns_list = self.core_v1.list_namespace()
            
            for ns in ns_list.items:
                namespaces.append(ns.metadata.name)
            
            return namespaces
        
        except Exception as e:
            self.logger.error(f"获取命名空间失败: {e}")
            raise
    
    def get_services(self, namespace: str) -> List[ServiceInfo]:
        """获取服务列表"""
        try:
            services = []
            svc_list = self.core_v1.list_namespaced_service(namespace=namespace)
            
            for svc in svc_list.items:
                service_info = ServiceInfo(
                    service_id=str(uuid.uuid4()),
                    name=svc.metadata.name,
                    namespace=svc.metadata.namespace,
                    version=svc.metadata.labels.get('version', 'unknown'),
                    labels=svc.metadata.labels or {},
                    endpoints=[f"{svc.metadata.name}.{svc.metadata.namespace}.svc.cluster.local"],
                    mesh_type=MeshType.ISTIO  # 默认为Istio
                )
                services.append(service_info)
            
            return services
        
        except Exception as e:
            self.logger.error(f"获取服务列表失败: {e}")
            raise
    
    def get_pods(self, namespace: str) -> List[Dict[str, Any]]:
        """获取Pod列表"""
        try:
            pods = []
            pod_list = self.core_v1.list_namespaced_pod(namespace=namespace)
            
            for pod in pod_list.items:
                pod_info = {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'labels': pod.metadata.labels or {},
                    'status': pod.status.phase,
                    'ip': pod.status.pod_ip,
                    'node': pod.spec.node_name
                }
                pods.append(pod_info)
            
            return pods
        
        except Exception as e:
            self.logger.error(f"获取Pod列表失败: {e}")
            raise
    
    def get_istio_config(self, namespace: str) -> Dict[str, Any]:
        """获取Istio配置"""
        try:
            istio_config = {}
            
            # 获取VirtualService
            vs_list = self.custom_api.list_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=namespace,
                plural="virtualservices"
            )
            istio_config['virtual_services'] = vs_list.get('items', [])
            
            # 获取DestinationRule
            dr_list = self.custom_api.list_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=namespace,
                plural="destinationrules"
            )
            istio_config['destination_rules'] = dr_list.get('items', [])
            
            # 获取Gateway
            gw_list = self.custom_api.list_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=namespace,
                plural="gateways"
            )
            istio_config['gateways'] = gw_list.get('items', [])
            
            return istio_config
        
        except Exception as e:
            self.logger.error(f"获取Istio配置失败: {e}")
            return {}

class PrometheusConnector:
    """Prometheus连接器"""
    
    def __init__(self, prometheus_url: str):
        self.logger = logging.getLogger(__name__)
        self.prometheus_url = prometheus_url
        self.session = requests.Session()
    
    def query(self, query: str, time_param: Optional[str] = None) -> Dict[str, Any]:
        """执行Prometheus查询"""
        try:
            params = {'query': query}
            if time_param:
                params['time'] = time_param
            
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Prometheus查询失败: {e}")
            raise
    
    def query_range(self, query: str, start: str, end: str, step: str) -> Dict[str, Any]:
        """执行Prometheus范围查询"""
        try:
            params = {
                'query': query,
                'start': start,
                'end': end,
                'step': step
            }
            
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            self.logger.error(f"Prometheus范围查询失败: {e}")
            raise
    
    def get_traffic_metrics(self, service: str, namespace: str, 
                           duration: str = "1h") -> List[TrafficMetrics]:
        """获取流量指标"""
        try:
            metrics = []
            
            # 查询请求总数
            request_query = f'sum(rate(istio_requests_total{{destination_service="{service}",destination_namespace="{namespace}"}}[5m]))'
            request_result = self.query(request_query)
            
            # 查询响应时间
            latency_query = f'histogram_quantile(0.95, sum(rate(istio_request_duration_seconds_bucket{{destination_service="{service}",destination_namespace="{namespace}"}}[5m])) by (le))'
            latency_result = self.query(latency_query)
            
            # 查询错误率
            error_query = f'sum(rate(istio_requests_total{{destination_service="{service}",destination_namespace="{namespace}",response_code!~"2.."}}[5m])) / sum(rate(istio_requests_total{{destination_service="{service}",destination_namespace="{namespace}"}}[5m]))'
            error_result = self.query(error_query)
            
            # 解析结果
            timestamp = datetime.now()
            
            request_count = 0
            if request_result.get('data', {}).get('result'):
                request_count = float(request_result['data']['result'][0]['value'][1])
            
            response_time = 0.0
            if latency_result.get('data', {}).get('result'):
                response_time = float(latency_result['data']['result'][0]['value'][1])
            
            error_rate = 0.0
            if error_result.get('data', {}).get('result'):
                error_rate = float(error_result['data']['result'][0]['value'][1])
            
            throughput = request_count / 3600  # 每秒请求数
            
            metric = TrafficMetrics(
                metrics_id=str(uuid.uuid4()),
                source_service="unknown",
                destination_service=service,
                request_count=int(request_count * 3600),  # 1小时内的总请求数
                response_time=response_time,
                error_rate=error_rate,
                throughput=throughput,
                timestamp=timestamp
            )
            
            metrics.append(metric)
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"获取流量指标失败: {e}")
            return []

class TrafficAnalyzer:
    """流量分析器"""
    
    def __init__(self, prometheus_connector: PrometheusConnector):
        self.logger = logging.getLogger(__name__)
        self.prometheus = prometheus_connector
        self.traffic_data = []
        self.lock = threading.Lock()
    
    def analyze_traffic(self, services: List[ServiceInfo], 
                       namespace: str, duration: str = "1h") -> Dict[str, Any]:
        """分析流量模式"""
        try:
            analysis_result = {
                'total_requests': 0,
                'total_services': len(services),
                'service_metrics': {},
                'traffic_matrix': {},
                'top_services': [],
                'anomalies': []
            }
            
            total_requests = 0
            
            for service in services:
                # 获取服务流量指标
                metrics = self.prometheus.get_traffic_metrics(
                    service.name, namespace, duration
                )
                
                if metrics:
                    metric = metrics[0]
                    analysis_result['service_metrics'][service.name] = {
                        'request_count': metric.request_count,
                        'response_time': metric.response_time,
                        'error_rate': metric.error_rate,
                        'throughput': metric.throughput
                    }
                    
                    total_requests += metric.request_count
            
            analysis_result['total_requests'] = total_requests
            
            # 生成流量矩阵
            analysis_result['traffic_matrix'] = self._generate_traffic_matrix(
                services, namespace
            )
            
            # 识别Top服务
            analysis_result['top_services'] = self._identify_top_services(
                analysis_result['service_metrics']
            )
            
            # 异常检测
            analysis_result['anomalies'] = self._detect_anomalies(
                analysis_result['service_metrics']
            )
            
            return analysis_result
        
        except Exception as e:
            self.logger.error(f"流量分析失败: {e}")
            raise
    
    def _generate_traffic_matrix(self, services: List[ServiceInfo], 
                                namespace: str) -> Dict[str, Dict[str, float]]:
        """生成流量矩阵"""
        try:
            traffic_matrix = {}
            
            for source_service in services:
                traffic_matrix[source_service.name] = {}
                
                for dest_service in services:
                    if source_service.name == dest_service.name:
                        continue
                    
                    # 查询服务间流量
                    query = f'sum(rate(istio_requests_total{{source_service="{source_service.name}",destination_service="{dest_service.name}"}}[5m]))'
                    result = self.prometheus.query(query)
                    
                    traffic_value = 0.0
                    if result.get('data', {}).get('result'):
                        traffic_value = float(result['data']['result'][0]['value'][1])
                    
                    traffic_matrix[source_service.name][dest_service.name] = traffic_value
            
            return traffic_matrix
        
        except Exception as e:
            self.logger.error(f"生成流量矩阵失败: {e}")
            return {}
    
    def _identify_top_services(self, service_metrics: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别Top服务"""
        try:
            top_services = []
            
            for service_name, metrics in service_metrics.items():
                top_services.append({
                    'service_name': service_name,
                    'request_count': metrics['request_count'],
                    'response_time': metrics['response_time'],
                    'error_rate': metrics['error_rate']
                })
            
            # 按请求数排序
            top_services.sort(key=lambda x: x['request_count'], reverse=True)
            
            return top_services[:10]  # 返回Top 10
        
        except Exception as e:
            self.logger.error(f"识别Top服务失败: {e}")
            return []
    
    def _detect_anomalies(self, service_metrics: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测异常"""
        try:
            anomalies = []
            
            for service_name, metrics in service_metrics.items():
                service_anomalies = []
                
                # 检测高错误率
                if metrics['error_rate'] > 0.05:  # 5%
                    service_anomalies.append({
                        'type': 'high_error_rate',
                        'value': metrics['error_rate'],
                        'threshold': 0.05,
                        'severity': AlertLevel.HIGH
                    })
                
                # 检测高响应时间
                if metrics['response_time'] > 1.0:  # 1秒
                    service_anomalies.append({
                        'type': 'high_response_time',
                        'value': metrics['response_time'],
                        'threshold': 1.0,
                        'severity': AlertLevel.MEDIUM
                    })
                
                # 检测低吞吐量
                if metrics['throughput'] < 1.0:  # 每秒少于1个请求
                    service_anomalies.append({
                        'type': 'low_throughput',
                        'value': metrics['throughput'],
                        'threshold': 1.0,
                        'severity': AlertLevel.LOW
                    })
                
                if service_anomalies:
                    anomalies.append({
                        'service_name': service_name,
                        'anomalies': service_anomalies
                    })
            
            return anomalies
        
        except Exception as e:
            self.logger.error(f"检测异常失败: {e}")
            return []

class SecurityAnalyzer:
    """安全分析器"""
    
    def __init__(self, prometheus_connector: PrometheusConnector):
        self.logger = logging.getLogger(__name__)
        self.prometheus = prometheus_connector
        self.security_events = []
        self.lock = threading.Lock()
    
    def analyze_security(self, services: List[ServiceInfo], 
                        namespace: str) -> Dict[str, Any]:
        """分析安全状况"""
        try:
            security_analysis = {
                'total_events': 0,
                'security_score': 0.0,
                'policy_violations': [],
                'authentication_failures': [],
                'authorization_failures': [],
                'suspicious_activities': []
            }
            
            # 检查认证失败
            auth_failures = self._check_authentication_failures(namespace)
            security_analysis['authentication_failures'] = auth_failures
            
            # 检查授权失败
            authz_failures = self._check_authorization_failures(namespace)
            security_analysis['authorization_failures'] = authz_failures
            
            # 检查可疑活动
            suspicious_activities = self._check_suspicious_activities(namespace)
            security_analysis['suspicious_activities'] = suspicious_activities
            
            # 计算安全评分
            security_analysis['security_score'] = self._calculate_security_score(
                security_analysis
            )
            
            security_analysis['total_events'] = (
                len(auth_failures) + len(authz_failures) + len(suspicious_activities)
            )
            
            return security_analysis
        
        except Exception as e:
            self.logger.error(f"安全分析失败: {e}")
            raise
    
    def _check_authentication_failures(self, namespace: str) -> List[Dict[str, Any]]:
        """检查认证失败"""
        try:
            failures = []
            
            # 查询认证失败指标
            query = f'sum(rate(istio_authentication_denied{{namespace="{namespace}"}}[5m]))'
            result = self.prometheus.query(query)
            
            if result.get('data', {}).get('result'):
                for item in result['data']['result']:
                    failure_rate = float(item['value'][1])
                    
                    if failure_rate > 0:
                        failures.append({
                            'type': 'authentication_failure',
                            'source': item['metric'].get('source_service', 'unknown'),
                            'destination': item['metric'].get('destination_service', 'unknown'),
                            'failure_rate': failure_rate,
                            'severity': AlertLevel.HIGH
                        })
            
            return failures
        
        except Exception as e:
            self.logger.error(f"检查认证失败失败: {e}")
            return []
    
    def _check_authorization_failures(self, namespace: str) -> List[Dict[str, Any]]:
        """检查授权失败"""
        try:
            failures = []
            
            # 查询授权失败指标
            query = f'sum(rate(istio_authorization_denied{{namespace="{namespace}"}}[5m]))'
            result = self.prometheus.query(query)
            
            if result.get('data', {}).get('result'):
                for item in result['data']['result']:
                    failure_rate = float(item['value'][1])
                    
                    if failure_rate > 0:
                        failures.append({
                            'type': 'authorization_failure',
                            'source': item['metric'].get('source_service', 'unknown'),
                            'destination': item['metric'].get('destination_service', 'unknown'),
                            'failure_rate': failure_rate,
                            'severity': AlertLevel.MEDIUM
                        })
            
            return failures
        
        except Exception as e:
            self.logger.error(f"检查授权失败失败: {e}")
            return []
    
    def _check_suspicious_activities(self, namespace: str) -> List[Dict[str, Any]]:
        """检查可疑活动"""
        try:
            suspicious = []
            
            # 检查异常高频请求
            query = f'sum(rate(istio_requests_total{{namespace="{namespace}"}}[5m])) by (source_service)'
            result = self.prometheus.query(query)
            
            if result.get('data', {}).get('result'):
                for item in result['data']['result']:
                    request_rate = float(item['value'][1])
                    
                    if request_rate > 1000:  # 每秒超过1000个请求
                        suspicious.append({
                            'type': 'high_frequency_requests',
                            'source_service': item['metric'].get('source_service', 'unknown'),
                            'request_rate': request_rate,
                            'severity': AlertLevel.MEDIUM
                        })
            
            return suspicious
        
        except Exception as e:
            self.logger.error(f"检查可疑活动失败: {e}")
            return []
    
    def _calculate_security_score(self, security_analysis: Dict[str, Any]) -> float:
        """计算安全评分"""
        try:
            base_score = 100.0
            
            # 根据事件数量扣分
            auth_failure_penalty = len(security_analysis['authentication_failures']) * 10
            authz_failure_penalty = len(security_analysis['authorization_failures']) * 5
            suspicious_penalty = len(security_analysis['suspicious_activities']) * 3
            
            total_penalty = auth_failure_penalty + authz_failure_penalty + suspicious_penalty
            
            score = max(0.0, base_score - total_penalty)
            
            return score
        
        except Exception as e:
            self.logger.error(f"计算安全评分失败: {e}")
            return 0.0

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, prometheus_connector: PrometheusConnector):
        self.logger = logging.getLogger(__name__)
        self.prometheus = prometheus_connector
        self.performance_data = []
        self.lock = threading.Lock()
    
    def analyze_performance(self, services: List[ServiceInfo], 
                           namespace: str) -> Dict[str, Any]:
        """分析性能状况"""
        try:
            performance_analysis = {
                'total_services': len(services),
                'service_performance': {},
                'bottlenecks': [],
                'optimization_suggestions': [],
                'performance_score': 0.0
            }
            
            for service in services:
                # 获取服务性能指标
                service_perf = self._get_service_performance(service.name, namespace)
                performance_analysis['service_performance'][service.name] = service_perf
                
                # 检测性能瓶颈
                bottlenecks = self._detect_bottlenecks(service_perf)
                if bottlenecks:
                    performance_analysis['bottlenecks'].extend(bottlenecks)
                
                # 生成优化建议
                suggestions = self._generate_optimization_suggestions(service_perf)
                if suggestions:
                    performance_analysis['optimization_suggestions'].extend(suggestions)
            
            # 计算性能评分
            performance_analysis['performance_score'] = self._calculate_performance_score(
                performance_analysis['service_performance']
            )
            
            return performance_analysis
        
        except Exception as e:
            self.logger.error(f"性能分析失败: {e}")
            raise
    
    def _get_service_performance(self, service_name: str, namespace: str) -> Dict[str, Any]:
        """获取服务性能指标"""
        try:
            performance = {}
            
            # 查询CPU使用率
            cpu_query = f'sum(rate(container_cpu_usage_seconds_total{{pod=~"{service_name}.*",namespace="{namespace}"}}[5m]))'
            cpu_result = self.prometheus.query(cpu_query)
            
            # 查询内存使用率
            memory_query = f'sum(container_memory_usage_bytes{{pod=~"{service_name}.*",namespace="{namespace}"}}) / sum(container_spec_memory_limit_bytes{{pod=~"{service_name}.*",namespace="{namespace}"}})'
            memory_result = self.prometheus.query(memory_query)
            
            # 查询响应时间
            latency_query = f'histogram_quantile(0.95, sum(rate(istio_request_duration_seconds_bucket{{destination_service="{service_name}",destination_namespace="{namespace}"}}[5m])) by (le))'
            latency_result = self.prometheus.query(latency_query)
            
            # 解析结果
            if cpu_result.get('data', {}).get('result'):
                performance['cpu_usage'] = float(cpu_result['data']['result'][0]['value'][1])
            
            if memory_result.get('data', {}).get('result'):
                performance['memory_usage'] = float(memory_result['data']['result'][0]['value'][1])
            
            if latency_result.get('data', {}).get('result'):
                performance['response_time_p95'] = float(latency_result['data']['result'][0]['value'][1])
            
            return performance
        
        except Exception as e:
            self.logger.error(f"获取服务性能指标失败: {e}")
            return {}
    
    def _detect_bottlenecks(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测性能瓶颈"""
        try:
            bottlenecks = []
            
            # 检测CPU瓶颈
            cpu_usage = performance.get('cpu_usage', 0)
            if cpu_usage > 0.8:  # 80%
                bottlenecks.append({
                    'type': 'cpu_bottleneck',
                    'value': cpu_usage,
                    'threshold': 0.8,
                    'severity': AlertLevel.HIGH
                })
            
            # 检测内存瓶颈
            memory_usage = performance.get('memory_usage', 0)
            if memory_usage > 0.9:  # 90%
                bottlenecks.append({
                    'type': 'memory_bottleneck',
                    'value': memory_usage,
                    'threshold': 0.9,
                    'severity': AlertLevel.HIGH
                })
            
            # 检测响应时间瓶颈
            response_time = performance.get('response_time_p95', 0)
            if response_time > 2.0:  # 2秒
                bottlenecks.append({
                    'type': 'response_time_bottleneck',
                    'value': response_time,
                    'threshold': 2.0,
                    'severity': AlertLevel.MEDIUM
                })
            
            return bottlenecks
        
        except Exception as e:
            self.logger.error(f"检测性能瓶颈失败: {e}")
            return []
    
    def _generate_optimization_suggestions(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        try:
            suggestions = []
            
            # CPU优化建议
            cpu_usage = performance.get('cpu_usage', 0)
            if cpu_usage > 0.8:
                suggestions.append({
                    'type': 'cpu_optimization',
                    'suggestion': '增加CPU资源限制或优化代码以减少CPU使用',
                    'priority': 'high'
                })
            
            # 内存优化建议
            memory_usage = performance.get('memory_usage', 0)
            if memory_usage > 0.9:
                suggestions.append({
                    'type': 'memory_optimization',
                    'suggestion': '增加内存限制或检查内存泄漏',
                    'priority': 'high'
                })
            
            # 响应时间优化建议
            response_time = performance.get('response_time_p95', 0)
            if response_time > 2.0:
                suggestions.append({
                    'type': 'response_time_optimization',
                    'suggestion': '优化数据库查询、增加缓存或调整并发设置',
                    'priority': 'medium'
                })
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"生成优化建议失败: {e}")
            return []
    
    def _calculate_performance_score(self, service_performance: Dict[str, Dict[str, Any]]) -> float:
        """计算性能评分"""
        try:
            if not service_performance:
                return 0.0
            
            total_score = 0.0
            service_count = len(service_performance)
            
            for service_name, performance in service_performance.items():
                service_score = 100.0
                
                # CPU评分
                cpu_usage = performance.get('cpu_usage', 0)
                if cpu_usage > 0.8:
                    service_score -= (cpu_usage - 0.8) * 100
                
                # 内存评分
                memory_usage = performance.get('memory_usage', 0)
                if memory_usage > 0.9:
                    service_score -= (memory_usage - 0.9) * 100
                
                # 响应时间评分
                response_time = performance.get('response_time_p95', 0)
                if response_time > 2.0:
                    service_score -= (response_time - 2.0) * 20
                
                total_score += max(0.0, service_score)
            
            return total_score / service_count
        
        except Exception as e:
            self.logger.error(f"计算性能评分失败: {e}")
            return 0.0

class VisualizationEngine:
    """可视化引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_service_topology(self, services: List[ServiceInfo], 
                                 traffic_matrix: Dict[str, Dict[str, float]]) -> str:
        """生成服务拓扑图"""
        try:
            # 创建有向图
            G = nx.DiGraph()
            
            # 添加节点
            for service in services:
                G.add_node(service.name, 
                          namespace=service.namespace,
                          version=service.version)
            
            # 添加边
            for source_service, destinations in traffic_matrix.items():
                for dest_service, traffic_value in destinations.items():
                    if traffic_value > 0:
                        G.add_edge(source_service, dest_service, 
                                  weight=traffic_value)
            
            # 生成可视化
            fig = go.Figure()
            
            # 计算布局
            pos = nx.spring_layout(G)
            
            # 添加边
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            ))
            
            # 添加节点
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node)
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(
                    size=20,
                    color='lightblue',
                    line=dict(width=2, color='darkblue')
                )
            ))
            
            fig.update_layout(
                title="服务拓扑图",
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="服务网格拓扑",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color="grey", size=12)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            # 保存为HTML
            html_file = f"/tmp/service_topology_{uuid.uuid4()}.html"
            fig.write_html(html_file)
            
            return html_file
        
        except Exception as e:
            self.logger.error(f"生成服务拓扑图失败: {e}")
            raise
    
    def generate_traffic_dashboard(self, traffic_analysis: Dict[str, Any]) -> str:
        """生成流量仪表板"""
        try:
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Top服务', '错误率分布', '响应时间分布', '流量趋势'),
                specs=[[{"type": "bar"}, {"type": "pie"}],
                       [{"type": "scatter"}, {"type": "line"}]]
            )
            
            # Top服务柱状图
            top_services = traffic_analysis.get('top_services', [])[:10]
            service_names = [s['service_name'] for s in top_services]
            request_counts = [s['request_count'] for s in top_services]
            
            fig.add_trace(
                go.Bar(x=service_names, y=request_counts, name="请求数"),
                row=1, col=1
            )
            
            # 错误率饼图
            error_rates = {}
            for service_name, metrics in traffic_analysis.get('service_metrics', {}).items():
                error_rate = metrics.get('error_rate', 0)
                if error_rate > 0:
                    error_rates[service_name] = error_rate
            
            if error_rates:
                fig.add_trace(
                    go.Pie(labels=list(error_rates.keys()), 
                          values=list(error_rates.values()),
                          name="错误率"),
                    row=1, col=2
                )
            
            # 响应时间散点图
            response_times = []
            for service_name, metrics in traffic_analysis.get('service_metrics', {}).items():
                response_time = metrics.get('response_time', 0)
                if response_time > 0:
                    response_times.append({
                        'service': service_name,
                        'response_time': response_time
                    })
            
            if response_times:
                fig.add_trace(
                    go.Scatter(
                        x=[r['service'] for r in response_times],
                        y=[r['response_time'] for r in response_times],
                        mode='markers',
                        name="响应时间"
                    ),
                    row=2, col=1
                )
            
            # 更新布局
            fig.update_layout(
                title="流量分析仪表板",
                height=800,
                showlegend=False
            )
            
            # 保存为HTML
            html_file = f"/tmp/traffic_dashboard_{uuid.uuid4()}.html"
            fig.write_html(html_file)
            
            return html_file
        
        except Exception as e:
            self.logger.error(f"生成流量仪表板失败: {e}")
            raise

class ServiceMeshAnalyzer:
    """服务网格分析器主类"""
    
    def __init__(self, cluster_config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.cluster_config = cluster_config
        self.k8s_connector = KubernetesConnector(cluster_config.get('kubeconfig_path'))
        self.prometheus_connector = PrometheusConnector(cluster_config.get('prometheus_url'))
        self.traffic_analyzer = TrafficAnalyzer(self.prometheus_connector)
        self.security_analyzer = SecurityAnalyzer(self.prometheus_connector)
        self.performance_analyzer = PerformanceAnalyzer(self.prometheus_connector)
        self.visualization_engine = VisualizationEngine()
    
    def initialize(self):
        """初始化分析器"""
        try:
            self.k8s_connector.connect()
            self.logger.info("服务网格分析器初始化成功")
        
        except Exception as e:
            self.logger.error(f"服务网格分析器初始化失败: {e}")
            raise
    
    def analyze_mesh(self, namespace: str) -> Dict[str, Any]:
        """分析服务网格"""
        try:
            # 获取服务列表
            services = self.k8s_connector.get_services(namespace)
            
            # 流量分析
            traffic_analysis = self.traffic_analyzer.analyze_traffic(services, namespace)
            
            # 安全分析
            security_analysis = self.security_analyzer.analyze_security(services, namespace)
            
            # 性能分析
            performance_analysis = self.performance_analyzer.analyze_performance(services, namespace)
            
            # 生成可视化
            topology_file = self.visualization_engine.generate_service_topology(
                services, traffic_analysis.get('traffic_matrix', {})
            )
            
            dashboard_file = self.visualization_engine.generate_traffic_dashboard(traffic_analysis)
            
            # 综合分析结果
            analysis_result = {
                'namespace': namespace,
                'total_services': len(services),
                'traffic_analysis': traffic_analysis,
                'security_analysis': security_analysis,
                'performance_analysis': performance_analysis,
                'visualizations': {
                    'topology': topology_file,
                    'dashboard': dashboard_file
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return analysis_result
        
        except Exception as e:
            self.logger.error(f"服务网格分析失败: {e}")
            raise
    
    def generate_report(self, analysis_result: Dict[str, Any], 
                      output_path: str) -> str:
        """生成分析报告"""
        try:
            report_content = f"""# 服务网格分析报告

## 基本信息

- **命名空间**: {analysis_result['namespace']}
- **服务总数**: {analysis_result['total_services']}
- **分析时间**: {analysis_result['timestamp']}

## 流量分析

- **总请求数**: {analysis_result['traffic_analysis'].get('total_requests', 0)}
- **Top服务**: {len(analysis_result['traffic_analysis'].get('top_services', []))}
- **异常数量**: {len(analysis_result['traffic_analysis'].get('anomalies', []))}

## 安全分析

- **安全事件**: {analysis_result['security_analysis'].get('total_events', 0)}
- **安全评分**: {analysis_result['security_analysis'].get('security_score', 0):.2f}
- **认证失败**: {len(analysis_result['security_analysis'].get('authentication_failures', []))}
- **授权失败**: {len(analysis_result['security_analysis'].get('authorization_failures', []))}

## 性能分析

- **性能评分**: {analysis_result['performance_analysis'].get('performance_score', 0):.2f}
- **瓶颈数量**: {len(analysis_result['performance_analysis'].get('bottlenecks', []))}
- **优化建议**: {len(analysis_result['performance_analysis'].get('optimization_suggestions', []))}

## 可视化

- **服务拓扑**: {analysis_result['visualizations'].get('topology', '')}
- **流量仪表板**: {analysis_result['visualizations'].get('dashboard', '')}

## 详细信息

### 流量详情
{json.dumps(analysis_result['traffic_analysis'], indent=2, ensure_ascii=False)}

### 安全详情
{json.dumps(analysis_result['security_analysis'], indent=2, ensure_ascii=False)}

### 性能详情
{json.dumps(analysis_result['performance_analysis'], indent=2, ensure_ascii=False)}
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"分析报告已保存到: {output_path}")
            
            return output_path
        
        except Exception as e:
            self.logger.error(f"生成分析报告失败: {e}")
            raise

# 使用示例
# 配置集群信息
cluster_config = {
    'kubeconfig_path': '/path/to/kubeconfig',
    'prometheus_url': 'http://prometheus:9090'
}

# 创建服务网格分析器
analyzer = ServiceMeshAnalyzer(cluster_config)

# 初始化
analyzer.initialize()

# 分析服务网格
try:
    result = analyzer.analyze_mesh('default')
    print(f"分析完成: 服务数量 {result['total_services']}")
    print(f"安全评分: {result['security_analysis']['security_score']:.2f}")
    print(f"性能评分: {result['performance_analysis']['performance_score']:.2f}")
    
    # 生成报告
    report_path = analyzer.generate_report(result, '/tmp/mesh_analysis_report.md')
    print(f"报告已生成: {report_path}")
    
except Exception as e:
    print(f"分析失败: {e}")
```

## 参考资源

### 服务网格文档
- [Istio官方文档](https://istio.io/docs/)
- [Linkerd官方文档](https://linkerd.io/docs/)
- [Consul Connect文档](https://www.consul.io/docs/connect)
- [服务网格对比](https://kubernetes.io/blog/2018/08/service-mesh-comparison/)

### 监控和可视化
- [Prometheus文档](https://prometheus.io/docs/)
- [Grafana文档](https://grafana.com/docs/)
- [Kubernetes监控](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/)
- [服务网格监控最佳实践](https://istio.io/docs/tasks/observability/)

### 安全和性能
- [Istio安全文档](https://istio.io/docs/concepts/security/)
- [服务网格性能优化](https://istio.io/docs/tasks/observability/telemetry/)
- [微服务安全最佳实践](https://owasp.org/www-project-microservices-security/)
- [服务网格故障排查](https://istio.io/docs/tasks/debugging/)
