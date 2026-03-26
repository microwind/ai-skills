# API契约验证器参考文档

## API契约验证器概述

### 什么是API契约验证器
API契约验证器是一种用于验证API接口规范与实际实现一致性的工具。它通过解析OpenAPI、Swagger、GraphQL等API规范文档，对API接口的定义、数据模型、响应格式等进行全面验证，确保API的设计与实现保持一致。API契约验证器支持多种规范格式，提供灵活的验证规则配置，能够帮助开发团队在API开发过程中及早发现和修复问题，提高API质量和开发效率。

### 主要功能
- **规范解析**: 支持OpenAPI 3.0/3.1、Swagger 2.0、GraphQL SDL等多种API规范格式
- **结构验证**: 验证API接口的结构完整性，包括必填字段、数据类型、格式规范等
- **业务规则验证**: 支持自定义业务规则验证，满足特定业务场景的验证需求
- **安全验证**: 检测API中的安全问题和敏感信息泄露风险
- **CI/CD集成**: 与主流CI/CD工具集成，实现自动化验证和质量门禁
- **IDE集成**: 提供IDE插件支持，实现实时验证和代码辅助功能
- **监控报告**: 提供详细的验证报告和监控指标，支持趋势分析

## API契约验证器核心

### 规范解析器
```python
# api_contract_validator.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import datetime
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import math
import requests
import jsonschema
from pydantic import BaseModel, ValidationError
import jinja2
import markdown
import xml.etree.ElementTree as ET

class SpecificationType(Enum):
    """规范类型枚举"""
    OPENAPI_30 = "openapi_3.0"
    OPENAPI_31 = "openapi_3.1"
    SWAGGER_20 = "swagger_2.0"
    GRAPHQL_SDL = "graphql_sdl"
    CUSTOM = "custom"

class ValidationLevel(Enum):
    """验证级别枚举"""
    STRICT = "strict"
    LENIENT = "lenient"
    WARNING = "warning"
    CUSTOM = "custom"

class ErrorLevel(Enum):
    """错误级别枚举"""
    FATAL = "fatal"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"

@dataclass
class ValidationResult:
    """验证结果"""
    result_id: str
    specification_path: str
    validation_time: datetime
    total_errors: int
    total_warnings: int
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    execution_time: float = 0.0

@dataclass
class ValidationRule:
    """验证规则"""
    rule_id: str
    name: str
    description: str
    level: ErrorLevel
    condition: str
    message: str
    enabled: bool = True

@dataclass
class APISpecification:
    """API规范"""
    spec_id: str
    spec_type: SpecificationType
    version: str
    title: str
    description: str
    content: Dict[str, Any]
    file_path: str
    last_modified: datetime

class SpecificationParser:
    """规范解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.parsers = {
            SpecificationType.OPENAPI_30: self._parse_openapi30,
            SpecificationType.OPENAPI_31: self._parse_openapi31,
            SpecificationType.SWAGGER_20: self._parse_swagger20,
            SpecificationType.GRAPHQL_SDL: self._parse_graphql_sdl,
            SpecificationType.CUSTOM: self._parse_custom
        }
    
    def parse_specification(self, file_path: str, spec_type: Optional[SpecificationType] = None) -> APISpecification:
        """解析API规范"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检测规范类型
            if spec_type is None:
                spec_type = self._detect_specification_type(content, file_path)
            
            # 解析规范内容
            parsed_content = self._parse_content(content, spec_type)
            
            # 提取基本信息
            title = parsed_content.get('info', {}).get('title', 'Unknown API')
            description = parsed_content.get('info', {}).get('description', '')
            version = parsed_content.get('info', {}).get('version', '1.0.0')
            
            # 获取文件修改时间
            file_stat = os.stat(file_path)
            last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            
            # 创建规范对象
            specification = APISpecification(
                spec_id=str(uuid.uuid4()),
                spec_type=spec_type,
                version=version,
                title=title,
                description=description,
                content=parsed_content,
                file_path=file_path,
                last_modified=last_modified
            )
            
            self.logger.info(f"规范解析成功: {file_path}")
            
            return specification
        
        except Exception as e:
            self.logger.error(f"规范解析失败: {file_path}, {e}")
            raise
    
    def _detect_specification_type(self, content: str, file_path: str) -> SpecificationType:
        """检测规范类型"""
        try:
            # 尝试解析为JSON
            if content.strip().startswith('{'):
                data = json.loads(content)
                
                # OpenAPI 3.0/3.1
                if 'openapi' in data:
                    version = data.get('openapi', '')
                    if version.startswith('3.0'):
                        return SpecificationType.OPENAPI_30
                    elif version.startswith('3.1'):
                        return SpecificationType.OPENAPI_31
                
                # Swagger 2.0
                elif 'swagger' in data:
                    return SpecificationType.SWAGGER_20
            
            # 尝试解析为YAML
            elif content.strip().startswith(('openapi:', 'swagger:', 'type:')):
                data = yaml.safe_load(content)
                
                if 'openapi' in data:
                    version = data.get('openapi', '')
                    if version.startswith('3.0'):
                        return SpecificationType.OPENAPI_30
                    elif version.startswith('3.1'):
                        return SpecificationType.OPENAPI_31
                
                elif 'swagger' in data:
                    return SpecificationType.SWAGGER_20
            
            # GraphQL SDL
            elif 'type' in content or 'schema' in content:
                return SpecificationType.GRAPHQL_SDL
            
            # 默认为自定义类型
            return SpecificationType.CUSTOM
        
        except Exception as e:
            self.logger.error(f"检测规范类型失败: {e}")
            return SpecificationType.CUSTOM
    
    def _parse_content(self, content: str, spec_type: SpecificationType) -> Dict[str, Any]:
        """解析规范内容"""
        try:
            parser = self.parsers.get(spec_type)
            if parser:
                return parser(content)
            else:
                raise ValueError(f"不支持的规范类型: {spec_type}")
        
        except Exception as e:
            self.logger.error(f"解析规范内容失败: {e}")
            raise
    
    def _parse_openapi30(self, content: str) -> Dict[str, Any]:
        """解析OpenAPI 3.0规范"""
        try:
            if content.strip().startswith('{'):
                return json.loads(content)
            else:
                return yaml.safe_load(content)
        
        except Exception as e:
            self.logger.error(f"解析OpenAPI 3.0规范失败: {e}")
            raise
    
    def _parse_openapi31(self, content: str) -> Dict[str, Any]:
        """解析OpenAPI 3.1规范"""
        try:
            if content.strip().startswith('{'):
                return json.loads(content)
            else:
                return yaml.safe_load(content)
        
        except Exception as e:
            self.logger.error(f"解析OpenAPI 3.1规范失败: {e}")
            raise
    
    def _parse_swagger20(self, content: str) -> Dict[str, Any]:
        """解析Swagger 2.0规范"""
        try:
            if content.strip().startswith('{'):
                return json.loads(content)
            else:
                return yaml.safe_load(content)
        
        except Exception as e:
            self.logger.error(f"解析Swagger 2.0规范失败: {e}")
            raise
    
    def _parse_graphql_sdl(self, content: str) -> Dict[str, Any]:
        """解析GraphQL SDL规范"""
        try:
            # 简单的GraphQL SDL解析
            lines = content.strip().split('\n')
            schema = {
                'type': 'graphql',
                'definitions': {},
                'queries': [],
                'mutations': [],
                'subscriptions': []
            }
            
            current_type = None
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 解析类型定义
                if line.startswith('type '):
                    type_match = re.match(r'type\s+(\w+)', line)
                    if type_match:
                        current_type = type_match.group(1)
                        schema['definitions'][current_type] = {'fields': []}
                
                # 解析字段定义
                elif current_type and ':' in line:
                    field_match = re.match(r'\s*(\w+):\s*(\w+)', line)
                    if field_match:
                        field_name = field_match.group(1)
                        field_type = field_match.group(2)
                        schema['definitions'][current_type]['fields'].append({
                            'name': field_name,
                            'type': field_type
                        })
            
            return schema
        
        except Exception as e:
            self.logger.error(f"解析GraphQL SDL规范失败: {e}")
            raise
    
    def _parse_custom(self, content: str) -> Dict[str, Any]:
        """解析自定义规范"""
        try:
            # 尝试解析为JSON或YAML
            if content.strip().startswith('{'):
                return json.loads(content)
            else:
                return yaml.safe_load(content)
        
        except Exception as e:
            self.logger.error(f"解析自定义规范失败: {e}")
            raise

class ValidationEngine:
    """验证引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = self._load_default_rules()
        self.custom_rules = []
    
    def validate_specification(self, specification: APISpecification, 
                             validation_level: ValidationLevel = ValidationLevel.STRICT) -> ValidationResult:
        """验证API规范"""
        try:
            start_time = time.time()
            
            errors = []
            warnings = []
            
            # 执行基础验证
            basic_errors, basic_warnings = self._validate_basic_structure(specification)
            errors.extend(basic_errors)
            warnings.extend(basic_warnings)
            
            # 执行详细验证
            if validation_level in [ValidationLevel.STRICT, ValidationLevel.LENIENT]:
                detailed_errors, detailed_warnings = self._validate_detailed_structure(specification)
                errors.extend(detailed_errors)
                warnings.extend(detailed_warnings)
            
            # 执行自定义规则验证
            custom_errors, custom_warnings = self._validate_custom_rules(specification)
            errors.extend(custom_errors)
            warnings.extend(custom_warnings)
            
            # 生成统计信息
            statistics = self._generate_statistics(specification, errors, warnings)
            
            execution_time = time.time() - start_time
            
            # 创建验证结果
            result = ValidationResult(
                result_id=str(uuid.uuid4()),
                specification_path=specification.file_path,
                validation_time=datetime.now(),
                total_errors=len(errors),
                total_warnings=len(warnings),
                errors=errors,
                warnings=warnings,
                statistics=statistics,
                execution_time=execution_time
            )
            
            self.logger.info(f"规范验证完成: {specification.file_path}, 错误: {len(errors)}, 警告: {len(warnings)}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"规范验证失败: {specification.file_path}, {e}")
            raise
    
    def _validate_basic_structure(self, specification: APISpecification) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """验证基础结构"""
        errors = []
        warnings = []
        content = specification.content
        
        # 验证必要字段
        if specification.spec_type in [SpecificationType.OPENAPI_30, SpecificationType.OPENAPI_31, SpecificationType.SWAGGER_20]:
            # 验证info字段
            if 'info' not in content:
                errors.append({
                    'level': ErrorLevel.ERROR.value,
                    'message': '缺少info字段',
                    'path': '$',
                    'rule': 'required_info'
                })
            else:
                info = content['info']
                if 'title' not in info:
                    errors.append({
                        'level': ErrorLevel.ERROR.value,
                        'message': '缺少API标题',
                        'path': '$.info',
                        'rule': 'required_title'
                    })
                
                if 'version' not in info:
                    warnings.append({
                        'level': ErrorLevel.WARN.value,
                        'message': '建议指定API版本',
                        'path': '$.info',
                        'rule': 'recommended_version'
                    })
            
            # 验证paths字段
            if 'paths' not in content:
                errors.append({
                    'level': ErrorLevel.ERROR.value,
                    'message': '缺少paths字段',
                    'path': '$',
                    'rule': 'required_paths'
                })
            elif not content['paths']:
                warnings.append({
                    'level': ErrorLevel.WARN.value,
                    'message': 'paths字段为空，没有定义任何API路径',
                    'path': '$.paths',
                    'rule': 'empty_paths'
                })
        
        return errors, warnings
    
    def _validate_detailed_structure(self, specification: APISpecification) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """验证详细结构"""
        errors = []
        warnings = []
        content = specification.content
        
        if specification.spec_type in [SpecificationType.OPENAPI_30, SpecificationType.OPENAPI_31, SpecificationType.SWAGGER_20]:
            # 验证路径定义
            paths = content.get('paths', {})
            for path, path_item in paths.items():
                # 验证路径格式
                if not path.startswith('/'):
                    errors.append({
                        'level': ErrorLevel.ERROR.value,
                        'message': f'路径格式错误: {path}，必须以/开头',
                        'path': f'$.paths.{path}',
                        'rule': 'path_format'
                    })
                
                # 验证HTTP方法
                for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    if method in path_item:
                        operation = path_item[method]
                        
                        # 验证operationId
                        if 'operationId' not in operation:
                            warnings.append({
                                'level': ErrorLevel.WARN.value,
                                'message': f'建议为{method} {path}添加operationId',
                                'path': f'$.paths.{path}.{method}',
                                'rule': 'recommended_operationId'
                            })
                        
                        # 验证响应定义
                        if 'responses' not in operation:
                            errors.append({
                                'level': ErrorLevel.ERROR.value,
                                'message': f'{method} {path}缺少responses定义',
                                'path': f'$.paths.{path}.{method}',
                                'rule': 'required_responses'
                            })
                        else:
                            responses = operation['responses']
                            if '200' not in responses and '201' not in responses:
                                warnings.append({
                                    'level': ErrorLevel.WARN.value,
                                    'message': f'{method} {path}缺少成功响应定义',
                                    'path': f'$.paths.{path}.{method}.responses',
                                    'rule': 'recommended_success_response'
                                })
        
        return errors, warnings
    
    def _validate_custom_rules(self, specification: APISpecification) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """验证自定义规则"""
        errors = []
        warnings = []
        
        for rule in self.custom_rules:
            if not rule.enabled:
                continue
            
            try:
                # 执行自定义规则验证
                rule_errors, rule_warnings = self._execute_rule(rule, specification)
                errors.extend(rule_errors)
                warnings.extend(rule_warnings)
            
            except Exception as e:
                self.logger.error(f"执行自定义规则失败: {rule.name}, {e}")
        
        return errors, warnings
    
    def _execute_rule(self, rule: ValidationRule, specification: APISpecification) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """执行验证规则"""
        errors = []
        warnings = []
        
        # 这里可以根据规则条件执行具体的验证逻辑
        # 简化示例：检查特定字段
        if rule.condition == 'check_security':
            content = specification.content
            if 'security' not in content:
                warnings.append({
                    'level': rule.level.value,
                    'message': rule.message,
                    'path': '$',
                    'rule': rule.rule_id
                })
        
        return errors, warnings
    
    def _generate_statistics(self, specification: APISpecification, 
                           errors: List[Dict[str, Any]], warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成统计信息"""
        try:
            content = specification.content
            stats = {
                'specification_type': specification.spec_type.value,
                'version': specification.version,
                'total_paths': 0,
                'total_operations': 0,
                'total_schemas': 0,
                'error_types': Counter(),
                'warning_types': Counter()
            }
            
            if specification.spec_type in [SpecificationType.OPENAPI_30, SpecificationType.OPENAPI_31, SpecificationType.SWAGGER_20]:
                # 统计路径和操作
                paths = content.get('paths', {})
                stats['total_paths'] = len(paths)
                
                for path_item in paths.values():
                    for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                        if method in path_item:
                            stats['total_operations'] += 1
                
                # 统计模式
                components = content.get('components', {})
                schemas = components.get('schemas', {})
                stats['total_schemas'] = len(schemas)
            
            # 统计错误和警告类型
            for error in errors:
                rule = error.get('rule', 'unknown')
                stats['error_types'][rule] += 1
            
            for warning in warnings:
                rule = warning.get('rule', 'unknown')
                stats['warning_types'][rule] += 1
            
            return stats
        
        except Exception as e:
            self.logger.error(f"生成统计信息失败: {e}")
            return {}
    
    def _load_default_rules(self) -> List[ValidationRule]:
        """加载默认验证规则"""
        return [
            ValidationRule(
                rule_id="required_info",
                name="Info字段验证",
                description="验证API规范是否包含必要的info字段",
                level=ErrorLevel.ERROR,
                condition="check_info",
                message="API规范必须包含info字段"
            ),
            ValidationRule(
                rule_id="required_paths",
                name="Paths字段验证",
                description="验证API规范是否包含paths字段",
                level=ErrorLevel.ERROR,
                condition="check_paths",
                message="API规范必须包含paths字段"
            ),
            ValidationRule(
                rule_id="check_security",
                name="安全验证",
                description="检查API规范是否定义了安全配置",
                level=ErrorLevel.WARN,
                condition="check_security",
                message="建议为API添加安全配置"
            )
        ]
    
    def add_custom_rule(self, rule: ValidationRule):
        """添加自定义规则"""
        self.custom_rules.append(rule)
        self.logger.info(f"添加自定义规则: {rule.name}")
    
    def remove_custom_rule(self, rule_id: str):
        """移除自定义规则"""
        self.custom_rules = [rule for rule in self.custom_rules if rule.rule_id != rule_id]
        self.logger.info(f"移除自定义规则: {rule_id}")

class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, result: ValidationResult, format_type: str = "html") -> str:
        """生成验证报告"""
        try:
            if format_type == "html":
                return self._generate_html_report(result)
            elif format_type == "json":
                return self._generate_json_report(result)
            elif format_type == "pdf":
                return self._generate_pdf_report(result)
            elif format_type == "markdown":
                return self._generate_markdown_report(result)
            else:
                raise ValueError(f"不支持的报告格式: {format_type}")
        
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            raise
    
    def _generate_html_report(self, result: ValidationResult) -> str:
        """生成HTML报告"""
        try:
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>API契约验证报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .error { color: red; }
        .warning { color: orange; }
        .section { margin: 20px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>API契约验证报告</h1>
        <p>规范路径: {spec_path}</p>
        <p>验证时间: {validation_time}</p>
        <p>执行时间: {execution_time:.2f}秒</p>
    </div>
    
    <div class="summary">
        <h2>验证摘要</h2>
        <p>错误数量: <span class="error">{total_errors}</span></p>
        <p>警告数量: <span class="warning">{total_warnings}</span></p>
    </div>
    
    <div class="section">
        <h2>错误详情</h2>
        <table>
            <tr>
                <th>级别</th>
                <th>消息</th>
                <th>路径</th>
                <th>规则</th>
            </tr>
            {error_rows}
        </table>
    </div>
    
    <div class="section">
        <h2>警告详情</h2>
        <table>
            <tr>
                <th>级别</th>
                <th>消息</th>
                <th>路径</th>
                <th>规则</th>
            </tr>
            {warning_rows}
        </table>
    </div>
    
    <div class="section">
        <h2>统计信息</h2>
        <pre>{statistics}</pre>
    </div>
</body>
</html>
"""
            
            # 生成错误行
            error_rows = ""
            for error in result.errors:
                error_rows += f"""
                <tr>
                    <td class="error">{error['level']}</td>
                    <td>{error['message']}</td>
                    <td>{error['path']}</td>
                    <td>{error['rule']}</td>
                </tr>
                """
            
            # 生成警告行
            warning_rows = ""
            for warning in result.warnings:
                warning_rows += f"""
                <tr>
                    <td class="warning">{warning['level']}</td>
                    <td>{warning['message']}</td>
                    <td>{warning['path']}</td>
                    <td>{warning['rule']}</td>
                </tr>
                """
            
            # 填充模板
            html_content = html_template.format(
                spec_path=result.specification_path,
                validation_time=result.validation_time.strftime('%Y-%m-%d %H:%M:%S'),
                execution_time=result.execution_time,
                total_errors=result.total_errors,
                total_warnings=result.total_warnings,
                error_rows=error_rows,
                warning_rows=warning_rows,
                statistics=json.dumps(result.statistics, indent=2, ensure_ascii=False)
            )
            
            return html_content
        
        except Exception as e:
            self.logger.error(f"生成HTML报告失败: {e}")
            raise
    
    def _generate_json_report(self, result: ValidationResult) -> str:
        """生成JSON报告"""
        try:
            report_data = {
                'result_id': result.result_id,
                'specification_path': result.specification_path,
                'validation_time': result.validation_time.isoformat(),
                'execution_time': result.execution_time,
                'summary': {
                    'total_errors': result.total_errors,
                    'total_warnings': result.total_warnings
                },
                'errors': result.errors,
                'warnings': result.warnings,
                'statistics': result.statistics
            }
            
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"生成JSON报告失败: {e}")
            raise
    
    def _generate_pdf_report(self, result: ValidationResult) -> str:
        """生成PDF报告"""
        try:
            # 这里可以使用reportlab等库生成PDF
            # 简化实现：返回PDF文件路径
            pdf_path = f"/tmp/validation_report_{result.result_id}.pdf"
            
            # 实际实现中需要使用PDF库生成PDF文件
            # 这里只是示例
            with open(pdf_path, 'w') as f:
                f.write(f"PDF Report for {result.specification_path}")
            
            return pdf_path
        
        except Exception as e:
            self.logger.error(f"生成PDF报告失败: {e}")
            raise
    
    def _generate_markdown_report(self, result: ValidationResult) -> str:
        """生成Markdown报告"""
        try:
            markdown_content = f"""# API契约验证报告

## 基本信息

- **规范路径**: {result.specification_path}
- **验证时间**: {result.validation_time.strftime('%Y-%m-%d %H:%M:%S')}
- **执行时间**: {result.execution_time:.2f}秒

## 验证摘要

- **错误数量**: {result.total_errors}
- **警告数量**: {result.total_warnings}

## 错误详情

"""
            
            for error in result.errors:
                markdown_content += f"""### {error['level']}

- **消息**: {error['message']}
- **路径**: {error['path']}
- **规则**: {error['rule']}

"""
            
            markdown_content += "## 警告详情\n\n"
            
            for warning in result.warnings:
                markdown_content += f"""### {warning['level']}

- **消息**: {warning['message']}
- **路径**: {warning['path']}
- **规则**: {warning['rule']}

"""
            
            markdown_content += "## 统计信息\n\n"
            markdown_content += f"```json\n{json.dumps(result.statistics, indent=2, ensure_ascii=False)}\n```"
            
            return markdown_content
        
        except Exception as e:
            self.logger.error(f"生成Markdown报告失败: {e}")
            raise

class APIContractValidator:
    """API契约验证器主类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.parser = SpecificationParser()
        self.validation_engine = ValidationEngine()
        self.report_generator = ReportGenerator()
    
    def validate_file(self, file_path: str, spec_type: Optional[SpecificationType] = None,
                     validation_level: ValidationLevel = ValidationLevel.STRICT) -> ValidationResult:
        """验证单个文件"""
        try:
            # 解析规范
            specification = self.parser.parse_specification(file_path, spec_type)
            
            # 执行验证
            result = self.validation_engine.validate_specification(specification, validation_level)
            
            return result
        
        except Exception as e:
            self.logger.error(f"验证文件失败: {file_path}, {e}")
            raise
    
    def validate_directory(self, directory_path: str, pattern: str = "*.yaml",
                          validation_level: ValidationLevel = ValidationLevel.STRICT) -> List[ValidationResult]:
        """验证目录中的所有规范文件"""
        try:
            import glob
            
            results = []
            file_paths = glob.glob(os.path.join(directory_path, pattern))
            
            for file_path in file_paths:
                try:
                    result = self.validate_file(file_path, validation_level=validation_level)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"验证文件失败: {file_path}, {e}")
            
            return results
        
        except Exception as e:
            self.logger.error(f"验证目录失败: {directory_path}, {e}")
            raise
    
    def generate_report(self, result: ValidationResult, format_type: str = "html", 
                       output_path: Optional[str] = None) -> str:
        """生成验证报告"""
        try:
            report_content = self.report_generator.generate_report(result, format_type)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"报告已保存到: {output_path}")
            
            return report_content
        
        except Exception as e:
            self.logger.error(f"生成报告失败: {e}")
            raise
    
    def add_validation_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.validation_engine.add_custom_rule(rule)
    
    def remove_validation_rule(self, rule_id: str):
        """移除验证规则"""
        self.validation_engine.remove_custom_rule(rule_id)

# 使用示例
# 创建API契约验证器
validator = APIContractValidator()

# 验证单个文件
try:
    result = validator.validate_file("/path/to/api.yaml")
    print(f"验证完成: 错误 {result.total_errors}, 警告 {result.total_warnings}")
    
    # 生成HTML报告
    html_report = validator.generate_report(result, "html", "/tmp/validation_report.html")
    print("HTML报告已生成")
    
    # 生成JSON报告
    json_report = validator.generate_report(result, "json", "/tmp/validation_report.json")
    print("JSON报告已生成")
    
except Exception as e:
    print(f"验证失败: {e}")

# 验证目录
try:
    results = validator.validate_directory("/path/to/api/specs", "*.yaml")
    print(f"目录验证完成: 共验证 {len(results)} 个文件")
    
    for result in results:
        print(f"文件: {result.specification_path}, 错误: {result.total_errors}, 警告: {result.total_warnings}")
    
except Exception as e:
    print(f"目录验证失败: {e}")

# 添加自定义验证规则
custom_rule = ValidationRule(
    rule_id="custom_naming",
    name="命名规范验证",
    description="验证API路径是否符合命名规范",
    level=ErrorLevel.WARN,
    condition="check_naming",
    message="API路径应符合RESTful命名规范"
)

validator.add_validation_rule(custom_rule)
print("自定义规则已添加")
```

## 参考资源

### API规范文档
- [OpenAPI 3.0规范](https://swagger.io/specification/)
- [OpenAPI 3.1规范](https://spec.openapis.org/oas/v3.1.0)
- [Swagger 2.0规范](https://swagger.io/specification/v2/)
- [GraphQL规范](https://graphql.org/learn/schema/)

### 验证工具
- [Swagger Editor](https://editor.swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Prism](https://stoplight.io/open-source/prism)
- [Dredd](https://dredd.org/)

### 最佳实践
- [API设计指南](https://restfulapi.net/)
- [OpenAPI最佳实践](https://swagger.io/docs/specification/best-practices/)
- [RESTful API设计原则](https://www.ics.uci.edu/~fielding/pubs/dissertation/top.htm)
- [API版本控制策略](https://www.vinaysahni.com/best-way-to-version-your-api)

### 集成工具
- [Jenkins插件](https://plugins.jenkins.io/swagger-validation/)
- [GitHub Actions](https://github.com/marketplace/actions/openapi-validator)
- [GitLab CI](https://docs.gitlab.com/ee/ci/)
- [CircleCI](https://circleci.com/)
