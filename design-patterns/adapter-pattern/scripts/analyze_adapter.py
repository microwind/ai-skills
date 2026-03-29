#!/usr/bin/env python3
"""
适配器模式分析器 (Adapter Pattern Analyzer)

功能：检测代码中的适配器模式实现

关键特征：
- 适配不兼容接口
- 两个接口间的包装/桥接
- 目标接口定义
- 具体适配器实现

Adapter Pattern Analyzer
Detects Adapter Pattern implementation in code.
Key characteristics:
- Adapts incompatible interfaces
- Wrapper/bridge between two interfaces
- Target interface definition
- Concrete adapter implementation
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_target_interface: bool
    has_adaptee_class: bool
    has_adapter_class: bool
    adapts_interface: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_adapter_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Adapter Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Adapter Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_target_interface': False,
            'has_adaptee_class': False,
            'has_adapter_class': False,
            'adapts_interface': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查target interface
    if re.search(r'(class\s+\w*Target|Target\s*:|interface\s+\w*Target)', code_text):
        result['checks']['has_target_interface'] = True
        result['patterns'].append('Target interface detected')

    # 检查adaptee class
    if re.search(r'class\s+\w*Adaptee|adaptee|Adaptee\s*:', code_text):
        result['checks']['has_adaptee_class'] = True
        result['patterns'].append('Adaptee class detected')

    # 检查adapter implementation
    if re.search(r'class\s+\w*Adapter|Adapter\s*:', code_text):
        result['checks']['has_adapter_class'] = True
        result['patterns'].append('Adapter class detected')

    # 检查interface adaptation
    if re.search(r'class\s+\w*Adapter\(.*self\.adaptee|def\s+\w+\(self.*self\.adaptee', code_text):
        result['checks']['adapts_interface'] = True
        result['patterns'].append('Interface adaptation detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查method delegation
    if re.search(r'self\.adaptee\.\w+\(|return\s+self\.adaptee\.\w+', code_text):
        result['patterns'].append('Method delegation to adaptee detected')

    # 推荐建议
    if result['checks']['has_adaptee_class'] and not result['checks']['has_adapter_class']:
        result['recommendations'].append('Create adapter class to bridge incompatible interfaces')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_adapter_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
