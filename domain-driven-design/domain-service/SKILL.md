---
name: 领域服务
description: "封装不属于任何单个实体或值对象的领域逻辑，是无状态的纯业务操作。"
license: MIT
---

# 领域服务 (Domain Service)

## 概述

领域服务封装**不自然属于任何实体或值对象的领域逻辑**。它是无状态的，操作多个领域对象来完成一个业务操作。

**何时使用领域服务**：
- 操作涉及多个聚合
- 逻辑不自然属于任何一个实体
- 需要调用外部服务的领域逻辑（通过接口）

## 代码示例

```java
// ✅ 领域服务：转账涉及两个账户聚合
public class TransferService {  // 领域服务，无状态
    public void transfer(Account from, Account to, Money amount) {
        if (!from.hasSufficientFunds(amount)) {
            throw new InsufficientFundsException();
        }
        from.debit(amount);
        to.credit(amount);
    }
}

// ❌ 错误：把转账逻辑放在 Account 实体中
public class Account {
    public void transferTo(Account target, Money amount) {
        // Account 不应该知道另一个 Account 的存在
        this.debit(amount);
        target.credit(amount);  // 直接操作另一个聚合
    }
}
```

```python
# ✅ 领域服务：价格计算涉及多个因素
class PricingService:
    """领域服务：计算最终价格"""

    def calculate_price(self, product, customer, coupon=None) -> Money:
        base_price = product.price

        # 会员折扣
        if customer.is_vip():
            base_price = base_price.multiply(0.9)

        # 优惠券
        if coupon and coupon.is_valid():
            base_price = coupon.apply(base_price)

        return base_price
```

## 领域服务 vs 应用服务

| 维度 | 领域服务 | [应用服务](../application-service/) |
|------|---------|--------|
| 职责 | 纯业务逻辑 | 用例编排 |
| 状态 | 无状态 | 无状态 |
| 依赖 | 只依赖领域对象 | 依赖领域服务、仓储等 |
| 事务 | 不管理事务 | 管理事务 |
| 层次 | 领域层 | 应用层 |

```java
// 领域服务：纯业务逻辑
public class DiscountService {
    public Money calculateDiscount(Order order, Customer customer) {
        // 纯领域逻辑，无基础设施依赖
    }
}

// 应用服务：编排流程
@Service
@Transactional
public class OrderApplicationService {
    private final OrderRepository orderRepo;
    private final DiscountService discountService;

    public OrderDTO placeOrder(PlaceOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.getOrderId());
        Customer customer = customerRepo.findById(cmd.getCustomerId());
        Money discount = discountService.calculateDiscount(order, customer);
        order.applyDiscount(discount);
        order.place();
        orderRepo.save(order);
        return OrderDTO.from(order);
    }
}
```

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [实体](../entity/) | 领域服务操作实体但不替代实体的方法 |
| [应用服务](../application-service/) | 应用服务调用领域服务 |
| [领域模型](../domain-model/) | 领域服务是领域模型的一部分 |

## 总结

**核心**：领域服务封装跨实体的纯业务逻辑，无状态。

**判断标准**：如果逻辑不自然属于任何一个实体，就用领域服务。优先把逻辑放在实体中，领域服务是补充。
