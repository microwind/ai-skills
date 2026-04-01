# 开闭原则 - 参考实现

## 核心原理

OCP 强调通过**抽象**和**多态**实现扩展，而不是修改现有代码。

### 关键设计模式应用

| 变化点 | 推荐模式 | 实现方式 |
|--------|---------|---------|
| 新增产品/实现 | 工厂 + 策略 | 接口 + 工厂类 |
| 算法步骤变化 | 模板方法 | 抽象类 + 钩子 |
| 功能动态增强 | 装饰器 | 接口 + 装饰类 |
| 复杂对象创建 | 生成器 | 建造者类 |
| 行为切换 | 状态/策略 | 接口 + 实现类 |

---

## Java 完整参考实现

### 场景：支付系统扩展

```java
// ✅ 遵循OCP的设计

// 1. 支付网关接口（对扩展开放）
public interface PaymentGateway {
    PaymentResult processPayment(double amount);
    boolean supportsRefund();
    boolean refund(String transactionId);
}

// 2. 支付结果
public class PaymentResult {
    private final boolean success;
    private final String transactionId;
    private final String message;

    public PaymentResult(boolean success, String transactionId, String message) {
        this.success = success;
        this.transactionId = transactionId;
        this.message = message;
    }

    public boolean isSuccess() { return success; }
    public String getTransactionId() { return transactionId; }
    public String getMessage() { return message; }
}

// 3. 各种支付实现（可以单独添加，不修改现有类）
public class AlipayGateway implements PaymentGateway {
    @Override
    public PaymentResult processPayment(double amount) {
        System.out.println("Processing Alipay payment: " + amount);
        String txnId = "alipay_" + System.currentTimeMillis();
        return new PaymentResult(true, txnId, "Alipay payment successful");
    }

    @Override
    public boolean supportsRefund() { return true; }

    @Override
    public boolean refund(String transactionId) {
        System.out.println("Alipay refund: " + transactionId);
        return true;
    }
}

public class WechatGateway implements PaymentGateway {
    @Override
    public PaymentResult processPayment(double amount) {
        System.out.println("Processing WeChat payment: " + amount);
        String txnId = "wechat_" + System.currentTimeMillis();
        return new PaymentResult(true, txnId, "WeChat payment successful");
    }

    @Override
    public boolean supportsRefund() { return true; }

    @Override
    public boolean refund(String transactionId) {
        System.out.println("WeChat refund: " + transactionId);
        return true;
    }
}

public class StripeGateway implements PaymentGateway {
    @Override
    public PaymentResult processPayment(double amount) {
        System.out.println("Processing Stripe payment: " + amount);
        String txnId = "stripe_" + System.currentTimeMillis();
        return new PaymentResult(true, txnId, "Stripe payment successful");
    }

    @Override
    public boolean supportsRefund() { return true; }

    @Override
    public boolean refund(String transactionId) {
        System.out.println("Stripe refund: " + transactionId);
        return true;
    }
}

// 4. 工厂类（配置驱动，无需if-else）
public class PaymentGatewayFactory {
    private static final Map<String, Supplier<PaymentGateway>> REGISTRY =
        new ConcurrentHashMap<>();

    static {
        // 默认注册
        register("ALIPAY", AlipayGateway::new);
        register("WECHAT", WechatGateway::new);
        register("STRIPE", StripeGateway::new);
    }

    public static void register(String type, Supplier<PaymentGateway> creator) {
        REGISTRY.put(type.toUpperCase(), creator);
    }

    public static PaymentGateway create(String type) {
        Supplier<PaymentGateway> creator = REGISTRY.get(type.toUpperCase());
        if (creator == null) {
            throw new IllegalArgumentException("Unknown payment type: " + type);
        }
        return creator.get();
    }

    public static Set<String> getAvailableGateways() {
        return new HashSet<>(REGISTRY.keySet());
    }
}

// 5. 支付处理器（对修改关闭）
public class PaymentProcessor {
    /**
     * 处理支付 - 对扩展开放（可传入任何PaymentGateway实现）
     * - 对修改关闭（无需修改这个类添加新的支付方式）
     */
    public PaymentResult process(String paymentType, double amount) {
        PaymentGateway gateway = PaymentGatewayFactory.create(paymentType);
        return gateway.processPayment(amount);
    }

    public PaymentResult processWithGateway(PaymentGateway gateway, double amount) {
        return gateway.processPayment(amount);
    }
}

// 6. 使用示例
public class PaymentDemo {
    public static void main(String[] args) {
        PaymentProcessor processor = new PaymentProcessor();

        // 使用现有的支付方式
        processor.process("ALIPAY", 100);
        processor.process("WECHAT", 100);
        processor.process("STRIPE", 100);

        // 添加新的支付方式 - 无需修改 PaymentProcessor！
        PaymentGatewayFactory.register("PAYPAL", PayPalGateway::new);
        processor.process("PAYPAL", 100);

        // 或者直接传入gateway实现
        PaymentGateway customGateway = new CustomPaymentGateway();
        processor.processWithGateway(customGateway, 100);
    }
}

// 7. 单元测试
@Test
public void testPaymentProcessor() {
    PaymentProcessor processor = new PaymentProcessor();

    PaymentResult result = processor.process("ALIPAY", 100);
    assertTrue(result.isSuccess());

    result = processor.process("WECHAT", 100);
    assertTrue(result.isSuccess());

    // 新增支付方式，测试无需修改
    PaymentGatewayFactory.register("TEST", MockPaymentGateway::new);
    result = processor.process("TEST", 100);
    assertTrue(result.isSuccess());
}
```

