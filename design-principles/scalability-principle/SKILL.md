---
name: 可扩展性原则
description: "设计系统使其能够通过增加资源来应对负载增长，支持水平和垂直扩展。"
license: MIT
---

# 可扩展性原则 (Scalability Principle)

## 概述

可扩展性是系统应对增长的能力：**当负载增加时，系统能通过增加资源来维持或提升性能**。

**扩展方式**：
- **垂直扩展（Scale Up）**：升级单机配置（更多CPU、内存）
- **水平扩展（Scale Out）**：增加更多机器实例

## 水平扩展设计

```java
// ❌ 无法水平扩展：状态存在内存中
@RestController
public class CartController {
    private Map<String, Cart> carts = new HashMap<>();  // 内存中的状态

    @PostMapping("/cart/{userId}/add")
    public void addItem(@PathVariable String userId, @RequestBody Item item) {
        carts.computeIfAbsent(userId, k -> new Cart()).addItem(item);
        // 另一台机器收到请求时看不到这个购物车
    }
}

// ✅ 无状态设计：状态外置
@RestController
public class CartController {
    private final CartRepository cartRepo;  // Redis / 数据库

    @PostMapping("/cart/{userId}/add")
    public void addItem(@PathVariable String userId, @RequestBody Item item) {
        Cart cart = cartRepo.findByUserId(userId).orElse(new Cart(userId));
        cart.addItem(item);
        cartRepo.save(cart);
        // 任何实例都能处理请求
    }
}
```

## 常见扩展策略

### 数据库扩展

```
读写分离：
┌─────────┐     写     ┌──────────┐
│  应用    │───────────→│  主库    │
│         │            └──────────┘
│         │     读      ┌──────────┐
│         │───────────→│  从库 1   │
│         │            ├──────────┤
│         │───────────→│  从库 2   │
└─────────┘            └──────────┘

分库分表：
用户 ID % 4 = 0 → DB_0
用户 ID % 4 = 1 → DB_1
用户 ID % 4 = 2 → DB_2
用户 ID % 4 = 3 → DB_3
```

### 缓存扩展

```python
# 多级缓存
class CacheService:
    def __init__(self, local_cache, redis, db):
        self.local_cache = local_cache  # L1: 本地缓存
        self.redis = redis              # L2: 分布式缓存
        self.db = db                    # L3: 数据库

    def get(self, key: str):
        # L1
        value = self.local_cache.get(key)
        if value: return value

        # L2
        value = self.redis.get(key)
        if value:
            self.local_cache.set(key, value, ttl=60)
            return value

        # L3
        value = self.db.query(key)
        if value:
            self.redis.set(key, value, ttl=300)
            self.local_cache.set(key, value, ttl=60)
        return value
```

### 异步处理

```typescript
// ❌ 同步处理：阻塞响应
app.post('/api/orders', async (req, res) => {
    const order = await createOrder(req.body);
    await sendConfirmationEmail(order);    // 耗时
    await updateInventory(order);          // 耗时
    await notifyWarehouse(order);          // 耗时
    res.json(order);  // 用户等了很久
});

// ✅ 异步处理：快速响应，后台处理
app.post('/api/orders', async (req, res) => {
    const order = await createOrder(req.body);
    await messageQueue.publish('order.created', order);  // 发消息
    res.json(order);  // 快速返回
});

// 后台消费者分别处理
messageQueue.subscribe('order.created', sendConfirmationEmail);
messageQueue.subscribe('order.created', updateInventory);
messageQueue.subscribe('order.created', notifyWarehouse);
```

## 可扩展性检查清单

```
□ 应用层无状态，状态存储在外部
□ 数据库有读写分离或分片策略
□ 耗时操作使用异步/消息队列
□ 有缓存层减少数据库压力
□ 支持配置化的连接池和线程池
□ API 支持分页，避免返回海量数据
□ 有负载均衡策略
□ 有容量规划和压测方案
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [关注点分离](../separation-of-concerns/) | 分离后的组件可以独立扩展 |
| [模块化](../modularity-principle/) | 模块化支持独立扩展 |
| [性能优先](../performance-first-principle/) | 扩展性是性能的长期保障 |

## 总结

**核心**：无状态设计 + 状态外置 + 异步解耦。

**关键策略**：读写分离、缓存分层、消息队列、水平扩展。
