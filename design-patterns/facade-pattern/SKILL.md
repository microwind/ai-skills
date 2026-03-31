---
name: Facade
description: "为复杂的系统提供统一的、简化的接口"
license: MIT
---

# Facade Pattern (外观模式)

## 核心概念

**Facade** 是一种**结构型设计模式**，为复杂的子系统提供简化的、统一的接口。

### 核心作用
- 🎭 **隐藏复杂性** - 客户端只见简单接口
- 📦 **封装子系统** - 内部具体如何实现客户端不关心
- 🔪 **物理分离** - 客户端与内部实现解耦
- 🎯 **简化使用** - 降低学习成本

## 何时使用

1. **复杂子系统需要简化** - 多个类协作变成一个接口
2. **客户端与子系统解耦** - 内部改动不影响客户端
3. **按层分离关切** - 如MVC中的Controller作为Facade
4. **第三方库包装** - 统一API、处理版本差异
5. **渐进式重构** - 旧系统前面加Facade

## 实现方式

### 方法1: 单一Facade

```java
// 复杂子系统的各个类
public class AuthService { /* 认证逻辑 */ }
public class Database { /* 数据库访问 */ }
public class EmailService { /* 邮件发送 */ }

// Facade - 简化接口
public class UserRegistrationFacade {
    private AuthService auth;
    private Database db;
    private EmailService email;
    
    public UserRegistrationFacade() {
        this.auth = new AuthService();
        this.db = new Database();
        this.email = new EmailService();
    }
    
    // 统一接口
    public void register(String username, String pwd, String mail) {
        // 内部协调3个服务
        auth.validatePassword(pwd);
        db.insertUser(username, pwd);
        email.send(mail, "Welcome!");
    }
}

// 使用
UserRegistrationFacade facade = new UserRegistrationFacade();
facade.register("user", "pwd123", "user@mail.com");
```

### 方法2: 多层Facade

```java
// 顶层Facade
public class ApplicationFacade {
    private AuthenticationFacade authFacade;
    private DataProcessingFacade dataFacade;
    
    public void processUserData(String userId) {
        authFacade.authenticate(userId);
        dataFacade.process(userId);
    }
}

// 中层Facade
public class AuthenticationFacade {
    // 管理多个认证相关的类
}

public class DataProcessingFacade {
    // 管理多个数据处理的类
}
```

### 方法3: 外观工厂

```java
public class FacadeFactory {
    private static Map<String, Facade> facades = new HashMap<>();
    
    static {
        facades.put("auth", new AuthenticationFacade());
        facades.put("data", new DataProcessingFacade());
    }
    
    public static Facade getFacade(String name) {
        return facades.get(name);
    }
}

// 使用
Facade auth = FacadeFactory.getFacade("auth");
```

### 方法4: 动态Facade

```java
public class DynamicFacade {
    private Map<String, Operation> operations = new HashMap<>();
    
    public void register(String operationName, Operation op) {
        operations.put(operationName, op);
    }
    
    public void execute(String operationName, Object... args) {
        Operation op = operations.get(operationName);
        if (op != null) {
            op.execute(args);
        }
    }
}
```

## 使用场景

## 设计原则与最佳实践

### 核心设计原则

**原则1: 最小暴露**
```java
// ❌ 过度暴露
public class OrderFacade {
    public OrderService orderService;      // 不应该暴露
    public PaymentService paymentService;
    public ShippingService shippingService;
}

// ✅ 最小暴露
public class OrderFacade {
    private OrderService orderService;
    private PaymentService paymentService;
    private ShippingService shippingService;
    
    public OrderResult placeOrder(Order order) {
        // 只暴露必要的public方法
    }
}
```

**原则2: 单一职责**
```java
// ❌ 职责混乱
public class SuperFacade {
    // 包含了所有系统的所有操作！
    public void registerUser() { }
    public void processPayment() { }
    public void sendEmail() { }
    public void generateReport() { }
    public void backupDatabase() { }
}

// ✅ 职责清晰
public class UserRegistrationFacade { }     // 只管注册
public class PaymentFacade { }              // 只管支付
public class NotificationFacade { }         // 只管通知
```

