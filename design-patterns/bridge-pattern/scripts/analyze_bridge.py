#!/usr/bin/env python3
"""
桥接模式分析器 (Bridge Pattern Analyzer)

功能：检测代码中的桥接模式实现

关键特征：
- 将抽象与实现解耦
- 两个独立维度的变化
- 抽象类与实现类的继承关系
- 运行时灰活选择具体实现

Bridge Pattern Analyzer
Detects Bridge Pattern implementation in code.
Key characteristics:
- Decouples abstraction from implementation
- Multiple independent dimension variations
- Abstraction and implementation hierarchies
- Flexible composition
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_abstraction_hierarchy: bool
    has_implementation_hierarchy: bool
    decouples_abstractions: bool
    uses_composition: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_bridge_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Bridge Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Bridge Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_abstraction_hierarchy': False,
            'has_implementation_hierarchy': False,
            'decouples_abstractions': False,
            'uses_composition': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查abstraction hierarchy
    abstractions = len(re.findall(r'class\s+\w+\(.*Abstraction|class\s+\w+Abstraction', code_text))
    if abstractions >= 2:
        result['checks']['has_abstraction_hierarchy'] = True
        result['patterns'].append(f'Abstraction hierarchy ({abstractions}) detected')

    # 检查implementation hierarchy
    implementations = len(re.findall(r'class\s+\w+Impl|class\s+\w+Implementation', code_text))
    if implementations >= 2:
        result['checks']['has_implementation_hierarchy'] = True
        result['patterns'].append(f'Implementation hierarchy ({implementations}) detected')

    # 检查decoupling
    if re.search(r'self\.implementor|self\._impl|self\.impl', code_text):
        result['checks']['decouples_abstractions'] = True
        result['patterns'].append('Implementor reference detected')

    # 检查composition
    if re.search(r'def\s+__init__\(.*impl|self\.implementor\s*=', code_text):
        result['checks']['uses_composition'] = True
        result['patterns'].append('Composition over inheritance detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查abstraction delegation
    if re.search(r'self\.implementor\.\w+\(|self\._impl\.\w+\(', code_text):
        result['patterns'].append('Abstraction delegation to implementor detected')

    # 推荐建议
    if abstractions < 2:
        result['recommendations'].append('Create multiple abstraction levels')
    
    if implementations < 2:
        result['recommendations'].append('Create multiple implementation variants')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_bridge_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
