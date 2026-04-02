---
name: 接口隔离原则
description: "客户端不应该被迫依赖它不使用的接口。多个专用接口优于一个通用接口。"
license: MIT
---

# 接口隔离原则 (Interface Segregation Principle, ISP)

## 概述

接口隔离原则强调：**不应该强迫客户端依赖它不需要的接口**。将臃肿的接口拆分为更小、更具体的接口。

**核心思想**：
- 接口应该小而专注，只包含客户端需要的方法
- 一个类可以实现多个接口，而非一个大接口
- 避免"胖接口"，减少不必要的依赖
- 接口的粒度应由客户端的需求决定

**关键指标**：
- 实现类中没有空方法或抛 `UnsupportedOperationException` 的方法
- 每个接口的方法数 ≤ 5
- 接口变更影响的实现类数量最小化

## 何时使用

**始终使用**：
- 接口方法超过 5 个
- 实现类只用了接口中部分方法
- 不同客户端使用同一接口的不同子集
- 接口修改频繁影响不相关的实现类

**触发短语**：
- "实现了接口但好几个方法是空的"
- "只需要用其中两个方法却被迫实现了全部"
- "修改一个方法签名导致大量类需要改动"

## 实现方式

### 经典案例：多功能设备

```java
// ❌ 胖接口：强制实现所有功能
public interface MultiFunctionDevice {
    void print(Document doc);
    void scan(Document doc);
    void fax(Document doc);
    void staple(Document doc);
}

// 简单打印机被迫实现不需要的方法
public class SimplePrinter implements MultiFunctionDevice {
    @Override
    public void print(Document doc) {
        System.out.println("打印文档: " + doc.getName());
    }

    @Override
    public void scan(Document doc) {
        throw new UnsupportedOperationException("不支持扫描");
    }

    @Override
    public void fax(Document doc) {
        throw new UnsupportedOperationException("不支持传真");
    }

    @Override
    public void staple(Document doc) {
        throw new UnsupportedOperationException("不支持装订");
    }
}
```

```java
// ✅ 接口隔离：按职责拆分
public interface Printer {
    void print(Document doc);
}

public interface Scanner {
    void scan(Document doc);
}

public interface Fax {
    void fax(Document doc);
}

// 简单打印机只实现需要的接口
public class SimplePrinter implements Printer {
    @Override
    public void print(Document doc) {
        System.out.println("打印文档: " + doc.getName());
    }
}

// 多功能设备实现多个接口
public class MultiFunctionPrinter implements Printer, Scanner, Fax {
    @Override
    public void print(Document doc) { /* 打印实现 */ }

    @Override
    public void scan(Document doc) { /* 扫描实现 */ }

    @Override
    public void fax(Document doc) { /* 传真实现 */ }
}
```

### 经典案例：工人接口

```java
// ❌ 胖接口
public interface Worker {
    void work();
    void eat();
    void sleep();
}

// 机器人不需要吃饭和睡觉
public class Robot implements Worker {
    @Override
    public void work() { System.out.println("工作中..."); }

    @Override
    public void eat() { /* 空实现 */ }

    @Override
    public void sleep() { /* 空实现 */ }
}

// ✅ 拆分接口
public interface Workable {
    void work();
}

public interface Feedable {
    void eat();
}

public interface Restable {
    void sleep();
}

public class HumanWorker implements Workable, Feedable, Restable {
    @Override
    public void work() { System.out.println("人类工作中"); }
    @Override
    public void eat() { System.out.println("午餐时间"); }
    @Override
    public void sleep() { System.out.println("休息中"); }
}

public class Robot implements Workable {
    @Override
    public void work() { System.out.println("机器人工作中"); }
    // 不需要 eat 和 sleep
}
```

## 违反 ISP 的信号

```
□ 实现类中有空方法体
□ 方法实现中抛出 UnsupportedOperationException
□ 实现类只使用接口 30% 以下的方法
□ 接口修改导致大量不相关的类需要重新编译
□ 需要通过 null 检查或条件判断来避免调用某些方法
□ 接口方法超过 7 个
```

## 代码示例 - 完整实现

### Python

```python
from abc import ABC, abstractmethod

# ❌ 胖接口
class DataStore(ABC):
    @abstractmethod
    def read(self, key: str) -> str: pass

    @abstractmethod
    def write(self, key: str, value: str): pass

    @abstractmethod
    def delete(self, key: str): pass

    @abstractmethod
    def list_keys(self) -> list: pass

    @abstractmethod
    def backup(self): pass

    @abstractmethod
    def restore(self, backup_id: str): pass

# 缓存只需要读写，被迫实现 backup/restore
class Cache(DataStore):
    def backup(self): pass       # 空实现
    def restore(self, backup_id): pass  # 空实现


# ✅ 接口隔离
class Readable(ABC):
    @abstractmethod
    def read(self, key: str) -> str: pass

class Writable(ABC):
    @abstractmethod
    def write(self, key: str, value: str): pass

class Deletable(ABC):
    @abstractmethod
    def delete(self, key: str): pass

class Backupable(ABC):
    @abstractmethod
    def backup(self): pass

    @abstractmethod
    def restore(self, backup_id: str): pass

# 缓存只实现需要的接口
class Cache(Readable, Writable):
    def __init__(self):
        self._data = {}

    def read(self, key: str) -> str:
        return self._data.get(key, "")

    def write(self, key: str, value: str):
        self._data[key] = value

# 数据库实现所有接口
class Database(Readable, Writable, Deletable, Backupable):
    def read(self, key: str) -> str: ...
    def write(self, key: str, value: str): ...
    def delete(self, key: str): ...
    def backup(self): ...
    def restore(self, backup_id: str): ...
```

