# 最少知识原则 - 诊断与规划表

## 第1步: 需求诊断 - 你的代码是否违反了最少知识原则？

### 🔍 快速检查清单

```
□ 代码中存在链式调用超过 2 层（a.getB().getC().getD()）
□ 方法内部访问了"朋友的朋友"的属性或方法
□ 一个类需要了解另一个类的内部结构才能工作
□ 修改一个类的内部结构导致多个不相关的类需要修改
□ 方法参数传入对象后，只为了获取该对象内部的某个属性
□ 存在大量 getter 链（火车残骸代码）
□ 单元测试需要构建深层嵌套的 mock 对象
□ 一个模块对另一个模块的内部组织方式有假设
```

**诊断标准**:
- ✅ 0-1 项 → **知识边界控制良好**
- ⚠️ 2-4 项 → **应该考虑引入委托方法**
- ❌ 5 项以上 → **必须立即重构，耦合度过高**

### 🎯 火车残骸（Train Wreck）场景评估

| 场景 | 违规代码 | 危害 | 优先级 |
|------|---------|------|--------|
| 获取嵌套属性 | `order.getCustomer().getAddress().getCity()` | 依赖 3 个类的内部结构 | ⭐⭐⭐⭐⭐ |
| 条件判断深挖 | `if (user.getDept().getManager().getLevel() > 5)` | 业务规则散落 | ⭐⭐⭐⭐⭐ |
| 操作远端对象 | `order.getPayment().getCard().charge(amount)` | 违反 Tell-Don't-Ask | ⭐⭐⭐⭐ |
| 遍历内部集合 | `team.getMembers().get(0).getEmail()` | 暴露内部数据结构 | ⭐⭐⭐⭐ |
| 链式配置 | `config.getDb().getPool().getMaxSize()` | 配置结构泄漏 | ⭐⭐⭐ |

---

## 第2步: 朋友与陌生人分析

### 最少知识原则的"朋友"定义

```
一个对象的方法 M 只应该调用以下"朋友"的方法：

  1. 对象自身（this）
  2. M 的参数对象
  3. M 内部创建的对象
  4. 对象的直接成员变量

不应该调用"陌生人"（朋友返回的对象）的方法。
```

### 朋友/陌生人识别表

```
类名：________________
分析方法：________________

直接朋友（可以调用）：
  □ this（自身）              → 自身方法
  □ 方法参数                  → 参数名：________________
  □ 自身成员变量              → 字段名：________________
  □ 方法内新建的对象           → 变量名：________________

当前调用的陌生人（不应调用）：
  □ ________________.________________()  返回自→ ________________
  □ ________________.________________()  返回自→ ________________
  □ ________________.________________()  返回自→ ________________

重构方向：
  □ 在朋友类上添加委托方法
  □ 将逻辑移到拥有数据的对象中（Tell-Don't-Ask）
  □ 引入中间角色封装交互
```

### Java 朋友/陌生人分析示例

```java
// 分析下面的代码：
public class OrderProcessor {
    private Order order;              // 朋友：成员变量
    private Logger logger;            // 朋友：成员变量

    public void process(Discount discount) {   // 朋友：方法参数
        // ✅ 调用朋友（自身成员变量）
        String orderId = order.getId();

        // ✅ 调用朋友（方法参数）
        BigDecimal rate = discount.getRate();

        // ❌ 调用陌生人（order.getCustomer() 返回的 Customer 是陌生人）
        String city = order.getCustomer().getAddress().getCity();

        // ❌ 调用陌生人（order.getPayment() 返回的 Payment 是陌生人）
        order.getPayment().getCard().charge(order.getTotal());

        // ✅ 方法内新建的对象是朋友
        Receipt receipt = new Receipt(orderId);
        receipt.print();
    }
}
```

### Python 朋友/陌生人分析示例

