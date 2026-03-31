# Bridge Pattern - 诊断与规划表

## 第1步: 需求诊断 - 你真的需要Bridge吗？

### 🔍 快速检查清单

```
□ 有两个或以上的独立变化维度
□ 类爆炸问题（N×M个组合）
□ 想在运行时切换实现
□ 抽象和实现应该独立测试
□ 希望避免编译时绑定
□ 需要多平台或多方式支持
```

**诊断标准**:
- ✅ 勾选 4 项以上 → **强烈推荐使用**
- ⚠️ 勾选 2-3 项 → **可以使用**
- ❌ 勾选 2 项以下 → **可能过度设计**

**常见信号**:
- 类名如 WindowsCircle、LinuxCircle、MacCircle → 需要Bridge
- Shape类有 variant or platform 参数 → 需要Bridge
- 两个独立的继承体系 → 需要Bridge

---

## 抽象-实现维度识别矩阵

使用此表格确认两个维度:

| 维度 | 类别 | 变化频率 | 稳定性评分 | 示例 |
|------|------|---------|-----------|------|
| 抽象 | 功能分类 | 中-低 | 7/10 | Shape,Document,Payment |
| 实现 | 具体方式 | 中-高 | 5/10 | RenderingAPI,Database,Gateway |

**评估标准**:
- 稳定性 > 8/10: 可能不需要Bridge
- 稳定性 5-7: 理想Bridge候选
- 稳定性 < 5: Bridge很有必要

**实例**:
```
类爆炸问题:
- Shape: Circle(形状)  × Platform: Windows/Linux/Mac(平台)
- 结果: 9个类 (Circle-Windows, Circle-Linux, ...) ❌

使用Bridge:
- Shape (1个抽象) × RenderingAPI(实现)  
- 结果: 2+N个类 ✅ (灵活可扩展)
```

---

## 实现方法选择矩阵

| 方法 | 复杂度 | 灵活性 | 适用场景 | 学习曲线 |
|------|--------|--------|---------|----------|
| 虚方法式 | ⭐ | ⭐ | 简单系统，绑定固定 | 低 |
| 参数化式 | ⭐⭐ | ⭐⭐⭐ | 多数场景，运行时切换 | 中 |
| 配置驱动式 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 复杂系统，多环境部署 | 高 |
| 工厂式 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 大型项目，完全解耦 | 高 |

**选择指南**:
1. 原型/MVP → 虚方法式
2. 生产单平台 → 参数化式  
3. 多环境部署(开发/测试/生产) → 配置驱动式
4. 企业系统/需要高可维护性 → 工厂式

---

## 6步实施规划

### 第1步: 识别变化维度 (2小时)

**任务清单**:
- [ ] 列出所有要支持的功能维度
- [ ] 列出所有要支持的实现维度
- [ ] 评估每个维度的独立性(0-10)
- [ ] 计算预期的类数量(N×M)

**工作表**:
```
维度1: _________________ (变化频率: _/10)
维度2: _________________ (变化频率: _/10)

组合数量: ___ × ___ = ___ 个类
现有代码重复: ____ %

结论: Bridge收益 = (重复代码 × 维度独立性) / 总复杂度
```

### 第2步: 选择实现方法 (1小时)

**决策**:
- [ ] 虑所有4种方法
- [ ] 基于项目规模选择
- [ ] 获得团队共识

**记录决策理由**:
```
选择的方法: _________________
理由: _______________________
风险: _______________________
```

### 第3步: 设计抽象接口 (2小时)

**接口设计**:
```java
// 抽象维度接口
public abstract class AbstractionInterface {
    // 关键操作
    public abstract void operation1();
    public abstract void operation2();
}

// 实现维度接口
public interface Implementation {
    // 低级操作
    void lowLevelOp1();
    void lowLevelOp2();
}
```

**检查清单**:
- [ ] 接口职责清晰(单一职责)
- [ ] 没有循环依赖
- [ ] 操作数 ≤ 10 (否则拆分)
- [ ] 参数类型简洁

### 第4步: 实现具体类 (4小时/类)

**实施步骤**:
- [ ] ConcreteAbstraction1 实现
- [ ] ConcreteAbstraction2 实现
- [ ] ConcreteImplementation1 实现
- [ ] ConcreteImplementation2 实现

**质量检查**:
- [ ] 编译无错误
- [ ] 无代码重复(重复度 < 5%)
- [ ] 异常处理完整
- [ ] 日志记录充分

