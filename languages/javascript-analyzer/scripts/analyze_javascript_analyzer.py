#!/usr/bin/env python3
"""
Advanced JavaScript Code Quality Analyzer
Analyzes JavaScript code for performance issues, best practices,
and potential architectural problems.
"""

import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_linting: bool
    has_type_checking: bool
    has_performance_issues: bool
    has_security_concerns: bool

class ResultDict(TypedDict):
    name: str
    valid: bool
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict
    recommendations: List[str]

def analyze_javascript_analyzer(code_text: str) -> ResultDict:
    """Advanced analysis of JavaScript code"""
    result: ResultDict = {
        'name': 'javascript-analyzer',
        'valid': True,
        'issues': [],
        'patterns': [],
        'checks': {
            'has_linting': False,
            'has_type_checking': False,
            'has_performance_issues': False,
            'has_security_concerns': False
        },
        'recommendations': []
    }

    if not code_text or not code_text.strip():
        return result

    # Check for ESLint config
    if 'eslintrc' in code_text or 'eslint-disable' in code_text:
        result['checks']['has_linting'] = True
        result['patterns'].append('ESLint configuration detected')

    # Check for TypeScript/JSDoc
    if '@ts-check' in code_text or '/* @type' in code_text or '@param' in code_text:
        result['checks']['has_type_checking'] = True
        result['patterns'].append('Type checking via JSDoc/TypeScript')

    # Performance analysis
    if re.search(r'for\s*\(.*\sinside', code_text) or 'N+1' in code_text:
        result['checks']['has_performance_issues'] = True
        result['issues'].append('Potential N+1 query problem or nested loop inefficiency')

    if '.map(' in code_text and '.filter(' in code_text:
        result['patterns'].append('Functional programming patterns detected')

    if 'memo(' in code_text or 'useMemo' in code_text:
        result['patterns'].append('Performance optimization with memoization')

    # Security concerns
    if 'eval(' in code_text:
        result['checks']['has_security_concerns'] = True
        result['issues'].append('CRITICAL: eval() usage detected - major security risk')
        result['recommendations'].append('Replace eval() with safer alternatives')

    if 'innerHTML' in code_text:
        result['issues'].append('innerHTML used - potential XSS vulnerability. Use textContent or sanitize.')

    if 'dangerouslySetInnerHTML' in code_text:
        result['issues'].append('dangerouslySetInnerHTML detected in React code - ensure proper sanitization')

    if 'fetch(' in code_text or 'XMLHttpRequest' in code_text:
        result['patterns'].append('Network requests detected')

    # Recommendations
    if 'var ' in code_text:
        result['recommendations'].append('Use const/let instead of var for better scoping')

    if 'callback' in code_text and code_text.count('callback') > 3:
        result['recommendations'].append('Consider using async/await instead of callback hell')

    return result

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_javascript_analyzer(code)
    print(json.dumps(result, indent=2))
