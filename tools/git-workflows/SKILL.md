---
name: Git工作流管理
description: "当管理Git工作流时，分析分支策略，优化协作流程，解决合并冲突。验证工作流架构，设计CI/CD集成，和最佳实践。"
license: MIT
---

# Git工作流管理技能

## 概述

Git工作流是团队协作开发的核心机制，合理的分支策略和工作流程能够提高开发效率、降低冲突风险、保证代码质量。不当的工作流设计会导致合并困难、版本混乱、协作效率低下。

**核心原则**: 好的Git工作流应该清晰易懂、适合团队规模、支持持续集成、便于代码审查。坏的工作流会导致分支混乱、冲突频发、部署困难。

## 何时使用

**始终:**
- 团队协作开发时
- 多人维护同一项目时
- 需要代码审查时
- 持续集成/持续部署时
- 版本发布管理时
- 热修复紧急部署时

**触发短语:**
- "如何选择Git工作流？"
- "分支策略怎么设计？"
- "合并冲突怎么解决？"
- "代码审查流程"
- "发布版本管理"
- "热修复怎么处理？"

## Git工作流管理技能功能

### 分支策略
- Git Flow工作流
- GitHub Flow工作流
- GitLab Flow工作流
- 主干开发模式
- 功能分支策略
- 发布分支管理

### 协作流程
- 代码审查机制
- 合并请求管理
- 冲突解决策略
- 提交信息规范
- 版本标签管理
- 热修复流程

### CI/CD集成
- 自动化测试
- 构建流水线
- 部署策略
- 环境管理
- 回滚机制
- 监控告警

### 团队管理
- 权限控制
- 分支保护
- 提交规范
- 代码质量检查
- 发布流程
- 文档管理

## 常见问题

**❌ 分支策略混乱**
- 分支命名不规范
- 分支生命周期管理不当
- 合并策略不统一
- 长期分支积累过多

**❌ 合并冲突频发**
- 功能开发重叠
- 代码同步不及时
- 缺乏代码审查
- 重构操作不当

**❌ 版本管理混乱**
- 标签使用不规范
- 版本号不统一
- 发布流程不清晰
- 热修复处理不当

**❌ 团队协作低效**
- 提交信息不规范
- 代码审查缺失
- 权限管理不当
- 文档维护不足

## 代码示例

### Git Flow工作流配置

```bash
#!/bin/bash
# Git Flow 初始化脚本
setup_git_flow() {
    echo "初始化Git Flow工作流..."
    
    # 安装git-flow工具
    if command -v brew &> /dev/null; then
        brew install git-flow-avh
    elif command -v apt &> /dev/null; then
        sudo apt-get install git-flow
    else
        echo "请手动安装git-flow工具"
        return 1
    fi
    
    # 初始化git flow
    git flow init -d
    
    # 设置分支前缀
    git config gitflow.branch.feature "feature/"
    git config gitflow.branch.release "release/"
    git config gitflow.branch.hotfix "hotfix/"
    git config gitflow.branch.support "support/"
    git config gitflow.prefix.versiontag "v"
    
    echo "Git Flow初始化完成！"
}

# 创建功能分支
create_feature_branch() {
    local feature_name=$1
    echo "创建功能分支: $feature_name"
    
    # 确保在develop分支
    git checkout develop
    git pull origin develop
    
    # 创建功能分支
    git flow feature start $feature_name
    
    # 推送到远程
    git flow feature publish $feature_name
    
    echo "功能分支 $feature_name 创建完成"
}

# 完成功能开发
finish_feature_branch() {
    local feature_name=$1
    echo "完成功能分支: $feature_name"
    
    # 切换到功能分支
    git checkout feature/$feature_name
    
    # 确保代码最新
    git pull origin feature/$feature_name
    
    # 运行测试
    run_tests
    
    # 完成功能分支
    git flow feature finish $feature_name
    
    # 推送到远程
    git push origin develop
    
    echo "功能分支 $feature_name 已合并到develop"
}

# 创建发布分支
create_release_branch() {
    local version=$1
    echo "创建发布分支: $version"
    
    # 确保在develop分支
    git checkout develop
    git pull origin develop
    
    # 创建发布分支
    git flow release start $version
    
    # 推送到远程
    git flow release publish $version
    
    echo "发布分支 $version 创建完成"
}

# 完成发布
finish_release_branch() {
    local version=$1
    echo "完成发布: $version"
    
    # 更新版本号
    update_version_number $version
    
    # 完成发布分支
    git flow release finish $version
    
    # 推送标签和主分支
    git push origin main
    git push origin develop
    git push origin v$version
    
    echo "发布 $version 完成"
}

# 创建热修复分支
create_hotfix_branch() {
    local hotfix_name=$1
    echo "创建热修复分支: $hotfix_name"
    
    # 确保在main分支
    git checkout main
    git pull origin main
    
    # 创建热修复分支
    git flow hotfix start $hotfix_name
    
    # 推送到远程
    git flow hotfix publish $hotfix_name
    
    echo "热修复分支 $hotfix_name 创建完成"
}

# 运行测试
run_tests() {
    echo "运行测试..."
    # 这里添加具体的测试命令
    npm test || pytest || mvn test
}

# 更新版本号
update_version_number() {
    local version=$1
    echo "更新版本号到: $version"
    
    # 更新package.json
    if [ -f "package.json" ]; then
        npm version $version --no-git-tag-version
    fi
    
    # 更新其他版本文件
    # 根据项目需要添加更多版本文件更新逻辑
}
```

