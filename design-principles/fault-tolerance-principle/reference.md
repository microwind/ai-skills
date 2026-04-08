# 容错性原则 - 参考实现

> 完整的容错模式参考实现，涵盖熔断器、舱壁隔离、重试退避、超时控制和优雅降级。

---

## 核心原理与设计

### 容错性原则概述

容错性原则（Fault Tolerance Principle）要求系统在部分组件故障时仍能继续提供服务。核心思想：

1. **故障是必然的** — 网络会断、服务会挂、磁盘会满，设计时必须假设故障会发生
2. **快速失败优于长时间等待** — 及时发现并响应故障，避免资源浪费
3. **隔离故障传播** — 一个组件的故障不应导致整个系统不可用
4. **优雅降级** — 在能力受限时提供有限但可用的服务

### 核心容错模式

```
┌─────────────────────────────────────────────────┐
│                    客户端请求                      │
├─────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌─────────────┐ │
│  │  超时控制   │  │  重试退避   │  │  熔断器      │ │
│  │ (Timeout)  │  │  (Retry)  │  │ (Circuit    │ │
│  │           │  │           │  │  Breaker)   │ │
│  └───────────┘  └───────────┘  └─────────────┘ │
│  ┌───────────┐  ┌───────────┐  ┌─────────────┐ │
│  │  舱壁隔离   │  │  降级方案   │  │  负载脱落    │ │
│  │ (Bulkhead)│  │ (Fallback)│  │ (Load      │ │
│  │           │  │           │  │  Shedding)  │ │
│  └───────────┘  └───────────┘  └─────────────┘ │
├─────────────────────────────────────────────────┤
│                    外部依赖                       │
└─────────────────────────────────────────────────┘
```

### 模式之间的协作关系

```
请求 → 舱壁(限流) → 熔断器(判断) → 超时(限时) → 重试(恢复) → 调用
                                                            ↓
                                                         失败?
                                                            ↓
                                                       降级(兜底)
```

---

## Java 参考实现

### 熔断器实现 (Circuit Breaker)

```java
import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

/**
 * 熔断器实现
 *
 * 状态转换: CLOSED → OPEN → HALF_OPEN → CLOSED
 *          (正常)   (熔断)  (试探)      (恢复)
 */
public class CircuitBreaker {

    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final String name;
    private final int failureThreshold;
    private final int successThreshold;
    private final Duration openTimeout;

    private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicInteger successCount = new AtomicInteger(0);
    private volatile Instant openedAt;

    public CircuitBreaker(String name, int failureThreshold,
                          int successThreshold, Duration openTimeout) {
        this.name = name;
        this.failureThreshold = failureThreshold;
        this.successThreshold = successThreshold;
        this.openTimeout = openTimeout;
    }

    public <T> T execute(Supplier<T> action, Supplier<T> fallback) {
        if (!allowRequest()) {
            System.out.printf("[熔断器:%s] 状态=OPEN，执行降级%n", name);
            return fallback.get();
        }

        try {
            T result = action.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            if (state.get() == State.OPEN) {
                System.out.printf("[熔断器:%s] 失败次数达阈值，熔断器打开%n", name);
                return fallback.get();
            }
            throw e;
        }
    }

    private boolean allowRequest() {
        State currentState = state.get();
        if (currentState == State.CLOSED) {
            return true;
        }
        if (currentState == State.OPEN) {
            // 检查是否超过等待时间，可以进入半开状态
            if (Instant.now().isAfter(openedAt.plus(openTimeout))) {
                if (state.compareAndSet(State.OPEN, State.HALF_OPEN)) {
                    successCount.set(0);
                    System.out.printf("[熔断器:%s] 进入半开状态%n", name);
                }
                return true;
            }
            return false;
        }
        // HALF_OPEN: 允许有限请求通过
        return true;
    }

    private void onSuccess() {
        if (state.get() == State.HALF_OPEN) {
            int count = successCount.incrementAndGet();
            if (count >= successThreshold) {
                state.set(State.CLOSED);
                failureCount.set(0);
                System.out.printf("[熔断器:%s] 恢复正常，熔断器关闭%n", name);
            }
        } else {
            failureCount.set(0);
        }
    }

    private void onFailure() {
        int count = failureCount.incrementAndGet();
        if (state.get() == State.HALF_OPEN) {
            state.set(State.OPEN);
            openedAt = Instant.now();
        } else if (count >= failureThreshold) {
            state.set(State.OPEN);
            openedAt = Instant.now();
        }
    }

    public State getState() { return state.get(); }
    public int getFailureCount() { return failureCount.get(); }
}
```

### 舱壁隔离实现 (Bulkhead with Thread Pools)

