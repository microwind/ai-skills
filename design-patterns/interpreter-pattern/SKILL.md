---
name: Interpreter
description: "定义语言的文法表示，并定义一个解释器来处理该表示"
license: MIT
---

# Interpreter Pattern (解释器模式)

## 核心概念

**Interpreter**是一种Behavioral设计模式。

**定义**: 给定一个语言或表达式，定义它的文法，并建立一个解释器来解释该语言中的句子。它为特定的应用领域设计一套灵活的语言。

### 核心思想

- **文法表示**: 将语言的文法规则用类层次表示
- **递归解析**: 根据文法递归构建表达式树
- **统一处理**: 所有表达式都遵循统一的接口
- **可扩展**: 易于新增语言规则

---

## 何时使用

### 触发条件

1. **需要解析特定格式的表达式** - SQL、配置语言、公式
2. **文法规则已明确定义** - BNF、EBNF格式
3. **需要多种解析策略** - 不同方言或变体
4. **需要动态执行表达式** - 脚本、模板、规则引擎
5. **需要编译或优化表达式** - 如JIT编译

### 不适合场景

- ❌ 语言规则非常复杂 - 解释器模式会导致类爆炸
- ❌ 性能要求极高 - 解释执行效率低，应使用编译
- ❌ 语言会频繁变化 - 维护成本高
- ❌ 只需简单的表达式求值 - 直接使用脚本引擎

---

## 基本结构

### 参与者

1. **AbstractExpression** - 抽象表达式，定义interpret接口
2. **TerminalExpression** - 终结符表达式，不再包含其他表达式
3. **NonterminalExpression** - 非终结符表达式，包含其他表达式
4. **Context** - 上下文，存储解释时所需的全局信息

### UML关系

```
┌──────────────────────────┐
│  AbstractExpression      │
├──────────────────────────┤
│ + interpret(context)     │
└──────────────────────────┘
         △
         │ implements
    ┌────┴───────────────────┐
    │                        │
┌───────────────┐    ┌─────────────────┐
│Terminal       │    │Nonterminal      │
│Expression     │    │Expression       │
├───────────────┤    ├─────────────────┤
│ + interpret() │    │ - expressions   │
└───────────────┘    │ + interpret()   │
                     └─────────────────┘

Context 维护全局状态（变量、堆栈等）
```

---

## 实现方式对比

### 方法1: 递归下降解析 (Classic)

**特点**: 最基础的解释器，按表达式优先级递归

```java
// 简单的计算器: E := E+T | E-T | T
//               T := T*F | T/F | F
//               F := (E) | number

class Parser {
    private Scanner scanner;
    private int currentToken;
    
    public Parser(String input) {
        scanner = new Scanner(input);
        nextToken();
    }
    
    public Expression parse() {
        return parseExpression();
    }
    
    private Expression parseExpression() {
        Expression expr = parseTerm();
        while (currentToken == '+' || currentToken == '-') {
            int op = currentToken;
            nextToken();
            Expression right = parseTerm();
            expr = new BinaryExpression(expr, op, right);
        }
        return expr;
    }
    
    private Expression parseTerm() {
        Expression expr = parseFactor();
        while (currentToken == '*' || currentToken == '/') {
            int op = currentToken;
            nextToken();
            Expression right = parseFactor();
            expr = new BinaryExpression(expr, op, right);
        }
        return expr;
    }
    
    private Expression parseFactor() {
        if (currentToken == '(') {
            nextToken();
            Expression expr = parseExpression();
            if (currentToken == ')') nextToken();
            return expr;
        }
        return new NumberExpression(parseNumber());
    }
}
```

### 方法2: 访问者模式结合解释器

**特点**: 分离表达式结构和解释逻辑

```java
interface ExprVisitor {
    int visit(NumberExpr expr);
    int visit(BinaryExpr expr);
    int visit(VariableExpr expr);
}

class EvaluationVisitor implements ExprVisitor {
    Map<String, Integer> variables;
    
    @Override
    public int visit(NumberExpr expr) {
        return expr.value;
    }
    
    @Override
    public int visit(BinaryExpr expr) {
        int left = expr.left.accept(this);
        int right = expr.right.accept(this);
        return applyOperation(expr.op, left, right);
    }
    
    private int applyOperation(String op, int left, int right) {
        switch(op) {
            case "+": return left + right;
            case "-": return left - right;
            case "*": return left * right;
            case "/": return left / right;
            default: throw new IllegalArgumentException();
        }
    }
}
```

