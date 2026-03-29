# 策略模式应用诊断表单

## 📋 第1步: 需求诊断

### 是否真的需要策略模式?

回答以下4个问题：

1. **是否有2个或以上互不兼容的算法实现？**
   - [ ] 是 → 继续
   - [ ] 否 → 考虑简单条件语句

2. **这些算法在运行时需要动态切换吗？**
   - [ ] 是 → 继续
   - [ ] 否 → 考虑在编译期指定

3. **算法选择的条件会经常变化或增加新算法吗？**
   - [ ] 是 → 继续 (适合策略模式)
   - [ ] 否 → if-else可能足够

4. **当前代码中是否已经有大量的条件分支判断？**
   - [ ] 是 → 强烈推荐使用策略模式
   - [ ] 否 → 评估是否真的需要

**诊断结果**: 如果4个问题都是"是"，策略模式是最佳选择。3个"是"表示合适，2个或以下表示可能过度设计。

---

## 🎯 第2步: 实现方法选择矩阵

根据你的使用场景选择最合适的实现方法：

| 场景条件 | 直接注入法 | 工厂管理法 | 注解驱动法 | Lambda法 | 推荐指数 |
|---------|----------|----------|---------|---------|--------|
| 策略数 < 5 个，固定不变 | ✅ | - | - | ✅ | ⭐⭐ |
| 策略数 5-20 个，可能增加 | - | ✅ | - | - | ⭐⭐⭐ |
| 需要自动发现新策略 | - | - | ✅ | - | ⭐⭐⭐⭐ |
| 算法简单，无状态 | ✅ | - | - | ✅ | ⭐⭐⭐ |
| 算法复杂，有状态 | ✅ | ✅ | ✅ | - | ⭐⭐⭐⭐ |
| 需要异步执行 | ✅ | ✅ | ✅ | - | ⭐⭐⭐⭐ |
| 配置外部化 | - | ✅ | ✅ | - | ⭐⭐⭐⭐ |

**你选择的方法**: _________________________

---

## 📐 第3步: 实现规划

### 步骤1: 定义策略接口和Context

```java
// 策略接口 - 定义所有算法必须满足的契约
public interface PaymentStrategy {
    PaymentResult execute(PaymentContext context);
}

// Context 对象 - 包含策略执行所需的数据
public class PaymentContext {
    private double amount;
    private String orderId;
    private User user;
    private LocalDateTime timestamp;
    
    // 根据需要添加字段...
}

// 结果对象 - 返回统一的结果格式
public class PaymentResult {
    private boolean success;
    private String transactionId;
    private String errorMessage;
}
```

**需要实现的策略接口**: _________________________

**Context 需要的字段**:
- _________________________
- _________________________
- _________________________

### 步骤2: 实现具体的策略类

```java
public class CreditCardPayment implements PaymentStrategy {
    @Override
    public PaymentResult execute(PaymentContext context) {
        // TODO: 实现信用卡支付逻辑
        try {
            // 验证卡号
            validateCard(context);
            // 处理支付
            String txId = processPayment(context);
            // 返回结果
            return new PaymentResult(true, txId, null);
        } catch (Exception e) {
            return new PaymentResult(false, null, e.getMessage());
        }
    }
}

public class PayPalPayment implements PaymentStrategy {
    @Override
    public PaymentResult execute(PaymentContext context) {
        // TODO: 实现PayPal支付逻辑
    }
}

// 继续实现其他策略...
```

**需要实现的具体策略类**:
1. _________________________
2. _________________________
3. _________________________
4. _________________________

### 步骤3: 创建策略管理器/使用者

```java
// 方法A: 工厂模式管理（推荐）
public class PaymentStrategyFactory {
    private static final Map<String, PaymentStrategy> strategies = new HashMap<>();
    
    static {
        strategies.put("credit_card", new CreditCardPayment());
        strategies.put("paypal", new PayPalPayment());
        // 添加其他策略...
    }
    
    public static PaymentStrategy getStrategy(String type) {
        PaymentStrategy strategy = strategies.get(type);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown strategy: " + type);
        }
        return strategy;
    }
}

// 方法B: 直接依赖注入
public class PaymentProcessor {
    private PaymentStrategy strategy;
    
    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.strategy = strategy;
    }
    
    public PaymentResult processPayment(PaymentContext context) {
        return strategy.execute(context);
    }
}
```

**管理方式选择**: [ ] 工厂模式 [ ] 直接注入 [ ] 其他 _________

### 步骤4: 集成到现有系统

```java
// 在应用中使用
public class OrderService {
    private PaymentStrategyFactory factory;
    
    public void checkout(Order order, String paymentType) {
        PaymentContext context = new PaymentContext(order);
        PaymentStrategy strategy = factory.getStrategy(paymentType);
        PaymentResult result = strategy.execute(context);
        
        if (result.isSuccess()) {
            order.markAsPaid(result.getTransactionId());
        } else {
            throw new PaymentFailedException(result.getErrorMessage());
        }
    }
}
```

**集成点**: _________________________

**需要修改的现有代码**:
- _________________________
- _________________________
- _________________________

---

## ✅ 第4步: 测试规划

