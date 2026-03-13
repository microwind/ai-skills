---
name: 监控与告警
description: "当设计监控系统时，收集系统指标，设置告警规则，分析性能数据。验证监控配置，优化告警策略，和最佳实践。"
license: MIT
---

# 监控与告警技能

## 概述
监控与告警是系统可靠性的重要保障。没有监控的系统是黑盒，无法及时发现和解决问题。好的监控系统应该全面、实时、智能、可扩展。

**核心原则**: 好的监控应该预防性、自动化、上下文丰富、可操作。坏的监控会导致告警疲劳、漏报误报、响应迟缓。

## 何时使用

**始终:**
- 设计系统架构时
- 部署生产服务时
- 优化系统性能时
- 排查系统故障时
- 规划容量扩展时
- 制定运维策略时

**触发短语:**
- "监控与告警"
- "Prometheus配置"
- "告警规则设置"
- "系统监控指标"
- "性能监控分析"
- "告警通知策略"

## 监控与告警功能

### 指标收集
- 系统资源监控
- 应用性能监控
- 业务指标监控
- 自定义指标收集
- 指标聚合计算

### 告警管理
- 告警规则配置
- 告警级别管理
- 告警抑制机制
- 告警升级策略
- 告警通知渠道

### 数据存储
- 时序数据库
- 数据压缩存储
- 数据保留策略
- 数据查询优化
- 历史数据分析

### 可视化展示
- 实时仪表板
- 历史趋势图表
- 自定义可视化
- 报告生成
- 移动端展示

## 常见监控告警问题

### 告警疲劳问题
```
问题:
过多告警导致运维人员疲劳

错误示例:
- 告警阈值设置过低
- 告警规则过于敏感
- 缺少告警抑制
- 告警通知频繁

解决方案:
1. 优化告警阈值
2. 实施告警分级
3. 添加告警抑制规则
4. 设置告警聚合
```

### 监控盲区问题
```
问题:
关键指标缺失导致监控盲区

错误示例:
- 监控覆盖不全
- 指标选择不当
- 采样频率过低
- 监控数据丢失

解决方案:
1. 完善监控覆盖
2. 选择关键指标
3. 调整采样频率
4. 确保数据可靠性
```

### 告警延迟问题
```
问题:
告警响应延迟影响故障处理

错误示例:
- 检测周期过长
- 告警处理延迟
- 通知渠道不畅
- 响应流程复杂

解决方案:
1. 缩短检测周期
2. 优化告警处理
3. 多渠道通知
4. 简化响应流程
```

### 误报漏报问题
```
问题:
告警不准确影响运维效率

错误示例:
- 告警规则设计不当
- 阈值设置不合理
- 缺少上下文信息
- 告警逻辑错误

解决方案:
1. 优化告警规则
2. 动态调整阈值
3. 丰富上下文信息
4. 测试告警逻辑
```

## 代码实现示例

