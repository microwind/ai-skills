---
name: Django Web框架
description: "当开发Django应用时，分析项目结构，优化ORM查询，解决性能问题。验证MVC架构，设计企业级Web应用，和最佳实践。"
license: MIT
---

# Django Web框架技能

## 概述
Django是Python最强大的Web框架。不当的Django配置会导致性能问题、安全漏洞和维护困难。在开发Django应用前需要仔细分析项目需求。

**核心原则**: 好的Django应用应该遵循MTV模式、高效ORM、安全配置、易于扩展。坏的Django应用会导致性能瓶颈、安全风险和维护困难。

## 何时使用

**始终:**
- 开发企业级Web应用时
- 构建内容管理系统时
- 实现用户认证系统时
- 配置数据库ORM时
- 处理表单验证时

**触发短语:**
- "Django Web框架"
- "Python Web开发"
- "ORM查询优化"
- "MVC架构设计"
- "Django项目结构"
- "企业级Web应用"

## Django Web框架功能

### MTV架构
- 模型层设计
- 视图层处理
- 模板层渲染
- URL路由配置
- 中间件系统

### ORM系统
- 模型定义
- 查询优化
- 关系映射
- 数据迁移
- 原生SQL支持

### 用户认证
- 用户模型
- 权限系统
- 角色管理
- 会话管理
- 密码安全

### 管理后台
- 自动管理界面
- 自定义管理
- 批量操作
- 搜索过滤
- 导入导出

## 常见Django问题

### ORM性能问题
```
问题:
数据库查询慢，N+1查询问题

错误示例:
- 缺少select_related/prefetch_related
- 循环查询数据库
- 未使用数据库索引
- 复杂聚合查询

解决方案:
1. 使用select_related优化外键查询
2. 使用prefetch_related优化多对多查询
3. 添加适当的数据库索引
4. 使用缓存机制
```

### 安全配置问题
```
问题:
安全漏洞，数据泄露风险

错误示例:
- 调试模式在生产环境开启
- CSRF保护未启用
- SQL注入风险
- XSS攻击漏洞

解决方案:
1. 生产环境关闭DEBUG模式
2. 启用CSRF保护中间件
3. 使用ORM防止SQL注入
4. 模板自动转义防止XSS
```

### 项目结构问题
```
问题:
代码组织混乱，维护困难

错误示例:
- 应用职责不清晰
- 配置文件混乱
- 静态文件管理不当
- 模板结构不合理

解决方案:
1. 合理划分应用职责
2. 分环境配置管理
3. 统一静态文件处理
4. 优化模板继承结构
```

## 代码实现示例

