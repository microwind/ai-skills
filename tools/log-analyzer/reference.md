# 日志分析器参考文档

## 日志分析器概述

### 什么是日志分析器
日志分析器是一个专门用于处理、解析和分析各种格式日志数据的工具。该工具支持多种日志源（文件、网络、数据库、API），提供强大的解析引擎、实时分析、异常检测、性能监控和安全分析等功能。通过智能化的日志处理，帮助运维人员快速定位问题、监控系统状态、优化性能和保障安全。

### 主要功能
- **多源支持**: 支持文件、网络、数据库、API等多种日志源
- **格式解析**: 支持Apache、Nginx、JSON、XML等多种日志格式
- **实时分析**: 实时处理日志数据，提供即时分析结果
- **异常检测**: 智能检测异常模式、错误趋势和性能问题
- **安全监控**: 检测安全威胁、攻击行为和异常访问
- **性能分析**: 分析响应时间、吞吐量和资源使用情况
- **可视化展示**: 提供丰富的图表和仪表板展示
- **告警通知**: 支持多种告警方式和通知渠道

## 日志解析引擎

### 通用日志解析器
```python
# log_parser.py
import re
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union, Iterator
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging
from pathlib import Path

class LogFormat(Enum):
    APACHE_COMMON = "apache_common"
    APACHE_COMBINED = "apache_combined"
    NGINX = "nginx"
    JSON = "json"
    XML = "xml"
    SYSLOG = "syslog"
    CUSTOM = "custom"

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    UNKNOWN = "UNKNOWN"

@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    raw_line: str
    ip_address: Optional[str] = None
    user: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    additional_fields: Dict[str, Any] = None

@dataclass
class ParseResult:
    success: bool
    entry: Optional[LogEntry] = None
    error_message: Optional[str] = None

class LogParser:
    def __init__(self):
        self.parsers = {
            LogFormat.APACHE_COMMON: ApacheCommonParser(),
            LogFormat.APACHE_COMBINED: ApacheCombinedParser(),
            LogFormat.NGINX: NginxParser(),
            LogFormat.JSON: JsonParser(),
            LogFormat.XML: XmlParser(),
            LogFormat.SYSLOG: SyslogParser(),
            LogFormat.CUSTOM: CustomParser()
        }
        self.logger = logging.getLogger(__name__)
    
    def parse_line(self, line: str, log_format: LogFormat) -> ParseResult:
        """解析单行日志"""
        parser = self.parsers.get(log_format)
        if not parser:
            return ParseResult(
                success=False,
                error_message=f"不支持的日志格式: {log_format}"
            )
        
        return parser.parse(line)
    
    def parse_file(self, file_path: str, log_format: LogFormat) -> Iterator[ParseResult]:
        """解析日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    result = self.parse_line(line, log_format)
                    if result.success:
                        yield result
                    else:
                        self.logger.warning(f"解析失败 行{line_num}: {result.error_message}")
        
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
            yield ParseResult(success=False, error_message=str(e))
    
    def auto_detect_format(self, sample_lines: List[str]) -> LogFormat:
        """自动检测日志格式"""
        format_scores = {}
        
        for log_format in LogFormat:
            parser = self.parsers.get(log_format)
            if parser:
                score = parser.calculate_confidence(sample_lines)
                format_scores[log_format] = score
        
        # 返回得分最高的格式
        if format_scores:
            best_format = max(format_scores, key=format_scores.get)
            if format_scores[best_format] > 0.5:  # 置信度阈值
                return best_format
        
        return LogFormat.CUSTOM

# 基础解析器抽象类
class BaseParser:
    def parse(self, line: str) -> ParseResult:
        """解析日志行"""
        raise NotImplementedError
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        raise NotImplementedError
    
    def parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """解析时间戳"""
        timestamp_formats = [
            "%d/%b/%Y:%H:%M:%S %z",  # Apache格式
            "%Y-%m-%d %H:%M:%S",     # 标准格式
            "%Y-%m-%dT%H:%M:%S",     # ISO格式
            "%Y-%m-%dT%H:%M:%SZ",    # ISO格式UTC
            "%b %d %H:%M:%S",        # Syslog格式
        ]
        
        for fmt in timestamp_formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # 尝试Unix时间戳
        try:
            timestamp = float(timestamp_str)
            return datetime.fromtimestamp(timestamp)
        except ValueError:
            pass
        
        return None
    
    def parse_log_level(self, level_str: str) -> LogLevel:
        """解析日志级别"""
        level_str = level_str.upper()
        
        level_mapping = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARN": LogLevel.WARN,
            "WARNING": LogLevel.WARN,
            "ERROR": LogLevel.ERROR,
            "ERR": LogLevel.ERROR,
            "FATAL": LogLevel.FATAL,
            "CRITICAL": LogLevel.FATAL,
            "CRIT": LogLevel.FATAL
        }
        
        return level_mapping.get(level_str, LogLevel.UNKNOWN)

class ApacheCommonParser(BaseParser):
    """Apache通用日志格式解析器"""
    
    # Apache Common Log Format: %h %l %u %t "%r" %>s %b
    PATTERN = re.compile(
        r'(?P<ip>\S+) '
        r'(?P<ident>\S+) '
        r'(?P<authuser>\S+) '
        r'\[(?P<timestamp>[^\]]+)\] '
        r'"(?P<request>[^"]*)" '
        r'(?P<status>\d+) '
        r'(?P<size>\S+)'
    )
    
    def parse(self, line: str) -> ParseResult:
        """解析Apache通用日志格式"""
        match = self.PATTERN.match(line)
        if not match:
            return ParseResult(
                success=False,
                error_message="不匹配Apache通用日志格式"
            )
        
        groups = match.groupdict()
        
        # 解析时间戳
        timestamp = self.parse_timestamp(groups['timestamp'])
        if not timestamp:
            return ParseResult(
                success=False,
                error_message=f"无法解析时间戳: {groups['timestamp']}"
            )
        
        # 解析状态码
        try:
            status_code = int(groups['status'])
        except ValueError:
            status_code = None
        
        # 解析请求大小
        try:
            size = int(groups['size']) if groups['size'] != '-' else 0
        except ValueError:
            size = None
        
        # 解析请求信息
        request_parts = groups['request'].split()
        method = request_parts[0] if len(request_parts) > 0 else ""
        path = request_parts[1] if len(request_parts) > 1 else ""
        protocol = request_parts[2] if len(request_parts) > 2 else ""
        
        # 确定日志级别
        level = self._determine_level_from_status(status_code)
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=f"{method} {path} {protocol}",
            source="apache",
            raw_line=line,
            ip_address=groups['ip'],
            user=groups['authuser'] if groups['authuser'] != '-' else None,
            status_code=status_code,
            additional_fields={
                "method": method,
                "path": path,
                "protocol": protocol,
                "size": size,
                "ident": groups['ident']
            }
        )
        
        return ParseResult(success=True, entry=entry)
    
    def _determine_level_from_status(self, status_code: Optional[int]) -> LogLevel:
        """根据状态码确定日志级别"""
        if status_code is None:
            return LogLevel.UNKNOWN
        elif status_code >= 500:
            return LogLevel.ERROR
        elif status_code >= 400:
            return LogLevel.WARN
        else:
            return LogLevel.INFO
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        matched_lines = 0
        for line in sample_lines:
            if self.PATTERN.match(line):
                matched_lines += 1
        
        return matched_lines / len(sample_lines) if sample_lines else 0

class ApacheCombinedParser(BaseParser):
    """Apache组合日志格式解析器"""
    
    # Apache Combined Log Format: %h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-agent}i"
    PATTERN = re.compile(
        r'(?P<ip>\S+) '
        r'(?P<ident>\S+) '
        r'(?P<authuser>\S+) '
        r'\[(?P<timestamp>[^\]]+)\] '
        r'"(?P<request>[^"]*)" '
        r'(?P<status>\d+) '
        r'(?P<size>\S+) '
        r'"(?P<referer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def parse(self, line: str) -> ParseResult:
        """解析Apache组合日志格式"""
        match = self.PATTERN.match(line)
        if not match:
            return ParseResult(
                success=False,
                error_message="不匹配Apache组合日志格式"
            )
        
        groups = match.groupdict()
        
        # 解析时间戳
        timestamp = self.parse_timestamp(groups['timestamp'])
        if not timestamp:
            return ParseResult(
                success=False,
                error_message=f"无法解析时间戳: {groups['timestamp']}"
            )
        
        # 解析状态码
        try:
            status_code = int(groups['status'])
        except ValueError:
            status_code = None
        
        # 解析请求信息
        request_parts = groups['request'].split()
        method = request_parts[0] if len(request_parts) > 0 else ""
        path = request_parts[1] if len(request_parts) > 1 else ""
        protocol = request_parts[2] if len(request_parts) > 2 else ""
        
        # 确定日志级别
        level = self._determine_level_from_status(status_code)
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=f"{method} {path} {protocol}",
            source="apache",
            raw_line=line,
            ip_address=groups['ip'],
            user=groups['authuser'] if groups['authuser'] != '-' else None,
            status_code=status_code,
            referer=groups['referer'] if groups['referer'] != '-' else None,
            user_agent=groups['user_agent'],
            additional_fields={
                "method": method,
                "path": path,
                "protocol": protocol,
                "ident": groups['ident']
            }
        )
        
        return ParseResult(success=True, entry=entry)
    
    def _determine_level_from_status(self, status_code: Optional[int]) -> LogLevel:
        """根据状态码确定日志级别"""
        if status_code is None:
            return LogLevel.UNKNOWN
        elif status_code >= 500:
            return LogLevel.ERROR
        elif status_code >= 400:
            return LogLevel.WARN
        else:
            return LogLevel.INFO
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        matched_lines = 0
        for line in sample_lines:
            if self.PATTERN.match(line):
                matched_lines += 1
        
        return matched_lines / len(sample_lines) if sample_lines else 0

class NginxParser(BaseParser):
    """Nginx日志格式解析器"""
    
    # 默认Nginx格式: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
    PATTERN = re.compile(
        r'(?P<ip>\S+) '
        r'- '
        r'(?P<authuser>\S+) '
        r'\[(?P<timestamp>[^\]]+)\] '
        r'"(?P<request>[^"]*)" '
        r'(?P<status>\d+) '
        r'(?P<size>\d+) '
        r'"(?P<referer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def parse(self, line: str) -> ParseResult:
        """解析Nginx日志格式"""
        match = self.PATTERN.match(line)
        if not match:
            return ParseResult(
                success=False,
                error_message="不匹配Nginx日志格式"
            )
        
        groups = match.groupdict()
        
        # 解析时间戳
        timestamp = self.parse_timestamp(groups['timestamp'])
        if not timestamp:
            return ParseResult(
                success=False,
                error_message=f"无法解析时间戳: {groups['timestamp']}"
            )
        
        # 解析状态码
        try:
            status_code = int(groups['status'])
        except ValueError:
            status_code = None
        
        # 解析请求信息
        request_parts = groups['request'].split()
        method = request_parts[0] if len(request_parts) > 0 else ""
        path = request_parts[1] if len(request_parts) > 1 else ""
        protocol = request_parts[2] if len(request_parts) > 2 else ""
        
        # 确定日志级别
        level = self._determine_level_from_status(status_code)
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=f"{method} {path} {protocol}",
            source="nginx",
            raw_line=line,
            ip_address=groups['ip'],
            user=groups['authuser'] if groups['authuser'] != '-' else None,
            status_code=status_code,
            referer=groups['referer'] if groups['referer'] != '-' else None,
            user_agent=groups['user_agent'],
            additional_fields={
                "method": method,
                "path": path,
                "protocol": protocol,
                "size": int(groups['size'])
            }
        )
        
        return ParseResult(success=True, entry=entry)
    
    def _determine_level_from_status(self, status_code: Optional[int]) -> LogLevel:
        """根据状态码确定日志级别"""
        if status_code is None:
            return LogLevel.UNKNOWN
        elif status_code >= 500:
            return LogLevel.ERROR
        elif status_code >= 400:
            return LogLevel.WARN
        else:
            return LogLevel.INFO
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        matched_lines = 0
        for line in sample_lines:
            if self.PATTERN.match(line):
                matched_lines += 1
        
        return matched_lines / len(sample_lines) if sample_lines else 0

class JsonParser(BaseParser):
    """JSON格式日志解析器"""
    
    def parse(self, line: str) -> ParseResult:
        """解析JSON格式日志"""
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error_message=f"JSON解析失败: {e}"
            )
        
        # 解析时间戳
        timestamp = None
        timestamp_fields = ['timestamp', 'time', '@timestamp', 'datetime', 'date']
        for field in timestamp_fields:
            if field in data:
                timestamp = self.parse_timestamp(str(data[field]))
                if timestamp:
                    break
        
        if not timestamp:
            timestamp = datetime.now()
        
        # 解析日志级别
        level = LogLevel.INFO
        level_fields = ['level', 'severity', 'priority', 'loglevel']
        for field in level_fields:
            if field in data:
                level = self.parse_log_level(str(data[field]))
                break
        
        # 解析消息
        message = ""
        message_fields = ['message', 'msg', 'text', 'content']
        for field in message_fields:
            if field in data:
                message = str(data[field])
                break
        
        # 解析其他字段
        ip_address = data.get('ip') or data.get('remote_addr') or data.get('client_ip')
        user = data.get('user') or data.get('username') or data.get('authuser')
        session_id = data.get('session_id') or data.get('session')
        request_id = data.get('request_id') or data.get('trace_id')
        status_code = data.get('status') or data.get('status_code')
        response_time = data.get('response_time') or data.get('duration')
        user_agent = data.get('user_agent') or data.get('ua')
        referer = data.get('referer') or data.get('referrer')
        
        # 转换数据类型
        if status_code:
            try:
                status_code = int(status_code)
            except ValueError:
                status_code = None
        
        if response_time:
            try:
                response_time = float(response_time)
            except ValueError:
                response_time = None
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=data.get('source', 'json'),
            raw_line=line,
            ip_address=ip_address,
            user=user,
            session_id=session_id,
            request_id=request_id,
            status_code=status_code,
            response_time=response_time,
            user_agent=user_agent,
            referer=referer,
            additional_fields=data
        )
        
        return ParseResult(success=True, entry=entry)
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        valid_json_count = 0
        for line in sample_lines:
            try:
                json.loads(line)
                valid_json_count += 1
            except json.JSONDecodeError:
                continue
        
        return valid_json_count / len(sample_lines) if sample_lines else 0

class XmlParser(BaseParser):
    """XML格式日志解析器"""
    
    def parse(self, line: str) -> ParseResult:
        """解析XML格式日志"""
        try:
            root = ET.fromstring(line)
        except ET.ParseError as e:
            return ParseResult(
                success=False,
                error_message=f"XML解析失败: {e}"
            )
        
        # 解析时间戳
        timestamp = None
        timestamp_elements = root.findall('.//timestamp') + root.findall('.//time')
        for elem in timestamp_elements:
            if elem.text:
                timestamp = self.parse_timestamp(elem.text)
                if timestamp:
                    break
        
        if not timestamp:
            timestamp = datetime.now()
        
        # 解析日志级别
        level = LogLevel.INFO
        level_elements = root.findall('.//level') + root.findall('.//severity')
        for elem in level_elements:
            if elem.text:
                level = self.parse_log_level(elem.text)
                break
        
        # 解析消息
        message = ""
        message_elements = root.findall('.//message') + root.findall('.//msg')
        for elem in message_elements:
            if elem.text:
                message = elem.text
                break
        
        # 解析其他字段
        ip_address = None
        ip_elements = root.findall('.//ip') + root.findall('.//remote_addr')
        for elem in ip_elements:
            if elem.text:
                ip_address = elem.text
                break
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=root.tag or 'xml',
            raw_line=line,
            ip_address=ip_address,
            additional_fields=self._xml_to_dict(root)
        )
        
        return ParseResult(success=True, entry=entry)
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """将XML元素转换为字典"""
        result = {}
        
        # 添加属性
        if element.attrib:
            result.update(element.attrib)
        
        # 添加子元素
        for child in element:
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(self._xml_to_dict(child))
            else:
                if len(child) == 0:
                    result[child.tag] = child.text
                else:
                    result[child.tag] = self._xml_to_dict(child)
        
        # 添加文本内容
        if element.text and element.text.strip():
            if result:
                result['text'] = element.text.strip()
            else:
                result = element.text.strip()
        
        return result
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        valid_xml_count = 0
        for line in sample_lines:
            try:
                ET.fromstring(line)
                valid_xml_count += 1
            except ET.ParseError:
                continue
        
        return valid_xml_count / len(sample_lines) if sample_lines else 0

class SyslogParser(BaseParser):
    """Syslog格式解析器"""
    
    # RFC3164 Syslog格式: <priority>timestamp hostname tag message
    PATTERN = re.compile(
        r'<(?P<priority>\d+)>'
        r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<tag>\S+):\s*'
        r'(?P<message>.*)'
    )
    
    def parse(self, line: str) -> ParseResult:
        """解析Syslog格式"""
        match = self.PATTERN.match(line)
        if not match:
            return ParseResult(
                success=False,
                error_message="不匹配Syslog格式"
            )
        
        groups = match.groupdict()
        
        # 解析优先级
        try:
            priority = int(groups['priority'])
            facility = priority >> 3
            severity = priority & 7
            level = self._severity_to_level(severity)
        except ValueError:
            level = LogLevel.INFO
        
        # 解析时间戳
        timestamp = self.parse_timestamp(groups['timestamp'])
        if not timestamp:
            timestamp = datetime.now()
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=groups['message'],
            source=groups['hostname'],
            raw_line=line,
            additional_fields={
                'tag': groups['tag'],
                'priority': groups['priority'],
                'facility': facility,
                'severity': severity
            }
        )
        
        return ParseResult(success=True, entry=entry)
    
    def _severity_to_level(self, severity: int) -> LogLevel:
        """将Syslog严重性转换为日志级别"""
        severity_mapping = {
            0: LogLevel.ERROR,    # Emergency
            1: LogLevel.ERROR,    # Alert
            2: LogLevel.ERROR,    # Critical
            3: LogLevel.ERROR,    # Error
            4: LogLevel.WARN,     # Warning
            5: LogLevel.INFO,     # Notice
            6: LogLevel.INFO,     # Informational
            7: LogLevel.DEBUG     # Debug
        }
        
        return severity_mapping.get(severity, LogLevel.INFO)
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        matched_lines = 0
        for line in sample_lines:
            if self.PATTERN.match(line):
                matched_lines += 1
        
        return matched_lines / len(sample_lines) if sample_lines else 0

class CustomParser(BaseParser):
    """自定义格式解析器"""
    
    def __init__(self):
        self.pattern = None
        self.field_mapping = {}
    
    def set_pattern(self, pattern: str, field_mapping: Dict[str, str]):
        """设置自定义模式"""
        self.pattern = re.compile(pattern)
        self.field_mapping = field_mapping
    
    def parse(self, line: str) -> ParseResult:
        """解析自定义格式"""
        if not self.pattern:
            return ParseResult(
                success=False,
                error_message="未设置自定义模式"
            )
        
        match = self.pattern.match(line)
        if not match:
            return ParseResult(
                success=False,
                error_message="不匹配自定义模式"
            )
        
        groups = match.groupdict()
        
        # 解析时间戳
        timestamp = None
        timestamp_field = self.field_mapping.get('timestamp', 'timestamp')
        if timestamp_field in groups:
            timestamp = self.parse_timestamp(groups[timestamp_field])
        
        if not timestamp:
            timestamp = datetime.now()
        
        # 解析日志级别
        level = LogLevel.INFO
        level_field = self.field_mapping.get('level', 'level')
        if level_field in groups:
            level = self.parse_log_level(groups[level_field])
        
        # 解析消息
        message = ""
        message_field = self.field_mapping.get('message', 'message')
        if message_field in groups:
            message = groups[message_field]
        
        # 解析其他字段
        ip_address = groups.get(self.field_mapping.get('ip', 'ip'))
        user = groups.get(self.field_mapping.get('user', 'user'))
        
        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source="custom",
            raw_line=line,
            ip_address=ip_address,
            user=user,
            additional_fields=groups
        )
        
        return ParseResult(success=True, entry=entry)
    
    def calculate_confidence(self, sample_lines: List[str]) -> float:
        """计算格式置信度"""
        if not self.pattern:
            return 0.0
        
        matched_lines = 0
        for line in sample_lines:
            if self.pattern.match(line):
                matched_lines += 1
        
        return matched_lines / len(sample_lines) if sample_lines else 0

# 使用示例
parser = LogParser()

# 自动检测格式
sample_lines = [
    '192.168.1.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
    '{"timestamp": "2023-12-25T10:00:00Z", "level": "INFO", "message": "User login", "user": "john"}'
]

detected_format = parser.auto_detect_format(sample_lines)
print(f"检测到格式: {detected_format}")

# 解析日志行
log_line = '192.168.1.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
result = parser.parse_line(log_line, LogFormat.APACHE_COMBINED)

if result.success:
    entry = result.entry
    print(f"时间: {entry.timestamp}")
    print(f"级别: {entry.level}")
    print(f"消息: {entry.message}")
    print(f"IP: {entry.ip_address}")
    print(f"状态码: {entry.status_code}")
else:
    print(f"解析失败: {result.error_message}")

# 解析JSON日志
json_line = '{"timestamp": "2023-12-25T10:00:00Z", "level": "INFO", "message": "User login", "user": "john"}'
result = parser.parse_line(json_line, LogFormat.JSON)

if result.success:
    entry = result.entry
    print(f"JSON解析 - 时间: {entry.timestamp}, 用户: {entry.user}")
```

