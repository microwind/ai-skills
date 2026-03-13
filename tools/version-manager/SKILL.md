---
name: 版本管理器
description: "当管理版本时，分析版本号，优化发布流程，解决依赖冲突。验证版本规范，设计发布策略，和最佳实践。"
license: MIT
---

# 版本管理器技能

## 概述

版本管理是软件开发生命周期的重要组成部分，合理的版本策略能够清晰传达变更内容、管理依赖关系、支持向后兼容。不当的版本管理会导致用户困惑、依赖冲突、升级困难。

**核心原则**: 好的版本管理应该语义清晰、向后兼容、自动化程度高、发布流程规范。坏的版本管理会导致版本混乱、依赖地狱、升级风险。

## 何时使用

**始终:**
- 发布新版本时
- 规划破坏性变更时
- 确定发布类型时
- 更新依赖时
- 沟通变更时
- 版本回滚时

**触发短语:**
- "这个版本号正确吗？"
- "下一个版本是什么？"
- "检查semver"
- "验证版本"
- "版本发布策略"
- "依赖版本冲突"

## 版本管理器技能功能

### 版本号管理
- 语义化版本(SemVer)
- 版本号验证
- 版本比较
- 版本范围解析
- 预发布版本
- 构建元数据

### 发布策略
- 自动版本递增
- 变更日志生成
- 发布标签管理
- 版本回滚
- 分支策略
- 发布流程

### 依赖管理
- 版本冲突检测
- 依赖更新策略
- 安全漏洞检查
- 兼容性分析
- 锁定文件管理
- 传递依赖分析

### 自动化流程
- CI/CD集成
- 自动发布
- 版本检查
- 发布验证
- 回滚机制
- 监控告警

## 常见问题

**❌ 版本号不规范**
- 不遵循语义化版本
- 版本号格式错误
- 缺少版本信息
- 预发布版本混乱

**❌ 发布流程混乱**
- 缺少发布计划
- 变更日志缺失
- 发布验证不足
- 回滚机制缺失

**❌ 依赖管理问题**
- 版本冲突频繁
- 依赖更新滞后
- 安全漏洞未修复
- 兼容性问题

**❌ 沟通不足**
- 变更内容不清晰
- 影响范围未说明
- 升级指南缺失
- 用户通知不及时

## 代码示例

### 语义化版本管理

