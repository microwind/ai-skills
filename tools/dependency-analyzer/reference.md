# 依赖分析器参考文档

## 依赖分析器概述

### 什么是依赖分析器
依赖分析器是一个专门用于分析项目依赖关系的工具，能够扫描、解析和评估项目中的各种依赖包，包括直接依赖和间接依赖。该工具支持多种编程语言和包管理器，提供安全漏洞扫描、许可证合规检查、版本兼容性分析、依赖质量评估等功能，帮助开发者维护健康、安全、合规的依赖生态系统。

### 主要功能
- **多语言支持**: 支持JavaScript、Python、Java、.NET、Go、Rust等多种编程语言
- **依赖树分析**: 构建完整的依赖关系树，包括直接和间接依赖
- **安全漏洞扫描**: 基于CVE、NVD等数据库检测已知安全漏洞
- **许可证合规检查**: 分析依赖包的许可证，确保符合公司和法律要求
- **版本管理**: 检测过时依赖、版本冲突和兼容性问题
- **质量评估**: 评估依赖包的维护状态、流行度和代码质量
- **报告生成**: 生成详细的分析报告和建议

## 依赖解析引擎

### 通用依赖解析器
```python
# dependency_resolver.py
import json
import xml.etree.ElementTree as ET
import toml
import yaml
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import re
import requests
from urllib.parse import urljoin

class PackageManager(Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    PIP = "pip"
    POETRY = "poetry"
    MAVEN = "maven"
    GRADLE = "gradle"
    NUGET = "nuget"
    CARGO = "cargo"
    COMPOSER = "composer"
    BUNDLER = "bundler"

class DependencyType(Enum):
    DEPENDENCIES = "dependencies"
    DEV_DEPENDENCIES = "devDependencies"
    PEER_DEPENDENCIES = "peerDependencies"
    OPTIONAL_DEPENDENCIES = "optionalDependencies"
    BUNDLED_DEPENDENCIES = "bundledDependencies"

@dataclass
class Dependency:
    name: str
    version: str
    version_spec: str
    type: DependencyType
    resolved_version: Optional[str] = None
    integrity: Optional[str] = None
    dev: bool = False
    optional: bool = False
    bundled: bool = False
    license: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    author: Optional[str] = None
    keywords: List[str] = None
    size: Optional[int] = None
    vulnerabilities: List[Dict[str, Any]] = None

@dataclass
class DependencyTree:
    name: str
    version: str
    dependencies: List['DependencyTree']
    metadata: Dict[str, Any]

class DependencyResolver:
    def __init__(self):
        self.resolvers = {
            PackageManager.NPM: NPMResolver(),
            PackageManager.YARN: YarnResolver(),
            PackageManager.PIP: PipResolver(),
            PackageManager.POETRY: PoetryResolver(),
            PackageManager.MAVEN: MavenResolver(),
            PackageManager.GRADLE: GradleResolver(),
            PackageManager.NUGET: NuGetResolver(),
            PackageManager.CARGO: CargoResolver(),
            PackageManager.COMPOSER: ComposerResolver(),
            PackageManager.BUNDLER: BundlerResolver()
        }
    
    def resolve_dependencies(self, project_path: str, 
                           package_manager: PackageManager) -> DependencyTree:
        """解析项目依赖"""
        resolver = self.resolvers.get(package_manager)
        if not resolver:
            raise ValueError(f"不支持的包管理器: {package_manager}")
        
        return resolver.resolve(project_path)
    
    def get_dependency_info(self, package_name: str, package_manager: PackageManager,
                          version: str = None) -> Optional[Dependency]:
        """获取依赖包信息"""
        resolver = self.resolvers.get(package_manager)
        if not resolver:
            return None
        
        return resolver.get_package_info(package_name, version)
    
    def detect_package_manager(self, project_path: str) -> Optional[PackageManager]:
        """自动检测包管理器"""
        project_dir = Path(project_path)
        
        # 检测Node.js包管理器
        if (project_dir / "package.json").exists():
            if (project_dir / "yarn.lock").exists():
                return PackageManager.YARN
            elif (project_dir / "pnpm-lock.yaml").exists():
                return PackageManager.PNPM
            else:
                return PackageManager.NPM
        
        # 检测Python包管理器
        if (project_dir / "pyproject.toml").exists():
            return PackageManager.POETRY
        elif (project_dir / "Pipfile").exists():
            return PackageManager.PIP
        elif (project_dir / "requirements.txt").exists():
            return PackageManager.PIP
        
        # 检测Java包管理器
        if (project_dir / "pom.xml").exists():
            return PackageManager.MAVEN
        elif (project_dir / "build.gradle").exists():
            return PackageManager.GRADLE
        
        # 检测.NET包管理器
        if (project_dir / "packages.config").exists() or (project_dir / "*.csproj").exists():
            return PackageManager.NUGET
        
        # 检测Rust包管理器
        if (project_dir / "Cargo.toml").exists():
            return PackageManager.CARGO
        
        # 检测PHP包管理器
        if (project_dir / "composer.json").exists():
            return PackageManager.COMPOSER
        
        # 检测Ruby包管理器
        if (project_dir / "Gemfile").exists():
            return PackageManager.BUNDLER
        
        return None

# 基础解析器抽象类
class BaseResolver:
    def resolve(self, project_path: str) -> DependencyTree:
        """解析依赖树"""
        raise NotImplementedError
    
    def get_package_info(self, package_name: str, version: str = None) -> Optional[Dependency]:
        """获取包信息"""
        raise NotImplementedError
    
    def parse_version_spec(self, version_spec: str) -> str:
        """解析版本规范"""
        return version_spec

class NPMResolver(BaseResolver):
    def __init__(self):
        self.registry_url = "https://registry.npmjs.org"
    
    def resolve(self, project_path: str) -> DependencyTree:
        """解析NPM依赖"""
        project_dir = Path(project_path)
        package_json_path = project_dir / "package.json"
        
        if not package_json_path.exists():
            raise FileNotFoundError("package.json文件不存在")
        
        # 读取package.json
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # 构建依赖树
        root_name = package_data.get('name', 'root')
        root_version = package_data.get('version', '1.0.0')
        
        dependencies = []
        
        # 解析生产依赖
        deps = package_data.get('dependencies', {})
        for name, version_spec in deps.items():
            dep_info = self.get_package_info(name, version_spec)
            if dep_info:
                dependencies.append(self._build_dependency_tree(dep_info))
        
        # 解析开发依赖
        dev_deps = package_data.get('devDependencies', {})
        for name, version_spec in dev_deps.items():
            dep_info = self.get_package_info(name, version_spec)
            if dep_info:
                dep_info.dev = True
                dependencies.append(self._build_dependency_tree(dep_info))
        
        return DependencyTree(
            name=root_name,
            version=root_version,
            dependencies=dependencies,
            metadata={
                "package_manager": "npm",
                "package_json": package_data
            }
        )
    
    def get_package_info(self, package_name: str, version_spec: str = None) -> Optional[Dependency]:
        """获取NPM包信息"""
        try:
            url = f"{self.registry_url}/{package_name}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析版本
            resolved_version = self._resolve_version(data, version_spec)
            
            # 获取特定版本信息
            version_data = data.get('versions', {}).get(resolved_version, {})
            
            return Dependency(
                name=package_name,
                version=resolved_version,
                version_spec=version_spec or "*",
                type=DependencyType.DEPENDENCIES,
                license=version_data.get('license'),
                description=version_data.get('description'),
                homepage=version_data.get('homepage'),
                repository=self._extract_repository(version_data.get('repository')),
                author=self._extract_author(version_data.get('author')),
                keywords=version_data.get('keywords', []),
                size=data.get('dist', {}).get('unpackedSize')
            )
        
        except Exception as e:
            print(f"获取包信息失败 {package_name}: {e}")
            return None
    
    def _resolve_version(self, package_data: Dict[str, Any], version_spec: str) -> str:
        """解析版本"""
        if not version_spec or version_spec == "*":
            # 获取最新版本
            return package_data.get('dist-tags', {}).get('latest', 'latest')
        
        # 简化版本解析（实际需要更复杂的语义化版本解析）
        versions = list(package_data.get('versions', {}).keys())
        
        # 这里应该实现完整的语义化版本匹配
        # 简化实现：查找匹配的版本
        for version in versions:
            if self._match_version(version, version_spec):
                return version
        
        return versions[-1] if versions else "latest"
    
    def _match_version(self, version: str, spec: str) -> bool:
        """版本匹配"""
        # 简化版本匹配逻辑
        if spec.startswith("^"):
            # 兼容次版本
            major = spec[1:].split('.')[0]
            return version.startswith(major)
        elif spec.startswith("~"):
            # 兼容补丁版本
            major_minor = spec[1:].rsplit('.', 1)[0]
            return version.startswith(major_minor)
        elif spec.startswith(">="):
            # 大于等于
            return version >= spec[2:]
        else:
            # 精确匹配
            return version == spec
    
    def _build_dependency_tree(self, dependency: Dependency) -> DependencyTree:
        """构建依赖树"""
        # 这里应该递归解析子依赖
        # 简化实现，只返回单层
        return DependencyTree(
            name=dependency.name,
            version=dependency.version,
            dependencies=[],
            metadata={"dependency": dependency}
        )
    
    def _extract_repository(self, repo_info: Any) -> Optional[str]:
        """提取仓库信息"""
        if isinstance(repo_info, dict):
            return repo_info.get('url')
        elif isinstance(repo_info, str):
            return repo_info
        return None
    
    def _extract_author(self, author_info: Any) -> Optional[str]:
        """提取作者信息"""
        if isinstance(author_info, dict):
            return author_info.get('name')
        elif isinstance(author_info, str):
            return author_info
        return None

class PipResolver(BaseResolver):
    def __init__(self):
        self.pypi_url = "https://pypi.org/pypi"
    
    def resolve(self, project_path: str) -> DependencyTree:
        """解析Pip依赖"""
        project_dir = Path(project_path)
        
        # 检查requirements.txt
        requirements_txt = project_dir / "requirements.txt"
        if requirements_txt.exists():
            return self._parse_requirements_txt(requirements_txt)
        
        # 检查pyproject.toml
        pyproject_toml = project_dir / "pyproject.toml"
        if pyproject_toml.exists():
            return self._parse_pyproject_toml(pyproject_toml)
        
        # 检查Pipfile
        pipfile = project_dir / "Pipfile"
        if pipfile.exists():
            return self._parse_pipfile(pipfile)
        
        raise FileNotFoundError("未找到Python依赖文件")
    
    def _parse_requirements_txt(self, requirements_file: Path) -> DependencyTree:
        """解析requirements.txt"""
        dependencies = []
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 解析包名和版本
                    package_info = self._parse_requirement_line(line)
                    if package_info:
                        dep_info = self.get_package_info(package_info['name'], package_info['version'])
                        if dep_info:
                            dependencies.append(self._build_dependency_tree(dep_info))
        
        return DependencyTree(
            name="root",
            version="1.0.0",
            dependencies=dependencies,
            metadata={"package_manager": "pip", "requirements_file": str(requirements_file)}
        )
    
    def _parse_requirement_line(self, line: str) -> Optional[Dict[str, str]]:
        """解析requirements.txt行"""
        # 简化的解析逻辑
        if '==' in line:
            name, version = line.split('==', 1)
            return {"name": name.strip(), "version": version.strip()}
        elif '>=' in line:
            name, version = line.split('>=', 1)
            return {"name": name.strip(), "version": f">={version.strip()}"}
        elif '<=' in line:
            name, version = line.split('<=', 1)
            return {"name": name.strip(), "version": f"<={version.strip()}"}
        elif '>' in line:
            name, version = line.split('>', 1)
            return {"name": name.strip(), "version": f">{version.strip()}"}
        elif '<' in line:
            name, version = line.split('<', 1)
            return {"name": name.strip(), "version": f"<{version.strip()}"}
        else:
            return {"name": line.strip(), "version": "*"}
    
    def _parse_pyproject_toml(self, pyproject_file: Path) -> DependencyTree:
        """解析pyproject.toml"""
        with open(pyproject_file, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        dependencies = []
        
        # 解析project.dependencies
        project_deps = data.get('project', {}).get('dependencies', [])
        for dep_spec in project_deps:
            package_info = self._parse_requirement_line(dep_spec)
            if package_info:
                dep_info = self.get_package_info(package_info['name'], package_info['version'])
                if dep_info:
                    dependencies.append(self._build_dependency_tree(dep_info))
        
        # 解析project.optional-dependencies
        optional_deps = data.get('project', {}).get('optional-dependencies', {})
        for group_name, deps in optional_deps.items():
            for dep_spec in deps:
                package_info = self._parse_requirement_line(dep_spec)
                if package_info:
                    dep_info = self.get_package_info(package_info['name'], package_info['version'])
                    if dep_info:
                        dep_info.optional = True
                        dependencies.append(self._build_dependency_tree(dep_info))
        
        return DependencyTree(
            name=data.get('project', {}).get('name', 'root'),
            version=data.get('project', {}).get('version', '1.0.0'),
            dependencies=dependencies,
            metadata={"package_manager": "poetry", "pyproject_toml": data}
        )
    
    def _parse_pipfile(self, pipfile: Path) -> DependencyTree:
        """解析Pipfile"""
        import toml
        
        with open(pipfile, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        dependencies = []
        
        # 解析packages
        packages = data.get('packages', {})
        for name, version_spec in packages.items():
            if isinstance(version_spec, str):
                package_info = {"name": name, "version": version_spec}
            elif isinstance(version_spec, dict):
                package_info = {"name": name, "version": version_spec.get('version', '*')}
            else:
                continue
            
            dep_info = self.get_package_info(package_info['name'], package_info['version'])
            if dep_info:
                dependencies.append(self._build_dependency_tree(dep_info))
        
        # 解析dev-packages
        dev_packages = data.get('dev-packages', {})
        for name, version_spec in dev_packages.items():
            if isinstance(version_spec, str):
                package_info = {"name": name, "version": version_spec}
            elif isinstance(version_spec, dict):
                package_info = {"name": name, "version": version_spec.get('version', '*')}
            else:
                continue
            
            dep_info = self.get_package_info(package_info['name'], package_info['version'])
            if dep_info:
                dep_info.dev = True
                dependencies.append(self._build_dependency_tree(dep_info))
        
        return DependencyTree(
            name=data.get('source', {}).get('url', 'root'),
            version="1.0.0",
            dependencies=dependencies,
            metadata={"package_manager": "pipenv", "pipfile": data}
        )
    
    def get_package_info(self, package_name: str, version_spec: str = None) -> Optional[Dependency]:
        """获取PyPI包信息"""
        try:
            url = f"{self.pypi_url}/{package_name}/json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析版本
            resolved_version = self._resolve_version(data, version_spec)
            
            # 获取特定版本信息
            version_data = data.get('releases', {}).get(resolved_version, [{}])[0]
            latest_info = data.get('info', {})
            
            return Dependency(
                name=package_name,
                version=resolved_version,
                version_spec=version_spec or "*",
                type=DependencyType.DEPENDENCIES,
                license=latest_info.get('license'),
                description=latest_info.get('summary'),
                homepage=latest_info.get('home_page'),
                repository=latest_info.get('project_url'),
                author=latest_info.get('author'),
                keywords=latest_info.get('keywords', []),
                size=version_data.get('size')
            )
        
        except Exception as e:
            print(f"获取包信息失败 {package_name}: {e}")
            return None
    
    def _resolve_version(self, package_data: Dict[str, Any], version_spec: str) -> str:
        """解析版本"""
        if not version_spec or version_spec == "*":
            return package_data.get('info', {}).get('version', 'latest')
        
        # 简化版本解析
        versions = list(package_data.get('releases', {}).keys())
        
        # 实现版本匹配逻辑
        for version in versions:
            if self._match_version(version, version_spec):
                return version
        
        return versions[-1] if versions else "latest"
    
    def _match_version(self, version: str, spec: str) -> bool:
        """版本匹配"""
        # 实现Python版本匹配逻辑
        if spec.startswith(">="):
            return version >= spec[2:]
        elif spec.startswith("<="):
            return version <= spec[2:]
        elif spec.startswith(">"):
            return version > spec[1:]
        elif spec.startswith("<"):
            return version < spec[1:]
        elif spec.startswith("=="):
            return version == spec[2:]
        elif spec.startswith("!="):
            return version != spec[2:]
        else:
            return version == spec
    
    def _build_dependency_tree(self, dependency: Dependency) -> DependencyTree:
        """构建依赖树"""
        return DependencyTree(
            name=dependency.name,
            version=dependency.version,
            dependencies=[],
            metadata={"dependency": dependency}
        )

# 其他解析器实现类似...

# 使用示例
resolver = DependencyResolver()

# 自动检测包管理器
package_manager = resolver.detect_package_manager("./my-project")
print(f"检测到包管理器: {package_manager}")

if package_manager:
    # 解析依赖
    dependency_tree = resolver.resolve_dependencies("./my-project", package_manager)
    
    print(f"项目根: {dependency_tree.name} v{dependency_tree.version}")
    print(f"依赖数量: {len(dependency_tree.dependencies)}")
    
    # 获取特定包信息
    package_info = resolver.get_dependency_info("react", PackageManager.NPM)
    if package_info:
        print(f"React信息: {package_info.description}")
        print(f"许可证: {package_info.license}")
```

