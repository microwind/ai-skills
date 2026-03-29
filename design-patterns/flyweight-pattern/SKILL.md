---
name: 享元模式
description: "共享对象以节省内存。在需要创建大量相似对象时使用。"
license: MIT
---

# 享元模式 (Flyweight Pattern)

## 概述

享元模式通过共享相同的对象来优化内存使用。这个模式在需要创建大量相似对象时特别有用。

**核心原则**: 共享不可变对象，减少内存占用。

## 何时使用

**始终:**
- 需要创建大量相似对象
- 内存使用是瓶颈
- 对象状态大部分不变
- 游戏渲染
- 文本编辑器字符

**触发短语:**
- "大量对象占用内存"
- "性能优化"
- "内存优化"
- "对象复用"

## 享元模式的优缺点

### 优点 ✅
- 大幅降低内存使用
- 提高性能
- 减少对象创建开销
- 应用场景清晰

### 缺点 ❌
- 增加代码复杂度
- 线程安全问题
- 查找享元开销
- 调试困难

## 实现方式

### 字符享元
```java
public class Character {
    private final char value;
    private final Font font;
    
    public Character(char value, Font font) {
        this.value = value;
        this.font = font;
    }
}

public class CharacterFactory {
    private static final Map<String, Character> cache = 
        new HashMap<>();
    
    public static Character getCharacter(Character c, Font font) {
        String key = c + "_" + font.getName();
        return cache.computeIfAbsent(key, 
            k -> new Character(c, font));
    }
}
```

### 游戏树
```java
public class Tree {
    private String name;
    private Bitmap bitmap;  // 共享
    
    public Tree(String name, Bitmap bitmap) {
        this.name = name;
        this.bitmap = bitmap;  // 所有树共享相同位图
    }
}

public class BitmapFactory {
    private static Map<String, Bitmap> bitmaps = ...;
    
    public static Bitmap getBitmap(String filename) {
        return bitmaps.computeIfAbsent(filename, 
            f -> loadBitmap(f));
    }
}
```

## 典型应用场景

### 1. 文本编辑器
- 每个字符是享元
- 共享字体、颜色信息

### 2. 游戏渲染
- 树、草等对象复用贴图
- 减少显存占用

### 3. 连接池
- 复用数据库连接
- HTTP 连接复用

### 4. 对象池
- 线程池
- 缓冲池

## 享元 vs 对象池

| 方面 | 享元 | 对象池 |
|------|------|--------|
| 目的 | 共享不可变部分 | 复用对象 |
| 状态 | 不变 | 可变 |
| 线程安全 | 免疫 | 需要同步 |
| 适用场景 | 大量相似 | 创建开销大 |

## 最佳实践

1. ✅ 明确分离内部状态和外部状态
2. ✅ 享元对象不可变
3. ✅ 使用工厂模式管理享元
4. ✅ 测试内存节省效果

## 何时避免使用

- 对象很少
- 内存使用不是瓶颈
- 状态修改频繁
