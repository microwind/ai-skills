# 代码格式化器参考文档

## 代码格式化器概述

### 什么是代码格式化器
代码格式化器是一个自动化工具，用于按照预定义的规则和标准统一格式化源代码。该工具支持多种编程语言，提供灵活的配置选项，能够自动处理缩进、空格、换行、引号、分号等格式问题，确保代码风格的一致性和可读性。

### 主要功能
- **多语言支持**: 支持JavaScript、TypeScript、Python、Java、C#、Go等多种编程语言
- **格式化引擎**: 集成Prettier、Black、ESLint等主流格式化工具
- **自定义规则**: 支持自定义格式化规则和代码风格
- **批量处理**: 支持单文件、目录、项目级别的批量格式化
- **验证检查**: 格式化前后的验证和质量检查
- **IDE集成**: 与主流IDE和编辑器的无缝集成
- **CI/CD集成**: 支持持续集成和持续部署流程
- **报告生成**: 详细的格式化报告和统计信息

## 格式化引擎

### 通用格式化引擎
```python
# formatter_engine.py
import os
import subprocess
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import yaml

class Language(Enum):
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    PHP = "php"
    RUBY = "ruby"

class FormatterType(Enum):
    PRETTIER = "prettier"
    BLACK = "black"
    AUTOPEP8 = "autopep8"
    YAPF = "yapf"
    ESLINT = "eslint"
    GOOGLE_JAVA_FORMAT = "google_java_format"
    DOTNET_FORMAT = "dotnet_format"
    GOFMT = "gofmt"
    RUSTFMT = "rustfmt"
    CLANG_FORMAT = "clang_format"

@dataclass
class FormatResult:
    success: bool
    file_path: str
    original_content: str
    formatted_content: str
    changes_made: bool
    error_message: Optional[str] = None
    warnings: List[str] = None

@dataclass
class FormatterConfig:
    language: Language
    formatter_type: FormatterType
    config_file: Optional[str] = None
    options: Dict[str, Any] = None
    file_extensions: List[str] = None
    ignore_patterns: List[str] = None

class FormatterEngine:
    def __init__(self):
        self.formatters = {}
        self.configs = {}
        self._setup_default_formatters()
    
    def _setup_default_formatters(self):
        """设置默认格式化器"""
        self.formatters = {
            FormatterType.PRETTIER: PrettierFormatter(),
            FormatterType.BLACK: BlackFormatter(),
            FormatterType.AUTOPEP8: Autopep8Formatter(),
            FormatterType.YAPF: YAPFFormatter(),
            FormatterType.ESLINT: ESLintFormatter(),
            FormatterType.GOOGLE_JAVA_FORMAT: GoogleJavaFormatter(),
            FormatterType.DOTNET_FORMAT: DotnetFormatter(),
            FormatterType.GOFMT: GofmtFormatter(),
            FormatterType.RUSTFMT: RustfmtFormatter(),
            FormatterType.CLANG_FORMAT: ClangFormatter()
        }
    
    def register_formatter(self, formatter_type: FormatterType, formatter):
        """注册格式化器"""
        self.formatters[formatter_type] = formatter
    
    def format_file(self, file_path: str, config: FormatterConfig) -> FormatResult:
        """格式化单个文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return FormatResult(
                    success=False,
                    file_path=file_path,
                    original_content="",
                    formatted_content="",
                    changes_made=False,
                    error_message=f"文件不存在: {file_path}"
                )
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 获取格式化器
            formatter = self.formatters.get(config.formatter_type)
            if not formatter:
                return FormatResult(
                    success=False,
                    file_path=file_path,
                    original_content=original_content,
                    formatted_content="",
                    changes_made=False,
                    error_message=f"不支持的格式化器: {config.formatter_type}"
                )
            
            # 格式化文件
            result = formatter.format(file_path, original_content, config)
            
            return result
            
        except Exception as e:
            return FormatResult(
                success=False,
                file_path=file_path,
                original_content="",
                formatted_content="",
                changes_made=False,
                error_message=str(e)
            )
    
    def format_directory(self, directory_path: str, config: FormatterConfig, 
                        recursive: bool = True) -> List[FormatResult]:
        """格式化目录"""
        results = []
        
        # 获取文件列表
        files = self._get_files_to_format(directory_path, config, recursive)
        
        for file_path in files:
            result = self.format_file(file_path, config)
            results.append(result)
        
        return results
    
    def _get_files_to_format(self, directory_path: str, config: FormatterConfig, 
                           recursive: bool) -> List[str]:
        """获取需要格式化的文件列表"""
        files = []
        directory = Path(directory_path)
        
        # 遍历目录
        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # 检查文件扩展名
                if config.file_extensions:
                    if file_path.suffix not in config.file_extensions:
                        continue
                
                # 检查忽略模式
                if config.ignore_patterns:
                    if any(file_path.match(pattern) for pattern in config.ignore_patterns):
                        continue
                
                files.append(str(file_path))
        
        return files
    
    def check_format(self, file_path: str, config: FormatterConfig) -> bool:
        """检查文件格式是否正确"""
        result = self.format_file(file_path, config)
        return result.success and not result.changes_made
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.json'):
                    return json.load(f)
                elif config_file.endswith(('.yml', '.yaml')):
                    return yaml.safe_load(f)
                else:
                    raise ValueError(f"不支持的配置文件格式: {config_file}")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

# 基础格式化器抽象类
class BaseFormatter:
    def format(self, file_path: str, content: str, config: FormatterConfig) -> FormatResult:
        """格式化文件内容"""
        raise NotImplementedError
    
    def check_available(self) -> bool:
        """检查格式化工具是否可用"""
        raise NotImplementedError

class PrettierFormatter(BaseFormatter):
    def __init__(self):
        self.command = "prettier"
    
    def format(self, file_path: str, content: str, config: FormatterConfig) -> FormatResult:
        """使用Prettier格式化"""
        try:
            # 构建命令
            cmd = [self.command]
            
            # 添加配置文件
            if config.config_file:
                cmd.extend(['--config', config.config_file])
            
            # 添加选项
            if config.options:
                for key, value in config.options.items():
                    if isinstance(value, bool) and value:
                        cmd.append(f"--{key}")
                    elif not isinstance(value, bool):
                        cmd.extend([f"--{key}", str(value)])
            
            cmd.append(file_path)
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                formatted_content = result.stdout
                
                return FormatResult(
                    success=True,
                    file_path=file_path,
                    original_content=content,
                    formatted_content=formatted_content,
                    changes_made=content != formatted_content
                )
            else:
                return FormatResult(
                    success=False,
                    file_path=file_path,
                    original_content=content,
                    formatted_content="",
                    changes_made=False,
                    error_message=result.stderr
                )
        
        except Exception as e:
            return FormatResult(
                success=False,
                file_path=file_path,
                original_content=content,
                formatted_content="",
                changes_made=False,
                error_message=str(e)
            )
    
    def check_available(self) -> bool:
        """检查Prettier是否可用"""
        try:
            result = subprocess.run([self.command, '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

class BlackFormatter(BaseFormatter):
    def __init__(self):
        self.command = "black"
    
    def format(self, file_path: str, content: str, config: FormatterConfig) -> FormatResult:
        """使用Black格式化"""
        try:
            # 构建命令
            cmd = [self.command]
            
            # 添加配置文件
            if config.config_file:
                cmd.extend(['--config', config.config_file])
            
            # 添加选项
            if config.options:
                for key, value in config.options.items():
                    if isinstance(value, bool) and value:
                        cmd.append(f"--{key.replace('_', '-')}")
                    elif not isinstance(value, bool):
                        cmd.extend([f"--{key.replace('_', '-')}", str(value)])
            
            cmd.append(file_path)
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                # Black直接修改文件，需要读取格式化后的内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    formatted_content = f.read()
                
                return FormatResult(
                    success=True,
                    file_path=file_path,
                    original_content=content,
                    formatted_content=formatted_content,
                    changes_made=content != formatted_content
                )
            else:
                return FormatResult(
                    success=False,
                    file_path=file_path,
                    original_content=content,
                    formatted_content="",
                    changes_made=False,
                    error_message=result.stderr
                )
        
        except Exception as e:
            return FormatResult(
                success=False,
                file_path=file_path,
                original_content=content,
                formatted_content="",
                changes_made=False,
                error_message=str(e)
            )
    
    def check_available(self) -> bool:
        """检查Black是否可用"""
        try:
            result = subprocess.run([self.command, '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

# 其他格式化器实现类似...
class Autopep8Formatter(BaseFormatter):
    def __init__(self):
        self.command = "autopep8"
    
    def format(self, file_path: str, content: str, config: FormatterConfig) -> FormatResult:
        """使用autopep8格式化"""
        try:
            cmd = [self.command]
            
            if config.options:
                for key, value in config.options.items():
                    if isinstance(value, bool) and value:
                        cmd.append(f"--{key}")
                    elif not isinstance(value, bool):
                        cmd.extend([f"--{key}", str(value)])
            
            cmd.append(file_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                formatted_content = result.stdout
                
                return FormatResult(
                    success=True,
                    file_path=file_path,
                    original_content=content,
                    formatted_content=formatted_content,
                    changes_made=content != formatted_content
                )
            else:
                return FormatResult(
                    success=False,
                    file_path=file_path,
                    original_content=content,
                    formatted_content="",
                    changes_made=False,
                    error_message=result.stderr
                )
        
        except Exception as e:
            return FormatResult(
                success=False,
                file_path=file_path,
                original_content=content,
                formatted_content="",
                changes_made=False,
                error_message=str(e)
            )
    
    def check_available(self) -> bool:
        try:
            result = subprocess.run([self.command, '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

# 使用示例
engine = FormatterEngine()

# JavaScript/TypeScript配置
js_config = FormatterConfig(
    language=Language.JAVASCRIPT,
    formatter_type=FormatterType.PRETTIER,
    config_file=".prettierrc.json",
    options={
        "printWidth": 80,
        "tabWidth": 2,
        "useTabs": False,
        "semi": True,
        "singleQuote": True,
        "trailingComma": "es5"
    },
    file_extensions=[".js", ".jsx", ".ts", ".tsx"],
    ignore_patterns=["*.min.js", "node_modules/**"]
)

# Python配置
python_config = FormatterConfig(
    language=Language.PYTHON,
    formatter_type=FormatterType.BLACK,
    config_file="pyproject.toml",
    options={
        "line_length": 88,
        "target_version": ["py38"]
    },
    file_extensions=[".py"],
    ignore_patterns=["__pycache__/**", "*.pyc"]
)

# 格式化单个文件
result = engine.format_file("example.js", js_config)
print(f"格式化结果: {result.success}")
print(f"是否有变更: {result.changes_made}")

# 格式化目录
results = engine.format_directory("src", js_config)
for result in results:
    if result.changes_made:
        print(f"已格式化: {result.file_path}")
```

