---
name: Flask轻量级应用
description: "当开发Flask应用时，分析路由设计，优化中间件配置，解决性能问题。验证API架构，设计RESTful服务，和最佳实践。"
license: MIT
---

# Flask轻量级应用技能

## 概述
Flask是Python最流行的轻量级Web框架。不当的Flask应用设计会导致性能问题、安全漏洞和维护困难。在开发Flask应用前需要仔细分析架构需求。

**核心原则**: 好的Flask应用应该简洁高效、安全可靠、易于扩展。坏的Flask应用会导致代码混乱、性能瓶颈和安全风险。

## 何时使用

**始终:**
- 设计RESTful API时
- 构建Web应用后端时
- 实现微服务架构时
- 处理HTTP请求路由时
- 配置中间件和错误处理时

**触发短语:**
- "Flask应用设计"
- "Python Web开发"
- "Flask路由配置"
- "RESTful服务架构"
- "Flask性能优化"
- "Python微框架"

## Flask轻量级应用功能

### 路由设计
- RESTful路由规划
- 动态路由参数
- 路由中间件配置
- 错误处理路由
- API版本管理

### 中间件管理
- 请求处理中间件
- 身份验证中间件
- 日志记录中间件
- 错误处理中间件
- 自定义中间件开发

### 模板引擎
- Jinja2模板配置
- 模板继承设计
- 静态文件管理
- 模板缓存优化
- 前端集成

### 数据库集成
- SQLAlchemy配置
- 数据库迁移管理
- 连接池优化
- 查询性能优化
- 事务处理

## 常见Flask问题

### 路由设计不当
```
问题:
路由结构混乱，缺乏一致性

错误示例:
- 路由命名不规范
- 缺乏RESTful设计
- 参数验证缺失
- 错误处理不统一

解决方案:
1. 遵循RESTful设计原则
2. 统一路由命名规范
3. 实施参数验证装饰器
4. 建立统一错误处理机制
```

### 中间件滥用
```
问题:
中间件配置过多或顺序不当

错误示例:
- 不必要的中间件加载
- 中间件执行顺序错误
- 同步中间件阻塞
- 中间件依赖混乱

解决方案:
1. 只加载必要的中间件
2. 正确配置中间件顺序
3. 使用异步中间件
4. 清理中间件依赖关系
```

### 性能瓶颈
```
问题:
应用响应慢，并发能力差

错误示例:
- 同步阻塞操作
- 内存泄漏
- 数据库连接未复用
- 缺乏缓存机制

解决方案:
1. 使用异步操作避免阻塞
2. 实施内存监控和清理
3. 配置数据库连接池
4. 添加适当的缓存策略
```

## 代码实现示例