**原则3: 易用性优先**
```java
// ❌ 使用复杂
List<Step> steps = new ArrayList<>();
steps.add(authService.validate(creds));
steps.add(dbService.loadUser(userId));
steps.add(emailService.prepare(template));
// 还要客户端合并结果...

// ✅ 易用性好
UserProfile profile = userFacade.registerUser(email, password);
// 一行代码完成复杂流程
```

---

## 4种深度实现方法

### 方法1: 简单Facade（单一服务聚合）

```java
// 复杂子系统
public class CryptoService {
    public String encrypt(String data) { }
    public String decrypt(String data) { }
}

public class ValidationService {
    public boolean isValidEmail(String email) { }
    public boolean isStrongPassword(String pwd) { }
}

public class PersistenceService {
    public void saveUser(User user) { }
    public User loadUser(String id) { }
}

// Facade - 简化接口
public class UserManagementFacade {
    private CryptoService crypto;
    private ValidationService validation;
    private PersistenceService persistence;
    
    public UserManagementFacade() {
        this.crypto = new CryptoService();
        this.validation = new ValidationService();
        this.persistence = new PersistenceService();
    }
    
    // 简化的用户注册流程
    public boolean registerUser(String email, String password) {
        // 1. 验证
        if (!validation.isValidEmail(email)) {
            return false;
        }
        if (!validation.isStrongPassword(password)) {
            return false;
        }
        
        // 2. 加密
        String encryptedPwd = crypto.encrypt(password);
        
        // 3. 保存
        User user = new User(email, encryptedPwd);
        persistence.saveUser(user);
        
        return true;
    }
    
    // 简化的用户登录流程
    public User login(String email, String password) throws Exception {
        User user = persistence.loadUser(email);
        if (user == null) {
            throw new AuthException("用户不存在");
        }
        
        String encryptedInput = crypto.encrypt(password);
        if (!encryptedInput.equals(user.getPassword())) {
            throw new AuthException("密码错误");
        }
        
        return user;
    }
}

// 使用
UserManagementFacade facade = new UserManagementFacade();
if (facade.registerUser("user@example.com", "P@ssw0rd!")) {
    System.out.println("注册成功");
}
```

### 方法2: 分层Facade（PipeLine风格）

```java
// 第1层：基础Facade（处理单个域）
public class AuthenticationFacade {
    private CredentialValidator validator;
    private CryptoService crypto;
    private AuditLog log;
    
    public AuthToken authenticate(String username, String password) {
        validator.validate(username, password);
        
        User user = findUser(username);
        if (!crypto.verify(password, user.hashedPassword)) {
            throw new AuthException("认证失败");
        }
        
        log.record("认证成功: " + username);
        return new AuthToken(user);
    }
}

// 第2层：中层Facade（协调多个基础Facade）
public class OrderProcessingFacade {
    private AuthenticationFacade authFacade;
    private PaymentFacade paymentFacade;
    private InventoryFacade inventoryFacade;
    private ShippingFacade shippingFacade;
    
    public OrderResult placeOrder(AuthToken token, OrderRequest req) {
        // 1. 认证
        authFacade.validate(token);
        
        // 2. 检查库存
        InventoryCheck check = inventoryFacade.checkAvailability(req.items);
        if (!check.available) {
            throw new OutOfStockException();
        }
        
        // 3. 处理支付
        Payment payment = paymentFacade.processPayment(
            req.paymentInfo, 
            req.amount
        );
        
        // 4. 生成订单
        Order order = createOrder(req, payment);
        
        // 5. 安排发货
        shippingFacade.scheduleShipment(order);
        
        // 6. 返回结果
        return new OrderResult(order, payment);
    }
}

// 第3层：应用Facade（暴露给外部API）
public class ApplicationFacade {
    private AuthenticationFacade authFacade;
    private OrderProcessingFacade orderFacade;
    
    public OrderResponse handleOrderAPI(OrderRequest req) {
        try {
            AuthToken token = authFacade.authenticate(
                req.username, 
                req.password
            );
            OrderResult result = orderFacade.placeOrder(token, req);
            return new OrderResponse(result);
        } catch (Exception e) {
            return new OrderResponse(e);
        }
    }
}
```

### 方法3: 策略Facade（模式选择）

