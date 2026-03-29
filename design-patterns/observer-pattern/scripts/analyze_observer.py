#!/usr/bin/env python3
"""
观察者模式分析器 (Observer Pattern Analyzer)

功能：检测代码中的观察者模式实现

关键特征：
- 对象维持观察者列表
- 观察者注册或注销对象
- 对象状态改变时通知所有观察者
- 对象和观察者之间松散耦合

Observer Pattern Analyzer
Detects Observer Pattern implementation in code.
Key characteristics:
- Subject maintains list of observers
- Observers register/unregister with subject
- Subject notifies all observers on state change
- Loose coupling between subject and observers
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_subject_class: bool
    has_observer_interface: bool
    has_notify_method: bool
    has_observer_management: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_observer_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Observer Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Observer Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_subject_class': False,
            'has_observer_interface': False,
            'has_notify_method': False,
            'has_observer_management': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查subject/observable class
    if re.search(r'class\s+\w*(Subject|Observable|Publisher|Notifier)|Subject\s*:', code_text):
        result['checks']['has_subject_class'] = True
        result['patterns'].append('Subject/Observable class detected')

    # 检查observer interface
    if re.search(r'(class\s+\w*Observer|Observer\s*:|interface\s+\w*Observer|def\s+update\()', code_text):
        result['checks']['has_observer_interface'] = True
        result['patterns'].append('Observer interface detected')

    # 检查notify/publish method
    if re.search(r'def\s+(notify|publish|notify_all|fire_event)\(', code_text):
        result['checks']['has_notify_method'] = True
        result['patterns'].append('Notification method detected')

    # 检查observer management (register/unregister)
    if re.search(r'def\s+(register|subscribe|attach|add_observer|add_listener)\(|def\s+(unregister|unsubscribe|detach|remove_observer)\(', code_text):
        result['checks']['has_observer_management'] = True
        result['patterns'].append('Observer management (register/unregister) detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查observer list/collection
    if re.search(r'(observers|listeners|subscribers)\s*=|self\.observers|self\.listeners', code_text):
        result['patterns'].append('Observer collection handling detected')

    # 检查notification pattern
    if re.search(r'for\s+\w+\s+in\s+(self\.)?observers|for.*in.*listeners', code_text):
        result['patterns'].append('Observer notification loop detected')

    # 推荐建议
    if not result['checks']['has_observer_interface']:
        result['recommendations'].append('Define observer interface for loose coupling')
    
    if result['checks']['has_subject_class'] and not result['checks']['has_observer_management']:
        result['recommendations'].append('Add register/unregister methods for observer management')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_observer_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
