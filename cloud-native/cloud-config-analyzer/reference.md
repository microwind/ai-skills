# 云配置分析器参考文档

## 云配置分析器概述

### 什么是云配置分析器
云配置分析器是一个专业的云原生配置管理和分析工具，用于分析、验证、优化Kubernetes、Docker、Terraform等云原生配置文件。该工具提供安全分析、资源分析、性能分析、成本分析、合规性检查等功能，帮助云原生团队确保配置的安全性、可靠性和成本效益。

### 主要功能
- **配置分析**: 支持YAML、JSON、TOML等多种配置文件格式的分析
- **安全检查**: 提供权限检查、密钥检查、网络策略检查等安全分析功能
- **资源优化**: 包含资源配置分析、资源利用率分析、资源优化建议
- **性能监控**: 提供实时性能分析、历史性能分析、性能趋势分析
- **成本分析**: 支持成本计算、成本优化、ROI分析等成本管理功能
- **合规性检查**: 包含CIS基准、NSA检查、PCI-DSS等标准合规性检查

## 云配置分析器核心

### 配置分析引擎
```python
# cloud_config_analyzer.py
import json
import yaml
import toml
import re
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import requests
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import statistics
import math
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class ConfigType(Enum):
    """配置类型枚举"""
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    TERRAFORM = "terraform"
    HELM = "helm"
    DOCKER_COMPOSE = "docker_compose"
    CUSTOM = "custom"

class AnalysisType(Enum):
    """分析类型枚举"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COST = "cost"
    COMPLIANCE = "compliance"
    RESOURCE = "resource"

class Severity(Enum):
    """严重性枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ConfigFile:
    """配置文件"""
    file_id: str
    file_path: str
    file_type: ConfigType
    content: str
    parsed_content: Dict[str, Any]
    size: int
    checksum: str
    last_modified: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisResult:
    """分析结果"""
    result_id: str
    config_file: ConfigFile
    analysis_type: AnalysisType
    severity: Severity
    message: str
    description: str
    recommendation: str
    location: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SecurityIssue:
    """安全问题"""
    issue_id: str
    config_file: ConfigFile
    issue_type: str
    severity: Severity
    title: str
    description: str
    recommendation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    location: Optional[str] = None

@dataclass
class ResourceMetrics:
    """资源指标"""
    resource_id: str
    resource_type: str
    cpu_request: float
    cpu_limit: float
    memory_request: float
    memory_limit: float
    storage_request: float
    storage_limit: float
    actual_cpu_usage: float
    actual_memory_usage: float
    actual_storage_usage: float
    utilization_rate: float

@dataclass
class CostMetrics:
    """成本指标"""
    cost_id: str
    resource_id: str
    resource_type: str
    cpu_cost: float
    memory_cost: float
    storage_cost: float
    network_cost: float
    total_cost: float
    currency: str = "USD"
    period: str = "hourly"

@dataclass
class ComplianceCheck:
    """合规检查"""
    check_id: str
    config_file: ConfigFile
    standard: str
    control_id: str
    control_title: str
    status: str  # PASS, FAIL, WARNING
    description: str
    recommendation: str

class ConfigParser:
    """配置解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_config(self, file_path: str) -> ConfigFile:
        """解析配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检测文件类型
            file_type = self._detect_file_type(file_path)
            
            # 解析内容
            parsed_content = self._parse_content(content, file_type)
            
            # 计算校验和
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            # 获取文件信息
            stat = os.stat(file_path)
            
            config_file = ConfigFile(
                file_id=str(uuid.uuid4()),
                file_path=file_path,
                file_type=file_type,
                content=content,
                parsed_content=parsed_content,
                size=stat.st_size,
                checksum=checksum,
                last_modified=datetime.fromtimestamp(stat.st_mtime)
            )
            
            return config_file
        
        except Exception as e:
            self.logger.error(f"解析配置文件失败: {e}")
            raise
    
    def _detect_file_type(self, file_path: str) -> ConfigType:
        """检测文件类型"""
        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path).lower()
        
        if file_ext in ['.yaml', '.yml']:
            if 'k8s' in file_name or 'kubernetes' in file_name:
                return ConfigType.KUBERNETES
            elif 'docker-compose' in file_name:
                return ConfigType.DOCKER_COMPOSE
            else:
                return ConfigType.KUBERNETES  # 默认为K8s
        elif file_ext == '.json':
            return ConfigType.DOCKER
        elif file_ext == '.tf':
            return ConfigType.TERRAFORM
        elif file_ext in ['.toml']:
            return ConfigType.CUSTOM
        else:
            return ConfigType.CUSTOM
    
    def _parse_content(self, content: str, file_type: ConfigType) -> Dict[str, Any]:
        """解析内容"""
        try:
            if file_type in [ConfigType.KUBERNETES, ConfigType.DOCKER_COMPOSE]:
                return yaml.safe_load(content)
            elif file_type == ConfigType.DOCKER:
                return json.loads(content)
            elif file_type == ConfigType.TERRAFORM:
                return self._parse_terraform(content)
            elif file_type == ConfigType.CUSTOM:
                return self._parse_custom(content)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"解析内容失败: {e}")
            return {}
    
    def _parse_terraform(self, content: str) -> Dict[str, Any]:
        """解析Terraform配置"""
        # 简化实现，实际应该使用hcl解析器
        try:
            import hcl2
            return hcl2.loads(content)
        except ImportError:
            # 如果没有hcl2库，返回基本解析
            return {'raw_content': content}
    
    def _parse_custom(self, content: str) -> Dict[str, Any]:
        """解析自定义配置"""
        # 尝试多种格式
        try:
            return yaml.safe_load(content)
        except:
            try:
                return json.loads(content)
            except:
                try:
                    return toml.loads(content)
                except:
                    return {'raw_content': content}

class SecurityAnalyzer:
    """安全分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_rules = self._load_security_rules()
    
    def analyze_security(self, config_file: ConfigFile) -> List[SecurityIssue]:
        """分析安全"""
        issues = []
        
        if config_file.file_type == ConfigType.KUBERNETES:
            issues = self._analyze_kubernetes_security(config_file)
        elif config_file.file_type == ConfigType.DOCKER:
            issues = self._analyze_docker_security(config_file)
        elif config_file.file_type == ConfigType.TERRAFORM:
            issues = self._analyze_terraform_security(config_file)
        
        return issues
    
    def _analyze_kubernetes_security(self, config_file: ConfigFile) -> List[SecurityIssue]:
        """分析Kubernetes安全"""
        issues = []
        content = config_file.parsed_content
        
        if not isinstance(content, dict):
            return issues
        
        # 检查RBAC权限
        if content.get('kind') == 'ClusterRole':
            issues.extend(self._check_cluster_role_permissions(config_file, content))
        
        # 检查Pod安全
        if content.get('kind') == 'Pod':
            issues.extend(self._check_pod_security(config_file, content))
        
        # 检查Service安全
        if content.get('kind') == 'Service':
            issues.extend(self._check_service_security(config_file, content))
        
        # 检查Secret安全
        if content.get('kind') == 'Secret':
            issues.extend(self._check_secret_security(config_file, content))
        
        return issues
    
    def _check_cluster_role_permissions(self, config_file: ConfigFile, content: Dict) -> List[SecurityIssue]:
        """检查集群角色权限"""
        issues = []
        rules = content.get('rules', [])
        
        for rule in rules:
            verbs = rule.get('verbs', [])
            resources = rule.get('resources', [])
            
            # 检查危险权限
            if '*' in verbs and '*' in resources:
                issues.append(SecurityIssue(
                    issue_id=str(uuid.uuid4()),
                    config_file=config_file,
                    issue_type="excessive_permissions",
                    severity=Severity.CRITICAL,
                    title="过度权限",
                    description="集群角色具有所有资源的所有权限",
                    recommendation="限制权限范围，仅授予必要的权限",
                    cwe_id="CWE-862",
                    cvss_score=9.0
                ))
            
            # 检查cluster-admin权限
            if '*' in verbs and 'clusterroles' in resources:
                issues.append(SecurityIssue(
                    issue_id=str(uuid.uuid4()),
                    config_file=config_file,
                    issue_type="cluster_admin_permissions",
                    severity=Severity.HIGH,
                    title="集群管理员权限",
                    description="角色具有集群管理员权限",
                    recommendation="避免使用cluster-admin权限，使用更细粒度的权限",
                    cwe_id="CWE-862",
                    cvss_score=7.5
                ))
        
        return issues
    
    def _check_pod_security(self, config_file: ConfigFile, content: Dict) -> List[SecurityIssue]:
        """检查Pod安全"""
        issues = []
        spec = content.get('spec', {})
        
        # 检查特权容器
        containers = spec.get('containers', [])
        for i, container in enumerate(containers):
            security_context = container.get('securityContext', {})
            
            if security_context.get('privileged', False):
                issues.append(SecurityIssue(
                    issue_id=str(uuid.uuid4()),
                    config_file=config_file,
                    issue_type="privileged_container",
                    severity=Severity.HIGH,
                    title="特权容器",
                    description=f"容器 {container.get('name', i)} 运行在特权模式",
                    recommendation="避免使用特权容器，如必须使用请确保最小权限原则",
                    cwe_id="CWE-250",
                    cvss_score=7.5,
                    location=f"spec.containers[{i}].securityContext.privileged"
                ))
            
            # 检查root用户运行
            if security_context.get('runAsUser') == 0:
                issues.append(SecurityIssue(
                    issue_id=str(uuid.uuid4()),
                    config_file=config_file,
                    issue_type="root_user",
                    severity=Severity.MEDIUM,
                    title="Root用户运行",
                    description=f"容器 {container.get('name', i)} 以root用户运行",
                    recommendation="使用非root用户运行容器",
                    cwe_id="CWE-250",
                    cvss_score=5.5,
                    location=f"spec.containers[{i}].securityContext.runAsUser"
                ))
        
        return issues
    
    def _check_service_security(self, config_file: ConfigFile, content: Dict) -> List[SecurityIssue]:
        """检查Service安全"""
        issues = []
        spec = content.get('spec', {})
        
        # 检查NodePort
        if spec.get('type') == 'NodePort':
            issues.append(SecurityIssue(
                issue_id=str(uuid.uuid4()),
                config_file=config_file,
                issue_type="nodeport_service",
                severity=Severity.MEDIUM,
                title="NodePort服务",
                description="服务使用NodePort类型，可能暴露到外部",
                recommendation="避免使用NodePort，使用ClusterIP或LoadBalancer",
                cwe_id="CWE-200",
                cvss_score=5.5,
                location="spec.type"
            ))
        
        # 检查外部IP
        external_ips = spec.get('externalIPs', [])
        if external_ips:
            issues.append(SecurityIssue(
                issue_id=str(uuid.uuid4()),
                config_file=config_file,
                issue_type="external_ip",
                severity=Severity.MEDIUM,
                title="外部IP配置",
                description=f"服务配置了外部IP: {external_ips}",
                recommendation="避免使用外部IP，使用内部服务发现",
                cwe_id="CWE-200",
                cvss_score=5.5,
                location="spec.externalIPs"
            ))
        
        return issues
    
    def _check_secret_security(self, config_file: ConfigFile, content: Dict) -> List[SecurityIssue]:
        """检查Secret安全"""
        issues = []
        data = content.get('data', {})
        
        # 检查明文密钥
        string_data = content.get('stringData', {})
        if string_data:
            issues.append(SecurityIssue(
                issue_id=str(uuid.uuid4()),
                config_file=config_file,
                issue_type="plaintext_secret",
                severity=Severity.HIGH,
                title="明文密钥",
                description="Secret使用stringData字段，可能包含明文密钥",
                recommendation="使用加密的data字段，避免明文存储密钥",
                cwe_id="CWE-798",
                cvss_score=7.5,
                location="stringData"
            ))
        
        return issues
    
    def _analyze_docker_security(self, config_file: ConfigFile) -> List[SecurityIssue]:
        """分析Docker安全"""
        issues = []
        content = config_file.parsed_content
        
        # 检查root用户
        if content.get('User') == 'root' or content.get('User') == '0':
            issues.append(SecurityIssue(
                issue_id=str(uuid.uuid4()),
                config_file=config_file,
                issue_type="docker_root_user",
                severity=Severity.MEDIUM,
                title="Docker Root用户",
                description="Docker容器以root用户运行",
                recommendation="使用非root用户运行容器",
                cwe_id="CWE-250",
                cvss_score=5.5,
                location="User"
            ))
        
        return issues
    
    def _analyze_terraform_security(self, config_file: ConfigFile) -> List[SecurityIssue]:
        """分析Terraform安全"""
        issues = []
        content = config_file.parsed_content
        
        # 简化实现，实际应该解析HCL
        if 'raw_content' in content:
            raw_content = content['raw_content']
            
            # 检查明文密钥
            if 'password' in raw_content.lower() and '=' in raw_content:
                issues.append(SecurityIssue(
                    issue_id=str(uuid.uuid4()),
                    config_file=config_file,
                    issue_type="terraform_plaintext_password",
                    severity=Severity.HIGH,
                    title="Terraform明文密码",
                    description="Terraform配置中可能包含明文密码",
                    recommendation="使用变量和环境变量存储敏感信息",
                    cwe_id="CWE-798",
                    cvss_score=7.5
                ))
        
        return issues
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """加载安全规则"""
        return {
            'kubernetes': {
                'rbac': {
                    'dangerous_verbs': ['*'],
                    'dangerous_resources': ['*'],
                    'cluster_admin_verbs': ['*'],
                    'cluster_admin_resources': ['clusterroles']
                },
                'pod': {
                    'privileged_containers': True,
                    'root_user': 0,
                    'host_network': True,
                    'host_pid': True,
                    'host_ipc': True
                },
                'service': {
                    'nodeport_type': 'NodePort',
                    'external_ips': True
                },
                'secret': {
                    'string_data': True
                }
            }
        }

class ResourceAnalyzer:
    """资源分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_resources(self, config_file: ConfigFile) -> List[ResourceMetrics]:
        """分析资源"""
        metrics = []
        
        if config_file.file_type == ConfigType.KUBERNETES:
            metrics = self._analyze_kubernetes_resources(config_file)
        
        return metrics
    
    def _analyze_kubernetes_resources(self, config_file: ConfigFile) -> List[ResourceMetrics]:
        """分析Kubernetes资源"""
        metrics = []
        content = config_file.parsed_content
        
        if not isinstance(content, dict):
            return metrics
        
        # 分析Pod资源
        if content.get('kind') == 'Pod':
            metrics.extend(self._analyze_pod_resources(config_file, content))
        
        # 分析Deployment资源
        if content.get('kind') == 'Deployment':
            metrics.extend(self._analyze_deployment_resources(config_file, content))
        
        return metrics
    
    def _analyze_pod_resources(self, config_file: ConfigFile, content: Dict) -> List[ResourceMetrics]:
        """分析Pod资源"""
        metrics = []
        spec = content.get('spec', {})
        containers = spec.get('containers', [])
        
        for i, container in enumerate(containers):
            name = container.get('name', f'container-{i}')
            resources = container.get('resources', {})
            
            # 解析CPU和内存请求/限制
            cpu_request = self._parse_cpu(resources.get('requests', {}).get('cpu', '0'))
            cpu_limit = self._parse_cpu(resources.get('limits', {}).get('cpu', '0'))
            memory_request = self._parse_memory(resources.get('requests', {}).get('memory', '0'))
            memory_limit = self._parse_memory(resources.get('limits', {}).get('memory', '0'))
            
            # 计算利用率（这里使用模拟数据）
            actual_cpu_usage = cpu_request * 0.7  # 70%利用率
            actual_memory_usage = memory_request * 0.8  # 80%利用率
            
            utilization_rate = (actual_cpu_usage / cpu_limit) if cpu_limit > 0 else 0
            
            metric = ResourceMetrics(
                resource_id=str(uuid.uuid4()),
                resource_type='container',
                cpu_request=cpu_request,
                cpu_limit=cpu_limit,
                memory_request=memory_request,
                memory_limit=memory_limit,
                storage_request=0,
                storage_limit=0,
                actual_cpu_usage=actual_cpu_usage,
                actual_memory_usage=actual_memory_usage,
                actual_storage_usage=0,
                utilization_rate=utilization_rate
            )
            
            metrics.append(metric)
        
        return metrics
    
    def _analyze_deployment_resources(self, config_file: ConfigFile, content: Dict) -> List[ResourceMetrics]:
        """分析Deployment资源"""
        # Deployment分析逻辑类似Pod
        return self._analyze_pod_resources(config_file, content)
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """解析CPU值"""
        if not cpu_str:
            return 0.0
        
        cpu_str = cpu_str.strip()
        
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        else:
            return float(cpu_str)
    
    def _parse_memory(self, memory_str: str) -> float:
        """解析内存值"""
        if not memory_str:
            return 0.0
        
        memory_str = memory_str.strip()
        
        if memory_str.endswith('Ki'):
            return float(memory_str[:-2]) / 1024
        elif memory_str.endswith('Mi'):
            return float(memory_str[:-2])
        elif memory_str.endswith('Gi'):
            return float(memory_str[:-2]) * 1024
        else:
            return float(memory_str)

class CostAnalyzer:
    """成本分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pricing = {
            'cpu': {'on_demand': 0.05, 'reserved': 0.03, 'spot': 0.02},  # per vCPU/hour
            'memory': {'on_demand': 0.005, 'reserved': 0.003, 'spot': 0.002},  # per Gi/hour
            'storage': {'ssd': 0.1, 'hdd': 0.05, 'object': 0.02}  # per Gi/month
        }
    
    def analyze_costs(self, resource_metrics: List[ResourceMetrics]) -> List[CostMetrics]:
        """分析成本"""
        cost_metrics = []
        
        for metric in resource_metrics:
            cost_metric = self._calculate_resource_cost(metric)
            cost_metrics.append(cost_metric)
        
        return cost_metrics
    
    def _calculate_resource_cost(self, metric: ResourceMetrics) -> CostMetrics:
        """计算资源成本"""
        # CPU成本
        cpu_cost = metric.cpu_limit * self.pricing['cpu']['on_demand']
        
        # 内存成本
        memory_cost = metric.memory_limit * self.pricing['memory']['on_demand']
        
        # 存储成本
        storage_cost = metric.storage_limit * self.pricing['storage']['ssd'] / (30 * 24)  # 转换为小时
        
        # 网络成本（简化）
        network_cost = 0.01  # 假设每小时0.01美元
        
        total_cost = cpu_cost + memory_cost + storage_cost + network_cost
        
        return CostMetrics(
            cost_id=str(uuid.uuid4()),
            resource_id=metric.resource_id,
            resource_type=metric.resource_type,
            cpu_cost=cpu_cost,
            memory_cost=memory_cost,
            storage_cost=storage_cost,
            network_cost=network_cost,
            total_cost=total_cost
        )

class ComplianceAnalyzer:
    """合规分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_standards = self._load_compliance_standards()
    
    def analyze_compliance(self, config_file: ConfigFile) -> List[ComplianceCheck]:
        """分析合规性"""
        checks = []
        
        if config_file.file_type == ConfigType.KUBERNETES:
            checks = self._check_kubernetes_compliance(config_file)
        
        return checks
    
    def _check_kubernetes_compliance(self, config_file: ConfigFile) -> List[ComplianceCheck]:
        """检查Kubernetes合规性"""
        checks = []
        content = config_file.parsed_content
        
        if not isinstance(content, dict):
            return checks
        
        # CIS基准检查
        checks.extend(self._check_cis_benchmarks(config_file, content))
        
        return checks
    
    def _check_cis_benchmarks(self, config_file: ConfigFile, content: Dict) -> List[ComplianceCheck]:
        """检查CIS基准"""
        checks = []
        
        # CIS 1.1.1: 确保API Server匿名访问被禁用
        if content.get('kind') == 'APIServer':
            anonymous_auth = content.get('spec', {}).get('anonymousAuth', True)
            if anonymous_auth:
                checks.append(ComplianceCheck(
                    check_id=str(uuid.uuid4()),
                    config_file=config_file,
                    standard="CIS",
                    control_id="1.1.1",
                    control_title="确保API Server匿名访问被禁用",
                    status="FAIL",
                    description="API Server允许匿名访问",
                    recommendation="设置anonymousAuth: false"
                ))
        
        # CIS 5.7.1: 确保Pod安全策略被配置
        if content.get('kind') == 'Pod':
            security_context = content.get('spec', {}).get('securityContext', {})
            if not security_context:
                checks.append(ComplianceCheck(
                    check_id=str(uuid.uuid4()),
                    config_file=config_file,
                    standard="CIS",
                    control_id="5.7.1",
                    control_title="确保Pod安全策略被配置",
                    status="FAIL",
                    description="Pod未配置安全上下文",
                    recommendation="配置Pod安全上下文，包括runAsNonRoot等"
                ))
        
        return checks
    
    def _load_compliance_standards(self) -> Dict[str, Any]:
        """加载合规标准"""
        return {
            'CIS': {
                'kubernetes': {
                    '1.1.1': {
                        'title': '确保API Server匿名访问被禁用',
                        'description': 'API Server应该禁用匿名访问',
                        'recommendation': '设置anonymousAuth: false'
                    },
                    '5.7.1': {
                        'title': '确保Pod安全策略被配置',
                        'description': 'Pod应该配置安全上下文',
                        'recommendation': '配置Pod安全上下文，包括runAsNonRoot等'
                    }
                }
            }
        }

class CloudConfigAnalyzer:
    """云配置分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.config_parser = ConfigParser()
        self.security_analyzer = SecurityAnalyzer()
        self.resource_analyzer = ResourceAnalyzer()
        self.cost_analyzer = CostAnalyzer()
        self.compliance_analyzer = ComplianceAnalyzer()
        
        # 数据存储
        self.config_files = []
        self.analysis_results = []
        self.security_issues = []
        self.resource_metrics = []
        self.cost_metrics = []
        self.compliance_checks = []
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def analyze_config_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """分析配置文件"""
        self.logger.info(f"开始分析 {len(file_paths)} 个配置文件")
        
        # 解析配置文件
        for file_path in file_paths:
            try:
                config_file = self.config_parser.parse_config(file_path)
                self.config_files.append(config_file)
            except Exception as e:
                self.logger.error(f"解析文件失败 {file_path}: {e}")
        
        # 并行分析
        futures = []
        
        for config_file in self.config_files:
            # 安全分析
            future = self.executor.submit(self.security_analyzer.analyze_security, config_file)
            futures.append(('security', future))
            
            # 资源分析
            future = self.executor.submit(self.resource_analyzer.analyze_resources, config_file)
            futures.append(('resource', future))
            
            # 合规分析
            future = self.executor.submit(self.compliance_analyzer.analyze_compliance, config_file)
            futures.append(('compliance', future))
        
        # 收集结果
        for analysis_type, future in futures:
            try:
                result = future.result()
                if analysis_type == 'security':
                    self.security_issues.extend(result)
                elif analysis_type == 'resource':
                    self.resource_metrics.extend(result)
                    # 计算成本
                    cost_metrics = self.cost_analyzer.analyze_costs(result)
                    self.cost_metrics.extend(cost_metrics)
                elif analysis_type == 'compliance':
                    self.compliance_checks.extend(result)
            except Exception as e:
                self.logger.error(f"分析失败: {e}")
        
        # 生成分析报告
        report = self._generate_analysis_report()
        
        self.logger.info("配置文件分析完成")
        return report
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': len(self.config_files),
                'security_issues': len(self.security_issues),
                'resource_metrics': len(self.resource_metrics),
                'compliance_checks': len(self.compliance_checks),
                'total_cost': sum(c.total_cost for c in self.cost_metrics)
            },
            'security_analysis': {
                'issues_by_severity': self._group_issues_by_severity(),
                'issues_by_type': self._group_issues_by_type(),
                'top_issues': self._get_top_security_issues(10)
            },
            'resource_analysis': {
                'resource_utilization': self._calculate_resource_utilization(),
                'optimization_recommendations': self._get_optimization_recommendations()
            },
            'cost_analysis': {
                'cost_breakdown': self._get_cost_breakdown(),
                'cost_optimization': self._get_cost_optimization_suggestions()
            },
            'compliance_analysis': {
                'compliance_status': self._get_compliance_status(),
                'failed_checks': self._get_failed_compliance_checks()
            },
            'detailed_results': {
                'security_issues': [asdict(issue) for issue in self.security_issues],
                'resource_metrics': [asdict(metric) for metric in self.resource_metrics],
                'cost_metrics': [asdict(metric) for metric in self.cost_metrics],
                'compliance_checks': [asdict(check) for check in self.compliance_checks]
            }
        }
        
        return report
    
    def _group_issues_by_severity(self) -> Dict[str, int]:
        """按严重性分组问题"""
        severity_count = defaultdict(int)
        for issue in self.security_issues:
            severity_count[issue.severity.value] += 1
        return dict(severity_count)
    
    def _group_issues_by_type(self) -> Dict[str, int]:
        """按类型分组问题"""
        type_count = defaultdict(int)
        for issue in self.security_issues:
            type_count[issue.issue_type] += 1
        return dict(type_count)
    
    def _get_top_security_issues(self, limit: int) -> List[Dict[str, Any]]:
        """获取顶级安全问题"""
        # 按CVSS分数排序
        sorted_issues = sorted(
            self.security_issues,
            key=lambda x: x.cvss_score or 0,
            reverse=True
        )
        
        return [asdict(issue) for issue in sorted_issues[:limit]]
    
    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """计算资源利用率"""
        if not self.resource_metrics:
            return {}
        
        cpu_utilization = statistics.mean([m.utilization_rate for m in self.resource_metrics])
        memory_utilization = statistics.mean([
            m.actual_memory_usage / m.memory_limit if m.memory_limit > 0 else 0
            for m in self.resource_metrics
        ])
        
        return {
            'cpu_utilization': cpu_utilization,
            'memory_utilization': memory_utilization
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        utilization = self._calculate_resource_utilization()
        
        if utilization.get('cpu_utilization', 0) < 0.3:
            recommendations.append("CPU利用率较低，建议减少CPU请求")
        
        if utilization.get('memory_utilization', 0) < 0.3:
            recommendations.append("内存利用率较低，建议减少内存请求")
        
        # 检查资源浪费
        wasted_resources = [
            m for m in self.resource_metrics
            if m.utilization_rate < 0.5
        ]
        
        if len(wasted_resources) > len(self.resource_metrics) * 0.5:
            recommendations.append("超过50%的资源利用率低于50%，建议优化资源配置")
        
        return recommendations
    
    def _get_cost_breakdown(self) -> Dict[str, float]:
        """获取成本分解"""
        breakdown = {
            'cpu_cost': sum(c.cpu_cost for c in self.cost_metrics),
            'memory_cost': sum(c.memory_cost for c in self.cost_metrics),
            'storage_cost': sum(c.storage_cost for c in self.cost_metrics),
            'network_cost': sum(c.network_cost for c in self.cost_metrics)
        }
        
        breakdown['total_cost'] = sum(breakdown.values())
        
        return breakdown
    
    def _get_cost_optimization_suggestions(self) -> List[str]:
        """获取成本优化建议"""
        suggestions = []
        
        # 检查高成本资源
        high_cost_resources = [
            c for c in self.cost_metrics
            if c.total_cost > 10  # 每小时超过10美元
        ]
        
        if high_cost_resources:
            suggestions.append(f"发现 {len(high_cost_resources)} 个高成本资源，建议优化")
        
        # 检查资源浪费
        wasted_cost = sum(
            c.total_cost for c in self.cost_metrics
            if self._get_resource_utilization_by_id(c.resource_id) < 0.5
        )
        
        if wasted_cost > 5:  # 每小时浪费超过5美元
            suggestions.append(f"每小时浪费 ${wasted_cost:.2f}，建议优化资源配置")
        
        return suggestions
    
    def _get_resource_utilization_by_id(self, resource_id: str) -> float:
        """根据资源ID获取利用率"""
        for metric in self.resource_metrics:
            if metric.resource_id == resource_id:
                return metric.utilization_rate
        return 0.0
    
    def _get_compliance_status(self) -> Dict[str, int]:
        """获取合规状态"""
        status_count = defaultdict(int)
        for check in self.compliance_checks:
            status_count[check.status] += 1
        return dict(status_count)
    
    def _get_failed_compliance_checks(self) -> List[Dict[str, Any]]:
        """获取失败的合规检查"""
        failed_checks = [check for check in self.compliance_checks if check.status == 'FAIL']
        return [asdict(check) for check in failed_checks]

# 使用示例
# 创建分析器
analyzer = CloudConfigAnalyzer()

# 分析配置文件
config_files = [
    '/path/to/deployment.yaml',
    '/path/to/service.yaml',
    '/path/to/configmap.yaml'
]

report = analyzer.analyze_config_files(config_files)

# 输出报告
print(f"\n分析报告:")
print(json.dumps(report, indent=2, ensure_ascii=False, default=str))

# 查看安全问题
print(f"\n安全问题:")
for issue in analyzer.security_issues:
    print(f"- {issue.title}: {issue.description}")

# 查看资源优化建议
print(f"\n资源优化建议:")
utilization = analyzer._calculate_resource_utilization()
print(f"CPU利用率: {utilization.get('cpu_utilization', 0):.2%}")
print(f"内存利用率: {utilization.get('memory_utilization', 0):.2%}")

# 查看成本分析
cost_breakdown = analyzer._get_cost_breakdown()
print(f"\n成本分解:")
print(f"总成本: ${cost_breakdown.get('total_cost', 0):.2f}/小时")
print(f"CPU成本: ${cost_breakdown.get('cpu_cost', 0):.2f}/小时")
print(f"内存成本: ${cost_breakdown.get('memory_cost', 0):.2f}/小时")

# 查看合规状态
compliance_status = analyzer._get_compliance_status()
print(f"\n合规状态:")
print(f"通过: {compliance_status.get('PASS', 0)}")
print(f"失败: {compliance_status.get('FAIL', 0)}")
print(f"警告: {compliance_status.get('WARNING', 0)}")
```