```java
// 策略接口
public interface OrderStrategy {
    OrderResult process(OrderRequest req);
}

// 不同策略实现
public class StandardOrderStrategy implements OrderStrategy {
    public OrderResult process(OrderRequest req) {
        // 标准流程
        return standardProcess(req);
    }
}

public class ExpressOrderStrategy implements OrderStrategy {
    public OrderResult process(OrderRequest req) {
        // 快速流程：跳过某些检查
        return expressProcess(req);
    }
}

public class B2BOrderStrategy implements OrderStrategy {
    public OrderResult process(OrderRequest req) {
        // B2B流程：特殊审批
        return b2bProcess(req);
    }
}

// Facade选择合适策略
public class AdaptiveOrderFacade {
    private Map<String, OrderStrategy> strategies = new HashMap<>();
    
    public AdaptiveOrderFacade() {
        strategies.put("standard", new StandardOrderStrategy());
        strategies.put("express", new ExpressOrderStrategy());
        strategies.put("b2b", new B2BOrderStrategy());
    }
    
    public OrderResult placeOrder(OrderRequest req) {
        // 根据订单类型选择策略
        String strategyType = determineStrategy(req);
        OrderStrategy strategy = strategies.get(strategyType);
        
        return strategy.process(req);
    }
    
    private String determineStrategy(OrderRequest req) {
        if (req.isB2B()) return "b2b";
        if (req.isExpress()) return "express";
        return "standard";
    }
}
```

### 方法4: 链式Facade（Fluent API风格）

```java
public class FluentOrderFacade {
    private Order order;
    private PaymentResult paymentResult;
    
    public FluentOrderFacade createOrder(OrderRequest req) {
        this.order = new Order(req);
        return this;
    }
    
    public FluentOrderFacade validateOrder() {
        if (!order.isValid()) {
            throw new ValidationException("订单无效");
        }
        return this;
    }
    
    public FluentOrderFacade processPayment(PaymentInfo info) {
        PaymentFacade paymentFacade = new PaymentFacade();
        this.paymentResult = paymentFacade.process(order, info);
        return this;
    }
    
    public FluentOrderFacade checkInventory() {
        InventoryFacade inventoryFacade = new InventoryFacade();
        inventoryFacade.reserve(order.getItems());
        return this;
    }
    
    public FluentOrderFacade scheduleShipment() {
        ShippingFacade shippingFacade = new ShippingFacade();
        shippingFacade.schedule(order);
        return this;
    }
    
    public OrderResult complete() {
        return new OrderResult(order, paymentResult);
    }
}

// 使用 - 链式调用
OrderResult result = new FluentOrderFacade()
    .createOrder(req)
    .validateOrder()
    .processPayment(paymentInfo)
    .checkInventory()
    .scheduleShipment()
    .complete();
```

---

## 使用场景详解

### 场景1: MVC框架中的Controller

```java
// Model - 数据模型
public class User {
    private String username;
    private String email;
    private Role role;
}

// Service层 - 复杂业务逻辑
public class UserService {
    public boolean validateUsername(String username) { }
    public User findByEmail(String email) { }
    public void saveUser(User user) { }
    public void sendWelcomeEmail(User user) { }
}

public class AuthenticationService {
    public AuthToken login(String username, String password) { }
    public void logout(AuthToken token) { }
}

// Controller - Facade角色
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;
    @Autowired
    private AuthenticationService authService;
    
    // Facade方法1：注册
    @PostMapping("/register")
    public ResponseEntity<User> register(@RequestBody RegisterRequest req) {
        try {
            // 验证
            userService.validateUsername(req.getUsername());
            
            // 创建用户
            User user = new User(req.getUsername(), req.getEmail());
            userService.saveUser(user);
            
            // 发送欢迎邮件
            userService.sendWelcomeEmail(user);
            
            return ResponseEntity.ok(user);
        } catch (Exception e) {
            return ResponseEntity.status(400).build();
        }
    }
    
    // Facade方法2：登录
    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest req) {
        try {
            AuthToken token = authService.login(
                req.getUsername(), 
                req.getPassword()
            );
            return ResponseEntity.ok(new LoginResponse(token));
        } catch (Exception e) {
            return ResponseEntity.status(401).build();
        }
    }
}
```

### 场景2: ORM框架（Hibernate）

