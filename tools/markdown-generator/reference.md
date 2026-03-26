# Markdown生成器参考文档

## Markdown生成器概述

### 什么是Markdown生成器
Markdown生成器是一个专门用于从结构化数据生成Markdown文档的工具。该工具支持多种数据源、模板引擎、自动化生成和质量控制，提供完整的文档生成、格式化、优化和发布功能，帮助开发团队和技术作者快速创建高质量的技术文档、API文档和项目文档。

### 主要功能
- **多数据源支持**: 支持JSON、YAML、数据库、API等多种数据源
- **模板引擎**: 支持Jinja2、Mustache、Handlebars等模板引擎
- **智能生成**: 自动生成目录、索引、摘要和标签
- **质量控制**: 语法检查、结构验证和内容优化
- **多文件输出**: 支持单文件和多文件文档生成
- **插件系统**: 可扩展的插件架构和自定义功能

## Markdown生成引擎

### 核心生成器
```python
# markdown_generator.py
import os
import json
import yaml
import re
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
import markdown
from markdown.extensions import codehilite, tables, toc

class DocumentType(Enum):
    TECHNICAL_DOC = "technical_doc"
    API_DOC = "api_doc"
    USER_MANUAL = "user_manual"
    BLOG_POST = "blog_post"
    PROJECT_DOC = "project_doc"
    CUSTOM = "custom"

class OutputFormat(Enum):
    STANDARD = "standard"
    GITHUB = "github"
    GITLAB = "gitlab"
    CUSTOM = "custom"

class DataSourceType(Enum):
    JSON = "json"
    YAML = "yaml"
    DATABASE = "database"
    API = "api"
    FILE = "file"

@dataclass
class DocumentConfig:
    # 基础配置
    title: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    created_date: str = ""
    updated_date: str = ""
    language: str = "zh-CN"
    
    # 文档配置
    doc_type: DocumentType = DocumentType.TECHNICAL_DOC
    output_format: OutputFormat = OutputFormat.STANDARD
    encoding: str = "utf-8"
    line_ending: str = "\n"
    
    # 结构配置
    auto_toc: bool = True
    toc_depth: int = 3
    toc_position: str = "top"
    chapter_numbering: bool = True
    chapter_format: str = "1. 2. 3."
    
    # 输出配置
    output_path: str = ""
    file_naming: str = "title"  # title, date, number, custom
    file_extension: str = ".md"
    directory_structure: str = "flat"  # flat, hierarchical, date, category
    
    # 质量控制
    enable_validation: bool = True
    spell_check: bool = True
    link_check: bool = True
    format_check: bool = True

@dataclass
class GenerationResult:
    success: bool
    output_files: List[str]
    total_files: int
    total_size: int
    generation_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

class MarkdownGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.template_env = Environment(loader=FileSystemLoader('.'))
        self.plugins = {}
        self.validators = []
        self.processors = []
        self._register_default_processors()
    
    def _register_default_processors(self):
        """注册默认处理器"""
        self.processors = [
            TableProcessor(),
            CodeProcessor(),
            LinkProcessor(),
            TocProcessor(),
            MetadataProcessor()
        ]
    
    def generate_from_data(self, data: Dict[str, Any], 
                          config: DocumentConfig,
                          template_path: Optional[str] = None) -> GenerationResult:
        """从数据生成Markdown文档"""
        start_time = datetime.now()
        
        try:
            # 验证配置
            validation_errors = self._validate_config(config)
            if validation_errors:
                return GenerationResult(
                    success=False,
                    output_files=[],
                    total_files=0,
                    total_size=0,
                    generation_time=0,
                    errors=validation_errors
                )
            
            # 准备数据
            processed_data = self._prepare_data(data, config)
            
            # 生成内容
            if template_path:
                content = self._generate_from_template(processed_data, template_path, config)
            else:
                content = self._generate_from_data(processed_data, config)
            
            # 后处理
            processed_content = self._post_process(content, config)
            
            # 保存文件
            output_files = self._save_content(processed_content, config)
            
            # 计算统计信息
            total_size = sum(os.path.getsize(f) for f in output_files)
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # 收集统计信息
            statistics = self._collect_statistics(processed_content, output_files)
            
            return GenerationResult(
                success=True,
                output_files=output_files,
                total_files=len(output_files),
                total_size=total_size,
                generation_time=generation_time,
                statistics=statistics
            )
            
        except Exception as e:
            self.logger.error(f"生成Markdown文档失败: {e}")
            return GenerationResult(
                success=False,
                output_files=[],
                total_files=0,
                total_size=0,
                generation_time=(datetime.now() - start_time).total_seconds(),
                errors=[str(e)]
            )
    
    def generate_from_file(self, file_path: str, 
                          config: DocumentConfig,
                          template_path: Optional[str] = None) -> GenerationResult:
        """从文件生成Markdown文档"""
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                elif file_path.endswith(('.yaml', '.yml')):
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"不支持的文件格式: {file_path}")
            
            return self.generate_from_data(data, config, template_path)
            
        except Exception as e:
            self.logger.error(f"读取文件失败 {file_path}: {e}")
            return GenerationResult(
                success=False,
                output_files=[],
                total_files=0,
                total_size=0,
                generation_time=0,
                errors=[f"读取文件失败: {e}"]
            )
    
    def _validate_config(self, config: DocumentConfig) -> List[str]:
        """验证配置"""
        errors = []
        
        if not config.title:
            errors.append("文档标题不能为空")
        
        if not config.output_path:
            errors.append("输出路径不能为空")
        
        if config.toc_depth < 1 or config.toc_depth > 6:
            errors.append("目录深度必须在1-6之间")
        
        return errors
    
    def _prepare_data(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        """准备数据"""
        # 添加元数据
        prepared_data = {
            'metadata': {
                'title': config.title,
                'description': config.description,
                'author': config.author,
                'version': config.version,
                'created_date': config.created_date or datetime.now().strftime('%Y-%m-%d'),
                'updated_date': config.updated_date or datetime.now().strftime('%Y-%m-%d'),
                'language': config.language
            },
            'content': data,
            'config': asdict(config)
        }
        
        # 应用数据处理器
        for processor in self.processors:
            prepared_data = processor.process(prepared_data, config)
        
        return prepared_data
    
    def _generate_from_template(self, data: Dict[str, Any], 
                                template_path: str, 
                                config: DocumentConfig) -> str:
        """从模板生成内容"""
        try:
            template = self.template_env.get_template(template_path)
            content = template.render(**data)
            return content
        except Exception as e:
            self.logger.error(f"模板渲染失败: {e}")
            raise
    
    def _generate_from_data(self, data: Dict[str, Any], config: DocumentConfig) -> str:
        """从数据生成内容"""
        content_parts = []
        
        # 添加元数据
        if config.output_format == OutputFormat.GITHUB:
            content_parts.append(f"# {data['metadata']['title']}")
            content_parts.append(f"**作者**: {data['metadata']['author']}")
            content_parts.append(f"**版本**: {data['metadata']['version']}")
            content_parts.append(f"**更新时间**: {data['metadata']['updated_date']}")
            content_parts.append("")
        
        # 生成目录
        if config.auto_toc:
            toc = self._generate_toc(data['content'], config)
            if toc:
                content_parts.append("## 目录")
                content_parts.append(toc)
                content_parts.append("")
        
        # 生成正文
        content_parts.append(self._generate_content(data['content'], config))
        
        return "\n".join(content_parts)
    
    def _generate_toc(self, data: Dict[str, Any], config: DocumentConfig) -> str:
        """生成目录"""
        toc_items = []
        
        def extract_headings(obj, level=1):
            if level > config.toc_depth:
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)) and value:
                        indent = "  " * (level - 1)
                        toc_items.append(f"{indent}- [{key}](#{self._slugify(key)})")
                        extract_headings(value, level + 1)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)) and item:
                        indent = "  " * (level - 1)
                        toc_items.append(f"{indent}- [项目 {i+1}](#项目-{i+1})")
                        extract_headings(item, level + 1)
        
        extract_headings(data)
        return "\n".join(toc_items)
    
    def _slugify(self, text: str) -> str:
        """生成URL友好的slug"""
        # 简化的slugify实现
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def _generate_content(self, data: Any, config: DocumentConfig, level: int = 1) -> str:
        """生成内容"""
        if isinstance(data, dict):
            content_parts = []
            for key, value in data.items():
                if value is None:
                    continue
                
                # 生成标题
                heading_prefix = "#" * (level + 1)
                if config.chapter_numbering and level == 1:
                    # 简化的章节编号
                    chapter_num = len(content_parts) + 1
                    title = f"{heading_prefix} {chapter_num}. {key}"
                else:
                    title = f"{heading_prefix} {key}"
                
                content_parts.append(title)
                content_parts.append("")
                
                # 生成内容
                if isinstance(value, (dict, list)):
                    content = self._generate_content(value, config, level + 1)
                    content_parts.append(content)
                else:
                    content_parts.append(str(value))
                
                content_parts.append("")
            
            return "\n".join(content_parts)
        
        elif isinstance(data, list):
            content_parts = []
            for i, item in enumerate(data):
                if item is None:
                    continue
                
                if isinstance(item, (dict, list)):
                    content = self._generate_content(item, config, level)
                    content_parts.append(content)
                else:
                    content_parts.append(f"- {item}")
            
            return "\n".join(content_parts)
        
        else:
            return str(data)
    
    def _post_process(self, content: str, config: DocumentConfig) -> str:
        """后处理内容"""
        # 应用格式化
        content = self._format_content(content, config)
        
        # 应用验证
        if config.enable_validation:
            self._validate_content(content, config)
        
        return content
    
    def _format_content(self, content: str, config: DocumentConfig) -> str:
        """格式化内容"""
        # 标准化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 添加文档结尾的空行
        if not content.endswith('\n'):
            content += '\n'
        
        # 格式化代码块
        content = self._format_code_blocks(content)
        
        # 格式化表格
        content = self._format_tables(content)
        
        return content
    
    def _format_code_blocks(self, content: str) -> str:
        """格式化代码块"""
        # 确保代码块有语言标识
        content = re.sub(r'```\s*\n', '```\n', content)
        return content
    
    def _format_tables(self, content: str) -> str:
        """格式化表格"""
        # 简化的表格格式化
        return content
    
    def _validate_content(self, content: str, config: DocumentConfig):
        """验证内容"""
        # 检查Markdown语法
        if config.format_check:
            self._check_markdown_syntax(content)
        
        # 检查链接
        if config.link_check:
            self._check_links(content)
        
        # 拼写检查
        if config.spell_check:
            self._check_spelling(content)
    
    def _check_markdown_syntax(self, content: str):
        """检查Markdown语法"""
        # 简化的语法检查
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查标题层级
            if line.startswith('#'):
                heading_level = len(line) - len(line.lstrip('#'))
                if heading_level > 6:
                    self.logger.warning(f"第{i}行: 标题层级超过6级")
            
            # 检查列表格式
            if line.strip().startswith(('-', '*', '+')):
                if not line.strip().startswith(('- ', '* ', '+ ')):
                    self.logger.warning(f"第{i}行: 列表格式可能不正确")
    
    def _check_links(self, content: str):
        """检查链接"""
        # 简化的链接检查
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        
        for text, url in matches:
            if not url.strip():
                self.logger.warning(f"链接 '{text}' 的URL为空")
    
    def _check_spelling(self, content: str):
        """拼写检查"""
        # 简化的拼写检查占位符
        pass
    
    def _save_content(self, content: str, config: DocumentConfig) -> List[str]:
        """保存内容"""
        output_files = []
        
        # 创建输出目录
        output_dir = Path(config.output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = self._generate_filename(config)
        file_path = output_dir / filename
        
        # 保存文件
        with open(file_path, 'w', encoding=config.encoding, newline='') as f:
            f.write(content.replace('\n', config.line_ending))
        
        output_files.append(str(file_path))
        
        self.logger.info(f"文档已保存: {file_path}")
        return output_files
    
    def _generate_filename(self, config: DocumentConfig) -> str:
        """生成文件名"""
        if config.file_naming == "title":
            filename = self._slugify(config.title)
        elif config.file_naming == "date":
            filename = datetime.now().strftime('%Y-%m-%d')
        elif config.file_naming == "number":
            filename = "001"
        else:
            filename = config.file_naming
        
        return f"{filename}{config.file_extension}"
    
    def _collect_statistics(self, content: str, output_files: List[str]) -> Dict[str, Any]:
        """收集统计信息"""
        stats = {
            'character_count': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'heading_count': content.count('#'),
            'link_count': content.count('['),
            'file_count': len(output_files)
        }
        
        return stats

# 处理器基类
class ContentProcessor:
    def process(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        raise NotImplementedError

class TableProcessor(ContentProcessor):
    def process(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        # 表格数据处理
        return data

class CodeProcessor(ContentProcessor):
    def process(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        # 代码数据处理
        return data

class LinkProcessor(ContentProcessor):
    def process(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        # 链接数据处理
        return data

class TocProcessor(ContentProcessor):
    def process(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        # 目录数据处理
        return data

class MetadataProcessor(ContentProcessor):
    def process(self, data: Dict[str, Any], config: DocumentConfig) -> Dict[str, Any]:
        # 元数据处理
        return data

# 使用示例
generator = MarkdownGenerator()

# 配置文档
config = DocumentConfig(
    title="技术文档示例",
    description="这是一个技术文档的示例",
    author="作者姓名",
    version="1.0.0",
    doc_type=DocumentType.TECHNICAL_DOC,
    output_format=OutputFormat.GITHUB,
    auto_toc=True,
    toc_depth=3,
    output_path="./output",
    enable_validation=True
)

# 示例数据
sample_data = {
    "概述": {
        "项目背景": "这是项目的背景介绍",
        "目标": "这是项目的目标说明",
        "范围": "这是项目的范围定义"
    },
    "架构设计": {
        "系统架构": "这是系统架构的描述",
        "技术栈": {
            "前端": "React, TypeScript",
            "后端": "Node.js, Express",
            "数据库": "PostgreSQL, Redis"
        },
        "部署架构": "这是部署架构的说明"
    },
    "API文档": {
        "用户管理": [
            "GET /api/users - 获取用户列表",
            "POST /api/users - 创建新用户",
            "PUT /api/users/:id - 更新用户信息",
            "DELETE /api/users/:id - 删除用户"
        ],
        "认证授权": [
            "POST /api/auth/login - 用户登录",
            "POST /api/auth/logout - 用户登出",
            "POST /api/auth/refresh - 刷新令牌"
        ]
    }
}

# 生成文档
result = generator.generate_from_data(sample_data, config)

if result.success:
    print(f"文档生成成功:")
    print(f"输出文件: {result.output_files}")
    print(f"文件数量: {result.total_files}")
    print(f"总大小: {result.total_size} 字节")
    print(f"生成时间: {result.generation_time:.2f} 秒")
    print(f"统计信息: {result.statistics}")
else:
    print(f"文档生成失败:")
    for error in result.errors:
        print(f"  错误: {error}")
```

