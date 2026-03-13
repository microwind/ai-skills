---
name: 服务间通信
description: "当设计服务间通信时，分析通信协议，优化消息传递，解决网络问题。验证通信架构，设计可靠传输，和最佳实践。"
license: MIT
---

# 服务间通信技能

## 概述
服务间通信是微服务架构的核心，定义了服务之间如何交换数据和协调工作。选择合适的通信模式、协议和技术对系统的性能、可靠性和可维护性至关重要。不当的通信设计会导致性能瓶颈、服务耦合、故障传播。

**核心原则**: 好的服务通信应该松耦合、高性能、容错性强、可扩展性好。坏的通信会导致紧耦合、性能差、故障扩散。

## 何时使用

**始终:**
- 构建微服务架构时
- 设计服务接口时
- 处理服务调用时
- 实现消息传递时
- 优化系统性能时
- 处理分布式事务时

**触发短语:**
- "如何选择通信协议？"
- "服务间通信最佳实践"
- "REST vs gRPC vs 消息队列"
- "异步通信设计"
- "服务调用链优化"
- "微服务通信模式"

## 服务间通信技能功能

### 通信模式
- 同步通信
- 异步通信
- 事件驱动架构
- 请求响应模式
- 发布订阅模式

### 协议选择
- HTTP/REST
- gRPC
- WebSocket
- 消息队列
- 事件流

### 性能优化
- 连接池管理
- 负载均衡
- 缓存策略
- 批量处理
- 压缩传输

### 可靠性保障
- 重试机制
- 熔断降级
- 超时控制
- 幂等性设计
- 事务一致性

## 常见问题

### 性能问题
- **问题**: 通信延迟过高
- **原因**: 网络延迟、序列化开销、连接数不足
- **解决**: 优化协议、连接复用、数据压缩

- **问题**: 吞吐量不足
- **原因**: 单线程处理、资源竞争、I/O阻塞
- **解决**: 异步处理、连接池、批量操作

### 可靠性问题
- **问题**: 服务调用失败
- **原因**: 网络故障、服务不可用、超时设置不当
- **解决**: 重试机制、熔断器、健康检查

- **问题**: 数据不一致
- **原因**: 分布式事务处理不当
- **解决**: 幂等性设计、补偿机制、最终一致性

### 耦合问题
- **问题**: 服务间强耦合
- **原因**: 直接依赖、紧耦合接口
- **解决**: 引入中介、事件驱动、API版本管理

## 代码示例

