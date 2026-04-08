# 分层架构原则 - 参考实现

## 核心原理

分层架构将系统按职责划分为独立的层，每层只依赖其直接下层，**上层定义需求，下层提供实现**。这是管理大型系统复杂性的基础模式。

### 关键设计要点

| 要点 | 说明 | 应用场景 |
|------|------|---------|
| 单向依赖 | 上层依赖下层，下层不得反向依赖 | 所有层间交互 |
| 职责单一 | 每层只处理一类关注点 | 层划分决策 |
| 接口隔离 | 层间通过接口通信，非具体实现 | 层边界设计 |
| DTO 隔离 | 每层使用自己的数据结构 | 数据传递 |

---

## 完整场景：订单管理系统（四层架构）

```
请求流转：

HTTP Request
    ↓
┌─────────────────────────┐
│ Controller (表现层)       │  接收请求、参数校验、返回响应
│ OrderController          │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ AppService (应用服务层)   │  用例编排、事务管理、DTO 转换
│ OrderAppService          │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Domain (领域层)           │  业务规则、领域模型、值对象
│ Order, OrderItem, Money  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Repository (基础设施层)   │  数据持久化、外部服务调用
│ OrderRepositoryImpl      │
└─────────────────────────┘
```

---

## Java 完整参考实现

### ❌ 反面示例：Controller 直接操作数据库

```java
// ❌ 所有逻辑集中在 Controller，无分层可言
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostMapping
    public ResponseEntity<Map<String, Object>> createOrder(@RequestBody Map<String, Object> body) {
        String customerId = (String) body.get("customerId");
        List<Map<String, Object>> items = (List<Map<String, Object>>) body.get("items");

        // 业务逻辑在 Controller 中
        BigDecimal total = BigDecimal.ZERO;
        for (Map<String, Object> item : items) {
            int qty = (int) item.get("quantity");
            BigDecimal price = new BigDecimal(item.get("price").toString());
            total = total.add(price.multiply(BigDecimal.valueOf(qty)));
        }

        // 折扣逻辑也在 Controller 中
        if (total.compareTo(new BigDecimal("1000")) > 0) {
            total = total.multiply(new BigDecimal("0.9")); // 九折
        }

        // 直接执行 SQL
        String orderId = UUID.randomUUID().toString();
        jdbcTemplate.update(
            "INSERT INTO orders (id, customer_id, total, status) VALUES (?, ?, ?, ?)",
            orderId, customerId, total, "CREATED"
        );

        for (Map<String, Object> item : items) {
            jdbcTemplate.update(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                orderId, item.get("productId"), item.get("quantity"), item.get("price")
            );
        }

        // 直接返回内部数据结构
        Map<String, Object> result = new HashMap<>();
        result.put("orderId", orderId);
        result.put("total", total);
        result.put("status", "CREATED");
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getOrder(@PathVariable String id) {
        Map<String, Object> order = jdbcTemplate.queryForMap(
            "SELECT * FROM orders WHERE id = ?", id
        );
        return ResponseEntity.ok(order); // 数据库行直接暴露
    }
}
```

**问题：** 参数校验、业务逻辑、SQL、响应格式化全部混在一个方法中，无法测试、无法复用。

---

### ✅ 正面示例：标准四层架构

#### 1. 领域层 (Domain)

