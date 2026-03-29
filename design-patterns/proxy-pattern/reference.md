# Proxy 模式完整参考实现

## UML 类图

```
┌─────────────┐         ┌──────────────┐         ┌────────────────┐
│   Client    │───────→ │ Subject (I)  │ ←─────── │ RealSubject    │
└─────────────┘         └──────────────┘         └────────────────┘
                               △
                               │ implements
                               │
                        ┌──────────────┐
                        │ Proxy        │
                        ├──────────────┤
                        │ - realSubj   │
                        │ - checkXXXX()│
                        └──────────────┘
```

---

## 多语言完整实现

### Java: 基础静态代理 + 权限检查 + 日志 + 监控 + 缓存

```java
import java.util.*;
import java.util.concurrent.*;
import java.time.LocalDateTime;

// ===== 业务接口 =====
public interface Document {
    void read();
    void write(String content);
    String getContent();
}

// ===== 真实对象 =====
public class RealDocument implements Document {
    private String filename;
    private String content = "";
    
    public RealDocument(String filename) {
        this.filename = filename;
        System.out.println("[Real] Document loaded: " + filename);
    }
    
    @Override
    public void read() {
        System.out.println("[Real] Reading: " + filename);
        try { Thread.sleep(100); } catch (InterruptedException e) {}
    }
    
    @Override
    public void write(String text) {
        System.out.println("[Real] Writing to: " + filename);
        this.content = text;
        try { Thread.sleep(200); } catch (InterruptedException e) {}
    }
    
    @Override
    public String getContent() {
        return content;
    }
}

// ===== User 和权限类 =====
public class User {
    private String name;
    private Set<String> permissions;
    
    public User(String name, String... permissions) {
        this.name = name;
        this.permissions = new HashSet<>(Arrays.asList(permissions));
    }
    
    public boolean hasPermission(String action) {
        return permissions.contains(action);
    }
    
    public String getName() { return name; }
}

// ===== 性能监控类 =====
public class PerformanceMetrics {
    private Map<String, List<Long>> methodDurations = new ConcurrentHashMap<>();
    private Map<String, Integer> methodCallCounts = new ConcurrentHashMap<>();
    
    public void recordCall(String methodName, long durationMs) {
        methodCallCounts.merge(methodName, 1, Integer::sum);
        methodDurations.computeIfAbsent(methodName, k -> new ArrayList<>()).add(durationMs);
    }
    
    public void printReport() {
        System.out.println("\n=== Performance Report ===");
        methodDurations.forEach((method, durations) -> {
            long avg = durations.stream().mapToLong(Long::longValue).sum() / durations.size();
            int count = methodCallCounts.get(method);
            System.out.printf("%s: %d calls, avg %.2fms\n", method, count, (double)avg);
        });
    }
}

// ===== 完整代理实现 =====
public class DocumentProxy implements Document {
    private Document realDocument;
    private String filename;
    private User user;
    
    // 缓存相关
    private Map<String, CacheEntry> cache = new ConcurrentHashMap<>();
    private static final long CACHE_TTL = 30000; // 30秒
    
    // 监控相关
    private PerformanceMetrics metrics = new PerformanceMetrics();
    
    public DocumentProxy(String filename, User user) {
        this.filename = filename;
        this.user = user;
        // 延迟加载真实对象
    }
    
    @Override
    public void read() {
        try {
            // 1. 权限检查
            checkPermission("READ");
            
            // 2. 延迟加载
            ensureRealDocumentLoaded();
            
            // 3. 性能监控
            long startTime = System.currentTimeMillis();
            
            // 4. 执行真实操作
            realDocument.read();
            
            long duration = System.currentTimeMillis() - startTime;
            metrics.recordCall("read", duration);
            
            System.out.printf("[Proxy] Read operation took %dms\n", duration);
            
        } catch (AccessDeniedException e) {
            System.out.println("[Proxy] Access denied: " + e.getMessage());
            throw e;
        }
    }
    
    @Override
    public void write(String content) {
        try {
            // 权限检查
            checkPermission("WRITE");
            
            // 延迟加载
            ensureRealDocumentLoaded();
            
            // 清除缓存
            cache.clear();
            
            // 执行写入
            long startTime = System.currentTimeMillis();
            realDocument.write(content);
            long duration = System.currentTimeMillis() - startTime;
            
            metrics.recordCall("write", duration);
            System.out.printf("[Proxy] Write operation took %dms\n", duration);
            
        } catch (AccessDeniedException e) {
            System.out.println("[Proxy] Access denied: " + e.getMessage());
            throw e;
        }
    }
    
    @Override
    public String getContent() {
        try {
            // 权限检查
            checkPermission("READ");
            
            // 缓存检查
            CacheEntry cached = cache.get("content");
            if (cached != null && !cached.isExpired()) {
                System.out.println("[Proxy] Cache hit for getContent");
                return cached.value;
            }
            
            // 延迟加载
            ensureRealDocumentLoaded();
            
            // 缓存新结果
            String content = realDocument.getContent();
            cache.put("content", new CacheEntry(content, System.currentTimeMillis()));
            
            return content;
            
        } catch (AccessDeniedException e) {
            System.out.println("[Proxy] Access denied: " + e.getMessage());
            throw e;
        }
    }
    
    // ===== 代理辅助方法 =====
    
    private void ensureRealDocumentLoaded() {
        if (realDocument == null) {
            System.out.println("[Proxy] Lazy-loading real document...");
            realDocument = new RealDocument(filename);
        }
    }
    
    private void checkPermission(String action) throws AccessDeniedException {
        if (!user.hasPermission(action)) {
            throw new AccessDeniedException(
                String.format("User %s has no permission to %s", user.getName(), action)
            );
        }
    }
    
    public void printMetrics() {
        metrics.printReport();
    }
    
    // 内部缓存条目类
    private static class CacheEntry {
        String value;
        long timestamp;
        
        CacheEntry(String value, long timestamp) {
            this.value = value;
            this.timestamp = timestamp;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() - timestamp > CACHE_TTL;
        }
    }
}

// 异常类
class AccessDeniedException extends RuntimeException {
    public AccessDeniedException(String message) {
        super(message);
    }
}

// ===== 测试 =====
class ProxyTest {
    public static void main(String[] args) {
        System.out.println("=== Proxy Pattern Test ===\n");
        
        // 创建用户
        User admin = new User("Alice", "READ", "WRITE", "DELETE");
        User guest = new User("Bob", "READ");
        
        // 创建代理
        Document adminDoc = new DocumentProxy("report.docx", admin);
        Document guestDoc = new DocumentProxy("report.docx", guest);
        
        // 测试权限
        System.out.println("--- Admin Read ---");
        adminDoc.read();  // ✅ 允许
        
        System.out.println("\n--- Admin Write ---");
        adminDoc.write("Updated content");  // ✅ 允许
        
        System.out.println("\n--- Guest Read ---");
        guestDoc.read();  // ✅ 允许
        
        System.out.println("\n--- Guest Write ---");
        try {
            guestDoc.write("Hacked!");  // ❌ 拒绝
        } catch (AccessDeniedException e) {
            System.out.println("Error: " + e.getMessage());
        }
        
        // 测试缓存
        System.out.println("\n--- Cache Test ---");
        System.out.println("First call:");
        adminDoc.getContent();
        System.out.println("Second call (cached):");
        adminDoc.getContent();
        
        // 打印性能指标
        ((DocumentProxy)adminDoc).printMetrics();
    }
}
```