### REST通信实现
```java
// REST客户端配置
@Configuration
public class RestClientConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        
        // 设置连接池
        HttpComponentsClientHttpRequestFactory factory = 
            new HttpComponentsClientHttpRequestFactory();
        factory.setConnectTimeout(5000);
        factory.setReadTimeout(10000);
        
        // 配置连接池
        PoolingHttpClientConnectionManager connectionManager = 
            new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(200);
        connectionManager.setDefaultMaxPerRoute(50);
        
        CloseableHttpClient httpClient = HttpClients.custom()
            .setConnectionManager(connectionManager)
            .build();
        
        factory.setHttpClient(httpClient);
        restTemplate.setRequestFactory(factory);
        
        // 添加拦截器
        restTemplate.setInterceptors(Arrays.asList(
            new LoggingInterceptor(),
            new RetryInterceptor(),
            new AuthenticationInterceptor()
        ));
        
        return restTemplate;
    }
    
    @Bean
    public WebClient webClient() {
        return WebClient.builder()
            .baseUrl("http://user-service")
            .clientConnector(new ReactorClientHttpConnector(
                HttpClient.create()
                    .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
                    .responseTimeout(Duration.ofSeconds(10))
                    .keepAlive(true)
            ))
            .filter(new RetryFilter())
            .filter(new AuthenticationFilter())
            .build();
    }
}

// 用户服务客户端
@Service
public class UserServiceClient {
    
    private final RestTemplate restTemplate;
    private final WebClient webClient;
    private final CircuitBreaker circuitBreaker;
    
    @Value("${user.service.url}")
    private String userServiceUrl;
    
    public UserServiceClient(RestTemplate restTemplate, 
                           WebClient webClient,
                           CircuitBreaker circuitBreaker) {
        this.restTemplate = restTemplate;
        this.webClient = webClient;
        this.circuitBreaker = circuitBreaker;
    }
    
    // 同步REST调用
    public User getUserById(String userId) {
        String url = userServiceUrl + "/api/users/" + userId;
        
        return circuitBreaker.executeSupplier(() -> {
            try {
                ResponseEntity<User> response = restTemplate.getForEntity(url, User.class);
                return response.getBody();
            } catch (HttpClientErrorException e) {
                if (e.getStatusCode() == HttpStatus.NOT_FOUND) {
                    throw new UserNotFoundException("User not found: " + userId);
                }
                throw e;
            }
        });
    }
    
    // 异步REST调用
    public CompletableFuture<User> getUserByIdAsync(String userId) {
        String url = "/api/users/" + userId;
        
        return webClient.get()
            .uri(url)
            .retrieve()
            .bodyToMono(User.class)
            .toFuture()
            .exceptionally(throwable -> {
                if (throwable instanceof WebClientResponseException) {
                    WebClientResponseException ex = (WebClientResponseException) throwable;
                    if (ex.getStatusCode() == HttpStatus.NOT_FOUND) {
                        throw new UserNotFoundException("User not found: " + userId);
                    }
                }
                throw new RuntimeException("Failed to get user: " + userId, throwable);
            });
    }
    
    // 批量获取用户
    public List<User> getUsersByIds(List<String> userIds) {
        String url = userServiceUrl + "/api/users/batch";
        
        return circuitBreaker.executeSupplier(() -> {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<List<String>> request = new HttpEntity<>(userIds, headers);
            ResponseEntity<List<User>> response = restTemplate.exchange(
                url, HttpMethod.POST, request, 
                new ParameterizedTypeReference<List<User>>() {}
            );
            
            return response.getBody();
        });
    }
    
    // 创建用户
    public User createUser(UserCreateRequest request) {
        String url = userServiceUrl + "/api/users";
        
        return circuitBreaker.executeSupplier(() -> {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<UserCreateRequest> entity = new HttpEntity<>(request, headers);
            ResponseEntity<User> response = restTemplate.postForEntity(url, entity, User.class);
            
            return response.getBody();
        });
    }
    
    // 更新用户
    public User updateUser(String userId, UserUpdateRequest request) {
        String url = userServiceUrl + "/api/users/" + userId;
        
        return circuitBreaker.executeSupplier(() -> {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<UserUpdateRequest> entity = new HttpEntity<>(request, headers);
            ResponseEntity<User> response = restTemplate.exchange(
                url, HttpMethod.PUT, entity, User.class);
            
            return response.getBody();
        });
    }
}

// 重试拦截器
public class RetryInterceptor implements ClientHttpRequestInterceptor {
    
    private final RetryTemplate retryTemplate;
    
    public RetryInterceptor() {
        this.retryTemplate = new RetryTemplate();
        
        // 配置重试策略
        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy(3);
        ExponentialBackOffPolicy backOffPolicy = new ExponentialBackOffPolicy();
        backOffPolicy.setInitialInterval(1000);
        backOffPolicy.setMultiplier(2);
        backOffPolicy.setMaxInterval(10000);
        
        retryTemplate.setRetryPolicy(retryPolicy);
        retryTemplate.setBackOffPolicy(backOffPolicy);
    }
    
    @Override
    public ClientHttpResponse intercept(
            HttpRequest request, byte[] body, 
            ClientHttpRequestExecution execution) throws IOException {
        
        return retryTemplate.execute(context -> {
            try {
                return execution.execute(request, body);
            } catch (IOException e) {
                throw new RetryableException("Retryable exception", e);
            }
        });
    }
}

// 日志拦截器
public class LoggingInterceptor implements ClientHttpRequestInterceptor {
    
    private static final Logger logger = LoggerFactory.getLogger(LoggingInterceptor.class);
    
    @Override
    public ClientHttpResponse intercept(
            HttpRequest request, byte[] body, 
            ClientHttpRequestExecution execution) throws IOException {
        
        long startTime = System.currentTimeMillis();
        
        // 记录请求
        logger.info("Request: {} {} - Headers: {}", 
            request.getMethod(), request.getURI(), request.getHeaders());
        
        try {
            ClientHttpResponse response = execution.execute(request, body);
            
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;
            
            // 记录响应
            logger.info("Response: {} - Duration: {}ms", 
                response.getStatusCode(), duration);
            
            return response;
        } catch (Exception e) {
            long endTime = System.currentTimeMillis();
            long duration = endTime - startTime;
            
            logger.error("Request failed: {} {} - Duration: {}ms - Error: {}", 
                request.getMethod(), request.getURI(), duration, e.getMessage());
            
            throw e;
        }
    }
}
```