```java
// === 值对象 ===
public class OrderId {
    private final String value;

    public OrderId(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("订单ID不能为空");
        }
        this.value = value;
    }

    public String getValue() { return value; }

    public static OrderId generate() {
        return new OrderId(UUID.randomUUID().toString());
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof OrderId)) return false;
        return value.equals(((OrderId) o).value);
    }

    @Override
    public int hashCode() { return value.hashCode(); }
}

public class Money {
    private final BigDecimal amount;

    public Money(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("金额不能为负");
        }
        this.amount = amount.setScale(2, RoundingMode.HALF_UP);
    }

    public BigDecimal getValue() { return amount; }

    public Money add(Money other) {
        return new Money(this.amount.add(other.amount));
    }

    public Money multiply(int quantity) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(quantity)));
    }

    public Money applyDiscount(BigDecimal rate) {
        return new Money(this.amount.multiply(rate));
    }

    public boolean isGreaterThan(Money other) {
        return this.amount.compareTo(other.amount) > 0;
    }

    public static Money ZERO = new Money(BigDecimal.ZERO);
}

// === 领域实体 ===
public class OrderItem {
    private final String productId;
    private final int quantity;
    private final Money unitPrice;

    public OrderItem(String productId, int quantity, Money unitPrice) {
        if (quantity <= 0) throw new IllegalArgumentException("数量必须大于0");
        this.productId = productId;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }

    public Money getSubtotal() {
        return unitPrice.multiply(quantity);
    }

    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public Money getUnitPrice() { return unitPrice; }
}

// === 聚合根 ===
public class Order {
    private final OrderId id;
    private final String customerId;
    private final List<OrderItem> items;
    private OrderStatus status;
    private Money totalAmount;
    private final LocalDateTime createdAt;

    private static final Money DISCOUNT_THRESHOLD = new Money(new BigDecimal("1000"));
    private static final BigDecimal DISCOUNT_RATE = new BigDecimal("0.9");

    private Order(OrderId id, String customerId, List<OrderItem> items) {
        this.id = id;
        this.customerId = customerId;
        this.items = new ArrayList<>(items);
        this.status = OrderStatus.CREATED;
        this.createdAt = LocalDateTime.now();
        this.totalAmount = calculateTotal();
    }

    // 工厂方法
    public static Order create(String customerId, List<OrderItem> items) {
        if (items == null || items.isEmpty()) {
            throw new DomainException("订单至少需要一个订单项");
        }
        return new Order(OrderId.generate(), customerId, items);
    }

    // 业务规则：计算总价并应用折扣
    private Money calculateTotal() {
        Money subtotal = items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(Money.ZERO, Money::add);

        if (subtotal.isGreaterThan(DISCOUNT_THRESHOLD)) {
            return subtotal.applyDiscount(DISCOUNT_RATE);
        }
        return subtotal;
    }

    // 业务操作
    public void confirm() {
        if (status != OrderStatus.CREATED) {
            throw new DomainException("只有新建订单可以确认");
        }
        this.status = OrderStatus.CONFIRMED;
    }

    public void cancel() {
        if (status == OrderStatus.SHIPPED || status == OrderStatus.DELIVERED) {
            throw new DomainException("已发货或已送达的订单无法取消");
        }
        this.status = OrderStatus.CANCELLED;
    }

    // getter
    public OrderId getId() { return id; }
    public String getCustomerId() { return customerId; }
    public List<OrderItem> getItems() { return Collections.unmodifiableList(items); }
    public OrderStatus getStatus() { return status; }
    public Money getTotalAmount() { return totalAmount; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}

public enum OrderStatus {
    CREATED, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

public class DomainException extends RuntimeException {
    public DomainException(String message) { super(message); }
}

// === 仓储接口（领域层定义，基础设施层实现）===
public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(OrderId id);
    List<Order> findByCustomerId(String customerId);
}
```

#### 2. 应用服务层 (Application Service)

```java
// === 命令对象 ===
public class CreateOrderCommand {
    private final String customerId;
    private final List<OrderItemInfo> items;

    public CreateOrderCommand(String customerId, List<OrderItemInfo> items) {
        this.customerId = customerId;
        this.items = List.copyOf(items);
    }

    public String getCustomerId() { return customerId; }
    public List<OrderItemInfo> getItems() { return items; }
}

public class OrderItemInfo {
    private final String productId;
    private final int quantity;
    private final BigDecimal price;

    public OrderItemInfo(String productId, int quantity, BigDecimal price) {
        this.productId = productId;
        this.quantity = quantity;
        this.price = price;
    }

    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public BigDecimal getPrice() { return price; }
}

// === 响应 DTO ===
public class OrderDTO {
    private String orderId;
    private String customerId;
    private String status;
    private BigDecimal totalAmount;
    private List<OrderItemDTO> items;
    private String createdAt;

    public static OrderDTO fromDomain(Order order) {
        OrderDTO dto = new OrderDTO();
        dto.orderId = order.getId().getValue();
        dto.customerId = order.getCustomerId();
        dto.status = order.getStatus().name();
        dto.totalAmount = order.getTotalAmount().getValue();
        dto.items = order.getItems().stream()
            .map(OrderItemDTO::fromDomain)
            .collect(Collectors.toList());
        dto.createdAt = order.getCreatedAt().toString();
        return dto;
    }

    // getter/setter 省略
}

public class OrderItemDTO {
    private String productId;
    private int quantity;
    private BigDecimal unitPrice;
    private BigDecimal subtotal;

    public static OrderItemDTO fromDomain(OrderItem item) {
        OrderItemDTO dto = new OrderItemDTO();
        dto.productId = item.getProductId();
        dto.quantity = item.getQuantity();
        dto.unitPrice = item.getUnitPrice().getValue();
        dto.subtotal = item.getSubtotal().getValue();
        return dto;
    }
}

// === 应用服务 ===
@Service
public class OrderAppService {
    private final OrderRepository orderRepository;
    private final EventPublisher eventPublisher;

    public OrderAppService(OrderRepository orderRepository, EventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.eventPublisher = eventPublisher;
    }

    @Transactional
    public OrderDTO createOrder(CreateOrderCommand command) {
        // 1. 转换为领域对象
        List<OrderItem> items = command.getItems().stream()
            .map(info -> new OrderItem(
                info.getProductId(),
                info.getQuantity(),
                new Money(info.getPrice())
            ))
            .collect(Collectors.toList());

        // 2. 调用领域逻辑
        Order order = Order.create(command.getCustomerId(), items);

        // 3. 持久化
        orderRepository.save(order);

        // 4. 发布领域事件
        eventPublisher.publish(new OrderCreatedEvent(order.getId().getValue()));

        // 5. 返回 DTO
        return OrderDTO.fromDomain(order);
    }

    @Transactional(readOnly = true)
    public OrderDTO getOrder(String orderId) {
        Order order = orderRepository.findById(new OrderId(orderId))
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        return OrderDTO.fromDomain(order);
    }

    @Transactional
    public OrderDTO confirmOrder(String orderId) {
        Order order = orderRepository.findById(new OrderId(orderId))
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        order.confirm();
        orderRepository.save(order);
        return OrderDTO.fromDomain(order);
    }

    @Transactional
    public OrderDTO cancelOrder(String orderId) {
        Order order = orderRepository.findById(new OrderId(orderId))
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        order.cancel();
        orderRepository.save(order);
        eventPublisher.publish(new OrderCancelledEvent(orderId));
        return OrderDTO.fromDomain(order);
    }
}
```

