---
name: 环境验证器
description: "当验证环境变量时，检查配置，查找缺失变量，管理密钥。在部署前验证环境。"
license: MIT
---

# 环境验证器技能

## 概述

环境变量控制应用行为。缺失或错误的变量会导致运行时故障。在部署前必须验证。

**核心原则**: 错误的环境 = 坏掉的应用。好的环境管理应该完整、安全、一致、可验证。坏的环境管理会导致应用崩溃、安全漏洞、配置混乱。

## 何时使用

**始终:**
- 部署到任何环境之前
- 应用无法启动时
- 检查密钥泄露时
- 验证数据库连接时
- 核实API凭证时

**触发短语:**
- "检查我的环境"
- "密钥是否泄露？"
- "缺失环境变量"
- "验证配置"
- "检查数据库连接"

## 环境验证器技能功能

### 环境检查
- 必需变量验证
- 类型检查
- 格式验证
- 值范围检查
- 默认值设置
- 条件依赖验证

### 安全验证
- 密钥泄露检测
- 敏感信息扫描
- 权限检查
- 加密验证
- 访问控制
- 审计日志

### 连接测试
- 数据库连接
- API端点测试
- 外部服务验证
- 网络连通性
- 认证测试
- 超时检查

### 配置管理
- 环境差异检查
- 配置文件验证
- 版本一致性
- 变更追踪
- 回滚支持
- 文档生成

## 常见环境错误

**❌ 缺失变量**
- 必需环境变量未设置
- 配置文件路径错误
- 数据库连接信息缺失
- API密钥未配置

**❌ 类型错误**
- 端口号不是数字
- 布尔值格式错误
- 路径不存在
- URL格式不正确

**❌ 安全问题**
- 密钥硬编码在代码中
- 敏感信息打印到日志
- 弱密码策略
- 权限配置不当

**❌ 连接问题**
- 数据库无法连接
- API端点不可达
- 网络超时
- 认证失败

## 代码示例

### 环境验证器

