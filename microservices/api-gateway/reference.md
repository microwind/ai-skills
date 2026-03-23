# API网关参考文档

## API网关概述

### 什么是API网关
API网关是微服务架构中的关键组件，作为所有客户端请求的统一入口点。它负责请求路由、负载均衡、安全认证、监控日志等功能。

### 核心功能
- **请求路由**: 将请求转发到相应的后端服务
- **负载均衡**: 在多个服务实例间分配请求
- **安全认证**: 统一的认证和授权管理
- **监控日志**: 请求监控、日志记录和性能分析
- **缓存管理**: 响应缓存和性能优化
- **熔断降级**: 服务保护机制和故障处理

### 主要优势
- **简化客户端**: 客户端只需与网关交互
- **统一管理**: 集中管理安全、监控和路由
- **提高性能**: 通过缓存和负载均衡优化性能
- **增强安全**: 统一的安全策略和防护机制
- **便于维护**: 集中化的配置和管理

## 主流API网关

### Spring Cloud Gateway

#### 核心概念
```java
// 路由配置示例
@Configuration
public class GatewayConfig {
    
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r.path("/api/users/**")
                .filters(f -> f.filter(authFilter)
                    .filter(rateLimitFilter)
                    .retry(3))
                .uri("lb://user-service"))
            .route("order-service", r -> r.path("/api/orders/**")
                .filters(f -> f.circuitBreaker("order-service"))
                .uri("lb://order-service"))
            .build();
    }
}
```

#### 过滤器配置
```java
// 自定义过滤器
@Component
public class AuthFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 验证JWT Token
        String token = request.getHeaders().getFirst("Authorization");
        if (!isValidToken(token)) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        
        return chain.filter(exchange);
    }
    
    @Override
    public int getOrder() {
        return -100; // 高优先级
    }
}
```

#### 配置文件
```yaml
# application.yml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - AddRequestHeader=X-Request-Foo, Bar
            - AddRequestParameter=param, value
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true
```

### Kong

#### 核心架构
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│ Kong Gateway│───▶│   Service   │
└─────────────┘    └─────────────┘    └─────────────┘
                        │
                        ▼
                   ┌─────────────┐
                   │   Database  │
                   │ (PostgreSQL)│
                   └─────────────┘
```

#### 服务配置
```bash
# 创建服务
curl -X POST http://localhost:8001/services \
  --data "name=user-service" \
  --data "url=http://user-service:8080"

# 创建路由
curl -X POST http://localhost:8001/services/user-service/routes \
  --data "hosts[]=example.com" \
  --data "paths[]=/api/users"

# 添加插件
curl -X POST http://localhost:8001/services/user-service/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100" \
  --data "config.hour=1000"
```

#### 插件配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  kong:
    image: kong:3.4
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    ports:
      - "8000:8000"  # Proxy port
      - "8001:8001"  # Admin port
    networks:
      - kong-net

  kong-database:
    image: postgres:15
    environment:
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: kong
      POSTGRES_DB: kong
    ports:
      - "5432:5432"
    networks:
      - kong-net

networks:
  kong-net:
    driver: bridge
```

### Nginx + Lua

#### OpenResty配置
```nginx
# nginx.conf
worker_processes 1;
error_log logs/error.log warn;

events {
    worker_connections 1024;
}

http {
    upstream user_service {
        server user-service1:8080;
        server user-service2:8080;
        least_conn;
    }

    upstream order_service {
        server order-service1:8080;
        server order-service2:8080;
    }

    # 限流配置
    lua_shared_dict my_limit_conn_store 100m;
    lua_shared_dict my_limit_req_store 100m;

    init_by_lua_block {
        require "resty.core"
    }

    server {
        listen 80;
        
        # API路由
        location /api/users/ {
            default_type 'application/json';
            
            # 认证检查
            access_by_lua_block {
                local token = ngx.var.http_authorization
                if not token then
                    ngx.exit(ngx.HTTP_UNAUTHORIZED)
                end
                
                -- JWT验证逻辑
                local jwt = require "resty.jwt"
                local jwt_obj = jwt:verify_jwt_obj("your-secret", token)
                if not jwt_obj.valid then
                    ngx.exit(ngx.HTTP_UNAUTHORIZED)
                end
            }
            
            # 限流
            limit_req zone=my_limit_req burst=10 nodelay;
            
            proxy_pass http://user_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /api/orders/ {
            # 熔断检查
            access_by_lua_block {
                local circuit_breaker = require "circuit_breaker"
                if not circuit_breaker:allow_request("order_service") then
                    ngx.exit(ngx.HTTP_SERVICE_UNAVAILABLE)
                end
            }
            
            proxy_pass http://order_service;
        }
    }
}
```