### Django项目分析器
```python
import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import importlib.util

@dataclass
class DjangoApp:
    """Django应用信息"""
    name: str
    path: str
    models: List[str]
    views: List[str]
    urls: List[str]
    issues: List[str]

@dataclass
class DjangoModel:
    """Django模型信息"""
    name: str
    file: str
    fields: List[str]
    relationships: List[str]
    issues: List[str]

@dataclass
class DjangoIssue:
    """Django问题"""
    severity: str  # critical, high, medium, low
    type: str
    file: str
    message: str
    suggestion: str
    line: Optional[int] = None

class DjangoAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.apps: List[DjangoApp] = []
        self.models: List[DjangoModel] = []
        self.issues: List[DjangoIssue] = []
        
    def analyze_project(self) -> Dict[str, Any]:
        """分析Django项目"""
        try:
            # 检查Django项目结构
            self.check_project_structure()
            
            # 分析配置文件
            self.analyze_settings()
            
            # 扫描应用
            self.scan_apps()
            
            # 分析模型
            self.analyze_models()
            
            # 分析视图
            self.analyze_views()
            
            # 分析URL配置
            self.analyze_urls()
            
            # 生成分析报告
            return self.generate_report()
            
        except Exception as e:
            return {'error': f'分析失败: {e}'}
    
    def check_project_structure(self) -> None:
        """检查Django项目结构"""
        # 检查manage.py
        manage_py = self.project_path / 'manage.py'
        if not manage_py.exists():
            self.issues.append(DjangoIssue(
                severity='critical',
                type='structure',
                file='manage.py',
                message='缺少manage.py文件',
                suggestion='创建Django标准项目结构'
            ))
        
        # 检查settings.py
        settings_py = self.project_path / 'settings.py'
        if not settings_py.exists():
            # 检查settings目录
            settings_dir = self.project_path / 'settings'
            if not settings_dir.exists():
                self.issues.append(DjangoIssue(
                    severity='critical',
                    type='structure',
                    file='settings.py',
                    message='缺少settings.py文件',
                    suggestion='创建Django配置文件'
                ))
    
    def analyze_settings(self) -> None:
        """分析settings配置"""
        settings_files = []
        
        # 查找settings.py或settings目录
        settings_py = self.project_path / 'settings.py'
        if settings_py.exists():
            settings_files.append(settings_py)
        else:
            settings_dir = self.project_path / 'settings'
            if settings_dir.exists():
                for file in settings_dir.glob('*.py'):
                    if file.name.startswith('__'):
                        continue
                    settings_files.append(file)
        
        for settings_file in settings_files:
            self.analyze_settings_file(settings_file)
    
    def analyze_settings_file(self, settings_file: Path) -> None:
        """分析单个settings文件"""
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查DEBUG配置
            if 'DEBUG = True' in content:
                self.issues.append(DjangoIssue(
                    severity='high',
                    type='security',
                    file=str(settings_file),
                    message='DEBUG模式在生产环境中开启',
                    suggestion='生产环境应设置DEBUG = False'
                ))
            
            # 检查SECRET_KEY
            if 'SECRET_KEY' in content and not content.startswith('#'):
                # 检查是否硬编码
                if 'SECRET_KEY' in content and '=' in content.split('SECRET_KEY')[1].split('\n')[0]:
                    self.issues.append(DjangoIssue(
                        severity='high',
                        type='security',
                        file=str(settings_file),
                        message='SECRET_KEY硬编码在配置文件中',
                        suggestion='使用环境变量管理SECRET_KEY'
                    ))
            
            # 检查数据库配置
            if 'DATABASES' not in content:
                self.issues.append(DjangoIssue(
                    severity='high',
                    type='database',
                    file=str(settings_file),
                    message='缺少数据库配置',
                    suggestion='配置数据库连接'
                ))
            
            # 检查中间件配置
            required_middlewares = [
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware'
            ]
            
            for middleware in required_middlewares:
                if middleware not in content:
                    self.issues.append(DjangoIssue(
                        severity='medium',
                        type='middleware',
                        file=str(settings_file),
                        message=f'缺少重要中间件: {middleware}',
                        suggestion='添加Django标准中间件'
                    ))
            
            # 检查INSTALLED_APPS
            if 'INSTALLED_APPS' not in content:
                self.issues.append(DjangoIssue(
                    severity='high',
                    type='apps',
                    file=str(settings_file),
                    message='缺少INSTALLED_APPS配置',
                    suggestion='配置已安装的应用'
                ))
        
        except Exception as e:
            self.issues.append(DjangoIssue(
                severity='medium',
                type='analysis',
                file=str(settings_file),
                message=f'settings文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def scan_apps(self) -> None:
        """扫描Django应用"""
        # 查找应用目录
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                # 检查是否是Django应用
                if self.is_django_app(item):
                    app_info = self.analyze_app(item)
                    if app_info:
                        self.apps.append(app_info)
    
    def is_django_app(self, app_path: Path) -> bool:
        """检查是否是Django应用"""
        # 检查是否有__init__.py
        init_file = app_path / '__init__.py'
        if not init_file.exists():
            return False
        
        # 检查是否有models.py, views.py, urls.py
        required_files = ['models.py', 'views.py']
        for file_name in required_files:
            if not (app_path / file_name).exists():
                return False
        
        return True
    
    def analyze_app(self, app_path: Path) -> Optional[DjangoApp]:
        """分析Django应用"""
        app_name = app_path.name
        
        app_info = DjangoApp(
            name=app_name,
            path=str(app_path),
            models=[],
            views=[],
            urls=[],
            issues=[]
        )
        
        # 分析models.py
        models_file = app_path / 'models.py'
        if models_file.exists():
            app_info.models = self.extract_model_names(models_file)
        
        # 分析views.py
        views_file = app_path / 'views.py'
        if views_file.exists():
            app_info.views = self.extract_view_names(views_file)
        
        # 分析urls.py
        urls_file = app_path / 'urls.py'
        if urls_file.exists():
            app_info.urls = self.extract_url_patterns(urls_file)
        
        # 验证应用结构
        self.validate_app(app_info)
        
        return app_info
    
    def extract_model_names(self, models_file: Path) -> List[str]:
        """提取模型名称"""
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的类名提取
            model_names = []
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否继承自models.Model
                    if self.is_django_model(node):
                        model_names.append(node.name)
            
            return model_names
        
        except Exception:
            return []
    
    def is_django_model(self, node: ast.ClassDef) -> bool:
        """检查是否是Django模型"""
        if not node.bases:
            return False
        
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'Model':
                return True
            elif isinstance(base, ast.Attribute):
                if base.attr == 'Model':
                    return True
        
        return False
    
    def extract_view_names(self, views_file: Path) -> List[str]:
        """提取视图名称"""
        try:
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            view_names = []
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查是否是视图函数
                    if self.is_django_view(node):
                        view_names.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    # 检查是否是视图类
                    if self.is_django_class_view(node):
                        view_names.append(node.name)
            
            return view_names
        
        except Exception:
            return []
    
    def is_django_view(self, node: ast.FunctionDef) -> bool:
        """检查是否是Django视图函数"""
        # 简化实现，检查是否有request参数
        if node.args.args and len(node.args.args) >= 1:
            first_arg = node.args.args[0]
            if isinstance(first_arg, ast.arg) and first_arg.arg == 'request':
                return True
        return False
    
    def is_django_class_view(self, node: ast.ClassDef) -> bool:
        """检查是否是Django类视图"""
        if not node.bases:
            return False
        
        for base in node.bases:
            if isinstance(base, ast.Name):
                # 检查常见的Django视图基类
                view_bases = ['View', 'TemplateView', 'ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView']
                if base.id in view_bases:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr in view_bases:
                    return True
        
        return False
    
    def extract_url_patterns(self, urls_file: Path) -> List[str]:
        """提取URL模式"""
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            url_patterns = []
            
            # 简单的正则匹配
            path_pattern = r'path\([\'"]([^\'"]+)[\'"]'
            re_pattern = r'url\([\'"]r?([^\'"]+)[\'"]'
            
            paths = re.findall(path_pattern, content)
            urls = re.findall(re_pattern, content)
            
            url_patterns.extend(paths)
            url_patterns.extend(urls)
            
            return url_patterns
        
        except Exception:
            return []
    
    def validate_app(self, app: DjangoApp) -> None:
        """验证应用结构"""
        # 检查模型数量
        if len(app.models) == 0:
            app.issues.append('应用没有定义模型')
            self.issues.append(DjangoIssue(
                severity='medium',
                type='model',
                file=app.path,
                message=f'应用{app.name}没有定义模型',
                suggestion='考虑是否需要数据模型'
            ))
        
        # 检查视图数量
        if len(app.views) == 0:
            app.issues.append('应用没有定义视图')
            self.issues.append(DjangoIssue(
                severity='medium',
                type='view',
                file=app.path,
                message=f'应用{app.name}没有定义视图',
                suggestion='添加视图处理请求'
            ))
        
        # 检查URL配置
        if len(app.urls) == 0:
            app.issues.append('应用没有URL配置')
            self.issues.append(DjangoIssue(
                severity='medium',
                type='url',
                file=app.path,
                message=f'应用{app.name}没有URL配置',
                suggestion='添加URL路由配置'
            ))
    
    def analyze_models(self) -> None:
        """分析模型定义"""
        for app in self.apps:
            models_file = Path(app.path) / 'models.py'
            if models_file.exists():
                self.analyze_model_file(models_file, app.name)
    
    def analyze_model_file(self, models_file: Path, app_name: str) -> None:
        """分析模型文件"""
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and self.is_django_model(node):
                    model_info = self.parse_django_model(node, str(models_file))
                    if model_info:
                        self.models.append(model_info)
                        self.validate_model(model_info)
        
        except Exception as e:
            self.issues.append(DjangoIssue(
                severity='medium',
                type='analysis',
                file=str(models_file),
                message=f'模型文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def parse_django_model(self, node: ast.ClassDef, file_path: str) -> Optional[DjangoModel]:
        """解析Django模型"""
        if not node.name:
            return None
        
        model_info = DjangoModel(
            name=node.name,
            file=file_path,
            fields=[],
            relationships=[],
            issues=[]
        )
        
        # 解析字段
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        model_info.fields.append(field_name)
                        
                        # 检查是否是关系字段
                        if self.is_relationship_field(item):
                            model_info.relationships.append(field_name)
        
        return model_info
    
    def is_relationship_field(self, node: ast.Assign) -> bool:
        """检查是否是关系字段"""
        if not node.value:
            return False
        
        # 检查常见的Django关系字段
        relationship_fields = [
            'ForeignKey', 'OneToOneField', 'ManyToManyField', 'ManyToManyRel'
        ]
        
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                return node.value.func.id in relationship_fields
            elif isinstance(node.value.func, ast.Attribute):
                return node.value.func.attr in relationship_fields
        
        return False
    
    def validate_model(self, model: DjangoModel) -> None:
        """验证模型定义"""
        # 检查字段数量
        if len(model.fields) == 0:
            model.issues.append('模型没有字段')
            self.issues.append(DjangoIssue(
                severity='medium',
                type='model',
                file=model.file,
                message=f'模型{model.name}没有字段',
                suggestion='添加必要的字段定义',
                line=None
            ))
        
        # 检查是否缺少主键
        if 'id' not in model.fields and 'pk' not in model.fields:
            # 检查是否有显式主键
            has_primary_key = False
            for field in model.fields:
                if field.lower() in ['id', 'pk', 'uuid']:
                    has_primary_key = True
                    break
            
            if not has_primary_key:
                model.issues.append('模型缺少主键字段')
                self.issues.append(DjangoIssue(
                    severity='low',
                    type='model',
                    file=model.file,
                    message=f'模型{model.name}缺少主键字段',
                    suggestion='Django会自动添加id字段，或显式定义主键'
                ))
    
    def analyze_views(self) -> None:
        """分析视图定义"""
        for app in self.apps:
            views_file = Path(app.path) / 'views.py'
            if views_file.exists():
                self.analyze_view_file(views_file, app.name)
    
    def analyze_view_file(self, views_file: Path, app_name: str) -> None:
        """分析视图文件"""
        try:
            with open(views_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and self.is_django_view(node):
                    self.validate_view_function(node, str(views_file))
                elif isinstance(node, ast.ClassDef) and self.is_django_class_view(node):
                    self.validate_class_view(node, str(views_file))
        
        except Exception as e:
            self.issues.append(DjangoIssue(
                severity='medium',
                type='analysis',
                file=str(views_file),
                message=f'视图文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def validate_view_function(self, node: ast.FunctionDef, file_path: str) -> None:
        """验证视图函数"""
        # 检查返回值
        has_return = False
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                has_return = True
                break
        
        if not has_return:
            self.issues.append(DjangoIssue(
                severity='medium',
                type='view',
                file=file_path,
                message=f'视图函数{node.name}缺少返回值',
                suggestion='视图函数必须返回HttpResponse或渲染模板',
                line=node.lineno
            ))
    
    def validate_class_view(self, node: ast.ClassDef, file_path: str) -> None:
        """验证类视图"""
        # 检查是否继承自正确的基类
        has_valid_base = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'View':
                has_valid_base = True
                break
            elif isinstance(base, ast.Attribute) and base.attr == 'View':
                has_valid_base = True
                break
        
        if not has_valid_base:
            self.issues.append(DjangoIssue(
                severity='medium',
                type='view',
                file=file_path,
                message=f'类视图{node.name}没有继承正确的基类',
                suggestion='继承自django.views.View或其子类',
                line=node.lineno
            ))
    
    def analyze_urls(self) -> None:
        """分析URL配置"""
        # 分析主URL配置
        main_urls = self.project_path / 'urls.py'
        if main_urls.exists():
            self.analyze_url_file(main_urls, 'main')
        
        # 分析应用URL配置
        for app in self.apps:
            app_urls = Path(app.path) / 'urls.py'
            if app_urls.exists():
                self.analyze_url_file(app_urls, app.name)
    
    def analyze_url_file(self, urls_file: Path, context: str) -> None:
        """分析URL文件"""
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查URL模式
            if 'urlpatterns' not in content:
                self.issues.append(DjangoIssue(
                    severity='high',
                    type='url',
                    file=str(urls_file),
                    message=f'URL配置文件缺少urlpatterns',
                    suggestion='定义urlpatterns列表'
                ))
            
            # 检查是否包含应用URL
            if context == 'main':
                if 'include(' not in content:
                    self.issues.append(DjangoIssue(
                        severity='medium',
                        type='url',
                        file=str(urls_file),
                        message='主URL配置未包含应用URL',
                        suggestion='使用include()包含应用URL配置'
                    ))
        
        except Exception as e:
            self.issues.append(DjangoIssue(
                severity='medium',
                type='analysis',
                file=str(urls_file),
                message=f'URL文件分析失败: {e}',
                suggestion='检查文件语法和编码'
            ))
    
    def generate_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        summary = {
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i.severity == 'critical']),
            'high_issues': len([i for i in self.issues if i.severity == 'high']),
            'medium_issues': len([i for i in self.issues if i.severity == 'medium']),
            'low_issues': len([i for i in self.issues if i.severity == 'low']),
            'total_apps': len(self.apps),
            'total_models': len(self.models)
        }
        
        recommendations = self.generate_recommendations()
        
        return {
            'summary': summary,
            'apps': [self.app_to_dict(app) for app in self.apps],
            'models': [self.model_to_dict(model) for model in self.models],
            'issues': [self.issue_to_dict(issue) for issue in self.issues],
            'recommendations': recommendations,
            'health_score': self.calculate_health_score(summary)
        }
    
    def app_to_dict(self, app: DjangoApp) -> Dict[str, Any]:
        """将应用转换为字典"""
        return {
            'name': app.name,
            'path': app.path,
            'models': app.models,
            'views': app.views,
            'urls': app.urls,
            'issues': app.issues
        }
    
    def model_to_dict(self, model: DjangoModel) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'name': model.name,
            'file': model.file,
            'fields': model.fields,
            'relationships': model.relationships,
            'issues': model.issues
        }
    
    def issue_to_dict(self, issue: DjangoIssue) -> Dict[str, Any]:
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
        
        if issue_types.get('security', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'security',
                'message': f'发现{issue_types["security"]}个安全问题',
                suggestion: '加强Django安全配置'
            })
        
        if issue_types.get('model', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'type': 'model',
                'message': f'发现{issue_types["model"]}个模型问题',
                suggestion: '优化模型设计和ORM查询'
            })
        
        if issue_types.get('view', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                type='view',
                'message': f'发现{issue_types["view"]}个视图问题',
                suggestion: '完善视图处理逻辑'
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

# Django性能优化器
class DjangoOptimizer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def optimize_project(self) -> Dict[str, Any]:
        """优化Django项目"""
        optimizations = []
        
        # 检查并优化配置
        config_optimization = self.optimize_configuration()
        if config_optimization:
            optimizations.append(config_optimization)
        
        # 检查并优化数据库
        db_optimization = self.optimize_database()
        if db_optimization:
            optimizations.append(db_optimization)
        
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
    
    def optimize_configuration(self) -> Optional[Dict[str, str]]:
        """优化配置"""
        # 检查是否有缓存配置
        settings_files = self.find_settings_files()
        
        for settings_file in settings_files:
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'CACHES' not in content:
                    return {
                        'type': 'configuration',
                        'message': '添加缓存配置',
                        'suggestion': '配置Redis或Memcached缓存提升性能'
                    }
            except Exception:
                pass
        
        return None
    
    def optimize_database(self) -> Optional[Dict[str, str]]:
        """优化数据库配置"""
        settings_files = self.find_settings_files()
        
        for settings_file in settings_files:
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查数据库连接池配置
                if 'CONN_MAX_AGE' not in content:
                    return {
                        'type': 'database',
                        'message': '配置数据库连接池',
                        'suggestion': '设置CONN_MAX_AGE复用数据库连接'
                    }
            except Exception:
                pass
        
        return None
    
    def optimize_performance(self) -> Optional[Dict[str, str]]:
        """优化性能配置"""
        # 检查是否有静态文件配置
        settings_files = self.find_settings_files()
        
        for settings_file in settings_files:
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查静态文件服务
                if 'STATIC_ROOT' not in content:
                    return {
                        'type': 'performance',
                        'message': '配置静态文件服务',
                        'suggestion': '设置STATIC_ROOT和STATIC_URL用于生产环境'
                    }
            except Exception:
                pass
        
        return None
    
    def find_settings_files(self) -> List[Path]:
        """查找settings文件"""
        settings_files = []
        
        # 查找settings.py
        settings_py = self.project_path / 'settings.py'
        if settings_py.exists():
            settings_files.append(settings_py)
        
        # 查找settings目录
        settings_dir = self.project_path / 'settings'
        if settings_dir.exists():
            for file in settings_dir.glob('*.py'):
                if not file.name.startswith('__'):
                    settings_files.append(file)
        
        return settings_files
    
    def estimate_improvements(self, optimizations: List[Dict[str, str]]) -> Dict[str, int]:
        """估算改进效果"""
        improvements = {
            'performance': 0,
            'security': 0,
            'maintainability': 0
        }
        
        for opt in optimizations:
            if opt['type'] == 'database':
                improvements['performance'] += 25
            elif opt['type'] == 'configuration':
                improvements['performance'] += 20
            elif opt['type'] == 'performance':
                improvements['performance'] += 15
        
        return improvements

# 使用示例
def main():
    # 分析Django项目
    analyzer = DjangoAnalyzer('./my-django-project')
    report = analyzer.analyze_project()
    
    print("Django项目分析报告:")
    print(f"健康评分: {report['health_score']}")
    print(f"问题总数: {report['summary']['total_issues']}")
    print(f"应用总数: {report['summary']['total_apps']}")
    print(f"模型总数: {report['summary']['total_models']}")
    
    print("\n优化建议:")
    for rec in report['recommendations']:
        print(f"- {rec['message']}: {rec['suggestion']}")
    
    # 优化项目
    optimizer = DjangoOptimizer('./my-django-project')
    optimization = optimizer.optimize_project()
    
    print("\n优化建议:")
    for opt in optimization['optimizations']:
        print(f"- {opt['message']}: {opt['suggestion']}")

if __name__ == '__main__':
    main()
```

