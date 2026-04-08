# 里氏替换原则 - 诊断与规划表

## 第1步: 需求诊断 - 你的继承体系是否违反 LSP？

### 🔍 快速检查清单

```
□ 代码中存在 instanceof / typeof 检查来区分子类行为
□ 子类方法抛出父类未声明的异常
□ 子类方法是空实现（什么都不做）
□ 替换子类后程序行为不符合预期
□ 子类加强了方法的前置条件（要求更严格的输入）
□ 子类削弱了方法的后置条件（返回更弱的保证）
□ 子类修改了父类的不变量（invariants）
□ 存在"正方形继承矩形"类型的建模错误
```

**诊断标准**:
- ✅ 0-1 项 → **很好，继承体系符合 LSP**
- ⚠️ 2-4 项 → **应该审查继承层次设计**
- ❌ 5 项以上 → **必须重构继承体系**

### 🎯 具体场景评估

| 场景 | 违反现象 | 建议 | 优先级 |
|------|---------|------|--------|
| instanceof 泛滥 | 根据子类类型执行不同逻辑 | 使用多态或接口替代 | ⭐⭐⭐⭐⭐ |
| 空方法实现 | 子类覆写方法体为空 | 重新划分接口，使用 ISP | ⭐⭐⭐⭐⭐ |
| 意外异常 | 子类抛出 UnsupportedOperationException | 拆分接口，移除不适用的行为 | ⭐⭐⭐⭐ |
| 前置条件加强 | 子类要求更严格的参数 | 维持或放松父类前置条件 | ⭐⭐⭐⭐ |
| 后置条件削弱 | 子类返回值不满足父类约定 | 维持或加强父类后置条件 | ⭐⭐⭐⭐ |
| 不变量破坏 | 子类修改了父类建立的约束 | 改用组合而非继承 | ⭐⭐⭐⭐⭐ |

---

## 第2步: 继承层次审计

### 审计当前继承层次

```
对每个继承关系，验证 "IS-A" 的行为正确性：

继承关系 1：
  父类：____________
  子类：____________
  □ 子类能替换父类出现在所有使用场景中？  是 / 否
  □ 子类保持了父类所有方法的契约？        是 / 否
  □ 是否有客户端代码检查具体子类类型？     是 / 否

继承关系 2：
  父类：____________
  子类：____________
  □ 子类能替换父类出现在所有使用场景中？  是 / 否
  □ 子类保持了父类所有方法的契约？        是 / 否
  □ 是否有客户端代码检查具体子类类型？     是 / 否
```

### IS-A 关系行为验证矩阵

```
对于父类 P 和子类 S，逐项验证：

方法级验证：
┌──────────────────┬──────────┬───────────┬──────────┐
│ 父类方法         │ 子类实现 │ 行为兼容？ │ 备注     │
├──────────────────┼──────────┼───────────┼──────────┤
│                  │          │ 是 / 否   │          │
│                  │          │ 是 / 否   │          │
│                  │          │ 是 / 否   │          │
└──────────────────┴──────────┴───────────┴──────────┘

契约验证：
  前置条件：子类 ≤ 父类？（不能更严格）  是 / 否
  后置条件：子类 ≥ 父类？（不能更宽松）  是 / 否
  不变量：子类维持？                      是 / 否
```

---

## 第3步: 契约验证

### 契约定义模板

```java
// 为每个父类方法定义明确的契约

/**
 * @pre  前置条件描述（参数的合法范围）
 * @post 后置条件描述（返回值的保证）
 * @invariant 不变量描述（始终为真的条件）
 * @throws 声明可能抛出的异常
 */
```

### 契约验证检查表

```
方法：____________

前置条件检查：
  □ 父类前置条件：____________
  □ 子类前置条件：____________
  □ 子类是否放松或保持？  是（✅）/ 否（❌）

后置条件检查：
  □ 父类后置条件：____________
  □ 子类后置条件：____________
  □ 子类是否加强或保持？  是（✅）/ 否（❌）

异常检查：
  □ 父类声明异常：____________
  □ 子类抛出异常：____________
  □ 子类异常是否为父类异常的子集？  是（✅）/ 否（❌）
```

---

