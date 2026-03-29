---
name: 模板方法模式
description: "定义算法骨架，细节由子类实现。在需要算法框架稳定而实现多样时使用。"
license: MIT
---

# 模板方法模式 (Template Method Pattern)

## 概述

模板方法模式在操作中定义算法的骨架，延迟一些步骤到子类。这个模式让子类在不改变算法结构的前提下重新定义某些步骤。

**核心原则**: 框架稳定，细节多样。

## 何时使用

**始终:**
- 算法框架固定
- 实现细节多样
- 避免代码重复
- 数据处理流程
- 请求处理流程

**触发短语:**
- "算法框架"
- "代码重复"
- "步骤可定制"
- "流程固定"

## 模板方法的优缺点

### 优点 ✅
- 代码复用
- 框架控制
- 职责清晰
- 易于维护

### 缺点 ❌
- 类层级增加
- 继承引入的复杂性
- 违反 Liskov 原则可能

## 实现方式

### 数据流处理
```java
public abstract class DataProcessor {
    public final void process(String filename) {
        String data = readData(filename);
        String processed = processData(data);
        writeData(processed);
    }
    
    protected abstract String readData(String filename);
    protected abstract String processData(String data);
    protected abstract void writeData(String data);
}

public class CsvProcessor extends DataProcessor {
    @Override
    protected String readData(String filename) {
        // 读取 CSV
        return "...";
    }
    
    @Override
    protected String processData(String data) {
        // 处理 CSV
        return "...";
    }
    
    @Override
    protected void writeData(String data) {
        // 写入 CSV
    }
}
```

## 典型应用场景

### 1. Spring 框架
- 模板方法定义 Bean 生命周期
- 子类实现初始化/销毁逻辑

### 2. 数据导入
- 数据验证
- 数据转换
- 数据存储

### 3. HTTP 请求处理
- 参数解析
- 权限检查
- 业务处理
- 响应构建

## 最佳实践

1. ✅ 模板方法应该 final
2. ✅ 清晰标注可重写方法
3. ✅ 冲测方法数量合理
4. ✅ 避免过深的继承链

## 何时避免使用

- 步骤数很少
- 步骤变化频繁
- 不适合继承的场景
