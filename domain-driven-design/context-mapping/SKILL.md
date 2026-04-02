---
name: 上下文映射
description: "描述限界上下文之间的关系和集成方式，包括共享内核、防腐层、客户-供应商等模式。"
license: MIT
---

# 上下文映射 (Context Mapping)

## 概述

上下文映射描述**限界上下文之间的关系和集成方式**，是DDD战略设计的关键工具。

## 集成模式

### 1. 共享内核 (Shared Kernel)

```
两个上下文共享一小部分模型，需要双方协调修改。

┌──────────┐  ┌───────┐  ┌──────────┐
│  订单    │──│ 共享  │──│  物流    │
│  上下文  │  │ Address│  │  上下文  │
└──────────┘  └───────┘  └──────────┘

适用：紧密协作的团队
风险：修改共享部分影响双方
```

### 2. 客户-供应商 (Customer-Supplier)

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

### 3. 防腐层 (Anti-Corruption Layer, ACL)

```java
// ✅ 防腐层：隔离外部系统的模型，转换为本上下文的模型
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
    """防腐层：隔离外部CRM系统"""

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

### 4. 开放主机服务 (Open Host Service) + 发布语言

```
提供标准化的 API + 明确的数据契约：

┌─────────────────────────────────┐
│  库存服务 (Open Host Service)    │
│  API: REST + OpenAPI spec       │
│  事件: Avro schema              │
├─────────────────────────────────┤
│  消费方A    消费方B    消费方C    │
│  订单服务   报表服务   预警服务   │
└─────────────────────────────────┘
```

### 5. 各行其道 (Separate Ways)

```
完全不集成，各自独立实现：

适用：两个上下文之间没有真正的业务依赖
例：内部 HR 系统 和 面向客户的电商系统
```

## 上下文映射图

```
绘制方法：

[订单上下文] ←ACL-- [遗留ERP]

[订单上下文] --客户/供应商→ [库存上下文]

[订单上下文] --发布事件→ [通知上下文]
                      → [分析上下文]

[认证上下文] --共享内核-- [用户上下文]
```

## 选择集成模式

| 场景 | 推荐模式 |
|------|---------|
| 与遗留系统集成 | 防腐层 |
| 团队间紧密协作 | 共享内核 |
| 上游有明确API | 客户-供应商 |
| 多个消费方 | 开放主机服务 |
| 完全独立的系统 | 各行其道 |
| 事件驱动通信 | 发布语言 |

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [限界上下文](../bounded-context/) | 上下文映射描述限界上下文之间的关系 |
| [领域事件](../domain-events/) | 事件是上下文间异步通信的常用方式 |
| [微服务中的DDD](../ddd-in-microservices/) | 上下文映射指导微服务间的集成 |

## 总结

**核心**：明确限界上下文之间的关系和集成方式。

**关键模式**：防腐层隔离外部模型，客户-供应商定义依赖方向，开放主机服务标准化 API。
