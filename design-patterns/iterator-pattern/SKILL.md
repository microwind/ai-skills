---
name: Iterator
description: "提供一种方法顺序访问容器中的各个元素"
license: MIT
---

# Iterator Pattern (迭代器模式)

## 核心概念

**Iterator**是一种Behavioral设计模式。

**定义**: 提供一种方法来顺序访问一个聚合对象中的各个元素，而不暴露该对象的内部表示。它将集合的遍历与其内部结构分离。

### 核心思想

- **遍历算法与集合分离**: 集合不需要知道遍历算法
- **统一接口**: 所有迭代器遵循同一接口
- **多种遍历方式**: 支持前向、反向、深度优先等多种遍历
- **延迟计算**: 支持惰性求值和无限序列

---

## 何时使用

### 触发条件

1. **集合结构多样** - 数组、链表、树等，需要统一遍历
2. **多种遍历方式** - 同一个集合需要正向、反向、按文件夹等遍历
3. **隐藏内部结构** - 集合实现细节不想暴露
4. **支持并发遍历** - 同时进行多个遍历
5. **需要延迟加载** - 如数据库查询集合、无限序列

### 不适合场景

- ❌ 简单的数组或List - 直接使用for循环即可
- ❌ 一维序列 - 顺序遍历就足够了
- ❌ 性能极端敏感 - 迭代器有额外开销

---

## 基本结构

### 参与者

1. **Iterator** - 迭代器接口，定义遍历元素的方法
2. **ConcreteIterator** - 具体迭代器，实现遍历逻辑
3. **Aggregate** - 聚合对象接口，提供创建迭代器的方法
4. **ConcreteAggregate** - 具体集合

### UML关系

```
┌──────────────────┐
│    Iterator      │
├──────────────────┤
│ + next()         │
│ + hasNext()      │
│ + remove()       │
└──────────────────┘
         △
         │ implements
    ┌────┴─────────────────┐
    │                      │
┌──────────────────┐  ┌────────────────────┐
│ListIterator      │  │TreeIterator        │
├──────────────────┤  ├────────────────────┤
│ - current        │  │ - stack            │
│ + next()         │  │ + next()           │
└──────────────────┘  └────────────────────┘
         ▲                      ▲
         │                      │
    ┌────┴──────────────────────┴───────┐
    │                                   │
┌──────────────────┐          ┌──────────────────┐
│  Aggregate       │          │ ConcreteAggregate│
├──────────────────┤          ├──────────────────┤
│+ createIterator()│─────────→│ - elements: List │
└──────────────────┘          │+ createIterator()│
                              └──────────────────┘
```

---

## 实现方式对比

### 方法1: 外部迭代器 (Classic)

**特点**: 集合外部管理遍历状态

```java
interface Iterator<T> {
    boolean hasNext();
    T next();
    void remove();
}

class ListIterator<T> implements Iterator<T> {
    private List<T> list;
    private int currentIndex = 0;
    
    ListIterator(List<T> list) {
        this.list = list;
    }
    
    @Override
    public boolean hasNext() {
        return currentIndex < list.size();
    }
    
    @Override
    public T next() {
        if (!hasNext()) throw new NoSuchElementException();
        return list.get(currentIndex++);
    }
    
    @Override
    public void remove() {
        list.remove(--currentIndex);
    }
}

// 使用示例
List<String> names = Arrays.asList("Alice", "Bob", "Carol");
Iterator<String> iterator = new ListIterator<>(names);
while (iterator.hasNext()) {
    System.out.println(iterator.next());
}
```

### 方法2: 内部迭代器

**特点**: 集合内部管理遍历，通过回调处理元素

```java
interface Collection<T> {
    void forEach(Consumer<T> action);
}

class MyCollection<T> implements Collection<T> {
    private T[] elements;
    
    @Override
    public void forEach(Consumer<T> action) {
        for (T element : elements) {
            action.accept(element);
        }
    }
}

// 使用示例 - Lambda表达式
MyCollection<String> collection = new MyCollection<>();
collection.forEach(System.out::println);
```

