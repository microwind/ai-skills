#!/usr/bin/env python3
import sys
import json

def validate_kubernetes(manifest_text):
    """Validate Kubernetes manifest"""
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'resources': [],
        'checks': {
            'has_resource_limits': False,
            'has_health_probes': False,
            'has_image_pull_policy': False,
            'has_security_context': False
        }
    }

    if not manifest_text or not manifest_text.strip():
        result['errors'].append('Empty manifest')
        return result

    try:
        import yaml
        docs = list(yaml.safe_load_all(manifest_text))
        result['valid'] = True

        for doc in docs:
            if not doc:
                continue

            kind = doc.get('kind', 'Unknown')
            name = doc.get('metadata', {}).get('name', 'unnamed')
            result['resources'].append({'kind': kind, 'name': name})

            spec = doc.get('spec', {})
            if kind == 'Pod':
                containers = spec.get('containers', [])
                for container in containers:
                    resources = container.get('resources', {})
                    if resources.get('limits'):
                        result['checks']['has_resource_limits'] = True

                    if container.get('livenessProbe') or container.get('readinessProbe'):
                        result['checks']['has_health_probes'] = True

            if 'securityContext' in spec:
                result['checks']['has_security_context'] = True

            if kind == 'Deployment' and not spec.get('replicas'):
                result['warnings'].append(f'{name}: No explicit replicas set')

    except Exception as e:
        result['valid'] = False
        result['errors'].append(f'Error: {str(e)}')

    return result

if __name__ == '__main__':
    manifest = sys.stdin.read()
    result = validate_kubernetes(manifest)
    print(json.dumps(result, indent=2))
