---
name: 单一职责原则
description: "一个类应该只有一个职责，只有一个改变的理由。通过聚焦单一职责，提高代码的可维护性和复用性。"
license: MIT
---

# 单一职责原则 (Single Responsibility Principle, SRP)

## 概述

单一职责原则是SOLID五原则中最基础、最重要的一个。其核心定义是：**一个类应该只有一个职责，只有一个改变的理由**。

**核心思想**：
- 职责即改变的理由
- 一个类只承担一个业务职能
- 不同的职责应该分离到不同的类中
- 提高内聚力，降低耦合度

**关键指标**：
- 每个类的改变理由数量 ≤ 1
- 每个类的业务职责数量 ≤ 1
- 平均方法数 3-5 个
- 平均字段数 2-4 个

## 何时使用

**始终使用**：
- 一个类承担多个不相关的职责
- 修改一个功能需要改动多个无关的类部分
- 测试一个功能需要准备过多的测试数据
- 类的代码行数超过 200 行或方法超过 10 个
- 很难给类命名（如果难以命名，说明职责混乱）

**触发短语/场景**：
- "这个类做了太多事情"
- "改动这个功能涉及多个类部分"
- "这个类很难测试，需要mock很多东西"
- "类名用UserManager、ServiceHelper这样的宽泛名词"
- "类中有多个没关联的属性和方法"

**常见应用**：

| 错误示例 | 正确分离 | 职责分析 |
|---------|---------|--------|
| UserManager（处理用户、密码、验证、邮件） | User, PasswordValidator, EmailSender, UserRepository | 将不同职责拆分 |
| OrderProcessor（处理订单、支付、库存、发货） | Order, PaymentProcessor, InventoryManager, ShippingService | 职责单一化 |
| DatabaseHelper（连接、查询、事务、缓存） | DatabaseConnection, QueryExecutor, TransactionManager, CacheManager | 按功能分离 |

## 职责识别方法

### 1. 改变理由分析

```java
// ❌ 反面示例：多个改变理由
public class User {
    private String name;
    private String email;
    private String password;

    // 理由1：用户信息改变
    public void updateProfile(String name, String email) { }

    // 理由2：密码策略改变
    public void setPassword(String password) {
        if (password.length() < 8) throw new Exception("Too short");
        if (!password.matches(".*[A-Z].*")) throw new Exception("Need uppercase");
    }

    // 理由3：验证规则改变
    public boolean isValidEmail() {
        return email.matches("^[^@]+@[^@]+\\.[^@]+$");
    }

    // 理由4：存储方式改变
    public void save() {
        // 保存到数据库
    }
}

// ✅ 正确示例：单一职责
public class User {
    private String name;
    private String email;
    private String password;

    // 职责：管理用户信息
    public void updateProfile(String name, String email) { }
    public String getName() { return name; }
    public String getEmail() { return email; }
}

public class PasswordValidator {
    // 职责：验证密码强度
    public void validatePassword(String password) throws PasswordException {
        if (password.length() < 8) throw new PasswordException("Too short");
        if (!password.matches(".*[A-Z].*")) throw new PasswordException("Need uppercase");
    }

    public boolean isStrong(String password) { /* ... */ }
}

public class EmailValidator {
    // 职责：验证邮箱格式
    public boolean isValid(String email) {
        return email.matches("^[^@]+@[^@]+\\.[^@]+$");
    }
}

public class UserRepository {
    // 职责：用户数据持久化
    public void save(User user) { /* 保存到数据库 */ }
    public User findById(String id) { /* 从数据库查询 */ }
}
```

### 2. 类名分析法

```java
// ❌ 宽泛的类名（指示职责混乱）
UserHelper          // Helper意味着什么都做
ServiceHelper       // Service也很模糊
Util, Manager       // 这些是职责吗？
Processor           // 处理什么？不清楚

// ✅ 具体的职责名词
UserRegistrationService    // 负责用户注册
PasswordEncryptor         // 负责密码加密
EmailNotificationService  // 负责邮件通知
UserDataValidator         // 负责用户数据验证
```

### 3. 内聚力分析法

