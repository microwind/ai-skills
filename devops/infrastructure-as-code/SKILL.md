---
name: 基础设施即代码
description: "当设计基础设施即代码时，管理云资源，自动化部署，版本控制基础设施。验证Terraform配置，优化CloudFormation模板，和最佳实践。"
license: MIT
---

# 基础设施即代码技能

## 概述
基础设施即代码（IaC）是现代DevOps实践的核心。手动管理基础设施容易出错且不可重复，而IaC提供了自动化、版本控制和一致性。在实施IaC前需要理解核心概念和最佳实践。

**核心原则**: 好的IaC应该声明式、幂等性、可测试、可重用。坏的IaC会导致资源浪费、配置漂移和安全风险。

## 何时使用

**始终:**
- 设计云基础设施时
- 自动化资源部署时
- 版本控制基础设施时
- 实现环境一致性时
- 管理多环境配置时
- 优化资源成本时

**触发短语:**
- "基础设施即代码"
- "Terraform配置"
- "CloudFormation模板"
- "Ansible自动化"
- "Kubernetes清单"
- "基础设施自动化"

## 基础设施即代码功能

### 资源管理
- 云资源声明式定义
- 资源依赖关系管理
- 资源生命周期控制
- 资源标签和分类
- 资源成本优化

### 配置管理
- 环境配置标准化
- 配置参数化
- 配置验证和测试
- 配置版本控制
- 配置漂移检测

### 自动化部署
- 基础设施自动部署
- 滚动更新和回滚
- 蓝绿部署支持
- 金丝雀发布
- 灾难恢复自动化

### 监控合规
- 资源状态监控
- 合规性检查
- 安全策略验证
- 成本监控分析
- 性能指标收集

## 常见IaC问题

### 配置漂移问题
```
问题:
手动修改导致配置不一致

错误示例:
- 直接在控制台修改资源
- 跳过IaC直接操作
- 忘记更新配置文件
- 环境间配置差异

解决方案:
1. 禁用控制台直接访问
2. 实施配置漂移检测
3. 建立变更审批流程
4. 定期同步配置状态
```

### 资源依赖混乱
```
问题:
资源依赖关系不清晰

错误示例:
- 循环依赖
- 隐式依赖
- 依赖顺序错误
- 缺少依赖声明

解决方案:
1. 明确声明依赖关系
2. 使用依赖图分析
3. 分层设计资源
4. 避免循环依赖
```

### 状态管理问题
```
问题:
状态文件管理不当

错误示例:
- 状态文件丢失
- 状态文件冲突
- 敏感信息泄露
- 状态文件未备份

解决方案:
1. 使用远程状态存储
2. 实施状态锁定机制
3. 加密敏感状态信息
4. 定期备份状态文件
```

### 安全配置问题
```
问题:
安全策略配置不当

错误示例:
- 过度开放权限
- 硬编码密钥
- 网络配置错误
- 缺少安全扫描

解决方案:
1. 实施最小权限原则
2. 使用密钥管理服务
3. 配置网络安全组
4. 集成安全扫描工具
```

## 代码实现示例

