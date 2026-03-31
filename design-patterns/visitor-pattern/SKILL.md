---
name: 访问者模式
description: "在不改变对象结构的前提下，为对象添加新的操作。"
license: MIT
---

# 访问者模式 (Visitor Pattern)

## 核心概念

**Visitor**是**行为型设计模式**，使用双分派实现在不改变对象结构的情况下增加新操作。分离操作与对象结构，使得新增操作无需修改元素类。

**核心原则**: 双分派、操作与数据分离、开放封闭原则

---

## 何时使用

**始终使用**:
- 需要为对象结构中的元素进行多种不同操作
- 对象结构较稳定但操作经常变化  
- 需要避免修改元素类
- 支持多种不同的元素类型

**触发短语**: "为不同对象类型执行不同操作?" "如何为现有对象添加操作?"

**典型场景**:
| 场景 | 元素 | 操作 | 用途 |
|------|------|------|------|
| 编译器 | AST节点 | 类型检查/代码生成 | 语法分析 |
| 报告 | 数据元素 | 不同格式输出 | 数据导出 |
| 遍历 | 树/图节点 | 访问/统计 | 图处理 |

---

## 4个实现方法

### 方法1: 经典访问者模式

```java
// 元素接口
public interface Element {
    void accept(Visitor visitor);
}

// 具体元素
public class ConcreteElementA implements Element {
    @Override
    public void accept(Visitor v) { v.visitA(this); }
}

public class ConcreteElementB implements Element {
    @Override
    public void accept(Visitor v) { v.visitB(this); }
}

// 访问者接口
public interface Visitor {
    void visitA(ConcreteElementA e);
    void visitB(ConcreteElementB e);
}

// 具体访问者
public class ConcreteVisitor implements Visitor {
    @Override
    public void visitA(ConcreteElementA e) {
        System.out.println("Process A");
    }
    
    @Override
    public void visitB(ConcreteElementB e) {
        System.out.println("Process B");
    }
}
```

### 方法2: 参数化访问器

使用参数化类型支持返回值。

```java
public interface Visitor<T> {
    T visitA(ElementA e);
    T visitB(ElementB e);
}

public class SumVisitor implements Visitor<Integer> {
    @Override
    public Integer visitA(ElementA e) { return e.getValue(); }
    
    @Override
    public Integer visitB(ElementB e) { return e.getValue() * 2; }
}

// 使用
Visitor<Integer> v = new SumVisitor();
int result = elements.stream()
    .map(e -> e.accept(v))
    .reduce(0, Integer::sum);
```

### 方法3: 链式访问器

支持多个访问者链式执行。

```java
public class ChainedVisitor implements Visitor {
    private List<Visitor> chain = new ArrayList<>();
    
   public ChainedVisitor add(Visitor v) { 
        chain.add(v); 
        return this; 
    }
    
    @Override
    public void visitA(ElementA e) {
        for (Visitor v : chain) v.visitA(e);
    }
}

// 使用
new ChainedVisitor()
    .add(new ValidateVisitor())
    .add(new TransformVisitor())
    .add(new PrintVisitor());
```

### 方法4: 函数式访问器

用Lambda替代Visitor类。

```java
public class FunctionalVisitor {
    private Map<Class<?>, Consumer<?>> handlers = new HashMap<>();
    
    @SuppressWarnings("unchecked")
    public <T> FunctionalVisitor handle(Class<T> type, Consumer<T> handler) {
        handlers.put(type, handler);
        return this;
    }
    
    public void visit(Element e) {
        Consumer handler = handlers.get(e.getClass());
        if (handler != null) handler.accept(e);
    }
}

// 使用
new FunctionalVisitor()
    .handle(ElementA.class, e -> System.out.println("A"))
    .handle(ElementB.class, e -> System.out.println("B"))
    .visit(elementA);
```

---

## 常见问题

### ❌ 问题1: 元素结构变更

**症状**: 添加新元素类型导致所有访问者需改

**解决**: 提供默认处理

```java
public interface Visitor {
    void visitA(ElementA e);
    void visitB(ElementB e);
    
    // 默认处理未知元素
    default void visitUnknown(Element e) {}
}
```

