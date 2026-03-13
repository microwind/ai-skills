---
name: API网关设计
description: "当设计API网关时，分析路由策略，优化性能负载，解决安全问题。验证网关架构，设计统一入口，和最佳实践。"
license: MIT
---

# API网关设计技能

## 概述
API网关是微服务架构中的关键组件，作为所有客户端请求的统一入口点。API网关负责路由转发、负载均衡、认证授权、限流熔断、监控日志等功能。不当的网关设计会导致性能瓶颈、单点故障、安全风险。

**核心原则**: 好的API网关应该高性能、高可用、安全可靠、易于扩展。坏的网关会成为系统瓶颈，影响整个微服务架构。

## 何时使用

**始终:**
- 构建微服务架构时
- 需要统一API管理时
- 实现服务治理时
- 处理跨域请求时
- 实现API版本管理时
- 需要安全认证时

**触发短语:**
- "如何设计API网关？"
- "网关路由策略配置"
- "API网关性能优化"
- "网关安全认证方案"
- "微服务网关选型"
- "网关熔断降级策略"

## API网关设计技能功能

### 路由管理
- 请求路由转发
- 路径映射规则
- 负载均衡策略
- 服务发现集成
- 动态路由配置

### 安全控制
- 身份认证授权
- API密钥管理
- 请求验证过滤
- 跨域资源共享
- 安全策略配置

### 流量管理
- 限流控制
- 熔断降级
- 缓存策略
- 请求重试
- 流量分发

### 监控管理
- 请求日志记录
- 性能指标监控
- 错误追踪分析
- 健康检查
- 告警通知

## 常见问题

### 性能问题
- **问题**: 网关成为性能瓶颈
- **原因**: 单点架构，处理能力不足
- **解决**: 水平扩展，异步处理，缓存优化

- **问题**: 高并发下响应延迟
- **原因**: 同步阻塞处理，资源竞争
- **解决**: 异步非阻塞，连接池优化

### 可用性问题
- **问题**: 网关单点故障
- **原因**: 缺乏高可用设计
- **解决**: 集群部署，健康检查，故障转移

- **问题**: 服务依赖故障传播
- **原因**: 缺乏熔断机制
- **解决**: 实现熔断降级，超时控制

### 安全问题
- **问题**: API安全漏洞
- **原因**: 认证授权不完善
- **解决**: 多层安全防护，定期安全审计

## 代码示例