```python
class InvoiceService:
    def __init__(self, invoice_repo):
        self.invoice_repo = invoice_repo   # 朋友：成员变量

    def send_invoice(self, order):         # 朋友：方法参数 order
        # ✅ 调用朋友
        invoice = self.invoice_repo.find_by_order(order.id)

        # ❌ 陌生人：order.customer 是朋友，但 order.customer.email 的 email 对象是陌生人
        email_address = order.customer.contact_info.email

        # ❌ 陌生人链：通过 invoice 获取 payment 再获取 bank
        bank_name = invoice.payment.bank_account.bank_name

        # ✅ 应该改为：
        email_address = order.get_customer_email()        # 委托方法
        bank_name = invoice.get_payment_bank_name()       # 委托方法
```

### TypeScript 朋友/陌生人分析示例

```typescript
class ShippingService {
  constructor(
    private readonly warehouse: Warehouse,  // 朋友
    private readonly carrier: Carrier       // 朋友
  ) {}

  shipOrder(order: Order): void {           // 朋友：参数
    // ❌ 陌生人：order.customer.address 是陌生人的属性
    const zipCode = order.customer.address.zipCode;

    // ❌ 陌生人链：warehouse 返回的 shelf 是陌生人
    const location = this.warehouse.getShelf(order.items[0].sku).getLocation().getAisle();

    // ✅ 应该改为
    const zipCode2 = order.getShippingZipCode();          // 委托
    const location2 = this.warehouse.getItemLocation(order.items[0].sku);  // 委托
  }
}
```

---

## 第3步: 委托方法规划

### 委托方法设计模板

```
当前违规调用：a.getB().getC().doSomething()

重构方案：

方案 A - 在 A 上添加委托方法：
  a.doSomethingViaC()
  └── 内部实现：return this.b.getC().doSomething()

方案 B - 在 B 上添加委托方法：
  a.getB().doSomethingViaC()
  └── 内部实现：return this.c.doSomething()

方案 C - 重新分配职责（Tell-Don't-Ask）：
  将逻辑移到拥有数据的对象中
  a.performAction()  // A 知道如何完成整个操作
```

### 委托方法规划清单

```
违规位置 1：
  当前代码：________________
  涉及类：________________ → ________________ → ________________
  选择方案：A / B / C
  新增方法名：________________
  影响范围：________________

违规位置 2：
  当前代码：________________
  涉及类：________________ → ________________ → ________________
  选择方案：A / B / C
  新增方法名：________________
  影响范围：________________

违规位置 3：
  当前代码：________________
  涉及类：________________ → ________________ → ________________
  选择方案：A / B / C
  新增方法名：________________
  影响范围：________________
```

### Java 委托方法示例

```java
// ❌ 重构前：火车残骸
public class ReportGenerator {
    public String generateShippingLabel(Order order) {
        String name = order.getCustomer().getName();
        String street = order.getCustomer().getAddress().getStreet();
        String city = order.getCustomer().getAddress().getCity();
        String zip = order.getCustomer().getAddress().getZipCode();

        return String.format("%s\n%s\n%s, %s", name, street, city, zip);
    }
}

// ✅ 重构后：在 Order 上添加委托方法
public class Order {
    private Customer customer;
    private List<OrderItem> items;

    // 委托方法：隐藏内部结构
    public String getCustomerName() {
        return customer.getName();
    }

    public String getShippingAddress() {
        return customer.getFormattedAddress();
    }
}

public class Customer {
    private String name;
    private Address address;

    public String getName() { return name; }

    // 委托方法
    public String getFormattedAddress() {
        return address.format();
    }
}

public class Address {
    private String street;
    private String city;
    private String zipCode;

    public String format() {
        return String.format("%s\n%s, %s", street, city, zipCode);
    }
}

public class ReportGenerator {
    public String generateShippingLabel(Order order) {
        // ✅ 只与直接朋友 Order 交互
        return String.format("%s\n%s", order.getCustomerName(), order.getShippingAddress());
    }
}
```

### Python 委托方法示例

