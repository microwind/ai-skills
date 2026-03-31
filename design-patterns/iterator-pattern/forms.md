# Iterator Pattern - 诊断与规划表

## 第1步: 需求诊断 - 你真的需要Iterator吗？

### 🔍 快速检查清单（勾选所有适用项）

```
☐ 需要遍历聚合对象中的元素，但不想暴露其内部结构
☐ 需要支持多种遍历方式（顺序、逆序、树形、深度优先等）
☐ 需要统一接口来遍历不同类型的集合（List、Set、Tree、Graph等）
☐ 需要并发遍历同一集合的多个副本
☐ 需要在遍历过程中检测集合的并发修改
☐ 需要延迟计算或无限序列（如文件行、数据库游标）
☐ 需要支持暂停/恢复遍历的能力
☐ 需要跳过某些元素或进行条件遍历
```

**诊断标准**:
- ✅ 勾选 5 项以上 → **强烈推荐使用Iterator**
- ⚠️ 勾选 3-4 项 → **可以使用，权衡复杂性**
- ❌ 勾选 2 项以下 → **可能过度设计，使用简单循环**

---

## 第2步: 遍历方式分类与选择

### 遍历复杂度评估表

| 遍历类型 | 数据结构 | 复杂度 | 性能 | 适用场景 |
|---------|--------|--------|------|---------|
| **线性遍历** | Array/List | ⭐ | 极快 | 顺序访问所有元素 |
| **树形遍历** | Tree/Graph | ⭐⭐⭐ | 中等 | 分层结构、文件系统 |
| **深度优先(DFS)** | Graph | ⭐⭐⭐ | 中等 | 路径搜索、拓扑排序 |
| **广度优先(BFS)** | Graph | ⭐⭐⭐ | 中等 | 最短路径、层级遍历 |
| **倒序遍历** | List | ⭐ | 快速 | 栈式处理、撤销操作 |
| **条件过滤** | Any | ⭐⭐ | 中等 | 满足条件的元素 |
| **无限流** | Stream | ⭐⭐ | 快速 | 惰性求值、生成器 |
| **并发遍历** | ThreadSafe | ⭐⭐⭐⭐ | 较慢 | 多线程安全访问 |

---

## 第3步: 实现方法选择决策矩阵

### 4种主流实现方式对比

| 方法 | 语言特性 | 复杂度 | 灵活性 | 性能 | 最佳用途 |
|-----|--------|--------|--------|------|---------|
| **外部迭代器** | 接口契约 | ⭐⭐ | 高 | 高 | 标准集合库、多种遍历 |
| **内部迭代器** | 回调/闭包 | ⭐ | 中 | 高 | 函数式编程、简单处理 |
| **生成器** | yield/语法糖 | ⭐ | 高 | 极高 | Python/JavaScript, 流式处理 |
| **异步生成器** | async/await | ⭐⭐⭐ | 很高 | 中 | I/O密集、网络流、数据库游标 |

### 快速选择指南

```
你的编程语言？
├─ Java/C#/C++ → 外部迭代器 (Iterator<T>)
├─ Python/JavaScript/Ruby → 生成器 (yield)
├─ 需要异步? → 异步生成器 (async function*)
└─ 简单一次性遍历? → 内部迭代器 (forEach)
```

---

## 第4步: 集合结构分析 - 你需要迭代什么？

### 集合复杂度评估表

| 集合类型 | 元素数量 | 内存占用 | 迭代需求 | 推荐解决方案 |
|--------|--------|--------|---------|-----------|
| **小列表** (<100) | 少 | 低 | 简单顺序 | 直接for循环 |
| **大列表** (>10K) | 大 | 中等 | 顺序遍历 | 外部迭代器 |
| **二叉树** | 中等 | 中等 | DFS/BFS | TreeIterator + Stack/Queue |
| **图** | 可变 | 可变 | 多种遍历 | GraphIterator + 访问者模式 |
| **数据库表** | 超大 | 内存外 | 游标式遍历 | 惰性游标迭代器 |
| **无限流** | ∞ | 动态 | 部分遍历 | 生成器/惰性流 |
| **并发集合** | 中等 | 中等 | 线程安全 | 并发迭代器 + CopyOnWrite |

