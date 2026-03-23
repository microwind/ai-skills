# Git分析器参考文档

## Git分析器概述

### 什么是Git分析器
Git分析器是一个专门用于分析Git仓库历史数据、代码变更、团队协作和项目健康度的工具。该工具支持多维度分析、趋势预测、异常检测和可视化报告，帮助开发团队了解项目发展状况、优化开发流程、提升代码质量和团队效率。

### 主要功能
- **代码分析**: 提交历史、代码变更、文件分析、分支分析
- **团队分析**: 贡献者统计、协作模式、工作效率、团队网络
- **健康度分析**: 项目活跃度、稳定性评估、风险识别
- **趋势分析**: 代码增长趋势、质量趋势、活跃度趋势
- **对比分析**: 分支对比、版本对比、时间段对比
- **异常检测**: 异常提交、异常行为、异常模式检测

## Git数据分析引擎

### 仓库分析器
```python
# git_analyzer.py
import os
import subprocess
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pandas as pd
import numpy as np

class AnalysisType(Enum):
    COMMIT_HISTORY = "commit_history"
    CODE_CHANGES = "code_changes"
    FILE_ANALYSIS = "file_analysis"
    BRANCH_ANALYSIS = "branch_analysis"
    TEAM_ANALYSIS = "team_analysis"
    HEALTH_ANALYSIS = "health_analysis"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"

@dataclass
class CommitInfo:
    hash: str
    author: str
    email: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int
    branches: List[str] = field(default_factory=list)

@dataclass
class FileInfo:
    path: str
    change_count: int
    total_insertions: int
    total_deletions: int
    last_modified: datetime
    contributors: List[str] = field(default_factory=list)
    file_type: str = ""

@dataclass
class ContributorInfo:
    name: str
    email: str
    commits: int
    insertions: int
    deletions: int
    files_touched: int
    first_commit: datetime
    last_commit: datetime
    active_days: int = 0

@dataclass
class BranchInfo:
    name: str
    commits: int
    authors: List[str]
    created_date: Optional[datetime]
    last_commit: datetime
    merge_count: int = 0

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(__name__)
        
        if not self.repo_path.exists():
            raise FileNotFoundError(f"仓库路径不存在: {repo_path}")
        
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"不是Git仓库: {repo_path}")
    
    def _run_git_command(self, command: List[str]) -> str:
        """执行Git命令"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git命令执行失败: {e}")
            raise
    
    def get_commits(self, since_date: Optional[datetime] = None,
                   until_date: Optional[datetime] = None,
                   branch: str = "HEAD") -> List[CommitInfo]:
        """获取提交历史"""
        # 构建Git命令
        cmd = ["log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso", "--numstat"]
        
        if since_date:
            cmd.extend(["--since", since_date.isoformat()])
        if until_date:
            cmd.extend(["--until", until_date.isoformat()])
        
        cmd.append(branch)
        
        output = self._run_git_command(cmd)
        
        commits = []
        current_commit = None
        
        for line in output.split('\n'):
            if line and '|' in line:
                # 新的提交
                if current_commit:
                    commits.append(current_commit)
                
                parts = line.split('|')
                current_commit = CommitInfo(
                    hash=parts[0],
                    author=parts[1],
                    email=parts[2],
                    date=datetime.fromisoformat(parts[3]),
                    message=parts[4],
                    files_changed=0,
                    insertions=0,
                    deletions=0
                )
            elif line and current_commit and '\t' in line:
                # 文件变更统计
                parts = line.split('\t')
                if len(parts) >= 2:
                    insertions = int(parts[0]) if parts[0] != '-' else 0
                    deletions = int(parts[1]) if parts[1] != '-' else 0
                    
                    current_commit.insertions += insertions
                    current_commit.deletions += deletions
                    current_commit.files_changed += 1
        
        if current_commit:
            commits.append(current_commit)
        
        self.logger.info(f"获取到 {len(commits)} 个提交")
        return commits
    
    def get_file_stats(self, since_date: Optional[datetime] = None,
                      until_date: Optional[datetime] = None) -> Dict[str, FileInfo]:
        """获取文件统计"""
        # 获取所有提交的文件变更
        cmd = ["log", "--name-only", "--pretty=format:"]
        
        if since_date:
            cmd.extend(["--since", since_date.isoformat()])
        if until_date:
            cmd.extend(["--until", until_date.isoformat()])
        
        output = self._run_git_command(cmd)
        
        file_stats = {}
        
        for line in output.split('\n'):
            if line.strip():
                file_path = line.strip()
                
                if file_path not in file_stats:
                    file_stats[file_path] = FileInfo(
                        path=file_path,
                        change_count=0,
                        total_insertions=0,
                        total_deletions=0,
                        last_modified=datetime.now(),
                        file_type=Path(file_path).suffix
                    )
                
                file_stats[file_path].change_count += 1
        
        # 获取详细的文件统计
        cmd = ["log", "--numstat", "--pretty=format:"]
        if since_date:
            cmd.extend(["--since", since_date.isoformat()])
        if until_date:
            cmd.extend(["--until", until_date.isoformat()])
        
        output = self._run_git_command(cmd)
        
        for line in output.split('\n'):
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    file_path = parts[2]
                    insertions = int(parts[0]) if parts[0] != '-' else 0
                    deletions = int(parts[1]) if parts[1] != '-' else 0
                    
                    if file_path in file_stats:
                        file_stats[file_path].total_insertions += insertions
                        file_stats[file_path].total_deletions += deletions
        
        return file_stats
    
    def get_contributors(self, since_date: Optional[datetime] = None,
                        until_date: Optional[datetime] = None) -> Dict[str, ContributorInfo]:
        """获取贡献者统计"""
        commits = self.get_commits(since_date, until_date)
        
        contributors = {}
        
        for commit in commits:
            author_key = f"{commit.author} <{commit.email}>"
            
            if author_key not in contributors:
                contributors[author_key] = ContributorInfo(
                    name=commit.author,
                    email=commit.email,
                    commits=0,
                    insertions=0,
                    deletions=0,
                    files_touched=0,
                    first_commit=commit.date,
                    last_commit=commit.date
                )
            
            contributor = contributors[author_key]
            contributor.commits += 1
            contributor.insertions += commit.insertions
            contributor.deletions += commit.deletions
            contributor.files_touched += commit.files_changed
            
            if commit.date < contributor.first_commit:
                contributor.first_commit = commit.date
            if commit.date > contributor.last_commit:
                contributor.last_commit = commit.date
        
        # 计算活跃天数
        for contributor in contributors.values():
            active_days = (contributor.last_commit - contributor.first_commit).days
            contributor.active_days = max(active_days, 1)
        
        return contributors
    
    def get_branches(self) -> List[BranchInfo]:
        """获取分支信息"""
        # 获取所有分支
        cmd = ["branch", "-a", "--format=%(refname:short)|%(committerdate:iso)|%(authorname)"]
        output = self._run_git_command(cmd)
        
        branches = []
        
        for line in output.split('\n'):
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 3:
                    branch_name = parts[0].replace("origin/", "")
                    commit_date = datetime.fromisoformat(parts[1])
                    author = parts[2]
                    
                    # 获取分支提交数
                    try:
                        commit_count = len(self._run_git_command(
                            ["rev-list", "--count", branch_name]
                        ).split('\n'))
                    except:
                        commit_count = 0
                    
                    branch_info = BranchInfo(
                        name=branch_name,
                        commits=commit_count,
                        authors=[author],
                        created_date=None,
                        last_commit=commit_date
                    )
                    branches.append(branch_info)
        
        return branches
    
    def analyze_commit_patterns(self, commits: List[CommitInfo]) -> Dict[str, Any]:
        """分析提交模式"""
        if not commits:
            return {}
        
        # 按时间分组统计
        hourly_commits = {}
        daily_commits = {}
        weekly_commits = {}
        
        for commit in commits:
            hour = commit.date.hour
            day = commit.date.strftime("%Y-%m-%d")
            week = commit.date.isocalendar()[:2]  # (year, week)
            
            hourly_commits[hour] = hourly_commits.get(hour, 0) + 1
            daily_commits[day] = daily_commits.get(day, 0) + 1
            weekly_commits[week] = weekly_commits.get(week, 0) + 1
        
        # 计算提交频率
        date_range = commits[-1].date - commits[0].date
        days = max(date_range.days, 1)
        avg_commits_per_day = len(commits) / days
        
        # 分析提交消息
        message_patterns = self._analyze_commit_messages(commits)
        
        return {
            "total_commits": len(commits),
            "date_range": {
                "start": commits[0].date.isoformat(),
                "end": commits[-1].date.isoformat(),
                "days": days
            },
            "avg_commits_per_day": avg_commits_per_day,
            "hourly_distribution": hourly_commits,
            "daily_distribution": daily_commits,
            "weekly_distribution": weekly_commits,
            "message_patterns": message_patterns
        }
    
    def _analyze_commit_messages(self, commits: List[CommitInfo]) -> Dict[str, Any]:
        """分析提交消息模式"""
        messages = [commit.message for commit in commits]
        
        # 消息长度统计
        lengths = [len(msg) for msg in messages]
        avg_length = np.mean(lengths) if lengths else 0
        
        # 常见关键词
        keywords = ["fix", "feat", "docs", "style", "refactor", "test", "chore"]
        keyword_counts = {}
        
        for keyword in keywords:
            count = sum(1 for msg in messages if keyword.lower() in msg.lower())
            keyword_counts[keyword] = count
        
        # 消息格式分析
        conventional_commits = 0
        for msg in messages:
            if re.match(r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+', msg):
                conventional_commits += 1
        
        return {
            "avg_message_length": avg_length,
            "keyword_counts": keyword_counts,
            "conventional_commits": conventional_commits,
            "conventional_commits_rate": conventional_commits / len(messages) if messages else 0
        }
    
    def analyze_code_quality(self, commits: List[CommitInfo]) -> Dict[str, Any]:
        """分析代码质量指标"""
        if not commits:
            return {}
        
        # 代码变更统计
        total_insertions = sum(c.insertions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        total_files = sum(c.files_changed for c in commits)
        
        # 平均变更
        avg_insertions = total_insertions / len(commits)
        avg_deletions = total_deletions / len(commits)
        avg_files = total_files / len(commits)
        
        # 大提交分析
        large_commits = [c for c in commits if c.insertions > 1000 or c.deletions > 1000]
        large_commit_rate = len(large_commits) / len(commits)
        
        # 小提交分析
        small_commits = [c for c in commits if c.insertions < 10 and c.deletions < 10]
        small_commit_rate = len(small_commits) / len(commits)
        
        return {
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "total_files_changed": total_files,
            "avg_insertions_per_commit": avg_insertions,
            "avg_deletions_per_commit": avg_deletions,
            "avg_files_per_commit": avg_files,
            "large_commit_count": len(large_commits),
            "large_commit_rate": large_commit_rate,
            "small_commit_count": len(small_commits),
            "small_commit_rate": small_commit_rate
        }
    
    def analyze_team_collaboration(self, contributors: Dict[str, ContributorInfo]) -> Dict[str, Any]:
        """分析团队协作"""
        if not contributors:
            return {}
        
        # 贡献者统计
        total_contributors = len(contributors)
        active_contributors = len([c for c in contributors.values() if c.commits > 0])
        
        # 贡献分布
        commits_by_contributor = [c.commits for c in contributors.values()]
        avg_commits_per_contributor = np.mean(commits_by_contributor)
        
        # 活跃度分析
        active_days_by_contributor = [c.active_days for c in contributors.values()]
        avg_active_days = np.mean(active_days_by_contributor)
        
        # 贡献者排名
        top_contributors = sorted(contributors.values(), 
                                key=lambda x: x.commits, reverse=True)[:10]
        
        return {
            "total_contributors": total_contributors,
            "active_contributors": active_contributors,
            "avg_commits_per_contributor": avg_commits_per_contributor,
            "avg_active_days": avg_active_days,
            "top_contributors": [
                {
                    "name": c.name,
                    "commits": c.commits,
                    "insertions": c.insertions,
                    "active_days": c.active_days
                }
                for c in top_contributors
            ]
        }
    
    def detect_anomalies(self, commits: List[CommitInfo]) -> Dict[str, Any]:
        """异常检测"""
        if not commits:
            return {}
        
        anomalies = []
        
        # 检测异常提交大小
        insertions = [c.insertions for c in commits]
        deletions = [c.deletions for c in commits]
        
        if insertions:
            insertions_mean = np.mean(insertions)
            insertions_std = np.std(insertions)
            
            for commit in commits:
                if commit.insertions > insertions_mean + 3 * insertions_std:
                    anomalies.append({
                        "type": "large_insertions",
                        "commit": commit.hash,
                        "author": commit.author,
                        "date": commit.date.isoformat(),
                        "insertions": commit.insertions,
                        "threshold": insertions_mean + 3 * insertions_std
                    })
        
        # 检测异常提交频率
        if len(commits) > 1:
            time_diffs = []
            for i in range(1, len(commits)):
                diff = (commits[i].date - commits[i-1].date).total_seconds()
                time_diffs.append(diff)
            
            if time_diffs:
                time_diffs_mean = np.mean(time_diffs)
                time_diffs_std = np.std(time_diffs)
                
                for i in range(1, len(commits)):
                    diff = (commits[i].date - commits[i-1].date).total_seconds()
                    if diff < time_diffs_mean - 3 * time_diffs_std:
                        anomalies.append({
                            "type": "high_frequency",
                            "commit": commits[i].hash,
                            "author": commits[i].author,
                            "date": commits[i].date.isoformat(),
                            "time_diff": diff,
                            "threshold": time_diffs_mean - 3 * time_diffs_std
                        })
        
        return {
            "anomaly_count": len(anomalies),
            "anomalies": anomalies
        }
    
    def generate_trend_analysis(self, commits: List[CommitInfo], 
                              time_unit: str = "week") -> Dict[str, Any]:
        """趋势分析"""
        if not commits:
            return {}
        
        # 按时间单位分组
        if time_unit == "day":
            grouped = self._group_by_day(commits)
        elif time_unit == "week":
            grouped = self._group_by_week(commits)
        elif time_unit == "month":
            grouped = self._group_by_month(commits)
        else:
            grouped = self._group_by_week(commits)
        
        # 计算趋势
        periods = sorted(grouped.keys())
        commit_counts = [len(grouped[period]) for period in periods]
        insertion_counts = [sum(c.insertions for c in grouped[period]) for period in periods]
        
        # 简单线性趋势
        if len(periods) > 1:
            x = np.arange(len(periods))
            commit_trend = np.polyfit(x, commit_counts, 1)[0]
            insertion_trend = np.polyfit(x, insertion_counts, 1)[0]
        else:
            commit_trend = 0
            insertion_trend = 0
        
        return {
            "time_unit": time_unit,
            "periods": [period.isoformat() if hasattr(period, 'isoformat') else str(period) for period in periods],
            "commit_counts": commit_counts,
            "insertion_counts": insertion_counts,
            "commit_trend": commit_trend,
            "insertion_trend": insertion_trend
        }
    
    def _group_by_day(self, commits: List[CommitInfo]) -> Dict[datetime, List[CommitInfo]]:
        """按天分组提交"""
        grouped = {}
        for commit in commits:
            day = commit.date.date()
            if day not in grouped:
                grouped[day] = []
            grouped[day].append(commit)
        return grouped
    
    def _group_by_week(self, commits: List[CommitInfo]) -> Dict[Tuple, List[CommitInfo]]:
        """按周分组提交"""
        grouped = {}
        for commit in commits:
            week = commit.date.isocalendar()[:2]  # (year, week)
            if week not in grouped:
                grouped[week] = []
            grouped[week].append(commit)
        return grouped
    
    def _group_by_month(self, commits: List[CommitInfo]) -> Dict[Tuple, List[CommitInfo]]:
        """按月分组提交"""
        grouped = {}
        for commit in commits:
            month = (commit.date.year, commit.date.month)
            if month not in grouped:
                grouped[month] = []
            grouped[month].append(commit)
        return grouped
    
    def generate_report(self, output_path: str, 
                       since_date: Optional[datetime] = None,
                       until_date: Optional[datetime] = None) -> Dict[str, Any]:
        """生成分析报告"""
        self.logger.info("开始生成Git分析报告")
        
        # 收集数据
        commits = self.get_commits(since_date, until_date)
        file_stats = self.get_file_stats(since_date, until_date)
        contributors = self.get_contributors(since_date, until_date)
        branches = self.get_branches()
        
        # 执行分析
        commit_patterns = self.analyze_commit_patterns(commits)
        code_quality = self.analyze_code_quality(commits)
        team_collaboration = self.analyze_team_collaboration(contributors)
        anomalies = self.detect_anomalies(commits)
        trend_analysis = self.generate_trend_analysis(commits)
        
        # 生成报告
        report = {
            "repository": str(self.repo_path),
            "analysis_period": {
                "since": since_date.isoformat() if since_date else None,
                "until": until_date.isoformat() if until_date else None
            },
            "summary": {
                "total_commits": len(commits),
                "total_contributors": len(contributors),
                "total_files": len(file_stats),
                "total_branches": len(branches),
                "analysis_date": datetime.now().isoformat()
            },
            "commit_patterns": commit_patterns,
            "code_quality": code_quality,
            "team_collaboration": team_collaboration,
            "branches": [
                {
                    "name": branch.name,
                    "commits": branch.commits,
                    "last_commit": branch.last_commit.isoformat()
                }
                for branch in branches
            ],
            "anomalies": anomalies,
            "trend_analysis": trend_analysis
        }
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"报告已生成: {output_path}")
        return report

# 使用示例
analyzer = GitAnalyzer("/path/to/your/repository")

# 设置分析时间范围
since_date = datetime.now() - timedelta(days=90)
until_date = datetime.now()

# 生成分析报告
report = analyzer.generate_report(
    output_path="git_analysis_report.json",
    since_date=since_date,
    until_date=until_date
)

print(f"分析完成:")
print(f"总提交数: {report['summary']['total_commits']}")
print(f"贡献者数: {report['summary']['total_contributors']}")
print(f"文件数: {report['summary']['total_files']}")
print(f"分支数: {report['summary']['total_branches']}")
print(f"异常数: {report['anomalies']['anomaly_count']}")
```

