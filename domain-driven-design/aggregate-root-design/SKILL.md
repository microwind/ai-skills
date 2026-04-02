---
name: 聚合根设计
description: "聚合的入口点，外部只能通过聚合根访问聚合内部对象，保证数据一致性和业务不变量。"
license: MIT
---

# 聚合根设计 (Aggregate Root Design)

## 概述

聚合根是聚合的**唯一入口**，外部对象只能通过聚合根与聚合交互，聚合根负责维护聚合的一致性。

**核心规则**：
- 外部只引用聚合根，不直接引用内部实体
- 聚合根负责维护所有业务不变量
- 一个事务只修改一个聚合
- 聚合间通过 ID 引用，不通过对象引用

## 代码示例

```java
// ✅ Order 是聚合根，OrderItem 是内部实体
public class Order {  // 聚合根
    private OrderId id;
    private CustomerId customerId;  // 引用其他聚合用 ID
    private List<OrderItem> items = new ArrayList<>();
    private OrderStatus status;
    private Money totalAmount;

    // 所有操作通过聚合根进行
    public void addItem(ProductId productId, Money price, int quantity) {
        if (status != OrderStatus.DRAFT) {
            throw new DomainException("只有草稿订单可以添加商品");
        }
        if (quantity <= 0) {
            throw new DomainException("数量必须为正");
        }
        // 检查不变量：同一商品不能重复添加
        if (items.stream().anyMatch(i -> i.getProductId().equals(productId))) {
            throw new DomainException("商品已存在，请修改数量");
        }
        items.add(new OrderItem(productId, price, quantity));
        recalculateTotal();
    }

    public void removeItem(ProductId productId) {
        items.removeIf(i -> i.getProductId().equals(productId));
        recalculateTotal();
    }

    private void recalculateTotal() {
        this.totalAmount = items.stream()
            .map(OrderItem::subtotal)
            .reduce(Money.ZERO, Money::add);
    }
}

// OrderItem 是内部实体，外部不能直接访问
public class OrderItem {  // 内部实体
    private ProductId productId;
    private Money unitPrice;
    private int quantity;

    Money subtotal() { return unitPrice.multiply(quantity); }
}
```

```python
# ✅ 聚合根设计
class ShoppingCart:  # 聚合根
    def __init__(self, cart_id: str, customer_id: str):
        self.id = cart_id
        self.customer_id = customer_id  # 引用其他聚合用 ID
        self._items: list[CartItem] = []

    def add_item(self, product_id: str, price: Decimal, quantity: int):
        existing = self._find_item(product_id)
        if existing:
            existing.increase_quantity(quantity)
        else:
            self._items.append(CartItem(product_id, price, quantity))

    def checkout(self) -> "Order":
        if not self._items:
            raise DomainError("购物车为空")
        # 聚合根负责创建新聚合
        return Order.create_from_cart(self.customer_id, list(self._items))

    def _find_item(self, product_id: str):
        return next((i for i in self._items if i.product_id == product_id), None)
```

## 聚合设计原则

```
1. 尽量小的聚合
   ❌ 一个聚合包含 Order + Customer + Product + Payment
   ✅ Order 聚合只包含 Order + OrderItems

2. 聚合间通过 ID 引用
   ❌ private Customer customer;  // 对象引用
   ✅ private CustomerId customerId;  // ID 引用

3. 一个事务一个聚合
   ❌ 一个事务修改 Order + Inventory + Payment
   ✅ 一个事务只修改 Order，通过事件通知其他聚合

4. 最终一致性
   聚合内：强一致性（事务保证）
   聚合间：最终一致性（通过事件）
```

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [聚合](../aggregate/) | 聚合根是聚合的入口 |
| [实体](../entity/) | 聚合根本身是实体 |
| [领域事件](../domain-events/) | 聚合根发布领域事件 |
| [仓储](../repository/) | 仓储按聚合根为单位操作 |

## 总结

**核心**：聚合根是唯一入口，维护一致性，控制所有写操作。

**实践**：聚合尽量小、通过 ID 引用其他聚合、一个事务一个聚合。
