# Template Method - 诊断与规划表

## 第1步: 需求诊断 - 你真的需要Template Method吗？

### 🔍 快速检查清单

```
□ 多个类有相同的算法框架，只是某些步骤不同
□ 想复用稳定的算法框架，而不是复制代码
□ 算法有明确的"骨架"和"变化点"
□ 需要规范某类操作的执行顺序和流程
□ 用继承比用组合更合理（算法抽象）
□ 需要子类能选择性地定制特定步骤
□ 父类需要控制流程，子类不能打破流程
```

**诊断标准**:
- ✅ 勾选 5 项以上 → **强烈推荐使用**
- ⚠️ 勾选 3-4 项 → **可以使用**
- ❌ 勾选 2 项以下 → **考虑用Strategy替代**

**对比选择**:
| 情况 | Template Method | Strategy |
|------|----------------|----------|
| 算法是类的核心逻辑 | ✅ 优先 | - |
| 需要客户端动态选择算法 | - | ✅ 优先 |
| 多层继承关系 | ✅ 自然 | ⚠️ 平铺 |
| 需要复用框架 | ✅ 内置 | - |

---

## 第2步: 实现方法选择

### 方法对比矩阵

| 方法 | 复杂度 | 灵活性 | 适用场景 | 性能 |
|------|--------|--------|---------|------|
| **虚方法** | ⭐ 低 | ⭐ 低 | 简单算法，子类明确 | ⭐⭐⭐⭐⭐ |
| **钩子方法** | ⭐⭐ 中 | ⭐⭐ 中 | 多个可选步骤 | ⭐⭐⭐⭐ |
| **回调** | ⭐⭐ 中 | ⭐⭐⭐ 高 | 函数式、Lambda组合 | ⭐⭐⭐⭐ |
| **参数化** | ⭐⭐⭐ 高 | ⭐⭐⭐ 高 | 运行时流程定制 | ⭐⭐⭐ |
| **混合策略** | ⭐⭐⭐ 高 | ⭐⭐⭐⭐ 极高 | 复杂、多维变化 | ⭐⭐⭐ |

**如何选择**:
1. 简单情况(1-2个变化点) → **虚方法**
2. 多个可选步骤 → **钩子方法**
3. 需要函数式编程 → **回调**
4. 框架需要动态配置 → **参数化**
5. 多维度变化 → **混合策略**

---

## 第3步: 算法骨架规划

### 算法步骤分析表

填写此表格定义你的Template Method：

```
算法名称: _______________
目的: _______________
输入参数: _______________
输出结果: _______________

步骤     | 固定? | 实现方式 | 说明
---------|--------|---------|--------
Step 1   | ☐是 ☐否 | 虚/钩 | 
Step 2   | ☐是 ☐否 | 虚/钩 | 
Step 3   | ☐是 ☐否 | 虚/钩 | 
Step 4   | ☐是 ☐否 | 虚/钩 | 
```

### 可变部分识别矩阵

对于每个"可变部分"，填写此表：

```
可变点  | 哪些子类不同？ | 变化原因 | 参数化? | 
--------|-------------|---------|---------|
变化1   | ClassA...B  | 原因     | Y/N     |
变化2   | ClassX...Y  | 原因     | Y/N     |
```

### 抽象类设计决策树

```
你的算法是否有多个维度的变化？
├─ 是 → 考虑参数化 + 回调组合
└─ 否 → 虚方法足够

算法步骤数量？
├─ 1-2个 → 虚方法  
├─ 3-5个 → 钩子方法
└─ 6个以上 → 分割为多个Template

是否需要动态调整流程？
├─ 是 → 参数化 Template
└─ 否 → 标准虚方法
```

---

## 第4步: 实现规划

### 虚方法规划

```java
// 1. 定义抽象类
public abstract class Algorithm {
    // 2. 定义模板方法（final防止覆盖）
    public final void execute() {
        step1();
        step2();
        step3();
    }
    
    // 3. 定义虚方法
    protected abstract void step1();
    protected abstract void step2();
    protected abstract void step3();
}

// 4. 实现具体类
public class ConcreteAlgorithmA extends Algorithm {
    @Override
    protected void step1() { /* A的实现 */ }
    @Override
    protected void step2() { /* A的实现 */ }
    @Override
    protected void step3() { /* A的实现 */ }
}
```

### 钩子方法规划

```java
public abstract class Algorithm {
    public final void execute() {
        step1();
        if (needsStep2()) {  // 钩子
            step2();
        }
        step3();
    }
    
    protected abstract void step1();
    protected void step2() { } // 可选
    protected abstract void step3();
    
    // 默认钩子
    protected boolean needsStep2() {
        return true;
    }
}
```

