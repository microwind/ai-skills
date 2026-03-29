---
name: 装饰器模式
description: "动态给对象添加职责。在需要为对象增加功能但又不想改变类本身时使用。"
license: MIT
---

# 装饰器模式 (Decorator Pattern)

## 概述

装饰器模式动态地给对象添加职责，不改变对象本身和外部接口。它提供了比继承更有弹性的替代方案来扩展功能。通过组合而不是继承，实现功能的灵活扩展。

**核心原则**:
1. **组合优于继承**: 使用组合而非继承来拓展功能
2. **开闭原则**: 对扩展开放，对修改关闭
3. **单一职责**: 每个装饰器只添加一个职责
4. **透明性**: 装饰器与被装饰对象有相同接口

**与继承的根本区别**:
```
继承方式：        装饰器方式：
Vehicle           ┌─ Vehicle (接口)
 ├─ Car              ├─ RealCar
 ├─ CarWithAC        ├─ ACDecorator
 ├─ CarWithSunroof      ├─ SunroofDecorator
 ├─ CarWithACAndSunroof ├─ CustomPaintDecorator
 └─ ...             └─ ...
 爆炸式增长          灵活组合
```

## 6个完美的使用场景

### 1. Java IO流处理（最经典应用）
文件读写需要支持多种功能组合：压缩、加密、缓冲、编码转换等。不能为每个组合创建子类。

```java
// ❌ 不使用装饰器：类爆炸
FileInputStream
BufferedFileInputStream
GzipFileInputStream
GzipBufferedFileInputStream
GzipBufferedEncryptedFileInputStream
// ... 无法维护的组合爆炸

// ✅ 使用装饰器：灵活组合
InputStream in = new FileInputStream("file.txt.gz");
in = new GZIPInputStream(in);
in = new BufferedInputStream(in);
in = new CipherInputStream(in, cipher);
in = new InputStreamReader(in, "UTF-8");
```

### 2. Web框架中的功能中间件
服务方法需要支持多个功能：日志、缓存、鉴权、事务、性能监控、参数验证。每个功能独立，可选组合。

```java
// HTTP请求处理链
UserService service = new UserServiceImpl();
service = new CachingDecorator(service);      // 添加缓存
service = new LoggingDecorator(service);      // 添加日志
service = new AuthenticationDecorator(service); // 添加鉴权
service = new ValidationDecorator(service);   // 添加验证
service = new TransactionDecorator(service);  // 添加事务
```

### 3. GUI组件功能扩展
窗口需要支持多种特效和行为的自由组合：边框、阴影、滚动条、透明度、缩放动画。

```
Window
 ├─ BorderWindow（添加边框）
 ├─ ShadowWindow（添加阴影）
 ├─ ScrollableWindow（添加滚动）
 └─ 可以组合任意组合
```

### 4. 数据处理管道
数据需要经过多个处理步骤的自由组合：验证、转换、加密、压缩、序列化。

```java
DataProcessor processor = new RawDataProcessor();
processor = new ValidationDecorator(processor);
processor = new TransformationDecorator(processor);
processor = new EncryptionDecorator(processor);
processor = new CompressionDecorator(processor);
```

### 5. 咖啡订单系统（教科书例子）
基础咖啡可选添加配料：牛奶、糖、巧克力、肉桂等。价格和描述动态变化。

```java
Coffee coffee = new SimpleCoffee();  // $2.0
coffee = new MilkDecorator(coffee);   // +$0.5 → $2.5
coffee = new SugarDecorator(coffee);  // +$0.3 → $2.8
coffee = new ChocolateDecorator(coffee); // +$0.7 → $3.5
```

### 6. 数据库连接池和连接包装
物理连接需要添加透明的功能：连接验证、性能监控、慢查询日志、自动重连。

```java
Connection physicalConn = DriverManager.getConnection(url);
Connection conn = new MonitoringDecorator(physicalConn);
conn = new PooledConnectionDecorator(conn);
conn = new LoggingDecorator(conn);
conn = new TimeoutDecorator(conn);
```

