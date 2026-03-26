# 性能分析参考文档

## 性能分析概述

### 什么是性能分析
性能分析是通过监控、测量和分析程序运行时的各种性能指标，识别性能瓶颈、优化机会和潜在问题的过程。它包括CPU使用分析、内存使用分析、I/O性能分析、网络性能分析等多个方面，是优化系统性能和用户体验的关键技术。

### 性能分析价值
- **瓶颈识别**: 快速定位系统性能瓶颈
- **优化指导**: 提供具体的优化建议和方向
- **质量保证**: 确保系统性能满足业务需求
- **容量规划**: 为系统扩容和资源分配提供依据
- **问题诊断**: 快速定位和解决性能问题

### 分析类型
- **CPU性能分析**: 分析处理器使用情况和执行效率
- **内存性能分析**: 分析内存使用、分配和回收情况
- **I/O性能分析**: 分析磁盘和网络I/O性能
- **并发性能分析**: 分析多线程、多进程并发性能
- **分布式性能分析**: 分析分布式系统整体性能

## 性能分析核心实现

### CPU性能分析器
```python
# performance_profiler.py
import time
import psutil
import threading
import multiprocessing
import os
import sys
import signal
import json
import csv
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque
import cProfile
import pstats
import io
import tracemalloc
import gc
import inspect
import functools

class ProfilerType(Enum):
    """分析器类型枚举"""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"
    COMPREHENSIVE = "comprehensive"

class SamplingMode(Enum):
    """采样模式枚举"""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"

@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FunctionProfile:
    """函数性能档案"""
    name: str
    module: str
    line_number: int
    call_count: int
    total_time: float
    average_time: float
    max_time: float
    min_time: float
    cpu_time: float
    memory_usage: float
    call_stack: List[str] = field(default_factory=list)

@dataclass
class PerformanceReport:
    """性能报告"""
    project_name: str
    analysis_type: ProfilerType
    start_time: float
    end_time: float
    duration: float
    metrics: List[PerformanceMetric]
    function_profiles: List[FunctionProfile]
    system_info: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class CPUProfiler:
    """CPU性能分析器"""
    
    def __init__(self, sampling_rate: float = 1000.0):
        self.logger = logging.getLogger(__name__)
        self.sampling_rate = sampling_rate
        self.is_profiling = False
        self.profile_data = defaultdict(list)
        self.call_stack = []
        self.function_times = defaultdict(float)
        self.function_counts = defaultdict(int)
        self.start_time = None
        self.end_time = None
    
    def start_profiling(self):
        """开始CPU性能分析"""
        self.is_profiling = True
        self.start_time = time.time()
        self.call_stack = []
        self.function_times.clear()
        self.function_counts.clear()
        
        # 启动采样线程
        self.sampling_thread = threading.Thread(target=self._sampling_loop)
        self.sampling_thread.daemon = True
        self.sampling_thread.start()
        
        self.logger.info(f"CPU性能分析开始，采样率: {self.sampling_rate} Hz")
    
    def stop_profiling(self) -> Dict[str, Any]:
        """停止CPU性能分析"""
        self.is_profiling = False
        self.end_time = time.time()
        
        # 等待采样线程结束
        if hasattr(self, 'sampling_thread'):
            self.sampling_thread.join(timeout=1.0)
        
        # 生成分析结果
        analysis_result = self._generate_cpu_analysis()
        
        self.logger.info(f"CPU性能分析完成，耗时: {self.end_time - self.start_time:.2f}秒")
        
        return analysis_result
    
    def _sampling_loop(self):
        """采样循环"""
        interval = 1.0 / self.sampling_rate
        
        while self.is_profiling:
            try:
                # 获取当前调用栈
                current_stack = self._get_current_call_stack()
                
                if current_stack:
                    # 记录调用栈
                    self.call_stack.append(current_stack)
                    
                    # 更新函数统计
                    for func_name in current_stack:
                        self.function_times[func_name] += interval
                        self.function_counts[func_name] += 1
                
                # 记录系统CPU使用率
                cpu_percent = psutil.cpu_percent(interval=None)
                self.profile_data['cpu_percent'].append({
                    'timestamp': time.time(),
                    'value': cpu_percent
                })
                
                # 记录进程CPU使用率
                process = psutil.Process()
                process_cpu = process.cpu_percent()
                self.profile_data['process_cpu'].append({
                    'timestamp': time.time(),
                    'value': process_cpu
                })
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"采样错误: {e}")
                break
    
    def _get_current_call_stack(self) -> List[str]:
        """获取当前调用栈"""
        stack = []
        frame = inspect.currentframe()
        
        try:
            while frame:
                frame_info = inspect.getframeinfo(frame)
                if frame_info.function and not frame_info.function.startswith('_'):
                    func_name = f"{frame_info.function}:{frame_info.lineno}"
                    stack.append(func_name)
                frame = frame.f_back
        finally:
            del frame
        
        return stack[::-1]  # 反转栈顺序
    
    def _generate_cpu_analysis(self) -> Dict[str, Any]:
        """生成CPU分析结果"""
        duration = self.end_time - self.start_time
        
        # 分析热点函数
        hot_functions = []
        for func_name, total_time in self.function_times.items():
            call_count = self.function_counts[func_name]
            avg_time = total_time / call_count if call_count > 0 else 0
            
            hot_functions.append({
                'name': func_name,
                'total_time': total_time,
                'call_count': call_count,
                'average_time': avg_time,
                'percentage': (total_time / duration) * 100
            })
        
        # 按总时间排序
        hot_functions.sort(key=lambda x: x['total_time'], reverse=True)
        
        # 计算CPU使用率统计
        cpu_data = self.profile_data.get('cpu_percent', [])
        if cpu_data:
            cpu_values = [item['value'] for item in cpu_data]
            cpu_stats = {
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            }
        else:
            cpu_stats = {}
        
        # 生成优化建议
        recommendations = self._generate_cpu_recommendations(hot_functions, cpu_stats)
        
        return {
            'duration': duration,
            'hot_functions': hot_functions[:20],  # 前20个热点函数
            'cpu_stats': cpu_stats,
            'call_stack_samples': len(self.call_stack),
            'recommendations': recommendations
        }
    
    def _generate_cpu_recommendations(self, hot_functions: List[Dict], cpu_stats: Dict) -> List[str]:
        """生成CPU优化建议"""
        recommendations = []
        
        if not hot_functions:
            return ["未检测到明显的CPU热点函数"]
        
        # 分析最热的函数
        hottest = hot_functions[0]
        if hottest['percentage'] > 20:
            recommendations.append(f"函数 '{hottest['name']}' 占用CPU时间 {hottest['percentage']:.1f}%，建议优先优化")
        
        # 分析调用频率
        high_freq_functions = [f for f in hot_functions if f['call_count'] > 1000]
        if high_freq_functions:
            recommendations.append(f"发现 {len(high_freq_functions)} 个高频调用函数，考虑缓存或批量处理")
        
        # 分析平均执行时间
        slow_functions = [f for f in hot_functions if f['average_time'] > 0.001]
        if slow_functions:
            recommendations.append(f"发现 {len(slow_functions)} 个执行较慢的函数，建议算法优化")
        
        # CPU使用率分析
        if cpu_stats.get('average', 0) > 80:
            recommendations.append("平均CPU使用率较高，建议检查系统负载和进程优先级")
        
        return recommendations

class MemoryProfiler:
    """内存性能分析器"""
    
    def __init__(self, sampling_interval: float = 0.1):
        self.logger = logging.getLogger(__name__)
        self.sampling_interval = sampling_interval
        self.is_profiling = False
        self.memory_data = defaultdict(list)
        self.start_time = None
        self.end_time = None
        self.baseline_memory = None
    
    def start_profiling(self):
        """开始内存性能分析"""
        self.is_profiling = True
        self.start_time = time.time()
        
        # 启动内存跟踪
        tracemalloc.start()
        
        # 记录基线内存
        process = psutil.Process()
        self.baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 启动采样线程
        self.sampling_thread = threading.Thread(target=self._memory_sampling_loop)
        self.sampling_thread.daemon = True
        self.sampling_thread.start()
        
        self.logger.info(f"内存性能分析开始，基线内存: {self.baseline_memory:.2f} MB")
    
    def stop_profiling(self) -> Dict[str, Any]:
        """停止内存性能分析"""
        self.is_profiling = False
        self.end_time = time.time()
        
        # 等待采样线程结束
        if hasattr(self, 'sampling_thread'):
            self.sampling_thread.join(timeout=1.0)
        
        # 获取内存跟踪结果
        snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        # 生成分析结果
        analysis_result = self._generate_memory_analysis(snapshot)
        
        self.logger.info(f"内存性能分析完成，耗时: {self.end_time - self.start_time:.2f}秒")
        
        return analysis_result
    
    def _memory_sampling_loop(self):
        """内存采样循环"""
        while self.is_profiling:
            try:
                # 获取进程内存信息
                process = psutil.Process()
                memory_info = process.memory_info()
                
                # 记录RSS内存
                rss_memory = memory_info.rss / 1024 / 1024  # MB
                self.memory_data['rss_memory'].append({
                    'timestamp': time.time(),
                    'value': rss_memory
                })
                
                # 记录VMS内存
                vms_memory = memory_info.vms / 1024 / 1024  # MB
                self.memory_data['vms_memory'].append({
                    'timestamp': time.time(),
                    'value': vms_memory
                })
                
                # 获取系统内存信息
                system_memory = psutil.virtual_memory()
                self.memory_data['system_memory'].append({
                    'timestamp': time.time(),
                    'value': system_memory.percent
                })
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                self.logger.error(f"内存采样错误: {e}")
                break
    
    def _generate_memory_analysis(self, snapshot) -> Dict[str, Any]:
        """生成内存分析结果"""
        duration = self.end_time - self.start_time
        
        # 分析内存使用趋势
        rss_data = self.memory_data.get('rss_memory', [])
        if rss_data:
            rss_values = [item['value'] for item in rss_data]
            memory_growth = rss_values[-1] - rss_values[0] if len(rss_values) > 1 else 0
            
            memory_stats = {
                'initial': rss_values[0] if rss_values else 0,
                'final': rss_values[-1] if rss_values else 0,
                'peak': max(rss_values) if rss_values else 0,
                'average': sum(rss_values) / len(rss_values) if rss_values else 0,
                'growth': memory_growth,
                'growth_rate': memory_growth / duration if duration > 0 else 0
            }
        else:
            memory_stats = {}
        
        # 分析内存分配热点
        top_stats = snapshot.statistics('lineno')
        allocation_hotspots = []
        
        for stat in top_stats[:20]:  # 前20个热点
            allocation_hotspots.append({
                'filename': stat.traceback[0].filename,
                'line': stat.traceback[0].lineno,
                'size': stat.size / 1024,  # KB
                'count': stat.count,
                'average_size': stat.size / stat.count if stat.count > 0 else 0
            })
        
        # 检测可能的内存泄漏
        memory_leaks = self._detect_memory_leaks(rss_data)
        
        # 生成优化建议
        recommendations = self._generate_memory_recommendations(memory_stats, allocation_hotspots, memory_leaks)
        
        return {
            'duration': duration,
            'memory_stats': memory_stats,
            'allocation_hotspots': allocation_hotspots,
            'memory_leaks': memory_leaks,
            'recommendations': recommendations
        }
    
    def _detect_memory_leaks(self, memory_data: List[Dict]) -> List[Dict]:
        """检测内存泄漏"""
        leaks = []
        
        if len(memory_data) < 10:
            return leaks
        
        # 分析内存增长趋势
        values = [item['value'] for item in memory_data]
        timestamps = [item['timestamp'] for item in memory_data]
        
        # 计算移动平均
        window_size = min(10, len(values) // 4)
        if window_size > 1:
            moving_avg = []
            for i in range(window_size, len(values)):
                avg = sum(values[i-window_size:i]) / window_size
                moving_avg.append(avg)
            
            # 检测持续增长
            growth_count = 0
            for i in range(1, len(moving_avg)):
                if moving_avg[i] > moving_avg[i-1]:
                    growth_count += 1
                else:
                    growth_count = 0
                
                if growth_count >= len(moving_avg) // 2:  # 超过一半时间在增长
                    leaks.append({
                        'type': 'continuous_growth',
                        'start_time': timestamps[i],
                        'growth_rate': (moving_avg[-1] - moving_avg[0]) / (timestamps[-1] - timestamps[i]),
                        'severity': 'high' if growth_count > len(moving_avg) * 0.8 else 'medium'
                    })
                    break
        
        return leaks
    
    def _generate_memory_recommendations(self, memory_stats: Dict, 
                                       allocation_hotspots: List[Dict], 
                                       memory_leaks: List[Dict]) -> List[str]:
        """生成内存优化建议"""
        recommendations = []
        
        # 内存增长分析
        if memory_stats.get('growth', 0) > 100:  # 增长超过100MB
            recommendations.append(f"内存增长 {memory_stats['growth']:.1f} MB，建议检查是否存在内存泄漏")
        
        # 内存分配热点分析
        if allocation_hotspots:
            top_hotspot = allocation_hotspots[0]
            if top_hotspot['size'] > 1024:  # 超过1MB
                recommendations.append(f"发现大内存分配热点: {top_hotspot['filename']}:{top_hotspot['line']}，建议优化")
        
        # 内存泄漏检测
        if memory_leaks:
            for leak in memory_leaks:
                if leak['severity'] == 'high':
                    recommendations.append("检测到严重的内存泄漏，建议立即检查对象引用和垃圾回收")
        
        # 内存使用率分析
        system_memory = self.memory_data.get('system_memory', [])
        if system_memory:
            avg_usage = sum(item['value'] for item in system_memory) / len(system_memory)
            if avg_usage > 80:
                recommendations.append("系统内存使用率较高，建议优化内存使用或增加内存")
        
        return recommendations

class IOProfiler:
    """I/O性能分析器"""
    
    def __init__(self, sampling_interval: float = 0.1):
        self.logger = logging.getLogger(__name__)
        self.sampling_interval = sampling_interval
        self.is_profiling = False
        self.io_data = defaultdict(list)
        self.start_time = None
        self.end_time = None
        self.io_counters = {}
    
    def start_profiling(self):
        """开始I/O性能分析"""
        self.is_profiling = True
        self.start_time = time.time()
        
        # 记录初始I/O计数器
        process = psutil.Process()
        self.io_counters = process.io_counters()
        
        # 启动采样线程
        self.sampling_thread = threading.Thread(target=self._io_sampling_loop)
        self.sampling_thread.daemon = True
        self.sampling_thread.start()
        
        self.logger.info("I/O性能分析开始")
    
    def stop_profiling(self) -> Dict[str, Any]:
        """停止I/O性能分析"""
        self.is_profiling = False
        self.end_time = time.time()
        
        # 等待采样线程结束
        if hasattr(self, 'sampling_thread'):
            self.sampling_thread.join(timeout=1.0)
        
        # 生成分析结果
        analysis_result = self._generate_io_analysis()
        
        self.logger.info(f"I/O性能分析完成，耗时: {self.end_time - self.start_time:.2f}秒")
        
        return analysis_result
    
    def _io_sampling_loop(self):
        """I/O采样循环"""
        while self.is_profiling:
            try:
                # 获取进程I/O计数器
                process = psutil.Process()
                try:
                    io_counters = process.io_counters()
                    
                    # 计算I/O增量
                    read_bytes = io_counters.read_bytes - self.io_counters.read_bytes
                    write_bytes = io_counters.write_bytes - self.io_counters.write_bytes
                    read_count = io_counters.read_count - self.io_counters.read_count
                    write_count = io_counters.write_count - self.io_counters.write_count
                    
                    # 记录I/O数据
                    self.io_data['read_bytes'].append({
                        'timestamp': time.time(),
                        'value': read_bytes
                    })
                    
                    self.io_data['write_bytes'].append({
                        'timestamp': time.time(),
                        'value': write_bytes
                    })
                    
                    self.io_data['read_count'].append({
                        'timestamp': time.time(),
                        'value': read_count
                    })
                    
                    self.io_data['write_count'].append({
                        'timestamp': time.time(),
                        'value': write_count
                    })
                    
                    # 更新基准计数器
                    self.io_counters = io_counters
                    
                except (AttributeError, OSError):
                    # 某些系统可能不支持I/O计数器
                    pass
                
                # 获取磁盘I/O统计
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    self.io_data['disk_read_bytes'].append({
                        'timestamp': time.time(),
                        'value': disk_io.read_bytes
                    })
                    
                    self.io_data['disk_write_bytes'].append({
                        'timestamp': time.time(),
                        'value': disk_io.write_bytes
                    })
                
                # 获取网络I/O统计
                net_io = psutil.net_io_counters()
                if net_io:
                    self.io_data['net_bytes_sent'].append({
                        'timestamp': time.time(),
                        'value': net_io.bytes_sent
                    })
                    
                    self.io_data['net_bytes_recv'].append({
                        'timestamp': time.time(),
                        'value': net_io.bytes_recv
                    })
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                self.logger.error(f"I/O采样错误: {e}")
                break
    
    def _generate_io_analysis(self) -> Dict[str, Any]:
        """生成I/O分析结果"""
        duration = self.end_time - self.start_time
        
        # 分析进程I/O
        process_io_stats = {}
        for io_type in ['read_bytes', 'write_bytes', 'read_count', 'write_count']:
            data = self.io_data.get(io_type, [])
            if data:
                values = [item['value'] for item in data]
                total = sum(values)
                rate = total / duration if duration > 0 else 0
                
                process_io_stats[io_type] = {
                    'total': total,
                    'rate': rate,
                    'average': sum(values) / len(values) if values else 0
                }
        
        # 分析磁盘I/O
        disk_io_stats = {}
        for io_type in ['disk_read_bytes', 'disk_write_bytes']:
            data = self.io_data.get(io_type, [])
            if data:
                values = [item['value'] for item in data]
                if len(values) > 1:
                    total = values[-1] - values[0]  # 增量
                    rate = total / duration if duration > 0 else 0
                    
                    disk_io_stats[io_type] = {
                        'total': total,
                        'rate': rate
                    }
        
        # 分析网络I/O
        net_io_stats = {}
        for io_type in ['net_bytes_sent', 'net_bytes_recv']:
            data = self.io_data.get(io_type, [])
            if data:
                values = [item['value'] for item in data]
                if len(values) > 1:
                    total = values[-1] - values[0]  # 增量
                    rate = total / duration if duration > 0 else 0
                    
                    net_io_stats[io_type] = {
                        'total': total,
                        'rate': rate
                    }
        
        # 生成优化建议
        recommendations = self._generate_io_recommendations(process_io_stats, disk_io_stats, net_io_stats)
        
        return {
            'duration': duration,
            'process_io': process_io_stats,
            'disk_io': disk_io_stats,
            'network_io': net_io_stats,
            'recommendations': recommendations
        }
    
    def _generate_io_recommendations(self, process_io: Dict, disk_io: Dict, net_io: Dict) -> List[str]:
        """生成I/O优化建议"""
        recommendations = []
        
        # 进程I/O分析
        read_rate = process_io.get('read_bytes', {}).get('rate', 0)
        write_rate = process_io.get('write_bytes', {}).get('rate', 0)
        
        if read_rate > 1024 * 1024:  # 超过1MB/s
            recommendations.append(f"读取速率较高 ({read_rate/1024/1024:.2f} MB/s)，建议优化读取策略")
        
        if write_rate > 1024 * 1024:  # 超过1MB/s
            recommendations.append(f"写入速率较高 ({write_rate/1024/1024:.2f} MB/s)，建议优化写入策略")
        
        # 磁盘I/O分析
        disk_read_rate = disk_io.get('disk_read_bytes', {}).get('rate', 0)
        disk_write_rate = disk_io.get('disk_write_bytes', {}).get('rate', 0)
        
        if disk_read_rate > 10 * 1024 * 1024:  # 超过10MB/s
            recommendations.append("磁盘读取速率较高，建议考虑缓存或批量读取")
        
        if disk_write_rate > 10 * 1024 * 1024:  # 超过10MB/s
            recommendations.append("磁盘写入速率较高，建议考虑缓冲或批量写入")
        
        # 网络I/O分析
        net_send_rate = net_io.get('net_bytes_sent', {}).get('rate', 0)
        net_recv_rate = net_io.get('net_bytes_recv', {}).get('rate', 0)
        
        if net_send_rate > 10 * 1024 * 1024:  # 超过10MB/s
            recommendations.append("网络发送速率较高，建议优化数据压缩或批量发送")
        
        if net_recv_rate > 10 * 1024 * 1024:  # 超过10MB/s
            recommendations.append("网络接收速率较高，建议优化数据接收策略")
        
        return recommendations

class PerformanceAnalyzer:
    """性能分析器主类"""
    
    def __init__(self, project_name: str):
        self.logger = logging.getLogger(__name__)
        self.project_name = project_name
        self.profilers = {}
        self.reports = []
    
    def analyze_performance(self, source_dir: str, 
                          analysis_types: List[ProfilerType] = None,
                          duration: float = 60.0) -> PerformanceReport:
        """执行性能分析"""
        if analysis_types is None:
            analysis_types = [ProfilerType.CPU, ProfilerType.MEMORY]
        
        self.logger.info(f"开始性能分析项目: {self.project_name}")
        
        start_time = time.time()
        
        # 创建分析器
        for analysis_type in analysis_types:
            if analysis_type == ProfilerType.CPU:
                self.profilers[analysis_type] = CPUProfiler()
            elif analysis_type == ProfilerType.MEMORY:
                self.profilers[analysis_type] = MemoryProfiler()
            elif analysis_type == ProfilerType.IO:
                self.profilers[analysis_type] = IOProfiler()
        
        # 启动所有分析器
        for profiler in self.profilers.values():
            profiler.start_profiling()
        
        # 等待分析完成
        time.sleep(duration)
        
        # 停止所有分析器
        analysis_results = {}
        for analysis_type, profiler in self.profilers.items():
            analysis_results[analysis_type] = profiler.stop_profiling()
        
        end_time = time.time()
        
        # 生成综合报告
        report = self._generate_comprehensive_report(analysis_results, start_time, end_time)
        
        self.reports.append(report)
        
        self.logger.info(f"性能分析完成，生成报告: {report.project_name}")
        
        return report
    
    def _generate_comprehensive_report(self, analysis_results: Dict, 
                                     start_time: float, 
                                     end_time: float) -> PerformanceReport:
        """生成综合性能报告"""
        # 收集所有性能指标
        metrics = []
        function_profiles = []
        recommendations = []
        
        # 处理CPU分析结果
        if ProfilerType.CPU in analysis_results:
            cpu_result = analysis_results[ProfilerType.CPU]
            
            # 添加CPU指标
            metrics.append(PerformanceMetric(
                name="CPU使用率",
                value=cpu_result.get('cpu_stats', {}).get('average', 0),
                unit="%",
                timestamp=start_time
            ))
            
            # 添加函数性能档案
            for hot_func in cpu_result.get('hot_functions', []):
                profile = FunctionProfile(
                    name=hot_func['name'],
                    module="unknown",
                    line_number=0,
                    call_count=hot_func['call_count'],
                    total_time=hot_func['total_time'],
                    average_time=hot_func['average_time'],
                    max_time=0,
                    min_time=0,
                    cpu_time=hot_func['total_time'],
                    memory_usage=0
                )
                function_profiles.append(profile)
            
            recommendations.extend(cpu_result.get('recommendations', []))
        
        # 处理内存分析结果
        if ProfilerType.MEMORY in analysis_results:
            memory_result = analysis_results[ProfilerType.MEMORY]
            memory_stats = memory_result.get('memory_stats', {})
            
            # 添加内存指标
            metrics.append(PerformanceMetric(
                name="内存使用量",
                value=memory_stats.get('final', 0),
                unit="MB",
                timestamp=start_time
            ))
            
            metrics.append(PerformanceMetric(
                name="内存增长率",
                value=memory_stats.get('growth_rate', 0),
                unit="MB/s",
                timestamp=start_time
            ))
            
            recommendations.extend(memory_result.get('recommendations', []))
        
        # 处理I/O分析结果
        if ProfilerType.IO in analysis_results:
            io_result = analysis_results[ProfilerType.IO]
            
            # 添加I/O指标
            process_io = io_result.get('process_io', {})
            read_rate = process_io.get('read_bytes', {}).get('rate', 0)
            write_rate = process_io.get('write_bytes', {}).get('rate', 0)
            
            metrics.append(PerformanceMetric(
                name="读取速率",
                value=read_rate,
                unit="bytes/s",
                timestamp=start_time
            ))
            
            metrics.append(PerformanceMetric(
                name="写入速率",
                value=write_rate,
                unit="bytes/s",
                timestamp=start_time
            ))
            
            recommendations.extend(io_result.get('recommendations', []))
        
        # 获取系统信息
        system_info = self._get_system_info()
        
        # 创建报告
        report = PerformanceReport(
            project_name=self.project_name,
            analysis_type=ProfilerType.COMPREHENSIVE,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            metrics=metrics,
            function_profiles=function_profiles,
            system_info=system_info,
            recommendations=recommendations,
            metadata={
                'analysis_types': list(analysis_results.keys()),
                'analysis_results': analysis_results
            }
        )
        
        return report
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': psutil.disk_usage('/').total,
                'platform': sys.platform,
                'python_version': sys.version
            }
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def save_report(self, report: PerformanceReport, output_path: str):
        """保存性能报告"""
        report_data = asdict(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"性能报告已保存到: {output_path}")

# 使用示例
if __name__ == "__main__":
    # 创建性能分析器
    analyzer = PerformanceAnalyzer("MyProject")
    
    # 执行性能分析
    report = analyzer.analyze_performance(
        source_dir="src",
        analysis_types=[ProfilerType.CPU, ProfilerType.MEMORY, ProfilerType.IO],
        duration=30.0
    )
    
    # 保存报告
    analyzer.save_report(report, "performance_report.json")
    
    # 输出关键信息
    print(f"分析项目: {report.project_name}")
    print(f"分析时长: {report.duration:.2f} 秒")
    print(f"性能指标数量: {len(report.metrics)}")
    print(f"函数档案数量: {len(report.function_profiles)}")
    print(f"优化建议数量: {len(report.recommendations)}")
    
    print("\n优化建议:")
    for i, recommendation in enumerate(report.recommendations, 1):
        print(f"{i}. {recommendation}")
```

