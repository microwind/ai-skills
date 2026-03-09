#!/usr/bin/env python3
import sys
import json
import re

def validate_migration(migration_text):
    """Validate database migration"""
    result = {
        'valid': True,
        'risks': [],
        'warnings': [],
        'safety_checks': {
            'has_backup': False,
            'is_idempotent': False,
            'has_rollback': False,
            'has_downtime': False
        }
    }

    if not migration_text or not migration_text.strip():
        result['valid'] = False
        return result

    text_upper = migration_text.upper()

    if 'DROP' in text_upper:
        if 'BACKUP' not in text_upper:
            result['risks'].append('DROP without backup verification')

    if 'ALTER TABLE' in text_upper:
        if 'MODIFY COLUMN' in text_upper or 'CHANGE COLUMN' in text_upper:
            result['risks'].append('ALTER COLUMN may lock table')
            result['safety_checks']['has_downtime'] = True

    if 'IF EXISTS' in text_upper or 'IF NOT EXISTS' in text_upper:
        result['safety_checks']['is_idempotent'] = True
    else:
        result['warnings'].append('Non-idempotent migration')

    if 'ROLLBACK' in text_upper or 'DOWN' in text_upper:
        result['safety_checks']['has_rollback'] = True
    else:
        result['warnings'].append('No rollback documented')

    return result

if __name__ == '__main__':
    migration = sys.stdin.read()
    result = validate_migration(migration)
    print(json.dumps(result, indent=2))
