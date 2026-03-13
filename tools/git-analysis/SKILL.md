---
name: Git分析器
description: "当分析Git仓库、检查提交历史、理解项目演进或查找问题时，分析Git历史和提交。"
license: MIT
---

# Git分析器技能

## 概述
Git历史是项目的时间线。正确读取它以了解代码如何演进。误读历史会在调试时浪费时间。

**核心原则**: Git告诉你什么改变了以及为什么改变。

## 何时使用

**始终:**
- 理解代码演进
- 查找错误何时引入
- 跟踪功能开发
- 理解重构
- 代码审查
- 性能分析

**触发短语:**
- "分析Git历史"
- "查找错误引入点"
- "代码演进分析"
- "Git提交历史"
- "分支分析"
- "代码回溯"

## Git分析功能

### 历史分析
- 提交历史查看
- 分支演进跟踪
- 合并历史分析
- 标签历史查看
- 作者贡献统计

### 代码分析
- 文件变更历史
- 代码行数统计
- 热点文件识别
- 代码复杂度分析
- 技术债务检测

### 团队分析
- 开发者活跃度
- 贡献分布统计
- 协作模式分析
- 代码审查效率
- 工作时间分析

## 常见Git问题

### 提交信息不规范
```
问题:
提交信息不清晰或不规范

错误示例:
fix bug
update
temp commit
wip

解决方案:
使用规范的提交格式:
feat: 添加用户登录功能
fix: 修复登录验证错误
docs: 更新API文档
refactor: 重构用户服务模块
```

### 分支管理混乱
```
问题:
分支命名不规范，合并策略混乱

错误示例:
- feature1
- bug-fix-2
- test-branch
- master分支直接开发

解决方案:
- main/master: 主分支
- develop: 开发分支
- feature/xxx: 功能分支
- hotfix/xxx: 热修复分支
- release/xxx: 发布分支
```

### 合并冲突频发
```
问题:
频繁的合并冲突

原因:
- 功能分支过长时间不合并
- 多人修改同一文件
- 缺乏代码审查

解决方案:
1. 定期合并主分支
2. 小步提交，频繁集成
3. 建立代码审查流程
4. 使用功能开关
```

## 代码实现示例

