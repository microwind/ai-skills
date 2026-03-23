# 异步任务参考文档

## 异步任务概述

### 什么是异步任务
异步任务是一种在后台执行的非阻塞操作模式，允许主程序继续执行而不等待任务完成。该技能涵盖了后台任务处理、定时任务调度、队列管理、错误处理、监控告警等功能，帮助开发者构建高效、可靠、可扩展的异步任务系统。

### 主要功能
- **任务调度**: 支持定时任务、延迟任务、周期性任务和一次性任务
- **队列管理**: 支持内存队列、Redis队列、RabbitMQ队列等多种队列类型
- **并发控制**: 提供线程池、进程池、协程池等并发执行机制
- **错误处理**: 包含重试机制、死信队列、错误分类和恢复策略
- **监控告警**: 实时监控任务状态、性能指标和异常告警

## 异步任务引擎

### 核心任务管理器
```python
# async_task_manager.py
import asyncio
import threading
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import hashlib
import pickle
import redis
import celery
from celery import Celery
import schedule

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class Task:
    id: str
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    timeout: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskConfig:
    # 执行配置
    max_workers: int = 10
    worker_type: str = "thread"  # thread, process, coroutine
    timeout: float = 300.0
    
    # 队列配置
    queue_type: str = "memory"  # memory, redis, rabbitmq
    queue_size: int = 1000
    queue_name: str = "default"
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    
    # 监控配置
    enable_monitoring: bool = True
    monitoring_interval: float = 5.0
    
    # 持久化配置
    enable_persistence: bool = True
    storage_path: str = "./tasks"

class AsyncTaskManager:
    def __init__(self, config: TaskConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.tasks: Dict[str, Task] = {}
        self.task_queue: queue.Queue = queue.Queue(maxsize=config.queue_size)
        self.running_tasks: Dict[str, threading.Thread] = {}
        self.worker_pool = None
        self.monitor_thread = None
        self.running = False
        
        # 初始化组件
        self._init_queue()
        self._init_workers()
        self._init_monitoring()
    
    def _init_queue(self):
        """初始化队列"""
        if self.config.queue_type == "memory":
            self.task_queue = queue.Queue(maxsize=self.config.queue_size)
        elif self.config.queue_type == "redis":
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.task_queue = RedisQueue(self.redis_client, self.config.queue_name)
        elif self.config.queue_type == "rabbitmq":
            import pika
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            self.channel = self.rabbitmq_connection.channel()
            self.channel.queue_declare(queue=self.config.queue_name)
            self.task_queue = RabbitMQQueue(self.channel, self.config.queue_name)
    
    def _init_workers(self):
        """初始化工作线程池"""
        if self.config.worker_type == "thread":
            self.worker_pool = ThreadPoolExecutor(max_workers=self.config.max_workers)
        elif self.config.worker_type == "process":
            self.worker_pool = ProcessPoolExecutor(max_workers=self.config.max_workers)
        elif self.config.worker_type == "coroutine":
            self.worker_pool = AsyncioExecutor()
    
    def _init_monitoring(self):
        """初始化监控"""
        if self.config.enable_monitoring:
            self.monitor_thread = threading.Thread(target=self._monitor_tasks, daemon=True)
    
    def start(self):
        """启动任务管理器"""
        self.running = True
        self.logger.info("异步任务管理器启动")
        
        # 启动监控线程
        if self.monitor_thread:
            self.monitor_thread.start()
        
        # 启动工作线程
        self._start_workers()
    
    def stop(self):
        """停止任务管理器"""
        self.running = False
        self.logger.info("异步任务管理器停止")
        
        # 等待所有任务完成
        self._wait_for_completion()
        
        # 关闭工作线程池
        if self.worker_pool:
            self.worker_pool.shutdown(wait=True)
    
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """提交任务"""
        task_id = self._generate_task_id()
        task = Task(
            id=task_id,
            name=func.__name__,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=kwargs.pop('priority', TaskPriority.NORMAL),
            max_retries=kwargs.pop('max_retries', self.config.max_retries),
            timeout=kwargs.pop('timeout', self.config.timeout),
            scheduled_at=kwargs.pop('scheduled_at', None),
            metadata=kwargs.pop('metadata', {})
        )
        
        self.tasks[task_id] = task
        
        try:
            if task.scheduled_at and task.scheduled_at > datetime.now():
                # 延迟任务
                self._schedule_delayed_task(task)
            else:
                # 立即执行
                self.task_queue.put(task)
            
            self.logger.info(f"任务提交成功: {task_id}")
            return task_id
        
        except queue.Full:
            self.logger.error(f"任务队列已满，无法提交任务: {task_id}")
            raise RuntimeError("任务队列已满")
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        timestamp = str(int(time.time() * 1000))
        random_str = str(hash(time.time()))[-8:]
        return f"task_{timestamp}_{random_str}"
    
    def _schedule_delayed_task(self, task: Task):
        """调度延迟任务"""
        delay = (task.scheduled_at - datetime.now()).total_seconds()
        if delay > 0:
            timer = threading.Timer(delay, self.task_queue.put, args=[task])
            timer.daemon = True
            timer.start()
    
    def _start_workers(self):
        """启动工作线程"""
        for i in range(self.config.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.running_tasks[f"worker_{i}"] = worker
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1.0)
                if task:
                    self._execute_task(task)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"工作线程异常: {e}")
    
    def _execute_task(self, task: Task):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            self.logger.info(f"开始执行任务: {task.id}")
            
            # 提交到工作线程池
            if self.config.worker_type == "coroutine":
                future = self.worker_pool.submit(task.func, *task.args, **task.kwargs)
            else:
                future = self.worker_pool.submit(self._run_task_with_timeout, task)
            
            # 等待结果
            task.result = future.result(timeout=task.timeout)
            task.status = TaskStatus.SUCCESS
            task.completed_at = datetime.now()
            
            self.logger.info(f"任务执行成功: {task.id}")
        
        except Exception as e:
            task.error = e
            task.status = TaskStatus.FAILURE
            task.completed_at = datetime.now()
            
            self.logger.error(f"任务执行失败: {task.id}, 错误: {e}")
            
            # 重试逻辑
            if task.retry_count < task.max_retries:
                self._retry_task(task)
        
        finally:
            # 持久化任务状态
            if self.config.enable_persistence:
                self._save_task_state(task)
    
    def _run_task_with_timeout(self, task: Task):
        """带超时的任务执行"""
        if self.config.worker_type == "coroutine":
            return asyncio.run(task.func(*task.args, **task.kwargs))
        else:
            return task.func(*task.args, **task.kwargs)
    
    def _retry_task(self, task: Task):
        """重试任务"""
        task.retry_count += 1
        task.status = TaskStatus.RETRY
        
        # 计算重试延迟
        retry_delay = self.config.retry_delay * (self.config.retry_backoff ** (task.retry_count - 1))
        
        # 延迟后重新提交
        timer = threading.Timer(retry_delay, self.task_queue.put, args=[task])
        timer.daemon = True
        timer.start()
        
        self.logger.info(f"任务重试: {task.id}, 第{task.retry_count}次重试")
    
    def _monitor_tasks(self):
        """监控任务"""
        while self.running:
            try:
                self._collect_metrics()
                self._cleanup_completed_tasks()
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"监控异常: {e}")
    
    def _collect_metrics(self):
        """收集指标"""
        total_tasks = len(self.tasks)
        pending_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        running_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        success_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.SUCCESS)
        failure_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILURE)
        
        metrics = {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'running_tasks': running_tasks,
            'success_tasks': success_tasks,
            'failure_tasks': failure_tasks,
            'success_rate': success_tasks / total_tasks if total_tasks > 0 else 0,
            'queue_size': self.task_queue.qsize() if hasattr(self.task_queue, 'qsize') else 0
        }
        
        self.logger.info(f"任务指标: {metrics}")
    
    def _cleanup_completed_tasks(self):
        """清理已完成的任务"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        completed_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILURE] 
            and task.completed_at 
            and task.completed_at < cutoff_time
        ]
        
        for task_id in completed_tasks:
            del self.tasks[task_id]
    
    def _save_task_state(self, task: Task):
        """保存任务状态"""
        if not self.config.enable_persistence:
            return
        
        try:
            os.makedirs(self.config.storage_path, exist_ok=True)
            filename = os.path.join(self.config.storage_path, f"{task.id}.json")
            
            task_data = asdict(task)
            # 序列化日期时间
            for key, value in task_data.items():
                if isinstance(value, datetime):
                    task_data[key] = value.isoformat()
                elif key == 'func':
                    task_data[key] = value.__name__ if value else None
                elif key == 'error':
                    task_data[key] = str(value) if value else None
            
            with open(filename, 'w') as f:
                json.dump(task_data, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"保存任务状态失败: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_task_result(self, task_id: str) -> Any:
        """获取任务结果"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.SUCCESS:
            return task.result
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RETRY]:
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"任务已取消: {task_id}")
            return True
        return False
    
    def _wait_for_completion(self):
        """等待所有任务完成"""
        while any(task.status == TaskStatus.RUNNING for task in self.tasks.values()):
            time.sleep(0.1)

class RedisQueue:
    """Redis队列实现"""
    def __init__(self, redis_client, queue_name):
        self.redis = redis_client
        self.queue_name = queue_name
    
    def put(self, task):
        """放入任务"""
        task_data = pickle.dumps(task)
        self.redis.lpush(self.queue_name, task_data)
    
    def get(self, timeout=None):
        """获取任务"""
        task_data = self.redis.brpop(self.queue_name, timeout=timeout)
        if task_data:
            return pickle.loads(task_data[1])
        return None
    
    def qsize(self):
        """队列大小"""
        return self.redis.llen(self.queue_name)

class RabbitMQQueue:
    """RabbitMQ队列实现"""
    def __init__(self, channel, queue_name):
        self.channel = channel
        self.queue_name = queue_name
    
    def put(self, task):
        """放入任务"""
        task_data = pickle.dumps(task)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=task_data
        )
    
    def get(self, timeout=None):
        """获取任务"""
        method, properties, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        if body:
            return pickle.loads(body)
        return None
    
    def qsize(self):
        """队列大小"""
        result = self.channel.queue_declare(queue=self.queue_name, passive=True)
        return result.method.message_count

class AsyncioExecutor:
    """异步执行器"""
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor()
    
    def submit(self, func, *args, **kwargs):
        """提交异步任务"""
        if asyncio.iscoroutinefunction(func):
            return self.loop.run_in_executor(self.executor, lambda: asyncio.run(func(*args, **kwargs)))
        else:
            return self.loop.run_in_executor(self.executor, func, *args, **kwargs)

# 使用示例
# 定义任务函数
def send_email_task(to, subject, body):
    """发送邮件任务"""
    time.sleep(2)  # 模拟邮件发送
    print(f"发送邮件到 {to}: {subject}")
    return f"邮件发送成功: {to}"

def process_data_task(data):
    """处理数据任务"""
    time.sleep(1)  # 模拟数据处理
    result = sum(data)
    print(f"处理数据: {data} -> {result}")
    return result

def backup_database_task():
    """备份数据库任务"""
    time.sleep(5)  # 模拟数据库备份
    print("数据库备份完成")
    return "备份成功"

# 配置任务管理器
config = TaskConfig(
    max_workers=5,
    worker_type="thread",
    queue_type="memory",
    queue_size=100,
    max_retries=3,
    retry_delay=2.0,
    enable_monitoring=True,
    monitoring_interval=5.0,
    enable_persistence=True
)

# 创建任务管理器
task_manager = AsyncTaskManager(config)

# 启动任务管理器
task_manager.start()

# 提交任务
task1_id = task_manager.submit_task(send_email_task, "user@example.com", "测试邮件", "这是测试内容")
task2_id = task_manager.submit_task(process_data_task, [1, 2, 3, 4, 5])
task3_id = task_manager.submit_task(backup_database_task)

# 提交延迟任务
from datetime import datetime, timedelta
scheduled_time = datetime.now() + timedelta(seconds=10)
task4_id = task_manager.submit_task(send_email_task, "delayed@example.com", "延迟邮件", "这是延迟发送的邮件", scheduled_at=scheduled_time)

# 等待任务完成
time.sleep(15)

# 检查任务状态
for task_id in [task1_id, task2_id, task3_id, task4_id]:
    task = task_manager.get_task_status(task_id)
    if task:
        print(f"任务 {task_id}: {task.status.value}")
        if task.status == TaskStatus.SUCCESS:
            print(f"  结果: {task.result}")

# 停止任务管理器
task_manager.stop()
```

