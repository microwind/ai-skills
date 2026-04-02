---
name: 领域模型
description: "业务领域的抽象表示，捕获核心业务概念、规则和行为，是DDD的核心构建块。"
license: MIT
---

# 领域模型 (Domain Model)

## 概述

领域模型是对业务领域的**软件化抽象**，它捕获了业务概念、规则和行为，而非数据库表结构或UI字段。

**核心思想**：
- 领域模型反映业务专家的心智模型
- 模型应该包含行为（方法），而非仅有数据（属性）
- 领域模型独立于技术实现（数据库、框架）

## 贫血模型 vs 充血模型

```java
// ❌ 贫血模型：只有getter/setter，没有业务逻辑
public class Order {
    private Long id;
    private List<OrderItem> items;
    private OrderStatus status;
    private BigDecimal totalAmount;

    // 一堆 getter/setter...
}

// 业务逻辑散落在 Service 中
public class OrderService {
    public void confirmOrder(Order order) {
        if (order.getStatus() != OrderStatus.PENDING) {
            throw new IllegalStateException("只有待处理订单可以确认");
        }
        BigDecimal total = BigDecimal.ZERO;
        for (OrderItem item : order.getItems()) {
            total = total.add(item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())));
        }
        order.setTotalAmount(total);
        order.setStatus(OrderStatus.CONFIRMED);
    }
}

// ✅ 充血模型：数据和行为在一起
public class Order {
    private OrderId id;
    private List<OrderItem> items;
    private OrderStatus status;
    private Money totalAmount;

    public void confirm() {
        if (status != OrderStatus.PENDING) {
            throw new DomainException("只有待处理订单可以确认");
        }
        this.totalAmount = calculateTotal();
        this.status = OrderStatus.CONFIRMED;
    }

    public void addItem(Product product, int quantity) {
        if (status != OrderStatus.DRAFT) {
            throw new DomainException("只有草稿订单可以添加商品");
        }
        if (quantity <= 0) {
            throw new DomainException("数量必须为正数");
        }
        items.add(new OrderItem(product, quantity));
    }

    public void cancel(String reason) {
        if (!status.isCancellable()) {
            throw new DomainException("当前状态不允许取消");
        }
        this.status = OrderStatus.CANCELLED;
    }

    private Money calculateTotal() {
        return items.stream()
            .map(OrderItem::subtotal)
            .reduce(Money.ZERO, Money::add);
    }
}
```

## Python 充血模型

```python
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

class OrderStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class DomainError(Exception):
    pass

@dataclass
class Order:
    id: str
    customer_id: str
    items: list = field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT

    def add_item(self, product, quantity: int):
        if self.status != OrderStatus.DRAFT:
            raise DomainError("只有草稿订单可以添加商品")
        self.items.append(OrderItem(product, quantity))

    def submit(self):
        if not self.items:
            raise DomainError("订单不能为空")
        if self.status != OrderStatus.DRAFT:
            raise DomainError("只有草稿订单可以提交")
        self.status = OrderStatus.PENDING

    def confirm(self):
        if self.status != OrderStatus.PENDING:
            raise DomainError("只有待处理订单可以确认")
        self.status = OrderStatus.CONFIRMED

    @property
    def total(self) -> Decimal:
        return sum(item.subtotal for item in self.items)
```

## 领域模型构建步骤

```
1. 与领域专家沟通，理解业务流程
2. 识别核心概念（名词 → 实体/值对象）
3. 识别业务规则（动词 → 方法）
4. 确定聚合边界（一致性边界）
5. 定义领域事件（重要的业务发生）
6. 持续精化，随理解加深而演进
```

## 领域模型的特征

| 特征 | 说明 |
|------|------|
| 表达业务语言 | 方法名和类名反映业务术语 |
| 包含业务规则 | 验证和约束在模型内部 |
| 技术无关 | 不依赖数据库、HTTP、框架 |
| 自我保护 | 不允许进入非法状态 |
| 可测试 | 纯业务逻辑，无需外部依赖即可测试 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [实体](../entity/) | 领域模型的构建块，有唯一标识 |
| [值对象](../value-object/) | 领域模型的构建块，无标识 |
| [聚合](../aggregate/) | 一组实体和值对象的一致性边界 |
| [限界上下文](../bounded-context/) | 领域模型的适用边界 |
| [通用语言](../ubiquitous-language/) | 领域模型应该反映通用语言 |

## 总结

**核心**：领域模型 = 数据 + 行为 + 业务规则。

**实践**：用充血模型替代贫血模型，让业务逻辑回归领域对象。
