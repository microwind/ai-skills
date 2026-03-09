---
name: sql-optimizer
description: "Enhanced skill for sql-optimizer"
license: MIT
---

# SQL 优化r 技能

## 概述
详细的分析和验证 sql-optimizer.

**核心原则**: 缓慢 SQL 查询 compound. One 缓慢 查询 becomes 100 缓慢 事务. 优化 before scaling.

## 何时使用

**始终:**
- Optimizing 缓慢 查询
- 数据库 性能 问题
- Before scaling 数据库
- 查询 tuning after profiling
- 索引 strategy planning
- SQL review during 代码 review

**触发短语:**
- "优化 this SQL"
- "Why is this 查询 缓慢?"
- "How should I 索引 this?"
- "重写 this 低效的 查询"
- "查询 is taking 10 seconds"
- "数据库 CPU is at 100%"

## 功能

### 查询 Rewriting
- 使用 appropriate JOIN types
- Push predicates down (WHERE before JOIN)
- Aggregate before joining
- 使用 UNION instead of OR
- 批处理 operations 高效的ly

### 索引 Strategy
- Single 列 索引
- Composite 索引
- 索引 选择性 分析
- Covering 索引
- Partial 索引

### 执行ion Plan 分析
- 识别 sequential 扫描
- 查找 排序 operations
- 检测 temporary 表 usage
- 分析 predicate pushdown
- 检查 索引 usage

## 常见问题

### 缺失的 WHERE Clause
```
Problem:
SELECT * FROM orders (returns millions of rows)

Consequence:
- Memory overload
- Network congestion
- Database locks

Solution:
Add WHERE clause to limit results
```

### 隐式类型转换
```
Problem:
WHERE user_id = '123' (user_id is INT, string compared)

Consequence:
- Index not used (full scan)
- Query slow
- Inconsistent results

Solution:
Use correct type: WHERE user_id = 123
```

### OR条件低效
```
Problem:
WHERE status = 'active' OR status = 'pending' OR status = 'processing'

Consequence:
- Multiple index scans
- Slower than IN clause
- Inefficient

Solution:
Use IN: WHERE status IN ('active', 'pending', 'processing')
```

## 验证检查清单

- [ ] 查询 使用 appropriate 索引
- [ ] No 完整的 表 扫描 on large 表s
- [ ] JOIN order optimized
- [ ] WHERE conditions push down correctly
- [ ] LIMIT applied to large result sets
- [ ] No implicit type conversions
- [ ] Aggregations 高效的
- [ ] 执行ion plans reviewed

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ SELECT * without LIMIT
❌ 函数 on 索引ed 列s (breaks 索引)
❌ Implicit type conversions
❌ Complex OR conditions (使用 IN instead)
❌ Correlated sub查询 (N+1 查询)
❌ Using LIKE on non-索引ed 列s

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
