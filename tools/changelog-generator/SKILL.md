---
name: 变更日志生成器
description: "当生成变更日志时，创建发布说明，记录变更。从版本控制历史自动生成变更日志。"
license: MIT
---

# 变更日志生成器技能

## 概述

变更是历史。从提交自动记录它们。手动变更日志不完整且与代码不同步。

**核心原则**: 生成的历史是准确的历史。好的变更管理应该自动化、完整、及时、用户友好。坏的变更管理会导致信息丢失、用户困惑、维护困难。

## 何时使用

**始终:**
- 发布前
- 记录变更时
- 发布发布说明时
- 跟踪版本历史时
- 创建用户友好文档时

**触发短语:**
- "生成变更日志"
- "创建发布说明"
- "有什么变更？"
- "记录这些变更"

## 变更日志生成器技能功能

### 自动生成
- Git提交分析
- 提交分类整理
- 版本对比分析
- 变更摘要生成
- 时间线构建
- 贡献者统计

### 格式化输出
- 多种格式支持
- 模板自定义
- 样式配置
- 本地化支持
- Markdown输出
- HTML输出

### 发布管理
- 版本标记管理
- 发布说明生成
- 变更影响分析
- 向后兼容性检查
- 迁移指南生成
- 重要变更突出

### 内容分析
- 提交消息解析
- 变更类型识别
- 影响范围分析
- 破坏性变更检测
- 新功能识别
- 问题修复统计

## 常见变更日志问题

**❌ 信息缺失**
- 提交消息不规范
- 变更描述不完整
- 缺少用户影响说明
- 版本信息不准确

**❌ 格式混乱**
- 时间线不清晰
- 分类不明确
- 样式不一致
- 语言不统一

**❌ 内容错误**
- 遗漏重要变更
- 错误的版本号
- 过时的信息
- 重复的条目

**❌ 维护困难**
- 手动更新耗时
- 格式不统一
- 多语言支持差
- 历史记录丢失

## 代码示例

### 变更日志生成器