### 监控指标收集器
```python
import time
import json
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import psutil
import requests

@dataclass
class Metric:
    """监控指标"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    metric_type: str  # gauge, counter, histogram

@dataclass
class Alert:
    """告警信息"""
    name: str
    severity: str
    message: str
    labels: Dict[str, str]
    timestamp: datetime
    resolved: bool = False

class MetricsCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.collectors: Dict[str, Callable] = {}
        self.alert_rules: List[Dict[str, Any]] = []
        self.running = False
        self.collect_thread = None
        self.alert_thread = None
        
    def start(self) -> None:
        """启动监控收集器"""
        self.running = True
        
        # 启动指标收集线程
        self.collect_thread = threading.Thread(target=self._collect_loop)
        self.collect_thread.daemon = True
        self.collect_thread.start()
        
        # 启动告警检查线程
        self.alert_thread = threading.Thread(target=self._alert_loop)
        self.alert_thread.daemon = True
        self.alert_thread.start()
        
        logging.info("监控收集器已启动")
    
    def stop(self) -> None:
        """停止监控收集器"""
        self.running = False
        
        if self.collect_thread:
            self.collect_thread.join()
        
        if self.alert_thread:
            self.alert_thread.join()
        
        logging.info("监控收集器已停止")
    
    def register_collector(self, name: str, collector: Callable) -> None:
        """注册指标收集器"""
        self.collectors[name] = collector
    
    def add_alert_rule(self, rule: Dict[str, Any]) -> None:
        """添加告警规则"""
        self.alert_rules.append(rule)
    
    def _collect_loop(self) -> None:
        """指标收集循环"""
        collect_interval = self.config.get('collect_interval', 10)
        
        while self.running:
            try:
                # 收集所有指标
                for name, collector in self.collectors.items():
                    try:
                        metrics = collector()
                        if isinstance(metrics, list):
                            self.metrics.extend(metrics)
                        elif isinstance(metrics, Metric):
                            self.metrics.append(metrics)
                    except Exception as e:
                        logging.error(f"指标收集失败 {name}: {e}")
                
                # 清理过期指标
                self._cleanup_old_metrics()
                
                time.sleep(collect_interval)
            
            except Exception as e:
                logging.error(f"收集循环错误: {e}")
                time.sleep(collect_interval)
    
    def _alert_loop(self) -> None:
        """告警检查循环"""
        alert_interval = self.config.get('alert_interval', 30)
        
        while self.running:
            try:
                # 检查所有告警规则
                self._check_alert_rules()
                
                # 清理已解决的告警
                self._cleanup_resolved_alerts()
                
                time.sleep(alert_interval)
            
            except Exception as e:
                logging.error(f"告警循环错误: {e}")
                time.sleep(alert_interval)
    
    def _cleanup_old_metrics(self) -> None:
        """清理过期指标"""
        retention_period = timedelta(minutes=self.config.get('retention_minutes', 60))
        cutoff_time = datetime.now() - retention_period
        
        self.metrics = [
            metric for metric in self.metrics 
            if metric.timestamp > cutoff_time
        ]
    
    def _cleanup_resolved_alerts(self) -> None:
        """清理已解决的告警"""
        resolved_retention = timedelta(hours=self.config.get('resolved_retention_hours', 24))
        cutoff_time = datetime.now() - resolved_retention
        
        self.alerts = [
            alert for alert in self.alerts 
            if not alert.resolved or alert.timestamp > cutoff_time
        ]
    
    def _check_alert_rules(self) -> None:
        """检查告警规则"""
        for rule in self.alert_rules:
            try:
                self._evaluate_alert_rule(rule)
            except Exception as e:
                logging.error(f"告警规则评估失败: {e}")
    
    def _evaluate_alert_rule(self, rule: Dict[str, Any]) -> None:
        """评估告警规则"""
        metric_name = rule.get('metric')
        condition = rule.get('condition')
        threshold = rule.get('threshold')
        severity = rule.get('severity', 'warning')
        duration = rule.get('duration', 0)
        
        # 获取相关指标
        relevant_metrics = [
            metric for metric in self.metrics 
            if metric.name == metric_name
        ]
        
        if not relevant_metrics:
            return
        
        # 检查条件
        triggered_metrics = []
        for metric in relevant_metrics:
            if self._evaluate_condition(metric.value, condition, threshold):
                triggered_metrics.append(metric)
        
        # 检查持续时间
        if triggered_metrics:
            if duration > 0:
                # 检查是否持续满足条件
                earliest_time = min(m.timestamp for m in triggered_metrics)
                if datetime.now() - earliest_time < timedelta(seconds=duration):
                    return
        
        # 生成或更新告警
        alert_name = f"{metric_name}_{condition}_{threshold}"
        existing_alert = self._find_existing_alert(alert_name)
        
        if triggered_metrics and not existing_alert:
            # 创建新告警
            alert = Alert(
                name=alert_name,
                severity=severity,
                message=self._generate_alert_message(rule, triggered_metrics[-1]),
                labels=rule.get('labels', {}),
                timestamp=datetime.now()
            )
            self.alerts.append(alert)
            self._send_alert(alert)
        
        elif not triggered_metrics and existing_alert:
            # 解决告警
            existing_alert.resolved = True
            self._send_resolved_alert(existing_alert)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """评估条件"""
        if condition == 'gt':
            return value > threshold
        elif condition == 'lt':
            return value < threshold
        elif condition == 'eq':
            return value == threshold
        elif condition == 'gte':
            return value >= threshold
        elif condition == 'lte':
            return value <= threshold
        else:
            return False
    
    def _find_existing_alert(self, alert_name: str) -> Optional[Alert]:
        """查找现有告警"""
        for alert in self.alerts:
            if alert.name == alert_name and not alert.resolved:
                return alert
        return None
    
    def _generate_alert_message(self, rule: Dict[str, Any], metric: Metric) -> str:
        """生成告警消息"""
        return f"告警: {metric.name} {rule.get('condition', '')} {rule.get('threshold', '')} (当前值: {metric.value})"
    
    def _send_alert(self, alert: Alert) -> None:
        """发送告警通知"""
        try:
            # 这里可以实现各种通知方式
            message = f"[{alert.severity.upper()}] {alert.message}"
            
            # 发送到日志
            logging.warning(message)
            
            # 发送到外部通知系统
            if self.config.get('webhook_url'):
                self._send_webhook(alert)
            
            # 发送邮件通知
            if self.config.get('email_enabled'):
                self._send_email(alert)
            
            # 发送Slack通知
            if self.config.get('slack_webhook'):
                self._send_slack(alert)
        
        except Exception as e:
            logging.error(f"告警发送失败: {e}")
    
    def _send_resolved_alert(self, alert: Alert) -> None:
        """发送告警解决通知"""
        try:
            message = f"[RESOLVED] {alert.message}"
            logging.info(message)
            
            # 发送解决通知到外部系统
            if self.config.get('webhook_url'):
                resolved_alert = Alert(
                    name=alert.name,
                    severity=alert.severity,
                    message=f"已解决: {alert.message}",
                    labels=alert.labels,
                    timestamp=datetime.now(),
                    resolved=True
                )
                self._send_webhook(resolved_alert)
        
        except Exception as e:
            logging.error(f"告警解决通知失败: {e}")
    
    def _send_webhook(self, alert: Alert) -> None:
        """发送Webhook通知"""
        try:
            webhook_url = self.config.get('webhook_url')
            
            payload = {
                'alert_name': alert.name,
                'severity': alert.severity,
                'message': alert.message,
                'labels': alert.labels,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
        
        except Exception as e:
            logging.error(f"Webhook发送失败: {e}")
    
    def _send_email(self, alert: Alert) -> None:
        """发送邮件通知"""
        # 这里可以实现邮件发送逻辑
        pass
    
    def _send_slack(self, alert: Alert) -> None:
        """发送Slack通知"""
        try:
            webhook_url = self.config.get('slack_webhook')
            
            color = 'danger' if alert.severity == 'critical' else 'warning'
            if alert.resolved:
                color = 'good'
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': f"告警: {alert.name}",
                    'text': alert.message,
                    'fields': [
                        {'title': '严重程度', 'value': alert.severity, 'short': True},
                        {'title': '时间', 'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'), 'short': True}
                    ],
                    'footer': '监控系统',
                    'ts': int(alert.timestamp.timestamp())
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
        
        except Exception as e:
            logging.error(f"Slack发送失败: {e}")
    
    def get_metrics(self, metric_name: str = None, start_time: datetime = None, end_time: datetime = None) -> List[Metric]:
        """获取指标数据"""
        metrics = self.metrics
        
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
        
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        
        return metrics
    
    def get_alerts(self, severity: str = None, resolved: bool = None) -> List[Alert]:
        """获取告警信息"""
        alerts = self.alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return alerts

# 系统指标收集器
class SystemMetricsCollector:
    @staticmethod
    def cpu_usage() -> Metric:
        """CPU使用率"""
        return Metric(
            name='system_cpu_usage',
            value=psutil.cpu_percent(interval=1),
            labels={'host': 'localhost'},
            timestamp=datetime.now(),
            metric_type='gauge'
        )
    
    @staticmethod
    def memory_usage() -> Metric:
        """内存使用率"""
        memory = psutil.virtual_memory()
        return Metric(
            name='system_memory_usage',
            value=memory.percent,
            labels={'host': 'localhost'},
            timestamp=datetime.now(),
            metric_type='gauge'
        )
    
    @staticmethod
    def disk_usage() -> Metric:
        """磁盘使用率"""
        disk = psutil.disk_usage('/')
        return Metric(
            name='system_disk_usage',
            value=disk.percent,
            labels={'host': 'localhost', 'mount': '/'},
            timestamp=datetime.now(),
            metric_type='gauge'
        )
    
    @staticmethod
    def network_io() -> List[Metric]:
        """网络IO指标"""
        net_io = psutil.net_io_counters()
        return [
            Metric(
                name='system_network_bytes_sent',
                value=net_io.bytes_sent,
                labels={'host': 'localhost'},
                timestamp=datetime.now(),
                metric_type='counter'
            ),
            Metric(
                name='system_network_bytes_recv',
                value=net_io.bytes_recv,
                labels={'host': 'localhost'},
                timestamp=datetime.now(),
                metric_type='counter'
            )
        ]

# 应用指标收集器
class ApplicationMetricsCollector:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def record_request(self, response_time: float, is_error: bool = False) -> None:
        """记录请求"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.response_times.append(response_time)
        
        # 保持最近1000个响应时间
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_request_rate(self) -> Metric:
        """请求速率"""
        return Metric(
            name='app_request_rate',
            value=self.request_count,
            labels={'app': self.app_name},
            timestamp=datetime.now(),
            metric_type='counter'
        )
    
    def get_error_rate(self) -> Metric:
        """错误率"""
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        return Metric(
            name='app_error_rate',
            value=error_rate,
            labels={'app': self.app_name},
            timestamp=datetime.now(),
            metric_type='gauge'
        )
    
    def get_response_time(self) -> Metric:
        """平均响应时间"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return Metric(
            name='app_response_time',
            value=avg_response_time,
            labels={'app': self.app_name},
            timestamp=datetime.now(),
            metric_type='gauge'
        )

# 使用示例
def main():
    # 配置监控收集器
    config = {
        'collect_interval': 10,
        'alert_interval': 30,
        'retention_minutes': 60,
        'resolved_retention_hours': 24,
        'webhook_url': 'https://hooks.slack.com/services/xxx/yyy/zzz',
        'slack_webhook': 'https://hooks.slack.com/services/xxx/yyy/zzz'
    }
    
    collector = MetricsCollector(config)
    
    # 注册系统指标收集器
    collector.register_collector('cpu', SystemMetricsCollector.cpu_usage)
    collector.register_collector('memory', SystemMetricsCollector.memory_usage)
    collector.register_collector('disk', SystemMetricsCollector.disk_usage)
    collector.register_collector('network', SystemMetricsCollector.network_io)
    
    # 注册应用指标收集器
    app_collector = ApplicationMetricsCollector('web-app')
    collector.register_collector('app_requests', app_collector.get_request_rate)
    collector.register_collector('app_errors', app_collector.get_error_rate)
    collector.register_collector('app_response_time', app_collector.get_response_time)
    
    # 添加告警规则
    alert_rules = [
        {
            'metric': 'system_cpu_usage',
            'condition': 'gt',
            'threshold': 80,
            'severity': 'warning',
            'duration': 60,
            'labels': {'component': 'system'}
        },
        {
            'metric': 'system_memory_usage',
            'condition': 'gt',
            'threshold': 90,
            'severity': 'critical',
            'duration': 30,
            'labels': {'component': 'system'}
        },
        {
            'metric': 'app_error_rate',
            'condition': 'gt',
            'threshold': 5,
            'severity': 'warning',
            'duration': 120,
            'labels': {'component': 'application'}
        }
    ]
    
    for rule in alert_rules:
        collector.add_alert_rule(rule)
    
    # 启动监控
    collector.start()
    
    try:
        # 模拟应用运行
        for i in range(100):
            # 模拟请求
            import random
            response_time = random.uniform(0.1, 2.0)
            is_error = random.random() < 0.05  # 5%错误率
            app_collector.record_request(response_time, is_error)
            
            time.sleep(1)
    
    finally:
        collector.stop()

if __name__ == '__main__':
    main()
```

