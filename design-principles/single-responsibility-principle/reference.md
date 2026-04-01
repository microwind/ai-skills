# 单一职责原则 - 参考实现

## 核心原理与设计

### 职责的定义

职责 = **改变的理由**。识别职责的关键是：如果一个类有多个理由被修改，那么它有多个职责。

### 职责与改变的关系

```
示例：UserManager 类

改变理由1：邮箱验证规则升级
改变理由2：密码加密算法变化
改变理由3：数据库驱动升级
改变理由4：邮件服务变更

= 4 个改变的理由 = 至少 4 个职责 = 应该拆分成至少 4 个类

拆分后：
- EmailValidator：仅因为邮箱规则而改变
- PasswordEncryptor：仅因为加密算法而改变
- UserRepository：仅因为数据库而改变
- EmailService：仅因为邮件服务而改变
```

### 设计原则

**高内聚，低耦合**：
- 内聚：类内部的元素紧密相关
- 耦合：类之间的依赖尽量少

---

## Java 参考实现

### 反面示例：违反 SRP 的设计

```java
/**
 * ❌ 反面示例：一个类承担过多职责
 */
public class UserManager {
    private String name;
    private String email;
    private String password;
    private Connection dbConnection;
    private JavaMailSender mailSender;

    // 职责1：用户信息管理
    public void updateProfile(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // 职责2：邮箱验证
    public boolean validateEmail(String email) {
        return email.matches("^[^@]+@[^@]+\\.[^@]+$");
    }

    // 职责3：密码验证
    public void setPassword(String password) {
        if (password.length() < 8) throw new Exception("Too short");
        if (!password.matches(".*[A-Z].*")) throw new Exception("Need uppercase");
        this.password = password;
    }

    // 职责4：数据库操作
    public void save() {
        try {
            Statement stmt = dbConnection.createStatement();
            stmt.execute("INSERT INTO users VALUES (" + name + ", " + email + ")");
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    // 职责5：邮件发送
    public void sendWelcomeEmail() {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(email);
        message.setSubject("Welcome");
        message.setText("Welcome to our system!");
        mailSender.send(message);
    }

    // 职责6：删除用户
    public void delete() {
        try {
            Statement stmt = dbConnection.createStatement();
            stmt.execute("DELETE FROM users WHERE email = '" + email + "'");
        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }
}

// 单元测试非常困难
@Test
public void testSaveUser() {
    // 需要 mock：数据库连接、邮件服务，还要保证邮箱和密码验证
    UserManager user = new UserManager();
    user.setPassword("StrongPass123");  // 涉及密码验证
    user.validateEmail("test@example.com");  // 涉及邮箱验证
    user.save();  // 涉及数据库

    // 问题：一个测试涉及太多职责，难以隔离
}
```

### 正面示例：遵循 SRP 的设计

