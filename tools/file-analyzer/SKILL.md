---
name: 文件分析器
description: "当分析文件时，分析文件结构，优化存储空间，解决重复文件。验证文件架构，设计清理策略，和最佳实践。"
license: MIT
---

# 文件分析器技能

## 概述

文件分析是项目维护的重要工具，能够帮助识别大文件、重复文件、无用文件，优化存储空间和构建性能。不当的文件管理会导致项目膨胀、构建缓慢、存储浪费。

**核心原则**: 好的文件管理应该清晰分类、及时清理、定期分析、自动化维护。坏的文件管理会导致文件混乱、空间浪费、性能下降。

## 何时使用

**始终:**
- 部署前检查时
- 调查磁盘使用时
- 发现构建问题时
- 识别重复文件时
- 减少仓库大小时
- 清理无用文件时

**触发短语:**
- "查找大文件"
- "什么占用了空间？"
- "检测重复文件"
- "分析目录"
- "为什么这么臃肿？"
- "清理无用文件"

## 文件分析器技能功能

### 文件分析
- 大文件检测
- 重复文件识别
- 文件类型统计
- 目录结构分析
- 文件大小分布
- 文件变更追踪

### 存储优化
- 空间使用分析
- 压缩建议
- 清理策略
- 存储优化
- 备份管理
- 归档策略

### 质量检查
- 文件完整性验证
- 损坏文件检测
- 权限检查
- 编码验证
- 格式检查
- 内容验证

### 自动化管理
- 定期清理任务
- 自动归档
- 监控告警
- 报告生成
- 批量操作
- 脚本自动化

## 常见问题

**❌ 文件过大**
- 二进制文件未忽略
- 日志文件积累
- 临时文件未清理
- 媒体文件过多

**❌ 重复文件**
- 代码重复
- 资源文件重复
- 配置文件重复
- 依赖文件重复

**❌ 结构混乱**
- 文件分类不清
- 目录层次过深
- 命名不规范
- 组织结构混乱

**❌ 空间浪费**
- 无用文件堆积
- 临时文件未清理
- 备份文件过多
- 缓存文件过大

## 代码示例

### 文件大小分析器