### GitHub Flow工作流

```bash
#!/bin/bash
# GitHub Flow 工作流脚本

# 创建功能分支
create_gh_feature() {
    local feature_name=$1
    local base_branch=${2:-main}
    
    echo "在GitHub Flow中创建功能分支: $feature_name"
    
    # 确保本地代码最新
    git checkout $base_branch
    git pull origin $base_branch
    
    # 创建并切换到功能分支
    git checkout -b feature/$feature_name
    
    # 推送到远程
    git push -u origin feature/$feature_name
    
    echo "功能分支创建完成，可以开始开发了"
}

# 提交代码规范检查
commit_with_validation() {
    local message=$1
    
    echo "验证提交..."
    
    # 运行代码格式检查
    run_linter
    
    # 运行测试
    run_tests
    
    # 检查提交信息格式
    validate_commit_message "$message"
    
    # 添加所有更改
    git add .
    
    # 提交
    git commit -m "$message"
    
    echo "提交完成"
}

# 验证提交信息格式
validate_commit_message() {
    local message=$1
    
    # 检查提交信息格式
    if [[ ! "$message" =~ ^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50} ]]; then
        echo "错误: 提交信息格式不符合规范"
        echo "格式: type(scope): description"
        echo "类型: feat, fix, docs, style, refactor, test, chore"
        exit 1
    fi
}

# 创建Pull Request
create_pull_request() {
    local feature_branch=$1
    local base_branch=${2:-main}
    local title=$3
    local body=$4
    
    echo "创建Pull Request..."
    
    # 使用GitHub CLI创建PR
    if command -v gh &> /dev/null; then
        gh pr create \
            --base $base_branch \
            --head $feature_branch \
            --title "$title" \
            --body "$body" \
            --assignee @me
    else
        echo "请手动在GitHub上创建Pull Request"
        echo "分支: $feature_branch -> $base_branch"
        echo "标题: $title"
    fi
}

# 自动化部署检查
check_deploy_status() {
    local pr_number=$1
    
    echo "检查部署状态..."
    
    # 使用GitHub CLI检查PR状态
    if command -v gh &> /dev/null; then
        gh pr view $pr_number --json statusCheckRollup --jq '.statusCheckRollup'
    fi
}

# 合并到主分支
merge_to_main() {
    local feature_branch=$1
    
    echo "合并到主分支..."
    
    # 切换到主分支
    git checkout main
    git pull origin main
    
    # 合并功能分支
    git merge --no-ff feature/$feature_branch
    
    # 推送主分支
    git push origin main
    
    # 删除功能分支
    git branch -d feature/$feature_branch
    git push origin --delete feature/$feature_branch
    
    echo "合并完成"
}

# 运行代码检查
run_linter() {
    echo "运行代码检查..."
    
    # JavaScript/TypeScript
    if [ -f "package.json" ]; then
        npm run lint || echo "警告: 代码检查发现问题"
    fi
    
    # Python
    if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        flake8 . || echo "警告: 代码检查发现问题"
        black --check . || echo "警告: 代码格式不符合规范"
    fi
}
```

