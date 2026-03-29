---
name: Java编程
description: "当进行Java开发、性能优化、并发编程或设计模式应用时，分析代码质量和最佳实践。"
license: MIT
---

# Java编程技能

## 概述
Java是企业级应用开发的主流语言，从Java 8到Java 21的演进引入了大量现代特性。不同版本的Java在特性支持、性能、和编程范式上有显著差异。选择合适的特性和避免性能陷阱对于构建高质量应用至关重要。

**核心原则**: 好的Java代码应该清晰高效、资源管理清楚、并发安全、充分利用语言特性。坏的Java代码会内存泄漏、性能低下、难以维护。

## 何时使用

**始终:**
- Java项目代码审查
- 性能优化和调优
- 并发编程和线程安全分析
- 内存管理和GC优化
- 设计模式应用
- 框架集成和最佳实践

**触发短语:**
- "Java性能优化"
- "并发编程最佳实践"
- "Stream API用法"
- "Lambda表达式应用"
- "内存泄漏检测"
- "Java 8/11/21特性"

## Java编程技能功能

### 核心语言特性
- 类和接口设计
- 继承和多态
- 异常处理机制
- 泛型编程
- 注解和元数据

### Java 8特性（函数式编程）
- Lambda表达式
- 函数式接口
- Stream API
- Optional类型
- 方法引用

### Java 11及以后特性
- var局部变量类型推导
- 文本块（Text Blocks）
- 密封类（Sealed Classes）
- 记录类（Records）
- 模式匹配（Pattern Matching）

### 并发编程
- Thread和Runnable
- 同步机制（synchronized, Lock）
- 并发容器（ConcurrentHashMap等）
- 线程池和ExecutorService
- 内存模型和volatile

### 集合框架
- List, Set, Map使用
- 迭代器和遍历
- Collections工具类
- 性能特性（时间复杂度）
- 自定义集合

### I/O和资源管理
- try-with-resources
- Stream和Reader/Writer
- NIO和非阻塞I/O
- 文件操作
- 资源泄漏防护

## 常见问题

### 性能问题
- **问题**: String拼接性能
- **原因**: 循环中使用String +操作
- **解决**: 使用StringBuilder或StringBuffer

- **问题**: 集合初始化过小
- **原因**: 不设置初始容量导致频繁扩容
- **解决**: 根据预期数据量设置初始容量

- **问题**: 流慢速的I/O操作
- **原因**: 没有使用缓冲
- **解决**: 使用BufferedReader/BufferedWriter

### 并发问题
- **问题**: 竞态条件
- **原因**: 多线程访问共享数据没有同步
- **解决**: 使用synchronized、Lock或线程安全容器

- **问题**: 死锁
- **原因**: 获取锁的顺序不一致
- **解决**: 规定统一的锁获取顺序

- **问题**: 内存可见性问题
- **原因**: 没有使用volatile或happens-before关系
- **解决**: 正确使用同步机制建立happens-before关系

### 资源泄漏
- **问题**: 文件没有关闭
- **原因**: 异常时没有释放资源
- **解决**: 使用try-with-resources自动管理

## 代码示例

### Java 8 - Lambda和Stream
```java
import java.util.*;
import java.util.stream.*;

public class Java8Features {
    // Lambda表达式
    public void lambdaDemo() {
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
        
        // 使用lambda过滤和转换
        numbers.stream()
               .filter(n -> n % 2 == 0)
               .map(n -> n * n)
               .forEach(System.out::println);
    }
    
    // Stream API
    public void streamApiDemo() {
        List<String> words = Arrays.asList("hello", "world", "java", "stream");
        
        // 统计长度>3的单词
        long count = words.stream()
                          .filter(w -> w.length() > 3)
                          .count();
        System.out.println("Count: " + count);
        
        // 转换成包含长度的map
        Map<String, Integer> wordLengths = words.stream()
                                               .collect(Collectors.toMap(
                                                   Function.identity(),
                                                   String::length
                                               ));
    }
    
    // Optional处理null
    public void optionalDemo() {
        Optional<String> optional = Optional.of("Java");
        
        optional.ifPresent(System.out::println);
        String result = optional.orElse("Default");
        String mapped = optional.map(String::toUpperCase)
                               .orElse("EMPTY");
    }
}
```

### Java 11/ 17特性
```java
// Java 10+ - var类型推导
public class ModernJavaFeatures {
    public void varDemo() {
        var name = "Java";      // 推导为String
        var numbers = List.of(1, 2, 3);  // 推导为List<Integer>
        var map = new HashMap<String, Integer>();  // 推导为HashMap
        
        // 在循环中使用
        for (var num : numbers) {
            System.out.println(num);
        }
    }
    
    // Java 13+ - 文本块
    public String textBlockDemo() {
        String json = """
            {
                "name": "John",
                "age": 30,
                "city": "New York"
            }
            """;
        return json;
    }
    
    // Java 14+ - Records（数据类）
    public record Person(String name, int age, String email) {
        // 自动生成构造器、equals、hashCode、toString
        // 可以添加验证逻辑
        public Person {
            if (age < 0) throw new IllegalArgumentException("Age cannot be negative");
        }
    }
}
```

