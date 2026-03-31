---
name: Bridge
description: "将抽象与实现分离，使二者可独立变化"
license: MIT
---

# Bridge Pattern (桥接模式)

## 核心概念

**Bridge** 是一种**结构型设计模式**，用于将抽象与实现分离，使它们可以独立变化。

### 关键原理
- 🔗 **分离关切** (Separation of Concerns) - 抽象与实现分开
- 📐 **维度分离** - 按不同维度定义类层级
- 🔄 **独立变化** - 抽象和实现都能独立扩展
- ✏️ **灵活组合** - 通过组合实现多维特性

### 对比继承
| 继承 | 桥接 |
|------|------|
| Shape → Circle, Square | Shape + Renderer的组合 |
| 类爆炸（M×N个类） | 只需M+N个类 |
| 静态结构 | 动态灵活 |
| 修改一维影响全部 | 维度独立变化 |

## 何时使用

1. **两个独立维度的变化** - Color × Shape、OS × Window、Device × Renderer
2. **避免类爆炸** - 用组合代替多重继承
3. **隐藏实现细节** - 客户端只见抽象
4. **运行时切换实现** - 动态决定使用哪个Implementor
5. **共享实现** - 多个Abstraction复用同一Implementor

## 基本结构

### UML类图

```
         Abstraction              Implementor
              △                       △
              │                       │
    ┌─────────┼─────────┐   ┌────────┴────────┐
    │         │         │   │                 │
RefinedAbstraction   ConcreteImplementorA  ConcreteImplementorB
```

## 实现方式

### 方法1: 虚方法模式

```java
// 实现接口
public interface Renderer {
    void renderCircle();
}

// 实现者
public class PyramidRenderer implements Renderer {
    @Override
    public void renderCircle() {
        System.out.println("  ^  ");
        System.out.println(" / \ ");
    }
}

// 抽象（包含对Implementor的引用）
public abstract class Shape {
    protected Renderer renderer;
    
    public Shape(Renderer renderer) {
        this.renderer = renderer;
    }
    
    public abstract void draw();
}

// 精化抽象
public class Circle extends Shape {
    @Override
    public void draw() {
        renderer.renderCircle();
    }
}

// 使用
Renderer r = new PyramidRenderer();
Shape s = new Circle(r);
s.draw();
```

### 方法2: 参数化桥接

```java
public abstract class AbstractShape {
    private Map<String, Renderer> renderers;
    
    public AbstractShape() {
        this.renderers = new HashMap<>();
        initializeRenderers();
    }
    
    protected abstract void initializeRenderers();
    
    public void drawWith(String renderType) {
        Renderer renderer = renderers.get(renderType);
        if (renderer != null) {
            performDraw(renderer);
        }
    }
    
    protected abstract void performDraw(Renderer r);
}
```

### 方法3: 配置驱动

```java
public class BridgeFactory {
    public static Shape create(String shapeType, String renderType) {
        Renderer renderer = createRenderer(renderType);
        return createShape(shapeType, renderer);
    }
    
    private static Renderer createRenderer(String type) {
        // 从配置或工厂创建Renderer
        return RendererFactory.create(type);
    }
    
    private static Shape createShape(String type, Renderer r) {
        switch (type) {
            case "circle": return new Circle(r);
            case "square": return new Square(r);
            default: throw new IllegalArgumentException(type);
        }
    }
}

// 使用
Shape shape = BridgeFactory.create("circle", "pyramid");
shape.draw();
```

## 完美使用场景

### 场景1: 跨平台UI - Window与OS适配

```java
// 抽象
public abstract class Window {
    protected OS os;
    public Window(OS os) { this.os = os; }
}

// 具体窗口
public class StandardWindow extends Window {
    public void render() {
        os.drawWindow("Standard");
    }
}

// 实现者
public interface OS {
    void drawWindow(String style);
}

// 具体平台
public class WindowsOS implements OS {
    public void drawWindow(String style) {
        System.out.println("Rendering on Windows: " + style);
    }
}

// 使用
OS os = getOS();  // 运行时决定
Window win = new StandardWindow(os);
win.render();  // 跨平台
```

