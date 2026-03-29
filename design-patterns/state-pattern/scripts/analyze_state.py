#!/usr/bin/env python3
"""
状态模式分析器 (State Pattern Analyzer)

功能：检测代码中的状态模式实现

关键特征：
- 状态接口/协议
- 具体状态实现
- 上下文维持状态引用
- 依赖状态的行为

State Pattern Analyzer
Detects State Pattern implementation in code.
Key characteristics:
- State interface/protocol
- Concrete state implementations
- Context maintains state reference
- State-dependent behavior
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_state_interface: bool
    has_concrete_states: bool
    has_context_class: bool
    has_state_transitions: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_state_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测State Pattern implementation"""
    result: ResultDict = {
        'pattern': 'State Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_state_interface': False,
            'has_concrete_states': False,
            'has_context_class': False,
            'has_state_transitions': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查state interface
    if re.search(r'(class\s+\w*State|State\s*:|interface\s+\w*State|ABC.*State)', code_text):
        result['checks']['has_state_interface'] = True
        result['patterns'].append('State interface detected')

    # 检查concrete state implementations
    states = len(re.findall(r'class\s+\w+State\(|class\s+\w+\s*\(\s*State', code_text))
    if states >= 2:
        result['checks']['has_concrete_states'] = True
        result['patterns'].append(f'Concrete states ({states}) detected')

    # 检查context class
    if re.search(r'self\._state\s*=|self\.state\s*=|self\.current_state\s*=', code_text):
        result['checks']['has_context_class'] = True
        result['patterns'].append('Context with state reference detected')

    # 检查state transitions
    if re.search(r'self\._state\s*=|self\.state\s*=|set_state', code_text):
        result['checks']['has_state_transitions'] = True
        result['patterns'].append('State transitions detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查state-dependent behavior delegation
    if re.search(r'self\._state\.\w+\(|self\.state\.handle|defer.*state', code_text):
        result['patterns'].append('Behavior delegation to state detected')

    # 推荐建议
    if not result['checks']['has_state_interface']:
        result['recommendations'].append('Define state interface for consistent state behavior')
    
    if states < 2:
        result['recommendations'].append('Add more concrete state implementations')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_state_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
