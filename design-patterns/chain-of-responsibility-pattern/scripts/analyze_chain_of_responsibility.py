#!/usr/bin/env python3
"""
责任链模式分析器 (Chain of Responsibility Pattern Analyzer)

功能：检测代码中的责任链模式实现

关键特征：
- 处理者接口带后继
- 多个具体处理者
- 请求递阶传下去
- 处理者决定处理或递下

Chain of Responsibility Pattern Analyzer
Detects Chain of Responsibility Pattern implementation in code.
Key characteristics:
- Handler interface with successor
- Multiple concrete handlers
- Request passes through chain
- Handler decides to process or pass
"""
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_handler_interface: bool
    has_concrete_handlers: bool
    has_chain_link: bool
    can_pass_request: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_chain_of_responsibility_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Chain of Responsibility Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Chain of Responsibility Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_handler_interface': False,
            'has_concrete_handlers': False,
            'has_chain_link': False,
            'can_pass_request': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查handler interface
    if re.search(r'(class\s+\w*Handler|Handler\s*:|interface\s+\w*Handler)', code_text):
        result['checks']['has_handler_interface'] = True
        result['patterns'].append('Handler interface detected')

    # 检查concrete handlers
    handlers = len(re.findall(r'class\s+\w+Handler\(|class\s+\w+\(.*Handler', code_text))
    if handlers >= 2:
        result['checks']['has_concrete_handlers'] = True
        result['patterns'].append(f'Concrete handlers ({handlers}) detected')

    # 检查chain link (next handler reference)
    if re.search(r'self\.next|self\._next|self\.successor|self\.next_handler', code_text):
        result['checks']['has_chain_link'] = True
        result['patterns'].append('Chain link (successor reference) detected')

    # 检查request passing
    if re.search(r'self\.next\.\w+\(|self\._next\.handle|pass.*to.*next', code_text.lower()):
        result['checks']['can_pass_request'] = True
        result['patterns'].append('Request passing detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查conditional handling
    if re.search(r'if\s+.*condition|if\s+.*can_handle|if.*suitable', code_text):
        result['patterns'].append('Conditional request handling detected')

    # 检查default handler
    if re.search(r'(default.*handler|final.*handler)', code_text.lower()):
        result['patterns'].append('Default handler for terminating chain detected')

    # 推荐建议
    if not result['checks']['has_handler_interface']:
        result['recommendations'].append('Define handler interface for consistent request handling')

    if handlers < 2:
        result['recommendations'].append('Add more concrete handler implementations')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_chain_of_responsibility_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