### 场景2: 数据库访问 - 数据库方言

```java
public abstract class DataMapper {
    protected DatabaseDialect dialect;
}

public class UserMapper extends DataMapper {
    public List<User> findAll() {
        String sql = dialect.createSelectSQL("users");
        return dialect.execute(sql);
    }
}

// MySQL方言
public class MySQLDialect implements DatabaseDialect {
    @Override
    public String createSelectSQL(String table) {
        return "SELECT * FROM " + table + " LIMIT 100";
    }
}

// PostgreSQL方言
public class PostgreSQLDialect implements DatabaseDialect {
    @Override
    public String createSelectSQL(String table) {
        return "SELECT * FROM " + table + " OFFSET 0 LIMIT 100";
    }
}
```

### 场景3: 设备驱动 - 图形渲染

```java
public interface Renderer {
    void renderPixel(int x, int y, Color color);
    void drawLine(int x1, int y1, int x2, int y2);
}

public class GPURenderer implements Renderer {
    public void renderPixel(int x, int y, Color color) {
        // 调用GPU API
        cuda.setPixel(x, y, color);
    }
}

public abstract class Graphic {
    protected Renderer renderer;
    public abstract void draw();
}

public class Circle extends Graphic {
    private int radius;
    
    public void draw() {
        // 使用renderer接口，独立于GPU/CPU
        renderer.drawLine(...);
    }
}
```

### 场景4: 支付系统 - 支付方式与支付渠道

```java
// 抽象维度：支付方式
public interface PaymentMethod {
    double calculateFee(double amount);
    boolean validate(String info);
}

// 实现维度：支付渠道
public interface PaymentChannel {
    Receipt charge(double amount);
    Receipt refund(String receiptId);
}

// 具体支付方式
public class CreditCard implements PaymentMethod {
    public double calculateFee(double amount) {
        return amount * 0.02;  // 2%手续费
    }
}

// 具体支付渠道
public class AlipayChannel implements PaymentChannel {
    public Receipt charge(double amount) {
        // 调用Alipay API
        return alipayAPI.pay(amount);
    }
}

// 桥接：支付处理
public abstract class PaymentProcessor {
    protected PaymentMethod method;
    protected PaymentChannel channel;
    
    public Receipt processPayment(double amount) {
        double fee = method.calculateFee(amount);
        double total = amount + fee;
        return channel.charge(total);
    }
}
```

### 场景5: 日志系统 - 日志级别与输出目标

```java
public interface LogOutput {
    void write(String message);
    void flush();
}

public class FileLogOutput implements LogOutput {
    public void write(String message) {
        fileWriter.println(message);
    }
}

public abstract class Logger {
    protected LogOutput output;
    protected LogLevel level;
    
    protected void log(String message) {
        if (shouldLog()) {
            output.write(formatMessage(message));
        }
    }
    
    protected abstract String formatMessage(String message);
}

public class StructuredLogger extends Logger {
    protected String formatMessage(String message) {
        return String.format("[%s] %s", level, message);
    }
}
```

### 场景6: 消息队列 - 消息格式与传输协议

```java
// 传输协议(实现维度)
public interface Transport {
    void send(Message msg);
    Message receive();
    void connect(String brokerUrl);
}

// 消息格式(抽象维度)
public abstract class Message {
    protected Transport transport;
    abstract byte[] serialize();
}

// JSON消息
public class JSONMessage extends Message {
    byte[] serialize() {
        return gson.toJson(this).getBytes();
    }
}

// TCP传输
public class TCPTransport implements Transport {
    public void send(Message msg) {
        byte[] data = msg.serialize();
        socket.send(data);
    }
}

// AMQP传输
public class AMQPTransport implements Transport {
    public void send(Message msg) {
        channel.basicPublish(msg.serialize());
    }
}
```