### Terraform分析器
```python
import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import hcl2

class ResourceType(Enum):
    """资源类型"""
    COMPUTE = "compute"
    NETWORK = "network"
    STORAGE = "storage"
    DATABASE = "database"
    SECURITY = "security"
    MONITORING = "monitoring"

class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TerraformResource:
    """Terraform资源"""
    type: str
    name: str
    config: Dict[str, Any]
    dependencies: Set[str]
    issues: List[str]

@dataclass
class TerraformIssue:
    """Terraform问题"""
    severity: Severity
    type: str
    resource: str
    message: str
    suggestion: str
    line: Optional[int] = None

class TerraformAnalyzer:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.resources: List[TerraformResource] = []
        self.issues: List[TerraformIssue] = []
        self.variables: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        
    def analyze_infrastructure(self) -> Dict[str, Any]:
        """分析基础设施代码"""
        try:
            # 扫描Terraform文件
            self._scan_terraform_files()
            
            # 解析资源配置
            self._parse_resources()
            
            # 分析资源依赖
            self._analyze_dependencies()
            
            # 检查安全配置
            self._check_security()
            
            # 检查最佳实践
            self._check_best_practices()
            
            # 分析成本优化
            self._analyze_cost_optimization()
            
            # 生成分析报告
            return self._generate_report()
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def _scan_terraform_files(self) -> None:
        """扫描Terraform文件"""
        tf_files = []
        
        # 扫描.tf文件
        tf_files.extend(self.workspace_path.glob('*.tf'))
        tf_files.extend(self.workspace_path.glob('**/*.tf'))
        
        if not tf_files:
            self.issues.append(TerraformIssue(
                severity=Severity.HIGH,
                type='structure',
                resource='',
                message='未找到Terraform配置文件',
                suggestion='创建main.tf、variables.tf等配置文件'
            ))
        
        for tf_file in tf_files:
            self._parse_terraform_file(tf_file)
    
    def _parse_terraform_file(self, tf_file: Path) -> None:
        """解析Terraform文件"""
        try:
            with open(tf_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析HCL内容
            try:
                parsed = hcl2.loads(content)
            except Exception as e:
                self.issues.append(TerraformIssue(
                    severity=Severity.CRITICAL,
                    type='syntax',
                    resource=str(tf_file),
                    message=f'HCL语法错误: {e}',
                    suggestion='检查HCL语法和缩进'
                ))
                return
            
            # 解析不同区块
            if 'resource' in parsed:
                self._parse_resource_block(parsed['resource'], str(tf_file))
            
            if 'variable' in parsed:
                self._parse_variable_block(parsed['variable'])
            
            if 'output' in parsed:
                self._parse_output_block(parsed['output'])
            
            if 'provider' in parsed:
                self._parse_provider_block(parsed['provider'])
            
            if 'module' in parsed:
                self._parse_module_block(parsed['module'], str(tf_file))
        
        except Exception as e:
            self.issues.append(TerraformIssue(
                severity=Severity.MEDIUM,
                type='file_error',
                resource=str(tf_file),
                message=f'文件解析失败: {e}',
                suggestion='检查文件格式和编码'
            ))
    
    def _parse_resource_block(self, resources: Dict[str, Any], file_path: str) -> None:
        """解析资源区块"""
        for resource_type, resource_configs in resources.items():
            for resource_name, resource_config in resource_configs.items():
                resource = TerraformResource(
                    type=resource_type,
                    name=resource_name,
                    config=resource_config,
                    dependencies=set(),
                    issues=[]
                )
                
                # 分析资源配置
                self._analyze_resource_config(resource)
                
                self.resources.append(resource)
    
    def _parse_variable_block(self, variables: Dict[str, Any]) -> None:
        """解析变量区块"""
        for var_name, var_config in variables.items():
            self.variables[var_name] = var_config
    
    def _parse_output_block(self, outputs: Dict[str, Any]) -> None:
        """解析输出区块"""
        for output_name, output_config in outputs.items():
            self.outputs[output_name] = output_config
    
    def _parse_provider_block(self, providers: Dict[str, Any]) -> None:
        """解析提供商区块"""
        # 分析提供商配置
        for provider_name, provider_config in providers.items():
            self._analyze_provider_config(provider_name, provider_config)
    
    def _parse_module_block(self, modules: Dict[str, Any], file_path: str) -> None:
        """解析模块区块"""
        for module_name, module_config in modules.items():
            self._analyze_module_config(module_name, module_config, file_path)
    
    def _analyze_resource_config(self, resource: TerraformResource) -> None:
        """分析资源配置"""
        resource_type = resource.type
        config = resource.config
        
        # 安全检查
        self._check_resource_security(resource)
        
        # 最佳实践检查
        self._check_resource_best_practices(resource)
        
        # 依赖关系检查
        self._extract_resource_dependencies(resource)
        
        # 成本优化检查
        self._check_resource_cost_optimization(resource)
    
    def _check_resource_security(self, resource: TerraformResource) -> None:
        """检查资源安全配置"""
        resource_type = resource.type
        config = resource.config
        
        # 检查网络安全
        if resource_type in ['aws_security_group', 'azurerm_network_security_group']:
            self._check_security_group_security(resource)
        
        # 检查存储安全
        elif resource_type in ['aws_s3_bucket', 'azurerm_storage_account']:
            self._check_storage_security(resource)
        
        # 检查计算安全
        elif resource_type in ['aws_instance', 'azurerm_virtual_machine']:
            self._check_compute_security(resource)
        
        # 检查数据库安全
        elif resource_type in ['aws_rds_instance', 'azurerm_sql_database']:
            self._check_database_security(resource)
    
    def _check_security_group_security(self, resource: TerraformResource) -> None:
        """检查安全组安全配置"""
        config = resource.config
        
        # 检查是否开放所有端口
        if 'ingress' in config:
            for rule in config['ingress']:
                if rule.get('cidr_blocks') == ['0.0.0.0/0']:
                    from_port = rule.get('from_port', 0)
                    to_port = rule.get('to_port', 65535)
                    
                    if from_port == 0 and to_port == 65535:
                        resource.issues.append('开放所有端口到公网')
                        self.issues.append(TerraformIssue(
                            severity=Severity.CRITICAL,
                            type='security',
                            resource=resource.name,
                            message='安全组开放所有端口到公网',
                            suggestion='限制端口范围和源IP'
                        ))
                    elif from_port == 22 or from_port == 3389:
                        resource.issues.append('管理端口开放到公网')
                        self.issues.append(TerraformIssue(
                            severity=Severity.HIGH,
                            type='security',
                            resource=resource.name,
                            message='管理端口开放到公网',
                            suggestion='限制SSH/RDP访问源IP'
                        ))
        
        # 检查是否缺少出站规则
        if 'egress' not in config:
            resource.issues.append('缺少出站规则')
            self.issues.append(TerraformIssue(
                severity=Severity.MEDIUM,
                type='security',
                resource=resource.name,
                message='安全组缺少出站规则',
                suggestion='明确配置出站流量规则'
            ))
    
    def _check_storage_security(self, resource: TerraformResource) -> None:
        """检查存储安全配置"""
        config = resource.config
        
        # 检查S3桶公共访问
        if resource.type == 'aws_s3_bucket':
            if 'acl' in config and config['acl'] in ['public-read', 'public-read-write']:
                resource.issues.append('S3桶设置为公共访问')
                self.issues.append(TerraformIssue(
                    severity=Severity.CRITICAL,
                    type='security',
                    resource=resource.name,
                    message='S3桶设置为公共访问',
                    suggestion='使用私有访问或预签名URL'
                ))
            
            # 检查加密配置
            if 'server_side_encryption_configuration' not in config:
                resource.issues.append('S3桶未启用加密')
                self.issues.append(TerraformIssue(
                    severity=Severity.MEDIUM,
                    type='security',
                    resource=resource.name,
                    message='S3桶未启用服务器端加密',
                    suggestion='启用S3默认加密'
                ))
            
            # 检查版本控制
            if 'versioning' not in config:
                resource.issues.append('S3桶未启用版本控制')
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='reliability',
                    resource=resource.name,
                    message='S3桶未启用版本控制',
                    suggestion='启用S3版本防止意外删除'
                ))
    
    def _check_compute_security(self, resource: TerraformResource) -> None:
        """检查计算资源安全配置"""
        config = resource.config
        
        # 检查AMI/镜像
        if resource.type == 'aws_instance':
            if 'ami' in config:
                ami = config['ami']
                if isinstance(ami, str) and not ami.startswith('ami-'):
                    resource.issues.append('使用非标准AMI')
                    self.issues.append(TerraformIssue(
                        severity=Severity.MEDIUM,
                        type='security',
                        resource=resource.name,
                        message='使用非标准AMI',
                        suggestion='使用官方或经过验证的AMI'
                    ))
        
        # 检查密钥对
        if 'key_name' in config:
            key_name = config['key_name']
            if isinstance(key_name, str) and 'default' in key_name.lower():
                resource.issues.append('使用默认密钥对')
                self.issues.append(TerraformIssue(
                    severity=Severity.MEDIUM,
                    type='security',
                    resource=resource.name,
                    message='使用默认密钥对',
                    suggestion '创建专用的SSH密钥对'
                ))
    
    def _check_database_security(self, resource: TerraformResource) -> None:
        """检查数据库安全配置"""
        config = resource.config
        
        # 检查存储加密
        if 'storage_encrypted' not in config or not config['storage_encrypted']:
            resource.issues.append('数据库未启用存储加密')
            self.issues.append(TerraformIssue(
                severity=Severity.HIGH,
                type='security',
                resource=resource.name,
                message='数据库未启用存储加密',
                suggestion='启用数据库存储加密'
            ))
        
        # 检查备份配置
        if 'backup_retention_period' not in config or config['backup_retention_period'] == 0:
            resource.issues.append('数据库未启用备份')
            self.issues.append(TerraformIssue(
                severity=Severity.MEDIUM,
                type='reliability',
                resource=resource.name,
                message='数据库未启用自动备份',
                suggestion='配置自动备份策略'
            ))
        
        # 检查公开访问
        if 'publicly_accessible' in config and config['publicly_accessible']:
            resource.issues.append('数据库公开访问')
            self.issues.append(TerraformIssue(
                severity=Severity.CRITICAL,
                type='security',
                resource=resource.name,
                message='数据库允许公开访问',
                suggestion='禁用数据库公开访问'
            ))
    
    def _check_resource_best_practices(self, resource: TerraformResource) -> None:
        """检查资源最佳实践"""
        resource_type = resource.type
        config = resource.config
        
        # 检查标签
        if 'tags' not in config:
            resource.issues.append('资源缺少标签')
            self.issues.append(TerraformIssue(
                severity=Severity.LOW,
                type='best_practice',
                resource=resource.name,
                message='资源缺少标签',
                suggestion='添加Name、Environment等标签'
            ))
        else:
            tags = config['tags']
            if isinstance(tags, dict):
                if 'Name' not in tags:
                    resource.issues.append('资源缺少Name标签')
                    self.issues.append(TerraformIssue(
                        severity=Severity.LOW,
                        type='best_practice',
                        resource=resource.name,
                        message='资源缺少Name标签',
                        suggestion='添加Name标签便于识别'
                    ))
        
        # 检查资源命名
        if not re.match(r'^[a-z0-9_-]+$', resource.name):
            resource.issues.append('资源命名不规范')
            self.issues.append(TerraformIssue(
                severity=Severity.LOW,
                type='best_practice',
                resource=resource.name,
                message='资源命名不规范',
                suggestion='使用小写字母、数字、下划线和连字符'
            ))
    
    def _extract_resource_dependencies(self, resource: TerraformResource) -> None:
        """提取资源依赖关系"""
        config = resource.config
        
        # 查找资源引用
        content = str(config)
        
        # 查找${resource.type.resource_name.attr}模式
        dependency_pattern = r'\$\{([^}]+)\}'
        matches = re.findall(dependency_pattern, content)
        
        for match in matches:
            parts = match.split('.')
            if len(parts) >= 2 and parts[0] in ['resource', 'data', 'module']:
                if parts[0] == 'resource' and len(parts) >= 3:
                    ref_type = parts[1]
                    ref_name = parts[2]
                    resource.dependencies.add(f"{ref_type}.{ref_name}")
        
        # 查找implicit依赖
        self._find_implicit_dependencies(resource)
    
    def _find_implicit_dependencies(self, resource: TerraformResource) -> None:
        """查找隐式依赖"""
        resource_type = resource.type
        config = resource.config
        
        # 常见的隐式依赖关系
        implicit_deps = {
            'aws_instance': ['aws_subnet', 'aws_security_group', 'aws_key_pair'],
            'aws_rds_instance': ['aws_subnet', 'aws_security_group'],
            'aws_ebs_volume': ['aws_instance'],
            'aws_lb': ['aws_subnet', 'aws_security_group']
        }
        
        if resource_type in implicit_deps:
            for dep_type in implicit_deps[resource_type]:
                # 检查是否存在该类型的资源
                for other_resource in self.resources:
                    if other_resource.type == dep_type:
                        resource.dependencies.add(f"{dep_type}.{other_resource.name}")
    
    def _check_resource_cost_optimization(self, resource: TerraformResource) -> None:
        """检查资源成本优化"""
        resource_type = resource.type
        config = resource.config
        
        # 检查实例类型优化
        if resource_type == 'aws_instance':
            instance_type = config.get('instance_type', '')
            if instance_type in ['t2.micro', 't2.small']:
                resource.issues.append('使用较老的实例类型')
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='cost',
                    resource=resource.name,
                    message='使用较老的实例类型',
                    suggestion='考虑升级到t3或更新类型'
                ))
        
        # 检查存储优化
        elif resource_type == 'aws_ebs_volume':
            volume_type = config.get('type', 'gp2')
            if volume_type == 'gp2':
                resource.issues.append('使用较老的存储类型')
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='cost',
                    resource=resource.name,
                    message='使用gp2存储类型',
                    suggestion='考虑升级到gp3存储类型'
                ))
    
    def _analyze_dependencies(self) -> None:
        """分析资源依赖关系"""
        # 检查循环依赖
        self._check_circular_dependencies()
        
        # 检查依赖顺序
        self._check_dependency_order()
        
        # 检查缺失依赖
        self._check_missing_dependencies()
    
    def _check_circular_dependencies(self) -> None:
        """检查循环依赖"""
        # 构建依赖图
        dependency_graph = {}
        for resource in self.resources:
            dependency_graph[resource.name] = resource.dependencies
        
        # 检测循环
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for resource in self.resources:
            if resource.name not in visited:
                if has_cycle(resource.name):
                    self.issues.append(TerraformIssue(
                        severity=Severity.HIGH,
                        type='dependency',
                        resource=resource.name,
                        message='检测到循环依赖',
                        suggestion='重新设计资源依赖关系'
                    ))
    
    def _check_dependency_order(self) -> None:
        """检查依赖顺序"""
        # 这里可以实现依赖顺序检查逻辑
        pass
    
    def _check_missing_dependencies(self) -> None:
        """检查缺失依赖"""
        for resource in self.resources:
            for dep in resource.dependencies:
                dep_parts = dep.split('.')
                if len(dep_parts) >= 2:
                    dep_type = dep_parts[0]
                    dep_name = dep_parts[1]
                    
                    # 检查依赖的资源是否存在
                    found = False
                    for other_resource in self.resources:
                        if other_resource.type == dep_type and other_resource.name == dep_name:
                            found = True
                            break
                    
                    if not found:
                        resource.issues.append(f'缺失依赖资源: {dep}')
                        self.issues.append(TerraformIssue(
                            severity=Severity.MEDIUM,
                            type='dependency',
                            resource=resource.name,
                            message=f'缺失依赖资源: {dep}',
                            suggestion='创建或导入缺失的资源'
                        ))
    
    def _check_security(self) -> None:
        """检查整体安全配置"""
        # 检查提供商配置
        self._check_provider_security()
        
        # 检查变量安全
        self._check_variable_security()
        
        # 检查模块安全
        self._check_module_security()
    
    def _check_provider_security(self) -> None:
        """检查提供商安全配置"""
        # 这里可以实现提供商安全检查
        pass
    
    def _check_variable_security(self) -> None:
        """检查变量安全配置"""
        for var_name, var_config in self.variables.items():
            # 检查敏感变量
            if 'sensitive' not in var_config and any(
                keyword in var_name.lower() 
                for keyword in ['password', 'key', 'secret', 'token']
            ):
                self.issues.append(TerraformIssue(
                    severity=Severity.MEDIUM,
                    type='security',
                    resource=f'variable.{var_name}',
                    message='敏感变量未标记为sensitive',
                    suggestion='添加sensitive = true标记'
                ))
    
    def _check_module_security(self) -> None:
        """检查模块安全配置"""
        # 这里可以实现模块安全检查
        pass
    
    def _check_best_practices(self) -> None:
        """检查最佳实践"""
        # 检查文件结构
        self._check_file_structure()
        
        # 检查变量定义
        self._check_variable_definitions()
        
        # 检查输出定义
        self._check_output_definitions()
    
    def _check_file_structure(self) -> None:
        """检查文件结构"""
        required_files = ['main.tf', 'variables.tf', 'outputs.tf']
        
        for required_file in required_files:
            if not (self.workspace_path / required_file).exists():
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='structure',
                    resource='',
                    message=f'缺少标准文件: {required_file}',
                    suggestion='创建标准的Terraform文件结构'
                ))
    
    def _check_variable_definitions(self) -> None:
        """检查变量定义"""
        for var_name, var_config in self.variables.items():
            # 检查变量描述
            if 'description' not in var_config:
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='best_practice',
                    resource=f'variable.{var_name}',
                    message='变量缺少描述',
                    suggestion='添加变量说明文档'
                ))
            
            # 检查变量类型
            if 'type' not in var_config:
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='best_practice',
                    resource=f'variable.{var_name}',
                    message='变量缺少类型定义',
                    suggestion='明确定义变量类型'
                ))
    
    def _check_output_definitions(self) -> None:
        """检查输出定义"""
        for output_name, output_config in self.outputs.items():
            # 检查输出描述
            if 'description' not in output_config:
                self.issues.append(TerraformIssue(
                    severity=Severity.LOW,
                    type='best_practice',
                    resource=f'output.{output_name}',
                    message='输出缺少描述',
                    suggestion='添加输出说明文档'
                ))
            
            # 检查敏感输出
            if 'sensitive' not in output_config and any(
                keyword in output_name.lower()
                for keyword in ['password', 'key', 'secret', 'token']
            ):
                self.issues.append(TerraformIssue(
                    severity=Severity.MEDIUM,
                    type='security',
                    resource=f'output.{output_name}',
                    message='敏感输出未标记为sensitive',
                    suggestion='添加sensitive = true标记'
                ))
    
    def _analyze_cost_optimization(self) -> None:
        """分析成本优化"""
        # 检查资源标签成本分配
        self._check_cost_allocation_tags()
        
        # 检查资源大小优化
        self._check_resource_sizing()
        
        # 检查预留实例
        self._check_reserved_instances()
    
    def _check_cost_allocation_tags(self) -> None:
        """检查成本分配标签"""
        cost_tags = ['Environment', 'Owner', 'Project', 'CostCenter']
        
        for resource in self.resources:
            tags = resource.config.get('tags', {})
            if isinstance(tags, dict):
                missing_tags = [tag for tag in cost_tags if tag not in tags]
                if missing_tags:
                    resource.issues.append(f'缺少成本分配标签: {", ".join(missing_tags)}')
                    self.issues.append(TerraformIssue(
                        severity=Severity.LOW,
                        type='cost',
                        resource=resource.name,
                        message=f'缺少成本分配标签: {", ".join(missing_tags)}',
                        suggestion='添加成本分配标签便于成本分析'
                    ))
    
    def _check_resource_sizing(self) -> None:
        """检查资源配置"""
        # 这里可以实现资源大小检查
        pass
    
    def _check_reserved_instances(self) -> None:
        """检查预留实例"""
        # 这里可以实现预留实例检查
        pass
    
    def _analyze_provider_config(self, provider_name: str, provider_config: Dict[str, Any]) -> None:
        """分析提供商配置"""
        # 检查版本约束
        if 'version' not in provider_config:
            self.issues.append(TerraformIssue(
                severity=Severity.MEDIUM,
                type='best_practice',
                resource=f'provider.{provider_name}',
                message='提供商缺少版本约束',
                suggestion='指定提供商版本确保一致性'
            ))
        
        # 检查区域配置
        if provider_name == 'aws' and 'region' not in provider_config:
            self.issues.append(TerraformIssue(
                severity=Severity.MEDIUM,
                type='best_practice',
                resource=f'provider.{provider_name}',
                message='AWS提供商缺少区域配置',
                suggestion='指定默认区域'
            ))
    
    def _analyze_module_config(self, module_name: str, module_config: Dict[str, Any], file_path: str) -> None:
        """分析模块配置"""
        # 检查模块版本
        if 'version' not in module_config:
            self.issues.append(TerraformIssue(
                severity=Severity.MEDIUM,
                type='best_practice',
                resource=f'module.{module_name}',
                message='模块缺少版本约束',
                suggestion='指定模块版本确保一致性'
            ))
        
        # 检查模块源
        source = module_config.get('source', '')
        if source.startswith('./') or source.startswith('../'):
            # 本地模块
            module_path = self.workspace_path / source
            if not module_path.exists():
                self.issues.append(TerraformIssue(
                    severity=Severity.HIGH,
                    type='structure',
                    resource=f'module.{module_name}',
                    message='本地模块路径不存在',
                    suggestion='检查模块路径或创建模块目录'
                ))
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        summary = {
            'total_resources': len(self.resources),
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i.severity == Severity.CRITICAL]),
            'high_issues': len([i for i in self.issues if i.severity == Severity.HIGH]),
            'medium_issues': len([i for i in self.issues if i.severity == Severity.MEDIUM]),
            'low_issues': len([i for i in self.issues if i.severity == Severity.LOW]),
            'resource_types': self._count_resource_types()
        }
        
        recommendations = self._generate_recommendations()
        
        return {
            'summary': summary,
            'resources': [self._resource_to_dict(r) for r in self.resources],
            'issues': [self._issue_to_dict(i) for i in self.issues],
            'variables': self.variables,
            'outputs': self.outputs,
            'recommendations': recommendations,
            'health_score': self._calculate_health_score(summary)
        }
    
    def _count_resource_types(self) -> Dict[str, int]:
        """统计资源类型"""
        type_counts = {}
        for resource in self.resources:
            resource_type = resource.type
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
        return type_counts
    
    def _resource_to_dict(self, resource: TerraformResource) -> Dict[str, Any]:
        """将资源转换为字典"""
        return {
            'type': resource.type,
            'name': resource.name,
            'config': resource.config,
            'dependencies': list(resource.dependencies),
            'issues': resource.issues
        }
    
    def _issue_to_dict(self, issue: TerraformIssue) -> Dict[str, Any]:
        """将问题转换为字典"""
        return {
            'severity': issue.severity.value,
            'type': issue.type,
            'resource': issue.resource,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'line': issue.line
        }
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 基于问题类型生成建议
        issue_types = {}
        for issue in self.issues:
            issue_types[issue.type] = issue_types.get(issue.type, 0) + 1
        
        if issue_types.get('security', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'security',
                'message': f'发现{issue_types["security"]}个安全问题',
                'suggestion': '加强安全配置和访问控制'
            })
        
        if issue_types.get('cost', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'cost',
                'message': f'发现{issue_types["cost"]}个成本优化机会',
                'suggestion': '优化资源配置和标签管理'
            })
        
        if issue_types.get('best_practice', 0) > 0:
            recommendations.append({
                'priority': 'low',
                'type': 'best_practice',
                'message': f'发现{issue_types["best_practice"]}个最佳实践问题',
                'suggestion': '改进代码结构和配置规范'
            })
        
        return recommendations
    
    def _calculate_health_score(self, summary: Dict[str, int]) -> int:
        """计算健康评分"""
        score = 100
        
        score -= summary['critical_issues'] * 20
        score -= summary['high_issues'] * 10
        score -= summary['medium_issues'] * 5
        score -= summary['low_issues'] * 2
        
        return max(0, score)

# 使用示例
def main():
    # 分析Terraform基础设施
    analyzer = TerraformAnalyzer('./my-terraform-project')
    report = analyzer.analyze_infrastructure()
    
    print("Terraform基础设施分析报告:")
    print(f"健康评分: {report['health_score']}")
    print(f"资源总数: {report['summary']['total_resources']}")
    print(f"问题总数: {report['summary']['total_issues']}")
    
    print("\n资源类型统计:")
    for resource_type, count in report['summary']['resource_types'].items():
        print(f"- {resource_type}: {count}")
    
    print("\n优化建议:")
    for rec in report['recommendations']:
        print(f"- {rec['message']}: {rec['suggestion']}")

if __name__ == '__main__':
    main()
```

