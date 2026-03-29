#!/usr/bin/env python3
import sys
import json
import re
from typing import TypedDict, List

class ChecksDict(TypedDict):
    has_goroutines: bool
    has_channels: bool
    has_defer: bool
    ignores_errors: bool

class ResultDict(TypedDict):
    issues: List[str]
    patterns: List[str]
    checks: ChecksDict

def analyze_golang(code_text: str) -> ResultDict:
    """Analyze Golang code"""
    result: ResultDict = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_goroutines': False,
            'has_channels': False,
            'has_defer': False,
            'ignores_errors': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'go func' in code_text or re.search(r'go\s+[A-Za-z]', code_text):
        result['checks']['has_goroutines'] = True
        result['patterns'].append('Goroutines (go keyword) for concurrent execution')

    if 'chan ' in code_text or '<-chan' in code_text or 'chan<-' in code_text or 'make(chan' in code_text:
        result['checks']['has_channels'] = True
        result['patterns'].append('Channels detected for concurrency synchronization')

    if 'defer ' in code_text:
        result['checks']['has_defer'] = True
        result['patterns'].append('defer statements utilized for resource cleanup')

    if '_ = err' in code_text or '_, err :=' in code_text and 'err == nil' not in code_text:
        result['checks']['ignores_errors'] = True
        result['issues'].append('Errors are being explicitly ignored using blank identifier (_) or unhandled err')

    if 'interface{}' in code_text:
        result['issues'].append('interface{} found - empty interfaces reduce type safety (maybe use generic any or strict types)')

    if 'sync.Mutex' in code_text or 'sync.RWMutex' in code_text:
        result['patterns'].append('sync.Mutex used for manual lock-based synchronization')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_golang(code)
    print(json.dumps(result, indent=2))
