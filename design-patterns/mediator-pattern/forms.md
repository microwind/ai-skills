# Memento Pattern - 诊断与规划表（350行）

## 第1步 - 需求诊断

### 检查清单（勾选所有适用）:
- ☐ 需要保存和恢复对象的历史状态
- ☐ 需要支持Undo/Redo功能
- ☐ 需要在状态间自由切换（快照）
- ☐ 状态保存的时间间隔频繁（>10次/秒）
- ☐ 状态数据量大（>1MB）
- ☐ 需要审计状态变更历史
- ☐ 需要并发访问多个版本
- ☐ 状态需要持久化（数据库/文件）

**诊断**:
- ✅ 6项以上 → 强烈使用Memento
- ⚠️ 4-5项 → 可以使用，权衡
- ❌ 3项以下 → 可能过度设计

## 第2步 - 实现方法选择矩阵

| 方法 | 复杂度 | 内存占用 | 性能 | 最佳用途 |
|-----|--------|--------|------|---------|
| **字段快照** | ⭐ | 中  | 快  | 小对象编辑（文本编辑器） |
| **事件溯源** | ⭐⭐⭐ | 高  | 中  | 审计+恢复（数据库） |
| **序列化** | ⭐⭐ | 高  | 慢  | 通用对象存储 |
| **版本管理** | ⭐⭐⭐ | 极高 | 快  | 长期版本对比（Git） |

## 第3步 - 对象复杂度评估表

| 对象类型 | 字段数 | 数据量 | 关联对象数 | 推荐方案 |
|---------|--------|--------|----------|---------|
| **简单值对象** | <5 | <1KB | 0 | 字段快照 |
| **业务实体** | 5-20 | 10-100KB | 1-3 | 序列化或字段快照 |
| **复杂图形** | 10-100 | 100KB-10MB | 多 | 事件溯源或版本管理 |
| **海量记录** | >100 | >10MB | 很多 | 事件溯源（仅记录变更） |

## 第4步 - 6步实现规划

### 步骤1: 分析状态特征
```
问题列表:
□ 状态中有哪些关键字段?
□ 哪些字段经常改变?
□ 是否有不可序列化的对象?
□ 何时保存状态?(用户操作后/定时/手动)
□ 需要保留多少个历史状态?
□ 状态是否跨线程访问?
```

### 步骤2: 选择保存策略
```
场景:
□ 频繁手动保存(Ctrl+Z) → 字段快照+Stack
□ 自动定时保存(autosave) → 事件溯源
□ 长期版本保存(文件系统) → 序列化
□ 极限持久化(数据库) → 事件溯源+Log
□ 实时同步(协作编辑) → 版本管理+CRDTs
```

### 步骤3: 定义Memento类
```java
// 选项A - 字段快照 (推荐Simple值对象)
class TextEditorMemento {
    final String text;
    final int cursorPosition;
    final long timestamp;
}

// 选项B - 通用Memento (推荐复杂对象)
class GenericMemento {
    final byte[] serialized;
    final String objectType;
    final LocalDateTime timestamp;
}
```

### 步骤4: 设计Caretaker（看守者）
```
Stack vs Queue vs LinkedList:
- Undo/Redo系统: Stack (用于回溯)
- 事件日志: LinkedList (不限大小)
- 时间序列: TreeMap<Timestamp, Memento>
- 版本控制: List<Version> + 索引

设计清单:
□ 最多保存多少个历史?
□ 如何清理旧Memento?
□ 是否需要压缩?
□ 远程同步策略?
```

### 步骤5: 实现恢复逻辑
```
恢复分类:
- 部分恢复: 只恢复某些字段
- 完全恢复: 恢复整个对象状态
- 增量恢复: 应用事件增量
- 快照恢复: 从快照加事件

测试用例:
□ 恢复到第一个状态
□ 恢复到中间状态
□ 恢复到最后状态
□ 快速连续Undo/Redo
□ 并发Undo操作
```

