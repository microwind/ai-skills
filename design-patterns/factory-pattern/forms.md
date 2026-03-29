# Factory 模式 - 诊断与规划表

## 第1步: 需求诊断 - 你真的需要工厂吗？

### 🔍 快速检查清单

```
□ 系统需要支持多种相关的产品/实现
□ 产品类型不固定，可能在运行时动态改变
□ 不同产品类型的创建逻辑存在明显差异
□ 客户端代码不应该依赖具体的产品实现类
□ 创建逻辑复杂到不适合写在客户端代码中
□ 系统预期将来会增加新的产品类型
```

**诊断标准**:
- ✅ 勾选 5 项以上 → **强烈推荐使用工厂**
- ⚠️ 勾选 3-4 项 → **可以使用工厂**
- ❌ 勾选 2 项以下 → **可能过度设计，简单创建即可**

### 🎯 具体场景评估矩阵

| 场景 | 产品数 | 创建复杂度 | 扩展频率 | 推荐方案 | 优先级 |
|------|--------|----------|---------|---------|--------|
| 数据库连接 | 5+ | 高 | 频繁 | 参数化工厂 + 注册表 | ⭐⭐⭐⭐⭐ |
| 日志系统 | 3-4 | 中 | 偶尔 | 工厂方法 | ⭐⭐⭐⭐ |
| 支付渠道 | 4+ | 高 | 常见 | 参数化工厂 | ⭐⭐⭐⭐⭐ |
| UI框架 | 2-3 | 中 | 不频繁 | 简单工厂 | ⭐⭐⭐ |
| 消息队列 | 4-6 | 中 | 常见 | 工厂方法 + 配置 | ⭐⭐⭐⭐ |
| 文档处理 | 3-5 | 中 | 偶尔 | 工厂方法 | ⭐⭐⭐⭐ |

---

## 第2步: 工厂类型选择 - 5x5 对比矩阵

### 选择决策树

```
开始 → 产品类型数量?
   ├─ 1-2个 (如果稳定) → 直接创建，无需工厂
   ├─ 2-3个 (稳定) → 简单工厂 ✓
   └─ 3个+ 或 需扩展?
       ├─ 各产品创建逻辑完全不同? 
       │   └─ YES → 工厂方法 ✓
       ├─ 需要一次创建一族相关产品?
       │   └─ YES → 抽象工厂 ✓
       └─ 类型在配置文件中动态指定?
           └─ YES → 参数化工厂 ✓
```

### 详细对比表

| 指标 | 简单工厂 | 工厂方法 | 抽象工厂 | 参数化工厂 |
|------|---------|---------|---------|-----------|
| **代码复杂度** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **类文件数** | 1-2 | 5-8 | 8-12 | 1-2 |
| **类型安全** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **扩展性** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **学习成本** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **维护成本** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **适合新增类型** | ❌ | ✅ | ✅ | ✅✅ |
| **产品族关联性** | N/A | N/A | ✅✅ | N/A |
| **配置文件驱动** | ❌ | ❌ | ❌ | ✅ |

### 选择建议

#### ✅ 选择「简单工厂」If:
```
□ 产品类型 ≤ 3 个且稳定
□ 创建逻辑简单（<100 行）
□ 6 个月内不会增加新产品
□ 整个系统代码量 < 10K LOC
□ 团队人数 ≤ 5 人
```

#### ✅ 选择「工厂方法」If:
```
□ 产品类型 3-6 个
□ 产品创建逻辑各不相同
□ 将来可能增加新产品
□ 需要严格遵循开闭原则
□ 产品之间关联性不强
```

#### ✅ 选择「抽象工厂」If:
```
□ 需要创建「一族」相关的产品
□ 不同产品族之间要能整体切换
□ 产品之间有强依赖关系
□ 示例：UI(Button+TextField+Window)+Platform(Windows/Mac/Linux)
```

