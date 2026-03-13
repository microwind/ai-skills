---
name: 高并发系统设计
description: "当设计高并发系统时，分析并发模式，优化系统性能，解决资源竞争。验证并发架构，设计扩展策略，和最佳实践。"
license: MIT
---

# 高并发系统设计技能

## 概述
高并发系统设计是处理大量并发请求的技术，通过合理的架构设计和优化策略，确保系统在高负载下仍能保持良好的性能和稳定性。高并发设计涉及线程池、缓存、消息队列、数据库优化等多个方面，需要综合考虑性能、可用性和扩展性。

**核心原则**: 好的高并发设计应该水平扩展、异步处理、缓存优先、降级容错。坏的设计会导致性能瓶颈、系统崩溃、用户体验差。

## 何时使用

**始终:**
- 设计高流量网站时
- 处理大量并发请求时
- 优化系统性能时
- 构建分布式系统时
- 设计秒杀系统时
- 处理突发流量时

**触发短语:**
- "如何设计高并发系统？"
- "系统性能优化方案"
- "并发处理策略"
- "负载均衡设计"
- "缓存架构设计"
- "异步处理实现"

## 高并发系统设计技能功能

### 并发控制
- 线程池管理
- 信号量控制
- 限流策略
- 熔断机制
- 降级策略

### 性能优化
- 缓存策略
- 数据库优化
- 连接池管理
- 异步处理
- 批量操作

### 扩展设计
- 水平扩展
- 负载均衡
- 服务拆分
- 数据分片
- 微服务架构

### 监控运维
- 性能监控
- 容量规划
- 故障恢复
- 自动扩容
- 告警机制

## 常见问题

### 性能瓶颈
- **问题**: 响应时间过长
- **原因**: 数据库查询慢，锁竞争，资源不足
- **解决**: 优化数据库，使用缓存，增加资源

- **问题**: 吞吐量低
- **原因**: 单点瓶颈，同步处理，资源浪费
- **解决**: 分布式架构，异步处理，资源池化

### 并发问题
- **问题**: 线程安全问题
- **原因**: 共享资源，竞态条件，死锁
- **解决**: 无锁设计，线程本地存储，分布式锁

- **问题**: 资源竞争
- **原因**: 连接池耗尽，内存不足，CPU过载
- **解决**: 资源池化，限流控制，自动扩容

### 扩展性问题
- **问题**: 无法水平扩展
- **原因**: 状态存储，单点依赖，紧耦合
- **解决**: 无状态设计，分布式存储，服务解耦

## 代码示例

