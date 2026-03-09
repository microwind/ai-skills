#!/usr/bin/env python3
import sys
import json

def analyze_cloud_config(config_text):
    """Analyze cloud configuration"""
    result = {
        'valid': True,
        'security_issues': [],
        'cost_optimizations': [],
        'configuration': {
            'has_encryption': False,
            'has_iam_roles': False,
            'has_backup': False,
            'has_monitoring': False
        }
    }

    if not config_text or not config_text.strip():
        result['valid'] = False
        return result

    text = config_text.lower()

    if 'public' in text and ('read' in text or 'acl' in text):
        result['security_issues'].append('Public access detected')

    if 'password' in text and '=' in text:
        if not any(k in text for k in ['kms', 'secrets', 'encrypted']):
            result['security_issues'].append('Potential hardcoded password')

    if 'encrypt' in text or 'kms' in text:
        result['configuration']['has_encryption'] = True

    if 'iam' in text or 'role' in text:
        result['configuration']['has_iam_roles'] = True

    if 'backup' in text or 'replication' in text:
        result['configuration']['has_backup'] = True

    if 'monitor' in text or 'cloudwatch' in text:
        result['configuration']['has_monitoring'] = True

    return result

if __name__ == '__main__':
    config = sys.stdin.read()
    result = analyze_cloud_config(config)
    print(json.dumps(result, indent=2))