### gRPC通信实现
```java
// gRPC配置
@Configuration
public class GrpcConfig {
    
    @Bean
    public ManagedChannel userServiceChannel() {
        return ManagedChannelBuilder.forAddress("localhost", 9090)
            .usePlaintext()
            .keepAliveTime(30, TimeUnit.SECONDS)
            .keepAliveTimeout(5, TimeUnit.SECONDS)
            .keepAliveWithoutCalls(true)
            .maxInboundMessageSize(10 * 1024 * 1024) // 10MB
            .build();
    }
    
    @Bean
    public UserServiceGrpc.UserServiceBlockingStub userServiceBlockingStub(
            ManagedChannel channel) {
        return UserServiceGrpc.newBlockingStub(channel)
            .withDeadlineAfter(5, TimeUnit.SECONDS);
    }
    
    @Bean
    public UserServiceGrpc.UserServiceFutureStub userServiceFutureStub(
            ManagedChannel channel) {
        return UserServiceGrpc.newFutureStub(channel)
            .withDeadlineAfter(5, TimeUnit.SECONDS);
    }
    
    @Bean
    public UserServiceGrpc.UserServiceStub userServiceStub(
            ManagedChannel channel) {
        return UserServiceGrpc.newStub(channel)
            .withDeadlineAfter(5, TimeUnit.SECONDS);
    }
}

// gRPC客户端服务
@Service
public class UserGrpcClient {
    
    private final UserServiceGrpc.UserServiceBlockingStub blockingStub;
    private final UserServiceGrpc.UserServiceFutureStub futureStub;
    private final UserServiceGrpc.UserServiceStub asyncStub;
    
    public UserGrpcClient(UserServiceGrpc.UserServiceBlockingStub blockingStub,
                          UserServiceGrpc.UserServiceFutureStub futureStub,
                          UserServiceGrpc.UserServiceStub asyncStub) {
        this.blockingStub = blockingStub;
        this.futureStub = futureStub;
        this.asyncStub = asyncStub;
    }
    
    // 同步调用
    public User getUserById(String userId) {
        GetUserRequest request = GetUserRequest.newBuilder()
            .setUserId(userId)
            .build();
        
        try {
            GetUserResponse response = blockingStub.getUser(request);
            return convertToUser(response.getUser());
        } catch (StatusRuntimeException e) {
            if (e.getStatus().getCode() == Status.Code.NOT_FOUND) {
                throw new UserNotFoundException("User not found: " + userId);
            }
            throw new RuntimeException("Failed to get user: " + userId, e);
        }
    }
    
    // 异步调用
    public CompletableFuture<User> getUserByIdAsync(String userId) {
        GetUserRequest request = GetUserRequest.newBuilder()
            .setUserId(userId)
            .build();
        
        ListenableFuture<GetUserResponse> future = futureStub.getUser(request);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                GetUserResponse response = future.get();
                return convertToUser(response.getUser());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("Interrupted", e);
            } catch (ExecutionException e) {
                Throwable cause = e.getCause();
                if (cause instanceof StatusRuntimeException) {
                    StatusRuntimeException sre = (StatusRuntimeException) cause;
                    if (sre.getStatus().getCode() == Status.Code.NOT_FOUND) {
                        throw new UserNotFoundException("User not found: " + userId);
                    }
                }
                throw new RuntimeException("Failed to get user: " + userId, cause);
            }
        });
    }
    
    // 流式调用
    public StreamObserver<User> getUsersByIdsStream(List<String> userIds, 
                                                   Consumer<User> resultHandler,
                                                   Consumer<Throwable> errorHandler) {
        StreamObserver<GetUsersResponse> responseObserver = new StreamObserver<GetUsersResponse>() {
            @Override
            public void onNext(GetUsersResponse response) {
                resultHandler.accept(convertToUser(response.getUser()));
            }
            
            @Override
            public void onError(Throwable t) {
                errorHandler.accept(t);
            }
            
            @Override
            public void onCompleted() {
                // 流完成
            }
        };
        
        StreamObserver<GetUsersRequest> requestObserver = asyncStub.getUsersStream(responseObserver);
        
        // 发送请求
        for (String userId : userIds) {
            GetUsersRequest request = GetUsersRequest.newBuilder()
                .setUserId(userId)
                .build();
            requestObserver.onNext(request);
        }
        
        requestObserver.onCompleted();
        return responseObserver;
    }
    
    // 双向流调用
    public StreamObserver<User> userEventStream(
            Consumer<User> resultHandler,
            Consumer<Throwable> errorHandler) {
        
        StreamObserver<UserEventResponse> responseObserver = new StreamObserver<UserEventResponse>() {
            @Override
            public void onNext(UserEventResponse response) {
                resultHandler.accept(convertToUser(response.getUser()));
            }
            
            @Override
            public void onError(Throwable t) {
                errorHandler.accept(t);
            }
            
            @Override
            public void onCompleted() {
                // 流完成
            }
        };
        
        return asyncStub.userEventStream(responseObserver);
    }
    
    private User convertToUser(UserProto.User protoUser) {
        return User.builder()
            .id(protoUser.getId())
            .name(protoUser.getName())
            .email(protoUser.getEmail())
            .status(protoUser.getStatus())
            .createdAt(Instant.ofEpochMilli(protoUser.getCreatedAt()))
            .updatedAt(Instant.ofEpochMilli(protoUser.getUpdatedAt()))
            .build();
    }
}

// gRPC拦截器
@Component
public class GrpcClientInterceptor implements ClientInterceptor {
    
    private static final Logger logger = LoggerFactory.getLogger(GrpcClientInterceptor.class);
    
    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
            MethodDescriptor<ReqT, RespT> method,
            CallOptions callOptions,
            Channel next) {
        
        return new ForwardingClientCall.SimpleForwardingClientCall<ReqT, RespT>(
            next.newCall(method, callOptions)) {
            
            @Override
            public void start(Listener<RespT> responseListener, Metadata headers) {
                // 添加认证信息
                headers.put(Metadata.Key.of("authorization", Metadata.ASCII_STRING_MARSHALLER), 
                           "Bearer " + getCurrentToken());
                
                // 添加追踪信息
                headers.put(Metadata.Key.of("trace-id", Metadata.ASCII_STRING_MARSHALLER), 
                           getCurrentTraceId());
                
                super.start(new ForwardingClientCallListener.SimpleForwardingClientCallListener<RespT>(responseListener) {
                    @Override
                    public void onHeaders(Metadata headers) {
                        logger.info("gRPC Response headers: {}", headers);
                        super.onHeaders(headers);
                    }
                    
                    @Override
                    public void onMessage(RespT message) {
                        logger.info("gRPC Response message: {}", message);
                        super.onMessage(message);
                    }
                    
                    @Override
                    public void onClose(Status status, Metadata trailers) {
                        if (!status.isOk()) {
                            logger.error("gRPC call failed: {}", status);
                        }
                        super.onClose(status, trailers);
                    }
                }, headers);
            }
            
            @Override
            public void sendMessage(ReqT message) {
                logger.info("gRPC Request message: {}", message);
                super.sendMessage(message);
            }
        };
    }
    
    private String getCurrentToken() {
        // 获取当前用户的认证令牌
        return "current-token";
    }
    
    private String getCurrentTraceId() {
        // 获取当前追踪ID
        return "trace-id-" + UUID.randomUUID().toString();
    }
}
```

