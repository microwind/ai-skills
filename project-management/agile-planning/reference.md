# 敏捷规划参考文档

## 敏捷方法论概述

### 敏捷宣言
敏捷软件开发宣言包含四个核心价值观：
1. **个体和互动** 高于 流程和工具
2. **工作的软件** 高于 详尽的文档
3. **客户合作** 高于 合同谈判
4. **响应变化** 高于 遵循计划

### 敏捷十二原则
1. 最高优先级是通过持续交付有价值的软件来满足客户
2. 欢迎需求变化，即使在开发后期
3. 频繁交付可工作的软件，周期从几周到几个月不等
4. 业务人员和开发人员必须在整个项目期间每天合作
5. 围绕有动力的个体构建项目，给予他们所需的环境和支持
6. 面对面交谈是最有效的沟通方式
7. 可工作的软件是进度的首要度量标准
8. 敏捷过程倡导可持续开发
9. 持续关注技术卓越和良好设计
10. 简化是最大化未完成工作量的艺术
11. 最好的架构、需求和设计来自自组织团队
12. 团队定期反思如何提高效率，并调整行为

### 敏捷方法论比较

#### Scrum vs Kanban vs Scrumban
| 特性 | Scrum | Kanban | Scrumban |
|------|-------|--------|----------|
| 时间盒 | 固定Sprint长度 | 无时间盒 | 可选时间盒 |
| 角色定义 | 明确角色 | 无固定角色 | 灵活角色 |
| 迭代 | 增量迭代 | 持续流动 | 混合方式 |
| 估算 | 必需估算 | 可选估算 | 灵活估算 |
| 变更处理 | Sprint间变更 | 随时变更 | 灵活变更 |

## Scrum框架详解

### Scrum事件

#### Sprint
Sprint是Scrum的核心，是一个固定时长的时间盒，通常为1-4周。

```python
class Sprint:
    def __init__(self, sprint_number, duration_weeks, start_date):
        self.sprint_number = sprint_number
        self.duration_weeks = duration_weeks
        self.start_date = start_date
        self.end_date = start_date + timedelta(weeks=duration_weeks)
        self.sprint_goal = ""
        self.backlog_items = []
        self.daily_standups = []
        self.velocity = 0
        
    def calculate_duration_days(self):
        """计算Sprint工作天数"""
        total_days = 0
        current_date = self.start_date
        
        while current_date < self.end_date:
            if current_date.weekday() < 5:  # 周一到周五
                total_days += 1
            current_date += timedelta(days=1)
        
        return total_days
    
    def add_backlog_item(self, item):
        """添加待办事项到Sprint"""
        self.backlog_items.append(item)
    
    def calculate_velocity(self):
        """计算Sprint速度"""
        completed_points = sum(item.story_points for item in self.backlog_items 
                             if item.status == "Done")
        self.velocity = completed_points
        return self.velocity

# 使用示例
from datetime import datetime, timedelta

sprint = Sprint(
    sprint_number=5,
    duration_weeks=2,
    start_date=datetime(2024, 1, 15)
)

print(f"Sprint {sprint.sprint_number} 持续 {sprint.calculate_duration_days()} 个工作日")
```

#### 每日站会 (Daily Standup)
每日站会是15分钟的短会议，团队成员回答三个问题：
1. 昨天我做了什么？
2. 今天我将做什么？
3. 遇到了什么障碍？

```python
class DailyStandup:
    def __init__(self, date, participants):
        self.date = date
        self.participants = participants
        self.updates = []
        self.blockers = []
        
    def add_update(self, participant, yesterday_work, today_work, blockers=None):
        """添加每日更新"""
        update = {
            'participant': participant,
            'yesterday': yesterday_work,
            'today': today_work,
            'blockers': blockers or [],
            'timestamp': datetime.now()
        }
        self.updates.append(update)
        
        if blockers:
            self.blockers.extend(blockers)
    
    def generate_summary(self):
        """生成站会摘要"""
        summary = {
            'date': self.date,
            'participants_count': len(self.participants),
            'updates_count': len(self.updates),
            'blockers_count': len(self.blockers),
            'summary_text': self._create_summary_text()
        }
        return summary
    
    def _create_summary_text(self):
        """创建摘要文本"""
        text = f"每日站会 - {self.date}\n\n"
        
        for update in self.updates:
            text += f"{update['participant']}:\n"
            text += f"  昨天: {update['yesterday']}\n"
            text += f"  今天: {update['today']}\n"
            if update['blockers']:
                text += f"  障碍: {', '.join(update['blockers'])}\n"
            text += "\n"
        
        return text

# 使用示例
standup = DailyStandup(
    date=datetime(2024, 1, 16),
    participants=['Alice', 'Bob', 'Charlie']
)

standup.add_update(
    participant='Alice',
    yesterday_work='完成了用户登录功能',
    today_work='开始实现用户注册功能',
    blockers=['数据库连接问题']
)

standup.add_update(
    participant='Bob',
    yesterday_work='修复了3个bug',
    today_work='继续优化性能',
    blockers=[]
)

summary = standup.generate_summary()
print(summary['summary_text'])
```

