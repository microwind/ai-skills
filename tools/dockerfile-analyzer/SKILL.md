---
name: Dockerfile分析器
description: "当分析Dockerfile时，检查最佳实践，优化Docker配置，验证安全性。分析Dockerfile以优化和安全。"
license: MIT
---

# Dockerfile分析器技能

## 概述

Docker镜像可能膨胀到GB级别且存在安全隐患。无效的Dockerfile会导致构建失败或创建不安全的容器。在构建和部署前必须进行分析。

**核心原则**: 轻量镜像构建速度快，安全镜像值得信赖。好的Dockerfile应该层次清晰、安全性高、体积小、构建快。

## 何时使用

**始终:**
- 构建生产镜像前
- 优化镜像大小时
- 检查安全实践时
- 改进构建性能时
- 审查团队Dockerfile时

**触发短语:**
- "这个Dockerfile好吗？"
- "让镜像更小"
- "检查Docker最佳实践"
- "这安全吗？"
- "为什么这么大？"
- "优化Dockerfile"

## Dockerfile分析器技能功能

### 最佳实践检查
- 多阶段构建验证
- 基础镜像选择检查
- 层次优化分析
- 缓存优化建议
- 安全用户配置
- 环境变量管理

### 安全性分析
- 漏洞扫描
- 权限检查
- 敏感信息检测
- 网络安全验证
- 文件系统安全
- 运行时安全

### 性能优化
- 镜像大小分析
- 构建时间优化
- 层次缓存优化
- 依赖管理
- 启动时间优化
- 资源使用优化

### 质量评估
- 代码质量检查
- 维护性评估
- 可读性分析
- 标准合规性
- 文档完整性
- 版本管理

## 常见问题

**❌ 镜像过大**
- 使用过大基础镜像
- 包含不必要文件
- 层次过多
- 未使用多阶段构建

**❌ 安全隐患**
- 使用root用户运行
- 敏感信息泄露
- 未更新基础镜像
- 开放过多端口

**❌ 构建缓慢**
- 层次缓存失效
- 依赖安装顺序不当
- 频繁重建
- 网络下载过多

**❌ 维护困难**
- 缺少文档说明
- 版本管理混乱
- 配置硬编码
- 环境依赖复杂

## 代码示例

### Dockerfile分析器

