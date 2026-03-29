#!/usr/bin/env python3
"""
命令模式分析器 (Command Pattern Analyzer)

功能：检测代码中的命令模式实现

关键特征：
- 命令接口/协议
- 具体命令实现
- 准一执行程序/执行器类
- 解耦发送方与接收者

Command Pattern Analyzer
Detects Command Pattern implementation in code.
Key characteristics:
- Command interface/protocol
- Concrete command implementations
- Invoker/executor class
- Decoupling requestor from executor
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_command_interface: bool
    has_concrete_commands: bool
    has_invoker: bool
    has_execute_method: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_command_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Command Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Command Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_command_interface': False,
            'has_concrete_commands': False,
            'has_invoker': False,
            'has_execute_method': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查command interface
    if re.search(r'(class\s+\w*Command|Command\s*:|interface\s+\w*Command|ABC.*Command)', code_text):
        result['checks']['has_command_interface'] = True
        result['patterns'].append('Command interface detected')

    # 检查concrete command implementations
    commands = len(re.findall(r'class\s+\w+Command\(|class\s+\w+\s*\(\s*Command', code_text))
    if commands >= 2:
        result['checks']['has_concrete_commands'] = True
        result['patterns'].append(f'Concrete commands ({commands}) detected')

    # 检查invoker/executor
    if re.search(r'class\s+\w*(Invoker|Executor|Receiver)|self\.command\s*=', code_text):
        result['checks']['has_invoker'] = True
        result['patterns'].append('Invoker/executor class detected')

    # 检查execute method
    if re.search(r'def\s+(execute|invoke|run|execute_command)\(', code_text):
        result['checks']['has_execute_method'] = True
        result['patterns'].append('Execute/invoke method detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查undo/redo capability
    if re.search(r'(def\s+undo|def\s+redo|history|stack)', code_text):
        result['patterns'].append('Undo/redo capability detected')

    # 检查command queueing
    if re.search(r'(queue|list|deque).*command|command.*queue', code_text.lower()):
        result['patterns'].append('Command queuing detected')

    # 推荐建议
    if not result['checks']['has_command_interface']:
        result['recommendations'].append('Define command interface for consistent command execution')
    
    if result['checks']['has_command_interface'] and commands < 2:
        result['recommendations'].append('Add more concrete command implementations')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_command_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
