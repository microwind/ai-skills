# 文件分析器参考文档

## 文件分析器概述

### 什么是文件分析器
文件分析器是一个用于分析文件内容、结构、属性和元数据的工具。它可以处理各种类型的文件，包括代码文件、配置文件、文档文件、二进制文件等，提供全面的文件分析功能。

### 主要功能
- **文件类型检测**: 自动识别文件类型和编码格式
- **代码分析**: 语法分析、结构分析、质量分析
- **文本分析**: 内容统计、语言检测、关键词分析
- **二进制分析**: 文件格式检测、十六进制分析、签名验证
- **性能分析**: 文件大小分析、时间分析、依赖关系分析
- **报告生成**: 生成详细的分析报告和可视化图表

## 文件类型检测

### 基于扩展名的检测
```python
# file_type_detector.py
import os
import mimetypes
from typing import Optional, Dict, List

class FileTypeDetector:
    def __init__(self):
        # 文件扩展名映射
        self.extension_map = {
            # 代码文件
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c_header',
            '.hpp': 'cpp_header',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            
            # 配置文件
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.properties': 'properties',
            '.ini': 'ini',
            '.toml': 'toml',
            '.conf': 'config',
            '.cfg': 'config',
            
            # 文档文件
            '.md': 'markdown',
            '.txt': 'text',
            '.pdf': 'pdf',
            '.doc': 'word',
            '.docx': 'word',
            '.xls': 'excel',
            '.xlsx': 'excel',
            '.ppt': 'powerpoint',
            '.pptx': 'powerpoint',
            
            # 二进制文件
            '.exe': 'executable',
            '.dll': 'dll',
            '.so': 'shared_library',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.bmp': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.mp4': 'video',
            '.avi': 'video',
            '.zip': 'archive',
            '.rar': 'archive',
            '.7z': 'archive',
            '.tar': 'archive',
            '.gz': 'archive'
        }
    
    def detect_by_extension(self, file_path: str) -> Optional[str]:
        """基于文件扩展名检测文件类型"""
        _, ext = os.path.splitext(file_path.lower())
        return self.extension_map.get(ext)
    
    def detect_by_mime_type(self, file_path: str) -> Optional[str]:
        """基于MIME类型检测文件类型"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type.split('/')[0]
        return None
    
    def detect_file_type(self, file_path: str) -> Dict[str, str]:
        """综合检测文件类型"""
        file_info = {}
        
        # 基于扩展名检测
        extension_type = self.detect_by_extension(file_path)
        if extension_type:
            file_info['extension_type'] = extension_type
        
        # 基于MIME类型检测
        mime_type = self.detect_by_mime_type(file_path)
        if mime_type:
            file_info['mime_type'] = mime_type
        
        # 文件基本信息
        if os.path.exists(file_path):
            file_info['file_size'] = os.path.getsize(file_path)
            file_info['file_name'] = os.path.basename(file_path)
            file_info['file_extension'] = os.path.splitext(file_path)[1]
        
        return file_info

# 使用示例
detector = FileTypeDetector()

# 检测代码文件
code_files = ['example.java', 'script.py', 'app.js', 'config.json']
for file_path in code_files:
    file_info = detector.detect_file_type(file_path)
    print(f"文件: {file_path}")
    print(f"类型信息: {file_info}")
    print("-" * 40)
```

### 基于文件内容的检测
```python
# content_detector.py
import re
import chardet
from typing import Optional, Dict, List

class ContentDetector:
    def __init__(self):
        # 语言特征模式
        self.language_patterns = {
            'java': [
                r'public\s+class\s+\w+',
                r'import\s+java\.',
                r'public\s+static\s+void\s+main',
                r'package\s+\w+'
            ],
            'python': [
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'def\s+\w+\s*\(',
                r'if\s+__name__\s*==\s*["\']__main__["\']'
            ],
            'javascript': [
                r'function\s+\w+\s*\(',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'console\.log'
            ],
            'html': [
                r'<!DOCTYPE\s+html>',
                r'<html[^>]*>',
                r'<head[^>]*>',
                r'<body[^>]*>',
                r'<script[^>]*>'
            ],
            'css': [
                r'\.?\w+\s*\{[^}]*\}',
                r'@media\s+[^{]*\{',
                r'@import\s+',
                r'@font-face\s*'
            ],
            'json': [
                r'^\s*\{[^}]*\}\s*$',
                r'^\s*\[[^\]]*\]\s*$',
                r'"\w+"\s*:',
                r'\[\s*\{.*?\}\s*\]'
            ],
            'xml': [
                r'<\?xml\s+version',
                r'<[^>]+>[^<]*<\/[^>]+>',
                r'<[^>]*\/>',
                r'<!\[CDATA\[.*?\]\]>'
            ],
            'yaml': [
                r'^\w+\s*:\s*',
                r'^\s*-\s+\w+',
                r'^\s*\w+\s*:',
                r'^\s*#\s+'
            ]
        }
        
        # 二进制文件特征
        self.binary_signatures = {
            'png': b'\x89PNG\r\n\x1a\n',
            'jpg': b'\xff\xd8\xff',
            'gif': b'GIF87a|GIF89a',
            'pdf': b'%PDF-',
            'zip': b'PK\x03\x04',
            'exe': b'MZ\x90\x00',
            'class': b'\xca\xfe\xba\xbe'
        }
    
    def detect_encoding(self, file_path: str) -> Dict[str, any]:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(8192)  # 读取前8KB
            
            result = chardet.detect(raw_data)
            return {
                'encoding': result.get('encoding'),
                'confidence': result.get('confidence'),
                'language': result.get('language')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def detect_language_by_content(self, file_path: str) -> Dict[str, any]:
        """基于文件内容检测编程语言"""
        try:
            # 检测编码
            encoding_info = self.detect_encoding(file_path)
            encoding = encoding_info.get('encoding', 'utf-8')
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            # 计算每种语言的匹配分数
            language_scores = {}
            
            for language, patterns in self.language_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    score += len(matches)
                
                if score > 0:
                    language_scores[language] = score
            
            # 找出最可能的语言
            if language_scores:
                best_language = max(language_scores, key=language_scores.get)
                confidence = language_scores[best_language] / len(content.split('\n'))
                
                return {
                    'detected_language': best_language,
                    'confidence': min(confidence, 1.0),
                    'all_scores': language_scores,
                    'encoding_info': encoding_info
                }
            
            return {'detected_language': None, 'confidence': 0.0}
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_binary_type(self, file_path: str) -> Optional[str]:
        """检测二进制文件类型"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)  # 读取文件头
            
            for file_type, signature in self.binary_signatures.items():
                if header.startswith(signature):
                    return file_type
            
            return None
            
        except Exception as e:
            return None
    
    def is_binary_file(self, file_path: str) -> bool:
        """判断是否为二进制文件"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True

# 使用示例
detector = ContentDetector()

# 检测代码文件语言
code_files = ['example.java', 'script.py', 'index.html', 'data.json']
for file_path in code_files:
    print(f"分析文件: {file_path}")
    
    # 检测语言
    lang_result = detector.detect_language_by_content(file_path)
    print(f"检测结果: {lang_result}")
    
    # 检测编码
    encoding_result = detector.detect_encoding(file_path)
    print(f"编码信息: {encoding_result}")
    
    print("-" * 50)
```

