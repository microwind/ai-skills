---
name: 安全扫描器
description: "当扫描代码安全问题时，检测漏洞，分析安全。识别代码中的安全问题和漏洞。"
license: MIT
---

# 安全扫描器技能

## 概述

安全漏洞是静默的。代码看起来正常但包含漏洞。部署前必须扫描。未扫描的代码是负债。

**核心原则**: 假设代码有漏洞，直到证明安全。好的安全防护应该主动、全面、持续、自动化。坏的安全防护会导致数据泄露、系统被攻击、用户损失。

## 何时使用

**始终:**
- 生产部署前
- 代码处理用户数据时
- 检查常见漏洞时
- 代码审查期间
- 依赖更新后

**触发短语:**
- "扫描安全问题"
- "这安全吗？"
- "检查漏洞"
- "查找安全错误"

## 安全扫描器技能功能

### 代码扫描
- 静态代码分析
- 动态代码分析
- 依赖漏洞检测
- 配置安全检查
- 密钥泄露检测
- 恶意代码识别

### 漏洞检测
- SQL注入检测
- XSS攻击检测
- CSRF漏洞检测
- 路径遍历检测
- 命令注入检测
- 缓冲区溢出检测

### 安全配置
- 权限配置检查
- 网络安全配置
- 数据库安全配置
- 服务器安全配置
- 容器安全配置
- 云服务安全配置

### 合规检查
- 安全标准检查
- 行业合规检查
- 数据保护检查
- 隐私政策检查
- 审计日志检查
- 安全认证检查

## 常见安全问题

**❌ 注入攻击**
- SQL注入漏洞
- NoSQL注入
- 命令注入
- 代码注入
- 模板注入

**❌ 认证问题**
- 弱密码策略
- 会话管理不当
- 多因素认证缺失
- 权限提升漏洞
- 身份验证绕过

**❌ 数据泄露**
- 敏感数据暴露
- 日志信息泄露
- 错误信息泄露
- 调试信息泄露
- 配置文件泄露

**❌ 加密问题**
- 弱加密算法
- 硬编码密钥
- 不安全的随机数
- 传输加密缺失
- 存储加密缺失

## 代码示例

### 安全扫描器