### 线程池配置和管理
```java
// 高并发线程池配置
@Configuration
public class ThreadPoolConfig {
    
    @Bean("taskExecutor")
    public ThreadPoolTaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        
        // 核心线程数 = CPU核心数
        executor.setCorePoolSize(Runtime.getRuntime().availableProcessors());
        
        // 最大线程数 = CPU核心数 * 2
        executor.setMaxPoolSize(Runtime.getRuntime().availableProcessors() * 2);
        
        // 队列容量
        executor.setQueueCapacity(1000);
        
        // 线程名前缀
        executor.setThreadNamePrefix("high-concurrency-");
        
        // 拒绝策略：调用者运行
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        
        // 线程空闲时间
        executor.setKeepAliveSeconds(60);
        
        // 允许核心线程超时
        executor.setAllowCoreThreadTimeOut(true);
        
        // 等待所有任务完成后再关闭线程池
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(60);
        
        executor.initialize();
        return executor;
    }
    
    @Bean("ioExecutor")
    public ThreadPoolTaskExecutor ioExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        
        // IO密集型任务：线程数可以设置更高
        executor.setCorePoolSize(50);
        executor.setMaxPoolSize(200);
        executor.setQueueCapacity(5000);
        executor.setThreadNamePrefix("io-intensive-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setKeepAliveSeconds(30);
        executor.setAllowCoreThreadTimeOut(true);
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);
        
        executor.initialize();
        return executor;
    }
    
    @Bean("cpuExecutor")
    public ThreadPoolTaskExecutor cpuExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        
        // CPU密集型任务：线程数等于CPU核心数
        int cpuCount = Runtime.getRuntime().availableProcessors();
        executor.setCorePoolSize(cpuCount);
        executor.setMaxPoolSize(cpuCount);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("cpu-intensive-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.setKeepAliveSeconds(60);
        executor.setAllowCoreThreadTimeOut(true);
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(60);
        
        executor.initialize();
        return executor;
    }
}

// 高并发任务执行器
@Service
public class HighConcurrencyTaskExecutor {
    
    private final ThreadPoolTaskExecutor taskExecutor;
    private final ThreadPoolTaskExecutor ioExecutor;
    private final ThreadPoolTaskExecutor cpuExecutor;
    private final MeterRegistry meterRegistry;
    
    public HighConcurrencyTaskExecutor(ThreadPoolTaskExecutor taskExecutor,
                                       ThreadPoolTaskExecutor ioExecutor,
                                       ThreadPoolTaskExecutor cpuExecutor,
                                       MeterRegistry meterRegistry) {
        this.taskExecutor = taskExecutor;
        this.ioExecutor = ioExecutor;
        this.cpuExecutor = cpuExecutor;
        this.meterRegistry = meterRegistry;
    }
    
    // 执行CPU密集型任务
    public CompletableFuture<Object> executeCpuIntensiveTask(Callable<Object> task) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                return task.call();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }, cpuExecutor).whenComplete((result, throwable) -> {
            sample.stop(Timer.builder("cpu.task.execution").register(meterRegistry));
            if (throwable != null) {
                meterRegistry.counter("cpu.task.error").increment();
            }
        });
    }
    
    // 执行IO密集型任务
    public CompletableFuture<Object> executeIOIntensiveTask(Callable<Object> task) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                return task.call();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }, ioExecutor).whenComplete((result, throwable) -> {
            sample.stop(Timer.builder("io.task.execution").register(meterRegistry));
            if (throwable != null) {
                meterRegistry.counter("io.task.error").increment();
            }
        });
    }
    
    // 执行普通任务
    public CompletableFuture<Object> executeGeneralTask(Callable<Object> task) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                return task.call();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }, taskExecutor).whenComplete((result, throwable) -> {
            sample.stop(Timer.builder("general.task.execution").register(meterRegistry));
            if (throwable != null) {
                meterRegistry.counter("general.task.error").increment();
            }
        });
    }
    
    // 批量执行任务
    public CompletableFuture<List<Object>> executeBatchTasks(List<Callable<Object>> tasks, 
                                                         Executor executor) {
        List<CompletableFuture<Object>> futures = tasks.stream()
            .map(task -> CompletableFuture.supplyAsync(() -> {
                try {
                    return task.call();
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }, executor))
            .collect(Collectors.toList());
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList()));
    }
    
    // 获取线程池状态
    public Map<String, Object> getThreadPoolStatus() {
        Map<String, Object> status = new HashMap<>();
        
        status.put("taskExecutor", getExecutorStatus(taskExecutor));
        status.put("ioExecutor", getExecutorStatus(ioExecutor));
        status.put("cpuExecutor", getExecutorStatus(cpuExecutor));
        
        return status;
    }
    
    private Map<String, Object> getExecutorStatus(ThreadPoolTaskExecutor executor) {
        Map<String, Object> status = new HashMap<>();
        
        ThreadPoolExecutor threadPoolExecutor = executor.getThreadPoolExecutor();
        
        status.put("corePoolSize", threadPoolExecutor.getCorePoolSize());
        status.put("maximumPoolSize", threadPoolExecutor.getMaximumPoolSize());
        status.put("activeCount", threadPoolExecutor.getActiveCount());
        status.put("poolSize", threadPoolExecutor.getPoolSize());
        status.put("queueSize", threadPoolExecutor.getQueue().size());
        status.put("completedTaskCount", threadPoolExecutor.getCompletedTaskCount());
        status.put("taskCount", threadPoolExecutor.getTaskCount());
        
        return status;
    }
}
```