### 场景7: 主题(Pattern，配置系统 - UI主题与渲染引擎

```java
// 实现维度：渲染引擎
public interface RenderEngine {
    void drawButton(Theme theme, String label);
    void drawWindow(Theme theme, String title);
}

// 抽象维度：UI主题
public abstract class UITheme {
    protected RenderEngine engine;
    
    abstract void applyColors();
    
    public void renderUI() {
        applyColors();
        engine.drawWindow(this, "Main");
        engine.drawButton(this, "OK");
    }
}

// 浅色主题
public class LightTheme extends UITheme {
    void applyColors() {
        backgroundColor = Color.WHITE;
        textColor = Color.BLACK;
    }
}

// SWT渲染
public class SWTEngine implements RenderEngine {
    public void drawButton(UITheme theme, String label) {
        button = new Button(shell, SWT.PUSH);
        button.setText(label);
        button.setBackground(theme.getBackgroundColor());
    }
}

// Swing渲染
public class SwingEngine implements RenderEngine {
    public void drawButton(UITheme theme, String label) {
        JButton btn = new JButton(label);
        btn.setBackground(theme.getBackgroundColor());
    }
}
```

### 场景8: 数据存储 - 数据格式与存储介质

```java
// 存储介质(实现维度)
public interface Storage {
    void save(byte[] data);
    byte[] load();
}

// 数据格式(抽象维度)
public abstract class DataStore {
    protected Storage storage;
    
    abstract byte[] encode();
    abstract Object decode(byte[] data);
    
    public void persist(Object obj) {
        byte[] encoded = encode(obj);
        storage.save(encoded);
    }
}

// CSV格式
public class CSVDataStore extends DataStore {
    byte[] encode(Object obj) {
        return CSV.serialize(obj);
    }
}

// 文件存储
public class FileStorage implements Storage {
    public void save(byte[] data) {
        FileOutputStream.write(data);
    }
}

// 云存储（AWS S3）
public class S3Storage implements Storage {
    public void save(byte[] data) {
        s3Client.putObject(bucketName, key, data);
    }
}
```

---

## "分离"与"独立变化"的核心理解

### 为什么要分离？(核心原理)

桥接模式的本质是**解决两个独立变化维度的类爆炸问题**。

```
❌ 不用桥接：继承树爆炸
Shape
├── Circle
│   ├── CircleRed        （Shape×Color的笛卡尔积）
│   ├── CircleGreen
│   └── CircleBlue
├── Square
│   ├── SquareRed
│   ├── SquareGreen
│   └── SquareBlue
└── Triangle
    ├── TriangleRed
    ├── TriangleGreen
    └── TriangleBlue
# 总计: 3 Shape × 3 Color = 9个类

✅ 用桥接：矩阵分离
Shape: Circle, Square, Triangle (3个)
Color: Red, Green, Blue (3个)
# 总计: 3 + 3 = 6个类
# 组合: 3 × 3 = 9种对象，但只需6个类
```

### 分离的两个维度必须满足什么条件？

1. **独立变化** - 一个维度变化不影响另一个
   ```
   ✓ Shape和Color独立 → 分离
   ✗ Button和ButtonListener不独立 → 不分离
   ```

2. **正交性** - 两个维度没有强依赖
   ```
   ✓ Window和OS是正交的
   ✗ ListNode和DoubleLinkedListNode不正交
   ```

3. **各自可配置** - 都需要运行时决策
   ```
   ✓ Shape(Circle/Square) + Color(Red/Green) 都需要选择
   ✗ Object和Class不需要同时选择 → 不用桥接
   ```

### 判断是否应该用桥接