```python
#!/usr/bin/env python3
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json
import time

@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    mime_type: str
    hash: Optional[str] = None
    created_time: float = 0
    modified_time: float = 0
    accessed_time: float = 0

@dataclass
class DirectoryInfo:
    """目录信息"""
    path: str
    size: int
    file_count: int
    subdirectory_count: int
    largest_file: Optional[FileInfo] = None
    files: List[FileInfo] = None

class FileAnalyzer:
    """文件分析器"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.file_cache: Dict[str, FileInfo] = {}
        self.directory_cache: Dict[str, DirectoryInfo] = {}
        self.ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.vscode', 
            '.idea', 'dist', 'build', '.next', 'coverage'
        }
    
    def should_ignore(self, path: Path) -> bool:
        """判断是否应该忽略文件/目录"""
        parts = path.parts
        return any(part in self.ignore_patterns for part in parts)
    
    def calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """计算文件哈希值"""
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, PermissionError):
            return ""
    
    def get_file_info(self, file_path: Path) -> FileInfo:
        """获取文件信息"""
        if str(file_path) in self.file_cache:
            return self.file_cache[str(file_path)]
        
        try:
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            file_info = FileInfo(
                path=str(file_path),
                size=stat.st_size,
                mime_type=mime_type or 'unknown',
                created_time=stat.st_ctime,
                modified_time=stat.st_mtime,
                accessed_time=stat.st_atime
            )
            
            # 对大文件计算哈希
            if file_info.size > 1024 * 1024:  # 1MB以上
                file_info.hash = self.calculate_file_hash(file_path)
            
            self.file_cache[str(file_path)] = file_info
            return file_info
        
        except (OSError, PermissionError):
            return FileInfo(
                path=str(file_path),
                size=0,
                mime_type='error'
            )
    
    def analyze_directory(self, dir_path: Path = None) -> DirectoryInfo:
        """分析目录"""
        if dir_path is None:
            dir_path = self.root_path
        
        if str(dir_path) in self.directory_cache:
            return self.directory_cache[str(dir_path)]
        
        total_size = 0
        file_count = 0
        subdirectory_count = 0
        files = []
        largest_file = None
        
        try:
            for item in dir_path.iterdir():
                if self.should_ignore(item):
                    continue
                
                if item.is_file():
                    file_info = self.get_file_info(item)
                    files.append(file_info)
                    total_size += file_info.size
                    file_count += 1
                    
                    if largest_file is None or file_info.size > largest_file.size:
                        largest_file = file_info
                
                elif item.is_dir():
                    subdirectory_count += 1
                    sub_info = self.analyze_directory(item)
                    total_size += sub_info.size
                    file_count += sub_info.file_count
                    subdirectory_count += sub_info.subdirectory_count
        
        except (OSError, PermissionError):
            pass
        
        directory_info = DirectoryInfo(
            path=str(dir_path),
            size=total_size,
            file_count=file_count,
            subdirectory_count=subdirectory_count,
            largest_file=largest_file,
            files=files
        )
        
        self.directory_cache[str(dir_path)] = directory_info
        return directory_info
    
    def find_large_files(self, min_size_mb: int = 10) -> List[FileInfo]:
        """查找大文件"""
        min_size_bytes = min_size_mb * 1024 * 1024
        large_files = []
        
        for file_info in self.file_cache.values():
            if file_info.size >= min_size_bytes:
                large_files.append(file_info)
        
        return sorted(large_files, key=lambda x: x.size, reverse=True)
    
    def find_duplicate_files(self) -> Dict[str, List[FileInfo]]:
        """查找重复文件"""
        hash_groups = defaultdict(list)
        
        for file_info in self.file_cache.values():
            if file_info.hash:  # 只检查有哈希值的文件
                hash_groups[file_info.hash].append(file_info)
        
        # 返回有重复的文件组
        duplicates = {
            hash_val: files 
            for hash_val, files in hash_groups.items() 
            if len(files) > 1
        }
        
        return duplicates
    
    def analyze_file_types(self) -> Dict[str, Dict]:
        """分析文件类型"""
        type_stats = defaultdict(lambda: {
            'count': 0,
            'total_size': 0,
            'avg_size': 0,
            'largest_file': None
        })
        
        for file_info in self.file_cache.values():
            mime_type = file_info.mime_type
            stats = type_stats[mime_type]
            
            stats['count'] += 1
            stats['total_size'] += file_info.size
            
            if (stats['largest_file'] is None or 
                file_info.size > stats['largest_file'].size):
                stats['largest_file'] = file_info
        
        # 计算平均大小
        for mime_type, stats in type_stats.items():
            if stats['count'] > 0:
                stats['avg_size'] = stats['total_size'] / stats['count']
        
        return dict(type_stats)
    
    def get_directory_tree(self, max_depth: int = 3) -> Dict:
        """获取目录树结构"""
        def build_tree(path: Path, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth or self.should_ignore(path):
                return {}
            
            try:
                children = []
                total_size = 0
                total_files = 0
                
                for item in sorted(path.iterdir()):
                    if self.should_ignore(item):
                        continue
                    
                    if item.is_file():
                        file_info = self.get_file_info(item)
                        total_size += file_info.size
                        total_files += 1
                        children.append({
                            'name': item.name,
                            'type': 'file',
                            'size': file_info.size,
                            'mime_type': file_info.mime_type
                        })
                    
                    elif item.is_dir():
                        subtree = build_tree(item, current_depth + 1)
                        if subtree:
                            children.append({
                                'name': item.name,
                                'type': 'directory',
                                'size': subtree.get('size', 0),
                                'file_count': subtree.get('file_count', 0),
                                'children': subtree.get('children', [])
                            })
                            total_size += subtree.get('size', 0)
                            total_files += subtree.get('file_count', 0)
                
                return {
                    'name': path.name,
                    'type': 'directory',
                    'size': total_size,
                    'file_count': total_files,
                    'children': children
                }
            
            except (OSError, PermissionError):
                return {}
        
        return build_tree(self.root_path)
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        # 分析根目录
        root_info = self.analyze_directory()
        
        # 查找大文件
        large_files = self.find_large_files()
        
        # 查找重复文件
        duplicates = self.find_duplicate_files()
        
        # 分析文件类型
        file_types = self.analyze_file_types()
        
        # 获取目录树
        directory_tree = self.get_directory_tree()
        
        # 计算统计信息
        total_files = len(self.file_cache)
        total_size = sum(f.size for f in self.file_cache.values())
        
        # 找出最大的文件类型
        largest_type = max(file_types.items(), 
                         key=lambda x: x[1]['total_size'])[0] if file_types else None
        
        report = {
            'summary': {
                'total_files': total_files,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'largest_type': largest_type,
                'duplicate_groups': len(duplicates),
                'large_files_count': len(large_files)
            },
            'large_files': [
                {
                    'path': f.path,
                    'size_mb': round(f.size / (1024 * 1024), 2),
                    'mime_type': f.mime_type,
                    'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f.modified_time))
                }
                for f in large_files[:20]  # 只显示前20个
            ],
            'duplicate_files': {
                hash_val: [
                    {
                        'path': f.path,
                        'size_mb': round(f.size / (1024 * 1024), 2),
                        'mime_type': f.mime_type
                    }
                    for f in files
                ]
                for hash_val, files in list(duplicates.items())[:10]  # 只显示前10组
            },
            'file_types': {
                mime_type: {
                    'count': stats['count'],
                    'total_size_mb': round(stats['total_size'] / (1024 * 1024), 2),
                    'avg_size_mb': round(stats['avg_size'] / (1024 * 1024), 2),
                    'largest_file': {
                        'path': stats['largest_file'].path,
                        'size_mb': round(stats['largest_file'].size / (1024 * 1024), 2)
                    } if stats['largest_file'] else None
                }
                for mime_type, stats in sorted(file_types.items(), 
                                            key=lambda x: x[1]['total_size'], 
                                            reverse=True)[:10]  # 只显示前10种类型
            },
            'directory_tree': directory_tree
        }
        
        return report
    
    def save_report(self, output_file: str = "file_analysis_report.json"):
        """保存报告到文件"""
        report = self.generate_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"报告已保存到: {output_file}")
        return report

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='文件分析器')
    parser.add_argument('path', nargs='?', default='.', help='要分析的路径')
    parser.add_argument('--min-size', type=int, default=10, help='大文件最小大小(MB)')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    
    args = parser.parse_args()
    
    analyzer = FileAnalyzer(args.path)
    
    # 分析目录
    print("正在分析文件...")
    directory_info = analyzer.analyze_directory()
    
    print(f"分析完成:")
    print(f"  总文件数: {directory_info.file_count}")
    print(f"  总大小: {directory_info.size / (1024*1024):.2f} MB")
    print(f"  子目录数: {directory_info.subdirectory_count}")
    
    if directory_info.largest_file:
        print(f"  最大文件: {directory_info.largest_file.path} ({directory_info.largest_file.size / (1024*1024):.2f} MB)")
    
    # 查找大文件
    large_files = analyzer.find_large_files(args.min_size)
    if large_files:
        print(f"\n大于 {args.min_size} MB 的文件:")
        for file_info in large_files[:10]:
            print(f"  {file_info.path} ({file_info.size / (1024*1024):.2f} MB)")
    
    # 查找重复文件
    duplicates = analyzer.find_duplicate_files()
    if duplicates:
        print(f"\n重复文件组: {len(duplicates)}")
        for hash_val, files in list(duplicates.items())[:5]:
            print(f"  哈希: {hash_val[:8]}...")
            for file_info in files:
                print(f"    {file_info.path}")
    
    # 保存报告
    if args.output or args.json:
        output_file = args.output or "file_analysis_report.json"
        analyzer.save_report(output_file)
```