## 参考资源

### 性能分析工具
- [Python性能分析](https://docs.python.org/3/library/profile.html)
- [cProfile](https://docs.python.org/3/library/profile.html#module-cProfile)
- [memory_profiler](https://pypi.org/project/memory-profiler/)
- [line_profiler](https://pypi.org/project/line-profiler/)
- [py-spy](https://github.com/benfred/py-spy)

### 系统监控工具
- [psutil](https://psutil.readthedocs.io/)
- [tracemalloc](https://docs.python.org/3/library/tracemalloc.html)
- [perf](https://perf.wiki.kernel.org/)
- [Valgrind](https://valgrind.org/)
- [Intel VTune](https://software.intel.com/content/www/us/en/develop/tools/vtune-profiler.html)

### 性能优化指南
- [Python性能优化技巧](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [系统性能调优](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/monitoring_and_managing_system_performance/index)
- [内存优化最佳实践](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/)
- [I/O性能优化](https://www.kernel.org/doc/Documentation/block/iostats.txt)

### 可视化工具
- [Flame Graph](http://www.brendangregg.com/flamegraphs.html)
- [Grafana](https://grafana.com/)
- [Kibana](https://www.elastic.co/kibana/)
- [PyCharm Profiler](https://www.jetbrains.com/pycharm/features/profiler.html)
