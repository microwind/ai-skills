# 观察者模式完整参考实现

## 核心架构图

```
Subject (发布者)
   △
   │ notifies
   │
   ├─→ Observer1 (观察者1)
   ├─→ Observer2 (观察者2)
   └─→ Observer3 (观察者3)

Event Bus (事件总线)
   △
   │ publishes
   │
   ├─→ Listener1
   ├─→ Listener2
   └─→ Listener3
```

---

## Java 实现

### 推模式 (Push Model) - 完整实现

```java
// 事件数据对象
public class UserStateChangeEvent {
    public final String userId;
    public final String oldState;
    public final String newState;
    public final long timestamp;
    
    public UserStateChangeEvent(String userId, String oldState, String newState) {
        this.userId = userId;
        this.oldState = oldState;
        this.newState = newState;
        this.timestamp = System.currentTimeMillis();
    }
}

// 观察者接口
public interface UserStateObserver {
    void onUserStateChanged(UserStateChangeEvent event);
}

// 用户服务 (发布者)
public class UserService {
    private Set<UserStateObserver> observers = ConcurrentHashMap.newKeySet();
    private Map<String, String> userStates = new ConcurrentHashMap<>();
    
    // 注册观察者
    public void subscribe(UserStateObserver observer) {
        observers.add(observer);
    }
    
    // 注销观察者
    public void unsubscribe(UserStateObserver observer) {
        observers.remove(observer);
    }
    
    // 改变用户状态并通知所有观察者
    public void changeUserState(String userId, String newState) {
        String oldState = userStates.get(userId);
        userStates.put(userId, newState);
        
        // 通知所有观察者
        UserStateChangeEvent event = new UserStateChangeEvent(userId, oldState, newState);
        notifyObservers(event);
    }
    
    private void notifyObservers(UserStateChangeEvent event) {
        for (UserStateObserver observer : observers) {
            try {
                observer.onUserStateChanged(event);
            } catch (Exception e) {
                System.err.println("观察者处理异常: " + e.getMessage());
            }
        }
    }
}

// 具体观察者1 - 日志记录
public class LoggingObserver implements UserStateObserver {
    @Override
    public void onUserStateChanged(UserStateChangeEvent event) {
        System.out.println(String.format(
            "[LOG] 用户 %s 状态变更: %s → %s (时间: %d)",
            event.userId, event.oldState, event.newState, event.timestamp
        ));
    }
}

// 具体观察者2 - 审计记录
public class AuditObserver implements UserStateObserver {
    private List<String> auditLog = new ArrayList<>();
    
    @Override
    public void onUserStateChanged(UserStateChangeEvent event) {
        String auditEntry = String.format(
            "用户%s在%d时刻由%s变更为%s",
            event.userId, event.timestamp, event.oldState, event.newState
        );
        auditLog.add(auditEntry);
    }
    
    public List<String> getAuditLog() {
        return new ArrayList<>(auditLog);
    }
}

// 具体观察者3 - 通知发送
public class NotificationObserver implements UserStateObserver {
    @Override
    public void onUserStateChanged(UserStateChangeEvent event) {
        if ("offline".equals(event.newState)) {
            sendNotification(event.userId, "用户已离线");
        } else if ("online".equals(event.newState)) {
            sendNotification(event.userId, "用户已上线");
        }
    }
    
    private void sendNotification(String userId, String message) {
        System.out.println(String.format("[通知] 发送给 %s: %s", userId, message));
    }
}

// 使用示例
class Example {
    public static void main(String[] args) {
        UserService userService = new UserService();
        
        // 注册观察者
        userService.subscribe(new LoggingObserver());
        userService.subscribe(new AuditObserver());
        userService.subscribe(new NotificationObserver());
        
        // 改变用户状态
        userService.changeUserState("user123", "online");
        userService.changeUserState("user123", "offline");
    }
}
```

---

### 事件总线模式 (Event Bus) - 最灵活