```
是否有M×N的类爆炸? 
├─ 是 → 考虑桥接
└─ 否 → 继承足够

两个维度独立变化?
├─ 是 → 进一步优化用桥接
└─ 否 → 继承更好

都需要运行时选择?
├─ 是 → 使用桥接✅
└─ 否 → 考虑其他
```

---

## 深入的常见问题解决

### 问题1: 什么时候是"真正"的两个独立维度？

**症状**: 分不清什么是真独立，什么是虚独立

**分析工具 - 变化频率矩阵**:

```
维度组合         Shape变化频率    Renderer变化频率
─────────────────────────────────────────────────
Circle+GPU       每月1次          每周1次         ✅ 独立
Window+OS        每周1次          每月1次         ✅ 独立  
Employee+Role    几乎不变         每年1次         ⚠️ 伪独立
Button+Color     经常             很少            ⚠️ 非对称

判断：如果两个维度的变化频率差异>5倍，或一个几乎不变 → 虚独立 → 不用桥接
```

**错误示例**（伪独立）:
```java
// ❌ 不应该用桥接
public abstract class PaymentMethod {
    protected PaymentProcessor processor;  // 伪桥接
}
// 原因：PaymentMethod和Processor不独立
// Processor是PaymentMethod的依赖，不是平行维度
```

**正确示例**（真独立）:
```java
// ✅ 真正的桥接
public abstract class Logger {
    protected LogOutput output;  // 真桥接
}
// 原因：Logger(级别)和Output(目标)互不依赖，独立变化
```

### 问题2: 抽象与实现应该如何划分？

**规则**:
```
Abstraction: 
  → 高层业务逻辑
  → 稳定的部分
  → 不经常变化
  
Implementor:
  → 低层技术细节
  → 易变的部分
  → 经常替换
```

**判断标准 - 稳定性分析**:

```java
// 分析：哪个更稳定？
Logger logger = new Logger("FILE", LogLevel.DEBUG);  // 稳定
// vs
FileWriter fw = new FileWriter("/path/to/file.log");  // 易变

// Logger(抽象): 业务需要的日志级别 → 稳定
// FileWriter(实现): 具体输出目标 → 易变
// → Logger是Abstraction, FileWriter是Implementor ✅

// 反例：混淆了
public class Logger {
    protected Renderer renderer;  // 反了！
    // Logger实现细节，不是业务抽象
}
```

### 问题3: 如何动态切换Bridge的两端？

**场景**: 运行时需要改变Implementor（如切换数据库）

**方案1: Setter切换**（推荐简单场景）
```java
public class DataService {
    private DatabaseDialect dialect;
    
    public void setDialect(DatabaseDialect d) {
        this.dialect = d;
    }
    
    public List<User> getUsers() {
        return dialect.query("SELECT * FROM users");
    }
}

// 使用
DataService service = new DataService();
service.setDialect(new MySQLDialect());
service.getUsers();

// 切换
service.setDialect(new PostgreSQLDialect());
service.getUsers();  // 同一个service，不同backend
```

**方案2: 工厂切换**（推荐复杂场景）
```java
public class DialectFactory {
    private static Map<String, DatabaseDialect> dialects = new HashMap<>();
    
    static {
        dialects.put("mysql", new MySQLDialect());
        dialects.put("postgres", new PostgreSQLDialect());
        dialects.put("oracle", new OracleDialect());
    }
    
    public static DatabaseDialect getDialect(String dbType) {
        return dialects.get(dbType);
    }
}

// 使用：从配置读取
DatabaseDialect dialect = DialectFactory.getDialect(config.getDbType());
DataService service = new DataService(dialect);
```

**方案3: 策略切换**（推荐高频切换）
```java
public class AdaptiveService {
    private Map<String, DatabaseDialect> dialects;
    private DatabaseDialect current;
    
    public void executeWithBestDialect(Query q) {
        // 分析Query特征，选择最优Implementor
        DatabaseDialect best = selectBest(q);
        
        // 切换
        this.current = best;
        current.execute(q);
    }
    
    private DatabaseDialect selectBest(Query q) {
        if (q.isSimple()) return dialects.get("sqlite");
        if (q.isComplex()) return dialects.get("postgres");
        return dialects.get("mysql");
    }
}
```