## 语言特定格式化器

### JavaScript/TypeScript格式化器
```python
# js_formatter.py
import json
from typing import Dict, Any, Optional
from formatter_engine import BaseFormatter, FormatResult, FormatterConfig

class JavaScriptFormatter:
    def __init__(self):
        self.prettier_config = {
            "printWidth": 80,
            "tabWidth": 2,
            "useTabs": False,
            "semi": True,
            "singleQuote": False,
            "quoteProps": "as-needed",
            "trailingComma": "es5",
            "bracketSpacing": True,
            "bracketSameLine": False,
            "arrowParens": "avoid",
            "endOfLine": "lf"
        }
        
        self.eslint_config = {
            "env": {
                "browser": True,
                "es2021": True,
                "node": True
            },
            "extends": [
                "eslint:recommended",
                "@typescript-eslint/recommended"
            ],
            "parser": "@typescript-eslint/parser",
            "parserOptions": {
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "plugins": ["@typescript-eslint"],
            "rules": {
                "indent": ["error", 2],
                "linebreak-style": ["error", "unix"],
                "quotes": ["error", "double"],
                "semi": ["error", "always"]
            }
        }
    
    def generate_prettier_config(self, output_path: str = ".prettierrc.json"):
        """生成Prettier配置文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.prettier_config, f, indent=2)
    
    def generate_eslint_config(self, output_path: str = ".eslintrc.json"):
        """生成ESLint配置文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.eslint_config, f, indent=2)
    
    def update_prettier_config(self, updates: Dict[str, Any]):
        """更新Prettier配置"""
        self.prettier_config.update(updates)
    
    def update_eslint_config(self, updates: Dict[str, Any]):
        """更新ESLint配置"""
        self.eslint_config.update(updates)
    
    def format_with_prettier(self, file_path: str, config: FormatterConfig) -> FormatResult:
        """使用Prettier格式化"""
        # 这里调用PrettierFormatter
        pass
    
    def format_with_eslint(self, file_path: str, config: FormatterConfig) -> FormatResult:
        """使用ESLint格式化"""
        # 这里调用ESLintFormatter
        pass
    
    def validate_typescript(self, file_path: str) -> Dict[str, Any]:
        """验证TypeScript代码"""
        try:
            import subprocess
            
            cmd = ["npx", "tsc", "--noEmit", "--strict", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "errors": result.stderr if result.returncode != 0 else "",
                "warnings": result.stdout if result.returncode == 0 else ""
            }
        
        except Exception as e:
            return {
                "success": False,
                "errors": str(e),
                "warnings": ""
            }

# 使用示例
js_formatter = JavaScriptFormatter()

# 生成配置文件
js_formatter.generate_prettier_config()
js_formatter.generate_eslint_config()

# 更新配置
js_formatter.update_prettier_config({
    "printWidth": 100,
    "singleQuote": True
})

# 验证TypeScript
validation_result = js_formatter.validate_typescript("example.ts")
print(f"TypeScript验证: {validation_result['success']}")
```

