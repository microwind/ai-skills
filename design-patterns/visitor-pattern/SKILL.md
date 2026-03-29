---
name: 访问者模式
description: "为对象添加新操作而不改变结构。在需要对对象结构进行复杂操作时使用。"
license: MIT
---

# 访问者模式 (Visitor Pattern)

## 概述

访问者模式表示一个作用于某对象结构中的各元素的操作。让你可以在不改变各元素的类的前提下定义作用于这些元素的新操作。

**核心原则**: 操作对象化，分离数据和操作。

## 何时使用

**始终:**
- 对象结构复杂且稳定
- 需要多种操作
- 操作独立于对象结构
- 编译器 AST 遍历
- 报表生成

**触发短语:**
- "复杂对象遍历"
- "多种操作"
- "分离数据和操作"
- "编译器"

## 访问者的优缺点

### 优点 ✅
- 分离数据和操作
- 易于添加新操作
- 操作集中管理
- 灵活组合

### 缺点 ❌
- 复杂度高
- 难以理解和维护
- 添加新元素困难
- 破坏封装

## 实现方式

### AST 遍历
```java
public interface Element {
    void accept(Visitor visitor);
}

public class NumberElement implements Element {
    public int value;
    
    @Override
    public void accept(Visitor visitor) {
        visitor.visit(this);
    }
}

public interface Visitor {
    void visit(NumberElement element);
    void visit(BinaryOpElement element);
}

public class PrintVisitor implements Visitor {
    @Override
    public void visit(NumberElement element) {
        System.out.println("Number: " + element.value);
    }
    
    @Override
    public void visit(BinaryOpElement element) {
        System.out.println("BinOp: " + element.operator);
    }
}
```

## 典型应用场景

### 1. 编译器
- 语法树遍历
- 代码生成
- 优化

### 2. 报表系统
- 不同格式导出
- 数据统计

### 3. DOM 遍历
- 样式计算
- 事件处理

## 最佳实践

1. ✅ 元素结构稳定
2. ✅ 访问者接口完整
3. ✅ 支持访问者链
4. ✅ 文档说明访问顺序

## 何时避免使用

- 元素经常变化
- 操作少于 2 个
- 对象结构简单
