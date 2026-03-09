#!/usr/bin/env python3
"""
Enhance SKILL.md files for all category skills with detailed content
"""
import os
import json

skills_content = {
    "backend/database-query-analyzer": {
        "title": "Database Query Analyzer Skill",
        "core_principle": "Optimize queries before they slow down your system. Bad queries compound as data grows.",
        "when_to_use": [
            "Queries running slow",
            "Database CPU spiking",
            "App performance degrading",
            "Planning data model",
            "Reviewing SQL queries",
            "Investigating N+1 problems"
        ],
        "trigger_phrases": [
            "Optimize this query",
            "Why is this slow?",
            "Analyze query performance",
            "Check SQL efficiency",
            "Find N+1 queries",
            "Review this database design"
        ],
        "what_does": {
            "Query Analysis": [
                "Identify slow queries (full table scans)",
                "Find N+1 query problems",
                "Detect missing indexes",
                "Analyze query execution plans",
                "Check join efficiency"
            ],
            "Index Detection": [
                "Find missing indexes",
                "Identify unused indexes",
                "Suggest index columns",
                "Check composite index usage",
                "Analyze index selectivity"
            ],
            "Optimization Tips": [
                "Add missing indexes",
                "Rewrite inefficient queries",
                "Use EXPLAIN PLAN",
                "Batch operations",
                "Cache query results"
            ]
        },
        "common_issues": {
            "N+1 Query Problem": {
                "problem": "for item in items:\\n    item.user = User.find(item.user_id)",
                "consequence": ["1 query gets items", "N queries for each user (slow!)", "Performance degrades with data"],
                "solution": "Use JOIN: SELECT items.*, users.* FROM items JOIN users..."
            },
            "Missing Index": {
                "problem": "WHERE email = 'user@example.com' with no index on email column",
                "consequence": ["Full table scan (slow)", "Disk I/O increases", "CPU usage high"],
                "solution": "CREATE INDEX idx_email ON users(email)"
            },
            "Full Table Scan": {
                "problem": "SELECT * WHERE deleted_at IS NULL (no index on deleted_at)",
                "consequence": ["Scans entire table", "Slow for millions of rows", "Blocks other queries"],
                "solution": "Add index: CREATE INDEX idx_deleted_at ON table(deleted_at)"
            },
            "Inefficient JOIN": {
                "problem": "SELECT * FROM orders o, items i, users u WHERE...",
                "consequence": ["Cartesian product possible", "Temporary tables created", "High memory usage"],
                "solution": "Use proper JOIN syntax with ON clauses"
            }
        },
        "verification": [
            "All queries have appropriate indexes",
            "No N+1 query patterns detected",
            "JOIN conditions explicit",
            "LIMIT used for list queries",
            "Slow queries identified",
            "Query execution plan reviewed",
            "Indexes not duplicated",
            "Statistics updated"
        ],
        "anti_patterns": [
            "❌ Running query in loop (N+1)",
            "❌ SELECT * without WHERE clause",
            "❌ No indexes on WHERE columns",
            "❌ Implicit type conversion in WHERE",
            "❌ Functions on indexed columns",
            "❌ Not using LIMIT on large tables"
        ]
    },
    "cloud-native/kubernetes-validator": {
        "title": "Kubernetes Validator Skill",
        "core_principle": "Invalid Kubernetes manifests deploy silently then fail mysteriously. Validate before deploying.",
        "when_to_use": [
            "Before deploying to Kubernetes",
            "Validating YAML manifests",
            "Checking resource definitions",
            "Debugging pod failures",
            "Planning resource limits",
            "Reviewing deployment configs"
        ],
        "trigger_phrases": [
            "Is this Kubernetes config valid?",
            "Validate K8s manifest",
            "Check pod definition",
            "Review deployment config",
            "Why won't this deploy?",
            "Validate service mesh config"
        ],
        "what_does": {
            "YAML Validation": [
                "Syntax validation",
                "Required fields checking",
                "Type validation",
                "Resource limits validation"
            ],
            "Best Practices Check": [
                "Resource limits defined",
                "Health checks configured",
                "Security policies checked",
                "Image pull policies correct"
            ],
            "Configuration Analysis": [
                "Service discovery setup",
                "Volume mounts validation",
                "Environment variables",
                "Secret management"
            ]
        },
        "common_issues": {
            "Missing Resource Limits": {
                "problem": "Pod without CPU/memory limits",
                "consequence": ["Pod uses all available resources", "Starves other pods", "Cluster becomes unstable"],
                "solution": "Add resources.limits and resources.requests"
            },
            "No Health Checks": {
                "problem": "Deployment without liveness/readiness probes",
                "consequence": ["Pod marked healthy when failing", "Traffic sent to failing pods", "Bad user experience"],
                "solution": "Add livenessProbe and readinessProbe"
            },
            "Invalid Image": {
                "problem": "Image doesn't exist or wrong registry",
                "consequence": ["Pod never starts", "ImagePullBackOff error", "Service unavailable"],
                "solution": "Verify image exists, use correct registry URL"
            }
        },
        "verification": [
            "YAML syntax valid",
            "All required fields present",
            "Resource limits set",
            "Health probes configured",
            "Image pull policy correct",
            "Service labels match selectors",
            "Environment variables defined",
            "Security context configured"
        ],
        "anti_patterns": [
            "❌ No resource limits (pod can crash cluster)",
            "❌ No health checks (traffic to dead pods)",
            "❌ Latest image tag (unpredictable versions)",
            "❌ Running as root (security risk)",
            "❌ Storing secrets in ConfigMap",
            "❌ No pod disruption budgets"
        ]
    },
    "cloud-native/cloud-config-analyzer": {
        "title": "Cloud Config Analyzer Skill",
        "core_principle": "Misconfigured cloud resources leak data, waste money, and expose security vulnerabilities.",
        "when_to_use": [
            "Before deploying to cloud",
            "Reviewing cloud infrastructure",
            "Optimizing cloud costs",
            "Security audit of cloud resources",
            "Planning cloud migrations",
            "Investigating cloud failures"
        ],
        "trigger_phrases": [
            "Validate cloud config",
            "Check cloud security",
            "Optimize cloud costs",
            "Review cloud resources",
            "Find cloud misconfigurations",
            "Validate cloud permissions"
        ],
        "what_does": {
            "Security Checks": [
                "Public bucket detection",
                "Default security group rules",
                "Unencrypted databases",
                "Missing encryption keys"
            ],
            "Cost Optimization": [
                "Unused resources detection",
                "Instance size recommendations",
                "Storage optimization",
                "Bandwidth analysis"
            ],
            "Configuration Validation": [
                "IAM policy verification",
                "Network configuration",
                "Database backup settings",
                "Logging configuration"
            ]
        },
        "common_issues": {
            "Publicly Accessible Bucket": {
                "problem": "S3 bucket with public read/write access",
                "consequence": ["Data exposed to internet", "Anyone can download files", "Compliance violation"],
                "solution": "Remove public ACLs, use bucket policies"
            },
            "Unencrypted Database": {
                "problem": "RDS database without encryption at rest",
                "consequence": ["Data exposed if disk stolen", "Compliance violation", "Regulatory fines"],
                "solution": "Enable encryption at rest"
            },
            "Default Security Group": {
                "problem": "Security group allows all inbound traffic",
                "consequence": ["Exposed to the internet", "Unnecessary security risk", "Compliance issue"],
                "solution": "Restrict to specific ports/IPs"
            }
        },
        "verification": [
            "No publicly accessible storage",
            "Encryption enabled for sensitive data",
            "IAM policies follow least privilege",
            "Backup and recovery tested",
            "VPC configured correctly",
            "Security groups restrictive",
            "Logging enabled",
            "Cost optimization reviewed"
        ],
        "anti_patterns": [
            "❌ Public storage buckets (data leak)",
            "❌ Wide-open security groups (security risk)",
            "❌ Unencrypted sensitive data",
            "❌ Root account for everything (IAM issues)",
            "❌ No backup strategy",
            "❌ Oversized instances (wasted money)"
        ]
    },
    "database/sql-optimizer": {
        "title": "SQL Optimizer Skill",
        "core_principle": "Slow SQL queries compound. One slow query becomes 100 slow transactions. Optimize before scaling.",
        "when_to_use": [
            "Optimizing slow queries",
            "Database performance problems",
            "Before scaling database",
            "Query tuning after profiling",
            "Index strategy planning",
            "SQL review during code review"
        ],
        "trigger_phrases": [
            "Optimize this SQL",
            "Why is this query slow?",
            "How should I index this?",
            "Rewrite this inefficient query",
            "Query is taking 10 seconds",
            "Database CPU is at 100%"
        ],
        "what_does": {
            "Query Rewriting": [
                "Use appropriate JOIN types",
                "Push predicates down (WHERE before JOIN)",
                "Aggregate before joining",
                "Use UNION instead of OR",
                "Batch operations efficiently"
            ],
            "Index Strategy": [
                "Single column indexes",
                "Composite indexes",
                "Index selectivity analysis",
                "Covering indexes",
                "Partial indexes"
            ],
            "Execution Plan Analysis": [
                "Identify sequential scans",
                "Find sort operations",
                "Detect temporary table usage",
                "Analyze predicate pushdown",
                "Check index usage"
            ]
        },
        "common_issues": {
            "Missing WHERE Clause": {
                "problem": "SELECT * FROM orders (returns millions of rows)",
                "consequence": ["Memory overload", "Network congestion", "Database locks"],
                "solution": "Add WHERE clause to limit results"
            },
            "Implicit Type Conversion": {
                "problem": "WHERE user_id = '123' (user_id is INT, string compared)",
                "consequence": ["Index not used (full scan)", "Query slow", "Inconsistent results"],
                "solution": "Use correct type: WHERE user_id = 123"
            },
            "OR Condition Inefficiency": {
                "problem": "WHERE status = 'active' OR status = 'pending' OR status = 'processing'",
                "consequence": ["Multiple index scans", "Slower than IN clause", "Inefficient"],
                "solution": "Use IN: WHERE status IN ('active', 'pending', 'processing')"
            }
        },
        "verification": [
            "Queries use appropriate indexes",
            "No full table scans on large tables",
            "JOIN order optimized",
            "WHERE conditions push down correctly",
            "LIMIT applied to large result sets",
            "No implicit type conversions",
            "Aggregations efficient",
            "Execution plans reviewed"
        ],
        "anti_patterns": [
            "❌ SELECT * without LIMIT",
            "❌ Functions on indexed columns (breaks index)",
            "❌ Implicit type conversions",
            "❌ Complex OR conditions (use IN instead)",
            "❌ Correlated subqueries (N+1 queries)",
            "❌ Using LIKE on non-indexed columns"
        ]
    },
    "database/migration-validator": {
        "title": "Migration Validator Skill",
        "core_principle": "Bad migrations lock production, lose data, or cause downtime. Validate migrations before running.",
        "when_to_use": [
            "Before running database migrations",
            "Reviewing migration code",
            "Planning zero-downtime deploys",
            "Testing data transformations",
            "Validating schema changes",
            "Investigating migration failures"
        ],
        "trigger_phrases": [
            "Is this migration safe?",
            "Validate database migration",
            "Check data transformation",
            "Will this cause downtime?",
            "How to run this migration safely?",
            "Review migration strategy"
        ],
        "what_does": {
            "Safety Checks": [
                "Data loss detection",
                "Locking analysis",
                "Downtime estimation",
                "Rollback strategy",
                "Backup verification"
            ],
            "Data Validation": [
                "Data type compatibility",
                "Constraint violation detection",
                "Data transformation correctness",
                "Null value handling",
                "Index rebuild impact"
            ],
            "Performance Impact": [
                "Table lock duration",
                "Index recreation time",
                "Disk space requirements",
                "Query performance impact",
                "Connection pool impact"
            ]
        },
        "common_issues": {
            "Long-Running Migration": {
                "problem": "ALTER TABLE MODIFY COLUMN type on 1 billion row table (hours of table lock)",
                "consequence": ["Production database locked", "All queries blocked", "Downtime"],
                "solution": "Use online schema migration tools or shadow migration"
            },
            "Data Losing Migration": {
                "problem": "ALTER TABLE DROP COLUMN without backing up data first",
                "consequence": ["Data lost forever", "No recovery possible", "Regulatory violations"],
                "solution": "Backup first, verify before dropping"
            },
            "Unconvertible Data": {
                "problem": "Converting string column to integer without validation",
                "consequence": ["Non-numeric values can't convert", "Migration fails", "Partial data loss"],
                "solution": "Validate data before conversion, create temp column"
            }
        },
        "verification": [
            "Backup created before migration",
            "Migration is idempotent (safe to re-run)",
            "Rollback procedure documented",
            "Data loss checked (no DROP without backup)",
            "Downtime estimated and acceptable",
            "Index impact analyzed",
            "Test migration on staging first",
            "Performance impact acceptable"
        ],
        "anti_patterns": [
            "❌ No backup before migration",
            "❌ Long-running migrations on live table",
            "❌ No rollback plan",
            "❌ Data conversion without validation",
            "❌ Mixing multiple changes in one migration",
            "❌ No test run on staging"
        ]
    },
    "devops/cicd-validator": {
        "title": "CI/CD Validator Skill",
        "core_principle": "Bad CI/CD pipelines hide problems until production. Validate pipeline quality to catch issues early.",
        "when_to_use": [
            "Setting up CI/CD pipelines",
            "Reviewing GitHub Actions workflows",
            "Optimizing pipeline performance",
            "Debugging pipeline failures",
            "Planning deployment strategy",
            "Security audit of pipelines"
        ],
        "trigger_phrases": [
            "Validate CI/CD pipeline",
            "Review GitHub Actions workflow",
            "Optimize pipeline performance",
            "Why did the build fail?",
            "Design deployment strategy",
            "Check pipeline security"
        ],
        "what_does": {
            "Pipeline Structure": [
                "Stage sequencing",
                "Parallel job optimization",
                "Dependency management",
                "Artifact handling"
            ],
            "Quality Checks": [
                "Test coverage enforcement",
                "Code style validation",
                "Security scanning",
                "Dependency checking"
            ],
            "Deployment Safety": [
                "Environment separation",
                "Approval gates",
                "Rollback strategy",
                "Health checks after deploy"
            ]
        },
        "common_issues": {
            "Slow Pipeline": {
                "problem": "Tests run sequentially instead of parallel, 30 min build time",
                "consequence": ["Slow feedback to developers", "Low deployment frequency", "Bottleneck"],
                "solution": "Run tests in parallel, cache dependencies"
            },
            "No Test Coverage Gate": {
                "problem": "Pipeline doesn't fail if test coverage decreases",
                "consequence": ["Code quality degrades over time", "Bugs not caught", "Technical debt"],
                "solution": "Add coverage threshold check, fail if below threshold"
            },
            "Manual Approval Gate Missing": {
                "problem": "Any commit auto-deploys to production",
                "consequence": ["Broken features deploy", "Data loss possible", "Downtime risk"],
                "solution": "Add approval gate before production deployment"
            }
        },
        "verification": [
            "All tests run automatically",
            "Code quality checks enforce standards",
            "Security scanning enabled",
            "Artifacts properly versioned",
            "Environments properly separated",
            "Manual approval for production",
            "Deployment health checks",
            "Rollback procedure documented"
        ],
        "anti_patterns": [
            "❌ Manual deployment steps",
            "❌ No test coverage enforcement",
            "❌ Sequential job execution (slow)",
            "❌ No approval gates to production",
            "❌ Credentials in pipeline files",
            "❌ No rollback plan"
        ]
    },
    "devops/infrastructure-analyzer": {
        "title": "Infrastructure Analyzer Skill",
        "core_principle": "Good infrastructure scales. Bad infrastructure breaks at scale. Analyze before problems cascade.",
        "when_to_use": [
            "Planning infrastructure",
            "Scaling for growth",
            "Performance bottleneck investigation",
            "Disaster recovery planning",
            "Cost optimization",
            "Infrastructure code review"
        ],
        "trigger_phrases": [
            "Analyze infrastructure design",
            "Scale this for 10x growth",
            "Find infrastructure bottlenecks",
            "Plan disaster recovery",
            "Optimize infrastructure costs",
            "Review infrastructure as code"
        ],
        "what_does": {
            "Capacity Planning": [
                "Current utilization analysis",
                "Growth projections",
                "Scaling bottlenecks",
                "Resource requirements"
            ],
            "High Availability": [
                "Single points of failure detection",
                "Failover strategy analysis",
                "Backup completeness",
                "Disaster recovery validation"
            ],
            "Cost Optimization": [
                "Resource utilization analysis",
                "Right-sizing recommendations",
                "Reserved capacity analysis",
                "Unnecessary services"
            ]
        },
        "common_issues": {
            "Single Point of Failure": {
                "problem": "Only one database server, no replication",
                "consequence": ["Server fails -> entire app down", "No disaster recovery", "RTO is infinite"],
                "solution": "Add replica, failover automation"
            },
            "No Backup Strategy": {
                "problem": "Data deleted -> no backup to restore",
                "consequence": ["Data loss forever", "No recovery possible", "Regulatory violations"],
                "solution": "Regular backups, test restore procedures"
            },
            "Manual Scaling": {
                "problem": "Traffic spikes -> manually provision servers",
                "consequence": ["Delayed response to load", "Expensive", "User impact"],
                "solution": "Auto-scaling groups, load balancing"
            }
        },
        "verification": [
            "No single points of failure",
            "Backup strategy documented and tested",
            "Failover automation in place",
            "Monitoring and alerting configured",
            "Scaling plan documented",
            "Disaster recovery tested",
            "Cost optimization reviewed",
            "Security hardened"
        ],
        "anti_patterns": [
            "❌ Single server (single point of failure)",
            "❌ Manual scaling (slow, expensive)",
            "❌ No backups (data loss risk)",
            "❌ No monitoring (problems unknown)",
            "❌ Tight coupling (can't scale independently)",
            "❌ No disaster recovery plan"
        ]
    },
    "frameworks/flask-django-analyzer": {
        "title": "Flask/Django Analyzer Skill",
        "core_principle": "Web frameworks enable fast development but bad patterns create maintenance nightmares.",
        "when_to_use": [
            "Reviewing Flask/Django code",
            "Planning Flask/Django project structure",
            "Debugging framework issues",
            "Optimizing framework performance",
            "Security audit of Flask/Django apps",
            "Database query optimization"
        ],
        "trigger_phrases": [
            "Review Flask/Django patterns",
            "Optimize this view",
            "Check database queries",
            "Structure Flask project",
            "Improve Django ORM usage",
            "Security audit of Flask app"
        ],
        "what_does": {
            "Code Organization": [
                "Blueprint/app structure",
                "View organization",
                "Model relationships",
                "Middleware configuration"
            ],
            "ORM Optimization": [
                "Query efficiency",
                "N+1 query detection",
                "Select_related/prefetch_related usage",
                "Database indexing strategy"
            ],
            "Best Practices": [
                "Error handling patterns",
                "Logging configuration",
                "Testing structure",
                "Security configurations"
            ]
        },
        "common_issues": {
            "Lazy-loaded Queries": {
                "problem": "for item in items: print(item.user.name) (N+1 queries)",
                "consequence": ["1 query + N queries for relationships", "Extremely slow", "Database overload"],
                "solution": "Use select_related/prefetch_related"
            },
            "View Too Complex": {
                "problem": "Single view handles auth, queries, business logic, response (200+ lines)",
                "consequence": ["Hard to test", "Hard to maintain", "Hard to reuse"],
                "solution": "Extract to services, use decorators"
            }
        },
        "verification": [
            "Views under 50 lines",
            "Business logic in services",
            "ORM queries optimized",
            "No N+1 query patterns",
            "Error handling comprehensive",
            "Tests cover main paths",
            "Security checks in place",
            "Logging configured"
        ],
        "anti_patterns": [
            "❌ Lazy-loaded queries (N+1)",
            "❌ Views with business logic (hard to test)",
            "❌ Hardcoded database connections",
            "❌ No error handling",
            "❌ Missing CSRF/XSS protection",
            "❌ SQL injection vulnerabilities"
        ]
    },
    "frameworks/spring-analyzer": {
        "title": "Spring Framework Analyzer Skill",
        "core_principle": "Spring enables enterprise features but bad configuration leads to slow, unmaintainable code.",
        "when_to_use": [
            "Reviewing Spring code",
            "Spring Boot configuration",
            "Performance optimization",
            "Dependency injection review",
            "Security audit of Spring apps",
            "Database access optimization"
        ],
        "trigger_phrases": [
            "Review Spring patterns",
            "Optimize Spring performance",
            "Spring data JPA analysis",
            "Check Spring security config",
            "Spring transaction handling",
            "Analyze Spring bean configuration"
        ],
        "what_does": {
            "Bean Configuration": [
                "Dependency injection patterns",
                "Bean lifecycle",
                "Singleton vs prototype",
                "Circular dependency detection"
            ],
            "Performance": [
                "Lazy initialization strategy",
                "Database connection pooling",
                "Caching configuration",
                "Query optimization"
            ],
            "Best Practices": [
                "Exception handling",
                "Logging configuration",
                "Unit test patterns",
                "Integration test setup"
            ]
        },
        "common_issues": {
            "Circular Dependencies": {
                "problem": "Bean A depends on B, Bean B depends on A",
                "consequence": ["Wiring fails", "App won't start", "Refactoring needed"],
                "solution": "Restructure beans, use setter injection"
            },
            "Slow Queries": {
                "problem": "Spring Data JPA lazy loading in loops",
                "consequence": ["N+1 queries", "Database overload", "Timeouts"],
                "solution": "Use @EntityGraph or fetch joins"
            }
        },
        "verification": [
            "No circular dependencies",
            "Transaction boundaries clear",
            "Connection pool configured",
            "Lazy loading minimized",
            "Exception handling comprehensive",
            "Logging configured",
            "Tests cover main paths",
            "Security properly configured"
        ],
        "anti_patterns": [
            "❌ Circular dependencies",
            "❌ Lazy loading in loops (N+1)",
            "❌ Global exception handlers (lose context)",
            "❌ No transaction management",
            "❌ Blocking I/O in async code",
            "❌ Hardcoded configuration"
        ]
    },
    "frontend/css-validator": {
        "title": "CSS Validator Skill",
        "core_principle": "CSS is simple to write badly, hard to maintain if done wrong. Validate CSS for consistency and performance.",
        "when_to_use": [
            "Validating CSS syntax",
            "Performance optimization",
            "Accessibility review",
            "Responsive design validation",
            "Code style enforcement",
            "Cross-browser compatibility"
        ],
        "trigger_phrases": [
            "Validate CSS syntax",
            "Optimize CSS performance",
            "Check responsive design",
            "Review CSS specificity",
            "Accessibility audit",
            "CSS organization review"
        ],
        "what_does": {
            "Syntax Validation": [
                "Valid CSS selectors",
                "Proper property values",
                "Color format validation",
                "Unit consistency"
            ],
            "Performance": [
                "Unused styles detection",
                "Specificity analysis",
                "Media query optimization",
                "Animation performance"
            ],
            "Best Practices": [
                "Naming conventions",
                "Component organization",
                "Responsive breakpoints",
                "Accessibility considerations"
            ]
        },
        "common_issues": {
            "High Specificity": {
                "problem": ".container .section .item.special#main { color: red; } (very high specificity)",
                "consequence": ["Hard to override", "CSS bloat", "Maintenance nightmare"],
                "solution": "Use lower specificity, BEM naming"
            },
            "Not Responsive": {
                "problem": "Fixed widths, no media queries",
                "consequence": ["Broken on mobile", "Bad user experience", "Low SEO"],
                "solution": "Use responsive units, media queries"
            }
        },
        "verification": [
            "CSS syntax valid",
            "Selectors use low specificity",
            "BEM or similar naming convention",
            "Responsive breakpoints defined",
            "Colors accessible (contrast ratio)",
            "No unused styles",
            "Animations performant (transform/opacity)",
            "Cross-browser compatible"
        ],
        "anti_patterns": [
            "❌ High specificity (hard to override)",
            "❌ !important everywhere",
            "❌ Inline styles (not maintainable)",
            "❌ Not responsive (mobile broken)",
            "❌ Poor color contrast (accessibility)",
            "❌ Expensive animations (paint/reflow)"
        ]
    },
    "frontend/component-analyzer": {
        "title": "Component Analyzer Skill",
        "core_principle": "Good components are reusable, testable, and composable. Bad components are brittle and hard to maintain.",
        "when_to_use": [
            "Reviewing React/Vue/Angular components",
            "Planning component architecture",
            "Component reusability audit",
            "Performance optimization",
            "Testing strategy planning",
            "API contract validation"
        ],
        "trigger_phrases": [
            "Analyze component structure",
            "Review component design",
            "Component reusability audit",
            "Optimize component rendering",
            "Component API review",
            "Improve component testability"
        ],
        "what_does": {
            "Component Design": [
                "Props/input validation",
                "State management approach",
                "Lifecycle understanding",
                "Composition patterns"
            ],
            "Performance": [
                "Unnecessary re-renders",
                "Memoization opportunities",
                "Bundle size impact",
                "Lazy loading strategy"
            ],
            "Reusability": [
                "Props flexibility",
                "Composition ability",
                "Customization options",
                "Variant handling"
            ]
        },
        "common_issues": {
            "Over-Specific Component": {
                "problem": "Component hardcoded for one use case, not reusable",
                "consequence": ["Can't reuse elsewhere", "Code duplication", "Maintenance burden"],
                "solution": "Extract props, make flexible"
            },
            "Unnecessary Re-renders": {
                "problem": "Parent re-renders, all children re-render even unchanged",
                "consequence": ["Performance degradation", "Slow app", "Bad user experience"],
                "solution": "Use React.memo, useMemo"
            }
        },
        "verification": [
            "Component props clearly defined",
            "State minimal and local",
            "No unnecessary side effects",
            "Reusable across contexts",
            "Performance optimized",
            "Testable in isolation",
            "Error states handled",
            "Props documented"
        ],
        "anti_patterns": [
            "❌ Over-specific (not reusable)",
            "❌ Prop drilling (too many props passed)",
            "❌ Global state for everything",
            "❌ No error boundaries",
            "❌ Side effects in render",
            "❌ Tightly coupled to parent"
        ]
    },
    "frontend/bundle-analyzer": {
        "title": "Bundle Analyzer Skill",
        "core_principle": "Bundle size directly impacts page load time. Smaller bundles = faster pages = better UX.",
        "when_to_use": [
            "Optimizing bundle size",
            "Performance budgeting",
            "Dependency analysis",
            "Code splitting planning",
            "Performance monitoring",
            "Production deployment review"
        ],
        "trigger_phrases": [
            "Analyze bundle size",
            "Optimize JavaScript bundle",
            "Find code splitting opportunities",
            "Check dependency sizes",
            "Performance budget review",
            "Bundle analysis report"
        ],
        "what_does": {
            "Bundle Analysis": [
                "Total bundle size",
                "Individual module sizes",
                "Dependency relationships",
                "Duplicate detection"
            ],
            "Optimization": [
                "Code splitting opportunities",
                "Tree-shaking effectiveness",
                "Compression analysis",
                "Dynamic import candidates"
            ],
            "Performance": [
                "Load time estimation",
                "Memory impact",
                "Parse time analysis",
                "Cache effectiveness"
            ]
        },
        "common_issues": {
            "Large Dependencies": {
                "problem": "Including entire lodash library for one function",
                "consequence": ["Bundle 50KB larger", "Slower load", "Slower parse"],
                "solution": "Use cherry-pick imports or smaller libraries"
            },
            "No Code Splitting": {
                "problem": "All code in single bundle, even admin pages users never visit",
                "consequence": ["Initial load slow", "Wasted bandwidth", "Slow FCP"],
                "solution": "Route-based code splitting"
            }
        },
        "verification": [
            "Bundle size under budget",
            "No duplicate dependencies",
            "Large dependencies justified",
            "Code splitting implemented",
            "Tree-shaking enabled",
            "Compression optimized",
            "Cache headers configured",
            "Performance budget enforced"
        ],
        "anti_patterns": [
            "❌ No code splitting",
            "❌ Large dependencies for small use cases",
            "❌ Duplicate dependencies",
            "❌ No tree-shaking",
            "❌ Development dependencies in production",
            "❌ No compression"
        ]
    },
    "languages/python-analyzer": {
        "title": "Python Analyzer Skill",
        "core_principle": "Python makes it easy to write bad code. Analyze code quality to prevent technical debt.",
        "when_to_use": [
            "Python code review",
            "Performance optimization",
            "Type safety checking",
            "Testing strategy",
            "Security audit",
            "Maintainability assessment"
        ],
        "trigger_phrases": [
            "Analyze Python code quality",
            "Review Python patterns",
            "Optimize Python performance",
            "Check Python type hints",
            "Python security audit",
            "Improve Python testability"
        ],
        "what_does": {
            "Code Quality": [
                "PEP 8 compliance",
                "Type hint coverage",
                "Complexity analysis",
                "Naming conventions"
            ],
            "Performance": [
                "Algorithm efficiency",
                "Memory usage",
                "Dependency imports",
                "Loop optimization"
            ],
            "Best Practices": [
                "Exception handling",
                "Error messages",
                "Logging patterns",
                "Testing coverage"
            ]
        },
        "common_issues": {
            "No Type Hints": {
                "problem": "def process(data): ... (what type is data?)",
                "consequence": ["IDE can't help", "Runtime errors", "Hard to understand"],
                "solution": "Add type hints: def process(data: Dict[str, Any]) -> bool:"
            },
            "Mutable Default Arguments": {
                "problem": "def append(item, items=[]) (default list shared across calls)",
                "consequence": ["Unexpected behavior", "Items persist between calls", "Bugs"],
                "solution": "Use None: def append(item, items=None):"
            }
        },
        "verification": [
            "Type hints on all functions",
            "No bare except clauses",
            "Exception types specific",
            "Docstrings present",
            "Tests cover main paths",
            "Performance acceptable",
            "Security checked",
            "Code style consistent"
        ],
        "anti_patterns": [
            "❌ No type hints",
            "❌ Bare except (catch everything)",
            "❌ Mutable default arguments",
            "❌ Global variables",
            "❌ No error handling",
            "❌ Print debugging (use logging)"
        ]
    },
    "languages/javascript-analyzer": {
        "title": "JavaScript Analyzer Skill",
        "core_principle": "JavaScript's flexibility is a double-edged sword. Analyze code to prevent runtime surprises.",
        "when_to_use": [
            "JavaScript code review",
            "Performance optimization",
            "Browser compatibility",
            "Security audit",
            "Testing coverage",
            "Async code analysis"
        ],
        "trigger_phrases": [
            "Analyze JavaScript code",
            "Review JavaScript patterns",
            "Check async code",
            "Optimize JavaScript performance",
            "JavaScript security audit",
            "Improve JavaScript testability"
        ],
        "what_does": {
            "Code Quality": [
                "Async/await patterns",
                "Error handling",
                "Variable scoping",
                "Function complexity"
            ],
            "Performance": [
                "DOM manipulation efficiency",
                "Event listener leaks",
                "Memory leaks",
                "Script load optimization"
            ],
            "Best Practices": [
                "Type checking options",
                "Testing patterns",
                "Logging approach",
                "Security practices"
            ]
        },
        "common_issues": {
            "Callback Hell": {
                "problem": "nested callbacks making code unreadable",
                "consequence": ["Hard to read", "Hard to error handle", "Hard to test"],
                "solution": "Use async/await"
            },
            "Not Awaiting Promises": {
                "problem": "async function fetch().then(...) without await",
                "consequence": ["Race conditions", "Unexpected timing", "Bugs"],
                "solution": "Use await or return promise chain"
            }
        },
        "verification": [
            "Async/await used correctly",
            "Error handling comprehensive",
            "No memory leaks",
            "DOM manipulation optimized",
            "Event listeners cleaned up",
            "Tests cover main paths",
            "No console.log in production",
            "Browser compatibility checked"
        ],
        "anti_patterns": [
            "❌ Callback hell (hard to read)",
            "❌ Not handling promise rejections",
            "❌ Blocking main thread",
            "❌ Event listener leaks",
            "❌ Global variables",
            "❌ No error handling"
        ]
    },
    "microservices/service-mesh-analyzer": {
        "title": "Service Mesh Analyzer Skill",
        "core_principle": "Service mesh adds complexity to solve problems. Make sure it's solving the right problems.",
        "when_to_use": [
            "Planning service mesh adoption",
            "Service mesh configuration review",
            "Traffic management optimization",
            "Security policy review",
            "Performance monitoring",
            "Troubleshooting mesh issues"
        ],
        "trigger_phrases": [
            "Analyze service mesh setup",
            "Review Istio configuration",
            "Optimize service mesh performance",
            "Service mesh security audit",
            "Check traffic routing",
            "Service mesh troubleshooting"
        ],
        "what_does": {
            "Traffic Management": [
                "Load balancing strategy",
                "Circuit breaker configuration",
                "Retry policy",
                "Timeout settings"
            ],
            "Security": [
                "mTLS configuration",
                "Authorization policies",
                "Authentication setup",
                "Certificate rotation"
            ],
            "Observability": [
                "Distributed tracing",
                "Metrics collection",
                "Error tracking",
                "Performance monitoring"
            ]
        },
        "common_issues": {
            "Misconfigured Circuit Breaker": {
                "problem": "Circuit breaker trips too early or never breaks",
                "consequence": ["Unnecessary timeouts or cascading failures", "Service unavailable"],
                "solution": "Tune thresholds based on actual metrics"
            },
            "Missing Timeout": {
                "problem": "No timeout configured, requests hang forever",
                "consequence": ["Resource exhaustion", "Cascading failures", "Degradation"],
                "solution": "Set appropriate timeout values"
            }
        },
        "verification": [
            "mTLS enabled between services",
            "Authorization policies defined",
            "Circuit breakers configured",
            "Timeouts appropriate",
            "Retries configured",
            "Distributed tracing enabled",
            "Metrics collected",
            "Alerts configured"
        ],
        "anti_patterns": [
            "❌ Service mesh for 2 services (overkill)",
            "❌ mTLS disabled (security risk)",
            "❌ No circuit breakers (cascading failures)",
            "❌ No timeouts (hanging requests)",
            "❌ Missing observability (blind)",
            "❌ All traffic retried (amplification)"
        ]
    },
    "microservices/api-contract-validator": {
        "title": "API Contract Validator Skill",
        "core_principle": "Service integration depends on API contracts. Breaking contracts breaks integration.",
        "when_to_use": [
            "Microservice API review",
            "Contract testing planning",
            "API versioning strategy",
            "Integration testing",
            "Backward compatibility checking",
            "Schema evolution planning"
        ],
        "trigger_phrases": [
            "Validate API contract",
            "Review API breaking changes",
            "Check backward compatibility",
            "Plan API versioning",
            "Contract testing setup",
            "Analyze schema evolution"
        ],
        "what_does": {
            "Contract Definition": [
                "Request schema validation",
                "Response schema validation",
                "Header requirements",
                "Status code meanings"
            ],
            "Compatibility": [
                "Breaking change detection",
                "Backward compatibility",
                "Forward compatibility",
                "Version management"
            ],
            "Testing": [
                "Contract test generation",
                "Mock server generation",
                "Consumer validation",
                "Provider validation"
            ]
        },
        "common_issues": {
            "Breaking Change": {
                "problem": "API changed request format without versioning",
                "consequence": ["Old clients break", "Integration fails", "Downtime"],
                "solution": "Use versioning, document breaking changes"
            },
            "Missing Validation": {
                "problem": "Consumer doesn't validate response schema",
                "consequence": ["Unexpected fields ignored", "Missing fields cause errors"],
                "solution": "Add schema validation in consumer"
            }
        },
        "verification": [
            "Request schema defined and validated",
            "Response schema defined and validated",
            "Status codes documented",
            "Error responses consistent",
            "API versioning strategy clear",
            "Breaking changes documented",
            "Backward compatible changes tested",
            "Contract tests passing"
        ],
        "anti_patterns": [
            "❌ No API versioning",
            "❌ No schema validation",
            "❌ Breaking changes without notice",
            "❌ No contract testing",
            "❌ Implicit requirements (not documented)",
            "❌ No deprecation period for changes"
        ]
    }
}

