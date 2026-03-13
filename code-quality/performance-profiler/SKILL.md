---
name: 性能分析器
description: "当分析代码性能时，识别性能瓶颈，测量执行时间，优化慢查询。检测内存泄漏，分析资源使用，和性能优化策略。"
license: MIT
---

# 性能分析器技能

## 概述
性能分析是优化代码执行效率的关键技术。不当的性能分析会导致优化方向错误、资源浪费、用户体验差。需要系统化的性能分析方法。

**核心原则**: 好的性能分析应该准确测量、定位瓶颈、提供优化建议。坏的性能分析会导致误判问题、无效优化、性能下降。

## 何时使用

**始终:**
- 代码执行缓慢时
- 系统负载过高时
- 内存使用异常时
- 用户体验差时
- 资源竞争激烈时
- 扩展性受限时

**触发短语:**
- "代码执行慢"
- "性能分析"
- "查找瓶颈"
- "内存使用高"
- "优化循环"
- "性能分析"

## 性能分析功能

### CPU性能分析
- 函数执行时间测量
- 调用频率统计
- 热点函数识别
- 调用栈分析
- 执行路径追踪

### 内存分析
- 内存分配监控
- 内存泄漏检测
- 堆内存分析
- 对象生命周期追踪
- 垃圾回收分析

### I/O性能分析
- 文件操作监控
- 网络请求分析
- 数据库查询优化
- 缓存命中率统计
- 磁盘I/O分析

### 并发性能分析
- 线程竞争检测
- 锁竞争分析
- 死锁识别
- 并发瓶颈定位
- 资源争用分析

## 常见性能问题

### N+1查询问题
```
问题:
在循环中执行数据库查询，导致性能急剧下降

错误示例:
- 一次查询获取主数据
- 在循环中查询关联数据
- 大量重复查询
- 数据库连接池耗尽

解决方案:
1. 使用JOIN查询
2. 批量查询优化
3. 预加载关联数据
4. 使用缓存机制
```

### 内存泄漏问题
```
问题:
内存持续增长，最终导致系统崩溃

错误示例:
- 循环引用未释放
- 大对象长期持有
- 缓存无限制增长
- 资源未正确关闭

解决方案:
1. 及时释放资源
2. 使用弱引用
3. 实现缓存淘汰策略
4. 定期内存清理
```

### 算法效率问题
```
问题:
使用低效算法，导致时间复杂度过高

错误示例:
- O(n²)算法处理大数据
- 重复计算相同结果
- 不必要的数据复制
- 缺少缓存机制

解决方案:
1. 优化算法复杂度
2. 实现结果缓存
3. 减少数据复制
4. 使用高效数据结构
```

### I/O阻塞问题
```
问题:
同步I/O操作阻塞程序执行

错误示例:
- 同步文件读写
- 阻塞网络请求
- 数据库查询未优化
- 缺少异步处理

解决方案:
1. 使用异步I/O
2. 实现连接池
3. 批量操作优化
4. 非阻塞处理
```

## 代码实现示例

