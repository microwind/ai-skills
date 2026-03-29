---
name: 命令模式
description: "将请求封装为对象。在需要参数化请求或支持撤销/重做时使用。"
license: MIT
---

# 命令模式 (Command Pattern)

## 概述

命令模式将请求封装成一个对象，使得你可以参数化客户端的不同请求，对请求排序、记录请求日志以及支持可撤销的操作。

**核心原则**:
- 🎁 **请求对象化**: 将操作封装为 Command 对象
- ⏰ **延迟执行**: 稍后执行请求
- 🔄 **撤销/重做**: 支持操作回退
- 📝 **日志记录**: 记录完整操作历史
- 🗂️ **请求队列**: 将请求集合管理

## 何时使用

### 完美适用场景

| 场景 | 说明 | 优先级 |
|------|------|--------|
| **文本编辑器撤销系统** | 记录所有编辑操作，支持撤销/重做 | ⭐⭐⭐ |
| **事务管理** | 将多个操作作为一个事务，支持回滚 | ⭐⭐⭐ |
| **任务队列** | 异步执行、批量处理任务 | ⭐⭐⭐ |
| **远程命令调用** | RPC、网络命令执行 | ⭐⭐⭐ |
| **宏命令录制** | 记录一系列操作，批量重复执行 | ⭐⭐ |
| **定时任务** | 调度器、预定执行 | ⭐⭐ |
| **按钮映射** | UI 按钮映射到不同操作 | ⭐⭐ |

### 触发信号

✅ 以下信号表明应该使用命令模式：
- "需要支持撤销/重做"
- "想要延迟执行请求"
- "需要将操作序列化/持久化"
- "想要记录完整的操作日志"
- "需要参数化请求"
- "想要在多个地方重复执行操作"

❌ 以下情况不应该使用：
- 操作非常简单
- 不需要撤销功能
- 内存严重受限
- 操作次序无关紧要

## 命令模式的优缺点

### 优点 ✅

1. **实现撤销/重做**
   - 天然支持操作回退
   - 不需要额外的版本控制
   - 用户体验更佳

2. **延迟执行**
   - 可以稍后执行请求
   - 支持异步处理
   - 支持定时执行

3. **请求队列化**
   - 将多个请求排队
   - 支持批量处理
   - 易于实现并发控制

4. **完整的审计日志**
   - 记录每个操作
   - 追踪数据变化
   - 便于调试和问题追踪

5. **高度灵活**
   - 易于添加新命令
   - 命令组合灵活
   - 可以动态配置

### 缺点 ❌

1. **类数量增加**
   - 每个命令都需要一个类
   - 代码文件变多
   - 可能过度设计

2. **内存开销**
   - 每个命令都需要存储状态
   - 撤销栈占用内存
   - 可能导致内存溢出

3. **复杂度增加**
   - 需要管理命令历史
   - 处理命令间的依赖关系
   - 异常处理相对复杂

## 命令模式的 5 种实现方法

### 1. 基础 Command 模式

**特点**: 标准实现，每个操作一个 Command 类

```java
// 命令接口
public interface Command {
    void execute();
    void undo();
}

// 具体命令
public class WriteCommand implements Command {
    private Editor editor;
    private String text;
    private String backup;  // 保存原文本用于撤销
    
    public WriteCommand(Editor editor, String text) {
        this.editor = editor;
        this.text = text;
    }
    
    @Override
    public void execute() {
        backup = editor.getContent();
        editor.write(text);
        System.out.println("[Command] Writing: " + text);
    }
    
    @Override
    public void undo() {
        editor.setContent(backup);
        System.out.println("[Command] Undo write");
    }
}

// 命令执行器
public class CommandHistory {
    private Stack<Command> history = new Stack<>();
    private Stack<Command> redoStack = new Stack<>();
    
    public void execute(Command cmd) {
        cmd.execute();
        history.push(cmd);
        redoStack.clear();  // 执行新命令，清除 redo 历史
    }
    
    public void undo() {
        if (!history.isEmpty()) {
            Command cmd = history.pop();
            cmd.undo();
            redoStack.push(cmd);
        }
    }
    
    public void redo() {
        if (!redoStack.isEmpty()) {
            Command cmd = redoStack.pop();
            cmd.execute();
            history.push(cmd);
        }
    }
}

// 使用
Editor editor = new Editor();
CommandHistory history = new CommandHistory();

history.execute(new WriteCommand(editor, "Hello"));
history.execute(new WriteCommand(editor, " World"));
history.undo();  // 撤销
history.redo();  // 重做
```

