---
name: 熔断器模式
description: "当实现熔断器模式时，分析故障隔离，优化系统稳定性，解决级联故障问题。验证熔断策略，设计容错机制，和最佳实践。"
license: MIT
---

# 熔断器模式技能

## 概述
熔断器模式是微服务架构中的重要容错机制，用于防止系统中的故障扩散。熔断器通过监控服务调用状态，在检测到故障时自动断开连接，避免级联故障，提高系统的整体稳定性和可用性。不当的熔断器配置会导致误判、漏判或性能问题。

**核心原则**: 好的熔断器应该快速故障检测、及时恢复、合理阈值、高可用性。坏的熔断器会频繁误触发或无法及时检测故障。

## 何时使用

**始终:**
- 调用外部服务时
- 处理第三方API时
- 构建高可用系统时
- 需要故障隔离时
- 防止级联故障时
- 实现服务降级时

**触发短语:**
- "如何实现熔断器？"
- "熔断器配置策略"
- "服务降级方案"
- "故障隔离机制"
- "熔断器阈值设置"
- "微服务容错设计"

## 熔断器模式技能功能

### 状态管理
- 关闭状态（正常）
- 打开状态（熔断）
- 半开状态（试探）
- 状态转换逻辑
- 状态持久化

### 故障检测
- 失败率统计
- 响应时间监控
- 异常类型识别
- 超时检测
- 健康检查

### 恢复机制
- 自动恢复尝试
- 半开状态探测
- 渐进式恢复
- 恢复策略配置
- 监控告警

### 降级处理
- 默认返回值
- 缓存数据返回
- 备用服务调用
- 错误响应处理
- 用户体验优化

## 常见问题

### 配置问题
- **问题**: 熔断器频繁误触发
- **原因**: 阈值设置过低，检测窗口过小
- **解决**: 调整阈值配置，增加检测窗口

- **问题**: 故障检测延迟
- **原因**: 检测窗口过大，阈值过高
- **解决**: 优化配置参数，及时检测故障

### 性能问题
- **问题**: 熔断器性能开销
- **原因**: 过度统计计算，状态检查频繁
- **解决**: 优化算法，减少计算开销

- **问题**: 内存泄漏
- **原因**: 统计数据未及时清理
- **解决**: 定期清理历史数据，优化内存使用

### 恢复问题
- **问题**: 恢复过快导致反复熔断
- **原因**: 半开状态探测策略不当
- **解决**: 调整恢复策略，渐进式恢复

## 代码示例

