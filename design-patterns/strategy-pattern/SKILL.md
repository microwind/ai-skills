---
name: 策略模式
description: "定义一族可互换的算法。在需要灵活选择算法时使用。"
license: MIT
---

# 策略模式 (Strategy Pattern)

## 概述

策略模式定义一族可互换的算法，使得算法可独立于使用它们的客户端变化。这是行为型模式中最强大的多态应用，通过将算法封装为对象，实现运行时灵活选择和动态替换。

**核心原则**:
1. **算法族封装**: 将相关的一族算法独立封装
2. **互换性**: 这些算法可以相互替换
3. **独立变化**: 算法变化独立于使用者变化
4. **运行时选择**: 在运行时决定使用哪个算法

## 4个完美的使用场景

### 1. 支付系统 (支付渠道选择)
电商平台需要支持多种支付方式（信用卡、PayPal、微信、支付宝）且方式持续增加。不使用策略模式会导致PaymentProcessor中的if-else分支逐年膨胀。

### 2. 排序/搜索系统 (算法选择)
根据数据量、场景选择不同排序（快速排序、归并排序、堆排序）或搜索（二分查找、线性查找、哈希查找）。Java Collections.sort()允许传入Comparator即是此模式应用。

### 3. 数据压缩/加密 (编码算法选择)
媒体处理系统支持多种压缩（GZIP、BZIP2、DEFLATE）或加密（AES、RSA、MD5）算法。用户配置参数指定使用哪个算法。

### 4. 验证/计费规则 (业务规则选择)
不同用户、订单类型适用不同的验证规则或计费策略。运营人员通过配置表指定用户适用哪个策略。

### 5. 路由/分配策略 (调度算法选择)
负载均衡器选择不同策略（轮询、最小连接、IP哈希、随机）；任务队列选择任务分配算法（FIFO、优先级、基于资源）。

### 6. 价格/折扣计算 (定价策略)
电商平台针对不同用户等级（VIP、普通、新用户）应用不同折扣策略，且策略需根据市场变化快速调整。

## 核心优缺点分析

### 优点 ✅

**1. 开闭原则 (Open/Closed Principle)**
```java
// 添加新支付方式只需新增类，不修改PaymentProcessor
public class BitcoinPayment implements PaymentStrategy {
    @Override
    public PaymentResult pay(PaymentContext context) {
        // 比特币支付逻辑
    }
}
// PaymentProcessor无需修改就能支持比特币
```

**2. 消除条件分支**
```java
// ❌ 不使用策略模式：条件分支爆炸
public class PaymentProcessor {
    public void processPayment(String paymentType, double amount) {
        if ("credit_card".equals(paymentType)) {
            processCreditCard(amount);
        } else if ("paypal".equals(paymentType)) {
            processPayPal(amount);
        } else if ("alipay".equals(paymentType)) {
            processAlipay(amount);
        } else if ("wechat".equals(paymentType)) {
            processWechat(amount);
        } else if ("bitcoin".equals(paymentType)) {
            processBitcoin(amount);
        } // ... 每增加一个支付方式就添加一个分支
    }
}

// ✅ 使用策略模式：干净、可扩展
private Map<String, PaymentStrategy> strategies = new HashMap<>();
strategies.put("credit_card", new CreditCardPayment());
strategies.put("paypal", new PayPalPayment());
// 可以在运行时添加新策略
strategies.put("bitcoin", new BitcoinPayment());

public void processPayment(String paymentType, double amount) {
    PaymentStrategy strategy = strategies.get(paymentType);
    if (strategy != null) {
        strategy.pay(amount);
    }
}
```

**3. 运行时灵活切换**
```java
// 同一个订单可以在秒出前切换支付方式
PaymentContext context = order.getPaymentContext();
if (paymentFailed) {
    context.setStrategy(new AlternativePaymentStrategy());
    context.pay(); // 使用备选方案
}
```

**4. 独立测试**
```java
// 每个支付策略独立测试，相互不影响
@Test
public void testCreditCardPaymentStrategy() {
    PaymentStrategy strategy = new CreditCardPayment();
    PaymentResult result = strategy.pay(new PaymentContext(...));
    assertTrue(result.isSuccess());
}

@Test
public void testPayPalPaymentStrategy() {
    // 完全独立的测试
}
```

### 缺点 ❌

**1. 类数量增加**
```java
// 此模式下，每个算法都是一个类
CreditCardPayment.java
PayPalPayment.java
AlipayPayment.java
WechatPayment.java
GooglePayPayment.java
ApplePayPayment.java
BankTransferPayment.java
CryptoPayment.java
// ... 20+ 类文件
```