```java
/**
 * ✅ 正面示例：通过拆分职责，提高代码质量
 */

// 职责1：用户信息（纯数据对象）
public class User {
    private final String id;
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

    @Override
    public String toString() {
        return "User{" + "id='" + id + '\'' + ", name='" + name + '\'' +
               ", email='" + email + '\'' + '}';
    }
}

// 职责2：邮箱验证（单一职责：验证邮箱格式）
public class EmailValidator {
    public void validate(String email) throws ValidationException {
        if (!isValidEmail(email)) {
            throw new ValidationException("Invalid email format: " + email);
        }
    }

    public boolean isValidEmail(String email) {
        return email != null &&
               email.matches("^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\\.[A-Za-z]{2,})$");
    }

    public boolean hasValidDomain(String email) {
        if (!isValidEmail(email)) return false;
        String domain = email.substring(email.indexOf("@") + 1);
        // 可以检查黑名单、验证MX记录等
        return !domain.isEmpty();
    }
}

// 职责3：密码验证（单一职责：验证密码强度）
public class PasswordValidator {
    private static final int MIN_LENGTH = 8;
    private static final String HAS_UPPERCASE = ".*[A-Z].*";
    private static final String HAS_LOWERCASE = ".*[a-z].*";
    private static final String HAS_DIGIT = ".*\\d.*";

    public void validate(String password) throws ValidationException {
        StringBuilder errors = new StringBuilder();

        if (password.length() < MIN_LENGTH) {
            errors.append("At least 8 characters. ");
        }
        if (!password.matches(HAS_UPPERCASE)) {
            errors.append("At least one uppercase letter. ");
        }
        if (!password.matches(HAS_LOWERCASE)) {
            errors.append("At least one lowercase letter. ");
        }
        if (!password.matches(HAS_DIGIT)) {
            errors.append("At least one digit. ");
        }

        if (errors.length() > 0) {
            throw new ValidationException("Password too weak: " + errors.toString());
        }
    }

    public boolean isStrong(String password) {
        try {
            validate(password);
            return true;
        } catch (ValidationException e) {
            return false;
        }
    }
}

// 职责4：密码加密（单一职责：密码加密）
public class PasswordEncryptor {
    public String encrypt(String password) {
        // 使用 bcrypt 或其他安全算法
        return hashPassword(password);
    }

    public boolean matches(String rawPassword, String encryptedPassword) {
        return encrypt(rawPassword).equals(encryptedPassword);
    }

    private String hashPassword(String password) {
        // 简化示例，实际使用 Spring Security 的 BCryptPasswordEncoder
        return String.valueOf(password.hashCode());
    }
}

// 职责5：用户数据持久化（单一职责：数据库操作）
public class UserRepository {
    private final Map<String, User> database = new ConcurrentHashMap<>();
    private final DataSource dataSource;

    public UserRepository(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public void save(User user) {
        // 实际实现中使用 JDBC 或 ORM 框架
        database.put(user.getId(), user);
        System.out.println("User saved: " + user);
    }

    public User findById(String id) {
        return database.get(id);
    }

    public User findByEmail(String email) {
        return database.values().stream()
            .filter(u -> u.getEmail().equals(email))
            .findFirst()
            .orElse(null);
    }

    public void delete(String id) {
        database.remove(id);
        System.out.println("User deleted: " + id);
    }

    public List<User> findAll() {
        return new ArrayList<>(database.values());
    }
}

// 职责6：邮件通知（单一职责：邮件发送）
public class EmailNotificationService {
    private final JavaMailSender mailSender;
    private final String fromAddress;

    public EmailNotificationService(JavaMailSender mailSender, String fromAddress) {
        this.mailSender = mailSender;
        this.fromAddress = fromAddress;
    }

    public void sendWelcomeEmail(String toAddress, String userName) {
        String subject = "Welcome to Our System";
        String body = String.format("Hi %s,\n\nWelcome to our platform!\n\nBest regards", userName);
        sendEmail(toAddress, subject, body);
    }

    public void sendPasswordResetEmail(String toAddress, String resetToken) {
        String subject = "Password Reset Request";
        String body = String.format(
            "Click this link to reset your password: http://example.com/reset?token=%s",
            resetToken
        );
        sendEmail(toAddress, subject, body);
    }

    private void sendEmail(String toAddress, String subject, String body) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromAddress);
            message.setTo(toAddress);
            message.setSubject(subject);
            message.setText(body);
            mailSender.send(message);
            System.out.println("Email sent to " + toAddress);
        } catch (Exception e) {
            System.err.println("Failed to send email: " + e.getMessage());
        }
    }
}

// 核心服务：协调各个单一职责的类（业务流程）
public class UserRegistrationService {
    private final UserRepository userRepository;
    private final EmailValidator emailValidator;
    private final PasswordValidator passwordValidator;
    private final PasswordEncryptor passwordEncryptor;
    private final EmailNotificationService emailService;

    public UserRegistrationService(
            UserRepository userRepository,
            EmailValidator emailValidator,
            PasswordValidator passwordValidator,
            PasswordEncryptor passwordEncryptor,
            EmailNotificationService emailService) {
        this.userRepository = userRepository;
        this.emailValidator = emailValidator;
        this.passwordValidator = passwordValidator;
        this.passwordEncryptor = passwordEncryptor;
        this.emailService = emailService;
    }

    /**
     * 注册新用户的完整流程
     */
    public User registerUser(String name, String email, String password)
            throws ValidationException {
        // 第1步：验证邮箱
        emailValidator.validate(email);

        // 第2步：检查邮箱是否已注册
        if (userRepository.findByEmail(email) != null) {
            throw new ValidationException("Email already registered: " + email);
        }

        // 第3步：验证密码强度
        passwordValidator.validate(password);

        // 第4步：创建用户
        String userId = UUID.randomUUID().toString();
        User user = new User(userId, name, email);

        // 第5步：保存用户（带加密密码，实际应在 User 中存储）
        String encryptedPassword = passwordEncryptor.encrypt(password);
        userRepository.save(user);

        // 第6步：发送欢迎邮件
        try {
            emailService.sendWelcomeEmail(email, name);
        } catch (Exception e) {
            System.err.println("Welcome email failed, but user registered: " + e.getMessage());
        }

        return user;
    }

    /**
     * 重置密码流程
     */
    public void resetPassword(String email, String newPassword) throws ValidationException {
        // 验证邮箱存在
        User user = userRepository.findByEmail(email);
        if (user == null) {
            throw new ValidationException("User not found: " + email);
        }

        // 验证新密码强度
        passwordValidator.validate(newPassword);

        // 加密密码
        String encryptedPassword = passwordEncryptor.encrypt(newPassword);

        // 发送密码重置确认邮件
        emailService.sendPasswordResetEmail(email, "reset-token-123");
    }

    /**
     * 删除用户
     */
    public void deleteUser(String userId) throws ValidationException {
        User user = userRepository.findById(userId);
        if (user == null) {
            throw new ValidationException("User not found: " + userId);
        }
        userRepository.delete(userId);
    }
}

// 单元测试示例（现在容易多了）
class UserRegistrationServiceTest {
    private UserRepository userRepository;
    private EmailValidator emailValidator;
    private PasswordValidator passwordValidator;
    private PasswordEncryptor passwordEncryptor;
    private EmailNotificationService emailService;
    private UserRegistrationService service;

    @Before
    public void setUp() {
        userRepository = new UserRepository(null);
        emailValidator = new EmailValidator();
        passwordValidator = new PasswordValidator();
        passwordEncryptor = new PasswordEncryptor();
        emailService = mock(EmailNotificationService.class);

        service = new UserRegistrationService(
            userRepository, emailValidator, passwordValidator,
            passwordEncryptor, emailService
        );
    }

    @Test
    public void testRegisterUserSuccess() throws ValidationException {
        User user = service.registerUser("John Doe", "john@example.com", "StrongPass123");
        assertEquals("john@example.com", user.getEmail());
        verify(emailService).sendWelcomeEmail("john@example.com", "John Doe");
    }

    @Test
    public void testRegisterUserWithInvalidEmail() {
        assertThrows(ValidationException.class, () ->
            service.registerUser("John", "invalid-email", "StrongPass123")
        );
    }

    @Test
    public void testRegisterUserWithWeakPassword() {
        assertThrows(ValidationException.class, () ->
            service.registerUser("John", "john@example.com", "weak")
        );
    }
}
```

