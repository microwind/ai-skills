---
name: python-analyzer
description: "Enhanced skill for python-analyzer"
license: MIT
---

# Python 分析r 技能

## 概述
详细的分析和验证 python-analyzer.

**核心原则**: Python makes it easy to write bad 代码. 分析 代码 quality to prevent technical debt.

## 何时使用

**始终:**
- Python 代码 review
- 性能 优化
- Type safety checking
- 测试 strategy
- 安全 audit
- Maintainability assessment

**触发短语:**
- "分析 Python 代码 quality"
- "审查 Python 模式"
- "优化 Python 性能"
- "检查 Python type hints"
- "Python 安全 audit"
- "改进 Python testability"

## 功能

### 代码 Quality
- PEP 8 合规性
- Type hint coverage
- Complexity 分析
- Naming conventions

### 性能
- Algorithm 效率
- 内存 usage
- Dependency imports
- Loop 优化

### 最佳实践
- 异常 handling
- 错误 messages
- 日志 模式
- 测试 coverage

## 常见问题

### 没有类型提示
```
Problem:
def process(data): ... (what type is data?)

Consequence:
- IDE can't help
- Runtime errors
- Hard to understand

Solution:
Add type hints: def process(data: Dict[str, Any]) -> bool:
```

### 可变默认参数
```
Problem:
def append(item, items=[]) (default list shared across calls)

Consequence:
- Unexpected behavior
- Items persist between calls
- Bugs

Solution:
Use None: def append(item, items=None):
```

## 验证检查清单

- [ ] Type hints on all 函数
- [ ] No bare except clauses
- [ ] 异常 types specific
- [ ] Docstrings present
- [ ] Tests cover main paths
- [ ] 性能 accep表
- [ ] 安全 checked
- [ ] 代码 style consistent

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ No type hints
❌ Bare except (catch everything)
❌ Mu表 default arguments
❌ Global 变量
❌ No 错误 handling
❌ Print 调试 (使用 日志)

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
