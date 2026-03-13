---
name: 分布式链路追踪
description: "当实现分布式链路追踪时，分析请求链路，优化系统监控，解决性能问题。验证追踪架构，设计监控系统，和最佳实践。"
license: MIT
---

# 分布式链路追踪技能

## 概述
分布式链路追踪是微服务架构中的关键监控技术，用于跟踪请求在多个服务间的完整调用链路。通过链路追踪可以快速定位性能瓶颈、故障根因，优化系统性能。不当的追踪实现会产生大量开销，影响系统性能。

**核心原则**: 好的链路追踪应该低侵入性、高性能、可视化、易扩展。坏的追踪会严重影响系统性能，数据量过大。

## 何时使用

**始终:**
- 构建微服务架构时
- 需要性能监控时
- 故障排查定位时
- 系统优化分析时
- 服务依赖分析时
- 用户体验监控时

**触发短语:**
- "如何实现链路追踪？"
- "分布式追踪方案选型"
- "链路追踪性能优化"
- "追踪数据存储策略"
- "服务调用链分析"
- "微服务监控体系"

## 分布式链路追踪技能功能

### 追踪采集
- Trace和Span生成
- 上下文传播
- 采样策略配置
- 自定义标签添加
- 异步追踪处理

### 数据存储
- 时序数据库存储
- 追踪数据压缩
- 数据生命周期管理
- 索引优化策略
- 分布式存储

### 可视化分析
- 调用链拓扑图
- 性能指标展示
- 热点服务识别
- 错误率统计
- 延迟分布分析

### 集成扩展
- 多语言SDK集成
- 框架自动埋点
- 第三方服务集成
- 自定义追踪器
- 监控告警集成

## 常见问题

### 性能问题
- **问题**: 追踪开销过大
- **原因**: 采样率过高，数据量过大
- **解决**: 优化采样策略，异步处理

- **问题**: 内存泄漏
- **原因**: 追踪数据未及时清理
- **解决**: 设置合理的TTL，定期清理

### 数据问题
- **问题**: 追踪数据不完整
- **原因**: 上下文传播失败
- **解决**: 完善上下文传递机制

- **问题**: 数据存储压力
- **原因**: 数据量增长过快
- **解决**: 数据压缩，分片存储

### 集成问题
- **问题**: 跨服务追踪断链
- **原因**: 协议不兼容，配置错误
- **解决**: 统一协议，标准化配置

## 代码示例