### 告警规则引擎
```python
import re
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class AlertSeverity(Enum):
    """告警严重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class MetricType(Enum):
    """指标类型"""
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"

@dataclass
class AlertCondition:
    """告警条件"""
    metric: str
    operator: str  # gt, lt, eq, gte, lte, regex
    threshold: Union[float, str]
    duration: int  # 持续时间（秒）
    severity: AlertSeverity

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    conditions: List[AlertCondition]
    labels: Dict[str, str]
    annotations: Dict[str, str]
    enabled: bool = True
    last_evaluation: Optional[datetime] = None

@dataclass
class AlertInstance:
    """告警实例"""
    rule_name: str
    severity: AlertSeverity
    message: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    start_time: datetime
    end_time: Optional[datetime] = None
    resolved: bool = False

class AlertRuleEngine:
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, AlertInstance] = {}
        self.alert_history: List[AlertInstance] = []
        
    def add_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self.rules[rule.name] = rule
    
    def remove_rule(self, rule_name: str) -> None:
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            
            # 解决相关的活跃告警
            alert_key = f"{rule_name}_default"
            if alert_key in self.active_alerts:
                self.active_alerts[alert_key].resolved = True
                self.active_alerts[alert_key].end_time = datetime.now()
                self.alert_history.append(self.active_alerts[alert_key])
                del self.active_alerts[alert_key]
    
    def evaluate_rules(self, metrics: Dict[str, Any]) -> List[AlertInstance]:
        """评估所有告警规则"""
        new_alerts = []
        resolved_alerts = []
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                # 评估规则
                triggered = self._evaluate_rule(rule, metrics)
                alert_key = f"{rule_name}_default"
                
                if triggered and alert_key not in self.active_alerts:
                    # 创建新告警
                    alert = self._create_alert_instance(rule, triggered)
                    self.active_alerts[alert_key] = alert
                    new_alerts.append(alert)
                
                elif not triggered and alert_key in self.active_alerts:
                    # 解决告警
                    alert = self.active_alerts[alert_key]
                    alert.resolved = True
                    alert.end_time = datetime.now()
                    self.alert_history.append(alert)
                    del self.active_alerts[alert_key]
                    resolved_alerts.append(alert)
                
                rule.last_evaluation = datetime.now()
            
            except Exception as e:
                print(f"规则评估失败 {rule_name}: {e}")
        
        return new_alerts + resolved_alerts
    
    def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """评估单个告警规则"""
        # 所有条件都必须满足
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, metrics):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: AlertCondition, metrics: Dict[str, Any]) -> bool:
        """评估告警条件"""
        metric_value = metrics.get(condition.metric)
        
        if metric_value is None:
            return False
        
        # 评估操作符
        if condition.operator == 'gt':
            return float(metric_value) > float(condition.threshold)
        elif condition.operator == 'lt':
            return float(metric_value) < float(condition.threshold)
        elif condition.operator == 'eq':
            return metric_value == condition.threshold
        elif condition.operator == 'gte':
            return float(metric_value) >= float(condition.threshold)
        elif condition.operator == 'lte':
            return float(metric_value) <= float(condition.threshold)
        elif condition.operator == 'regex':
            if isinstance(metric_value, str):
                return bool(re.search(condition.threshold, metric_value))
            return False
        else:
            return False
    
    def _create_alert_instance(self, rule: AlertRule, triggered: bool) -> AlertInstance:
        """创建告警实例"""
        # 生成告警消息
        message = self._generate_alert_message(rule)
        
        return AlertInstance(
            rule_name=rule.name,
            severity=rule.conditions[0].severity if rule.conditions else AlertSeverity.WARNING,
            message=message,
            labels=rule.labels.copy(),
            annotations=rule.annotations.copy(),
            start_time=datetime.now()
        )
    
    def _generate_alert_message(self, rule: AlertRule) -> str:
        """生成告警消息"""
        if rule.conditions:
            condition = rule.conditions[0]
            return f"告警: {condition.metric} {condition.operator} {condition.threshold}"
        return f"告警: {rule.name}"
    
    def get_active_alerts(self) -> List[AlertInstance]:
        """获取活跃告警"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[AlertInstance]:
        """获取告警历史"""
        return sorted(self.alert_history, key=lambda a: a.start_time, reverse=True)[:limit]
    
    def get_rule_status(self) -> Dict[str, Dict[str, Any]]:
        """获取规则状态"""
        status = {}
        
        for rule_name, rule in self.rules.items():
            alert_key = f"{rule_name}_default"
            active = alert_key in self.active_alerts
            
            status[rule_name] = {
                'enabled': rule.enabled,
                'last_evaluation': rule.last_evaluation.isoformat() if rule.last_evaluation else None,
                'active_alert': active,
                'conditions_count': len(rule.conditions)
            }
        
        return status

# 告警规则配置示例
def create_sample_rules() -> List[AlertRule]:
    """创建示例告警规则"""
    rules = []
    
    # CPU使用率告警
    cpu_rule = AlertRule(
        name="high_cpu_usage",
        conditions=[
            AlertCondition(
                metric="system_cpu_usage",
                operator="gt",
                threshold=80.0,
                duration=300,
                severity=AlertSeverity.WARNING
            )
        ],
        labels={"component": "system", "metric": "cpu"},
        annotations={"description": "CPU使用率过高"}
    )
    rules.append(cpu_rule)
    
    # 内存使用率告警
    memory_rule = AlertRule(
        name="high_memory_usage",
        conditions=[
            AlertCondition(
                metric="system_memory_usage",
                operator="gt",
                threshold=90.0,
                duration=180,
                severity=AlertSeverity.CRITICAL
            )
        ],
        labels={"component": "system", "metric": "memory"},
        annotations={"description": "内存使用率过高"}
    )
    rules.append(memory_rule)
    
    # 应用错误率告警
    error_rate_rule = AlertRule(
        name="high_error_rate",
        conditions=[
            AlertCondition(
                metric="app_error_rate",
                operator="gt",
                threshold=5.0,
                duration=600,
                severity=AlertSeverity.WARNING
            )
        ],
        labels={"component": "application", "metric": "error_rate"},
        annotations={"description": "应用错误率过高"}
    )
    rules.append(error_rate_rule)
    
    # 磁盘空间告警
    disk_rule = AlertRule(
        name="low_disk_space",
        conditions=[
            AlertCondition(
                metric="system_disk_usage",
                operator="gt",
                threshold=85.0,
                duration=3600,
                severity=AlertSeverity.CRITICAL
            )
        ],
        labels={"component": "system", "metric": "disk"},
        annotations={"description": "磁盘空间不足"}
    )
    rules.append(disk_rule)
    
    return rules

# 使用示例
def main():
    # 创建告警规则引擎
    engine = AlertRuleEngine()
    
    # 添加示例规则
    for rule in create_sample_rules():
        engine.add_rule(rule)
    
    # 模拟指标数据
    sample_metrics = {
        "system_cpu_usage": 85.5,
        "system_memory_usage": 92.3,
        "app_error_rate": 7.8,
        "system_disk_usage": 87.1
    }
    
    # 评估告警规则
    alerts = engine.evaluate_rules(sample_metrics)
    
    print(f"触发了 {len(alerts)} 个告警:")
    for alert in alerts:
        status = "已解决" if alert.resolved else "活跃"
        print(f"- [{alert.severity.value.upper()}] {alert.message} ({status})")
    
    # 获取规则状态
    rule_status = engine.get_rule_status()
    print("\n规则状态:")
    for rule_name, status in rule_status.items():
        print(f"- {rule_name}: {'启用' if status['enabled'] else '禁用'}, 活跃告警: {status['active_alert']}")

if __name__ == '__main__':
    main()
```

