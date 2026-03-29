---
name: 观察者模式
description: "定义对象间一对多的依赖关系，当对象状态改变时通知所有依赖者。在设计事件系统、MVC框架、响应式编程等场景中使用。"
license: MIT
---

# 观察者模式 (Observer Pattern)

## 概述

观察者模式定义了对象间的一对多依赖关系。当一个对象（称为Subject）的状态改变时，它的所有依赖者（称为Observers）都会自动收到通知并更新。

**核心原则**:
- 🎯 一对多订阅：一个发布者，多个订阅者
- 📢 自动通知：状态改变时主动通知所有观察者
- 🔌 松耦合：发布者和订阅者相互独立
- ⚙️ 动态关系：运行时动态添加/移除观察者

## 何时使用

### 完美适用场景

| 场景 | 说明 | 优先级 |
|------|------|--------|
| **事件处理系统** | GUI 按钮点击、文本变更等事件 | ⭐⭐⭐ |
| **MVC 架构** | Model 变更→View 自动更新 | ⭐⭐⭐ |
| **响应式编程** | 数据绑定、实时流处理 | ⭐⭐⭐ |
| **消息系统** | 消息队列、事件总线 | ⭐⭐⭐ |
| **属性变更通知** | 对象属性变化通知 | ⭐⭐ |
| **模型-视图绑定** | Web 框架中的数据绑定 | ⭐⭐⭐ |

### 触发信号（何时考虑使用）

✅ 以下信号表明应该使用观察者：
- "状态改变时需要通知多个对象"
- "对象间存在一对多的依赖关系"
- "需要松耦合的事件通知机制"
- "需要动态添加/移除监听器"
- "事件驱动的应用架构"

❌ 以下情况不应该使用：
- "只有单向的命令式调用"
- "通知链太长导致性能问题"
- "观察者间存在复杂的依赖"

## 观察者模式的优缺点

### 优点 ✅

1. **高度解耦**
   - 发布者和订阅者完全解耦
   - 可以独立修改
   - 易于单元测试

2. **动态关系**
   - 运行时动态添加/移除观察者
   - 支持一对多的灵活关系
   - 无需修改发布者代码

3. **自动通知**
   - 状态改变时自动通知
   - 不需要主动查询
   - 反应式编程的基础

4. **支持广播通信**
   - 一个消息发送给多个接收者
   - 简化事件处理逻辑
   - 易于实现事件总线

### 缺点 ❌

1. **无法控制通知顺序**
   - 多个观察者的通知顺序不确定
   - 可能导致竞态条件
   - 依赖关系复杂时难以调试

2. **内存泄漏风险**
   - ❌ 观察者未正确反注册会持有引用
   - ❌ 导致内存泄漏
   - ❌ 特别是在 Web/移动应用中

3. **性能问题**
   - 观察者过多时性能下降
   - 同步通知会阻塞发布者
   - 异步通知增加复杂性

4. **调试困难**
   - 控制流不明显
   - 难以追踪执行路径
   - 出现问题难以定位

## 观察者模式的 3 种实现方式

### 1️⃣ 推模式（Push）- 发布者主动推送数据 ⭐⭐⭐

发布者将状态数据直接传给观察者。

```java
/**
 * 推模式 - 发布者将状态数据推送给观察者
 * 优点: 观察者获取完整信息，无需查询
 * 缺点: 观察者必须接受所有发送的数据
 */

// 事件数据对象
public class StockEvent {
    private String stockCode;
    private double price;
    private double change;
    
    public StockEvent(String code, double price, double change) {
        this.stockCode = code;
        this.price = price;
        this.change = change;
    }
    
    // Getters...
}

// 观察者接口
public interface StockObserver {
    void onStockUpdate(StockEvent event);
}

// 具体观察者
public class InvestorObserver implements StockObserver {
    private String name;
    
    public InvestorObserver(String name) {
        this.name = name;
    }
    
    @Override
    public void onStockUpdate(StockEvent event) {
        System.out.printf("%s: 股票 %s 价格 %.2f, 涨幅 %.2f%%\n",
            name, event.getStockCode(), event.getPrice(), event.getChange());
    }
}

// 发布者
public class StockMarket {
    private List<StockObserver> observers = new ArrayList<>();
    
    public void attach(StockObserver observer) {
        observers.add(observer);
    }
    
    public void detach(StockObserver observer) {
        observers.remove(observer);
    }
    
    public void notifyObservers(String code, double price, double change) {
        StockEvent event = new StockEvent(code, price, change);
        for (StockObserver observer : observers) {
            observer.onStockUpdate(event);
        }
    }
}

// 使用
StockMarket market = new StockMarket();
StockObserver investor1 = new InvestorObserver("张三");
StockObserver investor2 = new InvestorObserver("李四");

market.attach(investor1);
market.attach(investor2);

market.notifyObservers("AAPL", 150.5, 2.5);  // 通知所有观察者
```

