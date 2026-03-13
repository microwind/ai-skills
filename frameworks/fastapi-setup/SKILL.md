---
name: FastAPI高性能API
description: "当开发FastAPI应用时，分析路由设计，优化异步处理，解决性能问题。验证API架构，设计高性能服务，和最佳实践。"
license: MIT
---

# FastAPI高性能API技能

## 概述
FastAPI是Python最现代化的高性能Web框架。不当的FastAPI配置会导致性能问题、安全漏洞和维护困难。在开发FastAPI应用前需要仔细分析架构需求。

**核心原则**: 好的FastAPI应用应该高性能、类型安全、自动文档化、易于测试。坏的FastAPI应用会导致性能瓶颈、类型错误和维护困难。

## 何时使用

**始终:**
- 开发高性能API时
- 构建微服务架构时
- 实现异步处理时
- 配置自动文档时
- 处理数据验证时

**触发短语:**
- "FastAPI高性能API"
- "Python异步Web框架"
- "API性能优化"
- "类型安全API"
- "FastAPI路由设计"
- "异步API开发"

## FastAPI高性能API功能

### 路由系统
- RESTful路由设计
- 路径参数验证
- 查询参数处理
- 请求体验证
- 响应模型定义

### 异步处理
- 异步路由处理
- 并发请求管理
- 异步数据库操作
- 后台任务处理
- WebSocket支持

### 数据验证
- Pydantic模型验证
- 类型注解支持
- 自定义验证器
- 数据序列化
- 错误处理机制

### 自动文档
- OpenAPI规范生成
- Swagger UI集成
- ReDoc文档界面
- 交互式API测试
- 文档自定义配置

## 常见FastAPI问题

### 性能瓶颈
```
问题:
API响应慢，并发能力差

错误示例:
- 同步阻塞操作
- 数据库连接未复用
- 缺乏缓存机制
- 内存泄漏问题

解决方案:
1. 使用异步操作避免阻塞
2. 配置数据库连接池
3. 添加适当的缓存策略
4. 实施内存监控和清理
```

### 数据验证问题
```
问题:
数据验证不严格，类型错误频发

错误示例:
- 缺少输入验证
- 类型注解不完整
- 验证规则不合理
- 错误信息不清晰

解决方案:
1. 完善Pydantic模型定义
2. 添加严格的类型注解
3. 实施自定义验证规则
4. 提供清晰的错误信息
```

### 文档生成问题
```
问题:
API文档不完整，用户体验差

错误示例:
- 缺少响应模型
- 参数描述缺失
- 示例数据不完整
- 文档配置错误

解决方案:
1. 完善响应模型定义
2. 添加详细的参数描述
3. 提供完整的示例数据
4. 正确配置文档选项
```

## 代码实现示例

