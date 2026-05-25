---
name: 上下文映射
description: "描述限界上下文之间的关系和集成方式，包括共享内核、防腐层、客户-供应商等模式。"
---

# 上下文映射 (Context Mapping)

## 概述

上下文映射描述**限界上下文之间的关系、依赖方向与集成方式**，是 DDD 战略设计的关键工具。它不仅是技术集成图，更刻画了**团队之间的协作关系与权力结构**——上下游、影响力、所有权都由它表达。

Eric Evans 在蓝皮书中定义了多种上下文映射模式；DDD Crew 等社区在此基础上稳定下来 **9 种**：

## 9 种上下文映射模式

### 1. Partnership（合作关系）

```
两个上下文相互依赖，任一方失败则双方失败。
团队共同规划、共同发布。

适用：两个上下文不可独立成功（例如核心交易与库存）
风险：协调成本高；要建立共同的规划与集成节奏
```

### 2. Shared Kernel（共享内核）

```
两个上下文共享一小部分明确指定的模型与代码（"内核"）。
任何修改必须双方协商。

┌──────────┐  ┌──────────┐  ┌──────────┐
│  订单    │──│ 共享内核   │──│  物流     │
│  上下文  │  │ Address   │  │  上下文   │
└──────────┘  └──────────┘  └──────────┘

适用：紧密协作、信任度高的小团队
风险：内核越大，耦合越深；内核应小而稳定
```

### 3. Customer/Supplier（客户-供应商）

```
上游（供应商）把下游（客户）的需求纳入自己的规划。
下游对上游有正式的影响力，但不参与上游模型设计。
```

```java
// 上游（供应商）：库存服务提供 API
@RestController
public class StockController {
    @GetMapping("/api/stock/{sku}")
    public StockInfo getStock(@PathVariable String sku) {
        return stockService.getAvailability(sku);
    }
}

// 下游（客户）：订单服务消费 API
public class OrderService {
    private final StockClient stockClient;

    public void placeOrder(Order order) {
        for (OrderItem item : order.getItems()) {
            StockInfo stock = stockClient.getStock(item.getSku());
            if (stock.getAvailable() < item.getQuantity()) {
                throw new InsufficientStockException(item.getSku());
            }
        }
    }
}
```

### 4. Conformist（追随者）

```
下游放弃自己的模型，直接顺从上游的模型与术语。

适用：下游无力影响上游，且翻译成本高于顺从成本
风险：上游模型变化会直接波及下游；与 ACL 相反的选择
```

### 5. Anticorruption Layer（防腐层，ACL）

```java
// ✅ 防腐层：在下游侧建立隔离层，把上游模型翻译成本上下文的模型
public class LegacyPaymentACL implements PaymentGateway {
    private final LegacyPaymentClient legacyClient;

    @Override
    public PaymentResult charge(Money amount, PaymentMethod method) {
        // 转换为遗留系统的格式
        Map<String, String> legacyParams = new HashMap<>();
        legacyParams.put("amt", amount.getValue().toString());
        legacyParams.put("cur", amount.getCurrency().code());
        legacyParams.put("type", toLegacyType(method));

        // 调用遗留系统
        LegacyResponse response = legacyClient.doPayment(legacyParams);

        // 转换回本上下文的模型
        return new PaymentResult(
            response.getCode() == 0,
            response.getTxnRef(),
            response.getMessage()
        );
    }
}
```

```python
# ✅ Python ACL 示例
class ExternalCrmAdapter:
    """防腐层：隔离外部 CRM 系统"""

    def __init__(self, crm_client):
        self.crm_client = crm_client

    def find_customer(self, customer_id: str) -> Customer:
        # 外部系统返回的是完全不同的数据结构
        raw = self.crm_client.get_contact(customer_id)

        # ACL 负责转换
        return Customer(
            id=raw["contact_id"],
            name=f"{raw['first_name']} {raw['last_name']}",
            email=raw["primary_email"],
            tier=self._map_tier(raw["membership_level"])
        )

    def _map_tier(self, level: str) -> CustomerTier:
        mapping = {"gold": CustomerTier.VIP, "silver": CustomerTier.REGULAR}
        return mapping.get(level, CustomerTier.BASIC)
```

```
适用：与遗留系统、外部第三方、不可控上游集成
代价：维护翻译层；翻译层本身也是要演化的代码
```

### 6. Open Host Service（开放主机服务）

