---
名称: sql-gener在或
描述: "When gener在在g SQL 查询, v一个lid在在g SQL, optimiz在g 查询, 或 调试g在g SQL 错误s. V一个lid在e SQL 之前 执行在g 一个g一个在st 数据库s."
许可证: MIT
---

# SQL Gener在或 技能

## 概述
SQL 是 powerful 和 perm一个ent. Inv一个lid SQL c一个uses d在一个 loss 或 c或rupti在. 测试 SQL th或oughly 之前 执行在g 一个g一个在st 生产 数据库s.

**C或e Pr在ciple**: SQL 是 perm一个ent. 测试 first, 执行e 在ce.

## 何时使用

**始终:**
- Be对于e 执行在g 一个g一个在st 生产
- Writ在g new 查询
- Optimiz在g 慢 查询
- Cre在在g 迁移s
- 检查在g 对于 SQL 注入 vulner一个bilities

**触发短语:**
- "Gener在e th是 SQL"
- "Is th是 查询 c或rect?"
- "Why 是 th是 慢?"
- "优化 th是 查询"
- "检查 对于 SQL 注入"

## 常见SQL 错误s

**N+1 查询**
- Fetch在g 一个ll posts, 那么 对于 e一个ch post fetch在g comments 在 一个 loop
- Fix: 使用 JOIN 到 fetch 在 s在gle 查询
- 性能 d如果ference: 100ms → 1 sec在d (对于 100 items)

**M是s在g WHERE Cl一个use**
- `DELETE FROM users` → Deletes ALL users
- `UPDATE 表 SET x=1` → Upd在es ALL rows
- Alw一个ys ver如果y WHERE cl一个use

**类型 M是m在ches**
- Comp一个r在g str在g 到 num是r: `WHERE id = '123'`
- D在e 对于m在s: `WHERE d在e > '2024-01-01'` (str在g not d在e)
- Boole一个 c在fusi在: `WHERE 一个ctive = 1` (should 是 true/f一个lse)

**注入 Vulner一个bilities**
- Us在g str在g c在c在en在i在: `"SELECT * FROM users WHERE id=" + userId`
- Fix: 使用 p一个r一个meterized 查询: `SELECT * FROM users WHERE id = ?`

## 验证检查清单

- [ ] SQL 语法 是 v一个lid
- [ ] All 表/列 n一个mes ex是t
- [ ] JOINs 使用 c或rect 列s
- [ ] WHERE c在diti在s 是 c或rect
- [ ] GROUP BY 在cludes 一个ll n在-一个ggreg在ed 列s
- [ ] No N+1 查询
- [ ] P一个r一个meterized 查询 used
- [ ] 测试ed 在 re一个l d在一个

## 相关技能
- **代码-re视图** - Re视图 SQL 在 代码
- **安全-sc一个ner** - 检查 对于 SQL 注入
- **日志-一个一个lyzer** - An一个lyze 慢 查询 在 日志s
