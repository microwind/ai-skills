---
name: Proxy Pattern
description: "为其他对象提供代理以控制其访问和行为。支持延迟加载、权限控制、远程访问和监控。"
license: MIT
---

# Proxy 模式 (代理模式)

## 核心原理

**Proxy 模式**通过为真实对象创建代理，在客户端与真实对象之间建立一层控制层。代理与真实对象实现相同接口，但在转发请求前可以执行额外的逻辑。

**关键思想**:
```
客户端 → 代理对象 → (验证/检查/监控) → 真实对象
           ↓
        缓存/日志/计数
```

**四大应用场景**:
1. 🐢 **虚代理** (Lazy Proxy) - 延迟加载
2. 🔐 **保护代理** (Protection Proxy) - 访问控制
3. 🌐 **远程代理** (Remote Proxy) - 分布式访问
4. 📊 **日志代理** (Logging Proxy) - 监控审计

---

## 5个实现方法对比

### 方法1: 基础代理（静态代理）
**特点**: 为每个服务类编写一个代理类  
**优点**: 代码清晰，易于理解  
**缺点**: 代码量大，维护很乱（每个类都需要一个代理）

```java
// 产品接口
public interface Document {
    void read();
    void write(String content);
}

// 真实对象
public class RealDocument implements Document {
    private String filename;
    
    public RealDocument(String filename) {
        this.filename = filename;
        System.out.println("[Real] Document created: " + filename);
    }
    
    @Override public void read() {
        System.out.println("[Real] Reading: " + filename);
    }
    
    @Override public void write(String content) {
        System.out.println("[Real] Writing to: " + filename + " -> " + content);
    }
}

// 代理（静态 - 需要为每个接口编写一个）
public class DocumentProxy implements Document {
    private RealDocument realDocument;
    private String filename;
    private User currentUser;
    
    public DocumentProxy(String filename, User user) {
        this.filename = filename;
        this.currentUser = user;
    }
    
    @Override
    public void read() {
        // 代理逻辑：验证权限
        if (!currentUser.hasPermission("READ")) {
            throw new AccessDeniedException("No read permission");
        }
        
        // 代理逻辑：延迟加载
        if (realDocument == null) {
            this.realDocument = new RealDocument(filename);
        }
        
        realDocument.read();
    }
    
    @Override
    public void write(String content) {
        if (!currentUser.hasPermission("WRITE")) {
            throw new AccessDeniedException("No write permission");
        }
        
        if (realDocument == null) {
            this.realDocument = new RealDocument(filename);
        }
        
        realDocument.write(content);
    }
}
```

### 方法2: Java 动态代理 (Reflection-based)
**特点**: 运行时生成代理类，一个通用代理处理所有接口  
**优点**: 无需为每个类写代理  
**缺点**: 反射性能开销，调试困难

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;

// 通用代理处理器（处理所有被代理对象）
public class PermissionCheckingHandler implements InvocationHandler {
    private Object target;
    private User currentUser;
    private Map<String, Set<String>> permissions = new HashMap<>();
    
    public PermissionCheckingHandler(Object target, User user) {
        this.target = target;
        this.currentUser = user;
        initPermissions();
    }
    
    private void initPermissions() {
        permissions.put("read", Set.of("admin", "user", "guest"));
        permissions.put("write", Set.of("admin", "user"));
        permissions.put("delete", Set.of("admin"));
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        String methodName = method.getName();
        
        // 权限检查逻辑
        checkPermission(methodName);
        
        // 记录调用日志
        System.out.println("[Proxy] Calling: " + methodName + " for user: " + currentUser.getName());
        
        // 执行真实方法
        long startTime = System.currentTimeMillis();
        Object result = method.invoke(target, args);
        long duration = System.currentTimeMillis() - startTime;
        
        // 性能监控
        System.out.println("[Proxy] Method " + methodName + " took " + duration + "ms");
        
        return result;
    }
    
    private void checkPermission(String methodName) {
        Set<String> allowedRoles = permissions.get(methodName);
        if (allowedRoles == null || !allowedRoles.contains(currentUser.getRole())) {
            throw new AccessDeniedException("User " + currentUser.getName() + 
                " has no permission to call " + methodName);
        }
    }
}

// 使用 JDK 动态代理
Document realDoc = new RealDocument("report.docx");
User user = new User("Alice", "admin");

