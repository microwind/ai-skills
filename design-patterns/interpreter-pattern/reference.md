# Interpreter Pattern

Interpreter pattern is a behavioral design pattern that defines a grammar or language representation using classes, allowing you to parse and interpret sentences in that language.

## Purpose
- Define a grammar for a language
- Create an interpreter for sentences in that language
- Avoid hardcoding interpretation logic

## Key Characteristics
- Expression hierarchy with terminal and non-terminal expressions
- Each expression class represents a grammar rule
- Interpret method evaluates expressions
- Context stores interpretation state

## When to Use
- You need to parse and evaluate domain-specific languages
- Building query languages or formula interpreters
- Implementing configuration file parsers
- Creating mathematical expression evaluators

## Structure
- **Expression**: Interface for all expression nodes
- **TerminalExpression**: Implements leaf nodes in the grammar tree
- **NonTerminalExpression**: Implements composite nodes
- **Context**: Contains shared interpretation state
- **Client**: Builds AST and initiates interpretation

## Benefits
- Easy to add new grammar rules
- Represents grammar as classes
- Makes it easy to change and extend grammar

## Trade-offs
- Complex grammars become complicated
- Performance might be impacted
- Better alternatives (Regex, Parsers) for complex languages
