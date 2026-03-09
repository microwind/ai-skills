#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path

def analyze_git_repo(repo_path='.'):
    result = {
        'commits': 0,
        'authors': set(),
        'branches': [],
        'recent_activity': None
    }

    try:
        # Count commits
        output = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'],
                                       cwd=repo_path).decode().strip()
        result['commits'] = int(output)

        # Get authors
        output = subprocess.check_output(['git', 'log', '--format=%an'],
                                       cwd=repo_path).decode().strip()
        result['authors'] = len(set(output.split('\n')))

        # Get branches
        output = subprocess.check_output(['git', 'branch', '-a'],
                                       cwd=repo_path).decode().strip()
        result['branches'] = [b.strip() for b in output.split('\n')]

        return result
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    analysis = analyze_git_repo(path)
    print(json.dumps({k: (list(v) if isinstance(v, set) else v) for k, v in analysis.items()}, indent=2))