```java
// 问题：同一个类中的方法是否都在操作同一组数据？
public class BankAccount {
    private double balance;

    // ✓ 都在操作 balance
    public void deposit(double amount) { balance += amount; }
    public void withdraw(double amount) { balance -= amount; }
    public double getBalance() { return balance; }

    // ❌ 不在操作 balance，职责外的事
    public void sendEmail(String message) { /* ... */ }  // 不应该在这
    public void generateReport() { /* ... */ }           // 不应该在这
    public void updateDatabase() { /* ... */ }           // 不应该在这
}

// 正确做法
public class BankAccount {
    private double balance;

    // 职责：账户管理
    public void deposit(double amount) { balance += amount; }
    public void withdraw(double amount) { balance -= amount; }
    public double getBalance() { return balance; }
}

public class AccountNotificationService {
    // 职责：账户通知
    public void sendDepositNotification(BankAccount account) { /* ... */ }
}

public class AccountReportGenerator {
    // 职责：报表生成
    public void generateAccountStatement(BankAccount account) { /* ... */ }
}
```

### 4. 依赖关系分析法

```java
// ❌ 职责混乱导致依赖混乱
public class User {
    private DatabaseConnection db;           // 为了save()
    private EmailService emailService;       // 为了sendWelcomeEmail()
    private PasswordValidator validator;     // 为了validatePassword()
    private LoggerService logger;            // 为了log()

    // 这个类有太多依赖，说明职责太多
}

// ✅ 职责单一导致依赖清晰
public class User {
    // 只依赖核心数据和操作
    private String name;

    public void updateName(String newName) {
        this.name = newName;
    }
}

public class UserService {
    // 聚合各个单一职责的类
    private UserRepository repository;        // 数据持久化
    private EmailService emailService;        // 邮件通知
    private PasswordValidator validator;      // 密码验证

    public void registerUser(String email, String password) {
        validator.validatePassword(password);
        User user = new User(email, password);
        repository.save(user);
        emailService.sendWelcomeEmail(email);
    }
}
```

## 违反SRP的常见现象

### 1. 类过大（代码臃肿）

```java
// ❌ 300+ 行的超大类
public class OrderManager {
    public void createOrder() { /* 50 lines */ }
    public void processPayment() { /* 60 lines */ }
    public void validateInventory() { /* 40 lines */ }
    public void createShipment() { /* 50 lines */ }
    public void sendNotifications() { /* 50 lines */ }
    public void updateDatabase() { /* 50 lines */ }
    // ... 还有很多方法
}
```

### 2. 难以命名

```java
// ❌ 难以命名的类（说明职责混乱）
public class Processor { }      // Processor？处理什么？
public class Handler { }         // Handler？处理什么？
public class Manager { }         // Manager？管理什么？
public class Helper { }          // Helper？帮助什么？

// ✅ 清晰的职责名称
public class OrderPaymentProcessor { }
public class InventoryUpdateHandler { }
public class UserRegistrationService { }
```

### 3. 测试困难

```java
// ❌ 难以测试（因为职责过多）
@Test
public void testCreateOrder() {
    // 需要mock数据库、支付网关、库存系统、邮件服务...
    OrderManager manager = new OrderManager(
        mockDB, mockPaymentGateway, mockInventory, mockEmailService
    );
    // 难以隔离测试
}

// ✅ 易于测试（职责单一）
@Test
public void testCreateOrder() {
    // 只需要mock仓储层
    Order order = new Order("ITEM-001", 2);
    assertEquals(order.getQuantity(), 2);  // 清晰的单元测试
}

@Test
public void testProcessPayment() {
    // 只需要mock支付网关
    PaymentProcessor processor = new PaymentProcessor(mockPaymentGateway);
    PaymentResult result = processor.process(100);
    assertEquals(result.getStatus(), SUCCESS);
}
```

### 4. 多个改变理由

```java
// ❌ 多个改变理由
public class Employee {
    // 改变理由1：员工信息变化（加薪标准改变）
    public double calculateSalary() { /* 50 lines */ }

    // 改变理由2：报表格式改变
    public String generateReport() { /* 40 lines */ }

    // 改变理由3：数据库表结构改变
    public void save() { /* 30 lines */ }

    // 改变理由4：存储位置改变（文件、数据库、云）
    public void backup() { /* 30 lines */ }
}

// 一个改变就需要修改这个类，职责太多了
```