## 第4步: 行为兼容性测试

### 测试策略

```
对于每个子类 S 替换父类 P 的场景：

测试 1：基础替换测试
  □ 用子类实例替换所有父类引用
  □ 运行完整测试套件
  □ 结果：全部通过？  是 / 否

测试 2：前置条件边界测试
  □ 使用父类允许的最宽松输入
  □ 子类是否同样接受？  是 / 否
  □ 子类是否产生相同类型的输出？  是 / 否

测试 3：后置条件验证测试
  □ 调用方法后检查返回值范围
  □ 子类返回值是否在父类承诺的范围内？  是 / 否

测试 4：异常行为测试
  □ 子类是否抛出父类未声明的异常？  是 / 否
  □ 子类是否在不该成功时成功？  是 / 否
```

### 行为兼容性测试代码模板

```java
// Java - LSP 行为兼容性测试
public class LspComplianceTest {

    // 针对父类契约编写测试，用所有子类运行
    @ParameterizedTest
    @MethodSource("provideAllSubtypes")
    void shouldMaintainBaseContract(ParentType instance) {
        // 前置条件：父类允许的输入
        var input = createValidInput();

        // 执行
        var result = instance.doSomething(input);

        // 后置条件：必须满足父类的承诺
        assertNotNull(result);
        assertTrue(result.isValid());
    }

    static Stream<ParentType> provideAllSubtypes() {
        return Stream.of(
            new SubTypeA(),
            new SubTypeB(),
            new SubTypeC()
        );
    }
}
```

```python
# Python - LSP 行为兼容性测试
import pytest

class TestLspCompliance:
    """针对父类契约编写测试，用所有子类运行"""

    @pytest.fixture(params=[SubTypeA, SubTypeB, SubTypeC])
    def instance(self, request):
        return request.param()

    def test_should_maintain_base_contract(self, instance):
        # 前置条件：父类允许的输入
        valid_input = create_valid_input()

        # 执行
        result = instance.do_something(valid_input)

        # 后置条件：必须满足父类的承诺
        assert result is not None
        assert result.is_valid()

    def test_should_not_throw_unexpected_exception(self, instance):
        valid_input = create_valid_input()
        # 不应抛出父类未声明的异常
        result = instance.do_something(valid_input)
        assert result is not None
```

```typescript
// TypeScript - LSP 行为兼容性测试
describe('LSP Compliance', () => {
    const subtypes: ParentType[] = [
        new SubTypeA(),
        new SubTypeB(),
        new SubTypeC(),
    ];

    subtypes.forEach((instance) => {
        describe(`${instance.constructor.name}`, () => {
            it('should maintain base contract', () => {
                const input = createValidInput();
                const result = instance.doSomething(input);

                expect(result).toBeDefined();
                expect(result.isValid()).toBe(true);
            });

            it('should not throw unexpected exceptions', () => {
                const input = createValidInput();
                expect(() => instance.doSomething(input)).not.toThrow();
            });
        });
    });
});
```

---

## 第5步: 重新设计规划

### 违反 LSP 时的重构策略

```
策略选择：

□ 策略 A：提取接口
  适用：子类只需要父类的部分行为
  做法：将行为拆分为多个小接口
  示例：Bird 接口拆分为 Flyable + Swimmable

□ 策略 B：改用组合
  适用：IS-A 关系不成立
  做法：将继承改为组合 + 委托
  示例：Square 不继承 Rectangle，而是各自实现 Shape

□ 策略 C：引入抽象基类
  适用：需要共享部分实现
  做法：将共享行为提取到抽象基类
  示例：抽取 AbstractAccount 共享余额管理

□ 策略 D：重新建模
  适用：继承层次根本设计错误
  做法：从头设计类型层次
  示例：用 ReadableAccount + WithdrawableAccount 替代单一 Account 层次
```

### 重构计划模板

```
重构目标：____________
当前问题：____________

步骤 1：识别违反点
  □ 违反位置：____________
  □ 违反类型：____________（instanceof / 空实现 / 异常 / 契约破坏）

步骤 2：选择重构策略
  □ 选用策略：____________
  □ 理由：____________

步骤 3：设计新结构
  □ 新接口/基类定义：____________
  □ 新的类型层次图：____________

步骤 4：实施重构
  □ 创建新接口/基类
  □ 修改子类实现
  □ 更新客户端代码
  □ 运行 LSP 合规测试

步骤 5：验证
  □ 所有子类可替换测试通过
  □ 无 instanceof 检查
  □ 无空实现
  □ 无意外异常
```

