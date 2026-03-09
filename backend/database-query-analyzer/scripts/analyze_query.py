#!/usr/bin/env python3
import sys
import json
import re

def analyze_query(sql):
    """Analyze SQL query for performance issues"""
    result = {
        'valid': False,
        'issues': [],
        'warnings': [],
        'suggestions': [],
        'metrics': {
            'has_where': False,
            'has_limit': False,
            'index_candidates': [],
            'n_plus_one_risk': False,
            'full_scan_risk': False
        }
    }

    if not sql or not sql.strip():
        return result

    sql_upper = sql.upper()

    # Check SELECT * warning
    if 'SELECT *' in sql_upper:
        result['warnings'].append('SELECT * without specific columns')
        result['suggestions'].append('Specify only needed columns')

    # Check for WHERE clause
    if 'WHERE' in sql_upper:
        result['metrics']['has_where'] = True
    else:
        result['issues'].append('No WHERE clause - may scan entire table')
        result['metrics']['full_scan_risk'] = True

    # Check for LIMIT
    if 'LIMIT' in sql_upper:
        result['metrics']['has_limit'] = True
    else:
        if 'SELECT' in sql_upper:
            result['warnings'].append('No LIMIT - could return many rows')

    if 'SELECT' in sql_upper and 'FROM' in sql_upper:
        result['valid'] = True

    return result

if __name__ == '__main__':
    sql_input = sys.stdin.read().strip()
    result = analyze_query(sql_input)
    print(json.dumps(result, indent=2))
