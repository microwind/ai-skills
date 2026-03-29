# Java编程 技术参考文档

## 概述

Java是面向对象的编程语言，以"一次编写，到处运行"的特点而闻名。从Java 8到Java 21的演进引入了函数式编程、记录类、文本块等现代特性，使得Java代码更加简洁和高效。

## 核心特性演进

### Java标准版选择

| 特性 | Java 8 | Java 11 | Java 17 | Java 21 |
|------|--------|---------|---------|---------|
| Stream API | ✓ | ✓ | ✓ | ✓ |
| Lambda | ✓ | ✓ | ✓ | ✓ |
| 模块系统 | ✗ | ✓ | ✓ | ✓ |
| var类型推导 | ✗ | ✓ | ✓ | ✓ |
| 文本块 | ✗ | ✗ | ✓ | ✓ |
| Records | ✗ | ✗ | ✓ | ✓ |
| 密封类 | ✗ | ✗ | ✓ | ✓ |
| Virtual Threads | ✗ | ✗ | ✗ | ✓ |

## 集合框架

### 集合层次结构

```
Collection
├── List (有序，可重复)
│   ├── ArrayList (增删慢，查询快)
│   ├── LinkedList (增删快，查询慢)
│   └── Vector (同步，已过时)
├── Set (无序，不重复)
│   ├── HashSet (无序，快速查询)
│   ├── TreeSet (有序，慢速查询)
│   └── LinkedHashSet (插入有序)
└── Queue (队列)
    ├── PriorityQueue (优先级队列)
    └── Deque (双端队列)

Map (键值对，键不重复)
├── HashMap (快速查询，无序)
├── TreeMap (有序查询，慢速)
├── LinkedHashMap (插入有序)
└── Hashtable (同步，已过时)
```

### 集合选择指南

| 场景 | 推荐容器 | 时间复杂度 |
|------|--------|----------|
| 频繁查询 | ArrayList或HashMap | O(1)* |
| 频繁插入删除 | LinkedList | O(1) |
| 需要排序 | TreeSet或TreeMap | O(log n) |
| 线程安全 | ConcurrentHashMap | O(1)* |
| 需要不重复元素 | HashSet | O(1)* |

*平均时间复杂度

### 初始化最佳实践

```java
// 指定初始容量避免扩容
List<String> list = new ArrayList<>(100);
Map<String, Integer> map = new HashMap<>(100);
Set<String> set = new HashSet<>(100);

// 导致多次扩容的不好做法
List<String> badList = new ArrayList<>();  // 初始容量10
for (int i = 0; i < 100000; i++) {
    badList.add("item" + i);  // 多次扩容
}
```

## 多线程和并发

### 线程创建

```java
// 方法1：继承Thread
class MyThread extends Thread {
    @Override
    public void run() {
        // 线程任务
    }
}
MyThread t = new MyThread();
t.start();

// 方法2：实现Runnable（推荐）
Thread t = new Thread(() -> {
    // 线程任务
});
t.start();

// 方法3：实现Callable（有返回值）
ExecutorService executor = Executors.newFixedThreadPool(4);
Future<Integer> future = executor.submit(() -> {
    return 42;
});
Integer result = future.get();  // 阻塞直到完成
```

### 同步机制

```java
// synchronized方法
synchronized void increment() {
    counter++;
}

// synchronized块（更灵活）
void process() {
    synchronized(this) {
        // 临界区
    }
}

// Lock接口（java.util.concurrent.locks）
Lock lock = new ReentrantLock();
lock.lock();
try {
    // 临界区
} finally {
    lock.unlock();
}
```

### 并发工具类

| 类 | 用途 | 场景 |
|-----|------|------|
| CountDownLatch | 等待多个线程完成 | 等待初始化完成 |
| CyclicBarrier | 等待多个线程到达同一点 | 循环同步 |
| Semaphore | 限制并发数 | 连接池、资源控制 |
| Phaser | 分阶段同步 | 多阶段任务 |

## Stream API深入

### Stream操作分类