### 消息队列通信
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
        connectionFactory.setPublisherConfirms(true);
        connectionFactory.setPublisherReturns(true);
        return connectionFactory;
    }
    
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(new Jackson2JsonMessageConverter());
        template.setMandatory(true);
        template.setConfirmCallback((correlationData, ack, cause) -> {
            if (ack) {
                logger.info("Message confirmed: {}", correlationData);
            } else {
                logger.error("Message not confirmed: {} - {}", correlationData, cause);
            }
        });
        template.setReturnCallback((message, replyCode, replyText, exchange, routingKey) -> {
            logger.error("Message returned: {} - {} - {} - {}", 
                message, replyCode, replyText, exchange, routingKey);
        });
        return template;
    }
    
    @Bean
    public Queue userQueue() {
        return QueueBuilder.durable("user.queue")
            .withArgument("x-dead-letter-exchange", "user.dlx")
            .withArgument("x-dead-letter-routing-key", "user.dlq")
            .build();
    }
    
    @Bean
    public DirectExchange userExchange() {
        return new DirectExchange("user.exchange");
    }
    
    @Bean
    public Binding userBinding() {
        return BindingBuilder.bind(userQueue())
            .to(userExchange())
            .with("user.created");
    }
    
    @Bean
    public Queue userDeadLetterQueue() {
        return QueueBuilder.durable("user.dlq").build();
    }
    
    @Bean
    public DirectExchange userDeadLetterExchange() {
        return new DirectExchange("user.dlx");
    }
    
    @Bean
    public Binding userDeadLetterBinding() {
        return BindingBuilder.bind(userDeadLetterQueue())
            .to(userDeadLetterExchange())
            .with("user.dlq");
    }
}

