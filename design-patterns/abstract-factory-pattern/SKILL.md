---
name: 抽象工厂模式
description: "为一族相关对象的创建提供一致的接口，无需指定其具体类。"
license: MIT
---

# 抽象工厂模式 (Abstract Factory Pattern)

## 核心概念

**Abstract Factory**是一种**创建型设计模式**，用于创建**一族相关对象的集合**，而不是单个对象。它在工厂方法之上进行了抽象，提供接口定义一系列产品族的创建。

**核心原则**:
- 隐藏产品族的创建复杂性
- 保证产品族的一致性
- 支持产品族的灵活切换
- 将产品族的创建逻辑集中管理

**关键术语**:
- **产品族** (Product Family) - 相关产品的集合（如 Windows UI族包含Button、Window、TextBox）
- **抽象工厂** (Abstract Factory) - 定义创建产品族接口
- **具体工厂** (Concrete Factory) - 实现具体产品族创建

---

## 何时使用 - 触发模式

**始终使用**:
- 系统需要支持多个相关对象的集合（产品族）
- 需要在多个产品族之间灵活切换
- 希望保证一个产品族内产品的一致性
- 产品族的创建逻辑复杂/分散在多处

**触发短语**:
- "如何创建一组相关/相通的对象？"
- "需要支持多个主题/风格/变体，且每个涉及多个对象"
- "如何保证选定的产品都来自同一个族？"
- "产品族涉及多个维度的变化"

**典型场景**:
| 场景 | 产品族 | 工厂 |
|------|--------|------|
| UI 组件系统 | {Windows Button, Window, Dialog} vs {Mac Button, Window, Dialog} | WindowsUIFactory vs MacUIFactory |
| 数据库方言 | {MySQL SQL, Optimizer, Connection} vs {PostgreSQL ...} | MySQLDialectFactory vs PostgresDialectFactory |
| 游戏渲染引擎 | {DirectX Texture, Shader, Buffer} vs {OpenGL ...} | DirectXFactory vs OpenGLFactory |
| 操作系统适配 | {Windows FileSystem, Registry, Process} vs {Linux ...} | WindowsAdapterFactory vs LinuxAdapterFactory |

---

## 4个实现方法详解

### 方法1: 简单抽象工厂 (Simple Abstract Factory)

最直接的实现方式 - 为产品族定义接口，具体工厂实现。

```java
// 产品接口
public interface Button {
    void render();
    void click();
}

public interface TextField {
    void render();
    void setText(String text);
}

// 产品实现 - Windows 族
public class WindowsButton implements Button {
    @Override
    public void render() { System.out.println("🪟 Rendering Windows Button"); }
    
    @Override
    public void click() { System.out.println("Windows Button clicked"); }
}

public class WindowsTextField implements TextField {
    @Override
    public void render() { System.out.println("🪟 Rendering Windows TextField"); }
    
    @Override
    public void setText(String text) { System.out.println("Windows TextField: " + text); }
}

// 产品实现 - Mac 族
public class MacButton implements Button {
    @Override
    public void render() { System.out.println("🍎 Rendering Mac Button"); }
    
    @Override
    public void click() { System.out.println("Mac Button clicked"); }
}

public class MacTextField implements TextField {
    @Override
    public void render() { System.out.println("🍎 Rendering Mac TextField"); }
    
    @Override
    public void setText(String text) { System.out.println("Mac TextField: " + text); }
}

// 抽象工厂
public interface UIFactory {
    Button createButton();
    TextField createTextField();
}

// 具体工厂 - Windows
public class WindowsUIFactory implements UIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }
    
    @Override
    public TextField createTextField() {
        return new WindowsTextField();
    }
}

// 具体工厂 - Mac
public class MacUIFactory implements UIFactory {
    @Override
    public Button createButton() {
        return new MacButton();
    }
    
    @Override
    public TextField createTextField() {
        return new MacTextField();
    }
}

// 使用
public class Application {
    private UIFactory factory;
    
    public Application(UIFactory factory) {
        this.factory = factory;
    }
    
    public void renderUI() {
        Button button = factory.createButton();
        TextField textField = factory.createTextField();
        
        button.render();
        textField.render();
    }
    
    public static void main(String[] args) {
        // 根据配置选择工厂
        String os = System.getProperty("os.name");
        UIFactory factory = os.contains("Windows") 
            ? new WindowsUIFactory()
            : new MacUIFactory();
        
        Application app = new Application(factory);
        app.renderUI();
    }
}
```

