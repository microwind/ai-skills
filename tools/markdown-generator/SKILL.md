---
name: Markdown生成器
description: "当生成Markdown文档、转换格式、创建技术文档、编写README文件或自动化文档生成时，提供完整的Markdown处理和生成解决方案。"
license: MIT
---

# Markdown生成器技能

## 概述
Markdown是一种轻量级标记语言，广泛用于技术文档、README文件、博客文章和项目文档。Markdown生成器能够自动化创建结构化的Markdown文档，支持格式转换、模板生成和批量处理。

**核心原则**: 简洁明了、结构清晰、易于维护、自动化生成。

## 何时使用

**始终:**
- 创建项目README文件
- 生成技术文档
- 编写API文档
- 创建博客文章
- 生成报告和总结
- 转换文档格式
- 批量处理Markdown文件
- 创建模板和规范

**触发短语:**
- "生成Markdown文档"
- "创建README模板"
- "Markdown格式转换"
- "技术文档生成"
- "API文档编写"
- "博客文章模板"
- "文档自动化"
- "Markdown处理工具"

## Markdown语法和扩展

### 基础语法
- **标题**: 使用#号表示1-6级标题
- **段落**: 空行分隔段落
- **强调**: *斜体*、**粗体**、***粗斜体***
- **列表**: 无序列表(-)、有序列表(1.)
- **链接**: [文本](URL)
- **图片**: ![alt文本](URL)
- **代码**: `行内代码`、```代码块```

### 扩展语法
- **表格**: |列1|列2|
- **代码块语法高亮**: ```language
- **任务列表**: - [x] 已完成
- **脚注**: ^1
- **定义列表**: : 定义
- **数学公式**: $LaTeX$
- **图表**: Mermaid、PlantUML

## 常见文档类型

### README文档
```
结构:
- 项目标题和简介
- 安装说明
- 使用方法
- API文档
- 贡献指南
- 许可证信息

特点:
- 简洁明了
- 突出重点
- 易于理解
- 快速上手
```

### API文档
```
结构:
- API概述
- 认证方式
- 端点列表
- 请求/响应格式
- 错误处理
- 示例代码

特点:
- 结构清晰
- 示例丰富
- 错误说明
- 测试用例
```

### 技术博客
```
结构:
- 吸引人的标题
- 问题背景
- 解决方案
- 实现细节
- 总结展望

特点:
- 内容深入
- 代码示例
- 图文并茂
- 互动性强
```

## 代码实现示例

### Markdown生成器核心类
```python
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import yaml