### ❌ 问题2: 访问器数爆增

**症状**: 每个操作需要一个访问者类

**解决**: 使用函数式或配置驱动

```java  
// 配置驱动
Map<String, Consumer> visitors = new HashMap<>();
visitors.put("print", e -> System.out.println(e));
visitors.put("count", e -> count++);
```

### ❌ 问题3: 循环引用

**症状**: 图结构中可能无限循环

**解决**:

```java
public class CyclicVisitor implements Visitor {
    private Set<Element> visited = new HashSet<>();
    
    @Override
    public void visitA(ElementA e) {
        if (visited.contains(e)) return;
        visited.add(e);
        // 处理...
    }
}
```

### ❌ 问题4: 性能开销

**症状**: 大对象结构访问缓慢

**解决**: 缓存和并行处理

```java
public class OptimizedVisitor implements Visitor {
    private Map<Element, Object> cache = new ConcurrentHashMap<>();
    
    private Object getOrCompute(Element e, Function<Element, Object> comp) {
        return cache.computeIfAbsent(e, comp);
    }
}
```

---

## 最佳实践

✅ **分离操作与结构** - 访问者集中操作逻辑
✅ **支持扩展** - 易于添加新访问者
✅ **处理循环** - 记录已访问节点
✅ **性能优化** - 缓存计算结果
✅ **清晰命名** - visit方法名清楚
✅ **提供默认** - 简化新访问者开发

---

## 真实案例

- **编译器**: AST的类型检查、代码生成
- **报告系统**: 生成多种格式输出
- **遍历**: 树/图的搜索、统计

---

## 深度理论：双分派原理

### 单分派 vs 双分派

#### 单分派（传统OOP）

```java
// 单分派：执行方法仅基于接收者类型
public void process(Element e) {
    if (e instanceof ElementA) {
        processA((ElementA) e);
    } else if (e instanceof ElementB) {
        processB((ElementB) e);
    }
}
// 问题：客户端需要instanceof检查
```

#### 双分派（访问者模式）

```java
// 双分派：基于接收者 + 参数的类型
public interface Element {
    void accept(Visitor v); // 第一次分派：方法选择基于Element类型
}

public class ElementA implements Element {
    @Override
    public void accept(Visitor v) {
        v.visitA(this); // 第二次分派：方法选择基于Visitor类型
    }
}

// 客户端无需类型检查
element.accept(visitor);
```

### 双分派如何工作

```
step1: element.accept(visitor)
       |
       +-- ElementA重写accept()
       |   |
       +-- 调用 visitor.visitA(this)
           |
           +-- PrintVisitor重写visitA()
               +-- 执行对应逻辑
```

### 单/双分派对比

| 特性 | 单分派 | 双分派 |
|------|--------|--------|
| 类型检查 | 客户端 | 隐式 |
| 代码简洁 | 低 | 高 |
| 变更影响 | 客户端更改 | 无需改客户端 |
| 新元素 | 需改客户端 | 只需新的accept |
| 新操作 | 新访问者 | 只需新访问者 |

---

## 访问者模式 vs 其他模式

### 访问者 vs 策略

| 维度 | 访问者 | 策略 |
|------|--------|------|
| 关注点 | 操作 | 算法 |
| 结构 | 多元素 | 单对象 |
| 分派 | 双分派 | 单分派 |
| 应用场景 | 异构集合 | 同构对象 |

### 访问者 vs 命令

```java
// 访问者：固定接收者，遍历所有元素
visitor.visit(element);

// 命令：固定元素集，执行不同操作
command.execute();
```

---

## 五种高级实现

### 1. 基于反射的通用访问者

**何时用**：元素类型动态，无需修改访问者

```java
public class ReflectionVisitor {
    public void visit(Object element) {
        Method visitMethod = findVisitMethod(element.getClass());
        if (visitMethod != null) {
            visitMethod.invoke(this, element);
        }
    }
    
    private Method findVisitMethod(Class<?> elementClass) {
        String methodName = "visit" + elementClass.getSimpleName();
        try {
            return this.getClass().getDeclaredMethod(methodName, elementClass);
        } catch (NoSuchMethodException e) {
            return null;
        }
    }
    
    // 实现具体visit方法
    public void visitElementA(ElementA e) { /* handle A */ }
    public void visitElementB(ElementB e) { /* handle B */ }
}
```