```java
import java.util.concurrent.*;
import java.util.function.Supplier;

/**
 * 舱壁隔离 — 使用独立线程池隔离不同依赖的调用
 */
public class Bulkhead<T> {

    private final String name;
    private final ExecutorService executor;
    private final Semaphore semaphore;
    private final Duration timeout;

    public Bulkhead(String name, int maxConcurrency, int queueSize, Duration timeout) {
        this.name = name;
        this.timeout = timeout;
        this.semaphore = new Semaphore(maxConcurrency);
        this.executor = new ThreadPoolExecutor(
            maxConcurrency,                          // 核心线程数
            maxConcurrency,                          // 最大线程数
            60L, TimeUnit.SECONDS,                   // 空闲超时
            new ArrayBlockingQueue<>(queueSize),     // 有界队列
            new ThreadPoolExecutor.AbortPolicy()     // 队列满时拒绝
        );
    }

    public T execute(Callable<T> task, Supplier<T> fallback) {
        if (!semaphore.tryAcquire()) {
            System.out.printf("[舱壁:%s] 并发数已满，执行降级%n", name);
            return fallback.get();
        }

        try {
            Future<T> future = executor.submit(task);
            return future.get(timeout.toMillis(), TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            System.out.printf("[舱壁:%s] 执行超时，执行降级%n", name);
            return fallback.get();
        } catch (RejectedExecutionException e) {
            System.out.printf("[舱壁:%s] 线程池已满，执行降级%n", name);
            return fallback.get();
        } catch (ExecutionException e) {
            throw new RuntimeException("舱壁内部执行异常", e.getCause());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return fallback.get();
        } finally {
            semaphore.release();
        }
    }

    public void shutdown() {
        executor.shutdown();
    }
}
```

### 重试与退避实现 (Retry with Backoff)

```java
import java.time.Duration;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * 重试机制 — 支持指数退避和随机抖动
 */
public class Retry {

    private final int maxAttempts;
    private final Duration baseDelay;
    private final Duration maxDelay;
    private final Predicate<Exception> retryableCheck;

    public Retry(int maxAttempts, Duration baseDelay, Duration maxDelay,
                 Predicate<Exception> retryableCheck) {
        this.maxAttempts = maxAttempts;
        this.baseDelay = baseDelay;
        this.maxDelay = maxDelay;
        this.retryableCheck = retryableCheck;
    }

    public <T> T execute(Supplier<T> action) {
        Exception lastException = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                T result = action.get();
                if (attempt > 1) {
                    System.out.printf("[重试] 第%d次尝试成功%n", attempt);
                }
                return result;
            } catch (Exception e) {
                lastException = e;

                if (!retryableCheck.test(e)) {
                    throw new RuntimeException("不可重试的异常", e);
                }

                if (attempt < maxAttempts) {
                    Duration delay = calculateDelay(attempt);
                    System.out.printf("[重试] 第%d次失败，%dms后重试: %s%n",
                        attempt, delay.toMillis(), e.getMessage());
                    sleep(delay);
                }
            }
        }

        throw new RuntimeException(
            String.format("重试%d次后仍然失败", maxAttempts), lastException);
    }

    private Duration calculateDelay(int attempt) {
        // 指数退避: baseDelay * 2^(attempt-1)
        long exponentialMs = baseDelay.toMillis() * (1L << (attempt - 1));
        long cappedMs = Math.min(exponentialMs, maxDelay.toMillis());
        // 添加随机抖动: [0, cappedMs]
        long jitter = ThreadLocalRandom.current().nextLong(0, cappedMs + 1);
        return Duration.ofMillis(jitter);
    }

    private void sleep(Duration duration) {
        try {
            Thread.sleep(duration.toMillis());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // 构建器模式
    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private int maxAttempts = 3;
        private Duration baseDelay = Duration.ofMillis(200);
        private Duration maxDelay = Duration.ofSeconds(5);
        private Predicate<Exception> retryableCheck = e -> true;

        public Builder maxAttempts(int n) { this.maxAttempts = n; return this; }
        public Builder baseDelay(Duration d) { this.baseDelay = d; return this; }
        public Builder maxDelay(Duration d) { this.maxDelay = d; return this; }
        public Builder retryOn(Predicate<Exception> check) {
            this.retryableCheck = check; return this;
        }

        public Retry build() {
            return new Retry(maxAttempts, baseDelay, maxDelay, retryableCheck);
        }
    }
}
```

### 完整的弹性服务示例：无保护 vs 全保护

```java
// ❌ 无保护版本 — 任何故障都会导致整个服务不可用
public class FragileOrderService {

    private final PaymentClient paymentClient;
    private final InventoryClient inventoryClient;
    private final NotificationClient notificationClient;

    public OrderResult createOrder(Order order) {
        // 没有超时：paymentClient卡住 → 线程阻塞
        PaymentResult payment = paymentClient.charge(order.getAmount());

        // 没有重试：网络抖动 → 直接失败
        InventoryResult inventory = inventoryClient.reserve(order.getItems());

        // 没有隔离：notificationClient慢 → 影响所有订单
        notificationClient.sendConfirmation(order.getUserId());

        return new OrderResult(order.getId(), "SUCCESS");
    }
}
```

