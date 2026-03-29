#!/usr/bin/env python3
"""
解释器模式分析器 (Interpreter Pattern Analyzer)

功能：检测代码中的解释器模式实现

关键特征：
- 语法表示在类中
- 表达式层级结构
- 解释方法用于求值
- 上下文管理解释状态

Interpreter Pattern Analyzer
Detects Interpreter Pattern implementation in code.
Key characteristics:
- Grammar representation in classes
- Expression hierarchy
- Interpret method for evaluation
- Context for interpretation state
"""
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_expression_interface: bool
    has_terminal_expressions: bool
    has_non_terminal_expressions: bool
    has_interpret_method: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_interpreter_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Interpreter Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Interpreter Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_expression_interface': False,
            'has_terminal_expressions': False,
            'has_non_terminal_expressions': False,
            'has_interpret_method': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查expression interface
    if re.search(r'(class\s+\w*Expression|Expression\s*:|interface\s+\w*Expression)', code_text):
        result['checks']['has_expression_interface'] = True
        result['patterns'].append('Expression interface detected')

    # 检查terminal expressions
    terminals = len(re.findall(r'class\s+\w+Expression\(|terminal|leaf.*expression', code_text.lower()))
    if terminals >= 1:
        result['checks']['has_terminal_expressions'] = True
        result['patterns'].append(f'Terminal expression(s) ({terminals}) detected')

    # 检查non-terminal expressions
    non_terminals = len(re.findall(r'class\s+\w+(And|Or|Add|Subtract)\w*Expression', code_text))
    if non_terminals >= 1:
        result['checks']['has_non_terminal_expressions'] = True
        result['patterns'].append(f'Non-terminal expressions ({non_terminals}) detected')

    # 检查interpret method
    if re.search(r'def\s+(interpret|evaluate|parse)\(', code_text):
        result['checks']['has_interpret_method'] = True
        result['patterns'].append('Interpret/evaluate method detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查context usage
    if re.search(r'context|Context', code_text):
        result['patterns'].append('Context for interpretation state detected')

    # 检查recursive interpretation
    if re.search(r'interpret.*interpret|evaluate.*evaluate', code_text):
        result['patterns'].append('Recursive interpretation pattern detected')

    # 检查AST (Abstract Syntax Tree) pattern
    if re.search(r'tree|ast|syntax.*tree', code_text.lower()):
        result['patterns'].append('AST/syntax tree handling detected')

    # 推荐建议
    if not result['checks']['has_expression_interface']:
        result['recommendations'].append('Define expression interface for consistent interpretation')

    if not result['checks']['has_interpret_method']:
        result['recommendations'].append('Implement interpret method for expression evaluation')

    if terminals < 1:
        result['recommendations'].append('Add terminal expressions for base grammar rules')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_interpreter_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
