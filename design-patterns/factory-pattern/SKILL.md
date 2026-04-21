---
name: factory-pattern
description: "Use when you need to create objects without specifying concrete classes — 根据运行时条件创建不同实现。Decouple object creation from usage via factory interface, abstract factory for product families, or registry for plugin systems."
license: MIT
---

# 工厂模式 (Factory Pattern)

## 概述

工厂模式属于**创建型模式**，其核心是定义一个创建产品对象的接口，将对象创建的逻辑封装在工厂中，客户端通过工厂而非直接调用构造函数来获取对象实例。

**核心原则**: 
- 向客户端隐藏创建对象的复杂性
- 解耦对象创建与使用的逻辑
- 支持灵活的对象创建策略

## 何时使用

- 对象创建逻辑复杂或需要多步骤初始化
- 需要根据运行时条件/配置灵活切换实现类
- 希望集中管理对象创建逻辑，解耦创建与使用

## 工厂模式的三种形式

### 1. 简单工厂 (Simple Factory)

最简单的形式，通过一个静态方法返回不同的对象实例。

```java
public class LoggerFactory {
    public static Logger createLogger(String type) {
        switch(type) {
            case "FILE": return new FileLogger();
            case "CONSOLE": return new ConsoleLogger();
            case "REMOTE": return new RemoteLogger();
            default: throw new IllegalArgumentException("Unknown type: " + type);
        }
    }
}

// 使用
Logger logger = LoggerFactory.createLogger("FILE");
```

**优点:** 简单直接

**缺点:** 添加新类型需修改工厂，违反开闭原则

### 2. 工厂方法 (Factory Method) ⭐ 推荐

定义创建对象的抽象方法，让子类决定如何创建。

```java
// 抽象工厂类
public abstract class LoggerFactory {
    public abstract Logger createLogger();
    
    // 模板方法
    public void setupAndLog(String message) {
        Logger logger = createLogger();
        logger.initialize();
        logger.log(message);
    }
}

// 具体工厂1
public class FileLoggerFactory extends LoggerFactory {
    @Override
    public Logger createLogger() {
        return new FileLogger();
    }
}

// 具体工厂2
public class ConsoleLoggerFactory extends LoggerFactory {
    @Override
    public Logger createLogger() {
        return new ConsoleLogger();
    }
}

// 使用
LoggerFactory factory = new FileLoggerFactory();
Logger logger = factory.createLogger();
```

**优点:** 
- 符合开闭原则，易于扩展
- 创建逻辑可在子类中定制
- 每个工厂专注于一个产品

**缺点:**
- 类数增加较多
- 代码相对复杂

### 3. 抽象工厂 (Abstract Factory)

用于创建**一族相关的对象**，而不仅仅是单个对象。

```java
public interface UIFactory {
    Button createButton();
    TextField createTextField();
    Window createWindow();
}

public class WindowsUIFactory implements UIFactory {
    @Override
    public Button createButton() { return new WindowsButton(); }
    
    @Override
    public TextField createTextField() { return new WindowsTextField(); }
    
    @Override
    public Window createWindow() { return new WindowsWindow(); }
}

public class MacOSUIFactory implements UIFactory {
    @Override
    public Button createButton() { return new MacOSButton(); }
    
    @Override
    public TextField createTextField() { return new MacOSTextField(); }
    
    @Override
    public Window createWindow() { return new MacOSWindow(); }
}

// 使用
UIFactory factory = isWindows ? new WindowsUIFactory() : new MacOSUIFactory();
Button btn = factory.createButton();
textField = factory.createTextField();
```

## 优缺点分析

### ✅ 优点

1. **职责分离** - 创建逻辑与使用逻辑分离
2. **易于扩展** - 添加新的产品类型无需修改现有代码
3. **集中管理** - 所有创建逻辑集中在工厂
4. **条件解耦** - 客户端无需知道创建的具体类
5. **灵活切换** - 可在运行时切换实现

### ❌ 缺点

1. **代码增加** - 需要定义额外的工厂类
2. **复杂性增加** - 对于简单场景可能过度设计
3. **性能微小开销** - 多一层间接调用
4. **单应职责增加** - 工厂类可能变得复杂

## 常见问题与解决方案

### 问题1: 工厂方法与简单工厂的选择？

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 类型少，变化不频繁 | 简单工厂 | 简洁明快 |
| 类型多，未来可能扩展 | 工厂方法 | 开闭原则 |
| 创建涉及多个相关产品 | 抽象工厂 | 一族产品 |

