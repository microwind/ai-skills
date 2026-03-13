---
name: 文档生成器
description: "当生成文档时，分析代码结构，提取API信息，生成完整文档。验证文档质量，设计文档模板，和最佳实践。"
license: MIT
---

# 文档生成器技能

## 概述
文档生成是提升代码可维护性和团队协作效率的重要工具。不当的文档会导致理解困难、使用错误和维护成本高。需要系统化的文档生成策略。

**核心原则**: 好的文档生成应该自动化、准确、完整、易维护。坏的文档生成会导致信息过时、内容错误、维护困难。

## 何时使用

**始终:**
- 开发新项目时
- 发布API接口时
- 团队协作开发时
- 开源项目维护时
- 代码交接时
- 用户培训时

**触发短语:**
- "生成文档"
- "API文档"
- "写README"
- "代码注释"
- "使用指南"
- "开发文档"

## 文档生成功能

### 自动文档提取
- 代码注释解析
- API接口分析
- 类型定义提取
- 函数签名识别
- 模块结构分析

### 文档模板管理
- README模板
- API文档模板
- 用户指南模板
- 开发者文档模板
- 自定义模板

### 多格式输出
- Markdown文档
- HTML页面
- PDF文档
- 静态网站
- 交互式文档

### 文档质量验证
- 内容完整性检查
- 格式规范验证
- 链接有效性检测
- 示例代码验证
- 版本一致性检查

## 常见文档生成问题

### 文档内容过时
```
问题:
文档与实际代码不同步，导致误导用户

错误示例:
- API接口变更未更新文档
- 参数说明不准确
- 示例代码无法运行
- 版本信息错误

解决方案:
1. 自动化文档生成
2. 版本控制集成
3. 定期文档审查
4. 示例代码测试
```

### 文档结构混乱
```
问题:
文档组织不合理，难以查找信息

错误示例:
- 缺少目录结构
- 章节顺序混乱
- 重要信息不突出
- 重复内容过多

解决方案:
1. 标准化文档模板
2. 清晰的目录结构
3. 重要信息优先
4. 避免重复内容
```

### 示例代码错误
```
问题:
文档中的示例代码有错误，无法正常运行

错误示例:
- 语法错误
- 依赖缺失
- 环境配置问题
- 数据不匹配

解决方案:
1. 代码示例测试
2. 环境配置说明
3. 完整的依赖列表
4. 实际数据验证
```

### 文档可读性差
```
问题:
文档表达不清晰，用户难以理解

错误示例:
- 技术术语过多
- 缺少图表说明
- 语言表达复杂
- 缺少实际案例

解决方案:
1. 简化技术表达
2. 增加图表说明
3. 提供实际案例
4. 多层次内容组织
```

## 代码实现示例