// 消息发送服务
@Service
public class MessagePublisher {
    
    private final RabbitTemplate rabbitTemplate;
    private final ApplicationEventPublisher eventPublisher;
    
    public MessagePublisher(RabbitTemplate rabbitTemplate,
                           ApplicationEventPublisher eventPublisher) {
        this.rabbitTemplate = rabbitTemplate;
        this.eventPublisher = eventPublisher;
    }
    
    // 发送用户创建事件
    public void publishUserCreatedEvent(User user) {
        UserCreatedEvent event = UserCreatedEvent.builder()
            .userId(user.getId())
            .name(user.getName())
            .email(user.getEmail())
            .createdAt(user.getCreatedAt())
            .build();
        
        Message message = MessageBuilder
            .withBody(event)
            .setContentType(MessageProperties.CONTENT_TYPE_JSON)
            .setHeader("event-type", "user.created")
            .setHeader("event-version", "1.0")
            .setHeader("timestamp", System.currentTimeMillis())
            .build();
        
        rabbitTemplate.send("user.exchange", "user.created", message);
        
        // 发布本地事件
        eventPublisher.publishEvent(new UserCreatedLocalEvent(user));
    }
    
    // 发送用户更新事件
    public void publishUserUpdatedEvent(User user, Map<String, Object> changes) {
        UserUpdatedEvent event = UserUpdatedEvent.builder()
            .userId(user.getId())
            .changes(changes)
            .updatedAt(user.getUpdatedAt())
            .build();
        
        Message message = MessageBuilder
            .withBody(event)
            .setContentType(MessageProperties.CONTENT_TYPE_JSON)
            .setHeader("event-type", "user.updated")
            .setHeader("event-version", "1.0")
            .setHeader("timestamp", System.currentTimeMillis())
            .build();
        
        rabbitTemplate.send("user.exchange", "user.updated", message);
    }
    
    // 发送订单创建事件
    public void publishOrderCreatedEvent(Order order) {
        OrderCreatedEvent event = OrderCreatedEvent.builder()
            .orderId(order.getId())
            .userId(order.getUserId())
            .amount(order.getAmount())
            .currency(order.getCurrency())
            .createdAt(order.getCreatedAt())
            .build();
        
        Message message = MessageBuilder
            .withBody(event)
            .setContentType(MessageProperties.CONTENT_TYPE_JSON)
            .setHeader("event-type", "order.created")
            .setHeader("event-version", "1.0")
            .setHeader("timestamp", System.currentTimeMillis())
            .setExpiration("300000") // 5分钟过期
            .build();
        
        rabbitTemplate.send("order.exchange", "order.created", message);
    }
    
    // 延迟消息发送
    public void publishDelayedMessage(String exchange, String routingKey, Object message, long delayMillis) {
        Message delayedMessage = MessageBuilder
            .withBody(message)
            .setContentType(MessageProperties.CONTENT_TYPE_JSON)
            .setHeader("x-delay", delayMillis)
            .build();
        
        rabbitTemplate.send(exchange, routingKey, delayedMessage);
    }
    
    // 事务性消息发送
    @Transactional
    public void publishTransactionalMessage(String exchange, String routingKey, Object message) {
        rabbitTemplate.send(exchange, routingKey, message);
        // 如果事务回滚，消息也会被回滚
    }
}

// 消息监听服务
@Component
public class MessageListener {
    
    private static final Logger logger = LoggerFactory.getLogger(MessageListener.class);
    
