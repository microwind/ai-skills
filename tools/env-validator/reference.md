# 环境变量验证器参考文档

## 环境变量验证器概述

### 什么是环境变量验证器
环境变量验证器是一个专门用于验证和管理应用程序环境变量的工具。该工具支持多种变量类型、验证规则、环境配置和错误处理，提供完整的变量定义、验证、报告和集成功能，帮助开发团队确保环境配置的正确性、安全性和一致性。

### 主要功能
- **变量定义**: 支持多种变量类型和约束定义
- **验证规则**: 提供基础验证、业务验证和安全验证
- **环境管理**: 支持多环境配置和环境特定验证
- **错误处理**: 完善的错误分类、处理和通知机制
- **报告生成**: 生成详细的验证报告和修复建议
- **集成能力**: 与CI/CD流程和应用框架无缝集成

## 环境变量验证引擎

### 验证器核心
```python
# env_validator.py
import os
import re
import json
import yaml
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime

class VariableType(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    EMAIL = "email"
    URL = "url"
    IP = "ip"
    JSON = "json"

class ValidationLevel(Enum):
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ValidationRule:
    name: str
    validator: Callable[[Any], bool]
    message: str
    level: ValidationLevel = ValidationLevel.ERROR
    enabled: bool = True

@dataclass
class VariableConstraint:
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    forbidden_values: Optional[List[Any]] = None
    required: bool = True

@dataclass
class EnvironmentVariable:
    name: str
    var_type: VariableType
    description: str = ""
    default_value: Optional[str] = None
    constraint: Optional[VariableConstraint] = None
    validation_rules: List[ValidationRule] = field(default_factory=list)
    environments: List[EnvironmentType] = field(default_factory=list)
    is_sensitive: bool = False

@dataclass
class ValidationResult:
    variable_name: str
    is_valid: bool
    value: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

@dataclass
class ValidationReport:
    total_variables: int
    valid_variables: int
    invalid_variables: int
    warnings_count: int
    errors_count: int
    fatal_count: int
    results: List[ValidationResult]
    execution_time: float
    timestamp: datetime
    environment: EnvironmentType

class EnvironmentValidator:
    def __init__(self):
        self.variables: Dict[str, EnvironmentVariable] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self._register_builtin_validators()
    
    def _register_builtin_validators(self):
        """注册内置验证器"""
        self.custom_validators.update({
            'email': self._validate_email,
            'url': self._validate_url,
            'ip': self._validate_ip,
            'json': self._validate_json,
            'port': self._validate_port,
            'database_url': self._validate_database_url
        })
    
    def add_variable(self, variable: EnvironmentVariable):
        """添加环境变量定义"""
        self.variables[variable.name] = variable
        self.logger.info(f"添加环境变量: {variable.name}")
    
    def remove_variable(self, variable_name: str):
        """移除环境变量定义"""
        if variable_name in self.variables:
            del self.variables[variable_name]
            self.logger.info(f"移除环境变量: {variable_name}")
    
    def add_custom_validator(self, name: str, validator: Callable[[Any], bool]):
        """添加自定义验证器"""
        self.custom_validators[name] = validator
        self.logger.info(f"添加自定义验证器: {name}")
    
    def validate_environment(self, environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
                           env_vars: Optional[Dict[str, str]] = None) -> ValidationReport:
        """验证环境变量"""
        start_time = datetime.now()
        
        if env_vars is None:
            env_vars = dict(os.environ)
        
        results = []
        
        for var_name, variable in self.variables.items():
            # 检查变量是否适用于当前环境
            if variable.environments and environment not in variable.environments:
                continue
            
            result = self._validate_variable(variable, env_vars, environment)
            results.append(result)
        
        # 统计结果
        total_vars = len(results)
        valid_vars = sum(1 for r in results if r.is_valid)
        invalid_vars = total_vars - valid_vars
        warnings_count = sum(len(r.warnings) for r in results)
        errors_count = sum(len(r.errors) for r in results)
        fatal_count = sum(1 for r in results if any("FATAL" in error for error in r.errors))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        report = ValidationReport(
            total_variables=total_vars,
            valid_variables=valid_vars,
            invalid_variables=invalid_vars,
            warnings_count=warnings_count,
            errors_count=errors_count,
            fatal_count=fatal_count,
            results=results,
            execution_time=execution_time,
            timestamp=start_time,
            environment=environment
        )
        
        self.logger.info(f"环境验证完成: {valid_vars}/{total_vars} 通过, 耗时 {execution_time:.2f}s")
        return report
    
    def _validate_variable(self, variable: EnvironmentVariable, 
                          env_vars: Dict[str, str], 
                          environment: EnvironmentType) -> ValidationResult:
        """验证单个变量"""
        result = ValidationResult(variable_name=variable.name, is_valid=True)
        
        # 获取变量值
        value = env_vars.get(variable.name, variable.default_value)
        
        if value is None:
            if variable.constraint and variable.constraint.required:
                result.errors.append(f"必需的环境变量 '{variable.name}' 未设置")
                result.is_valid = False
            return result
        
        result.value = value
        
        # 类型验证
        type_error = self._validate_type(value, variable.var_type)
        if type_error:
            result.errors.append(type_error)
            result.is_valid = False
        
        # 约束验证
        if variable.constraint:
            constraint_errors = self._validate_constraints(value, variable.constraint)
            result.errors.extend(constraint_errors)
            if constraint_errors:
                result.is_valid = False
        
        # 自定义验证规则
        for rule in variable.validation_rules:
            if not rule.enabled:
                continue
            
            try:
                if rule.validator(value):
                    if rule.level == ValidationLevel.INFO:
                        result.info.append(rule.message)
                    elif rule.level == ValidationLevel.WARNING:
                        result.warnings.append(rule.message)
                else:
                    if rule.level == ValidationLevel.FATAL:
                        result.errors.append(f"[FATAL] {rule.message}")
                        result.is_valid = False
                    elif rule.level == ValidationLevel.ERROR:
                        result.errors.append(rule.message)
                        result.is_valid = False
                    elif rule.level == ValidationLevel.WARNING:
                        result.warnings.append(rule.message)
                    elif rule.level == ValidationLevel.INFO:
                        result.info.append(rule.message)
            except Exception as e:
                result.errors.append(f"验证器 '{rule.name}' 执行失败: {e}")
                result.is_valid = False
        
        return result
    
    def _validate_type(self, value: str, var_type: VariableType) -> Optional[str]:
        """验证变量类型"""
        try:
            if var_type == VariableType.STRING:
                return None  # 字符串总是有效的
            elif var_type == VariableType.NUMBER:
                float(value)
            elif var_type == VariableType.BOOLEAN:
                if value.lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']:
                    return f"值 '{value}' 不是有效的布尔值"
            elif var_type == VariableType.ARRAY:
                json.loads(value)  # 验证是否为有效的JSON数组
            elif var_type == VariableType.OBJECT:
                json.loads(value)  # 验证是否为有效的JSON对象
            elif var_type in [VariableType.EMAIL, VariableType.URL, VariableType.IP, VariableType.JSON]:
                validator_name = var_type.value
                if validator_name in self.custom_validators:
                    if not self.custom_validators[validator_name](value):
                        return f"值 '{value}' 不是有效的{var_type.value}"
            return None
        except (ValueError, json.JSONDecodeError) as e:
            return f"值 '{value}' 不是有效的{var_type.value}: {e}"
    
    def _validate_constraints(self, value: str, constraint: VariableConstraint) -> List[str]:
        """验证约束条件"""
        errors = []
        
        # 长度约束
        if constraint.min_length is not None and len(value) < constraint.min_length:
            errors.append(f"值长度 {len(value)} 小于最小长度 {constraint.min_length}")
        
        if constraint.max_length is not None and len(value) > constraint.max_length:
            errors.append(f"值长度 {len(value)} 大于最大长度 {constraint.max_length}")
        
        # 数值约束
        if constraint.min_value is not None or constraint.max_value is not None:
            try:
                num_value = float(value)
                if constraint.min_value is not None and num_value < constraint.min_value:
                    errors.append(f"值 {num_value} 小于最小值 {constraint.min_value}")
                if constraint.max_value is not None and num_value > constraint.max_value:
                    errors.append(f"值 {num_value} 大于最大值 {constraint.max_value}")
            except ValueError:
                pass  # 类型错误已在类型验证中处理
        
        # 正则表达式约束
        if constraint.pattern:
            if not re.match(constraint.pattern, value):
                errors.append(f"值 '{value}' 不匹配模式 '{constraint.pattern}'")
        
        # 允许值约束
        if constraint.allowed_values and value not in constraint.allowed_values:
            errors.append(f"值 '{value}' 不在允许的值列表中: {constraint.allowed_values}")
        
        # 禁止值约束
        if constraint.forbidden_values and value in constraint.forbidden_values:
            errors.append(f"值 '{value}' 在禁止的值列表中: {constraint.forbidden_values}")
        
        return errors
    
    def _validate_email(self, value: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, value) is not None
    
    def _validate_url(self, value: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        return re.match(pattern, value) is not None
    
    def _validate_ip(self, value: str) -> bool:
        """验证IP地址格式"""
        import ipaddress
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    
    def _validate_json(self, value: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
    
    def _validate_port(self, value: str) -> bool:
        """验证端口号"""
        try:
            port = int(value)
            return 1 <= port <= 65535
        except ValueError:
            return False
    
    def _validate_database_url(self, value: str) -> bool:
        """验证数据库URL格式"""
        pattern = r'^[a-zA-Z]+://[a-zA-Z0-9:_-]+@[a-zA-Z0-9.-]+:[0-9]+/[a-zA-Z0-9_-]+$'
        return re.match(pattern, value) is not None
    
    def load_config_from_file(self, config_path: str):
        """从文件加载配置"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                config = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
        
        # 解析配置
        self._parse_config(config)
        self.logger.info(f"配置文件已加载: {config_path}")
    
    def _parse_config(self, config: Dict[str, Any]):
        """解析配置"""
        variables_config = config.get('variables', {})
        
        for var_name, var_config in variables_config.items():
            # 解析变量类型
            var_type_str = var_config.get('type', 'string')
            var_type = VariableType(var_type_str)
            
            # 解析约束
            constraint_config = var_config.get('constraint', {})
            constraint = VariableConstraint(
                min_length=constraint_config.get('min_length'),
                max_length=constraint_config.get('max_length'),
                min_value=constraint_config.get('min_value'),
                max_value=constraint_config.get('max_value'),
                pattern=constraint_config.get('pattern'),
                allowed_values=constraint_config.get('allowed_values'),
                forbidden_values=constraint_config.get('forbidden_values'),
                required=constraint_config.get('required', True)
            )
            
            # 解析验证规则
            validation_rules = []
            rules_config = var_config.get('validation_rules', [])
            for rule_config in rules_config:
                rule_name = rule_config.get('name')
                if rule_name in self.custom_validators:
                    rule = ValidationRule(
                        name=rule_name,
                        validator=self.custom_validators[rule_name],
                        message=rule_config.get('message', f'{rule_name}验证失败'),
                        level=ValidationLevel(rule_config.get('level', 'error')),
                        enabled=rule_config.get('enabled', True)
                    )
                    validation_rules.append(rule)
            
            # 解析环境
            environments = []
            env_config = var_config.get('environments', [])
            for env_str in env_config:
                environments.append(EnvironmentType(env_str))
            
            # 创建变量
            variable = EnvironmentVariable(
                name=var_name,
                var_type=var_type,
                description=var_config.get('description', ''),
                default_value=var_config.get('default_value'),
                constraint=constraint,
                validation_rules=validation_rules,
                environments=environments,
                is_sensitive=var_config.get('is_sensitive', False)
            )
            
            self.add_variable(variable)
    
    def generate_report(self, report: ValidationReport, output_format: str = "json") -> str:
        """生成验证报告"""
        if output_format.lower() == "json":
            return self._generate_json_report(report)
        elif output_format.lower() == "html":
            return self._generate_html_report(report)
        elif output_format.lower() == "markdown":
            return self._generate_markdown_report(report)
        else:
            raise ValueError(f"不支持的报告格式: {output_format}")
    
    def _generate_json_report(self, report: ValidationReport) -> str:
        """生成JSON报告"""
        report_data = {
            'summary': {
                'total_variables': report.total_variables,
                'valid_variables': report.valid_variables,
                'invalid_variables': report.invalid_variables,
                'warnings_count': report.warnings_count,
                'errors_count': report.errors_count,
                'fatal_count': report.fatal_count,
                'execution_time': report.execution_time,
                'timestamp': report.timestamp.isoformat(),
                'environment': report.environment.value
            },
            'results': []
        }
        
        for result in report.results:
            result_data = {
                'variable_name': result.variable_name,
                'is_valid': result.is_valid,
                'value': result.value,
                'errors': result.errors,
                'warnings': result.warnings,
                'info': result.info
            }
            report_data['results'].append(result_data)
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self, report: ValidationReport) -> str:
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>环境变量验证报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .warning { color: #ffc107; }
        .info { color: #17a2b8; }
        .variable { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .valid { border-left: 5px solid #28a745; }
        .invalid { border-left: 5px solid #dc3545; }
        .code { background-color: #f5f5f5; padding: 10px; font-family: monospace; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>环境变量验证报告</h1>
        <p>环境: {environment}</p>
        <p>验证时间: {timestamp}</p>
        <p>执行时间: {execution_time:.2f}秒</p>
    </div>
    
    <div class="summary">
        <h2>验证摘要</h2>
        <p>总变量数: <span class="info">{total_variables}</span></p>
        <p>有效变量: <span class="success">{valid_variables}</span></p>
        <p>无效变量: <span class="error">{invalid_variables}</span></p>
        <p>警告数: <span class="warning">{warnings_count}</span></p>
        <p>错误数: <span class="error">{errors_count}</span></p>
        <p>致命错误: <span class="error">{fatal_count}</span></p>
    </div>
    
    <div class="variables">
        <h2>变量详情</h2>
        {variable_list}
    </div>
</body>
</html>
        """
        
        variable_html = ""
        for result in report.results:
            css_class = "valid" if result.is_valid else "invalid"
            
            errors_html = ""
            if result.errors:
                errors_html = "<h4>错误:</h4><ul>"
                for error in result.errors:
                    errors_html += f"<li class='error'>{error}</li>"
                errors_html += "</ul>"
            
            warnings_html = ""
            if result.warnings:
                warnings_html = "<h4>警告:</h4><ul>"
                for warning in result.warnings:
                    warnings_html += f"<li class='warning'>{warning}</li>"
                warnings_html += "</ul>"
            
            info_html = ""
            if result.info:
                info_html = "<h4>信息:</h4><ul>"
                for info_item in result.info:
                    info_html += f"<li class='info'>{info_item}</li>"
                info_html += "</ul>"
            
            variable_html += f"""
        <div class="variable {css_class}">
            <h3>{result.variable_name}</h3>
            <p><strong>状态:</strong> {'通过' if result.is_valid else '失败'}</p>
            <p><strong>值:</strong> <span class="code">{result.value or '未设置'}</span></p>
            {errors_html}
            {warnings_html}
            {info_html}
        </div>
            """
        
        return html_template.format(
            environment=report.environment.value,
            timestamp=report.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            execution_time=report.execution_time,
            total_variables=report.total_variables,
            valid_variables=report.valid_variables,
            invalid_variables=report.invalid_variables,
            warnings_count=report.warnings_count,
            errors_count=report.errors_count,
            fatal_count=report.fatal_count,
            variable_list=variable_html
        )
    
    def _generate_markdown_report(self, report: ValidationReport) -> str:
        """生成Markdown报告"""
        lines = [
            "# 环境变量验证报告",
            "",
            f"**环境**: {report.environment.value}",
            f"**验证时间**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**执行时间**: {report.execution_time:.2f}秒",
            "",
            "## 验证摘要",
            "",
            f"- 总变量数: {report.total_variables}",
            f"- 有效变量: {report.valid_variables}",
            f"- 无效变量: {report.invalid_variables}",
            f"- 警告数: {report.warnings_count}",
            f"- 错误数: {report.errors_count}",
            f"- 致命错误: {report.fatal_count}",
            "",
            "## 变量详情",
            ""
        ]
        
        for result in report.results:
            status = "✅ 通过" if result.is_valid else "❌ 失败"
            lines.extend([
                f"### {result.variable_name}",
                "",
                f"**状态**: {status}",
                f"**值**: `{result.value or '未设置'}`",
                ""
            ])
            
            if result.errors:
                lines.append("**错误**:")
                for error in result.errors:
                    lines.append(f"- ❌ {error}")
                lines.append("")
            
            if result.warnings:
                lines.append("**警告**:")
                for warning in result.warnings:
                    lines.append(f"- ⚠️ {warning}")
                lines.append("")
            
            if result.info:
                lines.append("**信息**:")
                for info_item in result.info:
                    lines.append(f"- ℹ️ {info_item}")
                lines.append("")
        
        return "\n".join(lines)

# 使用示例
validator = EnvironmentValidator()

# 添加环境变量定义
db_url_var = EnvironmentVariable(
    name="DATABASE_URL",
    var_type=VariableType.STRING,
    description="数据库连接URL",
    constraint=VariableConstraint(
        required=True,
        pattern=r'^[a-zA-Z]+://[a-zA-Z0-9:_-]+@[a-zA-Z0-9.-]+:[0-9]+/[a-zA-Z0-9_-]+$'
    ),
    validation_rules=[
        ValidationRule(
            name="database_url",
            validator=validator._validate_database_url,
            message="无效的数据库URL格式"
        )
    ],
    environments=[EnvironmentType.DEVELOPMENT, EnvironmentType.PRODUCTION]
)

debug_var = EnvironmentVariable(
    name="DEBUG",
    var_type=VariableType.BOOLEAN,
    description="调试模式开关",
    default_value="false",
    environments=[EnvironmentType.DEVELOPMENT]
)

port_var = EnvironmentVariable(
    name="PORT",
    var_type=VariableType.NUMBER,
    description="服务端口",
    default_value="8000",
    constraint=VariableConstraint(
        required=False,
        min_value=1,
        max_value=65535
    )
)

validator.add_variable(db_url_var)
validator.add_variable(debug_var)
validator.add_variable(port_var)

# 从配置文件加载
# validator.load_config_from_file("env_config.yaml")

# 验证环境
report = validator.validate_environment(EnvironmentType.DEVELOPMENT)

# 生成报告
json_report = validator.generate_report(report, "json")
html_report = validator.generate_report(report, "html")
markdown_report = validator.generate_report(report, "markdown")

# 保存报告
with open("env_validation_report.json", "w", encoding="utf-8") as f:
    f.write(json_report)

with open("env_validation_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)

with open("env_validation_report.md", "w", encoding="utf-8") as f:
    f.write(markdown_report)

print(f"验证完成: {report.valid_variables}/{report.total_variables} 通过")
print(f"错误数: {report.errors_count}")
print(f"警告数: {report.warnings_count}")
```

