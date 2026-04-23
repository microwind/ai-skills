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
- **不可变**：创建后不改变（变更时只能替换为新实例）
- **值相等**：属性值相同就相等
- **自我验证**：保证内部一致性

## 值对象的业务形态

大多数情况下实体具有很多属性，这些属性一般都是平铺。但**有的属性归类和聚合后能表达一个业务含义**，就把这些属性封装成值对象，从而：

- **方便沟通** —— 用业务名词（如 `Address`）替代多个原始字段
- **无需关注细节** —— 调用方只关心"是什么"，不关心"怎么组合"
- **消除原始类型偏执 (Primitive Obsession)** —— 避免到处传 `String`、`BigDecimal`

> **一句话**：值对象就是用来**描述实体的特征**。实体的单一属性也可以是值对象。

## 值对象的两种代码形态

### 形态 1：单一属性值对象

只封装一个值，但赋予它领域含义。通常基于字符串、整型、枚举等原始类型。

```java
// ❌ 原始类型偏执
public class User {
    private String email;      // 只是个字符串，随便赋值
    private String phone;
}

// ✅ 单一属性值对象
public final class Email {
    private final String value;

    public Email(String value) {
        if (value == null || !value.matches("^[\\w.-]+@[\\w.-]+$")) {
            throw new DomainException("邮箱格式不合法: " + value);
        }
        this.value = value.toLowerCase();
    }

    public String domain() {
        return value.substring(value.indexOf('@') + 1);
    }

    @Override
    public boolean equals(Object o) {
        return (o instanceof Email) && value.equals(((Email) o).value);
    }

    @Override
    public int hashCode() { return value.hashCode(); }
}

public enum SubscriptionStatus {   // 枚举也是值对象
    ACTIVE, CANCELLED, EXPIRED
}

public class User {
    private final Email email;                    // 有自我验证
    private final SubscriptionStatus status;      // 业务语义清晰
}
```

### 形态 2：多属性值对象

把多个相关属性组合成一个概念整体。**设计成 class（或 record / dataclass），包含多个属性，但没有 ID**。值对象中可以嵌套值对象。

```java
// ✅ 多属性值对象：Money（amount + currency）
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) { ... }

    public Money add(Money other) {
        if (!currency.equals(other.currency)) {
            throw new DomainException("币种不一致");
        }
        return new Money(amount.add(other.amount), currency);   // 返回新对象
    }
}

// ✅ 多属性值对象：Address（嵌套 PostCode 值对象）
public final class Address {
    private final String province;
    private final String city;
    private final String street;
    private final PostCode postCode;     // 嵌套值对象

    // ...
}

// ✅ 多属性值对象：DateRange
public final class DateRange {
    private final LocalDate start;
    private final LocalDate end;

    public DateRange(LocalDate start, LocalDate end) {
        if (end.isBefore(start)) {
            throw new DomainException("end 不能早于 start");
        }
        this.start = start;
        this.end = end;
    }

    public boolean contains(LocalDate date) {
        return !date.isBefore(start) && !date.isAfter(end);
    }

    public Duration length() { return Duration.between(start.atStartOfDay(), end.atStartOfDay()); }
}
```

### Python 实现两种形态

```python
from dataclasses import dataclass
from decimal import Decimal

# 单一属性值对象
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if '@' not in self.value:
            raise ValueError(f"Invalid email: {self.value}")
        object.__setattr__(self, 'value', self.value.lower())   # frozen 下用 object.__setattr__

    def domain(self) -> str:
        return self.value.split('@')[1]

# 多属性值对象
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

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