---

### 2. 参数化 Command

**特点**: 分离命令定义和参数，一个命令类支持多种参数

```java
// 参数化命令
public class GenericCommand<T> implements Command {
    private final Runnable executeAction;
    private final Runnable undoAction;
    
    public GenericCommand(Runnable executeAction, Runnable undoAction) {
        this.executeAction = executeAction;
        this.undoAction = undoAction;
    }
    
    @Override
    public void execute() {
        executeAction.run();
    }
    
    @Override
    public void undo() {
        undoAction.run();
    }
}

// 使用
class TextField {
    private StringBuilder content = new StringBuilder();
    
    public void write(String text) {
        content.append(text);
        System.out.println("Content: " + content);
    }
    
    public void clear() {
        content.setLength(0);
        System.out.println("Cleared");
    }
}

TextField field = new TextField();
CommandHistory history = new CommandHistory();

// 轻松创建命令，无需定义新类
String originalContent = "";
history.execute(new GenericCommand<>(
    () -> field.write("Hello"),
    () -> field.clear()
));

history.undo();
```

---

### 3. 异步 Command

**特点**: 支持异步执行，使用 Future 或 Callback

```java
public interface AsyncCommand {
    void execute(CommandCallback callback);
    void undo();
}

public interface CommandCallback {
    void onSuccess(Object result);
    void onError(Exception e);
}

// 异步任务查询
public class AsyncDatabaseQueryCommand implements AsyncCommand {
    private String query;
    private String originalResult;
    
    public AsyncDatabaseQueryCommand(String query) {
        this.query = query;
    }
    
    @Override
    public void execute(CommandCallback callback) {
        // 在后台线程执行
        new Thread(() -> {
            try {
                // 模拟数据库查询
                Thread.sleep(1000);
                String result = "Query result for: " + query;
                originalResult = result;
                callback.onSuccess(result);
            } catch (InterruptedException e) {
                callback.onError(e);
            }
        }).start();
    }
    
    @Override
    public void undo() {
        // 撤销可能是清除缓存或日志
        System.out.println("Undoing query");
        originalResult = null;
    }
}

// 异步命令执行器
public class AsyncCommandExecutor {
    private Stack<AsyncCommand> history = new Stack<>();
    
    public void execute(AsyncCommand cmd) {
        cmd.execute(new CommandCallback() {
            @Override
            public void onSuccess(Object result) {
                history.push(cmd);
                System.out.println("Command executed successfully: " + result);
            }
            
            @Override
            public void onError(Exception e) {
                System.out.println("Command failed: " + e.getMessage());
            }
        });
    }
}
```

---

### 4. 宏命令（复合命令）

**特点**: 将多个命令组合成一个，作为一个原子操作执行

