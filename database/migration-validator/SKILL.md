---
name: migration-validator
description: "Enhanced skill for migration-validator"
license: MIT
---

# 迁移 验证器 技能

## 概述
详细的分析和验证 迁移-validator.

**核心原则**: Bad 迁移 lock production, lose data, or cause downtime. 验证 迁移 before running.

## 何时使用

**始终:**
- Before running 数据库 迁移
- 审查ing 迁移 代码
- Planning zero-downtime deploys
- 测试 data transformations
- Validating 模式 changes
- Investigating 迁移 failures

**触发短语:**
- "Is this 迁移 safe?"
- "验证 数据库 迁移"
- "检查 data transformation"
- "Will this cause downtime?"
- "如何 run this 迁移 safely?"
- "审查 迁移 strategy"

## 功能

### Safety 检查s
- Data loss 检测
- Locking 分析
- Downtime estimation
- Rollback strategy
- Backup verification

### Data Validation
- Data type compatibility
- Constraint violation 检测
- Data transformation correctness
- Null value handling
- 索引 rebuild impact

### 性能 Impact
- 表 lock duration
- 索引 recreation time
- 磁盘 space requirements
- 查询 性能 impact
- Connection pool impact

## 常见问题

### Long-Running 迁移
```
Problem:
ALTER TABLE MODIFY COLUMN type on 1 billion row table (hours of table lock)

Consequence:
- Production database locked
- All queries blocked
- Downtime

Solution:
Use online schema migration tools or shadow migration
```

### Data Losing 迁移
```
Problem:
ALTER TABLE DROP COLUMN without backing up data first

Consequence:
- Data lost forever
- No recovery possible
- Regulatory violations

Solution:
Backup first, verify before dropping
```

### Unconvertible Data
```
Problem:
Converting string column to integer without validation

Consequence:
- Non-numeric values can't convert
- Migration fails
- Partial data loss

Solution:
Validate data before conversion, create temp column
```

## 验证检查清单

- [ ] Backup created before 迁移
- [ ] 迁移 is idempotent (safe to re-run)
- [ ] Rollback procedure documented
- [ ] Data loss checked (no DROP without backup)
- [ ] Downtime estimated and accep表
- [ ] 索引 impact analyzed
- [ ] 测试 迁移 on staging first
- [ ] 性能 impact accep表

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ No backup before 迁移
❌ Long-running 迁移 on live 表
❌ No rollback plan
❌ Data conversion without validation
❌ Mixing multiple changes in one 迁移
❌ No 测试 run on staging

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
