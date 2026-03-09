#!/usr/bin/env python3
import sys
import re

def validate_semver(version):
    '''Validate semantic version format'''
    pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'

    return bool(re.match(pattern, version))

def parse_version(version):
    '''Parse version string'''
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-(.*?))?(?:\+(.+))?$', version)
    if not match:
        return None

    return {
        'major': int(match.group(1)),
        'minor': int(match.group(2)),
        'patch': int(match.group(3)),
        'prerelease': match.group(4),
        'metadata': match.group(5)
    }

if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else '1.0.0'

    parsed = parse_version(version)
    result = {
        'version': version,
        'valid': validate_semver(version),
        'parsed': parsed
    }

    import json
    print(json.dumps(result, indent=2))
