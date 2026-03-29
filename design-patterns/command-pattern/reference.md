# 命令模式完整参考实现

## UML 类图

```
┌──────────────┐
│   Invoker    │  (调用者/驱动程序)
├──────────────┤
│ - commands[] │
│ + execute()  │
└──────┬───────┘
       │ 使用
       ▼
┌──────────────────┐
│   Command        │  (接口)
├──────────────────┤
│ + execute()      │
│ + undo()         │
│ + redo()         │
└──────┬───────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│ ConcreteCommand │  │ MacroCommand │
├─────────────────┤  ├──────────────┤
│ - receiver      │  │ - commands[] │
│ - args          │  │ + execute()  │
│ + execute()     │  └──────────────┘
└─────────────────┘
       │
       └─→ ┌──────────────┐
           │   Receiver   │  (接收者)
           ├──────────────┤
           │ + action()   │
           └──────────────┘
```

---

## Java: 文本编辑器撤销系统

### 核心类

```java
import java.util.*;
import java.time.LocalDateTime;

// ===== 命令接口 =====
public interface Command {
    void execute();
    void undo();
    void redo();
    String getDescription();
    LocalDateTime getExecutedTime();
}

// ===== 编辑器（接收者） =====
public class TextEditor {
    private StringBuilder text = new StringBuilder();
    private int cursorPosition = 0;
    
    public void insertText(String content, int position) {
        cursorPosition = position;
        text.insert(position, content);
        System.out.printf("[Editor] 在位置%d插入: '%s'\n", position, content);
    }
    
    public void deleteText(int start, int end) {
        text.delete(start, end);
        System.out.printf("[Editor] 删除位置%d-%d的文本\n", start, end);
    }
    
    public String getText() {
        return text.toString();
    }
    
    public void replaceText(int start, int end, String newText) {
        text.replace(start, end, newText);
        System.out.printf("[Editor] 替换位置%d-%d为: '%s'\n", start, end, newText);
    }
    
    public void clear() {
        text.setLength(0);
        System.out.println("[Editor] 清空文本");
    }
}

// ===== 具体命令：插入文本 =====
public class InsertTextCommand implements Command {
    private TextEditor editor;
    private String textToInsert;
    private int position;
    private String previousText;
    private LocalDateTime executedTime;
    
    public InsertTextCommand(TextEditor editor, String text, int position) {
        this.editor = editor;
        this.textToInsert = text;
        this.position = position;
        this.previousText = editor.getText();
    }
    
    @Override
    public void execute() {
        editor.insertText(textToInsert, position);
        this.executedTime = LocalDateTime.now();
    }
    
    @Override
    public void undo() {
        int endPos = position + textToInsert.length();
        String currentText = editor.getText();
        editor.clear();
        // 恢复之前状态
        int insertStart = Math.min(position, currentText.length());
        int deleteEnd = Math.min(endPos, currentText.length());
        editor.deleteText(insertStart, deleteEnd);
        System.out.println("[Undo] 撤销插入操作");
    }
    
    @Override
    public void redo() {
        editor.insertText(textToInsert, position);
        System.out.println("[Redo] 重做插入操作");
    }
    
    @Override
    public String getDescription() {
        return String.format("插入文本: '%s' (位置:%d)", textToInsert, position);
    }
    
    @Override
    public LocalDateTime getExecutedTime() {
        return executedTime;
    }
}

// ===== 具体命令：删除文本 =====
public class DeleteTextCommand implements Command {
    private TextEditor editor;
    private int startPos;
    private int endPos;
    private String deletedText;
    private LocalDateTime executedTime;
    
    public DeleteTextCommand(TextEditor editor, int startPos, int endPos) {
        this.editor = editor;
        this.startPos = startPos;
        this.endPos = endPos;
        String fullText = editor.getText();
        this.deletedText = fullText.substring(
            Math.min(startPos, fullText.length()),
            Math.min(endPos, fullText.length())
        );
    }
    
    @Override
    public void execute() {
        editor.deleteText(startPos, endPos);
        this.executedTime = LocalDateTime.now();
    }
    
    @Override
    public void undo() {
        editor.insertText(deletedText, startPos);
        System.out.println("[Undo] 撤销删除操作");
    }
    
    @Override
    public void redo() {
        editor.deleteText(startPos, endPos);
        System.out.println("[Redo] 重做删除操作");
    }
    
    @Override
    public String getDescription() {
        return String.format("删除文本: '%s'", deletedText);
    }
    
    @Override
    public LocalDateTime getExecutedTime() {
        return executedTime;
    }
}

// ===== 具体命令：替换文本 =====
public class ReplaceTextCommand implements Command {
    private TextEditor editor;
    private int startPos;
    private int endPos;
    private String newText;
    private String oldText;
    private LocalDateTime executedTime;
    
    public ReplaceTextCommand(TextEditor editor, int start, int end, String newText) {
        this.editor = editor;
        this.startPos = start;
        this.endPos = end;
        this.newText = newText;
        String fullText = editor.getText();
        this.oldText = fullText.substring(
            Math.min(start, fullText.length()),
            Math.min(end, fullText.length())
        );
    }
    
    @Override
    public void execute() {
        editor.replaceText(startPos, endPos, newText);
        this.executedTime = LocalDateTime.now();
    }
    
    @Override
    public void undo() {
        editor.replaceText(startPos, startPos + newText.length(), oldText);
        System.out.println("[Undo] 撤销替换操作");
    }
    
    @Override
    public void redo() {
        editor.replaceText(startPos, endPos, newText);
        System.out.println("[Redo] 重做替换操作");
    }
    
    @Override
    public String getDescription() {
        return String.format("替换文本: '%s' → '%s'", oldText, newText);
    }
    
    @Override
    public LocalDateTime getExecutedTime() {
        return executedTime;
    }
}

// ===== 宏命令：批量操作 =====
public class MacroCommand implements Command {
    private List<Command> commands = new ArrayList<>();
    private String macroName;
    private LocalDateTime executedTime;
    
    public MacroCommand(String name) {
        this.macroName = name;
    }
    
    public void addCommand(Command cmd) {
        commands.add(cmd);
    }
    
    @Override
    public void execute() {
        System.out.println("\n[Macro] 执行宏命令: " + macroName);
        for (Command cmd : commands) {
            cmd.execute();
        }
        this.executedTime = LocalDateTime.now();
    }
    
    @Override
    public void undo() {
        System.out.println("[Macro] 撤销宏命令: " + macroName);
        for (int i = commands.size() - 1; i >= 0; i--) {
            commands.get(i).undo();
        }
    }
    
    @Override
    public void redo() {
        System.out.println("[Macro] 重做宏命令: " + macroName);
        for (Command cmd : commands) {
            cmd.redo();
        }
    }
    
    @Override
    public String getDescription() {
        return String.format("宏命令: %s (%d个操作)", macroName, commands.size());
    }
    
    @Override
    public LocalDateTime getExecutedTime() {
        return executedTime;
    }
}

// ===== 历史管理器（Invoker） =====
public class CommandHistory {
    private Stack<Command> undoStack = new Stack<>();
    private Stack<Command> redoStack = new Stack<>();
    private static final int MAX_HISTORY = 50;
    
    public void execute(Command cmd) {
        cmd.execute();
        undoStack.push(cmd);
        
        // 防止内存泄漏
        if (undoStack.size() > MAX_HISTORY) {
            undoStack.remove(0);
        }
        
        // 执行新命令后清空重做栈
        redoStack.clear();
    }
    
    public void undo() {
        if (undoStack.isEmpty()) {
            System.out.println("[History] 没有可撤销的操作");
            return;
        }
        
        Command cmd = undoStack.pop();
        cmd.undo();
        redoStack.push(cmd);
    }
    
    public void redo() {
        if (redoStack.isEmpty()) {
            System.out.println("[History] 没有可重做的操作");
            return;
        }
        
        Command cmd = redoStack.pop();
        cmd.redo();
        undoStack.push(cmd);
    }
    
    public void printHistory() {
        System.out.println("\n=== 命令历史 ===");
        System.out.println("撤销栈(" + undoStack.size() + "):");
        for (int i = undoStack.size() - 1; i >= 0; i--) {
            System.out.println("  " + (i+1) + ". " + undoStack.get(i).getDescription());
        }
        
        System.out.println("重做栈(" + redoStack.size() + "):");
        for (int i = redoStack.size() - 1; i >= 0; i--) {
            System.out.println("  " + (i+1) + ". " + redoStack.get(i).getDescription());
        }
    }
    
    public int getUndoCount() { return undoStack.size(); }
    public int getRedoCount() { return redoStack.size(); }
}
```

