---
name: YAML验证器
description: "当验证YAML文件、检查Kubernetes清单、调试Docker Compose或验证配置文件时，在部署前验证YAML。"
license: MIT
---

# YAML验证器技能

## 概述
YAML是DevOps中的核心技术 - Kubernetes、Docker Compose、GitHub Actions都使用YAML。无效的YAML会以神秘的错误消息静默破坏部署。

**核心原则**: 无效的YAML = 部署失败。在部署前验证。

## 何时使用

**始终:**
- 在部署Kubernetes清单之前
- 验证Docker Compose文件
- 检查持续集成/持续部署工作流文件
- 在提交配置文件之前
- 验证应用程序配置
- 检查基础设施即代码文件

**触发短语:**
- "验证这个YAML文件"
- "检查Kubernetes配置"
- "这个Docker Compose文件有问题吗？"
- "YAML语法错误"
- "部署失败，检查配置"
- "配置文件验证"

## YAML验证功能

### 语法检查
- 缩进验证
- 引号检查
- 特殊字符处理
- 注释格式验证
- 文档分隔符检查

### 结构验证
- 必需字段检查
- 数据类型验证
- 嵌套结构验证
- 引用完整性检查
- 模式匹配验证

### 语义分析
- 业务逻辑验证
- 依赖关系检查
- 配置一致性验证
- 最佳实践检查
- 安全性审查

## 常见YAML错误

### 缩进错误
```
问题:
YAML使用空格缩进，不能使用制表符

错误示例:
services:
  web:
	image: nginx:latest  ← 使用了制表符
  database:
	image: postgres:13

解决方案:
- 使用2个或4个空格进行缩进
- 统一缩进风格
- 配置编辑器显示空白字符
```

### 引号问题
```
问题:
特殊字符需要引号包围

错误示例:
password: my#password  ← #会被当作注释
url: https://example.com/api/v1/resource?id=123&key=value

解决方案:
password: "my#password"
url: "https://example.com/api/v1/resource?id=123&key=value"
```

### 数据类型混淆
```
问题:
YAML会自动推断数据类型

错误示例:
port: "8080"  ← 字符串而不是数字
enabled: "true"  ← 字符串而不是布尔值
timeout: 30s  ← 无效的时间格式

解决方案:
port: 8080
enabled: true
timeout: 30
```

## 代码实现示例

