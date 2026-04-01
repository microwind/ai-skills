# 依赖倒置原则 - 参考实现

## 核心原理

DIP 的本质是改变依赖方向：从"下对上"改为"向中间靠"。

```
传统设计（违反DIP）：
UI → Service → Repository → Database
高层 → 低层 → 更低层

DIP设计：
      ↓ 依赖
┌─────────────┐
│  接口层     │
│(定义合约)   │
└─────────────┘
    ↑      ↑
    |      | 实现
Service  Repository
(高层)    (低层)

都依赖中间的接口，方向一致
```

---

## Java 完整参考实现

```java
// 第1层：高层定义的接口（核心）
public interface UserRepository {
    void save(User user);
    Optional<User> findById(String id);
    Optional<User> findByEmail(String email);
}

public interface EmailService {
    void sendWelcomeEmail(String email, String name);
    void sendPasswordReset(String email);
}

public interface PasswordValidator {
    void validate(String password) throws ValidationException;
}

public interface AuditLogger {
    void log(String message);
}

// 第2层：高层业务逻辑（仅依赖接口）
@Service
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;
    private final PasswordValidator passwordValidator;
    private final AuditLogger auditLogger;

    // 构造注入所有依赖
    public UserService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator passwordValidator,
            AuditLogger auditLogger) {
        this.repository = repository;
        this.emailService = emailService;
        this.passwordValidator = passwordValidator;
        this.auditLogger = auditLogger;
    }

    public void registerUser(String email, String password, String name)
            throws ValidationException {
        // 所有调用都通过接口，无需知道具体实现
        passwordValidator.validate(password);

        User user = new User(email, password, name);
        repository.save(user);

        emailService.sendWelcomeEmail(email, name);

        auditLogger.log("User registered: " + email);
    }

    public void resetPassword(String email) throws Exception {
        Optional<User> user = repository.findByEmail(email);
        if (!user.isPresent()) {
            throw new Exception("User not found");
        }

        emailService.sendPasswordReset(email);
        auditLogger.log("Password reset requested for: " + email);
    }
}

// 第3层：低层具体实现（实现第1层接口）
@Repository
public class JpaUserRepository implements UserRepository {
    @Autowired
    private JpaRepository<User, String> jpaRepository;

    @Override
    public void save(User user) {
        jpaRepository.save(user);
    }

    @Override
    public Optional<User> findById(String id) {
        return jpaRepository.findById(id);
    }

    @Override
    public Optional<User> findByEmail(String email) {
        return jpaRepository.findByEmail(email);
    }
}

// 低层实现：邮件服务
@Service
public class SmtpEmailService implements EmailService {
    @Autowired
    private JavaMailSender mailSender;

    @Override
    public void sendWelcomeEmail(String email, String name) {
        sendEmail(email, "Welcome", "Hi " + name + ", welcome!");
    }

    @Override
    public void sendPasswordReset(String email) {
        sendEmail(email, "Reset Password", "Click here to reset your password");
    }

    private void sendEmail(String to, String subject, String body) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject(subject);
        message.setText(body);
        mailSender.send(message);
    }
}

// 低层实现：密码验证
@Component
public class StandardPasswordValidator implements PasswordValidator {
    @Override
    public void validate(String password) throws ValidationException {
        StringBuilder errors = new StringBuilder();

        if (password.length() < 8) {
            errors.append("At least 8 characters. ");
        }
        if (!password.matches(".*[A-Z].*")) {
            errors.append("At least one uppercase. ");
        }
        if (!password.matches(".*\\d.*")) {
            errors.append("At least one digit. ");
        }

        if (errors.length() > 0) {
            throw new ValidationException(errors.toString());
        }
    }
}

// 低层实现：审计日志
@Component
public class FileAuditLogger implements AuditLogger {
    private static final Logger logger = LoggerFactory.getLogger(FileAuditLogger.class);

    @Override
    public void log(String message) {
        logger.info(message);
    }
}

// 第4层：DI配置（管理依赖）
@Configuration
public class ApplicationConfiguration {
    @Bean
    public UserRepository userRepository() {
        // 想改成MongoDB？改这一行就行
        return new JpaUserRepository();
        // return new MongoUserRepository();
    }

    @Bean
    public EmailService emailService() {
        // 想改成其他邮件服务？改这一行
        return new SmtpEmailService();
        // return new AliyunEmailService();
    }

    @Bean
    public PasswordValidator passwordValidator() {
        return new StandardPasswordValidator();
    }

    @Bean
    public AuditLogger auditLogger() {
        return new FileAuditLogger();
    }

    @Bean
    public UserService userService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator passwordValidator,
            AuditLogger auditLogger) {
        return new UserService(repository, emailService, passwordValidator, auditLogger);
    }
}

// 单元测试（使用mock）
@Test
public void testUserRegistration() {
    // Mock所有依赖（容易，因为依赖的是接口）
    UserRepository mockRepository = mock(UserRepository.class);
    EmailService mockEmailService = mock(EmailService.class);
    PasswordValidator mockValidator = mock(PasswordValidator.class);
    AuditLogger mockLogger = mock(AuditLogger.class);

    UserService service = new UserService(
        mockRepository, mockEmailService, mockValidator, mockLogger);

    service.registerUser("john@example.com", "StrongPass123", "John");

    // 验证调用
    verify(mockValidator).validate("StrongPass123");
    verify(mockRepository).save(any(User.class));
    verify(mockEmailService).sendWelcomeEmail("john@example.com", "John");
    verify(mockLogger).log(contains("User registered"));
}

// 切换实现（无需修改业务代码）
@Configuration
@Profile("mongodb")
public class MongoConfiguration {
    @Bean
    public UserRepository userRepository() {
        return new MongoUserRepository();  // 简单替换！
    }
}
```

