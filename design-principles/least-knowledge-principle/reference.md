# 最少知识原则 - 参考实现

## 核心原理

最少知识原则（迪米特法则）要求**一个对象应尽可能少地了解其他对象的内部结构**。只与"直接朋友"交流，不与"陌生人"交流。这降低了类之间的耦合，使系统更易于修改和维护。

### 关键设计要点

| 要点 | 说明 | 应用场景 |
|------|------|---------|
| 只与朋友交谈 | 不调用返回对象的方法 | 所有对象交互 |
| 委托模式 | 在中间对象上添加封装方法 | 消除链式调用 |
| Tell-Don't-Ask | 告诉对象做什么，而非获取数据做决策 | 业务逻辑分配 |
| 信息隐藏 | 不暴露内部数据结构 | 接口设计 |

---

## 场景 1：订单配送地址

### ❌ 反面示例：火车残骸代码

#### Java

```java
// ❌ 违反最少知识原则：链式穿透 3 个对象
public class ShippingService {
    public ShippingLabel createLabel(Order order) {
        // 火车残骸：order → customer → address → 各属性
        String name = order.getCustomer().getName();
        String street = order.getCustomer().getAddress().getStreet();
        String city = order.getCustomer().getAddress().getCity();
        String zipCode = order.getCustomer().getAddress().getZipCode();
        String country = order.getCustomer().getAddress().getCountry();

        // 还需要了解 Customer 和 Address 的内部结构
        if ("CN".equals(order.getCustomer().getAddress().getCountry())) {
            // 国内运费计算
            return new ShippingLabel(name, street, city, zipCode, "国内快递");
        } else {
            // 国际运费计算
            return new ShippingLabel(name, street, city, zipCode, "国际快递");
        }
    }
}

// 问题：
// 1. ShippingService 需要了解 Order、Customer、Address 三个类的内部结构
// 2. 如果 Address 改为嵌套结构（省/市/区），ShippingService 也要改
// 3. 测试时需要构建完整的 Order → Customer → Address 对象链
```

#### Python

```python
# ❌ 违反最少知识原则
class ShippingService:
    def create_label(self, order):
        name = order.customer.name
        street = order.customer.address.street
        city = order.customer.address.city
        zip_code = order.customer.address.zip_code
        country = order.customer.address.country

        if order.customer.address.country == "CN":
            carrier = "国内快递"
        else:
            carrier = "国际快递"

        return ShippingLabel(name, street, city, zip_code, carrier)
```

#### TypeScript

```typescript
// ❌ 违反最少知识原则
class ShippingService {
  createLabel(order: Order): ShippingLabel {
    const name = order.customer.name;
    const street = order.customer.address.street;
    const city = order.customer.address.city;
    const zipCode = order.customer.address.zipCode;
    const country = order.customer.address.country;

    const carrier = order.customer.address.country === "CN" ? "国内快递" : "国际快递";

    return new ShippingLabel(name, street, city, zipCode, carrier);
  }
}
```

---

### ✅ 正面示例：委托方法 + Tell-Don't-Ask

#### Java

```java
// ✅ 遵循最少知识原则

// 值对象：Address 封装地址格式化逻辑
public class Address {
    private final String street;
    private final String city;
    private final String zipCode;
    private final String country;

    public Address(String street, String city, String zipCode, String country) {
        this.street = street;
        this.city = city;
        this.zipCode = zipCode;
        this.country = country;
    }

    public boolean isDomestic() {
        return "CN".equals(country);
    }

    public String format() {
        return String.format("%s, %s %s", street, city, zipCode);
    }

    // 只暴露业务需要的信息
    public String getCity() { return city; }
}

// Customer 提供委托方法
public class Customer {
    private final String name;
    private final Address address;

    public Customer(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    public String getName() { return name; }

    // 委托方法：隐藏 Address 的存在
    public String getFormattedAddress() {
        return address.format();
    }

    public boolean isDomesticCustomer() {
        return address.isDomestic();
    }
}

// Order 提供顶层委托方法
public class Order {
    private final OrderId id;
    private final Customer customer;
    private final List<OrderItem> items;

    public Order(OrderId id, Customer customer, List<OrderItem> items) {
        this.id = id;
        this.customer = customer;
        this.items = items;
    }

    // 委托方法：ShippingService 只需与 Order 交互
    public String getShippingName() {
        return customer.getName();
    }

    public String getShippingAddress() {
        return customer.getFormattedAddress();
    }

    public boolean isDomesticShipping() {
        return customer.isDomesticCustomer();
    }

    // Tell-Don't-Ask：Order 自己创建配送信息
    public ShippingInfo toShippingInfo() {
        return new ShippingInfo(
            customer.getName(),
            customer.getFormattedAddress(),
            customer.isDomesticCustomer() ? "国内快递" : "国际快递"
        );
    }
}

// ShippingService 只与直接朋友 Order 交互
public class ShippingService {
    public ShippingLabel createLabel(Order order) {
        // ✅ 方案 A：使用委托方法
        return new ShippingLabel(
            order.getShippingName(),
            order.getShippingAddress(),
            order.isDomesticShipping() ? "国内快递" : "国际快递"
        );
    }

    public ShippingLabel createLabelV2(Order order) {
        // ✅ 方案 B：Tell-Don't-Ask，让 Order 提供完整的配送信息
        ShippingInfo info = order.toShippingInfo();
        return new ShippingLabel(info.getName(), info.getAddress(), info.getCarrier());
    }
}
```