### 限流和熔断机制
```java
// 限流器配置
@Configuration
public class RateLimiterConfig {
    
    @Bean
    public RateLimiter apiRateLimiter() {
        // 每秒1000个请求
        return RateLimiter.create(1000.0);
    }
    
    @Bean
    public RateLimiter databaseRateLimiter() {
        // 每秒500个请求
        return RateLimiter.create(500.0);
    }
    
    @Bean
    public Semaphore concurrentSemaphore() {
        // 最大100个并发
        return new Semaphore(100);
    }
    
    @Bean
    public Map<String, RateLimiter> endpointRateLimiters() {
        Map<String, RateLimiter> limiters = new HashMap<>();
        
        // 不同端点的不同限流策略
        limiters.put("/api/users", RateLimiter.create(100.0));     // 每秒100个
        limiters.put("/api/orders", RateLimiter.create(50.0));     // 每秒50个
        limiters.put("/api/products", RateLimiter.create(200.0));   // 每秒200个
        
        return limiters;
    }
}

// 熔断器配置
@Configuration
public class CircuitBreakerConfig {
    
    @Bean
    public CircuitBreaker apiCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)                    // 失败率阈值50%
            .waitDurationInOpenState(Duration.ofSeconds(30))  // 熔断30秒
            .slidingWindowType(SlidingWindowType.COUNT_BASED)
            .slidingWindowSize(10)                    // 滑动窗口大小
            .minimumNumberOfCalls(5)                   // 最少调用次数
            .build();
        
        return CircuitBreaker.of("apiCircuitBreaker", config);
    }
    
    @Bean
    public CircuitBreaker databaseCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(30)                    // 失败率阈值30%
            .waitDurationInOpenState(Duration.ofSeconds(60))  // 熔断60秒
            .slidingWindowType(SlidingWindowType.TIME_BASED)
            .slidingWindowSize(Duration.ofMinutes(1))    // 滑动窗口1分钟
            .minimumNumberOfCalls(10)                  // 最少调用次数
            .build();
        
        return CircuitBreaker.of("databaseCircuitBreaker", config);
    }
}

// 高并发控制器
@RestController
@RequestMapping("/api/high-concurrency")
public class HighConcurrencyController {
    
    private final RateLimiter apiRateLimiter;
    private final RateLimiter databaseRateLimiter;
    private final Map<String, RateLimiter> endpointRateLimiters;
    private final Semaphore concurrentSemaphore;
    private final CircuitBreaker apiCircuitBreaker;
    private final CircuitBreaker databaseCircuitBreaker;
    private final HighConcurrencyTaskExecutor taskExecutor;
    
    public HighConcurrencyController(RateLimiter apiRateLimiter,
                                     RateLimiter databaseRateLimiter,
                                     Map<String, RateLimiter> endpointRateLimiters,
                                     Semaphore concurrentSemaphore,
                                     CircuitBreaker apiCircuitBreaker,
                                     CircuitBreaker databaseCircuitBreaker,
                                     HighConcurrencyTaskExecutor taskExecutor) {
        this.apiRateLimiter = apiRateLimiter;
        this.databaseRateLimiter = databaseRateLimiter;
        this.endpointRateLimiters = endpointRateLimiters;
        this.concurrentSemaphore = concurrentSemaphore;
        this.apiCircuitBreaker = apiCircuitBreaker;
        this.databaseCircuitBreaker = databaseCircuitBreaker;
        this.taskExecutor = taskExecutor;
    }
    
    // 高并发用户查询
    @GetMapping("/users/{id}")
    public CompletableFuture<ResponseEntity<User>> getUser(@PathVariable String id) {
        // 端点限流
        RateLimiter endpointLimiter = endpointRateLimiters.get("/api/users");
        if (endpointLimiter != null && !endpointLimiter.tryAcquire()) {
            return CompletableFuture.completedFuture(
                ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build());
        }
        
        // 全局限流
        if (!apiRateLimiter.tryAcquire()) {
            return CompletableFuture.completedFuture(
                ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build());
        }
        
        // 并发控制
        if (!concurrentSemaphore.tryAcquire()) {
            return CompletableFuture.completedFuture(
                ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).build());
        }
        
        try {
            // 使用熔断器执行查询
            Supplier<User> supplier = CircuitBreaker.decorateSupplier(
                databaseCircuitBreaker, () -> findUserById(id));
            
            User user = supplier.get();
            
            return CompletableFuture.completedFuture(
                ResponseEntity.ok(user));
                
        } catch (Exception e) {
            return CompletableFuture.completedFuture(
                ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
        } finally {
            concurrentSemaphore.release();
        }
    }
    
    // 批量用户查询
    @PostMapping("/users/batch")
    public CompletableFuture<ResponseEntity<List<User>>> getUsersBatch(@RequestBody List<String> userIds) {
        // 检查请求数量限制
        if (userIds.size() > 100) {
            return CompletableFuture.completedFuture(
                ResponseEntity.badRequest().build());
        }
        
        // 数据库限流
        if (!databaseRateLimiter.tryAcquire(userIds.size())) {
            return CompletableFuture.completedFuture(
                ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build());
        }
        
        // 并发查询
        List<Callable<User>> tasks = userIds.stream()
            .map(id -> (Callable<User>) () -> findUserById(id))
            .collect(Collectors.toList());
        
        return taskExecutor.executeBatchTasks(tasks, taskExecutor.getTaskExecutor())
            .thenApply(users -> ResponseEntity.ok(users))
            .exceptionally(throwable -> 
                ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
    }
    
    // 异步任务处理
    @PostMapping("/tasks")
    public CompletableFuture<ResponseEntity<String>> submitTask(@RequestBody TaskRequest request) {
        // 限流检查
        if (!apiRateLimiter.tryAcquire()) {
            return CompletableFuture.completedFuture(
                ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build());
        }
        
        // 异步执行任务
        return taskExecutor.executeIOIntensiveTask(() -> processTask(request))
            .thenApply(result -> ResponseEntity.ok("Task completed: " + result))
            .exceptionally(throwable -> 
                ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Task failed: " + throwable.getMessage()));
    }
    
    // 系统状态监控
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getSystemStatus() {
        Map<String, Object> status = new HashMap<>();
        
        // 线程池状态
        status.put("threadPools", taskExecutor.getThreadPoolStatus());
        
        // 限流器状态
        status.put("rateLimiters", Map.of(
            "apiRateLimiter", apiRateLimiter.getRate(),
            "databaseRateLimiter", databaseRateLimiter.getRate()
        ));
        
        // 熔断器状态
        status.put("circuitBreakers", Map.of(
            "apiCircuitBreaker", apiCircuitBreaker.getState(),
            "databaseCircuitBreaker", databaseCircuitBreaker.getState()
        ));
        
        // 信号量状态
        status.put("semaphore", Map.of(
            "availablePermits", concurrentSemaphore.availablePermits(),
            "queueLength", concurrentSemaphore.getQueueLength()
        ));
        
        return ResponseEntity.ok(status);
    }
    
    private User findUserById(String id) {
        // 模拟数据库查询
        try {
            Thread.sleep(10); // 模拟查询延迟
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        User user = new User();
        user.setId(id);
        user.setName("User-" + id);
        user.setEmail("user-" + id + "@example.com");
        
        return user;
    }
    
    private Object processTask(TaskRequest request) {
        // 模拟任务处理
        try {
            Thread.sleep(100); // 模拟处理时间
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        return "Processed: " + request.getData();
    }
}
```