### 方法3: AST + 解释器模式

**特点**: 先构建完整AST，再遍历解释

```java
// AST节点
interface ASTNode {
    void accept(ASTVisitor visitor);
}

class Program implements ASTNode {
    List<Statement> statements;
    
    @Override
    public void accept(ASTVisitor visitor) {
        visitor.visit(this);
    }
}

class Interpreter implements ASTVisitor {
    Map<String, Integer> variables = new HashMap<>();
    
    @Override
    public void visit(Program program) {
        for (Statement stmt : program.statements) {
            stmt.accept(this);
        }
    }
    
    @Override
    public void visit(AssignmentStatement stmt) {
        int value = evaluateExpression(stmt.expression);
        variables.put(stmt.variable, value);
    }
}
```

### 方法4: JIT编译解释 (高性能)

**特点**: 解释部分表达式后编译为字节码

```java
class JITInterpreter {
    private Map<String, CompiledExpression> cache = new HashMap<>();
    
    public int evaluate(String expression, Map<String, Integer> vars) {
        CompiledExpression compiled = cache.computeIfAbsent(expression, expr -> {
            // 解析表达式
            Expression ast = parse(expr);
            // 编译为字节码
            return compile(ast);
        });
        
        return compiled.execute(vars);
    }
    
    @FunctionalInterface
    interface CompiledExpression {
        int execute(Map<String, Integer> variables);
    }
}
```

---

## 6个真实使用场景

### 场景1: SQL查询解析

**应用**: 数据库引擎, ORM框架

```java
// SQL SELECT statement
class SelectStatement implements Expression {
    String table;
    List<Column> columns;
    Expression where;
    
    public void interpret(Context context) {
        List<Row> rows = context.getTable(table);
        for (Row row : rows) {
            if (where == null || where.evaluate(row)) {
                processRow(row, columns);
            }
        }
    }
}

class WhereClause implements Expression {
    Expression condition;
    
    public boolean evaluate(Row row) {
        return condition.evaluate(row);
    }
}
```

### 场景2: 配置语言解析

**应用**: 配置管理, DSL

```java
// 配置: key = value, key: [item1, item2]
class ConfigParser {
    public Config parse(String input) {
        Config config = new Config();
        for (String line : input.split("\n")) {
            if (line.contains("=")) {
                KeyValuePair pair = parseKeyValue(line);
                config.set(pair.key, pair.value);
            } else if (line.contains(":")) {
                ListDefinition list = parseList(line);
                config.set(list.key, list.values);
            }
        }
        return config;
    }
}
```

### 场景3: 正则表达式引擎

**应用**: 文本匹配, 字符串处理

```java
// 简单的正则: a|b (a或b), a* (a重复), a+ (a至少一次)
interface RegexExpr {
    boolean matches(String text);
}

class CharacterExpr implements RegexExpr {
    char c;
    
    public boolean matches(String text) {
        return text.length() > 0 && text.charAt(0) == c;
    }
}

class AlternationExpr implements RegexExpr {
    RegexExpr left, right;
    
    public boolean matches(String text) {
        return left.matches(text) || right.matches(text);
    }
}

class RepetitionExpr implements RegexExpr {
    RegexExpr expr;
    
    public boolean matches(String text) {
        int i = 0;
        while (i < text.length() && expr.matches(text.substring(i))) {
            i++;
        }
        return true;
    }
}
```

### 场景4: 模板引擎解析

**应用**: 代码生成, HTML模板, Velocity/FreeMarker

```java
// 模板: Hello ${name}, you have {{count}} messages
interface TemplateExpr {
    String render(Map<String, Object> context);
}

class LiteralExpr implements TemplateExpr {
    String text;
    
    public String render(Map<String, Object> context) {
        return text;
    }
}

class VariableExpr implements TemplateExpr {
    String name;
    
    public String render(Map<String, Object> context) {
        Object value = context.get(name);
        return value != null ? value.toString() : "";
    }
}

class IfStatementExpr implements TemplateExpr {
    String condition;
    TemplateExpr thenPart, elsePart;
    
    public String render(Map<String, Object> context) {
        boolean condResult = evaluateCondition(condition, context);
        return condResult ? thenPart.render(context) : elsePart.render(context);
    }
}
```