## 优缺点分析

### ✅ 优点

1. **高内聚** - 类内部相关性强，代码组织清晰
2. **低耦合** - 类之间独立性强，修改影响范围小
3. **易测试** - 单一职责的类更容易编写单元测试
4. **易复用** - 专注于单一职责的类更容易在其他地方复用
5. **易维护** - 代码含义清晰，修改集中
6. **易扩展** - 新增功能通常是添加新类，而非修改现有类

### ❌ 缺点

1. **类数增多** - 拆分过头会导致类过多，文件增加
2. **代码分散** - 相关功能分散在多个文件中
3. **调用链增长** - 功能实现需要多个类协作
4. **学习成本** - 新人需要理解更多的类和它们的关系
5. **过度设计风险** - 对于简单系统可能是过度设计

## 常见问题与解决方案

### 问题1: 拆分到什么程度？

**症状**: 不知道是否需要继续拆分

```java
// ❌ 都混在一起（职责太多）
public class User {
    // 用户信息、认证、权限、审计日志...
}

// ⚠️ 可能过度拆分
public class UserNameHandler { }
public class UserEmailHandler { }
public class UserStatusHandler { }

// ✅ 合理的拆分粒度
public class User {              // 用户信息
    private String name;
    private String email;
}

public class UserAuthentication {  // 认证
    public boolean authenticate(String password) { }
}

public class UserAuthorization {   // 权限
    public boolean hasPermission(String resource) { }
}

public class UserAuditLog {        // 审计日志
    public void logLogin(User user) { }
}
```

**评估标准**：
- 不同的改变理由
- 可以独立测试
- 可以被其他类复用
- 职责名称清晰

### 问题2: 类之间如何协作？

```java
// 当多个职责需要协作时，使用Facade或Service模式聚合
public class UserRegistrationFacade {
    // 聚合多个单一职责的类
    private UserRepository userRepository;
    private PasswordValidator passwordValidator;
    private PasswordEncryptor passwordEncryptor;
    private EmailNotificationService emailService;

    public void registerUser(String email, String password) {
        // 1. 验证密码
        passwordValidator.validate(password);

        // 2. 加密密码
        String encryptedPassword = passwordEncryptor.encrypt(password);

        // 3. 创建用户
        User user = new User(email, encryptedPassword);

        // 4. 保存用户
        userRepository.save(user);

        // 5. 发送邮件
        emailService.sendWelcomeEmail(email);
    }
}
```

### 问题3: 何时合并，何时拆分？

**合并的条件**：
- 两个类总是一起使用
- 两个类都很小且相关性很高
- 分离会导致代码分散和调用链过长

**拆分的条件**：
- 不同的改变理由
- 可以独立复用
- 职责概念完全不同
- 一个类已经超过200行或10个方法

```java
// ❌ 不必要的拆分
public class Money { }
public class Currency { }
public class ExchangeRate { }
// 这些概念紧密相关，合并为 MoneyAmount 更好

// ✅ 必要的拆分
public class Order { }                  // 订单
public class PaymentProcessor { }      // 支付处理（不同的改变理由）
public class InventoryManager { }      // 库存管理（不同的改变理由）
```

## 最佳实践

### 1️⃣ 使用清晰的类名
```java
// ❌ 不清晰
public class Handler { }

// ✅ 清晰
public class UserAuthenticationHandler { }
public class OrderPaymentProcessor { }
public class ProductInventoryValidator { }
```

### 2️⃣ 一个类一个源文件
```java
// ✅ 一个文件一个概念
// UserValidator.java
public class UserValidator { }

// UserRepository.java
public class UserRepository { }

// UserService.java
public class UserService { }
```

### 3️⃣ 使用Facade聚合复杂流程
```java
// 当需要多个类协作时，使用Facade
public class UserRegistrationService {
    private UserValidator validator;
    private UserRepository repository;
    private PasswordEncryptor encryptor;
    private EmailService emailService;

    public void register(String email, String password) {
        // 协调各个单一职责的类
    }
}
```