### Git分析器
```python
import subprocess
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, Counter
import os

@dataclass
class GitCommit:
    """Git提交信息"""
    hash: str
    author: str
    email: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int
    branches: List[str]

@dataclass
class GitFile:
    """Git文件信息"""
    path: str
    size: int
    last_modified: datetime
    last_author: str
    change_count: int
    total_insertions: int
    total_deletions: int

@dataclass
class GitAuthor:
    """Git作者信息"""
    name: str
    email: str
    commits: int
    insertions: int
    deletions: int
    files_touched: int
    first_commit: datetime
    last_commit: datetime
    active_days: int

@dataclass
class GitAnalysis:
    """Git分析结果"""
    total_commits: int
    total_authors: int
    total_files: int
    date_range: Tuple[datetime, datetime]
    top_authors: List[GitAuthor]
    hot_files: List[GitFile]
    commit_frequency: Dict[str, int]

class GitAnalyzer:
    """Git分析器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.git_cmd = ["git", "-C", repo_path]
    
    def _run_git_command(self, args: List[str]) -> str:
        """执行Git命令"""
        try:
            result = subprocess.run(
                self.git_cmd + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git命令执行失败: {e.stderr}")
    
    def get_commits(self, limit: int = 100, since: Optional[str] = None) -> List[GitCommit]:
        """获取提交历史"""
        args = [
            "log",
            f"--max-count={limit}",
            "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=iso",
            "--numstat",
            "--name-only"
        ]
        
        if since:
            args.append(f"--since={since}")
        
        output = self._run_git_command(args)
        return self._parse_commits(output)
    
    def _parse_commits(self, output: str) -> List[GitCommit]:
        """解析提交信息"""
        commits = []
        lines = output.split('\n')
        i = 0
        
        while i < len(lines):
            if not lines[i]:
                i += 1
                continue
            
            # 解析提交头信息
            header = lines[i].split('|')
            if len(header) >= 5:
                commit_hash = header[0]
                author = header[1]
                email = header[2]
                date = datetime.fromisoformat(header[3].replace(' ', 'T'))
                message = '|'.join(header[4:])
                
                i += 1
                
                # 解析文件统计信息
                insertions = 0
                deletions = 0
                files_changed = []
                
                while i < len(lines) and lines[i]:
                    line = lines[i]
                    if '\t' in line:
                        parts = line.split('\t')
                        if len(parts) == 3:
                            try:
                                ins = int(parts[0]) if parts[0] != '-' else 0
                                dels = int(parts[1]) if parts[1] != '-' else 0
                                file_path = parts[2]
                                
                                insertions += ins
                                deletions += dels
                                files_changed.append(file_path)
                            except ValueError:
                                pass
                    i += 1
                
                # 获取分支信息
                branches = self._get_commit_branches(commit_hash)
                
                commits.append(GitCommit(
                    hash=commit_hash,
                    author=author,
                    email=email,
                    date=date,
                    message=message,
                    files_changed=files_changed,
                    insertions=insertions,
                    deletions=deletions,
                    branches=branches
                ))
            else:
                i += 1
        
        return commits
    
    def _get_commit_branches(self, commit_hash: str) -> List[str]:
        """获取提交所在的分支"""
        try:
            output = self._run_git_command([
                "branch", "--contains", commit_hash
            ])
            branches = []
            for line in output.split('\n'):
                branch = line.strip().replace('* ', '')
                if branch and branch != 'HEAD':
                    branches.append(branch)
            return branches
        except:
            return []
    
    def get_file_history(self, file_path: str) -> List[GitCommit]:
        """获取文件历史"""
        output = self._run_git_command([
            "log",
            "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=iso",
            "--numstat",
            file_path
        ])
        return self._parse_commits(output)
    
    def get_authors(self) -> List[GitAuthor]:
        """获取作者统计"""
        output = self._run_git_command([
            "log",
            "--pretty=format:%an|%ae|%ad",
            "--date=iso",
            "--numstat"
        ])
        
        author_stats = defaultdict(lambda: {
            'commits': 0,
            'insertions': 0,
            'deletions': 0,
            'files': set(),
            'dates': [],
            'first_commit': None,
            'last_commit': None
        })
        
        lines = output.split('\n')
        i = 0
        
        while i < len(lines):
            if not lines[i]:
                i += 1
                continue
            
            if '|' in lines[i]:
                # 提交信息
                parts = lines[i].split('|')
                if len(parts) >= 3:
                    author = parts[0]
                    email = parts[1]
                    date = datetime.fromisoformat(parts[2].replace(' ', 'T'))
                    
                    stats = author_stats[author]
                    stats['commits'] += 1
                    stats['dates'].append(date)
                    
                    if not stats['first_commit'] or date < stats['first_commit']:
                        stats['first_commit'] = date
                    if not stats['last_commit'] or date > stats['last_commit']:
                        stats['last_commit'] = date
                    
                    i += 1
                    
                    # 文件统计
                    while i < len(lines) and lines[i] and '\t' in lines[i]:
                        file_parts = lines[i].split('\t')
                        if len(file_parts) >= 3:
                            file_path = file_parts[2]
                            stats['files'].add(file_path)
                            
                            try:
                                ins = int(file_parts[0]) if file_parts[0] != '-' else 0
                                dels = int(file_parts[1]) if file_parts[1] != '-' else 0
                                stats['insertions'] += ins
                                stats['deletions'] += dels
                            except ValueError:
                                pass
                        i += 1
            else:
                i += 1
        
        # 构建作者对象
        authors = []
        for author_name, stats in author_stats.items():
            active_days = len(set(d.date() for d in stats['dates']))
            
            authors.append(GitAuthor(
                name=author_name,
                email="",  # 需要额外获取
                commits=stats['commits'],
                insertions=stats['insertions'],
                deletions=stats['deletions'],
                files_touched=len(stats['files']),
                first_commit=stats['first_commit'],
                last_commit=stats['last_commit'],
                active_days=active_days
            ))
        
        return sorted(authors, key=lambda x: x.commits, reverse=True)
    
    def get_hot_files(self, limit: int = 10) -> List[GitFile]:
        """获取热点文件"""
        output = self._run_git_command([
            "log",
            "--name-only",
            "--pretty=format:"
        ])
        
        file_stats = defaultdict(lambda: {
            'count': 0,
            'last_modified': None,
            'last_author': None,
            'insertions': 0,
            'deletions': 0
        })
        
        lines = output.split('\n')
        current_commit = None
        
        for line in lines:
            if line.strip():
                if not line.startswith(' '):
                    # 新的提交
                    current_commit = line
                else:
                    # 文件路径
                    file_path = line.strip()
                    if file_path and file_path != '':
                        stats = file_stats[file_path]
                        stats['count'] += 1
                        # 这里可以添加更多统计信息
        
        # 获取文件详细信息
        hot_files = []
        for file_path, stats in file_stats.items():
            try:
                # 获取文件大小
                full_path = os.path.join(self.repo_path, file_path)
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                else:
                    size = 0
                
                # 获取最后修改信息
                last_commit_info = self._get_last_file_commit(file_path)
                
                hot_files.append(GitFile(
                    path=file_path,
                    size=size,
                    last_modified=last_commit_info.get('date', datetime.now()),
                    last_author=last_commit_info.get('author', ''),
                    change_count=stats['count'],
                    total_insertions=stats['insertions'],
                    total_deletions=stats['deletions']
                ))
            except:
                continue
        
        return sorted(hot_files, key=lambda x: x.change_count, reverse=True)[:limit]
    
    def _get_last_file_commit(self, file_path: str) -> Dict[str, Any]:
        """获取文件的最后提交信息"""
        try:
            output = self._run_git_command([
                "log",
                "-1",
                "--pretty=format:%an|%ad",
                "--date=iso",
                file_path
            ])
            
            if output:
                parts = output.split('|')
                return {
                    'author': parts[0] if len(parts) > 0 else '',
                    'date': datetime.fromisoformat(parts[1].replace(' ', 'T')) if len(parts) > 1 else datetime.now()
                }
        except:
            pass
        
        return {'author': '', 'date': datetime.now()}
    
    def analyze_repository(self) -> GitAnalysis:
        """分析整个仓库"""
        # 获取基本统计
        total_commits = int(self._run_git_command(["rev-list", "--count", "HEAD"]))
        
        # 获取作者数量
        authors = self.get_authors()
        total_authors = len(authors)
        
        # 获取文件数量
        output = self._run_git_command(["ls-files"])
        total_files = len(output.split('\n')) if output else 0
        
        # 获取日期范围
        first_date_str = self._run_git_command(["log", "--reverse", "--pretty=format:%ad", "--date=iso"]).split('\n')[0]
        last_date_str = self._run_git_command(["log", "-1", "--pretty=format:%ad", "--date=iso"])
        
        first_date = datetime.fromisoformat(first_date_str.replace(' ', 'T'))
        last_date = datetime.fromisoformat(last_date_str.replace(' ', 'T'))
        
        # 获取热点文件
        hot_files = self.get_hot_files()
        
        # 获取提交频率
        commit_frequency = self._get_commit_frequency()
        
        return GitAnalysis(
            total_commits=total_commits,
            total_authors=total_authors,
            total_files=total_files,
            date_range=(first_date, last_date),
            top_authors=authors[:10],
            hot_files=hot_files,
            commit_frequency=commit_frequency
        )
    
    def _get_commit_frequency(self) -> Dict[str, int]:
        """获取提交频率"""
        output = self._run_git_command([
            "log",
            "--pretty=format:%ad",
            "--date=format:%Y-%m-%d"
        ])
        
        dates = output.split('\n')
        return dict(Counter(dates))
    
    def find_bug_introduction(self, bug_description: str) -> List[GitCommit]:
        """查找错误引入点"""
        # 使用git bisect查找错误引入点
        # 这里简化实现，实际需要更复杂的逻辑
        
        commits = self.get_commits(limit=200)
        suspicious_commits = []
        
        for commit in commits:
            # 简单的关键词匹配
            if any(keyword in commit.message.lower() for keyword in ['fix', 'bug', 'error', 'issue']):
                suspicious_commits.append(commit)
        
        return suspicious_commits
    
    def generate_analysis_report(self, analysis: GitAnalysis) -> str:
        """生成分析报告"""
        report = ["=== Git仓库分析报告 ===\n"]
        
        # 基本统计
        report.append("=== 基本统计 ===")
        report.append(f"总提交数: {analysis.total_commits}")
        report.append(f"总作者数: {analysis.total_authors}")
        report.append(f"总文件数: {analysis.total_files}")
        report.append(f"时间范围: {analysis.date_range[0].strftime('%Y-%m-%d')} 到 {analysis.date_range[1].strftime('%Y-%m-%d')}")
        
        # 计算项目年龄
        project_age = (analysis.date_range[1] - analysis.date_range[0]).days
        report.append(f"项目年龄: {project_age} 天")
        
        if project_age > 0:
            avg_commits_per_day = analysis.total_commits / project_age
            report.append(f"平均每天提交: {avg_commits_per_day:.2f}")
        
        report.append("")
        
        # 顶级贡献者
        report.append("=== 顶级贡献者 ===")
        for i, author in enumerate(analysis.top_authors[:10], 1):
            report.append(f"{i}. {author.name}")
            report.append(f"   提交数: {author.commits}")
            report.append(f"   代码行数: +{author.insertions} -{author.deletions}")
            report.append(f"   活跃天数: {author.active_days}")
            report.append("")
        
        # 热点文件
        report.append("=== 热点文件 ===")
        for i, file in enumerate(analysis.hot_files[:10], 1):
            report.append(f"{i}. {file.path}")
            report.append(f"   修改次数: {file.change_count}")
            report.append(f"   文件大小: {file.size} bytes")
            report.append(f"   最后修改: {file.last_modified.strftime('%Y-%m-%d')}")
            report.append("")
        
        # 提交频率
        report.append("=== 最近提交频率 ===")
        recent_dates = sorted(analysis.commit_frequency.items(), reverse=True)[:10]
        for date, count in recent_dates:
            report.append(f"{date}: {count} 次提交")
        
        return '\n'.join(report)

# 使用示例
def main():
    analyzer = GitAnalyzer("/path/to/repo")
    
    # 分析仓库
    analysis = analyzer.analyze_repository()
    
    # 生成报告
    report = analyzer.generate_analysis_report(analysis)
    print(report)
    
    # 查找错误引入点
    bug_commits = analyzer.find_bug_introduction("login error")
    print(f"\n找到 {len(bug_commits)} 个可能相关的提交")

if __name__ == "__main__":
    main()
```

