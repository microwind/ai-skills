---
name: 微服务中的DDD
description: "将DDD战略设计应用于微服务架构，限界上下文指导服务拆分，领域事件实现服务间通信。"
license: MIT
---

# 微服务中的 DDD (DDD in Microservices)

## 概述

DDD 的战略设计天然适合微服务架构：**一个限界上下文 = 一个微服务**。

```
┌──────────┐  事件  ┌──────────┐  API  ┌──────────┐
│ 订单服务  │──────→│ 库存服务  │←─────│ 商品服务  │
│ Order BC │       │ Stock BC │      │Catalog BC│
│          │       │          │      │          │
│ 独立DB   │       │ 独立DB   │      │ 独立DB   │
└──────────┘       └──────────┘      └──────────┘
      │ 事件
      ▼
┌──────────┐       ┌──────────┐
│ 支付服务  │       │ 通知服务  │
│Payment BC│       │Notify BC │
└──────────┘       └──────────┘
```

## 服务拆分原则

```
✅ 按限界上下文拆分（推荐）
- 每个服务有独立的领域模型
- 每个服务有独立的数据库
- 服务边界 = 上下文边界 = 团队边界

❌ 按技术层拆分（不推荐）
- 用户服务、数据库服务、消息服务
- 一个业务变更需要改多个服务
```

### 从单体到微服务

```java
// 单体中的模块边界 → 未来的微服务边界

// module: order（未来的订单服务）
package com.shop.order;
public class OrderService { }
public interface OrderRepository { }  // 仓储接口
public class OrderPlacedEvent { }     // 领域事件

// module: inventory（未来的库存服务）
package com.shop.inventory;
public class InventoryService { }
public interface StockRepository { }

// 模块间通过接口通信，而非直接调用
// 迁移为微服务时，接口变为 API 调用
```

## 服务间通信

### 同步：API 调用（通过 ACL）

```java
// 订单服务调用库存服务
public class InventoryClient implements InventoryPort {
    private final RestTemplate rest;

    @Override
    public boolean checkStock(String sku, int quantity) {
        StockResponse response = rest.getForObject(
            "http://inventory-service/api/stock/{sku}", StockResponse.class, sku);
        return response.getAvailable() >= quantity;
    }
}
```

### 异步：领域事件（推荐）

```python
# 订单服务发布事件
class OrderService:
    def place_order(self, order):
        order.place()
        self.repo.save(order)
        self.message_broker.publish("order.placed", {
            "order_id": order.id,
            "items": [{"sku": i.sku, "qty": i.qty} for i in order.items]
        })

# 库存服务订阅事件
class InventoryEventHandler:
    def on_order_placed(self, event):
        for item in event["items"]:
            self.stock_service.reserve(item["sku"], item["qty"])
```

## 数据一致性

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| 事件驱动 | 发布事件，订阅方最终一致 | 大多数场景 |
| [Saga 模式](../saga-pattern/) | 编排/协同补偿事务 | 跨服务事务 |
| 同步调用 | API 直接调用 | 强一致性要求 |

## 微服务 DDD 检查清单

```
□ 每个服务对应一个限界上下文
□ 每个服务有独立的数据库（Database per Service）
□ 服务间不共享数据库表
□ 服务间通过 API 或事件通信，不直接访问对方数据
□ 每个服务有自己的领域模型，不共享领域对象
□ 使用防腐层隔离外部服务的模型
□ 分布式事务用 Saga 模式处理
```

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [限界上下文](../bounded-context/) | 一个上下文 = 一个微服务 |
| [上下文映射](../context-mapping/) | 指导服务间的集成模式 |
| [领域事件](../domain-events/) | 服务间异步通信的主要方式 |
| [Saga模式](../saga-pattern/) | 解决跨服务的分布式事务 |
| [六边形架构](../hexagonal-architecture/) | 每个微服务内部用六边形架构 |

## 总结

**核心**：限界上下文指导服务拆分，领域事件驱动服务通信，每个服务独立数据库。

**实践**：先在单体中划清模块边界（限界上下文），再按需拆分为微服务。