```java
// 宏命令 - 包含多个子命令
public class MacroCommand implements Command {
    private List<Command> commands = new ArrayList<>();
    
    public void add(Command cmd) {
        commands.add(cmd);
    }
    
    public void remove(Command cmd) {
        commands.remove(cmd);
    }
    
    @Override
    public void execute() {
        System.out.println("[Macro] Executing " + commands.size() + " commands");
        for (Command cmd : commands) {
            cmd.execute();
        }
    }
    
    @Override
    public void undo() {
        System.out.println("[Macro] Undoing " + commands.size() + " commands");
        for (int i = commands.size() - 1; i >= 0; i--) {
            commands.get(i).undo();
        }
    }
}

// 使用场景：保存文件为宏操作
public class SaveWorkspaceCommand implements Command {
    private MacroCommand macro = new MacroCommand();
    
    public SaveWorkspaceCommand(Document doc1, Document doc2, Document doc3) {
        // 将多个操作组合成一个
        macro.add(new SaveCommand(doc1));
        macro.add(new SaveCommand(doc2));
        macro.add(new SaveCommand(doc3));
        macro.add(new UpdateConfigCommand());
    }
    
    @Override
    public void execute() {
        macro.execute();
    }
    
    @Override
    public void undo() {
        macro.undo();
    }
}

// 执行整个工作流
SaveWorkspaceCommand save = new SaveWorkspaceCommand(doc1, doc2, doc3);
save.execute();  // 一次性执行所有子命令
save.undo();     // 一次性撤销所有子命令
```

---

### 5. 聚合器 Command

**特点**: 用于聚合同类操作，优化撤销栈

```java
// 聚合器 - 将多个相同类型的操作合并
public class AggregateCommand implements Command {
    private List<Command> batchedCommands = new ArrayList<>();
    private long createdTime;
    
    public void addCommand(Command cmd) {
        // 如果时间间隔过长，不再聚合
        if (!batchedCommands.isEmpty()) {
            long timeDiff = System.currentTimeMillis() - createdTime;
            if (timeDiff > 3000) {  // 3秒内的操作聚合
                return;
            }
        }
        
        batchedCommands.add(cmd);
        if (batchedCommands.size() == 1) {
            createdTime = System.currentTimeMillis();
        }
    }
    
    @Override
    public void execute() {
        System.out.println("[Aggregate] Executing " + batchedCommands.size() + " commands");
        for (Command cmd : batchedCommands) {
            cmd.execute();
        }
    }
    
    @Override
    public void undo() {
        // 一次性撤销所有聚合的操作
        for (int i = batchedCommands.size() - 1; i >= 0; i--) {
            batchedCommands.get(i).undo();
        }
    }
}

// 使用场景：快速连续输入的字符聚合
public class TextInput {
    private List<Command> pendingCommands = new ArrayList<>();
    private AggregateCommand aggregator = new AggregateCommand();
    
    public void type(char c) {
        Command cmd = new CharCommand(this, c);
        aggregator.addCommand(cmd);
    }
    
    public void flushCommands(CommandHistory history) {
        history.execute(aggregator);
        aggregator = new AggregateCommand();
    }
}
```

---

## 常见问题与完整解决方案

### 问题 1: 撤销栈占用过多内存

**症状**: 大量命令执行后，内存不断增加，导致 OutOfMemoryError

```java
// ✅ 解决方案1：限制历史记录大小
public class LimitedCommandHistory {
    private Stack<Command> history = new Stack<>();
    private static final int MAX_HISTORY = 100;  // 最多保留100条
    
    public void execute(Command cmd) {
        cmd.execute();
        history.push(cmd);
        
        // 超过限制时删除最早的
        if (history.size() > MAX_HISTORY) {
            // 移除最底层元素
            history.removeElementAt(0);
        }
    }
}

// ✅ 解决方案2：使用弱引用，允许 GC
public class GCFriendlyHistory {
    private Queue<WeakReference<Command>> history = new LinkedList<>();
    
    public void execute(Command cmd) {
        cmd.execute();
        history.offer(new WeakReference<>(cmd));
    }
    
    public void undo() {
        WeakReference<Command> ref = history.poll();
        if (ref != null && ref.get() != null) {
            ref.get().undo();
        }
    }
}

// ✅ 解决方案3：持久化到磁盘
public class PersistentCommandHistory {
    private File historyFile;
    private List<Command> memoryCache;
    private final int CACHE_SIZE = 10;
    
    public void execute(Command cmd) throws IOException {
        cmd.execute();
        
        // 写入磁盘
        saveToFile(cmd);
        
        // 内存中只保留最近的几条
        if (memoryCache.size() > CACHE_SIZE) {
            memoryCache.remove(0);
        }
    }
    
    private void saveToFile(Command cmd) throws IOException {
        // 序列化命令到文件
    }
}
```

