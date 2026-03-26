# 监控告警参考文档

## 监控告警概述

### 什么是监控告警系统
监控告警系统是一个综合性的运维监控解决方案，用于实时监控系统状态、收集性能指标、检测异常情况、发送告警通知和执行自动化响应。该系统支持多种监控目标、灵活的告警规则、多渠道通知和智能化的运维自动化，帮助运维团队快速发现和解决问题，保障系统稳定运行。

### 主要功能
- **多维度监控**: 应用性能、基础设施、业务指标、用户体验监控
- **实时指标收集**: 支持Agent、API、日志等多种数据采集方式
- **智能告警检测**: 阈值告警、趋势告警、异常检测和复合告警
- **多渠道通知**: 邮件、短信、即时消息、电话等多种通知方式
- **可视化仪表板**: 实时监控图表、系统概览和业务指标展示
- **自动化响应**: 自动扩容、自动重启、故障转移和自动修复
- **集成能力**: 与主流监控工具和云平台深度集成
- **数据分析**: 历史数据分析、趋势预测和容量规划

## 核心监控引擎

### 指标收集器
```python
# metrics_collector.py
import time
import psutil
import requests
import json
import threading
import queue
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class DataSource(Enum):
    AGENT = "agent"
    API = "api"
    LOG = "log"
    CUSTOM = "custom"

@dataclass
class Metric:
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str]
    source: str

@dataclass
class CollectionConfig:
    source_type: DataSource
    collection_interval: int  # 秒
    timeout: int = 30
    retry_count: int = 3
    batch_size: int = 100

class MetricsCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_queue = queue.Queue()
        self.collectors = {}
        self.is_running = False
        self.collection_threads = []
        self.callbacks = []
    
    def add_collector(self, name: str, collector_func: Callable[[], List[Metric]], config: CollectionConfig):
        """添加指标收集器"""
        self.collectors[name] = {
            'function': collector_func,
            'config': config,
            'last_collection': 0
        }
        self.logger.info(f"添加指标收集器: {name}")
    
    def add_callback(self, callback: Callable[[Metric], None]):
        """添加指标回调"""
        self.callbacks.append(callback)
    
    def start_collection(self):
        """开始指标收集"""
        self.is_running = True
        
        for name, collector_info in self.collectors.items():
            thread = threading.Thread(
                target=self._collection_loop,
                args=(name, collector_info)
            )
            thread.daemon = True
            thread.start()
            self.collection_threads.append(thread)
        
        self.logger.info("指标收集已启动")
    
    def stop_collection(self):
        """停止指标收集"""
        self.is_running = False
        
        for thread in self.collection_threads:
            thread.join()
        
        self.logger.info("指标收集已停止")
    
    def _collection_loop(self, name: str, collector_info: Dict[str, Any]):
        """收集循环"""
        collector_func = collector_info['function']
        config = collector_info['config']
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # 检查是否到了收集时间
                if current_time - collector_info['last_collection'] >= config.collection_interval:
                    # 收集指标
                    metrics = collector_func()
                    
                    # 处理指标
                    for metric in metrics:
                        self._process_metric(metric)
                    
                    collector_info['last_collection'] = current_time
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"收集器 {name} 运行失败: {e}")
                time.sleep(config.collection_interval)
    
    def _process_metric(self, metric: Metric):
        """处理指标"""
        try:
            # 放入队列
            self.metrics_queue.put(metric)
            
            # 调用回调
            for callback in self.callbacks:
                callback(metric)
                
        except Exception as e:
            self.logger.error(f"处理指标失败: {e}")
    
    def get_metrics(self, timeout: float = 1.0) -> List[Metric]:
        """获取指标"""
        metrics = []
        try:
            while True:
                metric = self.metrics_queue.get(timeout=timeout)
                metrics.append(metric)
        except queue.Empty:
            pass
        return metrics

# 系统指标收集器
def collect_system_metrics() -> List[Metric]:
    """收集系统指标"""
    metrics = []
    timestamp = datetime.now()
    
    # CPU指标
    cpu_percent = psutil.cpu_percent(interval=1)
    metrics.append(Metric(
        name="system_cpu_usage",
        value=cpu_percent,
        metric_type=MetricType.GAUGE,
        timestamp=timestamp,
        labels={"host": "localhost"},
        source="system"
    ))
    
    # 内存指标
    memory = psutil.virtual_memory()
    metrics.append(Metric(
        name="system_memory_usage",
        value=memory.percent,
        metric_type=MetricType.GAUGE,
        timestamp=timestamp,
        labels={"host": "localhost"},
        source="system"
    ))
    
    metrics.append(Metric(
        name="system_memory_available",
        value=memory.available,
        metric_type=MetricType.GAUGE,
        timestamp=timestamp,
        labels={"host": "localhost"},
        source="system"
    ))
    
    # 磁盘指标
    disk = psutil.disk_usage('/')
    disk_usage = (disk.used / disk.total) * 100
    metrics.append(Metric(
        name="system_disk_usage",
        value=disk_usage,
        metric_type=MetricType.GAUGE,
        timestamp=timestamp,
        labels={"host": "localhost", "mount": "/"},
        source="system"
    ))
    
    # 网络指标
    network = psutil.net_io_counters()
    metrics.append(Metric(
        name="system_network_bytes_sent",
        value=network.bytes_sent,
        metric_type=MetricType.COUNTER,
        timestamp=timestamp,
        labels={"host": "localhost"},
        source="system"
    ))
    
    metrics.append(Metric(
        name="system_network_bytes_recv",
        value=network.bytes_recv,
        metric_type=MetricType.COUNTER,
        timestamp=timestamp,
        labels={"host": "localhost"},
        source="system"
    ))
    
    return metrics

# 应用指标收集器
def collect_application_metrics() -> List[Metric]:
    """收集应用指标"""
    metrics = []
    timestamp = datetime.now()
    
    # 模拟应用指标
    import random
    
    # 响应时间
    response_time = random.uniform(50, 500)
    metrics.append(Metric(
        name="app_response_time",
        value=response_time,
        metric_type=MetricType.GAUGE,
        timestamp=timestamp,
        labels={"service": "web-api", "endpoint": "/api/users"},
        source="application"
    ))
    
    # 请求计数
    request_count = random.randint(100, 1000)
    metrics.append(Metric(
        name="app_requests_total",
        value=request_count,
        metric_type=MetricType.COUNTER,
        timestamp=timestamp,
        labels={"service": "web-api", "method": "GET"},
        source="application"
    ))
    
    # 错误率
    error_rate = random.uniform(0, 5)
    metrics.append(Metric(
        name="app_error_rate",
        value=error_rate,
        metric_type=MetricType.GAUGE,
        timestamp=timestamp,
        labels={"service": "web-api"},
        source="application"
    ))
    
    return metrics

# 使用示例
collector = MetricsCollector()

# 添加系统指标收集器
system_config = CollectionConfig(
    source_type=DataSource.AGENT,
    collection_interval=30
)
collector.add_collector("system", collect_system_metrics, system_config)

# 添加应用指标收集器
app_config = CollectionConfig(
    source_type=DataSource.CUSTOM,
    collection_interval=60
)
collector.add_collector("application", collect_application_metrics, app_config)

# 启动收集
collector.start_collection()

# 获取指标
while True:
    metrics = collector.get_metrics(timeout=1.0)
    for metric in metrics:
        print(f"{metric.timestamp} {metric.name}: {metric.value}")
    time.sleep(1)
```

