#!/usr/bin/env python3
import sys
import json

def analyze_service_mesh(config_text):
    """Analyze service mesh"""
    result = {
        'valid': False,
        'mesh_type': 'unknown',
        'configuration': {
            'mtls_enabled': False,
            'circuit_breaker': False,
            'timeout_configured': False,
            'retry_policy': False
        },
        'issues': []
    }

    if not config_text or not config_text.strip():
        return result

    text = config_text.lower()

    if 'istio' in text:
        result['mesh_type'] = 'Istio'
    elif 'linkerd' in text:
        result['mesh_type'] = 'Linkerd'

    try:
        import yaml
        config = yaml.safe_load(config_text)
        result['valid'] = True

        if any(k in text for k in ['mtls', 'tls', 'certificate']):
            result['configuration']['mtls_enabled'] = True
        else:
            result['issues'].append('mTLS not configured')

        if 'circuitbreaker' in text or 'outlier' in text:
            result['configuration']['circuit_breaker'] = True
        else:
            result['issues'].append('No circuit breaker')

        if 'timeout' in text:
            result['configuration']['timeout_configured'] = True
        else:
            result['issues'].append('No timeout configured')

        if 'retry' in text:
            result['configuration']['retry_policy'] = True

    except Exception:
        result['valid'] = False
        result['issues'].append('YAML parsing error')

    return result

if __name__ == '__main__':
    config = sys.stdin.read()
    result = analyze_service_mesh(config)
    print(json.dumps(result, indent=2))
