#!/usr/bin/env python3
"""
策略模式分析器 (Strategy Pattern Analyzer)

功能：检测代码中的策略模式实现

关键特征：
- 多个算法实现
- 策略接口/协议
- 上下文类使用策略
- 运行时算法选择

Strategy Pattern Analyzer
Detects Strategy Pattern implementation in code.
Key characteristics:
- Multiple algorithm implementations
- Strategy interface/protocol
- Context class uses strategy
- Runtime algorithm selection
"""
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_strategy_interface: bool
    has_concrete_strategies: bool
    has_context_class: bool
    supports_runtime_selection: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_strategy_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Strategy Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Strategy Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_strategy_interface': False,
            'has_concrete_strategies': False,
            'has_context_class': False,
            'supports_runtime_selection': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查strategy interface
    if re.search(r'(class\s+\w*Strategy|Strategy\s*:|interface\s+\w*Strategy)', code_text):
        result['checks']['has_strategy_interface'] = True
        result['patterns'].append('Strategy interface/protocol detected')

    # 检查concrete strategy implementations
    strategy_classes = len(re.findall(r'class\s+\w*\w+Strategy', code_text))
    if strategy_classes >= 2:
        result['checks']['has_concrete_strategies'] = True
        result['patterns'].append(f'Concrete strategies ({strategy_classes}) detected')

    # 检查context class
    if re.search(r'class\s+\w*(Context|Client)|self\.strategy\s*=|self\._strategy', code_text):
        result['checks']['has_context_class'] = True
        result['patterns'].append('Context class detected')

    # 检查runtime strategy selection
    if re.search(r'self\.strategy\s*=|set_strategy|strategy\s*=.*(\(|Strategy)', code_text):
        result['checks']['supports_runtime_selection'] = True
        result['patterns'].append('Runtime strategy selection detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查execution method
    if re.search(r'self\.strategy\.(execute|run|process|apply)\(', code_text):
        result['patterns'].append('Strategy execution detected')

    # 推荐建议
    if not result['checks']['has_strategy_interface']:
        result['recommendations'].append('Define strategy interface for consistent algorithm interface')
    
    if strategy_classes < 2 and result['checks']['has_strategy_interface']:
        result['recommendations'].append('Add more concrete strategy implementations')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_strategy_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