### 告警检测引擎
```python
# alert_engine.py
import time
import threading
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

class AlertStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ComparisonOperator(Enum):
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "ge"
    LESS_EQUAL = "le"
    EQUAL = "eq"
    NOT_EQUAL = "ne"

@dataclass
class AlertRule:
    name: str
    metric_name: str
    operator: ComparisonOperator
    threshold: float
    duration: int  # 秒
    severity: AlertStatus
    labels: Dict[str, str]
    enabled: bool = True

@dataclass
class Alert:
    id: str
    rule_name: str
    severity: AlertStatus
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime]
    labels: Dict[str, str]
    annotations: Dict[str, str]

@dataclass
class MetricValue:
    value: float
    timestamp: datetime
    labels: Dict[str, str]

class AlertEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = {}
        self.active_alerts = {}
        self.metric_history = {}
        self.alert_callbacks = []
        self.is_running = False
        self.evaluation_thread = None
        self.max_history_size = 1000
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.name] = rule
        self.logger.info(f"添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"移除告警规则: {rule_name}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def process_metric(self, metric: Metric):
        """处理指标"""
        # 存储指标历史
        metric_key = self._get_metric_key(metric)
        if metric_key not in self.metric_history:
            self.metric_history[metric_key] = []
        
        metric_value = MetricValue(
            value=metric.value,
            timestamp=metric.timestamp,
            labels=metric.labels
        )
        
        self.metric_history[metric_key].append(metric_value)
        
        # 限制历史数据大小
        if len(self.metric_history[metric_key]) > self.max_history_size:
            self.metric_history[metric_key] = self.metric_history[metric_key][-self.max_history_size:]
    
    def start_evaluation(self, interval: int = 60):
        """开始告警评估"""
        self.is_running = True
        self.evaluation_thread = threading.Thread(
            target=self._evaluation_loop,
            args=(interval,)
        )
        self.evaluation_thread.daemon = True
        self.evaluation_thread.start()
        self.logger.info("告警评估已启动")
    
    def stop_evaluation(self):
        """停止告警评估"""
        self.is_running = False
        if self.evaluation_thread:
            self.evaluation_thread.join()
        self.logger.info("告警评估已停止")
    
    def _evaluation_loop(self, interval: int):
        """评估循环"""
        while self.is_running:
            try:
                self._evaluate_rules()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"告警评估失败: {e}")
                time.sleep(interval)
    
    def _evaluate_rules(self):
        """评估所有规则"""
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                self._evaluate_rule(rule)
            except Exception as e:
                self.logger.error(f"评估规则 {rule_name} 失败: {e}")
    
    def _evaluate_rule(self, rule: AlertRule):
        """评估单个规则"""
        # 获取相关指标
        metric_values = self._get_metric_values(rule)
        
        if not metric_values:
            return
        
        # 检查是否触发告警
        is_alerting = self._check_alert_condition(rule, metric_values)
        
        alert_id = f"{rule.name}_{self._get_labels_hash(rule.labels)}"
        
        if is_alerting:
            # 检查是否已有活跃告警
            if alert_id not in self.active_alerts:
                # 创建新告警
                alert = Alert(
                    id=alert_id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=self._generate_alert_message(rule, metric_values),
                    triggered_at=datetime.now(),
                    resolved_at=None,
                    labels=rule.labels,
                    annotations=self._generate_alert_annotations(rule, metric_values)
                )
                
                self.active_alerts[alert_id] = alert
                self._trigger_alert(alert)
                
                self.logger.warning(f"触发告警: {rule.name}")
        else:
            # 检查是否需要解决告警
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved_at = datetime.now()
                self._resolve_alert(alert)
                del self.active_alerts[alert_id]
                
                self.logger.info(f"解决告警: {rule_name}")
    
    def _get_metric_key(self, metric: Metric) -> str:
        """获取指标键"""
        return f"{metric.name}_{hash(frozenset(metric.labels.items()))}"
    
    def _get_metric_values(self, rule: AlertRule) -> List[MetricValue]:
        """获取规则相关的指标值"""
        metric_key = f"{rule.metric_name}_{hash(frozenset(rule.labels.items()))}"
        return self.metric_history.get(metric_key, [])
    
    def _check_alert_condition(self, rule: AlertRule, metric_values: List[MetricValue]) -> bool:
        """检查告警条件"""
        if not metric_values:
            return False
        
        # 获取最近的指标值
        current_time = datetime.now()
        recent_values = [
            mv for mv in metric_values
            if current_time - mv.timestamp <= timedelta(seconds=rule.duration)
        ]
        
        if not recent_values:
            return False
        
        # 检查阈值条件
        latest_value = recent_values[-1].value
        
        if rule.operator == ComparisonOperator.GREATER_THAN:
            return latest_value > rule.threshold
        elif rule.operator == ComparisonOperator.LESS_THAN:
            return latest_value < rule.threshold
        elif rule.operator == ComparisonOperator.GREATER_EQUAL:
            return latest_value >= rule.threshold
        elif rule.operator == ComparisonOperator.LESS_EQUAL:
            return latest_value <= rule.threshold
        elif rule.operator == ComparisonOperator.EQUAL:
            return latest_value == rule.threshold
        elif rule.operator == ComparisonOperator.NOT_EQUAL:
            return latest_value != rule.threshold
        
        return False
    
    def _generate_alert_message(self, rule: AlertRule, metric_values: List[MetricValue]) -> str:
        """生成告警消息"""
        if not metric_values:
            return f"告警: {rule.name}"
        
        latest_value = metric_values[-1]
        return f"{rule.name}: {latest_value.value} {rule.operator.value} {rule.threshold}"
    
    def _generate_alert_annotations(self, rule: AlertRule, metric_values: List[MetricValue]) -> Dict[str, str]:
        """生成告警注释"""
        annotations = {
            "threshold": str(rule.threshold),
            "operator": rule.operator.value,
            "duration": str(rule.duration)
        }
        
        if metric_values:
            latest_value = metric_values[-1]
            annotations["current_value"] = str(latest_value.value)
            annotations["metric_timestamp"] = latest_value.timestamp.isoformat()
            
            # 计算统计信息
            values = [mv.value for mv in metric_values[-10:]]  # 最近10个值
            if len(values) > 1:
                annotations["avg_value"] = str(statistics.mean(values))
                annotations["min_value"] = str(min(values))
                annotations["max_value"] = str(max(values))
        
        return annotations
    
    def _get_labels_hash(self, labels: Dict[str, str]) -> str:
        """获取标签哈希"""
        return str(hash(frozenset(labels.items())))
    
    def _trigger_alert(self, alert: Alert):
        """触发告警"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"告警回调执行失败: {e}")
    
    def _resolve_alert(self, alert: Alert):
        """解决告警"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"告警解决回调执行失败: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())

# 告警回调示例
def console_alert_callback(alert: Alert):
    """控制台告警回调"""
    if alert.resolved_at:
        print(f"[RESOLVED] {alert.severity.value.upper()} {alert.message}")
    else:
        print(f"[ALERT] {alert.severity.value.upper()} {alert.message}")

# 使用示例
alert_engine = AlertEngine()

# 添加告警规则
cpu_rule = AlertRule(
    name="high_cpu_usage",
    metric_name="system_cpu_usage",
    operator=ComparisonOperator.GREATER_THAN,
    threshold=80.0,
    duration=300,  # 5分钟
    severity=AlertStatus.WARNING,
    labels={"host": "localhost"}
)

memory_rule = AlertRule(
    name="high_memory_usage",
    metric_name="system_memory_usage",
    operator=ComparisonOperator.GREATER_THAN,
    threshold=90.0,
    duration=180,  # 3分钟
    severity=AlertStatus.CRITICAL,
    labels={"host": "localhost"}
)

alert_engine.add_rule(cpu_rule)
alert_engine.add_rule(memory_rule)

# 添加告警回调
alert_engine.add_alert_callback(console_alert_callback)

# 启动评估
alert_engine.start_evaluation(interval=60)
```

