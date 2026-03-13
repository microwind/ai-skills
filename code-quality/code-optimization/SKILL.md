---
name: 代码优化技巧
description: "当优化代码性能时，分析算法复杂度，优化数据结构，解决性能瓶颈。验证优化效果，设计高效代码，和最佳实践。"
license: MIT
---

# 代码优化技巧技能

## 概述
代码优化是提升软件性能的关键技术。不当的优化策略会增加代码复杂性，甚至降低性能。在优化前需要仔细分析性能瓶颈和优化目标。

**核心原则**: 好的优化应该显著提升性能，同时保持代码可读性和可维护性。坏的优化会导致过度工程化，增加系统复杂性。

## 何时使用

**始终:**
- 分析性能瓶颈时
- 优化算法复杂度时
- 提升代码执行效率时
- 减少内存使用时
- 优化数据库查询时
- 改善用户体验时

**触发短语:**
- "代码优化技巧"
- "性能优化分析"
- "算法复杂度优化"
- "内存使用优化"
- "代码性能调优"
- "执行效率提升"

## 代码优化功能

### 算法优化
- 时间复杂度分析
- 空间复杂度优化
- 算法选择策略
- 数据结构优化
- 缓存友好设计

### 性能分析
- 性能瓶颈识别
- 执行时间分析
- 内存使用监控
- 资源消耗统计
- 性能基准测试

### 代码重构
- 循环优化技巧
- 条件分支优化
- 函数调用优化
- 内存管理优化
- 并发性能优化

### 编译器优化
- 编译优化选项
- 内联函数优化
- 死代码消除
- 循环展开优化
- 向量化优化

## 常见代码优化问题

### 过早优化问题
```
问题:
在缺乏性能数据时进行优化

错误示例:
- 假设性能瓶颈
- 过度复杂化代码
- 忽略可读性
- 优化错误的地方

解决方案:
1. 先进行性能分析
2. 识别真实瓶颈
3. 量化优化效果
4. 保持代码简洁
```

### 算法选择错误
```
问题:
选择不适合的算法导致性能问题

错误示例:
- 对小数据使用复杂算法
- 忽略数据特性
- 错误估计复杂度
- 忽略缓存局部性

解决方案:
1. 分析数据规模
2. 考虑数据特性
3. 评估算法复杂度
4. 进行基准测试
```

### 内存泄漏问题
```
问题:
不当的内存管理导致资源浪费

错误示例:
- 忘记释放内存
- 循环引用
- 大对象频繁创建
- 缓存策略不当

解决方案:
1. 使用智能指针
2. 避免循环引用
3. 实施对象池
4. 优化缓存策略
```

### 并发性能问题
```
问题:
并发编程中的性能陷阱

错误示例:
- 过度同步
- 锁竞争严重
- 线程创建开销
- 缓存一致性开销

解决方案:
1. 减少锁粒度
2. 使用无锁数据结构
3. 线程池复用
4. 优化内存布局
```

## 代码实现示例