```python
#!/usr/bin/env python3
import os
import re
import json
import yaml
import socket
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import subprocess

class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class VariableType(Enum):
    """变量类型"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    URL = "url"
    EMAIL = "email"
    PATH = "path"
    JSON = "json"
    LIST = "list"

@dataclass
class EnvironmentVariable:
    """环境变量定义"""
    name: str
    required: bool = True
    var_type: VariableType = VariableType.STRING
    default: Optional[str] = None
    description: str = ""
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    sensitive: bool = False
    depends_on: Optional[List[str]] = None

@dataclass
class ValidationIssue:
    """验证问题"""
    level: ValidationLevel
    variable: str
    message: str
    suggestion: Optional[str] = None
    details: Optional[Dict] = None

@dataclass
class ConnectionTest:
    """连接测试"""
    name: str
    test_type: str
    config: Dict[str, Any]
    timeout: int = 30
    required: bool = True

class EnvironmentValidator:
    """环境验证器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.variables: Dict[str, EnvironmentVariable] = {}
        self.connection_tests: List[ConnectionTest] = []
        self.issues: List[ValidationIssue] = []
        self.validation_rules = self._load_validation_rules()
        
        if config_file:
            self.load_config(config_file)
    
    def _load_validation_rules(self) -> Dict[str, Callable]:
        """加载验证规则"""
        return {
            VariableType.STRING: self._validate_string,
            VariableType.INTEGER: self._validate_integer,
            VariableType.BOOLEAN: self._validate_boolean,
            VariableType.URL: self._validate_url,
            VariableType.EMAIL: self._validate_email,
            VariableType.PATH: self._validate_path,
            VariableType.JSON: self._validate_json,
            VariableType.LIST: self._validate_list
        }
    
    def load_config(self, config_file: str):
        """加载配置文件"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            self.add_issue(ValidationLevel.ERROR, "config", f"配置文件不存在: {config_file}")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config = json.load(f)
                else:
                    self.add_issue(ValidationLevel.ERROR, "config", f"不支持的配置文件格式: {config_path.suffix}")
                    return
            
            # 解析环境变量定义
            for var_name, var_config in config.get('variables', {}).items():
                self.variables[var_name] = EnvironmentVariable(
                    name=var_name,
                    required=var_config.get('required', True),
                    var_type=VariableType(var_config.get('type', 'string')),
                    default=var_config.get('default'),
                    description=var_config.get('description', ''),
                    pattern=var_config.get('pattern'),
                    min_length=var_config.get('min_length'),
                    max_length=var_config.get('max_length'),
                    allowed_values=var_config.get('allowed_values'),
                    sensitive=var_config.get('sensitive', False),
                    depends_on=var_config.get('depends_on')
                )
            
            # 解析连接测试
            for test_name, test_config in config.get('connection_tests', {}).items():
                self.connection_tests.append(ConnectionTest(
                    name=test_name,
                    test_type=test_config.get('type'),
                    config=test_config.get('config', {}),
                    timeout=test_config.get('timeout', 30),
                    required=test_config.get('required', True)
                ))
        
        except Exception as e:
            self.add_issue(ValidationLevel.ERROR, "config", f"加载配置文件失败: {e}")
    
    def add_issue(self, level: ValidationLevel, variable: str, message: str, suggestion: Optional[str] = None, details: Optional[Dict] = None):
        """添加验证问题"""
        issue = ValidationIssue(
            level=level,
            variable=variable,
            message=message,
            suggestion=suggestion,
            details=details
        )
        self.issues.append(issue)
    
    def validate_environment(self) -> List[ValidationIssue]:
        """验证环境"""
        self.issues.clear()
        
        # 验证环境变量
        self._validate_variables()
        
        # 检查密钥泄露
        self._check_secret_leakage()
        
        # 执行连接测试
        self._run_connection_tests()
        
        return self.issues
    
    def _validate_variables(self):
        """验证环境变量"""
        for var_name, var_def in self.variables.items():
            value = os.getenv(var_name)
            
            # 检查必需变量
            if var_def.required and not value and not var_def.default:
                self.add_issue(
                    ValidationLevel.ERROR,
                    var_name,
                    f"必需的环境变量未设置: {var_name}",
                    f"请设置 {var_name} 环境变量"
                )
                continue
            
            # 使用默认值
            if not value and var_def.default:
                value = var_def.default
            
            if value:
                # 类型验证
                validator = self.validation_rules.get(var_def.var_type)
                if validator:
                    if not validator(value, var_def):
                        return
                
                # 自定义模式验证
                if var_def.pattern:
                    if not re.match(var_def.pattern, value):
                        self.add_issue(
                            ValidationLevel.ERROR,
                            var_name,
                            f"变量值不匹配模式: {var_def.pattern}",
                            f"确保 {var_name} 符合格式要求"
                        )
                
                # 长度验证
                if var_def.min_length and len(value) < var_def.min_length:
                    self.add_issue(
                        ValidationLevel.ERROR,
                        var_name,
                        f"变量值长度不足: 最小长度 {var_def.min_length}"
                    )
                
                if var_def.max_length and len(value) > var_def.max_length:
                    self.add_issue(
                        ValidationLevel.ERROR,
                        var_name,
                        f"变量值长度超限: 最大长度 {var_def.max_length}"
                    )
                
                # 允许值验证
                if var_def.allowed_values and value not in var_def.allowed_values:
                    self.add_issue(
                        ValidationLevel.ERROR,
                        var_name,
                        f"变量值不在允许范围内: {', '.join(var_def.allowed_values)}"
                    )
                
                # 依赖验证
                if var_def.depends_on:
                    for dep_var in var_def.depends_on:
                        if not os.getenv(dep_var):
                            self.add_issue(
                                ValidationLevel.WARNING,
                                var_name,
                                f"依赖变量未设置: {dep_var}"
                            )
    
    def _validate_string(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证字符串"""
        if not isinstance(value, str):
            self.add_issue(ValidationLevel.ERROR, var_def.name, "变量值必须是字符串")
            return False
        return True
    
    def _validate_integer(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证整数"""
        try:
            int(value)
            return True
        except ValueError:
            self.add_issue(ValidationLevel.ERROR, var_def.name, "变量值必须是整数")
            return False
    
    def _validate_boolean(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证布尔值"""
        valid_values = ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']
        if value.lower() not in valid_values:
            self.add_issue(
                ValidationLevel.ERROR,
                var_def.name,
                f"变量值必须是布尔值: {', '.join(valid_values)}"
            )
            return False
        return True
    
    def _validate_url(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(value):
            self.add_issue(ValidationLevel.ERROR, var_def.name, "变量值必须是有效的URL")
            return False
        return True
    
    def _validate_email(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证邮箱"""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(value):
            self.add_issue(ValidationLevel.ERROR, var_def.name, "变量值必须是有效的邮箱地址")
            return False
        return True
    
    def _validate_path(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证路径"""
        path = Path(value)
        if not path.exists():
            self.add_issue(
                ValidationLevel.WARNING,
                var_def.name,
                f"路径不存在: {value}",
                "请检查路径是否正确"
            )
        return True
    
    def _validate_json(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证JSON"""
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            self.add_issue(ValidationLevel.ERROR, var_def.name, "变量值必须是有效的JSON")
            return False
    
    def _validate_list(self, value: str, var_def: EnvironmentVariable) -> bool:
        """验证列表"""
        # 支持逗号分隔的列表
        items = [item.strip() for item in value.split(',')]
        if not items:
            self.add_issue(ValidationLevel.ERROR, var_def.name, "变量值不能为空列表")
            return False
        return True
    
    def _check_secret_leakage(self):
        """检查密钥泄露"""
        # 扫描代码文件中的硬编码密钥
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'aws_access_key_id\s*=\s*["\'][^"\']+["\']',
            r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        # 扫描常见代码文件
        code_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php']
        current_dir = Path('.')
        
        for ext in code_extensions:
            for file_path in current_dir.rglob(f'*{ext}'):
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in sensitive_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            self.add_issue(
                                ValidationLevel.ERROR,
                                "security",
                                f"发现硬编码敏感信息: {file_path}:{line_num}",
                                "请使用环境变量存储敏感信息"
                            )
                
                except Exception:
                    continue
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """判断是否应该忽略文件"""
        ignore_dirs = ['.git', '__pycache__', 'node_modules', '.vscode', '.idea']
        ignore_files = ['.env.example', '.env.template']
        
        # 检查目录
        for ignore_dir in ignore_dirs:
            if ignore_dir in file_path.parts:
                return True
        
        # 检查文件名
        if file_path.name in ignore_files:
            return True
        
        return False
    
    def _run_connection_tests(self):
        """执行连接测试"""
        for test in self.connection_tests:
            try:
                if test.test_type == 'database':
                    self._test_database_connection(test)
                elif test.test_type == 'api':
                    self._test_api_connection(test)
                elif test.test_type == 'tcp':
                    self._test_tcp_connection(test)
                elif test.test_type == 'http':
                    self._test_http_connection(test)
                else:
                    self.add_issue(
                        ValidationLevel.WARNING,
                        test.name,
                        f"不支持的连接测试类型: {test.test_type}"
                    )
            
            except Exception as e:
                level = ValidationLevel.ERROR if test.required else ValidationLevel.WARNING
                self.add_issue(
                    level,
                    test.name,
                    f"连接测试失败: {e}",
                    "请检查网络连接和配置"
                )
    
    def _test_database_connection(self, test: ConnectionTest):
        """测试数据库连接"""
        config = test.config
        db_type = config.get('type', 'postgresql')
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        database = config.get('database')
        username = config.get('username')
        password = config.get('password')
        
        # 简单的TCP连接测试
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(test.timeout)
        
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                self.add_issue(
                    ValidationLevel.INFO,
                    test.name,
                    f"数据库连接成功: {host}:{port}"
                )
            else:
                self.add_issue(
                    ValidationLevel.ERROR,
                    test.name,
                    f"无法连接到数据库: {host}:{port}",
                    "请检查数据库服务是否运行"
                )
        finally:
            sock.close()
    
    def _test_api_connection(self, test: ConnectionTest):
        """测试API连接"""
        config = test.config
        url = config.get('url')
        method = config.get('method', 'GET')
        headers = config.get('headers', {})
        timeout = test.timeout
        
        try:
            response = requests.request(method, url, headers=headers, timeout=timeout)
            
            if response.status_code < 400:
                self.add_issue(
                    ValidationLevel.INFO,
                    test.name,
                    f"API连接成功: {url} (状态码: {response.status_code})"
                )
            else:
                self.add_issue(
                    ValidationLevel.ERROR,
                    test.name,
                    f"API返回错误状态码: {response.status_code}",
                    "请检查API端点是否正确"
                )
        
        except requests.exceptions.RequestException as e:
            self.add_issue(
                ValidationLevel.ERROR,
                test.name,
                f"API连接失败: {e}",
                "请检查URL和网络连接"
            )
    
    def _test_tcp_connection(self, test: ConnectionTest):
        """测试TCP连接"""
        config = test.config
        host = config.get('host')
        port = config.get('port')
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(test.timeout)
        
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                self.add_issue(
                    ValidationLevel.INFO,
                    test.name,
                    f"TCP连接成功: {host}:{port}"
                )
            else:
                self.add_issue(
                    ValidationLevel.ERROR,
                    test.name,
                    f"TCP连接失败: {host}:{port}",
                    "请检查服务是否运行"
                )
        finally:
            sock.close()
    
    def _test_http_connection(self, test: ConnectionTest):
        """测试HTTP连接"""
        config = test.config
        url = config.get('url')
        timeout = test.timeout
        
        try:
            response = requests.get(url, timeout=timeout)
            
            if response.status_code < 400:
                self.add_issue(
                    ValidationLevel.INFO,
                    test.name,
                    f"HTTP连接成功: {url} (状态码: {response.status_code})"
                )
            else:
                self.add_issue(
                    ValidationLevel.WARNING,
                    test.name,
                    f"HTTP返回状态码: {response.status_code}"
                )
        
        except requests.exceptions.RequestException as e:
            self.add_issue(
                ValidationLevel.ERROR,
                test.name,
                f"HTTP连接失败: {e}"
            )
    
    def generate_report(self) -> Dict:
        """生成验证报告"""
        # 执行验证
        self.validate_environment()
        
        # 统计信息
        error_count = len([i for i in self.issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in self.issues if i.level == ValidationLevel.WARNING])
        info_count = len([i for i in self.issues if i.level == ValidationLevel.INFO])
        
        # 按级别分组
        issues_by_level = {
            ValidationLevel.ERROR: [i for i in self.issues if i.level == ValidationLevel.ERROR],
            ValidationLevel.WARNING: [i for i in self.issues if i.level == ValidationLevel.WARNING],
            ValidationLevel.INFO: [i for i in self.issues if i.level == ValidationLevel.INFO]
        }
        
        return {
            'summary': {
                'total_issues': len(self.issues),
                'error_count': error_count,
                'warning_count': warning_count,
                'info_count': info_count,
                'validation_time': datetime.now().isoformat()
            },
            'issues': [
                {
                    'level': issue.level.value,
                    'variable': issue.variable,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'details': issue.details
                }
                for issue in self.issues
            ],
            'issues_by_level': {
                level.value: [
                    {
                        'variable': issue.variable,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in issues
                ]
                for level, issues in issues_by_level.items()
            }
        }

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='环境验证器')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    parser.add_argument('--check-secrets', action='store_true', help='检查密钥泄露')
    parser.add_argument('--test-connections', action='store_true', help='测试连接')
    
    args = parser.parse_args()
    
    validator = EnvironmentValidator(args.config)
    
    try:
        report = validator.generate_report()
        
        if args.format == 'json':
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"报告已保存到: {args.output}")
            else:
                print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            print("=" * 50)
            print("环境验证报告")
            print("=" * 50)
            
            # 摘要
            summary = report['summary']
            print(f"总问题数: {summary['total_issues']}")
            print(f"错误数: {summary['error_count']}")
            print(f"警告数: {summary['warning_count']}")
            print(f"信息数: {summary['info_count']}")
            print()
            
            # 按级别显示问题
            level_names = {
                'error': '🚨 错误',
                'warning': '⚠️ 警告',
                'info': 'ℹ️ 信息'
            }
            
            for level in ['error', 'warning', 'info']:
                issues = report['issues_by_level'].get(level, [])
                if issues:
                    print(f"{level_names[level]}:")
                    for issue in issues:
                        print(f"  {issue['variable']}: {issue['message']}")
                        if issue['suggestion']:
                            print(f"    建议: {issue['suggestion']}")
                    print()
            
            # 状态总结
            if summary['error_count'] == 0:
                print("✅ 环境验证通过！")
            else:
                print(f"❌ 发现 {summary['error_count']} 个错误，需要修复")
    
    except Exception as e:
        print(f"验证失败: {e}")
        exit(1)
```