## 定时任务调度器

### Cron调度器
```python
# cron_scheduler.py
import time
import threading
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from croniter import croniter
import schedule

@dataclass
class ScheduledTask:
    id: str
    name: str
    func: Callable
    cron_expression: str
    args: tuple = ()
    kwargs: dict = None
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    timezone: str = "UTC"

class CronScheduler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_thread = None
    
    def add_task(self, 
                 name: str, 
                 func: Callable, 
                 cron_expression: str, 
                 *args, 
                 **kwargs) -> str:
        """添加定时任务"""
        task_id = f"cron_{int(time.time())}"
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            func=func,
            cron_expression=cron_expression,
            args=args,
            kwargs=kwargs or {},
            next_run=self._get_next_run_time(cron_expression)
        )
        
        self.tasks[task_id] = task
        self.logger.info(f"添加定时任务: {name} ({cron_expression})")
        
        return task_id
    
    def _get_next_run_time(self, cron_expression: str) -> datetime:
        """获取下次运行时间"""
        cron = croniter(cron_expression, datetime.now())
        return cron.get_next(datetime)
    
    def remove_task(self, task_id: str) -> bool:
        """移除定时任务"""
        if task_id in self.tasks:
            task_name = self.tasks[task_id].name
            del self.tasks[task_id]
            self.logger.info(f"移除定时任务: {task_name}")
            return True
        return False
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("定时任务调度器启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        self.logger.info("定时任务调度器停止")
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for task in self.tasks.values():
                    if (task.enabled and 
                        task.next_run and 
                        current_time >= task.next_run):
                        
                        self._execute_scheduled_task(task)
                
                time.sleep(1)  # 每秒检查一次
            
            except Exception as e:
                self.logger.error(f"调度器异常: {e}")
    
    def _execute_scheduled_task(self, task: ScheduledTask):
        """执行定时任务"""
        try:
            self.logger.info(f"执行定时任务: {task.name}")
            
            # 执行任务
            result = task.func(*task.args, **task.kwargs)
            
            # 更新任务状态
            task.last_run = datetime.now()
            task.next_run = self._get_next_run_time(task.cron_expression)
            
            self.logger.info(f"定时任务执行完成: {task.name}")
        
        except Exception as e:
            self.logger.error(f"定时任务执行失败: {task.name}, 错误: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[ScheduledTask]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            return True
        return False

# 使用示例
# 定义定时任务函数
def daily_backup():
    """每日备份任务"""
    print(f"执行每日备份: {datetime.now()}")

def hourly_cleanup():
    """每小时清理任务"""
    print(f"执行每小时清理: {datetime.now()}")

def weekly_report():
    """每周报告任务"""
    print(f"生成每周报告: {datetime.now()}")

# 创建调度器
scheduler = CronScheduler()

# 添加定时任务
scheduler.add_task("每日备份", daily_backup, "0 2 * * *")  # 每天凌晨2点
scheduler.add_task("每小时清理", hourly_cleanup, "0 * * * *")  # 每小时整点
scheduler.add_task("每周报告", weekly_report, "0 9 * * 1")  # 每周一上午9点

# 启动调度器
scheduler.start()

# 运行一段时间
time.sleep(10)

# 停止调度器
scheduler.stop()
```

## 参考资源

### 异步编程
- [Python asyncio文档](https://docs.python.org/3/library/asyncio.html)
- [Celery分布式任务队列](https://docs.celeryproject.org/)
- [RQ简单任务队列](https://python-rq.org/)
- [asyncio最佳实践](https://docs.python.org/3/library/asyncio-dev.html)

### 队列系统
- [Redis队列](https://redis.io/documentation)
- [RabbitMQ消息队列](https://www.rabbitmq.com/documentation.html)
- [Apache Kafka](https://kafka.apache.org/documentation/)
- [Amazon SQS](https://docs.aws.amazon.com/sqs/)

### 任务调度
- [APScheduler任务调度](https://apscheduler.readthedocs.io/)
- [Cron表达式教程](https://crontab.guru/)
- [schedule库](https://schedule.readthedocs.io/)
- [Airflow工作流](https://airflow.apache.org/docs/)

### 监控和日志
- [Python logging模块](https://docs.python.org/3/library/logging.html)
- [Prometheus监控](https://prometheus.io/docs/)
- [Grafana可视化](https://grafana.com/docs/)
- [ELK日志栈](https://www.elastic.co/guide/)