### 基础网关路由
```java
// Spring Cloud Gateway 路由配置
@Configuration
public class GatewayConfig {
    
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r.path("/api/users/**")
                .filters(f -> f.stripPrefix(2)
                    .circuitBreaker(config -> config.setName("userCircuit"))
                    .retry(retryConfig -> retryConfig.setRetries(3))
                    .requestRateLimiter(config -> config
                        .setKeyResolver(userKeyResolver())
                        .setRateLimit(100)))
                .uri("lb://user-service"))
            
            .route("order-service", r -> r.path("/api/orders/**")
                .filters(f -> f.stripPrefix(2)
                    .addRequestHeader("X-Request-Source", "gateway")
                    .addResponseHeader("X-Response-Source", "gateway"))
                .uri("lb://order-service"))
            
            .route("product-service", r -> r.path("/api/products/**")
                .filters(f -> f.stripPrefix(2)
                    .hystrix(config -> config.setName("productCircuit"))
                    .fallbackUri("forward:/fallback"))
                .uri("lb://product-service"))
            
            .build();
    }
    
    @Bean
    public KeyResolver userKeyResolver() {
        return exchange -> exchange.getRequest()
            .getHeaders().getFirst("X-User-ID")
            .map(userId -> (String) userId)
            .defaultIfEmpty("anonymous");
    }
}

// 自定义过滤器
@Component
public class AuthenticationFilter implements GlobalFilter, Ordered {
    
    @Autowired
    private JwtTokenUtil jwtTokenUtil;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 跳过认证的路径
        if (isPublicPath(request.getPath().value())) {
            return chain.filter(exchange);
        }
        
        // 验证JWT令牌
        String token = extractToken(request);
        if (token == null || !jwtTokenUtil.validateToken(token)) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        
        // 添加用户信息到请求头
        String username = jwtTokenUtil.getUsernameFromToken(token);
        ServerHttpRequest modifiedRequest = exchange.getRequest().mutate()
            .header("X-User-Name", username)
            .build();
        
        return chain.filter(exchange.mutate().request(modifiedRequest).build());
    }
    
    @Override
    public int getOrder() {
        return -100;
    }
    
    private boolean isPublicPath(String path) {
        return path.startsWith("/api/public/") || 
               path.equals("/api/auth/login") ||
               path.equals("/api/auth/register");
    }
    
    private String extractToken(ServerHttpRequest request) {
        String bearerToken = request.getHeaders().getFirst("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}

// 限流过滤器
@Component
public class RateLimitFilter implements GlobalFilter, Ordered {
    
    private final Map<String, RateLimiter> rateLimiters = new ConcurrentHashMap<>();
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String clientId = getClientId(exchange.getRequest());
        RateLimiter rateLimiter = rateLimiters.computeIfAbsent(clientId, 
            id -> RateLimiter.create(100.0)); // 每秒100个请求
        
        if (rateLimiter.tryAcquire()) {
            return chain.filter(exchange);
        } else {
            exchange.getResponse().setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
            return exchange.getResponse().setComplete();
        }
    }
    
    @Override
    public int getOrder() {
        return -50;
    }
    
    private String getClientId(ServerHttpRequest request) {
        return request.getHeaders().getFirst("X-Client-ID")
            .orElse(request.getRemoteAddress().getAddress().getHostAddress());
    }
}
```

### 熔断器配置
```java
// 熔断器配置
@Configuration
public class CircuitBreakerConfig {
    
    @Bean
    public ReactiveResilience4JCircuitBreakerFactory circuitBreakerFactory() {
        ReactiveResilience4JCircuitBreakerFactory factory = 
            new ReactiveResilience4JCircuitBreakerFactory();
        
        factory.configureDefault(id -> CircuitBreakerConfig.custom()
            .failureRateThreshold(50) // 失败率阈值50%
            .waitDurationInOpenState(Duration.ofSeconds(30)) // 熔断开启时间30秒
            .slidingWindowSize(10) // 滑动窗口大小
            .slidingWindowType(SlidingWindowType.COUNT_BASED) // 基于计数
            .minimumNumberOfCalls(5) // 最少调用次数
            .build());
        
        return factory;
    }
    
    @Bean
    public ReactiveResilience4JRetryFactory retryFactory() {
        ReactiveResilience4JRetryFactory factory = 
            new ReactiveResilience4JRetryFactory();
        
        factory.configureDefault(id -> RetryConfig.custom()
            .maxAttempts(3) // 最大重试次数
            .waitDuration(Duration.ofSeconds(1)) // 重试间隔
            .retryExceptions(IOException.class, TimeoutException.class) // 重试异常
            .build());
        
        return factory;
    }
}

// 降级处理
@Component
public class FallbackHandler {
    
    public Mono<ServerResponse> userFallback(ServerRequest request) {
        Map<String, Object> body = new HashMap<>();
        body.put("code", 503);
        body.put("message", "用户服务暂时不可用，请稍后重试");
        body.put("timestamp", System.currentTimeMillis());
        
        return ServerResponse.status(HttpStatus.SERVICE_UNAVAILABLE)
            .contentType(MediaType.APPLICATION_JSON)
            .body(BodyInserters.fromValue(body));
    }
    
    public Mono<ServerResponse> orderFallback(ServerRequest request) {
        Map<String, Object> body = new HashMap<>();
        body.put("code", 503);
        body.put("message", "订单服务暂时不可用，请稍后重试");
        body.put("timestamp", System.currentTimeMillis());
        
        return ServerResponse.status(HttpStatus.SERVICE_UNAVAILABLE)
            .contentType(MediaType.APPLICATION_JSON)
            .body(BodyInserters.fromValue(body));
    }
}
```