### CloudFormation分析器
```python
import json
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CloudFormationResource:
    """CloudFormation资源"""
    type: str
    logical_id: str
    properties: Dict[str, Any]
    dependencies: List[str]
    issues: List[str]

@dataclass
class CloudFormationIssue:
    """CloudFormation问题"""
    severity: str
    type: str
    resource: str
    message: str
    suggestion: str

class CloudFormationAnalyzer:
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.resources: List[CloudFormationResource] = []
        self.issues: List[CloudFormationIssue] = []
        self.parameters: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        
    def analyze_template(self) -> Dict[str, Any]:
        """分析CloudFormation模板"""
        try:
            # 解析模板
            template_data = self._parse_template()
            
            # 解析资源
            self._parse_resources(template_data)
            
            # 解析参数
            self._parse_parameters(template_data)
            
            # 解析输出
            self._parse_outputs(template_data)
            
            # 分析资源
            self._analyze_resources()
            
            # 生成报告
            return self._generate_report()
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def _parse_template(self) -> Dict[str, Any]:
        """解析模板文件"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if self.template_path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(content)
        elif self.template_path.suffix.lower() == '.json':
            return json.loads(content)
        else:
            raise ValueError('不支持的模板格式')
    
    def _parse_resources(self, template_data: Dict[str, Any]) -> None:
        """解析资源"""
        if 'Resources' not in template_data:
            self.issues.append(CloudFormationIssue(
                severity='high',
                type='structure',
                resource='',
                message='模板缺少Resources区块',
                suggestion='添加Resources区块定义资源'
            ))
            return
        
        resources = template_data['Resources']
        for logical_id, resource_def in resources.items():
            if 'Type' not in resource_def:
                self.issues.append(CloudFormationIssue(
                    severity='critical',
                    type='structure',
                    resource=logical_id,
                    message='资源缺少Type定义',
                    suggestion='指定资源类型'
                ))
                continue
            
            resource = CloudFormationResource(
                type=resource_def['Type'],
                logical_id=logical_id,
                properties=resource_def.get('Properties', {}),
                dependencies=[],
                issues=[]
            )
            
            self.resources.append(resource)
    
    def _parse_parameters(self, template_data: Dict[str, Any]) -> None:
        """解析参数"""
        if 'Parameters' in template_data:
            self.parameters = template_data['Parameters']
    
    def _parse_outputs(self, template_data: Dict[str, Any]) -> None:
        """解析输出"""
        if 'Outputs' in template_data:
            self.outputs = template_data['Outputs']
    
    def _analyze_resources(self) -> None:
        """分析资源"""
        for resource in self.resources:
            # 安全检查
            self._check_resource_security(resource)
            
            # 最佳实践检查
            self._check_resource_best_practices(resource)
            
            # 依赖关系检查
            self._extract_dependencies(resource)
    
    def _check_resource_security(self, resource: CloudFormationResource) -> None:
        """检查资源安全配置"""
        resource_type = resource.type
        properties = resource.properties
        
        # 检查安全组
        if resource_type == 'AWS::EC2::SecurityGroup':
            self._check_security_group_security(resource)
        
        # 检查S3桶
        elif resource_type == 'AWS::S3::Bucket':
            self._check_s3_bucket_security(resource)
        
        # 检查EC2实例
        elif resource_type == 'AWS::EC2::Instance':
            self._check_ec2_instance_security(resource)
    
    def _check_security_group_security(self, resource: CloudFormationResource) -> None:
        """检查安全组安全配置"""
        properties = resource.properties
        
        # 检查入站规则
        if 'SecurityGroupIngress' in properties:
            ingress_rules = properties['SecurityGroupIngress']
            if isinstance(ingress_rules, list):
                for rule in ingress_rules:
                    if rule.get('CidrIp') == '0.0.0.0/0':
                        from_port = rule.get('FromPort', 0)
                        to_port = rule.get('ToPort', 65535)
                        
                        if from_port == 0 and to_port == 65535:
                            resource.issues.append('开放所有端口到公网')
                            self.issues.append(CloudFormationIssue(
                                severity='critical',
                                type='security',
                                resource=resource.logical_id,
                                message='安全组开放所有端口到公网',
                                suggestion='限制端口范围和源IP'
                            ))
    
    def _check_s3_bucket_security(self, resource: CloudFormationResource) -> None:
        """检查S3桶安全配置"""
        properties = resource.properties
        
        # 检查公共访问
        if 'AccessControl' in properties and properties['AccessControl'] == 'PublicRead':
            resource.issues.append('S3桶设置为公共读取')
            self.issues.append(CloudFormationIssue(
                severity='critical',
                type='security',
                resource=resource.logical_id,
                message='S3桶设置为公共读取',
                suggestion='使用私有访问控制'
            ))
    
    def _check_ec2_instance_security(self, resource: CloudFormationResource) -> None:
        """检查EC2实例安全配置"""
        properties = resource.properties
        
        # 检查IAM实例配置文件
        if 'IamInstanceProfile' not in properties:
            resource.issues.append('EC2实例缺少IAM角色')
            self.issues.append(CloudFormationIssue(
                severity='medium',
                type='security',
                resource=resource.logical_id,
                message='EC2实例缺少IAM角色',
                suggestion='为实例分配适当的IAM角色'
            ))
    
    def _check_resource_best_practices(self, resource: CloudFormationResource) -> None:
        """检查资源最佳实践"""
        properties = resource.properties
        
        # 检查标签
        if 'Tags' not in properties:
            resource.issues.append('资源缺少标签')
            self.issues.append(CloudFormationIssue(
                severity='low',
                type='best_practice',
                resource=resource.logical_id,
                message='资源缺少标签',
                suggestion='添加Name、Environment等标签'
            ))
    
    def _extract_dependencies(self, resource: CloudFormationResource) -> None:
        """提取依赖关系"""
        properties = resource.properties
        
        # 查找Ref函数
        content = str(properties)
        ref_pattern = r'Ref":\s*"([^"]+)"'
        matches = re.findall(ref_pattern, content)
        
        for match in matches:
            # 检查是否是资源引用
            for other_resource in self.resources:
                if other_resource.logical_id == match:
                    resource.dependencies.append(match)
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        summary = {
            'total_resources': len(self.resources),
            'total_issues': len(self.issues),
            'resource_types': self._count_resource_types()
        }
        
        return {
            'summary': summary,
            'resources': [self._resource_to_dict(r) for r in self.resources],
            'issues': [self._issue_to_dict(i) for i in self.issues],
            'parameters': self.parameters,
            'outputs': self.outputs
        }
    
    def _count_resource_types(self) -> Dict[str, int]:
        """统计资源类型"""
        type_counts = {}
        for resource in self.resources:
            resource_type = resource.type
            type_counts[resource_type] = type_counts.get(resource_type, 0) + 1
        return type_counts
    
    def _resource_to_dict(self, resource: CloudFormationResource) -> Dict[str, Any]:
        """将资源转换为字典"""
        return {
            'type': resource.type,
            'logical_id': resource.logical_id,
            'properties': resource.properties,
            'dependencies': resource.dependencies,
            'issues': resource.issues
        }
    
    def _issue_to_dict(self, issue: CloudFormationIssue) -> Dict[str, Any]:
        """将问题转换为字典"""
        return {
            'severity': issue.severity,
            'type': issue.type,
            'resource': issue.resource,
            'message': issue.message,
            'suggestion': issue.suggestion
        }

# 使用示例
def main():
    # 分析CloudFormation模板
    analyzer = CloudFormationAnalyzer('./template.yaml')
    report = analyzer.analyze_template()
    
    print("CloudFormation模板分析报告:")
    print(f"资源总数: {report['summary']['total_resources']}")
    print(f"问题总数: {report['summary']['total_issues']}")
    
    print("\n资源类型统计:")
    for resource_type, count in report['summary']['resource_types'].items():
        print(f"- {resource_type}: {count}")

if __name__ == '__main__':
    main()
```