## 模板引擎集成

### Jinja2模板引擎
```python
# template_engine.py
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from typing import Dict, Any, List, Optional
import os
import logging

class Jinja2TemplateEngine:
    def __init__(self, template_dir: str = "templates"):
        self.logger = logging.getLogger(__name__)
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._register_filters()
        self._register_globals()
    
    def _register_filters(self):
        """注册自定义过滤器"""
        self.env.filters['markdown'] = self._markdown_filter
        self.env.filters['slugify'] = self._slugify_filter
        self.env.filters['format_date'] = self._format_date_filter
        self.env.filters['format_size'] = self._format_size_filter
        self.env.filters['code_highlight'] = self._code_highlight_filter
    
    def _register_globals(self):
        """注册全局函数"""
        self.env.globals['now'] = self._now_function
        self.env.globals['uuid'] = self._uuid_function
        self.env.globals['range'] = range
        self.env.globals['len'] = len
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """渲染模板"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            self.logger.error(f"模板渲染失败 {template_name}: {e}")
            raise
    
    def render_string(self, template_string: str, data: Dict[str, Any]) -> str:
        """渲染字符串模板"""
        try:
            template = self.env.from_string(template_string)
            return template.render(**data)
        except Exception as e:
            self.logger.error(f"字符串模板渲染失败: {e}")
            raise
    
    def _markdown_filter(self, text: str) -> str:
        """Markdown过滤器"""
        import markdown
        return markdown.markdown(text, extensions=['codehilite', 'tables', 'toc'])
    
    def _slugify_filter(self, text: str) -> str:
        """Slugify过滤器"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def _format_date_filter(self, date_str: str, format_str: str = '%Y-%m-%d') -> str:
        """日期格式化过滤器"""
        from datetime import datetime
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime(format_str)
        except:
            return date_str
    
    def _format_size_filter(self, size: int) -> str:
        """文件大小格式化过滤器"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _code_highlight_filter(self, code: str, language: str = '') -> str:
        """代码高亮过滤器"""
        try:
            import pygments
            from pygments import lexers, formatters
            
            if language:
                lexer = lexers.get_lexer_by_name(language)
            else:
                lexer = lexers.guess_lexer(code)
            
            formatter = formatters.HtmlFormatter(style='default')
            return pygments.highlight(code, lexer, formatter)
        except ImportError:
            return f"```{language}\n{code}\n```"
    
    def _now_function(self, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """当前时间函数"""
        from datetime import datetime
        return datetime.now().strftime(format_str)
    
    def _uuid_function(self) -> str:
        """UUID生成函数"""
        import uuid
        return str(uuid.uuid4())

# 模板示例
TEMPLATE_EXAMPLE = """
# {{ metadata.title }}

**作者**: {{ metadata.author }}  
**版本**: {{ metadata.version }}  
**更新时间**: {{ metadata.updated_date | format_date }}  

## 概述

{{ metadata.description }}

## 目录

{% if content %}
{% for section_name, section_content in content.items() %}
{% if section_content is mapping %}
- [{{ section_name }}](#{{ section_name | slugify }})
{% if section_content %}
{% for subsection_name, subsection_content in section_content.items() %}
{% if subsection_content %}
  - [{{ subsection_name }}](#{{ subsection_name | slugify }})
{% endif %}
{% endfor %}
{% endif %}
{% endif %}
{% endfor %}
{% endif %}

## 详细内容

{% if content %}
{% for section_name, section_content in content.items() %}
### {{ section_name }}

{% if section_content is mapping %}
{% for subsection_name, subsection_content in section_content.items() %}
{% if subsection_content %}
#### {{ subsection_name }}

{% if subsection_content is iterable and subsection_content is not string %}
{% for item in subsection_content %}
- {{ item }}
{% endfor %}
{% else %}
{{ subsection_content }}
{% endif %}

{% endif %}
{% endfor %}
{% elif section_content is iterable and section_content is not string %}
{% for item in section_content %}
- {{ item }}
{% endfor %}
{% else %}
{{ section_content }}
{% endif %}

{% endfor %}
{% endif %}

---
*文档生成时间: {{ now() }}*
"""

# 使用示例
template_engine = Jinja2TemplateEngine()

# 渲染模板
try:
    rendered_content = template_engine.render_string(TEMPLATE_EXAMPLE, {
        'metadata': {
            'title': 'API文档示例',
            'author': '开发团队',
            'version': '1.0.0',
            'updated_date': '2024-01-15T10:30:00Z',
            'description': '这是一个API文档的示例'
        },
        'content': {
            '认证接口': {
                '登录接口': 'POST /api/auth/login',
                '登出接口': 'POST /api/auth/logout',
                '刷新令牌': 'POST /api/auth/refresh'
            },
            '用户管理': [
                'GET /api/users - 获取用户列表',
                'POST /api/users - 创建用户',
                'PUT /api/users/:id - 更新用户',
                'DELETE /api/users/:id - 删除用户'
            ]
        }
    })
    
    print("模板渲染成功:")
    print(rendered_content[:500] + "...")
    
except Exception as e:
    print(f"模板渲染失败: {e}")
```