**优点**: 结构清晰，易于理解和维护
**缺点**: 添加新产品族需要创建多个新类

---

### 方法2: 配置驱动型工厂 (Configuration-Driven Factory)

使用配置或反射动态决定使用哪个产品族，减少硬编码。

```java
public class ConfigurableUIFactory implements UIFactory {
    private String platform;
    private Map<String, Class<?>> productRegistry;
    
    public ConfigurableUIFactory(String platform) {
        this.platform = platform;
        this.productRegistry = new HashMap<>();
        loadConfiguration(platform);
    }
    
    private void loadConfiguration(String platform) {
        // 从配置文件加载
        if ("WINDOWS".equalsIgnoreCase(platform)) {
            productRegistry.put("Button", WindowsButton.class);
            productRegistry.put("TextField", WindowsTextField.class);
        } else if ("MAC".equalsIgnoreCase(platform)) {
            productRegistry.put("Button", MacButton.class);
            productRegistry.put("TextField", MacTextField.class);
        }
    }
    
    @Override
    public Button createButton() {
        try {
            Class<?> clazz = productRegistry.get("Button");
            return (Button) clazz.getDeclaredConstructor().newInstance();
        } catch (Exception e) {
            throw new RuntimeException("Failed to create Button", e);
        }
    }
    
    @Override
    public TextField createTextField() {
        try {
            Class<?> clazz = productRegistry.get("TextField");
            return (TextField) clazz.getDeclaredConstructor().newInstance();
        } catch (Exception e) {
            throw new RuntimeException("Failed to create TextField", e);
        }
    }
}
```

**优点**: 通过配置切换产品族，无需重新编译
**缺点**: 运行时反射开销，异常处理复杂

---

### 方法3: 单例结合的工厂 (Singleton-Combined Factory)

确保每个产品族的工厂只有一个实例（资源共享）。

```java
public class SingletonUIFactory {
    private static final Map<String, UIFactory> instances = new HashMap<>();
    
    static {
        instances.put("WINDOWS", new WindowsUIFactory());
        instances.put("MAC", new MacUIFactory());
    }
    
    private SingletonUIFactory() {}
    
    public static UIFactory getInstance(String platform) {
        UIFactory factory = instances.get(platform);
        if (factory == null) {
            throw new IllegalArgumentException("Unknown platform: " + platform);
        }
        return factory;
    }
    
    // 获取当前系统的工厂
    public static UIFactory getCurrentFactory() {
        String os = System.getProperty("os.name");
        return getInstance(os.contains("Windows") ? "WINDOWS" : "MAC");
    }
}

// 使用
UIFactory factory = SingletonUIFactory.getCurrentFactory();
```

**优点**: 资源共享，单一全局访问点
**缺点**: 全局性可能导致测试困难

---

### 方法4: 动态注册工厂 (Dynamic Registry Factory)

允许在运行时注册和注销产品族，支持插件化架构。

```java
public class PluggableUIFactory implements UIFactory {
    private static final Map<String, UIFactory> registry = new ConcurrentHashMap<>();
    private String platformId;
    
    // 动态注册工厂
    public static void register(String platformId, UIFactory factory) {
        registry.put(platformId, factory);
        System.out.println("Registered factory for: " + platformId);
    }
    
    // 动态注销工厂
    public static void unregister(String platformId) {
        registry.remove(platformId);
        System.out.println("Unregistered factory for: " + platformId);
    }
    
    public PluggableUIFactory(String platformId) {
        if (!registry.containsKey(platformId)) {
            throw new IllegalArgumentException("No factory registered for: " + platformId);
        }
        this.platformId = platformId;
    }
    
    @Override
    public Button createButton() {
        return registry.get(platformId).createButton();
    }
    
    @Override
    public TextField createTextField() {
        return registry.get(platformId).createTextField();
    }
}

// 使用
public class Main {
    public static void main(String[] args) {
        // 在运行时注册工厂
        PluggableUIFactory.register("WINDOWS", new WindowsUIFactory());
        PluggableUIFactory.register("MAC", new MacUIFactory());
        
        // 使用注册的工厂
        UIFactory factory = new PluggableUIFactory("WINDOWS");
        Button button = factory.createButton();
        button.render();
        
        // 动态添加新的产品族
        PluggableUIFactory.register("LINUX", new LinuxUIFactory());
    }
}
```

