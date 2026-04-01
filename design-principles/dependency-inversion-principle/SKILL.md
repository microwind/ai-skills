---
name: 依赖倒置原则
description: "高层模块不应依赖低层模块，两者都应依赖于抽象。通过依赖抽象而非具体实现，降低模块间耦合。"
license: MIT
---

# 依赖倒置原则 (Dependency Inversion Principle, DIP)

## 概述

依赖倒置原则是SOLID中最被误解的一个，但也是最强大的。它定义了模块间的依赖关系：**高层模块不应依赖低层模块，两者都应依赖于抽象**。

**核心思想**：
- 倒置：从"高层→低层"改为"高层→抽象←低层"
- 面向接口编程，而非面向实现
- 高层模块定义接口，低层模块实现接口
- 通过依赖注入实现松耦合

**关键指标**：
- 具体类依赖 < 总依赖的20%
- 无反向依赖（低层不依赖高层）
- 无循环依赖

## 何时使用

**始终使用**：
- 系统有不同层级的模块（UI、业务、数据库）
- 模块之间存在多依赖关系
- 需要独立测试各模块
- 需要灵活切换底层实现
- 高层业务逻辑频繁改变，低层实现较稳定

**触发短语**：
- "改动数据库实现，影响了业务逻辑"
- "无法单独测试业务层，因为依赖太多具体类"
- "想切换ORM框架，但改动太大"
- "低层实现变化，导致高层代码修改"

## 错误的依赖关系（正常但违反DIP）

```java
// ❌ 常见但错误的设计
public class UserService {
    private UserRepository repository = new UserRepository();  // 直接依赖具体类
    private EmailService emailService = new EmailService();    // 直接依赖具体类
    private PasswordValidator validator = new PasswordValidator();  // 直接依赖具体类

    public void registerUser(String email, String password) {
        validator.validate(password);  // 依赖具体实现
        User user = new User(email, password);
        repository.save(user);         // 依赖具体实现
        emailService.sendWelcomeEmail(email);  // 依赖具体实现
    }
}

// 问题：
// 1. 无法替换实现（想换成MybatisUserRepository？不行，代码写死了）
// 2. 难以测试（无法mock UserRepository）
// 3. 层级混乱（高层UserService依赖低层具体类）
// 4. 改动低层（如数据库驱动），高层都受影响
```

## 正确的依赖关系（遵循DIP）

```java
// ✅ 正确的设计
public interface UserRepository {
    void save(User user);
    User findByEmail(String email);
}

public interface EmailService {
    void sendWelcomeEmail(String email);
}

public interface PasswordValidator {
    void validate(String password) throws ValidationException;
}

// 高层模块只依赖抽象
public class UserService {
    private UserRepository repository;
    private EmailService emailService;
    private PasswordValidator validator;

    // 通过构造注入依赖
    public UserService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator validator) {
        this.repository = repository;
        this.emailService = emailService;
        this.validator = validator;
    }

    public void registerUser(String email, String password) {
        validator.validate(password);
        User user = new User(email, password);
        repository.save(user);
        emailService.sendWelcomeEmail(email);
    }
}

// 低层模块实现高层定义的接口
public class JpaUserRepository implements UserRepository {
    @Override
    public void save(User user) { /* JPA实现 */ }
    @Override
    public User findByEmail(String email) { /* JPA查询 */ }
}

public class SmtpEmailService implements EmailService {
    @Override
    public void sendWelcomeEmail(String email) { /* SMTP发送 */ }
}

// 优点：
// 1. 可以轻松替换实现（换成MongoUserRepository，只需修改注入）
// 2. 易于测试（mock接口很简单）
// 3. 层级清晰（高层定义接口，低层实现接口）
// 4. 改动低层，高层无需改动
```

## 依赖倒置 vs 依赖注入

这两个概念经常混淆：

- **DIP (原则)**：设计原则，定义什么是好的依赖关系
- **DI (技术)**：实现技术，通过注入实现DIP

