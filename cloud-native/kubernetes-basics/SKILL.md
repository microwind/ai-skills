---
name: Kubernetes编排
description: "当实施Kubernetes编排时，分析集群架构设计，优化容器编排性能，解决K8s相关问题。验证资源配置，设计服务部署策略，和最佳实践。"
license: MIT
---

# Kubernetes编排技能

## 概述
Kubernetes是容器编排的事实标准。不当的K8s配置会导致资源浪费、性能问题和运维困难。在设计Kubernetes架构前需要仔细分析应用需求。

**核心原则**: 好的Kubernetes编排应该提升应用可用性和可扩展性，同时保证资源利用率。坏的编排会增加运维复杂性，甚至影响服务稳定性。

## 何时使用

**始终:**
- 设计微服务部署架构时
- 实现容器编排和调度时
- 优化Kubernetes集群性能时
- 解决服务发现和负载均衡问题时
- 建立自动化运维流程时

**触发短语:**
- "Kubernetes部署"
- "K8s集群优化"
- "Pod调度策略"
- "服务网格配置"
- "自动扩缩容"
- "Kubernetes安全"

## Kubernetes编排功能

### 集群架构设计
- Master节点配置
- Worker节点规划
- 网络插件选择
- 存储方案设计
- 高可用架构

### 资源管理
- Pod配置优化
- Deployment策略
- Service和Ingress配置
- ConfigMap和Secret管理
- 资源配额设置

### 调度和扩缩容
- 调度策略配置
- 自动扩缩容设置
- 节点亲和性规则
- 污点和容忍度
- 优先级和抢占

### 监控和运维
- 健康检查配置
- 日志收集方案
- 监控指标设置
- 告警规则配置
- 故障排查

## 常见Kubernetes问题

### 资源配置不当
```
问题:
Pod资源配置不合理导致性能问题

错误示例:
- 没有设置资源请求和限制
- CPU和内存配置过高或过低
- 忽略资源使用监控
- 不合理的QoS类别

解决方案:
1. 设置合理的requests和limits
2. 实施资源监控和告警
3. 优化Pod调度策略
4. 配置合适的QoS类别
```

### 网络通信问题
```
问题:
Kubernetes网络配置导致通信故障

错误示例:
- Service无法访问Pod
- Ingress配置错误
- 网络策略阻止通信
- DNS解析失败

解决方案:
1. 检查Service和Endpoint配置
2. 验证Ingress规则设置
3. 调整NetworkPolicy策略
4. 排查CoreDNS问题
```

### 存储挂载问题
```
问题:
持久化存储挂载失败或数据丢失

错误示例:
- PV和PVC配置不匹配
- 存储类选择错误
- 权限配置问题
- 数据备份策略缺失

解决方案:
1. 正确配置PV和PVC
2. 选择合适的StorageClass
3. 设置正确的访问权限
4. 实施定期备份策略
```

## 代码实现示例

