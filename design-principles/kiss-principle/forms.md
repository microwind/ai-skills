# KISS原则 - 诊断与规划表

## 第1步: 需求诊断 - 你的代码是否过度复杂？

### 快速检查清单

```
□ 方法超过 20 行
□ 条件嵌套超过 3 层
□ 方法参数超过 4 个
□ 使用了不必要的设计模式
□ 存在过度工程化的抽象
□ 代码中有"以防万一"的功能
□ 简单功能却有复杂的类层次结构
□ 存在未被使用的通用化设计
```

**诊断标准**:
- ✅ 0-1 项 → **很好，代码保持简洁**
- ⚠️ 2-4 项 → **存在过度设计倾向，建议简化**
- ❌ 5 项以上 → **严重过度设计，必须立即简化**

### 具体场景评估

| 场景 | 过度设计现象 | 简化建议 | 优先级 |
|------|-------------|---------|--------|
| 条件判断 | 多层嵌套 if-else | 使用 early return 扁平化 | ⭐⭐⭐⭐⭐ |
| 工具方法 | 为简单操作创建工厂+策略 | 直接写函数调用 | ⭐⭐⭐⭐⭐ |
| 数据转换 | 自定义 Mapper/Converter 框架 | 使用标准库或直接转换 | ⭐⭐⭐⭐ |
| 配置加载 | 多层抽象 + 插件机制 | 直接读取配置文件 | ⭐⭐⭐⭐ |
| 事件通知 | 自建事件总线 | 直接方法调用 | ⭐⭐⭐ |
| 字符串处理 | 自定义 Formatter 接口体系 | 使用语言内置格式化 | ⭐⭐⭐ |

---

## 第2步: 过度设计识别

### 方法复杂度度量

```
检查每个方法：

圈复杂度（Cyclomatic Complexity）:
  □ 1-5   → 简单，可以接受
  □ 6-10  → 中等，考虑拆分
  □ 11+   → 过于复杂，必须重构

行数检查：
  □ 1-10 行  → 理想状态
  □ 11-20 行 → 可以接受
  □ 21-50 行 → 应该拆分
  □ 50+ 行   → 必须立即拆分

参数数量：
  □ 0-2 个 → 理想
  □ 3-4 个 → 可接受，考虑使用对象封装
  □ 5+ 个  → 必须重构
```

### 抽象必要性检查

对项目中的每一个抽象层，回答以下问题：

```
□ 这个接口是否有超过一个实现？
  → 如果只有一个实现且未来不太可能扩展，直接用类即可

□ 这个工厂类是否只创建一种对象？
  → 如果是，直接 new 即可

□ 这个策略模式是否只有一种策略？
  → 如果是，直接写逻辑即可

□ 这个包装器是否只是透传调用？
  → 如果是，去掉包装器直接调用
```

### 设计模式必要性检查

| 模式 | 必要时机 | 不必要时机 |
|------|---------|-----------|
| 工厂模式 | 创建逻辑复杂、需要多种产品 | 只有一种产品且构造简单 |
| 策略模式 | 运行时需切换多种算法 | 只有一种固定算法 |
| 观察者模式 | 多个独立模块需要响应事件 | 只有一个接收者 |
| 装饰器模式 | 需要动态组合多种行为 | 行为固定不变 |
| 建造者模式 | 参数多且有可选参数 | 参数少于 3 个 |

### YAGNI 交叉检查

```
对每个"未来可能需要"的设计，问自己：

□ 现在是否有明确的需求需要这个设计？
□ 如果没有这个设计，现在的代码能正常工作吗？
□ 如果未来真的需要，重构的成本是否可接受？

如果三个答案都是"否、是、是"，那就删除这个设计。
```

---

## 第3步: 简化规划

### 3.1 扁平化条件判断

**Java 示例**:

```java
// ❌ 过度嵌套
public String processOrder(Order order) {
    if (order != null) {
        if (order.isValid()) {
            if (order.hasItems()) {
                if (order.getPayment() != null) {
                    if (order.getPayment().isConfirmed()) {
                        return "处理成功";
                    } else {
                        return "支付未确认";
                    }
                } else {
                    return "缺少支付信息";
                }
            } else {
                return "订单无商品";
            }
        } else {
            return "订单无效";
        }
    } else {
        return "订单为空";
    }
}

// ✅ 使用 early return 扁平化
public String processOrder(Order order) {
    if (order == null) return "订单为空";
    if (!order.isValid()) return "订单无效";
    if (!order.hasItems()) return "订单无商品";
    if (order.getPayment() == null) return "缺少支付信息";
    if (!order.getPayment().isConfirmed()) return "支付未确认";
    return "处理成功";
}
```

**Python 示例**:

```python
# ❌ 过度嵌套
def process_order(order):
    if order is not None:
        if order.is_valid():
            if order.has_items():
                if order.payment is not None:
                    if order.payment.is_confirmed():
                        return "处理成功"
                    else:
                        return "支付未确认"
                else:
                    return "缺少支付信息"
            else:
                return "订单无商品"
        else:
            return "订单无效"
    else:
        return "订单为空"

# ✅ 使用 early return 扁平化
def process_order(order):
    if order is None:
        return "订单为空"
    if not order.is_valid():
        return "订单无效"
    if not order.has_items():
        return "订单无商品"
    if order.payment is None:
        return "缺少支付信息"
    if not order.payment.is_confirmed():
        return "支付未确认"
    return "处理成功"
```

### 3.2 提取方法

```typescript
// ❌ 一个方法做太多事
function handleUserRegistration(data: any): string {
    // 验证邮箱
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        return "邮箱格式错误";
    }
    // 验证密码
    if (data.password.length < 8) {
        return "密码太短";
    }
    if (!/[A-Z]/.test(data.password)) {
        return "密码需要包含大写字母";
    }
    if (!/[0-9]/.test(data.password)) {
        return "密码需要包含数字";
    }
    // 验证用户名
    if (data.username.length < 3 || data.username.length > 20) {
        return "用户名长度需在3-20之间";
    }
    // 保存用户...
    return "注册成功";
}

// ✅ 提取独立方法
function validateEmail(email: string): string | null {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email) ? null : "邮箱格式错误";
}

function validatePassword(password: string): string | null {
    if (password.length < 8) return "密码太短";
    if (!/[A-Z]/.test(password)) return "密码需要包含大写字母";
    if (!/[0-9]/.test(password)) return "密码需要包含数字";
    return null;
}

function validateUsername(username: string): string | null {
    if (username.length < 3 || username.length > 20) {
        return "用户名长度需在3-20之间";
    }
    return null;
}

function handleUserRegistration(data: any): string {
    const emailError = validateEmail(data.email);
    if (emailError) return emailError;

    const passwordError = validatePassword(data.password);
    if (passwordError) return passwordError;

    const usernameError = validateUsername(data.username);
    if (usernameError) return usernameError;

    // 保存用户...
    return "注册成功";
}
```

### 3.3 移除不必要的抽象

```java
// ❌ 不必要的接口 + 工厂 + 实现
public interface StringFormatter {
    String format(String input);
}

public class UpperCaseFormatter implements StringFormatter {
    @Override
    public String format(String input) {
        return input.toUpperCase();
    }
}

public class StringFormatterFactory {
    public static StringFormatter create(String type) {
        if ("upper".equals(type)) {
            return new UpperCaseFormatter();
        }
        throw new IllegalArgumentException("Unknown type: " + type);
    }
}

// 使用
StringFormatter formatter = StringFormatterFactory.create("upper");
String result = formatter.format("hello");

// ✅ 直接调用标准库
String result = "hello".toUpperCase();
```

### 3.4 使用标准库

```python
# ❌ 自己实现排序
def custom_sort(items):
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] > items[j]:
                items[i], items[j] = items[j], items[i]
    return items

# ✅ 使用标准库
sorted_items = sorted(items)
```

### 3.5 简化 API

```typescript
// ❌ 过度复杂的 API
interface QueryBuilder<T> {
    select(fields: string[]): QueryBuilder<T>;
    where(condition: Condition): QueryBuilder<T>;
    orderBy(field: string, direction: "asc" | "desc"): QueryBuilder<T>;
    limit(n: number): QueryBuilder<T>;
    offset(n: number): QueryBuilder<T>;
    build(): Query<T>;
    execute(): Promise<T[]>;
}

// 只是为了查一个用户
const user = await new QueryBuilderImpl<User>()
    .select(["*"])
    .where(new EqualCondition("id", userId))
    .limit(1)
    .build()
    .execute();

// ✅ 简单直接的 API
async function findUserById(userId: string): Promise<User | null> {
    return db.query("SELECT * FROM users WHERE id = ?", [userId]);
}

const user = await findUserById(userId);
```

---

## 第4步: 测试计划

### 简化后的测试策略

```
□ 单元测试覆盖所有提取出的小方法
□ 确保简化前后的输入/输出行为一致
□ 边界条件测试（null、空字符串、极端值）
□ 异常路径测试
□ 性能对比测试（确认简化未引入性能问题）
```

### 测试示例

```java
// 针对简化后的 processOrder 方法
@Test
void processOrder_nullOrder_returnsError() {
    assertEquals("订单为空", processOrder(null));
}

@Test
void processOrder_invalidOrder_returnsError() {
    Order order = new Order();
    order.setValid(false);
    assertEquals("订单无效", processOrder(order));
}

@Test
void processOrder_validOrder_returnsSuccess() {
    Order order = createValidOrder();
    assertEquals("处理成功", processOrder(order));
}
```