```java
// 复杂的ORM底层操作
public class SessionFactory {
    public Session openSession() { }
}

public class Session {
    public void beginTransaction() { }
    public void save(Object entity) { }
    public void flush() { }
}

public class Transaction {
    public void commit() { }
    public void rollback() { }
}

// Facade - Repository模式
public interface UserRepository {
    void save(User user);
    User findById(Long id);
    List<User> findAll();
    void delete(User user);
}

@Repository
public class HibernateUserRepository implements UserRepository {
    
    @PersistenceContext
    private EntityManager em;  // Spring管理的Session
    
    @Override
    @Transactional
    public void save(User user) {
        // Facade隐藏了复杂的Transaction、flush操作
        em.persist(user);
    }
    
    @Override
    public User findById(Long id) {
        // 隐藏Query、ResultSet等复杂操作
        return em.find(User.class, id);
    }
    
    @Override
    public List<User> findAll() {
        // 隐藏JPQL、Criteria等查询复杂性
        Query query = em.createQuery("FROM User");
        return query.getResultList();
    }
    
    @Override
    @Transactional
    public void delete(User user) {
        em.remove(em.merge(user));
    }
}

// 使用 - 客户端无需知道Session、Transaction细节
UserRepository repo = applicationContext.getBean(UserRepository.class);
User user = new User("John", "john@example.com");
repo.save(user);  // 一行代码，Facade隐藏了事务管理
```

### 场景3: 第三方库包装

```java
// 复杂的第三方支付库API
import com.alipay.api.*;
import com.alipay.api.request.*;
import com.alipay.api.response.*;
import com.wechat.pay.api.*;

// Facade - 统一支付接口
public class UnifiedPaymentFacade {
    private AlipayClient alipayClient;
    private WechatPayClient wechatClient;
    
    public PaymentResult pay(PaymentRequest req) {
        PaymentMethod method = req.getPaymentMethod();
        
        switch (method) {
            case ALIPAY:
                return processAlipay(req);
            case WECHAT:
                return processWechat(req);
            case CARD:
                return processCard(req);
            default:
                throw new UnsupportedPaymentMethod();
        }
    }
    
    private PaymentResult processAlipay(PaymentRequest req) {
        try {
            // 包装复杂的Alipay API
            AlipayTradePagePayRequest request = new AlipayTradePagePayRequest();
            request.setReturnUrl(req.getReturnUrl());
            request.setNotifyUrl(req.getNotifyUrl());
            
            // 构建业务参数
            AlipayTradePagePayModel model = new AlipayTradePagePayModel();
            model.setOutTradeNo(req.getOrderId());
            model.setTotalAmount(req.getAmount().toString());
            model.setSubject(req.getProductName());
            request.setBizModel(model);
            
            // 执行支付
            AlipayTradePagePayResponse response = 
                alipayClient.pageExecute(request);
            
            // 转换为通用结果
            return new PaymentResult(
                response.isSuccess() ? "SUCCESS" : "FAILED",
                response.getTradeNo()
            );
        } catch (Exception e) {
            throw new AlipayException(e);
        }
    }
    
    private PaymentResult processWechat(PaymentRequest req) {
        // 类似的Wechat支付逻辑...
    }
    
    private PaymentResult processCard(PaymentRequest req) {
        // 银行卡支付逻辑...
    }
}

// 使用 - 统一的支付接口
PaymentFacade facade = new PaymentFacade();
PaymentRequest req = new PaymentRequest()
    .setOrderId("12345")
    .setAmount(new BigDecimal("99.99"))
    .setPaymentMethod(PaymentMethod.ALIPAY);

PaymentResult result = facade.pay(req);
if (result.isSuccessful()) {
    System.out.println("支付成功: " + result.getTransactionId());
}
```

### 场景4: 数据库连接管理