### Django性能监控器
```python
import time
import psutil
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from dataclasses import dataclass
from typing import Dict, Any, List
import threading
import json

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
    db_queries: int

@dataclass
class DatabaseMetrics:
    """数据库指标"""
    queries_count: int
    queries_time: float
    slow_queries: List[str]
    connection_usage: int

class DjangoPerformanceMonitor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.requests: List[RequestMetrics] = []
            self.start_time = time.time()
            self.initialized = True
    
    def record_request(self, request, response, duration: float, db_queries: int):
        """记录请求指标"""
        metrics = RequestMetrics(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration=duration,
            timestamp=time.time(),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip=self.get_client_ip(request),
            db_queries=db_queries
        )
        
        self.requests.append(metrics)
        
        # 保持最近1000个请求
        if len(self.requests) > 1000:
            self.requests.pop(0)
    
    def get_client_ip(self, request) -> str:
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or ''
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        request_stats = self.calculate_request_stats()
        performance_stats = self.get_performance_stats()
        database_stats = self.get_database_stats()
        cache_stats = self.get_cache_stats()
        
        return {
            "timestamp": time.time(),
            "uptime": time.time() - self.start_time,
            "request_stats": request_stats,
            "performance_stats": performance_stats,
            "database_stats": database_stats,
            "cache_stats": cache_stats
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
                "p99_response_time": 0,
                "average_db_queries": 0
            }
        
        total_requests = len(self.requests)
        uptime = time.time() - self.start_time
        requests_per_second = total_requests / uptime if uptime > 0 else 0
        
        response_times = [req.duration for req in self.requests]
        average_response_time = sum(response_times) / len(response_times)
        
        error_requests = [req for req in self.requests if req.status_code >= 400]
        error_rate = len(error_requests) / total_requests * 100 if total_requests > 0 else 0
        
        db_queries = [req.db_queries for req in self.requests]
        average_db_queries = sum(db_queries) / len(db_queries)
        
        return {
            "total_requests": total_requests,
            "requests_per_second": requests_per_second,
            "average_response_time": average_response_time,
            "error_rate": error_rate,
            "p95_response_time": self.calculate_percentile(response_times, 95),
            "p99_response_time": self.calculate_percentile(response_times, 99),
            "average_db_queries": average_db_queries
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_mb": psutil.virtual_memory().used / 1024 / 1024,
            "active_connections": len(psutil.net_connections()),
            "process_count": len(psutil.pids())
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计"""
        try:
            # 获取当前连接信息
            connections = connection.connection
            
            return {
                "is_connected": connections is not None,
                "vendor": connections.vendor if connections else "unknown",
                "database": connections.settings_dict.get('NAME', 'unknown') if connections else 'unknown',
                "host": connections.settings_dict.get('HOST', 'localhost') if connections else 'localhost'
            }
        except Exception:
            return {
                "is_connected": False,
                "error": "Unable to get database info"
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            # 测试缓存连接
            cache_key = 'django_performance_monitor_test'
            cache.set(cache_key, 'test', 10)
            cache_value = cache.get(cache_key)
            cache.delete(cache_key)
            
            return {
                "cache_available": cache_value == 'test',
                "cache_backend": getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown')
            }
        except Exception:
            return {
                "cache_available": False,
                "error": "Cache not available"
            }
    
    def calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

# 性能监控中间件
class PerformanceMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.monitor = DjangoPerformanceMonitor()
    
    def __call__(self, request):
        start_time = time.time()
        
        # 记录查询数量
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # 获取查询数量（仅在DEBUG=True时可用）
        if settings.DEBUG:
            db_queries = len(connection.queries) - initial_queries
        else:
            db_queries = 0
        
        # 记录请求指标
        self.monitor.record_request(request, response, duration, db_queries)
        
        return response

# 性能监控视图
@method_decorator(require_http_methods(["GET"]), name='dispatch')
class PerformanceMetricsView(View):
    def get(self, request):
        """获取性能指标"""
        monitor = DjangoPerformanceMonitor()
        metrics = monitor.get_metrics()
        
        return JsonResponse(metrics)

@method_decorator(require_http_methods(["GET"]), name='dispatch')
class HealthCheckView(View):
    def get(self, request):
        """健康检查"""
        monitor = DjangoPerformanceMonitor()
        
        # 简单的健康检查
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - monitor.start_time
        }
        
        # 检查数据库连接
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status["database"] = "healthy"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["database"] = f"error: {e}"
        
        # 检查缓存
        try:
            cache.set('health_check', 'ok', 10)
            cache_value = cache.get('health_check')
            if cache_value == 'ok':
                health_status["cache"] = "healthy"
            else:
                health_status["cache"] = "error"
            cache.delete('health_check')
        except Exception as e:
            health_status["cache"] = f"error: {e}"
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JsonResponse(health_status, status=status_code)

# 性能监控装饰器
def monitor_performance(func):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            # 可以在这里记录函数级别的性能数据
            print(f"Function {func.__name__} took {duration:.3f} seconds")
    
    return wrapper

# ORM查询优化装饰器
def optimize_queryset(func):
    """查询集优化装饰器"""
    def wrapper(*args, **kwargs):
        queryset = func(*args, **kwargs)
        
        # 自动添加select_related和prefetch_related
        # 这是一个简化的实现，实际需要根据具体查询优化
        if hasattr(queryset, 'model'):
            model = queryset.model
            # 检查外键关系
            for field in model._meta.fields:
                if field.is_relation and field.many_to_one:
                    queryset = queryset.select_related(field.name)
        
        return queryset
    
    return wrapper

# 使用示例
# 在settings.py中添加中间件
# MIDDLEWARE = [
#     ...
#     'path.to.PerformanceMonitoringMiddleware',
#     ...
# ]

# 在urls.py中添加监控端点
# urlpatterns = [
#     ...
#     path('metrics/', PerformanceMetricsView.as_view(), name='performance_metrics'),
#     path('health/', HealthCheckView.as_view(), name='health_check'),
#     ...
# ]

# 在视图中使用装饰器
# @monitor_performance
# def my_view(request):
#     # 视图逻辑
#     pass

# @optimize_queryset
# def get_users_queryset():
#     return User.objects.all()
```