**特点**:
- ✅ 轻松获得完整数据
- ✅ 实现简单
- ❌ 发送不关心的数据浪费资源
- 🎯 **适合**: 数据更新需要完整信息的场景

---

### 2️⃣ 拉模式（Pull）- 观察者主动查询状态 ⭐⭐

发布者只通知观察者有更新，具体数据由观察者主动查询。

```java
/**
 * 拉模式 - 发布者仅通知更新，观察者主动查询
 * 优点: 观察者只获取需要的信息
 * 缺点: 观察者需要主动查询，增加复杂度
 */

public interface Subject {
    void attach(Observer observer);
    void detach(Observer observer);
    void notifyObservers();
    
    // 观察者查询的方法
    String getState();
}

public interface Observer {
    void update(Subject subject);  // 仅通知，不传数据
}

public class ConcreteSubject implements Subject {
    private String state;
    private List<Observer> observers = new ArrayList<>();
    
    @Override
    public void attach(Observer observer) {
        if (!observers.contains(observer)) {
            observers.add(observer);
        }
    }
    
    @Override
    public void detach(Observer observer) {
        observers.remove(observer);
    }
    
    @Override
    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(this);  // 只通知，传递 Subject 引用
        }
    }
    
    @Override
    public String getState() {
        return state;
    }
    
    public void setState(String newState) {
        this.state = newState;
        notifyObservers();
    }
}

public class ConcreteObserver implements Observer {
    private String name;
    
    public ConcreteObserver(String name) {
        this.name = name;
    }
    
    @Override
    public void update(Subject subject) {
        // 主动查询状态
        System.out.println(name + "观察到状态变更: " + subject.getState());
    }
}
```

**特点**:
- ✅ 观察者按需获取信息
- ✅ 减少数据传输
- ❌ 需要多次查询，性能一般
- 🎯 **适合**: 少量观察者关心少量数据的场景

---

### 3️⃣ 事件总线（Event Bus）- 中介者模式结合 ⭐⭐⭐

使用中央事件总线，解耦发布者和订阅者完全。

```java
/**
 * 事件总线模式 - 最灵活且最常用
 * 优点: 完全解耦发布者和订阅者，易于扩展
 * 缺点: 多了一个中介，稍微增加复杂度
 */

// 事件接口
public interface Event {}

// 具体事件
public class UserLoginEvent implements Event {
    public final String userId;
    public final String timestamp;
    
    public UserLoginEvent(String userId, String timestamp) {
        this.userId = userId;
        this.timestamp = timestamp;
    }
}

public class UserLogoutEvent implements Event {
    public final String userId;
    
    public UserLogoutEvent(String userId) {
        this.userId = userId;
    }
}

// 事件监听器
public interface EventListener {
    void onEvent(Event event);
}

// 事件总线
public class EventBus {
    private final Map<Class<?>, List<EventListener>> listeners = new ConcurrentHashMap<>();
    
    @SuppressWarnings("unchecked")
    public <T extends Event> void subscribe(Class<T> eventType, EventListener listener) {
        listeners.computeIfAbsent(eventType, k -> new CopyOnWriteArrayList<>())
                 .add(listener);
    }
    
    public <T extends Event> void unsubscribe(Class<T> eventType, EventListener listener) {
        List<EventListener> eventListeners = listeners.get(eventType);
        if (eventListeners != null) {
            eventListeners.remove(listener);
        }
    }
    
    public void publish(Event event) {
        List<EventListener> eventListeners = listeners.get(event.getClass());
        if (eventListeners != null) {
            for (EventListener listener : eventListeners) {
                listener.onEvent(event);
            }
        }
    }
}

// 使用
EventBus bus = new EventBus();

bus.subscribe(UserLoginEvent.class, event -> {
    System.out.println("用户 " + event.userId + " 登录");
});

bus.subscribe(UserLogoutEvent.class, event -> {
    System.out.println("用户 " + event.userId + " 登出");
});

// 发布事件
bus.publish(new UserLoginEvent("user123", "2024-03-29"));
bus.publish(new UserLogoutEvent("user123"));
```

**特点**:
- ✅ 完全解耦
- ✅ 高度灵活可扩展
- ✅ 现代化设计
- ✅ 支持多种事件类型
- 🎯 **最推荐的实现方式**

---

## 常见问题与解决方案

### 问题 1: 内存泄漏 - 观察者未反注册