## 4个实现方法对比

| 方法 | 适用场景 | 优点 | 缺点 | 选择指数 |
|------|--------|------|------|---------|
| **继承式装饰器** | 规范工程 | 类型安全 | 代码多 | ⭐⭐⭐⭐ |
| **泛型装饰器** | 通用场景 | 通用性强 | 类型检查复杂 | ⭐⭐⭐⭐⭐ |
| **函数式装饰器** | 简单场景 | 代码简洁 | 难以复用 | ⭐⭐⭐ |
| **动态代理** | AOP场景 | 完全透明 | 性能开销 | ⭐⭐⭐ |

### 方法1: 继承式装饰器（标准实现）
```java
// 基础接口
public interface DataStream {
    String read();
    void write(String data);
}

// 具体实现
public class FileDataStream implements DataStream {
    @Override
    public String read() {
        return "File data";
    }
    
    @Override
    public void write(String data) {
        System.out.println("Writing to file: " + data);
    }
}

// 抽象装饰器
public abstract class DataStreamDecorator implements DataStream {
    protected DataStream wrappedStream;
    
    protected DataStreamDecorator(DataStream stream) {
        this.wrappedStream = stream;
    }
}

// 具体装饰器1：压缩
public class CompressionDecorator extends DataStreamDecorator {
    public CompressionDecorator(DataStream stream) {
        super(stream);
    }
    
    @Override
    public String read() {
        String data = wrappedStream.read();
        return decompress(data);  // 解压
    }
    
    @Override
    public void write(String data) {
        String compressed = compress(data);
        wrappedStream.write(compressed);
    }
    
    private String compress(String data) { return "compressed(" + data + ")"; }
    private String decompress(String data) { return "decompressed(" + data + ")"; }
}

// 具体装饰器2：加密
public class EncryptionDecorator extends DataStreamDecorator {
    public EncryptionDecorator(DataStream stream) {
        super(stream);
    }
    
    @Override
    public String read() {
        String data = wrappedStream.read();
        return decrypt(data);
    }
    
    @Override
    public void write(String data) {
        String encrypted = encrypt(data);
        wrappedStream.write(encrypted);
    }
    
    private String encrypt(String data) { return "encrypted(" + data + ")"; }
    private String decrypt(String data) { return "decrypted(" + data + ")"; }
}

// 具体装饰器3：缓冲
public class BufferingDecorator extends DataStreamDecorator {
    private List<String> buffer = new ArrayList<>();
    private static final int BUFFER_SIZE = 1024;
    
    public BufferingDecorator(DataStream stream) {
        super(stream);
    }
    
    @Override
    public String read() {
        // 缓冲读取逻辑
        return wrappedStream.read();
    }
    
    @Override
    public void write(String data) {
        buffer.add(data);
        if (buffer.size() >= BUFFER_SIZE) {
            flush();
        }
    }
    
    public void flush() {
        buffer.forEach(wrappedStream::write);
        buffer.clear();
    }
}

// 使用示例
DataStream stream = new FileDataStream();
stream = new CompressionDecorator(stream);
stream = new EncryptionDecorator(stream);
stream = new BufferingDecorator(stream);

stream.write("Hello World");  // 自动压缩→加密→缓冲
String data = stream.read();  // 自动解缓冲→解密→解压
```

