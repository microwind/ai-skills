#!/usr/bin/env python3
import sys
import json
import re

def analyze_infrastructure(config_text):
    """Analyze infrastructure"""
    result = {
        'reliability': {
            'single_points_of_failure': [],
            'redundancy_level': 'unknown',
            'failover_configured': False
        },
        'scalability': {
            'auto_scaling': False,
            'load_balancing': False,
            'horizontal_scaling': False
        },
        'recommendations': []
    }

    if not config_text or not config_text.strip():
        return result

    text = config_text.lower()

    if 'instance' in text:
        if not re.search(r'replica|cluster|asg|auto.*scaling|multi', text):
            result['reliability']['single_points_of_failure'].append('Single database')
            result['recommendations'].append('Add database replicas')

    if re.search(r'load.*balanc|alb|nlb', text):
        result['scalability']['load_balancing'] = True

    if re.search(r'auto.*scal|asg', text):
        result['scalability']['auto_scaling'] = True
    else:
        result['recommendations'].append('Configure auto-scaling')

    if re.search(r'replica|cluster|multi.*az', text):
        result['reliability']['redundancy_level'] = 'multi-instance'

    return result

if __name__ == '__main__':
    config = sys.stdin.read()
    result = analyze_infrastructure(config)
    print(json.dumps(result, indent=2))
