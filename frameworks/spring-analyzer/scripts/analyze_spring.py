#!/usr/bin/env python3
import sys
import json
import re

def analyze_spring(code_text):
    """Analyze Spring code"""
    result = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_dependency_injection': False,
            'has_exception_handling': False,
            'has_transaction_management': False,
            'has_logging': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if '@Autowired' in code_text or '@Inject' in code_text:
        result['checks']['has_dependency_injection'] = True
    else:
        result['issues'].append('No dependency injection detected')

    if '@Service' in code_text or '@Repository' in code_text:
        result['patterns'].append('Spring stereotypes found')

    if 'try {' in code_text:
        result['checks']['has_exception_handling'] = True

    if '@Transactional' in code_text:
        result['checks']['has_transaction_management'] = True

    if 'Logger' in code_text or 'log.' in code_text:
        result['checks']['has_logging'] = True

    if re.search(r'new\s+\w+Service', code_text):
        result['issues'].append('Manual object creation - use DI')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_spring(code)
    print(json.dumps(result, indent=2))
