# Prototype Pattern - 诊断与规划表

## 第1步: 需求诊断 - 你真的需要Prototype吗？

### 🔍 快速检查清单

```
□ 对象创建过程复杂，包含多步骤初始化
□ 创建对象的成本很高（时间或资源）
□ 需要创建与现有对象状态完全相同的副本
□ 对象的具体类型应该在运行时决定
□ 避免子类爆炸（各种参数组合的类）
□ 需要快速复制现有状态而不是从零开始
```

**诊断标准**:
- ✅ 勾选 4 项以上 → **强烈推荐使用Prototype**
- ⚠️ 勾选 2-3 项 → **可以使用Prototype**
- ❌ 勾选 1 项以下 → **简单的构造函数足够**

### 对标场景检验

```
□ 数据库记录对象复制？
□ 配置对象克隆？（配置复杂，字段多）
□ 缓存快照备份？
□ 撤销/重做功能？
□ 游戏保存系统？
□ UI组件模板复制？
□ 对象池管理？
```

**结果**: [数据库相关、缓存、撤销等 → 使用Prototype]

---

## 第2步: 克隆深度选择矩阵

### 浅拷贝 vs 深拷贝

| 特性 | 浅拷贝 | 深拷贝 |
|------|--------|--------|
| **复制基本字段** | ✅ | ✅ |
| **复制对象引用** | ❌ 共享 | ✅ 递归复制 |
| **性能** | ⚡⚡⚡ | ⚡ |
| **安全性** | ⚠️ 容易污染 | ✅ 完全独立 |
| **应用场景** | 只读对象 | 可变对象 |

### 选择流程图

```
对象中有嵌套的复杂对象吗?
├─ 否 → 浅拷贝足够
├─ 是 → 需要修改嵌套对象吗?
│      ├─ 是 → 必须深拷贝❌
│      └─ 否 → 可以浅拷贝✅
└─ 不确定 → 默认使用深拷贝✅
```

### 对象结构分析表

```
对象类型            嵌套复杂度  推荐策略        原因
────────────────────────────────────────────────────
基础值对象          简单       浅拷贝优化   String/Integer不变
配置对象            中等       深拷贝       内包含子配置对象
数据库记录          复杂       深拷贝       含多个关系对象
UI组件              很复杂     深拷贝       包含事件处理器等
图形对象            简单       浅拷贝       通常只读
游戏角色数据        很复杂     深拷贝       包含装备、技能等
```

---

## 第3步: 实现方法选择

### 4种实现方法对比

| 方法 | 代码复杂度 | 性能 | 深拷贝支持 | 推荐场景 |
|------|-----------|------|-----------|---------|
| **Cloneable** | ⭐ | ⭐⭐⭐ | ❌ 浅 | 简单对象 |
| **Copy Constructor** | ⭐⭐ | ⭐⭐⭐ | ✅ | 【推荐】深拷贝 |
| **Builder Clone** | ⭐⭐⭐ | ⭐⭐ | ✅ | 复杂对象+修改 |
| **序列化克隆** | ⭐ | ⭐ | ✅ | 通用方案 |

### 快速决策

```
需要深拷贝?
├─ 是 → 对象复杂吗?
│      ├─ 简单(< 5个字段) → Copy Constructor
│      └─ 复杂(> 5个字段) → Builder Clone或序列化
└─ 否 → Cloneable接口足够
```

---

## 第4步: 克隆策略规划

### 步骤1: 辨识克隆类型

```
对象分类:
- 不可变对象 (String, Date) → 浅拷贝即可
- 可变值对象 (Address, Config) → 需要递归克隆
- 容器对象 (List, Map) → 深拷贝内容
- 引用对象 (数据库连接) → 特殊处理
```

### 步骤2: 设计克隆接口

```
方案1: Cloneable接口
    接口: Cloneable
    实现: clone()
    问题: 浅拷贝

方案2: 自定义接口
    接口: Prototype<T> { T deepClone(); }
    实现: 明确约定深拷贝
    优势: 类型安全

方案3: Copy Constructor
    签名: MyClass(MyClass original) { }
    实现: 在构造中控制复制
    优势: 灵活清晰
```

### 步骤3: 处理特殊情况

```
- 不可序列化字段? → 自定义getter/setter
- 循环引用? → 使用visited Map追踪
- 性能关键? → 使用COW(Copy-On-Write)
- 大对象? → 使用对象池+克隆共享
- 线程安全? → 使用ThreadLocal或同步
```

---

## 第5步: 测试计划

### 单元测试清单

```
基础克隆:
□ 验证克隆对象与原对象字段相同
□ 验证克隆与原是不同的引用
□ 验证克隆包含原对象所有状态

深拷贝验证:
□ 修改克隆的嵌套对象，原对象不变
□ 修改克隆的集合，原对象不变
□ null字段正确处理

特殊情况:
□ 空对象克隆
□ 包含null字段的对象
□ 循环引用对象
□ 大对象克隆性能
□ 线程并发克隆
```

### 性能测试

```java
@Test
public void benchmark() {
    User original = createLargeUser();  // 复杂对象
    
    // 测试1: Copy Constructor
    long start = System.nanoTime();
    for (int i = 0; i < 100000; i++) {
        User copy = new User(original);
    }
    long ccTime = System.nanoTime() - start;
    
    // 测试2: 序列化克隆
    start = System.nanoTime();
    for (int i = 0; i < 100000; i++) {
        User copy = original.serializationClone();
    }
    long serTime = System.nanoTime() - start;
    
    // 比较
    System.out.println("Copy Constructor: " + ccTime/1000 + "μs");
    System.out.println("Serialization: " + serTime/1000 + "μs");
}
```