**2. 客户端必须理解所有策略**
```java
// 客户端不得不知道所有支付策略并选择合适的
if (user.isPremium()) {
    processor.setStrategy(new ExpressPaymentStrategy()); // 需要知道有快速支付
} else if (user.isStudent()) {
    processor.setStrategy(new StudentDiscountPaymentStrategy()); // 需要知道学生策略
} else {
    processor.setStrategy(new StandardPaymentStrategy());
}
```

**3. 对简单场景过度设计**
```java
// ❌ 不必要的策略模式使用
public interface StringFormatStrategy {
    String format(String input);
}
public class UpperCaseFormat implements StringFormatStrategy {
    public String format(String input) { return input.toUpperCase(); }
}
public class LowerCaseFormat implements StringFormatStrategy {
    public String format(String input) { return input.toLowerCase(); }
}
// 这样简单可以用Lambda直接处理

// ✅ 正确做法
Function<String, String> formatter = String::toUpperCase;
```

**4. 策略间数据共享困难**
```java
// ❌ 多个策略需要同一个上下文的多个字段
public interface DiscountStrategy {
    double calculateDiscount(double price, int quantity);
}

public class VolumeDiscount implements DiscountStrategy {
    @Override
    public double calculateDiscount(double price, int quantity) {
        // 需要访问discount_threshold, min_quantity等参数
        // 需要访问user.level信息
        // 需要访问季节性规则等
    }
}
// 传递大量参数会污染接口
```

## 4个实现方法对比

| 方法 | 适用场景 | 优点 | 缺点 | 选择指数 |
|------|--------|------|------|---------|
| **直接注入法** | 简单场景，策略数<5 | 直观、易懂 | 不支持工厂、配置 | ⭐⭐ |
| **工厂管理法** | 中等场景，策略数5-20 | 集中管理、动态注册 | 工厂类维护成本 | ⭐⭐⭐⭐ |
| **注解驱动法** | 复杂场景，需动态注册 | 解耦最彻底、可插拔 | 反射开销、学习曲线 | ⭐⭐⭐⭐⭐ |
| **Lambda表达式法** | 简单算法，无状态 | 代码最简洁 | 不支持复杂逻辑、难以重用 | ⭐⭐⭐ |

### 方法1: 直接注入法（Simple Injection）
```java
// 最直接的策略选择方式，适合策略较少的场景
public interface PaymentStrategy {
    PaymentResult execute(PaymentContext context);
}

public class PaymentProcessor {
    private PaymentStrategy strategy;
    
    public PaymentProcessor(PaymentStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void setStrategy(PaymentStrategy newStrategy) {
        this.strategy = newStrategy;
    }
    
    public PaymentResult process(PaymentContext context) {
        return strategy.execute(context);
    }
}

// 使用
PaymentProcessor processor = new PaymentProcessor(new CreditCardPayment());
processor.process(context);

// 切换策略
processor.setStrategy(new PayPalPayment());
processor.process(context);
```

### 方法2: 工厂管理法（Strategy Factory）
```java
// 集中管理所有策略，支持动态注册，最常用的方法
public class PaymentStrategyFactory {
    private static final Map<String, PaymentStrategy> strategies = new HashMap<>();
    
    static {
        // 初始注册
        register("credit_card", new CreditCardPayment());
        register("paypal", new PayPalPayment());
        register("alipay", new AlipayPayment());
    }
    
    public static void register(String key, PaymentStrategy strategy) {
        strategies.put(key, strategy);
    }
    
    public static PaymentStrategy getStrategy(String key) {
        PaymentStrategy strategy = strategies.get(key);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown payment strategy: " + key);
        }
        return strategy;
    }
    
    public static Set<String> getAvailableStrategies() {
        return strategies.keySet();
    }
}

// 使用
PaymentStrategy strategy = PaymentStrategyFactory.getStrategy("paypal");
processor.setStrategy(strategy);
processor.process(context);

// 运行时添加新策略
PaymentStrategyFactory.register("bitcoin", new BitcoinPayment());
```

