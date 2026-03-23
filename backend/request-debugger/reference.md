# 请求调试器参考文档

## 请求调试器概述

### 什么是请求调试器
请求调试器是一种用于捕获、分析、监控HTTP/HTTPS请求和响应的工具，通过实时拦截网络流量、记录请求详情、分析性能指标、检测异常行为等功能，帮助开发者快速定位问题、优化性能、提升安全性。该技能涵盖了请求捕获、数据分析、性能监控、安全防护、智能分析等功能，帮助开发者构建功能完善、性能优异的调试系统。

### 主要功能
- **请求捕获**: 支持多种协议和方法的请求拦截与记录
- **实时分析**: 提供请求响应时间、状态码、错误率等实时分析
- **性能监控**: 包含DNS解析、连接建立、SSL握手等性能指标监控
- **安全检测**: 提供SQL注入、XSS攻击、暴力破解等安全威胁检测
- **智能分析**: 支持机器学习异常检测、趋势分析、智能推荐等功能

## 请求调试器核心

### 请求捕获引擎
```python
# request_debugger.py
import asyncio
import json
import time
import uuid
import hashlib
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
import gzip
import base64
from urllib.parse import urlparse, parse_qs
import sqlite3
import redis
from concurrent.futures import ThreadPoolExecutor
import statistics
import ipaddress

class RequestType(Enum):
    """请求类型枚举"""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    GRAPHQL = "graphql"

class CaptureStatus(Enum):
    """捕获状态枚举"""
    PENDING = "pending"
    CAPTURING = "capturing"
    COMPLETED = "completed"
    FAILED = "failed"
    FILTERED = "filtered"

class AnalysisType(Enum):
    """分析类型枚举"""
    BASIC = "basic"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BEHAVIOR = "behavior"
    CUSTOM = "custom"

@dataclass
class RequestConfig:
    """请求调试配置"""
    # 基础配置
    debug_name: str = "request-debugger"
    debug_type: str = RequestType.HTTP.value
    debug_mode: str = "real-time"
    
    # 捕获配置
    capture_protocols: List[str] = field(default_factory=lambda: ["http", "https"])
    capture_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    capture_headers: bool = True
    capture_body: bool = True
    capture_response: bool = True
    max_body_size: int = 1024 * 1024  # 1MB
    
    # 过滤配置
    url_filters: List[str] = field(default_factory=list)
    exclude_filters: List[str] = field(default_factory=list)
    static_resource_filters: List[str] = field(default_factory=lambda: [".css", ".js", ".png", ".jpg", ".gif"])
    
    # 存储配置
    storage_type: str = "memory"  # memory, file, database
    storage_path: str = "./debug_data"
    max_records: int = 10000
    retention_days: int = 7
    
    # 安全配置
    sensitive_fields: List[str] = field(default_factory=lambda: ["password", "token", "jwt", "session"])
    mask_sensitive_data: bool = True
    enable_access_control: bool = False
    
    # 监控配置
    enable_monitoring: bool = True
    monitoring_interval: int = 60  # 秒
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "response_time": 5000,  # 毫秒
        "error_rate": 5.0,  # 百分比
        "request_rate": 1000  # 每秒请求数
    })
    
    # 集成配置
    enable_ai_analysis: bool = False
    enable_ml_detection: bool = False
    enable_distribution: bool = False

@dataclass
class RequestData:
    """请求数据"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    method: str = ""
    url: str = ""
    protocol: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    body_size: int = 0
    query_params: Dict[str, str] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    client_ip: str = ""
    user_agent: str = ""
    status_code: int = 0
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: str = ""
    response_size: int = 0
    response_time: float = 0.0
    error_message: str = ""
    capture_status: str = CaptureStatus.PENDING.value

@dataclass
class PerformanceMetrics:
    """性能指标"""
    dns_time: float = 0.0
    connect_time: float = 0.0
    ssl_time: float = 0.0
    first_byte_time: float = 0.0
    total_time: float = 0.0
    upload_time: float = 0.0
    download_time: float = 0.0

@dataclass
class SecurityAlert:
    """安全告警"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    alert_type: str = ""
    severity: str = "medium"  # low, medium, high, critical
    description: str = ""
    request_id: str = ""
    client_ip: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

class RequestFilter:
    """请求过滤器"""
    
    def __init__(self, config: RequestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.url_include_patterns = [re.compile(pattern) for pattern in config.url_filters]
        self.url_exclude_patterns = [re.compile(pattern) for pattern in config.exclude_filters]
        self.static_patterns = [re.compile(f".*{ext}$") for ext in config.static_resource_filters]
    
    def should_capture(self, request_data: RequestData) -> bool:
        """判断是否应该捕获请求"""
        # 检查协议
        if request_data.protocol.lower() not in self.config.capture_protocols:
            return False
        
        # 检查方法
        if request_data.method.upper() not in self.config.capture_methods:
            return False
        
        # 检查URL包含规则
        if self.url_include_patterns:
            if not any(pattern.match(request_data.url) for pattern in self.url_include_patterns):
                return False
        
        # 检查URL排除规则
        if self.url_exclude_patterns:
            if any(pattern.match(request_data.url) for pattern in self.url_exclude_patterns):
                return False
        
        # 检查静态资源
        if self.static_patterns:
            if any(pattern.match(request_data.url) for pattern in self.static_patterns):
                return False
        
        return True
    
    def filter_sensitive_data(self, request_data: RequestData) -> RequestData:
        """过滤敏感数据"""
        if not self.config.mask_sensitive_data:
            return request_data
        
        # 过滤请求头中的敏感数据
        filtered_headers = {}
        for key, value in request_data.headers.items():
            if any(sensitive in key.lower() for sensitive in self.config.sensitive_fields):
                filtered_headers[key] = "***MASKED***"
            else:
                filtered_headers[key] = value
        
        request_data.headers = filtered_headers
        
        # 过滤请求体中的敏感数据
        if request_data.body:
            try:
                # 尝试解析JSON
                body_json = json.loads(request_data.body)
                filtered_body = self._mask_sensitive_json(body_json)
                request_data.body = json.dumps(filtered_body)
            except json.JSONDecodeError:
                # 非JSON数据，简单替换
                for sensitive_field in self.config.sensitive_fields:
                    request_data.body = re.sub(
                        f'({sensitive_field}[=:]\s*)([^\s&]+)',
                        f'\\1***MASKED***',
                        request_data.body,
                        flags=re.IGNORECASE
                    )
        
        return request_data
    
    def _mask_sensitive_json(self, data: Any) -> Any:
        """递归屏蔽JSON中的敏感数据"""
        if isinstance(data, dict):
            filtered_data = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.config.sensitive_fields):
                    filtered_data[key] = "***MASKED***"
                elif isinstance(value, (dict, list)):
                    filtered_data[key] = self._mask_sensitive_json(value)
                else:
                    filtered_data[key] = value
            return filtered_data
        elif isinstance(data, list):
            return [self._mask_sensitive_json(item) for item in data]
        else:
            return data

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: RequestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.request_stats = defaultdict(list)
        self.error_stats = defaultdict(int)
        self.performance_stats = defaultdict(list)
    
    def process_request(self, request_data: RequestData) -> Dict[str, Any]:
        """处理请求数据"""
        processed_data = {
            'basic_stats': self._calculate_basic_stats(request_data),
            'performance_stats': self._calculate_performance_stats(request_data),
            'security_analysis': self._analyze_security(request_data),
            'behavior_analysis': self._analyze_behavior(request_data)
        }
        
        # 更新统计信息
        self._update_statistics(request_data)
        
        return processed_data
    
    def _calculate_basic_stats(self, request_data: RequestData) -> Dict[str, Any]:
        """计算基础统计"""
        return {
            'request_count': 1,
            'status_code': request_data.status_code,
            'response_time': request_data.response_time,
            'request_size': request_data.body_size,
            'response_size': request_data.response_size,
            'method': request_data.method,
            'url': request_data.url,
            'client_ip': request_data.client_ip
        }
    
    def _calculate_performance_stats(self, request_data: RequestData) -> Dict[str, Any]:
        """计算性能统计"""
        # 解析URL获取域名
        parsed_url = urlparse(request_data.url)
        domain = parsed_url.netloc
        
        # 记录性能数据
        self.performance_stats[domain].append(request_data.response_time)
        
        # 计算统计指标
        response_times = self.performance_stats[domain]
        if len(response_times) > 1:
            return {
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'std_response_time': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                'p95_response_time': self._percentile(response_times, 95),
                'p99_response_time': self._percentile(response_times, 99)
            }
        else:
            return {
                'avg_response_time': request_data.response_time,
                'median_response_time': request_data.response_time,
                'min_response_time': request_data.response_time,
                'max_response_time': request_data.response_time,
                'std_response_time': 0,
                'p95_response_time': request_data.response_time,
                'p99_response_time': request_data.response_time
            }
    
    def _analyze_security(self, request_data: RequestData) -> List[SecurityAlert]:
        """安全分析"""
        alerts = []
        
        # SQL注入检测
        sql_injection_alerts = self._detect_sql_injection(request_data)
        alerts.extend(sql_injection_alerts)
        
        # XSS攻击检测
        xss_alerts = self._detect_xss(request_data)
        alerts.extend(xss_alerts)
        
        # 暴力破解检测
        brute_force_alerts = self._detect_brute_force(request_data)
        alerts.extend(brute_force_alerts)
        
        # 异常IP检测
        ip_alerts = self._detect_suspicious_ip(request_data)
        alerts.extend(ip_alerts)
        
        return alerts
    
    def _detect_sql_injection(self, request_data: RequestData) -> List[SecurityAlert]:
        """检测SQL注入"""
        alerts = []
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bSELECT\b.*\bFROM\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bUPDATE\b.*\bSET\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bEXEC\b.*\bXP_\w+)",
            r"(\bOR\b.*\b1\s*=\s*1\b)",
            r"(\bAND\b.*\b1\s*=\s*1\b)",
            r"(\bOR\b.*\bTRUE\b)",
            r"(\bAND\b.*\bTRUE\b)"
        ]
        
        # 检查URL参数
        for param_value in request_data.query_params.values():
            for pattern in sql_patterns:
                if re.search(pattern, param_value, re.IGNORECASE):
                    alerts.append(SecurityAlert(
                        alert_type="SQL_INJECTION",
                        severity="high",
                        description=f"SQL注入攻击检测: {param_value}",
                        request_id=request_data.request_id,
                        client_ip=request_data.client_ip,
                        details={"pattern": pattern, "value": param_value}
                    ))
        
        # 检查请求体
        if request_data.body:
            for pattern in sql_patterns:
                if re.search(pattern, request_data.body, re.IGNORECASE):
                    alerts.append(SecurityAlert(
                        alert_type="SQL_INJECTION",
                        severity="high",
                        description=f"SQL注入攻击检测: {request_data.body[:100]}...",
                        request_id=request_data.request_id,
                        client_ip=request_data.client_ip,
                        details={"pattern": pattern, "value": request_data.body[:100]}
                    ))
        
        return alerts
    
    def _detect_xss(self, request_data: RequestData) -> List[SecurityAlert]:
        """检测XSS攻击"""
        alerts = []
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"eval\s*\(",
            r"alert\s*\(",
            r"confirm\s*\(",
            r"prompt\s*\("
        ]
        
        # 检查URL参数
        for param_value in request_data.query_params.values():
            for pattern in xss_patterns:
                if re.search(pattern, param_value, re.IGNORECASE):
                    alerts.append(SecurityAlert(
                        alert_type="XSS_ATTACK",
                        severity="medium",
                        description=f"XSS攻击检测: {param_value}",
                        request_id=request_data.request_id,
                        client_ip=request_data.client_ip,
                        details={"pattern": pattern, "value": param_value}
                    ))
        
        # 检查请求体
        if request_data.body:
            for pattern in xss_patterns:
                if re.search(pattern, request_data.body, re.IGNORECASE):
                    alerts.append(SecurityAlert(
                        alert_type="XSS_ATTACK",
                        severity="medium",
                        description=f"XSS攻击检测: {request_data.body[:100]}...",
                        request_id=request_data.request_id,
                        client_ip=request_data.client_ip,
                        details={"pattern": pattern, "value": request_data.body[:100]}
                    ))
        
        return alerts
    
    def _detect_brute_force(self, request_data: RequestData) -> List[SecurityAlert]:
        """检测暴力破解"""
        alerts = []
        
        # 检查登录失败的频率
        if request_data.status_code == 401:
            current_time = time.time()
            key = f"login_fail_{request_data.client_ip}"
            
            # 这里应该有更复杂的逻辑来跟踪失败次数
            # 简化实现，实际应该使用数据库或Redis来跟踪
        
        return alerts
    
    def _detect_suspicious_ip(self, request_data: RequestData) -> List[SecurityAlert]:
        """检测可疑IP"""
        alerts = []
        
        try:
            # 检查是否为私有IP
            ip = ipaddress.ip_address(request_data.client_ip)
            if ip.is_private:
                return alerts
            
            # 检查是否为已知恶意IP（这里简化，实际应该使用威胁情报库）
            # 可以集成第三方威胁情报服务
        
        except ValueError:
            # IP地址格式错误
            alerts.append(SecurityAlert(
                alert_type="INVALID_IP",
                severity="low",
                description=f"无效的IP地址: {request_data.client_ip}",
                request_id=request_data.request_id,
                client_ip=request_data.client_ip
            ))
        
        return alerts
    
    def _analyze_behavior(self, request_data: RequestData) -> Dict[str, Any]:
        """行为分析"""
        # 解析URL
        parsed_url = urlparse(request_data.url)
        path = parsed_url.path
        
        # 统计访问路径
        path_key = f"{request_data.client_ip}:{path}"
        self.request_stats[path_key].append(request_data.timestamp)
        
        # 分析访问模式
        recent_requests = self.request_stats[path_key][-10:]  # 最近10次请求
        
        behavior_analysis = {
            'access_frequency': len(recent_requests),
            'access_pattern': 'normal',
            'suspicious_activity': False
        }
        
        # 检测异常访问频率
        if len(recent_requests) > 5:
            time_diffs = [(recent_requests[i] - recent_requests[i-1]).total_seconds() 
                         for i in range(1, len(recent_requests))]
            avg_interval = statistics.mean(time_diffs) if time_diffs else 0
            
            if avg_interval < 1:  # 1秒内多次访问
                behavior_analysis['access_pattern'] = 'high_frequency'
                behavior_analysis['suspicious_activity'] = True
        
        return behavior_analysis
    
    def _update_statistics(self, request_data: RequestData):
        """更新统计信息"""
        # 更新错误统计
        if request_data.status_code >= 400:
            error_key = f"{request_data.status_code}:{request_data.url}"
            self.error_stats[error_key] += 1
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

class StorageManager:
    """存储管理器"""
    
    def __init__(self, config: RequestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        if self.config.storage_type == "file":
            self._init_file_storage()
        elif self.config.storage_type == "database":
            self._init_database_storage()
        elif self.config.storage_type == "redis":
            self._init_redis_storage()
    
    def _init_file_storage(self):
        """初始化文件存储"""
        import os
        os.makedirs(self.config.storage_path, exist_ok=True)
    
    def _init_database_storage(self):
        """初始化数据库存储"""
        self.db_connection = sqlite3.connect(f"{self.config.storage_path}/requests.db")
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                method TEXT,
                url TEXT,
                protocol TEXT,
                headers TEXT,
                body TEXT,
                body_size INTEGER,
                query_params TEXT,
                client_ip TEXT,
                user_agent TEXT,
                status_code INTEGER,
                response_headers TEXT,
                response_body TEXT,
                response_size INTEGER,
                response_time REAL,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                request_id TEXT,
                client_ip TEXT,
                details TEXT
            )
        ''')
        
        self.db_connection.commit()
    
    def _init_redis_storage(self):
        """初始化Redis存储"""
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def store_request(self, request_data: RequestData):
        """存储请求数据"""
        if self.config.storage_type == "file":
            self._store_request_file(request_data)
        elif self.config.storage_type == "database":
            self._store_request_database(request_data)
        elif self.config.storage_type == "redis":
            self._store_request_redis(request_data)
    
    def _store_request_file(self, request_data: RequestData):
        """文件存储请求"""
        filename = f"{self.config.storage_path}/request_{request_data.request_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(request_data), f, ensure_ascii=False, indent=2, default=str)
    
    def _store_request_database(self, request_data: RequestData):
        """数据库存储请求"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_data.request_id,
            request_data.timestamp.isoformat(),
            request_data.method,
            request_data.url,
            request_data.protocol,
            json.dumps(request_data.headers),
            request_data.body,
            request_data.body_size,
            json.dumps(request_data.query_params),
            request_data.client_ip,
            request_data.user_agent,
            request_data.status_code,
            json.dumps(request_data.response_headers),
            request_data.response_body,
            request_data.response_size,
            request_data.response_time,
            request_data.error_message
        ))
        self.db_connection.commit()
    
    def _store_request_redis(self, request_data: RequestData):
        """Redis存储请求"""
        key = f"request:{request_data.request_id}"
        self.redis_client.setex(
            key,
            self.config.retention_days * 86400,
            json.dumps(asdict(request_data), default=str)
        )
    
    def store_alert(self, alert: SecurityAlert):
        """存储安全告警"""
        if self.config.storage_type == "file":
            self._store_alert_file(alert)
        elif self.config.storage_type == "database":
            self._store_alert_database(alert)
        elif self.config.storage_type == "redis":
            self._store_alert_redis(alert)
    
    def _store_alert_file(self, alert: SecurityAlert):
        """文件存储告警"""
        filename = f"{self.config.storage_path}/alert_{alert.alert_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(alert), f, ensure_ascii=False, indent=2, default=str)
    
    def _store_alert_database(self, alert: SecurityAlert):
        """数据库存储告警"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_id,
            alert.timestamp.isoformat(),
            alert.alert_type,
            alert.severity,
            alert.description,
            alert.request_id,
            alert.client_ip,
            json.dumps(alert.details)
        ))
        self.db_connection.commit()
    
    def _store_alert_redis(self, alert: SecurityAlert):
        """Redis存储告警"""
        key = f"alert:{alert.alert_id}"
        self.redis_client.setex(
            key,
            self.config.retention_days * 86400,
            json.dumps(asdict(alert), default=str)
        )

class RequestDebugger:
    """请求调试器主类"""
    
    def __init__(self, config: RequestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.filter = RequestFilter(config)
        self.processor = DataProcessor(config)
        self.storage = StorageManager(config)
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_running = False
        self.captured_requests = deque(maxlen=config.max_records)
        self.security_alerts = deque(maxlen=1000)
        
        # 启动监控
        if config.enable_monitoring:
            self._start_monitoring()
    
    def start(self):
        """启动调试器"""
        self.is_running = True
        self.logger.info("请求调试器启动")
    
    def stop(self):
        """停止调试器"""
        self.is_running = False
        self.executor.shutdown(wait=True)
        self.logger.info("请求调试器停止")
    
    def capture_request(self, request_data: RequestData) -> Optional[Dict[str, Any]]:
        """捕获请求"""
        try:
            # 检查是否应该捕获
            if not self.filter.should_capture(request_data):
                request_data.capture_status = CaptureStatus.FILTERED.value
                return None
            
            # 过滤敏感数据
            request_data = self.filter.filter_sensitive_data(request_data)
            
            # 处理请求数据
            processed_data = self.processor.process_request(request_data)
            
            # 存储数据
            self.storage.store_request(request_data)
            
            # 处理安全告警
            alerts = processed_data.get('security_analysis', [])
            for alert in alerts:
                self.storage.store_alert(alert)
                self.security_alerts.append(alert)
            
            # 添加到内存缓存
            self.captured_requests.append(request_data)
            
            request_data.capture_status = CaptureStatus.COMPLETED.value
            
            self.logger.info(f"请求捕获成功: {request_data.request_id}")
            return processed_data
        
        except Exception as e:
            self.logger.error(f"请求捕获失败: {e}")
            request_data.capture_status = CaptureStatus.FAILED.value
            request_data.error_message = str(e)
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.captured_requests:
            return {}
        
        # 基础统计
        total_requests = len(self.captured_requests)
        error_requests = sum(1 for req in self.captured_requests if req.status_code >= 400)
        error_rate = (error_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # 响应时间统计
        response_times = [req.response_time for req in self.captured_requests if req.response_time > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # 状态码分布
        status_codes = defaultdict(int)
        for req in self.captured_requests:
            status_codes[req.status_code] += 1
        
        # 方法分布
        methods = defaultdict(int)
        for req in self.captured_requests:
            methods[req.method] += 1
        
        # 安全告警统计
        alert_types = defaultdict(int)
        for alert in self.security_alerts:
            alert_types[alert.alert_type] += 1
        
        return {
            'total_requests': total_requests,
            'error_requests': error_requests,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'status_codes': dict(status_codes),
            'methods': dict(methods),
            'security_alerts': {
                'total': len(self.security_alerts),
                'by_type': dict(alert_types)
            }
        }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的请求"""
        recent_requests = list(self.captured_requests)[-limit:]
        return [asdict(req) for req in recent_requests]
    
    def get_security_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取安全告警"""
        recent_alerts = list(self.security_alerts)[-limit:]
        return [asdict(alert) for alert in recent_alerts]
    
    def _start_monitoring(self):
        """启动监控"""
        def monitor_loop():
            while self.is_running:
                try:
                    # 检查告警阈值
                    stats = self.get_statistics()
                    self._check_alert_thresholds(stats)
                    
                    # 清理过期数据
                    self._cleanup_expired_data()
                    
                    time.sleep(self.config.monitoring_interval)
                
                except Exception as e:
                    self.logger.error(f"监控循环异常: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _check_alert_thresholds(self, stats: Dict[str, Any]):
        """检查告警阈值"""
        # 检查响应时间阈值
        if stats.get('avg_response_time', 0) > self.config.alert_thresholds.get('response_time', 5000):
            self.logger.warning(f"响应时间超过阈值: {stats['avg_response_time']}ms")
        
        # 检查错误率阈值
        if stats.get('error_rate', 0) > self.config.alert_thresholds.get('error_rate', 5.0):
            self.logger.warning(f"错误率超过阈值: {stats['error_rate']}%")
        
        # 检查安全告警
        if stats.get('security_alerts', {}).get('total', 0) > 10:
            self.logger.warning(f"安全告警数量过多: {stats['security_alerts']['total']}")
    
    def _cleanup_expired_data(self):
        """清理过期数据"""
        # 这里应该实现数据清理逻辑
        # 简化实现，实际应该根据配置的保留策略进行清理
        pass

# 全局调试器实例
request_debugger = None

def init_request_debugger(config: RequestConfig):
    """初始化请求调试器"""
    global request_debugger
    request_debugger = RequestDebugger(config)
    request_debugger.start()

def get_request_debugger() -> RequestDebugger:
    """获取请求调试器"""
    return request_debugger

# 使用示例
# 配置请求调试器
config = RequestConfig(
    debug_name="api-debugger",
    debug_type="http",
    debug_mode="real-time",
    capture_protocols=["http", "https"],
    capture_methods=["GET", "POST", "PUT", "DELETE"],
    capture_headers=True,
    capture_body=True,
    capture_response=True,
    max_body_size=1024 * 1024,  # 1MB
    url_filters=["/api/*"],
    exclude_filters=["/health", "/metrics"],
    static_resource_filters=[".css", ".js", ".png", ".jpg", ".gif"],
    storage_type="file",
    storage_path="./debug_data",
    max_records=10000,
    retention_days=7,
    sensitive_fields=["password", "token", "jwt", "session"],
    mask_sensitive_data=True,
    enable_monitoring=True,
    monitoring_interval=60,
    alert_thresholds={
        "response_time": 5000,
        "error_rate": 5.0,
        "request_rate": 1000
    },
    enable_ai_analysis=False,
    enable_ml_detection=False,
    enable_distribution=False
)

# 初始化调试器
init_request_debugger(config)
debugger = get_request_debugger()

# 模拟请求数据
sample_requests = [
    RequestData(
        method="GET",
        url="https://api.example.com/users/123",
        protocol="https",
        headers={"Authorization": "Bearer token123", "Content-Type": "application/json"},
        body="",
        query_params={"include": "profile"},
        client_ip="192.168.1.100",
        user_agent="Mozilla/5.0",
        status_code=200,
        response_headers={"Content-Type": "application/json"},
        response_body='{"id": 123, "name": "John Doe"}',
        response_size=50,
        response_time=150.5
    ),
    RequestData(
        method="POST",
        url="https://api.example.com/login",
        protocol="https",
        headers={"Content-Type": "application/json"},
        body='{"username": "admin", "password": "secret123"}',
        query_params={},
        client_ip="192.168.1.101",
        user_agent="Mozilla/5.0",
        status_code=401,
        response_headers={"Content-Type": "application/json"},
        response_body='{"error": "Invalid credentials"}',
        response_size=35,
        response_time=200.3
    ),
    RequestData(
        method="GET",
        url="https://api.example.com/search?q=<script>alert('xss')</script>",
        protocol="https",
        headers={"Content-Type": "application/json"},
        body="",
        query_params={"q": "<script>alert('xss')</script>"},
        client_ip="192.168.1.102",
        user_agent="Mozilla/5.0",
        status_code=400,
        response_headers={"Content-Type": "application/json"},
        response_body='{"error": "Invalid query"}',
        response_size=30,
        response_time=100.2
    )
]

# 捕获请求
for request in sample_requests:
    result = debugger.capture_request(request)
    if result:
        print(f"请求处理完成: {request.request_id}")
        print(f"安全告警数量: {len(result.get('security_analysis', []))}")

# 获取统计信息
stats = debugger.get_statistics()
print(f"\n统计信息:")
print(f"总请求数: {stats.get('total_requests', 0)}")
print(f"错误率: {stats.get('error_rate', 0):.2f}%")
print(f"平均响应时间: {stats.get('avg_response_time', 0):.2f}ms")

# 获取安全告警
alerts = debugger.get_security_alerts(limit=10)
print(f"\n安全告警:")
for alert in alerts:
    print(f"- {alert.alert_type}: {alert.description}")

# 获取最近请求
recent_requests = debugger.get_recent_requests(limit=5)
print(f"\n最近请求:")
for req in recent_requests:
    print(f"- {req['method']} {req['url']} ({req['status_code']})")

# 停止调试器
time.sleep(2)
debugger.stop()
```

## 参考资源

### 网络调试工具
- [Wireshark网络分析器](https://www.wireshark.org/)
- [Fiddler HTTP调试器](https://www.telerik.com/fiddler)
- [Charles代理调试器](https://www.charlesproxy.com/)
- [Burp Suite安全测试](https://portswigger.net/burp)

### Python网络库
- [Requests库](https://docs.python-requests.org/)
- [httpx异步HTTP客户端](https://www.python-httpx.org/)
- [aiohttp异步Web框架](https://docs.aiohttp.org/)
- [mitmproxy代理工具](https://mitmproxy.org/)

### 安全检测
- [OWASP安全指南](https://owasp.org/)
- [SQL注入检测](https://owasp.org/www-community/attacks/SQL_Injection)
- [XSS攻击防护](https://owasp.org/www-community/attacks/xss/)
- [安全编码实践](https://cheatsheetseries.owasp.org/)

### 性能监控
- [APM工具对比](https://newrelic.com/solutions/apm)
- [性能测试工具](https://loadtestingtool.org/)
- [监控最佳实践](https://prometheus.io/docs/practices/)
- [数据库性能优化](https://www.postgresql.org/docs/current/performance-tips.html)
