---
name: 包管理器
description: "当管理软件包、处理依赖关系、版本控制、包发布或自动化包管理时，提供完整的包管理和依赖解决方案。"
license: MIT
---

# 包管理器技能

## 概述
包管理器是软件开发中的核心工具，负责自动化安装、配置、升级和移除软件包。它处理依赖关系、版本冲突、安全更新和包发布等复杂任务，是现代软件开发工作流的重要组成部分。

**核心原则**: 依赖管理、版本控制、自动化、安全性、可重现性。

## 何时使用

**始终:**
- 安装项目依赖
- 管理包版本
- 解决依赖冲突
- 发布软件包
- 更新依赖项
- 清理无用包
- 检查安全漏洞
- 创建虚拟环境

**触发短语:**
- "包管理器使用"
- "依赖管理最佳实践"
- "版本控制策略"
- "包发布流程"
- "依赖冲突解决"
- "虚拟环境管理"
- "包安全检查"
- "自动化依赖管理"

## 主流包管理器

### Python生态
- **pip**: Python官方包管理器
- **conda**: 跨平台包和环境管理
- **poetry**: 现代Python依赖管理
- **pipenv**: 虚拟环境和依赖管理

### Node.js生态
- **npm**: Node.js包管理器
- **yarn**: Facebook开发的包管理器
- **pnpm**: 快速、节省磁盘空间的包管理器

### 其他语言
- **Maven**: Java项目管理和构建
- **Gradle**: Groovy-based构建工具
- **Cargo**: Rust包管理器
- **Composer**: PHP依赖管理

## 常见包管理问题

### 依赖冲突
```
问题:
不同包需要同一依赖的不同版本

症状:
- 安装失败
- 版本冲突错误
- 运行时异常
- 构建中断

解决方案:
- 使用依赖解析工具
- 指定兼容版本范围
- 更新到兼容版本
- 使用虚拟环境隔离
- 锁定依赖版本
```

### 版本漂移
```
问题:
依赖版本随时间变化导致不一致

症状:
- 不同环境行为不同
- 生产环境出现问题
- 难以重现bug
- 构建不稳定

解决方案:
- 使用版本锁定文件
- 指定精确版本号
- 定期更新依赖
- 使用CI/CD检查
- 文档化版本策略
```

### 安全漏洞
```
问题:
依赖包存在已知安全漏洞

症状:
- 安全扫描报告
- 潜在攻击风险
- 合规性问题
- 数据泄露风险

解决方案:
- 定期安全扫描
- 及时更新有漏洞的包
- 使用漏洞数据库
- 监控安全公告
- 实施安全策略
```

## 代码实现示例

