# 接口隔离原则 - 参考实现

## 核心原理与设计

ISP：**客户端不应该被迫依赖它不使用的接口**。将臃肿接口拆分为小而专注的接口，让实现类只实现需要的能力。

---

## Java 参考实现

### 反面示例

```java
/**
 * ❌ 胖接口：强制实现所有功能
 */
public interface MultiFunctionDevice {
    void print(Document doc);
    void scan(Document doc);
    void fax(Document doc);
    void staple(Document doc);
}

public class SimplePrinter implements MultiFunctionDevice {
    @Override public void print(Document doc) {
        System.out.println("打印: " + doc.getName());
    }
    @Override public void scan(Document doc) {
        throw new UnsupportedOperationException("不支持扫描");
    }
    @Override public void fax(Document doc) {
        throw new UnsupportedOperationException("不支持传真");
    }
    @Override public void staple(Document doc) {
        throw new UnsupportedOperationException("不支持装订");
    }
}
```

### 正面示例

```java
/**
 * ✅ 接口隔离
 */
public interface Printer {
    void print(Document doc);
}

public interface Scanner {
    void scan(Document doc);
}

public interface Fax {
    void fax(Document doc);
}

// 简单打印机
public class SimplePrinter implements Printer {
    @Override
    public void print(Document doc) {
        System.out.println("打印: " + doc.getName());
    }
}

// 多功能设备实现多个接口
public class MultiFunctionPrinter implements Printer, Scanner, Fax {
    @Override public void print(Document doc) { /* 打印 */ }
    @Override public void scan(Document doc) { /* 扫描 */ }
    @Override public void fax(Document doc) { /* 传真 */ }
}

// 按角色拆分：数据存储
public interface Readable {
    String read(String key);
    boolean exists(String key);
}

public interface Writable {
    void write(String key, String value);
    void delete(String key);
}

public interface Backupable {
    void backup();
    void restore(String backupId);
}

// 组合接口
public interface ReadWriteStore extends Readable, Writable {}

// 缓存只需读写
public class Cache implements Readable, Writable {
    private final Map<String, String> data = new HashMap<>();
    public String read(String key) { return data.get(key); }
    public boolean exists(String key) { return data.containsKey(key); }
    public void write(String key, String value) { data.put(key, value); }
    public void delete(String key) { data.remove(key); }
}

// 数据库实现所有接口
public class Database implements ReadWriteStore, Backupable {
    public String read(String key) { /* ... */ return ""; }
    public boolean exists(String key) { /* ... */ return false; }
    public void write(String key, String value) { /* ... */ }
    public void delete(String key) { /* ... */ }
    public void backup() { /* ... */ }
    public void restore(String backupId) { /* ... */ }
}

// 客户端按需依赖
public class ReportService {
    private final Readable store;  // 只需要读
    public ReportService(Readable store) { this.store = store; }
}

public class ImportService {
    private final Writable store;  // 只需要写
    public ImportService(Writable store) { this.store = store; }
}
```

---

## Python 参考实现

```python
from abc import ABC, abstractmethod

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

# 缓存只实现需要的
class Cache(Readable, Writable):
    def __init__(self):
        self._data = {}
    def read(self, key: str) -> str:
        return self._data.get(key, "")
    def write(self, key: str, value: str):
        self._data[key] = value

# 数据库实现所有
class Database(Readable, Writable, Deletable):
    def read(self, key: str) -> str: ...
    def write(self, key: str, value: str): ...
    def delete(self, key: str): ...

# 客户端按需依赖
class ReportGenerator:
    def __init__(self, store: Readable):
        self.store = store  # 只依赖 Readable
```

---

## TypeScript 参考实现

```typescript
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

// 只读场景
class UserProfilePage {
    constructor(private reader: UserReader) {}
    showProfile(id: string) {
        return this.reader.getUser(id);
    }
}

// 管理后台需要更多功能
class AdminPanel {
    constructor(
        private reader: UserReader,
        private writer: UserWriter,
        private notifier: UserNotifier
    ) {}
}
```

---

## 单元测试示例

```java
class SimplePrinterTest {
    @Test
    void testPrint() {
        SimplePrinter printer = new SimplePrinter();
        printer.print(new Document("test.pdf"));
        // 不需要测试 scan/fax — SimplePrinter 没有这些方法
    }
}

class ReportServiceTest {
    @Test
    void testOnlyNeedsReadable() {
        Readable mockStore = mock(Readable.class);
        when(mockStore.read("key")).thenReturn("value");
        ReportService service = new ReportService(mockStore);
        // 只需 mock Readable，不需要 mock Writable
    }
}
```

---

## 总结

| 指标 | 胖接口 | 隔离后 |
|------|--------|--------|
| 实现复杂度 | 高（空方法/异常） | 低（只实现需要的） |
| Mock 复杂度 | 高（mock 所有方法） | 低（只 mock 用到的） |
| 变更影响 | 大（修改影响所有实现） | 小（只影响相关实现） |
| 可复用性 | 低 | 高 |