```python
#!/usr/bin/env python3
import re
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    """严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class DockerfileIssue:
    """Dockerfile问题"""
    line_number: int
    severity: Severity
    rule: str
    message: str
    suggestion: str
    line_content: str

@dataclass
class LayerInfo:
    """层次信息"""
    instruction: str
    content: str
    estimated_size: int
    cache_hit: bool = False

class DockerfileAnalyzer:
    """Dockerfile分析器"""
    
    def __init__(self):
        self.issues: List[DockerfileIssue] = []
        self.layers: List[LayerInfo] = []
        self.security_rules = self._load_security_rules()
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_security_rules(self) -> Dict[str, Dict]:
        """加载安全规则"""
        return {
            'no_root_user': {
                'pattern': r'USER\s+(?!root)',
                'message': '应该使用非root用户运行容器',
                'severity': Severity.ERROR,
                'suggestion': '添加 USER 指令指定非root用户'
            },
            'no_secrets': {
                'pattern': r'(PASSWORD|SECRET|TOKEN|KEY)\s*=',
                'message': '检测到可能的敏感信息泄露',
                'severity': Severity.CRITICAL,
                'suggestion': '使用环境变量或密钥管理系统'
            },
            'update_packages': {
                'pattern': r'RUN\s+.*apt-get\s+update',
                'message': '应该更新包缓存并清理',
                'severity': Severity.WARNING,
                'suggestion': '使用 apt-get update && apt-get install -y && apt-get clean'
            },
            'specific_tag': {
                'pattern': r'FROM\s+[^:]+:(latest|latest)',
                'message': '不应该使用latest标签',
                'severity': Severity.ERROR,
                'suggestion': '使用具体的版本标签'
            },
            'minimize_layers': {
                'pattern': r'RUN\s+.*&&.*&&',
                'message': '可以合并多个RUN指令以减少层次',
                'severity': Severity.INFO,
                'suggestion': '使用 && 合并多个命令'
            }
        }
    
    def _load_optimization_rules(self) -> Dict[str, Dict]:
        """加载优化规则"""
        return {
            'multi_stage': {
                'pattern': r'FROM\s+.*\s+AS\s+\w+',
                'message': '建议使用多阶段构建',
                'severity': Severity.INFO,
                'suggestion': '使用多阶段构建减少最终镜像大小'
            },
            'copy_order': {
                'pattern': r'COPY\s+.*\s+.*\s+.*',
                'message': '应该先复制依赖文件，再复制源代码',
                'severity': Severity.WARNING,
                'suggestion': '优化COPY顺序以利用缓存'
            },
            'npm_cache': {
                'pattern': r'RUN\s+npm\s+install',
                'message': '应该利用npm缓存',
                'severity': Severity.INFO,
                'suggestion': '先复制package.json，运行npm install，再复制源代码'
            },
            'apt_clean': {
                'pattern': r'RUN\s+.*apt-get.*install.*(?<!apt-get clean)',
                'message': '安装包后应该清理缓存',
                'severity': Severity.WARNING,
                'suggestion': '添加 apt-get clean && rm -rf /var/lib/apt/lists/*'
            }
        }
    
    def parse_dockerfile(self, dockerfile_path: str) -> List[Tuple[str, int]]:
        """解析Dockerfile"""
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            instructions = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 处理多行指令
                    if line.endswith('\\'):
                        # 多行指令开始
                        multi_line = line[:-1]
                        j = i
                        while j < len(lines):
                            next_line = lines[j].strip()
                            if next_line.endswith('\\'):
                                multi_line += ' ' + next_line[:-1]
                                j += 1
                            else:
                                multi_line += ' ' + next_line
                                break
                        instructions.append((multi_line, i))
                        i = j
                    else:
                        instructions.append((line, i))
            
            return instructions
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Dockerfile不存在: {dockerfile_path}")
        except Exception as e:
            raise Exception(f"解析Dockerfile失败: {e}")
    
    def analyze_security(self, instructions: List[Tuple[str, int]]):
        """安全性分析"""
        for instruction, line_num in instructions:
            for rule_name, rule in self.security_rules.items():
                if re.search(rule['pattern'], instruction, re.IGNORECASE):
                    issue = DockerfileIssue(
                        line_number=line_num,
                        severity=rule['severity'],
                        rule=rule_name,
                        message=rule['message'],
                        suggestion=rule['suggestion'],
                        line_content=instruction
                    )
                    self.issues.append(issue)
    
    def analyze_optimization(self, instructions: List[Tuple[str, int]]):
        """优化分析"""
        for instruction, line_num in instructions:
            for rule_name, rule in self.optimization_rules.items():
                if re.search(rule['pattern'], instruction, re.IGNORECASE):
                    issue = DockerfileIssue(
                        line_number=line_num,
                        severity=rule['severity'],
                        rule=rule_name,
                        message=rule['message'],
                        suggestion=rule['suggestion'],
                        line_content=instruction
                    )
                    self.issues.append(issue)
    
    def analyze_layers(self, instructions: List[Tuple[str, int]]):
        """分析层次"""
        self.layers = []
        
        for instruction, line_num in instructions:
            # 提取指令类型
            parts = instruction.split(None, 1)
            if len(parts) >= 2:
                cmd_type = parts[0].upper()
                content = parts[1]
                
                # 估算层次大小
                estimated_size = self._estimate_layer_size(cmd_type, content)
                
                layer = LayerInfo(
                    instruction=cmd_type,
                    content=content,
                    estimated_size=estimated_size
                )
                
                self.layers.append(layer)
    
    def _estimate_layer_size(self, cmd_type: str, content: str) -> int:
        """估算层次大小"""
        if cmd_type == 'FROM':
            return 500 * 1024 * 1024  # 基础镜像约500MB
        elif cmd_type == 'COPY' or cmd_type == 'ADD':
            return 10 * 1024 * 1024   # 复制文件约10MB
        elif cmd_type == 'RUN':
            if 'apt-get install' in content:
                return 100 * 1024 * 1024  # 安装包约100MB
            elif 'npm install' in content:
                return 50 * 1024 * 1024   # npm包约50MB
            else:
                return 5 * 1024 * 1024    # 其他命令约5MB
        else:
            return 1 * 1024 * 1024     # 其他指令约1MB
    
    def calculate_image_size(self) -> int:
        """计算镜像大小"""
        return sum(layer.estimated_size for layer in self.layers)
    
    def suggest_optimizations(self) -> List[str]:
        """建议优化方案"""
        suggestions = []
        
        # 分析层次大小
        total_size = self.calculate_image_size()
        if total_size > 1024 * 1024 * 1024:  # > 1GB
            suggestions.append("镜像过大，考虑使用多阶段构建")
        
        # 分析RUN指令
        run_instructions = [layer for layer in self.layers if layer.instruction == 'RUN']
        if len(run_instructions) > 5:
            suggestions.append("合并RUN指令以减少层次数量")
        
        # 分析COPY指令
        copy_instructions = [layer for layer in self.layers if layer.instruction == 'COPY']
        if len(copy_instructions) > 3:
            suggestions.append("优化COPY指令顺序以利用缓存")
        
        # 检查基础镜像
        if self.layers and 'alpine' not in self.layers[0].content.lower():
            suggestions.append("考虑使用Alpine Linux作为基础镜像")
        
        return suggestions
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        # 按严重程度分组问题
        issues_by_severity = {}
        for severity in Severity:
            issues_by_severity[severity.value] = [
                {
                    'line_number': issue.line_number,
                    'rule': issue.rule,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'line_content': issue.line_content
                }
                for issue in self.issues if issue.severity == severity
            ]
        
        # 统计信息
        total_issues = len(self.issues)
        critical_issues = len(issues_by_severity['critical'])
        error_issues = len(issues_by_severity['error'])
        warning_issues = len(issues_by_severity['warning'])
        info_issues = len(issues_by_severity['info'])
        
        # 层次分析
        layer_analysis = {
            'total_layers': len(self.layers),
            'estimated_size_mb': round(self.calculate_image_size() / (1024 * 1024), 2),
            'layers': [
                {
                    'instruction': layer.instruction,
                    'estimated_size_mb': round(layer.estimated_size / (1024 * 1024), 2)
                }
                for layer in self.layers
            ]
        }
        
        # 优化建议
        optimizations = self.suggest_optimizations()
        
        return {
            'summary': {
                'total_issues': total_issues,
                'critical_issues': critical_issues,
                'error_issues': error_issues,
                'warning_issues': warning_issues,
                'info_issues': info_issues,
                'estimated_size_mb': round(self.calculate_image_size() / (1024 * 1024), 2)
            },
            'issues_by_severity': issues_by_severity,
            'layer_analysis': layer_analysis,
            'optimizations': optimizations
        }
    
    def analyze(self, dockerfile_path: str) -> Dict:
        """完整分析Dockerfile"""
        self.issues = []
        self.layers = []
        
        # 解析Dockerfile
        instructions = self.parse_dockerfile(dockerfile_path)
        
        # 执行各种分析
        self.analyze_security(instructions)
        self.analyze_optimization(instructions)
        self.analyze_layers(instructions)
        
        # 生成报告
        return self.generate_report()

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Dockerfile分析器')
    parser.add_argument('dockerfile', nargs='?', default='Dockerfile', help='Dockerfile路径')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    analyzer = DockerfileAnalyzer()
    
    try:
        report = analyzer.analyze(args.dockerfile)
        
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
            print("Dockerfile分析报告")
            print("=" * 50)
            
            # 摘要
            summary = report['summary']
            print(f"总问题数: {summary['total_issues']}")
            print(f"严重问题: {summary['critical_issues']}")
            print(f"错误问题: {summary['error_issues']}")
            print(f"警告问题: {summary['warning_issues']}")
            print(f"信息问题: {summary['info_issues']}")
            print(f"估计大小: {summary['estimated_size_mb']} MB")
            print()
            
            # 严重问题
            if report['issues_by_severity']['critical']:
                print("🚨 严重问题:")
                for issue in report['issues_by_severity']['critical']:
                    print(f"  行 {issue['line_number']}: {issue['message']}")
                    print(f"    建议: {issue['suggestion']}")
                    print()
            
            # 错误问题
            if report['issues_by_severity']['error']:
                print("❌ 错误问题:")
                for issue in report['issues_by_severity']['error']:
                    print(f"  行 {issue['line_number']}: {issue['message']}")
                    print(f"    建议: {issue['suggestion']}")
                    print()
            
            # 警告问题
            if report['issues_by_severity']['warning']:
                print("⚠️ 警告问题:")
                for issue in report['issues_by_severity']['warning']:
                    print(f"  行 {issue['line_number']}: {issue['message']}")
                    print(f"    建议: {issue['suggestion']}")
                    print()
            
            # 优化建议
            if report['optimizations']:
                print("💡 优化建议:")
                for suggestion in report['optimizations']:
                    print(f"  - {suggestion}")
                print()
            
            # 层次分析
            layer_analysis = report['layer_analysis']
            print(f"📊 层次分析:")
            print(f"  总层次数: {layer_analysis['total_layers']}")
            print(f"  估计大小: {layer_analysis['estimated_size_mb']} MB")
            
    except Exception as e:
        print(f"分析失败: {e}")
        exit(1)
```

