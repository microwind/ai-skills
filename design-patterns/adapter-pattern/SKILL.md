---
name: 适配器模式
description: "将一个类的接口转换为客户端期望的另一个接口，解决不兼容问题。"
license: MIT
---

# 适配器模式 (Adapter Pattern)

## 核心概念

**Adapter**是一种**结构型设计模式**，用于将一个不兼容的类的接口转换为客户端期望的接口。适配器充当"翻译"角色，使得原本无法协同工作的对象可以一起工作。

**核心原则**:
- 解决接口不兼容问题
- 无需修改原有接口即可集成新对象
- 促进代码复用，延长类的生命周期
- 支持第三方库的集成

**适配方式**:
- **类适配** (Class Adapter) - 通过继承实现
- **对象适配** (Object Adapter) - 通过组合实现 ⭐ 推荐

---

## 何时使用

**始终使用**:
- 需要使用第三方库但接口不兼容
- 旧系统与新系统集成
- 多个子系统接口不统一
- 希望不修改原有代码的情况下扩展功能

**触发短语**:
- "这个库的API不适配我们的系统"
- "需要集成遗留系统，但接口完全不同"
- "期望一个统一的接口来操作不同的实现"

**典型场景**:
| 场景 | 需适配的 | 目标接口 | 适配器 |
|------|----------|----------|--------|
| 支付网关整合 | Alipay, WeChat SDK | PaymentGateway | AlipayAdapter |
| 日期处理 | java.util.Date, LocalDateTime | DateConverter | DateAdapter |
| 数据库驱动 | MySQL, PostgreSQL | JdbcConnection | DbAdapter |
| UI组件库 | 第三方组件 | 内部UI接口 | ComponentAdapter |

---

## 4个实现方法

### 方法1: 对象适配器 (Object Adapter) ⭐推荐

通过组合原对象，适配其接口到目标接口。

```java
// 不兼容的现有接口 (第三方库)
public class LegacyPaymentSystem {
    public String processPayment(double amount) {
        return "支付宝处理: " + amount;
    }
}

// 目标接口 (系统期望)
public interface PaymentGateway {
    boolean pay(double amount);
    String getStatus();
}

// 对象适配器 - 通过组合
public class PaymentAdapter implements PaymentGateway {
    private LegacyPaymentSystem legacySystem;
    
    public PaymentAdapter(LegacyPaymentSystem system) {
        this.legacySystem = system;
    }
    
    @Override
    public boolean pay(double amount) {
        try {
            String result = legacySystem.processPayment(amount);
            System.out.println("适配结果: " + result);
            return result.contains("成功");
        } catch (Exception e) {
            return false;
        }
    }
    
    @Override
    public String getStatus() {
        return "已支付";
    }
}

// 使用
LegacyPaymentSystem legacy = new LegacyPaymentSystem();
PaymentGateway adapter = new PaymentAdapter(legacy);
adapter.pay(100.0);
```

**优点**: 灵活，不修改原类，可适配多个接口
**缺点**: 需要包装对象

### 方法2: 类适配器 (Class Adapter)

通过继承原类来适配。

```java
// 类适配器 - 通过继承
public class DirectPaymentAdapter extends LegacyPaymentSystem 
        implements PaymentGateway {
    
    @Override
    public boolean pay(double amount) {
        String result = super.processPayment(amount);
        return result.contains("成功");
    }
    
    @Override
    public String getStatus() {
        return "已处理";
    }
}

// 使用
PaymentGateway adapter = new DirectPaymentAdapter();
adapter.pay(100.0);
```

**优点**: 简单直接
**缺点**: 受限于Java单继承，不够灵活

### 方法3: 双向适配器 (Two-Way Adapter)

同时适配两个不兼容的接口。

