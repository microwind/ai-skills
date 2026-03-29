#!/usr/bin/env python3
import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    uses_const_let: bool
    has_arrow_functions: bool
    has_destructuring: bool
    has_modules: bool

class ResultDict(TypedDict):
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict

def analyze_javascript_es6(code_text: str) -> ResultDict:
    """Analyze JavaScript ES6 code"""
    result: ResultDict = {
        'issues': [],
        'patterns': [],
        'checks': {
            'uses_const_let': False,
            'has_arrow_functions': False,
            'has_destructuring': False,
            'has_modules': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'const ' in code_text or 'let ' in code_text:
        result['checks']['uses_const_let'] = True
        result['patterns'].append('Modern variable declarations (const/let) used')
    
    if 'var ' in code_text:
        result['issues'].append('Legacy var keyword used - prefer const or let')

    if '=>' in code_text:
        result['checks']['has_arrow_functions'] = True
        result['patterns'].append('Arrow functions used')

    if re.search(r'(const|let|var)\s+\{[^}]+\}\s*=', code_text) or re.search(r'(const|let|var)\s+\[[^\]]+\]\s*=', code_text):
        result['checks']['has_destructuring'] = True
        result['patterns'].append('Destructuring assignment used')

    if 'import ' in code_text and 'from ' in code_text or 'export ' in code_text:
        result['checks']['has_modules'] = True
        result['patterns'].append('ES6 Module syntax (import/export) used')

    if 'class ' in code_text and 'constructor' in code_text:
        result['patterns'].append('ES6 Class syntax used')

    if '...[' in code_text or '...{' in code_text or re.search(r'\.\.\.[a-zA-Z]', code_text):
        result['patterns'].append('Spread/Rest operator (...) used')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_javascript_es6(code)
    print(json.dumps(result, indent=2))
