#!/usr/bin/env python3
import sys
import re
from collections import defaultdict
from datetime import datetime

def analyze_log_file(content):
    '''Analyze log content and extract patterns'''
    lines = content.strip().split('\n')
    result = {
        'total_lines': len(lines),
        'log_levels': defaultdict(int),
        'errors': [],
        'warnings': [],
        'patterns': {},
        'timestamps': {'first': None, 'last': None}
    }

    # Define log patterns
    patterns = {
        'ERROR': re.compile(r'ERROR|Exception|Traceback', re.IGNORECASE),
        'WARN': re.compile(r'WARN|WARNING', re.IGNORECASE),
        'INFO': re.compile(r'INFO', re.IGNORECASE),
        'DEBUG': re.compile(r'DEBUG', re.IGNORECASE)
    }

    # Track error types
    error_types = defaultdict(int)

    for i, line in enumerate(lines):
        # Determine log level
        found_level = False
        for level, pattern in patterns.items():
            if pattern.search(line):
                result['log_levels'][level] += 1
                found_level = True

                # Capture errors
                if level == 'ERROR':
                    result['errors'].append({
                        'line_number': i + 1,
                        'message': line[:200]
                    })
                    # Extract error type
                    if 'timeout' in line.lower():
                        error_types['Timeout'] += 1
                    elif 'connection' in line.lower():
                        error_types['Connection'] += 1
                    elif 'memory' in line.lower():
                        error_types['Memory'] += 1
                    elif 'database' in line.lower():
                        error_types['Database'] += 1

                if level == 'WARN':
                    result['warnings'].append({
                        'line_number': i + 1,
                        'message': line[:200]
                    })
                break

        if not found_level:
            result['log_levels']['OTHER'] += 1

    # Convert defaultdict to dict for JSON serialization
    result['log_levels'] = dict(result['log_levels'])
    result['error_types'] = dict(error_types)

    return result

if __name__ == '__main__':
    content = sys.stdin.read()
    result = analyze_log_file(content)
    import json
    print(json.dumps(result, indent=2))
