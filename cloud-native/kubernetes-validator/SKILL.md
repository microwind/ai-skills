---
name: Kubernetes验证器
description: "当验证Kubernetes配置时，分析YAML清单语法，检查资源定义规范，验证部署配置。验证集群资源，设计安全策略，和最佳实践。"
license: MIT
---

# Kubernetes验证器技能

## 概述
Kubernetes配置验证是确保部署成功的关键步骤。无效的Kubernetes清单会静默部署然后神秘失败。在部署前进行全面验证可以避免生产环境问题。

**核心原则**: 好的配置验证应该覆盖语法、语义和最佳实践，确保部署的稳定性和安全性。坏的配置会导致部署失败、资源浪费和安全风险。

## 何时使用

**始终:**
- 部署到Kubernetes集群之前
- 验证YAML清单文件时
- 检查资源配置定义时
- 调试Pod启动失败时
- 规划资源限制策略时
- 审查部署配置时

**触发短语:**
- "这个Kubernetes配置有效吗？"
- "验证K8s清单文件"
- "检查Pod定义"
- "审查部署配置"
- "为什么无法部署？"
- "验证服务网格配置"

## Kubernetes验证功能

### YAML语法验证
- 语法结构检查
- 必填字段验证
- 数据类型验证
- 嵌套结构检查

### 资源定义验证
- API版本检查
- 资源规格验证
- 字段完整性检查
- 引用关系验证

### 最佳实践检查
- 资源限制设置
- 健康检查配置
- 安全策略验证
- 镜像拉取策略检查

### 配置分析
- 服务发现配置
- 存储挂载验证
- 环境变量检查
- 密钥管理验证

## 常见Kubernetes配置问题

### 缺失资源限制
```
问题:
Pod没有设置CPU和内存限制

错误示例:
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: nginx
    # 没有resources字段

后果:
- Pod可能耗尽所有可用资源
- 影响其他Pod正常运行
- 集群变得不稳定

解决方案:
1. 设置resources.requests确保调度
2. 设置resources.limits防止资源耗尽
3. 根据应用特点合理配置
4. 监控资源使用情况并调整
```

### 缺失健康检查
```
问题:
Deployment没有配置存活性和就绪性探针

错误示例:
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        image: nginx
        # 没有livenessProbe和readinessProbe

后果:
- 故障Pod仍被标记为健康
- 流量被发送到故障Pod
- 用户体验差

解决方案:
1. 配置livenessProbe检测容器健康
2. 配置readinessProbe检测服务就绪
3. 设置合适的检查间隔和阈值
4. 配置startupProbe处理启动慢的应用
```

### 镜像配置错误
```
问题:
镜像不存在或仓库地址错误

错误示例:
spec:
  containers:
  - name: app
    image: nonexistent/app:latest  # 镜像不存在

后果:
- Pod无法启动
- ImagePullBackOff错误
- 服务不可用

解决方案:
1. 验证镜像在仓库中存在
2. 使用正确的仓库地址和命名空间
3. 避免使用latest标签
4. 配置正确的镜像拉取策略
```

### 安全配置不当
```
问题:
容器以特权模式运行或使用root用户

错误示例:
spec:
  containers:
  - name: app
    securityContext:
      privileged: true  # 特权模式
      runAsUser: 0      # root用户

后果:
- 容器获得主机权限
- 安全风险增加
- 可能影响主机稳定性

解决方案:
1. 避免使用特权模式
2. 使用非root用户运行
3. 配置只读根文件系统
4. 限制Linux capabilities
```

## 代码实现示例

