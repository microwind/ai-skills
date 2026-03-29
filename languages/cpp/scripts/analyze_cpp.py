#!/usr/bin/env python3
"""
C++ Language Static Analyzer Script
A comprehensive C++ source code analyzer that checks for memory management,
RAII compliance, template safety, and modern C++ best practices.
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
    templates: int
    raw_pointers: int
    smart_pointers: int
    manual_new_delete: int

class ChecksDict(TypedDict):
    uses_smart_pointers: bool
    follows_raii: bool
    uses_stl: bool
    has_move_semantics: bool

class AnalysisResultDict(TypedDict):
    file: str
    metrics: MetricsDict
    issues: List[IssueDict]
    patterns: List[str]
    checks: ChecksDict

ANTI_PATTERNS: Dict[str, dict] = {
    'new ': {'severity': 'WARNING', 'message': 'Raw new allocation detected. Use smart pointers (unique_ptr/shared_ptr).'},
    'delete ': {'severity': 'WARNING', 'message': 'Raw delete detected. Use RAII or smart pointers.'},
    'raw pointer': {'severity': 'HIGH', 'message': 'Raw pointers detected. Consider using smart pointers.'},
    '.get()': {'severity': 'WARNING', 'message': 'Potential direct pointer access from smart pointer.'}
}

def analyze_cpp(code_text: str) -> AnalysisResultDict:
    """Analyze C++ code"""
    result: AnalysisResultDict = {
        'file': 'analysis',
        'metrics': {
            'lines_of_code': len(code_text.split('\n')),
            'classes': len(re.findall(r'class\s+\w+|struct\s+\w+', code_text)),
            'templates': len(re.findall(r'template\s*<', code_text)),
            'raw_pointers': len(re.findall(r'\w+\s*\*\s*\w+', code_text)),
            'smart_pointers': len(re.findall(r'(unique_ptr|shared_ptr)', code_text)),
            'manual_new_delete': len(re.findall(r'\bnew\b|\bdelete\b', code_text))
        },
        'issues': [],
        'patterns': [],
        'checks': {
            'uses_smart_pointers': False,
            'follows_raii': False,
            'uses_stl': False,
            'has_move_semantics': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    # Check for smart pointers
    if 'unique_ptr' in code_text or 'shared_ptr' in code_text:
        result['checks']['uses_smart_pointers'] = True
        result['patterns'].append('Smart pointers (unique_ptr/shared_ptr) for automatic memory management')

    # Check for RAII
    if '~' in code_text:
        result['checks']['follows_raii'] = True
        result['patterns'].append('RAII pattern with destructors')

    if re.search(r'new\s+\w+|delete\s+\w+', code_text):
        if result['metrics']['manual_new_delete'] > 5:
            result['issues'].append('Excessive manual new/delete. Consider using RAII/smart pointers.')

    # Check for STL usage
    if '#include <' in code_text:
        if any(stl in code_text for stl in ['vector', 'map', 'set', 'string', 'algorithm']):
            result['checks']['uses_stl'] = True
            result['patterns'].append('Standard Library containers for safer memory management')

    # Check for move semantics
    if '&&' in code_text or '::move' in code_text:
        result['checks']['has_move_semantics'] = True
        result['patterns'].append('Move semantics (rvalue references) for efficient resource transfer')

    # Check for modern C++ features
    if 'auto ' in code_text:
        result['patterns'].append('Type deduction with auto keyword')

    if 'constexpr' in code_text or 'const ' in code_text:
        result['patterns'].append('Const correctness and compile-time evaluation')

    return result

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze_cpp(code)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
