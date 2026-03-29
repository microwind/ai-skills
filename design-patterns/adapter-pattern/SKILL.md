---
name: 适配器模式
description: "将不兼容的接口转换为兼容的接口。在需要集成不同格式或系统时使用。"
license: MIT
---

# 适配器模式 (Adapter Pattern)

## 概述

适配器模式将一个接口转换成另一个接口，使得原本不兼容的类可以协作。这个模式解决接口不匹配的问题。

**核心原则**: 使不兼容的接口兼容，无需修改原始类。

## 何时使用

**始终:**
- 集成第三方库
- 统一不同数据格式
- 系统迁移和兼容
- 接口升级而需要兼容旧版本

**触发短语:**
- "第三方库接口不匹配"
- "需要统一接口"
- "系统集成"
- "格式转换"

## 适配器模式的优缺点

### 优点 ✅
- 提高类的复用性
- 增加类的透明性
- 灵活支持不同接口
- 符合开闭原则

### 缺点 ❌
- 代码复杂度增加
- 过多适配器导致系统混乱
- 性能可能有轻微影响

## 实现方式

### 类适配器
```java
public class PayPalAdapter extends PayPalPaymentGateway 
    implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        this.pay(amount);
    }
}
```

### 对象适配器
```java
public class PayPalAdapter implements PaymentProcessor {
    private PayPalPaymentGateway gateway;
    
    public PayPalAdapter(PayPalPaymentGateway gateway) {
        this.gateway = gateway;
    }
    
    @Override
    public void processPayment(double amount) {
        gateway.pay(amount);
    }
}
```

## 典型应用场景

### 1. 支付系统集成
```java
// 支付宝、微信、PayPal 使用统一接口
PaymentProcessor processor = new PayPalAdapter(paypal);
processor.processPayment(100.0);
```

### 2. 日志系统
```java
Logger logger = new Slf4jAdapter(logBackLogger);
logger.info("Message");
```

### 3. 数据格式转换
```java
JsonConverter json = new XmlToJsonAdapter(xmlData);
String jsonString = json.convert();
```

## 最佳实践

1. ✅ 区别于装饰器模式
2. ✅ 保持适配器简单  
3. ✅ 使用组合而非继承
4. ✅ 文档清明标注适配内容

## 何时避免使用

- 接口兼容不复杂
- 需要修改接口设计
- 适配的系统经常变化
