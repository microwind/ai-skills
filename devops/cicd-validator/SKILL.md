---
name: CI/CD验证器
description: "当验证CI/CD流水线时，检查配置正确性，验证安全策略，分析性能瓶颈。审查工作流配置，检查部署流程，和最佳实践。"
license: MIT
---

# CI/CD验证器技能

## 概述
CI/CD验证器用于检查流水线配置的正确性和最佳实践。不当的CI/CD配置会导致安全漏洞、性能问题和部署失败。在部署到生产环境前需要全面验证流水线配置。

**核心原则**: 好的CI/CD验证应该全面、自动化、持续、安全。坏的CI/CD验证会遗漏关键问题，导致生产环境故障。

## 何时使用

**始终:**
- 设置CI/CD流水线时
- 审查GitHub Actions工作流时
- 优化流水线性能时
- 调试流水线故障时
- 规划部署策略时
- 流水线安全审计时

**触发短语:**
- "验证CI/CD流水线"
- "审查GitHub Actions工作流"
- "优化流水线性能"
- "为什么构建失败？"
- "设计部署策略"
- "检查流水线安全"

## CI/CD验证功能

### 流水线结构验证
- 阶段顺序检查
- 并行作业优化
- 依赖关系管理
- 构建产物处理

### 质量检查验证
- 测试覆盖率强制执行
- 代码风格验证
- 安全扫描配置
- 依赖检查设置

### 部署安全验证
- 环境分离检查
- 审批门禁设置
- 回滚策略验证
- 部署后健康检查

## 常见CI/CD验证问题

### 流水线缓慢问题
```
问题:
测试串行执行而非并行，构建时间30分钟

后果:
- 开发者反馈缓慢
- 部署频率低
- 形成瓶颈

解决方案:
1. 并行执行测试
2. 缓存依赖项
3. 优化构建步骤
4. 使用矩阵策略
```

### 缺少测试覆盖率门禁
```
问题:
测试覆盖率降低时流水线不会失败

后果:
- 代码质量随时间下降
- 缺陷无法捕获
- 技术债务累积

解决方案:
1. 添加覆盖率阈值检查
2. 低于阈值时失败
3. 设置覆盖率趋势监控
4. 集成质量门禁
```

### 缺少手动审批门禁
```
问题:
任何提交都会自动部署到生产环境

后果:
- 损坏功能部署
- 可能数据丢失
- 停机风险

解决方案:
1. 生产部署前添加审批门禁
2. 设置多级审批流程
3. 配置环境保护规则
4. 实施部署策略
```

### 安全配置问题
```
问题:
敏感信息泄露，权限配置不当

后果:
- 安全漏洞
- 数据泄露风险
- 合规问题

解决方案:
1. 使用密钥管理服务
2. 配置最小权限原则
3. 添加安全扫描
4. 实施访问控制
```

## CI/CD验证检查清单

### 基础配置
- [ ] 所有测试自动运行
- [ ] 代码质量检查强制执行标准
- [ ] 安全扫描已启用
- [ ] 构建产物正确版本化
- [ ] 环境正确分离
- [ ] 生产环境需要手动审批
- [ ] 部署健康检查
- [ ] 回滚程序已文档化

### 性能优化
- [ ] 并行作业配置
- [ ] 依赖缓存启用
- [ ] 增量构建设置
- [ ] 资源限制合理
- [ ] 构建时间监控

### 安全配置
- [ ] 敏感信息不在配置文件中
- [ ] 使用密钥管理
- [ ] 权限最小化原则
- [ ] 安全扫描集成
- [ ] 审计日志启用

### 监控告警
- [ ] 构建状态监控
- [ ] 部署状态跟踪
- [ ] 性能指标收集
- [ ] 错误告警配置
- [ ] 失败通知机制

## 代码实现示例