### 方法3: 注解驱动法（Annotation-Driven）
```java
// 最高级的方式，结合Spring或其他DI框架，支持自动发现
@PaymentStrategyMarker(name = "credit_card")
public class CreditCardPayment implements PaymentStrategy {
    @Override
    public PaymentResult execute(PaymentContext context) {
        // 实现支付逻辑
    }
}

@PaymentStrategyMarker(name = "paypal")
public class PayPalPayment implements PaymentStrategy {
    @Override
    public PaymentResult execute(PaymentContext context) {
        // 实现支付逻辑
    }
}

@Component
public class PaymentStrategyRegistry {
    private final Map<String, PaymentStrategy> strategies = new HashMap<>();
    
    @Autowired
    public PaymentStrategyRegistry(List<PaymentStrategy> allStrategies) {
        allStrategies.forEach(strategy -> {
            PaymentStrategyMarker marker = strategy.getClass()
                .getAnnotation(PaymentStrategyMarker.class);
            if (marker != null) {
                strategies.put(marker.name(), strategy);
            }
        });
    }
    
    public PaymentStrategy getStrategy(String name) {
        return strategies.get(name);
    }
}

// 自动发现+注入，无需手动注册
```

### 方法4: Lambda表达式法（Functional Style）
```java
// Java 8+ 的现代做法，适合无状态的简单算法
public class PaymentManager {
    private Map<String, Function<PaymentContext, PaymentResult>> strategies;
    
    public PaymentManager() {
        strategies = new HashMap<>();
        
        // 使用Lambda定义策略
        strategies.put("credit_card", ctx -> {
            System.out.println("Processing credit card: " + ctx.getAmount());
            return new PaymentResult(true, "Credit card processed");
        });
        
        strategies.put("paypal", ctx -> {
            System.out.println("Redirecting to PayPal for: " + ctx.getAmount());
            return new PaymentResult(true, "PayPal processed");
        });
        
        strategies.put("alipay", ctx -> {
            System.out.println("Processing Alipay: " + ctx.getAmount());
            return new PaymentResult(true, "Alipay processed");
        });
    }
    
    public PaymentResult process(String paymentType, PaymentContext context) {
        Function<PaymentContext, PaymentResult> strategy = strategies.get(paymentType);
        if (strategy == null) {
            throw new IllegalArgumentException("Unknown payment type: " + paymentType);
        }
        return strategy.apply(context);
    }
}

// 使用
PaymentManager manager = new PaymentManager();
PaymentResult result = manager.process("credit_card", context);
```

## 4个常见问题 + 完整解决方案

### 问题1: 策略间数据共享 (Context Pollution)
**症状**: 不同策略需要访问不同的上下文参数，导致接口变得臃肿
```java
// ❌ 问题代码：接口膨胀
public interface DiscountStrategy {
    double calculate(
        double basePrice,
        int quantity,
        UserType userType,
        Season season,
        boolean isHoliday,
        int dayOfWeek,
        double inventoryLevel
    );
}
// 每个策略只需要其中2-3个参数，其余都被浪费

// ✅ 解决方案1：使用Context对象
public class DiscountContext {
    private double basePrice;
    private int quantity;
    private UserType userType;
    private Season season;
    private boolean isHoliday;
    private int dayOfWeek;
    private double inventoryLevel;
    
    // Getters
    public double getBasePrice() { return basePrice; }
    public int getQuantity() { return quantity; }
    // ... 其他getters
}

public interface DiscountStrategy {
    double calculate(DiscountContext context);
}

public class VolumeDiscount implements DiscountStrategy {
    @Override
    public double calculate(DiscountContext context) {
        return context.getBasePrice() * context.getQuantity() * 0.1;
    }
}

public class SeasonalDiscount implements DiscountStrategy {
    @Override
    public double calculate(DiscountContext context) {
        return context.getSeason() == Season.SUMMER ? 
            context.getBasePrice() * 0.15 : 
            context.getBasePrice() * 0.05;
    }
}
```

### 问题2: 策略执行失败回退 (Fallback Strategy)
**症状**: 首选支付方式失败，需要自动切换到备选方案
```java
// ❌ 问题代码：硬编码回退逻辑
public void processPayment(Order order) {
    try {
        payWithCreditCard(order);
    } catch (PaymentException e) {
        try {
            payWithPayPal(order);
        } catch (PaymentException e2) {
            try {
                payWithAlipay(order);
            } catch (PaymentException e3) {
                throw new FinalPaymentException();
            }
        }
    }
}

// ✅ 解决方案：链式策略管理
public class PaymentStrategyChain {
    private List<PaymentStrategy> strategies = new ArrayList<>();
    
    public void addStrategy(PaymentStrategy strategy) {
        strategies.add(strategy);
    }
    
    public PaymentResult processWithFallback(PaymentContext context) {
        for (PaymentStrategy strategy : strategies) {
            try {
                return strategy.execute(context);
            } catch (PaymentException e) {
                // 记录失败，继续尝试下一个
                logger.warn("Strategy failed: {}, trying next...", 
                    strategy.getClass().getSimpleName(), e);
                continue;
            }
        }
        throw new AllPaymentStrategiesFailedException();
    }
}

// 使用
PaymentStrategyChain chain = new PaymentStrategyChain();
chain.addStrategy(new CreditCardPayment());
chain.addStrategy(new PayPalPayment());
chain.addStrategy(new AlipayPayment());

PaymentResult result = chain.processWithFallback(context);
```

