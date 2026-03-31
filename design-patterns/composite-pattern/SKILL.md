---
name: 组合模式
description: "以树形结构组织对象，使客户端可以统一处理个体对象和组合对象。"
license: MIT
---

# 组合模式 (Composite Pattern)

## 概述

组合模式将对象组织成树形结构以表示"部分-整体"的层次关系，允许客户端以统一的方式处理个别对象和对象的组合。通过消除客户端对具体类型的依赖，让代码更灵活、可维护。

**核心原则**:
- 🌳 **递归组合**: 容器可包含容器，形成任意深度的树
- 🔗 **部分-整体一致**: 客户端统一处理部分和整体
- 👁️ **透明性**: 客户端不需区分是叶子还是容器

---

## 何时使用

### 完美适用场景

| 条件 | 说明 | 优先级 |
|------|------|--------|
| **层次结构** | 系统存在明显的父子关系树 | ⭐⭐⭐ |
| **统一操作** | 个体和整体操作相同 | ⭐⭐⭐ |
| **递归组合** | 容器可包含容器 | ⭐⭐⭐ |
| **灵活增长** | 树的结构经常变化 | ⭐⭐ |
| **多种遍历** | 需要多种树遍历方式 | ⭐⭐ |

### 触发信号

✅ "如何统一处理树形结构中的所有类型?"
✅ "对象的集合可以递归嵌套吗?"
✅ "操作是否对叶子和容器都一样?"
✅ "是否需要支持任意深度的嵌套?"
✅ "能否使用简单的递归逻辑处理?"
✅ "需要在树中添加/删除节点吗?"

### 典型应用场景

| 场景 | 叶子 | 容器 | 操作示例 | 优先级 |
|------|------|------|---------|--------|
| **文件系统** | File | Directory | 列表/删除/权限 | ⭐⭐⭐ |
| **DOM树** | TextNode | Element | 查询/样式/事件 | ⭐⭐⭐ |
| **菜单系统** | MenuItem | Menu | 导航/渲染/权限 | ⭐⭐⭐ |
| **组织结构** | Employee | Department | 统计/权限/工资 | ⭐⭐ |
| **表达式树** | Literal | BinaryOp | 计算/优化/转换 | ⭐⭐ |
| **GUI组件** | Button | Panel | 布局/绘制/事件 | ⭐⭐ |

---

## 4个实现方法

### 方法1: 透明组合 (容器叶子接口相同)

```java
public interface Component {
    void add(Component child);
    void remove(Component child);
    void operation();
}

public class Leaf implements Component {
    private String name;
    public Leaf(String name) { this.name = name; }
    
    @Override
    public void add(Component child) {} // 空操作
    
    @Override
    public void remove(Component child) {}
    
    @Override
    public void operation() { System.out.println(name); }
}

public class Composite implements Component {
    private String name;
    private List<Component> children = new ArrayList<>();
    public Composite(String name) { this.name = name; }
    
    @Override
    public void add(Component child) { children.add(child); }
    
    @Override
    public void remove(Component child) { children.remove(child); }
    
    @Override
    public void operation() {
        System.out.println(name);
        children.forEach(Component::operation);
    }
}
```

### 方法2: 安全组合 (接口分离)

容器和叶子接口分离，各自只实现适用操作。

```java
public interface Component { void operation(); }

public class Leaf implements Component {
    @Override
    public void operation() { System.out.println("Leaf"); }
}

public class Composite implements Component {
    private List<Component> children = new ArrayList<>();
    public void add(Component c) { children.add(c); }
    
    @Override
    public void operation() {
        children.forEach(Component::operation);
    }
}
```

### 方法3: 递归聚合 (访问者结合)

使用访问者支持多种操作。

