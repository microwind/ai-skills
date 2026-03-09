#!/usr/bin/env python3
import os
import json

# Create database-query-analyzer script
script1 = '''#!/usr/bin/env python3
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
'''

# Create kubernetes-validator script
script2 = '''#!/usr/bin/env python3
import sys
import json

def validate_kubernetes(manifest_text):
    """Validate Kubernetes manifest"""
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'resources': [],
        'checks': {
            'has_resource_limits': False,
            'has_health_probes': False,
            'has_image_pull_policy': False,
            'has_security_context': False
        }
    }

    if not manifest_text or not manifest_text.strip():
        result['errors'].append('Empty manifest')
        return result

    try:
        import yaml
        docs = list(yaml.safe_load_all(manifest_text))
        result['valid'] = True

        for doc in docs:
            if not doc:
                continue

            kind = doc.get('kind', 'Unknown')
            name = doc.get('metadata', {}).get('name', 'unnamed')
            result['resources'].append({'kind': kind, 'name': name})

            spec = doc.get('spec', {})
            if kind == 'Pod':
                containers = spec.get('containers', [])
                for container in containers:
                    resources = container.get('resources', {})
                    if resources.get('limits'):
                        result['checks']['has_resource_limits'] = True

                    if container.get('livenessProbe') or container.get('readinessProbe'):
                        result['checks']['has_health_probes'] = True

            if 'securityContext' in spec:
                result['checks']['has_security_context'] = True

            if kind == 'Deployment' and not spec.get('replicas'):
                result['warnings'].append(f'{name}: No explicit replicas set')

    except Exception as e:
        result['valid'] = False
        result['errors'].append(f'Error: {str(e)}')

    return result

if __name__ == '__main__':
    manifest = sys.stdin.read()
    result = validate_kubernetes(manifest)
    print(json.dumps(result, indent=2))
'''