#### Sprint计划会议
Sprint计划会议通常分为两部分：
1. **第一部分**：确定Sprint目标和Sprint待办列表
2. **第二部分**：详细规划如何完成工作

```python
class SprintPlanning:
    def __init__(self, sprint_number, team_capacity):
        self.sprint_number = sprint_number
        self.team_capacity = team_capacity  # 团队容量（故事点）
        self.sprint_goal = ""
        self.selected_items = []
        self.planning_notes = []
        
    def set_sprint_goal(self, goal):
        """设置Sprint目标"""
        self.sprint_goal = goal
        self.add_note(f"Sprint目标: {goal}")
    
    def select_backlog_items(self, product_backlog, available_capacity=None):
        """选择待办事项"""
        if available_capacity is None:
            available_capacity = self.team_capacity
        
        selected = []
        total_points = 0
        
        # 按优先级排序
        sorted_items = sorted(product_backlog, key=lambda x: x.priority, reverse=True)
        
        for item in sorted_items:
            if total_points + item.story_points <= available_capacity:
                selected.append(item)
                total_points += item.story_points
                self.add_note(f"选择: {item.title} ({item.story_points}点)")
            else:
                self.add_note(f"跳过: {item.title} (超出容量)")
        
        self.selected_items = selected
        self.add_note(f"总计选择 {len(selected)} 个事项，共 {total_points} 点")
        
        return selected
    
    def add_note(self, note):
        """添加规划笔记"""
        self.planning_notes.append({
            'timestamp': datetime.now(),
            'note': note
        })
    
    def generate_plan(self):
        """生成Sprint计划"""
        plan = {
            'sprint_number': self.sprint_number,
            'sprint_goal': self.sprint_goal,
            'team_capacity': self.team_capacity,
            'selected_items': len(self.selected_items),
            'total_story_points': sum(item.story_points for item in self.selected_items),
            'utilization': (sum(item.story_points for item in self.selected_items) / 
                          self.team_capacity * 100),
            'planning_notes': self.planning_notes
        }
        return plan

# 使用示例
class BacklogItem:
    def __init__(self, title, story_points, priority):
        self.title = title
        self.story_points = story_points
        self.priority = priority

# 创建产品待办列表
product_backlog = [
    BacklogItem("用户登录功能", 5, 10),
    BacklogItem("用户注册功能", 8, 9),
    BacklogItem("密码重置功能", 3, 8),
    BacklogItem("用户资料页面", 5, 7),
    BacklogItem("搜索功能", 13, 6),
]

planning = SprintPlanning(sprint_number=5, team_capacity=20)
planning.set_sprint_goal("完成用户认证系统的核心功能")
selected_items = planning.select_backlog_items(product_backlog)

plan = planning.generate_plan()
print(f"Sprint {plan['sprint_number']} 计划:")
print(f"目标: {plan['sprint_goal']}")
print(f"选择事项: {plan['selected_items']} 个")
print(f"总故事点: {plan['total_story_points']} 点")
print(f"容量利用率: {plan['utilization']:.1f}%")
```

### Scrum工件

#### 产品待办列表 (Product Backlog)
产品待办列表是产品所有需求的有序列表。

```python
class ProductBacklog:
    def __init__(self):
        self.items = []
        self.last_updated = datetime.now()
        
    def add_item(self, title, description, story_points, priority=1):
        """添加待办事项"""
        item = {
            'id': len(self.items) + 1,
            'title': title,
            'description': description,
            'story_points': story_points,
            'priority': priority,
            'status': 'Backlog',
            'created_date': datetime.now(),
            'updated_date': datetime.now()
        }
        self.items.append(item)
        self.last_updated = datetime.now()
        return item
    
    def update_priority(self, item_id, new_priority):
        """更新优先级"""
        for item in self.items:
            if item['id'] == item_id:
                item['priority'] = new_priority
                item['updated_date'] = datetime.now()
                break
        self.last_updated = datetime.now()
    
    def get_sorted_items(self):
        """获取按优先级排序的待办事项"""
        return sorted(self.items, key=lambda x: x['priority'], reverse=True)
    
    def get_total_story_points(self):
        """获取总故事点数"""
        return sum(item['story_points'] for item in self.items)
    
    def filter_by_status(self, status):
        """按状态过滤"""
        return [item for item in self.items if item['status'] == status]
    
    def get_velocity_forecast(self, avg_velocity, sprints_ahead=3):
        """预测未来Sprint能完成的工作"""
        sorted_items = self.get_sorted_items()
        backlog_items = [item for item in sorted_items if item['status'] == 'Backlog']
        
        forecast = []
        current_capacity = 0
        current_sprint = []
        
        for item in backlog_items:
            if current_capacity + item['story_points'] <= avg_velocity:
                current_sprint.append(item)
                current_capacity += item['story_points']
            else:
                if current_sprint:
                    forecast.append({
                        'sprint_number': len(forecast) + 1,
                        'items': current_sprint.copy(),
                        'total_points': current_capacity
                    })
                current_sprint = [item]
                current_capacity = item['story_points']
            
            if len(forecast) >= sprints_ahead:
                break
        
        # 添加最后一个Sprint
        if current_sprint and len(forecast) < sprints_ahead:
            forecast.append({
                'sprint_number': len(forecast) + 1,
                'items': current_sprint,
                'total_points': current_capacity
            })
        
        return forecast

# 使用示例
backlog = ProductBacklog()

# 添加待办事项
backlog.add_item("用户登录功能", "实现用户登录界面和后端逻辑", 5, 10)
backlog.add_item("用户注册功能", "实现用户注册流程", 8, 9)
backlog.add_item("密码重置功能", "实现密码重置邮件发送", 3, 8)
backlog.add_item("用户资料页面", "创建用户资料编辑页面", 5, 7)

print(f"产品待办列表总共有 {len(backlog.items)} 个事项")
print(f"总故事点数: {backlog.get_total_story_points()}")

# 预测未来Sprint
forecast = backlog.get_velocity_forecast(avg_velocity=20, sprints_ahead=3)
for sprint in forecast:
    print(f"Sprint {sprint['sprint_number']}: {len(sprint['items'])} 个事项, {sprint['total_points']} 点")
```

