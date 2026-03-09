---
name: spring-analyzer
description: "Enhanced skill for spring-analyzer"
license: MIT
---

# Spring 框架 分析r 技能

## 概述
详细的分析和验证 spring-analyzer.

**核心原则**: Spring enables enterprise features but bad configuration leads to 缓慢, unmaintainable 代码.

## 何时使用

**始终:**
- 审查ing Spring 代码
- Spring Boot configuration
- 性能 优化
- Dependency injection review
- 安全 audit of Spring apps
- 数据库 access 优化

**触发短语:**
- "审查 Spring 模式"
- "优化 Spring 性能"
- "Spring data JPA 分析"
- "检查 Spring 安全 config"
- "Spring 事务 handling"
- "分析 Spring bean configuration"

## 功能

### Bean Configuration
- Dependency injection 模式
- Bean lifecycle
- Singleton vs prototype
- Circular dependency 检测

### 性能
- Lazy initialization strategy
- 数据库 connection pooling
- 缓存 configuration
- 查询 优化

### 最佳实践
- 异常 handling
- 日志 configuration
- Unit 测试 模式
- 集成 测试 setup

## 常见问题

### 循环依赖
```
Problem:
Bean A depends on B, Bean B depends on A

Consequence:
- Wiring fails
- App won't start
- Refactoring needed

Solution:
Restructure beans, use setter injection
```

### 缓慢 查询
```
Problem:
Spring Data JPA lazy loading in loops

Consequence:
- N+1 queries
- Database overload
- Timeouts

Solution:
Use @EntityGraph or fetch joins
```

## 验证检查清单

- [ ] No circular dependencies
- [ ] 事务 boundaries clear
- [ ] Connection pool configured
- [ ] Lazy loading minimized
- [ ] 异常 handling comprehensive
- [ ] 日志 configured
- [ ] Tests cover main paths
- [ ] 安全 properly configured

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Circular dependencies
❌ Lazy loading in loops (N+1)
❌ Global 异常 handlers (lose context)
❌ No 事务 management
❌ Blocking I/O in async 代码
❌ Hardcoded configuration

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
