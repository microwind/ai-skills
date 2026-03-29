# 策略模式 - 完整参考实现

## 架构设计

```
┌─────────────────────────────────────────────┐
│            PaymentProcessor                 │  使用者
│ - setStrategy(PaymentStrategy)              │
│ - process(PaymentContext): PaymentResult    │
└────────────┬────────────────────────────────┘
             │ 使用
             ▼
┌─────────────────────────────────────────────┐
│      <<interface>>                          │
│      PaymentStrategy                        │
│ + execute(PaymentContext): PaymentResult    │
└────────┬───────────────────────────────┬────┘
         │ 实现                  实现    │
    ┌────▼─────┐        ┌──────────┐   │
    │ Cred Card│        │  PayPal  │   │...
    │ Payment  │        │ Payment  │   │
    └──────────┘        └──────────┘   │
```

---

## 方法1: 工厂模式 (最推荐用于生产环境)

### 完整实现代码

```java
import java.util.*;
import java.time.LocalDateTime;

// ============= 策略接口和Context定义 =============

/**
 * 支付结果类
 */
public class PaymentResult {
    private final boolean success;
    private final String transactionId;
    private final String errorMessage;
    private final LocalDateTime timestamp;
    
    public PaymentResult(boolean success, String transactionId, String errorMessage) {
        this.success = success;
        this.transactionId = transactionId;
        this.errorMessage = errorMessage;
        this.timestamp = LocalDateTime.now();
    }
    
    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getErrorMessage() { return errorMessage; }
    public LocalDateTime getTimestamp() { return timestamp; }
    
    @Override
    public String toString() {
        return "PaymentResult{" +
                "success=" + success +
                ", transactionId='" + transactionId + '\'' +
                ", errorMessage='" + errorMessage + '\'' +
                ", timestamp=" + timestamp +
                '}';
    }
}

/**
 * 支付上下文，包含支付所需的所有信息
 */
public class PaymentContext {
    private final double amount;
    private final String orderId;
    private final User user;
    private final String description;
    private Map<String, String> metadata = new HashMap<>();
    
    public PaymentContext(double amount, String orderId, User user, String description) {
        this.amount = amount;
        this.orderId = orderId;
        this.user = user;
        this.description = description;
    }
    
    // Getters
    public double getAmount() { return amount; }
    public String getOrderId() { return orderId; }
    public User getUser() { return user; }
    public String getDescription() { return description; }
    public Map<String, String> getMetadata() { return metadata; }
    public void addMetadata(String key, String value) { metadata.put(key, value); }
}

/**
 * 用户信息
 */
public class User {
    private String id;
    private String email;
    private String country;
    private double balance;
    
    public User(String id, String email, String country, double balance) {
        this.id = id;
        this.email = email;
        this.country = country;
        this.balance = balance;
    }
    
    public String getId() { return id; }
    public String getEmail() { return email; }
    public String getCountry() { return country; }
    public double getBalance() { return balance; }
}

/**
 * 策略接口 - 所有支付策略都必须实现这个接口
 */
public interface PaymentStrategy {
    /**
     * 执行支付
     */
    PaymentResult execute(PaymentContext context);
    
    /**
     * 获取策略名称
     */
    default String getName() {
        return this.getClass().getSimpleName();
    }
}

// ============= 具体的支付策略 =============

/**
 * 信用卡支付
 */
public class CreditCardPaymentStrategy implements PaymentStrategy {
    private static final String TRANSACTION_PREFIX = "CC_";
    
    @Override
    public PaymentResult execute(PaymentContext context) {
        System.out.println("[CreditCard] Processing payment: " + context.getAmount());
        
        try {
            // 模拟验证
            validateCard(context);
            
            // 模拟交易
            String transactionId = TRANSACTION_PREFIX + UUID.randomUUID().toString().substring(0, 8);
            simulateProcessing(1000); // 模拟网络延迟
            
            System.out.println("[CreditCard] ✓ Success - Transaction ID: " + transactionId);
            return new PaymentResult(true, transactionId, null);
            
        } catch (Exception e) {
            System.out.println("[CreditCard] ✗ Failed - " + e.getMessage());
            return new PaymentResult(false, null, e.getMessage());
        }
    }
    
    private void validateCard(PaymentContext context) throws Exception {
        String cardInfo = context.getMetadata().get("card_number");
        if (cardInfo == null || cardInfo.length() < 13) {
            throw new Exception("Invalid card number");
        }
        if (context.getAmount() > 50000) {
            throw new Exception("Amount exceeds limit");
        }
    }
    
    private void simulateProcessing(long millis) throws InterruptedException {
        Thread.sleep(millis);
    }
}

/**
 * PayPal支付
 */
public class PayPalPaymentStrategy implements PaymentStrategy {
    private static final String TRANSACTION_PREFIX = "PP_";
    
    @Override
    public PaymentResult execute(PaymentContext context) {
        System.out.println("[PayPal] Redirecting to PayPal for: " + context.getAmount());
        
        try {
            // 模拟验证
            String email = context.getUser().getEmail();
            if (!email.contains("@")) {
                throw new Exception("Invalid PayPal email");
            }
            
            // 模拟交易
            String transactionId = TRANSACTION_PREFIX + UUID.randomUUID().toString().substring(0, 8);
            simulateProcessing(1500);
            
            System.out.println("[PayPal] ✓ Success - Transaction ID: " + transactionId);
            return new PaymentResult(true, transactionId, null);
            
        } catch (Exception e) {
            System.out.println("[PayPal] ✗ Failed - " + e.getMessage());
            return new PaymentResult(false, null, e.getMessage());
        }
    }
    
    private void simulateProcessing(long millis) throws InterruptedException {
        Thread.sleep(millis);
    }
}

/**
 * 支付宝支付（中国）
 */
public class AlipayPaymentStrategy implements PaymentStrategy {
    private static final String TRANSACTION_PREFIX = "ALIPAY_";
    
    @Override
    public PaymentResult execute(PaymentContext context) {
        System.out.println("[Alipay] Processing payment: " + context.getAmount());
        
        try {
            // 支付宝特有：检查是否中国用户
            if (!"CN".equals(context.getUser().getCountry())) {
                throw new Exception("Alipay only available in China");
            }
            
            if (context.getAmount() > 100000) {
                throw new Exception("Single transaction limit exceeded");
            }
            
            String transactionId = TRANSACTION_PREFIX + UUID.randomUUID().toString().substring(0, 8);
            simulateProcessing(800);
            
            System.out.println("[Alipay] ✓ Success - Transaction ID: " + transactionId);
            return new PaymentResult(true, transactionId, null);
            
        } catch (Exception e) {
            System.out.println("[Alipay] ✗ Failed - " + e.getMessage());
            return new PaymentResult(false, null, e.getMessage());
        }
    }
    
    private void simulateProcessing(long millis) throws InterruptedException {
        Thread.sleep(millis);
    }
}

/**
 * 微信支付（中国）
 */
public class WechatPaymentStrategy implements PaymentStrategy {
    private static final String TRANSACTION_PREFIX = "WECHAT_";
    
    @Override
    public PaymentResult execute(PaymentContext context) {
        System.out.println("[Wechat] Processing WeChat payment: " + context.getAmount());
        
        try {
            // 检查地区限制
            if (!"CN".equals(context.getUser().getCountry())) {
                throw new Exception("WeChat Pay only available in China");
            }
            
            // 检查余额（虚拟钱包）
            double userBalance = context.getUser().getBalance();
            if (userBalance < context.getAmount()) {
                throw new Exception("Insufficient balance. Balance: " + userBalance);
            }
            
            String transactionId = TRANSACTION_PREFIX + UUID.randomUUID().toString().substring(0, 8);
            simulateProcessing(600);
            
            System.out.println("[Wechat] ✓ Success - Transaction ID: " + transactionId);
            return new PaymentResult(true, transactionId, null);
            
        } catch (Exception e) {
            System.out.println("[Wechat] ✗ Failed - " + e.getMessage());
            return new PaymentResult(false, null, e.getMessage());
        }
    }
    
    private void simulateProcessing(long millis) throws InterruptedException {
        Thread.sleep(millis);
    }
}

// ============= 策略工厂 =============

/**
 * 支付策略工厂 - 集中管理所有支付策略
 */
public class PaymentStrategyFactory {
    private static final Map<String, PaymentStrategy> strategies = new ConcurrentHashMap<>();
    
    static {
        // 初始化内置策略
        register("credit_card", new CreditCardPaymentStrategy());
        register("paypal", new PayPalPaymentStrategy());
        register("alipay", new AlipayPaymentStrategy());
        register("wechat", new WechatPaymentStrategy());
    }
    
    /**
     * 注册新的策略
     */
    public static void register(String key, PaymentStrategy strategy) {
        if (strategies.containsKey(key)) {
            System.out.println("[Factory] Overwriting strategy: " + key);
        }
        strategies.put(key, strategy);
        System.out.println("[Factory] Strategy registered: " + key);
    }
    
    /**
     * 获取策略
     */
    public static PaymentStrategy getStrategy(String key) {
        PaymentStrategy strategy = strategies.get(key);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown payment strategy: " + key + 
                ". Available: " + strategies.keySet());
        }
        return strategy;
    }
    
    /**
     * 获取所有可用的支付方式
     */
    public static Set<String> getAvailablePaymentMethods() {
        return new HashSet<>(strategies.keySet());
    }
    
    /**
     * 根据用户和订单自动选择最优支付方式
     */
    public static PaymentStrategy suggestStrategy(User user, PaymentContext context) {
        // 中国用户优先微信（更快）
        if ("CN".equals(user.getCountry())) {
            return getStrategy("wechat");
        }
        // 国际用户使用PayPal
        return getStrategy("paypal");
    }
}

// ============= 支付处理器 (使用策略的客户端) =============

/**
 * 支付处理器 - 使用策略模式的核心类
 */
public class PaymentProcessor {
    private PaymentStrategy strategy;
    private List<PaymentResult> paymentHistory = new ArrayList<>();
    
    public PaymentProcessor(PaymentStrategy initialStrategy) {
        this.strategy = initialStrategy;
    }
    
    /**
     * 设置支付策略
     */
    public void setStrategy(PaymentStrategy newStrategy) {
        this.strategy = newStrategy;
        System.out.println("[Processor] Strategy switched to: " + newStrategy.getName());
    }
    
    /**
     * 处理支付
     */
    public PaymentResult processPayment(PaymentContext context) {
        if (strategy == null) {
            throw new IllegalStateException("No payment strategy set");
        }
        
        PaymentResult result = strategy.execute(context);
        paymentHistory.add(result);
        return result;
    }
    
    /**
     * 处理支付，带回退机制
     * 如果首选策略失败，自动切换到备选策略
     */
    public PaymentResult processPaymentWithFallback(PaymentContext context, 
                                                     String primaryMethod, 
                                                     String fallbackMethod) {
        try {
            setStrategy(PaymentStrategyFactory.getStrategy(primaryMethod));
            PaymentResult result = processPayment(context);
            
            if (result.isSuccess()) {
                return result;
            }
        } catch (Exception e) {
            System.out.println("[Processor] Primary strategy failed: " + e.getMessage());
        }
        
        System.out.println("[Processor] Trying fallback strategy: " + fallbackMethod);
        setStrategy(PaymentStrategyFactory.getStrategy(fallbackMethod));
        return processPayment(context);
    }
    
    /**
     * 获取支付历史
     */
    public List<PaymentResult> getPaymentHistory() {
        return new ArrayList<>(paymentHistory);
    }
}

// ============= 使用示例 =============

public class StrategyPatternDemo {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("========== 策略模式演示 ==========\n");
        
        // 创建用户和订单上下文
        User johnDoe = new User("U001", "john@example.com", "US", 5000);
        User zhangsan = new User("U002", "zhang@example.com", "CN", 10000);
        
        PaymentContext context1 = new PaymentContext(99.99, "ORDER001", johnDoe, "Electronics");
        context1.addMetadata("card_number", "1234567890123456");
        
        PaymentContext context2 = new PaymentContext(199.99, "ORDER002", zhangsan, "Books");
        context2.addMetadata("card_number", "1234567890123456");
        
        // ===== 场景1: 基本的策略切换 =====
        System.out.println("【场景1】基本的策略切换");
        System.out.println("----------------------------------------");
        
        PaymentProcessor processor = new PaymentProcessor(
            PaymentStrategyFactory.getStrategy("credit_card")
        );
        
        PaymentResult result1 = processor.processPayment(context1);
        System.out.println("Result: " + result1 + "\n");
        
        // 切换到PayPal
        processor.setStrategy(PaymentStrategyFactory.getStrategy("paypal"));
        PaymentResult result2 = processor.processPayment(context1);
        System.out.println("Result: " + result2 + "\n");
        
        // ===== 场景2: 根据用户选择支付方式 =====
        System.out.println("【场景2】根据用户地区选择支付方式");
        System.out.println("----------------------------------------");
        
        PaymentStrategy suggestedForChina = PaymentStrategyFactory.suggestStrategy(zhangsan, context2);
        processor.setStrategy(suggestedForChina);
        System.out.println("Suggested for China: " + suggestedForChina.getName());
        
        PaymentResult result3 = processor.processPayment(context2);
        System.out.println("Result: " + result3 + "\n");
        
        // ===== 场景3: 失败回退机制 =====
        System.out.println("【场景3】支付失败自动回退");
        System.out.println("----------------------------------------");
        
        User internationalUser = new User("U003", "bob@example.com", "FR", 5000);
        PaymentContext context3 = new PaymentContext(50.0, "ORDER003", internationalUser, "Software");
        context3.addMetadata("card_number", "1234567890123456");
        
        // 尝试支付宝会失败（非中国用户），自动回退到PayPal
        PaymentResult result4 = processor.processPaymentWithFallback(context3, "alipay", "paypal");
        System.out.println("Result: " + result4 + "\n");
        
        // ===== 场景4: 动态添加新支付方式 =====
        System.out.println("【场景4】运行时添加新支付方式");
        System.out.println("----------------------------------------");
        
        // 动态注册比特币支付
        PaymentStrategyFactory.register("bitcoin", new PaymentStrategy() {
            @Override
            public PaymentResult execute(PaymentContext context) {
                System.out.println("[Bitcoin] Processing blockchain transaction: " + context.getAmount());
                Thread.sleep(2000);
                String txId = "BTC_" + UUID.randomUUID().toString().substring(0, 8);
                System.out.println("[Bitcoin] ✓ Success - Transaction ID: " + txId);
                return new PaymentResult(true, txId, null);
            }
        });
        
        processor.setStrategy(PaymentStrategyFactory.getStrategy("bitcoin"));
        PaymentContext context4 = new PaymentContext(0.05, "ORDER004", johnDoe, "Cryptocurrency");
        PaymentResult result5 = processor.processPayment(context4);
        System.out.println("Result: " + result5 + "\n");
        
        // ===== 场景5: 查询可用支付方式 =====
        System.out.println("【场景5】查询所有可用支付方式");
        System.out.println("----------------------------------------");
        System.out.println("Available payment methods: " + 
            PaymentStrategyFactory.getAvailablePaymentMethods());
        
        // ===== 场景6: 支付历史 =====
        System.out.println("\n【场景6】支付历史");
        System.out.println("----------------------------------------");
        processor.getPaymentHistory().forEach(r -> 
            System.out.println("  - " + r)
        );
    }
}
```

