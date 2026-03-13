---
name: Python分析器
description: "当进行Python代码审查、性能优化、类型安全检查或测试策略规划时，分析Python代码质量和最佳实践。"
license: MIT
---

# Python分析器技能

## 概述
Python让编写糟糕代码变得容易。分析代码质量以防止技术债务。

**核心原则**: Python让编写糟糕代码变得容易。分析代码质量以防止技术债务。

## 何时使用

**始终:**
- Python代码审查
- 性能优化
- 类型安全检查
- 测试策略规划
- 代码重构
- 架构设计评审

**触发短语:**
- "分析Python代码"
- "Python性能优化"
- "代码质量检查"
- "Python最佳实践"
- "类型安全分析"
- "测试覆盖率"

## Python分析功能

### 代码质量
- PEP 8规范检查
- 代码复杂度分析
- 代码重复检测
- 命名规范检查
- 文档字符串审查

### 性能分析
- 瓶颈识别
- 内存使用分析
- 算法复杂度评估
- 并发性能检查
- I/O优化建议

### 类型安全
- 类型注解检查
- 类型推断分析
- 类型错误检测
- mypy兼容性
- 运行时类型验证

## 常见Python问题

### 代码风格问题
```
问题:
不符合PEP 8编码规范

错误示例:
- 变量名使用驼峰命名
- 行长度超过79字符
- 缺少空行分隔
- 导入语句不规范

解决方案:
1. 使用black自动格式化
2. 配置flake8检查
3. 使用isort整理导入
4. 遵循PEP 8指南
```

### 性能问题
```
问题:
Python代码性能低下

错误示例:
- 在循环中使用+拼接字符串
- 不必要的列表推导
- 全局变量访问
- 缺少缓存机制

解决方案:
1. 使用join拼接字符串
2. 优化数据结构选择
3. 使用局部变量
4. 实现缓存策略
```

### 类型安全问题
```
问题:
缺少类型注解导致运行时错误

错误示例:
- 函数参数无类型提示
- 返回值类型不明确
- 可选参数未标注
- 泛型使用不当

解决方案:
1. 添加类型注解
2. 使用Optional标注可选值
3. 使用TypeVar定义泛型
4. 运行mypy检查
```

## 代码实现示例