    @RabbitListener(queues = "user.queue")
    public void handleUserCreatedEvent(UserCreatedEvent event, 
                                      @Header Map<String, Object> headers) {
        try {
            logger.info("Received user created event: {}", event);
            
            // 处理用户创建事件
            processUserCreatedEvent(event);
            
            // 确认消息
            logger.info("Processed user created event: {}", event.getUserId());
            
        } catch (Exception e) {
            logger.error("Failed to process user created event: {}", event.getUserId(), e);
            throw new AmqpRejectAndDontRequeueException("Failed to process event", e);
        }
    }
    
    @RabbitListener(queues = "user.queue")
    public void handleUserUpdatedEvent(UserUpdatedEvent event,
                                      @Header Map<String, Object> headers) {
        try {
            logger.info("Received user updated event: {}", event);
            
            // 处理用户更新事件
            processUserUpdatedEvent(event);
            
            logger.info("Processed user updated event: {}", event.getUserId());
            
        } catch (Exception e) {
            logger.error("Failed to process user updated event: {}", event.getUserId(), e);
            throw new AmqpRejectAndDontRequeueException("Failed to process event", e);
        }
    }
    
    @RabbitListener(queues = "order.queue")
    public void handleOrderCreatedEvent(OrderCreatedEvent event,
                                      @Header Map<String, Object> headers) {
        try {
            logger.info("Received order created event: {}", event);
            
            // 处理订单创建事件
            processOrderCreatedEvent(event);
            
            logger.info("Processed order created event: {}", event.getOrderId());
            
        } catch (Exception e) {
            logger.error("Failed to process order created event: {}", event.getOrderId(), e);
            throw new AmqpRejectAndDontRequeueException("Failed to process event", e);
        }
    }
    
    // 死信队列处理
    @RabbitListener(queues = "user.dlq")
    public void handleDeadLetterMessage(Message message, 
                                       @Header Map<String, Object> headers) {
        logger.error("Received dead letter message: {}", message);
        
        // 分析失败原因
        String errorReason = (String) headers.get("x-death-reason");
        String failedExchange = (String) headers.get("x-death-exchange");
        String failedRoutingKey = (String) headers.get("x-death-routing-key");
        
        logger.error("Dead letter reason: {}, exchange: {}, routing key: {}", 
            errorReason, failedExchange, failedRoutingKey);
        
        // 根据情况决定是否重新处理或人工干预
        handleDeadLetter(message, headers);
    }
    
    private void processUserCreatedEvent(UserCreatedEvent event) {
        // 实现用户创建事件处理逻辑
        // 例如：发送欢迎邮件、初始化用户数据等
    }
    
    private void processUserUpdatedEvent(UserUpdatedEvent event) {
        // 实现用户更新事件处理逻辑
        // 例如：更新缓存、同步到其他系统等
    }
    
    private void processOrderCreatedEvent(OrderCreatedEvent event) {
        // 实现订单创建事件处理逻辑
        // 例如：库存扣减、发送确认邮件等
    }
    
    private void handleDeadLetter(Message message, Map<String, Object> headers) {
        // 实现死信消息处理逻辑
        // 例如：记录到数据库、发送告警等
    }
}
```

### 事件驱动架构
```java
// 事件定义
@Data
@Builder
public class UserCreatedEvent {
    private String userId;
    private String name;
    private String email;
    private Instant createdAt;
}

@Data
@Builder
public class UserUpdatedEvent {
    private String userId;
    private Map<String, Object> changes;
    private Instant updatedAt;
}

@Data
@Builder
public class OrderCreatedEvent {
    private String orderId;
    private String userId;
    private BigDecimal amount;
    private String currency;
    private Instant createdAt;
}

// 事件处理器接口
public interface EventHandler<T> {
    void handle(T event);
    boolean canHandle(String eventType);
    String getEventType();
}

// 用户事件处理器
@Component
public class UserEventHandler implements EventHandler<UserCreatedEvent> {
    
    private final EmailService emailService;
    private final CacheService cacheService;
    
    public UserEventHandler(EmailService emailService, CacheService cacheService) {
        this.emailService = emailService;
        this.cacheService = cacheService;
    }
    
    @Override
    public void handle(UserCreatedEvent event) {
        // 发送欢迎邮件
        emailService.sendWelcomeEmail(event.getEmail(), event.getName());
        
        // 初始化用户缓存
        cacheService.initializeUserCache(event.getUserId());
        
        // 记录审计日志
        auditService.logUserCreation(event);
    }
    