**现象**: 应用内存不断增长，最终 OutOfMemory

**原因**: 观察者被添加后未被移除，发布者持有对观察者的强引用

**解决方案**:

```java
// ❌ 错误做法 - 强引用导致内存泄漏
public class View {
    private EventBus bus = new EventBus();
    
    public View() {
        bus.subscribe(UserEvent.class, (event) -> {
            update();
        });
        // 没有注销监听器，View 销毁时内存被占用
    }
}

// ✅ 正确做法1 - 显式注销
public class View implements Closeable {
    private EventBus bus;
    private EventListener listener;
    
    public View(EventBus bus) {
        this.bus = bus;
        this.listener = (event) -> update();
        bus.subscribe(UserEvent.class, listener);
    }
    
    @Override
    public void close() {
        bus.unsubscribe(UserEvent.class, listener);
    }
}

// ✅ 正确做法2 - 弱引用观察者
public class WeakObserverHolder<T extends Event> {
    private WeakReference<EventListener> listenerRef;
    private Class<T> eventType;
    
    public WeakObserverHolder(EventListener listener, Class<T> eventType) {
        this.listenerRef = new WeakReference<>(listener);
        this.eventType = eventType;
    }
    
    public void onEvent(Event event) {
        EventListener listener = listenerRef.get();
        if (listener != null) {
            listener.onEvent(event);
        }
    }
}

// ✅ 正确做法3 - 使用 try-with-resources
try (EventSubscription sub = bus.subscribe(UserEvent.class, listener)) {
    // 事件处理
}  // 自动注销
```

**最佳实践**: 
- 使用 try-with-resources 或显式 close() 方法
- 在 Activity/Fragment/Component 销毁时注销
- 考虑使用弱引用观察者

---

### 问题 2: 通知顺序不确定

**现象**: 多个观察者的通知顺序随意，导致依赖的业务逻辑出错

**解决方案**:

```java
// ❌ 错误做法 - 顺序不确定
eventBus.publish(new StateChangeEvent());  // 多个监听器顺序不确定

// ✅ 正确做法1 - 指定优先级
public class PriorityEventBus {
    private static class ListenerWrapper {
        int priority;
        EventListener listener;
    }
    
    public void subscribe(Class<?> eventType, EventListener listener, int priority) {
        // 按优先级排序
    }
}

// ✅ 正确做法2 - 顺序观察链
public class OrderedEventBus {
    public void publish(Event event, EventListener... listeners) {
        for (EventListener listener : listeners) {
            listener.onEvent(event);  // 按指定顺序执行
        }
    }
}

// ✅ 正确做法3 - 异步处理避免时序问题
public class AsyncEventBus {
    private ExecutorService executor = Executors.newFixedThreadPool(4);
    
    public void publishAsync(Event event) {
        executor.submit(() -> {
            // 异步处理，避免阻塞
        });
    }
}
```

---

### 问题 3: 性能问题 - 观察者过多

**现象**: 观察者增加后，通知性能明显下降

**原因**: 需要遍历所有观察者，如果观察者处理缓慢会阻塞发布者

**解决方案**:

```java
// ❌ 同步通知可能阻塞
for (Observer observer : observers) {
    observer.update(event);  // 如果某个观察者卡住，会阻塞所有后续观察者
}

// ✅ 使用线程池异步通知
ExecutorService executor = Executors.newFixedThreadPool(4);
for (Observer observer : observers) {
    executor.submit(() -> observer.update(event));
}

// ✅ 分组通知 - 将观察者分组，不同组并行处理
Map<String, List<Observer>> groupedObservers = observers.stream()
    .collect(Collectors.groupingBy(Observer::getGroup));

groupedObservers.forEach((group, listeners) -> {
    executor.submit(() -> {
        for (Observer observer : listeners) {
            observer.update(event);
        }
    });
});

// ✅ 性能计数 - 监控观察者执行时间
long startTime = System.nanoTime();
observer.update(event);
long duration = System.nanoTime() - startTime;
if (duration > 1_000_000_000) {  // 超过1秒
    logger.warn("观察者 {} 执行耗时 {}ms", observer.getClass(), duration / 1_000_000);
}
```

---

### 问题 4: 异常处理

**现象**: 一个观察者抛出异常，其他观察者不被通知

**解决方案**:

