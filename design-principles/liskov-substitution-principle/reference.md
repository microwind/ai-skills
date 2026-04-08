# 里氏替换原则 - 参考实现

## 核心原理

里氏替换原则（LSP）：**子类型必须能够替换其基类型，而不改变程序的正确性**。即对于基类 T 的所有对象 o1，存在子类 S 的对象 o2，使得所有针对 T 编写的程序 P，在用 o2 替换 o1 后，P 的行为不变。

### 关键设计要点

| 要点 | 说明 | 应用场景 |
|------|------|---------|
| 行为兼容 | 子类行为必须符合父类契约 | 继承设计 |
| 前置条件 | 子类不能加强前置条件 | 方法参数验证 |
| 后置条件 | 子类不能削弱后置条件 | 返回值保证 |
| 不变量 | 子类必须维持父类的不变量 | 状态管理 |
| 异常兼容 | 子类不能抛出新的异常类型 | 异常处理 |

---

## 案例一：矩形与正方形问题

### ❌ 错误实现 - Square 继承 Rectangle

```java
// Java - 经典 LSP 违反
public class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int width) {
        this.width = width;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    public int getWidth() { return width; }
    public int getHeight() { return height; }

    public int getArea() {
        return width * height;
    }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        // ❌ 破坏了 width 和 height 的独立性
        this.width = width;
        this.height = width;
    }

    @Override
    public void setHeight(int height) {
        // ❌ 破坏了 width 和 height 的独立性
        this.width = height;
        this.height = height;
    }
}

// 客户端代码 - 用 Square 替换 Rectangle 时失败
public class Client {
    public void resize(Rectangle rect) {
        rect.setWidth(5);
        rect.setHeight(10);
        // 期望面积 = 50
        assert rect.getArea() == 50; // ❌ Square 返回 100!
    }
}
```

```python
# Python - 经典 LSP 违反
class Rectangle:
    def __init__(self):
        self._width = 0
        self._height = 0

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    def get_area(self):
        return self._width * self._height

class Square(Rectangle):
    @Rectangle.width.setter
    def width(self, value):
        # ❌ 破坏独立性
        self._width = value
        self._height = value

    @Rectangle.height.setter
    def height(self, value):
        # ❌ 破坏独立性
        self._width = value
        self._height = value
```

```typescript
// TypeScript - 经典 LSP 违反
class Rectangle {
    protected _width: number = 0;
    protected _height: number = 0;

    set width(value: number) { this._width = value; }
    set height(value: number) { this._height = value; }
    get width() { return this._width; }
    get height() { return this._height; }

    getArea(): number {
        return this._width * this._height;
    }
}

class Square extends Rectangle {
    // ❌ 破坏独立性
    set width(value: number) {
        this._width = value;
        this._height = value;
    }
    set height(value: number) {
        this._width = value;
        this._height = value;
    }
}
```

### ✅ 正确实现 - Shape 接口

```java
// Java - 使用接口替代错误继承
public interface Shape {
    int getArea();
    int getPerimeter();
}

public class Rectangle implements Shape {
    private final int width;
    private final int height;

    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }

    public int getWidth() { return width; }
    public int getHeight() { return height; }

    @Override
    public int getArea() {
        return width * height;
    }

    @Override
    public int getPerimeter() {
        return 2 * (width + height);
    }

    public Rectangle withWidth(int newWidth) {
        return new Rectangle(newWidth, this.height);
    }

    public Rectangle withHeight(int newHeight) {
        return new Rectangle(this.width, newHeight);
    }
}

public class Square implements Shape {
    private final int side;

    public Square(int side) {
        this.side = side;
    }

    public int getSide() { return side; }

    @Override
    public int getArea() {
        return side * side;
    }

    @Override
    public int getPerimeter() {
        return 4 * side;
    }

    public Square withSide(int newSide) {
        return new Square(newSide);
    }
}

// 客户端代码 - 面向接口编程
public class AreaCalculator {
    public int totalArea(List<Shape> shapes) {
        return shapes.stream()
            .mapToInt(Shape::getArea)
            .sum();
    }
}
```