#### Sprint待办列表 (Sprint Backlog)
Sprint待办列表是Sprint期间要完成的工作项集合。

```python
class SprintBacklog:
    def __init__(self, sprint_number):
        self.sprint_number = sprint_number
        self.items = []
        self.daily_progress = []
        self.created_date = datetime.now()
        
    def add_item(self, backlog_item, assignee=None):
        """添加Sprint事项"""
        sprint_item = {
            'original_item': backlog_item,
            'assignee': assignee,
            'status': 'To Do',
            'hours_remaining': backlog_item['story_points'] * 8,  # 假设1点=8小时
            'added_date': datetime.now(),
            'start_date': None,
            'complete_date': None
        }
        self.items.append(sprint_item)
        return sprint_item
    
    def update_item_status(self, item_id, status, hours_worked=0):
        """更新事项状态"""
        for item in self.items:
            if item['original_item']['id'] == item_id:
                old_status = item['status']
                item['status'] = status
                
                if status == 'In Progress' and old_status != 'In Progress':
                    item['start_date'] = datetime.now()
                elif status == 'Done' and old_status != 'Done':
                    item['complete_date'] = datetime.now()
                    item['hours_remaining'] = 0
                elif status == 'In Progress':
                    item['hours_remaining'] -= hours_worked
                
                break
    
    def record_daily_progress(self):
        """记录每日进度"""
        progress = {
            'date': datetime.now().date(),
            'total_items': len(self.items),
            'completed_items': len([item for item in self.items if item['status'] == 'Done']),
            'in_progress_items': len([item for item in self.items if item['status'] == 'In Progress']),
            'to_do_items': len([item for item in self.items if item['status'] == 'To Do']),
            'total_hours_remaining': sum(item['hours_remaining'] for item in self.items)
        }
        self.daily_progress.append(progress)
        return progress
    
    def generate_burndown_data(self):
        """生成燃尽图数据"""
        if not self.daily_progress:
            return []
        
        # 计算理想燃尽线
        total_hours = self.daily_progress[0]['total_hours_remaining']
        sprint_days = len(self.daily_progress)
        ideal_burndown = [
            total_hours - (total_hours * day / sprint_days)
            for day in range(sprint_days + 1)
        ]
        
        # 实际燃尽线
        actual_burndown = [total_hours]  # 开始时的总小时数
        for progress in self.daily_progress:
            actual_burndown.append(progress['total_hours_remaining'])
        
        return {
            'days': list(range(sprint_days + 1)),
            'ideal': ideal_burndown,
            'actual': actual_burndown
        }
    
    def get_sprint_summary(self):
        """获取Sprint摘要"""
        completed_items = [item for item in self.items if item['status'] == 'Done']
        completed_points = sum(item['original_item']['story_points'] for item in completed_items)
        
        return {
            'sprint_number': self.sprint_number,
            'total_items': len(self.items),
            'completed_items': len(completed_items),
            'completion_rate': len(completed_items) / len(self.items) * 100,
            'total_story_points': sum(item['original_item']['story_points'] for item in self.items),
            'completed_story_points': completed_points,
            'sprint_velocity': completed_points
        }

# 使用示例
# 创建产品待办事项
item1 = {'id': 1, 'title': '用户登录功能', 'story_points': 5, 'priority': 10}
item2 = {'id': 2, 'title': '用户注册功能', 'story_points': 8, 'priority': 9}

# 创建Sprint待办列表
sprint_backlog = SprintBacklog(sprint_number=5)
sprint_backlog.add_item(item1, assignee='Alice')
sprint_backlog.add_item(item2, assignee='Bob')

# 模拟每日进度
for day in range(10):  # 10个工作日
    sprint_backlog.record_daily_progress()
    
    # 更新一些事项的状态
    if day == 2:
        sprint_backlog.update_item_status(1, 'In Progress', hours_worked=8)
    if day == 5:
        sprint_backlog.update_item_status(1, 'Done')
        sprint_backlog.update_item_status(2, 'In Progress', hours_worked=8)
    if day == 8:
        sprint_backlog.update_item_status(2, 'Done')

# 生成燃尽图数据
burndown_data = sprint_backlog.generate_burndown_data()
print(f"燃尽图数据点数: {len(burndown_data['days'])}")

# 获取Sprint摘要
summary = sprint_backlog.get_sprint_summary()
print(f"Sprint {summary['sprint_number']} 摘要:")
print(f"完成率: {summary['completion_rate']:.1f}%")
print(f"Sprint速度: {summary['sprint_velocity']} 点")
```