```java
// ✅ 全保护版本 — 具备完整的容错能力
public class ResilientOrderService {

    private final PaymentClient paymentClient;
    private final InventoryClient inventoryClient;
    private final NotificationClient notificationClient;

    // 每个依赖独立的熔断器
    private final CircuitBreaker paymentBreaker =
        new CircuitBreaker("payment", 5, 3, Duration.ofSeconds(30));
    private final CircuitBreaker inventoryBreaker =
        new CircuitBreaker("inventory", 3, 2, Duration.ofSeconds(15));
    private final CircuitBreaker notificationBreaker =
        new CircuitBreaker("notification", 3, 1, Duration.ofSeconds(10));

    // 每个依赖独立的舱壁
    private final Bulkhead<PaymentResult> paymentBulkhead =
        new Bulkhead<>("payment", 10, 20, Duration.ofSeconds(5));
    private final Bulkhead<InventoryResult> inventoryBulkhead =
        new Bulkhead<>("inventory", 8, 15, Duration.ofSeconds(3));

    // 重试策略
    private final Retry paymentRetry = Retry.builder()
        .maxAttempts(3)
        .baseDelay(Duration.ofMillis(500))
        .maxDelay(Duration.ofSeconds(5))
        .retryOn(e -> e instanceof java.net.SocketTimeoutException
                   || e instanceof java.io.IOException)
        .build();

    public OrderResult createOrder(Order order) {
        // 支付：舱壁 → 熔断器 → 重试 → 超时 → 降级
        PaymentResult payment = paymentBulkhead.execute(
            () -> paymentBreaker.execute(
                () -> paymentRetry.execute(
                    () -> paymentClient.chargeWithTimeout(
                        order.getAmount(), Duration.ofSeconds(5))),
                () -> PaymentResult.pending("支付排队中，稍后确认")
            ),
            () -> PaymentResult.pending("系统繁忙，支付稍后处理")
        );

        // 库存：舱壁 → 熔断器 → 超时 → 降级
        InventoryResult inventory = inventoryBulkhead.execute(
            () -> inventoryBreaker.execute(
                () -> inventoryClient.reserveWithTimeout(
                    order.getItems(), Duration.ofSeconds(3)),
                () -> InventoryResult.fromCache(order.getItems())
            ),
            () -> InventoryResult.fromCache(order.getItems())
        );

        // 通知：非关键路径，异步 + 熔断 + 静默降级
        CompletableFuture.runAsync(() -> {
            notificationBreaker.execute(
                () -> {
                    notificationClient.sendConfirmation(order.getUserId());
                    return null;
                },
                () -> null  // 通知失败不影响订单
            );
        });

        return new OrderResult(order.getId(),
            payment.isPending() ? "PENDING" : "SUCCESS");
    }
}
```

---

## Python 参考实现

### 熔断器装饰器 (Circuit Breaker Decorator)

```python
import time
import threading
from enum import Enum
from functools import wraps
from typing import Callable, Optional, TypeVar, Any

T = TypeVar('T')


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """熔断器打开时抛出的异常"""
    pass


class CircuitBreaker:
    """
    熔断器实现

    用法:
        breaker = CircuitBreaker("payment", failure_threshold=5)

        @breaker
        def call_payment(amount):
            return payment_client.charge(amount)
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        open_timeout: float = 30.0,
        fallback: Optional[Callable] = None,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.open_timeout = open_timeout
        self.fallback = fallback

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at: float = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._opened_at >= self.open_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
            return self._state

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(lambda: func(*args, **kwargs))
        wrapper.circuit_breaker = self
        return wrapper

    def execute(self, action: Callable[[], T]) -> T:
        current_state = self.state

        if current_state == CircuitState.OPEN:
            if self.fallback:
                return self.fallback()
            raise CircuitOpenError(
                f"熔断器 [{self.name}] 已打开，"
                f"将在 {self.open_timeout}s 后尝试恢复"
            )

        try:
            result = action()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if self.state == CircuitState.OPEN and self.fallback:
                return self.fallback()
            raise

    def _on_success(self):
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    print(f"[熔断器:{self.name}] 恢复正常")
            else:
                self._failure_count = 0

    def _on_failure(self):
        with self._lock:
            self._failure_count += 1
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = time.time()
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                self._opened_at = time.time()
                print(f"[熔断器:{self.name}] 打开! 失败次数={self._failure_count}")


# 使用示例
payment_breaker = CircuitBreaker(
    "payment",
    failure_threshold=5,
    success_threshold=3,
    open_timeout=30.0,
    fallback=lambda: {"status": "pending", "message": "支付排队中"},
)

@payment_breaker
def charge_payment(amount: float) -> dict:
    """带熔断器保护的支付调用"""
    return payment_client.charge(amount)
```