#### Python

```python
# ✅ 遵循最少知识原则

class Address:
    def __init__(self, street: str, city: str, zip_code: str, country: str):
        self._street = street
        self._city = city
        self._zip_code = zip_code
        self._country = country

    def is_domestic(self) -> bool:
        return self._country == "CN"

    def format(self) -> str:
        return f"{self._street}, {self._city} {self._zip_code}"


class Customer:
    def __init__(self, name: str, address: Address):
        self._name = name
        self._address = address

    @property
    def name(self) -> str:
        return self._name

    def get_formatted_address(self) -> str:
        return self._address.format()

    def is_domestic(self) -> bool:
        return self._address.is_domestic()


class Order:
    def __init__(self, order_id: str, customer: Customer, items: list):
        self._id = order_id
        self._customer = customer
        self._items = items

    def get_shipping_name(self) -> str:
        return self._customer.name

    def get_shipping_address(self) -> str:
        return self._customer.get_formatted_address()

    def is_domestic_shipping(self) -> bool:
        return self._customer.is_domestic()

    def to_shipping_info(self) -> "ShippingInfo":
        carrier = "国内快递" if self._customer.is_domestic() else "国际快递"
        return ShippingInfo(
            name=self._customer.name,
            address=self._customer.get_formatted_address(),
            carrier=carrier,
        )


@dataclass
class ShippingInfo:
    name: str
    address: str
    carrier: str


class ShippingService:
    def create_label(self, order: Order) -> "ShippingLabel":
        # ✅ 只与 order 交互
        info = order.to_shipping_info()
        return ShippingLabel(info.name, info.address, info.carrier)
```

#### TypeScript

```typescript
// ✅ 遵循最少知识原则

class Address {
  constructor(
    private readonly street: string,
    private readonly city: string,
    private readonly zipCode: string,
    private readonly country: string
  ) {}

  isDomestic(): boolean {
    return this.country === "CN";
  }

  format(): string {
    return `${this.street}, ${this.city} ${this.zipCode}`;
  }
}

class Customer {
  constructor(
    private readonly _name: string,
    private readonly address: Address
  ) {}

  get name(): string {
    return this._name;
  }

  getFormattedAddress(): string {
    return this.address.format();
  }

  isDomestic(): boolean {
    return this.address.isDomestic();
  }
}

class Order {
  constructor(
    public readonly id: string,
    private readonly customer: Customer,
    private readonly items: OrderItem[]
  ) {}

  getShippingName(): string {
    return this.customer.name;
  }

  getShippingAddress(): string {
    return this.customer.getFormattedAddress();
  }

  isDomesticShipping(): boolean {
    return this.customer.isDomestic();
  }

  toShippingInfo(): ShippingInfo {
    return {
      name: this.customer.name,
      address: this.customer.getFormattedAddress(),
      carrier: this.customer.isDomestic() ? "国内快递" : "国际快递",
    };
  }
}

class ShippingService {
  createLabel(order: Order): ShippingLabel {
    // ✅ 只与 order 交互
    const info = order.toShippingInfo();
    return new ShippingLabel(info.name, info.address, info.carrier);
  }
}
```

---

## 场景 2：权限检查

### ❌ 反面示例

#### Java