### 问题4: 循环依赖问题

**症状**: Abstraction引用Implementor，Implementor又需要Abstraction

**反面示例**（循环）:
```java
// ❌ 循环依赖
public abstract class Shape {
    protected Renderer renderer;
    
    public void render() {
        renderer.render(this);  // Shape传给Renderer
    }
}

public interface Renderer {
    void render(Shape shape);  // Renderer依赖Shape
}
// 问题：Shape和Renderer相互依赖
```

**正确示例**（单向依赖）:
```java
// ✅ 单向依赖：Shape→Renderer
public abstract class Shape {
    protected Renderer renderer;
    
    public void render() {
        Color c = getColor();
        Size s = getSize();
        renderer.render(c, s);  // 只传递必要数据，不传Shape
    }
}

public interface Renderer {
    void render(Color color, Size size);  // 无需知道Shape
}
```

---

## 高级实现变体

### 变体1: 多维桥接（3个或更多维度）

```java
// 场景：同时有Shape、Color、Renderer三个维度
public abstract class Shape {
    protected ColorRenderer colorRenderer;
    protected GeometryRenderer geometryRenderer;
    
    public void render() {
        geometryRenderer.render(this);
        colorRenderer.render(this);
    }
}

// 或者用组合模式
public class MultiDimensionalBridge {
    private Map<String, Renderer> renderers = new HashMap<>();
    
    public void register(String dimension, Renderer renderer) {
        renderers.put(dimension, renderer);
    }
    
    public void render(Shape shape) {
        renderers.values().forEach(r -> r.render(shape));
    }
}
```

### 变体2: 动态代理桥接

```java
public class DynamicBridge {
    private Object implementor;
    private Class<?> implementorInterface;
    
    public DynamicBridge(Object impl, Class<?> iface) {
        this.implementor = impl;
        this.implementorInterface = iface;
    }
    
    public Object invoke(String methodName, Object... args) {
        return MethodHandle.from(implementor, methodName)
            .invokeWithArguments(args);
    }
}

// 使用
DynamicBridge bridge = new DynamicBridge(
    new MySQLDialect(),
    DatabaseDialect.class
);
bridge.invoke("query", sqlStatement);  // 动态调用
```

---

## 与其他模式的关系

| 模式 | 区别 | 何时结合 |
|--------|------|---------|
| Adapter | Adapter修补不兼容；Bridge分离设计 | 先用Bridge设计，Adapter处理遗留系统 |
| Strategy | Strategy处理算法选择；Bridge分离维度 | Bridge用于类层次，Strategy用于运行时选择 |
| Composite | Composite处理树结构；Bridge分离维度 | 多维树可同时用：Bridge分离Color，Composite管理父子 |
| Factory | Factory创建对象；Bridge分离实现 | 结合使用：BridgeFactory创建合适的Abstraction-Implementor对 |
| Decorator | Decorator逐层增强；Bridge分离实现 | 可结合：Decorator在Abstraction层做装饰 |

---

## 最佳实践

1. ✅ **明确界定两个独立维度** - 使用变化频率、依赖关系分析
2. ✅ **Implementor用接口而非抽象类** - 更轻量、更灵活
3. ✅ **Abstract层稳定，Implementor层易变** - 符合稳定依赖原则
4. ✅ **避免过度桥接** - 单维变化用简单继承就够
5. ✅ **文档化维度含义** - 明确说明为什么分离

## 何时避免使用

- ❌ 只有一个维度变化 - 简单继承足够
- ❌ 两个维度几乎不变化 - 过度设计
- ❌ 类数量少(< 6)，不会爆炸 - 继承足够清晰
- ❌ 时间紧张 - Bridge增加代码复杂度