### 2. 动态函数映射访问者

**何时用**：操作灵活，支持运行时配置

```java
public class DynamicVisitor<T> {
    private Map<Class<?>, Function<?, T>> handlers = new HashMap<>();
    
    @SuppressWarnings("unchecked")
    public <E> void register(Class<E> type, Function<E, T> handler) {
        handlers.put(type, handler);
    }
    
    @SuppressWarnings("unchecked")
    public T visit(Object element) {
        Function handler = handlers.get(element.getClass());
        if (handler == null) {
            throw new UnsupportedOperationException(
                "No handler for " + element.getClass());
        }
        return (T) handler.apply(element);
    }
}

// 使用
DynamicVisitor<Integer> calculator = new DynamicVisitor<>();
calculator.register(NumberNode.class, n -> n.value);
calculator.register(BinaryOp.class, b -> calculate(b));

int result = ast.accept(calculator);
```

### 3. 分组访问者（解决访问者爆炸）

**何时用**：很多访问者，需分类管理

```java
public class GroupedVisitor {
    private List<Visitor> validators = new ArrayList<>();
    private List<Visitor> transformers = new ArrayList<>();
    private List<Visitor> outputters = new ArrayList<>();
    
    public void validate(Element e) {
        validators.forEach(v -> e.accept(v));
    }
    
    public void transform(Element e) {
        transformers.forEach(v -> e.accept(v));
    }
    
    public void output(Element e) {
        outputters.forEach(v -> e.accept(v));
    }
}
```

### 4. 上下文感知访问者

**何时用**：访问过程需要上下文信息

```java
public interface Element {
    void accept(ContextualVisitor visitor, Context ctx);
}

public interface ContextualVisitor {
    void visitA(ElementA e, Context ctx);
    void visitB(ElementB e, Context ctx);
}

public class Context {
    private int depth = 0;
    private Set<Element> visited = new HashSet<>();
    
    public void enter() { depth++; }
    public void exit() { depth--; }
    public boolean hasVisited(Element e) { return visited.contains(e); }
    public void mark(Element e) { visited.add(e); }
}

public class PrintingVisitor implements ContextualVisitor {
    @Override
    public void visitA(ElementA e, Context ctx) {
        System.out.println("  ".repeat(ctx.depth) + e);
    }
}
```

### 5. 异步访问者

**何时用**：访问操作需要异步执行

```java
public interface AsyncElement {
    CompletableFuture<?> accept(AsyncVisitor visitor);
}

public interface AsyncVisitor {
    CompletableFuture<?> visitA(ElementA e);
    CompletableFuture<?> visitB(ElementB e);
}

public class AsyncPrintingVisitor implements AsyncVisitor {
    @Override
    public CompletableFuture<?> visitA(ElementA e) {
        return CompletableFuture.runAsync(() -> System.out.println(e));
    }
}

// 使用
CompletableFuture<?> future = element.accept(visitor);
future.join(); // 等待完成
```

---

## 处理循环引用

### 问题：图中的循环

```java
// ❌ 无限循环
Node a = new Node("A");
Node b = new Node("B");
a.addChild(b);
b.addChild(a); // 循环！

visitor.visit(a); // 无限递归
```

### 解决方案1：Set追踪

```java
public class CycleDetectingVisitor implements Visitor {
    private Set<Element> visited = new HashSet<>();
    
    @Override
    public void visitA(ElementA e) {
        if (visited.contains(e)) return; // 已访问，跳过
        visited.add(e);
        
        // 处理...
        if (e instanceof Composite) {
            for (Element child : ((Composite) e).getChildren()) {
                child.accept(this);
            }
        }
    }
}
```

### 解决方案2：深度限制

```java
public class DepthLimitedVisitor implements Visitor {
    private static final int MAX_DEPTH = 100;
    private int currentDepth = 0;
    
    @Override
    public void visitA(ElementA e) {
        if (currentDepth >= MAX_DEPTH) return;
        
        currentDepth++;
        try {
            // 处理...
        } finally {
            currentDepth--;
        }
    }
}
```