### 基础熔断器实现
```java
// 熔断器状态枚举
public enum CircuitBreakerState {
    CLOSED,    // 关闭状态 - 正常工作
    OPEN,      // 打开状态 - 熔断
    HALF_OPEN  // 半开状态 - 探测恢复
}

// 熔断器配置
public class CircuitBreakerConfig {
    private final int failureThreshold;        // 失败阈值
    private final long timeoutDuration;        // 超时时间（毫秒）
    private final int recoveryThreshold;       // 恢复阈值
    private final long recoveryTimeout;        // 恢复超时（毫秒）
    private final int windowSize;              // 统计窗口大小
    
    public CircuitBreakerConfig(int failureThreshold, long timeoutDuration,
                              int recoveryThreshold, long recoveryTimeout,
                              int windowSize) {
        this.failureThreshold = failureThreshold;
        this.timeoutDuration = timeoutDuration;
        this.recoveryThreshold = recoveryThreshold;
        this.recoveryTimeout = recoveryTimeout;
        this.windowSize = windowSize;
    }
    
    // 默认配置
    public static CircuitBreakerConfig defaultConfig() {
        return new CircuitBreakerConfig(
            5,      // 5次失败后熔断
            60000,  // 60秒后尝试恢复
            3,      // 3次成功后完全恢复
            10000,  // 10秒恢复超时
            100     // 100次调用窗口
        );
    }
}

// 熔断器实现
public class CircuitBreaker {
    private final CircuitBreakerConfig config;
    private volatile CircuitBreakerState state;
    private final AtomicInteger failureCount;
    private final AtomicInteger successCount;
    private final AtomicLong lastFailureTime;
    private final AtomicLong lastStateChangeTime;
    private final Queue<Boolean> callHistory;
    
    public CircuitBreaker(CircuitBreakerConfig config) {
        this.config = config;
        this.state = CircuitBreakerState.CLOSED;
        this.failureCount = new AtomicInteger(0);
        this.successCount = new AtomicInteger(0);
        this.lastFailureTime = new AtomicLong(0);
        this.lastStateChangeTime = new AtomicLong(System.currentTimeMillis());
        this.callHistory = new ConcurrentLinkedQueue<>();
    }
    
    public <T> T execute(Supplier<T> supplier, Supplier<T> fallback) throws Exception {
        if (!allowRequest()) {
            return fallback.get();
        }
        
        try {
            T result = supplier.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            return fallback.get();
        }
    }
    
    public <T> CompletableFuture<T> executeAsync(
            Supplier<CompletableFuture<T>> supplier,
            Supplier<CompletableFuture<T>> fallback) {
        
        if (!allowRequest()) {
            return fallback.get();
        }
        
        try {
            CompletableFuture<T> future = supplier.get();
            return future.whenComplete((result, throwable) -> {
                if (throwable != null) {
                    onFailure();
                } else {
                    onSuccess();
                }
            });
        } catch (Exception e) {
            onFailure();
            return fallback.get();
        }
    }
    
    private boolean allowRequest() {
        long currentTime = System.currentTimeMillis();
        
        switch (state) {
            case CLOSED:
                return true;
                
            case OPEN:
                // 检查是否可以尝试恢复
                if (currentTime - lastStateChangeTime.get() >= config.getTimeoutDuration()) {
                    transitionToHalfOpen();
                    return true;
                }
                return false;
                
            case HALF_OPEN:
                return true;
                
            default:
                return false;
        }
    }
    
    private void onSuccess() {
        successCount.incrementAndGet();
        recordCallResult(true);
        
        switch (state) {
            case HALF_OPEN:
                // 半开状态下的成功调用
                if (successCount.get() >= config.getRecoveryThreshold()) {
                    transitionToClosed();
                }
                break;
            case CLOSED:
                // 重置失败计数
                failureCount.set(0);
                break;
        }
    }
    
    private void onFailure() {
        failureCount.incrementAndGet();
        recordCallResult(false);
        lastFailureTime.set(System.currentTimeMillis());
        
        switch (state) {
            case CLOSED:
                // 检查是否需要熔断
                if (shouldOpenCircuit()) {
                    transitionToOpen();
                }
                break;
            case HALF_OPEN:
                // 半开状态下的失败调用，立即熔断
                transitionToOpen();
                break;
        }
    }
    
    private boolean shouldOpenCircuit() {
        // 基于失败率的判断
        double failureRate = calculateFailureRate();
        return failureRate >= (config.getFailureThreshold() * 1.0 / config.getWindowSize());
    }
    
    private double calculateFailureRate() {
        int totalCalls = callHistory.size();
        if (totalCalls == 0) return 0.0;
        
        long failures = callHistory.stream()
            .mapToLong(success -> success ? 0 : 1)
            .sum();
        
        return (double) failures / totalCalls;
    }
    
    private void recordCallResult(boolean success) {
        callHistory.offer(success);
        
        // 保持窗口大小
        while (callHistory.size() > config.getWindowSize()) {
            callHistory.poll();
        }
    }
    
    private void transitionToOpen() {
        state = CircuitBreakerState.OPEN;
        lastStateChangeTime.set(System.currentTimeMillis());
        failureCount.set(0);
        successCount.set(0);
        System.out.println("熔断器已打开");
    }
    
    private void transitionToHalfOpen() {
        state = CircuitBreakerState.HALF_OPEN;
        lastStateChangeTime.set(System.currentTimeMillis());
        successCount.set(0);
        System.out.println("熔断器进入半开状态");
    }
    
    private void transitionToClosed() {
        state = CircuitBreakerState.CLOSED;
        lastStateChangeTime.set(System.currentTimeMillis());
        failureCount.set(0);
        successCount.set(0);
        callHistory.clear();
        System.out.println("熔断器已关闭");
    }
    
    // 获取熔断器状态
    public CircuitBreakerState getState() {
        return state;
    }
    
    // 获取统计信息
    public CircuitBreakerStats getStats() {
        return CircuitBreakerStats.builder()
            .state(state)
            .failureCount(failureCount.get())
            .successCount(successCount.get())
            .failureRate(calculateFailureRate())
            .lastFailureTime(lastFailureTime.get())
            .lastStateChangeTime(lastStateChangeTime.get())
            .build();
    }
}

// 熔断器统计信息
@Data
@Builder
public class CircuitBreakerStats {
    private CircuitBreakerState state;
    private int failureCount;
    private int successCount;
    private double failureRate;
    private long lastFailureTime;
    private long lastStateChangeTime;
}
```