Document proxyDoc = (Document) Proxy.newProxyInstance(
    Document.class.getClassLoader(),
    new Class[]{Document.class},
    new PermissionCheckingHandler(realDoc, user)
);

proxyDoc.read();  // 自动检查权限、记录日志、计时
```

### 方法3: CGLib 代理（字节码生成）- 无需接口
**特点**: 通过继承生成代理，支持没有接口的类  
**优点**: 性能好（不用反射），无需实现接口  
**缺点**: 无法代理 final 类，GC 开销

```java
import net.sf.cglib.proxy.Enhancer;
import net.sf.cglib.proxy.MethodInterceptor;
import net.sf.cglib.proxy.MethodProxy;

public class PerformanceMonitorInterceptor implements MethodInterceptor {
    private Map<String, Long> callDurations = new ConcurrentHashMap<>();
    private Map<String, Integer> callCounts = new ConcurrentHashMap<>();
    
    @Override
    public Object intercept(Object obj, Method method, Object[] args, MethodProxy proxy) 
            throws Throwable {
        String key = method.getName();
        
        long startTime = System.nanoTime();
        Object result = proxy.invokeSuper(obj, args);
        long duration = System.nanoTime() - startTime;
        
        callCounts.merge(key, 1, Integer::sum);
        callDurations.merge(key, duration, Long::sum);
        
        System.out.printf("[CGLib Proxy] %s called (total: %d times, avg: %.2fms)%n",
            key, callCounts.get(key), callDurations.get(key) / 1_000_000.0 / callCounts.get(key));
        
        return result;
    }
    
    public Map<String, Double> getAverageCallTimes() {
        return callDurations.entrySet().stream()
            .collect(Collectors.toMap(
                Map.Entry::getKey,
                e -> e.getValue() / 1_000_000.0 / callCounts.get(e.getKey())
            ));
    }
}

// 使用 CGLib
public class RealFileService {  // 注意：没有接口
    public String readFile(String path) {
        System.out.println("[Real] Reading file: " + path);
        return "file content";
    }
    
    public void writeFile(String path, String content) {
        System.out.println("[Real] Writing to " + path);
    }
}

Enhancer enhancer = new Enhancer();
enhancer.setSuperclass(RealFileService.class);
enhancer.setCallback(new PerformanceMonitorInterceptor());

RealFileService proxy = (RealFileService) enhancer.create();
proxy.readFile("/tmp/test.txt");
proxy.writeFile("/tmp/test.txt", "new content");
```

### 方法4: Spring AOP 代理（最实用）
**特点**: 声明式代理，无需手工编写代理代码  
**优点**: 与 Spring 集成，支持注解，代码简洁  
**缺点**: 依赖 Spring 框架

```java
// 目标服务
@Service
public class UserService {
    public User getUser(String id) {
        System.out.println("[Service] Getting user: " + id);
        Thread.sleep(100);  // 模拟耗时操作
        return new User(id, "John");
    }
    
    public void deleteUser(String id) {
        System.out.println("[Service] Deleting user: " + id);
    }
}

// 自定义切面
@Aspect
@Component
public class PermissionAndPerformanceAspect {
    private static final Logger logger = LoggerFactory.getLogger(PermissionAndPerformanceAspect.class);
    
    @Before("execution(* com.example.UserService.*(..))")
    public void checkPermission(JoinPoint joinPoint) {
        User currentUser = SecurityContextHolder.getContext().getAuthentication();
        if (!currentUser.hasPermission(joinPoint.getSignature().getName())) {
            throw new AccessDeniedException("Permission denied");
        }
    }
    
    @Around("execution(* com.example.UserService.*(..))")
    public Object measurePerformance(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        Object result = joinPoint.proceed();  // 执行实际方法
        
        long duration = System.currentTimeMillis() - startTime;
        logger.info("Method {} took {}ms", joinPoint.getSignature().getName(), duration);
        
        if (duration > 500) {
            logger.warn("Slow method detected: {} took {}ms", 
                joinPoint.getSignature().getName(), duration);
        }
        
        return result;
    }
    
    @AfterThrowing(pointcut = "execution(* com.example.UserService.*(..))", throwing = "ex")
    public void logException(JoinPoint joinPoint, Exception ex) {
        logger.error("Method {} threw exception: {}", 
            joinPoint.getSignature().getName(), ex.getMessage());
    }
}