### 场景5: 规则引擎

**应用**: 业务规则, 权限检查, 审批流

```java
// 规则: if user.role == 'admin' and user.status == 'active'
interface Rule {
    boolean evaluate(Context context);
}

class AndRule implements Rule {
    Rule left, right;
    
    public boolean evaluate(Context context) {
        return left.evaluate(context) && right.evaluate(context);
    }
}

class ComparisonRule implements Rule {
    String field;
    String operator;
    Object value;
    
    public boolean evaluate(Context context) {
        Object fieldValue = context.getFieldValue(field);
        return compare(fieldValue, operator, value);
    }
}
```

### 场景6: 公式求值器

**应用**: Excel, 财务计算, 报表系统

```java
// 公式: IF(A1>100, A1*0.9, A1)
interface Formula {
    Number evaluate(Map<String, Number> vars);
}

class FormulaParser {
    public Formula parse(String formula) {
        // 解析: =IF(condition, trueExpr, falseExpr)
        // 或: =SUM(A1:A10)
        // 或: =A1+B1*C1
        return new CompositeFormula(parseExpression(formula));
    }
}

class FunctionCall implements Formula {
    String name;
    List<Formula> args;
    
    public Number evaluate(Map<String, Number> vars) {
        switch(name) {
            case "SUM": return args.stream().map(f -> f.evaluate(vars))
                .reduce(0, (a, b) -> a.doubleValue() + b.doubleValue());
            case "IF": return evaluateIf(args, vars);
            default: throw new IllegalArgumentException();
        }
    }
}
```

---

## 4个常见问题及解决方案

### 问题1: 语法错误恢复困难

**症状**:
- 语法错误时直接失败，无法给出有意义的错误信息
- 无法进行错误恢复和部分解析

**解决方案**:

```java
// ✅ 使用异常和错误恢复
class RobustParser {
    List<ParseError> errors = new ArrayList<>();
    
    public Expression parse(String input) throws ParseException {
        try {
            return parseExpression();
        } catch (SyntaxException e) {
            errors.add(new ParseError(e.getLine(), e.getMessage()));
            // 尝试恢复
            return recoverAndContinue();
        }
    }
    
    private Expression recoverAndContinue() {
        // 跳过直到找到有效的同步点
        while (currentToken != ';' && currentToken != EOF) {
            nextToken();
        }
        return null; // 或返回默认表达式
    }
}

// ✅ 提供详细的错误信息
class ParseError {
    int line, column;
    String message;
    String[] suggestions;
    
    ParseError(int line, String message) {
        this.line = line;
        this.message = message;
        // 生成建议
    }
}
```

### 问题2: 性能低，递归解析太慢

**症状**:
- 深层嵌套表达式导致栈溢出
- 解释执行速度远低于编译执行

**解决方案**:

```java
// ✅ 转换迭代式解析 + 虚拟机
class VirtualMachine {
    Stack<Integer> stack = new Stack<>();
    List<Instruction> instructions;
    
    public int execute() {
        for (Instruction instr : instructions) {
            switch(instr.op) {
                case PUSH: stack.push(instr.value); break;
                case ADD: stack.push(stack.pop() + stack.pop()); break;
                // ...
            }
        }
        return stack.pop();
    }
}

// ✅ 使用字节码缓存和JIT
class CachedInterpreter {
    Map<String, ByteCode> cache = new HashMap<>();
    
    public int evaluate(String expr, Variables vars) {
        ByteCode code = cache.computeIfAbsent(expr, e -> compile(e));
        return code.execute(vars);
    }
}

// ✅ 限制递归深度
class DepthLimitedParser {
    int maxDepth = 100;
    int currentDepth = 0;
    
    public Expression parse() {
        if (currentDepth++ > maxDepth) {
            throw new ParseException("Expression too deep");
        }
        try {
            return parseExpression();
        } finally {
            currentDepth--;
        }
    }
}
```

### 问题3: 上下文管理复杂

**症状**:
- 变量作用域混乱
- 函数调用时的栈帧管理复杂
- 递归调用时状态污染

**解决方案**:

```java
// ✅ 使用显式的Context stack
class ContextStack {
    Stack<Map<String, Object>> stack = new Stack<>();
    
    public void pushScope() {
        stack.push(new HashMap<>());
    }
    
    public void popScope() {
        stack.pop();
    }
    
    public void set(String name, Object value) {
        stack.peek().put(name, value);
    }
    
    public Object get(String name) {
        for (int i = stack.size() - 1; i >= 0; i--) {
            if (stack.get(i).containsKey(name)) {
                return stack.get(i).get(name);
            }
        }
        return null;
    }
}

// ✅ 使用ThreadLocal隔离并发上下文
class ThreadSafeContext {
    static ThreadLocal<Context> context = ThreadLocal.withInitial(Context::new);
    
    public static Context current() {
        return context.get();
    }
    
    public static void clear() {
        context.remove();
    }
}
```

### 问题4: 表达式优化困难

**症状**:
- 相同子表达式重复计算
- 无法进行常数折叠优化
- 表达式树过大

**解决方案**:

```java
// ✅ 表达式优化和简化
class ExpressionOptimizer {
    public Expression optimize(Expression expr) {
        if (expr instanceof BinaryExpression) {
            BinaryExpression binary = (BinaryExpression) expr;
            Expression left = optimize(binary.left);
            Expression right = optimize(binary.right);
            
            // 常数折叠
            if (left instanceof NumberExpr && right instanceof NumberExpr) {
                Number result = evaluate(binary.op, 
                    ((NumberExpr)left).value, 
                    ((NumberExpr)right).value);
                return new NumberExpr(result);
            }
            
            // 单位元优化 (+ 0, * 1)
            if (isIdentity(binary.op, left) || isIdentity(binary.op, right)) {
                return isIdentity(binary.op, left) ? right : left;
            }
            
            return new BinaryExpression(left, binary.op, right);
        }
        return expr;
    }
}

// ✅ 使用Flyweight共享常见表达式
class ExpressionCache {
    static Map<String, Expression> cache = new HashMap<>();
    
    static Expression getOrCreate(String key, Function<String, Expression> creator) {
        return cache.computeIfAbsent(key, creator);
    }
}
```

---

## 与其他模式的关系

| 模式 | 关系 | 何时结合 |
|--------|------|---------|
| **Visitor** | 分离结构和解释逻辑 | 表达式树结构复杂 |
| **Composite** | 构建表达式树 | 组织不同类型表达式 |
| **Factory** | 创建表达式节点 | 隐藏表达式创建细节 |
| **Strategy** | 不同的解释策略 | 支持多种求值方式 |
| **Flyweight** | 共享常见表达式 | 优化内存使用 |
| **Builder** | 构建复杂表达式 | 逐步构建AST |

---

## 最佳实践

### 1. 清晰的文法定义
```java
// ✅ 使用BNF或EBNF明确文法
// Expr := Term (('+' | '-') Term)*
// Term := Factor (('*' | '/') Factor)*
// Factor := Number | '(' Expr ')'
// Number := [0-9]+

// ✅ 通过ANTLR等工具生成解析器
@grammar("simple_expr.g4")
class Expr {}
```

### 2. 使用访问者模式分离关注
```java
// ✅ 表达式结构只关注表示
// 解释逻辑通过访问者实现
interface Expr {
    void accept(ExprVisitor visitor);
}

interface ExprVisitor {
    void visit(NumberExpr expr);
    void visit(BinaryExpr expr);
}
```

### 3. 提供有意义的错误报告
```java
// ✅ 准确的错误位置和建议
throw new ParseException(
    "Unexpected token at line " + line + ", column " + column +
    ". Expected '" + expected + "', got '" + actual + "'." +
    " Did you mean: " + suggestion
);
```

### 4. 优化常见情况
```java
// ✅ 缓存解析结果
// ✅ 进行表达式优化
// ✅ 使用JIT编译热路径
```

---

## 何时避免使用

- ❌ **语言过于复杂** - 解释器会变得非常复杂
- ❌ **性能至关重要** - 解释执行效率低
- ❌ **可以使用已有工具** - ANTLR, Bison等成熟方案
- ❌ **语言会频繁变化** - 维护成本太高

---

## 总结

解释器模式通过为特定领域的语言建立解释机制，提供了一种灵活的方式来实现和执行表达式。关键是：
- 清晰定义文法规则
- 正确实现递归解析或遍历
- 有效管理上下文和作用域
- 提供优化和缓存机制

