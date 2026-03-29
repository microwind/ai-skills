#!/usr/bin/env python3
"""
C Language Static Analyzer Script
A comprehensive C source code analyzer that checks for memory leaks,
buffer overflows, concurrency issues, and coding best practices.
"""

import sys
import json
import re
from typing import TypedDict, List, Dict, Any

class IssueDict(TypedDict):
    line: int
    type: str # 'security', 'memory', 'concurrency', 'best_practice'
    severity: str # 'CRITICAL', 'HIGH', 'WARNING', 'INFO'
    message: str
    code_snippet: str

class MetricsDict(TypedDict):
    lines_of_code: int
    functions: int
    malloc_calls: int
    free_calls: int
    mutex_locks: int
    mutex_unlocks: int
    file_opens: int
    file_closes: int

class ChecksDict(TypedDict):
    has_unsafe_funcs: bool
    potential_memory_leak: bool
    potential_deadlock: bool
    potential_fd_leak: bool

class AnalysisResultDict(TypedDict):
    file: str
    metrics: MetricsDict
    issues: List[IssueDict]
    patterns: List[str]
    checks: ChecksDict

UNSAFE_FUNCS: Dict[str, dict] = {
    'gets': {'severity': 'CRITICAL', 'message': 'Buffer overflow risk: gets() used. Replace with fgets().'},
    'strcpy': {'severity': 'WARNING', 'message': 'Buffer overflow risk: strcpy() used. Replace with strncpy() or snprintf().'},
    'sprintf': {'severity': 'WARNING', 'message': 'Buffer overflow risk: sprintf() used. Replace with snprintf().'},
    'strcat': {'severity': 'WARNING', 'message': 'Buffer overflow risk: strcat() used. Replace with strncat().'},
    'system': {'severity': 'HIGH', 'message': 'Command injection risk: system() used.'}
}

def analyze_c_code(code_text: str, filename: str = "stdin") -> AnalysisResultDict:
    """Analyze C source code for safety and patterns."""
    lines = code_text.split('\n') if code_text else []
    
    metrics: MetricsDict = {
        'lines_of_code': len(lines),
        'functions': 0,
        'malloc_calls': 0,
        'free_calls': 0,
        'mutex_locks': 0,
        'mutex_unlocks': 0,
        'file_opens': 0,
        'file_closes': 0
    }
    
    issues: List[IssueDict] = []
    patterns: set[str] = set()
    
    # Simple regexes to strip comments quickly
    single_line_comment_re = re.compile(r'//.*')
    
    in_block_comment = False
    
    for i, line in enumerate(lines, 1):
        # Handle block comments roughly
        if '/*' in line:
            in_block_comment = True
        
        if in_block_comment:
            if '*/' in line:
                in_block_comment = False
            continue
            
        clean_line = single_line_comment_re.sub('', line).strip()
        if not clean_line:
            continue
            
        # 1. Unsafe Functions Check
        for func, info in UNSAFE_FUNCS.items():
            if re.search(rf'\b{func}\s*\(', clean_line):
                issues.append({
                    'line': i,
                    'type': 'security',
                    'severity': info['severity'],
                    'message': info['message'],
                    'code_snippet': clean_line
                })
                
        # 2. Memory Management Checks (malloc, calloc, realloc, free)
        if re.search(r'\b(malloc|calloc|realloc)\s*\(', clean_line):
            metrics['malloc_calls'] += 1
            patterns.add('Dynamic Memory Allocation')

        if re.search(r'\bfree\s*\(', clean_line):
            metrics['free_calls'] += 1
            if 'NULL' not in code_text and '0' not in code_text:
                patterns.add('No NULL assignment after free()')

        # 3. Concurrency Checks
        if re.search(r'\bpthread_mutex_lock\s*\(', clean_line):
            metrics['mutex_locks'] += 1
            patterns.add('POSIX Mutex Usage')
            
        if re.search(r'\bpthread_mutex_unlock\s*\(', clean_line):
            metrics['mutex_unlocks'] += 1
            
        if re.search(r'\bpthread_create\s*\(', clean_line):
            patterns.add('POSIX Threads')

        # 4. File I/O Checks
        if re.search(r'\bfopen\s*\(', clean_line) or re.search(r'\bopen\s*\(', clean_line):
            metrics['file_opens'] += 1
            
        if re.search(r'\bfclose\s*\(', clean_line) or re.search(r'\bclose\s*\(', clean_line):
            metrics['file_closes'] += 1

        # 5. Functions Detection (heuristic)
        # Matches typical function definitions, e.g. int main(int argc, char** argv) {
        if re.match(r'^\s*[A-Za-z_][A-Za-z0-9_*\s]*\s+[A-Za-z_][A-Za-z0-9_]*\s*\([^;]*\)\s*\{', clean_line):
            metrics['functions'] += 1

    # Aggregate Issues
    checks: ChecksDict = {
        'has_unsafe_funcs': any(issue['type'] == 'security' for issue in issues),
        'potential_memory_leak': metrics['malloc_calls'] > metrics['free_calls'],
        'potential_deadlock': metrics['mutex_locks'] != metrics['mutex_unlocks'],
        'potential_fd_leak': metrics['file_opens'] > metrics['file_closes']
    }
    
    if checks['potential_memory_leak']:
        issues.append({
            'line': 0,
            'type': 'memory',
            'severity': 'HIGH',
            'message': f"Possible memory leak: {metrics['malloc_calls']} allocations vs {metrics['free_calls']} frees.",
            'code_snippet': "N/A"
        })
        
    if checks['potential_deadlock']:
        issues.append({
            'line': 0,
            'type': 'concurrency',
            'severity': 'CRITICAL',
            'message': f"Possible deadlock: {metrics['mutex_locks']} unlocks vs {metrics['mutex_unlocks']} locks.",
            'code_snippet': "N/A"
        })

    if checks['potential_fd_leak']:
        issues.append({
            'line': 0,
            'type': 'resource',
            'severity': 'WARNING',
            'message': f"Possible FD leak: {metrics['file_opens']} opens vs {metrics['file_closes']} closes.",
            'code_snippet': "N/A"
        })

    return {
        'file': filename,
        'metrics': metrics,
        'issues': issues,
        'patterns': sorted(list(patterns)),
        'checks': checks
    }

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_c_code(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