### Kubernetes集群分析器
```python
import kubernetes
import yaml
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ClusterMetrics:
    """集群指标"""
    node_count: int
    pod_count: int
    service_count: int
    deployment_count: int
    namespace_count: int
    cpu_capacity: float
    memory_capacity: float
    cpu_usage: float
    memory_usage: float

@dataclass
class PodMetrics:
    """Pod指标"""
    name: str
    namespace: str
    status: str
    node_name: str
    cpu_requests: float
    cpu_limits: float
    memory_requests: float
    memory_limits: float
    restart_count: int
    age_seconds: int

@dataclass
class ClusterIssue:
    """集群问题"""
    severity: str  # critical, high, medium, low
    type: str
    resource: str
    namespace: str
    message: str
    suggestion: str

class KubernetesClusterAnalyzer:
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.load_kubernetes_config()
        self.v1 = kubernetes.client.CoreV1Api()
        self.apps_v1 = kubernetes.client.AppsV1Api()
        self.networking_v1 = kubernetes.client.NetworkingV1Api()
        self.issues: List[ClusterIssue] = []
        
    def load_kubernetes_config(self):
        """加载Kubernetes配置"""
        try:
            if self.kubeconfig_path:
                kubernetes.config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                kubernetes.config.load_incluster_config()
        except Exception as e:
            try:
                kubernetes.config.load_kube_config()
            except Exception as e2:
                raise Exception(f'无法加载Kubernetes配置: {e2}')
    
    def analyze_cluster(self) -> Dict[str, Any]:
        """分析整个集群"""
        try:
            # 获取集群指标
            cluster_metrics = self.get_cluster_metrics()
            
            # 分析Pod
            pod_analysis = self.analyze_pods()
            
            # 分析节点
            node_analysis = self.analyze_nodes()
            
            # 分析资源使用
            resource_analysis = self.analyze_resource_usage()
            
            # 分析网络
            network_analysis = self.analyze_network()
            
            # 生成报告
            report = {
                'cluster_metrics': cluster_metrics,
                'pod_analysis': pod_analysis,
                'node_analysis': node_analysis,
                'resource_analysis': resource_analysis,
                'network_analysis': network_analysis,
                'issues': self.issues,
                'recommendations': self.generate_recommendations(),
                'health_score': self.calculate_health_score(cluster_metrics)
            }
            
            return report
            
        except Exception as e:
            return {'error': f'分析集群失败: {e}'}
    
    def get_cluster_metrics(self) -> ClusterMetrics:
        """获取集群指标"""
        try:
            # 获取节点数量
            nodes = self.v1.list_node()
            node_count = len(nodes.items)
            
            # 获取Pod数量
            pods = self.v1.list_pod_for_all_namespaces()
            pod_count = len(pods.items)
            
            # 获取Service数量
            services = self.v1.list_service_for_all_namespaces()
            service_count = len(services.items)
            
            # 获取Deployment数量
            deployments = self.apps_v1.list_deployment_for_all_namespaces()
            deployment_count = len(deployments.items)
            
            # 获取Namespace数量
            namespaces = self.v1.list_namespace()
            namespace_count = len(namespaces.items)
            
            # 计算资源容量
            cpu_capacity = 0
            memory_capacity = 0
            for node in nodes.items:
                cpu_capacity += self.parse_cpu(node.status.capacity.get('cpu', '0'))
                memory_capacity += self.parse_memory(node.status.capacity.get('memory', '0'))
            
            return ClusterMetrics(
                node_count=node_count,
                pod_count=pod_count,
                service_count=service_count,
                deployment_count=deployment_count,
                namespace_count=namespace_count,
                cpu_capacity=cpu_capacity,
                memory_capacity=memory_capacity,
                cpu_usage=0,  # 需要通过metrics server获取
                memory_usage=0
            )
            
        except Exception as e:
            raise Exception(f'获取集群指标失败: {e}')
    
    def analyze_pods(self) -> Dict[str, Any]:
        """分析Pod状态"""
        try:
            pods = self.v1.list_pod_for_all_namespaces()
            pod_metrics = []
            
            status_counts = defaultdict(int)
            namespace_counts = defaultdict(int)
            
            for pod in pods.items:
                # 获取Pod指标
                metrics = self.get_pod_metrics(pod)
                pod_metrics.append(metrics)
                
                # 统计状态
                status_counts[pod.status.phase] += 1
                namespace_counts[pod.metadata.namespace] += 1
                
                # 检查Pod问题
                self.check_pod_issues(pod, metrics)
            
            return {
                'total_pods': len(pods.items),
                'status_distribution': dict(status_counts),
                'namespace_distribution': dict(namespace_counts),
                'pod_metrics': pod_metrics,
                'issues': [issue for issue in self.issues if issue.type.startswith('pod_')]
            }
            
        except Exception as e:
            return {'error': f'分析Pod失败: {e}'}
    
    def get_pod_metrics(self, pod) -> PodMetrics:
        """获取Pod指标"""
        try:
            # 解析资源请求和限制
            cpu_requests = 0
            cpu_limits = 0
            memory_requests = 0
            memory_limits = 0
            
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if container.resources:
                        if container.resources.requests:
                            cpu_requests += self.parse_cpu(container.resources.requests.get('cpu', '0'))
                            memory_requests += self.parse_memory(container.resources.requests.get('memory', '0'))
                        if container.resources.limits:
                            cpu_limits += self.parse_cpu(container.resources.limits.get('cpu', '0'))
                            memory_limits += self.parse_memory(container.resources.limits.get('memory', '0'))
            
            # 计算重启次数
            restart_count = 0
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    restart_count += container_status.restart_count
            
            # 计算Pod年龄
            creation_time = pod.metadata.creation_timestamp
            age_seconds = int((time.time() - creation_time.timestamp()))
            
            return PodMetrics(
                name=pod.metadata.name,
                namespace=pod.metadata.namespace,
                status=pod.status.phase,
                node_name=pod.spec.node_name or '',
                cpu_requests=cpu_requests,
                cpu_limits=cpu_limits,
                memory_requests=memory_requests,
                memory_limits=memory_limits,
                restart_count=restart_count,
                age_seconds=age_seconds
            )
            
        except Exception as e:
            raise Exception(f'获取Pod指标失败: {e}')
    
    def check_pod_issues(self, pod, metrics: PodMetrics) -> None:
        """检查Pod问题"""
        # 检查Pod状态
        if pod.status.phase == 'Pending':
            self.issues.append(ClusterIssue(
                severity='medium',
                type='pod_pending',
                resource=pod.metadata.name,
                namespace=pod.metadata.namespace,
                message='Pod处于Pending状态',
                suggestion='检查资源配额、节点调度或PVC绑定状态'
            ))
        elif pod.status.phase == 'Failed':
            self.issues.append(ClusterIssue(
                severity='high',
                type='pod_failed',
                resource=pod.metadata.name,
                namespace=pod.metadata.namespace,
                message='Pod处于Failed状态',
                suggestion='检查Pod日志和事件，确定失败原因'
            ))
        
        # 检查重启次数
        if metrics.restart_count > 5:
            self.issues.append(ClusterIssue(
                severity='high',
                type='pod_crash_loop',
                resource=pod.metadata.name,
                namespace=pod.metadata.namespace,
                message=f'Pod重启次数过多: {metrics.restart_count}',
                suggestion='检查应用日志，可能存在CrashLoopBackOff问题'
            ))
        
        # 检查资源配置
        if metrics.cpu_requests == 0 or metrics.memory_requests == 0:
            self.issues.append(ClusterIssue(
                severity='medium',
                type='pod_no_requests',
                resource=pod.metadata.name,
                namespace=pod.metadata.namespace,
                message='Pod没有设置资源请求',
                suggestion='设置CPU和内存请求以确保调度稳定性'
            ))
        
        if metrics.cpu_limits == 0 or metrics.memory_limits == 0:
            self.issues.append(ClusterIssue(
                severity='low',
                type='pod_no_limits',
                resource=pod.metadata.name,
                namespace=pod.metadata.namespace,
                message='Pod没有设置资源限制',
                suggestion='设置资源限制防止资源耗尽'
            ))
    
    def analyze_nodes(self) -> Dict[str, Any]:
        """分析节点状态"""
        try:
            nodes = self.v1.list_node()
            node_analysis = []
            
            for node in nodes.items:
                analysis = {
                    'name': node.metadata.name,
                    'status': self.get_node_status(node),
                    'roles': self.get_node_roles(node),
                    'capacity': node.status.capacity,
                    'allocatable': node.status.allocatable,
                    'conditions': node.status.conditions,
                    'issues': []
                }
                
                # 检查节点问题
                for condition in node.status.conditions or []:
                    if condition.type == 'Ready' and condition.status != 'True':
                        analysis['issues'].append({
                            'severity': 'high',
                            'message': f'节点{node.metadata.name}不可用',
                            'suggestion': '检查节点状态和网络连接'
                        })
                
                node_analysis.append(analysis)
            
            return {
                'total_nodes': len(nodes.items),
                'nodes': node_analysis,
                'ready_nodes': len([n for n in node_analysis if n['status'] == 'Ready'])
            }
            
        except Exception as e:
            return {'error': f'分析节点失败: {e}'}
    
    def get_node_status(self, node) -> str:
        """获取节点状态"""
        for condition in node.status.conditions or []:
            if condition.type == 'Ready':
                return 'Ready' if condition.status == 'True' else 'NotReady'
        return 'Unknown'
    
    def get_node_roles(self, node) -> List[str]:
        """获取节点角色"""
        roles = []
        labels = node.metadata.labels or {}
        
        for label in labels:
            if label.startswith('node-role.kubernetes.io/'):
                role = label.replace('node-role.kubernetes.io/', '')
                if role:
                    roles.append(role)
        
        return roles or ['worker']
    
    def analyze_resource_usage(self) -> Dict[str, Any]:
        """分析资源使用情况"""
        try:
            # 这里需要metrics-server支持
            # 简化实现，返回基本信息
            return {
                'message': '需要安装metrics-server获取详细资源使用信息',
                'recommendation': '请安装metrics-server: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml'
            }
            
        except Exception as e:
            return {'error': f'分析资源使用失败: {e}'}
    
    def analyze_network(self) -> Dict[str, Any]:
        """分析网络配置"""
        try:
            # 获取所有Service
            services = self.v1.list_service_for_all_namespaces()
            service_analysis = []
            
            for service in services.items:
                analysis = {
                    'name': service.metadata.name,
                    'namespace': service.metadata.namespace,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip,
                    'external_ips': service.spec.external_i_ps or [],
                    'ports': service.spec.ports or [],
                    'selector': service.spec.selector or {},
                    'issues': []
                }
                
                # 检查Service问题
                if service.spec.type == 'LoadBalancer' and not service.spec.cluster_ip:
                    analysis['issues'].append({
                        'severity': 'medium',
                        'message': 'LoadBalancer Service没有分配IP',
                        'suggestion': '检查云提供商配置或网络策略'
                    })
                
                if service.spec.selector and not service.spec.selector:
                    analysis['issues'].append({
                        'severity': 'low',
                        'message': 'Service没有选择器',
                        'suggestion': '添加选择器或将Service类型改为ExternalName'
                    })
                
                service_analysis.append(analysis)
            
            # 获取Ingress
            try:
                ingresses = self.networking_v1.list_ingress_for_all_namespaces()
                ingress_analysis = []
                
                for ingress in ingresses.items:
                    analysis = {
                        'name': ingress.metadata.name,
                        'namespace': ingress.metadata.namespace,
                        'rules': ingress.spec.rules or [],
                        'tls': ingress.spec.tls or [],
                        'backend': ingress.spec.backend,
                        'issues': []
                    }
                    
                    ingress_analysis.append(analysis)
            except:
                ingress_analysis = []
            
            return {
                'total_services': len(services.items),
                'services': service_analysis,
                'total_ingresses': len(ingress_analysis) if ingress_analysis else 0,
                'ingresses': ingress_analysis
            }
            
        except Exception as e:
            return {'error': f'分析网络失败: {e}'}
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 基于问题生成建议
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue.type] += 1
        
        if issue_counts['pod_pending'] > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'scheduling',
                'message': f'{issue_counts["pod_pending"]}个Pod处于Pending状态',
                'suggestion': '检查集群资源可用性和调度配置'
            })
        
        if issue_counts['pod_failed'] > 0:
            recommendations.append({
                'priority': 'critical',
                'type': 'reliability',
                'message': f'{issue_counts["pod_failed"]}个Pod处于Failed状态',
                'suggestion': '检查Pod日志和事件，修复应用问题'
            })
        
        if issue_counts['pod_no_requests'] > 5:
            recommendations.append({
                'priority': 'medium',
                'type': 'resource_management',
                'message': f'{issue_counts["pod_no_requests"]}个Pod没有设置资源请求',
                'suggestion': '为所有Pod设置资源请求确保调度稳定性'
            })
        
        return recommendations
    
    def calculate_health_score(self, metrics: ClusterMetrics) -> int:
        """计算集群健康评分"""
        score = 100
        
        # 根据问题扣分
        for issue in self.issues:
            if issue.severity == 'critical':
                score -= 20
            elif issue.severity == 'high':
                score -= 10
            elif issue.severity == 'medium':
                score -= 5
            elif issue.severity == 'low':
                score -= 2
        
        # 根据节点状态调整
        if metrics.node_count == 0:
            score = 0
        
        return max(0, int(score))
    
    def parse_cpu(self, cpu_str: str) -> float:
        """解析CPU字符串"""
        if not cpu_str:
            return 0
        
        cpu_str = cpu_str.lower()
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        else:
            return float(cpu_str)
    
    def parse_memory(self, memory_str: str) -> int:
        """解析内存字符串"""
        if not memory_str:
            return 0
        
        memory_str = memory_str.upper()
        if memory_str.endswith('KI'):
            return int(memory_str[:-2]) * 1024
        elif memory_str.endswith('MI'):
            return int(memory_str[:-2]) * 1024 * 1024
        elif memory_str.endswith('GI'):
            return int(memory_str[:-2]) * 1024 * 1024 * 1024
        elif memory_str.endswith('K'):
            return int(memory_str[:-1]) * 1000
        elif memory_str.endswith('M'):
            return int(memory_str[:-1]) * 1000 * 1000
        elif memory_str.endswith('G'):
            return int(memory_str[:-1]) * 1000 * 1000 * 1000
        else:
            return int(memory_str)

# Kubernetes部署优化器
class KubernetesDeploymentOptimizer:
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.load_kubernetes_config()
        self.apps_v1 = kubernetes.client.AppsV1Api()
        self.v1 = kubernetes.client.CoreV1Api()
        
    def load_kubernetes_config(self):
        """加载Kubernetes配置"""
        try:
            if self.kubeconfig_path:
                kubernetes.config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                kubernetes.config.load_incluster_config()
        except Exception as e:
            try:
                kubernetes.config.load_kube_config()
            except Exception as e2:
                raise Exception(f'无法加载Kubernetes配置: {e2}')
    
    def optimize_deployment(self, namespace: str, deployment_name: str) -> Dict[str, Any]:
        """优化Deployment配置"""
        try:
            # 获取当前Deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # 分析当前配置
            current_analysis = self.analyze_deployment_config(deployment)
            
            # 生成优化建议
            optimization_plan = self.generate_deployment_optimizations(deployment)
            
            # 生成优化后的配置
            optimized_deployment = self.generate_optimized_deployment(deployment, optimization_plan)
            
            return {
                'namespace': namespace,
                'deployment_name': deployment_name,
                'current_analysis': current_analysis,
                'optimization_plan': optimization_plan,
                'optimized_deployment': optimized_deployment,
                'estimated_improvements': self.estimate_deployment_improvements(deployment, optimized_deployment)
            }
            
        except Exception as e:
            return {'error': f'优化Deployment失败: {e}'}
    
    def analyze_deployment_config(self, deployment) -> Dict[str, Any]:
        """分析Deployment配置"""
        analysis = {
            'replicas': deployment.spec.replicas,
            'strategy': deployment.spec.strategy.type if deployment.spec.strategy else 'RollingUpdate',
            'pod_template': {
                'containers': []
            },
            'issues': []
        }
        
        # 分析容器配置
        if deployment.spec.template.spec.containers:
            for container in deployment.spec.template.spec.containers:
                container_analysis = {
                    'name': container.name,
                    'image': container.image,
                    'resources': {
                        'requests': container.resources.requests if container.resources else {},
                        'limits': container.resources.limits if container.resources else {}
                    },
                    'ports': container.ports or [],
                    'env_vars': len(container.env or []),
                    'volume_mounts': len(container.volume_mounts or []),
                    'liveness_probe': container.liveness_probe is not None,
                    'readiness_probe': container.readiness_probe is not None,
                    'startup_probe': container.startup_probe is not None
                }
                
                # 检查容器问题
                if not container.resources:
                    analysis['issues'].append({
                        'container': container.name,
                        'severity': 'high',
                        'message': '容器没有设置资源配置',
                        'suggestion': '设置CPU和内存的requests和limits'
                    })
                elif not container.resources.requests:
                    analysis['issues'].append({
                        'container': container.name,
                        'severity': 'medium',
                        'message': '容器没有设置资源请求',
                        'suggestion': '设置CPU和内存的requests'
                    })
                
                if not container.liveness_probe:
                    analysis['issues'].append({
                        'container': container.name,
                        'severity': 'medium',
                        'message': '容器没有设置存活探针',
                        'suggestion': '添加livenessProbe检测容器健康状态'
                    })
                
                if not container.readiness_probe:
                    analysis['issues'].append({
                        'container': container.name,
                        'severity': 'medium',
                        'message': '容器没有设置就绪探针',
                        'suggestion': '添加readinessProbe检测服务就绪状态'
                    })
                
                analysis['pod_template']['containers'].append(container_analysis)
        
        return analysis
    
    def generate_deployment_optimizations(self, deployment) -> List[Dict[str, Any]]:
        """生成Deployment优化建议"""
        optimizations = []
        
        # 检查副本数
        if deployment.spec.replicas == 1:
            optimizations.append({
                'type': 'availability',
                'priority': 'high',
                'message': '副本数为1，存在单点故障风险',
                'suggestion': '增加副本数提高可用性',
                'recommended_value': 3
            })
        
        # 检查更新策略
        if not deployment.spec.strategy or deployment.spec.strategy.type == 'RollingUpdate':
            strategy = deployment.spec.strategy
            if strategy and strategy.rolling_update:
                max_unavailable = strategy.rolling_update.max_unavailable
                max_surge = strategy.rolling_update.max_surge
                
                if not max_unavailable or max_unavailable == '25%':
                    optimizations.append({
                        'type': 'update_strategy',
                        'priority': 'medium',
                        'message': '使用默认的滚动更新配置',
                        'suggestion': '根据业务需求调整maxUnavailable和maxSurge'
                    })
        
        # 检查镜像版本
        if deployment.spec.template.spec.containers:
            for container in deployment.spec.template.spec.containers:
                if ':latest' in container.image:
                    optimizations.append({
                        'type': 'image_management',
                        'priority': 'high',
                        'message': f'容器{container.name}使用latest标签',
                        'suggestion': '使用具体的镜像版本标签确保部署一致性'
                    })
        
        return optimizations
    
    def generate_optimized_deployment(self, original_deployment, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成优化后的Deployment配置"""
        optimized_deployment = original_deployment
        
        # 应用优化建议
        for optimization in optimizations:
            if optimization['type'] == 'availability' and optimization.get('recommended_value'):
                optimized_deployment.spec.replicas = optimization['recommended_value']
            
            elif optimization['type'] == 'update_strategy':
                if not optimized_deployment.spec.strategy:
                    optimized_deployment.spec.strategy = kubernetes.client.V1DeploymentStrategy(
                        type='RollingUpdate',
                        rolling_update=kubernetes.client.V1RollingUpdateDeployment(
                            max_unavailable='1',
                            max_surge='1'
                        )
                    )
        
        return optimized_deployment
    
    def estimate_deployment_improvements(self, original, optimized) -> Dict[str, Any]:
        """估算改进效果"""
        improvements = {
            'availability_score': 0,
            'stability_score': 0,
            'maintainability_score': 0,
            'overall_score': 0
        }
        
        # 可用性改进
        if original.spec.replicas == 1 and optimized.spec.replicas > 1:
            improvements['availability_score'] += 40
        
        # 稳定性改进
        if optimized.spec.template.spec.containers:
            for container in optimized.spec.template.spec.containers:
                if container.resources and container.resources.requests:
                    improvements['stability_score'] += 20
        
        # 可维护性改进
        if optimized.spec.template.spec.containers:
            for container in optimized.spec.template.spec.containers:
                if ':latest' not in container.image:
                    improvements['maintainability_score'] += 15
        
        # 计算总体改进
        improvements['overall_score'] = (
            improvements['availability_score'] + 
            improvements['stability_score'] + 
            improvements['maintainability_score']
        ) // 3
        
        return improvements

# 使用示例
def main():
    # 集群分析
    analyzer = KubernetesClusterAnalyzer()
    cluster_report = analyzer.analyze_cluster()
    
    print("Kubernetes集群分析报告:")
    print(f"节点数: {cluster_report['cluster_metrics'].node_count}")
    print(f"Pod数: {cluster_report['cluster_metrics'].pod_count}")
    print(f"健康评分: {cluster_report['health_score']}")
    
    # Deployment优化
    optimizer = KubernetesDeploymentOptimizer()
    deployment_optimization = optimizer.optimize_deployment('default', 'my-app')
    
    print(f"\nDeployment优化建议:")
    for opt in deployment_optimization['optimization_plan']:
        print(f"- {opt['message']}: {opt['suggestion']}")

if __name__ == '__main__':
    main()
```