### 重试与退避 (Retry with Backoff)

```python
import time
import random
from functools import wraps
from typing import Callable, Type, Tuple, Optional

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 0.2,
    max_delay: float = 5.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    fallback: Optional[Callable] = None,
):
    """
    重试装饰器，支持指数退避和随机抖动

    用法:
        @retry_with_backoff(max_attempts=3, retryable_exceptions=(TimeoutError, ConnectionError))
        def call_api():
            return requests.get(url, timeout=3)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        print(f"[重试] {func.__name__} 第{attempt}次尝试成功")
                    return result
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        delay = _calculate_delay(attempt, base_delay, max_delay)
                        print(
                            f"[重试] {func.__name__} 第{attempt}次失败, "
                            f"{delay:.2f}s后重试: {e}"
                        )
                        time.sleep(delay)
                except Exception as e:
                    # 不可重试的异常，直接抛出
                    raise

            if fallback:
                print(f"[重试] {func.__name__} {max_attempts}次均失败，执行降级")
                return fallback(*args, **kwargs)

            raise RuntimeError(
                f"{func.__name__} 重试{max_attempts}次后失败"
            ) from last_exception

        return wrapper
    return decorator


def _calculate_delay(attempt: int, base_delay: float, max_delay: float) -> float:
    """指数退避 + 随机抖动"""
    exponential = base_delay * (2 ** (attempt - 1))
    capped = min(exponential, max_delay)
    jitter = random.uniform(0, capped)
    return jitter


# 使用示例
@retry_with_backoff(
    max_attempts=3,
    base_delay=0.5,
    max_delay=5.0,
    retryable_exceptions=(TimeoutError, ConnectionError, OSError),
    fallback=lambda user_id: {"recommendations": get_popular_items()},
)
def get_recommendations(user_id: str) -> dict:
    """获取推荐，带重试和降级"""
    response = requests.get(
        f"{RECOMMENDATION_URL}/users/{user_id}/recommendations",
        timeout=2,
    )
    response.raise_for_status()
    return response.json()
```

### 超时包装器 (Timeout Wrapper)

```python
import asyncio
from typing import TypeVar, Optional, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

T = TypeVar('T')

# --- 同步版本 ---

_executor = ThreadPoolExecutor(max_workers=20)

def call_with_timeout(
    func: Callable[..., T],
    timeout_seconds: float,
    *args,
    fallback: Optional[T] = None,
    **kwargs,
) -> T:
    """
    为同步函数添加超时控制

    用法:
        result = call_with_timeout(
            payment_client.charge, 3.0, amount=100,
            fallback=PaymentResult.pending()
        )
    """
    future = _executor.submit(func, *args, **kwargs)
    try:
        return future.result(timeout=timeout_seconds)
    except FuturesTimeout:
        future.cancel()
        if fallback is not None:
            print(f"[超时] {func.__name__} 超时({timeout_seconds}s)，执行降级")
            return fallback
        raise TimeoutError(f"{func.__name__} 在 {timeout_seconds}s 内未完成")


# --- 异步版本 ---

async def async_call_with_timeout(
    coro: Awaitable[T],
    timeout_seconds: float,
    fallback: Optional[T] = None,
) -> T:
    """
    为异步调用添加超时控制

    用法:
        result = await async_call_with_timeout(
            http_client.get(url),
            timeout_seconds=3.0,
            fallback=cached_data,
        )
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        if fallback is not None:
            print(f"[超时] 异步调用超时({timeout_seconds}s)，执行降级")
            return fallback
        raise


# --- 完整的弹性调用 ---

class ResilientCaller:
    """组合熔断器、重试、超时的弹性调用器"""

    def __init__(
        self,
        circuit_breaker: CircuitBreaker,
        max_retries: int = 3,
        timeout_seconds: float = 5.0,
    ):
        self.circuit_breaker = circuit_breaker
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def call(self, func: Callable[..., T], *args, fallback: T = None, **kwargs) -> T:
        """带完整容错保护的调用"""
        def action():
            @retry_with_backoff(
                max_attempts=self.max_retries,
                retryable_exceptions=(TimeoutError, ConnectionError),
            )
            def retried_call():
                return call_with_timeout(
                    func, self.timeout_seconds, *args, **kwargs
                )
            return retried_call()

        try:
            return self.circuit_breaker.execute(action)
        except (CircuitOpenError, RuntimeError):
            if fallback is not None:
                return fallback
            raise


# 使用示例
payment_caller = ResilientCaller(
    circuit_breaker=payment_breaker,
    max_retries=3,
    timeout_seconds=5.0,
)

result = payment_caller.call(
    payment_client.charge,
    amount=99.99,
    fallback={"status": "pending", "message": "支付排队中"},
)
```

