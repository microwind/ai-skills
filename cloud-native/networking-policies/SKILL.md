---
name: 网络策略配置
description: "当配置Kubernetes网络策略时，分析网络流量控制，优化安全隔离策略，解决网络通信问题。验证网络规则，设计微服务安全架构，和最佳实践。"
license: MIT
---

# 网络策略配置技能

## 概述
Kubernetes网络策略是保障集群安全的重要机制。不当的网络配置会导致安全漏洞和服务通信问题。在设计网络策略前需要仔细分析应用架构和安全需求。

**核心原则**: 好的网络策略应该实现最小权限原则，确保服务间安全通信，同时不影响正常业务。坏的网络策略会导致服务不可用或安全风险。

## 何时使用

**始终:**
- 设计微服务安全架构时
- 实施网络隔离策略时
- 配置服务间访问控制时
- 解决网络通信问题时
- 建立零信任网络架构时

**触发短语:**
- "配置网络策略"
- "K8s网络隔离"
- "服务间通信控制"
- "网络安全策略"
- "零信任网络"
- "NetworkPolicy配置"

## 网络策略配置功能

### 网络隔离设计
- 命名空间隔离策略
- 标签选择器配置
- 入站流量控制
- 出站流量控制
- 端口级访问控制

### 安全策略管理
- 白名单规则配置
- 黑名单规则设置
- 默认拒绝策略
- 例外规则处理
- 策略优先级管理

### 流量监控分析
- 网络流量统计
- 连接状态监控
- 拒绝流量分析
- 策略效果评估
- 安全事件告警

### 策略优化建议
- 规则简化建议
- 性能优化方案
- 安全加固指导
- 最佳实践推荐
- 架构改进建议

## 常见网络策略问题

### 策略配置错误
```
问题:
NetworkPolicy配置错误导致服务无法访问

错误示例:
- 选择器不匹配Pod标签
- 端口配置错误
- 策略方向设置错误
- 缺少必要的入站规则

解决方案:
1. 仔细检查Pod标签匹配
2. 验证端口和协议配置
3. 确认入站和出站规则
4. 测试策略生效情况
```

### 网络通信中断
```
问题:
过于严格的网络策略导致正常通信被阻断

错误示例:
- 默认拒绝所有流量
- 缺少DNS访问规则
- 忘记配置健康检查端口
- 忽略系统服务通信

解决方案:
1. 允许DNS和kube-proxy通信
2. 配置健康检查端口访问
3. 添加必要的系统服务规则
4. 使用渐进式策略部署
```

### 性能影响问题
```
问题:
复杂的网络策略影响网络性能

错误示例:
- 策略规则过多
- 复杂的选择器表达式
- 频繁的策略变更
- 缺乏策略优化

解决方案:
1. 简化策略规则
2. 优化选择器表达式
3. 合并相似策略
4. 监控性能影响
```

## 代码实现示例