### 解决方案3：时间戳标记

```java
public class TimestampVisitor implements Visitor {
    private static int timestamp = 0;
    private final int visitorId = timestamp++;
    private Map<Element, Integer> visitTime = new HashMap<>();
    
    @Override
    public void visitA(ElementA e) {
        Integer lastTime = visitTime.get(e);
        if (lastTime != null && lastTime == visitorId) {
            return; // 同一访问中已处理
        }
        visitTime.put(e, visitorId);
        // 处理...
    }
}
```

---

## 访问者爆炸问题（N×M问题）

### 问题描述

- N种元素类型
- M种访问操作
- 需实现 N×M 个方法

例如：10种元素 × 10种操作 = 100个方法

### 解决方案1：反射+注解

```java
public class AnnotationBasedVisitor {
    public void visit(Element e) throws IllegalAccessException {
        Method[] methods = this.getClass().getDeclaredMethods();
        Class<?> elementClass = e.getClass();
        
        for (Method m : methods) {
            VisitHandler handler = m.getAnnotation(VisitHandler.class);
            if (handler != null && m.getParameterCount() == 1) {
                Class<?> paramType = m.getParameterTypes()[0];
                if (paramType.isAssignableFrom(elementClass)) {
                    m.invoke(this, e);
                    return;
                }
            }
        }
    }
}

@VisitHandler
public void handleNumberNode(NumberNode n) { }

@VisitHandler
public void handleBinaryOp(BinaryOp op) { }
```

### 解决方案2：Map配置

```java
public class MapBasedVisitor {
    private Map<Class<?>, Consumer<?>> operations = new HashMap<>();
    
    {
        operations.put(ElementA.class, e -> handleA((ElementA) e));
        operations.put(ElementB.class, e -> handleB((ElementB) e));
    }
    
    @SuppressWarnings("unchecked")
    public void visit(Element e) {
        Consumer operation = operations.get(e.getClass());
        if (operation != null) {
            operation.accept(e);
        }
    }
    
    private void handleA(ElementA e) { }
    private void handleB(ElementB e) { }
}
```

### 解决方案3：分层架构

```java
// 基础操作
public interface BaseVisitor {
    void visit(Element e);
}

// 特定域操作
public interface ValidationVisitor extends BaseVisitor { }
public interface TransformationVisitor extends BaseVisitor { }
public interface OutputVisitor extends BaseVisitor { }

// 默认实现共用
public abstract class AbstractVisitor implements BaseVisitor {
    protected void visitDefault(Element e) { }
    
    @Override
    public void visit(Element e) {
        if (e instanceof SpecialElement) {
            visitSpecial((SpecialElement) e);
        } else {
            visitDefault(e);
        }
    }
}
```

---

## 性能优化

### 1. 缓存策略

```java
public class CachingVisitor implements Visitor {
    private Map<Element, Object> cache = new ConcurrentHashMap<>();
    
    @Override
    public void visitA(ElementA e) {
        Object result = cache.computeIfAbsent(e, key -> compute(e));
        use(result);
    }
    
    private Object compute(Element e) {
        // 昂贵计算
        return null;
    }
}
```

### 2. 批处理

```java
public class BatchVisitor implements Visitor {
    private List<Element> batch = new ArrayList<>();
    private static final int BATCH_SIZE = 100;
    
    @Override
    public void visitA(ElementA e) {
        batch.add(e);
        if (batch.size() >= BATCH_SIZE) {
            processBatch();
            batch.clear();
        }
    }
    
    private void processBatch() {
        // 批量处理比单个处理快
    }
}
```

### 3. 并行处理

```java
public class ParallelVisitor implements Visitor {
    private ForkJoinPool pool = ForkJoinPool.commonPool();
    
    @Override
    public void visitComposite(CompositeElement e) {
        List<CompletableFuture<?>> tasks = e.getChildren().stream()
            .map(child -> CompletableFuture.runAsync(
                () -> child.accept(this), pool))
            .collect(Collectors.toList());
        
        CompletableFuture.allOf(tasks.toArray(new CompletableFuture[0])).join();
    }
}
```

