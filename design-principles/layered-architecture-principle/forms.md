# 分层架构原则 - 诊断与规划表

## 第1步: 需求诊断 - 你的分层是否健康？

### 🔍 快速检查清单

```
□ Controller 直接访问数据库（跳过 Service 层）
□ 领域模型中包含框架注解（如 @Controller、@RequestMapping）
□ 跨层数据对象泄漏（实体直接暴露给前端）
□ 下层依赖上层（Repository 引用 Controller 的类）
□ 业务逻辑散落在 Controller 中
□ 一个层包含了多种职责（Service 同时做校验、编排、持久化）
□ 层与层之间没有明确的接口边界
□ 修改一层需要同时修改其他多层
□ 工具类直接操作多个层的数据
□ 测试时无法独立测试某一层
```

**诊断标准**:
- ✅ 0-2 项 → **分层架构健康**
- ⚠️ 3-5 项 → **需要重构分层边界**
- ❌ 6 项以上 → **分层架构严重混乱，必须立即治理**

### 🎯 层违规场景评估

| 违规类型 | 现象 | 危害 | 优先级 |
|----------|------|------|--------|
| Controller 访问 DB | Controller 中出现 SQL 或 ORM 查询 | 表现层与持久层耦合 | ⭐⭐⭐⭐⭐ |
| 领域带框架注解 | Entity 上有 @RestController 等 | 领域被基础设施污染 | ⭐⭐⭐⭐⭐ |
| 跨层数据泄漏 | 数据库实体直接返回给前端 | 内部结构暴露 | ⭐⭐⭐⭐ |
| 反向依赖 | 低层引用高层的包 | 依赖方向混乱 | ⭐⭐⭐⭐ |
| 业务逻辑上浮 | Controller 包含复杂 if-else 业务判断 | 无法复用业务逻辑 | ⭐⭐⭐⭐ |
| Service 层膨胀 | 单个 Service 类超过 1000 行 | 职责不清 | ⭐⭐⭐ |

---

## 第2步: 层职责定义

### 标准四层架构职责划分

```
┌─────────────────────────────────────────────┐
│  表现层 (Presentation / Controller)          │
│  职责：接收请求、参数校验、响应格式化         │
│  不应包含：业务逻辑、数据库操作              │
├─────────────────────────────────────────────┤
│  应用服务层 (Application Service)            │
│  职责：用例编排、事务管理、跨域协调           │
│  不应包含：领域规则、SQL 语句                │
├─────────────────────────────────────────────┤
│  领域层 (Domain)                             │
│  职责：业务规则、领域模型、值对象             │
│  不应包含：框架注解、HTTP 概念、持久化细节    │
├─────────────────────────────────────────────┤
│  基础设施层 (Infrastructure / Repository)     │
│  职责：数据持久化、外部服务调用、消息队列      │
│  不应包含：业务决策逻辑                      │
└─────────────────────────────────────────────┘
```

### 层职责自查表

```
表现层 (Controller):
  □ 只负责 HTTP 请求/响应转换？    是 / 否
  □ 参数校验在此层完成？           是 / 否
  □ 没有 if-else 业务判断？        是 / 否
  □ 没有直接调用 Repository？      是 / 否
  当前问题：________________

应用服务层 (Application Service):
  □ 只做用例编排，不做业务决策？    是 / 否
  □ 事务边界在此层管理？           是 / 否
  □ 没有直接操作数据库？           是 / 否
  □ 返回 DTO 而非领域对象？        是 / 否
  当前问题：________________

领域层 (Domain):
  □ 没有框架注解 (@Service、@Component)？ 是 / 否
  □ 业务规则集中在领域对象中？            是 / 否
  □ 不依赖任何外部框架？                 是 / 否
  □ 可以脱离框架独立测试？               是 / 否
  当前问题：________________

基础设施层 (Repository):
  □ 只提供数据访问接口实现？       是 / 否
  □ 不包含业务逻辑判断？           是 / 否
  □ 使用领域层定义的接口？         是 / 否
  当前问题：________________
```

