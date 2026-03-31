---
name: 模板方法模式
description: "在基类中定义算法骨架，由子类实现具体步骤。"
license: MIT
---

# 模板方法模式 (Template Method Pattern)

## 核心概念

**Template Method**是**行为型设计模式**，在基类中定义算法的骨架，将某些步骤延迟到子类实现。这样可以重用算法结构，让子类改变算法中的特定步骤。

**核心原则**: 算法不变部分与可变部分分离、好莱坞原则(不要调用我们，我们调用你)

---

## 何时使用

**始终使用**:
- 算法有不变的部分和可变的部分
- 多个子类有相似的算法结构  
- 希望避免代码重复
- 需要控制子类的扩展点

**触发短语**: "算法框架相同但细节不同?" "如何规范子类实现程序?"

**典型场景**:
| 模板 | 不变部分 | 可变部分 | 
|------|----------|----------|
| 排序 | 排序框架 | 比较逻辑 |
| 数据处理 | 读-处理-写 | 处理逻辑 |
| HTTP请求 | 请求框架 | 参数构建 |
| 数据库迁移 | 迁移框架 | 数据转换 |

---

##4个实现方法

### 方法1: 虚方法式

基类定义模板，子类实现虚方法。

```java
public abstract class DataProcessor {
    // 模板方法 - 定义算法骨架
    public final void process(String data) {
        String cleaned = preprocess(data);
        String result = transform(cleaned);
        save(result);
    }
    
    // 虚方法 - 由子类实现
    protected abstract String preprocess(String data);
    protected abstract String transform(String data);
    protected abstract void save(String data);
}

public class CSVProcessor extends DataProcessor {
    @Override
    protected String preprocess(String data) { return data.trim(); }
    
    @Override
    protected String transform(String data) { return data.toUpperCase(); }
    
    @Override
    protected void save(String data) { 
        System.out.println("Save to CSV: " + data); 
    }
}
```

### 方法2: 回调式

通过回调函数实现可变部分。

```java
public class Algorithm {
    private Callback callback;
    
    public Algorithm(Callback cb) { this.callback = cb; }
    
    public void execute(String input) {
        System.out.println("Step 1: Init");
        String result = callback.process(input);
        System.out.println("Step 3: Finalize");
    }
    
    @FunctionalInterface
    public interface Callback {
        String process(String input);
    }
}

// 使用
Algorithm algo = new Algorithm(input -> input.toUpperCase());
algo.execute("hello");
```

### 方法3: 策略改进式

使用策略模式替代虚方法。

```java
public class ProcessorWithStrategy {
    private Strategy strategy;
    
    public ProcessorWithStrategy(Strategy s) { this.strategy = s; }
    
    public void process(String data) {
        String cleaned = clean(data);
        String result = strategy.transform(cleaned);
        save(result);
    }
    
    private String clean(String d) { return d.trim(); }
    private void save(String d) { System.out.println(d); }
}

public interface Strategy {
    String transform(String data);
}
```

### 方法4: 函数式流程

用Lambda/Stream替代继承。

```java
public class FunctionalProcessor {
    private Function<String, String> processor;
    
    public FunctionalProcessor compose(
        Function<String, String> f1,
        Function<String, String> f2,
        Function<String, String> f3) {
        this.processor = f1.andThen(f2).andThen(f3);
        return this;
    }
    
    public String execute(String input) {
        return processor.apply(input);
    }
}

// 使用
FunctionalProcessor fp = new FunctionalProcessor()
    .compose(String::trim, String::toUpperCase, s -> "Result: " + s);
String result = fp.execute("  hello  ");
```

---

## 常见问题

### ❌ 问题1: 钩子方法过多导致复杂

**症状**: 太多虚方法导致子类混乱

**解决**:

```java
// 精简钩子，仅保留必要扩展点
public abstract class SimplifiedProcessor {
    public final void process(String data) {
        String step1 = preprocess(data);
        String step2 = customize(step1);
        save(step2);
    }
    
    protected String preprocess(String d) { return d.trim(); }
    protected abstract String customize(String d);
    protected void save(String d) {}
}
```

### ❌ 问题2: 子类职责不清

**症状**: 子类不知道该实现什么

**解决**: 提供清晰的文档和默认实现

```java
/**
 * 请实现transform方法来处理数据
 * 参数: 已清理的数据
 * 返回: 转换后的数据
 * 示例: return data.toUpperCase();
 */
protected abstract String transform(String data);

// 提供默认实现
protected String preprocess(String data) {
    return data != null ? data.trim() : "";
}
```

### ❌ 问题3: 流程变更成本高