### 缓存架构实现
```java
// 多级缓存配置
@Configuration
public class MultiLevelCacheConfig {
    
    @Bean
    public CacheManager caffeineCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(10000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .recordStats());
        
        return cacheManager;
    }
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.afterPropertiesSet();
        
        return template;
    }
    
    @Bean
    public CacheManager redisCacheManager(RedisTemplate<String, Object> redisTemplate) {
        RedisCacheWriter cacheWriter = RedisCacheWriter.nonLockingRedisCacheWriter(redisTemplate.getConnectionFactory());
        RedisCacheConfiguration cacheConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))
            .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return new RedisCacheManager(cacheWriter, cacheConfig);
    }
}

// 多级缓存服务
@Service
public class MultiLevelCacheService {
    
    private final CacheManager caffeineCacheManager;
    private final CacheManager redisCacheManager;
    private final RedisTemplate<String, Object> redisTemplate;
    private final MeterRegistry meterRegistry;
    
    public MultiLevelCacheService(CacheManager caffeineCacheManager,
                                  CacheManager redisCacheManager,
                                  RedisTemplate<String, Object> redisTemplate,
                                  MeterRegistry meterRegistry) {
        this.caffeineCacheManager = caffeineCacheManager;
        this.redisCacheManager = redisCacheManager;
        this.redisTemplate = redisTemplate;
        this.meterRegistry = meterRegistry;
    }
    
    // 获取数据（多级缓存）
    public <T> T get(String key, Class<T> type, Supplier<T> dataLoader) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            // L1缓存：本地缓存
            T value = getFromCaffeine(key, type);
            if (value != null) {
                meterRegistry.counter("cache.hit", Tags.of("level", "caffeine")).increment();
                return value;
            }
            
            // L2缓存：Redis缓存
            value = getFromRedis(key, type);
            if (value != null) {
                // 回填到L1缓存
                putToCaffeine(key, value);
                meterRegistry.counter("cache.hit", Tags.of("level", "redis")).increment();
                return value;
            }
            
            // 缓存未命中，从数据源加载
            value = dataLoader.get();
            if (value != null) {
                // 写入多级缓存
                putToCaffeine(key, value);
                putToRedis(key, value);
                meterRegistry.counter("cache.miss").increment();
            }
            
            return value;
            
        } finally {
            sample.stop(Timer.builder("cache.get").register(meterRegistry));
        }
    }
    
    // 设置数据
    public <T> void put(String key, T value) {
        putToCaffeine(key, value);
        putToRedis(key, value);
    }
    
    // 删除数据
    public void evict(String key) {
        evictFromCaffeine(key);
        evictFromRedis(key);
    }
    
    // 批量删除
    public void evictAll() {
        clearCaffeine();
        clearRedis();
    }
    
    // 预热缓存
    public <T> void warmUp(String key, Class<T> type, Supplier<T> dataLoader) {
        T value = dataLoader.get();
        if (value != null) {
            put(key, value);
        }
    }
    
    // 从Caffeine获取
    @SuppressWarnings("unchecked")
    private <T> T getFromCaffeine(String key, Class<T> type) {
        Cache cache = caffeineCacheManager.getCache("default");
        if (cache != null) {
            Cache.ValueWrapper wrapper = cache.get(key);
            if (wrapper != null) {
                Object value = wrapper.get();
                if (type.isInstance(value)) {
                    return (T) value;
                }
            }
        }
        return null;
    }
    
    // 从Redis获取
    @SuppressWarnings("unchecked")
    private <T> T getFromRedis(String key, Class<T> type) {
        try {
            Object value = redisTemplate.opsForValue().get(key);
            if (value != null && type.isInstance(value)) {
                return (T) value;
            }
        } catch (Exception e) {
            log.error("Failed to get from Redis cache: " + key, e);
        }
        return null;
    }
    
    // 写入Caffeine
    private <T> void putToCaffeine(String key, T value) {
        Cache cache = caffeineCacheManager.getCache("default");
        if (cache != null) {
            cache.put(key, value);
        }
    }
    
    // 写入Redis
    private <T> void putToRedis(String key, T value) {
        try {
            redisTemplate.opsForValue().set(key, value);
        } catch (Exception e) {
            log.error("Failed to put to Redis cache: " + key, e);
        }
    }
    
    // 从Caffeine删除
    private void evictFromCaffeine(String key) {
        Cache cache = caffeineCacheManager.getCache("default");
        if (cache != null) {
            cache.evict(key);
        }
    }
    
    // 从Redis删除
    private void evictFromRedis(String key) {
        try {
            redisTemplate.delete(key);
        } catch (Exception e) {
            log.error("Failed to evict from Redis cache: " + key, e);
        }
    }
    
    // 清空Caffeine
    private void clearCaffeine() {
        Cache cache = caffeineCacheManager.getCache("default");
        if (cache != null) {
            cache.clear();
        }
    }
    
    // 清空Redis
    private void clearRedis() {
        try {
            Set<String> keys = redisTemplate.keys("*");
            if (!keys.isEmpty()) {
                redisTemplate.delete(keys);
            }
        } catch (Exception e) {
            log.error("Failed to clear Redis cache", e);
        }
    }
    
    // 获取缓存统计
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        
        // Caffeine统计
        Cache cache = caffeineCacheManager.getCache("default");
        if (cache instanceof CaffeineCache) {
            CaffeineCache caffeineCache = (CaffeineCache) cache;
            CacheStats caffeineStats = caffeineCache.getNativeCache().stats();
            
            stats.put("caffeine", Map.of(
                "hitCount", caffeineStats.hitCount(),
                "missCount", caffeineStats.missCount(),
                "hitRate", caffeineStats.hitRate(),
                "size", caffeineCache.getNativeCache().estimatedSize()
            ));
        }
        
        // Redis统计
        try {
            Properties info = redisTemplate.getConnectionFactory()
                .getConnection().info();
            stats.put("redis", Map.of(
                "usedMemory", info.getProperty("used_memory"),
                "connectedClients", info.getProperty("connected_clients"),
                "totalCommandsProcessed", info.getProperty("total_commands_processed")
            ));
        } catch (Exception e) {
            log.error("Failed to get Redis stats", e);
        }
        
        return stats;
    }
}
```