```python
# ❌ 重构前
class NotificationService:
    def notify_manager(self, employee):
        manager_email = employee.department.manager.contact.email
        manager_name = employee.department.manager.name
        send_email(manager_email, f"通知 {manager_name}")


# ✅ 重构后：逐层添加委托
class Employee:
    def __init__(self, name: str, department: "Department"):
        self.name = name
        self.department = department

    def get_manager_email(self) -> str:
        return self.department.get_manager_email()

    def get_manager_name(self) -> str:
        return self.department.get_manager_name()


class Department:
    def __init__(self, name: str, manager: "Manager"):
        self.name = name
        self.manager = manager

    def get_manager_email(self) -> str:
        return self.manager.get_email()

    def get_manager_name(self) -> str:
        return self.manager.name


class Manager:
    def __init__(self, name: str, contact: "Contact"):
        self.name = name
        self.contact = contact

    def get_email(self) -> str:
        return self.contact.email


class NotificationService:
    def notify_manager(self, employee: Employee):
        # ✅ 只与直接朋友 employee 交互
        send_email(employee.get_manager_email(), f"通知 {employee.get_manager_name()}")
```

### TypeScript 委托方法示例

```typescript
// ❌ 重构前
class CheckoutService {
  processPayment(order: Order): void {
    const cardNumber = order.customer.paymentMethods[0].card.number;
    const expiry = order.customer.paymentMethods[0].card.expiry;
    this.gateway.charge(cardNumber, expiry, order.total);
  }
}

// ✅ 重构后
class Order {
  constructor(
    private readonly customer: Customer,
    private readonly items: OrderItem[]
  ) {}

  getPreferredPaymentCard(): CardInfo {
    return this.customer.getPreferredCard();
  }

  get total(): number {
    return this.items.reduce((sum, item) => sum + item.subtotal, 0);
  }
}

class Customer {
  constructor(private readonly paymentMethods: PaymentMethod[]) {}

  getPreferredCard(): CardInfo {
    return this.paymentMethods[0].getCardInfo();
  }
}

class PaymentMethod {
  constructor(private readonly card: Card) {}

  getCardInfo(): CardInfo {
    return this.card.toInfo();
  }
}

class CheckoutService {
  processPayment(order: Order): void {
    // ✅ 只与 order 交互
    const card = order.getPreferredPaymentCard();
    this.gateway.charge(card.number, card.expiry, order.total);
  }
}
```

---

## 第4步: Tell-Don't-Ask 重构规划

### Tell-Don't-Ask 核心思想

```
❌ Ask（询问）模式：
   从对象中获取数据 → 在外部做决策 → 将结果告诉对象
   data = object.getData()
   result = processExternally(data)
   object.setResult(result)

✅ Tell（命令）模式：
   告诉对象做什么 → 对象自己决策并执行
   object.performAction()
```

### Tell-Don't-Ask 重构清单

```
违规位置 1：
  Ask 代码：________________
  获取的数据：________________
  外部做的决策：________________
  重构为 Tell：________________

违规位置 2：
  Ask 代码：________________
  获取的数据：________________
  外部做的决策：________________
  重构为 Tell：________________
```

### Java Tell-Don't-Ask 示例

```java
// ❌ Ask 模式：外部获取数据做决策
public class OrderService {
    public void applyDiscount(Order order) {
        BigDecimal total = order.getTotal();
        String tier = order.getCustomer().getMembershipTier();
        BigDecimal discount;

        if ("GOLD".equals(tier)) {
            discount = total.multiply(new BigDecimal("0.2"));
        } else if ("SILVER".equals(tier)) {
            discount = total.multiply(new BigDecimal("0.1"));
        } else {
            discount = BigDecimal.ZERO;
        }

        order.setDiscount(discount);
        order.setFinalTotal(total.subtract(discount));
    }
}

// ✅ Tell 模式：告诉对象做什么，对象自己决策
public class Order {
    private Customer customer;
    private Money total;
    private Money discount;
    private Money finalTotal;

    public void applyMemberDiscount() {
        this.discount = customer.calculateDiscount(total);
        this.finalTotal = total.subtract(discount);
    }
}

public class Customer {
    private MembershipTier tier;

    public Money calculateDiscount(Money amount) {
        return tier.applyDiscount(amount);  // 策略模式
    }
}

public enum MembershipTier {
    GOLD(new BigDecimal("0.2")),
    SILVER(new BigDecimal("0.1")),
    BRONZE(BigDecimal.ZERO);

    private final BigDecimal rate;

    MembershipTier(BigDecimal rate) { this.rate = rate; }

    public Money applyDiscount(Money amount) {
        return amount.multiply(rate);
    }
}

// 调用方只需：
order.applyMemberDiscount();  // Tell，不 Ask
```

