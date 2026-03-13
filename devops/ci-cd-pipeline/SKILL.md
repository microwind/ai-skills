---
name: CI/CD流水线
description: "当构建CI/CD流水线时，分析构建流程，优化部署策略，解决集成问题。验证自动化测试，设计持续集成，和最佳实践。"
license: MIT
---

# CI/CD流水线技能

## 概述
CI/CD流水线是现代软件交付的核心。不当的CI/CD配置会导致构建缓慢、部署失败和质量问题。在设计CI/CD流水线前需要仔细分析交付需求。

**核心原则**: 好的CI/CD流水线应该快速、可靠、自动化、可监控。坏的CI/CD流水线会导致构建瓶颈、部署风险和质量问题。

## 何时使用

**始终:**
- 设计自动化构建时
- 配置持续集成时
- 实现自动部署时
- 优化交付流程时
- 监控流水线性能时

**触发短语:**
- "CI/CD流水线"
- "持续集成部署"
- "自动化构建"
- "部署策略优化"
- "流水线设计"
- "DevOps实践"

## CI/CD流水线功能

### 构建系统
- 代码编译构建
- 依赖管理配置
- 构建缓存优化
- 并行构建策略
- 构建产物管理

### 测试自动化
- 单元测试执行
- 集成测试配置
- 端到端测试
- 性能测试集成
- 测试报告生成

### 部署管理
- 环境配置管理
- 自动化部署
- 回滚策略
- 蓝绿部署
- 金丝雀发布

### 监控告警
- 构建状态监控
- 部署状态跟踪
- 性能指标收集
- 错误告警机制
- 流水线可视化

## 常见CI/CD问题

### 构建性能问题
```
问题:
构建缓慢，资源浪费

错误示例:
- 缺少构建缓存
- 依赖重复下载
- 串行构建流程
- 资源配置不足

解决方案:
1. 配置构建缓存机制
2. 优化依赖管理策略
3. 实施并行构建
4. 合理分配构建资源
```

### 部署失败问题
```
问题:
部署不稳定，回滚频繁

错误示例:
- 环境配置错误
- 部署脚本问题
- 健康检查缺失
- 回滚策略不当

解决方案:
1. 标准化环境配置
2. 完善部署脚本
3. 添加健康检查
4. 实施自动回滚
```

### 质量控制问题
```
问题:
代码质量差，缺陷频发

错误示例:
- 测试覆盖不足
- 代码检查缺失
- 安全扫描遗漏
- 质量门禁缺失

解决方案:
1. 提升测试覆盖率
2. 集成代码检查工具
3. 添加安全扫描
4. 设置质量门禁
```

## 代码实现示例