### 通知管理器
```python
# notification_manager.py
import smtplib
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DINGTALK = "dingtalk"
    WECHAT = "wechat"

class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class NotificationConfig:
    channel: NotificationChannel
    enabled: bool = True
    retry_count: int = 3
    timeout: int = 30

@dataclass
class EmailConfig(NotificationConfig):
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    recipients: List[str] = None

@dataclass
class SMSConfig(NotificationConfig):
    provider: str
    api_key: str
    api_secret: str
    phone_numbers: List[str] = None
    sign_name: str = ""
    template_code: str = ""

@dataclass
class SlackConfig(NotificationConfig):
    webhook_url: str
    channel: str = "#alerts"
    username: str = "AlertBot"

@dataclass
class WebhookConfig(NotificationConfig):
    url: str
    method: str = "POST"
    headers: Dict[str, str] = None
    auth_token: str = ""

@dataclass
class DingTalkConfig(NotificationConfig):
    webhook_url: str
    secret: str = ""

@dataclass
class Notification:
    id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    content: str
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime]
    error_message: Optional[str]

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.configs = {}
        self.notification_history = []
        self.max_history_size = 1000
    
    def add_email_config(self, name: str, config: EmailConfig):
        """添加邮件配置"""
        self.configs[name] = config
        self.logger.info(f"添加邮件配置: {name}")
    
    def add_sms_config(self, name: str, config: SMSConfig):
        """添加短信配置"""
        self.configs[name] = config
        self.logger.info(f"添加短信配置: {name}")
    
    def add_slack_config(self, name: str, config: SlackConfig):
        """添加Slack配置"""
        self.configs[name] = config
        self.logger.info(f"添加Slack配置: {name}")
    
    def add_webhook_config(self, name: str, config: WebhookConfig):
        """添加Webhook配置"""
        self.configs[name] = config
        self.logger.info(f"添加Webhook配置: {name}")
    
    def add_dingtalk_config(self, name: str, config: DingTalkConfig):
        """添加钉钉配置"""
        self.configs[name] = config
        self.logger.info(f"添加钉钉配置: {name}")
    
    def send_notification(self, config_name: str, subject: str, content: str, 
                         alert: Optional[Alert] = None) -> Notification:
        """发送通知"""
        config = self.configs.get(config_name)
        if not config:
            raise ValueError(f"配置不存在: {config_name}")
        
        if not config.enabled:
            self.logger.warning(f"通知渠道已禁用: {config_name}")
            return None
        
        notification = Notification(
            id=f"{config_name}_{int(time.time())}",
            channel=config.channel,
            recipient="",  # 根据配置设置
            subject=subject,
            content=content,
            status=NotificationStatus.PENDING,
            created_at=datetime.now(),
            sent_at=None,
            error_message=None
        )
        
        try:
            if config.channel == NotificationChannel.EMAIL:
                self._send_email_notification(config, notification, alert)
            elif config.channel == NotificationChannel.SMS:
                self._send_sms_notification(config, notification, alert)
            elif config.channel == NotificationChannel.SLACK:
                self._send_slack_notification(config, notification, alert)
            elif config.channel == NotificationChannel.WEBHOOK:
                self._send_webhook_notification(config, notification, alert)
            elif config.channel == NotificationChannel.DINGTALK:
                self._send_dingtalk_notification(config, notification, alert)
            
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now()
            
        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            self.logger.error(f"发送通知失败: {e}")
        
        # 记录通知历史
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history_size:
            self.notification_history = self.notification_history[-self.max_history_size:]
        
        return notification
    
    def _send_email_notification(self, config: EmailConfig, notification: Notification, alert: Optional[Alert]):
        """发送邮件通知"""
        msg = MIMEMultipart()
        msg['From'] = config.username
        msg['To'] = ", ".join(config.recipients)
        msg['Subject'] = notification.subject
        
        # 构建邮件内容
        body = notification.content
        if alert:
            body += f"\n\n告警详情:\n"
            body += f"级别: {alert.severity.value}\n"
            body += f"规则: {alert.rule_name}\n"
            body += f"触发时间: {alert.triggered_at}\n"
            body += f"标签: {alert.labels}\n"
            if alert.annotations:
                body += f"注释: {alert.annotations}\n"
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(config.smtp_server, config.smtp_port)
        if config.use_tls:
            server.starttls()
        server.login(config.username, config.password)
        server.send_message(msg)
        server.quit()
        
        notification.recipient = ", ".join(config.recipients)
    
    def _send_sms_notification(self, config: SMSConfig, notification: Notification, alert: Optional[Alert]):
        """发送短信通知"""
        # 这里需要根据具体的短信服务商API实现
        # 以下是阿里云短信的示例实现
        import hashlib
        import hmac
        import base64
        from urllib.parse import quote
        
        # 构建请求参数
        params = {
            'AccessKeyId': config.api_key,
            'Action': 'SendSms',
            'Format': 'JSON',
            'PhoneNumbers': ",".join(config.phone_numbers),
            'SignName': config.sign_name,
            'TemplateCode': config.template_code,
            'TemplateParam': json.dumps({
                'alert_level': alert.severity.value if alert else '',
                'message': notification.content[:100]  # 限制长度
            }),
            'Version': '2017-05-25',
            'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'SignatureNonce': str(int(time.time() * 1000))
        }
        
        # 计算签名
        sorted_params = sorted(params.items())
        canonicalized_resource = "/&".join([quote(k) + "=" + quote(v) for k, v in sorted_params])
        string_to_sign = "POST&%2F&" + quote(canonicalized_resource)
        
        signature = base64.b64encode(
            hmac.new(
                (config.api_secret + "&").encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode()
        
        params['Signature'] = signature
        
        # 发送请求
        response = requests.post(
            'https://dysmsapi.aliyuncs.com/',
            data=params,
            timeout=config.timeout
        )
        
        response.raise_for_status()
        
        notification.recipient = ", ".join(config.phone_numbers)
    
    def _send_slack_notification(self, config: SlackConfig, notification: Notification, alert: Optional[Alert]):
        """发送Slack通知"""
        payload = {
            "channel": config.channel,
            "username": config.username,
            "text": notification.subject,
            "attachments": [
                {
                    "color": self._get_color_for_alert(alert),
                    "text": notification.content,
                    "fields": []
                }
            ]
        }
        
        if alert:
            payload["attachments"][0]["fields"] = [
                {"title": "级别", "value": alert.severity.value, "short": True},
                {"title": "规则", "value": alert.rule_name, "short": True},
                {"title": "触发时间", "value": alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S'), "short": True}
            ]
        
        response = requests.post(
            config.webhook_url,
            json=payload,
            timeout=config.timeout
        )
        
        response.raise_for_status()
        
        notification.recipient = config.channel
    
    def _send_webhook_notification(self, config: WebhookConfig, notification: Notification, alert: Optional[Alert]):
        """发送Webhook通知"""
        payload = {
            "notification_id": notification.id,
            "subject": notification.subject,
            "content": notification.content,
            "timestamp": notification.created_at.isoformat()
        }
        
        if alert:
            payload["alert"] = {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat(),
                "labels": alert.labels,
                "annotations": alert.annotations
            }
        
        headers = config.headers or {}
        if config.auth_token:
            headers["Authorization"] = f"Bearer {config.auth_token}"
        
        response = requests.request(
            config.method,
            config.url,
            json=payload,
            headers=headers,
            timeout=config.timeout
        )
        
        response.raise_for_status()
        
        notification.recipient = config.url
    
    def _send_dingtalk_notification(self, config: DingTalkConfig, notification: Notification, alert: Optional[Alert]):
        """发送钉钉通知"""
        import hmac
        import hashlib
        import base64
        import urllib.parse
        
        # 计算签名
        timestamp = str(round(time.time() * 1000))
        secret_enc = config.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{config.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        url = f"{config.webhook_url}&timestamp={timestamp}&sign={sign}"
        
        # 构建消息
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": notification.subject,
                "text": f"## {notification.subject}\n\n{notification.content}"
            }
        }
        
        if alert:
            alert_info = f"\n\n**告警详情:**\n"
            alert_info += f"- 级别: {alert.severity.value}\n"
            alert_info += f"- 规则: {alert.rule_name}\n"
            alert_info += f"- 触发时间: {alert.triggered_at}\n"
            payload["markdown"]["text"] += alert_info
        
        response = requests.post(url, json=payload, timeout=config.timeout)
        response.raise_for_status()
        
        notification.recipient = config.webhook_url
    
    def _get_color_for_alert(self, alert: Optional[Alert]) -> str:
        """获取告警对应的颜色"""
        if not alert:
            return "good"
        
        color_map = {
            AlertStatus.OK: "good",
            AlertStatus.WARNING: "warning",
            AlertStatus.CRITICAL: "danger",
            AlertStatus.UNKNOWN: "#808080"
        }
        return color_map.get(alert.severity, "good")
    
    def get_notification_history(self, limit: int = 100) -> List[Notification]:
        """获取通知历史"""
        return self.notification_history[-limit:]

# 使用示例
notification_manager = NotificationManager()

# 添加邮件配置
email_config = EmailConfig(
    channel=NotificationChannel.EMAIL,
    smtp_server="smtp.example.com",
    smtp_port=587,
    username="alerts@example.com",
    password="password",
    use_tls=True,
    recipients=["admin@example.com", "ops@example.com"]
)
notification_manager.add_email_config("default_email", email_config)

# 添加Slack配置
slack_config = SlackConfig(
    channel=NotificationChannel.SLACK,
    webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    channel="#alerts",
    username="AlertBot"
)
notification_manager.add_slack_config("default_slack", slack_config)

# 发送通知
notification = notification_manager.send_notification(
    "default_email",
    "系统告警",
    "CPU使用率过高，当前值: 85.5%",
    alert
)
```

