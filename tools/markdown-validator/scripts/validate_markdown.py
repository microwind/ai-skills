#!/usr/bin/env python3
import sys
import re

def validate_markdown(content):
    '''Validate Markdown file'''
    lines = content.split('\n')
    result = {
        'valid': True,
        'total_lines': len(lines),
        'issues': [],
        'warnings': [],
        'statistics': {
            'headings': 0,
            'links': 0,
            'code_blocks': 0,
            'lists': 0
        }
    }

    in_code_block = False
    for i, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result['statistics']['code_blocks'] += 1
            continue

        if in_code_block:
            continue

        # Count headings
        if re.match(r'^#{1,6}\s', line):
            result['statistics']['headings'] += 1

        # Check for broken links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
        result['statistics']['links'] += len(links)

        for text, url in links:
            if not text.strip():
                result['issues'].append({
                    'line': i,
                    'issue': 'Empty link text',
                    'text': line[:50]
                })

        # Count lists
        if re.match(r'^\s*[-*+]\s', line) or re.match(r'^\s*\d+\.\s', line):
            result['statistics']['lists'] += 1

    return result

if __name__ == '__main__':
    content = sys.stdin.read()
    result = validate_markdown(content)
    import json
    print(json.dumps(result, indent=2))