---

## Python 完整参考实现

```python
"""
✅ 遵循OCP的Python设计
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Callable, Optional
from datetime import datetime

# 1. 支付网关接口
class PaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> 'PaymentResult':
        pass

    @abstractmethod
    def supports_refund(self) -> bool:
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        pass

# 2. 支付结果
class PaymentResult:
    def __init__(self, success: bool, transaction_id: str, message: str):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message

    def __repr__(self):
        return f"PaymentResult(success={self.success}, txn_id={self.transaction_id})"

# 3. 各种支付实现
class AlipayGateway(PaymentGateway):
    def process_payment(self, amount: float) -> PaymentResult:
        print(f"Processing Alipay payment: {amount}")
        txn_id = f"alipay_{datetime.now().timestamp()}"
        return PaymentResult(True, txn_id, "Alipay payment successful")

    def supports_refund(self) -> bool:
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"Alipay refund: {transaction_id}")
        return True

class WechatGateway(PaymentGateway):
    def process_payment(self, amount: float) -> PaymentResult:
        print(f"Processing WeChat payment: {amount}")
        txn_id = f"wechat_{datetime.now().timestamp()}"
        return PaymentResult(True, txn_id, "WeChat payment successful")

    def supports_refund(self) -> bool:
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"WeChat refund: {transaction_id}")
        return True

class StripeGateway(PaymentGateway):
    def process_payment(self, amount: float) -> PaymentResult:
        print(f"Processing Stripe payment: {amount}")
        txn_id = f"stripe_{datetime.now().timestamp()}"
        return PaymentResult(True, txn_id, "Stripe payment successful")

    def supports_refund(self) -> bool:
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"Stripe refund: {transaction_id}")
        return True

# 4. 工厂类（配置驱动）
class PaymentGatewayFactory:
    _registry: Dict[str, Callable[[], PaymentGateway]] = {}

    @classmethod
    def register(cls, payment_type: str, creator: Callable[[], PaymentGateway]):
        cls._registry[payment_type.upper()] = creator

    @classmethod
    def create(cls, payment_type: str) -> PaymentGateway:
        creator = cls._registry.get(payment_type.upper())
        if not creator:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return creator()

    @classmethod
    def get_available_gateways(cls) -> list:
        return list(cls._registry.keys())

# 注册默认支付方式
PaymentGatewayFactory.register("ALIPAY", AlipayGateway)
PaymentGatewayFactory.register("WECHAT", WechatGateway)
PaymentGatewayFactory.register("STRIPE", StripeGateway)

# 5. 支付处理器（对修改关闭）
class PaymentProcessor:
    def process(self, payment_type: str, amount: float) -> PaymentResult:
        """
        处理支付 - 对扩展开放，对修改关闭
        新增支付方式只需调用 PaymentGatewayFactory.register()
        """
        gateway = PaymentGatewayFactory.create(payment_type)
        return gateway.process_payment(amount)

    def process_with_gateway(self, gateway: PaymentGateway, amount: float) -> PaymentResult:
        return gateway.process_payment(amount)

# 6. 使用示例
if __name__ == "__main__":
    processor = PaymentProcessor()

    # 使用现有支付方式
    result = processor.process("ALIPAY", 100)
    print(result)

    result = processor.process("WECHAT", 100)
    print(result)

    # 添加新支付方式 - 无需修改任何现有代码！
    class PayPalGateway(PaymentGateway):
        def process_payment(self, amount: float) -> PaymentResult:
            print(f"Processing PayPal payment: {amount}")
            return PaymentResult(True, f"paypal_{datetime.now().timestamp()}", "PayPal successful")

        def supports_refund(self) -> bool:
            return True

        def refund(self, transaction_id: str) -> bool:
            return True

    PaymentGatewayFactory.register("PAYPAL", PayPalGateway)
    result = processor.process("PAYPAL", 100)
    print(result)

    print(f"Available gateways: {PaymentGatewayFactory.get_available_gateways()}")
```

---

## TypeScript 完整参考实现

