# 性能监控器参考文档

## 性能监控器概述

### 什么是性能监控器
性能监控器是一个综合性的系统监控工具，用于实时收集、分析和展示应用程序、系统和业务的性能指标。该工具支持多种监控目标，包括应用性能、系统资源、用户体验和业务指标，提供智能告警、可视化展示和数据分析功能，帮助运维团队及时发现性能问题、优化系统性能和提升用户体验。

### 主要功能
- **多维度监控**: 支持应用、系统、网络、数据库等多维度性能监控
- **实时数据收集**: 实时收集和处理性能指标数据
- **智能告警**: 基于阈值、趋势和异常检测的智能告警系统
- **可视化展示**: 丰富的图表和仪表板展示
- **业务指标**: 支持自定义业务指标监控和分析
- **用户体验**: 监控前端和移动应用的用户体验指标
- **集成能力**: 与主流监控工具和系统集成

## 性能数据收集引擎

### 数据收集器
```python
# data_collector.py
import time
import threading
import psutil
import requests
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import logging

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class MetricUnit(Enum):
    COUNT = "count"
    PERCENT = "percent"
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    BYTES = "bytes"
    REQUESTS_PER_SECOND = "requests_per_second"

@dataclass
class Metric:
    name: str
    value: float
    metric_type: MetricType
    unit: MetricUnit
    timestamp: datetime
    labels: Dict[str, str] = None
    tags: Dict[str, str] = None

@dataclass
class MetricFamily:
    name: str
    help_text: str
    metric_type: MetricType
    metrics: List[Metric]

class DataCollector:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.collectors = {}
        self.is_running = False
        self.collection_interval = 60  # 默认60秒
        self.max_metrics_per_family = 1000
        self.logger = logging.getLogger(__name__)
        
        # 注册默认收集器
        self._register_default_collectors()
    
    def _register_default_collectors(self):
        """注册默认收集器"""
        self.collectors['system'] = SystemMetricsCollector()
        self.collectors['application'] = ApplicationMetricsCollector()
        self.collectors['network'] = NetworkMetricsCollector()
        self.collectors['process'] = ProcessMetricsCollector()
    
    def register_collector(self, name: str, collector):
        """注册自定义收集器"""
        self.collectors[name] = collector
    
    def start_collection(self, interval: int = 60):
        """开始数据收集"""
        self.collection_interval = interval
        self.is_running = True
        
        def collection_worker():
            while self.is_running:
                try:
                    self._collect_all_metrics()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"数据收集错误: {e}")
        
        thread = threading.Thread(target=collection_worker)
        thread.daemon = True
        thread.start()
        
        self.logger.info(f"数据收集已启动，间隔: {interval}秒")
    
    def stop_collection(self):
        """停止数据收集"""
        self.is_running = False
        self.logger.info("数据收集已停止")
    
    def _collect_all_metrics(self):
        """收集所有指标"""
        timestamp = datetime.now()
        
        for name, collector in self.collectors.items():
            try:
                metrics = collector.collect()
                for metric in metrics:
                    metric.timestamp = timestamp
                    self._add_metric(metric)
            except Exception as e:
                self.logger.error(f"收集器 {name} 错误: {e}")
    
    def _add_metric(self, metric: Metric):
        """添加指标"""
        family_name = metric.name
        
        # 限制指标数量
        if len(self.metrics[family_name]) >= self.max_metrics_per_family:
            self.metrics[family_name].pop(0)
        
        self.metrics[family_name].append(metric)
    
    def get_metrics(self, metric_name: str = None, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> List[Metric]:
        """获取指标"""
        if metric_name:
            metrics = self.metrics.get(metric_name, [])
        else:
            metrics = []
            for family_metrics in self.metrics.values():
                metrics.extend(family_metrics)
        
        # 时间过滤
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        return metrics
    
    def get_metric_families(self) -> Dict[str, MetricFamily]:
        """获取指标族"""
        families = {}
        
        for name, metrics in self.metrics.items():
            if metrics:
                latest_metric = metrics[-1]
                families[name] = MetricFamily(
                    name=name,
                    help_text=f"指标 {name}",
                    metric_type=latest_metric.metric_type,
                    metrics=metrics
                )
        
        return families
    
    def add_metric(self, name: str, value: float, metric_type: MetricType,
                   unit: MetricUnit, labels: Dict[str, str] = None,
                   tags: Dict[str, str] = None):
        """手动添加指标"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            unit=unit,
            timestamp=datetime.now(),
            labels=labels,
            tags=tags
        )
        
        self._add_metric(metric)
    
    def increment_counter(self, name: str, value: float = 1.0,
                        labels: Dict[str, str] = None,
                        tags: Dict[str, str] = None):
        """递增计数器"""
        self.add_metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT,
            labels=labels,
            tags=tags
        )
    
    def set_gauge(self, name: str, value: float,
                 labels: Dict[str, str] = None,
                 tags: Dict[str, str] = None):
        """设置仪表盘值"""
        self.add_metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.COUNT,
            labels=labels,
            tags=tags
        )
    
    def record_histogram(self, name: str, value: float,
                       labels: Dict[str, str] = None,
                       tags: Dict[str, str] = None):
        """记录直方图"""
        self.add_metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            unit=MetricUnit.MILLISECONDS,
            labels=labels,
            tags=tags
        )

# 基础收集器抽象类
class BaseCollector:
    def collect(self) -> List[Metric]:
        """收集指标"""
        raise NotImplementedError

class SystemMetricsCollector(BaseCollector):
    """系统指标收集器"""
    
    def collect(self) -> List[Metric]:
        """收集系统指标"""
        metrics = []
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(Metric(
            name="system_cpu_usage",
            value=cpu_percent,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.PERCENT
        ))
        
        # 内存使用率
        memory = psutil.virtual_memory()
        metrics.append(Metric(
            name="system_memory_usage",
            value=memory.percent,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.PERCENT
        ))
        
        metrics.append(Metric(
            name="system_memory_total",
            value=memory.total,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.BYTES
        ))
        
        metrics.append(Metric(
            name="system_memory_available",
            value=memory.available,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.BYTES
        ))
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        metrics.append(Metric(
            name="system_disk_usage",
            value=disk_percent,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.PERCENT
        ))
        
        # 系统负载
        load_avg = psutil.getloadavg()
        metrics.append(Metric(
            name="system_load_1m",
            value=load_avg[0],
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.COUNT
        ))
        
        metrics.append(Metric(
            name="system_load_5m",
            value=load_avg[1],
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.COUNT
        ))
        
        metrics.append(Metric(
            name="system_load_15m",
            value=load_avg[2],
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.COUNT
        ))
        
        return metrics

class ApplicationMetricsCollector(BaseCollector):
    """应用指标收集器"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
    
    def collect(self) -> List[Metric]:
        """收集应用指标"""
        metrics = []
        
        # 请求计数
        metrics.append(Metric(
            name="application_requests_total",
            value=self.request_count,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT
        ))
        
        # 错误计数
        metrics.append(Metric(
            name="application_errors_total",
            value=self.error_count,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT
        ))
        
        # 错误率
        if self.request_count > 0:
            error_rate = (self.error_count / self.request_count) * 100
            metrics.append(Metric(
                name="application_error_rate",
                value=error_rate,
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.PERCENT
            ))
        
        # 平均响应时间
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            metrics.append(Metric(
                name="application_response_time_avg",
                value=avg_response_time,
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.MILLISECONDS
            ))
        
        return metrics
    
    def record_request(self, response_time: float, is_error: bool = False):
        """记录请求"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if is_error:
            self.error_count += 1

class NetworkMetricsCollector(BaseCollector):
    """网络指标收集器"""
    
    def collect(self) -> List[Metric]:
        """收集网络指标"""
        metrics = []
        
        # 网络I/O
        net_io = psutil.net_io_counters()
        
        metrics.append(Metric(
            name="network_bytes_sent",
            value=net_io.bytes_sent,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.BYTES
        ))
        
        metrics.append(Metric(
            name="network_bytes_recv",
            value=net_io.bytes_recv,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.BYTES
        ))
        
        metrics.append(Metric(
            name="network_packets_sent",
            value=net_io.packets_sent,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT
        ))
        
        metrics.append(Metric(
            name="network_packets_recv",
            value=net_io.packets_recv,
            metric_type=MetricType.COUNTER,
            unit=MetricUnit.COUNT
        ))
        
        # 网络连接数
        connections = psutil.net_connections()
        active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
        
        metrics.append(Metric(
            name="network_connections_active",
            value=active_connections,
            metric_type=MetricType.GAUGE,
            unit=MetricUnit.COUNT
        ))
        
        return metrics

class ProcessMetricsCollector(BaseCollector):
    """进程指标收集器"""
    
    def __init__(self, pid: int = None):
        self.pid = pid or os.getpid()
        self.process = psutil.Process(self.pid)
    
    def collect(self) -> List[Metric]:
        """收集进程指标"""
        metrics = []
        
        try:
            # 进程CPU使用率
            cpu_percent = self.process.cpu_percent()
            metrics.append(Metric(
                name="process_cpu_usage",
                value=cpu_percent,
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.PERCENT
            ))
            
            # 进程内存使用
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            metrics.append(Metric(
                name="process_memory_usage",
                value=memory_percent,
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.PERCENT
            ))
            
            metrics.append(Metric(
                name="process_memory_rss",
                value=memory_info.rss,
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.BYTES
            ))
            
            metrics.append(Metric(
                name="process_memory_vms",
                value=memory_info.vms,
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.BYTES
            ))
            
            # 进程文件描述符
            try:
                num_fds = self.process.num_fds()
                metrics.append(Metric(
                    name="process_file_descriptors",
                    value=num_fds,
                    metric_type=MetricType.GAUGE,
                    unit=MetricUnit.COUNT
                ))
            except (AttributeError, psutil.AccessDenied):
                pass
            
            # 进程线程数
            try:
                num_threads = self.process.num_threads()
                metrics.append(Metric(
                    name="process_threads",
                    value=num_threads,
                    metric_type=MetricType.GAUGE,
                    unit=MetricUnit.COUNT
                ))
            except (AttributeError, psutil.AccessDenied):
                pass
            
        except psutil.NoSuchProcess:
            pass
        
        return metrics

# 使用示例
collector = DataCollector()

# 启动数据收集
collector.start_collection(interval=30)

# 手动添加指标
collector.increment_counter("custom_requests", labels={"endpoint": "/api/users"})
collector.set_gauge("active_sessions", 150)
collector.record_histogram("response_time", 125.5, labels={"method": "GET"})

# 获取指标
system_metrics = collector.get_metrics("system_cpu_usage")
all_metrics = collector.get_metrics()

# 获取指标族
families = collector.get_metric_families()
for name, family in families.items():
    print(f"指标族: {name}, 类型: {family.metric_type.value}")

# 等待收集数据
time.sleep(60)

# 停止收集
collector.stop_collection()
```