### Flask应用分析器
```python
import os
import ast
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class FlaskRoute:
    """Flask路由信息"""
    method: str
    path: str
    function_name: str
    file: str
    line: int
    issues: List[str]

@dataclass
class FlaskMiddleware:
    """Flask中间件信息"""
    name: str
    type: str
    file: str
    line: int
    issues: List[str]

@dataclass
class FlaskIssue:
    """Flask问题"""
    severity: str  # critical, high, medium, low
    type: str
    file: str
    message: str
    suggestion: str
    line: Optional[int] = None

class FlaskAppAnalyzer:
    def __init__(self, app_path: str):
        self.app_path = app_path
        self.routes: List[FlaskRoute] = []
        self.middlewares: List[FlaskMiddleware] = []
        self.issues: List[FlaskIssue] = []
        
    def analyze_application(self) -> Dict[str, Any]:
        """分析Flask应用"""
        try:
            # 扫描Python文件
            python_files = self.find_python_files()
            
            for file_path in python_files:
                self.analyze_python_file(file_path)
            
            # 分析requirements.txt
            self.analyze_requirements()
            
            # 分析配置文件
            self.analyze_config_files()
            
            # 生成分析报告
            return self.generate_report()
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def find_python_files(self) -> List[str]:
        """查找Python文件"""
        python_files = []
        
        for root, dirs, files in os.walk(self.app_path):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def analyze_python_file(self, file_path: str) -> None:
        """分析Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 查找Flask应用
            flask_apps = self.find_flask_apps(tree, file_path)
            
            # 分析路由
            self.analyze_routes(tree, file_path, flask_apps)
            
            # 分析中间件
            self.analyze_middlewares(tree, file_path, flask_apps)
            
            # 分析代码质量
            self.analyze_code_quality(tree, file_path)
            
        except Exception as e:
            self.issues.append(FlaskIssue(
                severity='medium',
                type='analysis',
                file=file_path,
                message=f'文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def find_flask_apps(self, tree: ast.AST, file_path: str) -> List[str]:
        """查找Flask应用实例"""
        flask_apps = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # 检查是否是Flask实例
                        if (isinstance(node.value, ast.Call) and 
                            isinstance(node.value.func, ast.Name) and 
                            node.value.func.id == 'Flask'):
                            flask_apps.append(target.id)
                        elif (isinstance(node.value, ast.Call) and 
                              isinstance(node.value.func, ast.Attribute) and 
                              node.value.func.attr == 'Flask'):
                            flask_apps.append(target.id)
        
        return flask_apps
    
    def analyze_routes(self, tree: ast.AST, file_path: str, flask_apps: List[str]) -> None:
        """分析路由定义"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查路由装饰器
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch']):
                    
                    # 获取路由信息
                    route_info = self.extract_route_info(node, file_path, flask_apps)
                    if route_info:
                        self.routes.append(route_info)
                        self.validate_route(route_info)
    
    def extract_route_info(self, node: ast.Call, file_path: str, flask_apps: List[str]) -> Optional[FlaskRoute]:
        """提取路由信息"""
        try:
            # 获取HTTP方法
            method = 'GET'
            if node.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                method = node.func.attr.upper()
            
            # 获取路径
            path = '/'
            if node.args and isinstance(node.args[0], ast.Str):
                path = node.args[0].s
            elif node.args and isinstance(node.args[0], ast.Constant):
                path = node.args[0].value
            
            # 查找装饰的函数
            function_name = None
            line = node.lineno
            
            # 向上查找装饰的函数定义
            parent = self.find_parent_function(node)
            if parent and isinstance(parent, ast.FunctionDef):
                function_name = parent.name
            
            if function_name:
                return FlaskRoute(
                    method=method,
                    path=path,
                    function_name=function_name,
                    file=file_path,
                    line=line,
                    issues=[]
                )
        
        except Exception:
            pass
        
        return None
    
    def find_parent_function(self, node: ast.AST) -> Optional[ast.AST]:
        """查找父级函数定义"""
        # 这是一个简化的实现，实际需要更复杂的AST遍历
        return None
    
    def validate_route(self, route: FlaskRoute) -> None:
        """验证路由设计"""
        # 检查RESTful规范
        if not self.is_restful_path(route.path):
            route.issues.append('路径不符合RESTful规范')
            self.issues.append(FlaskIssue(
                severity='medium',
                type='design',
                file=route.file,
                message=f'路由路径不符合RESTful规范: {route.method} {route.path}',
                suggestion='使用名词复数形式，避免动词',
                line=route.line
            ))
        
        # 检查参数验证
        if self.has_parameters(route.path) and not self.has_validation(route.function_name):
            route.issues.append('缺少参数验证')
            self.issues.append(FlaskIssue(
                severity='high',
                type='security',
                file=route.file,
                message=f'路由缺少参数验证: {route.method} {route.path}',
                suggestion='添加参数验证装饰器或验证逻辑',
                line=route.line
            ))
    
    def is_restful_path(self, path: str) -> bool:
        """检查路径是否符合RESTful规范"""
        # 检查是否包含动词
        verbs = ['get', 'post', 'put', 'delete', 'patch', 'create', 'update', 'remove']
        path_parts = path.strip('/').split('/')
        
        for part in path_parts:
            if part.lower() in verbs:
                return False
        
        return True
    
    def has_parameters(self, path: str) -> bool:
        """检查路径是否包含参数"""
        return '<' in path and '>' in path
    
    def has_validation(self, function_name: str) -> bool:
        """检查函数是否有验证逻辑"""
        # 简化实现，实际需要分析函数体
        return False
    
    def analyze_middlewares(self, tree: ast.AST, file_path: str, flask_apps: List[str]) -> None:
        """分析中间件配置"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查中间件注册
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr == 'before_request'):
                    
                    middleware_info = FlaskMiddleware(
                        name='before_request',
                        type='request',
                        file=file_path,
                        line=node.lineno,
                        issues=[]
                    )
                    
                    self.middlewares.append(middleware_info)
                
                elif (isinstance(node.func, ast.Attribute) and 
                      node.func.attr == 'after_request'):
                    
                    middleware_info = FlaskMiddleware(
                        name='after_request',
                        type='response',
                        file=file_path,
                        line=node.lineno,
                        issues=[]
                    )
                    
                    self.middlewares.append(middleware_info)
                
                elif (isinstance(node.func, ast.Attribute) and 
                      node.func.attr == 'errorhandler'):
                    
                    middleware_info = FlaskMiddleware(
                        name='errorhandler',
                        type='error',
                        file=file_path,
                        line=node.lineno,
                        issues=[]
                    )
                    
                    self.middlewares.append(middleware_info)
    
    def analyze_code_quality(self, tree: ast.AST, file_path: str) -> None:
        """分析代码质量"""
        # 检查函数复杂度
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self.calculate_complexity(node)
                if complexity > 10:
                    self.issues.append(FlaskIssue(
                        severity='medium',
                        type='quality',
                        file=file_path,
                        message=f'函数复杂度过高: {node.name} (复杂度: {complexity})',
                        suggestion='拆分复杂函数为多个小函数',
                        line=node.lineno
                    ))
        
        # 检查异常处理
        self.check_exception_handling(tree, file_path)
    
    def calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def check_exception_handling(self, tree: ast.AST, file_path: str) -> None:
        """检查异常处理"""
        has_try_except = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                has_try_except = True
                break
        
        if not has_try_except:
            self.issues.append(FlaskIssue(
                severity='medium',
                type='error_handling',
                file=file_path,
                message='文件缺少异常处理',
                suggestion='添加try-except块处理可能的异常'
            ))
    
    def analyze_requirements(self) -> None:
        """分析requirements.txt"""
        requirements_path = os.path.join(self.app_path, 'requirements.txt')
        
        if not os.path.exists(requirements_path):
            self.issues.append(FlaskIssue(
                severity='high',
                type='dependency',
                file='requirements.txt',
                message='缺少requirements.txt文件',
                suggestion='创建requirements.txt文件并添加必要依赖'
            ))
            return
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            # 检查必要依赖
            required_deps = ['flask', 'gunicorn']
            security_deps = ['flask-cors', 'flask-helmet']
            performance_deps = ['redis', 'flask-caching']
            
            for dep in required_deps:
                if not any(dep.lower() in req.lower() for req in requirements):
                    self.issues.append(FlaskIssue(
                        severity='high',
                        type='dependency',
                        file='requirements.txt',
                        message=f'缺少必要依赖: {dep}',
                        suggestion=f'添加{dep}到requirements.txt'
                    ))
            
            for dep in security_deps:
                if not any(dep.lower() in req.lower() for req in requirements):
                    self.issues.append(FlaskIssue(
                        severity='medium',
                        type='security',
                        file='requirements.txt',
                        message=f'建议添加安全依赖: {dep}',
                        suggestion=f'添加{dep}增强应用安全性'
                    ))
            
            for dep in performance_deps:
                if not any(dep.lower() in req.lower() for req in requirements):
                    self.issues.append(FlaskIssue(
                        severity='low',
                        type='performance',
                        file='requirements.txt',
                        message=f'建议添加性能依赖: {dep}',
                        suggestion=f'添加{dep}提升应用性能'
                    ))
        
        except Exception as e:
            self.issues.append(FlaskIssue(
                severity='medium',
                type='analysis',
                file='requirements.txt',
                message=f'requirements.txt分析失败: {e}',
                suggestion='检查文件格式和编码'
            ))
    
    def analyze_config_files(self) -> None:
        """分析配置文件"""
        config_files = ['config.py', 'settings.py', '.env']
        
        for config_file in config_files:
            config_path = os.path.join(self.app_path, config_file)
            
            if os.path.exists(config_path):
                self.analyze_config_file(config_path)
        
        # 检查是否有配置文件
        if not any(os.path.exists(os.path.join(self.app_path, f)) for f in config_files):
            self.issues.append(FlaskIssue(
                severity='medium',
                type='configuration',
                file='config',
                message='缺少配置文件',
                suggestion='创建config.py或.env文件管理配置'
            ))
    
    def analyze_config_file(self, config_path: str) -> None:
        """分析配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查敏感信息
            sensitive_keys = ['password', 'secret', 'key', 'token', 'api_key']
            
            for key in sensitive_keys:
                if key in content.lower():
                    self.issues.append(FlaskIssue(
                        severity='high',
                        type='security',
                        file=config_path,
                        message=f'配置文件包含敏感信息: {key}',
                        suggestion='使用环境变量或密钥管理服务'
                    ))
        
        except Exception as e:
            self.issues.append(FlaskIssue(
                severity='low',
                type='analysis',
                file=config_path,
                message=f'配置文件分析失败: {e}',
                suggestion='检查文件格式和编码'
            ))
    
    def generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        summary = {
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'high_issues': len([i for i in self.issues if i.severity == 'high']),
            'medium_issues': len([i for i in self.issues if i.severity == 'medium']),
            'low_issues': len([i for i in self.issues if i.severity == 'low']),
            'total_routes': len(self.routes),
            'total_middlewares': len(self.middlewares)
        }
        
        recommendations = self.generate_recommendations()
        
        return {
            'summary': summary,
            'routes': [self.route_to_dict(r) for r in self.routes],
            'middlewares': [self.middleware_to_dict(m) for m in self.middlewares],
            'issues': [self.issue_to_dict(i) for i in self.issues],
            'recommendations': recommendations,
            'health_score': self.calculate_health_score(summary)
        }
    
    def route_to_dict(self, route: FlaskRoute) -> Dict[str, Any]:
        """将路由转换为字典"""
        return {
            'method': route.method,
            'path': route.path,
            'function_name': route.function_name,
            'file': route.file,
            'line': route.line,
            'issues': route.issues
        }
    
    def middleware_to_dict(self, middleware: FlaskMiddleware) -> Dict[str, Any]:
        """将中间件转换为字典"""
        return {
            'name': middleware.name,
            'type': middleware.type,
            'file': middleware.file,
            'line': middleware.line,
            'issues': middleware.issues
        }
    
    def issue_to_dict(self, issue: FlaskIssue) -> Dict[str, Any]:
        """将问题转换为字典"""
        return {
            'severity': issue.severity,
            'type': issue.type,
            'file': issue.file,
            'message': issue.message,
            'suggestion': issue.suggestion,
            'line': issue.line
        }
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 基于问题类型生成建议
        issue_types = defaultdict(int)
        for issue in self.issues:
            issue_types[issue.type] += 1
        
        if issue_types['security'] > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'security',
                'message': f'发现{issue_types["security"]}个安全问题',
                suggestion: '优先修复安全漏洞，添加必要的安全中间件'
            })
        
        if issue_types['performance'] > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'performance',
                'message': f'发现{issue_types["performance"]}个性能问题',
                suggestion: '优化代码结构，添加性能监控和缓存'
            })
        
        if issue_types['design'] > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'design',
                'message': f'发现{issue_types["design"]}个设计问题',
                suggestion: '重构代码设计，遵循Flask最佳实践'
            })
        
        return recommendations
    
    def calculate_health_score(self, summary: Dict[str, int]) -> int:
        """计算健康评分"""
        score = 100
        
        score -= summary['critical_issues'] * 20
        score -= summary['high_issues'] * 10
        score -= summary['medium_issues'] * 5
        score -= summary['low_issues'] * 2
        
        return max(0, score)

# Flask应用优化器
class FlaskAppOptimizer:
    def __init__(self, app_path: str):
        self.app_path = app_path
    
    def optimize_application(self) -> Dict[str, Any]:
        """优化Flask应用"""
        optimizations = []
        
        # 检查并优化依赖
        dependency_optimization = self.optimize_dependencies()
        if dependency_optimization:
            optimizations.append(dependency_optimization)
        
        # 检查并优化配置
        config_optimization = self.optimize_configuration()
        if config_optimization:
            optimizations.append(config_optimization)
        
        # 检查并优化结构
        structure_optimization = self.optimize_structure()
        if structure_optimization:
            optimizations.append(structure_optimization)
        
        return {
            'optimizations': optimizations,
            'summary': {
                'total_optimizations': len(optimizations),
                'estimated_improvements': self.estimate_improvements(optimizations)
            }
        }
    
    def optimize_dependencies(self) -> Optional[Dict[str, str]]:
        """优化依赖配置"""
        requirements_path = os.path.join(self.app_path, 'requirements.txt')
        
        if not os.path.exists(requirements_path):
            return {
                'type': 'dependency',
                'message': '创建requirements.txt文件',
                'suggestion': '添加Flask和必要依赖'
            }
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            # 检查性能依赖
            performance_deps = ['gunicorn', 'redis', 'flask-caching']
            missing_deps = []
            
            for dep in performance_deps:
                if not any(dep.lower() in req.lower() for req in requirements):
                    missing_deps.append(dep)
            
            if missing_deps:
                return {
                    'type': 'dependency',
                    'message': f'建议添加性能依赖: {", ".join(missing_deps)}',
                    'suggestion': '这些依赖可以提升应用性能'
                }
        
        except Exception:
            pass
        
        return None
    
    def optimize_configuration(self) -> Optional[Dict[str, str]]:
        """优化配置管理"""
        config_files = ['config.py', 'settings.py', '.env']
        
        if not any(os.path.exists(os.path.join(self.app_path, f)) for f in config_files):
            return {
                'type': 'configuration',
                'message': '创建配置文件',
                'suggestion': '使用config.py或.env管理应用配置'
            }
        
        return None
    
    def optimize_structure(self) -> Optional[Dict[str, str]]:
        """优化项目结构"""
        required_dirs = ['templates', 'static']
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(self.app_path, dir_name)):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return {
                'type': 'structure',
                'message': f'创建必要目录: {", ".join(missing_dirs)}',
                'suggestion': '这些目录是Flask应用的标准结构'
            }
        
        return None
    
    def estimate_improvements(self, optimizations: List[Dict[str, str]]) -> Dict[str, int]:
        """估算改进效果"""
        improvements = {
            'performance': 0,
            'security': 0,
            'maintainability': 0
        }
        
        for opt in optimizations:
            if opt['type'] == 'dependency':
                improvements['performance'] += 20
            elif opt['type'] == 'configuration':
                improvements['security'] += 15
            elif opt['type'] == 'structure':
                improvements['maintainability'] += 25
        
        return improvements

# 使用示例
def main():
    # 分析Flask应用
    analyzer = FlaskAppAnalyzer('./my-flask-app')
    report = analyzer.analyze_application()
    
    print("Flask应用分析报告:")
    print(f"健康评分: {report['health_score']}")
    print(f"问题总数: {report['summary']['total_issues']}")
    print(f"路由总数: {report['summary']['total_routes']}")
    
    print("\n优化建议:")
    for rec in report['recommendations']:
        print(f"- {rec['message']}: {rec['suggestion']}")
    
    # 优化应用
    optimizer = FlaskAppOptimizer('./my-flask-app')
    optimization = optimizer.optimize_application()
    
    print("\n优化建议:")
    for opt in optimization['optimizations']:
        print(f"- {opt['message']}: {opt['suggestion']}")

if __name__ == '__main__':
    main()
```