## 参考资源

### 云原生安全
- [Kubernetes安全最佳实践](https://kubernetes.io/docs/concepts/security/)
- [CIS Kubernetes基准](https://www.cisecurity.org/benchmark/kubernetes)
- [NSA Kubernetes安全指南](https://www.nsa.gov/News-Features/Feature-Stories/Article-View/Article/2169668/nsacisa-technical-report-hardening-kubernetes/)
- [OWASP Kubernetes安全指南](https://owasp.org/www-project-kubernetes-top-ten/)

### 配置管理
- [Kubernetes配置最佳实践](https://kubernetes.io/docs/concepts/configuration/)
- [Docker安全配置](https://docs.docker.com/engine/security/)
- [Terraform安全配置](https://www.terraform.io/docs/cloud-docs/security-encryption)
- [Helm最佳实践](https://helm.sh/docs/topics/best_practices/)

### 成本优化
- [Kubernetes成本优化指南](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/)
- [云成本管理最佳实践](https://docs.microsoft.com/en-us/azure/architecture/framework/cost/overview)
- [AWS成本优化](https://aws.amazon.com/cost-management/)
- [GCP成本管理](https://cloud.google.com/cost-management)

### 合规性
- [CIS基准](https://www.cisecurity.org/cis-benchmarks/)
- [PCI-DSS合规](https://www.pcisecuritystandards.org/)
- [SOC 2合规](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/pages/aicpasoc2report.aspx)
- [GDPR合规](https://gdpr-info.eu/)
