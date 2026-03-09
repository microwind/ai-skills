---
name: infrastructure-analyzer
description: "Enhanced skill for infrastructure-analyzer"
license: MIT
---

# Infrastructure 分析r 技能

## 概述
详细的分析和验证 infrastructure-analyzer.

**核心原则**: 好的基础设施可以扩展. 糟糕的基础设施在扩展时会崩溃. 分析 before 问题 cascade.

## 何时使用

**始终:**
- Planning infrastructure
- Scaling for growth
- 性能 bottleneck investigation
- Disaster recovery planning
- Cost 优化
- Infrastructure 代码 review

**触发短语:**
- "分析 infrastructure 设计"
- "Scale this for 10x growth"
- "查找 infrastructure bottlenecks"
- "Plan disaster recovery"
- "优化 infrastructure costs"
- "审查 infrastructure as 代码"

## 功能

### Capacity Planning
- Current utilization 分析
- Growth projections
- Scaling bottlenecks
- 资源 requirements

### High Availability
- Single points of failure 检测
- Failover strategy 分析
- Backup completeness
- Disaster recovery validation

### Cost 优化
- 资源 utilization 分析
- Right-sizing recommendations
- Reserved capacity 分析
- Unnecessary 服务

## 常见问题

### Single Point of Failure
```
Problem:
Only one database server, no replication

Consequence:
- Server fails -> entire app down
- No disaster recovery
- RTO is infinite

Solution:
Add replica, failover automation
```

### No Backup Strategy
```
Problem:
Data deleted -> no backup to restore

Consequence:
- Data loss forever
- No recovery possible
- Regulatory violations

Solution:
Regular backups, test restore procedures
```

### Manual Scaling
```
Problem:
Traffic spikes -> manually provision servers

Consequence:
- Delayed response to load
- Expensive
- User impact

Solution:
Auto-scaling groups, load balancing
```

## 验证检查清单

- [ ] No single points of failure
- [ ] Backup strategy documented and tested
- [ ] Failover automation in place
- [ ] 监控 and alerting configured
- [ ] Scaling plan documented
- [ ] Disaster recovery tested
- [ ] Cost 优化 reviewed
- [ ] 安全 hardened

## 当困难时

| 问题 | 解决方案 |
|---------|----------|
| "Not sure where to start" | 识别 the specific issue using the 常见问题 section above. |
| "性能 is poor" | Profile first to 识别 bottleneck before optimizing. |
| "Not sure about 最佳实践" | 检查 the 验证检查清单 to understand quality standards. |

## 反模式 (红旗警告)

❌ Single 服务器 (single point of failure)
❌ Manual scaling (缓慢, expensive)
❌ No backups (data loss risk)
❌ No 监控 (问题 unknown)
❌ Tight coupling (can't scale independently)
❌ No disaster recovery plan

## 相关技能

- **代码-review** - 审查 implementation of this 技能
- **架构-analyzer** - 分析 larger 设计 implications
