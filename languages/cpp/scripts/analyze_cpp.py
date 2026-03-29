#!/usr/bin/env python3
"""
Modern C++ Static Analyzer Script
Checks for RAII violations, raw pointers, pass-by-value of large objects,
lock misusage, and auto/smart pointer usage.
"""

import sys
import json
import re
from typing import TypedDict, List, Dict

class IssueDict(TypedDict):
    line: int
    type: str # 'memory', 'performance', 'concurrency', 'modernize', 'style'
    severity: str # 'CRITICAL', 'HIGH', 'WARNING', 'INFO'
    message: str
    code_snippet: str

class MetricsDict(TypedDict):
    lines_of_code: int
    classes: int
    raw_new_calls: int
    raw_delete_calls: int
    shared_ptr_count: int
    unique_ptr_count: int
    make_shared_unique: int
    auto_count: int
    threads: int

class ChecksDict(TypedDict):
    has_raw_pointers: bool
    has_pass_by_value_large_objects: bool
    has_manual_locks: bool
    has_c_style_casts: bool

class AnalysisResultDict(TypedDict):
    file: str
    metrics: MetricsDict
    issues: List[IssueDict]
    patterns: List[str]
    checks: ChecksDict

def analyze_cpp_code(code_text: str, filename: str = "stdin") -> AnalysisResultDict:
    """Analyze C++ source code for modern C++ idioms and safety."""
    lines = code_text.split('\n') if code_text else []
    
    metrics: MetricsDict = {
        'lines_of_code': len(lines),
        'classes': 0,
        'raw_new_calls': 0,
        'raw_delete_calls': 0,
        'shared_ptr_count': 0,
        'unique_ptr_count': 0,
        'make_shared_unique': 0,
        'auto_count': 0,
        'threads': 0
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
            
        # Strip single line comments
        clean_line = re.sub(r'//.*', '', line).strip()
        if not clean_line:
            continue
            
        # 1. Memory Management & Smart Pointers
        if re.search(r'\bnew\b\s+[a-zA-Z_]', clean_line):
            metrics['raw_new_calls'] += 1
            issues.append({
                'line': i,
                'type': 'memory',
                'severity': 'WARNING',
                'message': "Avoid naked 'new'. Use std::make_unique or std::make_shared for exception safety.",
                'code_snippet': clean_line
            })
            
        if re.search(r'\bdelete\b\s+', clean_line) or re.search(r'\bdelete\b\s*\[\s*\]', clean_line):
            metrics['raw_delete_calls'] += 1

        if 'std::shared_ptr' in clean_line:
            metrics['shared_ptr_count'] += 1
            patterns.add('Smart Pointers (shared)')
        if 'std::unique_ptr' in clean_line:
            metrics['unique_ptr_count'] += 1
            patterns.add('Smart Pointers (unique)')
        if 'std::make_shared' in clean_line or 'std::make_unique' in clean_line:
            metrics['make_shared_unique'] += 1
            patterns.add('Modern Allocation (make_*)')
            
        # Check for shared_ptr(new X) anti-pattern
        if re.search(r'shared_ptr\s*<[^>]+>\s*\([^)]*new\s+', clean_line):
            issues.append({
                'line': i,
                'type': 'memory',
                'severity': 'HIGH',
                'message': "Anti-pattern detected: shared_ptr(new X). Use std::make_shared for performance and safety.",
                'code_snippet': clean_line
            })

        # 2. Performance Issues
        # Range-based for loop passing by value
        if m := re.search(r'for\s*\(\s*(const\s+)?[a-zA-Z_0-9:]+\s+([a-zA-Z_0-9]+)\s*:\s*[a-zA-Z_0-9().]+\s*\)', clean_line):
            if '&' not in clean_line and 'int ' not in clean_line and 'float ' not in clean_line and 'double ' not in clean_line:
                issues.append({
                    'line': i,
                    'type': 'performance',
                    'severity': 'INFO',
                    'message': "Range-based for-loop takes element by value. Use 'const auto&' for large objects.",
                    'code_snippet': clean_line
                })
                
        # Catch by value
        if re.search(r'catch\s*\(\s*(const\s+)?[a-zA-Z_0-9:]+\s+[a-zA-Z_0-9]+\s*\)', clean_line) and '&' not in clean_line:
            issues.append({
                'line': i,
                'type': 'correctness',
                'severity': 'HIGH',
                'message': "Exception caught by value. This causes slicing. Catch by const reference instead.",
                'code_snippet': clean_line
            })

        # 3. Concurrency
        if 'std::thread' in clean_line:
            metrics['threads'] += 1
            patterns.add('C++11 Threading')
            
        if re.search(r'\.lock\s*\(\s*\)', clean_line) and 'mutex' in clean_line.lower():
            issues.append({
                'line': i,
                'type': 'concurrency',
                'severity': 'WARNING',
                'message': "Manual .lock() call detected. Use std::lock_guard or std::scoped_lock for RAII safety.",
                'code_snippet': clean_line
            })

        # 4. Modern C++ & Style Practices
        if re.search(r'\bauto\b', clean_line):
            metrics['auto_count'] += 1
            patterns.add('Type Inference (auto)')
            
        if re.search(r'\bclass\b\s+[A-Za-z0-9_]+', clean_line):
            metrics['classes'] += 1
            
        # Detect C-style casts e.g., (int)x, (Foo*)bar
        if re.search(r'\(\s*(int|long|short|char|float|double|([A-Za-z_]\w*\*))\s*\)\s*[a-zA-Z_]', clean_line):
            issues.append({
                'line': i,
                'type': 'style',
                'severity': 'INFO',
                'message': "C-style cast detected. Use static_cast, reinterpret_cast, or C++ style cast like T(x).",
                'code_snippet': clean_line
            })

    checks: ChecksDict = {
        'has_raw_pointers': metrics['raw_new_calls'] > 0 or metrics['raw_delete_calls'] > 0,
        'has_pass_by_value_large_objects': any(iss['type'] == 'performance' for iss in issues),
        'has_manual_locks': any(iss['type'] == 'concurrency' for iss in issues),
        'has_c_style_casts': any(iss['type'] == 'style' for iss in issues)
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
    result = analyze_cpp_code(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