## 基础设施即代码最佳实践

### 代码组织
1. **模块化设计**: 将相关资源组织成模块
2. **环境分离**: 使用不同的配置文件管理环境
3. **版本控制**: 所有IaC代码纳入版本控制
4. **文档完善**: 为变量和输出添加描述
5. **命名规范**: 使用一致的命名约定

### 安全实践
1. **最小权限**: 遵循最小权限原则
2. **密钥管理**: 使用密钥管理服务
3. **网络安全**: 配置适当的网络规则
4. **加密存储**: 启用存储和传输加密
5. **审计日志**: 启用操作审计和日志

### 成本优化
1. **资源标签**: 添加成本分配标签
2. **实例优化**: 选择合适的实例类型
3. **存储优化**: 使用经济高效的存储类型
4. **预留实例**: 购买预留实例降低成本
5. **监控成本**: 定期监控和分析成本

### 可靠性实践
1. **高可用设计**: 设计多可用区架构
2. **备份策略**: 配置自动备份和恢复
3. **健康检查**: 配置健康检查和监控
4. **故障转移**: 实施自动故障转移
5. **灾难恢复**: 制定灾难恢复计划

## 相关技能

- **ci-cd-pipeline** - CI/CD流水线集成
- **monitoring-alerting** - 基础设施监控
- **security-best-practices** - 安全最佳实践
- **cloud-native/kubernetes-basics** - Kubernetes基础