### Python Tell-Don't-Ask 示例

```python
# ❌ Ask 模式
class ShippingCalculator:
    def calculate_cost(self, order):
        weight = 0
        for item in order.get_items():
            product = item.get_product()
            weight += product.get_weight() * item.get_quantity()

        address = order.get_customer().get_address()
        zone = self.get_zone(address.get_zip_code())

        if zone == "LOCAL":
            return weight * 0.5
        elif zone == "DOMESTIC":
            return weight * 1.0
        else:
            return weight * 2.5


# ✅ Tell 模式
class Order:
    def __init__(self, customer, items):
        self._customer = customer
        self._items = items

    def calculate_total_weight(self) -> float:
        return sum(item.get_weight() for item in self._items)

    def get_shipping_zone(self) -> str:
        return self._customer.get_shipping_zone()

    def calculate_shipping_cost(self, rate_calculator) -> float:
        """Tell：订单自己计算运费"""
        weight = self.calculate_total_weight()
        zone = self.get_shipping_zone()
        return rate_calculator.get_rate(zone, weight)


class Customer:
    def __init__(self, name, address):
        self._name = name
        self._address = address

    def get_shipping_zone(self) -> str:
        return self._address.get_zone()


# 调用方：
cost = order.calculate_shipping_cost(rate_calculator)
```

### TypeScript Tell-Don't-Ask 示例

```typescript
// ❌ Ask 模式
class PermissionChecker {
  canAccess(user: User, resource: Resource): boolean {
    const role = user.getRole();
    const department = user.getDepartment().getName();
    const resourceOwner = resource.getOwner().getDepartment().getName();
    const accessLevel = resource.getAccessLevel();

    if (role === "ADMIN") return true;
    if (department === resourceOwner && accessLevel !== "CONFIDENTIAL") return true;
    return false;
  }
}

// ✅ Tell 模式：把判断逻辑分配到拥有数据的对象
class User {
  constructor(
    private readonly role: Role,
    private readonly department: Department
  ) {}

  isAdmin(): boolean {
    return this.role === Role.ADMIN;
  }

  isSameDepartment(other: Department): boolean {
    return this.department.equals(other);
  }
}

class Resource {
  constructor(
    private readonly owner: User,
    private readonly accessLevel: AccessLevel,
    private readonly ownerDepartment: Department
  ) {}

  isAccessibleBy(user: User): boolean {
    if (user.isAdmin()) return true;
    if (user.isSameDepartment(this.ownerDepartment) && !this.isConfidential()) {
      return true;
    }
    return false;
  }

  private isConfidential(): boolean {
    return this.accessLevel === AccessLevel.CONFIDENTIAL;
  }
}

// 调用方：
const canAccess = resource.isAccessibleBy(user);  // Tell，不 Ask
```

---

## 5 个常见陷阱

### 陷阱 1：过度委托导致类膨胀

