# 变更日志生成器参考文档

## 变更日志生成器概述

### 什么是变更日志生成器
变更日志生成器是一个自动化工具，用于从版本控制系统（如Git）的提交历史中提取、分类和格式化变更信息，生成结构化的变更日志文档。该工具支持多种提交格式规范（如Conventional Commits），提供灵活的模板系统和自定义分类规则，帮助项目维护者快速生成专业、一致的变更日志。

### 主要功能
- **Git集成**: 自动从Git仓库提取提交信息、标签和分支信息
- **提交解析**: 支持Conventional Commits等多种提交格式规范
- **智能分类**: 根据提交类型自动分类变更（新功能、修复、文档等）
- **模板系统**: 支持Markdown、HTML、JSON等多种输出格式
- **版本管理**: 支持语义化版本管理和版本范围过滤
- **自定义规则**: 灵活的过滤、排序和分组规则
- **多语言支持**: 支持国际化和本地化配置
- **自动化发布**: 支持自动发布到GitHub Release等平台

## Git集成

### Git仓库分析器
```python
# git_analyzer.py
import git
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class CommitType(Enum):
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
    SECURITY = "security"

@dataclass
class CommitInfo:
    hash: str
    short_hash: str
    message: str
    body: str
    author_name: str
    author_email: str
    author_date: datetime
    commit_date: datetime
    type: Optional[CommitType]
    scope: Optional[str]
    breaking: bool
    issues: List[str]

@dataclass
class TagInfo:
    name: str
    commit_hash: str
    date: datetime
    message: str

class GitAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.repo = None
        self.conventional_pattern = re.compile(
            r'^(?P<type>\w+)(\((?P<scope>.+)\))?(?P<breaking>!)?:\s*(?P<description>.+)$'
        )
        self.issue_pattern = re.compile(r'(?i)(?:fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved)\s+(?:#|issue\s+)(\d+)')
    
    def open_repository(self) -> bool:
        """打开Git仓库"""
        try:
            self.repo = git.Repo(self.repo_path)
            return True
        except Exception as e:
            print(f"打开Git仓库失败: {e}")
            return False
    
    def get_commits_between_tags(self, from_tag: str = None, to_tag: str = None) -> List[CommitInfo]:
        """获取两个标签之间的提交"""
        try:
            if from_tag and to_tag:
                # 获取两个标签之间的提交
                from_commit = self.repo.tags[from_tag].commit
                to_commit = self.repo.tags[to_tag].commit
                commits = list(self.repo.iter_commits(f"{from_commit}..{to_commit}"))
            elif from_tag:
                # 从指定标签到最新提交
                from_commit = self.repo.tags[from_tag].commit
                commits = list(self.repo.iter_commits(f"{from_commit}..HEAD"))
            elif to_tag:
                # 从开始到指定标签
                to_commit = self.repo.tags[to_tag].commit
                commits = list(self.repo.iter_commits(to_commit))
            else:
                # 所有提交
                commits = list(self.repo.iter_commits())
            
            return [self._parse_commit(commit) for commit in commits]
        
        except Exception as e:
            print(f"获取提交失败: {e}")
            return []
    
    def get_commits_since_date(self, since_date: datetime) -> List[CommitInfo]:
        """获取指定日期之后的提交"""
        try:
            commits = list(self.repo.iter_commits(since=since_date))
            return [self._parse_commit(commit) for commit in commits]
        
        except Exception as e:
            print(f"获取提交失败: {e}")
            return []
    
    def get_all_tags(self) -> List[TagInfo]:
        """获取所有标签"""
        try:
            tags = []
            for tag in self.repo.tags:
                tag_info = TagInfo(
                    name=tag.name,
                    commit_hash=tag.commit.hexsha,
                    date=datetime.fromtimestamp(tag.commit.committed_date),
                    message=tag.tag.message if tag.tag else tag.name
                )
                tags.append(tag_info)
            
            # 按日期排序
            tags.sort(key=lambda x: x.date, reverse=True)
            return tags
        
        except Exception as e:
            print(f"获取标签失败: {e}")
            return []
    
    def get_latest_tag(self) -> Optional[TagInfo]:
        """获取最新标签"""
        tags = self.get_all_tags()
        return tags[0] if tags else None
    
    def _parse_commit(self, commit) -> CommitInfo:
        """解析提交信息"""
        # 基本信息
        commit_info = CommitInfo(
            hash=commit.hexsha,
            short_hash=commit.hexsha[:7],
            message=commit.message.strip(),
            body=commit.message.strip(),
            author_name=commit.author.name,
            author_email=commit.author.email,
            author_date=datetime.fromtimestamp(commit.authored_date),
            commit_date=datetime.fromtimestamp(commit.committed_date),
            type=None,
            scope=None,
            breaking=False,
            issues=[]
        )
        
        # 解析Conventional Commits格式
        self._parse_conventional_commit(commit_info)
        
        # 提取问题引用
        self._extract_issues(commit_info)
        
        return commit_info
    
    def _parse_conventional_commit(self, commit_info: CommitInfo):
        """解析Conventional Commits格式"""
        lines = commit_info.message.split('\n')
        first_line = lines[0] if lines else ""
        
        match = self.conventional_pattern.match(first_line)
        if match:
            groups = match.groupdict()
            
            # 提交类型
            type_str = groups.get('type', '').lower()
            try:
                commit_info.type = CommitType(type_str)
            except ValueError:
                # 自定义类型
                commit_info.type = type_str
            
            # 提交范围
            commit_info.scope = groups.get('scope')
            
            # 破坏性变更
            commit_info.breaking = bool(groups.get('breaking'))
        
        # 检查body中的破坏性变更
        if not commit_info.breaking and commit_info.body:
            breaking_pattern = re.compile(r'^BREAKING CHANGE:\s*(.+)$', re.MULTILINE)
            if breaking_pattern.search(commit_info.body):
                commit_info.breaking = True
    
    def _extract_issues(self, commit_info: CommitInfo):
        """提取问题引用"""
        issues = self.issue_pattern.findall(commit_info.message)
        commit_info.issues = list(set(issues))  # 去重
    
    def get_file_changes(self, commit_hash: str) -> Dict[str, Any]:
        """获取文件变更信息"""
        try:
            commit = self.repo.commit(commit_hash)
            
            changes = {
                'added': [],
                'modified': [],
                'deleted': [],
                'renamed': []
            }
            
            for item in commit.diff(commit.parents[0] if commit.parents else None):
                if item.new_file:
                    changes['added'].append(item.a_path)
                elif item.deleted_file:
                    changes['deleted'].append(item.a_path)
                elif item.renamed_file:
                    changes['renamed'].append((item.a_path, item.b_path))
                else:
                    changes['modified'].append(item.a_path)
            
            return changes
        
        except Exception as e:
            print(f"获取文件变更失败: {e}")
            return {}
    
    def get_contributors(self, since_date: datetime = None) -> List[Dict[str, Any]]:
        """获取贡献者信息"""
        try:
            commits = list(self.repo.iter_commits(since=since_date) if since_date else self.repo.iter_commits())
            
            contributors = {}
            for commit in commits:
                author = commit.author
                if author.name not in contributors:
                    contributors[author.name] = {
                        'name': author.name,
                        'email': author.email,
                        'commits': 0,
                        'first_commit': datetime.fromtimestamp(commit.authored_date),
                        'last_commit': datetime.fromtimestamp(commit.authored_date)
                    }
                
                contributors[author.name]['commits'] += 1
                
                commit_date = datetime.fromtimestamp(commit.authored_date)
                if commit_date < contributors[author.name]['first_commit']:
                    contributors[author.name]['first_commit'] = commit_date
                if commit_date > contributors[author.name]['last_commit']:
                    contributors[author.name]['last_commit'] = commit_date
            
            return list(contributors.values())
        
        except Exception as e:
            print(f"获取贡献者失败: {e}")
            return []

# 使用示例
analyzer = GitAnalyzer("/path/to/your/repo")

if analyzer.open_repository():
    # 获取最新标签
    latest_tag = analyzer.get_latest_tag()
    print(f"最新标签: {latest_tag.name if latest_tag else 'None'}")
    
    # 获取两个标签之间的提交
    commits = analyzer.get_commits_between_tags("v1.0.0", "v1.1.0")
    print(f"找到 {len(commits)} 个提交")
    
    # 显示前几个提交
    for i, commit in enumerate(commits[:5]):
        print(f"\n提交 {i+1}:")
        print(f"  哈希: {commit.short_hash}")
        print(f"  类型: {commit.type}")
        print(f"  范围: {commit.scope}")
        print(f"  描述: {commit.message}")
        print(f"  作者: {commit.author_name}")
        print(f"  日期: {commit.commit_date}")
        print(f"  破坏性: {commit.breaking}")
        print(f"  问题: {commit.issues}")
    
    # 获取贡献者
    contributors = analyzer.get_contributors()
    print(f"\n贡献者数量: {len(contributors)}")
```

