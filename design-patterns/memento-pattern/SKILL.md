# Memento Pattern - 完整技能指南

## 核心概念

**Memento**（备忘录）是一种Behavioral（行为型）设计模式。

**定义**：不违反对象的封装性,捕获了存储一个对象在某个时刻的状态,使得后续可以恢复到这个状态。

**核心意图**：
- 保存对象的历史状态，便于后续恢复
- 避免污染对象内部，封装性不被破坏
- 支持撤销/重做（Undo/Redo）
- 支持状态的自由切换和比较

---

## 4种实现方法

### 方法1: 字段快照方式（Field Snapshot）
**核心思想**：捕获对象所有字段的当前值

```java
public class Memento {
    private String state1;
    private String state2;
    private int state3;
    
    public Memento(String s1, String s2, int s3) {
        this.state1 = s1;
        this.state2 = s2;
        this.state3 = s3;
    }
}
```

**优点**：简单，效率高
**缺点**：每改变字段就需要修改Memento类
**用途**：文档编辑器、画图应用

### 方法2: 事件溯源方式（Event Sourcing）
**核心思想**：记录一系列对象的事件，然后重演事件以恢复状态

```java
public class EventLog {
    private List<Event> events = new ArrayList<>();
    
    public void record(Event event) {
        events.add(event);
    }
    
    public void replay() {
        for (Event event : events) {
            event.execute();
        }
    }
}
```

**优点**：任意时刻恢复、可审计历程
**缺点**：事件堆积多、需要定期整理
**用途**：数据库事务、分布式系统

### 方法3: 序列化方案（Serialization）
**核心思想**：序列化整个对象状态

```java
public class Memento {
    private byte[] serialized;
    
    public Memento(Object obj) throws IOException {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(obj);
        this.serialized = bos.toByteArray();
    }
}
```

**优点**：通用,便于持久化
**缺点**：序列化开销大,可能不安全
**用途**：对象存储、RPC传输

### 方法4: 版本管理方案（Version Management）
**核心思想**：为整个对象状态打包为不同的版本

```java
public class VersionedMemento {
    private Map<LocalDateTime, Object> versions = new TreeMap<>();
    
    public void saveVersion(Object state) {
        versions.put(LocalDateTime.now(), deepCopy(state));
    }
    
    public Object restore(LocalDateTime timestamp) {
        return versions.get(timestamp);
    }
}
```

**优点**：支持长期版本管理，比较清晰
**缺点**：内存膨胀（memory bloat）风险大
**用途**：git版本控制、文档版本管理

---

## 6个真实应用场景

### 场景1: 文本编辑器Undo/Redo
**问题**：用户需要撤销和重做上一步编辑
**解决**：使用字段快照Memento,维护两个Stack（撤销、重做）

### 场景2: 数据库事务回滚
**问题**：事务失败需要回滚到之前的状态
**解决**：事务开始前保存序列化Memento,失败时恢复

### 场景3: 版本控制系统（Git）
**问题**：代码增改需要追溯历史
**解决**：每个commit是一个Memento，记录代码库的一个快照

### 场景4: 游戏存档/检查点模式
**问题**：玩家需要恢复到之前的游戏状态
**解决**：在每个Checkpoint记录整个游戏世界的Memento

### 场景5: 数据库定时快照
**问题**：定时需要创建整个数据库的快照
**解决**：使用RDB、WAL等方法定时创建Memento

### 场景6: 前端分页状态（Pagination State）
**问题**：用户浏览多页后需要保存页面配置
**解决**：保存viewState时将整个布局状态存为Memento

---

## 4个常见问题与解决方案

### 问题1: Memento爆炸（Memento Explosion）
**原因**：对象状态变化频繁，需要频繁保存Memento
**症状**：Memento数量庞大，内存占用飙升
**解决方案**：
- 不是每次变更都保存Memento，而是在关键节点才保存
- 使用增量Memento（只记录差异部分）
- 清理旧的快照，例如5分钟前的

### 问题2: 深拷贝问题（Deep Copy）
**原因**：保存状态时使用了浅拷贝，导致Memento与原对象共享引用
**症状**：修改原对象后，Memento中的状态也随之改变
**解决方案**：
- 使用深拷贝（Deep Clone）而非浅拷贝
- 使用序列化实现完整拷贝
- CoW（Copy on Write）优化

### 问题3: 封装性被破坏
**原因**：Originator的字段改变时，Memento类也需要同步修改
**症状**：Memento类与Originator紧耦合，维护成本高
**解决方案**：
- 不要为每个字段单独建立存取方法，而是让Memento整体保存
- 使用Reflection自动发现字段并保存
- 版本化Memento（每个版本对应一个快照结构）

### 问题4: 不可修改的对象Restoration
**原因**：目标对象是不可变对象，没有提供修改状态的方法
**症状**：Restore失败，因为对象没有提供Setter方法
**解决方案**：
- 通过构造函数重新创建不可变对象，而非尝试修改
- 使用工厂方法重新创建实例
- 使用反射机制直接写入字段

---

## 与其他模式的关系矩阵

| 模式 | 关系 | 何时结合 | 示例 |
|--------|------|---------|------|
| **Command** | 中层 | Command执行动作,Memento保存状态 | 撤销系统 |
| **Iterator** | 互补 | Iterator遍历,Memento保存状态 | 文件迭代 |
| **Prototype** | 相似 | 两者都涉及克隆，Prototype更通用，Memento更专注 | 深拷贝 |
| **State** | 互补 | State管理状态转换，Memento保存状态快照 | 推荐结合使用，State更侧重行为 |

---

## 最佳实践

1. ✅ **不违反封装性** - Memento不应暴露内部细节，不暴露私有数据
2. ✅ **确保深拷贝** - 保存状态时必须使用深拷贝，避免引用共享
3. ✅ **清理历史快照，防止内存膨胀** - 需要维护FIFO队列，避免快照无限积累
4. ✅ **高效的对象拷贝** - 使用Flyweight减少重复数据，或使用COW（Copy on Write）优化
5. ✅ **确保Restore操作的完整性** - Restore需要保证恢复后状态的一致性和完整性
6. ✅ **为快照添加版本标识** - 记录版本ID，便于追溯和恢复到指定版本
7. ✅ **为Memento添加描述信息** - 记录每个Memento的创建时间、触发原因等元数据