---

## 5 个常见陷阱

### 陷阱 1：正方形继承矩形

```java
// ❌ 经典错误
class Rectangle {
    protected int width, height;

    void setWidth(int w) { this.width = w; }
    void setHeight(int h) { this.height = h; }
    int getArea() { return width * height; }
}

class Square extends Rectangle {
    // 违反 LSP：修改了 setWidth/setHeight 的独立性
    @Override
    void setWidth(int w) { this.width = w; this.height = w; }
    @Override
    void setHeight(int h) { this.width = h; this.height = h; }
}

// 客户端代码在用 Square 替换 Rectangle 时行为异常
void resize(Rectangle r) {
    r.setWidth(5);
    r.setHeight(10);
    assert r.getArea() == 50; // Square 时失败！返回 100
}
```

**解决方案**: 让 Rectangle 和 Square 各自实现 Shape 接口。

---

### 陷阱 2：不能飞的鸟继承了飞行行为

```python
# ❌ 企鹅不会飞
class Bird:
    def fly(self):
        print("飞翔中...")
    def eat(self):
        print("进食中...")

class Penguin(Bird):
    def fly(self):
        raise UnsupportedError("企鹅不会飞")  # 违反 LSP
```

**解决方案**: 拆分为 Bird 基类 + Flyable 接口，Penguin 不实现 Flyable。

---

### 陷阱 3：子类加强前置条件

```typescript
// ❌ 子类要求更严格的输入
class Logger {
    log(message: string): void {
        console.log(message);
    }
}

class FileLogger extends Logger {
    log(message: string): void {
        if (message.length > 1000) {
            throw new Error("消息太长"); // 父类没有这个限制！
        }
        // 写入文件...
    }
}
```

**解决方案**: FileLogger 应接受任意长度消息，内部做截断或分段写入。

---

### 陷阱 4：子类削弱后置条件

```java
// ❌ 子类返回值不满足父类承诺
class Collection {
    /** @return 排好序的列表，永不为 null */
    List<String> getSorted() {
        List<String> list = new ArrayList<>(items);
        Collections.sort(list);
        return list;
    }
}

class LazyCollection extends Collection {
    @Override
    List<String> getSorted() {
        return items; // ❌ 未排序！违反后置条件
    }
}
```

**解决方案**: 子类必须保证返回排好序的列表。

---

### 陷阱 5：基于 instanceof 的类型判断

```python
# ❌ 用 isinstance 区分子类行为
def calculate_shipping(product):
    if isinstance(product, DigitalProduct):
        return 0  # 数字产品不需要运费
    elif isinstance(product, FragileProduct):
        return product.weight * 2.0  # 易碎品加价
    elif isinstance(product, HeavyProduct):
        return product.weight * 1.5
    else:
        return product.weight * 1.0
```

**解决方案**: 让每个 Product 子类实现 `calculate_shipping()` 方法，利用多态消除 isinstance。

```python
# ✅ 多态替代 isinstance
class Product:
    def calculate_shipping(self) -> float:
        return self.weight * 1.0

class DigitalProduct(Product):
    def calculate_shipping(self) -> float:
        return 0

class FragileProduct(Product):
    def calculate_shipping(self) -> float:
        return self.weight * 2.0
```

---

## 决策速查表

| 问题 | 答案 | 行动 |
|------|------|------|
| 子类能完全替代父类吗？ | 否 | 改用组合或接口 |
| 存在 instanceof 检查？ | 是 | 用多态替代 |
| 子类有空方法实现？ | 是 | 拆分接口 (ISP) |
| 子类抛出意外异常？ | 是 | 重新设计层次 |
| 前置条件加强了？ | 是 | 放松子类前置条件 |
| 后置条件削弱了？ | 是 | 加强子类后置条件 |
| IS-A 关系成立吗？ | 否 | 改用 HAS-A 组合 |
