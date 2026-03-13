---
name: 错误处理与日志系统
description: "当设计错误处理和日志系统时，分析异常处理策略，优化日志记录性能，解决系统监控问题。验证错误架构，设计日志模式，和最佳实践。"
license: MIT
---

# 错误处理与日志系统技能

## 概述
错误处理和日志记录是构建可靠、可维护系统的基础设施。不当的错误处理会导致系统崩溃、调试困难；不合理的日志记录会影响性能并浪费存储空间。需要建立完善的错误处理和日志体系。

**核心原则**: 好的错误处理应该优雅地处理异常，提供有用的错误信息；好的日志系统应该记录关键信息，便于问题排查和性能分析。

## 何时使用

**始终:**
- 设计新系统架构时
- 处理异常和错误时
- 实现日志记录系统时
- 设计监控告警时
- 调试生产问题时
- 进行系统审计时

**触发短语:**
- "系统出错了怎么处理？"
- "如何设计日志系统？"
- "异常应该怎么捕获？"
- "日志级别怎么设置？"
- "如何快速定位问题？"
- "监控告警怎么配置？"

## 错误处理技能功能

### 异常处理策略
- 全局异常捕获
- 分层异常处理
- 异常分类和映射
- 错误码标准化
- 异常恢复机制

### 日志记录模式
- 结构化日志
- 日志级别管理
- 日志聚合和索引
- 日志轮转和归档
- 实时日志分析

### 监控告警检查
- 错误率监控
- 性能指标监控
- 业务指标监控
- 告警规则配置
- 自动化响应

## 常见错误处理问题

### 异常吞噬问题
```
问题:
捕获异常但不处理，直接忽略

后果:
- 问题被掩盖
- 调试困难
- 系统状态异常
- 用户体验差

解决方案:
- 记录异常信息
- 分类处理不同异常
- 提供用户友好的错误信息
- 实现适当的恢复机制
```

### 日志过度记录
```
问题:
记录过多无用日志信息

后果:
- 存储空间浪费
- 查找困难
- 性能影响
- 成本增加

解决方案:
- 合理设置日志级别
- 结构化日志格式
- 日志采样策略
- 敏感信息过滤
```

### 错误信息泄露
```
问题:
向用户暴露技术细节

后果:
- 安全漏洞
- 用户体验差
- 系统信息泄露
- 攻击面增加

解决方案:
- 错误信息脱敏
- 用户友好提示
- 技术详情记录到日志
- 统一错误响应格式
```

## 错误处理架构设计

### 分层错误处理
```
架构: 控制器层 -> 服务层 -> 数据层

处理策略:
- 控制器层: 参数验证、用户错误
- 服务层: 业务逻辑错误
- 数据层: 数据库、网络错误

实现要点:
- 每层定义自己的异常类型
- 上层捕获下层异常并转换
- 统一错误响应格式
- 记录完整的错误链路
```

### 全局异常处理
```
架构: 统一异常处理器 -> 错误分类 -> 响应生成

适用场景:
- Web应用全局错误处理
- API服务错误响应
- 批量任务异常处理

实现要点:
- 异常捕获机制
- 错误分类映射
- 日志记录集成
- 监控告警触发
```

## 日志系统设计

### 日志级别规范
| 级别 | 用途 | 示例 |
|------|------|------|
| ERROR | 系统错误、异常 | 数据库连接失败、空指针异常 |
| WARN | 警告信息 | 配置项缺失、性能问题 |
| INFO | 重要业务信息 | 用户登录、订单创建 |
| DEBUG | 调试信息 | 方法调用、参数值 |
| TRACE | 详细跟踪信息 | 循环执行、状态变化 |

### 结构化日志格式
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "ERROR",
  "service": "user-service",
  "trace_id": "abc123",
  "user_id": "user456",
  "message": "User login failed",
  "context": {
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "error_code": "INVALID_PASSWORD"
  },
  "stack_trace": "java.lang.IllegalArgumentException..."
}
```

## 代码实现示例

### Python错误处理
```python
import logging
import traceback
from functools import wraps
from typing import Optional
import json

# 配置日志系统
def setup_logging():
    """配置结构化日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

# 自定义异常类
class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message: str, error_code: str = None, context: dict = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)

class SystemException(Exception):
    """系统异常"""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

# 错误处理装饰器
def handle_errors(logger: logging.Logger):
    """统一错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BusinessException as e:
                logger.error(f"Business error in {func.__name__}: {e.message}", 
                           extra={'error_code': e.error_code, 'context': e.context})
                raise
            except SystemException as e:
                logger.error(f"System error in {func.__name__}: {e.message}", 
                           exc_info=e.original_error)
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", 
                           exc_info=True)
                raise SystemException("系统内部错误", e)
        return wrapper
    return decorator