### 消息队列异步处理
```java
// 消息队列配置
@Configuration
@EnableRabbit
public class RabbitMQConfig {
    
    @Bean
    public ConnectionFactory connectionFactory() {
        CachingConnectionFactory connectionFactory = new CachingConnectionFactory("localhost");
        connectionFactory.setUsername("guest");
        connectionFactory.setPassword("guest");
        connectionFactory.setVirtualHost("/");
        
        // 连接池配置
        connectionFactory.setChannelCacheSize(25);
        connectionFactory.setConnectionCacheSize(5);
        
        // 发布确认
        connectionFactory.setPublisherConfirms(true);
        connectionFactory.setPublisherReturns(true);
        
        return connectionFactory;
    }
    
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(new Jackson2JsonMessageConverter());
        
        // 发布确认
        template.setConfirmCallback((correlationData, ack, cause) -> {
            if (ack) {
                log.info("Message confirmed: " + correlationData);
            } else {
                log.error("Message not confirmed: " + cause);
            }
        });
        
        // 返回消息
        template.setReturnCallback((message, replyCode, replyText, exchange, routingKey) -> {
            log.error("Message returned: " + message);
        });
        
        return template;
    }
    
    @Bean
    public Queue highPriorityQueue() {
        return QueueBuilder.durable("high.priority.queue")
            .withArgument("x-max-priority", 10)
            .build();
    }
    
    @Bean
    public Queue normalPriorityQueue() {
        return QueueBuilder.durable("normal.priority.queue")
            .withArgument("x-max-priority", 5)
            .build();
    }
    
    @Bean
    public Queue lowPriorityQueue() {
        return QueueBuilder.durable("low.priority.queue")
            .withArgument("x-max-priority", 1)
            .build();
    }
    
    @Bean
    public TopicExchange messageExchange() {
        return new TopicExchange("message.exchange", true, false);
    }
    
    @Bean
    public Binding highPriorityBinding() {
        return BindingBuilder.bind(highPriorityQueue())
            .to(messageExchange())
            .with("high.priority");
    }
    
    @Bean
    public Binding normalPriorityBinding() {
        return BindingBuilder.bind(normalPriorityQueue())
            .to(messageExchange())
            .with("normal.priority");
    }
    
    @Bean
    public Binding lowPriorityBinding() {
        return BindingBuilder.bind(lowPriorityQueue())
            .to(messageExchange())
            .with("low.priority");
    }
}

// 高并发消息生产者
@Service
public class HighConcurrencyMessageProducer {
    
    private final RabbitTemplate rabbitTemplate;
    private final MeterRegistry meterRegistry;
    
    public HighConcurrencyMessageProducer(RabbitTemplate rabbitTemplate,
                                          MeterRegistry meterRegistry) {
        this.rabbitTemplate = rabbitTemplate;
        this.meterRegistry = meterRegistry;
    }
    
    // 发送高优先级消息
    public void sendHighPriorityMessage(String routingKey, Object message) {
        sendWithPriority(routingKey, message, 10, "high.priority");
    }
    
    // 发送普通优先级消息
    public void sendNormalPriorityMessage(String routingKey, Object message) {
        sendWithPriority(routingKey, message, 5, "normal.priority");
    }
    
    // 发送低优先级消息
    public void sendLowPriorityMessage(String routingKey, Object message) {
        sendWithPriority(routingKey, message, 1, "low.priority");
    }
    
    // 批量发送消息
    public void sendBatchMessages(List<MessageRequest> requests) {
        requests.parallelStream().forEach(request -> {
            switch (request.getPriority()) {
                case HIGH:
                    sendHighPriorityMessage(request.getRoutingKey(), request.getMessage());
                    break;
                case NORMAL:
                    sendNormalPriorityMessage(request.getRoutingKey(), request.getMessage());
                    break;
                case LOW:
                    sendLowPriorityMessage(request.getRoutingKey(), request.getMessage());
                    break;
            }
        });
    }
    
    // 延迟发送消息
    public void sendDelayedMessage(String routingKey, Object message, Duration delay) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            rabbitTemplate.convertAndSend("message.exchange", routingKey, message, msg -> {
                msg.getMessageProperties().setDelay((int) delay.toMillis());
                msg.getMessageProperties().setPriority(5);
                return msg;
            });
            
            meterRegistry.counter("message.sent", Tags.of("type", "delayed")).increment();
            
        } finally {
            sample.stop(Timer.builder("message.send").register(meterRegistry));
        }
    }
    
    // 可靠发送（带重试）
    public void sendReliably(String routingKey, Object message, int maxRetries) {
        int retryCount = 0;
        
        while (retryCount < maxRetries) {
            try {
                rabbitTemplate.convertAndSend("message.exchange", routingKey, message);
                meterRegistry.counter("message.sent", Tags.of("type", "reliable")).increment();
                return;
                
            } catch (Exception e) {
                retryCount++;
                log.warn("Failed to send message, retry {}/{}: {}", retryCount, maxRetries, e.getMessage());
                
                if (retryCount >= maxRetries) {
                    meterRegistry.counter("message.failed", Tags.of("type", "reliable")).increment();
                    throw new RuntimeException("Failed to send message after " + maxRetries + " retries", e);
                }
                
                try {
                    Thread.sleep(1000 * retryCount); // 指数退避
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Interrupted during retry", ie);
                }
            }
        }
    }
    
    private void sendWithPriority(String routingKey, Object message, int priority, String type) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            rabbitTemplate.convertAndSend("message.exchange", routingKey, message, msg -> {
                msg.getMessageProperties().setPriority(priority);
                return msg;
            });
            
            meterRegistry.counter("message.sent", Tags.of("type", type)).increment();
            
        } catch (Exception e) {
            meterRegistry.counter("message.failed", Tags.of("type", type)).increment();
            throw e;
        } finally {
            sample.stop(Timer.builder("message.send").register(meterRegistry));
        }
    }
}

// 高并发消息消费者
@Service
public class HighConcurrencyMessageConsumer {
    
    private final MultiLevelCacheService cacheService;
    private final MeterRegistry meterRegistry;
    
    public HighConcurrencyMessageConsumer(MultiLevelCacheService cacheService,
                                        MeterRegistry meterRegistry) {
        this.cacheService = cacheService;
        this.meterRegistry = meterRegistry;
    }
    
    // 高优先级消息监听器
    @RabbitListener(queues = "high.priority.queue", concurrency = "5")
    public void handleHighPriorityMessage(@Payload Message message,
                                        @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag,
                                        Channel channel,
                                        MessageHeaders headers) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            processMessage(message, "HIGH");
            
            // 手动确认
            channel.basicAck(deliveryTag, false);
            
            meterRegistry.counter("message.processed", Tags.of("priority", "high")).increment();
            
        } catch (Exception e) {
            log.error("Failed to process high priority message", e);
            
            try {
                // 拒绝并重新入队
                channel.basicNack(deliveryTag, false, true);
                meterRegistry.counter("message.failed", Tags.of("priority", "high")).increment();
            } catch (IOException ioException) {
                log.error("Failed to nack message", ioException);
            }
        } finally {
            sample.stop(Timer.builder("message.process").register(meterRegistry));
        }
    }
    
    // 普通优先级消息监听器
    @RabbitListener(queues = "normal.priority.queue", concurrency = "3")
    public void handleNormalPriorityMessage(@Payload Message message,
                                           @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag,
                                           Channel channel) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            processMessage(message, "NORMAL");
            channel.basicAck(deliveryTag, false);
            
            meterRegistry.counter("message.processed", Tags.of("priority", "normal")).increment();
            
        } catch (Exception e) {
            log.error("Failed to process normal priority message", e);
            
            try {
                channel.basicNack(deliveryTag, false, false); // 不重新入队
                meterRegistry.counter("message.failed", Tags.of("priority", "normal")).increment();
            } catch (IOException ioException) {
                log.error("Failed to nack message", ioException);
            }
        } finally {
            sample.stop(Timer.builder("message.process").register(meterRegistry));
        }
    }
    
    // 低优先级消息监听器
    @RabbitListener(queues = "low.priority.queue", concurrency = "2")
    public void handleLowPriorityMessage(@Payload Message message,
                                         @Header(AmqpHeaders.DELIVERY_TAG) long deliveryTag,
                                         Channel channel) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        try {
            processMessage(message, "LOW");
            channel.basicAck(deliveryTag, false);
            
            meterRegistry.counter("message.processed", Tags.of("priority", "low")).increment();
            
        } catch (Exception e) {
            log.error("Failed to process low priority message", e);
            
            try {
                channel.basicNack(deliveryTag, false, false);
                meterRegistry.counter("message.failed", Tags.of("priority", "low")).increment();
            } catch (IOException ioException) {
                log.error("Failed to nack message", ioException);
            }
        } finally {
            sample.stop(Timer.builder("message.process").register(meterRegistry));
        }
    }
    
    private void processMessage(Message message, String priority) {
        // 模拟消息处理
        String cacheKey = "message:" + message.getId();
        
        // 检查缓存
        Message cachedMessage = cacheService.get(cacheKey, Message.class, () -> null);
        if (cachedMessage != null) {
            log.info("Message {} found in cache, skipping processing", message.getId());
            return;
        }
        
        // 处理消息
        try {
            Thread.sleep(50); // 模拟处理时间
            
            // 更新消息状态
            message.setStatus("PROCESSED");
            message.setProcessedAt(System.currentTimeMillis());
            
            // 缓存处理结果
            cacheService.put(cacheKey, message);
            
            log.info("Processed {} priority message: {}", priority, message.getId());
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Message processing interrupted", e);
        }
    }
}

// 消息请求
public class MessageRequest {
    private String routingKey;
    private Object message;
    private MessagePriority priority;
    
    // Getters and setters
    public String getRoutingKey() { return routingKey; }
    public void setRoutingKey(String routingKey) { this.routingKey = routingKey; }
    public Object getMessage() { return message; }
    public void setMessage(Object message) { this.message = message; }
    public MessagePriority getPriority() { return priority; }
    public void setPriority(MessagePriority priority) { this.priority = priority; }
}

// 消息优先级
public enum MessagePriority {
    HIGH, NORMAL, LOW
}
```

