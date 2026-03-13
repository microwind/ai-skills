---
name: 日志分析器
description: "当分析日志、解析错误、查找模式或调试问题时，分析应用程序日志以识别问题和模式。"
license: MIT
---

# 日志分析器技能

## 概述
日志是应用程序的黑匣子飞行记录器。正确读取它们以了解发生了什么。误读日志 = 错误结论。

**核心原则**: 日志不会说谎。日志准确地告诉我们发生了什么。

## 何时使用

**始终:**
- 调试生产问题
- 查找性能瓶颈
- 识别错误模式
- 事后分析
- 监控系统状态
- 安全审计

**触发短语:**
- "分析这个日志文件"
- "查找错误日志"
- "日志中出现异常"
- "性能问题排查"
- "日志模式识别"
- "调试生产问题"

## 日志分析功能

### 日志解析
- 多格式支持
- 时间戳解析
- 结构化日志解析
- 自定义格式支持
- 编码检测

### 错误分析
- 错误级别分类
- 异常堆栈提取
- 错误频率统计
- 错误关联分析
- 根本原因识别

### 模式识别
- 时间模式分析
- 用户行为模式
- 系统性能模式
- 业务流程模式
- 异常检测

## 常见日志问题

### 时间戳混乱
```
问题:
不同服务使用不同的时间格式和时区

错误示例:
[2023-01-01 10:00:00] Service A: Request started
[01/01/2023 10:00:01] Service B: Processing
[2023-01-01 02:00:02 UTC] Service C: Response sent

解决方案:
1. 统一时间格式为 ISO 8601
2. 统一时区为 UTC
3. 在日志中包含时区信息
```

### 日志级别不当
```
问题:
错误使用日志级别，影响问题定位

错误示例:
logger.info("Database connection failed")  ← 应该是 error
logger.debug("User login successful")     ← 应该是 info
logger.error("Page loaded successfully")   ← 应该是 info

解决方案:
- FATAL: 系统无法继续运行
- ERROR: 错误发生，但系统可以继续
- WARN: 潜在问题，需要关注
- INFO: 重要的业务信息
- DEBUG: 调试信息
```

### 敏感信息泄露
```
问题:
日志中包含敏感信息

错误示例:
User login: username=admin, password=secret123
Payment processed: card=4111-1111-1111-1111, cvv=123

解决方案:
- 脱敏处理：User login: username=admin, password=***
- 使用哈希：Payment processed: card_hash=ab123..., cvv=***
- 避免记录敏感字段
```

## 代码实现示例