---

## 方法2: Lambda表达式（简洁版）

```java
import java.util.*;
import java.util.function.Function;

public class PaymentManagerLambda {
    private Map<String, Function<Double, String>> paymentMethods;
    
    public PaymentManagerLambda() {
        paymentMethods = new HashMap<>();
        
        // 使用Lambda定义支付策略
        paymentMethods.put("credit_card", amount -> {
            System.out.println("Processing credit card payment: $" + amount);
            return "CC_" + UUID.randomUUID().toString().substring(0, 8);
        });
        
        paymentMethods.put("paypal", amount -> {
            System.out.println("Processing PayPal: $" + amount);
            return "PP_" + UUID.randomUUID().toString().substring(0, 8);
        });
        
        paymentMethods.put("alipay", amount -> {
            System.out.println("Processing Alipay: $" + amount);
            return "ALIPAY_" + UUID.randomUUID().toString().substring(0, 8);
        });
    }
    
    public String pay(String method, double amount) {
        Function<Double, String> payment = paymentMethods.get(method);
        if (payment == null) {
            throw new IllegalArgumentException("Unknown payment method");
        }
        return payment.apply(amount);
    }
}

// 使用
PaymentManagerLambda manager = new PaymentManagerLambda();
String txId = manager.pay("credit_card", 99.99);
System.out.println("Transaction: " + txId);
```