## 插件系统

### 插件架构
```python
# plugin_system.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
import importlib
import os
from pathlib import Path

class Plugin(ABC):
    """插件基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
        self.enabled = True
    
    @abstractmethod
    def process(self, data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """处理数据"""
        pass
    
    def validate_config(self, config: Any) -> List[str]:
        """验证配置"""
        return []
    
    def get_info(self) -> Dict[str, str]:
        """获取插件信息"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': str(self.enabled)
        }

class PluginManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_hooks: Dict[str, List[Plugin]] = {}
    
    def register_plugin(self, plugin: Plugin):
        """注册插件"""
        self.plugins[plugin.name] = plugin
        self.logger.info(f"注册插件: {plugin.name}")
    
    def unregister_plugin(self, plugin_name: str):
        """注销插件"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            self.logger.info(f"注销插件: {plugin_name}")
    
    def load_plugins_from_directory(self, plugin_dir: str):
        """从目录加载插件"""
        plugin_path = Path(plugin_dir)
        if not plugin_path.exists():
            self.logger.warning(f"插件目录不存在: {plugin_dir}")
            return
        
        for file_path in plugin_path.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            
            try:
                module_name = file_path.stem
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找插件类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Plugin) and 
                        attr != Plugin):
                        plugin = attr()
                        self.register_plugin(plugin)
                        break
                        
            except Exception as e:
                self.logger.error(f"加载插件失败 {file_path}: {e}")
    
    def execute_plugins(self, hook_name: str, data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """执行插件"""
        if hook_name in self.plugin_hooks:
            for plugin in self.plugin_hooks[hook_name]:
                if plugin.enabled:
                    try:
                        data = plugin.process(data, config)
                    except Exception as e:
                        self.logger.error(f"插件执行失败 {plugin.name}: {e}")
        
        return data
    
    def add_hook(self, hook_name: str, plugin: Plugin):
        """添加钩子"""
        if hook_name not in self.plugin_hooks:
            self.plugin_hooks[hook_name] = []
        
        if plugin not in self.plugin_hooks[hook_name]:
            self.plugin_hooks[hook_name].append(plugin)
    
    def remove_hook(self, hook_name: str, plugin: Plugin):
        """移除钩子"""
        if hook_name in self.plugin_hooks:
            if plugin in self.plugin_hooks[hook_name]:
                self.plugin_hooks[hook_name].remove(plugin)
    
    def get_plugin_list(self) -> List[Dict[str, str]]:
        """获取插件列表"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def enable_plugin(self, plugin_name: str):
        """启用插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.logger.info(f"启用插件: {plugin_name}")
    
    def disable_plugin(self, plugin_name: str):
        """禁用插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self.logger.info(f"禁用插件: {plugin_name}")

# 示例插件
class TableOfContentsPlugin(Plugin):
    """目录生成插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "TableOfContentsPlugin"
        self.description = "自动生成目录"
        self.author = "AI Skills Team"
    
    def process(self, data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """生成目录"""
        if 'content' not in data:
            return data
        
        toc = self._generate_toc(data['content'])
        data['table_of_contents'] = toc
        
        return data
    
    def _generate_toc(self, content: Any, level: int = 1) -> List[Dict[str, Any]]:
        """生成目录结构"""
        toc = []
        
        if isinstance(content, dict):
            for key, value in content.items():
                if value:
                    toc_item = {
                        'title': key,
                        'level': level,
                        'anchor': self._slugify(key),
                        'children': []
                    }
                    
                    if isinstance(value, (dict, list)):
                        toc_item['children'] = self._generate_toc(value, level + 1)
                    
                    toc.append(toc_item)
        
        return toc
    
    def _slugify(self, text: str) -> str:
        """生成锚点"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

class CodeBlockPlugin(Plugin):
    """代码块处理插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "CodeBlockPlugin"
        self.description = "处理代码块格式"
        self.author = "AI Skills Team"
    
    def process(self, data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """处理代码块"""
        # 递归处理数据中的代码块
        self._process_code_blocks(data)
        return data
    
    def _process_code_blocks(self, obj: Any):
        """递归处理代码块"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and self._is_code_block(value):
                    obj[key] = self._format_code_block(value)
                else:
                    self._process_code_blocks(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and self._is_code_block(item):
                    obj[i] = self._format_code_block(item)
                else:
                    self._process_code_blocks(item)
    
    def _is_code_block(self, text: str) -> bool:
        """判断是否为代码块"""
        return '```' in text or text.strip().startswith('    ')
    
    def _format_code_block(self, code: str) -> str:
        """格式化代码块"""
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith('```'):
                if line.startswith('    '):
                    formatted_lines.append(line[4:])
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

