# Composite - 诊断与规划表

## 第1步: 需求诊断 - 你真的需要Composite吗？

### 🔍 快速检查清单

```
□ 系统存在明显的树形结构（父-子-孙关系）
□ 需要递归遍历和处理嵌套对象
□ 个体对象和容器对象支持相同操作
□ 需要统一处理单个叶子和复合节点
□ 经常需要按层级进行批量操作
□ 对象数量会动态变化
□ 需要支持添加/移除子组件
```

**诊断标准**:
- ✅ 勾选 5 项以上 → **强烈推荐使用 Composite**
- ⚠️ 勾选 3-4 项 → **可以使用 Composite**
- ❌ 勾选 2 项以下 → **可能过度设计，考虑简单继承**

### 真实场景检验

```
□ 文件系统？（Folder contains Files, Folders）
□ UI组件树？（Panel contains Buttons, Panels）
□ 组织架构？（Department contains Teams, Employees）
□ DOM树结构？（Element contains Elements）
□ 菜单系统？（Menu contains MenuItem, SubMenu）
□ 游戏场景图？（Node contains Nodes）
```

**检查结果**: [上述场景匹配度高 → 使用Composite]

---

## 第2步: 组合方式选择矩阵

### 透明组合 vs 安全组合

| 维度 | 透明组合 | 安全组合 |
|------|---------|---------|
| **接口** | 相同接口 | 分离接口 |
| **类型安全** | ❌ 弱 | ✅ 强 |
| **易用性** | ✅ 简单 | ⚠️ 需强转 |
| **代码示例** | `Component.add(c)` | `Composite.add(c)` |
| **Runtime异常** | ✅ 可能 | ❌ 无 |
| **推荐场景** | 操作统一 | 需要类型安全 |

```java
// ✅ 推荐: 安全组合
Component c = new Leaf();
// 正确代码: 
Composite comp = new Composite();
comp.add(c);  // 类型明确

// ❌ 问题: 透明组合
Component leaf = new Leaf();
Component comp = new Composite();
leaf.add(comp);  // Runtime异常!
```

---

## 第3步: 树形结构规划

### 关键评估项

#### 递归深度评估
```
浅树(1-3层)    → 递归无压力
中树(4-6层)    → 需要性能测试
深树(7+层)     → 考虑迭代或分层加载
无限深度       → 必须设置depth limit
```

**决策**:
- [ ] 最大预期深度: _____ 层
- [ ] 性能要求: 百ms内完成 / 秒级可接受 / 无要求
- [ ] 是否需要深度限制: 是 / 否

#### 循环引用风险评估
```
静态树(一次构建)     → 低风险
动态添加             → 需要检测
用户操作添加         → 高风险，必须检测
```

**预防措施**:
- [ ] 实现循环引用检测
- [ ] 方案选择: 
  - 【a】 添加时检测(add时)
  - 【b】 递归时检测(traverse时)
  - 【c】 禁止反向引用(设计约束)

```java
// 循环引用检测示例
public void add(Component c) {
    if (isAncestor(c)) {
        throw new IllegalArgumentException("循环引用!");
    }
    children.add(c);
}

private boolean isAncestor(Component c) {
    if (this == c) return true;
    if (parent != null) {
        return parent.isAncestor(c);
    }
    return false;
}
```

#### 节点数量与内存评估
```
小树(< 1000节点)     → 内存无压力
中树(1000-100K)      → 需要优化
大树(> 100K节点)     → 需要分层/缓存
数百万节点           → 需要对象池/享元
```

**内存优化策略**:
- [ ] 使用WeakReference去除不用节点
- [ ] 实现对象池复用节点
- [ ] 分层加载(lazy loading)
- [ ] 定期清理缓存

---

## 第4步: 实现方法选择

### 4大核心实现方式

| 方式 | 代码复杂度 | 性能 | 类型安全 | 适用场景 |
|------|-----------|------|---------|---------|
| **安全组合** | ⭐ | ⭐⭐⭐ | ✅ | 【推荐】需要类型安全 |
| **透明组合** | ⭐ | ⭐⭐⭐ | ❌ | 操作完全统一 |
| **迭代实现** | ⭐⭐ | ⭐⭐⭐⭐ | ✅ | 极深的树，避免栈溢出 |
| **访问者模式** | ⭐⭐⭐ | ⭐⭐ | ✅ | 多种操作频繁变化 |