## Django Web框架最佳实践

### 项目结构
1. **应用划分**: 合理划分应用职责
2. **配置管理**: 分环境配置管理
3. **静态文件**: 统一静态文件处理
4. **模板组织**: 优化模板继承结构
5. **测试覆盖**: 完善的测试体系

### ORM优化
1. **查询优化**: 使用select_related和prefetch_related
2. **索引优化**: 添加适当的数据库索引
3. **批量操作**: 使用批量创建和更新
4. **缓存策略**: 合理使用查询缓存
5. **连接池**: 配置数据库连接池

### 安全配置
1. **DEBUG设置**: 生产环境关闭DEBUG
2. **SECRET_KEY**: 使用环境变量管理
3. **CSRF保护**: 启用CSRF中间件
4. **SQL注入**: 使用ORM防止注入
5. **XSS防护**: 模板自动转义

### 性能优化
1. **缓存配置**: 配置Redis或Memcached
2. **静态文件**: 使用CDN服务静态文件
3. **数据库优化**: 优化数据库配置
4. **中间件优化**: 精简中间件配置
5. **监控告警**: 实时性能监控

## 相关技能

- **python-development** - Python开发
- **database-optimization** - 数据库优化
- **web-security** - Web安全
- **restful-api-design** - RESTful API设计
