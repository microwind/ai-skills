#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path

def validate_env_file(env_file='.env'):
    '''Validate environment file'''
    if not Path(env_file).exists():
        return {'error': f'{env_file} not found'}

    env_vars = {}
    issues = []

    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                env_vars[key] = value

                # Check for exposed secrets
                if any(secret in key for secret in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                    if len(value) > 4 and not value.startswith('***'):
                        issues.append(f'WARNING: {key} might be exposed')

    return {
        'env_file': env_file,
        'variables': len(env_vars),
        'issues': issues,
        'keys': list(env_vars.keys())
    }

if __name__ == '__main__':
    result = validate_env_file()
    print(json.dumps(result, indent=2))
