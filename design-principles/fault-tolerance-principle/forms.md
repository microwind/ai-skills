# 容错性原则 - 诊断与规划表

> 系统化诊断容错缺陷，规划改进方案，构建弹性系统。

---

## 第1步: 需求诊断

### 容错性缺陷检查清单

逐项检查当前系统，标记存在的问题：

| # | 检查项 | 风险等级 | 是否存在 |
|---|--------|----------|----------|
| 1 | **无超时设置** — 外部调用没有超时限制，可能无限阻塞 | 🔴 高 | ☐ |
| 2 | **无重试机制** — 瞬时故障直接导致请求失败 | 🟡 中 | ☐ |
| 3 | **级联故障** — 一个服务故障导致整个调用链崩溃 | 🔴 高 | ☐ |
| 4 | **无熔断器** — 持续调用已故障的服务，浪费资源 | 🔴 高 | ☐ |
| 5 | **无舱壁隔离** — 一个慢依赖耗尽所有线程/连接 | 🔴 高 | ☐ |
| 6 | **无降级方案** — 依赖不可用时没有备选逻辑 | 🟡 中 | ☐ |

### 诊断示例

```java
// ❌ 无任何容错保护的调用
public class OrderService {
    private final PaymentClient paymentClient;
    private final InventoryClient inventoryClient;

    public OrderResult createOrder(Order order) {
        // 没有超时 — 如果 paymentClient 卡住，线程永远阻塞
        PaymentResult payment = paymentClient.charge(order.getAmount());

        // 没有重试 — 网络抖动直接失败
        InventoryResult inventory = inventoryClient.reserve(order.getItems());

        // 没有降级 — 任何一个失败整个订单就失败
        if (!payment.isSuccess() || !inventory.isSuccess()) {
            throw new OrderFailedException("下单失败");
        }
        return new OrderResult(order.getId(), "SUCCESS");
    }
}
```

```python
# ❌ 无容错保护
class RecommendationService:
    def __init__(self, ml_client, cache_client):
        self.ml_client = ml_client
        self.cache_client = cache_client

    def get_recommendations(self, user_id: str) -> list:
        # 没有超时，没有熔断，没有降级
        features = self.ml_client.get_features(user_id)
        predictions = self.ml_client.predict(features)
        self.cache_client.set(f"rec:{user_id}", predictions)
        return predictions
```

```typescript
// ❌ 无容错保护
class ProductService {
  async getProductDetails(productId: string): Promise<Product> {
    // 没有超时，没有重试
    const response = await fetch(`${this.apiUrl}/products/${productId}`);
    if (!response.ok) {
      throw new Error(`获取产品失败: ${response.status}`);
    }
    return response.json();
  }
}
```

### 风险评分

- 勾选 0-1 项：系统容错性较好，关注细节优化
- 勾选 2-3 项：存在明显风险，需要尽快改进
- 勾选 4-6 项：系统脆弱，任何外部故障都可能导致严重事故

---

## 第2步: 故障模式识别

### 方法一：故障模式分析 (Failure Mode Analysis)

列出每个外部依赖，分析其可能的故障模式：

| 依赖 | 故障模式 | 发生概率 | 影响范围 | 当前保护 |
|------|----------|----------|----------|----------|
| 支付服务 | 超时 / 拒绝 / 返回错误 | 中 | 订单流程阻塞 | 无 |
| 数据库 | 连接耗尽 / 慢查询 | 低 | 全部功能不可用 | 无 |
| 缓存 | 连接断开 / 数据丢失 | 中 | 性能下降 | 无 |
| 消息队列 | 消息堆积 / 不可用 | 低 | 异步任务延迟 | 无 |

```java
// 故障模式分析工具类
public class FailureModeAnalyzer {

    public record Dependency(String name, List<FailureMode> modes) {}

    public record FailureMode(
        String type,          // TIMEOUT, ERROR, SLOW, UNAVAILABLE
        String probability,   // HIGH, MEDIUM, LOW
        String blastRadius,   // 影响范围
        String currentProtection
    ) {}

    public static List<Dependency> analyzeDependencies() {
        return List.of(
            new Dependency("PaymentService", List.of(
                new FailureMode("TIMEOUT", "MEDIUM", "订单创建阻塞", "无"),
                new FailureMode("ERROR", "LOW", "支付失败", "简单重试"),
                new FailureMode("SLOW", "MEDIUM", "线程池耗尽", "无")
            )),
            new Dependency("InventoryService", List.of(
                new FailureMode("UNAVAILABLE", "LOW", "无法下单", "无"),
                new FailureMode("SLOW", "MEDIUM", "级联延迟", "无")
            ))
        );
    }
}
```

