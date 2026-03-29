#!/usr/bin/env python3
"""
Java Language Static Analyzer Script
A comprehensive Java source code analyzer that checks for null pointer issues,
resource management, thread safety, and coding best practices.
"""

import sys
import json
import re
from typing import TypedDict, List, Dict, Any

class IssueDict(TypedDict):
    line: int
    type: str
    severity: str
    message: str
    code_snippet: str

class MetricsDict(TypedDict):
    lines_of_code: int
    classes: int
    methods: int
    try_catch_blocks: int
    synchronized_blocks: int
    resource_management_issues: int

class ChecksDict(TypedDict):
    has_null_checks: bool
    has_try_resources: bool
    has_thread_safety: bool
    has_serialization: bool

class AnalysisResultDict(TypedDict):
    file: str
    metrics: MetricsDict
    issues: List[IssueDict]
    patterns: List[str]
    checks: ChecksDict

ANTI_PATTERNS: Dict[str, dict] = {
    'NullPointerException': {'severity': 'HIGH', 'message': 'Potential null pointer dereference detected.'},
    'unchecked cast': {'severity': 'WARNING', 'message': 'Unchecked type casting detected.'},
    'raw use of parameterized class': {'severity': 'WARNING', 'message': 'Generic type parameter not specified.'},
    'serialVersionUID': {'severity': 'INFO', 'message': 'Serializable class should define serialVersionUID.'}
}

def analyze_java(code_text: str) -> AnalysisResultDict:
    """Analyze Java code"""
    result: AnalysisResultDict = {
        'file': 'analysis',
        'metrics': {
            'lines_of_code': len(code_text.split('\n')),
            'classes': len(re.findall(r'class\s+\w+', code_text)),
            'methods': len(re.findall(r'(public|private|protected)?\s+(static)?\s+\w+\s+\w+\(', code_text)),
            'try_catch_blocks': len(re.findall(r'try\s*{', code_text)),
            'synchronized_blocks': len(re.findall(r'synchronized\s*\(', code_text)),
            'resource_management_issues': 0
        },
        'issues': [],
        'patterns': [],
        'checks': {
            'has_null_checks': False,
            'has_try_resources': False,
            'has_thread_safety': False,
            'has_serialization': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    # Check for null checks
    if 'if (' in code_text and '!= null' in code_text:
        result['checks']['has_null_checks'] = True
        result['patterns'].append('Null pointer checks with conditional statements')

    # Check for try-with-resources
    if 'try (' in code_text or 'try (' in code_text:
        result['checks']['has_try_resources'] = True
        result['patterns'].append('Try-with-resources for automatic resource management')
    else:
        if 'new FileInputStream' in code_text or 'new FileOutputStream' in code_text:
            result['issues'].append('Resource management: Manual resource closing required')
            result['metrics']['resource_management_issues'] += 1

    # Check for thread safety
    if 'synchronized' in code_text:
        result['checks']['has_thread_safety'] = True
        result['patterns'].append('Synchronized blocks for thread safety')

    if 'volatile' in code_text:
        result['patterns'].append('Volatile keyword used for thread-safe field access')

    # Check for serialization
    if 'implements Serializable' in code_text:
        result['checks']['has_serialization'] = True
        if 'serialVersionUID' not in code_text:
            result['issues'].append('Serializable class missing serialVersionUID constant')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_java(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
