---
name: CSS验证器
description: "当验证CSS代码时，分析CSS语法，检查样式规范，优化CSS性能。验证响应式设计，检查可访问性，和最佳实践。"
license: MIT
---

# CSS验证器技能

## 概述
CSS验证是保证前端样式质量的重要环节。不当的CSS会导致样式冲突、性能问题和维护困难。需要系统性的CSS验证和优化方法。

**核心原则**: 好的CSS应该结构清晰、性能优良、易于维护。坏的CSS会导致样式冲突、加载缓慢、难以调试。

## 何时使用

**始终:**
- 验证CSS语法正确性
- 优化CSS性能
- 检查响应式设计
- 审查CSS优先级
- 可访问性审计
- CSS组织结构审查

**触发短语:**
- "CSS验证器"
- "验证CSS语法"
- "优化CSS性能"
- "检查响应式设计"
- "审查CSS优先级"
- "CSS组织审查"

## CSS验证功能

### 语法验证
- 有效CSS选择器检查
- 正确属性值验证
- 颜色格式验证
- 单位一致性检查

### 性能优化
- 未使用样式检测
- 优先级分析
- 媒体查询优化
- 动画性能检查

### 最佳实践
- 命名规范检查
- 组件组织验证
- 响应式断点检查
- 可访问性考虑

## 常见CSS问题

### 高优先级问题
```
问题:
CSS选择器优先级过高，难以覆盖

错误示例:
.container .section .item.special#main { color: red; } (优先级过高)

后果:
- 难以覆盖样式
- CSS代码膨胀
- 维护困难

解决方案:
1. 使用低优先级选择器
2. 采用BEM命名规范
3. 避免过度嵌套
4. 使用CSS模块化
```

### 响应式设计问题
```
问题:
固定宽度设计，缺少媒体查询

错误示例:
.container { width: 1200px; } /* 固定宽度 */

后果:
- 移动端显示异常
- 用户体验差
- SEO排名降低

解决方案:
1. 使用相对单位
2. 添加媒体查询
3. 采用弹性布局
4. 移动优先设计
```

### 性能问题
```
问题:
CSS性能低效，影响页面加载

错误示例:
- 过度使用@import
- 大量重复样式
- 复杂选择器
- 未优化的动画

解决方案:
1. 减少CSS文件大小
2. 优化选择器性能
3. 使用CSS压缩
4. 优化动画性能
```

### 可访问性问题
```
问题:
CSS可访问性不足，影响用户使用

错误示例:
- 颜色对比度不足
- 缺少焦点样式
- 依赖颜色传达信息
- 字体大小过小

解决方案:
1. 确保颜色对比度
2. 添加焦点指示器
3. 提供多种信息传达方式
4. 使用合适的字体大小
```

## 代码实现示例

