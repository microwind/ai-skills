---
name: 依赖分析器
description: "当分析依赖时，检查漏洞，查找未使用的包，管理版本。分析和优化依赖。"
license: MIT
---

# 依赖分析器技能

## 概述

依赖是项目的风险来源。漏洞、过时版本和未使用的包会逐渐累积。在部署前必须进行分析。

**核心原则**: 了解你的依赖。好的依赖管理应该安全、精简、及时更新、版本可控。坏的依赖管理会导致安全风险、技术债务、维护困难。

## 何时使用

**始终:**
- 生产部署前
- 检查安全更新时
- 查找未使用包时
- 检测冲突时
- 管理技术债务时

**触发短语:**
- "检查漏洞"
- "查找未使用依赖"
- "更新依赖"
- "检测冲突"
- "检查过时包"

## 依赖分析器技能功能

### 安全性检查
- 漏洞扫描
- 安全建议
- 风险评估
- 补丁建议
- 许可证检查
- 供应链安全

### 依赖优化
- 未使用包检测
- 版本更新建议
- 冲突解决
- 依赖树分析
- 包大小优化
- 替代方案建议

### 版本管理
- 版本兼容性检查
- 语义化版本分析
- 更新策略制定
- 锁定文件验证
- 发布周期管理
- 回滚计划

### 质量评估
- 包质量评分
- 维护状态检查
- 社区活跃度
- 文档完整性
- 测试覆盖率
- 性能影响

## 常见问题

**❌ 安全漏洞**
- 使用已知漏洞的包
- 未及时更新安全补丁
- 恶意依赖注入
- 许可证合规问题

**❌ 依赖冗余**
- 未使用的包堆积
- 重复功能依赖
- 过度依赖
- 传递依赖过多

**❌ 版本冲突**
- 版本不兼容
- 依赖树冲突
- 锁定文件不一致
- 更新困难

**❌ 维护困难**
- 依赖版本过时
- 维护者不活跃
- 文档缺失
- 社区支持不足

## 代码示例

### 依赖分析器

