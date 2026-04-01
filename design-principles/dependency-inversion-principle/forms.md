# 依赖倒置原则 - 诊断与规划表

## 第1步: 需求诊断 - 你的代码是否存在依赖混乱？

### 🔍 快速检查清单

```
□ 无法单独测试业务逻辑，因为依赖太多具体类
□ 修改数据库实现，导致业务层代码也要改
□ 到处是 new 关键字创建对象
□ 业务层直接依赖低层实现类（如Repository、数据库驱动）
□ 无法替换某个实现（想换ORM框架？困难！）
□ 代码中有反向依赖（低层依赖高层）
□ 循环依赖的警告或错误
□ 测试代码比生产代码还多，全是mock
```

**诊断标准**:
- ✅ 0-1 项 → **很好，依赖关系清晰**
- ⚠️ 2-4 项 → **应该考虑重构**
- ❌ 5 项以上 → **必须立即重构，依赖关系混乱**

### 🎯 具体场景评估

| 场景 | 现象 | 原因 | 建议 | 优先级 |
|------|------|------|------|--------|
| 无法测试业务逻辑 | 测试需要启动数据库 | 业务层直接依赖Repository | 注入依赖 | ⭐⭐⭐⭐⭐ |
| 修改ORM困难 | 从Hibernate换JPA，到处改代码 | 到处是具体类依赖 | 定义接口 | ⭐⭐⭐⭐ |
| 无法添加新功能 | 新功能需要修改现有类 | 依赖具体实现 | 使用接口 | ⭐⭐⭐⭐ |
| 代码耦合度高 | 一个改动影响多个模块 | 高层依赖低层 | DI容器管理 | ⭐⭐⭐⭐ |

---

## 第2步: 依赖关系分析

### 识别你的依赖

```
分析当前代码：UserService

当前实现:
public class UserService {
    private UserRepository repository = new JpaUserRepository();  // 直接依赖
    private EmailService emailService = new SmtpEmailService();   // 直接依赖
    private PasswordValidator validator = new Bcrypt Validator(); // 直接依赖
}

依赖分析：
1. 依赖的具体类：JpaUserRepository, SmtpEmailService, BcryptValidator
2. 如果要改成MongoDB： repository = new MongoUserRepository()  -> 需要改UserService代码
3. 如果要改成其他邮件服务：emailService = new ...  -> 需要改UserService代码
4. 测试时无法mock这些依赖  -> 测试困难

问题：UserService（高层）依赖JpaUserRepository（低层具体实现）
```

### 清单

```
分析当前类: ___________________________

直接创建或依赖的具体类（用new创建的）：
1. __________________ (类型：___ , 作用：___)
2. __________________ (类型：___ , 作用：___)
3. __________________ (类型：___ , 作用：___)
4. __________________ (类型：___ , 作用：___)

总计 ____ 个具体类依赖

这些依赖能否被替换？
□ JpaUserRepository 能换成 MongoUserRepository？ YES / NO
□ SmtpEmailService 能换成其他邮件服务？ YES / NO
□ 能否在单元测试时mock这些依赖？ YES / NO

□ 如果任何一项是 NO，说明存在依赖问题
```

### 绘制依赖图

```
当前依赖关系（错误）：

UserService (高层)
    ├─> JpaUserRepository (具体实现，低层)  ❌ 错误方向
    ├─> SmtpEmailService (具体实现，低层)   ❌ 错误方向
    └─> BcryptValidator (具体实现，低层)    ❌ 错误方向

这是"正常"的依赖，但违反DIP


应该改为（遵循DIP）：

UserService (高层)
    ├─> UserRepository (接口)    ✅
    ├─> EmailService (接口)      ✅
    └─> PasswordValidator (接口) ✅
         ↑        ↑         ↑
         |        |         |
         └────────┴─────────┘
    由DI容器实现和注入
```

---

## 第3步: 设计抽象接口

### 为每个依赖定义接口