# 结构化日志记录
class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(self, level: str, event: str, **context):
        """记录事件日志"""
        log_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat(),
            **context
        }
        getattr(self.logger, level.lower())(json.dumps(log_data))
    
    def log_error(self, error: Exception, **context):
        """记录错误日志"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            **context
        }
        self.logger.error(json.dumps(error_data))

# 使用示例
logger = StructuredLogger('user-service')

@handle_errors(logger.logger)
def create_user(user_data: dict):
    """创建用户"""
    if not user_data.get('email'):
        raise BusinessException("邮箱不能为空", 
                             error_code="MISSING_EMAIL",
                             context={'user_data': user_data})
    
    try:
        # 创建用户逻辑
        user_id = save_user_to_db(user_data)
        logger.log_event('INFO', 'user_created', 
                        user_id=user_id, email=user_data['email'])
        return user_id
    except DatabaseError as e:
        raise SystemException("数据库操作失败", e)

# 统一错误响应
def create_error_response(error: Exception) -> dict:
    """创建统一错误响应"""
    if isinstance(error, BusinessException):
        return {
            'error': 'business_error',
            'message': error.message,
            'error_code': error.error_code,
            'context': error.context
        }
    else:
        return {
            'error': 'system_error',
            'message': '系统内部错误，请稍后重试'
        }
```

### Java错误处理
```java
// 自定义异常类
public class BusinessException extends RuntimeException {
    private String errorCode;
    private Map<String, Object> context;
    
    public BusinessException(String message, String errorCode) {
        super(message);
        this.errorCode = errorCode;
        this.context = new HashMap<>();
    }
    
    // getters and setters
}

// 全局异常处理器
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        logger.error("Business error: {}", e.getMessage(), e);
        
        ErrorResponse response = ErrorResponse.builder()
            .error("business_error")
            .message(e.getMessage())
            .errorCode(e.getErrorCode())
            .context(e.getContext())
            .timestamp(Instant.now())
            .build();
            
        return ResponseEntity.badRequest().body(response);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception e) {
        logger.error("Unexpected error: {}", e.getMessage(), e);
        
        ErrorResponse response = ErrorResponse.builder()
            .error("system_error")
            .message("系统内部错误")
            .timestamp(Instant.now())
            .build();
            
        return ResponseEntity.status(500).body(response);
    }
}

// 结构化日志
@Component
public class StructuredLogger {
    private final Logger logger;
    
    public StructuredLogger() {
        this.logger = LoggerFactory.getLogger(StructuredLogger.class);
    }
    
    public void logEvent(String level, String event, Map<String, Object> context) {
        Map<String, Object> logData = new HashMap<>();
        logData.put("event", event);
        logData.put("timestamp", Instant.now());
        logData.putAll(context);
        
        String logMessage = JsonUtils.toJson(logData);
        
        switch (level.toUpperCase()) {
            case "ERROR":
                logger.error(logMessage);
                break;
            case "WARN":
                logger.warn(logMessage);
                break;
            case "INFO":
                logger.info(logMessage);
                break;
            default:
                logger.debug(logMessage);
        }
    }
}
```

## 监控和告警

### 关键监控指标
- **错误率**: ERROR级别日志数量/总请求数
- **响应时间**: API响应时间分布
- **吞吐量**: 每秒处理请求数
- **资源使用**: CPU、内存、磁盘使用率
- **业务指标**: 订单量、用户活跃度等

### 告警规则配置
```yaml
# Prometheus告警规则示例
groups:
- name: error_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(error_logs_total[5m]) > 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "错误率过高"
      description: "5分钟内错误率超过10%"
      
  - alert: DatabaseConnectionFailed
    expr: increase(db_connection_errors_total[1m]) > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "数据库连接失败"
      description: "检测到数据库连接错误"
```

## 日志管理最佳实践

### 日志记录原则
1. **适量原则**: 记录必要信息，避免过度记录
2. **结构化**: 使用统一格式，便于解析和查询
3. **安全原则**: 避免记录敏感信息
4. **性能考虑**: 异步记录，避免影响主业务
5. **可追溯性**: 包含足够的上下文信息

### 日志分析策略
- **实时监控**: 关键指标实时告警
- **趋势分析**: 长期趋势分析
- **异常检测**: 自动异常模式识别
- **根因分析**: 多维度关联分析
- **容量规划**: 基于日志数据的容量预测

## 相关技能

- **api-validator** - API接口验证和错误处理
- **security-scanner** - 安全漏洞扫描和告警
- **performance-profiler** - 性能分析和监控
- **monitoring-alerting** - 监控告警系统