### 负载均衡策略
```java
// 自定义负载均衡策略
@Component
public class CustomLoadBalancer implements ReactorServiceInstanceLoadBalancer {
    
    private final String serviceId;
    private final ServiceInstanceListSupplier serviceInstanceListSupplier;
    
    public CustomLoadBalancer(String serviceId, 
                             ServiceInstanceListSupplier serviceInstanceListSupplier) {
        this.serviceId = serviceId;
        this.serviceInstanceListSupplier = serviceInstanceListSupplier;
    }
    
    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        return serviceInstanceListSupplier.get().next()
            .map(instances -> selectInstance(instances, request));
    }
    
    private Response<ServiceInstance> selectInstance(
            List<ServiceInstance> instances, Request request) {
        if (instances.isEmpty()) {
            return new DefaultResponse(null);
        }
        
        // 基于权重的负载均衡
        return new DefaultResponse(weightedRoundRobin(instances));
    }
    
    private ServiceInstance weightedRoundRobin(List<ServiceInstance> instances) {
        // 计算总权重
        int totalWeight = instances.stream()
            .mapToInt(instance -> getWeight(instance))
            .sum();
        
        // 随机选择
        int randomWeight = ThreadLocalRandom.current().nextInt(totalWeight);
        
        int currentWeight = 0;
        for (ServiceInstance instance : instances) {
            currentWeight += getWeight(instance);
            if (randomWeight < currentWeight) {
                return instance;
            }
        }
        
        return instances.get(0);
    }
    
    private int getWeight(ServiceInstance instance) {
        Map<String, String> metadata = instance.getMetadata();
        return Integer.parseInt(metadata.getOrDefault("weight", "1"));
    }
}

// 健康检查
@Component
public class HealthCheckService {
    
    private final Map<String, ServiceHealth> serviceHealthMap = new ConcurrentHashMap<>();
    
    @Scheduled(fixedRate = 30000) // 每30秒检查一次
    public void performHealthChecks() {
        serviceHealthMap.forEach((serviceId, health) -> {
            boolean isHealthy = checkServiceHealth(health.getInstance());
            health.updateHealth(isHealthy);
            
            if (!isHealthy) {
                log.warn("Service {} is unhealthy: {}", serviceId, health.getLastError());
            }
        });
    }
    
    private boolean checkServiceHealth(ServiceInstance instance) {
        try {
            String healthUrl = String.format("http://%s:%s/actuator/health",
                instance.getHost(), instance.getPort());
            
            ResponseEntity<String> response = restTemplate.getForEntity(healthUrl, String.class);
            return response.getStatusCode().is2xxSuccessful();
        } catch (Exception e) {
            log.error("Health check failed for service {}", instance.getInstanceId(), e);
            return false;
        }
    }
    
    public boolean isServiceHealthy(String serviceId) {
        ServiceHealth health = serviceHealthMap.get(serviceId);
        return health != null && health.isHealthy();
    }
}
```

