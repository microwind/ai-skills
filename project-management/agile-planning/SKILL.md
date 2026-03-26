---
name: 敏捷项目管理
description: "当实施敏捷开发、规划Sprint、管理产品待办列表、组织Scrum会议或优化团队协作流程时，提供完整的敏捷项目管理指导。"
license: MIT
---

# 敏捷项目管理技能

## 概述
敏捷项目管理是一种以迭代、增量方式进行项目管理的方法论，强调快速响应变化、持续交付价值和团队协作。它通过短周期的迭代（Sprint）和持续反馈来确保项目朝着正确的方向发展。

**核心原则**: 个体和互动高于流程和工具，工作的软件高于详尽的文档，客户合作高于合同谈判，响应变化高于遵循计划。

## 何时使用

**始终:**
- 启动新的软件开发项目
- 转换传统项目管理模式
- 优化现有敏捷流程
- 处理项目进度延迟
- 改善团队协作效率
- 管理产品需求变更
- 进行Sprint规划和回顾
- 处理团队冲突和问题

**触发短语:**
- "如何实施敏捷开发"
- "Sprint规划怎么做"
- "敏捷项目管理流程"
- "Scrum会议组织"
- "产品待办列表管理"
- "团队协作优化"
- "敏捷工具推荐"
- "项目进度管理"

## 敏捷框架和方法论

### Scrum框架
- **Sprint**: 2-4周的固定时间盒
- **角色**: Product Owner、Scrum Master、开发团队
- **事件**: Sprint计划会、每日站会、Sprint评审会、Sprint回顾会
- **工件**: 产品待办列表、Sprint待办列表、增量

### Kanban方法
- **可视化工作流**: 看板展示工作状态
- **限制在制品**: 控制同时进行的工作数量
- **管理流动**: 优化工作流程
- **明确策略**: 制定工作规则

### 极限编程(XP)
- **编码标准**: 统一的代码风格
- **测试驱动开发**: 先写测试再写代码
- **结对编程**: 两人协作开发
- **持续集成**: 频繁集成和测试

## 敏捷项目管理流程

### 1. 项目启动阶段
- **愿景定义**: 明确项目目标和成功标准
- **团队组建**: 确定角色和职责
- **工具准备**: 选择协作工具和平台
- **初始规划**: 制定高阶路线图

### 2. 需求管理阶段
- **用户故事**: 以用户视角描述需求
- **待办列表**: 按优先级排序的需求清单
- **估算技术**: 评估工作量和复杂度
- **价值排序**: 基于业务价值确定优先级

### 3. Sprint执行阶段
- **Sprint规划**: 选择本次迭代的工作
- **每日站会**: 同步进度和识别障碍
- **持续开发**: 按计划完成工作
- **Sprint评审**: 展示成果和收集反馈

### 4. 持续改进阶段
- **Sprint回顾**: 反思流程和改进机会
- **度量分析**: 跟踪关键指标
- **流程优化**: 调整工作方法
- **团队建设**: 提升协作能力

## 常见敏捷问题

### Sprint规划问题
```
问题:
Sprint规划时间过长，工作量估算不准确

症状:
- 规划会议超过4小时
- Sprint经常无法完成计划
- 工作量估算偏差很大
- 团队成员对承诺缺乏信心

解决方案:
- 使用故事点相对估算
- 准备详细的接受标准
- 建立历史速度基线
- 分解大型用户故事
- 使用规划扑克等技术
```

### 团队协作问题
```
问题:
团队成员协作不畅，沟通效率低

症状:
- 信息孤岛现象严重
- 重复工作频发
- 决策过程缓慢
- 团队士气低落

解决方案:
- 建立有效沟通机制
- 实施每日站会制度
- 使用协作工具平台
- 定期团队建设活动
- 明确角色和职责
```

### 需求变更管理
```
问题:
需求频繁变更影响项目进度

症状:
- Sprint中需求不断变化
- 开发方向频繁调整
- 团队对变更产生抵触
- 项目目标不清晰

解决方案:
- 建立变更控制流程
- 明确变更优先级
- 保持产品待办列表灵活性
- 加强与利益相关者沟通
- 快速响应合理变更
```

## 代码实现示例

