# API文档生成器参考文档

## API文档生成器概述

### 什么是API文档生成器
API文档生成器是一个自动化工具，用于从源代码、配置文件或现有文档中提取API信息，并生成结构化的API文档。它支持多种API类型（REST、GraphQL、gRPC等），能够自动分析代码结构、提取注释信息，并生成符合OpenAPI、RAML等标准的文档。

### 主要功能
- **源代码分析**: 自动扫描和分析源代码中的API定义
- **注释提取**: 提取Javadoc、Python docstring、JSDoc等注释信息
- **多格式支持**: 支持OpenAPI/Swagger、RAML、API Blueprint等格式
- **模板定制**: 提供可定制的文档模板和样式
- **多语言支持**: 支持多种编程语言的API文档生成
- **版本管理**: 支持API版本控制和变更追踪
- **安全配置**: 支持认证、授权等安全信息配置

## 源代码分析

### Java代码分析器
```python
# java_analyzer.py
import re
import os
import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class ApiEndpoint:
    path: str
    method: HttpMethod
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Any]
    tags: List[str]

@dataclass
class ApiModel:
    name: str
    type: str
    properties: Dict[str, Any]
    description: str
    example: Optional[Dict[str, Any]]

class JavaCodeAnalyzer:
    def __init__(self):
        self.annotation_patterns = {
            'rest_controller': re.compile(r'@RestController|@Controller'),
            'request_mapping': re.compile(r'@RequestMapping\((.*?)\)'),
            'get_mapping': re.compile(r'@GetMapping\((.*?)\)'),
            'post_mapping': re.compile(r'@PostMapping\((.*?)\)'),
            'put_mapping': re.compile(r'@PutMapping\((.*?)\)'),
            'delete_mapping': re.compile(r'@DeleteMapping\((.*?)\)'),
            'patch_mapping': re.compile(r'@PatchMapping\((.*?)\)'),
            'request_param': re.compile(r'@RequestParam\((.*?)\)'),
            'path_variable': re.compile(r'@PathVariable\((.*?)\)'),
            'request_body': re.compile(r'@RequestBody\((.*?)\)'),
            'response_body': re.compile(r'@ResponseBody'),
            'api_operation': re.compile(r'@ApiOperation\((.*?)\)'),
            'api_param': re.compile(r'@ApiParam\((.*?)\)')
        }
        
        self.type_mapping = {
            'String': 'string',
            'Integer': 'integer',
            'Long': 'integer',
            'Double': 'number',
            'Float': 'number',
            'Boolean': 'boolean',
            'Date': 'date',
            'LocalDateTime': 'datetime',
            'List': 'array',
            'Map': 'object'
        }
    
    def analyze_java_files(self, project_path: str) -> Dict[str, Any]:
        """分析Java项目文件"""
        api_info = {
            'endpoints': [],
            'models': [],
            'base_path': '',
            'info': {}
        }
        
        # 扫描Java文件
        java_files = self._find_java_files(project_path)
        
        for java_file in java_files:
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_analysis = self._analyze_java_file(content, java_file)
                
                # 合并分析结果
                api_info['endpoints'].extend(file_analysis.get('endpoints', []))
                api_info['models'].extend(file_analysis.get('models', []))
                
            except Exception as e:
                print(f"分析文件 {java_file} 失败: {e}")
        
        return api_info
    
    def _find_java_files(self, project_path: str) -> List[str]:
        """查找Java文件"""
        java_files = []
        
        for root, dirs, files in os.walk(project_path):
            # 跳过测试目录和构建目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['target', 'build', 'test']]
            
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))
        
        return java_files
    
    def _analyze_java_file(self, content: str, file_path: str) -> Dict[str, Any]:
        """分析单个Java文件"""
        analysis = {
            'endpoints': [],
            'models': [],
            'base_path': ''
        }
        
        lines = content.split('\n')
        current_class = None
        class_annotations = []
        class_methods = []
        
        # 解析类级别信息
        for i, line in enumerate(lines):
            # 检查类注解
            if self.annotation_patterns['rest_controller'].search(line):
                class_annotations.append('RestController')
            
            # 检查RequestMapping在类级别
            mapping_match = self.annotation_patterns['request_mapping'].search(line)
            if mapping_match:
                base_path = self._extract_path_from_annotation(mapping_match.group(1))
                analysis['base_path'] = base_path
            
            # 检查类定义
            if 'class ' in line and '{' in line:
                class_match = re.search(r'class\s+(\w+)', line)
                if class_match:
                    current_class = class_match.group(1)
        
        # 解析方法
        method_start = None
        method_lines = []
        
        for i, line in enumerate(lines):
            if '{' in line and any(mapping in line for mapping in ['@GetMapping', '@PostMapping', '@PutMapping', '@DeleteMapping', '@PatchMapping']):
                method_start = i
                method_lines = [line]
            elif method_start is not None:
                method_lines.append(line)
                if '}' in line and i > method_start + 1:
                    # 方法结束，分析方法
                    method_analysis = self._analyze_method(method_lines, current_class, analysis['base_path'])
                    if method_analysis:
                        analysis['endpoints'].append(method_analysis)
                    
                    method_start = None
                    method_lines = []
        
        # 分析模型类
        if current_class and not any('Controller' in anno for anno in class_annotations):
            model_analysis = self._analyze_model_class(content, current_class)
            if model_analysis:
                analysis['models'].append(model_analysis)
        
        return analysis
    
    def _extract_path_from_annotation(self, annotation_content: str) -> str:
        """从注解中提取路径"""
        # 简化的路径提取逻辑
        path_match = re.search(r'value\s*=\s*["\']([^"\']+)["\']', annotation_content)
        if path_match:
            return path_match.group(1)
        
        # 如果没有value属性，尝试直接提取
        direct_match = re.search(r'["\']([^"\']+)["\']', annotation_content)
        if direct_match:
            return direct_match.group(1)
        
        return ''
    
    def _analyze_method(self, method_lines: List[str], class_name: str, base_path: str) -> Optional[Dict[str, Any]]:
        """分析方法"""
        if not method_lines:
            return None
        
        method_content = '\n'.join(method_lines)
        
        # 确定HTTP方法
        method_type = None
        path = ''
        
        for line in method_lines:
            if '@GetMapping' in line:
                method_type = HttpMethod.GET
                path = self._extract_path_from_annotation(line)
            elif '@PostMapping' in line:
                method_type = HttpMethod.POST
                path = self._extract_path_from_annotation(line)
            elif '@PutMapping' in line:
                method_type = HttpMethod.PUT
                path = self._extract_path_from_annotation(line)
            elif '@DeleteMapping' in line:
                method_type = HttpMethod.DELETE
                path = self._extract_path_from_annotation(line)
            elif '@PatchMapping' in line:
                method_type = HttpMethod.PATCH
                path = self._extract_path_from_annotation(line)
        
        if not method_type:
            return None
        
        # 提取方法签名
        method_signature = None
        for line in method_lines:
            if 'public ' in line or 'private ' in line or 'protected ' in line:
                method_signature = line.strip()
                break
        
        if not method_signature:
            return None
        
        # 提取方法名和参数
        method_match = re.search(r'(\w+)\s*\((.*?)\)', method_signature)
        if not method_match:
            return None
        
        method_name = method_match.group(1)
        params_str = method_match.group(2)
        
        # 分析参数
        parameters = []
        request_body = None
        
        if params_str.strip() and params_str.strip() != 'void':
            param_list = [p.strip() for p in params_str.split(',')]
            
            for param in param_list:
                if param:
                    param_analysis = self._analyze_parameter(param, method_lines)
                    if param_analysis:
                        if param_analysis.get('in') == 'body':
                            request_body = param_analysis
                        else:
                            parameters.append(param_analysis)
        
        # 提取注释
        description = self._extract_method_description(method_lines)
        
        # 构建完整路径
        full_path = base_path + path
        
        return {
            'path': full_path,
            'method': method_type.value,
            'operation_id': method_name,
            'summary': description,
            'description': description,
            'parameters': parameters,
            'request_body': request_body,
            'responses': {
                '200': {
                    'description': 'Success'
                }
            },
            'tags': [class_name] if class_name else []
        }
    
    def _analyze_parameter(self, param_str: str, method_lines: List[str]) -> Optional[Dict[str, Any]]:
        """分析参数"""
        # 解析参数类型和名称
        param_parts = param_str.split()
        if len(param_parts) < 2:
            return None
        
        param_type = param_parts[-2]
        param_name = param_parts[-1].rstrip(';')
        
        # 检查参数注解
        param_location = 'query'
        required = False
        
        for line in method_lines:
            if '@RequestParam' in line and param_name in line:
                param_location = 'query'
                required_match = re.search(r'required\s*=\s*(true|false)', line)
                if required_match:
                    required = required_match.group(1) == 'true'
            elif '@PathVariable' in line and param_name in line:
                param_location = 'path'
                required = True
            elif '@RequestBody' in line and param_name in line:
                param_location = 'body'
                required = True
        
        # 映射类型
        schema_type = self.type_mapping.get(param_type, 'string')
        
        return {
            'name': param_name,
            'in': param_location,
            'required': required,
            'schema': {
                'type': schema_type
            }
        }
    
    def _extract_method_description(self, method_lines: List[str]) -> str:
        """提取方法描述"""
        description = ''
        
        # 查找方法上方的注释
        for i, line in enumerate(method_lines):
            if '@' in line and any(mapping in line for mapping in ['@GetMapping', '@PostMapping', '@PutMapping', '@DeleteMapping', '@PatchMapping']):
                # 向上查找注释
                for j in range(i-1, -1, -1):
                    prev_line = method_lines[j].strip()
                    if prev_line.startswith('/**') or prev_line.startswith('/*'):
                        # 找到注释开始
                        comment_lines = []
                        for k in range(j, len(method_lines)):
                            comment_line = method_lines[k].strip()
                            if '*/' in comment_line:
                                comment_lines.append(comment_line.replace('*/', ''))
                                break
                            comment_lines.append(comment_line.replace('*', '').replace('/', '').strip())
                        
                        description = ' '.join([line for line in comment_lines if line])
                        break
                break
        
        return description
    
    def _analyze_model_class(self, content: str, class_name: str) -> Optional[Dict[str, Any]]:
        """分析模型类"""
        # 简化的模型分析
        properties = {}
        
        lines = content.split('\n')
        in_class = False
        
        for line in lines:
            if 'class ' in line and class_name in line:
                in_class = True
                continue
            
            if in_class and '}' in line:
                break
            
            if in_class and 'private ' in line and ';' in line:
                # 提取属性
                prop_match = re.search(r'private\s+(\w+)\s+(\w+)', line)
                if prop_match:
                    prop_type = prop_match.group(1)
                    prop_name = prop_match.group(2)
                    
                    schema_type = self.type_mapping.get(prop_type, 'string')
                    
                    properties[prop_name] = {
                        'type': schema_type
                    }
        
        if properties:
            return {
                'name': class_name,
                'type': 'object',
                'properties': properties,
                'description': f'{class_name} model'
            }
        
        return None

# 使用示例
analyzer = JavaCodeAnalyzer()

# 分析Java项目
try:
    api_info = analyzer.analyze_java_files('/path/to/java/project')
    
    print(f"发现 {len(api_info['endpoints'])} 个API端点")
    print(f"发现 {len(api_info['models'])} 个数据模型")
    
    for endpoint in api_info['endpoints'][:3]:  # 显示前3个端点
        print(f"端点: {endpoint['method']} {endpoint['path']}")
        print(f"描述: {endpoint['summary']}")
        print(f"参数数量: {len(endpoint['parameters'])}")
        print("-" * 50)
    
except Exception as e:
    print(f"分析失败: {e}")
```