## Kanban方法详解

### Kanban原则
1. **可视化工作流**: 将工作流程可视化
2. **限制在制品 (WIP)**: 限制同时进行的工作数量
3. **管理流动**: 优化工作流动
4. **明确策略**: 制定明确的流程策略
5. **实施反馈循环**: 建立反馈机制
6. **协作改进**: 团队协作持续改进

### Kanban看板实现

#### 看板系统
```python
class KanbanBoard:
    def __init__(self, name):
        self.name = name
        self.columns = ['Backlog', 'To Do', 'In Progress', 'Testing', 'Done']
        self.wip_limits = {
            'Backlog': None,  # 无限制
            'To Do': 10,
            'In Progress': 3,
            'Testing': 2,
            'Done': None
        }
        self.cards = []
        self.swimlanes = ['Default']
        
    def add_card(self, title, description, priority=1, swimlane='Default'):
        """添加卡片"""
        card = {
            'id': len(self.cards) + 1,
            'title': title,
            'description': description,
            'priority': priority,
            'column': 'Backlog',
            'swimlane': swimlane,
            'created_date': datetime.now(),
            'moved_date': datetime.now(),
            'blocked': False,
            'block_reason': None
        }
        self.cards.append(card)
        return card
    
    def move_card(self, card_id, new_column, block_reason=None):
        """移动卡片到新列"""
        card = self.get_card(card_id)
        if card:
            # 检查WIP限制
            if self.wip_limits.get(new_column) is not None:
                current_wip = len([c for c in self.cards 
                                if c['column'] == new_column and c['id'] != card_id])
                if current_wip >= self.wip_limits[new_column]:
                    raise ValueError(f"列 '{new_column}' 的WIP限制已达到")
            
            old_column = card['column']
            card['column'] = new_column
            card['moved_date'] = datetime.now()
            
            if block_reason:
                card['blocked'] = True
                card['block_reason'] = block_reason
            else:
                card['blocked'] = False
                card['block_reason'] = None
            
            return True
        return False
    
    def get_card(self, card_id):
        """获取卡片"""
        for card in self.cards:
            if card['id'] == card_id:
                return card
        return None
    
    def get_cards_by_column(self, column):
        """获取指定列的卡片"""
        return [card for card in self.cards if card['column'] == column]
    
    def get_wip_status(self):
        """获取WIP状态"""
        wip_status = {}
        for column in self.columns:
            cards = self.get_cards_by_column(column)
            wip_limit = self.wip_limits.get(column)
            
            wip_status[column] = {
                'current_count': len(cards),
                'limit': wip_limit,
                'utilization': (len(cards) / wip_limit * 100) if wip_limit else None,
                'is_over_limit': wip_limit and len(cards) > wip_limit
            }
        
        return wip_status
    
    def calculate_cycle_time(self, card_id):
        """计算卡片周期时间"""
        card = self.get_card(card_id)
        if card and card['column'] == 'Done':
            cycle_time = card['moved_date'] - card['created_date']
            return cycle_time.days
        return None
    
    def calculate_lead_time(self, card_id):
        """计算卡片前置时间"""
        card = self.get_card(card_id)
        if card and card['column'] == 'Done':
            # 假设前置时间从创建到完成
            lead_time = card['moved_date'] - card['created_date']
            return lead_time.days
        return None
    
    def get_flow_metrics(self):
        """获取流动指标"""
        completed_cards = [card for card in self.cards if card['column'] == 'Done']
        
        if not completed_cards:
            return None
        
        cycle_times = [self.calculate_cycle_time(card['id']) for card in completed_cards]
        cycle_times = [ct for ct in cycle_times if ct is not None]
        
        if cycle_times:
            avg_cycle_time = sum(cycle_times) / len(cycle_times)
            min_cycle_time = min(cycle_times)
            max_cycle_time = max(cycle_times)
        else:
            avg_cycle_time = min_cycle_time = max_cycle_time = 0
        
        return {
            'completed_cards': len(completed_cards),
            'avg_cycle_time': avg_cycle_time,
            'min_cycle_time': min_cycle_time,
            'max_cycle_time': max_cycle_time,
            'throughput': len(completed_cards) / 30  # 假设30天期间
        }
    
    def add_swimlane(self, name):
        """添加泳道"""
        if name not in self.swimlanes:
            self.swimlanes.append(name)
    
    def get_board_view(self):
        """获取看板视图"""
        board_view = {}
        
        for column in self.columns:
            column_cards = self.get_cards_by_column(column)
            board_view[column] = {
                'cards': column_cards,
                'wip_limit': self.wip_limits.get(column),
                'count': len(column_cards)
            }
        
        return board_view

# 使用示例
board = KanbanBoard("Web应用开发")

# 添加卡片
board.add_card("用户登录功能", "实现用户登录界面", priority=10)
board.add_card("数据库设计", "设计用户表结构", priority=9)
board.add_card("API开发", "开发用户认证API", priority=8)
board.add_card("前端页面", "创建登录页面", priority=7)

# 移动卡片
board.move_card(1, "To Do")
board.move_card(1, "In Progress")
board.move_card(2, "In Progress")

# 检查WIP状态
wip_status = board.get_wip_status()
for column, status in wip_status.items():
    print(f"{column}: {status['current_count']}/{status['limit']} "
          f"({status['utilization']:.1f}%)" if status['utilization'] else f"{column}: {status['current_count']}")

# 获取流动指标
flow_metrics = board.get_flow_metrics()
if flow_metrics:
    print(f"平均周期时间: {flow_metrics['avg_cycle_time']:.1f} 天")
    print(f"吞吐量: {flow_metrics['throughput']:.1f} 卡片/天")
```

