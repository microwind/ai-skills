#!/usr/bin/env python3
import sys
import re

def format_python_code(code):
    '''Basic Python code formatting'''
    lines = code.split('\n')
    formatted = []

    for line in lines:
        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith('#'):
            formatted.append(line)
            continue

        # Fix spacing around operators
        formatted_line = re.sub(r'(\w)([+\-*/=])(\w)', r'\1 \2 \3', line)

        # Fix spacing after commas
        formatted_line = re.sub(r',([^ ])', r', \1', formatted_line)

        formatted.append(formatted_line)

    return '\n'.join(formatted)

if __name__ == '__main__':
    code = sys.stdin.read()
    formatted = format_python_code(code)
    print(formatted)