### 并发修改检测表

```
╔══════════════════════════════════════════╗
║   遍历中集合被修改 - 如何应对？         ║
╚══════════════════════════════════════════╝

选项1: 快速失败 (Fail-Fast)
  ✅ 立即抛出 ConcurrentModificationException
  ✅ 实现: 记录modcount，每次操作检查
  ❌ 可能中断操作
  用于: 调试、开发

选项2: 快速失败 (Fail-Safe)  
  ✅ 创建集合快照/副本
  ✅ 继续遍历副本，原集合可修改
  ❌ 额外内存开销
  用于: 生产环境安全

选项3: 弱一致性 (Weakly Consistent)
  ✅ 允许遍历时修改，但结果不确定
  ✅ 最小性能开销
  ❌ 结果不可预测
  用于: CopyOnWriteArrayList, ConcurrentHashMap
```

---

## 第5步: 实现规划 - 6步走

### ✅ 步骤1: 理解你的集合
```
问题列表:
□ 集合中元素类型? ___________
□ 集合大小范围? ___________  
□ 元素是否修改? ___________
□ 是否多线程访问? ___________
□ 是否需要多个迭代器同时运行? ___________
```

### ✅ 步骤2: 选择迭代方向与算法
```
遍历类型:
□ 线性顺序       □ 线性逆序
□ 树形DFS        □ 树形BFS  
□ 图遍历         □ 条件过滤
□ 惰性/流式      □ 并发安全
```

### ✅ 步骤3: 定义迭代器接口
```java
// 最小接口
interface Iterator<T> {
    boolean hasNext();
    T next();     // 获取下一个元素
    void remove(); // 可选: 移除当前元素
}

// 扩展接口  
interface AdvancedIterator<T> extends Iterator<T> {
    void rewind();      // 重置到起始位置
    T previous();       // 倒序移动
    int size();         // 集合大小
    void reset(String algorithm); // 切换遍历算法
}
```

### ✅ 步骤4: 实现具体迭代器
```java
类名模板:
- CollectionNameIterator: XXX集合的外部迭代器
- CollectionName.Itr: 嵌套内部迭代器
- CollectionNameGenerator: 生成器实现

关键检查点:
□ 边界条件处理 (首元素、末元素)
□ 并发修改检测（如适用）
□ 异常情况处理
□ 资源清理（如适用）
```

### ✅ 步骤5: 集合与迭代器关联
```
模式选项:

选项A - 集合创建迭代器 (推荐)
class MyCollection {
    public Iterator<T> iterator() {
        return new MyIterator(this.elements);
    }
}

选项B - 迭代器自己查询集合
class MyIterator {
    public MyIterator(MyCollection collection) {
        this.collection = collection;
        this.index = 0;
    }
}

选项C - 工厂模式创建
class IteratorFactory {
    static Iterator<T> create(Collection<T> c, String type) {
        switch(type) {
            case "DFS": return new DFSIterator(c);
            case "BFS": return new BFSIterator(c);
            // ...
        }
    }
}
```

### ✅ 步骤6: 编写测试与文档
```
测试清单:
□ 正常遍历路径（Happy Path）
□ 空集合情况
□ 单元素集合  
□ 大数据集合性能测试
□ 并发修改检测（如适用）
□ 异常恢复
□ 内存泄漏检查
□ 多个迭代器并发运行

文档要点:
□ 遍历顺序说明
□ 边界行为（如无下一个元素）
□ ConcurrentModificationException条件
□ 性能特征 (O(n)? O(log n)?...)
□ 内存占用 (O(1)? O(n)?...)
□ 示例代码与常见错误
```

---

## 第6步: 性能检查清单

### 性能测试场景

| 场景 | 数据量 | 遍历次数 | 期望时间 | 检查项 |
|-----|--------|--------|---------|--------|
| 顺序遍历 | 100K | 1x | <10ms | Throughput, GC |
| 倒序遍历 | 100K | 1x | <15ms | Stack overhead |
| DFS深树 | 10K节点 | 1x | <5ms | Recursion depth |
| 并发遍历 | 10K | 10线程 | <50ms | Lock contention |
| 部分遍历 | 1M | 1% | <5ms | Laziness验证 |