```python
#!/usr/bin/env python3
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ChangeType(Enum):
    """变更类型"""
    ADDED = "added"
    CHANGED = "changed"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    FIXED = "fixed"
    SECURITY = "security"

@dataclass
class CommitInfo:
    """提交信息"""
    hash: str
    message: str
    author: str
    date: datetime
    files: List[str]
    change_type: Optional[ChangeType] = None

@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    date: datetime
    commits: List[CommitInfo]
    tag_hash: str

@dataclass
class ChangelogEntry:
    """变更日志条目"""
    change_type: ChangeType
    description: str
    scope: Optional[str] = None
    breaking: bool = False
    issues: List[str] = None

class ChangelogGenerator:
    """变更日志生成器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.commits: List[CommitInfo] = []
        self.versions: List[VersionInfo] = []
        self.config = self._load_config()
        
        # 提交消息模式
        self.commit_patterns = {
            ChangeType.ADDED: [
                r'^(?:feat|add|new)(?:\(.+\))?\s*:\s*(.+)',
                r'^add(?:ed)?\s+(.+)',
                r'^new\s+(.+)'
            ],
            ChangeType.CHANGED: [
                r'^(?:change|update|modify)(?:\(.+\))?\s*:\s*(.+)',
                r'^update(?:d)?\s+(.+)',
                r'^modify\s+(.+)'
            ],
            ChangeType.DEPRECATED: [
                r'^(?:deprecate|deprecation)(?:\(.+\))?\s*:\s*(.+)',
                r'^deprecate(?:d)?\s+(.+)'
            ],
            ChangeType.REMOVED: [
                r'^(?:remove|delete|del)(?:\(.+\))?\s*:\s*(.+)',
                r'^remove(?:d)?\s+(.+)',
                r'^delete(?:d)?\s+(.+)'
            ],
            ChangeType.FIXED: [
                r'^(?:fix|bugfix)(?:\(.+\))?\s*:\s*(.+)',
                r'^fix(?:ed)?\s+(.+)',
                r'^bugfix\s+(.+)',
                r'^hotfix\s+(.+)'
            ],
            ChangeType.SECURITY: [
                r'^(?:security|sec)(?:\(.+\))?\s*:\s*(.+)',
                r'^security\s+(.+)',
                r'^fix\s+security\s+(.+)'
            ]
        }
    
    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = self.repo_path / "changelog-config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 默认配置
        return {
            "commit_types": {
                "added": "新增",
                "changed": "变更", 
                "deprecated": "废弃",
                "removed": "移除",
                "fixed": "修复",
                "security": "安全"
            },
            "scopes": {
                "api": "API",
                "ui": "用户界面",
                "docs": "文档",
                "test": "测试",
                "build": "构建",
                "deps": "依赖"
            },
            "ignore_patterns": [
                r'^Merge.*',
                r'^Revert.*',
                r'^chore.*',
                r'^style.*',
                r'^refactor.*',
                r'^test.*',
                r'^ci.*',
                r'^docs.*'
            ]
        }
    
    def generate_changelog(self, from_version: Optional[str] = None, 
                          to_version: Optional[str] = None,
                          output_format: str = "markdown") -> str:
        """生成变更日志"""
        # 获取提交历史
        self._fetch_commits(from_version, to_version)
        
        # 分析提交
        self._analyze_commits()
        
        # 获取版本信息
        self._fetch_versions()
        
        # 生成变更日志
        if output_format == "markdown":
            return self._generate_markdown()
        elif output_format == "html":
            return self._generate_html()
        elif output_format == "json":
            return self._generate_json()
        else:
            raise ValueError(f"不支持的格式: {output_format}")
    
    def _fetch_commits(self, from_version: Optional[str], to_version: Optional[str]):
        """获取提交历史"""
        try:
            # 构建git log命令
            cmd = ["git", "log", "--pretty=format:%H|%s|%an|%ai", "--date=iso"]
            
            if from_version and to_version:
                cmd.extend([f"{from_version}..{to_version}"])
            elif from_version:
                cmd.extend([f"{from_version}..HEAD"])
            elif to_version:
                cmd.extend([f"HEAD..{to_version}"])
            
            # 执行命令
            result = subprocess.run(cmd, cwd=self.repo_path, 
                                  capture_output=True, text=True, check=True)
            
            # 解析提交
            self.commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commit_hash = parts[0]
                        message = '|'.join(parts[1:-2])
                        author = parts[-2]
                        date_str = parts[-1]
                        
                        try:
                            date = datetime.fromisoformat(date_str.replace(' ', 'T'))
                            
                            # 获取修改的文件
                            files = self._get_commit_files(commit_hash)
                            
                            commit = CommitInfo(
                                hash=commit_hash,
                                message=message,
                                author=author,
                                date=date,
                                files=files
                            )
                            self.commits.append(commit)
                        except ValueError:
                            continue
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"获取提交历史失败: {e}")
    
    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """获取提交修改的文件"""
        try:
            cmd = ["git", "show", "--name-only", "--format=", commit_hash]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            
            files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            return files
        except subprocess.CalledProcessError:
            return []
    
    def _analyze_commits(self):
        """分析提交"""
        for commit in self.commits:
            # 跳过忽略的提交
            if self._should_ignore_commit(commit.message):
                continue
            
            # 识别变更类型
            commit.change_type = self._identify_change_type(commit.message)
    
    def _should_ignore_commit(self, message: str) -> bool:
        """判断是否应该忽略提交"""
        for pattern in self.config.get("ignore_patterns", []):
            if re.match(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def _identify_change_type(self, message: str) -> Optional[ChangeType]:
        """识别变更类型"""
        for change_type, patterns in self.commit_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, message, re.IGNORECASE)
                if match:
                    return change_type
        return None
    
    def _fetch_versions(self):
        """获取版本信息"""
        try:
            # 获取所有标签
            cmd = ["git", "tag", "--sort=-version:refname"]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            
            tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # 为每个标签创建版本信息
            self.versions = []
            for tag in tags:
                if tag:
                    try:
                        # 获取标签信息
                        tag_info = self._get_tag_info(tag)
                        if tag_info:
                            self.versions.append(tag_info)
                    except:
                        continue
        
        except subprocess.CalledProcessError:
            # 如果没有标签，创建一个默认版本
            if self.commits:
                latest_date = max(commit.date for commit in self.commits)
                version = VersionInfo(
                    version="HEAD",
                    date=latest_date,
                    commits=self.commits,
                    tag_hash=""
                )
                self.versions.append(version)
    
    def _get_tag_info(self, tag: str) -> Optional[VersionInfo]:
        """获取标签信息"""
        try:
            # 获取标签提交哈希
            cmd = ["git", "rev-list", "-n", "1", tag]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            tag_hash = result.stdout.strip()
            
            # 获取标签日期
            cmd = ["git", "log", "-1", "--format=%ai", tag]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            date_str = result.stdout.strip()
            date = datetime.fromisoformat(date_str.replace(' ', 'T'))
            
            # 获取该标签到下一个标签之间的提交
            commits = self._get_commits_between_tags(tag)
            
            return VersionInfo(
                version=tag,
                date=date,
                commits=commits,
                tag_hash=tag_hash
            )
        
        except subprocess.CalledProcessError:
            return None
    
    def _get_commits_between_tags(self, tag: str) -> List[CommitInfo]:
        """获取标签之间的提交"""
        try:
            # 获取从标签到HEAD的提交
            cmd = ["git", "log", f"{tag}..HEAD", "--pretty=format:%H"]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            
            commit_hashes = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # 过滤出这些提交
            commits = []
            for commit in self.commits:
                if commit.hash in commit_hashes:
                    commits.append(commit)
            
            return commits
        except subprocess.CalledProcessError:
            return []
    
    def _generate_markdown(self) -> str:
        """生成Markdown格式变更日志"""
        lines = []
        
        # 标题
        lines.append("# 变更日志")
        lines.append("")
        
        # 按版本分组
        for version in self.versions:
            if not version.commits:
                continue
            
            # 版本标题
            lines.append(f"## [{version.version}] - {version.date.strftime('%Y-%m-%d')}")
            lines.append("")
            
            # 按变更类型分组
            changes_by_type = {}
            for commit in version.commits:
                if commit.change_type:
                    change_type = commit.change_type
                    if change_type not in changes_by_type:
                        changes_by_type[change_type] = []
                    changes_by_type[change_type].append(commit)
            
            # 输出各类型的变更
            for change_type in ChangeType:
                if change_type in changes_by_type:
                    commits = changes_by_type[change_type]
                    if commits:
                        # 类型标题
                        type_name = self.config["commit_types"].get(change_type.value, change_type.value)
                        lines.append(f"### {type_name}")
                        lines.append("")
                        
                        # 变更列表
                        for commit in commits:
                            description = self._extract_description(commit.message)
                            lines.append(f"- {description}")
                        
                        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(self) -> str:
        """生成HTML格式变更日志"""
        lines = []
        
        # HTML头部
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<meta charset='utf-8'>")
        lines.append("<title>变更日志</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; margin: 40px; }")
        lines.append("h1 { color: #333; }")
        lines.append("h2 { color: #666; border-bottom: 2px solid #eee; }")
        lines.append("h3 { color: #999; }")
        lines.append("ul { margin: 10px 0; }")
        lines.append("li { margin: 5px 0; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        
        # 标题
        lines.append("<h1>变更日志</h1>")
        
        # 按版本分组
        for version in self.versions:
            if not version.commits:
                continue
            
            # 版本标题
            lines.append(f"<h2>[{version.version}] - {version.date.strftime('%Y-%m-%d')}</h2>")
            
            # 按变更类型分组
            changes_by_type = {}
            for commit in version.commits:
                if commit.change_type:
                    change_type = commit.change_type
                    if change_type not in changes_by_type:
                        changes_by_type[change_type] = []
                    changes_by_type[change_type].append(commit)
            
            # 输出各类型的变更
            for change_type in ChangeType:
                if change_type in changes_by_type:
                    commits = changes_by_type[change_type]
                    if commits:
                        # 类型标题
                        type_name = self.config["commit_types"].get(change_type.value, change_type.value)
                        lines.append(f"<h3>{type_name}</h3>")
                        lines.append("<ul>")
                        
                        # 变更列表
                        for commit in commits:
                            description = self._extract_description(commit.message)
                            lines.append(f"<li>{description}</li>")
                        
                        lines.append("</ul>")
        
        # HTML尾部
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
    
    def _generate_json(self) -> str:
        """生成JSON格式变更日志"""
        data = {
            "title": "变更日志",
            "generated_at": datetime.now().isoformat(),
            "versions": []
        }
        
        for version in self.versions:
            if not version.commits:
                continue
            
            version_data = {
                "version": version.version,
                "date": version.date.isoformat(),
                "changes": []
            }
            
            # 按变更类型分组
            changes_by_type = {}
            for commit in version.commits:
                if commit.change_type:
                    change_type = commit.change_type
                    if change_type not in changes_by_type:
                        changes_by_type[change_type] = []
                    changes_by_type[change_type].append(commit)
            
            # 添加各类型的变更
            for change_type in ChangeType:
                if change_type in changes_by_type:
                    commits = changes_by_type[change_type]
                    for commit in commits:
                        description = self._extract_description(commit.message)
                        version_data["changes"].append({
                            "type": change_type.value,
                            "description": description,
                            "commit": commit.hash,
                            "author": commit.author,
                            "date": commit.date.isoformat()
                        })
            
            data["versions"].append(version_data)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _extract_description(self, message: str) -> str:
        """提取变更描述"""
        # 尝试从各种提交格式中提取描述
        patterns = [
            r'^(?:feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(?:\(.+\))?\s*:\s*(.+)',
            r'^(?:add|change|update|modify|remove|delete|deprecate|fix|security)(?:\(.+\))?\s*:\s*(.+)',
            r'^(?:added|changed|updated|modified|removed|deleted|deprecated|fixed|security)\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有匹配，返回原消息
        return message.strip()
    
    def generate_release_notes(self, version: str) -> str:
        """生成发布说明"""
        # 查找指定版本
        target_version = None
        for v in self.versions:
            if v.version == version:
                target_version = v
                break
        
        if not target_version:
            raise ValueError(f"版本 {version} 不存在")
        
        lines = []
        lines.append(f"# {version} 发布说明")
        lines.append("")
        lines.append(f"发布日期: {target_version.date.strftime('%Y-%m-%d')}")
        lines.append("")
        
        # 统计信息
        total_commits = len(target_version.commits)
        lines.append(f"## 统计")
        lines.append(f"- 总提交数: {total_commits}")
        
        # 贡献者
        contributors = set(commit.author for commit in target_version.commits)
        lines.append(f"- 贡献者: {', '.join(contributors)}")
        lines.append("")
        
        # 主要变更
        lines.append("## 主要变更")
        lines.append("")
        
        # 按类型分组
        changes_by_type = {}
        for commit in target_version.commits:
            if commit.change_type:
                change_type = commit.change_type
                if change_type not in changes_by_type:
                    changes_by_type[change_type] = []
                changes_by_type[change_type].append(commit)
        
        # 输出变更
        for change_type in [ChangeType.ADDED, ChangeType.CHANGED, ChangeType.FIXED]:
            if change_type in changes_by_type:
                commits = changes_by_type[change_type]
                if commits:
                    type_name = self.config["commit_types"].get(change_type.value, change_type.value)
                    lines.append(f"### {type_name}")
                    lines.append("")
                    
                    for commit in commits:
                        description = self._extract_description(commit.message)
                        lines.append(f"- {description}")
                    
                    lines.append("")
        
        # 破坏性变更
        breaking_changes = []
        for commit in target_version.commits:
            if "BREAKING" in commit.message or "breaking" in commit.message.lower():
                breaking_changes.append(commit)
        
        if breaking_changes:
            lines.append("### ⚠️ 破坏性变更")
            lines.append("")
            for commit in breaking_changes:
                description = self._extract_description(commit.message)
                lines.append(f"- {description}")
            lines.append("")
        
        return "\n".join(lines)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='变更日志生成器')
    parser.add_argument('--repo-path', default='.', help='仓库路径')
    parser.add_argument('--from-version', help='起始版本')
    parser.add_argument('--to-version', help='结束版本')
    parser.add_argument('--format', choices=['markdown', 'html', 'json'], 
                       default='markdown', help='输出格式')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--release-notes', help='生成指定版本的发布说明')
    
    args = parser.parse_args()
    
    generator = ChangelogGenerator(args.repo_path)
    
    try:
        if args.release_notes:
            # 生成发布说明
            release_notes = generator.generate_release_notes(args.release_notes)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(release_notes)
                print(f"发布说明已保存到: {args.output}")
            else:
                print(release_notes)
        else:
            # 生成变更日志
            changelog = generator.generate_changelog(
                from_version=args.from_version,
                to_version=args.to_version,
                output_format=args.format
            )
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(changelog)
                print(f"变更日志已保存到: {args.output}")
            else:
                print(changelog)
    
    except Exception as e:
        print(f"生成失败: {e}")
        exit(1)
```