### 性能分析器
```python
import time
import tracemalloc
import functools
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from collections import defaultdict
import statistics

@dataclass
class PerformanceMetrics:
    """性能指标"""
    execution_time: float
    memory_usage: int
    peak_memory: int
    function_calls: int
    avg_time_per_call: float

class PerformanceProfiler:
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.call_stack: List[str] = []
        self.start_time: Optional[float] = None
        self.start_memory: Optional[int] = None
        
    def start_profiling(self) -> None:
        """开始性能分析"""
        tracemalloc.start()
        self.start_time = time.perf_counter()
        snapshot = tracemalloc.take_snapshot()
        self.start_memory = snapshot.compare_to(snapshot, 'lineno')[0].size_diff if snapshot.compare_to(snapshot, 'lineno') else 0
        
    def stop_profiling(self) -> Dict[str, Any]:
        """停止性能分析并返回结果"""
        if not self.start_time:
            return {'error': '性能分析未开始'}
        
        end_time = time.perf_counter()
        current_snapshot = tracemalloc.take_snapshot()
        current_memory = current_snapshot.compare_to(current_snapshot, 'lineno')[0].size_diff if current_snapshot.compare_to(current_snapshot, 'lineno') else 0
        
        total_time = end_time - self.start_time
        total_memory = current_memory - (self.start_memory or 0)
        
        # 找出峰值内存
        peak_memory = max(
            (metric.peak_memory for metric in self.metrics.values()),
            default=0
        )
        
        return {
            'total_execution_time': total_time,
            'total_memory_usage': total_memory,
            'peak_memory_usage': peak_memory,
            'function_metrics': {
                name: {
                    'execution_time': metric.execution_time,
                    'memory_usage': metric.memory_usage,
                    'peak_memory': metric.peak_memory,
                    'function_calls': metric.function_calls,
                    'avg_time_per_call': metric.avg_time_per_call
                }
                for name, metric in self.metrics.items()
            }
        }
    
    def profile_function(self, func_name: str) -> Callable:
        """函数性能分析装饰器"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 记录开始时间和内存
                start_time = time.perf_counter()
                snapshot1 = tracemalloc.take_snapshot()
                
                try:
                    # 执行函数
                    result = func(*args, **kwargs)
                    
                    # 记录结束时间和内存
                    end_time = time.perf_counter()
                    snapshot2 = tracemalloc.take_snapshot()
                    
                    # 计算内存差异
                    memory_diff = 0
                    if snapshot1 and snapshot2:
                        diff = snapshot2.compare_to(snapshot1, 'lineno')
                        memory_diff = sum(stat.size_diff for stat in diff)
                    
                    execution_time = end_time - start_time
                    
                    # 更新指标
                    if func_name not in self.metrics:
                        self.metrics[func_name] = PerformanceMetrics(
                            execution_time=0,
                            memory_usage=0,
                            peak_memory=0,
                            function_calls=0,
                            avg_time_per_call=0
                        )
                    
                    metric = self.metrics[func_name]
                    metric.execution_time += execution_time
                    metric.memory_usage += memory_diff
                    metric.peak_memory = max(metric.peak_memory, memory_diff)
                    metric.function_calls += 1
                    metric.avg_time_per_call = metric.execution_time / metric.function_calls
                    
                    return result
                
                except Exception as e:
                    # 记录异常情况
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    
                    if func_name not in self.metrics:
                        self.metrics[func_name] = PerformanceMetrics(
                            execution_time=0,
                            memory_usage=0,
                            peak_memory=0,
                            function_calls=0,
                            avg_time_per_call=0
                        )
                    
                    metric = self.metrics[func_name]
                    metric.execution_time += execution_time
                    metric.function_calls += 1
                    if metric.function_calls > 0:
                        metric.avg_time_per_call = metric.execution_time / metric.function_calls
                    
                    raise e
            
            return wrapper
        return decorator

# 算法优化分析器
class AlgorithmOptimizer:
    def __init__(self):
        self.profiler = PerformanceProfiler()
        
    def analyze_complexity(self, func: Callable, input_sizes: List[int]) -> Dict[str, Any]:
        """分析算法复杂度"""
        results = {
            'input_sizes': input_sizes,
            'execution_times': [],
            'memory_usage': [],
            'complexity_analysis': {}
        }
        
        for size in input_sizes:
            # 生成测试数据
            test_data = self._generate_test_data(func, size)
            
            # 性能测试
            self.profiler.start_profiling()
            
            try:
                # 执行算法
                start_time = time.perf_counter()
                result = func(test_data)
                end_time = time.perf_counter()
                
                # 记录性能数据
                execution_time = end_time - start_time
                results['execution_times'].append(execution_time)
                
                # 获取内存使用情况
                profile_result = self.profiler.stop_profiling()
                memory_usage = profile_result.get('total_memory_usage', 0)
                results['memory_usage'].append(memory_usage)
                
            except Exception as e:
                results['execution_times'].append(float('inf'))
                results['memory_usage'].append(0)
        
        # 分析复杂度
        results['complexity_analysis'] = self._analyze_time_complexity(
            input_sizes, results['execution_times']
        )
        
        return results
    
    def _generate_test_data(self, func: Callable, size: int) -> Any:
        """生成测试数据"""
        # 这里可以根据函数名推断数据类型
        if 'sort' in func.__name__:
            return list(range(size, 0, -1))  # 逆序列表用于排序
        elif 'search' in func.__name__:
            return list(range(size))  # 有序列表用于搜索
        elif 'sum' in func.__name__:
            return list(range(size))  # 数字列表用于求和
        else:
            return list(range(size))  # 默认数字列表
    
    def _analyze_time_complexity(self, input_sizes: List[int], execution_times: List[float]) -> Dict[str, Any]:
        """分析时间复杂度"""
        if len(input_sizes) < 3:
            return {'estimated_complexity': 'insufficient_data'}
        
        # 计算增长率
        growth_rates = []
        for i in range(1, len(input_sizes)):
            if execution_times[i-1] > 0:
                rate = execution_times[i] / execution_times[i-1]
                input_growth = input_sizes[i] / input_sizes[i-1]
                growth_rates.append(rate / input_growth)
        
        if not growth_rates:
            return {'estimated_complexity': 'no_data'}
        
        avg_growth_rate = statistics.mean(growth_rates)
        
        # 估计复杂度
        if avg_growth_rate < 1.5:
            complexity = "O(1) - 常数时间"
        elif avg_growth_rate < 2.5:
            complexity = "O(log n) - 对数时间"
        elif avg_growth_rate < 5:
            complexity = "O(n) - 线性时间"
        elif avg_growth_rate < 15:
            complexity = "O(n log n) - 线性对数时间"
        elif avg_growth_rate < 50:
            complexity = "O(n²) - 平方时间"
        else:
            complexity = "O(n³) 或更高 - 立方或更高时间"
        
        return {
            'estimated_complexity': complexity,
            'average_growth_rate': avg_growth_rate,
            'growth_rates': growth_rates
        }
    
    def compare_algorithms(self, algorithms: Dict[str, Callable], input_sizes: List[int]) -> Dict[str, Any]:
        """比较不同算法的性能"""
        comparison_results = {}
        
        for name, func in algorithms.items():
            comparison_results[name] = self.analyze_complexity(func, input_sizes)
        
        # 生成比较报告
        report = {
            'algorithms': comparison_results,
            'performance_ranking': self._rank_algorithms(comparison_results),
            'recommendations': self._generate_optimization_recommendations(comparison_results)
        }
        
        return report
    
    def _rank_algorithms(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """对算法进行性能排名"""
        rankings = []
        
        for name, result in results.items():
            if result['execution_times'] and result['execution_times'][-1] != float('inf'):
                avg_time = statistics.mean(result['execution_times'])
                rankings.append({
                    'algorithm': name,
                    'average_time': avg_time,
                    'complexity': result['complexity_analysis'].get('estimated_complexity', 'Unknown')
                })
        
        # 按平均执行时间排序
        rankings.sort(key=lambda x: x['average_time'])
        
        return rankings
    
    def _generate_optimization_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for name, result in results.items():
            complexity = result['complexity_analysis'].get('estimated_complexity', '')
            
            if 'O(n²)' in complexity or 'O(n³)' in complexity:
                recommendations.append(f"算法 {name} 复杂度较高，考虑使用更高效的算法")
            
            if result['memory_usage']:
                max_memory = max(result['memory_usage'])
                if max_memory > 100 * 1024 * 1024:  # 100MB
                    recommendations.append(f"算法 {name} 内存使用较高，考虑优化内存使用")
        
        if not recommendations:
            recommendations.append("所有算法性能表现良好，无需优化")
        
        return recommendations

# 代码优化建议器
class CodeOptimizer:
    def __init__(self):
        self.optimization_patterns = {
            'loop_optimization': self._analyze_loop_optimization,
            'memory_optimization': self._analyze_memory_optimization,
            'algorithm_optimization': self._analyze_algorithm_optimization,
            'data_structure_optimization': self._analyze_data_structure_optimization
        }
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """分析代码并提供优化建议"""
        analysis = {
            'code_length': len(code),
            'line_count': len(code.split('\n')),
            'optimization_suggestions': [],
            'complexity_indicators': {},
            'performance_issues': []
        }
        
        # 检查各种优化模式
        for pattern_name, analyzer in self.optimization_patterns.items():
            suggestions = analyzer(code)
            if suggestions:
                analysis['optimization_suggestions'].extend(suggestions)
        
        # 分析复杂度指标
        analysis['complexity_indicators'] = self._calculate_complexity_indicators(code)
        
        # 检测性能问题
        analysis['performance_issues'] = self._detect_performance_issues(code)
        
        return analysis
    
    def _analyze_loop_optimization(self, code: str) -> List[str]:
        """分析循环优化机会"""
        suggestions = []
        
        # 检查嵌套循环
        nested_loops = code.count('for') - 1  # 简化检测
        if nested_loops > 2:
            suggestions.append("检测到深层嵌套循环，考虑优化算法或使用更高效的数据结构")
        
        # 检查循环中的函数调用
        if 'for' in code and '()' in code:
            suggestions.append("循环中包含函数调用，考虑将函数调用移到循环外或使用内联优化")
        
        # 检查循环中的重复计算
        if 'for' in code and code.count('len(') > 1:
            suggestions.append("循环中可能存在重复计算，考虑缓存计算结果")
        
        return suggestions
    
    def _analyze_memory_optimization(self, code: str) -> List[str]:
        """分析内存优化机会"""
        suggestions = []
        
        # 检查大对象创建
        if '[]' in code and code.count('[]') > 3:
            suggestions.append("检测到多个列表创建，考虑使用预分配或对象池")
        
        # 检查可能的内存泄漏
        if 'open(' in code and 'close(' not in code:
            suggestions.append("检测到文件打开但未关闭，可能导致内存泄漏")
        
        # 检查全局变量使用
        if 'global ' in code:
            suggestions.append("检测到全局变量使用，可能影响内存管理")
        
        return suggestions
    
    def _analyze_algorithm_optimization(self, code: str) -> List[str]:
        """分析算法优化机会"""
        suggestions = []
        
        # 检查排序算法
        if 'sort' in code and 'for' in code:
            suggestions.append("检测到可能的排序实现，考虑使用内置排序函数")
        
        # 检查查找算法
        if 'for' in code and 'if' in code and 'return' in code:
            suggestions.append("检测到线性搜索，对于大数据集考虑使用二分查找或哈希表")
        
        # 检查递归使用
        if code.count('def ') > 1 and 'return' in code:
            suggestions.append("检测到可能的递归实现，考虑使用迭代优化或尾递归优化")
        
        return suggestions
    
    def _analyze_data_structure_optimization(self, code: str) -> List[str]:
        """分析数据结构优化机会"""
        suggestions = []
        
        # 检查列表使用
        if '[]' in code and 'in' in code:
            suggestions.append("检测到列表查找操作，对于频繁查找考虑使用集合或字典")
        
        # 检查字典使用
        if '{}' in code and 'for' in code:
            suggestions.append("检测到字典遍历，考虑使用字典视图方法优化")
        
        # 检查字符串操作
        if '+' in code and '"' in code and code.count('+') > 2:
            suggestions.append("检测到多次字符串拼接，考虑使用join()方法或格式化字符串")
        
        return suggestions
    
    def _calculate_complexity_indicators(self, code: str) -> Dict[str, int]:
        """计算复杂度指标"""
        indicators = {
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(code),
            'nested_depth': self._calculate_nested_depth(code),
            'function_count': code.count('def '),
            'loop_count': code.count('for ') + code.count('while '),
            'conditional_count': code.count('if ') + code.count('elif ')
        }
        
        return indicators
    
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """计算圈复杂度"""
        # 简化的圈复杂度计算
        complexity = 1  # 基础复杂度
        complexity += code.count('if ')
        complexity += code.count('elif ')
        complexity += code.count('for ')
        complexity += code.count('while ')
        complexity += code.count('and ')
        complexity += code.count('or ')
        
        return complexity
    
    def _calculate_nested_depth(self, code: str) -> int:
        """计算嵌套深度"""
        max_depth = 0
        current_depth = 0
        
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped.startswith('if ') or stripped.startswith('for ') or stripped.startswith('while '):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped == '' or not stripped.startswith(' '):
                current_depth = 0
        
        return max_depth
    
    def _detect_performance_issues(self, code: str) -> List[str]:
        """检测性能问题"""
        issues = []
        
        # 检查过度复杂的函数
        if len(code.split('\n')) > 50:
            issues.append("函数过长，考虑拆分为更小的函数")
        
        # 检查过多的条件分支
        if code.count('if ') > 10:
            issues.append("条件分支过多，考虑使用策略模式或查表法")
        
        # 检查深层嵌套
        if self._calculate_nested_depth(code) > 4:
            issues.append("嵌套层级过深，考虑使用早期返回或提取函数")
        
        return issues

# 使用示例
def main():
    # 创建性能分析器
    profiler = PerformanceProfiler()
    
    # 示例算法：冒泡排序
    @profiler.profile_function("bubble_sort")
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    
    # 示例算法：快速排序
    @profiler.profile_function("quick_sort")
    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
    
    # 创建算法优化器
    optimizer = AlgorithmOptimizer()
    
    # 比较算法性能
    algorithms = {
        'bubble_sort': bubble_sort,
        'quick_sort': quick_sort
    }
    
    input_sizes = [100, 500, 1000, 2000]
    comparison = optimizer.compare_algorithms(algorithms, input_sizes)
    
    print("算法性能比较:")
    for ranking in comparison['performance_ranking']:
        print(f"- {ranking['algorithm']}: {ranking['complexity']}, 平均时间: {ranking['average_time']:.6f}s")
    
    print("\n优化建议:")
    for rec in comparison['recommendations']:
        print(f"- {rec}")
    
    # 创建代码优化器
    code_optimizer = CodeOptimizer()
    
    # 示例代码分析
    sample_code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            for i in range(len(item)):
                if item % 2 == 0:
                    result.append(item * 2)
    return result
"""
    
    analysis = code_optimizer.analyze_code(sample_code)
    print("\n代码优化分析:")
    for suggestion in analysis['optimization_suggestions']:
        print(f"- {suggestion}")

if __name__ == '__main__':
    main()
```

