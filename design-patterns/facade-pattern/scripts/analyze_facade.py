#!/usr/bin/env python3
"""
外观模式分析器 (Facade Pattern Analyzer)

功能：检测代码中的外观模式实现

关键特征：
- 为复杂子系统提供简化接口
- 低耦合度
- 封装系统较辛
- 隔离客户端与子系统

Facade Pattern Analyzer
Detects Facade Pattern implementation in code.
Key characteristics:
- Provides unified interface to subsystem
- One interface for many
- Simplifies client code
- Isolates clients from complex subsystems
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_facade_class: bool
    has_subsystem_classes: bool
    provides_simplified_interface: bool
    hides_complexity: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_facade_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Facade Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Facade Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_facade_class': False,
            'has_subsystem_classes': False,
            'provides_simplified_interface': False,
            'hides_complexity': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查facade class
    if re.search(r'class\s+\w*Facade|Facade\s*:', code_text):
        result['checks']['has_facade_class'] = True
        result['patterns'].append('Facade class detected')

    # 检查subsystem classes
    subsystems = len(re.findall(r'self\.(\w+)\s*=\s*\w+\(|self\.(\w+)', code_text))
    if subsystems >= 2:
        result['checks']['has_subsystem_classes'] = True
        result['patterns'].append(f'Subsystem references ({subsystems}) detected')

    # 检查simplified public interface
    public_methods = len(re.findall(r'def\s+(\w+)\(self[^_]|def\s+[a-z_]+\(self\):', code_text))
    if public_methods >= 2:
        result['checks']['provides_simplified_interface'] = True
        result['patterns'].append(f'Simplified public methods ({public_methods}) detected')

    # 检查complexity hiding
    if re.search(r'self\.\w+\.\w+\(.*self\.\w+\.\w+\(|multiple.*operations|coordinate', code_text.lower()):
        result['checks']['hides_complexity'] = True
        result['patterns'].append('Complex subsystem orchestration hidden')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查method orchestration
    if re.search(r'def\s+\w+\(self\):.*\n\s+self\.\w+\.\w+\(', code_text):
        result['patterns'].append('Subsystem method orchestration detected')

    # 推荐建议
    if result['checks']['has_facade_class'] and subsystems < 2:
        result['recommendations'].append('Add more subsystem references to justify facade pattern')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_facade_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