### 回调函数规划

```java
public class ProcedureTemplate {
    private Consumer<Context> step1;
    private Consumer<Context> step2;
    
    public void execute(Context ctx) {
        if (step1 != null) step1.accept(ctx);
        if (step2 != null) step2.accept(ctx);
    }
}

// 使用
new ProcedureTemplate()
    .onStep1(ctx -> { ... })
    .onStep2(ctx -> { ... })
    .execute(context);
```

---

## 第5步: 测试计划

### 单元测试

```
□ 模板方法按正确顺序调用虚方法
□ 虚方法被正确覆盖
□ 钩子方法的默认行为正确
□ 子类覆盖后行为正确改变
□ 异常处理：某步抛异常，流程中断
□ 性能：无多余函数调用开销
□ 参数传递：参数正确流转各步骤
```

### 集成测试

```
□ Template与具体子类协作正确
□ 多个子类之间不互相影响
□ 框架级别的流程整合测试
□ 并发执行：多线程安全性
□ 大量数据：性能是否退化
```

### 测试代码示例

```java
@Test
public void testTemplateMethodCallOrder() {
    List<Integer> callOrder = new ArrayList<>();
    Algorithm algo = new Algorithm() {
        @Override
        protected void step1() { callOrder.add(1); }
        @Override
        protected void step2() { callOrder.add(2); }
        @Override
        protected void step3() { callOrder.add(3); }
    };
    
    algo.execute();
    
    assertEquals(Arrays.asList(1, 2, 3), callOrder);
}

@Test
public void testHookMethod() {
    Algorithm algo = new Algorithm() {
        @Override
        protected void step1() { }
        @Override
        protected void step2() { }
        @Override
        protected void step3() { }
        @Override
        protected boolean needsStep2() { return false; }
    };
    
    List<Integer> executed = new ArrayList<>();
    algo.execute();  // step2应该被跳过
}
```

---

## 第6步: 代码审查清单

### 设计审查

- [ ] 抽象类的步骤划分清晰（不超过6个虚方法）
- [ ] 虚方法职责单一，不承载业务逻辑
- [ ] 钩子方法的默认行为合理
- [ ] 模板方法被标记为final
- [ ] 虚方法被标记为protected/abstract
- [ ] 框架与具体实现清晰分离
- [ ] 继承链不超过2-3层

### 实现审查

- [ ] 所有虚方法都在子类中实现
- [ ] 没有在虚方法中调用虚方法（避免双重分派混乱）
- [ ] 参数正确传递到每个虚方法
- [ ] 异常处理适当放在模板或子类
- [ ] 没有过度使用钩子方法（超过3个）
- [ ] 子类代码无明显冗余

### 性能审查

- [ ] 虚方法调用链长度合理（不超过10层）
- [ ] 没有创建过多临时对象
- [ ] 递归深度可控
- [ ] 缓存机制若有，与Template不冲突

---

## 常见陷阱预防

### ⚠️ 陷阱1: 钩子方法过多导致理解困难

**症状**: 模板方法有7个以上虚方法/钩子，导致子类实现混乱

**预防**:
```java
// ❌ 问题做法：太多虚方法
public abstract void step1();
public abstract void step2();
public abstract void step3();
public abstract void step4();
public abstract void step5();
public abstract void step6();
public abstract void step7();

// ✅ 解决方案：分组聚合
// 分为3个逻辑阶段，每阶段1-2个虚方法
public final void execute() {
    initPhase();      // 初始化阶段
    processPhase();   // 处理阶段
    finalizePhase();  // 收尾阶段
}

protected abstract void initPhase();
protected abstract void processPhase();
protected abstract void finalizePhase();
```

### ⚠️ 陷阱2: 子类不知道调用父类虚方法

**症状**: 子类覆盖虚方法后，完全遗漏了super.step()的调用

**预防**:
```java
// ❌ 常见错误
public class ConcreteA extends Algorithm {
    @Override
    protected void step2() {
        // 忘记调用 super.step2()
        // 导致一些初始化工作被遗漏
        doCustomWork();
    }
}

// ✅ 解决方案1：文档明确说明
/**
 * 实现此方法时，需要调用super.step2()
 */
protected void step2() {
    initResources();
}

// ✅ 解决方案2：分离可选部分
public class Algorithm {
    public final void execute() {
        step1();
        customizeStep2();  // 允许完全覆盖
        step3();
    }
    
    protected void customizeStep2() {
        // 默认实现
    }
}
```