### Python格式化器
```python
# python_formatter.py
import toml
from typing import Dict, Any, Optional
from formatter_engine import BaseFormatter, FormatResult, FormatterConfig

class PythonFormatter:
    def __init__(self):
        self.black_config = {
            "line-length": 88,
            "target-version": ["py38", "py39", "py310"],
            "include": "\\.pyi?$",
            "extend-exclude": """
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
"""
        }
        
        self.isort_config = {
            "profile": "black",
            "multi_line_output": 3,
            "include_trailing_comma": True,
            "force_grid_wrap": 0,
            "use_parentheses": True,
            "ensure_newline_before_comments": True,
            "line_length": 88
        }
        
        self.flake8_config = {
            "max-line-length": 88,
            "extend-ignore": ["E203", "W503"],
            "exclude": [
                ".git",
                "__pycache__",
                "build",
                "dist"
            ]
        }
    
    def generate_black_config(self, output_path: str = "pyproject.toml"):
        """生成Black配置文件"""
        config = {
            "tool": {
                "black": self.black_config
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            toml.dump(config, f)
    
    def generate_isort_config(self, output_path: str = "pyproject.toml"):
        """生成isort配置文件"""
        config = {
            "tool": {
                "isort": self.isort_config
            }
        }
        
        with open(output_path, 'a', encoding='utf-8') as f:
            toml.dump(config, f)
    
    def generate_flake8_config(self, output_path: str = ".flake8"):
        """生成flake8配置文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("[flake8]\n")
            for key, value in self.flake8_config.items():
                if isinstance(value, list):
                    f.write(f"{key} = {', '.join(value)}\n")
                else:
                    f.write(f"{key} = {value}\n")
    
    def format_imports(self, file_path: str) -> FormatResult:
        """格式化导入语句"""
        try:
            import subprocess
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            cmd = ["isort", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    formatted_content = f.read()
                
                return FormatResult(
                    success=True,
                    file_path=file_path,
                    original_content=original_content,
                    formatted_content=formatted_content,
                    changes_made=original_content != formatted_content
                )
            else:
                return FormatResult(
                    success=False,
                    file_path=file_path,
                    original_content=original_content,
                    formatted_content="",
                    changes_made=False,
                    error_message=result.stderr
                )
        
        except Exception as e:
            return FormatResult(
                success=False,
                file_path=file_path,
                original_content="",
                formatted_content="",
                changes_made=False,
                error_message=str(e)
            )
    
    def check_python_code(self, file_path: str) -> Dict[str, Any]:
        """检查Python代码质量"""
        try:
            import subprocess
            
            # 使用flake8检查
            cmd = ["flake8", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                "success": result.returncode == 0,
                "issues": result.stdout if result.returncode != 0 else "",
                "warnings": result.stderr if result.stderr else ""
            }
        
        except Exception as e:
            return {
                "success": False,
                "issues": str(e),
                "warnings": ""
            }
    
    def analyze_complexity(self, file_path: str) -> Dict[str, Any]:
        """分析代码复杂度"""
        try:
            import ast
            import radon.complexity as radon_cc
            import radon.metrics as radon_metrics
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 解析AST
            tree = ast.parse(code)
            
            # 计算复杂度
            cc = radon_cc.cc_visit(tree)
            metrics = radon_metrics.mi_visit(code)
            
            return {
                "cyclomatic_complexity": cc,
                "maintainability_index": metrics,
                "halstead_metrics": radon_metrics.h_visit(code)
            }
        
        except Exception as e:
            return {
                "error": str(e)
            }

# 使用示例
python_formatter = PythonFormatter()

# 生成配置文件
python_formatter.generate_black_config()
python_formatter.generate_isort_config()
python_formatter.generate_flake8_config()

# 格式化导入
import_result = python_formatter.format_imports("example.py")
print(f"导入格式化: {import_result.success}")

# 检查代码质量
quality_check = python_formatter.check_python_code("example.py")
print(f"代码质量检查: {quality_check['success']}")

# 分析复杂度
complexity = python_formatter.analyze_complexity("example.py")
if "error" not in complexity:
    print(f"圈复杂度: {len(complexity['cyclomatic_complexity'])}")
```