### Dockerfile优化工具

```bash
#!/bin/bash
# dockerfile-optimizer.sh - Dockerfile优化工具

set -e

# 配置
DOCKERFILE=${1:-"Dockerfile"}
OUTPUT_FILE=${2:-"Dockerfile.optimized"}
BACKUP_FILE="Dockerfile.backup"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查Dockerfile是否存在
check_dockerfile() {
    if [ ! -f "$DOCKERFILE" ]; then
        log_error "Dockerfile不存在: $DOCKERFILE"
        exit 1
    fi
    
    log_info "分析Dockerfile: $DOCKERFILE"
}

# 备份原始文件
backup_original() {
    if [ ! -f "$BACKUP_FILE" ]; then
        cp "$DOCKERFILE" "$BACKUP_FILE"
        log_info "已备份原始文件到: $BACKUP_FILE"
    fi
}

# 优化基础镜像
optimize_base_image() {
    log_step "优化基础镜像..."
    
    # 检查是否使用latest标签
    if grep -q "FROM.*:latest" "$DOCKERFILE"; then
        log_warn "检测到latest标签，建议使用具体版本"
        
        # 尝试获取最新稳定版本
        if grep -q "FROM.*node:latest" "$DOCKERFILE"; then
            sed -i.bak 's/FROM.*node:latest/FROM node:18-alpine/g' "$DOCKERFILE"
            log_info "已将Node.js更新为18-alpine"
        elif grep -q "FROM.*python:latest" "$DOCKERFILE"; then
            sed -i.bak 's/FROM.*python:latest/FROM python:3.11-slim/g' "$DOCKERFILE"
            log_info "已将Python更新为3.11-slim"
        fi
    fi
    
    # 检查是否可以使用Alpine版本
    if grep -q "FROM.*ubuntu" "$DOCKERFILE" && ! grep -q "alpine" "$DOCKERFILE"; then
        log_warn "建议使用Alpine Linux以减小镜像大小"
    fi
}

# 优化RUN指令
optimize_run_commands() {
    log_step "优化RUN指令..."
    
    # 创建临时文件
    temp_file=$(mktemp)
    
    # 处理apt-get命令
    awk '
    /^RUN/ && /apt-get/ {
        # 检查是否已经包含clean
        if (!/apt-get clean/ && !/rm -rf \/var\/lib\/apt\/lists\//) {
            # 添加清理命令
            gsub(/RUN\s+apt-get install -y/, "RUN apt-get update && apt-get install -y")
            $0 = $0 " && apt-get clean && rm -rf /var/lib/apt/lists/*"
        }
    }
    { print }
    ' "$DOCKERFILE" > "$temp_file"
    
    mv "$temp_file" "$DOCKERFILE"
    
    # 合并连续的RUN指令
    python3 -c "
import re

with open('$DOCKERFILE', 'r') as f:
    content = f.read()

# 合并连续的RUN指令
lines = content.split('\n')
result = []
run_buffer = []

for line in lines:
    if line.strip().startswith('RUN'):
        run_buffer.append(line)
    else:
        if run_buffer:
            # 合并RUN指令
            if len(run_buffer) > 1:
                merged_run = 'RUN ' + ' && '.join([
                    line.replace('RUN', '').strip() 
                    for line in run_buffer
                ])
                result.append(merged_run)
            else:
                result.extend(run_buffer)
            run_buffer = []
        result.append(line)

# 处理最后的RUN缓冲
if run_buffer:
    if len(run_buffer) > 1:
        merged_run = 'RUN ' + ' && '.join([
            line.replace('RUN', '').strip() 
            for line in run_buffer
        ])
        result.append(merged_run)
    else:
        result.extend(run_buffer)

with open('$DOCKERFILE', 'w') as f:
    f.write('\n'.join(result))
"
    
    log_info "已优化RUN指令"
}

# 优化COPY指令
optimize_copy_commands() {
    log_step "优化COPY指令..."
    
    # 检查COPY顺序
    if grep -q "COPY.*\." "$DOCKERFILE" && grep -q "package.json" "$DOCKERFILE"; then
        log_warn "建议先复制package.json，再复制源代码以利用缓存"
    fi
    
    # 检查是否应该使用.dockerignore
    if [ ! -f ".dockerignore" ]; then
        log_warn "建议创建.dockerignore文件"
        cat > .dockerignore << EOF
.git
.gitignore
README.md
Dockerfile
.dockerignore
node_modules
npm-debug.log
coverage
.nyc_output
.cache
dist
build
EOF
        log_info "已创建.dockerignore文件"
    fi
}

# 添加安全配置
add_security_config() {
    log_step "添加安全配置..."
    
    # 检查是否有非root用户
    if ! grep -q "USER.*[a-zA-Z]" "$DOCKERFILE"; then
        log_warn "建议添加非root用户"
        
        # 在文件末尾添加用户配置
        echo "" >> "$DOCKERFILE"
        echo "# 创建非root用户" >> "$DOCKERFILE"
        echo "RUN groupadd -r appuser && useradd -r -g appuser appuser" >> "$DOCKERFILE"
        echo "USER appuser" >> "$DOCKERFILE"
        
        log_info "已添加非root用户配置"
    fi
    
    # 检查工作目录
    if ! grep -q "WORKDIR" "$DOCKERFILE"; then
        log_warn "建议设置工作目录"
        sed -i '/FROM.*/a WORKDIR /app' "$DOCKERFILE"
        log_info "已添加工作目录"
    fi
}

# 优化多阶段构建
optimize_multi_stage() {
    log_step "检查多阶段构建..."
    
    # 检查是否已经是多阶段构建
    if ! grep -q "AS.*" "$DOCKERFILE"; then
        # 检查是否需要多阶段构建
        if grep -q "npm\|yarn\|go build\|mvn package\|gradle build" "$DOCKERFILE"; then
            log_warn "建议使用多阶段构建"
            
            # 为Node.js项目创建多阶段构建示例
            if grep -q "node\|npm" "$DOCKERFILE"; then
                log_info "为Node.js项目创建多阶段构建示例"
                cat > Dockerfile.multi-stage << 'EOF'
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 运行阶段
FROM node:18-alpine AS runtime
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
USER nextjs
EXPOSE 3000
CMD ["npm", "start"]
EOF
                log_info "已创建多阶段构建示例: Dockerfile.multi-stage"
            fi
        fi
    else
        log_info "已使用多阶段构建"
    fi
}

# 生成优化报告
generate_optimization_report() {
    log_step "生成优化报告..."
    
    local report_file="dockerfile_optimization_report.md"
    
    cat > "$report_file" << EOF
# Dockerfile优化报告

## 原始文件分析
- 文件名: $DOCKERFILE
- 文件大小: $(du -h "$DOCKERFILE" | cut -f1)
- 行数: $(wc -l < "$DOCKERFILE")

## 优化项目
EOF
    
    # 检查各项优化
    if grep -q "FROM.*:latest" "$BACKUP_FILE"; then
        echo "- ✅ 移除latest标签" >> "$report_file"
    fi
    
    if grep -q "apt-get clean" "$DOCKERFILE"; then
        echo "- ✅ 添加apt-get清理" >> "$report_file"
    fi
    
    if grep -q "USER.*[a-zA-Z]" "$DOCKERFILE"; then
        echo "- ✅ 添加非root用户" >> "$report_file"
    fi
    
    if [ -f ".dockerignore" ]; then
        echo "- ✅ 创建.dockerignore文件" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## 建议进一步优化" >> "$report_file"
    echo "- 使用Alpine Linux作为基础镜像" >> "$report_file"
    echo "- 优化COPY指令顺序" >> "$report_file"
    echo "- 使用多阶段构建" >> "$report_file"
    echo "- 定期更新基础镜像" >> "$report_file"
    
    log_info "优化报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始Dockerfile优化..."
    
    # 检查和备份
    check_dockerfile
    backup_original
    
    # 执行优化
    optimize_base_image
    optimize_run_commands
    optimize_copy_commands
    add_security_config
    optimize_multi_stage
    
    # 生成报告
    generate_optimization_report
    
    log_info "Dockerfile优化完成！"
    log_info "优化后的文件: $DOCKERFILE"
    log_info "原始备份: $BACKUP_FILE"
    
    # 显示对比
    echo ""
    echo "文件大小对比:"
    echo "  原始: $(du -h "$BACKUP_FILE" | cut -f1)"
    echo "  优化后: $(du -h "$DOCKERFILE" | cut -f1)"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [dockerfile] [output_file]"
    echo ""
    echo "参数:"
    echo "  dockerfile   Dockerfile路径，默认: Dockerfile"
    echo "  output_file  输出文件路径，默认: Dockerfile.optimized"
    echo ""
    echo "示例:"
    echo "  $0 Dockerfile Dockerfile.new"
    echo "  $0 ./path/to/Dockerfile"
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    exit 0
fi

main "$@"
```

