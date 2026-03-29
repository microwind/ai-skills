#!/usr/bin/env python3
"""
代理模式分析器 (Proxy Pattern Analyzer)

功能：检测代码中的代理模式实现

关键特征：
- 代理对象控制访问
- 延迟加载重对象
- 使用缓存减少费用操作
- 前置处理（安全检查和日志记录）

Proxy Pattern Analyzer
Detects Proxy Pattern implementation in code.
Key characteristics:
- Proxy object controls access
- Lazy loading of heavy objects
- Use caching to reduce expensive operations
- Pre-processing (security check and logging)
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_subject_interface: bool
    has_real_subject: bool
    has_proxy_class: bool
    controls_access: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_proxy_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Proxy Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Proxy Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_subject_interface': False,
            'has_real_subject': False,
            'has_proxy_class': False,
            'controls_access': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查subject interface
    if re.search(r'(class\s+\w*Subject|Subject\s*:|interface\s+\w*Subject)', code_text):
        result['checks']['has_subject_interface'] = True
        result['patterns'].append('Subject interface detected')

    # 检查real subject
    if re.search(r'class\s+Real\w+|RealSubject|real_object', code_text):
        result['checks']['has_real_subject'] = True
        result['patterns'].append('Real subject class detected')

    # 检查proxy class
    if re.search(r'class\s+\w*Proxy|Proxy\s*:', code_text):
        result['checks']['has_proxy_class'] = True
        result['patterns'].append('Proxy class detected')

    # 检查access control (lazy loading, caching, access restrictions)
    if re.search(r'if\s+self\._\w+\s+is\s+None|self\._cached|if not.*initialized|permission|check_access', code_text):
        result['checks']['controls_access'] = True
        result['patterns'].append('Access control/lazy loading detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查request forwarding
    if re.search(r'self\._subject\.\w+\(|self\.real_object\.\w+\(', code_text):
        result['patterns'].append('Request forwarding to real subject detected')

    # 检查lazy initialization
    if re.search(r'if\s+self\._\w+\s+is\s+None.*self\._\w+\s*=', code_text):
        result['patterns'].append('Lazy initialization detected')

    # 推荐建议
    if not result['checks']['has_subject_interface']:
        result['recommendations'].append('Define subject interface for proxy consistency')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_proxy_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