### 方法2: 泛型装饰器（通用性最强）
```java
// 泛型装饰器，支持任何类型
public abstract class GenericDecorator<T> {
    protected T wrapped;
    
    protected GenericDecorator(T wrapped) {
        this.wrapped = wrapped;
    }
    
    // 子类可以灵活拦截任何方法
}

// 日志装饰器
public class LoggingDecorator<T> implements InvocationHandler {
    private T target;
    
    public LoggingDecorator(T target) {
        this.target = target;
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        long startTime = System.currentTimeMillis();
        System.out.println("[LOG] Calling: " + method.getName());
        
        try {
            Object result = method.invoke(target, args);
            System.out.println("[LOG] Success: " + method.getName());
            return result;
        } catch (Exception e) {
            System.out.println("[LOG] Failed: " + method.getName());
            throw e;
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("[LOG] Duration: " + duration + "ms");
        }
    }
    
    @SuppressWarnings("unchecked")
    public <I> I decorate(Class<I> interfaceClass) {
        return (I) Proxy.newProxyInstance(
            interfaceClass.getClassLoader(),
            new Class[]{interfaceClass},
            this
        );
    }
}

// 使用示例（可装饰任何接口）
UserService originalService = new UserServiceImpl();
LoggingDecorator<UserService> decorator = new LoggingDecorator<>(originalService);
UserService loggingService = decorator.decorate(UserService.class);
loggingService.getUser(123);  // 自动记录日志
```

### 方法3: 函数式装饰器（Java 8+）
```java
// 使用函数式接口
@FunctionalInterface
public interface Processor<T> {
    T process(T input);
}

// 装饰器工厂
public class FunctionalDecorators {
    // 日志装饰器
    public static <T> Processor<T> withLogging(Processor<T> processor) {
        return input -> {
            System.out.println("Processing: " + input);
            T result = processor.process(input);
            System.out.println("Result: " + result);
            return result;
        };
    }
    
    // 缓存装饰器
    public static <T> Processor<T> withCaching(Processor<T> processor) {
        Map<T, T> cache = new ConcurrentHashMap<>();
        return input -> cache.computeIfAbsent(input, k -> processor.process(k));
    }
    
    // 性能监控装饰器
    public static <T> Processor<T> withProfiling(Processor<T> processor) {
        return input -> {
            long start = System.currentTimeMillis();
            T result = processor.process(input);
            long duration = System.currentTimeMillis() - start;
            System.out.println("Execution time: " + duration + "ms");
            return result;
        };
    }
}

// 使用示例
Processor<Integer> processor = x -> x * 2;
processor = FunctionalDecorators.withLogging(processor);
processor = FunctionalDecorators.withCaching(processor);
processor = FunctionalDecorators.withProfiling(processor);

Integer result = processor.process(5);  // 链式调用所有装饰器
```

### 方法4: 动态代理装饰（AOP风格）
```java
// 需要JDK动态代理或CGLIB
public class DecoratorProxy {
    public static <T> T decorate(T target, Class<T> interfaceClass, 
                                  List<Interceptor> interceptors) {
        return (T) Proxy.newProxyInstance(
            interfaceClass.getClassLoader(),
            new Class[]{interfaceClass},
            (proxy, method, args) -> {
                InterceptionChain chain = new InterceptionChain(method, target, interceptors);
                return chain.proceed(args);
            }
        );
    }
}

public interface Interceptor {
    Object intercept(Method method, Object[] args, InterceptionChain chain) throws Throwable;
}

// 使用示例
UserService service = new UserServiceImpl();
List<Interceptor> interceptors = Arrays.asList(
    new LoggingInterceptor(),
    new CachingInterceptor(),
    new PerformanceMonitorInterceptor()
);
UserService decoratedService = DecoratorProxy.decorate(service, UserService.class, interceptors);
```

## 4个常见问题 + 完整解决方案

### 问题1: 装饰器顺序问题 (Order Matters)
**症状**: 不同顺序的装饰导致结果完全不同，且很难发现