```
当前具体类 ──→ 对应接口

JpaUserRepository  ──→  UserRepository (接口)
SmtpEmailService   ──→  EmailService (接口)
BcryptValidator    ──→  PasswordValidator (接口)

关键原则：
- 接口定义在HIGH层（UserService所在）
- 实现位于LOW层（Repository、Service等）
- 两者都依赖中间的接口
```

### 清单

```
识别需要抽象的依赖：

依赖1：数据访问
  当前具体类：JpaUserRepository
  定义接口：interface UserRepository {
    void save(User user);
    Optional<User> findByEmail(String email);
    void delete(String id);
  }

依赖2：邮件服务
  当前具体类：SmtpEmailService
  定义接口：interface EmailService {
    void sendWelcomeEmail(String email);
    void sendResetEmail(String email);
  }

依赖3：密码验证
  当前具体类：BcryptValidator
  定义接口：interface PasswordValidator {
    void validate(String password) throws ValidationException;
  }
```

---

## 第4步: 改造为依赖注入

### 方式1：构造注入（推荐）

```
前：
public class UserService {
    private UserRepository repository = new JpaUserRepository();
}

后：
public class UserService {
    private final UserRepository repository;

    // 构造注入
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}

优点：
□ 依赖清晰可见
□ 不可变（final）
□ 易于测试
□ 强制注入依赖
```

### 方式2：属性注入（Spring）

```
@Service
public class UserService {
    @Autowired
    private UserRepository repository;
}

优点：
□ 代码简洁
□ Spring自动管理

缺点：
□ 依赖不明显
□ 可能为null
```

### 方式3：Setter注入

```
public class UserService {
    private UserRepository repository;

    public void setRepository(UserRepository repository) {
        this.repository = repository;
    }
}

优点：
□ 可选依赖
□ 灵活

缺点：
□ 对象可能不完整
□ 线程不安全
```

### 推荐：构造注入

```
public class UserService {
    private final UserRepository repository;
    private final EmailService emailService;
    private final PasswordValidator validator;

    // 所有依赖通过构造函数注入
    public UserService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator validator) {
        this.repository = repository;
        this.emailService = emailService;
        this.validator = validator;
    }
}
```

---

## 第5步: 配置DI容器

### Spring配置示例

```
@Configuration
public class ApplicationConfig {
    @Bean
    public UserRepository userRepository() {
        return new JpaUserRepository();
        // 想改成MongoDB？改这里就行：return new MongoUserRepository();
    }

    @Bean
    public EmailService emailService() {
        return new SmtpEmailService();
    }

    @Bean
    public PasswordValidator passwordValidator() {
        return new StandardPasswordValidator();
    }

    @Bean
    public UserService userService(
            UserRepository repository,
            EmailService emailService,
            PasswordValidator validator) {
        return new UserService(repository, emailService, validator);
    }
}

优点：
□ 所有依赖配置在一处
□ 改变实现只需改配置
□ 业务代码完全不受影响
```

---

## 第6步: 测试

### 单元测试（使用mock）

```
@Test
public void testUserRegistration() {
    // Mock依赖（容易！因为依赖的是接口）
    UserRepository mockRepo = mock(UserRepository.class);
    EmailService mockEmail = mock(EmailService.class);
    PasswordValidator mockValidator = mock(PasswordValidator.class);

    // 注入mock
    UserService service = new UserService(mockRepo, mockEmail, mockValidator);

    // 执行测试
    service.registerUser("john@example.com", "StrongPass123");

    // 验证调用
    verify(mockRepo).save(any(User.class));
    verify(mockEmail).sendWelcomeEmail("john@example.com");
}

优点：
□ 快速（无需启动数据库）
□ 隔离（只测试业务逻辑）
□ 可重复（结果稳定）
```

### 集成测试（使用真实实现）

