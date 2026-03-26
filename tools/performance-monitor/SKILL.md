---
name: 性能监控器
description: "当监控系统性能、分析资源使用、检测性能瓶颈、优化系统性能或生成性能报告时，提供全面的性能监控和分析解决方案。"
license: MIT
---

# 性能监控器技能

## 概述
性能监控是确保系统稳定运行和优化用户体验的关键技术。它通过实时收集和分析系统指标、应用性能、资源使用情况等数据，帮助识别性能瓶颈、预测系统趋势和制定优化策略。

**核心原则**: 实时监控、数据驱动、预防性维护、持续优化、可视化展示。

## 何时使用

**始终:**
- 监控服务器性能
- 分析应用响应时间
- 检测系统瓶颈
- 优化资源使用
- 生成性能报告
- 设置性能告警
- 预测性能趋势
- 调试性能问题

**触发短语:**
- "系统性能监控"
- "性能瓶颈分析"
- "资源使用率检查"
- "应用性能优化"
- "性能指标监控"
- "性能告警设置"
- "性能报告生成"
- "性能趋势分析"

## 性能监控层次

### 1. 基础设施层
- **CPU使用率**: 处理器负载监控
- **内存使用**: 内存占用和交换区
- **磁盘I/O**: 读写性能和空间使用
- **网络I/O**: 带宽使用和网络延迟
- **系统负载**: 整体系统负载指标

### 2. 应用层
- **响应时间**: 请求处理时间
- **吞吐量**: 每秒处理请求数
- **错误率**: 系统错误和异常
- **并发用户**: 同时在线用户数
- **业务指标**: 关键业务KPI

### 3. 用户体验层
- **页面加载时间**: 前端性能
- **用户交互延迟**: 交互响应时间
- **渲染性能**: 页面渲染速度
- **资源加载**: 静态资源加载时间
- **用户体验指标**: Core Web Vitals

## 常见性能问题

### CPU瓶颈
```
问题:
CPU使用率持续过高

症状:
- 系统响应缓慢
- 进程排队等待
- 用户体验下降
- 系统不稳定

解决方案:
- 优化算法复杂度
- 增加缓存机制
- 使用异步处理
- 负载均衡分布
- 代码性能优化
```

### 内存泄漏
```
问题:
内存使用持续增长不释放

症状:
- 内存使用率上升
- 系统变慢
- OOM错误
- 服务重启频繁

解决方案:
- 检查内存泄漏点
- 优化对象生命周期
- 使用内存分析工具
- 调整JVM参数
- 实施内存监控
```

### I/O瓶颈
```
问题:
磁盘或网络I/O成为瓶颈

症状:
- 读写操作缓慢
- 网络延迟高
- 数据库查询慢
- 文件操作延迟

解决方案:
- 使用SSD存储
- 优化数据库查询
- 实施缓存策略
- 网络优化
- 异步I/O处理
```

## 代码实现示例