### FastAPI应用分析器
```python
import ast
import os
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import sys

@dataclass
class FastAPIRoute:
    """FastAPI路由信息"""
    path: str
    method: str
    function_name: str
    file: str
    line: int
    issues: List[str]

@dataclass
class FastAPIModel:
    """FastAPI模型信息"""
    name: str
    file: str
    line: int
    fields: List[str]
    issues: List[str]

@dataclass
class FastAPIIssue:
    """FastAPI问题"""
    severity: str  # critical, high, medium, low
    type: str
    file: str
    message: str
    suggestion: str
    line: Optional[int] = None

class FastAPIAnalyzer:
    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
        self.routes: List[FastAPIRoute] = []
        self.models: List[FastAPIModel] = []
        self.issues: List[FastAPIIssue] = []
        
    def analyze_application(self) -> Dict[str, Any]:
        """分析FastAPI应用"""
        try:
            # 扫描Python文件
            python_files = self.find_python_files()
            
            for file_path in python_files:
                self.analyze_python_file(file_path)
            
            # 分析依赖配置
            self.analyze_dependencies()
            
            # 分析配置文件
            self.analyze_configuration()
            
            # 生成分析报告
            return self.generate_report()
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def find_python_files(self) -> List[Path]:
        """查找Python文件"""
        python_files = []
        
        for root, dirs, files in os.walk(self.app_path):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def analyze_python_file(self, file_path: Path) -> None:
        """分析Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 查找FastAPI应用
            fastapi_apps = self.find_fastapi_apps(tree, str(file_path))
            
            # 分析路由
            self.analyze_routes(tree, str(file_path), fastapi_apps)
            
            # 分析模型
            self.analyze_models(tree, str(file_path))
            
            # 分析代码质量
            self.analyze_code_quality(tree, str(file_path))
            
        except Exception as e:
            self.issues.append(FastAPIIssue(
                severity='medium',
                type='analysis',
                file=str(file_path),
                message=f'文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def find_fastapi_apps(self, tree: ast.AST, file_path: str) -> List[str]:
        """查找FastAPI应用实例"""
        fastapi_apps = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # 检查是否是FastAPI实例
                        if (isinstance(node.value, ast.Call) and 
                            isinstance(node.value.func, ast.Name) and 
                            node.value.func.id == 'FastAPI'):
                            fastapi_apps.append(target.id)
                        elif (isinstance(node.value, ast.Call) and 
                              isinstance(node.value.func, ast.Attribute) and 
                              node.value.func.attr == 'FastAPI'):
                            fastapi_apps.append(target.id)
        
        return fastapi_apps
    
    def analyze_routes(self, tree: ast.AST, file_path: str, fastapi_apps: List[str]) -> None:
        """分析路由定义"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查路由装饰器
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']):
                    
                    # 获取路由信息
                    route_info = self.extract_route_info(node, file_path, fastapi_apps)
                    if route_info:
                        self.routes.append(route_info)
                        self.validate_route(route_info)
    
    def extract_route_info(self, node: ast.Call, file_path: str, fastapi_apps: List[str]) -> Optional[FastAPIRoute]:
        """提取路由信息"""
        try:
            # 获取HTTP方法
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
                return FastAPIRoute(
                    path=path,
                    method=method,
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
    
    def validate_route(self, route: FastAPIRoute) -> None:
        """验证路由设计"""
        # 检查RESTful规范
        if not self.is_restful_path(route.path):
            route.issues.append('路径不符合RESTful规范')
            self.issues.append(FastAPIIssue(
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
            self.issues.append(FastAPIIssue(
                severity='high',
                type='validation',
                file=route.file,
                message=f'路由缺少参数验证: {route.method} {route.path}',
                suggestion='添加Pydantic模型进行参数验证',
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
        return '{' in path and '}' in path
    
    def has_validation(self, function_name: str) -> bool:
        """检查函数是否有验证逻辑"""
        # 简化实现，实际需要分析函数体
        return False
    
    def analyze_models(self, tree: ast.AST, file_path: str) -> None:
        """分析Pydantic模型"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否是Pydantic模型
                if self.is_pydantic_model(node):
                    model_info = self.parse_pydantic_model(node, file_path)
                    if model_info:
                        self.models.append(model_info)
                        self.validate_model(model_info)
    
    def is_pydantic_model(self, node: ast.ClassDef) -> bool:
        """检查是否是Pydantic模型"""
        if not node.bases:
            return False
        
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'BaseModel':
                return True
            elif isinstance(base, ast.Attribute) and base.attr == 'BaseModel':
                return True
        
        return False
    
    def parse_pydantic_model(self, node: ast.ClassDef, file_path: str) -> Optional[FastAPIModel]:
        """解析Pydantic模型"""
        if not node.name:
            return None
        
        model_info = FastAPIModel(
            name=node.name,
            file=file_path,
            line=node.lineno,
            fields=[],
            issues=[]
        )
        
        # 解析字段
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                model_info.fields.append(item.target.id)
        
        return model_info
    
    def validate_model(self, model: FastAPIModel) -> None:
        """验证Pydantic模型"""
        # 检查字段类型注解
        if len(model.fields) == 0:
            model.issues.append('模型没有字段')
            self.issues.append(FastAPIIssue(
                severity='medium',
                type='model',
                file=model.file,
                message=f'模型没有字段: {model.name}',
                suggestion='添加必要的字段定义',
                line=model.line
            ))
        
        # 检查模型命名规范
        if not model.name.endswith('Model') and not model.name.endswith('DTO'):
            model.issues.append('模型命名不规范')
            self.issues.append(FastAPIIssue(
                severity='low',
                type='naming',
                file=model.file,
                message=f'模型命名不规范: {model.name}',
                suggestion='使用Model或DTO后缀',
                line=model.line
            ))
    
    def analyze_code_quality(self, tree: ast.AST, file_path: str) -> None:
        """分析代码质量"""
        # 检查函数复杂度
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self.calculate_complexity(node)
                if complexity > 10:
                    self.issues.append(FastAPIIssue(
                        severity='medium',
                        type='quality',
                        file=file_path,
                        message=f'函数复杂度过高: {node.name} (复杂度: {complexity})',
                        suggestion='拆分复杂函数为多个小函数',
                        line=node.lineno
                    ))
        
        # 检查异步使用
        self.check_async_usage(tree, file_path)
    
    def calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def check_async_usage(self, tree: ast.AST, file_path: str) -> None:
        """检查异步使用"""
        has_async_def = False
        has_await = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                has_async_def = True
            elif isinstance(node, ast.Await):
                has_await = True
        
        if has_async_def and not has_await:
            self.issues.append(FastAPIIssue(
                severity='medium',
                type='async',
                file=file_path,
                message='异步函数中没有使用await',
                suggestion='在异步函数中使用await关键字'
            ))
    
    def analyze_dependencies(self) -> None:
        """分析依赖配置"""
        requirements_path = self.app_path / 'requirements.txt'
        pyproject_path = self.app_path / 'pyproject.toml'
        
        if requirements_path.exists():
            self.analyze_requirements_txt(requirements_path)
        elif pyproject_path.exists():
            self.analyze_pyproject_toml(pyproject_path)
        else:
            self.issues.append(FastAPIIssue(
                severity='high',
                type='dependency',
                file='requirements',
                message='缺少依赖配置文件',
                suggestion='创建requirements.txt或pyproject.toml文件'
            ))
    
    def analyze_requirements_txt(self, requirements_path: Path) -> None:
        """分析requirements.txt"""
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            # 检查必要依赖
            required_deps = ['fastapi', 'uvicorn']
            performance_deps = ['pydantic', 'python-multipart']
            
            for dep in required_deps:
                if not any(dep.lower() in req.lower() for req in requirements):
                    self.issues.append(FastAPIIssue(
                        severity='high',
                        type='dependency',
                        file=str(requirements_path),
                        message=f'缺少必要依赖: {dep}',
                        suggestion=f'添加{dep}到requirements.txt'
                    ))
            
            for dep in performance_deps:
                if not any(dep.lower() in req.lower() for req in requirements):
                    self.issues.append(FastAPIIssue(
                        severity='medium',
                        type='dependency',
                        file=str(requirements_path),
                        message=f'建议添加依赖: {dep}',
                        suggestion=f'添加{dep}提升性能'
                    ))
        
        except Exception as e:
            self.issues.append(FastAPIIssue(
                severity='medium',
                type='analysis',
                file=str(requirements_path),
                message=f'requirements.txt分析失败: {e}',
                suggestion='检查文件格式和编码'
            ))
    
    def analyze_pyproject_toml(self, pyproject_path: Path) -> None:
        """分析pyproject.toml"""
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单检查是否包含FastAPI
            if 'fastapi' not in content.lower():
                self.issues.append(FastAPIIssue(
                    severity='high',
                    type='dependency',
                    file=str(pyproject_path),
                    message='缺少FastAPI依赖',
                    suggestion='添加FastAPI到依赖列表'
                ))
        
        except Exception as e:
            self.issues.append(FastAPIIssue(
                severity='medium',
                type='analysis',
                file=str(pyproject_path),
                message=f'pyproject.toml分析失败: {e}',
                suggestion='检查文件格式和编码'
            ))
    
    def analyze_configuration(self) -> None:
        """分析配置文件"""
        # 检查是否有主应用文件
        main_files = ['main.py', 'app.py', 'server.py']
        has_main_file = False
        
        for main_file in main_files:
            if (self.app_path / main_file).exists():
                has_main_file = True
                break
        
        if not has_main_file:
            self.issues.append(FastAPIIssue(
                severity='medium',
                type='structure',
                file='structure',
                message='缺少主应用文件',
                suggestion='创建main.py或app.py文件'
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
            'total_models': len(self.models)
        }
        
        recommendations = self.generate_recommendations()
        
        return {
            'summary': summary,
            'routes': [self.route_to_dict(r) for r in self.routes],
            'models': [self.model_to_dict(m) for m in self.models],
            'issues': [self.issue_to_dict(i) for i in self.issues],
            'recommendations': recommendations,
            'health_score': self.calculate_health_score(summary)
        }
    
    def route_to_dict(self, route: FastAPIRoute) -> Dict[str, Any]:
        """将路由转换为字典"""
        return {
            'path': route.path,
            'method': route.method,
            'function_name': route.function_name,
            'file': route.file,
            'line': route.line,
            'issues': route.issues
        }
    
    def model_to_dict(self, model: FastAPIModel) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'name': model.name,
            'file': model.file,
            'line': model.line,
            'fields': model.fields,
            'issues': model.issues
        }
    
    def issue_to_dict(self, issue: FastAPIIssue) -> Dict[str, Any]:
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
        issue_types = {}
        for issue in self.issues:
            issue_types[issue.type] = issue_types.get(issue.type, 0) + 1
        
        if issue_types.get('validation', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'validation',
                'message': f'发现{issue_types["validation"]}个验证问题',
                suggestion: '完善Pydantic模型验证'
            })
        
        if issue_types.get('performance', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'performance',
                'message': f'发现{issue_types["performance"]}个性能问题',
                suggestion: '优化异步处理和数据库连接'
            })
        
        if issue_types.get('design', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'design',
                'message': f'发现{issue_types["design"]}个设计问题',
                suggestion: '遵循RESTful API设计原则'
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

# FastAPI性能优化器
class FastAPIOptimizer:
    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
    
    def optimize_application(self) -> Dict[str, Any]:
        """优化FastAPI应用"""
        optimizations = []
        
        # 检查并优化依赖
        dependency_optimization = self.optimize_dependencies()
        if dependency_optimization:
            optimizations.append(dependency_optimization)
        
        # 检查并优化配置
        config_optimization = self.optimize_configuration()
        if config_optimization:
            optimizations.append(config_optimization)
        
        # 检查并优化性能
        performance_optimization = self.optimize_performance()
        if performance_optimization:
            optimizations.append(performance_optimization)
        
        return {
            'optimizations': optimizations,
            'summary': {
                'total_optimizations': len(optimizations),
                'estimated_improvements': self.estimate_improvements(optimizations)
            }
        }
    
    def optimize_dependencies(self) -> Optional[Dict[str, str]]:
        """优化依赖配置"""
        requirements_path = self.app_path / 'requirements.txt'
        
        if not requirements_path.exists():
            return {
                'type': 'dependency',
                'message': '创建requirements.txt文件',
                'suggestion': '添加FastAPI和必要依赖'
            }
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            # 检查性能依赖
            performance_deps = ['uvicorn[standard]', 'gunicorn', 'redis']
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
        # 检查是否有环境配置
        env_file = self.app_path / '.env'
        
        if not env_file.exists():
            return {
                'type': 'configuration',
                'message': '创建环境配置文件',
                'suggestion': '使用.env文件管理环境变量'
            }
        
        return None
    
    def optimize_performance(self) -> Optional[Dict[str, str]]:
        """优化性能配置"""
        # 检查是否有异步配置
        main_files = ['main.py', 'app.py', 'server.py']
        
        for main_file in main_files:
            file_path = self.app_path / main_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'async def' not in content:
                        return {
                            'type': 'performance',
                            'message': '使用异步处理',
                            'suggestion': '将路由处理函数改为异步以提升性能'
                        }
                except Exception:
                    pass
        
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
            elif opt['type'] == 'performance':
                improvements['performance'] += 25
        
        return improvements

# 使用示例
def main():
    # 分析FastAPI应用
    analyzer = FastAPIAnalyzer('./my-fastapi-app')
    report = analyzer.analyze_application()
    
    print("FastAPI应用分析报告:")
    print(f"健康评分: {report['health_score']}")
    print(f"问题总数: {report['summary']['total_issues']}")
    print(f"路由总数: {report['summary']['total_routes']}")
    print(f"模型总数: {report['summary']['total_models']}")
    
    print("\n优化建议:")
    for rec in report['recommendations']:
        print(f"- {rec['message']}: {rec['suggestion']}")
    
    # 优化应用
    optimizer = FastAPIOptimizer('./my-fastapi-app')
    optimization = optimizer.optimize_application()
    
    print("\n优化建议:")
    for opt in optimization['optimizations']:
        print(f"- {opt['message']}: {opt['suggestion']}")

if __name__ == '__main__':
    main()
```