### Python代码分析器
```python
# python_analyzer.py
import ast
import re
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

class PythonCodeAnalyzer:
    def __init__(self):
        self.framework_patterns = {
            'flask': [
                r'@app\.route\(',
                r'@bp\.route\(',
                r'@api\.route\(',
                r'flask'
            ],
            'django': [
                r'@api_view\(',
                r'@action\(',
                r'@detail_route\(',
                r'django'
            ],
            'fastapi': [
                r'@app\.get\(',
                r'@app\.post\(',
                r'@app\.put\(',
                r'@app\.delete\(',
                r'@router\.get\(',
                r'@router\.post\(',
                r'fastapi'
            ]
        }
        
        self.type_mapping = {
            'str': 'string',
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object',
            'datetime': 'datetime',
            'date': 'date'
        }
    
    def analyze_python_files(self, project_path: str) -> Dict[str, Any]:
        """分析Python项目文件"""
        api_info = {
            'endpoints': [],
            'models': [],
            'framework': None,
            'info': {}
        }
        
        # 检测框架
        api_info['framework'] = self._detect_framework(project_path)
        
        # 扫描Python文件
        python_files = self._find_python_files(project_path)
        
        for python_file in python_files:
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_analysis = self._analyze_python_file(content, python_file, api_info['framework'])
                
                # 合并分析结果
                api_info['endpoints'].extend(file_analysis.get('endpoints', []))
                api_info['models'].extend(file_analysis.get('models', []))
                
            except Exception as e:
                print(f"分析文件 {python_file} 失败: {e}")
        
        return api_info
    
    def _detect_framework(self, project_path: str) -> Optional[str]:
        """检测Web框架"""
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        for framework, patterns in self.framework_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    return framework
                    except:
                        continue
        
        return None
    
    def _find_python_files(self, project_path: str) -> List[str]:
        """查找Python文件"""
        python_files = []
        
        for root, dirs, files in os.walk(project_path):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _analyze_python_file(self, content: str, file_path: str, framework: Optional[str]) -> Dict[str, Any]:
        """分析单个Python文件"""
        analysis = {
            'endpoints': [],
            'models': []
        }
        
        try:
            tree = ast.parse(content)
            
            if framework == 'flask':
                analysis = self._analyze_flask_file(tree, content)
            elif framework == 'django':
                analysis = self._analyze_django_file(tree, content)
            elif framework == 'fastapi':
                analysis = self._analyze_fastapi_file(tree, content)
            else:
                # 通用分析
                analysis = self._analyze_generic_file(tree, content)
                
        except SyntaxError as e:
            print(f"语法错误在文件 {file_path}: {e}")
        
        return analysis
    
    def _analyze_flask_file(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """分析Flask文件"""
        analysis = {
            'endpoints': [],
            'models': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数装饰器
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr == 'route':
                                endpoint = self._analyze_flask_route(node, decorator)
                                if endpoint:
                                    analysis['endpoints'].append(endpoint)
        
        return analysis
    
    def _analyze_flask_route(self, node: ast.FunctionDef, decorator: ast.Call) -> Optional[Dict[str, Any]]:
        """分析Flask路由"""
        # 获取路由路径
        path = '/'
        methods = ['GET']
        
        if decorator.args:
            path_arg = decorator.args[0]
            if isinstance(path_arg, ast.Str):
                path = path_arg.s
            elif isinstance(path_arg, ast.Constant):
                path = path_arg.value
        
        # 检查methods参数
        for keyword in decorator.keywords:
            if keyword.arg == 'methods':
                if isinstance(keyword.value, ast.List):
                    methods = []
                    for elt in keyword.value.elts:
                        if isinstance(elt, ast.Str):
                            methods.append(elt.s)
                        elif isinstance(elt, ast.Constant):
                            methods.append(elt.value)
        
        # 提取函数文档字符串
        description = ast.get_docstring(node) or ''
        
        # 分析参数
        parameters = []
        request_body = None
        
        for arg in node.args.args:
            param_name = arg.arg
            
            # 简化的参数分析
            param_type = 'string'
            param_location = 'query'
            
            # 检查是否有类型注解
            if arg.annotation:
                param_type = self._get_type_from_annotation(arg.annotation)
            
            parameters.append({
                'name': param_name,
                'in': param_location,
                'required': True,
                'schema': {
                    'type': param_type
                }
            })
        
        return {
            'path': path,
            'method': methods[0] if methods else 'GET',
            'operation_id': node.name,
            'summary': description.split('\n')[0] if description else '',
            'description': description,
            'parameters': parameters,
            'request_body': request_body,
            'responses': {
                '200': {
                    'description': 'Success'
                }
            },
            'tags': []
        }
    
    def _analyze_fastapi_file(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """分析FastAPI文件"""
        analysis = {
            'endpoints': [],
            'models': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数装饰器
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            method = decorator.func.attr.lower()
                            if method in ['get', 'post', 'put', 'delete', 'patch']:
                                endpoint = self._analyze_fastapi_route(node, decorator, method.upper())
                                if endpoint:
                                    analysis['endpoints'].append(endpoint)
            
            elif isinstance(node, ast.ClassDef):
                # 检查是否是Pydantic模型
                if self._is_pydantic_model(node):
                    model = self._analyze_pydantic_model(node)
                    if model:
                        analysis['models'].append(model)
        
        return analysis
    
    def _analyze_fastapi_route(self, node: ast.FunctionDef, decorator: ast.Call, method: str) -> Optional[Dict[str, Any]]:
        """分析FastAPI路由"""
        # 获取路由路径
        path = '/'
        
        if decorator.args:
            path_arg = decorator.args[0]
            if isinstance(path_arg, ast.Str):
                path = path_arg.s
            elif isinstance(path_arg, ast.Constant):
                path = path_arg.value
        
        # 提取函数文档字符串
        description = ast.get_docstring(node) or ''
        
        # 分析参数
        parameters = []
        request_body = None
        
        for arg in node.args.args:
            param_name = arg.arg
            
            # 检查参数类型和位置
            param_type = 'string'
            param_location = 'query'
            required = True
            
            if arg.annotation:
                param_type = self._get_type_from_annotation(arg.annotation)
                
                # 检查是否是请求体参数
                if isinstance(arg.annotation, ast.Name):
                    if param_name in ['body', 'data', 'item']:
                        param_location = 'body'
                        request_body = {
                            'required': required,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': param_type
                                    }
                                }
                            }
                        }
                        continue
            
            if param_location != 'body':
                parameters.append({
                    'name': param_name,
                    'in': param_location,
                    'required': required,
                    'schema': {
                        'type': param_type
                    }
                })
        
        return {
            'path': path,
            'method': method,
            'operation_id': node.name,
            'summary': description.split('\n')[0] if description else '',
            'description': description,
            'parameters': parameters,
            'request_body': request_body,
            'responses': {
                '200': {
                    'description': 'Success'
                }
            },
            'tags': []
        }
    
    def _is_pydantic_model(self, node: ast.ClassDef) -> bool:
        """检查是否是Pydantic模型"""
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id == 'BaseModel':
                    return True
        return False
    
    def _analyze_pydantic_model(self, node: ast.ClassDef) -> Optional[Dict[str, Any]]:
        """分析Pydantic模型"""
        properties = {}
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                # 获取属性名
                if isinstance(item.target, ast.Name):
                    prop_name = item.target.id
                    
                    # 获取类型
                    prop_type = self._get_type_from_annotation(item.annotation)
                    
                    properties[prop_name] = {
                        'type': prop_type
                    }
        
        if properties:
            return {
                'name': node.name,
                'type': 'object',
                'properties': properties,
                'description': f'{node.name} model'
            }
        
        return None
    
    def _analyze_django_file(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """分析Django文件"""
        # Django分析实现
        return {
            'endpoints': [],
            'models': []
        }
    
    def _analyze_generic_file(self, tree: ast.AST, content: str) -> Dict[str, Any]:
        """通用文件分析"""
        analysis = {
            'endpoints': [],
            'models': []
        }
        
        # 通用分析逻辑
        return analysis
    
    def _get_type_from_annotation(self, annotation: ast.AST) -> str:
        """从类型注解获取类型"""
        if isinstance(annotation, ast.Name):
            return self.type_mapping.get(annotation.id, 'string')
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                if base_type == 'List':
                    return 'array'
                elif base_type == 'Dict':
                    return 'object'
        
        return 'string'

# 使用示例
analyzer = PythonCodeAnalyzer()

# 分析Python项目
try:
    api_info = analyzer.analyze_python_files('/path/to/python/project')
    
    print(f"检测到框架: {api_info['framework']}")
    print(f"发现 {len(api_info['endpoints'])} 个API端点")
    print(f"发现 {len(api_info['models'])} 个数据模型")
    
    for endpoint in api_info['endpoints'][:3]:  # 显示前3个端点
        print(f"端点: {endpoint['method']} {endpoint['path']}")
        print(f"描述: {endpoint['summary']}")
        print(f"参数数量: {len(endpoint['parameters'])}")
        print("-" * 50)
    
except Exception as e:
    print(f"分析失败: {e}")
```

