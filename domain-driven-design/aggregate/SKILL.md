---
name: 聚合 (Aggregate)
description: "以聚合根为边界，包含多个相关Entity和ValueObject的集合。保证数据一致性和事务边界。"
---

# 聚合 (Aggregate)

## 概述

Eric Evans 将聚合定义为：**一组相关对象的集合，作为数据变更的整体单元**（"a cluster of associated objects that we treat as a unit for the purpose of data changes"）。每个聚合都有一个**聚合根**——作为外部访问聚合内部对象的唯一入口，以及一条由根的标识划定的**一致性边界**。

**核心概念**：
- **聚合根（Aggregate Root）**：一个 Entity，作为聚合的唯一入口；外部引用只能指向它
- **一致性边界**：聚合内的不变量在事务内必须成立
- **事务单位**：原则上**一个事务只修改一个聚合实例**——这是 DDD 的基线规则，目的是保证聚合的独立性、可扩展性与最终一致的演进空间。仅当同一限界上下文内、跨聚合的不变量在业务上确实必须强一致（且最终一致代价高于事务耦合的代价）时，可有保留地放宽；放宽前应优先重新审视聚合边界是否划错了
- **聚合间引用**：通过 ID 引用，不通过对象引用

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

## Vaughn Vernon 的四条聚合设计规则

Vaughn Vernon 在 *Implementing Domain-Driven Design*（IDDD，红皮书）中提炼了四条被广泛认可的聚合设计经验：

1. **在聚合边界内保护真正的业务不变量** ——只有"必须强一致"的规则，才值得放进同一个聚合。
2. **设计小聚合** ——优先单根 + 少量值对象；避免把所有相关 Entity 全塞进一个根。
3. **聚合之间通过全局唯一标识引用** ——不要用对象引用穿透聚合边界。
4. **聚合外部使用最终一致性** ——跨聚合的协同通过领域事件与最终一致机制完成。

```java
// ✅ 遵循规则：小聚合 + ID 引用
public class Order {
    private OrderId id;
    private CustomerId customerId;        // 通过 ID 引用其他聚合，而非 Customer 对象
    private List<OrderLine> items;        // 聚合内部实体
    private OrderStatus status;
}

// ❌ 违反规则：穿透边界、对象引用
public class Order {
    private Customer customer;            // 直接持有另一聚合的对象引用
    private List<OrderLine> items;
    public void changeCustomerEmail(String email) {
        customer.setEmail(email);         // 跨聚合直接写——破坏单写规则
    }
}
```

## 聚合大小如何把握

"小聚合"是原则，但"多小才算小"没有标准答案。下列实操判据可帮助判断：

**判断聚合是否过大**：

- 一次加载需要拉取大量子对象（数十乃至数百条），多数操作只用到其中一小部分
- 频繁出现"我只想改这一个字段，却要先 load 整个聚合"的吐槽
- 高并发下因聚合粒度大而触发版本冲突 / 乐观锁失败
- 同一聚合内的不同部分**修改频率明显不同**——通常意味着隐藏着另一个聚合

**判断聚合是否过小（被切碎了）**：

- 一个业务操作需要同时改 3 个以上聚合并维护强一致
- 频繁需要跨聚合 join 才能完成基本查询
- 业务规则被迫散落到应用服务里"做编排式校验"

**经验判据**：

- 优先把**真正共享一致性的最小子集**放进同一聚合
- 当聚合内某子集**修改频率独立、查询路径独立**，就考虑独立成新聚合
- "**先粗后细**"——不确定时先做大聚合，等出现性能或冲突信号再拆，比反过来从碎片合并容易得多

## 常见误区

❌ **上帝聚合**——把 Order + Customer + Product + Inventory 全塞进一个根
→ 用 ID 引用其他聚合，每个聚合只承载自己的真实不变量

❌ **从外部直接操作聚合内部对象**——`order.getItems().add(...)` 跳过聚合根校验
→ 暴露行为方法 `order.addItem(...)`，集合修改入口只在聚合根内部

❌ **跨聚合写在一个事务里**——一次事务同时更新 Order、Inventory、Payment
→ 同一事务只改一个聚合，跨聚合协同用领域事件 + 最终一致性

聚合是建立清晰边界、保证数据一致的关键设计。