```java
// 两个不兼容的接口
public interface ChinesePayment {
    String payWithUnifiedOrder(double amount);
}

public interface WeternPayment {
    boolean processPayment(double amount);
}

// 双向适配器
public class BidirectionalAdapter implements ChinesePayment, WeternPayment {
    private Object target;
    
    public BidirectionalAdapter(Object target) {
        this.target = target;
    }
    
    @Override
    public String payWithUnifiedOrder(double amount) {
        // 适配到 WeternPayment 接口
        if (target instanceof WeternPayment) {
            boolean success = ((WeternPayment) target).processPayment(amount);
            return success ? "成功" : "失败";
        }
        return "不支持";
    }
    
    @Override
    public boolean processPayment(double amount) {
        // 适配到 ChinesePayment 接口
        if (target instanceof ChinesePayment) {
            String result = ((ChinesePayment) target).payWithUnifiedOrder(amount);
            return result.contains("成功");
        }
        return false;
    }
}
```

### 方法4: 装饰改进的适配器

在适配的同时添加额外功能。

```java
public class EnhancedPaymentAdapter implements PaymentGateway {
    private LegacyPaymentSystem legacy;
    private List<PaymentInterceptor> interceptors = new ArrayList<>();
    
    public EnhancedPaymentAdapter(LegacyPaymentSystem legacy) {
        this.legacy = legacy;
    }
    
    public void addInterceptor(PaymentInterceptor interceptor) {
        interceptors.add(interceptor);
    }
    
    @Override
    public boolean pay(double amount) {
        // 前拦截器
        for (PaymentInterceptor interceptor : interceptors) {
            if (!interceptor.beforePay(amount)) {
                return false;
            }
        }
        
        // 适配的支付
        boolean result = legacyProcessPayment(amount);
        
        // 后拦截器
        for (PaymentInterceptor interceptor : interceptors) {
            interceptor.afterPay(amount, result);
        }
        
        return result;
    }
    
    private boolean legacyProcessPayment(double amount) {
        try {
            String response = legacy.processPayment(amount);
            return response.contains("成功");
        } catch (Exception e) {
            return false;
        }
    }
    
    @Override
    public String getStatus() { return "已处理"; }
}

public interface PaymentInterceptor {
    boolean beforePay(double amount);
    void afterPay(double amount, boolean success);
}

// 使用
EnhancedPaymentAdapter adapter = new EnhancedPaymentAdapter(legacy);
adapter.addInterceptor(new LoggingInterceptor());
adapter.addInterceptor(new ValidationInterceptor());
adapter.pay(100.0);
```

---

## 常见问题与解决方案

### ❌ 问题1: 适配器性能开销

**症状**: 频繁调用适配器，性能下降。

**根本原因**: 每次调用都经过一层包装，特别是双适配。

**解决方案**:

```java
// ✅ 缓存适配后的对象
public class CachedPaymentAdapter implements PaymentGateway {
    private Map<String, Object> cache = new ConcurrentHashMap<>();
    private LegacyPaymentSystem legacy;
    
    @Override
    public boolean pay(double amount) {
        String key = "payment_" + amount;
        Object cached = cache.get(key);
        
        if (cached != null) {
            return (Boolean) cached;
        }
        
        boolean result = legacyProcessPayment(amount);
        cache.put(key, result);
        return result;
    }
    
    private boolean legacyProcessPayment(double amount) {
        return legacy.processPayment(amount).contains("成功");
    }
    
    @Override
    public String getStatus() { return "已处理"; }
}
```

---

### ❌ 问题2: 接口不完全兼容

**症状**: 适配器无法完整适配所有功能。

**根本原因**: 被适配类功能集合与目标接口功能集合不匹配。

**解决方案**:

```java
// ✅ 分离适配与补充功能
public interface FullPaymentGateway extends PaymentGateway {
    boolean refund(String transactionId);
    List<Transaction> getHistory();
}

public class CompletePaymentAdapter implements FullPaymentGateway {
    private LegacyPaymentSystem legacy;
    private List<Transaction> localHistory = new ArrayList<>();
    
    @Override
    public boolean pay(double amount) {
        boolean result = legacy.processPayment(amount).contains("成功");
        if (result) {
            localHistory.add(new Transaction(amount, System.currentTimeMillis()));
        }
        return result;
    }
    
    @Override
    public boolean refund(String transactionId) {
        // 补充功能: 旧系统不支持退款
        localHistory.removeIf(t -> t.getId().equals(transactionId));
        return true;
    }
    
    @Override
    public List<Transaction> getHistory() {
        return new ArrayList<>(localHistory);
    }
    
    @Override
    public String getStatus() { return "已处理"; }
}
```

