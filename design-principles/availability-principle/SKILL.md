---
name: 可用性原则
description: "设计系统使其在各种条件下都能持续提供服务，最大化正常运行时间和服务质量。"
license: MIT
---

# 可用性原则 (Availability Principle)

## 概述

可用性衡量系统正常提供服务的时间比例：**系统应该在用户需要时可用**。

**可用性等级**：

| 等级 | 可用率 | 年停机时间 |
|------|--------|-----------|
| 2个9 | 99% | 3.65天 |
| 3个9 | 99.9% | 8.76小时 |
| 4个9 | 99.99% | 52.6分钟 |
| 5个9 | 99.999% | 5.26分钟 |

## 提高可用性的策略

### 1. 冗余设计

```
单点故障消除：

❌ 单点架构
Client → [单一服务器] → [单一数据库]

✅ 冗余架构
Client → [负载均衡器]
            ├→ [服务器A] ──→ [主数据库]
            ├→ [服务器B]      ↕ 同步
            └→ [服务器C] ──→ [从数据库]
```

### 2. 健康检查

```java
// ✅ 健康检查端点
@RestController
public class HealthController {

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> status = new LinkedHashMap<>();

        // 检查数据库
        try {
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            status.put("database", "UP");
        } catch (Exception e) {
            status.put("database", "DOWN");
            return ResponseEntity.status(503).body(status);
        }

        // 检查缓存
        try {
            redisTemplate.opsForValue().get("health-check");
            status.put("cache", "UP");
        } catch (Exception e) {
            status.put("cache", "DOWN");
        }

        status.put("status", "UP");
        return ResponseEntity.ok(status);
    }
}
```

### 3. 优雅降级

```python
class ProductService:
    def __init__(self, db, cache, recommendation_service):
        self.db = db
        self.cache = cache
        self.recommendation_service = recommendation_service

    def get_product_page(self, product_id: str) -> dict:
        # 核心功能：必须可用
        product = self._get_product(product_id)

        # 非核心功能：降级处理
        try:
            recommendations = self.recommendation_service.get(product_id)
        except ServiceUnavailableError:
            recommendations = []  # 推荐服务挂了，返回空列表，页面仍可用

        return {"product": product, "recommendations": recommendations}

    def _get_product(self, product_id: str):
        # 缓存降级
        try:
            return self.cache.get(f"product:{product_id}")
        except CacheError:
            return self.db.find_product(product_id)  # 缓存挂了走数据库
```

### 4. 超时与重试

```typescript
// ✅ 合理的超时和重试策略
async function callExternalService(url: string): Promise<Response> {
    const maxRetries = 3;
    const timeout = 3000;  // 3秒超时

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);

            const response = await fetch(url, { signal: controller.signal });
            clearTimeout(timeoutId);

            if (response.ok) return response;

            // 5xx 错误重试，4xx 不重试
            if (response.status < 500) throw new Error(`Client error: ${response.status}`);
        } catch (error) {
            if (attempt === maxRetries) throw error;
            // 指数退避
            await sleep(Math.pow(2, attempt) * 100);
        }
    }
    throw new Error('Max retries exceeded');
}
```

## 可用性检查清单

```
□ 无单点故障（数据库、缓存、服务都有冗余）
□ 有健康检查接口
□ 非核心功能支持降级
□ 外部调用有超时设置
□ 有失败重试机制（带退避策略）
□ 有监控告警（响应时间、错误率、资源使用）
□ 有灾备方案和恢复演练
□ 部署支持滚动更新（零停机发布）
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [容错性](../fault-tolerance-principle/) | 容错是可用性的技术保障 |
| [可扩展性](../scalability-principle/) | 扩展能力防止过载导致不可用 |
| [关注点分离](../separation-of-concerns/) | 核心与非核心分离，支持独立降级 |

## 总结

**核心**：消除单点故障、优雅降级、快速恢复。

**实践**：冗余部署、健康检查、超时重试、监控告警。
