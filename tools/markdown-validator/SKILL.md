---
name: Markdown验证器
description: "当验证Markdown文件时，检查文档，查找损坏链接，改进文档。发布前验证Markdown。"
license: MIT
---

# Markdown验证器技能

## 概述

文档会静默损坏。损坏的链接、无效语法和缺失文件使文档不可用。发布前必须验证。

**核心原则**: 文档即代码。需要验证。好的文档管理应该完整、准确、可访问、易维护。坏的文档管理会导致信息混乱、用户体验差、维护困难。

## 何时使用

**始终:**
- 发布文档前
- 检查损坏链接时
- 验证语法时
- 提交前
- 测试文档渲染时

**触发短语:**
- "检查这个README"
- "查找损坏链接"
- "验证文档"
- "这个Markdown正确吗？"

## Markdown验证器技能功能

### 语法验证
- Markdown语法检查
- 标题层级验证
- 代码块格式检查
- 列表结构验证
- 表格格式检查
- 链接语法验证

### 链接检查
- 内部链接验证
- 外部链接测试
- 图片引用检查
- 锚点链接验证
- 相对路径检查
- 文件存在性验证

### 内容质量
- 文档完整性检查
- 拼写错误检测
- 语法问题识别
- 格式一致性检查
- TOC生成验证
- 元数据验证

### 渲染测试
- 多平台渲染测试
- 样式一致性检查
- 图片显示验证
- 代码高亮检查
- 数学公式验证
- 导出格式测试

## 常见Markdown问题

**❌ 损坏链接**
- 链接到不存在的文件
- 错误的相对路径
- 重命名文件的旧引用
- 外部链接失效

**❌ 语法错误**
- 不当的标题层级(H4后接H2)
- 未匹配的括号/括号
- 无效的代码块围栏
- 错误的列表缩进

**❌ 内容问题**
- 引用不存在的图片
- 不完整的章节
- 遗留的TODO注释
- 重复内容

**❌ 格式问题**
- 不一致的标题风格
- 错误的表格格式
- 混乱的列表结构
- 缺失的空行

## 代码示例

### Markdown验证器

