# Markdown Validator 技术参考

## 概述

Markdown Validator 是一个专门用于验证 Markdown 文档格式和结构的工具，提供语法检查、链接验证、格式规范检查和文档质量评估功能。

## 核心功能

### 语法验证
- **基础语法**: 检查 Markdown 基础语法正确性
- **扩展语法**: 支持 GFM、CommonMark 等扩展语法
- **嵌套结构**: 验证标题、列表、代码块的嵌套关系
- **特殊字符**: 检查转义字符和特殊符号使用

### 链接验证
- **内部链接**: 验证文档内部锚点链接
- **外部链接**: 检查外部 URL 的可访问性
- **图片链接**: 验证图片链接的有效性
- **相对路径**: 检查相对路径链接的正确性

### 格式检查
- **文档结构**: 检查标题层次和文档结构
- **列表格式**: 验证有序和无序列表的格式
- **代码块**: 检查代码块语法高亮和格式
- **表格格式**: 验证 Markdown 表格的语法

## 配置指南

### 基础配置
```json
{
  "markdown-validator": {
    "enabled": true,
    "parser": "commonmark",
    "extensions": [".md", ".markdown"],
    "rules": {
      "syntax": {
        "enabled": true,
        "strict": false,
        "allow-html": false
      },
      "links": {
        "enabled": true,
        "check-internal": true,
        "check-external": true,
        "timeout": 5000
      },
      "format": {
        "enabled": true,
        "line-length": 120,
        "trailing-whitespace": true,
        "final-newline": true
      }
    }
  }
}
```

### 高级配置
```json
{
  "markdown-validator": {
    "advanced": {
      "custom-rules": [
        {
          "name": "require-alt-text",
          "pattern": "!\\[.*?\\]\\(.*?\\)",
          "message": "Images must have alt text",
          "severity": "warning"
        },
        {
          "name": "heading-style",
          "pattern": "^#{1,6}\\s+",
          "message": "Headings must have space after #",
          "severity": "error"
        }
      ],
      "ignore-paths": [
        "node_modules/**",
        "dist/**",
        "*.min.md"
      ],
      "plugins": [
        "markdownlint",
        "remark-lint",
        "markdown-it"
      ]
    }
  }
}
```

## API 参考

### 验证器主类
```python
class MarkdownValidator:
    def __init__(self, config=None):
        self.config = Config(config or {})
        self.parser = self._create_parser()
        self.rules = RuleManager(self.config)
        self.link_checker = LinkChecker(self.config)
    
    def validate_file(self, file_path):
        """验证单个 Markdown 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.validate_content(content, file_path)
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(f"File read error: {e}")],
                file_path=file_path
            )
    
    def validate_content(self, content, file_path=None):
        """验证 Markdown 内容"""
        # 解析 Markdown
        ast = self.parser.parse(content)
        
        # 执行规则检查
        syntax_errors = self.rules.check_syntax(ast, content)
        format_errors = self.rules.check_format(content)
        structure_errors = self.rules.check_structure(ast)
        
        # 检查链接
        link_errors = self.link_checker.check_links(content, file_path)
        
        all_errors = syntax_errors + format_errors + structure_errors + link_errors
        
        return ValidationResult(
            valid=len(all_errors) == 0,
            errors=all_errors,
            file_path=file_path,
            ast=ast
        )
    
    def validate_directory(self, directory_path):
        """验证目录中的所有 Markdown 文件"""
        results = []
        
        for root, dirs, files in os.walk(directory_path):
            # 忽略配置的路径
            dirs[:] = [d for d in dirs if not self._should_ignore_path(d)]
            
            for file in files:
                if self._is_markdown_file(file):
                    file_path = os.path.join(root, file)
                    result = self.validate_file(file_path)
                    results.append(result)
        
        return DirectoryValidationResult(results)
```

### 规则管理器
```python
class RuleManager:
    def __init__(self, config):
        self.config = config
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """加载验证规则"""
        rules = []
        
        # 语法规则
        if self.config.get('rules.syntax.enabled', True):
            rules.extend([
                HeadingRule(),
                ListRule(),
                CodeBlockRule(),
                LinkRule(),
                ImageRule()
            ])
        
        # 格式规则
        if self.config.get('rules.format.enabled', True):
            rules.extend([
                LineLengthRule(self.config.get('rules.format.line-length', 120)),
                TrailingWhitespaceRule(),
                FinalNewlineRule()
            ])
        
        # 自定义规则
        custom_rules = self.config.get('advanced.custom-rules', [])
        for rule_config in custom_rules:
            rules.append(CustomRule(rule_config))
        
        return rules
    
    def check_syntax(self, ast, content):
        """检查语法规则"""
        errors = []
        
        for rule in self.syntax_rules:
            rule_errors = rule.check(ast, content)
            errors.extend(rule_errors)
        
        return errors
    
    def check_format(self, content):
        """检查格式规则"""
        errors = []
        
        for rule in self.format_rules:
            rule_errors = rule.check(content)
            errors.extend(rule_errors)
        
        return errors
    
    def check_structure(self, ast):
        """检查文档结构"""
        errors = []
        
        # 检查标题层次
        errors.extend(self._check_heading_hierarchy(ast))
        
        # 检查文档结构完整性
        errors.extend(self._check_document_structure(ast))
        
        return errors
```

