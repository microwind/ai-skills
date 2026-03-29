---
name: 工厂模式
description: "使用工厂创建对象而不指定具体类。在对象创建逻辑复杂或需要灵活切换实现时使用。"
license: MIT
---

# 工厂模式 (Factory Pattern)

## 概述

工厂模式定义一个创建对象的接口，让子类决定实例化哪个类。这个模式解耦了客户端代码与具体对象创建的关系。

**核心原则**: 向客户端隐藏对象创建的复杂性。

## 何时使用

**始终:**
- 对象创建逻辑复杂
- 需要支持多个实现
- 需要灵活的对象创建策略
- 数据库驱动程序选择
- 日志系统实现选择
- UI 组件创建

**触发短语:**
- "如何灵活创建不同类型的对象"
- "需要抽象对象创建"
- "支持多个实现"
- "简化复杂的创建逻辑"

## 工厂模式的优缺点

### 优点 ✅
- 松耦合设计
- 易于扩展新类型
- 集中化创建逻辑
- 支持多个实现

### 缺点 ❌
- 可能过度设计
- 增加代码复杂度
- 创建层次过多

## 实现方式

### 1. 简单工厂
```java
public class LoggerFactory {
    public static Logger createLogger(String type) {
        if ("FILE".equals(type)) {
            return new FileLogger();
        } else if ("CONSOLE".equals(type)) {
            return new ConsoleLogger();
        }
        return null;
    }
}
```

### 2. 工厂方法模式
```java
public abstract class MessageFactory {
    public abstract Message createMessage();
}

public class EmailMessageFactory extends MessageFactory {
    @Override
    public Message createMessage() {
        return new EmailMessage();
    }
}
```

## 常见场景

### 数据库连接
- MySQL 连接
- PostgreSQL 连接
- MongoDB 连接

### 支付系统
- 支付宝
- 微信
- 银联

### 消息队列
- RabbitMQ
- Kafka  
- Redis

## 最佳实践

1. ✅ 为每个创建类型提供工厂
2. ✅ 使用注册机制管理实现
3. ✅ 分离配置和创建逻辑
4. ✅ 支持工厂方法的继承

## 何时避免使用

- 只有单一实现
- 创建逻辑非常简单
- 不需要扩展的静态场景
