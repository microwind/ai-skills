---
name: 单例模式
description: "确保类只有一个实例，并提供全局访问点。在设计全局配置、日志系统、连接池等单一实例应用时使用。"
license: MIT
---

# 单例模式 (Singleton Pattern)

## 概述

单例模式确保一个类只有一个实例，并提供一个全局访问点。这个模式在需要控制资源共享或全局状态时非常有用。

**核心原则**: 
- 🎯 唯一实例：全局仅有一个对象
- 🔐 全局访问：提供受控的全局访问点
- ⏰ 延迟初始化：按需创建，优化启动时间
- 🧵 线程安全：多线程环境中保证唯一性

## 何时使用

### 完美适用场景

| 场景 | 说明 | 优先级 |
|------|------|--------|
| **日志系统** | 全应用共享一个日志记录器 | ⭐⭐⭐ |
| **配置管理** | 全局应用配置对象 | ⭐⭐⭐ |
| **数据库连接池** | 管理数据库连接资源 | ⭐⭐⭐ |
| **缓存管理** | 应用级缓存 | ⭐⭐⭐ |
| **事件总线** | 全局事件发布订阅 | ⭐⭐ |
| **线程池** | 共享线程资源 | ⭐⭐⭐ |

### 触发信号（何时考虑使用）

✅ 以下信号表明应该使用单例：
- "这个类全应用只需要一个实例"
- "需要全局访问点，避免传递参数"
- "创建成本高，初始化工作量大"
- "需要保证全应用数据一致"
- "资源受限（连接、内存等）"

❌ 以下情况不应该使用：
- "可能需要多个实例"
- "需要灵活切换实现"
- "单元测试需要 mock"
- "需要独立的配置副本"

## 单例模式的优缺点

### 优点 ✅

1. **确保唯一性**
   - 全应用仅有一个实例
   - 无需传递对象引用
   - 代码简洁直观

2. **全局访问点**
   - 任何地方可访问
   - 无需依赖注入框架
   - 兼容遗留系统

3. **延迟初始化**
   - 减少启动时间
   - 按需创建资源
   - 优化应用性能

4. **线程安全**
   - 多线程环境可靠
   - 不需要额外同步
   - 性能更好

### 缺点 ❌

1. **难以测试**
   - ❌ 全局状态难以 mock
   - ❌ 测试之间会相互影响
   - ❌ 需要特殊的测试框架

2. **隐藏依赖**
   - ❌ 代码依赖关系不清晰
   - ❌ 难以追踪数据流
   - ❌ 对新开发者不友好

3. **限制灵活性**
   - ❌ 无法灵活创建多个实例
   - ❌ 不支持同时使用不同版本
   - ❌ 扩展性受限

4. **线程复杂性**
   - ❌ 初心者容易出错
   - ❌ 序列化、反射等可能破坏单例
   - ❌ 需要特殊处理

## 单例模式的 5 种实现方式

### 1. 懒汉式（Lazy Initialization）- 最基础

```java
public class LazyLogger {
    private static LazyLogger instance;
    
    private LazyLogger() {}
    
    public static synchronized LazyLogger getInstance() {
        if (instance == null) {
            instance = new LazyLogger();
        }
        return instance;
    }
}
```

**特点**: 
- ✅ 延迟初始化
- ❌ 每次访问都需要同步，性能一般
- 🎯 适用：初始化成本高但访问不频繁的场景

---

### 2. 饿汉式（Eager Initialization）- 最简洁

```java
public class EagerLogger {
    private static final EagerLogger instance = new EagerLogger();
    
    private EagerLogger() {}
    
    public static EagerLogger getInstance() {
        return instance;
    }
}
```

**特点**:
- ✅ 线程安全，性能最好
- ✅ 代码最简洁
- ❌ 启动时就创建，耗费资源
- 🎯 适用：初始化快，全应用都使用的场景

---

### 3. 双检查锁定（Double-Checked Locking）- 最实用

```java
public class DoubleCheckedLogger {
    private static volatile DoubleCheckedLogger instance;
    
    private DoubleCheckedLogger() {}
    
    public static DoubleCheckedLogger getInstance() {
        if (instance == null) {  // 第一次检查（无锁）
            synchronized (DoubleCheckedLogger.class) {
                if (instance == null) {  // 第二次检查（有锁）
                    instance = new DoubleCheckedLogger();
                }
            }
        }
        return instance;
    }
}
```

**特点**:
- ✅ 延迟初始化且性能好
- ✅ 减少同步开销
- ⚠️ 代码复杂，需要 `volatile` 关键字
- 🎯 适用：初始化成本高且访问频繁

**关键点**: 必须使用 `volatile` 关键字，否则可能在多线程中失败

---

### 4. Bill Pugh 单例（静态内部类）- 最优雅 ⭐⭐⭐