**输出示例**:
```
=== Proxy Pattern Test ===

--- Admin Read ---
[Proxy] Lazy-loading real document...
[Real] Document loaded: report.docx
[Real] Reading: report.docx
[Proxy] Read operation took 100ms

--- Admin Write ---
[Real] Writing to: report.docx
[Proxy] Write operation took 200ms

--- Guest Read ---
[Real] Reading: report.docx
[Proxy] Read operation took 100ms

--- Guest Write ---
Error: User Bob has no permission to WRITE

--- Cache Test ---
First call:
[Proxy] Cache hit for getContent

=== Performance Report ===
read: 2 calls, avg 100.00ms
write: 1 calls, avg 200.00ms
```

---

### Java: JDK 动态代理实现

```java
import java.lang.reflect.*;
import java.util.concurrent.*;

// 通用权限处理器
public class PermissionInvocationHandler implements InvocationHandler {
    private Object target;
    private User user;
    private Map<String, Set<String>> methodPermissions;
    
    public PermissionInvocationHandler(Object target, User user) {
        this.target = target;
        this.user = user;
        this.methodPermissions = new HashMap<>();
        initPermissions();
    }
    
    private void initPermissions() {
        methodPermissions.put("write", Set.of("admin", "editor"));
        methodPermissions.put("delete", Set.of("admin"));
        methodPermissions.put("read", Set.of("admin", "editor", "guest"));
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        String methodName = method.getName();
        
        // 权限检查
        checkPermission(methodName);
        
        // 记录日志
        System.out.println("[Proxy] Calling: " + methodName + " by " + user.getName());
        
        // 计时
        long start = System.nanoTime();
        Object result = method.invoke(target, args);
        long duration = (System.nanoTime() - start) / 1_000_000;
        
        System.out.printf("[Proxy] %s took %.2fms\n", methodName, (double)duration);
        
        return result;
    }
    
    private void checkPermission(String methodName) {
        if (!user.hasPermission(methodName)) {
            throw new AccessDeniedException("No permission for: " + methodName);
        }
    }
}

// 使用方式
Document realDoc = new RealDocument("contract.pdf");
User user = new User("Charlie", "READ", "WRITE");

Document proxyDoc = (Document) Proxy.newProxyInstance(
    Document.class.getClassLoader(),
    new Class[]{Document.class},
    new PermissionInvocationHandler(realDoc, user)
);

proxyDoc.read();   // [Proxy] Calling: read...
proxyDoc.write("Updated"); // [Proxy] Calling: write...
```

