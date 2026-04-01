---
name: 面向对象编程
description: "通过封装、继承、多态三大特性组织代码，将复杂问题分解为相互协作的对象。"
license: MIT
---

# 面向对象编程 (Object-Oriented Programming, OOP)

## 概述

OOP 是一种编程范式，通过将数据和行为组织成**对象**来解决问题。核心概念：万物皆对象。

**三大特性**：
- **封装**：数据隐藏，提供接口访问
- **继承**：代码复用，建立分类体系
- **多态**：同一接口，多种实现

**关键优势**：
- 代码复用性高
- 问题分解更直观
- 维护扩展更容易
- 更接近现实世界建模

## 核心概念

### 1. 封装 (Encapsulation)

```java
// ❌ 无封装：公开所有字段
public class BankAccount {
    public double balance;  // 任意修改！

    public void withdraw(double amount) {
        balance -= amount;  // 无验证
    }
}

// ✅ 有封装：隐藏内部，提供受控接口
public class BankAccount {
    private double balance;  // 隐藏

    public void withdraw(double amount) throws Exception {
        if (amount > balance) {
            throw new Exception("Insufficient balance");
        }
        balance -= amount;  // 有验证
    }

    public double getBalance() {
        return balance;  // 只读访问
    }
}
```

### 2. 继承 (Inheritance)

```java
// 基类定义通用特性
public abstract class Shape {
    protected String color;

    public abstract double getArea();
    public abstract void draw();
}

// 子类继承并特化
public class Circle extends Shape {
    private double radius;

    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }

    @Override
    public void draw() {
        System.out.println("Drawing circle with color " + color);
    }
}

public class Rectangle extends Shape {
    private double width, height;

    @Override
    public double getArea() {
        return width * height;
    }

    @Override
    public void draw() {
        System.out.println("Drawing rectangle with color " + color);
    }
}
```

### 3. 多态 (Polymorphism)

```java
List<Shape> shapes = new ArrayList<>();
shapes.add(new Circle());
shapes.add(new Rectangle());

// 同一接口，不同行为
for (Shape shape : shapes) {
    System.out.println("Area: " + shape.getArea());
    shape.draw();  // 每个形状各自的draw实现
}

// 输出：
// Area: 78.54...
// Drawing circle with color RED
// Area: 100.0
// Drawing rectangle with color BLUE
```

## 何时使用OOP

**非常适合**：
- 系统有多个相关的对象类型
- 需要代码复用（继承层级）
- 需要多态行为
- 业务逻辑复杂

**不太适合**：
- 函数式、声明式处理（数据流）
- 简单的脚本工作
- 数据转换管道

## OOP 的四大设计原则

1. **单一职责** - 一个类一个职责
2. **开闭原则** - 对扩展开放，对修改关闭
3. **里氏替换** - 子类可替换父类
4. **接口隔离** - 依赖最小化接口

## 实战建议

### 1️⃣ 优先使用组合而非继承

```java
// ❌ 继承导致层级过深
public class FlyingCar extends Car {
    private boolean flying;
    public void fly() { ... }
}

// ✅ 组合更灵活
public class Car {
    private Engine engine;
    private Optional<Wing> wing;

    public void drive() { engine.run(); }
    public void fly() { wing.ifPresent(Wing::fly); }
}
```

### 2️⃣ 面向接口编程

```java
// ❌ 面向实现
public class UserService {
    private JpaUserRepository repository;
}

// ✅ 面向接口
public class UserService {
    private UserRepository repository;  // 接口
}
```

### 3️⃣ 避免继承层级过深

```
// ❌ 层级过深（脆弱基类问题）
Animal → Mammal → Carnivore → Cat → PersianCat → FatPersianCat

// ✅ 合理的层级
Animal → Cat
Cat 有 Breed, Weight 等属性
```

### 4️⃣ 使用设计模式

```java
// 工厂模式：创建对象
Factory factory = new ShapeFactory();
Shape shape = factory.create("CIRCLE");

// 观察者模式：对象间通信
observable.register(observer);

// 策略模式：行为组合
Sorter sorter = new Sorter(new QuickSort());
```

## 优缺点

### ✅ 优点
- 代码复用性高
- 易于维护和扩展
- 更接近现实建模
- 便于分工协作

### ❌ 缺点
- 学习曲线陡
- 过度设计风险
- 性能开销（多层调用）
- 继承滥用导致脆弱

## Python 实现示例

```python
from abc import ABC, abstractmethod

# 基类
class Animal(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def make_sound(self):
        pass

    @abstractmethod
    def move(self):
        pass

# 子类
class Dog(Animal):
    def make_sound(self):
        return "Woof!"

    def move(self):
        return "Running on four legs"

class Bird(Animal):
    def make_sound(self):
        return "Tweet!"

    def move(self):
        return "Flying with wings"

# 多态使用
animals = [Dog("Buddy"), Bird("Tweety")]
for animal in animals:
    print(f"{animal.name}: {animal.make_sound()}")
    print(f"  {animal.move()}")
```

## TypeScript 实现示例

```typescript
// 接口定义
interface Animal {
    name: string;
    makeSound(): string;
    move(): string;
}

// 实现
class Dog implements Animal {
    constructor(public name: string) {}

    makeSound(): string {
        return "Woof!";
    }

    move(): string {
        return "Running on four legs";
    }
}

// 多态使用
const animals: Animal[] = [
    new Dog("Buddy"),
    new Dog("Max")
];

animals.forEach(animal => {
    console.log(`${animal.name}: ${animal.makeSound()}`);
});
```

## 何时避免OOP

- 数据处理管道 → 使用函数式
- 配置驱动 → 使用配置文件
- 临时脚本 → 过度设计
- 仅需简单转换 → 直接函数

---

## 总结

**OOP的核心**：
- 将世界建模为对象
- 通过封装隐藏复杂性
- 通过继承复用代码
- 通过多态实现灵活性

**最佳实践**：
- 优先组合，后继承
- 面向接口编程
- 避免过深继承
- 遵循SOLID原则

OOP 适合复杂的业务系统，能大幅提高代码质量和可维护性。