#### 3. 表现层 (Controller)

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderAppService orderAppService;

    public OrderController(OrderAppService orderAppService) {
        this.orderAppService = orderAppService;
    }

    @PostMapping
    public ResponseEntity<OrderDTO> createOrder(@Valid @RequestBody CreateOrderRequest request) {
        CreateOrderCommand command = new CreateOrderCommand(
            request.getCustomerId(),
            request.getItems().stream()
                .map(item -> new OrderItemInfo(
                    item.getProductId(),
                    item.getQuantity(),
                    item.getPrice()
                ))
                .collect(Collectors.toList())
        );
        OrderDTO result = orderAppService.createOrder(command);
        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }

    @GetMapping("/{id}")
    public ResponseEntity<OrderDTO> getOrder(@PathVariable String id) {
        return ResponseEntity.ok(orderAppService.getOrder(id));
    }

    @PostMapping("/{id}/confirm")
    public ResponseEntity<OrderDTO> confirmOrder(@PathVariable String id) {
        return ResponseEntity.ok(orderAppService.confirmOrder(id));
    }

    @PostMapping("/{id}/cancel")
    public ResponseEntity<OrderDTO> cancelOrder(@PathVariable String id) {
        return ResponseEntity.ok(orderAppService.cancelOrder(id));
    }

    @ExceptionHandler(OrderNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(OrderNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("ORDER_NOT_FOUND", e.getMessage()));
    }

    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ErrorResponse> handleDomainError(DomainException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse("DOMAIN_ERROR", e.getMessage()));
    }
}
```

#### 4. 基础设施层 (Repository)

```java
@Repository
public class JpaOrderRepository implements OrderRepository {
    private final OrderJpaRepository jpaRepository;
    private final OrderItemJpaRepository itemJpaRepository;

    public JpaOrderRepository(OrderJpaRepository jpaRepository,
                              OrderItemJpaRepository itemJpaRepository) {
        this.jpaRepository = jpaRepository;
        this.itemJpaRepository = itemJpaRepository;
    }

    @Override
    public void save(Order order) {
        OrderEntity entity = toEntity(order);
        jpaRepository.save(entity);
        List<OrderItemEntity> itemEntities = order.getItems().stream()
            .map(item -> toItemEntity(order.getId(), item))
            .collect(Collectors.toList());
        itemJpaRepository.saveAll(itemEntities);
    }

    @Override
    public Optional<Order> findById(OrderId id) {
        return jpaRepository.findById(id.getValue())
            .map(this::toDomain);
    }

    @Override
    public List<Order> findByCustomerId(String customerId) {
        return jpaRepository.findByCustomerId(customerId).stream()
            .map(this::toDomain)
            .collect(Collectors.toList());
    }