```java
// ❌ 问题代码：顺序导致结果不一致
InputStream in1 = new FileInputStream("file.txt.gz");
in1 = new GZIPInputStream(in1);  // 先解压
in1 = new BufferedInputStream(in1);  // 再缓冲

// vs

InputStream in2 = new FileInputStream("file.txt.gz");
in2 = new BufferedInputStream(in2);  // 先缓冲
in2 = new GZIPInputStream(in2);  // 再解压
// in1和in2处理的数据不同！

// ✅ 解决方案1：记录装饰顺序
public class DecoratorChain<T> {
    private T target;
    private List<String> decorators = new ArrayList<>();
    
    public DecoratorChain(T target) {
        this.target = target;
    }
    
    public <D extends T> DecoratorChain<T> addDecorator(Class<D> decoratorClass) {
        decorators.add(decoratorClass.getSimpleName());
        return this;
    }
    
    public void printChain() {
        System.out.println("Decoration order: " + decorators);
    }
}

// ✅ 解决方案2：提供预定义的装饰器组合
public class DataStreamBuilder {
    private InputStream in;
    
    public DataStreamBuilder(InputStream in) {
        this.in = in;
    }
    
    public DataStreamBuilder withCompression() {
        try {
            in = new GZIPInputStream(in);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        return this;
    }
    
    public DataStreamBuilder withBuffering() {
        in = new BufferedInputStream(in);
        return this;
    }
    
    public DataStreamBuilder withEncryption(Cipher cipher) {
        in = new CipherInputStream(in, cipher);
        return this;
    }
    
    // 正确的顺序：数据流→解压缩→解密→缓冲（解码）
    public InputStream buildForDecryption() {
        return withCompression()
            .withEncryption(null)  // 伪代码
            .withBuffering()
            .get();
    }
    
    public InputStream get() {
        return in;
    }
}
```

### 问题2: 装饰器与被装饰对象接口签名不匹配
**症状**: 装饰器添加了新方法，破坏了与原接口的一致性

```java
// ❌ 问题代码：装饰器有额外方法
public class CachedUserService extends UserService {  // 继承而非实现接口
    @Override
    public User getUser(int id) {
        // 缓存逻辑
    }
    
    // 额外方法，破坏接口一致性
    public void clearCache() { }
    public Cache getCache() { }
}

// ✅ 解决方案：使用适配器模式或严格遵循接口
public interface UserService {
    User getUser(int id);
    // ... 其他方法
}

public class CachedUserServiceDecorator implements UserService {
    private UserService wrapped;
    private Cache cache;
    
    public CachedUserServiceDecorator(UserService wrapped, Cache cache) {
        this.wrapped = wrapped;
        this.cache = cache;
    }
    
    @Override
    public User getUser(int id) {
        User cached = cache.get(id);
        if (cached != null) return cached;
        
        User user = wrapped.getUser(id);
        cache.put(id, user);
        return user;
    }
    
    // 如需额外功能，提供独立方法
    public void clearCache() {
        if (cache instanceof Clearable) {
            ((Clearable) cache).clear();
        }
    }
}
```

### 问题3: 多层装饰导致性能问题和调试困难
**症状**: 8层装饰导致进程变得极其缓慢，且栈跟踪极深

```java
// ❌ 问题代码：过度装饰
service = new LoggingDecorator(service);
service = new CachingDecorator(service);
service = new ValidationDecorator(service);
service = new TransactionDecorator(service);
service = new PerformanceMonitorDecorator(service);
service = new SecurityDecorator(service);
service = new AuditingDecorator(service);
service = new CircuitBreakerDecorator(service);  // 8层深度

// ✅ 解决方案1：限制装饰深度
public class DecoratorDepthValidator {
    private static final int MAX_DEPTH = 3;
    
    public static <T> void validate(T decorated) {
        int depth = calculateDepth(decorated);
        if (depth > MAX_DEPTH) {
            throw new IllegalArgumentException(
                "Decorator depth " + depth + " exceeds maximum " + MAX_DEPTH
            );
        }
    }
    
    private static <T> int calculateDepth(T obj) {
        int depth = 0;
        Object current = obj;
        while (current instanceof Decorator) {
            depth++;
            current = ((Decorator) current).getWrapped();
        }
        return depth;
    }
}

// ✅ 解决方案2：组合装饰器合并功能
public class ComprehensiveServiceDecorator implements UserService {
    private UserService wrapped;
    private Cache cache;
    private PerformanceMonitor monitor;
    private AuditLog auditLog;
    
    public ComprehensiveServiceDecorator(UserService wrapped) {
        this.wrapped = wrapped;
        this.cache = new Cache();
        this.monitor = new PerformanceMonitor();
        this.auditLog = new AuditLog();
    }
    
    @Override
    public User getUser(int id) {
        long startTime = System.currentTimeMillis();
        
        try {
            // 缓存检查
            User cached = cache.get(id);
            if (cached != null) {
                auditLog.log("Cache hit for user " + id);
                return cached;
            }
            
            // 执行
            User user = wrapped.getUser(id);
            cache.put(id, user);
            
            // 审计
            auditLog.log("Fetched user " + id);
            return user;
            
        } finally {
            // 性能监控
            long duration = System.currentTimeMillis() - startTime;
            monitor.record("getUser", duration);
        }
    }
}
```

