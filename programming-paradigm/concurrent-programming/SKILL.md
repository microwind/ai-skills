---
name: 并发编程
description: "多线程、异步和并行处理的编程范式，解决并发安全、同步和协调问题。"
license: MIT
---

# 并发编程 (Concurrent Programming)

## 概述

并发编程处理**多个任务的同时执行**，核心挑战是共享状态的安全访问和任务间的协调。

**关键概念**：
- **并发 (Concurrency)**：多个任务交替执行（一个CPU）
- **并行 (Parallelism)**：多个任务真正同时执行（多个CPU）
- **异步 (Asynchronous)**：非阻塞地等待结果

## 常见并发问题

### 1. 竞态条件 (Race Condition)

```java
// ❌ 竞态条件
public class Counter {
    private int count = 0;

    public void increment() {
        count++;  // 非原子操作：读-改-写
        // 线程A读count=5, 线程B读count=5
        // 两个都写6，实际应该是7
    }
}

// ✅ 线程安全
public class Counter {
    private final AtomicInteger count = new AtomicInteger(0);

    public void increment() {
        count.incrementAndGet();  // 原子操作
    }
}
```

### 2. 死锁 (Deadlock)

```java
// ❌ 死锁：两个线程互相等待
Object lockA = new Object();
Object lockB = new Object();

// 线程1: 锁A → 等锁B
new Thread(() -> {
    synchronized(lockA) {
        synchronized(lockB) { /* ... */ }
    }
}).start();

// 线程2: 锁B → 等锁A
new Thread(() -> {
    synchronized(lockB) {
        synchronized(lockA) { /* ... */ }  // 死锁！
    }
}).start();

// ✅ 避免死锁：固定锁顺序
// 所有线程都先锁A再锁B
```

## Java 并发

```java
// CompletableFuture：组合异步操作
CompletableFuture<User> userFuture = userService.findByIdAsync(userId);
CompletableFuture<List<Order>> ordersFuture = orderService.findByUserAsync(userId);

// 并行执行两个查询
CompletableFuture.allOf(userFuture, ordersFuture)
    .thenApply(v -> new Dashboard(userFuture.join(), ordersFuture.join()))
    .thenAccept(dashboard -> render(dashboard));

// Virtual Threads (Java 21+)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> futures = urls.stream()
        .map(url -> executor.submit(() -> fetchUrl(url)))
        .toList();

    List<String> results = futures.stream()
        .map(f -> f.get())
        .toList();
}
```

## Python 并发

```python
import asyncio

# asyncio：协程
async def fetch_user(user_id: str) -> dict:
    await asyncio.sleep(0.1)  # 模拟网络请求
    return {"id": user_id, "name": "Alice"}

async def fetch_orders(user_id: str) -> list:
    await asyncio.sleep(0.2)
    return [{"id": "1", "total": 100}]

async def get_dashboard(user_id: str):
    # 并行执行
    user, orders = await asyncio.gather(
        fetch_user(user_id),
        fetch_orders(user_id)
    )
    return {"user": user, "orders": orders}

asyncio.run(get_dashboard("123"))

# ThreadPoolExecutor：线程池
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_url(url: str) -> str:
    return requests.get(url).text

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_url, url): url for url in urls}
    for future in as_completed(futures):
        result = future.result()
```

## TypeScript 并发

```typescript
// Promise.all：并行执行
async function getDashboard(userId: string) {
    const [user, orders, notifications] = await Promise.all([
        fetchUser(userId),
        fetchOrders(userId),
        fetchNotifications(userId)
    ]);
    return { user, orders, notifications };
}

// Promise.allSettled：所有完成（不管成功失败）
const results = await Promise.allSettled([
    fetchCriticalData(),
    fetchOptionalData()
]);

results.forEach(result => {
    if (result.status === 'fulfilled') {
        console.log('成功:', result.value);
    } else {
        console.log('失败:', result.reason);
    }
});
```

## 并发模型对比

| 模型 | 原理 | 适用场景 | 语言 |
|------|------|---------|------|
| 线程 + 锁 | 共享内存，锁同步 | 通用 | Java, C++ |
| Actor 模型 | 消息传递，无共享状态 | 分布式系统 | Erlang, Akka |
| CSP | 通过 Channel 通信 | 并发编排 | Go |
| 协程 | 协作式调度，轻量 | I/O 密集 | Python, Kotlin |
| 虚拟线程 | 轻量线程，阻塞不浪费OS线程 | 高并发服务 | Java 21+ |
| 事件循环 | 单线程 + 回调 | I/O 密集 | Node.js |

## 最佳实践

1. **优先不可变数据** — 不可变对象天然线程安全
2. **最小化共享状态** — 能不共享就不共享
3. **使用高级抽象** — CompletableFuture / asyncio 而非裸线程
4. **避免锁嵌套** — 降低死锁风险
5. **使用线程池** — 不要无限制创建线程

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [FP](../functional-programming/) | 不可变数据天然并发安全 |
| [响应式](../reactive-programming/) | 响应式是并发的高级抽象 |
| [OOP](../object-oriented-programming/) | 需要注意对象的线程安全 |

## 总结

**核心**：安全地管理共享状态，高效地协调并行任务。

**实践**：优先不可变 → 最小化共享 → 使用高级并发抽象 → 注意死锁和竞态。
