---
name: DDD 工厂
description: "封装复杂对象和聚合的创建过程，将创建职责从领域对象中剥离，保证聚合创建时的不变量满足。"
license: MIT
---

# 工厂 (Factory)

## 概述

工厂是 DDD 战术设计的一个构建块，源于 GoF 设计模式中的工厂模式。DDD 对其的采用是**"拿来主义"**——当对象或聚合的创建过程足够复杂，以至于让对象自己"生自己"会污染领域模型时，把创建逻辑独立成工厂。

**核心动机**：

> 将创建复杂对象和聚合的职责分配给一个单独的对象，该对象本身并不承担领域模型中的职责，但依然是领域设计的一部分。工厂应该提供一个创建对象的接口，封装所有创建对象的复杂操作过程，并确保聚合的不变量得到满足。

## 何时使用工厂

```
✅ 需要工厂的场景：
  ▸ 创建逻辑涉及多个步骤或外部数据
  ▸ 聚合内部包含复杂的对象图（多层嵌套的实体和值对象）
  ▸ 需要保证创建时的不变量（例如订单必须至少有一个商品行）
  ▸ 构造函数参数过多，难以理解
  ▸ 对象的初始状态需要根据上下文计算

❌ 不需要工厂的场景：
  ▸ 简单对象：直接用构造函数即可
  ▸ 无任何不变量的值对象：直接 new 没问题
  ▸ 工厂只是构造函数的"套壳"
```

## 工厂的三种形态

### 1. 独立工厂类（Factory Class）

当创建逻辑复杂、依赖外部服务时使用。

```java
public class OrderFactory {
    private final ProductRepository productRepo;
    private final DiscountPolicy discountPolicy;

    public OrderFactory(ProductRepository productRepo, DiscountPolicy discountPolicy) {
        this.productRepo = productRepo;
        this.discountPolicy = discountPolicy;
    }

    public Order create(CustomerId customerId, List<OrderLineSpec> specs) {
        if (specs == null || specs.isEmpty()) {
            throw new DomainException("订单必须至少有一个商品");
        }

        OrderId orderId = OrderId.generate();
        List<OrderLine> lines = specs.stream()
            .map(spec -> {
                Product product = productRepo.findById(spec.productId())
                    .orElseThrow(() -> new DomainException("商品不存在"));
                Money unitPrice = discountPolicy.applyTo(product.getPrice(), customerId);
                return new OrderLine(product.getId(), unitPrice, spec.quantity());
            })
            .toList();

        Order order = new Order(orderId, customerId, lines);
        return order;
    }
}
```

### 2. 聚合根上的工厂方法（Static Factory Method）

适用于大多数常规聚合。

```java
public class Subscription {
    private final SubscriptionId id;
    private final ReaderId reader;
    private final ColumnId column;
    private final Instant startTime;
    private SubscriptionStatus status;

    private Subscription(SubscriptionId id, ReaderId reader, ColumnId column, Instant startTime) {
        this.id = id;
        this.reader = reader;
        this.column = column;
        this.startTime = startTime;
        this.status = SubscriptionStatus.ACTIVE;
    }

    public static Subscription fromPayment(Payment payment, Column column) {
        if (!payment.isCompleted()) {
            throw new DomainException("只有支付完成才能创建订阅");
        }
        if (payment.getAmount().compareTo(column.getPrice()) < 0) {
            throw new DomainException("支付金额不足");
        }
        return new Subscription(
            SubscriptionId.generate(),
            payment.getPayerId(),
            column.getId(),
            payment.getCompletedAt()
        );
    }
}
```

### 3. 值对象工厂（Value Object Factory）

对构造逻辑不平凡的值对象做一层封装。

```java
public class Money {
    private final BigDecimal amount;
    private final Currency currency;

    private Money(BigDecimal amount, Currency currency) { ... }

    public static Money of(BigDecimal amount, Currency currency) {
        if (amount.scale() > currency.getDefaultFractionDigits()) {
            throw new DomainException("精度超过货币允许范围");
        }
        return new Money(amount.setScale(currency.getDefaultFractionDigits(), RoundingMode.HALF_EVEN), currency);
    }

    public static Money yuan(long yuan) {
        return of(BigDecimal.valueOf(yuan), Currency.getInstance("CNY"));
    }

    public static Money zero(Currency currency) {
        return of(BigDecimal.ZERO, currency);
    }
}
```