// 使用（自动被 Spring 代理）
@Autowired
private UserService userService;

public void example() {
    User user = userService.getUser("123");  // 自动执行 AOP 切面
}
```

### 方法5: 纯函数式代理（FP 风格）
**特点**: 使用函数式编程，代理是函数的组合  
**优点**: 高度灵活，易于组合和测试  
**缺点**: 学习曲线陡

```java
import java.util.function.Function;

// 定义服务接口为纯函数
public interface Service {
    String execute(String input);
}

// 创建代理是中间件的组合
public class FunctionalProxyBuilder {
    private List<Function<Service, Service>> middlewares = new ArrayList<>();
    
    public FunctionalProxyBuilder addPermissionCheck(User user) {
        middlewares.add(service -> input -> {
            if (!user.hasPermission("execute")) {
                throw new AccessDeniedException();
            }
            return service.execute(input);
        });
        return this;
    }
    
    public FunctionalProxyBuilder addLogging() {
        middlewares.add(service -> input -> {
            System.out.println("[Proxy] Executing with input: " + input);
            String result = service.execute(input);
            System.out.println("[Proxy] Result: " + result);
            return result;
        });
        return this;
    }
    
    public FunctionalProxyBuilder addCaching() {
        Map<String, String> cache = new ConcurrentHashMap<>();
        middlewares.add(service -> input -> {
            if (cache.containsKey(input)) {
                System.out.println("[Proxy] Cache hit for: " + input);
                return cache.get(input);
            }
            String result = service.execute(input);
            cache.put(input, result);
            return result;
        });
        return this;
    }
    
    public FunctionalProxyBuilder addRateLimiting(int maxCallsPerMinute) {
        AtomicInteger counter = new AtomicInteger(0);
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        
        scheduler.scheduleAtFixedRate(() -> counter.set(0), 1, 1, TimeUnit.MINUTES);
        
        middlewares.add(service -> input -> {
            if (counter.incrementAndGet() > maxCallsPerMinute) {
                throw new RateLimitExceededException();
            }
            return service.execute(input);
        });
        return this;
    }
    
    public Service build(Service realService) {
        Service proxy = realService;
        for (Function<Service, Service> middleware : middlewares) {
            proxy = middleware.apply(proxy);
        }
        return proxy;
    }
}

// 使用示例
Service realService = input -> "Processed: " + input;

Service proxyService = new FunctionalProxyBuilder()
    .addPermissionCheck(currentUser)
    .addLogging()
    .addCaching()
    .addRateLimiting(100)
    .build(realService);

String result = proxyService.execute("query");  // 会依次执行所有中间件
```

---

## 代理 vs 装饰 vs 外观 - 全面对比

| 维度 | 代理 | 装饰 | 外观 |
|------|------|------|------|
| **目的** | 控制访问 | 添加功能 | 简化接口 |
| **职责数** | 通常1-2个 | 可多个 | 多个 |
| **创建时机** | 代替原对象 | 自由叠加 | 统一管理 |
| **大小关系** | 相同接口 | 可扩展接口 | 可更简单 |
| **何时使用** | 权限/性能 | 功能加强 | 接口封装 |
| **示例** | 文件访问代理 | Logger 装饰器 | Facade 简化 |

---

## 4个常见问题 + 完整解决方案

### 问题1: 代理与装饰器的实际区别
**症状**: 容易混淆代理和装饰器，不知道何时用哪个

```java
// ❌ 错误混淆
class LoggingProxy implements DataService {  // 这其实是装饰器
    private DataService target;
    
    @Override
    public Data fetch() {
        log("Fetching data");
        return target.fetch();  // 同时做了权限+日志，职责混乱
    }
}

// ✅ 清晰的代理 - 专注于控制访问
class PermissionCheckingProxy implements DataService {
    private DataService target;
    private User user;
    
    @Override
    public Data fetch() {
        if (!user.hasPermission("READ")) {
            throw new AccessDeniedException();
        }
        return target.fetch();  // 只负责权限检查
    }
}

// ✅ 清晰的装饰器 - 专注于功能增强
class LoggingDecorator implements DataService {
    private DataService wrapped;
    
    @Override
    public Data fetch() {
        System.out.println("Before fetch");
        Data result = wrapped.fetch();
        System.out.println("After fetch");
        return result;  // 只负责添加日志
    }
}