### 敏捷项目管理系统
```python
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json

class SprintStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StoryStatus(Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class UserStory:
    """用户故事"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    story_points: Optional[int] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: StoryStatus = StoryStatus.BACKLOG
    assignee: Optional[str] = None
    created_date: datetime = None
    updated_date: datetime = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
        if self.updated_date is None:
            self.updated_date = datetime.now()

@dataclass
class Sprint:
    """Sprint"""
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    stories: List[str]  # story IDs
    status: SprintStatus = SprintStatus.PLANNING
    capacity: Optional[int] = None  # 团队容量（故事点）
    velocity: Optional[float] = None  # 实际完成速度
    
    @property
    def duration_days(self) -> int:
        """Sprint持续天数"""
        return (self.end_date - self.start_date).days + 1

@dataclass
class TeamMember:
    """团队成员"""
    id: str
    name: str
    role: str  # Product Owner, Scrum Master, Developer
    skills: List[str]
    availability: float = 1.0  # 可用性系数
    current_stories: List[str] = None
    
    def __post_init__(self):
        if self.current_stories is None:
            self.current_stories = []

class AgileProjectManager:
    """敏捷项目管理器"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.stories: Dict[str, UserStory] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.team_members: Dict[str, TeamMember] = {}
        self.product_backlog: List[str] = []  # story IDs
        self.sprint_history: List[Dict] = []
        
    def add_user_story(self, story: UserStory):
        """添加用户故事"""
        self.stories[story.id] = story
        self.product_backlog.append(story.id)
        self._sort_backlog()
        
    def _sort_backlog(self):
        """按优先级排序待办列表"""
        self.product_backlog.sort(
            key=lambda story_id: self.stories[story_id].priority.value,
            reverse=True
        )
    
    def create_sprint(self, sprint_id: str, name: str, start_date: datetime, 
                     duration_days: int = 14, capacity: int = None) -> Sprint:
        """创建Sprint"""
        end_date = start_date + timedelta(days=duration_days - 1)
        
        sprint = Sprint(
            id=sprint_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
            stories=[],
            capacity=capacity
        )
        
        self.sprints[sprint_id] = sprint
        return sprint
    
    def plan_sprint(self, sprint_id: str, story_ids: List[str]) -> bool:
        """Sprint规划"""
        if sprint_id not in self.sprints:
            return False
        
        sprint = self.sprints[sprint_id]
        
        # 计算总故事点
        total_points = 0
        for story_id in story_ids:
            if story_id not in self.stories:
                return False
            story = self.stories[story_id]
            if story.story_points is None:
                return False
            total_points += story.story_points
        
        # 检查容量限制
        if sprint.capacity and total_points > sprint.capacity:
            print(f"警告: Sprint容量不足 ({total_points} > {sprint.capacity})")
            return False
        
        # 分配故事到Sprint
        sprint.stories = story_ids
        sprint.status = SprintStatus.ACTIVE
        
        # 更新故事状态
        for story_id in story_ids:
            self.stories[story_id].status = StoryStatus.IN_PROGRESS
            # 从待办列表移除
            if story_id in self.product_backlog:
                self.product_backlog.remove(story_id)
        
        return True
    
    def assign_story(self, story_id: str, assignee_id: str) -> bool:
        """分配用户故事"""
        if story_id not in self.stories or assignee_id not in self.team_members:
            return False
        
        story = self.stories[story_id]
        assignee = self.team_members[assignee_id]
        
        story.assignee = assignee_id
        if story_id not in assignee.current_stories:
            assignee.current_stories.append(story_id)
        
        return True
    
    def update_story_status(self, story_id: str, status: StoryStatus) -> bool:
        """更新故事状态"""
        if story_id not in self.stories:
            return False
        
        story = self.stories[story_id]
        old_status = story.status
        story.status = status
        story.updated_date = datetime.now()
        
        # 如果故事完成，从成员当前任务中移除
        if status == StoryStatus.DONE and story.assignee:
            assignee = self.team_members.get(story.assignee)
            if assignee and story_id in assignee.current_stories:
                assignee.current_stories.remove(story_id)
        
        return True
    
    def get_sprint_progress(self, sprint_id: str) -> Dict:
        """获取Sprint进度"""
        if sprint_id not in self.sprints:
            return {}
        
        sprint = self.sprints[sprint_id]
        
        total_stories = len(sprint.stories)
        completed_stories = sum(
            1 for story_id in sprint.stories
            if self.stories[story_id].status == StoryStatus.DONE
        )
        
        total_points = sum(
            self.stories[story_id].story_points or 0
            for story_id in sprint.stories
        )
        completed_points = sum(
            self.stories[story_id].story_points or 0
            for story_id in sprint.stories
            if self.stories[story_id].status == StoryStatus.DONE
        )
        
        return {
            'sprint_id': sprint_id,
            'total_stories': total_stories,
            'completed_stories': completed_stories,
            'story_completion_rate': completed_stories / total_stories if total_stories > 0 else 0,
            'total_points': total_points,
            'completed_points': completed_points,
            'point_completion_rate': completed_points / total_points if total_points > 0 else 0,
            'status': sprint.status.value
        }
    
    def calculate_team_velocity(self, num_sprints: int = 3) -> float:
        """计算团队速度（平均每Sprint完成的故事点）"""
        completed_sprints = [
            sprint for sprint in self.sprints.values()
            if sprint.status == SprintStatus.COMPLETED
        ]
        
        if not completed_sprints:
            return 0.0
        
        # 取最近N个完成的Sprint
        recent_sprints = sorted(
            completed_sprints,
            key=lambda s: s.end_date,
            reverse=True
        )[:num_sprints]
        
        total_points = 0
        for sprint in recent_sprints:
            sprint_points = sum(
                self.stories[story_id].story_points or 0
                for story_id in sprint.stories
                if self.stories[story_id].status == StoryStatus.DONE
            )
            total_points += sprint_points
        
        return total_points / len(recent_sprints) if recent_sprints else 0.0
    
    def generate_burndown_chart(self, sprint_id: str) -> Dict:
        """生成燃尽图数据"""
        if sprint_id not in self.sprints:
            return {}
        
        sprint = self.sprints[sprint_id]
        
        # 理想燃尽线
        total_points = sum(
            self.stories[story_id].story_points or 0
            for story_id in sprint.stories
        )
        
        days = sprint.duration_days
        ideal_burndown = [
            {'day': i, 'remaining': total_points - (total_points * i / days)}
            for i in range(days + 1)
        ]
        
        # 实际燃尽线（简化版本，实际应该基于每日数据）
        actual_burndown = []
        # 这里需要实际的每日完成数据，简化处理
        
        return {
            'sprint_id': sprint_id,
            'total_points': total_points,
            'duration_days': days,
            'ideal_burndown': ideal_burndown,
            'actual_burndown': actual_burndown
        }
    
    def conduct_sprint_review(self, sprint_id: str) -> Dict:
        """进行Sprint评审"""
        if sprint_id not in self.sprints:
            return {}
        
        sprint = self.sprints[sprint_id]
        progress = self.get_sprint_progress(sprint_id)
        
        review_results = {
            'sprint_id': sprint_id,
            'sprint_name': sprint.name,
            'review_date': datetime.now(),
            'completion_rate': progress['point_completion_rate'],
            'total_stories': progress['total_stories'],
            'completed_stories': progress['completed_stories'],
            'velocity': progress['completed_points']
        }
        
        # 记录Sprint历史
        self.sprint_history.append(review_results)
        
        # 更新Sprint状态
        sprint.status = SprintStatus.COMPLETED
        sprint.velocity = progress['completed_points']
        
        return review_results
    
    def suggest_next_sprint_capacity(self) -> int:
        """建议下一个Sprint的容量"""
        avg_velocity = self.calculate_team_velocity()
        
        # 基于历史速度的80%-120%范围建议
        min_capacity = int(avg_velocity * 0.8)
        max_capacity = int(avg_velocity * 1.2)
        
        return max_capacity if avg_velocity > 0 else 20  # 默认容量
    
    def export_project_data(self, file_path: str):
        """导出项目数据"""
        data = {
            'project_name': self.project_name,
            'export_date': datetime.now().isoformat(),
            'stories': [
                {
                    'id': story.id,
                    'title': story.title,
                    'description': story.description,
                    'story_points': story.story_points,
                    'priority': story.priority.value,
                    'status': story.status.value,
                    'assignee': story.assignee
                }
                for story in self.stories.values()
            ],
            'sprints': [
                {
                    'id': sprint.id,
                    'name': sprint.name,
                    'start_date': sprint.start_date.isoformat(),
                    'end_date': sprint.end_date.isoformat(),
                    'status': sprint.status.value,
                    'capacity': sprint.capacity,
                    'velocity': sprint.velocity
                }
                for sprint in self.sprints.values()
            ],
            'team_members': [
                {
                    'id': member.id,
                    'name': member.name,
                    'role': member.role,
                    'skills': member.skills,
                    'availability': member.availability
                }
                for member in self.team_members.values()
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# 使用示例
def main():
    """示例使用"""
    # 创建敏捷项目管理器
    pm = AgileProjectManager("电商平台开发")
    
    # 添加团队成员
    pm.team_members["member1"] = TeamMember(
        id="member1", name="张三", role="Product Owner", 
        skills=["需求分析", "产品设计"]
    )
    pm.team_members["member2"] = TeamMember(
        id="member2", name="李四", role="Scrum Master", 
        skills=["项目管理", "团队协调"]
    )
    pm.team_members["member3"] = TeamMember(
        id="member3", name="王五", role="Developer", 
        skills=["前端开发", "React"]
    )
    
    # 添加用户故事
    story1 = UserStory(
        id="story1",
        title="用户登录功能",
        description="用户可以使用邮箱和密码登录系统",
        acceptance_criteria=[
            "用户输入正确邮箱和密码可以登录",
            "显示错误信息当凭据无效",
            "支持记住登录状态"
        ],
        story_points=5,
        priority=TaskPriority.HIGH
    )
    
    story2 = UserStory(
        id="story2",
        title="商品搜索功能",
        description="用户可以搜索商品并查看结果",
        acceptance_criteria=[
            "支持关键词搜索",
            "显示搜索结果列表",
            "支持分类筛选"
        ],
        story_points=8,
        priority=TaskPriority.MEDIUM
    )
    
    pm.add_user_story(story1)
    pm.add_user_story(story2)
    
    # 创建Sprint
    sprint1 = pm.create_sprint(
        sprint_id="sprint1",
        name="Sprint 1 - 基础功能",
        start_date=datetime.now(),
        duration_days=14,
        capacity=20
    )
    
    # Sprint规划
    pm.plan_sprint("sprint1", ["story1", "story2"])
    
    # 分配任务
    pm.assign_story("story1", "member3")
    pm.assign_story("story2", "member3")
    
    # 更新进度
    pm.update_story_status("story1", StoryStatus.DONE)
    
    # 查看进度
    progress = pm.get_sprint_progress("sprint1")
    print(f"Sprint进度: {progress}")
    
    # 计算团队速度
    velocity = pm.calculate_team_velocity()
    print(f"团队速度: {velocity}")
    
    print("敏捷项目管理器演示完成!")

if __name__ == "__main__":
    main()
```

