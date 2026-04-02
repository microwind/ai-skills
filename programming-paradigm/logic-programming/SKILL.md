---
name: 逻辑编程
description: "基于形式逻辑的编程范式，通过声明事实和规则，让推理引擎自动推导结论。"
license: MIT
---

# 逻辑编程 (Logic Programming)

## 概述

逻辑编程基于**形式逻辑**：程序员声明事实和规则，系统自动推导结论。不关心"怎么做"，只关心"是什么"。

**核心思想**：
- 程序 = 事实 + 规则
- 执行 = 查询 + 推理
- 不指定执行步骤，引擎自动搜索

## Prolog 示例

```prolog
% 事实（Facts）
parent(tom, bob).      % tom 是 bob 的父母
parent(tom, liz).
parent(bob, ann).
parent(bob, pat).

male(tom).
male(bob).
female(liz).
female(ann).
female(pat).

% 规则（Rules）
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.

% 查询（Queries）
?- father(tom, bob).        % true
?- grandparent(tom, ann).   % true
?- sibling(ann, pat).       % true
?- father(X, ann).          % X = bob
```

## Python 中的逻辑编程

```python
# 使用 pyDatalog 实现逻辑编程
from pyDatalog import pyDatalog

pyDatalog.create_terms('parent, ancestor, X, Y, Z')

# 事实
+parent('Tom', 'Bob')
+parent('Bob', 'Ann')
+parent('Bob', 'Pat')

# 规则
ancestor(X, Y) <= parent(X, Y)
ancestor(X, Y) <= parent(X, Z) & ancestor(Z, Y)

# 查询
print(ancestor('Tom', Y))  # Y = Bob, Ann, Pat

# 简单的规则引擎实现
class RuleEngine:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def add_fact(self, fact: tuple):
        self.facts.add(fact)

    def add_rule(self, condition, conclusion):
        self.rules.append((condition, conclusion))

    def query(self, pattern: tuple) -> list:
        results = []
        for fact in self.facts:
            if self._matches(fact, pattern):
                results.append(fact)
        return results

    def infer(self):
        changed = True
        while changed:
            changed = False
            for condition, conclusion in self.rules:
                new_facts = conclusion(self.facts)
                for fact in new_facts:
                    if fact not in self.facts:
                        self.facts.add(fact)
                        changed = True

# 使用
engine = RuleEngine()
engine.add_fact(("parent", "Tom", "Bob"))
engine.add_fact(("parent", "Bob", "Ann"))
```

## 应用场景

| 场景 | 说明 |
|------|------|
| 专家系统 | 医疗诊断、故障排查 |
| 规则引擎 | 业务规则（Drools） |
| 自然语言处理 | 语法解析 |
| 数据库查询 | SQL 本质上是逻辑编程 |
| 约束求解 | 排班、调度问题 |
| 类型推断 | 编译器中的类型系统 |

## SQL 即逻辑编程

```sql
-- SQL 是声明式的逻辑查询
-- 只描述"要什么"，不描述"怎么找"

SELECT e.name, d.department_name
FROM employees e
JOIN departments d ON e.dept_id = d.id
WHERE e.salary > 50000;

-- 等价的 Prolog 式理解：
-- 查找 (Name, DeptName)
-- 其中 employee(Name, Salary, DeptId)
-- 且 department(DeptId, DeptName)
-- 且 Salary > 50000
```

## 优缺点

### ✅ 优点
- **声明式** — 关注问题描述而非解决步骤
- **自动推理** — 引擎自动搜索答案
- **适合知识表示** — 天然表达事实和关系

### ❌ 缺点
- **性能不可控** — 推理效率依赖引擎
- **调试困难** — 推理过程不透明
- **应用范围窄** — 主流开发中使用少

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [FP](../functional-programming/) | 都是声明式的 |
| [过程式](../procedural-programming/) | 过程式是命令式的，逻辑编程是声明式的 |

## 总结

**核心**：声明事实和规则，让引擎推导结论。

**适用**：规则引擎、专家系统、约束求解、数据库查询。