### 代码优化工具
```python
import ast
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class OptimizationSuggestion:
    """优化建议"""
    type: str
    line_number: int
    message: str
    suggestion: str
    impact: str  # high, medium, low

class CodeAnalyzer:
    def __init__(self):
        self.suggestions: List[OptimizationSuggestion] = []
        
    def analyze_python_code(self, code: str) -> List[OptimizationSuggestion]:
        """分析Python代码并提供优化建议"""
        self.suggestions = []
        
        try:
            # 解析AST
            tree = ast.parse(code)
            
            # 分析各种优化机会
            self._analyze_loops(tree)
            self._analyze_function_calls(tree)
            self._analyze_memory_usage(tree)
            self._analyze_data_structures(tree)
            
        except SyntaxError as e:
            self.suggestions.append(OptimizationSuggestion(
                type='syntax_error',
                line_number=e.lineno or 0,
                message='语法错误',
                suggestion=f'修复语法错误: {e.msg}',
                impact='high'
            ))
        
        return self.suggestions
    
    def _analyze_loops(self, tree: ast.AST) -> None:
        """分析循环优化机会"""
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # 检查循环中的函数调用
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        self.suggestions.append(OptimizationSuggestion(
                            type='loop_optimization',
                            line_number=getattr(node, 'lineno', 0),
                            message='循环中包含函数调用',
                            suggestion='考虑将函数调用移到循环外或缓存结果',
                            impact='medium'
                        ))
                        break
                
                # 检查循环范围计算
                if hasattr(node, 'iter') and isinstance(node.iter, ast.Call):
                    self.suggestions.append(OptimizationSuggestion(
                        type='loop_optimization',
                        line_number=getattr(node, 'lineno', 0),
                        message='循环范围可能重复计算',
                        suggestion='预先计算循环范围',
                        impact='low'
                    ))
    
    def _analyze_function_calls(self, tree: ast.AST) -> None:
        """分析函数调用优化机会"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 检查重复的函数调用
                func_name = self._get_function_name(node)
                if func_name:
                    call_count = sum(1 for n in ast.walk(tree) 
                                   if isinstance(n, ast.Call) and self._get_function_name(n) == func_name)
                    
                    if call_count > 3:
                        self.suggestions.append(OptimizationSuggestion(
                            type='function_optimization',
                            line_number=getattr(node, 'lineno', 0),
                            message=f'函数 {func_name} 被多次调用',
                            suggestion='考虑缓存函数结果或使用批量处理',
                            impact='medium'
                        ))
    
    def _analyze_memory_usage(self, tree: ast.AST) -> None:
        """分析内存使用优化机会"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                self.suggestions.append(OptimizationSuggestion(
                    type='memory_optimization',
                    line_number=getattr(node, 'lineno', 0),
                    message='列表推导式可能创建大列表',
                    suggestion='考虑使用生成器表达式或分批处理',
                    impact='medium'
                ))
            
            elif isinstance(node, ast.Assign):
                # 检查大对象创建
                if isinstance(node.value, ast.List) or isinstance(node.value, ast.Dict):
                    self.suggestions.append(OptimizationSuggestion(
                        type='memory_optimization',
                        line_number=getattr(node, 'lineno', 0),
                        message='创建大型数据结构',
                        suggestion='考虑预分配大小或使用更高效的数据结构',
                        impact='low'
                    ))
    
    def _analyze_data_structures(self, tree: ast.AST) -> None:
        """分析数据结构优化机会"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                # 检查列表查找操作
                if isinstance(node.left, ast.Name) and isinstance(node.ops[0], ast.In):
                    self.suggestions.append(OptimizationSuggestion(
                        type='data_structure_optimization',
                        line_number=getattr(node, 'lineno', 0),
                        message='使用in操作符检查列表成员',
                        suggestion='对于频繁查找，考虑使用集合或字典',
                        impact='high'
                    ))
    
    def _get_function_name(self, node: ast.Call) -> Optional[str]:
        """获取函数名称"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

# 使用示例
def main():
    # 示例代码
    sample_code = """
def process_items(items):
    result = []
    for item in items:
        if item in valid_items:  # 列表查找
            processed = expensive_function(item)  # 循环中函数调用
            result.append(processed)
    return result

def expensive_function(x):
    # 模拟耗时操作
    return x * 2

valid_items = [1, 2, 3, 4, 5]  # 列表用于查找
"""
    
    # 分析代码
    analyzer = CodeAnalyzer()
    suggestions = analyzer.analyze_python_code(sample_code)
    
    print("代码优化建议:")
    for suggestion in suggestions:
        print(f"- 第{suggestion.line_number}行: {suggestion.message}")
        print(f"  建议: {suggestion.suggestion}")
        print(f"  影响: {suggestion.impact}")
        print()

if __name__ == '__main__':
    main()
```