#### ✅ 选择「参数化工厂」If:
```
□ 产品类型由配置文件指定
□ 新产品类型无需修改代码
□ 支持插件化架构
□ 需要零修改扩展
□ 示例：Database(MySQL/PostgreSQL/MongoDB/SQLite)
```

---

## 第3步: 实现规划 - 5个关键步骤

### ✏️ 步骤1: 产品接口设计

```
□ 定义产品接口/抽象类
□ 产品应该有哪些主要操作？列出 3-5 个
□ 是否需要初始化方法 (init/setup)?
□ 是否需要清理方法 (close/cleanup)?
□ 产品间是否需要比较 (equals/hashCode)?

示例：
Logger 接口的主要方法：
  ✓ log(String message)
  ✓ close()
  ✓ setLevel(LogLevel level)
  ✓ isEnabled(LogLevel level)
```

### ✏️ 步骤2: 具体产品实现

```
□ 列出需要支持的产品类型：_________________
   1. _________________ (当前必需)
   2. _________________ (当前必需)
   3. _________________ (将来可能)
   4. _________________ (将来可能)

□ 每个产品类型的初始化参数是什么？
   类型1: _______________
   类型2: _______________

□ 产品创建成本高吗？ (CPU/内存/IO)
   是 → 考虑缓存或对象池
   否 → 每次创建新实例
```

### ✏️ 步骤3: 工厂类结构设计

#### IF 使用简单工厂:
```
□ 工厂类名: LoggerFactory_______________
□ 工厂方法签名: 
   public static Logger create(String type)
□ 支持的类型参数：FILE, CONSOLE, DATABASE, ...
□ 创建失败时的处理：异常 / 返回默认值 / 返回 null
```

#### IF 使用工厂方法:
```
□ 抽象工厂类名: LoggerFactory_______________
□ 工厂方法名: createLogger()_______________
□ 具体工厂类数: 需要 ___ 个
   1. FileLoggerFactory (负责创建 FileLogger)
   2. ConsoleLoggerFactory (负责创建 ConsoleLogger)
   3. ...

□ 工厂继承关系：
   LoggerFactory (abstract)
      ├── FileLoggerFactory
      ├── ConsoleLoggerFactory
      └── ...
```

#### IF 使用抽象工厂:
```
□ 抽象工厂接口名: UIFactory_______________
□ 产品族包括：
   □ Button, TextField, Window (UI 元素)
   □ 产品族1: _______________
   □ 产品族2: _______________

□ 具体工厂实现：
   □ WindowsUIFactory (创建 Windows 风格的 UI)
   □ MacUIFactory (创建 Mac 风格的 UI)
   □ ...

□ 工厂选择策略：
   根据 _____ (平台/配置/参数) 选择工厂
```

#### IF 使用参数化工厂:
```
□ 工厂类名: LoggerFactory_______________
□ 注册机制：Map<String, Supplier<Logger>>___
□ 默认注册的类型：FILE, CONSOLE, DATABASE, ...
□ 支持动态注册：YES / NO
□ 类型查询是否区分大小写：_______________
```

### ✏️ 步骤4: 创建参数与配置

```
□ 产品创建需要的参数：
   必需:
     - _________________ (类型必须指定)
     - _________________ (每次创建必须指定)
   
   可选:
     - _________________ (有默认值)
     - _________________ (有默认值)

□ 配置来源：
   □ 硬编码常量
   □ 系统属性 (System.getProperty)
   □ 环境变量 (System.getenv)
   □ 配置文件 (properties/yaml/json)
   □ 数据库
   □ 注册中心 (Spring, Guice, etc)

□ 参数过多时的处理：
   □ 使用 Builder 模式: LoggerConfig.builder()...
   □ 使用配置对象: new LoggerConfig(...)
   □ 使用 Map 传参: create(params)
```

### ✏️ 步骤5: 错误处理与回退

