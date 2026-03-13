---
name: 基础设施分析器
description: "当分析基础设施时，检查系统架构，优化资源配置，审查安全策略。验证基础设施配置，分析性能瓶颈，和最佳实践。"
license: MIT
---

# 基础设施分析器技能

## 概述
好的基础设施可以扩展。糟糕的基础设施在扩展时会崩溃。在问题级联之前分析。需要建立完善的基础设施分析和优化机制。

**核心原则**: 好的基础设施可以扩展。糟糕的基础设施在扩展时会崩溃。在问题级联之前分析。

## 何时使用

**始终:**
- 规划基础设施
- 为增长扩展
- 性能瓶颈调查
- 灾难恢复规划
- 成本优化分析
- 安全架构审查

**触发短语:**
- "分析基础设施架构"
- "优化资源配置"
- "检查基础设施安全"
- "基础设施性能问题"
- "灾难恢复计划"
- "基础设施成本分析"

## 基础设施分析功能

### 架构分析
- 系统拓扑检查
- 组件依赖分析
- 扩展性评估
- 可用性分析
- 容错能力检查

### 性能分析
- 资源使用监控
- 瓶颈识别
- 负载均衡分析
- 网络性能检查
- 存储性能评估

### 安全分析
- 安全配置检查
- 访问控制审查
- 网络安全分析
- 数据保护检查
- 合规性验证

## 常见基础设施问题

### 单点故障
```
问题:
系统存在单点故障风险

后果:
- 服务中断
- 数据丢失
- 业务影响
- 声誉损失

解决方案:
- 实现高可用架构
- 添加冗余组件
- 设置故障转移
- 建立监控告警
```

### 资源配置不当
```
问题:
资源配置不合理

后果:
- 性能瓶颈
- 资源浪费
- 成本增加
- 扩展困难

解决方案:
- 容量规划
- 自动扩缩容
- 资源监控
- 成本优化
```

### 安全配置缺陷
```
问题:
安全配置存在漏洞

后果:
- 数据泄露
- 系统入侵
- 合规违规
- 法律风险

解决方案:
- 安全审计
- 配置加固
- 访问控制
- 监控告警
```

## 基础设施优化策略

### 高可用设计
```
冗余架构:
- 多区域部署
- 负载均衡
- 故障转移
- 健康检查

容错机制:
- 断路器模式
- 重试机制
- 降级策略
- 熔断保护
```

### 性能优化
```
资源优化:
- 垂直扩展
- 水平扩展
- 缓存策略
- CDN加速

网络优化:
- 带宽规划
- 延迟优化
- 负载分布
- 流量管理
```

## 代码实现示例