**症状**: 修改算法步骤需改基类

**解决**: 支持步骤的增删

```java
public class FlexibleProcessor {
    private List<String> steps = new ArrayList<>();
    
    public void addStep(String name) { steps.add(name); }
    public void removeStep(String name) { steps.remove(name); }
    
    public void execute(String data) {
        for (String step : steps) {
            data = executeStep(step, data);
        }
    }
}
```

### ❌ 问题4: 测试困难

**症状**: 独立测试每个步骤困难

**解决**:

```java
// 注入依赖便于测试
public class TestableProcessor {
    private Function<String, String> preprocessor;
    private Function<String, String> transformer;
    
    public TestableProcessor(
        Function<String, String> pre,
        Function<String, String> trans) {
        this.preprocessor = pre;
        this.transformer = trans;
    }
    
    public String process(String data) {
        return transformer.apply(preprocessor.apply(data));
    }
}

// 测试时注入Mock
@Test
public void test() {
    TestableProcessor p = new TestableProcessor(
        d -> d.trim(),
        d -> d.toUpperCase()
    );
    assertEquals("HELLO", p.process("  hello  "));
}
```

---

## 最佳实践

✅ **保持模板简洁** - 仅保留核心流程
✅ **清晰命名钩子** - 名称反映功能
✅ **提供默认实现** - 减少子类负担
✅ **完整文档** - 说明每个钩子用途
✅ **支持灵活扩展** - 允许步骤增删
✅ **便于测试** - 注入依赖或提供Mock

---

## 真实案例

- **排序算法**: 排序框架 + 比较逻辑
- **数据处理**: 读-处理-写流程
- **HTTP请求**: 请求-响应框架
- **报告生成**: 收集-处理-输出流程

---

## 深度分析：模板方法 vs 策略 vs 钩子方法

### 模板方法 vs 策略模式

| 维度 | 模板方法 | 策略模式 |
|------|----------|---------|
| 继承结构 | 基类-子类 | 独立接口 |
| 控制流程 | 基类控制 | 客户端控制 |
| 灵活性 | 编译时 | 运行时 |
| 易用性 | 子类简单 | 客户端控制 |
| 适用场景 | 算法框架 | 算法替换 |

**何时选用**：
```java
// ❌ 不好：策略模式用于紧耦合的框架
public class FixedAlgorithm {
    public String execute(Strategy s, String input) {
        return s.process(input); // 无框架
    }
}

// ✅ 好：模板方法定义框架
public abstract class FrameworkAlgorithm {
    public final String execute(String input) {
        String prep = preprocess(input);
        String result = process(prep); // 虚方法灵活
        String final_ = postprocess(result);
        return final_;
    }
    
    protected abstract String process(String input);
}
```

### 模板方法 vs 钩子方法

**钩子方法** (Hook Method)：可选的虚方法，有默认实现

```java
// 模板方法 - 必须实现
public abstract class Template {
    public final void execute() {
        step1();
        step2(); // 抽象方法，必须实现
        step3();
    }
    
    protected abstract void step2();
}

// 带钩子方法 - 可选
public abstract class TemplateWithHooks {
    public final void execute() {
        step1();
        if (shouldExecuteStep2()) {
            step2();
        }
        step3();
    }
    
    protected void step2() {} // 默认空实现
    protected boolean shouldExecuteStep2() { return true; } // 钩子
}

// 子类可选地覆盖钩子
public class ConcreteTemplate extends TemplateWithHooks {
    @Override
    protected boolean shouldExecuteStep2() {
        return false; // 跳过step2
    }
}
```

**钩子方法的优势**：
- ✅ 子类可选覆盖
- ✅ 默认行为可用
- ✅ 灵活控制流程
- ✅ 向后兼容

---

## 五种实现框架的选择

### 1. 经典虚方法框架

**何时用**：Java传统方式，需要强制子类实现

```java
public abstract class OrderProcessor {
    public final void processOrder(Order order) {
        validateOrder(order);
        preparePayment(order);
        processPayment(order);
        sendConfirmation(order);
    }
    
    protected void validateOrder(Order o) {}
    protected abstract void preparePayment(Order o);
    protected abstract void processPayment(Order o);
    protected void sendConfirmation(Order o) {}
}

public class OnlineOrderProcessor extends OrderProcessor {
    @Override
    protected void preparePayment(Order o) { /* 在线支付准备 */ }
    @Override
    protected void processPayment(Order o) { /* 处理支付 */ }
}
```

### 2. 模板+钩子混合框架

**何时用**：需要可选扩展点的灵活框架