## 监控告警最佳实践

### 指标设计
1. **关键指标**: 选择核心业务和技术指标
2. **指标命名**: 使用一致的命名规范
3. **标签丰富**: 添加有意义的标签信息
4. **采样频率**: 根据指标特性设置合适频率
5. **数据类型**: 选择合适的指标类型

### 告警策略
1. **分级告警**: 设置不同严重程度的告警
2. **阈值设置**: 基于历史数据和业务需求
3. **持续时间**: 避免瞬时波动触发告警
4. **告警聚合**: 合并相关告警减少噪音
5. **抑制规则**: 防止告警风暴

### 通知管理
1. **多渠道通知**: 邮件、短信、即时消息等
2. **通知升级**: 重要告警的多级通知
3. **静默规则**: 维护期间的告警静默
4. **值班轮换**: 合理的告警响应安排
5. **自动解决**: 自动检测告警恢复

### 可视化展示
1. **实时仪表板**: 关键指标的实时监控
2. **趋势分析**: 历史数据的趋势展示
3. **告警统计**: 告警频率和类型统计
4. **SLA监控**: 服务水平协议的可视化
5. **容量规划**: 资源使用趋势和预测

## 相关技能

- **log-aggregation** - 日志聚合分析
- **infrastructure-as-code** - 基础设施即代码
- **ci-cd-pipeline** - CI/CD流水线
- **security-best-practices** - 安全最佳实践