---

## TypeScript 参考实现

### 熔断器类 (Circuit Breaker Class)

```typescript
enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

interface CircuitBreakerOptions {
  name: string;
  failureThreshold: number;
  successThreshold: number;
  openTimeoutMs: number;
}

class CircuitBreakerError extends Error {
  constructor(name: string) {
    super(`熔断器 [${name}] 已打开`);
    this.name = 'CircuitBreakerError';
  }
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private openedAt = 0;
  private readonly options: CircuitBreakerOptions;

  constructor(options: CircuitBreakerOptions) {
    this.options = options;
  }

  async execute<T>(action: () => Promise<T>, fallback?: () => Promise<T>): Promise<T> {
    if (!this.allowRequest()) {
      console.log(`[熔断器:${this.options.name}] OPEN, 执行降级`);
      if (fallback) return fallback();
      throw new CircuitBreakerError(this.options.name);
    }

    try {
      const result = await action();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      if (this.state === CircuitState.OPEN && fallback) {
        return fallback();
      }
      throw error;
    }
  }

  private allowRequest(): boolean {
    if (this.state === CircuitState.CLOSED) return true;

    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.openedAt >= this.options.openTimeoutMs) {
        this.state = CircuitState.HALF_OPEN;
        this.successCount = 0;
        console.log(`[熔断器:${this.options.name}] 进入半开状态`);
        return true;
      }
      return false;
    }

    return true; // HALF_OPEN
  }

  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= this.options.successThreshold) {
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        console.log(`[熔断器:${this.options.name}] 恢复正常`);
      }
    } else {
      this.failureCount = 0;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
      this.openedAt = Date.now();
    } else if (this.failureCount >= this.options.failureThreshold) {
      this.state = CircuitState.OPEN;
      this.openedAt = Date.now();
      console.log(
        `[熔断器:${this.options.name}] 打开! 失败次数=${this.failureCount}`
      );
    }
  }

  getState(): CircuitState {
    return this.state;
  }
}

// 使用示例
const paymentBreaker = new CircuitBreaker({
  name: 'payment',
  failureThreshold: 5,
  successThreshold: 3,
  openTimeoutMs: 30000,
});

async function chargePayment(amount: number): Promise<PaymentResult> {
  return paymentBreaker.execute(
    () => paymentClient.charge(amount),
    () => Promise.resolve({ status: 'pending', message: '支付排队中' }),
  );
}
```

### 超时请求 (fetchWithTimeout)

```typescript
class TimeoutError extends Error {
  constructor(url: string, timeoutMs: number) {
    super(`请求 ${url} 超时 (${timeoutMs}ms)`);
    this.name = 'TimeoutError';
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit & { timeoutMs?: number } = {},
): Promise<Response> {
  const { timeoutMs = 5000, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    return response;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new TimeoutError(url, timeoutMs);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * 带超时和降级的数据获取
 */
async function fetchWithFallback<T>(
  url: string,
  timeoutMs: number,
  fallback: T,
): Promise<T> {
  try {
    const response = await fetchWithTimeout(url, { timeoutMs });
    if (!response.ok) {
      console.warn(`[HTTP] ${url} 返回 ${response.status}，使用降级值`);
      return fallback;
    }
    return (await response.json()) as T;
  } catch (error) {
    console.warn(`[HTTP] ${url} 请求失败: ${error}，使用降级值`);
    return fallback;
  }
}

// 使用示例
const product = await fetchWithFallback<Product>(
  `${API_BASE}/products/${productId}`,
  3000,
  getCachedProduct(productId),
);
```

### 重试工具 (Retry Utility)

```typescript
interface RetryOptions {
  maxAttempts: number;
  baseDelayMs: number;
  maxDelayMs: number;
  retryOn?: (error: unknown) => boolean;
}

async function withRetry<T>(
  action: () => Promise<T>,
  options: RetryOptions,
): Promise<T> {
  const {
    maxAttempts,
    baseDelayMs,
    maxDelayMs,
    retryOn = () => true,
  } = options;
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await action();
      if (attempt > 1) {
        console.log(`[重试] 第${attempt}次尝试成功`);
      }
      return result;
    } catch (error) {
      lastError = error;

      if (!retryOn(error)) {
        throw error; // 不可重试
      }

      if (attempt < maxAttempts) {
        const delay = calculateBackoff(attempt, baseDelayMs, maxDelayMs);
        console.log(`[重试] 第${attempt}次失败, ${delay}ms后重试`);
        await sleep(delay);
      }
    }
  }

  throw new Error(`重试${maxAttempts}次后失败: ${lastError}`);
}

function calculateBackoff(
  attempt: number,
  baseDelayMs: number,
  maxDelayMs: number,
): number {
  const exponential = baseDelayMs * Math.pow(2, attempt - 1);
  const capped = Math.min(exponential, maxDelayMs);
  const jitter = Math.random() * capped;
  return Math.round(jitter);
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 使用示例
const data = await withRetry(
  () => fetchWithTimeout(`${API_BASE}/data`, { timeoutMs: 3000 }),
  {
    maxAttempts: 3,
    baseDelayMs: 500,
    maxDelayMs: 5000,
    retryOn: (error) =>
      error instanceof TimeoutError ||
      (error instanceof Error && error.message.includes('fetch')),
  },
);
```