---

## Python 参考实现

```python
"""
✅ 遵循 SRP 的 Python 实现
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import re
import uuid

# 异常定义
class ValidationException(Exception):
    pass

# 职责1：用户信息（纯数据）
@dataclass
class User:
    """用户信息对象 - 职责：存储用户数据"""
    id: str
    name: str
    email: str

    def update_profile(self, name: str, email: str):
        """更新用户信息"""
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

# 职责2：邮箱验证
class EmailValidator:
    """验证邮箱格式 - 职责：邮箱验证"""

    EMAIL_PATTERN = r'^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$'

    @classmethod
    def validate(cls, email: str):
        """验证邮箱，不合法抛出异常"""
        if not cls.is_valid(email):
            raise ValidationException(f"Invalid email format: {email}")

    @classmethod
    def is_valid(cls, email: str) -> bool:
        """检查邮箱是否合法"""
        return email is not None and re.match(cls.EMAIL_PATTERN, email) is not None

    @classmethod
    def get_domain(cls, email: str) -> Optional[str]:
        """提取邮箱域名"""
        if '@' in email:
            return email.split('@')[1]
        return None

# 职责3：密码验证
class PasswordValidator:
    """验证密码强度 - 职责：密码验证"""

    MIN_LENGTH = 8

    @classmethod
    def validate(cls, password: str):
        """验证密码，不合法抛出异常"""
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f"At least {cls.MIN_LENGTH} characters")

        if not re.search(r'[A-Z]', password):
            errors.append("At least one uppercase letter")

        if not re.search(r'[a-z]', password):
            errors.append("At least one lowercase letter")

        if not re.search(r'\d', password):
            errors.append("At least one digit")

        if errors:
            raise ValidationException("Password too weak: " + ", ".join(errors))

    @classmethod
    def is_strong(cls, password: str) -> bool:
        """检查密码是否足够强"""
        try:
            cls.validate(password)
            return True
        except ValidationException:
            return False

# 职责4：密码加密
class PasswordEncryptor:
    """密码加密 - 职责：密码加密和验证"""

    @staticmethod
    def encrypt(password: str) -> str:
        """加密密码（简化示例，实际使用 bcrypt）"""
        # 实际项目中应使用 bcrypt 或 argon2
        return f"hashed_{password}_{hash(password)}"

    @staticmethod
    def matches(raw_password: str, encrypted_password: str) -> bool:
        """验证密码是否匹配"""
        return PasswordEncryptor.encrypt(raw_password) == encrypted_password

# 职责5：用户数据持久化
class UserRepository:
    """用户数据持久化 - 职责：数据库操作"""

    def __init__(self):
        # 模拟数据库
        self._database: dict[str, User] = {}

    def save(self, user: User):
        """保存用户"""
        self._database[user.id] = user
        print(f"User saved: {user}")

    def find_by_id(self, user_id: str) -> Optional[User]:
        """按ID查找用户"""
        return self._database.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        """按邮箱查找用户"""
        for user in self._database.values():
            if user.email == email:
                return user
        return None

    def delete(self, user_id: str):
        """删除用户"""
        if user_id in self._database:
            del self._database[user_id]
            print(f"User deleted: {user_id}")

    def find_all(self) -> List[User]:
        """获取所有用户"""
        return list(self._database.values())

# 职责6：邮件通知
class EmailNotificationService:
    """邮件通知 - 职责：邮件发送"""

    def __init__(self, from_address: str = "noreply@example.com"):
        self.from_address = from_address

    def send_welcome_email(self, to_address: str, user_name: str):
        """发送欢迎邮件"""
        subject = "Welcome to Our System"
        body = f"Hi {user_name},\n\nWelcome to our platform!\n\nBest regards"
        self._send_email(to_address, subject, body)

    def send_password_reset_email(self, to_address: str, reset_token: str):
        """发送密码重置邮件"""
        subject = "Password Reset Request"
        body = f"Click this link to reset your password: http://example.com/reset?token={reset_token}"
        self._send_email(to_address, subject, body)

    def _send_email(self, to_address: str, subject: str, body: str):
        """发送邮件（私有方法）"""
        try:
            # 实际项目中调用真实的邮件服务（SMTP）
            print(f"Email sent to {to_address}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
        except Exception as e:
            print(f"Failed to send email: {e}")

# 核心服务：协调各个单一职责的类
class UserRegistrationService:
    """用户注册服务 - 职责：协调业务流程"""

    def __init__(
            self,
            user_repository: UserRepository,
            email_validator: EmailValidator,
            password_validator: PasswordValidator,
            password_encryptor: PasswordEncryptor,
            email_service: EmailNotificationService
    ):
        self.repository = user_repository
        self.email_validator = email_validator
        self.password_validator = password_validator
        self.password_encryptor = password_encryptor
        self.email_service = email_service

    def register_user(self, name: str, email: str, password: str) -> User:
        """注册新用户的完整流程"""
        # 第1步：验证邮箱
        self.email_validator.validate(email)

        # 第2步：检查邮箱是否已注册
        if self.repository.find_by_email(email) is not None:
            raise ValidationException(f"Email already registered: {email}")

        # 第3步：验证密码强度
        self.password_validator.validate(password)

        # 第4步：创建用户
        user = User(id=str(uuid.uuid4()), name=name, email=email)

        # 第5步：保存用户
        self.repository.save(user)

        # 第6步：发送欢迎邮件
        try:
            self.email_service.send_welcome_email(email, name)
        except Exception as e:
            print(f"Welcome email failed, but user registered: {e}")

        return user

    def reset_password(self, email: str, new_password: str):
        """重置密码流程"""
        # 验证邮箱存在
        user = self.repository.find_by_email(email)
        if user is None:
            raise ValidationException(f"User not found: {email}")

        # 验证新密码强度
        self.password_validator.validate(new_password)

        # 发送密码重置邮件
        self.email_service.send_password_reset_email(email, "reset-token-123")

    def delete_user(self, user_id: str):
        """删除用户"""
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise ValidationException(f"User not found: {user_id}")
        self.repository.delete(user_id)

# 使用示例
if __name__ == "__main__":
    # 创建依赖
    repository = UserRepository()
    email_validator = EmailValidator()
    password_validator = PasswordValidator()
    password_encryptor = PasswordEncryptor()
    email_service = EmailNotificationService()

    # 创建服务
    service = UserRegistrationService(
        repository, email_validator, password_validator,
        password_encryptor, email_service
    )

    # 注册用户
    try:
        user = service.register_user("John Doe", "john@example.com", "StrongPass123")
        print(f"\nUser registered successfully: {user}")
    except ValidationException as e:
        print(f"Registration failed: {e}")

    # 尝试注册相同邮箱
    try:
        user2 = service.register_user("Jane Doe", "john@example.com", "StrongPass123")
    except ValidationException as e:
        print(f"Second registration failed (expected): {e}")

    # 尝试注册弱密码
    try:
        user3 = service.register_user("Bob", "bob@example.com", "weak")
    except ValidationException as e:
        print(f"Registration with weak password failed (expected): {e}")
```