```python
#!/usr/bin/env python3
import re
import os
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urljoin, urlparse
import time

class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    """验证问题"""
    level: ValidationLevel
    line_number: int
    column: int
    message: str
    suggestion: Optional[str] = None
    rule: Optional[str] = None

@dataclass
class LinkInfo:
    """链接信息"""
    text: str
    url: str
    line_number: int
    column: int
    link_type: str  # internal, external, image, anchor

class MarkdownValidator:
    """Markdown验证器"""
    
    def __init__(self, file_path: str, base_path: Optional[str] = None):
        self.file_path = Path(file_path)
        self.base_path = Path(base_path) if base_path else self.file_path.parent
        self.content = ""
        self.lines = []
        self.issues: List[ValidationIssue] = []
        self.links: List[LinkInfo] = []
        self.headers: List[Tuple[str, int, int]] = []  # (text, level, line_number)
        
        # 验证规则
        self.validation_rules = {
            'heading_hierarchy': self._validate_heading_hierarchy,
            'link_format': self._validate_link_format,
            'code_blocks': self._validate_code_blocks,
            'list_structure': self._validate_list_structure,
            'table_format': self._validate_table_format,
            'image_references': self._validate_image_references
        }
    
    def validate(self) -> List[ValidationIssue]:
        """执行验证"""
        self.issues.clear()
        
        # 读取文件
        if not self._read_file():
            return self.issues
        
        # 解析内容
        self._parse_content()
        
        # 执行各种验证
        for rule_name, rule_func in self.validation_rules.items():
            try:
                rule_func()
            except Exception as e:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    line_number=1,
                    column=1,
                    message=f"验证规则 {rule_name} 执行失败: {e}",
                    rule=rule_name
                ))
        
        # 检查链接
        self._check_links()
        
        return self.issues
    
    def _read_file(self) -> bool:
        """读取文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
            return True
        except FileNotFoundError:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                line_number=1,
                column=1,
                message=f"文件不存在: {self.file_path}"
            ))
            return False
        except UnicodeDecodeError:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                line_number=1,
                column=1,
                message="文件编码错误，请使用UTF-8编码"
            ))
            return False
    
    def _parse_content(self):
        """解析内容"""
        for line_num, line in enumerate(self.lines, 1):
            # 解析标题
            self._parse_headers(line, line_num)
            
            # 解析链接
            self._parse_links(line, line_num)
    
    def _parse_headers(self, line: str, line_num: int):
        """解析标题"""
        # 匹配Markdown标题
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            text = header_match.group(2).strip()
            self.headers.append((text, level, line_num))
    
    def _parse_links(self, line: str, line_num: int):
        """解析链接"""
        # 匹配链接格式: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, line):
            text = match.group(1)
            url = match.group(2)
            column = match.start() + 1
            
            # 判断链接类型
            link_type = self._determine_link_type(url)
            
            self.links.append(LinkInfo(
                text=text,
                url=url,
                line_number=line_num,
                column=column,
                link_type=link_type
            ))
        
        # 匹配图片格式: ![alt](url)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, line):
            alt = match.group(1)
            url = match.group(2)
            column = match.start() + 1
            
            self.links.append(LinkInfo(
                text=alt,
                url=url,
                line_number=line_num,
                column=column,
                link_type='image'
            ))
    
    def _determine_link_type(self, url: str) -> str:
        """确定链接类型"""
        if url.startswith('#'):
            return 'anchor'
        elif url.startswith('http://') or url.startswith('https://'):
            return 'external'
        elif url.startswith('mailto:'):
            return 'email'
        elif url.startswith('/') or './' in url or '../' in url:
            return 'internal'
        else:
            return 'internal'
    
    def _validate_heading_hierarchy(self):
        """验证标题层级"""
        prev_level = 0
        
        for text, level, line_num in self.headers:
            if prev_level > 0:
                # 检查层级跳跃
                if level > prev_level + 1:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        line_number=line_num,
                        column=1,
                        message=f"标题层级跳跃: H{prev_level} 后直接接 H{level}",
                        suggestion=f"建议使用 H{prev_level + 1} 或更小的跳跃",
                        rule='heading_hierarchy'
                    ))
            
            prev_level = level
    
    def _validate_link_format(self):
        """验证链接格式"""
        for line_num, line in enumerate(self.lines, 1):
            # 检查未匹配的括号
            open_brackets = line.count('[')
            close_brackets = line.count(']')
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            if open_brackets != close_brackets:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    line_number=line_num,
                    column=1,
                    message="方括号不匹配",
                    suggestion="检查链接语法",
                    rule='link_format'
                ))
            
            if open_parens != close_parens:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    line_number=line_num,
                    column=1,
                    message="圆括号不匹配",
                    suggestion="检查链接语法",
                    rule='link_format'
                ))
            
            # 检查空链接文本
            empty_link_pattern = r'\[\]\(([^)]+)\)'
            if re.search(empty_link_pattern, line):
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    line_number=line_num,
                    column=1,
                    message="链接文本为空",
                    suggestion="添加有意义的链接文本",
                    rule='link_format'
                ))
    
    def _validate_code_blocks(self):
        """验证代码块"""
        in_code_block = False
        code_block_start = 0
        code_fence = ''
        
        for line_num, line in enumerate(self.lines, 1):
            # 检查代码块围栏
            fence_match = re.match(r'^(`{3,}|~{3,})\s*(.*)$', line)
            if fence_match:
                current_fence = fence_match.group(1)
                language = fence_match.group(2)
                
                if not in_code_block:
                    # 开始代码块
                    in_code_block = True
                    code_block_start = line_num
                    code_fence = current_fence
                elif current_fence == code_fence:
                    # 结束代码块
                    in_code_block = False
                    code_fence = ''
                else:
                    # 不匹配的围栏
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        line_number=line_num,
                        column=1,
                        message="代码块围栏不匹配",
                        suggestion="使用相同数量和类型的围栏字符",
                        rule='code_blocks'
                    ))
        
        # 检查未关闭的代码块
        if in_code_block:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                line_number=code_block_start,
                column=1,
                message="代码块未关闭",
                suggestion="在文件末尾添加关闭围栏",
                rule='code_blocks'
            ))
    
    def _validate_list_structure(self):
        """验证列表结构"""
        list_stack = []  # 存储列表层级信息
        
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.lstrip()
            
            # 检查列表项
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+', stripped)
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                
                # 检查缩进一致性
                if list_stack:
                    last_indent, last_marker = list_stack[-1]
                    
                    # 有序列表和无序列表混用
                    if (marker.isdigit() and not last_marker.isdigit()) or \
                       (not marker.isdigit() and last_marker.isdigit()):
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            line_number=line_num,
                            column=indent + 1,
                            message="有序列表和无序列表混用",
                            suggestion="保持列表类型一致",
                            rule='list_structure'
                        ))
                
                list_stack.append((indent, marker))
            elif stripped and not line.startswith('#') and not line.startswith('>'):
                # 非列表行，清空栈
                list_stack.clear()
    
    def _validate_table_format(self):
        """验证表格格式"""
        in_table = False
        table_start = 0
        column_count = 0
        
        for line_num, line in enumerate(self.lines, 1):
            # 检查表格行
            if '|' in line:
                if not in_table:
                    # 表格开始
                    in_table = True
                    table_start = line_num
                    column_count = line.count('|') - 1  # 减去两端的|
                else:
                    # 表格继续
                    current_columns = line.count('|') - 1
                    if current_columns != column_count:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            line_number=line_num,
                            column=1,
                            message=f"表格列数不一致: 期望 {column_count} 列，实际 {current_columns} 列",
                            suggestion="确保每行的列数相同",
                            rule='table_format'
                        ))
            else:
                # 表格结束
                if in_table:
                    in_table = False
                    column_count = 0
    
    def _validate_image_references(self):
        """验证图片引用"""
        for link in self.links:
            if link.link_type == 'image':
                # 检查图片文件是否存在
                if not link.url.startswith('http://') and not link.url.startswith('https://'):
                    image_path = self.base_path / link.url
                    if not image_path.exists():
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.ERROR,
                            line_number=link.line_number,
                            column=link.column,
                            message=f"图片文件不存在: {link.url}",
                            suggestion="检查图片路径或添加图片文件",
                            rule='image_references'
                        ))
    
    def _check_links(self):
        """检查链接"""
        for link in self.links:
            if link.link_type == 'internal':
                self._check_internal_link(link)
            elif link.link_type == 'external':
                self._check_external_link(link)
            elif link.link_type == 'anchor':
                self._check_anchor_link(link)
    
    def _check_internal_link(self, link: LinkInfo):
        """检查内部链接"""
        # 解析相对路径
        if link.url.startswith('./'):
            target_path = self.base_path / link.url[2:]
        elif link.url.startswith('../'):
            target_path = self.base_path / link.url
        else:
            target_path = self.base_path / link.url
        
        # 检查文件是否存在
        if not target_path.exists():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                line_number=link.line_number,
                column=link.column,
                message=f"内部链接目标不存在: {link.url}",
                suggestion="检查文件路径或创建目标文件",
                rule='link_check'
            ))
    
    def _check_external_link(self, link: LinkInfo):
        """检查外部链接"""
        try:
            # 发送HEAD请求检查链接
            response = requests.head(link.url, timeout=10, allow_redirects=True)
            if response.status_code >= 400:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    line_number=link.line_number,
                    column=link.column,
                    message=f"外部链接可能失效: {link.url} (状态码: {response.status_code})",
                    suggestion="检查链接是否正确或更新链接",
                    rule='link_check'
                ))
        except requests.RequestException:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                line_number=link.line_number,
                column=link.column,
                message=f"无法检查外部链接: {link.url}",
                suggestion="手动检查链接有效性",
                rule='link_check'
            ))
    
    def _check_anchor_link(self, link: LinkInfo):
        """检查锚点链接"""
        anchor = link.url[1:]  # 移除#
        
        # 查找对应的标题
        found = False
        for text, level, line_num in self.headers:
            # 生成锚点ID (GitHub风格)
            anchor_id = text.lower()
            anchor_id = re.sub(r'[^\w\s-]', '', anchor_id)
            anchor_id = re.sub(r'[-\s]+', '-', anchor_id)
            
            if anchor_id == anchor:
                found = True
                break
        
        if not found:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                line_number=link.line_number,
                column=link.column,
                message=f"锚点链接目标不存在: {link.url}",
                suggestion="检查标题文本或更新锚点",
                rule='link_check'
            ))
    
    def generate_report(self) -> Dict:
        """生成验证报告"""
        # 执行验证
        self.validate()
        
        # 统计信息
        error_count = len([i for i in self.issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in self.issues if i.level == ValidationLevel.WARNING])
        info_count = len([i for i in self.issues if i.level == ValidationLevel.INFO])
        
        # 按规则分组
        issues_by_rule = {}
        for issue in self.issues:
            rule = issue.rule or 'other'
            if rule not in issues_by_rule:
                issues_by_rule[rule] = []
            issues_by_rule[rule].append(issue)
        
        return {
            'file_path': str(self.file_path),
            'summary': {
                'total_issues': len(self.issues),
                'error_count': error_count,
                'warning_count': warning_count,
                'info_count': info_count,
                'links_checked': len(self.links),
                'headers_found': len(self.headers)
            },
            'issues': [
                {
                    'level': issue.level.value,
                    'line_number': issue.line_number,
                    'column': issue.column,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'rule': issue.rule
                }
                for issue in self.issues
            ],
            'issues_by_rule': {
                rule: [
                    {
                        'line_number': issue.line_number,
                        'column': issue.column,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in issues
                ]
                for rule, issues in issues_by_rule.items()
            },
            'links': [
                {
                    'text': link.text,
                    'url': link.url,
                    'line_number': link.line_number,
                    'type': link.link_type
                }
                for link in self.links
            ],
            'headers': [
                {
                    'text': text,
                    'level': level,
                    'line_number': line_num
                }
                for text, level, line_num in self.headers
            ]
        }

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Markdown验证器')
    parser.add_argument('file', help='Markdown文件路径')
    parser.add_argument('--base-path', help='基础路径（用于相对链接解析）')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    parser.add_argument('--check-external', action='store_true', help='检查外部链接')
    
    args = parser.parse_args()
    
    validator = MarkdownValidator(args.file, args.base_path)
    
    try:
        report = validator.generate_report()
        
        if args.format == 'json':
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"报告已保存到: {args.output}")
            else:
                print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            print("=" * 50)
            print("Markdown验证报告")
            print("=" * 50)
            print(f"文件: {report['file_path']}")
            
            # 摘要
            summary = report['summary']
            print(f"总问题数: {summary['total_issues']}")
            print(f"错误数: {summary['error_count']}")
            print(f"警告数: {summary['warning_count']}")
            print(f"信息数: {summary['info_count']}")
            print(f"检查的链接数: {summary['links_checked']}")
            print(f"发现的标题数: {summary['headers_found']}")
            print()
            
            # 按级别显示问题
            level_names = {
                'error': '🚨 错误',
                'warning': '⚠️ 警告',
                'info': 'ℹ️ 信息'
            }
            
            for level in ['error', 'warning', 'info']:
                issues = [i for i in report['issues'] if i['level'] == level]
                if issues:
                    print(f"{level_names[level]}:")
                    for issue in issues:
                        print(f"  行 {issue['line_number']}: {issue['message']}")
                        if issue['suggestion']:
                            print(f"    建议: {issue['suggestion']}")
                    print()
            
            # 状态总结
            if summary['error_count'] == 0:
                print("✅ Markdown验证通过！")
            else:
                print(f"❌ 发现 {summary['error_count']} 个错误，需要修复")
    
    except Exception as e:
        print(f"验证失败: {e}")
        exit(1)