### 方法3: 生成器风格的迭代器

**特点**: 使用生成器或协程处理无限序列

```java
// Java生成器模式
abstract class Generator<T> {
    abstract void execute();
    
    protected void yield(T value) {
        // 储存value，暂停执行
    }
}

// Python生成器
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

gen = fibonacci()
for i in range(10):
    print(next(gen))
```

### 方法4: 异步迭代器

**特点**: 支持异步操作，如异步I/O

```java
async function* asyncGenerator() {
    for (let i = 0; i < 5; i++) {
        await delay(1000);
        yield i;
    }
}

// 使用
for await (const value of asyncGenerator()) {
    console.log(value);
}
```

---

## 6个真实使用场景

### 场景1: 数据库游标 (Database Cursor)

**应用**: JDBC ResultSet, ORM框架

```java
// 数据库查询结果遍历
try (Statement stmt = connection.createStatement()) {
    ResultSet rs = stmt.executeQuery("SELECT * FROM users");
    while (rs.next()) {
        System.out.println(rs.getString("name"));
    }
}

// 或使用迭代器
class DatabaseIterator implements Iterator<Record> {
    private ResultSet resultSet;
    
    @Override
    public boolean hasNext() {
        try {
            return resultSet.next();
        } catch (SQLException e) {
            return false;
        }
    }
    
    @Override
    public Record next() {
        try {
            return mapRecord(resultSet);
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 场景2: DOM树遍历 (DOM Traversal)

**应用**: XML/HTML解析, DOM操作

```java
// XML节点遍历
interface NodeIterator {
    Node nextNode();
}

class DepthFirstIterator implements NodeIterator {
    private Stack<Node> stack;
    
    public DepthFirstIterator(Node root) {
        stack = new Stack<>();
        stack.push(root);
    }
    
    @Override
    public Node nextNode() {
        if (stack.isEmpty()) return null;
        
        Node node = stack.pop();
        // 按相反顺序压入子节点  
        for (int i = node.getChildCount() - 1; i >= 0; i--) {
            stack.push(node.getChild(i));
        }
        return node;
    }
}
```

### 场景3: 集合框架 (Collection Framework)

**应用**: Java Collections Framework

```java
// Java内置迭代器
List<String> list = new ArrayList<>();
list.add("A");
list.add("B");

// 外部迭代器
Iterator<String> iter1 = list.iterator();
while (iter1.hasNext()) {
    System.out.println(iter1.next());
}

// 内部迭代器 (Stream API)
list.forEach(System.out::println);

// 增强for循环  (Iterator的语法糖)
for (String item : list) {
    System.out.println(item);
}
```

### 场景4: 目录文件遍历 (File System)

**应用**: 文件系统遍历, 递归查找

```java
// 遍历目录结构
class DirectoryIterator {
    private Queue<File> queue = new LinkedList<>();
    
    public DirectoryIterator(File root) {
        queue.offer(root);
    }
    
    public File next() {
        if (queue.isEmpty()) return null;
        
        File file = queue.poll();
        if (file.isDirectory()) {
            for (File child : file.listFiles()) {
                queue.offer(child);
            }
        }
        return file;
    }
}

// Java NIO
try (DirectoryStream<Path> stream = Files.newDirectoryStream(path)) {
    for (Path file : stream) {
        System.out.println(file);
    }
}
```

### 场景5: 分页和游标 (Pagination)

**应用**: Web框架分页, API游标

```java
// 分页式加载
class PageIterator<T> implements Iterator<T> {
    private int pageSize;
    private int currentPage = 0;
    private List<T> currentPageData;
    private DataRepository repo;
    
    @Override
    public boolean hasNext() {
        if (currentPageData == null) {
            loadNextPage();
        }
        return !currentPageData.isEmpty();
    }
    