## 代码分析

### 语法分析器
```python
# code_analyzer.py
import ast
import re
from typing import Dict, List, Any, Optional
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self):
        self.language_analyzers = {
            'python': self._analyze_python,
            'java': self._analyze_java,
            'javascript': self._analyze_javascript
        }
    
    def analyze_code(self, file_path: str, language: str) -> Dict[str, Any]:
        """分析代码文件"""
        if language not in self.language_analyzers:
            return {'error': f'不支持的语言: {language}'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.language_analyzers[language](content)
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """分析Python代码"""
        try:
            tree = ast.parse(content)
            
            analysis = {
                'language': 'python',
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'lines_of_code': len(content.split('\n')),
                'comments': self._extract_python_comments(content),
                'docstrings': self._extract_python_docstrings(tree)
            }
            
            # 分析函数和类
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, 'unparse') else [],
                        'complexity': self._calculate_complexity(node)
                    }
                    analysis['functions'].append(func_info)
                    analysis['complexity'] += func_info['complexity']
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [],
                        'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)],
                        'decorators': [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, 'unparse') else []
                    }
                    
                    # 分析类方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'line': item.lineno,
                                'args': [arg.arg for arg in item.args.args],
                                'complexity': self._calculate_complexity(item)
                            }
                            class_info['methods'].append(method_info)
                            analysis['complexity'] += method_info['complexity']
                    
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append({
                                'module': alias.name,
                                'alias': alias.asname,
                                'line': node.lineno
                            })
                    else:
                        analysis['imports'].append({
                            'module': node.module,
                            'names': [alias.name for alias in node.names],
                            'line': node.lineno
                        })
            
            return analysis
            
        except SyntaxError as e:
            return {'error': f'语法错误: {e}'}
    
    def _analyze_java(self, content: str) -> Dict[str, Any]:
        """分析Java代码"""
        analysis = {
            'language': 'java',
            'package': None,
            'imports': [],
            'classes': [],
            'methods': [],
            'lines_of_code': len(content.split('\n')),
            'comments': self._extract_java_comments(content)
        }
        
        # 提取包名
        package_match = re.search(r'package\s+([\w.]+);', content)
        if package_match:
            analysis['package'] = package_match.group(1)
        
        # 提取导入
        import_matches = re.findall(r'import\s+([\w.]+);', content)
        analysis['imports'] = import_matches
        
        # 提取类
        class_pattern = r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?'
        class_matches = re.finditer(class_pattern, content)
        
        for match in class_matches:
            class_info = {
                'name': match.group(1),
                'extends': match.group(2),
                'implements': [c.strip() for c in match.group(3).split(',')] if match.group(3) else [],
                'line': content[:match.start()].count('\n') + 1
            }
            analysis['classes'].append(class_info)
        
        # 提取方法
        method_pattern = r'(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        method_matches = re.finditer(method_pattern, content)
        
        for match in method_matches:
            method_info = {
                'name': match.group(1),
                'line': content[:match.start()].count('\n') + 1
            }
            analysis['methods'].append(method_info)
        
        return analysis
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """分析JavaScript代码"""
        analysis = {
            'language': 'javascript',
            'functions': [],
            'variables': [],
            'lines_of_code': len(content.split('\n')),
            'comments': self._extract_js_comments(content)
        }
        
        # 提取函数
        function_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'var\s+(\w+)\s*=\s*function\s*\([^)]*\)',
            r'(\w+)\s*:\s*function\s*\([^)]*\)'
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_info = {
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                }
                analysis['functions'].append(func_info)
        
        # 提取变量
        variable_patterns = [
            r'const\s+(\w+)\s*=',
            r'let\s+(\w+)\s*=',
            r'var\s+(\w+)\s*='
        ]
        
        for pattern in variable_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                var_info = {
                    'name': match.group(1),
                    'line': content[:match.start()].count('\n') + 1
                }
                analysis['variables'].append(var_info)
        
        return analysis
    
    def _extract_python_comments(self, content: str) -> List[str]:
        """提取Python注释"""
        comments = []
        
        # 单行注释
        single_line_comments = re.findall(r'#\s*(.*)', content)
        comments.extend(single_line_comments)
        
        # 多行注释 (docstring)
        docstring_pattern = r'"""(.*?)"""'
        docstrings = re.findall(docstring_pattern, content, re.DOTALL)
        comments.extend(docstrings)
        
        return comments
    
    def _extract_python_docstrings(self, tree: ast.AST) -> List[str]:
        """提取Python文档字符串"""
        docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    docstrings.append(node.body[0].value.s)
                elif (node.body and isinstance(node.body[0], ast.Expr) and 
                      isinstance(node.body[0].value, ast.Constant) and 
                      isinstance(node.body[0].value.value, str)):
                    docstrings.append(node.body[0].value.value)
        
        return docstrings
    
    def _extract_java_comments(self, content: str) -> List[str]:
        """提取Java注释"""
        comments = []
        
        # 单行注释
        single_line_comments = re.findall(r'//\s*(.*)', content)
        comments.extend(single_line_comments)
        
        # 多行注释
        multi_line_pattern = r'/\*(.*?)\*/'
        multi_line_comments = re.findall(multi_line_pattern, content, re.DOTALL)
        comments.extend(multi_line_comments)
        
        return comments
    
    def _extract_js_comments(self, content: str) -> List[str]:
        """提取JavaScript注释"""
        comments = []
        
        # 单行注释
        single_line_comments = re.findall(r'//\s*(.*)', content)
        comments.extend(single_line_comments)
        
        # 多行注释
        multi_line_pattern = r'/\*(.*?)\*/'
        multi_line_comments = re.findall(multi_line_pattern, content, re.DOTALL)
        comments.extend(multi_line_comments)
        
        return comments
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

# 使用示例
analyzer = CodeAnalyzer()

# 分析Python代码
python_analysis = analyzer.analyze_code('example.py', 'python')
print("Python代码分析结果:")
print(python_analysis)

# 分析Java代码
java_analysis = analyzer.analyze_code('Example.java', 'java')
print("\nJava代码分析结果:")
print(java_analysis)

# 分析JavaScript代码
js_analysis = analyzer.analyze_code('script.js', 'javascript')
print("\nJavaScript代码分析结果:")
print(js_analysis)
```