### Jaeger追踪实现
```java
// Jaeger配置
@Configuration
public class JaegerConfig {
    
    @Bean
    public io.jaegertracing.Configuration jaegerConfig() {
        return io.jaegertracing.Configuration.fromEnv("microservice-app")
            .withSampler(
                Configuration.SamplerConfiguration.fromEnv()
                    .withType("const")
                    .withParam(1)
            )
            .withReporter(
                Configuration.ReporterConfiguration.fromEnv()
                    .withLogSpans(true)
                    .withSender(
                        Configuration.SenderConfiguration.fromEnv()
                            .withAgentHost("localhost")
                            .withAgentPort(6831)
                    )
            );
    }
    
    @Bean
    public Tracer tracer(io.jaegertracing.Configuration config) {
        return config.getTracer();
    }
}

// 追踪拦截器
@Component
public class TracingInterceptor implements HandlerInterceptor {
    
    private final Tracer tracer;
    
    public TracingInterceptor(Tracer tracer) {
        this.tracer = tracer;
    }
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                           HttpServletResponse response, 
                           Object handler) throws Exception {
        
        Span span = tracer.buildSpan(request.getRequestURI())
            .withTag("http.method", request.getMethod())
            .withTag("http.url", request.getRequestURL().toString())
            .withTag("http.host", request.getServerName())
            .withTag("http.port", request.getServerPort())
            .start();
        
        // 将Span放入请求属性
        request.setAttribute("span", span);
        
        // 激活Span
        try (Scope scope = tracer.activateSpan(span)) {
            return true;
        }
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, 
                              HttpServletResponse response, 
                              Object handler, Exception ex) throws Exception {
        
        Span span = (Span) request.getAttribute("span");
        if (span != null) {
            span.setTag("http.status_code", response.getStatus());
            
            if (ex != null) {
                span.setTag("error", true);
                span.setTag("error.message", ex.getMessage());
                span.log("error occurred: " + ex.getMessage());
            }
            
            span.finish();
        }
    }
}

// 服务层追踪
@Service
public class UserService {
    
    private final Tracer tracer;
    private final OrderServiceClient orderServiceClient;
    
    public UserService(Tracer tracer, OrderServiceClient orderServiceClient) {
        this.tracer = tracer;
        this.orderServiceClient = orderServiceClient;
    }
    
    @Traced(operationName = "getUserById")
    public User getUserById(String userId) {
        Span span = tracer.activeSpan();
        
        try {
            // 添加业务标签
            span.setTag("user.id", userId);
            span.setTag("service.name", "user-service");
            
            // 模拟数据库查询
            User user = findUserInDatabase(userId);
            
            // 调用其他服务
            List<Order> orders = orderServiceClient.getOrdersByUserId(userId);
            user.setOrders(orders);
            
            span.setTag("user.found", user != null);
            return user;
            
        } catch (Exception e) {
            span.setTag("error", true);
            span.log("getUserById failed: " + e.getMessage());
            throw e;
        }
    }
    
    private User findUserInDatabase(String userId) {
        // 模拟数据库查询延迟
        try {
            Thread.sleep(ThreadLocalRandom.current().nextInt(50, 200));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        return User.builder()
            .id(userId)
            .name("User-" + userId)
            .email("user" + userId + "@example.com")
            .build();
    }
}

// 异步追踪
@Component
public class AsyncUserService {
    
    private final Tracer tracer;
    private final TaskExecutor taskExecutor;
    
    public AsyncUserService(Tracer tracer, TaskExecutor taskExecutor) {
        this.tracer = tracer;
        this.taskExecutor = taskExecutor;
    }
    
    @Async("taskExecutor")
    public CompletableFuture<User> getUserByIdAsync(String userId) {
        Span parentSpan = tracer.activeSpan();
        
        return CompletableFuture.supplyAsync(() -> {
            // 创建子Span
            Span span = tracer.buildSpan("async-getUserById")
                .asChildOf(parentSpan)
                .withTag("user.id", userId)
                .start();
            
            try (Scope scope = tracer.activateSpan(span)) {
                User user = findUserInDatabase(userId);
                span.setTag("user.found", user != null);
                return user;
            } catch (Exception e) {
                span.setTag("error", true);
                span.log("async-getUserById failed: " + e.getMessage());
                throw new RuntimeException(e);
            } finally {
                span.finish();
            }
        }, taskExecutor);
    }
    
    private User findUserInDatabase(String userId) {
        // 模拟异步数据库查询
        try {
            Thread.sleep(ThreadLocalRandom.current().nextInt(100, 300));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        return User.builder()
            .id(userId)
            .name("AsyncUser-" + userId)
            .email("asyncuser" + userId + "@example.com")
            .build();
    }
}
```