### 方法二：依赖链分析 (Dependency Chain Analysis)

绘制服务依赖关系，识别关键路径和单点故障：

```
用户请求
  → API网关
    → 订单服务 (关键)
      → 支付服务 (关键) → 银行接口 (外部)
      → 库存服务 (关键) → 数据库
      → 通知服务 (非关键) → 邮件服务 (外部)
      → 推荐服务 (非关键) → ML模型服务
```

```python
# 依赖链分析
from dataclasses import dataclass, field
from enum import Enum

class Criticality(Enum):
    CRITICAL = "关键"    # 故障导致功能完全不可用
    IMPORTANT = "重要"   # 故障导致功能降级
    OPTIONAL = "可选"    # 故障不影响核心功能

@dataclass
class DependencyNode:
    name: str
    criticality: Criticality
    timeout_ms: int = 0
    has_circuit_breaker: bool = False
    has_fallback: bool = False
    children: list['DependencyNode'] = field(default_factory=list)

    def audit(self, path: str = "") -> list[str]:
        """审计依赖链，返回问题列表"""
        issues = []
        current_path = f"{path} → {self.name}" if path else self.name

        if self.criticality == Criticality.CRITICAL:
            if self.timeout_ms == 0:
                issues.append(f"[严重] {current_path}: 关键依赖无超时")
            if not self.has_circuit_breaker:
                issues.append(f"[严重] {current_path}: 关键依赖无熔断器")
            if not self.has_fallback:
                issues.append(f"[警告] {current_path}: 关键依赖无降级方案")

        for child in self.children:
            issues.extend(child.audit(current_path))
        return issues

# 使用示例
order_service = DependencyNode(
    name="订单服务",
    criticality=Criticality.CRITICAL,
    children=[
        DependencyNode("支付服务", Criticality.CRITICAL, timeout_ms=0),
        DependencyNode("库存服务", Criticality.CRITICAL, timeout_ms=3000),
        DependencyNode("通知服务", Criticality.OPTIONAL, has_fallback=True),
    ]
)

for issue in order_service.audit():
    print(issue)
```

### 方法三：爆炸半径评估 (Blast Radius Assessment)

```typescript
// 评估故障影响范围
interface BlastRadiusReport {
  dependency: string;
  failureMode: string;
  affectedServices: string[];
  affectedUsers: string;  // 百分比
  revenueImpact: 'HIGH' | 'MEDIUM' | 'LOW';
  mitigationPlan: string;
}

function assessBlastRadius(dependency: string): BlastRadiusReport {
  const assessments: Record<string, BlastRadiusReport> = {
    'payment-service': {
      dependency: 'payment-service',
      failureMode: '超时或不可用',
      affectedServices: ['order-service', 'subscription-service', 'refund-service'],
      affectedUsers: '100% 付费用户',
      revenueImpact: 'HIGH',
      mitigationPlan: '实现熔断器 + 支付队列异步化',
    },
    'recommendation-service': {
      dependency: 'recommendation-service',
      failureMode: 'ML模型响应慢',
      affectedServices: ['product-page', 'home-page'],
      affectedUsers: '所有浏览用户',
      revenueImpact: 'LOW',
      mitigationPlan: '降级为热门商品列表',
    },
  };
  return assessments[dependency]!;
}
```

---

## 第3步: 容错改进规划

### 步骤 1: 添加超时 (Timeouts)

所有外部调用必须设置超时，超时时间基于 P99 延迟设定。

```java
// ✅ 为所有外部调用添加超时
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class TimeoutConfig {

    // 根据依赖的 P99 延迟设定超时
    // 规则：超时 = P99 延迟 × 2，但不超过业务可接受上限
    public static final Duration PAYMENT_TIMEOUT = Duration.ofSeconds(5);
    public static final Duration INVENTORY_TIMEOUT = Duration.ofSeconds(3);
    public static final Duration NOTIFICATION_TIMEOUT = Duration.ofSeconds(2);

    public static HttpClient createHttpClient(Duration connectTimeout) {
        return HttpClient.newBuilder()
            .connectTimeout(connectTimeout)
            .build();
    }

    public static HttpRequest.Builder withTimeout(
            HttpRequest.Builder builder, Duration readTimeout) {
        return builder.timeout(readTimeout);
    }
}
```

