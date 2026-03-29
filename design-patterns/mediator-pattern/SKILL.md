---
name: 中介者模式
description: "定义一个对象来封装一组对象间的交互。在需要协调多个对象时使用。"
license: MIT
---

# 中介者模式 (Mediator Pattern)

## 概述

中介者模式定义了一个对象来封装一组对象间的交互，促进了松耦合。这个模式使各对象间不需要显示相互关联。

**核心原则**: 集中交互，解耦对象。

## 何时使用

**始永:**
- 多个对象通信复杂
- 对象间耦合度高
- 需要集中管理交互
- 对话框内多控件
- 聊天室

**触发短语:**
- "多对象交互"
- "耦合度高"
- "集中管理"
- "中介者"

## 中介者的优缺点

### 优点 ✅
- 分离对象间通信
- 集中管理交互
- 易于扩展
- 降低耦合度

### 缺点 ❌
- 中介者可能复杂
- 性能可能受影响
- 违反单一职责原则

## 实现方式

### 聊天室
```java
public interface Mediator {
    void sendMessage(String message, User from, User to);
}

public class ChatRoom implements Mediator {
    private List<User> users = new ArrayList<>();
    
    public void register(User user) {
        users.add(user);
        user.setMediator(this);
    }
    
    @Override
    public void sendMessage(String message, User from, User to) {
        System.out.println(from.getName() + " sends to " + 
            to.getName() + ": " + message);
    }
}

public class User {
    private String name;
    private Mediator mediator;
    
    public void send(String message, User to) {
        mediator.sendMessage(message, this, to);
    }
}
```

## 典型应用场景

### 1. 对话框
- 按钮、输入框、标签交互

### 2. 聊天应用
- 用户消息交互

### 3. 空中交通管理
- 飞机与控制塔交互

### 4. GUI 框架
- 组件交互管理

## 最佳实践

1. ✅ 中介者职责清晰
2. ✅ 支持灵活的消息格式
3. ✅ 提供中介者接口
4. ✅ 避免中介者过度复杂

## 何时避免使用

- 只有两个对象通信
- 交互很简单
- 不需要集中管理