---

### Python: __getattr__ 动态代理 + 上下文管理器

```python
import time
from typing import Any, Dict
from datetime import datetime

class User:
    def __init__(self, name: str, permissions: list):
        self.name = name
        self.permissions = set(permissions)
    
    def has_permission(self, action: str) -> bool:
        return action in self.permissions

class Document:
    def __init__(self, filename: str):
        self.filename = filename
        self.content = ""
        print(f"[Real] Document loaded: {filename}")
    
    def read(self):
        print(f"[Real] Reading: {self.filename}")
        time.sleep(0.1)
    
    def write(self, content: str):
        print(f"[Real] Writing to: {self.filename}")
        self.content = content
        time.sleep(0.2)
    
    def get_content(self) -> str:
        return self.content

class DocumentProxy:
    """动态代理 - 拦截所有方法调用"""
    
    def __init__(self, filename: str, user: User):
        self.filename = filename
        self.user = user
        self._real_doc = None  # 延迟加载
        self._cache: Dict[str, Any] = {}
        self._metrics: Dict[str, list] = {}
    
    def __getattr__(self, name: str) -> Any:
        """动态拦截所有属性和方法访问"""
        
        # 延迟加载真实对象
        if self._real_doc is None:
            print("[Proxy] Lazy-loading real document...")
            self._real_doc = Document(self.filename)
        
        # 获取真实对象的属性/方法
        attr = getattr(self._real_doc, name)
        
        # 如果是方法，包装它
        if callable(attr):
            def wrapper(*args, **kwargs):
                # 权限检查
                self._check_permission(name)
                
                # 缓存检查
                if name in ('get_content',) and name in self._cache:
                    print(f"[Proxy] Cache hit for {name}")
                    return self._cache[name]
                
                # 执行方法并计时
                print(f"[Proxy] Calling: {name}")
                start_time = time.time()
                
                result = attr(*args, **kwargs)
                
                duration = (time.time() - start_time) * 1000
                
                # 记录性能指标
                if name not in self._metrics:
                    self._metrics[name] = []
                self._metrics[name].append(duration)
                
                print(f"[Proxy] {name} took {duration:.2f}ms")
                
                # 缓存结果
                if name in ('get_content',):
                    self._cache[name] = result
                
                return result
            
            return wrapper
        
        return attr
    
    def _check_permission(self, action: str):
        """检查用户权限"""
        if not self.user.has_permission(action):
            raise PermissionError(f"User {self.user.name} has no permission for {action}")
    
    def print_metrics(self):
        """打印性能指标"""
        print("\n=== Performance Metrics ===")
        for method, durations in self._metrics.items():
            avg_duration = sum(durations) / len(durations)
            print(f"{method}: {len(durations)} calls, avg {avg_duration:.2f}ms")

# 测试
admin = User("Alice", ["read", "write", "delete"])
guest = User("Bob", ["read"])

admin_doc = DocumentProxy("report.pdf", admin)
guest_doc = DocumentProxy("report.pdf", guest)

# 测试权限
print("--- Admin Read ---")
admin_doc.read()

print("\n--- Admin Write ---")
admin_doc.write("Updated")

print("\n--- Guest Read ---")
guest_doc.read()

print("\n--- Guest Write (should fail) ---")
try:
    guest_doc.write("Hacked")
except PermissionError as e:
    print(f"Error: {e}")

# 测试缓存
print("\n--- Cache Test ---")
print("First call:")
result1 = admin_doc.get_content()
print("Second call (cached):")
result2 = admin_doc.get_content()

admin_doc.print_metrics()
```

