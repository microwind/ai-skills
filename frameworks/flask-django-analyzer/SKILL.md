---
name: flask-django-analyzer
description: "Enhanced skill for flask-django-analyzer"
license: MIT
---

# Flask/Django 分析r 技能

## 概述
详细的分析和验证 flask-django-analyzer.

**核心原则**: Web框架实现快速开发 but bad 模式 create maintenance nightmares.

## 何时使用

**始终:**
- 审查ing Flask/Django 代码
- Planning Flask/Django project structure
- 调试 框架 issues
- Optimizing 框架 性能
- 安全 audit of Flask/Django apps
- 数据库 查询 优化

**触发短语:**
- "审查 Flask/Django 模式"
- "优化 this view"
- "检查 数据库 查询"
- "Structure Flask project"
- "改进 Django ORM usage"
- "安全 audit of Flask app"

## 功能

### 代码 Organization
- Blueprint/app structure
- View organization
- Model relationships
- 中间件 configuration

### ORM 优化
- 查询 效率
- N+1 查询 检测
- Select_related/prefetch_related usage
- 数据库 索引ing strategy

### 最佳实践
- 错误 handling 模式
- 日志 configuration
- 测试 structure
- 安全 configurations

## 常见问题

### Lazy-loaded 查询
```
Problem:
for item in items: print(item.user.name) (N+1 queries)

Consequence:
- 1 query + N queries for relationships
- Extremely slow
- Database overload

Solution:
Use select_related/prefetch_related
```

### 视图过于复杂
```
Problem:
Single view handles auth, queries, business logic, response (200+ lines)

Consequence:
- Hard to test
- Hard to maintain
- Hard to reuse

Solution:
Extract to services, use decorators
```

## 验证检查清单

- [ ] Views under 50 lines
- [ ] Business logic in 服务
- [ ] ORM 查询 optimized
- [ ] No N+1 查询 模式
- [ ] 错误 handling comprehensive
- [ ] Tests cover main paths
- [ ] 安全 checks in place
- [ ] 日志 configured

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Lazy-loaded 查询 (N+1)
❌ Views with business logic (hard to 测试)
❌ Hardcoded 数据库 connections
❌ No 错误 handling
❌ 缺失的 CSRF/XSS protection
❌ SQL injection 漏洞

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