```python
#!/usr/bin/env python3
import re
import ast
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SeverityLevel(Enum):
    """严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class VulnerabilityType(Enum):
    """漏洞类型"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_RANDOM = "insecure_random"
    AUTH_ISSUE = "auth_issue"
    DATA_EXPOSURE = "data_exposure"

@dataclass
class Vulnerability:
    """漏洞信息"""
    type: VulnerabilityType
    severity: SeverityLevel
    file_path: str
    line_number: int
    column: int
    description: str
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None

@dataclass
class SecurityReport:
    """安全报告"""
    scan_time: datetime
    total_files: int
    scanned_files: int
    vulnerabilities: List[Vulnerability]
    summary: Dict[str, int]

class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path)
        self.vulnerabilities: List[Vulnerability] = []
        self.scanned_files = 0
        
        # 安全模式
        self.security_patterns = {
            VulnerabilityType.SQL_INJECTION: [
                r'execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'format\s*\(\s*["\'].*\%.*["\']',
                r'\.execute\s*\(\s*f[\'"][^\'"]*\{[^}]*\}[^\'"]*[\'"]',
                r'select\s+.*\s+from\s+.*\s+where\s+.*\+',
                r'insert\s+into\s+.*\s+values\s*\(.*\+',
                r'update\s+.*\s+set\s+.*\+.*\s+where',
                r'delete\s+from\s+.*\s+where\s+.*\+'
            ],
            VulnerabilityType.XSS: [
                r'innerHTML\s*=.*\+',
                r'outerHTML\s*=.*\+',
                r'document\.write\s*\(\s*.*\+',
                r'eval\s*\(\s*.*\+',
                r'setTimeout\s*\(\s*.*\+',
                r'setInterval\s*\(\s*.*\+',
                r'<script[^>]*>.*</script>',
                r'on\w+\s*=\s*["\'][^"\']*["\']',
                r'href\s*=\s*["\']javascript:',
                r'src\s*=\s*["\'][^"\']*["\']'
            ],
            VulnerabilityType.COMMAND_INJECTION: [
                r'system\s*\(\s*.*\+',
                r'exec\s*\(\s*.*\+',
                r'subprocess\.call\s*\(\s*.*\+',
                r'os\.system\s*\(\s*.*\+',
                r'eval\s*\(\s*.*\+',
                r'shell_exec\s*\(\s*.*\+',
                r'passthru\s*\(\s*.*\+',
                r'popen\s*\(\s*.*\+'
            ],
            VulnerabilityType.HARDCODED_SECRET: [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'secret\s*=\s*["\'][^"\']{16,}["\']',
                r'key\s*=\s*["\'][^"\']{16,}["\']',
                r'token\s*=\s*["\'][^"\']{16,}["\']',
                r'api_key\s*=\s*["\'][^"\']{16,}["\']',
                r'private_key\s*=\s*["\'][^"\']{16,}["\']',
                r'access_token\s*=\s*["\'][^"\']{16,}["\']',
                r'auth\s*=\s*["\'][^"\']{16,}["\']'
            ],
            VulnerabilityType.WEAK_CRYPTO: [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'hashlib\.md5',
                r'hashlib\.sha1',
                r'Crypto\.Cipher\.DES',
                r'Crypto\.Cipher\.RC4',
                r'openssl_encrypt\s*\([^,]*,\s*["\']DES["\']',
                r'openssl_encrypt\s*\([^,]*,\s*["\']RC4["\']'
            ],
            VulnerabilityType.INSECURE_RANDOM: [
                r'random\.random\s*\(',
                r'math\.random\s*\(',
                r'random\.randint\s*\(',
                r'random\.randrange\s*\(',
                r'time\.time\s*\(',
                r'os\.getpid\s*\(',
                r'hash\s*\([^)]*\)\s*\%[^)]*\)'
            ],
            VulnerabilityType.PATH_TRAVERSAL: [
                r'open\s*\(\s*.*\+',
                r'file\s*\(\s*.*\+',
                r'read_file\s*\(\s*.*\+',
                r'write_file\s*\(\s*.*\+',
                r'\.\.\/',
                r'\.\.\\',
                r'path\s*\.\s*join\s*\([^)]*\+[^)]*\)',
                r'os\.path\.join\s*\([^)]*\+[^)]*\)'
            ]
        }
        
        # CWE映射
        self.cwe_mapping = {
            VulnerabilityType.SQL_INJECTION: "CWE-89",
            VulnerabilityType.XSS: "CWE-79",
            VulnerabilityType.CSRF: "CWE-352",
            VulnerabilityType.PATH_TRAVERSAL: "CWE-22",
            VulnerabilityType.COMMAND_INJECTION: "CWE-78",
            VulnerabilityType.HARDCODED_SECRET: "CWE-798",
            VulnerabilityType.WEAK_CRYPTO: "CWE-327",
            VulnerabilityType.INSECURE_RANDOM: "CWE-338",
            VulnerabilityType.AUTH_ISSUE: "CWE-287",
            VulnerabilityType.DATA_EXPOSURE: "CWE-200"
        }
        
        # CVSS评分
        self.cvss_scores = {
            SeverityLevel.CRITICAL: 9.0,
            SeverityLevel.HIGH: 7.0,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 3.0,
            SeverityLevel.INFO: 1.0
        }
    
    def scan(self, file_patterns: Optional[List[str]] = None) -> SecurityReport:
        """执行安全扫描"""
        start_time = datetime.now()
        
        # 获取要扫描的文件
        files_to_scan = self._get_files_to_scan(file_patterns)
        
        # 扫描每个文件
        for file_path in files_to_scan:
            self._scan_file(file_path)
        
        # 生成报告
        report = SecurityReport(
            scan_time=start_time,
            total_files=len(files_to_scan),
            scanned_files=self.scanned_files,
            vulnerabilities=self.vulnerabilities,
            summary=self._generate_summary()
        )
        
        return report
    
    def _get_files_to_scan(self, patterns: Optional[List[str]]) -> List[Path]:
        """获取要扫描的文件"""
        if not patterns:
            patterns = ["*.py", "*.js", "*.java", "*.php", "*.rb", "*.go", "*.cs"]
        
        files = []
        for pattern in patterns:
            files.extend(self.scan_path.rglob(pattern))
        
        # 排除不需要扫描的目录
        exclude_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
        files = [f for f in files if not any(exclude_dir in f.parts for exclude_dir in exclude_dirs)]
        
        return files
    
    def _scan_file(self, file_path: Path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            self.scanned_files += 1
            
            # 根据文件类型选择扫描方法
            if file_path.suffix == '.py':
                self._scan_python_file(file_path, lines)
            elif file_path.suffix == '.js':
                self._scan_javascript_file(file_path, lines)
            elif file_path.suffix == '.java':
                self._scan_java_file(file_path, lines)
            else:
                self._scan_generic_file(file_path, lines)
        
        except Exception as e:
            print(f"扫描文件 {file_path} 时出错: {e}")
    
    def _scan_python_file(self, file_path: Path, lines: List[str]):
        """扫描Python文件"""
        try:
            # 解析AST
            tree = ast.parse('\n'.join(lines))
            
            # 扫描AST节点
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    self._check_python_function_call(file_path, node, lines)
                elif isinstance(node, ast.Import):
                    self._check_python_import(file_path, node, lines)
                elif isinstance(node, ast.Assign):
                    self._check_python_assignment(file_path, node, lines)
        
        except SyntaxError:
            # 如果解析失败，使用文本扫描
            self._scan_generic_file(file_path, lines)
    
    def _check_python_function_call(self, file_path: Path, node: ast.Call, lines: List[str]):
        """检查Python函数调用"""
        # 检查危险的函数调用
        dangerous_functions = {
            'eval': VulnerabilityType.COMMAND_INJECTION,
            'exec': VulnerabilityType.COMMAND_INJECTION,
            'system': VulnerabilityType.COMMAND_INJECTION,
            'subprocess.call': VulnerabilityType.COMMAND_INJECTION,
            'subprocess.run': VulnerabilityType.COMMAND_INJECTION,
            'os.system': VulnerabilityType.COMMAND_INJECTION,
            'hashlib.md5': VulnerabilityType.WEAK_CRYPTO,
            'hashlib.sha1': VulnerabilityType.WEAK_CRYPTO,
            'random.random': VulnerabilityType.INSECURE_RANDOM,
            'random.randint': VulnerabilityType.INSECURE_RANDOM
        }
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in dangerous_functions:
                vuln_type = dangerous_functions[func_name]
                line_num = node.lineno - 1
                if line_num < len(lines):
                    self._add_vulnerability(
                        vuln_type,
                        file_path,
                        line_num + 1,
                        1,
                        f"使用了危险的函数: {func_name}",
                        lines[line_num],
                        f"避免使用 {func_name}，使用更安全的替代方案"
                    )
        
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                func_name = node.func.attr
                full_name = f"{module_name}.{func_name}"
                
                if full_name in dangerous_functions:
                    vuln_type = dangerous_functions[full_name]
                    line_num = node.lineno - 1
                    if line_num < len(lines):
                        self._add_vulnerability(
                            vuln_type,
                            file_path,
                            line_num + 1,
                            1,
                            f"使用了危险的函数: {full_name}",
                            lines[line_num],
                            f"避免使用 {full_name}，使用更安全的替代方案"
                        )
    
    def _check_python_import(self, file_path: Path, node: ast.Import, lines: List[str]):
        """检查Python导入"""
        dangerous_modules = {
            'pickle': 'pickle模块可能执行恶意代码',
            'cPickle': 'cPickle模块可能执行恶意代码',
            'subprocess': 'subprocess模块可能被用于命令注入',
            'os': 'os模块可能被用于命令注入'
        }
        
        for alias in node.names:
            if alias.name in dangerous_modules:
                line_num = node.lineno - 1
                if line_num < len(lines):
                    self._add_vulnerability(
                        VulnerabilityType.COMMAND_INJECTION,
                        file_path,
                        line_num + 1,
                        1,
                        f"导入了危险的模块: {alias.name}",
                        lines[line_num],
                        f"谨慎使用 {alias.name} 模块，确保输入验证"
                    )
    
    def _check_python_assignment(self, file_path: Path, node: ast.Assign, lines: List[str]):
        """检查Python赋值"""
        # 检查硬编码密钥
        if isinstance(node.value, ast.Constant):
            value = str(node.value)
            if len(value) > 16 and any(keyword in str(node.targets[0]).lower() 
                                   for keyword in ['password', 'secret', 'key', 'token']):
                line_num = node.lineno - 1
                if line_num < len(lines):
                    self._add_vulnerability(
                        VulnerabilityType.HARDCODED_SECRET,
                        file_path,
                        line_num + 1,
                        1,
                        f"检测到硬编码的敏感信息",
                        lines[line_num],
                        "使用环境变量或配置文件存储敏感信息"
                    )
    
    def _scan_javascript_file(self, file_path: Path, lines: List[str]):
        """扫描JavaScript文件"""
        for line_num, line in enumerate(lines):
            # 检查XSS漏洞
            xss_patterns = [
                r'innerHTML\s*=',
                r'outerHTML\s*=',
                r'document\.write\s*\(',
                r'eval\s*\(',
                r'setTimeout\s*\([^,]*\+',
                r'setInterval\s*\([^,]*\+'
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_vulnerability(
                        VulnerabilityType.XSS,
                        file_path,
                        line_num + 1,
                        1,
                        "检测到潜在的XSS漏洞",
                        line,
                        "使用textContent替代innerHTML，或使用安全的DOM操作方法"
                    )
            
            # 检查硬编码密钥
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'secret\s*=\s*["\'][^"\']{16,}["\']',
                r'key\s*=\s*["\'][^"\']{16,}["\']',
                r'token\s*=\s*["\'][^"\']{16,}["\']'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_vulnerability(
                        VulnerabilityType.HARDCODED_SECRET,
                        file_path,
                        line_num + 1,
                        1,
                        "检测到硬编码的敏感信息",
                        line,
                        "使用环境变量或配置文件存储敏感信息"
                    )
    
    def _scan_java_file(self, file_path: Path, lines: List[str]):
        """扫描Java文件"""
        for line_num, line in enumerate(lines):
            # 检查SQL注入
            sql_patterns = [
                r'Statement\.execute\s*\(',
                r'createStatement\s*\(\s*\)',
                r'executeQuery\s*\([^)]*\+',
                r'executeUpdate\s*\([^)]*\+'
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_vulnerability(
                        VulnerabilityType.SQL_INJECTION,
                        file_path,
                        line_num + 1,
                        1,
                        "检测到潜在的SQL注入漏洞",
                        line,
                        "使用PreparedStatement替代Statement，使用参数化查询"
                    )
            
            # 检查弱加密
            crypto_patterns = [
                r'MessageDigest\.getInstance\s*\(\s*["\']MD5["\']',
                r'MessageDigest\.getInstance\s*\(\s*["\']SHA1["\']',
                r'Cipher\.getInstance\s*\(\s*["\']DES["\']',
                r'Cipher\.getInstance\s*\(\s*["\']RC4["\']'
            ]
            
            for pattern in crypto_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_vulnerability(
                        VulnerabilityType.WEAK_CRYPTO,
                        file_path,
                        line_num + 1,
                        1,
                        "检测到弱加密算法",
                        line,
                        "使用强加密算法如AES-256、SHA-256等"
                    )
    
    def _scan_generic_file(self, file_path: Path, lines: List[str]):
        """通用文件扫描"""
        for line_num, line in enumerate(lines):
            # 扫描所有模式
            for vuln_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self._add_vulnerability(
                            vuln_type,
                            file_path,
                            line_num + 1,
                            1,
                            f"检测到潜在的安全问题: {vuln_type.value}",
                            line,
                            self._get_recommendation(vuln_type)
                        )
    
    def _add_vulnerability(self, vuln_type: VulnerabilityType, file_path: Path, 
                          line_num: int, column: int, description: str, 
                          code_snippet: str, recommendation: str):
        """添加漏洞"""
        severity = self._determine_severity(vuln_type)
        cwe_id = self.cwe_mapping.get(vuln_type)
        cvss_score = self.cvss_scores.get(severity)
        
        vulnerability = Vulnerability(
            type=vuln_type,
            severity=severity,
            file_path=str(file_path),
            line_number=line_num,
            column=column,
            description=description,
            code_snippet=code_snippet,
            recommendation=recommendation,
            cwe_id=cwe_id,
            cvss_score=cvss_score
        )
        
        self.vulnerabilities.append(vulnerability)
    
    def _determine_severity(self, vuln_type: VulnerabilityType) -> SeverityLevel:
        """确定漏洞严重性"""
        severity_mapping = {
            VulnerabilityType.SQL_INJECTION: SeverityLevel.CRITICAL,
            VulnerabilityType.XSS: SeverityLevel.HIGH,
            VulnerabilityType.COMMAND_INJECTION: SeverityLevel.CRITICAL,
            VulnerabilityType.HARDCODED_SECRET: SeverityLevel.HIGH,
            VulnerabilityType.WEAK_CRYPTO: SeverityLevel.MEDIUM,
            VulnerabilityType.INSECURE_RANDOM: SeverityLevel.MEDIUM,
            VulnerabilityType.PATH_TRAVERSAL: SeverityLevel.HIGH,
            VulnerabilityType.CSRF: SeverityLevel.MEDIUM,
            VulnerabilityType.AUTH_ISSUE: SeverityLevel.HIGH,
            VulnerabilityType.DATA_EXPOSURE: SeverityLevel.MEDIUM
        }
        
        return severity_mapping.get(vuln_type, SeverityLevel.MEDIUM)
    
    def _get_recommendation(self, vuln_type: VulnerabilityType) -> str:
        """获取修复建议"""
        recommendations = {
            VulnerabilityType.SQL_INJECTION: "使用参数化查询或ORM框架，避免字符串拼接SQL",
            VulnerabilityType.XSS: "对用户输入进行HTML编码，使用安全的DOM操作方法",
            VulnerabilityType.COMMAND_INJECTION: "避免直接执行用户输入，使用白名单验证",
            VulnerabilityType.HARDCODED_SECRET: "使用环境变量或密钥管理服务存储敏感信息",
            VulnerabilityType.WEAK_CRYPTO: "使用强加密算法如AES-256、SHA-256等",
            VulnerabilityType.INSECURE_RANDOM: "使用密码学安全的随机数生成器",
            VulnerabilityType.PATH_TRAVERSAL: "验证用户输入，使用白名单限制文件访问",
            VulnerabilityType.CSRF: "使用CSRF令牌，验证请求来源",
            VulnerabilityType.AUTH_ISSUE: "实施强身份认证机制，使用多因素认证",
            VulnerabilityType.DATA_EXPOSURE: "避免在日志和错误信息中暴露敏感数据"
        }
        
        return recommendations.get(vuln_type, "请参考安全最佳实践进行修复")
    
    def _generate_summary(self) -> Dict[str, int]:
        """生成漏洞摘要"""
        summary = {
            "total": len(self.vulnerabilities),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        
        for vuln in self.vulnerabilities:
            summary[vuln.severity.value] += 1
        
        return summary
    
    def generate_report(self, output_format: str = "json") -> str:
        """生成扫描报告"""
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        elif output_format == "markdown":
            return self._generate_markdown_report()
        else:
            raise ValueError(f"不支持的格式: {output_format}")
    
    def _generate_json_report(self) -> str:
        """生成JSON格式报告"""
        report_data = {
            "scan_time": datetime.now().isoformat(),
            "summary": self._generate_summary(),
            "vulnerabilities": [
                {
                    "type": vuln.type.value,
                    "severity": vuln.severity.value,
                    "file_path": vuln.file_path,
                    "line_number": vuln.line_number,
                    "column": vuln.column,
                    "description": vuln.description,
                    "code_snippet": vuln.code_snippet,
                    "recommendation": vuln.recommendation,
                    "cwe_id": vuln.cwe_id,
                    "cvss_score": vuln.cvss_score
                }
                for vuln in self.vulnerabilities
            ]
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self) -> str:
        """生成HTML格式报告"""
        lines = []
        
        # HTML头部
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<meta charset='utf-8'>")
        lines.append("<title>安全扫描报告</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; margin: 40px; }")
        lines.append("h1 { color: #333; }")
        lines.append("h2 { color: #666; }")
        lines.append(".critical { color: #d32f2f; }")
        lines.append(".high { color: #f57c00; }")
        lines.append(".medium { color: #fbc02d; }")
        lines.append(".low { color: #388e3c; }")
        lines.append(".info { color: #1976d2; }")
        lines.append("pre { background: #f5f5f5; padding: 10px; border-radius: 4px; }")
        lines.append(".vulnerability { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        
        # 标题
        lines.append("<h1>安全扫描报告</h1>")
        lines.append(f"<p>扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        # 摘要
        summary = self._generate_summary()
        lines.append("<h2>漏洞摘要</h2>")
        lines.append("<ul>")
        lines.append(f"<li class='critical'>严重: {summary['critical']}</li>")
        lines.append(f"<li class='high'>高危: {summary['high']}</li>")
        lines.append(f"<li class='medium'>中危: {summary['medium']}</li>")
        lines.append(f"<li class='low'>低危: {summary['low']}</li>")
        lines.append(f"<li class='info'>信息: {summary['info']}</li>")
        lines.append(f"<li>总计: {summary['total']}</li>")
        lines.append("</ul>")
        
        # 漏洞详情
        lines.append("<h2>漏洞详情</h2>")
        for vuln in self.vulnerabilities:
            lines.append(f"<div class='vulnerability {vuln.severity.value}'>")
            lines.append(f"<h3>{vuln.type.value} - {vuln.severity.value.upper()}</h3>")
            lines.append(f"<p><strong>文件:</strong> {vuln.file_path}:{vuln.line_number}</p>")
            lines.append(f"<p><strong>描述:</strong> {vuln.description}</p>")
            lines.append(f"<p><strong>代码:</strong></p>")
            lines.append(f"<pre>{vuln.code_snippet}</pre>")
            lines.append(f"<p><strong>建议:</strong> {vuln.recommendation}</p>")
            if vuln.cwe_id:
                lines.append(f"<p><strong>CWE:</strong> {vuln.cwe_id}</p>")
            if vuln.cvss_score:
                lines.append(f"<p><strong>CVSS:</strong> {vuln.cvss_score}</p>")
            lines.append("</div>")
        
        # HTML尾部
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self) -> str:
        """生成Markdown格式报告"""
        lines = []
        
        # 标题
        lines.append("# 安全扫描报告")
        lines.append("")
        lines.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 摘要
        summary = self._generate_summary()
        lines.append("## 漏洞摘要")
        lines.append("")
        lines.append(f"- **严重**: {summary['critical']}")
        lines.append(f"- **高危**: {summary['high']}")
        lines.append(f"- **中危**: {summary['medium']}")
        lines.append(f"- **低危**: {summary['low']}")
        lines.append(f"- **信息**: {summary['info']}")
        lines.append(f"- **总计**: {summary['total']}")
        lines.append("")
        
        # 漏洞详情
        lines.append("## 漏洞详情")
        lines.append("")
        
        for vuln in self.vulnerabilities:
            lines.append(f"### {vuln.type.value} - {vuln.severity.value.upper()}")
            lines.append("")
            lines.append(f"**文件**: `{vuln.file_path}:{vuln.line_number}`")
            lines.append("")
            lines.append(f"**描述**: {vuln.description}")
            lines.append("")
            lines.append(f"**代码**:")
            lines.append("")
            lines.append("```")
            lines.append(vuln.code_snippet)
            lines.append("```")
            lines.append("")
            lines.append(f"**建议**: {vuln.recommendation}")
            lines.append("")
            if vuln.cwe_id:
                lines.append(f"**CWE**: {vuln.cwe_id}")
                lines.append("")
            if vuln.cvss_score:
                lines.append(f"**CVSS**: {vuln.cvss_score}")
                lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='安全扫描器')
    parser.add_argument('path', nargs='?', default='.', help='扫描路径')
    parser.add_argument('--patterns', nargs='+', help='文件模式')
    parser.add_argument('--output', help='输出文件')
    parser.add_argument('--format', choices=['json', 'html', 'markdown'], 
                       default='json', help='输出格式')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low', 'info'],
                       help='最低严重级别')
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.path)
    
    try:
        # 执行扫描
        report = scanner.scan(args.patterns)
        
        # 过滤严重级别
        if args.severity:
            severity_order = ['critical', 'high', 'medium', 'low', 'info']
            min_index = severity_order.index(args.severity)
            filtered_vulns = []
            for vuln in report.vulnerabilities:
                vuln_index = severity_order.index(vuln.severity.value)
                if vuln_index <= min_index:
                    filtered_vulns.append(vuln)
            report.vulnerabilities = filtered_vulns
            report.summary = scanner._generate_summary()
        
        # 生成报告
        scan_report = scanner.generate_report(args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(scan_report)
            print(f"报告已保存到: {args.output}")
        else:
            print(scan_report)
    
    except Exception as e:
        print(f"扫描失败: {e}")
        exit(1)
```

### 依赖安全扫描器

```python
#!/usr/bin/env python3
import re
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class DependencyVulnerability:
    """依赖漏洞"""
    package_name: str
    version: str
    vulnerability_id: str
    severity: str
    description: str
    cve_id: Optional[str]
    cvss_score: Optional[float]
    fixed_in: Optional[str]
    references: List[str]

@dataclass
class DependencyReport:
    """依赖报告"""
    scan_time: datetime
    total_dependencies: int
    vulnerable_dependencies: int
    vulnerabilities: List[DependencyVulnerability]
    package_files: List[str]

class DependencySecurityScanner:
    """依赖安全扫描器"""
    
    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path)
        self.vulnerabilities: List[DependencyVulnerability] = []
        self.package_files: List[str] = []
        
        # 漏洞数据库API
        self.vulnerability_apis = {
            "npm": "https://registry.npmjs.org/-/v1/security advisories",
            "pypi": "https://pypi.org/pypi/{}/json",
            "maven": "https://search.maven.org/solrsearch/select",
            "rubygems": "https://rubygems.org/api/v1/gems/{}/versions.json"
        }
    
    def scan_dependencies(self) -> DependencyReport:
        """扫描依赖漏洞"""
        start_time = datetime.now()
        
        # 查找包文件
        self._find_package_files()
        
        # 解析依赖
        dependencies = self._parse_dependencies()
        
        # 检查漏洞
        self._check_vulnerabilities(dependencies)
        
        # 生成报告
        report = DependencyReport(
            scan_time=start_time,
            total_dependencies=len(dependencies),
            vulnerable_dependencies=len(set(vuln.package_name for vuln in self.vulnerabilities)),
            vulnerabilities=self.vulnerabilities,
            package_files=self.package_files
        )
        
        return report
    
    def _find_package_files(self):
        """查找包文件"""
        package_files = [
            "package.json", "package-lock.json", "yarn.lock",
            "requirements.txt", "Pipfile", "Pipfile.lock", "poetry.lock",
            "pom.xml", "build.gradle", "gradle.lockfile",
            "Gemfile", "Gemfile.lock",
            "go.mod", "go.sum",
            "Cargo.toml", "Cargo.lock"
        ]
        
        for file_name in package_files:
            files = list(self.scan_path.rglob(file_name))
            self.package_files.extend(str(f) for f in files)
    
    def _parse_dependencies(self) -> Dict[str, str]:
        """解析依赖"""
        dependencies = {}
        
        for file_path in self.package_files:
            file_name = Path(file_path).name
            
            if file_name == "package.json":
                deps = self._parse_package_json(file_path)
                dependencies.update(deps)
            elif file_name == "requirements.txt":
                deps = self._parse_requirements_txt(file_path)
                dependencies.update(deps)
            elif file_name == "pom.xml":
                deps = self._parse_pom_xml(file_path)
                dependencies.update(deps)
            elif file_name == "Gemfile":
                deps = self._parse_gemfile(file_path)
                dependencies.update(deps)
            elif file_name == "go.mod":
                deps = self._parse_go_mod(file_path)
                dependencies.update(deps)
            elif file_name == "Cargo.toml":
                deps = self._parse_cargo_toml(file_path)
                dependencies.update(deps)
        
        return dependencies
    
    def _parse_package_json(self, file_path: str) -> Dict[str, str]:
        """解析package.json"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dependencies = {}
            
            # dependencies
            if 'dependencies' in data:
                dependencies.update(data['dependencies'])
            
            # devDependencies
            if 'devDependencies' in data:
                dependencies.update(data['devDependencies'])
            
            return dependencies
        except Exception:
            return {}
    
    def _parse_requirements_txt(self, file_path: str) -> Dict[str, str]:
        """解析requirements.txt"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dependencies = {}
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 解析格式: package==version
                    if '==' in line:
                        package, version = line.split('==', 1)
                        dependencies[package.strip()] = version.strip()
                    elif '>=' in line:
                        package, version = line.split('>=', 1)
                        dependencies[package.strip()] = version.strip()
                    elif '<=' in line:
                        package, version = line.split('<=', 1)
                        dependencies[package.strip()] = version.strip()
            
            return dependencies
        except Exception:
            return {}
    
    def _parse_pom_xml(self, file_path: str) -> Dict[str, str]:
        """解析pom.xml"""
        try:
            # 使用正则表达式解析XML（简化实现）
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = {}
            
            # 查找dependency标签
            dependency_pattern = r'<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?<version>([^<]+)</version>.*?</dependency>'
            matches = re.findall(dependency_pattern, content, re.DOTALL)
            
            for group_id, artifact_id, version in matches:
                package_name = f"{group_id}:{artifact_id}"
                dependencies[package_name] = version
            
            return dependencies
        except Exception:
            return {}
    
    def _parse_gemfile(self, file_path: str) -> Dict[str, str]:
        """解析Gemfile"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dependencies = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('gem '):
                    # 解析格式: gem 'package', 'version'
                    match = re.search(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?", line)
                    if match:
                        package = match.group(1)
                        version = match.group(2) if match.group(2) else "latest"
                        dependencies[package] = version
            
            return dependencies
        except Exception:
            return {}
    
    def _parse_go_mod(self, file_path: str) -> Dict[str, str]:
        """解析go.mod"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dependencies = {}
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('module'):
                    parts = line.split()
                    if len(parts) >= 2:
                        package = parts[0]
                        version = parts[1]
                        dependencies[package] = version
            
            return dependencies
        except Exception:
            return {}
    
    def _parse_cargo_toml(self, file_path: str) -> Dict[str, str]:
        """解析Cargo.toml"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = {}
            
            # 查找[dependencies]部分
            deps_section = re.search(r'\[dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
            if deps_section:
                deps_content = deps_section.group(1)
                
                # 解析每个依赖
                for line in deps_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            package, version = line.split('=', 1)
                            package = package.strip()
                            version = version.strip().strip('"\'')
                            dependencies[package] = version
            
            return dependencies
        except Exception:
            return {}
    
    def _check_vulnerabilities(self, dependencies: Dict[str, str]):
        """检查漏洞"""
        for package, version in dependencies.items():
            # 根据包名判断包管理器
            if self._is_npm_package(package):
                self._check_npm_vulnerability(package, version)
            elif self._is_pypi_package(package):
                self._check_pypi_vulnerability(package, version)
            elif self._is_maven_package(package):
                self._check_maven_vulnerability(package, version)
            elif self._is_ruby_package(package):
                self._check_ruby_vulnerability(package, version)
    
    def _is_npm_package(self, package: str) -> bool:
        """判断是否为npm包"""
        # 简化判断：包名通常不包含冒号
        return ':' not in package and '.' not in package
    
    def _is_pypi_package(self, package: str) -> bool:
        """判断是否为PyPI包"""
        # 简化判断：PyPI包名通常使用下划线或连字符
        return '_' in package or '-' in package
    
    def _is_maven_package(self, package: str) -> bool:
        """判断是否为Maven包"""
        # Maven包格式: groupId:artifactId
        return ':' in package and package.count(':') == 1
    
    def _is_ruby_package(self, package: str) -> bool:
        """判断是否为Ruby包"""
        # 简化判断：Ruby包名通常使用连字符
        return '-' in package and not self._is_npm_package(package)
    
    def _check_npm_vulnerability(self, package: str, version: str):
        """检查npm漏洞"""
        try:
            # 使用npm audit命令
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                
                if 'vulnerabilities' in audit_data:
                    for vuln_id, vuln_data in audit_data['vulnerabilities'].items():
                        if vuln_data.get('package_name') == package:
                            vulnerability = DependencyVulnerability(
                                package_name=package,
                                version=version,
                                vulnerability_id=vuln_id,
                                severity=vuln_data.get('severity', 'unknown'),
                                description=vuln_data.get('title', ''),
                                cve_id=vuln_data.get('cwe'),
                                cvss_score=vuln_data.get('cvss_score'),
                                fixed_in=vuln_data.get('fix_available'),
                                references=vuln_data.get('url', [])
                            )
                            self.vulnerabilities.append(vulnerability)
        
        except Exception:
            # 如果npm audit失败，尝试使用API
            self._check_npm_api_vulnerability(package, version)
    
    def _check_npm_api_vulnerability(self, package: str, version: str):
        """使用npm API检查漏洞"""
        try:
            url = f"https://registry.npmjs.org/{package}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查是否有安全公告
                if 'security' in data:
                    for advisory in data['security']:
                        vulnerability = DependencyVulnerability(
                            package_name=package,
                            version=version,
                            vulnerability_id=advisory.get('id', ''),
                            severity=advisory.get('severity', 'unknown'),
                            description=advisory.get('title', ''),
                            cve_id=advisory.get('cwe'),
                            cvss_score=advisory.get('cvss_score'),
                            fixed_in=advisory.get('fixed_in'),
                            references=advisory.get('url', [])
                        )
                        self.vulnerabilities.append(vulnerability)
        
        except Exception:
            pass
    
    def _check_pypi_vulnerability(self, package: str, version: str):
        """检查PyPI漏洞"""
        try:
            url = f"https://pypi.org/pypi/{package}/json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查版本是否有已知漏洞
                # 这里简化实现，实际应该查询漏洞数据库
                vulnerabilities = data.get('vulnerabilities', [])
                
                for vuln in vulnerabilities:
                    # 检查当前版本是否受影响
                    affected_versions = vuln.get('affected_versions', [])
                    if version in affected_versions:
                        vulnerability = DependencyVulnerability(
                            package_name=package,
                            version=version,
                            vulnerability_id=vuln.get('id', ''),
                            severity=vuln.get('severity', 'unknown'),
                            description=vuln.get('summary', ''),
                            cve_id=vuln.get('cve_id'),
                            cvss_score=vuln.get('cvss_score'),
                            fixed_in=vuln.get('fixed_in'),
                            references=vuln.get('references', [])
                        )
                        self.vulnerabilities.append(vulnerability)
        
        except Exception:
            pass
    
    def _check_maven_vulnerability(self, package: str, version: str):
        """检查Maven漏洞"""
        # 简化实现，实际应该使用OSS Index或其他漏洞数据库
        pass
    
    def _check_ruby_vulnerability(self, package: str, version: str):
        """检查Ruby漏洞"""
        # 简化实现，实际应该使用RubyGems API或漏洞数据库
        pass
    
    def generate_report(self, output_format: str = "json") -> str:
        """生成报告"""
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        elif output_format == "markdown":
            return self._generate_markdown_report()
        else:
            raise ValueError(f"不支持的格式: {output_format}")
    
    def _generate_json_report(self) -> str:
        """生成JSON报告"""
        report_data = {
            "scan_time": datetime.now().isoformat(),
            "total_dependencies": len(self.vulnerabilities),
            "vulnerable_dependencies": len(set(vuln.package_name for vuln in self.vulnerabilities)),
            "package_files": self.package_files,
            "vulnerabilities": [
                {
                    "package_name": vuln.package_name,
                    "version": vuln.version,
                    "vulnerability_id": vuln.vulnerability_id,
                    "severity": vuln.severity,
                    "description": vuln.description,
                    "cve_id": vuln.cve_id,
                    "cvss_score": vuln.cvss_score,
                    "fixed_in": vuln.fixed_in,
                    "references": vuln.references
                }
                for vuln in self.vulnerabilities
            ]
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self) -> str:
        """生成HTML报告"""
        lines = []
        
        # HTML头部
        lines.append("<!DOCTYPE html>")
        lines.append("<html>")
        lines.append("<head>")
        lines.append("<meta charset='utf-8'>")
        lines.append("<title>依赖安全扫描报告</title>")
        lines.append("<style>")
        lines.append("body { font-family: Arial, sans-serif; margin: 40px; }")
        lines.append("h1 { color: #333; }")
        lines.append("h2 { color: #666; }")
        lines.append(".critical { color: #d32f2f; }")
        lines.append(".high { color: #f57c00; }")
        lines.append(".medium { color: #fbc02d; }")
        lines.append(".low { color: #388e3c; }")
        lines.append(".vulnerability { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; }")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")
        
        # 标题
        lines.append("<h1>依赖安全扫描报告</h1>")
        lines.append(f"<p>扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        # 摘要
        lines.append("<h2>漏洞摘要</h2>")
        lines.append(f"<p>总依赖数: {len(self.vulnerabilities)}</p>")
        lines.append(f"<p>有漏洞的依赖: {len(set(vuln.package_name for vuln in self.vulnerabilities))}</p>")
        
        # 漏洞详情
        lines.append("<h2>漏洞详情</h2>")
        for vuln in self.vulnerabilities:
            lines.append(f"<div class='vulnerability {vuln.severity}'>")
            lines.append(f"<h3>{vuln.package_name} - {vuln.severity.upper()}</h3>")
            lines.append(f"<p><strong>版本:</strong> {vuln.version}</p>")
            lines.append(f"<p><strong>漏洞ID:</strong> {vuln.vulnerability_id}</p>")
            lines.append(f"<p><strong>描述:</strong> {vuln.description}</p>")
            if vuln.cve_id:
                lines.append(f"<p><strong>CVE:</strong> {vuln.cve_id}</p>")
            if vuln.fixed_in:
                lines.append(f"<p><strong>修复版本:</strong> {vuln.fixed_in}</p>")
            if vuln.references:
                lines.append(f"<p><strong>参考:</strong> {', '.join(vuln.references)}</p>")
            lines.append("</div>")
        
        # HTML尾部
        lines.append("</body>")
        lines.append("</html>")
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self) -> str:
        """生成Markdown报告"""
        lines = []
        
        # 标题
        lines.append("# 依赖安全扫描报告")
        lines.append("")
        lines.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 摘要
        lines.append("## 漏洞摘要")
        lines.append("")
        lines.append(f"- **总依赖数**: {len(self.vulnerabilities)}")
        lines.append(f"- **有漏洞的依赖**: {len(set(vuln.package_name for vuln in self.vulnerabilities))}")
        lines.append("")
        
        # 漏洞详情
        lines.append("## 漏洞详情")
        lines.append("")
        
        for vuln in self.vulnerabilities:
            lines.append(f"### {vuln.package_name} - {vuln.severity.upper()}")
            lines.append("")
            lines.append(f"**版本**: {vuln.version}")
            lines.append("")
            lines.append(f"**漏洞ID**: {vuln.vulnerability_id}")
            lines.append("")
            lines.append(f"**描述**: {vuln.description}")
            lines.append("")
            if vuln.cve_id:
                lines.append(f"**CVE**: {vuln.cve_id}")
                lines.append("")
            if vuln.fixed_in:
                lines.append(f"**修复版本**: {vuln.fixed_in}")
                lines.append("")
            if vuln.references:
                lines.append(f"**参考**: {', '.join(vuln.references)}")
                lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='依赖安全扫描器')
    parser.add_argument('path', nargs='?', default='.', help='扫描路径')
    parser.add_argument('--output', help='输出文件')
    parser.add_argument('--format', choices=['json', 'html', 'markdown'], 
                       default='json', help='输出格式')
    
    args = parser.parse_args()
    
    scanner = DependencySecurityScanner(args.path)
    
    try:
        # 执行扫描
        report = scanner.scan_dependencies()
        
        # 生成报告
        scan_report = scanner.generate_report(args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(scan_report)
            print(f"报告已保存到: {args.output}")
        else:
            print(scan_report)
    
    except Exception as e:
        print(f"扫描失败: {e}")
        exit(1)
```

## 最佳实践

### 安全编码
- **输入验证**: 对所有用户输入进行严格验证
- **输出编码**: 对输出内容进行适当编码
- **最小权限**: 使用最小权限原则
- **安全默认**: 使用安全的默认配置

### 漏洞管理
- **定期扫描**: 建立定期安全扫描机制
- **及时修复**: 优先修复高危漏洞
- **漏洞跟踪**: 建立漏洞跟踪系统
- **安全培训**: 提供安全编码培训

### 依赖安全
- **依赖审计**: 定期审计第三方依赖
- **版本更新**: 及时更新到安全版本
- **供应链安全**: 关注软件供应链安全
- **漏洞监控**: 监控新发现的漏洞

### 合规要求
- **安全标准**: 遵循相关安全标准
- **法规遵从**: 满足法规要求
- **审计准备**: 准备安全审计
- **文档记录**: 记录安全措施

## 相关技能

- [代码格式化器](./code-formatter/) - 代码格式规范
- [环境验证器](./env-validator/) - 环境安全检查
- [文件分析器](./file-analyzer/) - 文件安全分析
- [依赖分析器](./dependency-analyzer/) - 依赖安全分析

**SQL 注入**
- Str在g c在c在en在i在 在 查询
- 使用r 在put 在 SQL
- Fix: 使用 p一个r一个meterized 查询

**H一个rd代码d 秘钥s**
- API keys 在 代码
- 数据库 密码s
- AWS 凭证s

**Uns一个fe 函数s**
- `ev一个l()`, `exec()` - 一个rbitr一个ry 代码
- No 在put v一个lid在i在
- Comm和 注入

**We一个k Cryp到gr一个phy**
- MD5, SHA1 对于 密码s
- H一个rd代码d 加密 keys
- We一个k r和om num是r gener在i在

## 验证检查清单

- [ ] No SQL 注入 vulner一个bilities
- [ ] No h一个rd代码d 秘钥s
- [ ] No uns一个fe ev一个l/exec
- [ ] Input v一个lid在i在 present
- [ ] Proper 身份认证
- [ ] Secure cryp到gr一个phy
- [ ] No 跨站脚本 vulner一个bilities
- [ ] Sensitive d在一个 加密的

## 相关技能
- **代码-re视图** - Re视图 安全 implic在i在s
- **env-v一个lid在或** - 检查 对于 exposed 秘钥s
- **日志-一个一个lyzer** - F在d 安全 事件s 在 日志s
