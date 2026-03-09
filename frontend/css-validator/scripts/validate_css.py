#!/usr/bin/env python3
import sys
import json
import re

def validate_css(css_text):
    """Validate CSS"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'metrics': {
            'selectors': 0,
            'rules': 0,
            'high_specificity': 0
        }
    }

    if not css_text or not css_text.strip():
        result['valid'] = False
        return result

    brace_count = css_text.count('{') - css_text.count('}')
    if brace_count != 0:
        result['valid'] = False
        result['errors'].append('Unmatched braces')

    result['metrics']['rules'] = len(re.findall(r'\{[^}]*\}', css_text))
    result['metrics']['selectors'] = len(re.findall(r'[^{};]+\{', css_text))

    if '!important' in css_text:
        result['warnings'].append('!important declarations present')

    if '@media' not in css_text:
        result['warnings'].append('No media queries - not responsive')

    return result

if __name__ == '__main__':
    css = sys.stdin.read()
    result = validate_css(css)
    print(json.dumps(result, indent=2))