## 最佳实践

### 并发控制
1. **线程池优化**: 根据任务类型选择合适的线程池配置
2. **限流策略**: 使用令牌桶、漏桶等算法控制请求速率
3. **熔断机制**: 防止级联故障，保护系统稳定性
4. **异步处理**: 提高系统吞吐量，降低响应时间

### 缓存策略
1. **多级缓存**: 本地缓存 + 分布式缓存提高命中率
2. **缓存预热**: 提前加载热点数据
3. **缓存更新**: 合理的缓存失效和更新策略
4. **缓存穿透**: 使用布隆过滤器防止无效查询

### 系统扩展
1. **水平扩展**: 无状态设计，支持负载均衡
2. **服务拆分**: 按业务领域拆分微服务
3. **数据库分片**: 数据水平分片提高并发能力
4. **消息队列**: 异步处理解耦系统

### 监控运维
1. **性能监控**: 实时监控系统性能指标
2. **容量规划**: 提前规划系统容量
3. **自动扩容**: 根据负载自动调整资源
4. **故障恢复**: 快速故障检测和恢复

## 相关技能

- **cap-theorem** - CAP定理应用
- **distributed-consistency** - 分布式一致性
- **database-sharding** - 数据库分片
- **cache-invalidation** - 缓存失效
- **algorithm-advisor** - 算法顾问
