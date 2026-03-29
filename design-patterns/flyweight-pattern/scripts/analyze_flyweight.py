#!/usr/bin/env python3
"""
享元模式分析器 (Flyweight Pattern Analyzer)

功能：检测代码中的享元模式实现

关键特征：
- 共享对象以节省内存
- 内部状态与外部状态的分离
- 享元工厂
- 对象池/缓存

Flyweight Pattern Analyzer
Detects Flyweight Pattern implementation in code.
Key characteristics:
- Shared objects to save memory
- Separation of intrinsic and extrinsic state
- Flyweight factory
- Object pool/cache
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_flyweight_interface: bool
    has_flyweight_factory: bool
    has_object_pool: bool
    shares_objects: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_flyweight_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Flyweight Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Flyweight Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_flyweight_interface': False,
            'has_flyweight_factory': False,
            'has_object_pool': False,
            'shares_objects': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查flyweight interface
    if re.search(r'class\s+\w*Flyweight|Flyweight\s*:', code_text):
        result['checks']['has_flyweight_interface'] = True
        result['patterns'].append('Flyweight interface detected')

    # 检查flyweight factory
    if re.search(r'(class\s+\w*Factory|Factory\s*:|def\s+get_flyweight)', code_text):
        result['checks']['has_flyweight_factory'] = True
        result['patterns'].append('Flyweight factory detected')

    # 检查object pool/cache
    if re.search(r'pool|cache|_instances|_pool|_cache', code_text):
        result['checks']['has_object_pool'] = True
        result['patterns'].append('Object pool/cache detected')

    # 检查object sharing
    if re.search(r'if\s+.*in.*pool|in.*_instances|return.*pool\[|get.*from.*cache', code_text):
        result['checks']['shares_objects'] = True
        result['patterns'].append('Object sharing pattern detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查intrinsic state
    if re.search(r'__init__\(self.*:.*\):|self\.\w+\s*=.*final', code_text):
        result['patterns'].append('Intrinsic state detected')

    # 检查extrinsic state
    if re.search(r'def\s+\w+\(.*extrinsic|operation.*pass.*param', code_text):
        result['patterns'].append('Extrinsic state handling detected')

    # 推荐建议
    if not result['checks']['has_flyweight_factory']:
        result['recommendations'].append('Implement flyweight factory for consistent object management')

    if not result['checks']['has_object_pool']:
        result['recommendations'].append('Add object pool to cache and reuse flyweight objects')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_flyweight_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