### 使用示例

```java
class TextEditorDemo {
    public static void main(String[] args) {
        System.out.println("=== 文本编辑器撤销演示 ===\n");
        
        TextEditor editor = new TextEditor();
        CommandHistory history = new CommandHistory();
        
        // ===== 第1阶段：基本插入和删除 =====
        System.out.println("--- 第1阶段：编辑文本 ---");
        history.execute(new InsertTextCommand(editor, "Hello", 0));
        history.execute(new InsertTextCommand(editor, " World", 5));
        history.execute(new InsertTextCommand(editor, "!", 11));
        System.out.println("当前文本: " + editor.getText());
        
        // ===== 第2阶段：替换操作 =====
        System.out.println("\n--- 第2阶段：替换操作 ---");
        history.execute(new ReplaceTextCommand(editor, 6, 11, "Python"));
        System.out.println("当前文本: " + editor.getText());
        
        // ===== 第3阶段：撤销操作 =====
        System.out.println("\n--- 第3阶段：撤销操作 ---");
        history.undo();
        System.out.println("撤销后: " + editor.getText());
        
        history.undo();
        System.out.println("再次撤销: " + editor.getText());
        
        // ===== 第4阶段：重做操作 =====
        System.out.println("\n--- 第4阶段：重做操作 ---");
        history.redo();
        System.out.println("重做后: " + editor.getText());
        
        // ===== 第5阶段：宏命令 =====
        System.out.println("\n--- 第5阶段：宏命令 ---");
        MacroCommand macro = new MacroCommand("格式化页面");
        macro.addCommand(new InsertTextCommand(editor, "\n---\n", 0));
        macro.addCommand(new InsertTextCommand(editor, "\n---", editor.getText().length()));
        history.execute(macro);
        System.out.println("宏执行后: " + editor.getText());
        
        // 打印历史
        history.printHistory();
    }
}
```