#### Lua脚本示例
```lua
-- circuit_breaker.lua
local _M = {}

local circuit_breakers = {}

function _M.allow_request(service_name)
    local cb = circuit_breakers[service_name]
    if not cb then
        cb = {
            state = "CLOSED",
            failure_count = 0,
            success_count = 0,
            last_failure_time = 0,
            failure_threshold = 5,
            recovery_timeout = 60,
            success_threshold = 3
        }
        circuit_breakers[service_name] = cb
    end
    
    if cb.state == "OPEN" then
        if ngx.time() - cb.last_failure_time > cb.recovery_timeout then
            cb.state = "HALF_OPEN"
            cb.success_count = 0
        else
            return false
        end
    end
    
    return true
end

function _M.record_success(service_name)
    local cb = circuit_breakers[service_name]
    if not cb then return end
    
    if cb.state == "HALF_OPEN" then
        cb.success_count = cb.success_count + 1
        if cb.success_count >= cb.success_threshold then
            cb.state = "CLOSED"
            cb.failure_count = 0
        end
    else
        cb.failure_count = 0
    end
end

function _M.record_failure(service_name)
    local cb = circuit_breakers[service_name]
    if not cb then return end
    
    cb.failure_count = cb.failure_count + 1
    cb.last_failure_time = ngx.time()
    
    if cb.failure_count >= cb.failure_threshold then
        cb.state = "OPEN"
    end
end

return _M
```

## 路由策略

### 路径匹配策略

#### 精确匹配
```yaml
# Spring Cloud Gateway
spring:
  cloud:
    gateway:
      routes:
        - id: exact-match
          uri: lb://user-service
          predicates:
            - Path=/api/users/123
```

#### 前缀匹配
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: prefix-match
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=2  # 移除前两个路径段
```

#### 正则匹配
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: regex-match
          uri: lb://user-service
          predicates:
            - Path=/api/v[0-9]+/users/**
          filters:
            - SetPath=/api/users/{segment}
```

### 条件路由

#### 多条件组合
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: multi-condition
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
            - Method=GET,POST
            - Header=X-Request-Source, mobile
            - Query=version, v1
            - Host=**.example.com
```

#### 权重路由
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: weight-route-v1
          uri: lb://user-service-v1
          predicates:
            - Weight=user-service, 80
        - id: weight-route-v2
          uri: lb://user-service-v2
          predicates:
            - Weight=user-service, 20
```

## 安全策略

### JWT认证

#### JWT验证实现
```java
@Component
public class JwtAuthenticationFilter implements GlobalFilter {
    
    @Value("${jwt.secret}")
    private String jwtSecret;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 跳过公开路径
        if (isPublicPath(request.getPath().value())) {
            return chain.filter(exchange);
        }
        
        String authHeader = request.getHeaders().getFirst("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return handleUnauthorized(exchange);
        }
        
        String token = authHeader.substring(7);
        try {
            Claims claims = Jwts.parser()
                .setSigningKey(jwtSecret)
                .parseClaimsJws(token)
                .getBody();
            
            // 将用户信息添加到请求头
            ServerHttpRequest modifiedRequest = request.mutate()
                .header("X-User-ID", claims.getSubject())
                .header("X-User-Roles", String.join(",", claims.get("roles", List.class)))
                .build();
            
            return chain.filter(exchange.mutate().request(modifiedRequest).build());
        } catch (Exception e) {
            return handleUnauthorized(exchange);
        }
    }
    
    private boolean isPublicPath(String path) {
        return path.startsWith("/api/public/") || 
               path.equals("/api/auth/login") || 
               path.equals("/api/auth/register");
    }
    
    private Mono<Void> handleUnauthorized(ServerWebExchange exchange) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().add("Content-Type", "application/json");
        
        String body = "{\"error\":\"Unauthorized\",\"message\":\"Invalid or missing token\"}";
        DataBuffer buffer = response.bufferFactory().wrap(body.getBytes());
        return response.writeWith(Mono.just(buffer));
    }
}
```

### OAuth2集成

#### OAuth2配置
```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          gateway:
            client-id: gateway-client
            client-secret: ${OAUTH2_CLIENT_SECRET}
            authorization-grant-type: authorization_code
            redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
            scope: openid,profile,email
        provider:
          gateway:
            authorization-uri: https://auth.example.com/oauth/authorize
            token-uri: https://auth.example.com/oauth/token
            user-info-uri: https://auth.example.com/oauth/userinfo
            user-name-attribute: sub
```

