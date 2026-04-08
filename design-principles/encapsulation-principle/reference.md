# 封装原则 - 参考实现

## 核心原理与设计

封装 = **隐藏内部实现 + 保护数据完整性 + 通过受控接口交互**。封装不仅是 private 关键字，更是通过设计保证对象始终处于有效状态。

---

## Java 参考实现

### 反面示例

```java
/**
 * ❌ 缺乏封装
 */
public class BankAccount {
    public double balance;                    // 公开字段
    public List<Transaction> transactions;    // 公开可变集合

    // 任何人可以直接修改余额
    // account.balance = -1000;  合法但错误！
    // account.transactions.clear();  可以清空交易记录！
}
```

### 正面示例

```java
/**
 * ✅ 良好封装
 */
public class BankAccount {
    private double balance;
    private final List<Transaction> transactions = new ArrayList<>();
    private final String accountId;

    public BankAccount(String accountId, double initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("初始余额不能为负");
        this.accountId = accountId;
        this.balance = initialBalance;
    }

    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("存款金额必须为正");
        this.balance += amount;
        transactions.add(new Transaction(TransactionType.DEPOSIT, amount));
    }

    public void withdraw(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("取款金额必须为正");
        if (amount > balance) throw new InsufficientFundsException("余额不足");
        this.balance -= amount;
        transactions.add(new Transaction(TransactionType.WITHDRAWAL, amount));
    }

    public double getBalance() { return balance; }
    public String getAccountId() { return accountId; }

    // 返回不可变视图
    public List<Transaction> getTransactions() {
        return Collections.unmodifiableList(transactions);
    }
}

// 使用
BankAccount account = new BankAccount("ACC001", 1000);
account.deposit(500);
account.withdraw(200);
// account.balance = -1;  // 编译错误
// account.getTransactions().clear();  // UnsupportedOperationException
```

---

## Python 参考实现

```python
"""
✅ Python 封装实现
"""
class ShoppingCart:
    def __init__(self):
        self._items: list = []  # 受保护

    def add_item(self, product, quantity: int):
        if quantity <= 0:
            raise ValueError("数量必须为正")
        existing = self._find_item(product.id)
        if existing:
            existing.quantity += quantity
        else:
            self._items.append(CartItem(product, quantity))

    def remove_item(self, product_id: str):
        self._items = [i for i in self._items if i.product.id != product_id]

    @property
    def total(self) -> float:
        return sum(i.subtotal for i in self._items)

    @property
    def item_count(self) -> int:
        return sum(i.quantity for i in self._items)

    @property
    def items(self) -> tuple:
        return tuple(self._items)  # 返回不可变副本

    def _find_item(self, product_id: str):
        return next((i for i in self._items if i.product.id == product_id), None)

# ✅ Tell, Don't Ask
class Order:
    def __init__(self, items: list, customer):
        self._items = list(items)  # 防御性拷贝
        self._customer = customer
        self._status = "pending"

    def confirm(self):
        """告诉对象做什么，而非获取状态再判断"""
        if self._status != "pending":
            raise ValueError(f"只有待处理订单可以确认，当前状态: {self._status}")
        if not self._items:
            raise ValueError("空订单不能确认")
        self._status = "confirmed"

    def cancel(self):
        if self._status not in ("pending", "confirmed"):
            raise ValueError(f"当前状态 {self._status} 不可取消")
        self._status = "cancelled"

    @property
    def status(self) -> str:
        return self._status

    @property
    def total(self) -> float:
        return sum(i.price * i.quantity for i in self._items)
```

---

## TypeScript 参考实现

```typescript
/**
 * ✅ TypeScript 封装
 */
class User {
    private readonly _id: string;
    private _name: string;
    private _email: string;
    private readonly _roles: Set<string> = new Set();

    constructor(id: string, name: string, email: string) {
        if (!name.trim()) throw new Error('名字不能为空');
        if (!email.includes('@')) throw new Error('邮箱格式无效');
        this._id = id;
        this._name = name;
        this._email = email;
    }

    get id(): string { return this._id; }
    get name(): string { return this._name; }
    get email(): string { return this._email; }

    // 业务方法代替 setter
    updateProfile(name: string, email: string): void {
        if (!name.trim()) throw new Error('名字不能为空');
        if (!email.includes('@')) throw new Error('邮箱格式无效');
        this._name = name;
        this._email = email;
    }

    addRole(role: string): void {
        this._roles.add(role);
    }

    hasRole(role: string): boolean {
        return this._roles.has(role);
    }

    // 返回不可变副本
    get roles(): ReadonlySet<string> {
        return this._roles;
    }
}

// 不可变值对象
class Money {
    private constructor(
        private readonly _amount: number,
        private readonly _currency: string
    ) {
        if (_amount < 0) throw new Error('金额不能为负');
    }

    static of(amount: number, currency: string): Money {
        return new Money(amount, currency);
    }

    get amount(): number { return this._amount; }
    get currency(): string { return this._currency; }

    add(other: Money): Money {
        if (this._currency !== other._currency) throw new Error('币种不同');
        return Money.of(this._amount + other._amount, this._currency);
    }

    subtract(other: Money): Money {
        if (this._currency !== other._currency) throw new Error('币种不同');
        return Money.of(this._amount - other._amount, this._currency);
    }
}
```

---

## 单元测试示例

```java
class BankAccountTest {
    @Test
    void testDepositIncreasesBalance() {
        BankAccount account = new BankAccount("ACC001", 1000);
        account.deposit(500);
        assertEquals(1500, account.getBalance());
    }

    @Test
    void testWithdrawReducesBalance() {
        BankAccount account = new BankAccount("ACC001", 1000);
        account.withdraw(300);
        assertEquals(700, account.getBalance());
    }

    @Test
    void testCannotWithdrawMoreThanBalance() {
        BankAccount account = new BankAccount("ACC001", 100);
        assertThrows(InsufficientFundsException.class, () -> account.withdraw(200));
    }

    @Test
    void testTransactionsAreImmutable() {
        BankAccount account = new BankAccount("ACC001", 1000);
        account.deposit(100);
        assertThrows(UnsupportedOperationException.class,
            () -> account.getTransactions().clear());
    }

    @Test
    void testCannotCreateWithNegativeBalance() {
        assertThrows(IllegalArgumentException.class,
            () -> new BankAccount("ACC001", -100));
    }
}
```

```python
class TestShoppingCart:
    def test_add_item_increases_total(self):
        cart = ShoppingCart()
        cart.add_item(Product("P1", "商品A", 100), 2)
        assert cart.total == 200

    def test_items_returns_immutable(self):
        cart = ShoppingCart()
        cart.add_item(Product("P1", "商品A", 100), 1)
        items = cart.items
        assert isinstance(items, tuple)  # 不可变
```

---

## 总结

| 指标 | 无封装 | 良好封装 |
|------|--------|---------|
| 数据保护 | 任意修改 | 通过验证方法修改 |
| 不变量 | 随时可能被破坏 | 始终保持 |
| API 表面 | 所有字段暴露 | 最小必要接口 |
| 可维护性 | 修改内部影响所有调用方 | 内部变更对外透明 |
| 可测试性 | 需要设置大量内部状态 | 通过公开方法测试 |