### CSS验证器
```python
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class IssueSeverity(Enum):
    """问题严重程度"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class IssueCategory(Enum):
    """问题类别"""
    SYNTAX = "syntax"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    BEST_PRACTICE = "best_practice"

@dataclass
class CSSIssue:
    """CSS问题"""
    line_number: int
    column: int
    severity: IssueSeverity
    category: IssueCategory
    message: str
    suggestion: str
    rule_id: str

@dataclass
class ValidationResult:
    """验证结果"""
    file_path: str
    issues: List[CSSIssue]
    metrics: Dict[str, Any]
    score: float

class CSSValidator:
    def __init__(self):
        self.issues: List[CSSIssue] = []
        self.css_rules = []
        
    def validate_css(self, css_content: str, file_path: str) -> ValidationResult:
        """验证CSS内容"""
        self.issues = []
        
        # 解析CSS
        self.css_rules = self._parse_css(css_content)
        
        # 执行各种检查
        self._check_syntax(css_content)
        self._check_performance(css_content)
        self._check_accessibility(css_content)
        self._check_best_practices(css_content)
        
        # 计算指标
        metrics = self._calculate_metrics(css_content)
        
        # 计算评分
        score = self._calculate_score()
        
        return ValidationResult(
            file_path=file_path,
            issues=self.issues,
            metrics=metrics,
            score=score
        )
    
    def _parse_css(self, css_content: str) -> List[Dict[str, Any]]:
        """解析CSS规则"""
        rules = []
        
        # 简化的CSS解析
        selector_pattern = r'([^{]+)\s*{([^}]*)}'
        matches = re.finditer(selector_pattern, css_content, re.MULTILINE)
        
        for match in matches:
            selector = match.group(1).strip()
            properties = match.group(2).strip()
            
            rules.append({
                'selector': selector,
                'properties': properties,
                'line': css_content[:match.start()].count('\n') + 1
            })
        
        return rules
    
    def _check_syntax(self, css_content: str) -> None:
        """检查CSS语法"""
        lines = css_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('/*'):
                continue
            
            # 检查选择器语法
            if '{' in line:
                selector_part = line.split('{')[0].strip()
                if not self._is_valid_selector(selector_part):
                    self.issues.append(CSSIssue(
                        line_number=line_num,
                        column=0,
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.SYNTAX,
                        message=f"无效的选择器: {selector_part}",
                        suggestion="检查选择器语法是否正确",
                        rule_id="invalid_selector"
                    ))
            
            # 检查属性语法
            if ':' in line and not line.startswith('@'):
                if not self._is_valid_property(line):
                    self.issues.append(CSSIssue(
                        line_number=line_num,
                        column=0,
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.SYNTAX,
                        message="CSS属性语法错误",
                        suggestion="检查属性和值的格式",
                        rule_id="invalid_property"
                    ))
    
    def _check_performance(self, css_content: str) -> None:
        """检查CSS性能"""
        lines = css_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查高优先级选择器
            if self._has_high_specificity(line):
                self.issues.append(CSSIssue(
                    line_number=line_num,
                    column=0,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.PERFORMANCE,
                    message="选择器优先级过高",
                    suggestion="简化选择器，降低优先级",
                    rule_id="high_specificity"
                ))
            
            # 检查昂贵的属性
            expensive_props = ['box-shadow', 'border-radius', 'transform', 'filter']
            for prop in expensive_props:
                if prop in line and ':' in line:
                    self.issues.append(CSSIssue(
                        line_number=line_num,
                        column=0,
                        severity=IssueSeverity.INFO,
                        category=IssueCategory.PERFORMANCE,
                        message=f"使用性能昂贵的属性: {prop}",
                        suggestion=f"谨慎使用{prop}，考虑性能影响",
                        rule_id="expensive_property"
                    ))
    
    def _check_accessibility(self, css_content: str) -> None:
        """检查可访问性"""
        lines = css_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查固定字体大小
            if 'font-size:' in line and any(unit in line for unit in ['px', 'pt']):
                self.issues.append(CSSIssue(
                    line_number=line_num,
                    column=0,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.ACCESSIBILITY,
                    message="使用固定字体大小",
                    suggestion="使用相对单位如rem或em",
                    rule_id="fixed_font_size"
                ))
            
            # 检查仅依赖颜色
            if 'color:' in line and not any(keyword in css_content for keyword in ['border', 'background', 'text-decoration']):
                self.issues.append(CSSIssue(
                    line_number=line_num,
                    column=0,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.ACCESSIBILITY,
                    message="仅依赖颜色传达信息",
                    suggestion="添加其他视觉提示如边框或背景",
                    rule_id="color_only"
                ))
    
    def _check_best_practices(self, css_content: str) -> None:
        """检查最佳实践"""
        lines = css_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检查!important使用
            if '!important' in line:
                self.issues.append(CSSIssue(
                    line_number=line_num,
                    column=0,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    message="使用!important",
                    suggestion="避免使用!important，重构选择器优先级",
                    rule_id="important_usage"
                ))
            
            # 检查ID选择器
            if '#' in line and '{' in line:
                selector = line.split('{')[0].strip()
                id_count = selector.count('#')
                if id_count > 1:
                    self.issues.append(CSSIssue(
                        line_number=line_num,
                        column=0,
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.BEST_PRACTICE,
                        message="使用多个ID选择器",
                        suggestion="使用类选择器替代ID选择器",
                        rule_id="multiple_ids"
                    ))
    
    def _is_valid_selector(self, selector: str) -> bool:
        """检查选择器是否有效"""
        # 简化的选择器验证
        if not selector:
            return False
        
        # 检查基本语法
        invalid_chars = ['<', '>', '(', ')', '+', '~', '=']
        return not any(char in selector for char in invalid_chars)
    
    def _is_valid_property(self, line: str) -> bool:
        """检查属性是否有效"""
        if ':' not in line:
            return False
        
        parts = line.split(':', 1)
        if len(parts) != 2:
            return False
        
        property_name = parts[0].strip()
        property_value = parts[1].strip()
        
        # 检查属性名
        if not re.match(r'^[a-zA-Z-]+$', property_name):
            return False
        
        # 检查属性值
        if not property_value or property_value.endswith(';'):
            return False
        
        return True
    
    def _has_high_specificity(self, line: str) -> bool:
        """检查是否有高优先级"""
        if '{' not in line:
            return False
        
        selector = line.split('{')[0].strip()
        
        # 计算优先级
        id_count = selector.count('#')
        class_count = selector.count('.')
        element_count = len(re.findall(r'\b[a-zA-Z]+\b', selector)) - class_count
        
        # 简化的优先级检查
        return id_count > 0 or class_count > 3 or element_count > 5
    
    def _calculate_metrics(self, css_content: str) -> Dict[str, Any]:
        """计算CSS指标"""
        lines = css_content.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'total_rules': len(self.css_rules),
            'total_selectors': sum(1 for rule in self.css_rules if rule['selector']),
            'total_properties': sum(len(rule['properties'].split(';')) for rule in self.css_rules),
            'issues_by_severity': {
                severity.value: len([issue for issue in self.issues if issue.severity == severity])
                for severity in IssueSeverity
            },
            'issues_by_category': {
                category.value: len([issue for issue in self.issues if issue.category == category])
                for category in IssueCategory
            }
        }
        
        # 计算复杂度指标
        metrics['average_specificity'] = self._calculate_average_specificity()
        metrics['unused_percentage'] = self._estimate_unused_percentage()
        
        return metrics
    
    def _calculate_average_specificity(self) -> float:
        """计算平均优先级"""
        if not self.css_rules:
            return 0.0
        
        total_specificity = 0
        for rule in self.css_rules:
            selector = rule['selector']
            specificity = self._calculate_specificity(selector)
            total_specificity += specificity
        
        return total_specificity / len(self.css_rules)
    
    def _calculate_specificity(self, selector: str) -> int:
        """计算选择器优先级"""
        id_count = selector.count('#')
        class_count = selector.count('.')
        element_count = len(re.findall(r'\b[a-zA-Z]+\b', selector)) - class_count
        
        return id_count * 100 + class_count * 10 + element_count
    
    def _estimate_unused_percentage(self) -> float:
        """估算未使用CSS百分比"""
        # 简化实现
        return 15.0  # 示例值
    
    def _calculate_score(self) -> float:
        """计算CSS评分"""
        score = 100.0
        
        # 根据问题严重程度扣分
        severity_weights = {
            IssueSeverity.ERROR: 10,
            IssueSeverity.WARNING: 5,
            IssueSeverity.INFO: 1
        }
        
        for issue in self.issues:
            score -= severity_weights[issue.severity]
        
        return max(0, score)

# CSS优化器
class CSSOptimizer:
    def __init__(self):
        self.optimizations = []
    
    def optimize_css(self, css_content: str) -> str:
        """优化CSS内容"""
        optimized = css_content
        
        # 移除注释
        optimized = self._remove_comments(optimized)
        
        # 压缩空白
        optimized = self._minify_whitespace(optimized)
        
        # 合并相同选择器
        optimized = self._merge_selectors(optimized)
        
        # 移除未使用的CSS
        optimized = self._remove_unused_css(optimized)
        
        # 优化颜色值
        optimized = self._optimize_colors(optimized)
        
        return optimized
    
    def _remove_comments(self, css_content: str) -> str:
        """移除注释"""
        return re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    def _minify_whitespace(self, css_content: str) -> str:
        """压缩空白字符"""
        # 移除多余的空白
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        
        return css_content.strip()
    
    def _merge_selectors(self, css_content: str) -> str:
        """合并相同选择器"""
        # 简化实现
        return css_content
    
    def _remove_unused_css(self, css_content: str) -> str:
        """移除未使用的CSS"""
        # 简化实现
        return css_content
    
    def _optimize_colors(self, css_content: str) -> str:
        """优化颜色值"""
        # 转换长颜色值为短格式
        css_content = re.sub(r'#([0-9a-fA-F])\1([0-9a-fA-F])\2([0-9a-fA-F])\3', r'#\1\2\3', css_content)
        
        return css_content

# 使用示例
def main():
    # 示例CSS
    sample_css = '''
/* 主样式 */
.container .section .item.special#main {
    color: red !important;
    background-color: #ffffff;
    font-size: 14px;
    margin: 10px;
    padding: 5px;
}

.button {
    background-color: #ff0000;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
}

@media (max-width: 768px) {
    .container {
        width: 100%;
    }
}
'''
    
    # 创建验证器
    validator = CSSValidator()
    
    # 验证CSS
    result = validator.validate_css(sample_css, "styles.css")
    
    print("CSS验证结果:")
    print(f"文件: {result.file_path}")
    print(f"评分: {result.score:.1f}")
    print(f"问题数量: {len(result.issues)}")
    print()
    
    # 显示问题
    for issue in result.issues:
        print(f"- 第{issue.line_number}行: {issue.message}")
        print(f"  严重程度: {issue.severity.value}")
        print(f"  建议: {issue.suggestion}")
        print()
    
    # 显示指标
    print("CSS指标:")
    for metric, value in result.metrics.items():
        if isinstance(value, dict):
            print(f"- {metric}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"- {metric}: {value}")
    
    # 优化CSS
    print("\n=== CSS优化 ===")
    optimizer = CSSOptimizer()
    optimized_css = optimizer.optimize_css(sample_css)
    
    print("优化后的CSS:")
    print(optimized_css)

if __name__ == '__main__':
    main()
```