```java
// ❌ Ask 模式：获取多层数据，在外部做权限决策
public class DocumentService {
    public boolean canEdit(User user, Document document) {
        String userRole = user.getRole().getName();
        String userDept = user.getDepartment().getName();
        int userLevel = user.getDepartment().getManager().getLevel();

        String docOwnerDept = document.getOwner().getDepartment().getName();
        String docSensitivity = document.getMetadata().getSensitivity();

        if ("ADMIN".equals(userRole)) return true;
        if (userDept.equals(docOwnerDept) && !"TOP_SECRET".equals(docSensitivity)) return true;
        if (userLevel >= 5 && !"TOP_SECRET".equals(docSensitivity)) return true;
        return false;
    }
}
```

#### Python

```python
# ❌ Ask 模式
class DocumentService:
    def can_edit(self, user, document):
        user_role = user.role.name
        user_dept = user.department.name
        user_level = user.department.manager.level

        doc_owner_dept = document.owner.department.name
        doc_sensitivity = document.metadata.sensitivity

        if user_role == "ADMIN":
            return True
        if user_dept == doc_owner_dept and doc_sensitivity != "TOP_SECRET":
            return True
        if user_level >= 5 and doc_sensitivity != "TOP_SECRET":
            return True
        return False
```

#### TypeScript

```typescript
// ❌ Ask 模式
class DocumentService {
  canEdit(user: User, document: Document): boolean {
    const userRole = user.role.name;
    const userDept = user.department.name;
    const userLevel = user.department.manager.level;

    const docOwnerDept = document.owner.department.name;
    const docSensitivity = document.metadata.sensitivity;

    if (userRole === "ADMIN") return true;
    if (userDept === docOwnerDept && docSensitivity !== "TOP_SECRET") return true;
    if (userLevel >= 5 && docSensitivity !== "TOP_SECRET") return true;
    return false;
  }
}
```

---

### ✅ 正面示例：职责分配到拥有数据的对象

#### Java

```java
// ✅ Tell-Don't-Ask：将权限判断分配到拥有数据的对象

public class User {
    private final Role role;
    private final Department department;

    public boolean isAdmin() {
        return role.isAdmin();
    }

    public boolean isSameDepartment(Department other) {
        return department.equals(other);
    }

    public boolean isSeniorManager() {
        return department.hasManagerWithLevel(5);
    }

    // 顶层委托：用户是否有权编辑文档
    public boolean canEdit(Document document) {
        if (isAdmin()) return true;
        return document.isAccessibleBy(this);
    }
}

public class Document {
    private final User owner;
    private final DocumentMetadata metadata;

    public boolean isAccessibleBy(User user) {
        if (metadata.isTopSecret()) return false;
        if (user.isSameDepartment(owner.getDepartment())) return true;
        if (user.isSeniorManager()) return true;
        return false;
    }

    public Department getOwnerDepartment() {
        return owner.getDepartment();
    }
}

public class DocumentMetadata {
    private final Sensitivity sensitivity;

    public boolean isTopSecret() {
        return sensitivity == Sensitivity.TOP_SECRET;
    }
}

// 调用方极简
public class DocumentService {
    public boolean canEdit(User user, Document document) {
        return user.canEdit(document);  // ✅ 一行搞定
    }
}
```

#### Python

```python
# ✅ Tell-Don't-Ask

class User:
    def __init__(self, role: Role, department: Department):
        self._role = role
        self._department = department

    def is_admin(self) -> bool:
        return self._role.is_admin()

    def is_same_department(self, other: "Department") -> bool:
        return self._department == other

    def is_senior_manager(self) -> bool:
        return self._department.has_manager_with_level(5)

    def can_edit(self, document: "Document") -> bool:
        if self.is_admin():
            return True
        return document.is_accessible_by(self)

    @property
    def department(self) -> "Department":
        return self._department


class Document:
    def __init__(self, owner: User, metadata: "DocumentMetadata"):
        self._owner = owner
        self._metadata = metadata

    def is_accessible_by(self, user: User) -> bool:
        if self._metadata.is_top_secret():
            return False
        if user.is_same_department(self._owner.department):
            return True
        if user.is_senior_manager():
            return True
        return False


class DocumentMetadata:
    def __init__(self, sensitivity: str):
        self._sensitivity = sensitivity

    def is_top_secret(self) -> bool:
        return self._sensitivity == "TOP_SECRET"


# 调用方
class DocumentService:
    def can_edit(self, user: User, document: Document) -> bool:
        return user.can_edit(document)
```

#### TypeScript