### 文档生成器
```python
import os
import re
import json
import ast
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import inspect
from pathlib import Path

class DocumentType(Enum):
    """文档类型"""
    README = "readme"
    API = "api"
    USER_GUIDE = "user_guide"
    DEVELOPER_GUIDE = "developer_guide"
    CHANGELOG = "changelog"

class OutputFormat(Enum):
    """输出格式"""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"

@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    returns: Dict[str, Any]
    examples: List[str]
    source_file: str
    line_number: int

@dataclass
class ClassInfo:
    """类信息"""
    name: str
    description: str
    methods: List[FunctionInfo]
    attributes: List[Dict[str, Any]]
    inheritance: List[str]
    source_file: str
    line_number: int

@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    description: str
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    constants: Dict[str, Any]
    imports: List[str]
    source_file: str

class CodeAnalyzer:
    def __init__(self):
        self.function_pattern = re.compile(r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*([^:]+):')
        self.class_pattern = re.compile(r'class\s+(\w+)(?:\(([^)]+)\))?:')
        self.docstring_pattern = re.compile(r'"""([^"]*)"""', re.MULTILINE | re.DOTALL)
    
    def analyze_file(self, file_path: str) -> ModuleInfo:
        """分析Python文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"无法解析文件 {file_path}: {e}")
        
        # 提取模块信息
        module_name = Path(file_path).stem
        module_docstring = ast.get_docstring(tree) or ""
        
        functions = []
        classes = []
        constants = {}
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._analyze_function(node, file_path)
                functions.append(func_info)
            elif isinstance(node, ast.ClassDef):
                class_info = self._analyze_class(node, file_path)
                classes.append(class_info)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        constants[target.id] = self._get_constant_value(node.value)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return ModuleInfo(
            name=module_name,
            description=module_docstring,
            functions=functions,
            classes=classes,
            constants=constants,
            imports=imports,
            source_file=file_path
        )
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> FunctionInfo:
        """分析函数"""
        # 提取文档字符串
        docstring = ast.get_docstring(node) or ""
        
        # 分析参数
        parameters = []
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type': self._get_type_annotation(arg.annotation),
                'default': None,
                'description': ''
            }
            
            # 提取参数描述从文档字符串
            param_desc = self._extract_param_description(docstring, arg.arg)
            if param_desc:
                param_info['description'] = param_desc
            
            parameters.append(param_info)
        
        # 分析返回值
        return_info = {
            'type': self._get_type_annotation(node.returns),
            'description': self._extract_return_description(docstring)
        }
        
        # 提取示例
        examples = self._extract_examples(docstring)
        
        return FunctionInfo(
            name=node.name,
            description=docstring,
            parameters=parameters,
            returns=return_info,
            examples=examples,
            source_file=file_path,
            line_number=node.lineno
        )
    
    def _analyze_class(self, node: ast.ClassDef, file_path: str) -> ClassInfo:
        """分析类"""
        # 提取文档字符串
        docstring = ast.get_docstring(node) or ""
        
        # 分析继承
        inheritance = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                inheritance.append(base.id)
        
        # 分析方法
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item, file_path)
                methods.append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr_info = {
                            'name': target.id,
                            'type': self._get_type_annotation(item.type_annotation),
                            'description': ''
                        }
                        attributes.append(attr_info)
        
        return ClassInfo(
            name=node.name,
            description=docstring,
            methods=methods,
            attributes=attributes,
            inheritance=inheritance,
            source_file=file_path,
            line_number=node.lineno
        )
    
    def _get_type_annotation(self, annotation) -> str:
        """获取类型注解"""
        if annotation is None:
            return "Any"
        elif isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return f"{annotation.value.id}.{annotation.attr}"
        else:
            return str(annotation)
    
    def _get_constant_value(self, node) -> Any:
        """获取常量值"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        else:
            return "Unknown"
    
    def _extract_param_description(self, docstring: str, param_name: str) -> str:
        """从文档字符串提取参数描述"""
        # 查找参数描述模式
        pattern = rf':param {param_name}:\s*([^\n]+)'
        match = re.search(pattern, docstring)
        return match.group(1) if match else ""
    
    def _extract_return_description(self, docstring: str) -> str:
        """从文档字符串提取返回值描述"""
        pattern = r':return:\s*([^\n]+)'
        match = re.search(pattern, docstring)
        return match.group(1) if match else ""
    
    def _extract_examples(self, docstring: str) -> List[str]:
        """从文档字符串提取示例"""
        examples = []
        
        # 查找示例代码块
        example_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(example_pattern, docstring, re.MULTILINE | re.DOTALL)
        examples.extend(matches)
        
        return examples

class DocumentGenerator:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.templates = self._load_templates()
    
    def generate_documentation(self, source_dir: str, output_dir: str, 
                             doc_type: DocumentType, 
                             output_format: OutputFormat = OutputFormat.MARKDOWN) -> bool:
        """生成文档"""
        try:
            # 分析源代码
            modules = self._analyze_source_directory(source_dir)
            
            # 生成文档内容
            if doc_type == DocumentType.API:
                content = self._generate_api_documentation(modules)
            elif doc_type == DocumentType.README:
                content = self._generate_readme(modules)
            elif doc_type == DocumentType.USER_GUIDE:
                content = self._generate_user_guide(modules)
            elif doc_type == DocumentType.DEVELOPER_GUIDE:
                content = self._generate_developer_guide(modules)
            else:
                content = self._generate_changelog(modules)
            
            # 格式化输出
            if output_format == OutputFormat.MARKDOWN:
                formatted_content = content
            elif output_format == OutputFormat.HTML:
                formatted_content = self._convert_to_html(content)
            elif output_format == OutputFormat.JSON:
                formatted_content = self._convert_to_json(content)
            else:
                formatted_content = content
            
            # 写入文件
            output_file = os.path.join(output_dir, f"{doc_type.value}.{output_format.value}")
            os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            print(f"文档生成成功: {output_file}")
            return True
            
        except Exception as e:
            print(f"文档生成失败: {e}")
            return False
    
    def _analyze_source_directory(self, source_dir: str) -> List[ModuleInfo]:
        """分析源代码目录"""
        modules = []
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    try:
                        module_info = self.analyzer.analyze_file(file_path)
                        modules.append(module_info)
                    except Exception as e:
                        print(f"分析文件失败 {file_path}: {e}")
        
        return modules
    
    def _generate_api_documentation(self, modules: List[ModuleInfo]) -> str:
        """生成API文档"""
        content = ["# API 文档", ""]
        
        # 生成目录
        content.append("## 目录")
        content.append("")
        for module in modules:
            content.append(f"- [{module.name}](#{module.name.lower()})")
        content.append("")
        
        # 生成模块文档
        for module in modules:
            content.append(f"## {module.name}")
            content.append("")
            
            if module.description:
                content.append(module.description)
                content.append("")
            
            # 添加函数文档
            if module.functions:
                content.append("### 函数")
                content.append("")
                for func in module.functions:
                    content.extend(self._generate_function_documentation(func))
            
            # 添加类文档
            if module.classes:
                content.append("### 类")
                content.append("")
                for cls in module.classes:
                    content.extend(self._generate_class_documentation(cls))
        
        return "\n".join(content)
    
    def _generate_function_documentation(self, func: FunctionInfo) -> List[str]:
        """生成函数文档"""
        content = []
        
        # 函数签名
        params = ", ".join([f"{p['name']}: {p['type']}" for p in func.parameters])
        content.append(f"#### {func.name}({params}) -> {func.returns['type']}")
        content.append("")
        
        # 描述
        if func.description:
            content.append(func.description)
            content.append("")
        
        # 参数
        if func.parameters:
            content.append("**参数:**")
            content.append("")
            for param in func.parameters:
                param_desc = f"- `{param['name']}` ({param['type']}): {param['description'] or '无描述'}"
                content.append(param_desc)
            content.append("")
        
        # 返回值
        if func.returns and func.returns['description']:
            content.append(f"**返回值:** {func.returns['description']}")
            content.append("")
        
        # 示例
        if func.examples:
            content.append("**示例:**")
            content.append("")
            for example in func.examples:
                content.append("```python")
                content.append(example)
                content.append("```")
                content.append("")
        
        return content
    
    def _generate_class_documentation(self, cls: ClassInfo) -> List[str]:
        """生成类文档"""
        content = []
        
        # 类名和继承
        inheritance_str = f"({', '.join(cls.inheritance)})" if cls.inheritance else ""
        content.append(f"#### {cls.name}{inheritance_str}")
        content.append("")
        
        # 描述
        if cls.description:
            content.append(cls.description)
            content.append("")
        
        # 属性
        if cls.attributes:
            content.append("**属性:**")
            content.append("")
            for attr in cls.attributes:
                attr_desc = f"- `{attr['name']}` ({attr['type']}): {attr['description'] or '无描述'}"
                content.append(attr_desc)
            content.append("")
        
        # 方法
        if cls.methods:
            content.append("**方法:**")
            content.append("")
            for method in cls.methods:
                method_params = ", ".join([f"{p['name']}: {p['type']}" for p in method.parameters])
                content.append(f"- `{method.name}({method_params}) -> {method.returns['type']}`: {method.description[:50]}...")
            content.append("")
        
        return content
    
    def _generate_readme(self, modules: List[ModuleInfo]) -> str:
        """生成README文档"""
        content = [
            "# 项目名称",
            "",
            "项目描述...",
            "",
            "## 功能特性",
            "",
            "- 功能1",
            "- 功能2",
            "- 功能3",
            "",
            "## 安装说明",
            "",
            "```bash",
            "pip install package-name",
            "```",
            "",
            "## 快速开始",
            "",
            "```python",
            "from package import Module",
            "",
            "# 使用示例",
            "module = Module()",
            "result = module.do_something()",
            "print(result)",
            "```",
            "",
            "## API 文档",
            "",
            "详细的API文档请参考 [API文档](./api.md)",
            "",
            "## 贡献指南",
            "",
            "欢迎贡献代码！请参考 [贡献指南](./CONTRIBUTING.md)",
            "",
            "## 许可证",
            "",
            "MIT License"
        ]
        
        return "\n".join(content)
    
    def _generate_user_guide(self, modules: List[ModuleInfo]) -> str:
        """生成用户指南"""
        content = [
            "# 用户指南",
            "",
            "## 简介",
            "",
            "本项目提供了...",
            "",
            "## 安装和配置",
            "",
            "### 系统要求",
            "- Python 3.8+",
            "- 依赖包列表",
            "",
            "### 安装步骤",
            "1. 下载源代码",
            "2. 安装依赖",
            "3. 配置环境",
            "",
            "## 基本使用",
            "",
            "### 第一个例子",
            "```python",
            "# 基本使用示例",
            "```",
            "",
            "### 常见用例",
            "",
            "## 高级功能",
            "",
            "## 故障排除",
            "",
            "## 常见问题",
            ""
        ]
        
        return "\n".join(content)
    
    def _generate_developer_guide(self, modules: List[ModuleInfo]) -> str:
        """生成开发者指南"""
        content = [
            "# 开发者指南",
            "",
            "## 项目结构",
            "",
            "```,
            "project/",
            "├── src/",
            "│   ├── module1/",
            "│   └── module2/",
            "├── tests/",
            "├── docs/",
            "└── README.md",
            "```",
            "",
            "## 开发环境设置",
            "",
            "### 本地开发",
            "1. 克隆仓库",
            "2. 安装开发依赖",
            "3. 运行测试",
            "",
            "## 代码规范",
            "",
            "## 测试指南",
            "",
            "## 发布流程",
            ""
        ]
        
        return "\n".join(content)
    
    def _generate_changelog(self, modules: List[ModuleInfo]) -> str:
        """生成变更日志"""
        content = [
            "# 变更日志",
            "",
            "## [版本号] - 日期",
            "",
            "### 新增",
            "- 新功能1",
            "- 新功能2",
            "",
            "### 修复",
            "- 修复问题1",
            "- 修复问题2",
            "",
            "### 改进",
            "- 改进1",
            "- 改进2",
            "",
            "### 移除",
            "- 移除功能1",
            "",
            "## [上一版本] - 日期",
            "",
            "### 新增",
            "- ..."
        ]
        
        return "\n".join(content)
    
    def _convert_to_html(self, markdown_content: str) -> str:
        """转换为HTML"""
        # 简化的Markdown到HTML转换
        html_content = markdown_content
        
        # 转换标题
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        
        # 转换代码块
        html_content = re.sub(r'```python\n(.*?)\n```', r'<pre><code>\1</code></pre>', 
                            html_content, flags=re.MULTILINE | re.DOTALL)
        
        # 转换粗体
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        
        # 转换斜体
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        
        # 转换链接
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>API 文档</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #666; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    
    def _convert_to_json(self, markdown_content: str) -> str:
        """转换为JSON"""
        # 简化的JSON格式
        return json.dumps({
            "content": markdown_content,
            "format": "markdown",
            "generated_at": "2024-01-01T00:00:00Z"
        }, ensure_ascii=False, indent=2)
    
    def _load_templates(self) -> Dict[str, str]:
        """加载文档模板"""
        return {
            "readme": "# {project_name}\n\n{description}",
            "api": "# API 文档\n\n{content}",
            "user_guide": "# 用户指南\n\n{content}",
            "developer_guide": "# 开发者指南\n\n{content}"
        }