## 安全漏洞扫描

### 漏洞扫描引擎
```python
# vulnerability_scanner.py
import requests
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib

class VulnerabilitySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: Optional[float]
    cve_id: Optional[str]
    published_date: Optional[datetime]
    modified_date: Optional[datetime]
    references: List[str]
    affected_versions: List[str]
    patched_versions: List[str]
    recommendations: List[str]

@dataclass
class VulnerabilityMatch:
    vulnerability: Vulnerability
    package_name: str
    package_version: str
    match_reason: str

class VulnerabilityScanner:
    def __init__(self):
        self.vulnerability_databases = [
            OSVDatabase(),
            NVDDatabase(),
            GitHubAdvisoryDatabase(),
            SnykDatabase()
        ]
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    def scan_dependencies(self, dependencies: List[Dependency]) -> List[VulnerabilityMatch]:
        """扫描依赖漏洞"""
        matches = []
        
        for dependency in dependencies:
            package_matches = self._scan_package(dependency)
            matches.extend(package_matches)
        
        return matches
    
    def _scan_package(self, dependency: Dependency) -> List[VulnerabilityMatch]:
        """扫描单个包的漏洞"""
        matches = []
        
        # 检查缓存
        cache_key = f"{dependency.name}:{dependency.version}"
        if cache_key in self.cache:
            cached_time, cached_matches = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                return cached_matches
        
        # 从各个数据库查询
        for database in self.vulnerability_databases:
            try:
                vulnerabilities = database.query_vulnerabilities(dependency.name, dependency.version)
                
                for vuln in vulnerabilities:
                    match = VulnerabilityMatch(
                        vulnerability=vuln,
                        package_name=dependency.name,
                        package_version=dependency.version,
                        match_reason=self._get_match_reason(dependency.version, vuln)
                    )
                    matches.append(match)
            
            except Exception as e:
                print(f"数据库查询失败 {database.__class__.__name__}: {e}")
        
        # 缓存结果
        self.cache[cache_key] = (datetime.now(), matches)
        
        return matches
    
    def _get_match_reason(self, package_version: str, vulnerability: Vulnerability) -> str:
        """获取匹配原因"""
        if package_version in vulnerability.affected_versions:
            return f"版本 {package_version} 在受影响版本列表中"
        elif self._version_in_range(package_version, vulnerability.affected_versions):
            return f"版本 {package_version} 在受影响版本范围内"
        else:
            return f"版本 {package_version} 可能受影响"
    
    def _version_in_range(self, version: str, version_ranges: List[str]) -> bool:
        """检查版本是否在范围内"""
        # 简化的版本范围检查
        for range_spec in version_ranges:
            if self._match_version_range(version, range_spec):
                return True
        return False
    
    def _match_version_range(self, version: str, range_spec: str) -> bool:
        """匹配版本范围"""
        # 实现版本范围匹配逻辑
        # 这里需要完整的语义化版本匹配
        return False
    
    def get_vulnerability_details(self, vulnerability_id: str) -> Optional[Vulnerability]:
        """获取漏洞详细信息"""
        for database in self.vulnerability_databases:
            try:
                vulnerability = database.get_vulnerability_details(vulnerability_id)
                if vulnerability:
                    return vulnerability
            except Exception as e:
                print(f"获取漏洞详情失败 {vulnerability_id}: {e}")
        
        return None
    
    def generate_security_report(self, matches: List[VulnerabilityMatch]) -> Dict[str, Any]:
        """生成安全报告"""
        # 统计信息
        total_vulnerabilities = len(matches)
        severity_counts = {}
        package_counts = {}
        
        for match in matches:
            severity = match.vulnerability.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            package_name = match.package_name
            package_counts[package_name] = package_counts.get(package_name, 0) + 1
        
        # 风险评分
        risk_score = self._calculate_risk_score(matches)
        
        # 修复建议
        recommendations = self._generate_recommendations(matches)
        
        return {
            "summary": {
                "total_vulnerabilities": total_vulnerabilities,
                "severity_distribution": severity_counts,
                "affected_packages": len(package_counts),
                "risk_score": risk_score
            },
            "vulnerabilities": [
                {
                    "id": match.vulnerability.id,
                    "title": match.vulnerability.title,
                    "severity": match.vulnerability.severity.value,
                    "package": match.package_name,
                    "version": match.package_version,
                    "cve_id": match.vulnerability.cve_id,
                    "cvss_score": match.vulnerability.cvss_score,
                    "published_date": match.vulnerability.published_date.isoformat() if match.vulnerability.published_date else None,
                    "recommendations": match.vulnerability.recommendations
                }
                for match in matches
            ],
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_risk_score(self, matches: List[VulnerabilityMatch]) -> float:
        """计算风险评分"""
        severity_weights = {
            VulnerabilitySeverity.CRITICAL: 10,
            VulnerabilitySeverity.HIGH: 7,
            VulnerabilitySeverity.MEDIUM: 4,
            VulnerabilitySeverity.LOW: 2,
            VulnerabilitySeverity.INFO: 1
        }
        
        total_score = 0
        for match in matches:
            weight = severity_weights.get(match.vulnerability.severity, 1)
            total_score += weight
        
        # 归一化到0-100分
        max_possible_score = len(matches) * 10
        if max_possible_score > 0:
            return (total_score / max_possible_score) * 100
        return 0
    
    def _generate_recommendations(self, matches: List[VulnerabilityMatch]) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        # 按严重性分组
        critical_matches = [m for m in matches if m.vulnerability.severity == VulnerabilitySeverity.CRITICAL]
        high_matches = [m for m in matches if m.vulnerability.severity == VulnerabilitySeverity.HIGH]
        
        if critical_matches:
            recommendations.append(f"立即修复 {len(critical_matches)} 个严重漏洞")
        
        if high_matches:
            recommendations.append(f"优先修复 {len(high_matches)} 个高危漏洞")
        
        # 通用建议
        recommendations.append("定期更新依赖包到最新稳定版本")
        recommendations.append("使用自动化工具监控安全漏洞")
        recommendations.append("建立安全漏洞响应流程")
        
        return recommendations

# 漏洞数据库抽象基类
class VulnerabilityDatabase:
    def query_vulnerabilities(self, package_name: str, package_version: str) -> List[Vulnerability]:
        """查询漏洞"""
        raise NotImplementedError
    
    def get_vulnerability_details(self, vulnerability_id: str) -> Optional[Vulnerability]:
        """获取漏洞详情"""
        raise NotImplementedError

class OSVDatabase(VulnerabilityDatabase):
    def __init__(self):
        self.base_url = "https://api.osv.dev/v1"
    
    def query_vulnerabilities(self, package_name: str, package_version: str) -> List[Vulnerability]:
        """查询OSV数据库"""
        try:
            url = f"{self.base_url}/query"
            payload = {
                "package": {
                    "name": package_name,
                    "ecosystem": self._get_ecosystem(package_name)
                },
                "version": package_version
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = []
            
            for vuln_data in data.get('vulns', []):
                vulnerability = self._parse_osv_vulnerability(vuln_data)
                if vulnerability:
                    vulnerabilities.append(vulnerability)
            
            return vulnerabilities
        
        except Exception as e:
            print(f"OSV查询失败: {e}")
            return []
    
    def get_vulnerability_details(self, vulnerability_id: str) -> Optional[Vulnerability]:
        """获取OSV漏洞详情"""
        try:
            url = f"{self.base_url}/vulns/{vulnerability_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_osv_vulnerability(data)
        
        except Exception as e:
            print(f"获取OSV漏洞详情失败: {e}")
            return None
    
    def _get_ecosystem(self, package_name: str) -> str:
        """获取生态系统"""
        # 根据包名推断生态系统
        if package_name.startswith('@'):
            return "npm"
        elif '.' in package_name:
            return "PyPI"
        else:
            return "npm"  # 默认
    
    def _parse_osv_vulnerability(self, vuln_data: Dict[str, Any]) -> Optional[Vulnerability]:
        """解析OSV漏洞数据"""
        try:
            severity = self._determine_severity(vuln_data)
            
            return Vulnerability(
                id=vuln_data.get('id', ''),
                title=vuln_data.get('summary', ''),
                description=vuln_data.get('details', ''),
                severity=severity,
                cvss_score=self._extract_cvss_score(vuln_data),
                cve_id=self._extract_cve_id(vuln_data),
                published_date=self._parse_date(vuln_data.get('published')),
                modified_date=self._parse_date(vuln_data.get('modified')),
                references=vuln_data.get('references', []),
                affected_versions=self._extract_affected_versions(vuln_data),
                patched_versions=self._extract_patched_versions(vuln_data),
                recommendations=self._extract_recommendations(vuln_data)
            )
        
        except Exception as e:
            print(f"解析OSV漏洞失败: {e}")
            return None
    
    def _determine_severity(self, vuln_data: Dict[str, Any]) -> VulnerabilitySeverity:
        """确定严重性"""
        severity_info = vuln_data.get('severity', [])
        
        for severity in severity_info:
            score = severity.get('score', '')
            if 'CRITICAL' in score:
                return VulnerabilitySeverity.CRITICAL
            elif 'HIGH' in score:
                return VulnerabilitySeverity.HIGH
            elif 'MEDIUM' in score:
                return VulnerabilitySeverity.MEDIUM
            elif 'LOW' in score:
                return VulnerabilitySeverity.LOW
        
        return VulnerabilitySeverity.INFO
    
    def _extract_cvss_score(self, vuln_data: Dict[str, Any]) -> Optional[float]:
        """提取CVSS评分"""
        severity_info = vuln_data.get('severity', [])
        for severity in severity_info:
            if 'score' in severity:
                try:
                    score_str = severity['score']
                    if isinstance(score_str, str) and score_str.replace('.', '').isdigit():
                        return float(score_str)
                except:
                    pass
        return None
    
    def _extract_cve_id(self, vuln_data: Dict[str, Any]) -> Optional[str]:
        """提取CVE ID"""
        aliases = vuln_data.get('aliases', [])
        for alias in aliases:
            if alias.startswith('CVE-'):
                return alias
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _extract_affected_versions(self, vuln_data: Dict[str, Any]) -> List[str]:
        """提取受影响版本"""
        versions = []
        
        for affect in vuln_data.get('affected', []):
            ranges = affect.get('ranges', [])
            for range_info in ranges:
                events = range_info.get('events', [])
                for event in events:
                    if 'introduced' in event:
                        versions.append(event['introduced'])
                    if 'fixed' in event:
                        versions.append(f"before {event['fixed']}")
        
        return versions
    
    def _extract_patched_versions(self, vuln_data: Dict[str, Any]) -> List[str]:
        """提取修复版本"""
        versions = []
        
        for affect in vuln_data.get('affected', []):
            ranges = affect.get('ranges', [])
            for range_info in ranges:
                events = range_info.get('events', [])
                for event in events:
                    if 'fixed' in event:
                        versions.append(event['fixed'])
        
        return versions
    
    def _extract_recommendations(self, vuln_data: Dict[str, Any]) -> List[str]:
        """提取修复建议"""
        recommendations = []
        
        # 基于修复版本生成建议
        patched_versions = self._extract_patched_versions(vuln_data)
        if patched_versions:
            recommendations.append(f"升级到 {', '.join(patched_versions)} 或更高版本")
        
        return recommendations

class NVDDatabase(VulnerabilityDatabase):
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = None  # 可以设置API密钥
    
    def query_vulnerabilities(self, package_name: str, package_version: str) -> List[Vulnerability]:
        """查询NVD数据库"""
        # 实现NVD查询逻辑
        return []
    
    def get_vulnerability_details(self, vulnerability_id: str) -> Optional[Vulnerability]:
        """获取NVD漏洞详情"""
        # 实现NVD详情获取逻辑
        return None

# 其他数据库实现类似...

# 使用示例
scanner = VulnerabilityScanner()

# 创建示例依赖
dependencies = [
    Dependency(
        name="react",
        version="16.8.0",
        version_spec="^16.8.0",
        type=DependencyType.DEPENDENCIES
    ),
    Dependency(
        name="lodash",
        version="4.17.15",
        version_spec="^4.17.15",
        type=DependencyType.DEPENDENCIES
    )
]

# 扫描漏洞
vulnerabilities = scanner.scan_dependencies(dependencies)

print(f"发现 {len(vulnerabilities)} 个漏洞")

# 生成安全报告
security_report = scanner.generate_security_report(vulnerabilities)

print(f"风险评分: {security_report['summary']['risk_score']:.1f}")
print(f"严重性分布: {security_report['summary']['severity_distribution']}")

for recommendation in security_report['recommendations']:
    print(f"建议: {recommendation}")
```