### 4️⃣ 依赖注入降低耦合
```java
// ✅ 通过注入依赖，降低耦合
public class UserService {
    private final UserRepository repository;
    private final PasswordValidator validator;

    // 构造注入
    public UserService(UserRepository repository, PasswordValidator validator) {
        this.repository = repository;
        this.validator = validator;
    }
}
```

### 5️⃣ 定期重构检查职责
```
每次修改时询问自己：
1. 这个改动涉及多少个责任范围？
2. 如果改两个不相关的功能，需要改同一个类吗？
3. 有多少个理由可以改这个类？
```

## 代码示例综合

### Python 实现

```python
# ❌ 违反SRP的设计
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    # 职责1：用户信息
    def update_profile(self, name, email):
        self.name = name
        self.email = email

    # 职责2：密码验证
    def validate_password(self, password):
        if len(password) < 8:
            raise ValueError("Password too short")
        return True

    # 职责3：数据库操作
    def save(self):
        # SQL save logic
        pass

    # 职责4：邮件发送
    def send_welcome_email(self):
        # Email logic
        pass

# ✅ 遵循SRP的设计
class User:
    """职责：管理用户信息"""
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def update_profile(self, name, email):
        self.name = name
        self.email = email

class PasswordValidator:
    """职责：验证密码强度"""
    @staticmethod
    def validate(password):
        if len(password) < 8:
            raise ValueError("Password too short")
        if not any(c.isupper() for c in password):
            raise ValueError("Need uppercase letter")
        return True

class UserRepository:
    """职责：用户数据持久化"""
    def save(self, user):
        # Save to database
        pass

    def find_by_id(self, user_id):
        # Query from database
        pass

class EmailService:
    """职责：邮件发送"""
    def send_welcome_email(self, email):
        # Send email logic
        pass

class UserService:
    """聚合各个单一职责的类，协调业务流程"""
    def __init__(self, repository, validator, email_service):
        self.repository = repository
        self.validator = validator
        self.email_service = email_service

    def register_user(self, name, email, password):
        # 1. 验证密码
        self.validator.validate(password)

        # 2. 创建用户
        user = User(name, email)

        # 3. 保存用户
        self.repository.save(user)

        # 4. 发送欢迎邮件
        self.email_service.send_welcome_email(email)

        return user
```

### TypeScript 实现

```typescript
// ✅ 遵循SRP的设计

// 职责1：用户信息管理
class User {
    constructor(
        public readonly id: string,
        public name: string,
        public email: string
    ) {}

    updateProfile(name: string, email: string): void {
        this.name = name;
        this.email = email;
    }

    getInfo(): { name: string; email: string } {
        return { name: this.name, email: this.email };
    }
}

// 职责2：密码验证
class PasswordValidator {
    validate(password: string): void {
        if (password.length < 8) {
            throw new Error("Password must be at least 8 characters");
        }
        if (!/[A-Z]/.test(password)) {
            throw new Error("Password must contain uppercase letter");
        }
        if (!/\d/.test(password)) {
            throw new Error("Password must contain number");
        }
    }
}

// 职责3：密码加密
class PasswordEncryptor {
    encrypt(password: string): string {
        // Encryption logic
        return `encrypted_${password}`;
    }
}

// 职责4：用户数据持久化
class UserRepository {
    private users: Map<string, User> = new Map();

    save(user: User): void {
        this.users.set(user.id, user);
    }

    findById(id: string): User | undefined {
        return this.users.get(id);
    }
}

// 职责5：邮件通知
class EmailNotificationService {
    sendWelcomeEmail(email: string): void {
        console.log(`Sending welcome email to ${email}`);
    }

    sendPasswordResetEmail(email: string): void {
        console.log(`Sending password reset email to ${email}`);
    }
}

// 聚合类：协调各个单一职责的类
class UserRegistrationService {
    constructor(
        private repository: UserRepository,
        private passwordValidator: PasswordValidator,
        private passwordEncryptor: PasswordEncryptor,
        private emailService: EmailNotificationService
    ) {}

    registerUser(name: string, email: string, password: string): User {
        // 1. 验证密码强度
        this.passwordValidator.validate(password);

        // 2. 加密密码
        const encryptedPassword = this.passwordEncryptor.encrypt(password);

        // 3. 创建用户
        const user = new User(Date.now().toString(), name, email);

        // 4. 保存用户
        this.repository.save(user);

        // 5. 发送欢迎邮件
        this.emailService.sendWelcomeEmail(email);

        return user;
    }
}

// 使用示例
const repository = new UserRepository();
const validator = new PasswordValidator();
const encryptor = new PasswordEncryptor();
const emailService = new EmailNotificationService();

const registrationService = new UserRegistrationService(
    repository,
    validator,
    encryptor,
    emailService
);

const newUser = registrationService.registerUser("John Doe", "john@example.com", "SecurePass123");
```

