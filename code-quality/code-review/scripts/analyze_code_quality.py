#!/usr/bin/env python3
import ast
import sys

def analyze_code(code_string):
    '''Analyze code structure and return metrics'''
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return {'error': f'Syntax error: {e}'}

    metrics = {
        'functions': 0,
        'classes': 0,
        'imports': 0,
        'lines': len(code_string.split('\n')),
        'issues': []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            metrics['functions'] += 1
            # Check function length
            if node.end_lineno - node.lineno > 50:
                metrics['issues'].append(f"Long function: {node.name} ({node.end_lineno - node.lineno} lines)")

        elif isinstance(node, ast.ClassDef):
            metrics['classes'] += 1

        elif isinstance(node, ast.Import):
            metrics['imports'] += 1

    return metrics

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_code(code)
    import json
    print(json.dumps(result, indent=2))