---

## Python: 异步命令队列

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from threading import Thread
import queue
import time

class AsyncCommand(ABC):
    """异步命令接口"""
    
    def __init__(self):
        self.executed_time: Optional[datetime] = None
        self.callback: Optional[callable] = None
    
    @abstractmethod
    def execute(self) -> any:
        """执行命令，返回结果"""
        pass
    
    def set_callback(self, callback):
        """设置回调函数"""
        self.callback = callback
        return self

class DatabaseQueryCommand(AsyncCommand):
    """数据库查询命令"""
    
    def __init__(self, query: str):
        super().__init__()
        self.query = query
        self.result = None
        self.error = None
    
    def execute(self) -> dict:
        """模拟数据库查询"""
        print(f"[DB] 执行查询: {self.query}")
        
        try:
            # 模拟数据库延迟
            time.sleep(1)
            
            self.executed_time = datetime.now()
            self.result = {"status": "success", "rows": 100}
            
            print(f"[DB] 查询完成: 返回{self.result['rows']}行")
            
            if self.callback:
                self.callback(self.result)
            
            return self.result
            
        except Exception as e:
            self.error = str(e)
            print(f"[DB] 查询失败: {e}")
            return None

class APICallCommand(AsyncCommand):
    """API调用命令"""
    
    def __init__(self, endpoint: str):
        super().__init__()
        self.endpoint = endpoint
        self.response = None
    
    def execute(self) -> dict:
        """模拟API调用"""
        print(f"[API] 调用端点: {self.endpoint}")
        
        # 模拟网络延迟
        time.sleep(0.5)
        
        self.executed_time = datetime.now()
        self.response = {"code": 200, "data": []}
        
        print(f"[API] 响应: {self.response}")
        
        if self.callback:
            self.callback(self.response)
        
        return self.response

class CommandQueue:
    """异步命令队列"""
    
    def __init__(self, max_workers: int = 3):
        self.queue = queue.Queue()
        self.results = {}
        self.workers = []
        self.max_workers = max_workers
        self.running = False
    
    def submit(self, cmd: AsyncCommand, cmd_id: str = None) -> str:
        """提交命令到队列"""
        cmd_id = cmd_id or f"CMD_{time.time()}"
        self.queue.put((cmd_id, cmd))
        print(f"[Queue] 添加命令: {cmd_id}")
        return cmd_id
    
    def start(self):
        """启动工作线程"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        print(f"[Queue] 启动{self.max_workers}个工作线程")
    
    def _worker(self):
        """工作线程循环"""
        while self.running:
            try:
                cmd_id, cmd = self.queue.get(timeout=1)
                print(f"[Worker] 执行: {cmd_id}")
                
                result = cmd.execute()
                self.results[cmd_id] = result
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Worker] 错误: {e}")
    
    def wait_for_result(self, cmd_id: str, timeout: int = 10) -> Optional[dict]:
        """等待命令结果"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if cmd_id in self.results:
                return self.results[cmd_id]
            time.sleep(0.1)
        
        return None
    
    def shutdown(self):
        """关闭队列"""
        self.queue.join()
        self.running = False
        print("[Queue] 队列已关闭")