## OpenAPI文档生成

### OpenAPI生成器
```python
# openapi_generator.py
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime

class OpenAPIGenerator:
    def __init__(self):
        self.openapi_version = "3.0.3"
        self.default_info = {
            "title": "API Documentation",
            "version": "1.0.0",
            "description": "Generated API documentation"
        }
    
    def generate_openapi_spec(self, api_info: Dict[str, Any], format: str = 'json') -> str:
        """生成OpenAPI规范"""
        openapi_spec = {
            "openapi": self.openapi_version,
            "info": self._generate_info_section(api_info),
            "servers": self._generate_servers_section(api_info),
            "paths": self._generate_paths_section(api_info),
            "components": self._generate_components_section(api_info),
            "tags": self._generate_tags_section(api_info)
        }
        
        if format.lower() == 'json':
            return json.dumps(openapi_spec, indent=2, ensure_ascii=False)
        elif format.lower() == 'yaml':
            return yaml.dump(openapi_spec, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _generate_info_section(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成信息部分"""
        info = self.default_info.copy()
        
        # 从API信息中更新
        if 'info' in api_info:
            api_info_data = api_info['info']
            info.update({
                k: v for k, v in api_info_data.items() 
                if k in ['title', 'version', 'description', 'termsOfService', 'contact', 'license']
            })
        
        return info
    
    def _generate_servers_section(self, api_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成服务器部分"""
        servers = []
        
        # 默认服务器
        servers.append({
            "url": "http://localhost:8080",
            "description": "Development server"
        })
        
        # 从API信息中添加服务器
        if 'servers' in api_info:
            servers.extend(api_info['servers'])
        
        return servers
    
    def _generate_paths_section(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成路径部分"""
        paths = {}
        
        for endpoint in api_info.get('endpoints', []):
            path = endpoint['path']
            method = endpoint['method'].lower()
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = self._generate_operation(endpoint)
        
        return paths
    
    def _generate_operation(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """生成操作定义"""
        operation = {
            "operationId": endpoint.get('operation_id', ''),
            "summary": endpoint.get('summary', ''),
            "description": endpoint.get('description', ''),
            "tags": endpoint.get('tags', []),
            "parameters": self._generate_parameters(endpoint.get('parameters', [])),
            "responses": self._generate_responses(endpoint.get('responses', {}))
        }
        
        # 添加请求体
        if endpoint.get('request_body'):
            operation['requestBody'] = endpoint['request_body']
        
        # 添加安全要求
        if endpoint.get('security'):
            operation['security'] = endpoint['security']
        
        return operation
    
    def _generate_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成参数定义"""
        openapi_params = []
        
        for param in parameters:
            openapi_param = {
                "name": param['name'],
                "in": param['in'],
                "required": param.get('required', False),
                "schema": param.get('schema', {"type": "string"})
            }
            
            if 'description' in param:
                openapi_param['description'] = param['description']
            
            openapi_params.append(openapi_param)
        
        return openapi_params
    
    def _generate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """生成响应定义"""
        openapi_responses = {}
        
        for status_code, response in responses.items():
            openapi_response = {
                "description": response.get('description', '')
            }
            
            if 'content' in response:
                openapi_response['content'] = response['content']
            
            if 'headers' in response:
                openapi_response['headers'] = response['headers']
            
            openapi_responses[str(status_code)] = openapi_response
        
        return openapi_responses
    
    def _generate_components_section(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成组件部分"""
        components = {}
        
        # 生成模式定义
        schemas = {}
        for model in api_info.get('models', []):
            schemas[model['name']] = self._generate_schema(model)
        
        if schemas:
            components['schemas'] = schemas
        
        # 生成安全方案
        security_schemes = {}
        if 'security' in api_info:
            for scheme_name, scheme_config in api_info['security'].items():
                security_schemes[scheme_name] = scheme_config
        
        if security_schemes:
            components['securitySchemes'] = security_schemes
        
        return components
    
    def _generate_schema(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """生成模式定义"""
        schema = {
            "type": model.get('type', 'object'),
            "description": model.get('description', '')
        }
        
        if 'properties' in model:
            schema['properties'] = model['properties']
        
        if 'required' in model:
            schema['required'] = model['required']
        
        if 'example' in model:
            schema['example'] = model['example']
        
        return schema
    
    def _generate_tags_section(self, api_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成标签部分"""
        tags = []
        tag_names = set()
        
        # 从端点中收集标签
        for endpoint in api_info.get('endpoints', []):
            for tag in endpoint.get('tags', []):
                tag_names.add(tag)
        
        # 生成标签定义
        for tag_name in sorted(tag_names):
            tags.append({
                "name": tag_name,
                "description": f"Operations related to {tag_name}"
            })
        
        return tags

# 使用示例
generator = OpenAPIGenerator()

# 生成OpenAPI规范
try:
    # 假设已经通过代码分析获得了api_info
    api_info = {
        'endpoints': [
            {
                'path': '/api/users',
                'method': 'GET',
                'operation_id': 'getUsers',
                'summary': 'Get all users',
                'description': 'Retrieve a list of all users',
                'parameters': [
                    {
                        'name': 'page',
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'integer'}
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Success',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {'$ref': '#/components/schemas/User'}
                                }
                            }
                        }
                    }
                },
                'tags': ['users']
            }
        ],
        'models': [
            {
                'name': 'User',
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'email': {'type': 'string'}
                },
                'required': ['id', 'name', 'email'],
                'description': 'User model'
            }
        ]
    }
    
    # 生成JSON格式
    openapi_json = generator.generate_openapi_spec(api_info, 'json')
    print("OpenAPI JSON:")
    print(openapi_json)
    
    # 生成YAML格式
    openapi_yaml = generator.generate_openapi_spec(api_info, 'yaml')
    print("\nOpenAPI YAML:")
    print(openapi_yaml)
    
except Exception as e:
    print(f"生成失败: {e}")
```