### 代码质量分析
```python
# code_quality_analyzer.py
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict

class CodeQualityAnalyzer:
    def __init__(self):
        self.quality_rules = {
            'naming_conventions': self._check_naming_conventions,
            'code_duplication': self._check_code_duplication,
            'method_length': self._check_method_length,
            'class_size': self._check_class_size,
            'comment_ratio': self._check_comment_ratio,
            'complexity': self._check_complexity,
            'security_issues': self._check_security_issues
        }
        
        # 命名规范
        self.naming_patterns = {
            'java': {
                'class': r'^[A-Z][a-zA-Z0-9]*$',
                'method': r'^[a-z][a-zA-Z0-9]*$',
                'variable': r'^[a-z][a-zA-Z0-9]*$',
                'constant': r'^[A-Z][A-Z0-9_]*$'
            },
            'python': {
                'class': r'^[A-Z][a-zA-Z0-9]*$',
                'method': r'^[a-z_][a-z0-9_]*$',
                'variable': r'^[a-z_][a-z0-9_]*$',
                'constant': r'^[A-Z][A-Z0-9_]*$'
            },
            'javascript': {
                'class': r'^[A-Z][a-zA-Z0-9]*$',
                'method': r'^[a-z][a-zA-Z0-9]*$',
                'variable': r'^[a-z][a-zA-Z0-9]*$',
                'constant': r'^[A-Z][A-Z0-9_]*$'
            }
        }
        
        # 安全问题模式
        self.security_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'sprintf\s*\([^)]*%s[^)]*\)',
                r'\.format\s*\([^)]*\)'
            ],
            'xss': [
                r'innerHTML\s*=',
                r'outerHTML\s*=',
                r'document\.write\s*\(',
                r'eval\s*\('
            ],
            'hardcoded_password': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'pwd\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']'
            ],
            'path_traversal': [
                r'\.\.\/',
                r'\.\.\\',
                r'readFile\s*\([^)]*\.\.',
                r'open\s*\([^)]*\.\.'
            ]
        }
    
    def analyze_quality(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """分析代码质量"""
        quality_report = {
            'overall_score': 0,
            'issues': [],
            'metrics': {},
            'recommendations': []
        }
        
        total_score = 0
        rule_count = 0
        
        for rule_name, rule_func in self.quality_rules.items():
            try:
                rule_result = rule_func(file_path, language, code_analysis)
                quality_report['metrics'][rule_name] = rule_result
                
                # 计算分数
                if 'score' in rule_result:
                    total_score += rule_result['score']
                    rule_count += 1
                
                # 收集问题
                if 'issues' in rule_result:
                    quality_report['issues'].extend(rule_result['issues'])
                
                # 收集建议
                if 'recommendations' in rule_result:
                    quality_report['recommendations'].extend(rule_result['recommendations'])
                    
            except Exception as e:
                quality_report['metrics'][rule_name] = {'error': str(e)}
        
        # 计算总体分数
        if rule_count > 0:
            quality_report['overall_score'] = total_score / rule_count
        
        return quality_report
    
    def _check_naming_conventions(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查命名规范"""
        issues = []
        score = 100
        
        if language not in self.naming_patterns:
            return {'score': 0, 'issues': ['不支持的语言']}
        
        patterns = self.naming_patterns[language]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 检查类名
            if 'classes' in code_analysis:
                for class_info in code_analysis['classes']:
                    class_name = class_info['name']
                    if not re.match(patterns['class'], class_name):
                        issues.append({
                            'type': 'naming_convention',
                            'severity': 'warning',
                            'line': class_info.get('line', 0),
                            'message': f'类名 "{class_name}" 不符合命名规范',
                            'suggestion': f'应该使用 {patterns["class"]} 格式'
                        })
                        score -= 5
            
            # 检查方法名
            if 'functions' in code_analysis:
                for func_info in code_analysis['functions']:
                    func_name = func_info['name']
                    if not re.match(patterns['method'], func_name):
                        issues.append({
                            'type': 'naming_convention',
                            'severity': 'warning',
                            'line': func_info.get('line', 0),
                            'message': f'方法名 "{func_name}" 不符合命名规范',
                            'suggestion': f'应该使用 {patterns["method"]} 格式'
                        })
                        score -= 3
            
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['遵循统一的命名规范', '使用有意义的名称']
        }
    
    def _check_code_duplication(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查代码重复"""
        issues = []
        score = 100
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的重复检测：检查相似的代码行
            lines = content.split('\n')
            line_groups = defaultdict(list)
            
            for i, line in enumerate(lines):
                # 移除空白和注释，规范化代码
                normalized = re.sub(r'\s+', ' ', line.strip())
                if normalized and not normalized.startswith('#') and not normalized.startswith('//'):
                    line_groups[normalized].append(i + 1)
            
            # 找出重复的代码行
            for normalized_line, line_numbers in line_groups.items():
                if len(line_numbers) > 1:
                    issues.append({
                        'type': 'code_duplication',
                        'severity': 'info',
                        'lines': line_numbers,
                        'message': f'发现重复代码行: {normalized_line}',
                        'suggestion': '考虑提取为函数或方法'
                    })
                    score -= 2
            
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['提取重复代码为函数', '使用继承或组合减少重复']
        }
    
    def _check_method_length(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查方法长度"""
        issues = []
        score = 100
        max_method_length = 50  # 最大方法行数
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            if 'functions' in code_analysis:
                for func_info in code_analysis['functions']:
                    func_name = func_info['name']
                    start_line = func_info.get('line', 0)
                    
                    # 简单估算方法长度（不精确，需要更复杂的解析）
                    method_length = 0
                    in_method = False
                    
                    for i in range(start_line - 1, len(lines)):
                        line = lines[i].strip()
                        
                        if line.startswith('def ') or line.startswith('function ') or '(' in line:
                            in_method = True
                        
                        if in_method:
                            method_length += 1
                            
                            # 检查方法结束
                            if line and not line.startswith(' ') and not line.startswith('\t'):
                                if i > start_line - 1:  # 不是方法定义行
                                    break
                    
                    if method_length > max_method_length:
                        issues.append({
                            'type': 'method_length',
                            'severity': 'warning',
                            'line': start_line,
                            'message': f'方法 "{func_name}" 过长 ({method_length} 行)',
                            'suggestion': f'建议将方法拆分，最大不超过 {max_method_length} 行'
                        })
                        score -= 10
            
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['保持方法简短', '单一职责原则']
        }
    
    def _check_class_size(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查类大小"""
        issues = []
        score = 100
        max_class_size = 300  # 最大类行数
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            if 'classes' in code_analysis:
                for class_info in code_analysis['classes']:
                    class_name = class_info['name']
                    start_line = class_info.get('line', 0)
                    
                    # 简单估算类大小
                    class_size = 0
                    in_class = False
                    
                    for i in range(start_line - 1, len(lines)):
                        line = lines[i].strip()
                        
                        if line.startswith('class ') or line.startswith('public class '):
                            in_class = True
                        
                        if in_class:
                            class_size += 1
                            
                            # 检查类结束
                            if line == '}' and i > start_line:
                                break
                    
                    if class_size > max_class_size:
                        issues.append({
                            'type': 'class_size',
                            'severity': 'warning',
                            'line': start_line,
                            'message': f'类 "{class_name}" 过大 ({class_size} 行)',
                            'suggestion': f'建议将类拆分，最大不超过 {max_class_size} 行'
                        })
                        score -= 15
            
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['保持类的小巧', '遵循单一职责原则']
        }
    
    def _check_comment_ratio(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查注释比例"""
        issues = []
        score = 100
        min_comment_ratio = 0.1  # 最小注释比例 10%
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            total_lines = len([line for line in lines if line.strip()])
            comment_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                    comment_lines += 1
            
            if total_lines > 0:
                comment_ratio = comment_lines / total_lines
                
                if comment_ratio < min_comment_ratio:
                    issues.append({
                        'type': 'comment_ratio',
                        'severity': 'info',
                        'message': f'注释比例过低 ({comment_ratio:.1%})',
                        'suggestion': f'建议注释比例不低于 {min_comment_ratio:.1%}'
                    })
                    score -= 10
                
                score = min(100, max(0, 100 - (min_comment_ratio - comment_ratio) * 100))
            
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['添加适当的注释', '注释复杂逻辑']
        }
    
    def _check_complexity(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查代码复杂度"""
        issues = []
        score = 100
        max_complexity = 10  # 最大圈复杂度
        
        if 'complexity' in code_analysis:
            total_complexity = code_analysis['complexity']
            
            if total_complexity > max_complexity:
                issues.append({
                    'type': 'complexity',
                    'severity': 'warning',
                    'message': f'代码复杂度过高 ({total_complexity})',
                    'suggestion': f'建议圈复杂度不超过 {max_complexity}'
                })
                score -= 20
            
            score = min(100, max(0, 100 - (total_complexity - max_complexity) * 5))
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['简化复杂逻辑', '使用设计模式']
        }
    
    def _check_security_issues(self, file_path: str, language: str, code_analysis: Dict) -> Dict[str, Any]:
        """检查安全问题"""
        issues = []
        score = 100
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for issue_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1]
                        
                        severity = 'critical' if issue_type in ['sql_injection', 'xss'] else 'warning'
                        
                        issues.append({
                            'type': 'security',
                            'subtype': issue_type,
                            'severity': severity,
                            'line': line_num,
                            'message': f'发现潜在安全问题: {issue_type}',
                            'code': line_content.strip(),
                            'suggestion': '请检查并修复安全问题'
                        })
                        
                        score -= 20 if severity == 'critical' else 10
            
        except Exception as e:
            return {'error': str(e)}
        
        return {
            'score': max(0, score),
            'issues': issues,
            'recommendations': ['使用参数化查询', '输入验证和输出编码']
        }

# 使用示例
quality_analyzer = CodeQualityAnalyzer()

# 假设我们已经有了代码分析结果
code_analysis = {
    'language': 'python',
    'functions': [
        {'name': 'bad_function_name', 'line': 10},
        {'name': 'very_long_function_name_that_is_too_long', 'line': 20}
    ],
    'classes': [
        {'name': 'badclassname', 'line': 5}
    ],
    'complexity': 15
}

# 分析代码质量
quality_report = quality_analyzer.analyze_quality('example.py', 'python', code_analysis)
print("代码质量报告:")
print(f"总体分数: {quality_report['overall_score']}")
print(f"问题数量: {len(quality_report['issues'])}")
for issue in quality_report['issues']:
    print(f"- {issue['message']} (行 {issue.get('line', 'N/A')})")
```