### 完整的弹性服务示例 (TypeScript)

```typescript
// ✅ 组合所有容错模式的完整服务
class ResilientProductService {
  private readonly productBreaker = new CircuitBreaker({
    name: 'product-api',
    failureThreshold: 5,
    successThreshold: 3,
    openTimeoutMs: 30000,
  });

  private readonly reviewBreaker = new CircuitBreaker({
    name: 'review-api',
    failureThreshold: 3,
    successThreshold: 1,
    openTimeoutMs: 10000,
  });

  private readonly cache = new Map<string, { data: any; expiry: number }>();

  async getProductPage(productId: string): Promise<ProductPage> {
    // 商品详情 — 关键路径，熔断器 + 重试 + 超时 + 缓存降级
    const product = await this.productBreaker.execute(
      () =>
        withRetry(
          () =>
            fetchWithTimeout(`${API}/products/${productId}`, {
              timeoutMs: 3000,
            }).then(r => r.json()),
          {
            maxAttempts: 2,
            baseDelayMs: 200,
            maxDelayMs: 2000,
            retryOn: (e) => e instanceof TimeoutError,
          },
        ),
      () => this.getCached(`product:${productId}`, { id: productId, name: '加载中...' }),
    );

    // 缓存成功结果
    this.setCache(`product:${productId}`, product, 300000);

    // 评论 — 非关键路径，熔断器 + 超时 + 静默降级
    const reviews = await this.reviewBreaker.execute(
      () =>
        fetchWithFallback<Review[]>(
          `${API}/products/${productId}/reviews`,
          2000,
          [],
        ),
      () => Promise.resolve([]),  // 评论不可用时返回空数组
    );

    // 推荐 — 非关键路径，超时 + 降级
    const recommendations = await fetchWithFallback<Product[]>(
      `${API}/products/${productId}/recommendations`,
      1500,
      await this.getPopularProducts(),
    );

    return { product, reviews, recommendations };
  }

  private getCached<T>(key: string, defaultValue: T): Promise<T> {
    const entry = this.cache.get(key);
    if (entry && entry.expiry > Date.now()) {
      return Promise.resolve(entry.data as T);
    }
    return Promise.resolve(defaultValue);
  }

  private setCache(key: string, data: any, ttlMs: number): void {
    this.cache.set(key, { data, expiry: Date.now() + ttlMs });
  }

  private async getPopularProducts(): Promise<Product[]> {
    return this.getCached('popular-products', []);
  }
}
```

---

## 单元测试示例

### Java 测试

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CircuitBreakerTest {

    @Test
    void shouldOpenAfterFailureThreshold() {
        CircuitBreaker breaker = new CircuitBreaker("test", 3, 2, Duration.ofSeconds(5));
        assertEquals(CircuitBreaker.State.CLOSED, breaker.getState());

        // 连续失败3次
        for (int i = 0; i < 3; i++) {
            assertThrows(RuntimeException.class, () ->
                breaker.execute(
                    () -> { throw new RuntimeException("模拟故障"); },
                    () -> "fallback"
                )
            );
        }

        // 此时应该触发降级而不是异常（因为有fallback）
        // 重新创建以验证状态
        CircuitBreaker breaker2 = new CircuitBreaker("test2", 3, 2, Duration.ofSeconds(5));
        for (int i = 0; i < 3; i++) {
            String result = breaker2.execute(
                () -> { throw new RuntimeException("模拟故障"); },
                () -> "fallback"
            );
        }
        assertEquals(CircuitBreaker.State.OPEN, breaker2.getState());
    }

    @Test
    void shouldReturnFallbackWhenOpen() {
        CircuitBreaker breaker = new CircuitBreaker("test", 2, 1, Duration.ofSeconds(60));

        // 触发熔断
        for (int i = 0; i < 2; i++) {
            breaker.execute(
                () -> { throw new RuntimeException("故障"); },
                () -> "fallback"
            );
        }

        // 熔断后应直接返回 fallback，不调用 action
        String result = breaker.execute(
            () -> { fail("不应该调用 action"); return "action"; },
            () -> "fallback"
        );
        assertEquals("fallback", result);
    }

    @Test
    void shouldRecoverAfterTimeout() throws InterruptedException {
        CircuitBreaker breaker = new CircuitBreaker("test", 2, 1, Duration.ofMillis(100));

        // 触发熔断
        for (int i = 0; i < 2; i++) {
            breaker.execute(
                () -> { throw new RuntimeException("故障"); },
                () -> "fallback"
            );
        }
        assertEquals(CircuitBreaker.State.OPEN, breaker.getState());

        // 等待超时
        Thread.sleep(150);

        // 应进入半开状态，允许请求通过
        String result = breaker.execute(() -> "success", () -> "fallback");
        assertEquals("success", result);
        assertEquals(CircuitBreaker.State.CLOSED, breaker.getState());
    }
}