```java
// 复杂的数据源管理
public class DataSourceManager {
    private Map<String, DataSource> dataSources = new HashMap<>();
    private ConnectionPool connectionPool;
    
    public Connection getConnection(String dbName) { }
    public void releaseConnection(Connection conn) { }
    public void closePool() { }
}

// Facade - 简化数据库操作
public class DatabaseAccessFacade {
    private DataSourceManager dsManager;
    private TransactionManager transactionManager;
    private QueryBuilder queryBuilder;
    
    public List<Map<String, Object>> query(String sql, Object... params) {
        Connection conn = null;
        try {
            conn = dsManager.getConnection("default");
            
            PreparedStatement stmt = conn.prepareStatement(sql);
            for (int i = 0; i < params.length; i++) {
                stmt.setObject(i + 1, params[i]);
            }
            
            ResultSet rs = stmt.executeQuery();
            List<Map<String, Object>> results = new ArrayList<>();
            
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                for (int i = 1; i <= rs.getMetaData().getColumnCount(); i++) {
                    row.put(
                        rs.getMetaData().getColumnName(i),
                        rs.getObject(i)
                    );
                }
                results.add(row);
            }
            
            return results;
        } finally {
            if (conn != null) {
                dsManager.releaseConnection(conn);
            }
        }
    }
    
    public int update(String sql, Object... params) {
        Connection conn = null;
        try {
            conn = dsManager.getConnection("default");
            transactionManager.begin();
            
            PreparedStatement stmt = conn.prepareStatement(sql);
            for (int i = 0; i < params.length; i++) {
                stmt.setObject(i + 1, params[i]);
            }
            
            int affected = stmt.executeUpdate();
            transactionManager.commit();
            
            return affected;
        } catch (Exception e) {
            transactionManager.rollback();
            throw new DatabaseException(e);
        } finally {
            if (conn != null) {
                dsManager.releaseConnection(conn);
            }
        }
    }
}

// 使用
DatabaseAccessFacade facade = new DatabaseAccessFacade();
List<Map<String, Object>> results = facade.query(
    "SELECT * FROM users WHERE age > ?",
    18
);
```

### 场景5: 文件处理系统

```java
// 复杂的文件处理库
public class PDFProcessor { }
public class ImageProcessor { }
public class DocumentProcessor { }
public class ZipProcessor { }
public class FileValidator { }
public class FileEncryption { }

// Facade - 统一文件处理
public class FileProcessingFacade {
    private PDFProcessor pdfProcessor;
    private ImageProcessor imageProcessor;
    private FileEncryption encryption;
    private FileValidator validator;
    
    public ProcessResult processFile(File file, ProcessOptions options) {
        // 1. 验证
        if (!validator.isValid(file)) {
            throw new InvalidFileException();
        }
        
        // 2. 确定类型
        FileType type = determineType(file);
        
        // 3. 处理
        Object processed = null;
        switch (type) {
            case PDF:
                processed = pdfProcessor.process(file);
                break;
            case IMAGE:
                processed = imageProcessor.process(file);
                break;
            default:
                processed = documentProcessor.process(file);
        }
        
        // 4. 加密（如果需要）
        if (options.shouldEncrypt()) {
            processed = encryption.encrypt(processed);
        }
        
        return new ProcessResult(processed);
    }
}
```

---

## 4个常见问题与深度解决

### 问题1: Facade vs Adapter的区别？

**症状**: 混淆Facade和Adapter的使用场景

**对比分析:**

| 特性 | Facade | Adapter |
|------|--------|---------|
| **目的** | 简化复杂系统 | 适配不兼容接口 |
| **场景** | 复杂系统 → 客户端 | 不兼容的类 ↔ 中间件 |
| **设计时机** | 系统设计阶段 | 集成遗留系统时 |
| **介入点** | 整个子系统前面 | 两个具体类之间 |

**决策流程:**
```
需要简化使用复杂系统? → Facade
需要适配不兼容的接口? → Adapter
```

**示例对比:**
```java
// Facade: 简化Library API
public class LibraryFacade {
    private BookService bookService;
    private LoanService loanService;
    
    public Book borrowBook(String title) {
        // 简化借书流程
    }
}

// Adapter: 适配旧Logger到新Logger
public class OldLoggerAdapter implements NewLogger {
    private OldLogger oldLogger;
    
    @Override
    public void log(String message) {
        oldLogger.logMessage(message);  // 适配
    }
}
```

### 问题2: Facade成了"God Object"怎么办？

**症状**: Facade越来越大，包含了所有操作

**预防与修复:**

