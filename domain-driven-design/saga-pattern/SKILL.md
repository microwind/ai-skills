---
name: Saga模式
description: "管理跨多个服务的分布式事务，通过编排或协调事件序列确保数据最终一致性。"
license: MIT
---

# Saga 模式 (Saga Pattern)

## 概述

Saga 模式用于管理**跨多个聚合或服务的长事务**，将大事务拆分为一系列本地事务，每个本地事务有对应的补偿操作。

```
正常流程：
T1(创建订单) → T2(扣减库存) → T3(扣款) → T4(确认订单)

补偿流程（T3 失败时）：
T3失败 → C2(恢复库存) → C1(取消订单)
```

## 两种实现方式

### 1. 编排式 Saga (Orchestration)

```java
// 中央协调器控制整个流程
public class OrderSagaOrchestrator {
    public void execute(CreateOrderCommand cmd) {
        String sagaId = UUID.randomUUID().toString();
        try {
            // Step 1: 创建订单
            Order order = orderService.create(cmd);

            // Step 2: 预留库存
            inventoryService.reserve(order.getItems());

            // Step 3: 扣款
            paymentService.charge(order.getCustomerId(), order.getTotal());

            // Step 4: 确认订单
            order.confirm();
            orderRepo.save(order);

        } catch (PaymentFailedException e) {
            // 补偿：恢复库存
            inventoryService.cancelReservation(cmd.getItems());
            // 补偿：取消订单
            orderService.cancel(cmd.getOrderId(), "支付失败");
            throw new SagaFailedException("下单失败：支付异常", e);

        } catch (InsufficientStockException e) {
            orderService.cancel(cmd.getOrderId(), "库存不足");
            throw new SagaFailedException("下单失败：库存不足", e);
        }
    }
}
```

### 2. 协同式 Saga (Choreography)

```python
# 每个服务监听事件并做出反应，没有中央协调器

# 订单服务
class OrderService:
    def create_order(self, data):
        order = Order.create(data)
        self.repo.save(order)
        self.events.publish(OrderCreatedEvent(order.id, order.items))

    def on_payment_completed(self, event: PaymentCompletedEvent):
        order = self.repo.find_by_id(event.order_id)
        order.confirm()
        self.repo.save(order)

    def on_payment_failed(self, event: PaymentFailedEvent):
        order = self.repo.find_by_id(event.order_id)
        order.cancel("支付失败")
        self.repo.save(order)

# 库存服务
class InventoryService:
    def on_order_created(self, event: OrderCreatedEvent):
        try:
            self.reserve_stock(event.items)
            self.events.publish(StockReservedEvent(event.order_id))
        except InsufficientStockError:
            self.events.publish(StockReservationFailedEvent(event.order_id))

    def on_payment_failed(self, event: PaymentFailedEvent):
        self.release_stock(event.order_id)  # 补偿

# 支付服务
class PaymentService:
    def on_stock_reserved(self, event: StockReservedEvent):
        try:
            self.charge(event.order_id)
            self.events.publish(PaymentCompletedEvent(event.order_id))
        except PaymentError:
            self.events.publish(PaymentFailedEvent(event.order_id))
```

## 编排 vs 协同

| 维度 | 编排式 | 协同式 |
|------|--------|--------|
| 控制方式 | 中央协调器 | 事件驱动，无中心 |
| 复杂度 | 流程集中管理 | 逻辑分散在各服务 |
| 耦合度 | 协调器依赖所有服务 | 服务间松耦合 |
| 可观测性 | 容易追踪流程 | 难以追踪全链路 |
| 适用场景 | 流程复杂、步骤多 | 流程简单、参与方少 |

## 最佳实践

1. **每个步骤都要有补偿操作** — 不可忽略
2. **补偿操作必须是幂等的** — 可能被重复执行
3. **记录 Saga 状态** — 便于排查和恢复
4. **设置超时** — 防止 Saga 永远挂起

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [领域事件](../domain-events/) | Saga 通过事件触发和通信 |
| [聚合根](../aggregate-root-design/) | 每个 Saga 步骤操作一个聚合 |
| [微服务中的DDD](../ddd-in-microservices/) | Saga 解决微服务间的分布式事务 |

## 总结

**核心**：将分布式事务拆分为本地事务序列 + 补偿操作。

**选择**：流程复杂用编排式，流程简单用协同式。
