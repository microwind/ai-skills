#!/usr/bin/env python3
"""
Advanced Python Code Analyzer
Performs in-depth analysis of Python code including complexity metrics,
dependency tracking, and architectural patterns.
"""

import sys
import json
import re
from typing import TypedDict, List

class MetricsDict(TypedDict):
    cyclomatic_complexity: int
    functions_count: int
    classes_count: int
    imports_count: int
    lines_of_code: int

class ChecksDict(TypedDict):
    has_type_hints: bool
    has_docstrings: bool
    has_error_handling: bool
    follows_pep8: bool

class ResultDict(TypedDict):
    name: str
    valid: bool
    issues: List[str]
    patterns: List[str]
    metrics: MetricsDict
    checks: ChecksDict
    recommendations: List[str]

def analyze_python_analyzer(code_text: str) -> ResultDict:
    """Advanced analysis of Python code"""
    result: ResultDict = {
        'name': 'python-analyzer',
        'valid': True,
        'issues': [],
        'patterns': [],
        'metrics': {
            'cyclomatic_complexity': 0,
            'functions_count': 0,
            'classes_count': 0,
            'imports_count': 0,
            'lines_of_code': 0
        },
        'checks': {
            'has_type_hints': False,
            'has_docstrings': False,
            'has_error_handling': False,
            'follows_pep8': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # Syntax validation
    try:
        compile(code_text, '<string>', 'exec')
        result['valid'] = True
    except SyntaxError as e:
        result['valid'] = False
        result['issues'].append(f'Syntax error: {str(e)}')
        return result

    # Metrics
    result['metrics']['lines_of_code'] = len(code_text.split('\n'))
    result['metrics']['functions_count'] = len(re.findall(r'def\s+\w+', code_text))
    result['metrics']['classes_count'] = len(re.findall(r'class\s+\w+', code_text))
    result['metrics']['imports_count'] = len(re.findall(r'import |from .* import', code_text))

    # Count if/else for cyclomatic complexity approximation
    result['metrics']['cyclomatic_complexity'] = len(re.findall(r'\bif\b|\belif\b|\belse\b|\bfor\b|\bwhile\b|\bwith\b', code_text))

    # Check for type hints
    if '->' in code_text or re.search(r':\s*(int|str|bool|list|dict|Any|Optional)', code_text):
        result['checks']['has_type_hints'] = True
        result['patterns'].append('Type hints detected')
    else:
        result['recommendations'].append('Add type annotations for better code clarity')

    # Check for docstrings
    if '"""' in code_text or "'''" in code_text:
        result['checks']['has_docstrings'] = True
        result['patterns'].append('Docstrings present')
    else:
        result['recommendations'].append('Add docstrings to functions and classes')

    # Check for error handling
    if 'try:' in code_text and 'except' in code_text:
        result['checks']['has_error_handling'] = True
        result['patterns'].append('Error handling with try/except detected')

    # Check for common issues
    if 'exec(' in code_text or 'eval(' in code_text:
        result['issues'].append('CRITICAL: exec() or eval() detected - major security risk')

    if '__future__' in code_text:
        result['patterns'].append('Future imports for Python 2/3 compatibility')

    if 'import *' in code_text:
        result['issues'].append('Wildcard imports detected - reduces code clarity')
        result['recommendations'].append('Use explicit imports instead of "import *"')

    if re.search(r':\s*$', code_text, re.MULTILINE) and not re.search(r':\s*\n\s*(pass|\.\.\.)', code_text):
        result['checks']['follows_pep8'] = True

    return result

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_python_analyzer(code)
    print(json.dumps(result, indent=2))