```python
#!/usr/bin/env python3
import json
import re
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import semver
import toml
import yaml

class VulnerabilityLevel(Enum):
    """漏洞等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PackageManager(Enum):
    """包管理器类型"""
    NPM = "npm"
    PIP = "pip"
    MAVEN = "maven"
    GRADLE = "gradle"
    YARN = "yarn"

@dataclass
class Dependency:
    """依赖信息"""
    name: str
    version: str
    dev: bool = False
    optional: bool = False
    direct: bool = True
    licenses: List[str] = None
    size: int = 0
    last_updated: str = ""

@dataclass
class Vulnerability:
    """漏洞信息"""
    package: str
    severity: VulnerabilityLevel
    title: str
    description: str
    patched_versions: List[str]
    cve_id: Optional[str] = None
    references: List[str] = None

@dataclass
class DependencyIssue:
    """依赖问题"""
    type: str
    severity: str
    package: str
    description: str
    suggestion: str
    details: Dict = None

class DependencyAnalyzer:
    """依赖分析器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.dependencies: Dict[str, Dependency] = {}
        self.vulnerabilities: List[Vulnerability] = []
        self.issues: List[DependencyIssue] = []
        self.package_manager = self._detect_package_manager()
    
    def _detect_package_manager(self) -> PackageManager:
        """检测包管理器类型"""
        if (self.project_path / "package.json").exists():
            if (self.project_path / "yarn.lock").exists():
                return PackageManager.YARN
            return PackageManager.NPM
        elif (self.project_path / "requirements.txt").exists() or (self.project_path / "pyproject.toml").exists():
            return PackageManager.PIP
        elif (self.project_path / "pom.xml").exists():
            return PackageManager.MAVEN
        elif (self.project_path / "build.gradle").exists():
            return PackageManager.GRADLE
        else:
            return PackageManager.NPM  # 默认
    
    def parse_dependencies(self) -> Dict[str, Dependency]:
        """解析依赖文件"""
        if self.package_manager == PackageManager.NPM:
            return self._parse_npm_dependencies()
        elif self.package_manager == PackageManager.PIP:
            return self._parse_pip_dependencies()
        elif self.package_manager == PackageManager.MAVEN:
            return self._parse_maven_dependencies()
        elif self.package_manager == PackageManager.GRADLE:
            return self._parse_gradle_dependencies()
        else:
            return {}
    
    def _parse_npm_dependencies(self) -> Dict[str, Dependency]:
        """解析npm依赖"""
        package_json_path = self.project_path / "package.json"
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = {}
            
            # 解析生产依赖
            for name, version in package_data.get('dependencies', {}).items():
                dependencies[name] = Dependency(
                    name=name,
                    version=version,
                    dev=False,
                    direct=True
                )
            
            # 解析开发依赖
            for name, version in package_data.get('devDependencies', {}).items():
                dependencies[name] = Dependency(
                    name=name,
                    version=version,
                    dev=True,
                    direct=True
                )
            
            # 解析可选依赖
            for name, version in package_data.get('optionalDependencies', {}).items():
                if name in dependencies:
                    dependencies[name].optional = True
                else:
                    dependencies[name] = Dependency(
                        name=name,
                        version=version,
                        dev=False,
                        optional=True,
                        direct=True
                    )
            
            return dependencies
        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"解析package.json失败: {e}")
            return {}
    
    def _parse_pip_dependencies(self) -> Dict[str, Dependency]:
        """解析pip依赖"""
        dependencies = {}
        
        # 解析requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 解析包名和版本
                            match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!]+.*)?$', line)
                            if match:
                                name = match.group(1)
                                version = match.group(2) or "*"
                                dependencies[name] = Dependency(
                                    name=name,
                                    version=version,
                                    dev=False,
                                    direct=True
                                )
            except Exception as e:
                print(f"解析requirements.txt失败: {e}")
        
        # 解析pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r', encoding='utf-8') as f:
                    pyproject_data = toml.load(f)
                
                # 解析项目依赖
                deps = pyproject_data.get('project', {}).get('dependencies', [])
                for dep in deps:
                    match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!]+.*)?$', dep)
                    if match:
                        name = match.group(1)
                        version = match.group(2) or "*"
                        dependencies[name] = Dependency(
                            name=name,
                            version=version,
                            dev=False,
                            direct=True
                        )
                
                # 解析可选依赖
                optional_deps = pyproject_data.get('project', {}).get('optional-dependencies', {})
                for group, deps in optional_deps.items():
                    for dep in deps:
                        match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!]+.*)?$', dep)
                        if match:
                            name = match.group(1)
                            version = match.group(2) or "*"
                            if name in dependencies:
                                dependencies[name].optional = True
                            else:
                                dependencies[name] = Dependency(
                                    name=name,
                                    version=version,
                                    dev=False,
                                    optional=True,
                                    direct=True
                                )
            except Exception as e:
                print(f"解析pyproject.toml失败: {e}")
        
        return dependencies
    
    def _parse_maven_dependencies(self) -> Dict[str, Dependency]:
        """解析Maven依赖"""
        pom_file = self.project_path / "pom.xml"
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(pom_file)
            root = tree.getroot()
            
            dependencies = {}
            
            # 处理命名空间
            namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
            
            for dep in root.findall('.//maven:dependency', namespace):
                group_id = dep.find('maven:groupId', namespace)
                artifact_id = dep.find('maven:artifactId', namespace)
                version = dep.find('maven:version', namespace)
                scope = dep.find('maven:scope', namespace)
                
                if group_id is not None and artifact_id is not None:
                    name = f"{group_id.text}:{artifact_id.text}"
                    version_str = version.text if version is not None else "*"
                    is_dev = scope is not None and scope.text == 'test'
                    
                    dependencies[name] = Dependency(
                        name=name,
                        version=version_str,
                        dev=is_dev,
                        direct=True
                    )
            
            return dependencies
        
        except Exception as e:
            print(f"解析pom.xml失败: {e}")
            return {}
    
    def _parse_gradle_dependencies(self) -> Dict[str, Dependency]:
        """解析Gradle依赖"""
        build_file = self.project_path / "build.gradle"
        
        try:
            with open(build_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = {}
            
            # 解析依赖声明
            # 简单的正则匹配，实际项目中可能需要更复杂的解析
            patterns = [
                r'implementation\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]',
                r'api\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]',
                r'testImplementation\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]',
                r'compile\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]',
                r'testCompile\s+[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    group_id, artifact_id, version = match.groups()
                    name = f"{group_id}:{artifact_id}"
                    is_dev = 'test' in pattern
                    
                    dependencies[name] = Dependency(
                        name=name,
                        version=version,
                        dev=is_dev,
                        direct=True
                    )
            
            return dependencies
        
        except Exception as e:
            print(f"解析build.gradle失败: {e}")
            return {}
    
    def check_vulnerabilities(self) -> List[Vulnerability]:
        """检查安全漏洞"""
        vulnerabilities = []
        
        for dep_name, dependency in self.dependencies.items():
            # 这里应该调用实际的漏洞数据库API
            # 例如: npm audit, pip audit, OWASP Dependency-Check等
            # 这里是模拟实现
            mock_vulns = self._get_mock_vulnerabilities(dep_name, dependency.version)
            vulnerabilities.extend(mock_vulns)
        
        self.vulnerabilities = vulnerabilities
        return vulnerabilities
    
    def _get_mock_vulnerabilities(self, package: str, version: str) -> List[Vulnerability]:
        """获取模拟漏洞数据"""
        # 实际实现中应该调用真实的漏洞数据库
        mock_vulns = []
        
        # 模拟一些常见漏洞
        if package.lower() in ['lodash', 'request', 'moment']:
            mock_vulns.append(Vulnerability(
                package=package,
                severity=VulnerabilityLevel.HIGH,
                title="原型污染漏洞",
                description="包中存在原型污染漏洞，可能导致安全风险",
                patched_versions=[">=4.17.21"],
                cve_id="CVE-2021-23337"
            ))
        
        if package.lower() in ['axios', 'express']:
            mock_vulns.append(Vulnerability(
                package=package,
                severity=VulnerabilityLevel.MEDIUM,
                title="SSRF漏洞",
                description="服务器端请求伪造漏洞",
                patched_versions=[">=0.21.1"],
                cve_id="CVE-2021-3749"
            ))
        
        return mock_vulns
    
    def find_unused_dependencies(self) -> List[str]:
        """查找未使用的依赖"""
        unused = []
        
        if self.package_manager == PackageManager.NPM:
            unused = self._find_unused_npm()
        elif self.package_manager == PackageManager.PIP:
            unused = self._find_unused_pip()
        
        return unused
    
    def _find_unused_npm(self) -> List[str]:
        """查找npm未使用依赖"""
        # 这里应该使用实际的代码分析
        # 例如: depcheck工具
        # 简化实现
        unused = []
        
        for dep_name, dependency in self.dependencies.items():
            if not dependency.dev:
                # 检查代码中是否使用了这个依赖
                if not self._is_npm_dep_used(dep_name):
                    unused.append(dep_name)
        
        return unused
    
    def _is_npm_dep_used(self, dep_name: str) -> bool:
        """检查npm依赖是否被使用"""
        # 简化实现，实际应该扫描代码文件
        source_files = []
        
        # 查找源代码文件
        for pattern in ['**/*.js', '**/*.ts', '**/*.jsx', '**/*.tsx']:
            source_files.extend(self.project_path.glob(pattern))
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查import/require语句
                patterns = [
                    f'import.*from.*[\'"]{dep_name}[\'"]',
                    f'require\([\'"]{dep_name}[\'"]\)',
                    f'import.*[\'"]{dep_name}[\'"]'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        return True
            
            except Exception:
                continue
        
        return False
    
    def _find_unused_pip(self) -> List[str]:
        """查找pip未使用依赖"""
        # 类似npm的实现
        unused = []
        
        for dep_name, dependency in self.dependencies.items():
            if not dependency.dev:
                if not self._is_pip_dep_used(dep_name):
                    unused.append(dep_name)
        
        return unused
    
    def _is_pip_dep_used(self, dep_name: str) -> bool:
        """检查pip依赖是否被使用"""
        source_files = []
        
        # 查找Python源代码文件
        for pattern in ['**/*.py']:
            source_files.extend(self.project_path.glob(pattern))
        
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查import语句
                patterns = [
                    f'import {dep_name}',
                    f'from {dep_name} import',
                    f'import {dep_name.replace("-", "_")}',
                    f'from {dep_name.replace("-", "_")} import'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content):
                        return True
            
            except Exception:
                continue
        
        return False
    
    def check_outdated_dependencies(self) -> Dict[str, Dict]:
        """检查过时依赖"""
        outdated = {}
        
        for dep_name, dependency in self.dependencies.items():
            latest_version = self._get_latest_version(dep_name)
            if latest_version and self._is_outdated(dependency.version, latest_version):
                outdated[dep_name] = {
                    'current': dependency.version,
                    'latest': latest_version,
                    'type': self._get_update_type(dependency.version, latest_version)
                }
        
        return outdated
    
    def _get_latest_version(self, package: str) -> Optional[str]:
        """获取最新版本"""
        # 实际实现应该调用npm registry, PyPI等API
        # 这里是模拟实现
        return "1.2.3"
    
    def _is_outdated(self, current: str, latest: str) -> bool:
        """检查是否过时"""
        try:
            # 简化的版本比较
            current_clean = current.replace('^', '').replace('~', '').replace('>=', '').replace('<=', '')
            latest_clean = latest.replace('^', '').replace('~', '').replace('>=', '').replace('<=', '')
            
            return current_clean != latest_clean
        except:
            return False
    
    def _get_update_type(self, current: str, latest: str) -> str:
        """获取更新类型"""
        try:
            current_clean = current.replace('^', '').replace('~', '').replace('>=', '').replace('<=', '')
            latest_clean = latest.replace('^', '').replace('~', '').replace('>=', '').replace('<=', '')
            
            current_parts = current_clean.split('.')
            latest_parts = latest_clean.split('.')
            
            if len(current_parts) >= 1 and len(latest_parts) >= 1:
                if current_parts[0] != latest_parts[0]:
                    return "major"
                elif len(current_parts) >= 2 and current_parts[1] != latest_parts[1]:
                    return "minor"
                else:
                    return "patch"
            
            return "patch"
        except:
            return "patch"
    
    def analyze_dependency_tree(self) -> Dict:
        """分析依赖树"""
        # 这里应该解析实际的依赖树文件
        # 例如: npm ls, pip show等
        return {
            'total_dependencies': len(self.dependencies),
            'direct_dependencies': len([d for d in self.dependencies.values() if d.direct]),
            'transitive_dependencies': len([d for d in self.dependencies.values() if not d.direct]),
            'dev_dependencies': len([d for d in self.dependencies.values() if d.dev]),
            'optional_dependencies': len([d for d in self.dependencies.values() if d.optional])
        }
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        # 解析依赖
        self.dependencies = self.parse_dependencies()
        
        # 执行各项检查
        vulnerabilities = self.check_vulnerabilities()
        unused_deps = self.find_unused_dependencies()
        outdated_deps = self.check_outdated_dependencies()
        tree_analysis = self.analyze_dependency_tree()
        
        # 统计信息
        total_vulns = len(vulnerabilities)
        critical_vulns = len([v for v in vulnerabilities if v.severity == VulnerabilityLevel.CRITICAL])
        high_vulns = len([v for v in vulnerabilities if v.severity == VulnerabilityLevel.HIGH])
        medium_vulns = len([v for v in vulnerabilities if v.severity == VulnerabilityLevel.MEDIUM])
        low_vulns = len([v for v in vulnerabilities if v.severity == VulnerabilityLevel.LOW])
        
        return {
            'summary': {
                'total_dependencies': len(self.dependencies),
                'total_vulnerabilities': total_vulns,
                'critical_vulnerabilities': critical_vulns,
                'high_vulnerabilities': high_vulns,
                'medium_vulnerabilities': medium_vulns,
                'low_vulnerabilities': low_vulns,
                'unused_dependencies': len(unused_deps),
                'outdated_dependencies': len(outdated_deps)
            },
            'vulnerabilities': [
                {
                    'package': vuln.package,
                    'severity': vuln.severity.value,
                    'title': vuln.title,
                    'description': vuln.description,
                    'patched_versions': vuln.patched_versions,
                    'cve_id': vuln.cve_id
                }
                for vuln in vulnerabilities
            ],
            'unused_dependencies': unused_deps,
            'outdated_dependencies': outdated_deps,
            'dependency_tree': tree_analysis
        }

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='依赖分析器')
    parser.add_argument('path', nargs='?', default='.', help='项目路径')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    parser.add_argument('--check-vulnerabilities', action='store_true', help='检查安全漏洞')
    parser.add_argument('--find-unused', action='store_true', help='查找未使用依赖')
    parser.add_argument('--check-outdated', action='store_true', help='检查过时依赖')
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer(args.path)
    
    try:
        report = analyzer.generate_report()
        
        if args.format == 'json':
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"报告已保存到: {args.output}")
            else:
                print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            print("=" * 50)
            print("依赖分析报告")
            print("=" * 50)
            
            # 摘要
            summary = report['summary']
            print(f"总依赖数: {summary['total_dependencies']}")
            print(f"总漏洞数: {summary['total_vulnerabilities']}")
            print(f"严重漏洞: {summary['critical_vulnerabilities']}")
            print(f"高危漏洞: {summary['high_vulnerabilities']}")
            print(f"中危漏洞: {summary['medium_vulnerabilities']}")
            print(f"低危漏洞: {summary['low_vulnerabilities']}")
            print(f"未使用依赖: {summary['unused_dependencies']}")
            print(f"过时依赖: {summary['outdated_dependencies']}")
            print()
            
            # 漏洞详情
            if report['vulnerabilities']:
                print("🚨 安全漏洞:")
                for vuln in report['vulnerabilities']:
                    print(f"  {vuln['package']} ({vuln['severity']})")
                    print(f"    {vuln['title']}")
                    print(f"    {vuln['description']}")
                    if vuln['patched_versions']:
                        print(f"    修复版本: {', '.join(vuln['patched_versions'])}")
                    print()
            
            # 未使用依赖
            if report['unused_dependencies']:
                print("🗑️ 未使用依赖:")
                for dep in report['unused_dependencies']:
                    print(f"  - {dep}")
                print()
            
            # 过时依赖
            if report['outdated_dependencies']:
                print("⬆️ 过时依赖:")
                for dep, info in report['outdated_dependencies'].items():
                    print(f"  {dep}: {info['current']} -> {info['latest']} ({info['type']})")
                print()
    
    except Exception as e:
        print(f"分析失败: {e}")
        exit(1)
```

