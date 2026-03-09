#!/usr/bin/env python3
import sys
import json
import re

def validate_cicd(pipeline_text):
    """Validate CI/CD pipeline"""
    result = {
        'valid': False,
        'pipeline_type': 'unknown',
        'stages': [],
        'checks': {
            'has_tests': False,
            'has_build': False,
            'has_deploy': False,
            'has_approval': False
        },
        'issues': []
    }

    if not pipeline_text or not pipeline_text.strip():
        return result

    text = pipeline_text.lower()

    if 'github' in text or '.github' in pipeline_text:
        result['pipeline_type'] = 'GitHub Actions'
    elif 'gitlab' in text:
        result['pipeline_type'] = 'GitLab CI'

    if re.search(r'test|pytest|jest', text):
        result['checks']['has_tests'] = True
        result['stages'].append('tests')

    if re.search(r'build|docker|npm.*build', text):
        result['checks']['has_build'] = True
        result['stages'].append('build')

    if re.search(r'deploy|kubernetes|helm', text):
        result['checks']['has_deploy'] = True
        result['stages'].append('deploy')

    if re.search(r'approval|manual', text):
        result['checks']['has_approval'] = True
        result['stages'].append('approval')

    if result['stages']:
        result['valid'] = True

    if not result['checks']['has_tests']:
        result['issues'].append('No test stage')

    if not result['checks']['has_approval'] and result['checks']['has_deploy']:
        result['issues'].append('No approval gate before deployment')

    if 'password' in pipeline_text or 'secret' in text:
        result['issues'].append('Credentials may be exposed')

    return result

if __name__ == '__main__':
    pipeline = sys.stdin.read()
    result = validate_cicd(pipeline)
    print(json.dumps(result, indent=2))