    @Override
    public boolean canHandle(String eventType) {
        return "user.created".equals(eventType);
    }
    
    @Override
    public String getEventType() {
        return "user.created";
    }
}

// 事件总线
@Component
public class EventBus {
    
    private final Map<String, List<EventHandler>> handlers = new ConcurrentHashMap<>();
    private final ApplicationEventPublisher eventPublisher;
    
    public EventBus(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }
    
    @Autowired
    public void registerHandlers(List<EventHandler> eventHandlers) {
        for (EventHandler handler : eventHandlers) {
            registerHandler(handler);
        }
    }
    
    public void registerHandler(EventHandler handler) {
        handlers.computeIfAbsent(handler.getEventType(), k -> new ArrayList<>())
                 .add(handler);
    }
    
    public void publish(Object event) {
        String eventType = determineEventType(event);
        List<EventHandler> eventHandlers = handlers.get(eventType);
        
        if (eventHandlers != null) {
            for (EventHandler handler : eventHandlers) {
                try {
                    handler.handle(event);
                } catch (Exception e) {
                    handleEventProcessingError(event, handler, e);
                }
            }
        }
        
        // 发布Spring事件
        eventPublisher.publishEvent(event);
    }
    
    private String determineEventType(Object event) {
        if (event instanceof UserCreatedEvent) {
            return "user.created";
        } else if (event instanceof UserUpdatedEvent) {
            return "user.updated";
        } else if (event instanceof OrderCreatedEvent) {
            return "order.created";
        }
        return event.getClass().getSimpleName().toLowerCase();
    }
    
    private void handleEventProcessingError(Object event, EventHandler handler, Exception e) {
        logger.error("Error processing event {} with handler {}", 
            event.getClass().getSimpleName(), handler.getClass().getSimpleName(), e);
        
        // 可以实现重试、死信队列等机制
    }
}

// 事件存储（用于事件溯源）
@Repository
public class EventStore {
    
    private final JdbcTemplate jdbcTemplate;
    
    public EventStore(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }
    
    public void saveEvent(String aggregateId, Object event, int version) {
        String sql = """
            INSERT INTO event_store (aggregate_id, event_type, event_data, version, created_at)
            VALUES (?, ?, ?, ?, ?)
            """;
        
        jdbcTemplate.update(sql, 
            aggregateId, 
            event.getClass().getSimpleName(), 
            serializeEvent(event), 
            version, 
            Instant.now());
    }
    
    public List<Object> getEvents(String aggregateId, long fromVersion) {
        String sql = """
            SELECT event_type, event_data FROM event_store 
            WHERE aggregate_id = ? AND version > ? 
            ORDER BY version ASC
            """;
        
        return jdbcTemplate.query(sql, new Object[]{aggregateId, fromVersion}, 
            (rs, rowNum) -> deserializeEvent(
                rs.getString("event_type"), 
                rs.getString("event_data")
            ));
    }
    
    private String serializeEvent(Object event) {
        // 实现事件序列化逻辑
        return "";
    }
    
    private Object deserializeEvent(String eventType, String eventData) {
        // 实现事件反序列化逻辑
        return null;
    }
}
```

## 最佳实践

### 协议选择
1. **REST API**: 简单易用，适合CRUD操作
2. **gRPC**: 高性能，适合内部服务通信
3. **消息队列**: 异步处理，适合事件驱动
4. **WebSocket**: 实时通信，适合推送场景

### 性能优化
1. **连接复用**: 使用连接池减少连接开销
2. **数据压缩**: 减少网络传输数据量
3. **批量操作**: 合并多个请求减少网络调用
4. **缓存策略**: 缓存频繁访问的数据

### 可靠性保障
1. **重试机制**: 合理的重试策略和退避算法
2. **熔断降级**: 防止故障传播
3. **超时控制**: 避免长时间等待
4. **幂等性**: 确保重复调用安全

### 监控治理
1. **性能监控**: 监控延迟、吞吐量、错误率
2. **链路追踪**: 跟踪服务调用链路
3. **日志记录**: 详细记录通信日志
4. **告警机制**: 及时发现和处理问题

## 相关技能

- **api-gateway** - API网关设计
- **circuit-breaker** - 熔断器模式
- **distributed-tracing** - 分布式追踪
- **service-discovery** - 服务发现
- **backend** - 后端开发
