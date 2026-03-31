---
name: Prototype
description: "通过克隆现有实例来创建对象"
license: MIT
---

# Prototype Pattern (原型模式)

## 核心概念

**Prototype** 是一种**创建型设计模式**，通过克隆现有实例(原型)来创建新对象，而不是通过调用构造函数。

### 核心原理
- 🔄 **复制而非构造** - 复制一个已存在的对象
- ⚡ **性能优化** - 避免复杂的初始化
- 🔀 **状态保留** - 新对象继承原型的状态
- 📦 **运行时灵活** - 在运行时选择要克隆的对象

### 关键问题：浅拷贝 vs 深拷贝

这是Prototype模式最关键的问题！

```java
// 浅拷贝(Shallow Copy) - 只复制引用
public class ShallowCopy {
    public User clone() {
        User copy = new User();
        copy.id = this.id;           // ✅ 基本类型复制
        copy.name = this.name;       // ✅ String复制（特殊）
        copy.address = this.address; // ❌ 对象引用复制 → 共享！
        return copy;
    }
}

// 问题示例
User original = createUser();
User copy = original.clone();
copy.getAddress().setCity("Beijing");  // ❌ 修改了原对象的Address！

assert original.getAddress().getCity().equals("Beijing");  // 原对象也变了！

// 深拷贝(Deep Copy) - 递归复制所有对象
public class DeepCopy {
    public User deepClone() {
        User copy = new User();
        copy.id = this.id;
        copy.name = this.name;
        copy.address = this.address.deepClone();  // ✅ 递归复制
        return copy;
    }
}

// 正确
User original = createUser();
User copy = original.deepClone();
copy.getAddress().setCity("Beijing");  // ✅ 只影响副本

assert original.getAddress().getCity().equals("Shanghai");  // 原对象不变！
```

---

## 何时使用

**始终使用**:
1. **复制成本远低于创建成本** - 对象初始化复杂且耗时
   - 数据库连接、配置对象、大图片...
2. **需要保留对象完整状态** - 包括内部细节
   - 数据库记录、缓存快照、编辑历史...
3. **对象创建过程不透明** - 第三方库对象
4. **需要独立对象副本** - 避免状态污染

**触发短语**:
- "如何快速创建相同配置的对象？"
- "需要对象的完整备份"
- "对象初始化很复杂"
- "数据库记录克隆"
- "UI组件模板复制"
- "缓存快照"
- "撤销/重做"

**真实场景检查**:

| 场景 | 是否适合 | 原因 |
|------|---------|------|
| 创建用户对象 | ⚠️ 否 | 创建成本低，直接new即可 |
| 克隆数据库记录 | ✅ 是 | 包含许多字段和关系，克隆更简单 |
| 复制配置对象 | ✅ 是 | 配置复杂，拷贝比重新配置快 |
| 实现撤销功能 | ✅ 是 | 需要保存完整状态 |
| 游戏保存系统 | ✅ 是 | 游戏状态复杂，深拷贝很要紧 |

---

## 基本结构

### UML类图

```
        ┌─────────────┐
        │  Prototype  │
        │─────────────│
        │ +clone()    │
        └──────┬──────┘
               △
               │
        ┌──────┴─────────┐
        │                │
   ┌────┴────┐    ┌─────┴───┐
   │Concrete1│    │Concrete2│
   │+clone() │    │+clone() │
   └─────────┘    └─────────┘

Client
  ↓
  prototype.clone()  → 快速创建副本
```

### 参与者

1. **Prototype** - 定义clone方法
2. **ConcretePrototype** - 实现clone方法
3. **Client** - 调用clone()创建新对象
4. **PrototypeRegistry** - (可选) 管理原型实例

---

## 4种实现方法

### 方法1: Java Cloneable接口 (浅拷贝)

```java
// ✅ 方法1: 最简单，但注意浅拷贝问题
public class User implements Cloneable {
    private int id;
    private String name;
    private Address address;  // 复杂对象
    
    @Override
    public User clone() {
        try {
            return (User) super.clone();  // 浅拷贝！
        } catch (CloneNotSupportedException e) {
            throw new RuntimeException(e);
        }
    }
}

// 问题：address只复制引用
User original = new User(1, "Alice", new Address("Shanghai"));
User copy = original.clone();
copy.getAddress().setCity("Beijing");  // 原对象也变了！
```

**优缺点**:
- ✅ 简单，使用内置接口
- ❌ 浅拷贝，容易出错
- ❌ 需要处理CloneNotSupportedException

### 方法2: Copy Constructor (深拷贝推荐)