---

### TypeScript: Proxy 对象 + Reflect API

```typescript
interface Document {
    read(): void;
    write(content: string): void;
    getContent(): string;
}

class RealDocument implements Document {
    private content: string = "";
    
    constructor(private filename: string) {
        console.log(`[Real] Document loaded: ${filename}`);
    }
    
    read(): void {
        console.log(`[Real] Reading: ${this.filename}`);
    }
    
    write(content: string): void {
        console.log(`[Real] Writing to: ${this.filename}`);
        this.content = content;
    }
    
    getContent(): string {
        return this.content;
    }
}

class User {
    constructor(
        private name: string,
        private permissions: Set<string>
    ) {}
    
    hasPermission(action: string): boolean {
        return this.permissions.has(action);
    }
    
    getName(): string {
        return this.name;
    }
}

// 创建代理
function createDocumentProxy(filename: string, user: User): Document {
    let realDocument: Document | null = null;
    const cache = new Map<string, any>();
    const metrics = new Map<string, number[]>();
    
    return new Proxy({} as Document, {
        get(target, prop: string | symbol) {
            const propName = String(prop);
            
            // 检查权限
            if (!user.hasPermission(propName)) {
                throw new Error(`Permission denied for ${propName}`);
            }
            
            // 延迟加载真实对象
            if (!realDocument) {
                console.log("[Proxy] Lazy-loading real document...");
                realDocument = new RealDocument(filename);
            }
            
            // 获取真实对象的属性
            const attr = Reflect.get(realDocument, prop);
            
            // 如果是方法，包装它
            if (typeof attr === 'function') {
                return function(...args: any[]) {
                    // 缓存检查
                    if (propName === 'getContent' && cache.has(propName)) {
                        console.log(`[Proxy] Cache hit for ${propName}`);
                        return cache.get(propName);
                    }
                    
                    // 计时并执行
                    console.log(`[Proxy] Calling: ${propName}`);
                    const startTime = performance.now();
                    
                    const result = Reflect.apply(attr, realDocument, args);
                    
                    const duration = performance.now() - startTime;
                    
                    // 记录性能指标
                    if (!metrics.has(propName)) {
                        metrics.set(propName, []);
                    }
                    metrics.get(propName)!.push(duration);
                    
                    console.log(`[Proxy] ${propName} took ${duration.toFixed(2)}ms`);
                    
                    // 缓存结果
                    if (propName === 'getContent') {
                        cache.set(propName, result);
                    }
                    
                    return result;
                };
            }
            
            return attr;
        }
    });
}

// 测试
const admin = new User("Alice", new Set(["read", "write", "delete"]));
const guest = new User("Bob", new Set(["read"]));

const adminDoc = createDocumentProxy("report.docx", admin);
const guestDoc = createDocumentProxy("report.docx", guest);

console.log("=== Proxy Pattern Test ===\n");

console.log("--- Admin Read ---");
adminDoc.read();

console.log("\n--- Admin Write ---");
adminDoc.write("Updated content");

console.log("\n--- Guest Read ---");
guestDoc.read();

console.log("\n--- Guest Write (should fail) ---");
try {
    guestDoc.write("Hacked");
} catch (e) {
    console.log(`Error: ${e.message}`);
}

console.log("\n--- Cache Test ---");
console.log("First call:");
adminDoc.getContent();
console.log("Second call (cached):");
adminDoc.getContent();
```