# 使用示例
def main():
    print("=== 文档生成器 ===")
    
    # 创建文档生成器
    generator = DocumentGenerator()
    
    # 示例：生成API文档
    print("生成API文档...")
    success = generator.generate_documentation(
        source_dir="./src",
        output_dir="./docs",
        doc_type=DocumentType.API,
        output_format=OutputFormat.MARKDOWN
    )
    
    if success:
        print("API文档生成成功")
    else:
        print("API文档生成失败")
    
    # 示例：生成README
    print("\n生成README...")
    success = generator.generate_documentation(
        source_dir="./src",
        output_dir="./docs",
        doc_type=DocumentType.README,
        output_format=OutputFormat.MARKDOWN
    )
    
    if success:
        print("README生成成功")
    else:
        print("README生成失败")
    
    # 示例：生成HTML文档
    print("\n生成HTML文档...")
    success = generator.generate_documentation(
        source_dir="./src",
        output_dir="./docs",
        doc_type=DocumentType.API,
        output_format=OutputFormat.HTML
    )
    
    if success:
        print("HTML文档生成成功")
    else:
        print("HTML文档生成失败")

if __name__ == '__main__':
    main()
```

### 文档质量检查器
```python
import re
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os

class IssueType(Enum):
    """问题类型"""
    MISSING_CONTENT = "missing_content"
    BROKEN_LINK = "broken_link"
    FORMAT_ERROR = "format_error"
    OUTDATED_INFO = "outdated_info"
    EXAMPLE_ERROR = "example_error"

