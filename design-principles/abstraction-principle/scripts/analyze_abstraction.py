#!/usr/bin/env python3
"""
抽象原则分析器 (Abstraction Principle Analyzer)

功能：检测代码中的抽象原则实现

关键特征：
- 接口/抽象类定义
- 分层抽象结构
- 依赖注入使用
- 实现细节封装

Abstraction Principle Analyzer
Detects Abstraction Principle implementation in code.
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_interface_or_abstract: bool
    has_implementation: bool
    has_dependency_injection: bool
    has_information_hiding: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_abstraction(code_text: str) -> ResultDict:
    """提取并分析代码以检测抽象原则实现"""
    result: ResultDict = {
        'pattern': '抽象原则',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_interface_or_abstract': False,
            'has_implementation': False,
            'has_dependency_injection': False,
            'has_information_hiding': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查接口/抽象类
    if re.search(r'(interface\s+\w+|abstract\s+class\s+\w+|class\s+\w+\(ABC\)|@abstractmethod)', code_text):
        result['checks']['has_interface_or_abstract'] = True
        result['patterns'].append('接口或抽象类定义已检测到')

    # 检查实现
    if re.search(r'(implements\s+\w+|extends\s+\w+|class\s+\w+\(\w+\))', code_text):
        result['checks']['has_implementation'] = True
        result['patterns'].append('抽象实现已检测到')

    # 检查依赖注入
    if re.search(r'(constructor\s*\(.*\w+\s+\w+|def\s+__init__\s*\(self,\s*\w+:\s*\w+|@Inject|@Autowired)', code_text):
        result['checks']['has_dependency_injection'] = True
        result['patterns'].append('依赖注入已检测到')

    # 检查信息隐藏
    if re.search(r'(private\s+\w+|protected\s+\w+|self\._\w+|#\w+)', code_text):
        result['checks']['has_information_hiding'] = True
        result['patterns'].append('信息隐藏已检测到')

    # 计算置信度
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查潜在问题
    if re.search(r'new\s+\w+\(', code_text) and not result['checks']['has_dependency_injection']:
        result['issues'].append('直接实例化而非依赖注入，可能违反抽象原则')

    # 推荐建议
    if not result['checks']['has_interface_or_abstract']:
        result['recommendations'].append('建议定义接口或抽象类来提高抽象层次')
    if not result['checks']['has_dependency_injection']:
        result['recommendations'].append('建议使用依赖注入降低耦合')
    if not result['checks']['has_information_hiding']:
        result['recommendations'].append('建议使用访问修饰符隐藏实现细节')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_abstraction(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