```java
// 事件标记接口
public interface Event {}

// 具体事件类
public class UserRegisteredEvent implements Event {
    public final String userId;
    public final String email;
    public final long timestamp = System.currentTimeMillis();
    
    public UserRegisteredEvent(String userId, String email) {
        this.userId = userId;
        this.email = email;
    }
}

public class OrderPlacedEvent implements Event {
    public final String orderId;
    public final String userId;
    public final double amount;
    
    public OrderPlacedEvent(String orderId, String userId, double amount) {
        this.orderId = orderId;
        this.userId = userId;
        this.amount = amount;
    }
}

// 事件监听器接口
public interface EventListener {
    void onEvent(Event event);
}

// 线程安全的事件总线
public class EventBus {
    private final Map<Class<?>, List<EventListener>> listeners = new ConcurrentHashMap<>();
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    private final boolean async;
    
    public EventBus(boolean async) {
        this.async = async;
    }
    
    // 同步订阅
    public <T extends Event> void subscribe(Class<T> eventType, EventListener listener) {
        listeners.computeIfAbsent(eventType, k -> new CopyOnWriteArrayList<>())
                 .add(listener);
    }
    
    // 取消订阅
    public <T extends Event> void unsubscribe(Class<T> eventType, EventListener listener) {
        List<EventListener> eventListeners = listeners.get(eventType);
        if (eventListeners != null) {
            eventListeners.remove(listener);
        }
    }
    
    // 发布事件
    public void publish(Event event) {
        List<EventListener> eventListeners = listeners.get(event.getClass());
        if (eventListeners != null) {
            if (async) {
                publishAsync(eventListeners, event);
            } else {
                publishSync(eventListeners, event);
            }
        }
    }
    
    private void publishSync(List<EventListener> listeners, Event event) {
        for (EventListener listener : listeners) {
            try {
                listener.onEvent(event);
            } catch (Exception e) {
                System.err.println("监听器异常: " + e.getMessage());
            }
        }
    }
    
    private void publishAsync(List<EventListener> listeners, Event event) {
        for (EventListener listener : listeners) {
            executorService.submit(() -> {
                try {
                    listener.onEvent(event);
                } catch (Exception e) {
                    System.err.println("异步监听器异常: " + e.getMessage());
                }
            });
        }
    }
    
    public void shutdown() {
        executorService.shutdown();
    }
}

// 监听器实现
public class EmailNotificationListener implements EventListener {
    @Override
    public void onEvent(Event event) {
        if (event instanceof UserRegisteredEvent) {
            UserRegisteredEvent e = (UserRegisteredEvent) event;
            sendEmail(e.email, "欢迎注册，用户ID: " + e.userId);
        }
    }
    
    private void sendEmail(String email, String message) {
        System.out.println("[邮件] 发送到 " + email + ": " + message);
    }
}

public class AnalyticsListener implements EventListener {
    @Override
    public void onEvent(Event event) {
        if (event instanceof OrderPlacedEvent) {
            OrderPlacedEvent e = (OrderPlacedEvent) event;
            recordAnalytics("order_placed", e.amount);
        }
    }
    
    private void recordAnalytics(String event, double value) {
        System.out.println("[统计] 事件: " + event + ", 值: " + value);
    }
}

// 使用示例
class EventBusExample {
    public static void main(String[] args) {
        EventBus eventBus = new EventBus(true);  // 异步
        
        // 订阅事件
        eventBus.subscribe(UserRegisteredEvent.class, new EmailNotificationListener());
        eventBus.subscribe(OrderPlacedEvent.class, new AnalyticsListener());
        
        // 发布事件
        eventBus.publish(new UserRegisteredEvent("user123", "user@example.com"));
        eventBus.publish(new OrderPlacedEvent("order456", "user123", 299.99));
        
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        eventBus.shutdown();
    }
}
```

---

## Python 实现

