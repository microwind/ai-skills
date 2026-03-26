# Kubernetes验证器参考文档

## Kubernetes验证器概述

### 什么是Kubernetes验证器
Kubernetes验证器是一个专业的Kubernetes集群配置验证和合规性检查工具，用于自动化检测Kubernetes资源配置、安全策略、网络策略、存储策略等方面的合规性和安全性问题。该工具支持多种验证标准（如CIS基准、NSA指南等），提供实时验证、批量验证、定时验证等多种模式，帮助云原生团队确保Kubernetes集群的安全性和合规性。

### 主要功能
- **资源验证**: 检查Pods、Services、Deployments等Kubernetes资源的配置正确性
- **安全验证**: 验证RBAC权限、网络策略、Pod安全策略等安全配置
- **存储验证**: 检查PVC、存储类等存储配置的合规性和性能
- **网络验证**: 验证Ingress、网络策略等网络配置的安全性
- **合规检查**: 支持CIS基准、NSA指南等多种合规标准的检查
- **自动修复**: 提供自动修复功能和修复建议
- **多集群支持**: 支持多集群的统一管理和验证

## Kubernetes验证器核心

### 验证引擎
```python
# kubernetes_validator.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import re
import requests
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

class ValidationType(Enum):
    """验证类型枚举"""
    RESOURCE = "resource"
    SECURITY = "security"
    NETWORK = "network"
    STORAGE = "storage"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class Severity(Enum):
    """严重性枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    """合规标准枚举"""
    CIS = "cis"
    NSA = "nsa"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    NIST = "nist"
    CUSTOM = "custom"

@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    rule_name: str
    rule_type: ValidationType
    severity: Severity
    description: str
    category: str
    standard: Optional[ComplianceStandard] = None
    control_id: Optional[str] = None
    evaluation: str = ""
    remediation: str = ""
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    custom_script: Optional[str] = None

@dataclass
class ValidationIssue:
    """验证问题"""
    issue_id: str
    rule_id: str
    resource_type: str
    resource_name: str
    namespace: str
    severity: Severity
    title: str
    description: str
    remediation: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationReport:
    """验证报告"""
    report_id: str
    cluster_name: str
    validation_type: ValidationType
    timestamp: datetime
    total_resources: int
    total_issues: int
    issues_by_severity: Dict[str, int]
    issues_by_category: Dict[str, int]
    compliance_score: float
    recommendations: List[str]
    issues: List[ValidationIssue] = field(default_factory=list)

@dataclass
class ClusterConfig:
    """集群配置"""
    cluster_id: str
    cluster_name: str
    cluster_type: str
    kubeconfig_path: str
    context: str
    namespaces: List[str]
    labels: Dict[str, str] = field(default_factory=dict)
    environment: str = "development"

class KubernetesClient:
    """Kubernetes客户端"""
    
    def __init__(self, kubeconfig_path: str = None, context: str = None):
        self.logger = logging.getLogger(__name__)
        
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path, context=context)
            else:
                config.load_incluster_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            self.rbac_v1 = client.RbacAuthorizationV1Api()
            self.storage_v1 = client.StorageV1Api()
            self.policy_v1 = client.PolicyV1Api()
            
            self.logger.info("Kubernetes客户端初始化成功")
        
        except Exception as e:
            self.logger.error(f"Kubernetes客户端初始化失败: {e}")
            raise
    
    def get_namespaces(self, label_selector: str = None) -> List[str]:
        """获取命名空间列表"""
        try:
            namespaces = self.v1.list_namespace(label_selector=label_selector)
            return [ns.metadata.name for ns in namespaces.items]
        except Exception as e:
            self.logger.error(f"获取命名空间失败: {e}")
            return []
    
    def get_pods(self, namespace: str = None, label_selector: str = None) -> List[Dict[str, Any]]:
        """获取Pod列表"""
        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
            return [self._serialize_pod(pod) for pod in pods.items]
        except Exception as e:
            self.logger.error(f"获取Pod失败: {e}")
            return []
    
    def get_services(self, namespace: str = None, label_selector: str = None) -> List[Dict[str, Any]]:
        """获取Service列表"""
        try:
            services = self.v1.list_namespaced_service(namespace=namespace, label_selector=label_selector)
            return [self._serialize_service(service) for service in services.items]
        except Exception as e:
            self.logger.error(f"获取Service失败: {e}")
            return []
    
    def get_deployments(self, namespace: str = None, label_selector: str = None) -> List[Dict[str, Any]]:
        """获取Deployment列表"""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace, label_selector=label_selector)
            return [self._serialize_deployment(deployment) for deployment in deployments.items]
        except Exception as e:
            self.logger.error(f"获取Deployment失败: {e}")
            return []
    
    def get_network_policies(self, namespace: str = None, label_selector: str = None) -> List[Dict[str, Any]]:
        """获取NetworkPolicy列表"""
        try:
            policies = self.networking_v1.list_namespaced_network_policy(namespace=namespace, label_selector=label_selector)
            return [self._serialize_network_policy(policy) for policy in policies.items]
        except Exception as e:
            self.logger.error(f"获取NetworkPolicy失败: {e}")
            return []
    
    def get_pvcs(self, namespace: str = None, label_selector: str = None) -> List[Dict[str, Any]]:
        """获取PVC列表"""
        try:
            pvcs = self.v1.list_namespaced_persistent_volume_claim(namespace=namespace, label_selector=label_selector)
            return [self._serialize_pvc(pvc) for pvc in pvcs.items]
        except Exception as e:
            self.logger.error(f"获取PVC失败: {e}")
            return []
    
    def _serialize_pod(self, pod) -> Dict[str, Any]:
        """序列化Pod对象"""
        return {
            'name': pod.metadata.name,
            'namespace': pod.metadata.namespace,
            'labels': pod.metadata.labels or {},
            'annotations': pod.metadata.annotations or {},
            'spec': {
                'containers': [
                    {
                        'name': container.name,
                        'image': container.image,
                        'resources': container.resources or {},
                        'security_context': container.security_context or {},
                        'ports': container.ports or []
                    } for container in pod.spec.containers
                ],
                'security_context': pod.spec.security_context or {},
                'volumes': pod.spec.volumes or [],
                'restart_policy': pod.spec.restart_policy
            },
            'status': {
                'phase': pod.status.phase,
                'pod_ip': pod.status.pod_ip,
                'host_ip': pod.status.host_ip
            }
        }
    
    def _serialize_service(self, service) -> Dict[str, Any]:
        """序列化Service对象"""
        return {
            'name': service.metadata.name,
            'namespace': service.metadata.namespace,
            'labels': service.metadata.labels or {},
            'annotations': service.metadata.annotations or {},
            'spec': {
                'type': service.spec.type,
                'cluster_ip': service.spec.cluster_ip,
                'external_ips': service.spec.external_ips or [],
                'ports': service.spec.ports or [],
                'selector': service.spec.selector or {},
                'session_affinity': service.spec.session_affinity
            }
        }
    
    def _serialize_deployment(self, deployment) -> Dict[str, Any]:
        """序列化Deployment对象"""
        return {
            'name': deployment.metadata.name,
            'namespace': deployment.metadata.namespace,
            'labels': deployment.metadata.labels or {},
            'annotations': deployment.metadata.annotations or {},
            'spec': {
                'replicas': deployment.spec.replicas,
                'selector': deployment.spec.selector or {},
                'strategy': deployment.spec.strategy or {},
                'template': {
                    'metadata': deployment.spec.template.metadata or {},
                    'spec': {
                        'containers': [
                            {
                                'name': container.name,
                                'image': container.image,
                                'resources': container.resources or {},
                                'security_context': container.security_context or {}
                            } for container in deployment.spec.template.spec.containers
                        ],
                        'security_context': deployment.spec.template.spec.security_context or {}
                    }
                }
            }
        }
    
    def _serialize_network_policy(self, policy) -> Dict[str, Any]:
        """序列化NetworkPolicy对象"""
        return {
            'name': policy.metadata.name,
            'namespace': policy.metadata.namespace,
            'labels': policy.metadata.labels or {},
            'annotations': policy.metadata.annotations or {},
            'spec': {
                'pod_selector': policy.spec.pod_selector or {},
                'policy_types': policy.spec.policy_types or [],
                'ingress': policy.spec.ingress or [],
                'egress': policy.spec.egress or []
            }
        }
    
    def _serialize_pvc(self, pvc) -> Dict[str, Any]:
        """序列化PVC对象"""
        return {
            'name': pvc.metadata.name,
            'namespace': pvc.metadata.namespace,
            'labels': pvc.metadata.labels or {},
            'annotations': pvc.metadata.annotations or {},
            'spec': {
                'access_modes': pvc.spec.access_modes or [],
                'resources': pvc.spec.resources or {},
                'storage_class_name': pvc.spec.storage_class_name,
                'volume_name': pvc.spec.volume_name
            },
            'status': {
                'phase': pvc.status.phase,
                'capacity': pvc.status.capacity or {}
            }
        }

class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = {}
        self.custom_functions = {}
        self._load_builtin_rules()
    
    def _load_builtin_rules(self):
        """加载内置规则"""
        # Pod安全规则
        self.add_rule(ValidationRule(
            rule_id="pod_security_context",
            rule_name="Pod安全上下文检查",
            rule_type=ValidationType.SECURITY,
            severity=Severity.HIGH,
            description="检查Pod是否配置了安全上下文",
            category="Pod安全",
            standard=ComplianceStandard.CIS,
            control_id="5.7.3",
            evaluation="pod.spec.security_context must be defined",
            remediation="为Pod配置安全上下文，包括runAsNonRoot、readOnlyRootFilesystem等"
        ))
        
        self.add_rule(ValidationRule(
            rule_id="container_privileged",
            rule_name="特权容器检查",
            rule_type=ValidationType.SECURITY,
            severity=Severity.CRITICAL,
            description="检查容器是否以特权模式运行",
            category="容器安全",
            standard=ComplianceStandard.CIS,
            control_id="5.2.2",
            evaluation="container.security_context.privileged must be false or undefined",
            remediation="移除容器的特权配置，使用最小权限原则"
        ))
        
        self.add_rule(ValidationRule(
            rule_id="container_run_as_root",
            rule_name="Root用户运行检查",
            rule_type=ValidationType.SECURITY,
            severity=Severity.HIGH,
            description="检查容器是否以root用户运行",
            category="容器安全",
            standard=ComplianceStandard.CIS,
            control_id="5.2.6",
            evaluation="container.security_context.runAsUser must not be 0",
            remediation="配置容器以非root用户运行"
        ))
        
        # 资源配置规则
        self.add_rule(ValidationRule(
            rule_id="pod_resource_limits",
            rule_name="Pod资源限制检查",
            rule_type=ValidationType.RESOURCE,
            severity=Severity.MEDIUM,
            description="检查Pod是否配置了资源限制",
            category="资源配置",
            evaluation="container.resources.limits must be defined for cpu and memory",
            remediation="为容器配置CPU和内存限制"
        ))
        
        self.add_rule(ValidationRule(
            rule_id="pod_resource_requests",
            rule_name="Pod资源请求检查",
            rule_type=ValidationType.RESOURCE,
            severity=Severity.MEDIUM,
            description="检查Pod是否配置了资源请求",
            category="资源配置",
            evaluation="container.resources.requests must be defined for cpu and memory",
            remediation="为容器配置CPU和内存请求"
        ))
        
        # 网络安全规则
        self.add_rule(ValidationRule(
            rule_id="service_external_ip",
            rule_name="Service外部IP检查",
            rule_type=ValidationType.NETWORK,
            severity=Severity.MEDIUM,
            description="检查Service是否配置了外部IP",
            category="网络安全",
            evaluation="service.spec.externalIPs should be empty",
            remediation="移除Service的外部IP配置，使用LoadBalancer或NodePort"
        ))
        
        self.add_rule(ValidationRule(
            rule_id="network_policy_default",
            rule_name="默认网络策略检查",
            rule_type=ValidationType.NETWORK,
            severity=Severity.HIGH,
            description="检查命名空间是否配置了默认网络策略",
            category="网络安全",
            evaluation="每个命名空间应该有默认拒绝的网络策略",
            remediation="为每个命名空间配置默认拒绝的网络策略"
        ))
    
    def add_rule(self, rule: ValidationRule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
        self.logger.info(f"添加规则: {rule.rule_name}")
    
    def remove_rule(self, rule_id: str):
        """移除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self.logger.info(f"移除规则: {rule_id}")
    
    def get_rules(self, rule_type: ValidationType = None, severity: Severity = None, 
                  standard: ComplianceStandard = None) -> List[ValidationRule]:
        """获取规则列表"""
        rules = list(self.rules.values())
        
        if rule_type:
            rules = [rule for rule in rules if rule.rule_type == rule_type]
        
        if severity:
            rules = [rule for rule in rules if rule.severity == severity]
        
        if standard:
            rules = [rule for rule in rules if rule.standard == standard]
        
        return rules
    
    def evaluate_rule(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """评估规则"""
        try:
            if rule.custom_script:
                return self._evaluate_custom_rule(rule, resource)
            else:
                return self._evaluate_builtin_rule(rule, resource)
        except Exception as e:
            self.logger.error(f"评估规则失败 {rule.rule_id}: {e}")
            return None
    
    def _evaluate_builtin_rule(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """评估内置规则"""
        if rule.rule_id == "pod_security_context":
            return self._check_pod_security_context(rule, resource)
        elif rule.rule_id == "container_privileged":
            return self._check_container_privileged(rule, resource)
        elif rule.rule_id == "container_run_as_root":
            return self._check_container_run_as_root(rule, resource)
        elif rule.rule_id == "pod_resource_limits":
            return self._check_pod_resource_limits(rule, resource)
        elif rule.rule_id == "pod_resource_requests":
            return self._check_pod_resource_requests(rule, resource)
        elif rule.rule_id == "service_external_ip":
            return self._check_service_external_ip(rule, resource)
        elif rule.rule_id == "network_policy_default":
            return self._check_network_policy_default(rule, resource)
        
        return None
    
    def _check_pod_security_context(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查Pod安全上下文"""
        if resource.get('resource_type') != 'Pod':
            return None
        
        pod_spec = resource.get('spec', {})
        security_context = pod_spec.get('security_context', {})
        
        if not security_context:
            return ValidationIssue(
                issue_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                resource_type=resource.get('resource_type'),
                resource_name=resource.get('name'),
                namespace=resource.get('namespace'),
                severity=rule.severity,
                title=rule.rule_name,
                description="Pod未配置安全上下文",
                remediation=rule.remediation,
                evidence={'security_context': security_context}
            )
        
        return None
    
    def _check_container_privileged(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查特权容器"""
        if resource.get('resource_type') != 'Pod':
            return None
        
        containers = resource.get('spec', {}).get('containers', [])
        
        for container in containers:
            security_context = container.get('security_context', {})
            if security_context.get('privileged', False):
                return ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    resource_type=resource.get('resource_type'),
                    resource_name=resource.get('name'),
                    namespace=resource.get('namespace'),
                    severity=rule.severity,
                    title=rule.rule_name,
                    description=f"容器 {container.get('name')} 以特权模式运行",
                    remediation=rule.remediation,
                    evidence={
                        'container_name': container.get('name'),
                        'security_context': security_context
                    }
                )
        
        return None
    
    def _check_container_run_as_root(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查root用户运行"""
        if resource.get('resource_type') != 'Pod':
            return None
        
        containers = resource.get('spec', {}).get('containers', [])
        
        for container in containers:
            security_context = container.get('security_context', {})
            run_as_user = security_context.get('runAsUser')
            
            if run_as_user == 0:
                return ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    resource_type=resource.get('resource_type'),
                    resource_name=resource.get('name'),
                    namespace=resource.get('namespace'),
                    severity=rule.severity,
                    title=rule.rule_name,
                    description=f"容器 {container.get('name')} 以root用户运行",
                    remediation=rule.remediation,
                    evidence={
                        'container_name': container.get('name'),
                        'security_context': security_context
                    }
                )
        
        return None
    
    def _check_pod_resource_limits(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查Pod资源限制"""
        if resource.get('resource_type') != 'Pod':
            return None
        
        containers = resource.get('spec', {}).get('containers', [])
        
        for container in containers:
            resources = container.get('resources', {})
            limits = resources.get('limits', {})
            
            if not limits.get('cpu') or not limits.get('memory'):
                return ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    resource_type=resource.get('resource_type'),
                    resource_name=resource.get('name'),
                    namespace=resource.get('namespace'),
                    severity=rule.severity,
                    title=rule.rule_name,
                    description=f"容器 {container.get('name')} 未配置资源限制",
                    remediation=rule.remediation,
                    evidence={
                        'container_name': container.get('name'),
                        'resources': resources
                    }
                )
        
        return None
    
    def _check_pod_resource_requests(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查Pod资源请求"""
        if resource.get('resource_type') != 'Pod':
            return None
        
        containers = resource.get('spec', {}).get('containers', [])
        
        for container in containers:
            resources = container.get('resources', {})
            requests = resources.get('requests', {})
            
            if not requests.get('cpu') or not requests.get('memory'):
                return ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    resource_type=resource.get('resource_type'),
                    resource_name=resource.get('name'),
                    namespace=resource.get('namespace'),
                    severity=rule.severity,
                    title=rule.rule_name,
                    description=f"容器 {container.get('name')} 未配置资源请求",
                    remediation=rule.remediation,
                    evidence={
                        'container_name': container.get('name'),
                        'resources': resources
                    }
                )
        
        return None
    
    def _check_service_external_ip(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查Service外部IP"""
        if resource.get('resource_type') != 'Service':
            return None
        
        service_spec = resource.get('spec', {})
        external_ips = service_spec.get('external_ips', [])
        
        if external_ips:
            return ValidationIssue(
                issue_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                resource_type=resource.get('resource_type'),
                resource_name=resource.get('name'),
                namespace=resource.get('namespace'),
                severity=rule.severity,
                title=rule.rule_name,
                description=f"Service配置了外部IP: {external_ips}",
                remediation=rule.remediation,
                evidence={'external_ips': external_ips}
            )
        
        return None
    
    def _check_network_policy_default(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """检查默认网络策略"""
        if resource.get('resource_type') != 'NetworkPolicy':
            return None
        
        # 这个检查需要全局视角，这里简化处理
        return None
    
    def _evaluate_custom_rule(self, rule: ValidationRule, resource: Dict[str, Any]) -> Optional[ValidationIssue]:
        """评估自定义规则"""
        try:
            # 创建安全的执行环境
            safe_globals = {
                '__builtins__': {},
                'resource': resource,
                'len': len,
                'str': str,
                'int': int,
                'bool': bool,
                'dict': dict,
                'list': list,
                'get': dict.get,
                'in': lambda x, y: x in y,
                'not': lambda x: not x,
                'and': lambda x, y: x and y,
                'or': lambda x, y: x or y,
                're': re
            }
            
            # 执行自定义脚本
            result = eval(rule.custom_script, safe_globals)
            
            if not result:
                return ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    resource_type=resource.get('resource_type'),
                    resource_name=resource.get('name'),
                    namespace=resource.get('namespace'),
                    severity=rule.severity,
                    title=rule.rule_name,
                    description=rule.description,
                    remediation=rule.remediation,
                    evidence={'evaluation': rule.evaluation}
                )
        
        except Exception as e:
            self.logger.error(f"执行自定义规则失败 {rule.rule_id}: {e}")
        
        return None

class ValidationEngine:
    """验证引擎"""
    
    def __init__(self, k8s_client: KubernetesClient, rule_engine: RuleEngine):
        self.k8s_client = k8s_client
        self.rule_engine = rule_engine
        self.logger = logging.getLogger(__name__)
    
    def validate_cluster(self, cluster_config: ClusterConfig, validation_type: ValidationType = None) -> ValidationReport:
        """验证集群"""
        self.logger.info(f"开始验证集群: {cluster_config.cluster_name}")
        
        # 获取资源
        resources = self._collect_resources(cluster_config)
        
        # 获取规则
        rules = self.rule_engine.get_rules(rule_type=validation_type)
        
        # 执行验证
        issues = []
        for resource in resources:
            for rule in rules:
                if rule.enabled:
                    issue = self.rule_engine.evaluate_rule(rule, resource)
                    if issue:
                        issues.append(issue)
        
        # 生成报告
        report = self._generate_report(cluster_config, validation_type, resources, issues)
        
        self.logger.info(f"集群验证完成: {cluster_config.cluster_name}, 发现 {len(issues)} 个问题")
        return report
    
    def _collect_resources(self, cluster_config: ClusterConfig) -> List[Dict[str, Any]]:
        """收集资源"""
        resources = []
        
        for namespace in cluster_config.namespaces:
            # 收集Pod
            pods = self.k8s_client.get_pods(namespace, cluster_config.labels)
            for pod in pods:
                pod['resource_type'] = 'Pod'
                resources.append(pod)
            
            # 收集Service
            services = self.k8s_client.get_services(namespace, cluster_config.labels)
            for service in services:
                service['resource_type'] = 'Service'
                resources.append(service)
            
            # 收集Deployment
            deployments = self.k8s_client.get_deployments(namespace, cluster_config.labels)
            for deployment in deployments:
                deployment['resource_type'] = 'Deployment'
                resources.append(deployment)
            
            # 收集NetworkPolicy
            network_policies = self.k8s_client.get_network_policies(namespace, cluster_config.labels)
            for policy in network_policies:
                policy['resource_type'] = 'NetworkPolicy'
                resources.append(policy)
            
            # 收集PVC
            pvcs = self.k8s_client.get_pvcs(namespace, cluster_config.labels)
            for pvc in pvcs:
                pvc['resource_type'] = 'PVC'
                resources.append(pvc)
        
        return resources
    
    def _generate_report(self, cluster_config: ClusterConfig, validation_type: ValidationType, 
                        resources: List[Dict[str, Any]], issues: List[ValidationIssue]) -> ValidationReport:
        """生成验证报告"""
        # 统计问题
        issues_by_severity = defaultdict(int)
        issues_by_category = defaultdict(int)
        
        for issue in issues:
            issues_by_severity[issue.severity.value] += 1
            issues_by_category[issue.rule_id] += 1
        
        # 计算合规分数
        total_rules = len(self.rule_engine.get_rules(validation_type))
        compliance_score = max(0, 100 - (len(issues) / max(total_rules, 1)) * 100)
        
        # 生成建议
        recommendations = self._generate_recommendations(issues)
        
        return ValidationReport(
            report_id=str(uuid.uuid4()),
            cluster_name=cluster_config.cluster_name,
            validation_type=validation_type or ValidationType.CUSTOM,
            timestamp=datetime.now(),
            total_resources=len(resources),
            total_issues=len(issues),
            issues_by_severity=dict(issues_by_severity),
            issues_by_category=dict(issues_by_category),
            compliance_score=compliance_score,
            recommendations=recommendations,
            issues=issues
        )
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 按严重性分组
        critical_issues = [issue for issue in issues if issue.severity == Severity.CRITICAL]
        high_issues = [issue for issue in issues if issue.severity == Severity.HIGH]
        
        if critical_issues:
            recommendations.append(f"发现 {len(critical_issues)} 个严重问题，建议立即修复")
        
        if high_issues:
            recommendations.append(f"发现 {len(high_issues)} 个高危问题，建议优先修复")
        
        # 按类别分组
        security_issues = [issue for issue in issues if 'security' in issue.rule_id or 'privileged' in issue.rule_id]
        resource_issues = [issue for issue in issues if 'resource' in issue.rule_id]
        network_issues = [issue for issue in issues if 'network' in issue.rule_id or 'service' in issue.rule_id]
        
        if security_issues:
            recommendations.append(f"发现 {len(security_issues)} 个安全问题，建议加强安全配置")
        
        if resource_issues:
            recommendations.append(f"发现 {len(resource_issues)} 个资源配置问题，建议优化资源配置")
        
        if network_issues:
            recommendations.append(f"发现 {len(network_issues)} 个网络配置问题，建议检查网络策略")
        
        return recommendations

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.template_env = jinja2.Environment(loader=jinja2.DictLoader({
            'html_report': '''
<!DOCTYPE html>
<html>
<head>
    <title>Kubernetes验证报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .issue { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .critical { border-left-color: #d32f2f; }
        .high { border-left-color: #f57c00; }
        .medium { border-left-color: #fbc02d; }
        .low { border-left-color: #388e3c; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ cluster_name }} - Kubernetes验证报告</h1>
        <p>生成时间: {{ timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        <p>验证类型: {{ validation_type.value }}</p>
        <p>合规分数: {{ "%.2f"|format(compliance_score) }}%</p>
    </div>
    
    <div class="summary">
        <h2>验证摘要</h2>
        <table>
            <tr><th>总资源数</th><td>{{ total_resources }}</td></tr>
            <tr><th>总问题数</th><td>{{ total_issues }}</td></tr>
            {% for severity, count in issues_by_severity.items() %}
            <tr><th>{{ severity }}问题</th><td>{{ count }}</td></tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="recommendations">
        <h2>修复建议</h2>
        <ul>
            {% for recommendation in recommendations %}
            <li>{{ recommendation }}</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="issues">
        <h2>详细问题</h2>
        {% for issue in issues %}
        <div class="issue {{ issue.severity.value }}">
            <h3>{{ issue.title }}</h3>
            <p><strong>严重性:</strong> {{ issue.severity.value }}</p>
            <p><strong>资源:</strong> {{ issue.resource_type }}/{{ issue.resource_name }} ({{ issue.namespace }})</p>
            <p><strong>描述:</strong> {{ issue.description }}</p>
            <p><strong>修复建议:</strong> {{ issue.remediation }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
            ''',
            'json_report': '''
{
    "report_id": "{{ report_id }}",
    "cluster_name": "{{ cluster_name }}",
    "validation_type": "{{ validation_type.value }}",
    "timestamp": "{{ timestamp.isoformat() }}",
    "summary": {
        "total_resources": {{ total_resources }},
        "total_issues": {{ total_issues }},
        "issues_by_severity": {{ issues_by_severity | tojson }},
        "issues_by_category": {{ issues_by_category | tojson }},
        "compliance_score": {{ compliance_score }}
    },
    "recommendations": {{ recommendations | tojson }},
    "issues": [
        {% for issue in issues %}
        {
            "issue_id": "{{ issue.issue_id }}",
            "rule_id": "{{ issue.rule_id }}",
            "resource_type": "{{ issue.resource_type }}",
            "resource_name": "{{ issue.resource_name }}",
            "namespace": "{{ issue.namespace }}",
            "severity": "{{ issue.severity.value }}",
            "title": "{{ issue.title }}",
            "description": "{{ issue.description }}",
            "remediation": "{{ issue.remediation }}",
            "timestamp": "{{ issue.timestamp.isoformat() }}"
        }{% if not loop.last %},{% endif %}
        {% endfor %}
    ]
}
            '''
        }))
    
    def generate_report(self, report: ValidationReport, format_type: str = 'html') -> str:
        """生成报告"""
        try:
            if format_type == 'html':
                template = self.template_env.get_template('html_report')
            elif format_type == 'json':
                template = self.template_env.get_template('json_report')
            else:
                raise ValueError(f"不支持的报告格式: {format_type}")
            
            return template.render(**asdict(report))
        
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            raise
    
    def save_report(self, report: ValidationReport, file_path: str, format_type: str = 'html'):
        """保存报告"""
        try:
            report_content = self.generate_report(report, format_type)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"报告已保存到: {file_path}")
        
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            raise

class KubernetesValidator:
    """Kubernetes验证器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.k8s_client = KubernetesClient(
            kubeconfig_path=config.get('kubeconfig_path'),
            context=config.get('context')
        )
        self.rule_engine = RuleEngine()
        self.validation_engine = ValidationEngine(self.k8s_client, self.rule_engine)
        self.report_generator = ReportGenerator()
        
        # 加载自定义规则
        if config.get('custom_rules'):
            self._load_custom_rules(config['custom_rules'])
    
    def _load_custom_rules(self, custom_rules: List[Dict[str, Any]]):
        """加载自定义规则"""
        for rule_data in custom_rules:
            rule = ValidationRule(
                rule_id=rule_data.get('rule_id'),
                rule_name=rule_data.get('rule_name'),
                rule_type=ValidationType(rule_data.get('rule_type')),
                severity=Severity(rule_data.get('severity')),
                description=rule_data.get('description'),
                category=rule_data.get('category'),
                evaluation=rule_data.get('evaluation'),
                remediation=rule_data.get('remediation'),
                custom_script=rule_data.get('custom_script')
            )
            self.rule_engine.add_rule(rule)
    
    def validate(self, cluster_name: str, namespaces: List[str] = None, 
                 validation_type: ValidationType = None, 
                 labels: Dict[str, str] = None) -> ValidationReport:
        """执行验证"""
        try:
            # 创建集群配置
            cluster_config = ClusterConfig(
                cluster_id=str(uuid.uuid4()),
                cluster_name=cluster_name,
                cluster_type="kubernetes",
                kubeconfig_path=self.config.get('kubeconfig_path'),
                context=self.config.get('context'),
                namespaces=namespaces or ['default'],
                labels=labels or {},
                environment=self.config.get('environment', 'development')
            )
            
            # 执行验证
            report = self.validation_engine.validate_cluster(cluster_config, validation_type)
            
            return report
        
        except Exception as e:
            self.logger.error(f"验证失败: {e}")
            raise
    
    def generate_and_save_report(self, report: ValidationReport, output_dir: str = '.', 
                                formats: List[str] = ['html', 'json']):
        """生成并保存报告"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for format_type in formats:
                file_name = f"k8s_validation_report_{report.cluster_name}_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.{format_type}"
                file_path = os.path.join(output_dir, file_name)
                
                self.report_generator.save_report(report, file_path, format_type)
            
            self.logger.info(f"报告已生成并保存到: {output_dir}")
        
        except Exception as e:
            self.logger.error(f"生成并保存报告失败: {e}")
            raise

# 使用示例
# 配置
config = {
    'kubeconfig_path': '~/.kube/config',
    'context': 'minikube',
    'environment': 'development',
    'custom_rules': [
        {
            'rule_id': 'custom_label_check',
            'rule_name': '自定义标签检查',
            'rule_type': 'custom',
            'severity': 'medium',
            'description': '检查资源是否包含必需的标签',
            'category': '标签管理',
            'evaluation': 'resource.get("labels", {}).get("environment") is not None',
            'remediation': '为资源添加environment标签'
        }
    ]
}

# 创建验证器
validator = KubernetesValidator(config)

# 执行验证
report = validator.validate(
    cluster_name='my-cluster',
    namespaces=['default', 'kube-system'],
    validation_type=ValidationType.SECURITY,
    labels={'app': 'my-app'}
)

# 输出结果
print(f"验证完成:")
print(f"- 集群: {report.cluster_name}")
print(f"- 总资源数: {report.total_resources}")
print(f"- 总问题数: {report.total_issues}")
print(f"- 合规分数: {report.compliance_score:.2f}%")

print(f"\n问题统计:")
for severity, count in report.issues_by_severity.items():
    print(f"- {severity}: {count}")

print(f"\n修复建议:")
for recommendation in report.recommendations:
    print(f"- {recommendation}")

# 生成并保存报告
validator.generate_and_save_report(report, output_dir='./reports', formats=['html', 'json'])
```

