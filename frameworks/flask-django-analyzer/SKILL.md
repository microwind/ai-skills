---
name: Flask/Django分析器
description: "当审查Flask/Django代码、规划项目结构、调试框架问题或优化框架性能时，分析Flask/Django Web框架的最佳实践和架构模式。"
license: MIT
---

# Flask/Django分析器技能

## 概述
Web框架实现快速开发，但不良模式会创建维护噩梦。

**核心原则**: Web框架实现快速开发，但不良模式会创建维护噩梦。

## 何时使用

**始终:**
- 审查Flask/Django代码
- 规划Flask/Django项目结构
- 调试框架问题
- 优化框架性能
- 架构设计评审
- 安全性分析

**触发短语:**
- "分析Flask代码"
- "Django项目架构"
- "Web框架最佳实践"
- "Flask/Django性能优化"
- "框架安全检查"
- "项目结构规划"

## Flask/Django分析功能

### 代码质量
- MVC/MVT模式检查
- 蓝图/应用结构分析
- 模型设计验证
- 视图函数审查
- 模板使用检查

### 性能分析
- 数据库查询优化
- 缓存策略分析
- 中间件性能检查
- 静态文件优化
- 会话管理评估

### 安全检查
- CSRF保护验证
- SQL注入防护
- XSS漏洞检测
- 认证授权检查
- 敏感数据保护

## 常见Flask/Django问题

### 架构问题
```
问题:
项目结构混乱，违反框架设计原则

错误示例:
- 所有代码放在一个文件
- 模型与视图耦合
- 缺少模块化设计
- 业务逻辑分散

解决方案:
1. 遵循MVC/MVT架构
2. 使用蓝图/应用分离
3. 创建清晰的模块结构
4. 实现关注点分离
```

### 数据库问题
```
问题:
数据库设计不当，查询效率低下

错误示例:
- 缺少索引优化
- N+1查询问题
- 事务管理不当
- 数据模型设计不合理

解决方案:
1. 优化数据库索引
2. 使用select_related/prefetch_related
3. 合理管理事务
4. 规范数据模型设计
```

### 安全问题
```
问题:
Web应用存在安全漏洞

错误示例:
- 缺少CSRF保护
- SQL注入风险
- XSS攻击漏洞
- 认证机制不完善

解决方案:
1. 启用CSRF保护
2. 使用ORM防止SQL注入
3. 模板自动转义
4. 实现完善的认证系统
```

## 代码实现示例