```python
# ✅ 超时包装器
import asyncio
import signal
from functools import wraps

def with_timeout(seconds: float, fallback=None):
    """同步函数超时装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"{func.__name__} 超时 ({seconds}s)")
            old = signal.signal(signal.SIGALRM, handler)
            signal.setitimer(signal.ITIMER_REAL, seconds)
            try:
                return func(*args, **kwargs)
            except TimeoutError:
                if fallback is not None:
                    return fallback
                raise
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)
        return wrapper
    return decorator

async def async_with_timeout(coro, seconds: float, fallback=None):
    """异步调用超时包装"""
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        if fallback is not None:
            return fallback
        raise
```

### 步骤 2: 实现熔断器 (Circuit Breaker)

当故障率超过阈值时自动断开，避免持续调用已故障的服务。

```typescript
// ✅ 熔断器配置规划
interface CircuitBreakerPlan {
  service: string;
  failureThreshold: number;     // 触发熔断的失败次数
  successThreshold: number;     // 恢复所需的成功次数
  timeoutMs: number;            // 半开状态等待时间
  fallbackStrategy: string;
}

const circuitBreakerPlans: CircuitBreakerPlan[] = [
  {
    service: 'payment-service',
    failureThreshold: 5,
    successThreshold: 3,
    timeoutMs: 30000,
    fallbackStrategy: '将支付请求放入队列，稍后重试',
  },
  {
    service: 'inventory-service',
    failureThreshold: 3,
    successThreshold: 2,
    timeoutMs: 15000,
    fallbackStrategy: '使用缓存中的库存数据（标记为近似值）',
  },
  {
    service: 'recommendation-service',
    failureThreshold: 3,
    successThreshold: 1,
    timeoutMs: 10000,
    fallbackStrategy: '返回热门商品列表',
  },
];
```

### 步骤 3: 设计舱壁隔离 (Bulkheads)

将不同的依赖调用隔离到独立的资源池，防止一个慢依赖耗尽所有资源。

```java
// ✅ 舱壁隔离规划
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;

public class BulkheadConfig {

    // 每个依赖使用独立的线程池
    public static final ExecutorService PAYMENT_POOL =
        Executors.newFixedThreadPool(10);      // 最多10个并发支付调用

    public static final ExecutorService INVENTORY_POOL =
        Executors.newFixedThreadPool(8);       // 最多8个并发库存调用

    public static final ExecutorService NOTIFICATION_POOL =
        Executors.newFixedThreadPool(5);       // 最多5个并发通知调用

    // 信号量隔离 — 限制并发数但不创建新线程
    public static final Semaphore PAYMENT_SEMAPHORE = new Semaphore(10);
    public static final Semaphore INVENTORY_SEMAPHORE = new Semaphore(8);

    public static <T> T executeWithBulkhead(
            Semaphore semaphore, java.util.concurrent.Callable<T> task)
            throws Exception {
        if (!semaphore.tryAcquire(100, java.util.concurrent.TimeUnit.MILLISECONDS)) {
            throw new BulkheadFullException("舱壁已满，请求被拒绝");
        }
        try {
            return task.call();
        } finally {
            semaphore.release();
        }
    }
}
```

### 步骤 4: 规划重试策略 (Retry Strategy)

```python
# ✅ 重试策略规划
from dataclasses import dataclass
from enum import Enum

class RetryPolicy(Enum):
    NO_RETRY = "不重试"
    FIXED_DELAY = "固定延迟"
    EXPONENTIAL_BACKOFF = "指数退避"
    EXPONENTIAL_WITH_JITTER = "指数退避+抖动"

@dataclass
class RetryPlan:
    service: str
    policy: RetryPolicy
    max_attempts: int
    base_delay_ms: int
    max_delay_ms: int
    retryable_exceptions: list[str]
    non_retryable_exceptions: list[str]

retry_plans = [
    RetryPlan(
        service="支付服务",
        policy=RetryPolicy.EXPONENTIAL_WITH_JITTER,
        max_attempts=3,
        base_delay_ms=500,
        max_delay_ms=5000,
        retryable_exceptions=["TimeoutError", "ConnectionError", "HTTP 503"],
        non_retryable_exceptions=["HTTP 400", "HTTP 401", "HTTP 409"],
    ),
    RetryPlan(
        service="库存服务",
        policy=RetryPolicy.EXPONENTIAL_BACKOFF,
        max_attempts=2,
        base_delay_ms=200,
        max_delay_ms=2000,
        retryable_exceptions=["TimeoutError", "ConnectionError"],
        non_retryable_exceptions=["HTTP 4xx"],
    ),
    RetryPlan(
        service="通知服务",
        policy=RetryPolicy.NO_RETRY,
        max_attempts=1,
        base_delay_ms=0,
        max_delay_ms=0,
        retryable_exceptions=[],
        non_retryable_exceptions=["所有异常 — 通知失败不应阻塞主流程"],
    ),
]
```