    @Override
    public T next() {
        if (currentPageData == null || currentPageData.isEmpty()) {
            loadNextPage();
        }
        return currentPageData.remove(0);
    }
    
    private void loadNextPage() {
        currentPageData = repo.findPage(currentPage++, pageSize);
    }
}
```

### 场景6: 流和管道处理 (Stream/Pipeline)

**应用**: 函数式编程, 数据流处理

```java
// Stream API - 内置迭代
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
numbers.stream()
    .filter(n -> n > 2)
    .map(n -> n * 2)
    .forEach(System.out::println);

// 自定义流迭代
class StreamIterator<T> implements Iterator<T> {
    private List<T> data;
    private Function<T, Boolean> filter;
    private Function<T, T> transform;
    private int index = 0;
    
    @Override
    public boolean hasNext() {
        // 跳过不符合filter的元素
        while (index < data.size()) {
            if (filter.apply(data.get(index))) {
                return true;
            }
            index++;
        }
        return false;
    }
    
    @Override
    public T next() {
        return transform.apply(data.get(index++));
    }
}
```

---

## 4个常见问题及解决方案

### 问题1: 并发修改异常 (Concurrent Modification)

**症状**:
- 遍历集合时添加/删除元素导致异常
- fail-fast行为

**解决方案**:

```java
// ✅ 使用迭代器的remove()方法
List<String> list = new ArrayList<>();
list.add("A"); list.add("B"); list.add("C");

Iterator<String> iter = list.iterator();
while (iter.hasNext()) {
    String item = iter.next();
    if (item.equals("B")) {
        iter.remove(); // ✅ 安全
    }
}

// ❌ 直接修改集合会失败
for (String item : list) {
    if (item.equals("B")) {
        list.remove(item); // ❌ ConcurrentModificationException
    }
}

// ✅ 或使用线程安全的集合
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// ✅ 或使用Copy-On-Write集合
List<String> cowList = new CopyOnWriteArrayList<>(list);
for (String item : cowList) {
    if (item.equals("B")) {
        cowList.remove(item);
    }
}
```

### 问题2: 延迟加载和无限序列

**症状**:
- 集合太大，全部加载会耗尽内存
- 需要表示无限序列

**解决方案**:

```java
// ✅ 延迟加载迭代器
abstract class LazyIterator<T> implements Iterator<T> {
    protected abstract T loadNext();
    
    @Override
    public T next() {
        return loadNext();
    }
}

// 无限序列 - Fibonacci
class FibonacciIterator implements Iterator<Long> {
    private long prev = 0, curr = 1;
    
    @Override
    public boolean hasNext() {
        return true; // 无限
    }
    
    @Override
    public Long next() {
        long next = prev + curr;
        prev = curr;
        curr = next;
        return prev;
    }
}

// 使用
FibonacciIterator fib = new FibonacciIterator();
for (int i = 0; i < 10; i++) {
    System.out.println(fib.next());
}
```

### 问题3: 复杂的遍历模式

**症状**:
- 需要多种遍历方式(BFS, DFS, Level-order等)
- 遍历逻辑复杂且易出错

**解决方案**:

```java
// ✅ 为每种遍历模式定义专门的迭代器
interface TreeIterator<T> extends Iterator<T> {}

class PreOrderIterator<T> implements TreeIterator<T> {
    private Stack<TreeNode<T>> stack;
    
    public PreOrderIterator(TreeNode<T> root) {
        stack = new Stack<>();
        stack.push(root);
    }
    
    @Override
    public boolean hasNext() {
        return !stack.isEmpty();
    }
    
    @Override
    public T next() {
        TreeNode<T> node = stack.pop();
        // 先压入右子树，再压入左子树（使左子树先出）
        if (node.right != null) stack.push(node.right);
        if (node.left != null) stack.push(node.left);
        return node.value;
    }
}

