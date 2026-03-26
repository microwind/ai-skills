# 代码优化参考文档

## 代码优化概述

### 什么是代码优化
代码优化是通过改进算法、数据结构、编程技巧和系统配置来提高程序性能、减少资源消耗的过程。它包括时间优化（提高执行速度）、空间优化（减少内存使用）、并发优化（提高并行效率）等多个方面，是软件开发中提升系统性能和用户体验的关键技术。

### 优化层次
1. **算法层优化**: 选择更高效的算法和数据结构
2. **代码层优化**: 改进代码实现和编程技巧
3. **编译层优化**: 利用编译器优化选项和特性
4. **系统层优化**: 操作系统和硬件层面的优化
5. **架构层优化**: 系统架构和分布式优化

### 优化原则
- **性能优先**: 在保证正确性的前提下追求最高性能
- **可维护性**: 优化不应过度牺牲代码可读性和可维护性
- **测量驱动**: 基于性能测量和分析进行优化
- **渐进优化**: 分步骤进行优化，每次优化后验证效果
- **成本效益**: 权衡优化成本和性能收益

## 算法优化核心实现

### 复杂度分析与优化
```python
# algorithm_optimization.py
import time
import math
import random
import heapq
import bisect
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, deque
import numpy as np
import pandas as pd

class ComplexityAnalyzer:
    """复杂度分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.time_measurements = {}
        self.space_measurements = {}
    
    def measure_time_complexity(self, func: callable, input_sizes: List[int]) -> Dict[str, Any]:
        """测量时间复杂度"""
        measurements = {}
        
        for size in input_sizes:
            # 生成测试数据
            test_data = self._generate_test_data(func, size)
            
            # 测量执行时间
            start_time = time.perf_counter()
            result = func(test_data)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            measurements[size] = execution_time
        
        # 分析复杂度趋势
        complexity_type = self._analyze_complexity_trend(measurements)
        
        return {
            'measurements': measurements,
            'complexity_type': complexity_type,
            'recommendations': self._get_optimization_recommendations(complexity_type)
        }
    
    def measure_space_complexity(self, func: callable, input_sizes: List[int]) -> Dict[str, Any]:
        """测量空间复杂度"""
        import sys
        import tracemalloc
        
        measurements = {}
        
        for size in input_sizes:
            # 生成测试数据
            test_data = self._generate_test_data(func, size)
            
            # 开始内存跟踪
            tracemalloc.start()
            
            # 执行函数
            result = func(test_data)
            
            # 获取内存使用情况
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            measurements[size] = peak / 1024 / 1024  # MB
        
        # 分析空间复杂度趋势
        complexity_type = self._analyze_space_complexity_trend(measurements)
        
        return {
            'measurements': measurements,
            'complexity_type': complexity_type,
            'recommendations': self._get_space_optimization_recommendations(complexity_type)
        }
    
    def _generate_test_data(self, func: callable, size: int) -> Any:
        """生成测试数据"""
        func_name = func.__name__
        
        if 'sort' in func_name.lower():
            return [random.randint(0, 1000) for _ in range(size)]
        elif 'search' in func_name.lower():
            return [random.randint(0, 1000) for _ in range(size)]
        elif 'graph' in func_name.lower():
            return self._generate_graph(size)
        else:
            return list(range(size))
    
    def _generate_graph(self, size: int) -> Dict[int, List[int]]:
        """生成图数据"""
        graph = {}
        for i in range(size):
            graph[i] = []
            # 每个节点随机连接到其他节点
            for j in range(size):
                if i != j and random.random() < 0.1:
                    graph[i].append(j)
        return graph
    
    def _analyze_complexity_trend(self, measurements: Dict[int, float]) -> str:
        """分析时间复杂度趋势"""
        sizes = sorted(measurements.keys())
        times = [measurements[size] for size in sizes]
        
        # 计算增长率
        if len(sizes) >= 2:
            growth_rates = []
            for i in range(1, len(sizes)):
                if times[i-1] > 0:
                    rate = times[i] / times[i-1]
                    growth_rates.append(rate)
            
            avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 1
            
            # 判断复杂度类型
            if avg_growth_rate < 2:
                return "O(n) - 线性时间"
            elif avg_growth_rate < 4:
                return "O(n log n) - 线性对数时间"
            elif avg_growth_rate < 10:
                return "O(n²) - 平方时间"
            else:
                return "O(n³) 或更高 - 多项式时间"
        
        return "未知复杂度"
    
    def _analyze_space_complexity_trend(self, measurements: Dict[int, float]) -> str:
        """分析空间复杂度趋势"""
        sizes = sorted(measurements.keys())
        spaces = [measurements[size] for size in sizes]
        
        # 计算空间增长率
        if len(sizes) >= 2:
            growth_rates = []
            for i in range(1, len(sizes)):
                if spaces[i-1] > 0:
                    rate = spaces[i] / spaces[i-1]
                    growth_rates.append(rate)
            
            avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 1
            
            # 判断空间复杂度类型
            if avg_growth_rate < 2:
                return "O(n) - 线性空间"
            elif avg_growth_rate < 4:
                return "O(n log n) - 线性对数空间"
            elif avg_growth_rate < 10:
                return "O(n²) - 平方空间"
            else:
                return "O(n³) 或更高 - 多项式空间"
        
        return "未知复杂度"
    
    def _get_optimization_recommendations(self, complexity_type: str) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        if "O(n²)" in complexity_type:
            recommendations.extend([
                "考虑使用哈希表将查找优化到O(1)",
                "尝试分治算法降低复杂度",
                "使用动态规划避免重复计算",
                "考虑预处理和缓存机制"
            ])
        elif "O(n log n)" in complexity_type:
            recommendations.extend([
                "检查是否可以进一步优化到O(n)",
                "考虑使用更高效的数据结构",
                "分析算法瓶颈进行局部优化"
            ])
        elif "线性时间" in complexity_type:
            recommendations.extend([
                "优化常数因子",
                "考虑并行化处理",
                "优化内存访问模式"
            ])
        
        return recommendations
    
    def _get_space_optimization_recommendations(self, complexity_type: str) -> List[str]:
        """获取空间优化建议"""
        recommendations = []
        
        if "O(n²)" in complexity_type:
            recommendations.extend([
                "使用原地算法减少空间使用",
                "考虑分块处理减少内存占用",
                "使用生成器或迭代器",
                "及时释放不需要的内存"
            ])
        elif "线性空间" in complexity_type:
            recommendations.extend([
                "优化数据结构布局",
                "使用更紧凑的数据类型",
                "考虑内存池技术"
            ])
        
        return recommendations

class AlgorithmOptimizer:
    """算法优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.complexity_analyzer = ComplexityAnalyzer()
    
    def optimize_sorting(self, data: List[int]) -> Tuple[List[int], Dict[str, Any]]:
        """排序算法优化"""
        original_data = data.copy()
        
        # 选择最优排序算法
        if len(data) < 10:
            # 小数据量使用插入排序
            sorted_data = self._insertion_sort(data)
            algorithm = "插入排序"
        elif len(data) < 1000:
            # 中等数据量使用快速排序
            sorted_data = self._quick_sort(data)
            algorithm = "快速排序"
        else:
            # 大数据量使用归并排序
            sorted_data = self._merge_sort(data)
            algorithm = "归并排序"
        
        # 性能分析
        performance = self._analyze_sorting_performance(original_data, sorted_data, algorithm)
        
        return sorted_data, performance
    
    def _insertion_sort(self, arr: List[int]) -> List[int]:
        """插入排序 - 适用于小数据量"""
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr
    
    def _quick_sort(self, arr: List[int]) -> List[int]:
        """快速排序 - 适用于中等数据量"""
        if len(arr) <= 1:
            return arr
        
        # 三数取中法选择pivot
        first, middle, last = arr[0], arr[len(arr)//2], arr[-1]
        pivot = sorted([first, middle, last])[1]
        
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return self._quick_sort(left) + middle + self._quick_sort(right)
    
    def _merge_sort(self, arr: List[int]) -> List[int]:
        """归并排序 - 适用于大数据量"""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self._merge_sort(arr[:mid])
        right = self._merge_sort(arr[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        """归并两个有序数组"""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        
        return result
    
    def _analyze_sorting_performance(self, original: List[int], sorted_data: List[int], algorithm: str) -> Dict[str, Any]:
        """分析排序性能"""
        # 验证排序正确性
        is_correct = sorted_data == sorted(original)
        
        # 计算复杂度
        time_complexity = self._get_sorting_time_complexity(algorithm, len(original))
        space_complexity = self._get_sorting_space_complexity(algorithm)
        
        return {
            'algorithm': algorithm,
            'data_size': len(original),
            'is_correct': is_correct,
            'time_complexity': time_complexity,
            'space_complexity': space_complexity,
            'recommendations': self._get_sorting_recommendations(algorithm, len(original))
        }
    
    def _get_sorting_time_complexity(self, algorithm: str, size: int) -> str:
        """获取排序时间复杂度"""
        complexity_map = {
            "插入排序": "O(n²)",
            "快速排序": "O(n log n)",
            "归并排序": "O(n log n)"
        }
        return complexity_map.get(algorithm, "未知")
    
    def _get_sorting_space_complexity(self, algorithm: str) -> str:
        """获取排序空间复杂度"""
        complexity_map = {
            "插入排序": "O(1)",
            "快速排序": "O(log n)",
            "归并排序": "O(n)"
        }
        return complexity_map.get(algorithm, "未知")
    
    def _get_sorting_recommendations(self, algorithm: str, size: int) -> List[str]:
        """获取排序优化建议"""
        recommendations = []
        
        if algorithm == "插入排序" and size > 100:
            recommendations.append("数据量较大，建议使用快速排序或归并排序")
        elif algorithm == "快速排序" and size > 10000:
            recommendations.append("大数据量可以考虑并行快速排序")
        elif algorithm == "归并排序":
            recommendations.append("可以考虑使用TimSort（Python内置排序）")
        
        recommendations.append("对于部分有序数据，插入排序可能更高效")
        
        return recommendations
    
    def optimize_search(self, data: List[int], target: int) -> Tuple[Optional[int], Dict[str, Any]]:
        """搜索算法优化"""
        # 检查数据是否有序
        is_sorted = all(data[i] <= data[i+1] for i in range(len(data)-1))
        
        if is_sorted:
            # 有序数据使用二分查找
            index = self._binary_search(data, target)
            algorithm = "二分查找"
            complexity = "O(log n)"
        else:
            # 无序数据使用哈希表查找
            index = self._hash_search(data, target)
            algorithm = "哈希查找"
            complexity = "O(1)"
        
        performance = {
            'algorithm': algorithm,
            'data_size': len(data),
            'target': target,
            'found': index is not None,
            'index': index,
            'time_complexity': complexity,
            'data_sorted': is_sorted
        }
        
        return index, performance
    
    def _binary_search(self, arr: List[int], target: int) -> Optional[int]:
        """二分查找"""
        left, right = 0, len(arr) - 1
        
        while left <= right:
            mid = (left + right) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return None
    
    def _hash_search(self, arr: List[int], target: int) -> Optional[int]:
        """哈希查找"""
        hash_map = {value: index for index, value in enumerate(arr)}
        return hash_map.get(target)

class DataStructureOptimizer:
    """数据结构优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize_collection_operations(self, operations: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """优化集合操作"""
        # 分析操作模式
        operation_stats = self._analyze_operations(operations)
        
        # 推荐最优数据结构
        recommended_structure = self._recommend_data_structure(operation_stats)
        
        # 性能对比
        performance_comparison = self._compare_structures(operations, recommended_structure)
        
        return {
            'operation_stats': operation_stats,
            'recommended_structure': recommended_structure,
            'performance_comparison': performance_comparison,
            'optimization_suggestions': self._get_optimization_suggestions(operation_stats)
        }
    
    def _analyze_operations(self, operations: List[Tuple[str, Any]]) -> Dict[str, int]:
        """分析操作模式"""
        stats = defaultdict(int)
        
        for op, _ in operations:
            stats[op] += 1
        
        total_ops = len(operations)
        
        return {
            'total_operations': total_ops,
            'operation_counts': dict(stats),
            'operation_ratios': {op: count/total_ops for op, count in stats.items()},
            'dominant_operation': max(stats.items(), key=lambda x: x[1])[0] if stats else None
        }
    
    def _recommend_data_structure(self, operation_stats: Dict[str, Any]) -> Dict[str, str]:
        """推荐数据结构"""
        dominant_op = operation_stats.get('dominant_operation')
        ratios = operation_stats.get('operation_ratios', {})
        
        recommendations = {}
        
        if dominant_op == 'search' and ratios.get('search', 0) > 0.5:
            recommendations['python'] = 'set 或 dict (O(1)查找)'
            recommendations['java'] = 'HashSet 或 HashMap'
            recommendations['javascript'] = 'Set 或 Map'
        elif dominant_op == 'insert' and ratios.get('insert', 0) > 0.5:
            recommendations['python'] = 'list (O(1)末尾插入)'
            recommendations['java'] = 'ArrayList'
            recommendations['javascript'] = 'Array'
        elif dominant_op == 'delete' and ratios.get('delete', 0) > 0.5:
            recommendations['python'] = 'set (O(1)删除)'
            recommendations['java'] = 'HashSet'
            recommendations['javascript'] = 'Set'
        elif ratios.get('range_query', 0) > 0.3:
            recommendations['python'] = 'sorted list 或 bisect'
            recommendations['java'] = 'TreeSet 或 TreeMap'
            recommendations['javascript'] = '排序数组 + 二分查找'
        else:
            recommendations['python'] = 'list (通用性好)'
            recommendations['java'] = 'ArrayList'
            recommendations['javascript'] = 'Array'
        
        return recommendations
    
    def _compare_structures(self, operations: List[Tuple[str, Any]], 
                          recommendations: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        """对比不同数据结构的性能"""
        # 简化的性能对比
        structures = ['list', 'set', 'dict', 'deque']
        
        performance = {}
        for structure in structures:
            performance[structure] = self._estimate_performance(operations, structure)
        
        return performance
    
    def _estimate_performance(self, operations: List[Tuple[str, Any]], structure: str) -> Dict[str, float]:
        """估算数据结构性能"""
        # 简化的性能估算
        complexity_map = {
            'list': {'search': 1.0, 'insert': 0.1, 'delete': 1.0, 'range_query': 0.1},
            'set': {'search': 0.1, 'insert': 0.1, 'delete': 0.1, 'range_query': 1.0},
            'dict': {'search': 0.1, 'insert': 0.1, 'delete': 0.1, 'range_query': 1.0},
            'deque': {'search': 1.0, 'insert': 0.1, 'delete': 0.1, 'range_query': 0.1}
        }
        
        total_time = 0
        for op, _ in operations:
            total_time += complexity_map.get(structure, {}).get(op, 1.0)
        
        return {'total_time': total_time, 'average_time': total_time / len(operations)}
    
    def _get_optimization_suggestions(self, operation_stats: Dict[str, Any]) -> List[str]:
        """获取优化建议"""
        suggestions = []
        ratios = operation_stats.get('operation_ratios', {})
        dominant_op = operation_stats.get('dominant_operation')
        
        if dominant_op == 'search':
            suggestions.append("频繁查找操作建议使用哈希表或集合")
            suggestions.append("考虑预构建索引以提高查找效率")
        elif dominant_op == 'insert':
            suggestions.append("频繁插入操作建议使用动态数组")
            suggestions.append("考虑批量插入减少开销")
        elif dominant_op == 'delete':
            suggestions.append("频繁删除操作建议使用链表或集合")
            suggestions.append("考虑延迟删除策略")
        
        if ratios.get('range_query', 0) > 0.3:
            suggestions.append("范围查询较多建议使用有序数据结构")
            suggestions.append("考虑使用跳表或平衡树")
        
        return suggestions

# 使用示例
if __name__ == "__main__":
    # 创建优化器
    optimizer = AlgorithmOptimizer()
    ds_optimizer = DataStructureOptimizer()
    
    # 测试排序优化
    test_data = [random.randint(0, 1000) for _ in range(1000)]
    sorted_data, performance = optimizer.optimize_sorting(test_data)
    print(f"排序优化结果: {performance}")
    
    # 测试搜索优化
    index, search_performance = optimizer.optimize_search(sorted_data, 500)
    print(f"搜索优化结果: {search_performance}")
    
    # 测试数据结构优化
    operations = [('search', 1), ('insert', 2), ('search', 3), ('delete', 1)] * 100
    ds_performance = ds_optimizer.optimize_collection_operations(operations)
    print(f"数据结构优化结果: {ds_performance}")
```

