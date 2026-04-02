---
name: 响应式编程
description: "基于异步数据流和变化传播的编程范式，用声明式方式处理事件流和异步操作。"
license: MIT
---

# 响应式编程 (Reactive Programming)

## 概述

响应式编程是一种**面向数据流和变化传播**的编程范式，将一切看作异步数据流（事件、消息、数据变化）。

**核心概念**：
- **Observable（可观察对象）**：数据流的源头
- **Observer（观察者）**：数据流的消费者
- **Operator（操作符）**：转换、过滤、组合数据流
- **Subscription（订阅）**：连接 Observable 和 Observer
- **Backpressure（背压）**：消费者控制生产速度

## 弹珠图 (Marble Diagram)

```
Observable:   --1--2--3--4--5--|
                 │
filter(x>2):  --------3--4--5--|
                 │
map(x*10):    --------30-40-50-|
                 │
Observer:     --------30-40-50-|

--  时间轴
|   完成
X   错误
```

## Java (Project Reactor)

```java
// ✅ 响应式处理异步数据流
Flux<Order> orders = orderRepository.findAll();  // 响应式数据源

orders
    .filter(order -> order.getStatus() == OrderStatus.PENDING)
    .map(order -> {
        order.process();
        return order;
    })
    .flatMap(order -> paymentService.charge(order))  // 异步调用
    .doOnNext(order -> log.info("处理完成: {}", order.getId()))
    .doOnError(error -> log.error("处理失败", error))
    .subscribe();

// 组合多个数据流
Mono<User> user = userService.findById(userId);
Mono<List<Order>> orders = orderService.findByUser(userId);

Mono.zip(user, orders)
    .map(tuple -> new UserDashboard(tuple.getT1(), tuple.getT2()))
    .subscribe(dashboard -> renderPage(dashboard));
```

## JavaScript (RxJS)

```typescript
import { fromEvent, interval, merge } from 'rxjs';
import { map, filter, debounceTime, switchMap, takeUntil } from 'rxjs/operators';

// 搜索框：防抖 + 取消前一个请求
const search$ = fromEvent<InputEvent>(searchInput, 'input').pipe(
    map(event => (event.target as HTMLInputElement).value),
    filter(query => query.length >= 2),
    debounceTime(300),                              // 300ms 防抖
    switchMap(query => fetch(`/api/search?q=${query}`)  // 取消前一个请求
        .then(r => r.json()))
);

search$.subscribe(results => renderResults(results));

// 实时数据流
const stockPrice$ = new WebSocket('ws://prices');
const ticker$ = fromEvent(stockPrice$, 'message').pipe(
    map(msg => JSON.parse(msg.data)),
    filter(price => price.symbol === 'AAPL'),
    map(price => price.value)
);

ticker$.subscribe(price => updateChart(price));
```

## Python (RxPY)

```python
import rx
from rx import operators as ops

# 数据处理管道
source = rx.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

source.pipe(
    ops.filter(lambda x: x % 2 == 0),
    ops.map(lambda x: x ** 2),
    ops.reduce(lambda acc, x: acc + x)
).subscribe(
    on_next=lambda result: print(f"结果: {result}"),
    on_error=lambda e: print(f"错误: {e}"),
    on_completed=lambda: print("完成")
)
```

## 背压 (Backpressure)

```java
// 生产者速度 > 消费者速度时的处理策略

Flux.range(1, 1000000)
    .onBackpressureBuffer(1000)    // 缓冲区
    // .onBackpressureDrop()       // 丢弃多余的
    // .onBackpressureLatest()     // 只保留最新的
    .subscribe(new BaseSubscriber<Integer>() {
        @Override
        protected void hookOnSubscribe(Subscription s) {
            request(10);  // 一次只请求10个
        }

        @Override
        protected void hookOnNext(Integer value) {
            process(value);
            request(10);  // 处理完再请求
        }
    });
```

## 何时使用

```
✅ 非常适合：
- UI 事件处理（点击、输入、滚动）
- 实时数据流（股票行情、消息推送）
- 异步 API 组合（多个服务并行调用）
- WebSocket 数据处理
- 搜索自动补全（防抖+取消）

❌ 不太适合：
- 简单的同步 CRUD
- 计算密集型任务
- 团队不熟悉响应式概念
```

## 优缺点

### ✅ 优点
1. **声明式** — 描述"做什么"而非"怎么做"
2. **组合性强** — 操作符自由组合
3. **天然异步** — 非阻塞，高吞吐
4. **背压支持** — 消费者控制速度

### ❌ 缺点
1. **学习曲线陡** — 需要转变思维方式
2. **调试困难** — 异步链路难以追踪
3. **错误处理复杂** — 异步错误传播不直观
4. **资源管理** — 需要正确取消订阅，避免内存泄漏

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [FP](../functional-programming/) | 响应式大量使用函数式操作符 |
| [并发编程](../concurrent-programming/) | 响应式是处理并发的高级抽象 |
| [OOP](../object-oriented-programming/) | Observable/Observer 是观察者模式的扩展 |

## 总结

**核心**：一切皆数据流，通过操作符声明式地处理异步事件。

**实践**：UI 事件用 RxJS，后端异步用 Reactor/RxJava，注意背压和取消订阅。