## 许可证分析

### 许可证分析器
```python
# license_analyzer.py
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import requests

class LicenseType(Enum):
    PERMISSIVE = "permissive"
    COPYLEFT = "copyleft"
    PROPRIETARY = "proprietary"
    PUBLIC_DOMAIN = "public_domain"
    UNKNOWN = "unknown"

class LicenseCompliance(Enum):
    ALLOWED = "allowed"
    FORBIDDEN = "forbidden"
    WARNING = "warning"
    UNKNOWN = "unknown"

@dataclass
class License:
    name: str
    spdx_id: str
    license_type: LicenseType
    description: str
    permissions: List[str]
    conditions: List[str]
    limitations: List[str]
    commercial_use: bool
    distribution: bool
    modification: bool
    patent_use: bool
    private_use: bool

@dataclass
class LicensePolicy:
    allowed_licenses: Set[str]
    forbidden_licenses: Set[str]
    warning_licenses: Set[str]
    require_license_text: bool
    allow_dual_licensing: bool

@dataclass
class LicenseViolation:
    package_name: str
    package_version: str
    license_name: str
    compliance: LicenseCompliance
    reason: str
    recommendations: List[str]

class LicenseAnalyzer:
    def __init__(self):
        self.license_database = LicenseDatabase()
        self.policy = LicensePolicy(
            allowed_licenses={"MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause"},
            forbidden_licenses={"GPL-3.0", "AGPL-3.0"},
            warning_licenses={"LGPL-2.1", "MPL-2.0"},
            require_license_text=False,
            allow_dual_licensing=True
        )
        self.license_cache = {}
    
    def analyze_licenses(self, dependencies: List[Dependency]) -> List[LicenseViolation]:
        """分析许可证合规性"""
        violations = []
        
        for dependency in dependencies:
            license_violations = self._analyze_dependency_license(dependency)
            violations.extend(license_violations)
        
        return violations
    
    def _analyze_dependency_license(self, dependency: Dependency) -> List[LicenseViolation]:
        """分析单个依赖的许可证"""
        violations = []
        
        if not dependency.license:
            violations.append(LicenseViolation(
                package_name=dependency.name,
                package_version=dependency.version,
                license_name="Unknown",
                compliance=LicenseCompliance.WARNING,
                reason="缺少许可证信息",
                recommendations=["联系作者确认许可证", "查找替代包"]
            ))
            return violations
        
        # 解析许可证名称
        license_names = self._parse_license_string(dependency.license)
        
        for license_name in license_names:
            # 获取许可证详情
            license_info = self._get_license_info(license_name)
            
            if not license_info:
                violations.append(LicenseViolation(
                    package_name=dependency.name,
                    package_version=dependency.version,
                    license_name=license_name,
                    compliance=LicenseCompliance.WARNING,
                    reason="未知许可证",
                    recommendations=["确认许可证类型", "评估许可证风险"]
                ))
                continue
            
            # 检查合规性
            compliance = self._check_license_compliance(license_info)
            
            if compliance != LicenseCompliance.ALLOWED:
                violation = LicenseViolation(
                    package_name=dependency.name,
                    package_version=dependency.version,
                    license_name=license_name,
                    compliance=compliance,
                    reason=self._get_compliance_reason(compliance, license_info),
                    recommendations=self._get_license_recommendations(compliance, license_info)
                )
                violations.append(violation)
        
        return violations
    
    def _parse_license_string(self, license_string: str) -> List[str]:
        """解析许可证字符串"""
        if not license_string:
            return []
        
        # 处理常见的许可证格式
        license_string = license_string.strip()
        
        # 处理括号内的许可证 (MIT OR Apache-2.0)
        if '(' in license_string and ')' in license_string:
            # 提取括号内容
            match = re.search(r'\(([^)]+)\)', license_string)
            if match:
                inner_content = match.group(1)
                return self._parse_license_string(inner_content)
        
        # 处理OR分隔的许可证
        if ' OR ' in license_string:
            parts = license_string.split(' OR ')
            return [part.strip() for part in parts]
        
        # 处理AND分隔的许可证
        if ' AND ' in license_string:
            parts = license_string.split(' AND ')
            return [part.strip() for part in parts]
        
        # 处理斜杠分隔的许可证
        if '/' in license_string:
            parts = license_string.split('/')
            return [part.strip() for part in parts]
        
        # 单个许可证
        return [license_string]
    
    def _get_license_info(self, license_name: str) -> Optional[License]:
        """获取许可证信息"""
        # 检查缓存
        if license_name in self.license_cache:
            return self.license_cache[license_name]
        
        # 从数据库获取
        license_info = self.license_database.get_license(license_name)
        
        # 缓存结果
        if license_info:
            self.license_cache[license_name] = license_info
        
        return license_info
    
    def _check_license_compliance(self, license_info: License) -> LicenseCompliance:
        """检查许可证合规性"""
        spdx_id = license_info.spdx_id
        
        # 检查禁止列表
        if spdx_id in self.policy.forbidden_licenses:
            return LicenseCompliance.FORBIDDEN
        
        # 检查允许列表
        if spdx_id in self.policy.allowed_licenses:
            return LicenseCompliance.ALLOWED
        
        # 检查警告列表
        if spdx_id in self.policy.warning_licenses:
            return LicenseCompliance.WARNING
        
        # 默认为未知
        return LicenseCompliance.UNKNOWN
    
    def _get_compliance_reason(self, compliance: LicenseCompliance, license_info: License) -> str:
        """获取合规性原因"""
        if compliance == LicenseCompliance.FORBIDDEN:
            return f"许可证 {license_info.spdx_id} 在禁止列表中"
        elif compliance == LicenseCompliance.WARNING:
            return f"许可证 {license_info.spdx_id} 需要特别注意"
        elif compliance == LicenseCompliance.UNKNOWN:
            return f"许可证 {license_info.spdx_id} 未在策略中定义"
        else:
            return "许可证合规"
    
    def _get_license_recommendations(self, compliance: LicenseCompliance, 
                                   license_info: License) -> List[str]:
        """获取许可证建议"""
        recommendations = []
        
        if compliance == LicenseCompliance.FORBIDDEN:
            recommendations.append("立即移除此依赖")
            recommendations.append("寻找替代的许可证兼容包")
            recommendations.append("联系法务部门评估风险")
        elif compliance == LicenseCompliance.WARNING:
            recommendations.append("评估许可证风险")
            recommendations.append("确认使用场景是否符合许可证要求")
            recommendations.append("考虑寻找替代方案")
        elif compliance == LicenseCompliance.UNKNOWN:
            recommendations.append("确认许可证类型")
            recommendations.append("评估许可证兼容性")
            recommendations.append("更新许可证策略")
        
        return recommendations
    
    def detect_license_conflicts(self, dependencies: List[Dependency]) -> List[Dict[str, Any]]:
        """检测许可证冲突"""
        conflicts = []
        
        # 获取所有许可证
        all_licenses = set()
        license_packages = {}
        
        for dep in dependencies:
            if dep.license:
                license_names = self._parse_license_string(dep.license)
                for license_name in license_names:
                    all_licenses.add(license_name)
                    if license_name not in license_packages:
                        license_packages[license_name] = []
                    license_packages[license_name].append(dep.name)
        
        # 检测GPL冲突
        gpl_licenses = [lic for lic in all_licenses if 'GPL' in lic]
        if gpl_licenses:
            # GPL要求所有衍生作品也使用GPL
            non_gpl_licenses = all_licenses - set(gpl_licenses)
            if non_gpl_licenses:
                conflicts.append({
                    "type": "GPL传染性冲突",
                    "description": "GPL许可证要求所有衍生作品使用GPL许可证",
                    "gpl_licenses": gpl_licenses,
                    "conflicting_licenses": list(non_gpl_licenses),
                    "affected_packages": [
                        pkg for lic in non_gpl_licenses 
                        for pkg in license_packages.get(lic, [])
                    ]
                })
        
        # 检测商业使用限制
        non_commercial_licenses = [
            lic for lic in all_licenses 
            if self._is_non_commercial(lic)
        ]
        
        if non_commercial_licenses:
            conflicts.append({
                "type": "商业使用限制",
                "description": "某些许可证禁止商业使用",
                "restricted_licenses": non_commercial_licenses,
                "affected_packages": [
                    pkg for lic in non_commercial_licenses 
                    for pkg in license_packages.get(lic, [])
                ]
            })
        
        return conflicts
    
    def _is_non_commercial(self, license_name: str) -> bool:
        """检查是否为非商业许可证"""
        non_commercial_keywords = [
            "CC-BY-NC", "CC-NC", "NON-COMMERCIAL", "NC"
        ]
        
        license_upper = license_name.upper()
        return any(keyword in license_upper for keyword in non_commercial_keywords)
    
    def generate_license_report(self, violations: List[LicenseViolation], 
                               conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成许可证报告"""
        # 统计信息
        total_dependencies = len(set(v.package_name for v in violations))
        total_violations = len(violations)
        
        compliance_counts = {}
        for violation in violations:
            compliance = violation.compliance.value
            compliance_counts[compliance] = compliance_counts.get(compliance, 0) + 1
        
        # 许可证分布
        license_distribution = {}
        for violation in violations:
            license_name = violation.license_name
            license_distribution[license_name] = license_distribution.get(license_name, 0) + 1
        
        return {
            "summary": {
                "total_dependencies": total_dependencies,
                "total_violations": total_violations,
                "compliance_distribution": compliance_counts,
                "license_distribution": license_distribution,
                "conflicts_count": len(conflicts)
            },
            "violations": [
                {
                    "package": violation.package_name,
                    "version": violation.package_version,
                    "license": violation.license_name,
                    "compliance": violation.compliance.value,
                    "reason": violation.reason,
                    "recommendations": violation.recommendations
                }
                for violation in violations
            ],
            "conflicts": conflicts,
            "recommendations": self._generate_overall_recommendations(violations, conflicts),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_overall_recommendations(self, violations: List[LicenseViolation], 
                                        conflicts: List[Dict[str, Any]]) -> List[str]:
        """生成整体建议"""
        recommendations = []
        
        # 基于违规类型生成建议
        forbidden_violations = [v for v in violations if v.compliance == LicenseCompliance.FORBIDDEN]
        if forbidden_violations:
            recommendations.append(f"立即处理 {len(forbidden_violations)} 个禁止许可证违规")
        
        warning_violations = [v for v in violations if v.compliance == LicenseCompliance.WARNING]
        if warning_violations:
            recommendations.append(f"评估 {len(warning_violations)} 个警告许可证风险")
        
        unknown_violations = [v for v in violations if v.compliance == LicenseCompliance.UNKNOWN]
        if unknown_violations:
            recommendations.append(f"确认 {len(unknown_violations)} 个未知许可证状态")
        
        # 基于冲突生成建议
        if conflicts:
            recommendations.append("解决许可证冲突问题")
            recommendations.append("考虑使用相同许可证族的依赖")
        
        # 通用建议
        recommendations.append("建立许可证审查流程")
        recommendations.append("定期更新许可证策略")
        recommendations.append("使用自动化工具监控许可证合规性")
        
        return recommendations

class LicenseDatabase:
    def __init__(self):
        self.licenses = self._load_common_licenses()
    
    def _load_common_licenses(self) -> Dict[str, License]:
        """加载常见许可证"""
        return {
            "MIT": License(
                name="MIT License",
                spdx_id="MIT",
                license_type=LicenseType.PERMISSIVE,
                description="宽松的许可证，允许几乎任何使用",
                permissions=["商业使用", "修改", "分发", "私有使用"],
                conditions=["包含许可证和版权声明"],
                limitations=["责任限制", "担保限制"],
                commercial_use=True,
                distribution=True,
                modification=True,
                patent_use=True,
                private_use=True
            ),
            "Apache-2.0": License(
                name="Apache License 2.0",
                spdx_id="Apache-2.0",
                license_type=LicenseType.PERMISSIVE,
                description="宽松的许可证，包含专利授权",
                permissions=["商业使用", "修改", "分发", "专利使用", "私有使用"],
                conditions=["包含许可证和版权声明", "声明修改"],
                limitations=["责任限制", "担保限制", "商标使用"],
                commercial_use=True,
                distribution=True,
                modification=True,
                patent_use=True,
                private_use=True
            ),
            "GPL-3.0": License(
                name="GNU General Public License v3.0",
                spdx_id="GPL-3.0",
                license_type=LicenseType.COPYLEFT,
                description="Copyleft许可证，要求衍生作品也使用GPL",
                permissions=["商业使用", "修改", "分发", "专利使用", "私有使用"],
                conditions=["包含许可证和版权声明", " disclose source", " same license"],
                limitations=["责任限制", "担保限制"],
                commercial_use=True,
                distribution=True,
                modification=True,
                patent_use=True,
                private_use=True
            ),
            "BSD-3-Clause": License(
                name="BSD 3-Clause License",
                spdx_id="BSD-3-Clause",
                license_type=LicenseType.PERMISSIVE,
                description="宽松的许可证，类似MIT但更详细",
                permissions=["商业使用", "修改", "分发", "私有使用"],
                conditions=["包含许可证和版权声明"],
                limitations=["责任限制", "担保限制"],
                commercial_use=True,
                distribution=True,
                modification=True,
                patent_use=False,
                private_use=True
            )
        }
    
    def get_license(self, license_name: str) -> Optional[License]:
        """获取许可证信息"""
        # 直接匹配
        if license_name in self.licenses:
            return self.licenses[license_name]
        
        # 模糊匹配
        for spdx_id, license_info in self.licenses.items():
            if license_name.lower() == spdx_id.lower():
                return license_info
            if license_name.lower() == license_info.name.lower():
                return license_info
        
        return None

# 使用示例
analyzer = LicenseAnalyzer()

# 创建示例依赖
dependencies = [
    Dependency(
        name="react",
        version="16.8.0",
        version_spec="^16.8.0",
        type=DependencyType.DEPENDENCIES,
        license="MIT"
    ),
    Dependency(
        name="some-gpl-package",
        version="1.0.0",
        version_spec="^1.0.0",
        type=DependencyType.DEPENDENCIES,
        license="GPL-3.0"
    )
]

# 分析许可证
violations = analyzer.analyze_licenses(dependencies)

# 检测许可证冲突
conflicts = analyzer.detect_license_conflicts(dependencies)

# 生成报告
license_report = analyzer.generate_license_report(violations, conflicts)

print(f"发现 {len(violations)} 个许可证违规")
print(f"发现 {len(conflicts)} 个许可证冲突")

for violation in violations:
    print(f"违规: {violation.package_name} - {violation.license_name} ({violation.compliance.value})")

for conflict in conflicts:
    print(f"冲突: {conflict['type']} - {conflict['description']}")
```

## 参考资源

### 漏洞数据库
- [OSV.dev](https://osv.dev/)
- [NVD](https://nvd.nist.gov/)
- [GitHub Advisory](https://github.com/advisories)
- [Snyk Vulnerability Database](https://snyk.io/vuln/)

### 许可证信息
- [SPDX License List](https://spdx.org/licenses/)
- [Choose a License](https://choosealicense.com/)
- [Open Source Initiative](https://opensource.org/licenses)
- [FOSSA](https://fossa.com/)

### 包管理器文档
- [npm Documentation](https://docs.npmjs.com/)
- [PyPI Documentation](https://pypi.org/help)
- [Maven Documentation](https://maven.apache.org/)
- [Gradle Documentation](https://gradle.org/guides/)

### 安全工具
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [Snyk](https://snyk.io/)
- [WhiteSource](https://www.whitesourcesoftware.com/)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