### TypeScript

```typescript
// ❌ 胖接口
interface UserService {
    getUser(id: string): User;
    createUser(data: CreateUserDTO): User;
    updateUser(id: string, data: UpdateUserDTO): User;
    deleteUser(id: string): void;
    sendEmail(userId: string, template: string): void;
    generateReport(userId: string): Report;
    exportToCSV(userIds: string[]): Buffer;
}

// ✅ 接口隔离
interface UserReader {
    getUser(id: string): User;
}

interface UserWriter {
    createUser(data: CreateUserDTO): User;
    updateUser(id: string, data: UpdateUserDTO): User;
    deleteUser(id: string): void;
}

interface UserNotifier {
    sendEmail(userId: string, template: string): void;
}

interface UserReporter {
    generateReport(userId: string): Report;
    exportToCSV(userIds: string[]): Buffer;
}

// 只读服务只依赖 UserReader
class UserProfilePage {
    constructor(private userReader: UserReader) {}

    async showProfile(id: string) {
        const user = this.userReader.getUser(id);
        // 只需要读取，不依赖写入和通知
    }
}

// 管理后台需要所有功能
class AdminPanel {
    constructor(
        private reader: UserReader,
        private writer: UserWriter,
        private notifier: UserNotifier,
        private reporter: UserReporter
    ) {}
}
```

### Java - 接口组合

```java
// 通过接口组合创建复合接口
public interface ReadableStore {
    String read(String key);
    boolean exists(String key);
}

public interface WritableStore {
    void write(String key, String value);
    void delete(String key);
}

// 组合接口：需要读写的场景
public interface ReadWriteStore extends ReadableStore, WritableStore {
}

// 客户端按需依赖
public class ReportService {
    private final ReadableStore store;  // 只需要读

    public ReportService(ReadableStore store) {
        this.store = store;
    }
}

public class ImportService {
    private final WritableStore store;  // 只需要写

    public ImportService(WritableStore store) {
        this.store = store;
    }
}
```

## 优缺点分析

### ✅ 优点

1. **降低耦合** - 客户端只依赖需要的方法
2. **提高内聚** - 每个接口职责明确
3. **便于维护** - 接口修改影响范围小
4. **增强灵活性** - 实现类自由组合接口
5. **改善可测试性** - mock 更简单，只 mock 需要的接口

### ❌ 缺点

1. **接口数量增多** - 需要管理更多接口
2. **设计复杂度** - 需要准确划分接口边界
3. **过度拆分风险** - 每个方法一个接口是反模式

## 最佳实践

### 1. 按角色拆分接口

```
同一个实体，不同角色看到不同的接口：
- UserReader: 前端展示层使用
- UserWriter: 管理后台使用
- UserAuth:   认证模块使用
```

### 2. 接口粒度控制

```
✅ 合理的粒度：3-5 个方法
❌ 太细：1 个方法（除非是函数式接口）
❌ 太粗：10+ 个方法

判断标准：接口中的所有方法是否总是被一起使用？
- 是 → 保持在一个接口中
- 否 → 拆分
```

### 3. 从客户端角度设计接口

```java
// 先看客户端需要什么，再设计接口
// 而不是先设计一个大接口再让客户端去适应

// Step 1: 分析客户端需求
// - 展示页面只需 read
// - 编辑页面需要 read + write
// - 管理后台需要 read + write + delete + export

// Step 2: 按需求拆分接口
public interface Readable { ... }
public interface Writable { ... }
public interface Deletable { ... }
public interface Exportable { ... }
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [SRP](../single-responsibility-principle/) | SRP 拆分类的职责，ISP 拆分接口的职责 |
| [LSP](../liskov-substitution-principle/) | ISP 避免子类被迫实现无关方法，减少 LSP 违反 |
| [OCP](../open-closed-principle/) | 细粒度接口更容易扩展新实现 |
| [DIP](../dependency-inversion-principle/) | DIP 依赖抽象，ISP 确保抽象足够精确 |

## 总结

**ISP 核心**：
- 接口应小而专注
- 客户端不依赖不需要的方法
- 多个专用接口优于一个通用接口

**实践方法**：
- 从客户端需求出发设计接口
- 按角色拆分胖接口
- 使用接口组合构建复合能力
- 保持接口 3-5 个方法的粒度

**违反信号**：
- 空方法实现
- UnsupportedOperationException
- 实现类只用了接口部分方法
