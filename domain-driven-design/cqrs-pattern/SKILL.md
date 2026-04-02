---
name: CQRS模式
description: "命令查询责任分离，将数据的写入操作和读取操作分别用不同的模型处理，优化各自的性能。"
license: MIT
---

# CQRS 模式 (Command Query Responsibility Segregation)

## 概述

CQRS 将系统分为**命令端（写）和查询端（读）**，使用不同的模型处理各自的需求。

**核心思想**：
- 命令（Command）：改变系统状态，不返回数据
- 查询（Query）：返回数据，不改变状态
- 写模型为业务规则优化，读模型为查询性能优化

```
            ┌─────────────┐
     命令 → │  写模型      │ → 领域模型（充血、聚合、事务）
            │  (Command)   │ → 数据库（规范化）
            └─────────────┘
                    │ 事件/同步
                    ▼
            ┌─────────────┐
     查询 → │  读模型      │ → 查询优化的视图
            │  (Query)     │ → 数据库（反规范化）
            └─────────────┘
```

## 代码示例

```java
// 命令端：严格的领域模型
public class OrderCommandHandler {
    private final OrderRepository orderRepo;

    public void handle(PlaceOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.getOrderId());
        order.place();  // 领域逻辑
        orderRepo.save(order);
        // 发布事件 → 更新读模型
    }

    public void handle(CancelOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.getOrderId());
        order.cancel(cmd.getReason());
        orderRepo.save(order);
    }
}

// 查询端：为展示优化的模型
public class OrderQueryService {
    private final JdbcTemplate jdbc;

    // 直接查询优化后的视图，不走领域模型
    public OrderListDTO findOrders(OrderSearchCriteria criteria) {
        String sql = "SELECT o.id, o.status, c.name as customer_name, "
                   + "o.total_amount, o.created_at "
                   + "FROM order_view o JOIN customer c ON o.customer_id = c.id "
                   + "WHERE o.status = ? ORDER BY o.created_at DESC LIMIT ?";
        return jdbc.query(sql, criteria.getStatus(), criteria.getLimit());
    }

    public OrderDetailDTO findOrderDetail(String orderId) {
        // 从反规范化的视图中一次查出所有需要的数据
        return jdbc.queryForObject(
            "SELECT * FROM order_detail_view WHERE id = ?", orderId);
    }
}
```

```python
# 命令端
class PlaceOrderCommandHandler:
    def __init__(self, order_repo, event_publisher):
        self.order_repo = order_repo
        self.event_publisher = event_publisher

    def handle(self, cmd: PlaceOrderCommand):
        order = self.order_repo.find_by_id(cmd.order_id)
        order.place()
        self.order_repo.save(order)
        for event in order.collect_events():
            self.event_publisher.publish(event)

# 查询端
class OrderQueryService:
    def __init__(self, read_db):
        self.read_db = read_db

    def search_orders(self, filters: dict) -> list[OrderSummaryDTO]:
        """直接从读优化的视图查询"""
        return self.read_db.query("order_summary_view", filters)

# 读模型更新器（监听事件）
class OrderReadModelUpdater:
    def on_order_placed(self, event: OrderPlacedEvent):
        self.read_db.upsert("order_summary_view", {
            "id": event.order_id,
            "status": "PLACED",
            "customer_name": event.customer_name,
            "total": event.total_amount,
        })
```

## 何时使用 CQRS

```
✅ 适用场景：
- 读写比例悬殊（读多写少）
- 读和写的模型差异大
- 需要独立扩展读和写
- 需要复杂的查询（报表、搜索）

❌ 不适用场景：
- 简单的 CRUD 应用
- 读写模型几乎相同
- 团队不熟悉事件驱动
- 最终一致性不可接受
```

## CQRS 变体

| 变体 | 说明 | 复杂度 |
|------|------|--------|
| 同一数据库 | 写和读用同一个库的不同视图 | 低 |
| 独立数据库 | 写用关系数据库，读用 Elasticsearch/Redis | 中 |
| 事件溯源 + CQRS | 写端用事件，读端从事件投影 | 高 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [领域事件](../domain-events/) | 事件驱动读模型更新 |
| [事件溯源](../event-sourcing/) | 常与 CQRS 配合使用 |
| [读模型优化](../read-model-optimization/) | 读端的具体优化策略 |
| [聚合根](../aggregate-root-design/) | 命令端使用聚合模型 |

## 总结

**核心**：读写分离，各自优化。命令端用领域模型保证业务正确，查询端用反规范化视图保证性能。

**权衡**：增加了架构复杂度，换来了读写各自的可扩展性和性能。