## Python 示例

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class OrderLineSpec:
    product_id: str
    quantity: int


class OrderFactory:
    def __init__(self, product_repo, discount_policy):
        self.product_repo = product_repo
        self.discount_policy = discount_policy

    def create(self, customer_id: str, specs: List[OrderLineSpec]) -> "Order":
        if not specs:
            raise DomainError("订单必须至少有一个商品")

        lines = []
        for spec in specs:
            product = self.product_repo.find_by_id(spec.product_id)
            if not product:
                raise DomainError(f"商品不存在: {spec.product_id}")
            unit_price = self.discount_policy.apply(product.price, customer_id)
            lines.append(OrderLine(product.id, unit_price, spec.quantity))

        return Order(id=OrderId.generate(), customer_id=customer_id, lines=lines)
```

## 工厂 vs 构造函数 vs 仓储

```
┌─────────────┐   ┌─────────────────┐   ┌─────────────────────┐
│ Constructor │   │   Factory       │   │   Repository        │
├─────────────┤   ├─────────────────┤   ├─────────────────────┤
│ 简单对象创建  │   │ 复杂对象创建     │   │ 重建已存在的聚合      │
│ 参数少       │   │ 多步骤/多依赖    │   │ 从存储加载数据         │
│ 无外部依赖   │   │ 可能访问仓储/服务 │   │ 负责持久化            │
└─────────────┘   └─────────────────┘   └─────────────────────┘

新建 (create) ─▶ Factory
重建 (reconstitute) ─▶ Repository
简单值对象 ─▶ Constructor
```

## 最佳实践

### 1️⃣ 工厂不能产生违反不变量的对象

```java
// ❌ 工厂只是组合字段，不校验
public static Order create(CustomerId customerId, List<OrderLine> lines) {
    return new Order(customerId, lines);   // lines 为空也能过！
}

// ✅ 工厂保证不变量
public static Order create(CustomerId customerId, List<OrderLine> lines) {
    if (lines == null || lines.isEmpty()) {
        throw new DomainException("订单必须至少有一个商品");
    }
    if (lines.size() > MAX_LINES) {
        throw new DomainException("商品行数超限");
    }
    return new Order(OrderId.generate(), customerId, lines);
}
```

### 2️⃣ 工厂属于领域层

工厂是领域设计的一部分，**定义在领域层**，与聚合同 package。不要放到应用服务或基础设施层。

```
domain/
  └── order/
        ├── Order.java           ← 聚合根
        ├── OrderLine.java       ← 实体
        ├── OrderFactory.java    ← 工厂（同层）
        └── OrderRepository.java ← 仓储接口
```

### 3️⃣ 优先使用聚合根静态方法

对于大部分场景，**聚合根的静态工厂方法**就够了，不需要独立工厂类：

```java
// 大多数场景
Order order = Order.create(customerId, lines);

// 仅当创建需要外部依赖（查商品、算折扣）时，才用独立工厂类
Order order = orderFactory.create(customerId, lineSpecs);
```

### 4️⃣ 工厂方法名要表达意图

```java
// ❌ 抽象的 create / build
Subscription.create(payment);

// ✅ 表达业务语义
Subscription.fromPayment(payment);        // 因支付而产生
Subscription.giftFrom(author, reader);    // 作者赠予
Subscription.trialFor(reader, days);      // 试用订阅
```

## 与其他 DDD 概念的关系

| 概念 | 关系 |
|------|------|
| [聚合](../aggregate/) | 工厂的主要用途是创建聚合 |
| [聚合根设计](../aggregate-root-design/) | 聚合根上的静态工厂方法是首选形态 |
| [实体](../entity/) | 工厂负责为实体分配身份标识 |
| [仓储](../repository/) | 仓储负责"重建"已有聚合，工厂负责"新建"聚合 |
| [领域服务](../domain-service/) | 创建涉及多个聚合协作时，常以领域服务形式出现工厂 |

## 总结

**核心**：把复杂的对象 / 聚合创建过程从领域模型中独立出来，同时保证创建时的业务不变量。

**实践**：

- 简单对象 → 构造函数
- 常规聚合 → 聚合根静态工厂方法
- 复杂创建（依赖仓储 / 服务 / 策略）→ 独立工厂类
- 已存在聚合的加载 → 仓储，不是工厂

**关键**：工厂的名字应表达业务意图，工厂必须保证聚合创建即合法。