    private OrderEntity toEntity(Order order) {
        OrderEntity entity = new OrderEntity();
        entity.setId(order.getId().getValue());
        entity.setCustomerId(order.getCustomerId());
        entity.setTotalAmount(order.getTotalAmount().getValue());
        entity.setStatus(order.getStatus().name());
        entity.setCreatedAt(order.getCreatedAt());
        return entity;
    }

    private Order toDomain(OrderEntity entity) {
        List<OrderItemEntity> itemEntities = itemJpaRepository.findByOrderId(entity.getId());
        List<OrderItem> items = itemEntities.stream()
            .map(ie -> new OrderItem(
                ie.getProductId(),
                ie.getQuantity(),
                new Money(ie.getUnitPrice())
            ))
            .collect(Collectors.toList());
        return Order.reconstitute(
            new OrderId(entity.getId()),
            entity.getCustomerId(),
            items,
            OrderStatus.valueOf(entity.getStatus()),
            entity.getCreatedAt()
        );
    }
}
```

---

## Python 完整参考实现

### 领域层

```python
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class OrderStatus(Enum):
    CREATED = "CREATED"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class DomainError(Exception):
    pass


@dataclass(frozen=True)
class OrderId:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("订单ID不能为空")

    @staticmethod
    def generate() -> OrderId:
        return OrderId(str(uuid4()))


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("金额不能为负")

    def add(self, other: Money) -> Money:
        return Money(self.amount + other.amount)

    def multiply(self, qty: int) -> Money:
        return Money(self.amount * qty)

    def apply_discount(self, rate: Decimal) -> Money:
        return Money((self.amount * rate).quantize(Decimal("0.01")))

    def is_greater_than(self, other: Money) -> bool:
        return self.amount > other.amount

    ZERO: Money = None  # 类级别初始化见下方


Money.ZERO = Money(Decimal("0"))


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("数量必须大于0")

    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)


class Order:
    """聚合根：订单"""

    DISCOUNT_THRESHOLD = Money(Decimal("1000"))
    DISCOUNT_RATE = Decimal("0.9")

    def __init__(self, order_id: OrderId, customer_id: str,
                 items: List[OrderItem], status: OrderStatus = OrderStatus.CREATED,
                 created_at: Optional[datetime] = None):
        self.id = order_id
        self.customer_id = customer_id
        self.items = list(items)
        self.status = status
        self.created_at = created_at or datetime.now()
        self.total_amount = self._calculate_total()

    @staticmethod
    def create(customer_id: str, items: List[OrderItem]) -> Order:
        if not items:
            raise DomainError("订单至少需要一个订单项")
        return Order(OrderId.generate(), customer_id, items)

    def _calculate_total(self) -> Money:
        subtotal = Money.ZERO
        for item in self.items:
            subtotal = subtotal.add(item.subtotal)
        if subtotal.is_greater_than(self.DISCOUNT_THRESHOLD):
            return subtotal.apply_discount(self.DISCOUNT_RATE)
        return subtotal

    def confirm(self):
        if self.status != OrderStatus.CREATED:
            raise DomainError("只有新建订单可以确认")
        self.status = OrderStatus.CONFIRMED

    def cancel(self):
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise DomainError("已发货或已送达的订单无法取消")
        self.status = OrderStatus.CANCELLED


# 仓储接口（领域层定义）
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]: ...

    @abstractmethod
    def find_by_customer_id(self, customer_id: str) -> List[Order]: ...
```

### 应用服务层

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: List["OrderItemInfo"]


@dataclass(frozen=True)
class OrderItemInfo:
    product_id: str
    quantity: int
    price: Decimal


@dataclass
class OrderDTO:
    order_id: str
    customer_id: str
    status: str
    total_amount: Decimal
    items: List[dict]
    created_at: str

    @classmethod
    def from_domain(cls, order: Order) -> "OrderDTO":
        return cls(
            order_id=order.id.value,
            customer_id=order.customer_id,
            status=order.status.value,
            total_amount=order.total_amount.amount,
            items=[
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price.amount),
                    "subtotal": str(item.subtotal.amount),
                }
                for item in order.items
            ],
            created_at=order.created_at.isoformat(),
        )


class OrderAppService:
    def __init__(self, order_repository: OrderRepository, event_publisher=None):
        self._repo = order_repository
        self._events = event_publisher

    def create_order(self, command: CreateOrderCommand) -> OrderDTO:
        items = [
            OrderItem(
                product_id=info.product_id,
                quantity=info.quantity,
                unit_price=Money(info.price),
            )
            for info in command.items
        ]
        order = Order.create(command.customer_id, items)
        self._repo.save(order)
        if self._events:
            self._events.publish("order_created", {"order_id": order.id.value})
        return OrderDTO.from_domain(order)

    def get_order(self, order_id: str) -> OrderDTO:
        order = self._repo.find_by_id(OrderId(order_id))
        if not order:
            raise ValueError(f"订单不存在: {order_id}")
        return OrderDTO.from_domain(order)

    def confirm_order(self, order_id: str) -> OrderDTO:
        order = self._repo.find_by_id(OrderId(order_id))
        if not order:
            raise ValueError(f"订单不存在: {order_id}")
        order.confirm()
        self._repo.save(order)
        return OrderDTO.from_domain(order)

    def cancel_order(self, order_id: str) -> OrderDTO:
        order = self._repo.find_by_id(OrderId(order_id))
        if not order:
            raise ValueError(f"订单不存在: {order_id}")
        order.cancel()
        self._repo.save(order)
        return OrderDTO.from_domain(order)
```

