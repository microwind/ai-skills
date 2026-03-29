---
name: 单例模式
description: "确保类只有一个实例，并提供全局访问点。在设计全局配置、日志系统、连接池等单一实例应用时使用。"
license: MIT
---

# 单例模式 (Singleton Pattern)

## 概述

单例模式确保一个类只有一个实例，并提供一个全局访问点。这个模式在需要控制资源共享或全局状态时非常有用。

**核心原则**: 某些类应该只有一个实例，提供全局却受控的访问。

## 何时使用

**始终:**
- 需要全局配置管理
- 数据库连接池
- 日志系统
- 缓存管理
- 应用程序范围的对象

**触发短语:**
- "需要只有一个实例的类"
- "全局配置访问"
- "共享资源管理"
- "连接池"

## 单例模式的优缺点

### 优点 ✅
- 确保类只有一个实例
- 提供全局访问点
- 延迟初始化（按需创建）
- 线程安全的全局访问

### 缺点 ❌
- 难以单元测试（全局状态）
- 隐藏依赖关系
- 可能成为性能瓶颈
- 多线程下需要特殊处理

## 实现方式

### 1. 懒汉式（Thread-Safe）
```java
public class Singleton {
    private static Singleton instance;
    
    private Singleton() {}
    
    public static synchronized Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```

### 2. 饿汉式  
```java
public class Singleton {
    private static final Singleton instance = new Singleton();
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        return instance;
    }
}
```

### 3. 双检查锁定（Double-Checked Locking）
```java
public class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

## 常见问题

### 多线程环全下数据库连接泄漏
```
问题: 不同线程获取同一连接，导致并发问题

解决方案: 使用线程安全的初始化机制
```

### 序列化破坏单例
```
问题: 反序列化创建新实例

解决方案: 实现 readResolve() 方法
```

## 最佳实践

1. ✅ 使用 Bill Pugh 单例（静态内部类）
2. ✅ 考虑依赖注入替代方案  
3. ✅ 谨慎处理多线程场景
4. ✅ 编写易于测试的代码

## 何时避免使用

- 需要多个实例的场景
- 需要灵活切换实现
- 严格的单元测试要求