### 步骤 5: 设计优雅降级 (Graceful Degradation)

```typescript
// ✅ 降级策略规划
interface DegradationPlan {
  feature: string;
  normalBehavior: string;
  degradedBehavior: string;
  trigger: string;
  userNotification: string;
}

const degradationPlans: DegradationPlan[] = [
  {
    feature: '商品推荐',
    normalBehavior: 'ML模型个性化推荐',
    degradedBehavior: '返回热门商品缓存',
    trigger: '推荐服务熔断器打开',
    userNotification: '不通知，用户无感知',
  },
  {
    feature: '实时库存',
    normalBehavior: '实时查询库存数量',
    degradedBehavior: '显示"库存充足/紧张"而非具体数字',
    trigger: '库存服务响应 > 2s 或不可用',
    userNotification: '显示"库存信息可能有延迟"',
  },
  {
    feature: '订单创建',
    normalBehavior: '同步支付 + 同步扣库存',
    degradedBehavior: '接受订单，异步处理支付和库存',
    trigger: '支付或库存服务部分不可用',
    userNotification: '显示"订单处理中，稍后通知结果"',
  },
  {
    feature: '用户评论',
    normalBehavior: '实时加载评论列表',
    degradedBehavior: '显示"评论暂时不可用"',
    trigger: '评论服务不可用',
    userNotification: '页面提示"评论加载失败，请稍后刷新"',
  },
];
```

---

## 第4步: 测试计划

### 故障注入测试 (Fault Injection)

```java
// 故障注入测试框架
public class FaultInjector {

    public enum FaultType {
        LATENCY,        // 注入延迟
        EXCEPTION,      // 注入异常
        TIMEOUT,        // 模拟超时
        PARTIAL_FAILURE // 部分失败（如50%请求失败）
    }

    private final Map<String, FaultConfig> activeFaults = new ConcurrentHashMap<>();

    public record FaultConfig(FaultType type, double probability, Duration duration) {}

    public void injectFault(String service, FaultConfig config) {
        activeFaults.put(service, config);
    }

    public void clearFault(String service) {
        activeFaults.remove(service);
    }

    public <T> T executeWithFaultInjection(
            String service, Callable<T> action) throws Exception {
        FaultConfig fault = activeFaults.get(service);
        if (fault == null) {
            return action.call();
        }

        if (Math.random() < fault.probability()) {
            switch (fault.type()) {
                case LATENCY:
                    Thread.sleep(fault.duration().toMillis());
                    break;
                case EXCEPTION:
                    throw new RuntimeException("注入故障: " + service + " 不可用");
                case TIMEOUT:
                    Thread.sleep(fault.duration().toMillis());
                    throw new java.util.concurrent.TimeoutException("注入超时");
                case PARTIAL_FAILURE:
                    throw new RuntimeException("注入部分故障");
            }
        }
        return action.call();
    }
}

// 测试示例
class FaultToleranceTest {
    @Test
    void testCircuitBreakerOpensOnRepeatedFailures() {
        FaultInjector injector = new FaultInjector();
        injector.injectFault("payment-service",
            new FaultConfig(FaultType.EXCEPTION, 1.0, Duration.ZERO));

        OrderService service = new OrderService(injector);

        // 连续失败应触发熔断
        for (int i = 0; i < 5; i++) {
            assertThrows(ServiceUnavailableException.class,
                () -> service.createOrder(testOrder));
        }

        // 熔断器打开后应快速失败（不再实际调用）
        long start = System.currentTimeMillis();
        assertThrows(CircuitOpenException.class,
            () -> service.createOrder(testOrder));
        long elapsed = System.currentTimeMillis() - start;
        assertTrue(elapsed < 50, "熔断器应快速失败");
    }
}
```

### 混沌工程测试 (Chaos Engineering)