### Flask代码分析器
```python
import ast
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FlaskIssue:
    """Flask代码问题"""
    file_path: str
    line_number: int
    column: int
    severity: str  # error, warning, info
    message: str
    rule_id: str
    suggestion: Optional[str] = None

@dataclass
class RouteMetrics:
    """路由指标"""
    endpoint: str
    methods: List[str]
    line_number: int
    has_auth: bool
    has_validation: bool
    complexity: int
    docstring: bool

@dataclass
class ModelMetrics:
    """模型指标"""
    name: str
    fields_count: int
    relationships_count: int
    has_indexes: bool
    has_validators: bool
    docstring: bool

class FlaskAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.issues: List[FlaskIssue] = []
        self.route_metrics: List[RouteMetrics] = []
        self.model_metrics: List[ModelMetrics] = []
        self.config_files: List[str] = []
        self.template_files: List[str] = []
        
    def analyze_project(self) -> Dict[str, Any]:
        """分析整个Flask项目"""
        results = {
            'project_structure': self.analyze_project_structure(),
            'routes': self.analyze_routes(),
            'models': self.analyze_models(),
            'templates': self.analyze_templates(),
            'config': self.analyze_config(),
            'security': self.analyze_security(),
            'performance': self.analyze_performance(),
            'issues': self.issues,
            'summary': self.generate_summary()
        }
        
        return results
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """分析项目结构"""
        structure = {
            'has_app_factory': False,
            'has_blueprints': False,
            'has_config_separation': False,
            'has_tests': False,
            'has_docs': False,
            'directory_structure': {},
            'issues': []
        }
        
        # 检查目录结构
        for root, dirs, files in os.walk(self.project_root):
            rel_path = os.path.relpath(root, self.project_root)
            structure['directory_structure'][rel_path] = {
                'dirs': dirs,
                'files': files
            }
            
            # 检查关键文件和目录
            if 'app.py' in files or '__init__.py' in files:
                with open(os.path.join(root, 'app.py' if 'app.py' in files else '__init__.py'), 'r') as f:
                    content = f.read()
                    if 'create_app' in content:
                        structure['has_app_factory'] = True
            
            if 'blueprints' in dirs or any('blueprint' in f.lower() for f in files):
                structure['has_blueprints'] = True
            
            if 'config.py' in files or 'settings.py' in files:
                structure['has_config_separation'] = True
            
            if 'tests' in dirs or 'test' in dirs:
                structure['has_tests'] = True
            
            if 'docs' in dirs or 'doc' in dirs:
                structure['has_docs'] = True
        
        # 生成结构建议
        if not structure['has_app_factory']:
            structure['issues'].append({
                'type': 'structure',
                'message': '建议使用应用工厂模式',
                'suggestion': '创建create_app函数实现应用工厂'
            })
        
        if not structure['has_blueprints']:
            structure['issues'].append({
                'type': 'structure',
                'message': '建议使用蓝图组织代码',
                'suggestion': '将功能模块拆分为蓝图'
            })
        
        return structure
    
    def analyze_routes(self) -> Dict[str, Any]:
        """分析路由定义"""
        route_files = self.find_files(['app.py', '__init__.py', 'views.py', 'routes.py'])
        
        for file_path in route_files:
            self.analyze_route_file(file_path)
        
        return {
            'total_routes': len(self.route_metrics),
            'routes': self.route_metrics,
            'issues': [issue for issue in self.issues if issue.rule_id.startswith('route_')]
        }
    
    def analyze_route_file(self, file_path: str) -> None:
        """分析单个路由文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否是路由函数
                    decorators = [d for d in node.decorator_list 
                                if isinstance(d, ast.Call) and 
                                isinstance(d.func, ast.Name) and 
                                d.func.id in ['route', 'api_route']]
                    
                    if decorators:
                        self.analyze_route_function(node, file_path, decorators)
                        
        except Exception as e:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=0,
                column=0,
                severity='error',
                message=f'解析路由文件失败: {e}',
                rule_id='parse_error'
            ))
    
    def analyze_route_function(self, node: ast.FunctionDef, file_path: str, decorators: List[ast.Call]) -> None:
        """分析路由函数"""
        # 获取路由信息
        route_info = self.extract_route_info(decorators[0])
        
        # 检查认证
        has_auth = self.check_route_auth(node)
        
        # 检查参数验证
        has_validation = self.check_route_validation(node)
        
        # 计算复杂度
        complexity = self.calculate_complexity(node)
        
        # 检查文档字符串
        has_docstring = ast.get_docstring(node) is not None
        
        metrics = RouteMetrics(
            endpoint=route_info.get('path', '/'),
            methods=route_info.get('methods', ['GET']),
            line_number=node.lineno,
            has_auth=has_auth,
            has_validation=has_validation,
            complexity=complexity,
            docstring=has_docstring
        )
        
        self.route_metrics.append(metrics)
        
        # 检查问题
        if not has_auth and any(method in ['POST', 'PUT', 'DELETE'] for method in metrics.methods):
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='warning',
                message=f'路由{metrics.endpoint}缺少认证保护',
                rule_id='route_missing_auth',
                suggestion='添加认证装饰器'
            ))
        
        if not has_validation and any(method in ['POST', 'PUT', 'PATCH'] for method in metrics.methods):
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='info',
                message=f'路由{metrics.endpoint}缺少参数验证',
                rule_id='route_missing_validation',
                suggestion='添加请求参数验证'
            ))
        
        if complexity > 10:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='warning',
                message=f'路由函数{node.name}复杂度过高({complexity})',
                rule_id='route_high_complexity',
                suggestion='拆分复杂逻辑到服务层'
            ))
    
    def extract_route_info(self, decorator: ast.Call) -> Dict[str, Any]:
        """提取路由信息"""
        info = {'path': '/', 'methods': ['GET']}
        
        if decorator.args:
            if isinstance(decorator.args[0], ast.Str):
                info['path'] = decorator.args[0].s
            elif isinstance(decorator.args[0], ast.Constant):
                info['path'] = decorator.args[0].value
        
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
                    info['methods'] = methods
        
        return info
    
    def check_route_auth(self, node: ast.FunctionDef) -> bool:
        """检查路由认证"""
        # 检查装饰器中的认证
        auth_decorators = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in ['login_required', 'auth_required', 'jwt_required']:
                    auth_decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in ['login_required', 'auth_required', 'jwt_required']:
                        auth_decorators.append(decorator.func.id)
        
        return len(auth_decorators) > 0
    
    def check_route_validation(self, node: ast.FunctionDef) -> bool:
        """检查参数验证"""
        # 简化实现：检查是否使用验证库
        validation_patterns = [
            'request.form.get',
            'request.json.get',
            'request.args.get',
            'validate',
            'schema',
            'marshmallow',
            'pydantic'
        ]
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if any(pattern in child.func.attr for pattern in validation_patterns):
                        return True
                elif isinstance(child.func, ast.Name):
                    if child.func.id in validation_patterns:
                        return True
        
        return False
    
    def analyze_models(self) -> Dict[str, Any]:
        """分析数据模型"""
        model_files = self.find_files(['models.py', 'model.py'])
        
        for file_path in model_files:
            self.analyze_model_file(file_path)
        
        return {
            'total_models': len(self.model_metrics),
            'models': self.model_metrics,
            'issues': [issue for issue in self.issues if issue.rule_id.startswith('model_')]
        }
    
    def analyze_model_file(self, file_path: str) -> None:
        """分析模型文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否是模型类
                    if self.is_model_class(node):
                        self.analyze_model_class(node, file_path)
                        
        except Exception as e:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=0,
                column=0,
                severity='error',
                message=f'解析模型文件失败: {e}',
                rule_id='parse_error'
            ))
    
    def is_model_class(self, node: ast.ClassDef) -> bool:
        """检查是否是模型类"""
        # 检查基类
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in ['db.Model', 'Model', 'SQLAlchemyModel']:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr == 'Model':
                    return True
        
        # 检查类装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == 'dataclass':
                    return True
        
        return False
    
    def analyze_model_class(self, node: ast.ClassDef, file_path: str) -> None:
        """分析模型类"""
        fields_count = 0
        relationships_count = 0
        has_indexes = False
        has_validators = False
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        # 检查字段类型
                        if isinstance(item.value, ast.Call):
                            if isinstance(item.value.func, ast.Name):
                                if item.value.func.id in ['Column', 'Field', 'String', 'Integer']:
                                    fields_count += 1
                                    
                                    # 检查索引
                                    for keyword in item.value.keywords:
                                        if keyword.arg == 'index' and keyword.value.value is True:
                                            has_indexes = True
                            
                            elif isinstance(item.value.func, ast.Attribute):
                                if item.value.func.attr in ['Column', 'Field', 'relationship']:
                                    if item.value.func.attr == 'relationship':
                                        relationships_count += 1
                                    else:
                                        fields_count += 1
        
        # 检查文档字符串
        has_docstring = ast.get_docstring(node) is not None
        
        metrics = ModelMetrics(
            name=node.name,
            fields_count=fields_count,
            relationships_count=relationships_count,
            has_indexes=has_indexes,
            has_validators=has_validators,
            docstring=has_docstring
        )
        
        self.model_metrics.append(metrics)
        
        # 检查问题
        if fields_count > 20:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='warning',
                message=f'模型{node.name}字段过多({fields_count})',
                rule_id='model_too_many_fields',
                suggestion='考虑拆分模型或使用继承'
            ))
        
        if not has_docstring:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='info',
                message=f'模型{node.name}缺少文档字符串',
                rule_id='model_missing_docstring',
                suggestion='添加模型文档说明'
            ))
    
    def analyze_templates(self) -> Dict[str, Any]:
        """分析模板文件"""
        template_dirs = ['templates', 'template']
        
        for template_dir in template_dirs:
            template_path = os.path.join(self.project_root, template_dir)
            if os.path.exists(template_path):
                self.analyze_template_directory(template_path)
        
        return {
            'template_files': len(self.template_files),
            'issues': [issue for issue in self.issues if issue.rule_id.startswith('template_')]
        }
    
    def analyze_template_directory(self, template_dir: str) -> None:
        """分析模板目录"""
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith(('.html', '.htm', '.jinja', '.j2')):
                    file_path = os.path.join(root, file)
                    self.analyze_template_file(file_path)
    
    def analyze_template_file(self, file_path: str) -> None:
        """分析模板文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.template_files.append(file_path)
            
            # 检查模板问题
            self.check_template_security(file_path, content)
            self.check_template_structure(file_path, content)
            
        except Exception as e:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=0,
                column=0,
                severity='error',
                message=f'解析模板文件失败: {e}',
                rule_id='template_parse_error'
            ))
    
    def check_template_security(self, file_path: str, content: str) -> None:
        """检查模板安全问题"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 检查XSS风险
            if '|safe' in line and '{{' in line:
                self.issues.append(FlaskIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=line.find('|safe'),
                    severity='warning',
                    message='使用|safe可能导致XSS攻击',
                    rule_id='template_xss_risk',
                    suggestion='确保内容安全或使用其他过滤方法'
                ))
            
            # 检查未转义输出
            if '{{' in line and '}}' in line and '|safe' not in line and 'url_for' not in line:
                # 这是一个简化的检查，实际需要更复杂的解析
                pass
    
    def check_template_structure(self, file_path: str, content: str) -> None:
        """检查模板结构"""
        lines = content.split('\n')
        
        # 检查是否继承基础模板
        has_extends = any('extends' in line for line in lines)
        
        if not has_extends and file_path.endswith('.html'):
            # 检查是否是基础模板
            is_base_template = any('block' in line for line in lines)
            
            if not is_base_template:
                self.issues.append(FlaskIssue(
                    file_path=file_path,
                    line_number=1,
                    column=0,
                    severity='info',
                    message='建议使用模板继承',
                    rule_id='template_missing_extends',
                    suggestion='创建基础模板并使用extends继承'
                ))
    
    def analyze_config(self) -> Dict[str, Any]:
        """分析配置文件"""
        config_files = self.find_files(['config.py', 'settings.py', 'app.py', '__init__.py'])
        
        for file_path in config_files:
            self.analyze_config_file(file_path)
        
        return {
            'config_files': len(self.config_files),
            'issues': [issue for issue in self.issues if issue.rule_id.startswith('config_')]
        }
    
    def analyze_config_file(self, file_path: str) -> None:
        """分析配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查配置问题
            self.check_config_security(file_path, content)
            self.check_config_structure(file_path, content)
            
        except Exception as e:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=0,
                column=0,
                severity='error',
                message=f'解析配置文件失败: {e}',
                rule_id='config_parse_error'
            ))
    
    def check_config_security(self, file_path: str, content: str) -> None:
        """检查配置安全问题"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 检查硬编码密钥
            if 'SECRET_KEY' in line and '=' in line:
                value = line.split('=')[1].strip()
                if value.startswith('"') or value.startswith("'"):
                    self.issues.append(FlaskIssue(
                        file_path=file_path,
                        line_number=line_num,
                        column=line.find('='),
                        severity='error',
                        message='密钥硬编码在代码中',
                        rule_id='config_hardcoded_secret',
                        suggestion='使用环境变量存储密钥'
                    ))
            
            # 检查调试模式
            if 'DEBUG' in line and '= True' in line:
                self.issues.append(FlaskIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=line.find('='),
                    severity='warning',
                    message='生产环境不应开启调试模式',
                    rule_id='config_debug_enabled',
                    suggestion='使用环境变量控制调试模式'
                ))
    
    def check_config_structure(self, file_path: str, content: str) -> None:
        """检查配置结构"""
        # 检查是否使用环境变量
        has_env_vars = 'os.environ' in content or 'environ' in content
        
        if not has_env_vars:
            self.issues.append(FlaskIssue(
                file_path=file_path,
                line_number=1,
                column=0,
                severity='info',
                message='建议使用环境变量管理配置',
                rule_id='config_missing_env_vars',
                suggestion='使用python-dotenv或os.environ管理配置'
            ))
    
    def analyze_security(self) -> Dict[str, Any]:
        """分析安全问题"""
        security_issues = []
        
        # 检查CSRF保护
        if not self.has_csrf_protection():
            security_issues.append({
                'type': 'csrf',
                'severity': 'warning',
                'message': '缺少CSRF保护',
                'suggestion': '启用Flask-WTF或Flask-SeaSurf'
            })
        
        # 检查安全头
        if not self.has_security_headers():
            security_issues.append({
                'type': 'headers',
                'severity': 'info',
                'message': '缺少安全HTTP头',
                'suggestion': '使用Flask-Talisman配置安全头'
            })
        
        return {
            'security_issues': security_issues,
            'score': self.calculate_security_score(security_issues)
        }
    
    def has_csrf_protection(self) -> bool:
        """检查是否有CSRF保护"""
        # 简化实现：检查是否导入相关库
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if 'csrf' in content.lower() or 'sea_surf' in content:
                            return True
                    except:
                        continue
        return False
    
    def has_security_headers(self) -> bool:
        """检查是否有安全头配置"""
        # 简化实现
        return False
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析性能问题"""
        performance_issues = []
        
        # 检查缓存配置
        if not self.has_cache_config():
            performance_issues.append({
                'type': 'cache',
                'severity': 'info',
                'message': '缺少缓存配置',
                'suggestion': '配置Redis或Memcached缓存'
            })
        
        # 检查数据库连接池
        if not self.has_connection_pool():
            performance_issues.append({
                'type': 'database',
                'severity': 'info',
                'message': '缺少数据库连接池',
                'suggestion': '配置数据库连接池'
            })
        
        return {
            'performance_issues': performance_issues,
            'score': self.calculate_performance_score(performance_issues)
        }
    
    def has_cache_config(self) -> bool:
        """检查是否有缓存配置"""
        # 简化实现
        return False
    
    def has_connection_pool(self) -> bool:
        """检查是否有数据库连接池"""
        # 简化实现
        return False
    
    def calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def find_files(self, filenames: List[str]) -> List[str]:
        """查找指定文件"""
        found_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file in filenames:
                    found_files.append(os.path.join(root, file))
        
        return found_files
    
    def calculate_security_score(self, issues: List[Dict]) -> int:
        """计算安全评分"""
        score = 100
        for issue in issues:
            if issue['severity'] == 'error':
                score -= 30
            elif issue['severity'] == 'warning':
                score -= 15
            elif issue['severity'] == 'info':
                score -= 5
        return max(0, score)
    
    def calculate_performance_score(self, issues: List[Dict]) -> int:
        """计算性能评分"""
        score = 100
        for issue in issues:
            if issue['severity'] == 'error':
                score -= 25
            elif issue['severity'] == 'warning':
                score -= 10
            elif issue['severity'] == 'info':
                score -= 5
        return max(0, score)
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        total_issues = len(self.issues)
        error_count = len([i for i in self.issues if i.severity == 'error'])
        warning_count = len([i for i in self.issues if i.severity == 'warning'])
        info_count = len([i for i in self.issues if i.severity == 'info'])
        
        return {
            'total_issues': total_issues,
            'errors': error_count,
            'warnings': warning_count,
            'info': info_count,
            'score': max(0, 100 - error_count * 10 - warning_count * 5 - info_count),
            'recommendations': self.generate_recommendations()
        }
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        # 基于问题类型生成建议
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue.rule_id] += 1
        
        if issue_counts['config_hardcoded_secret'] > 0:
            recommendations.append({
                'priority': 'critical',
                'message': '修复硬编码密钥问题',
                'action': '使用环境变量存储敏感配置'
            })
        
        if issue_counts['route_missing_auth'] > 2:
            recommendations.append({
                'priority': 'high',
                'message': '加强路由认证保护',
                'action': '为敏感路由添加认证装饰器'
            })
        
        if issue_counts['model_too_many_fields'] > 0:
            recommendations.append({
                'priority': 'medium',
                'message': '优化模型设计',
                'action': '拆分大模型或使用继承关系'
            })
        
        return recommendations

# Django分析器
class DjangoAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.issues: List[FlaskIssue] = []
        
    def analyze_project(self) -> Dict[str, Any]:
        """分析Django项目"""
        return {
            'settings': self.analyze_settings(),
            'urls': self.analyze_urls(),
            'views': self.analyze_views(),
            'models': self.analyze_models(),
            'admin': self.analyze_admin(),
            'issues': self.issues
        }
    
    def analyze_settings(self) -> Dict[str, Any]:
        """分析Django设置"""
        settings_files = ['settings.py', 'settings/', 'settings']
        issues = []
        
        for settings_file in settings_files:
            settings_path = os.path.join(self.project_root, settings_file)
            if os.path.exists(settings_path):
                # 分析设置文件
                pass
        
        return {'issues': issues}
    
    def analyze_urls(self) -> Dict[str, Any]:
        """分析URL配置"""
        url_files = ['urls.py']
        issues = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file == 'urls.py':
                    # 分析URL配置
                    pass
        
        return {'issues': issues}
    
    def analyze_views(self) -> Dict[str, Any]:
        """分析视图"""
        view_files = ['views.py']
        issues = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file == 'views.py':
                    # 分析视图
                    pass
        
        return {'issues': issues}
    
    def analyze_models(self) -> Dict[str, Any]:
        """分析模型"""
        model_files = ['models.py']
        issues = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file == 'models.py':
                    # 分析模型
                    pass
        
        return {'issues': issues}
    
    def analyze_admin(self) -> Dict[str, Any]:
        """分析管理后台"""
        admin_files = ['admin.py']
        issues = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file == 'admin.py':
                    # 分析管理后台
                    pass
        
        return {'issues': issues}

# 使用示例
def main():
    project_path = './my_flask_app'
    
    # Flask分析
    flask_analyzer = FlaskAnalyzer(project_path)
    flask_result = flask_analyzer.analyze_project()
    
    print("Flask分析结果:")
    print(f"总问题数: {flask_result['summary']['total_issues']}")
    print(f"评分: {flask_result['summary']['score']}")
    
    # Django分析
    django_analyzer = DjangoAnalyzer(project_path)
    django_result = django_analyzer.analyze_project()
    
    print("\nDjango分析结果:")
    print(f"总问题数: {len(django_result['issues'])}")

if __name__ == '__main__':
    main()
```