// 使用组合：代理控制访问，装饰器添加日志
DataService service = new DataService();
DataService withPermission = new PermissionCheckingProxy(service, user);
DataService withLog = new LoggingDecorator(withPermission);
```

### 问题2: 动态代理性能问题
**症状**: 使用 JDK 动态代理导致性能下降 50%+

```java
// ❌ 反面：反射导致性能问题
public class SlowReflectionProxy implements InvocationHandler {
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        return method.invoke(target, args);  // 每次调用都通过反射
    }
}

// ✅ 解决方案1：使用字节码生成 (CGLib)
public class FastCGLibProxy {
    public static <T> T createProxy(T target, MethodInterceptor interceptor) {
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(target.getClass());
        enhancer.setCallback(interceptor);
        return (T) enhancer.create();
    }
}

// ✅ 解决方案2：静态代理（最快，但需手写）
public class FastStaticProxy implements UserService {
    private UserService target;
    
    @Override
    public void deleteUser(String id) {
        // 直接调用，无反射
        checkPermission();
        target.deleteUser(id);
    }
    
    private void checkPermission() { /* ... */ }
}

// ✅ 解决方案3：缓存反射结果
public class CachedReflectionProxy implements InvocationHandler {
    private Map<Method, Object> resultCache = new ConcurrentHashMap<>();
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        String key = method.getName() + Arrays.toString(args);
        return resultCache.computeIfAbsent(key, k -> {
            try {
                return method.invoke(target, args);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        });
    }
}

// 性能测试对比
long start = System.nanoTime();
for (int i = 0; i < 1_000_000; i++) {
    proxy.execute();
}
long duration = (System.nanoTime() - start) / 1_000_000;
// JDK 动态代理: ~500ms
// CGLib: ~200ms
// 静态代理: ~50ms
```

### 问题3: 代理链（多个代理叠加）问题
**症状**: 多个代理叠加导致代码混乱、调试困难

```java
// ❌ 反面：代理链过长，难以管理
UserService service = new RealUserService();
service = new PermissionCheckingProxy(service, user);
service = new LoggingProxy(service);
service = new CachingProxy(service);
service = new RateLimitingProxy(service, 100);
service = new TimeoutProxy(service, 5000);
// 调试时不知道哪一层出错了

// ✅ 解决方案：使用代理构建器
public class ProxyChainBuilder {
    private UserService target;
    
    public ProxyChainBuilder withPermissionChecking(User user) {
        target = new PermissionCheckingProxy(target, user);
        return this;
    }
    
    public ProxyChainBuilder withLogging() {
        target = new LoggingProxy(target);
        return this;
    }
    
    public ProxyChainBuilder withCaching() {
        target = new CachingProxy(target);
        return this;
    }
    
    public ProxyChainBuilder withRateLimiting(int limit) {
        target = new RateLimitingProxy(target, limit);
        return this;
    }
    
    public UserService build() {
        return target;
    }
}

// 使用更清晰
UserService service = new ProxyChainBuilder()
    .withPermissionChecking(user)
    .withCaching()
    .withRateLimiting(100)
    .build();
```

### 问题4: 远程代理 (RPC) 的网络错误处理
**症状**: 网络延迟、超时、连接错误时没有处理

```java
// ❌ 反面：没有考虑网络问题
public class RemoteServiceProxy implements RemoteService {
    private String serverUrl;
    
    @Override
    public Data fetch() {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder(URI.create(serverUrl + "/fetch"))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return parseResponse(response.body());  // 如果网络故障直接崩溃
    }
}

// ✅ 解决方案：添加重试、超时、熔断
public class RobustRemoteServiceProxy implements RemoteService {
    private String serverUrl;
    private final int MAX_RETRIES = 3;
    private final int TIMEOUT_MS = 5000;
    private final CircuitBreaker circuitBreaker;
    
    public RobustRemoteServiceProxy(String serverUrl) {
        this.serverUrl = serverUrl;
        this.circuitBreaker = new CircuitBreaker(3, Duration.ofSeconds(30));
    }
    
    @Override
    public Data fetch() throws ServiceUnavailableException {
        // 熔断检查
        if (circuitBreaker.isOpen()) {
            throw new ServiceUnavailableException("Service temporarily unavailable");
        }
        
        try {
            Data result = fetchWithRetry();
            circuitBreaker.recordSuccess();
            return result;
        } catch (IOException | InterruptedException | TimeoutException e) {
            circuitBreaker.recordFailure();
            throw new ServiceUnavailableException("Remote service failed: " + e.getMessage(), e);
        }
    }
    