---

## 第3步: 依赖方向审计

### 合法依赖方向

```
✅ 合法方向（从上到下）：
   Controller → AppService → Domain → Repository(接口)

❌ 非法方向（从下到上）：
   Repository → Domain（具体实现） ✅ 允许
   Repository → Controller           ❌ 禁止
   Domain → Controller               ❌ 禁止
   AppService → Controller           ❌ 禁止
```

### Java 依赖审计

```java
// ❌ 违规：Controller 直接依赖 Repository
@RestController
public class OrderController {
    @Autowired
    private OrderRepository orderRepository;  // 跳过了 Service 层

    @GetMapping("/orders/{id}")
    public Order getOrder(@PathVariable Long id) {
        return orderRepository.findById(id).orElse(null); // 直接查 DB
    }
}

// ✅ 正确：Controller 只依赖 AppService
@RestController
public class OrderController {
    private final OrderAppService orderAppService;

    public OrderController(OrderAppService orderAppService) {
        this.orderAppService = orderAppService;
    }

    @GetMapping("/orders/{id}")
    public OrderDTO getOrder(@PathVariable Long id) {
        return orderAppService.getOrder(id);
    }
}
```

### Python 依赖审计

```python
# ❌ 违规：视图函数直接操作数据库
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)

@app.route("/orders/<int:order_id>")
def get_order(order_id):
    db = get_db_session()
    result = db.execute(text("SELECT * FROM orders WHERE id = :id"), {"id": order_id})
    row = result.fetchone()
    return {"id": row.id, "total": float(row.total)}  # 直接暴露数据库结构


# ✅ 正确：视图函数只调用应用服务
from flask import Flask
from app.services.order_service import OrderAppService

app = Flask(__name__)
order_service = OrderAppService()

@app.route("/orders/<int:order_id>")
def get_order(order_id):
    order_dto = order_service.get_order(order_id)
    return order_dto.to_dict()
```

### TypeScript 依赖审计

```typescript
// ❌ 违规：Controller 直接使用 ORM
import { getRepository } from "typeorm";
import { OrderEntity } from "../entities/OrderEntity";

export class OrderController {
  async getOrder(req: Request, res: Response) {
    const repo = getRepository(OrderEntity);
    const order = await repo.findOne({ where: { id: req.params.id } });
    res.json(order); // 实体直接暴露
  }
}

// ✅ 正确：Controller 委托给 AppService
import { OrderAppService } from "../services/OrderAppService";

export class OrderController {
  constructor(private orderAppService: OrderAppService) {}

  async getOrder(req: Request, res: Response) {
    const orderDto = await this.orderAppService.getOrder(req.params.id);
    res.json(orderDto);
  }
}
```

---

## 第4步: DTO 规划

### DTO 转换策略

```
  表现层              应用服务层            领域层              基础设施层
  ┌──────┐           ┌──────────┐        ┌──────────┐        ┌──────────┐
  │请求DTO│──转换──→  │ Command  │──映射→ │领域对象   │──映射→ │持久化实体 │
  └──────┘           └──────────┘        └──────────┘        └──────────┘
  ┌──────┐           ┌──────────┐        ┌──────────┐        ┌──────────┐
  │响应DTO│←──转换──  │ 查询结果 │←─映射─ │领域对象   │←─映射─ │持久化实体 │
  └──────┘           └──────────┘        └──────────┘        └──────────┘
```

### DTO 定义清单

```
需要定义的 DTO：

请求 DTO：
  □ CreateOrderRequest   - 创建订单请求
  □ UpdateOrderRequest   - 更新订单请求
  □ OrderQueryRequest    - 查询订单请求
  用途：隔离外部输入格式与内部模型

响应 DTO：
  □ OrderDTO             - 订单响应
  □ OrderListDTO         - 订单列表响应
  □ OrderSummaryDTO      - 订单摘要响应
  用途：隔离内部模型与外部输出格式

命令对象：
  □ CreateOrderCommand   - 创建订单命令
  □ CancelOrderCommand   - 取消订单命令
  用途：应用服务层的输入，携带业务意图
```

