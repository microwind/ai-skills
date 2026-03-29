#!/usr/bin/env python3
import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_unsafe: bool
    uses_unwrap: bool
    has_results_options: bool
    has_lifetimes: bool

class ResultDict(TypedDict):
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict

def analyze_rust(code_text: str) -> ResultDict:
    """Analyze Rust code"""
    result: ResultDict = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_unsafe': False,
            'uses_unwrap': False,
            'has_results_options': False,
            'has_lifetimes': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'unsafe {' in code_text:
        result['checks']['has_unsafe'] = True
        result['issues'].append('unsafe block used - ensure strict safety boundary reviews')

    if '.unwrap()' in code_text:
        result['checks']['uses_unwrap'] = True
        result['issues'].append('.unwrap() used - panics on error. Prefer proper error handling via match or ?')

    if 'Result<' in code_text or 'Option<' in code_text:
        result['checks']['has_results_options'] = True
        result['patterns'].append('Result/Option monads detected for safe error/null handling')

    if re.search(r"\'[a-z]+", code_text) and not "'static" in code_text:
        result['checks']['has_lifetimes'] = True
        result['patterns'].append('Explicit lifetime annotations utilized')

    if 'mut ' in code_text:
        result['patterns'].append('Mutable bindings (mut) detected')

    if 'Rc<' in code_text or 'Arc<' in code_text:
        result['patterns'].append('Reference counted smart pointers utilized')
        
    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_rust(code)
    print(json.dumps(result, indent=2))
