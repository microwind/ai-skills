---
name: 责任链模式
description: "将请求沿着链传递。在需要多处理程序处理请求时使用。"
license: MIT
---

# 责任链模式 (Chain of Responsibility Pattern)

## 概述

责任链模式使多个对象都有机会处理请求，从而避免请求的发送者和接收者之间的耦合。将这些对象连成一条链，并沿着这条链传递请求，直到有一个对象处理它为止。

**核心原则**: 请求传递链，灵活处理。

## 何时使用

**始终:**
- 多个处理程序可处理请求
- 处理程序顺序可变
- 请求不知道处理程序
- 日志级别处理
- 请求审批流程

**触发短语:**
- "多级处理"
- "批准流程"
- "日志级别"
- "责任链"

## 责任链的优缺点

### 优点 ✅
- 请求发送者和接收者解耦
- 灵活组合处理程序
- 支持动态链构建
- 易于扩展处理程序

### 缺点 ❌
- 调试困难
- 处理程序可能被跳过
- 性能可能受影响
- 链可能太长

## 实现方式

### 请求批准流程
```java
public abstract class Approver {
    protected Approver successor;
    
    public void setSuccessor(Approver successor) {
        this.successor = successor;
    }
    
    public abstract void processRequest(Request request);
}

public class Manager extends Approver {
    @Override
    public void processRequest(Request request) {
        if (request.getAmount() <= 10000) {
            System.out.println("Manager approved");
        } else if (successor != null) {
            successor.processRequest(request);
        }
    }
}

public class Director extends Approver {
    @Override
    public void processRequest(Request request) {
        if (request.getAmount() <= 50000) {
            System.out.println("Director approved");
        } else if (successor != null) {
            successor.processRequest(request);
        }
    }
}
```

## 典型应用场景

### 1. 日志系统
```java
logger.setNext(consoleLogger)
    .setNext(fileLogger)
    .setNext(networkLogger);
```

### 2. HTTP 请求处理
```java
// Servlet Filter 链
// 认证 -> 授权 -> 业务逻辑
```

### 3. 事件处理
```java
handler1.setNext(handler2)
    .setNext(handler3);
handler1.handle(event);
```

### 4. 异常处理
```java
// 应用异常 -> 中间件异常 -> 通用异常
```

## 最佳实践

1. ✅ 处理程序职责清晰
2. ✅ 支持动态链构建
3. ✅ 提供链构建器
4. ✅ 文档说明处理顺序

## 何时避免使用

- 只有一个处理程序
- 处理程序顺序固定
- 所有请求都已知
