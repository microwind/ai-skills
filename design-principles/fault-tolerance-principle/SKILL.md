---
name: 容错性原则
description: "设计系统使其在部分组件失败时仍能继续提供服务，优雅地处理和恢复错误。"
license: MIT
---

# 容错性原则 (Fault Tolerance Principle)

## 概述

容错性：**系统在部分组件发生故障时，仍能继续正确地提供服务**。故障是必然的，系统设计必须考虑故障场景。

**核心思想**：
- Design for failure —— 为故障而设计
- 故障是常态，不是例外
- 故障应该被检测、隔离和恢复

## 容错模式

### 1. 断路器模式 (Circuit Breaker)

```java
// ✅ 断路器：防止故障蔓延
public class CircuitBreaker {
    private int failureCount = 0;
    private int threshold = 5;
    private long lastFailureTime;
    private long resetTimeout = 30_000;  // 30秒

    enum State { CLOSED, OPEN, HALF_OPEN }
    private State state = State.CLOSED;

    public <T> T execute(Supplier<T> action, Supplier<T> fallback) {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime > resetTimeout) {
                state = State.HALF_OPEN;  // 尝试恢复
            } else {
                return fallback.get();  // 直接走降级
            }
        }

        try {
            T result = action.get();
            if (state == State.HALF_OPEN) {
                state = State.CLOSED;  // 恢复正常
                failureCount = 0;
            }
            return result;
        } catch (Exception e) {
            failureCount++;
            lastFailureTime = System.currentTimeMillis();
            if (failureCount >= threshold) {
                state = State.OPEN;  // 打开断路器
            }
            return fallback.get();
        }
    }
}

// 使用
CircuitBreaker breaker = new CircuitBreaker();
String result = breaker.execute(
    () -> externalService.call(),     // 正常调用
    () -> "默认值"                     // 降级方案
);
```

### 2. 舱壁模式 (Bulkhead)

```python
# ✅ 资源隔离：一个服务出问题不影响其他服务
from concurrent.futures import ThreadPoolExecutor

class BulkheadService:
    def __init__(self):
        # 不同服务使用独立的线程池
        self.order_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="order")
        self.payment_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="payment")
        self.notification_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="notify")

    def process_order(self, order_data):
        # 支付服务卡住不会耗尽订单服务的线程
        return self.order_pool.submit(self._do_process, order_data)

    def process_payment(self, payment_data):
        return self.payment_pool.submit(self._do_payment, payment_data)
```

### 3. 重试与退避

```typescript
// ✅ 指数退避重试
async function withRetry<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
): Promise<T> {
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            if (attempt === maxRetries) throw error;

            // 指数退避 + 随机抖动
            const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
    throw new Error('Unreachable');
}

// 使用
const data = await withRetry(() => fetch('/api/data').then(r => r.json()));
```

### 4. 超时控制

```java
// ✅ 所有外部调用必须有超时
public class HttpClient {
    public String get(String url) {
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setConnectTimeout(3000);  // 连接超时 3 秒
        conn.setReadTimeout(5000);     // 读取超时 5 秒
        return readResponse(conn);
    }
}
```

## Fail-Fast vs Fail-Safe

```
Fail-Fast（快速失败）：
- 尽早发现错误并报告
- 适用于编程错误、配置错误
- 例：参数验证失败立即抛异常

Fail-Safe（安全失败）：
- 发生错误时继续运行
- 适用于运行时可恢复的故障
- 例：缓存失败走数据库
```

## 容错检查清单

```
□ 所有外部调用有超时设置
□ 关键调用有断路器保护
□ 不同服务间有资源隔离（舱壁）
□ 有重试机制（带指数退避和抖动）
□ 有降级方案（核心功能不依赖非核心服务）
□ 有死信队列处理失败消息
□ 错误日志包含足够的上下文信息
□ 定期进行故障注入测试（Chaos Engineering）
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [可用性](../availability-principle/) | 容错是保障可用性的技术手段 |
| [关注点分离](../separation-of-concerns/) | 隔离故障域需要清晰的边界 |
| [封装](../encapsulation-principle/) | 故障处理逻辑封装在基础设施中 |

## 总结

**核心**：为故障而设计，检测、隔离、恢复。

**关键模式**：断路器、舱壁、重试退避、超时控制、优雅降级。
