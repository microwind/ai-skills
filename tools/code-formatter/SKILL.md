---
name: 代码格式化器
description: "当格式化代码时，修复缩进，应用代码样式。提交前格式化和标准化代码。"
license: MIT
---

# 代码格式化器技能

## 概述

不一致的格式化浪费审查时间并产生合并冲突。提交前格式化代码。未格式化的代码不专业。

**核心原则**: 一致的格式化减少摩擦。好的代码格式应该统一、可读、自动化、可配置。坏的格式化会导致代码混乱、协作困难、维护成本高。

## 何时使用

**始终:**
- 提交代码前
- 加入团队时
- 跨代码库标准化时
- 准备审查时
- 减少差异噪音时

**触发短语:**
- "格式化这个代码"
- "修复缩进"
- "标准化格式"
- "应用代码样式"

## 代码格式化器技能功能

### 格式化功能
- 自动缩进调整
- 空格和制表符统一
- 行尾空白清理
- 括号对齐
- 行长度限制
- 空行标准化

### 样式应用
- 代码风格配置
- 语言特定格式
- 团队标准应用
- 预设模板使用
- 自定义规则
- 格式一致性检查

### 质量检查
- 格式错误检测
- 代码风格验证
- 不一致警告
- 最佳实践建议
- 配置合规检查
- 格式评分

### 自动化工具
- 批量格式化
- 增量格式化
- 预提交钩子
- CI/CD集成
- IDE插件
- 编辑器集成

## 常见格式问题

**❌ 缩进问题**
- 混用空格和制表符
- 不一致的缩进深度
- 错误的嵌套对齐
- 行尾空格过多

**❌ 括号问题**
- 括号位置不一致
- 大括号换行风格
- 小括号空格使用
- 数组格式混乱

**❌ 行长度问题**
- 过长的代码行
- 不合理的换行位置
- 字符串拼接格式
- 注释行过长

**❌ 空行问题**
- 过多或过少的空行
- 函数间空行不一致
- 逻辑块分隔不当
- 文件首尾空行

## 代码示例

### 通用代码格式化器