### 表现层（Flask）

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# 依赖注入（简化示例）
order_service = OrderAppService(order_repository=get_repository())


@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    command = CreateOrderCommand(
        customer_id=data["customerId"],
        items=[
            OrderItemInfo(
                product_id=item["productId"],
                quantity=item["quantity"],
                price=Decimal(str(item["price"])),
            )
            for item in data["items"]
        ],
    )
    dto = order_service.create_order(command)
    return jsonify(dto.__dict__), 201


@app.route("/api/orders/<order_id>", methods=["GET"])
def get_order(order_id: str):
    dto = order_service.get_order(order_id)
    return jsonify(dto.__dict__)


@app.route("/api/orders/<order_id>/confirm", methods=["POST"])
def confirm_order(order_id: str):
    dto = order_service.confirm_order(order_id)
    return jsonify(dto.__dict__)


@app.route("/api/orders/<order_id>/cancel", methods=["POST"])
def cancel_order(order_id: str):
    dto = order_service.cancel_order(order_id)
    return jsonify(dto.__dict__)


@app.errorhandler(DomainError)
def handle_domain_error(e):
    return jsonify({"error": "DOMAIN_ERROR", "message": str(e)}), 400


@app.errorhandler(ValueError)
def handle_not_found(e):
    return jsonify({"error": "NOT_FOUND", "message": str(e)}), 404
```

### 基础设施层

```python
class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def save(self, order: Order) -> None:
        with self._session_factory() as session:
            entity = self._to_entity(order)
            session.merge(entity)
            session.commit()

    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        with self._session_factory() as session:
            entity = session.query(OrderOrmModel).get(order_id.value)
            if entity is None:
                return None
            return self._to_domain(entity)

    def find_by_customer_id(self, customer_id: str) -> List[Order]:
        with self._session_factory() as session:
            entities = session.query(OrderOrmModel).filter_by(
                customer_id=customer_id
            ).all()
            return [self._to_domain(e) for e in entities]

    def _to_entity(self, order: Order) -> "OrderOrmModel":
        return OrderOrmModel(
            id=order.id.value,
            customer_id=order.customer_id,
            total_amount=order.total_amount.amount,
            status=order.status.value,
            created_at=order.created_at,
        )

    def _to_domain(self, entity: "OrderOrmModel") -> Order:
        items = [
            OrderItem(
                product_id=ie.product_id,
                quantity=ie.quantity,
                unit_price=Money(ie.unit_price),
            )
            for ie in entity.items
        ]
        return Order(
            order_id=OrderId(entity.id),
            customer_id=entity.customer_id,
            items=items,
            status=OrderStatus(entity.status),
            created_at=entity.created_at,
        )
```

---

## TypeScript 完整参考实现

### 领域层

```typescript
// === 值对象 ===
export class OrderId {
  constructor(public readonly value: string) {
    if (!value || !value.trim()) {
      throw new Error("订单ID不能为空");
    }
  }

  static generate(): OrderId {
    return new OrderId(crypto.randomUUID());
  }

  equals(other: OrderId): boolean {
    return this.value === other.value;
  }
}

export class Money {
  constructor(public readonly amount: number) {
    if (amount < 0) throw new Error("金额不能为负");
  }

  add(other: Money): Money {
    return new Money(this.amount + other.amount);
  }

  multiply(qty: number): Money {
    return new Money(this.amount * qty);
  }

  applyDiscount(rate: number): Money {
    return new Money(Math.round(this.amount * rate * 100) / 100);
  }