### Git工作流自动化脚本

```python
#!/usr/bin/env python3
import subprocess
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class GitWorkflowManager:
    def __init__(self, config_file: str = "git-workflow.json"):
        self.config = self.load_config(config_file)
        self.branch_types = self.config.get("branch_types", {
            "feature": "feature/",
            "bugfix": "bugfix/",
            "hotfix": "hotfix/",
            "release": "release/",
            "docs": "docs/"
        })
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_default_config(config_file)
    
    def create_default_config(self, config_file: str) -> Dict:
        """创建默认配置"""
        default_config = {
            "branch_types": {
                "feature": "feature/",
                "bugfix": "bugfix/",
                "hotfix": "hotfix/",
                "release": "release/",
                "docs": "docs/"
            },
            "protected_branches": ["main", "master", "develop"],
            "commit_message_format": "type(scope): description",
            "require_tests": True,
            "require_review": True,
            "auto_merge": False
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def run_git_command(self, command: List[str]) -> str:
        """执行Git命令"""
        try:
            result = subprocess.run(
                ["git"] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git命令执行失败: {e.stderr}")
            sys.exit(1)
    
    def get_current_branch(self) -> str:
        """获取当前分支"""
        return self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    
    def create_branch(self, branch_type: str, name: str, base_branch: Optional[str] = None) -> str:
        """创建新分支"""
        if branch_type not in self.branch_types:
            raise ValueError(f"不支持的分支类型: {branch_type}")
        
        prefix = self.branch_types[branch_type]
        branch_name = f"{prefix}{name}"
        
        # 确保基础分支最新
        if base_branch:
            self.run_git_command(["checkout", base_branch])
            self.run_git_command(["pull", "origin", base_branch])
        else:
            base_branch = self.get_current_branch()
        
        # 创建新分支
        self.run_git_command(["checkout", "-b", branch_name])
        
        # 推送到远程
        self.run_git_command(["push", "-u", "origin", branch_name])
        
        print(f"创建分支成功: {branch_name} (基于 {base_branch})")
        return branch_name
    
    def validate_commit_message(self, message: str) -> bool:
        """验证提交信息格式"""
        pattern = r"^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}"
        return bool(re.match(pattern, message))
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> bool:
        """提交更改"""
        if not self.validate_commit_message(message):
            print("错误: 提交信息格式不符合规范")
            print("格式: type(scope): description")
            return False
        
        # 添加文件
        if files:
            for file in files:
                self.run_git_command(["add", file])
        else:
            self.run_git_command(["add", "."])
        
        # 提交
        self.run_git_command(["commit", "-m", message])
        print(f"提交成功: {message}")
        return True
    
    def create_pull_request(self, title: str, body: str, head: str, base: str = "main") -> bool:
        """创建Pull Request"""
        try:
            # 使用GitHub CLI创建PR
            result = subprocess.run([
                "gh", "pr", "create",
                "--title", title,
                "--body", body,
                "--base", base,
                "--head", head
            ], capture_output=True, text=True, check=True)
            
            print(f"Pull Request创建成功: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            print("创建Pull Request失败，请手动创建")
            return False
    
    def get_branch_status(self, branch: str) -> Dict:
        """获取分支状态"""
        try:
            # 获取分支信息
            ahead = self.run_git_command(["rev-list", "--count", f"origin/{branch}..{branch}"])
            behind = self.run_git_command(["rev-list", "--count", f"{branch}..origin/{branch}"])
            
            return {
                "branch": branch,
                "ahead": int(ahead),
                "behind": int(behind),
                "status": "ahead" if int(ahead) > 0 else "behind" if int(behind) > 0 else "clean"
            }
        except:
            return {"branch": branch, "status": "unknown"}
    
    def sync_branch(self, branch: str) -> bool:
        """同步分支"""
        try:
            self.run_git_command(["checkout", branch])
            self.run_git_command(["pull", "origin", branch])
            print(f"分支 {branch} 同步完成")
            return True
        except:
            print(f"分支 {branch} 同步失败")
            return False
    
    def cleanup_branches(self, days_old: int = 30) -> List[str]:
        """清理旧分支"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        # 获取所有分支
        branches = self.run_git_command(["branch", "-r"]).split('\n')
        old_branches = []
        
        for branch in branches:
            branch = branch.strip().replace('origin/', '')
            if branch in self.config.get("protected_branches", []):
                continue
            
            try:
                # 获取分支最后提交时间
                last_commit = self.run_git_command(["log", "-1", "--format=%ct", f"origin/{branch}"])
                if int(last_commit) < cutoff_date:
                    old_branches.append(branch)
            except:
                continue
        
        return old_branches

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python git-workflow.py <command> [options]")
        print("命令: create-branch, commit, pr, status, sync, cleanup")
        sys.exit(1)
    
    manager = GitWorkflowManager()
    command = sys.argv[1]
    
    if command == "create-branch":
        if len(sys.argv) < 4:
            print("用法: python git-workflow.py create-branch <type> <name> [base]")
            sys.exit(1)
        
        branch_type = sys.argv[2]
        name = sys.argv[3]
        base = sys.argv[4] if len(sys.argv) > 4 else None
        
        manager.create_branch(branch_type, name, base)
    
    elif command == "commit":
        if len(sys.argv) < 3:
            print("用法: python git-workflow.py commit <message>")
            sys.exit(1)
        
        message = sys.argv[2]
        manager.commit_changes(message)
    
    elif command == "status":
        current = manager.get_current_branch()
        status = manager.get_branch_status(current)
        print(f"当前分支: {current}")
        print(f"状态: {status}")
    
    elif command == "sync":
        current = manager.get_current_branch()
        manager.sync_branch(current)
    
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()
```