```python
# 混沌工程测试计划
import random
from dataclasses import dataclass

@dataclass
class ChaosExperiment:
    name: str
    hypothesis: str
    injection: str
    expected_behavior: str
    rollback_plan: str
    blast_radius: str

chaos_experiments = [
    ChaosExperiment(
        name="支付服务全部超时",
        hypothesis="熔断器在5次失败后打开，订单进入异步队列",
        injection="在支付服务前的网关注入3s延迟",
        expected_behavior="用户看到'订单处理中'而非错误页面",
        rollback_plan="移除网关延迟规则",
        blast_radius="仅影响新订单，已有订单不受影响",
    ),
    ChaosExperiment(
        name="数据库连接池耗尽",
        hypothesis="舱壁隔离确保读操作不被写操作阻塞",
        injection="人为占用80%写连接池",
        expected_behavior="读操作正常，写操作排队或降级",
        rollback_plan="释放占用的连接",
        blast_radius="仅影响写操作",
    ),
    ChaosExperiment(
        name="缓存层完全不可用",
        hypothesis="系统自动降级到数据库直读，响应变慢但不中断",
        injection="关闭Redis实例",
        expected_behavior="P99延迟升高但无错误",
        rollback_plan="重启Redis实例",
        blast_radius="全站性能降级",
    ),
]

def run_chaos_experiment(experiment: ChaosExperiment):
    """执行混沌实验"""
    print(f"🧪 实验: {experiment.name}")
    print(f"📋 假设: {experiment.hypothesis}")
    print(f"💉 注入: {experiment.injection}")
    print(f"🎯 预期: {experiment.expected_behavior}")
    print(f"🔙 回滚: {experiment.rollback_plan}")
    print(f"💥 影响: {experiment.blast_radius}")
```

### 测试检查清单

| # | 测试场景 | 测试方法 | 通过标准 | 状态 |
|---|---------|----------|----------|------|
| 1 | 单个依赖超时 | 故障注入 | 请求在超时时间内返回降级结果 | ☐ |
| 2 | 单个依赖持续失败 | 故障注入 | 熔断器打开，快速失败 | ☐ |
| 3 | 多个依赖同时故障 | 混沌工程 | 系统核心功能可用 | ☐ |
| 4 | 故障恢复后系统恢复 | 混沌工程 | 熔断器自动关闭，流量恢复 | ☐ |
| 5 | 高并发下的故障 | 压力测试+故障注入 | 舱壁隔离有效，无级联故障 | ☐ |
| 6 | 重试风暴 | 故障注入+监控 | 重试次数在预期范围内 | ☐ |
| 7 | 降级路径正确性 | 集成测试 | 降级数据符合业务要求 | ☐ |

---

## 第5步: 代码审查指南

### 审查要点

在代码审查中，关注以下容错相关问题：

**1. 外部调用检查**

```java
// 审查问题：这个HTTP调用有超时吗？
// ❌ 无超时
HttpResponse<String> resp = client.send(request, BodyHandlers.ofString());

// ✅ 有超时
HttpRequest req = HttpRequest.newBuilder()
    .uri(uri)
    .timeout(Duration.ofSeconds(3))
    .build();
HttpResponse<String> resp = client.send(req, BodyHandlers.ofString());
```

**2. 异常处理检查**

```python
# 审查问题：异常处理是否区分了可重试和不可重试错误？
# ❌ 一刀切
try:
    result = api_client.call()
except Exception:
    raise ServiceError("调用失败")

# ✅ 区分处理
try:
    result = api_client.call()
except ConnectionError:
    # 可重试 — 网络问题
    return retry_or_fallback()
except ValueError:
    # 不可重试 — 参数错误
    raise BadRequestError("请求参数错误")
except TimeoutError:
    # 可重试 — 超时
    return retry_or_fallback()
```

**3. 资源限制检查**

```typescript
// 审查问题：并发调用是否有限制？
// ❌ 无限制
async function processItems(items: Item[]): Promise<Result[]> {
  return Promise.all(items.map(item => callExternalService(item)));
}

// ✅ 限制并发
async function processItems(items: Item[]): Promise<Result[]> {
  const CONCURRENCY_LIMIT = 10;
  const results: Result[] = [];
  for (let i = 0; i < items.length; i += CONCURRENCY_LIMIT) {
    const batch = items.slice(i, i + CONCURRENCY_LIMIT);
    const batchResults = await Promise.all(
      batch.map(item => callExternalService(item))
    );
    results.push(...batchResults);
  }
  return results;
}
```

**4. 降级逻辑检查**

审查每个外部依赖调用是否有对应的降级方案，降级数据是否满足业务最低要求。

**5. 监控与告警检查**

确认关键容错组件（熔断器、重试、降级）有对应的监控指标和告警规则。

