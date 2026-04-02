---
name: 限界上下文
description: "领域模型的明确边界，同一术语在不同上下文中可以有不同含义，是DDD战略设计的核心。"
license: MIT
---

# 限界上下文 (Bounded Context)

## 概述

限界上下文是DDD战略设计最重要的概念：**一个明确的边界，在这个边界内，特定的领域模型是一致且完整的**。

**核心思想**：
- 同一个术语在不同上下文中含义不同（"订单"在销售、物流、财务中不同）
- 每个上下文有自己独立的模型
- 上下文边界 = 团队边界 = 代码库/模块边界

## 经典示例：电商系统

```
同一个"商品"在不同上下文的含义：

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   商品目录上下文   │  │   库存上下文      │  │   订单上下文      │
│                  │  │                  │  │                  │
│ Product:         │  │ StockItem:       │  │ OrderItem:       │
│  - name          │  │  - sku           │  │  - productId     │
│  - description   │  │  - quantity      │  │  - price         │
│  - images        │  │  - warehouse     │  │  - quantity      │
│  - categories    │  │  - reorderPoint  │  │  - discount      │
│  - price         │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘

每个上下文只关心自己需要的属性和行为
```

## 代码示例

```java
// 销售上下文中的 Product
package com.shop.catalog;

public class Product {
    private ProductId id;
    private String name;
    private String description;
    private List<Image> images;
    private Money price;
    private List<Category> categories;

    public void updatePrice(Money newPrice) { /* 定价逻辑 */ }
    public void publish() { /* 上架逻辑 */ }
}

// 库存上下文中的"商品" — 完全不同的模型
package com.shop.inventory;

public class StockItem {
    private String sku;
    private int quantity;
    private String warehouseId;
    private int reorderPoint;

    public void reserve(int amount) { /* 预留库存 */ }
    public boolean needsReorder() { return quantity <= reorderPoint; }
}

// 订单上下文中的"商品" — 又不同
package com.shop.order;

public class OrderLine {
    private String productId;  // 仅引用ID
    private Money unitPrice;   // 下单时的价格快照
    private int quantity;

    public Money subtotal() { return unitPrice.multiply(quantity); }
}
```

```python
# ✅ 每个上下文独立的模型

# 用户上下文：关注认证
class User:  # auth context
    def __init__(self, user_id, email, password_hash):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash

    def verify_password(self, password): ...
    def change_password(self, old, new): ...

# 客户上下文：关注个人信息
class Customer:  # customer context
    def __init__(self, customer_id, name, shipping_address, phone):
        self.customer_id = customer_id
        self.name = name
        self.shipping_address = shipping_address

    def update_address(self, new_address): ...

# 同一个人，不同上下文，不同模型
```

## 识别限界上下文

```
识别方法：

1. 语言边界：同一个词在不同场景含义不同
   "账户" → 认证上下文（登录凭证）vs 财务上下文（资金账户）

2. 团队边界：不同团队负责不同业务
   订单团队、支付团队、物流团队

3. 业务流程边界：不同的业务流程
   下单流程、支付流程、退货流程

4. 数据一致性边界：需要强一致性的范围
   一个上下文内强一致，上下文间最终一致
```

## 上下文间通信

```java
// 上下文之间通过防腐层（ACL）通信，不直接依赖

// 订单上下文需要库存信息，通过 ACL 转换
public class InventoryAntiCorruptionLayer {
    private final InventoryServiceClient client;

    public boolean isAvailable(String productId, int quantity) {
        // 调用库存上下文的API
        StockResponse response = client.checkStock(productId);
        // 转换为本上下文的概念
        return response.getAvailableQty() >= quantity;
    }
}

// 或通过领域事件异步通信
// 库存上下文发布事件
public class StockDepletedEvent {
    private String sku;
    private String warehouseId;
}

// 订单上下文订阅并处理
@EventHandler
public void onStockDepleted(StockDepletedEvent event) {
    // 标记相关商品为不可购买
}
```

## 上下文映射模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| 共享内核 | 两个上下文共享一部分模型 | 紧密协作的团队 |
| 客户-供应商 | 上游提供API，下游消费 | 明确的依赖关系 |
| 防腐层 | 在边界处做模型转换 | 与遗留系统集成 |
| 开放主机服务 | 提供标准化API | 多个下游消费者 |
| 发布语言 | 定义共享的数据格式 | 事件驱动集成 |
| 各行其道 | 不集成，完全独立 | 无依赖的系统 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [通用语言](../ubiquitous-language/) | 每个限界上下文有自己的通用语言 |
| [上下文映射](../context-mapping/) | 描述上下文间的关系 |
| [领域模型](../domain-model/) | 领域模型在限界上下文内有效 |
| [聚合](../aggregate/) | 聚合存在于限界上下文内 |

## 总结

**核心**：限界上下文为模型定义了明确的边界，同一概念在不同上下文有不同含义。

**实践**：按语言/团队/业务流程划分上下文，上下文间通过 ACL 或事件通信。
