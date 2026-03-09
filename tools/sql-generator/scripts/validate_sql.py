#!/usr/bin/env python3
import re
import sys
import json

def validate_sql(query):
    '''Basic SQL validation'''
    issues = []

    # Check for common issues
    if '*' in query and 'SELECT' in query.upper():
        issues.append('WARNING: Wildcard SELECT found - specify columns')

    if 'DELETE' in query.upper() and 'WHERE' not in query.upper():
        issues.append('CRITICAL: DELETE without WHERE clause')

    if 'UPDATE' in query.upper() and 'WHERE' not in query.upper():
        issues.append('CRITICAL: UPDATE without WHERE clause')

    # Check for SQL injection vulnerability
    if "'" in query and '?' not in query:
        issues.append('WARNING: Possible SQL injection - use parameterized queries')

    # Check syntax
    if not query.strip().endswith(';'):
        issues.append('WARNING: Missing semicolon')

    return {
        'query': query,
        'valid': len([i for i in issues if i.startswith('CRITICAL')]) == 0,
        'issues': issues
    }

if __name__ == '__main__':
    query = sys.stdin.read()
    result = validate_sql(query)
    print(json.dumps(result, indent=2))
