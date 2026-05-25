---
name: 限界上下文
description: "领域模型的明确边界，同一术语在不同上下文中可以有不同含义，是DDD战略设计的核心。"
---

# 限界上下文 (Bounded Context)

## 概述

限界上下文是 DDD 战略设计最重要的概念：**一个明确的语义和模型边界，在这个边界内，特定的领域模型与通用语言保持一致且完整**。Eric Evans 强调，对大型系统进行"模型大一统"既不现实也不经济，应当显式地为每个模型划出适用边界。

**核心思想**：
- 同一个术语在不同上下文中含义不同（"订单"在销售、物流、财务中含义不同）
- 每个上下文有自己独立的模型、通用语言与团队所有权
- 上下文边界 = 团队边界 = 代码库 / 模块 / 微服务边界
- 边界的划分主要由"业务语言与组织文化"驱动，而非纯技术考量

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

上下文之间的协作方式由 [上下文映射](../context-mapping/) 模式决定，常见手段包括同步 RPC、异步事件，以及在需要"保护本上下文模型"时引入**防腐层（ACL）**：

```java
// 防腐层（ACL）：在边界处做模型转换，避免外部概念污染本上下文
public class InventoryAntiCorruptionLayer {
    private final InventoryServiceClient client;

    public boolean isAvailable(String productId, int quantity) {
        // 调用库存上下文的 API
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

DDD 共定义 9 种上下文映射模式（详见 [context-mapping](../context-mapping/)）：

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| Partnership（合作关系） | 双方相互依赖，共同规划与集成 | 不可独立成功的两个上下文 |
| Shared Kernel（共享内核） | 两个上下文共享一小部分模型，变更需双方协调 | 紧密协作、信任度高的团队 |
| Customer/Supplier（客户-供应商） | 上游团队把下游需求纳入规划 | 明确的上下游协作关系 |
| Conformist（追随者） | 下游放弃自己的模型，直接顺从上游模型 | 无法影响上游、且翻译成本过高 |
| Anticorruption Layer（防腐层） | 下游构建隔离层，做模型转换 | 与遗留系统或外部系统集成 |
| Open Host Service（开放主机服务） | 上游提供标准化协议，供多个下游消费 | 公共能力 / 平台型服务 |
| Published Language（发布语言） | 用文档化的共享语言（如 JSON Schema、Avro）通信 | 跨上下文 / 跨组织集成 |
| Separate Ways（各行其道） | 不集成，各自独立实现 | 无显著业务依赖 |
| Big Ball of Mud（大泥球） | 标记杂乱无章的遗留区域，防止其模型扩散 | 遗留系统的隔离与控制 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [通用语言](../ubiquitous-language/) | 每个限界上下文有自己的通用语言 |
| [上下文映射](../context-mapping/) | 描述上下文间的关系 |
| [领域模型](../domain-model/) | 领域模型在限界上下文内有效 |
| [聚合](../aggregate/) | 聚合存在于限界上下文内 |

## 总结

**核心**：限界上下文为模型与通用语言划定明确的适用边界，同一概念在不同上下文可以有不同含义。

**实践**：按业务语言 / 团队所有权 / 业务流程划分上下文，上下文间根据上下文映射模式（合作、共享内核、客户-供应商、防腐层、开放主机服务等）协同。
