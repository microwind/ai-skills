---
name: 装饰器模式
description: "动态给对象添加职责。在需要为对象增加功能但又不想改变类本身时使用。"
license: MIT
---

# 装饰器模式 (Decorator Pattern)

## 概述

装饰器模式动态地给对象添加职责。装饰提供了比继承更有弹性的替代方案来扩展功能。

**核心原则**: 装饰而非继承，动态组合而非静态继承。

## 何时使用

**始终:**
- 为对象添加新功能
- 避免大量子类
- 功能需要灵活组合
- 责任可以独立加或撤回

**触发短语:**
- "需要为对象添加能力"
- "功能需要灵活组合"
- "避免子类爆炸"
- "动态功能扩展"

## 装饰器模式的优缺点

### 优点 ✅
- 比继承更灵活
- 支持功能动态组合
- 符合单一职责原则
- 可以多个装饰器叠加

### 缺点 ❌
- 对象层级增加
- 代码复杂度提升
- 调试困难
- 顺序依赖

## 实现方式

### Java IO 装饰器链
```java
InputStream input = new GZIPInputStream(
    new BufferedInputStream(
        new FileInputStream("file.txt.gz")
    )
);
```

### 咖啡装饰器
```java
public abstract class CoffeeDecorator implements Coffee {
    protected Coffee coffee;
    
    public CoffeeDecorator(Coffee coffee) {
        this.coffee = coffee;
    }
}

public class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) {
        super(coffee);
    }
    
    @Override
    public double getCost() {
        return coffee.getCost() + 0.5;
    }
}
```

## 典型应用场景

### 1. 日志和监控
```java
UserService service = new UserService();
service = new LoggingDecorator(service);
service = new CachingDecorator(service);
service = new ValidationDecorator(service);
```

### 2. 权限检查
```java
Operation op = new DeleteUserOperation();
op = new AuthorizationDecorator(op);
op = new AuditingDecorator(op);
op.execute();
```

### 3. 数据转换
```java
OutputStream out = new FileOutputStream("file.bin");
out = new GZIPOutputStream(out);
out = new BufferedOutputStream(out);
out.write(data);
```

## 最佳实践

1. ✅ 装饰器和被装饰对象遵循同一接口
2. ✅ 装饰器职责单一
3. ✅ 支持多层装饰
4. ✅ 避免过深的装饰层级

## 装饰器 vs 继承

| 方面 | 装饰器 | 继承 |
|------|--------|------|
| 灵活性 | 高 | 低 |
| 组合 | 可以 | 不可以 |
| 复杂度 | 中 | 低 |
| 子类数 | 少 | 多 |

## 何时避免使用

- 只需要简单继承
- 功能组合不复杂
- 对象层级不深