```

### 批量Markdown检查工具

```bash
#!/bin/bash
# markdown-batch-checker.sh - 批量Markdown检查工具

set -e

# 配置
SCAN_DIR=${1:-"."}
OUTPUT_DIR=${2:-"markdown-reports"}
CHECK_EXTERNAL=${3:-false}
PARALLEL_JOBS=${4:-4}
LOG_FILE="markdown_batch_check.log"

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

# 创建输出目录
create_output_dir() {
    if [ ! -d "$OUTPUT_DIR" ]; then
        mkdir -p "$OUTPUT_DIR"
        log_info "创建输出目录: $OUTPUT_DIR"
    fi
}

# 查找Markdown文件
find_markdown_files() {
    log_step "查找Markdown文件..."
    
    local markdown_files=()
    
    # 查找所有.md文件
    while IFS= read -r -d '' file; do
        markdown_files+=("$file")
    done < <(find "$SCAN_DIR" -name "*.md" -type f -print0)
    
    log_info "找到 ${#markdown_files[@]} 个Markdown文件"
    
    # 保存文件列表
    printf '%s\n' "${markdown_files[@]}" > "$OUTPUT_DIR/markdown_files.list"
    
    echo "${#markdown_files[@]}"
}

# 检查单个文件
check_single_file() {
    local file_path="$1"
    local file_basename=$(basename "$file_path" .md)
    local report_file="$OUTPUT_DIR/${file_basename}_report.json"
    
    log_info "检查文件: $file_path"
    
    # 使用Python验证器
    if command -v python3 &> /dev/null; then
        python3 markdown_validator.py "$file_path" --output "$report_file" --format json 2>> "$LOG_FILE"
    else
        log_error "Python3未安装，无法执行验证"
        return 1
    fi
    
    # 检查是否成功
    if [ $? -eq 0 ]; then
        log_info "✅ $file_path 检查完成"
        return 0
    else
        log_error "❌ $file_path 检查失败"
        return 1
    fi
}

