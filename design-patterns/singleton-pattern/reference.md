# 单例模式完整参考实现

## UML 类图

```
┌─────────────────────────────┐
│       Singleton             │
├─────────────────────────────┤
│ - instance: Singleton       │
├─────────────────────────────┤
│ - Singleton()               │
│ + getInstance(): Singleton  │
└─────────────────────────────┘
     △
     │
     └─ 唯一实例
```

---

## 五种实现方式完全参考

### 1️⃣ 枚举单例 (Java) - 推荐 ⭐⭐⭐

**最安全的实现方式**

```java
/**
 * 枚举单例 - 最安全的单例实现
 * 
 * 特点:
 * 1. 天然防止反射攻击
 * 2. 天然支持序列化
 * 3. 线程安全（由 JVM 保证）
 * 4. 代码最简洁
 * 5. 性能最佳
 */
public enum SingletonLogger {
    // 枚举元素（单例实例）
    INSTANCE;
    
    // 初始化代码（可选）
    SingletonLogger() {
        System.out.println("日志系统初始化");
    }
    
    // 对外提供的方法
    public void log(String message) {
        System.out.println("[LOG] " + message);
    }
    
    public void info(String message) {
        System.out.println("[INFO] " + message);
    }
    
    public void error(String message) {
        System.out.println("[ERROR] " + message);
    }
}

// 使用方式
class Application {
    public static void main(String[] args) {
        SingletonLogger.INSTANCE.log("应用启动");
        SingletonLogger.INSTANCE.info("初始化完成");
        // 多次访问得到同一个实例
        SingletonLogger.INSTANCE.error("无错误");
    }
}
```

---

### 2️⃣ Bill Pugh 单例 (Java) - 推荐 ⭐⭐⭐

**最优雅的实现方式（面向对象设计）**

```java
/**
 * Bill Pugh 单例 - 静态内部类
 * 
 * 特点:
 * 1. 延迟初始化（按需创建）
 * 2. 线程安全（由 JVM 保证）
 * 3. 代码优雅，易于理解
 * 4. 性能优异
 * 5. 支持继承（与枚举不同）
 */
public class DatabaseConnection {
    private String url;
    private String user;
    
    // 私有构造函数
    private DatabaseConnection() {
        this.url = "jdbc:mysql://localhost:3306/db";
        this.user = "admin";
        System.out.println("数据库连接初始化");
    }
    
    // 静态内部类（持有实例）
    private static class SingletonHolder {
        // 静态初始化器在类加载时执行一次
        static final DatabaseConnection INSTANCE = new DatabaseConnection();
    }
    
    // 获取唯一实例
    public static DatabaseConnection getInstance() {
        return SingletonHolder.INSTANCE;
    }
    
    public void executeQuery(String sql) {
        System.out.println("执行查询: " + sql);
    }
}

// 测试
class Test {
    public static void main(String[] args) {
        DatabaseConnection db1 = DatabaseConnection.getInstance();
        DatabaseConnection db2 = DatabaseConnection.getInstance();
        System.out.println("db1 == db2: " + (db1 == db2));  // true
    }
}
```

---

### 3️⃣ 双检查锁定 (Java)

**平衡考虑（不太推荐，复杂）**

```java
/**
 * 双检查锁定单例
 * 
 * 特点:
 * 1. 延迟初始化
 * 2. 性能还可以（减少同步开销）
 * 3. 代码复杂（需要 volatile）
 * 4. 容易出错
 * 
 * 注意: 必须使用 volatile 关键字！
 */
public class CacheManager {
    // volatile 确保可见性和有序性
    private static volatile CacheManager instance;
    private static final Object lock = new Object();
    
    private Map<String, Object> cache;
    
    private CacheManager() {
        this.cache = new ConcurrentHashMap<>();
        System.out.println("缓存系统初始化");
    }
    
    public static CacheManager getInstance() {
        // 第一次检查（无锁）
        if (instance == null) {
            // 加锁以创建实例
            synchronized (lock) {
                // 第二次检查（有锁）
                if (instance == null) {
                    instance = new CacheManager();
                }
            }
        }
        return instance;
    }
    
    public void put(String key, Object value) {
        cache.put(key, value);
    }
    
    public Object get(String key) {
        return cache.get(key);
    }
}

// 测试
class Test {
    public static void main(String[] args) {
        CacheManager cm1 = CacheManager.getInstance();
        CacheManager cm2 = CacheManager.getInstance();
        System.out.println("cm1 == cm2: " + (cm1 == cm2));  // true
    }
}
```

