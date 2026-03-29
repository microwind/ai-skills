#!/usr/bin/env python3
"""
单例模式分析器 (Singleton Pattern Analyzer)

功能：检测代码中的单例模式实现

关键特征：
- 私有构造函数
- 单一实例
- 全局访问点
- 线程安全的实例创建

Singleton Pattern Analyzer
Detects Singleton Pattern implementation in code.
Key characteristics:
- Private constructor
- Single instance
- Global access point
- Thread-safe instance creation
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_private_constructor: bool
    has_static_instance: bool
    has_access_method: bool
    is_thread_safe: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_singleton_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Singleton Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Singleton Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_private_constructor': False,
            'has_static_instance': False,
            'has_access_method': False,
            'is_thread_safe': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查private constructor
    if re.search(r'(def __init__|__new__)\(self.*self\)', code_text) and 'private' in code_text.lower():
        result['checks']['has_private_constructor'] = True
        result['patterns'].append('Private constructor detected')

    # 检查static/class instance
    if re.search(r'_instance\s*=|__instance\s*=|@classmethod.*_instance', code_text):
        result['checks']['has_static_instance'] = True
        result['patterns'].append('Static instance variable detected')

    # 检查getInstance or similar access method
    if re.search(r'def\s+(get|getInstance|instance|__new__|__call__)\(', code_text):
        result['checks']['has_access_method'] = True
        result['patterns'].append('Singleton access method detected')

    # 检查thread-safety mechanisms
    if re.search(r'(lock|Lock|RLock|synchronized|threading|mutex)', code_text):
        result['checks']['is_thread_safe'] = True
        result['patterns'].append('Thread-safe implementation detected')
    else:
        result['issues'].append('No thread-safety mechanism detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # Additional checks
    if '_instance' in code_text:
        if re.search(r'if\s+.*_instance.*is\s+None', code_text) or 'if _instance is None' in code_text:
            result['patterns'].append('Lazy initialization detected')

    # 推荐建议
    if not result['checks']['is_thread_safe']:
        result['recommendations'].append('Implement thread-safe instance creation')
    
    if result['detected']:
        if 'import' not in code_text:
            result['recommendations'].append('Consider using a factory or dependency injection container')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_singleton_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
