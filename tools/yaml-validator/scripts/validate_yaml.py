#!/usr/bin/env python3
import sys

def validate_yaml(content):
    '''Validate YAML syntax'''
    try:
        import yaml
        data = yaml.safe_load(content)
        return {
            'valid': True,
            'error': None,
            'data': data,
            'line_count': len(content.split('\n'))
        }
    except ImportError:
        # Fallback: basic YAML validation without pyyaml
        result = {
            'valid': True,
            'error': None,
            'warnings': [],
            'line_count': len(content.split('\n'))
        }

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for tab indentation
            if '\t' in line:
                result['warnings'].append(f'Line {i}: Contains tabs (use spaces)')
                result['valid'] = False

            # Check for unclosed quotes
            if line.count('"') % 2 != 0:
                result['warnings'].append(f'Line {i}: Unclosed double quote')

            # Check for unclosed braces
            if line.count('{') != line.count('}'):
                if line.count('[') != line.count(']'):
                    result['warnings'].append(f'Line {i}: Unclosed bracket')

        return result
    except Exception as e:
        return {
            'valid': False,
            'error': f'YAML Error: {str(e)}',
            'line_count': len(content.split('\n'))
        }

if __name__ == '__main__':
    content = sys.stdin.read()
    result = validate_yaml(content)
    import json
    print(json.dumps(result, indent=2))