### 性能分析器
```python
import time
import psutil
import tracemalloc
import cProfile
import pstats
import io
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import threading
import json

class MetricType(Enum):
    """指标类型"""
    CPU_TIME = "cpu_time"
    MEMORY_USAGE = "memory_usage"
    EXECUTION_TIME = "execution_time"
    CALL_COUNT = "call_count"
    I/O_OPS = "io_ops"

class PerformanceLevel(Enum):
    """性能级别"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    metric_type: MetricType

@dataclass
class FunctionProfile:
    """函数性能档案"""
    function_name: str
    call_count: int
    total_time: float
    avg_time: float
    max_time: float
    min_time: float
    memory_usage: float
    cpu_percent: float

@dataclass
class PerformanceReport:
    """性能报告"""
    start_time: float
    end_time: float
    total_duration: float
    metrics: List[PerformanceMetric]
    function_profiles: List[FunctionProfile]
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]

class PerformanceProfiler:
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.function_profiles: List[FunctionProfile] = {}
        self.start_time = None
        self.end_time = None
        self.is_profiling = False
        self.profile_lock = threading.Lock()
        
        # 性能监控配置
        self.monitoring_interval = 0.1  # 100ms
        self.memory_threshold = 100 * 1024 * 1024  # 100MB
        self.cpu_threshold = 80.0  # 80%
        
        # 启动内存追踪
        tracemalloc.start()
    
    def start_profiling(self):
        """开始性能分析"""
        with self.profile_lock:
            if self.is_profiling:
                return False
            
            self.is_profiling = True
            self.start_time = time.time()
            self.metrics.clear()
            self.function_profiles.clear()
            
            # 启动监控线程
            self.monitor_thread = threading.Thread(target=self._monitor_system)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            print("性能分析已开始")
            return True
    
    def stop_profiling(self) -> PerformanceReport:
        """停止性能分析并生成报告"""
        with self.profile_lock:
            if not self.is_profiling:
                return None
            
            self.is_profiling = False
            self.end_time = time.time()
            
            # 等待监控线程结束
            self.monitor_thread.join(timeout=1.0)
            
            # 生成性能报告
            report = self._generate_report()
            
            print("性能分析已完成")
            return report
    
    def profile_function(self, name: Optional[str] = None):
        """函数性能分析装饰器"""
        def decorator(func: Callable):
            func_name = name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 记录开始时间
                start_time = time.perf_counter()
                start_memory = tracemalloc.get_traced_memory()[0]
                
                # 执行函数
                try:
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    result = e
                    success = False
                
                # 记录结束时间
                end_time = time.perf_counter()
                end_memory = tracemalloc.get_traced_memory()[0]
                
                # 计算性能指标
                execution_time = end_time - start_time
                memory_delta = end_memory - start_memory
                cpu_percent = psutil.cpu_percent()
                
                # 更新函数档案
                self._update_function_profile(
                    func_name, execution_time, memory_delta, cpu_percent, success
                )
                
                # 记录指标
                self._record_metric(
                    f"function_{func_name}_time",
                    execution_time,
                    "seconds",
                    MetricType.EXECUTION_TIME
                )
                
                self._record_metric(
                    f"function_{func_name}_memory",
                    memory_delta,
                    "bytes",
                    MetricType.MEMORY_USAGE
                )
                
                return result
            
            return wrapper
        return decorator
    
    def profile_code_block(self, block_name: str):
        """代码块性能分析上下文管理器"""
        class CodeBlockProfiler:
            def __init__(self, profiler, name):
                self.profiler = profiler
                self.name = name
                self.start_time = None
                self.start_memory = None
            
            def __enter__(self):
                self.start_time = time.perf_counter()
                self.start_memory = tracemalloc.get_traced_memory()[0]
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.perf_counter()
                end_memory = tracemalloc.get_traced_memory()[0]
                
                execution_time = end_time - self.start_time
                memory_delta = end_memory - self.start_memory
                
                self.profiler._record_metric(
                    f"block_{self.name}_time",
                    execution_time,
                    "seconds",
                    MetricType.EXECUTION_TIME
                )
                
                self.profiler._record_metric(
                    f"block_{self.name}_memory",
                    memory_delta,
                    "bytes",
                    MetricType.MEMORY_USAGE
                )
                
                print(f"代码块 '{self.name}' 执行时间: {execution_time:.4f}s")
                print(f"代码块 '{self.name}' 内存变化: {memory_delta / 1024:.2f}KB")
        
        return CodeBlockProfiler(self, block_name)
    
    def _monitor_system(self):
        """监控系统性能"""
        process = psutil.Process()
        
        while self.is_profiling:
            try:
                # CPU使用率
                cpu_percent = process.cpu_percent()
                self._record_metric("cpu_percent", cpu_percent, "percent", MetricType.CPU_TIME)
                
                # 内存使用
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self._record_metric("memory_usage", memory_mb, "MB", MetricType.MEMORY_USAGE)
                
                # 线程数
                thread_count = process.num_threads()
                self._record_metric("thread_count", thread_count, "count", MetricType.CALL_COUNT)
                
                # 文件描述符
                try:
                    fd_count = process.num_fds()
                    self._record_metric("fd_count", fd_count, "count", MetricType.CALL_COUNT)
                except (AttributeError, psutil.AccessDenied):
                    pass
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"监控异常: {e}")
                break
    
    def _record_metric(self, name: str, value: float, unit: str, metric_type: MetricType):
        """记录性能指标"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            metric_type=metric_type
        )
        
        with self.profile_lock:
            self.metrics.append(metric)
    
    def _update_function_profile(self, func_name: str, execution_time: float, 
                               memory_delta: float, cpu_percent: float, success: bool):
        """更新函数性能档案"""
        with self.profile_lock:
            if func_name not in self.function_profiles:
                self.function_profiles[func_name] = FunctionProfile(
                    function_name=func_name,
                    call_count=0,
                    total_time=0.0,
                    avg_time=0.0,
                    max_time=0.0,
                    min_time=float('inf'),
                    memory_usage=0.0,
                    cpu_percent=0.0
                )
            
            profile = self.function_profiles[func_name]
            profile.call_count += 1
            profile.total_time += execution_time
            profile.avg_time = profile.total_time / profile.call_count
            profile.max_time = max(profile.max_time, execution_time)
            profile.min_time = min(profile.min_time, execution_time)
            profile.memory_usage += memory_delta
            profile.cpu_percent = max(profile.cpu_percent, cpu_percent)
    
    def _generate_report(self) -> PerformanceReport:
        """生成性能报告"""
        total_duration = self.end_time - self.start_time
        
        # 识别性能瓶颈
        bottlenecks = self._identify_bottlenecks()
        
        # 生成优化建议
        recommendations = self._generate_recommendations(bottlenecks)
        
        return PerformanceReport(
            start_time=self.start_time,
            end_time=self.end_time,
            total_duration=total_duration,
            metrics=self.metrics.copy(),
            function_profiles=list(self.function_profiles.values()),
            bottlenecks=bottlenecks,
            recommendations=recommendations
        )
    
    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """识别性能瓶颈"""
        bottlenecks = []
        
        # 分析函数性能
        for profile in self.function_profiles.values():
            if profile.total_time > 1.0:  # 超过1秒
                bottlenecks.append({
                    "type": "slow_function",
                    "function": profile.function_name,
                    "total_time": profile.total_time,
                    "call_count": profile.call_count,
                    "avg_time": profile.avg_time,
                    "severity": "high" if profile.total_time > 5.0 else "medium"
                })
            
            if profile.call_count > 1000:  # 调用次数过多
                bottlenecks.append({
                    "type": "frequent_calls",
                    "function": profile.function_name,
                    "call_count": profile.call_count,
                    "total_time": profile.total_time,
                    "severity": "medium" if profile.call_count > 5000 else "low"
                })
            
            if profile.memory_usage > 10 * 1024 * 1024:  # 内存使用超过10MB
                bottlenecks.append({
                    "type": "memory_intensive",
                    "function": profile.function_name,
                    "memory_usage": profile.memory_usage,
                    "call_count": profile.call_count,
                    "severity": "high" if profile.memory_usage > 50 * 1024 * 1024 else "medium"
                })
        
        # 分析系统指标
        cpu_metrics = [m for m in self.metrics if m.name == "cpu_percent"]
        if cpu_metrics:
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > self.cpu_threshold:
                bottlenecks.append({
                    "type": "high_cpu",
                    "avg_cpu": avg_cpu,
                    "max_cpu": max(m.value for m in cpu_metrics),
                    "severity": "high" if avg_cpu > 90 else "medium"
                })
        
        memory_metrics = [m for m in self.metrics if m.name == "memory_usage"]
        if memory_metrics:
            max_memory = max(m.value for m in memory_metrics)
            if max_memory > self.memory_threshold / 1024 / 1024:  # 转换为MB
                bottlenecks.append({
                    "type": "high_memory",
                    "max_memory": max_memory,
                    "avg_memory": sum(m.value for m in memory_metrics) / len(memory_metrics),
                    "severity": "high" if max_memory > 500 else "medium"
                })
        
        return bottlenecks
    
    def _generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck["type"] == "slow_function":
                recommendations.append(
                    f"函数 {bottleneck['function']} 执行时间过长 "
                    f"({bottleneck['total_time']:.2f}s)，建议优化算法或添加缓存"
                )
            elif bottleneck["type"] == "frequent_calls":
                recommendations.append(
                    f"函数 {bottleneck['function']} 调用次数过多 "
                    f"({bottleneck['call_count']}次)，建议批量处理或缓存结果"
                )
            elif bottleneck["type"] == "memory_intensive":
                recommendations.append(
                    f"函数 {bottleneck['function']} 内存使用过高 "
                    f"({bottleneck['memory_usage']/1024/1024:.2f}MB)，建议优化内存使用"
                )
            elif bottleneck["type"] == "high_cpu":
                recommendations.append(
                    f"CPU使用率过高 ({bottleneck['avg_cpu']:.1f}%)，建议优化计算密集型操作"
                )
            elif bottleneck["type"] == "high_memory":
                recommendations.append(
                    f"内存使用过高 ({bottleneck['max_memory']:.1f}MB)，建议检查内存泄漏"
                )
        
        return recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.is_profiling and not self.metrics:
            return {"status": "no_data"}
        
        summary = {
            "status": "profiling" if self.is_profiling else "completed",
            "total_metrics": len(self.metrics),
            "function_count": len(self.function_profiles),
            "start_time": self.start_time,
            "duration": time.time() - self.start_time if self.start_time else 0
        }
        
        if self.metrics:
            # 计算平均值
            cpu_metrics = [m for m in self.metrics if m.name == "cpu_percent"]
            if cpu_metrics:
                summary["avg_cpu"] = sum(m.value for m in cpu_metrics) / len(cpu_metrics)
                summary["max_cpu"] = max(m.value for m in cpu_metrics)
            
            memory_metrics = [m for m in self.metrics if m.name == "memory_usage"]
            if memory_metrics:
                summary["avg_memory"] = sum(m.value for m in memory_metrics) / len(memory_metrics)
                summary["max_memory"] = max(m.value for m in memory_metrics)
        
        return summary

# 使用示例
def main():
    print("=== 性能分析器 ===")
    
    # 创建性能分析器
    profiler = PerformanceProfiler()
    
    # 示例1: 函数性能分析
    @profiler.profile_function()
    def slow_function(n: int) -> int:
        """模拟慢函数"""
        total = 0
        for i in range(n):
            total += i * i
        return total
    
    @profiler.profile_function()
    def memory_intensive_function(size: int) -> List[int]:
        """模拟内存密集型函数"""
        return [i for i in range(size)]
    
    # 开始性能分析
    profiler.start_profiling()
    
    # 执行一些函数
    print("执行测试函数...")
    
    for i in range(10):
        result = slow_function(10000)
    
    for i in range(5):
        data = memory_intensive_function(100000)
    
    # 使用代码块分析
    with profiler.profile_code_block("data_processing"):
        # 模拟数据处理
        data = []
        for i in range(50000):
            data.append(i * 2)
        processed = sum(data)
    
    # 停止分析并获取报告
    report = profiler.stop_profiling()
    
    if report:
        print(f"\n=== 性能报告 ===")
        print(f"总执行时间: {report.total_duration:.2f}s")
        print(f"指标数量: {len(report.metrics)}")
        print(f"函数数量: {len(report.function_profiles)}")
        
        print(f"\n=== 函数性能排名 ===")
        sorted_profiles = sorted(report.function_profiles, key=lambda x: x.total_time, reverse=True)
        for i, profile in enumerate(sorted_profiles[:5], 1):
            print(f"{i}. {profile.function_name}")
            print(f"   总时间: {profile.total_time:.4f}s")
            print(f"   调用次数: {profile.call_count}")
            print(f"   平均时间: {profile.avg_time:.4f}s")
            print(f"   内存使用: {profile.memory_usage/1024:.2f}KB")
        
        print(f"\n=== 性能瓶颈 ===")
        for bottleneck in report.bottlenecks:
            print(f"- {bottleneck['type']}: {bottleneck.get('function', 'N/A')} "
                  f"(严重程度: {bottleneck['severity']})")
        
        print(f"\n=== 优化建议 ===")
        for recommendation in report.recommendations:
            print(f"- {recommendation}")
    
    # 获取性能摘要
    summary = profiler.get_performance_summary()
    print(f"\n=== 性能摘要 ===")
    print(f"状态: {summary['status']}")
    if 'avg_cpu' in summary:
        print(f"平均CPU: {summary['avg_cpu']:.1f}%")
        print(f"最大CPU: {summary['max_cpu']:.1f}%")
    if 'avg_memory' in summary:
        print(f"平均内存: {summary['avg_memory']:.1f}MB")
        print(f"最大内存: {summary['max_memory']:.1f}MB")

if __name__ == '__main__':
    main()
```