### 链接检查器
```python
class LinkChecker:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.get('rules.links.timeout', 5)
    
    def check_links(self, content, file_path=None):
        """检查文档中的所有链接"""
        errors = []
        
        # 提取链接
        links = self._extract_links(content)
        
        for link in links:
            if link['type'] == 'internal':
                errors.extend(self._check_internal_link(link, file_path))
            elif link['type'] == 'external':
                errors.extend(self._check_external_link(link))
            elif link['type'] == 'image':
                errors.extend(self._check_image_link(link, file_path))
        
        return errors
    
    def _extract_links(self, content):
        """提取文档中的所有链接"""
        links = []
        
        # 匹配 Markdown 链接 [text](url)
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text, url = match.groups()
            
            if url.startswith('#'):
                links.append({
                    'type': 'internal',
                    'url': url,
                    'text': text,
                    'position': match.start()
                })
            elif url.startswith(('http://', 'https://')):
                links.append({
                    'type': 'external',
                    'url': url,
                    'text': text,
                    'position': match.start()
                })
            else:
                links.append({
                    'type': 'image' if text.startswith('!') else 'relative',
                    'url': url,
                    'text': text,
                    'position': match.start()
                })
        
        return links
    
    def _check_external_link(self, link):
        """检查外部链接的可访问性"""
        errors = []
        
        try:
            response = self.session.head(link['url'], allow_redirects=True)
            if response.status_code >= 400:
                errors.append(ValidationError(
                    f"External link returned {response.status_code}: {link['url']}",
                    position=link['position'],
                    severity='error'
                ))
        except requests.RequestException as e:
            errors.append(ValidationError(
                f"Failed to check external link: {link['url']} - {str(e)}",
                position=link['position'],
                severity='warning'
            ))
        
        return errors
```

## 内置规则

### 语法规则
```python
class HeadingRule:
    """标题规则检查"""
    
    def check(self, ast, content):
        errors = []
        
        # 检查标题格式
        heading_pattern = r'^(#{1,6})([^#\s].*)$'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                
                # 检查标题后是否有空格
                if not re.match(r'^#{1,6}\s+', line):
                    errors.append(ValidationError(
                        "Heading must have space after #",
                        line=line_num,
                        severity='error'
                    ))
                
                # 检查标题是否为空
                if not text:
                    errors.append(ValidationError(
                        "Heading cannot be empty",
                        line=line_num,
                        severity='error'
                    ))
        
        return errors

class ListRule:
    """列表规则检查"""
    
    def check(self, ast, content):
        errors = []
        lines = content.split('\n')
        
        in_list = False
        list_indent = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.lstrip()
            
            # 检查无序列表
            if re.match(r'^[-*+]\s+', stripped):
                if not in_list:
                    in_list = True
                    list_indent = len(line) - len(stripped)
                elif self._get_indent(line) != list_indent:
                    errors.append(ValidationError(
                        "List items must have consistent indentation",
                        line=line_num,
                        severity='error'
                    ))
            
            # 检查有序列表
            elif re.match(r'^\d+\.\s+', stripped):
                if not in_list:
                    in_list = True
                    list_indent = len(line) - len(stripped)
                elif self._get_indent(line) != list_indent:
                    errors.append(ValidationError(
                        "List items must have consistent indentation",
                        line=line_num,
                        severity='error'
                    ))
            
            # 检查列表结束
            elif in_list and stripped and not re.match(r'^\s*[-*+\d\.]', line):
                in_list = False
        
        return errors
    
    def _get_indent(self, line):
        """获取行缩进"""
        return len(line) - len(line.lstrip())
```

### 格式规则
```python
class LineLengthRule:
    """行长度规则检查"""
    
    def __init__(self, max_length=120):
        self.max_length = max_length
    
    def check(self, content):
        errors = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # 忽略代码块中的行
            if self._in_code_block(content, line_num):
                continue
            
            if len(line) > self.max_length:
                errors.append(ValidationError(
                    f"Line too long ({len(line)} > {self.max_length})",
                    line=line_num,
                    severity='warning'
                ))
        
        return errors

class TrailingWhitespaceRule:
    """尾随空白字符规则检查"""
    
    def check(self, content):
        errors = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            if line.endswith(' ') or line.endswith('\t'):
                errors.append(ValidationError(
                    "Trailing whitespace not allowed",
                    line=line_num,
                    severity='warning'
                ))
        
        return errors
```

## 集成指南