### 单元测试模板

```java
// 测试具体策略
@Test
public void testCreditCardPaymentSuccess() {
    PaymentContext context = new PaymentContext();
    context.setAmount(100.0);
    context.setCardNumber("1234567890123456");
    
    CreditCardPayment strategy = new CreditCardPayment();
    PaymentResult result = strategy.execute(context);
    
    assertTrue(result.isSuccess());
    assertNotNull(result.getTransactionId());
}

@Test
public void testCreditCardPaymentFailure() {
    PaymentContext context = new PaymentContext();
    context.setAmount(100.0);
    context.setCardNumber("invalid");
    
    CreditCardPayment strategy = new CreditCardPayment();
    PaymentResult result = strategy.execute(context);
    
    assertFalse(result.isSuccess());
    assertNotNull(result.getErrorMessage());
}

// 测试策略切换
@Test
public void testPaymentStrategySwitch() {
    PaymentProcessor processor = new PaymentProcessor();
    PaymentContext context = new PaymentContext();
    
    // 先用信用卡
    processor.setPaymentStrategy(new CreditCardPayment());
    PaymentResult result1 = processor.process(context);
    assertTrue(result1.isSuccess());
    
    // 切换到PayPal
    processor.setPaymentStrategy(new PayPalPayment());
    PaymentResult result2 = processor.process(context);
    assertTrue(result2.isSuccess());
}

// 测试工厂
@Test
public void testStrategyFactory() {
    PaymentStrategy strategy = PaymentStrategyFactory.getStrategy("credit_card");
    assertNotNull(strategy);
    assertTrue(strategy instanceof CreditCardPayment);
}

@Test(expected = IllegalArgumentException.class)
public void testFactoryUnknownStrategy() {
    PaymentStrategyFactory.getStrategy("unknown_payment");
}
```

**需要编写的测试**: 
- [ ] 每个具体策略的成功场景
- [ ] 每个具体策略的失败场景  
- [ ] 策略切换测试
- [ ] 工厂获取测试
- [ ] 边界条件测试

---

## ⚠️ 第5步: 常见陷阱检查清单

在提交代码前，确保避免以下陷阱：

| 陷阱 | 症状 | 检查方法 | 修复方案 |
|-----|------|--------|--------|
| **过度设计** | 只有1-2个策略，仍使用策略模式 | 数一数实际策略个数 | 如果<3个，考虑简化 |
| **Context膨胀** | Context有20+个字段，大多数策略只用2-3个 | 审查Context类 | 提取子Context或使用Builder |
| **优先级混乱** | 回退策略失败处理不当，导致支付丢失 | 检查异常处理 | 实现完整的异常链 |
| **内存泄漏** | 策略持有大对象引用导致回收困难 | 检查策略成员变量 | 使用弱引用或及时清理 |
| **线程安全问题** | 多线程环境下策略状态混乱 | 检查状态修改 | 使用不可变策略或同步访问 |
| **性能下降** | 多态调用开销过大（极少见） | Profiling工具测试 | 缓存策略实例 |

---

## 📊 第6步: 代码审查清单

完成实现后，进行以下代码审查：

### 策略接口审查
- [ ] 接口职责单一，不做过多事情
- [ ] 方法签名清晰，参数不超过3个  
- [ ] 返回类型统一
- [ ] 有明确的异常处理规约
- [ ] 接口文档完整

### 具体策略审查
- [ ] 每个策略只负责一种算法
- [ ] 策略间没有代码重复
- [ ] 策略创建失败时有清晰的错误信息
- [ ] 单元测试覆盖率 > 90%
- [ ] 没有硬编码的魔法值

### 使用者审查
- [ ] 策略选择逻辑清晰，易于维护
- [ ] 有异常处理（策略不存在、执行失败）
- [ ] 支持运行时添加新策略
- [ ] 支持策略回退或重试机制
- [ ] 记录了使用的策略（用于调试）

### 性能审查
- [ ] 频繁创建的策略对象带有缓存
- [ ] 没有不必要的策略复制
- [ ] Context对象序列化考虑
- [ ] 内存占用评估（若需要）

---

## 🚀 第7步: 实现时间线

| 阶段 | 任务 | 预计时间 | 状态 |
|-----|------|---------|------|
| 分析 | 定义策略接口和Context | 1-2小时 | [ ] |
| 实现 | 实现2-3个关键策略 | 4-6小时 | [ ] |
| 集成 | 集成到现有系统 | 2-3小时 | [ ] |
| 测试 | 编写和运行单元测试 | 2-4小时 | [ ] |
| 优化 | 性能优化和重构 | 1-2小时 | [ ] |
| 文档 | 编写使用文档 | 1小时 | [ ] |

**总预计**: 11-18小时

**团队分工**: _________________________

---

## 📝 实现笔记

在这里记录实现过程中的关键决策和学习：

**决策1**: 为什么选择这个实现方法?
_________________________________________________________________________

**决策2**: Context设计中做的权衡是什么?
_________________________________________________________________________

**高风险点**: 在实现中需要特别关注的地方?
_________________________________________________________________________

**可优化点**: 完成后可以进一步改进的地方?
_________________________________________________________________________

