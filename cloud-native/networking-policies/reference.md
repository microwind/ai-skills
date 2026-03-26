# Kubernetes网络策略参考文档

## Kubernetes网络策略概述

### 什么是Kubernetes网络策略
Kubernetes网络策略是Kubernetes提供的原生网络流量控制机制，用于定义Pod之间以及Pod与外部服务之间的通信规则。网络策略基于标签选择器工作，可以控制入站（ingress）和出站（egress）流量，实现微服务架构中的网络隔离和安全防护。网络策略是云原生安全体系的重要组成部分，为Kubernetes集群提供了细粒度的网络访问控制。

### 主要功能
- **网络隔离**: 实现Pod级别的网络隔离，控制服务间通信
- **流量控制**: 精确控制入站和出站流量，支持端口和协议级别的控制
- **安全防护**: 防止未经授权的网络访问，增强集群安全性
- **合规支持**: 满足安全合规要求，如PCI-DSS、HIPAA等
- **微服务安全**: 为微服务架构提供网络层面的安全保障
- **多租户隔离**: 在多租户环境中实现租户间的网络隔离

## Kubernetes网络策略核心

### 网络策略引擎
```python
# kubernetes_networking_policies.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import re
import ipaddress
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import statistics
import math
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import jinja2
import networkx as nx
from ipaddress import IPv4Network, IPv6Network, ip_network

class PolicyType(Enum):
    """策略类型枚举"""
    INGRESS = "ingress"
    EGRESS = "egress"
    BIDIRECTIONAL = "bidirectional"
    ISOLATION = "isolation"

class PolicyAction(Enum):
    """策略动作枚举"""
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"
    CUSTOM = "custom"

class Protocol(Enum):
    """协议枚举"""
    TCP = "TCP"
    UDP = "UDP"
    SCTP = "SCTP"
    ICMP = "ICMP"
    ANY = "any"

@dataclass
class NetworkPolicyRule:
    """网络策略规则"""
    rule_id: str
    policy_type: PolicyType
    action: PolicyAction
    description: str
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IngressRule:
    """入站规则"""
    rule_id: str
    from_sources: List[Dict[str, Any]] = field(default_factory=list)
    ports: List[Dict[str, Any]] = field(default_factory=list)
    action: PolicyAction = PolicyAction.ALLOW
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EgressRule:
    """出站规则"""
    rule_id: str
    to_destinations: List[Dict[str, Any]] = field(default_factory=list)
    ports: List[Dict[str, Any]] = field(default_factory=list)
    action: PolicyAction = PolicyAction.ALLOW
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkPolicy:
    """网络策略"""
    policy_id: str
    name: str
    namespace: str
    pod_selector: Dict[str, str]
    policy_types: List[PolicyType]
    ingress_rules: List[IngressRule] = field(default_factory=list)
    egress_rules: List[EgressRule] = field(default_factory=list)
    ingress_action: PolicyAction = PolicyAction.ALLOW
    egress_action: PolicyAction = PolicyAction.ALLOW
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

@dataclass
class TrafficFlow:
    """流量流"""
    flow_id: str
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: Protocol
    timestamp: datetime
    action: str
    policy_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class NetworkPolicyManager:
    """网络策略管理器"""
    
    def __init__(self, k8s_client=None):
        self.k8s_client = k8s_client or self._create_k8s_client()
        self.logger = logging.getLogger(__name__)
        self.policies = {}
        self.policy_graph = nx.DiGraph()
        self.traffic_flows = []
        self.lock = threading.Lock()
    
    def _create_k8s_client(self):
        """创建Kubernetes客户端"""
        try:
            config.load_kube_config()
            return client.NetworkingV1Api()
        except Exception as e:
            self.logger.error(f"创建Kubernetes客户端失败: {e}")
            raise
    
    def create_policy(self, policy: NetworkPolicy) -> bool:
        """创建网络策略"""
        try:
            # 创建Kubernetes NetworkPolicy对象
            k8s_policy = self._convert_to_k8s_policy(policy)
            
            # 应用到集群
            self.k8s_client.create_namespaced_network_policy(
                namespace=policy.namespace,
                body=k8s_policy
            )
            
            # 更新本地状态
            with self.lock:
                self.policies[policy.policy_id] = policy
                self._update_policy_graph()
            
            self.logger.info(f"网络策略创建成功: {policy.name}")
            return True
        
        except Exception as e:
            self.logger.error(f"创建网络策略失败: {e}")
            return False
    
    def update_policy(self, policy: NetworkPolicy) -> bool:
        """更新网络策略"""
        try:
            # 转换为Kubernetes对象
            k8s_policy = self._convert_to_k8s_policy(policy)
            
            # 更新集群中的策略
            self.k8s_client.patch_namespaced_network_policy(
                name=policy.name,
                namespace=policy.namespace,
                body=k8s_policy
            )
            
            # 更新本地状态
            with self.lock:
                policy.updated_at = datetime.now()
                self.policies[policy.policy_id] = policy
                self._update_policy_graph()
            
            self.logger.info(f"网络策略更新成功: {policy.name}")
            return True
        
        except Exception as e:
            self.logger.error(f"更新网络策略失败: {e}")
            return False
    
    def delete_policy(self, policy_id: str, namespace: str) -> bool:
        """删除网络策略"""
        try:
            policy = self.policies.get(policy_id)
            if not policy:
                self.logger.warning(f"策略不存在: {policy_id}")
                return False
            
            # 从集群删除
            self.k8s_client.delete_namespaced_network_policy(
                name=policy.name,
                namespace=policy.namespace
            )
            
            # 更新本地状态
            with self.lock:
                del self.policies[policy_id]
                self._update_policy_graph()
            
            self.logger.info(f"网络策略删除成功: {policy.name}")
            return True
        
        except Exception as e:
            self.logger.error(f"删除网络策略失败: {e}")
            return False
    
    def get_policy(self, policy_id: str) -> Optional[NetworkPolicy]:
        """获取网络策略"""
        with self.lock:
            return self.policies.get(policy_id)
    
    def list_policies(self, namespace: str = None) -> List[NetworkPolicy]:
        """列出网络策略"""
        with self.lock:
            policies = list(self.policies.values())
            if namespace:
                policies = [p for p in policies if p.namespace == namespace]
            return policies
    
    def _convert_to_k8s_policy(self, policy: NetworkPolicy) -> Dict[str, Any]:
        """转换为Kubernetes NetworkPolicy对象"""
        k8s_policy = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'NetworkPolicy',
            'metadata': {
                'name': policy.name,
                'namespace': policy.namespace,
                'labels': policy.labels,
                'annotations': policy.annotations
            },
            'spec': {
                'podSelector': policy.pod_selector,
                'policyTypes': [pt.value for pt in policy.policy_types]
            }
        }
        
        # 添加入站规则
        if PolicyType.INGRESS in policy.policy_types or PolicyType.BIDIRECTIONAL in policy.policy_types:
            k8s_policy['spec']['ingress'] = []
            for rule in policy.ingress_rules:
                ingress_rule = {}
                
                # 添加来源
                if rule.from_sources:
                    ingress_rule['from'] = []
                    for source in rule.from_sources:
                        if 'podSelector' in source:
                            ingress_rule['from'].append({'podSelector': source['podSelector']})
                        elif 'namespaceSelector' in source:
                            ingress_rule['from'].append({'namespaceSelector': source['namespaceSelector']})
                        elif 'ipBlock' in source:
                            ingress_rule['from'].append({'ipBlock': source['ipBlock']})
                
                # 添加端口
                if rule.ports:
                    ingress_rule['ports'] = []
                    for port in rule.ports:
                        port_rule = {}
                        if 'port' in port:
                            port_rule['port'] = port['port']
                        if 'protocol' in port:
                            port_rule['protocol'] = port['protocol']
                        if 'endPort' in port:
                            port_rule['endPort'] = port['endPort']
                        ingress_rule['ports'].append(port_rule)
                
                k8s_policy['spec']['ingress'].append(ingress_rule)
        
        # 添加出站规则
        if PolicyType.EGRESS in policy.policy_types or PolicyType.BIDIRECTIONAL in policy.policy_types:
            k8s_policy['spec']['egress'] = []
            for rule in policy.egress_rules:
                egress_rule = {}
                
                # 添加目标
                if rule.to_destinations:
                    egress_rule['to'] = []
                    for dest in rule.to_destinations:
                        if 'podSelector' in dest:
                            egress_rule['to'].append({'podSelector': dest['podSelector']})
                        elif 'namespaceSelector' in dest:
                            egress_rule['to'].append({'namespaceSelector': dest['namespaceSelector']})
                        elif 'ipBlock' in dest:
                            egress_rule['to'].append({'ipBlock': dest['ipBlock']})
                
                # 添加端口
                if rule.ports:
                    egress_rule['ports'] = []
                    for port in rule.ports:
                        port_rule = {}
                        if 'port' in port:
                            port_rule['port'] = port['port']
                        if 'protocol' in port:
                            port_rule['protocol'] = port['protocol']
                        if 'endPort' in port:
                            port_rule['endPort'] = port['endPort']
                        egress_rule['ports'].append(port_rule)
                
                k8s_policy['spec']['egress'].append(egress_rule)
        
        return k8s_policy
    
    def _update_policy_graph(self):
        """更新策略图"""
        self.policy_graph.clear()
        
        for policy in self.policies.values():
            # 添加策略节点
            self.policy_graph.add_node(
                policy.policy_id,
                name=policy.name,
                namespace=policy.namespace,
                type='policy'
            )
            
            # 添加Pod选择器节点
            selector_key = f"{policy.namespace}:{json.dumps(policy.pod_selector, sort_keys=True)}"
            self.policy_graph.add_node(
                selector_key,
                selector=policy.pod_selector,
                namespace=policy.namespace,
                type='pod_selector'
            )
            
            # 连接策略到选择器
            self.policy_graph.add_edge(policy.policy_id, selector_key, type='selects')
            
            # 添加入站连接
            for rule in policy.ingress_rules:
                for source in rule.from_sources:
                    if 'podSelector' in source:
                        source_key = f"{policy.namespace}:{json.dumps(source['podSelector'], sort_keys=True)}"
                        self.policy_graph.add_node(
                            source_key,
                            selector=source['podSelector'],
                            namespace=policy.namespace,
                            type='source'
                        )
                        self.policy_graph.add_edge(source_key, policy.policy_id, type='ingress')
            
            # 添加出站连接
            for rule in policy.egress_rules:
                for dest in rule.to_destinations:
                    if 'podSelector' in dest:
                        dest_key = f"{policy.namespace}:{json.dumps(dest['podSelector'], sort_keys=True)}"
                        self.policy_graph.add_node(
                            dest_key,
                            selector=dest['podSelector'],
                            namespace=policy.namespace,
                            type='destination'
                        )
                        self.policy_graph.add_edge(policy.policy_id, dest_key, type='egress')

class TrafficAnalyzer:
    """流量分析器"""
    
    def __init__(self, policy_manager: NetworkPolicyManager):
        self.policy_manager = policy_manager
        self.logger = logging.getLogger(__name__)
        self.traffic_data = defaultdict(list)
        self.analysis_results = {}
    
    def record_traffic(self, flow: TrafficFlow):
        """记录流量"""
        self.traffic_data[flow.dest_ip].append(flow)
        
        # 分析流量
        self._analyze_flow(flow)
    
    def _analyze_flow(self, flow: TrafficFlow):
        """分析流量流"""
        try:
            # 获取目标Pod的策略
            policies = self.policy_manager.list_policies()
            
            # 检查是否被策略允许
            action = self._evaluate_traffic(flow, policies)
            
            # 更新流动作
            flow.action = action
            
            # 记录分析结果
            if flow.policy_id not in self.analysis_results:
                self.analysis_results[flow.policy_id] = {
                    'allowed_count': 0,
                    'denied_count': 0,
                    'total_bytes': 0,
                    'flows': []
                }
            
            result = self.analysis_results[flow.policy_id]
            if action == 'allow':
                result['allowed_count'] += 1
            else:
                result['denied_count'] += 1
            
            result['flows'].append(flow)
        
        except Exception as e:
            self.logger.error(f"分析流量失败: {e}")
    
    def _evaluate_traffic(self, flow: TrafficFlow, policies: List[NetworkPolicy]) -> str:
        """评估流量"""
        # 简化的流量评估逻辑
        for policy in policies:
            # 检查入站策略
            if PolicyType.INGRESS in policy.policy_types:
                for rule in policy.ingress_rules:
                    if self._matches_ingress_rule(flow, rule):
                        flow.policy_id = policy.policy_id
                        return 'allow' if rule.action == PolicyAction.ALLOW else 'deny'
            
            # 检查出站策略
            if PolicyType.EGRESS in policy.policy_types:
                for rule in policy.egress_rules:
                    if self._matches_egress_rule(flow, rule):
                        flow.policy_id = policy.policy_id
                        return 'allow' if rule.action == PolicyAction.ALLOW else 'deny'
        
        # 默认行为
        return 'deny'
    
    def _matches_ingress_rule(self, flow: TrafficFlow, rule: IngressRule) -> bool:
        """检查是否匹配入站规则"""
        # 检查端口匹配
        if rule.ports:
            port_matched = False
            for port in rule.ports:
                if self._matches_port(flow.dest_port, port):
                    port_matched = True
                    break
            if not port_matched:
                return False
        
        # 检查来源匹配（简化实现）
        return True
    
    def _matches_egress_rule(self, flow: TrafficFlow, rule: EgressRule) -> bool:
        """检查是否匹配出站规则"""
        # 检查端口匹配
        if rule.ports:
            port_matched = False
            for port in rule.ports:
                if self._matches_port(flow.dest_port, port):
                    port_matched = True
                    break
            if not port_matched:
                return False
        
        # 检查目标匹配（简化实现）
        return True
    
    def _matches_port(self, port: int, port_rule: Dict[str, Any]) -> bool:
        """检查端口匹配"""
        if 'port' in port_rule:
            rule_port = port_rule['port']
            if isinstance(rule_port, int):
                return port == rule_port
            elif isinstance(rule_port, str):
                return str(port) == rule_port
        
        if 'endPort' in port_rule:
            start_port = port_rule.get('port', 0)
            end_port = port_rule['endPort']
            return start_port <= port <= end_port
        
        return True
    
    def get_traffic_statistics(self, policy_id: str = None) -> Dict[str, Any]:
        """获取流量统计"""
        if policy_id:
            return self.analysis_results.get(policy_id, {})
        
        # 聚合所有策略的统计
        total_stats = {
            'allowed_count': 0,
            'denied_count': 0,
            'total_bytes': 0,
            'policy_stats': {}
        }
        
        for pid, stats in self.analysis_results.items():
            total_stats['allowed_count'] += stats['allowed_count']
            total_stats['denied_count'] += stats['denied_count']
            total_stats['total_bytes'] += stats['total_bytes']
            total_stats['policy_stats'][pid] = stats
        
        return total_stats
    
    def get_top_talkers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取流量最大的通信"""
        traffic_by_ip = defaultdict(int)
        
        for flows in self.traffic_data.values():
            for flow in flows:
                traffic_by_ip[flow.dest_ip] += 1
        
        top_talkers = sorted(
            traffic_by_ip.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [{'ip': ip, 'count': count} for ip, count in top_talkers]

class PolicyValidator:
    """策略验证器"""
    
    def __init__(self, policy_manager: NetworkPolicyManager):
        self.policy_manager = policy_manager
        self.logger = logging.getLogger(__name__)
    
    def validate_policy(self, policy: NetworkPolicy) -> Dict[str, Any]:
        """验证策略"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # 验证基本字段
        self._validate_basic_fields(policy, validation_result)
        
        # 验证选择器
        self._validate_selector(policy.pod_selector, validation_result)
        
        # 验证入站规则
        for rule in policy.ingress_rules:
            self._validate_ingress_rule(rule, validation_result)
        
        # 验证出站规则
        for rule in policy.egress_rules:
            self._validate_egress_rule(rule, validation_result)
        
        # 验证策略冲突
        self._validate_policy_conflicts(policy, validation_result)
        
        # 生成建议
        self._generate_recommendations(policy, validation_result)
        
        validation_result['valid'] = len(validation_result['errors']) == 0
        return validation_result
    
    def _validate_basic_fields(self, policy: NetworkPolicy, result: Dict[str, Any]):
        """验证基本字段"""
        if not policy.name:
            result['errors'].append("策略名称不能为空")
        
        if not policy.namespace:
            result['errors'].append("命名空间不能为空")
        
        if not policy.pod_selector:
            result['warnings'].append("Pod选择器为空，将影响所有Pod")
        
        if not policy.policy_types:
            result['errors'].append("策略类型不能为空")
    
    def _validate_selector(self, selector: Dict[str, str], result: Dict[str, Any]):
        """验证选择器"""
        if not isinstance(selector, dict):
            result['errors'].append("选择器必须是字典类型")
            return
        
        for key, value in selector.items():
            if not key or not isinstance(key, str):
                result['errors'].append(f"无效的选择器键: {key}")
            
            if not isinstance(value, str):
                result['errors'].append(f"无效的选择器值: {value}")
    
    def _validate_ingress_rule(self, rule: IngressRule, result: Dict[str, Any]):
        """验证入站规则"""
        if not rule.from_sources and not rule.ports:
            result['warnings'].append("入站规则没有指定来源或端口")
        
        # 验证来源
        for source in rule.from_sources:
            if 'ipBlock' in source:
                self._validate_ip_block(source['ipBlock'], result)
        
        # 验证端口
        for port in rule.ports:
            self._validate_port(port, result)
    
    def _validate_egress_rule(self, rule: EgressRule, result: Dict[str, Any]):
        """验证出站规则"""
        if not rule.to_destinations and not rule.ports:
            result['warnings'].append("出站规则没有指定目标或端口")
        
        # 验证目标
        for dest in rule.to_destinations:
            if 'ipBlock' in dest:
                self._validate_ip_block(dest['ipBlock'], result)
        
        # 验证端口
        for port in rule.ports:
            self._validate_port(port, result)
    
    def _validate_ip_block(self, ip_block: Dict[str, Any], result: Dict[str, Any]):
        """验证IP块"""
        if 'cidr' not in ip_block:
            result['errors'].append("IP块必须包含CIDR")
            return
        
        try:
            network = ip_network(ip_block['cidr'])
            
            # 验证except
            if 'except' in ip_block:
                for except_cidr in ip_block['except']:
                    try:
                        except_network = ip_network(except_cidr)
                        if not except_network.subnet_of(network):
                            result['errors'].append(f"例外CIDR {except_cidr} 不在主CIDR {ip_block['cidr']} 内")
                    except ValueError:
                        result['errors'].append(f"无效的例外CIDR: {except_cidr}")
        
        except ValueError:
            result['errors'].append(f"无效的CIDR: {ip_block['cidr']}")
    
    def _validate_port(self, port: Dict[str, Any], result: Dict[str, Any]):
        """验证端口"""
        if 'port' in port:
            port_value = port['port']
            if isinstance(port_value, int):
                if port_value < 1 or port_value > 65535:
                    result['errors'].append(f"无效的端口号: {port_value}")
            elif isinstance(port_value, str):
                if not port_value:
                    result['errors'].append("端口名称不能为空")
        
        if 'endPort' in port:
            end_port = port['endPort']
            if not isinstance(end_port, int) or end_port < 1 or end_port > 65535:
                result['errors'].append(f"无效的结束端口: {end_port}")
            
            if 'port' in port and isinstance(port['port'], int):
                if end_port < port['port']:
                    result['errors'].append("结束端口不能小于起始端口")
        
        if 'protocol' in port:
            protocol = port['protocol']
            if protocol not in ['TCP', 'UDP', 'SCTP']:
                result['errors'].append(f"无效的协议: {protocol}")
    
    def _validate_policy_conflicts(self, policy: NetworkPolicy, result: Dict[str, Any]):
        """验证策略冲突"""
        policies = self.policy_manager.list_policies(policy.namespace)
        
        for other_policy in policies:
            if other_policy.policy_id == policy.policy_id:
                continue
            
            # 检查选择器冲突
            if self._selectors_conflict(policy.pod_selector, other_policy.pod_selector):
                result['warnings'].append(f"策略可能与 {other_policy.name} 存在选择器冲突")
    
    def _selectors_conflict(self, selector1: Dict[str, str], selector2: Dict[str, str]) -> bool:
        """检查选择器冲突"""
        # 简化的冲突检测
        if not selector1 or not selector2:
            return False
        
        for key, value in selector1.items():
            if key in selector2 and selector2[key] != value:
                return False
        
        return True
    
    def _generate_recommendations(self, policy: NetworkPolicy, result: Dict[str, Any]):
        """生成建议"""
        recommendations = []
        
        # 安全建议
        if not policy.ingress_rules:
            recommendations.append("建议添加入站规则以控制进入Pod的流量")
        
        if not policy.egress_rules:
            recommendations.append("建议添加出站规则以控制Pod发出的流量")
        
        # 性能建议
        if len(policy.ingress_rules) > 50:
            recommendations.append("入站规则较多，建议考虑合并或简化规则")
        
        if len(policy.egress_rules) > 50:
            recommendations.append("出站规则较多，建议考虑合并或简化规则")
        
        # 最佳实践建议
        if policy.pod_selector:
            if 'app' not in policy.pod_selector:
                recommendations.append("建议在Pod选择器中包含app标签")
        
        result['recommendations'] = recommendations

class NetworkPolicyGenerator:
    """网络策略生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载模板"""
        return {
            'default_deny': '''
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: {{ namespace }}
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
            ''',
            'allow_same_namespace': '''
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
  namespace: {{ namespace }}
spec:
  podSelector:
    matchLabels:
      {{ pod_selector | to_nice_yaml | indent(6) }}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: {{ namespace }}
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: {{ namespace }}
            ''',
            'allow_specific_ports': '''
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-specific-ports
  namespace: {{ namespace }}
spec:
  podSelector:
    matchLabels:
      {{ pod_selector | to_nice_yaml | indent(6) }}
  policyTypes:
  - Ingress
  ingress:
  - from: []
    ports:
    {% for port in ports %}
    - port: {{ port }}
      protocol: TCP
    {% endfor %}
            '''
        }
    
    def generate_policy(self, template_name: str, **kwargs) -> str:
        """生成策略"""
        try:
            template = self.templates.get(template_name)
            if not template:
                raise ValueError(f"模板不存在: {template_name}")
            
            jinja_template = jinja2.Template(template)
            return jinja_template.render(**kwargs)
        
        except Exception as e:
            self.logger.error(f"生成策略失败: {e}")
            raise
    
    def generate_default_deny_policy(self, namespace: str) -> str:
        """生成默认拒绝策略"""
        return self.generate_policy('default_deny', namespace=namespace)
    
    def generate_allow_same_namespace_policy(self, namespace: str, pod_selector: Dict[str, str]) -> str:
        """生成允许同命名空间通信策略"""
        return self.generate_policy(
            'allow_same_namespace',
            namespace=namespace,
            pod_selector=pod_selector
        )
    
    def generate_allow_specific_ports_policy(self, namespace: str, pod_selector: Dict[str, str], ports: List[int]) -> str:
        """生成允许特定端口策略"""
        return self.generate_policy(
            'allow_specific_ports',
            namespace=namespace,
            pod_selector=pod_selector,
            ports=ports
        )

class NetworkPolicyOrchestrator:
    """网络策略编排器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.policy_manager = NetworkPolicyManager()
        self.traffic_analyzer = TrafficAnalyzer(self.policy_manager)
        self.policy_validator = PolicyValidator(self.policy_manager)
        self.policy_generator = NetworkPolicyGenerator()
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def create_isolation_policy(self, namespace: str, pod_selector: Dict[str, str]) -> NetworkPolicy:
        """创建隔离策略"""
        try:
            policy = NetworkPolicy(
                policy_id=str(uuid.uuid4()),
                name=f"isolation-{namespace}",
                namespace=namespace,
                pod_selector=pod_selector,
                policy_types=[PolicyType.INGRESS, PolicyType.EGRESS],
                ingress_action=PolicyAction.DENY,
                egress_action=PolicyAction.DENY
            )
            
            # 验证策略
            validation_result = self.policy_validator.validate_policy(policy)
            if not validation_result['valid']:
                self.logger.error(f"策略验证失败: {validation_result['errors']}")
                raise ValueError("策略验证失败")
            
            # 创建策略
            if self.policy_manager.create_policy(policy):
                self.logger.info(f"隔离策略创建成功: {policy.name}")
                return policy
            else:
                raise RuntimeError("策略创建失败")
        
        except Exception as e:
            self.logger.error(f"创建隔离策略失败: {e}")
            raise
    
    def create_communication_policy(self, namespace: str, source_selector: Dict[str, str], 
                                  dest_selector: Dict[str, str], ports: List[int]) -> NetworkPolicy:
        """创建通信策略"""
        try:
            # 创建入站规则
            ingress_rule = IngressRule(
                rule_id=str(uuid.uuid4()),
                from_sources=[{'podSelector': source_selector}],
                ports=[{'port': port, 'protocol': 'TCP'} for port in ports],
                action=PolicyAction.ALLOW
            )
            
            # 创建出站规则
            egress_rule = EgressRule(
                rule_id=str(uuid.uuid4()),
                to_destinations=[{'podSelector': dest_selector}],
                ports=[{'port': port, 'protocol': 'TCP'} for port in ports],
                action=PolicyAction.ALLOW
            )
            
            policy = NetworkPolicy(
                policy_id=str(uuid.uuid4()),
                name=f"communication-{namespace}",
                namespace=namespace,
                pod_selector=dest_selector,
                policy_types=[PolicyType.INGRESS, PolicyType.EGRESS],
                ingress_rules=[ingress_rule],
                egress_rules=[egress_rule]
            )
            
            # 验证策略
            validation_result = self.policy_validator.validate_policy(policy)
            if not validation_result['valid']:
                self.logger.error(f"策略验证失败: {validation_result['errors']}")
                raise ValueError("策略验证失败")
            
            # 创建策略
            if self.policy_manager.create_policy(policy):
                self.logger.info(f"通信策略创建成功: {policy.name}")
                return policy
            else:
                raise RuntimeError("策略创建失败")
        
        except Exception as e:
            self.logger.error(f"创建通信策略失败: {e}")
            raise
    
    def analyze_network_security(self, namespace: str = None) -> Dict[str, Any]:
        """分析网络安全"""
        try:
            # 获取策略
            policies = self.policy_manager.list_policies(namespace)
            
            # 获取流量统计
            traffic_stats = self.traffic_analyzer.get_traffic_statistics()
            
            # 获取流量最大的通信
            top_talkers = self.traffic_analyzer.get_top_talkers()
            
            # 分析策略覆盖率
            coverage_analysis = self._analyze_policy_coverage(policies)
            
            # 分析安全风险
            security_risks = self._analyze_security_risks(policies)
            
            return {
                'namespace': namespace,
                'policy_count': len(policies),
                'traffic_statistics': traffic_stats,
                'top_talkers': top_talkers,
                'coverage_analysis': coverage_analysis,
                'security_risks': security_risks,
                'recommendations': self._generate_security_recommendations(policies, security_risks)
            }
        
        except Exception as e:
            self.logger.error(f"分析网络安全失败: {e}")
            raise
    
    def _analyze_policy_coverage(self, policies: List[NetworkPolicy]) -> Dict[str, Any]:
        """分析策略覆盖率"""
        coverage = {
            'namespaces_with_policies': set(),
            'pods_covered': 0,
            'total_pods': 0,
            'coverage_percentage': 0.0
        }
        
        for policy in policies:
            coverage['namespaces_with_policies'].add(policy.namespace)
        
        # 简化的覆盖率计算
        coverage['coverage_percentage'] = len(coverage['namespaces_with_policies']) * 10.0  # 假设值
        
        return coverage
    
    def _analyze_security_risks(self, policies: List[NetworkPolicy]) -> List[Dict[str, Any]]:
        """分析安全风险"""
        risks = []
        
        for policy in policies:
            # 检查默认允许风险
            if not policy.ingress_rules and PolicyType.INGRESS in policy.policy_types:
                risks.append({
                    'type': 'default_allow_ingress',
                    'policy': policy.name,
                    'namespace': policy.namespace,
                    'severity': 'high',
                    'description': '策略允许所有入站流量'
                })
            
            if not policy.egress_rules and PolicyType.EGRESS in policy.policy_types:
                risks.append({
                    'type': 'default_allow_egress',
                    'policy': policy.name,
                    'namespace': policy.namespace,
                    'severity': 'medium',
                    'description': '策略允许所有出站流量'
                })
        
        return risks
    
    def _generate_security_recommendations(self, policies: List[NetworkPolicy], risks: List[Dict[str, Any]]) -> List[str]:
        """生成安全建议"""
        recommendations = []
        
        if not policies:
            recommendations.append("建议为命名空间创建网络策略")
            return recommendations
        
        # 基于风险生成建议
        high_risks = [risk for risk in risks if risk['severity'] == 'high']
        if high_risks:
            recommendations.append("发现高风险配置，建议立即检查和修复")
        
        # 基于策略数量生成建议
        if len(policies) < 5:
            recommendations.append("建议增加网络策略以提高安全性")
        
        return recommendations

# 使用示例
# 创建编排器
orchestrator = NetworkPolicyOrchestrator()

# 创建隔离策略
isolation_policy = orchestrator.create_isolation_policy(
    namespace="production",
    pod_selector={"app": "database"}
)

# 创建通信策略
communication_policy = orchestrator.create_communication_policy(
    namespace="production",
    source_selector={"app": "frontend"},
    dest_selector={"app": "backend"},
    ports=[8080, 8443]
)

# 模拟流量
flow = TrafficFlow(
    flow_id=str(uuid.uuid4()),
    source_ip="10.1.1.10",
    source_port=12345,
    dest_ip="10.1.1.20",
    dest_port=8080,
    protocol=Protocol.TCP,
    timestamp=datetime.now(),
    action="unknown"
)

orchestrator.traffic_analyzer.record_traffic(flow)

# 分析网络安全
security_analysis = orchestrator.analyze_network_security("production")
print(f"网络安全分析: {security_analysis}")
```

