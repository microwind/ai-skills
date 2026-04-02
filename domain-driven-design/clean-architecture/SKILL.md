---
name: 清洁架构
description: "通过依赖规则将系统分为同心圆层次，内层不依赖外层，实现业务逻辑与技术细节的完全分离。"
license: MIT
---

# 清洁架构 (Clean Architecture)

## 概述

清洁架构由 Robert C. Martin（Uncle Bob）提出，核心是**依赖规则：源码依赖只能指向内层**。

```
┌─────────────────────────────────────────┐
│  Frameworks & Drivers (最外层)           │
│  Web框架、数据库、UI                      │
│  ┌─────────────────────────────────┐    │
│  │  Interface Adapters              │    │
│  │  控制器、Gateway、Presenter       │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │  Application (Use Cases) │    │    │
│  │  │  应用业务规则             │    │    │
│  │  │  ┌─────────────────┐    │    │    │
│  │  │  │  Entities        │    │    │    │
│  │  │  │  企业业务规则     │    │    │    │
│  │  │  └─────────────────┘    │    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

依赖方向：外 → 内（箭头永远指向中心）
```

## 代码示例

```java
// ===== 最内层：Entities（领域模型） =====
public class Order {
    private OrderId id;
    private List<OrderItem> items;
    private OrderStatus status;

    public void place() {
        if (items.isEmpty()) throw new DomainException("订单不能为空");
        this.status = OrderStatus.PLACED;
    }
}

// ===== Use Cases 层 =====
// 输入端口
public interface PlaceOrderUseCase {
    PlaceOrderOutput execute(PlaceOrderInput input);
}

// 输出端口
public interface OrderGateway {
    Order findById(String id);
    void save(Order order);
}

// 用例实现
public class PlaceOrderInteractor implements PlaceOrderUseCase {
    private final OrderGateway orderGateway;

    @Override
    public PlaceOrderOutput execute(PlaceOrderInput input) {
        Order order = orderGateway.findById(input.getOrderId());
        order.place();
        orderGateway.save(order);
        return new PlaceOrderOutput(order.getId(), order.getStatus());
    }
}

// ===== Interface Adapters 层 =====
@RestController
public class OrderController {
    private final PlaceOrderUseCase placeOrder;

    @PostMapping("/orders/{id}/place")
    public ResponseEntity<?> place(@PathVariable String id) {
        var output = placeOrder.execute(new PlaceOrderInput(id));
        return ResponseEntity.ok(OrderResponse.from(output));
    }
}

// ===== Frameworks 层 =====
@Repository
public class JpaOrderGateway implements OrderGateway {
    @Override
    public Order findById(String id) { /* JPA 实现 */ }
    @Override
    public void save(Order order) { /* JPA 实现 */ }
}
```

## 依赖规则

```
✅ 合法依赖：
Controller → UseCase → Entity
JpaGateway → OrderGateway(interface) ← UseCase

❌ 非法依赖：
Entity → JpaRepository（内层依赖外层）
UseCase → Spring annotation（业务依赖框架）
Entity → HttpClient（领域依赖基础设施）
```

## 与六边形架构的对比

| 维度 | 清洁架构 | [六边形架构](../hexagonal-architecture/) |
|------|---------|---------|
| 层次 | 4层同心圆 | 内外两区（核心 + 适配器） |
| 重点 | 依赖规则 | 端口与适配器 |
| Entity层 | 独立的最内层 | 包含在核心中 |
| 本质 | 相同理念，不同表达 | 相同理念，不同表达 |

## 最佳实践

1. **Entity 层零依赖** — 纯 Java/Python 对象，不引入任何框架
2. **Use Case 通过接口访问外部** — Gateway 接口定义在 Use Case 层
3. **数据跨层传递用 DTO** — 不让 Entity 泄漏到外层
4. **框架是细节** — Spring、Django 等都在最外层

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [六边形架构](../hexagonal-architecture/) | 同源理念，清洁架构更细化层次 |
| [领域模型](../domain-model/) | Entity 层对应领域模型 |
| [应用服务](../application-service/) | Use Case 层对应应用服务 |
| [仓储](../repository/) | Gateway 对应仓储模式 |

## 总结

**核心**：依赖只能从外向内，业务逻辑在最内层，不依赖任何技术细节。

**实践**：Entity → Use Case → Adapter → Framework，每层通过接口与外层通信。