### Flask/Django性能分析器
```python
import time
import psutil
import threading
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from functools import wraps

@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    metadata: Dict[str, Any]

class FlaskDjangoPerformanceAnalyzer:
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 5) -> None:
        """开始性能监控"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: int) -> None:
        """监控循环"""
        while self.is_monitoring:
            self._collect_system_metrics()
            time.sleep(interval)
    
    def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent()
        self.record_metric('cpu_usage', cpu_percent, '%')
        
        # 内存使用
        memory = psutil.virtual_memory()
        self.record_metric('memory_usage', memory.percent, '%')
        self.record_metric('memory_available', memory.available, 'bytes')
        
        # 磁盘使用
        disk = psutil.disk_usage('/')
        self.record_metric('disk_usage', disk.percent, '%')
        self.record_metric('disk_free', disk.free, 'bytes')
    
    def record_metric(self, name: str, value: float, unit: str, metadata: Dict[str, Any] = None) -> None:
        """记录性能指标"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        self.metrics.append(metric)
        
        # 保持最近1000条记录
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def profile_view_function(self, view_name: str) -> Callable:
        """视图函数性能分析装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    
                    # 记录指标
                    self.record_metric(f'view_{view_name}_duration', 
                                    end_time - start_time, 'seconds',
                                    {'success': success, 'error': error})
                    
                    self.record_metric(f'view_{view_name}_memory', 
                                    end_memory - start_memory, 'bytes',
                                    {'success': success, 'error': error})
                
                return result
            
            return wrapper
        return decorator
    
    def profile_database_query(self, query_name: str) -> Callable:
        """数据库查询性能分析装饰器"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    query_count = getattr(result, 'query_count', 1)
                    success = True
                except Exception as e:
                    query_count = 0
                    success = False
                    raise
                finally:
                    end_time = time.time()
                    
                    # 记录查询指标
                    self.record_metric(f'db_{query_name}_duration', 
                                    end_time - start_time, 'seconds',
                                    {'query_count': query_count, 'success': success})
                    
                    self.record_metric(f'db_{query_name}_queries', 
                                    query_count, 'count',
                                    {'success': success})
                
                return result
            
            return wrapper
        return decorator
    
    def analyze_request_performance(self, request_data: Dict[str, Any]) -> None:
        """分析请求性能"""
        if 'response_time' in request_data:
            self.record_metric('request_response_time', 
                            request_data['response_time'], 'seconds',
                            {'endpoint': request_data.get('endpoint', 'unknown')})
        
        if 'status_code' in request_data:
            self.record_metric('request_status', 
                            request_data['status_code'], 'count',
                            {'endpoint': request_data.get('endpoint', 'unknown')})
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        report = {
            'timestamp': time.time(),
            'summary': self._generate_summary(),
            'metrics_by_type': self._group_metrics_by_type(),
            'performance_trends': self._analyze_trends(),
            'recommendations': self._generate_performance_recommendations()
        }
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成性能摘要"""
        if not self.metrics:
            return {'message': 'No metrics available'}
        
        # 按类型分组指标
        metrics_by_type = defaultdict(list)
        for metric in self.metrics:
            metrics_by_type[metric.name].append(metric)
        
        summary = {}
        
        # 计算各类指标的平均值
        for metric_type, metrics in metrics_by_type.items():
            if metrics:
                values = [m.value for m in metrics]
                summary[metric_type] = {
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values),
                    'unit': metrics[0].unit
                }
        
        return summary
    
    def _group_metrics_by_type(self) -> Dict[str, List[PerformanceMetric]]:
        """按类型分组指标"""
        grouped = defaultdict(list)
        for metric in self.metrics:
            grouped[metric.name].append(metric)
        return dict(grouped)
    
    def _analyze_trends(self) -> Dict[str, str]:
        """分析性能趋势"""
        trends = {}
        
        grouped = self._group_metrics_by_type()
        for metric_type, metrics in grouped.items():
            if len(metrics) >= 2:
                # 简单趋势分析：比较最近和最早的值
                recent = metrics[-1].value
                earliest = metrics[0].value
                
                if recent > earliest * 1.1:
                    trends[metric_type] = 'increasing'
                elif recent < earliest * 0.9:
                    trends[metric_type] = 'decreasing'
                else:
                    trends[metric_type] = 'stable'
        
        return trends
    
    def _generate_performance_recommendations(self) -> List[Dict[str, str]]:
        """生成性能建议"""
        recommendations = []
        summary = self._generate_summary()
        
        # CPU使用率建议
        if 'cpu_usage' in summary and summary['cpu_usage']['average'] > 80:
            recommendations.append({
                'type': 'cpu',
                'priority': 'high',
                'message': 'CPU使用率过高',
                'suggestion': '优化算法或增加服务器资源'
            })
        
        # 内存使用建议
        if 'memory_usage' in summary and summary['memory_usage']['average'] > 85:
            recommendations.append({
                'type': 'memory',
                'priority': 'high',
                'message': '内存使用率过高',
                'suggestion': '检查内存泄漏或增加内存'
            })
        
        # 请求响应时间建议
        request_metrics = [m for m in self.metrics if 'request_response_time' in m.name]
        if request_metrics:
            avg_response_time = sum(m.value for m in request_metrics) / len(request_metrics)
            if avg_response_time > 2.0:
                recommendations.append({
                    'type': 'response_time',
                    'priority': 'medium',
                    'message': '响应时间过长',
                    'suggestion': '优化数据库查询或使用缓存'
                })
        
        return recommendations

# 使用示例
def main():
    analyzer = FlaskDjangoPerformanceAnalyzer()
    
    # 开始监控
    analyzer.start_monitoring()
    
    # 模拟一些操作
    @analyzer.profile_view_function('home')
    def home_view():
        time.sleep(0.1)
        return "Hello World"
    
    @analyzer.profile_database_query('user_query')
    def get_users():
        time.sleep(0.05)
        return []
    
    # 执行一些操作
    home_view()
    get_users()
    
    # 模拟请求
    analyzer.analyze_request_performance({
        'endpoint': '/home',
        'response_time': 0.15,
        'status_code': 200
    })
    
    # 等待收集指标
    time.sleep(2)
    
    # 停止监控
    analyzer.stop_monitoring()
    
    # 生成报告
    report = analyzer.generate_performance_report()
    print("性能报告:", report)

if __name__ == '__main__':
    main()
```

## Flask/Django最佳实践

### 项目结构
1. **应用工厂**: 使用create_app模式
2. **蓝图组织**: 按功能模块分离
3. **配置分离**: 环境变量管理配置
4. **测试覆盖**: 完整的测试套件

### 数据库设计
1. **模型规范**: 遵循数据库设计原则
2. **索引优化**: 合理创建索引
3. **查询优化**: 避免N+1问题
4. **事务管理**: 正确使用事务

### 安全实践
1. **CSRF保护**: 启用跨站请求伪造保护
2. **输入验证**: 验证所有用户输入
3. **SQL注入防护**: 使用ORM参数化查询
4. **认证授权**: 实现完善的权限控制

### 性能优化
1. **缓存策略**: 合理使用Redis/Memcached
2. **数据库优化**: 连接池和查询优化
3. **静态文件**: CDN加速和压缩
4. **异步任务**: 使用Celery处理耗时任务

## 相关技能

- **python-analyzer** - Python代码分析
- **sql-optimizer** - SQL优化
- **web-security** - Web安全
- **api-design** - API设计