  isGreaterThan(other: Money): boolean {
    return this.amount > other.amount;
  }

  static ZERO = new Money(0);
}

// === 领域实体 ===
export class OrderItem {
  constructor(
    public readonly productId: string,
    public readonly quantity: number,
    public readonly unitPrice: Money
  ) {
    if (quantity <= 0) throw new Error("数量必须大于0");
  }

  get subtotal(): Money {
    return this.unitPrice.multiply(this.quantity);
  }
}

export enum OrderStatus {
  CREATED = "CREATED",
  CONFIRMED = "CONFIRMED",
  SHIPPED = "SHIPPED",
  DELIVERED = "DELIVERED",
  CANCELLED = "CANCELLED",
}

export class DomainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DomainError";
  }
}

// === 聚合根 ===
export class Order {
  private static readonly DISCOUNT_THRESHOLD = new Money(1000);
  private static readonly DISCOUNT_RATE = 0.9;

  public readonly totalAmount: Money;

  private constructor(
    public readonly id: OrderId,
    public readonly customerId: string,
    public readonly items: ReadonlyArray<OrderItem>,
    public status: OrderStatus,
    public readonly createdAt: Date
  ) {
    this.totalAmount = this.calculateTotal();
  }

  static create(customerId: string, items: OrderItem[]): Order {
    if (!items || items.length === 0) {
      throw new DomainError("订单至少需要一个订单项");
    }
    return new Order(OrderId.generate(), customerId, items, OrderStatus.CREATED, new Date());
  }

  static reconstitute(
    id: OrderId, customerId: string, items: OrderItem[],
    status: OrderStatus, createdAt: Date
  ): Order {
    return new Order(id, customerId, items, status, createdAt);
  }

  private calculateTotal(): Money {
    const subtotal = this.items.reduce(
      (sum, item) => sum.add(item.subtotal), Money.ZERO
    );
    if (subtotal.isGreaterThan(Order.DISCOUNT_THRESHOLD)) {
      return subtotal.applyDiscount(Order.DISCOUNT_RATE);
    }
    return subtotal;
  }

  confirm(): void {
    if (this.status !== OrderStatus.CREATED) {
      throw new DomainError("只有新建订单可以确认");
    }
    this.status = OrderStatus.CONFIRMED;
  }

  cancel(): void {
    if (this.status === OrderStatus.SHIPPED || this.status === OrderStatus.DELIVERED) {
      throw new DomainError("已发货或已送达的订单无法取消");
    }
    this.status = OrderStatus.CANCELLED;
  }
}

// === 仓储接口 ===
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomerId(customerId: string): Promise<Order[]>;
}
```

### 应用服务层

```typescript
// === 命令与 DTO ===
export interface CreateOrderCommand {
  customerId: string;
  items: { productId: string; quantity: number; price: number }[];
}

export interface OrderDTO {
  orderId: string;
  customerId: string;
  status: string;
  totalAmount: number;
  items: { productId: string; quantity: number; unitPrice: number; subtotal: number }[];
  createdAt: string;
}

function toOrderDTO(order: Order): OrderDTO {
  return {
    orderId: order.id.value,
    customerId: order.customerId,
    status: order.status,
    totalAmount: order.totalAmount.amount,
    items: order.items.map((item) => ({
      productId: item.productId,
      quantity: item.quantity,
      unitPrice: item.unitPrice.amount,
      subtotal: item.subtotal.amount,
    })),
    createdAt: order.createdAt.toISOString(),
  };
}

// === 应用服务 ===
export class OrderAppService {
  constructor(
    private readonly orderRepo: OrderRepository,
    private readonly eventPublisher?: EventPublisher
  ) {}

  async createOrder(command: CreateOrderCommand): Promise<OrderDTO> {
    const items = command.items.map(
      (i) => new OrderItem(i.productId, i.quantity, new Money(i.price))
    );
    const order = Order.create(command.customerId, items);
    await this.orderRepo.save(order);
    this.eventPublisher?.publish("order_created", { orderId: order.id.value });
    return toOrderDTO(order);
  }

  async getOrder(orderId: string): Promise<OrderDTO> {
    const order = await this.orderRepo.findById(new OrderId(orderId));
    if (!order) throw new Error(`订单不存在: ${orderId}`);
    return toOrderDTO(order);
  }

  async confirmOrder(orderId: string): Promise<OrderDTO> {
    const order = await this.orderRepo.findById(new OrderId(orderId));
    if (!order) throw new Error(`订单不存在: ${orderId}`);
    order.confirm();
    await this.orderRepo.save(order);
    return toOrderDTO(order);
  }