### Kubernetes配置验证器
```python
import yaml
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ValidationIssue:
    """验证问题"""
    severity: str  # critical, high, medium, low
    type: str
    resource: str
    field: str
    message: str
    suggestion: str
    line_number: Optional[int] = None

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    issues: List[ValidationIssue]
    warnings: List[ValidationIssue]
    summary: Dict[str, Any]

class KubernetesConfigValidator:
    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.warnings: List[ValidationIssue] = []
        
        # Kubernetes资源必填字段定义
        self.required_fields = {
            'Pod': {
                'apiVersion': True,
                'kind': True,
                'metadata': True,
                'spec': True,
                'spec.containers': True
            },
            'Deployment': {
                'apiVersion': True,
                'kind': True,
                'metadata': True,
                'spec': True,
                'spec.selector': True,
                'spec.template': True
            },
            'Service': {
                'apiVersion': True,
                'kind': True,
                'metadata': True,
                'spec': True,
                'spec.selector': True,
                'spec.ports': True
            }
        }
        
        # 最佳实践规则
        self.best_practice_rules = {
            'resource_limits': 'medium',
            'health_checks': 'medium',
            'image_tag': 'low',
            'security_context': 'high',
            'replicas': 'medium'
        }
    
    def validate_yaml_file(self, file_path: str) -> ValidationResult:
        """验证YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.validate_yaml_content(content, file_path)
            
        except FileNotFoundError:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='file_error',
                resource='',
                field='',
                message=f'文件不存在: {file_path}',
                suggestion='检查文件路径是否正确'
            ))
            return self._generate_result()
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='file_error',
                resource='',
                field='',
                message=f'读取文件失败: {e}',
                suggestion='检查文件权限和格式'
            ))
            return self._generate_result()
    
    def validate_yaml_content(self, content: str, file_name: str = '') -> ValidationResult:
        """验证YAML内容"""
        try:
            # 重置问题列表
            self.issues = []
            self.warnings = []
            
            # 解析YAML
            documents = yaml.safe_load_all(content)
            
            for doc in documents:
                if doc is None:
                    continue
                
                # 验证单个文档
                self.validate_document(doc, file_name)
            
            return self._generate_result()
            
        except yaml.YAMLError as e:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='syntax_error',
                resource='',
                field='',
                message=f'YAML语法错误: {e}',
                suggestion='检查YAML语法，注意缩进和格式'
            ))
            return self._generate_result()
    
    def validate_document(self, doc: Dict[str, Any], file_name: str) -> None:
        """验证单个文档"""
        if not isinstance(doc, dict):
            self.issues.append(ValidationIssue(
                severity='critical',
                type='structure_error',
                resource='',
                field='',
                message='文档必须是字典类型',
                suggestion='检查YAML文档结构'
            ))
            return
        
        # 获取资源类型
        kind = doc.get('kind', '')
        api_version = doc.get('apiVersion', '')
        
        if not kind:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='missing_field',
                resource='',
                field='kind',
                message='缺少kind字段',
                suggestion='添加资源类型，如Pod、Deployment等'
            ))
            return
        
        # 验证必填字段
        self.validate_required_fields(doc, kind)
        
        # 验证特定资源类型
        if kind == 'Pod':
            self.validate_pod(doc)
        elif kind == 'Deployment':
            self.validate_deployment(doc)
        elif kind == 'Service':
            self.validate_service(doc)
        
        # 验证最佳实践
        self.validate_best_practices(doc, kind)
    
    def validate_required_fields(self, doc: Dict[str, Any], kind: str) -> None:
        """验证必填字段"""
        required = self.required_fields.get(kind, {})
        
        for field, is_required in required.items():
            if is_required:
                value = self.get_nested_field(doc, field)
                if value is None:
                    self.issues.append(ValidationIssue(
                        severity='critical',
                        type='missing_field',
                        resource=kind,
                        field=field,
                        message=f'缺少必填字段: {field}',
                        suggestion=f'添加{field}字段'
                    ))
    
    def get_nested_field(self, doc: Dict[str, Any], field_path: str) -> Any:
        """获取嵌套字段值"""
        keys = field_path.split('.')
        value = doc
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def validate_pod(self, doc: Dict[str, Any]) -> None:
        """验证Pod配置"""
        spec = doc.get('spec', {})
        containers = spec.get('containers', [])
        
        if not containers:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='missing_field',
                resource='Pod',
                field='spec.containers',
                message='Pod必须包含至少一个容器',
                suggestion='添加容器配置'
            ))
            return
        
        for i, container in enumerate(containers):
            container_name = container.get('name', f'container-{i}')
            
            # 验证容器名称
            if not container.get('name'):
                self.issues.append(ValidationIssue(
                    severity='high',
                    type='missing_field',
                    resource='Pod',
                    field=f'spec.containers[{i}].name',
                    message='容器缺少名称',
                    suggestion='为容器设置唯一名称'
                ))
            
            # 验证镜像
            image = container.get('image', '')
            if not image:
                self.issues.append(ValidationIssue(
                    severity='critical',
                    type='missing_field',
                    resource='Pod',
                    field=f'spec.containers[{i}].image',
                    message='容器缺少镜像',
                    suggestion='指定容器镜像'
                ))
            elif ':latest' in image:
                self.warnings.append(ValidationIssue(
                    severity='medium',
                    type='best_practice',
                    resource='Pod',
                    field=f'spec.containers[{i}].image',
                    message='使用latest镜像标签',
                    suggestion='使用具体的版本标签确保部署一致性'
                ))
            
            # 验证资源配置
            resources = container.get('resources', {})
            if not resources:
                self.warnings.append(ValidationIssue(
                    severity='medium',
                    type='best_practice',
                    resource='Pod',
                    field=f'spec.containers[{i}].resources',
                    message='容器没有设置资源配置',
                    suggestion='设置CPU和内存的requests和limits'
                ))
            else:
                # 检查资源请求
                requests = resources.get('requests', {})
                if not requests:
                    self.warnings.append(ValidationIssue(
                        severity='medium',
                        type='best_practice',
                        resource='Pod',
                        field=f'spec.containers[{i}].resources.requests',
                        message='容器没有设置资源请求',
                        suggestion='设置CPU和内存请求以确保调度'
                    ))
                
                # 检查资源限制
                limits = resources.get('limits', {})
                if not limits:
                    self.warnings.append(ValidationIssue(
                        severity='medium',
                        type='best_practice',
                        resource='Pod',
                        field=f'spec.containers[{i}].resources.limits',
                        message='容器没有设置资源限制',
                        suggestion='设置CPU和内存限制防止资源耗尽'
                    ))
            
            # 验证健康检查
            liveness_probe = container.get('livenessProbe')
            readiness_probe = container.get('readinessProbe')
            
            if not liveness_probe and not readiness_probe:
                self.warnings.append(ValidationIssue(
                    severity='medium',
                    type='best_practice',
                    resource='Pod',
                    field=f'spec.containers[{i}].probes',
                    message='容器没有配置健康检查',
                    suggestion='添加livenessProbe和readinessProbe'
                ))
            
            # 验证安全上下文
            security_context = container.get('securityContext', {})
            if security_context.get('privileged', False):
                self.issues.append(ValidationIssue(
                    severity='high',
                    type='security',
                    resource='Pod',
                    field=f'spec.containers[{i}].securityContext.privileged',
                    message='容器以特权模式运行',
                    suggestion='避免使用特权模式，最小化权限'
                ))
            
            if security_context.get('runAsUser') == 0:
                self.warnings.append(ValidationIssue(
                    severity='medium',
                    type='security',
                    resource='Pod',
                    field=f'spec.containers[{i}].securityContext.runAsUser',
                    message='容器以root用户运行',
                    suggestion='使用非root用户运行容器'
                ))
    
    def validate_deployment(self, doc: Dict[str, Any]) -> None:
        """验证Deployment配置"""
        spec = doc.get('spec', {})
        template = spec.get('template', {})
        pod_spec = template.get('spec', {})
        
        # 验证副本数
        replicas = spec.get('replicas', 1)
        if replicas == 1:
            self.warnings.append(ValidationIssue(
                severity='medium',
                type='availability',
                resource='Deployment',
                field='spec.replicas',
                message='副本数为1，存在单点故障风险',
                suggestion='增加副本数提高可用性'
            ))
        
        # 验证选择器匹配
        selector = spec.get('selector', {})
        match_labels = selector.get('matchLabels', {})
        template_labels = template.get('metadata', {}).get('labels', {})
        
        if not match_labels:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='configuration_error',
                resource='Deployment',
                field='spec.selector.matchLabels',
                message='Deployment缺少选择器',
                suggestion='添加matchLabels确保Pod正确关联'
            ))
        
        # 验证标签匹配
        for key, value in match_labels.items():
            if template_labels.get(key) != value:
                self.issues.append(ValidationIssue(
                    severity='critical',
                    type='configuration_error',
                    resource='Deployment',
                    field='spec.template.metadata.labels',
                    message=f'模板标签与选择器不匹配: {key}',
                    suggestion='确保模板标签与选择器匹配'
                ))
        
        # 验证Pod模板
        pod_doc = {
            'kind': 'Pod',
            'spec': pod_spec
        }
        self.validate_pod(pod_doc)
    
    def validate_service(self, doc: Dict[str, Any]) -> None:
        """验证Service配置"""
        spec = doc.get('spec', {})
        selector = spec.get('selector', {})
        ports = spec.get('ports', [])
        
        # 验证端口配置
        if not ports:
            self.issues.append(ValidationIssue(
                severity='critical',
                type='missing_field',
                resource='Service',
                field='spec.ports',
                message='Service缺少端口配置',
                suggestion='添加端口配置'
            ))
        
        # 验证选择器
        service_type = spec.get('type', 'ClusterIP')
        if service_type != 'ExternalName' and not selector:
            self.warnings.append(ValidationIssue(
                severity='medium',
                type='configuration_error',
                resource='Service',
                field='spec.selector',
                message='Service没有选择器',
                suggestion='添加选择器或将Service类型改为ExternalName'
            ))
        
        # 验证端口配置
        for i, port in enumerate(ports):
            if not port.get('port'):
                self.issues.append(ValidationIssue(
                    severity='critical',
                    type='missing_field',
                    resource='Service',
                    field=f'spec.ports[{i}].port',
                    message='端口配置缺少port字段',
                    suggestion='指定服务端口'
                ))
            
            # 检查端口冲突
            target_port = port.get('targetPort', port.get('port'))
            if isinstance(target_port, str) and not target_port.isdigit():
                # 如果是名称端口，需要检查容器是否定义
                pass
    
    def validate_best_practices(self, doc: Dict[str, Any], kind: str) -> None:
        """验证最佳实践"""
        # 验证标签
        metadata = doc.get('metadata', {})
        labels = metadata.get('labels', {})
        
        if not labels:
            self.warnings.append(ValidationIssue(
                severity='low',
                type='best_practice',
                resource=kind,
                field='metadata.labels',
                message='资源没有设置标签',
                suggestion='添加标签便于管理和选择'
            ))
        
        # 验证命名空间
        namespace = metadata.get('namespace', 'default')
        if namespace == 'default' and kind != 'Namespace':
            self.warnings.append(ValidationIssue(
                severity='low',
                type='best_practice',
                resource=kind,
                field='metadata.namespace',
                message='使用default命名空间',
                suggestion='创建专用命名空间隔离资源'
            ))
    
    def _generate_result(self) -> ValidationResult:
        """生成验证结果"""
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        high_issues = [i for i in self.issues if i.severity == 'high']
        
        is_valid = len(critical_issues) == 0 and len(high_issues) == 0
        
        summary = {
            'total_issues': len(self.issues),
            'total_warnings': len(self.warnings),
            'critical_issues': len(critical_issues),
            'high_issues': len(high_issues),
            'medium_issues': len([i for i in self.issues if i.severity == 'medium']),
            'low_issues': len([i for i in self.issues if i.severity == 'low'])
        }
        
        return ValidationResult(
            is_valid=is_valid,
            issues=self.issues,
            warnings=self.warnings,
            summary=summary
        )

# Kubernetes集群验证器
class ClusterResourceValidator:
    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path
        self.load_kubernetes_config()
        self.v1 = kubernetes.client.CoreV1Api()
        self.apps_v1 = kubernetes.client.AppsV1Api()
        
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
    
    def validate_cluster_resources(self, namespace: str = 'default') -> Dict[str, Any]:
        """验证集群资源"""
        validation_results = {
            'namespace': namespace,
            'pods': self.validate_pods(namespace),
            'deployments': self.validate_deployments(namespace),
            'services': self.validate_services(namespace),
            'summary': {}
        }
        
        # 生成摘要
        total_issues = 0
        for resource_type, result in validation_results.items():
            if isinstance(result, dict) and 'issues' in result:
                total_issues += len(result['issues'])
        
        validation_results['summary'] = {
            'total_issues': total_issues,
            'cluster_health': 'healthy' if total_issues == 0 else 'unhealthy'
        }
        
        return validation_results
    
    def validate_pods(self, namespace: str) -> Dict[str, Any]:
        """验证Pod资源"""
        try:
            pods = self.v1.list_namespaced_pod(namespace)
            pod_results = []
            
            for pod in pods.items:
                issues = []
                
                # 检查Pod状态
                if pod.status.phase == 'Pending':
                    issues.append({
                        'severity': 'high',
                        'message': 'Pod处于Pending状态',
                        'suggestion': '检查资源配额或调度问题'
                    })
                elif pod.status.phase == 'Failed':
                    issues.append({
                        'severity': 'critical',
                        'message': 'Pod处于Failed状态',
                        'suggestion': '检查Pod日志和事件'
                    })
                
                # 检查重启次数
                restart_count = 0
                if pod.status.container_statuses:
                    for container_status in pod.status.container_statuses:
                        restart_count += container_status.restart_count
                
                if restart_count > 5:
                    issues.append({
                        'severity': 'high',
                        'message': f'Pod重启次数过多: {restart_count}',
                        'suggestion': '检查应用配置和资源限制'
                    })
                
                pod_results.append({
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'restart_count': restart_count,
                    'issues': issues
                })
            
            return {
                'total_pods': len(pods.items),
                'pods': pod_results,
                'issues': [issue for pod in pod_results for issue in pod['issues']]
            }
            
        except Exception as e:
            return {'error': f'验证Pod失败: {e}'}
    
    def validate_deployments(self, namespace: str) -> Dict[str, Any]:
        """验证Deployment资源"""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace)
            deployment_results = []
            
            for deployment in deployments.items:
                issues = []
                
                # 检查副本数
                replicas = deployment.spec.replicas
                ready_replicas = deployment.status.ready_replicas or 0
                
                if ready_replicas < replicas:
                    issues.append({
                        'severity': 'medium',
                        'message': f'就绪副本数不足: {ready_replicas}/{replicas}',
                        'suggestion': '检查Pod状态和资源可用性'
                    })
                
                if replicas == 1:
                    issues.append({
                        'severity': 'medium',
                        'message': '副本数为1，存在单点故障风险',
                        'suggestion': '考虑增加副本数提高可用性'
                    })
                
                # 检查更新策略
                strategy = deployment.spec.strategy
                if not strategy or strategy.type == 'RollingUpdate':
                    if strategy and strategy.rolling_update:
                        max_unavailable = strategy.rolling_update.max_unavailable
                        if not max_unavailable:
                            issues.append({
                                'severity': 'low',
                                'message': '使用默认的maxUnavailable配置',
                                'suggestion': '根据业务需求调整更新策略'
                            })
                
                deployment_results.append({
                    'name': deployment.metadata.name,
                    'replicas': replicas,
                    'ready_replicas': ready_replicas,
                    'issues': issues
                })
            
            return {
                'total_deployments': len(deployments.items),
                'deployments': deployment_results,
                'issues': [issue for deployment in deployment_results for issue in deployment['issues']]
            }
            
        except Exception as e:
            return {'error': f'验证Deployment失败: {e}'}
    
    def validate_services(self, namespace: str) -> Dict[str, Any]:
        """验证Service资源"""
        try:
            services = self.v1.list_namespaced_service(namespace)
            service_results = []
            
            for service in services.items:
                issues = []
                
                # 检查Service类型
                service_type = service.spec.type
                if service_type == 'LoadBalancer':
                    if not service.status.load_balancer or not service.status.load_balancer.ingress:
                        issues.append({
                            'severity': 'medium',
                            'message': 'LoadBalancer Service没有分配外部IP',
                            'suggestion': '检查云提供商配置'
                        })
                
                # 检查端点
                if service.spec.selector:
                    # 检查是否有匹配的Pod
                    try:
                        endpoints = self.v1.read_namespaced_endpoints(
                            name=service.metadata.name,
                            namespace=namespace
                        )
                        
                        if not endpoints.subsets:
                            issues.append({
                                'severity': 'medium',
                                'message': 'Service没有对应的端点',
                                'suggestion': '检查选择器标签是否匹配Pod'
                            })
                    except:
                        issues.append({
                            'severity': 'medium',
                            'message': '无法获取Service端点',
                            'suggestion': '检查Service配置'
                        })
                
                # 检查端口配置
                ports = service.spec.ports or []
                if not ports:
                    issues.append({
                        'severity': 'high',
                        'message': 'Service没有配置端口',
                        'suggestion': '添加端口配置'
                    })
                
                service_results.append({
                    'name': service.metadata.name,
                    'type': service_type,
                    'cluster_ip': service.spec.cluster_ip,
                    'ports': len(ports),
                    'issues': issues
                })
            
            return {
                'total_services': len(services.items),
                'services': service_results,
                'issues': [issue for service in service_results for issue in service['issues']]
            }
            
        except Exception as e:
            return {'error': f'验证Service失败: {e}'}

# 使用示例
def main():
    # 文件验证
    validator = KubernetesConfigValidator()
    result = validator.validate_yaml_file('deployment.yaml')
    
    print("Kubernetes配置验证结果:")
    print(f"是否有效: {result.is_valid}")
    print(f"问题数量: {result.summary['total_issues']}")
    print(f"警告数量: {result.summary['total_warnings']}")
    
    for issue in result.issues:
        print(f"- {issue.severity}: {issue.message}")
    
    for warning in result.warnings:
        print(f"- 警告: {warning.message}")
    
    # 集群验证
    try:
        cluster_validator = ClusterResourceValidator()
        cluster_result = cluster_validator.validate_cluster_resources('default')
        
        print(f"\n集群资源验证结果:")
        print(f"总问题数: {cluster_result['summary']['total_issues']}")
        print(f"集群健康状态: {cluster_result['summary']['cluster_health']}")
    except Exception as e:
        print(f"集群验证失败: {e}")

if __name__ == '__main__':
    main()
```

