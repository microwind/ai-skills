---
name: 值对象 (Value Object)
description: "没有身份标识，通过属性值判断相等的对象。不可变，通常代表领域中的度量或描述。"
license: MIT
---

# 值对象 (Value Object)

## 概述

值对象是DDD中的基础概念，表示**没有唯一身份的对象**。两个值对象如果属性值完全相同，就认为它们是相等的。

**核心特征**：
- **无身份**：没有唯一标识符
- **不可变**：创建后不改变
- **值相等**：属性值相同就相等
- **自我验证**：保证内部一致性

## Java 实现

```java
// ✅ 值对象：Money
public class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative");
        }
        this.amount = amount;
        this.currency = currency;
    }

    public Money add(Money other) {
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException("Cannot add different currencies");
        }
        return new Money(amount.add(other.amount), currency);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money)) return false;
        Money money = (Money) o;
        return amount.equals(money.amount) && currency.equals(money.currency);
    }

    @Override
    public int hashCode() {
        return Objects.hash(amount, currency);
    }
}

// 使用
Money m1 = new Money(new BigDecimal("100"), Currency.USD);
Money m2 = new Money(new BigDecimal("100"), Currency.USD);
assertEquals(m1, m2);  // 值相等
```

## Python 实现

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # 不可变
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

# 使用
m1 = Money(Decimal("100"), "USD")
m2 = Money(Decimal("100"), "USD")
assert m1 == m2  # 值相等
```

---

## 与 Entity 的对比

| 特性 | Entity | Value Object |
|------|--------|--------------|
| 身份 | 有 ID | 无 ID |
| 相等性 | 基于 ID | 基于值 |
| 可变性 | 可变 | 不可变 |
| 示例 | User, Order | Money, Email, Address |

---

## 最佳实践

1. **不可变** - 创建后不修改
2. **自验证** - 构造时验证有效性
3. **无副作用** - 方法返回新对象
4. **值相等** - equals/hashCode 基于属性

值对象简化了代码，提高了安全性。