### Java DTO 示例

```java
// 请求 DTO（表现层）
public class CreateOrderRequest {
    @NotBlank(message = "客户ID不能为空")
    private String customerId;
    @NotEmpty(message = "订单项不能为空")
    private List<OrderItemRequest> items;

    // getter/setter
}

// 命令对象（应用服务层）
public class CreateOrderCommand {
    private final String customerId;
    private final List<OrderItemInfo> items;

    public CreateOrderCommand(String customerId, List<OrderItemInfo> items) {
        this.customerId = customerId;
        this.items = List.copyOf(items);
    }
    // getter
}

// 响应 DTO（表现层）
public class OrderDTO {
    private String orderId;
    private String status;
    private BigDecimal totalAmount;
    private LocalDateTime createdAt;

    // 从领域对象转换
    public static OrderDTO fromDomain(Order order) {
        OrderDTO dto = new OrderDTO();
        dto.orderId = order.getId().getValue();
        dto.status = order.getStatus().name();
        dto.totalAmount = order.getTotalAmount().getValue();
        dto.createdAt = order.getCreatedAt();
        return dto;
    }
}
```

### Python DTO 示例

```python
from dataclasses import dataclass
from typing import List
from decimal import Decimal
from datetime import datetime


# 请求 DTO（表现层）
@dataclass(frozen=True)
class CreateOrderRequest:
    customer_id: str
    items: List[dict]

    def validate(self):
        if not self.customer_id:
            raise ValueError("客户ID不能为空")
        if not self.items:
            raise ValueError("订单项不能为空")


# 命令对象（应用服务层）
@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: List["OrderItemInfo"]


# 响应 DTO（表现层）
@dataclass
class OrderDTO:
    order_id: str
    status: str
    total_amount: Decimal
    created_at: datetime

    @classmethod
    def from_domain(cls, order: "Order") -> "OrderDTO":
        return cls(
            order_id=str(order.id),
            status=order.status.value,
            total_amount=order.total_amount,
            created_at=order.created_at,
        )
```

### TypeScript DTO 示例

```typescript
// 请求 DTO（表现层）
interface CreateOrderRequest {
  customerId: string;
  items: { productId: string; quantity: number; price: number }[];
}

// 命令对象（应用服务层）
class CreateOrderCommand {
  constructor(
    public readonly customerId: string,
    public readonly items: ReadonlyArray<OrderItemInfo>
  ) {}
}

// 响应 DTO（表现层）
interface OrderDTO {
  orderId: string;
  status: string;
  totalAmount: number;
  createdAt: string;
}

function toOrderDTO(order: Order): OrderDTO {
  return {
    orderId: order.id.value,
    status: order.status,
    totalAmount: order.totalAmount.value,
    createdAt: order.createdAt.toISOString(),
  };
}
```

---

## 第5步: 迁移计划

### 分层重构路线图

```
阶段 1：识别边界（1-2 天）
  □ 梳理当前代码中的层边界
  □ 标记所有违规依赖
  □ 绘制当前依赖关系图
  □ 确定目标分层结构

阶段 2：提取领域层（3-5 天）
  □ 识别核心业务规则
  □ 将业务逻辑从 Controller/Service 移至领域对象
  □ 去除领域对象上的框架注解
  □ 确保领域层无外部依赖

阶段 3：引入应用服务层（2-3 天）
  □ 创建应用服务类，编排用例流程
  □ 将事务管理提升到应用服务层
  □ Controller 改为调用 AppService

阶段 4：定义 DTO 与转换（2-3 天）
  □ 创建各层的 DTO 类
  □ 实现 DTO 转换逻辑
  □ 消除实体直接暴露给前端的情况

阶段 5：验证与测试（2-3 天）
  □ 为每层编写独立单元测试
  □ 验证依赖方向正确
  □ 使用架构测试工具（ArchUnit 等）自动检查
```