```typescript
// ✅ Tell-Don't-Ask

class User {
  constructor(
    private readonly role: Role,
    private readonly _department: Department
  ) {}

  isAdmin(): boolean {
    return this.role.isAdmin();
  }

  isSameDepartment(other: Department): boolean {
    return this._department.equals(other);
  }

  isSeniorManager(): boolean {
    return this._department.hasManagerWithLevel(5);
  }

  get department(): Department {
    return this._department;
  }

  canEdit(document: Document): boolean {
    if (this.isAdmin()) return true;
    return document.isAccessibleBy(this);
  }
}

class Document {
  constructor(
    private readonly owner: User,
    private readonly metadata: DocumentMetadata
  ) {}

  isAccessibleBy(user: User): boolean {
    if (this.metadata.isTopSecret()) return false;
    if (user.isSameDepartment(this.owner.department)) return true;
    if (user.isSeniorManager()) return true;
    return false;
  }
}

class DocumentMetadata {
  constructor(private readonly sensitivity: Sensitivity) {}

  isTopSecret(): boolean {
    return this.sensitivity === Sensitivity.TOP_SECRET;
  }
}

// 调用方
class DocumentService {
  canEdit(user: User, document: Document): boolean {
    return user.canEdit(document);
  }
}
```

---

## 场景 3：通知系统

### ❌ 反面示例

```java
// ❌ 深度穿透获取通知信息
public class NotificationSender {
    public void sendOrderNotification(Order order) {
        String email = order.getCustomer().getContactInfo().getEmail();
        String phone = order.getCustomer().getContactInfo().getPhone();
        String preference = order.getCustomer().getNotificationPreference().getChannel();

        String message = String.format(
            "订单 %s 已确认，总计 %s 元",
            order.getId(),
            order.getPaymentInfo().getAmount().getValue()
        );

        if ("EMAIL".equals(preference)) {
            emailService.send(email, message);
        } else if ("SMS".equals(preference)) {
            smsService.send(phone, message);
        }
    }
}
```

### ✅ 正面示例

```java
// ✅ 职责分配到各对象

public class Order {
    private final OrderId id;
    private final Customer customer;
    private final Money totalAmount;

    public NotificationRequest toConfirmationNotification() {
        String message = String.format("订单 %s 已确认，总计 %s 元",
            id.getValue(), totalAmount.getValue());
        return customer.createNotification(message);
    }
}

public class Customer {
    private final ContactInfo contactInfo;
    private final NotificationPreference preference;

    public NotificationRequest createNotification(String message) {
        return preference.createRequest(contactInfo, message);
    }
}

public class NotificationPreference {
    private final Channel channel;

    public NotificationRequest createRequest(ContactInfo contact, String message) {
        return switch (channel) {
            case EMAIL -> new EmailNotification(contact.getEmail(), message);
            case SMS -> new SmsNotification(contact.getPhone(), message);
        };
    }
}

// 调用方只做分发
public class NotificationSender {
    public void sendOrderNotification(Order order) {
        NotificationRequest notification = order.toConfirmationNotification();
        notificationGateway.send(notification);
    }
}
```

### Python 版本

```python
class Order:
    def to_confirmation_notification(self) -> "NotificationRequest":
        message = f"订单 {self._id} 已确认，总计 {self._total_amount} 元"
        return self._customer.create_notification(message)


class Customer:
    def create_notification(self, message: str) -> "NotificationRequest":
        return self._preference.create_request(self._contact_info, message)


class NotificationPreference:
    def create_request(self, contact: "ContactInfo", message: str) -> "NotificationRequest":
        if self._channel == Channel.EMAIL:
            return EmailNotification(contact.email, message)
        else:
            return SmsNotification(contact.phone, message)


class NotificationSender:
    def send_order_notification(self, order: Order):
        notification = order.to_confirmation_notification()
        self._gateway.send(notification)
```

### TypeScript 版本

```typescript
class Order {
  toConfirmationNotification(): NotificationRequest {
    const message = `订单 ${this.id} 已确认，总计 ${this.totalAmount} 元`;
    return this.customer.createNotification(message);
  }
}

class Customer {
  createNotification(message: string): NotificationRequest {
    return this.preference.createRequest(this.contactInfo, message);
  }
}

class NotificationPreference {
  createRequest(contact: ContactInfo, message: string): NotificationRequest {
    if (this.channel === Channel.EMAIL) {
      return new EmailNotification(contact.email, message);
    }
    return new SmsNotification(contact.phone, message);
  }
}

class NotificationSender {
  sendOrderNotification(order: Order): void {
    const notification = order.toConfirmationNotification();
    this.gateway.send(notification);
  }
}
```