### 问题3: 动态策略选择条件复杂 (Complex Selection Logic)
**症状**: 选择哪个策略的逻辑本身很复杂，经常变更
```java
// ❌ 问题代码：选择逻辑繁复
public class PaymentStrategySelector {
    public static PaymentStrategy selectStrategy(Order order, User user) {
        if (user.isPremium() && order.getAmount() > 1000) {
            return new ExpressPaymentStrategy();
        } else if (user.isInternational() && order.getAmount() > 5000) {
            return new InternationalLoanPaymentStrategy();
        } else if (order.getAmount() < 100 && order.isBulk()) {
            return new BulkDiscountPaymentStrategy();
        } else if (LocalDate.now().getMonth() == Month.DECEMBER) {
            return new HolidayPaymentStrategy();
        } else if (user.getLoyaltyPoints() > 1000) {
            return new PointsExchangePaymentStrategy();
        } else {
            return new StandardPaymentStrategy();
        }
    }
}

// ✅ 解决方案：提取为策略选择策略
public interface StrategySelector {
    PaymentStrategy select(Order order, User user);
}

public class RuleBasedStrategySelector implements StrategySelector {
    private List<StrategySelectionRule> rules = new ArrayList<>();
    
    public RuleBasedStrategySelector() {
        rules.add(new PremiumUserHighAmountRule());
        rules.add(new InternationalLargeOrderRule());
        rules.add(new BulkOrderRule());
        rules.add(new HolidaySeasonRule());
        rules.add(new LoyaltyPointsRule());
    }
    
    @Override
    public PaymentStrategy select(Order order, User user) {
        for (StrategySelectionRule rule : rules) {
            if (rule.matches(order, user)) {
                return rule.getStrategy();
            }
        }
        return new StandardPaymentStrategy();
    }
}

public interface StrategySelectionRule {
    boolean matches(Order order, User user);
    PaymentStrategy getStrategy();
}

public class PremiumUserHighAmountRule implements StrategySelectionRule {
    @Override
    public boolean matches(Order order, User user) {
        return user.isPremium() && order.getAmount() > 1000;
    }
    
    @Override
    public PaymentStrategy getStrategy() {
        return new ExpressPaymentStrategy();
    }
}
```

### 问题4: 策略执行异步化 (Async Strategy Execution)
**症状**: 某些策略需要异步执行（如多渠道支付验证），某些需要同步
```java
// ❌ 问题代码：混合同步异步导致复杂性
public PaymentResult processPayment(PaymentContext context) {
    if (context.getStrategyType().equals("bank_transfer")) {
        // 等待实时验证
        return bankStrategySync();
    } else if (context.getStrategyType().equals("blockchain")) {
        // 需要异步监听交易确认
        return blockchainStrategyAsync();
    }
}

// ✅ 解决方案：统一的异步策略接口
public interface PaymentStrategy {
    CompletableFuture<PaymentResult> executeAsync(PaymentContext context);
    
    // 同步包装器
    default PaymentResult execute(PaymentContext context) {
        try {
            return executeAsync(context).get(30, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            throw new PaymentTimeoutException(e);
        }
    }
}

public class BlockchainPaymentStrategy implements PaymentStrategy {
    @Override
    public CompletableFuture<PaymentResult> executeAsync(PaymentContext context) {
        return CompletableFuture.supplyAsync(() -> {
            // 提交交易到区块链
            String txId = submitToBlockchain(context);
            
            // 异步监听确认
            return waitForBlockchainConfirmation(txId, 30);
        });
    }
}

public class CreditCardPaymentStrategy implements PaymentStrategy {
    @Override
    public CompletableFuture<PaymentResult> executeAsync(PaymentContext context) {
        // 信用卡支付快速完成，直接返回
        return CompletableFuture.completedFuture(
            executeImmediately(context)
        );
    }
}

// 使用
PaymentStrategy strategy = factory.getStrategy("blockchain");
strategy.executeAsync(context)
    .thenAccept(result -> logger.info("Payment result: {}", result))
    .exceptionally(error -> {
        logger.error("Payment failed", error);
        return null;
    });
```

## 最佳实践指南

### 1️⃣ 策略接口设计要精准
```java
// ❌ 接口太宽泛
public interface Strategy {
    void execute(Object... inputs);
}

// ✅ 接口职责清晰
public interface SortingStrategy {
    <T extends Comparable<T>> List<T> sort(List<T> items);
}

public interface DiscountStrategy {
    double calculateDiscount(DiscountContext context);
}
```

