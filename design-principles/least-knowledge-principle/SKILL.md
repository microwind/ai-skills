---
name: 最少知识原则
description: "一个对象应该对其他对象有尽可能少的了解，只与直接朋友通信，不与陌生人说话。又称迪米特法则。"
license: MIT
---

# 最少知识原则 (Law of Demeter / Least Knowledge Principle)

## 概述

最少知识原则（迪米特法则）：**一个对象应该只与它的直接朋友交互，不要和陌生人说话**。

**核心规则 — 方法只应调用**：
1. 自身的方法
2. 方法参数的方法
3. 自身创建的对象的方法
4. 自身持有的组件的方法

## 违反示例

```java
// ❌ 火车残骸（Train Wreck）：连续调用链
String city = order.getCustomer().getAddress().getCity();

// 问题：Order 需要知道 Customer 有 Address，Address 有 City
// 任何中间结构变化都会影响这行代码

// ✅ 遵循迪米特法则
String city = order.getShippingCity();

// Order 内部
public class Order {
    private Customer customer;

    public String getShippingCity() {
        return customer.getShippingCity();  // 委托给直接朋友
    }
}
```

```python
# ❌ 深层访问
def calculate_shipping(order):
    distance = order.customer.address.coordinates.distance_to(warehouse)
    return distance * rate

# ✅ 告诉，不要问（Tell, Don't Ask）
def calculate_shipping(order):
    distance = order.distance_to(warehouse)
    return distance * rate
```

```typescript
// ❌ 违反：访问对象的内部结构
function getManagerName(employee: Employee): string {
    return employee.getDepartment().getManager().getName();
}

// ✅ 遵循
function getManagerName(employee: Employee): string {
    return employee.getManagerName();
}
```

## 最佳实践

### Tell, Don't Ask（告诉，不要问）

```java
// ❌ 问了再做（Ask then Act）
if (account.getBalance() >= amount) {
    account.setBalance(account.getBalance() - amount);
}

// ✅ 直接告诉对象要做什么
account.withdraw(amount);  // 让 Account 自己处理
```

### 合理使用委托

```java
// 不要机械地为每个属性创建委托方法
// 只在需要隐藏内部结构时委托

// ✅ 有意义的委托
public class Order {
    public boolean isShippable() {
        return items.stream().allMatch(Item::isInStock)
            && customer.hasVerifiedAddress();
    }
}

// ❌ 无意义的委托（过度应用）
public class Order {
    public String getCustomerName() { return customer.getName(); }
    public String getCustomerEmail() { return customer.getEmail(); }
    public String getCustomerPhone() { return customer.getPhone(); }
    // 这其实在暴露 Customer 的全部信息
}
```

## 例外情况

```
可以接受链式调用的场景：
✅ 流式 API / Builder 模式（返回自身）
   stream.filter(...).map(...).collect(...)

✅ 值对象（无行为，纯数据）
   config.getDatabase().getHost()

✅ DSL（领域特定语言）
   select().from("users").where("age > 18")
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [封装](../encapsulation-principle/) | 迪米特法则强化了封装 |
| [SRP](../single-responsibility-principle/) | 减少知识依赖有助于保持单一职责 |
| [关注点分离](../separation-of-concerns/) | 限制交互范围帮助分离关注点 |

## 总结

**核心**：只与直接朋友通信，不要深入访问对象的内部结构。

**实践**：
- 避免链式属性访问（a.b.c.d）
- 使用"告诉，不要问"模式
- 通过委托隐藏内部结构
- 区分数据结构和对象——数据结构可以直接访问