---

## 测试

### Java 测试

```java
class OrderTest {

    @Test
    void 应返回配送名称() {
        Address address = new Address("中关村大街1号", "北京", "100080", "CN");
        Customer customer = new Customer("张三", address);
        Order order = new Order(OrderId.generate(), customer, List.of());

        assertEquals("张三", order.getShippingName());
    }

    @Test
    void 应返回格式化的配送地址() {
        Address address = new Address("中关村大街1号", "北京", "100080", "CN");
        Customer customer = new Customer("张三", address);
        Order order = new Order(OrderId.generate(), customer, List.of());

        assertEquals("中关村大街1号, 北京 100080", order.getShippingAddress());
    }

    @Test
    void 国内订单应标记为国内配送() {
        Address address = new Address("中关村大街1号", "北京", "100080", "CN");
        Customer customer = new Customer("张三", address);
        Order order = new Order(OrderId.generate(), customer, List.of());

        assertTrue(order.isDomesticShipping());
    }

    @Test
    void 国际订单应标记为国际配送() {
        Address address = new Address("5th Ave", "New York", "10001", "US");
        Customer customer = new Customer("John", address);
        Order order = new Order(OrderId.generate(), customer, List.of());

        assertFalse(order.isDomesticShipping());
    }

    @Test
    void toShippingInfo应生成完整配送信息() {
        Address address = new Address("中关村大街1号", "北京", "100080", "CN");
        Customer customer = new Customer("张三", address);
        Order order = new Order(OrderId.generate(), customer, List.of());

        ShippingInfo info = order.toShippingInfo();

        assertEquals("张三", info.getName());
        assertEquals("中关村大街1号, 北京 100080", info.getAddress());
        assertEquals("国内快递", info.getCarrier());
    }
}

class UserPermissionTest {

    @Test
    void 管理员可以编辑任何文档() {
        User admin = new User(Role.ADMIN, new Department("IT"));
        Document doc = new Document(
            new User(Role.STAFF, new Department("HR")),
            new DocumentMetadata(Sensitivity.TOP_SECRET)
        );

        assertTrue(admin.canEdit(doc));
    }

    @Test
    void 同部门非机密文档可以编辑() {
        Department dept = new Department("IT");
        User user = new User(Role.STAFF, dept);
        Document doc = new Document(
            new User(Role.STAFF, dept),
            new DocumentMetadata(Sensitivity.INTERNAL)
        );

        assertTrue(user.canEdit(doc));
    }

    @Test
    void 机密文档不可被非管理员编辑() {
        User user = new User(Role.STAFF, new Department("IT"));
        Document doc = new Document(
            new User(Role.STAFF, new Department("IT")),
            new DocumentMetadata(Sensitivity.TOP_SECRET)
        );

        assertFalse(user.canEdit(doc));
    }
}
```

### Python 测试

```python
class TestOrder:
    def test_应返回配送名称(self):
        address = Address("中关村大街1号", "北京", "100080", "CN")
        customer = Customer("张三", address)
        order = Order("O001", customer, [])

        assert order.get_shipping_name() == "张三"

    def test_应返回格式化的配送地址(self):
        address = Address("中关村大街1号", "北京", "100080", "CN")
        customer = Customer("张三", address)
        order = Order("O001", customer, [])

        assert order.get_shipping_address() == "中关村大街1号, 北京 100080"

    def test_国内订单应标记为国内配送(self):
        address = Address("中关村大街1号", "北京", "100080", "CN")
        customer = Customer("张三", address)
        order = Order("O001", customer, [])

        assert order.is_domestic_shipping() is True

    def test_国际订单应标记为国际配送(self):
        address = Address("5th Ave", "New York", "10001", "US")
        customer = Customer("John", address)
        order = Order("O001", customer, [])

        assert order.is_domestic_shipping() is False

    def test_toShippingInfo应生成完整配送信息(self):
        address = Address("中关村大街1号", "北京", "100080", "CN")
        customer = Customer("张三", address)
        order = Order("O001", customer, [])

        info = order.to_shipping_info()

        assert info.name == "张三"
        assert info.address == "中关村大街1号, 北京 100080"
        assert info.carrier == "国内快递"


class TestUserPermission:
    def test_管理员可以编辑任何文档(self):
        admin = User(Role.ADMIN, Department("IT"))
        doc = Document(
            User(Role.STAFF, Department("HR")),
            DocumentMetadata("TOP_SECRET"),
        )

        assert admin.can_edit(doc) is True

    def test_同部门非机密文档可以编辑(self):
        dept = Department("IT")
        user = User(Role.STAFF, dept)
        doc = Document(User(Role.STAFF, dept), DocumentMetadata("INTERNAL"))

        assert user.can_edit(doc) is True

    def test_机密文档不可被非管理员编辑(self):
        user = User(Role.STAFF, Department("IT"))
        doc = Document(
            User(Role.STAFF, Department("IT")),
            DocumentMetadata("TOP_SECRET"),
        )

        assert user.can_edit(doc) is False
```