### 内存泄漏检测器
```python
import gc
import tracemalloc
import weakref
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import time
import psutil

class LeakType(Enum):
    """泄漏类型"""
    REFERENCE_CYCLE = "reference_cycle"
    UNRELEASED_RESOURCE = "unreleased_resource"
    GROWING_CACHE = "growing_cache"
    LISTENER_LEAK = "listener_leak"
    THREAD_LEAK = "thread_leak"

@dataclass
class MemoryLeak:
    """内存泄漏"""
    leak_type: LeakType
    object_type: str
    object_count: int
    memory_size: int
    location: str
    description: str

class MemoryLeakDetector:
    def __init__(self):
        self.object_snapshots: List[Dict[str, int]] = []
        self.reference_map: Dict[int, Set[int]] = {}
        self.weak_refs: List[weakref.ref] = []
        self.start_time = None
        self.is_monitoring = False
        
        # 启动内存追踪
        tracemalloc.start()
        
        # 泄漏检测阈值
        self.growth_threshold = 1.5  # 对象数量增长50%
        self.memory_threshold = 10 * 1024 * 1024  # 10MB
    
    def start_monitoring(self):
        """开始内存监控"""
        self.is_monitoring = True
        self.start_time = time.time()
        self.object_snapshots.clear()
        
        # 记录初始状态
        self._take_snapshot()
        
        print("内存泄漏检测已开始")
    
    def stop_monitoring(self) -> List[MemoryLeak]:
        """停止监控并检测泄漏"""
        if not self.is_monitoring:
            return []
        
        self.is_monitoring = False
        
        # 记录最终状态
        self._take_snapshot()
        
        # 检测泄漏
        leaks = self._detect_leaks()
        
        print(f"内存泄漏检测完成，发现 {len(leaks)} 个潜在泄漏")
        return leaks
    
    def _take_snapshot(self):
        """拍摄内存快照"""
        # 获取对象计数
        object_counts = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
        
        # 获取内存使用情况
        current, peak = tracemalloc.get_traced_memory()
        
        snapshot = {
            "timestamp": time.time(),
            "object_counts": object_counts,
            "current_memory": current,
            "peak_memory": peak
        }
        
        self.object_snapshots.append(snapshot)
    
    def _detect_leaks(self) -> List[MemoryLeak]:
        """检测内存泄漏"""
        leaks = []
        
        if len(self.object_snapshots) < 2:
            return leaks
        
        # 比较快照
        first_snapshot = self.object_snapshots[0]
        last_snapshot = self.object_snapshots[-1]
        
        # 检测对象数量增长
        for obj_type, final_count in last_snapshot["object_counts"].items():
            initial_count = first_snapshot["object_counts"].get(obj_type, 0)
            
            if initial_count == 0:
                continue
            
            growth_ratio = final_count / initial_count
            
            if growth_ratio > self.growth_threshold:
                leak = MemoryLeak(
                    leak_type=LeakType.REFERENCE_CYCLE,
                    object_type=obj_type,
                    object_count=final_count - initial_count,
                    memory_size=0,  # 需要进一步计算
                    location="Unknown",
                    description=f"{obj_type} 对象数量增长了 {growth_ratio:.1f} 倍"
                )
                leaks.append(leak)
        
        # 检测内存增长
        memory_growth = last_snapshot["current_memory"] - first_snapshot["current_memory"]
        if memory_growth > self.memory_threshold:
            leak = MemoryLeak(
                leak_type=LeakType.UNRELEASED_RESOURCE,
                object_type="Unknown",
                object_count=0,
                memory_size=memory_growth,
                location="Unknown",
                description=f"内存使用增长了 {memory_growth / 1024 / 1024:.1f}MB"
            )
            leaks.append(leak)
        
        # 检测循环引用
        cycle_leaks = self._detect_reference_cycles()
        leaks.extend(cycle_leaks)
        
        return leaks
    
    def _detect_reference_cycles(self) -> List[MemoryLeak]:
        """检测循环引用"""
        leaks = []
        
        try:
            # 查找循环引用
            found_cycles = gc.collect()
            
            if found_cycles > 0:
                leak = MemoryLeak(
                    leak_type=LeakType.REFERENCE_CYCLE,
                    object_type="Various",
                    object_count=found_cycles,
                    memory_size=0,
                    location="Unknown",
                    description=f"发现 {found_cycles} 个循环引用"
                )
                leaks.append(leak)
        
        except Exception as e:
            print(f"循环引用检测失败: {e}")
        
        return leaks
    
    def analyze_object_references(self, obj_id: int) -> Dict[str, Any]:
        """分析对象引用"""
        analysis = {
            "object_id": obj_id,
            "references": [],
            "referrers": [],
            "potential_leaks": []
        }
        
        try:
            # 获取对象
            obj = None
            for tracked_obj in gc.get_objects():
                if id(tracked_obj) == obj_id:
                    obj = tracked_obj
                    break
            
            if obj is None:
                return analysis
            
            # 分析引用
            analysis["object_type"] = type(obj).__name__
            analysis["object_size"] = sys.getsizeof(obj)
            
            # 获取引用的对象
            try:
                analysis["references"] = [str(type(ref).__name__) for ref in gc.get_referents(obj)]
            except:
                pass
            
            # 获取引用该对象的对象
            try:
                analysis["referrers"] = [str(type(ref).__name__) for ref in gc.get_referrers(obj)]
            except:
                pass
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """获取内存使用摘要"""
        if not self.object_snapshots:
            return {"status": "no_data"}
        
        latest = self.object_snapshots[-1]
        
        summary = {
            "status": "monitoring" if self.is_monitoring else "completed",
            "current_memory": latest["current_memory"],
            "peak_memory": latest["peak_memory"],
            "object_types": len(latest["object_counts"]),
            "total_objects": sum(latest["object_counts"].values())
        }
        
        if len(self.object_snapshots) > 1:
            first = self.object_snapshots[0]
            summary["memory_growth"] = latest["current_memory"] - first["current_memory"]
            summary["object_growth"] = summary["total_objects"] - sum(first["object_counts"].values())
        
        # 找出最大的对象类型
        if latest["object_counts"]:
            largest_type = max(latest["object_counts"].items(), key=lambda x: x[1])
            summary["largest_type"] = {
                "type": largest_type[0],
                "count": largest_type[1]
            }
        
        return summary

# 使用示例
def main():
    print("=== 内存泄漏检测器 ===")
    
    # 创建检测器
    detector = MemoryLeakDetector()
    
    # 开始监控
    detector.start_monitoring()
    
    # 模拟一些可能导致内存泄漏的操作
    print("模拟内存操作...")
    
    # 创建一些对象
    objects = []
    for i in range(1000):
        objects.append({"id": i, "data": "x" * 100})
    
    # 模拟循环引用
    class Node:
        def __init__(self, name):
            self.name = name
            self.children = []
            self.parent = None
    
    # 创建循环引用
    parent = Node("parent")
    child = Node("child")
    parent.children.append(child)
    child.parent = parent
    
    # 模拟缓存增长
    cache = {}
    for i in range(500):
        cache[f"key_{i}"] = "x" * 1000
    
    # 等待一段时间
    time.sleep(1)
    
    # 停止监控
    leaks = detector.stop_monitoring()
    
    if leaks:
        print(f"\n=== 发现的内存泄漏 ===")
        for i, leak in enumerate(leaks, 1):
            print(f"{i}. {leak.leak_type.value}")
            print(f"   对象类型: {leak.object_type}")
            print(f"   对象数量: {leak.object_count}")
            print(f"   内存大小: {leak.memory_size / 1024:.1f}KB")
            print(f"   描述: {leak.description}")
    else:
        print("\n未发现明显的内存泄漏")
    
    # 获取内存摘要
    summary = detector.get_memory_summary()
    print(f"\n=== 内存摘要 ===")
    print(f"状态: {summary['status']}")
    print(f"当前内存: {summary['current_memory'] / 1024 / 1024:.1f}MB")
    print(f"峰值内存: {summary['peak_memory'] / 1024 / 1024:.1f}MB")
    print(f"对象类型数: {summary['object_types']}")
    print(f"总对象数: {summary['total_objects']}")
    
    if 'memory_growth' in summary:
        print(f"内存增长: {summary['memory_growth'] / 1024:.1f}KB")
        print(f"对象增长: {summary['object_growth']}")
    
    if 'largest_type' in summary:
        print(f"最大对象类型: {summary['largest_type']['type']} "
              f"({summary['largest_type']['count']} 个)")

if __name__ == '__main__':
    main()
```