### CI/CD流水线分析器
```python
import yaml
import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class PipelineStage:
    """流水线阶段信息"""
    name: str
    type: str  # build, test, deploy, etc.
    commands: List[str]
    dependencies: List[str]
    issues: List[str]

@dataclass
class PipelineIssue:
    """流水线问题"""
    severity: str  # critical, high, medium, low
    type: str
    file: str
    message: str
    suggestion: str
    line: Optional[int] = None

class CICDAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.stages: List[PipelineStage] = []
        self.issues: List[PipelineIssue] = []
        
    def analyze_pipeline(self) -> Dict[str, Any]:
        """分析CI/CD流水线"""
        try:
            # 扫描CI/CD配置文件
            self.scan_ci_files()
            
            # 分析构建配置
            self.analyze_build_config()
            
            # 分析测试配置
            self.analyze_test_config()
            
            # 分析部署配置
            self.analyze_deploy_config()
            
            # 分析安全配置
            self.analyze_security_config()
            
            # 生成分析报告
            return self.generate_report()
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def scan_ci_files(self) -> None:
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
            self.issues.append(PipelineIssue(
                severity='high',
                type='configuration',
                file='CI/CD',
                message='未找到CI/CD配置文件',
                suggestion='创建CI/CD配置文件实现自动化构建'
            ))
        else:
            for ci_file in ci_files:
                self.analyze_ci_file(ci_file)
    
    def analyze_ci_file(self, ci_file: Path) -> None:
        """分析CI配置文件"""
        try:
            with open(ci_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if ci_file.suffix in ['.yml', '.yaml']:
                self.analyze_yaml_ci(content, str(ci_file))
            elif ci_file.name == 'Jenkinsfile':
                self.analyze_jenkins_file(content, str(ci_file))
        
        except Exception as e:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='analysis',
                file=str(ci_file),
                message=f'CI文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def analyze_yaml_ci(self, content: str, file_path: str) -> None:
        """分析YAML格式的CI配置"""
        try:
            yaml_data = yaml.safe_load(content)
            
            # 检查是否有触发器配置
            if 'on' not in yaml_data and 'triggers' not in yaml_data:
                self.issues.append(PipelineIssue(
                    severity='medium',
                    type='trigger',
                    file=file_path,
                    message='缺少触发器配置',
                    suggestion='配置push、pull_request等触发器'
                ))
            
            # 分析作业配置
            if 'jobs' in yaml_data:
                self.analyze_jobs(yaml_data['jobs'], file_path)
            
            # 检查环境变量
            self.check_environment_variables(yaml_data, file_path)
            
            # 检查缓存配置
            self.check_cache_configuration(yaml_data, file_path)
        
        except yaml.YAMLError as e:
            self.issues.append(PipelineIssue(
                severity='high',
                type='syntax',
                file=file_path,
                message=f'YAML语法错误: {e}',
                suggestion='修复YAML语法错误'
            ))
    
    def analyze_jenkins_file(self, content: str, file_path: str) -> None:
        """分析Jenkinsfile"""
        # 检查是否有pipeline定义
        if 'pipeline' not in content:
            self.issues.append(PipelineIssue(
                severity='high',
                type='structure',
                file=file_path,
                message='缺少pipeline定义',
                suggestion='定义Jenkins pipeline结构'
            ))
        
        # 检查stage配置
        stages = re.findall(r'sage\s*\([\'"]([^\'"]+)[\'"]\)', content)
        if len(stages) == 0:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='stage',
                file=file_path,
                message='未定义构建阶段',
                suggestion='添加build、test、deploy等阶段'
            ))
        
        # 检查post操作
        if 'post' not in content:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='post',
                file=file_path,
                message='缺少post操作',
                suggestion='添加always、success、failure等post操作'
            ))
    
    def analyze_jobs(self, jobs: Dict[str, Any], file_path: str) -> None:
        """分析作业配置"""
        for job_name, job_config in jobs.items():
            # 检查作业是否运行在runner上
            if 'runs-on' not in job_config:
                self.issues.append(PipelineIssue(
                    severity='medium',
                    type='runner',
                    file=file_path,
                    message=f'作业{job_name}缺少runner配置',
                    suggestion='指定运行环境(ubuntu-latest, windows-latest等)'
                ))
            
            # 检查作业步骤
            if 'steps' not in job_config:
                self.issues.append(PipelineIssue(
                    severity='high',
                    type='steps',
                    file=file_path,
                    message=f'作业{job_name}缺少执行步骤',
                    suggestion='添加checkout、build、test等步骤'
                ))
            else:
                self.analyze_job_steps(job_config['steps'], job_name, file_path)
    
    def analyze_job_steps(self, steps: List[Dict[str, Any]], job_name: str, file_path: str) -> None:
        """分析作业步骤"""
        has_checkout = False
        has_build = False
        has_test = False
        
        for step in steps:
            if 'uses' in step:
                # GitHub Actions
                if 'actions/checkout' in step['uses']:
                    has_checkout = True
                elif 'build' in step['uses'].lower():
                    has_build = True
                elif 'test' in step['uses'].lower():
                    has_test = True
            elif 'run' in step:
                # 自定义命令
                command = step['run']
                if 'checkout' in command.lower():
                    has_checkout = True
                elif 'build' in command.lower() or 'compile' in command.lower():
                    has_build = True
                elif 'test' in command.lower():
                    has_test = True
        
        # 检查必要步骤
        if not has_checkout:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='checkout',
                file=file_path,
                message=f'作业{job_name}缺少代码检出步骤',
                suggestion='添加actions/checkout或git clone步骤'
            ))
        
        if not has_build and 'build' in job_name.lower():
            self.issues.append(PipelineIssue(
                severity='medium',
                type='build',
                file=file_path,
                message=f'构建作业{job_name}缺少构建步骤',
                suggestion='添加编译或构建命令'
            ))
        
        if not has_test and 'test' in job_name.lower():
            self.issues.append(PipelineIssue(
                severity='medium',
                type='test',
                file=file_path,
                message=f'测试作业{job_name}缺少测试步骤',
                suggestion='添加单元测试或集成测试命令'
            ))
    
    def check_environment_variables(self, yaml_data: Dict[str, Any], file_path: str) -> None:
        """检查环境变量配置"""
        # 检查是否使用secrets
        if 'env' not in yaml_data:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='environment',
                file=file_path,
                message='缺少环境变量配置',
                suggestion='配置必要的环境变量'
            ))
        
        # 检查敏感信息泄露
        content = str(yaml_data)
        sensitive_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues.append(PipelineIssue(
                    severity='critical',
                    type='security',
                    file=file_path,
                    message='可能存在敏感信息泄露',
                    suggestion='使用secrets或环境变量管理敏感信息'
                ))
    
    def check_cache_configuration(self, yaml_data: Dict[str, Any], file_path: str) -> None:
        """检查缓存配置"""
        content = str(yaml_data)
        
        if 'cache' not in content:
            self.issues.append(PipelineIssue(
                severity='low',
                type='cache',
                file=file_path,
                message='缺少缓存配置',
                suggestion='配置依赖缓存提升构建速度'
            ))
    
    def analyze_build_config(self) -> None:
        """分析构建配置"""
        # 检查构建工具配置
        build_files = [
            'pom.xml',  # Maven
            'build.gradle',  # Gradle
            'package.json',  # npm/yarn
            'requirements.txt',  # pip
            'Cargo.toml',  # Rust
            'go.mod'  # Go
        ]
        
        build_file_found = False
        for build_file in build_files:
            if (self.repo_path / build_file).exists():
                build_file_found = True
                self.analyze_build_file(self.repo_path / build_file)
                break
        
        if not build_file_found:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='build',
                file='build',
                message='未找到构建配置文件',
                suggestion '添加构建配置文件'
            ))
    
    def analyze_build_file(self, build_file: Path) -> None:
        """分析构建文件"""
        try:
            with open(build_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if build_file.name == 'package.json':
                self.analyze_package_json(content, str(build_file))
            elif build_file.name == 'pom.xml':
                self.analyze_pom_xml(content, str(build_file))
            elif build_file.name == 'build.gradle':
                self.analyze_build_gradle(content, str(build_file))
        
        except Exception as e:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='analysis',
                file=str(build_file),
                message=f'构建文件分析失败: {e}',
                suggestion='检查文件格式和编码'
            ))
    
    def analyze_package_json(self, content: str, file_path: str) -> None:
        """分析package.json"""
        try:
            package_data = json.loads(content)
            
            # 检查scripts
            if 'scripts' not in package_data:
                self.issues.append(PipelineIssue(
                    severity='medium',
                    type='scripts',
                    file=file_path,
                    message='缺少构建脚本',
                    suggestion='添加build、test等npm脚本'
                ))
            else:
                scripts = package_data['scripts']
                if 'build' not in scripts:
                    self.issues.append(PipelineIssue(
                        severity='medium',
                        type='scripts',
                        file=file_path,
                        message='缺少build脚本',
                        suggestion='添加npm run build命令'
                    ))
                
                if 'test' not in scripts:
                    self.issues.append(PipelineIssue(
                        severity='medium',
                        type='scripts',
                        file=file_path,
                        message='缺少test脚本',
                        suggestion='添加npm test命令'
                    ))
        
        except json.JSONDecodeError as e:
            self.issues.append(PipelineIssue(
                severity='high',
                type='syntax',
                file=file_path,
                message=f'JSON语法错误: {e}',
                suggestion='修复JSON语法错误'
            ))
    
    def analyze_pom_xml(self, content: str, file_path: str) -> None:
        """分析pom.xml"""
        # 检查是否有测试插件
        if 'maven-surefire-plugin' not in content:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='plugin',
                file=file_path,
                message='缺少测试插件配置',
                suggestion='添加maven-surefire-plugin执行测试'
            ))
        
        # 检查是否有构建插件
        if 'maven-compiler-plugin' not in content:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='plugin',
                file=file_path,
                message='缺少编译插件配置',
                suggestion='添加maven-compiler-plugin配置编译'
            ))
    
    def analyze_build_gradle(self, content: str, file_path: str) -> None:
        """分析build.gradle"""
        # 检查是否有测试任务
        if 'test' not in content:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='task',
                file=file_path,
                message='缺少测试任务',
                suggestion='添加test任务执行单元测试'
            ))
        
        # 检查是否有构建任务
        if 'build' not in content:
            self.issues.append(PipelineIssue(
                severity='medium',
                type='task',
                file=file_path,
                message='缺少构建任务',
                suggestion='添加build任务编译项目'
            ))
    
    def analyze_test_config(self) -> None:
        """分析测试配置"""
        # 检查测试配置文件
        test_configs = [
            'jest.config.js',  # Jest
            'pytest.ini',  # pytest
            'karma.conf.js',  # Karma
            'testng.xml'  # TestNG
        ]
        
        test_config_found = False
        for test_config in test_configs:
            if (self.repo_path / test_config).exists():
                test_config_found = True
                break
        
        if not test_config_found:
            self.issues.append(PipelineIssue(
                severity='low',
                type='test',
                file='test',
                message='未找到测试配置文件',
                suggestion='添加测试配置文件'
            ))
    
    def analyze_deploy_config(self) -> None:
        """分析部署配置"""
        # 检查部署配置文件
        deploy_configs = [
            'docker-compose.yml',
            'Dockerfile',
            'k8s',
            'helm',
            'terraform'
        ]
        
        deploy_config_found = False
        for deploy_config in deploy_configs:
            if (self.repo_path / deploy_config).exists():
                deploy_config_found = True
                break
        
        if not deploy_config_found:
            self.issues.append(PipelineIssue(
                severity='low',
                type='deploy',
                file='deploy',
                message='未找到部署配置文件',
                suggestion='添加部署配置文件'
            ))
    
    def analyze_security_config(self) -> None:
        """分析安全配置"""
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
            self.issues.append(PipelineIssue(
                severity='medium',
                type='security',
                file='security',
                message='未找到安全配置文件',
                suggestion='添加安全扫描配置'
            ))
    
    def generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        summary = {
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'high_issues': len([i for i in self.issues if i.severity == 'high']),
            'medium_issues': len([i for i in self.issues if i.severity == 'medium']),
            'low_issues': len([i for i in self.issues if i.severity == 'low']),
            'total_stages': len(self.stages)
        }
        
        recommendations = self.generate_recommendations()
        
        return {
            'summary': summary,
            'stages': [self.stage_to_dict(stage) for stage in self.stages],
            'issues': [self.issue_to_dict(issue) for issue in self.issues],
            'recommendations': recommendations,
            'health_score': self.calculate_health_score(summary)
        }
    
    def stage_to_dict(self, stage: PipelineStage) -> Dict[str, Any]:
        """将阶段转换为字典"""
        return {
            'name': stage.name,
            'type': stage.type,
            'commands': stage.commands,
            'dependencies': stage.dependencies,
            'issues': stage.issues
        }
    
    def issue_to_dict(self, issue: PipelineIssue) -> Dict[str, Any]:
        """将问题转换为字典"""
        return {
            'severity': issue.severity,
            'type': issue.type,
            'file': issue.file,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'line': issue.line
        }
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
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
                suggestion: '加强CI/CD安全配置'
            })
        
        if issue_types.get('build', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'build',
                'message': f'发现{issue_types["build"]}个构建问题',
                suggestion: '优化构建配置和流程'
            })
        
        if issue_types.get('test', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'test',
                'message': f'发现{issue_types["test"]}个测试问题',
                suggestion: '完善测试配置和覆盖率'
            })
        
        return recommendations
    
    def calculate_health_score(self, summary: Dict[str, int]) -> int:
        """计算健康评分"""
        score = 100
        
        score -= summary['critical_issues'] * 20
        score -= summary['high_issues'] * 10
        score -= summary['medium_issues'] * 5
        score -= summary['low_issues'] * 2
        
        return max(0, score)

# CI/CD流水线优化器
class CICDOptimizer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
    
    def optimize_pipeline(self) -> Dict[str, Any]:
        """优化CI/CD流水线"""
        optimizations = []
        
        # 检查并优化构建配置
        build_optimization = self.optimize_build_configuration()
        if build_optimization:
            optimizations.append(build_optimization)
        
        # 检查并优化测试配置
        test_optimization = self.optimize_test_configuration()
        if test_optimization:
            optimizations.append(test_optimization)
        
        # 检查并优化部署配置
        deploy_optimization = self.optimize_deploy_configuration()
        if deploy_optimization:
            optimizations.append(deploy_optimization)
        
        return {
            'optimizations': optimizations,
            'summary': {
                'total_optimizations': len(optimizations),
                'estimated_improvements': self.estimate_improvements(optimizations)
            }
        }
    
    def optimize_build_configuration(self) -> Optional[Dict[str, str]]:
        """优化构建配置"""
        # 检查是否有构建缓存
        github_workflows = self.repo_path / '.github' / 'workflows'
        if github_workflows.exists():
            for workflow_file in github_workflows.glob('*.yml'):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'cache' not in content:
                        return {
                            'type': 'build',
                            'message': '添加构建缓存',
                            'suggestion': '配置依赖缓存减少构建时间'
                        }
                except Exception:
                    pass
        
        return None
    
    def optimize_test_configuration(self) -> Optional[Dict[str, str]]:
        """优化测试配置"""
        # 检查是否有并行测试
        github_workflows = self.repo_path / '.github' / 'workflows'
        if github_workflows.exists():
            for workflow_file in github_workflows.glob('*.yml'):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'matrix' not in content:
                        return {
                            'type': 'test',
                            'message': '添加并行测试',
                            'suggestion': '使用matrix策略并行执行测试'
                        }
                except Exception:
                    pass
        
        return None
    
    def optimize_deploy_configuration(self) -> Optional[Dict[str, str]]:
        """优化部署配置"""
        # 检查是否有环境管理
        github_workflows = self.repo_path / '.github' / 'workflows'
        if github_workflows.exists():
            for workflow_file in github_workflows.glob('*.yml'):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'environment' not in content:
                        return {
                            'type': 'deploy',
                            'message': '添加环境管理',
                            'suggestion': '配置部署环境提升安全性'
                        }
                except Exception:
                    pass
        
        return None
    
    def estimate_improvements(self, optimizations: List[Dict[str, str]]) -> Dict[str, int]:
        """估算改进效果"""
        improvements = {
            'speed': 0,
            'reliability': 0,
            'security': 0
        }
        
        for opt in optimizations:
            if opt['type'] == 'build':
                improvements['speed'] += 30
            elif opt['type'] == 'test':
                improvements['speed'] += 20
            elif opt['type'] == 'deploy':
                improvements['security'] += 25
                improvements['reliability'] += 15
        
        return improvements

# 使用示例
def main():
    # 分析CI/CD流水线
    analyzer = CICDAnalyzer('./my-project')
    report = analyzer.analyze_pipeline()
    
    print("CI/CD流水线分析报告:")
    print(f"健康评分: {report['health_score']}")
    print(f"问题总数: {report['summary']['total_issues']}")
    print(f"阶段总数: {report['summary']['total_stages']}")
    
    print("\n优化建议:")
    for rec in report['recommendations']:
        print(f"- {rec['message']}: {rec['suggestion']}")
    
    # 优化流水线
    optimizer = CICDOptimizer('./my-project')
    optimization = optimizer.optimize_pipeline()
    
    print("\n优化建议:")
    for opt in optimization['optimizations']:
        print(f"- {opt['message']}: {opt['suggestion']}")

if __name__ == '__main__':
    main()
```