### 2️⃣ 使用工厂模式管理策略生命周期
```java
// ✅ 工厂集中管理
@Component
public class StrategyFactory {
    @Autowired
    private List<PaymentStrategy> strategies;
    
    @PostConstruct
    private void registerStrategies() {
        strategies.forEach(s -> {
            PaymentMethod method = s.getClass()
                .getAnnotation(PaymentMethod.class);
            if (method != null) {
                registry.register(method.value(), s);
            }
        });
    }
}
```

### 3️⃣ 提供策略元数据和发现机制
```java
// ✅ 策略可发现、可配置
public interface PaymentStrategy {
    PaymentResult execute(PaymentContext context);
    
    StrategyMetadata getMetadata();
}

public class StrategyMetadata {
    private String name;
    private String description;
    private double minAmount;
    private double maxAmount;
    private Set<String> supportedCountries;
    private Set<String> supportedCurrencies;
}

// 客户端可查询支持哪些策略
Set<StrategyMetadata> available = factory.getAvailableStrategies();
```

### 4️⃣ 支持策略间的委托和组合
```java
// ✅ 组合多个策略实现更复杂逻辑
public class CompositeDiscountStrategy implements DiscountStrategy {
    private List<DiscountStrategy> strategies;
    private DiscountCombination combination; // SUM, MAX, MULTIPLY
    
    @Override
    public double calculate(DiscountContext context) {
        List<Double> results = strategies.stream()
            .map(s -> s.calculate(context))
            .collect(toList());
        
        return combination.combine(results);
    }
}

// 使用
DiscountStrategy composite = new CompositeDiscountStrategy(
    Arrays.asList(
        new VolumeDiscount(),
        new LoyaltyDiscount(),
        new SeasonalDiscount()
    ),
    DiscountCombination.SUM
);
```

### 5️⃣ 性能监控和策略选择优化
```java
// ✅ 记录策略性能，动态调整
@Aspect
public class StrategyPerformanceMonitor {
    @Around("execution(* *.PaymentStrategy.execute(..))")
    public Object monitorPerformance(ProceedingJoinPoint pjp) throws Throwable {
        long startTime = System.currentTimeMillis();
        try {
            Object result = pjp.proceed();
            long duration = System.currentTimeMillis() - startTime;
            
            String strategyName = pjp.getTarget().getClass().getSimpleName();
            metrics.recordStrategyDuration(strategyName, duration);
            
            return result;
        } catch (Exception e) {
            metrics.recordStrategyFailure(pjp.getTarget().getClass().getSimpleName());
            throw e;
        }
    }
}
```

## 与其他模式的关系

| 相关模式 | 关系 | 何时选择 |
|--------|------|--------|
| **State** | 都改变对象行为，但Strategy是客户端选择，State是对象自身变化 | 行为依赖外部条件→Strategy；行为随对象生命周期→State |
| **Command** | 都将请求参数化，但Strategy是"如何做"，Command是"做什么" | 需要灵活选择执行方式→Strategy；需要队列化/撤销/重放→Command |
| **Factory** | 通常配套使用，Factory负责创建Strategy | 需要集中管理策略实例 |
| **Decorator** | Decorator添加新行为，Strategy替换算法 | 需要扩展而不改变接口→Decorator；需要切换算法→Strategy |
| **Template Method** | 都使用多态，但Template在基类中定义骨架，Strategy在独立类中 | 需要通用模版→Template Method；需要完全替换算法→Strategy |

## 多语言实现考量

### Java特性应用
- 使用`Function<T, R>`替代简单策略接口
- 利用`CompletableFuture`支持异步策略
- 使用`@Qualifier`进行基于注解的策略注入（Spring框架）

### Python考量
- 函数优先哲学：大多数情况用函数而不是类
- `duck typing`强大，类型检查需要谨慎
- 支持一级函数的方法特别自然

### TypeScript/JavaScript考量
- 支持高阶函数，可完全使用函数替代类
- 对象字面量可作为策略集合
- 动态类型使策略创建更灵活但需要运行时检查

## 何时避免使用

- ❌ **只有一个算法**: if-else或简单条件更轻量
- ❌ **算法选择固定不变**: 编译期确定算法，不必运行时选择
- ❌ **算法极其复杂且有状态**: 考虑State模式或更复杂的架构
- ❌ **策略间需要大量共享状态**: 会导致Context对象过度膨胀
- ❌ **性能极其关键**: 多态调用有微小开销（通常可忽略）
