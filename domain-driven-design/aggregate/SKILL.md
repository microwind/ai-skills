---
name: 聚合 (Aggregate)
description: "以聚合根为边界，包含多个相关Entity和ValueObject的集合。保证数据一致性和事务边界。"
license: MIT
---

# 聚合 (Aggregate)

## 概述

聚合是DDD中的**设计模式**，用于组织Entity和ValueObject。每个聚合有一个**聚合根**，作为访问聚合内部对象的唯一入口。

**核心概念**：
- **聚合根**：Entity，聚合的入口
- **边界**：明确的聚合边界
- **一致性**：保证聚合内的数据一致
- **事务单位**：聚合是最小事务单位

## Java 实现

```java
// 聚合根：Order
public class Order {
    private final String orderId;
    private List<OrderLine> items;  // 从属于聚合
    private OrderStatus status;
    private Money totalAmount;

    public void addItem(Product product, int quantity) {
        OrderLine line = new OrderLine(product, quantity);
        items.add(line);
        recalculateTotal();
    }

    public void cancel() {
        if (!canBeCanceled()) {
            throw new IllegalStateException("Cannot cancel order");
        }
        this.status = OrderStatus.CANCELED;
    }

    // 只通过聚合根修改数据，不直接访问items
    // ❌ 不要：order.getItems().add(...);
    // ✅ 要：order.addItem(...);

    private void recalculateTotal() {
        totalAmount = items.stream()
            .map(OrderLine::getTotal)
            .reduce(Money.ZERO, Money::add);
    }

    private boolean canBeCanceled() {
        return status == OrderStatus.PENDING || status == OrderStatus.PAID;
    }
}

// OrderLine：聚合内的对象，不应该独立存在
public class OrderLine {
    private final Product product;
    private final int quantity;

    public Money getTotal() {
        return product.getPrice().multiply(quantity);
    }
}
```

## Python 实现

```python
class Order:
    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = []
        self.status = "PENDING"
        self.total_amount = Money(0, "USD")

    def add_item(self, product: 'Product', quantity: int):
        """通过聚合根添加项"""
        line = OrderLine(product, quantity)
        self.items.append(line)
        self._recalculate_total()

    def can_be_canceled(self) -> bool:
        return self.status in ["PENDING", "PAID"]

    def cancel(self):
        if not self.can_be_canceled():
            raise ValueError("Cannot cancel order")
        self.status = "CANCELED"

    def _recalculate_total(self):
        self.total_amount = sum(
            (line.get_total() for line in self.items),
            Money(0, "USD")
        )

class OrderLine:
    def __init__(self, product: 'Product', quantity: int):
        self.product = product
        self.quantity = quantity

    def get_total(self) -> 'Money':
        return self.product.price.multiply(self.quantity)
```

---

## 聚合的边界设计

### 原则

1. **根引用聚合内部**：聚合根可以引用内部对象
2. **外部引用聚合根**：外部只能引用聚合根
3. **内部对象不引用外部**：不创建循环引用

### 反例

```java
// ❌ 错误：从外部直接访问聚合内部
Order order = orderRepository.find("O001");
OrderLine line = order.getItems().get(0);  // 直接访问！
line.setQuantity(100);  // 修改！

// ✅ 正确：通过聚合根
Order order = orderRepository.find("O001");
order.updateItem(0, 100);  // 通过聚合根修改
```

---

## 最佳实践

1. **设定清晰的聚合边界**
2. **只通过聚合根操作**
3. **保护聚合内的一致性**
4. **聚合根是仓储的访问点**

聚合是建立清晰边界、保证数据一致的关键设计。