### 日志分析器
```python
import re
import json
import gzip
from typing import Dict, List, Any, Optional, Union, Iterator
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import logging
from collections import defaultdict, Counter
import statistics

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    thread: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    extra: Dict[str, Any] = None

@dataclass
class LogAnalysis:
    """日志分析结果"""
    total_entries: int
    error_count: int
    warning_count: int
    time_range: tuple
    top_errors: List[tuple]
    performance_metrics: Dict[str, Any]
    patterns: Dict[str, Any]

class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self):
        self.log_patterns = self._initialize_patterns()
        self.time_patterns = self._initialize_time_patterns()
        self.error_patterns = self._initialize_error_patterns()
    
    def parse_log_file(self, file_path: str, log_format: str = "auto") -> Iterator[LogEntry]:
        """解析日志文件"""
        # 检测文件格式
        if file_path.endswith('.gz'):
            opener = gzip.open
        else:
            opener = open
        
        with opener(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = self._parse_log_line(line.strip(), log_format)
                    if entry:
                        yield entry
                except Exception as e:
                    logging.warning(f"Failed to parse line {line_num}: {str(e)}")
                    continue
    
    def _parse_log_line(self, line: str, log_format: str) -> Optional[LogEntry]:
        """解析单行日志"""
        # 自动检测格式
        if log_format == "auto":
            log_format = self._detect_log_format(line)
        
        # 根据格式解析
        if log_format == "json":
            return self._parse_json_log(line)
        elif log_format == "apache":
            return self._parse_apache_log(line)
        elif log_format == "nginx":
            return self._parse_nginx_log(line)
        elif log_format == "python":
            return self._parse_python_log(line)
        else:
            return self._parse_generic_log(line)
    
    def _detect_log_format(self, line: str) -> str:
        """检测日志格式"""
        line = line.strip()
        
        # JSON格式
        if line.startswith('{') and line.endswith('}'):
            return "json"
        
        # Apache格式
        if re.match(r'^\S+ \S+ \S+ \[.+?\] ".+?" \d+ \d+', line):
            return "apache"
        
        # Nginx格式
        if re.match(r'^\S+ - \S+ \[.+?\] ".+?" \d+ \d+ ".+?" ".+?"', line):
            return "nginx"
        
        # Python格式
        if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', line):
            return "python"
        
        return "generic"
    
    def _parse_json_log(self, line: str) -> Optional[LogEntry]:
        """解析JSON格式日志"""
        try:
            data = json.loads(line)
            
            # 提取时间戳
            timestamp = self._parse_timestamp(data.get('timestamp') or data.get('@timestamp') or data.get('time'))
            
            # 提取日志级别
            level_str = data.get('level') or data.get('severity') or 'INFO'
            level = LogLevel(level_str.upper())
            
            # 提取消息
            message = data.get('message') or data.get('msg') or str(data)
            
            # 提取其他字段
            source = data.get('source') or data.get('service') or 'unknown'
            thread = data.get('thread') or data.get('thread_id')
            user_id = data.get('user_id') or data.get('userId')
            request_id = data.get('request_id') or data.get('requestId')
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=message,
                source=source,
                thread=thread,
                user_id=user_id,
                request_id=request_id,
                extra=data
            )
            
        except Exception as e:
            logging.warning(f"Failed to parse JSON log: {str(e)}")
            return None
    
    def _parse_apache_log(self, line: str) -> Optional[LogEntry]:
        """解析Apache格式日志"""
        # Apache Common Log Format
        pattern = r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "([^"]*)" (\d+) (\S+)'
        match = re.match(pattern, line)
        
        if match:
            ip, ident, user, timestamp_str, request, status, size = match.groups()
            
            timestamp = self._parse_timestamp(timestamp_str)
            level = LogLevel.INFO if int(status) < 400 else LogLevel.ERROR
            message = f"{request} - {status}"
            source = "apache"
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=message,
                source=source,
                extra={
                    'ip': ip,
                    'request': request,
                    'status': int(status),
                    'size': size
                }
            )
        
        return None
    
    def _parse_nginx_log(self, line: str) -> Optional[LogEntry]:
        """解析Nginx格式日志"""
        # Nginx Combined Log Format
        pattern = r'^(\S+) - (\S+) \[([^\]]+)\] "([^"]*)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
        match = re.match(pattern, line)
        
        if match:
            ip, ident, user, timestamp_str, request, status, size, referer, user_agent = match.groups()
            
            timestamp = self._parse_timestamp(timestamp_str)
            level = LogLevel.INFO if int(status) < 400 else LogLevel.ERROR
            message = f"{request} - {status}"
            source = "nginx"
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=message,
                source=source,
                extra={
                    'ip': ip,
                    'request': request,
                    'status': int(status),
                    'size': int(size),
                    'referer': referer,
                    'user_agent': user_agent
                }
            )
        
        return None
    
    def _parse_python_log(self, line: str) -> Optional[LogEntry]:
        """解析Python格式日志"""
        # Python logging format
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.*)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str, level_str, message = match.groups()
            
            timestamp = self._parse_timestamp(timestamp_str)
            level = LogLevel(level_str.upper())
            source = "python"
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=message,
                source=source
            )
        
        return None
    
    def _parse_generic_log(self, line: str) -> Optional[LogEntry]:
        """解析通用格式日志"""
        # 尝试提取时间戳
        timestamp = self._extract_timestamp(line)
        
        # 尝试提取日志级别
        level = self._extract_log_level(line)
        
        # 使用整行作为消息
        message = line
        source = "generic"
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=source
        )
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """解析时间戳"""
        if not timestamp_str:
            return datetime.now(timezone.utc)
        
        # 常见时间格式
        formats = [
            '%Y-%m-%d %H:%M:%S,%f',  # Python logging
            '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO 8601 with microseconds
            '%Y-%m-%dT%H:%M:%SZ',      # ISO 8601
            '%Y-%m-%d %H:%M:%S',       # Simple format
            '%d/%b/%Y:%H:%M:%S %z',    # Apache format
            '%Y-%m-%d %H:%M:%S %z',    # With timezone
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # 如果都不匹配，返回当前时间
        logging.warning(f"Failed to parse timestamp: {timestamp_str}")
        return datetime.now(timezone.utc)
    
    def _extract_timestamp(self, line: str) -> datetime:
        """从日志行中提取时间戳"""
        # 时间戳正则模式
        patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,\.]\d{3}',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return self._parse_timestamp(match.group())
        
        return datetime.now(timezone.utc)
    
    def _extract_log_level(self, line: str) -> LogLevel:
        """从日志行中提取日志级别"""
        line_upper = line.upper()
        
        for level in LogLevel:
            if level.value in line_upper:
                return level
        
        return LogLevel.INFO
    
    def analyze_logs(self, log_entries: List[LogEntry]) -> LogAnalysis:
        """分析日志"""
        if not log_entries:
            return LogAnalysis(
                total_entries=0,
                error_count=0,
                warning_count=0,
                time_range=(None, None),
                top_errors=[],
                performance_metrics={},
                patterns={}
            )
        
        # 基本统计
        total_entries = len(log_entries)
        error_count = sum(1 for entry in log_entries if entry.level == LogLevel.ERROR)
        warning_count = sum(1 for entry in log_entries if entry.level == LogLevel.WARN)
        
        # 时间范围
        timestamps = [entry.timestamp for entry in log_entries if entry.timestamp]
        time_range = (min(timestamps), max(timestamps)) if timestamps else (None, None)
        
        # 错误统计
        error_messages = [entry.message for entry in log_entries if entry.level == LogLevel.ERROR]
        top_errors = Counter(error_messages).most_common(10)
        
        # 性能指标
        performance_metrics = self._calculate_performance_metrics(log_entries)
        
        # 模式分析
        patterns = self._analyze_patterns(log_entries)
        
        return LogAnalysis(
            total_entries=total_entries,
            error_count=error_count,
            warning_count=warning_count,
            time_range=time_range,
            top_errors=top_errors,
            performance_metrics=performance_metrics,
            patterns=patterns
        )
    
    def _calculate_performance_metrics(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {}
        
        # 按小时统计
        hourly_counts = defaultdict(int)
        for entry in log_entries:
            hour = entry.timestamp.hour if entry.timestamp else 0
            hourly_counts[hour] += 1
        
        metrics['hourly_distribution'] = dict(hourly_counts)
        metrics['peak_hour'] = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (0, 0)
        
        # 错误率
        if log_entries:
            metrics['error_rate'] = sum(1 for entry in log_entries if entry.level == LogLevel.ERROR) / len(log_entries)
            metrics['warning_rate'] = sum(1 for entry in log_entries if entry.level == LogLevel.WARN) / len(log_entries)
        
        # 响应时间分析（如果有）
        response_times = []
        for entry in log_entries:
            if entry.extra and 'response_time' in entry.extra:
                response_times.append(entry.extra['response_time'])
        
        if response_times:
            metrics['avg_response_time'] = statistics.mean(response_times)
            metrics['median_response_time'] = statistics.median(response_times)
            metrics['p95_response_time'] = sorted(response_times)[int(len(response_times) * 0.95)]
        
        return metrics
    
    def _analyze_patterns(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """分析日志模式"""
        patterns = {}
        
        # 错误模式
        error_entries = [entry for entry in log_entries if entry.level == LogLevel.ERROR]
        if error_entries:
            patterns['error_patterns'] = self._find_error_patterns(error_entries)
        
        # 时间模式
        patterns['time_patterns'] = self._analyze_time_patterns(log_entries)
        
        # 用户行为模式
        patterns['user_patterns'] = self._analyze_user_patterns(log_entries)
        
        return patterns
    
    def _find_error_patterns(self, error_entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """查找错误模式"""
        patterns = []
        
        # 按错误类型分组
        error_types = defaultdict(list)
        for entry in error_entries:
            error_type = self._classify_error(entry.message)
            error_types[error_type].append(entry)
        
        for error_type, entries in error_types.items():
            if len(entries) > 1:  # 只显示重复出现的错误
                patterns.append({
                    'type': error_type,
                    'count': len(entries),
                    'first_occurrence': min(e.timestamp for e in entries),
                    'last_occurrence': max(e.timestamp for e in entries),
                    'sample_message': entries[0].message
                })
        
        return sorted(patterns, key=lambda x: x['count'], reverse=True)
    
    def _classify_error(self, message: str) -> str:
        """分类错误类型"""
        message_lower = message.lower()
        
        if 'connection' in message_lower or 'timeout' in message_lower:
            return 'connection_error'
        elif 'sql' in message_lower or 'database' in message_lower:
            return 'database_error'
        elif 'authentication' in message_lower or 'authorization' in message_lower:
            return 'auth_error'
        elif 'memory' in message_lower or 'out of memory' in message_lower:
            return 'memory_error'
        elif 'file' in message_lower and 'not found' in message_lower:
            return 'file_error'
        else:
            return 'general_error'
    
    def _analyze_time_patterns(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """分析时间模式"""
        patterns = {}
        
        # 按小时统计
        hourly_activity = defaultdict(int)
        for entry in log_entries:
            if entry.timestamp:
                hourly_activity[entry.timestamp.hour] += 1
        
        patterns['hourly_activity'] = dict(hourly_activity)
        
        # 按星期统计
        weekly_activity = defaultdict(int)
        for entry in log_entries:
            if entry.timestamp:
                weekly_activity[entry.timestamp.weekday()] += 1
        
        patterns['weekly_activity'] = dict(weekly_activity)
        
        return patterns
    
    def _analyze_user_patterns(self, log_entries: List[LogEntry]) -> Dict[str, Any]:
        """分析用户行为模式"""
        patterns = {}
        
        # 用户活动统计
        user_activity = defaultdict(int)
        for entry in log_entries:
            if entry.user_id:
                user_activity[entry.user_id] += 1
        
        patterns['user_activity'] = dict(user_activity)
        patterns['active_users'] = len(user_activity)
        
        return patterns
    
    def _initialize_patterns(self) -> Dict[str, Any]:
        """初始化日志模式"""
        return {
            'timestamp_patterns': [
                r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[,\.]\d{3}',
                r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',
            ],
            'level_patterns': [
                r'\b(DEBUG|INFO|WARN|ERROR|FATAL)\b',
            ]
        }
    
    def _initialize_time_patterns(self) -> Dict[str, Any]:
        """初始化时间模式"""
        return {
            'formats': [
                '%Y-%m-%d %H:%M:%S,%f',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
            ]
        }
    
    def _initialize_error_patterns(self) -> Dict[str, Any]:
        """初始化错误模式"""
        return {
            'connection': r'connection|timeout|network',
            'database': r'sql|database|query',
            'authentication': r'auth|login|password',
            'memory': r'memory|out of memory|oom',
            'file': r'file|directory|path',
        }
    
    def generate_analysis_report(self, analysis: LogAnalysis) -> str:
        """生成分析报告"""
        report = ["=== 日志分析报告 ===\n"]
        
        # 基本统计
        report.append("=== 基本统计 ===")
        report.append(f"总日志条目: {analysis.total_entries}")
        report.append(f"错误数量: {analysis.error_count}")
        report.append(f"警告数量: {analysis.warning_count}")
        
        if analysis.total_entries > 0:
            error_rate = analysis.error_count / analysis.total_entries * 100
            warning_rate = analysis.warning_count / analysis.total_entries * 100
            report.append(f"错误率: {error_rate:.2f}%")
            report.append(f"警告率: {warning_rate:.2f}%")
        
        if analysis.time_range[0] and analysis.time_range[1]:
            report.append(f"时间范围: {analysis.time_range[0]} 到 {analysis.time_range[1]}")
        
        report.append("")
        
        # 性能指标
        if analysis.performance_metrics:
            report.append("=== 性能指标 ===")
            metrics = analysis.performance_metrics
            
            if 'peak_hour' in metrics:
                peak_hour, peak_count = metrics['peak_hour']
                report.append(f"最活跃时间: {peak_hour}:00 ({peak_count} 条日志)")
            
            if 'avg_response_time' in metrics:
                report.append(f"平均响应时间: {metrics['avg_response_time']:.2f}ms")
                report.append(f"中位数响应时间: {metrics['median_response_time']:.2f}ms")
                report.append(f"95%响应时间: {metrics['p95_response_time']:.2f}ms")
            
            report.append("")
        
        # 错误分析
        if analysis.top_errors:
            report.append("=== 错误分析 ===")
            for i, (error, count) in enumerate(analysis.top_errors[:10], 1):
                report.append(f"{i}. {error} (出现 {count} 次)")
            report.append("")
        
        # 模式分析
        if analysis.patterns:
            report.append("=== 模式分析 ===")
            patterns = analysis.patterns
            
            if 'error_patterns' in patterns:
                report.append("错误模式:")
                for pattern in patterns['error_patterns'][:5]:
                    report.append(f"  - {pattern['type']}: {pattern['count']} 次")
            
            if 'time_patterns' in patterns:
                time_patterns = patterns['time_patterns']
                if 'peak_hour' in time_patterns:
                    report.append(f"最活跃小时: {time_patterns['peak_hour']}")
            
            if 'user_patterns' in patterns:
                user_patterns = patterns['user_patterns']
                if 'active_users' in user_patterns:
                    report.append(f"活跃用户数: {user_patterns['active_users']}")
        
        return '\n'.join(report)

# 使用示例
def main():
    analyzer = LogAnalyzer()
    
    # 解析日志文件
    log_entries = list(analyzer.parse_log_file("app.log"))
    
    # 分析日志
    analysis = analyzer.analyze_logs(log_entries)
    
    # 生成报告
    report = analyzer.generate_analysis_report(analysis)
    print(report)

if __name__ == "__main__":
    main()
```