#### OAuth2过滤器
```java
@Component
public class OAuth2AuthenticationFilter implements GlobalFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 检查是否有有效的OAuth2 token
        String token = extractToken(request);
        if (token == null) {
            return redirectToAuth(exchange);
        }
        
        // 验证token
        return validateToken(token)
            .flatMap(isValid -> {
                if (isValid) {
                    return chain.filter(exchange);
                } else {
                    return redirectToAuth(exchange);
                }
            });
    }
    
    private String extractToken(ServerHttpRequest request) {
        // 从请求头或cookie中提取token
        String authHeader = request.getHeaders().getFirst("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.substring(7);
        }
        
        HttpCookie cookie = request.getCookies().getFirst("access_token");
        return cookie != null ? cookie.getValue() : null;
    }
    
    private Mono<Void> redirectToAuth(ServerWebExchange exchange) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.FOUND);
        response.getHeaders().add("Location", "/oauth2/authorization/gateway");
        return response.setComplete();
    }
    
    private Mono<Boolean> validateToken(String token) {
        // 调用OAuth2服务验证token
        return webClient.get()
            .uri("https://auth.example.com/oauth/introspect")
            .header("Authorization", "Bearer " + token)
            .retrieve()
            .bodyToMono(Map.class)
            .map(map -> Boolean.TRUE.equals(map.get("active")))
            .defaultIfEmpty(false);
    }
}
```

### API限流

#### Redis限流实现
```java
@Component
public class RateLimitFilter implements GlobalFilter, Ordered {
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String clientId = getClientId(exchange.getRequest());
        String key = "rate_limit:" + clientId;
        
        // 使用令牌桶算法
        return redisTemplate.opsForZSet().add(key, String.valueOf(System.currentTimeMillis()), 1)
            .flatMap(score -> {
                // 移除过期令牌
                long now = System.currentTimeMillis();
                redisTemplate.opsForZSet().removeRangeByScore(key, 0, now - 60000);
                
                // 检查当前令牌数
                return redisTemplate.opsForZSet().count(key, now - 60000, now);
            })
            .flatMap(count -> {
                if (count > 100) {  // 每分钟最多100个请求
                    return handleRateLimitExceeded(exchange);
                }
                return chain.filter(exchange);
            });
    }
    
    private String getClientId(ServerHttpRequest request) {
        // 根据IP、用户ID等生成客户端标识
        String ip = request.getHeaders().getFirst("X-Forwarded-For");
        if (ip == null) {
            ip = request.getRemoteAddress().getAddress().getHostAddress();
        }
        return ip;
    }
    
    private Mono<Void> handleRateLimitExceeded(ServerWebExchange exchange) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
        response.getHeaders().add("X-RateLimit-Limit", "100");
        response.getHeaders().add("X-RateLimit-Remaining", "0");
        response.getHeaders().add("X-RateLimit-Reset", String.valueOf(System.currentTimeMillis() + 60000));
        
        String body = "{\"error\":\"Rate limit exceeded\",\"message\":\"Too many requests\"}";
        DataBuffer buffer = response.bufferFactory().wrap(body.getBytes());
        return response.writeWith(Mono.just(buffer));
    }
    
    @Override
    public int getOrder() {
        return -200; // 高优先级
    }
}
```

## 监控和日志

### Prometheus监控

#### 监控指标配置
```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5,0.9,0.95,0.99
```

#### 自定义监控指标
```java
@Component
public class GatewayMetrics {
    
    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Timer responseTimer;
    
    public GatewayMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder("gateway_requests_total")
            .description("Total number of requests")
            .tag("method", "unknown")
            .tag("status", "unknown")
            .register(meterRegistry);
        
        this.responseTimer = Timer.builder("gateway_response_time")
            .description("Response time")
            .register(meterRegistry);
    }
    
    public void recordRequest(String method, int status) {
        requestCounter
            .tag("method", method)
            .tag("status", String.valueOf(status))
            .increment();
    }
    
    public Timer.Sample startTimer() {
        return Timer.start(meterRegistry);
    }
    
    public void recordResponseTime(Timer.Sample sample) {
        sample.stop(responseTimer);
    }
}
```

### 分布式追踪

#### Jaeger集成
```yaml
# application.yml
spring:
  sleuth:
    sampler:
      probability: 1.0  # 100% 采样率
    zipkin:
      base-url: http://jaeger:9411
    jaeger:
      base-url: http://jaeger:14268
      sender:
        type: http
```