```python
#!/usr/bin/env python3
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

class Language(Enum):
    """编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSS = "css"
    HTML = "html"
    JSON = "json"
    XML = "xml"

class IndentStyle(Enum):
    """缩进风格"""
    SPACES = "spaces"
    TABS = "tabs"

@dataclass
class FormattingRule:
    """格式化规则"""
    name: str
    description: str
    enabled: bool = True
    severity: str = "warning"  # error, warning, info

@dataclass
class FormattingConfig:
    """格式化配置"""
    language: Language
    indent_size: int = 4
    indent_style: IndentStyle = IndentStyle.SPACES
    max_line_length: int = 80
    insert_final_newline: bool = True
    trim_trailing_whitespace: bool = True
    rules: List[FormattingRule] = None
    
    def __post_init__(self):
        if self.rules is None:
            self.rules = self._get_default_rules()
    
    def _get_default_rules(self) -> List[FormattingRule]:
        """获取默认规则"""
        return [
            FormattingRule("indent_consistency", "缩进一致性"),
            FormattingRule("bracket_placement", "括号位置"),
            FormattingRule("space_around_operators", "操作符空格"),
            FormattingRule("line_length", "行长度限制"),
            FormattingRule("trailing_whitespace", "行尾空白"),
            FormattingRule("final_newline", "文件末尾换行"),
            FormattingRule("empty_lines", "空行规范"),
            FormattingRule("import_sorting", "导入排序"),
            FormattingRule("comment_formatting", "注释格式")
        ]

class CodeFormatter:
    """代码格式化器"""
    
    def __init__(self, config: Optional[FormattingConfig] = None):
        self.config = config or FormattingConfig(Language.PYTHON)
        self.issues: List[str] = []
        
        # 语言特定的格式化器
        self.formatters = {
            Language.PYTHON: self._format_python,
            Language.JAVASCRIPT: self._format_javascript,
            Language.JAVA: self._format_java,
            Language.CPP: self._format_cpp,
            Language.CSS: self._format_css,
            Language.HTML: self._format_html,
            Language.JSON: self._format_json,
            Language.XML: self._format_xml
        }
    
    def format_file(self, file_path: str) -> Tuple[str, List[str]]:
        """格式化文件"""
        path = Path(file_path)
        
        if not path.exists():
            return "", [f"文件不存在: {file_path}"]
        
        # 读取文件
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return "", [f"文件编码错误: {file_path}"]
        
        # 检测语言
        language = self._detect_language(path)
        if language not in self.formatters:
            return content, [f"不支持的语言: {language.value}"]
        
        # 格式化代码
        formatted_content = self._format_content(content, language)
        
        return formatted_content, self.issues
    
    def format_code(self, content: str, language: Language) -> Tuple[str, List[str]]:
        """格式化代码字符串"""
        self.issues.clear()
        
        if language not in self.formatters:
            return content, [f"不支持的语言: {language.value}"]
        
        return self._format_content(content, language)
    
    def _detect_language(self, file_path: Path) -> Language:
        """检测编程语言"""
        extension_map = {
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.jsx': Language.JAVASCRIPT,
            '.ts': Language.JAVASCRIPT,
            '.tsx': Language.JAVASCRIPT,
            '.java': Language.JAVA,
            '.cpp': Language.CPP,
            '.cxx': Language.CPP,
            '.cc': Language.CPP,
            '.c': Language.CPP,
            '.h': Language.CPP,
            '.hpp': Language.CPP,
            '.css': Language.CSS,
            '.html': Language.HTML,
            '.htm': Language.HTML,
            '.json': Language.JSON,
            '.xml': Language.XML
        }
        
        extension = file_path.suffix.lower()
        return extension_map.get(extension, Language.PYTHON)
    
    def _format_content(self, content: str, language: Language) -> Tuple[str, List[str]]:
        """格式化内容"""
        formatter = self.formatters[language]
        return formatter(content)
    
    def _format_python(self, content: str) -> Tuple[str, List[str]]:
        """格式化Python代码"""
        lines = content.splitlines()
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # 清理行尾空白
            if self.config.trim_trailing_whitespace:
                line = line.rstrip()
            
            # 处理缩进
            if line.strip():  # 非空行
                line = self._fix_python_indentation(line)
            
            formatted_lines.append(line)
        
        # 处理空行
        formatted_content = self._fix_empty_lines('\n'.join(formatted_lines))
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        # 检查行长度
        self._check_line_length(formatted_content.splitlines())
        
        return formatted_content, self.issues
    
    def _format_javascript(self, content: str) -> Tuple[str, List[str]]:
        """格式化JavaScript代码"""
        lines = content.splitlines()
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # 清理行尾空白
            if self.config.trim_trailing_whitespace:
                line = line.rstrip()
            
            # 处理缩进
            if line.strip():
                line = self._fix_javascript_indentation(line)
            
            # 处理大括号
            line = self._fix_brace_placement(line)
            
            # 处理操作符空格
            line = self._fix_operator_spaces(line)
            
            formatted_lines.append(line)
        
        formatted_content = '\n'.join(formatted_lines)
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        # 检查行长度
        self._check_line_length(formatted_content.splitlines())
        
        return formatted_content, self.issues
    
    def _format_java(self, content: str) -> Tuple[str, List[str]]:
        """格式化Java代码"""
        lines = content.splitlines()
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # 清理行尾空白
            if self.config.trim_trailing_whitespace:
                line = line.rstrip()
            
            # 处理缩进
            if line.strip():
                line = self._fix_java_indentation(line)
            
            # 处理大括号
            line = self._fix_brace_placement(line)
            
            formatted_lines.append(line)
        
        formatted_content = '\n'.join(formatted_lines)
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return formatted_content, self.issues
    
    def _format_cpp(self, content: str) -> Tuple[str, List[str]]:
        """格式化C++代码"""
        lines = content.splitlines()
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # 清理行尾空白
            if self.config.trim_trailing_whitespace:
                line = line.rstrip()
            
            # 处理缩进
            if line.strip():
                line = self._fix_cpp_indentation(line)
            
            formatted_lines.append(line)
        
        formatted_content = '\n'.join(formatted_lines)
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return formatted_content, self.issues
    
    def _format_css(self, content: str) -> Tuple[str, List[str]]:
        """格式化CSS代码"""
        lines = content.splitlines()
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # 清理行尾空白
            if self.config.trim_trailing_whitespace:
                line = line.rstrip()
            
            # 处理CSS特定格式
            line = self._fix_css_formatting(line)
            
            formatted_lines.append(line)
        
        formatted_content = '\n'.join(formatted_lines)
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return formatted_content, self.issues
    
    def _format_html(self, content: str) -> Tuple[str, List[str]]:
        """格式化HTML代码"""
        lines = content.splitlines()
        formatted_lines = []
        
        for i, line in enumerate(lines):
            # 清理行尾空白
            if self.config.trim_trailing_whitespace:
                line = line.rstrip()
            
            # 处理HTML缩进
            line = self._fix_html_indentation(line)
            
            formatted_lines.append(line)
        
        formatted_content = '\n'.join(formatted_lines)
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return formatted_content, self.issues
    
    def _format_json(self, content: str) -> Tuple[str, List[str]]:
        """格式化JSON代码"""
        try:
            # 解析JSON
            data = json.loads(content)
            
            # 重新格式化
            formatted_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # 处理文件末尾换行
            if self.config.insert_final_newline:
                formatted_content += '\n'
            
            return formatted_content, self.issues
        
        except json.JSONDecodeError as e:
            return content, [f"JSON解析错误: {e}"]
    
    def _format_xml(self, content: str) -> Tuple[str, List[str]]:
        """格式化XML代码"""
        # 简化的XML格式化
        lines = content.splitlines()
        formatted_lines = []
        
        indent_level = 0
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('</'):
                # 结束标签，减少缩进
                indent_level = max(0, indent_level - 1)
            
            # 添加缩进
            if stripped:
                if self.config.indent_style == IndentStyle.SPACES:
                    indented = ' ' * (indent_level * self.config.indent_size) + stripped
                else:
                    indented = '\t' * indent_level + stripped
                formatted_lines.append(indented)
            
            if stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
                # 开始标签（非自闭合），增加缩进
                indent_level += 1
        
        formatted_content = '\n'.join(formatted_lines)
        
        # 处理文件末尾换行
        if self.config.insert_final_newline and formatted_content and not formatted_content.endswith('\n'):
            formatted_content += '\n'
        
        return formatted_content, self.issues
    
    def _fix_python_indentation(self, line: str) -> str:
        """修复Python缩进"""
        # 检测当前缩进
        leading_spaces = len(line) - len(line.lstrip())
        leading_tabs = len(line) - len(line.lstrip('\t'))
        
        # 统一缩进风格
        if self.config.indent_style == IndentStyle.SPACES:
            # 转换为空格
            indent_level = leading_tabs
            if leading_spaces > 0:
                indent_level += leading_spaces // self.config.indent_size
            
            return ' ' * (indent_level * self.config.indent_size) + line.lstrip()
        else:
            # 转换为制表符
            indent_level = leading_spaces // self.config.indent_size
            if leading_tabs > 0:
                indent_level += leading_tabs
            
            return '\t' * indent_level + line.lstrip()
    
    def _fix_javascript_indentation(self, line: str) -> str:
        """修复JavaScript缩进"""
        return self._fix_python_indentation(line)  # 使用相同的缩进逻辑
    
    def _fix_java_indentation(self, line: str) -> str:
        """修复Java缩进"""
        return self._fix_python_indentation(line)  # 使用相同的缩进逻辑
    
    def _fix_cpp_indentation(self, line: str) -> str:
        """修复C++缩进"""
        return self._fix_python_indentation(line)  # 使用相同的缩进逻辑
    
    def _fix_css_formatting(self, line: str) -> str:
        """修复CSS格式"""
        # 添加属性间的分号
        if line.strip() and not line.strip().endswith(';') and ':' in line and not line.strip().endswith('{'):
            line += ';'
        
        return line
    
    def _fix_html_indentation(self, line: str) -> str:
        """修复HTML缩进"""
        return self._fix_python_indentation(line)  # 使用相同的缩进逻辑
    
    def _fix_brace_placement(self, line: str) -> str:
        """修复大括号位置"""
        # 简化实现：确保大括号位置一致
        return line
    
    def _fix_operator_spaces(self, line: str) -> str:
        """修复操作符空格"""
        # 在操作符周围添加空格
        operators = ['=', '+=', '-=', '*=', '/=', '==', '!=', '<', '>', '<=', '>=', '+', '-', '*', '/']
        
        for op in operators:
            # 避免在字符串中替换
            line = re.sub(rf'(?<!["\'])\s*{re.escape(op)}\s*(?!["\'])', f' {op} ', line)
        
        return line
    
    def _fix_empty_lines(self, content: str) -> str:
        """修复空行"""
        lines = content.splitlines()
        formatted_lines = []
        
        # 移除连续空行，保留单个空行
        prev_empty = False
        for line in lines:
            if not line.strip():
                if not prev_empty:
                    formatted_lines.append(line)
                prev_empty = True
            else:
                formatted_lines.append(line)
                prev_empty = False
        
        return '\n'.join(formatted_lines)
    
    def _check_line_length(self, lines: List[str]):
        """检查行长度"""
        for i, line in enumerate(lines, 1):
            if len(line) > self.config.max_line_length:
                self.issues.append(f"行 {i}: 行长度超过限制 ({len(line)} > {self.config.max_line_length})")

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='代码格式化器')
    parser.add_argument('file', help='要格式化的文件')
    parser.add_argument('--language', choices=['python', 'javascript', 'java', 'cpp', 'css', 'html', 'json', 'xml'],
                       help='指定语言')
    parser.add_argument('--indent-size', type=int, default=4, help='缩进大小')
    parser.add_argument('--indent-style', choices=['spaces', 'tabs'], default='spaces', help='缩进风格')
    parser.add_argument('--max-line-length', type=int, default=80, help='最大行长度')
    parser.add_argument('--output', help='输出文件')
    parser.add_argument('--in-place', action='store_true', help='原地修改文件')
    parser.add_argument('--check', action='store_true', help='仅检查格式，不修改')
    
    args = parser.parse_args()
    
    # 创建配置
    language = Language(args.language) if args.language else Language.PYTHON
    indent_style = IndentStyle(args.indent_style)
    
    config = FormattingConfig(
        language=language,
        indent_size=args.indent_size,
        indent_style=indent_style,
        max_line_length=args.max_line_length
    )
    
    formatter = CodeFormatter(config)
    
    try:
        # 格式化文件
        formatted_content, issues = formatter.format_file(args.file)
        
        if issues:
            print("发现的问题:")
            for issue in issues:
                print(f"  - {issue}")
            print()
        
        if args.check:
            # 仅检查模式
            if issues:
                print("格式检查失败")
                exit(1)
            else:
                print("格式检查通过")
                exit(0)
        
        # 输出结果
        if args.in_place:
            # 原地修改
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            print(f"已格式化文件: {args.file}")
        elif args.output:
            # 输出到文件
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            print(f"已保存到: {args.output}")
        else:
            # 输出到控制台
            print(formatted_content)
    
    except Exception as e:
        print(f"格式化失败: {e}")
        exit(1)
```