```java
public class BillPughLogger {
    private BillPughLogger() {}
    
    // 静态内部类（延迟初始化）
    private static class LoggerHolder {
        private static final BillPughLogger instance = new BillPughLogger();
    }
    
    public static BillPughLogger getInstance() {
        return LoggerHolder.instance;
    }
}
```

**特点**:
- ✅ 延迟初始化，性能最佳
- ✅ 线程安全（由JVM保证）
- ✅ 代码简洁优雅
- ✅ 自动处理反序列化
- 🎯 **推荐用于 Java**

---

### 5. 枚举单例（Enum）- 最安全 ⭐⭐⭐

```java
public enum EnumLogger {
    INSTANCE;
    
    public void log(String message) {
        System.out.println("LOG: " + message);
    }
}

// 使用方式
EnumLogger.INSTANCE.log("Hello");
```

**特点**:
- ✅ 天然防止反射攻击
- ✅ 天然防止序列化破坏
- ✅ 线程安全
- ✅ 代码最简洁
- ✅ 支持序列化保持单例
- 🎯 **最安全的实现方式**

---

## 常见问题与解决方案

### 问题 1: 序列化破坏单例

**现象**: 对象序列化后反序列化，得到不同的实例

**原因**: 默认反序列化会创建新实例

**解决方案**:

```java
public class SerializedSingleton implements Serializable {
    private static final SerializedSingleton instance = new SerializedSingleton();
    
    private SerializedSingleton() {}
    
    public static SerializedSingleton getInstance() {
        return instance;
    }
    
    // 防止反序列化破坏单例
    protected Object readResolve() {
        return getInstance();
    }
}
```

**最佳实践**: 使用枚举单例，天然支持序列化

---

### 问题 2: 反射攻击破坏单例

**现象**: 使用反射强制调用构造函数，创建新实例

```java
// 反射攻击示例（危险！）
Constructor<Singleton> constructor = 
    Singleton.class.getDeclaredConstructor();
constructor.setAccessible(true);
Singleton fakeInstance = constructor.newInstance();  // 创建了新实例！
```

**解决方案**:

```java
public class SafeSingleton {
    private static final SafeSingleton instance = new SafeSingleton();
    private static boolean created = false;
    
    private SafeSingleton() {
        if (created) {
            throw new IllegalStateException("单例已被创建，不能重复创建");
        }
        created = true;
    }
    
    public static SafeSingleton getInstance() {
        return instance;
    }
}
```

**最佳实践**: 使用枚举单例，完全防止反射攻击

---

### 问题 3: 单元测试困难

**现象**: 全局单例状态污染测试，测试之间相互影响

**解决方案**:

```java
// 方案1: 为测试提供 reset 方法
public class MockableSingleton {
    private static MockableSingleton instance = new MockableSingleton();
    
    public static MockableSingleton getInstance() {
        return instance;
    }
    
    // 仅供测试使用
    static void reset() {
        instance = new MockableSingleton();
    }
    
    static void setInstance(MockableSingleton mock) {
        instance = mock;
    }
}

// 测试代码
@After
public void tearDown() {
    MockableSingleton.reset();
}
```

**最佳实践**: 考虑使用依赖注入替代品

---

### 问题 4: 多线程竞态条件

**现象**: 多线程下出现多个实例

**原因**: 初始化代码不是原子操作

**解决方案**:

```java
// ❌ 错误做法
private static Singleton instance;
public static Singleton getInstance() {
    if (instance == null) {
        instance = new Singleton();  // 非原子操作！
    }
    return instance;
}

// ✅ 正确做法1: Bill Pugh
private static class Holder {
    static Singleton instance = new Singleton();
}
public static Singleton getInstance() {
    return Holder.instance;  // JVM保证线程安全
}

// ✅ 正确做法2: 枚举
public enum Singleton { INSTANCE; }
```

---

### 问题 5: ClassLoader 隔离问题

**现象**: 不同 ClassLoader 加载产生多个实例

**解决方案**:

```java
public class ClassLoaderAwareSingleton {
    private static final Map<ClassLoader, ClassLoaderAwareSingleton> instances 
        = new ConcurrentHashMap<>();
    
    private ClassLoaderAwareSingleton() {}
    
    public static ClassLoaderAwareSingleton getInstance() {
        ClassLoader loader = Thread.currentThread().getContextClassLoader();
        return instances.computeIfAbsent(loader, 
            k -> new ClassLoaderAwareSingleton());
    }
}
```

---

## 最佳实践 TOP 5

### 1. ✅ 选择正确的实现方式

| 实现方式 | Java | Python | TypeScript | 推荐度 |
|---------|------|--------|-----------|--------|
| 饿汉式 | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ |
| 懒汉式 | ⭐ | ⭐ | ⭐ | ⭐ |
| 双检查锁 | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ |
| Bill Pugh | ⭐⭐⭐ | - | - | ⭐⭐⭐ |
| 枚举 | ⭐⭐⭐ | - | - | ⭐⭐⭐ |

**建议**:
- **Java**: 优先选择枚举或 Bill Pugh
- **Python**: 使用装饰器或元类
- **TypeScript**: 使用类静态属性