---

## Python实现

```python
from abc import ABC, abstractmethod
from datetime import datetime
import uuid
from typing import Optional, Dict

class PaymentResult:
    """支付结果"""
    def __init__(self, success: bool, transaction_id: Optional[str], error_msg: Optional[str]):
        self.success = success
        self.transaction_id = transaction_id
        self.error_message = error_msg
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"PaymentResult(success={self.success}, txid={self.transaction_id}, error={self.error_message})"

class PaymentContext:
    """支付上下文"""
    def __init__(self, amount: float, order_id: str, user_email: str, country: str = "US"):
        self.amount = amount
        self.order_id = order_id
        self.user_email = user_email
        self.country = country
        self.metadata = {}

class PaymentStrategy(ABC):
    """策略接口"""
    @abstractmethod
    def execute(self, context: PaymentContext) -> PaymentResult:
        pass

class CreditCardPayment(PaymentStrategy):
    """信用卡支付"""
    def execute(self, context: PaymentContext) -> PaymentResult:
        print(f"[CreditCard] Processing: ${context.amount}")
        try:
            if context.amount > 50000:
                raise Exception("Amount exceeds limit")
            
            txid = f"CC_{uuid.uuid4().hex[:8]}"
            print(f"[CreditCard] ✓ Success - {txid}")
            return PaymentResult(True, txid, None)
        except Exception as e:
            print(f"[CreditCard] ✗ Failed - {e}")
            return PaymentResult(False, None, str(e))

class PayPalPayment(PaymentStrategy):
    """PayPal支付"""
    def execute(self, context: PaymentContext) -> PaymentResult:
        print(f"[PayPal] Processing: ${context.amount}")
        if "@" not in context.user_email:
            return PaymentResult(False, None, "Invalid email")
        
        txid = f"PP_{uuid.uuid4().hex[:8]}"
        print(f"[PayPal] ✓ Success - {txid}")
        return PaymentResult(True, txid, None)

class AlipayPayment(PaymentStrategy):
    """支付宝支付"""
    def execute(self, context: PaymentContext) -> PaymentResult:
        print(f"[Alipay] Processing: ${context.amount}")
        if context.country != "CN":
            return PaymentResult(False, None, "Only available in China")
        
        txid = f"ALIPAY_{uuid.uuid4().hex[:8]}"
        print(f"[Alipay] ✓ Success - {txid}")
        return PaymentResult(True, txid, None)

class PaymentStrategyFactory:
    """策略工厂"""
    _strategies: Dict[str, PaymentStrategy] = {}
    
    @classmethod
    def register(cls, name: str, strategy: PaymentStrategy):
        cls._strategies[name] = strategy
        print(f"[Factory] Registered: {name}")
    
    @classmethod
    def get_strategy(cls, name: str) -> PaymentStrategy:
        if name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return cls._strategies[name]

# 初始化
PaymentStrategyFactory.register("credit_card", CreditCardPayment())
PaymentStrategyFactory.register("paypal", PayPalPayment())
PaymentStrategyFactory.register("alipay", AlipayPayment())

# 使用
context = PaymentContext(99.99, "ORDER001", "john@example.com", "US")
strategy = PaymentStrategyFactory.get_strategy("paypal")
result = strategy.execute(context)
print(f"Result: {result}")
```