### Dockerfile安全扫描器

```python
#!/usr/bin/env python3
import re
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class VulnerabilityLevel(Enum):
    """漏洞等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityIssue:
    """安全问题"""
    type: str
    level: VulnerabilityLevel
    description: str
    recommendation: str
    cve_id: Optional[str] = None
    package: Optional[str] = None
    version: Optional[str] = None

class DockerSecurityScanner:
    """Docker安全扫描器"""
    
    def __init__(self):
        self.security_issues: List[SecurityIssue] = []
        self.base_image_vulnerabilities = {}
    
    def scan_dockerfile(self, dockerfile_path: str) -> List[SecurityIssue]:
        """扫描Dockerfile安全问题"""
        self.security_issues = []
        
        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 扫描各种安全问题
            self._scan_user_privileges(content)
            self._scan_secrets(content)
            self._scan_network_security(content)
            self._scan_file_permissions(content)
            self._scan_base_image(content)
            
            return self.security_issues
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Dockerfile不存在: {dockerfile_path}")
        except Exception as e:
            raise Exception(f"扫描失败: {e}")
    
    def _scan_user_privileges(self, content: str):
        """扫描用户权限问题"""
        # 检查是否使用root用户
        if not re.search(r'USER\s+(?!root)', content, re.IGNORECASE):
            if re.search(r'USER\s+root', content, re.IGNORECASE) or 'USER' not in content:
                self.security_issues.append(SecurityIssue(
                    type="user_privileges",
                    level=VulnerabilityLevel.HIGH,
                    description="容器以root用户运行",
                    recommendation="创建并使用非root用户运行应用"
                ))
        
        # 检查sudo使用
        if re.search(r'sudo\s+', content, re.IGNORECASE):
            self.security_issues.append(SecurityIssue(
                type="sudo_usage",
                level=VulnerabilityLevel.MEDIUM,
                description="检测到sudo使用",
                recommendation="避免在容器中使用sudo，直接配置用户权限"
            ))
    
    def _scan_secrets(self, content: str):
        """扫描敏感信息泄露"""
        secret_patterns = [
            (r'PASSWORD\s*=\s*[\'"][^\'"]+[\'"]', "硬编码密码"),
            (r'SECRET\s*=\s*[\'"][^\'"]+[\'"]', "硬编码密钥"),
            (r'TOKEN\s*=\s*[\'"][^\'"]+[\'"]', "硬编码令牌"),
            (r'API_KEY\s*=\s*[\'"][^\'"]+[\'"]', "硬编码API密钥"),
            (r'PRIVATE_KEY\s*=\s*[\'"][^\'"]+[\'"]', "硬编码私钥"),
        ]
        
        for pattern, description in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.security_issues.append(SecurityIssue(
                    type="secret_exposure",
                    level=VulnerabilityLevel.CRITICAL,
                    description=description,
                    recommendation="使用环境变量或密钥管理系统"
                ))
        
        # 检查环境文件复制
        if re.search(r'COPY.*\.env|COPY.*\.key|COPY.*\.pem', content, re.IGNORECASE):
            self.security_issues.append(SecurityIssue(
                type="env_file_copy",
                level=VulnerabilityLevel.HIGH,
                description="复制可能包含敏感信息的文件",
                recommendation="避免复制敏感文件，使用环境变量注入"
            ))
    
    def _scan_network_security(self, content: str):
        """扫描网络安全问题"""
        # 检查开放端口过多
        expose_count = len(re.findall(r'EXPOSE\s+\d+', content, re.IGNORECASE))
        if expose_count > 5:
            self.security_issues.append(SecurityIssue(
                type="excessive_ports",
                level=VulnerabilityLevel.MEDIUM,
                description=f"开放端口过多({expose_count}个)",
                recommendation="只开放必要的端口"
            ))
        
        # 检查是否使用HTTPS
        if re.search(r'EXPOSE\s+80', content, re.IGNORECASE) and not re.search(r'EXPOSE\s+443', content, re.IGNORECASE):
            self.security_issues.append(SecurityIssue(
                type="http_only",
                level=VulnerabilityLevel.MEDIUM,
                description="只开放HTTP端口，未使用HTTPS",
                recommendation="使用HTTPS或通过反向代理处理SSL"
            ))
        
        # 检查网络模式
        if '--network=host' in content:
            self.security_issues.append(SecurityIssue(
                type="host_network",
                level=VulnerabilityLevel.HIGH,
                description="使用host网络模式",
                recommendation="避免使用host网络，使用自定义网络"
            ))
    
    def _scan_file_permissions(self, content: str):
        """扫描文件权限问题"""
        # 检查chmod 777
        if re.search(r'chmod\s+777', content, re.IGNORECASE):
            self.security_issues.append(SecurityIssue(
                type="permissive_permissions",
                level=VulnerabilityLevel.MEDIUM,
                description="使用过于宽松的文件权限(777)",
                recommendation="使用最小必要权限原则"
            ))
        
        # 检查world-writable文件
        if re.search(r'chmod\s+.*[0-7][0-7][2367]', content, re.IGNORECASE):
            self.security_issues.append(SecurityIssue(
                type="world_writable",
                level=VulnerabilityLevel.MEDIUM,
                description="设置world-writable权限",
                recommendation="避免设置world-writable权限"
            ))
    
    def _scan_base_image(self, content: str):
        """扫描基础镜像问题"""
        # 提取基础镜像信息
        from_match = re.search(r'FROM\s+([^\s]+)', content, re.IGNORECASE)
        if from_match:
            base_image = from_match.group(1)
            
            # 检查latest标签
            if ':latest' in base_image or base_image.count(':') == 0:
                self.security_issues.append(SecurityIssue(
                    type="latest_tag",
                    level=VulnerabilityLevel.HIGH,
                    description="使用latest标签的基础镜像",
                    recommendation="使用具体版本标签确保可重现性"
                ))
            
            # 检查是否使用官方镜像
            if '/' not in base_image or base_image.startswith('library/'):
                # 这是官方镜像，相对安全
                pass
            else:
                self.security_issues.append(SecurityIssue(
                    type="untrusted_image",
                    level=VulnerabilityLevel.MEDIUM,
                    description="使用非官方基础镜像",
                    recommendation="优先使用官方镜像或验证镜像来源"
                ))
    
    def scan_image_vulnerabilities(self, image_name: str) -> Dict:
        """扫描镜像漏洞（需要Docker环境）"""
        try:
            # 使用docker scout或其他工具扫描
            # 这里是模拟实现
            vulnerabilities = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'vulnerabilities': []
            }
            
            # 模拟一些常见漏洞
            mock_vulns = [
                {
                    'id': 'CVE-2023-1234',
                    'package': 'openssl',
                    'version': '1.1.1',
                    'severity': 'high',
                    'description': 'OpenSSL缓冲区溢出漏洞'
                },
                {
                    'id': 'CVE-2023-5678',
                    'package': 'curl',
                    'version': '7.68.0',
                    'severity': 'medium',
                    'description': 'cURL信息泄露漏洞'
                }
            ]
            
            for vuln in mock_vulns:
                vulnerabilities[vuln['severity']] += 1
                vulnerabilities['vulnerabilities'].append(vuln)
            
            return vulnerabilities
        
        except Exception as e:
            return {'error': str(e)}
    
    def generate_security_report(self, dockerfile_path: str, image_name: Optional[str] = None) -> Dict:
        """生成安全报告"""
        # 扫描Dockerfile
        dockerfile_issues = self.scan_dockerfile(dockerfile_path)
        
        # 扫描镜像漏洞（如果提供了镜像名）
        image_vulnerabilities = None
        if image_name:
            image_vulnerabilities = self.scan_image_vulnerabilities(image_name)
        
        # 按严重程度分组
        issues_by_level = {}
        for level in VulnerabilityLevel:
            issues_by_level[level.value] = [
                {
                    'type': issue.type,
                    'description': issue.description,
                    'recommendation': issue.recommendation
                }
                for issue in dockerfile_issues if issue.level == level
            ]
        
        # 计算安全评分
        total_issues = len(dockerfile_issues)
        critical_count = len(issues_by_level['critical'])
        high_count = len(issues_by_level['high'])
        medium_count = len(issues_by_level['medium'])
        low_count = len(issues_by_level['low'])
        
        # 简单的安全评分算法
        score = 100
        score -= critical_count * 25
        score -= high_count * 15
        score -= medium_count * 10
        score -= low_count * 5
        score = max(0, score)
        
        return {
            'security_score': score,
            'total_issues': total_issues,
            'issues_by_level': issues_by_level,
            'image_vulnerabilities': image_vulnerabilities,
            'recommendations': self._generate_recommendations(dockerfile_issues)
        }
    
    def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """生成安全建议"""
        recommendations = set()
        
        for issue in issues:
            recommendations.add(issue.recommendation)
        
        # 添加通用建议
        recommendations.add("定期更新基础镜像")
        recommendations.add("使用最小权限原则")
        recommendations.add("启用容器运行时安全扫描")
        recommendations.add("实施镜像签名验证")
        
        return list(recommendations)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Docker安全扫描器')
    parser.add_argument('dockerfile', nargs='?', default='Dockerfile', help='Dockerfile路径')
    parser.add_argument('--image', help='镜像名称（用于漏洞扫描）')
    parser.add_argument('--output', help='输出报告文件')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    scanner = DockerSecurityScanner()
    
    try:
        report = scanner.generate_security_report(args.dockerfile, args.image)
        
        if args.format == 'json':
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"安全报告已保存到: {args.output}")
            else:
                print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            # 文本格式输出
            print("=" * 50)
            print("Docker安全扫描报告")
            print("=" * 50)
            
            print(f"安全评分: {report['security_score']}/100")
            print(f"总问题数: {report['total_issues']}")
            print()
            
            # 按严重程度显示问题
            for level in ['critical', 'high', 'medium', 'low']:
                issues = report['issues_by_level'][level]
                if issues:
                    level_names = {
                        'critical': '🚨 严重',
                        'high': '❌ 高危',
                        'medium': '⚠️ 中危',
                        'low': 'ℹ️ 低危'
                    }
                    print(f"{level_names[level]}问题:")
                    for issue in issues:
                        print(f"  - {issue['description']}")
                        print(f"    建议: {issue['recommendation']}")
                    print()
            
            # 安全建议
            if report['recommendations']:
                print("📋 安全建议:")
                for rec in report['recommendations']:
                    print(f"  - {rec}")
                print()
            
            # 镜像漏洞
            if report['image_vulnerabilities'] and 'error' not in report['image_vulnerabilities']:
                vulns = report['image_vulnerabilities']
                print("🔍 镜像漏洞:")
                print(f"  严重: {vulns['critical']}")
                print(f"  高危: {vulns['high']}")
                print(f"  中危: {vulns['medium']}")
                print(f"  低危: {vulns['low']}")
    
    except Exception as e:
        print(f"扫描失败: {e}")
        exit(1)
```