### 敏捷度量分析工具
```python
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd

class AgileMetricsAnalyzer:
    """敏捷度量分析器"""
    
    def __init__(self, project_manager: AgileProjectManager):
        self.pm = project_manager
        
    def plot_velocity_chart(self, num_sprints: int = 6):
        """绘制速度图"""
        completed_sprints = [
            sprint for sprint in self.pm.sprints.values()
            if sprint.status == SprintStatus.COMPLETED
        ]
        
        if not completed_sprints:
            print("没有已完成的Sprint数据")
            return
        
        # 按结束日期排序
        completed_sprints.sort(key=lambda s: s.end_date)
        
        sprint_names = []
        velocities = []
        
        for sprint in completed_sprints[-num_sprints:]:
            sprint_names.append(sprint.name)
            velocities.append(sprint.velocity or 0)
        
        plt.figure(figsize=(12, 6))
        plt.bar(sprint_names, velocities, color='skyblue')
        plt.title('团队速度趋势')
        plt.xlabel('Sprint')
        plt.ylabel('完成的故事点')
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        
        # 添加平均线
        if velocities:
            avg_velocity = sum(velocities) / len(velocities)
            plt.axhline(y=avg_velocity, color='red', linestyle='--', 
                       label=f'平均速度: {avg_velocity:.1f}')
            plt.legend()
        
        plt.tight_layout()
        plt.show()
    
    def plot_cumulative_flow(self):
        """绘制累积流图"""
        # 按状态统计故事数量
        status_counts = {}
        for status in StoryStatus:
            status_counts[status.value] = sum(
                1 for story in self.pm.stories.values()
                if story.status == status
            )
        
        plt.figure(figsize=(10, 6))
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        colors = ['lightcoral', 'gold', 'lightgreen', 'skyblue', 'plum']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('故事状态分布')
        plt.axis('equal')
        plt.show()
    
    def generate_sprint_report(self, sprint_id: str) -> str:
        """生成Sprint报告"""
        if sprint_id not in self.pm.sprints:
            return "Sprint不存在"
        
        sprint = self.pm.sprints[sprint_id]
        progress = self.pm.get_sprint_progress(sprint_id)
        
        report = f"""
# {sprint.name} Sprint报告

## 基本信息
- **Sprint ID**: {sprint.id}
- **开始日期**: {sprint.start_date.strftime('%Y-%m-%d')}
- **结束日期**: {sprint.end_date.strftime('%Y-%m-%d')}
- **持续时间**: {sprint.duration_days} 天
- **计划容量**: {sprint.capacity or '未设置'} 故事点

## 完成情况
- **总故事数**: {progress['total_stories']}
- **完成故事数**: {progress['completed_stories']}
- **故事完成率**: {progress['story_completion_rate']:.1%}
- **总故事点**: {progress['total_points']}
- **完成故事点**: {progress['completed_points']}
- **点完成率**: {progress['point_completion_rate']:.1%}

## 故事详情
"""
        
        for story_id in sprint.stories:
            story = self.pm.stories[story_id]
            status_icon = "✅" if story.status == StoryStatus.DONE else "⏳"
            report += f"- {status_icon} **{story.title}** ({story.story_points}点) - {story.assignee or '未分配'}\n"
        
        report += f"""
## 团队表现
- **Sprint速度**: {progress['completed_points']} 点
- **效率**: {progress['point_completion_rate']:.1%}

## 改进建议
"""
        
        if progress['point_completion_rate'] < 0.8:
            report += "- 考虑减少Sprint容量或分解大型故事\n"
        if progress['point_completion_rate'] > 1.0:
            report += "- 可以适当增加Sprint容量\n"
        if progress['story_completion_rate'] < progress['point_completion_rate']:
            report += "- 注意故事点估算的准确性\n"
        
        return report

# 使用示例
def main():
    print("敏捷度量分析器已准备就绪!")

if __name__ == "__main__":
    main()
```