class RetryTest {

    @Test
    void shouldRetryAndSucceed() {
        var callCount = new AtomicInteger(0);
        Retry retry = Retry.builder()
            .maxAttempts(3)
            .baseDelay(Duration.ofMillis(10))
            .build();

        String result = retry.execute(() -> {
            if (callCount.incrementAndGet() < 3) {
                throw new RuntimeException("暂时失败");
            }
            return "success";
        });

        assertEquals("success", result);
        assertEquals(3, callCount.get());
    }

    @Test
    void shouldNotRetryNonRetryableException() {
        Retry retry = Retry.builder()
            .maxAttempts(3)
            .retryOn(e -> e instanceof java.io.IOException)
            .build();

        assertThrows(RuntimeException.class, () ->
            retry.execute(() -> {
                throw new IllegalArgumentException("参数错误");
            })
        );
    }
}

class BulkheadTest {

    @Test
    void shouldRejectWhenFull() throws Exception {
        Bulkhead<String> bulkhead = new Bulkhead<>("test", 1, 1, Duration.ofSeconds(5));

        // 占用唯一的槽位
        CountDownLatch latch = new CountDownLatch(1);
        bulkhead.execute(() -> { latch.await(); return "blocking"; }, () -> "fallback");

        // 第二个请求应被拒绝
        // 注：实际测试需要异步执行第一个，这里简化演示
    }
}
```

### Python 测试

```python
import pytest
import time

class TestCircuitBreaker:
    def test_should_open_after_threshold(self):
        breaker = CircuitBreaker("test", failure_threshold=3, success_threshold=2)
        assert breaker.state == CircuitState.CLOSED

        for _ in range(3):
            with pytest.raises(RuntimeError):
                breaker.execute(lambda: (_ for _ in ()).throw(RuntimeError("故障")))

        assert breaker.state == CircuitState.OPEN

    def test_should_call_fallback_when_open(self):
        breaker = CircuitBreaker(
            "test",
            failure_threshold=2,
            fallback=lambda: "降级结果",
        )

        for _ in range(2):
            try:
                breaker.execute(lambda: (_ for _ in ()).throw(RuntimeError("故障")))
            except RuntimeError:
                pass

        result = breaker.execute(lambda: "不应该被调用")
        assert result == "降级结果"

    def test_should_recover_after_timeout(self):
        breaker = CircuitBreaker(
            "test",
            failure_threshold=2,
            open_timeout=0.1,
        )

        for _ in range(2):
            try:
                breaker.execute(lambda: (_ for _ in ()).throw(RuntimeError("故障")))
            except RuntimeError:
                pass

        assert breaker.state == CircuitState.OPEN

        time.sleep(0.15)
        result = breaker.execute(lambda: "恢复成功")
        assert result == "恢复成功"


class TestRetryWithBackoff:
    def test_should_retry_and_succeed(self):
        call_count = 0

        @retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            retryable_exceptions=(RuntimeError,),
        )
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("暂时失败")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_should_not_retry_non_retryable(self):
        @retry_with_backoff(
            max_attempts=3,
            retryable_exceptions=(ConnectionError,),
        )
        def bad_request():
            raise ValueError("参数错误")

        with pytest.raises(ValueError):
            bad_request()

    def test_should_use_fallback_after_exhaustion(self):
        @retry_with_backoff(
            max_attempts=2,
            base_delay=0.01,
            fallback=lambda: "降级结果",
        )
        def always_fail():
            raise RuntimeError("持续失败")

        result = always_fail()
        assert result == "降级结果"


class TestCallWithTimeout:
    def test_should_timeout_slow_function(self):
        def slow():
            time.sleep(10)
            return "done"

        result = call_with_timeout(slow, 0.1, fallback="超时降级")
        assert result == "超时降级"

    def test_should_return_result_for_fast_function(self):
        def fast():
            return "fast result"

        result = call_with_timeout(fast, 5.0)
        assert result == "fast result"
```

### TypeScript 测试

```typescript
import { describe, it, expect, vi } from 'vitest';