### ⚠️ 陷阱3: 流程变更导致所有子类改动

**症状**: 添加新步骤或改变步骤顺序，导致所有子类都要改

**预防**:
```java
// ❌ 容易变动的设计
public final void process() {
    readInput();   // 将来要改？
    transform();   // 将来要改？
    writeOutput(); // 新增？
}

// ✅ 解决方案：参数化流程
public class ProcessingPipeline {
    private List<Step> steps = new ArrayList<>();
    
    public ProcessingPipeline add(Step step) {
        this.steps.add(step);
        return this;
    }
    
    public void execute(Context ctx) {
        for (Step step : steps) {
            step.execute(ctx);
        }
    }
}

// 使用
ProcessingPipeline pipeline = new ProcessingPipeline()
    .add(new ReadStep())
    .add(new TransformStep())
    .add(new WriteStep());  // 易于添加新步骤
```

### ⚠️ 陷阱4: 虚方法中包含太多业务逻辑

**症状**: 虚方法变成了"小型模板方法"，导致协调困难

**预防**:
```java
// ❌ 问题做法：虚方法太复杂
protected abstract void processData() {
    // 包含条件分支、循环、异常处理等复杂逻辑
}

// ✅ 解决方案：分离顾虑
protected abstract DataProcessor createProcessor();

protected final void processData() {
    DataProcessor processor = createProcessor();
    processor.process(data);  // 业务逻辑放在具体类
}
```

---

## 快速参考

### 模板方法最小实现

```java
// 步骤1: 定义模板
public abstract class Algorithm {
    public final void execute() {
        step1();
        step2();
    }
    
    protected abstract void step1();
    protected abstract void step2();
}

// 步骤2: 实现具体算法
public class AlgorithmA extends Algorithm {
    @Override
    protected void step1() { System.out.println("A: step1"); }
    
    @Override
    protected void step2() { System.out.println("A: step2"); }
}

// 步骤3: 使用
Algorithm algo = new AlgorithmA();
algo.execute();
```

### 决策速查表

**我应该使用Template Method吗？**

| 条件 | 答案 |
|------|------|
| "我有80%相同的代码，20%需要定制" | ✅ YES |
| "我需要规范操作顺序" | ✅ YES |
| "算法是继承关系的主角" | ✅ YES |
| "我想在运行时切换算法" | ❌ Use Strategy |
| "只有1-2个类实现" | ⚠️ 可能过度设计 |
| "算法完全不同没有共同点" | ❌ Don't use |



| 步骤 | 用途 | 可变性 | 实现方式 | 优先级 |
|------|------|--------|---------|--------|
| 预处理 | 数据准备 | 高 | 虚方法 | P0 |
| 验证 | 数据检查 | 中 | 回调 | P0 |
| 转换 | 主逻辑 | 高 | 虚方法 | P1 |
| 聚合 | 结果处理 | 中 | 虚方法 | P1 |
| 后处理 | 清理 | 低 | 钩子 | P2 |
| 错误处理 | 异常捕获 | 高 | 策略 | P0 |

**模板**:
1. 新算法:
   - 步骤名: _______________
   - 用途: _______________
   - 可变性: __/10
   - 建议实现: _______________

---

## 可变部分识别矩阵

判断第N部分是"固定"还是"可变":

| 部分 | 固定 | 可变 | 跨文件 | 文档 |
|------|------|------|--------|------|
| 读取 | ✅ | - | 是 | 输入格式 |
| 验证 | - | ✅ | 否 | 规则集 |
| 处理 | - | ✅ | 是 | 算法 |
| 存储 | - | ✅ | 是 | 输出格式 |
| 日志 | ✅ | △ | 是 | 级别 |

**评分指南**:
- ✅ 固定: 所有实现相同 (0%变异)
- △ 半固定: 90%相同，可参数化 (标准化钩子)
- ❌ 可变: 实现差异大 (3+版本存在)

---

## 钩子方法规划表

为模板方法设计适当的钩子:

```
模板方法名: process()

┌─ 强制步骤 (必须实现)
│  ├─ step1() - 子类必须覆盖
│  ├─ step2() - 子类必须覆盖
│
├─ 可选钩子 (子类可覆盖)
│  ├─ onBeforeStep1() {}  // 默认空实现
│  ├─ onAfterStep2() {}   // 默认空实现
│
└─ 配置钩子 (子类提供参数)
   ├─ getTimeout(): int
   ├─ getRetryCount(): int
```