### Spring Cloud Circuit Breaker
```java
// Resilience4J 熔断器配置
@Configuration
public class Resilience4JConfig {
    
    @Bean
    public CircuitBreaker circuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)                    // 失败率阈值50%
            .waitDurationInOpenState(Duration.ofSeconds(30))  // 熔断开启30秒
            .slidingWindowSize(10)                        // 滑动窗口10次调用
            .slidingWindowType(SlidingWindowType.COUNT_BASED)  // 基于计数
            .minimumNumberOfCalls(5)                     // 最少5次调用
            .slowCallDurationThreshold(Duration.ofSeconds(5))   // 慢调用阈值5秒
            .slowCallRateThreshold(50)                    // 慢调用率阈值50%
            .permittedNumberOfCallsInHalfOpenState(3)    // 半开状态允许3次调用
            .automaticTransitionFromOpenToHalfOpenEnabled(true)  // 自动转换
            .recordExceptions(IOException.class, TimeoutException.class)  // 记录异常
            .ignoreExceptions(BusinessException.class)     // 忽略业务异常
            .build();
        
        return CircuitBreaker.of("userService", config);
    }
    
    @Bean
    public TimeLimiter timeLimiter() {
        TimeLimiterConfig config = TimeLimiterConfig.custom()
            .timeoutDuration(Duration.ofSeconds(10))      // 超时时间10秒
            .cancelRunningFuture(true)                    // 取消运行中的future
            .build();
        
        return TimeLimiter.of("userService", config);
    }
}

// 服务层使用熔断器
@Service
public class UserService {
    
    private final CircuitBreaker circuitBreaker;
    private final TimeLimiter timeLimiter;
    private final UserApiClient userApiClient;
    
    public UserService(CircuitBreaker circuitBreaker,
                     TimeLimiter timeLimiter,
                     UserApiClient userApiClient) {
        this.circuitBreaker = circuitBreaker;
        this.timeLimiter = timeLimiter;
        this.userApiClient = userApiClient;
    }
    
    public User getUserById(String userId) {
        Supplier<User> supplier = () -> {
            try {
                return timeLimiter.decorateFuture(
                    CompletableFuture.supplyAsync(() -> userApiClient.getUser(userId))
                ).get();
            } catch (Exception e) {
                throw new RuntimeException("服务调用失败", e);
            }
        };
        
        Supplier<User> decoratedSupplier = CircuitBreaker
            .decorateSupplier(circuitBreaker, supplier);
        
        try {
            return decoratedSupplier.get();
        } catch (Exception e) {
            // 降级处理
            return getDefaultUser(userId);
        }
    }
    
    public List<User> getAllUsers() {
        Supplier<List<User>> supplier = () -> {
            try {
                return timeLimiter.decorateFuture(
                    CompletableFuture.supplyAsync(() -> userApiClient.getAllUsers())
                ).get();
            } catch (Exception e) {
                throw new RuntimeException("服务调用失败", e);
            }
        };
        
        Supplier<List<User>> decoratedSupplier = CircuitBreaker
            .decorateSupplier(circuitBreaker, supplier);
        
        try {
            return decoratedSupplier.get();
        } catch (Exception e) {
            // 降级处理
            return getCachedUsers();
        }
    }
    
    private User getDefaultUser(String userId) {
        return User.builder()
            .id(userId)
            .name("默认用户")
            .email("default@example.com")
            .status("INACTIVE")
            .build();
    }
    
    private List<User> getCachedUsers() {
        // 从缓存获取用户列表
        return Collections.emptyList();
    }
}

// 注解方式使用熔断器
@Service
public class OrderService {
    
    @CircuitBreaker(name = "orderService", fallbackMethod = "fallbackGetOrder")
    public Order getOrder(String orderId) {
        return orderApiClient.getOrder(orderId);
    }
    
    @CircuitBreaker(name = "orderService", fallbackMethod = "fallbackCreateOrder")
    @TimeLimiter(name = "orderService")
    public CompletableFuture<Order> createOrder(OrderRequest request) {
        return CompletableFuture.supplyAsync(() -> orderApiClient.createOrder(request));
    }
    
    public Order fallbackGetOrder(String orderId, Exception e) {
        log.warn("获取订单失败，使用降级策略: {}", e.getMessage());
        return Order.builder()
            .id(orderId)
            .status("UNAVAILABLE")
            .message("服务暂时不可用")
            .build();
    }
    
    public CompletableFuture<Order> fallbackCreateOrder(OrderRequest request, Exception e) {
        log.warn("创建订单失败，使用降级策略: {}", e.getMessage());
        return CompletableFuture.completedFuture(
            Order.builder()
                .id("fallback-" + UUID.randomUUID().toString())
                .status("FAILED")
                .message("服务暂时不可用，订单创建失败")
                .build()
        );
    }
}
```