```java
// ❌ 有DI但没有DIP（注入具体类）
public class UserService {
    private UserRepository repository;

    public UserService(UserRepository repository) {  // DI：注入依赖
        this.repository = repository;               // 但注入的是具体类
    }
}

// ✅ 既有DIP又有DI
public class UserService {
    private IUserRepository repository;  // DIP：依赖抽象

    public UserService(IUserRepository repository) {  // DI：注入依赖
        this.repository = repository;
    }
}
```

## 常见违反DIP的模式

### 1. 直接创建依赖

```java
// ❌ 违反DIP
public class OrderService {
    public void processOrder(Order order) {
        PaymentProcessor processor = new PaymentProcessor();  // 直接new
        processor.charge(order.getAmount());
    }
}

// ✅ 遵循DIP
public class OrderService {
    private PaymentProcessor processor;

    public OrderService(PaymentProcessor processor) {
        this.processor = processor;
    }

    public void processOrder(Order order) {
        processor.charge(order.getAmount());
    }
}
```

### 2. 依赖具体实现

```java
// ❌ 违反DIP
public class UserService {
    private JpaUserRepository repository;  // 依赖具体实现
}

// ✅ 遵循DIP
public class UserService {
    private UserRepository repository;  // 依赖抽象
}
```

### 3. 向下的依赖

```java
// ❌ 违反DIP（混乱的依赖）
// Service (高层) 依赖 Repository (低层)
// Repository (低层) 依赖 Service (高层)  <- 反向依赖！

UserService → UserRepository  // 正常
UserRepository → UserService  // 反向依赖！违反分层

// ✅ 遵循DIP
// 两层都依赖接口，无反向依赖
UserService → UserRepositoryInterface ← UserRepository
```

## 依赖倒置的层级设计

```
❌ 错误的依赖方向（金字塔模式，高层依赖低层）

┌──────────────┐
│ UI Layer     │
└──────┬───────┘
       │ 依赖
       ▼
┌──────────────┐
│ Service      │  <- 高层依赖具体实现
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Repository   │  <- 低层具体实现
└──────────────┘

问题：改动Repository，Service和UI都要改


✅ 正确的依赖方向（倒金字塔，都依赖抽象）

┌──────────────┐
│ UI Layer     │
└──────┬───────┘
       │ 依赖抽象
       ▼
┌──────────────┐
│ Interfaces   │  <- 中间的抽象层（核心）
└──────┬──────┬┴──────┐
       │      │       │ 实现
       ▼      ▼       ▼
  Service   Repository  Validator

优点：改动任何低层实现，高层无需改动
```

## 最佳实践

### 1️⃣ 为每个外部依赖定义接口

```java
// ❌ 不清晰
public class UserService {
    private JpaUserRepository repository;
    private SmtpEmailService emailService;
}

// ✅ 清晰
public class UserService {
    private UserRepository repository;        // 接口
    private EmailService emailService;        // 接口
    private PasswordValidator passwordValidator;  // 接口
}
```

### 2️⃣ 使用构造注入而非属性注入

```java
// ❌ 属性注入（不清晰，难以测试）
@Service
public class UserService {
    @Autowired
    private UserRepository repository;
}

// ✅ 构造注入（清晰，强制注入）
@Service
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

### 3️⃣ 一个方向的依赖流

```
推荐：
UI → Service → Repository → Database
        ↓
      (interfaces)
        ↑
    (implementations)

不推荐有如下情况：
- Repository 依赖 Service
- UI 直接依赖 Repository
- 循环依赖
```

### 4️⃣ 依赖注入容器

```java
// 使用Spring DI容器管理依赖
@Configuration
public class ApplicationConfig {
    @Bean
    public UserRepository userRepository() {
        return new JpaUserRepository();  // 或 MongoUserRepository
    }

    @Bean
    public EmailService emailService() {
        return new SmtpEmailService();
    }

