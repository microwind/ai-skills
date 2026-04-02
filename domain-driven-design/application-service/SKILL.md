---
name: 应用服务
description: "应用层的服务，负责用例编排、事务管理和协调领域对象，不包含业务逻辑。"
license: MIT
---

# 应用服务 (Application Service)

## 概述

应用服务是**应用层的协调者**，负责编排领域对象完成一个完整的用例，但自身不包含业务逻辑。

**职责**：
- 接收外部请求（DTO/Command）
- 加载领域对象
- 调用领域对象的方法（业务逻辑在领域对象中）
- 管理事务
- 发布领域事件
- 返回结果（DTO）

## 代码示例

```java
@Service
@Transactional
public class OrderApplicationService {
    private final OrderRepository orderRepo;
    private final CustomerRepository customerRepo;
    private final EventPublisher eventPublisher;

    // 用例：下单
    public OrderDTO placeOrder(PlaceOrderCommand cmd) {
        // 1. 加载领域对象
        Customer customer = customerRepo.findById(cmd.getCustomerId())
            .orElseThrow(() -> new NotFoundException("客户不存在"));
        Order order = orderRepo.findById(cmd.getOrderId())
            .orElseThrow(() -> new NotFoundException("订单不存在"));

        // 2. 调用领域逻辑（逻辑在 Order 中）
        order.place();

        // 3. 持久化
        orderRepo.save(order);

        // 4. 发布事件
        order.getDomainEvents().forEach(eventPublisher::publish);
        order.clearDomainEvents();

        // 5. 返回 DTO
        return OrderDTO.from(order);
    }

    // 用例：取消订单
    public void cancelOrder(CancelOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.getOrderId())
            .orElseThrow(() -> new NotFoundException("订单不存在"));

        order.cancel(cmd.getReason());  // 业务逻辑在领域对象中

        orderRepo.save(order);
        order.getDomainEvents().forEach(eventPublisher::publish);
        order.clearDomainEvents();
    }
}
```

```python
class OrderApplicationService:
    def __init__(self, order_repo, customer_repo, event_publisher):
        self.order_repo = order_repo
        self.customer_repo = customer_repo
        self.event_publisher = event_publisher

    def place_order(self, cmd: PlaceOrderCommand) -> OrderDTO:
        customer = self.customer_repo.find_by_id(cmd.customer_id)
        if not customer:
            raise NotFoundError("客户不存在")

        order = self.order_repo.find_by_id(cmd.order_id)
        order.place()  # 业务逻辑在领域对象中

        self.order_repo.save(order)
        for event in order.collect_events():
            self.event_publisher.publish(event)

        return OrderDTO.from_domain(order)
```

## 应用服务 vs 领域服务

```
❌ 应用服务中写业务逻辑
public OrderDTO placeOrder(PlaceOrderCommand cmd) {
    Order order = orderRepo.findById(cmd.getOrderId());
    // 业务逻辑泄漏到应用层！
    if (order.getItems().isEmpty()) throw new Exception("订单为空");
    if (order.getStatus() != DRAFT) throw new Exception("状态错误");
    order.setStatus(PLACED);
    order.setTotalAmount(calculateTotal(order));
}

✅ 应用服务只做编排
public OrderDTO placeOrder(PlaceOrderCommand cmd) {
    Order order = orderRepo.findById(cmd.getOrderId());
    order.place();  // 所有业务逻辑在 Order 内部
    orderRepo.save(order);
}
```

| 维度 | 应用服务 | [领域服务](../domain-service/) |
|------|---------|---------|
| 层次 | 应用层 | 领域层 |
| 职责 | 编排用例流程 | 纯业务逻辑 |
| 事务 | 管理事务边界 | 不管事务 |
| 依赖 | Repository, EventPublisher | 只依赖领域对象 |
| 业务逻辑 | 不包含 | 包含（跨实体的） |

## 最佳实践

1. **应用服务是薄层** — 如果应用服务很厚，说明业务逻辑泄漏了
2. **一个方法 = 一个用例** — placeOrder, cancelOrder, shipOrder
3. **输入用 Command/DTO** — 不传领域对象给外部
4. **输出用 DTO** — 不直接返回领域对象

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [领域服务](../domain-service/) | 应用服务调用领域服务 |
| [仓储](../repository/) | 应用服务通过仓储加载/保存聚合 |
| [领域事件](../domain-events/) | 应用服务负责发布领域事件 |

## 总结

**核心**：应用服务 = 用例编排器，不含业务逻辑。

**模式**：加载对象 → 调用领域方法 → 保存 → 发布事件 → 返回DTO。
