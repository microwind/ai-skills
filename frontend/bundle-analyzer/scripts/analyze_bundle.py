#!/usr/bin/env python3
import sys
import json
import re

def analyze_bundle(manifest_text):
    """Analyze bundle"""
    result = {
        'total_size_estimate': 0,
        'issues': [],
        'optimizations': [],
        'splits_found': 0,
        'large_modules': []
    }

    if not manifest_text or not manifest_text.strip():
        return result

    text = manifest_text.lower()

    if 'lodash' in text:
        result['issues'].append('Lodash detected - use cherry-pick or date-fns')

    if 'moment' in text:
        result['issues'].append('Moment.js is large - use date-fns')

    if 'dynamic import' in text or 'lazy' in text:
        result['splits_found'] += 1

    if result['splits_found'] == 0:
        result['optimizations'].append('Implement code splitting')

    return result

if __name__ == '__main__':
    manifest = sys.stdin.read()
    result = analyze_bundle(manifest)
    print(json.dumps(result, indent=2))