### 性能监控器核心类
```python
import psutil
import time
import threading
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque
import queue
import smtplib
from email.mime.text import MIMEText

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    CUSTOM = "custom"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MetricData:
    """指标数据"""
    timestamp: datetime
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str = ""
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric_name: str
    condition: str  # >, <, ==, !=
    threshold: float
    level: AlertLevel
    duration: int = 60  # 持续时间（秒）
    enabled: bool = True
    message_template: str = ""

@dataclass
class Alert:
    """告警信息"""
    timestamp: datetime
    rule_name: str
    level: AlertLevel
    message: str
    current_value: float
    threshold: float
    resolved: bool = False

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, monitoring_interval: int = 5):
        self.monitoring_interval = monitoring_interval
        self.metrics_history: deque = deque(maxlen=10000)
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.monitoring = False
        self.callbacks: List[Callable] = []
        self.db_connection = None
        
        # 初始化数据库
        self._init_database()
        
        # 系统信息
        self.system_info = self._get_system_info()
        
    def _init_database(self):
        """初始化数据库"""
        self.db_connection = sqlite3.connect('performance_monitor.db', check_same_thread=False)
        cursor = self.db_connection.cursor()
        
        # 创建指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp TEXT,
                metric_type TEXT,
                metric_name TEXT,
                value REAL,
                unit TEXT,
                tags TEXT
            )
        ''')
        
        # 创建告警表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                timestamp TEXT,
                rule_name TEXT,
                level TEXT,
                message TEXT,
                current_value REAL,
                threshold REAL,
                resolved BOOLEAN
            )
        ''')
        
        self.db_connection.commit()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            'memory_total': psutil.virtual_memory().total,
            'disk_info': {disk.mountpoint: disk._asdict() for disk in psutil.disk_partitions()},
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
    
    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring:
            self.monitoring = True
            monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitor_thread.start()
            print("性能监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        print("性能监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                
                # 检查告警规则
                self._check_alert_rules()
                
                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(self.get_latest_metrics())
                    except Exception as e:
                        print(f"回调函数执行失败: {str(e)}")
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"监控循环错误: {str(e)}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        timestamp = datetime.now()
        
        # CPU指标
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        self._add_metric(timestamp, MetricType.CPU, "cpu_percent", cpu_percent, "%")
        self._add_metric(timestamp, MetricType.CPU, "cpu_count", cpu_count, "cores")
        
        if cpu_freq:
            self._add_metric(timestamp, MetricType.CPU, "cpu_freq_current", cpu_freq.current, "MHz")
            self._add_metric(timestamp, MetricType.CPU, "cpu_freq_min", cpu_freq.min, "MHz")
            self._add_metric(timestamp, MetricType.CPU, "cpu_freq_max", cpu_freq.max, "MHz")
        
        # 内存指标
        memory = psutil.virtual_memory()
        self._add_metric(timestamp, MetricType.MEMORY, "memory_total", memory.total, "bytes")
        self._add_metric(timestamp, MetricType.MEMORY, "memory_available", memory.available, "bytes")
        self._add_metric(timestamp, MetricType.MEMORY, "memory_percent", memory.percent, "%")
        self._add_metric(timestamp, MetricType.MEMORY, "memory_used", memory.used, "bytes")
        self._add_metric(timestamp, MetricType.MEMORY, "memory_cached", getattr(memory, 'cached', 0), "bytes")
        
        # 磁盘指标
        disk_partitions = psutil.disk_partitions()
        for partition in disk_partitions:
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint)
                mountpoint = partition.mountpoint.replace('/', '_').replace('\\', '_')
                
                self._add_metric(timestamp, MetricType.DISK, f"disk_total_{mountpoint}", 
                              disk_usage.total, "bytes", {"mountpoint": partition.mountpoint})
                self._add_metric(timestamp, MetricType.DISK, f"disk_used_{mountpoint}", 
                              disk_usage.used, "bytes", {"mountpoint": partition.mountpoint})
                self._add_metric(timestamp, MetricType.DISK, f"disk_free_{mountpoint}", 
                              disk_usage.free, "bytes", {"mountpoint": partition.mountpoint})
                self._add_metric(timestamp, MetricType.DISK, f"disk_percent_{mountpoint}", 
                              (disk_usage.used / disk_usage.total) * 100, "%", {"mountpoint": partition.mountpoint})
                
                # 磁盘I/O
                disk_io = psutil.disk_io_counters(perdisk=True)
                if partition.device in disk_io:
                    io_stats = disk_io[partition.device]
                    device_name = partition.device.replace('/', '_').replace('\\', '_')
                    
                    self._add_metric(timestamp, MetricType.DISK, f"disk_read_bytes_{device_name}", 
                                  io_stats.read_bytes, "bytes", {"device": partition.device})
                    self._add_metric(timestamp, MetricType.DISK, f"disk_write_bytes_{device_name}", 
                                  io_stats.write_bytes, "bytes", {"device": partition.device})
                    self._add_metric(timestamp, MetricType.DISK, f"disk_read_count_{device_name}", 
                                  io_stats.read_count, "count", {"device": partition.device})
                    self._add_metric(timestamp, MetricType.DISK, f"disk_write_count_{device_name}", 
                                  io_stats.write_count, "count", {"device": partition.device})
            except PermissionError:
                continue
        
        # 网络指标
        network_io = psutil.net_io_counters()
        self._add_metric(timestamp, MetricType.NETWORK, "network_bytes_sent", network_io.bytes_sent, "bytes")
        self._add_metric(timestamp, MetricType.NETWORK, "network_bytes_recv", network_io.bytes_recv, "bytes")
        self._add_metric(timestamp, MetricType.NETWORK, "network_packets_sent", network_io.packets_sent, "count")
        self._add_metric(timestamp, MetricType.NETWORK, "network_packets_recv", network_io.packets_recv, "count")
        
        # 进程指标
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # CPU使用率最高的进程
        top_cpu_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
        for i, proc in enumerate(top_cpu_processes):
            self._add_metric(timestamp, MetricType.PROCESS, f"top_cpu_process_{i+1}", 
                          proc['cpu_percent'], "%", 
                          {"pid": str(proc['pid']), "name": proc['name']})
        
        # 内存使用率最高的进程
        top_mem_processes = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
        for i, proc in enumerate(top_mem_processes):
            self._add_metric(timestamp, MetricType.PROCESS, f"top_mem_process_{i+1}", 
                          proc['memory_percent'], "%", 
                          {"pid": str(proc['pid']), "name": proc['name']})
    
    def _add_metric(self, timestamp: datetime, metric_type: MetricType, 
                   metric_name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
        """添加指标数据"""
        metric = MetricData(timestamp, metric_type, metric_name, value, unit, tags)
        self.metrics_history.append(metric)
        
        # 保存到数据库
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            timestamp.isoformat(),
            metric_type.value,
            metric_name,
            value,
            unit,
            json.dumps(tags) if tags else "{}"
        ))
        self.db_connection.commit()
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.name] = rule
        print(f"添加告警规则: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str):
        """移除告警规则"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            print(f"移除告警规则: {rule_name}")
    
    def _check_alert_rules(self):
        """检查告警规则"""
        latest_metrics = self.get_latest_metrics()
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            if rule.metric_name in latest_metrics:
                current_value = latest_metrics[rule.metric_name]
                
                # 检查条件
                triggered = False
                if rule.condition == ">":
                    triggered = current_value > rule.threshold
                elif rule.condition == "<":
                    triggered = current_value < rule.threshold
                elif rule.condition == "==":
                    triggered = abs(current_value - rule.threshold) < 0.001
                elif rule.condition == "!=":
                    triggered = abs(current_value - rule.threshold) >= 0.001
                
                if triggered:
                    self._handle_alert_trigger(rule, current_value)
                else:
                    self._handle_alert_resolve(rule_name, current_value)
    
    def _handle_alert_trigger(self, rule: AlertRule, current_value: float):
        """处理告警触发"""
        if rule.name not in self.active_alerts:
            # 新告警
            message = rule.message_template.format(
                rule_name=rule.name,
                threshold=rule.threshold,
                current_value=current_value,
                condition=rule.condition
            )
            
            alert = Alert(
                timestamp=datetime.now(),
                rule_name=rule.name,
                level=rule.level,
                message=message,
                current_value=current_value,
                threshold=rule.threshold
            )
            
            self.active_alerts[rule.name] = alert
            
            # 保存到数据库
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.timestamp.isoformat(),
                alert.rule_name,
                alert.level.value,
                alert.message,
                alert.current_value,
                alert.threshold,
                alert.resolved
            ))
            self.db_connection.commit()
            
            print(f"🚨 告警触发: {rule.name} - {message}")
            
            # 发送通知
            self._send_notification(alert)
    
    def _handle_alert_resolve(self, rule_name: str, current_value: float):
        """处理告警解决"""
        if rule_name in self.active_alerts:
            alert = self.active_alerts[rule_name]
            alert.resolved = True
            
            # 更新数据库
            cursor = self.db_connection.cursor()
            cursor.execute('''
                UPDATE alerts SET resolved = ? WHERE rule_name = ? AND resolved = 0
            ''', (True, rule_name))
            self.db_connection.commit()
            
            print(f"✅ 告警解决: {rule_name}")
            
            del self.active_alerts[rule_name]
    
    def _send_notification(self, alert: Alert):
        """发送通知"""
        # 这里可以实现邮件、短信、Slack等通知
        print(f"通知发送: {alert.level.value} - {alert.message}")
        
        # 示例：邮件通知
        # self._send_email_notification(alert)
    
    def get_latest_metrics(self) -> Dict[str, float]:
        """获取最新指标"""
        if not self.metrics_history:
            return {}
        
        latest_metrics = {}
        seen_metrics = set()
        
        # 从最新的数据开始遍历
        for metric in reversed(self.metrics_history):
            key = metric.metric_name
            if key not in seen_metrics:
                latest_metrics[key] = metric.value
                seen_metrics.add(key)
        
        return latest_metrics
    
    def get_metrics_history(self, metric_name: str, duration_minutes: int = 60) -> List[MetricData]:
        """获取指标历史"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        return [
            metric for metric in self.metrics_history
            if metric.metric_name == metric_name and metric.timestamp >= cutoff_time
        ]
    
    def generate_performance_report(self, duration_minutes: int = 60) -> str:
        """生成性能报告"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # 获取报告期间的指标
        report_metrics = [
            metric for metric in self.metrics_history
            if metric.timestamp >= cutoff_time
        ]
        
        if not report_metrics:
            return "没有可用的性能数据"
        
        # 按指标类型分组
        metrics_by_type = {}
        for metric in report_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        # 生成报告
        report = f"""
# 性能监控报告

**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**监控周期**: {duration_minutes} 分钟
**数据点数**: {len(report_metrics)}

## 系统概览

"""
        
        # CPU统计
        if MetricType.CPU in metrics_by_type:
            cpu_metrics = [m for m in metrics_by_type[MetricType.CPU] if m.metric_name == "cpu_percent"]
            if cpu_metrics:
                cpu_values = [m.value for m in cpu_metrics]
                report += f"### CPU使用率\n"
                report += f"- 平均值: {statistics.mean(cpu_values):.2f}%\n"
                report += f"- 最大值: {max(cpu_values):.2f}%\n"
                report += f"- 最小值: {min(cpu_values):.2f}%\n"
                report += f"- 标准差: {statistics.stdev(cpu_values):.2f}%\n\n"
        
        # 内存统计
        if MetricType.MEMORY in metrics_by_type:
            mem_metrics = [m for m in metrics_by_type[MetricType.MEMORY] if m.metric_name == "memory_percent"]
            if mem_metrics:
                mem_values = [m.value for m in mem_metrics]
                report += f"### 内存使用率\n"
                report += f"- 平均值: {statistics.mean(mem_values):.2f}%\n"
                report += f"- 最大值: {max(mem_values):.2f}%\n"
                report += f"- 最小值: {min(mem_values):.2f}%\n"
                report += f"- 标准差: {statistics.stdev(mem_values):.2f}%\n\n"
        
        # 磁盘统计
        if MetricType.DISK in metrics_by_type:
            disk_metrics = [m for m in metrics_by_type[MetricType.DISK] if m.metric_name.startswith("disk_percent_")]
            if disk_metrics:
                report += f"### 磁盘使用率\n"
                for metric in disk_metrics:
                    mountpoint = metric.tags.get("mountpoint", "unknown")
                    report += f"- {mountpoint}: {metric.value:.2f}%\n"
                report += "\n"
        
        # 网络统计
        if MetricType.NETWORK in metrics_by_type:
            net_sent = [m for m in metrics_by_type[MetricType.NETWORK] if m.metric_name == "network_bytes_sent"]
            net_recv = [m for m in metrics_by_type[MetricType.NETWORK] if m.metric_name == "network_bytes_recv"]
            
            if net_sent and len(net_sent) > 1:
                sent_diff = net_sent[-1].value - net_sent[0].value
                report += f"### 网络流量\n"
                report += f"- 发送流量: {self._format_bytes(sent_diff)}\n"
            
            if net_recv and len(net_recv) > 1:
                recv_diff = net_recv[-1].value - net_recv[0].value
                report += f"- 接收流量: {self._format_bytes(recv_diff)}\n\n"
        
        # 告警统计
        report += f"## 告警统计\n"
        report += f"- 活跃告警: {len(self.active_alerts)}\n"
        if self.active_alerts:
            report += f"- 告警详情:\n"
            for alert in self.active_alerts.values():
                report += f"  - {alert.level.value}: {alert.message}\n"
        
        return report
    
    def _format_bytes(self, bytes_value: float) -> str:
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"
    
    def plot_metrics(self, metric_name: str, duration_minutes: int = 60, save_path: str = None):
        """绘制指标图表"""
        metrics = self.get_metrics_history(metric_name, duration_minutes)
        
        if not metrics:
            print(f"没有指标 {metric_name} 的数据")
            return
        
        timestamps = [m.timestamp for m in metrics]
        values = [m.value for m in metrics]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, values, marker='o', linestyle='-', linewidth=2, markersize=4)
        plt.title(f"{metric_name} - 最近 {duration_minutes} 分钟")
        plt.xlabel("时间")
        plt.ylabel(metrics[0].unit if metrics[0].unit else "值")
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        else:
            plt.show()
    
    def export_metrics(self, file_path: str, format_type: str = "csv", duration_minutes: int = 60):
        """导出指标数据"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        export_data = [
            metric for metric in self.metrics_history
            if metric.timestamp >= cutoff_time
        ]
        
        if format_type.lower() == "csv":
            df = pd.DataFrame([
                {
                    'timestamp': m.timestamp,
                    'metric_type': m.metric_type.value,
                    'metric_name': m.metric_name,
                    'value': m.value,
                    'unit': m.unit,
                    'tags': json.dumps(m.tags) if m.tags else "{}"
                }
                for m in export_data
            ])
            df.to_csv(file_path, index=False)
        
        elif format_type.lower() == "json":
            data = []
            for m in export_data:
                data.append({
                    'timestamp': m.timestamp.isoformat(),
                    'metric_type': m.metric_type.value,
                    'metric_name': m.metric_name,
                    'value': m.value,
                    'unit': m.unit,
                    'tags': m.tags
                })
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"指标数据已导出到: {file_path}")
    
    def add_callback(self, callback: Callable[[Dict[str, float]], None]):
        """添加回调函数"""
        self.callbacks.append(callback)

# 使用示例
def main():
    """示例使用"""
    print("📊 性能监控器启动")
    print("=" * 50)
    
    # 创建监控器
    monitor = PerformanceMonitor(monitoring_interval=5)
    
    # 添加告警规则
    cpu_alert = AlertRule(
        name="high_cpu_usage",
        metric_name="cpu_percent",
        condition=">",
        threshold=80.0,
        level=AlertLevel.WARNING,
        message_template="CPU使用率过高: {current_value:.1f}% > {threshold}%"
    )
    
    memory_alert = AlertRule(
        name="high_memory_usage",
        metric_name="memory_percent",
        condition=">",
        threshold=85.0,
        level=AlertLevel.CRITICAL,
        message_template="内存使用率过高: {current_value:.1f}% > {threshold}%"
    )
    
    monitor.add_alert_rule(cpu_alert)
    monitor.add_alert_rule(memory_alert)
    
    # 添加回调函数
    def metric_callback(metrics):
        if "cpu_percent" in metrics and "memory_percent" in metrics:
            print(f"回调: CPU={metrics['cpu_percent']:.1f}%, MEM={metrics['memory_percent']:.1f}%")
    
    monitor.add_callback(metric_callback)
    
    # 开始监控
    monitor.start_monitoring()
    
    print("监控运行中，按 Ctrl+C 停止...")
    
    try:
        # 运行30秒后生成报告
        time.sleep(30)
        
        # 生成性能报告
        report = monitor.generate_performance_report(30)
        print("\n" + "=" * 50)
        print(report)
        
        # 绘制CPU使用率图表
        monitor.plot_metrics("cpu_percent", 30, "cpu_usage.png")
        
        # 导出数据
        monitor.export_metrics("metrics.csv", "csv", 30)
        
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()
    
    print("\n✅ 性能监控器演示完成!")

if __name__ == "__main__":
    main()
```

