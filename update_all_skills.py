#!/usr/bin/env python3
"""
批量为所有 tools 下的 Skills 生成详细 SKILL.md
"""

from pathlib import Path

TOOLS_SKILLS = {
    "yaml-validator": """---
name: yaml-validator
description: "When validating YAML files, checking Kubernetes manifests, debugging Docker Compose, or validating configuration files. Validate YAML before deployment."
license: MIT
---

# YAML Validator Skill

## Overview
YAML is everywhere in DevOps - Kubernetes, Docker Compose, GitHub Actions. Invalid YAML breaks deployments silently with cryptic error messages.

**Core Principle**: Invalid YAML = failed deployment. Validate before deploying.

## When to Use

**Always:**
- Before deploying Kubernetes manifests
- Validating Docker Compose files
- Checking CI/CD workflow files
- Before committing configuration
- When deployment mysteriously fails

**Trigger phrases:**
- "Is this YAML valid?"
- "Validate Kubernetes config"
- "Check this Docker Compose"
- "Why won't this deploy?"
- "Fix this YAML error"

## Common YAML Errors

### Indentation Errors (Most Common)
- Tabs instead of spaces (YAML hates tabs)
- Inconsistent spacing (mixing 2 and 4 spaces)
- Missing indentation for nested values
- Extra spaces breaking structure

### Syntax Errors
- Missing colons after keys
- Unclosed quotes
- Duplicate keys (silently overwrites)
- Unquoted values with special characters

### Type Errors
- Port numbers as strings instead of numbers
- Booleans written as strings ("true" vs true)
- Arrays expected but strings provided

## Verification Checklist

- [ ] YAML syntax is valid
- [ ] Indentation is consistent (2 or 4 spaces, NOT tabs)
- [ ] All required fields present
- [ ] Data types are correct
- [ ] No duplicate keys
- [ ] Special characters escaped
- [ ] File encoding is UTF-8
- [ ] Deploys without errors

## How to Use

```bash
python3 validate_yaml.py < config.yaml
```

## Related Skills
- **json-validator** - Validate JSON files
- **dockerfile-analyzer** - Validate Docker files
- **security-scanner** - Check YAML for security issues
""",

    "regex-tester": """---
name: regex-tester
description: "When testing regular expressions, validating patterns, debugging regex issues, or optimizing regex performance. Test regex before using in production."
license: MIT
---

# Regex Tester Skill

## Overview
Regular expressions are powerful but fragile. One typo breaks the pattern completely. Test regex thoroughly before deploying.

**Core Principle**: If you didn't test with edge cases, the regex is wrong.

## When to Use

**Always:**
- Before using regex in validation
- Optimizing regex performance
- Debugging "doesn't match" issues
- Testing edge cases
- Before committing regex patterns

**Trigger phrases:**
- "Does this regex work?"
- "Test this pattern"
- "Why doesn't this match?"
- "Generate a regex for..."
- "Optimize this regex"

## Common Regex Mistakes

**Unescaped Special Characters**
- `.` matches any character (including newlines)
- `*` means zero or more (use `\\*` for literal asterisk)
- `+`, `?`, `[]`, `{}` all have special meaning

**Greedy vs Non-Greedy**
- `.*` matches everything up to the LAST match
- `.*?` matches everything up to the FIRST match
- Wrong choice breaks your pattern

**Missing Anchors**
- Without `^` and `$`, pattern matches anywhere in string
- Email validation: `email` matches within "myemail@example.com"
- Fix: `^[^@]+@[^@]+$`

**Wrong Escape Sequences**
- `\\d` in code = `\d` in regex (one backslash)
- `\\\\d` in code = `\\d` in regex (two backslashes)
- Language-specific: Python, JavaScript, Java all differ

## Verification Checklist

- [ ] Pattern matches intended inputs
- [ ] Pattern rejects invalid inputs
- [ ] Edge cases tested (empty, null, very long)
- [ ] Performance acceptable on large inputs
- [ ] Special characters properly escaped
- [ ] Anchors correctly placed
- [ ] Capture groups work as intended
- [ ] Tested in target language

## Related Skills
- **code-review** - Review regex patterns in code
- **security-scanner** - Check regex for ReDoS vulnerabilities
- **json-validator** - Validate regex patterns themselves
""",

    "sql-generator": """---
name: sql-generator
description: "When generating SQL queries, validating SQL, optimizing queries, or debugging SQL errors. Validate SQL before executing against databases."
license: MIT
---

# SQL Generator Skill

## Overview
SQL is powerful and permanent. Invalid SQL causes data loss or corruption. Test SQL thoroughly before executing against production databases.

**Core Principle**: SQL is permanent. Test first, execute once.

## When to Use

**Always:**
- Before executing against production
- Writing new queries
- Optimizing slow queries
- Creating migrations
- Checking for SQL injection vulnerabilities

**Trigger phrases:**
- "Generate this SQL"
- "Is this query correct?"
- "Why is this slow?"
- "Optimize this query"
- "Check for SQL injection"

## Common SQL Errors

**N+1 Queries**
- Fetching all posts, then for each post fetching comments in a loop
- Fix: Use JOIN to fetch in single query
- Performance difference: 100ms → 1 second (for 100 items)

**Missing WHERE Clause**
- `DELETE FROM users` → Deletes ALL users
- `UPDATE table SET x=1` → Updates ALL rows
- Always verify WHERE clause

**Type Mismatches**
- Comparing string to number: `WHERE id = '123'`
- Date formats: `WHERE date > '2024-01-01'` (string not date)
- Boolean confusion: `WHERE active = 1` (should be true/false)

**Injection Vulnerabilities**
- Using string concatenation: `"SELECT * FROM users WHERE id=" + userId`
- Fix: Use parameterized queries: `SELECT * FROM users WHERE id = ?`

## Verification Checklist

- [ ] SQL syntax is valid
- [ ] All table/column names exist
- [ ] JOINs use correct columns
- [ ] WHERE conditions are correct
- [ ] GROUP BY includes all non-aggregated columns
- [ ] No N+1 queries
- [ ] Parameterized queries used
- [ ] Tested on real data

## Related Skills
- **code-review** - Review SQL in code
- **security-scanner** - Check for SQL injection
- **log-analyzer** - Analyze slow queries in logs
""",

    "env-validator": """---
name: env-validator
description: "When validating environment variables, checking configuration, finding missing vars, or managing secrets. Validate environment before deployment."
license: MIT
---

# Environment Validator Skill

## Overview
Environment variables control application behavior. Missing or incorrect variables cause runtime failures. Validate before deployment.

**Core Principle**: Bad environment = broken application.

## When to Use

**Always:**
- Before deploying to any environment
- When application fails to start
- Checking for exposed secrets
- Validating database connections
- Verifying API credentials

**Trigger phrases:**
- "Check my environment"
- "Are secrets exposed?"
- "Missing environment variable"
- "Validate config"
- "Check database connection"

## Common Environment Errors

**Hardcoded Secrets in Code**
- API keys visible in repository
- Database passwords in config files
- AWS credentials in code

**Missing Required Variables**
- Database URL not set
- API key not provided
- Configuration incomplete
- Application won't start

**Wrong Format**
- `DATABASE_URL` should be full URI, not just host
- `PORT` should be number, not string
- Boolean should be "true"/"false" or "1"/"0"

**Exposed Secrets in .gitignore**
- .env file not in .gitignore
- Secrets committed to git history
- Hard to remove once committed

## Verification Checklist

- [ ] All required variables present
- [ ] Variable formats correct
- [ ] No hardcoded secrets in code
- [ ] .env not in version control
- [ ] .env.example has template (no values)
- [ ] Application starts without errors
- [ ] Database connection works
- [ ] API credentials are valid
- [ ] No sensitive data in logs

## Related Skills
- **security-scanner** - Check for hardcoded secrets
- **file-analyzer** - Verify .env file not committed
- **api-tester** - Test API connections with env vars
""",

    "dockerfile-analyzer": """---
name: dockerfile-analyzer
description: "When analyzing Dockerfile, checking best practices, improving Docker configuration, or validating security. Analyze Dockerfiles for optimization and security."
license: MIT
---

# Dockerfile Analyzer Skill

## Overview
Docker images can balloon to gigabytes with one mistake. Invalid Dockerfiles fail or create insecure containers. Analyze before building and deploying.

**Core Principle**: Lean images are fast. Secure images are trustworthy.

## When to Use

**Always:**
- Before building production images
- Optimizing image size
- Checking security practices
- Improving build performance
- Reviewing team Docker files

**Trigger phrases:**
- "Is this Dockerfile good?"
- "Make this image smaller"
- "Check Docker best practices"
- "Is this secure?"
- "Why is this so big?"

## Common Dockerfile Mistakes

**Large Base Images**
- Using `ubuntu:latest` (1.2GB) vs `alpine:latest` (7MB)
- Using `node:18` (900MB) vs `node:18-alpine` (150MB)
- Difference: 800MB+ in final image

**Unnecessary Layers**
- Each `RUN` command creates a layer
- `RUN apt-get update && apt-get install` should be ONE command
- Wrong: Multiple RUN commands can't share cache

**Running as Root**
- Container runs as root user by default
- Security risk: container breakout = full system access
- Fix: Add `USER appuser` directive

**Copying Entire Directory**
- `COPY . /app` includes everything (node_modules, .git, etc.)
- Fix: Use `.dockerignore` to exclude files
- Result: 500MB → 50MB

**Not Pinning Base Image**
- `FROM node` uses latest (unpredictable)
- Fix: `FROM node:18.14.0` (specific version)
- Different versions may behave differently

## Verification Checklist

- [ ] Base image pinned to specific version
- [ ] Running as non-root user
- [ ] `.dockerignore` excludes unnecessary files
- [ ] RUN commands consolidated
- [ ] Final image size reasonable
- [ ] No secrets in image
- [ ] Health check included
- [ ] Layers optimized for caching

## Related Skills
- **security-scanner** - Check image for vulnerabilities
- **code-review** - Review Dockerfile logic
- **yaml-validator** - Validate docker-compose.yml
""",

    "api-tester": """---
name: api-tester
description: "When testing APIs, making HTTP requests, debugging responses, or validating endpoints. Test HTTP APIs and validate responses before integration."
license: MIT
---

# API Tester Skill

## Overview
APIs are contracts between systems. Broken APIs break applications. Test endpoints thoroughly before integrating.

**Core Principle**: API contracts must be verified before deployment.

## When to Use

**Always:**
- Testing API endpoints
- Validating responses
- Checking status codes
- Verifying headers
- Testing authentication

**Trigger phrases:**
- "Test this endpoint"
- "Is this API working?"
- "Debug this response"
- "Check API response"
- "Validate the endpoint"

## Common API Issues

**Wrong Status Codes**
- 200 OK for errors (should be 400-500)
- 500 Server Error when should be 400 Bad Request
- Client can't tell success from failure

**Invalid Response Format**
- Expected JSON, got HTML error page
- Missing required fields in response
- Data type mismatch (string vs number)

**Authentication Failures**
- Missing Authorization header
- Wrong token format
- Expired or invalid credentials
- Permissions not granted

**Performance Issues**
- Response time > 1 second
- Timeout on large requests
- Memory leaks causing slowdowns

## Verification Checklist

- [ ] Endpoint returns correct status code
- [ ] Response is valid JSON/XML
- [ ] Required fields present in response
- [ ] Data types match specification
- [ ] Authentication works
- [ ] Response time acceptable
- [ ] Handles errors gracefully
- [ ] Works with real data

## Related Skills
- **json-validator** - Validate API response JSON
- **code-review** - Review API implementation
- **security-scanner** - Check API for security issues
""",

    "log-analyzer": """---
name: log-analyzer
description: "When analyzing logs, parsing errors, finding patterns, or debugging issues. Analyze application logs to identify problems and patterns."
license: MIT
---

# Log Analyzer Skill

## Overview
Logs are the black box flight recorder of your application. Read them correctly to understand what happened. Misread logs = wrong conclusions.

**Core Principle**: Logs don't lie. Logs tell exactly what happened.

## When to Use

**Always:**
- Debugging production issues
- Finding performance bottlenecks
- Identifying error patterns
- Post-incident analysis
- Understanding system behavior

**Trigger phrases:**
- "Analyze these logs"
- "Find the error"
- "What went wrong?"
- "Find performance issues"
- "Why is this slow?"

## What to Look For in Logs

**Error Patterns**
- Repeated errors (N+1, timeout, connection)
- Error rates spiking at specific times
- Cascading failures (error A causes error B)

**Performance Issues**
- Slow requests (duration > threshold)
- Memory usage spikes
- Increasing response times over time
- Database query timeouts

**System Events**
- Service startup/shutdown
- Configuration changes
- Resource exhaustion (disk, memory, connections)
- Rate limiting triggered

## Common Log Mistakes

**Ignoring context**
- Single error doesn't mean failure
- Look for patterns over time
- Understand error frequency

**Wrong error source**
- Application says "timeout"
- Root cause is slow database
- Fix in wrong place

**Missing correlation**
- Error at 14:00
- Look for what changed at 13:55
- Causes appear BEFORE effects

## Verification Checklist

- [ ] Understand the error message
- [ ] Found the source file/function
- [ ] Identified error pattern (single vs repeated)
- [ ] Checked related logs (before/after)
- [ ] Considered environment differences
- [ ] Verified reproduction conditions

## Related Skills
- **security-scanner** - Find security events in logs
- **code-review** - Review logging statements
- **api-tester** - Test APIs related to error
""",

    "file-analyzer": """---
name: file-analyzer
description: "When analyzing files, finding large files, detecting duplicates, or analyzing file structure. Analyze and manage files in projects."
license: MIT
---

# File Analyzer Skill

## Overview
Large files waste storage, slow down deployments, and hide problems. Track what files exist and why. Uncontrolled file growth indicates bugs.

**Core Principle**: Track what you have. Know why you have it.

## When to Use

**Always:**
- Before deployments
- Investigating disk usage
- Finding build artifacts
- Identifying duplicates
- Reducing repository size

**Trigger phrases:**
- "Find large files"
- "What's taking up space?"
- "Detect duplicates"
- "Analyze directory"
- "Why is this bloated?"

## Common File Issues

**Build Artifacts in Repository**
- `node_modules` (500MB+)
- `dist/` or `build/` folders
- `.next/` directory
- Package locks that change constantly

**Duplicate Files**
- Same file in multiple locations
- Different names, same content
- Dead code branches

**Unnecessary Files**
- Backup files (.bak, .backup)
- Temporary files (.tmp)
- Log files (.log)
- IDE settings (.vscode, .idea)

## Verification Checklist

- [ ] Understand what files you have
- [ ] Know why each large file exists
- [ ] No build artifacts in source control
- [ ] Duplicates identified and resolved
- [ ] .gitignore excludes temporary files
- [ ] Repository size is reasonable

## Related Skills
- **code-review** - Review file organization
- **security-scanner** - Check for exposed files
- **git-analysis** - Find large commits
""",

    "code-formatter": """---
name: code-formatter
description: "When formatting code, fixing indentation, or applying code style. Format and standardize code before committing."
license: MIT
---

# Code Formatter Skill

## Overview
Inconsistent formatting wastes review time and creates merge conflicts. Format code before committing. Unformatted code is unprofessional.

**Core Principle**: Consistent formatting reduces friction.

## When to Use

**Always:**
- Before committing code
- When joining a team
- Standardizing across codebase
- Preparing for review
- Reducing diff noise

**Trigger phrases:**
- "Format this code"
- "Fix indentation"
- "Standardize formatting"
- "Apply code style"

## What Formatters Fix

**Indentation**
- Inconsistent spaces/tabs
- Wrong indentation level
- Mixed indentation styles

**Spacing**
- Missing spaces around operators
- Extra spaces in declarations
- Inconsistent blank lines

**Line Length**
- Lines too long (>80-100 chars)
- Breaking long lines
- Consistent wrapping style

**Quotes and Semicolons**
- Single vs double quotes
- Semicolon requirements
- Bracket placement

## Verification Checklist

- [ ] Code formatted consistently
- [ ] All files follow same style
- [ ] No whitespace-only changes in diffs
- [ ] Line length acceptable
- [ ] Indentation correct
- [ ] Semicolons consistent

## Related Skills
- **code-review** - Review formatted code
- **security-scanner** - Check code after formatting
""",

    "security-scanner": """---
name: security-scanner
description: "When scanning code for security issues, detecting vulnerabilities, or analyzing security. Identify security problems and vulnerabilities in code."
license: MIT
---

# Security Scanner Skill

## Overview
Security vulnerabilities are silent. Code looks fine but contains exploits. Scan before deploying. Unscanned code is a liability.

**Core Principle**: Assume code has vulnerabilities until proven secure.

## When to Use

**Always:**
- Before production deployment
- When code handles user data
- Checking for common mistakes
- During code review
- After dependency updates

**Trigger phrases:**
- "Scan for security issues"
- "Is this secure?"
- "Check for vulnerabilities"
- "Find security bugs"

## Critical Vulnerabilities

**SQL Injection**
- String concatenation in queries
- User input in SQL
- Fix: Use parameterized queries

**Hardcoded Secrets**
- API keys in code
- Database passwords
- AWS credentials

**Unsafe Functions**
- `eval()`, `exec()` - arbitrary code
- No input validation
- Command injection

**Weak Cryptography**
- MD5, SHA1 for passwords
- Hardcoded encryption keys
- Weak random number generation

## Verification Checklist

- [ ] No SQL injection vulnerabilities
- [ ] No hardcoded secrets
- [ ] No unsafe eval/exec
- [ ] Input validation present
- [ ] Proper authentication
- [ ] Secure cryptography
- [ ] No XSS vulnerabilities
- [ ] Sensitive data encrypted

## Related Skills
- **code-review** - Review security implications
- **env-validator** - Check for exposed secrets
- **log-analyzer** - Find security events in logs
""",

    "markdown-validator": """---
name: markdown-validator
description: "When validating Markdown files, checking documentation, finding broken links, or improving docs. Validate Markdown before publishing."
license: MIT
---

# Markdown Validator Skill

## Overview
Documentation breaks silently. Broken links, invalid syntax, and missing files make docs unusable. Validate before publishing.

**Core Principle**: Documentation is code. Validate it.

## When to Use

**Always:**
- Before publishing documentation
- Checking for broken links
- Validating syntax
- Before commit
- Testing documentation rendering

**Trigger phrases:**
- "Check this README"
- "Find broken links"
- "Validate documentation"
- "Is this markdown correct?"

## Common Markdown Issues

**Broken Links**
- Links to non-existent files
- Incorrect relative paths
- Renamed files with old references

**Syntax Errors**
- Improper heading hierarchy (H4 after H2)
- Unmatched brackets/parentheses
- Invalid code block fences

**Missing Content**
- References to images that don't exist
- Incomplete sections
- TODO comments left in

## Verification Checklist

- [ ] Markdown syntax is valid
- [ ] All links work and reference correct files
- [ ] Headings properly hierarchical
- [ ] Code blocks properly formatted
- [ ] No broken images
- [ ] No TODO comments
- [ ] Renders correctly
- [ ] File encoding is UTF-8

## Related Skills
- **code-review** - Review documentation content
- **file-analyzer** - Find broken image files
""",

    "changelog-generator": """---
name: changelog-generator
description: "When generating changelog, creating release notes, or documenting changes. Generate changelog from version control history."
license: MIT
---

# Changelog Generator Skill

## Overview
Changes are history. Document them automatically from commits. Manual changelogs are incomplete and out of sync with code.

**Core Principle**: Generated history is accurate history.

## When to Use

**Always:**
- Before release
- Documenting changes
- Publishing release notes
- Tracking version history
- Creating user-facing documentation

**Trigger phrases:**
- "Generate changelog"
- "Create release notes"
- "What changed?"
- "Document these changes"

## Changelog Information

**Features (User-Visible)**
- New capabilities
- Improved functionality
- User-facing enhancements

**Bug Fixes**
- Resolved issues
- Fixed errors
- Corrected behavior

**Breaking Changes**
- API changes
- Behavior changes
- Deprecations

**Internal Changes**
- Refactoring
- Performance improvements
- Technical debt reduction

## Verification Checklist

- [ ] All changes documented
- [ ] Grouped by type (feat, fix, etc.)
- [ ] User-facing changes highlighted
- [ ] Breaking changes clearly marked
- [ ] Date/version recorded
- [ ] Links to commits/PRs included

## Related Skills
- **version-manager** - Determine version number
- **git-analysis** - Analyze commits
""",

    "version-manager": """---
name: version-manager
description: "When managing versions, validating version numbers, or handling semantic versioning. Validate and manage version numbers."
license: MIT
---

# Version Manager Skill

## Overview
Versions are agreements. Breaking versions without notice break users' applications. Follow semantic versioning.

**Core Principle**: Versions communicate contract changes to users.

## When to Use

**Always:**
- Before releasing
- Planning breaking changes
- Determining release type
- Updating dependencies
- Communicating changes

**Trigger phrases:**
- "Is this version correct?"
- "What's the next version?"
- "Check semver"
- "Validate version"

## Semantic Versioning (SemVer)

**MAJOR.MINOR.PATCH**
- MAJOR: Breaking changes (1.0.0 → 2.0.0)
- MINOR: New features, backward compatible (1.0.0 → 1.1.0)
- PATCH: Bug fixes only (1.0.0 → 1.0.1)

**Pre-release Versions**
- 1.0.0-alpha, 1.0.0-beta, 1.0.0-rc.1
- Ordered: alpha < beta < rc < release

## Verification Checklist

- [ ] Version follows SemVer format
- [ ] MAJOR incremented for breaking changes
- [ ] MINOR incremented for new features
- [ ] PATCH incremented for bug fixes
- [ ] Pre-release tags used for unreleased versions
- [ ] Previous versions documented
- [ ] Users notified of breaking changes

## Related Skills
- **changelog-generator** - Document changes with version
- **code-review** - Review version bumps
""",

    "git-analysis": """---
name: git-analysis
description: "When analyzing Git repository, checking commit history, understanding project evolution, or finding issues. Analyze Git history and commits."
license: MIT
---

# Git Analysis Skill

## Overview
Git history is a project timeline. Read it correctly to understand how code evolved. Misread history wastes debugging time.

**Core Principle**: Git tells you what changed and why.

## When to Use

**Always:**
- Understanding code evolution
- Finding when bugs were introduced
- Tracking feature development
- Understanding refactorings
- Analyzing code patterns

**Trigger phrases:**
- "Analyze this repository"
- "When was this added?"
- "Who wrote this?"
- "Analyze commits"
- "When did this break?"

## What to Look For

**Commit Patterns**
- Frequency (active vs stale)
- Message quality
- Size (large vs small)
- Author distribution

**Code Evolution**
- Feature growth
- Refactoring patterns
- Bug introduction and fixes
- Architecture changes

**Issues**
- Large commits (>500 lines)
- Poor commit messages
- Stale branches
- Inconsistent style

## Verification Checklist

- [ ] Understand commit history
- [ ] Find relevant commits for feature/bug
- [ ] Check who made each change
- [ ] Understand why change was made
- [ ] Identify breaking changes
- [ ] Track feature development

## Related Skills
- **changelog-generator** - Generate changelog from commits
- **code-review** - Review commit patterns
""",

    "dependency-analyzer": """---
name: dependency-analyzer
description: "When analyzing dependencies, checking for vulnerabilities, finding unused packages, or managing versions. Analyze and optimize dependencies."
license: MIT
---

# Dependency Analyzer Skill

## Overview
Dependencies are risks. Vulnerabilities, outdated versions, and unused packages accumulate. Analyze before deploying.

**Core Principle**: Know what you depend on.

## When to Use

**Always:**
- Before production deployment
- Checking security updates
- Finding unused packages
- Detecting conflicts
- Managing technical debt

**Trigger phrases:**
- "Check for vulnerabilities"
- "Find unused dependencies"
- "Update dependencies"
- "Detect conflicts"
- "Check for outdated packages"

## Common Issues

**Known Vulnerabilities**
- CVE in dependencies
- Exploit code publicly available
- Attackers targeting known issues

**Outdated Versions**
- Security patches missing
- Performance improvements not applied
- Bug fixes not available

**Unused Dependencies**
- Dead weight in bundle
- Maintenance burden
- Security liabilities

**Conflicting Versions**
- Different packages need different versions
- Can cause unexpected behavior
- Hard to debug

## Verification Checklist

- [ ] No known vulnerabilities
- [ ] Dependencies up to date
- [ ] No unused packages
- [ ] No version conflicts
- [ ] Size impact understood
- [ ] Maintenance burden acceptable

## Related Skills
- **security-scanner** - Find vulnerabilities
- **code-review** - Review dependency usage
""",

    "architecture-analyzer": """---
name: architecture-analyzer
description: "When analyzing project architecture, understanding system design, checking for issues, or planning refactoring. Analyze system architecture and design."
license: MIT
---

# Architecture Analyzer Skill

## Overview
Architecture determines if a system is maintainable. Bad architecture hides problems until they cascade. Analyze before complexity spirals.

**Core Principle**: Fix architecture early. Fixes cascade down.

## When to Use

**Always:**
- Reviewing new designs
- Refactoring legacy code
- Planning major changes
- Finding coupling problems
- Improving maintainability

**Trigger phrases:**
- "Is the design good?"
- "Find architecture issues"
- "How should this be organized?"
- "Identify coupling"
- "Improve maintainability"

## Architecture Issues

**Tight Coupling**
- Components depend on each other
- Can't test independently
- Changes ripple everywhere

**God Objects**
- Classes doing too much
- High responsibility
- Hard to understand and modify

**Circular Dependencies**
- Module A depends on B, B depends on A
- Can't separate concerns
- Hard to test

**Missing Abstraction**
- Implementation details exposed
- Can't swap implementations
- Fragile to changes

## Verification Checklist

- [ ] Understand component responsibilities
- [ ] Identify dependencies
- [ ] Find tight coupling
- [ ] Check for circular dependencies
- [ ] Evaluate design patterns used
- [ ] Consider testability
- [ ] Plan refactoring strategy

## Related Skills
- **code-review** - Review architectural decisions
- **dependency-analyzer** - Find unwanted dependencies
"""
}

def create_skill_files():
    """Create all SKILL.md files"""
    base_path = Path("/Users/jarry/github/ai-skills/tools")

    for skill_name, content in TOOLS_SKILLS.items():
        skill_path = base_path / skill_name
        if skill_path.exists():
            skill_file = skill_path / "SKILL.md"
            skill_file.write_text(content, encoding='utf-8')
            print(f"✅ Updated: {skill_name}/SKILL.md")
        else:
            print(f"⚠️  Skipped: {skill_name} (directory not found)")

    print(f"\n✅ Updated {len(TOOLS_SKILLS)} SKILL.md files!")

if __name__ == '__main__':
    create_skill_files()
