# 安全扫描器参考文档

## 安全扫描器概述

### 什么是安全扫描器
安全扫描器是一个综合性的安全检测工具，用于发现和评估应用程序、系统、网络和基础设施中的安全漏洞。该工具支持静态代码分析、动态应用测试、依赖安全扫描、配置安全检查等多种扫描方式，提供全面的安全评估、漏洞管理和合规检查功能，帮助开发团队构建安全可靠的软件系统。

### 主要功能
- **多维度扫描**: 支持代码、依赖、配置、网络、运行时等多维度安全扫描
- **漏洞检测**: 基于多种检测引擎和规则库发现已知和未知漏洞
- **风险评估**: 提供漏洞严重性评估和风险等级划分
- **合规检查**: 支持多种安全标准和合规框架检查
- **报告生成**: 生成详细的安全报告和修复建议
- **集成能力**: 与CI/CD流程和第三方安全工具无缝集成

## 静态代码分析引擎

### 代码安全扫描器
```python
# static_code_scanner.py
import os
import re
import ast
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    COMMAND_INJECTION = "command_injection"
    FILE_INCLUSION = "file_inclusion"
    CODE_INJECTION = "code_injection"
    HARDCODED_CREDENTIALS = "hardcoded_credentials"
    WEAK_CRYPTOGRAPHY = "weak_cryptography"
    INSECURE_RANDOM = "insecure_random"
    BUFFER_OVERFLOW = "buffer_overflow"
    RACE_CONDITION = "race_condition"
    RESOURCE_LEAK = "resource_leak"

class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    id: str
    type: VulnerabilityType
    severity: SeverityLevel
    title: str
    description: str
    file_path: str
    line_number: int
    column_number: int
    code_snippet: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    remediation: Optional[str] = None
    references: List[str] = None

@dataclass
class ScanResult:
    total_files: int
    scanned_files: int
    vulnerabilities: List[Vulnerability]
    scan_time: float
    summary: Dict[str, int]

class StaticCodeScanner:
    def __init__(self):
        self.rules = self._load_security_rules()
        self.logger = logging.getLogger(__name__)
        self.file_extensions = {
            '.py', '.js', '.ts', '.java', '.cs', '.go', '.rs', '.php', '.rb'
        }
    
    def _load_security_rules(self) -> Dict[VulnerabilityType, List[Dict[str, Any]]]:
        """加载安全规则"""
        return {
            VulnerabilityType.SQL_INJECTION: [
                {
                    'pattern': r'\b(execute|query|raw)\s*\(\s*["\'].*?\+.*?["\']',
                    'description': '可能的SQL注入漏洞',
                    'severity': SeverityLevel.HIGH,
                    'cwe_id': 'CWE-89',
                    'owasp_category': 'A03:2021 – Injection'
                },
                {
                    'pattern': r'\b(exec|execute|sp_executesql)\s*\(\s*["\'].*?\+',
                    'description': '动态SQL执行',
                    'severity': SeverityLevel.CRITICAL,
                    'cwe_id': 'CWE-89',
                    'owasp_category': 'A03:2021 – Injection'
                }
            ],
            VulnerabilityType.XSS: [
                {
                    'pattern': r'\b(document\.write|innerHTML|outerHTML)\s*\(\s*.*?\+',
                    'description': '可能的XSS漏洞',
                    'severity': SeverityLevel.HIGH,
                    'cwe_id': 'CWE-79',
                    'owasp_category': 'A03:2021 – Injection'
                },
                {
                    'pattern': r'\b(eval|Function|setTimeout|setInterval)\s*\(\s*.*?\+',
                    'description': '动态代码执行',
                    'severity': SeverityLevel.CRITICAL,
                    'cwe_id': 'CWE-94',
                    'owasp_category': 'A03:2021 – Injection'
                }
            ],
            VulnerabilityType.HARDCODED_CREDENTIALS: [
                {
                    'pattern': r'\b(password|passwd|pwd|secret|key|token|api_key)\s*=\s*["\'][^"\']{3,}["\']',
                    'description': '硬编码凭证',
                    'severity': SeverityLevel.HIGH,
                    'cwe_id': 'CWE-798',
                    'owasp_category': 'A07:2021 – Identification and Authentication Failures'
                },
                {
                    'pattern': r'\b(username|user|login)\s*=\s*["\'][^"\']{3,}["\']',
                    'description': '硬编码用户名',
                    'severity': SeverityLevel.MEDIUM,
                    'cwe_id': 'CWE-798',
                    'owasp_category': 'A07:2021 – Identification and Authentication Failures'
                }
            ],
            VulnerabilityType.WEAK_CRYPTOGRAPHY: [
                {
                    'pattern': r'\b(md5|sha1|crc32)\s*\(',
                    'description': '弱加密算法',
                    'severity': SeverityLevel.MEDIUM,
                    'cwe_id': 'CWE-327',
                    'owasp_category': 'A02:2021 – Cryptographic Failures'
                },
                {
                    'pattern': r'\b(des|rc4|rc5)\s*\(',
                    'description': '不安全的加密算法',
                    'severity': SeverityLevel.HIGH,
                    'cwe_id': 'CWE-327',
                    'owasp_category': 'A02:2021 – Cryptographic Failures'
                }
            ],
            VulnerabilityType.FILE_INCLUSION: [
                {
                    'pattern': r'\b(include|require|include_once|require_once)\s*\(\s*.*?\$',
                    'description': '文件包含漏洞',
                    'severity': SeverityLevel.HIGH,
                    'cwe_id': 'CWE-98',
                    'owasp_category': 'A01:2021 – Broken Access Control'
                }
            ]
        }
    
    def scan_directory(self, directory_path: str, 
                      file_patterns: List[str] = None,
                      exclude_patterns: List[str] = None) -> ScanResult:
        """扫描目录"""
        start_time = time.time()
        
        directory = Path(directory_path)
        all_files = list(directory.rglob('*'))
        
        # 过滤文件
        source_files = self._filter_files(all_files, file_patterns, exclude_patterns)
        
        vulnerabilities = []
        
        for file_path in source_files:
            try:
                file_vulnerabilities = self.scan_file(file_path)
                vulnerabilities.extend(file_vulnerabilities)
            except Exception as e:
                self.logger.error(f"扫描文件失败 {file_path}: {e}")
        
        scan_time = time.time() - start_time
        
        # 生成摘要
        summary = self._generate_summary(vulnerabilities)
        
        return ScanResult(
            total_files=len(all_files),
            scanned_files=len(source_files),
            vulnerabilities=vulnerabilities,
            scan_time=scan_time,
            summary=summary
        )
    
    def scan_file(self, file_path: str) -> List[Vulnerability]:
        """扫描单个文件"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            file_extension = Path(file_path).suffix.lower()
            
            # 根据文件类型选择扫描器
            if file_extension == '.py':
                vulnerabilities.extend(self._scan_python_file(file_path, lines))
            elif file_extension in ['.js', '.ts']:
                vulnerabilities.extend(self._scan_javascript_file(file_path, lines))
            elif file_extension == '.java':
                vulnerabilities.extend(self._scan_java_file(file_path, lines))
            elif file_extension == '.cs':
                vulnerabilities.extend(self._scan_csharp_file(file_path, lines))
            else:
                vulnerabilities.extend(self._scan_generic_file(file_path, lines))
        
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
        
        return vulnerabilities
    
    def _filter_files(self, files: List[Path], 
                     include_patterns: List[str] = None,
                     exclude_patterns: List[str] = None) -> List[Path]:
        """过滤文件"""
        filtered_files = []
        
        for file_path in files:
            if not file_path.is_file():
                continue
            
            # 检查文件扩展名
            if file_path.suffix.lower() not in self.file_extensions:
                continue
            
            # 检查包含模式
            if include_patterns:
                if not any(file_path.match(pattern) for pattern in include_patterns):
                    continue
            
            # 检查排除模式
            if exclude_patterns:
                if any(file_path.match(pattern) for pattern in exclude_patterns):
                    continue
            
            filtered_files.append(file_path)
        
        return filtered_files
    
    def _scan_python_file(self, file_path: str, lines: List[str]) -> List[Vulnerability]:
        """扫描Python文件"""
        vulnerabilities = []
        
        try:
            # 解析AST
            tree = ast.parse('\n'.join(lines))
            
            # AST分析
            vulnerabilities.extend(self._analyze_python_ast(file_path, tree, lines))
            
        except SyntaxError:
            # 如果解析失败，使用正则表达式扫描
            vulnerabilities.extend(self._scan_generic_file(file_path, lines))
        
        return vulnerabilities
    
    def _analyze_python_ast(self, file_path: str, tree: ast.AST, lines: List[str]) -> List[Vulnerability]:
        """分析Python AST"""
        vulnerabilities = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # 检查危险的函数调用
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    
                    # SQL注入检查
                    if func_name in ['execute', 'executemany', 'query']:
                        if self._check_sql_injection(node):
                            vulnerabilities.append(Vulnerability(
                                id=f"SQL_INJECTION_{node.lineno}",
                                type=VulnerabilityType.SQL_INJECTION,
                                severity=SeverityLevel.HIGH,
                                title="可能的SQL注入漏洞",
                                description="检测到可能的SQL注入漏洞",
                                file_path=file_path,
                                line_number=node.lineno,
                                column_number=node.col_offset,
                                code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                                cwe_id="CWE-89",
                                owasp_category="A03:2021 – Injection"
                            ))
                    
                    # 危险函数调用
                    elif func_name in ['eval', 'exec', 'compile']:
                        vulnerabilities.append(Vulnerability(
                            id=f"CODE_INJECTION_{node.lineno}",
                            type=VulnerabilityType.CODE_INJECTION,
                            severity=SeverityLevel.CRITICAL,
                            title="危险的代码执行",
                            description=f"检测到危险的函数调用: {func_name}",
                            file_path=file_path,
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            cwe_id="CWE-94",
                            owasp_category="A03:2021 – Injection"
                        ))
                
                self.generic_visit(node)
            
            def _check_sql_injection(self, node):
                """检查SQL注入"""
                # 简化的检查逻辑
                if node.args:
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                            if isinstance(arg.left, ast.Str) or isinstance(arg.right, ast.Str):
                                return True
                return False
        
        visitor = SecurityVisitor()
        visitor.visit(tree)
        
        return vulnerabilities
    
    def _scan_javascript_file(self, file_path: str, lines: List[str]) -> List[Vulnerability]:
        """扫描JavaScript文件"""
        vulnerabilities = []
        
        for line_num, line in enumerate(lines, 1):
            # XSS检查
            xss_patterns = [
                r'document\.write\s*\(',
                r'innerHTML\s*=',
                r'eval\s*\(',
                r'Function\s*\(',
                r'setTimeout\s*\(',
                r'setInterval\s*\('
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append(Vulnerability(
                        id=f"XSS_{line_num}",
                        type=VulnerabilityType.XSS,
                        severity=SeverityLevel.HIGH,
                        title="可能的XSS漏洞",
                        description="检测到可能的跨站脚本攻击漏洞",
                        file_path=file_path,
                        line_number=line_num,
                        column_number=0,
                        code_snippet=line.strip(),
                        cwe_id="CWE-79",
                        owasp_category="A03:2021 – Injection"
                    ))
                    break
        
        return vulnerabilities
    
    def _scan_java_file(self, file_path: str, lines: List[str]) -> List[Vulnerability]:
        """扫描Java文件"""
        vulnerabilities = []
        
        for line_num, line in enumerate(lines, 1):
            # SQL注入检查
            if re.search(r'executeQuery\s*\(\s*.*?\+', line, re.IGNORECASE):
                vulnerabilities.append(Vulnerability(
                    id=f"SQL_INJECTION_{line_num}",
                    type=VulnerabilityType.SQL_INJECTION,
                    severity=SeverityLevel.HIGH,
                    title="可能的SQL注入漏洞",
                    description="检测到可能的SQL注入漏洞",
                    file_path=file_path,
                    line_number=line_num,
                    column_number=0,
                    code_snippet=line.strip(),
                    cwe_id="CWE-89",
                    owasp_category="A03:2021 – Injection"
                ))
            
            # 硬编码凭证检查
            if re.search(r'(password|passwd|pwd)\s*=\s*"[^"]{3,}"', line, re.IGNORECASE):
                vulnerabilities.append(Vulnerability(
                    id=f"HARDCODED_CREDENTIALS_{line_num}",
                    type=VulnerabilityType.HARDCODED_CREDENTIALS,
                    severity=SeverityLevel.HIGH,
                    title="硬编码凭证",
                    description="检测到硬编码的密码或凭证",
                    file_path=file_path,
                    line_number=line_num,
                    column_number=0,
                    code_snippet=line.strip(),
                    cwe_id="CWE-798",
                    owasp_category="A07:2021 – Identification and Authentication Failures"
                ))
        
        return vulnerabilities
    
    def _scan_csharp_file(self, file_path: str, lines: List[str]) -> List[Vulnerability]:
        """扫描C#文件"""
        vulnerabilities = []
        
        for line_num, line in enumerate(lines, 1):
            # SQL注入检查
            if re.search(r'ExecuteReader\s*\(\s*.*?\+', line, re.IGNORECASE):
                vulnerabilities.append(Vulnerability(
                    id=f"SQL_INJECTION_{line_num}",
                    type=VulnerabilityType.SQL_INJECTION,
                    severity=SeverityLevel.HIGH,
                    title="可能的SQL注入漏洞",
                    description="检测到可能的SQL注入漏洞",
                    file_path=file_path,
                    line_number=line_num,
                    column_number=0,
                    code_snippet=line.strip(),
                    cwe_id="CWE-89",
                    owasp_category="A03:2021 – Injection"
                ))
        
        return vulnerabilities
    
    def _scan_generic_file(self, file_path: str, lines: List[str]) -> List[Vulnerability]:
        """扫描通用文件"""
        vulnerabilities = []
        
        for line_num, line in enumerate(lines, 1):
            # 应用所有规则
            for vuln_type, rules in self.rules.items():
                for rule in rules:
                    if re.search(rule['pattern'], line, re.IGNORECASE):
                        vulnerabilities.append(Vulnerability(
                            id=f"{vuln_type.value.upper()}_{line_num}",
                            type=vuln_type,
                            severity=rule['severity'],
                            title=rule['description'],
                            description=rule['description'],
                            file_path=file_path,
                            line_number=line_num,
                            column_number=0,
                            code_snippet=line.strip(),
                            cwe_id=rule.get('cwe_id'),
                            owasp_category=rule.get('owasp_category')
                        ))
                        break
        
        return vulnerabilities
    
    def _generate_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, int]:
        """生成扫描摘要"""
        summary = {
            'total': len(vulnerabilities),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for vuln in vulnerabilities:
            severity = vuln.severity.value
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    def generate_report(self, scan_result: ScanResult, output_format: str = "json") -> str:
        """生成扫描报告"""
        if output_format.lower() == "json":
            return self._generate_json_report(scan_result)
        elif output_format.lower() == "html":
            return self._generate_html_report(scan_result)
        else:
            raise ValueError(f"不支持的报告格式: {output_format}")
    
    def _generate_json_report(self, scan_result: ScanResult) -> str:
        """生成JSON报告"""
        report_data = {
            'scan_info': {
                'total_files': scan_result.total_files,
                'scanned_files': scan_result.scanned_files,
                'scan_time': scan_result.scan_time,
                'timestamp': datetime.now().isoformat()
            },
            'summary': scan_result.summary,
            'vulnerabilities': [
                {
                    'id': vuln.id,
                    'type': vuln.type.value,
                    'severity': vuln.severity.value,
                    'title': vuln.title,
                    'description': vuln.description,
                    'file_path': vuln.file_path,
                    'line_number': vuln.line_number,
                    'column_number': vuln.column_number,
                    'code_snippet': vuln.code_snippet,
                    'cwe_id': vuln.cwe_id,
                    'owasp_category': vuln.owasp_category,
                    'remediation': vuln.remediation,
                    'references': vuln.references or []
                }
                for vuln in scan_result.vulnerabilities
            ]
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self, scan_result: ScanResult) -> str:
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>安全扫描报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .vulnerability { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .critical { border-left: 5px solid #d32f2f; }
        .high { border-left: 5px solid #f57c00; }
        .medium { border-left: 5px solid #fbc02d; }
        .low { border-left: 5px solid #388e3c; }
        .info { border-left: 5px solid #1976d2; }
        .code { background-color: #f5f5f5; padding: 10px; font-family: monospace; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>安全扫描报告</h1>
        <p>扫描时间: {timestamp}</p>
        <p>扫描文件数: {scanned_files}/{total_files}</p>
        <p>扫描耗时: {scan_time:.2f}秒</p>
    </div>
    
    <div class="summary">
        <h2>扫描摘要</h2>
        <p>总漏洞数: {total_vulns}</p>
        <p>严重: {critical}</p>
        <p>高危: {high}</p>
        <p>中危: {medium}</p>
        <p>低危: {low}</p>
        <p>信息: {info}</p>
    </div>
    
    <div class="vulnerabilities">
        <h2>漏洞详情</h2>
        {vulnerability_list}
    </div>
</body>
</html>
        """
        
        vulnerability_html = ""
        for vuln in scan_result.vulnerabilities:
            vulnerability_html += f"""
        <div class="vulnerability {vuln.severity.value}">
            <h3>{vuln.title}</h3>
            <p><strong>类型:</strong> {vuln.type.value}</p>
            <p><strong>严重性:</strong> {vuln.severity.value}</p>
            <p><strong>文件:</strong> {vuln.file_path}:{vuln.line_number}</p>
            <p><strong>描述:</strong> {vuln.description}</p>
            <div class="code">{vuln.code_snippet}</div>
            {f'<p><strong>CWE ID:</strong> {vuln.cwe_id}</p>' if vuln.cwe_id else ''}
            {f'<p><strong>OWASP类别:</strong> {vuln.owasp_category}</p>' if vuln.owasp_category else ''}
        </div>
            """
        
        return html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            scanned_files=scan_result.scanned_files,
            total_files=scan_result.total_files,
            scan_time=scan_result.scan_time,
            total_vulns=scan_result.summary['total'],
            critical=scan_result.summary['critical'],
            high=scan_result.summary['high'],
            medium=scan_result.summary['medium'],
            low=scan_result.summary['low'],
            info=scan_result.summary['info'],
            vulnerability_list=vulnerability_html
        )

# 使用示例
scanner = StaticCodeScanner()

# 扫描目录
scan_result = scanner.scan_directory(
    directory_path="./src",
    file_patterns=["*.py", "*.js", "*.java"],
    exclude_patterns=["test_*", "*_test.py"]
)

print(f"扫描完成:")
print(f"总文件数: {scan_result.total_files}")
print(f"扫描文件数: {scan_result.scanned_files}")
print(f"发现漏洞数: {len(scan_result.vulnerabilities)}")
print(f"扫描耗时: {scan_result.scan_time:.2f}秒")

# 生成报告
json_report = scanner.generate_report(scan_result, "json")
html_report = scanner.generate_report(scan_result, "html")

# 保存报告
with open("security_scan_report.json", "w", encoding="utf-8") as f:
    f.write(json_report)

with open("security_scan_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)
```