### CSS检查清单生成器
```python
from typing import List, Dict, Any

class CSSChecklistGenerator:
    def __init__(self):
        self.checklist_items = []
    
    def generate_checklist(self, project_type: str = "web") -> List[Dict[str, Any]]:
        """生成CSS检查清单"""
        checklist = []
        
        # 语法检查
        checklist.extend(self._get_syntax_checks())
        
        # 性能检查
        checklist.extend(self._get_performance_checks())
        
        # 可访问性检查
        checklist.extend(self._get_accessibility_checks())
        
        # 最佳实践检查
        checklist.extend(self._get_best_practice_checks())
        
        # 项目特定检查
        if project_type == "mobile":
            checklist.extend(self._get_mobile_specific_checks())
        elif project_type == "enterprise":
            checklist.extend(self._get_enterprise_specific_checks())
        
        return checklist
    
    def _get_syntax_checks(self) -> List[Dict[str, Any]]:
        """获取语法检查项"""
        return [
            {
                "category": "语法",
                "item": "CSS语法正确性",
                "description": "检查所有CSS语法是否符合规范",
                "priority": "高",
                "check_method": "使用CSS验证器检查"
            },
            {
                "category": "语法",
                "item": "选择器有效性",
                "description": "确保所有选择器都是有效的",
                "priority": "高",
                "check_method": "检查选择器语法"
            },
            {
                "category": "语法",
                "item": "属性值正确性",
                "description": "验证所有属性值都是有效的",
                "priority": "高",
                "check_method": "检查属性值格式"
            }
        ]
    
    def _get_performance_checks(self) -> List[Dict[str, Any]]:
        """获取性能检查项"""
        return [
            {
                "category": "性能",
                "item": "选择器优先级",
                "description": "避免过高的选择器优先级",
                "priority": "中",
                "check_method": "计算选择器优先级"
            },
            {
                "category": "性能",
                "item": "未使用样式",
                "description": "移除未使用的CSS规则",
                "priority": "中",
                "check_method": "使用工具检测未使用样式"
            },
            {
                "category": "性能",
                "item": "CSS文件大小",
                "description": "控制CSS文件大小",
                "priority": "中",
                "check_method": "检查文件大小并压缩"
            }
        ]
    
    def _get_accessibility_checks(self) -> List[Dict[str, Any]]:
        """获取可访问性检查项"""
        return [
            {
                "category": "可访问性",
                "item": "颜色对比度",
                "description": "确保文本与背景有足够的对比度",
                "priority": "高",
                "check_method": "使用对比度检查工具"
            },
            {
                "category": "可访问性",
                "item": "相对字体大小",
                "description": "使用相对单位设置字体大小",
                "priority": "中",
                "check_method": "检查字体大小单位"
            },
            {
                "category": "可访问性",
                "item": "焦点样式",
                "description": "为可交互元素添加焦点样式",
                "priority": "高",
                "check_method": "检查:focus样式"
            }
        ]
    
    def _get_best_practice_checks(self) -> List[Dict[str, Any]]:
        """获取最佳实践检查项"""
        return [
            {
                "category": "最佳实践",
                "item": "命名规范",
                "description": "使用一致的CSS命名规范",
                "priority": "中",
                "check_method": "检查类名和ID命名"
            },
            {
                "category": "最佳实践",
                "item": "避免!important",
                "description": "避免使用!important",
                "priority": "中",
                "check_method": "搜索!important使用"
            },
            {
                "category": "最佳实践",
                "item": "响应式设计",
                "description": "确保网站支持响应式设计",
                "priority": "高",
                "check_method": "检查媒体查询"
            }
        ]
    
    def _get_mobile_specific_checks(self) -> List[Dict[str, Any]]:
        """获取移动端特定检查项"""
        return [
            {
                "category": "移动端",
                "item": "触摸目标大小",
                "description": "确保触摸目标足够大",
                "priority": "高",
                "check_method": "检查按钮和链接大小"
            },
            {
                "category": "移动端",
                "item": "视口设置",
                "description": "正确设置视口元标签",
                "priority": "高",
                "check_method": "检查viewport设置"
            }
        ]
    
    def _get_enterprise_specific_checks(self) -> List[Dict[str, Any]]:
        """获取企业级特定检查项"""
        return [
            {
                "category": "企业级",
                "item": "CSS模块化",
                "description": "使用CSS模块化架构",
                "priority": "中",
                "check_method": "检查CSS组织结构"
            },
            {
                "category": "企业级",
                "item": "浏览器兼容性",
                "description": "确保跨浏览器兼容性",
                "priority": "高",
                "check_method": "检查浏览器前缀和兼容性"
            }
        ]
    
    def export_checklist(self, checklist: List[Dict[str, Any]], format: str = "markdown") -> str:
        """导出检查清单"""
        if format == "markdown":
            return self._export_markdown(checklist)
        elif format == "json":
            return self._export_json(checklist)
        else:
            return str(checklist)
    
    def _export_markdown(self, checklist: List[Dict[str, Any]]) -> str:
        """导出为Markdown格式"""
        output = ["# CSS检查清单\n"]
        
        current_category = ""
        for item in checklist:
            if item["category"] != current_category:
                current_category = item["category"]
                output.append(f"## {current_category}\n")
            
            output.append(f"- [ ] **{item['item']}** ({item['priority']})")
            output.append(f"  - 描述: {item['description']}")
            output.append(f"  - 检查方法: {item['check_method']}\n")
        
        return "\n".join(output)
    
    def _export_json(self, checklist: List[Dict[str, Any]]) -> str:
        """导出为JSON格式"""
        import json
        return json.dumps(checklist, indent=2, ensure_ascii=False)

# 使用示例
def main():
    print("=== CSS检查清单生成器 ===")
    
    generator = CSSChecklistGenerator()
    
    # 生成Web项目检查清单
    web_checklist = generator.generate_checklist("web")
    
    # 导出为Markdown
    markdown_checklist = generator.export_checklist(web_checklist, "markdown")
    print("Web项目CSS检查清单:")
    print(markdown_checklist)
    
    # 生成移动端项目检查清单
    mobile_checklist = generator.generate_checklist("mobile")
    
    print("\n=== 移动端特定检查项 ===")
    for item in mobile_checklist[-2:]:  # 显示最后两个移动端特定项
        print(f"- {item['item']}: {item['description']}")

if __name__ == '__main__':
    main()
```