    @Bean
    public UserService userService(
            UserRepository repository,
            EmailService emailService) {
        return new UserService(repository, emailService);
    }
}

// 实际使用
@Autowired
private UserService userService;  // 自动注入，无需知道具体实现
```

## 代码示例 - 完整实现

### Python

```python
from abc import ABC, abstractmethod
from typing import Optional

# 定义抽象接口（高层定义）
class UserRepository(ABC):
    @abstractmethod
    def save(self, user: 'User') -> None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional['User']:
        pass

class EmailService(ABC):
    @abstractmethod
    def send_welcome_email(self, email: str) -> None:
        pass

class PasswordValidator(ABC):
    @abstractmethod
    def validate(self, password: str) -> None:
        pass

# 具体实现（低层实现，实现高层定义的接口）
class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

class JpaUserRepository(UserRepository):
    def save(self, user: User) -> None:
        print(f"Saving user to JPA: {user.email}")

    def find_by_email(self, email: str) -> Optional[User]:
        print(f"Finding user from JPA: {email}")
        return None

class SmtpEmailService(EmailService):
    def send_welcome_email(self, email: str) -> None:
        print(f"Sending SMTP email to {email}")

class StandardPasswordValidator(PasswordValidator):
    def validate(self, password: str) -> None:
        if len(password) < 8:
            raise ValueError("Password too short")
        print(f"Password validated")

# 高层业务模块（只依赖抽象）
class UserService:
    def __init__(
            self,
            repository: UserRepository,
            email_service: EmailService,
            password_validator: PasswordValidator):
        self.repository = repository
        self.email_service = email_service
        self.password_validator = password_validator

    def register_user(self, email: str, password: str) -> User:
        # 只使用接口，不知道具体实现
        self.password_validator.validate(password)
        user = User(email, password)
        self.repository.save(user)
        self.email_service.send_welcome_email(email)
        return user

# 使用示例
if __name__ == "__main__":
    # 注入具体实现，高层不知道
    service = UserService(
        JpaUserRepository(),
        SmtpEmailService(),
        StandardPasswordValidator()
    )

    # 调用时完全不知道具体实现
    user = service.register_user("john@example.com", "StrongPass123")

    # 切换实现：只需创建新的Repository实现
    class MongoUserRepository(UserRepository):
        def save(self, user: User) -> None:
            print(f"Saving user to MongoDB: {user.email}")

        def find_by_email(self, email: str) -> Optional[User]:
            return None

    # 无需修改UserService，仅改注入
    service = UserService(
        MongoUserRepository(),  # 不同的实现
        SmtpEmailService(),
        StandardPasswordValidator()
    )
    user = service.register_user("jane@example.com", "StrongPass456")
```

### TypeScript

```typescript
/**
 * ✅ 遵循DIP的TypeScript设计
 */

// 定义抽象接口
interface UserRepository {
    save(user: User): void;
    findByEmail(email: string): User | null;
}

interface EmailService {
    sendWelcomeEmail(email: string): void;
}

interface PasswordValidator {
    validate(password: string): void;
}

// 具体实现
class User {
    constructor(public email: string, public password: string) {}
}

class JpaUserRepository implements UserRepository {
    save(user: User): void {
        console.log(`Saving user to JPA: ${user.email}`);
    }

    findByEmail(email: string): User | null {
        console.log(`Finding user from JPA: ${email}`);
        return null;
    }
}

class SmtpEmailService implements EmailService {
    sendWelcomeEmail(email: string): void {
        console.log(`Sending SMTP email to ${email}`);
    }
}

class StandardPasswordValidator implements PasswordValidator {
    validate(password: string): void {
        if (password.length < 8) {
            throw new Error("Password too short");
        }
        console.log("Password validated");
    }
}

// 高层业务模块（只依赖抽象）
class UserService {
    constructor(
        private repository: UserRepository,
        private emailService: EmailService,
        private passwordValidator: PasswordValidator
    ) {}

