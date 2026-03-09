---
name: cicd-validator
description: "Enhanced skill for cicd-validator"
license: MIT
---

# CI/CD 验证器 技能

## 概述
详细的分析和验证 cicd-validator.

**核心原则**: Bad CI/CD pipelines hide 问题 until production. 验证管道质量以尽早发现问题.

## 何时使用

**始终:**
- Setting up CI/CD pipelines
- 审查ing GitHub Actions workflows
- Optimizing pipeline 性能
- 调试 pipeline failures
- Planning 部署 strategy
- 安全 audit of pipelines

**触发短语:**
- "验证 CI/CD pipeline"
- "审查 GitHub Actions workflow"
- "优化 pipeline 性能"
- "Why did the build fail?"
- "设计 部署 strategy"
- "检查 pipeline 安全"

## 功能

### Pipeline Structure
- Stage sequencing
- Parallel job 优化
- Dependency management
- Artifact handling

### Quality 检查s
- 测试 coverage enforcement
- 代码 style validation
- 安全 扫描
- Dependency checking

### 部署 Safety
- 环境 separation
- Approval gates
- Rollback strategy
- Health checks after deploy

## 常见问题

### 缓慢 Pipeline
```
Problem:
Tests run sequentially instead of parallel, 30 min build time

Consequence:
- Slow feedback to developers
- Low deployment frequency
- Bottleneck

Solution:
Run tests in parallel, cache dependencies
```

### No 测试 Coverage Gate
```
Problem:
Pipeline doesn't fail if test coverage decreases

Consequence:
- Code quality degrades over time
- Bugs not caught
- Technical debt

Solution:
Add coverage threshold check, fail if below threshold
```

### Manual Approval Gate 缺失的
```
Problem:
Any commit auto-deploys to production

Consequence:
- Broken features deploy
- Data loss possible
- Downtime risk

Solution:
Add approval gate before production deployment
```

## 验证检查清单

- [ ] All tests run automatically
- [ ] 代码 quality checks enforce standards
- [ ] 安全 扫描 enabled
- [ ] Artifacts properly versioned
- [ ] Environments properly separated
- [ ] Manual approval for production
- [ ] 部署 health checks
- [ ] Rollback procedure documented

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Manual 部署 steps
❌ No 测试 coverage enforcement
❌ Sequential job 执行ion (缓慢)
❌ No approval gates to production
❌ Credentials in pipeline files
❌ No rollback plan

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