class MarkdownElementType(Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    LINK = "link"
    IMAGE = "image"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"
    HORIZONTAL_RULE = "horizontal_rule"
    TASK_LIST = "task_list"

@dataclass
class MarkdownElement:
    """Markdown元素"""
    type: MarkdownElementType
    content: str
    level: Optional[int] = None  # 用于标题级别
    attributes: Optional[Dict[str, Any]] = None

class MarkdownGenerator:
    """Markdown生成器"""
    
    def __init__(self):
        self.elements: List[MarkdownElement] = []
        self.metadata: Dict[str, Any] = {}
        self.toc_enabled = True
        self.toc_max_level = 3
        
    def add_heading(self, text: str, level: int = 1) -> 'MarkdownGenerator':
        """添加标题"""
        if level < 1 or level > 6:
            raise ValueError("标题级别必须在1-6之间")
        
        element = MarkdownElement(
            type=MarkdownElementType.HEADING,
            content=text,
            level=level
        )
        self.elements.append(element)
        return self
    
    def add_paragraph(self, text: str) -> 'MarkdownGenerator':
        """添加段落"""
        element = MarkdownElement(
            type=MarkdownElementType.PARAGRAPH,
            content=text
        )
        self.elements.append(element)
        return self
    
    def add_list(self, items: List[str], ordered: bool = False) -> 'MarkdownGenerator':
        """添加列表"""
        prefix = "1. " if ordered else "- "
        content = "\n".join(f"{prefix}{item}" for item in items)
        
        element = MarkdownElement(
            type=MarkdownElementType.LIST,
            content=content,
            attributes={"ordered": ordered}
        )
        self.elements.append(element)
        return self
    
    def add_code_block(self, code: str, language: str = "", 
                      caption: str = "") -> 'MarkdownGenerator':
        """添加代码块"""
        content = f"```{language}\n{code}\n```"
        
        if caption:
            content += f"\n*{caption}*"
        
        element = MarkdownElement(
            type=MarkdownElementType.CODE_BLOCK,
            content=content,
            attributes={"language": language, "caption": caption}
        )
        self.elements.append(element)
        return self
    
    def add_inline_code(self, code: str) -> 'MarkdownGenerator':
        """添加行内代码"""
        element = MarkdownElement(
            type=MarkdownElementType.INLINE_CODE,
            content=f"`{code}`"
        )
        self.elements.append(element)
        return self
    
    def add_link(self, text: str, url: str, title: str = "") -> 'MarkdownGenerator':
        """添加链接"""
        if title:
            content = f"[{text}]({url} \"{title}\")"
        else:
            content = f"[{text}]({url})"
        
        element = MarkdownElement(
            type=MarkdownElementType.LINK,
            content=content,
            attributes={"url": url, "title": title}
        )
        self.elements.append(element)
        return self
    
    def add_image(self, alt_text: str, url: str, title: str = "") -> 'MarkdownGenerator':
        """添加图片"""
        if title:
            content = f"![{alt_text}]({url} \"{title}\")"
        else:
            content = f"![{alt_text}]({url})"
        
        element = MarkdownElement(
            type=MarkdownElementType.IMAGE,
            content=content,
            attributes={"url": url, "title": title}
        )
        self.elements.append(element)
        return self
    
    def add_table(self, headers: List[str], rows: List[List[str]]) -> 'MarkdownGenerator':
        """添加表格"""
        # 构建表格内容
        content = "| " + " | ".join(headers) + " |\n"
        content += "|" + "|".join(["---"] * len(headers)) + "|\n"
        
        for row in rows:
            content += "| " + " | ".join(row) + " |\n"
        
        element = MarkdownElement(
            type=MarkdownElementType.TABLE,
            content=content.strip(),
            attributes={"headers": headers, "rows": rows}
        )
        self.elements.append(element)
        return self
    
    def add_blockquote(self, text: str) -> 'MarkdownGenerator':
        """添加引用"""
        lines = text.split('\n')
        quoted_lines = [f"> {line}" for line in lines]
        content = '\n'.join(quoted_lines)
        
        element = MarkdownElement(
            type=MarkdownElementType.BLOCKQUOTE,
            content=content
        )
        self.elements.append(element)
        return self
    
    def add_horizontal_rule(self) -> 'MarkdownGenerator':
        """添加水平线"""
        element = MarkdownElement(
            type=MarkdownElementType.HORIZONTAL_RULE,
            content = "---"
        )
        self.elements.append(element)
        return self
    
    def add_task_list(self, tasks: List[Dict[str, Union[str, bool]]]) -> 'MarkdownGenerator':
        """添加任务列表"""
        items = []
        for task in tasks:
            text = task['text']
            checked = task.get('checked', False)
            checkbox = "- [x]" if checked else "- [ ]"
            items.append(f"{checkbox} {text}")
        
        content = "\n".join(items)
        
        element = MarkdownElement(
            type=MarkdownElementType.TASK_LIST,
            content=content,
            attributes={"tasks": tasks}
        )
        self.elements.append(element)
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'MarkdownGenerator':
        """添加元数据"""
        self.metadata[key] = value
        return self
    
    def generate_toc(self) -> str:
        """生成目录"""
        if not self.toc_enabled:
            return ""
        
        headings = [
            element for element in self.elements
            if element.type == MarkdownElementType.HEADING
            and element.level <= self.toc_max_level
        ]
        
        if not headings:
            return ""
        
        toc_lines = ["## 目录\n"]
        
        for heading in headings:
            indent = "  " * (heading.level - 1)
            # 生成锚点链接
            anchor = self._generate_anchor(heading.content)
            toc_lines.append(f"{indent}- [{heading.content}](#{anchor})")
        
        return "\n".join(toc_lines) + "\n"
    
    def _generate_anchor(self, text: str) -> str:
        """生成锚点链接"""
        # 移除特殊字符，转换为小写，用连字符替换空格
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def render(self) -> str:
        """渲染Markdown内容"""
        lines = []
        
        # 添加前置元数据
        if self.metadata:
            lines.append("---")
            lines.append("yaml")
            for key, value in self.metadata.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
                else:
                    lines.append(f"{key}: {value}")
            lines.append("---")
            lines.append("")
        
        # 添加目录
        if self.toc_enabled:
            toc = self.generate_toc()
            if toc:
                lines.append(toc)
                lines.append("")
        
        # 渲染所有元素
        for element in self.elements:
            lines.append(element.content)
            lines.append("")
        
        return '\n'.join(lines).strip()
    
    def save_to_file(self, file_path: str):
        """保存到文件"""
        content = self.render()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def clear(self) -> 'MarkdownGenerator':
        """清空内容"""
        self.elements.clear()
        self.metadata.clear()
        return self

class DocumentTemplate:
    """文档模板"""
    
    @staticmethod
    def create_readme_template(project_info: Dict[str, Any]) -> MarkdownGenerator:
        """创建README模板"""
        md = MarkdownGenerator()
        
        # 添加元数据
        md.add_metadata("title", project_info.get("name", "项目名称"))
        md.add_metadata("description", project_info.get("description", ""))
        md.add_metadata("author", project_info.get("author", ""))
        
        # 项目标题
        md.add_heading(project_info.get("name", "项目名称"), 1)
        
        # 项目描述
        description = project_info.get("description", "项目描述")
        badges = project_info.get("badges", [])
        
        if badges:
            badge_line = " ".join(badges)
            md.add_paragraph(badge_line)
        
        md.add_paragraph(description)
        
        # 目录
        md.add_heading("目录", 2)
        
        toc_items = [
            "安装说明",
            "使用方法", 
            "API文档",
            "贡献指南",
            "许可证"
        ]
        md.add_list(toc_items)
        
        # 安装说明
        md.add_heading("安装说明", 2)
        
        install_methods = project_info.get("install_methods", {})
        if install_methods:
            for method, instructions in install_methods.items():
                md.add_heading(method, 3)
                md.add_code_block(instructions, "bash")
        else:
            md.add_code_block("pip install project-name", "bash")
        
        # 使用方法
        md.add_heading("使用方法", 2)
        
        usage_examples = project_info.get("usage_examples", [])
        if usage_examples:
            for i, example in enumerate(usage_examples, 1):
                md.add_heading(f"示例 {i}", 3)
                md.add_code_block(example.get("code", ""), example.get("language", "python"))
                if example.get("description"):
                    md.add_paragraph(example["description"])
        else:
            md.add_code_block("""
# 基本使用示例
from project import main

result = main()
print(result)
""", "python")
        
        # API文档
        md.add_heading("API文档", 2)
        
        api_info = project_info.get("api_info", {})
        if api_info:
            for endpoint, details in api_info.items():
                md.add_heading(endpoint, 3)
                md.add_paragraph(details.get("description", ""))
                
                if details.get("parameters"):
                    md.add_heading("参数", 4)
                    param_headers = ["参数名", "类型", "必需", "描述"]
                    param_rows = []
                    for param in details["parameters"]:
                        param_rows.append([
                            param["name"],
                            param["type"],
                            "是" if param.get("required", False) else "否",
                            param["description"]
                        ])
                    md.add_table(param_headers, param_rows)
                
                if details.get("example"):
                    md.add_heading("示例", 4)
                    md.add_code_block(details["example"], details.get("language", "python"))
        
        # 贡献指南
        md.add_heading("贡献指南", 2)
        
        contribution_info = project_info.get("contribution_info", {})
        if contribution_info:
            md.add_paragraph(contribution_info.get("description", ""))
            
            if contribution_info.get("steps"):
                md.add_heading("贡献步骤", 3)
                md.add_list(contribution_info["steps"])
        else:
            md.add_paragraph("欢迎贡献代码！请遵循以下步骤：")
            md.add_list([
                "Fork 本仓库",
                "创建特性分支 (git checkout -b feature/AmazingFeature)",
                "提交更改 (git commit -m 'Add some AmazingFeature')",
                "推送到分支 (git push origin feature/AmazingFeature)",
                "创建 Pull Request"
            ])
        
        # 许可证
        md.add_heading("许可证", 2)
        license_info = project_info.get("license", "MIT")
        md.add_paragraph(f"本项目采用 {license_info} 许可证。")
        
        return md
    
    @staticmethod
    def create_api_documentation(api_info: Dict[str, Any]) -> MarkdownGenerator:
        """创建API文档"""
        md = MarkdownGenerator()
        
        # 添加元数据
        md.add_metadata("title", "API文档")
        md.add_metadata("generated", datetime.now().isoformat())
        
        # 文档标题
        md.add_heading("API文档", 1)
        
        # API概述
        md.add_heading("概述", 2)
        md.add_paragraph(api_info.get("description", ""))
        
        # 基础信息
        base_info = api_info.get("base_info", {})
        if base_info:
            md.add_heading("基础信息", 2)
            
            info_items = []
            if base_info.get("base_url"):
                info_items.append(f"**基础URL**: {base_info['base_url']}")
            if base_info.get("version"):
                info_items.append(f"**API版本**: {base_info['version']}")
            if base_info.get("protocol"):
                info_items.append(f"**协议**: {base_info['protocol']}")
            
            md.add_paragraph("\n".join(info_items))
        
        # 认证
        auth_info = api_info.get("authentication", {})
        if auth_info:
            md.add_heading("认证", 2)
            md.add_paragraph(auth_info.get("description", ""))
            
            if auth_info.get("type"):
                md.add_heading(f"认证类型: {auth_info['type']}", 3)
                md.add_code_block(auth_info.get("example", ""), "http")
        
        # 端点列表
        endpoints = api_info.get("endpoints", [])
        if endpoints:
            md.add_heading("端点列表", 2)
            
            # 端点概览表格
            headers = ["方法", "端点", "描述"]
            rows = []
            for endpoint in endpoints:
                rows.append([
                    endpoint.get("method", "GET"),
                    endpoint.get("path", "/"),
                    endpoint.get("description", "")
                ])
            md.add_table(headers, rows)
            
            # 详细端点信息
            for endpoint in endpoints:
                md.add_heading(f"{endpoint.get('method', 'GET')} {endpoint.get('path', '/')}", 3)
                
                if endpoint.get("description"):
                    md.add_paragraph(endpoint["description"])
                
                # 请求参数
                if endpoint.get("parameters"):
                    md.add_heading("请求参数", 4)
                    
                    param_headers = ["参数名", "位置", "类型", "必需", "描述"]
                    param_rows = []
                    for param in endpoint["parameters"]:
                        param_rows.append([
                            param["name"],
                            param.get("location", "query"),
                            param["type"],
                            "是" if param.get("required", False) else "否",
                            param["description"]
                        ])
                    md.add_table(param_headers, param_rows)
                
                # 请求示例
                if endpoint.get("request_example"):
                    md.add_heading("请求示例", 4)
                    md.add_code_block(
                        endpoint["request_example"],
                        endpoint.get("language", "http")
                    )
                
                # 响应格式
                if endpoint.get("response"):
                    md.add_heading("响应格式", 4)
                    response = endpoint["response"]
                    
                    if response.get("description"):
                        md.add_paragraph(response["description"])
                    
                    if response.get("example"):
                        md.add_code_block(
                            response["example"],
                            response.get("language", "json")
                    )
                
                # 错误处理
                if endpoint.get("errors"):
                    md.add_heading("错误响应", 4)
                    
                    error_headers = ["状态码", "错误类型", "描述"]
                    error_rows = []
                    for error in endpoint["errors"]:
                        error_rows.append([
                            str(error["status_code"]),
                            error["error_type"],
                            error["description"]
                        ])
                    md.add_table(error_headers, error_rows)
        
        return md
    
    @staticmethod
    def create_blog_post(post_info: Dict[str, Any]) -> MarkdownGenerator:
        """创建博客文章"""
        md = MarkdownGenerator()
        
        # 添加元数据
        md.add_metadata("title", post_info.get("title", ""))
        md.add_metadata("date", post_info.get("date", datetime.now().strftime("%Y-%m-%d")))
        md.add_metadata("author", post_info.get("author", ""))
        md.add_metadata("tags", post_info.get("tags", []))
        md.add_metadata("category", post_info.get("category", ""))
        
        # 文章标题
        md.add_heading(post_info.get("title", ""), 1)
        
        # 文章信息
        meta_info = []
        if post_info.get("author"):
            meta_info.append(f"**作者**: {post_info['author']}")
        if post_info.get("date"):
            meta_info.append(f"**发布日期**: {post_info['date']}")
        if post_info.get("category"):
            meta_info.append(f"**分类**: {post_info['category']}")
        if post_info.get("tags"):
            tags = ", ".join(post_info["tags"])
            meta_info.append(f"**标签**: {tags}")
        
        if meta_info:
            md.add_paragraph(" | ".join(meta_info))
        
        # 摘要
        if post_info.get("summary"):
            md.add_heading("摘要", 2)
            md.add_paragraph(post_info["summary"])
            md.add_horizontal_rule()
        
        # 正文内容
        content_sections = post_info.get("content", [])
        for section in content_sections:
            if section.get("heading"):
                md.add_heading(section["heading"], section.get("level", 2))
            
            if section.get("content"):
                md.add_paragraph(section["content"])
            
            if section.get("code"):
                md.add_code_block(
                    section["code"],
                    section.get("language", "python")
                )
            
            if section.get("image"):
                img = section["image"]
                md.add_image(
                    img.get("alt", ""),
                    img.get("url", ""),
                    img.get("title", "")
                )
            
            if section.get("list"):
                md.add_list(section["list"], section.get("ordered", False))
        
        # 结论
        if post_info.get("conclusion"):
            md.add_heading("结论", 2)
            md.add_paragraph(post_info["conclusion"])
        
        return md

class MarkdownConverter:
    """Markdown转换器"""
    
    @staticmethod
    def to_html(markdown_content: str) -> str:
        """转换为HTML"""
        try:
            import markdown
            extensions = ['codehilite', 'tables', 'toc', 'fenced_code']
            return markdown.markdown(markdown_content, extensions=extensions)
        except ImportError:
            return "# 需要安装 markdown 库\n\npip install markdown"
    
    @staticmethod
    def to_pdf(markdown_content: str, output_path: str):
        """转换为PDF"""
        try:
            import weasyprint
            html_content = MarkdownConverter.to_html(markdown_content)
            
            # 添加基本CSS样式
            css_style = """
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1, h2, h3 { color: #333; }
            code { background-color: #f4f4f4; padding: 2px 4px; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 4px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            """
            
            html_doc = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>{css_style}</style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            weasyprint.HTML(string=html_doc).write_pdf(output_path)
            return True
        except ImportError:
            print("需要安装 weasyprint 库")
            return False

# 使用示例
def main():
    """示例使用"""
    print("📝 Markdown生成器启动")
    print("=" * 50)
    
    # 创建README文档
    project_info = {
        "name": "Awesome Project",
        "description": "一个很棒的项目示例",
        "author": "Developer Name",
        "badges": [
            "![Build Status](https://img.shields.io/badge/build-passing-brightgreen)",
            "![License](https://img.shields.io/badge/license-MIT-blue)"
        ],
        "install_methods": {
            "使用pip": "pip install awesome-project",
            "使用conda": "conda install -c conda-forge awesome-project"
        },
        "usage_examples": [
            {
                "code": "from awesome_project import main\nresult = main()",
                "language": "python",
                "description": "基本使用示例"
            }
        ],
        "license": "MIT"
    }
    
    readme_md = DocumentTemplate.create_readme_template(project_info)
    readme_md.save_to_file("README.md")
    print("✅ README.md 生成完成!")
    
    # 创建API文档
    api_info = {
        "description": "示例API接口文档",
        "base_info": {
            "base_url": "https://api.example.com/v1",
            "version": "1.0.0",
            "protocol": "HTTPS"
        },
        "authentication": {
            "type": "Bearer Token",
            "description": "使用Bearer Token进行身份验证",
            "example": "Authorization: Bearer your-token-here"
        },
        "endpoints": [
            {
                "method": "GET",
                "path": "/users",
                "description": "获取用户列表",
                "parameters": [
                    {
                        "name": "page",
                        "location": "query",
                        "type": "integer",
                        "required": False,
                        "description": "页码，默认为1"
                    }
                ],
                "response": {
                    "description": "返回用户列表",
                    "example": '{\n  "users": [...],\n  "total": 100\n}'
                }
            }
        ]
    }
    
    api_md = DocumentTemplate.create_api_documentation(api_info)
    api_md.save_to_file("API.md")
    print("✅ API.md 生成完成!")
    
    # 创建博客文章
    blog_info = {
        "title": "如何使用Markdown生成器",
        "author": "技术博主",
        "date": "2024-01-15",
        "category": "技术教程",
        "tags": ["Markdown", "文档", "Python"],
        "summary": "介绍如何使用Python生成高质量的Markdown文档",
        "content": [
            {
                "heading": "引言",
                "level": 2,
                "content": "Markdown是一种轻量级标记语言..."
            },
            {
                "heading": "基本用法",
                "level": 2,
                "content": "使用MarkdownGenerator类可以轻松创建文档",
                "code": "md = MarkdownGenerator()\nmd.add_heading('标题', 1)",
                "language": "python"
            }
        ],
        "conclusion": "通过这个工具，我们可以高效地生成各种文档"
    }
    
    blog_md = DocumentTemplate.create_blog_post(blog_info)
    blog_md.save_to_file("blog-post.md")
    print("✅ blog-post.md 生成完成!")
    
    # 转换为HTML
    html_content = MarkdownConverter.to_html(readme_md.render())
    with open("README.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ README.html 转换完成!")
    
    print("\n✅ Markdown生成器演示完成!")

if __name__ == "__main__":
    main()
```

### Markdown分析器
```python
class MarkdownAnalyzer:
    """Markdown分析器"""
    
    def __init__(self):
        self.element_patterns = {
            'heading': re.compile(r'^(#{1,6})\s+(.+)$'),
            'list': re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.+)$'),
            'code_block': re.compile(r'^```(\w*)\n(.*?)\n```$', re.MULTILINE | re.DOTALL),
            'image': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
            'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'table': re.compile(r'^\|(.+)\|\n\|[-\s\|]+\|\n((?:\|.+\|\n?)*)', re.MULTILINE)
        }
    
    def analyze(self, markdown_content: str) -> Dict[str, Any]:
        """分析Markdown内容"""
        lines = markdown_content.split('\n')
        
        analysis = {
            'total_lines': len(lines),
            'total_characters': len(markdown_content),
            'elements': {
                'headings': [],
                'lists': [],
                'code_blocks': [],
                'images': [],
                'links': [],
                'tables': []
            },
            'statistics': {},
            'structure': []
        }
        
        # 分析每一行
        for i, line in enumerate(lines, 1):
            element_info = self._analyze_line(line, i)
            if element_info:
                analysis['structure'].append(element_info)
                element_type = element_info['type']
                if element_type in analysis['elements']:
                    analysis['elements'][element_type].append(element_info)
        
        # 计算统计信息
        analysis['statistics'] = self._calculate_statistics(analysis['elements'])
        
        return analysis
    
    def _analyze_line(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """分析单行内容"""
        line = line.rstrip()
        
        # 检查标题
        heading_match = self.element_patterns['heading'].match(line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            return {
                'type': 'heading',
                'line': line_number,
                'level': level,
                'text': text,
                'anchor': self._generate_anchor(text)
            }
        
        # 检查列表
        list_match = self.element_patterns['list'].match(line)
        if list_match:
            indent = len(list_match.group(1))
            marker = list_match.group(2)
            text = list_match.group(3)
            ordered = marker.endswith('.')
            return {
                'type': 'list',
                'line': line_number,
                'indent': indent,
                'ordered': ordered,
                'text': text
            }
        
        # 检查表格
        if '|' in line and line.strip():
            return {
                'type': 'table_row',
                'line': line_number,
                'content': line
            }
        
        return None
    
    def _calculate_statistics(self, elements: Dict[str, List]) -> Dict[str, Any]:
        """计算统计信息"""
        stats = {}
        
        # 标题统计
        headings = elements['headings']
        stats['headings'] = {
            'total': len(headings),
            'by_level': {}
        }
        
        for heading in headings:
            level = heading['level']
            stats['headings']['by_level'][level] = stats['headings']['by_level'].get(level, 0) + 1
        
        # 列表统计
        lists = elements['lists']
        stats['lists'] = {
            'total': len(lists),
            'ordered': sum(1 for lst in lists if lst['ordered']),
            'unordered': sum(1 for lst in lists if not lst['ordered'])
        }
        
        # 其他元素统计
        for element_type in ['code_blocks', 'images', 'links', 'tables']:
            stats[element_type] = len(elements[element_type])
        
        return stats
    
    def _generate_anchor(self, text: str) -> str:
        """生成锚点"""
        import re
        anchor = re.sub(r'[^\w\s-]', '', text.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def generate_toc(self, markdown_content: str, max_level: int = 3) -> str:
        """生成目录"""
        analysis = self.analyze(markdown_content)
        headings = analysis['elements']['headings']
        
        toc_lines = ["## 目录\n"]
        
        for heading in headings:
            if heading['level'] <= max_level:
                indent = "  " * (heading['level'] - 1)
                toc_lines.append(f"{indent}- [{heading['text']}](#{heading['anchor']})")
        
        return "\n".join(toc_lines)

# 使用示例
def main():
    analyzer = MarkdownAnalyzer()
    print("Markdown分析器已准备就绪!")

if __name__ == "__main__":
    main()
```

## Markdown最佳实践

### 文档结构
1. **层次清晰**: 合理使用标题层级
2. **逻辑有序**: 内容按逻辑顺序组织
3. **导航友好**: 提供目录和锚点
4. **易于扫描**: 使用列表和表格

### 内容质量
1. **简洁明了**: 避免冗长描述
2. **示例丰富**: 提供充分的代码示例
3. **图文并茂**: 适当使用图片和图表
4. **及时更新**: 保持文档与代码同步

### 格式规范
1. **一致性**: 保持格式风格统一
2. **可读性**: 合理使用空行和缩进
3. **链接有效**: 确保所有链接可访问
4. **代码规范**: 使用语法高亮

## Markdown工具推荐

### 编辑器
- **Typora**: 所见即所得编辑器
- **Mark Text**: 开源Markdown编辑器
- **Obsidian**: 知识管理工具
- **Notion**: 集成文档平台

### 转换工具
- **Pandoc**: 通用文档转换器
- **Marp**: Markdown到PPT
- **Hugo**: 静态网站生成器
- **Jekyll**: GitHub Pages支持

### 扩展语法
- **Mermaid**: 图表和流程图
- **PlantUML**: UML图表
- **KaTeX**: 数学公式
- **GitHub Flavored Markdown**: 扩展语法

## 相关技能

- **technical-writing** - 技术写作
- **documentation** - 文档管理
- **content-management** - 内容管理
- **web-development** - Web开发
- **api-documentation** - API文档
- **blog-writing** - 博客写作