## 配置管理

### 配置管理器
```python
# config_manager.py
import json
import yaml
import toml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
import os

@dataclass
class GlobalConfig:
    """全局配置"""
    default_language: str = "javascript"
    backup_files: bool = True
    backup_directory: str = ".format_backup"
    parallel_processing: bool = True
    max_workers: int = 4
    log_level: str = "INFO"
    report_format: str = "json"

@dataclass
class LanguageConfig:
    """语言特定配置"""
    language: str
    formatter: str
    config_file: Optional[str] = None
    options: Dict[str, Any] = None
    file_extensions: List[str] = None
    ignore_patterns: List[str] = None
    pre_commands: List[str] = None
    post_commands: List[str] = None

class ConfigManager:
    def __init__(self, config_dir: str = ".format_config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.global_config_file = self.config_dir / "global.json"
        self.languages_config_file = self.config_dir / "languages.json"
        
        self.global_config = self._load_global_config()
        self.language_configs = self._load_language_configs()
    
    def _load_global_config(self) -> GlobalConfig:
        """加载全局配置"""
        if self.global_config_file.exists():
            try:
                with open(self.global_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return GlobalConfig(**data)
            except Exception as e:
                print(f"加载全局配置失败: {e}")
        
        return GlobalConfig()
    
    def _load_language_configs(self) -> Dict[str, LanguageConfig]:
        """加载语言配置"""
        if self.languages_config_file.exists():
            try:
                with open(self.languages_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                configs = {}
                for lang_name, lang_data in data.items():
                    configs[lang_name] = LanguageConfig(**lang_data)
                
                return configs
            except Exception as e:
                print(f"加载语言配置失败: {e}")
        
        return self._get_default_language_configs()
    
    def _get_default_language_configs(self) -> Dict[str, LanguageConfig]:
        """获取默认语言配置"""
        return {
            "javascript": LanguageConfig(
                language="javascript",
                formatter="prettier",
                config_file=".prettierrc.json",
                options={
                    "printWidth": 80,
                    "tabWidth": 2,
                    "useTabs": False,
                    "semi": True,
                    "singleQuote": False
                },
                file_extensions=[".js", ".jsx"],
                ignore_patterns=["*.min.js", "node_modules/**"]
            ),
            "typescript": LanguageConfig(
                language="typescript",
                formatter="prettier",
                config_file=".prettierrc.json",
                options={
                    "printWidth": 80,
                    "tabWidth": 2,
                    "useTabs": False,
                    "semi": True,
                    "singleQuote": False
                },
                file_extensions=[".ts", ".tsx"],
                ignore_patterns=["*.d.ts", "node_modules/**"]
            ),
            "python": LanguageConfig(
                language="python",
                formatter="black",
                config_file="pyproject.toml",
                options={
                    "line_length": 88,
                    "target_version": ["py38"]
                },
                file_extensions=[".py"],
                ignore_patterns=["__pycache__/**", "*.pyc"]
            ),
            "java": LanguageConfig(
                language="java",
                formatter="google_java_format",
                config_file=None,
                options={
                    "aosp": False,
                    "skip_javadoc_formatting": False
                },
                file_extensions=[".java"],
                ignore_patterns=["target/**", "build/**"]
            ),
            "csharp": LanguageConfig(
                language="csharp",
                formatter="dotnet_format",
                config_file=".editorconfig",
                options={
                    "indent_size": 4,
                    "indent_style": "space"
                },
                file_extensions=[".cs"],
                ignore_patterns=["bin/**", "obj/**"]
            ),
            "go": LanguageConfig(
                language="go",
                formatter="gofmt",
                config_file=None,
                options={},
                file_extensions=[".go"],
                ignore_patterns=["vendor/**"]
            ),
            "rust": LanguageConfig(
                language="rust",
                formatter="rustfmt",
                config_file="rustfmt.toml",
                options={
                    "edition": "2021",
                    "use_small_heuristics": "Default"
                },
                file_extensions=[".rs"],
                ignore_patterns=["target/**"]
            )
        }
    
    def save_global_config(self):
        """保存全局配置"""
        try:
            with open(self.global_config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.global_config), f, indent=2)
        except Exception as e:
            print(f"保存全局配置失败: {e}")
    
    def save_language_configs(self):
        """保存语言配置"""
        try:
            data = {}
            for lang_name, config in self.language_configs.items():
                data[lang_name] = asdict(config)
            
            with open(self.languages_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"保存语言配置失败: {e}")
    
    def get_language_config(self, language: str) -> Optional[LanguageConfig]:
        """获取语言配置"""
        return self.language_configs.get(language)
    
    def set_language_config(self, language: str, config: LanguageConfig):
        """设置语言配置"""
        self.language_configs[language] = config
    
    def update_global_config(self, **kwargs):
        """更新全局配置"""
        for key, value in kwargs.items():
            if hasattr(self.global_config, key):
                setattr(self.global_config, key, value)
    
    def generate_formatter_configs(self, output_dir: str = "."):
        """生成格式化器配置文件"""
        output_path = Path(output_dir)
        
        for lang_name, config in self.language_configs.items():
            if config.config_file:
                config_path = output_path / config.config_file
                
                if config.formatter == "prettier":
                    self._generate_prettier_config(config, config_path)
                elif config.formatter == "black":
                    self._generate_black_config(config, config_path)
                elif config.formatter == "eslint":
                    self._generate_eslint_config(config, config_path)
                # 其他格式化器配置...
    
    def _generate_prettier_config(self, config: LanguageConfig, config_path: Path):
        """生成Prettier配置"""
        prettier_config = config.options or {}
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(prettier_config, f, indent=2)
    
    def _generate_black_config(self, config: LanguageConfig, config_path: Path):
        """生成Black配置"""
        black_config = {
            "tool": {
                "black": config.options or {}
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            toml.dump(black_config, f)
    
    def _generate_eslint_config(self, config: LanguageConfig, config_path: Path):
        """生成ESLint配置"""
        eslint_config = {
            "env": {
                "browser": True,
                "es2021": True
            },
            "extends": ["eslint:recommended"],
            "parserOptions": {
                "ecmaVersion": 12,
                "sourceType": "module"
            },
            "rules": {}
        }
        
        # 将选项转换为ESLint规则
        if config.options:
            rules = {}
            for key, value in config.options.items():
                if key == "semi":
                    rules["semi"] = ["error", "always" if value else "never"]
                elif key == "singleQuote":
                    rules["quotes"] = ["error", "single" if value else "double"]
                elif key == "tabWidth":
                    rules["indent"] = ["error", value]
            
            eslint_config["rules"] = rules
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(eslint_config, f, indent=2)
    
    def detect_language_from_file(self, file_path: str) -> Optional[str]:
        """从文件路径检测语言"""
        file_ext = Path(file_path).suffix.lower()
        
        for lang_name, config in self.language_configs.items():
            if file_ext in config.file_extensions:
                return lang_name
        
        return None
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        issues = []
        
        # 验证全局配置
        if self.global_config.max_workers < 1:
            issues.append("max_workers必须大于0")
        
        if self.global_config.log_level not in ["DEBUG", "INFO", "WARN", "ERROR"]:
            issues.append("无效的log_level")
        
        # 验证语言配置
        for lang_name, config in self.language_configs.items():
            if not config.file_extensions:
                issues.append(f"{lang_name}: 缺少文件扩展名配置")
            
            if not config.formatter:
                issues.append(f"{lang_name}: 缺少格式化器配置")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

# 使用示例
config_manager = ConfigManager()

# 获取语言配置
js_config = config_manager.get_language_config("javascript")
print(f"JavaScript格式化器: {js_config.formatter}")

# 更新全局配置
config_manager.update_global_config(
    max_workers=8,
    backup_files=True
)

# 添加新语言配置
new_config = LanguageConfig(
    language="php",
    formatter="php_cs_fixer",
    config_file=".php_cs",
    options={
        "using_cache": True,
        "rules": {
            "@PSR12": True
        }
    },
    file_extensions=[".php"],
    ignore_patterns=["vendor/**"]
)
config_manager.set_language_config("php", new_config)

# 生成配置文件
config_manager.generate_formatter_configs()

# 验证配置
validation = config_manager.validate_config()
print(f"配置验证: {validation['valid']}")
if not validation['valid']:
    for issue in validation['issues']:
        print(f"问题: {issue}")
```

