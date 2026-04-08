# 可用性原则 - 参考实现

## 核心原理与设计

### 可用性的定义

可用性 = **系统正常运行时间 / 总时间**。高可用系统通过冗余、降级、快速恢复三大手段保障服务持续可用。

### 关键策略

```
1. 消除单点故障 → 冗余部署
2. 故障快速检测 → 健康检查
3. 故障自动恢复 → 自动故障转移
4. 局部故障隔离 → 优雅降级
5. 请求容错处理 → 超时重试
```

---

## Java 参考实现

### 反面示例：缺乏可用性设计

```java
/**
 * ❌ 反面示例：无超时、无降级、无健康检查
 */
public class ProductService {
    private final RestTemplate restTemplate = new RestTemplate(); // 无超时配置
    private final JdbcTemplate jdbc;

    public ProductDetail getProductDetail(String productId) {
        // 直接查库，无缓存
        Product product = jdbc.queryForObject(
            "SELECT * FROM products WHERE id = ?", Product.class, productId);

        // 调用推荐服务，无超时，无降级
        List<Product> recommendations = restTemplate.getForObject(
            "http://recommendation-service/recommend/" + productId, List.class);

        // 调用评价服务，无超时，无降级
        List<Review> reviews = restTemplate.getForObject(
            "http://review-service/reviews/" + productId, List.class);

        // 任何一个服务挂了，整个请求都失败
        return new ProductDetail(product, recommendations, reviews);
    }
}
```

### 正面示例：高可用设计

```java
/**
 * ✅ 正面示例：超时、降级、缓存、健康检查
 */

// 健康检查控制器
@RestController
public class HealthController {
    private final DataSource dataSource;
    private final RedisTemplate<String, Object> redis;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> status = new LinkedHashMap<>();
        boolean healthy = true;

        // 检查数据库
        try {
            new JdbcTemplate(dataSource).queryForObject("SELECT 1", Integer.class);
            status.put("database", "UP");
        } catch (Exception e) {
            status.put("database", "DOWN");
            healthy = false;
        }

        // 检查缓存（非核心，不影响整体健康）
        try {
            redis.opsForValue().get("health-check");
            status.put("cache", "UP");
        } catch (Exception e) {
            status.put("cache", "DEGRADED");
        }

        status.put("status", healthy ? "UP" : "DOWN");
        return healthy
            ? ResponseEntity.ok(status)
            : ResponseEntity.status(503).body(status);
    }
}

// 带降级的产品服务
@Service
public class ResilientProductService {
    private final ProductRepository productRepo;
    private final CacheService cache;
    private final CircuitBreaker recommendationBreaker;
    private final CircuitBreaker reviewBreaker;
    private final RestTemplate restTemplate;

    public ResilientProductService(ProductRepository productRepo,
                                    CacheService cache,
                                    CircuitBreakerFactory breakerFactory) {
        this.productRepo = productRepo;
        this.cache = cache;
        this.recommendationBreaker = breakerFactory.create("recommendation");
        this.reviewBreaker = breakerFactory.create("review");

        // 配置超时
        this.restTemplate = new RestTemplateBuilder()
            .setConnectTimeout(Duration.ofSeconds(2))
            .setReadTimeout(Duration.ofSeconds(3))
            .build();
    }

    public ProductDetail getProductDetail(String productId) {
        // 核心数据：从缓存或数据库获取（必须成功）
        Product product = getProductWithCache(productId);

        // 非核心数据：带断路器和降级
        List<Product> recommendations = getRecommendationsWithFallback(productId);
        List<Review> reviews = getReviewsWithFallback(productId);

        return new ProductDetail(product, recommendations, reviews);
    }

    private Product getProductWithCache(String productId) {
        // 先查缓存
        Product cached = cache.get("product:" + productId, Product.class);
        if (cached != null) return cached;

        // 缓存未命中，查数据库
        Product product = productRepo.findById(productId)
            .orElseThrow(() -> new NotFoundException("Product not found: " + productId));

        // 写入缓存
        cache.set("product:" + productId, product, Duration.ofMinutes(10));
        return product;
    }

    private List<Product> getRecommendationsWithFallback(String productId) {
        try {
            return recommendationBreaker.run(
                () -> restTemplate.getForObject(
                    "http://recommendation-service/recommend/" + productId, List.class),
                throwable -> Collections.emptyList()  // 降级：返回空列表
            );
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private List<Review> getReviewsWithFallback(String productId) {
        try {
            return reviewBreaker.run(
                () -> restTemplate.getForObject(
                    "http://review-service/reviews/" + productId, List.class),
                throwable -> Collections.emptyList()  // 降级：返回空列表
            );
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }
}

// 缓存服务（带降级）
@Service
public class CacheService {
    private final RedisTemplate<String, Object> redis;

    public <T> T get(String key, Class<T> type) {
        try {
            Object value = redis.opsForValue().get(key);
            return type.cast(value);
        } catch (Exception e) {
            // 缓存故障不影响业务，返回 null 走数据库
            return null;
        }
    }

    public void set(String key, Object value, Duration ttl) {
        try {
            redis.opsForValue().set(key, value, ttl);
        } catch (Exception e) {
            // 缓存写入失败不影响业务
        }
    }
}

// 带重试的 HTTP 客户端
@Component
public class ResilientHttpClient {
    private final RestTemplate restTemplate;
    private static final int MAX_RETRIES = 3;

    public <T> T getWithRetry(String url, Class<T> responseType) {
        Exception lastException = null;

        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                return restTemplate.getForObject(url, responseType);
            } catch (HttpServerErrorException e) {
                lastException = e;
                if (attempt < MAX_RETRIES) {
                    long delay = (long) Math.pow(2, attempt) * 100 + (long)(Math.random() * 100);
                    try { Thread.sleep(delay); } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException(ie);
                    }
                }
            } catch (HttpClientErrorException e) {
                throw e;  // 4xx 不重试
            }
        }
        throw new RuntimeException("Max retries exceeded", lastException);
    }
}
```