---

## TypeScript 参考实现

```typescript
/**
 * ✅ 遵循 SRP 的 TypeScript 实现
 */

// 异常定义
class ValidationException extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ValidationException';
    }
}

// 职责1：用户信息（纯数据）
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

    toString(): string {
        return `User(id=${this.id}, name=${this.name}, email=${this.email})`;
    }
}

// 职责2：邮箱验证
class EmailValidator {
    private static readonly EMAIL_PATTERN =
        /^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$/;

    static validate(email: string): void {
        if (!this.isValid(email)) {
            throw new ValidationException(`Invalid email format: ${email}`);
        }
    }

    static isValid(email: string | null): boolean {
        if (!email) return false;
        return this.EMAIL_PATTERN.test(email);
    }

    static getDomain(email: string): string | null {
        const parts = email.split('@');
        return parts.length === 2 ? parts[1] : null;
    }
}

// 职责3：密码验证
class PasswordValidator {
    private static readonly MIN_LENGTH = 8;

    static validate(password: string): void {
        const errors: string[] = [];

        if (password.length < this.MIN_LENGTH) {
            errors.push(`At least ${this.MIN_LENGTH} characters`);
        }

        if (!/[A-Z]/.test(password)) {
            errors.push('At least one uppercase letter');
        }

        if (!/[a-z]/.test(password)) {
            errors.push('At least one lowercase letter');
        }

        if (!/\d/.test(password)) {
            errors.push('At least one digit');
        }

        if (errors.length > 0) {
            throw new ValidationException(`Password too weak: ${errors.join(', ')}`);
        }
    }

    static isStrong(password: string): boolean {
        try {
            this.validate(password);
            return true;
        } catch {
            return false;
        }
    }
}

// 职责4：密码加密
class PasswordEncryptor {
    static encrypt(password: string): string {
        // 简化示例，实际使用 bcrypt
        return `hashed_${password}_${password.length}`;
    }

    static matches(rawPassword: string, encryptedPassword: string): boolean {
        return this.encrypt(rawPassword) === encryptedPassword;
    }
}

// 职责5：用户数据持久化
class UserRepository {
    private database: Map<string, User> = new Map();

    save(user: User): void {
        this.database.set(user.id, user);
        console.log(`User saved: ${user}`);
    }

    findById(userId: string): User | undefined {
        return this.database.get(userId);
    }

    findByEmail(email: string): User | undefined {
        for (const user of this.database.values()) {
            if (user.email === email) {
                return user;
            }
        }
        return undefined;
    }

    delete(userId: string): void {
        if (this.database.has(userId)) {
            this.database.delete(userId);
            console.log(`User deleted: ${userId}`);
        }
    }

    findAll(): User[] {
        return Array.from(this.database.values());
    }
}

// 职责6：邮件通知
class EmailNotificationService {
    constructor(private fromAddress: string = 'noreply@example.com') {}

    sendWelcomeEmail(toAddress: string, userName: string): void {
        const subject = 'Welcome to Our System';
        const body = `Hi ${userName},\n\nWelcome to our platform!\n\nBest regards`;
        this.sendEmail(toAddress, subject, body);
    }

    sendPasswordResetEmail(toAddress: string, resetToken: string): void {
        const subject = 'Password Reset Request';
        const body = `Click this link to reset your password: http://example.com/reset?token=${resetToken}`;
        this.sendEmail(toAddress, subject, body);
    }

    private sendEmail(toAddress: string, subject: string, body: string): void {
        try {
            console.log(`Email sent to ${toAddress}`);
            console.log(`Subject: ${subject}`);
            console.log(`Body: ${body}`);
        } catch (error) {
            console.error(`Failed to send email: ${error}`);
        }
    }
}

