# Interpreter - 诊断、规划、实现表单

## 第1步：诊断 (Diagnosis)

### 语法复杂度评估

| 因素 | 简单 | 中等 | 复杂 |
|------|------|------|------|
| **文法规则数** | <10条 | 10-30条 | >30条 |
| **运算符优先级** | 无 | 2-3层 | 4+层 |
| **嵌套深度** | <5 | 5-20 | >20 |
| **错误恢复** | 无需 | 基础 | 完善 |
| **优化需求** | 无 | 基础 | 复杂 |

**评估**: 如果大多数是"简单"→ **可用Interpreter模式** | 如果大多数是"复杂" → **考虑ANTLR等工具**

---

## 第2步：规划 (Planning)

### DSL vs 通用语言决策矩阵

| 标准 | DSL | 通用语言 |
|------|-----|--------|
| **学习曲线** | 低 | 高 |
| **功能覆盖** | 有限+特定 | 无限通用 |
| **性能** | 可优化 | 需编译 |
| **保守期** | 短 | 长 |
| **维护成本** | 低 | 高 |

**推荐**: 
- 简单表达式 → 直接实现Interpreter
- 中等复杂 → 使用ANTLR / javacc
- 复杂+多语言 → 考虑编译型语言

---

## 第3步：文法定义

### 语法规则设计

为你的语言定义BNF：

```
Rule1: ...
Rule2: ...
Rule3: ...
```

**检查清单**:
- [ ] 是否左递归? (需要改写)
- [ ] 是否有二义性? (需要优先级)
- [ ] 是否易于解析? (LL(1)最优)

---

## 第4步：实现规划 (Implementation Strategy)

### 6步解析实现流程

#### Step 1: 定义Expression接口
```java
interface Expression {
    Object interpret(Context context);
}
```

#### Step 2: 实现基础表达式
```java
class TerminalExpression implements Expression {
    public Object interpret(Context context) {
        // 终结符处理
    }
}
```

#### Step 3: 实现复合表达式
```java
class NonterminalExpression implements Expression {
    Private Expression left, right;
    public Object interpret(Context context) {
        // 递归处理子表达式
    }
}
```

#### Step 4: 构建解析器
```java
class Parser {
    public Expression parse(String input) {
        // 递归下降或其他解析策略
        return parseExpression();
    }
}
```

#### Step 5: 创建上下文
```java
class Context {
    private Map<String, Object> variables;
    // getter / setter
}
```

#### Step 6: 集成使用
```java
Parser parser = new Parser();
Expression ast = parser.parse(input);
Context ctx = new Context();
Object result = ast.interpret(ctx);
```

---

## 第5步：测试 (Testing)

### 单元测试清单

- [ ] 终结符表达式的正确性
- [ ] 运算符优先级
- [ ] 变量作用域管理
- [ ] 错误情况处理
- [ ] 性能和递归深度

### 集成测试清单

- [ ] 完整表达式的求值
- [ ] 复杂嵌套表达式
- [ ] 边界情况
- [ ] 内存泄漏

---

## 第6步：优化 (Optimization)

### 性能规划清单

- [ ] 表达式缓存 (MRU)
- [ ] 常数折叠优化
- [ ] 短路求值
- [ ] 虚拟机字节码
- [ ] JIT编译

### 常见陷阱预防

| 陷阱 | 症状 | 防止方法 |
|------|------|--------|
| 栈溢出 | 深层嵌套失败 | 限制递归深度或改用迭代 |
| 性能差 | 重复计算 | 表达式缓存，常数折叠 |
| 错误信息差 | 无法定位问题 | 保存token位置信息 |
| 内存泄漏 | 缓存过大 | 使用LRU缓存策略 |
| 二义性 | 歧义解析 | 显式定义优先级和结合性 |

---

## 决策流程

```
【分析语言特性】
    ↓
【确定复杂度】
    ├→ 简单 → 直接Interpreter
    ├→ 中等 → ANTLR + Visitor
    └→ 复杂 → 编译型语言或现成工具
        ↓
【选择实现方式】
    ├→ 递归下降 (容易理解)
    ├→ AST+访问者 (易扩展)
    └→ 虚拟机+字节码 (高性能)
        ↓
【实现】
```

---

## 快速检查清单

在实现Interpreter前检查：

- [ ] 文法规则是否为LL(1)或易于解析?
- [ ] 最大表达式深度是多少?
- [ ] 需要支持哪些优化?
- [ ] 性能要求是什么?
- [ ] 是否需要完整的错误恢复?
- [ ] 修改文法的频率有多高?