### 2. ✅ 考虑依赖注入作为替代

```java
// ❌ 过度使用单例
class UserService {
    private Logger logger = Logger.getInstance();  // 隐藏依赖
}

// ✅ 使用依赖注入
class UserService {
    private final Logger logger;
    public UserService(Logger logger) {  // 显式依赖
        this.logger = logger;
    }
}
```

**优势**:
- 代码更清晰
- 易于测试
- 便于扩展

### 3. ✅ 提供受控的生命周期

```java
public class ControlledSingleton {
    private static ControlledSingleton instance;
    private static final Object lock = new Object();
    
    private ControlledSingleton() {}
    
    public static void initialize() {
        synchronized (lock) {
            if (instance == null) {
                instance = new ControlledSingleton();
            }
        }
    }
    
    public static ControlledSingleton getInstance() {
        if (instance == null) {
            throw new IllegalStateException("未初始化");
        }
        return instance;
    }
    
    public static void destroy() {
        synchronized (lock) {
            instance = null;
        }
    }
}
```

### 4. ✅ 提供有意义的日志

```java
public enum SingletonLogger {
    INSTANCE;
    
    private SingletonLogger() {
        System.out.println("日志系统初始化: " + System.currentTimeMillis());
    }
    
    public void log(String message) {
        System.out.println("[" + new Date() + "] " + message);
    }
}
```

### 5. ✅ 文档化使用说明

```java
/**
 * 全应用日志单例
 * 
 * 使用方式:
 * <pre>
 * Logger logger = Logger.getInstance();
 * logger.info("应用启动成功");
 * </pre>
 * 
 * 线程安全: 是
 * 序列化安全: 是（使用 readResolve）
 * 
 * 注意: 不支持单元测试中的 mock，考虑注入 Logger 接口
 */
public class Logger { ... }
```

---

## 与其他模式的关系

| 模式 | 关系 | 场景 |
|------|------|------|
| **Factory** | 工厂返回单例实例 | 延迟创建单例 |
| **Abstract Factory** | 工厂类通常是单例 | 简化工厂访问 |
| **Facade** | 外观模式常用单例 | 简化子系统访问 |
| **Proxy** | 结合代理实现访问控制 | 受限的实例访问 |
| **Observer** | 事件总线通常是单例 | 全应用事件系统 |

---

## 语言特定实现

### Python 装饰器方式
```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class DatabasePool:
    pass
```

### TypeScript 类静态属性
```typescript
class Logger {
    private static instance: Logger;
    
    private constructor() {}
    
    public static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }
}
```

---

## 性能对比

| 实现 | 首次访问 | 后续访问 | 内存开销 | 线程安全 |
|------|---------|---------|--------|---------|
| 饿汉式 | 应用启动 | 最快 ✨ | 低 | ✅ |
| 懒汉式 | 首次获取 | 有同步开销 | 最低 | ⚠️ |
| 双检查锁 | 首次获取 | 无开销 | 低 | ✅ |
| Bill Pugh | 首次获取 | 无开销 | 低 | ✅ |
| 枚举 | 应用启动 | 最快 | 低 | ✅ |

---

## 何时应避免使用

❌ **以下情况不应使用单例**:

1. **可能需要多个实例**
   ```java
   // ❌ 错误: 数据库连接应该用连接池，不是单例
   public enum DatabaseConnection { INSTANCE; }
   ```

2. **需要灵活切换实现**
   ```java
   // ❌ 错误: 单例限制了灵活性
   Logger logger = Logger.getInstance();
   
   // ✅ 正确: 使用接口注入
   Logger logger = container.get(Logger.class);
   ```

3. **严格的单元测试要求**
   ```java
   // ❌ 单例难以 mock
   Singleton singleton = Singleton.getInstance();
   
   // ✅ 使用接口便于测试
   interface Service {}
   class ServiceImpl implements Service {}
   ```

4. **需要独立的配置副本**
   ```java
   // ❌ 单例无法提供不同的配置
   Config config = Config.getInstance();
   
   // ✅ 创建多个配置对象
   Config config1 = new Config("app.properties");
   Config config2 = new Config("test.properties");
   ```

---

## 总结

**单例模式何时使用**:
- ✅ 确实需要全应用唯一实例
- ✅ 资源受限（连接、内存等）
- ✅ 初始化成本高
- ✅ 需要全局访问点

**正确实现方式**:
- Java: 优先选择 **枚举** 或 **Bill Pugh**
- Python: 使用 **装饰器** 或 **元类**
- TypeScript: 使用 **类静态属性**

**记住**: 单例是一个有用的模式，但也容易被滥用。谨慎使用，优先考虑依赖注入！

---

**相关文件**:
- 应用规划: [forms.md](./forms.md)
- 完整参考: [reference.md](./reference.md)
- 分析脚本: [scripts/analyze_singleton.py](./scripts/analyze_singleton.py)
