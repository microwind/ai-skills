# DRY原则 - 参考实现

## 核心原理与设计

DRY（Don't Repeat Yourself）：**系统中每一个知识点都应该有唯一、权威的表示**。重复不仅是代码重复，更是知识的重复。

---

## Java 参考实现

### 反面示例：三种重复

```java
/**
 * ❌ 代码重复：计算逻辑复制粘贴
 */
public class OrderService {
    public double calculateOrderTotal(Order order) {
        double total = 0;
        for (Item item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        if (total > 1000) total *= 0.9;
        total *= 1.13;  // 税率
        return total;
    }

    public double calculateQuoteTotal(List<Item> items) {
        double total = 0;
        for (Item item : items) {
            total += item.getPrice() * item.getQuantity();  // 重复！
        }
        if (total > 1000) total *= 0.9;  // 重复！
        total *= 1.13;  // 重复！
        return total;
    }
}

/**
 * ❌ 知识重复：同一规则多处定义
 */
// config.java
public static final int MAX_LOGIN_ATTEMPTS = 5;

// AuthService.java
if (attempts > 5) { lockAccount(); }  // 硬编码，与配置不同步

// auth.test.java
assertEquals(5, maxAttempts);  // 测试中又写了一遍
```

### 正面示例：消除重复

```java
/**
 * ✅ 提取共同逻辑为独立服务
 */
public class PricingService {
    private static final double DISCOUNT_THRESHOLD = 1000;
    private static final double DISCOUNT_RATE = 0.9;
    private static final double TAX_RATE = 1.13;

    public double calculateSubtotal(List<Item> items) {
        return items.stream()
            .mapToDouble(i -> i.getPrice() * i.getQuantity())
            .sum();
    }

    public double applyDiscountAndTax(double subtotal) {
        double discounted = subtotal > DISCOUNT_THRESHOLD
            ? subtotal * DISCOUNT_RATE : subtotal;
        return discounted * TAX_RATE;
    }

    public double calculateTotal(List<Item> items) {
        return applyDiscountAndTax(calculateSubtotal(items));
    }
}

public class OrderService {
    private final PricingService pricing;

    public double calculateOrderTotal(Order order) {
        return pricing.calculateTotal(order.getItems());
    }
}

public class QuoteService {
    private final PricingService pricing;

    public double calculateQuoteTotal(List<Item> items) {
        return pricing.calculateTotal(items);
    }
}

/**
 * ✅ 知识的单一来源
 */
public class AuthConfig {
    public static final int MAX_LOGIN_ATTEMPTS = 5;
}

// 所有地方引用同一常量
if (attempts > AuthConfig.MAX_LOGIN_ATTEMPTS) { lockAccount(); }

/**
 * ✅ 统一验证逻辑
 */
public class EmailValidator {
    private static final Pattern EMAIL_PATTERN =
        Pattern.compile("^[\\w.]+@[\\w.]+\\.\\w+$");

    public static boolean isValid(String email) {
        return email != null && EMAIL_PATTERN.matcher(email).matches();
    }
}

// 所有需要验证邮箱的地方都调用同一个方法
public class UserService {
    public void register(String email) {
        if (!EmailValidator.isValid(email)) throw new ValidationException("无效邮箱");
    }
}

public class NewsletterService {
    public void subscribe(String email) {
        if (!EmailValidator.isValid(email)) throw new ValidationException("无效邮箱");
    }
}
```

---

## Python 参考实现