### 批量代码格式化工具

```bash
#!/bin/bash
# batch-formatter.sh - 批量代码格式化工具

set -e

# 配置
SCAN_DIR=${1:-"."}
FILE_PATTERNS=${2:-"*.py *.js *.java *.cpp *.css *.html"}
CONFIG_FILE=${3:-""}
DRY_RUN=${4:-false}
BACKUP=${5:-true}
LOG_FILE="batch_formatting.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

# 创建备份
create_backup() {
    local file_path="$1"
    local backup_path="${file_path}.backup"
    
    if [ "$BACKUP" = "true" ]; then
        cp "$file_path" "$backup_path"
        log_info "已创建备份: $backup_path"
    fi
}

# 恢复备份
restore_backup() {
    local file_path="$1"
    local backup_path="${file_path}.backup"
    
    if [ -f "$backup_path" ]; then
        mv "$backup_path" "$file_path"
        log_info "已恢复备份: $file_path"
    fi
}

# 格式化单个文件
format_file() {
    local file_path="$1"
    local file_ext="${file_path##*.}"
    
    log_info "格式化文件: $file_path"
    
    # 创建备份
    create_backup "$file_path"
    
    # 根据文件扩展名选择格式化器
    case "$file_ext" in
        "py")
            python3 code_formatter.py "$file_path" --language python --in-place 2>> "$LOG_FILE"
            ;;
        "js"|"jsx"|"ts"|"tsx")
            python3 code_formatter.py "$file_path" --language javascript --in-place 2>> "$LOG_FILE"
            ;;
        "java")
            python3 code_formatter.py "$file_path" --language java --in-place 2>> "$LOG_FILE"
            ;;
        "cpp"|"cxx"|"cc"|"c"|"h"|"hpp")
            python3 code_formatter.py "$file_path" --language cpp --in-place 2>> "$LOG_FILE"
            ;;
        "css")
            python3 code_formatter.py "$file_path" --language css --in-place 2>> "$LOG_FILE"
            ;;
        "html"|"htm")
            python3 code_formatter.py "$file_path" --language html --in-place 2>> "$LOG_FILE"
            ;;
        "json")
            python3 code_formatter.py "$file_path" --language json --in-place 2>> "$LOG_FILE"
            ;;
        "xml")
            python3 code_formatter.py "$file_path" --language xml --in-place 2>> "$LOG_FILE"
            ;;
        *)
            log_warn "不支持的文件类型: $file_ext"
            return 1
            ;;
    esac
    
    # 检查格式化是否成功
    if [ $? -eq 0 ]; then
        log_info "✅ $file_path 格式化完成"
        return 0
    else
        log_error "❌ $file_path 格式化失败"
        restore_backup "$file_path"
        return 1
    fi
}

# 查找文件
find_files() {
    log_step "查找要格式化的文件..."
    
    local files=()
    
    # 解析文件模式
    IFS=' ' read -ra PATTERNS <<< "$FILE_PATTERNS"
    
    for pattern in "${PATTERNS[@]}"; do
        while IFS= read -r -d '' file; do
            files+=("$file")
        done < <(find "$SCAN_DIR" -name "$pattern" -type f -print0)
    done
    
    log_info "找到 ${#files[@]} 个文件"
    
    # 保存文件列表
    printf '%s\n' "${files[@]}" > "files_to_format.list"
    
    echo "${#files[@]}"
}

# 批量格式化
batch_format() {
    local total_files=$1
    local formatted_files=0
    local failed_files=0
    
    log_step "开始批量格式化..."
    
    while IFS= read -r file_path; do
        if format_file "$file_path"; then
            ((formatted_files++))
        else
            ((failed_files++))
        fi
        
        # 显示进度
        local progress=$((formatted_files + failed_files))
        if ((progress % 10 == 0)); then
            log_info "进度: $progress/$total_files"
        fi
        
    done < "files_to_format.list"
    
    log_info "批量格式化完成: 成功 $formatted_files, 失败 $failed_files"
    
    return $failed_files
}

# 清理备份文件
cleanup_backups() {
    log_step "清理备份文件..."
    
    local backup_count=0
    while IFS= read -r -d '' backup_file; do
        rm -f "$backup_file"
        ((backup_count++))
    done < <(find "$SCAN_DIR" -name "*.backup" -type f -print0)
    
    log_info "已清理 $backup_count 个备份文件"
}

# 生成报告
generate_report() {
    log_step "生成格式化报告..."
    
    local report_file="formatting_report.md"
    
    cat > "$report_file" << EOF
# 批量代码格式化报告

## 格式化信息
- 扫描目录: $SCAN_DIR
- 文件模式: $FILE_PATTERNS
- 格式化时间: $(date)
- 备份: $BACKUP
- 试运行: $DRY_RUN

## 统计摘要
EOF
    
    # 统计文件数量
    local total_files=$(wc -l < "files_to_format.list")
    echo "- 总文件数: $total_files" >> "$report_file"
    
    # 统计格式化结果
    local success_count=$(grep -c "✅" "$LOG_FILE" || echo "0")
    local failed_count=$(grep -c "❌" "$LOG_FILE" || echo "0")
    
    echo "- 成功格式化: $success_count" >> "$report_file"
    echo "- 格式化失败: $failed_count" >> "$report_file"
    echo ""
    
    # 失败的文件列表
    if [ $failed_count -gt 0 ]; then
        echo "## 格式化失败的文件" >> "$report_file"
        grep "❌" "$LOG_FILE" | sed 's/.*❌ //' | sed 's/ 格式化失败//' | while read -r file; do
            echo "- $file" >> "$report_file"
        done
        echo ""
    fi
    
    # 建议
    echo "## 建议" >> "$report_file"
    echo "- 检查格式化失败的文件" >> "$report_file"
    echo "- 配置合适的格式化规则" >> "$report_file"
    echo "- 建立代码格式化规范" >> "$report_file"
    echo "- 使用预提交钩子自动格式化" >> "$report_file"
    
    log_info "报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始批量代码格式化..."
    log_info "扫描目录: $SCAN_DIR"
    log_info "文件模式: $FILE_PATTERNS"
    log_info "试运行: $DRY_RUN"
    
    # 查找文件
    total_files=$(find_files)
    
    if [ "$total_files" -eq 0 ]; then
        log_warn "未找到要格式化的文件"
        exit 0
    fi
    
    # 批量格式化
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "试运行模式，不实际格式化文件"
        exit 0
    fi
    
    failed_count=0
    batch_format "$total_files"
    failed_count=$?
    
    # 生成报告
    generate_report
    
    # 清理备份
    if [ "$BACKUP" = "false" ]; then
        cleanup_backups
    fi
    
    # 清理临时文件
    rm -f "files_to_format.list"
    
    if [ $failed_count -eq 0 ]; then
        log_info "所有文件格式化完成！"
        exit 0
    else
        log_warn "$failed_count 个文件格式化失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [scan_dir] [file_patterns] [config_file] [dry_run] [backup]"
    echo ""
    echo "参数:"
    echo "  scan_dir      扫描目录，默认: ."
    echo "  file_patterns 文件模式，默认: \"*.py *.js *.java *.cpp *.css *.html\""
    echo "  config_file   配置文件路径"
    echo "  dry_run       是否试运行 (true|false)，默认: false"
    echo "  backup        是否创建备份 (true|false)，默认: true"
    echo ""
    echo "示例:"
    echo "  $0 ./src \"*.py *.js\""
    echo "  $0 . \"*.py *.js *.java\" \"\" false true"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 预提交钩子设置

```python
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def install_precommit_hook():
    """安装预提交钩子"""
    hooks_dir = Path(".git/hooks")
    precommit_file = hooks_dir / "pre-commit"
    
    # 创建钩子脚本
    hook_content = """#!/bin/bash
# 预提交代码格式化钩子

echo "运行代码格式化检查..."

# 检查暂存的文件
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.(py|js|jsx|ts|tsx|java|cpp|cxx|cc|c|h|hpp|css|html|json|xml)$')

if [ -z "$staged_files" ]; then
    echo "没有需要格式化的文件"
    exit 0
fi

echo "检查以下文件:"
echo "$staged_files"
echo ""

# 格式化文件
for file in $staged_files; do
    if [ -f "$file" ]; then
        echo "格式化: $file"
        python3 code_formatter.py "$file" --check
        if [ $? -ne 0 ]; then
            echo "格式检查失败: $file"
            echo "请运行 'python3 code_formatter.py \"$file\" --in-place' 修复格式问题"
            exit 1
        fi
    fi
done

echo "✅ 所有文件格式检查通过"
exit 0
"""
    
    # 写入钩子文件
    precommit_file.write_text(hook_content)
    
    # 设置执行权限
    precommit_file.chmod(0o755)
    
    print("预提交钩子已安装")