### 自动发布工具

```bash
#!/bin/bash
# auto-release.sh - 自动发布工具

set -e

# 配置
REPO_PATH=${1:-"."}
VERSION_TYPE=${2:-"patch"}  # major, minor, patch
DRY_RUN=${3:-false}
CREATE_TAG=${4:-true}
PUSH_TO_REMOTE=${5:-true}
LOG_FILE="auto_release.log"

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

# 检查仓库状态
check_repo_status() {
    log_step "检查仓库状态..."
    
    cd "$REPO_PATH"
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_error "仓库有未提交的更改，请先提交或暂存"
        exit 1
    fi
    
    # 检查是否在主分支
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        log_warn "当前不在主分支 ($current_branch)"
    fi
    
    # 拉取最新更改
    log_info "拉取最新更改..."
    git pull origin "$current_branch" || true
    
    log_info "仓库状态检查完成"
}

# 获取当前版本
get_current_version() {
    # 尝试从package.json获取
    if [ -f "package.json" ]; then
        if command -v jq &> /dev/null; then
            jq -r '.version' package.json 2>/dev/null
        else
            grep -o '"version": "[^"]*"' package.json | cut -d'"' -f4
        fi
    # 尝试从pyproject.toml获取
    elif [ -f "pyproject.toml" ]; then
        grep -o '^version = "[^"]*"' pyproject.toml | cut -d'"' -f2
    # 尝试从Cargo.toml获取
    elif [ -f "Cargo.toml" ]; then
        grep -o '^version = "[^"]*"' Cargo.toml | cut -d'"' -f2
    # 尝试从git标签获取
    else
        git describe --tags --abbrev=0 2>/dev/null || echo "0.0.1"
    fi
}

# 计算新版本
calculate_new_version() {
    local current_version=$1
    local version_type=$2
    
    # 解析版本号
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $version_type in
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
    esac
    
    echo "${major}.${minor}.${patch}"
}

# 更新版本文件
update_version_files() {
    local new_version=$1
    
    log_step "更新版本文件到 $new_version..."
    
    # 更新package.json
    if [ -f "package.json" ]; then
        if command -v jq &> /dev/null; then
            jq --arg version "$new_version" '.version = $version' package.json > package.json.tmp
            mv package.json.tmp package.json
            log_info "已更新 package.json"
        else
            log_warn "jq未安装，跳过package.json更新"
        fi
    fi
    
    # 更新pyproject.toml
    if [ -f "pyproject.toml" ]; then
        sed -i.bak "s/^version = .*/version = \"$new_version\"/" pyproject.toml
        rm -f pyproject.toml.bak
        log_info "已更新 pyproject.toml"
    fi
    
    # 更新Cargo.toml
    if [ -f "Cargo.toml" ]; then
        sed -i.bak "s/^version = .*/version = \"$new_version\"/" Cargo.toml
        rm -f Cargo.toml.bak
        log_info "已更新 Cargo.toml"
    fi
    
    # 更新其他可能的版本文件
    for file in setup.py __init__.py; do
        if [ -f "$file" ]; then
            if grep -q "__version__" "$file"; then
                sed -i.bak "s/__version__ = .*/__version__ = \"$new_version\"/" "$file"
                rm -f "${file}.bak"
                log_info "已更新 $file"
            fi
        fi
    done
}

# 生成变更日志
generate_changelog() {
    local new_version=$1
    local previous_version=$2
    
    log_step "生成变更日志..."
    
    # 使用Python生成器
    if command -v python3 &> /dev/null; then
        python3 changelog_generator.py \
            --from-version "$previous_version" \
            --to-version "HEAD" \
            --output "CHANGELOG.md" \
            --format markdown 2>> "$LOG_FILE" || true
        
        if [ -f "CHANGELOG.md" ]; then
            log_info "变更日志已生成: CHANGELOG.md"
        else
            log_warn "变更日志生成失败"
        fi
    else
        log_warn "Python3未安装，跳过变更日志生成"
    fi
}

# 创建发布标签
create_release_tag() {
    local version=$1
    
    log_step "创建发布标签..."
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "试运行模式，不创建实际标签"
        return
    fi
    
    # 提交版本文件更改
    git add .
    git commit -m "chore: bump version to $version"
    
    # 创建标签
    git tag -a "v$version" -m "Release $version"
    
    log_info "已创建标签 v$version"
}

# 推送到远程
push_to_remote() {
    local version=$1
    
    log_step "推送到远程仓库..."
    
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "试运行模式，不推送到远程"
        return
    fi
    
    # 推送提交
    git push origin
    
    # 推送标签
    git push origin "v$version"
    
    log_info "已推送到远程仓库"
}

# 生成发布说明
generate_release_notes() {
    local version=$1
    
    log_step "生成发布说明..."
    
    if command -v python3 &> /dev/null; then
        python3 changelog_generator.py \
            --release-notes "$version" \
            --output "RELEASE_NOTES.md" 2>> "$LOG_FILE" || true
        
        if [ -f "RELEASE_NOTES.md" ]; then
            log_info "发布说明已生成: RELEASE_NOTES.md"
            
            # 显示发布说明
            echo ""
            echo "=== 发布说明 ==="
            cat RELEASE_NOTES.md
            echo "=================="
        else
            log_warn "发布说明生成失败"
        fi
    else
        log_warn "Python3未安装，跳过发布说明生成"
    fi
}

# 主函数
main() {
    log_info "开始自动发布流程..."
    log_info "仓库路径: $REPO_PATH"
    log_info "版本类型: $VERSION_TYPE"
    log_info "试运行: $DRY_RUN"
    
    # 检查仓库状态
    check_repo_status
    
    # 获取当前版本
    current_version=$(get_current_version)
    log_info "当前版本: $current_version"
    
    # 计算新版本
    new_version=$(calculate_new_version "$current_version" "$VERSION_TYPE")
    log_info "新版本: $new_version"
    
    # 更新版本文件
    update_version_files "$new_version"
    
    # 生成变更日志
    generate_changelog "$new_version" "$current_version"
    
    # 创建标签
    if [ "$CREATE_TAG" = "true" ]; then
        create_release_tag "$new_version"
    fi
    
    # 推送到远程
    if [ "$PUSH_TO_REMOTE" = "true" ]; then
        push_to_remote "$new_version"
    fi
    
    # 生成发布说明
    generate_release_notes "$new_version"
    
    log_info "自动发布流程完成！"
    log_info "新版本: $new_version"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [repo_path] [version_type] [dry_run] [create_tag] [push_to_remote]"
    echo ""
    echo "参数:"
    echo "  repo_path      仓库路径，默认: ."
    echo "  version_type   版本类型 (major|minor|patch)，默认: patch"
    echo "  dry_run        是否试运行 (true|false)，默认: false"
    echo "  create_tag     是否创建标签 (true|false)，默认: true"
    echo "  push_to_remote 是否推送到远程 (true|false)，默认: true"
    echo ""
    echo "示例:"
    echo "  $0 . minor false true true"
    echo "  $0 ./myproject patch"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 提交消息规范化工具

```python
#!/usr/bin/env python3
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class CommitType(Enum):
    """提交类型"""
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    PERF = "perf"
    CI = "ci"
    BUILD = "build"
    REVERT = "revert"