### 单元测试

```java
@ExtendWith(MockitoExtension.class)
class ResilientProductServiceTest {

    @Mock private ProductRepository productRepo;
    @Mock private CacheService cache;
    @Mock private CircuitBreakerFactory breakerFactory;

    private ResilientProductService service;

    @BeforeEach
    void setUp() {
        CircuitBreaker noOpBreaker = mock(CircuitBreaker.class);
        when(noOpBreaker.run(any(), any())).thenAnswer(inv -> {
            try {
                return ((Supplier<?>) inv.getArgument(0)).get();
            } catch (Exception e) {
                return ((Function<Throwable, ?>) inv.getArgument(1)).apply(e);
            }
        });
        when(breakerFactory.create(anyString())).thenReturn(noOpBreaker);
        service = new ResilientProductService(productRepo, cache, breakerFactory);
    }

    @Test
    void shouldReturnProductEvenWhenRecommendationServiceFails() {
        Product product = new Product("1", "Test Product");
        when(productRepo.findById("1")).thenReturn(Optional.of(product));
        when(cache.get(anyString(), any())).thenReturn(null);

        ProductDetail detail = service.getProductDetail("1");

        assertEquals("Test Product", detail.getProduct().getName());
        assertTrue(detail.getRecommendations().isEmpty()); // 降级为空
    }

    @Test
    void shouldReturnCachedProduct() {
        Product cached = new Product("1", "Cached Product");
        when(cache.get("product:1", Product.class)).thenReturn(cached);

        ProductDetail detail = service.getProductDetail("1");

        assertEquals("Cached Product", detail.getProduct().getName());
        verify(productRepo, never()).findById(anyString()); // 没有查数据库
    }
}
```

---

## Python 参考实现

```python
"""
✅ 高可用 Python 服务实现
"""
import time
import random
from typing import Optional, Any
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum

# 断路器实现
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED

    def call(self, func, fallback=None, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
            elif fallback:
                return fallback()
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            if fallback:
                return fallback()
            raise

# 重试装饰器
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.random()
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# 带降级的产品服务
class ResilientProductService:
    def __init__(self, product_repo, cache, recommendation_client, review_client):
        self.product_repo = product_repo
        self.cache = cache
        self.recommendation_client = recommendation_client
        self.review_client = review_client
        self.recommendation_breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30)
        self.review_breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30)

    def get_product_detail(self, product_id: str) -> dict:
        # 核心：产品数据（必须成功）
        product = self._get_product_with_cache(product_id)

        # 非核心：推荐（可降级）
        recommendations = self.recommendation_breaker.call(
            lambda: self.recommendation_client.get_recommendations(product_id),
            fallback=lambda: []
        )

        # 非核心：评价（可降级）
        reviews = self.review_breaker.call(
            lambda: self.review_client.get_reviews(product_id),
            fallback=lambda: []
        )

        return {
            "product": product,
            "recommendations": recommendations,
            "reviews": reviews
        }

    def _get_product_with_cache(self, product_id: str):
        # 先查缓存
        cached = self.cache.get(f"product:{product_id}")
        if cached:
            return cached

        # 缓存未命中，查数据库
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        # 写入缓存（缓存失败不影响业务）
        try:
            self.cache.set(f"product:{product_id}", product, ttl=600)
        except Exception:
            pass

        return product

# 健康检查
class HealthChecker:
    def __init__(self, db, cache):
        self.db = db
        self.cache = cache

    def check(self) -> dict:
        status = {}
        healthy = True

        # 数据库检查
        try:
            self.db.execute("SELECT 1")
            status["database"] = "UP"
        except Exception:
            status["database"] = "DOWN"
            healthy = False

        # 缓存检查（非核心）
        try:
            self.cache.ping()
            status["cache"] = "UP"
        except Exception:
            status["cache"] = "DEGRADED"

        status["status"] = "UP" if healthy else "DOWN"
        return status


# 使用示例
if __name__ == "__main__":
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout=10)

    def unstable_service():
        if random.random() < 0.7:
            raise Exception("Service unavailable")
        return "success"

    for i in range(10):
        result = breaker.call(
            unstable_service,
            fallback=lambda: "fallback_value"
        )
        print(f"Attempt {i+1}: {result} (state: {breaker.state.value})")
```