// 核心服务：协调各个单一职责的类
class UserRegistrationService {
    constructor(
        private repository: UserRepository,
        private emailValidator: typeof EmailValidator,
        private passwordValidator: typeof PasswordValidator,
        private passwordEncryptor: typeof PasswordEncryptor,
        private emailService: EmailNotificationService
    ) {}

    registerUser(name: string, email: string, password: string): User {
        // 第1步：验证邮箱
        this.emailValidator.validate(email);

        // 第2步：检查邮箱是否已注册
        if (this.repository.findByEmail(email)) {
            throw new ValidationException(`Email already registered: ${email}`);
        }

        // 第3步：验证密码强度
        this.passwordValidator.validate(password);

        // 第4步：创建用户
        const user = new User(this.generateId(), name, email);

        // 第5步：保存用户
        this.repository.save(user);

        // 第6步：发送欢迎邮件
        try {
            this.emailService.sendWelcomeEmail(email, name);
        } catch (error) {
            console.error(`Welcome email failed, but user registered: ${error}`);
        }

        return user;
    }

    resetPassword(email: string, newPassword: string): void {
        // 验证邮箱存在
        const user = this.repository.findByEmail(email);
        if (!user) {
            throw new ValidationException(`User not found: ${email}`);
        }

        // 验证新密码强度
        this.passwordValidator.validate(newPassword);

        // 发送密码重置邮件
        this.emailService.sendPasswordResetEmail(email, 'reset-token-123');
    }

