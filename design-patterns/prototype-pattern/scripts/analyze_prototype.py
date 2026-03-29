#!/usr/bin/env python3
"""
原型模式分析器 (Prototype Pattern Analyzer)

功能：检测代码中的原型模式实现

关键特征：
- 对象克隆/复制
- 避免昂贵的创建操作
- 运行时对象创建
- 浅复制或深复制

Prototype Pattern Analyzer
Detects Prototype Pattern implementation in code.
Key characteristics:
- Object cloning/copying
- Avoid expensive creation operations
- Runtime object creation
- Shallow or deep copy
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_clone_method: bool
    has_copy_operation: bool
    creates_from_existing: bool
    handles_deep_copy: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_prototype_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Prototype Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Prototype Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_clone_method': False,
            'has_copy_operation': False,
            'creates_from_existing': False,
            'handles_deep_copy': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查clone/copy methods
    if re.search(r'def\s+(clone|copy|duplicate|replicate)\(', code_text):
        result['checks']['has_clone_method'] = True
        result['patterns'].append('Clone/copy method detected')

    # 检查copy operations
    if re.search(r'(copy\.deepcopy|copy\.copy|__copy__|__deepcopy__|clone)', code_text):
        result['checks']['has_copy_operation'] = True
        result['patterns'].append('Copy operation detected')

    # 检查creating from existing object
    if re.search(r'def\s+\w+\(self,\s*\w+:\s*[\'"]?self|__init__\(self,\s*other', code_text):
        result['checks']['creates_from_existing'] = True
        result['patterns'].append('Object creation from existing instance detected')

    # 检查deep copy handling
    if re.search(r'copy\.deepcopy|deep_copy|__deepcopy__|recursive.*copy', code_text):
        result['checks']['handles_deep_copy'] = True
        result['patterns'].append('Deep copy implementation detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查prototype registry (registry pattern combined with prototype)
    if re.search(r'registry|register|prototype_map|prototypes\s*=\s*\{', code_text):
        result['patterns'].append('Prototype registry detected')

    # 推荐建议
    if not result['checks']['has_deepcopy'] and result['checks']['has_copy_operation']:
        result['recommendations'].append('Consider using deep copy for complex nested objects')

    if result['detected'] and 'copy' not in code_text:
        result['recommendations'].append('Import copy module for proper cloning support')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_prototype_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
