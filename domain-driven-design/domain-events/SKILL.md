---
name: 领域事件
description: "表示领域中发生的重要业务事件，用于聚合间通信和实现最终一致性。"
license: MIT
---

# 领域事件 (Domain Events)

## 概述

领域事件表示**领域中已经发生的重要业务事实**，是过去时态的描述。

**核心特征**：
- 已发生的事实（不可变）
- 命名用过去时态（OrderPlaced, PaymentCompleted）
- 包含事件发生时的关键数据
- 用于聚合间的松耦合通信

## 代码示例

```java
// 领域事件定义
public class OrderPlacedEvent {
    private final String orderId;
    private final String customerId;
    private final BigDecimal totalAmount;
    private final LocalDateTime occurredAt;

    public OrderPlacedEvent(String orderId, String customerId, BigDecimal totalAmount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.totalAmount = totalAmount;
        this.occurredAt = LocalDateTime.now();
    }
    // getters...
}

// 聚合根发布事件
public class Order {
    private List<DomainEvent> domainEvents = new ArrayList<>();

    public void place() {
        if (this.items.isEmpty()) throw new DomainException("订单不能为空");
        this.status = OrderStatus.PLACED;
        // 记录事件
        domainEvents.add(new OrderPlacedEvent(id, customerId, totalAmount));
    }

    public List<DomainEvent> getDomainEvents() {
        return Collections.unmodifiableList(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }
}

// 应用层发布事件
@Service
public class OrderApplicationService {
    public void placeOrder(PlaceOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.getOrderId());
        order.place();
        orderRepo.save(order);

        // 发布所有领域事件
        order.getDomainEvents().forEach(eventPublisher::publish);
        order.clearDomainEvents();
    }
}

// 事件处理器 — 其他上下文处理
@EventHandler
public class InventoryEventHandler {
    public void on(OrderPlacedEvent event) {
        inventoryService.reserveStock(event.getOrderId(), event.getItems());
    }
}

@EventHandler
public class NotificationEventHandler {
    public void on(OrderPlacedEvent event) {
        emailService.sendOrderConfirmation(event.getCustomerId(), event.getOrderId());
    }
}
```

```python
# Python 领域事件
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)  # 不可变
class OrderPlacedEvent:
    order_id: str
    customer_id: str
    total_amount: float
    occurred_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class PaymentCompletedEvent:
    order_id: str
    payment_id: str
    amount: float
    occurred_at: datetime = field(default_factory=datetime.now)

# 聚合根收集事件
class Order:
    def __init__(self):
        self._events = []

    def place(self):
        self.status = "PLACED"
        self._events.append(OrderPlacedEvent(
            order_id=self.id,
            customer_id=self.customer_id,
            total_amount=self.total
        ))

    def collect_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events
```

## 事件命名规范

```
✅ 正确：过去时态，描述已发生的事实
- OrderPlaced（订单已下单）
- PaymentCompleted（支付已完成）
- ItemShipped（商品已发货）
- AccountActivated（账户已激活）

❌ 错误：命令式或现在时
- PlaceOrder → 这是命令，不是事件
- ProcessingPayment → 这是进行中，不是完成
```

## 事件的用途

| 用途 | 说明 |
|------|------|
| 聚合间通信 | Order → 事件 → Inventory |
| 最终一致性 | 事务内改聚合，事务外发事件 |
| 审计日志 | 事件记录了所有重要业务变更 |
| [事件溯源](../event-sourcing/) | 用事件序列重建状态 |
| 通知 | 触发邮件、短信等通知 |
| 分析 | 事件流为数据分析提供原始数据 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [聚合根](../aggregate-root-design/) | 聚合根负责发布事件 |
| [限界上下文](../bounded-context/) | 事件用于上下文间通信 |
| [事件溯源](../event-sourcing/) | 事件作为持久化的基本单元 |
| [Saga模式](../saga-pattern/) | Saga 通过事件编排分布式事务 |
| [CQRS](../cqrs-pattern/) | 事件驱动读模型的更新 |

## 总结

**核心**：领域事件 = 已发生的业务事实，用于聚合间解耦通信。

**实践**：过去时态命名、不可变、聚合根发布、应用层分发、其他上下文订阅处理。