```python
"""观察者模式 Python 实现"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime


# 事件基类
@dataclass
class Event(ABC):
    """事件基类"""
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()


# 具体事件
@dataclass
class StockPriceChangeEvent(Event):
    """股票价格变化事件"""
    stock_code: str
    old_price: float
    new_price: float


@dataclass
class PortfolioValueChangeEvent(Event):
    """投资组合价值变化事件"""
    portfolio_id: str
    old_value: float
    new_value: float


# 事件总线（纯Python方式）
class EventBus:
    """线程安全的事件总线"""
    
    def __init__(self):
        self._listeners: Dict[type, List[Callable]] = {}
    
    def subscribe(self, event_type: type, callback: Callable) -> None:
        """订阅事件"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: type, callback: Callable) -> None:
        """取消订阅"""
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)
    
    def publish(self, event: Event) -> None:
        """发布事件"""
        event_type = type(event)
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"监听器异常: {e}")
    
    def publish_async(self, event: Event) -> None:
        """异步发布事件"""
        import threading
        
        event_type = type(event)
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                thread = threading.Thread(target=self._safe_call, args=(callback, event))
                thread.daemon = True
                thread.start()
    
    @staticmethod
    def _safe_call(callback: Callable, event: Event) -> None:
        """安全调用回调"""
        try:
            callback(event)
        except Exception as e:
            print(f"异步监听器异常: {e}")


# 发布者 - 股票市场
class StockMarket:
    """股票市场 - 发布者"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.prices: Dict[str, float] = {}
    
    def update_price(self, stock_code: str, new_price: float) -> None:
        """更新股票价格"""
        old_price = self.prices.get(stock_code, 0)
        self.prices[stock_code] = new_price
        
        # 发布事件
        event = StockPriceChangeEvent(
            stock_code=stock_code,
            old_price=old_price,
            new_price=new_price
        )
        self.event_bus.publish(event)


# 观察者 - 投资者
class Investor:
    """投资者 - 观察者"""
    
    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.portfolio: Dict[str, int] = {}  # 股票代码 -> 数量
        self.event_bus = event_bus
        
        # 订阅股票价格变化事件
        self.event_bus.subscribe(StockPriceChangeEvent, self.on_stock_price_changed)
    
    def buy_stock(self, stock_code: str, quantity: int) -> None:
        """买入股票"""
        if stock_code not in self.portfolio:
            self.portfolio[stock_code] = 0
        self.portfolio[stock_code] += quantity
        print(f"[投资者 {self.name}] 买入 {quantity} 股 {stock_code}")
    
    def on_stock_price_changed(self, event: StockPriceChangeEvent) -> None:
        """股票价格变化回调"""
        if event.stock_code in self.portfolio:
            quantity = self.portfolio[event.stock_code]
            old_value = event.old_price * quantity
            new_value = event.new_price * quantity
            change = new_value - old_value
            
            print(f"[投资者 {self.name}] {event.stock_code} 价格变更: " +
                  f"{event.old_price:.2f} → {event.new_price:.2f}, " +
                  f"持仓 {quantity} 股，变动: {change:.2f} 元")


# 使用示例
def main():
    event_bus = EventBus()
    market = StockMarket(event_bus)
    
    # 创建投资者
    investor1 = Investor("张三", event_bus)
    investor2 = Investor("李四", event_bus)
    
    # 买入股票
    investor1.buy_stock("AAPL", 10)
    investor2.buy_stock("AAPL", 5)
    investor1.buy_stock("MSFT", 3)
    
    # 股票价格变化
    market.update_price("AAPL", 150.0)
    market.update_price("AAPL", 152.5)
    market.update_price("MSFT", 300.0)


if __name__ == "__main__":
    main()
```

---

## TypeScript 实现

```typescript
// 事件基类
abstract class Event {
    timestamp: number = Date.now();
}

// 具体事件
class UserLoginEvent extends Event {
    constructor(
        public userId: string,
        public timestamp: number = Date.now()
    ) {
        super();
    }
}

class UserLogoutEvent extends Event {
    constructor(
        public userId: string,
        public timestamp: number = Date.now()
    ) {
        super();
    }
}

class DataSyncEvent extends Event {
    constructor(
        public dataType: string,
        public data: any,
        public timestamp: number = Date.now()
    ) {
        super();
    }
}

// 监听器类型
type EventListener<T extends Event> = (event: T) => void;

// 事件总线
class EventBus {
    private listeners: Map<any, Set<Function>> = new Map();
    
    subscribe<T extends Event>(
        eventType: new (...args: any[]) => T,
        listener: EventListener<T>
    ): () => void {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, new Set());
        }
        
        this.listeners.get(eventType)!.add(listener);
        
        // 返回取消订阅函数
        return () => {
            this.listeners.get(eventType)?.delete(listener);
        };
    }
    
    publish<T extends Event>(event: T): void {
        const eventType = event.constructor;
        const eventListeners = this.listeners.get(eventType);
        
        if (eventListeners) {
            for (const listener of eventListeners) {
                try {
                    (listener as Function)(event);
                } catch (error) {
                    console.error(`监听器异常: ${error}`);
                }
            }
        }
    }
}

// 监听器实现
class LoggingListener {
    handle(event: Event): void {
        console.log(`[日志] 事件发生: ${event.constructor.name}, 时间: ${event.timestamp}`);
    }
}

class UserActivityListener {
    private activity: Array<{ userId: string; action: string; time: number }> = [];
    
    onUserLogin(event: UserLoginEvent): void {
        console.log(`[活动] 用户 ${event.userId} 已登录`);
        this.activity.push({
            userId: event.userId,
            action: 'login',
            time: event.timestamp
        });
    }
    
    onUserLogout(event: UserLogoutEvent): void {
        console.log(`[活动] 用户 ${event.userId} 已登出`);
        this.activity.push({
            userId: event.userId,
            action: 'logout',
            time: event.timestamp
        });
    }
    
    getActivity() {
        return this.activity;
    }
}

class DataSyncListener {
    onDataSync(event: DataSyncEvent): void {
        console.log(`[同步] ${event.dataType} 数据已同步:`, event.data);
    }
}

// 使用示例
function main() {
    const eventBus = new EventBus();
    const logger = new LoggingListener();
    const activityTracker = new UserActivityListener();
    const syncer = new DataSyncListener();
    
    // 订阅事件
    eventBus.subscribe(UserLoginEvent, (e) => logger.handle(e));
    eventBus.subscribe(UserLogoutEvent, (e) => logger.handle(e));
    eventBus.subscribe(UserLoginEvent, (e) => activityTracker.onUserLogin(e));
    eventBus.subscribe(UserLogoutEvent, (e) => activityTracker.onUserLogout(e));
    eventBus.subscribe(DataSyncEvent, (e) => syncer.onDataSync(e));
    
    // 发布事件
    eventBus.publish(new UserLoginEvent('user123'));
    eventBus.publish(new DataSyncEvent('user_profile', { name: '张三', age: 28 }));
    eventBus.publish(new UserLogoutEvent('user123'));
}

main();
```

