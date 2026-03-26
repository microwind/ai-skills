# 文档生成参考文档

## 文档生成概述

### 什么是文档生成
文档生成是通过自动化工具从源代码、注释和配置文件中提取信息，按照预定义模板和规则生成结构化文档的过程。它能够保持文档与代码的同步性，减少手工维护文档的工作量，提高文档的质量和一致性。

### 核心价值
- **自动化维护**: 代码变更时自动更新文档
- **一致性保证**: 统一的文档格式和风格
- **完整性覆盖**: 自动提取所有API和类信息
- **多格式支持**: 生成HTML、PDF、Markdown等多种格式
- **多语言支持**: 支持中文、英文等多种语言
- **版本同步**: 文档版本与代码版本保持同步

### 文档类型
- **API文档**: 函数、类、接口的详细说明
- **用户文档**: 使用指南和教程
- **开发者文档**: 架构设计和开发规范
- **部署文档**: 安装配置和运维指南
- **技术文档**: 技术原理和最佳实践

## 文档生成核心实现

### 代码分析引擎
```python
# documentation_generator.py
import ast
import inspect
import importlib
import os
import re
import json
import yaml
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import importlib.util
import types

class DocumentationType(Enum):
    """文档类型枚举"""
    API = "api"
    USER = "user"
    DEVELOPER = "developer"
    DEPLOYMENT = "deployment"
    TECHNICAL = "technical"
    COMPREHENSIVE = "comprehensive"

class OutputFormat(Enum):
    """输出格式枚举"""
    HTML = "html"
    MARKDOWN = "markdown"
    PDF = "pdf"
    WORD = "word"
    LATEX = "latex"
    CUSTOM = "custom"

class ElementType(Enum):
    """代码元素类型枚举"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    DECORATOR = "decorator"

@dataclass
class DocumentationElement:
    """文档元素"""
    name: str
    element_type: ElementType
    file_path: str
    line_number: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    returns: Optional[Dict[str, Any]] = None
    raises: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)
    deprecated: bool = False
    since_version: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class DocumentationPage:
    """文档页面"""
    title: str
    content: str
    file_path: str
    elements: List[DocumentationElement]
    toc_items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentationProject:
    """文档项目"""
    name: str
    version: str
    description: str
    author: str
    pages: List[DocumentationPage]
    index_page: Optional[DocumentationPage] = None
    navigation: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.elements = []
        self.imports = defaultdict(set)
        self.type_hints = {}
    
    def analyze_file(self, file_path: str) -> List[DocumentationElement]:
        """分析Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            elements = []
            
            # 分析模块级别的元素
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    element = self._analyze_function(node, file_path)
                    elements.append(element)
                elif isinstance(node, ast.ClassDef):
                    element = self._analyze_class(node, file_path)
                    elements.append(element)
                elif isinstance(node, ast.Assign):
                    elements.extend(self._analyze_variables(node, file_path))
                elif isinstance(node, ast.Import):
                    self._analyze_import(node)
                elif isinstance(node, ast.ImportFrom):
                    self._analyze_import_from(node)
            
            return elements
        
        except Exception as e:
            self.logger.error(f"分析文件失败 {file_path}: {e}")
            return []
    
    def analyze_directory(self, directory_path: str) -> Dict[str, List[DocumentationElement]]:
        """分析目录中的所有Python文件"""
        all_elements = {}
        
        for root, dirs, files in os.walk(directory_path):
            # 跳过__pycache__目录
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    module_name = Path(file_path).stem
                    elements = self.analyze_file(file_path)
                    all_elements[module_name] = elements
        
        return all_elements
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> DocumentationElement:
        """分析函数"""
        # 提取参数信息
        parameters = []
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'annotation': ast.unparse(arg.annotation) if arg.annotation else None,
                'default': None,
                'type': 'positional'
            }
            parameters.append(param_info)
        
        # 提取返回类型
        returns = None
        if node.returns:
            returns = {
                'type': ast.unparse(node.returns),
                'description': None
            }
        
        # 提取文档字符串
        docstring = ast.get_docstring(node)
        
        # 解析文档字符串
        doc_info = self._parse_docstring(docstring) if docstring else {}
        
        element = DocumentationElement(
            name=node.name,
            element_type=ElementType.FUNCTION,
            file_path=file_path,
            line_number=node.lineno,
            docstring=docstring,
            signature=self._get_function_signature(node),
            parameters=parameters,
            returns=returns,
            raises=doc_info.get('raises', []),
            examples=doc_info.get('examples', []),
            see_also=doc_info.get('see_also', []),
            deprecated=doc_info.get('deprecated', False),
            since_version=doc_info.get('since'),
            tags=doc_info.get('tags', [])
        )
        
        return element
    
    def _analyze_class(self, node: ast.ClassDef, file_path: str) -> DocumentationElement:
        """分析类"""
        # 提取类文档字符串
        docstring = ast.get_docstring(node)
        doc_info = self._parse_docstring(docstring) if docstring else {}
        
        # 提取类方法
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._analyze_function(item, file_path)
                method.element_type = ElementType.METHOD
                methods.append(method)
        
        # 提取基类
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(ast.unparse(base))
        
        element = DocumentationElement(
            name=node.name,
            element_type=ElementType.CLASS,
            file_path=file_path,
            line_number=node.lineno,
            docstring=docstring,
            signature=f"class {node.name}({', '.join(base_classes)})",
            parameters=[],
            returns=None,
            raises=doc_info.get('raises', []),
            examples=doc_info.get('examples', []),
            see_also=doc_info.get('see_also', []),
            deprecated=doc_info.get('deprecated', False),
            since_version=doc_info.get('since'),
            tags=doc_info.get('tags', [])
        )
        
        return element
    
    def _analyze_variables(self, node: ast.Assign, file_path: str) -> List[DocumentationElement]:
        """分析变量"""
        elements = []
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                element = DocumentationElement(
                    name=target.id,
                    element_type=ElementType.VARIABLE,
                    file_path=file_path,
                    line_number=node.lineno,
                    docstring=None,
                    signature=f"{target.id} = {ast.unparse(node.value)}",
                    parameters=[],
                    returns=None
                )
                elements.append(element)
        
        return elements
    
    def _analyze_import(self, node: ast.Import):
        """分析import语句"""
        for alias in node.names:
            self.imports[alias.name].add('import')
    
    def _analyze_import_from(self, node: ast.ImportFrom):
        """分析from...import语句"""
        if node.module:
            for alias in node.names:
                self.imports[f"{node.module}.{alias.name}"].add('import_from')
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """获取函数签名"""
        args = []
        
        # 位置参数
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # 默认参数
        for i, default in enumerate(node.args.defaults):
            if i < len(args):
                args[-(i+1)] += f" = {ast.unparse(default)}"
        
        # 可变参数
        if node.args.vararg:
            vararg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg_str)
        
        # 关键字参数
        if node.args.kwarg:
            kwarg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg_str)
        
        return f"{node.name}({', '.join(args)})"
    
    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """解析文档字符串"""
        doc_info = {
            'description': '',
            'parameters': [],
            'returns': None,
            'raises': [],
            'examples': [],
            'see_also': [],
            'deprecated': False,
            'since': None,
            'tags': []
        }
        
        if not docstring:
            return doc_info
        
        lines = docstring.split('\n')
        current_section = 'description'
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # 检查是否是段落标题
            if line.startswith(':') or line.lower() in ['parameters:', 'returns:', 'raises:', 'examples:', 'see also:', 'deprecated:', 'since:', 'tags:']:
                # 保存之前的内容
                if current_content:
                    content = '\n'.join(current_content).strip()
                    if current_section == 'description':
                        doc_info['description'] = content
                    elif current_section == 'examples':
                        doc_info['examples'].append(content)
                    elif current_section == 'see also':
                        doc_info['see_also'].extend([item.strip() for item in content.split(',')])
                    elif current_section == 'tags':
                        doc_info['tags'].extend([item.strip() for item in content.split(',')])
                
                current_content = []
                
                # 确定新段落
                if line.startswith(':param'):
                    current_section = 'parameters'
                    param_match = re.match(r':param\s+(\w+):\s*(.*)', line)
                    if param_match:
                        param_name = param_match.group(1)
                        param_desc = param_match.group(2)
                        doc_info['parameters'].append({'name': param_name, 'description': param_desc})
                elif line.startswith(':type'):
                    # 参数类型信息
                    pass
                elif line.startswith(':return'):
                    current_section = 'returns'
                    return_match = re.match(r':return:\s*(.*)', line)
                    if return_match:
                        doc_info['returns'] = {'description': return_match.group(1)}
                elif line.startswith(':rtype'):
                    # 返回类型信息
                    pass
                elif line.startswith(':raises'):
                    current_section = 'raises'
                    raise_match = re.match(r':raises\s+(\w+):\s*(.*)', line)
                    if raise_match:
                        exception_type = raise_match.group(1)
                        exception_desc = raise_match.group(2)
                        doc_info['raises'].append({'type': exception_type, 'description': exception_desc})
                elif line.lower().startswith('examples:'):
                    current_section = 'examples'
                elif line.lower().startswith('see also:'):
                    current_section = 'see also'
                elif line.lower().startswith('deprecated:'):
                    current_section = 'deprecated'
                    doc_info['deprecated'] = True
                elif line.lower().startswith('since:'):
                    current_section = 'since'
                    since_match = re.match(r'since:\s*(.*)', line, re.IGNORECASE)
                    if since_match:
                        doc_info['since'] = since_match.group(1)
                elif line.lower().startswith('tags:'):
                    current_section = 'tags'
                else:
                    current_section = 'description'
                    current_content.append(line)
            else:
                current_content.append(line)
        
        # 处理最后的内容
        if current_content:
            content = '\n'.join(current_content).strip()
            if current_section == 'description':
                doc_info['description'] = content
            elif current_section == 'examples':
                doc_info['examples'].append(content)
            elif current_section == 'see also':
                doc_info['see_also'].extend([item.strip() for item in content.split(',')])
            elif current_section == 'tags':
                doc_info['tags'].extend([item.strip() for item in content.split(',')])
        
        return doc_info

class TemplateEngine:
    """模板引擎"""
    
    def __init__(self, template_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.template_path = template_path
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载模板"""
        # 默认模板
        self.templates['page'] = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - {{ project_name }}</title>
    <link rel="stylesheet" href="{{ css_path }}">
</head>
<body>
    <header>
        <h1>{{ project_name }}</h1>
        <nav>
            {% for item in navigation %}
            <a href="{{ item.url }}">{{ item.title }}</a>
            {% endfor %}
        </nav>
    </header>
    <main>
        <h2>{{ title }}</h2>
        {{ content }}
    </main>
    <footer>
        <p>Generated on {{ generation_time }}</p>
    </footer>
</body>
</html>
        """
        
        self.templates['api_page'] = """
# {{ title }}

{{ description }}

## Functions

{% for function in functions %}
### {{ function.name }}

```python
{{ function.signature }}
```

{{ function.description }}

**Parameters:**
{% for param in function.parameters %}
- `{{ param.name }}` ({{ param.annotation or 'any' }}): {{ param.description or 'No description' }}
{% endfor %}

**Returns:**
{{ returns.description or 'No description' }}

{% if function.raises %}
**Raises:**
{% for exc in function.raises %}
- `{{ exc.type }}`: {{ exc.description }}
{% endfor %}
{% endif %}

{% if function.examples %}
**Examples:**
{% for example in function.examples %}
```python
{{ example }}
```
{% endfor %}
{% endif %}

{% endfor %}

## Classes

{% for class in classes %}
### {{ class.name }}

```python
{{ class.signature }}
```

{{ class.description }}

{% if class.methods %}
**Methods:**
{% for method in class.methods %}
- `{{ method.name }}`: {{ method.description or 'No description' }}
{% endfor %}
{% endif %}

{% if class.examples %}
**Examples:**
{% for example in class.examples %}
```python
{{ example }}
```
{% endfor %}
{% endif %}

{% endfor %}
        """
        
        self.templates['index'] = """
# {{ project_name }}

{{ description }}

## Table of Contents

{% for page in pages %}
- [{{ page.title }}]({{ page.file_path }})
{% endfor %}

## API Reference

{% for module in modules %}
### {{ module.name }}

{% for element in module.elements %}
- [`{{ element.name }}`](#{{ element.name }}): {{ element.description or 'No description' }}
{% endfor %}

{% endfor %}
        """
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"模板 '{template_name}' 不存在")
        
        # 简单的模板渲染
        rendered = template
        
        # 替换简单变量
        for key, value in context.items():
            if isinstance(value, str):
                rendered = rendered.replace(f"{{{{ {key} }}}}", value)
            elif isinstance(value, (list, dict)):
                # 处理复杂结构
                rendered = self._render_complex_structure(rendered, key, value)
        
        return rendered
    
    def _render_complex_structure(self, template: str, key: str, value: Any) -> str:
        """渲染复杂结构"""
        if isinstance(value, list):
            # 处理列表
            pattern = rf"{{%\s*for\s+\w+\s+in\s+{key}\s*%}}(.*?){{%\s*endfor\s*%}}"
            matches = re.finditer(pattern, template, re.DOTALL)
            
            for match in matches:
                loop_content = match.group(1)
                rendered_items = []
                
                for item in value:
                    item_content = loop_content
                    if isinstance(item, dict):
                        for item_key, item_value in item.items():
                            if isinstance(item_value, str):
                                item_content = item_content.replace(f"{{{{ {item_key} }}}}", item_value)
                    elif isinstance(item, str):
                        item_content = item_content.replace(f"{{{{ item }}}}", item)
                    
                    rendered_items.append(item_content)
                
                template = template.replace(match.group(0), '\n'.join(rendered_items))
        
        return template

class DocumentationGenerator:
    """文档生成器主类"""
    
    def __init__(self, project_name: str, output_dir: str = "docs"):
        self.logger = logging.getLogger(__name__)
        self.project_name = project_name
        self.output_dir = output_dir
        self.analyzer = CodeAnalyzer()
        self.template_engine = TemplateEngine()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_documentation(self, source_dir: str, 
                              doc_type: DocumentationType = DocumentationType.API,
                              output_format: OutputFormat = OutputFormat.HTML) -> DocumentationProject:
        """生成文档"""
        self.logger.info(f"开始生成文档: {self.project_name}")
        
        # 分析源代码
        all_elements = self.analyzer.analyze_directory(source_dir)
        
        # 创建文档项目
        project = DocumentationProject(
            name=self.project_name,
            version="1.0.0",
            description=f"Generated documentation for {self.project_name}",
            author="Documentation Generator",
            pages=[],
            metadata={
                'generation_time': datetime.now().isoformat(),
                'source_dir': source_dir,
                'doc_type': doc_type.value,
                'output_format': output_format.value
            }
        )
        
        # 生成文档页面
        for module_name, elements in all_elements.items():
            page = self._generate_module_page(module_name, elements, doc_type)
            project.pages.append(page)
        
        # 生成索引页面
        index_page = self._generate_index_page(project)
        project.index_page = index_page
        
        # 生成导航
        project.navigation = self._generate_navigation(project)
        
        # 写入文件
        self._write_documentation(project, output_format)
        
        self.logger.info(f"文档生成完成，共生成 {len(project.pages)} 个页面")
        
        return project
    
    def _generate_module_page(self, module_name: str, 
                             elements: List[DocumentationElement],
                             doc_type: DocumentationType) -> DocumentationPage:
        """生成模块页面"""
        # 按类型分组元素
        functions = [e for e in elements if e.element_type == ElementType.FUNCTION]
        classes = [e for e in elements if e.element_type == ElementType.CLASS]
        variables = [e for e in elements if e.element_type == ElementType.VARIABLE]
        
        # 生成页面内容
        if doc_type == DocumentationType.API:
            content = self.template_engine.render_template('api_page', {
                'title': module_name,
                'description': f"API documentation for {module_name}",
                'functions': functions,
                'classes': classes,
                'variables': variables
            })
        else:
            # 生成通用页面内容
            content = f"# {module_name}\n\n"
            
            if functions:
                content += "## Functions\n\n"
                for func in functions:
                    content += f"### {func.name}\n\n"
                    content += f"```python\n{func.signature}\n```\n\n"
                    if func.docstring:
                        content += f"{func.docstring}\n\n"
            
            if classes:
                content += "## Classes\n\n"
                for cls in classes:
                    content += f"### {cls.name}\n\n"
                    content += f"```python\n{cls.signature}\n```\n\n"
                    if cls.docstring:
                        content += f"{cls.docstring}\n\n"
        
        # 生成目录项
        toc_items = []
        for func in functions:
            toc_items.append({'title': func.name, 'level': 2, 'anchor': func.name})
        for cls in classes:
            toc_items.append({'title': cls.name, 'level': 2, 'anchor': cls.name})
        
        page = DocumentationPage(
            title=module_name,
            content=content,
            file_path=f"{module_name}.html",
            elements=elements,
            toc_items=toc_items,
            metadata={'module_name': module_name}
        )
        
        return page
    
    def _generate_index_page(self, project: DocumentationProject) -> DocumentationPage:
        """生成索引页面"""
        content = self.template_engine.render_template('index', {
            'project_name': project.name,
            'description': project.description,
            'pages': project.pages,
            'modules': [{'name': page.metadata.get('module_name', page.title), 
                       'elements': page.elements} for page in project.pages]
        })
        
        index_page = DocumentationPage(
            title="Index",
            content=content,
            file_path="index.html",
            elements=[],
            toc_items=[],
            metadata={'is_index': True}
        )
        
        return index_page
    
    def _generate_navigation(self, project: DocumentationProject) -> List[Dict[str, Any]]:
        """生成导航"""
        navigation = []
        
        # 添加首页
        if project.index_page:
            navigation.append({
                'title': 'Home',
                'url': project.index_page.file_path,
                'active': True
            })
        
        # 添加其他页面
        for page in project.pages:
            navigation.append({
                'title': page.title,
                'url': page.file_path,
                'active': False
            })
        
        return navigation
    
    def _write_documentation(self, project: DocumentationProject, 
                            output_format: OutputFormat):
        """写入文档文件"""
        if output_format == OutputFormat.HTML:
            self._write_html_documentation(project)
        elif output_format == OutputFormat.MARKDOWN:
            self._write_markdown_documentation(project)
        else:
            self.logger.warning(f"暂不支持输出格式: {output_format}")
    
    def _write_html_documentation(self, project: DocumentationProject):
        """写入HTML文档"""
        # 写入索引页面
        if project.index_page:
            index_content = self.template_engine.render_template('page', {
                'title': project.index_page.title,
                'project_name': project.name,
                'content': project.index_page.content,
                'navigation': project.navigation,
                'generation_time': project.metadata['generation_time'],
                'lang': 'zh-CN',
                'css_path': 'styles.css'
            })
            
            index_path = os.path.join(self.output_dir, project.index_page.file_path)
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
        
        # 写入其他页面
        for page in project.pages:
            page_content = self.template_engine.render_template('page', {
                'title': page.title,
                'project_name': project.name,
                'content': page.content,
                'navigation': project.navigation,
                'generation_time': project.metadata['generation_time'],
                'lang': 'zh-CN',
                'css_path': 'styles.css'
            })
            
            page_path = os.path.join(self.output_dir, page.file_path)
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(page_content)
        
        # 生成CSS样式文件
        self._generate_css_file()
    
    def _write_markdown_documentation(self, project: DocumentationProject):
        """写入Markdown文档"""
        # 写入索引页面
        if project.index_page:
            index_path = os.path.join(self.output_dir, "index.md")
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(project.index_page.content)
        
        # 写入其他页面
        for page in project.pages:
            page_path = os.path.join(self.output_dir, f"{page.title}.md")
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(page.content)
    
    def _generate_css_file(self):
        """生成CSS样式文件"""
        css_content = """
/* Documentation Styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
}

header {
    background-color: #007bff;
    color: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

header h1 {
    margin: 0;
    font-size: 1.8rem;
}

nav {
    margin-top: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
    margin-right: 1.5rem;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: rgba(255,255,255,0.1);
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
}

main h2 {
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

main h3 {
    color: #495057;
    margin-top: 2rem;
}

pre {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 1rem;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
}

code {
    background-color: #e9ecef;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}

footer {
    background-color: #6c757d;
    color: white;
    text-align: center;
    padding: 1rem;
    margin-top: 2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    main {
        padding: 0 1rem;
    }
    
    header {
        padding: 1rem;
    }
    
    nav a {
        display: block;
        margin: 0.5rem 0;
    }
}
        """
        
        css_path = os.path.join(self.output_dir, "styles.css")
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)

# 使用示例
if __name__ == "__main__":
    # 创建文档生成器
    generator = DocumentationGenerator(
        project_name="My Project",
        output_dir="generated_docs"
    )
    
    # 生成文档
    project = generator.generate_documentation(
        source_dir="src",
        doc_type=DocumentationType.API,
        output_format=OutputFormat.HTML
    )
    
    print(f"文档生成完成，共生成 {len(project.pages)} 个页面")
    print(f"输出目录: {generator.output_dir}")
```