### 应用性能监控器
```python
class ApplicationPerformanceMonitor:
    """应用性能监控器"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_counts = deque(maxlen=1000)
        self.active_users = set()
        self.performance_metrics = {}
        
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """记录请求"""
        timestamp = datetime.now()
        
        # 记录响应时间
        self.request_times.append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'response_time': response_time,
            'status_code': status_code
        })
        
        # 记录错误
        if status_code >= 400:
            self.error_counts.append({
                'timestamp': timestamp,
                'endpoint': endpoint,
                'status_code': status_code
            })
        
        # 更新端点指标
        if endpoint not in self.performance_metrics:
            self.performance_metrics[endpoint] = {
                'total_requests': 0,
                'total_response_time': 0,
                'error_count': 0
            }
        
        self.performance_metrics[endpoint]['total_requests'] += 1
        self.performance_metrics[endpoint]['total_response_time'] += response_time
        
        if status_code >= 400:
            self.performance_metrics[endpoint]['error_count'] += 1
    
    def track_user(self, user_id: str):
        """跟踪活跃用户"""
        self.active_users.add(user_id)
    
    def get_performance_summary(self, duration_minutes: int = 5) -> Dict:
        """获取性能摘要"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # 过滤时间范围内的数据
        recent_requests = [
            req for req in self.request_times
            if req['timestamp'] >= cutoff_time
        ]
        
        recent_errors = [
            err for err in self.error_counts
            if err['timestamp'] >= cutoff_time
        ]
        
        if not recent_requests:
            return {
                'total_requests': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'active_users': len(self.active_users),
                'throughput': 0
            }
        
        response_times = [req['response_time'] for req in recent_requests]
        total_requests = len(recent_requests)
        error_count = len(recent_errors)
        
        return {
            'total_requests': total_requests,
            'avg_response_time': statistics.mean(response_times),
            'p95_response_time': self._percentile(response_times, 95),
            'p99_response_time': self._percentile(response_times, 99),
            'error_rate': (error_count / total_requests) * 100,
            'active_users': len(self.active_users),
            'throughput': total_requests / duration_minutes
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

# 使用示例
def main():
    apm = ApplicationPerformanceMonitor()
    print("应用性能监控器已准备就绪!")

if __name__ == "__main__":
    main()
```