## 敏捷最佳实践

### 团队协作
1. **每日站会**: 15分钟同步进度
2. **面对面沟通**: 优先直接交流
3. **透明度**: 所有信息对团队可见
4. **自组织**: 团队自主决策工作方式

### 需求管理
1. **用户故事**: 以用户价值为导向
2. **接受标准**: 明确完成定义
3. **优先级排序**: 基于业务价值
4. **持续反馈**: 定期收集用户意见

### 持续改进
1. **Sprint回顾**: 定期反思和改进
2. **度量驱动**: 基于数据决策
3. **实验精神**: 尝试新方法
4. **学习文化**: 鼓励知识分享

## 敏捷工具推荐

### 项目管理工具
- **Jira**: 功能完整的敏捷项目管理
- **Azure DevOps**: 微软的DevOps平台
- **Trello**: 简单的看板工具
- **ClickUp**: 多功能项目管理

### 协作工具
- **Slack**: 团队沟通平台
- **Microsoft Teams**: 集成办公套件
- **Confluence**: 文档协作平台
- **Miro**: 在线白板协作

### 开发工具
- **GitHub**: 代码托管和协作
- **GitLab**: DevOps生命周期管理
- **Jenkins**: 持续集成服务器
- **Docker**: 容器化部署

## 相关技能

- **product-management** - 产品管理
- **team-collaboration** - 团队协作
- **project-planning** - 项目规划
- **requirements-analysis** - 需求分析
- **stakeholder-management** - 利益相关者管理
- **continuous-improvement** - 持续改进