```python
# Python - 使用协议替代错误继承
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def get_area(self) -> int:
        pass

    @abstractmethod
    def get_perimeter(self) -> int:
        pass

class Rectangle(Shape):
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def get_area(self) -> int:
        return self._width * self._height

    def get_perimeter(self) -> int:
        return 2 * (self._width + self._height)

    def with_width(self, new_width: int) -> 'Rectangle':
        return Rectangle(new_width, self._height)

    def with_height(self, new_height: int) -> 'Rectangle':
        return Rectangle(self._width, new_height)

class Square(Shape):
    def __init__(self, side: int):
        self._side = side

    @property
    def side(self) -> int:
        return self._side

    def get_area(self) -> int:
        return self._side * self._side

    def get_perimeter(self) -> int:
        return 4 * self._side

    def with_side(self, new_side: int) -> 'Square':
        return Square(new_side)

class AreaCalculator:
    @staticmethod
    def total_area(shapes: list[Shape]) -> int:
        return sum(s.get_area() for s in shapes)
```

```typescript
// TypeScript - 使用接口替代错误继承
interface Shape {
    getArea(): number;
    getPerimeter(): number;
}

class Rectangle implements Shape {
    constructor(
        private readonly _width: number,
        private readonly _height: number
    ) {}

    get width() { return this._width; }
    get height() { return this._height; }

    getArea(): number {
        return this._width * this._height;
    }

    getPerimeter(): number {
        return 2 * (this._width + this._height);
    }

    withWidth(newWidth: number): Rectangle {
        return new Rectangle(newWidth, this._height);
    }

    withHeight(newHeight: number): Rectangle {
        return new Rectangle(this._width, newHeight);
    }
}

class Square implements Shape {
    constructor(private readonly _side: number) {}

    get side() { return this._side; }

    getArea(): number {
        return this._side * this._side;
    }

    getPerimeter(): number {
        return 4 * this._side;
    }

    withSide(newSide: number): Square {
        return new Square(newSide);
    }
}

class AreaCalculator {
    static totalArea(shapes: Shape[]): number {
        return shapes.reduce((sum, s) => sum + s.getArea(), 0);
    }
}
```

---

## 案例二：鸟与企鹅问题

### ❌ 错误实现 - Penguin 继承 Bird 并抛出异常

```java
// Java - 企鹅继承了飞行能力
public class Bird {
    public void fly() {
        System.out.println("展翅飞翔...");
    }

    public void eat() {
        System.out.println("进食中...");
    }

    public String getSound() {
        return "叽叽喳喳";
    }
}

public class Penguin extends Bird {
    @Override
    public void fly() {
        // ❌ 抛出父类未声明的异常
        throw new UnsupportedOperationException("企鹅不会飞!");
    }

    @Override
    public String getSound() {
        return "嘎嘎";
    }
}

// 客户端代码
public class BirdMigration {
    public void migrate(List<Bird> birds) {
        for (Bird bird : birds) {
            bird.fly(); // ❌ 遇到企鹅时崩溃!
        }
    }
}
```

```python
# Python - 企鹅继承了飞行能力
class Bird:
    def fly(self):
        print("展翅飞翔...")

    def eat(self):
        print("进食中...")

class Penguin(Bird):
    def fly(self):
        # ❌ 抛出意外异常
        raise NotImplementedError("企鹅不会飞!")

def migrate(birds: list[Bird]):
    for bird in birds:
        bird.fly()  # ❌ 遇到企鹅时崩溃!
```

```typescript
// TypeScript - 企鹅继承了飞行能力
class Bird {
    fly(): void {
        console.log("展翅飞翔...");
    }
    eat(): void {
        console.log("进食中...");
    }
}

class Penguin extends Bird {
    fly(): void {
        // ❌ 抛出意外异常
        throw new Error("企鹅不会飞!");
    }
}

function migrate(birds: Bird[]): void {
    for (const bird of birds) {
        bird.fly(); // ❌ 遇到企鹅时崩溃!
    }
}
```

### ✅ 正确实现 - Flyable 接口分离