#### 追踪配置
```java
@Component
public class TracingFilter implements GlobalFilter {
    
    @Autowired
    private Tracer tracer;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        Span span = tracer.nextSpan()
            .name("gateway-request")
            .tag("http.method", exchange.getRequest().getMethod().name())
            .tag("http.url", exchange.getRequest().getURI().toString())
            .start();
        
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
            return chain.filter(exchange)
                .doOnSuccess(aVoid -> {
                    span.tag("http.status_code", 
                        String.valueOf(exchange.getResponse().getStatusCode().value()));
                    span.end();
                })
                .doOnError(error -> {
                    span.tag("error", error.getMessage());
                    span.end();
                });
        }
    }
}
```

## 性能优化

### 缓存策略

#### Redis缓存配置
```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .build();
    }
}
```

#### 缓存过滤器
```java
@Component
public class CacheFilter implements GlobalFilter {
    
    @Autowired
    private CacheManager cacheManager;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 只缓存GET请求
        if (!request.getMethod().equals(HttpMethod.GET)) {
            return chain.filter(exchange);
        }
        
        String cacheKey = generateCacheKey(request);
        Cache cache = cacheManager.getCache("gateway-cache");
        
        // 尝试从缓存获取响应
        String cachedResponse = cache.get(cacheKey, String.class);
        if (cachedResponse != null) {
            ServerHttpResponse response = exchange.getResponse();
            response.getHeaders().add("X-Cache", "HIT");
            response.getHeaders().add("Content-Type", "application/json");
            
            DataBuffer buffer = response.bufferFactory()
                .wrap(cachedResponse.getBytes(StandardCharsets.UTF_8));
            return response.writeWith(Mono.just(buffer));
        }
        
        // 缓存未命中，继续处理请求
        return chain.filter(exchange)
            .doOnSuccess(aVoid -> {
                // 缓存响应
                ServerHttpResponse response = exchange.getResponse();
                if (response.getStatusCode().is2xxSuccessful()) {
                    response.getHeaders().add("X-Cache", "MISS");
                    // 这里需要捕获响应体进行缓存
                }
            });
    }
    
    private String generateCacheKey(ServerHttpRequest request) {
        return request.getURI().toString() + "#" + 
               request.getQueryParams().toSingleValueMap().toString();
    }
}
```

### 连接池优化

#### HTTP客户端配置
```java
@Configuration
public class HttpClientConfig {
    
    @Bean
    public WebClient webClient() {
        return WebClient.builder()
            .clientConnector(new ReactorClientHttpConnector(
                HttpClient.create()
                    .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
                    .responseTimeout(Duration.ofSeconds(10))
                    .keepAlive(true)
                    .compress(true)
            ))
            .build();
    }
}
```

## 故障处理

### 熔断器配置

#### Resilience4j熔断器
```java
@Configuration
public class CircuitBreakerConfig {
    
    @Bean
    public CircuitBreaker circuitBreaker() {
        return CircuitBreaker.ofDefaults("gateway-circuit-breaker");
    }
    
    @Bean
    public CircuitBreakerFilter circuitBreakerFilter() {
        return new CircuitBreakerFilter(circuitBreaker());
    }
}

@Component
public class CircuitBreakerFilter implements GlobalFilter {
    
    private final CircuitBreaker circuitBreaker;
    
    public CircuitBreakerFilter(CircuitBreaker circuitBreaker) {
        this.circuitBreaker = circuitBreaker;
    }
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        return circuitBreaker.executeSupplier(() -> 
            chain.filter(exchange)
                .onErrorResume(throwable -> {
                    return handleCircuitBreakerOpen(exchange);
                })
        );
    }
    
    private Mono<Void> handleCircuitBreakerOpen(ServerWebExchange exchange) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.SERVICE_UNAVAILABLE);
        response.getHeaders().add("Content-Type", "application/json");
        
        String body = "{\"error\":\"Service Unavailable\",\"message\":\"Circuit breaker is open\"}";
        DataBuffer buffer = response.bufferFactory().wrap(body.getBytes());
        return response.writeWith(Mono.just(buffer));
    }
}
```

### 重试机制

#### 重试配置
```java
@Component
public class RetryFilter implements GlobalFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        return chain.filter(exchange)
            .retryWhen(Retry.backoff(3, Duration.ofSeconds(1))
                .maxBackoff(Duration.ofSeconds(10))
                .doBeforeRetry(retrySignal -> {
                    log.warn("Retrying request: attempt {}", retrySignal.totalRetries() + 1);
                })
                .onRetryExhaustedThrow((retryBackoffSpec, retrySignal) -> {
                    return new RetryExhaustedException("Retry exhausted", retrySignal.failure());
                }));
    }
}
```