### OpenTelemetry集成
```java
// OpenTelemetry配置
@Configuration
public class OpenTelemetryConfig {
    
    @Bean
    public OpenTelemetry openTelemetry() {
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(
                JaegerGrpcSpanExporter.builder()
                    .setEndpoint("http://localhost:14250")
                    .build())
                .setScheduleDelay(Duration.ofSeconds(1))
                .setMaxExportBatchSize(512)
                .setMaxQueueSize(2048)
                .build())
            .setResource(Resource.getDefault()
                .toBuilder()
                .put(ResourceAttributes.SERVICE_NAME, "user-service")
                .put(ResourceAttributes.SERVICE_VERSION, "1.0.0")
                .build())
            .build();
        
        OpenTelemetry openTelemetry = OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setPropagators(ContextPropagators.create(
                TextMapPropagator.composite(
                    HttpTraceContext.injector(),
                    HttpBaggage.injector()
                )
            ))
            .build();
        
        // 添加JVM监控
        Runtime.getRuntime().addShutdownHook(new Thread(tracerProvider::close));
        
        return openTelemetry;
    }
    
    @Bean
    public Tracer tracer(OpenTelemetry openTelemetry) {
        return openTelemetry.getTracer("user-service-tracer");
    }
}

// OpenTelemetry追踪服务
@Service
public class TracingService {
    
    private final Tracer tracer;
    
    public TracingService(Tracer tracer) {
        this.tracer = tracer;
    }
    
    public void traceOperation(String operationName, Runnable operation) {
        Span span = tracer.spanBuilder(operationName)
            .setAttribute("operation.type", "custom")
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            operation.run();
            span.setAttribute("operation.status", "success");
        } catch (Exception e) {
            span.setAttribute("operation.status", "error");
            span.setAttribute("error.message", e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    public <T> T traceOperation(String operationName, Supplier<T> operation) {
        Span span = tracer.spanBuilder(operationName)
            .setAttribute("operation.type", "custom")
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            T result = operation.get();
            span.setAttribute("operation.status", "success");
            return result;
        } catch (Exception e) {
            span.setAttribute("operation.status", "error");
            span.setAttribute("error.message", e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    public <T> CompletableFuture<T> traceOperationAsync(
            String operationName, Supplier<CompletableFuture<T>> operation) {
        
        Span span = tracer.spanBuilder(operationName)
            .setAttribute("operation.type", "async")
            .startSpan();
        
        return operation.get().whenComplete((result, throwable) -> {
            if (throwable != null) {
                span.setAttribute("operation.status", "error");
                span.setAttribute("error.message", throwable.getMessage());
                span.recordException(throwable);
            } else {
                span.setAttribute("operation.status", "success");
            }
            span.end();
        });
    }
}

// 数据库追踪
@Repository
public class UserRepository {
    
    private final Tracer tracer;
    private final JdbcTemplate jdbcTemplate;
    
    public UserRepository(Tracer tracer, JdbcTemplate jdbcTemplate) {
        this.tracer = tracer;
        this.jdbcTemplate = jdbcTemplate;
    }
    
    public User findById(String id) {
        Span span = tracer.spanBuilder("user.findById")
            .setAttribute("db.system", "postgresql")
            .setAttribute("db.operation", "SELECT")
            .setAttribute("db.statement", "SELECT * FROM users WHERE id = ?")
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            String sql = "SELECT * FROM users WHERE id = ?";
            return jdbcTemplate.queryForObject(sql, new Object[]{id}, new UserRowMapper());
        } catch (Exception e) {
            span.setAttribute("error", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    public void save(User user) {
        Span span = tracer.spanBuilder("user.save")
            .setAttribute("db.system", "postgresql")
            .setAttribute("db.operation", "INSERT")
            .setAttribute("db.statement", "INSERT INTO users (id, name, email) VALUES (?, ?, ?)")
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            String sql = "INSERT INTO users (id, name, email) VALUES (?, ?, ?)";
            jdbcTemplate.update(sql, user.getId(), user.getName(), user.getEmail());
        } catch (Exception e) {
            span.setAttribute("error", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}

// HTTP客户端追踪
@Component
public class TracingRestTemplate {
    
    private final RestTemplate restTemplate;
    private final Tracer tracer;
    
    public TracingRestTemplate(Tracer tracer) {
        this.tracer = tracer;
        this.restTemplate = new RestTemplate();
        
        // 添加拦截器
        this.restTemplate.setInterceptors(
            Collections.singletonList(new TracingClientInterceptor(tracer))
        );
    }
    
    public <T> ResponseEntity<T> exchange(
            String url, HttpMethod method, HttpEntity<?> entity, 
            Class<T> responseType, Object... uriVariables) {
        
        return restTemplate.exchange(url, method, entity, responseType, uriVariables);
    }
}

// HTTP客户端追踪拦截器
public class TracingClientInterceptor implements ClientHttpRequestInterceptor {
    
    private final Tracer tracer;
    
    public TracingClientInterceptor(Tracer tracer) {
        this.tracer = tracer;
    }
    
    @Override
    public ClientHttpResponse intercept(
            HttpRequest request, byte[] body, 
            ClientHttpRequestExecution execution) throws IOException {
        
        Span span = tracer.spanBuilder("HTTP-" + request.getMethod().name())
            .setAttribute("http.method", request.getMethod().name())
            .setAttribute("http.url", request.getURI().toString())
            .setAttribute("http.host", request.getURI().getHost())
            .setAttribute("http.port", request.getURI().getPort())
            .setAttribute("http.scheme", request.getURI().getScheme())
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            ClientHttpResponse response = execution.execute(request, body);
            
            span.setAttribute("http.status_code", response.getStatusCode().value());
            span.setAttribute("http.status_text", response.getStatusCode().getReasonPhrase());
            
            if (response.getStatusCode().is4xxClientError() || 
                response.getStatusCode().is5xxServerError()) {
                span.setAttribute("error", true);
            }
            
            return response;
        } catch (Exception e) {
            span.setAttribute("error", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

### 自定义追踪器
```java
// 业务追踪器
@Component
public class BusinessTracer {
    