**优点**: 高度灵活，支持运行时插件
**缺点**: 复杂度高，需要仔细管理注册表

---

## 常见问题与解决方案

### ❌ 问题1: 产品族的管理和扩展

**症状**: 添加新的产品族时，需要修改多个地方；添加新的产品类型时，需要修改所有工厂类。

**根本原因**: 产品族边界不清晰，扩展点不明确。

**解决方案**:

```java
// ✅ 改进：使用Builder模式来管理产品族的复杂构建
public class UIFactoryBuilder {
    private Map<String, Class<?>> buttonImpls = new HashMap<>();
    private Map<String, Class<?>> textFieldImpls = new HashMap<>();
    
    public UIFactoryBuilder registerButton(String platform, Class<?> impl) {
        buttonImpls.put(platform, impl);
        return this;
    }
    
    public UIFactoryBuilder registerTextField(String platform, Class<?> impl) {
        textFieldImpls.put(platform, impl);
        return this;
    }
    
    public UIFactory build(String platform) {
        return new ConfigurableUIFactory(platform, buttonImpls, textFieldImpls);
    }
}

// 使用
UIFactory factory = new UIFactoryBuilder()
    .registerButton("WINDOWS", WindowsButton.class)
    .registerTextField("WINDOWS", WindowsTextField.class)
    .build("WINDOWS");
```

---

### ❌ 问题2: 产品族一致性保证

**症状**: 某个工厂返回的产品来自不同的族（混杂），导致风格不一致。

**根本原因**: 工厂实现不规范，产品隔离不足。

**解决方案**:

```java
// ✅ 使用版本控制和验证确保一致性
public abstract class BaseUIFactory implements UIFactory {
    protected String version;
    
    public BaseUIFactory(String version) {
        this.version = version;
    }
    
    // 验证产品一致性
    protected final void validateConsistency(Button button, TextField textField) {
        if (!button.getVersion().equals(textField.getVersion())) {
            throw new IllegalStateException(
                "Inconsistent product family: " + 
                button.getVersion() + " vs " + textField.getVersion()
            );
        }
    }
}

public class ConsistentWindowsUIFactory extends BaseUIFactory {
    public ConsistentWindowsUIFactory() {
        super("1.0");
    }
    
    @Override
    public Button createButton() {
        return new VersionedWindowsButton("1.0");
    }
    
    @Override
    public TextField createTextField() {
        return new VersionedWindowsTextField("1.0");
    }
}
```

---

### ❌ 问题3: 产品族扩展成本

**症状**: 添加新的产品类型时，需要修改所有工厂类；代码改动范围大，容易引入Bug。

**根本原因**: 产品族的接口设计不够灵活。

**解决方案**:

```java
// ✅ 使用组合和装饰器扩展产品族
public interface UIProduct {
    String getType();
    void render();
}

public class ProductFactory {
    private UIFactory delegate;
    private List<ProductDecorator> decorators;
    
    public ProductFactory(UIFactory delegate) {
        this.delegate = delegate;
        this.decorators = new ArrayList<>();
    }
    
    public ProductFactory addDecorator(ProductDecorator decorator) {
        decorators.add(decorator);
        return this;
    }
    
    public Button createButton() {
        Button button = delegate.createButton();
        for (ProductDecorator decorator : decorators) {
            button = decorator.decorate(button);
        }
        return button;
    }
}

// 新增产品类型无需修改工厂
public interface ProductDecorator {
    Button decorate(Button button);
}

public class TooltipDecorator implements ProductDecorator {
    @Override
    public Button decorate(Button button) {
        return new TooltipButton(button);
    }
}
```

---

### ❌ 问题4: 产品序列化和反序列化

**症状**: 需要保存和恢复产品状态，但工厂创建的对象难以序列化。

**根本原因**: 序列化信息不完整或工厂引用无法恢复。

**解决方案**:

```java
// ✅ 实现序列化工厂
public class SerializableUIFactory implements UIFactory, Serializable {
    private String platformId;
    
    public SerializableUIFactory(String platformId) {
        this.platformId = platformId;
    }
    
    @Override
    public Button createButton() {
        Button button = getPlatformFactory().createButton();
        return new SerializableButton(button, platformId);
    }
    
    @Override
    public TextField createTextField() {
        TextField field = getPlatformFactory().createTextField();
        return new SerializableTextField(field, platformId);
    }
    
    private UIFactory getPlatformFactory() {
        if ("WINDOWS".equals(platformId)) {
            return new WindowsUIFactory();
        }
        return new MacUIFactory();
    }
}

public class SerializableButton implements Button, Serializable {
    private Button delegate;
    private String platformId;
    
    // 序列化后可通过工厂恢复
    private void readObject(java.io.ObjectInputStream in) 
            throws IOException, ClassNotFoundException {
        in.defaultReadObject();
        this.delegate = SerializableUIFactory.getInstance(platformId).createButton();
    }
}
```

---

## 与其他模式的关系

| 模式 | 关系 | 使用场景差异 |
|------|------|-----------|
| **工厂方法** | Abstract Factory 通常使用工厂方法创建产品 | 工厂方法：单个产品；Abstract Factory：产品族 |
| **单例** | 常结合使用，确保工厂唯一性 | 需要全局一致性时组合使用 |
| **生成器** | 可用于复杂产品族的创建 | 产品族构建复杂时结合使用 |
| **适配器** | 用于兼容旧系统的产品族 | 需要与既有系统集成时使用 |
| **装饰器** | 可用于扩展产品族功能 | 需要动态添加产品功能时组合使用 |

---

## 最佳实践

✅ **清晰的产品族定义** - 明确界定哪些产品属于一个族  
✅ **版本管理** - 为产品族版本化，避免混杂  
✅ **配置化** - 优先使用配置而非硬编码决定工厂选择  
✅ **一致性保证** - 在工厂中验证产品一致性  
✅ **扩展点清晰** - 明确新产品类型的添加流程  
✅ **避免过度设计** - 产品族较少时不必使用  

---

## 何时避免使用

❌ 系统只有单个产品（使用工厂方法）  
❌ 产品家族变化频繁且无规律（可能设计不当）  
❌ 产品间没有明显关联（可能不算一个族）  
❌ 过度预测未来需求（导致过度设计）  

---

## 真实使用场景

### 场景1: 数据库方言工厂

```java
public interface SQLDialect {
    String getDateFormatFunction();
    String getPageClause(long offset, long limit);
    String getCountQuery(String sql);
}

public class MySQLDialect implements SQLDialect {
    @Override
    public String getDateFormatFunction() { return "DATE_FORMAT"; }
    
    @Override
    public String getPageClause(long offset, long limit) {
        return "LIMIT " + offset + ", " + limit;
    }
    
    @Override
    public String getCountQuery(String sql) {
        return "SELECT COUNT(*) FROM (" + sql + ")";
    }
}

public class PostgresDialect implements SQLDialect {
    @Override
    public String getDateFormatFunction() { return "TO_CHAR"; }
    
    @Override
    public String getPageClause(long offset, long limit) {
        return "OFFSET " + offset + " LIMIT " + limit;
    }
    
    @Override
    public String getCountQuery(String sql) {
        return "SELECT COUNT(*) FROM (" + sql + ") AS t";
    }
}

// 应用：ORM框架根据数据库类型选择方言
public class QueryBuilder {
    private SQLDialect dialect;
    
    public QueryBuilder(String dbType) {
        this.dialect = DialectFactory.getDialect(dbType);
    }
    
    public String buildQuery(String sql, long offset, long limit) {
        return sql + " " + dialect.getPageClause(offset, limit);
    }
}
```

### 场景2: 游戏渲染引擎工厂

跨平台游戏引擎通常需要支持不同的渲染API（DirectX、OpenGL、Metal）。抽象工厂确保图片、着色器、缓冲区成套来自同一个渲染后端。

### 场景3: 云服务商适配工厂

多云架构中使用抽象工厂为不同云服务商（AWS、Azure、GCP）提供统一接口。每个工厂创建该云商的全套服务（存储、计算、网络）。