### 架构测试验证（Java ArchUnit）

```java
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.*;
import static com.tngtech.archunit.library.Architectures.layeredArchitecture;

public class LayerArchitectureTest {

    @Test
    void 分层依赖方向必须正确() {
        var classes = new ClassFileImporter().importPackages("com.example.order");

        ArchRule rule = layeredArchitecture()
            .consideringOnlyDependenciesInLayers()
            .layer("Controller").definedBy("..controller..")
            .layer("AppService").definedBy("..appservice..")
            .layer("Domain").definedBy("..domain..")
            .layer("Infrastructure").definedBy("..infrastructure..")
            .whereLayer("Controller").mayNotBeAccessedByAnyLayer()
            .whereLayer("AppService").mayOnlyBeAccessedByLayers("Controller")
            .whereLayer("Domain").mayOnlyBeAccessedByLayers("AppService", "Infrastructure")
            .whereLayer("Infrastructure").mayOnlyBeAccessedByLayers("AppService");

        rule.check(classes);
    }

    @Test
    void 领域层不得使用Spring注解() {
        var classes = new ClassFileImporter().importPackages("com.example.order.domain");

        ArchRule rule = noClasses()
            .that().resideInAPackage("..domain..")
            .should().beAnnotatedWith("org.springframework.stereotype.Service")
            .orShould().beAnnotatedWith("org.springframework.stereotype.Component")
            .orShould().beAnnotatedWith("org.springframework.web.bind.annotation.RestController");

        rule.check(classes);
    }

    @Test
    void Controller不得直接访问Repository() {
        var classes = new ClassFileImporter().importPackages("com.example.order");

        ArchRule rule = noClasses()
            .that().resideInAPackage("..controller..")
            .should().dependOnClassesThat()
            .resideInAPackage("..infrastructure..");

        rule.check(classes);
    }
}
```

---

## 5 个常见陷阱

### 陷阱 1：贫血服务层

```java
// ❌ Service 层只是简单的透传，没有任何编排逻辑
@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;

    public Order getOrder(Long id) {
        return orderRepository.findById(id).orElse(null); // 透传
    }

    public void save(Order order) {
        orderRepository.save(order); // 透传
    }
}

// ✅ Service 层负责用例编排和事务管理
@Service
public class OrderAppService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;
    private final EventPublisher eventPublisher;

    @Transactional
    public OrderDTO createOrder(CreateOrderCommand command) {
        // 1. 检查库存
        inventoryService.checkAvailability(command.getItems());
        // 2. 创建领域对象
        Order order = Order.create(command.getCustomerId(), command.getItems());
        // 3. 持久化
        orderRepository.save(order);
        // 4. 发布事件
        eventPublisher.publish(new OrderCreatedEvent(order.getId()));
        // 5. 返回 DTO
        return OrderDTO.fromDomain(order);
    }
}
```

### 陷阱 2：领域对象被框架污染

```python
# ❌ 领域模型直接使用 ORM 基类和框架装饰器
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Order(Base):                    # 领域对象继承了 ORM 基类
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50))
    total = Column(Numeric(10, 2))

    def confirm(self):
        self.status = "CONFIRMED"


# ✅ 领域模型是纯粹的业务对象，ORM 映射在基础设施层
class Order:
    """纯领域对象，无框架依赖"""
    def __init__(self, order_id: str, customer_id: str, items: list):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items
        self.status = OrderStatus.CREATED
        self._total = sum(item.subtotal for item in items)

    def confirm(self):
        if self.status != OrderStatus.CREATED:
            raise DomainError("只有新建订单可以确认")
        self.status = OrderStatus.CONFIRMED

    @property
    def total(self):
        return self._total


# 基础设施层的 ORM 映射
class OrderOrmModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50))
    total = Column(Numeric(10, 2))
    status = Column(String(20))

    def to_domain(self) -> Order:
        return Order(
            order_id=str(self.id),
            customer_id=self.customer_id,
            items=self._load_items(),
        )
```