# 并行检查文件
check_files_parallel() {
    local total_files=$1
    local checked_files=0
    local failed_files=0
    
    log_step "开始并行检查 (并行度: $PARALLEL_JOBS)..."
    
    # 从文件列表读取并并行处理
    while IFS= read -r file_path; do
        # 控制并发数
        if (( $(jobs -r | wc -l) >= PARALLEL_JOBS )); then
            wait -n
        fi
        
        # 启动后台任务
        {
            if check_single_file "$file_path"; then
                echo "SUCCESS:$file_path" >> "$OUTPUT_DIR/check_results.tmp"
            else
                echo "FAILED:$file_path" >> "$OUTPUT_DIR/check_results.tmp"
            fi
        } &
        
        ((checked_files++))
        
        # 显示进度
        if (( checked_files % 10 == 0 )); then
            log_info "进度: $checked_files/$total_files"
        fi
        
    done < "$OUTPUT_DIR/markdown_files.list"
    
    # 等待所有任务完成
    wait
    
    # 统计结果
    if [ -f "$OUTPUT_DIR/check_results.tmp" ]; then
        failed_files=$(grep -c "^FAILED:" "$OUTPUT_DIR/check_results.tmp" || echo "0")
        successful_files=$(grep -c "^SUCCESS:" "$OUTPUT_DIR/check_results.tmp" || echo "0")
    else
        failed_files=0
        successful_files=0
    fi
    
    log_info "检查完成: 成功 $successful_files, 失败 $failed_files"
    
    return $failed_files
}

