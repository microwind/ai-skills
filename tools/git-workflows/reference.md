# Git工作流配置器参考文档

## Git工作流配置器概述

### 什么是Git工作流配置器
Git工作流配置器是一个专门用于设计、配置和管理Git工作流的工具。该工具支持多种主流工作流模式（Git Flow、GitHub Flow、GitLab Flow等），提供分支策略、代码审查、发布管理、团队协作等完整功能，帮助开发团队建立规范、高效的版本控制流程。

### 主要功能
- **工作流设计**: 支持多种工作流模式和自定义工作流
- **分支管理**: 完整的分支策略和保护规则
- **代码审查**: 自动化代码审查流程和质量检查
- **发布管理**: 版本控制、发布策略和自动化发布
- **团队协作**: 权限管理和协作规则
- **质量保证**: 代码质量标准和测试策略

## 工作流引擎

### 工作流配置器
```python
# git_workflow_engine.py
import os
import json
import yaml
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime

class WorkflowType(Enum):
    GIT_FLOW = "git_flow"
    GITHUB_FLOW = "github_flow"
    GITLAB_FLOW = "gitlab_flow"
    TRUNK_BASED = "trunk_based"
    FEATURE_BRANCH = "feature_branch"
    CUSTOM = "custom"

class MergeStrategy(Enum):
    MERGE_COMMIT = "merge_commit"
    SQUASH_MERGE = "squash_merge"
    REBASE_MERGE = "rebase_merge"
    CUSTOM = "custom"

class ProtectionLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"

@dataclass
class BranchConfig:
    name: str
    source_branch: str
    protection_level: ProtectionLevel
    merge_strategy: MergeStrategy
    auto_merge: bool = False
    required_reviewers: int = 1
    required_checks: List[str] = field(default_factory=list)
    force_push_allowed: bool = False
    delete_after_merge: bool = False

@dataclass
class ReviewConfig:
    required_reviewers: int = 1
    require_owner_review: bool = False
    require_code_owner_review: bool = False
    dismiss_stale_reviews: bool = True
    require_up_to_date: bool = True
    auto_assign_reviewers: bool = False
    reviewer_selection: str = "random"  # random, rotate, skill_based
    review_timeout_hours: int = 72

@dataclass
class ReleaseConfig:
    version_scheme: str = "semver"  # semver, custom
    auto_tag: bool = True
    tag_format: str = "v{version}"
    changelog_auto_generate: bool = True
    release_branch_pattern: str = "release/*"
    hotfix_branch_pattern: str = "hotfix/*"
    release_checks: List[str] = field(default_factory=list)

@dataclass
class WorkflowConfig:
    name: str
    workflow_type: WorkflowType
    main_branch: str = "main"
    develop_branch: str = "develop"
    branches: Dict[str, BranchConfig] = field(default_factory=dict)
    review_config: ReviewConfig = field(default_factory=ReviewConfig)
    release_config: ReleaseConfig = field(default_factory=ReleaseConfig)
    custom_rules: Dict[str, Any] = field(default_factory=dict)

class GitWorkflowEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflows: Dict[str, WorkflowConfig] = {}
        self.templates = self._load_workflow_templates()
    
    def _load_workflow_templates(self) -> Dict[WorkflowType, WorkflowConfig]:
        """加载工作流模板"""
        return {
            WorkflowType.GIT_FLOW: self._create_git_flow_template(),
            WorkflowType.GITHUB_FLOW: self._create_github_flow_template(),
            WorkflowType.GITLAB_FLOW: self._create_gitlab_flow_template(),
            WorkflowType.TRUNK_BASED: self._create_trunk_based_template(),
            WorkflowType.FEATURE_BRANCH: self._create_feature_branch_template()
        }
    
    def _create_git_flow_template(self) -> WorkflowConfig:
        """创建Git Flow模板"""
        branches = {
            "main": BranchConfig(
                name="main",
                source_branch="",
                protection_level=ProtectionLevel.STRICT,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=2,
                required_checks=["ci/build", "ci/test"],
                force_push_allowed=False,
                delete_after_merge=False
            ),
            "develop": BranchConfig(
                name="develop",
                source_branch="main",
                protection_level=ProtectionLevel.STANDARD,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build"],
                force_push_allowed=False,
                delete_after_merge=False
            ),
            "feature": BranchConfig(
                name="feature/*",
                source_branch="develop",
                protection_level=ProtectionLevel.BASIC,
                merge_strategy=MergeStrategy.SQUASH_MERGE,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build"],
                force_push_allowed=True,
                delete_after_merge=True
            ),
            "release": BranchConfig(
                name="release/*",
                source_branch="develop",
                protection_level=ProtectionLevel.STANDARD,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=2,
                required_checks=["ci/build", "ci/test", "ci/security"],
                force_push_allowed=False,
                delete_after_merge=True
            ),
            "hotfix": BranchConfig(
                name="hotfix/*",
                source_branch="main",
                protection_level=ProtectionLevel.STRICT,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=2,
                required_checks=["ci/build", "ci/test", "ci/security"],
                force_push_allowed=False,
                delete_after_merge=True
            )
        }
        
        return WorkflowConfig(
            name="Git Flow",
            workflow_type=WorkflowType.GIT_FLOW,
            main_branch="main",
            develop_branch="develop",
            branches=branches,
            review_config=ReviewConfig(
                required_reviewers=2,
                require_owner_review=True,
                dismiss_stale_reviews=True,
                require_up_to_date=True
            ),
            release_config=ReleaseConfig(
                version_scheme="semver",
                auto_tag=True,
                changelog_auto_generate=True
            )
        )
    
    def _create_github_flow_template(self) -> WorkflowConfig:
        """创建GitHub Flow模板"""
        branches = {
            "main": BranchConfig(
                name="main",
                source_branch="",
                protection_level=ProtectionLevel.STRICT,
                merge_strategy=MergeStrategy.SQUASH_MERGE,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build", "ci/test"],
                force_push_allowed=False,
                delete_after_merge=False
            ),
            "feature": BranchConfig(
                name="feature/*",
                source_branch="main",
                protection_level=ProtectionLevel.BASIC,
                merge_strategy=MergeStrategy.SQUASH_MERGE,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build"],
                force_push_allowed=True,
                delete_after_merge=True
            )
        }
        
        return WorkflowConfig(
            name="GitHub Flow",
            workflow_type=WorkflowType.GITHUB_FLOW,
            main_branch="main",
            branches=branches,
            review_config=ReviewConfig(
                required_reviewers=1,
                dismiss_stale_reviews=True,
                require_up_to_date=True
            ),
            release_config=ReleaseConfig(
                version_scheme="semver",
                auto_tag=True
            )
        )
    
    def _create_gitlab_flow_template(self) -> WorkflowConfig:
        """创建GitLab Flow模板"""
        branches = {
            "main": BranchConfig(
                name="main",
                source_branch="",
                protection_level=ProtectionLevel.STRICT,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=2,
                required_checks=["ci/build", "ci/test"],
                force_push_allowed=False,
                delete_after_merge=False
            ),
            "develop": BranchConfig(
                name="develop",
                source_branch="main",
                protection_level=ProtectionLevel.STANDARD,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build"],
                force_push_allowed=False,
                delete_after_merge=False
            ),
            "feature": BranchConfig(
                name="feature/*",
                source_branch="develop",
                protection_level=ProtectionLevel.BASIC,
                merge_strategy=MergeStrategy.SQUASH_MERGE,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build"],
                force_push_allowed=True,
                delete_after_merge=True
            ),
            "production": BranchConfig(
                name="production",
                source_branch="main",
                protection_level=ProtectionLevel.STRICT,
                merge_strategy=MergeStrategy.MERGE_COMMIT,
                auto_merge=False,
                required_reviewers=2,
                required_checks=["ci/build", "ci/test", "ci/security"],
                force_push_allowed=False,
                delete_after_merge=False
            )
        }
        
        return WorkflowConfig(
            name="GitLab Flow",
            workflow_type=WorkflowType.GITLAB_FLOW,
            main_branch="main",
            develop_branch="develop",
            branches=branches,
            review_config=ReviewConfig(
                required_reviewers=2,
                require_owner_review=True,
                dismiss_stale_reviews=True
            ),
            release_config=ReleaseConfig(
                version_scheme="semver",
                auto_tag=True,
                changelog_auto_generate=True
            )
        )
    
    def _create_trunk_based_template(self) -> WorkflowConfig:
        """创建Trunk Based模板"""
        branches = {
            "main": BranchConfig(
                name="main",
                source_branch="",
                protection_level=ProtectionLevel.STANDARD,
                merge_strategy=MergeStrategy.REBASE_MERGE,
                auto_merge=True,
                required_reviewers=1,
                required_checks=["ci/build", "ci/test"],
                force_push_allowed=False,
                delete_after_merge=False
            )
        }
        
        return WorkflowConfig(
            name="Trunk Based Development",
            workflow_type=WorkflowType.TRUNK_BASED,
            main_branch="main",
            branches=branches,
            review_config=ReviewConfig(
                required_reviewers=1,
                dismiss_stale_reviews=True,
                require_up_to_date=True,
                review_timeout_hours=24
            ),
            release_config=ReleaseConfig(
                version_scheme="semver",
                auto_tag=True
            )
        )
    
    def _create_feature_branch_template(self) -> WorkflowConfig:
        """创建Feature Branch模板"""
        branches = {
            "main": BranchConfig(
                name="main",
                source_branch="",
                protection_level=ProtectionLevel.STANDARD,
                merge_strategy=MergeStrategy.SQUASH_MERGE,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build", "ci/test"],
                force_push_allowed=False,
                delete_after_merge=False
            ),
            "feature": BranchConfig(
                name="feature/*",
                source_branch="main",
                protection_level=ProtectionLevel.BASIC,
                merge_strategy=MergeStrategy.SQUASH_MERGE,
                auto_merge=False,
                required_reviewers=1,
                required_checks=["ci/build"],
                force_push_allowed=True,
                delete_after_merge=True
            )
        }
        
        return WorkflowConfig(
            name="Feature Branch Workflow",
            workflow_type=WorkflowType.FEATURE_BRANCH,
            main_branch="main",
            branches=branches,
            review_config=ReviewConfig(
                required_reviewers=1,
                dismiss_stale_reviews=True
            ),
            release_config=ReleaseConfig(
                version_scheme="semver",
                auto_tag=True
            )
        )
    
    def create_workflow(self, name: str, workflow_type: WorkflowType, 
                       customizations: Optional[Dict[str, Any]] = None) -> WorkflowConfig:
        """创建工作流"""
        if workflow_type not in self.templates:
            raise ValueError(f"不支持的工作流类型: {workflow_type}")
        
        # 复制模板
        workflow = self.templates[workflow_type]
        workflow_dict = asdict(workflow)
        workflow_dict['name'] = name
        
        # 应用自定义配置
        if customizations:
            self._apply_customizations(workflow_dict, customizations)
        
        # 创建工作流配置
        new_workflow = WorkflowConfig(**workflow_dict)
        self.workflows[name] = new_workflow
        
        self.logger.info(f"创建工作流: {name} ({workflow_type.value})")
        return new_workflow
    
    def _apply_customizations(self, workflow_dict: Dict[str, Any], 
                            customizations: Dict[str, Any]):
        """应用自定义配置"""
        for key, value in customizations.items():
            if key in workflow_dict:
                if isinstance(value, dict) and isinstance(workflow_dict[key], dict):
                    workflow_dict[key].update(value)
                else:
                    workflow_dict[key] = value
    
    def get_workflow(self, name: str) -> Optional[WorkflowConfig]:
        """获取工作流配置"""
        return self.workflows.get(name)
    
    def update_workflow(self, name: str, updates: Dict[str, Any]) -> bool:
        """更新工作流配置"""
        if name not in self.workflows:
            return False
        
        workflow = self.workflows[name]
        workflow_dict = asdict(workflow)
        self._apply_customizations(workflow_dict, updates)
        
        # 重新创建工作流对象
        updated_workflow = WorkflowConfig(**workflow_dict)
        self.workflows[name] = updated_workflow
        
        self.logger.info(f"更新工作流: {name}")
        return True
    
    def delete_workflow(self, name: str) -> bool:
        """删除工作流"""
        if name in self.workflows:
            del self.workflows[name]
            self.logger.info(f"删除工作流: {name}")
            return True
        return False
    
    def validate_workflow(self, workflow: WorkflowConfig) -> List[str]:
        """验证工作流配置"""
        errors = []
        
        # 验证分支配置
        for branch_name, branch_config in workflow.branches.items():
            if not branch_config.name:
                errors.append(f"分支 {branch_name} 名称不能为空")
            
            if branch_config.required_reviewers < 0:
                errors.append(f"分支 {branch_name} 审查者数量不能为负数")
            
            if branch_config.protection_level == ProtectionLevel.NONE and branch_config.required_reviewers > 0:
                errors.append(f"分支 {branch_name} 保护级别为None但设置了审查者要求")
        
        # 验证审查配置
        if workflow.review_config.required_reviewers < 0:
            errors.append("审查配置中审查者数量不能为负数")
        
        if workflow.review_config.review_timeout_hours < 0:
            errors.append("审查配置中超时时间不能为负数")
        
        # 验证发布配置
        if workflow.release_config.version_scheme not in ["semver", "custom"]:
            errors.append("发布配置中版本方案必须是semver或custom")
        
        return errors
    
    def generate_workflow_config(self, workflow_name: str, 
                               output_path: str = "workflow_config.yaml") -> str:
        """生成工作流配置文件"""
        if workflow_name not in self.workflows:
            raise ValueError(f"工作流不存在: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        
        # 验证配置
        errors = self.validate_workflow(workflow)
        if errors:
            raise ValueError(f"工作流配置无效: {', '.join(errors)}")
        
        # 转换为可序列化的字典
        config_dict = asdict(workflow)
        config_dict['workflow_type'] = workflow.workflow_type.value
        config_dict['branches'] = {
            name: asdict(branch) for name, branch in workflow.branches.items()
        }
        config_dict['branches'] = {
            name: {
                **branch,
                'protection_level': branch['protection_level'].value,
                'merge_strategy': branch['merge_strategy'].value
            }
            for name, branch in config_dict['branches'].items()
        }
        config_dict['review_config'] = asdict(workflow.review_config)
        config_dict['release_config'] = asdict(workflow.release_config)
        
        # 生成YAML配置
        yaml_content = yaml.dump(config_dict, default_flow_style=False, 
                               allow_unicode=True, sort_keys=False)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        self.logger.info(f"工作流配置已生成: {output_path}")
        return yaml_content
    
    def load_workflow_from_file(self, config_path: str) -> WorkflowConfig:
        """从文件加载工作流配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # 转换枚举类型
        config_dict['workflow_type'] = WorkflowType(config_dict['workflow_type'])
        
        for branch_name, branch_config in config_dict['branches'].items():
            branch_config['protection_level'] = ProtectionLevel(branch_config['protection_level'])
            branch_config['merge_strategy'] = MergeStrategy(branch_config['merge_strategy'])
        
        # 创建工作流配置
        workflow = WorkflowConfig(**config_dict)
        self.workflows[workflow.name] = workflow
        
        self.logger.info(f"从文件加载工作流: {workflow.name}")
        return workflow
    
    def list_workflows(self) -> List[str]:
        """列出所有工作流"""
        return list(self.workflows.keys())
    
    def get_workflow_summary(self, workflow_name: str) -> Dict[str, Any]:
        """获取工作流摘要"""
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            return {}
        
        return {
            "name": workflow.name,
            "type": workflow.workflow_type.value,
            "main_branch": workflow.main_branch,
            "develop_branch": workflow.develop_branch,
            "branch_count": len(workflow.branches),
            "required_reviewers": workflow.review_config.required_reviewers,
            "auto_tag": workflow.release_config.auto_tag,
            "version_scheme": workflow.release_config.version_scheme
        }

# 使用示例
engine = GitWorkflowEngine()

# 创建Git Flow工作流
git_flow = engine.create_workflow(
    name="my-project-git-flow",
    workflow_type=WorkflowType.GIT_FLOW,
    customizations={
        "main_branch": "main",
        "develop_branch": "develop",
        "review_config": {
            "required_reviewers": 2,
            "require_owner_review": True
        }
    }
)

# 创建GitHub Flow工作流
github_flow = engine.create_workflow(
    name="my-project-github-flow",
    workflow_type=WorkflowType.GITHUB_FLOW,
    customizations={
        "review_config": {
            "required_reviewers": 1,
            "auto_assign_reviewers": True
        }
    }
)

# 生成配置文件
engine.generate_workflow_config("my-project-git-flow", "git-flow-config.yaml")
engine.generate_workflow_config("my-project-github-flow", "github-flow-config.yaml")

# 列出工作流
workflows = engine.list_workflows()
print(f"可用工作流: {workflows}")

# 获取工作流摘要
for workflow_name in workflows:
    summary = engine.get_workflow_summary(workflow_name)
    print(f"\n工作流: {summary['name']}")
    print(f"类型: {summary['type']}")
    print(f"主分支: {summary['main_branch']}")
    print(f"分支数: {summary['branch_count']}")
    print(f"审查者数: {summary['required_reviewers']}")
```