---

## Python 完整参考实现

```python
"""
✅ 完整的DIP实现：Python版本
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

# 第1层：高层定义的接口

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: 'User') -> None:
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional['User']:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional['User']:
        pass

class EmailService(ABC):
    @abstractmethod
    def send_welcome_email(self, email: str, name: str) -> None:
        pass

    @abstractmethod
    def send_password_reset(self, email: str) -> None:
        pass

class PasswordValidator(ABC):
    @abstractmethod
    def validate(self, password: str) -> None:
        pass

class AuditLogger(ABC):
    @abstractmethod
    def log(self, message: str) -> None:
        pass

# 第2层：高层业务逻辑

@dataclass
class User:
    email: str
    password: str
    name: str
    user_id: str = None

class UserService:
    """高层业务逻辑 - 仅依赖抽象"""
    def __init__(
            self,
            repository: UserRepository,
            email_service: EmailService,
            password_validator: PasswordValidator,
            audit_logger: AuditLogger):
        self.repository = repository
        self.email_service = email_service
        self.password_validator = password_validator
        self.audit_logger = audit_logger

    def register_user(self, email: str, password: str, name: str) -> User:
        # 所有调用都通过接口
        self.password_validator.validate(password)

        user = User(email=email, password=password, name=name)
        self.repository.save(user)

        self.email_service.send_welcome_email(email, name)
        self.audit_logger.log(f"User registered: {email}")

        return user

    def reset_password(self, email: str) -> None:
        user = self.repository.find_by_email(email)
        if not user:
            raise ValueError(f"User not found: {email}")

        self.email_service.send_password_reset(email)
        self.audit_logger.log(f"Password reset requested for: {email}")

# 第3层：低层具体实现

class InMemoryUserRepository(UserRepository):
    """实现：内存存储"""
    def __init__(self):
        self._users = {}

    def save(self, user: User) -> None:
        user.user_id = f"user_{len(self._users)}"
        self._users[user.user_id] = user
        print(f"User saved in memory: {user.email}")

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

class SmtpEmailService(EmailService):
    """实现：SMTP邮件"""
    def send_welcome_email(self, email: str, name: str) -> None:
        print(f"Sending SMTP welcome email to {email}")

    def send_password_reset(self, email: str) -> None:
        print(f"Sending SMTP password reset to {email}")

class StandardPasswordValidator(PasswordValidator):
    """实现：标准密码验证"""
    def validate(self, password: str) -> None:
        errors = []

        if len(password) < 8:
            errors.append("At least 8 characters")

        if not any(c.isupper() for c in password):
            errors.append("At least one uppercase")

        if not any(c.isdigit() for c in password):
            errors.append("At least one digit")

        if errors:
            raise ValueError("Password too weak: " + ", ".join(errors))

class ConsoleAuditLogger(AuditLogger):
    """实现：控制台审计日志"""
    def log(self, message: str) -> None:
        print(f"[AUDIT] {message}")

# 第4层：DI容器（管理依赖）

class ServiceContainer:
    """简单的DI容器"""
    def __init__(self):
        self._repository: Optional[UserRepository] = None
        self._email_service: Optional[EmailService] = None
        self._password_validator: Optional[PasswordValidator] = None
        self._audit_logger: Optional[AuditLogger] = None
        self._user_service: Optional[UserService] = None

    def set_repository(self, repository: UserRepository):
        self._repository = repository
        return self

    def set_email_service(self, email_service: EmailService):
        self._email_service = email_service
        return self

    def set_password_validator(self, validator: PasswordValidator):
        self._password_validator = validator
        return self

    def set_audit_logger(self, logger: AuditLogger):
        self._audit_logger = logger
        return self

    def build(self) -> UserService:
        if not all([self._repository, self._email_service,
                   self._password_validator, self._audit_logger]):
            raise ValueError("Missing dependencies")

        return UserService(
            self._repository,
            self._email_service,
            self._password_validator,
            self._audit_logger
        )

# 使用示例
if __name__ == "__main__":
    # 配置DI容器
    container = ServiceContainer()
    container.set_repository(InMemoryUserRepository())
    container.set_email_service(SmtpEmailService())
    container.set_password_validator(StandardPasswordValidator())
    container.set_audit_logger(ConsoleAuditLogger())

    # 获取服务
    user_service = container.build()

    # 使用服务
    user = user_service.register_user("john@example.com", "StrongPass123", "John")
    print(f"User registered: {user}")

    # 切换实现：只需改容器配置
    class AliyunEmailService(EmailService):
        def send_welcome_email(self, email: str, name: str) -> None:
            print(f"Sending Aliyun welcome email to {email}")

        def send_password_reset(self, email: str) -> None:
            print(f"Sending Aliyun password reset to {email}")

    # 无需修改 UserService，仅改容器
    container2 = ServiceContainer()
    container2.set_repository(InMemoryUserRepository())
    container2.set_email_service(AliyunEmailService())  # 不同实现
    container2.set_password_validator(StandardPasswordValidator())
    container2.set_audit_logger(ConsoleAuditLogger())

    user_service2 = container2.build()
    user2 = user_service2.register_user("jane@example.com", "StrongPass456", "Jane")
```