### 环境配置检查工具

```bash
#!/bin/bash
# env-checker.sh - 环境配置检查工具

set -e

# 配置
ENV_FILE=${1:-".env"}
CONFIG_FILE=${2:-"env-config.yaml"}
CHECK_SECRETS=${3:-true}
TEST_CONNECTIONS=${4:-false}
LOG_FILE="env_check.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查环境文件
check_env_file() {
    log_step "检查环境文件..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error "环境文件不存在: $ENV_FILE"
        return 1
    fi
    
    # 检查文件权限
    file_perms=$(stat -c "%a" "$ENV_FILE" 2>/dev/null || stat -f "%A" "$ENV_FILE" 2>/dev/null)
    if [ "$file_perms" != "600" ]; then
        log_warn "环境文件权限不安全: $file_perms (建议: 600)"
    fi
    
    # 检查文件编码
    if file "$ENV_FILE" | grep -q "UTF-8"; then
        log_info "文件编码正确: UTF-8"
    else
        log_warn "文件编码可能有问题"
    fi
    
    # 统计变量数量
    var_count=$(grep -c "^[A-Z_][A-Z0-9_]*=" "$ENV_FILE" 2>/dev/null || echo "0")
    log_info "发现 $var_count 个环境变量"
    
    return 0
}

# 检查必需变量
check_required_variables() {
    log_step "检查必需变量..."
    
    # 从配置文件读取必需变量列表
    if [ -f "$CONFIG_FILE" ]; then
        if command -v yq &> /dev/null; then
            required_vars=$(yq eval '.variables[] | select(.required == true) | .name' "$CONFIG_FILE" 2>/dev/null || echo "")
        elif command -v jq &> /dev/null && [[ "$CONFIG_FILE" == *.json ]]; then
            required_vars=$(jq -r '.variables[] | select(.required == true) | .name' "$CONFIG_FILE" 2>/dev/null || echo "")
        fi
    fi
    
    # 默认必需变量列表
    if [ -z "$required_vars" ]; then
        required_vars="NODE_ENV PORT DATABASE_URL"
    fi
    
    missing_vars=""
    
    for var in $required_vars; do
        if ! grep -q "^${var}=" "$ENV_FILE" 2>/dev/null; then
            if [ -z "$missing_vars" ]; then
                missing_vars="$var"
            else
                missing_vars="$missing_vars $var"
            fi
        fi
    done
    
    if [ -n "$missing_vars" ]; then
        log_error "缺失必需变量: $missing_vars"
        return 1
    else
        log_info "所有必需变量都已设置"
        return 0
    fi
}

# 检查变量格式
check_variable_format() {
    log_step "检查变量格式..."
    
    format_errors=0
    
    # 检查变量名格式
    while IFS= read -r line; do
        # 跳过注释和空行
        if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
            continue
        fi
        
        # 检查变量名格式
        if [[ "$line" =~ ^[A-Z_][A-Z0-9_]*= ]]; then
            var_name=$(echo "$line" | cut -d'=' -f1)
            var_value=$(echo "$line" | cut -d'=' -f2-)
            
            # 检查变量名长度
            if [ ${#var_name} -gt 50 ]; then
                log_warn "变量名过长: $var_name"
            fi
            
            # 检查变量值是否为空
            if [ -z "$var_value" ]; then
                log_warn "变量值为空: $var_name"
            fi
            
            # 检查特定变量格式
            case "$var_name" in
                *PORT*)
                    if ! [[ "$var_value" =~ ^[0-9]+$ ]]; then
                        log_error "端口变量格式错误: $var_name=$var_value"
                        ((format_errors++))
                    fi
                    ;;
                *URL*)
                    if ! [[ "$var_value" =~ ^https?:// ]]; then
                        log_error "URL变量格式错误: $var_name=$var_value"
                        ((format_errors++))
                    fi
                    ;;
                *EMAIL*)
                    if ! [[ "$var_value" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                        log_error "邮箱变量格式错误: $var_name=$var_value"
                        ((format_errors++))
                    fi
                    ;;
            esac
        else
            log_warn "变量格式不正确: $line"
            ((format_errors++))
        fi
    done < "$ENV_FILE"
    
    if [ $format_errors -eq 0 ]; then
        log_info "变量格式检查通过"
        return 0
    else
        log_error "发现 $format_errors 个格式错误"
        return 1
    fi
}

# 检查密钥泄露
check_secret_leakage() {
    if [ "$CHECK_SECRETS" != "true" ]; then
        return 0
    fi
    
    log_step "检查密钥泄露..."
    
    # 扫描代码文件中的硬编码密钥
    secret_patterns=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "api_key\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
        "aws_access_key_id\s*=\s*['\"][^'\"]+['\"]"
        "aws_secret_access_key\s*=\s*['\"][^'\"]+['\"]"
    )
    
    secret_count=0
    
    # 扫描常见代码文件
    for ext in py js ts java go rb php; do
        find . -name "*.$ext" -not -path "./node_modules/*" -not -path "./.git/*" -not -path "./__pycache__/*" 2>/dev/null | while read file; do
            for pattern in "${secret_patterns[@]}"; do
                if grep -iE "$pattern" "$file" > /dev/null 2>&1; then
                    log_error "发现硬编码密钥: $file"
                    ((secret_count++))
                fi
            done
        done
    done
    
    if [ $secret_count -eq 0 ]; then
        log_info "未发现密钥泄露"
        return 0
    else
        log_error "发现 $secret_count 个密钥泄露"
        return 1
    fi
}

# 测试连接
test_connections() {
    if [ "$TEST_CONNECTIONS" != "true" ]; then
        return 0
    fi
    
    log_step "测试连接..."
    
    # 测试数据库连接
    if grep -q "DATABASE_URL=" "$ENV_FILE"; then
        db_url=$(grep "DATABASE_URL=" "$ENV_FILE" | cut -d'=' -f2-)
        
        # 简单的连接测试
        if [[ "$db_url" =~ postgresql:// ]]; then
            # 提取主机和端口
            host=$(echo "$db_url" | sed -n 's/.*@\([^:]*\):.*/\1/p')
            port=$(echo "$db_url" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
            
            if [ -n "$host" ] && [ -n "$port" ]; then
                if nc -z "$host" "$port" 2>/dev/null; then
                    log_info "数据库连接成功: $host:$port"
                else
                    log_error "数据库连接失败: $host:$port"
                fi
            fi
        fi
    fi
    
    # 测试Redis连接
    if grep -q "REDIS_URL=" "$ENV_FILE"; then
        redis_url=$(grep "REDIS_URL=" "$ENV_FILE" | cut -d'=' -f2-)
        
        if [[ "$redis_url" =~ redis:// ]]; then
            host=$(echo "$redis_url" | sed -n 's/.*@\([^:]*\):.*/\1/p')
            port=$(echo "$redis_url" | sed -n 's/.*:\([0-9]*\)/\1/p')
            
            if [ -n "$host" ] && [ -n "$port" ]; then
                if nc -z "$host" "$port" 2>/dev/null; then
                    log_info "Redis连接成功: $host:$port"
                else
                    log_error "Redis连接失败: $host:$port"
                fi
            fi
        fi
    fi
    
    # 测试HTTP端点
    if grep -q "API_BASE_URL=" "$ENV_FILE"; then
        api_url=$(grep "API_BASE_URL=" "$ENV_FILE" | cut -d'=' -f2-)
        
        if command -v curl &> /dev/null; then
            if curl -s --head --request GET "$api_url" | grep -q "200 OK\|HTTP/2 200"; then
                log_info "API端点可访问: $api_url"
            else
                log_warn "API端点可能不可访问: $api_url"
            fi
        fi
    fi
}

# 生成报告
generate_report() {
    log_step "生成检查报告..."
    
    local report_file="env_check_report.md"
    
    cat > "$report_file" << EOF
# 环境检查报告

## 检查信息
- 环境文件: $ENV_FILE
- 配置文件: $CONFIG_FILE
- 检查时间: $(date)
- 密钥检查: $CHECK_SECRETS
- 连接测试: $TEST_CONNECTIONS

## 检查结果
EOF
    
    # 统计日志文件中的结果
    error_count=$(grep -c "\[ERROR\]" "$LOG_FILE" 2>/dev/null || echo "0")
    warning_count=$(grep -c "\[WARN\]" "$LOG_FILE" 2>/dev/null || echo "0")
    info_count=$(grep -c "\[INFO\]" "$LOG_FILE" 2>/dev/null || echo "0")
    
    echo "- 错误数: $error_count" >> "$report_file"
    echo "- 警告数: $warning_count" >> "$report_file"
    echo "- 信息数: $info_count" >> "$report_file"
    echo "" >> "$report_file"
    
    echo "## 详细问题" >> "$report_file"
    
    if [ $error_count -gt 0 ]; then
        echo "### 错误" >> "$report_file"
        grep "\[ERROR\]" "$LOG_FILE" | sed 's/.*\[ERROR\]/-/' >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    if [ $warning_count -gt 0 ]; then
        echo "### 警告" >> "$report_file"
        grep "\[WARN\]" "$LOG_FILE" | sed 's/.*\[WARN\]/-/' >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    echo "## 建议" >> "$report_file"
    echo "- 定期检查环境配置" >> "$report_file"
    echo "- 使用环境变量管理工具" >> "$report_file"
    echo "- 实施配置验证流程" >> "$report_file"
    echo "- 监控环境变更" >> "$report_file"
    
    log_info "检查报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始环境检查..."
    log_info "环境文件: $ENV_FILE"
    log_info "配置文件: $CONFIG_FILE"
    
    # 执行检查
    local exit_code=0
    
    check_env_file || exit_code=$?
    check_required_variables || exit_code=$?
    check_variable_format || exit_code=$?
    check_secret_leakage || exit_code=$?
    test_connections || exit_code=$?
    
    # 生成报告
    generate_report
    
    if [ $exit_code -eq 0 ]; then
        log_info "环境检查完成！"
    else
        log_error "环境检查发现问题，请查看报告"
    fi
    
    exit $exit_code
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [env_file] [config_file] [check_secrets] [test_connections]"
    echo ""
    echo "参数:"
    echo "  env_file         环境文件路径，默认: .env"
    echo "  config_file     配置文件路径，默认: env-config.yaml"
    echo "  check_secrets    是否检查密钥泄露 (true|false)，默认: true"
    echo "  test_connections 是否测试连接 (true|false)，默认: false"
    echo ""
    echo "示例:"
    echo "  $0 .env config.yaml true true"
    echo "  $0 production.env"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 密钥安全扫描器

```python
#!/usr/bin/env python3
import re
import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SecretMatch:
    """密钥匹配"""
    file_path: str
    line_number: int
    line_content: str
    secret_type: str
    confidence: str
    pattern: str

