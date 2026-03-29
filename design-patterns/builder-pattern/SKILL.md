---
name: 建造者模式
description: "分步骤构建复杂对象。在对象有很多可选参数或构建步骤复杂时使用。"
license: MIT
---

# 建造者模式 (Builder Pattern)

## 概述

建造者模式将复杂对象的构建与其表示分离，使得可以按步骤构建对象。这个模式适用于对象有多个可选属性的场景。

**核心原则**: 分离对象构建和表示，支持不同的构建方式。

## 何时使用

**始终:**
- 对象有很多可选参数
- 构建过程有多个步骤
- 参数间有依赖关系
- 需要构建不同的表示形式

**触发短语:**
- "对象有太多构造函数参数"
- "需要灵活的对象构建"
- "参数可选、可配置"
- "构建步骤复杂"

## 建造者模式的优缺点

### 优点 ✅
- 代码易读性好
- 灵活处理可选参数
- 分离构建和表示
- 支持链式调用
- 参数验证集中

### 缺点 ❌
- 代码量增加
- 过度设计简单对象
- 运行时灵活性不如其他方案

## 实现方式

### 链式调用（Fluent Interface）
```java
public class HttpRequest {
    private String url;
    private String method = "GET";
    private Map<String, String> headers = new HashMap<>();
    
    public static class Builder {
        private String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        
        public Builder url(String url) {
            this.url = url;
            return this;
        }
        
        public Builder method(String method) {
            this.method = method;
            return this;
        }
        
        public Builder header(String key, String value) {
            headers.put(key, value);
            return this;
        }
        
        public HttpRequest build() {
            return new HttpRequest(this);
        }
    }
}
```

### 使用示例
```java
HttpRequest request = new HttpRequest.Builder()
    .url("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .build();
```

## 典型应用场景

### 1. SQL 查询构建
```java
SelectQuery query = new SelectQueryBuilder()
    .select("*")
    .from("users")
    .where("age > 18")
    .orderBy("name")
    .build();
```

### 2. HTTP 请求封装
```java
Request request = new RequestBuilder()
    .url(url)
    .addParameter("key", "value")
    .addHeader("Authorization", token)
    .build();
```

### 3. 复杂对象初始化
```java
UIPanel panel = new UIPanelBuilder()
    .setLayout(new GridLayout(3, 3))
    .setBackground(Color.WHITE)
    .setBorder(new Border(5))
    .build();
```

## 最佳实践

1. ✅ 支持链式调用提高易用性
2. ✅ 在 build() 前验证必填参数
3. ✅ 提供合理的默认值
4. ✅ 考虑不可变对象设计

## 何时避免使用

- 参数只有 1-2 个
- 对象相对简单
- 构建逻辑固定
