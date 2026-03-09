---
name: kubernetes-validator
description: "Enhanced skill for kubernetes-validator"
license: MIT
---

# Kubernetes 验证器 技能

## 概述
详细的分析和验证 Kubernetes-validator.

**核心原则**: 无效的Kubernetes清单会静默部署然后神秘失败. 在部署前进行验证.

## 何时使用

**始终:**
- Before deploying to Kubernetes
- Validating YAML manifests
- 检查ing 资源 definitions
- 调试 pod failures
- Planning 资源 limits
- 审查ing 部署 configs

**触发短语:**
- "Is this Kubernetes config valid?"
- "验证 K8s manifest"
- "检查 pod definition"
- "审查 部署 config"
- "Why won't this deploy?"
- "验证 服务 mesh config"

## 功能

### YAML Validation
- Syntax validation
- Required fields checking
- Type validation
- 资源 limits validation

### 最佳实践 检查
- 资源 limits defined
- Health checks configured
- 安全 policies checked
- Image pull policies correct

### Configuration 分析
- 服务 discovery setup
- Volume mounts validation
- 环境 变量
- Secret management

## 常见问题

### 缺失的 资源 Limits
```
Problem:
Pod without CPU/memory limits

Consequence:
- Pod uses all available resources
- Starves other pods
- Cluster becomes unstable

Solution:
Add resources.limits and resources.requests
```

### No Health 检查s
```
Problem:
Deployment without liveness/readiness probes

Consequence:
- Pod marked healthy when failing
- Traffic sent to failing pods
- Bad user experience

Solution:
Add livenessProbe and readinessProbe
```

### Invalid Image
```
Problem:
Image doesn't exist or wrong registry

Consequence:
- Pod never starts
- ImagePullBackOff error
- Service unavailable

Solution:
Verify image exists, use correct registry URL
```

## 验证检查清单

- [ ] YAML syntax valid
- [ ] All required fields present
- [ ] 资源 limits set
- [ ] Health probes configured
- [ ] Image pull policy correct
- [ ] 服务 labels match selectors
- [ ] 环境 变量 defined
- [ ] 安全 context configured

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ No 资源 limits (pod can crash cluster)
❌ No health checks (traffic to dead pods)
❌ Latest image tag (unpredic表 版本)
❌ Running as root (安全 risk)
❌ Storing secrets in ConfigMap
❌ No pod disruption budgets

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
