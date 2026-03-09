#!/usr/bin/env python3
import sys
import json
import re

def optimize_sql(sql):
    """Suggest SQL optimizations"""
    result = {
        'optimizations': [],
        'warnings': [],
        'estimated_improvement': 'Unknown',
        'patterns_found': []
    }

    if not sql or not sql.strip():
        return result

    sql_upper = sql.upper()

    # Check for OR conditions
    or_count = len(re.findall(r' OR ', sql_upper))
    if or_count >= 2:
        result['patterns_found'].append('Multiple OR conditions')
        result['optimizations'].append('Use IN clause instead of OR')

    if 'UNION' in sql_upper and 'UNION ALL' not in sql_upper:
        result['optimizations'].append('Use UNION ALL if duplicates acceptable')

    if 'IN (SELECT' in sql_upper:
        result['patterns_found'].append('Subquery in IN clause')
        result['optimizations'].append('Consider using JOIN instead')

    if 'DISTINCT' in sql_upper:
        result['warnings'].append('DISTINCT is expensive - verify necessary')

    return result

if __name__ == '__main__':
    sql_input = sys.stdin.read().strip()
    result = optimize_sql(sql_input)
    print(json.dumps(result, indent=2))