### 自动文件清理工具

```bash
#!/bin/bash
# file-cleanup.sh - 自动文件清理脚本

set -e

# 配置
PROJECT_ROOT=${1:-"."}
MIN_SIZE_MB=${2:-50}
DRY_RUN=${3:-true}
LOG_FILE="file_cleanup.log"

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

# 检查路径是否存在
check_path() {
    if [ ! -d "$PROJECT_ROOT" ]; then
        log_error "路径不存在: $PROJECT_ROOT"
        exit 1
    fi
}

# 查找大文件
find_large_files() {
    log_step "查找大文件 (>${MIN_SIZE_MB}MB)..."
    
    local large_files_file="large_files.tmp"
    find "$PROJECT_ROOT" -type f -size "+${MIN_SIZE_MB}M" -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -not -path "*/dist/*" -not -path "*/build/*" > "$large_files_file"
    
    local count=$(wc -l < "$large_files_file")
    log_info "发现 $count 个大文件"
    
    if [ $count -gt 0 ]; then
        echo "大文件列表:"
        while IFS= read -r file; do
            local size=$(du -h "$file" | cut -f1)
            echo "  $size $file"
        done < "$large_files_file"
    fi
}

# 查找重复文件
find_duplicate_files() {
    log_step "查找重复文件..."
    
    local duplicates_file="duplicates.tmp"
    
    # 使用fdupes查找重复文件
    if command -v fdupes &> /dev/null; then
        fdupes -r "$PROJECT_ROOT" --noempty --suppressempty | grep -v "^$" > "$duplicates_file"
    else
        log_warn "fdupes未安装，跳过重复文件检查"
        return
    fi
    
    # 解析重复文件组
    local groups=0
    local current_group=""
    
    while IFS= read -r line; do
        if [[ "$line" != "$current_group" ]]; then
            if [ -n "$current_group" ]; then
                groups=$((groups + 1))
            fi
            current_group="$line"
        else
            echo "  重复: $line"
        fi
    done < "$duplicates_file"
    
    log_info "发现 $groups 组重复文件"
}

# 查找空目录
find_empty_directories() {
    log_step "查找空目录..."
    
    local empty_dirs_file="empty_dirs.tmp"
    find "$PROJECT_ROOT" -type d -empty -not -path "*/.git/*" > "$empty_dirs_file"
    
    local count=$(wc -l < "$empty_dirs_file")
    log_info "发现 $count 个空目录"
    
    if [ $count -gt 0 ]; then
        echo "空目录列表:"
        while IFS= read -r dir; do
            echo "  $dir"
        done < "$empty_dirs_file"
    fi
}

# 查找临时文件
find_temp_files() {
    log_step "查找临时文件..."
    
    local temp_patterns=(
        "*.tmp"
        "*.temp"
        "*.swp"
        "*.swo"
        "*~"
        ".#*"
        "#*#"
        "*.log"
        "*.bak"
        "*.backup"
        ".DS_Store"
        "Thumbs.db"
    )
    
    local temp_files_file="temp_files.tmp"
    > "$temp_files_file"
    
    for pattern in "${temp_patterns[@]}"; do
        find "$PROJECT_ROOT" -name "$pattern" -not -path "*/.git/*" >> "$temp_files_file"
    done
    
    local count=$(wc -l < "$temp_files_file")
    log_info "发现 $count 个临时文件"
    
    if [ $count -gt 0 ]; then
        echo "临时文件列表:"
        while IFS= read -r file; do
            echo "  $file"
        done < "$temp_files_file"
    fi
}

# 清理文件
cleanup_files() {
    if [ "$DRY_RUN" = "true" ]; then
        log_warn "这是试运行模式，不会实际删除文件"
        return
    fi
    
    log_step "开始清理文件..."
    
    # 清理大文件 (需要确认)
    if [ -f "large_files.tmp" ] && [ -s "large_files.tmp" ]; then
        echo "发现大文件，是否删除？(y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            while IFS= read -r file; do
                if [ -f "$file" ]; then
                    rm "$file"
                    log_info "已删除: $file"
                fi
            done < "large_files.tmp"
        fi
    fi
    
    # 清理重复文件 (保留第一个)
    if [ -f "duplicates.tmp" ] && [ -s "duplicates.tmp" ]; then
        log_info "清理重复文件 (保留每组第一个)..."
        python3 -c "
import sys
current_group = []
for line in open('duplicates.tmp'):
    line = line.strip()
    if not line:
        continue
    if line.startswith('$PROJECT_ROOT'):
        if current_group:
            # 删除除第一个外的所有文件
            for file in current_group[1:]:
                try:
                    import os
                    os.remove(file)
                    print(f'已删除: {file}')
                except:
                    pass
        current_group = [line]
    else:
        current_group.append(line)
# 处理最后一组
if current_group and len(current_group) > 1:
    for file in current_group[1:]:
        try:
            import os
            os.remove(file)
            print(f'已删除: {file}')
        except:
            pass
"
    fi
    
    # 清理空目录
    if [ -f "empty_dirs.tmp" ] && [ -s "empty_dirs.tmp" ]; then
        while IFS= read -r dir; do
            if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
                rmdir "$dir"
                log_info "已删除空目录: $dir"
            fi
        done < "empty_dirs.tmp"
    fi
    
    # 清理临时文件
    if [ -f "temp_files.tmp" ] && [ -s "temp_files.tmp" ]; then
        while IFS= read -r file; do
            if [ -f "$file" ]; then
                rm "$file"
                log_info "已删除临时文件: $file"
            fi
        done < "temp_files.tmp"
    fi
}

# 生成清理报告
generate_cleanup_report() {
    log_step "生成清理报告..."
    
    local report_file="cleanup_report.json"
    
    # 计算清理前后的统计信息
    local before_size=$(du -sm "$PROJECT_ROOT" | cut -f1)
    
    python3 -c "
import json
import os
import subprocess
from pathlib import Path

project_root = '$PROJECT_ROOT'
report_file = '$report_file'

# 获取项目统计信息
def get_project_stats():
    result = subprocess.run(['du', '-sm', project_root], capture_output=True, text=True)
    size_mb = int(result.stdout.strip().split()[0])
    
    file_count = 0
    for root, dirs, files in os.walk(project_root):
        file_count += len(files)
    
    return {
        'size_mb': size_mb,
        'file_count': file_count
    }

# 生成报告
report = {
    'cleanup_time': '$(date -Iseconds)',
    'project_root': project_root,
    'before': get_project_stats(),
    'actions_performed': []
}

# 添加清理动作
if os.path.exists('large_files.tmp'):
    with open('large_files.tmp') as f:
        large_files = [line.strip() for line in f if line.strip()]
    if large_files:
        report['actions_performed'].append({
            'type': 'large_files_found',
            'count': len(large_files),
            'files': large_files[:10]  # 只记录前10个
        })

if os.path.exists('duplicates.tmp'):
    with open('duplicates.tmp') as f:
        content = f.read().strip()
    duplicate_groups = len([group for group in content.split('\n\n') if group.strip()])
    if duplicate_groups > 0:
        report['actions_performed'].append({
            'type': 'duplicate_files_found',
            'groups': duplicate_groups
        })

if os.path.exists('empty_dirs.tmp'):
    with open('empty_dirs.tmp') as f:
        empty_dirs = [line.strip() for line in f if line.strip()]
    if empty_dirs:
        report['actions_performed'].append({
            'type': 'empty_directories_found',
            'count': len(empty_dirs)
        })

if os.path.exists('temp_files.tmp'):
    with open('temp_files.tmp') as f:
        temp_files = [line.strip() for line in f if line.strip()]
    if temp_files:
        report['actions_performed'].append({
            'type': 'temp_files_found',
            'count': len(temp_files)
        })

# 如果不是试运行，计算清理后的统计
if '$DRY_RUN' == 'false':
    report['after'] = get_project_stats()
    report['size_saved_mb'] = report['before']['size_mb'] - report['after']['size_mb']
    report['files_removed'] = report['before']['file_count'] - report['after']['file_count']

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f'报告已保存到: {report_file}')
"
    
    log_info "清理报告已生成: $report_file"
}

# 清理临时文件
cleanup_temp_files() {
    rm -f large_files.tmp duplicates.tmp empty_dirs.tmp temp_files.tmp
}

# 主函数
main() {
    log_info "开始文件清理分析..."
    log_info "项目路径: $PROJECT_ROOT"
    log_info "最小文件大小: ${MIN_SIZE_MB}MB"
    log_info "试运行模式: $DRY_RUN"
    
    # 检查路径
    check_path
    
    # 执行各种分析
    find_large_files
    find_duplicate_files
    find_empty_directories
    find_temp_files
    
    # 清理文件
    cleanup_files
    
    # 生成报告
    generate_cleanup_report
    
    # 清理临时文件
    cleanup_temp_files
    
    log_info "文件清理完成！"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [project_path] [min_size_mb] [dry_run]"
    echo ""
    echo "参数:"
    echo "  project_path  项目路径，默认: ."
    echo "  min_size_mb   大文件最小大小(MB)，默认: 50"
    echo "  dry_run       是否试运行 (true|false)，默认: true"
    echo ""
    echo "示例:"
    echo "  $0 . 10 true    # 试运行，查找大于10MB的文件"
    echo "  $0 ./myproject 5 false  # 实际清理，查找大于5MB的文件"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### 文件监控工具

```python
#!/usr/bin/env python3
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import queue

