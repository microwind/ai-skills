---
name: 里氏替换原则
description: "子类型必须能够替换其基类型而不改变程序的正确性。所有引用基类的地方必须能透明地使用其子类对象。"
license: MIT
---

# 里氏替换原则 (Liskov Substitution Principle, LSP)

## 概述

里氏替换原则由 Barbara Liskov 于1987年提出，是 SOLID 原则中最容易被忽视但最关键的一条：**子类型必须能替换其父类型**。

**核心思想**：
- 子类可以扩展父类功能，但不能改变父类原有的行为
- 任何使用父类的地方，换成子类必须仍然正确
- 子类不应该加强前置条件或削弱后置条件
- 违反 LSP 通常意味着继承关系设计错误

**契约规则**：
- **前置条件**：子类不能比父类更严格
- **后置条件**：子类不能比父类更宽松
- **不变量**：子类必须维护父类的所有不变量

## 何时使用

**始终使用**：
- 使用继承构建类层次结构时
- 设计接口和抽象类时
- 泛型/模板编程中约束类型参数
- 多态替换场景

**触发短语**：
- "子类重写了父类方法但行为完全不同"
- "用子类替换父类后系统出现异常"
- "需要通过 instanceof 判断具体类型再处理"
- "子类抛出了父类不会抛出的异常"

## 经典案例：正方形与长方形

```java
// ❌ 违反 LSP：正方形继承长方形
public class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int width) { this.width = width; }
    public void setHeight(int height) { this.height = height; }
    public int getArea() { return width * height; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        this.width = width;
        this.height = width;  // 强制宽高相等，改变了父类行为
    }

    @Override
    public void setHeight(int height) {
        this.width = height;
        this.height = height;  // 强制宽高相等
    }
}

// 使用父类引用时出现问题
public void resize(Rectangle rect) {
    rect.setWidth(5);
    rect.setHeight(10);
    assert rect.getArea() == 50;  // Square 时失败！面积是 100
}
```

```java
// ✅ 正确设计：使用共同抽象
public interface Shape {
    int getArea();
}

public class Rectangle implements Shape {
    private final int width;
    private final int height;

    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public int getArea() { return width * height; }
}

public class Square implements Shape {
    private final int side;

    public Square(int side) { this.side = side; }

    @Override
    public int getArea() { return side * side; }
}
```

## 经典案例：鸟与企鹅

```java
// ❌ 违反 LSP：企鹅是鸟，但不会飞
public class Bird {
    public void fly() {
        System.out.println("飞行中...");
    }
}

public class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException("企鹅不会飞");
        // 子类抛出了父类不会抛出的异常
    }
}

public void makeBirdFly(Bird bird) {
    bird.fly();  // Penguin 时抛异常！
}
```

```java
// ✅ 正确设计：分离飞行能力
public abstract class Bird {
    public abstract String getName();
}

public interface Flyable {
    void fly();
}

public class Sparrow extends Bird implements Flyable {
    @Override
    public String getName() { return "麻雀"; }

    @Override
    public void fly() { System.out.println("麻雀飞行中"); }
}

public class Penguin extends Bird {
    @Override
    public String getName() { return "企鹅"; }
    // 企鹅不实现 Flyable，不会被要求飞行
}
```

## 违反 LSP 的常见表现

### 1. 子类抛出意外异常

```java
// ❌ 父类不抛异常，子类抛异常
public class FileReader {
    public String read(String path) {
        return "文件内容";
    }
}

public class EncryptedFileReader extends FileReader {
    @Override
    public String read(String path) {
        if (!hasPermission()) {
            throw new SecurityException("无权限");  // 违反 LSP
        }
        return decrypt(super.read(path));
    }
}
```

### 2. 子类忽略父类方法

```java
// ❌ 空实现 = 违反 LSP
public interface Collection<T> {
    void add(T item);
    void remove(T item);
    int size();
}

public class ReadOnlyList<T> implements Collection<T> {
    @Override
    public void add(T item) {
        // 什么都不做，静默忽略
    }

    @Override
    public void remove(T item) {
        throw new UnsupportedOperationException();  // 或者抛异常
    }
}
```

### 3. 需要类型检查才能工作

```java
// ❌ 代码中出现 instanceof 判断 = LSP 违反信号
public void processShape(Shape shape) {
    if (shape instanceof Circle) {
        // Circle 特殊处理
    } else if (shape instanceof Rectangle) {
        // Rectangle 特殊处理
    }
    // 每新增一种 Shape 都要修改这里
}

// ✅ 利用多态，无需类型判断
public void processShape(Shape shape) {
    shape.draw();  // 每种 Shape 自己实现 draw
}
```

## 代码示例 - 完整实现

### Python