## Java 实现

```java
// ✅ 遵循SRP的完整实现

// 职责1：用户信息
public class User {
    private String id;
    private String name;
    private String email;

    public User(String id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }

    public void updateProfile(String name, String email) {
        this.name = name;
        this.email = email;
    }
}

// 职责2：密码验证
public class PasswordValidator {
    public void validate(String password) throws ValidationException {
        if (password.length() < 8) {
            throw new ValidationException("Password too short");
        }
        if (!password.matches(".*[A-Z].*")) {
            throw new ValidationException("Need uppercase");
        }
        if (!password.matches(".*\\d.*")) {
            throw new ValidationException("Need digit");
        }
    }
}

// 职责3：用户数据持久化
public class UserRepository {
    private final Map<String, User> database = new ConcurrentHashMap<>();

    public void save(User user) {
        database.put(user.getId(), user);
    }

    public User findById(String id) {
        return database.get(id);
    }
}

// 职责4：邮件通知
public class EmailNotificationService {
    public void sendWelcomeEmail(String email) {
        System.out.println("Sending welcome email to " + email);
    }
}

// 聚合类：协调业务流程
public class UserRegistrationService {
    private final UserRepository repository;
    private final PasswordValidator validator;
    private final EmailNotificationService emailService;

    public UserRegistrationService(
            UserRepository repository,
            PasswordValidator validator,
            EmailNotificationService emailService) {
        this.repository = repository;
        this.validator = validator;
        this.emailService = emailService;
    }

    public User registerUser(String name, String email, String password)
            throws ValidationException {
        // 1. 验证密码
        validator.validate(password);

        // 2. 创建用户
        User user = new User(UUID.randomUUID().toString(), name, email);

        // 3. 保存用户
        repository.save(user);

        // 4. 发送邮件
        emailService.sendWelcomeEmail(email);

        return user;
    }
}
```

## 与其他原则的关系

| 原则 | 关系 | 说明 |
|------|------|------|
| **开闭原则** | 相辅相成 | SRP使类职责单一，更易于扩展而不修改 |
| **里氏替换** | 相辅相成 | 单一职责的类更容易遵循LSP |
| **接口隔离** | 相辅相成 | SRP在类层面，ISP在接口层面 |
| **依赖反转** | 相辅相成 | 单一职责的类更容易通过DI降低耦合 |
| **DRY** | 促进关系 | 单一职责有利于代码复用 |

## 何时违反SRP是可以接受的

- 简单的业务实体（如DTO、VO）可以混合数据和简单操作
- 非常小的项目或脚本，过度拆分无益
- 性能关键路径，但应该有注释说明
- 第三方库的不可控部分

---

## 重点总结

SRP是最基础的设计原则，遵循它能大幅改善代码质量：

**核心指标**：
- 职责数 = 1
- 改变理由数 = 1
- 类方法数 ≤ 10
- 类代码行数 ≤ 200

**实施方法**：
1. 用"改变理由"识别职责
2. 用类名明确职责
3. 使用Facade聚合复杂操作
4. 通过DI降低耦合

**效果**：
- 代码更清晰、更易维护
- 测试更简单、覆盖更全面
- 复用更容易、耦合更低