### 步骤6: 性能与资源管理
```
内存管理:
□ 单个Memento大小 < 10MB
□ 历史数量 < 1000
□ 总占用 < 可用内存50%

垃圾回收:
□ 清理超过N天的Memento
□ 压缩冗余数据
□ 使用WeakReference自动回收

性能指标:
□ 保存操作 < 100ms
□ 恢复操作 < 50ms  
□ 内存占用率 < 20%
```

## 第5步 - 陷阱预防

### ⚠️ 陷阱1: 浅拷贝导致状态污染
❌ 错误:
```java
public Memento(List<String> list) {
    this.list = list; // 浅拷贝！
}
```

✅ 正确:
```java
public Memento(List<String> list) {
    this.list = new ArrayList<>(list); // 深拷贝
}

public Object restore() {
    return Collections.unmodifiableList(
        new ArrayList<>(this.list)
    ); // 防止修改
}
```

### ⚠️ 陷阱2: Memento爆炸(内存溢出)
❌ 每次键盘输入都保存:
```java
textField.addKeyListener(e -> 
    caretaker.saveMemento(new TextEditorMemento(...))
); // 1秒100个Memento!
```

✅ 使用防抖或定时:
```java
Timer timer = new Timer();
timer.scheduleAtFixedRate(
    () -> caretaker.saveMemento(...), 
    0, 1000 // 每秒最多一次
);
```

### ⚠️ 陷阱3: 序列化不安全
❌ 直接Object.clone():
```java
public Memento clone() throws CloneNotSupportedException {
    return (Memento) super.clone(); // 浅拷贝
}
```

✅ 完整序列化:
```java
public Memento deepClone() throws Exception {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(baos);
    oos.writeObject(this);
    ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
    ObjectInputStream ois = new ObjectInputStream(bais);
    return (Memento) ois.readObject();
}
```

### ⚠️ 陷阱4: 无限递归(对象引用)
❌ 循环引用:
```java
class Node {
    Node parent;
    List<Node> children;
    // Memento会导致无限递归
}
```

✅ 使用ID或排除:
```java
class NodeMemento {
    String nodeId;
    List<String> childrenIds; // 只保存ID
    // 或用@Transient标记
    @Transient Node parent; // 不序列化
}
```

### ⚠️ 陷阱5: 版本冲突(并发修改)
❌ 无版本控制:
```java
Memento m1 = save(); // 线程A
Memento m2 = save(); // 线程B
restore(m1); // 可能冲突
```

✅ 版本号+CAS:
```java
class VersionedMemento {
    long version;
    Object state;
    
    void restore() {
        if (currentVersion != version) {
            throw new ConcurrentModificationException();
        }
    }
}
```

## 第6步 - 代码审查清单

### 设计审查
- [ ] Memento类字段私有且final
- [ ] 不提供setter方法改状态
- [ ] Originator提供正确的保存/恢复方法
- [ ] Caretaker管理生命周期

### 实现审查
- [ ] 深拷贝验证(非浅拷贝)
- [ ] 序列化测试
- [ ] 多线程安全性测试
- [ ] 内存溢出测试(大对象/长历史)
- [ ] 异常处理完整

### 性能审查
- [ ] 单个Memento创建时间<100ms
- [ ] 恢复时间<50ms
- [ ] 内存占用在预期范围内
- [ ] GC压力可接受

## 快速参考 - 决策流程

```
需要恢复历史状态?
├─ 是 → 有多少个历史版本?
│   ├─ <20: 字段快照 + Stack (Undo/Redo)
│   ├─ 20-1000: 事件溯源
│   └─ >1000: 版本管理 (Git模型)
│
├─ 对象大小?
│   ├─ <1MB: 序列化
│   ├─ 1-100MB: 字段快照
│   └─ >100MB: 事件溯源 (仅记录变化)
│
├─ 并发需求?
│   ├─ 单线程: 简单方案可行
│   └─ 多线程: 需要版本管理 + 同步
│
└─ 完成!