class InOrderIterator<T> implements TreeIterator<T> {
    private Stack<TreeNode<T>> stack = new Stack<>();
    private TreeNode<T> current;
    
    public InOrderIterator(TreeNode<T> root) {
        current = root;
    }
    
    @Override
    public boolean hasNext() {
        return current != null || !stack.isEmpty();
    }
    
    @Override
    public T next() {
        while (current != null) {
            stack.push(current);
            current = current.left;
        }
        current = stack.pop();
        T result = current.value;
        current = current.right;
        return result;
    }
}
```

### 问题4: 快照 vs 动态视图

**症状**:
- 迭代器返回的是集合当前状态的快照还是动态视图？
- 集合修改是否影响已创建的迭代器?

**解决方案**:

```java
// ✅ 快照方式 - 迭代列表当时的副本
class SnapshotIterator<T> implements Iterator<T> {
    private List<T> snapshot;
    private int index = 0;
    
    public SnapshotIterator(List<T> original) {
        this.snapshot = new ArrayList<>(original); // 深拷贝
    }
    
    @Override
    public boolean hasNext() {
        return index < snapshot.size();
    }
    
    @Override
    public T next() {
        return snapshot.get(index++);
    }
}

// ✅ 动态视图方式 - 始终反映集合当前状态
class DynamicViewIterator<T> implements Iterator<T> {
    private List<T> original;
    private int index = 0;
    
    public DynamicViewIterator(List<T> original) {
        this.original = original;
    }
    
    @Override
    public boolean hasNext() {
        return index < original.size();
    }
    
    @Override
    public T next() {
        if (index >= original.size()) {
            throw new NoSuchElementException();
        }
        return original.get(index++);
    }
}

// 选择合适的方式
List<String> list = new ArrayList<>();
// 快照 - 线程安全，但可能过时
Iterator<String> snapshot = new SnapshotIterator<>(list);
// 动态 - 实时但不安全
Iterator<String> dynamic = new DynamicViewIterator<>(list);
```

---

## 与其他模式的关系

| 模式 | 关系 | 何时结合 |
|--------|------|---------|
| **Composite** | 遍历树形结构 | 树的递归遍历 |
| **Factory** | 创建正确的迭代器 | 根据集合类型选择迭代器 |
| **Strategy** | 不同的遍历算法 | 支持多种遍历方式 |
| **Visitor** | 访问集合中的元素 | 结合迭代器遍历和元素操作 |
| **Observer** | 订阅集合变化 | 遍历时响应集合变化 |

---

## 最佳实践

### 1. 遵循Iterator接口
```java
// ✅ 实现标准接口
public class MyIterator implements Iterator<T> {
    @Override
    public boolean hasNext() { }
    
    @Override
    public T next() { }
    
    @Override
    public void remove() { }
}
```

### 2. 提供多种遍历方式
```java
// ✅ 为不同场景提供不同迭代器
class TreeNode<T> {
    Iterator<T> preOrder() { }
    Iterator<T> inOrder() { }
    Iterator<T> postOrder() { }
    Iterator<T> levelOrder() { }
}
```

### 3. 考虑fail-fast行为
```java
// ✅ 检测并发修改
class SafeIterator<T> implements Iterator<T> {
    private int modCount;
    private int expectedModCount;
    
    @Override
    public T next() {
        checkConcurrentModification();
        return ...;
    }
    
    private void checkConcurrentModification() {
        if (modCount != expectedModCount) {
            throw new ConcurrentModificationException();
        }
    }
}
```

---

## 何时避免使用

- ❌ **简单的for循环足够** - 不需要为此创建迭代器
- ❌ **单一遍历方式** - 直接遍历即可
- ❌ **性能关键** - 迭代器有额外开销

---

## 总结

迭代器模式通过提供统一的遍历接口，将集合的结构与遍历算法分离，提供了灵活的遍历机制。现代语言（如Java的Stream API、Python的生成器）已经内置了迭代器的强大功能，使该模式更容易使用。