## 配置管理器

### 多环境配置管理
```python
# config_manager.py
import os
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging

class ConfigFormat(Enum):
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    TOML = "toml"

@dataclass
class ConfigSource:
    name: str
    path: str
    format: ConfigFormat
    priority: int = 0
    required: bool = True
    environment_specific: bool = False

class ConfigManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_sources: List[ConfigSource] = []
        self.merged_config: Dict[str, Any] = {}
        self.environment_overrides: Dict[str, Dict[str, Any]] = {}
    
    def add_config_source(self, source: ConfigSource):
        """添加配置源"""
        self.config_sources.append(source)
        self.config_sources.sort(key=lambda x: x.priority, reverse=True)
        self.logger.info(f"添加配置源: {source.name} (优先级: {source.priority})")
    
    def remove_config_source(self, source_name: str):
        """移除配置源"""
        self.config_sources = [s for s in self.config_sources if s.name != source_name]
        self.logger.info(f"移除配置源: {source_name}")
    
    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """加载配置"""
        self.merged_config = {}
        
        # 按优先级加载配置源
        for source in self.config_sources:
            if source.environment_specific and environment:
                # 环境特定配置
                env_config = self._load_environment_config(source, environment)
                if env_config:
                    self._merge_config(self.merged_config, env_config)
            else:
                # 通用配置
                config = self._load_config_file(source)
                if config:
                    self._merge_config(self.merged_config, config)
        
        # 应用环境变量覆盖
        env_overrides = self._load_environment_overrides()
        if env_overrides:
            self._merge_config(self.merged_config, env_overrides)
        
        self.logger.info(f"配置加载完成，共 {len(self.merged_config)} 个配置项")
        return self.merged_config
    
    def _load_config_file(self, source: ConfigSource) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        config_path = Path(source.path)
        
        if not config_path.exists():
            if source.required:
                raise FileNotFoundError(f"必需的配置文件不存在: {source.path}")
            else:
                self.logger.warning(f"可选配置文件不存在: {source.path}")
                return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if source.format == ConfigFormat.JSON:
                    config = json.load(f)
                elif source.format == ConfigFormat.YAML:
                    config = yaml.safe_load(f)
                elif source.format == ConfigFormat.ENV:
                    config = self._parse_env_file(f)
                elif source.format == ConfigFormat.TOML:
                    try:
                        import toml
                        config = toml.load(f)
                    except ImportError:
                        self.logger.error("TOML格式需要安装toml库")
                        return None
                else:
                    raise ValueError(f"不支持的配置格式: {source.format}")
            
            self.logger.debug(f"加载配置文件: {source.path}")
            return config
        
        except Exception as e:
            if source.required:
                raise
            else:
                self.logger.error(f"加载配置文件失败 {source.path}: {e}")
                return None
    
    def _load_environment_config(self, source: ConfigSource, environment: str) -> Optional[Dict[str, Any]]:
        """加载环境特定配置"""
        config_path = Path(source.path)
        
        # 构建环境特定文件路径
        if config_path.suffix:
            env_path = config_path.with_name(f"{config_path.stem}.{environment}{config_path.suffix}")
        else:
            env_path = config_path.with_name(f"{config_path.name}.{environment}")
        
        if not env_path.exists():
            self.logger.debug(f"环境配置文件不存在: {env_path}")
            return None
        
        # 创建临时配置源
        env_source = ConfigSource(
            name=f"{source.name}.{environment}",
            path=str(env_path),
            format=source.format,
            priority=source.priority,
            required=False,
            environment_specific=True
        )
        
        return self._load_config_file(env_source)
    
    def _parse_env_file(self, file) -> Dict[str, Any]:
        """解析.env文件"""
        config = {}
        
        for line in file:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # 移除引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                config[key] = value
        
        return config
    
    def _load_environment_overrides(self) -> Dict[str, Any]:
        """加载环境变量覆盖"""
        overrides = {}
        
        # 查找所有以APP_或CONFIG_开头的环境变量
        for key, value in os.environ.items():
            if key.startswith(('APP_', 'CONFIG_')):
                config_key = key[4:] if key.startswith('APP_') else key[7:]
                # 转换为嵌套字典结构
                self._set_nested_value(overrides, config_key.lower().split('_'), value)
        
        return overrides
    
    def _set_nested_value(self, config: Dict[str, Any], keys: List[str], value: str):
        """设置嵌套值"""
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """深度合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        current = self.merged_config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def set_config_value(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        current = self.merged_config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def validate_config(self, schema: Dict[str, Any]) -> List[str]:
        """验证配置"""
        errors = []
        
        for key, rules in schema.items():
            value = self.get_config_value(key)
            
            # 必需检查
            if rules.get('required', False) and value is None:
                errors.append(f"配置项 '{key}' 是必需的")
                continue
            
            if value is not None:
                # 类型检查
                expected_type = rules.get('type')
                if expected_type and not isinstance(value, expected_type):
                    errors.append(f"配置项 '{key}' 类型错误，期望 {expected_type.__name__}")
                
                # 值范围检查
                min_value = rules.get('min')
                max_value = rules.get('max')
                if isinstance(value, (int, float)):
                    if min_value is not None and value < min_value:
                        errors.append(f"配置项 '{key}' 值 {value} 小于最小值 {min_value}")
                    if max_value is not None and value > max_value:
                        errors.append(f"配置项 '{key}' 值 {value} 大于最大值 {max_value}")
                
                # 允许值检查
                allowed_values = rules.get('allowed_values')
                if allowed_values and value not in allowed_values:
                    errors.append(f"配置项 '{key}' 值 {value} 不在允许的值列表中: {allowed_values}")
        
        return errors
    
    def export_config(self, output_path: str, format: ConfigFormat = ConfigFormat.YAML):
        """导出配置"""
        output_file = Path(output_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if format == ConfigFormat.JSON:
                json.dump(self.merged_config, f, indent=2, ensure_ascii=False)
            elif format == ConfigFormat.YAML:
                yaml.dump(self.merged_config, f, default_flow_style=False, allow_unicode=True)
            elif format == ConfigFormat.ENV:
                self._export_as_env(f)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
        
        self.logger.info(f"配置已导出到: {output_path}")
    
    def _export_as_env(self, file):
        """导出为.env格式"""
        for key, value in self._flatten_config(self.merged_config).items():
            file.write(f"{key.upper()}={value}\n")
    
    def _flatten_config(self, config: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """扁平化配置"""
        flattened = {}
        
        for key, value in config.items():
            new_key = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_config(value, new_key))
            else:
                flattened[new_key] = str(value)
        
        return flattened

# 使用示例
config_manager = ConfigManager()

# 添加配置源
config_manager.add_config_source(ConfigSource(
    name="default",
    path="config/default.yaml",
    format=ConfigFormat.YAML,
    priority=1
))

config_manager.add_config_source(ConfigSource(
    name="environment",
    path="config/config.yaml",
    format=ConfigFormat.YAML,
    priority=2,
    environment_specific=True
))

config_manager.add_config_source(ConfigSource(
    name="local",
    path=".env.local",
    format=ConfigFormat.ENV,
    priority=3,
    required=False
))

# 加载配置
config = config_manager.load_config("development")

# 获取配置值
database_url = config_manager.get_config_value("database.url", "sqlite:///app.db")
debug_mode = config_manager.get_config_value("debug", False)
port = config_manager.get_config_value("server.port", 8000)

print(f"数据库URL: {database_url}")
print(f"调试模式: {debug_mode}")
print(f"服务端口: {port}")

# 验证配置
schema = {
    "database.url": {"required": True, "type": str},
    "debug": {"required": False, "type": bool},
    "server.port": {"required": False, "type": int, "min": 1, "max": 65535}
}

errors = config_manager.validate_config(schema)
if errors:
    print("配置验证错误:")
    for error in errors:
        print(f"  - {error}")
else:
    print("配置验证通过")

# 导出配置
config_manager.export_config("exported_config.yaml", ConfigFormat.YAML)
```

## 参考资源

### 环境变量管理
- [Twelve-Factor App - Config](https://12factor.net/config)
- [Docker Environment Variables](https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file)
- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)

### 配置管理
- [Spring Boot Configuration](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config)
- [Django Settings](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Node.js Environment Variables](https://nodejs.dev/learn/how-to-use-environment-variables)

### 验证工具
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [JSON Schema](https://json-schema.org/)
- [Cerberus](https://docs.python-cerberus.org/en/stable/)

### 安全最佳实践
- [Environment Variable Security](https://snyk.io/blog/10-best-practices-to-containerize-and-use-environment-variables/)
- [Secrets Management](https://kubernetes.io/docs/concepts/configuration/secret/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