#### 累积流图 (Cumulative Flow Diagram)
```python
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class CumulativeFlowDiagram:
    def __init__(self, kanban_board):
        self.board = kanban_board
        self.history_data = []
        
    def record_snapshot(self):
        """记录当前状态快照"""
        snapshot = {
            'date': datetime.now(),
            'columns': {}
        }
        
        for column in self.board.columns:
            cards = self.board.get_cards_by_column(column)
            snapshot['columns'][column] = len(cards)
        
        self.history_data.append(snapshot)
    
    def generate_cfd_data(self):
        """生成CFD数据"""
        if not self.history_data:
            return None
        
        columns = self.board.columns
        dates = [snapshot['date'] for snapshot in self.history_data]
        
        cfd_data = {
            'dates': dates,
            'columns': {}
        }
        
        for column in columns:
            cumulative_counts = []
            cumulative_total = 0
            
            for snapshot in self.history_data:
                cumulative_total += snapshot['columns'][column]
                cumulative_counts.append(cumulative_total)
            
            cfd_data['columns'][column] = cumulative_counts
        
        return cfd_data
    
    def plot_cfd(self):
        """绘制累积流图"""
        cfd_data = self.generate_cfd_data()
        if not cfd_data:
            print("没有足够的数据绘制CFD")
            return
        
        plt.figure(figsize=(12, 6))
        
        dates = cfd_data['dates']
        for column, counts in cfd_data['columns'].items():
            if column != 'Done':  # 不绘制Done列，因为它是累积终点
                plt.plot(dates, counts, label=column, marker='o')
        
        plt.xlabel('日期')
        plt.ylabel('累积工作项数量')
        plt.title('累积流图 (Cumulative Flow Diagram)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def calculate_flow_metrics(self):
        """计算流动指标"""
        cfd_data = self.generate_cfd_data()
        if not cfd_data or len(cfd_data['dates']) < 2:
            return None
        
        # 计算平均周期时间
        if 'In Progress' in cfd_data['columns'] and 'Done' in cfd_data['columns']:
            in_progress_counts = cfd_data['columns']['In Progress']
            done_counts = cfd_data['columns']['Done']
            
            avg_wip = sum(in_progress_counts) / len(in_progress_counts)
            avg_throughput = (done_counts[-1] - done_counts[0]) / len(cfd_data['dates'])
            
            if avg_throughput > 0:
                avg_cycle_time = avg_wip / avg_throughput
            else:
                avg_cycle_time = 0
        else:
            avg_cycle_time = 0
        
        return {
            'avg_cycle_time': avg_cycle_time,
            'avg_wip': sum(cfd_data['columns'].get('In Progress', [0])) / len(cfd_data['dates']),
            'total_throughput': cfd_data['columns'].get('Done', [0])[-1]
        }

# 使用示例
# 假设已经有一个KanbanBoard实例
# board = KanbanBoard("示例项目")
# cfd = CumulativeFlowDiagram(board)

# 模拟记录快照
# for i in range(10):
#     cfd.record_snapshot()
#     # 模拟一些卡片移动
#     if i % 2 == 0:
#         board.move_card(i+1, "To Do")
#     if i % 3 == 0:
#         board.move_card(i+1, "In Progress")
#     if i % 4 == 0:
#         board.move_card(i+1, "Done")

# cfd.plot_cfd()
# metrics = cfd.calculate_flow_metrics()
# print(f"平均周期时间: {metrics['avg_cycle_time']:.1f}")
```

## 用户故事和估算