### YAML验证器
```python
import yaml
import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import jsonschema

class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    """验证结果"""
    level: ValidationLevel
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None

@dataclass
class YAMLDocument:
    """YAML文档"""
    content: Dict[str, Any]
    line_map: Dict[int, str]
    metadata: Dict[str, Any]

class YAMLValidator:
    """YAML验证器"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.kubernetes_schemas = self._load_kubernetes_schemas()
        self.docker_compose_schema = self._load_docker_compose_schema()
    
    def validate_yaml_file(self, file_path: Union[str, Path]) -> List[ValidationResult]:
        """验证YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return [ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"无法读取文件: {str(e)}"
            )]
        
        return self.validate_yaml_content(content, lines)
    
    def validate_yaml_content(self, content: str, lines: List[str] = None) -> List[ValidationResult]:
        """验证YAML内容"""
        results = []
        
        # 语法验证
        syntax_results = self._validate_syntax(content, lines)
        results.extend(syntax_results)
        
        # 如果有语法错误，跳过其他验证
        if any(r.level == ValidationLevel.ERROR for r in syntax_results):
            return results
        
        try:
            # 解析YAML
            yaml_data = yaml.safe_load(content)
            
            # 结构验证
            structure_results = self._validate_structure(yaml_data, lines)
            results.extend(structure_results)
            
            # 语义验证
            semantic_results = self._validate_semantics(yaml_data, lines)
            results.extend(semantic_results)
            
            # 特定框架验证
            framework_results = self._validate_framework_specific(yaml_data, lines)
            results.extend(framework_results)
            
        except yaml.YAMLError as e:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"YAML解析错误: {str(e)}",
                line=getattr(e, 'problem_mark', None).line + 1 if hasattr(e, 'problem_mark') else None,
                column=getattr(e, 'problem_mark', None).column + 1 if hasattr(e, 'problem_mark') else None
            ))
        
        return results
    
    def _validate_syntax(self, content: str, lines: List[str]) -> List[ValidationResult]:
        """验证语法"""
        results = []
        
        if not lines:
            lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 检查制表符
            if '\t' in line:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message="YAML不允许使用制表符，请使用空格",
                    line=line_num,
                    column=line.find('\t') + 1,
                    suggestion="将制表符替换为空格"
                ))
            
            # 检查缩进一致性
            if line.strip():
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces % 2 != 0:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        message="建议使用2个或4个空格的倍数进行缩进",
                        line=line_num,
                        column=1,
                        suggestion="使用统一的缩进风格"
                    ))
            
            # 检查未转义的特殊字符
            if ':' in line and not line.strip().startswith('#'):
                # 检查冒号后的值是否需要引号
                parts = line.split(':', 1)
                if len(parts) == 2:
                    value = parts[1].strip()
                    if value and not (value.startswith('"') or value.startswith("'")):
                        if re.search(r'[#&*|>!%@`]', value):
                            results.append(ValidationResult(
                                level=ValidationLevel.WARNING,
                                message="包含特殊字符的值应该用引号包围",
                                line=line_num,
                                column=len(parts[0]) + 2,
                                suggestion=f'将值改为: "{value}"'
                            ))
        
        return results
    
    def _validate_structure(self, yaml_data: Dict[str, Any], lines: List[str]) -> List[ValidationResult]:
        """验证结构"""
        results = []
        
        # 检查必需字段
        if isinstance(yaml_data, dict):
            required_fields = self.validation_rules.get('required_fields', [])
            for field in required_fields:
                if field not in yaml_data:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"缺少必需字段: {field}",
                        suggestion=f"添加 {field}: <value>"
                    ))
        
        # 检查数据类型
        type_rules = self.validation_rules.get('type_rules', {})
        self._check_data_types(yaml_data, type_rules, "", results)
        
        # 检查嵌套结构
        structure_rules = self.validation_rules.get('structure_rules', {})
        self._check_structure(yaml_data, structure_rules, "", results)
        
        return results
    
    def _check_data_types(self, data: Any, type_rules: Dict[str, str], path: str, results: List[ValidationResult]):
        """检查数据类型"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if key in type_rules:
                    expected_type = type_rules[key]
                    if not self._is_valid_type(value, expected_type):
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"字段 {current_path} 类型错误，期望 {expected_type}，实际 {type(value).__name__}",
                            suggestion=f"将 {current_path} 的值转换为 {expected_type} 类型"
                        ))
                
                # 递归检查嵌套结构
                if isinstance(value, (dict, list)):
                    self._check_data_types(value, type_rules, current_path, results)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, (dict, list)):
                    self._check_data_types(item, type_rules, current_path, results)
    
    def _is_valid_type(self, value: Any, expected_type: str) -> bool:
        """检查类型是否有效"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True
    
    def _check_structure(self, data: Any, structure_rules: Dict[str, Any], path: str, results: List[ValidationResult]):
        """检查结构"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if key in structure_rules:
                    rule = structure_rules[key]
                    if isinstance(rule, dict):
                        # 检查子结构
                        if 'required_fields' in rule:
                            for field in rule['required_fields']:
                                if field not in value:
                                    results.append(ValidationResult(
                                        level=ValidationLevel.ERROR,
                                        message=f"缺少必需字段: {current_path}.{field}",
                                        suggestion=f"添加 {field}: <value>"
                                    ))
                        
                        if 'max_items' in rule and isinstance(value, list):
                            if len(value) > rule['max_items']:
                                results.append(ValidationResult(
                                    level=ValidationLevel.WARNING,
                                    message=f"{current_path} 项目数量超过限制 ({len(value)} > {rule['max_items']})",
                                    suggestion=f"减少项目数量或调整限制"
                                ))
                
                # 递归检查
                if isinstance(value, (dict, list)):
                    self._check_structure(value, structure_rules, current_path, results)
    
    def _validate_semantics(self, yaml_data: Dict[str, Any], lines: List[str]) -> List[ValidationResult]:
        """验证语义"""
        results = []
        
        # 检查常见的语义问题
        semantic_rules = self.validation_rules.get('semantic_rules', {})
        
        # 检查端口范围
        self._check_port_ranges(yaml_data, results)
        
        # 检查资源限制
        self._check_resource_limits(yaml_data, results)
        
        # 检查环境变量
        self._check_environment_variables(yaml_data, results)
        
        # 检查密码和密钥
        self._check_secrets(yaml_data, results)
        
        return results
    
    def _check_port_ranges(self, data: Any, results: List[ValidationResult], path: str = ""):
        """检查端口范围"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if 'port' in key.lower() and isinstance(value, int):
                    if not (1 <= value <= 65535):
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"端口值 {value} 超出有效范围 (1-65535)",
                            suggestion=f"将端口设置为 1-65535 范围内的值"
                        ))
                
                self._check_port_ranges(value, results, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_port_ranges(item, results, current_path)
    
    def _check_resource_limits(self, data: Any, results: List[ValidationResult], path: str = ""):
        """检查资源限制"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if key in ['memory', 'mem'] and isinstance(value, str):
                    if not re.match(r'^\d+[KMGT]i?$', value):
                        results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"内存格式不正确: {value}",
                            suggestion="使用如 '128Mi', '1Gi' 等格式"
                        ))
                
                if key in ['cpu'] and isinstance(value, str):
                    if not re.match(r'^\d+m?$', value):
                        results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"CPU格式不正确: {value}",
                            suggestion="使用如 '100m', '0.5', '1' 等格式"
                        ))
                
                self._check_resource_limits(value, results, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_resource_limits(item, results, current_path)
    
    def _check_environment_variables(self, data: Any, results: List[ValidationResult], path: str = ""):
        """检查环境变量"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if key.lower() in ['env', 'environment', 'environment_variables'] and isinstance(value, dict):
                    for env_key, env_value in value.items():
                        if isinstance(env_value, str) and env_value.startswith('${') and env_value.endswith('}'):
                            # 检查环境变量引用
                            var_name = env_value[2:-1]
                            if not re.match(r'^[A-Z_][A-Z0-9_]*$', var_name):
                                results.append(ValidationResult(
                                    level=ValidationLevel.WARNING,
                                    message=f"环境变量名称格式不正确: {var_name}",
                                    suggestion="使用大写字母、数字和下划线"
                                ))
                
                self._check_environment_variables(value, results, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_environment_variables(item, results, current_path)
    
    def _check_secrets(self, data: Any, results: List[ValidationResult], path: str = ""):
        """检查密码和密钥"""
        sensitive_keys = ['password', 'passwd', 'secret', 'key', 'token', 'api_key']
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    if isinstance(value, str) and len(value) > 0:
                        results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"敏感信息 {key} 直接写在配置文件中",
                            suggestion="使用环境变量或密钥管理系统"
                        ))
                
                self._check_secrets(value, results, current_path)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self._check_secrets(item, results, current_path)
    
    def _validate_framework_specific(self, yaml_data: Dict[str, Any], lines: List[str]) -> List[ValidationResult]:
        """验证特定框架"""
        results = []
        
        # 检测框架类型
        framework_type = self._detect_framework_type(yaml_data)
        
        if framework_type == 'kubernetes':
            results.extend(self._validate_kubernetes(yaml_data))
        elif framework_type == 'docker-compose':
            results.extend(self._validate_docker_compose(yaml_data))
        elif framework_type == 'github-actions':
            results.extend(self._validate_github_actions(yaml_data))
        
        return results
    
    def _detect_framework_type(self, yaml_data: Dict[str, Any]) -> str:
        """检测框架类型"""
        if not isinstance(yaml_data, dict):
            return 'unknown'
        
        keys = yaml_data.keys()
        
        if 'apiVersion' in keys and 'kind' in keys:
            return 'kubernetes'
        elif 'services' in keys or 'version' in keys and 'services' in yaml_data.get('version', {}):
            return 'docker-compose'
        elif 'on' in keys and 'jobs' in keys:
            return 'github-actions'
        
        return 'unknown'
    
    def _validate_kubernetes(self, yaml_data: Dict[str, Any]) -> List[ValidationResult]:
        """验证Kubernetes配置"""
        results = []
        
        # 检查必需字段
        required_fields = ['apiVersion', 'kind', 'metadata']
        for field in required_fields:
            if field not in yaml_data:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Kubernetes资源缺少必需字段: {field}",
                    suggestion=f"添加 {field}: <value>"
                ))
        
        # 检查标签选择器
        if 'spec' in yaml_data and isinstance(yaml_data['spec'], dict):
            spec = yaml_data['spec']
            if 'selector' in spec and 'matchLabels' in spec.get('selector', {}):
                # 检查selector和template.labels是否匹配
                if 'template' in spec and 'metadata' in spec['template']:
                    template_labels = spec['template']['metadata'].get('labels', {})
                    selector_labels = spec['selector']['matchLabels']
                    
                    for key, value in selector_labels.items():
                        if template_labels.get(key) != value:
                            results.append(ValidationResult(
                                level=ValidationLevel.ERROR,
                                message=f"选择器标签 {key}={value} 与模板标签不匹配",
                                suggestion="确保选择器和模板标签一致"
                            ))
        
        return results
    
    def _validate_docker_compose(self, yaml_data: Dict[str, Any]) -> List[ValidationResult]:
        """验证Docker Compose配置"""
        results = []
        
        # 检查版本
        if 'version' in yaml_data:
            version = yaml_data['version']
            if isinstance(version, str) and not version.startswith('"') and not version.startswith("'"):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="Docker Compose版本应该用引号包围",
                    suggestion=f'将版本改为: "{version}"'
                ))
        
        # 检查服务配置
        if 'services' in yaml_data and isinstance(yaml_data['services'], dict):
            for service_name, service_config in yaml_data['services'].items():
                if isinstance(service_config, dict):
                    # 检查镜像
                    if 'image' not in service_config:
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"服务 {service_name} 缺少镜像配置",
                            suggestion=f"添加 image: <image_name>"
                        ))
                    
                    # 检查端口配置
                    if 'ports' in service_config and isinstance(service_config['ports'], list):
                        for port in service_config['ports']:
                            if isinstance(port, str) and ':' in port:
                                host_port, container_port = port.split(':', 1)
                                try:
                                    host_port_num = int(host_port)
                                    if not (1 <= host_port_num <= 65535):
                                        results.append(ValidationResult(
                                            level=ValidationLevel.ERROR,
                                            message=f"主机端口 {host_port_num} 超出有效范围",
                                            suggestion="使用 1-65535 范围内的端口"
                                        ))
                                except ValueError:
                                    results.append(ValidationResult(
                                        level=ValidationLevel.ERROR,
                                        message=f"无效的端口格式: {port}",
                                        suggestion="使用 'host:container' 格式"
                                    ))
        
        return results
    
    def _validate_github_actions(self, yaml_data: Dict[str, Any]) -> List[ValidationResult]:
        """验证GitHub Actions配置"""
        results = []
        
        # 检查必需字段
        required_fields = ['on', 'jobs']
        for field in required_fields:
            if field not in yaml_data:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"GitHub Actions工作流缺少必需字段: {field}",
                    suggestion=f"添加 {field}: <value>"
                ))
        
        # 检查作业配置
        if 'jobs' in yaml_data and isinstance(yaml_data['jobs'], dict):
            for job_name, job_config in yaml_data['jobs'].items():
                if isinstance(job_config, dict):
                    # 检查runs-on
                    if 'runs-on' not in job_config:
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"作业 {job_name} 缺少 runs-on 配置",
                            suggestion="添加 runs-on: ubuntu-latest"
                        ))
                    
                    # 检查steps
                    if 'steps' not in job_config:
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"作业 {job_name} 缺少 steps 配置",
                            suggestion="添加 steps 配置"
                        ))
                    elif isinstance(job_config['steps'], list):
                        for i, step in enumerate(job_config['steps']):
                            if isinstance(step, dict) and 'uses' not in step and 'run' not in step:
                                results.append(ValidationResult(
                                    level=ValidationLevel.ERROR,
                                    message=f"步骤 {i+1} 缺少 uses 或 run 配置",
                                    suggestion="添加 uses: <action> 或 run: <command>"
                                ))
        
        return results
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """初始化验证规则"""
        return {
            'required_fields': [],
            'type_rules': {},
            'structure_rules': {},
            'semantic_rules': {}
        }
    
    def _load_kubernetes_schemas(self) -> Dict[str, Any]:
        """加载Kubernetes模式"""
        # 简化版本，实际应该从官方API加载
        return {}
    
    def _load_docker_compose_schema(self) -> Dict[str, Any]:
        """加载Docker Compose模式"""
        # 简化版本，实际应该从官方规范加载
        return {}
    
    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """生成验证报告"""
        if not results:
            return "✅ YAML文件验证通过，未发现问题"
        
        report = ["=== YAML验证报告 ===\n"]
        
        # 按严重程度分组
        by_level = {
            ValidationLevel.ERROR: [],
            ValidationLevel.WARNING: [],
            ValidationLevel.INFO: []
        }
        
        for result in results:
            by_level[result.level].append(result)
        
        for level in [ValidationLevel.ERROR, ValidationLevel.WARNING, ValidationLevel.INFO]:
            if by_level[level]:
                level_name = level.value.upper()
                report.append(f"{level_name} ({len(by_level[level])}):")
                
                for result in by_level[level]:
                    location = ""
                    if result.line:
                        location = f" (第{result.line}行"
                        if result.column:
                            location += f", 第{result.column}列"
                        location += ")"
                    
                    report.append(f"  - {result.message}{location}")
                    
                    if result.suggestion:
                        report.append(f"    建议: {result.suggestion}")
                
                report.append("")
        
        # 总结
        error_count = len(by_level[ValidationLevel.ERROR])
        warning_count = len(by_level[ValidationLevel.WARNING])
        info_count = len(by_level[ValidationLevel.INFO])
        
        summary = f"总结: {error_count} 个错误, {warning_count} 个警告, {info_count} 个信息"
        if error_count > 0:
            summary += " ❌ 需要修复错误才能使用"
        elif warning_count > 0:
            summary += " ⚠️ 建议修复警告"
        else:
            summary += " ✅ 配置良好"
        
        report.append(summary)
        
        return '\n'.join(report)