## 告警引擎

### 告警系统
```python
# alert_engine.py
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging
from data_collector import Metric, DataCollector

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"

@dataclass
class AlertRule:
    name: str
    condition: str
    severity: AlertSeverity
    threshold: float
    duration: int  # 持续时间（秒）
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    enabled: bool = True

@dataclass
class Alert:
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    value: float = 0.0

@dataclass
class AlertNotification:
    alert: Alert
    channels: List[str]
    sent_at: datetime
    success: bool
    error_message: Optional[str] = None

class AlertEngine:
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.rules = {}
        self.alerts = {}
        self.notification_handlers = {}
        self.is_running = False
        self.evaluation_interval = 30  # 默认30秒
        self.logger = logging.getLogger(__name__)
        
        # 告警状态跟踪
        self.rule_states = defaultdict(lambda: {
            'last_evaluation': None,
            'firing_since': None,
            'alert_sent': False
        })
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.name] = rule
        self.logger.info(f"添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"移除告警规则: {rule_name}")
    
    def add_notification_handler(self, channel: str, handler: Callable[[Alert], bool]):
        """添加通知处理器"""
        self.notification_handlers[channel] = handler
        self.logger.info(f"添加通知处理器: {channel}")
    
    def start_evaluation(self, interval: int = 30):
        """开始告警评估"""
        self.evaluation_interval = interval
        self.is_running = True
        
        def evaluation_worker():
            while self.is_running:
                try:
                    self._evaluate_all_rules()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"告警评估错误: {e}")
        
        thread = threading.Thread(target=evaluation_worker)
        thread.daemon = True
        thread.start()
        
        self.logger.info(f"告警评估已启动，间隔: {interval}秒")
    
    def stop_evaluation(self):
        """停止告警评估"""
        self.is_running = False
        self.logger.info("告警评估已停止")
    
    def _evaluate_all_rules(self):
        """评估所有规则"""
        current_time = datetime.now()
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                self._evaluate_rule(rule, current_time)
            except Exception as e:
                self.logger.error(f"评估规则 {rule_name} 错误: {e}")
    
    def _evaluate_rule(self, rule: AlertRule, current_time: datetime):
        """评估单个规则"""
        state = self.rule_states[rule_name]
        
        # 解析条件并获取指标值
        metric_value = self._evaluate_condition(rule.condition)
        
        if metric_value is None:
            return
        
        # 检查是否触发告警
        is_firing = self._check_threshold(metric_value, rule.threshold, rule.condition)
        
        state['last_evaluation'] = current_time
        
        if is_firing:
            # 告警触发
            if state['firing_since'] is None:
                state['firing_since'] = current_time
            
            # 检查是否满足持续时间
            firing_duration = (current_time - state['firing_since']).total_seconds()
            
            if firing_duration >= rule.duration:
                if not state['alert_sent']:
                    self._fire_alert(rule, metric_value, current_time)
                    state['alert_sent'] = True
        else:
            # 告警恢复
            if state['firing_since'] is not None:
                self._resolve_alert(rule, current_time)
                state['firing_since'] = None
                state['alert_sent'] = False
    
    def _evaluate_condition(self, condition: str) -> Optional[float]:
        """评估条件表达式"""
        try:
            # 简化的条件解析
            # 支持格式: metric_name > threshold
            if '>' in condition:
                metric_name, threshold = condition.split('>', 1)
                operator = '>'
            elif '<' in condition:
                metric_name, threshold = condition.split('<', 1)
                operator = '<'
            elif '>=' in condition:
                metric_name, threshold = condition.split('>=', 1)
                operator = '>='
            elif '<=' in condition:
                metric_name, threshold = condition.split('<=', 1)
                operator = '<='
            else:
                return None
            
            metric_name = metric_name.strip()
            threshold = float(threshold.strip())
            
            # 获取最新指标值
            metrics = self.data_collector.get_metrics(metric_name)
            if not metrics:
                return None
            
            latest_metric = metrics[-1]
            return latest_metric.value
            
        except Exception as e:
            self.logger.error(f"条件评估失败: {e}")
            return None
    
    def _check_threshold(self, value: float, threshold: float, condition: str) -> bool:
        """检查阈值"""
        try:
            if '>' in condition:
                return value > threshold
            elif '<' in condition:
                return value < threshold
            elif '>=' in condition:
                return value >= threshold
            elif '<=' in condition:
                return value <= threshold
            else:
                return False
        except Exception:
            return False
    
    def _fire_alert(self, rule: AlertRule, value: float, timestamp: datetime):
        """触发告警"""
        alert = Alert(
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.FIRING,
            message=self._generate_alert_message(rule, value),
            timestamp=timestamp,
            labels=rule.labels,
            annotations=rule.annotations,
            value=value
        )
        
        self.alerts[rule.name] = alert
        self.logger.warning(f"告警触发: {rule.name} - {alert.message}")
        
        # 发送通知
        self._send_notifications(alert)
    
    def _resolve_alert(self, rule: AlertRule, timestamp: datetime):
        """解决告警"""
        if rule.name in self.alerts:
            alert = self.alerts[rule.name]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = timestamp
            
            self.logger.info(f"告警解决: {rule.name}")
            
            # 发送解决通知
            self._send_notifications(alert)
    
    def _generate_alert_message(self, rule: AlertRule, value: float) -> str:
        """生成告警消息"""
        condition_parts = rule.condition.split()
        if len(condition_parts) >= 3:
            metric_name = condition_parts[0]
            operator = condition_parts[1]
            threshold = condition_parts[2]
            
            return f"{metric_name} {operator} {threshold} (当前值: {value})"
        else:
            return f"告警规则 {rule.name} 触发"
    
    def _send_notifications(self, alert: Alert):
        """发送通知"""
        for channel, handler in self.notification_handlers.items():
            try:
                success = handler(alert)
                if success:
                    self.logger.info(f"通知发送成功: {channel}")
                else:
                    self.logger.error(f"通知发送失败: {channel}")
            except Exception as e:
                self.logger.error(f"通知处理器 {channel} 错误: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [alert for alert in self.alerts.values() 
                if alert.status == AlertStatus.FIRING]
    
    def get_alert_history(self, rule_name: str = None) -> List[Alert]:
        """获取告警历史"""
        if rule_name:
            return [self.alerts[rule_name]] if rule_name in self.alerts else []
        else:
            return list(self.alerts.values())

# 通知处理器示例
class EmailNotificationHandler:
    def __init__(self, smtp_config: Dict[str, str]):
        self.smtp_config = smtp_config
    
    def __call__(self, alert: Alert) -> bool:
        """邮件通知处理器"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            subject = f"[{alert.severity.value.upper()}] {alert.rule_name}"
            
            if alert.status == AlertStatus.FIRING:
                body = f"""
告警触发: {alert.rule_name}
严重性: {alert.severity.value}
时间: {alert.timestamp}
消息: {alert.message}
当前值: {alert.value}

标签: {alert.labels}
注释: {alert.annotations}
                """
            else:
                body = f"""
告警解决: {alert.rule_name}
严重性: {alert.severity.value}
触发时间: {alert.timestamp}
解决时间: {alert.resolved_at}
消息: {alert.message}
                """
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['from']
            msg['To'] = self.smtp_config['to']
            
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False

class SlackNotificationHandler:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def __call__(self, alert: Alert) -> bool:
        """Slack通知处理器"""
        try:
            color = {
                AlertSeverity.INFO: "good",
                AlertSeverity.WARNING: "warning",
                AlertSeverity.CRITICAL: "danger",
                AlertSeverity.EMERGENCY: "danger"
            }.get(alert.severity, "warning")
            
            if alert.status == AlertStatus.FIRING:
                title = f"🚨 告警触发: {alert.rule_name}"
            else:
                title = f"✅ 告警解决: {alert.rule_name}"
            
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "严重性",
                                "value": alert.severity.value,
                                "short": True
                            },
                            {
                                "title": "时间",
                                "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True
                            }
                        ],
                        "footer": "性能监控系统",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack通知发送失败: {e}")
            return False

class WebhookNotificationHandler:
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {}
    
    def __call__(self, alert: Alert) -> bool:
        """Webhook通知处理器"""
        try:
            payload = {
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "value": alert.value,
                "labels": alert.labels,
                "annotations": alert.annotations
            }
            
            if alert.resolved_at:
                payload["resolved_at"] = alert.resolved_at.isoformat()
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Webhook通知发送失败: {e}")
            return False

# 使用示例
# 创建数据收集器
data_collector = DataCollector()
data_collector.start_collection(interval=30)

# 创建告警引擎
alert_engine = AlertEngine(data_collector)

# 添加告警规则
cpu_rule = AlertRule(
    name="high_cpu_usage",
    condition="system_cpu_usage > 80",
    severity=AlertSeverity.WARNING,
    threshold=80.0,
    duration=300  # 5分钟
)

memory_rule = AlertRule(
    name="high_memory_usage",
    condition="system_memory_usage > 90",
    severity=AlertSeverity.CRITICAL,
    threshold=90.0,
    duration=180  # 3分钟
)

alert_engine.add_rule(cpu_rule)
alert_engine.add_rule(memory_rule)

# 添加通知处理器
# email_config = {
#     'host': 'smtp.gmail.com',
#     'port': 587,
#     'username': 'your_email@gmail.com',
#     'password': 'your_password',
#     'from': 'your_email@gmail.com',
#     'to': 'admin@example.com'
# }
# email_handler = EmailNotificationHandler(email_config)
# alert_engine.add_notification_handler('email', email_handler)

slack_handler = SlackNotificationHandler('https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK')
alert_engine.add_notification_handler('slack', slack_handler)

webhook_handler = WebhookNotificationHandler('https://your-webhook-url.com/alerts')
alert_engine.add_notification_handler('webhook', webhook_handler)

# 启动告警评估
alert_engine.start_evaluation(interval=30)

# 模拟一些指标数据
import random
for i in range(10):
    cpu_usage = random.uniform(70, 95)
    memory_usage = random.uniform(80, 98)
    
    data_collector.set_gauge("system_cpu_usage", cpu_usage)
    data_collector.set_gauge("system_memory_usage", memory_usage)
    
    time.sleep(5)

# 获取活跃告警
active_alerts = alert_engine.get_active_alerts()
print(f"活跃告警数量: {len(active_alerts)}")

for alert in active_alerts:
    print(f"告警: {alert.rule_name} - {alert.message}")

# 停止系统
time.sleep(60)
alert_engine.stop_evaluation()
data_collector.stop_collection()
```

## 参考资源

### 监控工具
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [InfluxDB](https://www.influxdata.com/)
- [Zabbix](https://www.zabbix.com/)
- [Nagios](https://www.nagios.org/)

### 性能分析
- [New Relic](https://newrelic.com/)
- [Datadog](https://www.datadoghq.com/)
- [AppDynamics](https://www.appdynamics.com/)
- [Dynatrace](https://www.dynatrace.com/)

### 系统监控
- [psutil](https://psutil.readthedocs.io/)
- [collectd](https://collectd.org/)
- [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/)
- [StatsD](https://github.com/statsd/statsd)

### 告警通知
- [PagerDuty](https://www.pagerduty.com/)
- [OpsGenie](https://www.atlassian.com/software/opsgenie)
- [VictorOps](https://victorops.com/)
- [Slack](https://slack.com/)