```java
// ❌ 为每一个嵌套属性都创建委托方法，导致类方法爆炸
public class Order {
    private Customer customer;

    public String getCustomerName() { return customer.getName(); }
    public String getCustomerEmail() { return customer.getEmail(); }
    public String getCustomerPhone() { return customer.getPhone(); }
    public String getCustomerStreet() { return customer.getAddress().getStreet(); }
    public String getCustomerCity() { return customer.getAddress().getCity(); }
    public String getCustomerZip() { return customer.getAddress().getZipCode(); }
    public String getCustomerCountry() { return customer.getAddress().getCountry(); }
    // ... 还有更多

// ✅ 只为实际需要的业务场景创建有意义的委托方法
public class Order {
    private Customer customer;

    // 只暴露业务需要的方法
    public String getShippingAddress() {
        return customer.getFormattedShippingAddress();
    }

    public String getContactInfo() {
        return customer.getContactSummary();
    }
}
```

### 陷阱 2：混淆数据结构与对象

```python
# 数据结构（DTO/Value Object）的链式访问是合理的
order_dto = {
    "customer": {"name": "张三", "address": {"city": "北京"}},
    "total": 100.0,
}
# ✅ 这是数据结构，链式访问 OK
city = order_dto["customer"]["address"]["city"]


# 对象的链式调用才需要遵循最少知识原则
# ❌ 这是对象，不应链式调用
city = order.get_customer().get_address().get_city()

# ✅ 应该委托
city = order.get_shipping_city()
```

### 陷阱 3：在流式 API 上误用原则

```typescript
// ✅ 流式 API（Fluent Interface）不违反最少知识原则
// 因为每个方法返回的都是同一个构建器对象
const query = QueryBuilder.select("*")
  .from("orders")
  .where("status", "=", "ACTIVE")
  .orderBy("created_at", "DESC")
  .limit(10)
  .build();

// ✅ Stream/集合操作也不违反
const names = orders
  .filter((o) => o.isActive())
  .map((o) => o.customerName)
  .sort();

// ❌ 这才是违反：每一步返回不同类型的对象
const city = order.getCustomer().getAddress().getCity();
```

### 陷阱 4：不区分"问"和"告诉"的场景

```java
// ❌ 有些人把所有查询都改成了 Tell 模式，导致接口不自然
public class Account {
    // 过度 Tell：让 Account 自己打印余额
    public void printBalance(PrintStream out) {
        out.println("余额: " + this.balance);
    }
}

// ✅ 查询类方法返回值是合理的（CQS 原则）
public class Account {
    public Money getBalance() {
        return this.balance;
    }
}

// Tell-Don't-Ask 的重点是：不要获取数据后在外部做业务决策
// 查询数据用于展示是完全合理的
```

### 陷阱 5：忽视上下文边界

```python
# ❌ 跨越上下文边界时过度封装
class OrderService:
    def process(self, order):
        # 跨上下文调用：支付系统和物流系统是独立上下文
        # 这里需要提取数据传递给外部系统，是合理的
        payment_info = order.get_payment_info()  # 提取数据
        self.payment_gateway.charge(payment_info)  # 传递给外部


# ✅ 在同一个上下文内才需要严格遵循最少知识原则
class OrderService:
    def process(self, order):
        # 同一上下文内，使用 Tell 模式
        order.confirm()
        order.schedule_shipment(self.shipping_scheduler)

        # 跨上下文时，提取必要数据传递给外部 API
        payment_request = order.to_payment_request()  # 创建跨上下文的 DTO
        self.payment_gateway.charge(payment_request)
```

---

## 决策速查表

| 问题 | 答案 | 行动 |
|------|------|------|
| 链式调用超过 2 层？ | 是 | 添加委托方法 |
| 获取数据后在外部做业务决策？ | 是 | 改为 Tell-Don't-Ask |
| 返回的是同类型的 Fluent API？ | 是 | 不需要修改，这不违规 |
| 是纯数据结构的属性访问？ | 是 | 不需要修改，DTO 可以直接访问 |
| 委托方法导致类超过 20 个公开方法？ | 是 | 考虑拆分类，职责可能过多 |
| 跨上下文需要传递数据？ | 是 | 使用 DTO，不必强制委托 |
| 单测需要 3 层以上的 mock？ | 是 | 一定违反了最少知识原则 |
