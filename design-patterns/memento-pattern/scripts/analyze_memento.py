#!/usr/bin/env python3
"""
备忘录模式分析器 (Memento Pattern Analyzer)

功能：检测代码中的备忘录模式实现

关键特征：
- 备忘录存储对象状态
- 发起者创建备忘录
- 管理员管理备忘录历史
- 恢复对象到先前状态

Memento Pattern Analyzer
Detects Memento Pattern implementation in code.
Key characteristics:
- Memento stores object state
- Originator creates memento
- Caretaker manages memento history
- Restore object to previous state
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_memento_class: bool
    has_originator_class: bool
    has_caretaker_class: bool
    saves_restores_state: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_memento_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Memento Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Memento Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_memento_class': False,
            'has_originator_class': False,
            'has_caretaker_class': False,
            'saves_restores_state': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查memento class
    if re.search(r'class\s+\w*Memento|Memento\s*:', code_text):
        result['checks']['has_memento_class'] = True
        result['patterns'].append('Memento class detected')

    # 检查originator class
    if re.search(r'class\s+\w*Originator|Originator\s*:|def\s+create_memento', code_text):
        result['checks']['has_originator_class'] = True
        result['patterns'].append('Originator class detected')

    # 检查caretaker class
    if re.search(r'class\s+\w*Caretaker|Caretaker\s*:|history|memento_stack', code_text):
        result['checks']['has_caretaker_class'] = True
        result['patterns'].append('Caretaker class detected')

    # 检查state saving/restoring
    if re.search(r'def\s+(save|restore|undo|redo)\(|self\.history', code_text):
        result['checks']['saves_restores_state'] = True
        result['patterns'].append('State save/restore methods detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查history management
    if re.search(r'(history|stack|memento_history).*append|memento.*list', code_text):
        result['patterns'].append('History/stack management detected')

    # 检查snapshot capability
    if re.search(r'snapshot|save.*state|store.*state', code_text.lower()):
        result['patterns'].append('State snapshot capability detected')

    # 推荐建议
    if not result['checks']['has_memento_class']:
        result['recommendations'].append('Create memento class to store object state')

    if not result['checks']['has_caretaker_class']:
        result['recommendations'].append('Implement caretaker to manage memento history')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_memento_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
