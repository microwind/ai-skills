---
name: 性能优先原则
description: "在性能关键路径上，以性能为首要考量进行设计和优化，同时避免过早优化。"
license: MIT
---

# 性能优先原则 (Performance-First Principle)

## 概述

性能优先原则关注：**在正确性之后，性能是系统最重要的质量属性之一**。但要区分"性能意识"和"过早优化"。

**核心思想**：
- "过早优化是万恶之源" —— Knuth（但不要忽视性能）
- 先让代码正确，再让代码快
- 用数据驱动优化决策，不要凭直觉
- 性能瓶颈通常在 20% 的代码中

## 性能优化流程

```
1. 测量 → 2. 分析 → 3. 优化 → 4. 验证

❌ 错误流程：直觉 → 优化 → 期望变快
✅ 正确流程：Profiler → 找到热点 → 定向优化 → 基准测试确认
```

## 常见性能优化

### 数据库层

```java
// ❌ N+1 查询问题
public List<OrderDTO> getOrders() {
    List<Order> orders = orderRepo.findAll();  // 1次查询
    return orders.stream().map(order -> {
        Customer c = customerRepo.findById(order.getCustomerId());  // N次查询
        return new OrderDTO(order, c);
    }).collect(toList());
}

// ✅ 批量查询
public List<OrderDTO> getOrders() {
    List<Order> orders = orderRepo.findAll();
    Set<Long> customerIds = orders.stream()
        .map(Order::getCustomerId).collect(toSet());
    Map<Long, Customer> customers = customerRepo.findByIds(customerIds)
        .stream().collect(toMap(Customer::getId, c -> c));
    return orders.stream()
        .map(o -> new OrderDTO(o, customers.get(o.getCustomerId())))
        .collect(toList());
}
```

### 缓存策略

```python
# ✅ 合理使用缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_permissions(user_id: str) -> set:
    """频繁调用、结果稳定的查询适合缓存"""
    return permission_repo.find_by_user(user_id)

# 缓存原则
# 1. 读多写少的数据
# 2. 计算成本高的结果
# 3. 设置合理的过期时间
# 4. 数据变更时主动失效缓存
```

### 算法选择

```java
// ❌ O(n²)
public boolean hasDuplicate(List<Integer> list) {
    for (int i = 0; i < list.size(); i++)
        for (int j = i + 1; j < list.size(); j++)
            if (list.get(i).equals(list.get(j))) return true;
    return false;
}

// ✅ O(n)
public boolean hasDuplicate(List<Integer> list) {
    return list.size() != new HashSet<>(list).size();
}
```

## 过早优化 vs 性能意识

```
✅ 性能意识（始终应该有）：
- 选择合适的数据结构（HashMap vs LinkedList）
- 避免 N+1 查询
- 不在循环中创建不必要的对象
- 合理使用索引

❌ 过早优化（应该避免）：
- 在没有性能问题时手写缓存
- 用位运算替代乘除法
- 为了"性能"牺牲可读性
- 在非瓶颈处花大量时间优化
```

## 性能检查清单

```
□ 数据库查询有合适的索引
□ 没有 N+1 查询问题
□ 大列表操作使用分页
□ 频繁访问的数据有缓存策略
□ API 有合理的超时设置
□ 文件/网络 I/O 使用异步或批处理
□ 有性能基准测试和监控
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [KISS](../kiss-principle/) | 简单的代码通常性能也不差 |
| [YAGNI](../yagni-principle/) | 不需要的优化不要做 |
| [关注点分离](../separation-of-concerns/) | 性能优化集中在瓶颈处 |

## 总结

**核心**：用数据驱动性能优化，优化瓶颈而非猜测。

**实践**：先正确 → 再测量 → 再优化 → 再验证。
