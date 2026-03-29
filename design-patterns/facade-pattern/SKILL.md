---
name: 外观模式
description: "提供高层的统一接口。在需要简化复杂系统的接口时使用。"
license: MIT
---

# 外观模式 (Facade Pattern)

## 概述

外观模式提供一个统一的高层接口，用来访问子系统中的一群接口。外观模式定义了一个高层接口，让客户端不需要直接与系统交互。

**核心原则**: 简化复杂系统，提供统一入口。

## 何时使用

**始终:**
- 系统复杂度高
- 需要简化客户端接口
- 子系统独立性强
- 需要分层建筑

**触发短语:**
- "系统太复杂"
- "需要简化接口"
- "需要统一入口"
- "子系统解耦"

## 外观模式的优缺点

### 优点 ✅
- 简化客户端代码
- 降低系统复杂度
- 解耦客户端和子系统
- 提供统一入口

### 缺点 ❌
- 可能过度封装
- 隐藏子系统细节
- 不支持细粒度控制

## 实现方式

### 银行转账系统
```java
public class BankFacade {
    private AccountService accountService;
    private FeeService feeService;
    private NotificationService notificationService;
    
    public boolean transfer(String from, String to, double amount) {
        if (!accountService.validateAccount(from)) {
            return false;
        }
        double fee = feeService.calculateFee(amount);
        accountService.debit(from, amount + fee);
        accountService.credit(to, amount);
        notificationService.notify(from, to, amount);
        return true;
    }
}
```

## 典型应用场景

### 1. 音乐播放系统
```java
public class HomeTheaterFacade {
    private Projector projector;
    private SoundSystem soundSystem;
    private PlayerApplication application;
    
    public void watchMovie(String movie) {
        projector.on();
        soundSystem.on();
        application.play(movie);
    }
    
    public void stopMovie() {
        projector.off();
        soundSystem.off();
        application.stop();
    }
}
```

### 2. 数据库操作
```java
public class DatabaseFacade {
    public void saveEntity(Entity entity) {
        // 数据验证
        // 数据转换
        // 数据持久化
        // 缓存更新
        // 事件发送
    }
}
```

### 3. Spring 框架
```java
// ResourceLoaderFacade 统一资源加载
Resource resource = new ClassPathResource("config.properties");
```

## 最佳实践

1. ✅ 外观本身不实现逻辑
2. ✅ 提供简洁的 API
3. ✅ 支持灵活访问子系统
4. ✅ 文档清晰说明职责

## 何时避免使用

- 客户端需要细粒度控制
- 子系统只有一个
- 系统相对简单