### 自动依赖更新工具

```bash
#!/bin/bash
# dependency-updater.sh - 自动依赖更新工具

set -e

# 配置
PROJECT_PATH=${1:-"."}
DRY_RUN=${2:-true}
UPDATE_TYPE=${3:-"patch"}  # patch, minor, major
LOG_FILE="dependency_update.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

# 检测包管理器
detect_package_manager() {
    if [ -f "$PROJECT_PATH/package.json" ]; then
        if [ -f "$PROJECT_PATH/yarn.lock" ]; then
            echo "yarn"
        else
            echo "npm"
        fi
    elif [ -f "$PROJECT_PATH/requirements.txt" ] || [ -f "$PROJECT_PATH/pyproject.toml" ]; then
        echo "pip"
    elif [ -f "$PROJECT_PATH/pom.xml" ]; then
        echo "maven"
    elif [ -f "$PROJECT_PATH/build.gradle" ]; then
        echo "gradle"
    else
        echo "unknown"
    fi
}

# 更新npm依赖
update_npm_dependencies() {
    log_step "更新npm依赖..."
    
    cd "$PROJECT_PATH"
    
    # 检查过时依赖
    log_info "检查过时依赖..."
    npm outdated > outdated_deps.tmp 2>/dev/null || true
    
    if [ -s "outdated_deps.tmp" ]; then
        log_info "发现过时依赖"
        
        if [ "$DRY_RUN" = "true" ]; then
            log_warn "试运行模式，不会实际更新"
            cat outdated_deps.tmp
        else
            # 根据更新类型执行更新
            case $UPDATE_TYPE in
                "patch")
                    log_info "更新补丁版本..."
                    npm update
                    ;;
                "minor")
                    log_info "更新次要版本..."
                    npm update
                    # 对于npm，需要手动更新package.json中的版本范围
                    ;;
                "major")
                    log_warn "主要版本更新需要手动处理"
                    ;;
            esac
            
            # 重新安装以确保一致性
            npm install
        fi
    else
        log_info "没有发现过时依赖"
    fi
    
    rm -f outdated_deps.tmp
}

# 更新pip依赖
update_pip_dependencies() {
    log_step "更新pip依赖..."
    
    cd "$PROJECT_PATH"
    
    # 检查过时依赖
    if command -v pip-upgrade-outdated &> /dev/null; then
        if [ "$DRY_RUN" = "true" ]; then
            log_warn "试运行模式，显示可更新的包"
            pip-upgrade-outdated --dry-run
        else
            log_info "更新pip依赖..."
            pip-upgrade-outdated
        fi
    else
        log_warn "pip-upgrade-outdated未安装，尝试手动更新"
        
        # 创建requirements文件
        if [ -f "requirements.txt" ]; then
            if [ "$DRY_RUN" = "false" ]; then
                log_info "备份requirements.txt"
                cp requirements.txt requirements.txt.backup
                
                log_info "更新requirements.txt中的依赖"
                # 这里应该使用更智能的更新逻辑
                pip-review --auto || true
            fi
        fi
    fi
}

# 更新maven依赖
update_maven_dependencies() {
    log_step "更新maven依赖..."
    
    cd "$PROJECT_PATH"
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "试运行模式，检查maven依赖更新"
        mvn versions:display-dependency-updates
    else
        log_info "更新maven依赖..."
        mvn versions:use-latest-releases
        mvn versions:use-latest-versions
        mvn versions:commit
    fi
}

# 更新gradle依赖
update_gradle_dependencies() {
    log_step "更新gradle依赖..."
    
    cd "$PROJECT_PATH"
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "试运行模式，检查gradle依赖更新"
        ./gradlew dependencyUpdates || true
    else
        log_info "更新gradle依赖..."
        # 使用gradle-use-latest-versions插件或其他工具
        ./gradlew useLatestVersions || true
    fi
}

# 安全检查
security_audit() {
    log_step "执行安全审计..."
    
    cd "$PROJECT_PATH"
    
    case $(detect_package_manager) in
        "npm")
            log_info "执行npm audit..."
            npm audit --audit-level=moderate || true
            ;;
        "yarn")
            log_info "执行yarn audit..."
            yarn audit || true
            ;;
        "pip")
            log_info "执行pip audit..."
            if command -v pip-audit &> /dev/null; then
                pip-audit || true
            else
                log_warn "pip-audit未安装，跳过安全审计"
            fi
            ;;
        *)
            log_warn "不支持的包管理器，跳过安全审计"
            ;;
    esac
}

# 清理未使用依赖
cleanup_unused() {
    log_step "清理未使用依赖..."
    
    cd "$PROJECT_PATH"
    
    case $(detect_package_manager) in
        "npm")
            if command -v depcheck &> /dev/null; then
                log_info "检查未使用的npm依赖..."
                depcheck || true
            else
                log_warn "depcheck未安装，跳过未使用依赖检查"
            fi
            ;;
        "pip")
            if command -v pip-autoremove &> /dev/null; then
                if [ "$DRY_RUN" = "false" ]; then
                    log_info "移除未使用的pip依赖..."
                    pip-autoremove || true
                fi
            else
                log_warn "pip-autoremove未安装，跳过未使用依赖清理"
            fi
            ;;
        *)
            log_warn "不支持的包管理器，跳过清理"
            ;;
    esac
}

# 生成更新报告
generate_report() {
    log_step "生成更新报告..."
    
    local report_file="dependency_update_report.md"
    
    cat > "$report_file" << EOF
# 依赖更新报告

## 更新信息
- 项目路径: $PROJECT_PATH
- 更新类型: $UPDATE_TYPE
- 执行模式: $DRY_RUN
- 更新时间: $(date)

## 包管理器
- 检测到的包管理器: $(detect_package_manager)

## 执行的操作
EOF
    
    if [ "$DRY_RUN" = "false" ]; then
        echo "- ✅ 依赖更新已执行" >> "$report_file"
        echo "- ✅ 安全审计已执行" >> "$report_file"
        echo "- ✅ 清理操作已执行" >> "$report_file"
    else
        echo "- 🔍 试运行模式，未实际执行更新" >> "$report_file"
        echo "- 🔍 安全审计已执行" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## 建议" >> "$report_file"
    echo "- 定期更新依赖以保持安全性" >> "$report_file"
    echo "- 在生产环境更新前进行充分测试" >> "$report_file"
    echo "- 使用CI/CD自动化依赖更新流程" >> "$report_file"
    echo "- 监控依赖的安全漏洞和更新通知" >> "$report_file"
    
    log_info "更新报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始依赖更新流程..."
    log_info "项目路径: $PROJECT_PATH"
    log_info "更新类型: $UPDATE_TYPE"
    log_info "执行模式: $DRY_RUN"
    
    # 检测包管理器
    package_manager=$(detect_package_manager)
    log_info "检测到包管理器: $package_manager"
    
    if [ "$package_manager" = "unknown" ]; then
        log_error "无法检测包管理器"
        exit 1
    fi
    
    # 执行更新
    case $package_manager in
        "npm"|"yarn")
            update_npm_dependencies
            ;;
        "pip")
            update_pip_dependencies
            ;;
        "maven")
            update_maven_dependencies
            ;;
        "gradle")
            update_gradle_dependencies
            ;;
    esac
    
    # 安全审计
    security_audit
    
    # 清理未使用依赖
    if [ "$DRY_RUN" = "false" ]; then
        cleanup_unused
    fi
    
    # 生成报告
    generate_report
    
    log_info "依赖更新流程完成！"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [project_path] [dry_run] [update_type]"
    echo ""
    echo "参数:"
    echo "  project_path  项目路径，默认: ."
    echo "  dry_run       是否试运行 (true|false)，默认: true"
    echo "  update_type   更新类型 (patch|minor|major)，默认: patch"
    echo ""
    echo "示例:"
    echo "  $0 . false patch    # 实际更新补丁版本"
    echo "  $0 ./myproject true minor  # 试运行，更新次要版本"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 依赖安全扫描器

```python
#!/usr/bin/env python3
import json
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SecurityAdvisory:
    """安全建议"""
    id: str
    package: str
    severity: str
    title: str
    description: str
    patched_versions: List[str]
    vulnerable_versions: List[str]
    cve_id: Optional[str] = None
    published_at: Optional[str] = None
    references: List[str] = None

