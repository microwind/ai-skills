#!/usr/bin/env python3
import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_generators: bool
    has_decorators: bool
    has_context_managers: bool
    has_dataclasses: bool

class ResultDict(TypedDict):
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict

def analyze_python_advanced(code_text: str) -> ResultDict:
    """Analyze Advanced Python code"""
    result: ResultDict = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_generators': False,
            'has_decorators': False,
            'has_context_managers': False,
            'has_dataclasses': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'yield ' in code_text:
        result['checks']['has_generators'] = True
        result['patterns'].append('Generator function (yield) detected')

    if re.search(r'@[A-Za-z0-9_]+', code_text):
        result['checks']['has_decorators'] = True
        result['patterns'].append('Decorator usage detected')

    if 'with ' in code_text and ' as ' in code_text:
        result['checks']['has_context_managers'] = True
        result['patterns'].append('Context Manager (with statement) detected')

    if '@dataclass' in code_text:
        result['checks']['has_dataclasses'] = True
        result['patterns'].append('Dataclass usage detected')

    if 'lambda ' in code_text:
        result['patterns'].append('Lambda function used')

    if 'eval(' in code_text or 'exec(' in code_text:
        result['issues'].append('Dangerous function eval() or exec() used - major security risk')

    if 'type(' in code_text and 'name, bases, dict' in code_text:
        result['patterns'].append('Metaclass creation pattern detected')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_python_advanced(code)
    print(json.dumps(result, indent=2))