## 提交解析

### Conventional Commits解析器
```python
# commit_parser.py
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ConventionalType(Enum):
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    BUILD = "build"
    CI = "ci"
    CHORE = "chore"
    REVERT = "revert"

@dataclass
class ParsedCommit:
    type: str
    scope: Optional[str]
    breaking: bool
    description: str
    body: str
    footer: Dict[str, str]
    issues: List[str]
    raw_message: str

class ConventionalCommitsParser:
    def __init__(self):
        # 主模式匹配
        self.header_pattern = re.compile(
            r'^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<description>[^\n]+)'
        )
        
        # 破坏性变更模式
        self.breaking_pattern = re.compile(
            r'^BREAKING[ -]CHANGE:\s*(?P<description>.+)$',
            re.MULTILINE
        )
        
        # 页脚模式
        self.footer_pattern = re.compile(
            r'^(?P<token>[A-Z][A-Za-z-]+)(?:\s+#(?P<value>\d+))?\s*:\s*(?P<description>.+)$',
            re.MULTILINE
        )
        
        # 问题引用模式
        self.issue_pattern = re.compile(
            r'(?i)(?:clos(?:e|es|ed)|fix(?:es|ed)?|resolv(?:e|es|ed))\s+(?:#|issue\s+)(?P<issue>\d+)'
        )
        
        # 类型映射
        self.type_mapping = {
            'feature': ConventionalType.FEAT,
            'feat': ConventionalType.FEAT,
            'fix': ConventionalType.FIX,
            'docs': ConventionalType.DOCS,
            'doc': ConventionalType.DOCS,
            'style': ConventionalType.STYLE,
            'refactor': ConventionalType.REFACTOR,
            'perf': ConventionalType.PERF,
            'test': ConventionalType.TEST,
            'tests': ConventionalType.TEST,
            'build': ConventionalType.BUILD,
            'ci': ConventionalType.CI,
            'chore': ConventionalType.CHORE,
            'revert': ConventionalType.REVERT
        }
    
    def parse(self, message: str) -> ParsedCommit:
        """解析Conventional Commits格式的提交信息"""
        lines = message.strip().split('\n')
        
        # 解析头部
        header_line = lines[0] if lines else ""
        header_match = self.header_pattern.match(header_line)
        
        if not header_match:
            # 非Conventional Commits格式
            return ParsedCommit(
                type="other",
                scope=None,
                breaking=False,
                description=header_line,
                body="\n".join(lines[1:]) if len(lines) > 1 else "",
                footer={},
                issues=[],
                raw_message=message
            )
        
        groups = header_match.groupdict()
        
        # 提取类型
        raw_type = groups.get('type', '').lower()
        type_value = self.type_mapping.get(raw_type, raw_type)
        
        # 提取范围
        scope = groups.get('scope')
        
        # 提取破坏性变更标记
        breaking = bool(groups.get('breaking'))
        
        # 提取描述
        description = groups.get('description', '')
        
        # 解析主体和页脚
        body_text = "\n".join(lines[1:]) if len(lines) > 1 else ""
        body, footer = self._parse_body_and_footer(body_text)
        
        # 检查破坏性变更
        breaking_changes = self.breaking_pattern.findall(body_text)
        if breaking_changes:
            breaking = True
            footer['BREAKING CHANGE'] = '\n'.join(breaking_changes)
        
        # 提取问题引用
        issues = self._extract_issues(message)
        
        return ParsedCommit(
            type=type_value.value if isinstance(type_value, ConventionalType) else type_value,
            scope=scope,
            breaking=breaking,
            description=description,
            body=body,
            footer=footer,
            issues=issues,
            raw_message=message
        )
    
    def _parse_body_and_footer(self, text: str) -> Tuple[str, Dict[str, str]]:
        """解析主体和页脚"""
        if not text:
            return "", {}
        
        # 分割主体和页脚
        lines = text.split('\n')
        body_lines = []
        footer_lines = []
        
        in_footer = False
        for line in lines:
            line = line.strip()
            if not line:
                if in_footer:
                    continue
                else:
                    body_lines.append(line)
                    continue
            
            # 检查是否是页脚
            if self.footer_pattern.match(line):
                in_footer = True
                footer_lines.append(line)
            elif in_footer:
                footer_lines.append(line)
            else:
                body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        footer_text = '\n'.join(footer_lines)
        
        # 解析页脚
        footer = {}
        if footer_text:
            footer_matches = self.footer_pattern.finditer(footer_text)
            for match in footer_matches:
                token = match.group('token')
                value = match.group('value') or ""
                description = match.group('description')
                
                if value:
                    footer[f"{token} #{value}"] = description
                else:
                    footer[token] = description
        
        return body, footer
    
    def _extract_issues(self, message: str) -> List[str]:
        """提取问题引用"""
        issues = []
        matches = self.issue_pattern.finditer(message)
        for match in matches:
            issue = match.group('issue')
            if issue and issue not in issues:
                issues.append(issue)
        return issues
    
    def validate(self, message: str) -> Dict[str, Any]:
        """验证提交信息格式"""
        parsed = self.parse(message)
        errors = []
        warnings = []
        
        # 检查基本格式
        if parsed.type == "other":
            errors.append("提交类型不符合Conventional Commits规范")
        
        # 检查描述长度
        if len(parsed.description) > 72:
            warnings.append("描述长度超过72个字符")
        
        # 检查描述格式
        if parsed.description and parsed.description[0].islower():
            warnings.append("描述应该以大写字母开头")
        
        # 检查描述结尾
        if parsed.description and parsed.description.endswith('.'):
            warnings.append("描述不应该以句号结尾")
        
        # 检查主体格式
        if parsed.body:
            body_lines = parsed.body.split('\n')
            for i, line in enumerate(body_lines):
                if line and len(line) > 100:
                    warnings.append(f"主体第{i+1}行超过100个字符")
        
        # 检查破坏性变更
        if parsed.breaking and "BREAKING CHANGE" not in parsed.footer:
            warnings.append("破坏性变更应该在页脚中包含BREAKING CHANGE说明")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'parsed': parsed
        }
    
    def suggest_improvements(self, message: str) -> List[str]:
        """建议改进"""
        result = self.validate(message)
        suggestions = []
        
        if result['errors']:
            suggestions.extend(["错误: " + error for error in result['errors']])
        
        if result['warnings']:
            suggestions.extend(["建议: " + warning for warning in result['warnings']])
        
        parsed = result['parsed']
        
        # 类型建议
        if parsed.type == "other":
            suggestions.append("建议使用标准类型: feat, fix, docs, style, refactor, test, chore")
        
        # 范围建议
        if not parsed.scope and parsed.type in ['feat', 'fix']:
            suggestions.append("建议为功能添加范围说明，如 feat(auth): 添加用户登录功能")
        
        # 主体建议
        if not parsed.body and parsed.breaking:
            suggestions.append("破坏性变更应该在主体中详细说明影响和迁移指南")
        
        return suggestions

# 使用示例
parser = ConventionalCommitsParser()

# 示例提交信息
commits = [
    "feat(auth): add user login functionality",
    "fix: resolve memory leak in data processing",
    "docs: update API documentation",
    "feat!: breaking change to user interface",
    "fix(api): handle null values in user service\n\nCloses #123",
    "refactor: simplify code structure\n\nBREAKING CHANGE: removed deprecated methods"
]

for commit in commits:
    print(f"\n解析提交: {commit}")
    
    parsed = parser.parse(commit)
    print(f"  类型: {parsed.type}")
    print(f"  范围: {parsed.scope}")
    print(f"  描述: {parsed.description}")
    print(f"  破坏性: {parsed.breaking}")
    print(f"  问题: {parsed.issues}")
    print(f"  页脚: {parsed.footer}")
    
    # 验证
    validation = parser.validate(commit)
    print(f"  有效: {validation['valid']}")
    
    if validation['errors'] or validation['warnings']:
        suggestions = parser.suggest_improvements(commit)
        for suggestion in suggestions:
            print(f"  {suggestion}")
```