```
上游对外提供一个标准化、稳定的协议（API），供多个下游消费；
为通用场景而设计，特殊需求由各自的翻译层处理。

┌─────────────────────────────────┐
│  库存服务 (Open Host Service)    │
│  API: REST + OpenAPI spec       │
│  事件: Avro schema              │
├─────────────────────────────────┤
│  消费方 A   消费方 B   消费方 C   │
│  订单服务   报表服务   预警服务   │
└─────────────────────────────────┘

适用：平台型 / 多消费方的能力
```

### 7. Published Language（发布语言）

```
不同上下文 / 不同组织之间，使用一种文档化、共享的语言（Schema）通信，
例如 JSON Schema、Avro、ProtoBuf、行业标准（如 HL7 / EDI）。

通常与 Open Host Service 搭配使用：协议是发布语言的载体。
```

### 8. Separate Ways（各行其道）

```
两个上下文之间没有真正的业务依赖，明确决定不集成。

适用：内部 HR 系统 与 面向客户的电商系统
价值：避免无意义的耦合
```

### 9. Big Ball of Mud（大泥球）

```
一种"反模式标记"：识别出系统中边界混乱、模型杂糅的遗留区域，
显式地把它框出来，防止其混乱扩散到其他上下文。

策略：在边界外用 ACL 隔离；逐步剥离与改造，而非贸然重构。
```

## 上下文映射图

```
绘制方法：

[订单上下文] ←—— ACL ——— [遗留 ERP]

[订单上下文] ── 客户/供应商 ──▶ [库存上下文]

[订单上下文] ── 发布事件 ──▶ [通知上下文]
                          ──▶ [分析上下文]

[认证上下文] ── 共享内核 ── [用户上下文]
```

## 选择集成模式

| 场景 | 推荐模式 |
|------|---------|
| 与遗留系统 / 外部不可控系统集成 | Anticorruption Layer |
| 无影响力且翻译成本高 | Conformist |
| 双方共担成败、协同发布 | Partnership |
| 小而稳定的共享概念 | Shared Kernel |
| 明确上下游协作 | Customer/Supplier |
| 平台型 / 多个下游消费 | Open Host Service |
| 跨组织 / 跨服务事件流 | Published Language |
| 完全独立的系统 | Separate Ways |
| 框出杂乱遗留区域 | Big Ball of Mud |

## 落地建议

- **9 种模式是工具箱，不是清单**：实际项目通常只用到 3–4 种，按真实集成关系挑选，不必为完整性强行套用。
- **不必画一张大图**：DDD Crew 推荐**按问题域绘制多张小图**——例如"我们与支付系统的关系图""核心交易内部的上下文关系图"，每张图只回答一个具体问题。
- **关系是会演化的**：今天的 Conformist 明天可能变成 ACL；上下文映射是活文档，应该随系统演进定期更新。
- **避免反向推导**：不要先决定"我们要用 ACL"再去找用 ACL 的理由；先识别上下文之间的真实关系（依赖方向、影响力、信任度），再让模式自然浮现。

## 常见误区

❌ **默认所有依赖都加 ACL**——每接入一个上下文就先建翻译层，过度设计
→ 简单稳定的依赖直接用 Open Host Service 或 Conformist；ACL 留给"模型必须隔离"的场景

❌ **把"调用关系图"当 Context Map**——只画了谁调谁，没标依赖方向 / 影响力 / 关系类型
→ Context Map 的价值在于刻画**关系类型**（Customer/Supplier、Conformist、Partnership 等），不止是箭头

❌ **不画也不澄清依赖**——团队凭口口相传集成，上下游分歧反复爆发
→ 哪怕只画一张白板小图，把关键关系类型标出来，对集成谈判和职责划分帮助巨大

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [限界上下文](../bounded-context/) | 上下文映射描述限界上下文之间的关系 |
| [领域事件](../domain-events/) | 事件是上下文间异步通信的常用方式 |
| [微服务中的DDD](../ddd-in-microservices/) | 上下文映射指导微服务间的集成 |

## 总结

**核心**：上下文映射不仅是技术集成方案，更是团队协作与权力关系的可视化。

**关键模式**：Anticorruption Layer 隔离外部模型，Customer/Supplier 明确依赖方向，Open Host Service 标准化对外能力，Conformist / Separate Ways 表达"主动放弃"或"不集成"的清醒选择。
