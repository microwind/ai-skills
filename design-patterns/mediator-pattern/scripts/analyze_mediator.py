#!/usr/bin/env python3
"""
中介模式分析器 (Mediator Pattern Analyzer)

功能：检测代码中的中介模式实现

关键特征：
- 中介接口协调同事对象
- 具体中介实现
- 同事对象通过中介通信
- 减少同事之间的耦合度

Mediator Pattern Analyzer
Detects Mediator Pattern implementation in code.
Key characteristics:
- Mediator interface for colleague coordination
- Concrete mediator implementation
- Colleague objects communicate through mediator
- Reduces coupling between colleagues
"""
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_mediator_interface: bool
    has_concrete_mediator: bool
    has_colleague_classes: bool
    coordinates_communication: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_mediator_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Mediator Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Mediator Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_mediator_interface': False,
            'has_concrete_mediator': False,
            'has_colleague_classes': False,
            'coordinates_communication': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查mediator interface
    if re.search(r'(class\s+\w*Mediator|Mediator\s*:|interface\s+\w*Mediator)', code_text):
        result['checks']['has_mediator_interface'] = True
        result['patterns'].append('Mediator interface detected')

    # 检查concrete mediator
    if re.search(r'class\s+\w+Mediator\(|class\s+\w+\(.*Mediator', code_text):
        result['checks']['has_concrete_mediator'] = True
        result['patterns'].append('Concrete mediator implementation detected')

    # 检查colleague classes
    colleagues = len(re.findall(r'class\s+\w+Colleague|self\.mediator\s*=|self\._mediator\s*=', code_text))
    if colleagues >= 2:
        result['checks']['has_colleague_classes'] = True
        result['patterns'].append(f'Colleague classes ({colleagues}) detected')

    # 检查communication coordination
    if re.search(r'self\.mediator\.\w+\(|self\._mediator\.notify', code_text):
        result['checks']['coordinates_communication'] = True
        result['patterns'].append('Mediated communication detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查colleague registration
    if re.search(r'register|notify|send_message', code_text):
        result['patterns'].append('Colleague registration/notification detected')

    # 检查reducing direct coupling
    if not re.search(r'self\.colleague\d+\.\w+\(', code_text):
        result['patterns'].append('Indirect colleague interaction detected')

    # 推荐建议
    if not result['checks']['has_mediator_interface']:
        result['recommendations'].append('Define mediator interface for colleague coordination')

    if colleagues < 2:
        result['recommendations'].append('Add more colleague classes to justify mediator usage')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_mediator_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