### 自定义熔断器监控
```java
// 熔断器监控服务
@Component
public class CircuitBreakerMonitor {
    
    private final Map<String, CircuitBreakerMetrics> metricsMap = new ConcurrentHashMap<>();
    private final MeterRegistry meterRegistry;
    
    public CircuitBreakerMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    @EventListener
    public void onCircuitBreakerEvent(CircuitBreakerEvent event) {
        String circuitBreakerName = event.getCircuitBreakerName();
        CircuitBreakerEventType eventType = event.getEventType();
        
        updateMetrics(circuitBreakerName, eventType);
        recordMetrics(circuitBreakerName, eventType);
    }
    
    private void updateMetrics(String circuitBreakerName, CircuitBreakerEventType eventType) {
        CircuitBreakerMetrics metrics = metricsMap.computeIfAbsent(
            circuitBreakerName, 
            name -> new CircuitBreakerMetrics(name)
        );
        
        metrics.recordEvent(eventType);
    }
    
    private void recordMetrics(String circuitBreakerName, CircuitBreakerEventType eventType) {
        switch (eventType) {
            case SUCCESS:
                meterRegistry.counter("circuitbreaker.success", 
                    "name", circuitBreakerName).increment();
                break;
            case ERROR:
                meterRegistry.counter("circuitbreaker.error", 
                    "name", circuitBreakerName).increment();
                break;
            case TIMEOUT:
                meterRegistry.counter("circuitbreaker.timeout", 
                    "name", circuitBreakerName).increment();
                break;
            case NOT_PERMITTED:
                meterRegistry.counter("circuitbreaker.not_permitted", 
                    "name", circuitBreakerName).increment();
                break;
            case STATE_TRANSITION:
                meterRegistry.counter("circuitbreaker.state_transition", 
                    "name", circuitBreakerName).increment();
                break;
        }
    }
    
    public CircuitBreakerMetrics getMetrics(String circuitBreakerName) {
        return metricsMap.get(circuitBreakerName);
    }
    
    public Map<String, CircuitBreakerMetrics> getAllMetrics() {
        return new HashMap<>(metricsMap);
    }
}

// 熔断器指标
@Data
public class CircuitBreakerMetrics {
    private final String circuitBreakerName;
    private final AtomicLong successCount = new AtomicLong(0);
    private final AtomicLong errorCount = new AtomicLong(0);
    private final AtomicLong timeoutCount = new AtomicLong(0);
    private final AtomicLong notPermittedCount = new AtomicLong(0);
    private final AtomicLong stateTransitionCount = new AtomicLong(0);
    private volatile CircuitBreakerState currentState = CircuitBreakerState.CLOSED;
    private volatile Instant lastStateChange = Instant.now();
    
    public CircuitBreakerMetrics(String circuitBreakerName) {
        this.circuitBreakerName = circuitBreakerName;
    }
    
    public void recordEvent(CircuitBreakerEventType eventType) {
        switch (eventType) {
            case SUCCESS:
                successCount.incrementAndGet();
                break;
            case ERROR:
                errorCount.incrementAndGet();
                break;
            case TIMEOUT:
                timeoutCount.incrementAndGet();
                break;
            case NOT_PERMITTED:
                notPermittedCount.incrementAndGet();
                break;
            case STATE_TRANSITION:
                stateTransitionCount.incrementAndGet();
                break;
        }
    }
    
    public void updateState(CircuitBreakerState newState) {
        this.currentState = newState;
        this.lastStateChange = Instant.now();
    }
    
    public double getFailureRate() {
        long totalCalls = successCount.get() + errorCount.get() + timeoutCount.get();
        return totalCalls > 0 ? 
            (double) (errorCount.get() + timeoutCount.get()) / totalCalls : 0.0;
    }
    
    public long getTotalCalls() {
        return successCount.get() + errorCount.get() + timeoutCount.get();
    }
}
```