scripts_to_create = [
    ("backend/database-query-analyzer", "analyze_query.py", script1),
    ("cloud-native/kubernetes-validator", "validate_k8s.py", script2),
    ("cloud-native/cloud-config-analyzer", "analyze_cloud_config.py", '''#!/usr/bin/env python3
import sys
import json

def analyze_cloud_config(config_text):
    """Analyze cloud configuration"""
    result = {
        'valid': True,
        'security_issues': [],
        'cost_optimizations': [],
        'configuration': {
            'has_encryption': False,
            'has_iam_roles': False,
            'has_backup': False,
            'has_monitoring': False
        }
    }

    if not config_text or not config_text.strip():
        result['valid'] = False
        return result

    text = config_text.lower()

    if 'public' in text and ('read' in text or 'acl' in text):
        result['security_issues'].append('Public access detected')

    if 'password' in text and '=' in text:
        if not any(k in text for k in ['kms', 'secrets', 'encrypted']):
            result['security_issues'].append('Potential hardcoded password')

    if 'encrypt' in text or 'kms' in text:
        result['configuration']['has_encryption'] = True

    if 'iam' in text or 'role' in text:
        result['configuration']['has_iam_roles'] = True

    if 'backup' in text or 'replication' in text:
        result['configuration']['has_backup'] = True

    if 'monitor' in text or 'cloudwatch' in text:
        result['configuration']['has_monitoring'] = True

    return result

if __name__ == '__main__':
    config = sys.stdin.read()
    result = analyze_cloud_config(config)
    print(json.dumps(result, indent=2))
'''),
    ("database/sql-optimizer", "optimize_sql.py", '''#!/usr/bin/env python3
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
'''),
    ("database/migration-validator", "validate_migration.py", '''#!/usr/bin/env python3
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
'''),
    ("devops/cicd-validator", "validate_cicd.py", '''#!/usr/bin/env python3
import sys
import json
import re

def validate_cicd(pipeline_text):
    """Validate CI/CD pipeline"""
    result = {
        'valid': False,
        'pipeline_type': 'unknown',
        'stages': [],
        'checks': {
            'has_tests': False,
            'has_build': False,
            'has_deploy': False,
            'has_approval': False
        },
        'issues': []
    }

    if not pipeline_text or not pipeline_text.strip():
        return result

    text = pipeline_text.lower()

    if 'github' in text or '.github' in pipeline_text:
        result['pipeline_type'] = 'GitHub Actions'
    elif 'gitlab' in text:
        result['pipeline_type'] = 'GitLab CI'

    if re.search(r'test|pytest|jest', text):
        result['checks']['has_tests'] = True
        result['stages'].append('tests')

    if re.search(r'build|docker|npm.*build', text):
        result['checks']['has_build'] = True
        result['stages'].append('build')

    if re.search(r'deploy|kubernetes|helm', text):
        result['checks']['has_deploy'] = True
        result['stages'].append('deploy')

    if re.search(r'approval|manual', text):
        result['checks']['has_approval'] = True
        result['stages'].append('approval')

    if result['stages']:
        result['valid'] = True

    if not result['checks']['has_tests']:
        result['issues'].append('No test stage')

    if not result['checks']['has_approval'] and result['checks']['has_deploy']:
        result['issues'].append('No approval gate before deployment')

    if 'password' in pipeline_text or 'secret' in text:
        result['issues'].append('Credentials may be exposed')

    return result

if __name__ == '__main__':
    pipeline = sys.stdin.read()
    result = validate_cicd(pipeline)
    print(json.dumps(result, indent=2))
'''),
    ("devops/infrastructure-analyzer", "analyze_infrastructure.py", '''#!/usr/bin/env python3
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
'''),
    ("frameworks/flask-django-analyzer", "analyze_framework.py", '''#!/usr/bin/env python3
import sys
import json
import re

def analyze_framework(code_text):
    """Analyze framework code"""
    result = {
        'framework': 'unknown',
        'patterns': [],
        'issues': [],
        'best_practices': {
            'has_error_handling': False,
            'has_logging': False,
            'has_tests': False,
            'organized_views': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'from flask import' in code_text or '@app.route' in code_text:
        result['framework'] = 'Flask'
    elif 'from django' in code_text:
        result['framework'] = 'Django'

    if re.search(r'try:|except', code_text):
        result['best_practices']['has_error_handling'] = True

    if 'import logging' in code_text or 'logger.' in code_text:
        result['best_practices']['has_logging'] = True
    else:
        result['issues'].append('No logging configured')

    if re.search(r'test_|TestCase', code_text):
        result['best_practices']['has_tests'] = True

    if 'for item in items:' in code_text and '.objects.get' in code_text:
        result['issues'].append('N+1 query pattern detected')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_framework(code)
    print(json.dumps(result, indent=2))
'''),
    ("frameworks/spring-analyzer", "analyze_spring.py", '''#!/usr/bin/env python3
import sys
import json
import re

def analyze_spring(code_text):
    """Analyze Spring code"""
    result = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_dependency_injection': False,
            'has_exception_handling': False,
            'has_transaction_management': False,
            'has_logging': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if '@Autowired' in code_text or '@Inject' in code_text:
        result['checks']['has_dependency_injection'] = True
    else:
        result['issues'].append('No dependency injection detected')

    if '@Service' in code_text or '@Repository' in code_text:
        result['patterns'].append('Spring stereotypes found')

    if 'try {' in code_text:
        result['checks']['has_exception_handling'] = True

    if '@Transactional' in code_text:
        result['checks']['has_transaction_management'] = True

    if 'Logger' in code_text or 'log.' in code_text:
        result['checks']['has_logging'] = True

    if re.search(r'new\\s+\\w+Service', code_text):
        result['issues'].append('Manual object creation - use DI')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_spring(code)
    print(json.dumps(result, indent=2))
'''),
    ("frontend/css-validator", "validate_css.py", '''#!/usr/bin/env python3
import sys
import json
import re

def validate_css(css_text):
    """Validate CSS"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'metrics': {
            'selectors': 0,
            'rules': 0,
            'high_specificity': 0
        }
    }

    if not css_text or not css_text.strip():
        result['valid'] = False
        return result

    brace_count = css_text.count('{') - css_text.count('}')
    if brace_count != 0:
        result['valid'] = False
        result['errors'].append('Unmatched braces')

    result['metrics']['rules'] = len(re.findall(r'\\{[^}]*\\}', css_text))
    result['metrics']['selectors'] = len(re.findall(r'[^{};]+\\{', css_text))

    if '!important' in css_text:
        result['warnings'].append('!important declarations present')

    if '@media' not in css_text:
        result['warnings'].append('No media queries - not responsive')

    return result

if __name__ == '__main__':
    css = sys.stdin.read()
    result = validate_css(css)
    print(json.dumps(result, indent=2))
'''),
    ("frontend/component-analyzer", "analyze_component.py", '''#!/usr/bin/env python3
import sys
import json
import re

def analyze_component(code_text):
    """Analyze component"""
    result = {
        'framework': 'unknown',
        'issues': [],
        'patterns': [],
        'metrics': {
            'lines': 0,
            'state_count': 0,
            'prop_count': 0,
            'has_tests': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    result['metrics']['lines'] = len(code_text.split('\\n'))

    if 'useState' in code_text or 'useEffect' in code_text:
        result['framework'] = 'React'
    elif '@Component' in code_text:
        result['framework'] = 'Vue'

    result['metrics']['state_count'] = len(re.findall(r'useState|this\\.state', code_text))
    result['metrics']['prop_count'] = len(re.findall(r'props\\.', code_text))

    if result['metrics']['state_count'] > 5:
        result['issues'].append('Too much state')

    if result['metrics']['prop_count'] > 10:
        result['issues'].append('Too many props - consider context')

    if 'React.memo' in code_text or 'useMemo' in code_text:
        result['patterns'].append('Memoization used')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_component(code)
    print(json.dumps(result, indent=2))
'''),
    ("frontend/bundle-analyzer", "analyze_bundle.py", '''#!/usr/bin/env python3
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
'''),
    ("languages/python-analyzer", "analyze_python.py", '''#!/usr/bin/env python3
import sys
import json
import re

def analyze_python(code_text):
    """Analyze Python code"""
    result = {
        'valid': False,
        'issues': [],
        'patterns': [],
        'metrics': {
            'has_type_hints': False,
            'has_docstrings': False,
            'has_error_handling': False,
            'functions_count': 0
        }
    }

    if not code_text or not code_text.strip():
        return result

    try:
        compile(code_text, '<string>', 'exec')
        result['valid'] = True
    except SyntaxError as e:
        result['issues'].append(f'Syntax error: {str(e)}')
        return result

    if '->' in code_text or ': int' in code_text:
        result['metrics']['has_type_hints'] = True
    else:
        result['issues'].append('No type hints')

    result['metrics']['functions_count'] = len(re.findall(r'def ', code_text))

    if 'try:' in code_text:
        result['metrics']['has_error_handling'] = True

    if 'except:' in code_text:
        result['issues'].append('Bare except clause - specify exception')

    if 'import logging' in code_text:
        result['patterns'].append('Logging configured')
    elif 'print(' in code_text:
        result['issues'].append('Using print - use logging')

    if '=[]' in code_text and 'def ' in code_text:
        result['issues'].append('Mutable default argument')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_python(code)
    print(json.dumps(result, indent=2))
'''),
    ("languages/javascript-analyzer", "analyze_javascript.py", '''#!/usr/bin/env python3
import sys
import json
import re

def analyze_javascript(code_text):
    """Analyze JavaScript code"""
    result = {
        'issues': [],
        'patterns': [],
        'checks': {
            'has_async_await': False,
            'has_error_handling': False,
            'has_comments': False,
            'uses_const_let': False
        }
    }

    if not code_text or not code_text.strip():
        return result

    if 'async ' in code_text or 'await ' in code_text:
        result['checks']['has_async_await'] = True
    elif '.then(' in code_text:
        result['patterns'].append('Promise chains detected')

    if 'try' in code_text or 'catch' in code_text:
        result['checks']['has_error_handling'] = True
    else:
        result['issues'].append('No error handling')

    if '//' in code_text or '/*' in code_text:
        result['checks']['has_comments'] = True

    if 'var ' in code_text:
        result['issues'].append('Using var - use const/let')
    else:
        result['checks']['uses_const_let'] = True

    if 'console.log' in code_text:
        result['issues'].append('console.log in production code')

    if 'addEventListener' in code_text:
        if 'removeEventListener' not in code_text:
            result['issues'].append('Event listeners not cleaned up')

    return result

if __name__ == '__main__':
    code = sys.stdin.read()
    result = analyze_javascript(code)
    print(json.dumps(result, indent=2))
'''),
    ("microservices/service-mesh-analyzer", "analyze_service_mesh.py", '''#!/usr/bin/env python3
import sys
import json

def analyze_service_mesh(config_text):
    """Analyze service mesh"""
    result = {
        'valid': False,
        'mesh_type': 'unknown',
        'configuration': {
            'mtls_enabled': False,
            'circuit_breaker': False,
            'timeout_configured': False,
            'retry_policy': False
        },
        'issues': []
    }

    if not config_text or not config_text.strip():
        return result

    text = config_text.lower()

    if 'istio' in text:
        result['mesh_type'] = 'Istio'
    elif 'linkerd' in text:
        result['mesh_type'] = 'Linkerd'

    try:
        import yaml
        config = yaml.safe_load(config_text)
        result['valid'] = True

        if any(k in text for k in ['mtls', 'tls', 'certificate']):
            result['configuration']['mtls_enabled'] = True
        else:
            result['issues'].append('mTLS not configured')

        if 'circuitbreaker' in text or 'outlier' in text:
            result['configuration']['circuit_breaker'] = True
        else:
            result['issues'].append('No circuit breaker')

        if 'timeout' in text:
            result['configuration']['timeout_configured'] = True
        else:
            result['issues'].append('No timeout configured')

        if 'retry' in text:
            result['configuration']['retry_policy'] = True

    except Exception:
        result['valid'] = False
        result['issues'].append('YAML parsing error')

    return result

if __name__ == '__main__':
    config = sys.stdin.read()
    result = analyze_service_mesh(config)
    print(json.dumps(result, indent=2))
'''),
    ("microservices/api-contract-validator", "validate_api_contract.py", '''#!/usr/bin/env python3
import sys
import json

def validate_api_contract(contract_text):
    """Validate API contract"""
    result = {
        'valid': False,
        'format': 'unknown',
        'endpoints': [],
        'issues': [],
        'checks': {
            'has_request_schema': False,
            'has_response_schema': False,
            'has_status_codes': False,
            'has_examples': False
        }
    }

    if not contract_text or not contract_text.strip():
        return result

    if 'openapi' in contract_text.lower():
        result['format'] = 'OpenAPI'
    elif 'swagger' in contract_text.lower():
        result['format'] = 'Swagger'

    try:
        import yaml
        contract = yaml.safe_load(contract_text)
        result['valid'] = True

        if 'paths' in contract:
            result['endpoints'] = list(contract['paths'].keys())

        if 'components' in contract and 'schemas' in contract['components']:
            result['checks']['has_request_schema'] = True
            result['checks']['has_response_schema'] = True

        if 'responses' in contract_text:
            result['checks']['has_status_codes'] = True

        if 'example' in contract_text.lower():
            result['checks']['has_examples'] = True
        else:
            result['issues'].append('No examples provided')

        if 'version' not in contract_text:
            result['issues'].append('No API version specified')

    except Exception as e:
        result['valid'] = False
        result['issues'].append(f'YAML error: {str(e)}')

    return result

if __name__ == '__main__':
    contract = sys.stdin.read()
    result = validate_api_contract(contract)
    print(json.dumps(result, indent=2))
'''),
]

created = 0
for skill_path, script_name, script_content in scripts_to_create:
    script_dir = f"/Users/jarry/github/ai-skills/{skill_path}/scripts"
    script_file = f"{script_dir}/{script_name}"

    with open(script_file, 'w') as f:
        f.write(script_content)

    os.chmod(script_file, 0o755)
    created += 1
    print(f"✅ Created {skill_path}/scripts/{script_name}")

print(f"\n✅ All {created} executable scripts created!")