---

### ❌ 问题3: 第三方库版本变更导致适配器失效

**症状**: 升级第三方库后，适配器报错。

**根本原因**: 适配器强耦合于特定版本的第三方库。

**解决方案**:

```java
// ✅ 使用策略模式支持多版本
public interface PaymentAdapterStrategy {
    boolean pay(double amount);
}

public class AlipayV1Adapter implements PaymentAdapterStrategy {
    private LegacyPaymentSystem legacyV1;
    
    @Override
    public boolean pay(double amount) {
        return legacyV1.processPayment(amount).contains("成功");
    }
}

public class AlipayV2Adapter implements PaymentAdapterStrategy {
    private NewPaymentSystem newV2;
    
    @Override
    public boolean pay(double amount) {
        return newV2.executePayment(amount) == PaymentResult.SUCCESS;
    }
}

public class VersionAwareAdapter implements PaymentGateway {
    private PaymentAdapterStrategy strategy;
    
    public VersionAwareAdapter(String version) {
        if ("1.0".equals(version)) {
            this.strategy = new AlipayV1Adapter(...);
        } else {
            this.strategy = new AlipayV2Adapter(...);
        }
    }
    
    @Override
    public boolean pay(double amount) {
        return strategy.pay(amount);
    }
    
    @Override
    public String getStatus() { return "已处理"; }
}
```

---

### ❌ 问题4: 多个不兼容接口混合导致混乱

**症状**: 系统中混用不同的支付接口，代码难以维护。

**根本原因**: 缺陷统一的适配策略。

**解决方案**:

```java
// ✅ 使用层次适配器
public abstract class BasePaymentAdapter implements PaymentGateway {
    protected abstract void executePayment(double amount);
    protected abstract String extractStatus();
    
    @Override
    public final boolean pay(double amount) {
        try {
            executePayment(amount);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    @Override
    public final String getStatus() {
        return extractStatus();
    }
}

public class SpecificAlipayAdapter extends BasePaymentAdapter {
    private LegacyPaymentSystem system;
    
    @Override
    protected void executePayment(double amount) {
        system.processPayment(amount);
    }
    
    @Override
    protected String extractStatus() {
        return "已支付";
    }
}
```

---

## 类适配 vs 对象适配对比

| 方面 | 类适配 | 对象适配 |
|------|--------|---------|
| 实现方式 | 继承 | 组合 |
| 灵活性 | 低 (单一父类) | 高 |
| 多适配 | 不支持 | 支持 |
| 性能 | 略好 | 略差 |
| 推荐度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 最佳实践

✅ **优先对象适配** - 灵活性更好  
✅ **隔离第三方库** - 通过适配器屏蔽变化  
✅ **单一职责** - 适配器只负责接口转换  
✅ **缓存策略** - 高频调用时缓存适配结果  
✅ **版本管理** - 支持多版本第三方库  
✅ **异常处理** - 完整的错误处理和日志  

---

## 何时避免

❌ 简单的接口转换可以直接修改源类  
❌ 不兼容问题源于设计缺陷，应该重构而非适配  
❌ 过度适配导致代码复杂度增加  

---

## 真实案例

### 案例1: 支付网关整合

不同支付商 (支付宝、微信、Stripe) 接口完全不同，使用适配器统一为内部接口。

### 案例2: 日期处理库

java.util.Date 与 java.time.LocalDateTime 接口不兼容，适配器转换。

### 案例3: 旧系统集成

集成20年前的遗留系统，现代系统与之通信需要适配器转换。
