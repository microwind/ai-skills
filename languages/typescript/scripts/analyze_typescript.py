#!/usr/bin/env python3
import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_interfaces: bool
    uses_any: bool
    has_generics: bool
    has_types: bool

class ResultDict(TypedDict):
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict

def analyze_typescript(code_text: str) -> ResultDict:
    """Analyze TypeScript code"""
    result: ResultDict = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_interfaces': False,
            'uses_any': False,
            'has_generics': False,
            'has_types': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'interface ' in code_text:
        result['checks']['has_interfaces'] = True
        result['patterns'].append('Interface declarations detected')

    if 'type ' in code_text:
        result['checks']['has_types'] = True
        result['patterns'].append('Type aliases detected')

    if ': any' in code_text or '<any>' in code_text or 'as any' in code_text:
        result['checks']['uses_any'] = True
        result['issues'].append('Usage of \'any\' type observed - defeats TypeScript\'s strict typing purpose')

    if re.search(r'<[A-Z]>', code_text) or re.search(r'<[a-zA-Z]+>', code_text) and 'interface' in code_text:
        result['checks']['has_generics'] = True
        result['patterns'].append('Generics utilized')

    if '@ts-ignore' in code_text:
        result['issues'].append('@ts-ignore is used - consider refactoring types instead of ignoring')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_typescript(code)
    print(json.dumps(result, indent=2))
