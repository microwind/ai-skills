---
name: 组合优于继承
description: "优先使用对象组合而非类继承来实现代码复用，获得更灵活的设计。"
license: MIT
---

# 组合优于继承 (Composition over Inheritance)

## 概述

Gang of Four 在《设计模式》中提出：**优先使用对象组合而非类继承**。继承是"is-a"关系，组合是"has-a"关系。

**核心思想**：
- 继承创建紧耦合，组合创建松耦合
- 继承在编译时确定，组合在运行时可变
- 继承暴露父类实现细节，组合隐藏内部实现

## 继承的问题

```java
// ❌ 继承导致的问题：脆弱基类
public class ArrayList<E> {
    public void add(E element) { /* ... */ }
    public void addAll(Collection<E> c) {
        for (E e : c) add(e);  // 内部调用 add
    }
}

public class CountingList<E> extends ArrayList<E> {
    private int addCount = 0;

    @Override
    public void add(E element) {
        addCount++;
        super.add(element);
    }

    @Override
    public void addAll(Collection<E> c) {
        addCount += c.size();
        super.addAll(c);  // 父类 addAll 又调用了 add，计数翻倍！
    }
}
```

```java
// ✅ 组合：不依赖父类实现细节
public class CountingList<E> {
    private final List<E> list = new ArrayList<>();
    private int addCount = 0;

    public void add(E element) {
        addCount++;
        list.add(element);
    }

    public void addAll(Collection<E> c) {
        addCount += c.size();
        list.addAll(c);  // 不关心 ArrayList 内部如何实现
    }

    public int getAddCount() { return addCount; }
}
```

## 组合实现多态

```python
# ❌ 多重继承导致菱形问题
class Flyer:
    def move(self):
        return "飞行"

class Swimmer:
    def move(self):
        return "游泳"

class Duck(Flyer, Swimmer):  # 菱形继承，move() 是哪个？
    pass

# ✅ 组合：行为可插拔
class FlyBehavior:
    def move(self) -> str:
        return "飞行"

class SwimBehavior:
    def move(self) -> str:
        return "游泳"

class Duck:
    def __init__(self):
        self.fly_behavior = FlyBehavior()
        self.swim_behavior = SwimBehavior()

    def fly(self) -> str:
        return self.fly_behavior.move()

    def swim(self) -> str:
        return self.swim_behavior.move()
```

## TypeScript 中的组合

```typescript
// ❌ 继承层次过深
class Animal { move() {} }
class Bird extends Animal { fly() {} }
class Parrot extends Bird { talk() {} }
class PetParrot extends Parrot { tricks() {} }
// 4 层继承，耦合严重

// ✅ 组合 + 接口
interface Movable { move(): void; }
interface Flyable { fly(): void; }
interface Talkable { talk(): void; }

class Parrot implements Movable, Flyable, Talkable {
    constructor(
        private mover: Movable,
        private flyer: Flyable,
        private talker: Talkable
    ) {}

    move() { this.mover.move(); }
    fly() { this.flyer.fly(); }
    talk() { this.talker.talk(); }
}
```

## 何时使用继承

```
继承仍然适用的场景：
✅ 真正的 "is-a" 关系（Cat is an Animal）
✅ 框架要求（Android Activity、JUnit TestCase）
✅ 模板方法模式（固定算法骨架，子类实现步骤）
✅ 类层次稳定且不深（≤ 2 层）

应该用组合的场景：
✅ "has-a" 或 "uses-a" 关系
✅ 需要运行时切换行为
✅ 需要复用多个不相关类的功能
✅ 继承层次超过 2 层
```

## 最佳实践

| 场景 | 继承 | 组合 |
|------|------|------|
| 代码复用 | ❌ | ✅ |
| 多态 | ✅ 接口继承 | ✅ 策略模式 |
| 行为扩展 | ❌ 脆弱基类 | ✅ 装饰器模式 |
| 运行时变化 | ❌ 编译时固定 | ✅ 可插拔 |

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [LSP](../liskov-substitution-principle/) | 违反 LSP 时通常应改用组合 |
| [OCP](../open-closed-principle/) | 组合通过注入新行为实现 OCP |
| [DIP](../dependency-inversion-principle/) | 组合 + 接口 = DIP 的典型实现 |
| [ISP](../interface-segregation-principle/) | 小接口 + 组合 = 灵活的设计 |

## 总结

**核心原则**：优先使用组合，仅在真正的 "is-a" 关系时使用继承。

**实践要点**：
- 继承用于"是什么"，组合用于"有什么"和"能做什么"
- 继承层次不超过 2 层
- 用接口定义行为，用组合注入实现
- 当你犹豫时，选组合