**解决方案:**
```java
// 简单工厂适合：
LoggerFactory.getLogger("FILE")

// 工厂方法适合：
Logger logger = new FileLoggerFactory().create();

// 抽象工厂适合：
UIFactory factory = OSDetector.isWindows() ? 
    new WindowsUIFactory() : new MacOSUIFactory();
```

### 问题2: 工厂与 Singleton 的关系？

常见模式：工厂返回 Singleton 实例

```java
public class LoggerFactory {
    private static final Map<String, Logger> instances = new ConcurrentHashMap<>();
    
    public static Logger getLogger(String type) {
        return instances.computeIfAbsent(type, t -> {
            switch(t) {
                case "FILE": return new FileLogger();
                case "CONSOLE": return new ConsoleLogger();
                default: throw new IllegalArgumentException();
            }
        });
    }
}
```

### 问题3: 参数化工厂 (参数工厂) 的陷阱？

❌ **反面示例** - 过度参数化
```java
Logger logger = LoggerFactory.create(
    "FILE",              // 类型
    "/var/log/app.log",  // 文件路径
    LogLevel.DEBUG,      // 日志级别
    128 * 1024,          // 缓冲区大小
    true,                // 是否同步
    "UTF-8"              // 编码
);
// 问题：参数过多，难以维护
```

✅ **最佳实践** - 使用 Builder
```java
Logger logger = LoggerFactory.create(
    LoggerConfig.builder()
        .type("FILE")
        .path("/var/log/app.log")
        .level(LogLevel.DEBUG)
        .bufferSize(128 * 1024)
        .sync(true)
        .encoding("UTF-8")
        .build()
);
```

### 问题4: 如何处理创建失败？

```java
public class RobustLoggerFactory {
    private static final Logger FALLBACK_LOGGER = new ConsoleLogger();
    
    public static Logger createLogger(String type) {
        try {
            return doCreate(type);
        } catch (Exception e) {
            System.err.println("Failed to create logger: " + e.getMessage());
            return FALLBACK_LOGGER;  // 降级方案
        }
    }
}
```

## 工厂模式的变体与进阶

### 1. 参数化工厂 (Parameterized Factory)
```java
public class ObjectFactory {
    private Map<String, Supplier<?>> registry = new HashMap<>();
    
    public <T> void register(String key, Supplier<T> creator) {
        registry.put(key, creator);
    }
    
    public <T> T create(String key) {
        return (T) registry.get(key).get();
    }
}

// 使用
ObjectFactory factory = new ObjectFactory();
factory.register("logger", FileLogger::new);
factory.register("cache", RedisCache::new);

Logger logger = factory.create("logger");
```

### 2. 工厂注册表
```java
public class LoggerFactoryRegistry {
    private static Map<String, Class<? extends Logger>> registry = new HashMap<>();
    
    static {
        register("FILE", FileLogger.class);
        register("CONSOLE", ConsoleLogger.class);
        register("REMOTE", RemoteLogger.class);
    }
    
    public static void register(String type, Class<? extends Logger> clazz) {
        registry.put(type, clazz);
    }
    
    public static Logger create(String type) {
        try {
            return registry.get(type).newInstance();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 3. 工厂链 (Factory Chain)
```java
public interface LoggerFactory {
    Logger create(String type);
    LoggerFactory next();
}

public class FileLoggerFactory implements LoggerFactory {
    @Override
    public Logger create(String type) {
        if ("FILE".equals(type)) {
            return new FileLogger();
        }
        return next().create(type);
    }
    
    @Override
    public LoggerFactory next() {
        return new ConsoleLoggerFactory();
    }
}
```

## 最佳实践

1. **优先使用接口** - 工厂应该返回接口类型，不是具体类
   ```java
   // ✓ 好
   public Logger createLogger() { return new FileLogger(); }
   
   // ✗ 不好
   public FileLogger createLogger() { ... }
   ```

2. **Lazy 初始化** - 延迟创建，节省资源
   ```java
   private static final Supplier<Logger> logger = 
       Suppliers.memoize(FileLogger::new);
   ```

3. **配置驱动** - 从配置文件或环境变量读取工厂类型
   ```java
   String loggerType = System.getProperty("logger.type", "CONSOLE");
   Logger logger = LoggerFactory.create(loggerType);
   ```

4. **组合现有工厂** - 和 Singleton、Builder 等模式结合
   ```java
   public Logger createLogger() {
       return Logger.getInstance()  // Singleton
           .withConfig(loggerConfig) // Builder
           .build();
   }
   ```

5. **错误处理** - 工厂应该清晰地处理创建失败
   ```java
   public Logger createLogger(String type) throws LoggerCreationException {
       if (!isSupported(type)) {
           throw new LoggerCreationException("Unsupported type: " + type);
       }
       // ... 创建逻辑
   }
   ```

## 代码示例综合

### Python 实现
```python
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def log(self, message):
        pass

