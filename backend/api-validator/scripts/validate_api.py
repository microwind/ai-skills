#!/usr/bin/env python3
import sys
import json
import re

def validate_api(api_text):
    """Validate API design and REST conventions"""
    result = {
        'valid': True,
        'endpoints': [],
        'issues': [],
        'warnings': [],
        'checks': {
            'has_versioning': False,
            'restful_methods': False,
            'consistent_naming': False,
            'error_documentation': False
        }
    }

    if not api_text or not api_text.strip():
        result['valid'] = False
        return result

    text = api_text.lower()

    # Check for endpoints
    endpoints = re.findall(r'(?:get|post|put|patch|delete)\s+[/\w\-{}]+', text, re.IGNORECASE)
    result['endpoints'] = endpoints

    # Check for RESTful methods
    methods = ['get', 'post', 'put', 'patch', 'delete']
    if any(method in text for method in methods):
        result['checks']['restful_methods'] = True

    # Check for versioning
    if '/v1/' in text or '/v2/' in text or 'version' in text:
        result['checks']['has_versioning'] = True
    else:
        result['warnings'].append('No API versioning detected')

    # Check for consistent naming
    if re.search(r'/users|/products|/orders', text):
        result['checks']['consistent_naming'] = True
    else:
        result['warnings'].append('Inconsistent resource naming')

    # Check for error documentation
    if '400' in text or '404' in text or '500' in text or 'error' in text:
        result['checks']['error_documentation'] = True
    else:
        result['issues'].append('No error codes documented')

    # Check for RPC-style endpoints
    if re.search(r'/(get|create|delete|update)\w+', text):
        result['issues'].append('RPC-style endpoints detected - use RESTful style')

    # Check for POST usage
    if 'post' not in text:
        result['warnings'].append('No POST endpoints - likely incomplete API')

    return result

if __name__ == '__main__':
    api_text = sys.stdin.read()
    result = validate_api(api_text)
    print(json.dumps(result, indent=2))