## 文本分析

### 文本统计分析
```python
# text_analyzer.py
import re
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple
import jieba
import chardet

class TextAnalyzer:
    def __init__(self):
        self.stop_words = {
            'english': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'},
            'chinese': {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它', '们', '这个', '那个', '什么', '怎么', '为什么', '哪里', '什么时候', '如何'}
        }
    
    def analyze_text(self, file_path: str) -> Dict[str, Any]:
        """分析文本文件"""
        try:
            # 检测编码
            encoding = self._detect_encoding(file_path)
            
            # 读取文件
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            analysis = {
                'encoding': encoding,
                'basic_stats': self._basic_text_stats(content),
                'language_detection': self._detect_language(content),
                'word_analysis': self._analyze_words(content),
                'sentence_analysis': self._analyze_sentences(content),
                'readability': self._analyze_readability(content),
                'keyword_analysis': self._analyze_keywords(content)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(8192)
            
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8')
            
        except:
            return 'utf-8'
    
    def _basic_text_stats(self, content: str) -> Dict[str, Any]:
        """基础文本统计"""
        lines = content.split('\n')
        characters = len(content)
        characters_no_spaces = len(content.replace(' ', '').replace('\t', '').replace('\n', ''))
        words = re.findall(r'\b\w+\b', content)
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'total_characters': characters,
            'characters_no_spaces': characters_no_spaces,
            'total_words': len(words),
            'unique_words': len(set(words.lower() for word in words)),
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }
    
    def _detect_language(self, content: str) -> Dict[str, Any]:
        """检测文本语言"""
        # 简单的语言检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        
        total_chars = len(content.replace(' ', '').replace('\t', '').replace('\n', ''))
        
        if total_chars == 0:
            return {'primary_language': 'unknown', 'confidence': 0.0}
        
        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_words / total_chars
        
        if chinese_ratio > 0.3:
            primary_language = 'chinese'
            confidence = chinese_ratio
        elif english_ratio > 0.5:
            primary_language = 'english'
            confidence = english_ratio
        else:
            primary_language = 'mixed'
            confidence = max(chinese_ratio, english_ratio)
        
        return {
            'primary_language': primary_language,
            'confidence': confidence,
            'chinese_chars': chinese_chars,
            'english_words': english_words,
            'ratios': {
                'chinese': chinese_ratio,
                'english': english_ratio
            }
        }
    
    def _analyze_words(self, content: str) -> Dict[str, Any]:
        """分析词汇"""
        language_info = self._detect_language(content)
        primary_language = language_info['primary_language']
        
        if primary_language == 'chinese':
            return self._analyze_chinese_words(content)
        elif primary_language == 'english':
            return self._analyze_english_words(content)
        else:
            # 混合语言，分别分析
            chinese_analysis = self._analyze_chinese_words(content)
            english_analysis = self._analyze_english_words(content)
            
            return {
                'type': 'mixed_language',
                'chinese': chinese_analysis,
                'english': english_analysis
            }
    
    def _analyze_chinese_words(self, content: str) -> Dict[str, Any]:
        """分析中文词汇"""
        # 使用jieba分词
        words = jieba.lcut(content)
        
        # 过滤停用词和标点
        stop_words = self.stop_words['chinese']
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1 and not re.match(r'[^\u4e00-\u9fff]', word)]
        
        # 词频统计
        word_freq = Counter(filtered_words)
        
        return {
            'type': 'chinese',
            'total_words': len(words),
            'unique_words': len(set(words)),
            'filtered_words': len(filtered_words),
            'word_frequency': dict(word_freq.most_common(20)),
            'average_word_length': sum(len(word) for word in filtered_words) / len(filtered_words) if filtered_words else 0
        }
    
    def _analyze_english_words(self, content: str) -> Dict[str, Any]:
        """分析英文词汇"""
        # 提取英文单词
        words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
        
        # 过滤停用词
        stop_words = self.stop_words['english']
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # 词频统计
        word_freq = Counter(filtered_words)
        
        # 词长统计
        word_lengths = [len(word) for word in filtered_words]
        
        return {
            'type': 'english',
            'total_words': len(words),
            'unique_words': len(set(words)),
            'filtered_words': len(filtered_words),
            'word_frequency': dict(word_freq.most_common(20)),
            'average_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            'word_length_distribution': Counter(word_lengths)
        }
    
    def _analyze_sentences(self, content: str) -> Dict[str, Any]:
        """分析句子"""
        # 句子分割
        sentences = re.split(r'[.!?。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 句子长度统计
        sentence_lengths = [len(sentence) for sentence in sentences]
        
        return {
            'total_sentences': len(sentences),
            'average_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentences else 0,
            'longest_sentence': max(sentence_lengths) if sentence_lengths else 0,
            'shortest_sentence': min(sentence_lengths) if sentence_lengths else 0,
            'sentence_length_distribution': Counter(sentence_lengths)
        }
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """分析可读性"""
        language_info = self._detect_language(content)
        primary_language = language_info['primary_language']
        
        if primary_language == 'english':
            return self._analyze_english_readability(content)
        else:
            return self._analyze_chinese_readability(content)
    
    def _analyze_english_readability(self, content: str) -> Dict[str, Any]:
        """分析英文可读性"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b[a-zA-Z]+\b', content)
        
        if not sentences or not words:
            return {'readability_score': 0, 'level': 'unknown'}
        
        # 计算平均句子长度
        avg_sentence_length = len(words) / len(sentences)
        
        # 计算平均音节数（简化版本）
        def count_syllables(word):
            word = word.lower()
            vowels = 'aeiouy'
            syllable_count = 0
            prev_char_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_char_was_vowel:
                    syllable_count += 1
                prev_char_was_vowel = is_vowel
            
            if word.endswith('e'):
                syllable_count -= 1
            if syllable_count == 0:
                syllable_count = 1
            
            return syllable_count
        
        total_syllables = sum(count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / len(words)
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # 确定阅读级别
        if flesch_score >= 90:
            level = 'very_easy'
        elif flesch_score >= 80:
            level = 'easy'
        elif flesch_score >= 70:
            level = 'fairly_easy'
        elif flesch_score >= 60:
            level = 'standard'
        elif flesch_score >= 50:
            level = 'fairly_difficult'
        elif flesch_score >= 30:
            level = 'difficult'
        else:
            level = 'very_difficult'
        
        return {
            'readability_score': round(flesch_score, 2),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'formula': 'Flesch Reading Ease'
        }
    
    def _analyze_chinese_readability(self, content: str) -> Dict[str, Any]:
        """分析中文可读性"""
        # 中文可读性分析（简化版本）
        sentences = re.split(r'[。！？]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = jieba.lcut(content)
        
        if not sentences or not words:
            return {'readability_score': 0, 'level': 'unknown'}
        
        # 计算平均句子长度（字数）
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        # 计算平均词汇长度
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # 简化的可读性评分
        readability_score = 100 - (avg_sentence_length * 2) - (avg_word_length * 5)
        
        # 确定阅读级别
        if readability_score >= 80:
            level = 'very_easy'
        elif readability_score >= 60:
            level = 'easy'
        elif readability_score >= 40:
            level = 'standard'
        elif readability_score >= 20:
            level = 'difficult'
        else:
            level = 'very_difficult'
        
        return {
            'readability_score': round(readability_score, 2),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(avg_word_length, 2),
            'formula': 'Simplified Chinese Readability'
        }
    
    def _analyze_keywords(self, content: str) -> Dict[str, Any]:
        """分析关键词"""
        language_info = self._detect_language(content)
        primary_language = language_info['primary_language']
        
        if primary_language == 'chinese':
            return self._extract_chinese_keywords(content)
        elif primary_language == 'english':
            return self._extract_english_keywords(content)
        else:
            return self._extract_mixed_keywords(content)
    
    def _extract_chinese_keywords(self, content: str) -> Dict[str, Any]:
        """提取中文关键词"""
        words = jieba.lcut(content)
        
        # 过滤停用词
        stop_words = self.stop_words['chinese']
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 词频统计
        word_freq = Counter(filtered_words)
        
        # 提取关键词（基于词频和词长）
        keywords = []
        for word, freq in word_freq.most_common(50):
            if len(word) >= 2 and freq >= 2:
                keywords.append({
                    'word': word,
                    'frequency': freq,
                    'length': len(word),
                    'importance': freq * len(word)  # 简单的重要性计算
                })
        
        # 按重要性排序
        keywords.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'type': 'chinese',
            'keywords': keywords[:20],
            'total_keywords': len(keywords)
        }
    
    def _extract_english_keywords(self, content: str) -> Dict[str, Any]:
        """提取英文关键词"""
        words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
        
        # 过滤停用词
        stop_words = self.stop_words['english']
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # 词频统计
        word_freq = Counter(filtered_words)
        
        # 提取关键词
        keywords = []
        for word, freq in word_freq.most_common(50):
            if freq >= 2:
                keywords.append({
                    'word': word,
                    'frequency': freq,
                    'length': len(word),
                    'importance': freq * len(word)
                })
        
        # 按重要性排序
        keywords.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'type': 'english',
            'keywords': keywords[:20],
            'total_keywords': len(keywords)
        }
    
    def _extract_mixed_keywords(self, content: str) -> Dict[str, Any]:
        """提取混合语言关键词"""
        chinese_keywords = self._extract_chinese_keywords(content)
        english_keywords = self._extract_english_keywords(content)
        
        # 合并关键词
        all_keywords = []
        
        for kw in chinese_keywords.get('keywords', []):
            all_keywords.append({
                'word': kw['word'],
                'language': 'chinese',
                'frequency': kw['frequency'],
                'importance': kw['importance']
            })
        
        for kw in english_keywords.get('keywords', []):
            all_keywords.append({
                'word': kw['word'],
                'language': 'english',
                'frequency': kw['frequency'],
                'importance': kw['importance']
            })
        
        # 按重要性排序
        all_keywords.sort(key=lambda x: x['importance'], reverse=True)
        
        return {
            'type': 'mixed',
            'keywords': all_keywords[:20],
            'total_keywords': len(all_keywords),
            'chinese_count': len(chinese_keywords.get('keywords', [])),
            'english_count': len(english_keywords.get('keywords', []))
        }

# 使用示例
analyzer = TextAnalyzer()

# 分析文本文件
text_analysis = analyzer.analyze_text('example.txt')
print("文本分析结果:")
print(f"基础统计: {text_analysis['basic_stats']}")
print(f"语言检测: {text_analysis['language_detection']}")
print(f"词汇分析: {text_analysis['word_analysis']}")
print(f"可读性分析: {text_analysis['readability']}")
print(f"关键词分析: {text_analysis['keyword_analysis']}")
```