### Python代码分析器
```python
import ast
import os
import re
from collections import defaultdict
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeIssue:
    """代码问题"""
    file_path: str
    line_number: int
    column: int
    severity: str  # error, warning, info
    message: str
    rule_id: str
    suggestion: Optional[str] = None

@dataclass
class FunctionMetrics:
    """函数指标"""
    name: str
    line_start: int
    line_end: int
    complexity: int
    arguments: int
    returns: int
    docstring: bool
    type_annotations: bool

@dataclass
class ClassMetrics:
    """类指标"""
    name: str
    line_start: int
    line_end: int
    methods: int
    attributes: int
    inheritance_depth: int
    docstring: bool

class PythonAnalyzer:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self.get_default_config()
        self.issues: List[CodeIssue] = []
        self.function_metrics: List[FunctionMetrics] = []
        self.class_metrics: List[ClassMetrics] = []
        self.imports: Dict[str, List[str]] = defaultdict(list)
        self.complexity_threshold = self.config.get('complexity_threshold', 10)
        
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'max_line_length': 79,
            'max_function_length': 50,
            'max_class_length': 200,
            'complexity_threshold': 10,
            'require_type_annotations': True,
            'require_docstrings': True,
            'check_imports': True,
            'check_naming': True
        }
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content, filename=file_path)
            
            # 重置状态
            self.issues = []
            self.function_metrics = []
            self.class_metrics = []
            self.imports = defaultdict(list)
            
            # 执行各种分析
            self.check_style(file_path, content)
            self.analyze_ast(tree, file_path)
            self.check_complexity(tree, file_path)
            self.check_type_safety(tree, file_path)
            self.check_documentation(tree, file_path)
            
            return {
                'file_path': file_path,
                'issues': self.issues,
                'function_metrics': self.function_metrics,
                'class_metrics': self.class_metrics,
                'imports': dict(self.imports),
                'summary': self.generate_summary()
            }
            
        except SyntaxError as e:
            return {
                'file_path': file_path,
                'error': f'语法错误: {e}',
                'issues': [CodeIssue(
                    file_path=file_path,
                    line_number=e.lineno or 0,
                    column=e.offset or 0,
                    severity='error',
                    message=f'语法错误: {e.msg}',
                    rule_id='syntax_error'
                )]
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'error': f'分析失败: {e}',
                'issues': []
            }
    
    def analyze_directory(self, directory: str) -> Dict[str, Any]:
        """分析整个目录"""
        results = []
        all_issues = []
        
        for root, dirs, files in os.walk(directory):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    result = self.analyze_file(file_path)
                    results.append(result)
                    all_issues.extend(result.get('issues', []))
        
        return {
            'directory': directory,
            'files': results,
            'total_issues': len(all_issues),
            'issue_summary': self.categorize_issues(all_issues),
            'recommendations': self.generate_recommendations(all_issues)
        }
    
    def check_style(self, file_path: str, content: str) -> None:
        """检查代码风格"""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > self.config['max_line_length']:
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=self.config['max_line_length'],
                    severity='warning',
                    message=f'行长度超过{self.config["max_line_length"]}字符',
                    rule_id='line_too_long',
                    suggestion='考虑拆分长行或使用括号换行'
                ))
            
            # 检查尾随空格
            if line.endswith(' '):
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=len(line.rstrip()),
                    severity='info',
                    message='行末有多余空格',
                    rule_id='trailing_whitespace',
                    suggestion='删除行末空格'
                ))
            
            # 检查Tab字符
            if '\t' in line:
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=line.find('\t'),
                    severity='warning',
                    message='使用了Tab字符，应该使用空格',
                    rule_id='tab_character',
                    suggestion='将Tab替换为4个空格'
                ))
    
    def analyze_ast(self, tree: ast.AST, file_path: str) -> None:
        """分析AST结构"""
        # 分析导入
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports['import'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    self.imports['from'].append(f'{module}.{alias.name}')
        
        # 分析函数和类
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.analyze_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self.analyze_class(node, file_path)
    
    def analyze_function(self, node: ast.FunctionDef, file_path: str) -> None:
        """分析函数"""
        # 计算复杂度
        complexity = self.calculate_complexity(node)
        
        # 统计参数
        args = len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg:
            args += 1
        if node.args.kwarg:
            args += 1
        
        # 检查返回语句
        returns = len([n for n in ast.walk(node) if isinstance(n, ast.Return)])
        
        # 检查文档字符串
        has_docstring = (ast.get_docstring(node) is not None)
        
        # 检查类型注解
        has_type_annotations = (
            all(arg.annotation for arg in node.args.args) and
            (node.returns is not None)
        )
        
        metrics = FunctionMetrics(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            complexity=complexity,
            arguments=args,
            returns=returns,
            docstring=has_docstring,
            type_annotations=has_type_annotations
        )
        
        self.function_metrics.append(metrics)
        
        # 检查问题
        if complexity > self.complexity_threshold:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='warning',
                message=f'函数{node.name}复杂度过高({complexity})',
                rule_id='high_complexity',
                suggestion='考虑拆分函数或简化逻辑'
            ))
        
        if not has_docstring and self.config['require_docstrings']:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='info',
                message=f'函数{node.name}缺少文档字符串',
                rule_id='missing_docstring',
                suggestion='添加函数文档说明'
            ))
        
        if not has_type_annotations and self.config['require_type_annotations']:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='info',
                message=f'函数{node.name}缺少类型注解',
                rule_id='missing_type_annotations',
                suggestion='添加参数和返回值类型注解'
            ))
    
    def analyze_class(self, node: ast.ClassDef, file_path: str) -> None:
        """分析类"""
        # 统计方法和属性
        methods = 0
        attributes = 0
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods += 1
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes += 1
        
        # 计算继承深度
        inheritance_depth = self.calculate_inheritance_depth(node)
        
        # 检查文档字符串
        has_docstring = (ast.get_docstring(node) is not None)
        
        metrics = ClassMetrics(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            attributes=attributes,
            inheritance_depth=inheritance_depth,
            docstring=has_docstring
        )
        
        self.class_metrics.append(metrics)
        
        # 检查问题
        if inheritance_depth > 3:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='warning',
                message=f'类{node.name}继承层次过深({inheritance_depth})',
                rule_id='deep_inheritance',
                suggestion='考虑使用组合替代继承'
            ))
        
        if not has_docstring and self.config['require_docstrings']:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=0,
                severity='info',
                message=f'类{node.name}缺少文档字符串',
                rule_id='missing_docstring',
                suggestion='添加类文档说明'
            ))
    
    def calculate_complexity(self, node: ast.AST) -> int:
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
    
    def calculate_inheritance_depth(self, node: ast.ClassDef) -> int:
        """计算继承深度"""
        if not node.bases:
            return 0
        
        max_depth = 0
        for base in node.bases:
            if isinstance(base, ast.Name):
                # 简化实现，实际需要解析整个模块
                max_depth = max(max_depth, 1)
        
        return max_depth
    
    def check_complexity(self, tree: ast.AST, file_path: str) -> None:
        """检查复杂度相关问题"""
        # 检查嵌套深度
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.If)):
                depth = self.calculate_nesting_depth(node)
                if depth > 3:
                    self.issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=0,
                        severity='warning',
                        message=f'嵌套层次过深({depth})',
                        rule_id='deep_nesting',
                        suggestion='考虑提取函数或使用早期返回'
                    ))
    
    def calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """计算嵌套深度"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.With, ast.Try)):
                child_depth = self.calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def check_type_safety(self, tree: ast.AST, file_path: str) -> None:
        """检查类型安全"""
        for node in ast.walk(tree):
            # 检查函数参数类型
            if isinstance(node, ast.FunctionDef):
                self.check_function_types(node, file_path)
            
            # 检查可能的None值
            elif isinstance(node, ast.Attribute):
                self.check_none_safety(node, file_path)
    
    def check_function_types(self, node: ast.FunctionDef, file_path: str) -> None:
        """检查函数类型安全"""
        if self.config['require_type_annotations']:
            # 检查参数类型注解
            for arg in node.args.args:
                if not arg.annotation:
                    self.issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=0,
                        severity='info',
                        message=f'参数{arg.arg}缺少类型注解',
                        rule_id='missing_parameter_type',
                        suggestion=f'添加类型注解: {arg.arg}: type'
                    ))
            
            # 检查返回值类型注解
            if not node.returns:
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=node.lineno,
                    column=0,
                    severity='info',
                    message='函数缺少返回值类型注解',
                    rule_id='missing_return_type',
                    suggestion='添加返回值类型注解'
                ))
    
    def check_none_safety(self, node: ast.Attribute, file_path: str) -> None:
        """检查None值安全"""
        # 简化实现，检查可能的None访问
        if isinstance(node.value, ast.Name) and node.value.id == 'None':
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                severity='error',
                message='尝试访问None的属性',
                rule_id='none_attribute_access',
                suggestion='检查对象是否为None'
            ))
    
    def check_documentation(self, tree: ast.AST, file_path: str) -> None:
        """检查文档"""
        # 检查模块文档
        if not ast.get_docstring(tree) and self.config['require_docstrings']:
            self.issues.append(CodeIssue(
                file_path=file_path,
                line_number=1,
                column=0,
                severity='info',
                message='模块缺少文档字符串',
                rule_id='missing_module_docstring',
                suggestion='添加模块级文档说明'
            ))
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        total_issues = len(self.issues)
        error_count = len([i for i in self.issues if i.severity == 'error'])
        warning_count = len([i for i in self.issues if i.severity == 'warning'])
        info_count = len([i for i in self.issues if i.severity == 'info'])
        
        return {
            'total_issues': total_issues,
            'errors': error_count,
            'warnings': warning_count,
            'info': info_count,
            'functions': len(self.function_metrics),
            'classes': len(self.class_metrics),
            'average_complexity': self.calculate_average_complexity()
        }
    
    def calculate_average_complexity(self) -> float:
        """计算平均复杂度"""
        if not self.function_metrics:
            return 0.0
        
        total_complexity = sum(f.complexity for f in self.function_metrics)
        return total_complexity / len(self.function_metrics)
    
    def categorize_issues(self, issues: List[CodeIssue]) -> Dict[str, List[CodeIssue]]:
        """分类问题"""
        categorized = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        for issue in issues:
            categorized[issue.severity].append(issue)
        
        return categorized
    
    def generate_recommendations(self, issues: List[CodeIssue]) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        # 统计问题类型
        issue_counts = defaultdict(int)
        for issue in issues:
            issue_counts[issue.rule_id] += 1
        
        # 基于问题类型生成建议
        if issue_counts['line_too_long'] > 5:
            recommendations.append({
                'type': 'style',
                'priority': 'medium',
                'message': '发现多个长行，建议使用black自动格式化',
                'action': 'pip install black && black .'
            })
        
        if issue_counts['missing_docstring'] > 3:
            recommendations.append({
                'type': 'documentation',
                'priority': 'low',
                'message': '多个函数缺少文档字符串，建议完善文档',
                'action': '为所有公共函数和类添加文档字符串'
            })
        
        if issue_counts['high_complexity'] > 2:
            recommendations.append({
                'type': 'complexity',
                'priority': 'high',
                'message': '发现多个高复杂度函数，建议重构',
                'action': '拆分复杂函数，提取辅助函数'
            })
        
        if issue_counts['missing_type_annotations'] > 5:
            recommendations.append({
                'type': 'type_safety',
                'priority': 'medium',
                'message': '缺少类型注解，建议添加类型提示',
                'action': '使用mypy检查并添加类型注解'
            })
        
        return recommendations

# 使用示例
def main():
    analyzer = PythonAnalyzer()
    
    # 分析单个文件
    result = analyzer.analyze_file('./example.py')
    print(f"文件: {result['file_path']}")
    print(f"问题数: {len(result['issues'])}")
    
    # 分析整个目录
    directory_result = analyzer.analyze_directory('./src')
    print(f"目录: {directory_result['directory']}")
    print(f"总问题数: {directory_result['total_issues']}")
    
    # 打印建议
    for rec in directory_result['recommendations']:
        print(f"- {rec['message']}")

if __name__ == '__main__':
    main()
```