---

## TypeScript实现

```typescript
interface PaymentResult {
    success: boolean;
    transactionId?: string;
    errorMessage?: string;
    timestamp: Date;
}

interface PaymentContext {
    amount: number;
    orderId: string;
    userEmail: string;
    country?: string;
}

// 策略接口
interface PaymentStrategy {
    execute(context: PaymentContext): Promise<PaymentResult>;
}

// 信用卡策略
class CreditCardPayment implements PaymentStrategy {
    async execute(context: PaymentContext): Promise<PaymentResult> {
        console.log(`[CreditCard] Processing: $${context.amount}`);
        
        if (context.amount > 50000) {
            return {
                success: false,
                errorMessage: "Amount exceeds limit",
                timestamp: new Date()
            };
        }
        
        const transactionId = `CC_${Math.random().toString(16).slice(2, 10)}`;
        console.log(`[CreditCard] ✓ Success - ${transactionId}`);
        
        return {
            success: true,
            transactionId,
            timestamp: new Date()
        };
    }
}

// PayPal策略
class PayPalPayment implements PaymentStrategy {
    async execute(context: PaymentContext): Promise<PaymentResult> {
        console.log(`[PayPal] Processing: $${context.amount}`);
        
        if (!context.userEmail.includes("@")) {
            return {
                success: false,
                errorMessage: "Invalid email",
                timestamp: new Date()
            };
        }
        
        const transactionId = `PP_${Math.random().toString(16).slice(2, 10)}`;
        return {
            success: true,
            transactionId,
            timestamp: new Date()
        };
    }
}

// 支付宝策略
class AlipayPayment implements PaymentStrategy {
    async execute(context: PaymentContext): Promise<PaymentResult> {
        console.log(`[Alipay] Processing: $${context.amount}`);
        
        if (context.country !== "CN") {
            return {
                success: false,
                errorMessage: "Only available in China",
                timestamp: new Date()
            };
        }
        
        const transactionId = `ALIPAY_${Math.random().toString(16).slice(2, 10)}`;
        return {
            success: true,
            transactionId,
            timestamp: new Date()
        };
    }
}

// 策略工厂
class PaymentStrategyFactory {
    private static strategies: Map<string, PaymentStrategy> = new Map();
    
    static register(name: string, strategy: PaymentStrategy): void {
        this.strategies.set(name, strategy);
        console.log(`[Factory] Registered: ${name}`);
    }
    
    static getStrategy(name: string): PaymentStrategy {
        const strategy = this.strategies.get(name);
        if (!strategy) {
            throw new Error(`Unknown strategy: ${name}`);
        }
        return strategy;
    }
}

// 支付处理器
class PaymentProcessor {
    private strategy: PaymentStrategy;
    private history: PaymentResult[] = [];
    
    constructor(strategy: PaymentStrategy) {
        this.strategy = strategy;
    }
    
    setStrategy(strategy: PaymentStrategy): void {
        this.strategy = strategy;
    }
    
    async process(context: PaymentContext): Promise<PaymentResult> {
        const result = await this.strategy.execute(context);
        this.history.push(result);
        return result;
    }
    
    getHistory(): PaymentResult[] {
        return [...this.history];
    }
}

// 使用示例
async function demo() {
    // 初始化工厂
    PaymentStrategyFactory.register("credit_card", new CreditCardPayment());
    PaymentStrategyFactory.register("paypal", new PayPalPayment());
    PaymentStrategyFactory.register("alipay", new AlipayPayment());
    
    // 创建处理器
    const processor = new PaymentProcessor(
        PaymentStrategyFactory.getStrategy("credit_card")
    );
    
    // 处理支付
    const context: PaymentContext = {
        amount: 99.99,
        orderId: "ORDER001",
        userEmail: "john@example.com",
        country: "US"
    };
    
    let result = await processor.process(context);
    console.log("Result:", result);
    
    // 切换策略
    processor.setStrategy(PaymentStrategyFactory.getStrategy("paypal"));
    result = await processor.process(context);
    console.log("Result:", result);
    
    // 中国用户使用支付宝
    const chinaContext: PaymentContext = {
        amount: 199.99,
        orderId: "ORDER002",
        userEmail: "zhang@example.com",
        country: "CN"
    };
    
    processor.setStrategy(PaymentStrategyFactory.getStrategy("alipay"));
    result = await processor.process(chinaContext);
    console.log("Result:", result);
}

demo().catch(console.error);
```