```python
"""
✅ 消除重复的 Python 实现
"""

# ❌ 重复的验证逻辑
class UserRegistration:
    def register(self, email):
        if "@" not in email or "." not in email.split("@")[1]:
            raise ValueError("无效邮箱")

class Newsletter:
    def subscribe(self, email):
        import re
        if not re.match(r'^[\w.]+@[\w.]+\.\w+$', email):
            raise ValueError("邮箱格式错误")

# ✅ 统一验证
import re

class EmailValidator:
    PATTERN = re.compile(r'^[\w.]+@[\w.]+\.\w+$')

    @classmethod
    def validate(cls, email: str):
        if not cls.PATTERN.match(email):
            raise ValueError(f"无效邮箱: {email}")

    @classmethod
    def is_valid(cls, email: str) -> bool:
        return bool(cls.PATTERN.match(email))

class UserRegistration:
    def register(self, email):
        EmailValidator.validate(email)
        # ... 注册逻辑

class Newsletter:
    def subscribe(self, email):
        EmailValidator.validate(email)
        # ... 订阅逻辑


# ✅ 模板方法消除算法重复
from abc import ABC, abstractmethod

class DataExporter(ABC):
    """导出流程固定，格式不同 → 模板方法"""
    def export(self, data: list) -> str:
        filtered = self.filter_data(data)
        formatted = self.format_data(filtered)
        return self.write_output(formatted)

    def filter_data(self, data):
        return [d for d in data if d.get("active")]

    @abstractmethod
    def format_data(self, data) -> str: pass

    @abstractmethod
    def write_output(self, content: str) -> str: pass

class CsvExporter(DataExporter):
    def format_data(self, data):
        lines = [",".join(data[0].keys())]
        for row in data:
            lines.append(",".join(str(v) for v in row.values()))
        return "\n".join(lines)

    def write_output(self, content):
        return content  # 返回 CSV 字符串

class JsonExporter(DataExporter):
    def format_data(self, data):
        import json
        return json.dumps(data, ensure_ascii=False)

    def write_output(self, content):
        return content  # 返回 JSON 字符串
```

---

## TypeScript 参考实现

```typescript
// ❌ 知识重复
const MAX_RETRIES_ORDER = 3;  // order.service.ts
const MAX_RETRIES_PAYMENT = 3;  // payment.service.ts
const maxRetries = 3;  // notification.service.ts

// ✅ 单一来源
// config.ts
export const RETRY_CONFIG = {
    MAX_RETRIES: 3,
    BASE_DELAY_MS: 1000,
} as const;

// ✅ 提取公共重试逻辑
async function withRetry<T>(
    fn: () => Promise<T>,
    maxRetries = RETRY_CONFIG.MAX_RETRIES,
    baseDelay = RETRY_CONFIG.BASE_DELAY_MS
): Promise<T> {
    let lastError: Error;
    for (let i = 0; i <= maxRetries; i++) {
        try { return await fn(); }
        catch (e) {
            lastError = e as Error;
            if (i < maxRetries) await sleep(baseDelay * Math.pow(2, i));
        }
    }
    throw lastError!;
}

// 所有服务复用同一重试逻辑
class OrderService {
    async createOrder(data: OrderDTO) {
        return withRetry(() => this.api.post('/orders', data));
    }
}

class PaymentService {
    async charge(amount: number) {
        return withRetry(() => this.api.post('/payments', { amount }));
    }
}
```

---

## 单元测试示例

```java
class PricingServiceTest {
    PricingService pricing = new PricingService();

    @Test
    void testSubtotal() {
        List<Item> items = List.of(new Item("A", 100, 2), new Item("B", 50, 3));
        assertEquals(350.0, pricing.calculateSubtotal(items));
    }

    @Test
    void testDiscountApplied() {
        double result = pricing.applyDiscountAndTax(2000);
        assertEquals(2000 * 0.9 * 1.13, result, 0.01);
    }

    @Test
    void testNoDiscount() {
        double result = pricing.applyDiscountAndTax(500);
        assertEquals(500 * 1.13, result, 0.01);
    }
}

class EmailValidatorTest {
    @Test
    void testValidEmail() {
        assertTrue(EmailValidator.isValid("user@example.com"));
    }

    @Test
    void testInvalidEmail() {
        assertFalse(EmailValidator.isValid("invalid"));
        assertFalse(EmailValidator.isValid(null));
    }
}
```

---

## 总结

| 重复类型 | 消除方法 | 效果 |
|----------|---------|------|
| 代码片段 | 提取方法/服务 | 一处修改，全局生效 |
| 验证逻辑 | 统一验证器 | 规则一致，不会遗漏 |
| 配置值 | 集中配置常量 | 不会出现不同步 |
| 算法骨架 | 模板方法 | 复用流程，扩展步骤 |
| 数据定义 | 代码生成 | 自动同步，减少手动维护 |