### Python性能分析器
```python
import time
import cProfile
import pstats
import io
from functools import wraps
from typing import Callable, Dict, Any, List
from dataclasses import dataclass

@dataclass
class PerformanceMetric:
    """性能指标"""
    function_name: str
    execution_time: float
    call_count: int
    memory_usage: int
    cpu_usage: float

class PythonPerformanceAnalyzer:
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.profiles: Dict[str, cProfile.Profile] = {}
        
    def profile_function(self, func: Callable) -> Callable:
        """函数性能分析装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 创建性能分析器
            profiler = cProfile.Profile()
            
            # 开始分析
            start_time = time.time()
            profiler.enable()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 结束分析
                profiler.disable()
                end_time = time.time()
                
                # 记录指标
                execution_time = end_time - start_time
                self.record_metric(func.__name__, execution_time, profiler)
                
                # 保存分析器
                self.profiles[func.__name__] = profiler
                
            return result
        
        return wrapper
    
    def record_metric(self, func_name: str, execution_time: float, profiler: cProfile.Profile) -> None:
        """记录性能指标"""
        # 获取调用统计
        stats = pstats.Stats(profiler)
        
        # 获取调用次数
        call_count = 0
        for func_info, (calls, _, _, _, _) in stats.stats.items():
            if func_info[2] == func_name:
                call_count = calls
                break
        
        metric = PerformanceMetric(
            function_name=func_name,
            execution_time=execution_time,
            call_count=call_count,
            memory_usage=0,  # 需要memory_profiler
            cpu_usage=0.0    # 需要psutil
        )
        
        self.metrics.append(metric)
    
    def get_performance_report(self, func_name: str) -> Dict[str, Any]:
        """获取性能报告"""
        if func_name not in self.profiles:
            return {'error': f'函数{func_name}没有性能数据'}
        
        profiler = self.profiles[func_name]
        stats = pstats.Stats(profiler)
        
        # 获取热点函数
        hotspots = []
        for func_info, (calls, total_time, cum_time, _, _) in stats.stats.items():
            hotspots.append({
                'function': func_info[2],
                'calls': calls,
                'total_time': total_time,
                'cumulative_time': cum_time
            })
        
        # 按累计时间排序
        hotspots.sort(key=lambda x: x['cumulative_time'], reverse=True)
        
        return {
            'function_name': func_name,
            'hotspots': hotspots[:10],  # 前10个热点
            'total_calls': sum(h['calls'] for h in hotspots),
            'total_time': sum(h['cumulative_time'] for h in hotspots)
        }
    
    def optimize_suggestions(self, func_name: str) -> List[str]:
        """生成优化建议"""
        report = self.get_performance_report(func_name)
        suggestions = []
        
        if 'error' in report:
            return suggestions
        
        hotspots = report['hotspots']
        
        # 分析热点函数
        for hotspot in hotspots[:5]:
            if hotspot['cumulative_time'] > 0.1:  # 超过100ms
                suggestions.append(
                    f"函数{hotspot['function']}耗时较多({hotspot['cumulative_time']:.3f}s)，"
                    f"考虑优化算法或使用缓存"
                )
            
            if hotspot['calls'] > 1000:
                suggestions.append(
                    f"函数{hotspot['function']}调用频繁({hotspot['calls']}次)，"
                    f"考虑使用缓存或批量处理"
                )
        
        return suggestions

# 使用示例
@PythonPerformanceAnalyzer().profile_function
def slow_function():
    """模拟慢函数"""
    time.sleep(0.1)
    result = sum(i * i for i in range(1000))
    return result

def main():
    # 运行函数多次
    for _ in range(5):
        slow_function()
    
    # 获取性能报告
    analyzer = PythonPerformanceAnalyzer()
    report = analyzer.get_performance_report('slow_function')
    print("性能报告:", report)
    
    # 获取优化建议
    suggestions = analyzer.optimize_suggestions('slow_function')
    print("优化建议:", suggestions)

if __name__ == '__main__':
    main()
```

## Python最佳实践

### 代码风格
1. **PEP 8**: 遵循Python编码规范
2. **自动格式化**: 使用black和isort
3. **代码检查**: 使用flake8和pylint
4. **类型注解**: 使用typing模块

### 性能优化
1. **算法选择**: 选择合适的数据结构
2. **缓存机制**: 使用functools.lru_cache
3. **并发编程**: 使用asyncio和multiprocessing
4. **内存管理**: 避免内存泄漏

### 安全实践
1. **输入验证**: 验证外部输入
2. **SQL注入**: 使用参数化查询
3. **依赖管理**: 定期更新依赖
4. **代码审计**: 定期安全检查

## 相关技能

- **python-testing** - Python测试
- **python-performance** - Python性能优化
- **python-security** - Python安全
- **python-architecture** - Python架构设计
