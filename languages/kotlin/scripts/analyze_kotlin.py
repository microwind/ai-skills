#!/usr/bin/env python3
"""
Modern Kotlin Static Analyzer Script
Checks for Coroutine leaks (GlobalScope), threading issues (runBlocking),
unsafe nullability (!!), and basic best practices like scoping function abuse.
"""

import sys
import json
import re
from typing import TypedDict, List, Dict

class IssueDict(TypedDict):
    line: int
    type: str # 'safety', 'concurrency', 'performance', 'architecture'
    severity: str # 'CRITICAL', 'HIGH', 'WARNING', 'INFO'
    message: str
    code_snippet: str

class MetricsDict(TypedDict):
    lines_of_code: int
    classes: int
    data_classes: int
    extension_functions: int
    non_null_assertions: int
    global_scopes: int
    run_blockings: int
    vars_declared: int

class ChecksDict(TypedDict):
    has_unsafe_null_calls: bool
    has_global_scope_leak: bool
    has_blocking_calls: bool
    has_swallowed_cancellation: bool

class AnalysisResultDict(TypedDict):
    file: str
    metrics: MetricsDict
    issues: List[IssueDict]
    patterns: List[str]
    checks: ChecksDict

def analyze_kotlin_code(code_text: str, filename: str = "stdin") -> AnalysisResultDict:
    """Analyze Kotlin source code for idioms and coroutine safety."""
    lines = code_text.split('\n') if code_text else []
    
    metrics: MetricsDict = {
        'lines_of_code': len(lines),
        'classes': 0,
        'data_classes': 0,
        'extension_functions': 0,
        'non_null_assertions': 0,
        'global_scopes': 0,
        'run_blockings': 0,
        'vars_declared': 0
    }
    
    issues: List[IssueDict] = []
    patterns: set[str] = set()
    
    in_block_comment = False
    
    for i, line in enumerate(lines, 1):
        if '/*' in line:
            in_block_comment = True
            
        if in_block_comment:
            if '*/' in line:
                in_block_comment = False
            continue
            
        # Strip single-line comments
        clean_line = re.sub(r'//.*', '', line).strip()
        if not clean_line:
            continue
            
        # 1. Null Safety & Basic Idioms
        if '!!' in clean_line:
            metrics['non_null_assertions'] += 1
            issues.append({
                'line': i,
                'type': 'safety',
                'severity': 'HIGH',
                'message': "Unsafe non-null assertion '!!' detected. Can lead to NullPointerException. Use '?.' or '?:'.",
                'code_snippet': clean_line
            })

        if re.search(r'\bvar\b\s+[a-zA-Z_]', clean_line):
            metrics['vars_declared'] += 1

        # 2. Coroutines & Concurrency
        if 'GlobalScope.launch' in clean_line or 'GlobalScope.async' in clean_line:
            metrics['global_scopes'] += 1
            patterns.add('Global Coroutine Scope')
            issues.append({
                'line': i,
                'type': 'concurrency',
                'severity': 'CRITICAL',
                'message': "GlobalScope usage detected. This leads to memory/coroutine leaks as it is never cancelled. Use structured concurrency (e.g., viewModelScope, lifecycleScope).",
                'code_snippet': clean_line
            })

        if 'runBlocking' in clean_line:
            metrics['run_blockings'] += 1
            patterns.add('Blocking Coroutine Builder')
            issues.append({
                'line': i,
                'type': 'performance',
                'severity': 'WARNING',
                'message': "runBlocking call found. It blocks the underlying thread until completion. Avoid using this in production non-test code.",
                'code_snippet': clean_line
            })

        if re.search(r'catch\s*\(\s*[a-zA-Z0-9_]+\s*:\s*Exception\s*\)', clean_line):
            issues.append({
                'line': i,
                'type': 'concurrency',
                'severity': 'HIGH',
                'message': "Catching generic 'Exception' will swallow 'CancellationException', preventing coroutines from cancelling cleanly. Catch specific exceptions instead.",
                'code_snippet': clean_line
            })

        # 3. OOP & Architecture
        if re.search(r'\bclass\b\s+', clean_line) and 'data class' not in clean_line:
            metrics['classes'] += 1
        if re.search(r'\bdata\s+class\b', clean_line):
            metrics['data_classes'] += 1
            patterns.add('Data Classes')

        if re.search(r'\bfun\s+([A-Z][a-zA-Z0-9_<>]+\.)[a-zA-Z0-9_]+\(', clean_line):
            metrics['extension_functions'] += 1
            patterns.add('Extension Functions')

    checks: ChecksDict = {
        'has_unsafe_null_calls': metrics['non_null_assertions'] > 0,
        'has_global_scope_leak': metrics['global_scopes'] > 0,
        'has_blocking_calls': metrics['run_blockings'] > 0,
        'has_swallowed_cancellation': any("swallow" in iss['message'].lower() for iss in issues)
    }

    return {
        'file': filename,
        'metrics': metrics,
        'issues': issues,
        'patterns': sorted(list(patterns)),
        'checks': checks
    }

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_kotlin_code(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