### 通用包管理器
```python
import os
import json
import subprocess
import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import hashlib
import requests
from datetime import datetime

class PackageManagerType(Enum):
    PIP = "pip"
    NPM = "npm"
    YARN = "yarn"
    CONDA = "conda"
    POETRY = "poetry"
    MAVEN = "maven"
    GRADLE = "gradle"

class DependencyType(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"
    PEER = "peer"

@dataclass
class Package:
    """包信息"""
    name: str
    version: str
    description: str = ""
    homepage: str = ""
    license: str = ""
    dependencies: Dict[str, str] = None
    dev_dependencies: Dict[str, str] = None
    installed_version: Optional[str] = None
    latest_version: Optional[str] = None
    vulnerable: bool = False
    vulnerabilities: List[Dict] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = {}
        if self.dev_dependencies is None:
            self.dev_dependencies = {}
        if self.vulnerabilities is None:
            self.vulnerabilities = []

@dataclass
class DependencyConflict:
    """依赖冲突"""
    package: str
    required_version: str
    conflicting_version: str
    conflict_type: str
    resolution_suggestions: List[str]

class UniversalPackageManager:
    """通用包管理器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.package_manager_type = self._detect_package_manager()
        self.installed_packages: Dict[str, Package] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.conflicts: List[DependencyConflict] = []
        
    def _detect_package_manager(self) -> PackageManagerType:
        """检测项目使用的包管理器"""
        files = list(self.project_path.iterdir())
        
        # Python包管理器检测
        if any(f.name in ['requirements.txt', 'setup.py', 'pyproject.toml'] for f in files):
            if 'poetry.lock' in [f.name for f in files]:
                return PackageManagerType.POETRY
            elif 'environment.yml' in [f.name for f in files]:
                return PackageManagerType.CONDA
            else:
                return PackageManagerType.PIP
        
        # Node.js包管理器检测
        if any(f.name in ['package.json', 'yarn.lock', 'package-lock.json'] for f in files):
            if 'yarn.lock' in [f.name for f in files]:
                return PackageManagerType.YARN
            else:
                return PackageManagerType.NPM
        
        # Java包管理器检测
        if any(f.name in ['pom.xml', 'build.gradle', 'build.gradle.kts'] for f in files):
            if 'pom.xml' in [f.name for f in files]:
                return PackageManagerType.MAVEN
            else:
                return PackageManagerType.GRADLE
        
        return PackageManagerType.PIP  # 默认
    
    def install_package(self, package_name: str, version: str = "",
                        save_type: DependencyType = DependencyType.PRODUCTION,
                        global_install: bool = False) -> bool:
        """安装包"""
        try:
            if self.package_manager_type == PackageManagerType.PIP:
                return self._pip_install(package_name, version, save_type, global_install)
            elif self.package_manager_type == PackageManagerType.NPM:
                return self._npm_install(package_name, version, save_type, global_install)
            elif self.package_manager_type == PackageManagerType.YARN:
                return self._yarn_install(package_name, version, save_type, global_install)
            elif self.package_manager_type == PackageManagerType.POETRY:
                return self._poetry_install(package_name, version, save_type)
            elif self.package_manager_type == PackageManagerType.CONDA:
                return self._conda_install(package_name, version)
            else:
                print(f"暂不支持 {self.package_manager_type.value} 包管理器")
                return False
        except Exception as e:
            print(f"安装包失败: {str(e)}")
            return False
    
    def _pip_install(self, package_name: str, version: str,
                    save_type: DependencyType, global_install: bool) -> bool:
        """使用pip安装包"""
        # 构建包名和版本
        full_package = f"{package_name}=={version}" if version else package_name
        
        # 构建命令
        cmd = ["pip", "install"]
        
        if global_install:
            cmd.append("--global")
        else:
            # 保存到requirements文件
            if save_type == DependencyType.PRODUCTION:
                cmd.extend(["--requirement", "requirements.txt"])
            elif save_type == DependencyType.DEVELOPMENT:
                cmd.extend(["--requirement", "requirements-dev.txt"])
        
        cmd.append(full_package)
        
        # 执行安装
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        
        if result.returncode == 0:
            # 更新requirements文件
            if not global_install and save_type != DependencyType.OPTIONAL:
                self._update_requirements_txt(package_name, version, save_type)
            return True
        else:
            print(f"pip安装失败: {result.stderr}")
            return False
    
    def _npm_install(self, package_name: str, version: str,
                    save_type: DependencyType, global_install: bool) -> bool:
        """使用npm安装包"""
        cmd = ["npm", "install"]
        
        if global_install:
            cmd.append("--global")
        else:
            if save_type == DependencyType.PRODUCTION:
                cmd.append("--save")
            elif save_type == DependencyType.DEVELOPMENT:
                cmd.append("--save-dev")
            elif save_type == DependencyType.OPTIONAL:
                cmd.append("--save-optional")
        
        full_package = f"{package_name}@{version}" if version else package_name
        cmd.append(full_package)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        
        return result.returncode == 0
    
    def _yarn_install(self, package_name: str, version: str,
                     save_type: DependencyType, global_install: bool) -> bool:
        """使用yarn安装包"""
        cmd = ["yarn", "add"]
        
        if global_install:
            cmd.append("--global")
        else:
            if save_type == DependencyType.DEVELOPMENT:
                cmd.append("--dev")
            elif save_type == DependencyType.OPTIONAL:
                cmd.append("--optional")
            elif save_type == DependencyType.PEER:
                cmd.append("--peer")
        
        full_package = f"{package_name}@{version}" if version else package_name
        cmd.append(full_package)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        
        return result.returncode == 0
    
    def _poetry_install(self, package_name: str, version: str,
                       save_type: DependencyType) -> bool:
        """使用poetry安装包"""
        cmd = ["poetry", "add"]
        
        if save_type == DependencyType.DEVELOPMENT:
            cmd.append("--group=dev")
        
        full_package = f"{package_name}=={version}" if version else package_name
        cmd.append(full_package)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        
        return result.returncode == 0
    
    def _conda_install(self, package_name: str, version: str) -> bool:
        """使用conda安装包"""
        cmd = ["conda", "install", "-y"]
        
        if version:
            full_package = f"{package_name}={version}"
        else:
            full_package = package_name
        
        cmd.append(full_package)
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        
        return result.returncode == 0
    
    def uninstall_package(self, package_name: str, global_install: bool = False) -> bool:
        """卸载包"""
        try:
            if self.package_manager_type == PackageManagerType.PIP:
                cmd = ["pip", "uninstall", "-y", package_name]
                if global_install:
                    cmd.append("--global")
            elif self.package_manager_type == PackageManagerType.NPM:
                cmd = ["npm", "uninstall", package_name]
                if global_install:
                    cmd.append("--global")
            elif self.package_manager_type == PackageManagerType.YARN:
                cmd = ["yarn", "remove", package_name]
                if global_install:
                    cmd.append("--global")
            elif self.package_manager_type == PackageManagerType.POETRY:
                cmd = ["poetry", "remove", package_name]
            elif self.package_manager_type == PackageManagerType.CONDA:
                cmd = ["conda", "remove", "-y", package_name]
            else:
                return False
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
            return result.returncode == 0
        except Exception as e:
            print(f"卸载包失败: {str(e)}")
            return False
    
    def update_package(self, package_name: str = "", check_only: bool = False) -> bool:
        """更新包"""
        try:
            if self.package_manager_type == PackageManagerType.PIP:
                if package_name:
                    cmd = ["pip", "install", "--upgrade", package_name]
                else:
                    cmd = ["pip", "list", "--outdated"] if check_only else ["pip", "install", "--upgrade"]
            elif self.package_manager_type == PackageManagerType.NPM:
                cmd = ["npm", "update"] if not check_only else ["npm", "outdated"]
            elif self.package_manager_type == PackageManagerType.YARN:
                cmd = ["yarn", "upgrade"] if not check_only else ["yarn", "outdated"]
            elif self.package_manager_type == PackageManagerType.POETRY:
                cmd = ["poetry", "update"] if not check_only else ["poetry", "show", "--outdated"]
            elif self.package_manager_type == PackageManagerType.CONDA:
                cmd = ["conda", "update", "--all"] if not check_only else ["conda", "update", "--dry-run", "--all"]
            else:
                return False
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
            
            if check_only:
                print("过时包列表:")
                print(result.stdout)
            
            return result.returncode == 0
        except Exception as e:
            print(f"更新包失败: {str(e)}")
            return False
    
    def list_installed_packages(self, global_install: bool = False) -> Dict[str, Package]:
        """列出已安装的包"""
        try:
            if self.package_manager_type == PackageManagerType.PIP:
                return self._pip_list(global_install)
            elif self.package_manager_type == PackageManagerType.NPM:
                return self._npm_list(global_install)
            elif self.package_manager_type == PackageManagerType.YARN:
                return self._yarn_list(global_install)
            elif self.package_manager_type == PackageManagerType.POETRY:
                return self._poetry_list()
            elif self.package_manager_type == PackageManagerType.CONDA:
                return self._conda_list()
            else:
                return {}
        except Exception as e:
            print(f"列出包失败: {str(e)}")
            return {}
    
    def _pip_list(self, global_install: bool) -> Dict[str, Package]:
        """使用pip列出包"""
        cmd = ["pip", "list", "--format=json"]
        if global_install:
            cmd.append("--global")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            packages_data = json.loads(result.stdout)
            packages = {}
            
            for pkg_data in packages_data:
                package = Package(
                    name=pkg_data['name'],
                    version=pkg_data['version'],
                    installed_version=pkg_data['version']
                )
                packages[pkg_data['name']] = package
            
            return packages
        
        return {}
    
    def _npm_list(self, global_install: bool) -> Dict[str, Package]:
        """使用npm列出包"""
        cmd = ["npm", "list", "--json", "--depth=0"]
        if global_install:
            cmd.append("--global")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            packages = {}
            
            if 'dependencies' in data:
                for name, info in data['dependencies'].items():
                    package = Package(
                        name=name,
                        version=info.get('version', 'unknown'),
                        installed_version=info.get('version', 'unknown')
                    )
                    packages[name] = package
            
            return packages
        
        return {}
    
    def check_vulnerabilities(self) -> List[Dict]:
        """检查安全漏洞"""
        try:
            if self.package_manager_type == PackageManagerType.NPM:
                cmd = ["npm", "audit", "--json"]
            elif self.package_manager_type == PackageManagerType.YARN:
                cmd = ["yarn", "audit", "--json"]
            elif self.package_manager_type == PackageManagerType.POETRY:
                cmd = ["poetry", "audit"]
            else:
                # pip使用safety检查
                cmd = ["safety", "check", "--json"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
            
            if result.returncode == 0:
                if self.package_manager_type in [PackageManagerType.NPM, PackageManagerType.YARN]:
                    data = json.loads(result.stdout)
                    return data.get('vulnerabilities', [])
                else:
                    # safety输出格式不同
                    return []
            else:
                return []
        except Exception as e:
            print(f"检查漏洞失败: {str(e)}")
            return []
    
    def resolve_conflicts(self) -> List[DependencyConflict]:
        """解决依赖冲突"""
        conflicts = []
        
        # 获取依赖图
        self._build_dependency_graph()
        
        # 检测版本冲突
        for package, dependents in self.dependency_graph.items():
            versions = set()
            
            for dependent in dependents:
                # 简化版本检测逻辑
                pkg_info = self.installed_packages.get(dependent)
                if pkg_info and package in pkg_info.dependencies:
                    versions.add(pkg_info.dependencies[package])
            
            if len(versions) > 1:
                conflict = DependencyConflict(
                    package=package,
                    required_version=list(versions)[0],
                    conflicting_version=list(versions)[1],
                    conflict_type="version_conflict",
                    resolution_suggestions=[
                        f"统一{package}版本到最新兼容版本",
                        f"使用包管理器的冲突解决功能",
                        f"考虑升级或降级相关依赖"
                    ]
                )
                conflicts.append(conflict)
        
        self.conflicts = conflicts
        return conflicts
    
    def _build_dependency_graph(self):
        """构建依赖图"""
        self.dependency_graph.clear()
        
        for name, package in self.installed_packages.items():
            for dep_name, dep_version in package.dependencies.items():
                if dep_name not in self.dependency_graph:
                    self.dependency_graph[dep_name] = []
                self.dependency_graph[dep_name].append(name)
    
    def generate_lock_file(self) -> bool:
        """生成锁定文件"""
        try:
            if self.package_manager_type == PackageManagerType.NPM:
                cmd = ["npm", "install", "--package-lock-only"]
            elif self.package_manager_type == PackageManagerType.YARN:
                cmd = ["yarn", "install", "--frozen-lockfile"]
            elif self.package_manager_type == PackageManagerType.POETRY:
                cmd = ["poetry", "lock"]
            elif self.package_manager_type == PackageManagerType.PIP:
                cmd = ["pip", "freeze", "> requirements.txt"]
            else:
                return False
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
            return result.returncode == 0
        except Exception as e:
            print(f"生成锁定文件失败: {str(e)}")
            return False
    
    def clean_packages(self, dry_run: bool = True) -> List[str]:
        """清理无用包"""
        removed_packages = []
        
        try:
            if self.package_manager_type == PackageManagerType.PIP:
                cmd = ["pip", "autoremove"]
                if dry_run:
                    cmd.append("--dry-run")
            elif self.package_manager_type == PackageManagerType.NPM:
                cmd = ["npm", "prune"]
                if dry_run:
                    cmd.append("--dry-run")
            elif self.package_manager_type == PackageManagerType.YARN:
                cmd = ["yarn", "autoclean"]
                if dry_run:
                    cmd.append("--dry-run")
            else:
                return removed_packages
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
            
            if result.returncode == 0:
                # 解析输出获取移除的包列表
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'would remove' in line.lower() or 'removed' in line.lower():
                        # 简化解析，实际应该更精确
                        removed_packages.append(line.strip())
            
            return removed_packages
        except Exception as e:
            print(f"清理包失败: {str(e)}")
            return removed_packages
    
    def _update_requirements_txt(self, package_name: str, version: str,
                                 save_type: DependencyType):
        """更新requirements.txt文件"""
        if save_type == DependencyType.DEVELOPMENT:
            filename = "requirements-dev.txt"
        else:
            filename = "requirements.txt"
        
        filepath = self.project_path / filename
        
        # 读取现有内容
        existing_lines = []
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing_lines = f.readlines()
        
        # 检查包是否已存在
        package_line = f"{package_name}=={version}" if version else package_name
        package_exists = False
        
        for i, line in enumerate(existing_lines):
            if line.strip().startswith(package_name):
                existing_lines[i] = f"{package_line}\n"
                package_exists = True
                break
        
        # 如果不存在，添加新行
        if not package_exists:
            existing_lines.append(f"{package_line}\n")
        
        # 写回文件
        with open(filepath, 'w') as f:
            f.writelines(existing_lines)
    
    def export_dependencies(self, format_type: str = "json") -> str:
        """导出依赖信息"""
        packages_data = {}
        
        for name, package in self.installed_packages.items():
            packages_data[name] = {
                'version': package.version,
                'installed_version': package.installed_version,
                'dependencies': package.dependencies,
                'description': package.description,
                'license': package.license
            }
        
        if format_type.lower() == "json":
            return json.dumps(packages_data, indent=2, ensure_ascii=False)
        elif format_type.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Name', 'Version', 'Description', 'License'])
            
            for name, package in self.installed_packages.items():
                writer.writerow([name, package.version, package.description, package.license])
            
            return output.getvalue()
        else:
            return str(packages_data)
    
    def create_virtual_environment(self, env_name: str = "venv",
                                 python_version: str = "") -> bool:
        """创建虚拟环境"""
        try:
            if self.package_manager_type in [PackageManagerType.PIP, PackageManagerType.POETRY]:
                # 使用venv创建虚拟环境
                cmd = ["python", "-m", "venv", env_name]
                if python_version:
                    cmd = [f"python{python_version}", "-m", "venv", env_name]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
                
                if result.returncode == 0:
                    print(f"虚拟环境 {env_name} 创建成功")
                    print(f"激活命令: source {env_name}/bin/activate")
                    return True
                else:
                    print(f"创建虚拟环境失败: {result.stderr}")
                    return False
            
            elif self.package_manager_type == PackageManagerType.CONDA:
                # 使用conda创建环境
                cmd = ["conda", "create", "-n", env_name, "python"]
                if python_version:
                    cmd[-1] = f"python={python_version}"
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
            
            else:
                print("当前包管理器不支持虚拟环境创建")
                return False
        except Exception as e:
            print(f"创建虚拟环境失败: {str(e)}")
            return False

# 使用示例
def main():
    """示例使用"""
    print("📦 通用包管理器启动")
    print("=" * 50)
    
    # 创建包管理器实例
    pm = UniversalPackageManager(".")
    
    print(f"检测到包管理器: {pm.package_manager_type.value}")
    
    # 列出已安装的包
    print("\n📋 已安装的包:")
    packages = pm.list_installed_packages()
    
    for name, package in list(packages.items())[:5]:  # 只显示前5个
        print(f"  - {name}: {package.installed_version}")
    
    if len(packages) > 5:
        print(f"  ... 还有 {len(packages) - 5} 个包")
    
    # 检查安全漏洞
    print("\n🔒 检查安全漏洞:")
    vulnerabilities = pm.check_vulnerabilities()
    if vulnerabilities:
        print(f"发现 {len(vulnerabilities)} 个安全漏洞")
        for vuln in vulnerabilities[:3]:  # 显示前3个
            print(f"  - {vuln.get('name', 'Unknown')}: {vuln.get('severity', 'Unknown')}")
    else:
        print("✅ 未发现安全漏洞")
    
    # 检查依赖冲突
    print("\n⚠️  检查依赖冲突:")
    conflicts = pm.resolve_conflicts()
    if conflicts:
        print(f"发现 {len(conflicts)} 个依赖冲突")
        for conflict in conflicts[:3]:  # 显示前3个
            print(f"  - {conflict.package}: {conflict.conflict_type}")
    else:
        print("✅ 未发现依赖冲突")
    
    # 演示包安装（模拟）
    print("\n📥 演示包安装:")
    print("  - 安装 requests 包...")
    # success = pm.install_package("requests", "2.28.1")
    # print(f"    {'✅ 成功' if success else '❌ 失败'}")
    print("    (演示模式，未实际安装)")
    
    # 生成锁定文件
    print("\n🔒 生成锁定文件:")
    # success = pm.generate_lock_file()
    # print(f"  {'✅ 成功' if success else '❌ 失败'}")
    print("  (演示模式，未实际生成)")
    
    # 导出依赖信息
    print("\n📤 导出依赖信息:")
    dependencies_json = pm.export_dependencies("json")
    print(f"  导出了 {len(packages)} 个包的依赖信息")
    
    # 创建虚拟环境
    print("\n🐍 创建虚拟环境:")
    # success = pm.create_virtual_environment("demo-env")
    # print(f"  {'✅ 成功' if success else '❌ 失败'}")
    print("  (演示模式，未实际创建)")
    
    print("\n✅ 包管理器演示完成!")

if __name__ == "__main__":
    main()
```