  async cancelOrder(orderId: string): Promise<OrderDTO> {
    const order = await this.orderRepo.findById(new OrderId(orderId));
    if (!order) throw new Error(`订单不存在: ${orderId}`);
    order.cancel();
    await this.orderRepo.save(order);
    return toOrderDTO(order);
  }
}
```

### 表现层（Express）

```typescript
import express, { Request, Response, NextFunction } from "express";

const app = express();
app.use(express.json());

const orderAppService = new OrderAppService(orderRepository);

app.post("/api/orders", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const command: CreateOrderCommand = {
      customerId: req.body.customerId,
      items: req.body.items,
    };
    const dto = await orderAppService.createOrder(command);
    res.status(201).json(dto);
  } catch (e) { next(e); }
});

app.get("/api/orders/:id", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const dto = await orderAppService.getOrder(req.params.id);
    res.json(dto);
  } catch (e) { next(e); }
});

app.post("/api/orders/:id/confirm", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const dto = await orderAppService.confirmOrder(req.params.id);
    res.json(dto);
  } catch (e) { next(e); }
});

app.post("/api/orders/:id/cancel", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const dto = await orderAppService.cancelOrder(req.params.id);
    res.json(dto);
  } catch (e) { next(e); }
});

// 统一错误处理
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof DomainError) {
    res.status(400).json({ error: "DOMAIN_ERROR", message: err.message });
  } else if (err.message.startsWith("订单不存在")) {
    res.status(404).json({ error: "NOT_FOUND", message: err.message });
  } else {
    res.status(500).json({ error: "INTERNAL_ERROR", message: "服务器内部错误" });
  }
});
```

---

## 测试

### Java 单元测试

```java
class OrderTest {

    @Test
    void 创建订单应计算总价() {
        List<OrderItem> items = List.of(
            new OrderItem("P001", 2, new Money(new BigDecimal("100"))),
            new OrderItem("P002", 1, new Money(new BigDecimal("200")))
        );

        Order order = Order.create("C001", items);

        assertEquals(new BigDecimal("400.00"), order.getTotalAmount().getValue());
        assertEquals(OrderStatus.CREATED, order.getStatus());
    }

    @Test
    void 超过1000元应自动打九折() {
        List<OrderItem> items = List.of(
            new OrderItem("P001", 10, new Money(new BigDecimal("200")))
        );

        Order order = Order.create("C001", items);

        // 2000 * 0.9 = 1800
        assertEquals(new BigDecimal("1800.00"), order.getTotalAmount().getValue());
    }

    @Test
    void 确认订单应改变状态() {
        Order order = createSampleOrder();
        order.confirm();
        assertEquals(OrderStatus.CONFIRMED, order.getStatus());
    }

    @Test
    void 已发货订单不能取消() {
        Order order = createShippedOrder();
        assertThrows(DomainException.class, order::cancel);
    }

    @Test
    void 空订单项应抛出异常() {
        assertThrows(DomainException.class, () -> Order.create("C001", List.of()));
    }
}

class OrderAppServiceTest {

    private OrderRepository mockRepository;
    private EventPublisher mockPublisher;
    private OrderAppService service;

    @BeforeEach
    void setup() {
        mockRepository = mock(OrderRepository.class);
        mockPublisher = mock(EventPublisher.class);
        service = new OrderAppService(mockRepository, mockPublisher);
    }

    @Test
    void 创建订单应保存并发布事件() {
        CreateOrderCommand command = new CreateOrderCommand("C001", List.of(
            new OrderItemInfo("P001", 2, new BigDecimal("100"))
        ));

        OrderDTO result = service.createOrder(command);

        verify(mockRepository).save(any(Order.class));
        verify(mockPublisher).publish(any(OrderCreatedEvent.class));
        assertNotNull(result.getOrderId());
        assertEquals("CREATED", result.getStatus());
    }

    @Test
    void 查询不存在的订单应抛出异常() {
        when(mockRepository.findById(any())).thenReturn(Optional.empty());
        assertThrows(OrderNotFoundException.class, () -> service.getOrder("nonexistent"));
    }
}
```

### Python 单元测试

```python
import pytest
from decimal import Decimal
from unittest.mock import MagicMock