```java
// 中间操作（返回Stream）
stream.filter(n -> n > 0)      // 过滤
      .map(n -> n * 2)          // 转换
      .distinct()               // 去重
      .sorted()                 // 排序
      .limit(10)                // 限制
      .skip(5)                  // 跳过
      .peek(System.out::println); // 观察

// 终端操作（消费Stream）
stream.collect(Collectors.toList());    // 收集为List
stream.collect(Collectors.toMap(...)    // 收集为Map
stream.forEach(System.out::println);    // 遍历
stream.reduce((a, b) -> a + b);         // 折叠
stream.count();                         // 计数
stream.findFirst();                     // 查找第一个
stream.anyMatch(n -> n > 10);           // 任意匹配
stream.allMatch(n -> n > 0);            // 全部匹配
```

### Stream性能考虑

```java
// 避免：多次创建Stream
list.stream().filter(...).count();
list.stream().map(...).collect(...);

// 优选：链式操作
list.stream()
    .filter(...)
    .map(...)
    .collect(...);

// 并行Stream需谨慎
list.parallelStream()              // 可能更慢！
    .filter(predicate)
    .collect(Collectors.toList());

// 性能测试前先确认必要性
```

## 现代Java特性

### Records（Java 14+，Java 16正式）
```java
record Point(int x, int y) {}  // 自动生成构造、equals、hashCode、toString

// 使用
Point p = new Point(1, 2);
System.out.println(p);  // Point[x=1, y=2]
```

### var类型推导（Java 10+）
```java
var list = new ArrayList<String>();  // 推导为List<String>
var count = 0;                         // 推导为int
for (var item : list) {  // item推导为String
    // ...
}
```

### 文本块（Java 13+）
```java
String json = """
    {
        "name": "John",
        "age": 30
    }
    """;

String sql = """
    SELECT id, name
    FROM users
    WHERE age > ?
    """;
```

### Sealed类（Java 17）
```java
sealed class Animal permits Dog, Cat { }
final class Dog extends Animal { }
final class Cat extends Animal { }
```

## 异常处理

### try-with-resources
```java
// 自动关闭资源
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        // 处理
    }
} catch (IOException e) {
    // 异常处理
}
// 资源自动关闭
```

### 多异常捕获
```java
try {
    // 代码
} catch (IOException | SQLException e) {  // 多个异常同时捕获
    // 处理
}
```

## 泛型编程

### 类型参数和类型边界

```java
// 简单泛型
class Box<T> {
    private T value;
    
    void set(T value) { this.value = value; }
    T get() { return value; }
}

// 类型边界
class NumberBox<T extends Number> {  // T必须是Number子类
    void process(T value) {
        // 可以调用Number的方法
    }
}

// 多重边界
class Complex<T extends Number & Comparable<T>> {
    // T既是Number也是Comparable
}

// 通配符
void process(List<?> list) { }                      // 任意类型
void processNumbers(List<? extends Number> list) { } // Number子类
void addNumbers(List<? super Integer> list) { }     // Integer超类
```

## 性能优化建议

### 1. 避免创建不必要的对象
```java
// 不好：在循环中创建对象
for (int i = 0; i < 1000; i++) {
    String s = new String("item");  // 1000个对象
}

// 更好
String item = "item";
for (int i = 0; i < 1000; i++) {
    // 使用item
}
```

### 2. String拼接优化
```java
// 不好：O(n²)时间复杂度
String result = "";
for (int i = 0; i < 10000; i++) {
    result += "text" + i;
}

// 更好：O(n)时间复杂度
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append("text").append(i);
}
String result = sb.toString();
```

### 3. 集合初始化
```java
// 避免频繁扩容
List<String> items = new ArrayList<>(10000);
Map<String, Integer> counts = new HashMap<>(10000);
```

### 4. 缓存频繁计算
```java
// 不好：重复计算
for (int i = 0; i < list.size(); i++) {  // 每次循环都调用size()
    // ...
}

// 更好：缓存size
int size = list.size();
for (int i = 0; i < size; i++) {
    // ...
}
```

## 编码规范清单

- [ ] 使用final修饰不可变对象
- [ ] 优先使用接口而不是具体类
- [ ] 异常处理应该具体明确
- [ ] 避免忽略异常
- [ ] 使用lombok或record减少冗余代码
- [ ] 正确使用equals和hashCode
- [ ] 避免过度同步
- [ ] 文档化公开API
- [ ] 提供单元测试
- [ ] 考虑Java版本兼容性
