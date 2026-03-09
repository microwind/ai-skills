#!/usr/bin/env python3
import sys
import re

def scan_security_issues(code):
    '''Scan code for common security issues'''
    issues = []

    # SQL injection patterns
    if re.search(r"(SELECT|INSERT|UPDATE|DELETE).*['\"]\s*\+", code, re.IGNORECASE):
        issues.append({
            'severity': 'CRITICAL',
            'type': 'SQL_INJECTION',
            'message': 'Possible SQL injection detected'
        })

    # Hardcoded credentials
    patterns = [
        (r'password\s*=\s*['\"]', 'HARDCODED_PASSWORD'),
        (r'api_key\s*=\s*['\"]', 'HARDCODED_API_KEY'),
        (r'secret\s*=\s*['\"]', 'HARDCODED_SECRET'),
    ]

    for pattern, issue_type in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append({
                'severity': 'CRITICAL',
                'type': issue_type,
                'message': f'{issue_type} detected'
            })

    # Unsafe eval/exec
    if re.search(r'\b(eval|exec)\s*\(', code):
        issues.append({
            'severity': 'CRITICAL',
            'type': 'UNSAFE_EVAL',
            'message': 'Use of eval/exec detected'
        })

    # Weak cryptography
    if re.search(r'(md5|sha1)', code, re.IGNORECASE):
        issues.append({
            'severity': 'HIGH',
            'type': 'WEAK_CRYPTO',
            'message': 'Weak cryptographic algorithm detected'
        })

    return issues

if __name__ == '__main__':
    code = sys.stdin.read()
    issues = scan_security_issues(code)
    import json
    print(json.dumps(issues, indent=2))