## CSS验证最佳实践

### 验证准备
1. **明确目标**: 确定验证的重点和标准
2. **选择工具**: 选择合适的CSS验证工具
3. **建立基准**: 建立CSS质量基准
4. **制定计划**: 制定验证计划和时间表
5. **团队培训**: 培训团队成员CSS最佳实践

### 验证执行
1. **语法检查**: 检查CSS语法正确性
2. **性能分析**: 分析CSS性能问题
3. **可访问性审查**: 检查可访问性合规性
4. **最佳实践验证**: 验证最佳实践遵循情况
5. **兼容性测试**: 测试浏览器兼容性

### 问题修复
1. **优先级排序**: 按严重程度排序问题
2. **制定修复方案**: 制定具体的修复方案
3. **实施修复**: 逐步修复发现的问题
4. **验证修复**: 验证修复效果
5. **更新标准**: 更新CSS标准和规范

### 持续改进
1. **定期验证**: 定期进行CSS验证
2. **监控指标**: 监控CSS质量指标
3. **团队反馈**: 收集团队反馈和建议
4. **工具更新**: 更新验证工具和方法
5. **标准演进**: 持续演进CSS标准

## 相关技能

- **bundle-analyzer** - 包分析器
- **performance-optimization** - 性能优化
- **component-analyzer** - 组件分析器
- **accessibility-audit** - 可访问性审计
