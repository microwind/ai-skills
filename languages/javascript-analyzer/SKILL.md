---
name: javascript-analyzer
description: "Enhanced skill for javascript-analyzer"
license: MIT
---

# JavaScript 分析r 技能

## 概述
详细的分析和验证 javascript-analyzer.

**核心原则**: JavaScript's flexibility is a double-edged sword. 分析 代码 to prevent runtime surprises.

## 何时使用

**始终:**
- JavaScript 代码 review
- 性能 优化
- Browser compatibility
- 安全 audit
- 测试 coverage
- Async 代码 分析

**触发短语:**
- "分析 JavaScript 代码"
- "审查 JavaScript 模式"
- "检查 async 代码"
- "优化 JavaScript 性能"
- "JavaScript 安全 audit"
- "改进 JavaScript testability"

## 功能

### 代码 Quality
- Async/await 模式
- 错误 handling
- 变量 scoping
- 函数 complexity

### 性能
- DOM manipulation 效率
- Event listener leaks
- 内存 leaks
- Script load 优化

### 最佳实践
- Type checking options
- 测试 模式
- 日志 approach
- 安全 practices

## 常见问题

### Callback Hell
```
Problem:
nested callbacks making code unreadable

Consequence:
- Hard to read
- Hard to error handle
- Hard to test

Solution:
Use async/await
```

### Not Awaiting Promises
```
Problem:
async function fetch().then(...) without await

Consequence:
- Race conditions
- Unexpected timing
- Bugs

Solution:
Use await or return promise chain
```

## 验证检查清单

- [ ] Async/await used correctly
- [ ] 错误 handling comprehensive
- [ ] No 内存 leaks
- [ ] DOM manipulation optimized
- [ ] Event listeners cleaned up
- [ ] Tests cover main paths
- [ ] No console.日志 in production
- [ ] Browser compatibility checked

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Callback hell (hard to read)
❌ Not handling promise rejections
❌ Blocking main thread
❌ Event listener leaks
❌ Global 变量
❌ No 错误 handling

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
