---
name: cloud-config-analyzer
description: "Enhanced skill for cloud-config-analyzer"
license: MIT
---

# Cloud Config 分析r 技能

## 概述
详细的分析和验证 cloud-config-analyzer.

**核心原则**: Misconfigured cloud 资源 leak data, waste money, and expose 安全 漏洞.

## 何时使用

**始终:**
- Before deploying to cloud
- 审查ing cloud infrastructure
- Optimizing cloud costs
- 安全 audit of cloud 资源
- Planning cloud 迁移
- Investigating cloud failures

**触发短语:**
- "验证 cloud config"
- "检查 cloud 安全"
- "优化 cloud costs"
- "审查 cloud 资源"
- "查找 cloud misconfigurations"
- "验证 cloud permissions"

## 功能

### 安全 检查s
- Public bucket 检测
- Default 安全 group rules
- Unencrypted 数据库s
- 缺失的 加密 keys

### Cost 优化
- 未使用的 资源 检测
- Instance size recommendations
- Storage 优化
- Bandwidth 分析

### Configuration Validation
- IAM policy verification
- Network configuration
- 数据库 backup settings
- 日志 configuration

## 常见问题

### Publicly Accessible Bucket
```
Problem:
S3 bucket with public read/write access

Consequence:
- Data exposed to internet
- Anyone can download files
- Compliance violation

Solution:
Remove public ACLs, use bucket policies
```

### Unencrypted 数据库
```
Problem:
RDS database without encryption at rest

Consequence:
- Data exposed if disk stolen
- Compliance violation
- Regulatory fines

Solution:
Enable encryption at rest
```

### Default 安全 Group
```
Problem:
Security group allows all inbound traffic

Consequence:
- Exposed to the internet
- Unnecessary security risk
- Compliance issue

Solution:
Restrict to specific ports/IPs
```

## 验证检查清单

- [ ] No publicly accessible storage
- [ ] 加密 enabled for sensitive data
- [ ] IAM policies follow least privilege
- [ ] Backup and recovery tested
- [ ] VPC configured correctly
- [ ] 安全 groups restrictive
- [ ] 日志 enabled
- [ ] Cost 优化 reviewed

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Public storage buckets (data leak)
❌ Wide-open 安全 groups (安全 risk)
❌ Unencrypted sensitive data
❌ Root account for everything (IAM issues)
❌ No backup strategy
❌ Oversized instances (wasted money)

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