### 仪表板生成器
```python
# dashboard_generator.py
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging

class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    GAUGE = "gauge"
    STAT = "stat"
    TABLE = "table"
    HEATMAP = "heatmap"

class PanelType(Enum):
    GRAPH = "graph"
    SINGLE_STAT = "singlestat"
    TABLE = "table"
    HEATMAP = "heatmap"

@dataclass
class Panel:
    id: str
    title: str
    type: PanelType
    chart_type: ChartType
    metrics: List[str]
    position: Dict[str, int]  # {x, y, w, h}
    targets: List[Dict[str, Any]]
    options: Dict[str, Any]

@dataclass
class Dashboard:
    id: str
    title: str
    description: str
    panels: List[Panel]
    time_range: Dict[str, str]
    refresh_interval: str
    tags: List[str]

class DashboardGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dashboards = {}
        self.templates = {}
    
    def create_system_dashboard(self, dashboard_id: str, title: str) -> Dashboard:
        """创建系统监控仪表板"""
        panels = []
        
        # 系统概览面板
        panels.append(Panel(
            id="system_overview",
            title="系统概览",
            type=PanelType.SINGLE_STAT,
            chart_type=ChartType.STAT,
            metrics=["system_cpu_usage", "system_memory_usage", "system_disk_usage"],
            position={"x": 0, "y": 0, "w": 12, "h": 8},
            targets=[
                {
                    "metric": "system_cpu_usage",
                    "legend": "CPU使用率"
                },
                {
                    "metric": "system_memory_usage", 
                    "legend": "内存使用率"
                },
                {
                    "metric": "system_disk_usage",
                    "legend": "磁盘使用率"
                }
            ],
            options={
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "orientation": "horizontal",
                "textMode": "auto"
            }
        ))
        
        # CPU使用率图表
        panels.append(Panel(
            id="cpu_usage",
            title="CPU使用率",
            type=PanelType.GRAPH,
            chart_type=ChartType.LINE,
            metrics=["system_cpu_usage"],
            position={"x": 0, "y": 8, "w": 12, "h": 8},
            targets=[
                {
                    "metric": "system_cpu_usage",
                    "legend": "CPU使用率 (%)"
                }
            ],
            options={
                "lines": True,
                "fill": 1,
                "linewidth": 2,
                "yaxes": [
                    {
                        "max": 100,
                        "min": 0,
                        "unit": "percent"
                    }
                ]
            }
        ))
        
        # 内存使用率图表
        panels.append(Panel(
            id="memory_usage",
            title="内存使用率",
            type=PanelType.GRAPH,
            chart_type=ChartType.LINE,
            metrics=["system_memory_usage"],
            position={"x": 12, "y": 8, "w": 12, "h": 8},
            targets=[
                {
                    "metric": "system_memory_usage",
                    "legend": "内存使用率 (%)"
                }
            ],
            options={
                "lines": True,
                "fill": 1,
                "linewidth": 2,
                "yaxes": [
                    {
                        "max": 100,
                        "min": 0,
                        "unit": "percent"
                    }
                ]
            }
        ))
        
        # 网络流量图表
        panels.append(Panel(
            id="network_traffic",
            title="网络流量",
            type=PanelType.GRAPH,
            chart_type=ChartType.LINE,
            metrics=["system_network_bytes_sent", "system_network_bytes_recv"],
            position={"x": 0, "y": 16, "w": 24, "h": 8},
            targets=[
                {
                    "metric": "system_network_bytes_sent",
                    "legend": "发送流量"
                },
                {
                    "metric": "system_network_bytes_recv",
                    "legend": "接收流量"
                }
            ],
            options={
                "lines": True,
                "fill": 0,
                "linewidth": 2,
                "yaxes": [
                    {
                        "unit": "bytes"
                    }
                ]
            }
        ))
        
        dashboard = Dashboard(
            id=dashboard_id,
            title=title,
            description="系统监控仪表板",
            panels=panels,
            time_range={"from": "now-1h", "to": "now"},
            refresh_interval="30s",
            tags=["system", "monitoring"]
        )
        
        self.dashboards[dashboard_id] = dashboard
        return dashboard
    
    def create_application_dashboard(self, dashboard_id: str, title: str) -> Dashboard:
        """创建应用监控仪表板"""
        panels = []
        
        # 应用概览
        panels.append(Panel(
            id="app_overview",
            title="应用概览",
            type=PanelType.SINGLE_STAT,
            chart_type=ChartType.STAT,
            metrics=["app_response_time", "app_requests_total", "app_error_rate"],
            position={"x": 0, "y": 0, "w": 24, "h": 8},
            targets=[
                {
                    "metric": "app_response_time",
                    "legend": "响应时间"
                },
                {
                    "metric": "app_requests_total",
                    "legend": "请求数"
                },
                {
                    "metric": "app_error_rate",
                    "legend": "错误率"
                }
            ],
            options={
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "orientation": "horizontal",
                "textMode": "auto"
            }
        ))
        
        # 响应时间图表
        panels.append(Panel(
            id="response_time",
            title="响应时间趋势",
            type=PanelType.GRAPH,
            chart_type=ChartType.LINE,
            metrics=["app_response_time"],
            position={"x": 0, "y": 8, "w": 12, "h": 8},
            targets=[
                {
                    "metric": "app_response_time",
                    "legend": "响应时间 (ms)"
                }
            ],
            options={
                "lines": True,
                "fill": 1,
                "linewidth": 2,
                "yaxes": [
                    {
                        "unit": "ms"
                    }
                ]
            }
        ))
        
        # 错误率图表
        panels.append(Panel(
            id="error_rate",
            title="错误率",
            type=PanelType.GRAPH,
            chart_type=ChartType.LINE,
            metrics=["app_error_rate"],
            position={"x": 12, "y": 8, "w": 12, "h": 8},
            targets=[
                {
                    "metric": "app_error_rate",
                    "legend": "错误率 (%)"
                }
            ],
            options={
                "lines": True,
                "fill": 1,
                "linewidth": 2,
                "yaxes": [
                    {
                        "max": 100,
                        "min": 0,
                        "unit": "percent"
                    }
                ]
            }
        ))
        
        # 请求量图表
        panels.append(Panel(
            id="request_volume",
            title="请求量",
            type=PanelType.GRAPH,
            chart_type=ChartType.BAR,
            metrics=["app_requests_total"],
            position={"x": 0, "y": 16, "w": 24, "h": 8},
            targets=[
                {
                    "metric": "app_requests_total",
                    "legend": "请求数/分钟"
                }
            ],
            options={
                "bars": True,
                "fill": 1,
                "linewidth": 2,
                "yaxes": [
                    {
                        "unit": "reqps"
                    }
                ]
            }
        ))
        
        dashboard = Dashboard(
            id=dashboard_id,
            title=title,
            description="应用监控仪表板",
            panels=panels,
            time_range={"from": "now-1h", "to": "now"},
            refresh_interval="15s",
            tags=["application", "monitoring"]
        )
        
        self.dashboards[dashboard_id] = dashboard
        return dashboard
    
    def create_alert_dashboard(self, dashboard_id: str, title: str) -> Dashboard:
        """创建告警仪表板"""
        panels = []
        
        # 活跃告警数量
        panels.append(Panel(
            id="active_alerts",
            title="活跃告警",
            type=PanelType.SINGLE_STAT,
            chart_type=ChartType.STAT,
            metrics=["alerts_active_total"],
            position={"x": 0, "y": 0, "w": 8, "h": 8},
            targets=[
                {
                    "metric": "alerts_active_total",
                    "legend": "活跃告警"
                }
            ],
            options={
                "reduceOptions": {
                    "values": False,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "textMode": "auto",
                "color": {
                    "mode": "thresholds"
                },
                "thresholds": {
                    "steps": [
                        {"color": "green", "value": 0},
                        {"color": "yellow", "value": 1},
                        {"color": "red", "value": 5}
                    ]
                }
            }
        ))
        
        # 告警级别分布
        panels.append(Panel(
            id="alert_severity",
            title="告警级别分布",
            type=PanelType.GRAPH,
            chart_type=ChartType.PIE,
            metrics=["alerts_by_severity"],
            position={"x": 8, "y": 0, "w": 8, "h": 8},
            targets=[
                {
                    "metric": "alerts_by_severity",
                    "legend": "按级别"
                }
            ],
            options={
                "pieType": "pie",
                "displayLabels": ["name", "percent"],
                "legend": {
                    "displayMode": "list",
                    "placement": "right"
                }
            }
        ))
        
        # 告警趋势
        panels.append(Panel(
            id="alert_trend",
            title="告警趋势",
            type=PanelType.GRAPH,
            chart_type=ChartType.LINE,
            metrics=["alerts_triggered_total"],
            position={"x": 16, "y": 0, "w": 8, "h": 8},
            targets=[
                {
                    "metric": "alerts_triggered_total",
                    "legend": "触发告警数"
                }
            ],
            options={
                "lines": True,
                "fill": 1,
                "linewidth": 2,
                "yaxes": [
                    {
                        "unit": "reqps"
                    }
                ]
            }
        ))
        
        # 告警列表
        panels.append(Panel(
            id="alert_list",
            title="告警列表",
            type=PanelType.TABLE,
            chart_type=ChartType.TABLE,
            metrics=["alerts_list"],
            position={"x": 0, "y": 8, "w": 24, "h": 16},
            targets=[
                {
                    "metric": "alerts_list",
                    "legend": "告警详情"
                }
            ],
            options={
                "showHeader": True,
                "columns": [
                    {"text": "告警名称", "value": "alert_name"},
                    {"text": "级别", "value": "severity"},
                    {"text": "状态", "value": "status"},
                    {"text": "触发时间", "value": "triggered_at"},
                    {"text": "消息", "value": "message"}
                ],
                "sortBy": [
                    {"desc": true, "displayName": "触发时间"}
                ]
            }
        ))
        
        dashboard = Dashboard(
            id=dashboard_id,
            title=title,
            description="告警监控仪表板",
            panels=panels,
            time_range={"from": "now-24h", "to": "now"},
            refresh_interval="1m",
            tags=["alert", "monitoring"]
        )
        
        self.dashboards[dashboard_id] = dashboard
        return dashboard
    
    def export_dashboard(self, dashboard_id: str, format: str = "json") -> str:
        """导出仪表板"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            raise ValueError(f"仪表板不存在: {dashboard_id}")
        
        if format == "json":
            return json.dumps(asdict(dashboard), indent=2, ensure_ascii=False)
        elif format == "grafana":
            return self._convert_to_grafana_json(dashboard)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _convert_to_grafana_json(self, dashboard: Dashboard) -> str:
        """转换为Grafana JSON格式"""
        grafana_dashboard = {
            "dashboard": {
                "id": None,
                "title": dashboard.title,
                "description": dashboard.description,
                "tags": dashboard.tags,
                "timezone": "browser",
                "panels": [],
                "time": {
                    "from": dashboard.time_range["from"],
                    "to": dashboard.time_range["to"]
                },
                "refresh": dashboard.refresh_interval
            }
        }
        
        for panel in dashboard.panels:
            grafana_panel = {
                "id": len(grafana_dashboard["dashboard"]["panels"]) + 1,
                "title": panel.title,
                "type": panel.type.value,
                "gridPos": {
                    "x": panel.position["x"],
                    "y": panel.position["y"],
                    "w": panel.position["w"],
                    "h": panel.position["h"]
                },
                "targets": panel.targets,
                "options": panel.options
            }
            
            grafana_dashboard["dashboard"]["panels"].append(grafana_panel)
        
        return json.dumps(grafana_dashboard, indent=2, ensure_ascii=False)
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """获取仪表板"""
        return self.dashboards.get(dashboard_id)
    
    def list_dashboards(self) -> List[Dashboard]:
        """列出所有仪表板"""
        return list(self.dashboards.values())

# 使用示例
generator = DashboardGenerator()

# 创建系统监控仪表板
system_dashboard = generator.create_system_dashboard(
    "system_monitoring",
    "系统监控"
)

# 创建应用监控仪表板
app_dashboard = generator.create_application_dashboard(
    "application_monitoring", 
    "应用监控"
)

# 创建告警仪表板
alert_dashboard = generator.create_alert_dashboard(
    "alert_monitoring",
    "告警监控"
)

# 导出仪表板
dashboard_json = generator.export_dashboard("system_monitoring")
print(dashboard_json)
```