---

## 性能对比表

| 方案 | 代码复杂度 | 运行时开销 | 扩展性 | 维护性 | 推荐场景 |
|-----|---------|---------|-------|-------|--------|
| **工厂模式** | 中 | 低 | 极高 | 高 | 生产环境、策略多 |
| **直接注入** | 低 | 极低 | 中 | 中 | 原型、简单场景 |
| **Lambda** | 低 | 中 | 低 | 中 | 简单算法 |
| **注解驱动** | 高 | 中 | 极高 | 高 | 企业级应用 |

---

## 单元测试示例

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PaymentStrategyTest {
    
    @Test
    public void testCreditCardSuccess() {
        User user = new User("U001", "john@example.com", "US", 5000);
        PaymentContext context = new PaymentContext(99.99, "ORDER001", user, "Test");
        context.addMetadata("card_number", "1234567890123456");
        
        PaymentStrategy strategy = new CreditCardPaymentStrategy();
        PaymentResult result = strategy.execute(context);
        
        assertTrue(result.isSuccess());
        assertNotNull(result.getTransactionId());
    }
    
    @Test
    public void testPayPalSuccess() {
        User user = new User("U002", "jane@example.com", "US", 5000);
        PaymentContext context = new PaymentContext(50.0, "ORDER002", user, "Test");
        
        PaymentStrategy strategy = new PayPalPaymentStrategy();
        PaymentResult result = strategy.execute(context);
        
        assertTrue(result.isSuccess());
        assertTrue(result.getTransactionId().startsWith("PP_"));
    }
    
    @Test
    public void testAlipayOnlyChinese() {
        User user = new User("U003", "bob@example.com", "US", 5000);
        PaymentContext context = new PaymentContext(100.0, "ORDER003", user, "Test");
        
        PaymentStrategy strategy = new AlipayPaymentStrategy();
        PaymentResult result = strategy.execute(context);
        
        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("China"));
    }
    
    @Test
    public void testStrategySwitch() {
        PaymentProcessor processor = new PaymentProcessor(
            new CreditCardPaymentStrategy()
        );
        
        processor.setStrategy(new PayPalPaymentStrategy());
        // 验证策略已切换
        assertEquals("PayPalPaymentStrategy", processor.getCurrentStrategy().getClass().getSimpleName());
    }
    
    @Test
    public void testFactoryUnknownStrategy() {
        assertThrows(IllegalArgumentException.class, () -> {
            PaymentStrategyFactory.getStrategy("unknown");
        });
    }
    
    @Test
    public void testDynamicStrategyRegistration() {
        PaymentStrategy customStrategy = new PaymentStrategy() {
            @Override
            public PaymentResult execute(PaymentContext context) {
                return new PaymentResult(true, "CUSTOM_123", null);
            }
        };
        
        PaymentStrategyFactory.register("custom", customStrategy);
        PaymentStrategy retrieved = PaymentStrategyFactory.getStrategy("custom");
        
        assertNotNull(retrieved);
        assertTrue(retrieved.getClass().getName().contains("anonymousClass"));
    }
}
```

---

## 常见错误及解决方案

### ❌ 错误1: 同一个策略对象被多个线程使用导致状态混乱

```java
// ❌ 问题代码
public class BankTransferStrategy implements PaymentStrategy {
    private String accountNumber;  // 状态
    