## 二进制分析

### 十六进制分析器
```python
# hex_analyzer.py
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple

class HexAnalyzer:
    def __init__(self):
        self.file_signatures = {
            'PNG': b'\x89PNG\r\n\x1a\n',
            'JPEG': b'\xff\xd8\xff',
            'GIF87a': b'GIF87a',
            'GIF89a': b'GIF89a',
            'PDF': b'%PDF-',
            'ZIP': b'PK\x03\x04',
            'EXE': b'MZ\x90\x00',
            'ELF': b'\x7fELF',
            'BMP': b'BM',
            'TIFF': b'II*\x00',
            'MP3': b'ID3',
            'WAV': b'RIFF',
            'AVI': b'RIFF',
            'MP4': b'ftyp'
        }
    
    def analyze_binary_file(self, file_path: str) -> Dict[str, Any]:
        """分析二进制文件"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            analysis = {
                'file_info': self._get_file_info(file_path, content),
                'file_type': self._detect_file_type(content),
                'hex_dump': self._generate_hex_dump(content),
                'hash_values': self._calculate_hashes(content),
                'entropy': self._calculate_entropy(content),
                'strings': self._extract_strings(content),
                'structure_analysis': self._analyze_structure(content)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_file_info(self, file_path: str, content: bytes) -> Dict[str, Any]:
        """获取文件基本信息"""
        import os
        
        return {
            'file_name': os.path.basename(file_path),
            'file_size': len(content),
            'file_size_human': self._format_size(len(content))
        }
    
    def _detect_file_type(self, content: bytes) -> Dict[str, Any]:
        """检测文件类型"""
        detected_types = []
        
        for file_type, signature in self.file_signatures.items():
            if content.startswith(signature):
                detected_types.append(file_type)
        
        return {
            'detected_types': detected_types,
            'is_executable': any(ext in detected_types for ext in ['EXE', 'ELF']),
            'is_image': any(ext in detected_types for ext in ['PNG', 'JPEG', 'GIF', 'BMP', 'TIFF']),
            'is_archive': any(ext in detected_types for ext in ['ZIP']),
            'is_document': any(ext in detected_types for ext in ['PDF'])
        }
    
    def _generate_hex_dump(self, content: bytes, bytes_per_line: int = 16) -> List[str]:
        """生成十六进制转储"""
        hex_lines = []
        
        for i in range(0, len(content), bytes_per_line):
            chunk = content[i:i + bytes_per_line]
            
            # 十六进制部分
            hex_part = ' '.join(f'{byte:02x}' for byte in chunk)
            hex_part = hex_part.ljust(bytes_per_line * 3 - 1)  # 对齐
            
            # ASCII部分
            ascii_part = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
            
            # 地址
            address = f'{i:08x}'
            
            hex_lines.append(f'{address}  {hex_part}  |{ascii_part}|')
        
        return hex_lines
    
    def _calculate_hashes(self, content: bytes) -> Dict[str, str]:
        """计算各种哈希值"""
        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        hashes = {}
        
        for algorithm in algorithms:
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(content)
            hashes[algorithm] = hash_obj.hexdigest()
        
        return hashes
    
    def _calculate_entropy(self, content: bytes) -> Dict[str, Any]:
        """计算文件熵值"""
        if not content:
            return {'entropy': 0.0, 'is_encrypted': False}
        
        # 计算字节频率
        byte_counts = [0] * 256
        for byte in content:
            byte_counts[byte] += 1
        
        # 计算熵
        entropy = 0.0
        data_len = len(content)
        
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability.bit_length() - 1)
        
        # 判断是否可能加密
        is_encrypted = entropy > 7.0  # 高熵值可能表示加密或压缩
        
        return {
            'entropy': round(entropy, 4),
            'is_encrypted': is_encrypted,
            'entropy_level': 'high' if entropy > 7.0 else 'medium' if entropy > 5.0 else 'low'
        }
    
    def _extract_strings(self, content: bytes, min_length: int = 4) -> List[Dict[str, Any]]:
        """提取字符串"""
        strings = []
        current_string = ""
        start_offset = 0
        
        for i, byte in enumerate(content):
            if 32 <= byte <= 126:  # 可打印ASCII字符
                if not current_string:
                    start_offset = i
                current_string += chr(byte)
            else:
                if len(current_string) >= min_length:
                    strings.append({
                        'string': current_string,
                        'offset': start_offset,
                        'length': len(current_string)
                    })
                current_string = ""
        
        # 处理文件末尾的字符串
        if len(current_string) >= min_length:
            strings.append({
                'string': current_string,
                'offset': start_offset,
                'length': len(current_string)
            })
        
        return strings
    
    def _analyze_structure(self, content: bytes) -> Dict[str, Any]:
        """分析文件结构"""
        structure = {
            'header_analysis': self._analyze_header(content),
            'patterns': self._find_patterns(content),
            'sections': self._identify_sections(content)
        }
        
        return structure
    
    def _analyze_header(self, content: bytes) -> Dict[str, Any]:
        """分析文件头"""
        header_size = min(512, len(content))
        header = content[:header_size]
        
        return {
            'header_size': header_size,
            'header_hex': header.hex(),
            'header_ascii': ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in header),
            'magic_numbers': [f'{byte:02x}' for byte in header[:8]]
        }
    
    def _find_patterns(self, content: bytes) -> List[Dict[str, Any]]:
        """查找常见模式"""
        patterns = []
        
        # 查找重复字节序列
        for length in range(2, 8):  # 2-7字节序列
            for i in range(len(content) - length):
                sequence = content[i:i + length]
                
                # 查找相同序列的其他出现位置
                for j in range(i + length, len(content) - length):
                    if content[j:j + length] == sequence:
                        patterns.append({
                            'type': 'repeated_sequence',
                            'sequence': sequence.hex(),
                            'length': length,
                            'offsets': [i, j]
                        })
                        break
        
        # 查找零字节区域
        zero_regions = []
        start = None
        
        for i, byte in enumerate(content):
            if byte == 0:
                if start is None:
                    start = i
            else:
                if start is not None:
                    zero_regions.append({
                        'type': 'zero_region',
                        'start': start,
                        'end': i - 1,
                        'length': i - start
                    })
                    start = None
        
        # 处理文件末尾的零字节区域
        if start is not None:
            zero_regions.append({
                'type': 'zero_region',
                'start': start,
                'end': len(content) - 1,
                'length': len(content) - start
            })
        
        patterns.extend(zero_regions)
        
        return patterns
    
    def _identify_sections(self, content: bytes) -> List[Dict[str, Any]]:
        """识别文件节区"""
        sections = []
        
        # 简单的节区识别（基于常见的节区标记）
        section_markers = {
            b'.text': '代码段',
            b'.data': '数据段',
            b'.bss': 'BSS段',
            b'.rdata': '只读数据段',
            b'.idata': '导入表',
            b'.edata': '导出表',
            b'.reloc': '重定位表',
            b'.debug': '调试信息'
        }
        
        for marker, description in section_markers.items():
            offset = content.find(marker)
            if offset != -1:
                sections.append({
                    'name': description,
                    'marker': marker.decode('ascii', errors='ignore'),
                    'offset': offset,
                    'type': 'section_marker'
                })
        
        return sections
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def search_hex_pattern(self, file_path: str, pattern: str, case_sensitive: bool = True) -> List[Dict[str, Any]]:
        """搜索十六进制模式"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 转换搜索模式
            if pattern.startswith('0x') or pattern.startswith('0X'):
                # 十六进制输入
                search_bytes = bytes.fromhex(pattern[2:])
            else:
                # ASCII输入
                if case_sensitive:
                    search_bytes = pattern.encode('ascii')
                else:
                    search_bytes = pattern.lower().encode('ascii')
                    content = content.lower()
            
            # 搜索模式
            matches = []
            offset = 0
            
            while True:
                offset = content.find(search_bytes, offset)
                if offset == -1:
                    break
                
                matches.append({
                    'offset': offset,
                    'pattern': search_bytes.hex(),
                    'context': self._get_context(content, offset, len(search_bytes))
                })
                
                offset += 1
            
            return matches
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def _get_context(self, content: bytes, offset: int, length: int, context_size: int = 32) -> Dict[str, str]:
        """获取搜索上下文"""
        start = max(0, offset - context_size)
        end = min(len(content), offset + length + context_size)
        
        context_bytes = content[start:end]
        
        return {
            'before': content[start:offset].hex(),
            'match': content[offset:offset + length].hex(),
            'after': content[offset + length:end].hex(),
            'full_context': context_bytes.hex()
        }

# 使用示例
analyzer = HexAnalyzer()

# 分析二进制文件
binary_analysis = analyzer.analyze_binary_file('example.exe')
print("二进制文件分析结果:")
print(f"文件信息: {binary_analysis['file_info']}")
print(f"文件类型: {binary_analysis['file_type']}")
print(f"哈希值: {binary_analysis['hash_values']}")
print(f"熵值: {binary_analysis['entropy']}")

# 搜索十六进制模式
search_results = analyzer.search_hex_pattern('example.exe', '4D5A')  # 搜索PE头
print(f"搜索结果: {search_results}")
```