### 熔断器管理器
```java
// 熔断器管理器
@Component
public class CircuitBreakerManager {
    
    private final Map<String, CircuitBreaker> circuitBreakers = new ConcurrentHashMap<>();
    private final CircuitBreakerConfig defaultConfig;
    
    public CircuitBreakerManager() {
        this.defaultConfig = CircuitBreakerConfig.defaultConfig();
    }
    
    public CircuitBreaker getCircuitBreaker(String name) {
        return circuitBreakers.computeIfAbsent(name, this::createCircuitBreaker);
    }
    
    public CircuitBreaker getCircuitBreaker(String name, CircuitBreakerConfig config) {
        return circuitBreakers.compute(name, (key, existing) -> {
            if (existing != null) {
                return existing;
            }
            return createCircuitBreaker(key, config);
        });
    }
    
    private CircuitBreaker createCircuitBreaker(String name) {
        return createCircuitBreaker(name, defaultConfig);
    }
    
    private CircuitBreaker createCircuitBreaker(String name, CircuitBreakerConfig config) {
        return new CircuitBreaker(config);
    }
    
    public void resetCircuitBreaker(String name) {
        CircuitBreaker circuitBreaker = circuitBreakers.get(name);
        if (circuitBreaker != null) {
            // 重置熔断器状态
            circuitBreakers.remove(name);
        }
    }
    
    public void resetAllCircuitBreakers() {
        circuitBreakers.clear();
    }
    
    public Map<String, CircuitBreakerStats> getAllStats() {
        return circuitBreakers.entrySet().stream()
            .collect(Collectors.toMap(
                Map.Entry::getKey,
                entry -> entry.getValue().getStats()
            ));
    }
    
    public List<String> getOpenCircuitBreakers() {
        return circuitBreakers.entrySet().stream()
            .filter(entry -> entry.getValue().getState() == CircuitBreakerState.OPEN)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}

// 熔断器健康检查
@Component
public class CircuitBreakerHealthIndicator implements HealthIndicator {
    
    private final CircuitBreakerManager circuitBreakerManager;
    
    public CircuitBreakerHealthIndicator(CircuitBreakerManager circuitBreakerManager) {
        this.circuitBreakerManager = circuitBreakerManager;
    }
    
    @Override
    public Health health() {
        Map<String, CircuitBreakerStats> allStats = circuitBreakerManager.getAllStats();
        List<String> openCircuitBreakers = circuitBreakerManager.getOpenCircuitBreakers();
        
        Health.Builder builder = new Health.Builder();
        
        if (openCircuitBreakers.isEmpty()) {
            builder.up();
        } else {
            builder.down();
        }
        
        builder.withDetail("totalCircuitBreakers", allStats.size())
               .withDetail("openCircuitBreakers", openCircuitBreakers)
               .withDetail("circuitBreakers", allStats);
        
        return builder.build();
    }
}
```

## 最佳实践

### 配置策略
1. **阈值设置**: 根据业务特点合理设置失败率阈值
2. **窗口大小**: 选择合适的统计窗口大小
3. **恢复策略**: 配置渐进式恢复机制
4. **超时设置**: 设置合理的超时时间

### 监控告警
1. **状态监控**: 实时监控熔断器状态变化
2. **性能指标**: 监控失败率、响应时间等指标
3. **告警机制**: 设置熔断器状态变化告警
4. **日志记录**: 详细记录熔断器事件

### 降级策略
1. **默认值**: 提供合理的默认返回值
2. **缓存数据**: 使用缓存数据作为降级方案
3. **备用服务**: 准备备用服务或降级接口
4. **用户体验**: 保证用户体验不受影响

### 测试验证
1. **故障测试**: 模拟各种故障场景
2. **恢复测试**: 验证熔断器恢复机制
3. **性能测试**: 测试熔断器性能影响
4. **压力测试**: 验证高并发下的表现

## 相关技能

- **api-gateway** - API网关设计
- **distributed-tracing** - 分布式追踪
- **service-discovery** - 服务发现
- **service-communication** - 服务间通信
- **backend** - 后端开发