class SecretScanner:
    """密钥安全扫描器"""
    
    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path)
        self.matches: List[SecretMatch] = []
        self.secret_patterns = self._load_secret_patterns()
        self.ignore_patterns = self._load_ignore_patterns()
    
    def _load_secret_patterns(self) -> Dict[str, List[Dict]]:
        """加载密钥模式"""
        return {
            'aws_access_key': [
                {
                    'pattern': r'AKIA[0-9A-Z]{16}',
                    'confidence': 'high',
                    'description': 'AWS访问密钥ID'
                }
            ],
            'aws_secret_key': [
                {
                    'pattern': r'[A-Za-z0-9/+=]{40}',
                    'confidence': 'medium',
                    'description': 'AWS秘密访问密钥'
                }
            ],
            'github_token': [
                {
                    'pattern': r'ghp_[a-zA-Z0-9]{36}',
                    'confidence': 'high',
                    'description': 'GitHub个人访问令牌'
                },
                {
                    'pattern': r'gho_[a-zA-Z0-9]{36}',
                    'confidence': 'high',
                    'description': 'GitHub OAuth令牌'
                },
                {
                    'pattern': r'ghu_[a-zA-Z0-9]{36}',
                    'confidence': 'high',
                    'description': 'GitHub用户令牌'
                },
                {
                    'pattern': r'ghs_[a-zA-Z0-9]{36}',
                    'confidence': 'high',
                    'description': 'GitHub服务器令牌'
                },
                {
                    'pattern': r'ghr_[a-zA-Z0-9]{36}',
                    'confidence': 'high',
                    'description': 'GitHub刷新令牌'
                }
            ],
            'jwt_token': [
                {
                    'pattern': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
                    'confidence': 'medium',
                    'description': 'JWT令牌'
                }
            ],
            'api_key': [
                {
                    'pattern': r'api[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9_-]{16,}["\']?',
                    'confidence': 'medium',
                    'description': '通用API密钥'
                }
            ],
            'secret_key': [
                {
                    'pattern': r'secret[_-]?key\s*[:=]\s*["\']?[A-Za-z0-9_-]{16,}["\']?',
                    'confidence': 'medium',
                    'description': '通用密钥'
                }
            ],
            'password': [
                {
                    'pattern': r'password\s*[:=]\s*["\'][^"\']{8,}["\']',
                    'confidence': 'low',
                    'description': '密码字段'
                }
            ],
            'database_url': [
                {
                    'pattern': r'(mysql|postgresql|mongodb)://[^:]+:[^@]+@[^/]+',
                    'confidence': 'high',
                    'description': '数据库连接URL'
                }
            ],
            'private_key': [
                {
                    'pattern': r'-----BEGIN (RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY-----',
                    'confidence': 'high',
                    'description': '私钥文件'
                }
            ],
            'slack_token': [
                {
                    'pattern': r'xox[baprs]-[A-Za-z0-9-]+',
                    'confidence': 'high',
                    'description': 'Slack令牌'
                }
            ],
            'stripe_key': [
                {
                    'pattern': r'sk_live_[A-Za-z0-9]{24}',
                    'confidence': 'high',
                    'description': 'Stripe实时密钥'
                },
                {
                    'pattern': r'sk_test_[A-Za-z0-9]{24}',
                    'confidence': 'medium',
                    'description': 'Stripe测试密钥'
                }
            ]
        }
    
    def _load_ignore_patterns(self) -> List[str]:
        """加载忽略模式"""
        return [
            r'^\.git/',
            r'^node_modules/',
            r'^__pycache__/',
            r'^\.venv/',
            r'^venv/',
            r'^env/',
            r'^dist/',
            r'^build/',
            r'^target/',
            r'^\.vscode/',
            r'^\.idea/',
            r'\.min\.js$',
            r'\.bundle\.js$',
            r'\.lock$',
            r'\.log$',
            r'\.tmp$',
            r'\.env\.example$',
            r'\.env\.template$',
            r'\.env\.sample$'
        ]
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """判断是否应该忽略文件"""
        relative_path = str(file_path.relative_to(self.scan_path))
        
        # 检查忽略模式
        for pattern in self.ignore_patterns:
            if re.match(pattern, relative_path):
                return True
        
        # 检查文件大小（避免扫描大文件）
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB
                return True
        except:
            pass
        
        return False
    
    def _should_ignore_line(self, line: str) -> bool:
        """判断是否应该忽略行"""
        # 忽略注释行
        if line.strip().startswith('#') or line.strip().startswith('//'):
            return True
        
        # 忽略示例和测试代码
        if any(keyword in line.lower() for keyword in ['example', 'test', 'sample', 'demo', 'fake']):
            return True
        
        return False
    
    def scan_file(self, file_path: Path) -> List[SecretMatch]:
        """扫描单个文件"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                if self._should_ignore_line(line):
                    continue
                
                for secret_type, patterns in self.secret_patterns.items():
                    for pattern_info in patterns:
                        pattern = pattern_info['pattern']
                        confidence = pattern_info['confidence']
                        
                        # 查找匹配
                        for match in re.finditer(pattern, line, re.IGNORECASE):
                            secret_match = SecretMatch(
                                file_path=str(file_path.relative_to(self.scan_path)),
                                line_number=line_num,
                                line_content=line.strip(),
                                secret_type=secret_type,
                                confidence=confidence,
                                description=pattern_info['description']
                            )
                            matches.append(secret_match)
        
        except Exception as e:
            print(f"扫描文件失败 {file_path}: {e}")
        
        return matches
    
    def scan_directory(self) -> List[SecretMatch]:
        """扫描目录"""
        all_matches = []
        
        # 支持的文件扩展名
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php',
            '.c', '.cpp', '.h', '.cs', '.swift', '.kt', '.scala', '.rs',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            '.yml', '.yaml', '.json', '.xml', '.toml', '.ini', '.cfg',
            '.sql', '.pl', '.lua', '.r', '.m', '.dart', '.vue', '.svelte'
        }
        
        # 查找所有文件
        for file_path in self.scan_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                if not self._should_ignore_file(file_path):
                    matches = self.scan_file(file_path)
                    all_matches.extend(matches)
        
        self.matches = all_matches
        return all_matches
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成扫描报告"""
        report = []
        report.append("# 密钥安全扫描报告")
        report.append("")
        report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"扫描路径: {self.scan_path}")
        report.append("")
        
        # 统计信息
        total_matches = len(self.matches)
        high_confidence = len([m for m in self.matches if m.confidence == 'high'])
        medium_confidence = len([m for m in self.matches if m.confidence == 'medium'])
        low_confidence = len([m for m in self.matches if m.confidence == 'low'])
        
        report.append("## 扫描摘要")
        report.append(f"- 总匹配数: {total_matches}")
        report.append(f"- 高置信度: {high_confidence}")
        report.append(f"- 中置信度: {medium_confidence}")
        report.append(f"- 低置信度: {low_confidence}")
        report.append("")
        
        # 按类型分组
        matches_by_type = {}
        for match in self.matches:
            if match.secret_type not in matches_by_type:
                matches_by_type[match.secret_type] = []
            matches_by_type[match.secret_type].append(match)
        
        # 按置信度排序
        confidence_order = ['high', 'medium', 'low']
        
        if self.matches:
            report.append("## 发现的密钥")
            
            for secret_type, matches in matches_by_type.items():
                report.append(f"### {secret_type}")
                
                for match in matches:
                    confidence_icon = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(match.confidence, '⚪')
                    
                    report.append(f"{confidence_icon} **{match.file_path}:{match.line_number}**")
                    report.append(f"   置信度: {match.confidence}")
                    report.append(f"   描述: {match.description}")
                    report.append(f"   内容: `{match.line_content[:100]}...`")
                    report.append("")
        else:
            report.append("## ✅ 未发现密钥")
        
        # 建议
        report.append("## 安全建议")
        report.append("- 使用环境变量存储敏感信息")
        report.append("- 不要在代码中硬编码密钥")
        report.append("- 使用密钥管理服务")
        report.append("- 定期轮换密钥")
        report.append("- 实施代码审查流程")
        report.append("- 使用预提交钩子检查密钥")
        
        report_content = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"扫描报告已保存到: {output_file}")
        
        return report_content
    
    def scan_and_report(self, output_file: Optional[str] = None) -> str:
        """扫描并生成报告"""
        print("开始扫描密钥...")
        matches = self.scan_directory()
        print(f"扫描完成，发现 {len(matches)} 个潜在密钥")
        
        return self.generate_report(output_file)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='密钥安全扫描器')
    parser.add_argument('path', nargs='?', default='.', help='扫描路径')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--confidence', choices=['high', 'medium', 'low'], help='最低置信度')
    
    args = parser.parse_args()
    
    scanner = SecretScanner(args.path)
    
    try:
        report = scanner.scan_and_report(args.output)
        
        if not args.output:
            print(report)
        
        # 根据置信度过滤
        if args.confidence:
            confidence_levels = {'high': 3, 'medium': 2, 'low': 1}
            min_level = confidence_levels[args.confidence]
            
            filtered_matches = [
                match for match in scanner.matches
                if confidence_levels[match.confidence] >= min_level
            ]
            
            print(f"\n{args.confidence}置信度及以上的匹配: {len(filtered_matches)}")
    
    except Exception as e:
        print(f"扫描失败: {e}")
        exit(1)