```
@SpringBootTest
public class UserServiceIntegrationTest {
    @Autowired
    private UserService userService;

    @Test
    public void testFullFlow() {
        // 使用真实的Repository、EmailService等
        userService.registerUser("jane@example.com", "StrongPass456");
        // 验证数据库中真的保存了用户
    }
}
```

---

## 常见陷阱预防

### 陷阱1: 使用静态工厂方法逃避DIP

```
❌ 仍然违反DIP：
public class UserService {
    private UserRepository repository = UserRepositoryFactory.create();
}

✅ 遵循DIP：
public class UserService {
    private UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

### 陷阱2: 过度注入

```
❌ 注入过多：
public UserService(
    UserRepository r1,
    EmailService e1,
    PasswordValidator v1,
    AuditService a1,
    NotificationService n1,
    Logger logger,
    Config config,
    MetricsCollector metrics
) // 太多了！

✅ 合理注入：
public UserService(
    UserRepository repository,
    EmailService emailService,
    PasswordValidator validator
)  // 只注入直接需要的
```

**预防**：
```
□ 一个类注入 > 5 个依赖，说明职责太多（违反SRP）
□ 应该拆分成多个类，每个类职责单一
```

### 陷阱3: 循环依赖

```
❌ 循环依赖：
UserService → OrderService → UserService  // 循环！

✅ 消除循环：
1. 提取共用接口
2. 定义清晰的分层
3. 使用Lazy初始化
```

### 陷阱4: 忘记实际配置

```
❌ 定义了接口，但没有配置DI：
public class UserService {
    private UserRepository repository;  // null指针异常！
}

✅ 完整的配置：
@Configuration
public class Config {
    @Bean
    public UserRepository userRepository() {
        return new JpaUserRepository();
    }

    @Bean
    public UserService userService(UserRepository repository) {
        return new UserService(repository);
    }
}
```

---

## 迁移清单

从当前代码迁移到遵循DIP的代码：

```
□ 第1步：为每个具体依赖定义接口
  □ UserRepository接口
  □ EmailService接口
  □ PasswordValidator接口

□ 第2步：修改UserService使用接口
  □ 声明字段为接口类型
  □ 添加构造注入
  □ 所有调用使用接口方法

□ 第3步：具体实现维持不变
  □ JpaUserRepository extends ... implements UserRepository
  □ SmtpEmailService extends ... implements EmailService

□ 第4步：配置DI容器
  □ 定义Bean（UserRepository、EmailService等）
  □ 定义UserService的Bean，注入依赖

□ 第5步：逐步迁移调用代码
  □ 用 UserService userService = context.getBean(UserService.class);
  □ 替换直接new的代码

□ 第6步：更新单元测试
  □ 使用mock接口
  □ 验证方法调用

□ 第7步：删除旧代码
  □ 确认所有调用都已迁移
  □ 删除直接new的代码

总时间：3-5 天
```

---

## 效果评估

| 指标 | 改造前 | 改造后 | 改善 |
|------|--------|--------|------|
| 单元测试覆盖率 | 20% | 85% | ✅ |
| 修改ORM时代码改动 | 30+ 行 | 1 行（Bean配置） | ✅ |
| 测试速度 | 慢（需要启动DB） | 快（纯mock） | ✅ |
| 代码耦合度 | 高 | 低 | ✅ |
| 能否切换实现 | 困难 | 容易 | ✅ |

---

## 重构检查表

```
设计检查：
□ 所有外部依赖都有接口
□ 无直接依赖具体类（除了配置类）
□ 无反向依赖（低层不依赖高层）
□ 无循环依赖

代码检查：
□ 业务类中无 new 关键字（除了创建值对象）
□ 所有依赖通过构造或Set注入
□ 依赖声明为接口类型，不是具体类

测试检查：
□ 单元测试可独立运行，无需启动容器
□ 所有依赖都可以mock
□ 测试覆盖率 ≥ 80%

配置检查：
□ DI配置完整，所有Bean都能创建
□ 无缺失的依赖
□ 应用启动无错误
```

DIP是构建可维护、可测试系统的基础。