    private final Tracer tracer;
    
    public BusinessTracer(Tracer tracer) {
        this.tracer = tracer;
    }
    
    public void traceUserRegistration(UserRegistrationRequest request) {
        Span span = tracer.spanBuilder("user.registration")
            .setAttribute("business.process", "user-registration")
            .setAttribute("user.email", request.getEmail())
            .setAttribute("user.type", request.getUserType())
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 验证用户信息
            validateUserInfo(request);
            span.addEvent("user.info.validated");
            
            // 创建用户账户
            createUserAccount(request);
            span.addEvent("user.account.created");
            
            // 发送欢迎邮件
            sendWelcomeEmail(request.getEmail());
            span.addEvent("welcome.email.sent");
            
            span.setAttribute("registration.success", true);
            
        } catch (Exception e) {
            span.setAttribute("registration.success", false);
            span.setAttribute("error.message", e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    public void traceOrderProcessing(OrderRequest orderRequest) {
        Span span = tracer.spanBuilder("order.processing")
            .setAttribute("business.process", "order-processing")
            .setAttribute("order.id", orderRequest.getOrderId())
            .setAttribute("order.amount", orderRequest.getAmount())
            .setAttribute("order.currency", orderRequest.getCurrency())
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 检查库存
            checkInventory(orderRequest);
            span.addEvent("inventory.checked");
            
            // 计算价格
            calculatePrice(orderRequest);
            span.addEvent("price.calculated");
            
            // 处理支付
            processPayment(orderRequest);
            span.addEvent("payment.processed");
            
            // 更新库存
            updateInventory(orderRequest);
            span.addEvent("inventory.updated");
            
            // 发送确认邮件
            sendConfirmationEmail(orderRequest);
            span.addEvent("confirmation.email.sent");
            
            span.setAttribute("order.processed", true);
            
        } catch (Exception e) {
            span.setAttribute("order.processed", false);
            span.setAttribute("error.message", e.getMessage());
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    private void validateUserInfo(UserRegistrationRequest request) {
        // 实现用户信息验证逻辑
    }
    
    private void createUserAccount(UserRegistrationRequest request) {
        // 实现用户账户创建逻辑
    }
    
    private void sendWelcomeEmail(String email) {
        // 实现欢迎邮件发送逻辑
    }
    
    private void checkInventory(OrderRequest orderRequest) {
        // 实现库存检查逻辑
    }
    
    private void calculatePrice(OrderRequest orderRequest) {
        // 实现价格计算逻辑
    }
    
    private void processPayment(OrderRequest orderRequest) {
        // 实现支付处理逻辑
    }
    
    private void updateInventory(OrderRequest orderRequest) {
        // 实现库存更新逻辑
    }
    
    private void sendConfirmationEmail(OrderRequest orderRequest) {
        // 实现确认邮件发送逻辑
    }
}

// 性能追踪器
@Component
public class PerformanceTracer {
    
    private final Tracer tracer;
    
    public PerformanceTracer(Tracer tracer) {
        this.tracer = tracer;
    }
    
    public <T> T traceWithPerformance(String operationName, Supplier<T> operation) {
        Span span = tracer.spanBuilder(operationName)
            .setAttribute("performance.tracking", "true")
            .startSpan();
        
        long startTime = System.nanoTime();
        
        try (Scope scope = span.makeCurrent()) {
            T result = operation.get();
            
            long endTime = System.nanoTime();
            long duration = endTime - startTime;
            
            span.setAttribute("operation.duration.nanos", duration);
            span.setAttribute("operation.duration.ms", duration / 1_000_000);
            
            return result;
        } catch (Exception e) {
            span.setAttribute("operation.failed", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    public void traceWithPerformance(String operationName, Runnable operation) {
        Span span = tracer.spanBuilder(operationName)
            .setAttribute("performance.tracking", "true")
            .startSpan();
        
        long startTime = System.nanoTime();
        
        try (Scope scope = span.makeCurrent()) {
            operation.run();
            
            long endTime = System.nanoTime();
            long duration = endTime - startTime;
            
            span.setAttribute("operation.duration.nanos", duration);
            span.setAttribute("operation.duration.ms", duration / 1_000_000);
            
        } catch (Exception e) {
            span.setAttribute("operation.failed", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    public void traceMemoryUsage(String operationName, Runnable operation) {
        Span span = tracer.spanBuilder(operationName)
            .setAttribute("performance.tracking", "true")
            .setAttribute("memory.tracking", "true")
            .startSpan();
        
        Runtime runtime = Runtime.getRuntime();
        long beforeMemory = runtime.totalMemory() - runtime.freeMemory();
        
        try (Scope scope = span.makeCurrent()) {
            operation.run();
            
            long afterMemory = runtime.totalMemory() - runtime.freeMemory();
            long memoryUsed = afterMemory - beforeMemory;
            
            span.setAttribute("memory.used.bytes", memoryUsed);
            span.setAttribute("memory.used.mb", memoryUsed / (1024 * 1024));
            
        } catch (Exception e) {
            span.setAttribute("operation.failed", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

### 追踪数据分析
```java
// 追踪数据服务
@Service
public class TraceAnalysisService {
    
    private final Tracer tracer;
    private final MeterRegistry meterRegistry;
    
    public TraceAnalysisService(Tracer tracer, MeterRegistry meterRegistry) {
        this.tracer = tracer;
        this.meterRegistry = meterRegistry;
    }
    
    public void analyzeTracePerformance(String traceId) {
        Span span = tracer.spanBuilder("trace.analysis")
            .setAttribute("trace.id", traceId)
            .setAttribute("analysis.type", "performance")
            .startSpan();
        
        try (Scope scope = span.makeCurrent()) {
            // 获取追踪数据
            TraceData traceData = getTraceData(traceId);
            
            // 分析Span性能
            analyzeSpanPerformance(traceData);
            
            // 识别瓶颈
            identifyBottlenecks(traceData);
            
            // 生成报告
            generatePerformanceReport(traceData);
            
        } catch (Exception e) {
            span.setAttribute("analysis.failed", true);
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
    
    private TraceData getTraceData(String traceId) {
        // 从追踪系统获取数据
        return new TraceData();
    }
    
    private void analyzeSpanPerformance(TraceData traceData) {
        List<SpanData> spans = traceData.getSpans();
        
        for (SpanData span : spans) {
            long duration = span.getDuration();
            String operationName = span.getOperationName();
            
            // 记录性能指标
            meterRegistry.timer("span.duration", 
                "operation", operationName)
                .record(duration, TimeUnit.NANOSECONDS);
            
            // 慢操作告警
            if (duration > TimeUnit.SECONDS.toNanos(5)) {
                meterRegistry.counter("span.slow", 
                    "operation", operationName)
                    .increment();
                
                // 发送告警
                sendSlowOperationAlert(operationName, duration);
            }
        }
    }
    
    private void identifyBottlenecks(TraceData traceData) {
        List<SpanData> spans = traceData.getSpans();
        
        // 按持续时间排序
        spans.sort((a, b) -> Long.compare(b.getDuration(), a.getDuration()));
        
        // 识别最慢的操作
        if (!spans.isEmpty()) {
            SpanData slowestSpan = spans.get(0);
            long totalDuration = traceData.getTotalDuration();
            double percentage = (double) slowestSpan.getDuration() / totalDuration * 100;
            
            if (percentage > 50) {
                meterRegistry.counter("trace.bottleneck", 
                    "operation", slowestSpan.getOperationName())
                    .increment();
                
                sendBottleneckAlert(slowestSpan, percentage);
            }
        }
    }
    
    private void generatePerformanceReport(TraceData traceData) {
        PerformanceReport report = PerformanceReport.builder()
            .traceId(traceData.getTraceId())
            .totalDuration(traceData.getTotalDuration())
            .spanCount(traceData.getSpans().size())
            .errorCount(traceData.getErrorCount())
            .build();
        
        // 保存报告
        savePerformanceReport(report);
    }
    
    private void sendSlowOperationAlert(String operationName, long duration) {
        // 实现慢操作告警
    }
    
    private void sendBottleneckAlert(SpanData span, double percentage) {
        // 实现瓶颈告警
    }
    
    private void savePerformanceReport(PerformanceReport report) {
        // 实现报告保存
    }
}

// 追踪监控指标
@Component
public class TraceMetricsCollector {
    
    private final MeterRegistry meterRegistry;
    private final Tracer tracer;
    
    public TraceMetricsCollector(MeterRegistry meterRegistry, Tracer tracer) {
        this.meterRegistry = meterRegistry;
        this.tracer = tracer;
    }
    
    @EventListener
    public void handleSpanEvent(SpanEvent event) {
        switch (event.getType()) {
            case START:
                recordSpanStart(event);
                break;
            case END:
                recordSpanEnd(event);
                break;
            case ERROR:
                recordSpanError(event);
                break;
        }
    }
    
    private void recordSpanStart(SpanEvent event) {
        meterRegistry.counter("span.started",
            "operation", event.getOperationName(),
            "service", event.getServiceName())
            .increment();
    }
    
    private void recordSpanEnd(SpanEvent event) {
        SpanData span = event.getSpanData();
        
        // 记录持续时间
        meterRegistry.timer("span.duration",
            "operation", span.getOperationName(),
            "service", span.getServiceName())
            .record(span.getDuration(), TimeUnit.NANOSECONDS);
        
        // 记录吞吐量
        meterRegistry.counter("span.completed",
            "operation", span.getOperationName(),
            "service", span.getServiceName())
            .increment();
    }
    
    private void recordSpanError(SpanEvent event) {
        SpanData span = event.getSpanData();
        
        meterRegistry.counter("span.errors",
            "operation", span.getOperationName(),
            "service", span.getServiceName(),
            "error.type", span.getErrorType())
            .increment();
        
        // 错误率告警
        double errorRate = calculateErrorRate(span.getServiceName());
        if (errorRate > 0.05) { // 5%错误率告警
            sendErrorRateAlert(span.getServiceName(), errorRate);
        }
    }
    
    private double calculateErrorRate(String serviceName) {
        // 计算服务错误率
        return 0.0;
    }
    
    private void sendErrorRateAlert(String serviceName, double errorRate) {
        // 发送错误率告警
    }
}
```

## 最佳实践

### 采样策略
1. **合理采样**: 根据系统负载调整采样率
2. **分层采样**: 不同服务采用不同采样策略
3. **动态调整**: 根据系统状态动态调整采样率
4. **关键追踪**: 确保关键请求100%追踪

### 性能优化
1. **异步处理**: 使用异步方式处理追踪数据
2. **批量发送**: 批量发送追踪数据减少网络开销
3. **数据压缩**: 压缩追踪数据减少存储空间
4. **本地缓存**: 缓存追踪配置减少重复计算

### 数据管理
1. **生命周期管理**: 设置合理的数据保留期限
2. **分级存储**: 热数据快速访问，冷数据归档
3. **索引优化**: 优化查询索引提高检索效率
4. **数据清理**: 定期清理过期数据

### 监控告警
1. **实时监控**: 监控追踪系统本身的状态
2. **性能告警**: 设置性能指标告警阈值
3. **容量规划**: 监控存储容量及时扩容
4. **故障恢复**: 建立故障恢复机制

## 相关技能

- **api-gateway** - API网关设计
- **circuit-breaker** - 熔断器模式
- **service-discovery** - 服务发现
- **service-communication** - 服务间通信
- **backend** - 后端开发