## 报告生成

### HTML报告生成器
```python
# report_generator.py
import json
from datetime import datetime
from typing import Dict, List, Any
import base64

class HTMLReportGenerator:
    def __init__(self):
        self.template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件分析报告</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            color: #666;
            margin-top: 10px;
            font-size: 1.1em;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        .metric-card h3 {
            margin: 0 0 10px 0;
            color: #333;
            font-size: 1.1em;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        .metric-unit {
            color: #666;
            font-size: 0.9em;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .table th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }
        .table tr:hover {
            background-color: #f5f5f5;
        }
        .severity-high {
            color: #d32f2f;
            font-weight: bold;
        }
        .severity-medium {
            color: #f57c00;
            font-weight: bold;
        }
        .severity-low {
            color: #388e3c;
            font-weight: bold;
        }
        .code-block {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-fill {
            height: 100%;
            background-color: #4CAF50;
            transition: width 0.3s ease;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            .metric-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>文件分析报告</h1>
            <div class="subtitle">生成时间: {generation_time}</div>
        </div>
        
        {content}
        
        <div class="footer">
            <p>报告由文件分析器自动生成 | 生成时间: {generation_time}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def generate_report(self, analysis_data: Dict[str, Any], output_path: str) -> bool:
        """生成HTML报告"""
        try:
            content = self._build_content(analysis_data)
            
            html_content = self.template.format(
                generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                content=content
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            return False
    
    def _build_content(self, data: Dict[str, Any]) -> str:
        """构建报告内容"""
        content_sections = []
        
        # 文件基本信息
        if 'file_info' in data:
            content_sections.append(self._build_file_info_section(data['file_info']))
        
        # 代码分析结果
        if 'code_analysis' in data:
            content_sections.append(self._build_code_analysis_section(data['code_analysis']))
        
        # 文本分析结果
        if 'text_analysis' in data:
            content_sections.append(self._build_text_analysis_section(data['text_analysis']))
        
        # 二进制分析结果
        if 'binary_analysis' in data:
            content_sections.append(self._build_binary_analysis_section(data['binary_analysis']))
        
        # 质量分析结果
        if 'quality_analysis' in data:
            content_sections.append(self._build_quality_analysis_section(data['quality_analysis']))
        
        return '\n'.join(content_sections)
    
    def _build_file_info_section(self, file_info: Dict[str, Any]) -> str:
        """构建文件信息部分"""
        html = """
        <div class="section">
            <h2>文件基本信息</h2>
            <div class="metric-grid">
        """
        
        metrics = [
            ('文件名', file_info.get('file_name', 'N/A')),
            ('文件大小', file_info.get('file_size_human', 'N/A')),
            ('文件类型', file_info.get('file_type', 'N/A')),
            ('编码格式', file_info.get('encoding', 'N/A'))
        ]
        
        for label, value in metrics:
            html += f"""
                <div class="metric-card">
                    <h3>{label}</h3>
                    <div class="metric-value">{value}</div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _build_code_analysis_section(self, code_analysis: Dict[str, Any]) -> str:
        """构建代码分析部分"""
        html = """
        <div class="section">
            <h2>代码分析结果</h2>
        """
        
        # 基础统计
        if 'basic_stats' in code_analysis:
            stats = code_analysis['basic_stats']
            html += """
                <h3>基础统计</h3>
                <div class="metric-grid">
            """
            
            metrics = [
                ('代码行数', stats.get('lines_of_code', 0)),
                ('函数数量', len(code_analysis.get('functions', []))),
                ('类数量', len(code_analysis.get('classes', []))),
                ('圈复杂度', code_analysis.get('complexity', 0))
            ]
            
            for label, value in metrics:
                html += f"""
                    <div class="metric-card">
                        <h3>{label}</h3>
                        <div class="metric-value">{value}</div>
                    </div>
                """
            
            html += "</div>"
        
        # 函数列表
        if 'functions' in code_analysis:
            html += """
                <h3>函数列表</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>函数名</th>
                            <th>行号</th>
                            <th>复杂度</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for func in code_analysis['functions']:
                html += f"""
                    <tr>
                        <td>{func.get('name', 'N/A')}</td>
                        <td>{func.get('line', 'N/A')}</td>
                        <td>{func.get('complexity', 'N/A')}</td>
                    </tr>
                """
            
            html += """
                    </tbody>
                </table>
            """
        
        html += "</div>"
        return html
    
    def _build_text_analysis_section(self, text_analysis: Dict[str, Any]) -> str:
        """构建文本分析部分"""
        html = """
        <div class="section">
            <h2>文本分析结果</h2>
        """
        
        # 基础统计
        if 'basic_stats' in text_analysis:
            stats = text_analysis['basic_stats']
            html += """
                <h3>基础统计</h3>
                <div class="metric-grid">
            """
            
            metrics = [
                ('总行数', stats.get('total_lines', 0)),
                ('总字符数', stats.get('total_characters', 0)),
                ('总词数', stats.get('total_words', 0)),
                ('平均词长', f"{stats.get('average_word_length', 0):.1f}")
            ]
            
            for label, value in metrics:
                html += f"""
                    <div class="metric-card">
                        <h3>{label}</h3>
                        <div class="metric-value">{value}</div>
                    </div>
                """
            
            html += "</div>"
        
        # 语言检测
        if 'language_detection' in text_analysis:
            lang_info = text_analysis['language_detection']
            html += f"""
                <h3>语言检测</h3>
                <div class="metric-card">
                    <h3>主要语言</h3>
                    <div class="metric-value">{lang_info.get('primary_language', 'N/A')}</div>
                    <div class="metric-unit">置信度: {lang_info.get('confidence', 0):.1%}</div>
                </div>
            """
        
        # 关键词
        if 'keyword_analysis' in text_analysis:
            keywords = text_analysis['keyword_analysis'].get('keywords', [])
            html += """
                <h3>关键词分析</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>关键词</th>
                            <th>频率</th>
                            <th>重要性</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for keyword in keywords[:10]:  # 显示前10个
                html += f"""
                    <tr>
                        <td>{keyword.get('word', 'N/A')}</td>
                        <td>{keyword.get('frequency', 0)}</td>
                        <td>{keyword.get('importance', 0)}</td>
                    </tr>
                """
            
            html += """
                    </tbody>
                </table>
            """
        
        html += "</div>"
        return html
    
    def _build_binary_analysis_section(self, binary_analysis: Dict[str, Any]) -> str:
        """构建二进制分析部分"""
        html = """
        <div class="section">
            <h2>二进制分析结果</h2>
        """
        
        # 文件类型
        if 'file_type' in binary_analysis:
            file_type = binary_analysis['file_type']
            html += f"""
                <h3>文件类型检测</h3>
                <div class="metric-card">
                    <h3>检测到的类型</h3>
                    <div class="metric-value">{', '.join(file_type.get('detected_types', ['N/A']))}</div>
                </div>
            """
        
        # 哈希值
        if 'hash_values' in binary_analysis:
            hashes = binary_analysis['hash_values']
            html += """
                <h3>哈希值</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>算法</th>
                            <th>哈希值</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for algorithm, hash_value in hashes.items():
                html += f"""
                    <tr>
                        <td>{algorithm.upper()}</td>
                        <td><code>{hash_value}</code></td>
                    </tr>
                """
            
            html += """
                    </tbody>
                </table>
            """
        
        # 熵值分析
        if 'entropy' in binary_analysis:
            entropy = binary_analysis['entropy']
            html += f"""
                <h3>熵值分析</h3>
                <div class="metric-card">
                    <h3>文件熵值</h3>
                    <div class="metric-value">{entropy.get('entropy', 0)}</div>
                    <div class="metric-unit">级别: {entropy.get('entropy_level', 'N/A')}</div>
                </div>
            """
        
        html += "</div>"
        return html
    
    def _build_quality_analysis_section(self, quality_analysis: Dict[str, Any]) -> str:
        """构建质量分析部分"""
        html = """
        <div class="section">
            <h2>代码质量分析</h2>
        """
        
        # 总体分数
        overall_score = quality_analysis.get('overall_score', 0)
        html += f"""
            <h3>总体质量分数</h3>
            <div class="metric-card">
                <h3>质量评分</h3>
                <div class="metric-value">{overall_score:.1f}</div>
                <div class="metric-unit">满分100分</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {overall_score}%"></div>
            </div>
        """
        
        # 问题列表
        issues = quality_analysis.get('issues', [])
        if issues:
            html += """
                <h3>发现的问题</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>类型</th>
                            <th>严重程度</th>
                            <th>行号</th>
                            <th>描述</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for issue in issues:
                severity_class = f"severity-{issue.get('severity', 'low')}"
                html += f"""
                    <tr>
                        <td>{issue.get('type', 'N/A')}</td>
                        <td class="{severity_class}">{issue.get('severity', 'N/A')}</td>
                        <td>{issue.get('line', 'N/A')}</td>
                        <td>{issue.get('message', 'N/A')}</td>
                    </tr>
                """
            
            html += """
                    </tbody>
                </table>
            """
        
        html += "</div>"
        return html

# 使用示例
generator = HTMLReportGenerator()

# 模拟分析数据
analysis_data = {
    'file_info': {
        'file_name': 'example.py',
        'file_size_human': '2.5 KB',
        'file_type': 'Python',
        'encoding': 'UTF-8'
    },
    'code_analysis': {
        'basic_stats': {
            'lines_of_code': 150,
            'functions': 8,
            'classes': 2,
            'complexity': 25
        },
        'functions': [
            {'name': 'main', 'line': 10, 'complexity': 5},
            {'name': 'process_data', 'line': 25, 'complexity': 8}
        ],
        'classes': [
            {'name': 'DataProcessor', 'line': 5}
        ]
    },
    'quality_analysis': {
        'overall_score': 75.5,
        'issues': [
            {'type': 'naming_convention', 'severity': 'medium', 'line': 25, 'message': '方法名不符合规范'},
            {'type': 'complexity', 'severity': 'high', 'line': 30, 'message': '方法复杂度过高'}
        ]
    }
}

# 生成报告
success = generator.generate_report(analysis_data, 'analysis_report.html')
print(f"报告生成成功: {success}")
```

