---
name: 实体 (Entity)
description: "在DDD中具有唯一身份标识和生命周期的对象，通过身份而非属性值相等判断。"
license: MIT
---

# 实体 (Entity)

## 概述

实体是DDD中的核心概念，表示具有**唯一身份标识**的对象。两个实体即使拥有完全相同的属性，但只要身份标识不同，它们就是不同的对象。

**核心特征**：
- **唯一身份**：每个实体有唯一的 ID（标识符）
- **可变性**：实体在生命周期内可以改变属性
- **生命周期**：实体有创建、修改、删除的过程
- **连续性**：通过 ID 追踪实体的演变

**对比值对象**：
- 实体：有身份，关心身份相等
- 值对象：无身份，关心值相等

## 何时使用Entity

**应该是Entity的**：
- 用户（User）- 每个用户有唯一 ID
- 订单（Order）- 每个订单有唯一订单号
- 产品（Product）- 每个产品有唯一SKU
- 账户（Account）- 每个账户有唯一账号

**不应该是Entity的**：
- 金额（Money）- 只关心数值，不关心"哪个"金额
- 地址（Address）- 两个相同地址就是一样的
- 颜色（Color）- 只关心颜色值，不关心"哪个"颜色

## 实体的关键特征

### 1. 身份标识

```java
public class User {
    private final String userId;  // 身份标识（不可变）
    private String name;          // 属性（可变）
    private String email;         // 属性（可变）

    public User(String userId, String name, String email) {
        this.userId = userId;
        this.name = name;
        this.email = email;
    }

    // 通过身份判断相等，不通过属性值
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof User)) return false;
        User user = (User) o;
        return Objects.equals(userId, user.userId);  // 只比对 ID
    }

    @Override
    public int hashCode() {
        return Objects.hash(userId);  // 只用 ID 计算哈希
    }
}

// 两个用户，相同属性但不同ID → 不相等
User user1 = new User("U001", "John", "john@example.com");
User user2 = new User("U002", "John", "john@example.com");
assertNotEquals(user1, user2);  // 不相等，因为 ID 不同
```

### 2. 生命周期管理

```java
public class Order {
    private final String orderId;
    private OrderStatus status;
    private List<OrderLine> items;
    private double totalAmount;
    private Instant createdAt;
    private Instant modifiedAt;

    // 创建
    public static Order create(String customerId, List<OrderLine> items) {
        Order order = new Order(UUID.randomUUID().toString(), items);
        order.status = OrderStatus.PENDING;
        order.createdAt = Instant.now();
        return order;
    }

    // 状态变化
    public void pay() {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Cannot pay order in status: " + status);
        }
        this.status = OrderStatus.PAID;
        this.modifiedAt = Instant.now();
    }

    public void ship() {
        if (status != OrderStatus.PAID) {
            throw new IllegalStateException("Cannot ship unpaid order");
        }
        this.status = OrderStatus.SHIPPED;
        this.modifiedAt = Instant.now();
    }

    public void deliver() {
        if (status != OrderStatus.SHIPPED) {
            throw new IllegalStateException("Cannot deliver unshipped order");
        }
        this.status = OrderStatus.DELIVERED;
        this.modifiedAt = Instant.now();
    }
}

// 订单的生命周期
Order order = Order.create("C001", items);
order.pay();      // PENDING → PAID
order.ship();     // PAID → SHIPPED
order.deliver();  // SHIPPED → DELIVERED
```

### 3. 可变性

```java
public class User {
    private final String userId;  // 不可变
    private String name;          // 可变
    private String email;         // 可变

    public void updateProfile(String newName, String newEmail) {
        this.name = newName;
        this.email = newEmail;
    }
}

// 实体的属性可以改变，但 ID 不变
User user = new User("U001", "John", "john@example.com");
user.updateProfile("Jane", "jane@example.com");
// 仍然是同一个用户，只是属性改变了
assertEquals("U001", user.getUserId());
```

## 最佳实践

### 1️⃣ 使用合适的标识符

```java
// ❌ 使用自增数字（可能重用）
public class User {
    private long id;  // 1, 2, 3... 不够唯一
}

// ✅ 使用 UUID（全局唯一）
public class User {
    private String userId = UUID.randomUUID().toString();
}

// ✅ 使用业务标识符（有含义）
public class Product {
    private String sku;  // 库存保留单位，业务上唯一
}
```

### 2️⃣ 保护实体的一致性