### 问题 2: 命令依赖和顺序问题

**症状**: 某些命令依赖其他命令的执行结果，撤销顺序错误

```java
// ✅ 解决方案：定义命令间的依赖
public class DependentCommand implements Command {
    private Command dependency;
    private Runnable action;
    
    public DependentCommand(Command dependency, Runnable action) {
        this.dependency = dependency;
        this.action = action;
    }
    
    @Override
    public void execute() {
        // 确保依赖已执行
        if (dependency == null) {
            throw new IllegalStateException("Dependency not executed");
        }
        action.run();
    }
    
    @Override
    public void undo() {
        action = null;  // 清除状态
    }
}

// 构建命令链
Command step1 = new UserRegisterCommand();
Command step2 = new DependentCommand(step1, () -> {
    // step1 必须先执行
    sendWelcomeEmail();
});
```

### 问题 3: 异常处理中的数据不一致

**症状**: 命令执行到一半出错，数据处于不一致状态

```java
// ✅ 解决方案：事务性操作
public class TransactionalCommand implements Command {
    private Object savedState;
    private Runnable action;
    private Supplier<Object> getState;
    private Consumer<Object> setState;
    
    @Override
    public void execute() {
        try {
            // 保存状态快照
            savedState = getState.get();
            
            // 执行操作
            action.run();
            
        } catch (Exception e) {
            // 发生错误，自动回滚
            setState.accept(savedState);
            throw e;
        }
    }
    
    @Override
    public void undo() {
        setState.accept(savedState);
    }
}

// 使用
TransactionalCommand cmd = new TransactionalCommand(
    () -> database.executeQuery(sql),  // 获取快照
    () -> doComplexOperation(),         // 执行操作
    state -> database.restore(state)    // 恢复状态
);
```

### 问题 4: 命令队列管理

**症状**: 高并发下多个命令竞争执行，导致结果错乱

```java
// ✅ 解决方案：线程安全的命令队列
public class ThreadSafeCommandQueue {
    private Queue<Command> queue = new ConcurrentLinkedQueue<>();
    private ExecutorService executor = Executors.newSingleThreadExecutor();
    
    public void submit(Command cmd) {
        queue.offer(cmd);
        executor.submit(this::processNextCommand);
    }
    
    private synchronized void processNextCommand() {
        Command cmd = queue.poll();
        if (cmd != null) {
            try {
                cmd.execute();
            } catch (Exception e) {
                System.err.println("Command failed: " + e.getMessage());
                cmd.undo();
            }
        }
    }
}
```

---

## 命令 vs 其他模式对比

| 方面 | 命令 | 策略 | 观察者 |
|------|------|------|--------|
| **目的** | 参数化请求 | 选择算法 | 通知观察者 |
| **执行时机** | 可延迟 | 立即执行 | 立即触发 |
| **撤销支持** | 天然支持 | 不支持 | 不支持 |
| **历史记录** | 可记录 | 无法记录 | 无法记录 |
| **示例** | 编辑器撤销 | 排序算法 | 事件监听 |

---

## 最佳实践

1. ✅ **命令职责单一** - 每个 Command 只做一件事
2. ✅ **完整的撤销实现** - 确保 undo() 能完全恢复状态
3. ✅ **限制历史大小** - 防止内存溢出
4. ✅ **处理异常** - 优雅降级和错误恢复
5. ✅ **文档化命令协议** - 说明执行和撤销的行为
6. ✅ **考虑序列化** - 便于持久化和网络传输

---

## 何时避免使用

- ❌ 操作非常简单，无需撤销
- ❌ 内存严重受限（嵌入式系统）
- ❌ 实时性要求极高（会有延迟）
- ❌ 操作无法重复执行（如删除操作）