---

### 4️⃣ 饿汉式单例 (Java)

**最简单（但启动时创建）**

```java
/**
 * 饿汉式单例
 * 
 * 特点:
 * 1. 代码最简单
 * 2. 线程安全
 * 3. 性能最佳（无同步开销）
 * 4. 启动时创建（可能浪费资源）
 */
public class Configuration {
    // 类加载时直接创建实例
    private static final Configuration instance = new Configuration();
    
    private Properties props;
    
    private Configuration() {
        loadConfig();
    }
    
    private void loadConfig() {
        props = new Properties();
        // 加载配置文件
        System.out.println("配置加载完成");
    }
    
    public static Configuration getInstance() {
        return instance;
    }
    
    public String get(String key) {
        return props.getProperty(key);
    }
}
```

---

### 5️⃣ Python 装饰器实现

```python
"""Python 单例实现 - 装饰器方式"""

def singleton(cls):
    """单例装饰器"""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class Logger:
    """日志系统（单例）"""
    
    def __init__(self):
        self.logs = []
        print("日志系统初始化")
    
    def log(self, message):
        self.logs.append(message)
        print(f"[LOG] {message}")
    
    def get_logs(self):
        return self.logs


# 使用方式
if __name__ == "__main__":
    logger1 = Logger()
    logger2 = Logger()
    
    print(logger1 is logger2)  # True
    
    logger1.log("应用启动")
    logger2.log("初始化完成")  # 同一个对象
```

---

### 6️⃣ TypeScript 类静态属性

```typescript
/**
 * TypeScript 单例实现
 */
class Logger {
    private static instance: Logger;
    private logs: string[] = [];
    
    // 私有构造函数
    private constructor() {
        console.log("日志系统初始化");
    }
    
    // 获取单例实例
    public static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }
    
    public log(message: string): void {
        this.logs.push(message);
        console.log(`[LOG] ${message}`);
    }
    
    public info(message: string): void {
        console.log(`[INFO] ${message}`);
    }
}

// 使用方式
const logger1 = Logger.getInstance();
const logger2 = Logger.getInstance();

console.log(logger1 === logger2);  // true

logger1.log("应用启动");
logger2.info("已就绪");
```

---

## 5 种实现方式对比表

| 特性 | 枚举 | Bill Pugh | 双检查锁 | 饿汉式 | 装饰器(Python) |
|------|------|----------|---------|--------|-----------------|
| **代码复杂度** | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| **线程安全** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **延迟初始化** | ❌ | ✅ | ✅ | ❌ | ✅ |
| **性能** | ✨⭐⭐⭐ | ✨⭐⭐⭐ | ⭐⭐ | ✨⭐⭐⭐ | ⭐⭐ |
| **反射防护** | ❌ 防护 | ❌ | ❌ | ❌ | N/A |
| **序列化支持** | ✅ 自动 | ⚠️ 需处理 | ⚠️ 需处理 | ⚠️ 需处理 | N/A |
| **易于测试** | ❌ 困难 | ❌ 困难 | ❌ 困难 | ❌ 困难 | ⚠️ 中等 |
| **推荐度** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## 特殊处理

### 处理序列化