## 代码优化最佳实践

### 性能分析
1. **基准测试**: 建立性能基准和测试用例
2. **性能监控**: 持续监控关键性能指标
3. **瓶颈识别**: 准确定位性能瓶颈位置
4. **量化优化**: 测量优化前后的性能差异
5. **回归测试**: 确保优化不影响功能正确性

### 算法选择
1. **复杂度分析**: 理解算法的时间和空间复杂度
2. **数据规模**: 根据数据规模选择合适算法
3. **数据特性**: 考虑数据的分布和特性
4. **缓存友好**: 优化内存访问模式
5. **并行化**: 考虑并行和并发优化

### 内存优化
1. **对象复用**: 使用对象池减少GC压力
2. **内存布局**: 优化数据结构内存布局
3. **延迟加载**: 按需加载和初始化
4. **缓存策略**: 合理使用缓存机制
5. **内存监控**: 监控内存使用和泄漏

### 代码重构
1. **函数拆分**: 将大函数拆分为小函数
2. **循环优化**: 减少循环内部计算
3. **条件优化**: 简化条件判断逻辑
4. **内联优化**: 适当使用内联函数
5. **编译优化**: 利用编译器优化选项

## 相关技能

- **performance-profiler** - 性能分析工具
- **refactoring-patterns** - 重构模式
- **code-review** - 代码审查
- **test-generation** - 测试生成