@dataclass
class CommitMessage:
    """提交消息"""
    type: CommitType
    scope: Optional[str]
    subject: str
    body: Optional[str]
    footer: Optional[str]
    breaking: bool = False

class CommitMessageNormalizer:
    """提交消息规范化工具"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.type_descriptions = {
            CommitType.FEAT: "新功能",
            CommitType.FIX: "修复",
            CommitType.DOCS: "文档",
            CommitType.STYLE: "格式",
            CommitType.REFACTOR: "重构",
            CommitType.TEST: "测试",
            CommitType.CHORE: "构建过程或辅助工具的变动",
            CommitType.PERF: "性能优化",
            CommitType.CI: "CI配置",
            CommitType.BUILD: "构建系统",
            CommitType.REVERT: "回滚"
        }
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置"""
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 默认配置
        return {
            "scopes": [
                "api", "ui", "docs", "test", "build", "deps", "config",
                "auth", "db", "cache", "logger", "utils", "types"
            ],
            "max_subject_length": 50,
            "max_body_line_length": 72,
            "require_scope": False,
            "require_body": False,
            "allow_breaking": True
        }
    
    def normalize_message(self, message: str) -> CommitMessage:
        """规范化提交消息"""
        # 清理消息
        cleaned_message = self._clean_message(message)
        
        # 解析现有消息
        parsed = self._parse_message(cleaned_message)
        
        # 如果解析失败，尝试智能识别
        if not parsed:
            parsed = self._intelligent_parse(cleaned_message)
        
        # 规范化各个部分
        if parsed:
            parsed = self._normalize_commit(parsed)
        
        return parsed
    
    def _clean_message(self, message: str) -> str:
        """清理消息"""
        # 移除多余空行
        lines = [line.strip() for line in message.split('\n')]
        
        # 移除空行
        cleaned_lines = [line for line in lines if line]
        
        return '\n'.join(cleaned_lines)
    
    def _parse_message(self, message: str) -> Optional[CommitMessage]:
        """解析提交消息"""
        lines = message.split('\n')
        if not lines:
            return None
        
        # 解析标题行
        header = lines[0]
        
        # 匹配格式: type(scope): subject
        match = re.match(r'^(\w+)(?:\(([^)]+)\))?\s*:\s*(.+)$', header)
        if not match:
            return None
        
        type_str = match.group(1)
        scope = match.group(2)
        subject = match.group(3)
        
        # 验证类型
        try:
            commit_type = CommitType(type_str)
        except ValueError:
            return None
        
        # 解析正文
        body = None
        footer = None
        breaking = False
        
        if len(lines) > 1:
            # 查找正文和脚注
            body_lines = []
            footer_lines = []
            
            i = 1
            while i < len(lines):
                line = lines[i]
                if line.startswith('BREAKING CHANGE:') or line.startswith('BREAKING-CHANGE:'):
                    breaking = True
                    footer_lines.append(line)
                elif line.lower().startswith('closes:') or line.lower().startswith('fixes:'):
                    footer_lines.append(line)
                elif body_lines or not footer_lines:
                    body_lines.append(line)
                else:
                    footer_lines.append(line)
                i += 1
            
            if body_lines:
                body = '\n'.join(body_lines)
            
            if footer_lines:
                footer = '\n'.join(footer_lines)
        
        return CommitMessage(
            type=commit_type,
            scope=scope,
            subject=subject,
            body=body,
            footer=footer,
            breaking=breaking
        )
    
    def _intelligent_parse(self, message: str) -> Optional[CommitMessage]:
        """智能解析提交消息"""
        lines = message.split('\n')
        if not lines:
            return None
        
        first_line = lines[0]
        
        # 尝试识别类型
        commit_type = self._identify_type(first_line)
        
        # 提取范围
        scope = self._extract_scope(first_line)
        
        # 提取主题
        subject = self._extract_subject(first_line)
        
        # 检查破坏性变更
        breaking = self._check_breaking(message)
        
        # 提取正文和脚注
        body, footer = self._extract_body_and_footer(lines[1:] if len(lines) > 1 else [])
        
        return CommitMessage(
            type=commit_type,
            scope=scope,
            subject=subject,
            body=body,
            footer=footer,
            breaking=breaking
        )
    
    def _identify_type(self, message: str) -> CommitType:
        """识别提交类型"""
        message_lower = message.lower()
        
        # 关键词映射
        type_keywords = {
            CommitType.FEAT: ['add', 'new', 'feature', 'implement', 'create'],
            CommitType.FIX: ['fix', 'bug', 'error', 'issue', 'problem', 'resolve'],
            CommitType.DOCS: ['doc', 'readme', 'document', 'comment'],
            CommitType.STYLE: ['style', 'format', 'lint', 'indent'],
            CommitType.REFACTOR: ['refactor', 'restructure', 'reorganize', 'cleanup'],
            CommitType.TEST: ['test', 'spec', 'unit', 'integration'],
            CommitType.CHORE: ['chore', 'maintenance', 'update', 'upgrade'],
            CommitType.PERF: ['performance', 'optimize', 'speed', 'fast'],
            CommitType.CI: ['ci', 'cd', 'pipeline', 'workflow'],
            CommitType.BUILD: ['build', 'compile', 'webpack', 'babel'],
            CommitType.REVERT: ['revert', 'undo', 'rollback']
        }
        
        for commit_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return commit_type
        
        # 默认为chore
        return CommitType.CHORE
    
    def _extract_scope(self, message: str) -> Optional[str]:
        """提取范围"""
        # 查找括号中的内容
        match = re.search(r'\(([^)]+)\)', message)
        if match:
            scope = match.group(1)
            # 验证范围是否在配置中
            if scope in self.config.get("scopes", []):
                return scope
        
        return None
    
    def _extract_subject(self, message: str) -> str:
        """提取主题"""
        # 移除类型和范围
        message = re.sub(r'^\w+(?:\([^)]+\))?\s*:\s*', '', message)
        
        # 移除破坏性变更标记
        message = re.sub(r'!\s*', '', message)
        
        return message.strip()
    
    def _check_breaking(self, message: str) -> bool:
        """检查是否为破坏性变更"""
        breaking_indicators = [
            'breaking', 'break', 'deprecated', 'remove', 'delete',
            'incompatible', 'major', 'api change'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in breaking_indicators)
    
    def _extract_body_and_footer(self, lines: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """提取正文和脚注"""
        if not lines:
            return None, None
        
        body_lines = []
        footer_lines = []
        
        for line in lines:
            if (line.startswith('BREAKING CHANGE:') or 
                line.startswith('BREAKING-CHANGE:') or
                line.lower().startswith('closes:') or
                line.lower().startswith('fixes:')):
                footer_lines.append(line)
            elif body_lines or not footer_lines:
                body_lines.append(line)
            else:
                footer_lines.append(line)
        
        body = '\n'.join(body_lines) if body_lines else None
        footer = '\n'.join(footer_lines) if footer_lines else None
        
        return body, footer
    
    def _normalize_commit(self, commit: CommitMessage) -> CommitMessage:
        """规范化提交"""
        # 规范化主题
        commit.subject = self._normalize_subject(commit.subject)
        
        # 规范化范围
        if commit.scope:
            commit.scope = self._normalize_scope(commit.scope)
        
        # 规范化正文
        if commit.body:
            commit.body = self._normalize_body(commit.body)
        
        # 规范化脚注
        if commit.footer:
            commit.footer = self._normalize_footer(commit.footer)
        
        return commit
    
    def _normalize_subject(self, subject: str) -> str:
        """规范化主题"""
        # 移除末尾句号
        subject = subject.rstrip('.')
        
        # 确保首字母小写
        if subject:
            subject = subject[0].lower() + subject[1:]
        
        # 检查长度
        max_length = self.config.get("max_subject_length", 50)
        if len(subject) > max_length:
            # 截断并添加省略号
            subject = subject[:max_length-3] + "..."
        
        return subject
    
    def _normalize_scope(self, scope: str) -> str:
        """规范化范围"""
        # 转换为小写
        scope = scope.lower()
        
        # 验证范围
        valid_scopes = self.config.get("scopes", [])
        if valid_scopes and scope not in valid_scopes:
            # 尝试找到最接近的有效范围
            for valid_scope in valid_scopes:
                if valid_scope in scope or scope in valid_scope:
                    return valid_scope
        
        return scope
    
    def _normalize_body(self, body: str) -> str:
        """规范化正文"""
        lines = body.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 检查行长度
                max_length = self.config.get("max_body_line_length", 72)
                if len(line) > max_length:
                    # 简单的单词换行
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) <= max_length:
                            current_line += (" " if current_line else "") + word
                        else:
                            if current_line:
                                normalized_lines.append(current_line)
                            current_line = word
                    if current_line:
                        normalized_lines.append(current_line)
                else:
                    normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _normalize_footer(self, footer: str) -> str:
        """规范化脚注"""
        lines = footer.split('\n')
        normalized_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 规范化关闭问题格式
                if line.lower().startswith('closes:') or line.lower().startswith('fixes:'):
                    # 提取问题编号
                    issues = re.findall(r'#(\d+)', line)
                    if issues:
                        line = f"Closes: {', '.join(f'#{issue}' for issue in issues)}"
                
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def format_message(self, commit: CommitMessage) -> str:
        """格式化提交消息"""
        parts = []
        
        # 标题行
        title_parts = [commit.type.value]
        if commit.scope:
            title_parts.append(f"({commit.scope})")
        if commit.breaking:
            title_parts.append("!")
        title_parts.append(f": {commit.subject}")
        
        parts.append(''.join(title_parts))
        
        # 正文
        if commit.body:
            parts.append("")
            parts.append(commit.body)
        
        # 脚注
        if commit.footer:
            parts.append("")
            parts.append(commit.footer)
        
        return '\n'.join(parts)
    
    def validate_message(self, commit: CommitMessage) -> List[str]:
        """验证提交消息"""
        errors = []
        
        # 检查主题长度
        max_subject_length = self.config.get("max_subject_length", 50)
        if len(commit.subject) > max_subject_length:
            errors.append(f"主题长度超过限制 ({max_subject_length} 字符)")
        
        # 检查是否需要范围
        if self.config.get("require_scope", False) and not commit.scope:
            errors.append("缺少提交范围")
        
        # 检查是否需要正文
        if self.config.get("require_body", False) and not commit.body:
            errors.append("缺少提交正文")
        
        # 检查破坏性变更
        if commit.breaking and not self.config.get("allow_breaking", True):
            errors.append("不允许破坏性变更")
        
        return errors

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='提交消息规范化工具')
    parser.add_argument('message', help='提交消息')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--validate', action='store_true', help='仅验证消息')
    parser.add_argument('--format', action='store_true', help='格式化消息')
    
    args = parser.parse_args()
    
    normalizer = CommitMessageNormalizer(args.config)
    
    try:
        # 规范化消息
        normalized = normalizer.normalize_message(args.message)
        
        if not normalized:
            print("无法解析提交消息")
            exit(1)
        
        if args.validate:
            # 验证消息
            errors = normalizer.validate_message(normalized)
            if errors:
                print("验证失败:")
                for error in errors:
                    print(f"  - {error}")
                exit(1)
            else:
                print("✅ 验证通过")
        elif args.format:
            # 格式化消息
            formatted = normalizer.format_message(normalized)
            print(formatted)
        else:
            # 显示规范化结果
            print(f"类型: {normalized.type.value}")
            print(f"范围: {normalized.scope or '无'}")
            print(f"主题: {normalized.subject}")
            print(f"破坏性: {'是' if normalized.breaking else '否'}")
            if normalized.body:
                print(f"正文: {normalized.body}")
            if normalized.footer:
                print(f"脚注: {normalized.footer}")
    
    except Exception as e:
        print(f"处理失败: {e}")
        exit(1)