    registerUser(email: string, password: string): User {
        // 只使用接口，不知道具体实现
        this.passwordValidator.validate(password);
        const user = new User(email, password);
        this.repository.save(user);
        this.emailService.sendWelcomeEmail(email);
        return user;
    }
}

// 使用示例
const service = new UserService(
    new JpaUserRepository(),
    new SmtpEmailService(),
    new StandardPasswordValidator()
);

service.registerUser("john@example.com", "StrongPass123");

// 切换实现（MongoDB）
class MongoUserRepository implements UserRepository {
    save(user: User): void {
        console.log(`Saving user to MongoDB: ${user.email}`);
    }

    findByEmail(email: string): User | null {
        return null;
    }
}

// 无需修改UserService
const service2 = new UserService(
    new MongoUserRepository(),
    new SmtpEmailService(),
    new StandardPasswordValidator()
);

service2.registerUser("jane@example.com", "StrongPass456");
```

### Java

```java
// ✅ 完整的DIP实现

// 第1层：定义高层接口（核心业务接口）
public interface UserRepository {
    void save(User user);
    Optional<User> findByEmail(String email);
}

public interface EmailService {
    void sendWelcomeEmail(String email);
}

public interface PasswordValidator {
    void validate(String password) throws ValidationException;
}

// 第2层：高层业务逻辑（仅依赖接口）
@Service
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;
    private final PasswordValidator passwordValidator;

    public UserService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator passwordValidator) {
        this.repository = repository;
        this.emailService = emailService;
        this.passwordValidator = passwordValidator;
    }

    public User registerUser(String email, String password) throws ValidationException {
        passwordValidator.validate(password);
        User user = new User(email, password);
        repository.save(user);
        emailService.sendWelcomeEmail(email);
        return user;
    }
}

// 第3层：低层具体实现（实现第1层接口）
@Repository
public class JpaUserRepository implements UserRepository {
    @Autowired
    private JpaRepository<User, Long> jpaRepository;

    @Override
    public void save(User user) {
        jpaRepository.save(user);
    }

    @Override
    public Optional<User> findByEmail(String email) {
        return jpaRepository.findByEmail(email);
    }
}

@Service
public class SmtpEmailService implements EmailService {
    @Override
    public void sendWelcomeEmail(String email) {
        // SMTP发送邮件
    }
}

@Component
public class StandardPasswordValidator implements PasswordValidator {
    @Override
    public void validate(String password) throws ValidationException {
        if (password.length() < 8) {
            throw new ValidationException("Password too short");
        }
    }
}

// 配置：管理依赖注入
@Configuration
public class ApplicationConfig {
    @Bean
    public UserService userService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator validator) {
        return new UserService(repository, emailService, validator);
    }
}

// 单元测试（因为遵循DIP，很容易mock）
@Test
public void testUserRegistration() {
    // Mock接口（容易！）
    UserRepository mockRepository = mock(UserRepository.class);
    EmailService mockEmailService = mock(EmailService.class);
    PasswordValidator mockValidator = mock(PasswordValidator.class);

    UserService service = new UserService(mockRepository, mockEmailService, mockValidator);

    service.registerUser("john@example.com", "StrongPass123");

    // 验证调用
    verify(mockRepository).save(any(User.class));
    verify(mockEmailService).sendWelcomeEmail("john@example.com");
}
```

## 与依赖注入框架的关系

```
DIP (原则) ← 指导设计
   ↓
DI 框架 ← 实现技术
   ↓
Spring, Guice, Dagger 等 ← 具体工具
```

## 总结

**DIP核心**：
- 定义清晰的抽象（接口）
- 高层依赖抽象，低层实现抽象
- 使用DI框架管理依赖

**效果**：
- 代码松耦合
- 易于测试
- 易于扩展
- 易于切换实现

**记住**：
- 接口定义在高层
- 实现位于低层
- 两者都依赖中间的抽象

这是构建可维护系统的核心原则。