class FileLogger(Logger):
    def log(self, message):
        with open("app.log", "a") as f:
            f.write(message + "\n")

class ConsoleLogger(Logger):
    def log(self, message):
        print(f"[LOG] {message}")

class LoggerFactory(ABC):
    @abstractmethod
    def create_logger(self) -> Logger:
        pass

class FileLoggerFactory(LoggerFactory):
    def create_logger(self) -> Logger:
        return FileLogger()

# 使用
factory: LoggerFactory = FileLoggerFactory()
logger = factory.create_logger()
logger.log("Application started")
```

## 选择指南

| 方法 | 复杂度 | 扩展性 | 推荐场景 |
|------|--------|--------|----------|
| **简单工厂** | 低 | 低 | 类型少且稳定 |
| **工厂方法** | 中 | 高 | 类型多、需扩展 |
| **抽象工厂** | 高 | 极高 | 产品族、跨平台 |
| **参数化工厂** | 中 | 极高 | 插件系统、配置驱动 |

---

## 6个完美的使用场景

### 1. 数据库连接管理（最经典应用）
不同应用需要支持多种数据库（MySQL、PostgreSQL、SQLite、MongoDB）。数据库连接参数不同，初始化过程复杂。

```java
// ❌ 不使用工厂：每处代码都重复初始化逻辑
Connection mysqlConn = DriverManager.getConnection("jdbc:mysql://...");
Connection postgresConn = DriverManager.getConnection("jdbc:postgresql://...");
Connection sqliteConn = DriverManager.getConnection("jdbc:sqlite:...");
// 维护困难，容易出bug

// ✅ 使用工厂：统一管理
DatabaseConnection conn = DatabaseFactory.create(DatabaseType.MYSQL);
```

### 2. UI框架跨平台支持（Abstract Factory应用）
桌面应用需要在Windows、macOS、Linux上都能运行，每个平台的UI组件实现完全不同。

```java
UIFactory factory = OSDetector.isMac() ? new MacUIFactory() : new WindowsUIFactory();
Button button = factory.createButton();      // 自动获得正确平台的Button
TextField field = factory.createTextField();
Window window = factory.createWindow();
```

### 3. 日志系统实现选择
应用支持多种日志输出方式（控制台、文件、远程服务器、数据库），用户通过配置灵活选择。

```java
Logger logger = LoggerFactory.create(config.getLoggerType());
// 配置改变时，无需修改代码，自动切换实现
```

### 4. 支付系统多渠道支持
电商平台需要支持多个支付渠道（支付宝、微信、Stripe、银行卡转账），每个渠道的API和流程不同。

```java
PaymentGateway gateway = PaymentFactory.create(userChoice.getPaymentMethod());
gateway.initialize(config);
gateway.charge(amount);
```

### 5. 消息队列选择
后端应用需要支持多个MQ系统（RabbitMQ、Kafka、ActiveMQ）以适应不同部署场景。

```java
MessageQueue queue = MessageQueueFactory.create("KAFKA");  // 配置驱动
queue.publish(topic, message);
```

### 6. 文档处理多格式支持
文档系统需要处理多种格式文件（PDF、Word、Excel、PowerPoint），每种格式的读写实现完全不同。

```java
DocumentHandler handler = DocumentFactory.create(file.getExtension());
Document doc = handler.read(file);
doc.process();
handler.write(file);
```

---

## 4个实现方法的完整对比与选择

### 方法1: 简单工厂（最直接，适合小型系统）

```java
/**
 * 简单工厂：通过静态方法返回不同的产品
 * 优点：实现最简单
 * 缺点：添加新类型需修改工厂代码（违反开闭原则）
 */