### 陷阱 3：跨层数据泄漏

```typescript
// ❌ 数据库实体直接暴露给前端（包含内部字段和敏感信息）
class OrderController {
  async getOrder(req: Request, res: Response) {
    const order = await this.orderService.getOrder(req.params.id);
    res.json(order); // 暴露了 passwordHash、internalNote 等字段
  }
}

// ✅ 通过 DTO 隔离内部结构
class OrderController {
  async getOrder(req: Request, res: Response) {
    const orderDto = await this.orderAppService.getOrder(req.params.id);
    // orderDto 只包含前端需要的字段
    res.json(orderDto);
  }
}

// DTO 转换（应用服务层内部）
function toOrderDTO(order: Order): OrderDTO {
  return {
    orderId: order.id,
    customerName: order.customerName,
    totalAmount: order.totalAmount,
    status: order.status,
    // 不暴露：internalNote, costPrice, auditTrail
  };
}
```

### 陷阱 4：循环依赖

```java
// ❌ Service 层之间循环依赖
@Service
public class OrderService {
    @Autowired
    private PaymentService paymentService;  // Order → Payment

    public void createOrder(CreateOrderCommand cmd) {
        paymentService.preAuthorize(cmd.getPaymentInfo());
    }
}

@Service
public class PaymentService {
    @Autowired
    private OrderService orderService;  // Payment → Order（循环！）

    public void onPaymentComplete(String paymentId) {
        orderService.confirmOrder(paymentId);
    }
}

// ✅ 通过事件或中介者打破循环
@Service
public class OrderService {
    private final PaymentGateway paymentGateway;  // 依赖接口
    private final EventPublisher eventPublisher;

    public void createOrder(CreateOrderCommand cmd) {
        paymentGateway.preAuthorize(cmd.getPaymentInfo());
        eventPublisher.publish(new OrderCreatedEvent(cmd.getOrderId()));
    }
}

@Service
public class PaymentService {
    // 通过事件监听，无需直接依赖 OrderService
    @EventListener
    public void onOrderCreated(OrderCreatedEvent event) {
        // 处理支付相关逻辑
    }
}
```

### 陷阱 5：层数过多或过少

```
❌ 过少（两层架构）：
  Controller → Repository
  问题：业务逻辑散落在 Controller 中，无法复用

❌ 过多（六七层）：
  Controller → Facade → AppService → DomainService → Domain → DAO → Repository
  问题：简单操作也要穿越多层，开发效率低下

✅ 适度分层（标准四层）：
  Controller → AppService → Domain → Repository
  原则：每层有明确职责，层数与复杂度匹配

判断标准：
  □ 每一层是否有独立的存在价值？
  □ 删除某层后，其职责是否会被其他层合理承担？
  □ 是否存在只做透传的层？（透传层应该合并）
  □ 团队成员是否能清晰说出每层的职责？
```

---

## 决策速查表

| 问题 | 答案 | 行动 |
|------|------|------|
| Controller 中有 SQL？ | 是 | 提取到 Repository，通过 Service 调用 |
| Entity 有 @RestController？ | 是 | 移除注解，分离领域与框架 |
| 前端直接拿到 DB 实体？ | 是 | 引入 DTO 层 |
| Service 只是透传？ | 是 | 要么丰富编排逻辑，要么合并层 |
| 修改一层影响多层？ | 是 | 检查依赖方向，引入接口隔离 |
| 层间有循环依赖？ | 是 | 使用事件机制或接口反转 |
| 不确定代码放哪层？ | - | 问：这是「做什么」还是「怎么做」 |