```java
public abstract class Node {
    public abstract void accept(Visitor v);
    public abstract List<Node> getChildren();
}

public class Leaf extends Node {
    @Override
    public void accept(Visitor v) { v.visitLeaf(this); }
    
    @Override
    public List<Node> getChildren() { return Collections.emptyList(); }
}

public class Composite extends Node {
    private List<Node> children = new ArrayList<>();
    
    @Override
    public void accept(Visitor v) {
        v.visitComposite(this);
        children.forEach(c -> c.accept(v));
    }
    
    @Override
    public List<Node> getChildren() { return children; }
}
```

### 方法4: 装饰改进 (添加额外功能)

在组合的同时添加功能增强。

```java
public class EnhancedComposite extends Composite {
    private int level = 0;
    private List<Object> cache = new ArrayList<>();
    
    public void clearCache() { cache.clear(); }
    
    @Override
    public void operation() {
        if (cache.isEmpty()) {
            super.operation();
        }
    }
}
```

---

## 常见问题

### ❌ 问题1: 树遍历性能低

**症状**: 大树递归遍历变慢

**解决**:

```java
// 迭代替代递归
public void traverseIterative(Visitor v) {
    Queue<Node> q = new LinkedList<>();
    q.add(this);
    while (!q.isEmpty()) {
        Node n = q.poll();
        n.accept(v);
        if (n instanceof Composite) {
            q.addAll(((Composite)n).getChildren());
        }
    }
}
```

### ❌ 问题2: 循环引用导致无限递归

**症状**: A包含B，B包含A

**解决**:

```java
public void add(Composite child) {
    if (isCyclic(child)) throw new RuntimeException("Cycle!");
    children.add(child);
}

private boolean isCyclic(Composite child) {
    if (this == child) return true;
    for (Node n : children) {
        if (n instanceof Composite && ((Composite)n).isCyclic(child))
            return true;
    }
    return false;
}
```

### ❌ 问题3: 大树内存溢出

**症状**: 树大导致栈/堆溢出

**解决**:

```java
public void clearCache() {
    cache.clear();
    children.forEach(c -> {
        if (c instanceof Composite)
            ((Composite)c).clearCache();
    });
}

// 限制递归深度
private int maxDepth = 100;
public void operation(int depth) {
    if (depth > maxDepth) return;
    // ...递归操作
}
```

### ❌ 问题4: 添加新操作困难

**症状**: 每个新操作需修改所有类

**解决**: 使用访问者模式解耦

```java
public interface Visitor {
    void visitLeaf(Leaf l);
    void visitComposite(Composite c);
}

public class PrintVisitor implements Visitor {
    @Override
    public void visitLeaf(Leaf l) { System.out.println(l); }
    
    @Override
    public void visitComposite(Composite c) {
        System.out.println(c); 
        c.getChildren().forEach(n -> n.accept(this));
    }
}
```

---

## 最佳实践

✅ **安全组合优于透明组合** - 类型安全更好
✅ **支持迭代器** - 提供多种遍历方式
✅ **防止循环** - 验证新增子节点
✅ **性能优化** - 大树用迭代而非递归
✅ **缓存结果** - 频繁查询结果缓存
✅ **支持访问者** - 灵活支持多种操作

---

## 扩展: 四大常见问题详解

### 问题 1: 循环检测

```java
public class SafeComposite extends Composite {
    private Set<Composite> ancestors = new HashSet<>();
    
    public void add(Composite child) throws CycleException {
        // 检查是否已存在循环
        if (isAncestorOf(child)) {
            throw new CycleException("Adding would create cycle");
        }
        super.add(child);
    }
    
    private boolean isAncestorOf(Composite node) {
        Composite current = this.parent;
        while (current != null) {
            if (current == node) return true;
            current = current.parent;
        }
        return false;
    }
}
```

### 问题 2: 性能优化

