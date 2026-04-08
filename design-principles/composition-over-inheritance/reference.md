# 组合优于继承 - 参考实现

## 核心原理与设计

### 继承 vs 组合

继承是**静态的、编译时绑定**的代码复用方式；组合是**动态的、运行时可变**的代码复用方式。当"is-a"关系不成立或需要运行时灵活性时，组合优于继承。

---

## Java 参考实现

### 反面示例：脆弱的继承设计

```java
/**
 * ❌ 反面示例：继承导致脆弱基类问题
 */
public class InstrumentedArrayList<E> extends ArrayList<E> {
    private int addCount = 0;

    @Override
    public boolean add(E e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);  // 父类 addAll 内部调用 add，导致计数翻倍！
    }

    public int getAddCount() { return addCount; }
}

// 测试
InstrumentedArrayList<String> list = new InstrumentedArrayList<>();
list.addAll(Arrays.asList("a", "b", "c"));
System.out.println(list.getAddCount());  // 期望3，实际6！
```

### 正面示例：组合实现相同功能

```java
/**
 * ✅ 正面示例：组合方式，不依赖父类实现细节
 */

// 方式1：包装器（装饰器）
public class InstrumentedList<E> implements List<E> {
    private final List<E> delegate;
    private int addCount = 0;

    public InstrumentedList(List<E> delegate) {
        this.delegate = delegate;
    }

    @Override
    public boolean add(E e) {
        addCount++;
        return delegate.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return delegate.addAll(c);  // 不关心内部实现
    }

    public int getAddCount() { return addCount; }

    // 委托其他 List 方法
    @Override public int size() { return delegate.size(); }
    @Override public E get(int index) { return delegate.get(index); }
    @Override public E remove(int index) { return delegate.remove(index); }
    // ... 其他方法委托给 delegate
}

// 使用
InstrumentedList<String> list = new InstrumentedList<>(new ArrayList<>());
list.addAll(Arrays.asList("a", "b", "c"));
System.out.println(list.getAddCount());  // 正确输出3

// 方式2：策略模式 - 行为注入
public interface FlyBehavior {
    String fly();
}

public interface QuackBehavior {
    String quack();
}

public class FlyWithWings implements FlyBehavior {
    public String fly() { return "振翅飞行"; }
}

public class FlyNoWay implements FlyBehavior {
    public String fly() { return "不会飞"; }
}

public class Quack implements QuackBehavior {
    public String quack() { return "嘎嘎叫"; }
}

public class MuteQuack implements QuackBehavior {
    public String quack() { return "（安静）"; }
}

// 鸭子类通过组合获得行为
public class Duck {
    private FlyBehavior flyBehavior;
    private QuackBehavior quackBehavior;
    private final String name;

    public Duck(String name, FlyBehavior flyBehavior, QuackBehavior quackBehavior) {
        this.name = name;
        this.flyBehavior = flyBehavior;
        this.quackBehavior = quackBehavior;
    }

    public String performFly() { return name + ": " + flyBehavior.fly(); }
    public String performQuack() { return name + ": " + quackBehavior.quack(); }

    // 运行时切换行为
    public void setFlyBehavior(FlyBehavior fb) { this.flyBehavior = fb; }
    public void setQuackBehavior(QuackBehavior qb) { this.quackBehavior = qb; }
}

// 使用
Duck mallard = new Duck("绿头鸭", new FlyWithWings(), new Quack());
Duck rubber = new Duck("橡皮鸭", new FlyNoWay(), new MuteQuack());

System.out.println(mallard.performFly());   // 绿头鸭: 振翅飞行
System.out.println(rubber.performFly());    // 橡皮鸭: 不会飞

// 运行时改变行为
rubber.setFlyBehavior(new FlyWithWings());
System.out.println(rubber.performFly());    // 橡皮鸭: 振翅飞行
```

---

## Python 参考实现