```python
from abc import ABC, abstractmethod

# ❌ 违反 LSP
class Account:
    def __init__(self, balance: float):
        self.balance = balance

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount

class FixedDepositAccount(Account):
    """定期存款账户"""
    def withdraw(self, amount: float):
        raise RuntimeError("定期账户不允许提前支取")
        # 违反了父类的契约

# ✅ 遵循 LSP
class Account(ABC):
    def __init__(self, balance: float):
        self.balance = balance

    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

    def withdraw(self, amount: float):
        if not self.can_withdraw(amount):
            raise ValueError("不满足提取条件")
        self.balance -= amount

class SavingsAccount(Account):
    def can_withdraw(self, amount: float) -> bool:
        return amount <= self.balance

class FixedDepositAccount(Account):
    def __init__(self, balance: float, maturity_date):
        super().__init__(balance)
        self.maturity_date = maturity_date

    def can_withdraw(self, amount: float) -> bool:
        from datetime import date
        return date.today() >= self.maturity_date and amount <= self.balance
```

### TypeScript

```typescript
// ❌ 违反 LSP
interface Logger {
    log(message: string): void;
    getHistory(): string[];
}

class ConsoleLogger implements Logger {
    private history: string[] = [];

    log(message: string): void {
        console.log(message);
        this.history.push(message);
    }

    getHistory(): string[] {
        return [...this.history];
    }
}

class ExternalLogger implements Logger {
    log(message: string): void {
        // 发送到外部服务
        fetch('/api/log', { method: 'POST', body: message });
    }

    getHistory(): string[] {
        return [];  // 无法获取历史，返回空数组，违反语义契约
    }
}

// ✅ 遵循 LSP：分离接口
interface Logger {
    log(message: string): void;
}

interface HistoryLogger extends Logger {
    getHistory(): string[];
}

class ConsoleLogger implements HistoryLogger {
    private history: string[] = [];

    log(message: string): void {
        console.log(message);
        this.history.push(message);
    }

    getHistory(): string[] {
        return [...this.history];
    }
}

class ExternalLogger implements Logger {
    log(message: string): void {
        fetch('/api/log', { method: 'POST', body: message });
    }
    // 不需要实现 getHistory
}
```

## 优缺点分析

### ✅ 优点

1. **提高可替换性** - 子类可以安全地替换父类
2. **增强多态性** - 多态代码更可靠、更可预测
3. **减少条件判断** - 不需要 instanceof 检查
4. **促进正确的继承设计** - 迫使思考"is-a"关系的本质
5. **提升可测试性** - mock 对象能真正替代真实对象

### ❌ 缺点

1. **设计难度高** - 需要仔细思考契约
2. **可能导致类层次重构** - 发现违反时需要重新设计
3. **过度约束** - 某些场景下完美遵循很困难

## 最佳实践

### 1. 用"行为一致性"验证继承

```
问自己：
□ 子类的每个方法是否都满足父类方法的契约？
□ 子类是否维护了父类的所有不变量？
□ 用子类替换父类后，所有测试是否仍然通过？
□ 调用方是否需要知道具体子类类型才能正确工作？
```

### 2. 优先使用组合而非继承

```java
// 当 "is-a" 关系不成立时，用组合代替继承
public class FixedDeposit {
    private final Account account;  // 组合而非继承
    private final LocalDate maturityDate;

    public void withdrawOnMaturity() {
        if (LocalDate.now().isBefore(maturityDate)) {
            throw new IllegalStateException("未到期");
        }
        account.withdraw(account.getBalance());
    }
}
```

### 3. 基于契约编程

```java
// 明确定义方法的前置条件和后置条件
public abstract class Sorter {
    /**
     * 前置条件: list != null
     * 后置条件: 返回的列表包含原列表所有元素，且有序
     */
    public abstract <T extends Comparable<T>> List<T> sort(List<T> list);
}
```

### 4. 编写父类测试套件验证子类

```java
// 父类的测试应该对所有子类都通过
public abstract class AccountTest<T extends Account> {
    protected abstract T createAccount(double balance);

    @Test
    public void withdrawShouldReduceBalance() {
        T account = createAccount(100);
        account.withdraw(30);
        assertEquals(70, account.getBalance(), 0.01);
    }

    @Test
    public void withdrawExceedingBalanceShouldFail() {
        T account = createAccount(100);
        assertThrows(Exception.class, () -> account.withdraw(200));
    }
}

// 每个子类继承这套测试
public class SavingsAccountTest extends AccountTest<SavingsAccount> {
    @Override
    protected SavingsAccount createAccount(double balance) {
        return new SavingsAccount(balance);
    }
}
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [SRP](../single-responsibility-principle/) | SRP 保证类职责单一，LSP 保证替换安全 |
| [OCP](../open-closed-principle/) | LSP 是 OCP 的基础，违反 LSP 常导致违反 OCP |
| [ISP](../interface-segregation-principle/) | ISP 拆分接口，避免子类被迫实现不需要的方法 |
| [DIP](../dependency-inversion-principle/) | DIP 依赖抽象，LSP 保证抽象的子类可安全替换 |

## 总结

**LSP 核心**：
- 子类型必须能完全替换父类型
- 不改变前置条件、后置条件和不变量
- 违反 LSP 的信号：instanceof、空实现、意外异常

**检查方法**：
- 父类的测试套件对子类全部通过
- 不需要 instanceof 判断具体类型
- 子类不抛出父类未声明的异常
- 子类不忽略父类方法的语义

**修复违反**：
- 重新审视"is-a"关系
- 使用组合替代继承
- 提取更细粒度的接口
- 引入抽象层分离行为差异
