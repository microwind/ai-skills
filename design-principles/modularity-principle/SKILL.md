---
name: 模块化原则
description: "将系统分解为独立、可替换的模块，每个模块高内聚低耦合，可独立开发、测试和部署。"
license: MIT
---

# 模块化原则 (Modularity Principle)

## 概述

模块化是管理复杂性的核心手段：**将系统分解为独立的模块，每个模块封装一组相关功能，通过明确的接口与外部交互**。

**核心指标**：
- **高内聚**：模块内部元素紧密相关
- **低耦合**：模块之间依赖最小化
- **可替换**：模块可以独立替换而不影响其他模块

## 好的模块 vs 差的模块

```java
// ❌ 低内聚高耦合：工具类
public class Utils {
    public static String formatDate(Date d) { /* ... */ }
    public static double calculateTax(double amount) { /* ... */ }
    public static void sendEmail(String to, String body) { /* ... */ }
    public static byte[] compressImage(byte[] data) { /* ... */ }
    // 完全不相关的功能放在一起
}

// ✅ 高内聚低耦合：按领域划分模块
// pricing 模块
public class PricingService {
    public double calculateSubtotal(List<Item> items) { /* ... */ }
    public double applyDiscount(double amount, Discount discount) { /* ... */ }
    public double calculateTax(double amount, TaxRegion region) { /* ... */ }
}

// notification 模块
public class NotificationService {
    public void sendEmail(String to, EmailTemplate template) { /* ... */ }
    public void sendSMS(String phone, String message) { /* ... */ }
}
```

## 模块边界设计

```
项目结构示例：

✅ 按功能/领域划分
src/
├── order/              # 订单模块
│   ├── OrderService.java
│   ├── OrderRepository.java
│   └── Order.java
├── payment/            # 支付模块
│   ├── PaymentService.java
│   └── PaymentGateway.java
├── shipping/           # 物流模块
│   ├── ShippingService.java
│   └── ShippingCalculator.java
└── notification/       # 通知模块
    ├── NotificationService.java
    └── EmailTemplate.java

❌ 按技术层划分（低内聚）
src/
├── controllers/        # 所有控制器混在一起
├── services/           # 所有服务混在一起
├── repositories/       # 所有仓储混在一起
└── models/             # 所有模型混在一起
```

## 模块间通信

```python
# ✅ 通过接口通信，不直接依赖实现
from abc import ABC, abstractmethod

# 支付模块定义接口
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float, method: str) -> str: pass

# 订单模块通过接口使用支付
class OrderService:
    def __init__(self, payment: PaymentGateway):
        self.payment = payment

    def complete_order(self, order):
        tx_id = self.payment.charge(order.total, order.payment_method)
        order.confirm(tx_id)

# 模块间通过事件解耦
class EventBus:
    def publish(self, event: str, data: dict): pass

class OrderService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def complete_order(self, order):
        order.confirm()
        self.event_bus.publish("order.completed", {"order_id": order.id})
        # 通知模块、物流模块各自订阅处理
```

## 内聚度量

| 内聚类型 | 程度 | 说明 |
|----------|------|------|
| 功能内聚 | 最高 ✅ | 所有元素完成同一功能 |
| 顺序内聚 | 高 | 一个元素的输出是另一个的输入 |
| 通信内聚 | 中 | 操作同一数据集 |
| 时间内聚 | 低 | 只是同时执行（如初始化） |
| 逻辑内聚 | 很低 | 逻辑相似但功能不同 |
| 偶然内聚 | 最低 ❌ | 无关元素放在一起（Utils类） |

## 耦合度量

| 耦合类型 | 程度 | 说明 |
|----------|------|------|
| 消息耦合 | 最低 ✅ | 通过消息/事件通信 |
| 数据耦合 | 低 | 只传递简单数据 |
| 接口耦合 | 中 | 通过接口交互 |
| 控制耦合 | 高 | 传递控制标志影响行为 |
| 内容耦合 | 最高 ❌ | 直接访问内部数据 |

## 最佳实践

1. **一个模块一个职责域** - 按业务能力划分，不按技术层划分
2. **明确公开接口** - 只暴露必要的 API，隐藏实现细节
3. **依赖接口不依赖实现** - 模块间通过抽象通信
4. **独立可测试** - 每个模块可以独立运行单元测试

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [SRP](../single-responsibility-principle/) | 模块级别的单一职责 |
| [封装](../encapsulation-principle/) | 模块封装内部实现 |
| [关注点分离](../separation-of-concerns/) | 每个模块处理一个关注点 |

## 总结

**模块化核心**：高内聚、低耦合、明确边界。

**实践要点**：
- 按业务领域而非技术层划分模块
- 模块通过接口或事件通信
- 追求功能内聚，避免偶然内聚
- 模块可独立开发、测试、部署