```
□ 工厂创建失败时的处理：
   □ 抛异常 (立即失败)
   □ 返回默认实现 (Console logger)
   □ 返回 Optional<Logger> (让调用者处理)
   □ 返回 LoggerCreationResult (包含成功/失败信息)

□ 创建失败的原因预测：
   - _________________ (如何处理?)
   - _________________ (如何处理?)
   - _________________ (如何处理?)

□ 降级策略：
   Primary:    _______________
   Fallback 1: _______________
   Fallback 2: _______________
   Final:      _______________
```

---

## 第4步: 测试计划 - 5个测试维度

### 📋 测试清单

#### 单元测试
```java
□ 测试所有产品类型都能正确创建
   - testCreateFileLogger()
   - testCreateConsoleLogger()
   - testCreateDatabaseLogger()
   
□ 测试返回的对象是否真的可用
   - testCreatedLoggerCanLog()
   - testLoggerPropertiesCorrect()
   
□ 测试无效类型处理
   - testInvalidTypeThrowsException()
   - testNullTypeHandling()
   
□ 测试参数传递
   - testLoggerCreatedWithCorrectParams()
```

#### 集成测试
```java
□ 工厂与产品的集成
   - testFactoryAndProductWorkTogether()
   - testMultipleInstancesIndependent()
   
□ 工厂与配置系统集成
   - testFactoryReadFromConfig()
   - testReloadConfigAndCreateNewProduct()
```

#### 性能测试
```
□ 单次创建性能
   - 期望: < 1ms (简单工厂)
   - 期望: < 5ms (工厂方法)
   - 期望: < 10ms (抽象工厂)
   
□ 大量创建性能 (如果支持对象池)
   - testCreating1000Instances()
   - testPoolReuseRate()
```

#### 并发测试
```
□ 多线程创建是否线程安全
   - testMultiThreadCreation()
   - testConcurrentPoolAccess()
```

#### 扩展性测试
```
□ 添加新产品类型后是否需要修改现有代码
   - YES → 违反开闭原则
   - NO → 设计良好
```

---

## 第5步: 代码审查指南

### 🔍 工厂模式代码审查清单

#### 设计审查
```
□ 产品接口设计是否合理？
   问题：产品接口是否太宽泛或太窄？
   
□ 工厂返回的是接口而非具体类？
   错误： return new FileLogger();
   正确： return (Logger) new FileLogger();
   
□ 工厂是否隐藏了创建的复杂性？
   应该隐藏：产品参数、初始化逻辑、依赖注入
   
□ 是否遵循了开闭原则？
   添加新产品是否需要修改现有工厂代码？
```

#### 实现审查
```
□ 工厂方法签名清晰吗？
   create(String type) - 清晰
   getLogger() - 太模糊
   
□ 参数验证是否完整？
   - null 检查
   - 范围检查
   - 依赖检查
   
□ 异常处理是否恰当？
   - 什么时候应该抛异常？
   - 什么时候应该返回默认值？
   
□ 是否支持工厂本身的扩展？
   - 简单工厂：后期难以扩展(✗)
   - 工厂方法：可通过子类扩展(✓)
```

#### 文档审查
```
□ 工厂的文档是否清晰？
   - 支持哪些产品类型？
   - 创建参数是什么？
   - 可能的异常有哪些？
   
□ 产品类型是否有枚举而非魔法字符串？
   错误： factory.create("FILE")
   正确： factory.create(LoggerType.FILE)
   
□ 是否有创建示例代码？
```

#### 维护性审查
```
□ 添加新产品类型有多难？
   简单工厂：需要修改 switch 语句(✗ 高风险)
   工厂方法：新增一个工厂类(✓ 低风险)
   
□ 将来是否容易支持配置文件驱动？
   现在就考虑升级路径
```

---

## 第6步: 常见陷阱预防

### ⚠️ 陷阱1: 工厂知道太多东西（God Object）