class IssueSeverity(Enum):
    """问题严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DocumentationIssue:
    """文档问题"""
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    location: str
    suggestion: str

class DocumentationValidator:
    def __init__(self):
        self.validation_rules = {
            'readme_structure': self._validate_readme_structure,
            'api_completeness': self._validate_api_completeness,
            'link_validity': self._validate_links,
            'code_examples': self._validate_code_examples,
            'format_consistency': self._validate_format_consistency,
        }
    
    def validate_documentation(self, doc_path: str) -> List[DocumentationIssue]:
        """验证文档质量"""
        issues = []
        
        if not os.path.exists(doc_path):
            return [DocumentationIssue(
                IssueType.MISSING_CONTENT,
                IssueSeverity.CRITICAL,
                f"文档文件不存在: {doc_path}",
                doc_path,
                "创建文档文件"
            )]
        
        # 读取文档内容
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 执行各种验证
        for rule_name, rule_func in self.validation_rules.items():
            rule_issues = rule_func(content, doc_path)
            issues.extend(rule_issues)
        
        return issues
    
    def _validate_readme_structure(self, content: str, doc_path: str) -> List[DocumentationIssue]:
        """验证README结构"""
        issues = []
        
        # 检查必需的章节
        required_sections = [
            "## 安装说明",
            "## 快速开始", 
            "## 使用方法",
            "## 许可证"
        ]
        
        for section in required_sections:
            if section not in content:
                issues.append(DocumentationIssue(
                    IssueType.MISSING_CONTENT,
                    IssueSeverity.HIGH,
                    f"缺少必需章节: {section}",
                    doc_path,
                    f"添加 {section} 章节"
                ))
        
        # 检查项目描述
        if not content.strip().startswith("# "):
            issues.append(DocumentationIssue(
                IssueType.FORMAT_ERROR,
                IssueSeverity.MEDIUM,
                "缺少项目标题",
                doc_path,
                "添加项目标题"
            ))
        
        # 检查安装说明
        if "pip install" not in content and "npm install" not in content:
            issues.append(DocumentationIssue(
                IssueType.MISSING_CONTENT,
                IssueSeverity.HIGH,
                "缺少安装说明",
                doc_path,
                "添加详细的安装步骤"
            ))
        
        return issues
    
    def _validate_api_completeness(self, content: str, doc_path: str) -> List[DocumentationIssue]:
        """验证API文档完整性"""
        issues = []
        
        # 检查API文档结构
        if "## API" in content or "## 接口" in content:
            # 检查是否有端点列表
            if not re.search(r'### (GET|POST|PUT|DELETE|PATCH)', content, re.IGNORECASE):
                issues.append(DocumentationIssue(
                    IssueType.MISSING_CONTENT,
                    IssueSeverity.HIGH,
                    "缺少API端点定义",
                    doc_path,
                    "添加API端点列表"
                ))
            
            # 检查是否有参数说明
            if "**参数**" not in content and "**Parameters**" not in content:
                issues.append(DocumentationIssue(
                    IssueType.MISSING_CONTENT,
                    IssueSeverity.MEDIUM,
                    "缺少API参数说明",
                    doc_path,
                    "添加参数详细说明"
                ))
            
            # 检查是否有响应示例
            if "```json" not in content and "```" not in content:
                issues.append(DocumentationIssue(
                    IssueType.MISSING_CONTENT,
                    IssueSeverity.MEDIUM,
                    "缺少响应示例",
                    doc_path,
                    "添加响应示例"
                ))
        
        return issues
    
    def _validate_links(self, content: str, doc_path: str) -> List[DocumentationIssue]:
        """验证链接有效性"""
        issues = []
        
        # 提取所有链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        
        for link_text, url in matches:
            # 检查相对链接
            if url.startswith('./') or url.startswith('../'):
                full_path = os.path.join(os.path.dirname(doc_path), url)
                if not os.path.exists(full_path):
                    issues.append(DocumentationIssue(
                        IssueType.BROKEN_LINK,
                        IssueSeverity.HIGH,
                        f"无效的相对链接: {url}",
                        doc_path,
                        f"检查文件路径: {full_path}"
                    ))
            # 检查HTTP链接（可选，需要网络请求）
            elif url.startswith('http'):
                # 这里可以添加HTTP链接验证
                pass
        
        return issues
    
    def _validate_code_examples(self, content: str, doc_path: str) -> List[DocumentationIssue]:
        """验证代码示例"""
        issues = []
        
        # 提取代码块
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(code_pattern, content, re.MULTILINE | re.DOTALL)
        
        for lang, code in matches:
            # 检查Python语法
            if lang == 'python' or lang == 'py':
                try:
                    compile(code, '<string>', 'exec')
                except SyntaxError as e:
                    issues.append(DocumentationIssue(
                        IssueType.EXAMPLE_ERROR,
                        IssueSeverity.HIGH,
                        f"Python代码语法错误: {e}",
                        doc_path,
                        "修复代码语法错误"
                    ))
            
            # 检查代码长度
            if len(code.split('\n')) < 3:
                issues.append(DocumentationIssue(
                    IssueType.EXAMPLE_ERROR,
                    IssueSeverity.LOW,
                    "代码示例过于简单",
                    doc_path,
                    "提供更完整的示例"
                ))
        
        return issues
    
    def _validate_format_consistency(self, content: str, doc_path: str) -> List[DocumentationIssue]:
        """验证格式一致性"""
        issues = []
        
        # 检查标题层级
        lines = content.split('\n')
        header_levels = []
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                header_levels.append(level)
        
        # 检查标题层级跳跃
        for i in range(1, len(header_levels)):
            if header_levels[i] - header_levels[i-1] > 1:
                issues.append(DocumentationIssue(
                    IssueType.FORMAT_ERROR,
                    IssueSeverity.MEDIUM,
                    f"标题层级跳跃过大: 从H{header_levels[i-1]}到H{header_levels[i]}",
                    doc_path,
                    "调整标题层级，避免跳跃"
                ))
        
        # 检查列表格式
        list_patterns = [
            r'^\d+\.',  # 有序列表
            r'^-',     # 无序列表
            r'^\*'     # 无序列表
        ]
        
        list_consistency = True
        current_list_type = None
        
        for line in lines:
            line = line.strip()
            if any(re.match(pattern, line) for pattern in list_patterns):
                # 确定列表类型
                if re.match(r'^\d+\.', line):
                    list_type = 'ordered'
                elif line.startswith('-'):
                    list_type = 'unordered_dash'
                elif line.startswith('*'):
                    list_type = 'unordered_star'
                else:
                    continue
                
                if current_list_type is None:
                    current_list_type = list_type
                elif current_list_type != list_type:
                    list_consistency = False
                    break
            elif line and not line.startswith('#'):
                current_list_type = None
        
        if not list_consistency:
            issues.append(DocumentationIssue(
                IssueType.FORMAT_ERROR,
                IssueSeverity.LOW,
                "列表格式不一致",
                doc_path,
                "统一列表格式，使用相同的标记符号"
            ))
        
        return issues
    
    def generate_quality_report(self, issues: List[DocumentationIssue]) -> Dict[str, Any]:
        """生成质量报告"""
        # 统计问题
        issue_counts = {}
        severity_counts = {}
        
        for issue in issues:
            issue_type = issue.issue_type.value
            severity = issue.severity.value
            
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # 计算质量分数
        total_issues = len(issues)
        critical_issues = severity_counts.get('critical', 0)
        high_issues = severity_counts.get('high', 0)
        
        if total_issues == 0:
            quality_score = 100
        else:
            # 根据问题严重程度计算分数
            score_deduction = (critical_issues * 20) + (high_issues * 10) + (total_issues - critical_issues - high_issues) * 2
            quality_score = max(0, 100 - score_deduction)
        
        return {
            'total_issues': total_issues,
            'quality_score': quality_score,
            'issue_counts': issue_counts,
            'severity_counts': severity_counts,
            'issues': [
                {
                    'type': issue.issue_type.value,
                    'severity': issue.severity.value,
                    'description': issue.description,
                    'location': issue.location,
                    'suggestion': issue.suggestion
                }
                for issue in issues
            ]
        }

# 使用示例
def main():
    print("=== 文档质量检查器 ===")
    
    # 创建验证器
    validator = DocumentationValidator()
    
    # 验证文档
    doc_path = "./README.md"
    print(f"验证文档: {doc_path}")
    
    issues = validator.validate_documentation(doc_path)
    
    if issues:
        print(f"发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. [{issue.severity.value.upper()}] {issue.description}")
            print(f"   位置: {issue.location}")
            print(f"   建议: {issue.suggestion}")
            print()
    else:
        print("文档质量良好，未发现问题")
    
    # 生成质量报告
    report = validator.generate_quality_report(issues)
    
    print("=== 质量报告 ===")
    print(f"总问题数: {report['total_issues']}")
    print(f"质量分数: {report['quality_score']}/100")
    print(f"问题分布: {report['issue_counts']}")
    print(f"严重程度分布: {report['severity_counts']}")

if __name__ == '__main__':
    main()
```

## 文档生成最佳实践

### 文档结构设计
1. **层次清晰**: 使用合理的标题层级，便于导航
2. **内容完整**: 覆盖安装、使用、API、故障排除等完整内容
3. **示例丰富**: 提供实际可运行的代码示例
4. **图文并茂**: 适当使用图表说明复杂概念
5. **持续更新**: 与代码保持同步更新

### 自动化策略
1. **代码分析**: 自动提取函数、类、模块信息
2. **模板管理**: 使用标准化模板确保一致性
3. **多格式输出**: 支持Markdown、HTML、PDF等多种格式
4. **质量检查**: 自动验证文档完整性和格式
5. **版本控制**: 与代码版本管理集成

### 质量保证方法
1. **内容验证**: 检查必需章节和内容完整性
2. **链接检查**: 验证内部和外部链接有效性
3. **代码测试**: 验证示例代码的正确性
4. **格式规范**: 确保文档格式一致性
5. **定期审查**: 建立定期文档审查机制

### 用户体验优化
1. **快速导航**: 提供清晰的目录和索引
2. **搜索友好**: 使用关键词和标签优化搜索
3. **多语言支持**: 考虑国际化需求
4. **响应式设计**: 适配不同设备和屏幕
5. **交互式文档**: 提供在线示例和演示

## 相关技能

- **code-review** - 代码审查
- **test-generation** - 测试生成
- **api-validator** - API验证
- **performance-profiler** - 性能分析