### CI/CD性能监控器
```python
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

@dataclass
class BuildMetrics:
    """构建指标"""
    build_id: str
    status: str
    duration: float
    start_time: datetime
    end_time: Optional[datetime]
    trigger: str
    branch: str

@dataclass
class PipelineMetrics:
    """流水线指标"""
    pipeline_id: str
    name: str
    status: str
    duration: float
    stages: List[str]
    artifacts: List[str]

class CICDPerformanceMonitor:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token
        self.builds: List[BuildMetrics] = []
        self.pipelines: List[PipelineMetrics] = []
    
    def collect_github_actions_metrics(self, owner: str, repo: str) -> Dict[str, Any]:
        """收集GitHub Actions指标"""
        headers = {
            'Authorization': f'token {self.api_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            # 获取工作流运行
            workflow_runs_url = f'{self.api_url}/repos/{owner}/{repo}/actions/runs'
            response = requests.get(workflow_runs_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            workflow_runs = data.get('workflow_runs', [])
            
            # 分析最近的工作流运行
            recent_runs = workflow_runs[:10]  # 最近10次运行
            
            metrics = {
                'total_runs': len(workflow_runs),
                'success_rate': self.calculate_success_rate(recent_runs),
                'average_duration': self.calculate_average_duration(recent_runs),
                'slowest_runs': self.get_slowest_runs(recent_runs, 5),
                'workflow_summary': self.summarize_workflows(recent_runs)
            }
            
            return metrics
        
        except Exception as e:
            return {'error': f'GitHub Actions指标收集失败: {e}'}
    
    def calculate_success_rate(self, runs: List[Dict[str, Any]]) -> float:
        """计算成功率"""
        if not runs:
            return 0.0
        
        successful_runs = len([run for run in runs if run['conclusion'] == 'success'])
        return (successful_runs / len(runs)) * 100
    
    def calculate_average_duration(self, runs: List[Dict[str, Any]]) -> float:
        """计算平均持续时间"""
        if not runs:
            return 0.0
        
        durations = []
        for run in runs:
            if run['status'] == 'completed':
                start_time = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds()
                durations.append(duration)
        
        return sum(durations) / len(durations) if durations else 0.0
    
    def get_slowest_runs(self, runs: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """获取最慢的运行"""
        completed_runs = [run for run in runs if run['status'] == 'completed']
        
        for run in completed_runs:
            start_time = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
            run['duration'] = (end_time - start_time).total_seconds()
        
        sorted_runs = sorted(completed_runs, key=lambda x: x['duration'], reverse=True)
        return sorted_runs[:limit]
    
    def summarize_workflows(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """汇总工作流信息"""
        workflow_summary = {}
        
        for run in runs:
            workflow_name = run.get('name', 'Unknown')
            if workflow_name not in workflow_summary:
                workflow_summary[workflow_name] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'failed_runs': 0,
                    'average_duration': 0.0
                }
            
            summary = workflow_summary[workflow_name]
            summary['total_runs'] += 1
            
            if run['conclusion'] == 'success':
                summary['successful_runs'] += 1
            elif run['conclusion'] == 'failure':
                summary['failed_runs'] += 1
        
        # 计算平均持续时间
        for workflow_name, summary in workflow_summary.items():
            workflow_runs = [run for run in runs if run.get('name') == workflow_name]
            summary['average_duration'] = self.calculate_average_duration(workflow_runs)
        
        return workflow_summary
    
    def collect_gitlab_ci_metrics(self, project_id: int) -> Dict[str, Any]:
        """收集GitLab CI指标"""
        headers = {
            'Private-Token': self.api_token
        }
        
        try:
            # 获取流水线
            pipelines_url = f'{self.api_url}/projects/{project_id}/pipelines'
            response = requests.get(pipelines_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            pipelines = data[:10]  # 最近10个流水线
            
            metrics = {
                'total_pipelines': len(data),
                'success_rate': self.calculate_pipeline_success_rate(pipelines),
                'average_duration': self.calculate_pipeline_average_duration(pipelines),
                'pipeline_summary': self.summarize_pipelines(pipelines)
            }
            
            return metrics
        
        except Exception as e:
            return {'error': f'GitLab CI指标收集失败: {e}'}
    
    def calculate_pipeline_success_rate(self, pipelines: List[Dict[str, Any]]) -> float:
        """计算流水线成功率"""
        if not pipelines:
            return 0.0
        
        successful_pipelines = len([p for p in pipelines if p['status'] == 'success'])
        return (successful_pipelines / len(pipelines)) * 100
    
    def calculate_pipeline_average_duration(self, pipelines: List[Dict[str, Any]]) -> float:
        """计算流水线平均持续时间"""
        if not pipelines:
            return 0.0
        
        durations = []
        for pipeline in pipelines:
            if pipeline.get('duration'):
                durations.append(pipeline['duration'])
        
        return sum(durations) / len(durations) if durations else 0.0
    
    def summarize_pipelines(self, pipelines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """汇总流水线信息"""
        status_summary = {}
        
        for pipeline in pipelines:
            status = pipeline['status']
            if status not in status_summary:
                status_summary[status] = 0
            status_summary[status] += 1
        
        return status_summary
    
    def generate_performance_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成性能报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'recommendations': self.generate_performance_recommendations(metrics),
            'trends': self.analyze_trends()
        }
        
        return report
    
    def generate_performance_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """生成性能建议"""
        recommendations = []
        
        # 基于成功率提供建议
        if 'success_rate' in metrics:
            success_rate = metrics['success_rate']
            if success_rate < 80:
                recommendations.append("成功率较低，建议检查构建失败原因并修复")
            elif success_rate < 95:
                recommendations.append("成功率有待提升，建议加强测试和质量检查")
        
        # 基于持续时间提供建议
        if 'average_duration' in metrics:
            avg_duration = metrics['average_duration']
            if avg_duration > 600:  # 10分钟
                recommendations.append("构建时间较长，建议优化构建缓存和并行执行")
            elif avg_duration > 300:  # 5分钟
                recommendations.append("构建时间偏长，考虑优化依赖管理和构建步骤")
        
        return recommendations
    
    def analyze_trends(self) -> Dict[str, Any]:
        """分析趋势"""
        # 这里可以实现趋势分析逻辑
        # 比较不同时间段的性能指标
        return {
            'build_trend': 'stable',
            'success_trend': 'improving',
            'duration_trend': 'stable'
        }

# CI/CD告警系统
class CICDAlertSystem:
    def __init__(self, monitor: CICDPerformanceMonitor):
        self.monitor = monitor
        self.alert_thresholds = {
            'success_rate_min': 90.0,
            'build_duration_max': 300.0,  # 5分钟
            'failure_count_max': 3
        }
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        
        # 检查成功率告警
        if 'success_rate' in metrics:
            success_rate = metrics['success_rate']
            if success_rate < self.alert_thresholds['success_rate_min']:
                alerts.append({
                    'type': 'success_rate',
                    'severity': 'high',
                    'message': f'成功率过低: {success_rate:.1f}%',
                    'threshold': self.alert_thresholds['success_rate_min']
                })
        
        # 检查构建时间告警
        if 'average_duration' in metrics:
            avg_duration = metrics['average_duration']
            if avg_duration > self.alert_thresholds['build_duration_max']:
                alerts.append({
                    'type': 'build_duration',
                    'severity': 'medium',
                    'message': f'构建时间过长: {avg_duration:.1f}秒',
                    'threshold': self.alert_thresholds['build_duration_max']
                })
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]) -> bool:
        """发送告警"""
        try:
            # 这里可以实现告警发送逻辑
            # 比如发送邮件、Slack、钉钉等
            print(f"告警: {alert['message']}")
            return True
        except Exception as e:
            print(f"告警发送失败: {e}")
            return False

# 使用示例
def main():
    # GitHub Actions监控
    monitor = CICDPerformanceMonitor(
        api_url='https://api.github.com',
        api_token='your-github-token'
    )
    
    metrics = monitor.collect_github_actions_metrics('owner', 'repo')
    
    # 生成性能报告
    report = monitor.generate_performance_report(metrics)
    print("CI/CD性能报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # 告警检查
    alert_system = CICDAlertSystem(monitor)
    alerts = alert_system.check_alerts(metrics)
    
    if alerts:
        print("\n告警信息:")
        for alert in alerts:
            print(f"- {alert['message']}")
            alert_system.send_alert(alert)

if __name__ == '__main__':
    main()
```

