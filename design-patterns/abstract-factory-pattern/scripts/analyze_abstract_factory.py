#!/usr/bin/env python3
"""
抽象工厂模式分析器 (Abstract Factory Pattern Analyzer)

功能：检测代码中的抽象工厂模式实现

关键特征：
- 多个工厂接口
- 相关产品族
- 产品族的统一创建接口

Abstract Factory Pattern Analyzer
Detects Abstract Factory Pattern implementation in code.
Key characteristics:
- Multiple factory interfaces
- Family of related products
- Unified creation interface for product families
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_abstract_factory: bool
    has_product_families: bool
    has_concrete_factories: bool
    creates_product_family: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_abstract_factory_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Abstract Factory Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Abstract Factory Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_abstract_factory': False,
            'has_product_families': False,
            'has_concrete_factories': False,
            'creates_product_family': bool
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查abstract factory interface/class
    if re.search(r'(abstract\s+class|class)\s+\w*Factory\w*|Factory\s*(Protocol|ABC)', code_text):
        result['checks']['has_abstract_factory'] = True
        result['patterns'].append('已检测到抽象工厂接口')

    # 检查multiple product families
    create_methods = len(re.findall(r'def\s+(create|make)_\w+\(', code_text))
    if create_methods >= 2:
        result['checks']['has_product_families'] = True
        result['patterns'].append(f'检测到多个产品创建方法 ({create_methods})')

    # 检查concrete factory implementations
    if re.search(r'(class\s+\w+Factory\(.*Factory|\w+FactoryImpl|Factory.*:\s+def)', code_text):
        result['checks']['has_concrete_factories'] = True
        result['patterns'].append('已检测到具体工厂实现')

    # 检查工厂是否创建相关产品族
    product_types = re.findall(r'(Button|Widget|Dialog|Component|Product\w+)', code_text)
    if len(set(product_types)) >= 2:
        result['checks']['creates_product_family'] = True
        result['patterns'].append('已检测到相关产品族创建')

    # 计算confidence
    checks_count = sum(1 for v in result['checks'].values() if isinstance(v, bool) and v)
    total_checks = sum(1 for v in result['checks'].values() if isinstance(v, bool))
    result['confidence'] = checks_count / total_checks if total_checks > 0 else 0.0
    result['detected'] = result['confidence'] >= 0.75

    # 推荐建议
    if not result['checks']['has_abstract_factory']:
        result['recommendations'].append('Define abstract factory interface for multiple factory types')
    
    if create_methods < 2:
        result['recommendations'].append('Add more product creation methods to support product families')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_abstract_factory_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