```java
public class BankAccount {
    private final String accountId;
    private double balance;

    // ❌ 不保护不变式
    public void setBalance(double balance) {
        this.balance = balance;  // 允许负数！
    }

    // ✅ 保护不变式
    public void withdraw(double amount) throws InsufficientFundsException {
        if (balance < amount) {
            throw new InsufficientFundsException();
        }
        this.balance -= amount;
    }

    public void deposit(double amount) throws InvalidAmountException {
        if (amount <= 0) {
            throw new InvalidAmountException();
        }
        this.balance += amount;
    }
}
```

### 3️⃣ 用值对象封装属性

```java
// ❌ 混乱的属性
public class User {
    private String firstName;
    private String lastName;
    private String emailValue;
    private String emailDomain;
}

// ✅ 用值对象组织
public class User {
    private final String userId;
    private FullName name;      // 值对象：firstName + lastName
    private Email email;        // 值对象：封装邮箱逻辑
    private Address address;    // 值对象：封装地址
}
```

### 4️⃣ 明确边界和聚合

```java
public class Order {
    private final String orderId;
    private Customer customer;      // 引用，不嵌入
    private List<OrderLine> items;  // 从属（聚合根）

    // ❌ 不要直接修改 items
    // public List<OrderLine> getItems() { return items; }

    // ✅ 提供受控的操作
    public void addItem(Product product, int quantity) {
        OrderLine line = new OrderLine(product, quantity);
        this.items.add(line);
    }

    public void removeItem(String productId) {
        items.removeIf(line -> line.getProduct().getId().equals(productId));
    }
}
```

## Java 实现示例

```java
public class Order {
    private final String orderId;
    private String customerId;
    private OrderStatus status;
    private List<OrderLine> items;
    private Money totalAmount;
    private Instant createdAt;
    private Instant modifiedAt;

    public Order(String orderId, String customerId) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.status = OrderStatus.PENDING;
        this.items = new ArrayList<>();
        this.createdAt = Instant.now();
    }

    public void addItem(Product product, int quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must > 0");
        }
        OrderLine line = new OrderLine(product, quantity);
        items.add(line);
        recalculateTotal();
    }

    public void pay() {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Can only pay pending orders");
        }
        this.status = OrderStatus.PAID;
        this.modifiedAt = Instant.now();
    }

    private void recalculateTotal() {
        totalAmount = items.stream()
            .map(OrderLine::getTotal)
            .reduce(Money.ZERO, Money::add);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Order)) return false;
        Order order = (Order) o;
        return Objects.equals(orderId, order.orderId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(orderId);
    }
}
```

## Python 实现示例

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import List

class OrderStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"

@dataclass
class OrderLine:
    product_id: str
    quantity: int
    unit_price: float

    def get_total(self) -> float:
        return self.quantity * self.unit_price

class Order:
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id  # 身份标识
        self.customer_id = customer_id
        self.status = OrderStatus.PENDING
        self.items: List[OrderLine] = []
        self.total_amount = 0.0
        self.created_at = datetime.now()
        self.modified_at = None

    def add_item(self, product_id: str, quantity: int, unit_price: float):
        if quantity <= 0:
            raise ValueError("Quantity must > 0")
        self.items.append(OrderLine(product_id, quantity, unit_price))
        self._recalculate_total()

    def pay(self):
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot pay order in status {self.status}")
        self.status = OrderStatus.PAID
        self.modified_at = datetime.now()

    def _recalculate_total(self):
        self.total_amount = sum(item.get_total() for item in self.items)

    def __eq__(self, other):
        # 通过 ID 判断相等
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)
```

## 与值对象的对比

| 特性 | Entity | Value Object |
|------|--------|--------------|
| 身份 | 有唯一 ID | 无 ID |
| 相等性 | 基于 ID | 基于属性值 |
| 可变性 | 通常可变 | 不可变 |
| 生命周期 | 有明确生命周期 | 无生命周期 |
| 例子 | User, Order | Money, Email, Address |

---

## 总结

**Entity 的核心**：
- 唯一身份标识
- 通过身份判断相等
- 有明确的生命周期
- 可变但需保护一致性

**最佳实践**：
- 选择合适的标识符（UUID、业务键）
- 通过 ID 而非属性判断相等
- 用值对象组织属性
- 保护实体的不变式

Entity 是 DDD 的核心概念，正确使用能大幅提高设计质量。