```typescript
/**
 * ✅ 遵循OCP的TypeScript设计
 */

// 1. 支付结果
class PaymentResult {
    constructor(
        public success: boolean,
        public transactionId: string,
        public message: string
    ) {}

    toString(): string {
        return `PaymentResult(success=${this.success}, txnId=${this.transactionId})`;
    }
}

// 2. 支付网关接口
interface PaymentGateway {
    processPayment(amount: number): PaymentResult;
    supportsRefund(): boolean;
    refund(transactionId: string): boolean;
}

// 3. 支付实现
class AlipayGateway implements PaymentGateway {
    processPayment(amount: number): PaymentResult {
        console.log(`Processing Alipay payment: ${amount}`);
        const txnId = `alipay_${Date.now()}`;
        return new PaymentResult(true, txnId, "Alipay successful");
    }

    supportsRefund(): boolean { return true; }

    refund(transactionId: string): boolean {
        console.log(`Alipay refund: ${transactionId}`);
        return true;
    }
}

class WechatGateway implements PaymentGateway {
    processPayment(amount: number): PaymentResult {
        console.log(`Processing WeChat payment: ${amount}`);
        const txnId = `wechat_${Date.now()}`;
        return new PaymentResult(true, txnId, "WeChat successful");
    }

    supportsRefund(): boolean { return true; }

    refund(transactionId: string): boolean {
        console.log(`WeChat refund: ${transactionId}`);
        return true;
    }
}

class StripeGateway implements PaymentGateway {
    processPayment(amount: number): PaymentResult {
        console.log(`Processing Stripe payment: ${amount}`);
        const txnId = `stripe_${Date.now()}`;
        return new PaymentResult(true, txnId, "Stripe successful");
    }

    supportsRefund(): boolean { return true; }

    refund(transactionId: string): boolean {
        console.log(`Stripe refund: ${transactionId}`);
        return true;
    }
}

// 4. 工厂类
class PaymentGatewayFactory {
    private static registry: Map<string, () => PaymentGateway> = new Map();

    static {
        this.register("ALIPAY", () => new AlipayGateway());
        this.register("WECHAT", () => new WechatGateway());
        this.register("STRIPE", () => new StripeGateway());
    }

    static register(type: string, creator: () => PaymentGateway): void {
        this.registry.set(type.toUpperCase(), creator);
    }

    static create(type: string): PaymentGateway {
        const creator = this.registry.get(type.toUpperCase());
        if (!creator) {
            throw new Error(`Unknown payment type: ${type}`);
        }
        return creator();
    }

    static getAvailableGateways(): string[] {
        return Array.from(this.registry.keys());
    }
}

// 5. 支付处理器
class PaymentProcessor {
    process(paymentType: string, amount: number): PaymentResult {
        const gateway = PaymentGatewayFactory.create(paymentType);
        return gateway.processPayment(amount);
    }

    processWithGateway(gateway: PaymentGateway, amount: number): PaymentResult {
        return gateway.processPayment(amount);
    }
}

// 6. 使用示例
const processor = new PaymentProcessor();

// 现有支付方式
console.log(processor.process("ALIPAY", 100));
console.log(processor.process("WECHAT", 100));

// 添加新支付方式 - 无需修改 PaymentProcessor
class PayPalGateway implements PaymentGateway {
    processPayment(amount: number): PaymentResult {
        console.log(`Processing PayPal payment: ${amount}`);
        return new PaymentResult(true, `paypal_${Date.now()}`, "PayPal successful");
    }

    supportsRefund(): boolean { return true; }

    refund(transactionId: string): boolean { return true; }
}

PaymentGatewayFactory.register("PAYPAL", () => new PayPalGateway());
console.log(processor.process("PAYPAL", 100));
```

---

## 单元测试示例

### Java JUnit

```java
@Test
public void testPaymentProcessor() {
    PaymentProcessor processor = new PaymentProcessor();

    // 测试现有支付方式
    PaymentResult result = processor.process("ALIPAY", 100);
    assertTrue(result.isSuccess());
    assertNotNull(result.getTransactionId());

    // 测试新增支付方式（不修改PaymentProcessor）
    PaymentGatewayFactory.register("MOCK", MockPaymentGateway::new);
    result = processor.process("MOCK", 100);
    assertTrue(result.isSuccess());
}

@Test
public void testNewPaymentGateway() {
    // 完全独立的新支付网关测试
    PaymentGateway gateway = new CustomPaymentGateway();
    PaymentResult result = gateway.processPayment(100);
    assertTrue(result.isSuccess());
}
```

### Python pytest

```python
def test_payment_processor():
    processor = PaymentProcessor()

    result = processor.process("ALIPAY", 100)
    assert result.success
    assert result.transaction_id is not None

def test_new_payment_gateway():
    class TestGateway(PaymentGateway):
        def process_payment(self, amount):
            return PaymentResult(True, "test_123", "Success")

        def supports_refund(self):
            return True

        def refund(self, transaction_id):
            return True

    PaymentGatewayFactory.register("TEST", TestGateway)
    processor = PaymentProcessor()
    result = processor.process("TEST", 100)
    assert result.success
```

---

## 总结

**OCP核心实现**：

1. **定义抽象接口** - 所有实现都遵循同一接口
2. **创建工厂类** - 无if-else，配置驱动
3. **业务逻辑依赖抽象** - 只用接口，不用具体类
4. **新增功能 = 新增类** - 无需修改现有代码

**效果**：
- 新增支付方式耗时 < 15分钟
- 无需回归测试现有功能
- 新增功能可独立并行开发
- 代码更稳定，风险更低

这是长期项目的最佳实践。