```python
#!/usr/bin/env python3
import re
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

class VersionPart(Enum):
    """版本部分"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"
    BUILD = "build"

@dataclass
class SemanticVersion:
    """语义化版本"""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    @classmethod
    def parse(cls, version_string: str) -> 'SemanticVersion':
        """解析版本字符串"""
        # 语义化版本正则表达式
        pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        
        match = re.match(pattern, version_string)
        if not match:
            raise ValueError(f"无效的语义化版本: {version_string}")
        
        major = int(match.group(1))
        minor = int(match.group(2))
        patch = int(match.group(3))
        prerelease = match.group(4)
        build = match.group(5)
        
        return cls(major, minor, patch, prerelease, build)
    
    def bump(self, part: VersionPart) -> 'SemanticVersion':
        """版本递增"""
        if part == VersionPart.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        elif part == VersionPart.MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        elif part == VersionPart.PATCH:
            return SemanticVersion(self.major, self.minor, self.patch + 1)
        elif part == VersionPart.PRERELEASE:
            # 预发布版本逻辑
            if self.prerelease:
                # 解析预发布版本号
                prerelease_parts = self.prerelease.split('.')
                if prerelease_parts[-1].isdigit():
                    # 数字递增
                    prerelease_parts[-1] = str(int(prerelease_parts[-1]) + 1)
                    new_prerelease = '.'.join(prerelease_parts)
                else:
                    # 添加数字后缀
                    new_prerelease = f"{self.prerelease}.1"
            else:
                # 新的预发布版本
                new_prerelease = "alpha.1"
            
            return SemanticVersion(self.major, self.minor, self.patch, new_prerelease, self.build)
        else:
            raise ValueError(f"不支持的版本部分: {part}")
    
    def is_prerelease(self) -> bool:
        """是否为预发布版本"""
        return self.prerelease is not None
    
    def is_compatible_with(self, other: 'SemanticVersion') -> bool:
        """检查兼容性（^版本范围）"""
        if self.major != other.major:
            return False
        if self.minor > other.minor:
            return False
        if self.minor == other.minor and self.patch > other.patch:
            return False
        return True
    
    def compare(self, other: 'SemanticVersion') -> int:
        """版本比较"""
        # 比较主版本
        if self.major != other.major:
            return 1 if self.major > other.major else -1
        
        # 比较次版本
        if self.minor != other.minor:
            return 1 if self.minor > other.minor else -1
        
        # 比较修订版本
        if self.patch != other.patch:
            return 1 if self.patch > other.patch else -1
        
        # 比较预发布版本
        if self.prerelease is None and other.prerelease is None:
            return 0
        elif self.prerelease is None:
            return 1  # 正式版本 > 预发布版本
        elif other.prerelease is None:
            return -1  # 预发布版本 < 正式版本
        else:
            return self._compare_prerelease(self.prerelease, other.prerelease)
    
    def _compare_prerelease(self, prerelease1: str, prerelease2: str) -> int:
        """比较预发布版本"""
        parts1 = prerelease1.split('.')
        parts2 = prerelease2.split('.')
        
        # 逐个比较
        for p1, p2 in zip(parts1, parts2):
            # 数字比较
            if p1.isdigit() and p2.isdigit():
                n1, n2 = int(p1), int(p2)
                if n1 != n2:
                    return 1 if n1 > n2 else -1
            # 字符串比较
            elif p1.isdigit():
                return -1  # 数字 < 字符串
            elif p2.isdigit():
                return 1   # 字符串 > 数字
            else:
                if p1 != p2:
                    return 1 if p1 > p2 else -1
        
        # 长度比较
        if len(parts1) != len(parts2):
            return 1 if len(parts1) > len(parts2) else -1
        
        return 0

class VersionManager:
    """版本管理器"""
    
    def __init__(self):
        self.current_version: Optional[SemanticVersion] = None
        self.version_history: List[SemanticVersion] = []
    
    def load_version(self, version_string: str) -> None:
        """加载当前版本"""
        self.current_version = SemanticVersion.parse(version_string)
        self.version_history.append(self.current_version)
    
    def bump_version(self, part: VersionPart, prerelease_type: Optional[str] = None) -> SemanticVersion:
        """递增版本"""
        if not self.current_version:
            raise ValueError("未加载当前版本")
        
        new_version = self.current_version.bump(part)
        
        # 处理预发布版本类型
        if part == VersionPart.PRERELEASE and prerelease_type:
            if prerelease_type in ['alpha', 'beta', 'rc']:
                new_version.prerelease = f"{prerelease_type}.1"
            else:
                raise ValueError(f"不支持的预发布类型: {prerelease_type}")
        
        self.current_version = new_version
        self.version_history.append(new_version)
        
        return new_version
    
    def validate_version(self, version_string: str) -> bool:
        """验证版本格式"""
        try:
            SemanticVersion.parse(version_string)
            return True
        except ValueError:
            return False
    
    def get_version_range(self, range_string: str) -> List[SemanticVersion]:
        """解析版本范围"""
        # 支持的版本范围格式
        # ^1.2.3, ~1.2.3, >=1.2.3, <=1.2.3, >1.2.3, <1.2.3
        # 1.2.3 - 1.5.0, 1.2.3 || 1.3.0
        
        versions = []
        
        # 解析不同的范围格式
        if range_string.startswith('^'):
            # 兼容版本范围
            base_version = SemanticVersion.parse(range_string[1:])
            for version in self.version_history:
                if version.is_compatible_with(base_version) and version >= base_version:
                    versions.append(version)
        
        elif range_string.startswith('~'):
            # 波浪版本范围
            base_version = SemanticVersion.parse(range_string[1:])
            for version in self.version_history:
                if (version.major == base_version.major and 
                    version.minor == base_version.minor and 
                    version >= base_version):
                    versions.append(version)
        
        elif range_string.startswith('>='):
            # 大于等于
            min_version = SemanticVersion.parse(range_string[2:])
            versions = [v for v in self.version_history if v >= min_version]
        
        elif range_string.startswith('<='):
            # 小于等于
            max_version = SemanticVersion.parse(range_string[2:])
            versions = [v for v in self.version_history if v <= max_version]
        
        elif range_string.startswith('>'):
            # 大于
            min_version = SemanticVersion.parse(range_string[1:])
            versions = [v for v in self.version_history if v > min_version]
        
        elif range_string.startswith('<'):
            # 小于
            max_version = SemanticVersion.parse(range_string[1:])
            versions = [v for v in self.version_history if v < max_version]
        
        elif ' - ' in range_string:
            # 范围版本
            min_str, max_str = range_string.split(' - ')
            min_version = SemanticVersion.parse(min_str.strip())
            max_version = SemanticVersion.parse(max_str.strip())
            versions = [v for v in self.version_history if min_version <= v <= max_version]
        
        elif ' || ' in range_string:
            # 或条件
            for part in range_string.split(' || '):
                versions.extend(self.get_version_range(part.strip()))
        
        else:
            # 精确版本
            try:
                exact_version = SemanticVersion.parse(range_string)
                if exact_version in self.version_history:
                    versions.append(exact_version)
            except ValueError:
                pass
        
        return sorted(set(versions), key=lambda v: (v.major, v.minor, v.patch))
    
    def suggest_next_version(self, changes: List[str]) -> SemanticVersion:
        """建议下一个版本"""
        if not self.current_version:
            raise ValueError("未加载当前版本")
        
        # 分析变更类型
        has_breaking = any('breaking' in change.lower() or '!' in change for change in changes)
        has_features = any('feat' in change.lower() for change in changes)
        has_fixes = any('fix' in change.lower() for change in changes)
        
        if has_breaking:
            return self.current_version.bump(VersionPart.MAJOR)
        elif has_features:
            return self.current_version.bump(VersionPart.MINOR)
        elif has_fixes:
            return self.current_version.bump(VersionPart.PATCH)
        else:
            return self.current_version.bump(VersionPart.PATCH)

# 使用示例
if __name__ == "__main__":
    manager = VersionManager()
    
    # 加载当前版本
    manager.load_version("1.2.3")
    print(f"当前版本: {manager.current_version}")
    
    # 版本递增
    patch_version = manager.bump_version(VersionPart.PATCH)
    print(f"补丁版本: {patch_version}")
    
    minor_version = manager.bump_version(VersionPart.MINOR)
    print(f"次版本: {minor_version}")
    
    major_version = manager.bump_version(VersionPart.MAJOR)
    print(f"主版本: {major_version}")
    
    # 预发布版本
    alpha_version = manager.bump_version(VersionPart.PRERELEASE, "alpha")
    print(f"Alpha版本: {alpha_version}")
    
    # 版本比较
    v1 = SemanticVersion.parse("1.2.3")
    v2 = SemanticVersion.parse("1.2.4")
    print(f"版本比较: {v1} vs {v2} = {v1.compare(v2)}")
    
    # 版本范围
    versions = manager.get_version_range("^1.2.0")
    print(f"兼容版本: {[str(v) for v in versions]}")
```