---

## 第6步: 代码审查清单

### 设计审查

- [ ] **克隆深度明确** - 文档说明是浅还是深
- [ ] **循环引用处理** - 对象图中有无循环
- [ ] **不可变性保证** - 克隆后不应该被修改
- [ ] **性能可接受** - 测试过大对象克隆
- [ ] **异常处理完整** - 克隆失败如何处理

### 实现审查

- [ ] **所有字段都克隆了** - 没有遗漏字段
- [ ] **嵌套对象深拷贝** - 不是浅拷贝引用
- [ ] **集合/数组复制** - 深拷贝内容
- [ ] **Null检查** - 避免NPE
- [ ] **资源清理** - 临时对象及时释放

```java
// ✅ 完整的深拷贝修检
public User deepClone() {
    User copy = new User();
    
    // ✓ 基本类型
    copy.id = this.id;
    copy.name = this.name;  // String特殊，可浅拷贝
    
    // ✓ 复杂对象
    copy.address = this.address == null ? 
        null : 
        new Address(this.address);
    
    // ✓ 集合
    copy.roles = this.roles == null ?
        null :
        this.roles.stream()
            .map(Role::new)  // Copy Constructor
            .collect(Collectors.toList());
    
    // ✓ 特殊处理
    copy.createdAt = new Date(this.createdAt.getTime());  // Date特殊
    
    return copy;
}
```

---

## 常见陷阱预防

### ⚠️ 陷阱1: 浅拷贝导致状态污染

❌ **反面做法**:
```java
public User clone() {
    User copy = new User();
    copy.address = this.address;  // ❌ 浅拷贝！
    return copy;
}

// 灾难
User original = new User(new Address("Shanghai"));
User copy = original.clone();
copy.getAddress().setCity("Beijing");
// 原对象也变了！
```

✅ **正确做法**:
```java
public User deepClone() {
    User copy = new User();
    copy.address = this.address == null ? 
        null : 
        new Address(this.address);  // ✅ 深拷贝
    return copy;
}
```

### ⚠️ 陷阱2: 忘记克隆集合

❌ **反面做法**:
```java
public User clone() {
    User copy = new User();
    copy.roles = this.roles;  // ❌ 共享List！
    return copy;
}

// 灾难
User original = new User(roles);
User copy = original.clone();
copy.getRoles().add(Role.ADMIN);
// 原对象的roles也变了！
```

✅ **正确做法**:
```java
public User deepClone() {
    User copy = new User();
    copy.roles = this.roles == null ?
        null :
        new ArrayList<>(this.roles);  // ✅ 复制列表
        // 或者深拷贝元素：
        // new ArrayList<>(
        //   this.roles.stream()
        //     .map(Role::new)
        //     .collect(toList())
        // )
    return copy;
}
```

### ⚠️ 陷阱3: 循环引用导致死循环

❌ **反面做法**:
```java
public Node clone() {
    Node copy = new Node();
    copy.next = this.next.clone();  // ❌ 如果有循环引用会死循环！
    return copy;
}
```

✅ **正确做法**:
```java
public Node deepClone() {
    return deepClone(new IdentityHashMap<>());
}

private Node deepClone(Map<Node, Node> visited) {
    if (visited.containsKey(this)) {  // ✅ 检测已访问
        return visited.get(this);
    }
    
    Node copy = new Node();
    visited.put(this, copy);  // 记录已访问
    
    if (this.next != null) {
        copy.next = this.next.deepClone(visited);
    }
    
    return copy;
}
```

### ⚠️ 陷阱4: 特殊对象处理不当

❌ **反面做法**:
```java
public Data clone() {
    Data copy = new Data();
    copy.date = this.date;  // ❌ Date可变，应该复制
    copy.connection = this.connection;  // ❌ 不能克隆连接
    copy.thread = this.thread;  // ❌ 不能克隆线程
    return copy;
}
```

✅ **正确做法**:
```java
public Data deepClone() {
    Data copy = new Data();
    copy.date = new Date(this.date.getTime());  // ✅ 复制Date
    // connection和thread不克隆，需要时重建
    copy.connection = null;  // 克隆后需要重建连接
    copy.thread = null;
    return copy;
}
```

---

## 快速参考

### 最小实现模板

```java
// Copy Constructor方式（推荐）
public class User {
    private int id;
    private String name;
    private Address address;
    private List<Role> roles;
    
    // Copy Constructor
    public User(User original) {
        this.id = original.id;
        this.name = original.name;
        this.address = new Address(original.address);
        this.roles = new ArrayList<>(original.roles);
    }
}
```

### 决策树

```
需要克隆对象?
├─ 创建成本低? → 简单直接new
├─ 对象简单(< 3个字段)? → Cloneable
├─ 对象复杂但只读? → 浅拷贝
├─ 对象复杂且可变? → 深拷贝
│  ├─ 需要修改克隆? → Builder Clone
│  └─ 只是复制状态? → Copy Constructor
└─ 不确定? → 默认Copy Constructor
```

### 克隆方法速查表

| 场景 | 推荐方法 | 代码示例 |
|------|---------|---------|
| 简单值对象 | Cloneable | `(User) super.clone()` |
| 复杂对象 | Copy Constructor | `new User(original)` |
| 需要修改 | Builder | `new UserBuilder(original).name("new").build()` |
| 序列化对象 | ObjectSerialization | `serialize+deserialize` |

---

## 相关资源

- **SKILL.md** - Prototype完整详解
- **reference.md** - 多语言实现
- **design-patterns/** - 相关模式