## CI/CD流水线最佳实践

### 构建优化
1. **缓存策略**: 配置依赖缓存和构建缓存
2. **并行执行**: 使用矩阵策略并行构建
3. **增量构建**: 只构建变更的部分
4. **资源管理**: 合理配置构建资源
5. **构建优化**: 优化构建工具配置

### 测试自动化
1. **测试分层**: 单元测试、集成测试、端到端测试
2. **并行测试**: 并行执行测试用例
3. **测试报告**: 生成详细的测试报告
4. **覆盖率监控**: 监控代码覆盖率
5. **质量门禁**: 设置质量检查门禁

### 部署策略
1. **环境管理**: 标准化环境配置
2. **蓝绿部署**: 实现零停机部署
3. **金丝雀发布**: 渐进式发布策略
4. **自动回滚**: 失败时自动回滚
5. **健康检查**: 完善的健康检查机制

### 安全实践
1. **密钥管理**: 使用密钥管理服务
2. **安全扫描**: 代码安全扫描
3. **依赖检查**: 检查依赖漏洞
4. **访问控制**: 严格的访问控制
5. **审计日志**: 完整的操作日志

## 相关技能

- **infrastructure-as-code** - 基础设施即代码
- **monitoring-alerting** - 监控告警
- **log-aggregation** - 日志聚合
- **security-best-practices** - 安全最佳实践
