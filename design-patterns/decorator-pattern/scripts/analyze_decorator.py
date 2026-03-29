#!/usr/bin/env python3
"""
装饰器模式分析器 (Decorator Pattern Analyzer)

功能：检测代码中的装饰器模式实现

关键特征：
- 包装原始对象
- 与装饰对象相同的接口
- 动态地添加咨任和责任
- 优先使用组合分校

Decorator Pattern Analyzer
Detects Decorator Pattern implementation in code.
Key characteristics:
- Wraps original object
- Same interface as wrapped object
- Adds responsibilities dynamically
- Composition over inheritance
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_component_interface: bool
    has_concrete_component: bool
    has_decorator_class: bool
    has_composition: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_decorator_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Decorator Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Decorator Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_component_interface': False,
            'has_concrete_component': False,
            'has_decorator_class': False,
            'has_composition': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查component interface
    if re.search(r'(class\s+\w*Component|Component\s*:|interface\s+\w*Component)', code_text):
        result['checks']['has_component_interface'] = True
        result['patterns'].append('Component interface detected')

    # 检查concrete component
    if re.search(r'class\s+\w+\(.*Component\)|class\s+Concrete\w+', code_text):
        result['checks']['has_concrete_component'] = True
        result['patterns'].append('Concrete component detected')

    # 检查decorator class
    if re.search(r'class\s+\w*Decorator|@.*decorator|@functools.wraps', code_text):
        result['checks']['has_decorator_class'] = True
        result['patterns'].append('Decorator class/function detected')

    # 检查composition (wrapping)
    if re.search(r'self\.component\s*=|self\._wrapped\s*=|self\.wrapped_obj|self\.wrapped', code_text):
        result['checks']['has_composition'] = True
        result['patterns'].append('Object composition/wrapping detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查method forwarding
    if re.search(r'return\s+self\.component\.\w+|self\._wrapped\.\w+', code_text):
        result['patterns'].append('Method forwarding to wrapped object detected')

    # 检查enhanced functionality
    if re.search(r'def\s+\w+\(self.*:.*\n\s+.*self\.component\.\w+', code_text):
        result['patterns'].append('Enhanced functionality wrapper detected')

    # 推荐建议
    if not result['checks']['has_component_interface']:
        result['recommendations'].append('Define component interface for consistent decorator interface')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_decorator_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
