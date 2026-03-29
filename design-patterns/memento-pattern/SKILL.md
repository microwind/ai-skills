---
name: 备忘录模式
description: "保存和恢复对象状态。在需要实现撤销/恢复时使用。"
license: MIT
---

# 备忘录模式 (Memento Pattern)

## 概述

备忘录模式在不破坏封装的前提下，捕获并外部化对象的内部状态，允许后来恢复到该状态。

**核心原则**: 保存状态，无需暴露细节。

## 何时使用

**始终:**
- 实现撤销/重做
- 保存对象快照
- 时间旅行功能
- 版本控制
- 事务回滚

**触发短语:**
- "撤销/重做"
- "保存状态"
- "版本控制"
- "快照"

## 备忘录的优缺点

### 优点 ✅
- 保存对象状态
- 不破坏封装
- 支持撤销/重做
- 版本管理

### 缺点 ❌
- 内存开销大
- 复制成本高
- 需要额外存储

## 实现方式

### 对象版本管理
```java
public class Memento {
    private final String state;
    
    public Memento(String state) {
        this.state = state;
    }
    
    public String getState() {
        return state;
    }
}

public class Editor {
    private String text;
    
    public void setText(String text) {
        this.text = text;
    }
    
    public Memento save() {
        return new Memento(text);
    }
    
    public void restore(Memento memento) {
        text = memento.getState();
    }
}

public class EditorHistory {
    private Stack<Memento> history = new Stack<>();
    
    public void save(Editor editor) {
        history.push(editor.save());
    }
    
    public void undo(Editor editor) {
        if (!history.isEmpty()) {
            editor.restore(history.pop());
        }
    }
}
```

## 典型应用场景

### 1. 文本编辑器
- 自动保存版本
- 撤销/重做

### 2. 游戏存档
- 游戏进度保存
- 加载存档

### 3. 数据库事务
- 事务回滚
- 恢复点

### 4. 配置管理
- 配置版本
- 回滚到上一版本

## 最佳实践

1. ✅ Memento 不暴露内部状态
2. ✅ 使用 Caretaker 管理历史
3. ✅ 考虑内存影响
4. ✅ 支持序列化

## 何时避免使用

- 对象状态很大
- 频繁保存状态
- 内存受限
