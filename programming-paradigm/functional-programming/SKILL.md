---
name: 函数式编程
description: "通过函数作为一等公民，强调不可变数据和纯函数，实现更可靠和可测试的代码。"
license: MIT
---

# 函数式编程 (Functional Programming, FP)

## 概述

FP 是一种编程范式，将计算描述为**函数的求值**，而非**状态的改变**。

**核心特征**：
- **一等函数**：函数作为值，可传递、返回
- **纯函数**：相同输入 → 相同输出，无副作用
- **不可变数据**：数据创建后不改变
- **函数组合**：小函数组合成大函数

**关键优势**：
- 代码更容易理解和推理
- 并发更安全（不可变）
- 测试更简单（纯函数）
- 复用性更高

## 核心概念

### 1. 纯函数 (Pure Function)

```java
// ❌ 不纯：有副作用
public int sum(List<Integer> numbers) {
    int total = 0;
    for (int n : numbers) {
        total += n;  // 修改total（副作用）
    }
    return total;
}

// ✅ 纯函数：无副作用，确定的输入→输出
public int sum(List<Integer> numbers) {
    return numbers.stream()
        .reduce(0, Integer::sum);
}

// 特点：
// 相同输入 → 相同输出
// 无修改外部状态
// 无I/O操作
// 无时间依赖
```

### 2. 不可变数据

```java
// ❌ 可变：修改列表
List<Integer> numbers = new ArrayList<>(Arrays.asList(1, 2, 3));
numbers.add(4);  // 修改原列表

// ✅ 不可变：创建新列表
List<Integer> original = Collections.unmodifiableList(Arrays.asList(1, 2, 3));
List<Integer> updated = new ArrayList<>(original);
updated.add(4);  // 创建新列表，原列表不变
```

### 3. 一等函数

```java
// 函数作为参数
public <T, R> List<R> map(List<T> list, Function<T, R> transform) {
    return list.stream().map(transform).collect(toList());
}

// 函数作为返回值
public Function<Integer, Integer> multiplyBy(int factor) {
    return x -> x * factor;
}

// 函数作为值（赋给变量）
Function<Integer, Integer> double_ = x -> x * 2;
```

### 4. 函数组合

```java
Function<Integer, Integer> addOne = x -> x + 1;
Function<Integer, Integer> double_ = x -> x * 2;

// 组合函数
Function<Integer, Integer> combined = addOne.andThen(double_);
// combined.apply(5) = (5 + 1) * 2 = 12
```

## 何时使用FP

**非常适合**：
- 数据处理管道（ETL、流处理）
- 并发编程（不可变性天然线程安全）
- 数学运算和变换
- 可测试的纯逻辑

**不太适合**：
- GUI事件处理（需要状态改变）
- 游戏开发（大量可变状态）
- 性能关键代码（可能有额外开销）

## 实战建议

### 1️⃣ 用Stream API处理集合

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// ❌ 命令式
int sum = 0;
for (int n : numbers) {
    if (n % 2 == 0) {
        sum += n * n;
    }
}

// ✅ 函数式
int sum = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .reduce(0, Integer::sum);
```

### 2️⃣ 使用Optional而非null

```java
// ❌ null检查
User user = findUser("john");
if (user != null) {
    String email = user.getEmail();
}

// ✅ Optional处理
Optional<User> user = findUser("john");
String email = user.map(User::getEmail).orElse("unknown");
```

### 3️⃣ 高阶函数

```java
// 接收函数作为参数
public List<Integer> applyToAll(List<Integer> numbers, Function<Integer, Integer> fn) {
    return numbers.stream().map(fn).collect(toList());
}

// 返回函数
public Function<Integer, Integer> createMultiplier(int factor) {
    return x -> x * factor;
}
```

### 4️⃣ 避免副作用

```java
// ❌ 有副作用
private List<String> names = new ArrayList<>();
public void processUsers(List<User> users) {
    users.forEach(u -> names.add(u.getName()));  // 修改names
}

// ✅ 纯函数
public List<String> extractNames(List<User> users) {
    return users.stream()
        .map(User::getName)
        .collect(toList());
}
```

## Python 实现示例

```python
from functools import reduce

# 纯函数
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# 函数作为参数
def map_transform(data, fn):
    return [fn(x) for x in data]

def filter_data(data, predicate):
    return [x for x in data if predicate(x)]

# 函数组合
def compose(f, g):
    return lambda x: f(g(x))

# 使用
numbers = [1, 2, 3, 4, 5]
result = filter_data(numbers, lambda x: x % 2 == 0)  # [2, 4]
result = map_transform(result, lambda x: x ** 2)      # [4, 16]
result = reduce(add, result)                          # 20
```

## TypeScript 实现示例

```typescript
// 纯函数
const add = (a: number, b: number): number => a + b;

// 高阶函数
const map = <T, R>(data: T[], fn: (x: T) => R): R[] => data.map(fn);
const filter = <T>(data: T[], pred: (x: T) => boolean): T[] => data.filter(pred);

// 函数组合
const compose = <T, U, V>(f: (x: U) => V, g: (x: T) => U) =>
    (x: T): V => f(g(x));

// 使用
const numbers = [1, 2, 3, 4, 5];
const result = numbers
    .filter(x => x % 2 === 0)  // [2, 4]
    .map(x => x ** 2)           // [4, 16]
    .reduce((a, b) => a + b);   // 20
```

## 优缺点

### ✅ 优点
- 代码易于理解和推理
- 并发安全（不可变性）
- 易于测试（纯函数）
- 更少的bug
- 易于并行化

### ❌ 缺点
- 学习曲线陡
- 性能可能略低（创建新对象）
- 某些问题表达困难
- 库生态相对少

## 与OOP的对比

| 特性 | OOP | FP |
|------|-----|-----|
| 数据组织 | 对象（数据+方法） | 纯数据 |
| 代码复用 | 继承 | 函数组合 |
| 变化 | 对象状态改变 | 新数据替换 |
| 并发 | 需要同步 | 天然安全 |
| 学习曲线 | 平缓 | 陡 |

---

## 总结

**FP的核心**：
- 纯函数：稳定可靠
- 不可变数据：线程安全
- 函数一等：灵活组合
- 函数组合：模块化

**最佳实践**：
- 优先纯函数，隔离副作用
- 使用 Stream/map/filter 处理集合
- 用 Optional 代替 null
- 倾向不可变数据结构

FP 适合数据处理系统，能大幅提高代码可靠性。