```java
// ❌ 反面：工厂承担过多责任
public class LoggerFactory {
    public static Logger create(String type) {
        Logger logger = null;
        
        // 创建逻辑
        if ("FILE".equals(type)) {
            logger = new FileLogger();
        }
        
        // 配置逻辑 (不应该在工厂)
        logger.setPath("/var/log/app.log");
        
        // 监控逻辑 (不应该在工厂)
        metricService.recordCreation("logger");
        
        // 依赖注入 (不应该在工厂)
        logger.setConfig(getConfig());
        
        return logger;
    }
}

// ✅ 改进：职责清晰
public class LoggerFactory {
    private static final LoggerConfiguration CONFIG = new LoggerConfiguration();
    
    // 工厂只负责创建
    public static Logger create(String type) {
        switch(type) {
            case "FILE": return new FileLogger();
            case "CONSOLE": return new ConsoleLogger();
            default: throw new IllegalArgumentException("Unknown type: " + type);
        }
    }
}

// 配置由单独的类负责
public class LoggerConfiguration {
    public void configure(Logger logger) {
        logger.setPath("/var/log/app.log");
    }
}
```

### ⚠️ 陷阱2: 忘记文档化产品类型

```java
// ❌ 缺乏文档
public static Logger create(String type) {
    // ... 
}

// ✅ 完整文档
/**
 * 创建 Logger 实例
 * 
 * @param type 日志类型，支持的值：
 *             - "FILE": 文件日志，需配置 log.file.path
 *             - "CONSOLE": 控制台日志
 *             - "DATABASE": 数据库日志，需配置数据源
 *             - "REMOTE": 远程日志，需配置远程服务器地址
 * 
 * @return 相应类型的 Logger 实例
 * @throws IllegalArgumentException 如果 type 不支持
 * 
 * @example
 * Logger logger = LoggerFactory.create("FILE");
 * logger.log("Hello");
 */
public static Logger create(String type) {
    // ...
}
```

### ⚠️ 陷阱3: 工厂返回具体类而非接口

```java
// ❌ 返回具体类，降低灵活性
public static FileLogger create() {
    return new FileLogger();
}

// ✅ 返回接口
public static Logger create(String type) {
    return createInternal(type);  // 返回 Logger 接口
}
```

### ⚠️ 陷阱4: 产品类型使用魔法字符串

```java
// ❌ 容易输入错误
factory.create("FLIE");  // 打错字，无法编译时捕获

// ✅ 使用枚举
public enum LoggerType {
    FILE("FILE"),
    CONSOLE("CONSOLE"),
    DATABASE("DATABASE");
    
    private final String value;
    LoggerType(String value) { this.value = value; }
}

Logger logger = factory.create(LoggerType.FILE);
```

### ⚠️ 陷阱5: 不考虑创建失败的情况

```java
// ❌ 可能出现 NullPointerException
Logger logger = factory.create(type);
logger.log("message");  // NPE if factory returns null

// ✅ 明确的失败处理
Logger logger = factory.create(type);
if (logger == null) {
    logger = new ConsoleLogger();  // 降级到默认实现
}
logger.log("message");

// 或使用 Optional
Optional<Logger> logger = factory.createOptional(type);
Logger finalLogger = logger.orElseGet(ConsoleLogger::new);
```

---

## 快速参考

### 工厂模式决策流程图

```
需要创建多个相关对象吗?
  ├─ NO → 直接 new，无需工厂
  └─ YES → 产品数量?
      ├─ 1-2 个 → 简单工厂 (60% 场景)
      ├─ 3-5 个 → 工厂方法 (30% 场景)
      ├─ 多个相关族 → 抽象工厂 (5% 场景)
      └─ 配置驱动 → 参数化工厂 (5% 场景)
```

### 快速启动模板

最小可用实现 (工厂方法，基础场景):
```java
// 1. 产品接口
interface Logger { void log(String msg); }

// 2. 产品实现
class FileLogger implements Logger { /* ... */ }

// 3. 工厂接口
abstract class LoggerFactory {
    abstract Logger createLogger();
}

// 4. 工厂实现
class FileLoggerFactory extends LoggerFactory {
    @Override Logger createLogger() { return new FileLogger(); }
}

// 5. 使用
LoggerFactory factory = new FileLoggerFactory();
Logger logger = factory.createLogger();
logger.log("Hello");
```


