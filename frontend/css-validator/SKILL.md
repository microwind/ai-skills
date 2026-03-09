---
name: css-validator
description: "Enhanced skill for css-validator"
license: MIT
---

# CSS 验证器 技能

## 概述
详细的分析和验证 css-validator.

**核心原则**: CSS is simple to write badly, hard to maintain if done wrong. 验证 CSS for consistency and 性能.

## 何时使用

**始终:**
- Validating CSS syntax
- 性能 优化
- Accessibility review
- Responsive 设计 validation
- 代码 style enforcement
- Cross-browser compatibility

**触发短语:**
- "验证 CSS syntax"
- "优化 CSS 性能"
- "检查 responsive 设计"
- "审查 CSS specificity"
- "Accessibility audit"
- "CSS organization review"

## 功能

### Syntax Validation
- Valid CSS selectors
- Proper property values
- Color format validation
- Unit consistency

### 性能
- 未使用的 styles 检测
- Specificity 分析
- Media 查询 优化
- Animation 性能

### 最佳实践
- Naming conventions
- 组件 organization
- Responsive breakpoints
- Accessibility considerations

## 常见问题

### 高特异性
```
Problem:
.container .section .item.special#main { color: red; } (very high specificity)

Consequence:
- Hard to override
- CSS bloat
- Maintenance nightmare

Solution:
Use lower specificity, BEM naming
```

### 不响应式
```
Problem:
Fixed widths, no media queries

Consequence:
- Broken on mobile
- Bad user experience
- Low SEO

Solution:
Use responsive units, media queries
```

## 验证检查清单

- [ ] CSS syntax valid
- [ ] Selectors 使用 low specificity
- [ ] BEM or similar naming convention
- [ ] Responsive breakpoints defined
- [ ] Colors accessible (contrast ratio)
- [ ] No 未使用的 styles
- [ ] Animations performant (transform/opacity)
- [ ] Cross-browser compatible

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ High specificity (hard to override)
❌ !important everywhere
❌ Inline styles (not maintainable)
❌ Not responsive (mobile broken)
❌ Poor color contrast (accessibility)
❌ Expensive animations (paint/reflow)

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
