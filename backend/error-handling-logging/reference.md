# 错误处理和日志参考文档

## 错误处理和日志概述

### 什么是错误处理和日志
错误处理和日志是一种系统性的错误管理和信息记录技术，通过捕获、处理、记录和分析系统运行中的异常情况，确保系统的稳定性、可维护性和可观测性。该技能涵盖了异常捕获处理、多级日志记录、错误监控告警、性能分析、安全防护等功能，帮助开发者构建健壮、可靠、可监控的应用系统。

### 主要功能
- **异常处理机制**: 提供全局异常捕获、分类处理、自动恢复和降级策略
- **多级日志系统**: 支持DEBUG、INFO、WARNING、ERROR、CRITICAL等多级别日志记录
- **实时监控告警**: 包含错误统计、性能监控、日志分析和智能告警
- **安全防护**: 提供敏感信息脱敏、数据加密、访问控制等安全功能
- **性能优化**: 支持并发处理、缓存策略、资源管理等性能优化技术

## 错误处理引擎核心

### 异常处理管理器
```python
# error_handling.py
import logging
import traceback
import threading
import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

class ErrorLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    BUSINESS = "business"
    SECURITY = "security"
    CUSTOM = "custom"

class RetryStrategy(Enum):
    FIXED = "fixed"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CUSTOM = "custom"

@dataclass
class ErrorInfo:
    error_id: str
    error_type: Type[Exception]
    error_message: str
    error_level: ErrorLevel
    error_category: ErrorCategory
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    module_name: str = ""
    function_name: str = ""

@dataclass
class RetryConfig:
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0
    max_delay: float = 60.0
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=list)

@dataclass
class FallbackConfig:
    enabled: bool = False
    fallback_function: Optional[Callable] = None
    fallback_data: Any = None
    fallback_timeout: float = 30.0

@dataclass
class ErrorHandlingConfig:
    # 基础配置
    enable_global_handler: bool = True
    enable_error_recovery: bool = True
    enable_retry: bool = True
    enable_fallback: bool = False
    
    # 重试配置
    default_retry_config: RetryConfig = field(default_factory=RetryConfig)
    
    # 降级配置
    default_fallback_config: FallbackConfig = field(default_factory=FallbackConfig)
    
    # 监控配置
    enable_monitoring: bool = True
    monitoring_interval: float = 60.0
    error_threshold: int = 10
    error_rate_threshold: float = 0.1
    
    # 通知配置
    enable_notifications: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email"])
    
    # 性能配置
    max_workers: int = 4
    queue_size: int = 1000
    timeout: float = 30.0

class ErrorHandlingManager:
    """错误处理管理器"""
    
    def __init__(self, config: ErrorHandlingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._error_handlers: Dict[Type[Exception], Callable] = {}
        self._error_stats: Dict[str, int] = {}
        self._error_queue = queue.Queue(maxsize=config.queue_size)
        self._executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self._running = False
        self._lock = threading.RLock()
        
        # 初始化组件
        self._init_global_handler()
        self._init_monitoring()
    
    def _init_global_handler(self):
        """初始化全局异常处理器"""
        if self.config.enable_global_handler:
            # 设置全局异常处理器
            def handle_exception(exc_type, exc_value, exc_traceback):
                error_info = self._create_error_info(
                    exc_value, ErrorLevel.CRITICAL, ErrorCategory.SYSTEM
                )
                self._process_error(error_info)
            
            # 设置系统异常处理器
            import sys
            sys.excepthook = handle_exception
    
    def _init_monitoring(self):
        """初始化监控"""
        if self.config.enable_monitoring:
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
    
    def register_handler(self, exception_type: Type[Exception], handler: Callable):
        """注册异常处理器"""
        self._error_handlers[exception_type] = handler
        self.logger.info(f"注册异常处理器: {exception_type.__name__}")
    
    def handle_exception(self, exception: Exception, 
                        level: ErrorLevel = ErrorLevel.ERROR,
                        category: ErrorCategory = ErrorCategory.CUSTOM,
                        context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """处理异常"""
        error_info = self._create_error_info(exception, level, category, context)
        self._process_error(error_info)
        return error_info
    
    def _create_error_info(self, exception: Exception, 
                          level: ErrorLevel,
                          category: ErrorCategory,
                          context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """创建错误信息"""
        error_id = self._generate_error_id()
        stack_trace = traceback.format_exc()
        
        # 获取调用上下文
        frame = traceback.extract_stack()[-2]
        module_name = frame.filename
        function_name = frame.name
        
        return ErrorInfo(
            error_id=error_id,
            error_type=type(exception),
            error_message=str(exception),
            error_level=level,
            error_category=category,
            stack_trace=stack_trace,
            context=context or {},
            module_name=module_name,
            function_name=function_name
        )
    
    def _generate_error_id(self) -> str:
        """生成错误ID"""
        timestamp = str(int(time.time() * 1000))
        random_str = str(hash(time.time()))[-8:]
        return f"err_{timestamp}_{random_str}"
    
    def _process_error(self, error_info: ErrorInfo):
        """处理错误"""
        try:
            # 更新统计
            self._update_error_stats(error_info)
            
            # 记录日志
            self._log_error(error_info)
            
            # 发送通知
            if self.config.enable_notifications:
                self._send_notification(error_info)
            
            # 添加到处理队列
            self._error_queue.put(error_info)
        
        except Exception as e:
            self.logger.error(f"处理错误时发生异常: {e}")
    
    def _update_error_stats(self, error_info: ErrorInfo):
        """更新错误统计"""
        with self._lock:
            error_key = f"{error_info.error_type.__name__}:{error_info.error_level.value}"
            self._error_stats[error_key] = self._error_stats.get(error_key, 0) + 1
    
    def _log_error(self, error_info: ErrorInfo):
        """记录错误日志"""
        log_message = f"[{error_info.error_id}] {error_info.error_type.__name__}: {error_info.error_message}"
        
        if error_info.context:
            log_message += f" | Context: {json.dumps(error_info.context, default=str)}"
        
        if error_info.stack_trace:
            log_message += f"\nStack Trace:\n{error_info.stack_trace}"
        
        # 根据错误级别记录日志
        if error_info.error_level == ErrorLevel.DEBUG:
            self.logger.debug(log_message)
        elif error_info.error_level == ErrorLevel.INFO:
            self.logger.info(log_message)
        elif error_info.error_level == ErrorLevel.WARNING:
            self.logger.warning(log_message)
        elif error_info.error_level == ErrorLevel.ERROR:
            self.logger.error(log_message)
        elif error_info.error_level == ErrorLevel.CRITICAL:
            self.logger.critical(log_message)
    
    def _send_notification(self, error_info: ErrorInfo):
        """发送错误通知"""
        if error_info.error_level in [ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
            # 异步发送通知
            self._executor.submit(self._do_send_notification, error_info)
    
    def _do_send_notification(self, error_info: ErrorInfo):
        """执行通知发送"""
        try:
            for channel in self.config.notification_channels:
                if channel == "email":
                    self._send_email_notification(error_info)
                elif channel == "webhook":
                    self._send_webhook_notification(error_info)
                elif channel == "slack":
                    self._send_slack_notification(error_info)
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")
    
    def _send_email_notification(self, error_info: ErrorInfo):
        """发送邮件通知"""
        # 这里需要配置邮件服务器信息
        # 示例实现，实际使用时需要配置SMTP服务器
        try:
            msg = MIMEMultipart()
            msg['From'] = "error-monitor@example.com"
            msg['To'] = "admin@example.com"
            msg['Subject'] = f"系统错误通知: {error_info.error_type.__name__}"
            
            body = f"""
            错误ID: {error_info.error_id}
            错误类型: {error_info.error_type.__name__}
            错误级别: {error_info.error_level.value}
            错误消息: {error_info.error_message}
            发生时间: {error_info.timestamp}
            模块: {error_info.module_name}
            函数: {error_info.function_name}
            
            上下文信息:
            {json.dumps(error_info.context, default=str, indent=2)}
            
            堆栈跟踪:
            {error_info.stack_trace}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # 实际发送邮件的代码需要根据SMTP配置
            self.logger.info(f"邮件通知已发送: {error_info.error_id}")
        
        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {e}")
    
    def _send_webhook_notification(self, error_info: ErrorInfo):
        """发送Webhook通知"""
        try:
            webhook_url = "https://your-webhook-url.com/error"
            payload = {
                "error_id": error_info.error_id,
                "error_type": error_info.error_type.__name__,
                "error_level": error_info.error_level.value,
                "error_message": error_info.error_message,
                "timestamp": error_info.timestamp.isoformat(),
                "module_name": error_info.module_name,
                "function_name": error_info.function_name,
                "context": error_info.context
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"Webhook通知已发送: {error_info.error_id}")
            else:
                self.logger.error(f"Webhook通知发送失败: {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"发送Webhook通知失败: {e}")
    
    def _send_slack_notification(self, error_info: ErrorInfo):
        """发送Slack通知"""
        try:
            webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            payload = {
                "text": f"🚨 系统错误通知",
                "attachments": [
                    {
                        "color": "danger" if error_info.error_level == ErrorLevel.CRITICAL else "warning",
                        "fields": [
                            {"title": "错误ID", "value": error_info.error_id, "short": True},
                            {"title": "错误类型", "value": error_info.error_type.__name__, "short": True},
                            {"title": "错误级别", "value": error_info.error_level.value, "short": True},
                            {"title": "模块", "value": error_info.module_name, "short": True},
                            {"title": "函数", "value": error_info.function_name, "short": True},
                            {"title": "错误消息", "value": error_info.error_message, "short": False}
                        ],
                        "ts": int(error_info.timestamp.timestamp())
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"Slack通知已发送: {error_info.error_id}")
            else:
                self.logger.error(f"Slack通知发送失败: {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"发送Slack通知失败: {e}")
    
    def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                self._check_error_thresholds()
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
    
    def _check_error_thresholds(self):
        """检查错误阈值"""
        with self._lock:
            total_errors = sum(self._error_stats.values())
            
            # 检查错误数量阈值
            if total_errors > self.config.error_threshold:
                self.logger.warning(f"错误数量超过阈值: {total_errors} > {self.config.error_threshold}")
            
            # 检查错误率阈值
            if hasattr(self, '_total_requests'):
                error_rate = total_errors / self._total_requests if self._total_requests > 0 else 0
                if error_rate > self.config.error_rate_threshold:
                    self.logger.warning(f"错误率超过阈值: {error_rate:.2%} > {self.config.error_rate_threshold:.2%}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        with self._lock:
            return {
                "error_stats": self._error_stats.copy(),
                "total_errors": sum(self._error_stats.values()),
                "error_types": list(self._error_stats.keys()),
                "queue_size": self._error_queue.qsize()
            }
    
    def clear_error_stats(self):
        """清空错误统计"""
        with self._lock:
            self._error_stats.clear()
            self.logger.info("错误统计已清空")

# 重试装饰器
def retry_on_exception(retry_config: Optional[RetryConfig] = None):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = retry_config or RetryConfig()
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 检查是否需要重试
                    if (config.retry_on_exceptions and 
                        not any(isinstance(e, exc_type) for exc_type in config.retry_on_exceptions)):
                        raise e
                    
                    if attempt < config.max_retries:
                        # 计算延迟时间
                        if config.retry_strategy == RetryStrategy.FIXED:
                            delay = config.retry_delay
                        elif config.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                            delay = min(config.retry_delay * (config.backoff_multiplier ** attempt), 
                                      config.max_delay)
                        elif config.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
                            delay = min(config.retry_delay * (attempt + 1), config.max_delay)
                        else:
                            delay = config.retry_delay
                        
                        error_handler.handle_exception(
                            e, ErrorLevel.WARNING, ErrorCategory.SYSTEM,
                            {"attempt": attempt + 1, "delay": delay, "function": func.__name__}
                        )
                        
                        time.sleep(delay)
                    else:
                        # 最后一次尝试失败，抛出异常
                        error_handler.handle_exception(
                            e, ErrorLevel.ERROR, ErrorCategory.SYSTEM,
                            {"attempts": attempt + 1, "function": func.__name__}
                        )
                        raise e
            
            # 这里不应该到达，但为了类型安全
            raise last_exception
        
        return wrapper
    return decorator

# 降级装饰器
def fallback_on_exception(fallback_config: Optional[FallbackConfig] = None):
    """降级装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = fallback_config or FallbackConfig()
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_exception(
                    e, ErrorLevel.WARNING, ErrorCategory.SYSTEM,
                    {"function": func.__name__, "fallback_enabled": config.enabled}
                )
                
                if config.enabled:
                    if config.fallback_function:
                        return config.fallback_function(*args, **kwargs)
                    elif config.fallback_data is not None:
                        return config.fallback_data
                    else:
                        return None
                else:
                    raise e
        
        return wrapper
    return decorator

# 异常处理装饰器
def handle_exception(level: ErrorLevel = ErrorLevel.ERROR,
                    category: ErrorCategory = ErrorCategory.CUSTOM,
                    reraise: bool = True):
    """异常处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_exception(e, level, category, {"function": func.__name__})
                if reraise:
                    raise e
                return None
        
        return wrapper
    return decorator

# 全局错误处理器实例
error_handler = None

def init_error_handling(config: ErrorHandlingConfig):
    """初始化错误处理器"""
    global error_handler
    error_handler = ErrorHandlingManager(config)

def get_error_handler() -> ErrorHandlingManager:
    """获取错误处理器"""
    return error_handler

# 使用示例
# 配置错误处理
config = ErrorHandlingConfig(
    enable_global_handler=True,
    enable_error_recovery=True,
    enable_retry=True,
    enable_fallback=True,
    default_retry_config=RetryConfig(
        max_retries=3,
        retry_delay=1.0,
        retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        backoff_multiplier=2.0,
        max_delay=60.0
    ),
    default_fallback_config=FallbackConfig(
        enabled=True,
        fallback_data={"status": "error", "message": "服务暂时不可用"}
    ),
    enable_monitoring=True,
    monitoring_interval=60.0,
    error_threshold=10,
    error_rate_threshold=0.1,
    enable_notifications=True,
    notification_channels=["email", "webhook"],
    max_workers=4,
    queue_size=1000,
    timeout=30.0
)

# 初始化错误处理器
init_error_handling(config)

# 定义测试函数
@retry_on_exception(RetryConfig(max_retries=3, retry_delay=1.0))
@handle_exception(ErrorLevel.ERROR, ErrorCategory.SYSTEM)
def unreliable_function(should_fail=False):
    """不可靠的函数"""
    import random
    if should_fail or random.random() < 0.3:  # 30%失败率
        raise ValueError("函数执行失败")
    return "操作成功"

@fallback_on_exception(FallbackConfig(
    enabled=True,
    fallback_data={"status": "fallback", "message": "降级响应"}
))
@handle_exception(ErrorLevel.WARNING, ErrorCategory.SYSTEM, reraise=False)
def api_call_function():
    """API调用函数"""
    # 模拟API调用失败
    raise ConnectionError("API连接失败")

# 测试错误处理
print("测试重试机制:")
try:
    result = unreliable_function(should_fail=True)
    print(f"结果: {result}")
except Exception as e:
    print(f"最终失败: {e}")

print("\n测试降级机制:")
result = api_call_function()
print(f"降级结果: {result}")

print("\n测试正常执行:")
result = unreliable_function(should_fail=False)
print(f"正常结果: {result}")

# 获取错误统计
stats = error_handler.get_error_stats()
print(f"\n错误统计: {stats}")

# 等待一段时间让监控线程运行
time.sleep(5)
```

