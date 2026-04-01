# 聚合 - 参考实现

## Java 完整例子

```java
public class Order {
    private final String orderId;
    private List<OrderLine> items;
    private Money totalAmount;
    private OrderStatus status;

    public void addItem(Product product, int quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException();
        }
        items.add(new OrderLine(product, quantity));
        recalculateTotal();
    }

    public void applyDiscount(Money discount) {
        if (discount.isGreaterThan(totalAmount)) {
            throw new IllegalArgumentException();
        }
        totalAmount = totalAmount.subtract(discount);
    }

    private void recalculateTotal() {
        totalAmount = items.stream()
            .map(OrderLine::getTotal)
            .reduce(Money.ZERO, Money::add);
    }

    // 不暴露集合
    public List<OrderLine> getItems() {
        return Collections.unmodifiableList(items);
    }
}

public class OrderLine {
    private final Product product;
    private final int quantity;

    public Money getTotal() {
        return product.getPrice().multiply(quantity);
    }
}
```

## Python 完整例子

```python
class Order:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self._items = []
        self._total_amount = Money(0, "USD")

    def add_item(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Invalid quantity")
        self._items.append(OrderLine(product, quantity))
        self._recalculate_total()

    def get_items(self):
        """返回副本，保护内部"""
        return list(self._items)

    def _recalculate_total(self):
        self._total_amount = sum(
            (line.total for line in self._items),
            Money(0, "USD")
        )
```

## TypeScript 完整例子

```typescript
class Order {
    private orderId: string;
    private items: OrderLine[] = [];
    private totalAmount: Money = Money.ZERO;

    addItem(product: Product, quantity: number): void {
        if (quantity <= 0) throw new Error("Invalid quantity");
        this.items.push(new OrderLine(product, quantity));
        this.recalculateTotal();
    }

    getItems(): OrderLine[] {
        return [...this.items];  // 返回副本
    }

    private recalculateTotal(): void {
        this.totalAmount = this.items
            .reduce((sum, line) => sum.add(line.getTotal()), Money.ZERO);
    }
}
```

聚合通过边界和一致性保证提高设计质量。