### 缓存配置
```java
// Redis缓存配置
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10)) // 缓存10分钟
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .transactionAware()
            .build();
    }
}

// 缓存过滤器
@Component
public class CacheFilter implements GlobalFilter, Ordered {
    
    @Autowired
    private CacheManager cacheManager;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String cacheKey = generateCacheKey(request);
        
        // 检查缓存
        Cache cache = cacheManager.getCache("api-cache");
        String cachedResponse = cache.get(cacheKey, String.class);
        
        if (cachedResponse != null) {
            ServerHttpResponse response = exchange.getResponse();
            response.setStatusCode(HttpStatus.OK);
            response.getHeaders().add("Content-Type", "application/json");
            response.getHeaders().add("X-Cache", "HIT");
            
            DataBuffer buffer = response.bufferFactory().wrap(cachedResponse.getBytes());
            return response.writeWith(Mono.just(buffer));
        }
        
        // 缓存未命中，继续处理
        return chain.filter(exchange)
            .then(Mono.fromRunnable(() -> {
                // 缓存响应
                ServerHttpResponse response = exchange.getResponse();
                if (response.getStatusCode().is2xxSuccessful()) {
                    cache.put(cacheKey, getResponseBody(response));
                    response.getHeaders().add("X-Cache", "MISS");
                }
            }));
    }
    
    @Override
    public int getOrder() {
        return -200;
    }
    
    private String generateCacheKey(ServerHttpRequest request) {
        return request.getMethod().name() + ":" + 
               request.getPath().value() + ":" + 
               request.getQueryParams().toSingleValueMap().hashCode();
    }
    
    private String getResponseBody(ServerHttpResponse response) {
        // 实现获取响应体的逻辑
        return "";
    }
}
```

### 监控和日志
```java
// 请求监控
@Component
public class RequestMonitor {
    
    private final MeterRegistry meterRegistry;
    private final Timer.Sample sample;
    
    public RequestMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.sample = Timer.start(meterRegistry);
    }
    
    @EventListener
    public void handleRequestEvent(RequestEvent event) {
        switch (event.getType()) {
            case REQUEST_DATA_RECEIVED:
                sample.start(Timer.builder("gateway.request")
                    .tag("method", event.getRoute().getUri().getMethod())
                    .tag("path", event.getRoute().getId())
                    .register(meterRegistry));
                break;
                
            case RESPONSE_DATA_RECEIVED:
                sample.stop(Timer.builder("gateway.request")
                    .tag("status", String.valueOf(event.getResponse().getStatusCode().value()))
                    .register(meterRegistry));
                break;
                
            case EXCEPTION:
                meterRegistry.counter("gateway.errors",
                    "exception", event.getThrowable().getClass().getSimpleName())
                    .increment();
                break;
        }
    }
}

// 日志过滤器
@Component
public class LoggingFilter implements GlobalFilter, Ordered {
    
    private static final Logger log = LoggerFactory.getLogger(LoggingFilter.class);
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        long startTime = System.currentTimeMillis();
        
        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;
            
            ServerHttpRequest request = exchange.getRequest();
            ServerHttpResponse response = exchange.getResponse();
            
            log.info("Gateway Request: {} {} - Status: {} - Duration: {}ms",
                request.getMethod().name(),
                request.getPath().value(),
                response.getStatusCode().value(),
                duration);
        }));
    }
    
    @Override
    public int getOrder() {
        return Ordered.LOWEST_PRECEDENCE;
    }
}
```

## 最佳实践

### 架构设计
1. **高可用性**: 集群部署，故障转移
2. **性能优化**: 异步处理，连接池，缓存
3. **安全防护**: 多层认证，输入验证
4. **监控告警**: 全面监控，及时告警

### 路由配置
1. **路径规划**: 合理的路径结构
2. **负载均衡**: 多种负载策略
3. **服务发现**: 动态服务注册
4. **版本管理**: API版本控制

### 安全控制
1. **身份认证**: JWT、OAuth2.0
2. **权限控制**: RBAC权限模型
3. **数据加密**: 传输加密，存储加密
4. **安全审计**: 访问日志，安全扫描

### 运维管理
1. **配置管理**: 统一配置中心
2. **部署策略**: 蓝绿部署，滚动更新
3. **容量规划**: 性能测试，容量评估
4. **故障处理**: 故障恢复，应急预案

## 相关技能

- **service-mesh-analyzer** - 服务网格分析
- **distributed-tracing** - 分布式追踪
- **circuit-breaker** - 熔断器模式
- **service-discovery** - 服务发现
- **backend** - 后端开发
