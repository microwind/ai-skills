---
name: 读模型优化
description: "为查询场景专门设计的数据模型，通过反规范化、物化视图等技术优化读取性能。"
license: MIT
---

# 读模型优化 (Read Model Optimization)

## 概述

读模型是**为查询性能专门优化的数据视图**，与写模型（领域模型）分离，可以按查询需求自由设计。

## 优化策略

### 1. 反规范化

```sql
-- 写模型：规范化（多表）
-- orders, order_items, customers, products（4张表，需要JOIN）

-- 读模型：反规范化（一张视图）
CREATE TABLE order_summary_view (
    order_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR,
    customer_email VARCHAR,
    total_amount DECIMAL,
    item_count INT,
    status VARCHAR,
    created_at TIMESTAMP
);
-- 查询时零 JOIN，直接读取
```

### 2. 事件驱动更新

```java
// 监听事件更新读模型
@EventHandler
public class OrderReadModelProjector {
    private final JdbcTemplate jdbc;

    public void on(OrderPlacedEvent event) {
        jdbc.update(
            "INSERT INTO order_summary_view (order_id, customer_name, total_amount, status) "
            + "VALUES (?, ?, ?, 'PLACED')",
            event.getOrderId(), event.getCustomerName(), event.getTotalAmount()
        );
    }

    public void on(OrderShippedEvent event) {
        jdbc.update(
            "UPDATE order_summary_view SET status = 'SHIPPED' WHERE order_id = ?",
            event.getOrderId()
        );
    }
}
```

### 3. 多种读模型

```python
# 同一数据，不同的读模型服务不同场景

# 列表页读模型（Redis Hash）
class OrderListCache:
    def get_recent_orders(self, customer_id: str, limit: int = 20):
        return self.redis.lrange(f"orders:{customer_id}", 0, limit)

# 搜索读模型（Elasticsearch）
class OrderSearchIndex:
    def search(self, keyword: str, filters: dict):
        return self.es.search(index="orders", query={"match": {"description": keyword}})

# 报表读模型（数据仓库）
class OrderReportView:
    def monthly_sales(self, year_month: str):
        return self.warehouse.query(
            "SELECT SUM(total) FROM sales_fact WHERE month = %s", year_month)
```

## 读模型存储选择

| 场景 | 推荐存储 | 原因 |
|------|---------|------|
| 列表展示 | Redis / 关系数据库视图 | 快速分页 |
| 全文搜索 | Elasticsearch | 倒排索引 |
| 报表分析 | 数据仓库 / ClickHouse | 列式存储 |
| 实时仪表盘 | Redis / 时序数据库 | 低延迟 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [CQRS](../cqrs-pattern/) | 读模型是 CQRS 查询端的核心 |
| [事件溯源](../event-sourcing/) | 从事件流投影生成读模型 |
| [领域事件](../domain-events/) | 事件驱动读模型的更新 |

## 总结

**核心**：为查询场景专门设计数据模型，反规范化优化读取性能。

**实践**：通过事件驱动更新读模型，不同场景用不同存储。