## 最佳实践

### 安全性
- **最小权限**: 使用非root用户运行容器
- **基础镜像**: 使用官方且经过安全审查的镜像
- **定期更新**: 定期更新基础镜像和依赖
- **密钥管理**: 使用环境变量或密钥管理服务

### 优化性
- **多阶段构建**: 使用多阶段构建减小镜像大小
- **层次优化**: 合理安排指令顺序优化缓存
- **Alpine镜像**: 优先使用Alpine等轻量级镜像
- **清理缓存**: 及时清理包管理器缓存

### 维护性
- **文档说明**: 添加必要的注释和说明
- **版本固定**: 使用具体版本标签
- **环境分离**: 区分开发和生产环境配置
- **标准化**: 遵循Dockerfile最佳实践

### 监控和审计
- **定期扫描**: 定期进行安全扫描
- **镜像签名**: 使用镜像签名验证
- **运行时监控**: 监控容器运行时安全
- **合规检查**: 确保符合安全合规要求

## 相关技能

- [Docker Compose编排](./docker-compose/) - 容器编排管理
- [安全扫描器](./security-scanner/) - 代码安全检查
- [环境验证器](./env-validator/) - 环境配置验证
- [代码格式化](./code-formatter/) - 代码规范检查

**L一个rge B作为e 镜像s**
- Us在g `ubuntu:l一个测试` (1.2GB) vs `一个lp在e:l一个测试` (7MB)
- Us在g `节点:18` (900MB) vs `节点:18-一个lp在e` (150MB)
- D如果ference: 800MB+ 在 f在一个l 镜像

