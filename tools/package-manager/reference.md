# 包管理器参考文档

## 包管理器概述

### 什么是包管理器
包管理器是一个专门用于管理软件包依赖、版本控制、构建发布和生命周期管理的工具。该工具支持多种包管理器（npm、yarn、pip、maven等），提供依赖分析、安全扫描、版本管理、构建优化和发布管理等功能，帮助开发团队高效管理项目依赖、确保安全合规和优化构建流程。

### 主要功能
- **多包管理器支持**: 支持npm、yarn、pip、maven、gradle、go modules、cargo等
- **依赖管理**: 依赖分析、版本控制、冲突解决和自动更新
- **安全管理**: 漏洞检测、安全策略、合规检查和许可证管理
- **构建优化**: 缓存策略、并行构建、性能优化和环境管理
- **发布管理**: 版本发布、包发布、平台集成和自动化流程

## 包管理引擎

### 核心包管理器
```python
# package_manager.py
import os
import json
import yaml
import subprocess
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

class PackageManagerType(Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    PIP = "pip"
    PIPENV = "pipenv"
    POETRY = "poetry"
    MAVEN = "maven"
    GRADLE = "gradle"
    GO_MOD = "go_mod"
    CARGO = "cargo"

class DependencyType(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"
    PEER = "peer"
    BUNDLED = "bundled"

class SecurityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class PackageInfo:
    name: str
    version: str
    description: str = ""
    author: str = ""
    license: str = ""
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)
    peer_dependencies: Dict[str, str] = field(default_factory=dict)
    optional_dependencies: Dict[str, str] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    engines: Dict[str, str] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)
    main: str = ""
    types: str = ""

@dataclass
class VulnerabilityInfo:
    package_name: str
    vulnerability_id: str
    severity: SecurityLevel
    title: str
    description: str
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    patched_versions: List[str] = field(default_factory=list)
    unaffected_versions: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    published_date: Optional[str] = None
    updated_date: Optional[str] = None

@dataclass
class DependencyAnalysis:
    total_packages: int
    production_packages: int
    development_packages: int
    optional_packages: int
    peer_packages: int
    total_size: int
    vulnerabilities: List[VulnerabilityInfo] = field(default_factory=list)
    outdated_packages: List[Dict[str, Any]] = field(default_factory=list)
    duplicate_packages: List[Dict[str, Any]] = field(default_factory=list)
    unused_packages: List[str] = field(default_factory=list)
    license_issues: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PackageManagerConfig:
    project_path: str
    package_manager: PackageManagerType
    registry_url: str = ""
    cache_enabled: bool = True
    cache_path: str = ""
    parallel_install: bool = True
    max_workers: int = 4
    security_scan: bool = True
    auto_update: bool = False
    update_strategy: str = "patch"  # patch, minor, major
    lock_file: bool = True
    audit_level: SecurityLevel = SecurityLevel.MEDIUM

class PackageManager:
    def __init__(self, config: PackageManagerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.project_path = Path(config.project_path)
        self.cache = {}
        self.vulnerability_db = VulnerabilityDatabase()
        
        # 验证项目路径
        if not self.project_path.exists():
            raise ValueError(f"项目路径不存在: {config.project_path}")
    
    def analyze_dependencies(self) -> DependencyAnalysis:
        """分析依赖"""
        self.logger.info(f"开始分析项目依赖: {self.config.project_path}")
        
        # 获取包信息
        package_info = self._get_package_info()
        
        # 分析依赖树
        dependency_tree = self._analyze_dependency_tree()
        
        # 检查漏洞
        vulnerabilities = []
        if self.config.security_scan:
            vulnerabilities = self._scan_vulnerabilities(dependency_tree)
        
        # 检查过时包
        outdated_packages = self._check_outdated_packages(dependency_tree)
        
        # 检查重复包
        duplicate_packages = self._check_duplicate_packages(dependency_tree)
        
        # 检查未使用包
        unused_packages = self._check_unused_packages(dependency_tree)
        
        # 检查许可证
        license_issues = self._check_licenses(dependency_tree)
        
        # 计算统计信息
        total_packages = len(dependency_tree)
        production_packages = len(package_info.dependencies)
        development_packages = len(package_info.dev_dependencies)
        optional_packages = len(package_info.optional_dependencies)
        peer_packages = len(package_info.peer_dependencies)
        
        # 计算总大小
        total_size = self._calculate_package_size(dependency_tree)
        
        return DependencyAnalysis(
            total_packages=total_packages,
            production_packages=production_packages,
            development_packages=development_packages,
            optional_packages=optional_packages,
            peer_packages=peer_packages,
            total_size=total_size,
            vulnerabilities=vulnerabilities,
            outdated_packages=outdated_packages,
            duplicate_packages=duplicate_packages,
            unused_packages=unused_packages,
            license_issues=license_issues
        )
    
    def _get_package_info(self) -> PackageInfo:
        """获取包信息"""
        if self.config.package_manager == PackageManagerType.NPM:
            return self._get_npm_package_info()
        elif self.config.package_manager == PackageManagerType.YARN:
            return self._get_yarn_package_info()
        elif self.config.package_manager == PackageManagerType.PIP:
            return self._get_pip_package_info()
        elif self.config.package_manager == PackageManagerType.MAVEN:
            return self._get_maven_package_info()
        else:
            raise ValueError(f"不支持的包管理器: {self.config.package_manager}")
    
    def _get_npm_package_info(self) -> PackageInfo:
        """获取npm包信息"""
        package_json_path = self.project_path / "package.json"
        
        if not package_json_path.exists():
            raise FileNotFoundError("package.json文件不存在")
        
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        return PackageInfo(
            name=package_data.get('name', ''),
            version=package_data.get('version', ''),
            description=package_data.get('description', ''),
            author=package_data.get('author', ''),
            license=package_data.get('license', ''),
            homepage=package_data.get('homepage', ''),
            repository=package_data.get('repository', {}).get('url', '') if isinstance(package_data.get('repository'), dict) else package_data.get('repository', ''),
            keywords=package_data.get('keywords', []),
            dependencies=package_data.get('dependencies', {}),
            dev_dependencies=package_data.get('devDependencies', {}),
            peer_dependencies=package_data.get('peerDependencies', {}),
            optional_dependencies=package_data.get('optionalDependencies', {}),
            scripts=package_data.get('scripts', {}),
            engines=package_data.get('engines', {}),
            files=package_data.get('files', []),
            main=package_data.get('main', ''),
            types=package_data.get('types', '')
        )
    
    def _get_yarn_package_info(self) -> PackageInfo:
        """获取yarn包信息"""
        # Yarn使用相同的package.json格式
        return self._get_npm_package_info()
    
    def _get_pip_package_info(self) -> PackageInfo:
        """获取pip包信息"""
        requirements_path = self.project_path / "requirements.txt"
        setup_py_path = self.project_path / "setup.py"
        
        dependencies = {}
        dev_dependencies = {}
        
        # 读取requirements.txt
        if requirements_path.exists():
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 解析依赖格式: package>=1.0.0
                        parts = re.split(r'[<>=!]', line, 1)
                        if parts:
                            package_name = parts[0].strip()
                            version_spec = line[len(package_name):].strip()
                            dependencies[package_name] = version_spec or "*"
        
        # 读取setup.py
        if setup_py_path.exists():
            # 简化的setup.py解析
            with open(setup_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取install_requires
                install_requires_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if install_requires_match:
                    requires_str = install_requires_match.group(1)
                    for req in re.findall(r'["\']([^"\']+)["\']', requires_str):
                        parts = re.split(r'[<>=!]', req, 1)
                        if parts:
                            package_name = parts[0].strip()
                            version_spec = req[len(package_name):].strip()
                            dependencies[package_name] = version_spec or "*"
        
        return PackageInfo(
            name=self.project_path.name,
            version="1.0.0",
            dependencies=dependencies,
            dev_dependencies=dev_dependencies
        )
    
    def _get_maven_package_info(self) -> PackageInfo:
        """获取maven包信息"""
        pom_path = self.project_path / "pom.xml"
        
        if not pom_path.exists():
            raise FileNotFoundError("pom.xml文件不存在")
        
        # 简化的pom.xml解析
        with open(pom_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取项目信息
        name_match = re.search(r'<name>(.*?)</name>', content)
        version_match = re.search(r'<version>(.*?)</version>', content)
        description_match = re.search(r'<description>(.*?)</description>', content)
        
        # 提取依赖
        dependencies = {}
        dep_matches = re.findall(r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?<version>(.*?)</version>.*?</dependency>', content, re.DOTALL)
        
        for group_id, artifact_id, version in dep_matches:
            package_name = f"{group_id}:{artifact_id}"
            dependencies[package_name] = version
        
        return PackageInfo(
            name=name_match.group(1) if name_match else self.project_path.name,
            version=version_match.group(1) if version_match else "1.0.0",
            description=description_match.group(1) if description_match else "",
            dependencies=dependencies
        )
    
    def _analyze_dependency_tree(self) -> Dict[str, Any]:
        """分析依赖树"""
        if self.config.package_manager == PackageManagerType.NPM:
            return self._analyze_npm_dependency_tree()
        elif self.config.package_manager == PackageManagerType.YARN:
            return self._analyze_yarn_dependency_tree()
        elif self.config.package_manager == PackageManagerType.PIP:
            return self._analyze_pip_dependency_tree()
        elif self.config.package_manager == PackageManagerType.MAVEN:
            return self._analyze_maven_dependency_tree()
        else:
            raise ValueError(f"不支持的包管理器: {self.config.package_manager}")
    
    def _analyze_npm_dependency_tree(self) -> Dict[str, Any]:
        """分析npm依赖树"""
        try:
            # 使用npm ls命令获取依赖树
            result = subprocess.run(
                ['npm', 'ls', '--json', '--depth=0'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"npm ls失败: {result.stderr}")
                return {}
            
            tree_data = json.loads(result.stdout)
            return tree_data
            
        except subprocess.TimeoutExpired:
            self.logger.error("npm ls超时")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"解析npm ls输出失败: {e}")
            return {}
    
    def _analyze_yarn_dependency_tree(self) -> Dict[str, Any]:
        """分析yarn依赖树"""
        try:
            # 使用yarn list命令获取依赖树
            result = subprocess.run(
                ['yarn', 'list', '--json', '--depth=0'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"yarn list失败: {result.stderr}")
                return {}
            
            # 解析yarn JSON输出
            lines = result.stdout.strip().split('\n')
            tree_data = {}
            
            for line in lines:
                try:
                    data = json.loads(line)
                    if 'data' in data:
                        tree_data.update(data['data'])
                except json.JSONDecodeError:
                    continue
            
            return tree_data
            
        except subprocess.TimeoutExpired:
            self.logger.error("yarn list超时")
            return {}
    
    def _analyze_pip_dependency_tree(self) -> Dict[str, Any]:
        """分析pip依赖树"""
        try:
            # 使用pip list命令获取已安装包
            result = subprocess.run(
                ['pip', 'list', '--format=json'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"pip list失败: {result.stderr}")
                return {}
            
            packages = json.loads(result.stdout)
            tree_data = {
                'packages': {pkg['name']: pkg for pkg in packages}
            }
            
            return tree_data
            
        except subprocess.TimeoutExpired:
            self.logger.error("pip list超时")
            return {}
    
    def _analyze_maven_dependency_tree(self) -> Dict[str, Any]:
        """分析maven依赖树"""
        try:
            # 使用mvn dependency:tree命令获取依赖树
            result = subprocess.run(
                ['mvn', 'dependency:tree', '-DoutputType=json'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.error(f"mvn dependency:tree失败: {result.stderr}")
                return {}
            
            # 解析Maven依赖树输出
            # 这里需要根据实际输出格式进行解析
            tree_data = {'dependencies': []}
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '+' in line or '\\' in line:
                    # 解析依赖行
                    dep_match = re.search(r'([^-]+)--\s+(.+):(.+):(.+):(.+)', line)
                    if dep_match:
                        scope, group_id, artifact_id, packaging, version = dep_match.groups()
                        tree_data['dependencies'].append({
                            'groupId': group_id.strip(),
                            'artifactId': artifact_id.strip(),
                            'version': version.strip(),
                            'scope': scope.strip()
                        })
            
            return tree_data
            
        except subprocess.TimeoutExpired:
            self.logger.error("mvn dependency:tree超时")
            return {}
    
    def _scan_vulnerabilities(self, dependency_tree: Dict[str, Any]) -> List[VulnerabilityInfo]:
        """扫描漏洞"""
        vulnerabilities = []
        
        # 提取所有包名和版本
        packages = self._extract_packages_from_tree(dependency_tree)
        
        # 并发检查漏洞
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_package = {
                executor.submit(self.vulnerability_db.check_vulnerability, name, version): (name, version)
                for name, version in packages.items()
            }
            
            for future in as_completed(future_to_package):
                name, version = future_to_package[future]
                try:
                    vulns = future.result()
                    vulnerabilities.extend(vulns)
                except Exception as e:
                    self.logger.error(f"检查包漏洞失败 {name}@{version}: {e}")
        
        return vulnerabilities
    
    def _extract_packages_from_tree(self, tree: Dict[str, Any]) -> Dict[str, str]:
        """从依赖树中提取包信息"""
        packages = {}
        
        if self.config.package_manager in [PackageManagerType.NPM, PackageManagerType.YARN]:
            # npm/yarn格式
            if 'dependencies' in tree:
                for name, info in tree['dependencies'].items():
                    packages[name] = info.get('version', 'unknown')
        
        elif self.config.package_manager == PackageManagerType.PIP:
            # pip格式
            if 'packages' in tree:
                for name, info in tree['packages'].items():
                    packages[name] = info.get('version', 'unknown')
        
        elif self.config.package_manager == PackageManagerType.MAVEN:
            # Maven格式
            if 'dependencies' in tree:
                for dep in tree['dependencies']:
                    name = f"{dep['groupId']}:{dep['artifactId']}"
                    packages[name] = dep.get('version', 'unknown')
        
        return packages
    
    def _check_outdated_packages(self, dependency_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查过时包"""
        outdated = []
        
        try:
            if self.config.package_manager == PackageManagerType.NPM:
                result = subprocess.run(
                    ['npm', 'outdated', '--json'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    outdated_data = json.loads(result.stdout)
                    for name, info in outdated_data.items():
                        outdated.append({
                            'name': name,
                            'current': info['current'],
                            'wanted': info['wanted'],
                            'latest': info['latest'],
                            'type': info.get('type', 'dependencies')
                        })
            
            elif self.config.package_manager == PackageManagerType.PIP:
                result = subprocess.run(
                    ['pip', 'list', '--outdated', '--format=json'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    outdated_data = json.loads(result.stdout)
                    for pkg in outdated_data:
                        outdated.append({
                            'name': pkg['name'],
                            'current': pkg['version'],
                            'latest': pkg['latest_version'],
                            'type': 'dependencies'
                        })
        
        except subprocess.TimeoutExpired:
            self.logger.error("检查过时包超时")
        except json.JSONDecodeError as e:
            self.logger.error(f"解析过时包信息失败: {e}")
        
        return outdated
    
    def _check_duplicate_packages(self, dependency_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查重复包"""
        duplicates = []
        
        # 提取所有包及其版本
        packages = self._extract_packages_from_tree(dependency_tree)
        
        # 检查同名不同版本的包
        version_map = {}
        for name, version in packages.items():
            if name not in version_map:
                version_map[name] = []
            version_map[name].append(version)
        
        for name, versions in version_map.items():
            if len(set(versions)) > 1:
                duplicates.append({
                    'name': name,
                    'versions': list(set(versions)),
                    'count': len(versions)
                })
        
        return duplicates
    
    def _check_unused_packages(self, dependency_tree: Dict[str, Any]) -> List[str]:
        """检查未使用包"""
        unused = []
        
        # 这里需要分析代码中实际使用的包
        # 简化实现：检查dev_dependencies中的包
        package_info = self._get_package_info()
        
        if self.config.package_manager == PackageManagerType.NPM:
            # 检查dev_dependencies中可能未使用的包
            for dev_dep in package_info.dev_dependencies:
                # 简单检查：如果包名不在代码中出现，标记为可能未使用
                if not self._is_package_used_in_code(dev_dep):
                    unused.append(dev_dep)
        
        return unused
    
    def _is_package_used_in_code(self, package_name: str) -> bool:
        """检查包是否在代码中使用"""
        # 简化实现：检查源代码文件中是否有import/require
        source_extensions = ['.js', '.ts', '.jsx', '.tsx', '.py', '.java']
        
        for ext in source_extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 检查import/require语句
                        if (f'import.*{package_name}' in content or 
                            f'require.*{package_name}' in content or
                            f'from.*{package_name}' in content):
                            return True
                except (UnicodeDecodeError, IOError):
                    continue
        
        return False
    
    def _check_licenses(self, dependency_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查许可证"""
        license_issues = []
        
        packages = self._extract_packages_from_tree(dependency_tree)
        
        for name, version in packages.items():
            try:
                # 获取包的许可证信息
                license_info = self._get_package_license(name, version)
                
                # 检查许可证兼容性
                if not self._is_license_compatible(license_info):
                    license_issues.append({
                        'name': name,
                        'version': version,
                        'license': license_info,
                        'issue': '许可证不兼容'
                    })
            
            except Exception as e:
                self.logger.error(f"检查包许可证失败 {name}@{version}: {e}")
        
        return license_issues
    
    def _get_package_license(self, package_name: str, version: str) -> str:
        """获取包许可证"""
        # 简化实现：返回默认许可证
        # 实际实现中应该从包仓库获取许可证信息
        return "MIT"
    
    def _is_license_compatible(self, license_name: str) -> bool:
        """检查许可证兼容性"""
        # 简化实现：假设所有许可证都兼容
        # 实际实现中应该根据项目许可证策略进行检查
        compatible_licenses = ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC']
        return license_name in compatible_licenses
    
    def _calculate_package_size(self, dependency_tree: Dict[str, Any]) -> int:
        """计算包大小"""
        total_size = 0
        
        packages = self._extract_packages_from_tree(dependency_tree)
        
        for name, version in packages.items():
            try:
                # 获取包大小
                size = self._get_package_size(name, version)
                total_size += size
            except Exception as e:
                self.logger.error(f"获取包大小失败 {name}@{version}: {e}")
        
        return total_size
    
    def _get_package_size(self, package_name: str, version: str) -> int:
        """获取包大小"""
        # 简化实现：返回估算大小
        # 实际实现中应该从包仓库获取实际大小
        return 1024 * 1024  # 1MB
    
    def install_dependencies(self, packages: Optional[List[str]] = None) -> bool:
        """安装依赖"""
        try:
            if self.config.package_manager == PackageManagerType.NPM:
                cmd = ['npm', 'install']
                if packages:
                    cmd.extend(packages)
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                return result.returncode == 0
            
            elif self.config.package_manager == PackageManagerType.PIP:
                cmd = ['pip', 'install']
                if packages:
                    cmd.extend(packages)
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                return result.returncode == 0
            
            else:
                self.logger.error(f"不支持的包管理器: {self.config.package_manager}")
                return False
        
        except subprocess.TimeoutExpired:
            self.logger.error("安装依赖超时")
            return False
    
    def update_dependencies(self, update_type: str = "patch") -> bool:
        """更新依赖"""
        try:
            if self.config.package_manager == PackageManagerType.NPM:
                if update_type == "patch":
                    cmd = ['npm', 'update']
                elif update_type == "minor":
                    cmd = ['npm', 'update']
                elif update_type == "major":
                    cmd = ['npm', 'update', '--save']
                else:
                    cmd = ['npm', 'update']
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                return result.returncode == 0
            
            elif self.config.package_manager == PackageManagerType.PIP:
                cmd = ['pip', 'install', '--upgrade']
                if update_type == "patch":
                    cmd.extend(['--upgrade-strategy', 'only-if-needed'])
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                return result.returncode == 0
            
            else:
                self.logger.error(f"不支持的包管理器: {self.config.package_manager}")
                return False
        
        except subprocess.TimeoutExpired:
            self.logger.error("更新依赖超时")
            return False

class VulnerabilityDatabase:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
    
    def check_vulnerability(self, package_name: str, version: str) -> List[VulnerabilityInfo]:
        """检查包漏洞"""
        cache_key = f"{package_name}:{version}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        vulnerabilities = []
        
        try:
            # 模拟漏洞检查
            # 实际实现中应该调用真实的漏洞数据库API
            vulnerabilities = self._query_vulnerability_db(package_name, version)
            
            self.cache[cache_key] = vulnerabilities
            
        except Exception as e:
            self.logger.error(f"查询漏洞数据库失败 {package_name}@{version}: {e}")
        
        return vulnerabilities
    
    def _query_vulnerability_db(self, package_name: str, version: str) -> List[VulnerabilityInfo]:
        """查询漏洞数据库"""
        # 简化实现：返回空列表
        # 实际实现中应该调用OSV、Snyk、GitHub Advisory等API
        return []

# 使用示例
config = PackageManagerConfig(
    project_path="./my-project",
    package_manager=PackageManagerType.NPM,
    registry_url="https://registry.npmjs.org",
    cache_enabled=True,
    security_scan=True,
    auto_update=False,
    update_strategy="patch"
)

manager = PackageManager(config)

# 分析依赖
analysis = manager.analyze_dependencies()

print(f"依赖分析结果:")
print(f"总包数: {analysis.total_packages}")
print(f"生产依赖: {analysis.production_packages}")
print(f"开发依赖: {analysis.development_packages}")
print(f"总大小: {analysis.total_size / (1024*1024):.2f} MB")
print(f"漏洞数量: {len(analysis.vulnerabilities)}")
print(f"过时包数: {len(analysis.outdated_packages)}")
print(f"重复包数: {len(analysis.duplicate_packages)}")
print(f"未使用包数: {len(analysis.unused_packages)}")
print(f"许可证问题: {len(analysis.license_issues)}")

# 安装依赖
success = manager.install_dependencies()
print(f"依赖安装: {'成功' if success else '失败'}")

# 更新依赖
success = manager.update_dependencies("patch")
print(f"依赖更新: {'成功' if success else '失败'}")
```