## 批量处理和自动化

### 批量格式化器
```python
# batch_formatter.py
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import json

from formatter_engine import FormatterEngine, FormatResult, FormatterConfig
from config_manager import ConfigManager

@dataclass
class BatchResult:
    total_files: int
    successful_files: int
    failed_files: int
    changed_files: int
    skipped_files: int
    processing_time: float
    results: List[FormatResult]
    errors: List[str]

class BatchFormatter:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.formatter_engine = FormatterEngine()
        self.progress_callback = None
        self.error_callback = None
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """设置进度回调"""
        self.progress_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """设置错误回调"""
        self.error_callback = callback
    
    def format_project(self, project_path: str, languages: List[str] = None,
                      recursive: bool = True, parallel: bool = True) -> BatchResult:
        """格式化整个项目"""
        start_time = time.time()
        
        # 获取所有需要格式化的文件
        files_to_format = self._get_project_files(project_path, languages, recursive)
        
        if not files_to_format:
            return BatchResult(
                total_files=0,
                successful_files=0,
                failed_files=0,
                changed_files=0,
                skipped_files=0,
                processing_time=0,
                results=[],
                errors=[]
            )
        
        # 批量格式化
        if parallel:
            results = self._format_files_parallel(files_to_format)
        else:
            results = self._format_files_sequential(files_to_format)
        
        # 统计结果
        successful_files = sum(1 for r in results if r.success)
        failed_files = sum(1 for r in results if not r.success)
        changed_files = sum(1 for r in results if r.changes_made)
        skipped_files = sum(1 for r in results if not r.success and "跳过" in str(r.error_message))
        
        processing_time = time.time() - start_time
        
        return BatchResult(
            total_files=len(files_to_format),
            successful_files=successful_files,
            failed_files=failed_files,
            changed_files=changed_files,
            skipped_files=skipped_files,
            processing_time=processing_time,
            results=results,
            errors=[r.error_message for r in results if r.error_message]
        )
    
    def _get_project_files(self, project_path: str, languages: List[str],
                          recursive: bool) -> List[Dict[str, Any]]:
        """获取项目中需要格式化的文件"""
        files = []
        project_dir = Path(project_path)
        
        # 确定要处理的语言
        if not languages:
            languages = list(self.config_manager.language_configs.keys())
        
        for language in languages:
            config = self.config_manager.get_language_config(language)
            if not config:
                continue
            
            # 查找文件
            pattern = "**/*" if recursive else "*"
            for file_path in project_dir.glob(pattern):
                if file_path.is_file():
                    # 检查文件扩展名
                    if file_path.suffix in config.file_extensions:
                        # 检查忽略模式
                        should_ignore = False
                        for ignore_pattern in config.ignore_patterns:
                            if file_path.match(ignore_pattern):
                                should_ignore = True
                                break
                        
                        if not should_ignore:
                            files.append({
                                "path": str(file_path),
                                "language": language,
                                "config": config
                            })
        
        return files
    
    def _format_files_parallel(self, files: List[Dict[str, Any]]) -> List[FormatResult]:
        """并行格式化文件"""
        results = []
        max_workers = self.config_manager.global_config.max_workers
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_file = {
                executor.submit(self._format_single_file, file_info): file_info
                for file_info in files
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if self.error_callback and result.error_message:
                        self.error_callback(f"{file_info['path']}: {result.error_message}")
                
                except Exception as e:
                    error_result = FormatResult(
                        success=False,
                        file_path=file_info['path'],
                        original_content="",
                        formatted_content="",
                        changes_made=False,
                        error_message=str(e)
                    )
                    results.append(error_result)
                    
                    if self.error_callback:
                        self.error_callback(f"{file_info['path']}: {e}")
                
                completed += 1
                if self.progress_callback:
                    self.progress_callback(completed, len(files))
        
        return results
    
    def _format_files_sequential(self, files: List[Dict[str, Any]]) -> List[FormatResult]:
        """顺序格式化文件"""
        results = []
        
        for i, file_info in enumerate(files):
            result = self._format_single_file(file_info)
            results.append(result)
            
            if self.error_callback and result.error_message:
                self.error_callback(f"{file_info['path']}: {result.error_message}")
            
            if self.progress_callback:
                self.progress_callback(i + 1, len(files))
        
        return results
    
    def _format_single_file(self, file_info: Dict[str, Any]) -> FormatResult:
        """格式化单个文件"""
        file_path = file_info['path']
        language = file_info['language']
        config = file_info['config']
        
        # 创建FormatterConfig
        formatter_config = FormatterConfig(
            language=language,
            formatter_type=config.formatter,
            config_file=config.config_file,
            options=config.options,
            file_extensions=config.file_extensions,
            ignore_patterns=config.ignore_patterns
        )
        
        # 执行前置命令
        if config.pre_commands:
            for command in config.pre_commands:
                try:
                    os.system(command)
                except Exception as e:
                    pass
        
        # 格式化文件
        result = self.formatter_engine.format_file(file_path, formatter_config)
        
        # 执行后置命令
        if config.post_commands and result.success:
            for command in config.post_commands:
                try:
                    os.system(command)
                except Exception as e:
                    pass
        
        return result
    
    def format_with_backup(self, file_path: str, config: FormatterConfig) -> FormatResult:
        """带备份的格式化"""
        # 创建备份
        if self.config_manager.global_config.backup_files:
            backup_dir = Path(self.config_manager.global_config.backup_directory)
            backup_dir.mkdir(exist_ok=True)
            
            backup_path = backup_dir / f"{Path(file_path).name}.bak"
            
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                pass
        
        # 格式化文件
        result = self.formatter_engine.format_file(file_path, config)
        
        return result
    
    def generate_report(self, batch_result: BatchResult, output_path: str = "format_report.json"):
        """生成格式化报告"""
        report = {
            "summary": {
                "total_files": batch_result.total_files,
                "successful_files": batch_result.successful_files,
                "failed_files": batch_result.failed_files,
                "changed_files": batch_result.changed_files,
                "skipped_files": batch_result.skipped_files,
                "processing_time": batch_result.processing_time,
                "success_rate": batch_result.successful_files / batch_result.total_files if batch_result.total_files > 0 else 0
            },
            "files": []
        }
        
        for result in batch_result.results:
            file_info = {
                "path": result.file_path,
                "success": result.success,
                "changed": result.changes_made,
                "error": result.error_message
            }
            report["files"].append(file_info)
        
        if batch_result.errors:
            report["errors"] = batch_result.errors
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

# 使用示例
config_manager = ConfigManager()
batch_formatter = BatchFormatter(config_manager)

# 设置回调函数
def progress_callback(completed, total):
    print(f"进度: {completed}/{total} ({completed/total*100:.1f}%)")

def error_callback(error):
    print(f"错误: {error}")

batch_formatter.set_progress_callback(progress_callback)
batch_formatter.set_error_callback(error_callback)

# 格式化项目
result = batch_formatter.format_project(
    project_path="./src",
    languages=["javascript", "python"],
    recursive=True,
    parallel=True
)

print(f"格式化完成:")
print(f"总文件数: {result.total_files}")
print(f"成功: {result.successful_files}")
print(f"失败: {result.failed_files}")
print(f"已更改: {result.changed_files}")
print(f"处理时间: {result.processing_time:.2f}秒")

# 生成报告
batch_formatter.generate_report(result)
```

## 参考资源

### 格式化工具
- [Prettier](https://prettier.io/)
- [Black](https://black.readthedocs.io/)
- [ESLint](https://eslint.org/)
- [autopep8](https://pypi.org/project/autopep8/)
- [YAPF](https://github.com/google/yapf)

### 代码质量工具
- [Flake8](https://flake8.pycqa.org/)
- [isort](https://isort.readthedocs.io/)
- [clang-format](https://clang.llvm.org/docs/ClangFormat.html)
- [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format)

### 配置标准
- [EditorConfig](https://editorconfig.org/)
- [PEP 8](https://pep8.org/)
- [Google Style Guides](https://google.github.io/styleguide/)
- [Airbnb Style Guide](https://airbnb.io/javascript/)

### IDE集成
- [VS Code Extensions](https://marketplace.visualstudio.com/)
- [IntelliJ IDEA Plugins](https://plugins.jetbrains.com/)
- [Vim Plugins](https://vim.org/)
- [Emacs Packages](https://www.gnu.org/software/emacs/)