### FastAPI性能监控器
```python
import time
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, Request, Response
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from dataclasses import dataclass
import psutil
import uvicorn

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

class FastAPIPerformanceMonitor:
    def __init__(self, app: FastAPI):
        self.app = app
        self.requests: List[RequestMetrics] = []
        self.start_time = time.time()
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """设置监控中间件"""
        self.app.add_middleware(PerformanceMiddleware, monitor=self)
        
        @self.app.get("/metrics")
        async def get_metrics():
            return self.get_metrics()
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": time.time()}
    
    def record_request(self, request: Request, response: Response, duration: float):
        """记录请求指标"""
        metrics = RequestMetrics(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
            timestamp=time.time(),
            user_agent=request.headers.get("user-agent", ""),
            ip=request.client.host if request.client else ""
        )
        
        self.requests.append(metrics)
        
        # 保持最近1000个请求
        if len(self.requests) > 1000:
            self.requests.pop(0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        request_stats = self.calculate_request_stats()
        performance_stats = self.get_performance_stats()
        route_stats = self.calculate_route_stats()
        
        return {
            "timestamp": time.time(),
            "uptime": time.time() - self.start_time,
            "request_stats": request_stats,
            "performance_stats": performance_stats,
            "route_stats": route_stats
        }
    
    def calculate_request_stats(self) -> Dict[str, Any]:
        """计算请求统计"""
        if not self.requests:
            return {
                "total_requests": 0,
                "requests_per_second": 0,
                "average_response_time": 0,
                "error_rate": 0,
                "p95_response_time": 0,
                "p99_response_time": 0
            }
        
        total_requests = len(self.requests)
        uptime = time.time() - self.start_time
        requests_per_second = total_requests / uptime if uptime > 0 else 0
        
        response_times = [req.duration for req in self.requests]
        average_response_time = sum(response_times) / len(response_times)
        
        error_requests = [req for req in self.requests if req.status_code >= 400]
        error_rate = len(error_requests) / total_requests * 100 if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "requests_per_second": requests_per_second,
            "average_response_time": average_response_time,
            "error_rate": error_rate,
            "p95_response_time": self.calculate_percentile(response_times, 95),
            "p99_response_time": self.calculate_percentile(response_times, 99)
        }
    
    def get_performance_stats(self) -> PerformanceMetrics:
        """获取性能统计"""
        return PerformanceMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            memory_mb=psutil.virtual_memory().used / 1024 / 1024,
            active_connections=len(psutil.net_connections()),
            requests_per_second=self.calculate_current_rps()
        )
    
    def calculate_route_stats(self) -> List[Dict[str, Any]]:
        """计算路由统计"""
        route_stats = {}
        
        for req in self.requests:
            route_key = f"{req.method} {req.path}"
            if route_key not in route_stats:
                route_stats[route_key] = {
                    "count": 0,
                    "total_duration": 0,
                    "average_duration": 0,
                    "errors": 0
                }
            
            stats = route_stats[route_key]
            stats["count"] += 1
            stats["total_duration"] += req.duration
            stats["average_duration"] = stats["total_duration"] / stats["count"]
            
            if req.status_code >= 400:
                stats["errors"] += 1
        
        # 转换为数组并排序
        return sorted(
            [
                {"route": route, **stats}
                for route, stats in route_stats.items()
            ],
            key=lambda x: x["count"],
            reverse=True
        )[:10]  # 返回前10个最繁忙的路由
    
    def calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def calculate_current_rps(self) -> float:
        """计算当前每秒请求数"""
        now = time.time()
        recent_requests = [req for req in self.requests if now - req.timestamp < 60]  # 最近1分钟
        return len(recent_requests) / 60  # 每秒请求数

class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app, monitor: FastAPIPerformanceMonitor):
        super().__init__(app)
        self.monitor = monitor
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        self.monitor.record_request(request, response, duration)
        
        return response

# 性能监控装饰器
def monitor_performance(monitor: FastAPIMonitor):
    """性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # 可以在这里记录函数级别的性能数据
        return wrapper
    return decorator

# 使用示例
def create_app():
    app = FastAPI(title="FastAPI Performance Monitor")
    
    # 初始化性能监控
    monitor = FastAPIPerformanceMonitor(app)
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/api/users")
    async def get_users():
        # 模拟数据库查询
        await asyncio.sleep(0.1)
        return {"users": []}
    
    @app.post("/api/users")
    async def create_user(user_data: dict):
        # 模拟用户创建
        await asyncio.sleep(0.05)
        return {"user": user_data, "status": "created"}
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    # 使用uvicorn运行
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
```

