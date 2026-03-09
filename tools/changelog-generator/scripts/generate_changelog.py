#!/usr/bin/env python3
import sys
import subprocess
import re
from collections import defaultdict

def generate_changelog():
    '''Generate changelog from git history'''
    result = {
        'version': None,
        'changes_by_type': defaultdict(list),
        'total_commits': 0
    }

    try:
        # Get commits since last tag
        output = subprocess.check_output(
            ['git', 'log', '--oneline', '--all'],
            stderr=subprocess.DEVNULL
        ).decode()

        commits = output.strip().split('\n')
        result['total_commits'] = len(commits)

        # Categorize commits
        for commit in commits:
            if 'feat:' in commit.lower():
                result['changes_by_type']['feat'].append(commit)
            elif 'fix:' in commit.lower():
                result['changes_by_type']['fix'].append(commit)
            elif 'docs:' in commit.lower():
                result['changes_by_type']['docs'].append(commit)
            else:
                result['changes_by_type']['other'].append(commit)

    except Exception as e:
        result['error'] = str(e)

    result['changes_by_type'] = dict(result['changes_by_type'])
    return result

if __name__ == '__main__':
    changelog = generate_changelog()
    import json
    print(json.dumps(changelog, indent=2, default=str))