## HTML文档生成

### HTML文档生成器
```python
# html_generator.py
from jinja2 import Template
import os
from typing import Dict, List, Any

class HTMLDocumentationGenerator:
    def __init__(self):
        self.template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism.min.css" rel="stylesheet">
    <style>
        .sidebar {
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
            width: 250px;
            background-color: #f8f9fa;
            border-right: 1px solid #dee2e6;
            overflow-y: auto;
        }
        .main-content {
            margin-left: 250px;
            padding: 20px;
        }
        .endpoint-card {
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }
        .method-badge {
            font-size: 0.8em;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            color: white;
        }
        .method-get { background-color: #28a745; }
        .method-post { background-color: #007bff; }
        .method-put { background-color: #ffc107; color: #000; }
        .method-delete { background-color: #dc3545; }
        .method-patch { background-color: #6f42c1; }
        .parameter-table th, .response-table th {
            background-color: #f8f9fa;
        }
        .code-example {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
        }
        .nav-link {
            color: #495057;
            padding: 0.5rem 1rem;
        }
        .nav-link:hover {
            color: #007bff;
            background-color: #e9ecef;
        }
        .nav-link.active {
            color: #007bff;
            background-color: #e9ecef;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="p-3">
            <h5>{{ title }}</h5>
            <hr>
            <nav class="nav flex-column">
                <a class="nav-link" href="#overview">概览</a>
                {% for tag in tags %}
                <a class="nav-link" href="#{{ tag.name | lower | replace(' ', '-') }}">{{ tag.name }}</a>
                {% endfor %}
                <a class="nav-link" href="#models">数据模型</a>
            </nav>
        </div>
    </div>
    
    <div class="main-content">
        <div class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <h1>{{ title }}</h1>
                    <p class="lead">{{ description }}</p>
                    
                    <section id="overview">
                        <h2>概览</h2>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">API版本</h5>
                                        <p class="card-text">{{ version }}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">基础URL</h5>
                                        <p class="card-text">{{ base_url }}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">端点数量</h5>
                                        <p class="card-text">{{ endpoints | length }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                    
                    {% for tag in tags %}
                    <section id="{{ tag.name | lower | replace(' ', '-') }}">
                        <h2>{{ tag.name }}</h2>
                        {% for endpoint in tag.endpoints %}
                        <div class="endpoint-card">
                            <div class="card-header">
                                <span class="method-badge method-{{ endpoint.method | lower }}">{{ endpoint.method }}</span>
                                <strong>{{ endpoint.path }}</strong>
                                <button class="btn btn-sm btn-outline-primary float-end" type="button" data-bs-toggle="collapse" data-bs-target="#endpoint-{{ loop.index0 }}">
                                    展开
                                </button>
                            </div>
                            <div class="collapse show" id="endpoint-{{ loop.index0 }}">
                                <div class="card-body">
                                    <h5>{{ endpoint.summary }}</h5>
                                    <p>{{ endpoint.description }}</p>
                                    
                                    {% if endpoint.parameters %}
                                    <h6>参数</h6>
                                    <table class="table table-sm parameter-table">
                                        <thead>
                                            <tr>
                                                <th>名称</th>
                                                <th>位置</th>
                                                <th>类型</th>
                                                <th>必需</th>
                                                <th>描述</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for param in endpoint.parameters %}
                                            <tr>
                                                <td><code>{{ param.name }}</code></td>
                                                <td>{{ param.in }}</td>
                                                <td>{{ param.schema.type }}</td>
                                                <td>{{ "是" if param.required else "否" }}</td>
                                                <td>{{ param.description | default("") }}</td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                    {% endif %}
                                    
                                    {% if endpoint.request_body %}
                                    <h6>请求体</h6>
                                    <div class="code-example">
                                        <pre><code class="language-json">{{ endpoint.request_body.example | default("{}") | tojson_pretty }}</code></pre>
                                    </div>
                                    {% endif %}
                                    
                                    <h6>响应</h6>
                                    {% for status, response in endpoint.responses.items() %}
                                    <div class="mb-3">
                                        <strong>{{ status }}</strong> - {{ response.description }}
                                        {% if response.content %}
                                        <div class="code-example">
                                            <pre><code class="language-json">{{ response.content["application/json"].example | default("{}") | tojson_pretty }}</code></pre>
                                        </div>
                                        {% endif %}
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </section>
                    {% endfor %}
                    
                    <section id="models">
                        <h2>数据模型</h2>
                        {% for model in models %}
                        <div class="card mb-3">
                            <div class="card-header">
                                <h5>{{ model.name }}</h5>
                            </div>
                            <div class="card-body">
                                <p>{{ model.description }}</p>
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>属性</th>
                                            <th>类型</th>
                                            <th>必需</th>
                                            <th>描述</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for prop_name, prop in model.properties.items() %}
                                        <tr>
                                            <td><code>{{ prop_name }}</code></td>
                                            <td>{{ prop.type }}</td>
                                            <td>{{ "是" if prop_name in model.get('required', []) else "否" }}</td>
                                            <td>{{ prop.description | default("") }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        {% endfor %}
                    </section>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>
        """
    
    def generate_html_documentation(self, api_info: Dict[str, Any], output_path: str) -> bool:
        """生成HTML文档"""
        try:
            # 准备模板数据
            template_data = self._prepare_template_data(api_info)
            
            # 渲染模板
            template = Template(self.template)
            html_content = template.render(**template_data)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"生成HTML文档失败: {e}")
            return False
    
    def _prepare_template_data(self, api_info: Dict[str, Any]) -> Dict[str, Any]:
        """准备模板数据"""
        # 基础信息
        info = api_info.get('info', {})
        
        template_data = {
            'title': info.get('title', 'API Documentation'),
            'description': info.get('description', ''),
            'version': info.get('version', '1.0.0'),
            'base_url': info.get('base_url', 'http://localhost:8080'),
            'endpoints': api_info.get('endpoints', []),
            'models': api_info.get('models', []),
            'tags': self._group_endpoints_by_tags(api_info.get('endpoints', []))
        }
        
        return template_data
    
    def _group_endpoints_by_tags(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按标签分组端点"""
        tags = {}
        
        for endpoint in endpoints:
            endpoint_tags = endpoint.get('tags', ['default'])
            
            for tag in endpoint_tags:
                if tag not in tags:
                    tags[tag] = {
                        'name': tag,
                        'endpoints': []
                    }
                
                tags[tag]['endpoints'].append(endpoint)
        
        # 转换为列表并排序
        tag_list = sorted(tags.values(), key=lambda x: x['name'])
        
        # 对每个标签内的端点按路径排序
        for tag in tag_list:
            tag['endpoints'].sort(key=lambda x: x['path'])
        
        return tag_list

# 使用示例
generator = HTMLDocumentationGenerator()

# 生成HTML文档
try:
    # 假设已经通过代码分析获得了api_info
    api_info = {
        'info': {
            'title': '用户管理API',
            'description': '用户管理系统的API接口文档',
            'version': '1.0.0',
            'base_url': 'http://localhost:8080/api'
        },
        'endpoints': [
            {
                'path': '/users',
                'method': 'GET',
                'summary': '获取用户列表',
                'description': '获取所有用户的列表信息',
                'tags': ['用户管理'],
                'parameters': [
                    {
                        'name': 'page',
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'integer'},
                        'description': '页码'
                    },
                    {
                        'name': 'size',
                        'in': 'query',
                        'required': False,
                        'schema': {'type': 'integer'},
                        'description': '每页数量'
                    }
                ],
                'responses': {
                    '200': {
                        'description': '成功获取用户列表',
                        'content': {
                            'application/json': {
                                'example': {
                                    'users': [
                                        {'id': 1, 'name': '张三', 'email': 'zhangsan@example.com'},
                                        {'id': 2, 'name': '李四', 'email': 'lisi@example.com'}
                                    ],
                                    'total': 2
                                }
                            }
                        }
                    }
                }
            },
            {
                'path': '/users',
                'method': 'POST',
                'summary': '创建用户',
                'description': '创建新的用户',
                'tags': ['用户管理'],
                'request_body': {
                    'example': {
                        'name': '王五',
                        'email': 'wangwu@example.com',
                        'password': 'password123'
                    }
                },
                'responses': {
                    '201': {
                        'description': '用户创建成功',
                        'content': {
                            'application/json': {
                                'example': {
                                    'id': 3,
                                    'name': '王五',
                                    'email': 'wangwu@example.com',
                                    'created_at': '2023-01-01T00:00:00Z'
                                }
                            }
                        }
                    }
                }
            }
        ],
        'models': [
            {
                'name': 'User',
                'description': '用户模型',
                'properties': {
                    'id': {'type': 'integer', 'description': '用户ID'},
                    'name': {'type': 'string', 'description': '用户名'},
                    'email': {'type': 'string', 'description': '邮箱地址'},
                    'created_at': {'type': 'datetime', 'description': '创建时间'}
                },
                'required': ['id', 'name', 'email']
            }
        ]
    }
    
    success = generator.generate_html_documentation(api_info, 'api_documentation.html')
    print(f"HTML文档生成成功: {success}")
    
except Exception as e:
    print(f"生成失败: {e}")
```