class DependencySecurityScanner:
    """依赖安全扫描器"""
    
    def __init__(self):
        self.advisories: List[SecurityAdvisory] = []
        self.cache_file = Path.home() / ".dependency_security_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache(self):
        """保存缓存"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except:
            pass
    
    def scan_npm_security(self, package_name: str, version: str) -> List[SecurityAdvisory]:
        """扫描npm包安全漏洞"""
        advisories = []
        
        try:
            # 使用npm advisory API
            url = f"https://registry.npmjs.org/-/v1/advisories"
            params = {
                'package': package_name,
                'version': version
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for advisory_data in data.get('objects', []):
                    advisory = SecurityAdvisory(
                        id=advisory_data.get('id', ''),
                        package=advisory_data.get('module_name', ''),
                        severity=advisory_data.get('severity', ''),
                        title=advisory_data.get('title', ''),
                        description=advisory_data.get('overview', ''),
                        patched_versions=advisory_data.get('patched_versions', []),
                        vulnerable_versions=advisory_data.get('vulnerable_versions', []),
                        cve_id=advisory_data.get('cve', ''),
                        published_at=advisory_data.get('created_at', ''),
                        references=advisory_data.get('references', [])
                    )
                    advisories.append(advisory)
        
        except Exception as e:
            print(f"扫描npm安全漏洞失败: {e}")
        
        return advisories
    
    def scan_pip_security(self, package_name: str, version: str) -> List[SecurityAdvisory]:
        """扫描pip包安全漏洞"""
        advisories = []
        
        try:
            # 使用PyPI安全API或OSV数据库
            url = "https://api.osv.dev/v1/query"
            data = {
                'package': {
                    'name': package_name,
                    'ecosystem': 'PyPI'
                },
                'version': version
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                
                for vuln in response_data.get('vulns', []):
                    advisory = SecurityAdvisory(
                        id=vuln.get('id', ''),
                        package=package_name,
                        severity=self._determine_severity(vuln.get('severity', [])),
                        title=vuln.get('summary', ''),
                        description=vuln.get('details', ''),
                        patched_versions=self._extract_patched_versions(vuln),
                        vulnerable_versions=self._extract_vulnerable_versions(vuln),
                        cve_id=self._extract_cve(vuln),
                        published_at=vuln.get('published', ''),
                        references=vuln.get('references', [])
                    )
                    advisories.append(advisory)
        
        except Exception as e:
            print(f"扫描pip安全漏洞失败: {e}")
        
        return advisories
    
    def _determine_severity(self, severity_info: List) -> str:
        """确定严重程度"""
        if not severity_info:
            return "unknown"
        
        severity_map = {
            'CRITICAL': 'critical',
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        
        for severity in severity_info:
            if severity in severity_map:
                return severity_map[severity]
        
        return "unknown"
    
    def _extract_patched_versions(self, vuln: Dict) -> List[str]:
        """提取修复版本"""
        patched = []
        
        for affected in vuln.get('affected', []):
            ranges = affected.get('ranges', [])
            for range_info in ranges:
                events = range_info.get('events', [])
                for event in events:
                    if 'fixed' in event:
                        patched.append(event['fixed'])
        
        return patched
    
    def _extract_vulnerable_versions(self, vuln: Dict) -> List[str]:
        """提取受影响版本"""
        vulnerable = []
        
        for affected in vuln.get('affected', []):
            ranges = affected.get('ranges', [])
            for range_info in ranges:
                events = range_info.get('events', [])
                for event in events:
                    if 'introduced' in event:
                        vulnerable.append(f">={event['introduced']}")
                    if 'limit' in event:
                        vulnerable.append(f"<{event['limit']}")
        
        return vulnerable
    
    def _extract_cve(self, vuln: Dict) -> Optional[str]:
        """提取CVE编号"""
        aliases = vuln.get('aliases', [])
        for alias in aliases:
            if alias.startswith('CVE-'):
                return alias
        return None
    
    def scan_dependencies(self, dependencies: Dict[str, str], ecosystem: str = 'npm') -> Dict:
        """扫描依赖安全漏洞"""
        all_advisories = []
        total_packages = len(dependencies)
        vulnerable_packages = 0
        
        print(f"开始扫描 {total_packages} 个包的安全漏洞...")
        
        for i, (package_name, version) in enumerate(dependencies.items(), 1):
            print(f"扫描进度: {i}/{total_packages} - {package_name}@{version}")
            
            # 检查缓存
            cache_key = f"{ecosystem}:{package_name}:{version}"
            if cache_key in self.cache:
                cached_advisories = [SecurityAdvisory(**adv) for adv in self.cache[cache_key]]
                all_advisories.extend(cached_advisories)
                if cached_advisories:
                    vulnerable_packages += 1
                continue
            
            # 扫描漏洞
            if ecosystem == 'npm':
                advisories = self.scan_npm_security(package_name, version)
            elif ecosystem == 'pip':
                advisories = self.scan_pip_security(package_name, version)
            else:
                print(f"不支持的生态系统: {ecosystem}")
                continue
            
            if advisories:
                vulnerable_packages += 1
                all_advisories.extend(advisories)
                
                # 缓存结果
                self.cache[cache_key] = [
                    {
                        'id': adv.id,
                        'package': adv.package,
                        'severity': adv.severity,
                        'title': adv.title,
                        'description': adv.description,
                        'patched_versions': adv.patched_versions,
                        'vulnerable_versions': adv.vulnerable_versions,
                        'cve_id': adv.cve_id,
                        'published_at': adv.published_at,
                        'references': adv.references
                    }
                    for adv in advisories
                ]
        
        # 保存缓存
        self._save_cache()
        
        # 统计信息
        critical_count = len([adv for adv in all_advisories if adv.severity == 'critical'])
        high_count = len([adv for adv in all_advisories if adv.severity == 'high'])
        medium_count = len([adv for adv in all_advisories if adv.severity == 'medium'])
        low_count = len([adv for adv in all_advisories if adv.severity == 'low'])
        
        return {
            'summary': {
                'total_packages': total_packages,
                'vulnerable_packages': vulnerable_packages,
                'total_advisories': len(all_advisories),
                'critical_advisories': critical_count,
                'high_advisories': high_count,
                'medium_advisories': medium_count,
                'low_advisories': low_count
            },
            'advisories': [
                {
                    'package': adv.package,
                    'severity': adv.severity,
                    'title': adv.title,
                    'description': adv.description,
                    'patched_versions': adv.patched_versions,
                    'vulnerable_versions': adv.vulnerable_versions,
                    'cve_id': adv.cve_id,
                    'published_at': adv.published_at
                }
                for adv in all_advisories
            ]
        }
    
    def generate_security_report(self, scan_result: Dict, output_file: Optional[str] = None) -> str:
        """生成安全报告"""
        report = []
        report.append("# 依赖安全扫描报告")
        report.append("")
        report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 摘要
        summary = scan_result['summary']
        report.append("## 扫描摘要")
        report.append(f"- 总包数: {summary['total_packages']}")
        report.append(f"- 有漏洞包数: {summary['vulnerable_packages']}")
        report.append(f"- 总建议数: {summary['total_advisories']}")
        report.append(f"- 严重漏洞: {summary['critical_advisories']}")
        report.append(f"- 高危漏洞: {summary['high_advisories']}")
        report.append(f"- 中危漏洞: {summary['medium_advisories']}")
        report.append(f"- 低危漏洞: {summary['low_advisories']}")
        report.append("")
        
        # 漏洞详情
        if scan_result['advisories']:
            report.append("## 漏洞详情")
            
            # 按严重程度分组
            advisories_by_severity = {}
            for advisory in scan_result['advisories']:
                severity = advisory['severity']
                if severity not in advisories_by_severity:
                    advisories_by_severity[severity] = []
                advisories_by_severity[severity].append(advisory)
            
            severity_order = ['critical', 'high', 'medium', 'low']
            severity_names = {
                'critical': '🚨 严重',
                'high': '❌ 高危',
                'medium': '⚠️ 中危',
                'low': 'ℹ️ 低危'
            }
            
            for severity in severity_order:
                if severity in advisories_by_severity:
                    report.append(f"### {severity_names[severity]}漏洞")
                    for advisory in advisories_by_severity[severity]:
                        report.append(f"#### {advisory['package']}")
                        report.append(f"**标题**: {advisory['title']}")
                        report.append(f"**描述**: {advisory['description']}")
                        if advisory['cve_id']:
                            report.append(f"**CVE**: {advisory['cve_id']}")
                        if advisory['patched_versions']:
                            report.append(f"**修复版本**: {', '.join(advisory['patched_versions'])}")
                        if advisory['vulnerable_versions']:
                            report.append(f"**受影响版本**: {', '.join(advisory['vulnerable_versions'])}")
                        report.append("")
        else:
            report.append("## ✅ 未发现安全漏洞")
        
        # 建议
        report.append("## 安全建议")
        report.append("- 定期更新依赖包到最新安全版本")
        report.append("- 使用自动化工具监控安全漏洞")
        report.append("- 在CI/CD流程中集成安全扫描")
        report.append("- 建立依赖安全评估流程")
        report.append("- 关注安全公告和CVE通知")
        
        report_content = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"安全报告已保存到: {output_file}")
        
        return report_content

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='依赖安全扫描器')
    parser.add_argument('--package', help='要扫描的单个包名')
    parser.add_argument('--version', help='包版本')
    parser.add_argument('--ecosystem', choices=['npm', 'pip'], default='npm', help='包生态系统')
    parser.add_argument('--dependencies-file', help='依赖文件路径')
    parser.add_argument('--output', help='输出报告文件')
    
    args = parser.parse_args()
    
    scanner = DependencySecurityScanner()
    
    try:
        if args.package and args.version:
            # 扫描单个包
            print(f"扫描 {args.package}@{args.version}...")
            
            if args.ecosystem == 'npm':
                advisories = scanner.scan_npm_security(args.package, args.version)
            else:
                advisories = scanner.scan_pip_security(args.package, args.version)
            
            if advisories:
                print(f"发现 {len(advisories)} 个安全漏洞:")
                for advisory in advisories:
                    print(f"  {advisory.severity}: {advisory.title}")
            else:
                print("未发现安全漏洞")
        
        elif args.dependencies_file:
            # 扫描依赖文件
            print(f"扫描依赖文件: {args.dependencies_file}")
            
            # 这里应该解析依赖文件，简化示例
            dependencies = {
                'lodash': '4.17.20',
                'express': '4.17.1',
                'axios': '0.21.1'
            }
            
            scan_result = scanner.scan_dependencies(dependencies, args.ecosystem)
            
            # 生成报告
            report_content = scanner.generate_security_report(scan_result, args.output)
            
            if not args.output:
                print(report_content)
        
        else:
            print("请指定要扫描的包或依赖文件")
            parser.print_help()
    
    except Exception as e:
        print(f"扫描失败: {e}")
        exit(1)
```

## 最佳实践

### 依赖管理
- **定期更新**: 定期检查和更新依赖版本
- **版本锁定**: 使用锁定文件确保构建一致性
- **安全扫描**: 定期进行安全漏洞扫描
- **依赖审计**: 定期审计和清理未使用依赖

### 安全性
- **漏洞监控**: 监控依赖的安全漏洞
- **自动更新**: 使用自动化工具更新安全补丁
- **许可证检查**: 检查依赖的许可证合规性
- **供应链安全**: 验证依赖的来源和完整性

### 优化策略
- **精简依赖**: 移除未使用和冗余依赖
- **版本策略**: 制定合理的版本更新策略
- **替代方案**: 寻找更安全、更轻量的替代方案
- **性能优化**: 优化依赖的加载和运行性能

### 团队协作
- **依赖规范**: 制定依赖管理规范
- **代码审查**: 在代码审查中检查依赖变更
- **文档维护**: 维护依赖文档和变更记录
- **培训指导**: 培训团队依赖管理最佳实践

## 相关技能

- [安全扫描器](./security-scanner/) - 代码安全检查
- [版本管理器](./version-manager/) - 版本控制管理
- [环境验证器](./env-validator/) - 环境配置验证
- [文件分析器](./file-analyzer/) - 项目文件分析

**Known Vulnerabilities**
- CVE 在 dependencies
- Exploit 代码 publicly available
- Attackers targeting known issues

**Outdated 版本s**
- 安全 patches missing
- 性能 improvements not applied
- 错误 fixes not available

**未使用的 Dependencies**
- Dead weight 在 包
- Maintenance burden
- 安全 liabilities

**Conflicting 版本s**
- Different packages need different 版本s
- Can cause unexpected behavior
- Hard 到 调试

## 验证检查清单

- [ ] No known vulnerabilities
- [ ] Dependencies up 到 date
- [ ] No 未使用的 packages
- [ ] No 版本 conflicts
- [ ] Size impact understood
- [ ] Maintenance burden acceptable

## 相关技能
- **security-scanner** - Find vulnerabilities
- **code-review** - Review dependency usage
