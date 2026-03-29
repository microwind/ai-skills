---
name: interpreter-pattern
description: "Interpreter Pattern - Define Grammar and Interpret Sentences"
keywords:
  - design-pattern
  - interpreter
  - grammar
  - language
  - behavioral-pattern
category: design-patterns
skills:
  - code-pattern-recognition
  - grammar-definition
  - expression-evaluation
  - syntax-tree-building
---

# Interpreter Pattern SKILL

## Summary
The Interpreter Pattern defines a grammar for a language and provides a mechanism to parse and interpret sentences in that language. It's useful for building custom languages, DSLs, and expression evaluators.

## Learning Objectives
1. Understand grammar representation using classes
2. Implement expression hierarchies
3. Build Abstract Syntax Trees (AST)
4. Create interpretation contexts
5. Apply pattern for domain-specific languages

## Core Concepts

### Expression Hierarchy
```
Expression (Interface)
├── TerminalExpression (NumberExpression, VariableExpression)
└── NonTerminalExpression (AddExpression, MultiplyExpression)
```

### Key Components
- **Expression**: Defines interpret operation
- **TerminalExpression**: Represents terminal symbols
- **NonTerminalExpression**: Represents non-terminal symbols
- **Context**: Contains interpretation-specific information

## Implementation Steps

### 1. Define Expression Interface
```python
class Expression(ABC):
    @abstractmethod
    def interpret(self, context):
        pass
```

### 2. Implement Terminal Expressions
```python
class NumberExpression(Expression):
    def __init__(self, value):
        self.value = value
    
    def interpret(self, context):
        return self.value
```

### 3. Implement Non-Terminal Expressions
```python
class AddExpression(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def interpret(self, context):
        return self.left.interpret(context) + self.right.interpret(context)
```

### 4. Create Context
```python
class Context:
    def __init__(self):
        self.variables = {}
    
    def get_value(self, name):
        return self.variables.get(name)
```

## Real-World Examples
- SQL query interpreters
- Mathematical expression evaluators
- Configuration file parsers
- DSL interpreters (domain-specific languages)
- Regular expression engines

## Anti-Patterns to Avoid
- Using for very complex grammars (use parser generators instead)
- Creating too many expression classes
- Not properly separating terminal from non-terminal expressions
- Ignoring performance implications

## Testing Strategies
- Test each expression type independently
- Test expression combinations
- Test context state management
- Test complex nested expressions
- Validate error handling

## References
- **Gang of Four**: "Design Patterns: Elements of Reusable Object-Oriented Software"
- **Source**: ~/github/design-patterns/interpreter-pattern/