```java
// Java - 使用接口分离飞行能力
public interface Animal {
    void eat();
    String getSound();
}

public interface Flyable {
    void fly();
    double getFlightSpeed();
}

public interface Swimmable {
    void swim();
    double getSwimSpeed();
}

public class Sparrow implements Animal, Flyable {
    @Override
    public void eat() {
        System.out.println("麻雀啄食...");
    }

    @Override
    public String getSound() {
        return "叽叽喳喳";
    }

    @Override
    public void fly() {
        System.out.println("麻雀飞翔...");
    }

    @Override
    public double getFlightSpeed() {
        return 40.0;
    }
}

public class Penguin implements Animal, Swimmable {
    @Override
    public void eat() {
        System.out.println("企鹅捕鱼...");
    }

    @Override
    public String getSound() {
        return "嘎嘎";
    }

    @Override
    public void swim() {
        System.out.println("企鹅游泳...");
    }

    @Override
    public double getSwimSpeed() {
        return 22.0;
    }
}

public class Duck implements Animal, Flyable, Swimmable {
    @Override
    public void eat() { System.out.println("鸭子觅食..."); }

    @Override
    public String getSound() { return "嘎嘎嘎"; }

    @Override
    public void fly() { System.out.println("鸭子飞翔..."); }

    @Override
    public double getFlightSpeed() { return 80.0; }

    @Override
    public void swim() { System.out.println("鸭子游泳..."); }

    @Override
    public double getSwimSpeed() { return 5.0; }
}

// 客户端代码 - 类型安全，无异常风险
public class Migration {
    public void migrate(List<Flyable> flyables) {
        for (Flyable f : flyables) {
            f.fly(); // ✅ 只有能飞的才会在这里
        }
    }
}
```

```python
# Python - 使用协议分离飞行能力
from abc import ABC, abstractmethod
from typing import Protocol

class Animal(ABC):
    @abstractmethod
    def eat(self) -> None:
        pass

    @abstractmethod
    def get_sound(self) -> str:
        pass

class Flyable(Protocol):
    def fly(self) -> None: ...
    def get_flight_speed(self) -> float: ...

class Swimmable(Protocol):
    def swim(self) -> None: ...
    def get_swim_speed(self) -> float: ...

class Sparrow(Animal):
    def eat(self) -> None:
        print("麻雀啄食...")

    def get_sound(self) -> str:
        return "叽叽喳喳"

    def fly(self) -> None:
        print("麻雀飞翔...")

    def get_flight_speed(self) -> float:
        return 40.0

class Penguin(Animal):
    def eat(self) -> None:
        print("企鹅捕鱼...")

    def get_sound(self) -> str:
        return "嘎嘎"

    def swim(self) -> None:
        print("企鹅游泳...")

    def get_swim_speed(self) -> float:
        return 22.0

class Duck(Animal):
    def eat(self) -> None:
        print("鸭子觅食...")

    def get_sound(self) -> str:
        return "嘎嘎嘎"

    def fly(self) -> None:
        print("鸭子飞翔...")

    def get_flight_speed(self) -> float:
        return 80.0

    def swim(self) -> None:
        print("鸭子游泳...")

    def get_swim_speed(self) -> float:
        return 5.0

def migrate(flyables: list[Flyable]) -> None:
    for f in flyables:
        f.fly()  # ✅ 类型安全
```

```typescript
// TypeScript - 使用接口分离飞行能力
interface Animal {
    eat(): void;
    getSound(): string;
}

interface Flyable {
    fly(): void;
    getFlightSpeed(): number;
}

interface Swimmable {
    swim(): void;
    getSwimSpeed(): number;
}

class Sparrow implements Animal, Flyable {
    eat(): void { console.log("麻雀啄食..."); }
    getSound(): string { return "叽叽喳喳"; }
    fly(): void { console.log("麻雀飞翔..."); }
    getFlightSpeed(): number { return 40.0; }
}

class Penguin implements Animal, Swimmable {
    eat(): void { console.log("企鹅捕鱼..."); }
    getSound(): string { return "嘎嘎"; }
    swim(): void { console.log("企鹅游泳..."); }
    getSwimSpeed(): number { return 22.0; }
}

class Duck implements Animal, Flyable, Swimmable {
    eat(): void { console.log("鸭子觅食..."); }
    getSound(): string { return "嘎嘎嘎"; }
    fly(): void { console.log("鸭子飞翔..."); }
    getFlightSpeed(): number { return 80.0; }
    swim(): void { console.log("鸭子游泳..."); }
    getSwimSpeed(): number { return 5.0; }
}

function migrate(flyables: Flyable[]): void {
    for (const f of flyables) {
        f.fly(); // ✅ 类型安全
    }
}
```

---

## 案例三：账户层次体系

### ❌ 错误实现 - 定期账户继承活期账户

