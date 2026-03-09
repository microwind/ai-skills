---
name: bundle-analyzer
description: "Enhanced skill for bundle-analyzer"
license: MIT
---

# Bundle 分析r 技能

## 概述
详细的分析和验证 bundle-analyzer.

**核心原则**: Bundle size directly impacts page load time. Smaller bundles = 快速er pages = better UX.

## 何时使用

**始终:**
- Optimizing bundle size
- 性能 budgeting
- Dependency 分析
- 代码 splitting planning
- 性能 监控
- Production 部署 review

**触发短语:**
- "分析 bundle size"
- "优化 JavaScript bundle"
- "查找 代码 splitting opportunities"
- "检查 dependency sizes"
- "性能 budget review"
- "Bundle 分析 report"

## 功能

### Bundle 分析
- Total bundle size
- Individual 模块 sizes
- Dependency relationships
- Duplicate 检测

### 优化
- 代码 splitting opportunities
- Tree-shaking effectiveness
- Compression 分析
- Dynamic import candidates

### 性能
- Load time estimation
- 内存 impact
- Parse time 分析
- 缓存 effectiveness

## 常见问题

### 大型依赖
```
Problem:
Including entire lodash library for one function

Consequence:
- Bundle 50KB larger
- Slower load
- Slower parse

Solution:
Use cherry-pick imports or smaller libraries
```

### No 代码 Splitting
```
Problem:
All code in single bundle, even admin pages users never visit

Consequence:
- Initial load slow
- Wasted bandwidth
- Slow FCP

Solution:
Route-based code splitting
```

## 验证检查清单

- [ ] Bundle size under budget
- [ ] No duplicate dependencies
- [ ] Large dependencies justified
- [ ] 代码 splitting implemented
- [ ] Tree-shaking enabled
- [ ] Compression optimized
- [ ] 缓存 头部 configured
- [ ] 性能 budget enforced

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ No 代码 splitting
❌ Large dependencies for small 使用 cases
❌ Duplicate dependencies
❌ No tree-shaking
❌ Development dependencies in production
❌ No compression

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