## 最佳实践

### 安全最佳实践

#### 1. 零信任架构
```yaml
# 所有请求都需要认证
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com
```

#### 2. 最小权限原则
```java
// 基于角色的访问控制
@Component
public class RoleBasedAccessFilter implements GlobalFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String path = exchange.getRequest().getPath().value();
        String userRole = getUserRole(exchange);
        
        if (!hasPermission(userRole, path)) {
            return handleForbidden(exchange);
        }
        
        return chain.filter(exchange);
    }
    
    private boolean hasPermission(String role, String path) {
        Map<String, List<String>> rolePermissions = Map.of(
            "ADMIN", List.of("/api/**"),
            "USER", List.of("/api/users/**", "/api/orders/**"),
            "GUEST", List.of("/api/public/**")
        );
        
        return rolePermissions.getOrDefault(role, List.of())
            .stream()
            .anyMatch(path::startsWith);
    }
}
```

### 性能最佳实践

#### 1. 连接池配置
```yaml
spring:
  cloud:
    gateway:
      httpclient:
        pool:
          max-connections: 500
          max-idle-time: 30s
          max-life-time: 60s
        connect-timeout: 5000
        response-timeout: 30s
```

#### 2. 缓存策略
```java
// 智能缓存策略
@Component
public class SmartCacheFilter implements GlobalFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        
        // 根据请求特征决定缓存策略
        CacheStrategy strategy = determineCacheStrategy(request);
        
        switch (strategy) {
            case AGGRESSIVE:
                return aggressiveCache(exchange, chain);
            case CONSERVATIVE:
                return conservativeCache(exchange, chain);
            case NO_CACHE:
                return chain.filter(exchange);
            default:
                return chain.filter(exchange);
        }
    }
    
    private CacheStrategy determineCacheStrategy(ServerHttpRequest request) {
        String path = request.getPath().value();
        String userAgent = request.getHeaders().getFirst("User-Agent");
        
        // 移动端请求使用激进缓存
        if (userAgent != null && userAgent.contains("Mobile")) {
            return CacheStrategy.AGGRESSIVE;
        }
        
        // API调用使用保守缓存
        if (path.startsWith("/api/")) {
            return CacheStrategy.CONSERVATIVE;
        }
        
        return CacheStrategy.NO_CACHE;
    }
}
```

### 监控最佳实践

#### 1. 关键指标监控
```java
@Component
public class CriticalMetricsFilter implements GlobalFilter {
    
    private final MeterRegistry meterRegistry;
    
    public CriticalMetricsFilter(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        Timer.Sample sample = Timer.start(meterRegistry);
        
        return chain.filter(exchange)
            .doOnSuccess(aVoid -> {
                recordMetrics(exchange, sample);
            })
            .doOnError(error -> {
                recordErrorMetrics(exchange, error, sample);
            });
    }
    
    private void recordMetrics(ServerWebExchange exchange, Timer.Sample sample) {
        String method = exchange.getRequest().getMethod().name();
        String path = exchange.getRequest().getPath().value();
        int status = exchange.getResponse().getStatusCode().value();
        
        // 记录请求计数
        meterRegistry.counter("gateway.requests", 
            "method", method, 
            "path", path, 
            "status", String.valueOf(status))
            .increment();
        
        // 记录响应时间
        sample.stop(Timer.builder("gateway.response.time")
            .tag("method", method)
            .tag("path", path)
            .register(meterRegistry));
        
        // 记录错误率
        if (status >= 400) {
            meterRegistry.counter("gateway.errors",
                "method", method,
                "path", path,
                "status", String.valueOf(status))
                .increment();
        }
    }
}
```

## 参考资源

### 官方文档
- [Spring Cloud Gateway Documentation](https://spring.io/projects/spring-cloud-gateway)
- [Kong Documentation](https://docs.konghq.com/)
- [OpenResty Documentation](https://openresty.org/en/documentation.html)
- [Nginx Documentation](https://nginx.org/en/docs/)

### 最佳实践指南
- [API Gateway Best Practices](https://microservices.io/patterns/apigateway.html)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Cloud Native Patterns](https://patterns.cloudnativeops.com/)

### 社区资源
- [API Gateway Community](https://github.com/topics/api-gateway)
- [Microservices on CNCF](https://cncf.io/)
- [Cloud Native Computing Foundation](https://www.cncf.io/)
