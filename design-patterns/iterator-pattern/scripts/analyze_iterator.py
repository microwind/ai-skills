#!/usr/bin/env python3
"""
迭代器模式分析器 (Iterator Pattern Analyzer)

功能：检测代码中的迭代器模式实现

关键特征：
- 迭代器接口用于顺序访问
- 具体迭代器实现
- 可迭代集合接口
- 分离算法与集合

Iterator Pattern Analyzer
Detects Iterator Pattern implementation in code.
Key characteristics:
- Iterator interface for sequential access
- Concrete iterator implementations
- Iterable collection interface
- Separates algorithm from collection
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_iterator_interface: bool
    has_iterable_interface: bool
    has_concrete_iterator: bool
    supports_sequential_access: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_iterator_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Iterator Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Iterator Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_iterator_interface': False,
            'has_iterable_interface': False,
            'has_concrete_iterator': False,
            'supports_sequential_access': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查iterator interface
    if re.search(r'(class\s+\w*Iterator|Iterator\s*:|def\s+__iter__|def\s+__next__)', code_text):
        result['checks']['has_iterator_interface'] = True
        result['patterns'].append('Iterator interface detected')

    # 检查iterable interface
    if re.search(r'(class\s+\w*Iterable|Iterable\s*:|def\s+__iter__.*def\s+__next__)', code_text):
        result['checks']['has_iterable_interface'] = True
        result['patterns'].append('Iterable interface detected')

    # 检查concrete iterator
    if re.search(r'class\s+\w+Iterator\(|class\s+\w+\(.*Iterator', code_text):
        result['checks']['has_concrete_iterator'] = True
        result['patterns'].append('Concrete iterator detected')

    # 检查sequential access (next, has_next)
    if re.search(r'def\s+(next|has_next|__next__|has_more)\(', code_text):
        result['checks']['supports_sequential_access'] = True
        result['patterns'].append('Sequential access methods detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查collection traversal
    if re.search(r'while\s+.*has_next|for\s+\w+\s+in.*iterator|traverse', code_text):
        result['patterns'].append('Collection traversal pattern detected')

    # 检查position tracking
    if re.search(r'self\._index|self\._position|self\.current', code_text):
        result['patterns'].append('Position tracking detected')

    # 推荐建议
    if not result['checks']['has_iterator_interface']:
        result['recommendations'].append('Implement iterator interface (__iter__, __next__)')

    if not result['checks']['has_iterable_interface']:
        result['recommendations'].append('Create iterable collection that returns iterators')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_iterator_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
