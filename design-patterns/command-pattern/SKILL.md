---
name: 命令模式
description: "将请求封装为对象。在需要参数化请求或支持撤销/重做时使用。"
license: MIT
---

# 命令模式 (Command Pattern)

## 概述

命令模式将请求封装成一个对象，使得你可以参数化客户端的不同请求，对请求排序，记录请求日志以及支持可撤销的操作。

**核心原则**: 请求对象化，支持撤销回退。

## 何时使用

**始终:**
- 参数化请求
- 支持撤销/重做
- 记录请求日志
- 队列处理
- 异步执行

**触发短语:**
- "撤销/重做"
- "请求队列"
- "命令对象"
- "异步执行"

## 命令模式的优缺点

### 优点 ✅
- 将请求解耦
- 支持撤销/重做
- 支持延迟执行
- 支持批量和宏命令
- 易于记录和审计

### 缺点 ❌
- 类数量增加
- 编码复杂度上升
- 内存开销

## 实现方式

### 文本编辑器命令
```java
public interface Command {
    void execute();
    void undo();
}

public class CopyCommand implements Command {
    private Editor editor;
    private String backup;
    
    public CopyCommand(Editor editor) {
        this.editor = editor;
    }
    
    @Override
    public void execute() {
        backup = editor.getSelectedText();
        editor.clipboard = backup;
    }
    
    @Override
    public void undo() {
        editor.clipboard = backup;
    }
}

public class CommandHistory {
    private Stack<Command> history = new Stack<>();
    
    public void execute(Command cmd) {
        cmd.execute();
        history.push(cmd);
    }
    
    public void undo() {
        if (!history.isEmpty()) {
            history.pop().undo();
        }
    }
}
```

## 典型应用场景

### 1. 文本编辑器
- 撤销/重做
- 宏命令

### 2. 遥控器
- 按钮命令
- 宏定义

### 3. 异步任务
- 任务队列
- 批处理

### 4. 事务处理
- 事务回滚
- 操作日志

## 宏命令（复合命令）
```java
public class MacroCommand implements Command {
    private List<Command> commands = new ArrayList<>();
    
    public void add(Command command) {
        commands.add(command);
    }
    
    @Override
    public void execute() {
        for (Command cmd : commands) {
            cmd.execute();
        }
    }
    
    @Override
    public void undo() {
        for (int i = commands.size() - 1; i >= 0; i--) {
            commands.get(i).undo();
        }
    }
}
```

## 最佳实践

1. ✅ 命令对象不可变
2. ✅ 支持宏命令
3. ✅ 实现 undo/redo
4. ✅ 记录命令执行时间

## 何时避免使用

- 命令很简单
- 不需要撤销功能
- 内存紧张