## 使用示例

### 完整监控告警系统
```python
# complete_monitoring_system.py
from metrics_collector import MetricsCollector, collect_system_metrics, collect_application_metrics
from alert_engine import AlertEngine, AlertRule, AlertStatus, ComparisonOperator
from notification_manager import NotificationManager, EmailConfig, SlackConfig, NotificationChannel
from dashboard_generator import DashboardGenerator
import threading
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringSystem:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_engine = AlertEngine()
        self.notification_manager = NotificationManager()
        self.dashboard_generator = DashboardGenerator()
        self.is_running = False
        
    def setup_metrics_collection(self):
        """设置指标收集"""
        # 系统指标
        system_config = CollectionConfig(
            source_type=DataSource.AGENT,
            collection_interval=30
        )
        self.metrics_collector.add_collector("system", collect_system_metrics, system_config)
        
        # 应用指标
        app_config = CollectionConfig(
            source_type=DataSource.CUSTOM,
            collection_interval=60
        )
        self.metrics_collector.add_collector("application", collect_application_metrics, app_config)
        
        # 设置指标处理回调
        self.metrics_collector.add_callback(self._process_metric)
    
    def setup_alert_rules(self):
        """设置告警规则"""
        # CPU使用率告警
        cpu_rule = AlertRule(
            name="high_cpu_usage",
            metric_name="system_cpu_usage",
            operator=ComparisonOperator.GREATER_THAN,
            threshold=80.0,
            duration=300,
            severity=AlertStatus.WARNING,
            labels={"host": "localhost", "type": "system"}
        )
        self.alert_engine.add_rule(cpu_rule)
        
        # 内存使用率告警
        memory_rule = AlertRule(
            name="high_memory_usage",
            metric_name="system_memory_usage",
            operator=ComparisonOperator.GREATER_THAN,
            threshold=90.0,
            duration=180,
            severity=AlertStatus.CRITICAL,
            labels={"host": "localhost", "type": "system"}
        )
        self.alert_engine.add_rule(memory_rule)
        
        # 响应时间告警
        response_time_rule = AlertRule(
            name="high_response_time",
            metric_name="app_response_time",
            operator=ComparisonOperator.GREATER_THAN,
            threshold=500.0,
            duration=120,
            severity=AlertStatus.WARNING,
            labels={"service": "web-api", "type": "application"}
        )
        self.alert_engine.add_rule(response_time_rule)
        
        # 错误率告警
        error_rate_rule = AlertRule(
            name="high_error_rate",
            metric_name="app_error_rate",
            operator=ComparisonOperator.GREATER_THAN,
            threshold=5.0,
            duration=60,
            severity=AlertStatus.CRITICAL,
            labels={"service": "web-api", "type": "application"}
        )
        self.alert_engine.add_rule(error_rate_rule)
        
        # 设置告警回调
        self.alert_engine.add_alert_callback(self._handle_alert)
    
    def setup_notifications(self):
        """设置通知配置"""
        # 邮件配置
        email_config = EmailConfig(
            channel=NotificationChannel.EMAIL,
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="alerts@example.com",
            password="password",
            use_tls=True,
            recipients=["admin@example.com"]
        )
        self.notification_manager.add_email_config("email", email_config)
        
        # Slack配置
        slack_config = SlackConfig(
            channel=NotificationChannel.SLACK,
            webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            channel="#alerts",
            username="MonitorBot"
        )
        self.notification_manager.add_slack_config("slack", slack_config)
    
    def setup_dashboards(self):
        """设置仪表板"""
        # 系统监控仪表板
        self.dashboard_generator.create_system_dashboard(
            "system_dashboard",
            "系统监控"
        )
        
        # 应用监控仪表板
        self.dashboard_generator.create_application_dashboard(
            "application_dashboard",
            "应用监控"
        )
        
        # 告警仪表板
        self.dashboard_generator.create_alert_dashboard(
            "alert_dashboard",
            "告警监控"
        )
    
    def _process_metric(self, metric):
        """处理指标"""
        # 将指标传递给告警引擎
        self.alert_engine.process_metric(metric)
    
    def _handle_alert(self, alert):
        """处理告警"""
        # 发送通知
        subject = f"[{alert.severity.value.upper()}] {alert.rule_name}"
        content = f"告警消息: {alert.message}"
        
        # 发送邮件通知
        try:
            self.notification_manager.send_notification("email", subject, content, alert)
        except Exception as e:
            logger.error(f"发送邮件通知失败: {e}")
        
        # 发送Slack通知
        try:
            self.notification_manager.send_notification("slack", subject, content, alert)
        except Exception as e:
            logger.error(f"发送Slack通知失败: {e}")
        
        logger.warning(f"处理告警: {alert.rule_name} - {alert.message}")
    
    def start(self):
        """启动监控系统"""
        self.is_running = True
        
        # 启动指标收集
        self.metrics_collector.start_collection()
        
        # 启动告警评估
        self.alert_engine.start_evaluation(interval=60)
        
        logger.info("监控系统已启动")
    
    def stop(self):
        """停止监控系统"""
        self.is_running = False
        
        self.metrics_collector.stop_collection()
        self.alert_engine.stop_evaluation()
        
        logger.info("监控系统已停止")
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "is_running": self.is_running,
            "active_alerts": len(self.alert_engine.get_active_alerts()),
            "notification_history": len(self.notification_manager.get_notification_history()),
            "dashboards": len(self.dashboard_generator.list_dashboards())
        }

# 使用示例
if __name__ == "__main__":
    monitoring_system = MonitoringSystem()
    
    # 设置各个组件
    monitoring_system.setup_metrics_collection()
    monitoring_system.setup_alert_rules()
    monitoring_system.setup_notifications()
    monitoring_system.setup_dashboards()
    
    # 启动系统
    monitoring_system.start()
    
    try:
        while True:
            status = monitoring_system.get_status()
            print(f"系统状态: {status}")
            time.sleep(60)
    except KeyboardInterrupt:
        monitoring_system.stop()
```

这个监控告警系统提供了完整的指标收集、告警检测、通知发送和仪表板展示功能，支持多种监控目标和通知渠道，可以满足不同规模和需求的监控场景。