### 第5步: 集成与测试 (3小时)

**集成步骤**:
- [ ] 抽象类与实现类组合
- [ ] 依赖注入配置
- [ ] 接口兼容性检查

**测试覆盖**:
- [ ] 单元测试: 每个类独立测试
- [ ] 集成测试: N×M组合抽样测试(10%)
- [ ] 性能测试: 基准对比
- [ ] 压力测试: 大数据场景

### 第6步: 文档与知识转移 (1小时)

**文档内容**:
- [ ] 维度说明(抽象vs实现)
- [ ] 实现选择理由
- [ ] 扩展指南(如何添加新维度)
- [ ] 常见错误预防
- [ ] 性能指标

---

## 常见陷阱预防

### ⚠️ 陷阱1: 类爆炸仍未解决

❌ 反面做法:
```
抽象维度: Shape, Window
实现维度: Platform, RenderingAPI, ColorFormat
结果: Shape×Platform×RenderingAPI×ColorFormat = 极多类
```

✅ 正确做法:
```
第1个Bridge: Shape × Platform
第2个Bridge: 结果 × RenderingAPI
保持浅层 ≤ 2层Bridge
```

### ⚠️ 陷阱2: 实现接口过复杂

❌ 反面做法:
```java
public interface Implementation {
    void draw();
    void resize();
    void move();
    void rotate();
    void scale();
    void skew();
    // 15个方法...
}
```

✅ 正确做法:
```java
public interface RenderingAPI {
    void drawPrimitive(Primitive p); // 只有核心方法
}

// 复杂操作由上层实现
public abstract class Shape {
    protected RenderingAPI api;
    public void rotate() { /* 基于drawPrimitive实现 */ }
}
```

### ⚠️ 陷阱3: 运行时性能下降

❌ 反面做法:
```java
// 每次调用都查表、反射
public class DynamicBridge {
    public void operation() {
        Implementation impl = getImplementationByConfig();
        impl.execute();
    }
}
```

✅ 正确做法:
```java
// 初始化一次，重复使用
public class OptimizedBridge {
    private final Implementation impl;
    
    public OptimizedBridge(Implementation impl) {
        this.impl = impl; // 缓存
    }
    
    public void operation() {
        impl.execute(); // 直接调用
    }
}
```

### ⚠️ 陷阱4: 维度混淆

❌ 反面做法:
```java
public abstract class Shape {
    protected DrawingAPI api;
    protected Color color;    // ❌ 混入了第3个维度
    protected int zOrder;     // ❌ 混入了第4个维度
}
```

✅ 正确做法:
```java
// 分离关注点
public interface Shape {
    void draw(DrawingAPI api);
}

public class ColoredShape extends ShapeDecorator {
    // 颜色由Decorator处理
}

public class OrderedShape extends ShapeComposite {
     // 层级由Composite处理
}
```

---

## 快速参考

### 决策流程图

```
问题: 需要Bridge吗?
│
├─ "有N×M个类组合的问题？"
│  ├─ YES → "两个维度都会变化？"
│  │  ├─ YES → "使用Bridge"
│  │  └─ NO → "使用继承"
│  └─ NO → "可能不需要"
│
└─ "何时切换实现？"
   ├─ "编译时确定" → "虚方法式"
   ├─ "运行时选择" → "参数化式"
   ├─ "多环境部署" → "配置驱动式"
   └─ "企业级需求" → "工厂式"
```

### 快速启动模板

**最小实现**:
```java
// 步骤1: 定义实现接口
public interface Implementation {
    void lowLevelOp();
}

// 步骤2: 创建抽象
public abstract class Abstraction {
    protected Implementation impl;
    
    public Abstraction(Implementation impl) {
        this.impl = impl;
    }
    
    public abstract void operation();
}

// 步骤3: 具体实现
public class ConcreteAbstraction extends Abstraction {
    @Override
    public void operation() {
        impl.lowLevelOp();
    }
}
```

### 复杂度评估

```
当出现以下信号时，Bridge好处最大:
✅ 需要跨越 2+ 物理边界(操作系统、语言、网络)
✅ 抽象和实现变化频率不同
✅ 需要运行时灵活切换
✅ 系统要支持多个第三方库

复杂度收益 = (现有代码重复百分比) × (维度独立性)
            ÷ (Bridge实现开销)

当收益 > 1.5 时，Bridge是明智选择
```
