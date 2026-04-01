# 面向对象编程 - 诊断与规划表

## 第1步: 需求诊断

### 快速检查清单

```
□ 系统有多个相关对象需要协作
□ 存在代码重复（可通过继承复用）
□ 业务逻辑复杂，需要清晰的结构
□ 需要多态行为（同一接口，多种实现）
□ 需要长期维护和扩展
□ 团队规模大，需要清晰的职责分工
```

**诊断**：
- ✅ 4+ 项 → **强烈推荐使用OOP**
- 2-3 项 → **可以考虑OOP**
- 0-1 项 → **考虑函数式或程序式**

### 场景评估

| 场景 | 是否适合 | 建议 | 优先级 |
|------|---------|------|--------|
| 电商系统（订单、支付、库存） | ✅ | 建立Product、Order等对象 | ⭐⭐⭐⭐⭐ |
| 数据处理管道 | ❌ | 使用函数式 | 否 |
| 游戏引擎 | ✅ | GameObject、Component等 | ⭐⭐⭐⭐⭐ |
| 日期计算脚本 | ❌ | 函数式足够 | 否 |
| CRM系统 | ✅ | Customer、Lead、Deal等 | ⭐⭐⭐⭐⭐ |

---

## 第2步: 对象设计

### 识别对象

```
系统：电商平台

业务实体（对象）：
1. Product（商品）
   属性：id, name, price, inventory
   行为：getPrice(), reduceInventory(), isAvailable()

2. Customer（客户）
   属性：id, email, address
   行为：createOrder(), getOrderHistory()

3. Order（订单）
   属性：id, customer, items, status
   行为：addItem(), calculateTotal(), pay()

4. Payment（支付）
   属性：orderId, amount, method
   行为：process(), refund()

设计原则：
□ 一个对象 = 一个职责
□ 属性 = 名词（状态）
□ 方法 = 动词（行为）
□ 对象间有清晰的关系
```

### 清单

```
你的系统需要的主要对象：
1. ________________
   核心属性：__________________
   主要行为：__________________

2. ________________
   核心属性：__________________
   主要行为：__________________

3. ________________
   核心属性：__________________
   主要行为：__________________
```

---

## 第3步: 继承体系设计

### 识别通用特性

```
❌ 不必要的继承：
Animal → Dog → LargeDog

✅ 合理的继承：
Animal (base)
  ├── Dog
  ├── Cat
  └── Bird

或更好的：组合而非继承
Dog {
  breed: Breed
  size: Size
}
```

### 深度评估

```
规则：继承深度 ≤ 3 层

当前设计：
User
  ├── Admin
  │    ├── SuperAdmin
  │    │    └── SystemAdmin  ❌ 4层，太深
  │    └── NormalAdmin
  └── Customer

改为：
User {
  role: Role  // 组合而非继承
  permissions: Permission[]
}
```

---

## 第4步: 实现规划

### 类结构

```
第1步：定义基类和接口
  □ 创建 Product, Customer, Order 基类
  □ 定义 PaymentProcessor 接口
  □ 时间：1-2 天

第2步：实现具体类
  □ 创建各个具体类
  □ 编写构造函数和getter/setter
  □ 时间：2-3 天

第3步：实现业务逻辑
  □ 编写方法实现
  □ 处理错误情况
  □ 时间：3-5 天

第4步：编写测试
  □ 单元测试
  □ 集成测试
  □ 时间：2-3 天

总时间：8-13 天
```

---

## 第5步: 测试计划

### 单元测试

```
对每个类：
□ 测试构造函数
□ 测试getter/setter
□ 测试主要业务方法
□ 测试异常情况

示例：
@Test
public void testProductReduceInventory() {
    Product product = new Product("Book", 100.0, 10);
    product.reduceInventory(3);
    assertEquals(7, product.getInventory());
}

@Test
public void testProductReduceInventoryTooMuch() {
    Product product = new Product("Book", 100.0, 5);
    assertThrows(Exception.class, () -> product.reduceInventory(10));
}
```

### 集成测试

```
测试对象间的协作：
□ 创建订单，添加产品
□ 计算订单总额
□ 处理支付流程
□ 验证最终状态
```

---

## 常见陷阱

### 陷阱1: 继承滥用

```
❌ 不适当的继承
FlyingCar extends Car
SquarePencil extends Pencil extends Pen

✅ 使用组合
Car { wing: Optional<Wing> }
Pencil { shape: Shape }
```

### 陷阱2: 过深的继承层级

```
❌ 层级过深
Animal → Mammal → Carnivore → Cat → PersianCat → FatPersianCat

✅ 合理的层级
Animal
  ├── Dog
  ├── Cat
  └── Bird

// 其他特性通过属性：
Cat {
  breed: String
  color: String
}
```

### 陷阱3: 忽视接口

```
❌ 依赖具体类
UserService {
  JpaUserRepository repository;
}

✅ 依赖接口
UserService {
  UserRepository repository;  // 接口
}
```

---

## 检查表

完成后验证：

```
设计检查：
□ 每个类职责清晰（单一职责）
□ 继承深度 ≤ 3 层
□ 倾向组合而非继承
□ 所有关键类都有对应的接口

代码质量：
□ 代码覆盖率 ≥ 80%
□ 无过度设计
□ 命名清晰准确
□ 代码行数合理

可维护性：
□ 易于理解结构
□ 易于添加新功能
□ 易于修改现有功能
□ 新人易于上手
```

OOP能极大提高代码的组织性和可维护性。
