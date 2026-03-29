---
name: 桥接模式
description: "将抽象部分与实现部分分离。在需要避免类层级爆炸时使用。"
license: MIT
---

# 桥接模式 (Bridge Pattern)

## 概述

桥接模式将抽象部分与实现部分分离，使它们可以独立地变化。这个模式用来处理多维度的变化。

**核心原则**: 分离抽象和实现，支持独立扩展。

## 何时使用

**始终:**
- 类的多维度变化
- 需要避免类层级爆炸
- 实现和抽象独立变化
- 需要运行时切换实现

**触发短语:**
- "类层级太多"
- "多维度变化"
- "实现和接口分离"
- "避免继承爆炸"

## 桥接模式的优缺点

### 优点 ✅
- 分离抽象和实现
- 避免类层级爆炸
- 支持多维度变化
- 提高代码灵活性

### 缺点 ❌
- 设计复杂度增加
- 难以理解
- 增加系统复杂度

## 实现方式

### 形状-颜色系统
```java
// 现代方法：分离形状和颜色
public abstract class Shape {
    protected Color color;
    
    public Shape(Color color) {
        this.color = color;
    }
    
    public abstract void draw();
}

public class Circle extends Shape {
    @Override
    public void draw() {
        System.out.println("Drawing " + color.getColorName() + " circle");
    }
}

public interface Color {
    String getColorName();
}
```

## 典型应用场景

### 1. 远程控制
```java
// 电视：抽象
// 实现：Sony、LG、Samsung
// 控制器：标准、智能、语音
```

### 2. 数据库驱动
```java
// 驱动程序：MySQL、PostgreSQL、Oracle
// 操作：增删改查
```

### 3. 消息队列
```java
// 消息队列：RabbitMQ、Kafka、Redis
// 操作：发送、接收、确认
```

## 桥接 vs 继承

### 继承方式（类爆炸）
```
Shape
├── FilledCircle
├── FilledSquare
├── OutlineCircle
└── OutlineSquare
```

### 桥接方式（灵活）
```
Shape
├── Circle
└── Square
    ├── FilledImpl
    └── OutlineImpl
```

## 最佳实践

1. ✅ 清晰定义抽象和实现边界
2. ✅ 使用组合替代继承
3. ✅ 文档说明维度分离
4. ✅ 考虑工厂模式创建对象

## 何时避免使用

- 只有单一维度变化
- 维度组合很少
- 设计相对简单
