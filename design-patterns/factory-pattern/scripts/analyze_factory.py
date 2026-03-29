#!/usr/bin/env python3
"""
工厂模式分析器 (Factory Pattern Analyzer)

功能：检测代码中的工厂模式实现

关键特征：
- 统一的对象创建接口
- 对象创建与使用的分离
- 子类决定实例化对象的类型

Factory Pattern Analyzer
Detects Factory Pattern implementation in code.
Key characteristics:
- Unified object creation interface
- Separation of object creation from usage
- Subclass decides instantiation strategy
"""

import sys
import json
import re
from typing import TypedDict, List, Dict

class ChecksDict(TypedDict):
    has_factory_method: bool
    has_product_interface: bool
    has_concrete_products: bool
    has_object_creation_logic: bool

class ResultDict(TypedDict):
    pattern: str
    detected: bool
    confidence: float
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_factory_pattern(code_text: str) -> ResultDict:
    """""提取并分析代码以检测Factory Pattern implementation"""
    result: ResultDict = {
        'pattern': 'Factory Pattern',
        'detected': False,
        'confidence': 0.0,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_factory_method': False,
            'has_product_interface': False,
            'has_concrete_products': False,
            'has_object_creation_logic': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # 检查工厂相关的关键字和模式
    factory_keywords = ['factory', 'create', 'make', 'build', 'construct']
    factory_count = sum(1 for kw in factory_keywords if kw in code_text.lower())

    # 检查工厂方法模式
    if re.search(r'def\s+(create|make|get|build)_\w+\(', code_text):
        result['checks']['has_factory_method'] = True
        result['patterns'].append('Factory method detected')

    # 检查产品接口/抽象类
    if re.search(r'(class|interface)\s+\w+Product|class\s+\w+Base|abstract\s+class', code_text):
        result['checks']['has_product_interface'] = True
        result['patterns'].append('产品接口或基类已检测到')

    # 检查具体产品实现
    if re.search(r'(class\s+\w+(Product|Impl|Type)\(|implements\s+\w+Product)', code_text):
        result['checks']['has_concrete_products'] = True
        result['patterns'].append('Concrete product implementations detected')

    # 检查带条件分支的创建逻辑
    if re.search(r'(if|elif|match|switch)\s*\(|isinstance\(.*type', code_text):
        if 'return' in code_text or 'return new' in code_text or 'return ' in code_text:
            result['checks']['has_object_creation_logic'] = True
            result['patterns'].append('检测到带条件分支的对象创建逻辑')

    # 计算置信度
    checks_count = sum(1 for v in result['checks'].values() if v)
    result['confidence'] = checks_count / len(result['checks'])
    result['detected'] = result['confidence'] >= 0.75

    # 分析最佳实践
    if result['detected']:
        if 'return new' in code_text:
            result['issues'].append('避免在工厂方法中使用显式"new"关键字，使用抽象代替')

    # 推荐
    if factory_keywords and factory_count < 2:
        result['recommendations'].append('Consider implementing a centralized factory class')
    
    if result['checks']['has_product_interface'] and not result['checks']['has_concrete_products']:
        result['recommendations'].append('Add concrete product implementations')

    if factory_count > 0 and not result['checks']['has_factory_method']:
        result['recommendations'].append('Extract object creation into dedicated factory methods')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_factory_pattern(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
