#!/usr/bin/env python3
"""
Modern Java Static Analyzer Script
Focuses on Java 17/21 patterns, memory leak detection (ThreadLocal, collections),
Spring Boot anti-patterns (Field Injection), and concurrency (synchronized pinning virtual threads).
"""

import sys
import json
import re
from typing import TypedDict, List, Dict

class IssueDict(TypedDict):
    line: int
    type: str # 'memory', 'performance', 'concurrency', 'architecture', 'security'
    severity: str # 'CRITICAL', 'HIGH', 'WARNING', 'INFO'
    message: str
    code_snippet: str

class MetricsDict(TypedDict):
    lines_of_code: int
    classes: int
    records: int
    autowired_fields: int
    synchronized_blocks: int
    threadlocals: int
    catch_exceptions: int

class ChecksDict(TypedDict):
    has_legacy_date: bool
    has_field_injection: bool
    has_synchronized_keyword: bool
    potential_threadlocal_leak: bool
    has_empty_catch: bool

class AnalysisResultDict(TypedDict):
    file: str
    metrics: MetricsDict
    issues: List[IssueDict]
    patterns: List[str]
    checks: ChecksDict

def analyze_java_code(code_text: str, filename: str = "stdin") -> AnalysisResultDict:
    """Analyze Java & Spring source code."""
    lines = code_text.split('\n') if code_text else []
    
    metrics: MetricsDict = {
        'lines_of_code': len(lines),
        'classes': 0,
        'records': 0,
        'autowired_fields': 0,
        'synchronized_blocks': 0,
        'threadlocals': 0,
        'catch_exceptions': 0
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
            
        # 1. OOP & Modern Structures (Java 14+)
        if re.search(r'\bclass\b\s+[A-Za-z0-9_]+', clean_line):
            metrics['classes'] += 1
        if re.search(r'\brecord\b\s+[A-Za-z0-9_]+', clean_line):
            metrics['records'] += 1
            patterns.add('Modern Data Class (record)')
            
        if re.search(r'\bjava\.util\.Date\b', clean_line) or re.search(r'\bnew\s+Date\(\)', clean_line):
            issues.append({
                'line': i,
                'type': 'modernization',
                'severity': 'INFO',
                'message': "Legacy java.util.Date detected. Use java.time.LocalDateTime or ZonedDateTime for thread safety.",
                'code_snippet': clean_line
            })

        # 2. Spring Boot Architecture Patterns
        if '@Autowired' in clean_line:
            # Check next line heuristically to see if it's applied on a field
            if i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith(('private', 'protected', 'public')) and '(' not in next_line:
                    metrics['autowired_fields'] += 1
                    patterns.add('Spring Field Injection (Anti-Pattern)')
                    issues.append({
                        'line': i,
                        'type': 'architecture',
                        'severity': 'WARNING',
                        'message': "Field injection with @Autowired is an anti-pattern. Use constructor injection with final fields.",
                        'code_snippet': f"@Autowired\n{next_line}"
                    })

        # 3. Concurrency & Virtual Threads (Java 21)
        if 'synchronized' in clean_line:
            metrics['synchronized_blocks'] += 1
            patterns.add('Monitor Lock (synchronized)')
            issues.append({
                'line': i,
                'type': 'concurrency',
                'severity': 'WARNING',
                'message': "synchronized keyword identified. If wrapping blocking I/O, it causes Virtual Thread Pinning in Java 21+. Consider using ReentrantLock.",
                'code_snippet': clean_line
            })

        if re.search(r'\bCompletableFuture\.supplyAsync\b', clean_line) and 'Executor' not in code_text:
            issues.append({
                'line': i,
                'type': 'performance',
                'severity': 'WARNING',
                'message': "CompletableFuture used without custom Executor. Defaults to ForkJoinPool.commonPool() which might lead to thread starvation.",
                'code_snippet': clean_line
            })

        # 4. Memory Leaks (ThreadLocal)
        if 'ThreadLocal' in clean_line:
            metrics['threadlocals'] += 1
            patterns.add('Thread-Local Storage')

        # 5. Exception Handling
        if re.search(r'catch\s*\([^)]+\)\s*{\s*}', clean_line):
            metrics['catch_exceptions'] += 1
            issues.append({
                'line': i,
                'type': 'security',
                'severity': 'HIGH',
                'message': "Swallowed exception (empty catch block). At minimum, log the exception or re-throw.",
                'code_snippet': clean_line
            })
            
        if 'e.printStackTrace()' in clean_line:
            issues.append({
                'line': i,
                'type': 'best_practice',
                'severity': 'INFO',
                'message': "Using e.printStackTrace() is discouraged in enterprise apps. Use a logger like SLF4J: log.error(\"Context\", e).",
                'code_snippet': clean_line
            })

    checks: ChecksDict = {
        'has_legacy_date': any('java.util.Date' in iss['message'] for iss in issues),
        'has_field_injection': metrics['autowired_fields'] > 0,
        'has_synchronized_keyword': metrics['synchronized_blocks'] > 0,
        'potential_threadlocal_leak': metrics['threadlocals'] > 0 and 'remove()' not in code_text,
        'has_empty_catch': metrics['catch_exceptions'] > 0
    }

    if checks['potential_threadlocal_leak']:
        issues.append({
            'line': 0,
            'type': 'memory',
            'severity': 'CRITICAL',
            'message': f"ThreadLocal allocation detected without a corresponding .remove() call. This causes severe memory leaks in Thread Pools (e.g., Tomcat).",
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
    result = analyze_java_code(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