### 用户故事管理
```python
class UserStory:
    def __init__(self, title, description, acceptance_criteria, story_points=None):
        self.id = None
        self.title = title
        self.description = description
        self.acceptance_criteria = acceptance_criteria
        self.story_points = story_points
        self.priority = 1
        self.status = 'Backlog'
        self.assignee = None
        self.created_date = datetime.now()
        self.updated_date = datetime.now()
        self.tags = []
        
    def add_acceptance_criterion(self, criterion):
        """添加验收标准"""
        if criterion not in self.acceptance_criteria:
            self.acceptance_criteria.append(criterion)
            self.updated_date = datetime.now()
    
    def estimate_story_points(self, points):
        """估算故事点"""
        self.story_points = points
        self.updated_date = datetime.now()
    
    def add_tag(self, tag):
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_date = datetime.now()
    
    def get_formatted_story(self):
        """获取格式化的用户故事"""
        return f"作为一个 {self.get_user_role()}, " \
               f"我想要 {self.get_goal()}, " \
               f"以便 {self.get_value()}."
    
    def get_user_role(self):
        """提取用户角色"""
        # 简单的角色提取逻辑
        if "用户" in self.title:
            return "用户"
        elif "管理员" in self.title:
            return "管理员"
        elif "客户" in self.title:
            return "客户"
        else:
            return "用户"
    
    def get_goal(self):
        """提取目标"""
        # 简单的目标提取逻辑
        return self.title.replace("功能", "").replace("页面", "").strip()
    
    def get_value(self):
        """提取价值"""
        # 简单的价值提取逻辑
        if "登录" in self.title:
            return "能够安全地访问系统"
        elif "注册" in self.title:
            return "能够创建新账户"
        else:
            return "提高系统可用性"

class UserStoryManager:
    def __init__(self):
        self.stories = []
        self.epics = []
        
    def create_story(self, title, description, acceptance_criteria):
        """创建用户故事"""
        story = UserStory(title, description, acceptance_criteria)
        story.id = len(self.stories) + 1
        self.stories.append(story)
        return story
    
    def get_stories_by_priority(self):
        """按优先级获取故事"""
        return sorted(self.stories, key=lambda x: x.priority, reverse=True)
    
    def get_stories_by_status(self, status):
        """按状态获取故事"""
        return [story for story in self.stories if story.status == status]
    
    def estimate_stories_with_planning_poker(self, story_ids, team_members):
        """使用计划扑克估算故事点"""
        estimation_results = {}
        
        for story_id in story_ids:
            story = self.get_story(story_id)
            if story:
                # 模拟团队成员估算
                estimates = {}
                for member in team_members:
                    # 随机生成估算值 (1, 2, 3, 5, 8, 13, 20)
                    fibonacci = [1, 2, 3, 5, 8, 13, 20]
                    estimates[member] = np.random.choice(fibonacci)
                
                # 计算最终估算（取众数或平均值）
                final_estimate = max(set(estimates.values()), 
                                  key=list(estimates.values()).count)
                
                story.estimate_story_points(final_estimate)
                estimation_results[story_id] = {
                    'individual_estimates': estimates,
                    'final_estimate': final_estimate,
                    'consensus': len(set(estimates.values())) == 1
                }
        
        return estimation_results
    
    def get_story(self, story_id):
        """获取故事"""
        for story in self.stories:
            if story.id == story_id:
                return story
        return None
    
    def create_epic(self, title, description):
        """创建史诗"""
        epic = {
            'id': len(self.epics) + 1,
            'title': title,
            'description': description,
            'stories': [],
            'created_date': datetime.now()
        }
        self.epics.append(epic)
        return epic
    
    def add_story_to_epic(self, story_id, epic_id):
        """将故事添加到史诗"""
        story = self.get_story(story_id)
        epic = next((e for e in self.epics if e['id'] == epic_id), None)
        
        if story and epic and story_id not in epic['stories']:
            epic['stories'].append(story_id)
            story.add_tag(f"Epic-{epic_id}")

# 使用示例
import numpy as np

story_manager = UserStoryManager()

# 创建用户故事
story1 = story_manager.create_story(
    title="用户登录功能",
    description="用户可以通过用户名和密码登录系统",
    acceptance_criteria=[
        "Given 我在登录页面, When 我输入正确的用户名和密码, Then 我应该成功登录",
        "Given 我在登录页面, When 我输入错误的凭据, Then 我应该看到错误消息",
        "Given 我成功登录, Then 我应该被重定向到主页"
    ]
)

story2 = story_manager.create_story(
    title="用户注册功能",
    description="新用户可以创建账户",
    acceptance_criteria=[
        "Given 我在注册页面, When 我填写所有必填字段, Then 我应该成功注册",
        "Given 我使用已存在的邮箱注册, Then 我应该看到错误消息",
        "Given 我成功注册, Then 我应该收到确认邮件"
    ]
)

# 设置优先级
story1.priority = 10
story2.priority = 9

# 使用计划扑克估算
team_members = ['Alice', 'Bob', 'Charlie']
estimation_results = story_manager.estimate_stories_with_planning_poker(
    [1, 2], team_members
)

for story_id, result in estimation_results.items():
    story = story_manager.get_story(story_id)
    print(f"故事 '{story.title}' 估算结果:")
    print(f"  个人估算: {result['individual_estimates']}")
    print(f"  最终估算: {result['final_estimate']} 点")
    print(f"  达成共识: {'是' if result['consensus'] else '否'}")
    print()

# 创建史诗
epic = story_manager.create_epic("用户认证系统", "包含用户登录、注册和密码管理功能")
story_manager.add_story_to_epic(1, epic['id'])
story_manager.add_story_to_epic(2, epic['id'])

print(f"史诗 '{epic['title']}' 包含 {len(epic['stories'])} 个故事")
```