### CI/CD验证器
```python
import yaml
import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    """问题严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ValidationType(Enum):
    """验证类型"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COMPLIANCE = "compliance"

@dataclass
class ValidationIssue:
    """验证问题"""
    severity: Severity
    type: ValidationType
    file: str
    resource: str
    field: str
    message: str
    suggestion: str
    line: Optional[int] = None

@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    issues: List[ValidationIssue]
    score: int
    summary: Dict[str, Any]

class CICDValidator:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.issues: List[ValidationIssue] = []
        self.validation_rules = self._load_validation_rules()
        
    def validate_pipeline(self) -> ValidationResult:
        """验证CI/CD流水线"""
        try:
            # 扫描CI/CD配置文件
            self._scan_ci_files()
            
            # 验证GitHub Actions
            self._validate_github_actions()
            
            # 验证GitLab CI
            self._validate_gitlab_ci()
            
            # 验证Jenkins
            self._validate_jenkins()
            
            # 验证安全配置
            self._validate_security()
            
            # 验证性能配置
            self._validate_performance()
            
            # 生成验证结果
            return self._generate_result()
            
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                type=ValidationType.RELIABILITY,
                file="system",
                resource="",
                field="",
                message=f"验证过程失败: {e}",
                suggestion="检查系统配置和权限"
            ))
            return self._generate_result()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """加载验证规则"""
        return {
            'security_rules': {
                'secrets_in_files': Severity.CRITICAL,
                'insecure_permissions': Severity.HIGH,
                'missing_security_scan': Severity.MEDIUM,
                'plain_text_credentials': Severity.CRITICAL
            },
            'performance_rules': {
                'no_parallel_jobs': Severity.MEDIUM,
                'no_cache': Severity.LOW,
                'sequential_tests': Severity.MEDIUM,
                'large_artifacts': Severity.LOW
            },
            'reliability_rules': {
                'no_approval_gates': Severity.HIGH,
                'no_health_checks': Severity.MEDIUM,
                'no_rollback': Severity.HIGH,
                'single_point_failure': Severity.MEDIUM
            },
            'compliance_rules': {
                'no_audit_logs': Severity.MEDIUM,
                'missing_documentation': Severity.LOW,
                'no_version_control': Severity.HIGH,
                'no_backup_strategy': Severity.MEDIUM
            }
        }
    
    def _scan_ci_files(self) -> None:
        """扫描CI/CD配置文件"""
        ci_files = []
        
        # GitHub Actions
        github_workflows = self.repo_path / '.github' / 'workflows'
        if github_workflows.exists():
            ci_files.extend(github_workflows.glob('*.yml'))
            ci_files.extend(github_workflows.glob('*.yaml'))
        
        # GitLab CI
        gitlab_ci = self.repo_path / '.gitlab-ci.yml'
        if gitlab_ci.exists():
            ci_files.append(gitlab_ci)
        
        # Jenkins
        jenkinsfile = self.repo_path / 'Jenkinsfile'
        if jenkinsfile.exists():
            ci_files.append(jenkinsfile)
        
        # Azure DevOps
        azure_pipelines = self.repo_path / 'azure-pipelines.yml'
        if azure_pipelines.exists():
            ci_files.append(azure_pipelines)
        
        if not ci_files:
            self.issues.append(ValidationIssue(
                severity=Severity.HIGH,
                type=ValidationType.COMPLIANCE,
                file="CI/CD",
                resource="",
                field="",
                message="未找到CI/CD配置文件",
                suggestion="创建CI/CD配置文件实现自动化"
            ))
    
    def _validate_github_actions(self) -> None:
        """验证GitHub Actions配置"""
        github_workflows = self.repo_path / '.github' / 'workflows'
        if not github_workflows.exists():
            return
        
        for workflow_file in github_workflows.glob('*.yml'):
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._validate_github_workflow(content, str(workflow_file))
            
            except Exception as e:
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.RELIABILITY,
                    file=str(workflow_file),
                    resource="",
                    field="",
                    message=f"工作流文件读取失败: {e}",
                    suggestion="检查文件格式和权限"
                ))
    
    def _validate_github_workflow(self, content: str, file_path: str) -> None:
        """验证GitHub工作流配置"""
        try:
            yaml_data = yaml.safe_load(content)
            
            # 检查触发器配置
            self._check_triggers(yaml_data, file_path)
            
            # 检查作业配置
            if 'jobs' in yaml_data:
                self._validate_jobs(yaml_data['jobs'], file_path)
            
            # 检查环境变量
            self._check_env_vars(yaml_data, file_path)
            
            # 检查安全配置
            self._check_workflow_security(yaml_data, file_path)
            
            # 检查性能配置
            self._check_workflow_performance(yaml_data, file_path)
        
        except yaml.YAMLError as e:
            self.issues.append(ValidationIssue(
                severity=Severity.CRITICAL,
                type=ValidationType.RELIABILITY,
                file=file_path,
                resource="",
                field="",
                message=f"YAML语法错误: {e}",
                suggestion="修复YAML语法错误"
            ))
    
    def _check_triggers(self, yaml_data: Dict[str, Any], file_path: str) -> None:
        """检查触发器配置"""
        if 'on' not in yaml_data and 'triggers' not in yaml_data:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.COMPLIANCE,
                file=file_path,
                resource="workflow",
                field="triggers",
                message="缺少触发器配置",
                suggestion="配置push、pull_request等触发器"
            ))
        
        # 检查是否过于频繁的触发
        if 'on' in yaml_data:
            triggers = yaml_data['on']
            if isinstance(triggers, dict) and 'schedule' in triggers:
                schedule = triggers['schedule']
                if isinstance(schedule, list) and len(schedule) > 10:
                    self.issues.append(ValidationIssue(
                        severity=Severity.LOW,
                        type=ValidationType.PERFORMANCE,
                        file=file_path,
                        resource="workflow",
                        field="schedule",
                        message="计划触发过于频繁",
                        suggestion="减少不必要的计划触发"
                    ))
    
    def _validate_jobs(self, jobs: Dict[str, Any], file_path: str) -> None:
        """验证作业配置"""
        for job_name, job_config in jobs.items():
            # 检查runner配置
            if 'runs-on' not in job_config:
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.RELIABILITY,
                    file=file_path,
                    resource=job_name,
                    field="runs-on",
                    message=f"作业{job_name}缺少runner配置",
                    suggestion="指定运行环境"
                ))
            
            # 检查步骤配置
            if 'steps' not in job_config:
                self.issues.append(ValidationIssue(
                    severity=Severity.HIGH,
                    type=ValidationType.RELIABILITY,
                    file=file_path,
                    resource=job_name,
                    field="steps",
                    message=f"作业{job_name}缺少执行步骤",
                    suggestion="添加必要的构建和测试步骤"
                ))
            else:
                self._validate_job_steps(job_config['steps'], job_name, file_path)
            
            # 检查并行配置
            if 'strategy' not in job_config and 'test' in job_name.lower():
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.PERFORMANCE,
                    file=file_path,
                    resource=job_name,
                    field="strategy",
                    message=f"测试作业{job_name}未配置并行执行",
                    suggestion="使用matrix策略并行执行测试"
                ))
    
    def _validate_job_steps(self, steps: List[Dict[str, Any]], job_name: str, file_path: str) -> None:
        """验证作业步骤"""
        has_checkout = False
        has_test = False
        has_security_scan = False
        
        for step in steps:
            if 'uses' in step:
                # GitHub Actions
                if 'actions/checkout' in step['uses']:
                    has_checkout = True
                elif 'security' in step['uses'].lower() or 'scan' in step['uses'].lower():
                    has_security_scan = True
                elif 'test' in step['uses'].lower():
                    has_test = True
            elif 'run' in step:
                # 自定义命令
                command = step['run']
                if 'checkout' in command.lower() or 'clone' in command.lower():
                    has_checkout = True
                elif 'test' in command.lower():
                    has_test = True
                elif 'security' in command.lower() or 'scan' in command.lower():
                    has_security_scan = True
        
        # 检查必要步骤
        if not has_checkout:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.RELIABILITY,
                file=file_path,
                resource=job_name,
                field="steps",
                message=f"作业{job_name}缺少代码检出步骤",
                suggestion="添加actions/checkout步骤"
            ))
        
        if not has_test and 'test' in job_name.lower():
            self.issues.append(ValidationIssue(
                severity=Severity.HIGH,
                type=ValidationType.RELIABILITY,
                file=file_path,
                resource=job_name,
                field="steps",
                message=f"测试作业{job_name}缺少测试步骤",
                suggestion="添加测试执行命令"
            ))
        
        if not has_security_scan and 'build' in job_name.lower():
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.SECURITY,
                file=file_path,
                resource=job_name,
                field="steps",
                message=f"构建作业{job_name}缺少安全扫描",
                suggestion="添加代码安全扫描步骤"
            ))
    
    def _check_env_vars(self, yaml_data: Dict[str, Any], file_path: str) -> None:
        """检查环境变量配置"""
        content = str(yaml_data)
        
        # 检查敏感信息泄露
        sensitive_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]',
            r'credential\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues.append(ValidationIssue(
                    severity=Severity.CRITICAL,
                    type=ValidationType.SECURITY,
                    file=file_path,
                    resource="env",
                    field="secrets",
                    message="可能存在敏感信息泄露",
                    suggestion="使用GitHub secrets管理敏感信息"
                ))
        
        # 检查是否使用secrets
        if 'secrets' not in content and 'env' in content:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.SECURITY,
                file=file_path,
                resource="env",
                field="secrets",
                message="未使用secrets管理环境变量",
                suggestion="使用GitHub secrets替代明文环境变量"
            ))
    
    def _check_workflow_security(self, yaml_data: Dict[str, Any], file_path: str) -> None:
        """检查工作流安全配置"""
        # 检查权限配置
        if 'permissions' not in yaml_data:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.SECURITY,
                file=file_path,
                resource="workflow",
                field="permissions",
                message="缺少权限配置",
                suggestion="配置最小权限原则"
            ))
        
        # 检查是否使用第三方Action
        content = str(yaml_data)
        if 'uses:' in content:
            # 检查是否使用固定版本
            uses_pattern = r'uses:\s*([^\n@]+)@([^\n\s]+)'
            matches = re.findall(uses_pattern, content)
            
            for action, version in matches:
                if version in ['main', 'master', 'latest']:
                    self.issues.append(ValidationIssue(
                        severity=Severity.HIGH,
                        type=ValidationType.SECURITY,
                        file=file_path,
                        resource="action",
                        field="version",
                        message=f"Action {action} 使用浮动版本 {version}",
                        suggestion="使用固定版本号或commit SHA"
                    ))
    
    def _check_workflow_performance(self, yaml_data: Dict[str, Any], file_path: str) -> None:
        """检查工作流性能配置"""
        content = str(yaml_data)
        
        # 检查缓存配置
        if 'cache' not in content:
            self.issues.append(ValidationIssue(
                severity=Severity.LOW,
                type=ValidationType.PERFORMANCE,
                file=file_path,
                resource="workflow",
                field="cache",
                message="缺少缓存配置",
                suggestion="配置依赖缓存提升构建速度"
            ))
        
        # 检查并发配置
        if 'concurrency' not in content:
            self.issues.append(ValidationIssue(
                severity=Severity.LOW,
                type=ValidationType.PERFORMANCE,
                file=file_path,
                resource="workflow",
                field="concurrency",
                message="缺少并发控制",
                suggestion="配置并发控制避免资源浪费"
            ))
    
    def _validate_gitlab_ci(self) -> None:
        """验证GitLab CI配置"""
        gitlab_ci = self.repo_path / '.gitlab-ci.yml'
        if not gitlab_ci.exists():
            return
        
        try:
            with open(gitlab_ci, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_data = yaml.safe_load(content)
            
            # 检查基本结构
            if 'stages' not in yaml_data:
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.COMPLIANCE,
                    file=str(gitlab_ci),
                    resource="",
                    field="stages",
                    message="缺少stages定义",
                    suggestion="定义构建、测试、部署等阶段"
                ))
            
            # 检查作业配置
            jobs = {k: v for k, v in yaml_data.items() if k != 'stages' and not k.startswith('.')}
            for job_name, job_config in jobs.items():
                self._validate_gitlab_job(job_config, job_name, str(gitlab_ci))
        
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.RELIABILITY,
                file=str(gitlab_ci),
                resource="",
                field="",
                message=f"GitLab CI配置验证失败: {e}",
                suggestion="检查配置文件格式"
            ))
    
    def _validate_gitlab_job(self, job_config: Dict[str, Any], job_name: str, file_path: str) -> None:
        """验证GitLab作业配置"""
        # 检查脚本配置
        if 'script' not in job_config:
            self.issues.append(ValidationIssue(
                severity=Severity.HIGH,
                type=ValidationType.RELIABILITY,
                file=file_path,
                resource=job_name,
                field="script",
                message=f"作业{job_name}缺少执行脚本",
                suggestion="添加script或使用预定义模板"
            ))
        
        # 检查artifacts配置
        if 'artifacts' in job_config:
            artifacts = job_config['artifacts']
            if isinstance(artifacts, dict) and 'expire_in' not in artifacts:
                self.issues.append(ValidationIssue(
                    severity=Severity.LOW,
                    type=ValidationType.PERFORMANCE,
                    file=file_path,
                    resource=job_name,
                    field="artifacts",
                    message=f"作业{job_name}的artifacts未设置过期时间",
                    suggestion="设置expire_in避免存储浪费"
                ))
        
        # 检查only/except规则
        if 'only' not in job_config and 'except' not in job_config and 'rules' not in job_config:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.COMPLIANCE,
                file=file_path,
                resource=job_name,
                field="rules",
                message=f"作业{job_name}缺少执行条件",
                suggestion="配置only/except/rules控制作业执行"
            ))
    
    def _validate_jenkins(self) -> None:
        """验证Jenkins配置"""
        jenkinsfile = self.repo_path / 'Jenkinsfile'
        if not jenkinsfile.exists():
            return
        
        try:
            with open(jenkinsfile, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查pipeline定义
            if 'pipeline' not in content:
                self.issues.append(ValidationIssue(
                    severity=Severity.HIGH,
                    type=ValidationType.COMPLIANCE,
                    file=str(jenkinsfile),
                    resource="",
                    field="pipeline",
                    message="缺少pipeline定义",
                    suggestion="定义Jenkins pipeline结构"
                ))
            
            # 检查agent配置
            if 'agent' not in content:
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.RELIABILITY,
                    file=str(jenkinsfile),
                    resource="",
                    field="agent",
                    message="缺少agent配置",
                    suggestion="指定执行agent"
                ))
            
            # 检查stage配置
            stages = re.findall(r'sage\s*\([\'"]([^\'"]+)[\'"]\)', content)
            if len(stages) == 0:
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.COMPLIANCE,
                    file=str(jenkinsfile),
                    resource="",
                    field="stages",
                    message="未定义构建阶段",
                    suggestion="添加build、test、deploy等阶段"
                ))
        
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.RELIABILITY,
                file=str(jenkinsfile),
                resource="",
                field="",
                message=f"Jenkins配置验证失败: {e}",
                suggestion="检查Jenkinsfile语法"
            ))
    
    def _validate_security(self) -> None:
        """验证安全配置"""
        # 检查安全扫描配置
        security_files = [
            '.github/dependabot.yml',
            '.github/CODEOWNERS',
            'sonar-project.properties',
            '.security-scan.yml'
        ]
        
        security_config_found = False
        for security_file in security_files:
            if (self.repo_path / security_file).exists():
                security_config_found = True
                break
        
        if not security_config_found:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.SECURITY,
                file="security",
                resource="",
                field="",
                message="未找到安全配置文件",
                suggestion="添加安全扫描配置"
            ))
    
    def _validate_performance(self) -> None:
        """验证性能配置"""
        # 检查构建工具配置
        build_files = [
            'package.json',
            'pom.xml',
            'build.gradle',
            'Cargo.toml',
            'go.mod'
        ]
        
        for build_file in build_files:
            file_path = self.repo_path / build_file
            if file_path.exists():
                self._validate_build_file(file_path)
    
    def _validate_build_file(self, build_file: Path) -> None:
        """验证构建文件"""
        try:
            with open(build_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if build_file.name == 'package.json':
                self._validate_package_json(content, str(build_file))
            elif build_file.name == 'pom.xml':
                self._validate_pom_xml(content, str(build_file))
        
        except Exception as e:
            self.issues.append(ValidationIssue(
                severity=Severity.LOW,
                type=ValidationType.RELIABILITY,
                file=str(build_file),
                resource="",
                field="",
                message=f"构建文件验证失败: {e}",
                suggestion="检查文件格式"
            ))
    
    def _validate_package_json(self, content: str, file_path: str) -> None:
        """验证package.json"""
        try:
            package_data = json.loads(content)
            
            # 检查scripts
            if 'scripts' not in package_data:
                self.issues.append(ValidationIssue(
                    severity=Severity.MEDIUM,
                    type=ValidationType.COMPLIANCE,
                    file=file_path,
                    resource="",
                    field="scripts",
                    message="缺少构建脚本",
                    suggestion="添加build、test等npm脚本"
                ))
        
        except json.JSONDecodeError as e:
            self.issues.append(ValidationIssue(
                severity=Severity.HIGH,
                type=ValidationType.RELIABILITY,
                file=file_path,
                resource="",
                field="",
                message=f"JSON语法错误: {e}",
                suggestion="修复JSON语法错误"
            ))
    
    def _validate_pom_xml(self, content: str, file_path: str) -> None:
        """验证pom.xml"""
        # 检查是否有测试插件
        if 'maven-surefire-plugin' not in content:
            self.issues.append(ValidationIssue(
                severity=Severity.MEDIUM,
                type=ValidationType.COMPLIANCE,
                file=file_path,
                resource="",
                field="plugins",
                message="缺少测试插件配置",
                suggestion="添加maven-surefire-plugin"
            ))
    
    def _generate_result(self) -> ValidationResult:
        """生成验证结果"""
        # 计算评分
        score = self._calculate_score()
        
        # 生成摘要
        summary = self._generate_summary()
        
        # 判断是否有效
        is_valid = score >= 80 and not any(
            issue.severity == Severity.CRITICAL for issue in self.issues
        )
        
        return ValidationResult(
            is_valid=is_valid,
            issues=self.issues,
            score=score,
            summary=summary
        )
    
    def _calculate_score(self) -> int:
        """计算验证评分"""
        score = 100
        
        for issue in self.issues:
            if issue.severity == Severity.CRITICAL:
                score -= 20
            elif issue.severity == Severity.HIGH:
                score -= 10
            elif issue.severity == Severity.MEDIUM:
                score -= 5
            elif issue.severity == Severity.LOW:
                score -= 2
        
        return max(0, score)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成验证摘要"""
        issue_counts = {
            'total': len(self.issues),
            'critical': len([i for i in self.issues if i.severity == Severity.CRITICAL]),
            'high': len([i for i in self.issues if i.severity == Severity.HIGH]),
            'medium': len([i for i in self.issues if i.severity == Severity.MEDIUM]),
            'low': len([i for i in self.issues if i.severity == Severity.LOW])
        }
        
        type_counts = {}
        for issue in self.issues:
            type_name = issue.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'issue_counts': issue_counts,
            'type_counts': type_counts,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于问题类型生成建议
        type_counts = {}
        for issue in self.issues:
            type_name = issue.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        if type_counts.get('security', 0) > 0:
            recommendations.append("加强安全配置，使用密钥管理服务")
        
        if type_counts.get('performance', 0) > 0:
            recommendations.append("优化性能配置，启用缓存和并行执行")
        
        if type_counts.get('reliability', 0) > 0:
            recommendations.append("提升可靠性，添加审批门禁和健康检查")
        
        if type_counts.get('compliance', 0) > 0:
            recommendations.append("完善合规配置，添加文档和审计日志")
        
        return recommendations

# 使用示例
def main():
    # 验证CI/CD流水线
    validator = CICDValidator('./my-project')
    result = validator.validate_pipeline()
    
    print("CI/CD验证结果:")
    print(f"是否有效: {result.is_valid}")
    print(f"评分: {result.score}")
    
    print("\n问题统计:")
    summary = result.summary
    issue_counts = summary['issue_counts']
    print(f"总问题数: {issue_counts['total']}")
    print(f"严重问题: {issue_counts['critical']}")
    print(f"高优先级: {issue_counts['high']}")
    print(f"中优先级: {issue_counts['medium']}")
    print(f"低优先级: {issue_counts['low']}")
    
    print("\n改进建议:")
    for rec in summary['recommendations']:
        print(f"- {rec}")
    
    print("\n详细问题:")
    for issue in result.issues:
        print(f"- [{issue.severity.value.upper()}] {issue.message}")
        print(f"  建议: {issue.suggestion}")

if __name__ == '__main__':
    main()
```