### 常见性能问题

```
问题1: Iterator每次next()都很慢
原因: 非顺序访问、复杂计算、同步锁
解决: 缓存、预计算、读写锁分离

问题2: 多个迭代器竞争导致GC压力
原因: 每个迭代器创建大量临时对象
解决: 对象池、迭代器重用、栈分配

问题3: 深度递归爆栈 (TreeIterator/GraphIterator)
原因: 树/图深度过深，递归栈溢出
解决: 显式栈(Stack)替代递归, 迭代式遍历
```

---

## 常见陷阱预防与解决方案

### ⚠️ 陷阱1: 遍历时修改集合 (ConcurrentModificationException)
❌ 错误做法:
```java
for (Iterator<String> it = list.iterator(); it.hasNext(); ) {
    String item = it.next();
    if (item.equals("remove_me")) {
        list.remove(item);  // ❌ ConcurrentModificationException!
    }
}
```

✅ 正确做法:
```java
// 方法1: 使用迭代器的remove()方法
for (Iterator<String> it = list.iterator(); it.hasNext(); ) {
    String item = it.next();
    if (item.equals("remove_me")) {
        it.remove();  // ✅ 安全
    }
}

// 方法2: 创建副本后修改
List<String> toRemove = new ArrayList<>();
for (String item : list) {
    if (item.equals("remove_me")) {
        toRemove.add(item);
    }
}
list.removeAll(toRemove);  // ✅ 安全
```

### ⚠️ 陷阱2: TreeIterator递归爆栈
❌ 递归实现 (深树时失败):
```python
def dfs_recursive(node):
    yield node
    for child in node.children:
        yield from dfs_recursive(child)  # 深树→爆栈!
```

✅ 显式栈实现 (安全):
```python
def dfs_iterative(root):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))  # 显式栈管理
```

### ⚠️ 陷阱3: 多个迭代器状态冲突
❌ 共享状态:
```java
class BadIterator {
    static int currentIndex = 0;  // ❌ 所有迭代器共享!
    
    public int next() {
        return collection.get(currentIndex++);
    }
}
```

✅ 独立状态:
```java
class GoodIterator {
    private int currentIndex = 0;  // ✅ 每个迭代器独立
    
    public int next() {
        return collection.get(currentIndex++);
    }
}
```

### ⚠️ 陷阱4: 生成器不清理资源
❌ 资源泄漏:
```python
def read_huge_file(filename):
    f = open(filename)  # ❌ 如果生成器中途中止，文件不关闭
    for line in f:
        yield line
```

✅ 自动资源管理:
```python
def read_huge_file(filename):
    with open(filename) as f:  # ✅ 自动关闭
        for line in f:
            yield line

# 或在迭代器中明确清理
class FileIterator:
    def __del__(self):
        if self.file:
            self.file.close()
```

### ⚠️ 陷阱5: 异步/IO迭代器超时
❌ 无限等待:
```typescript
async function* fetchData(ids) {
    for (const id of ids) {
        yield await fetch(`/api/${id}`);  // ❌ 可能无限等待
    }
}
```

✅ 超时控制:
```typescript
async function* fetchDataWithTimeout(ids, timeoutMs) {
    for (const id of ids) {
        try {
            yield await Promise.race([
                fetch(`/api/${id}`),
                new Promise((_, reject) => 
                    setTimeout(() => reject('timeout'), timeoutMs)
                )
            ]);
        } catch (e) {
            console.error(`Failed to fetch ${id}: ${e}`);
        }
    }
}
```

---

## 代码审查清单

### 设计审查
- [ ] Iterator接口职责清晰 (hasNext, next, remove)
- [ ] Collection支持iterator()方法
- [ ] 遍历顺序定义明确
- [ ] 支持多个独立的迭代器实例
- [ ] 符合集合框架规范

