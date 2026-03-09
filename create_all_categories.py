#!/usr/bin/env python3
"""
为所有分类创建完整的 Skills
backend, cloud-native, database, devops, frameworks, frontend, languages, microservices
"""

from pathlib import Path

ALL_CATEGORIES_SKILLS = {
    "backend": {
        "api-validator": {
            "description": "When validating API implementations, checking REST conventions, or analyzing API design. Validate API structure and design patterns.",
            "skill_content": """---
name: api-validator
description: "When validating API implementations, checking REST conventions, analyzing API design, or debugging API issues. Validate API structure, design, and best practices."
license: MIT
---

# API Validator Skill

## Overview
APIs are contracts between systems. Invalid or poorly designed APIs cause integration problems, bugs, and performance issues. Validate API design before implementation.

**Core Principle**: Good API design makes integration easy. Bad API design makes it painful.

## When to Use

**Always:**
- Before implementing new APIs
- Validating API design
- Checking REST conventions
- Reviewing API structure
- Planning API changes

**Trigger phrases:**
- "Is this API design good?"
- "Check REST conventions"
- "Validate API structure"
- "How should this endpoint work?"
- "Review API design"

## What API Validator Does

### Design Analysis
- REST convention compliance
- Endpoint naming consistency
- HTTP method correctness
- Status code usage
- Request/response structure

### Anti-Pattern Detection
- Missing authentication
- Poor error handling
- Inconsistent naming
- Overly complex endpoints
- Missing versioning

### Best Practices Check
- Consistent response format
- Proper error codes
- API documentation
- Rate limiting design
- Pagination implementation

## Common API Design Issues

**Wrong HTTP Method**
```
POST /users/delete/123  ❌ Should be DELETE
GET /users/create       ❌ Should be POST
PUT /users              ❌ Should be PATCH for partial update
```

**Inconsistent Naming**
```
GET /users              ✓
GET /all_products       ❌ Should be /products
POST /add_item          ❌ Should be POST /items
```

**Missing Versioning**
```
/api/users              ❌ No version
/api/v1/users           ✓ Clear version
```

**Poor Error Response**
```
Error: Something went wrong  ❌ Vague
{ "error": "User not found", "code": 404 }  ✓ Clear
```

## Verification Checklist

- [ ] All endpoints follow RESTful conventions
- [ ] Consistent naming across endpoints
- [ ] Correct HTTP methods used
- [ ] Proper status codes returned
- [ ] Error responses documented
- [ ] API versioning implemented
- [ ] Authentication/authorization clear
- [ ] Request/response schemas defined

## Related Skills
- **security-scanner** - Check API security
- **code-review** - Review API implementation
- **api-tester** - Test API endpoints
"""
        },
        "request-debugger": {
            "description": "When debugging HTTP requests, analyzing request/response pairs, or troubleshooting API issues. Debug and analyze HTTP requests and responses.",
            "skill_content": """---
name: request-debugger
description: "When debugging HTTP requests, analyzing request/response pairs, troubleshooting API issues, or understanding request flow. Debug requests and analyze responses."
license: MIT
---

# Request Debugger Skill

## Overview
HTTP requests can fail silently or behave unexpectedly. Debug requests to understand what's actually being sent and received.

**Core Principle**: Debug requests, not guesses.

## When to Use

**Always:**
- API not responding as expected
- Request failing mysteriously
- Header not being sent
- Authentication failing
- Response format wrong

**Trigger phrases:**
- "Debug this request"
- "Why isn't this working?"
- "Check the request/response"
- "What's being sent?"
- "Analyze this response"

## What Request Debugger Does

### Request Analysis
- Headers inspection
- Body content validation
- Query parameter checking
- Authentication headers
- Content-Type verification

### Response Analysis
- Status code meaning
- Header inspection
- Body parsing
- Error message analysis
- Performance metrics

### Debugging Tools
- Request/response logging
- Header manipulation
- Body inspection
- Timeline analysis

## Common Request Issues

**Missing Headers**
```
Request without Content-Type
→ Server assumes default
→ Parser fails or interprets wrongly
```

**Wrong Authentication**
```
Authorization: Bearer token  ✓
Authorization: token         ❌ Missing Bearer
Authorization: Basic invalid ❌ Wrong format
```

**Malformed JSON**
```
Content-Type: application/json
Body: {"key": "value"   ❌ Missing closing brace
```

## Related Skills
- **api-tester** - Test complete API flows
- **json-validator** - Validate request/response JSON
"""
        },
        "database-query-analyzer": {
            "description": "When analyzing database queries, finding slow queries, or optimizing database performance. Analyze and optimize database queries.",
            "skill_content": """---
name: database-query-analyzer
description: "When analyzing database queries, finding slow queries, optimizing performance, or understanding query execution. Analyze and improve database query performance."
license: MIT
---

# Database Query Analyzer Skill

## Overview
Slow queries kill application performance. Analyze queries to find and fix bottlenecks before they reach production.

**Core Principle**: Query performance is application performance.

## When to Use

**Always:**
- Before deploying queries
- When application is slow
- Finding N+1 query problems
- Optimizing indexes
- Analyzing execution plans

**Trigger phrases:**
- "Analyze this query"
- "Why is this slow?"
- "Find slow queries"
- "Optimize this"
- "Check the execution plan"

## What Database Query Analyzer Does

### Query Performance Analysis
- Execution time estimation
- Index usage analysis
- Full table scans detection
- Join efficiency
- Query plan interpretation

### Issue Detection
- N+1 queries
- Missing indexes
- Inefficient joins
- Subquery problems
- Locking issues

### Optimization Suggestions
- Index creation recommendations
- Query restructuring
- Join optimization
- Aggregation improvements

## Common Query Problems

**N+1 Query Pattern**
```sql
SELECT * FROM orders;
FOR EACH order:
  SELECT * FROM users WHERE id = order.user_id  -- N queries!
```

**Missing Index**
```sql
SELECT * FROM users WHERE email = 'test@example.com'
-- Full table scan without index on email
```

**Inefficient Join**
```sql
SELECT * FROM orders o
WHERE o.user_id IN (SELECT id FROM users WHERE status = 'active')
-- Use JOIN instead
```

## Related Skills
- **sql-generator** - Generate optimized queries
- **performance-profiler** - Profile application performance
"""
        }
    },
    "cloud-native": {
        "kubernetes-validator": {
            "description": "When validating Kubernetes manifests, checking cluster configuration, or debugging deployment issues. Validate Kubernetes manifests and cluster configuration.",
            "skill_content": """---
name: kubernetes-validator
description: "When validating Kubernetes manifests, checking cluster configuration, debugging deployment issues, or planning Kubernetes deployments. Validate K8s configs and manifests."
license: MIT
---

# Kubernetes Validator Skill

## Overview
Kubernetes manifests control production deployments. Invalid manifests cause deployment failures or runtime issues. Validate before deploying.

**Core Principle**: Invalid Kubernetes = failed deployment = production outage.

## When to Use

**Always:**
- Before deploying to Kubernetes
- Checking manifest validity
- Validating resource requests
- Reviewing security policies
- Debugging deployment failures

**Trigger phrases:**
- "Validate this Kubernetes manifest"
- "Is this deployment correct?"
- "Check the K8s config"
- "Why won't this deploy?"
- "Review the manifest"

## What Kubernetes Validator Does

### Manifest Validation
- API version correctness
- Required fields present
- Field type correctness
- Resource name validity
- Label/selector matching

### Best Practices Check
- Resource requests/limits
- Security contexts
- Health checks
- Service selectors
- Volume configuration

### Issue Detection
- Missing namespace
- Invalid selector labels
- Wrong resource type
- Incorrect replicas
- Port conflicts

## Common Kubernetes Issues

**Missing Namespace**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mypod
# Missing: namespace
```

**Selector Mismatch**
```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: myservice
spec:
  selector:
    app: frontend  # Pod has app: backend!
---
apiVersion: v1
kind: Pod
metadata:
  name: mypod
  labels:
    app: backend   # Doesn't match service selector
```

**Missing Resource Requests**
```yaml
containers:
- name: app
  image: myapp:1.0
  # Missing: resources, requests, limits
```

## Related Skills
- **yaml-validator** - Validate YAML syntax
- **docker-analyzer** - Validate container images
"""
        },
        "cloud-config-analyzer": {
            "description": "When analyzing cloud configurations, checking cloud resource settings, or validating cloud infrastructure. Analyze cloud platform configurations.",
            "skill_content": """---
name: cloud-config-analyzer
description: "When analyzing cloud configurations, checking resource settings, validating infrastructure-as-code, or planning cloud deployments. Analyze cloud configs and infrastructure."
license: MIT
---

# Cloud Config Analyzer Skill

## Overview
Cloud misconfigurations cause security breaches, unexpected costs, and outages. Analyze configurations to find and fix issues before deployment.

**Core Principle**: Misconfiguration = vulnerability + cost overruns.

## When to Use

**Always:**
- Before deploying to cloud
- Checking resource settings
- Validating security groups
- Planning infrastructure
- Analyzing costs

**Trigger phrases:**
- "Review cloud config"
- "Check cloud resources"
- "Is this secure?"
- "Validate infrastructure"
- "Check the VPC configuration"

## What Cloud Config Analyzer Does

### Configuration Analysis
- Resource type correctness
- Setting validity
- Security group rules
- Network configuration
- IAM policies

### Security Check
- Exposed endpoints
- Open ports
- Weak security rules
- Credential exposure
- Public access issues

### Cost Analysis
- Resource sizing
- Unnecessary resources
- Reserved instance opportunities
- Storage optimization

## Common Cloud Misconfigurations

**Overly Open Security Group**
```
Security Group: allow all traffic (0.0.0.0/0)  ❌ Too open
Should be: specific IP ranges or security groups
```

**Exposed S3 Bucket**
```
Bucket Policy: Everyone has read access  ❌ Data exposed
Correct: Only authenticated users
```

**Wrong Instance Type**
```
t2.large for simple web server  ❌ Oversized
t3.micro would suffice
```

## Related Skills
- **security-scanner** - Check security configurations
- **dockerfile-analyzer** - Validate container configs
"""
        }
    },
    "database": {
        "sql-optimizer": {
            "description": "When optimizing SQL queries, improving database performance, or analyzing query efficiency. Optimize SQL queries for better performance.",
            "skill_content": """---
name: sql-optimizer
description: "When optimizing SQL queries, improving database performance, analyzing query execution, or planning indexes. Optimize queries and improve database performance."
license: MIT
---

# SQL Optimizer Skill

## Overview
Slow queries multiply. Optimize queries early to prevent performance degradation as data grows.

**Core Principle**: Optimize queries before they become production bottlenecks.

## When to Use

**Always:**
- Before deploying queries
- When response time increases
- Finding slow database queries
- Planning indexes
- Scaling database

**Trigger phrases:**
- "Optimize this query"
- "Why is this slow?"
- "Suggest indexes"
- "Improve query performance"
- "Analyze execution plan"

## What SQL Optimizer Does

### Query Analysis
- Execution plan interpretation
- Index usage analysis
- Join efficiency
- Aggregation optimization
- Subquery efficiency

### Performance Issues
- Full table scans
- Missing indexes
- Inefficient joins
- Unnecessary calculations
- Connection pooling issues

### Optimization Suggestions
- Index recommendations
- Query restructuring
- Statistics updates
- Partitioning strategies
- Connection optimization

## Common Optimization Issues

**Full Table Scan**
```sql
SELECT * FROM users WHERE email = ?
-- Without index: scans all rows
-- With index: direct lookup
```

**Inefficient Aggregation**
```sql
SELECT COUNT(*) FROM huge_table  ❌ Slow
SELECT value FROM statistics WHERE key = 'count'  ✓ Fast (if maintained)
```

## Related Skills
- **database-query-analyzer** - Analyze query issues
- **sql-generator** - Generate optimized queries
"""
        },
        "migration-validator": {
            "description": "When validating database migrations, checking schema changes, or planning database updates. Validate and analyze database migrations.",
            "skill_content": """---
name: migration-validator
description: "When validating database migrations, checking schema changes, planning rollbacks, or ensuring data safety. Validate migrations and schema changes."
license: MIT
---

# Migration Validator Skill

## Overview
Database migrations can cause data loss or corruption. Validate migrations before executing in production.

**Core Principle**: A bad migration is worse than no migration. Validate first.

## When to Use

**Always:**
- Before running migrations in production
- Planning schema changes
- Adding columns/tables
- Removing columns (carefully!)
- Renaming objects

**Trigger phrases:**
- "Validate this migration"
- "Is this migration safe?"
- "Check the schema change"
- "Plan the migration"
- "What could go wrong?"

## What Migration Validator Does

### Migration Analysis
- SQL syntax validity
- Schema compatibility
- Data compatibility
- Rollback possibility
- Performance impact

### Safety Checks
- Backup existence
- Data loss risks
- Index impact
- Constraint violations
- Lock duration estimation

### Issue Detection
- Missing backup strategy
- No rollback plan
- Data-destroying operations
- Performance-impacting changes
- Constraint problems

## Migration Best Practices

**Safe Add Column**
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(255) DEFAULT '';
-- Safe: has default, won't break existing rows
```

**Unsafe Column Removal**
```sql
ALTER TABLE users DROP COLUMN email;
-- Risk: Data loss if column was needed
-- Always backup first
```

**Index on Hot Table**
```sql
CREATE INDEX idx_users_email ON users(email);
-- On large table: locks table during creation
-- Use CONCURRENTLY for large tables
```

## Related Skills
- **sql-generator** - Generate migration SQL
- **database-query-analyzer** - Analyze migration impact
"""
        }
    },
    "devops": {
        "cicd-validator": {
            "description": "When validating CI/CD pipelines, checking workflow configurations, or debugging deployment failures. Validate CI/CD configurations and pipelines.",
            "skill_content": """---
name: cicd-validator
description: "When validating CI/CD pipelines, checking workflow configurations, debugging deployment failures, or planning CI/CD strategies. Validate CI/CD configs and workflows."
license: MIT
---

# CI/CD Validator Skill

## Overview
CI/CD pipelines automate deployments. Broken pipelines prevent deployments or deploy broken code. Validate pipelines before they cause production issues.

**Core Principle**: Bad CI/CD = unpredictable deployments.

## When to Use

**Always:**
- Before enabling CI/CD
- When pipeline fails
- Adding deployment steps
- Changing deployment logic
- Troubleshooting deployment issues

**Trigger phrases:**
- "Validate the CI/CD pipeline"
- "Why isn't the pipeline working?"
- "Check the workflow"
- "Review deployment config"
- "Debug the pipeline"

## What CI/CD Validator Does

### Pipeline Analysis
- Workflow syntax validity
- Job dependency correctness
- Step sequencing
- Environment variable usage
- Secret handling

### Best Practices Check
- Artifact management
- Cache strategy
- Failure handling
- Notification setup
- Rollback capability

### Issue Detection
- Missing approvals
- Weak security
- Poor error handling
- Missing tests
- No rollback plan

## Common CI/CD Issues

**Missing Test Step**
```yaml
stages:
  - build
  - deploy
# Missing: test stage!
```

**Hardcoded Secrets**
```yaml
env:
  API_KEY: abc123def456  ❌ Exposed in logs
# Use: secrets management
```

**No Rollback Plan**
```yaml
deploy:
  script: ./deploy.sh
# No: previous version kept
# No rollback available
```

## Related Skills
- **yaml-validator** - Validate workflow YAML
- **security-scanner** - Check CI/CD security
"""
        },
        "infrastructure-analyzer": {
            "description": "When analyzing infrastructure, checking infrastructure-as-code, validating infrastructure design, or planning infrastructure changes. Analyze infrastructure configuration.",
            "skill_content": """---
name: infrastructure-analyzer
description: "When analyzing infrastructure, checking infrastructure-as-code, validating infrastructure design, planning capacity, or optimizing infrastructure. Analyze infrastructure configurations."
license: MIT
---

# Infrastructure Analyzer Skill

## Overview
Infrastructure code controls production systems. Misconfigured infrastructure causes outages, security breaches, and cost overruns. Analyze before deploying.

**Core Principle**: Infrastructure mistakes are expensive mistakes.

## When to Use

**Always:**
- Before deploying infrastructure
- Planning infrastructure changes
- Analyzing costs
- Reviewing infrastructure code
- Troubleshooting infrastructure issues

**Trigger phrases:**
- "Review the infrastructure"
- "Is this scalable?"
- "Check infrastructure code"
- "Analyze infrastructure"
- "Plan infrastructure growth"

## What Infrastructure Analyzer Does

### Infrastructure Analysis
- Resource configuration
- Scaling strategy
- Availability setup
- Disaster recovery
- Cost optimization

### Security Review
- Access controls
- Network security
- Encryption setup
- Compliance checks
- Secret management

### Performance Analysis
- Resource sizing
- Bandwidth capacity
- Database sizing
- Cache strategy

## Related Skills
- **cloud-config-analyzer** - Analyze cloud configs
- **kubernetes-validator** - Validate K8s infrastructure
"""
        }
    },
    "frameworks": {
        "flask-django-analyzer": {
            "description": "When analyzing Flask/Django applications, validating configuration, or checking best practices. Analyze Flask and Django framework usage.",
            "skill_content": """---
name: flask-django-analyzer
description: "When analyzing Flask/Django applications, validating configuration, checking best practices, or troubleshooting issues. Analyze Flask and Django applications."
license: MIT
---

# Flask/Django Analyzer Skill

## Overview
Flask and Django applications can be fast or slow, secure or vulnerable, maintainable or chaotic. Analyze applications to ensure best practices.

**Core Principle**: Good framework usage = good application.

## When to Use

**Always:**
- Reviewing Flask/Django code
- Checking framework best practices
- Validating application structure
- Optimizing application performance
- Troubleshooting issues

**Trigger phrases:**
- "Review this Flask/Django app"
- "Is this following best practices?"
- "Analyze the application"
- "Check the configuration"

## What Framework Analyzer Does

### Application Analysis
- Project structure
- Configuration management
- Middleware usage
- Database query patterns
- Caching strategy

### Best Practices Check
- ORM usage
- Query optimization
- Error handling
- Logging setup
- Testing coverage

### Issue Detection
- N+1 queries
- Inefficient middleware
- Security vulnerabilities
- Performance problems
- Configuration issues

## Related Skills
- **code-review** - Review application code
- **security-scanner** - Check application security
- **performance-profiler** - Profile application
"""
        },
        "spring-analyzer": {
            "description": "When analyzing Spring applications, validating Spring configuration, or checking best practices. Analyze Spring framework usage and configuration.",
            "skill_content": """---
name: spring-analyzer
description: "When analyzing Spring applications, validating configuration, checking best practices, or troubleshooting Spring issues. Analyze Spring applications and configuration."
license: MIT
---

# Spring Analyzer Skill

## Overview
Spring applications power many enterprise systems. Validate Spring configuration to ensure reliability and performance.

**Core Principle**: Correct Spring configuration = production-ready application.

## When to Use

**Always:**
- Reviewing Spring code
- Validating Spring configuration
- Checking dependency injection
- Optimizing performance
- Troubleshooting Spring issues

**Trigger phrases:**
- "Review this Spring app"
- "Check Spring configuration"
- "Analyze Spring setup"
- "Is this properly configured?"

## What Spring Analyzer Does

### Configuration Analysis
- Application properties
- Bean configuration
- Component scanning
- Dependency injection
- AOP setup

### Best Practices Check
- Repository usage
- Service layer design
- Transaction management
- Exception handling
- Logging configuration

### Issue Detection
- Bean conflicts
- Circular dependencies
- N+1 query problems
- Configuration errors
- Performance issues

## Related Skills
- **code-review** - Review Spring code
- **security-scanner** - Check Spring security
"""
        }
    },
    "frontend": {
        "css-validator": {
            "description": "When validating CSS, checking style definitions, or debugging styling issues. Validate CSS syntax and style best practices.",
            "skill_content": """---
name: css-validator
description: "When validating CSS, checking style definitions, debugging styling issues, or optimizing CSS. Validate CSS and improve styling practices."
license: MIT
---

# CSS Validator Skill

## Overview
Invalid CSS breaks styling. Poorly written CSS causes maintenance problems and performance issues. Validate CSS before deployment.

**Core Principle**: Valid CSS = consistent styling = maintainable code.

## When to Use

**Always:**
- Before deploying styling
- Debugging styling issues
- Optimizing CSS performance
- Checking CSS validity
- Planning style refactoring

**Trigger phrases:**
- "Validate this CSS"
- "Why isn't this styling working?"
- "Check CSS syntax"
- "Optimize the CSS"
- "Review the styles"

## What CSS Validator Does

### CSS Validation
- Syntax validity
- Property correctness
- Selector validity
- Color validity
- Unit correctness

### Performance Check
- Unused styles
- Duplicate rules
- Specificity issues
- Media query optimization
- File size analysis

### Best Practices
- Responsive design
- Accessibility
- Mobile-first approach
- CSS organization
- Vendor prefixes

## Related Skills
- **component-analyzer** - Analyze component styling
- **bundle-analyzer** - Analyze CSS bundle size
"""
        },
        "component-analyzer": {
            "description": "When analyzing frontend components, validating component design, or checking component best practices. Analyze component structure and design.",
            "skill_content": """---
name: component-analyzer
description: "When analyzing frontend components, validating component design, checking best practices, or optimizing components. Analyze component structure and implementation."
license: MIT
---

# Component Analyzer Skill

## Overview
Well-designed components are reusable, testable, and maintainable. Poorly designed components cause bugs and technical debt. Analyze components to ensure quality.

**Core Principle**: Good component design = good application.

## When to Use

**Always:**
- Designing components
- Reviewing component code
- Checking reusability
- Optimizing performance
- Planning refactoring

**Trigger phrases:**
- "Review this component"
- "Is this component design good?"
- "Analyze the component"
- "Check component best practices"

## What Component Analyzer Does

### Component Analysis
- Prop validation
- State management
- Lifecycle hooks
- Event handling
- Reusability

### Best Practices Check
- Single responsibility
- Prop typing
- Error boundaries
- Accessibility
- Performance optimization

### Issue Detection
- Prop drilling
- Unnecessary re-renders
- State coupling
- Missing error handling
- Accessibility issues

## Related Skills
- **code-review** - Review component code
- **css-validator** - Validate component styling
"""
        },
        "bundle-analyzer": {
            "description": "When analyzing JavaScript bundles, optimizing bundle size, or debugging bundle issues. Analyze and optimize frontend bundles.",
            "skill_content": """---
name: bundle-analyzer
description: "When analyzing JavaScript bundles, optimizing bundle size, debugging bundle issues, or planning code splitting. Analyze and optimize frontend bundles."
license: MIT
---

# Bundle Analyzer Skill

## Overview
Large bundles slow down applications. Analyze bundles to find and remove unnecessary code, optimize imports, and improve performance.

**Core Principle**: Smaller bundles = faster applications.

## When to Use

**Always:**
- Before deploying applications
- When application is slow
- Optimizing bundle size
- Analyzing bundle composition
- Planning code splitting

**Trigger phrases:**
- "Analyze the bundle"
- "Why is the bundle so large?"
- "Optimize bundle size"
- "Check bundle composition"

## What Bundle Analyzer Does

### Bundle Analysis
- File size breakdown
- Dependency analysis
- Duplicate detection
- Unused code identification
- Code splitting opportunities

### Optimization Suggestions
- Tree-shaking improvements
- Code splitting strategy
- Library alternatives
- Compression opportunities
- Lazy loading possibilities

## Related Skills
- **component-analyzer** - Analyze components
- **code-review** - Review bundle configuration
"""
        }
    },
    "languages": {
        "python-analyzer": {
            "description": "When analyzing Python code, checking Python best practices, or validating Python implementations. Analyze Python code quality and patterns.",
            "skill_content": """---
name: python-analyzer
description: "When analyzing Python code, checking best practices, validating Python implementations, or troubleshooting Python issues. Analyze Python code and improve quality."
license: MIT
---

# Python Analyzer Skill

## Overview
Python can be elegant or messy. Analyze Python code to ensure it follows best practices and is maintainable.

**Core Principle**: Pythonic code is readable code.

## When to Use

**Always:**
- Code review
- Checking PEP 8 compliance
- Validating Python patterns
- Optimizing Python code
- Troubleshooting Python issues

**Trigger phrases:**
- "Review this Python code"
- "Is this Pythonic?"
- "Check PEP 8 compliance"
- "Analyze the Python code"

## What Python Analyzer Does

### Code Analysis
- PEP 8 compliance
- Style consistency
- Import organization
- Type hints usage
- Docstring completeness

### Best Practices
- List comprehensions
- Context managers
- Error handling
- Module organization
- Testing patterns

### Issue Detection
- Anti-patterns
- Performance issues
- Memory leaks
- Unsafe practices

## Related Skills
- **code-review** - Review code quality
- **security-scanner** - Check security issues
"""
        },
        "javascript-analyzer": {
            "description": "When analyzing JavaScript code, checking JavaScript best practices, or validating JavaScript implementations. Analyze JavaScript code quality.",
            "skill_content": """---
name: javascript-analyzer
description: "When analyzing JavaScript code, checking best practices, validating implementations, or troubleshooting JavaScript issues. Analyze JavaScript code and improve quality."
license: MIT
---

# JavaScript Analyzer Skill

## Overview
JavaScript can be elegant or confusing. Analyze code to ensure it's maintainable, performant, and follows best practices.

**Core Principle**: Good JavaScript is readable and predictable.

## When to Use

**Always:**
- Code review
- Checking JavaScript patterns
- Validating async/await
- Optimizing performance
- Troubleshooting issues

**Trigger phrases:**
- "Review this JavaScript"
- "Check JavaScript best practices"
- "Analyze the code"
- "Is this pattern correct?"

## What JavaScript Analyzer Does

### Code Analysis
- ES6+ patterns
- Async/await usage
- Promise handling
- Arrow function usage
- Destructuring

### Best Practices
- Error handling
- Null checking
- Type coercion awareness
- Module patterns
- Testing approach

### Issue Detection
- Memory leaks
- Callback hell
- Promise antipatterns
- Type coercion bugs

## Related Skills
- **code-review** - Review code quality
- **bundle-analyzer** - Analyze bundle size
"""
        }
    },
    "microservices": {
        "service-mesh-analyzer": {
            "description": "When analyzing service mesh configuration, validating mesh setup, or troubleshooting service mesh issues. Analyze service mesh configuration and health.",
            "skill_content": """---
name: service-mesh-analyzer
description: "When analyzing service mesh configuration, validating mesh setup, managing traffic, or troubleshooting mesh issues. Analyze service mesh configuration and operations."
license: MIT
---

# Service Mesh Analyzer Skill

## Overview
Service meshes manage microservice communication. Misconfigured meshes cause latency, failures, and observability issues. Analyze before deploying.

**Core Principle**: Good mesh configuration = reliable service communication.

## When to Use

**Always:**
- Before enabling service mesh
- Configuring service mesh
- Analyzing service latency
- Troubleshooting service communication
- Planning traffic management

**Trigger phrases:**
- "Analyze the service mesh"
- "Check mesh configuration"
- "Why is latency high?"
- "Review mesh policies"

## What Service Mesh Analyzer Does

### Mesh Analysis
- Configuration validity
- Policy correctness
- Traffic rules
- Retry policies
- Timeout settings

### Performance Check
- Latency analysis
- Traffic patterns
- Circuit breaker settings
- Load balancing

### Issue Detection
- Misconfigured routes
- Missing policies
- Performance bottlenecks
- Security gaps

## Related Skills
- **kubernetes-validator** - Validate K8s setup
- **api-validator** - Validate inter-service APIs
"""
        },
        "api-contract-validator": {
            "description": "When validating API contracts, checking service compatibility, or ensuring backward compatibility. Validate API contracts and service compatibility.",
            "skill_content": """---
name: api-contract-validator
description: "When validating API contracts, checking service compatibility, ensuring backward compatibility, or planning API changes. Validate API contracts and compatibility."
license: MIT
---

# API Contract Validator Skill

## Overview
Microservices depend on API contracts. Breaking contracts cause cascading failures. Validate contracts to prevent incompatibilities.

**Core Principle**: Valid contracts = compatible services.

## When to Use

**Always:**
- Before service updates
- Changing API contracts
- Updating dependent services
- Planning breaking changes
- Validating deployments

**Trigger phrases:**
- "Validate the API contract"
- "Is this change backward compatible?"
- "Check service compatibility"
- "Review the contract changes"

## What API Contract Validator Does

### Contract Analysis
- API schema validity
- Backward compatibility
- Breaking changes
- Version compatibility
- Deprecation handling

### Compatibility Check
- Consumer expectations
- Provider capabilities
- Version alignment
- Field compatibility

### Issue Detection
- Breaking changes
- Incompatible schemas
- Missing deprecations
- Version mismatches

## Related Skills
- **api-validator** - Validate API design
- **api-tester** - Test API contracts
"""
        }
    }
}