```java
public abstract class FlexibleProcessor {
    public final void process(String data) {
        onBeforeProcess();
        String cleaned = cleanData(data);
        String processed = doProcess(cleaned);
        onAfterProcess();
        if (shouldSave()) {
            save(processed);
        }
    }
    
    // 虚方法 - 必须实现
    protected abstract String doProcess(String data);
    
    // 钩子方法 - 可选覆盖
    protected void onBeforeProcess() {}
    protected void onAfterProcess() {}
    protected boolean shouldSave() { return true; }
    
    protected String cleanData(String d) { return d.trim(); }
    protected void save(String d) { System.out.println(d); }
}
```

### 3. 参数化模板框架

**何时用**：需要根据参数控制流程

```java
public class ParameterizedAlgorithm {
    private Config config;
    
    public ParameterizedAlgorithm(Config cfg) { this.config = cfg; }
    
    public void execute(String input) {
        if (config.shouldValidate()) {
            validate(input);
        }
        
        String result = process(input);
        
        if (config.shouldOptimize()) {
            result = optimize(result);
        }
        
        if (config.getOutputFormat() == OutputFormat.JSON) {
            outputAsJson(result);
        } else {
            outputAsXml(result);
        }
    }
}

public class Config {
    private boolean validate;
    private boolean optimize;
    private OutputFormat format;
    // getters...
}
```

### 4. 策略+模板混合框架

**何时用**：框架 + 算法复用

```java
public class HybridProcessor {
    private List<ProcessingStep> steps;
    private OutputStrategy output;
    
    public void process(String data) {
        String current = data;
        for (ProcessingStep step : steps) {
            current = step.execute(current);
        }
        output.write(current);
    }
}

public interface ProcessingStep {
    String execute(String input);
}

public class TransformStep implements ProcessingStep {
    private Function<String, String> transformer;
    
    public TransformStep(Function<String, String> t) {
        this.transformer = t;
    }
    
    @Override
    public String execute(String input) {
        return transformer.apply(input);
    }
}
```

### 5. 函数式框架（Java 8+）

**何时用**：简洁代码，高阶函数支持

```java
public class FunctionalTemplate {
    private Function<String, String> step1;
    private Function<String, String> step2;
    private Function<String, String> step3;
    private Consumer<String> output;
    
    public void execute(String input) {
        String result = step1.andThen(step2).andThen(step3).apply(input);
        output.accept(result);
    }
    
    public FunctionalTemplate withStep1(Function<String, String> f) {
        this.step1 = f;
        return this;
    }
    
    public FunctionalTemplate withStep2(Function<String, String> f) {
        this.step2 = f;
        return this;
    }
    
    // 链式调用构建
}

// 使用
new FunctionalTemplate()
    .withStep1(String::trim)
    .withStep2(String::toUpperCase)
    .withStep3(s -> "Result: " + s)
    .execute("  input  ");
```

---

## 高级话题：流程控制与错误处理

### 条件分支流程

```java
public abstract class ConditionalTemplate {
    public final void execute(String data) {
        if (isValid(data)) {
            processValid(data);
        } else {
            processInvalid(data);
        }
    }
    
    protected abstract boolean isValid(String data);
    protected abstract void processValid(String data);
    protected abstract void processInvalid(String data);
}
```

### 循环流程

```java
public abstract class LoopingTemplate {
    public final void executeAll(List<String> items) {
        for (String item : items) {
            if (shouldProcess(item)) {
                process(item);
            }
        }
    }
    
    protected boolean shouldProcess(String item) { return true; }
    protected abstract void process(String item);
}
```

### 异常处理框架

```java
public abstract class SafeTemplate {
    public final void executeWithErrorHandling(String input) {
        try {
            execute(input);
        } catch (SpecificException e) {
            handleSpecificError(e);
        } catch (Exception e) {
            handleGeneralError(e);
        } finally {
            cleanup();
        }
    }
    
    protected abstract void execute(String input) throws Exception;
    protected void handleSpecificError(SpecificException e) {}
    protected void handleGeneralError(Exception e) {}
    protected void cleanup() {}
}
```

### 事务性框架

```java
public abstract class TransactionalTemplate {
    public final void executeTransaction(String data) {
        beginTransaction();
        try {
            process(data);
            commit();
        } catch (Exception e) {
            rollback();
            throw e;
        }
    }
    
    protected abstract void process(String data) throws Exception;
    protected void beginTransaction() {}
    protected void commit() {}
    protected void rollback() {}
}
```

---

## 并发与性能优化

### 并发模板