---

## 测试策略

### 单元测试

```java
public class VisitorTest {
    static class MockElement implements Element {
        @Override
        public void accept(Visitor v) { v.visitMock(this); }
    }
    
    static class TestVisitor implements Visitor {
        List<String> visited = new ArrayList<>();
        
        @Override
        public void visitMock(MockElement e) {
            visited.add("mock");
        }
    }
    
    @Test
    public void testVisitor() {
        Element e = new MockElement();
        TestVisitor v = new TestVisitor();
        
        e.accept(v);
        
        assertTrue(v.visited.contains("mock"));
    }
}
```

### 集成测试

```java
@Test
public void testComplexStructure() {
    CompositeElement root = buildTree();
    StatisticsVisitor stats = new StatisticsVisitor();
    
    root.accept(stats);
    
    assertEquals(100, stats.getNodeCount());
    assertEquals(50, stats.getMaxDepth());
}
```

---

## 最常见的实现错误

### 错误1：忘记处理新元素类型

❌ **问题**：
```java
public void visitA(ElementA e) { }
public void visitB(ElementB e) { }
// 新增ElementC，编译器不报错，运行时异常
```

✅ **修正**：
```java
public void visitA(ElementA e) { }
public void visitB(ElementB e) { }
public void visitC(ElementC e) { } // 必须添加

// 或使用默认处理
default void visitUnknown(Element e) { }
```

### 错误2：修改访问过程中的结构

❌ **问题**：
```java
public void visitA(ElementA e) {
    e.getParent().removeChild(e); // 错！正在遍历
}
```

✅ **修正**：
```java
public void visitA(ElementA e) {
    toRemove.add(e); // 延迟操作
}

// 遍历结束后清理
void cleanup() {
    toRemove.forEach(e -> e.getParent().removeChild(e));
}
```

### 错误3：无限循环

❌ **问题**：
```java
public void visitA(ElementA e) {
    for (Element child : e.getChildren()) {
        child.accept(this); // 可能循环
    }
}
```

✅ **修正**：
```java
private Set<Element> visited = new HashSet<>();

public void visitA(ElementA e) {
    if (visited.contains(e)) return;
    visited.add(e);
    
    for (Element child : e.getChildren()) {
        child.accept(this);
    }
}
```

---

## 决策清单

何时使用访问者模式？

- [ ] 对象结构复杂且稳定
- [ ] 需要对结构执行多种不同操作
- [ ] 新增操作频繁
- [ ] 修改元素类困难（如外部库）

✅ 满足所有条件 → 使用访问者

不适用情况：
- 结构经常变更 ❌
- 仅有一两个操作 ❌
- 类型安全很关键且类型复杂 ❌

---

## 与其他模式组合

### 访问者+组合

```java
public abstract class Node {
    abstract void accept(Visitor visitor);
}

public class Leaf extends Node {
    @Override
    void accept(Visitor visitor) { visitor.visitLeaf(this); }
}

public class Composite extends Node {
    List<Node> children;
    
    @Override
    void accept(Visitor visitor) {
        visitor.visitComposite(this);
        children.forEach(c -> c.accept(visitor));
    }
}
```

### 访问者+迭代器

```java
public interface TraversableElement {
    void accept(Visitor v);
    Iterator<Element> iterator();
}
```

### 访问者+工厂

```java
public class VisitorFactory {
    public static Visitor createPrinter() { return new PrintVisitor(); }
    public static Visitor createValidator() { return new ValidateVisitor(); }
}
```

---

## 总结对比表

| 特性 | 经典 | 参数化 | 链式 | 函数式 | 异步 |
|------|------|--------|------|--------|------|
| 复杂度 | 中 | 低 | 中 | 低 | 高 |
| 灵活性 | 高 | 高 | 高 | 低 | 中 |
| 性能 | 高 | 高 | 中 | 中 | 低 |
| 类型检查 | ✅ | ✅ | ✅ | ❌ | ✅ |
| 适用场景 | 复杂操作 | 有返回值 | 多操作链 | 简单操作 | 异步IO |