public class LoggerFactory {
    public static Logger create(String type) {
        switch(type.toUpperCase()) {
            case "FILE":
                return createFileLogger();
            case "CONSOLE":
                return createConsoleLogger();
            case "DATABASE":
                return createDatabaseLogger();
            case "REMOTE":
                return createRemoteLogger();
            default:
                throw new IllegalArgumentException("Unknown logger type: " + type);
        }
    }
    
    private static Logger createFileLogger() {
        FileLogger logger = new FileLogger();
        logger.setFilePath(System.getProperty("log.file"));
        logger.setBufferSize(Integer.getInteger("log.buffer", 4096));
        logger.setRotationSize(Long.getLong("log.rotation", 10L * 1024 * 1024));
        return logger;
    }
    
    private static Logger createConsoleLogger() {
        ConsoleLogger logger = new ConsoleLogger();
        logger.setLogLevel(LogLevel.valueOf(System.getProperty("log.level", "INFO")));
        return logger;
    }
    
    private static Logger createDatabaseLogger() {
        DatabaseLogger logger = new DatabaseLogger();
        logger.setDatabaseUrl(System.getProperty("log.db.url"));
        logger.setTableName(System.getProperty("log.db.table", "logs"));
        return logger;
    }
    
    private static Logger createRemoteLogger() {
        RemoteLogger logger = new RemoteLogger();
        logger.setRemoteUrl(System.getProperty("log.remote.url"));
        logger.setTimeout(Integer.getInteger("log.remote.timeout", 5000));
        return logger;
    }
}

// 使用简单工厂
Logger fileLogger = LoggerFactory.create("FILE");
Logger consoleLogger = LoggerFactory.create("CONSOLE");
```

**何时使用简单工厂**：
- ✅ 产品类型少（1-3个）且稳定
- ✅ 创建逻辑不复杂
- ✅ 小型项目或快速原型
- ❌ 产品类型频繁增加
- ❌ 需要工厂本身可扩展

### 方法2: 工厂方法（最灵活，推荐用于生产环境）

```java
/**
 * 工厂方法：定义创建接口，由子类实现
 * 优点：完全符合开闭原则，新增产品无需修改现有工厂
 * 缺点：类数增加较多
 */

// 1. 产品接口
public interface Logger {
    void log(String message);
}

// 2. 具体产品
public class FileLogger implements Logger {
    @Override
    public void log(String message) { System.out.println("[FILE] " + message); }
}

public class ConsoleLogger implements Logger {
    @Override
    public void log(String message) { System.out.println("[CONSOLE] " + message); }
}

// 3. 工厂接口
public abstract class LoggerFactory {
    // 工厂方法 - 由子类实现
    public abstract Logger createLogger();
    
    // 模板方法 - 使用工厂方法
    public final void setupAndLog(String message) {
        Logger logger = createLogger();
        logger.log(message);
    }
}

// 4. 具体工厂
public class FileLoggerFactory extends LoggerFactory {
    @Override
    public Logger createLogger() {
        FileLogger logger = new FileLogger();
        logger.setPath(getConfigPath());
        logger.setRotationSize(getRotationSize());
        return logger;
    }
    
    private String getConfigPath() {
        return System.getProperty("log.file.path", "/var/log/app.log");
    }
    
    private long getRotationSize() {
        return Long.getLong("log.rotation.size", 10L * 1024 * 1024);
    }
}

public class ConsoleLoggerFactory extends LoggerFactory {
    @Override
    public Logger createLogger() {
        ConsoleLogger logger = new ConsoleLogger();
        logger.setLogLevel(LogLevel.DEBUG);
        return logger;
    }
}

// 5. 使用工厂方法
LoggerFactory factory = new FileLoggerFactory();  // 或 new ConsoleLoggerFactory()
Logger logger = factory.createLogger();
logger.log("Application started");
```

**何时使用工厂方法**：
- ✅ 产品类型多（3个以上）或可能增加
- ✅ 每个工厂有特殊的创建逻辑
- ✅ 支持工厂本身的继承和定制
- ✅ 需要严格遵循开闭原则
- ❌ 会大幅增加代码量
- ❌ 对于简单创建逻辑过度设计

### 方法3: 抽象工厂（应对复杂系统，创建相关产品族）

```java
/**
 * 抽象工厂：创建一族相关的产品
 * 使用场景：需要创建多个相互关联的产品
 * 例：跨平台UI系统要同时创建Button、TextField、Window等
 */

// 1. 产品族接口
public interface Button { void click(); }
public interface TextField { void setText(String text); }
public interface Window { void display(); }