```java
public abstract class ConcurrentTemplate {
    private ExecutorService executor = Executors.newFixedThreadPool(4);
    
    public final void executeParallel(List<String> items) {
        List<Future<?>> futures = new ArrayList<>();
        
        for (String item : items) {
            Future<?> future = executor.submit(() -> process(item));
            futures.add(future);
        }
        
        // 等待所有任务完成
        for (Future<?> f : futures) {
            f.get();
        }
    }
    
    protected abstract void process(String item);
}
```

### 性能最优模板

```java
public class OptimizedTemplate {
    private static final int BATCH_SIZE = 1000;
    
    public void processBatch(List<String> items) {
        for (int i = 0; i < items.size(); i += BATCH_SIZE) {
            int end = Math.min(i + BATCH_SIZE, items.size());
            List<String> batch = items.subList(i, end);
            processBatch(batch);
        }
    }
    
    private void processBatch(List<String> batch) {
        // 批量处理，减少开销
    }
}
```

---

## 测试策略

### 单元测试

```java
public class TemplateMethodTest {
    
    public static class TestableProcessor extends OrderProcessor {
        public List<String> executedSteps = new ArrayList<>();
        
        @Override
        protected void preparePayment(Order o) {
            executedSteps.add("prepare");
        }
        
        @Override
        protected void processPayment(Order o) {
            executedSteps.add("process");
        }
    }
    
    @Test
    public void testOrderOfExecution() {
        TestableProcessor p = new TestableProcessor();
        Order order = new Order("123", 100);
        
        p.processOrder(order);
        
        assertThat(p.executedSteps).containsExactly(
            "validate", "prepare", "process", "confirm"
        );
    }
}
```

### 集成测试

```java
@Test
public void testRealWorldScenario() {
    OrderProcessor processor = new OnlineOrderProcessor();
    Order order = createTestOrder();
    
    processor.processOrder(order);
    
    // 验证订单状态
    assertEquals(OrderStatus.COMPLETED, order.getStatus());
    
    // 验证外部系统调用
    verify(paymentService).charge(100);
    verify(emailService).sendConfirmation(any());
}
```

---

## 常见错误与修正

### 错误1：过度使用虚方法

❌ **问题**：太多虚方法导致子类复杂

```java
// 25个虚方法 - 太多！
public abstract class OvercomplicatedTemplate {
    public final void execute() {
        step1(); step2(); step3(); // ... step25();
    }
    
    protected abstract void step1();
    protected abstract void step2();
    // ... 23个更多虚方法
}
```

✅ **修正**：简化到3-5个核心虚方法

```java
public abstract class CleanTemplate {
    public final void execute() {
        preprocess();
        core(); // 唯一虚方法
        postprocess();
    }
    
    protected abstract void core();
}
```

### 错误2：违反Liskov原则

❌ **问题**：子类无法正确替换基类

```java
public abstract class Template {
    public abstract void process();
}

public class Subclass extends Template {
    @Override
    public void process() {
        throw new UnsupportedOperationException(); // 违反！
    }
}
```

✅ **修正**：提供有效实现

```java
public class Subclass extends Template {
    @Override
    public void process() {
        // 提供真实实现
    }
}
```

### 错误3：忘记final关键字

❌ **问题**：子类无意中覆盖模板方法

```java
public class Template {
    public void execute() { // 缺少final
        step1();
        step2();
    }
}

public class Subclass extends Template {
    @Override
    public void execute() { // 不好！破坏框架
        step2(); // 省略step1
    }
}
```

✅ **修正**：使用final保护

```java
public class Template {
    public final void execute() { // final - 保护框架
        step1();
        step2();
    }
}
```

---

## 决策流程图

使用模板方法的决策：

1. 多个类有相似算法 → YES
2. 其中不变部分 > 30% → YES
3. 子类需要定制 → YES
4. 考虑使用模板方法 ✅

不适用情形：
- 仅一个类 ❌
- 完全不同算法 ❌
- 需要运行时切换 → 用策略模式 ❌

---

## 性能考量

### 虚方法调用开销

虚方法调用比静态方法慢 **5-10%**：
- JIT编译会优化常见情况
- 内联缓存加速
- MonomorphicCallSites 最快

### 内存占用

使用模板方法 vs 策略：
- 模板：每个子类一个对象
- 策略：多个策略共享对象

### 优化建议

```java
// 频繁调用时使用缓存
private static final ThreadLocal<ProcessorCache> cache = 
    ThreadLocal.withInitial(ProcessorCache::new);

public void execute(String input) {
    ProcessorCache c = cache.get();
    String result = c.getCachedResult(input);
    if (result == null) {
        result = processInternal(input);
        c.cache(input, result);
    }
    return result;
}
```