## 参考资源

### Kubernetes网络策略文档
- [Kubernetes网络策略官方文档](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [网络策略入门指南](https://kubernetes.io/docs/tasks/administer-cluster/declare-network-policy/)
- [网络策略故障排除](https://kubernetes.io/docs/tasks/administer-cluster/debug-network-policy/)
- [网络策略最佳实践](https://kubernetes.io/docs/concepts/cluster-administration/network-policy/)

### 网络插件
- [Calico网络策略](https://docs.projectcalico.org/getting-started/kubernetes/)
- [Cilium网络策略](https://cilium.readthedocs.io/en/stable/intro/)
- [Flannel网络配置](https://github.com/flannel-io/flannel)
- [Weave Net网络策略](https://www.weave.works/docs/net/latest/kubernetes/kubernetes-np/)

### 安全工具
- [Falco运行时安全](https://falco.org/)
- [OPA/Gatekeeper策略引擎](https://openpolicyagent.org/)
- [Kyverno策略引擎](https://kyverno.io/)
- [NeuVector容器安全](https://neuvector.com/)

### 监控和日志
- [Prometheus网络监控](https://prometheus.io/)
- [Grafana网络可视化](https://grafana.com/)
- [ELK网络日志分析](https://www.elastic.co/)
- [Fluentd日志收集](https://www.fluentd.org/)

### 实践指南
- [Kubernetes网络策略实战](https://kubernetes.io/blog/2019/07/18/kubernetes-network-policies/)
- [微服务网络隔离](https://kubernetes.io/blog/2018/05/24/kubernetes-network-isolation/)
- [多租户网络策略](https://kubernetes.io/blog/2021/05/19/multi-tenant-network-policies/)
- [网络策略性能优化](https://kubernetes.io/blog/2020/04/21/kubernetes-network-policies-performance/)