## 安全扫描引擎

### 漏洞检测系统
```python
# security_scanner.py
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import hashlib

@dataclass
class SecurityAdvisory:
    id: str
    package_name: str
    affected_versions: List[str]
    patched_versions: List[str]
    severity: str
    summary: str
    details: str
    references: List[str]
    published_at: str
    updated_at: str

class SecurityScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.advisory_sources = [
            GitHubAdvisorySource(),
            OSVAdvisorySource(),
            NVDAdvisorySource()
        ]
    
    def scan_package(self, package_name: str, version: str) -> List[SecurityAdvisory]:
        """扫描单个包的安全漏洞"""
        all_advisories = []
        
        for source in self.advisory_sources:
            try:
                advisories = source.get_advisories(package_name, version)
                all_advisories.extend(advisories)
            except Exception as e:
                self.logger.error(f"从 {source.__class__.__name__} 获取安全建议失败: {e}")
        
        # 去重和排序
        unique_advisories = self._deduplicate_advisories(all_advisories)
        sorted_advisories = self._sort_advisories_by_severity(unique_advisories)
        
        return sorted_advisories
    
    def _deduplicate_advisories(self, advisories: List[SecurityAdvisory]) -> List[SecurityAdvisory]:
        """去重安全建议"""
        seen = set()
        unique = []
        
        for advisory in advisories:
            advisory_hash = self._hash_advisory(advisory)
            if advisory_hash not in seen:
                seen.add(advisory_hash)
                unique.append(advisory)
        
        return unique
    
    def _hash_advisory(self, advisory: SecurityAdvisory) -> str:
        """生成安全建议哈希"""
        content = f"{advisory.package_name}{advisory.summary}{advisory.published_at}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _sort_advisories_by_severity(self, advisories: List[SecurityAdvisory]) -> List[SecurityAdvisory]:
        """按严重性排序安全建议"""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'moderate': 4}
        
        return sorted(
            advisories,
            key=lambda x: severity_order.get(x.severity.lower(), 5)
        )

class GitHubAdvisorySource:
    def __init__(self):
        self.base_url = "https://api.github.com/advisories"
        self.logger = logging.getLogger(__name__)
    
    def get_advisories(self, package_name: str, version: str) -> List[SecurityAdvisory]:
        """从GitHub获取安全建议"""
        advisories = []
        
        try:
            # 构建查询URL
            url = f"{self.base_url}"
            params = {
                'package': package_name,
                'ecosystem': 'npm',  # 根据包管理器类型调整
                'state': 'published',
                'per_page': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data:
                advisory = self._parse_github_advisory(item)
                if self._is_version_affected(version, advisory.affected_versions):
                    advisories.append(advisory)
        
        except requests.RequestException as e:
            self.logger.error(f"GitHub API请求失败: {e}")
        
        return advisories
    
    def _parse_github_advisory(self, item: Dict[str, Any]) -> SecurityAdvisory:
        """解析GitHub安全建议"""
        return SecurityAdvisory(
            id=item.get('ghsa_id', ''),
            package_name=item.get('package', {}).get('name', ''),
            affected_versions=item.get('vulnerable_version_range', []),
            patched_versions=item.get('patched_versions', []),
            severity=item.get('severity', 'unknown'),
            summary=item.get('summary', ''),
            details=item.get('description', ''),
            references=item.get('references', []),
            published_at=item.get('published_at', ''),
            updated_at=item.get('updated_at', '')
        )
    
    def _is_version_affected(self, version: str, affected_ranges: List[str]) -> bool:
        """检查版本是否受影响"""
        # 简化实现：实际应该使用语义化版本比较
        for range_str in affected_ranges:
            if self._version_in_range(version, range_str):
                return True
        return False
    
    def _version_in_range(self, version: str, range_str: str) -> bool:
        """检查版本是否在范围内"""
        # 简化实现
        return True

class OSVAdvisorySource:
    def __init__(self):
        self.base_url = "https://api.osv.dev/v1/query"
        self.logger = logging.getLogger(__name__)
    
    def get_advisories(self, package_name: str, version: str) -> List[SecurityAdvisory]:
        """从OSV获取安全建议"""
        advisories = []
        
        try:
            payload = {
                'package': {
                    'name': package_name,
                    'ecosystem': 'npm'  # 根据包管理器类型调整
                },
                'version': version
            }
            
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('vulns', []):
                advisory = self._parse_osv_advisory(item)
                advisories.append(advisory)
        
        except requests.RequestException as e:
            self.logger.error(f"OSV API请求失败: {e}")
        
        return advisories
    
    def _parse_osv_advisory(self, item: Dict[str, Any]) -> SecurityAdvisory:
        """解析OSV安全建议"""
        return SecurityAdvisory(
            id=item.get('id', ''),
            package_name=item.get('affected', [{}])[0].get('package', {}).get('name', ''),
            affected_versions=self._extract_affected_versions(item),
            patched_versions=self._extract_patched_versions(item),
            severity=self._extract_severity(item),
            summary=item.get('summary', ''),
            details=item.get('details', ''),
            references=self._extract_references(item),
            published_at=item.get('published', ''),
            updated_at=item.get('modified', '')
        )
    
    def _extract_affected_versions(self, item: Dict[str, Any]) -> List[str]:
        """提取受影响版本"""
        versions = []
        for affected in item.get('affected', []):
            versions.extend(affected.get('versions', []))
        return versions
    
    def _extract_patched_versions(self, item: Dict[str, Any]) -> List[str]:
        """提取已修复版本"""
        versions = []
        for affected in item.get('affected', []):
            versions.extend(affected.get('database_specific', {}).get('fixed_versions', []))
        return versions
    
    def _extract_severity(self, item: Dict[str, Any]) -> str:
        """提取严重性"""
        for affected in item.get('affected', []):
            severity = affected.get('database_specific', {}).get('severity', '')
            if severity:
                return severity
        return 'unknown'
    
    def _extract_references(self, item: Dict[str, Any]) -> List[str]:
        """提取参考链接"""
        return [ref.get('url', '') for ref in item.get('references', [])]

class NVDAdvisorySource:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
        self.logger = logging.getLogger(__name__)
    
    def get_advisories(self, package_name: str, version: str) -> List[SecurityAdvisory]:
        """从NVD获取安全建议"""
        advisories = []
        
        try:
            # 构建搜索参数
            params = {
                'keyword': package_name,
                'resultsPerPage': 100
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('CVE_Items', []):
                advisory = self._parse_nvd_advisory(item)
                if self._is_package_affected(package_name, version, advisory):
                    advisories.append(advisory)
        
        except requests.RequestException as e:
            self.logger.error(f"NVD API请求失败: {e}")
        
        return advisories
    
    def _parse_nvd_advisory(self, item: Dict[str, Any]) -> SecurityAdvisory:
        """解析NVD安全建议"""
        cve = item.get('cve', {})
        
        return SecurityAdvisory(
            id=cve.get('CVE_data_meta', {}).get('ID', ''),
            package_name='',  # 需要从描述中提取
            affected_versions=[],  # 需要从描述中提取
            patched_versions=[],  # 需要从描述中提取
            severity=self._extract_cvss_severity(item),
            summary=cve.get('description', {}).get('description_data', [{}])[0].get('value', ''),
            details='',
            references=self._extract_nvd_references(cve),
            published_at=item.get('publishedDate', ''),
            updated_at=item.get('lastModifiedDate', '')
        )
    
    def _extract_cvss_severity(self, item: Dict[str, Any]) -> str:
        """提取CVSS严重性"""
        impact = item.get('impact', {})
        
        if 'baseMetricV3' in impact:
            base_severity = impact['baseMetricV3'].get('cvssV3', {}).get('baseSeverity', '')
            return base_severity.lower()
        elif 'baseMetricV2' in impact:
            severity = impact['baseMetricV2'].get('severity', '')
            return severity.lower()
        
        return 'unknown'
    
    def _extract_nvd_references(self, cve: Dict[str, Any]) -> List[str]:
        """提取NVD参考链接"""
        return [ref.get('url', '') for ref in cve.get('references', {}).get('reference_data', [])]
    
    def _is_package_affected(self, package_name: str, version: str, advisory: SecurityAdvisory) -> bool:
        """检查包是否受影响"""
        # 简化实现：检查包名是否在描述中
        return package_name.lower() in advisory.summary.lower()

# 使用示例
scanner = SecurityScanner()

# 扫描包漏洞
advisories = scanner.scan_package("express", "4.17.1")

print(f"发现 {len(advisories)} 个安全漏洞:")
for advisory in advisories:
    print(f"- {advisory.id}: {advisory.severity} - {advisory.summary}")
```