# 生成汇总报告
generate_summary_report() {
    log_step "生成汇总报告..."
    
    local summary_file="$OUTPUT_DIR/summary_report.md"
    
    cat > "$summary_file" << EOF
# Markdown批量检查报告

## 检查信息
- 扫描目录: $SCAN_DIR
- 检查时间: $(date)
- 并行度: $PARALLEL_JOBS
- 输出目录: $OUTPUT_DIR

## 统计摘要
EOF
    
    # 统计文件总数
    local total_files=$(wc -l < "$OUTPUT_DIR/markdown_files.list")
    echo "- 总文件数: $total_files" >> "$summary_file"
    
    # 统计检查结果
    if [ -f "$OUTPUT_DIR/check_results.tmp" ]; then
        local failed_files=$(grep -c "^FAILED:" "$OUTPUT_DIR/check_results.tmp" || echo "0")
        local successful_files=$(grep -c "^SUCCESS:" "$OUTPUT_DIR/check_results.tmp" || echo "0")
        
        echo "- 成功检查: $successful_files" >> "$summary_file"
        echo "- 检查失败: $failed_files" >> "$summary_file"
    fi
    
    echo "" >> "$summary_file"
    
    # 统计问题
    local total_errors=0
    local total_warnings=0
    local total_issues=0
    
    for report_file in "$OUTPUT_DIR"/*_report.json; do
        if [ -f "$report_file" ]; then
            if command -v jq &> /dev/null; then
                local errors=$(jq -r '.summary.error_count // 0' "$report_file" 2>/dev/null || echo "0")
                local warnings=$(jq -r '.summary.warning_count // 0' "$report_file" 2>/dev/null || echo "0")
                local issues=$(jq -r '.summary.total_issues // 0' "$report_file" 2>/dev/null || echo "0")
                
                total_errors=$((total_errors + errors))
                total_warnings=$((total_warnings + warnings))
                total_issues=$((total_issues + issues))
            fi
        fi
    done
    
    echo "## 问题统计" >> "$summary_file"
    echo "- 总问题数: $total_issues" >> "$summary_file"
    echo "- 错误数: $total_errors" >> "$summary_file"
    echo "- 警告数: $total_warnings" >> "$summary_file"
    echo "" >> "$summary_file"
    
    # 失败的文件列表
    if [ -f "$OUTPUT_DIR/check_results.tmp" ]; then
        local failed_list=$(grep "^FAILED:" "$OUTPUT_DIR/check_results.tmp" | cut -d: -f2-)
        if [ -n "$failed_list" ]; then
            echo "## 检查失败的文件" >> "$summary_file"
            echo "$failed_list" | sed 's/^/- /' >> "$summary_file"
            echo "" >> "$summary_file"
        fi
    fi
    
    # 问题最多的文件
    echo "## 问题最多的文件" >> "$summary_file"
    echo "| 文件 | 错误 | 警告 | 总问题 |" >> "$summary_file"
    echo "|------|------|------|--------|" >> "$summary_file"
    
    # 创建临时文件排序
    local temp_file="$OUTPUT_DIR/file_stats.tmp"
    > "$temp_file"
    
    for report_file in "$OUTPUT_DIR"/*_report.json; do
        if [ -f "$report_file" ]; then
            local file_name=$(basename "$report_file" _report.json).md
            if command -v jq &> /dev/null; then
                local errors=$(jq -r '.summary.error_count // 0' "$report_file" 2>/dev/null || echo "0")
                local warnings=$(jq -r '.summary.warning_count // 0' "$report_file" 2>/dev/null || echo "0")
                local issues=$(jq -r '.summary.total_issues // 0' "$report_file" 2>/dev/null || echo "0")
                
                echo "$file_name|$errors|$warnings|$issues" >> "$temp_file"
            fi
        fi
    done
    
    # 按总问题数排序并输出前10个
    if [ -f "$temp_file" ]; then
        sort -t'|' -k4 -nr "$temp_file" | head -10 | while IFS='|' read -r file errors warnings issues; do
            echo "| $file | $errors | $warnings | $issues |" >> "$summary_file"
        done
        rm "$temp_file"
    fi
    
    echo "" >> "$summary_file"
    
    # 建议
    echo "## 建议" >> "$summary_file"
    echo "- 优先修复错误级别的问题" >> "$summary_file"
    echo "- 检查失败的文件可能需要手动处理" >> "$summary_file"
    echo "- 建立定期检查机制" >> "$summary_file"
    echo "- 使用预提交钩子自动检查" >> "$summary_file"
    
    log_info "汇总报告已生成: $summary_file"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    rm -f "$OUTPUT_DIR/check_results.tmp"
    rm -f "$OUTPUT_DIR/markdown_files.list"
}

# 主函数
main() {
    log_info "开始Markdown批量检查..."
    log_info "扫描目录: $SCAN_DIR"
    log_info "输出目录: $OUTPUT_DIR"
    
    # 创建输出目录
    create_output_dir
    
    # 查找文件
    total_files=$(find_markdown_files)
    
    if [ "$total_files" -eq 0 ]; then
        log_warn "未找到Markdown文件"
        exit 0
    fi
    
    # 并行检查
    failed_count=0
    check_files_parallel "$total_files"
    failed_count=$?
    
    # 生成汇总报告
    generate_summary_report
    
    # 清理
    cleanup
    
    if [ $failed_count -eq 0 ]; then
        log_info "所有文件检查完成！"
        exit 0
    else
        log_warn "$failed_count 个文件检查失败"
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [scan_dir] [output_dir] [check_external] [parallel_jobs]"
    echo ""
    echo "参数:"
    echo "  scan_dir        扫描目录，默认: ."
    echo "  output_dir      输出目录，默认: markdown-reports"
    echo "  check_external  是否检查外部链接 (true|false)，默认: false"
    echo "  parallel_jobs   并行任务数，默认: 4"
    echo ""
    echo "示例:"
    echo "  $0 ./docs ./reports true 8"
    echo "  $0 . ./markdown-check"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 文档质量评分器

```python
#!/usr/bin/env python3
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

@dataclass
class QualityMetric:
    """质量指标"""
    name: str
    score: float
    max_score: float
    description: str
    issues: List[str]

class DocumentQualityScorer:
    """文档质量评分器"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.lines = []
        self.metrics: List[QualityMetric] = []
        
        # 评分权重
        self.weights = {
            'structure': 0.25,
            'content': 0.30,
            'links': 0.20,
            'formatting': 0.15,
            'readability': 0.10
        }
    
    def score_document(self) -> Dict:
        """为文档评分"""
        # 读取文件
        if not self._read_file():
            return {'error': '无法读取文件'}
        
        # 计算各项指标
        self._analyze_structure()
        self._analyze_content()
        self._analyze_links()
        self._analyze_formatting()
        self._analyze_readability()
        
        # 计算总分
        total_score = self._calculate_total_score()
        
        return {
            'file_path': str(self.file_path),
            'total_score': total_score,
            'grade': self._get_grade(total_score),
            'metrics': [
                {
                    'name': metric.name,
                    'score': metric.score,
                    'max_score': metric.max_score,
                    'percentage': (metric.score / metric.max_score) * 100,
                    'description': metric.description,
                    'issues': metric.issues
                }
                for metric in self.metrics
            ],
            'recommendations': self._get_recommendations()
        }
    
    def _read_file(self) -> bool:
        """读取文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
            return True
        except:
            return False
    
    def _analyze_structure(self):
        """分析文档结构"""
        issues = []
        score = 0
        max_score = 100
        
        # 检查标题结构
        headers = self._extract_headers()
        if not headers:
            issues.append("文档缺少标题")
        else:
            # 检查是否有H1标题
            has_h1 = any(level == 1 for _, level, _ in headers)
            if not has_h1:
                issues.append("缺少H1主标题")
            else:
                score += 20
            
            # 检查标题层级
            prev_level = 0
            hierarchy_issues = 0
            for _, level, _ in headers:
                if prev_level > 0 and level > prev_level + 1:
                    hierarchy_issues += 1
                prev_level = level
            
            if hierarchy_issues == 0:
                score += 30
            elif hierarchy_issues <= 2:
                score += 20
                issues.append(f"发现 {hierarchy_issues} 个标题层级跳跃")
            else:
                issues.append(f"发现 {hierarchy_issues} 个标题层级跳跃")
        
        # 检查目录
        if self._has_toc():
            score += 20
        else:
            issues.append("缺少目录")
        
        # 检查章节平衡
        if len(headers) >= 3:
            score += 15
        else:
            issues.append("章节过少")
        
        # 检查文档长度
        word_count = len(self.content.split())
        if word_count >= 500:
            score += 15
        else:
            issues.append("文档过短")
        
        self.metrics.append(QualityMetric(
            name="结构质量",
            score=score,
            max_score=max_score,
            description="评估文档结构的完整性和合理性",
            issues=issues
        ))
    
    def _analyze_content(self):
        """分析内容质量"""
        issues = []
        score = 0
        max_score = 100
        
        # 检查代码块
        code_blocks = self._count_code_blocks()
        if code_blocks > 0:
            score += 20
        else:
            issues.append("缺少代码示例")
        
        # 检查图片
        images = self._count_images()
        if images > 0:
            score += 15
        else:
            issues.append("缺少图片说明")
        
        # 检查表格
        tables = self._count_tables()
        if tables > 0:
            score += 15
        else:
            issues.append("缺少表格数据")
        
        # 检查列表
        lists = self._count_lists()
        if lists > 0:
            score += 10
        else:
            issues.append("缺少列表内容")
        
        # 检查内容完整性
        if not self._has_todo_comments():
            score += 20
        else:
            issues.append("存在TODO注释")
        
        # 检查描述性内容
        desc_lines = sum(1 for line in self.lines if len(line.strip()) > 50)
        total_lines = len([line for line in self.lines if line.strip()])
        if total_lines > 0 and desc_lines / total_lines > 0.3:
            score += 20
        else:
            issues.append("描述性内容不足")
        
        self.metrics.append(QualityMetric(
            name="内容质量",
            score=score,
            max_score=max_score,
            description="评估文档内容的丰富性和完整性",
            issues=issues
        ))
    
    def _analyze_links(self):
        """分析链接质量"""
        issues = []
        score = 0
        max_score = 100
        
        links = self._extract_links()
        if not links:
            issues.append("文档中没有链接")
            self.metrics.append(QualityMetric(
                name="链接质量",
                score=0,
                max_score=max_score,
                description="评估文档链接的质量和有效性",
                issues=issues
            ))
            return
        
        # 检查链接数量
        if len(links) >= 5:
            score += 30
        elif len(links) >= 2:
            score += 20
        else:
            issues.append("链接数量过少")
        
        # 检查链接类型多样性
        link_types = set(link.link_type for link in links)
        if len(link_types) >= 3:
            score += 30
        elif len(link_types) >= 2:
            score += 20
        else:
            issues.append("链接类型单一")
        
        # 检查锚点链接
        anchor_links = [link for link in links if link.link_type == 'anchor']
        if anchor_links:
            score += 20
        else:
            issues.append("缺少内部锚点链接")
        
        # 检查外部链接
        external_links = [link for link in links if link.link_type == 'external']
        if external_links:
            score += 20
        else:
            issues.append("缺少外部参考链接")
        
        self.metrics.append(QualityMetric(
            name="链接质量",
            score=score,
            max_score=max_score,
            description="评估文档链接的质量和有效性",
            issues=issues
        ))
    
    def _analyze_formatting(self):
        """分析格式质量"""
        issues = []
        score = 0
        max_score = 100
        
        # 检查代码块格式
        if self._has_proper_code_blocks():
            score += 25
        else:
            issues.append("代码块格式不规范")
        
        # 检查列表格式
        if self._has_proper_lists():
            score += 25
        else:
            issues.append("列表格式不规范")
        
        # 检查表格格式
        if self._has_proper_tables():
            score += 25
        else:
            issues.append("表格格式不规范")
        
        # 检查空行使用
        if self._has_proper_spacing():
            score += 25
        else:
            issues.append("空行使用不当")
        
        self.metrics.append(QualityMetric(
            name="格式质量",
            score=score,
            max_score=max_score,
            description="评估文档格式的规范性和一致性",
            issues=issues
        ))
    
    def _analyze_readability(self):
        """分析可读性"""
        issues = []
        score = 0
        max_score = 100
        
        # 计算平均句子长度
        sentences = re.split(r'[.!?]+', self.content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            if 10 <= avg_sentence_length <= 20:
                score += 30
            elif 20 < avg_sentence_length <= 25:
                score += 20
                issues.append("句子偏长")
            else:
                issues.append("句子长度不合适")
        
        # 检查段落长度
        paragraphs = [p.strip() for p in self.content.split('\n\n') if p.strip()]
        long_paragraphs = sum(1 for p in paragraphs if len(p.split()) > 100)
        
        if long_paragraphs == 0:
            score += 30
        elif long_paragraphs <= 2:
            score += 20
        else:
            issues.append(f"发现 {long_paragraphs} 个过长段落")
        
        # 检查复杂词汇
        complex_words = self._count_complex_words()
        total_words = len(self.content.split())
        
        if total_words > 0:
            complex_ratio = complex_words / total_words
            if complex_ratio <= 0.1:
                score += 20
            elif complex_ratio <= 0.2:
                score += 15
            else:
                issues.append("复杂词汇比例过高")
        
        # 检查重复词汇
        if not self._has_excessive_repetition():
            score += 20
        else:
            issues.append("存在过度重复")
        
        self.metrics.append(QualityMetric(
            name="可读性",
            score=score,
            max_score=max_score,
            description="评估文档的可读性和易理解性",
            issues=issues
        ))
    
    def _extract_headers(self) -> List[Tuple[str, int, int]]:
        """提取标题"""
        headers = []
        for line_num, line in enumerate(self.lines, 1):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headers.append((text, level, line_num))
        return headers
    
    def _extract_links(self) -> List[LinkInfo]:
        """提取链接"""
        links = []
        for line_num, line in enumerate(self.lines, 1):
            # 匹配链接
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, line):
                text = match.group(1)
                url = match.group(2)
                column = match.start() + 1
                link_type = self._determine_link_type(url)
                
                links.append(LinkInfo(
                    text=text,
                    url=url,
                    line_number=line_num,
                    column=column,
                    link_type=link_type
                ))
            
            # 匹配图片
            image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            for match in re.finditer(image_pattern, line):
                alt = match.group(1)
                url = match.group(2)
                column = match.start() + 1
                
                links.append(LinkInfo(
                    text=alt,
                    url=url,
                    line_number=line_num,
                    column=column,
                    link_type='image'
                ))
        return links
    
    def _determine_link_type(self, url: str) -> str:
        """确定链接类型"""
        if url.startswith('#'):
            return 'anchor'
        elif url.startswith('http://') or url.startswith('https://'):
            return 'external'
        elif url.startswith('mailto:'):
            return 'email'
        else:
            return 'internal'
    
    def _has_toc(self) -> bool:
        """检查是否有目录"""
        toc_indicators = ['目录', 'TOC', 'Table of Contents', '## 目录', '### 目录']
        return any(indicator in self.content for indicator in toc_indicators)
    
    def _has_todo_comments(self) -> bool:
        """检查是否有TODO注释"""
        todo_patterns = [r'TODO:', r'FIXME:', r'XXX:', r'待办', r'待完成']
        return any(re.search(pattern, self.content, re.IGNORECASE) for pattern in todo_patterns)
    
    def _count_code_blocks(self) -> int:
        """统计代码块数量"""
        return len(re.findall(r'```[\s\S]*?```', self.content))
    
    def _count_images(self) -> int:
        """统计图片数量"""
        return len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', self.content))
    
    def _count_tables(self) -> int:
        """统计表格数量"""
        table_lines = [line for line in self.lines if '|' in line]
        return len([line for line in table_lines if line.strip().startswith('|')])
    
    def _count_lists(self) -> int:
        """统计列表数量"""
        return len([line for line in self.lines if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line)])
    
    def _has_proper_code_blocks(self) -> bool:
        """检查代码块格式"""
        fences = re.findall(r'^(`{3,}|~{3,})\s*$', self.content, re.MULTILINE)
        return len(fences) % 2 == 0
    
    def _has_proper_lists(self) -> bool:
        """检查列表格式"""
        # 简化检查
        return True
    
    def _has_proper_tables(self) -> bool:
        """检查表格格式"""
        # 简化检查
        return True
    
    def _has_proper_spacing(self) -> bool:
        """检查空行使用"""
        # 检查标题前是否有空行
        header_lines = [i for i, line in enumerate(self.lines) if re.match(r'^#{1,6}\s+', line)]
        proper_spacing = 0
        
        for line_num in header_lines:
            if line_num > 0 and self.lines[line_num - 1].strip() == '':
                proper_spacing += 1
        
        return len(header_lines) > 0 and proper_spacing / len(header_lines) > 0.5
    
    def _count_complex_words(self) -> int:
        """统计复杂词汇"""
        # 简化实现：统计长度超过8个字符的单词
        words = re.findall(r'\b\w+\b', self.content.lower())
        return len([word for word in words if len(word) > 8])
    
    def _has_excessive_repetition(self) -> bool:
        """检查过度重复"""
        words = re.findall(r'\b\w+\b', self.content.lower())
        if len(words) < 10:
            return False
        
        word_counts = Counter(words)
        most_common = word_counts.most_common(5)
        
        # 如果最常用的词出现频率超过20%，认为有过度重复
        return most_common[0][1] / len(words) > 0.2
    
    def _calculate_total_score(self) -> float:
        """计算总分"""
        total_score = 0
        total_weight = 0
        
        for metric in self.metrics:
            category = None
            if '结构' in metric.name:
                category = 'structure'
            elif '内容' in metric.name:
                category = 'content'
            elif '链接' in metric.name:
                category = 'links'
            elif '格式' in metric.name:
                category = 'formatting'
            elif '可读' in metric.name:
                category = 'readability'
            
            if category and category in self.weights:
                weight = self.weights[category]
                percentage = metric.score / metric.max_score
                total_score += percentage * weight * 100
                total_weight += weight
        
        return total_score if total_weight > 0 else 0
    
    def _get_grade(self, score: float) -> str:
        """获取等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _get_recommendations(self) -> List[str]:
        """获取改进建议"""
        recommendations = []
        
        for metric in self.metrics:
            if metric.score < metric.max_score * 0.7:
                if '结构' in metric.name:
                    recommendations.append("改进文档结构：添加清晰的标题层级和目录")
                elif '内容' in metric.name:
                    recommendations.append("丰富内容：添加代码示例、图片和表格")
                elif '链接' in metric.name:
                    recommendations.append("优化链接：添加更多相关链接和锚点")
                elif '格式' in metric.name:
                    recommendations.append("规范格式：检查代码块、列表和表格格式")
                elif '可读' in metric.name:
                    recommendations.append("提升可读性：简化句子和段落结构")
        
        return recommendations

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='文档质量评分器')
    parser.add_argument('file', help='Markdown文件路径')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    scorer = DocumentQualityScorer(args.file)
    
    try:
        result = scorer.score_document()
        
        if args.format == 'json':
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"评分报告已保存到: {args.output}")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            if 'error' in result:
                print(f"错误: {result['error']}")
                exit(1)
            
            print("=" * 50)
            print("文档质量评分报告")
            print("=" * 50)
            print(f"文件: {result['file_path']}")
            print(f"总分: {result['total_score']:.1f}/100")
            print(f"等级: {result['grade']}")
            print()
            
            # 各项指标
            print("## 各项指标")
            for metric in result['metrics']:
                print(f"### {metric['name']}")
                print(f"得分: {metric['score']:.1f}/{metric['max_score']} ({metric['percentage']:.1f}%)")
                print(f"描述: {metric['description']}")
                if metric['issues']:
                    print("问题:")
                    for issue in metric['issues']:
                        print(f"  - {issue}")
                print()
            
            # 改进建议
            if result['recommendations']:
                print("## 改进建议")
                for i, rec in enumerate(result['recommendations'], 1):
                    print(f"{i}. {rec}")
                print()
            
            # 总结
            grade_descriptions = {
                'A': '优秀 - 文档质量很高',
                'B': '良好 - 文档质量较好',
                'C': '一般 - 文档需要一些改进',
                'D': '较差 - 文档需要大量改进',
                'F': '很差 - 文档需要重写'
            }
            
            print(f"## 总结")
            print(f"文档质量: {grade_descriptions.get(result['grade'], '未知')}")
    
    except Exception as e:
        print(f"评分失败: {e}")
        exit(1)
```

## 最佳实践

### 文档结构
- **清晰层级**: 使用合理的标题层级结构
- **完整目录**: 提供详细的目录导航
- **章节平衡**: 各章节内容长度适中
- **逻辑顺序**: 内容按逻辑顺序组织

### 内容质量
- **代码示例**: 提供实用的代码示例
- **图片说明**: 使用图片增强理解
- **表格数据**: 用表格展示结构化信息
- **实例演示**: 包含实际使用案例

### 链接管理
- **内部链接**: 建立文档间的关联
- **外部参考**: 提供相关资源链接
- **锚点导航**: 使用锚点方便跳转
- **定期检查**: 定期验证链接有效性

### 格式规范
- **一致性**: 保持格式风格一致
- **可读性**: 注重阅读体验
- **标准化**: 遵循Markdown标准
- **兼容性**: 确保多平台兼容

## 相关技能

- [文件分析器](./file-analyzer/) - 文件结构检查
- [代码格式化器](./code-formatter/) - 代码格式优化
- [环境验证器](./env-validator/) - 文档环境检查
- [依赖分析器](./dependency-analyzer/) - 依赖文档验证