# 使用示例
def main():
    validator = YAMLValidator()
    
    # 示例YAML内容
    yaml_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: nginx:latest
        ports:
        - containerPort: 80
    """
    
    # 验证YAML
    results = validator.validate_yaml_content(yaml_content)
    
    # 生成报告
    report = validator.generate_validation_report(results)
    print(report)

if __name__ == "__main__":
    main()
```

### YAML格式化工具
```python
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class YAMLFormatter:
    """YAML格式化工具"""
    
    def __init__(self):
        self.indent_size = 2
        self.sort_keys = False
        self.default_flow_style = False
    
    def format_yaml_file(self, file_path: str, output_path: Optional[str] = None) -> bool:
        """格式化YAML文件"""
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析YAML
            data = yaml.safe_load(content)
            
            # 格式化输出
            formatted_content = yaml.dump(
                data,
                indent=self.indent_size,
                sort_keys=self.sort_keys,
                default_flow_style=self.default_flow_style,
                allow_unicode=True,
                encoding=None
            )
            
            # 写入文件
            output_file = output_path or file_path
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return True
        
        except Exception as e:
            print(f"格式化失败: {str(e)}")
            return False
    
    def yaml_to_json(self, yaml_file: str, json_file: str) -> bool:
        """将YAML转换为JSON"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
    
    def json_to_yaml(self, json_file: str, yaml_file: str) -> bool:
        """将JSON转换为YAML"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, indent=self.indent_size, allow_unicode=True)
            
            return True
        
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False

# 使用示例
def main():
    formatter = YAMLFormatter()
    
    # 格式化YAML文件
    success = formatter.format_yaml_file("config.yaml")
    if success:
        print("YAML文件格式化完成")
    
    # 转换为JSON
    formatter.yaml_to_json("config.yaml", "config.json")
    
    # 从JSON转换回YAML
    formatter.json_to_yaml("config.json", "config_formatted.yaml")

if __name__ == "__main__":
    main()
```

## YAML最佳实践

### 文件组织
1. **逻辑分组**: 相关配置放在一起
2. **注释说明**: 添加必要的注释
3. **命名规范**: 使用一致的命名风格
4. **模块化**: 将大文件拆分为小文件

### 安全考虑
1. **敏感信息**: 使用环境变量或密钥管理
2. **权限控制**: 限制文件访问权限
3. **加密存储**: 对敏感配置进行加密
4. **审计日志**: 记录配置变更

### 版本控制
1. **Git管理**: 使用Git跟踪配置变更
2. **分支策略**: 合理使用分支管理
3. **代码审查**: 配置变更需要审查
4. **自动化测试**: 自动验证配置正确性

## 相关技能

- **kubernetes-analyzer** - Kubernetes配置分析
- **docker-analyzer** - Docker配置分析
- **config-validator** - 配置验证
- **infrastructure-as-code** - 基础设施即代码
