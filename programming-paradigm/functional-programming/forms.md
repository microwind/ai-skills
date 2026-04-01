# 函数式编程 - 诊断与规划表

## 第1步: 需求诊断

### 快速检查清单

```
□ 需要处理数据流（转换、过滤、聚合）
□ 需要并发处理，且无需同步
□ 代码中有大量集合操作
□ 需要高度可测试（纯逻辑）
□ 数据不会改变（不可变）
□ 计算过程可以分解为小函数
```

**诊断**：
- ✅ 4+ 项 → **强烈推荐FP**
- 2-3 项 → **可混合使用**
- 0-1 项 → **OOP可能更好**

### 场景评估

| 场景 | 适合度 | 建议 |
|------|--------|------|
| 数据处理管道 | ⭐⭐⭐⭐⭐ | 完全函数式 |
| Web框架 | ⭐⭐⭐ | 混合 |
| 游戏引擎 | ⭐ | 避免，用OOP |
| 数据分析 | ⭐⭐⭐⭐⭐ | 完全函数式 |
| 业务系统 | ⭐⭐⭐ | 混合 |

---

## 第2步: 函数设计

### 纯函数识别

```
当前代码：calculateDiscount

❌ 不纯（有副作用）:
public double calculateDiscount(Order order) {
    double discount = order.getAmount() * 0.1;
    discountedAmount += discount;  // 修改全局变量
    order.setDiscount(discount);    // 修改对象
    return discount;
}

✅ 纯函数:
public double calculateDiscount(double orderAmount) {
    return orderAmount * 0.1;  // 无副作用，纯逻辑
}
```

### 清单

```
分析当前代码中的函数：

函数1: ____________________
  是否纯函数？ YES / NO
  副作用：__________________
  改进：__________________

函数2: ____________________
  是否纯函数？ YES / NO
  副作用：__________________
  改进：__________________

函数3: ____________________
  是否纯函数？ YES / NO
  副作用：__________________
  改进：__________________
```

---

## 第3步: 数据处理管道设计

### 识别处理步骤

```
处理：订单数据清洗和分析

输入：List<RawOrder>

第1步：过滤有效订单
  filter(order -> order.isValid())

第2步：转换为标准格式
  map(order -> new StandardOrder(order))

第3步：应用折扣
  map(order -> applyDiscount(order))

第4步：计算总额
  reduce((a, b) -> a + b.getAmount())

输出：double totalAmount

实现：
List<RawOrder> orders = ...;
double total = orders.stream()
    .filter(Order::isValid)
    .map(StandardOrder::new)
    .map(this::applyDiscount)
    .mapToDouble(Order::getAmount)
    .sum();
```

---

## 第4步: 高阶函数设计

### 函数作为参数

```
设计：filter操作

public <T> List<T> filterData(List<T> data, Predicate<T> condition) {
    return data.stream()
        .filter(condition)
        .collect(toList());
}

使用：
List<Integer> evens = filterData(numbers, x -> x % 2 == 0);
List<String> shortNames = filterData(names, s -> s.length() < 5);
```

---

## 第5步: 不可变数据结构

### 转换为不可变

```
❌ 可变：
List<User> users = new ArrayList<>();
users.add(newUser);

✅ 不可变：
List<User> users = Collections.unmodifiableList(
    new ArrayList<>(Collections.singletonList(newUser))
);

或使用专门的库：
List<User> users = List.of(newUser);  // Java 9+
```

---

## 测试计划

### 纯函数测试

```
@Test
public void testCalculateDiscount() {
    double discount = calculateDiscount(100);
    assertEquals(10, discount);

    // 再调用一次，结果相同
    double discount2 = calculateDiscount(100);
    assertEquals(discount, discount2);
}

@Test
public void testPipelineProcessing() {
    List<Integer> input = Arrays.asList(1, 2, 3, 4, 5);
    List<Integer> result = input.stream()
        .filter(x -> x % 2 == 0)
        .map(x -> x * 2)
        .collect(toList());

    assertEquals(Arrays.asList(4, 8), result);
}
```

---

## 常见陷阱

### 陷阱1: 隐藏的副作用

```
❌ 看似纯函数，实际有副作用
public int sum(List<Integer> numbers) {
    return numbers.stream()
        .peek(n -> System.out.println(n))  // I/O副作用！
        .reduce(0, Integer::sum);
}

✅ 分离关注
public List<Integer> getNumbers() { ... }
public void printNumbers(List<Integer> nums) {
    nums.forEach(System.out::println);
}
public int sum(List<Integer> nums) {
    return nums.stream().reduce(0, Integer::sum);
}
```

### 陷阱2: 过度函数化

```
❌ 过度复杂
list.stream()
    .parallel()
    .filter(...)
    .map(...)
    .flatMap(...)
    .collect(toList());

✅ 适度简洁
list.stream()
    .filter(isValid)
    .map(transform)
    .collect(toList());
```

---

## 检查表

完成后验证：

```
设计检查：
□ 核心业务逻辑都是纯函数
□ 副作用隔离到专门的地方
□ 数据结构不可变
□ 使用 Stream API 处理集合

代码质量：
□ 函数短小精干（≤ 20行）
□ 易于单元测试
□ 无全局状态修改
□ 容易理解数据流

性能：
□ 无性能回归
□ 并发安全
□ 内存使用合理
```

FP 特别适合数据密集型应用。