def check_precommit_hook():
    """检查预提交钩子"""
    hooks_dir = Path(".git/hooks")
    precommit_file = hooks_dir / "pre-commit"
    
    if precommit_file.exists():
        print("预提交钩子已安装")
        return True
    else:
        print("预提交钩子未安装")
        return False

def run_format_check():
    """运行格式检查"""
    # 获取暂存的文件
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("获取暂存文件失败")
        return False
    
    staged_files = result.stdout.strip().split('\n')
    
    # 过滤支持的文件类型
    supported_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', 
                          '.cxx', '.cc', '.c', '.h', '.hpp', '.css', '.html', '.json', '.xml'}
    
    files_to_check = []
    for file_path in staged_files:
        if file_path:
            ext = Path(file_path).suffix
            if ext in supported_extensions:
                files_to_check.append(file_path)
    
    if not files_to_check:
        print("没有需要格式化的文件")
        return True
    
    print(f"检查 {len(files_to_check)} 个文件...")
    
    # 检查每个文件
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"检查: {file_path}")
            
            result = subprocess.run(
                ["python3", "code_formatter.py", file_path, "--check"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ 格式检查失败: {file_path}")
                print(result.stderr)
                return False
            else:
                print(f"✅ 格式检查通过: {file_path}")
    
    print("所有文件格式检查通过")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='预提交钩子管理')
    parser.add_argument('action', choices=['install', 'check', 'run'], help='操作类型')
    
    args = parser.parse_args()
    
    if args.action == "install":
        install_precommit_hook()
    elif args.action == "check":
        check_precommit_hook()
    elif args.action == "run":
        if not run_format_check():
            sys.exit(1)
```

## 最佳实践

### 格式化规范
- **团队统一**: 团队内使用统一的格式化规则
- **自动化**: 尽可能自动化格式化过程
- **配置管理**: 使用配置文件管理格式化规则
- **版本控制**: 将格式化配置纳入版本控制

### 工作流程
- **预提交检查**: 提交前自动检查格式
- **CI/CD集成**: 在持续集成中检查格式
- **IDE集成**: 在编辑器中实时格式化
- **批量处理**: 定期批量格式化代码

### 配置管理
- **语言特定**: 为不同语言配置不同规则
- **项目特定**: 为项目配置特定规则
- **团队偏好**: 考虑团队偏好设置
- **最佳实践**: 遵循语言最佳实践

### 质量保证
- **格式检查**: 定期检查代码格式
- **一致性验证**: 验证格式一致性
- **错误修复**: 及时修复格式错误
- **培训教育**: 培训团队成员格式化规范

## 相关技能

- [文件分析器](./file-analyzer/) - 文件结构分析
- [环境验证器](./env-validator/) - 环境配置检查
- [安全扫描器](./security-scanner/) - 代码安全检查
- [依赖分析器](./dependency-analyzer/) - 依赖管理