    private Data fetchWithRetry() throws IOException, InterruptedException, TimeoutException {
        int attempt = 0;
        Exception lastException = null;
        
        while (attempt < MAX_RETRIES) {
            try {
                return fetchSingleAttempt();
            } catch (IOException | TimeoutException e) {
                lastException = e;
                attempt++;
                
                if (attempt < MAX_RETRIES) {
                    long backoff = 100 * (long) Math.pow(2, attempt - 1);  // 指数退避
                    System.out.println("[Proxy] Retry attempt " + attempt + " after " + backoff + "ms");
                    Thread.sleep(backoff);
                }
            }
        }
        
        throw new TimeoutException("Failed after " + MAX_RETRIES + " retries", lastException);
    }
    
    private Data fetchSingleAttempt() throws IOException, TimeoutException, InterruptedException {
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofMillis(TIMEOUT_MS))
            .build();
        
        HttpRequest request = HttpRequest.newBuilder(URI.create(serverUrl + "/fetch"))
            .timeout(Duration.ofMillis(TIMEOUT_MS))
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() != 200) {
            throw new IOException("Server returned status: " + response.statusCode());
        }
        
        return parseResponse(response.body());
    }
}
```

---

## 最佳实践指南

### 1️⃣ 代理职责单一
```java
// ❌ 混乱
class MixedProxy implements Service {
    public void execute() {
        checkPermission();  // 权限
        logCall();          // 日志
        cache();            // 缓存
        monitor();          // 监控
        target.execute();
    }
}

// ✅ 清晰 - 每个代理一个职责
class PermissionProxy implements Service {
    public void execute() {
        checkPermission();
        target.execute();
    }
}
```

### 2️⃣ 代理不应该修改行为
```java
// ❌ 错误 - 代理不应该改变返回值
class TransformingProxy implements Service {
    public String execute() {
        String result = target.execute();
        return result.toUpperCase();  // 不应该修改
    }
}

// ✅ 正确 - 只处理服务方面
class LoggingProxy implements Service {
    public String execute() {
        System.out.println("Before");
        String result = target.execute();
        System.out.println("After");
        return result;  // 返回原始结果
    }
}
```

### 3️⃣ 异常处理要完善
```java
// ✅ 代理应该处理自己的异常
public class RobustProxy implements Service {
    @Override
    public void execute() {
        try {
            checkPermission();
        } catch (PermissionException e) {
            logger.error("Permission denied", e);
            throw e;  // 或根据策略降级
        }
        
        try {
            target.execute();
        } catch (ServiceException e) {
            logger.error("Service failed", e);
            throw e;
        }
    }
}
```

### 4️⃣ 文档化代理行为
```java
/**
 * 权限检查代理 - 代理 UserService
 * 
 * 代理的行为:
 * - 每次调用前检查用户权限
 * - 如果权限不足抛出 AccessDeniedException
 * - 如果真实对象抛异常，直接转发
 * 
 * 性能影响:
 * - 每次调用增加 <1ms 的权限检查时间
 * 
 * @param user 当前用户
 */
public class PermissionCheckingProxy implements UserService {
    private UserService target;
    private User user;
    
    // ...
}
```

---

## 与其他模式的关系

| 模式 | 关系 | 何时结合 |
|--------|------|---------|
| **Decorator** | 都是包装对象，但目的不同 | 需要同时控制访问并添加功能 |
| **Facade** | 都简化接口，但 Facade 处理系统 | 对多个对象的统一简化 |
| **Adapter** | 都是中介，但 Adapter 改变接口 | 需要改变接口并控制访问 |
| **Strategy** | 都在运行时切换实现 | 代理负责访问，Strategy 负责算法 |
| **Factory** | 工厂创建代理 | 需要统一创建各类代理 |

---

## 何时使用 Proxy

✅ **强烈推荐**:
- ORM 框架的延迟加载
- RPC 分布式调用
- AOP 框架实现
- 权限与审计系统
- 性能监控与分析

⚠️ **权衡使用**:
- 简单的权限检查（可能过度设计）
- 低频率调用的对象

❌ **不推荐**:
- 对象创建成本极低
- 不需要任何中间处理
- 简单的直接调用