### Git Hooks配置

```bash
#!/bin/bash
# pre-commit hook - 提交前检查

echo "运行提交前检查..."

# 检查代码格式
check_code_format() {
    echo "检查代码格式..."
    
    # Python代码检查
    if command -v black &> /dev/null; then
        black --check .
        if [ $? -ne 0 ]; then
            echo "错误: Python代码格式不符合规范"
            echo "请运行: black ."
            exit 1
        fi
    fi
    
    # JavaScript代码检查
    if [ -f "package.json" ]; then
        npm run lint
        if [ $? -ne 0 ]; then
            echo "错误: JavaScript代码检查失败"
            exit 1
        fi
    fi
}

# 运行测试
run_tests() {
    echo "运行测试..."
    
    if [ -f "package.json" ]; then
        npm test
    elif [ -f "requirements.txt" ]; then
        python -m pytest
    elif [ -f "pom.xml" ]; then
        mvn test
    fi
    
    if [ $? -ne 0 ]; then
        echo "错误: 测试失败"
        exit 1
    fi
}

# 检查提交信息
check_commit_message() {
    local message=$(cat "$1")
    
    # 检查提交信息格式
    if [[ ! "$message" =~ ^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50} ]]; then
        echo "错误: 提交信息格式不符合规范"
        echo "格式: type(scope): description"
        echo "类型: feat, fix, docs, style, refactor, test, chore"
        exit 1
    fi
}

# 主检查流程
check_code_format
run_tests

if [ -f "$1" ]; then
    check_commit_message "$1"
fi

echo "提交前检查通过！"
```

## 最佳实践

### 分支策略
- **选择合适的工作流**: 根据团队规模和项目复杂度选择Git Flow、GitHub Flow等
- **统一分支命名**: 使用一致的分支命名规范
- **及时清理分支**: 定期删除已合并的分支
- **保护主分支**: 设置分支保护规则

### 提交规范
- **标准化提交信息**: 使用Conventional Commits规范
- **原子性提交**: 每次提交只做一件事
- **详细描述**: 提交信息要清晰描述更改内容
- **关联Issue**: 在提交信息中关联相关Issue

### 代码审查
- **强制代码审查**: 重要分支必须经过代码审查
- **审查清单**: 制定统一的代码审查清单
- **及时响应**: 及时处理审查意见
- **学习交流**: 通过审查互相学习

### CI/CD集成
- **自动化测试**: 每次提交都运行自动化测试
- **构建检查**: 确保代码能够成功构建
- **部署策略**: 使用蓝绿部署、金丝雀发布等策略
- **回滚机制**: 建立快速回滚机制

## 相关技能

- [API文档生成](./api-documentation/) - API版本管理和文档更新
- [Docker Compose编排](./docker-compose/) - 容器化部署工作流
- [版本管理器](./version-manager/) - 语义化版本管理
- [代码格式化](./code-formatter/) - 代码格式标准化
