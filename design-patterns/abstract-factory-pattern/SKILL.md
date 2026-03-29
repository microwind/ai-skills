---
name: 抽象工厂模式
description: "提供一个接口来创建相关对象族。在需要创建一族相关产品时使用。"
license: MIT
---

# 抽象工厂模式 (Abstract Factory Pattern)

## 概述

抽象工厂模式提供一个接口，用于创建一族相关或依赖的对象，而无需指定它们的具体类。

**核心原则**: 创建相关的对象族，保持其一致性。

## 何时使用

**始终:**
- UI 主题系统（浅色/深色主题）
- 跨平台应用（Windows/Mac/Linux）
- 数据库方言处理
- 操作系统相关功能
- 支付系统（各国不同接口）

**触发短语:**
- "需要创建一族相关的对象"
- "支持多个产品族"
- "产品之间需要协调"
- "跨平台实现"

## 抽象工厂的优缺点

### 优点 ✅
- 产品族内的一致性
- 易于切换整个产品族
- 隔离具体实现
- 支持新产品族的添加

### 缺点 ❌
- 系统复杂度增加
- 添加新产品需要修改接口
- 可能过度设计

## 实现方式

### UI 主题系统
```java
public interface ThemeFactory {
    Button createButton();
    TextInput createTextInput();
}

public class DarkThemeFactory implements ThemeFactory {
    public Button createButton() {
        return new DarkButton();
    }
    public TextInput createTextInput() {
        return new DarkTextInput();
    }
}
```

## 典型应用场景

### 1. UI 主题管理
- 浅色主题
- 深色主题
- 高对比度主题

### 2. 跨平台 GUI
- Windows 组件
- Mac 组件
- Linux 组件

### 3. 数据库方言
- MySQL
- Oracle
- PostgreSQL

## 最佳实践

1. ✅ 清晰定义产品族边界
2. ✅ 产品之间保持高内聚
3. ✅ 使用配置管理产品族选择
4. ✅ 考虑使用反射简化实现

## 何时避免使用

- 产品族不稳定
- 产品间依赖关系复杂
- 需要频繁添加新产品
