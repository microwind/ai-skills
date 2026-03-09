---
name: service-mesh-analyzer
description: "Enhanced skill for service-mesh-analyzer"
license: MIT
---

# 服务 Mesh 分析r 技能

## 概述
详细的分析和验证 服务-mesh-analyzer.

**核心原则**: 服务 mesh adds complexity to solve 问题. Make sure it's solving the right 问题.

## 何时使用

**始终:**
- Planning 服务 mesh adoption
- 服务 mesh configuration review
- Traffic management 优化
- 安全 policy review
- 性能 监控
- Troubleshooting mesh issues

**触发短语:**
- "分析 服务 mesh setup"
- "审查 Istio configuration"
- "优化 服务 mesh 性能"
- "服务 mesh 安全 audit"
- "检查 traffic routing"
- "服务 mesh troubleshooting"

## 功能

### Traffic Management
- Load balancing strategy
- Circuit breaker configuration
- Retry policy
- Timeout settings

### 安全
- mTLS configuration
- 授权 policies
- 身份认证 setup
- Certificate rotation

### Observability
- Distributed tracing
- Metrics collection
- 错误 tracking
- 性能 监控

## 常见问题

### Misconfigured Circuit Breaker
```
Problem:
Circuit breaker trips too early or never breaks

Consequence:
- Unnecessary timeouts or cascading failures
- Service unavailable

Solution:
Tune thresholds based on actual metrics
```

### 缺失的 Timeout
```
Problem:
No timeout configured, requests hang forever

Consequence:
- Resource exhaustion
- Cascading failures
- Degradation

Solution:
Set appropriate timeout values
```

## 验证检查清单

- [ ] mTLS enabled between 服务
- [ ] 授权 policies defined
- [ ] Circuit breakers configured
- [ ] Timeouts appropriate
- [ ] Retries configured
- [ ] Distributed tracing enabled
- [ ] Metrics collected
- [ ] Alerts configured

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ 服务 mesh for 2 服务 (overkill)
❌ mTLS disabled (安全 risk)
❌ No circuit breakers (cascading failures)
❌ No timeouts (hanging 请求)
❌ 缺失的 observability (blind)
❌ All traffic retried (amplification)

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
