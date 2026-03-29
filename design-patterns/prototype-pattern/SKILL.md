---
name: 原型模式
description: "通过复制已有对象来创建新对象。当对象创建成本高或需要保存对象状态时使用。"
license: MIT
---

# 原型模式 (Prototype Pattern)

## 概述

原型模式通过复制已有对象来创建新对象，而不是通过 new 关键字创建。这个模式在对象创建成本高时特别有用。

**核心原则**: 通过克隆而非创建来生成新对象。

## 何时使用

**始终:**
- 对象创建成本高
- 需要避免子类化
- 需要在运行时确定对象类型
- 对象状态较多且需要保存

**触发短语:**
- "创建对象成本太高"
- "需要深度复制对象"
- "保存对象的历史状态"
- "避免复杂的创建过程"

## 原型模式的优缺点

### 优点 ✅
- 绕过复杂的创建过程
- 性能更好（避免重复初始化）
- 运行时对象创建灵活
- 保存对象状态

### 缺点 ❌
- 深复制实现复杂
- 循环引用处理困难
- 需要正确实现 Cloneable
- 可能引入线程安全问题

## 实现方式

### Java 中的实现
```java
public class User implements Cloneable {
    private String name;
    private List<String> roles;
    
    @Override
    public User clone() throws CloneNotSupportedException {
        User cloned = (User) super.clone();
        // 深复制集合
        cloned.roles = new ArrayList<>(this.roles);
        return cloned;
    }
}
```

### 深复制示例
```java
public class Document implements Cloneable {
    private String content;
    private Map<String, Object> metadata;
    
    @Override
    public Document clone() throws CloneNotSupportedException {
        Document cloned = (Document) super.clone();
        // 深复制 Map
        cloned.metadata = new HashMap<>(this.metadata);
        return cloned;
    }
}
```

## 典型应用场景

### 1. 对象缓存
```java
User userTemplate = loadUserTemplate();
User newUser = userTemplate.clone();
newUser.setId(newId);
```

### 2. 撤销/重做
```java
// 保存版本
documentVersions.add(document.clone());
```

### 3. 配置管理
```java
Config baseConfig = loadDefaultConfig();
Config customConfig = baseConfig.clone();
customConfig.setProperty("theme", "dark");
```

## 最佳实践

1. ✅ 正确实现深复制
2. ✅ 处理循环引用
3. ✅ 记录克隆成本
4. ✅ 使用工厂模式管理原型注册

## 常见问题

### 浅复制 vs 深复制
- **浅复制**: 只复制对象引用
- **深复制**: 完整复制对象及其属性

### 循环引用问题
```
解决方案: 使用访问标记来跟踪已复制对象
```

## 何时避免使用

- 对象很简单
- 创建成本不高
- 不需要保存状态版本
