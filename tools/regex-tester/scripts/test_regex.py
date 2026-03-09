#!/usr/bin/env python3
import re
import sys
import json

def test_regex(pattern, test_cases):
    '''Test regex pattern against test cases'''
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return {'error': f'Invalid regex: {e}'}

    results = {
        'pattern': pattern,
        'valid_matches': [],
        'invalid_matches': [],
        'errors': []
    }

    for test in test_cases:
        if regex.search(test):
            results['valid_matches'].append(test)
        else:
            results['invalid_matches'].append(test)

    return results

def explain_regex(pattern):
    '''Explain what a regex does'''
    explanations = {
        '^': 'Start of string',
        '$': 'End of string',
        '.': 'Any character',
        '*': 'Zero or more',
        '+': 'One or more',
        '?': 'Zero or one',
        '\\w': 'Word character [a-zA-Z0-9_]',
        '\\d': 'Digit [0-9]',
        '\\s': 'Whitespace',
        '[]': 'Character class',
        '()': 'Capture group',
        '|': 'OR',
    }
    return explanations

if __name__ == '__main__':
    # Example usage
    pattern = sys.argv[1] if len(sys.argv) > 1 else '^[a-z]+$'
    test_cases = ['hello', 'Hello', '123', 'world']

    result = test_regex(pattern, test_cases)
    print(json.dumps(result, indent=2))