### 基础设施配置分析器
```python
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import boto3
import requests

class InfrastructureType(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"

@dataclass
class InfrastructureComponent:
    """基础设施组件"""
    name: str
    type: str
    region: str
    configuration: Dict[str, Any]
    dependencies: List[str]
    metrics: Dict[str, Any]

@dataclass
class SecurityIssue:
    """安全问题"""
    severity: str
    component: str
    description: str
    recommendation: str

class InfrastructureAnalyzer:
    """基础设施分析器"""
    
    def __init__(self, infrastructure_type: InfrastructureType):
        self.infrastructure_type = infrastructure_type
        self.components = []
        self.security_issues = []
        self.performance_metrics = {}
        self.cost_analysis = {}
        
    def analyze_infrastructure(self, config_path: str = None) -> Dict[str, Any]:
        """分析基础设施"""
        # 加载配置
        if config_path:
            config = self._load_configuration(config_path)
        else:
            config = self._fetch_cloud_configuration()
        
        # 分析组件
        self.components = self._extract_components(config)
        
        # 分析依赖关系
        dependency_analysis = self._analyze_dependencies(self.components)
        
        # 分析安全性
        security_analysis = self._analyze_security(self.components)
        
        # 分析性能
        performance_analysis = self._analyze_performance(self.components)
        
        # 分析成本
        cost_analysis = self._analyze_costs(self.components)
        
        # 分析可用性
        availability_analysis = self._analyze_availability(self.components)
        
        return {
            'infrastructure_type': self.infrastructure_type.value,
            'components_count': len(self.components),
            'dependency_analysis': dependency_analysis,
            'security_analysis': security_analysis,
            'performance_analysis': performance_analysis,
            'cost_analysis': cost_analysis,
            'availability_analysis': availability_analysis,
            'recommendations': self._generate_recommendations()
        }
    
    def _load_configuration(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    return json.load(f)
                else:
                    raise ValueError("不支持的配置文件格式")
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return {}
    
    def _fetch_cloud_configuration(self) -> Dict[str, Any]:
        """从云服务获取配置"""
        if self.infrastructure_type == InfrastructureType.AWS:
            return self._fetch_aws_configuration()
        elif self.infrastructure_type == InfrastructureType.AZURE:
            return self._fetch_azure_configuration()
        elif self.infrastructure_type == InfrastructureType.GCP:
            return self._fetch_gcp_configuration()
        else:
            return {}
    
    def _fetch_aws_configuration(self) -> Dict[str, Any]:
        """获取AWS配置"""
        try:
            session = boto3.Session()
            ec2 = session.client('ec2')
            rds = session.client('rds')
            elb = session.client('elbv2')
            
            config = {
                'ec2_instances': self._get_ec2_instances(ec2),
                'rds_instances': self._get_rds_instances(rds),
                'load_balancers': self._get_load_balancers(elb),
                'vpcs': self._get_vpcs(ec2)
            }
            
            return config
        except Exception as e:
            print(f"获取AWS配置失败: {str(e)}")
            return {}
    
    def _get_ec2_instances(self, ec2_client) -> List[Dict[str, Any]]:
        """获取EC2实例"""
        instances = []
        try:
            response = ec2_client.describe_instances()
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'region': instance['Placement']['AvailabilityZone'],
                        'security_groups': [sg['GroupId'] for sg in instance['SecurityGroups']],
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    })
        except Exception as e:
            print(f"获取EC2实例失败: {str(e)}")
        
        return instances
    
    def _get_rds_instances(self, rds_client) -> List[Dict[str, Any]]:
        """获取RDS实例"""
        instances = []
        try:
            response = rds_client.describe_db_instances()
            for instance in response['DBInstances']:
                instances.append({
                    'id': instance['DBInstanceIdentifier'],
                    'engine': instance['Engine'],
                    'status': instance['DBInstanceStatus'],
                    'instance_class': instance['DBInstanceClass'],
                    'multi_az': instance.get('MultiAZ', False),
                    'storage_type': instance.get('StorageType', 'standard')
                })
        except Exception as e:
            print(f"获取RDS实例失败: {str(e)}")
        
        return instances
    
    def _get_load_balancers(self, elb_client) -> List[Dict[str, Any]]:
        """获取负载均衡器"""
        load_balancers = []
        try:
            response = elb_client.describe_load_balancers()
            for lb in response['LoadBalancers']:
                load_balancers.append({
                    'name': lb['LoadBalancerArn'],
                    'type': lb['Type'],
                    'state': lb['State']['Code'],
                    'scheme': lb['Scheme'],
                    'vpc_id': lb['VpcId']
                })
        except Exception as e:
            print(f"获取负载均衡器失败: {str(e)}")
        
        return load_balancers
    
    def _get_vpcs(self, ec2_client) -> List[Dict[str, Any]]:
        """获取VPC"""
        vpcs = []
        try:
            response = ec2_client.describe_vpcs()
            for vpc in response['Vpcs']:
                vpcs.append({
                    'id': vpc['VpcId'],
                    'cidr': vpc['CidrBlock'],
                    'state': vpc['State'],
                    'is_default': vpc['IsDefault']
                })
        except Exception as e:
            print(f"获取VPC失败: {str(e)}")
        
        return vpcs
    
    def _extract_components(self, config: Dict[str, Any]) -> List[InfrastructureComponent]:
        """提取基础设施组件"""
        components = []
        
        # 提取EC2实例
        for instance in config.get('ec2_instances', []):
            component = InfrastructureComponent(
                name=instance['id'],
                type='EC2',
                region=instance['region'],
                configuration=instance,
                dependencies=self._extract_instance_dependencies(instance),
                metrics={}
            )
            components.append(component)
        
        # 提取RDS实例
        for instance in config.get('rds_instances', []):
            component = InfrastructureComponent(
                name=instance['id'],
                type='RDS',
                region=instance.get('region', 'unknown'),
                configuration=instance,
                dependencies=[],
                metrics={}
            )
            components.append(component)
        
        # 提取负载均衡器
        for lb in config.get('load_balancers', []):
            component = InfrastructureComponent(
                name=lb['name'],
                type='LoadBalancer',
                region=lb.get('region', 'unknown'),
                configuration=lb,
                dependencies=[],
                metrics={}
            )
            components.append(component)
        
        return components
    
    def _extract_instance_dependencies(self, instance: Dict[str, Any]) -> List[str]:
        """提取实例依赖关系"""
        dependencies = []
        
        # 检查安全组依赖
        for sg_id in instance.get('security_groups', []):
            dependencies.append(f"SecurityGroup:{sg_id}")
        
        # 检查子网依赖
        if 'SubnetId' in instance:
            dependencies.append(f"Subnet:{instance['SubnetId']}")
        
        return dependencies
    
    def _analyze_dependencies(self, components: List[InfrastructureComponent]) -> Dict[str, Any]:
        """分析依赖关系"""
        dependency_graph = {}
        single_points_of_failure = []
        circular_dependencies = []
        
        # 构建依赖图
        for component in components:
            dependency_graph[component.name] = component.dependencies
        
        # 检查单点故障
        dependency_counts = {}
        for dependencies in dependency_graph.values():
            for dep in dependencies:
                dependency_counts[dep] = dependency_counts.get(dep, 0) + 1
        
        # 找出被多个组件依赖的关键组件
        for dep, count in dependency_counts.items():
            if count > 3:  # 被3个以上组件依赖
                single_points_of_failure.append({
                    'component': dep,
                    'dependent_count': count,
                    'risk_level': 'high'
                })
        
        # 检查循环依赖（简化版）
        visited = set()
        recursion_stack = set()
        
        def has_circular_dependency(component: str) -> bool:
            if component in recursion_stack:
                return True
            if component in visited:
                return False
            
            visited.add(component)
            recursion_stack.add(component)
            
            for dep in dependency_graph.get(component, []):
                if has_circular_dependency(dep):
                    return True
            
            recursion_stack.remove(component)
            return False
        
        for component in dependency_graph:
            if has_circular_dependency(component):
                circular_dependencies.append(component)
        
        return {
            'dependency_graph': dependency_graph,
            'single_points_of_failure': single_points_of_failure,
            'circular_dependencies': circular_dependencies,
            'total_dependencies': len(dependency_counts)
        }
    
    def _analyze_security(self, components: List[InfrastructureComponent]) -> Dict[str, Any]:
        """分析安全性"""
        security_issues = []
        
        for component in components:
            if component.type == 'EC2':
                issues = self._analyze_ec2_security(component)
                security_issues.extend(issues)
            elif component.type == 'RDS':
                issues = self._analyze_rds_security(component)
                security_issues.extend(issues)
        
        # 按严重程度分类
        critical_issues = [issue for issue in security_issues if issue.severity == 'critical']
        high_issues = [issue for issue in security_issues if issue.severity == 'high']
        medium_issues = [issue for issue in security_issues if issue.severity == 'medium']
        low_issues = [issue for issue in security_issues if issue.severity == 'low']
        
        return {
            'total_issues': len(security_issues),
            'critical_issues': len(critical_issues),
            'high_issues': len(high_issues),
            'medium_issues': len(medium_issues),
            'low_issues': len(low_issues),
            'issues_by_component': self._group_issues_by_component(security_issues),
            'security_score': self._calculate_security_score(security_issues)
        }
    
    def _analyze_ec2_security(self, component: InfrastructureComponent) -> List[SecurityIssue]:
        """分析EC2安全性"""
        issues = []
        config = component.configuration
        
        # 检查安全组配置
        security_groups = config.get('security_groups', [])
        if len(security_groups) == 0:
            issues.append(SecurityIssue(
                severity='high',
                component=component.name,
                description='EC2实例没有配置安全组',
                recommendation='为实例配置适当的安全组'
            ))
        
        # 检查公开端口
        if config.get('public_ip'):
            issues.append(SecurityIssue(
                severity='medium',
                component=component.name,
                description='EC2实例具有公开IP地址',
                recommendation='确保只有必要的服务公开访问'
            ))
        
        # 检查IAM角色
        if not config.get('iam_instance_profile'):
            issues.append(SecurityIssue(
                severity='medium',
                component=component.name,
                description='EC2实例没有配置IAM角色',
                recommendation='为实例配置适当的IAM角色以限制权限'
            ))
        
        return issues
    
    def _analyze_rds_security(self, component: InfrastructureComponent) -> List[SecurityIssue]:
        """分析RDS安全性"""
        issues = []
        config = component.configuration
        
        # 检查多可用区
        if not config.get('multi_az', False):
            issues.append(SecurityIssue(
                severity='high',
                component=component.name,
                description='RDS实例未启用多可用区',
                recommendation='启用多可用区以提高可用性'
            ))
        
        # 检查加密
        if not config.get('storage_encrypted', False):
            issues.append(SecurityIssue(
                severity='high',
                component=component.name,
                description='RDS实例未启用存储加密',
                recommendation='启用存储加密以保护数据'
            ))
        
        # 检查公开访问
        if config.get('publicly_accessible', False):
            issues.append(SecurityIssue(
                severity='critical',
                component=component.name,
                description='RDS实例允许公开访问',
                recommendation='禁用公开访问，只允许VPC内部访问'
            ))
        
        return issues
    
    def _analyze_performance(self, components: List[InfrastructureComponent]) -> Dict[str, Any]:
        """分析性能"""
        performance_issues = []
        bottlenecks = []
        
        for component in components:
            if component.type == 'EC2':
                issues = self._analyze_ec2_performance(component)
                performance_issues.extend(issues)
            elif component.type == 'RDS':
                issues = self._analyze_rds_performance(component)
                performance_issues.extend(issues)
        
        # 识别性能瓶颈
        bottleneck_types = {}
        for issue in performance_issues:
            issue_type = issue.description.split(':')[0]
            bottleneck_types[issue_type] = bottleneck_types.get(issue_type, 0) + 1
        
        return {
            'total_issues': len(performance_issues),
            'bottleneck_types': bottleneck_types,
            'performance_score': self._calculate_performance_score(performance_issues),
            'recommendations': [issue.recommendation for issue in performance_issues]
        }
    
    def _analyze_ec2_performance(self, component: InfrastructureComponent) -> List[SecurityIssue]:
        """分析EC2性能"""
        issues = []
        config = component.configuration
        
        # 检查实例类型
        instance_type = config.get('type', '')
        if instance_type.startswith('t2.'):
            issues.append(SecurityIssue(
                severity='medium',
                component=component.name,
                description='EC2实例类型: 使用了突发性能实例',
                recommendation='考虑使用更稳定的实例类型以保证性能'
            ))
        
        # 检查状态
        state = config.get('state', '')
        if state != 'running':
            issues.append(SecurityIssue(
                severity='low',
                component=component.name,
                description=f'EC2实例状态: {state}',
                recommendation='确保实例处于运行状态'
            ))
        
        return issues
    
    def _analyze_rds_performance(self, component: InfrastructureComponent) -> List[SecurityIssue]:
        """分析RDS性能"""
        issues = []
        config = component.configuration
        
        # 检查实例类型
        instance_class = config.get('instance_class', '')
        if instance_class in ['db.t2.micro', 'db.t2.small']:
            issues.append(SecurityIssue(
                severity='medium',
                component=component.name,
                description='RDS实例类型: 使用了小规格实例',
                recommendation='根据工作负载选择合适的实例规格'
            ))
        
        # 检查存储类型
        storage_type = config.get('storage_type', 'standard')
        if storage_type == 'standard':
            issues.append(SecurityIssue(
                severity='medium',
                component=component.name,
                description='RDS存储类型: 使用了标准存储',
                recommendation='考虑使用SSD存储以提高I/O性能'
            ))
        
        return issues
    
    def _analyze_costs(self, components: List[InfrastructureComponent]) -> Dict[str, Any]:
        """分析成本"""
        cost_breakdown = {}
        total_estimated_cost = 0
        
        for component in components:
            if component.type == 'EC2':
                cost = self._estimate_ec2_cost(component)
            elif component.type == 'RDS':
                cost = self._estimate_rds_cost(component)
            else:
                cost = 0
            
            cost_breakdown[component.name] = cost
            total_estimated_cost += cost
        
        # 成本优化建议
        optimization_suggestions = self._generate_cost_optimization_suggestions(components)
        
        return {
            'total_estimated_cost': total_estimated_cost,
            'cost_breakdown': cost_breakdown,
            'optimization_suggestions': optimization_suggestions,
            'cost_efficiency_score': self._calculate_cost_efficiency(components)
        }
    
    def _estimate_ec2_cost(self, component: InfrastructureComponent) -> float:
        """估算EC2成本"""
        instance_type = component.configuration.get('type', '')
        # 简化的成本估算，实际应该使用AWS定价API
        cost_map = {
            't2.micro': 0.0116,
            't2.small': 0.023,
            't2.medium': 0.046,
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'c5.large': 0.085,
            'c5.xlarge': 0.17
        }
        
        return cost_map.get(instance_type, 0.1) * 24 * 30  # 月成本估算
    
    def _estimate_rds_cost(self, component: InfrastructureComponent) -> float:
        """估算RDS成本"""
        instance_class = component.configuration.get('instance_class', '')
        # 简化的成本估算
        cost_map = {
            'db.t2.micro': 0.0116,
            'db.t2.small': 0.029,
            'db.t2.medium': 0.058,
            'db.t3.micro': 0.0104,
            'db.t3.small': 0.0416,
            'db.t3.medium': 0.083,
            'db.m5.large': 0.145,
            'db.m5.xlarge': 0.29
        }
        
        base_cost = cost_map.get(instance_class, 0.15) * 24 * 30
        
        # 多可用区额外费用
        if component.configuration.get('multi_az', False):
            base_cost *= 2
        
        return base_cost
    
    def _generate_cost_optimization_suggestions(self, components: List[InfrastructureComponent]) -> List[str]:
        """生成成本优化建议"""
        suggestions = []
        
        # 检查闲置实例
        stopped_instances = [c for c in components if c.type == 'EC2' and c.configuration.get('state') == 'stopped']
        if stopped_instances:
            suggestions.append(f"发现{len(stopped_instances)}个停止的EC2实例，建议删除以节省成本")
        
        # 检查过度配置
        oversized_instances = [c for c in components if c.type == 'EC2' and c.configuration.get('type') in ['m5.2xlarge', 'c5.2xlarge']]
        if oversized_instances:
            suggestions.append(f"发现{len(oversized_instances)}个大规格实例，建议评估实际需求")
        
        # 检查存储优化
        rds_instances = [c for c in components if c.type == 'RDS']
        if rds_instances:
            suggestions.append("考虑使用RDS预留实例以降低成本")
        
        return suggestions
    
    def _analyze_availability(self, components: List[InfrastructureComponent]) -> Dict[str, Any]:
        """分析可用性"""
        availability_issues = []
        availability_score = 100
        
        for component in components:
            if component.type == 'EC2':
                issues = self._analyze_ec2_availability(component)
                availability_issues.extend(issues)
            elif component.type == 'RDS':
                issues = self._analyze_rds_availability(component)
                availability_issues.extend(issues)
        
        # 计算可用性评分
        for issue in availability_issues:
            if issue.severity == 'critical':
                availability_score -= 20
            elif issue.severity == 'high':
                availability_score -= 10
            elif issue.severity == 'medium':
                availability_score -= 5
            elif issue.severity == 'low':
                availability_score -= 2
        
        availability_score = max(0, availability_score)
        
        return {
            'availability_score': availability_score,
            'availability_issues': availability_issues,
            'redundancy_level': self._calculate_redundancy_level(components),
            'fault_tolerance': self._assess_fault_tolerance(components)
        }
    
    def _analyze_ec2_availability(self, component: InfrastructureComponent) -> List[SecurityIssue]:
        """分析EC2可用性"""
        issues = []
        config = component.configuration
        
        # 检查是否在单个可用区
        if len(set([config.get('region', '')])) == 1:
            issues.append(SecurityIssue(
                severity='high',
                component=component.name,
                description='EC2实例部署在单个可用区',
                recommendation='考虑跨多个可用区部署以提高可用性'
            ))
        
        return issues
    
    def _analyze_rds_availability(self, component: InfrastructureComponent) -> List[SecurityIssue]:
        """分析RDS可用性"""
        issues = []
        config = component.configuration
        
        # 检查多可用区
        if not config.get('multi_az', False):
            issues.append(SecurityIssue(
                severity='high',
                component=component.name,
                description='RDS实例未启用多可用区',
                recommendation='启用多可用区部署'
            ))
        
        # 检查备份
        if not config.get('backup_retention_period', 0):
            issues.append(SecurityIssue(
                severity='medium',
                component=component.name,
                description='RDS实例未启用备份',
                recommendation='启用自动备份'
            ))
        
        return issues
    
    def _calculate_redundancy_level(self, components: List[InfrastructureComponent]) -> str:
        """计算冗余级别"""
        ec2_count = len([c for c in components if c.type == 'EC2'])
        rds_count = len([c for c in components if c.type == 'RDS'])
        
        if ec2_count >= 3 and rds_count >= 2:
            return 'high'
        elif ec2_count >= 2 and rds_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _assess_fault_tolerance(self, components: List[InfrastructureComponent]) -> str:
        """评估容错能力"""
        multi_az_rds = len([c for c in components if c.type == 'RDS' and c.configuration.get('multi_az', False)])
        total_rds = len([c for c in components if c.type == 'RDS'])
        
        if total_rds > 0 and multi_az_rds / total_rds >= 0.8:
            return 'excellent'
        elif multi_az_rds / total_rds >= 0.5:
            return 'good'
        else:
            return 'poor'
    
    def _group_issues_by_component(self, issues: List[SecurityIssue]) -> Dict[str, List[SecurityIssue]]:
        """按组件分组问题"""
        grouped = {}
        for issue in issues:
            if issue.component not in grouped:
                grouped[issue.component] = []
            grouped[issue.component].append(issue)
        return grouped
    
    def _calculate_security_score(self, issues: List[SecurityIssue]) -> int:
        """计算安全评分"""
        score = 100
        for issue in issues:
            if issue.severity == 'critical':
                score -= 25
            elif issue.severity == 'high':
                score -= 15
            elif issue.severity == 'medium':
                score -= 8
            elif issue.severity == 'low':
                score -= 3
        return max(0, score)
    
    def _calculate_performance_score(self, issues: List[SecurityIssue]) -> int:
        """计算性能评分"""
        score = 100
        for issue in issues:
            if issue.severity == 'critical':
                score -= 20
            elif issue.severity == 'high':
                score -= 12
            elif issue.severity == 'medium':
                score -= 6
            elif issue.severity == 'low':
                score -= 2
        return max(0, score)
    
    def _calculate_cost_efficiency(self, components: List[InfrastructureComponent]) -> str:
        """计算成本效率"""
        # 简化的成本效率评估
        total_components = len(components)
        oversized_components = len([c for c in components if 'large' in c.configuration.get('type', '') or 'xlarge' in c.configuration.get('type', '')])
        
        if oversized_components / total_components > 0.3:
            return 'poor'
        elif oversized_components / total_components > 0.1:
            return 'medium'
        else:
            return 'good'
    
    def _generate_recommendations(self) -> List[str]:
        """生成综合建议"""
        recommendations = []
        
        # 基于安全分析的建议
        if self.security_issues:
            critical_count = len([i for i in self.security_issues if i.severity == 'critical'])
            if critical_count > 0:
                recommendations.append(f"发现{critical_count}个严重安全问题，需要立即处理")
        
        # 基于性能分析的建议
        recommendations.append("定期监控基础设施性能指标")
        
        # 基于成本分析的建议
        recommendations.append("定期审查基础设施成本，优化资源配置")
        
        # 基于可用性分析的建议
        recommendations.append("实施高可用架构以减少服务中断")
        
        return recommendations

# 使用示例
def main():
    analyzer = InfrastructureAnalyzer(InfrastructureType.AWS)
    
    # 分析基础设施
    analysis = analyzer.analyze_infrastructure()
    
    print("=== 基础设施分析报告 ===")
    print(f"基础设施类型: {analysis['infrastructure_type']}")
    print(f"组件数量: {analysis['components_count']}")
    
    print("\n--- 依赖关系分析 ---")
    dep_analysis = analysis['dependency_analysis']
    print(f"单点故障: {len(dep_analysis['single_points_of_failure'])}")
    print(f"循环依赖: {len(dep_analysis['circular_dependencies'])}")
    
    print("\n--- 安全分析 ---")
    sec_analysis = analysis['security_analysis']
    print(f"安全问题总数: {sec_analysis['total_issues']}")
    print(f"严重问题: {sec_analysis['critical_issues']}")
    print(f"高危问题: {sec_analysis['high_issues']}")
    print(f"安全评分: {sec_analysis['security_score']}")
    
    print("\n--- 性能分析 ---")
    perf_analysis = analysis['performance_analysis']
    print(f"性能问题: {perf_analysis['total_issues']}")
    print(f"性能评分: {perf_analysis['performance_score']}")
    
    print("\n--- 成本分析 ---")
    cost_analysis = analysis['cost_analysis']
    print(f"预估月成本: ${cost_analysis['total_estimated_cost']:.2f}")
    print(f"成本效率: {cost_analysis['cost_efficiency_score']}")
    
    print("\n--- 可用性分析 ---")
    avail_analysis = analysis['availability_analysis']
    print(f"可用性评分: {avail_analysis['availability_score']}")
    print(f"冗余级别: {avail_analysis['redundancy_level']}")
    print(f"容错能力: {avail_analysis['fault_tolerance']}")
    
    print("\n--- 建议 ---")
    for rec in analysis['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    main()
```

