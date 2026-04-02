---
name: 通用语言
description: "团队共享的业务语言，开发者与领域专家使用相同的术语沟通，代码直接反映业务概念。"
license: MIT
---

# 通用语言 (Ubiquitous Language)

## 概述

通用语言是DDD的基石：**开发团队和业务专家共同建立并使用的语言，贯穿于沟通、文档和代码中**。

**核心思想**：
- 代码中的命名 = 业务专家使用的术语
- 消除"翻译层"——开发者和业务人员说同一种话
- 语言的变化意味着模型的变化

## 对比示例

```java
// ❌ 技术语言：开发者能看懂，业务专家看不懂
public class DataProcessor {
    public void processRecord(Map<String, Object> record) {
        if ((int) record.get("type") == 1) {
            record.put("status", 2);
            dbHelper.updateRow("tbl_data", record);
        }
    }
}

// ✅ 通用语言：业务专家也能理解
public class LoanApplication {
    public void approve(Underwriter approvedBy) {
        if (this.status != ApplicationStatus.UNDER_REVIEW) {
            throw new DomainException("只有审核中的申请才能批准");
        }
        this.status = ApplicationStatus.APPROVED;
        this.approvedBy = approvedBy;
        this.approvedAt = LocalDateTime.now();
    }

    public void reject(Underwriter rejectedBy, String reason) {
        this.status = ApplicationStatus.REJECTED;
        this.rejectionReason = reason;
    }
}
```

```python
# ❌ 技术术语
class Handler:
    def handle(self, dto):
        entity = self.repo.get(dto.id)
        entity.flag = True
        self.repo.update(entity)

# ✅ 通用语言
class ClaimService:
    def submit_claim(self, policy_holder_id: str, incident_details: str):
        policy = self.policy_repo.find_active(policy_holder_id)
        claim = policy.file_claim(incident_details)
        self.claim_repo.save(claim)
        return claim
```

## 建立通用语言的方法

```
1. 事件风暴（Event Storming）
   - 用便签列出所有领域事件（"订单已提交"、"支付已完成"）
   - 识别命令（"提交订单"、"确认支付"）
   - 发现聚合和限界上下文

2. 术语表
   | 术语 | 定义 | 上下文 |
   |------|------|--------|
   | 保单 | 保险合同 | 保险 |
   | 理赔 | 保险事故后申请赔偿 | 理赔 |
   | 核保 | 评估风险决定是否承保 | 承保 |

3. 代码即文档
   - 类名、方法名、变量名都使用通用语言
   - 业务专家能读懂代码（至少是方法签名）
```

## 通用语言的约束

```
通用语言在限界上下文内有效：

上下文A（销售）          上下文B（物流）
"订单" = 客户的购买请求   "订单" = 需要配送的包裹
"取消" = 退回商品金额     "取消" = 停止配送流程
"地址" = 收货地址         "地址" = 仓库/中转站地址

→ 不同上下文可以用相同的词表达不同的概念
→ 这正是限界上下文存在的原因
```

## 命名检查清单

```
□ 类名是业务名词（Order, Claim, Policy）而非技术名词（DataObject, Record）
□ 方法名是业务动作（approve, submit, cancel）而非技术动作（update, process)
□ 枚举值反映业务状态（APPROVED, REJECTED）而非数字（1, 2, 3）
□ 业务专家能理解方法签名的含义
□ 代码注释用业务术语解释"为什么"，而非"做什么"
```

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [限界上下文](../bounded-context/) | 通用语言在限界上下文内有效 |
| [领域模型](../domain-model/) | 通用语言通过领域模型在代码中体现 |
| [领域事件](../domain-events/) | 事件名使用通用语言描述 |

## 总结

**核心**：开发者和业务专家使用同一套语言，代码反映业务术语。

**实践**：通过事件风暴建立术语表，代码命名使用业务概念，在限界上下文内保持语言一致。
