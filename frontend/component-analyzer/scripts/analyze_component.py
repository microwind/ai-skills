#!/usr/bin/env python3
import sys
import json
import re

def analyze_component(code_text):
    """Analyze component"""
    result = {
        'framework': 'unknown',
        'issues': [],
        'patterns': [],
        'metrics': {
            'lines': 0,
            'state_count': 0,
            'prop_count': 0,
            'has_tests': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    result['metrics']['lines'] = len(code_text.split('\n'))

    if 'useState' in code_text or 'useEffect' in code_text:
        result['framework'] = 'React'
    elif '@Component' in code_text:
        result['framework'] = 'Vue'

    result['metrics']['state_count'] = len(re.findall(r'useState|this\.state', code_text))
    result['metrics']['prop_count'] = len(re.findall(r'props\.', code_text))

    if result['metrics']['state_count'] > 5:
        result['issues'].append('Too much state')

    if result['metrics']['prop_count'] > 10:
        result['issues'].append('Too many props - consider context')

    if 'React.memo' in code_text or 'useMemo' in code_text:
        result['patterns'].append('Memoization used')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_component(code)
    print(json.dumps(result, indent=2))