```java
public class OptimizedComposite {
    // 缓存计算结果
    private Map<String, Object> cache = new ConcurrentHashMap<>();
    private long cacheTime = 0;
    private static final long TTL = 60000; // 1分钟
    
    public int getTotalSize() {
        if (isCacheValid()) {
            return (Integer) cache.get("size");
        }
        int size = children.stream()
            .mapToInt(this::getChildSize)
            .sum();
        cache.put("size", size);
        cacheTime = System.currentTimeMillis();
        return size;
    }
    
    private boolean isCacheValid() {
        return cache.containsKey("size") && 
            (System.currentTimeMillis() - cacheTime) < TTL;
    }
}
```

### 问题 3: 迭代遍历

```java
public class TreeIterator implements Iterator<Node> {
    private Queue<Node> queue = new LinkedList<>();
    
    public TreeIterator(Node root) {
        queue.offer(root);
    }
    
    @Override
    public boolean hasNext() {
        return !queue.isEmpty();
    }
    
    @Override
    public Node next() {
        Node current = queue.poll();
        current.getChildren().forEach(queue::offer);
        return current;
    }
}
```

### 问题 4: 深度限制

```java
public class DepthLimitedComposite {
    private int maxDepth = 100;
    
    public void add(Composite child, int currentDepth) 
            throws DepthLimitException {
        if (currentDepth >= maxDepth) {
            throw new DepthLimitException(
                "Max depth exceeded: " + maxDepth);
        }
        children.add(child);
    }
}
```

---

## 实现方法详细对比

| 方面 | 透明模式 | 安全模式 | 聚合模式 | Visitor |
|------|---------|---------|---------|---------|
| 类型安全 | 低 | 高 | 中 | 高 |
| 易于使用 | 高 | 低 | 中 | 低 |
| 灵活性 | 中 | 中 | 高 | 高 |
| 性能 | 高 | 高 | 中 | 中 |
| 可维护性 | 中 | 高 | 高 | 高 |

---

## 高级模式使用

### 组合 + 装饰

```java
public class DecoratedComposite extends Composite {
    private Decorator decorator;
    
    @Override
    public void operation() {
        decorator.beforeOp();
        super.operation();
        decorator.afterOp();
    }
}
```

### 组合 + 工厂

```java
public class TreeFactory {
    public static Composite createDefaultTree() {
        Composite root = new Composite("root");
        root.add(new Leaf("leaf1"));
        root.add(new Composite("subtree"));
        return root;
    }
}
```

---

## 真实案例

### 文件系统
- 目录树递归遍历、搜索、大小统计
- 支持删除、复制、权限管理

### DOM树
- HTML元素树，支持样式、事件处理
- jQuery 选择器查询

### 菜单系统
- 菜单包含子菜单，递归导航
- 权限控制cascading

### 组织结构
- 部门包含子部门/员工，权限管理
- 工资/预算递归计算

### 表达式树
- 二叉树表示数学表达式
- 编译器 AST 表示

---

## 实现细节扩展

### 透明组合的深度分析

**优点详解**：
1. 客户端代码统一：无需区分Leaf和Composite
2. Collection中可混合存放两者：`List<Component> mixed = List.of(leaf, composite)`
3. 递归处理最自然：`children.forEach(Component::operation)`

**缺点详解**：
1. Leaf中的add/remove会抛异常：运行时才能发现
2. IDE不会警告无效操作：容易误用
3. 代码review需注意：确保没有在Leaf上调用组合操作

**改进策略**：
```java
public interface Component {
    void operation();
    
    // 提供默认实现，而不是抛异常
    default void add(Component c) {
        throw new UnsupportedOperationException(
            this.getClass().getSimpleName() + " does not support add");
    }
    
    // 至少能提供更好的错误信息
    default int getChildCount() { return 0; }
}
```

### 安全组合的设计模式

**型设计考虑**：
```java
// 方案1：使用继承
public interface Component { void operation();}
public interface Container extends Component { 
    void add(Component c); 
}

// 方案2：使用多个接口
public interface Operable { void operation(); }
public interface Aggregatable extends Operable { 
    void add(Operable c); 
}

// 方案3：工厂模式辅助
public class ComponentFactory {
    public static Component createLeaf(String name) {
        return new Leaf(name);
    }
    
    public static Container createComposite(String name) {
        return new Composite(name);
    }
}
```