    deleteUser(userId: string): void {
        const user = this.repository.findById(userId);
        if (!user) {
            throw new ValidationException(`User not found: ${userId}`);
        }
        this.repository.delete(userId);
    }

    private generateId(): string {
        return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}

// 使用示例
const repository = new UserRepository();
const emailService = new EmailNotificationService();

const service = new UserRegistrationService(
    repository,
    EmailValidator,
    PasswordValidator,
    PasswordEncryptor,
    emailService
);

// 注册用户
try {
    const user = service.registerUser('John Doe', 'john@example.com', 'StrongPass123');
    console.log(`\nUser registered successfully: ${user}`);
} catch (error) {
    if (error instanceof ValidationException) {
        console.error(`Registration failed: ${error.message}`);
    }
}
```

---

## 单元测试示例

### Java JUnit 测试

```java
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class UserRegistrationServiceTest {
    private UserRepository repository;
    private EmailValidator emailValidator;
    private PasswordValidator passwordValidator;
    private PasswordEncryptor passwordEncryptor;
    private EmailNotificationService emailService;
    private UserRegistrationService service;

    @BeforeEach
    void setUp() {
        repository = new UserRepository(null);
        emailValidator = new EmailValidator();
        passwordValidator = new PasswordValidator();
        passwordEncryptor = new PasswordEncryptor();
        emailService = mock(EmailNotificationService.class);

        service = new UserRegistrationService(
            repository, emailValidator, passwordValidator,
            passwordEncryptor, emailService
        );
    }

    @Test
    void testRegisterUserSuccess() throws ValidationException {
        User user = service.registerUser("John Doe", "john@example.com", "StrongPass123");

        assertEquals("john@example.com", user.getEmail());
        assertEquals("John Doe", user.getName());
        assertNotNull(user.getId());

        verify(emailService).sendWelcomeEmail("john@example.com", "John Doe");
    }

    @Test
    void testRegisterUserWithInvalidEmail() {
        assertThrows(ValidationException.class, () ->
            service.registerUser("John", "invalid-email", "StrongPass123")
        );

        verify(emailService, never()).sendWelcomeEmail(anyString(), anyString());
    }

    @Test
    void testRegisterUserWithWeakPassword() {
        assertThrows(ValidationException.class, () ->
            service.registerUser("John", "john@example.com", "weak")
        );
    }

    @Test
    void testRegisterDuplicateEmail() throws ValidationException {
        service.registerUser("John", "john@example.com", "StrongPass123");

        assertThrows(ValidationException.class, () ->
            service.registerUser("Jane", "john@example.com", "StrongPass123")
        );
    }
}

class EmailValidatorTest {
    @Test
    void testValidEmail() {
        assertTrue(EmailValidator.isValid("john@example.com"));
        assertTrue(EmailValidator.isValid("user+tag@domain.co.uk"));
    }