## FastAPI高性能API最佳实践

### 路由设计
1. **RESTful规范**: 遵循REST API设计原则
2. **路径命名**: 使用名词复数形式
3. **HTTP方法**: 正确使用GET、POST、PUT、DELETE
4. **参数验证**: 严格的输入参数验证
5. **响应模型**: 定义清晰的响应模型

### 异步处理
1. **异步路由**: 使用async/await模式
2. **并发控制**: 合理控制并发数量
3. **异步数据库**: 使用异步数据库驱动
4. **后台任务**: 使用BackgroundTasks处理耗时操作
5. **WebSocket**: 支持实时通信

### 数据验证
1. **Pydantic模型**: 完善的数据模型定义
2. **类型注解**: 严格的类型注解
3. **自定义验证**: 实现自定义验证器
4. **错误处理**: 统一的错误处理机制
5. **数据序列化**: 高效的数据序列化

### 性能优化
1. **依赖注入**: 优化依赖注入性能
2. **缓存策略**: 合理使用缓存机制
3. **数据库优化**: 异步数据库操作
4. **内存管理**: 避免内存泄漏
5. **监控告警**: 实时性能监控

## 相关技能

- **restful-api-design** - RESTful API设计
- **api-validator** - API验证器
- **python-development** - Python开发
- **async-programming** - 异步编程