### 实现审查
- [ ] 正确处理空集合
- [ ] 正确处理单元素集合
- [ ] 边界条件: 首元素、末元素
- [ ] NoSuchElementException时机正确
- [ ] 并发修改检测正确 (如需要)
- [ ] 代码可读性强

### 性能审查
- [ ] next()调用时间复杂度 O(1) 或已说明
- [ ] 创建迭代器对象内存占用 O(1)
- [ ] 无不必要的数据复制
- [ ] 大数据集合上有性能测试

### 文档审查
- [ ] 遍历顺序明确说明
- [ ] 边界行为文档化
- [ ] 并发修改行为文档化
- [ ] 异常情况列举
- [ ] 性能特征说明
- [ ] 代码示例包含正确和错误用法

---

## 快速参考 - 决策流程图

```
需要遍历一个集合?
│
├─ 是 → 集合是什么类型?
│       │
│       ├─ List/Array → 外部迭代器 (index-based)
│       ├─ Tree → TreeIterator (DFS/BFS)
│       ├─ Graph → GraphIterator (DFS/BFS/拓扑排序)
│       ├─ 数据库/文件 → 游标迭代器 (lazy)
│       └─ 无限流 → 生成器 (yield)
│
├─ 需要多种遍历方式?
│       YES → 策略模式 + Iterator工厂
│       NO  → 单一迭代器足够
│
├─ 多线程访问?
│       YES → ConcurrentIterator (同步/CopyOnWrite)
│       NO  → 标准迭代器
│
├─ 遍历时修改集合?
│       YES → 使用it.remove() 或创建副本  
│       NO  → 直接遍历
│
└─ 完成!
```

---

## 快速启动代码模板

### Java - 标准外部迭代器
```java
// 集合类
public class MyCollection<T> {
    private T[] elements;
    
    public Iterator<T> iterator() {
        return new MyIterator();
    }
    
    // 内部迭代器类
    private class MyIterator implements Iterator<T> {
        private int index = 0;
        
        @Override
        public boolean hasNext() {
            return index < elements.length;
        }
        
        @Override
        public T next() {
            if (!hasNext()) throw new NoSuchElementException();
            return elements[index++];
        }
    }
}

// 使用
MyCollection<String> coll = new MyCollection<>();
for (String item : coll) {  // 使用简化的for-each
    System.out.println(item);
}
```

### Python - 生成器
```python
class MyCollection:
    def __init__(self, items):
        self.items = items
    
    def __iter__(self):
        for item in self.items:
            yield item

# 使用
coll = MyCollection(['A', 'B', 'C'])
for item in coll:
    print(item)

# 或直接创建生成器
def my_generator():
    yield 1
    yield 2
    yield 3

for item in my_generator():
    print(item)
```

### TypeScript - 异步迭代器
```typescript
class AsyncIterableCollection<T> {
    constructor(private items: T[], private delay: number) {}
    
    async *[Symbol.asyncIterator]() {
        for (const item of this.items) {
            await new Promise(resolve => setTimeout(resolve, this.delay));
            yield item;
        }
    }
}

// 使用
const coll = new AsyncIterableCollection(['A', 'B', 'C'], 100);
for await (const item of coll) {
    console.log(item);
}
```

---

## 集合类型vs最佳迭代方式对应表

| 集合类型 | 数据结构 | 推荐实现 | 遍历算法 | 代码位置 |
|---------|--------|--------|--------|---------|
| ArrayList | 数组 | 外部迭代器 | 索引遍历 | ArrayListIterator |
| LinkedList | 链表 | 双向迭代器 | 指针遍历 | LinkedListIterator |
| Tree | 树 | 树迭代器 | DFS/BFS | TreeIterator |
| Graph | 图 | 图迭代器 | DFS/BFS/拓扑 | GraphIterator |
| Database | SQL表 | 游标迭代器 | ResultSet遍历 | DatabaseCursor |
| FileSystem | 目录树 | 文件树迭代器 | DFS目录遍历 | DirectoryIterator |
| Stream | 流 | 生成器 | 惰性评估 | stream.map().filter() |
| 无限序列 | 算法生成 | 生成器 | yield每个值 | Fibonacci.generator() |