```python
"""
✅ Python 组合优于继承实现
"""
from abc import ABC, abstractmethod

# ❌ 多重继承的菱形问题
class Animal:
    def speak(self): return "..."

class Flyer(Animal):
    def speak(self): return "在飞"

class Swimmer(Animal):
    def speak(self): return "在游"

class FlyingFish(Flyer, Swimmer):  # MRO 决定调用哪个 speak
    pass

print(FlyingFish().speak())  # "在飞" - 取决于 MRO，不直观

# ✅ 组合方式
class FlyAbility(ABC):
    @abstractmethod
    def fly(self) -> str: pass

class SwimAbility(ABC):
    @abstractmethod
    def swim(self) -> str: pass

class WingFly(FlyAbility):
    def fly(self) -> str: return "用翅膀飞行"

class FinSwim(SwimAbility):
    def swim(self) -> str: return "用鳍游泳"

class FlyingFish:
    def __init__(self, fly_ability: FlyAbility, swim_ability: SwimAbility):
        self._fly = fly_ability
        self._swim = swim_ability

    def fly(self) -> str: return self._fly.fly()
    def swim(self) -> str: return self._swim.swim()

fish = FlyingFish(WingFly(), FinSwim())
print(fish.fly())   # 用翅膀飞行
print(fish.swim())  # 用鳍游泳


# ✅ 带行为注入的通知系统
class NotificationSender(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> bool: pass

class EmailSender(NotificationSender):
    def send(self, to: str, message: str) -> bool:
        print(f"发送邮件到 {to}: {message}")
        return True

class SmsSender(NotificationSender):
    def send(self, to: str, message: str) -> bool:
        print(f"发送短信到 {to}: {message}")
        return True

class PushSender(NotificationSender):
    def send(self, to: str, message: str) -> bool:
        print(f"推送通知到 {to}: {message}")
        return True

class NotificationService:
    """通过组合支持多种通知方式，运行时可配置"""
    def __init__(self, senders: list[NotificationSender]):
        self._senders = senders

    def notify(self, to: str, message: str):
        for sender in self._senders:
            sender.send(to, message)

    def add_sender(self, sender: NotificationSender):
        self._senders.append(sender)

# 灵活组合
service = NotificationService([EmailSender(), SmsSender()])
service.notify("user@example.com", "订单已发货")
service.add_sender(PushSender())  # 运行时添加新通知方式
```

---

## TypeScript 参考实现

```typescript
/**
 * ✅ TypeScript 组合实现
 */

// 行为接口
interface Logger {
    log(message: string): void;
}

interface Validator<T> {
    validate(data: T): boolean;
}

interface Repository<T> {
    save(entity: T): void;
    findById(id: string): T | undefined;
}

// 行为实现
class ConsoleLogger implements Logger {
    log(message: string): void {
        console.log(`[LOG] ${message}`);
    }
}

class UserValidator implements Validator<User> {
    validate(user: User): boolean {
        return user.name.length > 0 && user.email.includes('@');
    }
}

class InMemoryUserRepo implements Repository<User> {
    private store = new Map<string, User>();
    save(user: User): void { this.store.set(user.id, user); }
    findById(id: string): User | undefined { return this.store.get(id); }
}

// 通过组合构建服务（而非继承 BaseService）
class UserService {
    constructor(
        private logger: Logger,
        private validator: Validator<User>,
        private repository: Repository<User>
    ) {}

    createUser(user: User): void {
        this.logger.log(`Creating user: ${user.name}`);
        if (!this.validator.validate(user)) {
            throw new Error('Invalid user data');
        }
        this.repository.save(user);
        this.logger.log(`User created: ${user.id}`);
    }

    getUser(id: string): User | undefined {
        this.logger.log(`Finding user: ${id}`);
        return this.repository.findById(id);
    }
}

// 使用 - 可以自由组合不同实现
const service = new UserService(
    new ConsoleLogger(),
    new UserValidator(),
    new InMemoryUserRepo()
);
```

---

## 单元测试示例

```java
class DuckTest {
    @Test
    void testFlyBehaviorInjection() {
        Duck duck = new Duck("测试鸭", new FlyWithWings(), new Quack());
        assertEquals("测试鸭: 振翅飞行", duck.performFly());
    }

    @Test
    void testRuntimeBehaviorChange() {
        Duck duck = new Duck("测试鸭", new FlyNoWay(), new MuteQuack());
        assertEquals("测试鸭: 不会飞", duck.performFly());

        duck.setFlyBehavior(new FlyWithWings());
        assertEquals("测试鸭: 振翅飞行", duck.performFly());
    }
}

class InstrumentedListTest {
    @Test
    void testAddCountCorrect() {
        InstrumentedList<String> list = new InstrumentedList<>(new ArrayList<>());
        list.addAll(Arrays.asList("a", "b", "c"));
        assertEquals(3, list.getAddCount()); // 组合方式计数正确
    }
}
```

---

## 总结

| 指标 | 继承方式 | 组合方式 |
|------|---------|---------|
| 耦合度 | 高（依赖父类实现） | 低（依赖接口） |
| 灵活性 | 编译时固定 | 运行时可变 |
| 可测试性 | 难（需要父类上下文） | 易（可 mock 注入） |
| 代码复用 | 脆弱（基类变更影响所有子类） | 稳定（接口契约） |
| 适用场景 | 真正的 is-a + 层次 ≤ 2 | has-a / 需要灵活性 |
