#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def validate_json(content):
    '''Validate JSON syntax and structure'''
    result = {
        'valid': False,
        'error': None,
        'data': None,
        'stats': {
            'objects': 0,
            'arrays': 0,
            'strings': 0,
            'numbers': 0,
            'booleans': 0,
            'nulls': 0
        }
    }

    try:
        data = json.loads(content)
        result['valid'] = True
        result['data'] = data

        # Count elements
        def count_elements(obj):
            if isinstance(obj, dict):
                result['stats']['objects'] += 1
                for v in obj.values():
                    count_elements(v)
            elif isinstance(obj, list):
                result['stats']['arrays'] += 1
                for item in obj:
                    count_elements(item)
            elif isinstance(obj, str):
                result['stats']['strings'] += 1
            elif isinstance(obj, (int, float)):
                result['stats']['numbers'] += 1
            elif isinstance(obj, bool):
                result['stats']['booleans'] += 1
            elif obj is None:
                result['stats']['nulls'] += 1

        count_elements(data)

    except json.JSONDecodeError as e:
        result['error'] = f'JSON Error at line {e.lineno}, col {e.colno}: {e.msg}'
    except Exception as e:
        result['error'] = f'Error: {str(e)}'

    return result

def format_json(content, indent=2):
    '''Format JSON with proper indentation'''
    try:
        data = json.loads(content)
        return json.dumps(data, indent=indent, sort_keys=True)
    except Exception as e:
        return f'Error: {str(e)}'

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--format':
        content = sys.stdin.read()
        print(format_json(content))
    else:
        content = sys.stdin.read()
        result = validate_json(content)
        import json as j
        print(j.dumps(result, indent=2))