### 并发编程
```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ConcurrencyDemo {
    // 线程安全的计数器
    private AtomicInteger counter = new AtomicInteger(0);
    
    // 使用线程池
    public void threadPoolDemo() {
        ExecutorService executor = Executors.newFixedThreadPool(4);
        
        for (int i = 0; i < 10; i++) {
            final int taskId = i;
            executor.execute(() -> {
                System.out.println("Task " + taskId + " running");
                counter.incrementAndGet();
            });
        }
        
        executor.shutdown();
        try {
            executor.awaitTermination(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    // 使用CountDownLatch等待多个任务
    public void countDownLatchDemo() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3);
        
        for (int i = 0; i < 3; i++) {
            final int taskId = i;
            new Thread(() -> {
                System.out.println("Task " + taskId + " starting");
                try {
                    Thread.sleep(100);
                    System.out.println("Task " + taskId + " done");
                } finally {
                    latch.countDown();
                }
            }).start();
        }
        
        latch.await();  // 等待所有任务完成
        System.out.println("All tasks completed");
    }
    
    // 同步化访问
    public synchronized void synchronizedMethod() {
        counter.incrementAndGet();
    }
    
    // Lock接口
    private final Object lock = new Object();
    public void lockDemo() {
        synchronized (lock) {
            counter.incrementAndGet();
        }
    }
}
```

### 资源管理和异常处理
```java
import java.io.*;
import java.nio.file.*;

public class ResourceManmentation {
    // try-with-resources 自动管理资源
    public String readFileModern(String filename) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            return reader.lines()
                        .collect(Collectors.joining("\n"));
        }
    }
    
    // 多个资源管理
    public void multipleResourcesDemo() throws IOException {
        try (
            FileReader reader = new FileReader("input.txt");
            FileWriter writer = new FileWriter("output.txt")
        ) {
            // 使用reader和writer
            char[] buffer = new char[1024];
            int bytesRead;
            while ((bytesRead = reader.read(buffer)) != -1) {
                writer.write(buffer, 0, bytesRead);
            }
        }
        // 资源自动关闭
    }
    
    // 自定义AutoCloseable资源
    public static class DatabaseConnection implements AutoCloseable {
        private String connectionString;
        
        public DatabaseConnection(String connStr) {
            this.connectionString = connStr;
            System.out.println("Opening connection to " + connStr);
        }
        
        @Override
        public void close() {
            System.out.println("Closing connection");
        }
        
        public void execute(String sql) {
            System.out.println("Executing: " + sql);
        }
    }
    
    // 使用自定义资源
    public void customResource (final int taskId = i;
            executor.execute(() -> {
                System.out.println("Task " + taskId + " running");
                counter.incrementAndGet();
            });
        }
        
        executor.shutdown();
    }
    
    public static void main(String[] args) throws Exception {
        try (DatabaseConnection conn = new DatabaseConnection("jdbc:mysql://localhost/mydb")) {
            conn.execute("SELECT * FROM users");
        }
        // 连接自动关闭
    }
}
```

### 集合框架性能考虑
```java
import java.util.*;

public class CollectionPerformance {
    // 选择合适的集合类
    public void collectionChoiceDemo() {
        // List - 有序，可重复
        List<String> list = new ArrayList<>(100);  // 指定容量避免扩容
        list.add("item1");
        list.add("item2");
        
        // Set - 无序，不重复
        Set<String> set = new HashSet<>(100);  // 指定容量
        set.add("item1");
        set.add("item2");
        
        // Map - 键值对
        Map<String, Integer> map = new HashMap<>(100);
        map.put("key1", 1);
        map.put("key2", 2);
        
        // 线程安全的集合
        Map<String, Integer> concurrent = new ConcurrentHashMap<>();
        concurrent.putIfAbsent("key", 1);
    }
    
    // 迭代方式的性能考虑
    public void iterationDemo(List<String> items) {
        // 最快 - 直接索引
        for (int i = 0; i < items.size(); i++) {
            System.out.println(items.get(i));
        }
        
        // 推荐 - 增强for循环
        for (String item : items) {
            System.out.println(item);
        }
        
        // 通用 - 迭代器
        for (Iterator<String> it = items.iterator(); it.hasNext(); ) {
            System.out.println(it.next());
        }
        
        // 函数式 - 可读性好但可能有额外开销
        items.forEach(System.out::println);
    }
}
```