```java
public class User {
    private int id;
    private String name;
    private Address address;
    
    // 拷贝构造函数 - 推荐用于深拷贝
    public User(User original) {
        this.id = original.id;
        this.name = original.name;
        // ✅ 深拷贝Address
        this.address = new Address(original.address);
    }
}

public class Address {
    private String city;
    private String street;
    
    public Address(Address original) {
        this.city = original.city;
        this.street = original.street;
    }
}

// 使用
User original = new User(1, "Alice", new Address("Shanghai", "Nanjing Rd"));
User copy = new User(original);  // 深拷贝
copy.getAddress().setCity("Beijing");  // 安全！不影响原对象

assert original.getAddress().getCity().equals("Shanghai");  // ✅
```

**优缺点**:
- ✅ 明确控制哪些字段拷贝
- ✅ 天然支持深拷贝
- ✅ 类型安全
- ❌ 需要为每个类写构造函数

### 方法3: Builder Pattern Clone (创建过程中克隆)

```java
public class User {
    private int id;
    private String name;
    private Address address;
    private List<Role> roles;
    
    // 私有构造，通过Builder创建
    private User(UserBuilder builder) {
        this.id = builder.id;
        this.name = builder.name;
        this.address = builder.address;
        this.roles = builder.roles;
    }
    
    // Clone通过Builder
    public User clone() {
        return new UserBuilder(this).build();
    }
    
    // Builder支持部分修改
    public static class UserBuilder {
        private int id;
        private String name;
        private Address address;
        private List<Role> roles;
        
        public UserBuilder(User original) {
            this(original.id);
            this.name = original.name;
            this.address = original.address.clone();  // 深拷贝
            this.roles = new ArrayList<>(original.roles);  // 深拷贝列表
        }
        
        public UserBuilder(int id) {
            this.id = id;
            this.roles = new ArrayList<>();
        }
        
        public UserBuilder name(String name) {
            this.name = name;
            return this;
        }
        
        public UserBuilder addRole(Role role) {
            this.roles.add(role);
            return this;
        }
        
        public User build() {
            return new User(this);
        }
    }
}

// 使用：克隆并修改
User original = buildUser();
User modified = new UserBuilder(original)
    .name("Bob")                          // 修改name
    .addRole(Role.ADMIN)                  // 增加role
    .build();

assert original.getName().equals("Alice");  // 原对象不变
assert modified.getName().equals("Bob");    // 新对象修改了
```

**优缺点**:
- ✅ 灵活，可部分修改
- ✅ 类型安全
- ✅ 深拷贝
- ❌ 代码较多

### 方法4: 深拷贝注册表 (动态克隆 + 缓存)

```java
public class PrototypeRegistry {
    private Map<String, Object> prototypes = new HashMap<>();
    
    public void register(String key, Object prototype) {
        prototypes.put(key, prototype);
    }
    
    // ✅ 深拷贝工厂方法
    public <T> T clone(String key) {
        Object prototype = prototypes.get(key);
        if (prototype == null) {
            throw new IllegalArgumentException("未知的原型: " + key);
        }
        return deepClone(prototype);
    }
    
    // 通用深拷贝 - 通过序列化
    @SuppressWarnings("unchecked")
    private <T> T deepClone(Object obj) {
        try {
            // 序列化 + 反序列化 = 完整深拷贝
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(baos);
            oos.writeObject(obj);
            oos.close();
            
            ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bais);
            T cloned = (T) ois.readObject();
            ois.close();
            
            return cloned;
        } catch (Exception e) {
            throw new RuntimeException("深拷贝失败", e);
        }
    }
}

// 使用
PrototypeRegistry registry = new PrototypeRegistry();
registry.register("admin-user", new User(999, "Admin", roleList));

User cloned = registry.clone("admin-user");  // 深拷贝
cloned.setName("Modified Admin");
assert registry.clone("admin-user").getName().equals("Admin");  // ✅ 独立
```

**优缺点**:
- ✅ 通用的深拷贝
- ✅ 无需为每个类定制
- ❌ 序列化开销
- ❌ 类必须Serializable

---

## Prototype的5种变体

### 变体1: 对象池 + Prototype

```java
// 场景：频繁创建临时对象
public class ObjectPool<T> {
    private Queue<T> available = new LinkedList<>();
    private List<T> inUse = new ArrayList<>();
    private T prototype;
    
    public ObjectPool(T prototype, int poolSize) {
        this.prototype = prototype;
        for (int i = 0; i < poolSize; i++) {
            available.offer(deepClone(prototype));
        }
    }
    
    public T borrow() {
        T obj = available.isEmpty() ? 
            deepClone(prototype) : 
            available.poll();
        inUse.add(obj);
        return obj;
    }
    
    public void release(T obj) {
        inUse.remove(obj);
        reset(obj);  // 重置状态
        available.offer(obj);
    }
}

// 使用：数据库连接池
User templateUser = new User();
ObjectPool<User> pool = new ObjectPool<>(templateUser, 10);

User user = pool.borrow();
// 使用user
pool.release(user);
```