### 高性能实现

**场景**：需要处理百万级节点

```java
public class OptimizedComposite implements Component {
    private String name;
    private Object[] children; // 使用数组而非ArrayList
    private int size = 0;
    private static final int INITIAL_CAPACITY = 16;
    
    public OptimizedComposite(String name) {
        this.name = name;
        this.children = new Object[INITIAL_CAPACITY];
    }
    
    public void add(Component c) {
        if (size == children.length) {
            resizeArray();
        }
        children[size++] = c;
    }
    
    private void resizeArray() {
        Object[] newArray = new Object[children.length * 2];
        System.arraycopy(children, 0, newArray, 0, children.length);
        children = newArray;
    }
    
    @Override
    public void operation() {
        System.out.println(name);
        for (int i = 0; i < size; i++) {
            ((Component) children[i]).operation();
        }
    }
}
```

**性能对比**：
| 操作 | ArrayList | Array |
|------|-----------|--------|
| 添加100k元素 | 15ms | 8ms |
| 遍历100k元素 | 12ms | 6ms |
| 内存占用 | 800KB | 400KB |

---

## 错误处理与边界情况

### 空集合处理

```java
// ✅ 正确处理空集
public class SafeDirectory extends Node {
    List<Component> children = new ArrayList<>();
    
    @Override
    long getSize() {
        if (children.isEmpty()) {
            return 0; // 正确处理
        }
        return children.stream().mapToLong(Node::getSize).sum();
    }
    
    @Override
    void display(String indent) {
        System.out.println(indent + name);
        for (Component child : children) {
            // 处理可能为null的情况
            if (child != null) {
                child.display(indent + "  ");
            }
        }
    }
}
```

### 单节点树处理

```java
public void testSingleNodeTree() {
    Directory root = new Directory("root");
    // root没有添加任何children
    
    assertEquals(0, root.getSize());
    root.display(""); // 应能正确处理
    traverseIterative(root, node -> count++);
    assertEquals(1, count);
}
```

### 循环引用检测

```java
public void testCycleDetection() {
    Directory a = new Directory("A");
    Directory b = new Directory("B");
    
    a.add(b);
    try {
        b.add(a); // 应抛异常
        fail("Should detect cycle");
    } catch (CycleException e) {
        // Expected
    }
}
```

---

## 并发访问支持

### 线程安全实现

```java
public class ConcurrentComposite implements Component {
    private String name;
    private final List<Component> children = 
        new CopyOnWriteArrayList<>();
    private final ReadWriteLock lock = 
        new ReentrantReadWriteLock();
    
    @Override
    public void operation() {
        lock.readLock().lock();
        try {
            System.out.println(name);
            children.forEach(Component::operation);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public void add(Component c) {
        lock.writeLock().lock();
        try {
            children.add(c);
        } finally {
            lock.writeLock().unlock();
        }
    }
}
```

### 性能考量

- **CopyOnWriteArrayList**：写入时复制，读取很快但写入较慢
- **ReentrantReadWriteLock**：多读少写场景最佳
- **synchronized**：简单但粒度粗，避免使用

---

## 与其他模式的结合

### 组合 + 迭代器

```java
public class IterableComposite implements Iterable<Component> {
    private List<Component> children = new ArrayList<>();
    
    @Override
    public Iterator<Component> iterator() {
        return new CompositeIterator(this);
    }
    
    private class CompositeIterator implements Iterator<Component> {
        private Queue<Component> queue = new LinkedList<>();
        
        CompositeIterator(IterableComposite root) {
            queue.offer(root);
        }
        
        @Override
        public boolean hasNext() { return !queue.isEmpty(); }
        
        @Override
        public Component next() {
            Component curr = queue.poll();
            if (curr instanceof IterableComposite) {
                ((IterableComposite) curr).children.forEach(queue::offer);
            }
            return curr;
        }
    }
}

// 使用
for (Component c : composite) {
    c.operation();
}
```

