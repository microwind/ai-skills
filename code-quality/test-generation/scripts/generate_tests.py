#!/usr/bin/env python3
import ast
import sys

def generate_test_template(code_string):
    '''Generate test template from Python code'''
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return f'Syntax error: {e}'

    output = 'import pytest\nfrom module_under_test import *\n\n'

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            output += f'''
def test_{node.name}():
    # Test {node.name}
    pass

def test_{node.name}_edge_cases():
    # Test edge cases for {node.name}
    pass
'''

    return output

if __name__ == '__main__':
    code = sys.stdin.read()
    tests = generate_test_template(code)
    print(tests)
