---
name: 策略模式
description: "定义一族可互换的算法。在需要灵活选择算法时使用。"
license: MIT
---

# 策略模式 (Strategy Pattern)

## 概述

策略模式定义一族可互换的算法，使得算法可独立于使用它们的客户端变化。这个模式使用多态性来选择算法。

**核心原则**: 算法封装，灵活选择。

## 何时使用

**始终:**
- 多个算法可选
- 算法需要切换
- 避免 if-else 分支
- 支付方式选择
- 排序算法选择

**触发短语:**
- "多种算法"
- "灵活切换"
- "避免条件分支"
- "算法选择"

## 策略模式的优缺点

### 优点 ✅
- 算法封装
- 灵活切换
- 避免条件分支
- 易于扩展

### 缺点 ❌
- 类数量增加
- 客户端需要知道所有策略
- 对于简单选择过度设计

## 实现方式

### 支付方式
```java
public interface PaymentStrategy {
    void pay(double amount);
}

public class CreditCardPayment implements PaymentStrategy {
    @Override
    public void pay(double amount) {
        System.out.println("Paying " + amount + " by credit card");
    }
}

public class PayPalPayment implements PaymentStrategy {
    @Override
    public void pay(double amount) {
        System.out.println("Paying " + amount + " via PayPal");
    }
}

public class ShoppingCart {
    private double total;
    private PaymentStrategy paymentStrategy;
    
    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
    }
    
    public void checkout() {
        paymentStrategy.pay(total);
    }
}
```

## 典型应用场景

### 1. 排序算法
- 快速排序
- 归并排序
- 冒泡排序

### 2. 压缩算法
- GZIP
- BZIP2
- DEFLATE

### 3. 验证规则
- 邮箱验证
- 手机验证
- 身份证验证

## 最佳实践

1. ✅ 策略接口清晰
2. ✅ 使用工厂创建策略
3. ✅ 支持运行时切换
4. ✅ 文档说明各策略差异

## 策略 vs State

| 方面 | 策略 | 状态 |
|------|------|------|
| 目的 | 选择算法 | 对象行为随状态变化 |
| 选择者 | 客户端 | 对象自身 |
| 存储 | 通常不存储 | 存储状态 |
| 切换 | 灵活 | 受限制 |

## 何时避免使用

- 只有一个算法
- 算法选择固定
- 算法切换频繁