**Unnecess一个ry 层s**
- E一个ch `RUN` comm和 cre在es 一个 层
- `RUN 一个pt-get upd在e && 一个pt-get 在st一个ll` should 是 ONE comm和
- Wr在g: Multiple RUN comm和s c一个't sh是 缓存

**Runn在g 作为 Root**
- 容器 runs 作为 root user 通过 de故障
- 安全 r是k: 容器 bre一个kout = 完整的 系统 一个ccess
- Fix: 添加 `USER 一个ppuser` directive

**Copy在g Entire Direct或y**
- `COPY . /一个pp` 在cludes everyth在g (节点_模块s, .git, etc.)
- Fix: 使用 `.dockerign或e` 到 exclude files
- Result: 500MB → 50MB

**Not P在n在g B作为e 镜像**
- `FROM 节点` uses l一个测试 (unpredic表)
- Fix: `FROM 节点:18.14.0` (spec如果ic 版本)
- D如果ferent 版本s m一个y 是h一个ve d如果ferently

## 验证检查清单

- [ ] B作为e 镜像 p在ned 到 spec如果ic 版本
- [ ] Runn在g 作为 n在-root user
- [ ] `.dockerign或e` excludes unnecess一个ry files
- [ ] RUN comm和s c在solid在ed
- [ ] F在一个l 镜像 size re作为在一个ble
- [ ] No 秘钥s 在 镜像
- [ ] He一个lth 检查 在cluded
- [ ] 层s 优化d 对于 c一个ch在g

## 相关技能
- **安全-sc一个ner** - 检查 镜像 对于 vulner一个bilities
- **代码-re视图** - Re视图 Dockerfile 逻辑
- **y一个ml-v一个lid在或** - V一个lid在e Docker-compose.yml
