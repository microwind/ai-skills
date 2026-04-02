---
name: 封装原则
description: "隐藏对象的内部实现细节，只通过公共接口暴露必要的操作，保护数据完整性。"
license: MIT
---

# 封装原则 (Encapsulation Principle)

## 概述

封装是面向对象设计的基石：**隐藏对象内部状态和实现细节，只通过受控的接口与外部交互**。

**核心思想**：
- 数据和操作数据的方法绑定在一起
- 内部实现对外不可见
- 通过公共方法控制访问和修改
- 保护对象不变量不被外部破坏

## 代码示例

```java
// ❌ 缺乏封装：内部状态暴露
public class BankAccount {
    public double balance;      // 公开字段
    public List<Transaction> transactions;  // 公开集合

    // 任何人都可以直接修改余额
    // account.balance = -1000;  合法但错误！
}

// ✅ 良好封装
public class BankAccount {
    private double balance;
    private final List<Transaction> transactions = new ArrayList<>();

    public BankAccount(double initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("初始余额不能为负");
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("存款金额必须为正");
        this.balance += amount;
        transactions.add(new Transaction(TransactionType.DEPOSIT, amount));
    }

    public void withdraw(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("取款金额必须为正");
        if (amount > balance) throw new InsufficientFundsException();
        this.balance -= amount;
        transactions.add(new Transaction(TransactionType.WITHDRAWAL, amount));
    }

    public double getBalance() { return balance; }

    public List<Transaction> getTransactions() {
        return Collections.unmodifiableList(transactions);  // 返回不可变视图
    }
}
```

```python
# ✅ Python 封装
class ShoppingCart:
    def __init__(self):
        self._items: list[CartItem] = []  # 受保护

    def add_item(self, product, quantity: int):
        if quantity <= 0:
            raise ValueError("数量必须为正")
        existing = self._find_item(product.id)
        if existing:
            existing.quantity += quantity
        else:
            self._items.append(CartItem(product, quantity))

    def remove_item(self, product_id: str):
        self._items = [i for i in self._items if i.product.id != product_id]

    @property
    def total(self) -> float:
        return sum(i.subtotal for i in self._items)

    @property
    def items(self) -> tuple:
        return tuple(self._items)  # 返回不可变副本

    def _find_item(self, product_id: str):
        return next((i for i in self._items if i.product.id == product_id), None)
```

## 封装层次

| 层次 | 说明 | 示例 |
|------|------|------|
| 字段封装 | 私有字段 + getter/setter | private + getXxx() |
| 行为封装 | 数据和行为在一起 | account.withdraw() |
| 实现封装 | 隐藏算法细节 | sort() 不暴露排序算法 |
| 类型封装 | 隐藏具体类型 | 返回接口而非实现类 |
| 模块封装 | 隐藏内部类 | 只导出公共 API |

## 常见封装破坏

```java
// ❌ 1. 返回内部可变集合的引用
public List<Item> getItems() {
    return this.items;  // 外部可以直接修改！
}

// ✅ 返回不可变副本
public List<Item> getItems() {
    return Collections.unmodifiableList(this.items);
}

// ❌ 2. getter/setter 全部暴露 = 没有封装
public class User {
    private String name;
    private String email;
    private int age;
    // 为每个字段都生成 getter/setter = 等于公开字段
}

// ✅ 只暴露必要的操作
public class User {
    public void updateProfile(String name, String email) {
        validateEmail(email);
        this.name = name;
        this.email = email;
    }
}

// ❌ 3. 通过参数暴露内部结构
public void processOrder(Map<String, Object> orderData) {
    // 调用方需要知道 map 的 key 结构
}

// ✅ 使用类型化参数
public void processOrder(OrderRequest request) {
    // 结构明确，编译时检查
}
```

## 最佳实践

1. **默认 private** - 字段和方法默认私有，按需开放
2. **不可变优先** - 能用 final/readonly 就用
3. **防御性拷贝** - 返回集合或可变对象时返回副本
4. **告诉不要问** - 让对象执行操作，而非获取数据后外部操作

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [最少知识](../least-knowledge-principle/) | 封装支撑迪米特法则 |
| [SRP](../single-responsibility-principle/) | 封装帮助划定职责边界 |
| [OCP](../open-closed-principle/) | 封装变化点使扩展更安全 |

## 总结

**封装核心**：隐藏实现，暴露接口，保护不变量。

**实践**：字段私有、行为内聚、返回不可变视图、用类型代替裸数据。