### 依赖分析器
```python
class DependencyAnalyzer:
    """依赖分析器"""
    
    def __init__(self):
        self.dependency_tree = {}
        self.circular_dependencies = []
        self.unused_packages = []
        self.missing_dependencies = []
    
    def analyze_dependency_tree(self, package_manager: UniversalPackageManager) -> Dict:
        """分析依赖树"""
        packages = package_manager.installed_packages
        
        # 构建依赖树
        tree = {}
        for name, package in packages.items():
            tree[name] = {
                'version': package.version,
                'dependencies': package.dependencies,
                'dependents': [],
                'depth': 0
            }
        
        # 计算依赖深度
        self._calculate_dependency_depth(tree)
        
        # 查找循环依赖
        self._find_circular_dependencies(tree)
        
        return {
            'tree': tree,
            'circular_dependencies': self.circular_dependencies,
            'statistics': self._calculate_tree_statistics(tree)
        }
    
    def _calculate_dependency_depth(self, tree: Dict):
        """计算依赖深度"""
        def dfs(package_name: str, visited: set = None) -> int:
            if visited is None:
                visited = set()
            
            if package_name in visited:
                return 0  # 循环依赖
            
            visited.add(package_name)
            
            package = tree.get(package_name, {})
            dependencies = package.get('dependencies', {})
            
            max_depth = 0
            for dep_name in dependencies:
                depth = dfs(dep_name, visited.copy())
                max_depth = max(max_depth, depth + 1)
            
            tree[package_name]['depth'] = max_depth
            return max_depth
        
        for package_name in tree:
            dfs(package_name)
    
    def _find_circular_dependencies(self, tree: Dict):
        """查找循环依赖"""
        visited = set()
        rec_stack = set()
        
        def dfs(package_name: str, path: list):
            if package_name in rec_stack:
                # 找到循环依赖
                cycle_start = path.index(package_name)
                cycle = path[cycle_start:] + [package_name]
                self.circular_dependencies.append(cycle)
                return
            
            if package_name in visited:
                return
            
            visited.add(package_name)
            rec_stack.add(package_name)
            
            package = tree.get(package_name, {})
            dependencies = package.get('dependencies', {})
            
            for dep_name in dependencies:
                dfs(dep_name, path + [package_name])
            
            rec_stack.remove(package_name)
        
        for package_name in tree:
            dfs(package_name, [])
    
    def _calculate_tree_statistics(self, tree: Dict) -> Dict:
        """计算树统计信息"""
        total_packages = len(tree)
        
        depths = [pkg['depth'] for pkg in tree.values()]
        max_depth = max(depths) if depths else 0
        avg_depth = sum(depths) / len(depths) if depths else 0
        
        dependency_counts = [len(pkg['dependencies']) for pkg in tree.values()]
        max_dependencies = max(dependency_counts) if dependency_counts else 0
        avg_dependencies = sum(dependency_counts) / len(dependency_counts) if dependency_counts else 0
        
        return {
            'total_packages': total_packages,
            'max_depth': max_depth,
            'average_depth': avg_depth,
            'max_dependencies': max_dependencies,
            'average_dependencies': avg_dependencies,
            'circular_dependencies_count': len(self.circular_dependencies)
        }

# 使用示例
def main():
    analyzer = DependencyAnalyzer()
    print("依赖分析器已准备就绪!")

if __name__ == "__main__":
    main()
```