```java
// ❌ God Object
public class ApplicationFacade {
    // 包含了100+个public方法！
    public void registerUser() { }
    public void processPayment() { }
    public void sendEmail() { }
    public void generateReport() { }
    public void backupDatabase() { }
    // 还有很多...
}

// ✅ 拆分成多个小Facade
public interface UserServiceAPI {
    void registerUser();
}

public interface PaymentAPI {
    void processPayment();
}

public interface NotificationAPI {
    void sendEmail();
}

// 只在顶层聚合
public class ApplicationAggregator {
    private UserServicesAPI userAPI;
    private PaymentAPI paymentAPI;
    private NotificationAPI notificationAPI;
}
```

**拆分策略:**
```
1. 按业务域拆分 (Domain-driven)
2. 按操作类型拆分 (Read/Write/Delete)
3. 按访问频率拆分 (Common/Rare)
4. 按数据流拆分 (Input/Process/Output)
```

### 问题3: Facade中的错误处理

**症状**: 不清楚如何在Facade中处理异常

**最佳实践:**

```java
public class RobustFacade {
    public OrderResult placeOrder(OrderRequest req) {
        try {
            // 1. 验证
            validateOrder(req);
            
            // 2. 处理支付
            processPayment(req);
            
            // 3. 生成订单
            Order order = createOrder(req);
            
            return new OrderResult(true, order);
            
        } catch (ValidationException e) {
            // 预期的业务异常 → 返回给客户端
            return new OrderResult(false, "订单验证失败: " + e.getMessage());
            
        } catch (PaymentException e) {
            // 支付异常 → 回滚
            rollbackOrder(req);
            return new OrderResult(false, "支付失败");
            
        } catch (Exception e) {
            // 未预期的异常 → 记录并降级
            logger.error("订单处理异常", e);
            return new OrderResult(false, "系统错误，请稍后重试");
        }
    }
    
    private void validateOrder(OrderRequest req) throws ValidationException {
        if (req.getItems().isEmpty()) {
            throw new ValidationException("订单为空");
        }
    }
    
    private void processPayment(OrderRequest req) throws PaymentException {
        if (req.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new PaymentException("金额无效");
        }
    }
    
    private void rollbackOrder(OrderRequest req) {
        // 回滚操作
    }
}
```

### 问题4: 如何测试Facade？

**症状**: Facade中有太多依赖，测试困难

**解决方案 - 使用Mock:**

```java
@RunWith(MockitoRunner.class)
public class OrderFacadeTest {
    
    @Mock
    private PaymentService paymentService;
    
    @Mock
    private InventoryService inventoryService;
    
    private OrderFacade facade;
    
    @Before
    public void setup() {
        facade = new OrderFacade(paymentService, inventoryService);
    }
    
    @Test
    public void testSuccessfulOrder() {
        // Arrange
        OrderRequest req = new OrderRequest();
        when(inventoryService.checkAvailability(req.getItems()))
            .thenReturn(new InventoryCheck(true));
        when(paymentService.process(req.getAmount()))
            .thenReturn(new PaymentResult("SUCCESS"));
        
        // Act
        OrderResult result = facade.placeOrder(req);
        
        // Assert
        assertTrue(result.isSuccessful());
        verify(paymentService).process(req.getAmount());
        verify(inventoryService).reserve(req.getItems());
    }
    
    @Test
    public void testPaymentFailure() {
        // Arrange
        when(paymentService.process(any(BigDecimal.class)))
            .thenThrow(new PaymentException("余额不足"));
        
        // Act & Assert
        assertThrows(PaymentException.class, () -> 
            facade.placeOrder(new OrderRequest())
        );
    }
}
```

---

## 最佳实践

1. ✅ **Facade应该很傻** - 仅做协调，不做复杂业务逻辑
2. ✅ **按业务域分离** - 不要让一个Facade做所有事
3. ✅ **隐藏实现细节** - 不要暴露内部对象
4. ✅ **文档清晰** - 说明每个方法做了什么
5. ✅ **保持简单** - 如果Facade变复杂，考虑拆分

## 何时避免使用

- ❌ 子系统本身已经很简单 - 直接使用更清晰
- ❌ 不同客户端需要不同接口 - 用Adapter
- ❌ 会变成所有人都用的"万能类" - 这是设计问题信号
- ❌ 只是做传递，没有真正简化 - 这是中间人