```java
// ❌ 错误做法 - 异常会中断后续通知
for (Observer observer : observers) {
    observer.update(event);  // 如果抛出异常，后续优先级下降的观察者无法执行
}

// ✅ 正确做法 - 为每个观察者独立处理异常
for (Observer observer : observers) {
    try {
        observer.update(event);
    } catch (Exception e) {
        logger.error("观察者 {} 处理事件时出错", observer.getClass().getName(), e);
        // 继续处理其他观察者
    }
}

// ✅ 最佳实践 - 使用异步处理隔离异常
ExecutorService executor = Executors.newCachedThreadPool();
for (Observer observer : observers) {
    executor.submit(() -> {
        try {
            observer.update(event);
        } catch (Exception e) {
            logger.error("观察者异常", e);
        }
    });
}
```

---

## 最佳实践 TOP 5

### 1. ✅ 明确发布者和订阅者的职责

```java
// 发布者 - 仅发布事件，不关心订阅者
public class UserService {
    private EventBus eventBus;
    
    public void registerUser(String username) {
        // ... 注册逻辑 ...
        eventBus.publish(new UserRegisteredEvent(username));
    }
}

// 订阅者 - 监听相关事件
eventBus.subscribe(UserRegisteredEvent.class, event -> {
    // 发送邮件等后续操作
    sendWelcomeEmail(event.username);
});
```

### 2. ✅ 使用强类型事件，避免字符串键

```java
// ❌ 避免这样做 - 容易出错
eventBus.publish("user.registered", userData);

// ✅ 使用强类型
eventBus.publish(new UserRegisteredEvent(userId));
```

### 3. ✅ 使用异步处理防止阻塞

```java
// 异步发布
public void publishAsync(Event event) {
    executor.submit(() -> {
        try {
            publish(event);
        } catch (Exception e) {
            logger.error("事件发布异常", e);
        }
    });
}
```

### 4. ✅ 提供反注册机制，防止内存泄漏

```java
// 使用 AutoCloseable 简化反注册
try (Subscription sub = eventBus.subscribe(UserEvent.class, listener)) {
    // 在这个作用域内监听事件
}  // 自动取消订阅
```

### 5. ✅ 监控和日志

```java
public class LoggingEventBus extends EventBus {
    @Override
    public void publish(Event event) {
        logger.info("发布事件: {}", event.getClass().getSimpleName());
        long startTime = System.nanoTime();
        super.publish(event);
        long duration = System.nanoTime() - startTime;
        logger.info("事件处理耗时: {}ms", duration / 1_000_000);
    }
}
```

---

## 与其他模式的关系

| 模式 | 关系 | 场景 |
|------|------|------|
| **Mediator** | 中介者是观察者的特例（中央控制） | 复杂对象间的通信 |
| **Command** | 可结合使用（命令作为事件） | 命令队列+事件通知 |
| **Strategy** | 观察者可使用不同策略处理 | 灵活事件处理 |
| **Model-View** | MVC 中核心模式 | 模型变更自动更新视图 |

---

## 性能对比

| 实现方式 | 通知延迟 | 内存占用 | 易用性 | 推荐场景 |
|---------|---------|--------|--------|---------|
| 推模式 | 最短 | 中等 | ⭐⭐⭐ | 简单事件 |
| 拉模式 | 较长 | 最低 | ⭐⭐ | 性能关键 |
| 事件总线 | 中等 | 中等 | ⭐⭐⭐ | **现代应用** |

---

## 何时应避免使用

❌ **以下情况不应使用观察者**:

1. **同步命令式调用足够**
   ```java
   // ✅ 简单场景，直接调用更清晰
   userService.register(user);
   emailService.send(user.getEmail());
   ```

2. **观察者链过长或循环依赖**
   ```java
   // ❌ 避免：A→B→C→...→A 的循环
   ```

3. **需要精确控制执行顺序**
   ```java
   // ❌ 观察者顺序不确定，不适合
   ```

---

**相关文件**:
- 应用规划: [forms.md](./forms.md)
- 完整参考: [reference.md](./reference.md)
```

## 典型应用场景

### 1. GUI 事件系统
```java
button.addEventListener("click", event -> {
    // 处理点击
});
```

### 2. MVC 框架
```java
// 模型变化通知视图
dataModel.addListener(view);
```

### 3. 异步任务通知
```java
task.addProgressListener(progressBar::update);
```

## 最佳实践

1. ✅ 使用弱引用避免内存泄漏
2. ✅ 提供 add/remove 观察者方法
3. ✅ 异常观察者不影响其他观察者
4. ✅ 文档说明通知顺序和内容

## Java 内置观察者

### Observable/Observer
```java
public class Model extends Observable {
    public void setState(String state) {
        setChanged();
        notifyObservers(state);
    }
}
```

### PropertyChangeListener
```java
bean.addPropertyChangeListener("name", evt -> {
    System.out.println("Name changed to " + evt.getNewValue());
});
```

## 何时避免使用

- 只有一个发布者和订阅者
- 通知关系简单
- 不需要解耦