## 日志系统核心

### 日志管理器
```python
# logging_system.py
import logging
import logging.handlers
import json
import threading
import time
import gzip
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class LogFormat(Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    STRUCTURED = "structured"
    JSON = "json"

class RotationType(Enum):
    SIZE = "size"
    TIME = "time"
    COUNT = "count"

@dataclass
class LogConfig:
    # 基础配置
    logger_name: str = "app"
    level: LogLevel = LogLevel.INFO
    format_type: LogFormat = LogFormat.DETAILED
    
    # 控制台配置
    console_enabled: bool = True
    console_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_colorized: bool = True
    
    # 文件配置
    file_enabled: bool = True
    file_path: str = "logs/app.log"
    file_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    file_encoding: str = "utf-8"
    
    # 轮转配置
    rotation_enabled: bool = True
    rotation_type: RotationType = RotationType.SIZE
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    when: str = "midnight"
    interval: int = 1
    
    # 网络配置
    network_enabled: bool = False
    network_host: str = "localhost"
    network_port: int = 514
    network_protocol: str = "UDP"
    
    # 过滤配置
    filters: List[str] = field(default_factory=list)
    sensitive_fields: List[str] = field(default_factory=lambda: ["password", "token", "secret"])
    
    # 性能配置
    async_logging: bool = False
    queue_size: int = 1000
    buffer_size: int = 8192

class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器"""
    
    def __init__(self, sensitive_fields: List[str]):
        super().__init__()
        self.sensitive_fields = sensitive_fields
    
    def filter(self, record):
        """过滤敏感数据"""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._mask_sensitive_data(record.msg)
        
        if hasattr(record, 'args') and record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    new_args.append(self._mask_sensitive_data(arg))
                elif isinstance(arg, dict):
                    new_args.append(self._mask_dict_sensitive_data(arg))
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)
        
        return True
    
    def _mask_sensitive_data(self, text: str) -> str:
        """屏蔽敏感数据"""
        import re
        
        for field in self.sensitive_fields:
            # 匹配 field=value 格式
            pattern = rf'({field}\s*[:=]\s*)([^\s,;]+)'
            text = re.sub(pattern, lambda m: f"{m.group(1)}{'*' * len(m.group(2))}", text, flags=re.IGNORECASE)
            
            # 匹配 JSON 格式
            pattern = rf'("{field}"\s*:\s*")([^"]*)(")'
            text = re.sub(pattern, lambda m: f"{m.group(1)}{'*' * len(m.group(2))}{m.group(3)}", text, flags=re.IGNORECASE)
        
        return text
    
    def _mask_dict_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """屏蔽字典中的敏感数据"""
        masked_data = data.copy()
        
        for field in self.sensitive_fields:
            if field in masked_data:
                if isinstance(masked_data[field], str):
                    masked_data[field] = '*' * len(masked_data[field])
                else:
                    masked_data[field] = '***'
        
        return masked_data

class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def __init__(self, format_type: LogFormat = LogFormat.STRUCTURED):
        super().__init__()
        self.format_type = format_type
    
    def format(self, record):
        """格式化日志记录"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName',
                          'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_data[key] = value
        
        if self.format_type == LogFormat.JSON:
            return json.dumps(log_data, ensure_ascii=False, default=str)
        else:
            return self._format_structured(log_data)
    
    def _format_structured(self, log_data: Dict[str, Any]) -> str:
        """格式化结构化数据"""
        parts = []
        
        # 基础信息
        parts.append(f"[{log_data['timestamp']}]")
        parts.append(f"[{log_data['level']}]")
        parts.append(f"[{log_data['logger']}]")
        
        # 位置信息
        parts.append(f"{log_data['module']}:{log_data['function']}:{log_data['line']}")
        
        # 消息
        parts.append(f"- {log_data['message']}")
        
        # 额外信息
        extra_fields = {k: v for k, v in log_data.items() 
                       if k not in ['timestamp', 'level', 'logger', 'module', 'function', 'line', 'message']}
        if extra_fields:
            parts.append(f"| {json.dumps(extra_fields, ensure_ascii=False, default=str)}")
        
        return " ".join(parts)

class AsyncLogHandler(logging.Handler):
    """异步日志处理器"""
    
    def __init__(self, handler: logging.Handler, queue_size: int = 1000):
        super().__init__()
        self.handler = handler
        self.queue = queue.Queue(maxsize=queue_size)
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
    
    def emit(self, record):
        """发送日志记录"""
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            # 队列满时丢弃日志
            pass
    
    def _worker(self):
        """工作线程"""
        while True:
            try:
                record = self.queue.get(timeout=1)
                if record is None:  # 停止信号
                    break
                self.handler.emit(record)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"异步日志处理器错误: {e}")
    
    def close(self):
        """关闭处理器"""
        self.queue.put(None)  # 发送停止信号
        self.thread.join()
        self.handler.close()

class LoggingManager:
    """日志管理器"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.logger = logging.getLogger(config.logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志器"""
        # 设置日志级别
        self.logger.setLevel(self.config.level.value)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 添加处理器
        if self.config.console_enabled:
            self._add_console_handler()
        
        if self.config.file_enabled:
            self._add_file_handler()
        
        if self.config.network_enabled:
            self._add_network_handler()
        
        # 添加过滤器
        if self.config.sensitive_fields:
            sensitive_filter = SensitiveDataFilter(self.config.sensitive_fields)
            self.logger.addFilter(sensitive_filter)
    
    def _add_console_handler(self):
        """添加控制台处理器"""
        handler = logging.StreamHandler()
        
        # 设置格式化器
        if self.config.console_colorized:
            try:
                import colorlog
                formatter = colorlog.ColoredFormatter(
                    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt='%H:%M:%S',
                    log_colors={
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                )
            except ImportError:
                formatter = logging.Formatter(self.config.console_format)
        else:
            formatter = logging.Formatter(self.config.console_format)
        
        handler.setFormatter(formatter)
        
        if self.config.async_logging:
            handler = AsyncLogHandler(handler, self.config.queue_size)
        
        self.logger.addHandler(handler)
    
    def _add_file_handler(self):
        """添加文件处理器"""
        # 确保日志目录存在
        log_dir = os.path.dirname(self.config.file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建处理器
        if self.config.rotation_enabled:
            if self.config.rotation_type == RotationType.SIZE:
                handler = logging.handlers.RotatingFileHandler(
                    self.config.file_path,
                    maxBytes=self.config.max_bytes,
                    backupCount=self.config.backup_count,
                    encoding=self.config.file_encoding
                )
            elif self.config.rotation_type == RotationType.TIME:
                handler = logging.handlers.TimedRotatingFileHandler(
                    self.config.file_path,
                    when=self.config.when,
                    interval=self.config.interval,
                    backupCount=self.config.backup_count,
                    encoding=self.config.file_encoding
                )
            else:
                handler = logging.FileHandler(
                    self.config.file_path,
                    encoding=self.config.file_encoding
                )
        else:
            handler = logging.FileHandler(
                self.config.file_path,
                encoding=self.config.file_encoding
            )
        
        # 设置格式化器
        if self.config.format_type == LogFormat.JSON:
            formatter = StructuredFormatter(LogFormat.JSON)
        elif self.config.format_type == LogFormat.STRUCTURED:
            formatter = StructuredFormatter(LogFormat.STRUCTURED)
        else:
            formatter = logging.Formatter(self.config.file_format)
        
        handler.setFormatter(formatter)
        
        if self.config.async_logging:
            handler = AsyncLogHandler(handler, self.config.queue_size)
        
        self.logger.addHandler(handler)
    
    def _add_network_handler(self):
        """添加网络处理器"""
        if self.config.network_protocol.upper() == "UDP":
            handler = logging.handlers.DatagramHandler(
                self.config.network_host,
                self.config.network_port
            )
        else:
            handler = logging.handlers.SocketHandler(
                self.config.network_host,
                self.config.network_port
            )
        
        # 设置格式化器
        formatter = StructuredFormatter(LogFormat.JSON)
        handler.setFormatter(formatter)
        
        if self.config.async_logging:
            handler = AsyncLogHandler(handler, self.config.queue_size)
        
        self.logger.addHandler(handler)
    
    def get_logger(self) -> logging.Logger:
        """获取日志器"""
        return self.logger
    
    def set_level(self, level: LogLevel):
        """设置日志级别"""
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
    
    def add_custom_handler(self, handler: logging.Handler):
        """添加自定义处理器"""
        self.logger.addHandler(handler)
    
    def remove_handler(self, handler: logging.Handler):
        """移除处理器"""
        self.logger.removeHandler(handler)

# 日志装饰器
def log_function_call(level: LogLevel = LogLevel.INFO,
                    include_args: bool = True,
                    include_result: bool = True):
    """函数调用日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            
            # 记录函数调用
            if include_args:
                logger.log(level.value, f"调用函数 {func.__name__} - 参数: args={args}, kwargs={kwargs}")
            else:
                logger.log(level.value, f"调用函数 {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # 记录函数返回
                if include_result:
                    logger.log(level.value, f"函数 {func.__name__} 执行成功 - 返回值: {result}")
                else:
                    logger.log(level.value, f"函数 {func.__name__} 执行成功")
                
                return result
            
            except Exception as e:
                logger.error(f"函数 {func.__name__} 执行失败 - 异常: {e}")
                raise
        
        return wrapper
    return decorator

def log_performance(level: LogLevel = LogLevel.INFO):
    """性能日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.log(level.value, f"函数 {func.__name__} 执行时间: {execution_time:.3f}秒")
                return result
            
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"函数 {func.__name__} 执行失败 - 执行时间: {execution_time:.3f}秒, 异常: {e}")
                raise
        
        return wrapper
    return decorator

# 全局日志管理器
logging_manager = None

def init_logging(config: LogConfig):
    """初始化日志系统"""
    global logging_manager
    logging_manager = LoggingManager(config)

def get_logger(name: str = None) -> logging.Logger:
    """获取日志器"""
    if logging_manager:
        return logging_manager.get_logger() if name is None else logging.getLogger(name)
    else:
        return logging.getLogger(name)

# 使用示例
# 配置日志
log_config = LogConfig(
    logger_name="my_app",
    level=LogLevel.INFO,
    format_type=LogFormat.STRUCTURED,
    console_enabled=True,
    console_colorized=True,
    file_enabled=True,
    file_path="logs/app.log",
    rotation_enabled=True,
    rotation_type=RotationType.SIZE,
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    network_enabled=False,
    sensitive_fields=["password", "token", "secret", "api_key"],
    async_logging=True,
    queue_size=1000
)

# 初始化日志系统
init_logging(log_config)

# 获取日志器
logger = get_logger()

# 测试日志记录
logger.debug("这是一条调试信息")
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
logger.critical("这是一条严重错误日志")

# 测试敏感数据过滤
logger.info(f"用户登录 - username=admin, password=secret123, token=abc123def456")

# 测试结构化日志
logger.info("用户操作", extra={
    "user_id": "12345",
    "action": "login",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0"
})

# 使用装饰器
@log_function_call(LogLevel.INFO, include_args=True, include_result=True)
@log_performance(LogLevel.INFO)
def calculate_fibonacci(n: int) -> int:
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# 测试装饰器
result = calculate_fibonacci(10)
print(f"斐波那契数列第10项: {result}")

# 等待异步日志处理完成
time.sleep(2)
```

## 参考资源

### 错误处理技术
- [Python异常处理](https://docs.python.org/3/tutorial/errors.html)
- [异常处理最佳实践](https://docs.python.org/3/howto/logging.html#logging-advanced-tutorial)
- [错误恢复模式](https://martinfowler.com/articles/patterns-of-distributed-systems/)
- [重试模式](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)

### 日志技术
- [Python logging模块](https://docs.python.org/3/library/logging.html)
- [结构化日志](https://www.structlog.org/)
- [ELK日志栈](https://www.elastic.co/guide/)
- [Fluentd日志收集](https://www.fluentd.org/)

### 监控告警
- [Prometheus监控](https://prometheus.io/docs/)
- [Grafana可视化](https://grafana.com/docs/)
- [Alertmanager告警](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PagerDuty告警管理](https://www.pagerduty.com/docs/)

### 安全防护
- [OWASP安全日志](https://owasp.org/www-project-cheat-sheets/cheatsheets/Logging_Cheat_Sheet.html)
- [数据脱敏技术](https://en.wikipedia.org/wiki/Data_masking)
- [日志安全最佳实践](https://tools.ietf.org/html/rfc3195)
- [审计日志标准](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-92.pdf)
