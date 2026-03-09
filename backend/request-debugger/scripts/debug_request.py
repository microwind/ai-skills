#!/usr/bin/env python3
import sys
import json
import re

def debug_request(request_text):
    """Debug HTTP request and response"""
    result = {
        'request': {
            'method': 'unknown',
            'url': None,
            'headers': [],
            'body': None,
            'issues': []
        },
        'response': {
            'status_code': None,
            'headers': [],
            'body': None,
            'issues': []
        },
        'summary': []
    }

    if not request_text or not request_text.strip():
        return result

    lines = request_text.split('\n')

    # Parse request line (METHOD URL HTTP/VERSION)
    if lines:
        match = re.match(r'(\w+)\s+(\S+)\s+HTTP', lines[0])
        if match:
            result['request']['method'] = match.group(1)
            result['request']['url'] = match.group(2)

    # Check for method
    if result['request']['method'].upper() not in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']:
        result['request']['issues'].append('Invalid HTTP method')

    # Parse headers
    header_lines = []
    body_start = 0
    for i, line in enumerate(lines[1:], 1):
        if ':' in line:
            header_lines.append(line)
            result['request']['headers'].append(line.strip())
        elif line.strip() == '':
            body_start = i + 1
            break

    # Check for required headers
    headers_str = ' '.join(header_lines).lower()

    if result['request']['method'] == 'POST' or result['request']['method'] == 'PUT':
        if 'content-type' not in headers_str:
            result['request']['issues'].append('Missing Content-Type header')

    if 'authorization' not in headers_str:
        result['summary'].append('No Authorization header - check if auth required')

    # Parse body
    if body_start > 0 and body_start < len(lines):
        result['request']['body'] = '\n'.join(lines[body_start:])

        # Validate JSON if present
        if 'application/json' in headers_str or '{' in result['request']['body']:
            try:
                import json as json_lib
                json_lib.loads(result['request']['body'])
            except:
                result['request']['issues'].append('Invalid JSON body')

    # Check encoding
    if 'utf-8' not in headers_str.lower():
        result['summary'].append('No explicit UTF-8 encoding specified')

    return result

if __name__ == '__main__':
    request_text = sys.stdin.read()
    result = debug_request(request_text)
    print(json.dumps(result, indent=2))