## 参考资源

### 文件格式规范
- [File Extension Registry](https://www.iana.org/assignments/media-types/)
- [Magic Number Database](https://www.garykessler.net/library/file_sigs.html)
- [PE File Format](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format)
- [ELF File Format](https://refspecs.linuxfoundation.org/elf/elf.pdf)

### 代码分析工具
- [AST Module (Python)](https://docs.python.org/3/library/ast.html)
- [JavaParser](https://javaparser.org/)
- [Esprima (JavaScript)](https://esprima.org/)
- [Clang (C/C++)](https://clang.llvm.org/)

### 文本处理库
- [jieba (Chinese Text Processing)](https://github.com/fxsjy/jieba)
- [NLTK (Natural Language Toolkit)](https://www.nltk.org/)
- [chardet (Encoding Detection)](https://github.com/chardet/chardet)
- [langdetect (Language Detection)](https://github.com/Mimino666/langdetect)

### 二进制分析工具
- [binwalk](https://github.com/ReFirmLabs/binwalk)
- [hexdump](https://linux.die.net/man/1/hexdump)
- [xxd](https://linux.die.net/man/1/xxd)
- [file command](https://linux.die.net/man/1/file)

### 报告生成框架
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [WeasyPrint (HTML to PDF)](https://weasyprint.org/)
- [ReportLab (PDF Generation)](https://www.reportlab.com/)
- [Matplotlib (Charts)](https://matplotlib.org/)
