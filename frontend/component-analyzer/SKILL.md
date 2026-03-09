---
name: component-analyzer
description: "Enhanced skill for component-analyzer"
license: MIT
---

# 组件 分析r 技能

## 概述
详细的分析和验证 组件-analyzer.

**核心原则**: Good 组件 are reusable, tes表, and composable. Bad 组件 are brittle and hard to maintain.

## 何时使用

**始终:**
- 审查ing React/Vue/Angular 组件
- Planning 组件 架构
- 组件 reusability audit
- 性能 优化
- 测试 strategy planning
- API contract validation

**触发短语:**
- "分析 组件 structure"
- "审查 组件 设计"
- "组件 reusability audit"
- "优化 组件 rendering"
- "组件 API review"
- "改进 组件 testability"

## 功能

### 组件 设计
- Props/input validation
- State management approach
- Lifecycle understanding
- Composition 模式

### 性能
- Unnecessary re-renders
- Memoization opportunities
- Bundle size impact
- Lazy loading strategy

### Reusability
- Props flexibility
- Composition ability
- Customization options
- Variant handling

## 常见问题

### Over-Specific 组件
```
Problem:
Component hardcoded for one use case, not reusable

Consequence:
- Can't reuse elsewhere
- Code duplication
- Maintenance burden

Solution:
Extract props, make flexible
```

### 不必要的重新渲染
```
Problem:
Parent re-renders, all children re-render even unchanged

Consequence:
- Performance degradation
- Slow app
- Bad user experience

Solution:
Use React.memo, useMemo
```

## 验证检查清单

- [ ] 组件 props clearly defined
- [ ] State minimal and local
- [ ] No unnecessary side effects
- [ ] Reusable across contexts
- [ ] 性能 optimized
- [ ] Tes表 in isolation
- [ ] 错误 states handled
- [ ] Props documented

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Over-specific (not reusable)
❌ Prop drilling (too many props passed)
❌ Global state for everything
❌ No 错误 boundaries
❌ Side effects in render
❌ Tightly coupled to parent

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