class TestOrder:
    def test_创建订单应计算总价(self):
        items = [
            OrderItem("P001", 2, Money(Decimal("100"))),
            OrderItem("P002", 1, Money(Decimal("200"))),
        ]
        order = Order.create("C001", items)

        assert order.total_amount.amount == Decimal("400")
        assert order.status == OrderStatus.CREATED

    def test_超过1000元应自动打九折(self):
        items = [OrderItem("P001", 10, Money(Decimal("200")))]
        order = Order.create("C001", items)

        assert order.total_amount.amount == Decimal("1800.00")

    def test_确认订单应改变状态(self):
        order = create_sample_order()
        order.confirm()
        assert order.status == OrderStatus.CONFIRMED

    def test_已发货订单不能取消(self):
        order = create_shipped_order()
        with pytest.raises(DomainError):
            order.cancel()

    def test_空订单项应抛出异常(self):
        with pytest.raises(DomainError):
            Order.create("C001", [])


class TestOrderAppService:
    def setup_method(self):
        self.mock_repo = MagicMock(spec=OrderRepository)
        self.mock_events = MagicMock()
        self.service = OrderAppService(self.mock_repo, self.mock_events)

    def test_创建订单应保存并发布事件(self):
        command = CreateOrderCommand(
            customer_id="C001",
            items=[OrderItemInfo("P001", 2, Decimal("100"))],
        )

        result = self.service.create_order(command)

        self.mock_repo.save.assert_called_once()
        self.mock_events.publish.assert_called_once()
        assert result.status == "CREATED"

    def test_查询不存在的订单应抛出异常(self):
        self.mock_repo.find_by_id.return_value = None
        with pytest.raises(ValueError):
            self.service.get_order("nonexistent")
```

### TypeScript 单元测试

```typescript
describe("Order 领域模型", () => {
  it("创建订单应计算总价", () => {
    const items = [
      new OrderItem("P001", 2, new Money(100)),
      new OrderItem("P002", 1, new Money(200)),
    ];

    const order = Order.create("C001", items);

    expect(order.totalAmount.amount).toBe(400);
    expect(order.status).toBe(OrderStatus.CREATED);
  });

  it("超过1000元应自动打九折", () => {
    const items = [new OrderItem("P001", 10, new Money(200))];
    const order = Order.create("C001", items);

    expect(order.totalAmount.amount).toBe(1800);
  });

  it("确认订单应改变状态", () => {
    const order = createSampleOrder();
    order.confirm();
    expect(order.status).toBe(OrderStatus.CONFIRMED);
  });

  it("已发货订单不能取消", () => {
    const order = createShippedOrder();
    expect(() => order.cancel()).toThrow(DomainError);
  });

  it("空订单项应抛出异常", () => {
    expect(() => Order.create("C001", [])).toThrow(DomainError);
  });
});

describe("OrderAppService", () => {
  let mockRepo: jest.Mocked<OrderRepository>;
  let service: OrderAppService;

  beforeEach(() => {
    mockRepo = {
      save: jest.fn(),
      findById: jest.fn(),
      findByCustomerId: jest.fn(),
    };
    service = new OrderAppService(mockRepo);
  });

  it("创建订单应保存并返回DTO", async () => {
    const command: CreateOrderCommand = {
      customerId: "C001",
      items: [{ productId: "P001", quantity: 2, price: 100 }],
    };

    const result = await service.createOrder(command);

    expect(mockRepo.save).toHaveBeenCalledTimes(1);
    expect(result.status).toBe("CREATED");
    expect(result.orderId).toBeDefined();
  });

  it("查询不存在的订单应抛出异常", async () => {
    mockRepo.findById.mockResolvedValue(null);
    await expect(service.getOrder("nonexistent")).rejects.toThrow("订单不存在");
  });
});
```

---

## 层间通信总结

```
┌───────────┐  CreateOrderRequest  ┌────────────┐  CreateOrderCommand  ┌────────┐
│ Controller │ ──────────────────→  │ AppService  │ ──────────────────→  │ Domain │
│            │  ←─── OrderDTO ────  │             │  ←─── Order ───────  │        │
└───────────┘                      └────────────┘                      └────────┘
                                         │                                  ↑
                                         │ save(Order)                      │
                                         ↓                                  │
                                   ┌────────────┐                          │
                                   │ Repository  │ ── toDomain(Entity) ───┘
                                   │ (Infra)     │
                                   └────────────┘

关键规则：
  1. Controller 不直接接触 Domain 或 Repository
  2. AppService 编排用例，不包含业务规则
  3. Domain 不依赖任何框架，业务规则集中于此
  4. Repository 接口在 Domain 层定义，实现在 Infrastructure 层
  5. 每层使用自己的数据结构（Request/Command/Entity/DTO）
```