def create_skill_md(category, skill_name, content):
    """Create enhanced SKILL.md content"""

    parts = []

    # Frontmatter
    parts.append("---")
    parts.append(f'name: {skill_name}')
    description = content.get('description', f'Enhanced skill for {skill_name}')
    parts.append(f'description: "{description}"')
    parts.append('license: MIT')
    parts.append("---")
    parts.append("")

    # Title
    parts.append(f"# {content['title']}")
    parts.append("")

    # Overview
    parts.append("## Overview")
    overview = content.get('overview', f"Detailed analysis and validation of {skill_name}.")
    parts.append(overview)
    parts.append("")
    parts.append(f"**Core Principle**: {content['core_principle']}")
    parts.append("")

    # When to Use
    parts.append("## When to Use")
    parts.append("")
    parts.append("**Always:**")
    for item in content['when_to_use']:
        parts.append(f"- {item}")
    parts.append("")
    parts.append("**Trigger phrases:**")
    for phrase in content['trigger_phrases']:
        parts.append(f"- \"{phrase}\"")
    parts.append("")

    # What it Does
    parts.append(f"## What {content['title'].split()[0]} Does")
    parts.append("")
    for section, items in content['what_does'].items():
        parts.append(f"### {section}")
        for item in items:
            parts.append(f"- {item}")
        parts.append("")

    # Common Issues
    parts.append("## Common Issues")
    parts.append("")
    for issue_name, issue_data in content['common_issues'].items():
        parts.append(f"### {issue_name}")
        parts.append("```")
        parts.append(f"Problem:")
        parts.append(issue_data['problem'])
        parts.append("")
        parts.append("Consequence:")
        for consequence in issue_data['consequence']:
            parts.append(f"- {consequence}")
        parts.append("")
        parts.append("Solution:")
        parts.append(issue_data['solution'])
        parts.append("```")
        parts.append("")

    # Verification Checklist
    parts.append("## Verification Checklist")
    parts.append("")
    for item in content['verification']:
        parts.append(f"- [ ] {item}")
    parts.append("")

    # When Stuck
    parts.append("## When Stuck")
    parts.append("")
    parts.append("| Problem | Solution |")
    parts.append("|---------|----------|")
    parts.append("| \"Not sure where to start\" | Identify the specific issue using the Common Issues section above. |")
    parts.append("| \"Performance is poor\" | Profile first to identify bottleneck before optimizing. |")
    parts.append("| \"Not sure about best practices\" | Check the Verification Checklist to understand quality standards. |")
    parts.append("")

    # Anti-Patterns
    parts.append("## Anti-Patterns (Red Flags)")
    parts.append("")
    for pattern in content['anti_patterns']:
        parts.append(pattern)
    parts.append("")

    # Related Skills
    parts.append("## Related Skills")
    parts.append("")
    parts.append("- **code-review** - Review implementation of this skill")
    parts.append("- **architecture-analyzer** - Analyze larger design implications")
    parts.append("")

    return "\n".join(parts)

# Create all enhanced SKILL.md files
for path, content in skills_content.items():
    category, skill_name = path.split('/')
    skill_path = f"/Users/jarry/github/ai-skills/{category}/{skill_name}"
    skill_md_path = f"{skill_path}/SKILL.md"

    # Create SKILL.md
    skill_md_content = create_skill_md(category, skill_name, content)

    with open(skill_md_path, 'w') as f:
        f.write(skill_md_content)

    print(f"✅ Enhanced {category}/{skill_name}/SKILL.md ({len(skill_md_content)} bytes)")

print(f"\n✅ All {len(skills_content)} SKILL.md files enhanced!")