## 模板系统

### 模板引擎
```python
# template_engine.py
from jinja2 import Environment, FileSystemLoader, Template
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
import json
from datetime import datetime

@dataclass
class TemplateData:
    project_name: str
    project_description: str
    version: str
    release_date: datetime
    commits: List[Dict[str, Any]]
    categories: Dict[str, List[Dict[str, Any]]]
    contributors: List[Dict[str, Any]]
    stats: Dict[str, Any]

class TemplateEngine:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 注册自定义过滤器
        self._register_filters()
    
    def _register_filters(self):
        """注册自定义过滤器"""
        self.env.filters['short_hash'] = lambda x: x[:7] if len(x) > 7 else x
        self.env.filters['format_date'] = self._format_date
        self.env.filters['pluralize'] = self._pluralize
        self.env.filters['truncate'] = self._truncate
        self.env.filters['commit_url'] = self._generate_commit_url
        self.env.filters['issue_url'] = self._generate_issue_url
        self.env.filters['compare_url'] = self._generate_compare_url
    
    def render_template(self, template_name: str, data: TemplateData, 
                        output_path: str, **kwargs) -> bool:
        """渲染模板"""
        try:
            # 加载模板
            template = self.env.get_template(template_name)
            
            # 准备模板数据
            template_data = self._prepare_template_data(data, **kwargs)
            
            # 渲染模板
            rendered = template.render(**template_data)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(rendered)
            
            return True
        
        except Exception as e:
            print(f"渲染模板失败: {e}")
            return False
    
    def render_string(self, template_string: str, data: TemplateData, 
                     **kwargs) -> str:
        """渲染字符串模板"""
        try:
            template = Template(template_string, environment=self.env)
            template_data = self._prepare_template_data(data, **kwargs)
            return template.render(**template_data)
        
        except Exception as e:
            print(f"渲染字符串模板失败: {e}")
            return ""
    
    def _prepare_template_data(self, data: TemplateData, **kwargs) -> Dict[str, Any]:
        """准备模板数据"""
        template_data = {
            'project': {
                'name': data.project_name,
                'description': data.project_description
            },
            'release': {
                'version': data.version,
                'date': data.release_date,
                'formatted_date': self._format_date(data.release_date)
            },
            'commits': data.commits,
            'categories': data.categories,
            'contributors': data.contributors,
            'stats': data.stats,
            'generated_at': datetime.now(),
            'generated_at_formatted': self._format_date(datetime.now())
        }
        
        # 添加额外数据
        template_data.update(kwargs)
        
        return template_data
    
    def _format_date(self, date: datetime, format_str: str = "%Y-%m-%d") -> str:
        """格式化日期"""
        return date.strftime(format_str)
    
    def _pluralize(self, count: int, singular: str, plural: str = None) -> str:
        """复数化"""
        if count == 1:
            return f"{count} {singular}"
        else:
            return f"{count} {plural or singular + 's'}"
    
    def _truncate(self, text: str, length: int = 50, suffix: str = "...") -> str:
        """截断文本"""
        if len(text) <= length:
            return text
        return text[:length].rstrip() + suffix
    
    def _generate_commit_url(self, commit_hash: str, repo_url: str) -> str:
        """生成提交URL"""
        if not repo_url:
            return commit_hash
        
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        return f"{repo_url}/commit/{commit_hash}"
    
    def _generate_issue_url(self, issue_number: str, repo_url: str) -> str:
        """生成问题URL"""
        if not repo_url:
            return f"#{issue_number}"
        
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        return f"{repo_url}/issues/{issue_number}"
    
    def _generate_compare_url(self, from_tag: str, to_tag: str, repo_url: str) -> str:
        """生成比较URL"""
        if not repo_url:
            return f"{from_tag}...{to_tag}"
        
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        return f"{repo_url}/compare/{from_tag}...{to_tag}"

# Markdown模板示例
MARKDOWN_TEMPLATE = """# {{ project.name }} Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [{{ release.version }}] - {{ release.formatted_date }}

{% if categories['feat'] %}
### Added
{% for commit in categories['feat'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['fix'] %}
### Fixed
{% for commit in categories['fix'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['docs'] %}
### Documentation
{% for commit in categories['docs'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['style'] %}
### Style
{% for commit in categories['style'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['refactor'] %}
### Changed
{% for commit in categories['refactor'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['perf'] %}
### Performance
{% for commit in categories['perf'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['test'] %}
### Tests
{% for commit in categories['test'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if categories['build'] or categories['ci'] or categories['chore'] %}
### Build & CI
{% for commit in categories['build'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% for commit in categories['ci'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% for commit in categories['chore'] %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

{% if stats.breaking_changes %}
### BREAKING CHANGES
{% for commit in stats.breaking_changes %}
- {{ commit.description }} ({{ commit.short_hash | commit_url(repo_url) }})
{% endfor %}
{% endif %}

---

**Statistics:**
- {{ stats.total_commits }} commits
- {{ stats.total_files_changed }} files changed
- {{ stats.total_additions }} additions
- {{ stats.total_deletions }} deletions
- {{ contributors | length }} contributors

**Contributors:**
{% for contributor in contributors %}
- {{ contributor.name }} ({{ contributor.commits }} commits)
{% endfor %}

Generated on {{ generated_at_formatted }}
"""

# HTML模板示例
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project.name }} Changelog</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet">
    <style>
        .changelog-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 0;
            margin-bottom: 2rem;
        }
        .version-badge {
            background-color: #28a745;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
        }
        .commit-item {
            border-left: 3px solid #dee2e6;
            padding-left: 1rem;
            margin-bottom: 0.5rem;
        }
        .commit-hash {
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 0.125rem 0.25rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
        }
        .stats-card {
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="changelog-header">
        <div class="container">
            <h1>{{ project.name }} Changelog</h1>
            <p class="lead">{{ project.description }}</p>
            <div class="d-flex align-items-center">
                <span class="version-badge me-2">{{ release.version }}</span>
                <span>{{ release.formatted_date }}</span>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                {% if categories['feat'] %}
                <section class="mb-4">
                    <h2><span class="badge bg-success me-2">✨</span> Added</h2>
                    {% for commit in categories['feat'] %}
                    <div class="commit-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                {{ commit.description }}
                                {% if commit.scope %}
                                <span class="badge bg-secondary ms-2">{{ commit.scope }}</span>
                                {% endif %}
                            </div>
                            <a href="{{ commit.hash | commit_url(repo_url) }}" class="commit-hash">
                                {{ commit.short_hash }}
                            </a>
                        </div>
                        {% if commit.body %}
                        <div class="text-muted small mt-1">{{ commit.body | truncate(100) }}</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </section>
                {% endif %}
                
                {% if categories['fix'] %}
                <section class="mb-4">
                    <h2><span class="badge bg-danger me-2">🐛</span> Fixed</h2>
                    {% for commit in categories['fix'] %}
                    <div class="commit-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                {{ commit.description }}
                                {% if commit.issues %}
                                <div class="mt-1">
                                    {% for issue in commit.issues %}
                                    <a href="{{ issue | issue_url(repo_url) }}" class="badge bg-info me-1">#{{ issue }}</a>
                                    {% endfor %}
                                </div>
                                {% endif %}
                            </div>
                            <a href="{{ commit.hash | commit_url(repo_url) }}" class="commit-hash">
                                {{ commit.short_hash }}
                            </a>
                        </div>
                    </div>
                    {% endfor %}
                </section>
                {% endif %}
                
                <!-- 其他分类... -->
                
            </div>
            
            <div class="col-md-4">
                <div class="stats-card">
                    <h5>Statistics</h5>
                    <ul class="list-unstyled">
                        <li><strong>{{ stats.total_commits }}</strong> commits</li>
                        <li><strong>{{ stats.total_files_changed }}</strong> files changed</li>
                        <li><strong>{{ stats.total_additions }}</strong> additions</li>
                        <li><strong>{{ stats.total_deletions }}</strong> deletions</li>
                        <li><strong>{{ contributors | length }}</strong> contributors</li>
                    </ul>
                </div>
                
                <div class="stats-card">
                    <h5>Contributors</h5>
                    {% for contributor in contributors %}
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>{{ contributor.name }}</span>
                        <span class="badge bg-secondary">{{ contributor.commits }} commits</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <footer class="text-center text-muted py-4 mt-5 border-top">
            <p>Generated on {{ generated_at_formatted }}</p>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# 使用示例
engine = TemplateEngine()

# 创建示例数据
data = TemplateData(
    project_name="My Project",
    project_description="A sample project for changelog generation",
    version="1.2.0",
    release_date=datetime.now(),
    commits=[
        {
            'hash': 'abc123def456',
            'short_hash': 'abc123d',
            'type': 'feat',
            'scope': 'auth',
            'description': 'add user login functionality',
            'body': 'Implemented OAuth2 authentication with JWT tokens',
            'breaking': False,
            'issues': ['123', '124'],
            'author_name': 'John Doe',
            'author_date': datetime.now()
        }
    ],
    categories={
        'feat': [
            {
                'hash': 'abc123def456',
                'short_hash': 'abc123d',
                'description': 'add user login functionality',
                'scope': 'auth',
                'issues': ['123', '124']
            }
        ]
    },
    contributors=[
        {'name': 'John Doe', 'commits': 5},
        {'name': 'Jane Smith', 'commits': 3}
    ],
    stats={
        'total_commits': 8,
        'total_files_changed': 15,
        'total_additions': 200,
        'total_deletions': 50,
        'breaking_changes': []
    }
)

# 渲染Markdown模板
markdown_content = engine.render_string(MARKDOWN_TEMPLATE, data, repo_url="https://github.com/user/repo")
print("Markdown内容:")
print(markdown_content[:500] + "...")

# 渲染HTML模板
html_content = engine.render_string(HTML_TEMPLATE, data, repo_url="https://github.com/user/repo")
print("\nHTML内容:")
print(html_content[:500] + "...")
```