## 敏捷度量指标

### 关键敏捷指标
```python
class AgileMetrics:
    def __init__(self):
        self.sprint_data = []
        self.team_velocity_history = []
        self.cycle_times = []
        self.lead_times = []
        
    def add_sprint_data(self, sprint_number, planned_points, completed_points, 
                        team_capacity, sprint_days):
        """添加Sprint数据"""
        sprint_data = {
            'sprint_number': sprint_number,
            'planned_points': planned_points,
            'completed_points': completed_points,
            'team_capacity': team_capacity,
            'sprint_days': sprint_days,
            'utilization': completed_points / team_capacity * 100,
            'predictability': completed_points / planned_points * 100 if planned_points > 0 else 0
        }
        self.sprint_data.append(sprint_data)
        self.team_velocity_history.append(completed_points)
    
    def calculate_team_velocity(self, window_size=3):
        """计算团队速度"""
        if len(self.team_velocity_history) < window_size:
            return sum(self.team_velocity_history) / len(self.team_velocity_history)
        
        recent_velocities = self.team_velocity_history[-window_size:]
        return sum(recent_velocities) / window_size
    
    def calculate_velocity_stability(self):
        """计算速度稳定性"""
        if len(self.team_velocity_history) < 2:
            return 0
        
        mean_velocity = sum(self.team_velocity_history) / len(self.team_velocity_history)
        variance = sum((v - mean_velocity) ** 2 for v in self.team_velocity_history)
        std_dev = (variance / len(self.team_velocity_history)) ** 0.5
        
        # 稳定性 = 1 - (标准差 / 平均值)
        stability = max(0, 1 - (std_dev / mean_velocity)) if mean_velocity > 0 else 0
        return stability
    
    def calculate_burndown_rate(self, sprint_number):
        """计算燃尽率"""
        sprint_data = next((s for s in self.sprint_data if s['sprint_number'] == sprint_number), None)
        if not sprint_data:
            return 0
        
        # 理想燃尽率 = 总点数 / Sprint天数
        ideal_rate = sprint_data['planned_points'] / sprint_data['sprint_days']
        
        # 实际燃尽率 = 完成点数 / Sprint天数
        actual_rate = sprint_data['completed_points'] / sprint_data['sprint_days']
        
        return {
            'ideal_rate': ideal_rate,
            'actual_rate': actual_rate,
            'efficiency': actual_rate / ideal_rate if ideal_rate > 0 else 0
        }
    
    def add_cycle_time(self, item_id, cycle_time_days):
        """添加周期时间"""
        self.cycle_times.append({
            'item_id': item_id,
            'cycle_time': cycle_time_days,
            'date': datetime.now()
        })
    
    def add_lead_time(self, item_id, lead_time_days):
        """添加前置时间"""
        self.lead_times.append({
            'item_id': item_id,
            'lead_time': lead_time_days,
            'date': datetime.now()
        })
    
    def calculate_flow_efficiency(self):
        """计算流动效率"""
        if not self.cycle_times or not self.lead_times:
            return 0
        
        avg_cycle_time = sum(c['cycle_time'] for c in self.cycle_times) / len(self.cycle_times)
        avg_lead_time = sum(l['lead_time'] for l in self.lead_times) / len(self.lead_times)
        
        efficiency = avg_cycle_time / avg_lead_time if avg_lead_time > 0 else 0
        return efficiency
    
    def calculate_throughput(self, days=30):
        """计算吞吐量"""
        if not self.cycle_times:
            return 0
        
        # 计算最近30天的吞吐量
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_items = [c for c in self.cycle_times if c['date'] >= cutoff_date]
        
        return len(recent_items) / days
    
    def generate_metrics_report(self):
        """生成度量报告"""
        if not self.sprint_data:
            return "没有Sprint数据可用"
        
        report = "敏捷度量报告\n"
        report += "=" * 40 + "\n\n"
        
        # 速度指标
        avg_velocity = self.calculate_team_velocity()
        velocity_stability = self.calculate_velocity_stability()
        
        report += "速度指标:\n"
        report += f"  平均速度: {avg_velocity:.1f} 点/Sprint\n"
        report += f"  速度稳定性: {velocity_stability:.1%}\n\n"
        
        # 利用率和可预测性
        latest_sprint = self.sprint_data[-1]
        report += "最新Sprint指标:\n"
        report += f"  利用率: {latest_sprint['utilization']:.1%}\n"
        report += f"  可预测性: {latest_sprint['predictability']:.1%}\n\n"
        
        # 流动指标
        flow_efficiency = self.calculate_flow_efficiency()
        throughput = self.calculate_throughput()
        
        report += "流动指标:\n"
        report += f"  流动效率: {flow_efficiency:.1%}\n"
        report += f"  吞吐量: {throughput:.1f} 项/天\n\n"
        
        # 趋势分析
        if len(self.team_velocity_history) >= 3:
            recent_velocity = self.team_velocity_history[-3:]
            trend = "上升" if recent_velocity[-1] > recent_velocity[0] else "下降"
            report += f"速度趋势: {trend}\n"
        
        return report
    
    def plot_velocity_trend(self):
        """绘制速度趋势图"""
        if len(self.team_velocity_history) < 2:
            print("数据不足，无法绘制趋势图")
            return
        
        plt.figure(figsize=(10, 6))
        
        sprint_numbers = list(range(1, len(self.team_velocity_history) + 1))
        velocities = self.team_velocity_history
        
        plt.plot(sprint_numbers, velocities, marker='o', linewidth=2, markersize=8)
        plt.axhline(y=sum(velocities)/len(velocities), color='r', linestyle='--', 
                   label=f'平均速度 ({sum(velocities)/len(velocities):.1f})')
        
        plt.xlabel('Sprint编号')
        plt.ylabel('速度 (故事点)')
        plt.title('团队速度趋势')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_burndown_chart(self, sprint_number):
        """绘制燃尽图"""
        sprint_data = next((s for s in self.sprint_data if s['sprint_number'] == sprint_number), None)
        if not sprint_data:
            print(f"没有找到Sprint {sprint_number} 的数据")
            return
        
        # 生成模拟的每日燃尽数据
        days = list(range(0, sprint_data['sprint_days'] + 1))
        
        # 理想燃尽线
        ideal_burndown = [
            sprint_data['planned_points'] - (sprint_data['planned_points'] * day / sprint_data['sprint_days'])
            for day in days
        ]
        
        # 模拟实际燃尽线（基于实际完成情况）
        actual_burndown = [sprint_data['planned_points']]
        remaining_points = sprint_data['planned_points']
        daily_completion = sprint_data['completed_points'] / sprint_data['sprint_days']
        
        for day in range(1, sprint_data['sprint_days'] + 1):
            # 添加一些随机性来模拟实际情况
            daily_actual = daily_completion * (0.8 + np.random.random() * 0.4)
            remaining_points = max(0, remaining_points - daily_actual)
            actual_burndown.append(remaining_points)
        
        plt.figure(figsize=(10, 6))
        plt.plot(days, ideal_burndown, 'g--', label='理想燃尽', linewidth=2)
        plt.plot(days, actual_burndown, 'b-', label='实际燃尽', linewidth=2, marker='o')
        
        plt.xlabel('Sprint天数')
        plt.ylabel('剩余故事点')
        plt.title(f'Sprint {sprint_number} 燃尽图')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

# 使用示例
metrics = AgileMetrics()

# 添加Sprint数据
metrics.add_sprint_data(1, 20, 18, 20, 10)
metrics.add_sprint_data(2, 22, 20, 20, 10)
metrics.add_sprint_data(3, 25, 23, 20, 10)
metrics.add_sprint_data(4, 21, 19, 20, 10)
metrics.add_sprint_data(5, 24, 22, 20, 10)

# 添加流动时间数据
metrics.add_cycle_time(1, 3)
metrics.add_cycle_time(2, 5)
metrics.add_cycle_time(3, 4)
metrics.add_cycle_time(4, 6)

metrics.add_lead_time(1, 7)
metrics.add_lead_time(2, 10)
metrics.add_lead_time(3, 8)
metrics.add_lead_time(4, 12)

# 生成报告
report = metrics.generate_metrics_report()
print(report)

# 绘制图表
metrics.plot_velocity_trend()
metrics.plot_burndown_chart(5)
```