```java
/**
 * 支持序列化的单例
 * 反序列化后仍然是同一个实例
 */
public class SerializableSingleton implements Serializable {
    private static final long serialVersionUID = 1L;
    private static final SerializableSingleton instance = new SerializableSingleton();
    
    private SerializableSingleton() {}
    
    public static SerializableSingleton getInstance() {
        return instance;
    }
    
    // ✅ 关键: 实现 readResolve 方法
    protected Object readResolve() {
        return getInstance();
    }
}

// 测试
class Test {
    public static void main(String[] args) throws Exception {
        SerializableSingleton obj1 = SerializableSingleton.getInstance();
        
        // 序列化
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
        oos.writeObject(obj1);
        oos.close();
        
        // 反序列化
        ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
        ObjectInputStream ois = new ObjectInputStream(bais);
        SerializableSingleton obj2 = (SerializableSingleton) ois.readObject();
        ois.close();
        
        System.out.println("obj1 == obj2: " + (obj1 == obj2));  // true!
    }
}
```

### 防止反射攻击

```java
/**
 * 防止反射破坏单例
 */
public class RefectionSafeSingleton {
    private static final RefectionSafeSingleton instance = new RefectionSafeSingleton();
    private static boolean instantiated = false;
    
    private RefectionSafeSingleton() {
        synchronized (RefectionSafeSingleton.class) {
            if (instantiated) {
                throw new IllegalStateException("单例已被创建并不能重复创建！");
            }
            instantiated = true;
        }
    }
    
    public static RefectionSafeSingleton getInstance() {
        return instance;
    }
}

// 测试反射是否能破坏
class Test {
    public static void main(String[] args) throws Exception {
        RefectionSafeSingleton obj1 = RefectionSafeSingleton.getInstance();
        
        // 尝试使用反射创建新实例
        Constructor<RefectionSafeSingleton> constructor = 
            RefectionSafeSingleton.class.getDeclaredConstructor();
        constructor.setAccessible(true);
        
        try {
            RefectionSafeSingleton obj2 = constructor.newInstance();
            System.out.println("❌ 反射成功破坏了单例!");  // 不会执行
        } catch (InvocationTargetException e) {
            System.out.println("✅ 反射被阻止了: " + e.getCause().getMessage());
        }
    }
}
```

---

## 常见问题的完整解决方案

### 问题 1: ClassLoader 隔离

```java
/**
 * 支持多个 ClassLoader 的单例
 */
public class ContextAwareSingleton {
    private static final Map<ClassLoader, ContextAwareSingleton> instances 
        = new ConcurrentHashMap<>();
    
    private ContextAwareSingleton() {}
    
    public static ContextAwareSingleton getInstance() {
        ClassLoader loader = Thread.currentThread().getContextClassLoader();
        return instances.computeIfAbsent(loader, k -> new ContextAwareSingleton());
    }
}
```

### 问题 2: ThreadLocal 版本

```java
/**
 * 线程本地单例
 * 每个线程独享一个实例
 */
public class ThreadLocalSingleton {
    private static final ThreadLocal<ThreadLocalSingleton> instance = 
        ThreadLocal.withInitial(ThreadLocalSingleton::new);
    
    private ThreadLocalSingleton() {}
    
    public static ThreadLocalSingleton getInstance() {
        return instance.get();
    }
}
```

---

## 与其他模式的组合

### + Factory 模式

```java
/**
 * 工厂类本身是单例，返回不同的产品
 */
public enum LoggerFactory {
    INSTANCE;
    
    public Logger createLogger(LoggerType type) {
        switch (type) {
            case FILE:
                return new FileLogger();
            case CONSOLE:
                return new ConsoleLogger();
            case NETWORK:
                return new NetworkLogger();
            default:
                return new ConsoleLogger();
        }
    }
}
```

### + Builder 模式

```java
/**
 * 使用 Builder 创建配置单例
 */
public class Configuration {
    private String host;
    private int port;
    private String database;
    
    private static Configuration instance;
    
    private Configuration() {}
    
    public static void init(Builder builder) {
        instance = builder.build();
    }
    
    public static Configuration getInstance() {
        if (instance == null) {
            throw new IllegalStateException("Configuration 未初始化");
        }
        return instance;
    }
    
    public static class Builder {
        private String host = "localhost";
        private int port = 5432;
        private String database = "default";
        
        public Builder host(String host) {
            this.host = host;
            return this;
        }
        
        public Builder port(int port) {
            this.port = port;
            return this;
        }
        
        public Configuration build() {
            Configuration config = new Configuration();
            config.host = this.host;
            config.port = this.port;
            config.database = this.database;
            return config;
        }
    }
}

// 使用
Configuration.init(
    new Configuration.Builder()
        .host("192.168.1.1")
        .port(3306)
);
```

