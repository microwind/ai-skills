#!/usr/bin/env python3
"""
访问者模式分析器 (Visitor Pattern Analyzer)

功能：检测代码中的访问者模式实现

关键特征：
- 访问者接口对象操作
- 具体访问者实现
- 元素接口带接受方法
- 将算法与元素结构分离

Visitor Pattern Analyzer
Detects Visitor Pattern implementation in code.
Key characteristics:
- Visitor interface for operations
- Concrete visitor implementations
- Element interface with accept method
- Separates algorithms from element structure
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_visitor_interface: bool
    has_concrete_visitors: bool
    has_element_interface: bool
    has_accept_method: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_visitor_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Visitor Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Visitor Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_visitor_interface': False,
            'has_concrete_visitors': False,
            'has_element_interface': False,
            'has_accept_method': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查visitor interface
    if re.search(r'(class\s+\w*Visitor|Visitor\s*:|interface\s+\w*Visitor)', code_text):
        result['checks']['has_visitor_interface'] = True
        result['patterns'].append('Visitor interface detected')

    # 检查concrete visitor implementations
    visitors = len(re.findall(r'class\s+\w+Visitor\(|class\s+\w+\(.*Visitor', code_text))
    if visitors >= 1:
        result['checks']['has_concrete_visitors'] = True
        result['patterns'].append(f'Concrete visitor(s) ({visitors}) detected')

    # 检查element interface
    if re.search(r'(class\s+\w*Element|Element\s*:|interface\s+\w*Element)', code_text):
        result['checks']['has_element_interface'] = True
        result['patterns'].append('Element interface detected')

    # 检查accept method
    if re.search(r'def\s+accept\(.*visitor|def\s+accept\(\s*self', code_text):
        result['checks']['has_accept_method'] = True
        result['patterns'].append('Accept method for visitor handling detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查visit method calls
    if re.search(r'visitor\.visit\(|visitor\.visit_\w+', code_text):
        result['patterns'].append('Visitor method invocation detected')

    # 检查double dispatch
    if re.search(r'accept.*visitor|visitor\.visit\(self', code_text):
        result['patterns'].append('Double dispatch mechanism detected')

    # 推荐建议
    if not result['checks']['has_visitor_interface']:
        result['recommendations'].append('Define visitor interface for different operations')

    if not result['checks']['has_element_interface']:
        result['recommendations'].append('Create element interface with accept method')

    if not result['checks']['has_accept_method']:
        result['recommendations'].append('Implement accept method for double dispatch')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_visitor_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