**规划步骤**:
1. 识别不变部分 → 强制步骤
2. 识别可变部分 → 虚方法
3. 添加切入点 → 钩子方法
4. 验证灵活性 → 子类覆盖检查

---

## 代码审查清单

实现审查时检查:

### 设计审查

- [ ] 模板方法标记为 final (防止子类修改流程)
- [ ] 虚方法标记为 protected abstract (明确意图)
- [ ] 钩子方法有默认实现 (允许子类可选覆盖)
- [ ] 只有1个模板方法 (复杂度控制)
- [ ] 步骤数 ≤ 7 (认知负荷)

### 实现审查

- [ ] 所有虚方法都被实现 (编译检查)
- [ ] 无死代码路径 (覆盖分析)
- [ ] 参数传递一致 (类型检查)
- [ ] 异常处理完整 (错误路径)
- [ ] 子类逻辑不重复 (代码重复度 < 10%)

### 测试审查

- [ ] 单元测试:虚方法独立测试
- [ ] 集成测试:模板+子类组合
- [ ] 边界测试:空数据/异常
- [ ] 性能测试:基准对比

### 文档审查

- [ ] 模板方法文档清晰 (说明每个步骤)
- [ ] 虚方法文档完整 (契约明确)
- [ ] 子类实现示例提供 (使用指南)

---

## 常见陷阱预防

### 陷阱1: 钩子方法过多导致子类混乱

**症状**: 子类不知道该实现哪些方法

**预防**:
- [ ] 最多5个虚方法 (超过用策略模式)
- [ ] 清晰标记强制vs可选
- [ ] 提供实现指导文档

**检查脚本**:
```java
// 计数虚方法
int abstractMethodCount = 0;
for (Method m : baseClass.getDeclaredMethods()) {
    if (Modifier.isAbstract(m.getModifiers())) {
        abstractMethodCount++;
    }
}
assert abstractMethodCount <= 5 : "虚方法过多";
```

### 陷阱2: 子类修改了算法流程顺序

**症状**: 模板方法失效，流程混乱

**预防**:
- [ ] 模板方法使用 final
- [ ] 禁止覆盖模板方法
- [ ] 使用编译器检查

### 陷阱3: 虚方法之间有隐藏依赖

**症状**: step2() 依赖 step1() 结果但无法传递

**解决**:
```java
// ❌ 错误: 隐藏依赖
protected abstract void step1();
protected abstract void step2();

// ✅ 正确: 显式依赖
protected List<Data> step1();
protected void step2(List<Data> data);
```

### 陷阱4: 测试困难-无法独立测试子类

**症状**: 每次测试都需要新建模板+子类

**解决**:
```java
// 使用匿名类进行单元测试
DataProcessor processor = new DataProcessor() {
    @Override
    protected void validate(Data d) { 
        // 测试实现 
    }
};
```

### 陷阱5: 泛型类型不兼容

**症状**: 子类使用不同泛型导致类型错误

**预防**:
- [ ] 固定父类泛型 (避免双重泛型)
- [ ] 子类声明时指定类型
- [ ] 添加类型检查测试

---

## 快速实施步骤 (6步模板)

### 第1步: 分析现有代码 (2小时)

**任务**:
- [ ] 找出重复的算法代码
- [ ] 列出所有变化点
- [ ] 统计代码重复度

**检查清单**:
```
现有实现数: ___
重复代码行数: ___
平均差异百分比: ___/100%

变化点列表:
1. _______________
2. _______________
3. _______________
```

### 第2步: 设计模板方法 (1小时)

**决定**:
- [ ] 流程步骤数 (推荐3-7步)
- [ ] 强制虚方法数 (≤5)
- [ ] 可选钩子数 (≤3)

**设计**:
```
public final void process() {
    // 步骤1: _____________
    // 步骤2: _____________
    // 步骤3: _____________
}
```

### 第3步: 提取虚方法 (2小时)

**行动**:
- [ ] 为每个变化点创建虚方法
- [ ] 定义参数和返回类型
- [ ] 标记为 protected abstract

### 第4步: 实现子类 (1小时/类)

**检查**:
- [ ] 所有虚方法已实现
- [ ] 无额外逻辑重复
- [ ] 编译通过

### 第5步: 编写测试 (2小时)

**覆盖**:
- [ ] 每个虚方法单元测试
- [ ] 完整流程集成测试
- [ ] 边界和异常情况

### 第6步: 代码审查与优化 (1小时)

**审查**:
- [ ] 运行至少2人代码审查
- [ ] 性能基准对比
- [ ] 文档完整性检查
