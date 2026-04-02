---
name: DRY原则
description: "Don't Repeat Yourself - 系统中每一个知识点都应该有唯一、权威的表示，避免重复代码和重复逻辑。"
license: MIT
---

# DRY 原则 (Don't Repeat Yourself)

## 概述

DRY 原则由 Andy Hunt 和 Dave Thomas 在《程序员修炼之道》中提出：**系统中每一个知识点都应该有唯一、明确、权威的表示**。

**核心思想**：
- 不是仅仅指"不要复制粘贴代码"
- 更深层含义是避免**知识的重复**（业务规则、逻辑、数据定义）
- 修改一个业务规则时，只需要改一个地方

**重复的三种类型**：
- **代码重复**：相同的代码段出现多次
- **逻辑重复**：代码不同但做相同的事
- **知识重复**：同一业务规则在多处定义

## 代码重复示例

```java
// ❌ 代码重复
public class OrderService {
    public double calculateTotal(Order order) {
        double total = 0;
        for (Item item : order.getItems()) {
            total += item.getPrice() * item.getQuantity();
        }
        if (total > 1000) total *= 0.9;  // 折扣逻辑
        total *= 1.13;  // 税率
        return total;
    }

    public double calculateQuote(List<Item> items) {
        double total = 0;
        for (Item item : items) {
            total += item.getPrice() * item.getQuantity();  // 重复！
        }
        if (total > 1000) total *= 0.9;  // 重复！
        total *= 1.13;  // 重复！
        return total;
    }
}

// ✅ 消除重复
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
```

## 逻辑重复示例

```python
# ❌ 代码不同，但逻辑重复（都在验证邮箱）
class UserRegistration:
    def register(self, email: str):
        if "@" not in email or "." not in email.split("@")[1]:
            raise ValueError("无效邮箱")

class Newsletter:
    def subscribe(self, email: str):
        import re
        if not re.match(r'^[\w.]+@[\w.]+\.\w+$', email):
            raise ValueError("邮箱格式错误")

# ✅ 统一验证逻辑
class EmailValidator:
    @staticmethod
    def validate(email: str) -> bool:
        import re
        return bool(re.match(r'^[\w.]+@[\w.]+\.\w+$', email))

class UserRegistration:
    def register(self, email: str):
        if not EmailValidator.validate(email):
            raise ValueError("无效邮箱")

class Newsletter:
    def subscribe(self, email: str):
        if not EmailValidator.validate(email):
            raise ValueError("无效邮箱")
```

## 知识重复示例

```typescript
// ❌ 同一业务规则在多处定义
// config.ts
const MAX_LOGIN_ATTEMPTS = 5;

// auth.service.ts
if (attempts > 5) {  // 硬编码，与 config 不同步
    lockAccount();
}

// auth.test.ts
expect(lockAfterAttempts).toBe(5);  // 测试中又写了一遍

// ✅ 单一来源
// config.ts
export const AUTH_CONFIG = {
    MAX_LOGIN_ATTEMPTS: 5,
} as const;

// auth.service.ts
import { AUTH_CONFIG } from './config';
if (attempts > AUTH_CONFIG.MAX_LOGIN_ATTEMPTS) {
    lockAccount();
}
```

## 何时重复是可以接受的

```
1. 偶然重复：两段代码现在相同但变化原因不同
   - 订单折扣和会员折扣恰好都是 9 折
   - 未来可能独立变化，强行合并反而有害

2. 跨服务重复：微服务间的 DTO
   - 不同服务可能独立演进
   - 共享库引入更大的耦合问题

3. 测试代码：测试中的重复有时提高可读性
   - 每个测试方法自包含，比抽象更清晰
```

## 优缺点分析

### ✅ 优点
1. **一处修改，全局生效** - 减少遗漏
2. **代码量减少** - 更易维护
3. **一致性保证** - 业务规则不会自相矛盾
4. **bug 修复只需一次** - 不会修了一处忘了另一处

### ❌ 过度 DRY 的危害
1. **错误的抽象** - 把偶然相似的代码强行合并
2. **增加耦合** - 不相关的模块共享代码
3. **降低可读性** - 过度间接让代码难以追踪
4. **过早抽象** - 只出现两次就抽取，可能方向错误

## 最佳实践

### Rule of Three（三次法则）

```
第1次：直接写
第2次：允许重复，标注 TODO
第3次：重构，提取共同逻辑

不要在重复出现2次时就抽象——你可能还不了解正确的抽象方向
```

### 消除重复的方法

| 重复类型 | 消除方法 | 示例 |
|----------|---------|------|
| 代码片段重复 | 提取方法 | extractMethod() |
| 类间重复 | 提取基类/工具类 | BaseService, Utils |
| 配置重复 | 集中配置 | config.yaml |
| 数据定义重复 | 代码生成 | OpenAPI → DTO |
| 文档重复 | 从代码生成文档 | JavaDoc |

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [SRP](../single-responsibility-principle/) | SRP 拆分职责，DRY 合并重复知识 |
| [KISS](../kiss-principle/) | DRY 有时与 KISS 冲突，过度 DRY 增加复杂性 |
| [YAGNI](../yagni-principle/) | 不要为了未来可能的 DRY 而提前抽象 |

## 总结

**DRY 核心**：每个知识点只有一个权威表示。

**实践要点**：
- 区分代码重复、逻辑重复、知识重复
- 遵循三次法则，不要过早抽象
- 接受偶然重复和跨边界重复
- DRY 的反面不是 WET，而是**错误的抽象**
