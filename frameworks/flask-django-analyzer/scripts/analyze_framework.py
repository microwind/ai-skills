#!/usr/bin/env python3
import sys
import json
import re

def analyze_framework(code_text):
    """Analyze framework code"""
    result = {
        'framework': 'unknown',
        'patterns': [],
        'issues': [],
        'best_practices': {
            'has_error_handling': False,
            'has_logging': False,
            'has_tests': False,
            'organized_views': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'from flask import' in code_text or '@app.route' in code_text:
        result['framework'] = 'Flask'
    elif 'from django' in code_text:
        result['framework'] = 'Django'

    if re.search(r'try:|except', code_text):
        result['best_practices']['has_error_handling'] = True

    if 'import logging' in code_text or 'logger.' in code_text:
        result['best_practices']['has_logging'] = True
    else:
        result['issues'].append('No logging configured')

    if re.search(r'test_|TestCase', code_text):
        result['best_practices']['has_tests'] = True

    if 'for item in items:' in code_text and '.objects.get' in code_text:
        result['issues'].append('N+1 query pattern detected')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_framework(code)
    print(json.dumps(result, indent=2))
