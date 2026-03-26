# 熔断器参考文档

## 熔断器概述

### 什么是熔断器
熔断器是一种微服务架构中的关键保护机制，用于防止级联故障和提供系统弹性。当某个服务出现故障或响应超时时，熔断器会自动"熔断"该服务的调用，直接返回预设的降级响应，避免整个系统因单个服务故障而崩溃。熔断器通过监控服务调用的健康状况，实现了故障的快速检测、隔离和恢复，是构建高可用微服务系统的重要组件。

### 核心功能
- **故障检测**: 监控服务调用的成功率和响应时间，及时发现服务异常
- **自动熔断**: 当故障指标超过阈值时，自动切断对故障服务的调用
- **降级处理**: 提供预设的降级响应，保证系统基本功能可用
- **自动恢复**: 在服务恢复正常后，自动重新开放服务调用
- **状态管理**: 维护熔断器的三种状态（关闭、打开、半开）和状态转换
- **监控告警**: 提供详细的监控指标和告警机制

## 熔断器核心实现

### 熔断器状态机
```python
# circuit_breaker.py
import json
import time
import uuid
import logging
import threading
import queue
import hashlib
import datetime
import re
import statistics
import math
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import redis
import json
import yaml

class CircuitState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"      # 关闭状态 - 正常状态
    OPEN = "open"          # 打开状态 - 熔断状态
    HALF_OPEN = "half_open"  # 半开状态 - 测试状态

class FailureType(Enum):
    """失败类型枚举"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    CONNECTION_ERROR = "connection_error"
    BUSINESS_ERROR = "business_error"
    CUSTOM = "custom"

class AlertLevel(Enum):
    """告警级别枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class FailureRecord:
    """失败记录"""
    timestamp: datetime
    failure_type: FailureType
    error_message: str
    duration: float
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitMetrics:
    """熔断器指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0
    timeout_requests: int = 0
    average_response_time: float = 0.0
    failure_rate: float = 0.0
    last_failure_time: Optional[datetime] = None
    state_change_count: int = 0
    current_state: CircuitState = CircuitState.CLOSED

@dataclass
class CircuitConfig:
    """熔断器配置"""
    # 基础配置
    name: str
    service_name: str
    timeout: float = 5.0
    
    # 失败率熔断配置
    failure_rate_threshold: float = 0.5  # 50%
    failure_rate_min_requests: int = 10
    failure_rate_window: float = 60.0  # 60秒
    
    # 响应时间熔断配置
    response_time_threshold: float = 2.0  # 2秒
    response_time_percentile: float = 95.0  # P95
    
    # 熔断恢复配置
    recovery_timeout: float = 30.0  # 30秒
    half_open_max_calls: int = 5
    half_open_success_threshold: float = 0.5  # 50%
    
    # 异常熔断配置
    exception_types: List[str] = field(default_factory=list)
    custom_failure_conditions: List[Callable] = field(default_factory=list)
    
    # 降级配置
    fallback_enabled: bool = True
    fallback_response: Any = None
    fallback_function: Optional[Callable] = None
    
    # 监控配置
    metrics_enabled: bool = True
    logging_enabled: bool = True
    alerting_enabled: bool = True

class CircuitBreaker:
    """熔断器核心实现"""
    
    def __init__(self, config: CircuitConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics = CircuitMetrics()
        self.state = CircuitState.CLOSED
        self.lock = threading.RLock()
        self.failure_records = deque(maxlen=1000)
        self.response_times = deque(maxlen=1000)
        self.last_state_change = datetime.now()
        self.half_open_calls = 0
        self.half_open_successes = 0
        
        # 回调函数
        self.state_change_callbacks = []
        self.failure_callbacks = []
        self.recovery_callbacks = []
        
        self.logger.info(f"熔断器 {config.name} 初始化完成")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行受保护的方法调用"""
        start_time = time.time()
        
        try:
            # 检查熔断器状态
            if not self._allow_request():
                self.metrics.rejected_requests += 1
                return self._handle_rejection()
            
            # 执行实际调用
            result = func(*args, **kwargs)
            
            # 记录成功调用
            duration = time.time() - start_time
            self._record_success(duration)
            
            return result
        
        except Exception as e:
            # 记录失败调用
            duration = time.time() - start_time
            failure_type = self._classify_failure(e)
            self._record_failure(failure_type, str(e), duration)
            
            # 触发熔断检查
            self._check_circuit_conditions()
            
            # 返回降级响应
            return self._handle_fallback(e)
    
    def _allow_request(self) -> bool:
        """检查是否允许请求通过"""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                # 检查是否可以进入半开状态
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                # 半开状态限制请求数量
                return self.half_open_calls < self.config.half_open_max_calls
            return False
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        time_since_open = datetime.now() - self.last_state_change
        return time_since_open.total_seconds() >= self.config.recovery_timeout
    
    def _transition_to_half_open(self):
        """转换到半开状态"""
        with self.lock:
            self.state = CircuitState.HALF_OPEN
            self.last_state_change = datetime.now()
            self.half_open_calls = 0
            self.half_open_successes = 0
            self.metrics.state_change_count += 1
            
        self.logger.info(f"熔断器 {self.config.name} 进入半开状态")
        self._notify_state_change(CircuitState.OPEN, CircuitState.HALF_OPEN)
    
    def _record_success(self, duration: float):
        """记录成功调用"""
        with self.lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.response_times.append(duration)
            
            # 更新平均响应时间
            if self.response_times:
                self.metrics.average_response_time = statistics.mean(self.response_times)
            
            # 更新失败率
            self._update_failure_rate()
            
            # 半开状态处理
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
                self.half_open_successes += 1
                
                # 检查是否可以恢复到关闭状态
                if (self.half_open_calls >= self.config.half_open_max_calls and
                    self.half_open_successes / self.half_open_calls >= self.config.half_open_success_threshold):
                    self._transition_to_closed()
        
        self.logger.debug(f"熔断器 {self.config.name} 记录成功调用，耗时: {duration:.3f}s")
    
    def _record_failure(self, failure_type: FailureType, error_message: str, duration: float):
        """记录失败调用"""
        with self.lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_failure_time = datetime.now()
            
            # 记录失败详情
            failure_record = FailureRecord(
                timestamp=datetime.now(),
                failure_type=failure_type,
                error_message=error_message,
                duration=duration
            )
            self.failure_records.append(failure_record)
            
            # 更新失败率
            self._update_failure_rate()
            
            # 触发失败回调
            self._notify_failure(failure_record)
        
        self.logger.warning(f"熔断器 {self.config.name} 记录失败调用: {error_message}")
    
    def _update_failure_rate(self):
        """更新失败率"""
        if self.metrics.total_requests >= self.config.failure_rate_min_requests:
            self.metrics.failure_rate = self.metrics.failed_requests / self.metrics.total_requests
    
    def _classify_failure(self, exception: Exception) -> FailureType:
        """分类失败类型"""
        exception_type = type(exception).__name__
        
        if isinstance(exception, TimeoutError):
            return FailureType.TIMEOUT
        elif exception_type in ['ConnectionError', 'ConnectTimeout']:
            return FailureType.CONNECTION_ERROR
        elif exception_type in self.config.exception_types:
            return FailureType.BUSINESS_ERROR
        else:
            return FailureType.EXCEPTION
    
    def _check_circuit_conditions(self):
        """检查熔断条件"""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                # 检查失败率
                if (self.metrics.failure_rate >= self.config.failure_rate_threshold and
                    self.metrics.total_requests >= self.config.failure_rate_min_requests):
                    self._transition_to_open()
                    return
                
                # 检查响应时间
                if self._check_response_time_condition():
                    self._transition_to_open()
                    return
    
    def _check_response_time_condition(self) -> bool:
        """检查响应时间条件"""
        if not self.response_times:
            return False
        
        # 计算指定百分位的响应时间
        sorted_times = sorted(self.response_times)
        percentile_index = int(len(sorted_times) * self.config.response_time_percentile / 100)
        percentile_time = sorted_times[min(percentile_index, len(sorted_times) - 1)]
        
        return percentile_time >= self.config.response_time_threshold
    
    def _transition_to_open(self):
        """转换到打开状态"""
        with self.lock:
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
            self.metrics.state_change_count += 1
        
        self.logger.warning(f"熔断器 {self.config.name} 进入打开状态")
        self._notify_state_change(CircuitState.CLOSED, CircuitState.OPEN)
    
    def _transition_to_closed(self):
        """转换到关闭状态"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.last_state_change = datetime.now()
            self.metrics.state_change_count += 1
            self.half_open_calls = 0
            self.half_open_successes = 0
            
            # 清理部分统计数据
            self.failure_records.clear()
            self.response_times.clear()
        
        self.logger.info(f"熔断器 {self.config.name} 恢复到关闭状态")
        self._notify_state_change(CircuitState.HALF_OPEN, CircuitState.CLOSED)
        self._notify_recovery()
    
    def _handle_rejection(self) -> Any:
        """处理请求拒绝"""
        if self.config.fallback_enabled:
            if self.config.fallback_function:
                return self.config.fallback_function()
            else:
                return self.config.fallback_response
        else:
            raise CircuitBreakerOpenException(f"熔断器 {self.config.name} 处于打开状态")
    
    def _handle_fallback(self, original_exception: Exception) -> Any:
        """处理降级响应"""
        if self.config.fallback_enabled:
            if self.config.fallback_function:
                try:
                    return self.config.fallback_function(original_exception)
                except Exception as fallback_error:
                    self.logger.error(f"降级函数执行失败: {fallback_error}")
                    raise CircuitBreakerFallbackException(f"降级处理失败: {fallback_error}")
            else:
                return self.config.fallback_response
        else:
            raise original_exception
    
    def get_state(self) -> CircuitState:
        """获取当前状态"""
        with self.lock:
            return self.state
    
    def get_metrics(self) -> CircuitMetrics:
        """获取指标数据"""
        with self.lock:
            metrics = CircuitMetrics(
                total_requests=self.metrics.total_requests,
                successful_requests=self.metrics.successful_requests,
                failed_requests=self.metrics.failed_requests,
                rejected_requests=self.metrics.rejected_requests,
                timeout_requests=self.metrics.timeout_requests,
                average_response_time=self.metrics.average_response_time,
                failure_rate=self.metrics.failure_rate,
                last_failure_time=self.metrics.last_failure_time,
                state_change_count=self.metrics.state_change_count,
                current_state=self.state
            )
            return metrics
    
    def reset(self):
        """重置熔断器"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.last_state_change = datetime.now()
            self.metrics = CircuitMetrics()
            self.failure_records.clear()
            self.response_times.clear()
            self.half_open_calls = 0
            self.half_open_successes = 0
        
        self.logger.info(f"熔断器 {self.config.name} 已重置")
    
    def add_state_change_callback(self, callback: Callable):
        """添加状态变更回调"""
        self.state_change_callbacks.append(callback)
    
    def add_failure_callback(self, callback: Callable):
        """添加失败回调"""
        self.failure_callbacks.append(callback)
    
    def add_recovery_callback(self, callback: Callable):
        """添加恢复回调"""
        self.recovery_callbacks.append(callback)
    
    def _notify_state_change(self, old_state: CircuitState, new_state: CircuitState):
        """通知状态变更"""
        for callback in self.state_change_callbacks:
            try:
                callback(self.config.name, old_state, new_state)
            except Exception as e:
                self.logger.error(f"状态变更回调执行失败: {e}")
    
    def _notify_failure(self, failure_record: FailureRecord):
        """通知失败事件"""
        for callback in self.failure_callbacks:
            try:
                callback(self.config.name, failure_record)
            except Exception as e:
                self.logger.error(f"失败回调执行失败: {e}")
    
    def _notify_recovery(self):
        """通知恢复事件"""
        for callback in self.recovery_callbacks:
            try:
                callback(self.config.name)
            except Exception as e:
                self.logger.error(f"恢复回调执行失败: {e}")

class CircuitBreakerOpenException(Exception):
    """熔断器打开异常"""
    pass

class CircuitBreakerFallbackException(Exception):
    """熔断器降级异常"""
    pass

class CircuitBreakerManager:
    """熔断器管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.RLock()
    
    def create_circuit_breaker(self, config: CircuitConfig) -> CircuitBreaker:
        """创建熔断器"""
        with self.lock:
            if config.name in self.circuit_breakers:
                raise ValueError(f"熔断器 {config.name} 已存在")
            
            circuit_breaker = CircuitBreaker(config)
            self.circuit_breakers[config.name] = circuit_breaker
            
            self.logger.info(f"熔断器 {config.name} 创建成功")
            return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """获取熔断器"""
        with self.lock:
            return self.circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """移除熔断器"""
        with self.lock:
            if name in self.circuit_breakers:
                del self.circuit_breakers[name]
                self.logger.info(f"熔断器 {name} 已移除")
                return True
            return False
    
    def list_circuit_breakers(self) -> List[str]:
        """列出所有熔断器名称"""
        with self.lock:
            return list(self.circuit_breakers.keys())
    
    def get_all_metrics(self) -> Dict[str, CircuitMetrics]:
        """获取所有熔断器指标"""
        metrics = {}
        with self.lock:
            for name, circuit_breaker in self.circuit_breakers.items():
                metrics[name] = circuit_breaker.get_metrics()
        return metrics
    
    def reset_all(self):
        """重置所有熔断器"""
        with self.lock:
            for circuit_breaker in self.circuit_breakers.values():
                circuit_breaker.reset()
        
        self.logger.info("所有熔断器已重置")

class CircuitBreakerDecorator:
    """熔断器装饰器"""
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            return self.circuit_breaker.call(func, *args, **kwargs)
        return wrapper

class CircuitBreakerRegistry:
    """熔断器注册表"""
    
    def __init__(self):
        self.manager = CircuitBreakerManager()
        self.logger = logging.getLogger(__name__)
    
    def register(self, name: str, service_name: str, **kwargs) -> CircuitBreaker:
        """注册熔断器"""
        config = CircuitConfig(name=name, service_name=service_name, **kwargs)
        return self.manager.create_circuit_breaker(config)
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """获取熔断器"""
        return self.manager.get_circuit_breaker(name)
    
    def circuit_breaker(self, name: str, service_name: str, **kwargs):
        """熔断器装饰器"""
        circuit_breaker = self.register(name, service_name, **kwargs)
        return CircuitBreakerDecorator(circuit_breaker)

# 全局熔断器注册表
circuit_breaker_registry = CircuitBreakerRegistry()

# 使用示例
# 1. 直接使用熔断器
config = CircuitConfig(
    name="user_service_circuit",
    service_name="user_service",
    failure_rate_threshold=0.5,
    failure_rate_min_requests=10,
    response_time_threshold=2.0,
    recovery_timeout=30.0,
    fallback_response={"error": "Service temporarily unavailable"}
)

circuit_breaker = CircuitBreaker(config)

def call_user_service(user_id: str):
    """调用用户服务"""
    # 模拟服务调用
    time.sleep(0.1)  # 模拟网络延迟
    if user_id == "error":
        raise Exception("User not found")
    return {"user_id": user_id, "name": "Test User"}

# 使用熔断器保护服务调用
try:
    result = circuit_breaker.call(call_user_service, "123")
    print(f"调用成功: {result}")
except Exception as e:
    print(f"调用失败: {e}")

# 2. 使用装饰器
@circuit_breaker_registry.circuit_breaker(
    name="order_service_circuit",
    service_name="order_service",
    failure_rate_threshold=0.3,
    response_time_threshold=1.5,
    fallback_response={"error": "Order service unavailable"}
)
def create_order(user_id: str, product_id: str):
    """创建订单"""
    # 模拟订单创建
    time.sleep(0.2)
    if product_id == "invalid":
        raise ValueError("Invalid product")
    return {"order_id": str(uuid.uuid4()), "user_id": user_id, "product_id": product_id}

# 使用装饰器保护的函数
try:
    order = create_order("123", "product_1")
    print(f"订单创建成功: {order}")
except Exception as e:
    print(f"订单创建失败: {e}")

# 3. 监控熔断器状态
def monitor_circuit_breaker():
    """监控熔断器状态"""
    metrics = circuit_breaker.get_metrics()
    print(f"熔断器状态: {metrics.current_state}")
    print(f"总请求数: {metrics.total_requests}")
    print(f"成功请求数: {metrics.successful_requests}")
    print(f"失败请求数: {metrics.failed_requests}")
    print(f"拒绝请求数: {metrics.rejected_requests}")
    print(f"失败率: {metrics.failure_rate:.2%}")
    print(f"平均响应时间: {metrics.average_response_time:.3f}s")

monitor_circuit_breaker()
```