### 日志监控工具
```python
import time
import threading
from typing import Dict, List, Any, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue

class LogMonitor(FileSystemEventHandler):
    """日志文件监控器"""
    
    def __init__(self, log_analyzer: LogAnalyzer, alert_callback: Callable):
        self.log_analyzer = log_analyzer
        self.alert_callback = alert_callback
        self.log_queue = queue.Queue()
        self.monitoring = False
        self.error_threshold = 10  # 错误阈值
        self.time_window = 60  # 时间窗口（秒）
        
    def start_monitoring(self, log_paths: List[str]):
        """开始监控日志文件"""
        self.monitoring = True
        
        # 设置文件监控
        observer = Observer()
        for log_path in log_paths:
            observer.schedule(self, log_path, recursive=False)
        
        observer.start()
        
        # 启动日志处理线程
        processing_thread = threading.Thread(target=self._process_logs)
        processing_thread.daemon = True
        processing_thread.start()
        
        print(f"开始监控日志文件: {log_paths}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        Observer().stop()
        Observer().join()
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory and event.src_path.endswith('.log'):
            self._read_new_lines(event.src_path)
    
    def _read_new_lines(self, file_path: str):
        """读取新增的日志行"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 跳到文件末尾
                f.seek(0, 2)
                
                while self.monitoring:
                    line = f.readline()
                    if line:
                        entry = self.log_analyzer._parse_log_line(line.strip())
                        if entry:
                            self.log_queue.put(entry)
                    else:
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"读取日志文件失败: {str(e)}")
    
    def _process_logs(self):
        """处理日志队列"""
        recent_errors = []
        
        while self.monitoring:
            try:
                # 从队列获取日志条目
                entry = self.log_queue.get(timeout=1)
                
                # 检查错误
                if entry.level == LogLevel.ERROR:
                    recent_errors.append(entry)
                    
                    # 清理旧的错误记录
                    current_time = time.time()
                    recent_errors = [
                        e for e in recent_errors 
                        if (current_time - e.timestamp.timestamp()) < self.time_window
                    ]
                    
                    # 检查是否超过阈值
                    if len(recent_errors) >= self.error_threshold:
                        self.alert_callback({
                            'type': 'error_spike',
                            'count': len(recent_errors),
                            'time_window': self.time_window,
                            'errors': recent_errors[-5:]  # 最近5个错误
                        })
                        recent_errors.clear()  # 重置计数
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"处理日志失败: {str(e)}")

# 使用示例
def alert_handler(alert: Dict[str, Any]):
    """告警处理函数"""
    if alert['type'] == 'error_spike':
        print(f"🚨 错误激增告警: {alert['count']} 个错误在 {alert['time_window']} 秒内")
        for error in alert['errors']:
            print(f"  - {error.message}")

def main():
    analyzer = LogAnalyzer()
    monitor = LogMonitor(analyzer, alert_handler)
    
    # 开始监控
    monitor.start_monitoring(["/var/log/app.log"])
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
```

## 日志最佳实践

### 日志记录原则
1. **结构化**: 使用结构化格式（JSON）
2. **一致性**: 统一时间格式和时区
3. **分级**: 正确使用日志级别
4. **上下文**: 包含足够的上下文信息

### 性能考虑
1. **异步**: 使用异步日志记录
2. **缓冲**: 实现日志缓冲机制
3. **轮转**: 定期轮转日志文件
4. **压缩**: 压缩历史日志文件

### 安全考虑
1. **脱敏**: 避免记录敏感信息
2. **访问控制**: 限制日志文件访问权限
3. **传输加密**: 加密日志传输
4. **审计**: 记录日志访问行为

## 相关技能

- **error-handling** - 错误处理
- **monitoring** - 系统监控
- **performance-analysis** - 性能分析
- **security-audit** - 安全审计