## 可视化报告生成器

### 报告可视化
```python
# report_visualizer.py
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path
import logging

class GitReportVisualizer:
    def __init__(self, report_data: Dict[str, Any]):
        self.report = report_data
        self.logger = logging.getLogger(__name__)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 设置样式
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def generate_all_charts(self, output_dir: str = "git_charts"):
        """生成所有图表"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 生成各种图表
        self.plot_commit_activity(output_path / "commit_activity.png")
        self.plot_contributor_distribution(output_path / "contributor_distribution.png")
        self.plot_code_changes_trend(output_path / "code_changes_trend.png")
        self.plot_file_type_distribution(output_path / "file_type_distribution.png")
        self.plot_hourly_commits(output_path / "hourly_commits.png")
        self.plot_weekly_commits(output_path / "weekly_commits.png")
        self.plot_commit_message_patterns(output_path / "commit_message_patterns.png")
        self.plot_code_quality_metrics(output_path / "code_quality_metrics.png")
        
        self.logger.info(f"所有图表已生成到: {output_dir}")
    
    def plot_commit_activity(self, output_path: str):
        """绘制提交活动图"""
        patterns = self.report.get('commit_patterns', {})
        daily_dist = patterns.get('daily_distribution', {})
        
        if not daily_dist:
            return
        
        # 转换为DataFrame
        dates = list(daily_dist.keys())
        counts = list(daily_dist.values())
        
        df = pd.DataFrame({'date': pd.to_datetime(dates), 'commits': counts})
        df = df.sort_values('date')
        
        # 绘制图表
        plt.figure(figsize=(12, 6))
        plt.plot(df['date'], df['commits'], marker='o', linewidth=2)
        plt.title('每日提交活动', fontsize=16, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('提交数', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_contributor_distribution(self, output_path: str):
        """绘制贡献者分布图"""
        collaboration = self.report.get('team_collaboration', {})
        top_contributors = collaboration.get('top_contributors', [])
        
        if not top_contributors:
            return
        
        # 提取数据
        names = [c['name'] for c in top_contributors[:10]]
        commits = [c['commits'] for c in top_contributors[:10]]
        
        # 绘制图表
        plt.figure(figsize=(12, 8))
        bars = plt.barh(names, commits)
        plt.title('Top 10 贡献者', fontsize=16, fontweight='bold')
        plt.xlabel('提交数', fontsize=12)
        plt.ylabel('贡献者', fontsize=12)
        
        # 添加数值标签
        for bar, commit in zip(bars, commits):
            plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                    str(commit), va='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_code_changes_trend(self, output_path: str):
        """绘制代码变更趋势图"""
        trend = self.report.get('trend_analysis', {})
        periods = trend.get('periods', [])
        commit_counts = trend.get('commit_counts', [])
        insertion_counts = trend.get('insertion_counts', [])
        
        if not periods or not commit_counts:
            return
        
        # 转换日期
        dates = pd.to_datetime(periods)
        
        # 绘制图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 提交数趋势
        ax1.plot(dates, commit_counts, marker='o', linewidth=2, color='blue')
        ax1.set_title('提交数趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('提交数', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 代码插入趋势
        ax2.plot(dates, insertion_counts, marker='s', linewidth=2, color='green')
        ax2.set_title('代码插入趋势', fontsize=14, fontweight='bold')
        ax2.set_xlabel('时间', fontsize=12)
        ax2.set_ylabel('插入行数', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_file_type_distribution(self, output_path: str):
        """绘制文件类型分布图"""
        # 这里需要从原始数据中提取文件类型信息
        # 由于report中没有直接的文件类型统计，这里提供一个示例实现
        
        # 示例数据
        file_types = {
            '.py': 150,
            '.js': 120,
            '.html': 80,
            '.css': 60,
            '.md': 40,
            '.json': 30,
            '.yml': 20,
            '.txt': 15
        }
        
        # 绘制饼图
        plt.figure(figsize=(10, 8))
        plt.pie(file_types.values(), labels=file_types.keys(), autopct='%1.1f%%')
        plt.title('文件类型分布', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_hourly_commits(self, output_path: str):
        """绘制小时提交分布图"""
        patterns = self.report.get('commit_patterns', {})
        hourly_dist = patterns.get('hourly_distribution', {})
        
        if not hourly_dist:
            return
        
        hours = list(range(24))
        counts = [hourly_dist.get(hour, 0) for hour in hours]
        
        # 绘制图表
        plt.figure(figsize=(12, 6))
        plt.bar(hours, counts, alpha=0.7)
        plt.title('24小时提交分布', fontsize=16, fontweight='bold')
        plt.xlabel('小时', fontsize=12)
        plt.ylabel('提交数', fontsize=12)
        plt.xticks(hours)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_weekly_commits(self, output_path: str):
        """绘制周提交分布图"""
        patterns = self.report.get('commit_patterns', {})
        weekly_dist = patterns.get('weekly_distribution', {})
        
        if not weekly_dist:
            return
        
        # 转换周数据
        weeks = sorted(weekly_dist.keys())
        counts = [weekly_dist[week] for week in weeks]
        
        # 绘制图表
        plt.figure(figsize=(12, 6))
        plt.plot(range(len(counts)), counts, marker='o', linewidth=2)
        plt.title('周提交趋势', fontsize=16, fontweight='bold')
        plt.xlabel('周', fontsize=12)
        plt.ylabel('提交数', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_commit_message_patterns(self, output_path: str):
        """绘制提交消息模式图"""
        patterns = self.report.get('commit_patterns', {})
        keyword_counts = patterns.get('keyword_counts', {})
        
        if not keyword_counts:
            return
        
        # 提取数据
        keywords = list(keyword_counts.keys())
        counts = list(keyword_counts.values())
        
        # 绘制图表
        plt.figure(figsize=(10, 6))
        bars = plt.bar(keywords, counts, alpha=0.7)
        plt.title('提交消息关键词统计', fontsize=16, fontweight='bold')
        plt.xlabel('关键词', fontsize=12)
        plt.ylabel('出现次数', fontsize=12)
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(count), ha='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_code_quality_metrics(self, output_path: str):
        """绘制代码质量指标图"""
        quality = self.report.get('code_quality', {})
        
        if not quality:
            return
        
        # 提取指标
        metrics = {
            '平均插入/提交': quality.get('avg_insertions_per_commit', 0),
            '平均删除/提交': quality.get('avg_deletions_per_commit', 0),
            '平均文件/提交': quality.get('avg_files_per_commit', 0),
            '大提交率': quality.get('large_commit_rate', 0) * 100,
            '小提交率': quality.get('small_commit_rate', 0) * 100
        }
        
        # 绘制图表
        plt.figure(figsize=(12, 6))
        bars = plt.bar(metrics.keys(), metrics.values(), alpha=0.7)
        plt.title('代码质量指标', fontsize=16, fontweight='bold')
        plt.xlabel('指标', fontsize=12)
        plt.ylabel('数值', fontsize=12)
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for bar, value in zip(bars, metrics.values()):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.2f}', ha='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_html_report(self, output_path: str):
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Git分析报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #e9ecef; border-radius: 5px; }
        .chart { margin: 20px 0; text-align: center; }
        .chart img { max-width: 100%; height: auto; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Git分析报告</h1>
        <p>仓库: {repository}</p>
        <p>分析时间: {analysis_date}</p>
        <p>时间范围: {time_range}</p>
    </div>
    
    <div class="section">
        <h2>概览指标</h2>
        <div class="metric">
            <h3>总提交数</h3>
            <p>{total_commits}</p>
        </div>
        <div class="metric">
            <h3>贡献者数</h3>
            <p>{total_contributors}</p>
        </div>
        <div class="metric">
            <h3>文件数</h3>
            <p>{total_files}</p>
        </div>
        <div class="metric">
            <h3>分支数</h3>
            <p>{total_branches}</p>
        </div>
    </div>
    
    <div class="section">
        <h2>提交活动</h2>
        <div class="chart">
            <img src="commit_activity.png" alt="提交活动">
        </div>
    </div>
    
    <div class="section">
        <h2>贡献者分布</h2>
        <div class="chart">
            <img src="contributor_distribution.png" alt="贡献者分布">
        </div>
    </div>
    
    <div class="section">
        <h2>代码变更趋势</h2>
        <div class="chart">
            <img src="code_changes_trend.png" alt="代码变更趋势">
        </div>
    </div>
    
    <div class="section">
        <h2>代码质量指标</h2>
        <div class="chart">
            <img src="code_quality_metrics.png" alt="代码质量指标">
        </div>
    </div>
    
    <div class="section">
        <h2>异常检测</h2>
        <p>检测到 {anomaly_count} 个异常</p>
        {anomaly_details}
    </div>
</body>
</html>
        """
        
        # 准备数据
        summary = self.report.get('summary', {})
        anomalies = self.report.get('anomalies', {})
        
        anomaly_details = ""
        if anomalies.get('anomalies'):
            anomaly_details = "<table><tr><th>类型</th><th>提交</th><th>作者</th><th>详情</th></tr>"
            for anomaly in anomalies['anomalies'][:10]:  # 只显示前10个
                anomaly_details += f"""
                <tr>
                    <td>{anomaly['type']}</td>
                    <td>{anomaly['commit'][:8]}</td>
                    <td>{anomaly['author']}</td>
                    <td>{anomaly.get('insertions', '') or anomaly.get('time_diff', '')}</td>
                </tr>
                """
            anomaly_details += "</table>"
        
        # 生成HTML
        html_content = html_template.format(
            repository=self.report.get('repository', ''),
            analysis_date=summary.get('analysis_date', ''),
            time_range=f"{summary.get('since', '开始')} - {summary.get('until', '结束')}",
            total_commits=summary.get('total_commits', 0),
            total_contributors=summary.get('total_contributors', 0),
            total_files=summary.get('total_files', 0),
            total_branches=summary.get('total_branches', 0),
            anomaly_count=anomalies.get('anomaly_count', 0),
            anomaly_details=anomaly_details
        )
        
        # 保存HTML文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已生成: {output_path}")

# 使用示例
# 加载报告数据
with open("git_analysis_report.json", 'r', encoding='utf-8') as f:
    report_data = json.load(f)

# 生成可视化报告
visualizer = GitReportVisualizer(report_data)
visualizer.generate_all_charts("git_charts")
visualizer.generate_html_report("git_analysis_report.html")

print("可视化报告生成完成")
```

## 参考资源

### Git文档
- [Git官方文档](https://git-scm.com/doc)
- [Git参考手册](https://git-scm.com/docs)
- [Pro Git书籍](https://git-scm.com/book)

### 代码分析工具
- [GitStats](https://gitstats.sourceforge.net/)
- [GitInspector](https://github.com/ejwa/gitinspector)
- [CodeScene](https://empear.com/products/codescene/)
- [SonarQube](https://www.sonarqube.org/)

### 数据可视化
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [Plotly](https://plotly.com/)
- [D3.js](https://d3js.org/)

### 项目分析
- [GitHub API](https://docs.github.com/en/rest)
- [GitLab API](https://docs.gitlab.com/ee/api/)
- [Bitbucket API](https://developer.atlassian.com/bitbucket/api2/reference/)
- [GHTorrent](https://ghtorrent.org/)

### 团队协作
- [Git工作流](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [GitLab Flow](https://docs.gitlab.com/ee/topics/gitlab_flow.html)
- [Git分支策略](https://www.atlassian.com/git/tutorials/using-branches)
