#!/usr/bin/env python3
"""
为所有 tools 下的 Skills 创建详细的 SKILL.md 文件
参照用户提供的高质量格式标准
"""

SKILLS_CONTENT = {
    "yaml-validator": {
        "title": "YAML Validator Skill",
        "overview": "YAML is widely used for configuration (Kubernetes, Docker Compose, CI/CD). Invalid YAML breaks deployments silently. Validate before deploying.\n\n**Core Principle**: Valid YAML is structured data. Invalid YAML is a silent failure.",
        "always": [
            "Validating Kubernetes manifests",
            "Checking Docker Compose files",
            "Before committing configuration",
            "Debugging deployment failures",
            "When indentation looks suspicious"
        ],
        "triggers": [
            '"Is this YAML valid?"',
            '"Parse this YAML"',
            '"Fix this YAML error"',
            '"Validate Kubernetes config"',
            '"What\'s wrong with this Docker Compose?"'
        ]
    },
    "regex-tester": {
        "title": "Regex Tester Skill",
        "overview": "Regular expressions are powerful but easy to break. Test regex before using in production code. Invalid regex patterns cause runtime errors or miss cases.\n\n**Core Principle**: If you didn't test the regex with edge cases, it doesn't work.",
        "always": [
            "Writing email validation patterns",
            "Building URL matching patterns",
            "Creating text extraction patterns",
            "Validating input formats",
            "Testing regex performance on large data"
        ],
        "triggers": [
            '"Does this regex work?"',
            '"Test this pattern"',
            '"Why doesn\'t this regex match?"',
            '"Generate a regex for..."',
            '"Optimize this regex"'
        ]
    },
    "sql-generator": {
        "title": "SQL Generator Skill",
        "overview": "SQL is the language of data. Invalid SQL causes data loss, corruption, or security breaches. Validate before executing against production databases.\n\n**Core Principle**: SQL is permanent. Test first, execute once.",
        "always": [
            "Writing new database queries",
            "Optimizing slow queries",
            "Creating migrations",
            "Before executing against production",
            "Checking for SQL injection vulnerabilities"
        ],
        "triggers": [
            '"Generate this SQL"',
            '"Is this query correct?"',
            '"Why is this slow?"',
            '"Optimize this query"',
            '"Check for SQL injection"'
        ]
    },
    "env-validator": {
        "title": "Environment Validator Skill",
        "overview": "Environment variables control application behavior. Missing or incorrect variables cause runtime failures. Validate before deployment.\n\n**Core Principle**: Environment errors are caught at startup, not runtime.",
        "always": [
            "Before deploying to production",
            "When application fails to start",
            "Checking for exposed secrets",
            "Validating database connections",
            "Verifying API credentials"
        ],
        "triggers": [
            '"Check my environment"',
            '"Are secrets exposed?"',
            '"Missing environment variable"',
            '"Validate config"'
        ]
    },
    "stack-trace-analyzer": {
        "title": "Stack Trace Analyzer Skill",
        "overview": "Stack traces tell the story of what went wrong. Read them correctly to find bugs fast. Misinterpreted stack traces waste debugging time.\n\n**Core Principle**: The stack trace is your roadmap to the bug.",
        "always": [
            "Debugging crashes",
            "Understanding exceptions",
            "Finding where errors originate",
            "When error messages are cryptic",
            "Analyzing core dumps"
        ],
        "triggers": [
            '"What does this error mean?"',
            '"Help me debug this"',
            '"Where is the crash?"',
            '"Analyze this traceback"'
        ]
    },
    "dockerfile-analyzer": {
        "title": "Dockerfile Analyzer Skill",
        "overview": "Docker images can bloat to gigabytes with one mistake. Invalid Dockerfiles fail to build or create insecure containers. Validate before building.\n\n**Core Principle**: Lean images are fast. Secure images are trustworthy.",
        "always": [
            "Before building production images",
            "Optimizing image size",
            "Checking security practices",
            "Verifying best practices",
            "Improving build performance"
        ],
        "triggers": [
            '"Is this Dockerfile good?"',
            '"How big is this image?"',
            '"Make this smaller"',
            '"Check Docker best practices"',
            '"Is this secure?"'
        ]
    },
    "api-tester": {
        "title": "API Tester Skill",
        "overview": "APIs are contracts. Broken APIs break applications. Test endpoints before integrating. Invalid responses cause cascading failures.\n\n**Core Principle**: API contracts must be verified before deployment.",
        "always": [
            "Testing API endpoints",
            "Validating responses",
            "Checking status codes",
            "Verifying headers",
            "Testing authentication"
        ],
        "triggers": [
            '"Test this endpoint"',
            '"Is this API working?"',
            '"Debug this response"',
            '"Check API response"'
        ]
    },
    "log-analyzer": {
        "title": "Log Analyzer Skill",
        "overview": "Logs are the black box flight recorder. Read them correctly to understand what happened. Misread logs lead to wrong conclusions.\n\n**Core Principle**: Logs don't lie. Logs tell exactly what happened.",
        "always": [
            "Debugging production issues",
            "Finding performance bottlenecks",
            "Identifying error patterns",
            "Understanding system behavior",
            "Post-incident analysis"
        ],
        "triggers": [
            '"Analyze these logs"',
            '"Find the error"',
            '"What went wrong?"',
            '"Find performance issues"'
        ]
    },
    "file-analyzer": {
        "title": "File Analyzer Skill",
        "overview": "Large files waste storage, slow down deployments, and hide problems. Analyze before deployment. Uncontrolled file growth indicates bugs.\n\n**Core Principle**: Track what files exist and why.",
        "always": [
            "Before deployments",
            "Investigating disk usage",
            "Finding build artifacts",
            "Identifying duplicates",
            "Reducing repository size"
        ],
        "triggers": [
            '"Find large files"',
            '"What\'s taking up space?"',
            '"Detect duplicates"',
            '"Analyze directory"'
        ]
    },
    "code-formatter": {
        "title": "Code Formatter Skill",
        "overview": "Inconsistent formatting wastes review time and creates merge conflicts. Format code before committing. Unformatted code is unprofessional.\n\n**Core Principle**: Consistent formatting reduces friction.",
        "always": [
            "Before committing code",
            "When joining a team",
            "Standardizing across codebase",
            "Preparing for review",
            "Reducing diff noise"
        ],
        "triggers": [
            '"Format this code"',
            '"Fix indentation"',
            '"Standardize formatting"',
            '"Apply code style"'
        ]
    },
    "security-scanner": {
        "title": "Security Scanner Skill",
        "overview": "Security vulnerabilities are silent. Code looks fine but contains exploits. Scan before deploying. Unscanned code is a liability.\n\n**Core Principle**: Assume your code has vulnerabilities until proven secure.",
        "always": [
            "Before production deployment",
            "When code handles user data",
            "Checking for common mistakes",
            "During code review",
            "After dependencies update"
        ],
        "triggers": [
            '"Scan for security issues"',
            '"Is this secure?"',
            '"Check for vulnerabilities"',
            '"Find security bugs"'
        ]
    },
    "markdown-validator": {
        "title": "Markdown Validator Skill",
        "overview": "Documentation breaks silently. Broken links, invalid syntax, and missing files make docs unusable. Validate before publishing.\n\n**Core Principle**: Documentation is code. Validate it like code.",
        "always": [
            "Before publishing documentation",
            "Checking for broken links",
            "Validating syntax",
            "Before commit",
            "Testing documentation rendering"
        ],
        "triggers": [
            '"Check this README"',
            '"Find broken links"',
            '"Validate documentation"',
            '"Is this markdown correct?"'
        ]
    },
    "changelog-generator": {
        "title": "Changelog Generator Skill",
        "overview": "Changes are history. Document them automatically from commits. Manual changelogs are incomplete and out of sync.\n\n**Core Principle**: Generated history is accurate history.",
        "always": [
            "Before release",
            "Documenting changes",
            "Publishing release notes",
            "Tracking version history",
            "Creating user-facing documentation"
        ],
        "triggers": [
            '"Generate changelog"',
            '"Create release notes"',
            '"What changed?"',
            '"Document these changes"'
        ]
    },
    "version-manager": {
        "title": "Version Manager Skill",
        "overview": "Versions are agreements. Breaking versions without notice break users' applications. Validate version numbers follow semantic versioning.\n\n**Core Principle**: Versions communicate contract changes to users.",
        "always": [
            "Before releasing",
            "Planning breaking changes",
            "Determining release type",
            "Updating dependencies",
            "Communicating changes"
        ],
        "triggers": [
            '"Is this version correct?"',
            '"What\'s the next version?"',
            '"Check semver"',
            '"Validate version"'
        ]
    },
    "git-analysis": {
        "title": "Git Analysis Skill",
        "overview": "Git history is a project timeline. Read it correctly to understand how code evolved. Misread history wastes debugging time.\n\n**Core Principle**: Git tells you what changed and why.",
        "always": [
            "Understanding code evolution",
            "Finding when bugs were introduced",
            "Tracking feature development",
            "Understanding refactorings",
            "Analyzing code patterns"
        ],
        "triggers": [
            '"Analyze this repository"',
            '"When was this added?"',
            '"Who wrote this?"',
            '"Analyze commits"'
        ]
    },
    "dependency-analyzer": {
        "title": "Dependency Analyzer Skill",
        "overview": "Dependencies are risks. Vulnerabilities, outdated versions, and unused packages accumulate. Analyze before deploying.\n\n**Core Principle**: Know what you depend on.",
        "always": [
            "Before production deployment",
            "Checking security updates",
            "Finding unused packages",
            "Detecting conflicts",
            "Managing technical debt"
        ],
        "triggers": [
            '"Check for vulnerabilities"',
            '"Find unused dependencies"',
            '"Update dependencies"',
            '"Detect conflicts"'
        ]
    },
    "architecture-analyzer": {
        "title": "Architecture Analyzer Skill",
        "overview": "Architecture determines if a system is maintainable. Bad architecture hides problems until they cascade. Analyze before complexity spirals.\n\n**Core Principle**: Fix architecture early. Fixes cascade down.",
        "always": [
            "Reviewing new designs",
            "Refactoring legacy code",
            "Planning major changes",
            "Finding coupling problems",
            "Improving maintainability"
        ],
        "triggers": [
            '"Is the design good?"',
            '"Find architecture issues"',
            '"How should this be organized?"',
            '"Identify coupling"'
        ]
    }
}

