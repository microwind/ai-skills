---
name: OOP vs FP
description: "面向对象编程与函数式编程的深度对比，分析各自的优势、劣势和适用场景。"
license: MIT
---

# OOP vs FP 对比

## 核心哲学

| 维度 | [OOP](../object-oriented-programming/) | [FP](../functional-programming/) |
|------|-----|-----|
| 基本单元 | 对象（数据 + 行为） | 函数（输入 → 输出） |
| 状态管理 | 可变状态，封装在对象中 | 不可变数据，状态转换 |
| 代码复用 | 继承、组合 | 函数组合、高阶函数 |
| 多态 | 子类型多态（接口/继承） | 参数多态（泛型） |
| 副作用 | 允许，通过封装管理 | 避免，隔离到边界 |
| 抽象方式 | 类层次、设计模式 | 类型、函数 |

## 同一问题，两种解法

### 问题：计算订单总金额（含折扣）

```java
// OOP 风格
public class Order {
    private List<OrderItem> items;
    private DiscountPolicy discount;

    public Money calculateTotal() {
        Money subtotal = Money.ZERO;
        for (OrderItem item : items) {
            subtotal = subtotal.add(item.getSubtotal());
        }
        return discount.apply(subtotal);
    }
}

public interface DiscountPolicy {
    Money apply(Money amount);
}

public class PercentageDiscount implements DiscountPolicy {
    private double rate;
    public Money apply(Money amount) {
        return amount.multiply(1 - rate);
    }
}
```

```java
// FP 风格
Function<List<OrderItem>, Money> calculateSubtotal =
    items -> items.stream()
        .map(OrderItem::getSubtotal)
        .reduce(Money.ZERO, Money::add);

Function<Money, Money> percentageDiscount(double rate) {
    return amount -> amount.multiply(1 - rate);
}

// 组合
Function<List<OrderItem>, Money> calculateTotal =
    calculateSubtotal.andThen(percentageDiscount(0.1));

Money total = calculateTotal.apply(orderItems);
```

### 问题：状态机

```python
# OOP：状态模式
class OrderState(ABC):
    @abstractmethod
    def next(self, order): pass

class DraftState(OrderState):
    def next(self, order):
        order.state = PendingState()

class PendingState(OrderState):
    def next(self, order):
        order.state = ConfirmedState()

class Order:
    def __init__(self):
        self.state = DraftState()
    def advance(self):
        self.state.next(self)
```

```python
# FP：数据 + 纯函数
from enum import Enum

class State(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"

transitions = {
    State.DRAFT: State.PENDING,
    State.PENDING: State.CONFIRMED,
}

def advance(state: State) -> State:
    if state not in transitions:
        raise ValueError(f"无法从 {state} 前进")
    return transitions[state]

# 使用
state = State.DRAFT
state = advance(state)  # PENDING
state = advance(state)  # CONFIRMED
```

## 各自的优势场景

### OOP 更适合

```
✅ 复杂业务系统（实体、关系、生命周期）
✅ GUI 应用（组件、事件、状态）
✅ 游戏开发（角色、物品、交互）
✅ 需要丰富类型层次的系统
✅ 团队以 OOP 为主的项目
```

### FP 更适合

```
✅ 数据转换管道（ETL、数据处理）
✅ 并发/并行计算（不可变 = 线程安全）
✅ 编译器和解释器
✅ 数学和科学计算
✅ 事件处理和流处理
```

## 现代趋势：多范式融合

```java
// Java：OOP + FP 混合
public class OrderService {
    // OOP：对象封装状态和行为
    private final OrderRepository repo;

    public List<OrderDTO> getActiveOrders(CustomerId customerId) {
        return repo.findByCustomerId(customerId)
            .stream()
            // FP：函数式数据处理
            .filter(Order::isActive)
            .sorted(Comparator.comparing(Order::getCreatedAt).reversed())
            .map(OrderDTO::from)
            .collect(toList());
    }
}
```

## 选择建议

```
不是 OOP 或 FP 的二选一，而是：
- 核心业务模型用 OOP（实体、聚合、领域逻辑）
- 数据处理用 FP（Stream、map、filter、reduce）
- 并发控制用 FP（不可变数据）
- 状态管理用 OOP（封装可变状态）
- 两者都要学，灵活运用
```

## 总结

| 选择 | 依据 |
|------|------|
| OOP | 复杂对象关系、丰富交互、需要封装状态 |
| FP | 数据转换、并发安全、纯计算 |
| 混合 | 大多数现代项目的最佳选择 |