---

## 单元测试

### 基础测试

```java
@Test
public void testSingletonUniqueness() {
    SingletonLogger logger1 = SingletonLogger.INSTANCE;
    SingletonLogger logger2 = SingletonLogger.INSTANCE;
    
    assertSame(logger1, logger2);  // 同一个对象
}

@Test
public void testConcurrentAccess() throws InterruptedException {
    CountDownLatch latch = new CountDownLatch(100);
    Set<Singleton> instances = Collections.synchronizedSet(new HashSet<>());
    
    for (int i = 0; i < 100; i++) {
        new Thread(() -> {
            instances.add(Singleton.getInstance());
            latch.countDown();
        }).start();
    }
    
    latch.await();
    assertEquals(1, instances.size());  // 只有一个实例
}

@Test
public void testSerialization() throws Exception {
    Singleton obj1 = Singleton.getInstance();
    
    // 序列化
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    new ObjectOutputStream(baos).writeObject(obj1);
    
    // 反序列化
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
    Singleton obj2 = (Singleton) new ObjectInputStream(bais).readObject();
    
    assertSame(obj1, obj2);  // 仍是同一个对象
}
```

---

## 性能基准测试

```java
/**
 * 性能对比测试
 */
class PerformanceBenchmark {
    private static final int ITERATIONS = 1_000_000;
    
    // 测试不同实现的获取速度
    public static void main(String[] args) {
        benchmarkEnum();
        benchmarkBillPugh();
        benchmarkDoubleChecked();
        benchmarkEager();
    }
    
    private static void benchmarkEnum() {
        long start = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            SingletonLogger.INSTANCE.log("test");
        }
        long end = System.nanoTime();
        System.out.printf("Enum: %.2f ms\n", (end - start) / 1_000_000.0);
    }
    
    // ... 其他实现类似
}

// 输出示例:
// Enum:              0.05 ms  ← 最快
// Bill Pugh:         0.06 ms
// Eager:             0.05 ms
// Double-Checked:    0.25 ms  (同步开销)
```

---

## 最佳实践总结

✅ **推荐做法**:
1. **Java**: 优先使用 **枚举** 或 **Bill Pugh**
2. **Python**: 使用 **装饰器**
3. **TypeScript**: 使用 **类静态属性**
4. 提供 **reset/destroy** 方法便于测试
5. 为单例类提供 **详细的 JavaDoc**

❌ **反面教材**:
1. 不要逼迫使用单例（考虑依赖注入）
2. 不要在单例构造函数中做复杂初始化
3. 不要忽视序列化和反射问题
4. 不要在单例中存储大量可变状态
5. 不要在单元测试中滥用单例

---

**相关文件**:
- 概念指南: [SKILL.md](./SKILL.md)
- 应用规划: [forms.md](./forms.md)

## Python 实现

### 装饰器方式
```python
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class MyClass:
    pass
```

### 元类方式
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    pass
```

## 最佳实践

1. ✅ 私有构造函数
2. ✅ 线程安全初始化
3. ✅ 防止序列化破坏
4. ✅ 防止反射创建多实例

## 测试方法

```java
@Test
public void testSingletonIdentity() {
    Singleton s1 = Singleton.getInstance();
    Singleton s2 = Singleton.getInstance();
    assertTrue(s1 == s2);
}
```

## 常见问题

### Q: 线程安全吗？
**A**: 使用 Bill Pugh 单例或枚举实现完全线程安全。

### Q: 支持序列化吗？
**A**: 枚举实现支持，其他实现需要实现 readResolve() 方法。

### Q: 可以反射创建多实例吗？
**A**: 使用枚举实现无法被反射破坏。