## 性能监控最佳实践

### 监控策略
1. **分层监控**: 基础设施、应用、用户体验
2. **关键指标**: 专注最重要的性能指标
3. **合理频率**: 平衡监控精度和资源消耗
4. **数据保留**: 制定数据保留策略
5. **告警优化**: 避免告警疲劳

### 告警管理
1. **分级告警**: 不同级别不同处理方式
2. **阈值设置**: 基于历史数据设置合理阈值
3. **告警抑制**: 避免重复告警
4. **自动恢复**: 问题解决后自动恢复告警
5. **通知渠道**: 多渠道通知确保及时响应

### 性能优化
1. **基线建立**: 建立性能基线
2. **趋势分析**: 分析性能趋势
3. **瓶颈识别**: 快速识别性能瓶颈
4. **容量规划**: 基于监控数据做容量规划
5. **持续优化**: 建立持续优化流程

## 性能监控工具推荐

### 开源工具
- **Prometheus**: 时间序列数据库和监控系统
- **Grafana**: 可视化仪表板
- **InfluxDB**: 时间序列数据库
- **Telegraf**: 数据收集代理
- **Elastic Stack**: 日志和指标分析

### 商业工具
- **Datadog**: 全栈监控
- **New Relic**: 应用性能监控
- **AppDynamics**: 应用性能管理
- **Dynatrace**: AI驱动监控
- **Splunk**: 日志和监控平台

### 云服务
- **AWS CloudWatch**: AWS监控服务
- **Azure Monitor**: Azure监控服务
- **Google Cloud Monitoring**: GCP监控服务
- **阿里云监控**: 阿里云监控

## 相关技能

- **system-optimization** - 系统优化
- **performance-tuning** - 性能调优
- **capacity-planning** - 容量规划
- **bottleneck-analysis** - 瓶颈分析
- **resource-management** - 资源管理
- **metrics-analysis** - 指标分析