### 熔断器监控和告警
```python
# circuit_breaker_monitoring.py
import json
import time
import logging
import threading
import queue
import requests
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from circuit_breaker import CircuitBreaker, CircuitMetrics, CircuitState, AlertLevel

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: str
    threshold: float
    level: AlertLevel
    message: str
    enabled: bool = True

class CircuitBreakerMonitor:
    """熔断器监控器"""
    
    def __init__(self, circuit_breaker_manager):
        self.logger = logging.getLogger(__name__)
        self.manager = circuit_breaker_manager
        self.alert_rules: List[AlertRule] = []
        self.notification_handlers = []
        self.monitoring_enabled = True
        self.monitoring_interval = 10  # 10秒
        self.metrics_history = {}
        self.lock = threading.RLock()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        with self.lock:
            self.alert_rules.append(rule)
        self.logger.info(f"添加告警规则: {rule.name}")
    
    def add_notification_handler(self, handler):
        """添加通知处理器"""
        self.notification_handlers.append(handler)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring_enabled:
            try:
                self._check_all_circuit_breakers()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
    
    def _check_all_circuit_breakers(self):
        """检查所有熔断器"""
        all_metrics = self.manager.get_all_metrics()
        
        for name, metrics in all_metrics.items():
            self._store_metrics(name, metrics)
            self._check_alert_rules(name, metrics)
    
    def _store_metrics(self, name: str, metrics: CircuitMetrics):
        """存储指标历史"""
        with self.lock:
            if name not in self.metrics_history:
                self.metrics_history[name] = []
            
            self.metrics_history[name].append({
                'timestamp': datetime.now(),
                'metrics': metrics
            })
            
            # 保留最近1小时的数据
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.metrics_history[name] = [
                item for item in self.metrics_history[name]
                if item['timestamp'] > cutoff_time
            ]
    
    def _check_alert_rules(self, circuit_name: str, metrics: CircuitMetrics):
        """检查告警规则"""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_rule(rule, metrics):
                self._trigger_alert(circuit_name, rule, metrics)
    
    def _evaluate_rule(self, rule: AlertRule, metrics: CircuitMetrics) -> bool:
        """评估告警规则"""
        if rule.condition == "failure_rate":
            return metrics.failure_rate >= rule.threshold
        elif rule.condition == "response_time":
            return metrics.average_response_time >= rule.threshold
        elif rule.condition == "state_open":
            return metrics.current_state == CircuitState.OPEN
        elif rule.condition == "rejected_requests":
            return metrics.rejected_requests >= rule.threshold
        elif rule.condition == "total_requests":
            return metrics.total_requests >= rule.threshold
        else:
            return False
    
    def _trigger_alert(self, circuit_name: str, rule: AlertRule, metrics: CircuitMetrics):
        """触发告警"""
        alert_data = {
            'circuit_name': circuit_name,
            'rule_name': rule.name,
            'level': rule.level,
            'message': rule.message,
            'timestamp': datetime.now(),
            'metrics': metrics
        }
        
        # 发送通知
        for handler in self.notification_handlers:
            try:
                handler(alert_data)
            except Exception as e:
                self.logger.error(f"通知处理器执行失败: {e}")
        
        self.logger.warning(f"触发告警: {circuit_name} - {rule.name}")
    
    def get_metrics_history(self, circuit_name: str, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """获取指标历史"""
        with self.lock:
            if circuit_name not in self.metrics_history:
                return []
            
            history = self.metrics_history[circuit_name]
            
            if start_time or end_time:
                filtered_history = []
                for item in history:
                    timestamp = item['timestamp']
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    filtered_history.append(item)
                return filtered_history
            
            return history
    
    def get_circuit_health_score(self, circuit_name: str) -> float:
        """计算熔断器健康评分"""
        metrics = self.manager.get_circuit_breaker(circuit_name)
        if not metrics:
            return 0.0
        
        circuit_metrics = metrics.get_metrics()
        
        # 基础分数
        base_score = 100.0
        
        # 状态扣分
        if circuit_metrics.current_state == CircuitState.OPEN:
            base_score -= 50.0
        elif circuit_metrics.current_state == CircuitState.HALF_OPEN:
            base_score -= 25.0
        
        # 失败率扣分
        failure_penalty = circuit_metrics.failure_rate * 30.0
        base_score -= failure_penalty
        
        # 响应时间扣分
        response_time_penalty = min(circuit_metrics.average_response_time * 10.0, 20.0)
        base_score -= response_time_penalty
        
        # 拒绝请求扣分
        if circuit_metrics.total_requests > 0:
            rejection_rate = circuit_metrics.rejected_requests / circuit_metrics.total_requests
            rejection_penalty = rejection_rate * 20.0
            base_score -= rejection_penalty
        
        return max(0.0, base_score)

class EmailNotificationHandler:
    """邮件通知处理器"""
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 username: str, password: str, recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients
    
    def __call__(self, alert_data: Dict[str, Any]):
        """发送邮件通知"""
        try:
            subject = f"[{alert_data['level'].upper()}] 熔断器告警: {alert_data['circuit_name']}"
            
            body = f"""
熔断器告警通知

熔断器名称: {alert_data['circuit_name']}
告警规则: {alert_data['rule_name']}
告警级别: {alert_data['level']}
告警消息: {alert_data['message']}
告警时间: {alert_data['timestamp']}

当前指标:
- 状态: {alert_data['metrics'].current_state}
- 总请求数: {alert_data['metrics'].total_requests}
- 成功请求数: {alert_data['metrics'].successful_requests}
- 失败请求数: {alert_data['metrics'].failed_requests}
- 拒绝请求数: {alert_data['metrics'].rejected_requests}
- 失败率: {alert_data['metrics'].failure_rate:.2%}
- 平均响应时间: {alert_data['metrics'].average_response_time:.3f}s
"""
            
            msg = MimeMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logging.error(f"发送邮件通知失败: {e}")

class WebhookNotificationHandler:
    """Webhook通知处理器"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {}
    
    def __call__(self, alert_data: Dict[str, Any]):
        """发送Webhook通知"""
        try:
            payload = {
                'alert_type': 'circuit_breaker',
                'circuit_name': alert_data['circuit_name'],
                'rule_name': alert_data['rule_name'],
                'level': alert_data['level'].value,
                'message': alert_data['message'],
                'timestamp': alert_data['timestamp'].isoformat(),
                'metrics': {
                    'current_state': alert_data['metrics'].current_state.value,
                    'total_requests': alert_data['metrics'].total_requests,
                    'successful_requests': alert_data['metrics'].successful_requests,
                    'failed_requests': alert_data['metrics'].failed_requests,
                    'rejected_requests': alert_data['metrics'].rejected_requests,
                    'failure_rate': alert_data['metrics'].failure_rate,
                    'average_response_time': alert_data['metrics'].average_response_time
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
        except Exception as e:
            logging.error(f"发送Webhook通知失败: {e}")

class CircuitBreakerDashboard:
    """熔断器仪表板"""
    
    def __init__(self, monitor: CircuitBreakerMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """生成仪表板数据"""
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'circuit_breakers': [],
            'summary': {
                'total_circuits': 0,
                'open_circuits': 0,
                'half_open_circuits': 0,
                'closed_circuits': 0,
                'average_health_score': 0.0
            }
        }
        
        all_metrics = self.monitor.manager.get_all_metrics()
        health_scores = []
        
        for name, metrics in all_metrics.items():
            health_score = self.monitor.get_circuit_health_score(name)
            health_scores.append(health_score)
            
            circuit_data = {
                'name': name,
                'service_name': metrics.service_name if hasattr(metrics, 'service_name') else 'unknown',
                'state': metrics.current_state.value,
                'health_score': health_score,
                'metrics': {
                    'total_requests': metrics.total_requests,
                    'successful_requests': metrics.successful_requests,
                    'failed_requests': metrics.failed_requests,
                    'rejected_requests': metrics.rejected_requests,
                    'failure_rate': metrics.failure_rate,
                    'average_response_time': metrics.average_response_time,
                    'last_failure_time': metrics.last_failure_time.isoformat() if metrics.last_failure_time else None
                }
            }
            
            dashboard_data['circuit_breakers'].append(circuit_data)
            
            # 更新统计信息
            dashboard_data['summary']['total_circuits'] += 1
            if metrics.current_state == CircuitState.OPEN:
                dashboard_data['summary']['open_circuits'] += 1
            elif metrics.current_state == CircuitState.HALF_OPEN:
                dashboard_data['summary']['half_open_circuits'] += 1
            else:
                dashboard_data['summary']['closed_circuits'] += 1
        
        # 计算平均健康评分
        if health_scores:
            dashboard_data['summary']['average_health_score'] = sum(health_scores) / len(health_scores)
        
        return dashboard_data
    
    def export_metrics_csv(self, circuit_name: str, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> str:
        """导出指标为CSV格式"""
        history = self.monitor.get_metrics_history(circuit_name, start_time, end_time)
        
        if not history:
            return "No data available"
        
        csv_lines = [
            "timestamp,total_requests,successful_requests,failed_requests,rejected_requests,failure_rate,average_response_time,state"
        ]
        
        for item in history:
            timestamp = item['timestamp']
            metrics = item['metrics']
            
            line = f"{timestamp.isoformat()},{metrics.total_requests},{metrics.successful_requests},{metrics.failed_requests},{metrics.rejected_requests},{metrics.failure_rate},{metrics.average_response_time},{metrics.current_state.value}"
            csv_lines.append(line)
        
        return '\n'.join(csv_lines)

# 使用示例
# 创建监控器
monitor = CircuitBreakerMonitor(circuit_breaker_registry.manager)

# 添加告警规则
monitor.add_alert_rule(AlertRule(
    name="high_failure_rate",
    condition="failure_rate",
    threshold=0.5,
    level=AlertLevel.HIGH,
    message="失败率过高"
))

monitor.add_alert_rule(AlertRule(
    name="circuit_open",
    condition="state_open",
    threshold=0,
    level=AlertLevel.CRITICAL,
    message="熔断器已打开"
))

monitor.add_alert_rule(AlertRule(
    name="high_response_time",
    condition="response_time",
    threshold=2.0,
    level=AlertLevel.MEDIUM,
    message="响应时间过长"
))

# 添加通知处理器
email_handler = EmailNotificationHandler(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your_email@gmail.com",
    password="your_password",
    recipients=["admin@example.com"]
)

webhook_handler = WebhookNotificationHandler(
    webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
)

monitor.add_notification_handler(email_handler)
monitor.add_notification_handler(webhook_handler)

# 创建仪表板
dashboard = CircuitBreakerDashboard(monitor)

# 生成仪表板数据
dashboard_data = dashboard.generate_dashboard_data()
print(f"仪表板数据: {json.dumps(dashboard_data, indent=2, default=str)}")
```

## 参考资源

### 熔断器框架文档
- [Hystrix官方文档](https://github.com/Netflix/Hystrix/wiki)
- [Resilience4j官方文档](https://resilience4j.readme.io/)
- [Sentinel官方文档](https://sentinelguard.io/zh-cn/)
- [Spring Circuit Breaker](https://spring.io/projects/spring-boot)

### 设计模式和最佳实践
- [熔断器模式详解](https://martinfowler.com/bliki/CircuitBreaker.html)
- [微服务容错模式](https://microservices.io/patterns/reliability/circuit-breaker.html)
- [分布式系统设计模式](https://docs.microsoft.com/en-us/azure/architecture/patterns/)
- [云原生应用最佳实践](https://12factor.net/)

### 监控和运维
- [Prometheus监控指南](https://prometheus.io/docs/)
- [Grafana仪表板](https://grafana.com/docs/)
- [微服务监控最佳实践](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/)
- [分布式链路追踪](https://opentelemetry.io/docs/)
