# Interpreter Pattern - Interactive Forms

## Pattern Recognition Form

```yaml
pattern: interpreter
description: "Grammar representation and sentence interpretation"
questions:
  - question: "Does your code define a grammar or language structure?"
    keywords: ["expression", "grammar", "language", "syntax"]
    
  - question: "Do you have terminal and non-terminal expressions?"
    keywords: ["terminal", "non-terminal", "leaf", "composite"]
    
  - question: "Is there an interpret/evaluate method?"
    keywords: ["interpret", "evaluate", "parse"]
    
  - question: "Do you maintain context for interpretation state?"
    keywords: ["context", "state", "environment"]
```

## Implementation Checklist

- [ ] Define Expression interface
- [ ] Create TerminalExpression for basic grammar rules
- [ ] Create NonTerminalExpression for complex rules
- [ ] Implement interpret() method in each expression
- [ ] Create Context class for shared state
- [ ] Build AST (Abstract Syntax Tree) structure
- [ ] Test parsing and interpretation flow