## 参考资源

### Kubernetes官方文档
- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Kubernetes安全最佳实践](https://kubernetes.io/docs/concepts/security/)
- [Pod安全标准](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [网络策略](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [RBAC授权](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

### 合规标准
- [CIS Kubernetes基准](https://www.cisecurity.org/benchmark/kubernetes)
- [NSA Kubernetes安全指南](https://www.nsa.gov/News-Features/Feature-Stories/Article-View/Article/2169668/nsacisa-technical-report-hardening-kubernetes/)
- [PCI-DSS合规](https://www.pcisecuritystandards.org/)
- [NIST网络安全框架](https://www.nist.gov/cyberframework)

### 安全工具
- [Falco运行时安全](https://falco.org/)
- [OPA/Gatekeeper策略引擎](https://openpolicyagent.org/)
- [Kyverno策略引擎](https://kyverno.io/)
- [Polaris安全验证](https://github.com/FairwindsOps/polaris)

### 验证工具
- [kube-score](https://github.com/zegl/kube-score)
- [kube-bench](https://github.com/aquasecurity/kube-bench)
- [kube-hunter](https://github.com/aquasecurity/kube-hunter)
- [Kubesec](https://kubesec.io/)

### 监控和日志
- [Prometheus监控](https://prometheus.io/)
- [Grafana可视化](https://grafana.com/)
- [ELK日志收集](https://www.elastic.co/)
- [Fluentd日志收集](https://www.fluentd.org/)