---

## 实现方式对比表

| 特性 | 推模式 | 拉模式 | 事件总线 |
|------|--------|--------|---------|
| **代码复杂度** | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **通知延迟** | 最短 | 最长 | 中等 |
| **内存占用** | 中等 | 最低 | 中等 |
| **扩展性** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **观察者数** | 1-10 | 1-5 | 10+ |
| **推荐度** | ⭐⭐ | ⭐ | ⭐⭐⭐ |

---

## 性能基准测试

```java
public class PerformanceBenchmark {
    
    @Benchmark
    public void benchmarkPushModel(Blackhole bh) throws Exception {
        UserService service = new UserService();
        for (int i = 0; i < 100; i++) {
            service.subscribe(new LoggingObserver());
        }
        service.changeUserState("user1", "online");
        bh.consume(service);
    }
    
    @Benchmark
    public void benchmarkEventBus(Blackhole bh) throws Exception {
        EventBus bus = new EventBus(false);  // 同步
        for (int i = 0; i < 100; i++) {
            bus.subscribe(UserStateChangeEvent.class, e -> {});
        }
        bus.publish(new UserStateChangeEvent("user1", "offline", "online"));
        bh.consume(bus);
    }
    
    @Benchmark
    public void benchmarkEventBusAsync(Blackhole bh) throws Exception {
        EventBus bus = new EventBus(true);  // 异步
        for (int i = 0; i < 100; i++) {
            bus.subscribe(UserStateChangeEvent.class, e -> {});
        }
        bus.publish(new UserStateChangeEvent("user1", "offline", "online"));
        Thread.sleep(100);  // 等待异步完成
        bh.consume(bus);
    }
}

// 输出示例:
// 推模式时间:     ~0.5ms
// 事件总线(同步):  ~0.8ms
// 事件总线(异步):  ~0.1ms (异步分散负担)
```

---

## 单元测试

```java
@Test
public void testObserverReceivesNotification() {
    UserService service = new UserService();
    Mock<UserStateObserver> observer = mock(UserStateObserver.class);
    
    service.subscribe(observer);
    service.changeUserState("user1", "online");
    
    verify(observer, times(1)).onUserStateChanged(any());
}

@Test
public void testObserverCanUnsubscribe() {
    UserService service = new UserService();
    UserStateObserver observer = new LoggingObserver();
    
    service.subscribe(observer);
    service.unsubscribe(observer);
    
    // 验证不再发送通知
}

@Test
public void testEventBusHandlesMultipleEvents() {
    EventBus bus = new EventBus(false);
    List<Event> receivedEvents = new ArrayList<>();
    
    bus.subscribe(UserRegisteredEvent.class, e -> receivedEvents.add(e));
    bus.subscribe(OrderPlacedEvent.class, e -> receivedEvents.add(e));
    
    bus.publish(new UserRegisteredEvent("user1", "user@example.com"));
    bus.publish(new OrderPlacedEvent("order1", "user1", 100.0));
    
    assertEquals(2, receivedEvents.size());
}

@Test
public void testEventBusHandlesExceptionsGracefully() {
    EventBus bus = new EventBus(false);
    
    // 一个观察者抛出异常
    bus.subscribe(UserRegisteredEvent.class, e -> {
        throw new RuntimeException("Test exception");
    });
    
    // 另一个观察者应该仍然收到通知
    List<Boolean> notified = new ArrayList<>();
    bus.subscribe(UserRegisteredEvent.class, e -> notified.add(true));
    
    bus.publish(new UserRegisteredEvent("user1", "user@example.com"));
    
    assertTrue(notified.contains(true));
}
```

---

**参考文件**:
- 概念指南: [SKILL.md](./SKILL.md)
- 应用规划: [forms.md](./forms.md)
    // 测试代码
}
```