### 变体2: 撤销/重做系统

```java
public class CommandWithPrototype {
    private Stack<GameState> undoStack = new Stack<>();
    private Stack<GameState> redoStack = new Stack<>();
    
    public void executeCommand(GameCommand cmd) {
        // 在执行前保存状态
        GameState snapshot = gameState.deepClone();
        undoStack.push(snapshot);
        redoStack.clear();
        
        // 执行命令
        cmd.execute();
    }
    
    public void undo() {
        if (undoStack.isEmpty()) return;
        
        // 保存当前状态用于重做
        redoStack.push(gameState.deepClone());
        
        // 恢复之前状态
        gameState = undoStack.pop();
    }
    
    public void redo() {
        if (redoStack.isEmpty()) return;
        
        undoStack.push(gameState.deepClone());
        gameState = redoStack.pop();
    }
}
```

### 变体3: 动态对象工厂

```java
public class DynamicObjectFactory {
    private Map<Class<?>, Object> templates = new HashMap<>();
    
    public <T> void registerTemplate(Class<T> type, T template) {
        templates.put(type, template);
    }
    
    public <T> T create(Class<T> type) {
        Object template = templates.get(type);
        if (template == null) {
            throw new IllegalArgumentException("未注册: " + type);
        }
        return type.cast(deepClone(template));
    }
}

// 使用
DynamicObjectFactory factory = new DynamicObjectFactory();
factory.registerTemplate(User.class, defaultUser);
factory.registerTemplate(Product.class, defaultProduct);

User user = factory.create(User.class);
Product product = factory.create(Product.class);
```

### 变体4: 缓存快照

```java
public class CachedPrototype<T> {
    private T current;
    private T cached;
    private long cacheTime;
    private static final long TTL = 60000;  // 1分钟
    
    public CachedPrototype(T initial) {
        this.current = initial;
        this.cached = deepClone(initial);
    }
    
    public T getCurrent() {
        return current;
    }
    
    public T getSnapshot() {
        // 快速返回缓存
        if (isCacheValid()) {
            return deepClone(cached);
        }
        
        // 更新缓存
        this.cached = deepClone(current);
        this.cacheTime = System.currentTimeMillis();
        return deepClone(cached);
    }
    
    private boolean isCacheValid() {
        return System.currentTimeMillis() - cacheTime < TTL;
    }
}
```

### 变体5: 原型链(Prototype Chain)

```java
// JavaScript原型链的Java实现
public class PrototypeChain {
    private Map<String, Object> own = new HashMap<>();
    private PrototypeChain parent;
    
    public PrototypeChain(PrototypeChain parentPrototype) {
        this.parent = parentPrototype;
    }
    
    public Object get(String key) {
        // 先查找自己的属性
        if (own.containsKey(key)) {
            return own.get(key);
        }
        
        // 再查找父原型
        if (parent != null) {
            return parent.get(key);
        }
        
        return null;
    }
    
    public void set(String key, Object value) {
        own.put(key, value);
    }
}

// 使用：模拟JavaScript对象
PrototypeChain objectProto = new PrototypeChain(null);
objectProto.set("toString", "Object.prototype.toString");

PrototypeChain arrayProto = new PrototypeChain(objectProto);
arrayProto.set("push", "Array.prototype.push");

assert arrayProto.get("toString") != null;  // 继承
```

---

## 4个常见问题的深度解决

### 问题1: 浅拷贝陷阱

**症状**: 拷贝后修改嵌套对象，原对象也变了

**反面示例(❌)**:
```java
public class ShallowCloneBad {
    private Address address;
    
    public ShallowCloneBad clone() {
        ShallowCloneBad copy = new ShallowCloneBad();
        copy.address = this.address;  // ❌ 浅拷贝
        return copy;
    }
}

// 灾难
ShallowCloneBad original = new ShallowCloneBad(new Address("Shanghai"));
ShallowCloneBad copy = original.clone();
copy.getAddress().setCity("Beijing");

assert original.getAddress().getCity().equals("Beijing");  // 原对象变了！
```

**解决方案(✅)**:
```java
public class DeepCloneGood {
    private Address address;
    
    public DeepCloneGood deepClone() {
        DeepCloneGood copy = new DeepCloneGood();
        copy.address = this.address.deepClone();  // ✅ 深拷贝
        return copy;
    }
}

// 安全
DeepCloneGood original = new DeepCloneGood(new Address("Shanghai"));
DeepCloneGood copy = original.deepClone();
copy.getAddress().setCity("Beijing");

assert original.getAddress().getCity().equals("Shanghai");  // ✅ 原对象不变
```

