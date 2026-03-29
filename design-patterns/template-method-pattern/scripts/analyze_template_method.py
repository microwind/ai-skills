#!/usr/bin/env python3
"""
模板方法模式分析器 (Template Method Pattern Analyzer)

功能：检测代码中的模板方法模式实现

关键特征：
- 基础类定义算法骨架
- 子类实现具体步骤
- 不变部分在基础类上
- 变化部分覆盖在子类上

Template Method Pattern Analyzer
Detects Template Method Pattern implementation in code.
Key characteristics:
- Base class defines algorithm skeleton
- Subclasses implement specific steps
- Invariant parts in base class
- Variable parts overridden in subclasses
"""
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_base_class: bool
    has_template_method: bool
    has_abstract_methods: bool
    has_subclass_overrides: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_template_method_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Template Method Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Template Method Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_base_class': False,
            'has_template_method': False,
            'has_abstract_methods': False,
            'has_subclass_overrides': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查base class
    if re.search(r'class\s+\w+:|ABC|abstract.*class', code_text):
        result['checks']['has_base_class'] = True
        result['patterns'].append('Base class detected')

    # 检查template method
    if re.search(r'def\s+\w+\(self\):.*\n\s+self\.\w+\(', code_text):
        result['checks']['has_template_method'] = True
        result['patterns'].append('Template method detected')

    # 检查abstract/protected methods
    if re.search(r'@abstractmethod|raise\s+NotImplementedError|def\s+_\w+\(', code_text):
        result['checks']['has_abstract_methods'] = True
        result['patterns'].append('Abstract or protected methods detected')

    # 检查method overriding in subclasses
    subclasses = len(re.findall(r'class\s+\w+\(\w+\):', code_text))
    if subclasses >= 1 and re.search(r'def\s+\w+\(self\):', code_text):
        result['checks']['has_subclass_overrides'] = True
        result['patterns'].append(f'Subclass method overrides detected ({subclasses})')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查method calls within method
    if re.search(r'def\s+template\w+\(self\):.*self\.\w+\(\).*self\.\w+\(\)', code_text):
        result['patterns'].append('Algorithm skeleton with multiple steps detected')

    # 推荐建议
    if not result['checks']['has_abstract_methods']:
        result['recommendations'].append('Use @abstractmethod to define hooks for subclasses')

    if result['checks']['has_template_method'] and not result['checks']['has_subclass_overrides']:
        result['recommendations'].append('Create subclasses to override template method hooks')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_template_method_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
