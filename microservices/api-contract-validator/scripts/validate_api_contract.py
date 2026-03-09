#!/usr/bin/env python3
import sys
import json

def validate_api_contract(contract_text):
    """Validate API contract"""
    result = {
        'valid': False,
        'format': 'unknown',
        'endpoints': [],
        'issues': [],
        'checks': {
            'has_request_schema': False,
            'has_response_schema': False,
            'has_status_codes': False,
            'has_examples': False
        }
    }

    if not contract_text or not contract_text.strip():
        return result

    if 'openapi' in contract_text.lower():
        result['format'] = 'OpenAPI'
    elif 'swagger' in contract_text.lower():
        result['format'] = 'Swagger'

    try:
        import yaml
        contract = yaml.safe_load(contract_text)
        result['valid'] = True

        if 'paths' in contract:
            result['endpoints'] = list(contract['paths'].keys())

        if 'components' in contract and 'schemas' in contract['components']:
            result['checks']['has_request_schema'] = True
            result['checks']['has_response_schema'] = True

        if 'responses' in contract_text:
            result['checks']['has_status_codes'] = True

        if 'example' in contract_text.lower():
            result['checks']['has_examples'] = True
        else:
            result['issues'].append('No examples provided')

        if 'version' not in contract_text:
            result['issues'].append('No API version specified')

    except Exception as e:
        result['valid'] = False
        result['issues'].append(f'YAML error: {str(e)}')

    return result

if __name__ == '__main__':
    contract = sys.stdin.read()
    result = validate_api_contract(contract)
    print(json.dumps(result, indent=2))