@dataclass
class FileChangeEvent:
    """文件变更事件"""
    event_type: str  # created, modified, deleted, moved
    file_path: str
    timestamp: float
    file_size: int = 0
    file_hash: str = ""

class FileMonitor:
    """文件监控器"""
    
    def __init__(self, watch_path: str = "."):
        self.watch_path = Path(watch_path)
        self.file_states: Dict[str, Dict] = {}
        self.events: List[FileChangeEvent] = []
        self.is_running = False
        self.event_queue = queue.Queue()
        self.ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.vscode', 
            '.idea', 'dist', 'build', '.next', 'coverage'
        }
    
    def should_ignore(self, path: Path) -> bool:
        """判断是否应该忽略文件"""
        parts = path.parts
        return any(part in self.ignore_patterns for part in parts)
    
    def get_file_state(self, file_path: Path) -> Dict:
        """获取文件状态"""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'exists': True
            }
        except (OSError, FileNotFoundError):
            return {'exists': False}
    
    def scan_directory(self) -> Dict[str, Dict]:
        """扫描目录获取当前文件状态"""
        current_states = {}
        
        for root, dirs, files in os.walk(self.watch_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            for file_name in files:
                file_path = Path(root) / file_name
                if not self.should_ignore(file_path):
                    current_states[str(file_path)] = self.get_file_state(file_path)
        
        return current_states
    
    def detect_changes(self, old_states: Dict[str, Dict], new_states: Dict[str, Dict]):
        """检测文件变更"""
        current_time = time.time()
        
        # 检测新文件
        for file_path, state in new_states.items():
            if file_path not in old_states and state['exists']:
                event = FileChangeEvent(
                    event_type='created',
                    file_path=file_path,
                    timestamp=current_time,
                    file_size=state['size']
                )
                self.event_queue.put(event)
        
        # 检测删除的文件
        for file_path, state in old_states.items():
            if file_path not in new_states:
                event = FileChangeEvent(
                    event_type='deleted',
                    file_path=file_path,
                    timestamp=current_time
                )
                self.event_queue.put(event)
        
        # 检测修改的文件
        for file_path, new_state in new_states.items():
            if file_path in old_states:
                old_state = old_states[file_path]
                if (old_state['exists'] and new_state['exists'] and 
                    (old_state['size'] != new_state['size'] or 
                     old_state['mtime'] != new_state['mtime'])):
                    event = FileChangeEvent(
                        event_type='modified',
                        file_path=file_path,
                        timestamp=current_time,
                        file_size=new_state['size']
                    )
                    self.event_queue.put(event)
    
    def monitor_loop(self, interval: float = 1.0):
        """监控循环"""
        self.is_running = True
        
        # 初始扫描
        self.file_states = self.scan_directory()
        print(f"开始监控 {self.watch_path}，发现 {len(self.file_states)} 个文件")
        
        while self.is_running:
            try:
                # 扫描当前状态
                current_states = self.scan_directory()
                
                # 检测变更
                self.detect_changes(self.file_states, current_states)
                
                # 更新状态
                self.file_states = current_states
                
                # 处理事件队列
                while not self.event_queue.empty():
                    try:
                        event = self.event_queue.get_nowait()
                        self.events.append(event)
                        self.handle_event(event)
                    except queue.Empty:
                        break
                
                time.sleep(interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(interval)
    
    def handle_event(self, event: FileChangeEvent):
        """处理文件变更事件"""
        timestamp = datetime.fromtimestamp(event.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        if event.event_type == 'created':
            size_mb = event.file_size / (1024 * 1024)
            print(f"[{timestamp}] 创建: {event.file_path} ({size_mb:.2f} MB)")
        
        elif event.event_type == 'deleted':
            print(f"[{timestamp}] 删除: {event.file_path}")
        
        elif event.event_type == 'modified':
            size_mb = event.file_size / (1024 * 1024)
            print(f"[{timestamp}] 修改: {event.file_path} ({size_mb:.2f} MB)")
    
    def start_monitoring(self, interval: float = 1.0):
        """开始监控"""
        if self.is_running:
            print("监控已在运行中")
            return
        
        monitor_thread = threading.Thread(
            target=self.monitor_loop,
            args=(interval,),
            daemon=True
        )
        monitor_thread.start()
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            print("\n停止监控...")
            self.is_running = False
            monitor_thread.join()
    
    def get_events_summary(self) -> Dict:
        """获取事件摘要"""
        if not self.events:
            return {'total': 0, 'by_type': {}, 'recent': []}
        
        # 按类型统计
        by_type = {}
        for event in self.events:
            event_type = event.event_type
            if event_type not in by_type:
                by_type[event_type] = 0
            by_type[event_type] += 1
        
        # 最近的事件
        recent = [asdict(event) for event in sorted(self.events, key=lambda x: x.timestamp, reverse=True)[:10]]
        
        return {
            'total': len(self.events),
            'by_type': by_type,
            'recent': recent
        }
    
    def save_events(self, filename: str = "file_monitor_events.json"):
        """保存事件到文件"""
        events_data = [asdict(event) for event in self.events]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)
        
        print(f"事件已保存到: {filename}")

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='文件监控器')
    parser.add_argument('path', nargs='?', default='.', help='监控路径')
    parser.add_argument('--interval', type=float, default=1.0, help='检查间隔(秒)')
    parser.add_argument('--output', help='输出事件文件')
    
    args = parser.parse_args()
    
    monitor = FileMonitor(args.path)
    
    try:
        monitor.start_monitoring(args.interval)
    finally:
        if args.output:
            monitor.save_events(args.output)
        
        summary = monitor.get_events_summary()
        print(f"\n监控摘要:")
        print(f"  总事件数: {summary['total']}")
        print(f"  按类型统计: {summary['by_type']}")
```

## 最佳实践

### 文件组织
- **合理分类**: 按功能和类型组织文件
- **命名规范**: 使用一致的文件命名规范
- **目录结构**: 保持合理的目录层次
- **版本控制**: 正确配置.gitignore文件

### 存储优化
- **定期清理**: 定期清理无用文件
- **压缩存储**: 对大文件进行压缩
- **归档策略**: 建立文件归档策略
- **监控告警**: 设置存储空间监控

### 自动化管理
- **脚本自动化**: 使用脚本自动清理
- **定期任务**: 设置定期清理任务
- **监控工具**: 使用工具监控文件变化
- **报告生成**: 定期生成分析报告

### 团队协作
- **规范制定**: 制定文件管理规范
- **培训指导**: 培训团队成员
- **工具共享**: 共享有用的工具
- **经验分享**: 分享最佳实践

## 相关技能

- [Git工作流管理](./git-workflows/) - 文件版本控制
- [Docker Compose编排](./docker-compose/) - 容器文件管理
- [代码格式化](./code-formatter/) - 代码文件规范
- [安全扫描器](./security-scanner/) - 文件安全检查

**构建 Art如果一个cts 在 Reposit或y**
- `节点_模块s` (500MB+)
- `d是t/` 或 `构建/` folders
- `.next/` direct或y
- P一个ck一个ge 锁s 那个 ch一个ge c在st一个tly

**Duplic在e Files**
- S一个me file 在 multiple loc在i在s
- D如果ferent n一个mes, s一个me c在tent
- De一个d 代码 br一个ches

**Unnecess一个ry Files**
- 备份 files (.b一个k, .备份)
- Temp或一个ry files (.tmp)
- 日志 files (.日志)
- IDE sett在gs (.vs代码, .ide一个)

## 验证检查清单

- [ ] Underst和 什么 files you h一个ve
- [ ] Know 为什么 e一个ch l一个rge file ex是ts
- [ ] No 构建 一个rt如果一个cts 在 source c在trol
- [ ] Duplic在es ident如果ied 和 resolved
- [ ] .gitign或e excludes temp或一个ry files
- [ ] Reposit或y size 是 re作为在一个ble

## 相关技能
- **代码-re视图** - Re视图 file 或g一个iz在i在
- **安全-sc一个ner** - 检查 对于 exposed files
- **git-一个一个lys是** - F在d l一个rge commits