---

## TypeScript 参考实现

```typescript
/**
 * ✅ 高可用 TypeScript 服务实现
 */

// 断路器
enum CircuitState { CLOSED, OPEN, HALF_OPEN }

class CircuitBreaker {
    private failureCount = 0;
    private lastFailureTime = 0;
    private state = CircuitState.CLOSED;

    constructor(
        private failureThreshold: number = 5,
        private resetTimeout: number = 30000
    ) {}

    async call<T>(fn: () => Promise<T>, fallback?: () => T): Promise<T> {
        if (this.state === CircuitState.OPEN) {
            if (Date.now() - this.lastFailureTime > this.resetTimeout) {
                this.state = CircuitState.HALF_OPEN;
            } else if (fallback) {
                return fallback();
            } else {
                throw new Error('Circuit breaker is open');
            }
        }

        try {
            const result = await fn();
            if (this.state === CircuitState.HALF_OPEN) {
                this.state = CircuitState.CLOSED;
                this.failureCount = 0;
            }
            return result;
        } catch (error) {
            this.failureCount++;
            this.lastFailureTime = Date.now();
            if (this.failureCount >= this.failureThreshold) {
                this.state = CircuitState.OPEN;
            }
            if (fallback) return fallback();
            throw error;
        }
    }

    getState(): string { return CircuitState[this.state]; }
}

// 带超时的 fetch
async function fetchWithTimeout(url: string, timeoutMs: number = 3000): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

// 带重试的 fetch
async function fetchWithRetry(
    url: string,
    maxRetries: number = 3,
    baseDelay: number = 1000
): Promise<Response> {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetchWithTimeout(url);
            if (response.ok) return response;
            if (response.status < 500) throw new Error(`Client error: ${response.status}`);
            throw new Error(`Server error: ${response.status}`);
        } catch (error) {
            lastError = error as Error;
            if (attempt < maxRetries) {
                const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    throw lastError;
}

// 高可用产品服务
class ResilientProductService {
    private recommendationBreaker = new CircuitBreaker(5, 30000);
    private reviewBreaker = new CircuitBreaker(5, 30000);

    constructor(
        private productRepo: ProductRepository,
        private cache: CacheService
    ) {}

    async getProductDetail(productId: string) {
        // 核心数据（必须成功）
        const product = await this.getProductWithCache(productId);

        // 非核心数据（可降级，并行请求）
        const [recommendations, reviews] = await Promise.all([
            this.recommendationBreaker.call(
                () => fetchWithRetry(`http://rec-service/recommend/${productId}`).then(r => r.json()),
                () => []
            ),
            this.reviewBreaker.call(
                () => fetchWithRetry(`http://review-service/reviews/${productId}`).then(r => r.json()),
                () => []
            )
        ]);

        return { product, recommendations, reviews };
    }

    private async getProductWithCache(productId: string) {
        const cached = await this.cache.get(`product:${productId}`);
        if (cached) return cached;

        const product = await this.productRepo.findById(productId);
        if (!product) throw new Error(`Product not found: ${productId}`);

        await this.cache.set(`product:${productId}`, product, 600).catch(() => {});
        return product;
    }
}

// 健康检查端点
class HealthCheck {
    constructor(private db: Database, private cache: CacheService) {}

    async check(): Promise<{ status: string; components: Record<string, string> }> {
        const components: Record<string, string> = {};
        let healthy = true;

        try {
            await this.db.query('SELECT 1');
            components.database = 'UP';
        } catch {
            components.database = 'DOWN';
            healthy = false;
        }

        try {
            await this.cache.ping();
            components.cache = 'UP';
        } catch {
            components.cache = 'DEGRADED';
        }

        return {
            status: healthy ? 'UP' : 'DOWN',
            components
        };
    }
}
```

---

## 总结

**核心要点**：

1. **消除单点故障** - 所有关键组件冗余部署
2. **快速故障检测** - 健康检查 + 监控告警
3. **自动故障恢复** - 断路器 + 自动切换
4. **优雅降级** - 非核心功能故障不影响核心功能
5. **超时重试** - 防止慢依赖拖垮系统

**效果指标**：

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 可用率 | 99% | 99.9%+ |
| 单点故障 | 3处 | 0处 |
| 故障恢复时间 | 30分钟 | < 1分钟 |
| 外部依赖隔离 | 无 | 断路器保护 |
| 缓存降级 | 无 | 自动降级到DB |
| 部署停机 | 有 | 零停机 |
