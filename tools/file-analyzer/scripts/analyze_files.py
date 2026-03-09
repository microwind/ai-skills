#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from collections import defaultdict

def analyze_directory(root_path='.'):
    '''Analyze directory structure and file sizes'''
    result = {
        'total_size': 0,
        'total_files': 0,
        'largest_files': [],
        'file_types': defaultdict(int),
        'directories': {}
    }

    try:
        for root, dirs, files in os.walk(root_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    result['total_size'] += size
                    result['total_files'] += 1

                    # Track largest files
                    result['largest_files'].append({
                        'path': file_path,
                        'size': size
                    })

                    # Track file types
                    ext = os.path.splitext(file)[1] or 'no_extension'
                    result['file_types'][ext] += 1

                except (OSError, IOError):
                    pass

        # Sort largest files
        result['largest_files'] = sorted(
            result['largest_files'],
            key=lambda x: x['size'],
            reverse=True
        )[:10]

    except Exception as e:
        result['error'] = str(e)

    result['file_types'] = dict(result['file_types'])
    return result

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    analysis = analyze_directory(path)
    import json
    print(json.dumps(analysis, indent=2, default=str))