---

## TypeScript 完整参考实现

```typescript
/**
 * ✅ 完整的DIP实现：TypeScript版本
 */

// 第1层：高层定义的接口

interface UserRepository {
    save(user: User): void;
    findById(userId: string): User | null;
    findByEmail(email: string): User | null;
}

interface EmailService {
    sendWelcomeEmail(email: string, name: string): void;
    sendPasswordReset(email: string): void;
}

interface PasswordValidator {
    validate(password: string): void;
}

interface AuditLogger {
    log(message: string): void;
}

// 第2层：数据模型

class User {
    userId: string;

    constructor(
        public email: string,
        public password: string,
        public name: string
    ) {
        this.userId = `user_${Date.now()}`;
    }
}

// 第3层：高层业务逻辑（仅依赖接口）

class UserService {
    constructor(
        private repository: UserRepository,
        private emailService: EmailService,
        private passwordValidator: PasswordValidator,
        private auditLogger: AuditLogger
    ) {}

    registerUser(email: string, password: string, name: string): User {
        // 所有调用都通过接口
        this.passwordValidator.validate(password);

        const user = new User(email, password, name);
        this.repository.save(user);

        this.emailService.sendWelcomeEmail(email, name);
        this.auditLogger.log(`User registered: ${email}`);

        return user;
    }

    resetPassword(email: string): void {
        const user = this.repository.findByEmail(email);
        if (!user) {
            throw new Error(`User not found: ${email}`);
        }

        this.emailService.sendPasswordReset(email);
        this.auditLogger.log(`Password reset for: ${email}`);
    }
}

// 第4层：低层具体实现

class InMemoryUserRepository implements UserRepository {
    private users: Map<string, User> = new Map();

    save(user: User): void {
        this.users.set(user.userId, user);
        console.log(`User saved in memory: ${user.email}`);
    }

    findById(userId: string): User | null {
        return this.users.get(userId) || null;
    }

    findByEmail(email: string): User | null {
        for (const user of this.users.values()) {
            if (user.email === email) {
                return user;
            }
        }
        return null;
    }
}

class SmtpEmailService implements EmailService {
    sendWelcomeEmail(email: string, name: string): void {
        console.log(`Sending SMTP welcome email to ${email}`);
    }

    sendPasswordReset(email: string): void {
        console.log(`Sending SMTP password reset to ${email}`);
    }
}

class StandardPasswordValidator implements PasswordValidator {
    validate(password: string): void {
        const errors: string[] = [];

        if (password.length < 8) {
            errors.push("At least 8 characters");
        }

        if (!/[A-Z]/.test(password)) {
            errors.push("At least one uppercase");
        }

        if (!/\d/.test(password)) {
            errors.push("At least one digit");
        }

        if (errors.length > 0) {
            throw new Error(`Password too weak: ${errors.join(", ")}`);
        }
    }
}

class ConsoleAuditLogger implements AuditLogger {
    log(message: string): void {
        console.log(`[AUDIT] ${message}`);
    }
}

// 第5层：DI容器（管理依赖）

class ServiceContainer {
    private repository: UserRepository | null = null;
    private emailService: EmailService | null = null;
    private passwordValidator: PasswordValidator | null = null;
    private auditLogger: AuditLogger | null = null;

    setRepository(repository: UserRepository): this {
        this.repository = repository;
        return this;
    }

    setEmailService(emailService: EmailService): this {
        this.emailService = emailService;
        return this;
    }

    setPasswordValidator(validator: PasswordValidator): this {
        this.passwordValidator = validator;
        return this;
    }

    setAuditLogger(logger: AuditLogger): this {
        this.auditLogger = logger;
        return this;
    }

    build(): UserService {
        if (!this.repository || !this.emailService ||
            !this.passwordValidator || !this.auditLogger) {
            throw new Error("Missing dependencies");
        }

        return new UserService(
            this.repository,
            this.emailService,
            this.passwordValidator,
            this.auditLogger
        );
    }
}

// 使用示例
const container = new ServiceContainer();
container
    .setRepository(new InMemoryUserRepository())
    .setEmailService(new SmtpEmailService())
    .setPasswordValidator(new StandardPasswordValidator())
    .setAuditLogger(new ConsoleAuditLogger());

const userService = container.build();

// 注册用户
const user = userService.registerUser("john@example.com", "StrongPass123", "John");
console.log(`User registered: ${user.userId}`);

// 切换实现：无需修改UserService
class AliyunEmailService implements EmailService {
    sendWelcomeEmail(email: string, name: string): void {
        console.log(`Sending Aliyun welcome email to ${email}`);
    }

    sendPasswordReset(email: string): void {
        console.log(`Sending Aliyun password reset to ${email}`);
    }
}

// 简单重新配置
const container2 = new ServiceContainer();
container2
    .setRepository(new InMemoryUserRepository())
    .setEmailService(new AliyunEmailService())  // 不同实现
    .setPasswordValidator(new StandardPasswordValidator())
    .setAuditLogger(new ConsoleAuditLogger());

const userService2 = container2.build();
userService2.registerUser("jane@example.com", "StrongPass456", "Jane");
```