## 参考资源

### 敏捷框架官方资源
- [Scrum Guide](https://scrumguides.org/)
- [Kanban Guide](https://kanban.zealand.com/)
- [SAFe Framework](https://www.scaledagileframework.com/)
- [LeSS Framework](https://less.works/)

### 敏捷工具和平台
- [Atlassian Jira](https://www.atlassian.com/software/jira)
- [Azure DevOps](https://azure.microsoft.com/en-us/services/devops/)
- [Trello](https://trello.com/)
- [Asana](https://asana.com/)
- [ClickUp](https://clickup.com/)

### 敏捷认证和培训
- [Scrum.org](https://www.scrum.org/)
- [Scrum Alliance](https://www.scrumalliance.org/)
- [Scaled Agile](https://www.scaledagile.com/)
- [Kanban University](https://kanban.university/)

### 敏捷社区和博客
- [Agile Alliance](https://www.agilealliance.org/)
- [Mountain Goat Software](https://www.mountaingoatsoftware.com/)
- [InfoQ Agile](https://www.infoq.com/agile/)
- [Scrum.org Blog](https://www.scrum.org/blog/)

### 敏捷实践资源
- [User Stories Guide](https://www.atlassian.com/agile/project-management/user-stories)
- [Agile Estimating and Planning](https://www.mountaingoatsoftware.com/agile-planning/)
- [Agile Metrics](https://www.atlassian.com/agile/project-management/agile-metrics)
- [Retrospectives Guide](https://www.atlassian.com/agile/project-management/retrospectives/)
