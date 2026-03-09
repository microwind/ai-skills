---
name: api-contract-validator
description: "Enhanced skill for api-contract-validator"
license: MIT
---

# API Contract 验证器 技能

## 概述
详细的分析和验证 api-contract-validator.

**核心原则**: 服务 集成 depends on API contracts. Breaking contracts breaks 集成.

## 何时使用

**始终:**
- Microservice API review
- Contract 测试 planning
- API versioning strategy
- 集成 测试
- Backward compatibility checking
- 模式 evolution planning

**触发短语:**
- "验证 API contract"
- "审查 API breaking changes"
- "检查 backward compatibility"
- "Plan API versioning"
- "Contract 测试 setup"
- "分析 模式 evolution"

## 功能

### Contract Definition
- 请求 模式 validation
- 响应 模式 validation
- 头部 requirements
- 状态码 meanings

### Compatibility
- Breaking change 检测
- Backward compatibility
- Forward compatibility
- 版本 management

### 测试
- Contract 测试 generation
- Mock 服务器 generation
- Consumer validation
- Provider validation

## 常见问题

### Breaking Change
```
Problem:
API changed request format without versioning

Consequence:
- Old clients break
- Integration fails
- Downtime

Solution:
Use versioning, document breaking changes
```

### 缺失的 Validation
```
Problem:
Consumer doesn't validate response schema

Consequence:
- Unexpected fields ignored
- Missing fields cause errors

Solution:
Add schema validation in consumer
```

## 验证检查清单

- [ ] 请求 模式 defined and validated
- [ ] 响应 模式 defined and validated
- [ ] 状态码 documented
- [ ] 错误 响应 consistent
- [ ] API versioning strategy clear
- [ ] Breaking changes documented
- [ ] Backward compatible changes tested
- [ ] Contract tests passing

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ No API versioning
❌ No 模式 validation
❌ Breaking changes without notice
❌ No contract 测试
❌ Implicit requirements (not documented)
❌ No deprecation period for changes

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