---

## 单元测试示例

### Java with Mockito

```java
import static org.mockito.Mockito.*;

@Test
public void testUserRegistration() {
    // 创建mock
    UserRepository mockRepository = mock(UserRepository.class);
    EmailService mockEmailService = mock(EmailService.class);
    PasswordValidator mockValidator = mock(PasswordValidator.class);
    AuditLogger mockLogger = mock(AuditLogger.class);

    // 注入mock
    UserService service = new UserService(
        mockRepository, mockEmailService, mockValidator, mockLogger);

    // 执行
    service.registerUser("john@example.com", "StrongPass123", "John");

    // 验证
    verify(mockValidator).validate("StrongPass123");
    verify(mockRepository).save(any(User.class));
    verify(mockEmailService).sendWelcomeEmail("john@example.com", "John");
}

@Test
public void testPasswordValidationFailure() {
    PasswordValidator mockValidator = mock(PasswordValidator.class);
    doThrow(new ValidationException("Too weak"))
        .when(mockValidator).validate("weak");

    // ... 测试异常情况
}
```

---

## 总结

**DIP的核心**：

1. **定义抽象** - 高层定义接口，低层实现
2. **注入依赖** - 通过构造函数、Setter或容器注入
3. **配置管理** - DI容器管理所有依赖

**效果**：
- 代码松耦合
- 易于测试
- 易于切换实现
- 易于扩展

**关键指标**：
- 无直接依赖具体类
- 所有依赖可mock
- 测试覆盖率 ≥ 80%
- 新增功能无需修改现有业务类

这是构建高质量企业级应用的基础。