### Git代码审查工具
```python
import re
from typing import List, Dict, Any

class GitCodeReviewer:
    """Git代码审查工具"""
    
    def __init__(self, repo_path: str = "."):
        self.analyzer = GitAnalyzer(repo_path)
        self.review_rules = self._initialize_review_rules()
    
    def review_commit(self, commit_hash: str) -> Dict[str, Any]:
        """审查单个提交"""
        commits = self.analyzer.get_commits(limit=1)
        if not commits or commits[0].hash != commit_hash:
            # 获取特定提交
            output = self.analyzer._run_git_command([
                "show",
                "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso",
                "--numstat",
                commit_hash
            ])
            commits = self.analyzer._parse_commits(output)
        
        if not commits:
            return {"error": "提交不存在"}
        
        commit = commits[0]
        
        # 审查提交信息
        message_issues = self._review_commit_message(commit.message)
        
        # 审查代码变更
        code_issues = self._review_code_changes(commit)
        
        # 审查文件变更
        file_issues = self._review_file_changes(commit)
        
        return {
            "commit": commit,
            "issues": {
                "message": message_issues,
                "code": code_issues,
                "files": file_issues
            },
            "score": self._calculate_review_score(message_issues, code_issues, file_issues)
        }
    
    def _review_commit_message(self, message: str) -> List[str]:
        """审查提交信息"""
        issues = []
        
        # 检查长度
        if len(message) > 72:
            issues.append("提交信息过长，建议不超过72个字符")
        
        # 检查格式
        if not re.match(r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+', message):
            issues.append("提交信息格式不规范，建议使用类型: 描述格式")
        
        # 检查是否包含必要信息
        if len(message) < 10:
            issues.append("提交信息过于简单，缺少详细描述")
        
        # 检查是否包含敏感信息
        sensitive_patterns = [
            r'password',
            r'secret',
            r'key',
            r'token',
            r'credential'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                issues.append(f"提交信息可能包含敏感信息: {pattern}")
        
        return issues
    
    def _review_code_changes(self, commit: GitCommit) -> List[str]:
        """审查代码变更"""
        issues = []
        
        # 检查变更量
        total_changes = commit.insertions + commit.deletions
        if total_changes > 1000:
            issues.append("单次提交变更量过大，建议拆分为多个小提交")
        
        # 检查删除比例
        if commit.deletions > commit.insertions * 2:
            issues.append("删除代码过多，可能需要更好的重构策略")
        
        # 检查文件数量
        if len(commit.files_changed) > 20:
            issues.append("修改文件过多，可能影响多个功能模块")
        
        return issues
    
    def _review_file_changes(self, commit: GitCommit) -> List[str]:
        """审查文件变更"""
        issues = []
        
        # 检查敏感文件
        sensitive_files = [
            'config.py',
            '.env',
            'secrets.json',
            'private.key',
            'id_rsa'
        ]
        
        for file_path in commit.files_changed:
            for sensitive in sensitive_files:
                if sensitive in file_path:
                    issues.append(f"修改了敏感文件: {file_path}")
                    break
        
        # 检查测试文件
        test_files = [f for f in commit.files_changed if 'test' in f.lower()]
        if not test_files and len(commit.files_changed) > 5:
            issues.append("大量代码变更但没有测试文件修改")
        
        return issues
    
    def _calculate_review_score(self, message_issues: List[str], 
                               code_issues: List[str], 
                               file_issues: List[str]) -> int:
        """计算审查分数"""
        total_issues = len(message_issues) + len(code_issues) + len(file_issues)
        
        # 基础分数100，每个问题扣10分
        score = max(0, 100 - total_issues * 10)
        
        return score
    
    def review_branch(self, branch_name: str) -> Dict[str, Any]:
        """审查分支"""
        # 获取分支的所有提交
        output = self.analyzer._run_git_command([
            "log",
            f"{branch_name}..HEAD",
            "--pretty=format:%H"
        ])
        
        commit_hashes = output.split('\n') if output else []
        
        branch_reviews = []
        total_score = 0
        
        for commit_hash in commit_hashes:
            if commit_hash.strip():
                review = self.review_commit(commit_hash.strip())
                branch_reviews.append(review)
                total_score += review.get('score', 0)
        
        avg_score = total_score / len(branch_reviews) if branch_reviews else 0
        
        return {
            "branch": branch_name,
            "commits": branch_reviews,
            "total_commits": len(branch_reviews),
            "average_score": avg_score,
            "recommendation": self._get_branch_recommendation(avg_score)
        }
    
    def _get_branch_recommendation(self, score: float) -> str:
        """获取分支建议"""
        if score >= 80:
            return "可以合并"
        elif score >= 60:
            return "建议修复问题后合并"
        else:
            return "不建议合并，需要重大改进"
    
    def _initialize_review_rules(self) -> Dict[str, Any]:
        """初始化审查规则"""
        return {
            "max_commit_size": 1000,
            "max_files_per_commit": 20,
            "max_message_length": 72,
            "required_message_format": r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+',
            "sensitive_files": [
                'config.py', '.env', 'secrets.json', 'private.key', 'id_rsa'
            ]
        }

# 使用示例
def main():
    reviewer = GitCodeReviewer("/path/to/repo")
    
    # 审查最新提交
    latest_commit = reviewer.analyzer._run_git_command(["rev-parse", "HEAD"])
    review_result = reviewer.review_commit(latest_commit)
    
    print("=== 代码审查报告 ===")
    print(f"提交: {review_result['commit'].hash}")
    print(f"作者: {review_result['commit'].author}")
    print(f"分数: {review_result['score']}")
    
    if review_result['issues']['message']:
        print("\n提交信息问题:")
        for issue in review_result['issues']['message']:
            print(f"  - {issue}")
    
    if review_result['issues']['code']:
        print("\n代码变更问题:")
        for issue in review_result['issues']['code']:
            print(f"  - {issue}")
    
    if review_result['issues']['files']:
        print("\n文件变更问题:")
        for issue in review_result['issues']['files']:
            print(f"  - {issue}")

if __name__ == "__main__":
    main()
```

## Git最佳实践

### 提交规范
1. **原子提交**: 每个提交只做一件事
2. **清晰信息**: 使用描述性的提交信息
3. **格式统一**: 遵循团队约定的格式
4. **及时提交**: 频繁提交，小步快跑

### 分支策略
1. **主分支保护**: 主分支只接受合并
2. **功能分支**: 每个功能使用独立分支
3. **定期同步**: 定期合并主分支更新
4. **清理分支**: 及时删除已合并的分支

### 代码审查
1. **强制审查**: 所有代码必须经过审查
2. **审查清单**: 使用标准化的审查清单
3. **及时反馈**: 快速响应审查请求
4. **建设性意见**: 提供具体的改进建议

## 相关技能

- **code-review** - 代码审查
- **version-control** - 版本控制
- **project-management** - 项目管理
- **team-collaboration** - 团队协作