// 2. Windows平台产品族
public class WindowsButton implements Button {
    @Override
    public void click() { System.out.println("[Windows] Button clicked"); }
}

public class WindowsTextField implements TextField {
    @Override
    public void setText(String text) { System.out.println("[Windows] TextField: " + text); }
}

public class WindowsWindow implements Window {
    @Override
    public void display() { System.out.println("[Windows] Window displayed"); }
}

// 3. Mac平台产品族
public class MacButton implements Button {
    @Override
    public void click() { System.out.println("[Mac] Button clicked"); }
}

public class MacTextField implements TextField {
    @Override
    public void setText(String text) { System.out.println("[Mac] TextField: " + text); }
}

public class MacWindow implements Window {
    @Override
    public void display() { System.out.println("[Mac] Window displayed"); }
}

// 4. 抽象工厂
public interface UIFactory {
    Button createButton();
    TextField createTextField();
    Window createWindow();
}

// 5. 具体工厂
public class WindowsUIFactory implements UIFactory {
    @Override
    public Button createButton() { return new WindowsButton(); }
    
    @Override
    public TextField createTextField() { return new WindowsTextField(); }
    
    @Override
    public Window createWindow() { return new WindowsWindow(); }
}

public class MacUIFactory implements UIFactory {
    @Override
    public Button createButton() { return new MacButton(); }
    
    @Override
    public TextField createTextField() { return new MacTextField(); }
    
    @Override
    public Window createWindow() { return new MacWindow(); }
}

// 6. 使用抽象工厂
UIFactory factory = PlatformDetector.isMac() ? 
    new MacUIFactory() : new WindowsUIFactory();

Button btn = factory.createButton();
TextField field = factory.createTextField();
Window window = factory.createWindow();

// 所有UI元素自动匹配平台！
```

**何时使用抽象工厂**：
- ✅ 需要创建多个相关联的产品
- ✅ 不同的产品族之间要能整体切换
- ✅ 系统需要与具体产品族无关
- ❌ 产品族关联性不强
- ❌ 新增产品会影响所有工厂

### 方法4: 参数化工厂 + 注册表（最灵活，适合大型系统）

```java
/**
 * 参数化工厂 + 注册表：完全解耦，支持动态注册
 * 优点：最灵活，新增产品只需注册，无需修改工厂
 * 缺点：操作通过反射或Function，类型检查较弱
 */

// 1. 产品接口
public interface Logger {
    void log(String message);
}

// 2. 具体产品（可以在任何地方定义）
public class FileLogger implements Logger {
    @Override
    public void log(String message) { System.out.println("[FILE] " + message); }
}

public class ConsoleLogger implements Logger {
    @Override
    public void log(String message) { System.out.println("[CONSOLE] " + message); }
}

public class EmailLogger implements Logger {
    @Override
    public void log(String message) { System.out.println("[EMAIL] " + message); }
}

// 3. 参数化工厂 - 支持动态注册
public class LoggerFactory {
    private static final Map<String, Supplier<Logger>> REGISTRY = 
        new ConcurrentHashMap<>();
    
    static {
        // 默认注册
        register("FILE", FileLogger::new);
        register("CONSOLE", ConsoleLogger::new);
        register("EMAIL", EmailLogger::new);
    }
    
    /**
     * 动态注册新的Logger实现
     */
    public static void register(String type, Supplier<Logger> creator) {
        REGISTRY.put(type.toUpperCase(), creator);
        System.out.println("[Factory] Registered logger type: " + type);
    }
    
    /**
     * 注销Logger实现
     */
    public static void unregister(String type) {
        REGISTRY.remove(type.toUpperCase());
    }
    
    /**
     * 创建Logger实例
     */
    public static Logger create(String type) {
        Supplier<Logger> creator = REGISTRY.get(type.toUpperCase());
        if (creator == null) {
            throw new IllegalArgumentException(
                "Unknown logger type: " + type + 
                ". Available types: " + REGISTRY.keySet()
            );
        }
        return creator.get();
    }
    
    /**
     * 获取所有已注册的类型
     */
    public static Set<String> getAvailableTypes() {
        return new HashSet<>(REGISTRY.keySet());
    }
    
    /**
     * 支持带参数的工厂注册（Java 8+）
     */
    public static void registerWithConfig(String type, Function<Map<String, String>, Logger> creator) {
        // 这里可以支持更复杂的注册逻辑
    }
}