### 内存优化技术
```python
# memory_optimization.py
import gc
import sys
import psutil
import os
import weakref
import functools
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
import pandas as pd

class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.baseline_memory = None
        self.memory_snapshots = []
    
    def start_profiling(self):
        """开始内存分析"""
        gc.collect()  # 强制垃圾回收
        self.baseline_memory = self._get_memory_usage()
        self.logger.info(f"内存分析开始，基线内存: {self.baseline_memory:.2f} MB")
    
    def take_snapshot(self, label: str):
        """拍摄内存快照"""
        current_memory = self._get_memory_usage()
        snapshot = {
            'label': label,
            'memory_usage': current_memory,
            'delta_from_baseline': current_memory - self.baseline_memory if self.baseline_memory else 0,
            'timestamp': time.time()
        }
        self.memory_snapshots.append(snapshot)
        self.logger.info(f"内存快照 [{label}]: {current_memory:.2f} MB")
    
    def analyze_memory_growth(self) -> Dict[str, Any]:
        """分析内存增长"""
        if len(self.memory_snapshots) < 2:
            return {"error": "需要至少2个内存快照"}
        
        growth_analysis = {
            'total_growth': 0,
            'growth_rate': 0,
            'peak_memory': 0,
            'memory_leaks': [],
            'recommendations': []
        }
        
        # 计算总增长
        first_snapshot = self.memory_snapshots[0]
        last_snapshot = self.memory_snapshots[-1]
        growth_analysis['total_growth'] = last_snapshot['memory_usage'] - first_snapshot['memory_usage']
        
        # 计算增长率
        time_diff = last_snapshot['timestamp'] - first_snapshot['timestamp']
        if time_diff > 0:
            growth_analysis['growth_rate'] = growth_analysis['total_growth'] / time_diff
        
        # 找到峰值内存
        growth_analysis['peak_memory'] = max(snapshot['memory_usage'] for snapshot in self.memory_snapshots)
        
        # 检测可能的内存泄漏
        growth_analysis['memory_leaks'] = self._detect_memory_leaks()
        
        # 生成优化建议
        growth_analysis['recommendations'] = self._generate_memory_recommendations(growth_analysis)
        
        return growth_analysis
    
    def _get_memory_usage(self) -> float:
        """获取当前内存使用量（MB）"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def _detect_memory_leaks(self) -> List[str]:
        """检测内存泄漏"""
        leaks = []
        
        # 检查内存持续增长
        if len(self.memory_snapshots) >= 3:
            recent_snapshots = self.memory_snapshots[-3:]
            growth_trend = [snapshot['memory_usage'] for snapshot in recent_snapshots]
            
            # 简单的线性趋势检测
            if all(growth_trend[i] < growth_trend[i+1] for i in range(len(growth_trend)-1)):
                leaks.append("检测到内存持续增长，可能存在内存泄漏")
        
        return leaks
    
    def _generate_memory_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成内存优化建议"""
        recommendations = []
        
        if analysis['total_growth'] > 100:  # 超过100MB增长
            recommendations.append("内存增长较大，建议检查是否存在内存泄漏")
            recommendations.append("考虑使用内存分析工具进行详细分析")
        
        if analysis['growth_rate'] > 1:  # 每秒增长超过1MB
            recommendations.append("内存增长速度较快，建议优化内存使用")
            recommendations.append("考虑使用内存池或对象池技术")
        
        if analysis['memory_leaks']:
            recommendations.extend(analysis['memory_leaks'])
        
        return recommendations

class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.object_pool = {}
        self.weak_refs = weakref.WeakValueDictionary()
    
    def optimize_data_structures(self, data: Any) -> Dict[str, Any]:
        """优化数据结构"""
        optimization_results = {
            'original_size': self._calculate_size(data),
            'optimized_size': 0,
            'optimizations': [],
            'memory_saved': 0
        }
        
        # 根据数据类型进行优化
        if isinstance(data, list):
            optimized_data = self._optimize_list(data)
        elif isinstance(data, dict):
            optimized_data = self._optimize_dict(data)
        elif isinstance(data, str):
            optimized_data = self._optimize_string(data)
        else:
            optimized_data = data
        
        optimization_results['optimized_size'] = self._calculate_size(optimized_data)
        optimization_results['memory_saved'] = optimization_results['original_size'] - optimization_results['optimized_size']
        
        return optimization_results
    
    def _optimize_list(self, lst: List[Any]) -> List[Any]:
        """优化列表"""
        optimized = []
        
        for item in lst:
            if isinstance(item, str):
                # 字符串去重
                if item not in optimized:
                    optimized.append(item)
            elif isinstance(item, (int, float)):
                # 数值优化
                optimized.append(item)
            else:
                optimized.append(item)
        
        return optimized
    
    def _optimize_dict(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        """优化字典"""
        optimized = {}
        
        for key, value in d.items():
            # 键优化
            if isinstance(key, str):
                optimized_key = key.strip()  # 去除空白字符
            else:
                optimized_key = key
            
            # 值优化
            if isinstance(value, str):
                optimized_value = value.strip()
            elif isinstance(value, (list, dict)):
                # 递归优化嵌套结构
                optimized_value = self.optimize_data_structures(value)
            else:
                optimized_value = value
            
            optimized[optimized_key] = optimized_value
        
        return optimized
    
    def _optimize_string(self, s: str) -> str:
        """优化字符串"""
        # 去除多余空白字符
        optimized = ' '.join(s.split())
        return optimized
    
    def _calculate_size(self, obj: Any) -> int:
        """计算对象大小（字节）"""
        if isinstance(obj, (int, float, bool)):
            return sys.getsizeof(obj)
        elif isinstance(obj, str):
            return sys.getsizeof(obj)
        elif isinstance(obj, (list, tuple)):
            return sys.getsizeof(obj) + sum(self._calculate_size(item) for item in obj)
        elif isinstance(obj, dict):
            return sys.getsizeof(obj) + sum(self._calculate_size(k) + self._calculate_size(v) for k, v in obj.items())
        else:
            return sys.getsizeof(obj)
    
    def implement_object_pool(self, class_type: type, pool_size: int = 100) -> Callable:
        """实现对象池"""
        if class_type not in self.object_pool:
            self.object_pool[class_type] = []
        
        pool = self.object_pool[class_type]
        
        def get_object(*args, **kwargs):
            """从池中获取对象"""
            if pool:
                obj = pool.pop()
                # 重置对象状态
                if hasattr(obj, 'reset'):
                    obj.reset()
                return obj
            else:
                return class_type(*args, **kwargs)
        
        def return_object(obj):
            """将对象返回到池中"""
            if len(pool) < pool_size:
                pool.append(obj)
        
        # 绑定方法到类
        class_type.get_object = staticmethod(get_object)
        class_type.return_object = return_object
        
        return class_type
    
    def implement_lazy_loading(self, data_loader: Callable) -> Callable:
        """实现懒加载"""
        loaded_data = weakref.WeakValueDictionary()
        
        @functools.lru_cache(maxsize=128)
        def lazy_load(key: str):
            """懒加载数据"""
            if key not in loaded_data:
                loaded_data[key] = data_loader(key)
            return loaded_data[key]
        
        return lazy_load
    
    def implement_memory_mapping(self, file_path: str) -> Any:
        """实现内存映射"""
        try:
            import mmap
            
            with open(file_path, 'r+b') as f:
                # 创建内存映射
                mmapped_file = mmap.mmap(f.fileno(), 0)
                return mmapped_file
        
        except Exception as e:
            self.logger.error(f"内存映射失败: {e}")
            return None

class CacheOptimizer:
    """缓存优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.caches = {}
    
    def implement_lru_cache(self, maxsize: int = 128) -> Callable:
        """实现LRU缓存"""
        def decorator(func: Callable) -> Callable:
            cache = {}
            cache_order = []
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 创建缓存键
                key = str(args) + str(sorted(kwargs.items()))
                
                if key in cache:
                    # 更新访问顺序
                    cache_order.remove(key)
                    cache_order.append(key)
                    return cache[key]
                
                # 计算结果
                result = func(*args, **kwargs)
                
                # 缓存管理
                if len(cache) >= maxsize:
                    # 移除最久未使用的项
                    oldest_key = cache_order.pop(0)
                    del cache[oldest_key]
                
                cache[key] = result
                cache_order.append(key)
                
                return result
            
            return wrapper
        
        return decorator
    
    def implement_cache_invalidation(self, cache: Dict, ttl: int = 300) -> Dict:
        """实现缓存失效"""
        class CacheWithTTL:
            def __init__(self, ttl):
                self.cache = {}
                self.timestamps = {}
                self.ttl = ttl
            
            def get(self, key):
                if key in self.cache:
                    if time.time() - self.timestamps[key] < self.ttl:
                        return self.cache[key]
                    else:
                        del self.cache[key]
                        del self.timestamps[key]
                return None
            
            def set(self, key, value):
                self.cache[key] = value
                self.timestamps[key] = time.time()
            
            def clear_expired(self):
                current_time = time.time()
                expired_keys = [
                    key for key, timestamp in self.timestamps.items()
                    if current_time - timestamp >= self.ttl
                ]
                for key in expired_keys:
                    del self.cache[key]
                    del self.timestamps[key]
        
        return CacheWithTTL(ttl)
    
    def optimize_cache_strategy(self, access_pattern: Dict[str, int]) -> Dict[str, str]:
        """优化缓存策略"""
        total_access = sum(access_pattern.values())
        
        strategy_recommendations = {}
        
        for key, count in access_pattern.items():
            access_frequency = count / total_access
            
            if access_frequency > 0.5:
                strategy_recommendations[key] = "永久缓存"
            elif access_frequency > 0.1:
                strategy_recommendations[key] = "LRU缓存"
            elif access_frequency > 0.01:
                strategy_recommendations[key] = "TTL缓存"
            else:
                strategy_recommendations[key] = "不缓存"
        
        return strategy_recommendations

# 使用示例
if __name__ == "__main__":
    # 内存分析
    profiler = MemoryProfiler()
    profiler.start_profiling()
    
    # 创建一些数据
    large_list = [i for i in range(100000)]
    profiler.take_snapshot("创建大列表")
    
    # 优化数据结构
    optimizer = MemoryOptimizer()
    optimization_result = optimizer.optimize_data_structures(large_list)
    profiler.take_snapshot("数据结构优化")
    
    # 分析内存使用
    analysis = profiler.analyze_memory_growth()
    print(f"内存分析结果: {analysis}")
    
    # 缓存优化
    cache_optimizer = CacheOptimizer()
    
    @cache_optimizer.implement_lru_cache(maxsize=100)
    def expensive_computation(x):
        time.sleep(0.1)  # 模拟耗时操作
        return x * x
    
    # 测试缓存效果
    start_time = time.time()
    result1 = expensive_computation(42)
    first_call_time = time.time() - start_time
    
    start_time = time.time()
    result2 = expensive_computation(42)
    second_call_time = time.time() - start_time
    
    print(f"首次调用耗时: {first_call_time:.4f}s")
    print(f"缓存调用耗时: {second_call_time:.4f}s")
    print(f"性能提升: {first_call_time/second_call_time:.2f}x")
```

## 参考资源

### 性能分析工具
- [Python性能分析](https://docs.python.org/3/library/profile.html)
- [Java性能分析](https://docs.oracle.com/javase/8/docs/technotes/guides/visualvm/)
- [JavaScript性能分析](https://developer.chrome.com/docs/devtools/performance/)
- [C++性能分析](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)

### 优化技术文档
- [算法复杂度分析](https://en.wikipedia.org/wiki/Computational_complexity_theory)
- [数据结构优化](https://en.wikipedia.org/wiki/Data_structure)
- [内存管理优化](https://en.wikipedia.org/wiki/Memory_management)
- [并发编程优化](https://en.wikipedia.org/wiki/Concurrent_computing)

### 编译器优化
- [GCC优化选项](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [Clang优化指南](https://clang.llvm.org/docs/UsersManual.html#optimization)
- [JVM优化调优](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/)
- [V8引擎优化](https://v8.dev/docs)

### 系统性能优化
- [Linux性能调优](https://www.kernel.org/doc/html/latest/admin-guide/perf/)
- [Windows性能分析](https://docs.microsoft.com/en-us/windows/win32/perfcounters/performance-counters-portal)
- [数据库性能优化](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [网络性能优化](https://tools.ietf.org/html/rfc7231)
