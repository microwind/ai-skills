---
name: 代理模式
description: "为其他对象提供代理以控制其访问。在需要延迟加载、权限控制或监控时使用。"
license: MIT
---

# 代理模式 (Proxy Pattern)

## 概述

代理模式为其他对象提供一个代理或占位符。代理控制对真实对象的访问。

**核心原则**: 用代理对象替代真实对象，控制访问。

## 何时使用

**始终:**
- 延迟初始化（Lazy Loading）
- 访问控制（权限检查）
- 日志和审计
- 性能监控
- 远程对象访问

**触发短语:**
- "需要控制对象访问"
- "需要延迟加载"
- "需要权限检查"
- "需要对象监控"

## 代理模式的优缺点

### 优点 ✅
- 控制真实对象的访问
- 在访问之前执行初始化
- 实现权限检查
- 提供监控和日志

### 缺点 ❌
- 增加系统复杂度
- 性能开销
- 响应延迟增加

## 实现方式

### 虚代理（延迟加载）
```java
public class ImageProxy implements Image {
    private String filename;
    private RealImage realImage;
    
    public ImageProxy(String filename) {
        this.filename = filename;
    }
    
    @Override
    public void load() {
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        realImage.load();
    }
}
```

### 保护代理（权限控制）
```java
public class UserServiceProxy implements UserService {
    private UserService target;
    private User currentUser;
    
    @Override
    public void deleteUser(String userId) {
        if (!currentUser.hasPermission("delete_user")) {
            throw new AccessDeniedException();
        }
        target.deleteUser(userId);
    }
}
```

## 代理模式的类型

### 1. 虚代理
- 延迟初始化
- 按需加载

### 2. 保护代理
- 权限控制
- 访问检查

### 3. 远程代理
- RMI 代理
- Web Service 代理

### 4. 日志代理
- 记录方法调用
- 审计

## 典型应用场景

### 1. ORM 框架
```java
// Hibernate 使用代理实现延迟加载
User user = session.get(User.class, 1);
// user 是代理，关联集合在第一次访问时加载
user.getRoles(); // 此时才查询数据库
```

### 2. AOP 框架
```java
UserService service = ProxyFactory.createProxy(userService);
// 代理自动添加事务、日志、权限检查
```

## 最佳实践

1. ✅ 代理和真实对象实现同一接口
2. ✅ 代理职责清晰明确
3. ✅ 避免代理链过长
4. ✅ 文档说明代理行为

## 代理 vs 装饰器

| 方面 | 代理 | 装饰器 |
|------|------|--------|
| 目的 | 控制访问 | 添加功能 |
| 职责 | 单一 | 可多个 |
| 接口 | 通常相同 | 相同 |
| 何时创建 | 创建时 | 自由 |

## 何时避免使用

- 不需要访问控制
- 对象创建成本低
- 需要简单访问
