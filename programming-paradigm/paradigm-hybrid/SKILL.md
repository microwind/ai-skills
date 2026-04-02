---
name: 范式混合
description: "在同一项目中结合多种编程范式的优势，根据场景选择最合适的范式。"
license: MIT
---

# 范式混合 (Paradigm Hybrid)

## 概述

现代编程语言大多支持多范式。**在同一项目中根据场景选择最合适的范式**是实际开发的最佳实践。

## 混合示例

```java
// Java：OOP + FP + 响应式 混合

// OOP：领域模型
public class Order {
    private OrderId id;
    private List<OrderItem> items;
    private OrderStatus status;

    public void confirm() {
        if (status != OrderStatus.PENDING) throw new DomainException("无法确认");
        this.status = OrderStatus.CONFIRMED;
    }
}

// FP：数据转换
public class OrderAnalytics {
    public Map<String, BigDecimal> salesByCategory(List<Order> orders) {
        return orders.stream()
            .filter(Order::isConfirmed)
            .flatMap(o -> o.getItems().stream())
            .collect(groupingBy(
                OrderItem::getCategory,
                reducing(BigDecimal.ZERO, OrderItem::getAmount, BigDecimal::add)
            ));
    }
}

// 响应式：异步 I/O
public class OrderController {
    public Mono<OrderDTO> getOrder(String id) {
        return orderRepo.findById(id)           // 响应式数据库查询
            .map(OrderDTO::from)                 // FP 转换
            .switchIfEmpty(Mono.error(new NotFoundException()));
    }
}

// AOP：横切关注点
@Aspect
public class AuditAspect {
    @Around("execution(* *.confirm*(..))")
    public Object audit(ProceedingJoinPoint jp) throws Throwable {
        log.info("操作审计: {}", jp.getSignature());
        return jp.proceed();
    }
}
```

```python
# Python：混合范式

# 过程式：脚本和工具
def migrate_database():
    backup()
    run_migrations()
    verify()

# OOP：领域模型
class ShoppingCart:
    def __init__(self):
        self._items = []

    def add_item(self, product, qty):
        self._items.append(CartItem(product, qty))

# FP：数据处理
def analyze_orders(orders: list[Order]) -> dict:
    return {
        "total": sum(o.total for o in orders),
        "avg": sum(o.total for o in orders) / len(orders),
        "by_status": Counter(o.status for o in orders),
    }

# 装饰器（AOP）：横切关注
@login_required
@cache(ttl=300)
def get_dashboard(user_id):
    cart = ShoppingCart.load(user_id)     # OOP
    stats = analyze_orders(cart.orders)    # FP
    return render(cart, stats)             # 过程式
```

## 范式选择矩阵

| 场景 | 推荐范式 | 原因 |
|------|---------|------|
| 业务模型 | OOP | 封装状态和行为 |
| 数据转换 | FP | 管道式处理 |
| 异步 I/O | 响应式 / 异步 | 非阻塞 |
| 脚本工具 | 过程式 | 简单直接 |
| 横切关注 | AOP | 不侵入业务代码 |
| 性能关键 | 面向数据 | 缓存友好 |

## 最佳实践

1. **主范式统一** — 团队确定主范式（如 OOP），其他范式辅助
2. **按场景选择** — 不要强行用一个范式解决所有问题
3. **保持一致性** — 同一模块内风格统一
4. **团队共识** — 确保团队成员理解使用的范式

## 总结

**核心**：没有万能范式，根据场景选择最合适的，在同一项目中灵活混合。