**方式1: 安全组合（推荐）**
```java
// 完整实现框架
public interface Component {
    void operation();
}

public class Leaf implements Component {
    private String name;
    
    @Override
    public void operation() {
        System.out.println("Leaf: " + name);
    }
}

public class Composite implements Component {
    private String name;
    private List<Component> children = new ArrayList<>();
    
    public void add(Component c) {
        children.add(c);
    }
    
    public void remove(Component c) {
        children.remove(c);
    }
    
    @Override
    public void operation() {
        System.out.println("Composite: " + name);
        for (Component c : children) {
            c.operation();  // 递归调用
        }
    }
}
```

**方式2: 迭代实现（深树优化）**
```java
public void traverseIterative(Composite root) {
    Stack<Component> stack = new Stack<>();
    stack.push(root);
    
    while (!stack.isEmpty()) {
        Component current = stack.pop();
        current.operation();
        
        if (current instanceof Composite) {
            Composite composite = (Composite) current;
            // 反序入栈保持正序遍历
            for (int i = composite.getChildren().size() - 1; i >= 0; i--) {
                stack.push(composite.getChildren().get(i));
            }
        }
    }
}
```

---

## 第5步: 测试计划

### 单元测试检查清单

```
基础操作:
□ 单个Leaf操作
□ 单层Composite操作
□ 多层嵌套操作

功能测试:
□ add()添加子组件
□ remove()移除子组件
□ operation()递归执行
□ getChildren()获取子树

边界测试:
□ 空树操作
□ 单节点树
□ 非常深的树(depth > 100)
□ 大量节点(> 10000)

异常测试:
□ 循环引用检测
□ null引用处理
□ 深度溢出处理
□ 并发修改异常
```

### 性能测试

```java
@Test
public void testLargeTreeTraversal() {
    Composite root = buildDeepTree(1000);  // 1000层
    
    // 递归方式
    long start = System.nanoTime();
    traverseRecursive(root);
    long recursiveTime = System.nanoTime() - start;
    
    // 迭代方式
    start = System.nanoTime();
    traverseIterative(root);
    long iterativeTime = System.nanoTime() - start;
    
    System.out.println("Recursive: " + recursiveTime + "ns");
    System.out.println("Iterative: " + iterativeTime + "ns");
    
    // 迭代应该快很多
    assertTrue(iterativeTime < recursiveTime);
}
```

### 并发测试

```java
@Test
public void testConcurrentModification() throws InterruptedException {
    Composite root = new Composite();
    
    // 一个线程修改，另一个遍历
    ExecutorService exec = Executors.newFixedThreadPool(2);
    
    exec.submit(() -> {
        for (int i = 0; i < 1000; i++) {
            root.add(new Leaf());
        }
    });
    
    exec.submit(() -> {
        for (int i = 0; i < 100; i++) {
            root.operation();
        }
    });
    
    exec.awaitTermination(5, TimeUnit.SECONDS);
}
```

---

## 第6步: 代码审查清单

### 设计审查

- [ ] **是否真的需要Composite?** - 不是为了用而用
- [ ] **树的维度是否单一?** - 复杂树考虑组合多个树
- [ ] **操作接口是否合理?** - 不要把所有操作都放一个大接口
- [ ] **Component vs Composite职责清晰?** - 避免职责混乱
- [ ] **是否正确处理了循环引用?** - 动态树必须检测

### 实现审查

- [ ] **add/remove方法完整?** - 有添加必须有移除
- [ ] **递归深度有限制?** - 防止StackOverflow
- [ ] **null检查?** - children或参数为null
- [ ] **性能对数据规模的影响?** - 大树要用迭代
- [ ] **是否有并发问题?** - 考虑CopyOnWriteArrayList

```java
// ✅ 安全的并发实现
public class SafeComposite implements Component {
    private List<Component> children = 
        new CopyOnWriteArrayList<>();  // 线程安全
    
    public synchronized void add(Component c) {
        children.add(c);
    }
    
    @Override
    public void operation() {
        for (Component c : children) {
            c.operation();
        }
    }
}
```

### 性能审查

- [ ] **是否有不必要的创建?** - 使用对象池
- [ ] **性能监控?** - 大树记录遍历时间
- [ ] **内存监控?** - 监测GC频率
- [ ] **是否可以优化算法?** - 迭代 vs 递归权衡