```

## 最佳实践

### 环境管理
- **分离配置**: 将配置与代码分离
- **环境隔离**: 不同环境使用不同配置
- **版本控制**: 配置文件版本化管理
- **文档维护**: 维护配置文档和变更记录

### 安全措施
- **密钥管理**: 使用专门的密钥管理服务
- **访问控制**: 限制敏感信息的访问权限
- **加密存储**: 敏感配置加密存储
- **审计日志**: 记录配置变更和访问

### 验证流程
- **预部署检查**: 部署前验证环境配置
- **自动化测试**: 自动化环境验证流程
- **持续监控**: 持续监控环境状态
- **故障恢复**: 建立配置错误恢复机制

### 团队协作
- **配置规范**: 制定环境配置规范
- **权限管理**: 合理分配配置管理权限
- **培训指导**: 培训团队环境管理技能
- **知识分享**: 分享配置管理经验

## 相关技能

- [依赖分析器](./dependency-analyzer/) - 依赖安全检查
- [安全扫描器](./security-scanner/) - 代码安全分析
- [文件分析器](./file-analyzer/) - 配置文件检查
- [版本管理器](./version-manager/) - 环境版本控制

**Hardcoded secrets 在 代码**
- API keys visible 在 repository
- 数据库 passwords 在 config files
- AWS credentials 在 代码

**Missing Required variables**
- 数据库 URL not set
- API key not provided
- Configuration incomplete
- Application won't start

**Wrong Format**
- `DATABASE_URL` should 是 完整的 URI, not just host
- `PORT` should 是 number, not string
- Boolean should 是 "true"/"false" 或 "1"/"0"

**Exposed secrets 在 .gitignore**
- .env file not 在 .gitignore
- secrets committed 到 git history
- Hard 到 remove once committed

## 验证检查清单

- [ ] All required variables present
- [ ] 变量 formats correct
- [ ] No hardcoded secrets 在 代码
- [ ] .env not 在 版本 control
- [ ] .env.example 作为 template (no values)
- [ ] Application starts without errors
- [ ] 数据库 connection works
- [ ] API credentials 是 valid
- [ ] No sensitive data 在 logs

## 相关技能
- **security-scanner** - 检查 对于 hardcoded secrets
- **file-analyzer** - Verify .env file not committed
- **api-tester** - 测试 API connections 与 env vars