```

## 最佳实践

### 变更管理
- **自动化生成**: 从提交历史自动生成变更日志
- **标准化格式**: 使用统一的变更日志格式
- **版本标记**: 使用语义化版本号
- **发布说明**: 为每个版本生成详细说明

### 提交规范
- **约定式提交**: 使用标准化的提交消息格式
- **类型分类**: 明确区分不同类型的变更
- **范围限定**: 指定变更影响的范围
- **描述清晰**: 提供清晰简洁的变更描述

### 发布流程
- **预发布检查**: 发布前进行完整检查
- **自动化测试**: 确保代码质量
- **版本标记**: 创建准确的版本标签
- **文档更新**: 同步更新相关文档

### 用户友好
- **变更摘要**: 提供用户关心的变更摘要
- **影响说明**: 明确说明变更的影响
- **迁移指南**: 为破坏性变更提供迁移指南
- **多语言支持**: 支持多种语言的变更日志

## 相关技能

- [版本管理器](./version-manager/) - 版本控制管理
- [代码格式化器](./code-formatter/) - 代码格式规范
- [文件分析器](./file-analyzer/) - 文件变更分析
- [依赖分析器](./dependency-analyzer/) - 依赖变更跟踪

**Fe在ures (使用r-V是ible)**
- New c一个p一个bilities
- 改进d 函数一个lity
- 使用r-f一个c在g enh一个cements

**错误 Fixes**
- Resolved 是sues
- Fixed 错误s
- C或rected 是h一个vi或

**Bre一个k在g Ch一个ges**
- API ch一个ges
- Beh一个vi或 ch一个ges
- Deprec在i在s

**Intern一个l Ch一个ges**
- Ref一个ct或在g
- 性能 improvements
- Technic一个l debt reducti在

## 验证检查清单

- [ ] All ch一个ges documented
- [ ] Grouped 通过 类型 (fe在, fix, etc.)
- [ ] 使用r-f一个c在g ch一个ges highlighted
- [ ] Bre一个k在g ch一个ges cle一个rly m一个rked
- [ ] D在e/版本 rec或ded
- [ ] L在ks 到 commits/PRs 在cluded

## 相关技能
- **版本-m一个一个ger** - Determ在e 版本 num是r
- **git-一个一个lys是** - An一个lyze commits