```java
// Java - 定期账户违反提款契约
public class Account {
    protected double balance;

    public Account(double initialBalance) {
        this.balance = initialBalance;
    }

    public double getBalance() {
        return balance;
    }

    /**
     * 提款方法
     * @pre amount > 0 && amount <= balance
     * @post balance = old(balance) - amount
     */
    public void withdraw(double amount) {
        if (amount <= 0 || amount > balance) {
            throw new IllegalArgumentException("无效提款金额");
        }
        balance -= amount;
    }

    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("存款金额必须为正");
        }
        balance += amount;
    }
}

public class FixedDepositAccount extends Account {
    private final LocalDate maturityDate;

    public FixedDepositAccount(double balance, LocalDate maturityDate) {
        super(balance);
        this.maturityDate = maturityDate;
    }

    @Override
    public void withdraw(double amount) {
        // ❌ 加强了前置条件：还要检查到期日
        if (LocalDate.now().isBefore(maturityDate)) {
            throw new IllegalStateException("定期未到期，不可提款!");
        }
        super.withdraw(amount);
    }
}

// 客户端代码
public class ATM {
    public void processWithdrawal(Account account, double amount) {
        // 客户端按照 Account 的契约编写
        if (amount > 0 && amount <= account.getBalance()) {
            account.withdraw(amount); // ❌ FixedDepositAccount 可能抛出 IllegalStateException
        }
    }
}
```

### ✅ 正确实现 - 合理的账户契约

```java
// Java - 正确的账户层次设计
public interface Depositable {
    void deposit(double amount);
    double getBalance();
}

public interface Withdrawable {
    boolean canWithdraw(double amount);
    void withdraw(double amount);
}

public interface Account extends Depositable {
    String getAccountId();
    AccountType getType();
}

// 活期账户：可存可取
public class SavingsAccount implements Account, Withdrawable {
    private final String accountId;
    private double balance;

    public SavingsAccount(String accountId, double initialBalance) {
        this.accountId = accountId;
        this.balance = initialBalance;
    }

    @Override
    public String getAccountId() { return accountId; }

    @Override
    public AccountType getType() { return AccountType.SAVINGS; }

    @Override
    public double getBalance() { return balance; }

    @Override
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("金额必须为正");
        balance += amount;
    }

    @Override
    public boolean canWithdraw(double amount) {
        return amount > 0 && amount <= balance;
    }

    @Override
    public void withdraw(double amount) {
        if (!canWithdraw(amount)) {
            throw new IllegalArgumentException("无效提款金额");
        }
        balance -= amount;
    }
}

// 定期账户：可存，有条件取
public class FixedDepositAccount implements Account, Withdrawable {
    private final String accountId;
    private double balance;
    private final LocalDate maturityDate;

    public FixedDepositAccount(String accountId, double balance, LocalDate maturityDate) {
        this.accountId = accountId;
        this.balance = balance;
        this.maturityDate = maturityDate;
    }

    @Override
    public String getAccountId() { return accountId; }

    @Override
    public AccountType getType() { return AccountType.FIXED_DEPOSIT; }

    @Override
    public double getBalance() { return balance; }

    @Override
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("金额必须为正");
        balance += amount;
    }

    @Override
    public boolean canWithdraw(double amount) {
        // ✅ 通过 canWithdraw 告知客户端当前能否提款
        return amount > 0 && amount <= balance && !LocalDate.now().isBefore(maturityDate);
    }

    @Override
    public void withdraw(double amount) {
        if (!canWithdraw(amount)) {
            throw new IllegalArgumentException("无法提款：金额无效或定期未到期");
        }
        balance -= amount;
    }

    public LocalDate getMaturityDate() { return maturityDate; }
}

// ✅ 客户端代码 - 安全的提款流程
public class ATM {
    public void processWithdrawal(Withdrawable account, double amount) {
        if (account.canWithdraw(amount)) {
            account.withdraw(amount);
            System.out.println("提款成功");
        } else {
            System.out.println("当前无法提款，请检查条件");
        }
    }
}
```

