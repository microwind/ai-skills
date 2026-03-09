#!/usr/bin/env python3
import sys
import json
import re

def analyze_python(code_text):
    """Analyze Python code"""
    result = {
        'valid': False,
        'issues': [],
        'patterns': [],
        'metrics': {
            'has_type_hints': False,
            'has_docstrings': False,
            'has_error_handling': False,
            'functions_count': 0
        }
    }

    if not code_text or not code_text.strip():
        return result

    try:
        compile(code_text, '<string>', 'exec')
        result['valid'] = True
    except SyntaxError as e:
        result['issues'].append(f'Syntax error: {str(e)}')
        return result

    if '->' in code_text or ': int' in code_text:
        result['metrics']['has_type_hints'] = True
    else:
        result['issues'].append('No type hints')

    result['metrics']['functions_count'] = len(re.findall(r'def ', code_text))

    if 'try:' in code_text:
        result['metrics']['has_error_handling'] = True

    if 'except:' in code_text:
        result['issues'].append('Bare except clause - specify exception')

    if 'import logging' in code_text:
        result['patterns'].append('Logging configured')
    elif 'print(' in code_text:
        result['issues'].append('Using print - use logging')

    if '=[]' in code_text and 'def ' in code_text:
        result['issues'].append('Mutable default argument')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_python(code)
    print(json.dumps(result, indent=2))
