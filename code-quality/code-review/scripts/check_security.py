#!/usr/bin/env python3
import re
import sys

def check_security_issues(code):
    '''Check for common security vulnerabilities'''
    issues = []

    # SQL Injection patterns
    if re.search(r"SELECT.*FROM.*WHERE.*['\"]{1}\s*\+", code):
        issues.append({'type': 'SQL_INJECTION', 'msg': 'Possible SQL injection detected'})

    # Hardcoded secrets
    if re.search(r"(password|secret|api_key|token)\s*=\s*['"]", code, re.IGNORECASE):
        issues.append({'type': 'HARDCODED_SECRET', 'msg': 'Possible hardcoded secret found'})

    # Eval/exec
    if re.search(r"\b(eval|exec|compile)\s*\(", code):
        issues.append({'type': 'DANGEROUS_FUNCTION', 'msg': 'Use of eval/exec detected'})

    return issues

if __name__ == '__main__':
    code = sys.stdin.read()
    issues = check_security_issues(code)
    import json
    print(json.dumps(issues, indent=2))