// 4. 使用参数化工厂
Logger fileLogger = LoggerFactory.create("FILE");
Logger consoleLogger = LoggerFactory.create("CONSOLE");

// 运行时动态添加新的Logger实现
LoggerFactory.register("DATABASE", () -> {
    DatabaseLogger logger = new DatabaseLogger();
    logger.setTableName("application_logs");
    return logger;
});

Logger dbLogger = LoggerFactory.create("DATABASE");

// 查询可用类型
System.out.println("Available loggers: " + LoggerFactory.getAvailableTypes());
```

**何时使用参数化工厂**：
- ✅ 需要支持插件系统
- ✅ Logger类型由配置文件决定
- ✅ 需要在不修改代码的情况下扩展
- ✅ 系统足够大，值得投入复杂性
- ❌ 类型数有限且稳定
- ❌ 需要编译期类型检查

---

## 4个常见问题 + 完整解决方案

### 问题1: 简单工厂 vs 工厂方法 vs 抽象工厂 的选择
**症状**: 不清楚在什么场景使用哪种工厂

```java
// ✅ 决策树

if (只有1-2种产品类型 && 不太可能增加) {
    使用简单工厂;  // 代码最少
} else if (产品类型3个以上 || 将来可能扩展) {
    if (各产品类型创建逻辑差异大) {
        使用工厂方法;  // 每个工厂类定制化
    } else if (需要创建相关的产品族) {
        使用抽象工厂;  // Button+TextField+Window整体切换
    } else {
        使用参数化工厂;  // 配置驱动，最灵活
    }
}

// 实际例子
// Database -> 使用参数化工厂 (MySQL/PostgreSQL/SQLite灵活切换)
// UI Framework -> 使用抽象工厂 (Windows/Mac/Linux整体平台转换)
// Logger -> 使用工厂方法 (FileLogger/ConsoleLogger创建逻辑差异大)
```

### 问题2: 工厂与Singleton的关系
**症状**: 是否工厂应该返回Singleton？什么时候返回新实例？

```java
// ✅ 解决方案：根据产品特性决定

public class LoggerFactory {
    private static final Map<String, Logger> SINGLETON_INSTANCES = new ConcurrentHashMap<>();
    
    /**
     * 对于本身应该唯一的服务（数据库连接），工厂返回Singleton
     */
    public static Logger createSystemLogger(String type) {
        return SINGLETON_INSTANCES.computeIfAbsent(type, t -> {
            if ("MAIN".equals(t)) {
                return new FileLogger("/var/log/system.log");
            }
            return new ConsoleLogger();
        });
    }
    
    /**
     * 对于可以多实例的对象（用户会话Logger），工厂返回新实例
     */
    public static Logger createUserSessionLogger(String userId, String sessionId) {
        FileLogger logger = new FileLogger();
        logger.setPath("/var/logs/users/" + userId + "/" + sessionId + ".log");
        return logger;  // 返回新实例
    }
    
    /**
     * 对于有状态的对象（缓冲Logger），可能使用对象池
     */
    private static Queue<BufferedLogger> bufferPool = new LinkedList<>();
    
    public static BufferedLogger createBufferedLogger() {
        synchronized (bufferPool) {
            if (bufferPool.isEmpty()) {
                return new BufferedLogger();
            }
            return bufferPool.poll();
        }
    }
    
    public static void releaseBufferedLogger(BufferedLogger logger) {
        logger.reset();
        synchronized (bufferPool) {
            bufferPool.offer(logger);
        }
    }
}
```

### 问题3: 参数过多导致工厂方法签名复杂
**症状**: 创建对象需要很多参数，工厂方法变成：`create(String, int, boolean, double, Color, ...)`

```java
// ❌ 反面示例
public Logger createLogger(
    String name,
    String filePath,
    LogLevel level,
    int bufferSize,
    boolean async,
    String encoding,
    boolean rotation,
    long maxFileSize,
    int maxBackups
) { /* ... */ }

// 调用时难以维护
Logger logger = factory.createLogger(
    "MyLogger",
    "/var/log/app.log",
    LogLevel.INFO,
    4096,
    true,
    "UTF-8",
    true,
    10L * 1024 * 1024,
    5
);  // 容易出错

// ✅ 解决方案1：使用Builder模式
public class LoggerConfig {
    public static Builder builder() { return new Builder(); }
    
