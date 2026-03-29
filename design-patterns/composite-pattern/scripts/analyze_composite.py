#!/usr/bin/env python3
"""
组合模式分析器 (Composite Pattern Analyzer)

功能：检测代码中的组合模式实现

关键特征：
- 树形组合结构
- 叶子和靐叶子节点的统一接口
- 统一处理个体和组合对象
- 部分-整体的层次结构

Composite Pattern Analyzer
Detects Composite Pattern implementation in code.
Key characteristics:
- Tree structure composition
- Component interface for leaf and composite
- Treats individual and composite objects uniformly
- Part-whole hierarchy
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_component_interface: bool
    has_leaf_implementation: bool
    has_composite_implementation: bool
    has_tree_traversal: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_composite_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Composite Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Composite Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_component_interface': False,
            'has_leaf_implementation': False,
            'has_composite_implementation': False,
            'has_tree_traversal': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查component interface
    if re.search(r'(class\s+\w*Component|Component\s*:|interface\s+\w*Component)', code_text):
        result['checks']['has_component_interface'] = True
        result['patterns'].append('Component interface detected')

    # 检查leaf implementation
    if re.search(r'class\s+\w*Leaf|class\s+Leaf\(', code_text):
        result['checks']['has_leaf_implementation'] = True
        result['patterns'].append('Leaf class detected')

    # 检查composite implementation
    if re.search(r'class\s+\w*Composite|class\s+Composite\(|self\.children|self\._children', code_text):
        result['checks']['has_composite_implementation'] = True
        result['patterns'].append('Composite class with children detected')

    # 检查tree traversal
    if re.search(r'for\s+\w+\s+in\s+(self\.)?children|for\s+\w+\s+in\s+(self\.)?_children|traverse|visit', code_text):
        result['checks']['has_tree_traversal'] = True
        result['patterns'].append('Tree traversal pattern detected')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查child management
    if re.search(r'def\s+(add|remove|get_children)\(', code_text):
        result['patterns'].append('Child management methods detected')

    # 检查recursive operation
    if re.search(r'def\s+\w+\(self.*:\n.*for.*children.*self\.\w+\(', code_text):
        result['patterns'].append('Recursive operation detected')

    # 推荐建议
    if not result['checks']['has_component_interface']:
        result['recommendations'].append('Define component interface for uniform treatment')

    if not result['checks']['has_tree_traversal']:
        result['recommendations'].append('Implement tree traversal methods')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_composite_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