## 依赖安全扫描引擎

### 依赖漏洞扫描器
```python
# dependency_scanner.py
import json
import requests
import xml.etree.ElementTree as ET
import toml
import yaml
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging
import time

class PackageManager(Enum):
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    PIP = "pip"
    POETRY = "poetry"
    MAVEN = "maven"
    GRADLE = "gradle"
    NUGET = "nuget"
    CARGO = "cargo"
    COMPOSER = "composer"
    BUNDLER = "bundler"

class VulnerabilitySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class LicenseType(Enum):
    PERMISSIVE = "permissive"
    COPYLEFT = "copyleft"
    PROPRIETARY = "proprietary"
    PUBLIC_DOMAIN = "public_domain"
    UNKNOWN = "unknown"

@dataclass
class Dependency:
    name: str
    version: str
    package_manager: PackageManager
    license: Optional[str] = None
    description: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    author: Optional[str] = None

@dataclass
class Vulnerability:
    id: str
    title: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: Optional[float]
    cve_id: Optional[str]
    published_date: Optional[str]
    modified_date: Optional[str]
    references: List[str]
    affected_versions: List[str]
    patched_versions: List[str]

@dataclass
class DependencyVulnerability:
    dependency: Dependency
    vulnerability: Vulnerability
    fix_available: bool
    recommended_version: Optional[str]

@dataclass
class DependencyScanResult:
    total_dependencies: int
    vulnerable_dependencies: int
    vulnerabilities: List[DependencyVulnerability]
    license_issues: List[Dict[str, Any]]
    outdated_packages: List[Dict[str, Any]]
    scan_time: float
    summary: Dict[str, int]

class DependencyScanner:
    def __init__(self):
        self.vulnerability_databases = [
            OSVDatabase(),
            NVDDatabase(),
            GitHubAdvisoryDatabase(),
            SnykDatabase()
        ]
        self.license_database = LicenseDatabase()
        self.logger = logging.getLogger(__name__)
    
    def scan_project(self, project_path: str) -> DependencyScanResult:
        """扫描项目依赖"""
        start_time = time.time()
        
        dependencies = self._collect_dependencies(project_path)
        
        vulnerabilities = []
        license_issues = []
        outdated_packages = []
        
        for dependency in dependencies:
            # 扫描漏洞
            dep_vulnerabilities = self._scan_dependency_vulnerabilities(dependency)
            vulnerabilities.extend(dep_vulnerabilities)
            
            # 检查许可证
            license_issue = self._check_dependency_license(dependency)
            if license_issue:
                license_issues.append(license_issue)
            
            # 检查过时包
            outdated_info = self._check_outdated_package(dependency)
            if outdated_info:
                outdated_packages.append(outdated_info)
        
        scan_time = time.time() - start_time
        
        # 生成摘要
        summary = self._generate_summary(vulnerabilities)
        
        return DependencyScanResult(
            total_dependencies=len(dependencies),
            vulnerable_dependencies=len(set(v.dependency.name for v in vulnerabilities)),
            vulnerabilities=vulnerabilities,
            license_issues=license_issues,
            outdated_packages=outdated_packages,
            scan_time=scan_time,
            summary=summary
        )
    
    def _collect_dependencies(self, project_path: str) -> List[Dependency]:
        """收集项目依赖"""
        dependencies = []
        project_dir = Path(project_path)
        
        # 扫描不同包管理器的依赖文件
        dependency_files = {
            PackageManager.NPM: ["package.json"],
            PackageManager.YARN: ["package.json", "yarn.lock"],
            PackageManager.PNPM: ["package.json", "pnpm-lock.yaml"],
            PackageManager.PIP: ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
           .PackageManager.POETRY: ["pyproject.toml", "poetry.lock"],
            PackageManager.MAVEN: ["pom.xml"],
            PackageManager.GRADLE: ["build.gradle", "build.gradle.kts"],
            PackageManager.NUGET: ["packages.config", "*.csproj", "packages.lock.json"],
            PackageManager.CARGO: ["Cargo.toml", "Cargo.lock"],
            PackageManager.COMPOSER: ["composer.json", "composer.lock"],
            PackageManager.BUNDLER: ["Gemfile", "Gemfile.lock"]
        }
        
        for package_manager, files in dependency_files.items():
            for file_pattern in files:
                file_paths = list(project_dir.glob(file_pattern))
                for file_path in file_paths:
                    try:
                        file_dependencies = self._parse_dependency_file(
                            file_path, package_manager
                        )
                        dependencies.extend(file_dependencies)
                    except Exception as e:
                        self.logger.error(f"解析依赖文件失败 {file_path}: {e}")
        
        return dependencies
    
    def _parse_dependency_file(self, file_path: Path, 
                              package_manager: PackageManager) -> List[Dependency]:
        """解析依赖文件"""
        dependencies = []
        
        if package_manager == PackageManager.NPM:
            dependencies = self._parse_package_json(file_path)
        elif package_manager == PackageManager.PIP:
            dependencies = self._parse_requirements_txt(file_path)
        elif package_manager == PackageManager.MAVEN:
            dependencies = self._parse_pom_xml(file_path)
        elif package_manager == PackageManager.GRADLE:
            dependencies = self._parse_build_gradle(file_path)
        elif package_manager == PackageManager.CARGO:
            dependencies = self._parse_cargo_toml(file_path)
        # 其他包管理器的解析...
        
        # 设置包管理器
        for dep in dependencies:
            dep.package_manager = package_manager
        
        return dependencies
    
    def _parse_package_json(self, file_path: Path) -> List[Dependency]:
        """解析package.json"""
        dependencies = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析生产依赖
        deps = data.get('dependencies', {})
        for name, version in deps.items():
            dependencies.append(Dependency(
                name=name,
                version=version,
                package_manager=PackageManager.NPM
            ))
        
        # 解析开发依赖
        dev_deps = data.get('devDependencies', {})
        for name, version in dev_deps.items():
            dependencies.append(Dependency(
                name=name,
                version=version,
                package_manager=PackageManager.NPM
            ))
        
        return dependencies
    
    def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """解析requirements.txt"""
        dependencies = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 解析包名和版本
                    if '==' in line:
                        name, version = line.split('==', 1)
                    elif '>=' in line:
                        name, version = line.split('>=', 1)
                        version = '>=' + version
                    elif '<=' in line:
                        name, version = line.split('<=', 1)
                        version = '<=' + version
                    else:
                        name = line
                        version = '*'
                    
                    dependencies.append(Dependency(
                        name=name.strip(),
                        version=version.strip(),
                        package_manager=PackageManager.PIP
                    ))
        
        return dependencies
    
    def _parse_pom_xml(self, file_path: Path) -> List[Dependency]:
        """解析pom.xml"""
        dependencies = []
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 处理命名空间
        namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
        
        deps_elements = root.findall('.//maven:dependency', namespace)
        
        for dep_element in deps_elements:
            group_id = dep_element.find('maven:groupId', namespace)
            artifact_id = dep_element.find('maven:artifactId', namespace)
            version = dep_element.find('maven:version', namespace)
            
            if group_id is not None and artifact_id is not None:
                name = f"{group_id.text}:{artifact_id.text}"
                version_text = version.text if version is not None else '*'
                
                dependencies.append(Dependency(
                    name=name,
                    version=version_text,
                    package_manager=PackageManager.MAVEN
                ))
        
        return dependencies
    
    def _parse_build_gradle(self, file_path: Path) -> List[Dependency]:
        """解析build.gradle"""
        dependencies = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简化的Gradle依赖解析
        import re
        
        # 匹配依赖声明
        dependency_pattern = r'(?:implementation|compile|api|runtime|testImplementation)\s+([\'"])(.+?)\1'
        matches = re.findall(dependency_pattern, content)
        
        for match in matches:
            dep_string = match[1]
            
            # 解析 group:artifact:version 格式
            parts = dep_string.split(':')
            if len(parts) >= 2:
                if len(parts) == 2:
                    name = f"{parts[0]}:{parts[1]}"
                    version = '*'
                else:
                    name = f"{parts[0]}:{parts[1]}"
                    version = parts[2]
                
                dependencies.append(Dependency(
                    name=name,
                    version=version,
                    package_manager=PackageManager.GRADLE
                ))
        
        return dependencies
    
    def _parse_cargo_toml(self, file_path: Path) -> List[Dependency]:
        """解析Cargo.toml"""
        dependencies = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        # 解析依赖
        deps = data.get('dependencies', {})
        for name, version_info in deps.items():
            if isinstance(version_info, str):
                version = version_info
            elif isinstance(version_info, dict):
                version = version_info.get('version', '*')
            else:
                version = '*'
            
            dependencies.append(Dependency(
                name=name,
                version=version,
                package_manager=PackageManager.CARGO
            ))
        
        return dependencies
    
    def _scan_dependency_vulnerabilities(self, dependency: Dependency) -> List[DependencyVulnerability]:
        """扫描依赖漏洞"""
        vulnerabilities = []
        
        for database in self.vulnerability_databases:
            try:
                db_vulnerabilities = database.query_vulnerabilities(
                    dependency.name, dependency.version
                )
                
                for vuln in db_vulnerabilities:
                    fix_available = len(vuln.patched_versions) > 0
                    recommended_version = vuln.patched_versions[0] if vuln.patched_versions else None
                    
                    dep_vuln = DependencyVulnerability(
                        dependency=dependency,
                        vulnerability=vuln,
                        fix_available=fix_available,
                        recommended_version=recommended_version
                    )
                    vulnerabilities.append(dep_vuln)
            
            except Exception as e:
                self.logger.error(f"数据库查询失败 {database.__class__.__name__}: {e}")
        
        return vulnerabilities
    
    def _check_dependency_license(self, dependency: Dependency) -> Optional[Dict[str, Any]]:
        """检查依赖许可证"""
        try:
            license_info = self.license_database.get_license_info(dependency.name)
            
            if license_info:
                # 检查许可证合规性
                compliance_result = self.license_database.check_compliance(license_info['license'])
                
                if not compliance_result['compliant']:
                    return {
                        'dependency': dependency.name,
                        'license': license_info['license'],
                        'issues': compliance_result['issues'],
                        'recommendations': compliance_result['recommendations']
                    }
        
        except Exception as e:
            self.logger.error(f"许可证检查失败 {dependency.name}: {e}")
        
        return None
    
    def _check_outdated_package(self, dependency: Dependency) -> Optional[Dict[str, Any]]:
        """检查过时包"""
        try:
            latest_version = self._get_latest_version(dependency)
            
            if latest_version and self._is_version_outdated(dependency.version, latest_version):
                return {
                    'dependency': dependency.name,
                    'current_version': dependency.version,
                    'latest_version': latest_version,
                    'update_available': True
                }
        
        except Exception as e:
            self.logger.error(f"版本检查失败 {dependency.name}: {e}")
        
        return None
    
    def _get_latest_version(self, dependency: Dependency) -> Optional[str]:
        """获取最新版本"""
        # 简化实现，实际应该调用相应的包管理器API
        return None
    
    def _is_version_outdated(self, current: str, latest: str) -> bool:
        """检查版本是否过时"""
        # 简化的版本比较
        return current != latest
    
    def _generate_summary(self, vulnerabilities: List[DependencyVulnerability]) -> Dict[str, int]:
        """生成扫描摘要"""
        summary = {
            'total': len(vulnerabilities),
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for vuln in vulnerabilities:
            severity = vuln.vulnerability.severity.value
            if severity in summary:
                summary[severity] += 1
        
        return summary

# 漏洞数据库抽象基类
class VulnerabilityDatabase:
    def query_vulnerabilities(self, package_name: str, package_version: str) -> List[Vulnerability]:
        """查询漏洞"""
        raise NotImplementedError

class OSVDatabase(VulnerabilityDatabase):
    def __init__(self):
        self.base_url = "https://api.osv.dev/v1"
    
    def query_vulnerabilities(self, package_name: str, package_version: str) -> List[Vulnerability]:
        """查询OSV数据库"""
        try:
            url = f"{self.base_url}/query"
            payload = {
                "package": {
                    "name": package_name,
                    "ecosystem": self._get_ecosystem(package_name)
                },
                "version": package_version
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = []
            
            for vuln_data in data.get('vulns', []):
                vulnerability = self._parse_osv_vulnerability(vuln_data)
                if vulnerability:
                    vulnerabilities.append(vulnerability)
            
            return vulnerabilities
        
        except Exception as e:
            print(f"OSV查询失败: {e}")
            return []
    
    def _get_ecosystem(self, package_name: str) -> str:
        """获取生态系统"""
        # 根据包名推断生态系统
        if package_name.startswith('@'):
            return "npm"
        elif '.' in package_name:
            return "PyPI"
        else:
            return "npm"
    
    def _parse_osv_vulnerability(self, vuln_data: Dict[str, Any]) -> Optional[Vulnerability]:
        """解析OSV漏洞数据"""
        try:
            severity = self._determine_severity(vuln_data)
            
            return Vulnerability(
                id=vuln_data.get('id', ''),
                title=vuln_data.get('summary', ''),
                description=vuln_data.get('details', ''),
                severity=severity,
                cvss_score=self._extract_cvss_score(vuln_data),
                cve_id=self._extract_cve_id(vuln_data),
                published_date=vuln_data.get('published'),
                modified_date=vuln_data.get('modified'),
                references=vuln_data.get('references', []),
                affected_versions=self._extract_affected_versions(vuln_data),
                patched_versions=self._extract_patched_versions(vuln_data)
            )
        
        except Exception as e:
            print(f"解析OSV漏洞失败: {e}")
            return None
    
    def _determine_severity(self, vuln_data: Dict[str, Any]) -> VulnerabilitySeverity:
        """确定严重性"""
        severity_info = vuln_data.get('severity', [])
        
        for severity in severity_info:
            score = severity.get('score', '')
            if 'CRITICAL' in score:
                return VulnerabilitySeverity.CRITICAL
            elif 'HIGH' in score:
                return VulnerabilitySeverity.HIGH
            elif 'MEDIUM' in score:
                return VulnerabilitySeverity.MEDIUM
            elif 'LOW' in score:
                return VulnerabilitySeverity.LOW
        
        return VulnerabilitySeverity.INFO
    
    def _extract_cvss_score(self, vuln_data: Dict[str, Any]) -> Optional[float]:
        """提取CVSS评分"""
        severity_info = vuln_data.get('severity', [])
        for severity in severity_info:
            if 'score' in severity:
                try:
                    score_str = severity['score']
                    if isinstance(score_str, str) and score_str.replace('.', '').isdigit():
                        return float(score_str)
                except:
                    pass
        return None
    
    def _extract_cve_id(self, vuln_data: Dict[str, Any]) -> Optional[str]:
        """提取CVE ID"""
        aliases = vuln_data.get('aliases', [])
        for alias in aliases:
            if alias.startswith('CVE-'):
                return alias
        return None
    
    def _extract_affected_versions(self, vuln_data: Dict[str, Any]) -> List[str]:
        """提取受影响版本"""
        versions = []
        
        for affect in vuln_data.get('affected', []):
            ranges = affect.get('ranges', [])
            for range_info in ranges:
                events = range_info.get('events', [])
                for event in events:
                    if 'introduced' in event:
                        versions.append(event['introduced'])
                    if 'fixed' in event:
                        versions.append(f"before {event['fixed']}")
        
        return versions
    
    def _extract_patched_versions(self, vuln_data: Dict[str, Any]) -> List[str]:
        """提取修复版本"""
        versions = []
        
        for affect in vuln_data.get('affected', []):
            ranges = affect.get('ranges', [])
            for range_info in ranges:
                events = range_info.get('events', [])
                for event in events:
                    if 'fixed' in event:
                        versions.append(event['fixed'])
        
        return versions

# 许可证数据库
class LicenseDatabase:
    def __init__(self):
        self.license_policies = {
            'allowed': ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause'],
            'forbidden': ['GPL-3.0', 'AGPL-3.0'],
            'warning': ['LGPL-2.1', 'MPL-2.0']
        }
    
    def get_license_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """获取许可证信息"""
        # 这里应该调用实际的许可证数据库API
        # 简化实现
        return {
            'license': 'MIT',
            'description': 'MIT License',
            'permissions': ['commercial-use', 'modifications', 'distribution', 'private-use'],
            'conditions': ['include-copyright', 'include-license'],
            'limitations': ['liability', 'warranty']
        }
    
    def check_compliance(self, license_name: str) -> Dict[str, Any]:
        """检查许可证合规性"""
        issues = []
        recommendations = []
        
        if license_name in self.license_policies['forbidden']:
            issues.append(f"许可证 {license_name} 在禁止列表中")
            recommendations.append("移除此依赖或寻找替代方案")
            compliant = False
        elif license_name in self.license_policies['warning']:
            issues.append(f"许可证 {license_name} 需要特别注意")
            recommendations.append("评估许可证风险和合规要求")
            compliant = True
        elif license_name in self.license_policies['allowed']:
            compliant = True
        else:
            issues.append(f"未知许可证: {license_name}")
            recommendations.append("确认许可证类型和合规性")
            compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'recommendations': recommendations
        }

# 使用示例
scanner = DependencyScanner()

# 扫描项目
scan_result = scanner.scan_project("./my-project")

print(f"依赖扫描完成:")
print(f"总依赖数: {scan_result.total_dependencies}")
print(f"有漏洞的依赖数: {scan_result.vulnerable_dependencies}")
print(f"发现漏洞数: {len(scan_result.vulnerabilities)}")
print(f"许可证问题数: {len(scan_result.license_issues)}")
print(f"过时包数: {len(scan_result.outdated_packages)}")

# 显示漏洞信息
for vuln in scan_result.vulnerabilities[:5]:  # 显示前5个
    print(f"漏洞: {vuln.dependency.name}@{vuln.dependency.version}")
    print(f"  严重性: {vuln.vulnerability.severity.value}")
    print(f"  描述: {vuln.vulnerability.description}")
    print(f"  修复可用: {vuln.fix_available}")
    if vuln.recommended_version:
        print(f"  推荐版本: {vuln.recommended_version}")
    print()
```

## 参考资源

### 安全标准
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Mitre](https://cwe.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

### 静态分析工具
- [SonarQube](https://www.sonarqube.org/)
- [Checkmarx](https://www.checkmarx.com/)
- [Veracode](https://www.veracode.com/)
- [Fortify](https://www.microfocus.com/en-us/solutions/fortify)

### 动态分析工具
- [OWASP ZAP](https://www.zaproxy.org/)
- [Burp Suite](https://portswigger.net/burp)
- [Acunetix](https://www.acunetix.com/)
- [Nessus](https://www.tenable.com/products/nessus)

### 依赖安全
- [Snyk](https://snyk.io/)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [GitHub Dependabot](https://github.com/features/dependabot)
- [WhiteSource](https://www.whitesourcesoftware.com/)

### 容器安全
- [Trivy](https://github.com/aquasecurity/trivy)
- [Clair](https://github.com/quay/clair)
- [Anchore](https://anchore.com/)
- [Twistlock](https://www.twistlock.com/)