### 问题4: 装饰器链中异常处理不当
**症状**: 某个装饰器抛异常，导致整个链失败或失败模式不明确

```java
// ❌ 问题代码：异常处理不当
public String process(String data) {
    data = compressionDecorator.process(data);  // 可能失败
    data = encryptionDecorator.process(data);    // 可能失败
    data = validationDecorator.process(data);    // 可能失败
    return data;  // 如果中间失败，状态不清
}

// ✅ 解决方案：完善的异常处理和恢复
public class ResilientDecoratorChain {
    private List<SafeDecorator> decorators = new ArrayList<>();
    private ErrorHandler errorHandler;
    
    public ResilientDecoratorChain(ErrorHandler errorHandler) {
        this.errorHandler = errorHandler;
    }
    
    public Result process(Input input) {
        Result current = new Result(input);
        
        for (int i = 0; i < decorators.size(); i++) {
            try {
                current = decorators.get(i).decorate(current);
            } catch (Exception e) {
                // 记录失败点
                errorHandler.handle(input, i, decorators.get(i), e);
                
                // 决定是否继续
                if (errorHandler.shouldContinue(e)) {
                    // 跳过此装饰器，继续下一个
                    continue;
                } else if (errorHandler.shouldRetry(e)) {
                    // 重试此装饰器
                    i--;
                    continue;
                } else {
                    // 中止处理，返回失败状态
                    return Result.failure(e);
                }
            }
        }
        
        return current;
    }
}
```

## 最佳实践指南

### 1️⃣ 装饰器职责要专一
```java
// ❌ 一个装饰器做太多事
public class MegaDecorator extends DataStream {
    @Override
    public String read() {
        // 压缩、加密、日志、缓存、性能监控全部在这里
    }
}

// ✅ 各司其职
public class CompressionDecorator extends DataStream {
    @Override
    public String read() {
        return decompress(wrapped.read());
    }
}

public class LoggingDecorator extends DataStream {
    @Override
    public String read() {
        System.out.println("Reading...");
        return wrapped.read();
    }
}
```

### 2️⃣ 使用Builder模式简化装饰链构建
```java
// ✅ Builder模式
public class DataStreamBuilder {
    private InputStream stream;
    
    public DataStreamBuilder(InputStream stream) {
        this.stream = stream;
    }
    
    public DataStreamBuilder compress() {
        stream = new CompressionDecorator(stream);
        return this;
    }
    
    public DataStreamBuilder encrypt(Cipher cipher) {
        stream = new EncryptionDecorator(stream, cipher);
        return this;
    }
    
    public DataStreamBuilder buffer() {
        stream = new BufferingDecorator(stream);
        return this;
    }
    
    public InputStream build() {
        return stream;
    }
}

// 使用
InputStream in = new DataStreamBuilder(
    new FileInputStream("data.bin")
)
    .compress()
    .encrypt(cipher)
    .buffer()
    .build();
```