# 使用示例
if __name__ == "__main__":
    print("=== 异步命令队列示例 ===\n")
    
    queue_manager = CommandQueue(max_workers=2)
    queue_manager.start()
    
    # 提交数据库查询
    cmd_ids = []
    
    cmd1_id = queue_manager.submit(
        DatabaseQueryCommand("SELECT * FROM users WHERE active=1"),
        "query_users"
    )
    cmd_ids.append(cmd1_id)
    
    # 提交API调用
    cmd2_id = queue_manager.submit(
        APICallCommand("https://api.example.com/data"),
        "fetch_data"
    )
    cmd_ids.append(cmd2_id)
    
    # 等待结果
    print("\n--- 等待结果 ---")
    for cmd_id in cmd_ids:
        result = queue_manager.wait_for_result(cmd_id, timeout=5)
        print(f"[Result] {cmd_id}: {result}")
    
    queue_manager.shutdown()
```

---

## TypeScript: 事务管理

```typescript
/**
 * 事务命令系统
 */

interface TransactionCommand {
    execute(): Promise<void>;
    rollback(): Promise<void>;
    getDescription(): string;
}

class Transaction {
    private commands: TransactionCommand[] = [];
    private executedCommands: TransactionCommand[] = [];
    private isActive = false;
    
    public addCommand(cmd: TransactionCommand): this {
        this.commands.push(cmd);
        return this;
    }
    
    public async commit(): Promise<boolean> {
        if (this.isActive) {
            throw new Error("事务已在进行中");
        }
        
        this.isActive = true;
        
        try {
            console.log("[Transaction] 开始提交事务...");
            
            for (const cmd of this.commands) {
                console.log(`[Commit] ${cmd.getDescription()}`);
                await cmd.execute();
                this.executedCommands.push(cmd);
            }
            
            console.log("[Transaction] 事务提交成功!");
            this.isActive = false;
            return true;
            
        } catch (error) {
            console.error("[Transaction] 提交失败，开始回滚...", error);
            await this.rollback();
            throw error;
        }
    }
    
    public async rollback(): Promise<void> {
        console.log("[Transaction] 执行回滚...");
        
        // 反向执行回滚
        for (let i = this.executedCommands.length - 1; i >= 0; i--) {
            const cmd = this.executedCommands[i];
            console.log(`[Rollback] ${cmd.getDescription()}`);
            await cmd.rollback();
        }
        
        this.executedCommands = [];
        this.isActive = false;
        console.log("[Transaction] 回滚完成");
    }
}

// ===== 具体命令 =====

class UpdateUserCommand implements TransactionCommand {
    private userId: string;
    private oldData: any;
    private newData: any;
    
    constructor(userId: string, newData: any, oldData: any = null) {
        this.userId = userId;
        this.newData = newData;
        this.oldData = oldData;
    }
    