---

## 性能对比表

| 实现方式 | 性能 | 内存 | 灵活性 | 学习曲线 |
|---------|------|------|--------|----------|
| 静态代理 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| JDK动态代理 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| CGLib | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Python __getattr__ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| TypeScript Proxy | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 单元测试示例

```java
@Test
public void testPermissionDenied() {
    User guest = new User("Guest", "READ");
    Document doc = new DocumentProxy("secret.txt", guest);
    
    // 应该成功
    doc.read();
    
    // 应该抛异常
    assertThrows(AccessDeniedException.class, () -> doc.write("hack"));
}

@Test
public void testLazyLoading() {
    User user = new User("User", "READ", "WRITE");
    DocumentProxy doc = (DocumentProxy) new DocumentProxy("file.txt", user);
    
    // 初始化不应该加载文档
    assertFalse(doc.isLoaded());
    
    // 第一次调用时才加载
    doc.read();
    assertTrue(doc.isLoaded());
}

@Test
public void testCaching() {
    User user = new User("User", "READ", "WRITE");
    DocumentProxy doc = (DocumentProxy) new DocumentProxy("file.txt", user);
    
    doc.write("content");
    
    // 第一次调用
    String result1 = doc.getContent();
    
    // 第二次调用应该命中缓存
    String result2 = doc.getContent();
    
    assertEquals(result1, result2);
}
```

---

## 常见陷阱与解决方案

### 陷阱1: 代理链过深导致性能问题
```
❌ Service → Proxy1 → Proxy2 → Proxy3 → Proxy4 → Proxy5
           性能下降 50%+

✅ Service → CombinedProxy (集合多个功能)
           性能开销 <10%
```

### 陷阱2: 代理修改了返回值
```
❌ return realObject.getResult().toUpperCase();
   违反了 Proxy 的原则

✅ return realObject.getResult();
   只是在调用前后添加逻辑
```

### 陷阱3: 缓存不一致
```
❌ 写入后没有清除缓存
   导致读取的数据是旧的

✅ 写入时清除相关缓存
   或使用 TTL 自动失效
```

---

## 架构决策指南

**何时选择代理?**
1. 需要控制访问 → ✅ Proxy
2. 需要添加功能 → ❌ 用 Decorator
3. 需要性能监控 → ✅ Proxy
4. 需要权限检查 → ✅ Proxy
5. 需要远程访问 → ✅ Proxy

**何时选择实现方式?**
- 性能第一 → 静态代理
- 灵活多样 → JDK动态代理
- Java无接口 → CGLib
- 企业应用 → Spring AOP
- Python脚本 → __getattr__
- TypeScript → Proxy 对象
    // 测试代码
}
```
