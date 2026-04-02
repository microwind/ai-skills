---
name: 六边形架构
description: "通过端口和适配器将应用核心与外部技术隔离，使业务逻辑不依赖任何框架或基础设施。"
license: MIT
---

# 六边形架构 (Hexagonal Architecture)

## 概述

六边形架构（端口与适配器架构）由 Alistair Cockburn 提出：**应用核心通过端口（接口）与外部世界交互，适配器负责连接具体的技术实现**。

```
                    ┌─────────────────────┐
   HTTP ──adapter──▶│  Port               │
                    │    ┌─────────────┐  │
   CLI ───adapter──▶│    │  Application│  │
                    │    │    Core     │  │
   MQ ────adapter──▶│    │ (Domain +   │  │
                    │    │  Use Cases) │  │
                    │    └─────────────┘  │
                    │               Port  │──adapter── DB
                    │               Port  │──adapter── Email
                    │               Port  │──adapter── MQ
                    └─────────────────────┘
    驱动端（左侧）          应用核心          被驱动端（右侧）
```

**核心规则**：
- 应用核心不依赖任何外部技术
- 依赖方向：外部 → 内部（适配器依赖端口，端口定义在核心）
- 端口 = 接口，适配器 = 接口的实现

## 代码示例

```java
// ===== 应用核心（不依赖任何框架） =====

// 驱动端口（入口）：定义用例
public interface OrderUseCase {
    OrderDTO placeOrder(PlaceOrderCommand cmd);
    void cancelOrder(String orderId, String reason);
}

// 被驱动端口（出口）：定义需要的外部能力
public interface OrderRepository {
    Optional<Order> findById(String id);
    void save(Order order);
}

public interface PaymentPort {
    PaymentResult charge(String customerId, Money amount);
}

public interface NotificationPort {
    void sendOrderConfirmation(String email, String orderId);
}

// 应用核心实现
public class OrderService implements OrderUseCase {
    private final OrderRepository orderRepo;    // 被驱动端口
    private final PaymentPort payment;          // 被驱动端口
    private final NotificationPort notification; // 被驱动端口

    public OrderService(OrderRepository orderRepo, PaymentPort payment,
                        NotificationPort notification) {
        this.orderRepo = orderRepo;
        this.payment = payment;
        this.notification = notification;
    }

    @Override
    public OrderDTO placeOrder(PlaceOrderCommand cmd) {
        Order order = orderRepo.findById(cmd.getOrderId())
            .orElseThrow(() -> new NotFoundException("订单不存在"));
        order.place();
        payment.charge(order.getCustomerId(), order.getTotal());
        orderRepo.save(order);
        notification.sendOrderConfirmation(order.getCustomerEmail(), order.getId());
        return OrderDTO.from(order);
    }
}

// ===== 适配器（外部，依赖核心） =====

// 驱动适配器：HTTP
@RestController
public class OrderRestAdapter {
    private final OrderUseCase orderUseCase;  // 依赖端口

    @PostMapping("/api/orders/{id}/place")
    public ResponseEntity<OrderDTO> place(@PathVariable String id) {
        return ResponseEntity.ok(orderUseCase.placeOrder(new PlaceOrderCommand(id)));
    }
}

// 被驱动适配器：数据库
@Repository
public class JpaOrderAdapter implements OrderRepository {
    private final JpaEntityManager em;

    @Override
    public Optional<Order> findById(String id) {
        return Optional.ofNullable(em.find(OrderEntity.class, id))
            .map(OrderEntity::toDomain);
    }

    @Override
    public void save(Order order) {
        em.merge(OrderEntity.fromDomain(order));
    }
}

// 被驱动适配器：支付
public class StripePaymentAdapter implements PaymentPort {
    private final StripeClient stripe;

    @Override
    public PaymentResult charge(String customerId, Money amount) {
        StripeCharge charge = stripe.charges().create(/* ... */);
        return new PaymentResult(charge.getId(), charge.getStatus());
    }
}
```

```python
# 端口（接口）
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: pass
    @abstractmethod
    def save(self, order: Order): pass

class EmailPort(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str): pass

# 应用核心
class OrderService:
    def __init__(self, repo: OrderRepository, email: EmailPort):
        self.repo = repo
        self.email = email

    def place_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        order.place()
        self.repo.save(order)
        self.email.send(order.customer_email, "订单确认", f"订单{order.id}已确认")

# 适配器
class PostgresOrderRepository(OrderRepository):
    def find_by_id(self, order_id: str) -> Order | None:
        row = db.execute("SELECT * FROM orders WHERE id = %s", order_id)
        return Order.from_row(row) if row else None

class SmtpEmailAdapter(EmailPort):
    def send(self, to: str, subject: str, body: str):
        smtp.sendmail(to, subject, body)

# 测试时替换适配器
class InMemoryOrderRepository(OrderRepository):
    def __init__(self): self._store = {}
    def find_by_id(self, order_id): return self._store.get(order_id)
    def save(self, order): self._store[order.id] = order

class FakeEmailAdapter(EmailPort):
    def __init__(self): self.sent = []
    def send(self, to, subject, body): self.sent.append((to, subject, body))
```

## 项目结构

```
src/
├── core/                    # 应用核心（无外部依赖）
│   ├── domain/              # 领域模型
│   │   ├── Order.java
│   │   └── OrderItem.java
│   ├── port/
│   │   ├── in/              # 驱动端口（入口）
│   │   │   └── OrderUseCase.java
│   │   └── out/             # 被驱动端口（出口）
│   │       ├── OrderRepository.java
│   │       └── PaymentPort.java
│   └── service/             # 用例实现
│       └── OrderService.java
│
└── adapter/                 # 适配器（依赖核心）
    ├── in/                  # 驱动适配器
    │   ├── rest/
    │   │   └── OrderRestAdapter.java
    │   └── cli/
    │       └── OrderCliAdapter.java
    └── out/                 # 被驱动适配器
        ├── persistence/
        │   └── JpaOrderAdapter.java
        └── payment/
            └── StripePaymentAdapter.java
```

## 优缺点

### ✅ 优点
1. **技术无关** — 核心业务逻辑不依赖框架
2. **可测试** — 替换适配器即可测试核心逻辑
3. **可替换** — 换数据库、换框架只需换适配器
4. **清晰边界** — 依赖方向明确

### ❌ 缺点
1. **代码量多** — 需要定义端口和适配器
2. **间接层** — 调用链更长
3. **简单项目过度设计** — CRUD 应用不需要

## 与其他概念的关系

| 概念 | 关系 |
|------|------|
| [清洁架构](../clean-architecture/) | 清洁架构是六边形架构的演进 |
| [DIP](../../design-principles/dependency-inversion-principle/) | 端口 + 适配器是 DIP 的完美体现 |
| [仓储](../repository/) | Repository 就是一个被驱动端口 |

## 总结

**核心**：端口定义能力边界，适配器连接外部世界，应用核心零外部依赖。

**实践**：核心定义端口接口 → 适配器实现接口 → 测试时用 Fake 适配器。