### Flask性能监控器
```python
import time
import psutil
from functools import wraps
from typing import Dict, Any, List
from flask import Flask, request, g
from dataclasses import dataclass

@dataclass
class RequestMetrics:
    """请求指标"""
    method: str
    path: str
    status_code: int
    duration: float
    timestamp: float
    user_agent: str
    ip: str

@dataclass
class PerformanceMetrics:
    """性能指标"""
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    active_connections: int
    requests_per_second: float

class FlaskPerformanceMonitor:
    def __init__(self, app: Flask = None):
        self.app = app
        self.requests: List[RequestMetrics] = []
        self.start_time = time.time()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """初始化Flask应用"""
        self.app = app
        
        # 注册请求处理中间件
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)
    
    def _before_request(self) -> None:
        """请求开始前"""
        g.start_time = time.time()
    
    def _after_request(self, response) -> None:
        """请求结束后"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            metrics = RequestMetrics(
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration=duration,
                timestamp=time.time(),
                user_agent=request.headers.get('User-Agent', ''),
                ip=request.remote_addr or ''
            )
            
            self.requests.append(metrics)
            
            # 保持最近1000个请求
            if len(self.requests) > 1000:
                self.requests.pop(0)
        
        return response
    
    def _teardown_request(self, exception) -> None:
        """请求清理"""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        # 计算请求统计
        request_stats = self._calculate_request_stats()
        
        # 获取系统性能
        system_stats = self._get_system_stats()
        
        # 计算路由统计
        route_stats = self._calculate_route_stats()
        
        return {
            'timestamp': time.time(),
            'uptime': time.time() - self.start_time,
            'request_stats': request_stats,
            'system_stats': system_stats,
            'route_stats': route_stats
        }
    
    def _calculate_request_stats(self) -> Dict[str, Any]:
        """计算请求统计"""
        if not self.requests:
            return {
                'total_requests': 0,
                'requests_per_second': 0,
                'average_response_time': 0,
                'error_rate': 0
            }
        
        total_requests = len(self.requests)
        uptime = time.time() - self.start_time
        requests_per_second = total_requests / uptime if uptime > 0 else 0
        
        # 计算平均响应时间
        response_times = [req.duration for req in self.requests]
        average_response_time = sum(response_times) / len(response_times)
        
        # 计算错误率
        error_requests = [req for req in self.requests if req.status_code >= 400]
        error_rate = len(error_requests) / total_requests * 100 if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'requests_per_second': requests_per_second,
            'average_response_time': average_response_time,
            'error_rate': error_rate,
            'p95_response_time': self._calculate_percentile(response_times, 95),
            'p99_response_time': self._calculate_percentile(response_times, 99)
        }
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_mb': psutil.virtual_memory().used / 1024 / 1024,
            'active_connections': len(psutil.net_connections()),
            'process_count': len(psutil.pids())
        }
    
    def _calculate_route_stats(self) -> List[Dict[str, Any]]:
        """计算路由统计"""
        route_stats = {}
        
        for req in self.requests:
            route_key = f"{req.method} {req.path}"
            if route_key not in route_stats:
                route_stats[route_key] = {
                    'count': 0,
                    'total_duration': 0,
                    'average_duration': 0,
                    'errors': 0
                }
            
            stats = route_stats[route_key]
            stats['count'] += 1
            stats['total_duration'] += req.duration
            stats['average_duration'] = stats['total_duration'] / stats['count']
            
            if req.status_code >= 400:
                stats['errors'] += 1
        
        # 转换为列表并排序
        return sorted(
            [
                {
                    'route': route,
                    **stats
                }
                for route, stats in route_stats.items()
            ],
            key=lambda x: x['count'],
            reverse=True
        )[:10]  # 返回前10个最繁忙的路由
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

# 性能监控装饰器
def monitor_performance(monitor: FlaskPerformanceMonitor):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # 可以在这里记录函数级别的性能数据
        return wrapper
    return decorator

# 使用示例
def create_app():
    app = Flask(__name__)
    
    # 初始化性能监控
    monitor = FlaskPerformanceMonitor(app)
    
    @app.route('/metrics')
    def get_metrics():
        """获取性能指标"""
        return monitor.get_metrics()
    
    @app.route('/')
    def index():
        return "Hello, World!"
    
    @app.route('/api/users')
    def get_users():
        # 模拟数据库查询
        time.sleep(0.1)
        return {"users": []}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

## Flask轻量级应用最佳实践

### 应用结构
1. **模块化设计**: 按功能模块组织代码
2. **蓝图(Blueprint)**: 使用蓝图组织大型应用
3. **配置管理**: 分环境配置管理
4. **工厂模式**: 使用应用工厂模式
5. **目录结构**: 标准Flask项目结构

### 路由设计
1. **RESTful规范**: 遵循REST API设计原则
2. **路由命名**: 使用描述性路由名称
3. **参数验证**: 严格的输入参数验证
4. **错误处理**: 统一的错误处理机制
5. **版本控制**: API版本管理策略

### 安全配置
1. **CSRF保护**: 启用CSRF保护
2. **安全头**: 设置安全HTTP头
3. **输入验证**: 严格的输入验证和清理
4. **会话安全**: 安全的会话配置
5. **HTTPS**: 强制HTTPS连接

### 性能优化
1. **缓存策略**: Redis或Memcached缓存
2. **数据库优化**: 连接池和查询优化
3. **静态文件**: CDN和静态文件优化
4. **异步处理**: 使用Celery处理异步任务
5. **监控告警**: 性能监控和告警

## 相关技能

- **restful-api-design** - RESTful API设计
- **api-validator** - API验证器
- **python-development** - Python开发
- **microservices** - 微服务架构