# 使用示例
plugin_manager = PluginManager()

# 注册插件
plugin_manager.register_plugin(TableOfContentsPlugin())
plugin_manager.register_plugin(CodeBlockPlugin())

# 添加钩子
plugin_manager.add_hook("pre_process", plugin_manager.plugins["TableOfContentsPlugin"])
plugin_manager.add_hook("post_process", plugin_manager.plugins["CodeBlockPlugin"])

# 获取插件列表
plugins = plugin_manager.get_plugin_list()
print("已注册的插件:")
for plugin_info in plugins:
    print(f"  - {plugin_info['name']}: {plugin_info['description']}")

# 执行插件
sample_data = {
    'content': {
        '第一章': {
            '第一节': '这是第一节的代码示例:\n```python\nprint("Hello World")\n```',
            '第二节': '这是第二节的内容'
        },
        '第二章': '这是第二章的内容'
    }
}

processed_data = plugin_manager.execute_plugins("pre_process", sample_data, None)
print("插件处理完成")
```

## 参考资源

### Markdown文档
- [Markdown官方文档](https://daringfireball.net/projects/markdown/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [CommonMark规范](https://commonmark.org/)
- [Markdown指南](https://www.markdownguide.org/)

### 模板引擎
- [Jinja2文档](https://jinja.palletsprojects.com/)
- [Mustache文档](https://mustache.github.io/)
- [Handlebars.js](https://handlebarsjs.com/)
- [Django模板](https://docs.djangoproject.com/en/stable/topics/templates/)

### 文档生成工具
- [MkDocs](https://www.mkdocs.org/)
- [Sphinx](https://www.sphinx-doc.org/)
- [GitBook](https://www.gitbook.com/)
- [Docusaurus](https://docusaurus.io/)

### 静态站点生成
- [Jekyll](https://jekyllrb.com/)
- [Hugo](https://gohugo.io/)
- [Gatsby](https://www.gatsbyjs.com/)
- [Next.js](https://nextjs.org/)

### 代码高亮
- [Pygments](https://pygments.org/)
- [Prism.js](https://prismjs.com/)
- [highlight.js](https://highlightjs.org/)
- [CodeMirror](https://codemirror.net/)