## 实时分析引擎

### 实时日志分析器
```python
# realtime_analyzer.py
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import queue
import logging
from log_parser import LogEntry, LogLevel, LogParser, ParseResult

@dataclass
class AnalysisRule:
    name: str
    condition: str
    action: str
    threshold: Optional[float] = None
    time_window: Optional[int] = None
    enabled: bool = True

@dataclass
class AlertEvent:
    rule_name: str
    timestamp: datetime
    severity: str
    message: str
    details: Dict[str, Any]

class RealtimeAnalyzer:
    def __init__(self):
        self.log_parser = LogParser()
        self.analysis_rules = []
        self.alert_handlers = []
        self.is_running = False
        self.log_queue = queue.Queue()
        self.metrics = defaultdict(int)
        self.time_series_data = defaultdict(lambda: deque(maxlen=1000))
        self.logger = logging.getLogger(__name__)
        
        # 启动分析线程
        self.analysis_thread = threading.Thread(target=self._analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def add_log_line(self, line: str, log_format: str = "auto"):
        """添加日志行到分析队列"""
        try:
            if log_format == "auto":
                # 自动检测格式
                sample_lines = [line]
                detected_format = self.log_parser.auto_detect_format(sample_lines)
                format_enum = self.log_parser.parsers.get(detected_format)
            else:
                format_enum = self.log_parser.parsers.get(log_format)
            
            self.log_queue.put((line, format_enum))
        except Exception as e:
            self.logger.error(f"添加日志行失败: {e}")
    
    def add_analysis_rule(self, rule: AnalysisRule):
        """添加分析规则"""
        self.analysis_rules.append(rule)
    
    def add_alert_handler(self, handler: Callable[[AlertEvent], None]):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def start_analysis(self):
        """开始实时分析"""
        self.is_running = True
        self.logger.info("实时分析已启动")
    
    def stop_analysis(self):
        """停止实时分析"""
        self.is_running = False
        self.logger.info("实时分析已停止")
    
    def _analysis_worker(self):
        """分析工作线程"""
        while True:
            try:
                if not self.is_running:
                    time.sleep(1)
                    continue
                
                # 从队列获取日志
                try:
                    line, log_format = self.log_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # 解析日志
                if log_format:
                    result = self.log_parser.parse_line(line, log_format)
                else:
                    # 尝试所有格式
                    result = None
                    for fmt in self.log_parser.parsers:
                        result = self.log_parser.parse_line(line, fmt)
                        if result.success:
                            break
                
                if result and result.success:
                    self._process_log_entry(result.entry)
                else:
                    self.logger.warning(f"日志解析失败: {line}")
                
                # 标记任务完成
                self.log_queue.task_done()
            
            except Exception as e:
                self.logger.error(f"分析工作线程错误: {e}")
    
    def _process_log_entry(self, entry: LogEntry):
        """处理日志条目"""
        # 更新指标
        self._update_metrics(entry)
        
        # 应用分析规则
        for rule in self.analysis_rules:
            if rule.enabled and self._evaluate_rule(rule, entry):
                self._trigger_alert(rule, entry)
    
    def _update_metrics(self, entry: LogEntry):
        """更新指标"""
        # 基础指标
        self.metrics['total_logs'] += 1
        self.metrics[f'level_{entry.level.value.lower()}'] += 1
        self.metrics[f'source_{entry.source}'] += 1
        
        # 时间序列数据
        timestamp_key = entry.timestamp.strftime('%Y-%m-%d %H:%M')
        self.time_series_data['logs_per_minute'].append((entry.timestamp, 1))
        
        # 错误率
        if entry.level in [LogLevel.ERROR, LogLevel.FATAL]:
            self.time_series_data['errors_per_minute'].append((entry.timestamp, 1))
        
        # 响应时间
        if entry.response_time:
            self.time_series_data['response_time'].append((entry.timestamp, entry.response_time))
        
        # 状态码
        if entry.status_code:
            self.time_series_data[f'status_{entry.status_code}'].append((entry.timestamp, 1))
    
    def _evaluate_rule(self, rule: AnalysisRule, entry: LogEntry) -> bool:
        """评估分析规则"""
        try:
            # 这里应该实现规则条件评估
            # 简化实现，基于规则名称进行基本判断
            
            if rule.name == "error_rate_high":
                return self._check_error_rate(rule, entry)
            elif rule.name == "response_time_slow":
                return self._check_response_time(rule, entry)
            elif rule.name == "status_code_error":
                return self._check_status_code_error(rule, entry)
            elif rule.name == "log_level_error":
                return self._check_log_level_error(rule, entry)
            else:
                return False
        
        except Exception as e:
            self.logger.error(f"规则评估失败 {rule.name}: {e}")
            return False
    
    def _check_error_rate(self, rule: AnalysisRule, entry: LogEntry) -> bool:
        """检查错误率"""
        time_window = rule.time_window or 300  # 默认5分钟
        threshold = rule.threshold or 0.1  # 默认10%
        
        # 获取时间窗口内的错误数和总数
        now = datetime.now()
        start_time = now - timedelta(seconds=time_window)
        
        error_count = 0
        total_count = 0
        
        for timestamp, count in self.time_series_data['logs_per_minute']:
            if timestamp >= start_time:
                total_count += count
        
        for timestamp, count in self.time_series_data['errors_per_minute']:
            if timestamp >= start_time:
                error_count += count
        
        if total_count == 0:
            return False
        
        error_rate = error_count / total_count
        return error_rate > threshold
    
    def _check_response_time(self, rule: AnalysisRule, entry: LogEntry) -> bool:
        """检查响应时间"""
        if not entry.response_time:
            return False
        
        threshold = rule.threshold or 5.0  # 默认5秒
        return entry.response_time > threshold
    
    def _check_status_code_error(self, rule: AnalysisRule, entry: LogEntry) -> bool:
        """检查状态码错误"""
        if not entry.status_code:
            return False
        
        return entry.status_code >= 400
    
    def _check_log_level_error(self, rule: AnalysisRule, entry: LogEntry) -> bool:
        """检查日志级别错误"""
        return entry.level in [LogLevel.ERROR, LogLevel.FATAL]
    
    def _trigger_alert(self, rule: AnalysisRule, entry: LogEntry):
        """触发告警"""
        alert = AlertEvent(
            rule_name=rule.name,
            timestamp=datetime.now(),
            severity=self._get_alert_severity(rule),
            message=self._generate_alert_message(rule, entry),
            details={
                'entry': entry,
                'rule': rule,
                'metrics': dict(self.metrics)
            }
        )
        
        # 发送告警
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"告警处理器错误: {e}")
    
    def _get_alert_severity(self, rule: AnalysisRule) -> str:
        """获取告警严重性"""
        severity_mapping = {
            "error_rate_high": "high",
            "response_time_slow": "medium",
            "status_code_error": "medium",
            "log_level_error": "high"
        }
        return severity_mapping.get(rule.name, "medium")
    
    def _generate_alert_message(self, rule: AnalysisRule, entry: LogEntry) -> str:
        """生成告警消息"""
        message_templates = {
            "error_rate_high": f"错误率过高: {entry.source}",
            "response_time_slow": f"响应时间过慢: {entry.response_time}s",
            "status_code_error": f"HTTP错误状态码: {entry.status_code}",
            "log_level_error": f"错误日志: {entry.message}"
        }
        return message_templates.get(rule.name, f"触发规则: {rule.name}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return dict(self.metrics)
    
    def get_time_series_data(self, metric_name: str, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[tuple]:
        """获取时间序列数据"""
        data = list(self.time_series_data.get(metric_name, []))
        
        if start_time:
            data = [(t, v) for t, v in data if t >= start_time]
        
        if end_time:
            data = [(t, v) for t, v in data if t <= end_time]
        
        return data

# 告警处理器示例
class ConsoleAlertHandler:
    def __call__(self, alert: AlertEvent):
        """控制台告警处理器"""
        print(f"[ALERT] {alert.timestamp} - {alert.severity.upper()}")
        print(f"规则: {alert.rule_name}")
        print(f"消息: {alert.message}")
        print("-" * 50)

class EmailAlertHandler:
    def __init__(self, smtp_config: Dict[str, str]):
        self.smtp_config = smtp_config
    
    def __call__(self, alert: AlertEvent):
        """邮件告警处理器"""
        import smtplib
        from email.mime.text import MIMEText
        
        try:
            subject = f"[ALERT] {alert.rule_name} - {alert.severity.upper()}"
            body = f"""
时间: {alert.timestamp}
规则: {alert.rule_name}
严重性: {alert.severity}
消息: {alert.message}

详情:
{alert.details}
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
            
        except Exception as e:
            print(f"邮件发送失败: {e}")

# 使用示例
analyzer = RealtimeAnalyzer()

# 添加分析规则
error_rate_rule = AnalysisRule(
    name="error_rate_high",
    condition="error_rate > 0.1",
    action="alert",
    threshold=0.1,
    time_window=300
)

response_time_rule = AnalysisRule(
    name="response_time_slow",
    condition="response_time > 5.0",
    action="alert",
    threshold=5.0
)

analyzer.add_analysis_rule(error_rate_rule)
analyzer.add_analysis_rule(response_time_rule)

# 添加告警处理器
console_handler = ConsoleAlertHandler()
analyzer.add_alert_handler(console_handler)

# 邮件告警处理器（可选）
# email_config = {
#     'host': 'smtp.gmail.com',
#     'port': 587,
#     'username': 'your_email@gmail.com',
#     'password': 'your_password',
#     'from': 'your_email@gmail.com',
#     'to': 'admin@example.com'
# }
# email_handler = EmailAlertHandler(email_config)
# analyzer.add_alert_handler(email_handler)

# 启动分析
analyzer.start_analysis()

# 模拟日志输入
import json

sample_logs = [
    '{"timestamp": "2023-12-25T10:00:00Z", "level": "INFO", "message": "Request processed", "response_time": 0.5}',
    '{"timestamp": "2023-12-25T10:00:01Z", "level": "ERROR", "message": "Database connection failed"}',
    '{"timestamp": "2023-12-25T10:00:02Z", "level": "INFO", "message": "Request processed", "response_time": 6.0}',
    '{"timestamp": "2023-12-25T10:00:03Z", "level": "WARN", "message": "High memory usage"}',
]

for log_line in sample_logs:
    analyzer.add_log_line(log_line, "json")
    time.sleep(0.1)

# 等待分析完成
time.sleep(2)

# 获取指标
metrics = analyzer.get_metrics()
print(f"总日志数: {metrics['total_logs']}")
print(f"错误日志数: {metrics['level_error']}")

# 停止分析
analyzer.stop_analysis()
```

## 参考资源

### 日志格式标准
- [Apache Log Formats](https://httpd.apache.org/docs/2.4/logs.html)
- [Nginx Log Formats](https://nginx.org/en/docs/http/ngx_http_log_module.html)
- [Syslog Protocol](https://tools.ietf.org/html/rfc3164)
- [JSON Logging](https://jsonlog.org/)

### 日志分析工具
- [ELK Stack](https://www.elastic.co/)
- [Fluentd](https://www.fluentd.org/)
- [Logstash](https://www.elastic.co/logstash/)
- [Graylog](https://www.graylog.org/)

### 监控和告警
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Alertmanager](https://prometheus.io/docs/alerting/alertmanager/)
- [PagerDuty](https://www.pagerduty.com/)

### 安全分析
- [OSSEC](https://www.ossec.net/)
- [Wazuh](https://wazuh.com/)
- [Splunk](https://www.splunk.com/)
- [LogRhythm](https://logrhythm.com/)
