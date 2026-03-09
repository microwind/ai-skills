#!/usr/bin/env python3
import sys
import re

def analyze_dockerfile(content):
    '''Analyze Dockerfile for issues and improvements'''
    lines = content.split('\n')
    result = {
        'total_lines': len(lines),
        'base_image': None,
        'instructions': [],
        'issues': [],
        'warnings': [],
        'suggestions': []
    }

    for i, line in enumerate(lines, 1):
        # Skip comments and empty lines
        if line.strip().startswith('#') or not line.strip():
            continue

        # Extract instructions
        match = re.match(r'^(FROM|RUN|COPY|ADD|CMD|ENTRYPOINT|EXPOSE|ENV|USER|WORKDIR|ARG|LABEL|HEALTHCHECK)', line.upper())
        if match:
            instruction = match.group(1)
            result['instructions'].append({'line': i, 'type': instruction})

            # Check for issues
            if instruction == 'FROM':
                result['base_image'] = line.split()[1] if len(line.split()) > 1 else 'unknown'
                # Check if image is pinned
                if ':' not in result['base_image'] or result['base_image'].endswith(':latest'):
                    result['warnings'].append(f'Line {i}: Base image not pinned to specific version')

            elif instruction == 'USER' and 'root' in line:
                result['warnings'].append(f'Line {i}: Running as root user')

            elif instruction == 'RUN' and '&&' not in line and len(line) > 100:
                result['suggestions'].append(f'Line {i}: Consider consolidating RUN commands')

            elif instruction == 'COPY' or instruction == 'ADD':
                if '**' in line or '*' in line:
                    result['suggestions'].append(f'Line {i}: Using wildcards - ensure .dockerignore is present')

    # Check for common issues
    has_user = any(inst['type'] == 'USER' for inst in result['instructions'])
    if not has_user:
        result['warnings'].append('No USER directive found - container runs as root')

    has_healthcheck = any(inst['type'] == 'HEALTHCHECK' for inst in result['instructions'])
    if not has_healthcheck:
        result['suggestions'].append('Consider adding HEALTHCHECK instruction')

    return result

if __name__ == '__main__':
    content = sys.stdin.read()
    result = analyze_dockerfile(content)
    import json
    print(json.dumps(result, indent=2))