    public static class Builder {
        private String name = "DefaultLogger";
        private String filePath = "/var/log/default.log";
        private LogLevel level = LogLevel.INFO;
        private int bufferSize = 4096;
        // ... 其他字段
        
        public Builder name(String name) { this.name = name; return this; }
        public Builder filePath(String filePath) { this.filePath = filePath; return this; }
        public Builder level(LogLevel level) { this.level = level; return this; }
        // ... 其他setter
        
        public LoggerConfig build() {
            return new LoggerConfig(this);
        }
    }
}

// 工厂简化为
public Logger createLogger(LoggerConfig config) {
    // 使用config中的字段
}

// 调用时清晰易懂
Logger logger = factory.createLogger(
    LoggerConfig.builder()
        .name("MyLogger")
        .filePath("/var/log/app.log")
        .level(LogLevel.DEBUG)
        .bufferSize(8192)
        .async(true)
        .build()
);

// ✅ 解决方案2：使用配置文件驱动工厂
public Logger createLogger(String configFile) {
    Properties config = new Properties();
    config.load(new FileInputStream(configFile));
    // 从配置文件读取所有参数
    return createLoggerFromConfig(config);
}

// 配置文件示例 (logger.properties)
// logger.name=MyLogger
// logger.filePath=/var/log/app.log
// logger.level=DEBUG
// logger.bufferSize=8192
```

### 问题4: 创建失败的优雅处理
**症状**: 工厂创建过程中可能出错（文件系统权限、网络不可用等），如何处理？

```java
// ❌ 反面示例：异常导致程序崩溃
Logger logger = LoggerFactory.create("FILE");  // 如果权限不足，直接异常

// ✅ 解决方案1：阶段性降级
public class ResilientLoggerFactory {
    private static final Logger FALLBACK_LOGGER = new ConsoleLogger();
    
    public static Logger create(String type) {
        try {
            // 优先创建首选Logger
            return createPrimary(type);
        } catch (FilePermissionException e) {
            logger.warn("Cannot create primary logger: " + e.getMessage());
            
            // 降级到备选方案
            try {
                return createFallback(type);
            } catch (Exception e2) {
                logger.warn("Cannot create fallback logger: " + e2.getMessage());
                
                // 最终降级到控制台
                return FALLBACK_LOGGER;
            }
        }
    }
    
    private static Logger createPrimary(String type) {
        // 创建首选实现
    }
    
    private static Logger createFallback(String type) {
        // 创建备选实现
    }
}

// ✅ 解决方案2：异步创建 + 重试
public class AsyncLoggerFactory {
    public static CompletableFuture<Logger> createAsync(String type) {
        return CompletableFuture.supplyAsync(() -> {
            int retries = 3;
            Exception lastException = null;
            
            for (int i = 0; i < retries; i++) {
                try {
                    return createLogger(type);
                } catch (TemporaryException e) {
                    lastException = e;
                    if (i < retries - 1) {
                        sleep(1000 * (i + 1));  // 指数退避
                    }
                }
            }
            
            throw new FactoryException("Failed to create logger after " + retries + " retries", lastException);
        });
    }
}

// ✅ 解决方案3：创建结果包装
public class LoggerCreationResult {
    private final Logger logger;
    private final boolean isSuccess;
    private final String errorMessage;
    private final Exception exception;
    
    public static LoggerCreationResult success(Logger logger) {
        return new LoggerCreationResult(logger, true, null, null);
    }
    
    public static LoggerCreationResult failure(String message, Exception e) {
        return new LoggerCreationResult(null, false, message, e);
    }
    
    public Logger getLoggerOrThrow() throws FactoryException {
        if (!isSuccess) {
            throw new FactoryException(errorMessage, exception);
        }
        return logger;
    }
    
    public Logger getLoggerOrDefault(Logger defaultLogger) {
        return isSuccess ? logger : defaultLogger;
    }
}

// 使用
LoggerCreationResult result = LoggerFactory.tryCreate("FILE");
Logger logger = result.getLoggerOrDefault(FALLBACK_LOGGER);
```

---

## 最佳实践指南

### 1️⃣ 返回接口而非具体类
```java
// ❌ 错误：返回具体类
public static FileLogger create() {
    return new FileLogger();
}