def get_verification_checklist(skill_name):
    """Generate verification checklist for skill"""
    checklists = {
        "json-validator": [
            "JSON syntax is valid (passes JSON parser)",
            "All required fields present",
            "Data types match schema",
            "Nested structures are correct",
            "No trailing commas or single quotes",
            "All keys are properly quoted",
            "File encoding is UTF-8",
            "No circular references (if applicable)",
            "Size is reasonable (not bloated)",
            "Can't explain why it's valid? Re-validate"
        ],
        "yaml-validator": [
            "YAML syntax is valid",
            "Indentation is consistent (2 or 4 spaces, not tabs)",
            "All required fields present",
            "Data types are correct",
            "Special characters properly escaped",
            "Anchors and aliases valid",
            "No trailing whitespace",
            "File encoding is UTF-8",
            "Deploys without errors",
            "Can't explain why it's valid? Re-validate"
        ],
        "regex-tester": [
            "Pattern matches intended inputs",
            "Pattern rejects invalid inputs",
            "Edge cases tested",
            "Performance acceptable on large inputs",
            "Special characters properly escaped",
            "Anchors (^ $) correctly placed",
            "Capture groups work as intended",
            "Tested in target language/tool",
            "Can explain what pattern matches",
            "Can't explain pattern? Test more cases"
        ],
        "sql-generator": [
            "SQL syntax is valid",
            "All table/column names exist",
            "JOINs use correct columns",
            "WHERE conditions are correct",
            "GROUP BY includes all non-aggregated columns",
            "Indexes used effectively",
            "No N+1 queries",
            "Parameterized queries (prevent SQL injection)",
            "Proper aggregate functions",
            "Tested on real data (not small sample)"
        ],
        "env-validator": [
            "All required variables present",
            "Variable formats correct",
            "No hardcoded secrets",
            "No .env in version control",
            ".env.example has template (no values)",
            "Application starts without errors",
            "No sensitive data in logs",
            "Database connection works",
            "API credentials are valid",
            "Can't explain why variables valid? Re-check"
        ],
        "security-scanner": [
            "No SQL injection vulnerabilities",
            "No hardcoded secrets or credentials",
            "No unsafe eval/exec",
            "No weak cryptography",
            "Input validation present",
            "No XSS vulnerabilities",
            "No CSRF issues",
            "Authentication/authorization checked",
            "Sensitive data encrypted",
            "Can't explain security? Scan again"
        ]
    }
    return checklists.get(skill_name, [
        "Can explain the issue",
        "Have tested the fix",
        "No obvious regressions",
        "Code follows best practices",
        "Can't check all boxes? More work needed"
    ])

def get_common_errors(skill_name):
    """Generate common errors for skill"""
    errors = {
        "json-validator": {
            "Missing Comma": '{"name": "John",\n"age": 30\n}',
            "Trailing Comma": '{"name": "John",\n"age": 30,\n}',
            "Unquoted Keys": '{name: "John"}',
            "Single Quotes": "{'name': 'John'}"
        },
        "yaml-validator": {
            "Tab Indentation": 'key:\n\tvalue  # Uses tab',
            "Inconsistent Spacing": 'key1:\n  value\nkey2:\n   value  # Different spacing',
            "Missing Colon": 'key value  # Missing :',
            "Unclosed Quote": 'key: "value  # No closing quote'
        },
        "regex-tester": {
            "Unescaped Dot": '.* matches everything, including newlines',
            "Missing Anchors": 'email matches within longer strings',
            "Greedy Matching": '<.*> captures everything between < and last >',
            "Wrong Escape": '\\d vs d - forgot to escape'
        }
    }
    return errors.get(skill_name, {})

print("📝 SKILL.md 内容库已准备")
print(f"包含 {len(SKILLS_CONTENT)} 个 Skills 的完整内容")