---

## 常见陷阱预防

### 陷阱 1: 重试风暴 (Retry Storm)

```java
// ❌ 所有实例同时重试，加剧服务端压力
public <T> T retryBad(Supplier<T> action, int maxRetries) {
    for (int i = 0; i < maxRetries; i++) {
        try {
            return action.get();
        } catch (Exception e) {
            // 固定延迟，所有客户端同步重试
            Thread.sleep(1000);
        }
    }
    throw new RetriesExhaustedException();
}

// ✅ 指数退避 + 随机抖动，分散重试时间
public <T> T retryGood(Supplier<T> action, int maxRetries) {
    for (int i = 0; i < maxRetries; i++) {
        try {
            return action.get();
        } catch (RetryableException e) {
            long baseDelay = (long) Math.pow(2, i) * 100;
            long jitter = ThreadLocalRandom.current().nextLong(0, baseDelay);
            Thread.sleep(baseDelay + jitter);
        }
    }
    throw new RetriesExhaustedException();
}
```

### 陷阱 2: 级联故障 (Cascade Failures)

```python
# ❌ 服务A调服务B，B调C，C慢导致全链路阻塞
class ServiceA:
    def handle(self, request):
        # 没有超时，B慢就A也慢
        return self.service_b.call(request)

# ✅ 每一层都有独立的超时和熔断
class ServiceA:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=5)

    def handle(self, request):
        try:
            return self.circuit_breaker.call(
                lambda: async_with_timeout(
                    self.service_b.call(request),
                    seconds=2.0
                )
            )
        except (CircuitOpenError, TimeoutError):
            return self.fallback(request)
```

### 陷阱 3: 忽视慢依赖 (Ignoring Slow Dependencies)

```typescript
// ❌ 只处理了"失败"，没处理"慢"
async function getProduct(id: string): Promise<Product> {
  try {
    return await fetch(`/api/products/${id}`).then(r => r.json());
  } catch (error) {
    return getCachedProduct(id); // 只在失败时降级
  }
}

// ✅ 同时处理"慢"和"失败"
async function getProduct(id: string): Promise<Product> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    const response = await fetch(`/api/products/${id}`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return await response.json();
  } catch (error) {
    // 超时和失败都走降级
    return getCachedProduct(id);
  }
}
```

### 陷阱 4: 降级方案没有降级 (No Fallback for Fallback)

```java
// ❌ 降级方案本身也可能失败
public Product getProduct(String id) {
    try {
        return primaryService.get(id);
    } catch (Exception e) {
        // 如果缓存也挂了呢？
        return cacheService.get(id);
    }
}

// ✅ 多级降级，最终返回安全默认值
public Product getProduct(String id) {
    try {
        return primaryService.get(id);
    } catch (Exception e1) {
        try {
            return cacheService.get(id);
        } catch (Exception e2) {
            try {
                return localCache.get(id);
            } catch (Exception e3) {
                return Product.unavailable(id); // 最终安全默认值
            }
        }
    }
}
```

### 陷阱 5: 超时时间过长 (Timeout Too Long)

```python
# ❌ 超时30秒 — 用户早就离开了
response = requests.get(url, timeout=30)

# ✅ 根据用户体验设定超时
# 页面渲染：2-3秒
# API调用：3-5秒
# 后台任务：根据SLA设定
response = requests.get(url, timeout=3)
```

---

## 改进检查表

完成容错改进后，逐项确认：

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | 所有外部调用都有超时设置 | ☐ |
| 2 | 关键依赖都有熔断器保护 | ☐ |
| 3 | 不同依赖使用独立的资源池（舱壁隔离） | ☐ |
| 4 | 瞬时故障有重试机制（带退避和抖动） | ☐ |
| 5 | 每个外部依赖都有降级方案 | ☐ |
| 6 | 降级方案本身有兜底（安全默认值） | ☐ |
| 7 | 已区分可重试和不可重试的错误 | ☐ |
| 8 | 故障注入测试已通过 | ☐ |
| 9 | 混沌工程实验已验证核心假设 | ☐ |
| 10 | 熔断器/重试/降级有监控指标 | ☐ |
| 11 | 关键告警规则已配置 | ☐ |
| 12 | 运维手册已更新（包含降级操作指南） | ☐ |
| 13 | 团队成员了解容错机制和降级策略 | ☐ |
| 14 | 超时时间基于实际P99延迟设定 | ☐ |
| 15 | 重试不会导致幂等性问题 | ☐ |