### Kubernetes资源管理器
```python
import kubernetes
import yaml
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class KubernetesResourceManager:
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.load_kubernetes_config()
        self.v1 = kubernetes.client.CoreV1Api()
        self.apps_v1 = kubernetes.client.AppsV1Api()
        self.networking_v1 = kubernetes.client.NetworkingV1Api()
        
    def load_kubernetes_config(self):
        """加载Kubernetes配置"""
        try:
            if self.kubeconfig_path:
                kubernetes.config.load_kube_config(config_file=self.kubeconfig_path)
            else:
                kubernetes.config.load_incluster_config()
        except Exception as e:
            try:
                kubernetes.config.load_kube_config()
            except Exception as e2:
                raise Exception(f'无法加载Kubernetes配置: {e2}')
    
    def create_resource_from_yaml(self, yaml_file: str, namespace: str = 'default') -> Dict[str, Any]:
        """从YAML文件创建资源"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml_content = yaml.safe_load_all(f)
            
            created_resources = []
            
            for resource_dict in yaml_content:
                if not resource_dict:
                    continue
                
                # 根据资源类型创建相应的资源
                resource_kind = resource_dict.get('kind')
                resource_name = resource_dict.get('metadata', {}).get('name', '')
                
                if resource_kind == 'Deployment':
                    deployment = self.create_deployment_from_dict(resource_dict, namespace)
                    created_resources.append({
                        'type': 'Deployment',
                        'name': resource_name,
                        'namespace': namespace,
                        'status': 'created'
                    })
                
                elif resource_kind == 'Service':
                    service = self.create_service_from_dict(resource_dict, namespace)
                    created_resources.append({
                        'type': 'Service',
                        'name': resource_name,
                        'namespace': namespace,
                        'status': 'created'
                    })
                
                elif resource_kind == 'ConfigMap':
                    configmap = self.create_configmap_from_dict(resource_dict, namespace)
                    created_resources.append({
                        'type': 'ConfigMap',
                        'name': resource_name,
                        'namespace': namespace,
                        'status': 'created'
                    })
                
                elif resource_kind == 'Secret':
                    secret = self.create_secret_from_dict(resource_dict, namespace)
                    created_resources.append({
                        'type': 'Secret',
                        'name': resource_name,
                        'namespace': namespace,
                        'status': 'created'
                    })
            
            return {
                'created_resources': created_resources,
                'total_created': len(created_resources),
                'namespace': namespace
            }
            
        except Exception as e:
            return {'error': f'创建资源失败: {e}'}
    
    def create_deployment_from_dict(self, deployment_dict: Dict, namespace: str):
        """从字典创建Deployment"""
        deployment = kubernetes.client.V1Deployment(
            api_version='apps/v1',
            kind='Deployment',
            metadata=kubernetes.client.V1ObjectMeta(
                name=deployment_dict['metadata']['name'],
                namespace=namespace,
                labels=deployment_dict['metadata'].get('labels', {})
            ),
            spec=kubernetes.client.V1DeploymentSpec(
                replicas=deployment_dict['spec'].get('replicas', 1),
                selector=kubernetes.client.V1LabelSelector(
                    match_labels=deployment_dict['spec']['selector']['match_labels']
                ),
                template=self.create_pod_template_from_dict(deployment_dict['spec']['template'])
            )
        )
        
        return self.apps_v1.create_namespaced_deployment(
            namespace=namespace,
            body=deployment
        )
    
    def create_pod_template_from_dict(self, template_dict: Dict) -> kubernetes.client.V1PodTemplateSpec:
        """从字典创建Pod模板"""
        containers = []
        
        for container_dict in template_dict['spec']['containers']:
            container = kubernetes.client.V1Container(
                name=container_dict['name'],
                image=container_dict['image'],
                ports=[
                    kubernetes.client.V1ContainerPort(
                        container_port=port['containerPort'],
                        protocol=port.get('protocol', 'TCP')
                    ) for port in container_dict.get('ports', [])
                ],
                env=[
                    kubernetes.client.V1EnvVar(
                        name=env['name'],
                        value=env.get('value'),
                        value_from=env.get('valueFrom')
                    ) for env in container_dict.get('env', [])
                ],
                resources=self.create_resource_requirements_from_dict(
                    container_dict.get('resources', {})
                ) if 'resources' in container_dict else None,
                liveness_probe=self.create_probe_from_dict(
                    container_dict.get('livenessProbe', {})
                ) if 'livenessProbe' in container_dict else None,
                readiness_probe=self.create_probe_from_dict(
                    container_dict.get('readinessProbe', {})
                ) if 'readinessProbe' in container_dict else None
            )
            containers.append(container)
        
        return kubernetes.client.V1PodTemplateSpec(
            metadata=kubernetes.client.V1ObjectMeta(
                labels=template_dict['metadata'].get('labels', {}),
                annotations=template_dict['metadata'].get('annotations', {})
            ),
            spec=kubernetes.client.V1PodSpec(
                containers=containers,
                restart_policy=template_dict['spec'].get('restartPolicy', 'Always')
            )
        )
    
    def create_resource_requirements_from_dict(self, resources_dict: Dict) -> kubernetes.client.V1ResourceRequirements:
        """从字典创建资源需求"""
        return kubernetes.client.V1ResourceRequirements(
            requests=resources_dict.get('requests', {}),
            limits=resources_dict.get('limits', {})
        )
    
    def create_probe_from_dict(self, probe_dict: Dict) -> kubernetes.client.V1Probe:
        """从字典创建探针"""
        return kubernetes.client.V1Probe(
            http_get=kubernetes.client.V1HTTPGetAction(
                path=probe_dict.get('httpGet', {}).get('path', '/'),
                port=probe_dict.get('httpGet', {}).get('port', 80)
            ) if 'httpGet' in probe_dict else None,
            tcp_socket=kubernetes.client.V1TCPSocketAction(
                port=probe_dict.get('tcpSocket', {}).get('port', 80)
            ) if 'tcpSocket' in probe_dict else None,
            initial_delay_seconds=probe_dict.get('initialDelaySeconds', 30),
            period_seconds=probe_dict.get('periodSeconds', 10),
            timeout_seconds=probe_dict.get('timeoutSeconds', 5),
            failure_threshold=probe_dict.get('failureThreshold', 3)
        )
    
    def create_service_from_dict(self, service_dict: Dict, namespace: str):
        """从字典创建Service"""
        service = kubernetes.client.V1Service(
            api_version='v1',
            kind='Service',
            metadata=kubernetes.client.V1ObjectMeta(
                name=service_dict['metadata']['name'],
                namespace=namespace,
                labels=service_dict['metadata'].get('labels', {})
            ),
            spec=kubernetes.client.V1ServiceSpec(
                type=service_dict['spec'].get('type', 'ClusterIP'),
                selector=service_dict['spec'].get('selector', {}),
                ports=[
                    kubernetes.client.V1ServicePort(
                        port=port['port'],
                        target_port=port.get('targetPort', port['port']),
                        protocol=port.get('protocol', 'TCP')
                    ) for port in service_dict['spec']['ports']
                ]
            )
        )
        
        return self.v1.create_namespaced_service(
            namespace=namespace,
            body=service
        )
    
    def create_configmap_from_dict(self, configmap_dict: Dict, namespace: str):
        """从字典创建ConfigMap"""
        configmap = kubernetes.client.V1ConfigMap(
            api_version='v1',
            kind='ConfigMap',
            metadata=kubernetes.client.V1ObjectMeta(
                name=configmap_dict['metadata']['name'],
                namespace=namespace,
                labels=configmap_dict['metadata'].get('labels', {})
            ),
            data=configmap_dict.get('data', {}),
            binary_data=configmap_dict.get('binaryData', {})
        )
        
        return self.v1.create_namespaced_config_map(
            namespace=namespace,
            body=configmap
        )
    
    def create_secret_from_dict(self, secret_dict: Dict, namespace: str):
        """从字典创建Secret"""
        import base64
        
        # 编码敏感数据
        data = {}
        if 'data' in secret_dict:
            for key, value in secret_dict['data'].items():
                if isinstance(value, str):
                    data[key] = base64.b64encode(value.encode()).decode()
                else:
                    data[key] = value
        
        secret = kubernetes.client.V1Secret(
            api_version='v1',
            kind='Secret',
            metadata=kubernetes.client.V1ObjectMeta(
                name=secret_dict['metadata']['name'],
                namespace=namespace,
                labels=secret_dict['metadata'].get('labels', {})
            ),
            type=secret_dict.get('type', 'Opaque'),
            data=data,
            string_data=secret_dict.get('stringData', {})
        )
        
        return self.v1.create_namespaced_secret(
            namespace=namespace,
            body=secret
        )
    
    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int) -> Dict[str, Any]:
        """扩缩容Deployment"""
        try:
            # 获取当前Deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # 更新副本数
            deployment.spec.replicas = replicas
            
            # 应用更新
            updated_deployment = self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            return {
                'deployment_name': deployment_name,
                'namespace': namespace,
                'old_replicas': deployment.spec.replicas,
                'new_replicas': replicas,
                'status': 'scaled'
            }
            
        except Exception as e:
            return {'error': f'扩缩容失败: {e}'}
    
    def restart_deployment(self, namespace: str, deployment_name: str) -> Dict[str, Any]:
        """重启Deployment"""
        try:
            # 获取当前Deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # 通过更新注解触发重启
            if deployment.spec.template.metadata is None:
                deployment.spec.template.metadata = kubernetes.client.V1ObjectMeta()
            
            deployment.spec.template.metadata.annotations = {
                'kubectl.kubernetes.io/restartedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            # 应用更新
            updated_deployment = self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            return {
                'deployment_name': deployment_name,
                'namespace': namespace,
                'status': 'restarted',
                'restart_time': time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
        except Exception as e:
            return {'error': f'重启失败: {e}'}

# 使用示例
def main():
    resource_manager = KubernetesResourceManager()
    
    # 从YAML文件创建资源
    result = resource_manager.create_resource_from_yaml('deployment.yaml')
    print(f"创建资源结果: {result}")
    
    # 扩缩容Deployment
    scale_result = resource_manager.scale_deployment('default', 'my-app', 5)
    print(f"扩缩容结果: {scale_result}")
    
    # 重启Deployment
    restart_result = resource_manager.restart_deployment('default', 'my-app')
    print(f"重启结果: {restart_result}")

if __name__ == '__main__':
    main()
```

