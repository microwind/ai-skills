---
name: 事件驱动架构
description: "基于事件的异步通信架构，组件通过发布和订阅事件来交互，实现松耦合和高可扩展性。"
license: MIT
---

# 事件驱动架构 (Event-Driven Architecture, EDA)

## 概述

事件驱动架构中，组件通过**发布和订阅事件**来通信，而非直接调用。

```
传统：同步调用链
OrderService → InventoryService → PaymentService → NotificationService

事件驱动：发布-订阅
OrderService ──publish──→ [Event Bus] ──subscribe──→ InventoryService
                                      ──subscribe──→ PaymentService
                                      ──subscribe──→ NotificationService
```

## 事件类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 领域事件 | 业务中发生的事实 | OrderPlaced, PaymentCompleted |
| 集成事件 | 跨服务通信的事件 | 包含其他服务需要的数据 |
| 通知事件 | 仅通知，不含详细数据 | OrderChanged（接收方需要回查） |
| 事件携带状态转移 | 包含完整状态变更 | OrderPlaced + 所有订单详情 |

## 代码示例

```java
// 事件定义
public class OrderPlacedEvent {
    private final String orderId;
    private final String customerId;
    private final List<OrderItemDTO> items;
    private final BigDecimal totalAmount;
    private final Instant occurredAt;
}

// 发布者
@Service
public class OrderService {
    private final EventPublisher eventPublisher;

    public void placeOrder(Order order) {
        order.place();
        orderRepo.save(order);
        eventPublisher.publish(new OrderPlacedEvent(
            order.getId(), order.getCustomerId(),
            order.getItems(), order.getTotal()
        ));
    }
}

// 订阅者 — 各自独立处理
@Component
public class InventoryHandler {
    @EventListener
    public void on(OrderPlacedEvent event) {
        for (var item : event.getItems()) {
            inventoryService.reserve(item.getSku(), item.getQuantity());
        }
    }
}

@Component
public class NotificationHandler {
    @EventListener
    public void on(OrderPlacedEvent event) {
        emailService.sendOrderConfirmation(event.getCustomerId(), event.getOrderId());
    }
}

@Component
public class AnalyticsHandler {
    @EventListener
    public void on(OrderPlacedEvent event) {
        analyticsService.trackOrder(event.getOrderId(), event.getTotalAmount());
    }
}
```

```python
# Python 事件驱动
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event_type: str, handler):
        self._handlers[event_type].append(handler)

    def publish(self, event_type: str, data: dict):
        for handler in self._handlers[event_type]:
            handler(data)

# 使用
bus = EventBus()
bus.subscribe("order.placed", lambda e: reserve_stock(e["items"]))
bus.subscribe("order.placed", lambda e: send_email(e["customer_id"]))
bus.subscribe("order.placed", lambda e: track_analytics(e))

# 发布一个事件，三个处理器各自执行
bus.publish("order.placed", {"order_id": "123", "items": [...], "customer_id": "456"})
```

## 消息中间件选择

| 中间件 | 特点 | 适用场景 |
|--------|------|---------|
| Kafka | 高吞吐、持久化、回放 | 大规模事件流 |
| RabbitMQ | 灵活路由、确认机制 | 任务队列、RPC |
| Redis Streams | 轻量、低延迟 | 简单事件通知 |
| AWS SNS/SQS | 托管服务、易扩展 | 云原生应用 |

## EDA 模式

### 1. 事件通知 (Event Notification)

```
发送简单通知，接收方按需回查详情
OrderService → { event: "order.placed", orderId: "123" } → InventoryService
InventoryService 收到后调 OrderService API 获取详情
```

### 2. 事件携带状态转移 (Event-Carried State Transfer)

```
事件包含完整数据，接收方无需回查
OrderService → { event: "order.placed", orderId: "123", items: [...], total: 999 }
InventoryService 直接使用事件中的数据
```

## 优缺点

### ✅ 优点
1. **松耦合** — 发布者不知道谁订阅
2. **可扩展** — 新增订阅者无需修改发布者
3. **弹性** — 订阅者故障不影响发布者
4. **异步** — 非阻塞，提高吞吐

### ❌ 缺点
1. **最终一致性** — 非实时，有延迟
2. **调试困难** — 事件链路追踪复杂
3. **消息顺序** — 可能乱序到达
4. **幂等性** — 消费者必须处理重复消息

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [领域事件](../domain-events/) | EDA 的基础是领域事件 |
| [CQRS](../cqrs-pattern/) | 事件驱动更新读模型 |
| [Saga模式](../saga-pattern/) | 通过事件编排分布式事务 |
| [微服务中的DDD](../ddd-in-microservices/) | 事件是微服务间通信的推荐方式 |

## 总结

**核心**：通过事件发布-订阅实现组件间松耦合的异步通信。

**实践**：定义清晰的事件契约，保证消费者幂等，使用消息中间件可靠投递，做好事件链路追踪。