    async execute(): Promise<void> {
        console.log(`  → 更新用户 ${this.userId} 的数据`);
        // 模拟数据库更新
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    async rollback(): Promise<void> {
        console.log(`  ← 恢复用户 ${this.userId} 的旧数据`);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    getDescription(): string {
        return `UpdateUser(${this.userId})`;
    }
}

class CreateOrderCommand implements TransactionCommand {
    private orderId: string;
    private items: any[];
    
    constructor(orderId: string, items: any[]) {
        this.orderId = orderId;
        this.items = items;
    }
    
    async execute(): Promise<void> {
        console.log(`  → 创建订单 ${this.orderId} (${this.items.length}项)`);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    async rollback(): Promise<void> {
        console.log(`  ← 删除订单 ${this.orderId}`);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    getDescription(): string {
        return `CreateOrder(${this.orderId})`;
    }
}

class UpdateInventoryCommand implements TransactionCommand {
    private itemId: string;
    private quantity: number;
    
    constructor(itemId: string, quantity: number) {
        this.itemId = itemId;
        this.quantity = quantity;
    }
    
    async execute(): Promise<void> {
        console.log(`  → 扣减库存 ${this.itemId} (-${this.quantity})`);
        
        // 模拟库存不足的错误
        if (Math.random() > 0.7) {
            throw new Error(`库存不足: ${this.itemId}`);
        }
        
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    async rollback(): Promise<void> {
        console.log(`  ← 恢复库存 ${this.itemId} (+${this.quantity})`);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    getDescription(): string {
        return `UpdateInventory(${this.itemId}, -${this.quantity})`;
    }
}

// ===== 使用示例 =====

async function main() {
    console.log("=== 事务管理示例 ===\n");
    
    const transaction = new Transaction();
    
    // 构建事务
    transaction
        .addCommand(new UpdateUserCommand("U001", {age: 30}, {age: 28}))
        .addCommand(new CreateOrderCommand("ORD123", [{id: 'P001', qty: 2}]))
        .addCommand(new UpdateInventoryCommand("P001", 2));
    
    // 执行事务
    try {
        await transaction.commit();
    } catch (error) {
        console.error("[Main] 事务执行失败");
    }
}

main().catch(console.error);
```

---

## 单元测试

```java
@Test
public void testBasicCommandExecution() {
    TextEditor editor = new TextEditor();
    Command cmd = new InsertTextCommand(editor, "Test", 0);
    
    cmd.execute();
    assertEquals("Test", editor.getText());
    
    cmd.undo();
    assertEquals("", editor.getText());
}

@Test
public void testCommandHistory() {
    TextEditor editor = new TextEditor();
    CommandHistory history = new CommandHistory();
    
    history.execute(new InsertTextCommand(editor, "A", 0));
    history.execute(new InsertTextCommand(editor, "B", 1));
    
    assertEquals(2, history.getUndoCount());
    
    history.undo();
    assertEquals(1, history.getUndoCount());
    assertEquals(1, history.getRedoCount());
}

@Test
public void testMacroCommand() {
    TextEditor editor = new TextEditor();
    MacroCommand macro = new MacroCommand("测试宏");
    
    macro.addCommand(new InsertTextCommand(editor, "Hello", 0));
    macro.addCommand(new InsertTextCommand(editor, " ", 5));
    macro.addCommand(new InsertTextCommand(editor, "World", 6));
    
    macro.execute();
    assertEquals("Hello World", editor.getText());
    
    macro.undo();
    assertEquals("", editor.getText());
}

@Test(expected = IllegalStateException.class)
public void testInvalidCommandSequence() {
    TextEditor editor = new TextEditor();
    
    // 试图在空编辑器上删除
    new DeleteTextCommand(editor, 0, 5).execute();
}

@Test
public void testHistorySizeLimit() {
    TextEditor editor = new TextEditor();
    CommandHistory history = new CommandHistory();
    
    // 执行超过最大历史数的操作
    for (int i = 0; i < 60; i++) {
        history.execute(new InsertTextCommand(editor, String.valueOf(i % 10), 0));
    }
    
    // 只保留最近50个
    assertTrue(history.getUndoCount() <= 50);
}
```

---

## 性能对比表

| 实现方式 | 执行速度 | 内存占用 | 撤销支持 | 并发安全 |
|---------|---------|---------|--------|---------|
| 基础命令 | ⭐⭐⭐⭐⭐ | 低 | ✓ | ✗ |
| 参数化命令 | ⭐⭐⭐⭐ | 低-中 | ✓ | ✗ |
| 异步命令 | ⭐⭐⭐ | 中 | ✓ | ✓ |
| 宏命令 | ⭐⭐⭐ | 中 | ✓ | ✗ |
| 批量命令 | ⭐⭐⭐⭐ | 中-高 | ✓ | ✓ |
| 事务命令 | ⭐⭐ | 高 | ✓ | ✓ |

---

## 何时使用命令模式

✅ **强烈推荐**:
- 支持撤销/重做系统（文本编辑器、图形工具）
- 事务管理系统
- 任务队列和后台处理
- 宏命令和批量操作
- 远程过程调用 (RPC)
- 日志系统和审计追踪

⚠️ **权衡使用**:
- 简单一次性操作（过度设计）
- 高频率小命令执行（性能开销）

❌ **不推荐**:
- 顺序固定的简单操作
- C 风格函数指针足够的场景

## 常见问题

**Q1: 如何处理大型撤销栈导致的内存溢出?**
- 使用大小限制和弱引用
- 实现命令压缩/合并机制
- 使用文件持久化存储历史

**Q2: 异步命令如何处理失败和重试?**
- 实现 retry() 方法
- 使用指数退避策略
- 记录失败原因便于调试

**Q3: 如何保证事务的原子性?**
- 提前验证所有前置条件
- 使用回滚栈保存执行状态
- 记录操作日志便于恢复
    // 测试代码
}
```