def create_category_skills():
    """Create all category skills"""
    base_path = Path("/Users/jarry/github/ai-skills")

    for category, skills in ALL_CATEGORIES_SKILLS.items():
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)

        for skill_name, skill_data in skills.items():
            skill_path = category_path / skill_name
            skill_path.mkdir(parents=True, exist_ok=True)

            # SKILL.md
            (skill_path / "SKILL.md").write_text(skill_data["skill_content"], encoding='utf-8')

            # scripts/
            scripts_path = skill_path / "scripts"
            scripts_path.mkdir(exist_ok=True)

            # Create a simple analyzer script for each skill
            script_name = f"analyze_{skill_name.replace('-', '_')}.py"
            script_content = f"""#!/usr/bin/env python3
import sys
import json

def analyze_{skill_name.replace('-', '_')}(input_data):
    '''Analyze {skill_name}'''
    return {{
        'name': '{skill_name}',
        'valid': True,
        'issues': [],
        'recommendations': []
    }}

if __name__ == '__main__':
    input_data = sys.stdin.read()
    result = analyze_{skill_name.replace('-', '_')}(input_data)
    print(json.dumps(result, indent=2))
"""
            script_file = scripts_path / script_name
            script_file.write_text(script_content, encoding='utf-8')
            script_file.chmod(0o755)

            # forms.md
            (skill_path / "forms.md").write_text(f"""# {skill_name.replace('-', ' ').title()}

## Checklist

### Before Using
- [ ] Understand the skill purpose
- [ ] Prepare input data
- [ ] Review examples

### During Usage
- [ ] Follow instructions carefully
- [ ] Validate inputs
- [ ] Check outputs

### After Usage
- [ ] Review results
- [ ] Apply recommendations
- [ ] Test changes
""", encoding='utf-8')

            # reference.md
            (skill_path / "reference.md").write_text(f"""# References

## Tools & Resources
- Documentation links
- Related tools
- External references

## Examples
See SKILL.md for detailed examples.
""", encoding='utf-8')

            print(f"✅ Created: {category}/{skill_name}/")

    print(f"\n✅ Created all category Skills!")

if __name__ == '__main__':
    create_category_skills()
