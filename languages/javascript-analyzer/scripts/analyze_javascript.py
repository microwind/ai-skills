#!/usr/bin/env python3
import sys
import json
import re

def analyze_javascript(code_text):
    """Analyze JavaScript code"""
    result = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_async_await': False,
            'has_error_handling': False,
            'has_comments': False,
            'uses_const_let': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'async ' in code_text or 'await ' in code_text:
        result['checks']['has_async_await'] = True
    elif '.then(' in code_text:
        result['patterns'].append('Promise chains detected')

    if 'try' in code_text or 'catch' in code_text:
        result['checks']['has_error_handling'] = True
    else:
        result['issues'].append('No error handling')

    if '//' in code_text or '/*' in code_text:
        result['checks']['has_comments'] = True

    if 'var ' in code_text:
        result['issues'].append('Using var - use const/let')
    else:
        result['checks']['uses_const_let'] = True

    if 'console.log' in code_text:
        result['issues'].append('console.log in production code')

    if 'addEventListener' in code_text:
        if 'removeEventListener' not in code_text:
            result['issues'].append('Event listeners not cleaned up')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_javascript(code)
    print(json.dumps(result, indent=2))