### 自动化版本发布

```bash
#!/bin/bash
# version-release.sh - 自动化版本发布脚本

set -e

# 配置
PROJECT_NAME="myapp"
VERSION_FILE="version.txt"
CHANGELOG_FILE="CHANGELOG.md"
GIT_REMOTE="origin"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 获取当前版本
get_current_version() {
    if [ -f "$VERSION_FILE" ]; then
        cat "$VERSION_FILE"
    else
        log_error "版本文件不存在: $VERSION_FILE"
        exit 1
    fi
}

# 验证版本格式
validate_version() {
    local version=$1
    # 语义化版本正则表达式
    if [[ ! $version =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$ ]]; then
        log_error "无效的版本格式: $version"
        exit 1
    fi
}

# 递增版本
bump_version() {
    local current_version=$1
    local bump_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    major=${VERSION_PARTS[0]}
    minor=${VERSION_PARTS[1]}
    patch=${VERSION_PARTS[2]}
    
    case $bump_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            log_error "不支持的版本递增类型: $bump_type"
            exit 1
            ;;
    esac
    
    echo "${major}.${minor}.${patch}"
}

# 生成变更日志
generate_changelog() {
    local current_version=$1
    local new_version=$2
    
    log_step "生成变更日志..."
    
    # 获取上一个版本标签
    local previous_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    
    # 生成变更日志内容
    local changelog_content="# 更新日志\n\n"
    
    if [ -n "$previous_tag" ]; then
        changelog_content+="## [$new_version] - $(date +%Y-%m-%d)\n\n"
        
        # 获取提交信息
        local commits=$(git log --pretty=format:"- %s (%h)" $previous_tag..HEAD)
        
        if [ -n "$commits" ]; then
            # 分类提交
            local features=$(echo "$commits" | grep -i "feat\|feature" || true)
            local fixes=$(echo "$commits" | grep -i "fix\|bug" || true)
            local breaking=$(echo "$commits" | grep -i "breaking\|!" || true)
            local others=$(echo "$commits" | grep -iv "feat\|feature\|fix\|bug\|breaking\|!" || true)
            
            if [ -n "$features" ]; then
                changelog_content+="### 新功能\n\n$features\n\n"
            fi
            
            if [ -n "$fixes" ]; then
                changelog_content+="### 修复\n\n$fixes\n\n"
            fi
            
            if [ -n "$breaking" ]; then
                changelog_content+="### 破坏性变更\n\n$breaking\n\n"
            fi
            
            if [ -n "$others" ]; then
                changelog_content+="### 其他\n\n$others\n\n"
            fi
        fi
    else
        changelog_content+="## [$new_version] - $(date +%Y-%m-%d)\n\n"
        changelog_content+="### 初始发布\n\n"
    fi
    
    # 更新变更日志文件
    if [ -f "$CHANGELOG_FILE" ]; then
        # 保留现有内容，添加新版本
        temp_file=$(mktemp)
        echo -e "$changelog_content" > "$temp_file"
        tail -n +2 "$CHANGELOG_FILE" >> "$temp_file"
        mv "$temp_file" "$CHANGELOG_FILE"
    else
        echo -e "$changelog_content" > "$CHANGELOG_FILE"
    fi
    
    log_info "变更日志已更新: $CHANGELOG_FILE"
}

# 运行测试
run_tests() {
    log_step "运行测试..."
    
    # 根据项目类型运行不同的测试
    if [ -f "package.json" ]; then
        npm test
    elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        python -m pytest
    elif [ -f "pom.xml" ]; then
        mvn test
    elif [ -f "build.gradle" ]; then
        ./gradlew test
    else
        log_warn "未找到测试配置，跳过测试"
    fi
    
    log_info "测试通过"
}

# 构建项目
build_project() {
    log_step "构建项目..."
    
    # 根据项目类型运行不同的构建
    if [ -f "package.json" ]; then
        npm run build
    elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        python -m build
    elif [ -f "pom.xml" ]; then
        mvn package
    elif [ -f "build.gradle" ]; then
        ./gradlew build
    else
        log_warn "未找到构建配置，跳过构建"
    fi
    
    log_info "构建完成"
}

# 创建Git标签
create_tag() {
    local version=$1
    
    log_step "创建Git标签..."
    
    # 创建标签
    git tag -a "v$version" -m "Release version $version"
    
    # 推送标签
    git push $GIT_REMOTE "v$version"
    
    log_info "标签已创建并推送: v$version"
}

# 发布到仓库
publish_to_registry() {
    log_step "发布到仓库..."
    
    # 根据项目类型发布到不同的仓库
    if [ -f "package.json" ]; then
        npm publish
    elif [ -f "pyproject.toml" ]; then
        python -m twine upload dist/*
    elif [ -f "pom.xml" ]; then
        mvn deploy
    else
        log_warn "未找到发布配置，跳过发布"
    fi
    
    log_info "发布完成"
}

# 更新版本文件
update_version_file() {
    local new_version=$1
    
    echo "$new_version" > "$VERSION_FILE"
    log_info "版本文件已更新: $new_version"
}

# 主函数
main() {
    local bump_type=${1:-patch}
    local skip_tests=${2:-false}
    local skip_build=${3:-false}
    local skip_publish=${4:-false}
    
    log_info "开始版本发布流程..."
    
    # 检查工作目录是否干净
    if [ -n "$(git status --porcelain)" ]; then
        log_error "工作目录不干净，请先提交或暂存更改"
        exit 1
    fi
    
    # 获取当前版本
    local current_version=$(get_current_version)
    log_info "当前版本: $current_version"
    
    # 验证当前版本
    validate_version "$current_version"
    
    # 递增版本
    local new_version=$(bump_version "$current_version" "$bump_type")
    log_info "新版本: $new_version"
    
    # 更新版本文件
    update_version_file "$new_version"
    
    # 提交版本文件
    git add "$VERSION_FILE"
    git commit -m "chore: bump version to $new_version"
    
    # 运行测试
    if [ "$skip_tests" != "true" ]; then
        run_tests
    else
        log_warn "跳过测试"
    fi
    
    # 构建项目
    if [ "$skip_build" != "true" ]; then
        build_project
    else
        log_warn "跳过构建"
    fi
    
    # 生成变更日志
    generate_changelog "$current_version" "$new_version"
    
    # 提交变更日志
    git add "$CHANGELOG_FILE"
    git commit -m "docs: update changelog for $new_version"
    
    # 推送更改
    git push $GIT_REMOTE main
    
    # 创建标签
    create_tag "$new_version"
    
    # 发布到仓库
    if [ "$skip_publish" != "true" ]; then
        publish_to_registry
    else
        log_warn "跳过发布"
    fi
    
    log_info "版本发布完成: $new_version"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [bump_type] [skip_tests] [skip_build] [skip_publish]"
    echo ""
    echo "参数:"
    echo "  bump_type    版本递增类型 (major|minor|patch)，默认: patch"
    echo "  skip_tests   是否跳过测试 (true|false)，默认: false"
    echo "  skip_build   是否跳过构建 (true|false)，默认: false"
    echo "  skip_publish 是否跳过发布 (true|false)，默认: false"
    echo ""
    echo "示例:"
    echo "  $0 patch false false false  # 发布补丁版本"
    echo "  $0 minor true false true   # 发布次版本，跳过测试和发布"
    echo "  $0 major false true false  # 发布主版本，跳过构建"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 依赖版本管理

```python
#!/usr/bin/env python3
import json
import re
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests

@dataclass
class Dependency:
    """依赖信息"""
    name: str
    current_version: str
    latest_version: Optional[str] = None
    vulnerability_count: int = 0
    outdated: bool = False
    security_alert: bool = False

class DependencyManager:
    """依赖管理器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.dependencies: Dict[str, Dependency] = {}
    
    def scan_dependencies(self) -> Dict[str, Dependency]:
        """扫描项目依赖"""
        log_info("扫描项目依赖...")
        
        # 扫描不同类型的依赖文件
        if (self.project_path / "package.json").exists():
            self._scan_npm_dependencies()
        
        if (self.project_path / "requirements.txt").exists():
            self._scan_python_dependencies()
        
        if (self.project_path / "pyproject.toml").exists():
            self._scan_poetry_dependencies()
        
        if (self.project_path / "pom.xml").exists():
            self._scan_maven_dependencies()
        
        if (self.project_path / "build.gradle").exists():
            self._scan_gradle_dependencies()
        
        log_info(f"发现 {len(self.dependencies)} 个依赖")
        return self.dependencies
    
    def _scan_npm_dependencies(self):
        """扫描NPM依赖"""
        package_json_path = self.project_path / "package.json"
        
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)
        
        # 扫描dependencies和devDependencies
        for dep_type in ['dependencies', 'devDependencies']:
            if dep_type in package_data:
                for name, version in package_data[dep_type].items():
                    # 清理版本号
                    clean_version = self._clean_version(version)
                    
                    dependency = Dependency(
                        name=name,
                        current_version=clean_version
                    )
                    
                    self.dependencies[name] = dependency
    
    def _scan_python_dependencies(self):
        """扫描Python依赖"""
        requirements_path = self.project_path / "requirements.txt"
        
        with open(requirements_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 解析依赖行
                    match = re.match(r'^([a-zA-Z0-9\-_.]+)([><=!]+.+)?', line)
                    if match:
                        name = match.group(1)
                        version_spec = match.group(2) or ""
                        
                        dependency = Dependency(
                            name=name,
                            current_version=version_spec
                        )
                        
                        self.dependencies[name] = dependency
    
    def _scan_poetry_dependencies(self):
        """扫描Poetry依赖"""
        pyproject_path = self.project_path / "pyproject.toml"
        
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        with open(pyproject_path, 'rb') as f:
            pyproject_data = tomllib.load(f)
        
        # 扫描dependencies和dev-dependencies
        poetry_deps = pyproject_data.get('tool', {}).get('poetry', {})
        
        for dep_type in ['dependencies', 'dev-dependencies']:
            if dep_type in poetry_deps:
                for name, version in poetry_deps[dep_type].items():
                    if name != 'python':  # 跳过Python版本
                        clean_version = self._clean_version(str(version))
                        
                        dependency = Dependency(
                            name=name,
                            current_version=clean_version
                        )
                        
                        self.dependencies[name] = dependency
    
    def _scan_maven_dependencies(self):
        """扫描Maven依赖"""
        pom_path = self.project_path / "pom.xml"
        
        # 使用Maven命令获取依赖列表
        try:
            result = subprocess.run(
                ['mvn', 'dependency:list', '-DoutputFile=/dev/stdout'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析Maven输出
            for line in result.stdout.split('\n'):
                if ':' in line and not line.startswith('['):
                    parts = line.strip().split(':')
                    if len(parts) >= 4:
                        group_id = parts[0]
                        artifact_id = parts[1]
                        version = parts[3]
                        
                        name = f"{group_id}:{artifact_id}"
                        
                        dependency = Dependency(
                            name=name,
                            current_version=version
                        )
                        
                        self.dependencies[name] = dependency
        
        except subprocess.CalledProcessError:
            log_warn("Maven依赖扫描失败")
    
    def _scan_gradle_dependencies(self):
        """扫描Gradle依赖"""
        try:
            result = subprocess.run(
                ['./gradlew', 'dependencies', '--configuration', 'runtimeClasspath'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 解析Gradle输出
            for line in result.stdout.split('\n'):
                if '---' in line and ':' in line:
                    parts = line.strip().split('---')
                    if len(parts) >= 2:
                        dep_info = parts[1].strip()
                        dep_parts = dep_info.split(':')
                        
                        if len(dep_parts) >= 3:
                            group_id = dep_parts[0]
                            artifact_id = dep_parts[1]
                            version = dep_parts[2].split(' ')[0]
                            
                            name = f"{group_id}:{artifact_id}"
                            
                            dependency = Dependency(
                                name=name,
                                current_version=version
                            )
                            
                            self.dependencies[name] = dependency
        
        except subprocess.CalledProcessError:
            log_warn("Gradle依赖扫描失败")
    
    def _clean_version(self, version: str) -> str:
        """清理版本号"""
        # 移除版本范围符号
        version = re.sub(r'^[><=!^~]+', '', version)
        # 移除后缀
        version = re.sub(r'[^0-9.\-a-zA-Z]', '', version)
        return version
    
    def check_updates(self) -> Dict[str, Dependency]:
        """检查依赖更新"""
        log_info("检查依赖更新...")
        
        for name, dependency in self.dependencies.items():
            try:
                # 获取最新版本（这里使用NPM API作为示例）
                latest_version = self._get_latest_version(name)
                
                if latest_version:
                    dependency.latest_version = latest_version
                    dependency.outdated = self._is_outdated(
                        dependency.current_version, 
                        latest_version
                    )
            
            except Exception as e:
                log_warn(f"检查 {name} 更新失败: {e}")
        
        return self.dependencies
    
    def _get_latest_version(self, package_name: str) -> Optional[str]:
        """获取包的最新版本"""
        try:
            # 使用NPM API
            url = f"https://registry.npmjs.org/{package_name}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('dist-tags', {}).get('latest')
        
        except:
            # 对于其他类型的包，可以尝试不同的API
            return None
    
    def _is_outdated(self, current: str, latest: str) -> bool:
        """检查版本是否过时"""
        try:
            # 简单的版本比较
            current_parts = [int(x) for x in re.findall(r'\d+', current)]
            latest_parts = [int(x) for x in re.findall(r'\d+', latest)]
            
            # 补齐版本号
            max_len = max(len(current_parts), len(latest_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            
            return current_parts < latest_parts
        
        except:
            return False
    
    def check_vulnerabilities(self) -> Dict[str, Dependency]:
        """检查安全漏洞"""
        log_info("检查安全漏洞...")
        
        for name, dependency in self.dependencies.items():
            try:
                # 使用安全数据库检查漏洞
                vulns = self._get_vulnerabilities(name, dependency.current_version)
                dependency.vulnerability_count = len(vulns)
                dependency.security_alert = len(vulns) > 0
            
            except Exception as e:
                log_warn(f"检查 {name} 漏洞失败: {e}")
        
        return self.dependencies
    
    def _get_vulnerabilities(self, package_name: str, version: str) -> List[Dict]:
        """获取漏洞信息"""
        try:
            # 使用OSV API
            url = "https://api.osv.dev/v1/query"
            payload = {
                "package": {"name": package_name, "ecosystem": "npm"},
                "version": version
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('vulns', [])
        
        except:
            return []
    
    def update_dependencies(self, strategy: str = "patch") -> List[str]:
        """更新依赖"""
        log_info(f"更新依赖 (策略: {strategy})...")
        
        updated_packages = []
        
        for name, dependency in self.dependencies.items():
            if dependency.outdated and dependency.latest_version:
                if self._should_update(dependency, strategy):
                    try:
                        self._update_package(name, dependency.latest_version)
                        updated_packages.append(f"{name}: {dependency.current_version} -> {dependency.latest_version}")
                        dependency.current_version = dependency.latest_version
                        dependency.outdated = False
                    
                    except Exception as e:
                        log_error(f"更新 {name} 失败: {e}")
        
        log_info(f"更新了 {len(updated_packages)} 个包")
        return updated_packages
    
    def _should_update(self, dependency: Dependency, strategy: str) -> bool:
        """判断是否应该更新"""
        if dependency.security_alert:
            return True  # 安全漏洞总是要更新
        
        if strategy == "patch":
            # 只更新补丁版本
            current_parts = dependency.current_version.split('.')
            latest_parts = dependency.latest_version.split('.')
            
            return (current_parts[0] == latest_parts[0] and 
                   current_parts[1] == latest_parts[1])
        
        elif strategy == "minor":
            # 更新到次版本
            current_parts = dependency.current_version.split('.')
            latest_parts = dependency.latest_version.split('.')
            
            return current_parts[0] == latest_parts[0]
        
        elif strategy == "major":
            # 更新所有版本
            return True
        
        return False
    
    def _update_package(self, package_name: str, version: str):
        """更新包"""
        # 根据项目类型使用不同的包管理器
        if (self.project_path / "package.json").exists():
            subprocess.run(['npm', 'install', f'{package_name}@{version}'], 
                         cwd=self.project_path, check=True)
        
        elif (self.project_path / "requirements.txt").exists():
            # 更新requirements.txt
            requirements_path = self.project_path / "requirements.txt"
            with open(requirements_path, 'r') as f:
                lines = f.readlines()
            
            with open(requirements_path, 'w') as f:
                for line in lines:
                    if line.startswith(package_name):
                        f.write(f"{package_name}=={version}\n")
                    else:
                        f.write(line)
        
        elif (self.project_path / "pyproject.toml").exists():
            subprocess.run(['poetry', 'update', package_name], 
                         cwd=self.project_path, check=True)
    
    def generate_report(self) -> str:
        """生成依赖报告"""
        report = []
        report.append("# 依赖管理报告\n")
        
        total_deps = len(self.dependencies)
        outdated_deps = sum(1 for d in self.dependencies.values() if d.outdated)
        vulnerable_deps = sum(1 for d in self.dependencies.values() if d.security_alert)
        
        report.append(f"## 概览")
        report.append(f"- 总依赖数: {total_deps}")
        report.append(f"- 过时依赖: {outdated_deps}")
        report.append(f"- 漏洞依赖: {vulnerable_deps}\n")
        
        if outdated_deps > 0:
            report.append("## 过时依赖")
            for name, dep in self.dependencies.items():
                if dep.outdated:
                    report.append(f"- **{name}**: {dep.current_version} -> {dep.latest_version}")
            report.append("")
        
        if vulnerable_deps > 0:
            report.append("## 安全漏洞")
            for name, dep in self.dependencies.items():
                if dep.security_alert:
                    report.append(f"- **{name}**: {dep.vulnerability_count} 个漏洞")
            report.append("")
        
        report.append("## 所有依赖")
        for name, dep in sorted(self.dependencies.items()):
            status = "✅"
            if dep.security_alert:
                status = "🚨"
            elif dep.outdated:
                status = "⬆️"
            
            report.append(f"- {status} **{name}**: {dep.current_version}")
        
        return "\n".join(report)

def log_info(message: str):
    """日志输出"""
    print(f"[INFO] {message}")

def log_warn(message: str):
    """警告输出"""
    print(f"[WARN] {message}")

def log_error(message: str):
    """错误输出"""
    print(f"[ERROR] {message}")

# 使用示例
if __name__ == "__main__":
    manager = DependencyManager(".")
    
    # 扫描依赖
    dependencies = manager.scan_dependencies()
    
    # 检查更新
    manager.check_updates()
    
    # 检查漏洞
    manager.check_vulnerabilities()
    
    # 生成报告
    report = manager.generate_report()
    print(report)
    
    # 更新依赖
    # updated = manager.update_dependencies("patch")
    # print(f"更新的包: {updated}")
```

## 最佳实践

### 版本策略
- **语义化版本**: 严格遵循SemVer规范
- **自动化递增**: 使用工具自动管理版本号
- **预发布版本**: 合理使用alpha、beta、rc版本
- **版本锁定**: 生产环境锁定依赖版本

### 发布流程
- **自动化发布**: 使用CI/CD自动发布流程
- **变更日志**: 自动生成和维护变更日志
- **发布验证**: 发布前进行完整测试
- **回滚机制**: 建立快速回滚机制

### 依赖管理
- **定期更新**: 定期检查和更新依赖
- **安全扫描**: 定期扫描安全漏洞
- **兼容性测试**: 更新前进行兼容性测试
- **版本锁定**: 开发环境使用版本范围，生产环境锁定版本

### 团队协作
- **版本规范**: 建立团队版本规范
- **发布计划**: 制定清晰的发布计划
- **沟通机制**: 及时沟通版本变更
- **文档维护**: 维护版本相关文档

## 相关技能

- [Git工作流管理](./git-workflows/) - 版本发布流程
- [API文档生成](./api-documentation/) - API版本管理
- [Docker Compose编排](./docker-compose/) - 容器版本管理
- [代码格式化](./code-formatter/) - 代码版本规范

**MAJOR.MINOR.PATCH**
- MAJOR: Bre一个k在g ch一个ges (1.0.0 → 2.0.0)
- MINOR: New fe在ures, b一个ckw一个rd comp在ible (1.0.0 → 1.1.0)
- PATCH: 错误 fixes 在ly (1.0.0 → 1.0.1)

**Pre-发布 版本s**
- 1.0.0-一个lph一个, 1.0.0-是t一个, 1.0.0-rc.1
- Ordered: 一个lph一个 < 是t一个 < rc < 发布

## 验证检查清单

- [ ] 版本 follows SemVer 对于m在
- [ ] MAJOR 在cremented 对于 bre一个k在g ch一个ges
- [ ] MINOR 在cremented 对于 new fe在ures
- [ ] PATCH 在cremented 对于 错误 fixes
- [ ] Pre-发布 t一个gs used 对于 un发布d 版本s
- [ ] Previous 版本s documented
- [ ] 使用rs not如果ied 的 bre一个k在g ch一个ges

## 相关技能
- **ch一个ge日志-gener在或** - Document ch一个ges 与 版本
- **代码-re视图** - Re视图 版本 bumps