### 网络策略分析器
```python
import yaml
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class NetworkPolicy:
    """网络策略"""
    name: str
    namespace: str
    pod_selector: Dict[str, str]
    policy_types: List[str]
    ingress_rules: List[Dict[str, Any]]
    egress_rules: List[Dict[str, Any]]
    
@dataclass
class PolicyIssue:
    """策略问题"""
    severity: str  # critical, high, medium, low
    type: str
    policy_name: str
    message: str
    suggestion: str
    affected_pods: List[str]

@dataclass
class TrafficAnalysis:
    """流量分析"""
    allowed_connections: List[Dict[str, Any]]
    denied_connections: List[Dict[str, Any]]
    policy_coverage: Dict[str, float]
    security_gaps: List[Dict[str, Any]]

class NetworkPolicyAnalyzer:
    def __init__(self):
        self.policies: List[NetworkPolicy] = []
        self.issues: List[PolicyIssue] = []
        
    def analyze_policies_from_yaml(self, yaml_file: str) -> Dict[str, Any]:
        """从YAML文件分析网络策略"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.analyze_policies_content(content)
            
        except Exception as e:
            return {'error': f'读取文件失败: {e}'}
    
    def analyze_policies_content(self, content: str) -> Dict[str, Any]:
        """分析网络策略内容"""
        try:
            # 重置状态
            self.policies = []
            self.issues = []
            
            # 解析YAML
            documents = yaml.safe_load_all(content)
            
            for doc in documents:
                if doc is None:
                    continue
                
                if doc.get('kind') == 'NetworkPolicy':
                    policy = self.parse_network_policy(doc)
                    if policy:
                        self.policies.append(policy)
                        self.analyze_policy(policy)
            
            # 生成分析报告
            report = {
                'total_policies': len(self.policies),
                'policies': [self.policy_to_dict(p) for p in self.policies],
                'issues': self.issues,
                'traffic_analysis': self.analyze_traffic(),
                'security_assessment': self.assess_security(),
                'recommendations': self.generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def parse_network_policy(self, doc: Dict[str, Any]) -> Optional[NetworkPolicy]:
        """解析网络策略"""
        try:
            metadata = doc.get('metadata', {})
            spec = doc.get('spec', {})
            
            policy = NetworkPolicy(
                name=metadata.get('name', ''),
                namespace=metadata.get('namespace', 'default'),
                pod_selector=spec.get('podSelector', {}),
                policy_types=spec.get('policyTypes', []),
                ingress_rules=spec.get('ingress', []),
                egress_rules=spec.get('egress', [])
            )
            
            return policy
            
        except Exception as e:
            self.issues.append(PolicyIssue(
                severity='high',
                type='parse_error',
                policy_name=metadata.get('name', 'unknown'),
                message=f'解析策略失败: {e}',
                suggestion='检查YAML格式和字段',
                affected_pods=[]
            ))
            return None
    
    def analyze_policy(self, policy: NetworkPolicy) -> None:
        """分析单个策略"""
        # 检查策略基本配置
        self.check_policy_basic_config(policy)
        
        # 检查选择器配置
        self.check_selector_config(policy)
        
        # 检查入站规则
        self.check_ingress_rules(policy)
        
        # 检查出站规则
        self.check_egress_rules(policy)
        
        # 检查策略覆盖范围
        self.check_policy_coverage(policy)
    
    def check_policy_basic_config(self, policy: NetworkPolicy) -> None:
        """检查策略基本配置"""
        if not policy.name:
            self.issues.append(PolicyIssue(
                severity='critical',
                type='missing_name',
                policy_name='unknown',
                message='策略缺少名称',
                suggestion='为策略设置唯一名称',
                affected_pods=[]
            ))
        
        if not policy.policy_types:
            self.issues.append(PolicyIssue(
                severity='high',
                type='missing_policy_types',
                policy_name=policy.name,
                message='策略没有指定policyTypes',
                suggestion='添加Ingress和/或Egress类型',
                affected_pods=[]
            ))
        
        if not policy.pod_selector:
            self.issues.append(PolicyIssue(
                severity='critical',
                type='missing_selector',
                policy_name=policy.name,
                message='策略没有选择器',
                suggestion='添加podSelector选择目标Pod',
                affected_pods=[]
            ))
    
    def check_selector_config(self, policy: NetworkPolicy) -> None:
        """检查选择器配置"""
        if not policy.pod_selector:
            return
        
        # 检查选择器是否过于宽泛
        if len(policy.pod_selector) == 0:
            self.issues.append(PolicyIssue(
                severity='medium',
                type='broad_selector',
                policy_name=policy.name,
                message='选择器过于宽泛，影响所有Pod',
                suggestion='使用更具体的选择器标签',
                affected_pods=['all']
            ))
        
        # 检查标签是否存在
        for key, value in policy.pod_selector.items():
            if not key or not value:
                self.issues.append(PolicyIssue(
                    severity='high',
                    type='invalid_selector',
                    policy_name=policy.name,
                    message=f'无效的选择器: {key}={value}',
                    suggestion='检查标签键值对的有效性',
                    affected_pods=[]
                ))
    
    def check_ingress_rules(self, policy: NetworkPolicy) -> None:
        """检查入站规则"""
        if 'Ingress' in policy.policy_types and not policy.ingress_rules:
            self.issues.append(PolicyIssue(
                severity='medium',
                type='missing_ingress_rules',
                policy_name=policy.name,
                message='策略类型包含Ingress但没有入站规则',
                suggestion='添加入站规则或移除Ingress类型',
                affected_pods=[]
            ))
        
        for i, rule in enumerate(policy.ingress_rules):
            self.check_ingress_rule(policy, rule, i)
    
    def check_ingress_rule(self, policy: NetworkPolicy, rule: Dict[str, Any], index: int) -> None:
        """检查单个入站规则"""
        # 检查来源配置
        from_ = rule.get('from', [])
        if not from_:
            self.issues.append(PolicyIssue(
                severity='medium',
                type='ingress_no_from',
                policy_name=policy.name,
                message=f'入站规则{index}没有指定来源',
                suggestion='添加from字段限制访问来源',
                affected_pods=[]
            ))
        
        # 检查端口配置
        ports = rule.get('ports', [])
        if not ports:
            self.issues.append(PolicyIssue(
                severity='low',
                type='ingress_no_ports',
                policy_name=policy.name,
                message=f'入站规则{index}没有指定端口',
                suggestion='添加ports字段限制访问端口',
                affected_pods=[]
            ))
        else:
            for port in ports:
                if not port.get('port'):
                    self.issues.append(PolicyIssue(
                        severity='high',
                        type='invalid_port',
                        policy_name=policy.name,
                        message=f'入站规则{index}端口配置无效',
                        suggestion='检查端口号或端口名称',
                        affected_pods=[]
                    ))
    
    def check_egress_rules(self, policy: NetworkPolicy) -> None:
        """检查出站规则"""
        if 'Egress' in policy.policy_types and not policy.egress_rules:
            self.issues.append(PolicyIssue(
                severity='medium',
                type='missing_egress_rules',
                policy_name=policy.name,
                message='策略类型包含Egress但没有出站规则',
                suggestion='添加出站规则或移除Egress类型',
                affected_pods=[]
            ))
        
        for i, rule in enumerate(policy.egress_rules):
            self.check_egress_rule(policy, rule, i)
    
    def check_egress_rule(self, policy: NetworkPolicy, rule: Dict[str, Any], index: int) -> None:
        """检查单个出站规则"""
        # 检查目标配置
        to_ = rule.get('to', [])
        if not to_:
            self.issues.append(PolicyIssue(
                severity='medium',
                type='egress_no_to',
                policy_name=policy.name,
                message=f'出站规则{index}没有指定目标',
                suggestion='添加to字段限制访问目标',
                affected_pods=[]
            ))
        
        # 检查端口配置
        ports = rule.get('ports', [])
        if ports:
            for port in ports:
                if not port.get('port'):
                    self.issues.append(PolicyIssue(
                        severity='high',
                        type='invalid_port',
                        policy_name=policy.name,
                        message=f'出站规则{index}端口配置无效',
                        suggestion='检查端口号或端口名称',
                        affected_pods=[]
                    ))
    
    def check_policy_coverage(self, policy: NetworkPolicy) -> None:
        """检查策略覆盖范围"""
        # 检查是否覆盖了必要的系统流量
        has_dns = False
        has_kube_api = False
        
        for rule in policy.egress_rules:
            for to in rule.get('to', []):
                if to.get('namespaceSelector'):
                    # 检查是否允许kube-system命名空间
                    if 'kube-system' in str(to.get('namespaceSelector', {})):
                        has_dns = True
                        has_kube_api = True
        
        if not has_dns and 'Egress' in policy.policy_types:
            self.issues.append(PolicyIssue(
                severity='medium',
                type='missing_dns',
                policy_name=policy.name,
                message='策略可能阻止DNS访问',
                suggestion='添加对kube-system命名空间的DNS访问',
                affected_pods=[]
            ))
    
    def analyze_traffic(self) -> TrafficAnalysis:
        """分析网络流量"""
        allowed_connections = []
        denied_connections = []
        policy_coverage = {}
        security_gaps = []
        
        # 分析每个策略的流量影响
        for policy in self.policies:
            # 分析允许的连接
            for rule in policy.ingress_rules:
                for from_ in rule.get('from', []):
                    for port in rule.get('ports', []):
                        connection = {
                            'policy': policy.name,
                            'source': from_,
                            'destination': policy.pod_selector,
                            'port': port.get('port'),
                            'protocol': port.get('protocol', 'TCP'),
                            'direction': 'ingress'
                        }
                        allowed_connections.append(connection)
            
            # 分析出站连接
            for rule in policy.egress_rules:
                for to in rule.get('to', []):
                    for port in rule.get('ports', []):
                        connection = {
                            'policy': policy.name,
                            'source': policy.pod_selector,
                            'destination': to,
                            'port': port.get('port'),
                            'protocol': port.get('protocol', 'TCP'),
                            'direction': 'egress'
                        }
                        allowed_connections.append(connection)
        
        # 计算策略覆盖率
        total_pods = len(set(self.get_all_target_pods()))
        covered_pods = len(set(self.get_covered_pods()))
        
        if total_pods > 0:
            policy_coverage['overall'] = covered_pods / total_pods
        else:
            policy_coverage['overall'] = 0.0
        
        # 识别安全缺口
        security_gaps = self.identify_security_gaps()
        
        return TrafficAnalysis(
            allowed_connections=allowed_connections,
            denied_connections=denied_connections,
            policy_coverage=policy_coverage,
            security_gaps=security_gaps
        )
    
    def get_all_target_pods(self) -> List[str]:
        """获取所有目标Pod"""
        all_pods = []
        for policy in self.policies:
            selector = policy.pod_selector
            if selector:
                # 简化实现：使用选择器作为Pod标识
                pod_id = f"{policy.namespace}:{','.join(f'{k}={v}' for k, v in selector.items())}"
                all_pods.append(pod_id)
        return all_pods
    
    def get_covered_pods(self) -> List[str]:
        """获取被策略覆盖的Pod"""
        return self.get_all_target_pods()
    
    def identify_security_gaps(self) -> List[Dict[str, Any]]:
        """识别安全缺口"""
        gaps = []
        
        # 检查是否有默认拒绝策略
        has_default_deny = any(
            len(policy.pod_selector) == 0 and 
            'Ingress' in policy.policy_types and
            not policy.ingress_rules
            for policy in self.policies
        )
        
        if not has_default_deny:
            gaps.append({
                'type': 'no_default_deny',
                'severity': 'high',
                'message': '缺少默认拒绝策略',
                'suggestion': '添加默认拒绝所有入站流量的策略'
            })
        
        # 检查是否有未保护的Pod
        protected_pods = set()
        for policy in self.policies:
            protected_pods.update(self.get_target_pods_for_policy(policy))
        
        if len(protected_pods) == 0:
            gaps.append({
                'type': 'no_protection',
                'severity': 'critical',
                'message': '没有Pod受到网络策略保护',
                'suggestion': '为关键服务添加网络策略'
            })
        
        return gaps
    
    def get_target_pods_for_policy(self, policy: NetworkPolicy) -> List[str]:
        """获取策略的目标Pod"""
        selector = policy.pod_selector
        if selector:
            pod_id = f"{policy.namespace}:{','.join(f'{k}={v}' for k, v in selector.items())}"
            return [pod_id]
        return []
    
    def assess_security(self) -> Dict[str, Any]:
        """评估安全性"""
        assessment = {
            'security_score': 0,
            'risk_level': 'unknown',
            'compliance_status': 'non_compliant',
            'security_metrics': {}
        }
        
        # 计算安全评分
        score = 100
        
        # 根据问题扣分
        for issue in self.issues:
            if issue.severity == 'critical':
                score -= 30
            elif issue.severity == 'high':
                score -= 20
            elif issue.severity == 'medium':
                score -= 10
            elif issue.severity == 'low':
                score -= 5
        
        assessment['security_score'] = max(0, score)
        
        # 确定风险等级
        if score >= 80:
            assessment['risk_level'] = 'low'
            assessment['compliance_status'] = 'compliant'
        elif score >= 60:
            assessment['risk_level'] = 'medium'
        elif score >= 40:
            assessment['risk_level'] = 'high'
        else:
            assessment['risk_level'] = 'critical'
        
        # 安全指标
        assessment['security_metrics'] = {
            'total_policies': len(self.policies),
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'high_issues': len([i for i in self.issues if i.severity == 'high']),
            'policy_coverage': self.analyze_traffic().policy_coverage.get('overall', 0)
        }
        
        return assessment
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 基于问题生成建议
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue.type] += 1
        
        if issue_counts['missing_selector'] > 0:
            recommendations.append({
                'priority': 'critical',
                'type': 'configuration',
                'message': '存在没有选择器的策略',
                'suggestion': '为所有策略添加明确的Pod选择器'
            })
        
        if issue_counts['missing_policy_types'] > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'configuration',
                'message': '存在没有指定策略类型的策略',
                'suggestion': '为所有策略指定Ingress和/或Egress类型'
            })
        
        if issue_counts['broad_selector'] > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'security',
                'message': '存在过于宽泛的选择器',
                'suggestion': '使用更具体的标签选择器减少影响范围'
            })
        
        # 通用建议
        if len(self.policies) == 0:
            recommendations.append({
                'priority': 'high',
                'type': 'security',
                'message': '没有配置任何网络策略',
                'suggestion': '从关键服务开始添加网络策略保护'
            })
        
        # 安全建议
        security_assessment = self.assess_security()
        if security_assessment['risk_level'] in ['high', 'critical']:
            recommendations.append({
                'priority': 'critical',
                'type': 'security',
                'message': '安全风险较高',
                'suggestion': '立即审查和加强网络策略配置'
            })
        
        return recommendations
    
    def policy_to_dict(self, policy: NetworkPolicy) -> Dict[str, Any]:
        """将策略转换为字典"""
        return {
            'name': policy.name,
            'namespace': policy.namespace,
            'pod_selector': policy.pod_selector,
            'policy_types': policy.policy_types,
            'ingress_rules_count': len(policy.ingress_rules),
            'egress_rules_count': len(policy.egress_rules)
        }

# 网络策略生成器
class NetworkPolicyGenerator:
    def __init__(self):
        self.templates = self.load_policy_templates()
        
    def load_policy_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载策略模板"""
        return {
            'default_deny': {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'NetworkPolicy',
                'metadata': {
                    'name': 'default-deny-all'
                },
                'spec': {
                    'podSelector': {},
                    'policyTypes': ['Ingress', 'Egress']
                }
            },
            'allow_dns': {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'NetworkPolicy',
                'metadata': {
                    'name': 'allow-dns'
                },
                'spec': {
                    'podSelector': {},
                    'policyTypes': ['Egress'],
                    'egress': [
                        {
                            'to': [
                                {
                                    'namespaceSelector': {
                                        'matchLabels': {
                                            'name': 'kube-system'
                                        }
                                    }
                                }
                            ],
                            'ports': [
                                {
                                    'protocol': 'UDP',
                                    'port': 53
                                }
                            ]
                        }
                    ]
                }
            },
            'web_server': {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'NetworkPolicy',
                'metadata': {
                    'name': 'web-server-policy'
                },
                'spec': {
                    'podSelector': {
                        'matchLabels': {
                            'role': 'web'
                        }
                    },
                    'policyTypes': ['Ingress'],
                    'ingress': [
                        {
                            'from': [
                                {
                                    'namespaceSelector': {}
                                }
                            ],
                            'ports': [
                                {
                                    'protocol': 'TCP',
                                    'port': 80
                                },
                                {
                                    'protocol': 'TCP',
                                    'port': 443
                                }
                            ]
                        }
                    ]
                }
            }
        }
    
    def generate_policy(self, template_name: str, **kwargs) -> Dict[str, Any]:
        """生成网络策略"""
        if template_name not in self.templates:
            raise ValueError(f'未知模板: {template_name}')
        
        policy = self.deepcopy(self.templates[template_name])
        
        # 应用自定义参数
        self.apply_custom_params(policy, kwargs)
        
        return policy
    
    def apply_custom_params(self, policy: Dict[str, Any], params: Dict[str, Any]) -> None:
        """应用自定义参数"""
        # 设置名称
        if 'name' in params:
            policy['metadata']['name'] = params['name']
        
        # 设置命名空间
        if 'namespace' in params:
            policy['metadata']['namespace'] = params['namespace']
        
        # 设置Pod选择器
        if 'pod_selector' in params:
            policy['spec']['podSelector'] = params['pod_selector']
        
        # 设置策略类型
        if 'policy_types' in params:
            policy['spec']['policyTypes'] = params['policy_types']
        
        # 设置入站规则
        if 'ingress' in params:
            policy['spec']['ingress'] = params['ingress']
        
        # 设置出站规则
        if 'egress' in params:
            policy['spec']['egress'] = params['egress']
    
    def deepcopy(self, obj: Any) -> Any:
        """深拷贝对象"""
        import copy
        return copy.deepcopy(obj)
    
    def generate_microservice_policies(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为微服务生成策略"""
        policies = []
        
        # 生成默认拒绝策略
        default_deny = self.generate_policy('default_deny')
        policies.append(default_deny)
        
        # 生成DNS允许策略
        allow_dns = self.generate_policy('allow_dns')
        policies.append(allow_dns)
        
        # 为每个服务生成策略
        for service in services:
            service_name = service.get('name', 'unknown')
            namespace = service.get('namespace', 'default')
            labels = service.get('labels', {})
            ports = service.get('ports', [80])
            allowed_sources = service.get('allowed_sources', [])
            
            # 生成服务策略
            policy = {
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'NetworkPolicy',
                'metadata': {
                    'name': f'{service_name}-policy',
                    'namespace': namespace
                },
                'spec': {
                    'podSelector': {
                        'matchLabels': labels
                    },
                    'policyTypes': ['Ingress'],
                    'ingress': []
                }
            }
            
            # 添加允许的来源
            if allowed_sources:
                for source in allowed_sources:
                    rule = {'from': []}
                    
                    if source.get('namespace'):
                        rule['from'].append({
                            'namespaceSelector': {
                                'matchLabels': {
                                    'name': source['namespace']
                                }
                            }
                        })
                    
                    if source.get('labels'):
                        rule['from'].append({
                            'podSelector': {
                                'matchLabels': source['labels']
                            }
                        })
                    
                    # 添加端口
                    rule['ports'] = [
                        {'protocol': 'TCP', 'port': port}
                        for port in ports
                    ]
                    
                    policy['spec']['ingress'].append(rule)
            else:
                # 允许所有来源
                policy['spec']['ingress'].append({
                    'ports': [
                        {'protocol': 'TCP', 'port': port}
                        for port in ports
                    ]
                })
            
            policies.append(policy)
        
        return policies

# 使用示例
def main():
    # 分析现有策略
    analyzer = NetworkPolicyAnalyzer()
    analysis_result = analyzer.analyze_policies_from_yaml('network-policies.yaml')
    
    print("网络策略分析结果:")
    print(f"总策略数: {analysis_result['total_policies']}")
    print(f"安全评分: {analysis_result['security_assessment']['security_score']}")
    print(f"风险等级: {analysis_result['security_assessment']['risk_level']}")
    
    # 生成新策略
    generator = NetworkPolicyGenerator()
    
    # 生成微服务策略
    services = [
        {
            'name': 'web-service',
            'namespace': 'production',
            'labels': {'app': 'web', 'tier': 'frontend'},
            'ports': [80, 443],
            'allowed_sources': [
                {'namespace': 'ingress'},
                {'labels': {'app': 'api', 'tier': 'backend'}}
            ]
        },
        {
            'name': 'api-service',
            'namespace': 'production',
            'labels': {'app': 'api', 'tier': 'backend'},
            'ports': [8080],
            'allowed_sources': [
                {'labels': {'app': 'web', 'tier': 'frontend'}},
                {'labels': {'app': 'worker', 'tier': 'backend'}}
            ]
        }
    ]
    
    policies = generator.generate_microservice_policies(services)
    
    print(f"\n生成了 {len(policies)} 个网络策略:")
    for policy in policies:
        print(f"- {policy['metadata']['name']}")

if __name__ == '__main__':
    main()
```