---

## 常见陷阱与预防

### ⚠️ 陷阱1: 循环引用导致死循环

❌ **反面做法**:
```java
Composite a = new Composite();
Composite b = new Composite();
a.add(b);
b.add(a);  // 循环引用！

a.operation();  // 死循环!
```

✅ **正确做法**:
```java
public void add(Component c) {
    // 检测循环引用
    if (contains(c)) {
        throw new IllegalArgumentException("会形成循环!");
    }
    children.add(c);
    c.setParent(this);
}

private boolean contains(Component target) {
    if (this == target) return true;
    for (Component c : children) {
        if (c instanceof Composite) {
            if (((Composite)c).contains(target)) {
                return true;
            }
        }
    }
    return false;
}
```

### ⚠️ 陷阱2: StackOverflow in 深树

❌ **反面做法** - 总是用递归:
```java
public void traverseDeepTree(Component root, int depth) {
    if (depth > 1000) {
        throw new StackOverflowError();  // 太晚了!
    }
    root.operation();
    // ...递归
}
```

✅ **正确做法** - 用迭代处理深树:
```java
public void traverseDeepTree(Component root) {
    // 对于极深的树，直接用迭代
    Stack<Component> stack = new Stack<>();
    stack.push(root);
    
    while (!stack.isEmpty()) {
        Component current = stack.pop();
        current.operation();
        // 添加子节点
        if (current instanceof Composite) {
            ((Composite)current).getChildren()
                .forEach(stack::push);
        }
    }
}
```

### ⚠️ 陷阱3: 大量节点导致内存溢出

❌ **反面做法** - 一次加载全部:
```java
Composite root = new Composite();
for (int i = 0; i < 1000000; i++) {
    root.add(new Leaf());  // 内存爆炸!
}
```

✅ **正确做法** - 分层加载:
```java
public class LazyComposite implements Component {
    private List<Component> cached = new ArrayList<>();
    private LazyLoader loader;
    
    public List<Component> getChildren() {
        if (cached.isEmpty()) {
            cached.addAll(loader.load());  // 按需加载
        }
        return cached;
    }
    
    public void clearCache() {
        cached.clear();  // 及时释放
    }
}
```

### ⚠️ 陷阱4: 过度使用导致复杂性增加

❌ **反面做法** - 用Composite处理非树型结构:
```java
// 这不是树! 是图!
Composite a = new Composite();
Composite b = new Composite();
Composite c = new Composite();
a.add(b);
a.add(c);
b.add(c);  // c既在a下，又在b下 → 不是树!
```

✅ **正确做法** - 确实是树再用:
```
// 验证：每个节点只有一个父节点
// 没有循环
// 树根唯一
// 如果不满足 → 用Graph, 不用Composite
```

---

## 快速参考

### 最小实现模板

```java
interface Component {
    void operation();
}

class Leaf implements Component {
    @Override public void operation() { }
}

class Composite implements Component {
    List<Component> children = new ArrayList<>();
    public void add(Component c) { children.add(c); }
    
    @Override
    public void operation() {
        for (Component c : children) {
            c.operation();
        }
    }
}
```

### 决策流程图

```
需要递归处理树形结构?
├─ 是 → 是否需要类型安全?
│      ├─ 是 → 安全组合 ✅
│      └─ 否 → 透明组合
├─ 树很深(> 100层)?
│      └─ 是 → 改用迭代实现
└─ 否 → 考虑其他模式
```

### 故障排查表

| 问题 | 原因 | 检查项 | 解决方案 |
|------|------|--------|---------|
| StackOverflow | 1. 循环引用 2. 树太深 | 检测循环 / 测试深度 | 验证+ 迭代 |
| OutOfMemory | 节点过多 / 不释放 | 监控heap / 数据量 | 分层加载 / GC |
| 性能低 | 递归开销 / 未缓存 | profile / 对比递归vs迭代 | 用迭代 / 缓存 |
| 并发异常 | 多线程修改 | 查看异常栈 | CopyOnWriteArrayList |

---

## 相关资源

- **SKILL.md** - Composite Pattern 完整详解
- **reference.md** - 多语言完整实现
- **composite-pattern/** - 其他参考文件