## 集成和部署

### CI/CD集成脚本
```bash
#!/bin/bash
# generate_docs.sh - API文档生成脚本

set -e

# 配置变量
PROJECT_PATH=${1:-"."}
OUTPUT_DIR=${2:-"./docs"}
FORMAT=${3:-"html"}
CONFIG_FILE=${4:-"docs_config.json"}

echo "开始生成API文档..."
echo "项目路径: $PROJECT_PATH"
echo "输出目录: $OUTPUT_DIR"
echo "文档格式: $FORMAT"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 生成文档
echo "分析源代码..."
python3 generate_docs.py \
    --project_path "$PROJECT_PATH" \
    --output_dir "$OUTPUT_DIR" \
    --format "$FORMAT" \
    --config "$CONFIG_FILE"

# 检查生成结果
if [ $? -eq 0 ]; then
    echo "文档生成成功!"
    
    # 如果是HTML格式，可以启动本地服务器预览
    if [ "$FORMAT" = "html" ]; then
        echo "启动本地服务器预览文档..."
        cd "$OUTPUT_DIR"
        python3 -m http.server 8080
    fi
else
    echo "文档生成失败!"
    exit 1
fi
```

### GitHub Actions工作流
```yaml
# .github/workflows/docs.yml
name: Generate API Documentation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Generate documentation
      run: |
        python generate_docs.py \
          --project_path . \
          --output_dir docs \
          --format html \
          --config docs_config.json
    
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
```

## 参考资源

### 官方文档
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)
- [Swagger Documentation](https://swagger.io/docs/)
- [ReDoc Documentation](https://redocly.com/docs/)
- [Stoplight Studio](https://stoplight.io/studio)

### 代码分析工具
- [JavaParser](https://javaparser.org/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [TypeScript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)
- [Roslyn (C# Compiler Platform)](https://github.com/dotnet/roslyn)

### 文档生成工具
- [Swagger Codegen](https://github.com/swagger-api/swagger-codegen)
- [OpenAPI Generator](https://github.com/OpenAPITools/openapi-generator)
- [Redoc](https://github.com/Redocly/redoc)
- [Slate](https://github.com/slatedoc/slate)

### 模板和样式
- [Bootstrap](https://getbootstrap.com/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://github.com/Redocly/redoc)
- [Docusaurus](https://docusaurus.io/)