describe('CircuitBreaker', () => {
  it('should open after failure threshold', async () => {
    const breaker = new CircuitBreaker({
      name: 'test',
      failureThreshold: 3,
      successThreshold: 2,
      openTimeoutMs: 30000,
    });

    const failingAction = () => Promise.reject(new Error('故障'));

    for (let i = 0; i < 3; i++) {
      await breaker.execute(failingAction, () => Promise.resolve('fallback'));
    }

    expect(breaker.getState()).toBe(CircuitState.OPEN);
  });

  it('should return fallback when open', async () => {
    const breaker = new CircuitBreaker({
      name: 'test',
      failureThreshold: 2,
      successThreshold: 1,
      openTimeoutMs: 30000,
    });

    const fail = () => Promise.reject(new Error('故障'));
    const fallback = () => Promise.resolve('降级');

    for (let i = 0; i < 2; i++) {
      await breaker.execute(fail, fallback);
    }

    const action = vi.fn(() => Promise.resolve('不应调用'));
    const result = await breaker.execute(action, fallback);

    expect(result).toBe('降级');
    expect(action).not.toHaveBeenCalled();
  });

  it('should recover after timeout', async () => {
    vi.useFakeTimers();
    const breaker = new CircuitBreaker({
      name: 'test',
      failureThreshold: 2,
      successThreshold: 1,
      openTimeoutMs: 5000,
    });

    const fail = () => Promise.reject(new Error('故障'));
    for (let i = 0; i < 2; i++) {
      await breaker.execute(fail, () => Promise.resolve('fallback'));
    }

    vi.advanceTimersByTime(6000);

    const result = await breaker.execute(
      () => Promise.resolve('恢复'),
      () => Promise.resolve('fallback'),
    );
    expect(result).toBe('恢复');
    expect(breaker.getState()).toBe(CircuitState.CLOSED);

    vi.useRealTimers();
  });
});

describe('withRetry', () => {
  it('should retry and succeed', async () => {
    let attempt = 0;
    const result = await withRetry(
      async () => {
        attempt++;
        if (attempt < 3) throw new Error('暂时失败');
        return 'success';
      },
      { maxAttempts: 3, baseDelayMs: 10, maxDelayMs: 100 },
    );

    expect(result).toBe('success');
    expect(attempt).toBe(3);
  });

  it('should not retry non-retryable errors', async () => {
    await expect(
      withRetry(
        async () => { throw new TypeError('参数错误'); },
        {
          maxAttempts: 3,
          baseDelayMs: 10,
          maxDelayMs: 100,
          retryOn: (e) => e instanceof TimeoutError,
        },
      ),
    ).rejects.toThrow(TypeError);
  });
});

describe('fetchWithTimeout', () => {
  it('should abort on timeout', async () => {
    vi.useFakeTimers();
    const promise = fetchWithTimeout('https://slow.api/data', { timeoutMs: 1000 });
    vi.advanceTimersByTime(1100);
    await expect(promise).rejects.toThrow(TimeoutError);
    vi.useRealTimers();
  });
});
```

---

## 总结

### 容错模式速查表

| 模式 | 解决的问题 | 关键参数 | 适用场景 |
|------|-----------|----------|----------|
| **超时** | 无限等待 | 超时时间 (基于P99) | 所有外部调用 |
| **重试** | 瞬时故障 | 次数、延迟、抖动 | 网络抖动、临时不可用 |
| **熔断器** | 持续故障 | 失败阈值、恢复时间 | 依赖服务持续异常 |
| **舱壁** | 资源耗尽 | 并发数、队列大小 | 多依赖共享资源池 |
| **降级** | 功能不可用 | 降级数据、触发条件 | 非关键功能故障 |
| **负载脱落** | 过载 | 容量阈值、优先级 | 流量超出系统容量 |

### 设计原则

1. **按依赖重要性分级保护** — 关键依赖需要完整的容错链（舱壁+熔断+重试+超时+降级），非关键依赖可以简化
2. **超时是最基础的容错** — 没有超时，其他所有模式都可能失效
3. **重试必须带退避和抖动** — 否则会造成重试风暴
4. **降级方案必须有兜底** — 降级本身也可能失败，需要最终安全默认值
5. **容错机制需要可观测** — 所有熔断、重试、降级事件都应有监控和告警
6. **定期进行混沌工程验证** — 容错机制不经过实际故障验证就不可信

### 实施优先级

```
第1步: 为所有外部调用添加超时         ← 成本最低，收益最高
第2步: 为关键依赖添加熔断器           ← 防止级联故障
第3步: 实现舱壁隔离                   ← 防止资源耗尽
第4步: 添加重试（带退避和抖动）        ← 处理瞬时故障
第5步: 设计降级方案                   ← 保障用户体验
第6步: 建立混沌工程实践               ← 持续验证和改进
```
