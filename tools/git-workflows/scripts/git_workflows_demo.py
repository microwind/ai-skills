#!/usr/bin/env python3
"""
Git工作流演示 - 模拟Git分支策略和工作流程
"""

import os
import json
import time
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum

class BranchType(Enum):
    """分支类型"""
    MAIN = "main"
    DEVELOP = "develop"
    FEATURE = "feature"
    RELEASE = "release"
    HOTFIX = "hotfix"

class CommitStatus(Enum):
    """提交状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"

@dataclass
class Commit:
    """提交记录"""
    id: str
    message: str
    author: str
    timestamp: float
    branch: str
    files_changed: List[str]
    status: CommitStatus = CommitStatus.PENDING
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Branch:
    """分支"""
    name: str
    type: BranchType
    base_branch: Optional[str]
    commits: List[Commit]
    created_at: float
    last_updated: float
    
    def __post_init__(self):
        if not self.commits:
            self.commits = []

@dataclass
class PullRequest:
    """拉取请求"""
    id: str
    title: str
    description: str
    source_branch: str
    target_branch: str
    author: str
    created_at: float
    status: str = "open"
    reviewers: List[str] = None
    approvals: int = 0
    
    def __post_init__(self):
        if self.reviewers is None:
            self.reviewers = []

class GitRepository:
    """Git仓库模拟"""
    
    def __init__(self, name: str):
        self.name = name
        self.branches: Dict[str, Branch] = {}
        self.current_branch = "main"
        self.pull_requests: List[PullRequest] = []
        self.workflows: List[str] = ["Git Flow", "GitHub Flow", "GitLab Flow"]
        
        # 初始化主分支
        self._create_branch("main", BranchType.MAIN)
    
    def _create_branch(self, name: str, branch_type: BranchType, base_branch: str = None) -> Branch:
        """创建分支"""
        branch = Branch(
            name=name,
            type=branch_type,
            base_branch=base_branch,
            commits=[],
            created_at=time.time(),
            last_updated=time.time()
        )
        
        self.branches[name] = branch
        return branch
    
    def create_feature_branch(self, feature_name: str, base_branch: str = "develop") -> str:
        """创建功能分支"""
        branch_name = f"feature/{feature_name}"
        
        if base_branch not in self.branches:
            raise ValueError(f"Base branch {base_branch} does not exist")
        
        branch = self._create_branch(branch_name, BranchType.FEATURE, base_branch)
        
        # 复制基础分支的提交历史
        base_commits = self.branches[base_branch].commits.copy()
        branch.commits = base_commits
        
        print(f"🌿 创建功能分支: {branch_name} <- {base_branch}")
        return branch_name
    
    def create_release_branch(self, version: str, base_branch: str = "develop") -> str:
        """创建发布分支"""
        branch_name = f"release/{version}"
        
        branch = self._create_branch(branch_name, BranchType.RELEASE, base_branch)
        
        # 复制基础分支的提交历史
        base_commits = self.branches[base_branch].commits.copy()
        branch.commits = base_commits
        
        print(f"🚀 创建发布分支: {branch_name} <- {base_branch}")
        return branch_name
    
    def create_hotfix_branch(self, hotfix_name: str, base_branch: str = "main") -> str:
        """创建热修复分支"""
        branch_name = f"hotfix/{hotfix_name}"
        
        branch = self._create_branch(branch_name, BranchType.HOTFIX, base_branch)
        
        # 复制基础分支的提交历史
        base_commits = self.branches[base_branch].commits.copy()
        branch.commits = base_commits
        
        print(f"🔥 创建热修复分支: {branch_name} <- {base_branch}")
        return branch_name
    
    def commit(self, message: str, author: str, files: List[str] = None) -> str:
        """提交代码"""
        if files is None:
            files = ["README.md"]
        
        commit = Commit(
            id=self._generate_commit_id(),
            message=message,
            author=author,
            timestamp=time.time(),
            branch=self.current_branch,
            files_changed=files
        )
        
        self.branches[self.current_branch].commits.append(commit)
        self.branches[self.current_branch].last_updated = time.time()
        
        print(f"📝 提交: {commit.id[:8]} - {message}")
        return commit.id
    
    def switch_branch(self, branch_name: str):
        """切换分支"""
        if branch_name not in self.branches:
            raise ValueError(f"Branch {branch_name} does not exist")
        
        self.current_branch = branch_name
        print(f"🔄 切换到分支: {branch_name}")
    
    def merge_branch(self, source_branch: str, target_branch: str, strategy: str = "merge") -> bool:
        """合并分支"""
        if source_branch not in self.branches or target_branch not in self.branches:
            return False
        
        source = self.branches[source_branch]
        target = self.branches[target_branch]
        
        # 模拟合并冲突检查
        if self._has_conflicts(source, target):
            print(f"⚠️  检测到合并冲突: {source_branch} -> {target_branch}")
            return False
        
        # 执行合并
        if strategy == "merge":
            # 合并提交
            merge_commit = Commit(
                id=self._generate_commit_id(),
                message=f"Merge {source_branch} into {target_branch}",
                author="System",
                timestamp=time.time(),
                branch=target_branch,
                files_changed=[],
                status=CommitStatus.MERGED
            )
            
            # 合并提交历史
            target.commits.extend(source.commits)
            target.commits.append(merge_commit)
        
        elif strategy == "rebase":
            # 变基
            target.commits.extend(source.commits)
        
        target.last_updated = time.time()
        
        print(f"✅ 合并成功: {source_branch} -> {target_branch}")
        return True
    
    def create_pull_request(self, title: str, description: str, 
                          source_branch: str, target_branch: str, author: str) -> str:
        """创建拉取请求"""
        pr = PullRequest(
            id=self._generate_pr_id(),
            title=title,
            description=description,
            source_branch=source_branch,
            target_branch=target_branch,
            author=author,
            created_at=time.time()
        )
        
        self.pull_requests.append(pr)
        print(f"🔀 创建拉取请求: #{pr.id} - {title}")
        return pr.id
    
    def review_pull_request(self, pr_id: str, reviewer: str, approved: bool):
        """审核拉取请求"""
        pr = next((pr for pr in self.pull_requests if pr.id == pr_id), None)
        if not pr:
            return False
        
        if reviewer not in pr.reviewers:
            pr.reviewers.append(reviewer)
        
        if approved:
            pr.approvals += 1
            print(f"✅ {reviewer} 批准了 PR #{pr_id}")
        else:
            print(f"❌ {reviewer} 拒绝了 PR #{pr_id}")
        
        return True
    
    def merge_pull_request(self, pr_id: str) -> bool:
        """合并拉取请求"""
        pr = next((pr for pr in self.pull_requests if pr.id == pr_id), None)
        if not pr:
            return False
        
        # 检查批准数量
        if pr.approvals < 1:
            print(f"❌ PR #{pr_id} 批准数量不足")
            return False
        
        # 执行合并
        success = self.merge_branch(pr.source_branch, pr.target_branch)
        
        if success:
            pr.status = "merged"
            print(f"✅ PR #{pr_id} 已合并")
            
            # 删除源分支
            if pr.source_branch in self.branches:
                del self.branches[pr.source_branch]
                print(f"🗑️  删除分支: {pr.source_branch}")
        
        return success
    
    def _generate_commit_id(self) -> str:
        """生成提交ID"""
        return f"{random.randint(1000000, 9999999):x}"
    
    def _generate_pr_id(self) -> str:
        """生成PR ID"""
        return str(len(self.pull_requests) + 1)
    
    def _has_conflicts(self, source: Branch, target: Branch) -> bool:
        """检查是否有冲突"""
        # 简化的冲突检测：随机决定
        return random.random() < 0.1  # 10%概率有冲突
    
    def get_branch_history(self, branch_name: str) -> List[Commit]:
        """获取分支历史"""
        if branch_name not in self.branches:
            return []
        return self.branches[branch_name].commits
    
    def get_repository_status(self) -> dict:
        """获取仓库状态"""
        return {
            "name": self.name,
            "current_branch": self.current_branch,
            "branches": list(self.branches.keys()),
            "total_commits": sum(len(branch.commits) for branch in self.branches.values()),
            "open_prs": len([pr for pr in self.pull_requests if pr.status == "open"]),
            "merged_prs": len([pr for pr in self.pull_requests if pr.status == "merged"])
        }

class GitFlowWorkflow:
    """Git Flow工作流"""
    
    def __init__(self, repo: GitRepository):
        self.repo = repo
        self.repo._create_branch("develop", BranchType.DEVELOP, "main")
    
    def start_feature(self, feature_name: str) -> str:
        """开始功能开发"""
        branch_name = self.repo.create_feature_branch(feature_name)
        self.repo.switch_branch(branch_name)
        return branch_name
    
    def finish_feature(self, feature_name: str, author: str) -> bool:
        """完成功能开发"""
        branch_name = f"feature/{feature_name}"
        
        # 创建PR到develop分支
        pr_id = self.repo.create_pull_request(
            title=f"Feature: {feature_name}",
            description=f"Implement {feature_name} feature",
            source_branch=branch_name,
            target_branch="develop",
            author=author
        )
        
        # 模拟审核
        self.repo.review_pull_request(pr_id, "reviewer1", True)
        
        # 合并PR
        return self.repo.merge_pull_request(pr_id)
    
    def start_release(self, version: str) -> str:
        """开始发布准备"""
        branch_name = self.repo.create_release_branch(version)
        self.repo.switch_branch(branch_name)
        return branch_name
    
    def finish_release(self, version: str) -> bool:
        """完成发布"""
        release_branch = f"release/{version}"
        
        # 合并到main分支
        success1 = self.repo.merge_branch(release_branch, "main")
        
        # 合并到develop分支
        success2 = self.repo.merge_branch(release_branch, "develop")
        
        if success1 and success2:
            # 删除发布分支
            del self.repo.branches[release_branch]
            print(f"🎉 发布完成: {version}")
        
        return success1 and success2
    
    def create_hotfix(self, hotfix_name: str) -> str:
        """创建热修复"""
        branch_name = self.repo.create_hotfix_branch(hotfix_name)
        self.repo.switch_branch(branch_name)
        return branch_name
    
    def finish_hotfix(self, hotfix_name: str) -> bool:
        """完成热修复"""
        branch_name = f"hotfix/{hotfix_name}"
        
        # 合并到main分支
        success1 = self.repo.merge_branch(branch_name, "main")
        
        # 合并到develop分支
        success2 = self.repo.merge_branch(branch_name, "develop")
        
        if success1 and success2:
            # 删除热修复分支
            del self.repo.branches[branch_name]
            print(f"🔥 热修复完成: {hotfix_name}")
        
        return success1 and success2

class GitHubFlowWorkflow:
    """GitHub Flow工作流"""
    
    def __init__(self, repo: GitRepository):
        self.repo = repo
    
    def start_feature(self, feature_name: str) -> str:
        """开始功能开发"""
        branch_name = self.repo.create_feature_branch(feature_name, "main")
        self.repo.switch_branch(branch_name)
        return branch_name
    
    def finish_feature(self, feature_name: str, author: str) -> bool:
        """完成功能开发"""
        branch_name = f"feature/{feature_name}"
        
        # 创建PR到main分支
        pr_id = self.repo.create_pull_request(
            title=f"Feature: {feature_name}",
            description=f"Implement {feature_name} feature",
            source_branch=branch_name,
            target_branch="main",
            author=author
        )
        
        # 模拟审核
        self.repo.review_pull_request(pr_id, "reviewer1", True)
        self.repo.review_pull_request(pr_id, "reviewer2", True)
        
        # 合并PR
        return self.repo.merge_pull_request(pr_id)

def demonstrate_git_flow():
    """演示Git Flow"""
    print("\n🌊 Git Flow工作流演示")
    print("=" * 50)
    
    repo = GitRepository("my-project")
    gitflow = GitFlowWorkflow(repo)
    
    # 开发者Alice开始功能开发
    print("\n👨‍💻 Alice开始功能开发:")
    feature_branch = gitflow.start_feature("user-authentication")
    repo.commit("Add login form", "Alice", ["login.html", "login.css"])
    repo.commit("Implement authentication logic", "Alice", ["auth.js"])
    
    # 完成功能开发
    print("\n✅ Alice完成功能开发:")
    success = gitflow.finish_feature("user-authentication", "Alice")
    
    # 开发者Bob开始另一个功能
    print("\n👩‍💻 Bob开始功能开发:")
    feature_branch = gitflow.start_feature("user-profile")
    repo.commit("Add profile page", "Bob", ["profile.html"])
    repo.commit("Implement profile editing", "Bob", ["profile.js"])
    
    gitflow.finish_feature("user-profile", "Bob")
    
    # 开始发布准备
    print("\n🚀 开始发布准备:")
    release_branch = gitflow.start_release("v1.0.0")
    repo.commit("Update version to 1.0.0", "Release Manager", ["package.json"])
    repo.commit("Add changelog", "Release Manager", ["CHANGELOG.md"])
    
    gitflow.finish_release("v1.0.0")
    
    # 创建热修复
    print("\n🔥 创建热修复:")
    hotfix_branch = gitflow.create_hotfix("fix-login-bug")
    repo.commit("Fix critical login bug", "Alice", ["auth.js"])
    
    gitflow.finish_hotfix("fix-login-bug")
    
    # 显示仓库状态
    status = repo.get_repository_status()
    print(f"\n📊 仓库状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")

def demonstrate_github_flow():
    """演示GitHub Flow"""
    print("\n🐙 GitHub Flow工作流演示")
    print("=" * 50)
    
    repo = GitRepository("web-app")
    github_flow = GitHubFlowWorkflow(repo)
    
    # 开发者Carol开始功能开发
    print("\n👩‍💻 Carol开始功能开发:")
    feature_branch = github_flow.start_feature("dashboard")
    repo.commit("Create dashboard layout", "Carol", ["dashboard.html"])
    repo.commit("Add dashboard widgets", "Carol", ["dashboard.js"])
    repo.commit("Style dashboard components", "Carol", ["dashboard.css"])
    
    # 完成功能开发
    print("\n✅ Carol完成功能开发:")
    success = github_flow.finish_feature("dashboard", "Carol")
    
    # 开发者David开始另一个功能
    print("\n👨‍💻 David开始功能开发:")
    feature_branch = github_flow.start_feature("api-integration")
    repo.commit("Add API client", "David", ["api.js"])
    repo.commit("Implement data fetching", "David", ["data.js"])
    
    github_flow.finish_feature("api-integration", "David")
    
    # 显示仓库状态
    status = repo.get_repository_status()
    print(f"\n📊 仓库状态:")
    for key, value in status.items():
        print(f"  {key}: {value}")

def demonstrate_pull_requests():
    """演示拉取请求"""
    print("\n🔀 拉取请求演示")
    print("=" * 50)
    
    repo = GitRepository("demo-repo")
    
    # 创建功能分支
    feature_branch = repo.create_feature_branch("new-feature")
    repo.switch_branch(feature_branch)
    
    # 提交代码
    repo.commit("Add new feature", "Alice", ["feature.js"])
    repo.commit("Update tests", "Alice", ["test.js"])
    
    # 创建PR
    pr_id = repo.create_pull_request(
        title="Add new feature",
        description="This PR adds a new feature to improve user experience",
        source_branch=feature_branch,
        target_branch="main",
        author="Alice"
    )
    
    # 审核过程
    print("\n👀 审核过程:")
    repo.review_pull_request(pr_id, "Bob", True)
    repo.review_pull_request(pr_id, "Carol", False)
    repo.review_pull_request(pr_id, "David", True)
    
    # 修复问题后重新审核
    repo.commit("Fix review comments", "Alice", ["feature.js"])
    repo.review_pull_request(pr_id, "Carol", True)
    
    # 合并PR
    print("\n🔀 合并PR:")
    success = repo.merge_pull_request(pr_id)
    
    if success:
        print("✅ PR成功合并")
    else:
        print("❌ PR合并失败")

def demonstrate_branch_strategies():
    """演示分支策略"""
    print("\n🌿 分支策略演示")
    print("=" * 50)
    
    repo = GitRepository("strategy-demo")
    
    # 创建各种分支
    branches = [
        ("develop", BranchType.DEVELOP),
        ("feature/ui-update", BranchType.FEATURE),
        ("feature/api-v2", BranchType.FEATURE),
        ("release/v2.0.0", BranchType.RELEASE),
        ("hotfix/critical-bug", BranchType.HOTFIX)
    ]
    
    for branch_name, branch_type in branches:
        if branch_type == BranchType.DEVELOP:
            repo._create_branch(branch_name, branch_type, "main")
        elif branch_type == BranchType.FEATURE:
            repo.create_feature_branch(branch_name.replace("feature/", ""))
        elif branch_type == BranchType.RELEASE:
            repo.create_release_branch(branch_name.replace("release/", ""))
        elif branch_type == BranchType.HOTFIX:
            repo.create_hotfix_branch(branch_name.replace("hotfix/", ""))
    
    # 在不同分支提交
    repo.switch_branch("feature/ui-update")
    repo.commit("Update UI components", "UI Team")
    
    repo.switch_branch("feature/api-v2")
    repo.commit("Add new API endpoints", "Backend Team")
    
    repo.switch_branch("release/v2.0.0")
    repo.commit("Prepare for v2.0.0 release", "Release Team")
    
    repo.switch_branch("hotfix/critical-bug")
    repo.commit("Fix critical security bug", "Security Team")
    
    # 显示分支状态
    print("\n📊 分支状态:")
    for branch_name, branch in repo.branches.items():
        print(f"  {branch_name}:")
        print(f"    类型: {branch.type.value}")
        print(f"    提交数: {len(branch.commits)}")
        print(f"    基础分支: {branch.base_branch}")

def main():
    """主函数"""
    print("🔀 Git工作流演示")
    print("=" * 60)
    
    try:
        demonstrate_git_flow()
        demonstrate_github_flow()
        demonstrate_pull_requests()
        demonstrate_branch_strategies()
        
        print("\n✅ Git工作流演示完成!")
        print("\n📚 关键概念:")
        print("  - Git Flow: 严格的分支管理模型")
        print("  - GitHub Flow: 简化的分支模型")
        print("  - 功能分支: 独立的功能开发")
        print("  - 发布分支: 发布准备和测试")
        print("  - 热修复分支: 紧急修复")
        print("  - 拉取请求: 代码审核和合并")
        print("  - 分支策略: 适合团队的分支管理")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    main()