### 基础设施监控器
```python
import time
import psutil
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    load_average: List[float]

class InfrastructureMonitor:
    """基础设施监控器"""
    
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'load_average': 2.0
        }
        self.alerts = []
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_io=self._get_network_io(),
            load_average=list(psutil.getloadavg())
        )
        
        self.metrics_history.append(metrics)
        
        # 检查告警
        self._check_alerts(metrics)
        
        return metrics
    
    def _get_network_io(self) -> Dict[str, float]:
        """获取网络IO"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    def _check_alerts(self, metrics: SystemMetrics):
        """检查告警条件"""
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'cpu_high',
                'message': f"CPU使用率过高: {metrics.cpu_usage:.1f}%",
                'severity': 'high'
            })
        
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'memory_high',
                'message': f"内存使用率过高: {metrics.memory_usage:.1f}%",
                'severity': 'high'
            })
        
        if metrics.disk_usage > self.alert_thresholds['disk_usage']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'disk_high',
                'message': f"磁盘使用率过高: {metrics.disk_usage:.1f}%",
                'severity': 'critical'
            })
        
        if metrics.load_average[0] > self.alert_thresholds['load_average']:
            self.alerts.append({
                'timestamp': metrics.timestamp,
                'type': 'load_high',
                'message': f"系统负载过高: {metrics.load_average[0]:.2f}",
                'severity': 'medium'
            })
    
    def analyze_trends(self, hours: int = 24) -> Dict[str, Any]:
        """分析趋势"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        
        if len(recent_metrics) < 2:
            return {'message': '数据不足，无法分析趋势'}
        
        cpu_trend = self._calculate_trend([m.cpu_usage for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_usage for m in recent_metrics])
        disk_trend = self._calculate_trend([m.disk_usage for m in recent_metrics])
        
        return {
            'period_hours': hours,
            'data_points': len(recent_metrics),
            'cpu_trend': cpu_trend,
            'memory_trend': memory_trend,
            'disk_trend': disk_trend,
            'avg_cpu_usage': statistics.mean([m.cpu_usage for m in recent_metrics]),
            'avg_memory_usage': statistics.mean([m.memory_usage for m in recent_metrics]),
            'avg_disk_usage': statistics.mean([m.disk_usage for m in recent_metrics]),
            'peak_cpu_usage': max([m.cpu_usage for m in recent_metrics]),
            'peak_memory_usage': max([m.memory_usage for m in recent_metrics])
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return 'stable'
        
        # 简单的线性趋势
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.5:
            return 'increasing'
        elif slope < -0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    def generate_health_report(self) -> Dict[str, Any]:
        """生成健康报告"""
        if not self.metrics_history:
            return {'message': '没有监控数据'}
        
        latest_metrics = self.metrics_history[-1]
        
        # 计算健康评分
        health_score = 100
        if latest_metrics.cpu_usage > 80:
            health_score -= 20
        if latest_metrics.memory_usage > 85:
            health_score -= 20
        if latest_metrics.disk_usage > 90:
            health_score -= 30
        if latest_metrics.load_average[0] > 2.0:
            health_score -= 15
        
        health_score = max(0, health_score)
        
        # 获取最近告警
        recent_alerts = [
            alert for alert in self.alerts
            if alert['timestamp'] > datetime.now() - timedelta(hours=1)
        ]
        
        return {
            'health_score': health_score,
            'health_status': self._get_health_status(health_score),
            'current_metrics': {
                'cpu_usage': latest_metrics.cpu_usage,
                'memory_usage': latest_metrics.memory_usage,
                'disk_usage': latest_metrics.disk_usage,
                'load_average': latest_metrics.load_average[0]
            },
            'recent_alerts': recent_alerts,
            'trend_analysis': self.analyze_trends(),
            'recommendations': self._generate_health_recommendations(latest_metrics)
        }
    
    def _get_health_status(self, score: int) -> str:
        """获取健康状态"""
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_health_recommendations(self, metrics: SystemMetrics) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        if metrics.cpu_usage > 80:
            recommendations.append("CPU使用率较高，建议检查高CPU进程或扩展资源")
        
        if metrics.memory_usage > 85:
            recommendations.append("内存使用率较高，建议检查内存泄漏或增加内存")
        
        if metrics.disk_usage > 90:
            recommendations.append("磁盘空间不足，建议清理磁盘或扩展存储")
        
        if metrics.load_average[0] > 2.0:
            recommendations.append("系统负载较高，建议检查并发进程或优化应用")
        
        return recommendations

# 使用示例
def main():
    monitor = InfrastructureMonitor()
    
    # 模拟监控
    print("开始监控基础设施...")
    
    for i in range(10):
        metrics = monitor.collect_system_metrics()
        print(f"第{i+1}次监控 - CPU: {metrics.cpu_usage:.1f}%, 内存: {metrics.memory_usage:.1f}%, 磁盘: {metrics.disk_usage:.1f}%")
        time.sleep(2)
    
    # 生成报告
    report = monitor.generate_health_report()
    
    print("\n=== 基础设施健康报告 ===")
    print(f"健康评分: {report['health_score']}")
    print(f"健康状态: {report['health_status']}")
    
    print("\n当前指标:")
    current = report['current_metrics']
    print(f"CPU使用率: {current['cpu_usage']:.1f}%")
    print(f"内存使用率: {current['memory_usage']:.1f}%")
    print(f"磁盘使用率: {current['disk_usage']:.1f}%")
    print(f"系统负载: {current['load_average']:.2f}")
    
    if report['recent_alerts']:
        print("\n最近告警:")
        for alert in report['recent_alerts']:
            print(f"- {alert['message']}")
    
    if report['recommendations']:
        print("\n建议:")
        for rec in report['recommendations']:
            print(f"- {rec}")

if __name__ == "__main__":
    main()
```

## 基础设施最佳实践

### 架构设计
1. **高可用性**: 避免单点故障
2. **可扩展性**: 支持水平和垂直扩展
3. **安全性**: 多层安全防护
4. **成本优化**: 合理控制成本

### 监控运维
1. **全面监控**: 覆盖所有关键指标
2. **告警机制**: 及时发现问题
3. **自动化**: 减少人工干预
4. **文档化**: 完善的运维文档

### 灾难恢复
1. **备份策略**: 定期备份和恢复测试
2. **故障转移**: 自动故障转移机制
3. **应急预案**: 详细的应急响应流程
4. **演练测试**: 定期进行灾难演练

## 相关技能

- **kubernetes-analyzer** - Kubernetes配置分析
- **security-scanner** - 安全漏洞扫描
- **performance-profiler** - 性能分析和监控
- **cost-optimizer** - 成本优化分析