```python
# Python - 正确的账户层次设计
from abc import ABC, abstractmethod
from datetime import date

class Depositable(ABC):
    @abstractmethod
    def deposit(self, amount: float) -> None:
        pass

    @abstractmethod
    def get_balance(self) -> float:
        pass

class Withdrawable(ABC):
    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        pass

class SavingsAccount(Depositable, Withdrawable):
    def __init__(self, account_id: str, initial_balance: float):
        self._account_id = account_id
        self._balance = initial_balance

    def get_balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("金额必须为正")
        self._balance += amount

    def can_withdraw(self, amount: float) -> bool:
        return 0 < amount <= self._balance

    def withdraw(self, amount: float) -> None:
        if not self.can_withdraw(amount):
            raise ValueError("无效提款金额")
        self._balance -= amount

class FixedDepositAccount(Depositable, Withdrawable):
    def __init__(self, account_id: str, balance: float, maturity_date: date):
        self._account_id = account_id
        self._balance = balance
        self._maturity_date = maturity_date

    def get_balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("金额必须为正")
        self._balance += amount

    def can_withdraw(self, amount: float) -> bool:
        return 0 < amount <= self._balance and date.today() >= self._maturity_date

    def withdraw(self, amount: float) -> None:
        if not self.can_withdraw(amount):
            raise ValueError("无法提款")
        self._balance -= amount

# ✅ 客户端代码
def process_withdrawal(account: Withdrawable, amount: float) -> bool:
    if account.can_withdraw(amount):
        account.withdraw(amount)
        return True
    return False
```

```typescript
// TypeScript - 正确的账户层次设计
interface Depositable {
    deposit(amount: number): void;
    getBalance(): number;
}

interface Withdrawable {
    canWithdraw(amount: number): boolean;
    withdraw(amount: number): void;
}

class SavingsAccount implements Depositable, Withdrawable {
    private balance: number;

    constructor(
        private readonly accountId: string,
        initialBalance: number
    ) {
        this.balance = initialBalance;
    }

    getBalance(): number { return this.balance; }

    deposit(amount: number): void {
        if (amount <= 0) throw new Error("金额必须为正");
        this.balance += amount;
    }

    canWithdraw(amount: number): boolean {
        return amount > 0 && amount <= this.balance;
    }

    withdraw(amount: number): void {
        if (!this.canWithdraw(amount)) throw new Error("无效提款金额");
        this.balance -= amount;
    }
}

class FixedDepositAccount implements Depositable, Withdrawable {
    private balance: number;

    constructor(
        private readonly accountId: string,
        initialBalance: number,
        private readonly maturityDate: Date
    ) {
        this.balance = initialBalance;
    }

    getBalance(): number { return this.balance; }

    deposit(amount: number): void {
        if (amount <= 0) throw new Error("金额必须为正");
        this.balance += amount;
    }

    canWithdraw(amount: number): boolean {
        return amount > 0 && amount <= this.balance && new Date() >= this.maturityDate;
    }

    withdraw(amount: number): void {
        if (!this.canWithdraw(amount)) throw new Error("无法提款");
        this.balance -= amount;
    }
}

// ✅ 客户端代码
function processWithdrawal(account: Withdrawable, amount: number): boolean {
    if (account.canWithdraw(amount)) {
        account.withdraw(amount);
        return true;
    }
    return false;
}
```

---

## 测试

### LSP 合规测试

```java
// Java - 所有子类型的合规测试
public class ShapeLspTest {

    static Stream<Shape> allShapes() {
        return Stream.of(
            new Rectangle(5, 10),
            new Square(7)
        );
    }

    @ParameterizedTest
    @MethodSource("allShapes")
    void areaShouldBePositive(Shape shape) {
        assertTrue(shape.getArea() > 0);
    }

    @ParameterizedTest
    @MethodSource("allShapes")
    void perimeterShouldBePositive(Shape shape) {
        assertTrue(shape.getPerimeter() > 0);
    }
}

public class AnimalLspTest {

    static Stream<Animal> allAnimals() {
        return Stream.of(new Sparrow(), new Penguin(), new Duck());
    }

    @ParameterizedTest
    @MethodSource("allAnimals")
    void allAnimalsShouldEat(Animal animal) {
        assertDoesNotThrow(animal::eat);
    }

    @ParameterizedTest
    @MethodSource("allAnimals")
    void allAnimalsShouldHaveSound(Animal animal) {
        assertNotNull(animal.getSound());
        assertFalse(animal.getSound().isEmpty());
    }

    @Test
    void onlyFlyablesShouldFly() {
        List<Flyable> flyables = List.of(new Sparrow(), new Duck());
        for (Flyable f : flyables) {
            assertDoesNotThrow(f::fly);
            assertTrue(f.getFlightSpeed() > 0);
        }
    }
}

public class AccountLspTest {

    static Stream<Withdrawable> allWithdrawable() {
        return Stream.of(
            new SavingsAccount("S001", 1000),
            new FixedDepositAccount("F001", 1000, LocalDate.now().minusDays(1))
        );
    }

    @ParameterizedTest
    @MethodSource("allWithdrawable")
    void canWithdrawShouldReflectActualAbility(Withdrawable account) {
        if (account.canWithdraw(100)) {
            assertDoesNotThrow(() -> account.withdraw(100));
        }
    }

    @ParameterizedTest
    @MethodSource("allWithdrawable")
    void withdrawShouldReduceBalance(Withdrawable account) {
        if (account instanceof Depositable depositable) {
            double before = depositable.getBalance();
            if (account.canWithdraw(100)) {
                account.withdraw(100);
                assertEquals(before - 100, depositable.getBalance(), 0.01);
            }
        }
    }
}
```