    @Override
    public PaymentResult execute(PaymentContext context) {
        accountNumber = context.getMetadata().get("account");
        // 多线程下accountNumber会被覆盖
    }
}

// ✅ 解决方案：使用参数代替成员变量
public class BankTransferStrategy implements PaymentStrategy {
    @Override
    public PaymentResult execute(PaymentContext context) {
        String accountNumber = context.getMetadata().get("account");
        // 线程安全
    }
}
```

### ❌ 错误2: 策略异常没有被处理，导致外部系统崩溃

```java
// ❌ 问题代码
PaymentResult result = strategy.execute(context);  // 可能抛异常

// ✅ 解决方案：添加异常处理和回退
public PaymentResult executeWithFallback(String primaryMethod, String fallbackMethod) {
    try {
        PaymentStrategy strategy = factory.getStrategy(primaryMethod);
        PaymentResult result = strategy.execute(context);
        if (result.isSuccess()) return result;
    } catch (Exception e) {
        logger.error("Primary strategy failed", e);
    }
    
    try {
        PaymentStrategy fallback = factory.getStrategy(fallbackMethod);
        return fallback.execute(context);
    } catch (Exception e) {
        logger.error("Both strategies failed", e);
        throw new FinalPaymentException(e);
    }
}
```

### ❌ 错误3: 策略工厂内存泄漏，策略对象不被回收

```java
// ❌ 问题代码（假设策略持有大量数据）
PaymentStrategyFactory.register("expensive", new ExpensiveStrategy());  // 持有大量缓存
PaymentStrategyFactory.register("expensive", new ExpensiveStrategy());  // 旧的不会被回收

// ✅ 解决方案：支持注销策略
public static void unregister(String key) {
    strategies.remove(key);
}

public static void clear() {
    strategies.clear();
}
```

---

## 最佳实践总结

1. **✅ 策略接口精简**: 最多3个参数，使用Context对象
2. **✅ 一个策略一个类**: 避免在一个类中实现多个算法
3. **✅ 使用工厂管理**: 集中化策略创建和注册
4. **✅ 支持动态扩展**: 允许运行时添加新策略
5. **✅ 完整的异常处理**: 策略失败要有回退方案
6. **✅ 策略选择逻辑清晰**: 使用规则引擎或选择器模式
7. **✅ 性能监控**: 记录每个策略的执行时间和成功率
8. **✅ 充分的文档**: 说明每个策略的适用场景和限制