### TypeScript 测试

```typescript
describe("Order 最少知识原则", () => {
  const domesticAddress = new Address("中关村大街1号", "北京", "100080", "CN");
  const internationalAddress = new Address("5th Ave", "New York", "10001", "US");

  it("应返回配送名称", () => {
    const customer = new Customer("张三", domesticAddress);
    const order = new Order("O001", customer, []);

    expect(order.getShippingName()).toBe("张三");
  });

  it("应返回格式化的配送地址", () => {
    const customer = new Customer("张三", domesticAddress);
    const order = new Order("O001", customer, []);

    expect(order.getShippingAddress()).toBe("中关村大街1号, 北京 100080");
  });

  it("国内订单应标记为国内配送", () => {
    const customer = new Customer("张三", domesticAddress);
    const order = new Order("O001", customer, []);

    expect(order.isDomesticShipping()).toBe(true);
  });

  it("国际订单应标记为国际配送", () => {
    const customer = new Customer("John", internationalAddress);
    const order = new Order("O001", customer, []);

    expect(order.isDomesticShipping()).toBe(false);
  });

  it("toShippingInfo 应生成完整配送信息", () => {
    const customer = new Customer("张三", domesticAddress);
    const order = new Order("O001", customer, []);

    const info = order.toShippingInfo();

    expect(info.name).toBe("张三");
    expect(info.address).toBe("中关村大街1号, 北京 100080");
    expect(info.carrier).toBe("国内快递");
  });
});

describe("User 权限检查", () => {
  it("管理员可以编辑任何文档", () => {
    const admin = new User(Role.ADMIN, new Department("IT"));
    const doc = new Document(
      new User(Role.STAFF, new Department("HR")),
      new DocumentMetadata(Sensitivity.TOP_SECRET)
    );

    expect(admin.canEdit(doc)).toBe(true);
  });

  it("同部门非机密文档可以编辑", () => {
    const dept = new Department("IT");
    const user = new User(Role.STAFF, dept);
    const doc = new Document(
      new User(Role.STAFF, dept),
      new DocumentMetadata(Sensitivity.INTERNAL)
    );

    expect(user.canEdit(doc)).toBe(true);
  });

  it("机密文档不可被非管理员编辑", () => {
    const user = new User(Role.STAFF, new Department("IT"));
    const doc = new Document(
      new User(Role.STAFF, new Department("IT")),
      new DocumentMetadata(Sensitivity.TOP_SECRET)
    );

    expect(user.canEdit(doc)).toBe(false);
  });
});
```

---

## 重构手法总结

```
火车残骸消除法：

  a.getB().getC().doSomething()

  ┌──────────────────────────────────────────────────┐
  │ 手法 1：在 A 上添加委托方法                        │
  │   a.doSomethingViaC()                            │
  │   适用：A 是调用方的直接朋友                       │
  ├──────────────────────────────────────────────────┤
  │ 手法 2：Tell-Don't-Ask                            │
  │   a.performAction()                               │
  │   适用：外部在获取数据后做业务决策                  │
  ├──────────────────────────────────────────────────┤
  │ 手法 3：引入参数对象                               │
  │   service.doSomething(a.toSomethingInfo())         │
  │   适用：需要传递多个嵌套属性给外部系统              │
  ├──────────────────────────────────────────────────┤
  │ 手法 4：事件通知                                   │
  │   a.onChange(() -> handleChange())                 │
  │   适用：跨模块的间接通信                           │
  └──────────────────────────────────────────────────┘

不需要修改的情况：
  - Fluent API / Builder 模式（返回 this）
  - Stream / 集合操作链
  - 纯数据结构（DTO/Map）的属性访问
  - 跨上下文边界的数据提取
```