// ✅ 正确：返回接口
public static Logger create(String type) {
    if ("FILE".equals(type)) {
        return new FileLogger();
    }
    return new ConsoleLogger();
}
```

### 2️⃣ 虽然工厂隐藏了创建逻辑，但仍然要文档化
```java
/**
 * 创建Logger实例
 * 
 * @param type 日志类型：
 *             - "FILE"：文件输出，需要log.file.path系统属性
 *             - "CONSOLE"：控制台输出
 *             - "DATABASE"：数据库输出，需要配置数据源
 * 
 * @return Logger实例（线程安全）
 * 
 * @throws IllegalArgumentException 类型不支持
 * @throws IllegalStateException 配置缺失或不合法
 * 
 * 示例：
 * System.setProperty("log.file.path", "/var/log/app.log");
 * Logger logger = LoggerFactory.create("FILE");
 * logger.log("Hello");
 */
public static Logger create(String type) { /* ... */ }
```

### 3️⃣ 支持工厂的诊断和反思
```java
public class LoggerFactory {
    private static final Map<String, Integer> CREATION_STATS = new ConcurrentHashMap<>();
    
    public static Logger create(String type) {
        CREATION_STATS.merge(type, 1, Integer::sum);
        // ... 创建逻辑
    }
    
    /**
     * 获取创建统计（用于监控和调试）
     */
    public static Map<String, Integer> getCreationStats() {
        return new HashMap<>(CREATION_STATS);
    }
}
```

### 4️⃣ 性能考虑
```java
// ✅ 缓存工厂实例（对于工厂方法）
private static final LoggerFactory FILE_FACTORY = new FileLoggerFactory();
private static final LoggerFactory CONSOLE_FACTORY = new ConsoleLoggerFactory();

public static Logger create(String type) {
    LoggerFactory factory = FACTORY_MAP.get(type);  // O(1)查询
    return factory.createLogger();
}

// ✅ 对象池优化（对于创建成本高的对象）
public class PooledLoggerFactory {
    private static final BlockingQueue<Logger> POOL = new LinkedBlockingQueue<>(10);
    
    public static Logger borrow() throws InterruptedException {
        Logger logger = POOL.poll();
        return logger != null ? logger : new FileLogger();
    }
    
    public static void release(Logger logger) throws InterruptedException {
        logger.reset();
        POOL.offer(logger);
    }
}
```

### 5️⃣ 与其他模式结合
```java
// 工厂 + Singleton = 单例工厂返回单例产品
Logger logger = SingletonLoggerFactory.getInstance();

// 工厂 + Builder = 参数化创建
Logger logger = LoggerFactory.create(
    LoggerConfig.builder().file("/tmp/app.log").level(DEBUG).build()
);

// 工厂 + Strategy = 工厂选择策略算法
Sorter sorter = SorterFactory.create(config.getSortAlgorithm());
```

---

## 与其他模式的关系

| 模式 | 关系 | 何时结合 | 示例 |
|--------|------|--------|------|
| **Abstract Factory** | 工厂方法的升级版，创建一族产品 | 需要平台相关的多个产品 | UI组件（Button+TextField） |
| **Singleton** | 工厂返回单例产例 | 产品应该全局唯一 | 数据库连接、日志系统 |
| **Builder** | 工厂负责创建，Builder负责配置 | 创建参数众多 | LoggerFactory + LoggerConfig |
| **Prototype** | 通过克隆创建产品 | 创建成本高 | 复杂对象的工厂使用克隆 |
| **Strategy** | 工厂创建具体策略 | 需要运行时选择算法 | SorterFactory创建不同排序策略 |
| **Decorator** | 工厂可返回装饰后的产品 | 需要动态功能组合 | Logger功能叠加（日志+缓冲+加密） |

---

## 多语言实现考量

### Java特性应用
- 使用`Supplier<T>`支持泛型工厂
- 利用`ServiceLoader`支持插件化工厂
- 反射动态加载实现类

### Python考量
- 鸭子类型使工厂更灵活
- 支持一级函数作为工厂
- 模块导入本身可作为工厂

### TypeScript/JavaScript考量
- 支持高阶函数作为工厂
- 类型系统支持泛型工厂
- 动态require()支持运行时加载

---

## 何时避免使用

- ❌ **只有一个实现**: 工厂本身就是冗余
- ❌ **创建极其简单**: 对象创建就一行代码，工厂无价值
- ❌ **客户端需要知道具体类**: 工厂失去意义
- ❌ **创建逻辑频繁变化**: 考虑参数配置而非代码修改
- ❌ **系统足够小，不需要扩展**: 过度架构增加维护负担
