---
name: 分层架构原则
description: "将系统划分为职责明确的层次，每层只与相邻层交互，实现关注点分离和独立变化。"
license: MIT
---

# 分层架构原则 (Layered Architecture Principle)

## 概述

分层架构是最经典的软件架构模式：**将系统按职责划分为水平层次，每层为上层提供服务，同时使用下层的服务**。

**核心规则**：
- 每层职责单一且明确
- 上层依赖下层，下层不知道上层存在
- 跨层调用必须经过中间层（严格分层）或可跳层（松散分层）
- 同层内的组件可以互相调用

## 经典四层架构

```
┌─────────────────────────────┐
│    Presentation Layer       │  UI、API 接口、控制器
│    表示层                    │  接收输入，返回响应
├─────────────────────────────┤
│    Application Layer        │  用例编排、事务管理
│    应用层                    │  协调领域对象完成业务流程
├─────────────────────────────┤
│    Domain Layer             │  业务规则、领域模型
│    领域层                    │  核心业务逻辑，不依赖任何技术细节
├─────────────────────────────┤
│    Infrastructure Layer     │  数据库、消息队列、外部API
│    基础设施层                │  技术实现细节
└─────────────────────────────┘
```

## 代码示例

```java
// ✅ 清晰的分层

// 表示层：只负责 HTTP 请求/响应
@RestController
public class OrderController {
    private final OrderApplicationService appService;

    @PostMapping("/orders")
    public ResponseEntity<OrderDTO> create(@RequestBody CreateOrderRequest req) {
        OrderDTO result = appService.createOrder(req);
        return ResponseEntity.created(URI.create("/orders/" + result.getId())).body(result);
    }
}

// 应用层：编排业务流程
@Service
@Transactional
public class OrderApplicationService {
    private final OrderRepository orderRepo;
    private final InventoryService inventoryService;

    public OrderDTO createOrder(CreateOrderRequest req) {
        inventoryService.reserve(req.getItems());
        Order order = Order.create(req.getCustomerId(), req.getItems());
        orderRepo.save(order);
        return OrderDTO.from(order);
    }
}

// 领域层：纯业务逻辑
public class Order {
    private OrderId id;
    private List<OrderItem> items;
    private OrderStatus status;

    public static Order create(CustomerId customerId, List<ItemRequest> items) {
        // 业务规则验证
        if (items.isEmpty()) throw new DomainException("订单不能为空");
        return new Order(OrderId.generate(), customerId, items);
    }

    public void confirm() {
        if (status != OrderStatus.PENDING) {
            throw new DomainException("只有待处理订单可以确认");
        }
        this.status = OrderStatus.CONFIRMED;
    }
}

// 基础设施层：技术实现
@Repository
public class JpaOrderRepository implements OrderRepository {
    private final JpaEntityManager em;

    public void save(Order order) {
        em.persist(OrderEntity.fromDomain(order));
    }
}
```

```python
# ✅ Python 分层示例

# 表示层
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    result = order_app_service.create_order(data)
    return jsonify(result), 201

# 应用层
class OrderApplicationService:
    def __init__(self, order_repo, inventory_service):
        self.order_repo = order_repo
        self.inventory_service = inventory_service

    def create_order(self, data: dict) -> dict:
        self.inventory_service.reserve(data["items"])
        order = Order.create(data["customer_id"], data["items"])
        self.order_repo.save(order)
        return order.to_dict()

# 领域层
class Order:
    @staticmethod
    def create(customer_id: str, items: list) -> "Order":
        if not items:
            raise DomainError("订单不能为空")
        return Order(id=uuid4(), customer_id=customer_id, items=items)

# 基础设施层
class SqlOrderRepository:
    def save(self, order: Order):
        db.session.add(OrderModel.from_domain(order))
        db.session.commit()
```

## 违反分层的典型问题

```java
// ❌ 表示层直接访问数据库
@RestController
public class OrderController {
    @Autowired
    private JdbcTemplate jdbc;  // 跨层依赖！

    @GetMapping("/orders/{id}")
    public Map<String, Object> getOrder(@PathVariable Long id) {
        return jdbc.queryForMap("SELECT * FROM orders WHERE id = ?", id);
    }
}

// ❌ 领域层依赖框架
public class Order {
    @Autowired  // 领域对象不应该依赖 Spring
    private EmailService emailService;

    public void confirm() {
        this.status = CONFIRMED;
        emailService.send(this.customerEmail, "订单已确认");  // 领域层不应处理通知
    }
}
```

## 分层变体

| 模式 | 特点 | 适用场景 |
|------|------|---------|
| 严格分层 | 只能调用直接下层 | 大型企业系统 |
| 松散分层 | 可以跳层调用 | 中小型项目 |
| 六边形架构 | 端口+适配器 | 需要多种外部集成 |
| 洋葱架构 | 依赖指向中心 | DDD 项目 |

## 最佳实践

1. **领域层零依赖** - 不依赖框架、数据库、HTTP
2. **层间通过接口通信** - 上层定义接口，下层实现
3. **DTO 隔离** - 每层有自己的数据传输对象，不跨层传递领域对象
4. **依赖方向一致** - 依赖只能从上到下（或从外到内）

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [关注点分离](../separation-of-concerns/) | 分层是 SoC 最经典的实现 |
| [DIP](../dependency-inversion-principle/) | 通过 DIP 实现下层不依赖上层 |
| [封装](../encapsulation-principle/) | 每层封装自己的实现细节 |

## 总结

**分层架构核心**：按职责划分层次，依赖方向从上到下。

**实践要点**：
- 表示层：接收请求、返回响应
- 应用层：编排流程、管理事务
- 领域层：核心业务规则，零框架依赖
- 基础设施层：数据库、外部服务等技术实现