## 参考资源

### 包管理器文档
- [npm文档](https://docs.npmjs.com/)
- [yarn文档](https://yarnpkg.com/documentation)
- [pnpm文档](https://pnpm.js.org/documentation/)
- [pip文档](https://pip.pypa.io/en/stable/)
- [poetry文档](https://python-poetry.org/docs/)
- [maven文档](https://maven.apache.org/guides/)
- [gradle文档](https://docs.gradle.org/current/userguide/userguide.html)
- [go modules文档](https://golang.org/doc/modules/)
- [cargo文档](https://doc.rust-lang.org/cargo/)

### 安全数据库
- [GitHub Advisory](https://github.com/advisories)
- [OSV.dev](https://osv.dev/)
- [NVD](https://nvd.nist.gov/)
- [Snyk Vulnerability Database](https://snyk.io/vuln/)
- [CVE Database](https://cve.mitre.org/)

### 依赖分析工具
- [npm audit](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [yarn audit](https://yarnpkg.com/cli/audit)
- [pip-audit](https://pypi.org/project/pip-audit/)
- [safety](https://pypi.org/project/safety/)
- [snyk](https://snyk.io/)

### 构建优化
- [npm ci](https://docs.npmjs.com/cli/v8/commands/npm-ci)
- [yarn install --frozen-lockfile](https://yarnpkg.com/cli/install)
- [pip install --require-hashes](https://pip.pypa.io/en/stable/cli/pip_install/)
- [maven dependency management](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)
- [gradle dependency management](https://docs.gradle.org/current/userguide/dependency_management.html)