```python
# 针对简化后的 process_order 方法
def test_process_order_none():
    assert process_order(None) == "订单为空"

def test_process_order_invalid():
    order = Order(is_valid=False)
    assert process_order(order) == "订单无效"

def test_process_order_success():
    order = create_valid_order()
    assert process_order(order) == "处理成功"
```

```typescript
// 针对提取出的验证方法
describe("validateEmail", () => {
    it("should return null for valid email", () => {
        expect(validateEmail("user@example.com")).toBeNull();
    });

    it("should return error for invalid email", () => {
        expect(validateEmail("invalid")).toBe("邮箱格式错误");
    });
});

describe("validatePassword", () => {
    it("should return null for strong password", () => {
        expect(validatePassword("MyPass123")).toBeNull();
    });

    it("should return error for short password", () => {
        expect(validatePassword("short")).toBe("密码太短");
    });
});
```

---

## 第5步: 代码审查指南

### 审查检查项

```
在代码审查中关注以下问题：

□ 这段代码能否用更少的代码实现同样的功能？
□ 新引入的抽象是否有明确的、当前的需求？
□ 是否可以用标准库替代自定义实现？
□ 方法名是否清晰表达了意图？
□ 是否存在"以防万一"的代码？
□ 条件逻辑是否可以简化？
□ 是否存在只有一个实现的接口？
□ 类的职责是否单一且清晰？
```

### 审查回复模板

```
当发现过度设计时，使用以下模板回复：

"这里的 [具体设计] 增加了不必要的复杂度。
当前只有 [X] 种情况，建议简化为 [具体方案]。
如果未来确实需要扩展，重构成本约为 [评估]。"
```

### 审查中的权衡判断

| 场景 | 保持现状 | 简化 |
|------|---------|------|
| 接口只有一个实现 | 明确计划在近期添加第二个实现 | 没有明确计划 |
| 方法较长但逻辑清晰 | 拆分后反而更难理解 | 可以拆成独立可测试的单元 |
| 使用设计模式 | 确实解决了当前的具体问题 | 只是"以防万一" |
| 泛型设计 | 已有多处复用 | 只在一处使用 |

---

## 常见陷阱预防

### 陷阱1: 混淆"简单"与"简陋"

```java
// ❌ 简陋：忽略了必要的错误处理
public User findUser(Long id) {
    return userRepository.findById(id);  // 可能返回 null，未处理
}

// ✅ 简单但健壮：保留必要的错误处理
public User findUser(Long id) {
    User user = userRepository.findById(id);
    if (user == null) {
        throw new UserNotFoundException("用户不存在: " + id);
    }
    return user;
}
```

### 陷阱2: 删除必要的抽象

```python
# ❌ 过度简化：去掉了必要的数据库抽象
def get_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # 返回原始元组，调用方需要知道列顺序

# ✅ 保留必要的抽象
def get_user(user_id) -> User | None:
    """通过 ID 查找用户，返回 User 对象或 None。"""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return User(**row) if row else None
```

### 陷阱3: 过度简化错误处理

```typescript
// ❌ 过度简化：吞掉了所有错误
async function fetchData(url: string): Promise<any> {
    try {
        const res = await fetch(url);
        return await res.json();
    } catch {
        return null;  // 调用方无法知道发生了什么
    }
}

// ✅ 简单但保留错误信息
async function fetchData(url: string): Promise<any> {
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`请求失败: ${res.status} ${res.statusText}`);
    }
    return await res.json();
}
```

---

## 重构检查表

### 重构前确认

```
□ 已识别出需要简化的具体代码位置
□ 已理解当前代码的完整行为（包括边界情况）
□ 已有足够的测试覆盖（如果没有，先补测试）
□ 已确认简化不会删除必要的错误处理
□ 已确认简化不会破坏必要的抽象边界
```

### 重构执行

```
□ 每次只简化一个地方
□ 每次简化后运行全部测试
□ 使用版本控制，每次简化单独提交
□ 简化后检查：代码是否更容易理解了？
□ 简化后检查：新人能否快速理解这段代码？
```

### 重构后验证

```
□ 所有测试通过
□ 代码行数减少或持平（在不牺牲可读性的前提下）
□ 圈复杂度降低
□ 嵌套层级减少
□ 类/接口数量合理（没有只有一个实现的接口）
□ 代码审查通过
□ 团队成员认为更容易理解
```

### 简化效果度量

| 指标 | 简化前 | 简化后 | 改善 |
|------|-------|-------|------|
| 代码行数 | ___ | ___ | ___% |
| 圈复杂度 | ___ | ___ | ___% |
| 最大嵌套深度 | ___ | ___ | ___ 层 |
| 类/接口数量 | ___ | ___ | ___ 个 |
| 方法平均行数 | ___ | ___ | ___ 行 |
| 测试覆盖率 | ___% | ___% | ___% |