## 分类和过滤

### 变更分类器
```python
# change_classifier.py
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re

class ChangeCategory(Enum):
    ADDED = "added"
    CHANGED = "changed"
    DEPRECATED = "deprecated"
    REMOVED = "removed"
    FIXED = "fixed"
    SECURITY = "security"

@dataclass
class ClassificationRule:
    name: str
    type_match: List[str]
    scope_match: Optional[List[str]]
    description_match: Optional[List[str]]
    category: ChangeCategory
    priority: int
    enabled: bool = True

class ChangeClassifier:
    def __init__(self):
        self.rules = []
        self.custom_filters = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """设置默认分类规则"""
        default_rules = [
            ClassificationRule(
                name="new_features",
                type_match=["feat", "feature"],
                scope_match=None,
                description_match=None,
                category=ChangeCategory.ADDED,
                priority=1
            ),
            ClassificationRule(
                name="bug_fixes",
                type_match=["fix", "bugfix"],
                scope_match=None,
                description_match=None,
                category=ChangeCategory.FIXED,
                priority=1
            ),
            ClassificationRule(
                name="security_fixes",
                type_match=["security", "sec"],
                scope_match=None,
                description_match=["security", "vulnerability", "cve"],
                category=ChangeCategory.SECURITY,
                priority=2
            ),
            ClassificationRule(
                name="breaking_changes",
                type_match=["feat", "fix", "refactor"],
                scope_match=None,
                description_match=["breaking", "deprecated", "removed"],
                category=ChangeCategory.CHANGED,
                priority=3
            ),
            ClassificationRule(
                name="deprecated_features",
                type_match=["feat", "refactor"],
                scope_match=None,
                description_match=["deprecated", "obsolete"],
                category=ChangeCategory.DEPRECATED,
                priority=2
            ),
            ClassificationRule(
                name="removed_features",
                type_match=["feat", "refactor"],
                scope_match=None,
                description_match=["removed", "deleted"],
                category=ChangeCategory.REMOVED,
                priority=2
            ),
            ClassificationRule(
                name="documentation",
                type_match=["docs", "doc"],
                scope_match=None,
                description_match=None,
                category=ChangeCategory.ADDED,
                priority=3
            ),
            ClassificationRule(
                name="performance",
                type_match=["perf", "performance"],
                scope_match=None,
                description_match=["performance", "optimization", "speed"],
                category=ChangeCategory.CHANGED,
                priority=2
            ),
            ClassificationRule(
                name="refactoring",
                type_match=["refactor"],
                scope_match=None,
                description_match=None,
                category=ChangeCategory.CHANGED,
                priority=3
            ),
            ClassificationRule(
                name="testing",
                type_match=["test", "tests"],
                scope_match=None,
                description_match=None,
                category=ChangeCategory.ADDED,
                priority=3
            ),
            ClassificationRule(
                name="build_ci",
                type_match=["build", "ci", "chore"],
                scope_match=None,
                description_match=None,
                category=ChangeCategory.ADDED,
                priority=4
            )
        ]
        
        self.rules.extend(default_rules)
    
    def add_rule(self, rule: ClassificationRule):
        """添加分类规则"""
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda x: x.priority)
    
    def remove_rule(self, rule_name: str) -> bool:
        """移除分类规则"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def add_custom_filter(self, filter_func: Callable[[Dict[str, Any]], bool]):
        """添加自定义过滤器"""
        self.custom_filters.append(filter_func)
    
    def classify_commits(self, commits: List[Dict[str, Any]]) -> Dict[ChangeCategory, List[Dict[str, Any]]]:
        """分类提交"""
        classified = {
            category: [] for category in ChangeCategory
        }
        
        for commit in commits:
            category = self._classify_commit(commit)
            classified[category].append(commit)
        
        return classified
    
    def _classify_commit(self, commit: Dict[str, Any]) -> ChangeCategory:
        """分类单个提交"""
        # 应用自定义过滤器
        for filter_func in self.custom_filters:
            if filter_func(commit):
                return ChangeCategory.CHANGED  # 默认分类
        
        # 应用分类规则
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._matches_rule(commit, rule):
                return rule.category
        
        # 默认分类
        return ChangeCategory.CHANGED
    
    def _matches_rule(self, commit: Dict[str, Any], rule: ClassificationRule) -> bool:
        """检查提交是否匹配规则"""
        # 检查类型匹配
        commit_type = commit.get('type', '').lower()
        if rule.type_match and commit_type not in rule.type_match:
            return False
        
        # 检查范围匹配
        commit_scope = commit.get('scope', '').lower()
        if rule.scope_match and commit_scope not in rule.scope_match:
            return False
        
        # 检查描述匹配
        commit_description = commit.get('description', '').lower()
        commit_body = commit.get('body', '').lower()
        full_text = f"{commit_description} {commit_body}"
        
        if rule.description_match:
            for pattern in rule.description_match:
                if pattern.lower() in full_text:
                    return True
            return False
        
        return True
    
    def filter_commits(self, commits: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """过滤提交"""
        filtered_commits = []
        
        for commit in commits:
            if self._matches_filters(commit, filters):
                filtered_commits.append(commit)
        
        return filtered_commits
    
    def _matches_filters(self, commit: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """检查提交是否匹配过滤条件"""
        # 类型过滤
        if 'types' in filters and filters['types']:
            if commit.get('type') not in filters['types']:
                return False
        
        # 范围过滤
        if 'scopes' in filters and filters['scopes']:
            if commit.get('scope') not in filters['scopes']:
                return False
        
        # 作者过滤
        if 'authors' in filters and filters['authors']:
            if commit.get('author_name') not in filters['authors']:
                return False
        
        # 日期过滤
        if 'date_range' in filters and filters['date_range']:
            start_date = filters['date_range'].get('start')
            end_date = filters['date_range'].get('end')
            
            commit_date = commit.get('commit_date')
            if commit_date:
                if start_date and commit_date < start_date:
                    return False
                if end_date and commit_date > end_date:
                    return False
        
        # 关键词过滤
        if 'keywords' in filters and filters['keywords']:
            text = f"{commit.get('description', '')} {commit.get('body', '')}"
            for keyword in filters['keywords']:
                if keyword.lower() not in text.lower():
                    return False
        
        # 正则表达式过滤
        if 'regex' in filters and filters['regex']:
            pattern = re.compile(filters['regex'], re.IGNORECASE)
            text = f"{commit.get('description', '')} {commit.get('body', '')}"
            if not pattern.search(text):
                return False
        
        return True
    
    def get_statistics(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'total_commits': len(commits),
            'by_type': {},
            'by_scope': {},
            'by_author': {},
            'by_category': {},
            'breaking_changes': 0,
            'issues_fixed': set()
        }
        
        for commit in commits:
            # 按类型统计
            commit_type = commit.get('type', 'other')
            stats['by_type'][commit_type] = stats['by_type'].get(commit_type, 0) + 1
            
            # 按范围统计
            scope = commit.get('scope')
            if scope:
                stats['by_scope'][scope] = stats['by_scope'].get(scope, 0) + 1
            
            # 按作者统计
            author = commit.get('author_name', 'Unknown')
            stats['by_author'][author] = stats['by_author'].get(author, 0) + 1
            
            # 破坏性变更
            if commit.get('breaking', False):
                stats['breaking_changes'] += 1
            
            # 问题修复
            issues = commit.get('issues', [])
            stats['issues_fixed'].update(issues)
        
        # 按分类统计
        classified = self.classify_commits(commits)
        for category, commits_list in classified.items():
            stats['by_category'][category.value] = len(commits_list)
        
        stats['issues_fixed'] = list(stats['issues_fixed'])
        
        return stats

# 使用示例
classifier = ChangeClassifier()

# 示例提交数据
commits = [
    {
        'hash': 'abc123',
        'type': 'feat',
        'scope': 'auth',
        'description': 'add user login functionality',
        'body': 'Implemented OAuth2 authentication',
        'breaking': False,
        'author_name': 'John Doe',
        'commit_date': datetime.now()
    },
    {
        'hash': 'def456',
        'type': 'fix',
        'scope': 'api',
        'description': 'fix memory leak in data processing',
        'body': 'Fixed memory leak caused by unclosed connections',
        'breaking': False,
        'author_name': 'Jane Smith',
        'commit_date': datetime.now(),
        'issues': ['123']
    },
    {
        'hash': 'ghi789',
        'type': 'feat',
        'scope': 'ui',
        'description': 'breaking change to user interface',
        'body': 'BREAKING CHANGE: removed old UI components',
        'breaking': True,
        'author_name': 'Bob Johnson',
        'commit_date': datetime.now()
    }
]

# 分类提交
classified = classifier.classify_commits(commits)

print("分类结果:")
for category, commits_list in classified.items():
    if commits_list:
        print(f"{category.value}: {len(commits_list)} commits")
        for commit in commits_list:
            print(f"  - {commit['description']}")

# 过滤提交
filters = {
    'types': ['feat', 'fix'],
    'authors': ['John Doe', 'Jane Smith']
}

filtered = classifier.filter_commits(commits, filters)
print(f"\n过滤后提交数: {len(filtered)}")

# 获取统计信息
stats = classifier.get_statistics(commits)
print(f"\n统计信息:")
print(f"总提交数: {stats['total_commits']}")
print(f"按类型: {stats['by_type']}")
print(f"按作者: {stats['by_author']}")
print(f"破坏性变更: {stats['breaking_changes']}")
print(f"修复的问题: {stats['issues_fixed']}")
```

## 参考资源

### 规范和标准
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Angular Contributing Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md)

### Git工具
- [GitPython](https://gitpython.readthedocs.io/)
- [LibGit2](https://libgit2.org/)
- [Git CLI](https://git-scm.com/docs)
- [GitHub API](https://docs.github.com/en/rest)

### 模板引擎
- [Jinja2](https://jinja.palletsprojects.com/)
- [Handlebars](https://handlebarsjs.com/)
- [Mustache](https://mustache.github.io/)
- [Liquid](https://shopify.github.io/liquid/)

### 发布平台
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-about-releases)
- [GitLab Releases](https://docs.gitlab.com/ee/user/project/releases/)
- [NPM Publish](https://docs.npmjs.com/cli/v8/commands/npm-publish)
- [PyPI Publish](https://pypi.org/project/pypi/)