### Kubernetes配置修复器
```python
import yaml
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class KubernetesConfigFixer:
    def __init__(self):
        self.fixes_applied = []
        
    def fix_yaml_file(self, file_path: str, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """修复YAML文件中的问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixed_content, fixes = self.fix_yaml_content(content, issues)
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return {
                'file_path': file_path,
                'fixes_applied': fixes,
                'success': True
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': f'修复失败: {e}',
                'success': False
            }
    
    def fix_yaml_content(self, content: str, issues: List[ValidationIssue]) -> Tuple[str, List[str]]:
        """修复YAML内容中的问题"""
        fixes = []
        fixed_content = content
        
        try:
            documents = list(yaml.safe_load_all(content))
            fixed_documents = []
            
            for doc in documents:
                if doc is None:
                    continue
                
                fixed_doc, doc_fixes = self.fix_document(doc, issues)
                fixed_documents.append(fixed_doc)
                fixes.extend(doc_fixes)
            
            # 重新序列化YAML
            fixed_content = yaml.dump_all(fixed_documents, default_flow_style=False, allow_unicode=True)
            
        except Exception as e:
            fixes.append(f'修复过程中出错: {e}')
        
        return fixed_content, fixes
    
    def fix_document(self, doc: Dict[str, Any], issues: List[ValidationIssue]) -> Tuple[Dict[str, Any], List[str]]:
        """修复单个文档"""
        fixes = []
        fixed_doc = doc.copy()
        
        # 按优先级修复问题
        critical_issues = [i for i in issues if i.severity == 'critical']
        high_issues = [i for i in issues if i.severity == 'high']
        medium_issues = [i for i in issues if i.severity == 'medium']
        
        all_issues = critical_issues + high_issues + medium_issues
        
        for issue in all_issues:
            fix = self.fix_issue(fixed_doc, issue)
            if fix:
                fixed_doc = fix
                fixes.append(f"修复: {issue.message}")
        
        return fixed_doc, fixes
    
    def fix_issue(self, doc: Dict[str, Any], issue: ValidationIssue) -> Optional[Dict[str, Any]]:
        """修复单个问题"""
        if issue.type == 'missing_field':
            return self.fix_missing_field(doc, issue)
        elif issue.type == 'best_practice':
            return self.apply_best_practice(doc, issue)
        elif issue.type == 'security':
            return self.fix_security_issue(doc, issue)
        
        return None
    
    def fix_missing_field(self, doc: Dict[str, Any], issue: ValidationIssue) -> Dict[str, Any]:
        """修复缺失字段"""
        fixed_doc = doc.copy()
        
        if issue.field == 'kind':
            fixed_doc['kind'] = 'Deployment'  # 默认类型
        elif issue.field == 'apiVersion':
            fixed_doc['apiVersion'] = 'apps/v1'  # 默认API版本
        elif issue.field == 'metadata':
            fixed_doc['metadata'] = {'name': 'default-name'}
        elif issue.field == 'spec':
            fixed_doc['spec'] = {}
        elif issue.field.startswith('spec.'):
            self.set_nested_field(fixed_doc, issue.field, self.get_default_value(issue.field))
        
        return fixed_doc
    
    def apply_best_practice(self, doc: Dict[str, Any], issue: ValidationIssue) -> Dict[str, Any]:
        """应用最佳实践"""
        fixed_doc = doc.copy()
        
        if '资源限制' in issue.message:
            # 添加默认资源限制
            self.add_default_resources(fixed_doc)
        elif '健康检查' in issue.message:
            # 添加默认健康检查
            self.add_default_health_checks(fixed_doc)
        elif '副本数' in issue.message:
            # 增加副本数
            self.set_replicas(fixed_doc, 3)
        
        return fixed_doc
    
    def fix_security_issue(self, doc: Dict[str, Any], issue: ValidationIssue) -> Dict[str, Any]:
        """修复安全问题"""
        fixed_doc = doc.copy()
        
        if '特权模式' in issue.message:
            # 移除特权模式
            self.remove_privileged_mode(fixed_doc)
        elif 'root用户' in issue.message:
            # 设置非root用户
            self.set_non_root_user(fixed_doc)
        
        return fixed_doc
    
    def set_nested_field(self, doc: Dict[str, Any], field_path: str, value: Any) -> None:
        """设置嵌套字段"""
        keys = field_path.split('.')
        current = doc
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def get_default_value(self, field_path: str) -> Any:
        """获取字段默认值"""
        defaults = {
            'spec.replicas': 1,
            'spec.selector.matchLabels': {'app': 'default'},
            'spec.template.metadata.labels': {'app': 'default'},
            'spec.template.spec.containers': [],
            'spec.ports': []
        }
        
        return defaults.get(field_path, {})
    
    def add_default_resources(self, doc: Dict[str, Any]) -> None:
        """添加默认资源配置"""
        kind = doc.get('kind', '')
        
        if kind in ['Pod', 'Deployment']:
            containers = self.get_containers(doc)
            for container in containers:
                if 'resources' not in container:
                    container['resources'] = {
                        'requests': {
                            'cpu': '100m',
                            'memory': '128Mi'
                        },
                        'limits': {
                            'cpu': '500m',
                            'memory': '512Mi'
                        }
                    }
    
    def add_default_health_checks(self, doc: Dict[str, Any]) -> None:
        """添加默认健康检查"""
        containers = self.get_containers(doc)
        
        for container in containers:
            if 'livenessProbe' not in container:
                container['livenessProbe'] = {
                    'httpGet': {
                        'path': '/health',
                        'port': 80
                    },
                    'initialDelaySeconds': 30,
                    'periodSeconds': 10
                }
            
            if 'readinessProbe' not in container:
                container['readinessProbe'] = {
                    'httpGet': {
                        'path': '/ready',
                        'port': 80
                    },
                    'initialDelaySeconds': 5,
                    'periodSeconds': 5
                }
    
    def set_replicas(self, doc: Dict[str, Any], replicas: int) -> None:
        """设置副本数"""
        if doc.get('kind') == 'Deployment':
            if 'spec' not in doc:
                doc['spec'] = {}
            doc['spec']['replicas'] = replicas
    
    def remove_privileged_mode(self, doc: Dict[str, Any]) -> None:
        """移除特权模式"""
        containers = self.get_containers(doc)
        
        for container in containers:
            if 'securityContext' in container:
                container['securityContext'].pop('privileged', None)
    
    def set_non_root_user(self, doc: Dict[str, Any]) -> None:
        """设置非root用户"""
        containers = self.get_containers(doc)
        
        for container in containers:
            if 'securityContext' not in container:
                container['securityContext'] = {}
            container['securityContext']['runAsUser'] = 1000
            container['securityContext']['runAsGroup'] = 1000
    
    def get_containers(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取容器列表"""
        kind = doc.get('kind', '')
        containers = []
        
        if kind == 'Pod':
            containers = doc.get('spec', {}).get('containers', [])
        elif kind == 'Deployment':
            containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        
        return containers

# 使用示例
def main():
    # 验证并修复配置
    validator = KubernetesConfigValidator()
    fixer = KubernetesConfigFixer()
    
    # 验证配置
    result = validator.validate_yaml_file('deployment.yaml')
    
    if not result.is_valid:
        print("发现配置问题，开始修复...")
        
        # 修复配置
        fix_result = fixer.fix_yaml_file('deployment.yaml', result.issues)
        
        if fix_result['success']:
            print(f"修复完成，应用了 {len(fix_result['fixes_applied'])} 个修复:")
            for fix in fix_result['fixes_applied']:
                print(f"- {fix}")
        else:
            print(f"修复失败: {fix_result['error']}")
    else:
        print("配置验证通过，无需修复")

if __name__ == '__main__':
    main()
```

## Kubernetes验证最佳实践

### 验证流程
1. **语法验证**: 检查YAML语法正确性
2. **结构验证**: 验证必填字段和数据类型
3. **语义验证**: 检查资源配置和引用关系
4. **最佳实践**: 应用行业标准和安全规范
5. **集群验证**: 验证实际集群中的资源状态

### 安全验证
1. **权限检查**: 验证RBAC和权限配置
2. **网络策略**: 检查网络隔离和安全组
3. **镜像安全**: 扫描镜像漏洞和签名
4. **密钥管理**: 验证Secret和ConfigMap使用

### 性能验证
1. **资源限制**: 检查CPU和内存配置
2. **调度策略**: 验证节点亲和性和反亲和性
3. **存储配置**: 检查存储类和卷挂载
4. **网络配置**: 验证服务和Ingress设置

### 运维验证
1. **监控配置**: 检查Prometheus和Grafana
2. **日志收集**: 验证ELK或Fluentd配置
3. **备份策略**: 检查Velero或etcd备份
4. **故障恢复**: 验证恢复流程和预案

## 相关技能

- **kubernetes-basics** - Kubernetes基础
- **docker-containerization** - Docker容器化
- **microservices** - 微服务架构
- **security-audit** - 安全审计