```python
# Python - 合规测试
import pytest
from datetime import date, timedelta

class TestShapeLsp:
    @pytest.fixture(params=[
        Rectangle(5, 10),
        Square(7),
    ])
    def shape(self, request):
        return request.param

    def test_area_should_be_positive(self, shape):
        assert shape.get_area() > 0

    def test_perimeter_should_be_positive(self, shape):
        assert shape.get_perimeter() > 0

class TestAnimalLsp:
    @pytest.fixture(params=[Sparrow, Penguin, Duck])
    def animal(self, request):
        return request.param()

    def test_all_animals_should_eat(self, animal):
        animal.eat()  # 不应抛异常

    def test_all_animals_should_have_sound(self, animal):
        assert animal.get_sound()

class TestAccountLsp:
    @pytest.fixture(params=[
        lambda: SavingsAccount("S001", 1000),
        lambda: FixedDepositAccount("F001", 1000, date.today() - timedelta(days=1)),
    ])
    def withdrawable(self, request):
        return request.param()

    def test_can_withdraw_reflects_ability(self, withdrawable):
        if withdrawable.can_withdraw(100):
            withdrawable.withdraw(100)  # 不应抛异常

    def test_withdraw_reduces_balance(self, withdrawable):
        before = withdrawable.get_balance()
        if withdrawable.can_withdraw(100):
            withdrawable.withdraw(100)
            assert withdrawable.get_balance() == pytest.approx(before - 100)
```

```typescript
// TypeScript - 合规测试
describe('Shape LSP', () => {
    const shapes: Shape[] = [new Rectangle(5, 10), new Square(7)];

    shapes.forEach(shape => {
        describe(shape.constructor.name, () => {
            it('area should be positive', () => {
                expect(shape.getArea()).toBeGreaterThan(0);
            });
            it('perimeter should be positive', () => {
                expect(shape.getPerimeter()).toBeGreaterThan(0);
            });
        });
    });
});

describe('Animal LSP', () => {
    const animals: Animal[] = [new Sparrow(), new Penguin(), new Duck()];

    animals.forEach(animal => {
        it(`${animal.constructor.name} should eat without error`, () => {
            expect(() => animal.eat()).not.toThrow();
        });
        it(`${animal.constructor.name} should have a sound`, () => {
            expect(animal.getSound()).toBeTruthy();
        });
    });
});

describe('Account LSP', () => {
    const accounts: Withdrawable[] = [
        new SavingsAccount('S001', 1000),
        new FixedDepositAccount('F001', 1000, new Date(Date.now() - 86400000)),
    ];

    accounts.forEach(account => {
        it(`${account.constructor.name} canWithdraw reflects ability`, () => {
            if (account.canWithdraw(100)) {
                expect(() => account.withdraw(100)).not.toThrow();
            }
        });
    });
});
```

---

## 总结对照表

| 场景 | ❌ 违反 LSP | ✅ 遵循 LSP |
|------|-----------|-----------|
| 矩形/正方形 | Square 继承 Rectangle 并联动修改宽高 | 各自实现 Shape 接口，使用不可变对象 |
| 鸟/企鹅 | Penguin 继承 Bird 但 fly() 抛异常 | 拆分 Flyable/Swimmable 接口 |
| 账户体系 | FixedDeposit 继承 Account 并加强前置条件 | canWithdraw() 契约方法 + 接口分离 |