## 性能分析最佳实践

### 分析策略
1. **基线建立**: 建立性能基线，对比分析改进效果
2. **分层分析**: 从系统、应用、代码多个层面分析
3. **持续监控**: 建立持续性能监控机制
4. **问题定位**: 快速定位性能瓶颈和根本原因
5. **效果验证**: 验证优化措施的实际效果

### 优化方法
1. **算法优化**: 选择合适的数据结构和算法
2. **缓存策略**: 实现多级缓存提高响应速度
3. **并发优化**: 合理使用并发和异步处理
4. **资源管理**: 优化内存、CPU、I/O资源使用
5. **架构调整**: 必要时调整系统架构

### 监控指标
1. **响应时间**: 请求处理时间和用户体验
2. **吞吐量**: 系统处理能力指标
3. **资源利用率**: CPU、内存、磁盘、网络使用率
4. **错误率**: 系统错误和异常统计
5. **可用性**: 系统可用性和稳定性指标

### 工具选择
1. **性能分析工具**: 选择适合的分析工具和框架
2. **监控系统**: 建立完善的监控和告警体系
3. **日志分析**: 通过日志分析发现性能问题
4. **压力测试**: 进行压力测试验证性能极限
5. **APM工具**: 使用应用性能管理工具

## 相关技能

- **code-optimization** - 代码优化
- **code-review** - 代码审查
- **testing-strategies** - 测试策略
- **refactoring-patterns** - 重构模式