## CI/CD验证最佳实践

### 验证策略
1. **分层验证**: 基础配置、安全、性能、合规
2. **自动化验证**: 集成到CI/CD流水线中
3. **持续监控**: 定期重新验证配置
4. **评分机制**: 量化配置质量
5. **改进建议**: 提供具体的优化方案

### 安全验证
1. **敏感信息检查**: 确保无明文密钥
2. **权限验证**: 最小权限原则
3. **依赖扫描**: 检查第三方组件安全
4. **访问控制**: 验证访问控制配置
5. **审计日志**: 确保操作可追溯

### 性能验证
1. **并行执行**: 检查并行配置
2. **缓存策略**: 验证缓存配置
3. **资源优化**: 检查资源配置
4. **构建时间**: 分析构建性能
5. **并发控制**: 验证并发设置

### 可靠性验证
1. **错误处理**: 检查错误处理机制
2. **重试策略**: 验证重试配置
3. **健康检查**: 确保健康检查配置
4. **回滚策略**: 验证回滚机制
5. **监控告警**: 检查监控配置

## 相关技能

- **ci-cd-pipeline** - CI/CD流水线设计和配置
- **security-best-practices** - 安全最佳实践
- **infrastructure-as-code** - 基础设施即代码
- **monitoring-alerting** - 监控告警