### 3️⃣ 提供清晰的装饰器文档
```java
/**
 * 缓存装饰器
 * 
 * 作用: 缓存方法调用结果
 * 
 * 使用场景:
 * - 方法调用结果稳定且获取开销大
 * - 可以接受短时间的数据延迟
 * 
 * 顺序建议:
 * - 应该在日志装饰器之后（避免记录缓存命中）
 * - 应该在数据转换装饰器之前（缓存转换后的结果）
 * 
 * 性能影响:
 * - 首次调用: +20% 开销（缓存存储）
 * - 缓存命中: -80% 开销（直接返回）
 * - 内存: +N * (key_size + value_size)
 * 
 * @param <T> 被装饰对象类型
 */
public class CachingDecorator<T> extends Decorator<T> {
    // 实现...
}
```

### 4️⃣ 支持装饰器的反思和诊断
```java
public interface Decorator<T> {
    T getWrapped();
    String getDecoratorName();
    int getDecoratorDepth();
}

public class DecoratorDiagnostics {
    public static <T> void printChain(T decorated) {
        System.out.println("Decorator Chain:");
        Object current = decorated;
        int level = 0;
        
        while (current instanceof Decorator) {
            Decorator<?> decorator = (Decorator<?>) current;
            System.out.println(
                "  " + level + ". " + decorator.getDecoratorName()
            );
            current = decorator.getWrapped();
            level++;
        }
        
        System.out.println("  " + level + ". " + current.getClass().getSimpleName() + " (core)");
    }
}
```

### 5️⃣ 支持装饰器的动态移除和替换
```java
public class RemovableDecorator<T> implements Decorator<T> {
    private T wrapped;
    private String name;
    
    public RemovableDecorator(T wrapped, String name) {
        this.wrapped = wrapped;
        this.name = name;
    }
    
    @Override
    public T getWrapped() {
        return wrapped;  // 支持剥离此装饰器
    }
    
    public T unwrap() {
        return wrapped;  // 移除自己，返回被包装的对象
    }
}

// 使用示例
UserService service = originalService;
service = new LoggingDecorator(service);
service = new CachingDecorator(service);
service = new ValidationDecorator(service);

// 如需移除缓存装饰
if (service instanceof RemovableDecorator) {
    RemovableDecorator<?> removable = (RemovableDecorator<?>) service;
    service = (UserService) removable.unwrap();  // 恢复到去掉缓存前的状态
}
```

## 与其他模式的关系

| 相关模式 | 关系 | 何时选择 |
|--------|------|--------|
| **Strategy** | 都改变对象行为，但Strategy是替换算法，Decorator是添加功能 | 需要替换→Strategy；需要扩展→Decorator |
| **Proxy** | 都包装对象，但Proxy通常是一对一，Decorator支持多层 | 需要访问控制→Proxy；需要功能组合→Decorator |
| **Adapter** | 都改变接口，但Adapter改变不兼容接口，Decorator保持不变 | 接口不匹配→Adapter；功能扩展→Decorator |
| **Builder** | 都实现灵活的对象构建，Decorator运行时动态，Builder是构造时静态 | 构造时灵活→Builder；运行时灵活→Decorator |
| **Composite** | 都支持递归组合，但Composite处理树结构，Decorator是线性链 | 树形结构→Composite；链式功能→Decorator |

## 多语言实现考量

### Java特性应用
- 使用`extends + implements`支持多接口装饰
- 利用`@Delegate`注解（Lombok）自动转发方法
- Java IO是装饰器模式的标准库示范

### Python考量
- Python的鸭子类型使装饰器更灵活
- 支持`@property`和属性转发
- 函数装饰器(`@decorator`)比类装饰器更常见

### TypeScript/JavaScript考量
- 支持高阶函数，函数装饰器自然
- 装饰器提案(`@decorator`)语言原生支持
- 动态属性访问(Proxy对象)更强大

## 何时避免使用

- ❌ **只需要简单继承**: 类层级不复杂，功能组合不多
- ❌ **性能极其关键**: 多层装饰的调用链开销不可接受
- ❌ **接口频繁变化**: 装饰器维护成本超过继承
- ❌ **装饰顺序复杂**: 顺序依赖导致难以维护
- ❌ **单个装饰器过于复杂**: 应该考虑策略模式或责任链