## 包管理最佳实践

### 依赖管理
1. **版本锁定**: 使用锁定文件确保一致性
2. **语义化版本**: 遵循语义化版本规范
3. **最小依赖**: 只安装必要的包
4. **定期更新**: 及时更新到安全版本

### 安全管理
1. **定期扫描**: 使用工具检查安全漏洞
2. **及时更新**: 快速修复已知漏洞
3. **权限控制**: 使用最小权限原则
4. **审计日志**: 记录包管理操作

### 环境管理
1. **虚拟隔离**: 使用虚拟环境隔离依赖
2. **环境一致性**: 确保开发、测试、生产环境一致
3. **容器化**: 使用容器管理环境
4. **文档化**: 记录环境配置

## 包管理工具推荐

### Python工具
- **pip**: 官方包管理器
- **poetry**: 现代依赖管理
- **conda**: 科学计算环境管理
- **pipenv**: 虚拟环境和依赖管理

### Node.js工具
- **npm**: 官方包管理器
- **yarn**: 快速可靠的包管理
- **pnpm**: 节省空间的包管理
- **npx**: 包执行器

### 通用工具
- **Dependabot**: 自动依赖更新
- **Snyk**: 安全漏洞扫描
- **Renovate**: 自动依赖更新
- **WhiteSource**: 开源组件管理

## 相关技能

- **dependency-management** - 依赖管理
- **virtual-environment** - 虚拟环境
- **security-scanning** - 安全扫描
- **version-control** - 版本控制
- **continuous-integration** - 持续集成
- **package-publishing** - 包发布
