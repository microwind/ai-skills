---
name: 数据库-查询-analyzer
description: "Enhanced skill for 数据库-查询-analyzer"
license: MIT
---

# 数据库 查询 分析r 技能

## 概述
详细的分析和验证 数据库-查询-analyzer.

**核心原则**: 优化 查询 before they 缓慢 down your 系统. Bad 查询 compound as data grows.

## 何时使用

**始终:**
- 查询 运行缓慢
- 数据库 CPU spiking
- App 性能 degrading
- 规划数据模型
- 审查ing SQL 查询
- Investigating N+1 问题

**触发短语:**
- "优化 this 查询"
- "Why is this 缓慢?"
- "分析 查询 性能"
- "检查 SQL 效率"
- "查找 N+1 查询"
- "审查 this 数据库 设计"

## 功能

### 查询 分析
- 识别 缓慢 查询 (完整的 表 扫描)
- 查找 N+1 查询 问题
- 检测 缺失的 索引
- 分析 查询 执行ion plans
- 检查 join 效率

### 索引 检测
- 查找 缺失的 索引
- 识别 未使用的 索引
- Suggest 索引 列s
- 检查 composite 索引 usage
- 分析 索引 选择性

### 优化 技巧
- 添加 缺失的 索引
- 重写 低效的 查询
- 使用 EXPLAIN PLAN
- 批处理 operations
- 缓存 查询 results

## 常见问题

### N+1 查询 问题
```
Problem:
for item in items:\n    item.user = User.find(item.user_id)

Consequence:
- 1 query gets items
- N queries for each user (slow!)
- Performance degrades with data

Solution:
Use JOIN: SELECT items.*, users.* FROM items JOIN users...
```

### 缺失的 索引
```
Problem:
WHERE email = 'user@example.com' with no index on email column

Consequence:
- Full table scan (slow)
- Disk I/O increases
- CPU usage high

Solution:
CREATE INDEX idx_email ON users(email)
```

### 完整的 表 扫描
```
Problem:
SELECT * WHERE deleted_at IS NULL (no index on deleted_at)

Consequence:
- Scans entire table
- Slow for millions of rows
- Blocks other queries

Solution:
Add index: CREATE INDEX idx_deleted_at ON table(deleted_at)
```

### 低效的 JOIN
```
Problem:
SELECT * FROM orders o, items i, users u WHERE...

Consequence:
- Cartesian product possible
- Temporary tables created
- High memory usage

Solution:
Use proper JOIN syntax with ON clauses
```

## 验证检查清单

- [ ] All 查询 have appropriate 索引
- [ ] No N+1 查询 模式 detected
- [ ] JOIN conditions explicit
- [ ] LIMIT used for list 查询
- [ ] 缓慢 查询 identified
- [ ] 查询 执行ion plan reviewed
- [ ] 索引 not duplicated
- [ ] Statistics updated

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Running 查询 in loop (N+1)
❌ SELECT * 没有WHERE clause
❌ No 索引 on WHERE 列s
❌ Implicit type conversion in WHERE
❌ 函数 on 索引ed 列s
❌ Not using LIMIT on large 表s

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
