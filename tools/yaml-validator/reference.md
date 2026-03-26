# YAML验证器参考文档

## YAML概述

### 什么是YAML
YAML (YAML Ain't Markup Language) 是一种人类可读的数据序列化格式，常用于配置文件、数据交换和应用程序配置。它设计目标是易于人类阅读和编写，同时易于机器解析和生成。

### YAML核心特性
- **可读性强**: 使用缩进和简洁语法，易于人类理解
- **数据类型丰富**: 支持标量、序列、映射等复杂数据结构
- **语言无关**: 可与多种编程语言集成
- **注释支持**: 允许添加注释提高可维护性
- **引用机制**: 支持锚点和别名避免重复
- **多文档**: 支持单个文件包含多个YAML文档

## YAML语法基础

### 基础语法规则
```yaml
# 注释以#开头
# 基本键值对
name: "John Doe"
age: 30
active: true

# 列表/数组
hobbies:
  - reading
  - swimming
  - coding

# 嵌套结构
person:
  name: "Alice"
  address:
    street: "123 Main St"
    city: "New York"
    country: "USA"
  contacts:
    - type: "email"
      value: "alice@example.com"
    - type: "phone"
      value: "+1-555-0123"

# 多行字符串
description: |
  This is a multi-line
  string that preserves
  line breaks.

# 折叠多行字符串
summary: >
  This is a folded string
  that converts newlines
  to spaces.
```

### 高级语法特性
```yaml
# 锚点和别名
default_config: &default
  timeout: 30
  retries: 3
  debug: false

# 使用别名引用
production:
  <<: *default
  debug: true

development:
  <<: *default
  timeout: 60

# 多文档分隔符
---
document1:
  version: 1.0
  name: "First Document"

---
document2:
  version: 2.0
  name: "Second Document"

# 自定义标签
date: !!str 2023-12-25
number: !!int "42"
boolean: !!bool "true"
```

## YAML验证器架构

### 验证流程
```python
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    SYNTAX = "syntax"
    STRUCTURE = "structure"
    SEMANTIC = "semantic"
    SECURITY = "security"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class YAMLValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = self._load_validation_rules()
        
    def validate_file(self, file_path: str) -> ValidationResult:
        """验证YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.validate_content(content, source=file_path)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[{"type": "file_error", "message": str(e)}],
                warnings=[],
                metadata={"source": file_path}
            )
    
    def validate_content(self, content: str, source: str = "<string>") -> ValidationResult:
        """验证YAML内容"""
        errors = []
        warnings = []
        metadata = {"source": source}
        
        # 1. 语法验证
        try:
            data = yaml.safe_load(content)
            metadata["parsed"] = True
        except yaml.YAMLError as e:
            errors.append({
                "type": "syntax_error",
                "message": str(e),
                "line": getattr(e, 'problem_mark', None)
            })
            return ValidationResult(False, errors, warnings, metadata)
        
        # 2. 结构验证
        structure_errors = self._validate_structure(data)
        errors.extend(structure_errors)
        
        # 3. 数据类型验证
        type_errors = self._validate_types(data)
        errors.extend(type_errors)
        
        # 4. 安全验证
        security_warnings = self._validate_security(data)
        warnings.extend(security_warnings)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, metadata)
```

### 语法验证器
```python
class SyntaxValidator:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        
    def validate_indentation(self, content: str) -> List[Dict[str, Any]]:
        """验证缩进一致性"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip() == '' or line.strip().startswith('#'):
                continue
                
            # 检查缩进字符
            if '\t' in line and ' ' in line[:len(line) - len(line.lstrip())]:
                errors.append({
                    "type": "indentation_mixed",
                    "line": i,
                    "message": "Mixed spaces and tabs for indentation"
                })
        
        return errors
    
    def validate_special_characters(self, content: str) -> List[Dict[str, Any]]:
        """验证特殊字符使用"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查未转义的特殊字符
            if ':' in line and not line.strip().startswith('-'):
                # 简单的冒号使用检查
                pass
        
        return errors
    
    def validate_comments(self, content: str) -> List[Dict[str, Any]]:
        """验证注释格式"""
        warnings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查注释位置
            if '#' in line and not line.strip().startswith('#'):
                comment_pos = line.find('#')
                before_comment = line[:comment_pos].rstrip()
                if before_comment and not before_comment.endswith(':'):
                    warnings.append({
                        "type": "comment_position",
                        "line": i,
                        "message": "Comment might be better placed on separate line"
                    })
        
        return warnings
```

## 数据类型验证

### 类型检查器
```python
from typing import Union, List, Dict, Any
import re

class TypeValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        
    def validate_value(self, value: Any, expected_type: str, path: str = "") -> List[Dict[str, Any]]:
        """验证单个值的类型"""
        errors = []
        
        if expected_type == "string":
            if not isinstance(value, str):
                errors.append({
                    "type": "type_mismatch",
                    "path": path,
                    "expected": "string",
                    "actual": type(value).__name__
                })
        elif expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append({
                    "type": "type_mismatch",
                    "path": path,
                    "expected": "integer",
                    "actual": type(value).__name__
                })
        elif expected_type == "float":
            if not isinstance(value, (float, int)) or isinstance(value, bool):
                errors.append({
                    "type": "type_mismatch",
                    "path": path,
                    "expected": "float",
                    "actual": type(value).__name__
                })
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                errors.append({
                    "type": "type_mismatch",
                    "path": path,
                    "expected": "boolean",
                    "actual": type(value).__name__
                })
        elif expected_type == "array":
            if not isinstance(value, list):
                errors.append({
                    "type": "type_mismatch",
                    "path": path,
                    "expected": "array",
                    "actual": type(value).__name__
                })
        elif expected_type == "object":
            if not isinstance(value, dict):
                errors.append({
                    "type": "type_mismatch",
                    "path": path,
                    "expected": "object",
                    "actual": type(value).__name__
                })
        
        return errors
    
    def validate_string_format(self, value: str, format_pattern: str, path: str = "") -> List[Dict[str, Any]]:
        """验证字符串格式"""
        errors = []
        
        try:
            if not re.match(format_pattern, value):
                errors.append({
                    "type": "format_mismatch",
                    "path": path,
                    "pattern": format_pattern,
                    "value": value
                })
        except re.error:
            errors.append({
                "type": "invalid_pattern",
                "path": path,
                "pattern": format_pattern
            })
        
        return errors
    
    def validate_range(self, value: Union[int, float], min_val: Any = None, max_val: Any = None, path: str = "") -> List[Dict[str, Any]]:
        """验证数值范围"""
        errors = []
        
        if min_val is not None and value < min_val:
            errors.append({
                "type": "range_too_small",
                "path": path,
                "min": min_val,
                "actual": value
            })
        
        if max_val is not None and value > max_val:
            errors.append({
                "type": "range_too_large",
                "path": path,
                "max": max_val,
                "actual": value
            })
        
        return errors
```

### 模式验证
```python
class SchemaValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        
    def validate(self, data: Any, path: str = "") -> List[Dict[str, Any]]:
        """根据模式验证数据"""
        errors = []
        
        if "type" in self.schema:
            type_errors = self._validate_type(data, self.schema["type"], path)
            errors.extend(type_errors)
        
        if "properties" in self.schema and isinstance(data, dict):
            property_errors = self._validate_properties(data, self.schema["properties"], path)
            errors.extend(property_errors)
        
        if "required" in self.schema and isinstance(data, dict):
            required_errors = self._validate_required(data, self.schema["required"], path)
            errors.extend(required_errors)
        
        if "items" in self.schema and isinstance(data, list):
            item_errors = self._validate_array_items(data, self.schema["items"], path)
            errors.extend(item_errors)
        
        return errors
    
    def _validate_type(self, data: Any, expected_type: str, path: str) -> List[Dict[str, Any]]:
        """验证类型"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type and not isinstance(data, expected_python_type):
            return [{
                "type": "type_mismatch",
                "path": path,
                "expected": expected_type,
                "actual": type(data).__name__
            }]
        
        return []
    
    def _validate_properties(self, data: Dict[str, Any], properties: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        """验证对象属性"""
        errors = []
        
        for prop_name, prop_schema in properties.items():
            prop_path = f"{path}.{prop_name}" if path else prop_name
            
            if prop_name in data:
                prop_validator = SchemaValidator(prop_schema)
                prop_errors = prop_validator.validate(data[prop_name], prop_path)
                errors.extend(prop_errors)
        
        return errors
    
    def _validate_required(self, data: Dict[str, Any], required: List[str], path: str) -> List[Dict[str, Any]]:
        """验证必需字段"""
        errors = []
        
        for field in required:
            if field not in data:
                field_path = f"{path}.{field}" if path else field
                errors.append({
                    "type": "missing_required",
                    "path": field_path,
                    "field": field
                })
        
        return errors
```

## 安全验证

### 安全检查器
```python
import re
import os.path

class SecurityValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dangerous_patterns = self._load_dangerous_patterns()
        
    def _load_dangerous_patterns(self) -> List[Dict[str, Any]]:
        """加载危险模式"""
        return [
            {
                "name": "code_injection",
                "pattern": r'\$\{.*\}',
                "description": "Possible code injection"
            },
            {
                "name": "command_execution",
                "pattern": r'\|\s*\w+',
                "description": "Possible command execution"
            },
            {
                "name": "path_traversal",
                "pattern": r'\.\./',
                "description": "Path traversal attempt"
            },
            {
                "name": "sql_injection",
                "pattern": r'(?i)(union|select|insert|update|delete|drop)',
                "description": "Possible SQL injection"
            }
        ]
    
    def validate_content(self, data: Any, path: str = "") -> List[Dict[str, Any]]:
        """验证内容安全性"""
        warnings = []
        
        if isinstance(data, str):
            content_warnings = self._check_string_content(data, path)
            warnings.extend(content_warnings)
        elif isinstance(data, dict):
            for key, value in data.items():
                key_path = f"{path}.{key}" if path else key
                dict_warnings = self.validate_content(value, key_path)
                warnings.extend(dict_warnings)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]" if path else f"[{i}]"
                list_warnings = self.validate_content(item, item_path)
                warnings.extend(list_warnings)
        
        return warnings
    
    def _check_string_content(self, content: str, path: str) -> List[Dict[str, Any]]:
        """检查字符串内容"""
        warnings = []
        
        for pattern_info in self.dangerous_patterns:
            if re.search(pattern_info["pattern"], content):
                warnings.append({
                    "type": "security_warning",
                    "path": path,
                    "pattern": pattern_info["name"],
                    "description": pattern_info["description"],
                    "content": content[:100] + "..." if len(content) > 100 else content
                })
        
        return warnings
    
    def validate_file_paths(self, data: Any, path: str = "") -> List[Dict[str, Any]]:
        """验证文件路径安全性"""
        warnings = []
        
        if isinstance(data, str):
            path_warnings = self._check_file_path(data, path)
            warnings.extend(path_warnings)
        elif isinstance(data, (dict, list)):
            # 递归检查
            if isinstance(data, dict):
                for key, value in data.items():
                    key_path = f"{path}.{key}" if path else key
                    path_warnings = self.validate_file_paths(value, key_path)
                    warnings.extend(path_warnings)
            else:
                for i, item in enumerate(data):
                    item_path = f"{path}[{i}]" if path else f"[{i}]"
                    path_warnings = self.validate_file_paths(item, item_path)
                    warnings.extend(path_warnings)
        
        return warnings
    
    def _check_file_path(self, file_path: str, path: str) -> List[Dict[str, Any]]:
        """检查单个文件路径"""
        warnings = []
        
        # 检查路径遍历
        if ".." in file_path:
            warnings.append({
                "type": "path_traversal",
                "path": path,
                "file_path": file_path,
                "description": "Path contains directory traversal"
            })
        
        # 检查绝对路径
        if os.path.isabs(file_path):
            warnings.append({
                "type": "absolute_path",
                "path": path,
                "file_path": file_path,
                "description": "Absolute path detected"
            })
        
        return warnings
```

## 性能优化

### 大文件处理
```python
import yaml
from io import StringIO

class StreamingValidator:
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        
    def validate_large_file(self, file_path: str, validator: YAMLValidator) -> ValidationResult:
        """流式验证大文件"""
        errors = []
        warnings = []
        metadata = {"source": file_path, "streaming": True}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 分块读取和处理
                for chunk in self._read_chunks(f):
                    chunk_errors = self._validate_chunk(chunk, validator)
                    errors.extend(chunk_errors)
        
        except Exception as e:
            errors.append({
                "type": "file_error",
                "message": str(e)
            })
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, metadata)
    
    def _read_chunks(self, file_handle):
        """分块读取文件"""
        buffer = ""
        
        while True:
            chunk = file_handle.read(self.chunk_size)
            if not chunk:
                if buffer:
                    yield buffer
                break
            
            buffer += chunk
            lines = buffer.split('\n')
            buffer = lines[-1]  # 保留最后一行（可能不完整）
            
            for line in lines[:-1]:
                yield line
    
    def _validate_chunk(self, chunk: str, validator: YAMLValidator) -> List[Dict[str, Any]]:
        """验证单个块"""
        # 简单的语法检查
        errors = []
        
        try:
            # 尝试解析块（如果块包含完整的YAML结构）
            if chunk.strip() and ':' in chunk:
                yaml.safe_load(chunk)
        except yaml.YAMLError as e:
            errors.append({
                "type": "syntax_error",
                "message": str(e),
                "chunk_preview": chunk[:100]
            })
        
        return errors
```

### 缓存机制
```python
from functools import lru_cache
import hashlib
import pickle

class ValidationCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        
    def get_cache_key(self, content: str, config: Dict[str, Any]) -> str:
        """生成缓存键"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        config_hash = hashlib.md5(pickle.dumps(config)).hexdigest()
        return f"{content_hash}_{config_hash}"
    
    @lru_cache(maxsize=1000)
    def get_cached_result(self, cache_key: str) -> Optional[ValidationResult]:
        """获取缓存结果"""
        # 实际实现中这里会从持久化存储读取
        return None
    
    def cache_result(self, cache_key: str, result: ValidationResult):
        """缓存验证结果"""
        # 实际实现中这里会保存到持久化存储
        pass
```

## 集成和扩展

### IDE插件示例
```python
# VS Code扩展示例
import vscode
from yaml_validator import YAMLValidator

class YAMLValidatorExtension:
    def __init__(self):
        self.validator = YAMLValidator(self.get_config())
        self.diagnostics = vscode.languages.createDiagnosticCollection("yaml-validator")
        
    def activate(self, context):
        # 注册文档事件监听器
        context.subscriptions.append(
            vscode.workspace.onDidSaveTextDocument(self.on_document_save)
        )
        
        context.subscriptions.append(
            vscode.workspace.onDidChangeTextDocument(self.on_document_change)
        )
        
        # 注册命令
        context.subscriptions.append(
            vscode.commands.registerCommand('yaml-validator.validate', self.validate_current_document)
        )
    
    def on_document_save(self, document):
        """文档保存时验证"""
        if document.languageId == 'yaml':
            self.validate_document(document)
    
    def on_document_change(self, event):
        """文档内容变化时实时验证"""
        document = event.document
        if document.languageId == 'yaml':
            self.validate_document(document, real_time=True)
    
    def validate_document(self, document, real_time=False):
        """验证文档"""
        content = document.getText()
        result = self.validator.validate_content(content, source=document.uri)
        
        # 转换为VS Code诊断信息
        diagnostics = []
        
        for error in result.errors:
            line = error.get('line', 1) - 1  # VS Code使用0基索引
            range = vscode.Range(line, 0, line, 100)
            
            diagnostic = vscode.Diagnostic(
                range,
                error['message'],
                vscode.DiagnosticSeverity.Error
            )
            diagnostics.append(diagnostic)
        
        for warning in result.warnings:
            line = warning.get('line', 1) - 1
            range = vscode.Range(line, 0, line, 100)
            
            diagnostic = vscode.Diagnostic(
                range,
                warning['message'],
                vscode.DiagnosticSeverity.Warning
            )
            diagnostics.append(diagnostic)
        
        self.diagnostics.set(document.uri, diagnostics)
```

### CI/CD集成
```yaml
# GitHub Actions工作流示例
name: YAML Validation

on:
  push:
    paths:
      - '**/*.yaml'
      - '**/*.yml'
  pull_request:
    paths:
      - '**/*.yaml'
      - '**/*.yml'

jobs:
  validate-yaml:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install pyyaml jsonschema
    
    - name: Validate YAML files
      run: |
        python -m yaml_validator.validate \
          --config .github/yaml-validator-config.json \
          --format github \
          --output validation-report.json \
          **/*.yaml **/*.yml
    
    - name: Upload validation report
      uses: actions/upload-artifact@v2
      with:
        name: validation-report
        path: validation-report.json
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = JSON.parse(fs.readFileSync('validation-report.json', 'utf8'));
          
          const comment = `## YAML Validation Results
          
          **Status**: ${report.valid ? '✅ Passed' : '❌ Failed'}
          **Files checked**: ${report.files_checked}
          **Errors**: ${report.errors.length}
          **Warnings**: ${report.warnings.length}
          
          ${report.errors.length > 0 ? '### Errors:\n' + report.errors.map(e => `- ${e.file}:${e.line}: ${e.message}`).join('\n') : ''}
          ${report.warnings.length > 0 ? '### Warnings:\n' + report.warnings.map(w => `- ${w.file}:${w.line}: ${w.message}`).join('\n') : ''}
          `;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

## 最佳实践

### YAML编写规范
1. **缩进一致性**: 使用2个空格进行缩进，避免使用Tab
2. **命名规范**: 使用小写字母和连字符命名键
3. **注释使用**: 为复杂配置添加说明性注释
4. **文件组织**: 将相关配置分组，使用逻辑结构
5. **版本控制**: 在配置文件中包含版本信息

### 验证策略
1. **分层验证**: 语法 → 结构 → 语义 → 安全
2. **渐进式验证**: 从基础检查开始，逐步增加验证强度
3. **上下文相关**: 根据使用场景调整验证规则
4. **性能平衡**: 在验证强度和性能之间找到平衡

### 错误处理
1. **详细错误信息**: 提供准确的错误位置和描述
2. **修复建议**: 为常见错误提供修复建议
3. **错误分类**: 区分语法错误、类型错误、安全警告等
4. **批量处理**: 一次性报告所有错误，提高修复效率

这个YAML验证器参考文档提供了完整的验证框架实现，包括语法检查、类型验证、安全检测、性能优化和集成方案，帮助开发者构建可靠的YAML处理系统。