    @Test
    void testInvalidEmail() {
        assertFalse(EmailValidator.isValid("invalid-email"));
        assertFalse(EmailValidator.isValid("@example.com"));
        assertFalse(EmailValidator.isValid(null));
    }

    @Test
    void testValidateThrowsException() {
        assertThrows(ValidationException.class, () ->
            EmailValidator.validate("invalid-email")
        );
    }
}

class PasswordValidatorTest {
    @Test
    void testStrongPassword() {
        assertTrue(PasswordValidator.isStrong("StrongPass123"));
        PasswordValidator.validate("SecurePassword456");  // Should not throw
    }

    @Test
    void testWeakPassword() {
        assertFalse(PasswordValidator.isStrong("weak"));
        assertFalse(PasswordValidator.isStrong("short1"));
        assertFalse(PasswordValidator.isStrong("ONLYUPPERCASE123"));
    }

    @Test
    void testValidateThrowsException() {
        assertThrows(ValidationException.class, () ->
            PasswordValidator.validate("short")
        );
    }
}
```

### Python pytest 测试

```python
import pytest
from unittest.mock import MagicMock, patch

class TestUserRegistrationService:
    @pytest.fixture
    def setup(self):
        repository = UserRepository()
        email_validator = EmailValidator()
        password_validator = PasswordValidator()
        password_encryptor = PasswordEncryptor()
        email_service = MagicMock(spec=EmailNotificationService)

        service = UserRegistrationService(
            repository, email_validator, password_validator,
            password_encryptor, email_service
        )
        return service, repository, email_service

    def test_register_user_success(self, setup):
        service, repository, email_service = setup

        user = service.register_user("John Doe", "john@example.com", "StrongPass123")

        assert user.email == "john@example.com"
        assert user.name == "John Doe"
        email_service.send_welcome_email.assert_called_once_with("john@example.com", "John Doe")

    def test_register_user_invalid_email(self, setup):
        service, repository, email_service = setup

        with pytest.raises(ValidationException):
            service.register_user("John", "invalid-email", "StrongPass123")

        email_service.send_welcome_email.assert_not_called()

    def test_register_user_weak_password(self, setup):
        service, repository, email_service = setup

        with pytest.raises(ValidationException):
            service.register_user("John", "john@example.com", "weak")

class TestEmailValidator:
    def test_valid_email(self):
        assert EmailValidator.is_valid("john@example.com")
        assert EmailValidator.is_valid("user+tag@domain.co.uk")

    def test_invalid_email(self):
        assert not EmailValidator.is_valid("invalid-email")
        assert not EmailValidator.is_valid("@example.com")
        assert not EmailValidator.is_valid(None)

class TestPasswordValidator:
    def test_strong_password(self):
        assert PasswordValidator.is_strong("StrongPass123")
        PasswordValidator.validate("SecurePassword456")

    def test_weak_password(self):
        assert not PasswordValidator.is_strong("weak")
        assert not PasswordValidator.is_strong("short1")
```

---

## 总结

**核心要点**：

1. **识别职责** - 用"改变理由"来识别职责
2. **拆分职责** - 一个类一个职责
3. **聚合调用** - 用 Service 或 Facade 协调多个类
4. **依赖注入** - 降低类之间的耦合
5. **易于测试** - 每个类都可以独立测试

**效果指标**：

| 指标 | 拆分前 | 拆分后 |
|------|--------|--------|
| 类数 | 1 | 6 |
| 平均方法数 | 12 | 3 |
| 代码行数 | 300 | 1500（但分散） |
| 测试 mock 数 | 5 | 1-2 |
| 测试难度 | 高 | 低 |
| 复用度 | 低 | 高 |

单一职责原则虽然会增加代码文件数量，但大幅提高了代码的可维护性、可测试性和复用性，是长期项目维护的关键。