## Kubernetes编排最佳实践

### 集群设计
1. **高可用架构**: Master节点多副本部署
2. **节点规划**: 合理规划Master和Worker节点
3. **网络选择**: 选择合适的CNI插件
4. **存储方案**: 设计持久化存储策略
5. **安全隔离**: 实施网络和命名空间隔离

### 资源管理
1. **资源配额**: 设置合理的requests和limits
2. **QoS类别**: 明确服务质量等级
3. **命名空间**: 使用命名空间隔离资源
4. **标签管理**: 规范标签使用策略
5. **资源监控**: 实施全面的资源监控

### 部署策略
1. **滚动更新**: 使用零停机更新策略
2. **蓝绿部署**: 实现快速回滚机制
3. **金丝雀发布**: 渐进式发布验证
4. **健康检查**: 配置完善的探针
5. **自动扩缩**: 根据负载自动调整

### 运维管理
1. **日志收集**: 集中化日志管理
2. **监控告警**: 全方位监控体系
3. **备份策略**: 定期备份关键数据
4. **故障恢复**: 制定应急响应预案
5. **安全加固**: 实施安全最佳实践

## 相关技能

- **docker-containerization** - Docker容器化
- **container-registry** - 容器镜像管理
- **microservices** - 微服务架构
- **service-mesh** - 服务网格