## 分支管理器

### 分支策略管理
```python
# branch_manager.py
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class BranchType(Enum):
    MAIN = "main"
    DEVELOP = "develop"
    FEATURE = "feature"
    RELEASE = "release"
    HOTFIX = "hotfix"
    CUSTOM = "custom"

@dataclass
class BranchRule:
    pattern: str
    branch_type: BranchType
    source_branch: str
    target_branches: List[str]
    protection_level: str
    auto_delete: bool = False
    merge_strategy: str = "merge"

class BranchManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.branch_rules: Dict[str, BranchRule] = {}
        self.branch_protections: Dict[str, Dict[str, Any]] = {}
    
    def add_branch_rule(self, rule: BranchRule):
        """添加分支规则"""
        self.branch_rules[rule.pattern] = rule
        self.logger.info(f"添加分支规则: {rule.pattern} -> {rule.branch_type.value}")
    
    def remove_branch_rule(self, pattern: str):
        """移除分支规则"""
        if pattern in self.branch_rules:
            del self.branch_rules[pattern]
            self.logger.info(f"移除分支规则: {pattern}")
    
    def get_branch_type(self, branch_name: str) -> Optional[BranchType]:
        """获取分支类型"""
        for pattern, rule in self.branch_rules.items():
            if re.match(pattern, branch_name):
                return rule.branch_type
        return None
    
    def get_branch_rule(self, branch_name: str) -> Optional[BranchRule]:
        """获取分支规则"""
        for pattern, rule in self.branch_rules.items():
            if re.match(pattern, branch_name):
                return rule
        return None
    
    def validate_branch_name(self, branch_name: str) -> Tuple[bool, str]:
        """验证分支名称"""
        if not branch_name:
            return False, "分支名称不能为空"
        
        # 检查是否匹配任何规则
        branch_type = self.get_branch_type(branch_name)
        if not branch_type:
            return False, "分支名称不匹配任何规则"
        
        # 检查分支名称格式
        if branch_type == BranchType.FEATURE:
            if not re.match(r'feature/[a-zA-Z0-9_-]+', branch_name):
                return False, "特性分支名称格式应为: feature/名称"
        elif branch_type == BranchType.RELEASE:
            if not re.match(r'release/\d+\.\d+\.\d+', branch_name):
                return False, "发布分支名称格式应为: release/版本号"
        elif branch_type == BranchType.HOTFIX:
            if not re.match(r'hotfix/[a-zA-Z0-9_-]+', branch_name):
                return False, "热修复分支名称格式应为: hotfix/名称"
        
        return True, ""
    
    def get_source_branch(self, branch_name: str) -> Optional[str]:
        """获取源分支"""
        rule = self.get_branch_rule(branch_name)
        return rule.source_branch if rule else None
    
    def get_target_branches(self, branch_name: str) -> List[str]:
        """获取目标分支"""
        rule = self.get_branch_rule(branch_name)
        return rule.target_branches if rule else []
    
    def should_auto_delete(self, branch_name: str) -> bool:
        """是否自动删除"""
        rule = self.get_branch_rule(branch_name)
        return rule.auto_delete if rule else False
    
    def get_merge_strategy(self, branch_name: str) -> str:
        """获取合并策略"""
        rule = self.get_branch_rule(branch_name)
        return rule.merge_strategy if rule else "merge"
    
    def set_branch_protection(self, branch_pattern: str, protection: Dict[str, Any]):
        """设置分支保护"""
        self.branch_protections[branch_pattern] = protection
        self.logger.info(f"设置分支保护: {branch_pattern}")
    
    def get_branch_protection(self, branch_name: str) -> Optional[Dict[str, Any]]:
        """获取分支保护配置"""
        for pattern, protection in self.branch_protections.items():
            if re.match(pattern, branch_name):
                return protection
        return None
    
    def validate_branch_protection(self, branch_name: str, 
                                 protection: Dict[str, Any]) -> List[str]:
        """验证分支保护配置"""
        errors = []
        
        # 检查必需字段
        required_fields = ["required_reviewers", "require_status_checks"]
        for field in required_fields:
            if field not in protection:
                errors.append(f"缺少必需字段: {field}")
        
        # 检查审查者数量
        if "required_reviewers" in protection:
            if protection["required_reviewers"] < 0:
                errors.append("审查者数量不能为负数")
            if protection["required_reviewers"] > 10:
                errors.append("审查者数量不能超过10")
        
        # 检查状态检查
        if "require_status_checks" in protection:
            status_checks = protection["require_status_checks"]
            if not isinstance(status_checks, list):
                errors.append("状态检查必须是列表")
            elif len(status_checks) == 0:
                errors.append("状态检查列表不能为空")
        
        return errors
    
    def generate_branch_config(self, output_path: str = "branch_config.yaml") -> str:
        """生成分支配置文件"""
        import yaml
        
        config = {
            "branch_rules": {},
            "branch_protections": self.branch_protections
        }
        
        for pattern, rule in self.branch_rules.items():
            config["branch_rules"][pattern] = {
                "branch_type": rule.branch_type.value,
                "source_branch": rule.source_branch,
                "target_branches": rule.target_branches,
                "protection_level": rule.protection_level,
                "auto_delete": rule.auto_delete,
                "merge_strategy": rule.merge_strategy
            }
        
        yaml_content = yaml.dump(config, default_flow_style=False, 
                               allow_unicode=True, sort_keys=False)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        self.logger.info(f"分支配置已生成: {output_path}")
        return yaml_content
    
    def load_branch_config(self, config_path: str):
        """加载分支配置"""
        import yaml
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 加载分支规则
        if "branch_rules" in config:
            self.branch_rules.clear()
            for pattern, rule_config in config["branch_rules"].items():
                rule = BranchRule(
                    pattern=pattern,
                    branch_type=BranchType(rule_config["branch_type"]),
                    source_branch=rule_config["source_branch"],
                    target_branches=rule_config["target_branches"],
                    protection_level=rule_config["protection_level"],
                    auto_delete=rule_config.get("auto_delete", False),
                    merge_strategy=rule_config.get("merge_strategy", "merge")
                )
                self.branch_rules[pattern] = rule
        
        # 加载分支保护
        if "branch_protections" in config:
            self.branch_protections = config["branch_protections"]
        
        self.logger.info(f"分支配置已加载: {config_path}")

# 使用示例
manager = BranchManager()

# 添加分支规则
manager.add_branch_rule(BranchRule(
    pattern="main",
    branch_type=BranchType.MAIN,
    source_branch="",
    target_branches=[],
    protection_level="strict",
    auto_delete=False,
    merge_strategy="merge"
))

manager.add_branch_rule(BranchRule(
    pattern="develop",
    branch_type=BranchType.DEVELOP,
    source_branch="main",
    target_branches=["main"],
    protection_level="standard",
    auto_delete=False,
    merge_strategy="merge"
))

manager.add_branch_rule(BranchRule(
    pattern="feature/.*",
    branch_type=BranchType.FEATURE,
    source_branch="develop",
    target_branches=["develop"],
    protection_level="basic",
    auto_delete=True,
    merge_strategy="squash"
))

manager.add_branch_rule(BranchRule(
    pattern="release/.*",
    branch_type=BranchType.RELEASE,
    source_branch="develop",
    target_branches=["main", "develop"],
    protection_level="standard",
    auto_delete=True,
    merge_strategy="merge"
))

manager.add_branch_rule(BranchRule(
    pattern="hotfix/.*",
    branch_type=BranchType.HOTFIX,
    source_branch="main",
    target_branches=["main", "develop"],
    protection_level="strict",
    auto_delete=True,
    merge_strategy="merge"
))

# 设置分支保护
manager.set_branch_protection("main", {
    "required_reviewers": 2,
    "require_status_checks": ["ci/build", "ci/test", "ci/security"],
    "enforce_admins": True,
    "required_linear_history": True,
    "allow_force_pushes": False,
    "allow_deletions": False
})

manager.set_branch_protection("develop", {
    "required_reviewers": 1,
    "require_status_checks": ["ci/build", "ci/test"],
    "enforce_admins": False,
    "required_linear_history": False,
    "allow_force_pushes": True,
    "allow_deletions": False
})

# 验证分支名称
branch_names = ["main", "develop", "feature/user-auth", "release/1.0.0", "hotfix/critical-bug"]
for branch_name in branch_names:
    is_valid, message = manager.validate_branch_name(branch_name)
    print(f"分支 {branch_name}: {'有效' if is_valid else '无效'}")
    if not is_valid:
        print(f"  错误: {message}")

# 生成分支配置
manager.generate_branch_config("branch_config.yaml")
print("分支配置已生成")
```

## 参考资源

### Git工作流文档
- [Git Flow工作流](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [GitHub Flow工作流](https://guides.github.com/introduction/flow/)
- [GitLab Flow工作流](https://docs.gitlab.com/ee/topics/gitlab_flow.html)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)

### 分支策略
- [Git分支策略比较](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [分支保护规则](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Pull Request最佳实践](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)

### 代码审查
- [代码审查最佳实践](https://www.atlassian.com/agile/software-development/code-reviews)
- [Pull Request审查流程](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests)
- [代码审查工具](https://github.com/features/code-review)

### 发布管理
- [语义化版本控制](https://semver.org/)
- [Git标签管理](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [发布管理最佳实践](https://docs.github.com/en/repositories/releasing-projects-to-the-public/generating-releases-on-github)

### CI/CD集成
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [GitLab CI/CD文档](https://docs.gitlab.com/ee/ci/)
- [Jenkins Pipeline文档](https://www.jenkins.io/doc/book/pipeline/)
