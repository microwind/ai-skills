---
name: 状态模式
description: "对象状态变化时改变行为。在需要根据状态改变行为时使用。"
license: MIT
---

# 状态模式 (State Pattern)

## 概述

状态模式允许对象在其内部状态改变时改变它的行为。这个模式消除了大量的 if-else 分支判断。

**核心原则**: 状态对象化，行为随状态变化。

## 何时使用

**始终:**
- 对象行为随状态变化
- 多个状态转移
- 避免大量 if-else
- 工作流状态
- 订单状态

**触发短语:**
- "状态转移"
- "状态机"
- "条件分支"
- "工作流"

## 状态模式的优缺点

### 优点 ✅
- 避免大量条件分支
- 状态职责清晰
- 易于添加新状态
- 状态转移规则清晰

### 缺点 ❌
- 类数量增加
- 对于少状态过度设计
- 状态间通信需要小心

## 实现方式

### 订单状态
```java
public interface OrderState {
    void next(Order order);
    void previous(Order order);
    void print(Order order);
}

public class PendingState implements OrderState {
    @Override
    public void next(Order order) {
        order.setState(new ProcessingState());
    }
    
    @Override
    public void previous(Order order) {
        throw new IllegalStateException("Cannot go back");
    }
    
    @Override
    public void print(Order order) {
        System.out.println("Order status: Pending");
    }
}

public class Order {
    private OrderState state = new PendingState();
    
    public void goNext() {
        state.next(this);
    }
    
    public void setState(OrderState state) {
        this.state = state;
    }
}
```

## 典型应用场景

### 1. 订单工作流
- 待支付 -> 已支付 -> 处理中 -> 已发货 -> 已完成

### 2. 文件上传
- 就绪 -> 上传中 -> 已上传 -> 处理中 -> 完成

### 3. TCP 连接
- 关闭 -> 监听 -> 建立 -> 释放

### 4. 游戏角色
- 正常 -> 被冰冻 -> 被麻痹 -> 燃烧

## 状态 vs 策略

| 方面 | 状态 | 策略 |
|------|------|------|
| 目的 | 状态改变行为 | 算法选择 |
| 初始化 | 对象创建时 | 运行时 |
| 转移 | 由对象管理 | 由客户端管理 |
| 上下文 | 可改变 | 不改变 |

## 最佳实践

1. ✅ 状态职责清晰
2. ✅ 状态不存储数据
3. ✅ 文档说明状态转移
4. ✅ 考虑状态机框架

## 何时避免使用

- 状态少于 3 个
- 状态转移简单
- 不需要改变行为