## 参考资源

### 文档生成工具
- [Sphinx](https://www.sphinx-doc.org/) - Python文档生成工具
- [JSDoc](https://jsdoc.app/) - JavaScript文档生成工具
- [Javadoc](https://www.oracle.com/java/technologies/javase/javadoc/) - Java文档生成工具
- [Doxygen](https://www.doxygen.nl/) - 多语言文档生成工具
- [GitBook](https://www.gitbook.com/) - 现代文档平台

### 模板引擎
- [Jinja2](https://jinja.palletsprojects.com/) - Python模板引擎
- [Handlebars](https://handlebarsjs.com/) - JavaScript模板引擎
- [Mustache](https://mustache.github.io/) - 轻量级模板引擎
- [Liquid](https://shopify.github.io/liquid/) - Ruby模板引擎

### 静态站点生成器
- [Jekyll](https://jekyllrb.com/) - Ruby静态站点生成器
- [Hugo](https://gohugo.io/) - Go静态站点生成器
- [Gatsby](https://www.gatsbyjs.com/) - React静态站点生成器
- [Next.js](https://nextjs.org/) - React框架

### 文档最佳实践
- [Google文档风格指南](https://developers.google.com/tech-writing)
- [Microsoft文档写作指南](https://docs.microsoft.com/en-us/style-guide/)
- [技术文档写作最佳实践](https://www.writethedocs.org/)
- [API文档设计指南](https://api-docs-styleguide.github.io/)