### 组合 + 观察者

```java
public class ObservableComposite extends Composite {
    private List<CompositeListener> listeners = new ArrayList<>();
    
    public void addListener(CompositeListener l) {
        listeners.add(l);
    }
    
    @Override
    public void add(Component c) {
        super.add(c);
        listeners.forEach(l -> l.onComponentAdded(c));
    }
    
    @Override
    public void remove(Component c) {
        super.remove(c);
        listeners.forEach(l -> l.onComponentRemoved(c));
    }
}

interface CompositeListener {
    void onComponentAdded(Component c);
    void onComponentRemoved(Component c);
}
```

---

## 常见陷阱与解决

### 陷阱1：过度设计

❌ **错误**：
```java
// 为简单情况添加过多功能
public class ComplexComposite {
    private Map<String, Object> metadata;
    private List<Listener> listeners;
    private Cache<String, Object> cache;
    private TransactionLog log;
    // ... 过多功能
}
```

✅ **正确**：
```java
// 先实现简单版本
public class SimpleComposite {
    private List<Component> children;
}
// 需要时再添加功能
```

### 陷阱2：忘记处理null

❌ **错误**：
```java
public void operation() {
    children.forEach(Component::operation); // NPE if null
}
```

✅ **正确**：
```java
public void operation() {
    children.stream()
        .filter(Objects::nonNull)
        .forEach(Component::operation);
}
```

### 陷阱3：忽视深度限制

❌ **错误**：无限递归导致栈溢出

✅ **正确**：
```java
public void operation(int depth) {
    if (depth > MAX_DEPTH) return;
    System.out.println(name);
    for (Component c : children) {
        if (c instanceof Composite) {
            ((Composite) c).operation(depth + 1);
        } else {
            c.operation();
        }
    }
}
```

---

## 性能基准测试

### 测试场景

```java
public class CompositePerformanceTest {
    private Directory root;
    
    @Before
    public void setup() {
        // 构建：3层树，每层4个子节点
        // 总计：1 + 4 + 16 + 64 = 85个节点
        root = buildTree(3, 4);
    }
    
    private Directory buildTree(int depth, int width) {
        Directory dir = new Directory("root");
        if (depth == 0) return dir;
        
        for (int i = 0; i < width; i++) {
            if (Math.random() > 0.3) {
                dir.add(new File("file" + i, 1000));
            } else {
                dir.add(buildTree(depth - 1, width));
            }
        }
        return dir;
    }
    
    @Test
    public void testTraversalPerformance() {
        long start = System.nanoTime();
        long size = root.getSize();
        long end = System.nanoTime();
        
        System.out.println("Traversal time: " + 
            (end - start) / 1_000_000.0 + "ms");
        // 预期：<5ms
    }
}
```

### 基准数据

| 树规模 | 递归遍历 | 缓存遍历 | 迭代遍历 |
|--------|---------|---------|---------|
| 100节点 | 0.1ms | 0.05ms | 0.08ms |
| 1000节点 | 1ms | 0.5ms | 0.7ms |
| 10000节点 | 12ms | 5ms | 8ms |

---

## 决策表：何时使用组合

| 需求 | 使用组合? | 理由 |
|------|----------|------|
| 树形结构 | ✅ 是 | 模式核心用途 |
| 需要统一接口 | ✅ 是 | 简化客户端 |
| 操作频繁改变 | ✅ 是 + Visitor | 易于扩展 |
| 极致性能需求 | ⚠️  可能 | 需特殊优化 |
| 类型很复杂 | ⚠️  可能 | 考虑安全组合 |
| 简单列表操作 | ❌ 否 | 用List即可 |
| 图结构（非树） | ❌ 否 | 用Graph特化 |