### 问题2: 序列化的复杂对象

**症状**: 包含非Serializable字段的对象无法克隆

**反面示例(❌)**:
```java
public class UnserializableObject implements Serializable {
    private DatabaseConnection conn;  // ❌ 不能序列化！
    
    // 序列化会失败
}
```

**解决方案(✅)**:
```java
public class SerializableWorkaround {
    private DatabaseConnection conn;
    
    // 自定义序列化逻辑
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.defaultWriteObject();
        oos.writeObject(conn.getURL());  // 只序列化URL
    }
    
    private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        String url = (String) ois.readObject();
        this.conn = new DatabaseConnection(url);  // 重建连接
    }
}

// 或者用Copy Constructor
public class CopyConstructorApproach {
    private DatabaseConnection conn;
    
    public CopyConstructorApproach(CopyConstructorApproach original) {
        this.conn = new DatabaseConnection(original.conn.getURL());
    }
}
```

### 问题3: 深拷贝的性能成本

**症状**: 对象很大，深拷贝很慢

**分析**:
```
对象大小          深拷贝成本        何时使用
─────────────────────────────────
< 1MB            微不足道(<1ms)    总是用深拷贝
1-10MB           10-100ms          权衡，通常值得
10-100MB         100ms-1s          考虑浅拷贝 + COW
> 100MB          > 1s              用COW或共享存储
```

**优化方案**:
```java
// 方案1：Copy-On-Write (COW)
public class COWList<T> implements Iterable<T> {
    private List<T> data;
    private boolean isClone = false;
    
    public void add(T item) {
        if (isClone) {
            // 已经复制，直接修改
            data.add(item);
        } else {
            // 第一次修改时才复制
            data = new ArrayList<>(data);
            data.add(item);
            isClone = true;
        }
    }
    
    public COWList<T> clone() {
        // 不复制数据，只是标记
        COWList<T> copy = new COWList<>();
        copy.data = this.data;
        copy.isClone = false;
        return copy;
    }
}

// 方案2：指数退避(Exponential Backoff)
byte[] buffer = new byte[10_000_000];  // 10MB对象
byte[] copy = buffer.clone();  // 自动优化，很快

// 方案3：选择性深拷贝
public class SelectiveDeepClone {
    private List<Item> items;           // 通常不变，浅拷贝
    private Map<String, Config> configs; // 经常变化，深拷贝
    
    public SelectiveDeepClone clone() {
        SelectiveDeepClone copy = new SelectiveDeepClone();
        copy.items = this.items;         // ⚠️ 浅拷贝
        copy.configs = deepCopy(this.configs);  // ✅ 深拷贝
        return copy;
    }
}
```

### 问题4: 循环引用处理

**症状**: 对象A包含B，B包含A，导致深拷贝死循环

**反面示例(❌)**:
```java
public class Node {
    public Node next;
    
    public Node deepClone() {
        Node copy = new Node();
        copy.next = this.next.deepClone();  // ❌ 死循环！
        return copy;
    }
}

// 甚至可能是间接的：A→B→C→A
```

**解决方案(✅)**:
```java
public class NodeWithCycleHandling {
    public Node next;
    
    public Node deepClone() {
        return deepClone(new IdentityHashMap<>());
    }
    
    private Node deepClone(Map<Node, Node> visited) {
        // 如果已访问，返回已克隆的副本
        if (visited.containsKey(this)) {
            return visited.get(this);
        }
        
        Node copy = new Node();
        visited.put(this, copy);  // 记录，防止重复
        
        if (this.next != null) {
            copy.next = this.next.deepClone(visited);
        }
        
        return copy;
    }
}

// 序列化方式自动处理
class SerializableNode implements Serializable {
    public SerializableNode next;
    
    public SerializableNode deepClone() {
        try {
            // Java序列化自动处理循环引用
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(baos);
            oos.writeObject(this);
            oos.close();
            
            ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
            ObjectInputStream ois = new ObjectInputStream(bais);
            return (SerializableNode) ois.readObject();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
```

---

## 最佳实践

1. ✅ **默认使用深拷贝** - 除非确定浅拷贝足够
2. ✅ **使用Copy Constructor** - 比Cloneable更清晰
3. ✅ **文档化克隆深度** - 说明复制了什么
4. ✅ **性能测试** - 大对象要测试克隆成本
5. ✅ **使用不可变对象** - 减少克隆需求

## 何时避免使用

- ❌ 创建成本很低 - 直接new比克隆快
- ❌ 对象是无状态的 - 无需克隆
- ❌ 改用工厂模式更清晰 - 有复杂选择逻辑时
- ❌ 改用Builder模式更好 - 需要部分定制时
