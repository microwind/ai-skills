#!/usr/bin/env python3
"""
建造者模式分析器 (Builder Pattern Analyzer)

功能：检测代码中的建造者模式实现

关键特征：
- 分步骤构建对象
- 流畅接口（方法链接）
- 独立的构建类
- 复杂对象创建

Builder Pattern Analyzer
Detects Builder Pattern implementation in code.
Key characteristics:
- Step-by-step object construction
- Fluent interface (method chaining)
- Separate builder class
- Complex object creation
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_builder_class: bool
    has_fluent_interface: bool
    has_build_method: bool
    has_construction_steps: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_builder_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Builder Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Builder Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_builder_class': False,
            'has_fluent_interface': False,
            'has_build_method': False,
            'has_construction_steps': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查builder class
    if re.search(r'class\s+\w+Builder|Builder\s*:', code_text):
        result['checks']['has_builder_class'] = True
        result['patterns'].append('Builder class detected')

    # 检查fluent interface (return self)
    if re.search(r'return\s+self|\.set\w+\(.*return\s+self', code_text):
        result['checks']['has_fluent_interface'] = True
        result['patterns'].append('Fluent interface (method chaining) detected')

    # 检查build method
    if re.search(r'def\s+(build|create|construct)\(self\)', code_text):
        result['checks']['has_build_method'] = True
        result['patterns'].append('Build/create method detected')

    # 检查construction steps (multiple setter methods)
    setter_methods = len(re.findall(r'def\s+(set_|with_|add_)\w+\(self', code_text))
    if setter_methods >= 3:
        result['checks']['has_construction_steps'] = True
        result['patterns'].append(f'Construction steps ({setter_methods} methods) detected')
    
    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 检查common builder patterns
    if re.search(r'self\.\w+\s*=\s*\w+.*return\s+self', code_text):
        result['patterns'].append('Standard builder pattern implementation')

    # 推荐建议
    if setter_methods > 0 and not result['checks']['has_fluent_interface']:
        result['recommendations'].append('Implement fluent interface (return self) for method chaining')
    
    if result['checks']['has_builder_class'] and not result['checks']['has_build_method']:
        result['recommendations'].append('Add build() method to return constructed object')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_builder_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