### 命令行工具
```python
#!/usr/bin/env python3
# mdvalidator.py

import argparse
import sys
from markdown_validator import MarkdownValidator

def main():
    parser = argparse.ArgumentParser(description='Markdown Validator')
    parser.add_argument('paths', nargs='+', help='Files or directories to validate')
    parser.add_argument('--config', '-c', help='Configuration file')
    parser.add_argument('--format', '-f', choices=['text', 'json', 'html'], 
                       default='text', help='Output format')
    parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    validator = MarkdownValidator(config)
    
    # 验证文件
    all_results = []
    for path in args.paths:
        if os.path.isfile(path):
            result = validator.validate_file(path)
            all_results.append(result)
        elif os.path.isdir(path):
            result = validator.validate_directory(path)
            all_results.extend(result.results)
    
    # 输出结果
    formatter = OutputFormatter(args.format)
    output = formatter.format(all_results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)
    
    # 返回退出码
    has_errors = any(not result.valid for result in all_results)
    sys.exit(1 if has_errors else 0)

if __name__ == '__main__':
    main()
```

### VS Code 扩展
```typescript
import * as vscode from 'vscode';
import { MarkdownValidator } from './validator';

export function activate(context: vscode.ExtensionContext) {
    const validator = new MarkdownValidator();
    
    // 诊断提供者
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('markdown-validator');
    context.subscriptions.push(diagnosticCollection);
    
    // 验证当前文档
    const validateDocument = async (document: vscode.TextDocument) => {
        if (document.languageId !== 'markdown') {
            return;
        }
        
        const result = await validator.validateContent(document.getText(), document.uri.fsPath);
        const diagnostics = result.errors.map(error => {
            const range = new vscode.Range(
                new vscode.Position(error.line - 1, error.column || 0),
                new vscode.Position(error.line - 1, error.column || 0)
            );
            
            return new vscode.Diagnostic(
                range,
                error.message,
                error.severity === 'error' ? vscode.DiagnosticSeverity.Error : vscode.DiagnosticSeverity.Warning
            );
        });
        
        diagnosticCollection.set(document.uri, diagnostics);
    };
    
    // 注册事件监听器
    vscode.workspace.onDidOpenTextDocument(validateDocument);
    vscode.workspace.onDidChangeTextDocument(async (event) => {
        await validateDocument(event.document);
    });
    
    // 注册命令
    const validateCommand = vscode.commands.registerCommand('markdown-validator.validate', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            await validateDocument(editor.document);
            vscode.window.showInformationMessage('Markdown validation complete!');
        }
    });
    
    context.subscriptions.push(validateCommand);
}
```

## 最佳实践

### 文档结构
1. **标题层次**: 使用合理的标题层次结构
2. **目录导航**: 为长文档提供目录
3. **段落分隔**: 使用空行分隔段落
4. **列表格式**: 保持列表格式的一致性

### 链接管理
1. **描述性链接**: 使用描述性的链接文本
2. **相对路径**: 优先使用相对路径链接
3. **图片优化**: 为图片添加 alt 文本
4. **链接检查**: 定期检查外部链接的有效性

### 代码块
1. **语法高亮**: 为代码块指定语言类型
2. **代码注释**: 在代码块中添加必要的注释
3. **代码长度**: 保持代码块长度适中
4. **代码格式**: 保持代码格式的一致性

## 故障排除

### 常见问题
1. **解析错误**: 检查 Markdown 语法是否正确
2. **链接失效**: 更新或移除失效的链接
3. **格式不一致**: 统一文档格式规范
4. **性能问题**: 优化大文档的验证性能

### 调试技巧
1. **详细日志**: 启用详细的验证日志
2. **分步验证**: 逐步验证文档的不同部分
3. **规则禁用**: 临时禁用特定规则进行调试
4. **输出分析**: 分析验证输出的详细信息

## 工具和资源

### 开发工具
- **Markdown 编辑器**: Typora, Mark Text, Obsidian
- **在线验证器**: Markdown Lint Online, Daring Fireball
- **浏览器扩展**: Markdown Viewer, Markdown Preview
- **IDE 插件**: 各大 IDE 的 Markdown 插件

### 相关库
- **Python**: markdown, markdown2, mistune
- **JavaScript**: marked, markdown-it, remark
- **Ruby**: kramdown, redcarpet
- **Go**: goldmark, blackfriday

### 学习资源
- [Markdown 官方指南](https://www.markdownguide.org/)
- [CommonMark 规范](https://commonmark.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [Markdown 语法速查](https://markdown-it.github.io/)

### 社区支持
- [Stack Overflow Markdown 标签](https://stackoverflow.com/questions/tagged/markdown)
- [Reddit Markdown 社区](https://www.reddit.com/r/Markdown/)
- [GitHub Markdown 讨论](https://github.com/markdown/markdown/discussions)
- [Markdown 中文社区](https://markdown.org.cn/)