### 网络流量监控器
```python
import time
import json
import subprocess
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ConnectionInfo:
    """连接信息"""
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: str
    state: str
    bytes_sent: int
    bytes_received: int
    duration: float

@dataclass
class PolicyViolation:
    """策略违规"""
    timestamp: float
    source_pod: str
    dest_pod: str
    source_ip: str
    dest_ip: str
    port: int
    protocol: str
    policy_name: str
    violation_type: str
    action: str  # allow, deny

class NetworkTrafficMonitor:
    def __init__(self, namespace: str = 'default'):
        self.namespace = namespace
        self.connections: List[ConnectionInfo] = []
        self.violations: List[PolicyViolation] = []
        
    def monitor_network_traffic(self, duration: int = 60) -> Dict[str, Any]:
        """监控网络流量"""
        try:
            start_time = time.time()
            end_time = start_time + duration
            
            # 获取当前连接
            connections = self.get_current_connections()
            
            # 分析流量模式
            traffic_patterns = self.analyze_traffic_patterns(connections)
            
            # 检测策略违规
            violations = self.detect_policy_violations(connections)
            
            # 生成监控报告
            report = {
                'monitoring_period': duration,
                'timestamp': time.time(),
                'namespace': self.namespace,
                'active_connections': len(connections),
                'traffic_patterns': traffic_patterns,
                'policy_violations': violations,
                'network_health': self.assess_network_health(connections, violations)
            }
            
            return report
            
        except Exception as e:
            return {'error': f'监控失败: {e}'}
    
    def get_current_connections(self) -> List[ConnectionInfo]:
        """获取当前网络连接"""
        connections = []
        
        try:
            # 使用netstat获取连接信息
            result = subprocess.run(
                ['netstat', '-an'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'ESTABLISHED' in line or 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        conn = self.parse_netstat_line(line)
                        if conn:
                            connections.append(conn)
                            
        except subprocess.CalledProcessError:
            # 如果netstat失败，尝试使用ss
            try:
                result = subprocess.run(
                    ['ss', '-tan'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                for line in result.stdout.split('\n'):
                    if line and not line.startswith('State'):
                        conn = self.parse_ss_line(line)
                        if conn:
                            connections.append(conn)
                            
            except subprocess.CalledProcessError as e:
                print(f'获取网络连接失败: {e}')
        
        return connections
    
    def parse_netstat_line(self, line: str) -> Optional[ConnectionInfo]:
        """解析netstat输出行"""
        try:
            parts = line.split()
            if len(parts) < 6:
                return None
            
            protocol = parts[0]
            local_address = parts[3]
            foreign_address = parts[4]
            state = parts[5] if len(parts) > 5 else 'UNKNOWN'
            
            # 解析本地地址
            if ':' in local_address:
                local_ip, local_port = local_address.rsplit(':', 1)
                local_port = int(local_port)
            else:
                local_ip = local_address
                local_port = 0
            
            # 解析远程地址
            if ':' in foreign_address:
                foreign_ip, foreign_port = foreign_address.rsplit(':', 1)
                foreign_port = int(foreign_port)
            else:
                foreign_ip = foreign_address
                foreign_port = 0
            
            return ConnectionInfo(
                source_ip=foreign_ip,
                source_port=foreign_port,
                dest_ip=local_ip,
                dest_port=local_port,
                protocol=protocol,
                state=state,
                bytes_sent=0,
                bytes_received=0,
                duration=0
            )
            
        except (ValueError, IndexError):
            return None
    
    def parse_ss_line(self, line: str) -> Optional[ConnectionInfo]:
        """解析ss输出行"""
        try:
            parts = line.split()
            if len(parts) < 5:
                return None
            
            state = parts[0]
            local_address = parts[3]
            foreign_address = parts[4]
            
            # 解析协议
            protocol = 'TCP' if 'tcp' in line.lower() else 'UDP'
            
            # 解析地址
            if ':' in local_address:
                local_ip, local_port = local_address.rsplit(':', 1)
                local_port = int(local_port)
            else:
                local_ip = local_address
                local_port = 0
            
            if ':' in foreign_address:
                foreign_ip, foreign_port = foreign_address.rsplit(':', 1)
                foreign_port = int(foreign_port)
            else:
                foreign_ip = foreign_address
                foreign_port = 0
            
            return ConnectionInfo(
                source_ip=foreign_ip,
                source_port=foreign_port,
                dest_ip=local_ip,
                dest_port=local_port,
                protocol=protocol,
                state=state,
                bytes_sent=0,
                bytes_received=0,
                duration=0
            )
            
        except (ValueError, IndexError):
            return None
    
    def analyze_traffic_patterns(self, connections: List[ConnectionInfo]) -> Dict[str, Any]:
        """分析流量模式"""
        patterns = {
            'protocols': defaultdict(int),
            'ports': defaultdict(int),
            'states': defaultdict(int),
            'top_talkers': [],
            'geographic_distribution': defaultdict(int)
        }
        
        # 统计协议分布
        for conn in connections:
            patterns['protocols'][conn.protocol] += 1
            patterns['ports'][conn.dest_port] += 1
            patterns['states'][conn.state] += 1
        
        # 找出流量最大的连接
        connection_counts = defaultdict(int)
        for conn in connections:
            key = f"{conn.source_ip}:{conn.source_port} -> {conn.dest_ip}:{conn.dest_port}"
            connection_counts[key] += 1
        
        patterns['top_talkers'] = sorted(
            connection_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return dict(patterns)
    
    def detect_policy_violations(self, connections: List[ConnectionInfo]) -> List[PolicyViolation]:
        """检测策略违规"""
        violations = []
        
        # 这里应该与实际的网络策略进行比较
        # 简化实现：检测一些常见的违规模式
        
        for conn in connections:
            # 检测可疑连接
            if self.is_suspicious_connection(conn):
                violation = PolicyViolation(
                    timestamp=time.time(),
                    source_pod='unknown',
                    dest_pod='unknown',
                    source_ip=conn.source_ip,
                    dest_ip=conn.dest_ip,
                    port=conn.dest_port,
                    protocol=conn.protocol,
                    policy_name='unknown',
                    violation_type='suspicious_traffic',
                    action='deny'
                )
                violations.append(violation)
        
        return violations
    
    def is_suspicious_connection(self, conn: ConnectionInfo) -> bool:
        """判断是否为可疑连接"""
        # 检查是否连接到可疑端口
        suspicious_ports = [22, 23, 135, 139, 445, 1433, 3389]
        
        if conn.dest_port in suspicious_ports:
            return True
        
        # 检查是否来自可疑IP
        if self.is_private_ip(conn.source_ip) and not self.is_private_ip(conn.dest_ip):
            return True
        
        return False
    
    def is_private_ip(self, ip: str) -> bool:
        """判断是否为私有IP"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            first = int(parts[0])
            second = int(parts[1])
            
            # 10.0.0.0/8
            if first == 10:
                return True
            
            # 172.16.0.0/12
            if first == 172 and 16 <= second <= 31:
                return True
            
            # 192.168.0.0/16
            if first == 192 and second == 168:
                return True
            
            return False
            
        except (ValueError, IndexError):
            return False
    
    def assess_network_health(self, connections: List[ConnectionInfo], violations: List[PolicyViolation]) -> Dict[str, Any]:
        """评估网络健康状态"""
        health_score = 100
        
        # 根据违规数量扣分
        health_score -= len(violations) * 10
        
        # 根据连接数量评估
        if len(connections) > 1000:
            health_score -= 20
        elif len(connections) > 500:
            health_score -= 10
        
        # 根据连接状态评估
        failed_connections = len([c for c in connections if 'CLOSE' in c.state or 'TIME_WAIT' in c.state])
        if failed_connections > len(connections) * 0.1:
            health_score -= 15
        
        health_score = max(0, health_score)
        
        status = 'healthy'
        if health_score < 60:
            status = 'unhealthy'
        elif health_score < 80:
            status = 'warning'
        
        return {
            'health_score': health_score,
            'status': status,
            'total_connections': len(connections),
            'violations': len(violations),
            'failed_connections': failed_connections
        }

# 使用示例
def main():
    monitor = NetworkTrafficMonitor('production')
    
    # 监控网络流量
    report = monitor.monitor_network_traffic(30)
    
    print("网络流量监控报告:")
    print(f"活跃连接数: {report['active_connections']}")
    print(f"策略违规数: {report['policy_violations']}")
    print(f"网络健康状态: {report['network_health']['status']}")
    print(f"健康评分: {report['network_health']['health_score']}")

if __name__ == '__main__':
    main()
```

## 网络策略配置最佳实践

### 策略设计原则
1. **最小权限**: 只允许必要的网络通信
2. **默认拒绝**: 默认拒绝所有流量，明确允许需要的
3. **分层防护**: 在不同层级实施网络控制
4. **定期审查**: 定期检查和更新策略规则

### 安全配置
1. **命名空间隔离**: 使用命名空间隔离不同环境
2. **标签管理**: 规范Pod和服务标签使用
3. **端口控制**: 精确控制端口访问权限
4. **协议限制**: 限制不必要的网络协议

### 运维管理
1. **策略测试**: 在测试环境验证策略效果
2. **渐进部署**: 逐步部署新策略避免中断
3. **监控告警**: 实施策略违规监控告警
4. **文档维护**: 保持策略文档的及时更新

### 故障排查
1. **连接测试**: 使用网络工具测试连接
2. **日志分析**: 分析网络策略相关日志
3. **流量分析**: 监控网络流量模式
4. **策略验证**: 验证策略规则正确性

## 相关技能

- **kubernetes-basics** - Kubernetes基础
- **security-audit** - 安全审计
- **microservices** - 微服务架构
- **kubernetes-validator** - Kubernetes验证器
