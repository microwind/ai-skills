---
name: 日志聚合分析
description: "当设计日志聚合系统时，收集分布式日志，分析日志数据，监控系统状态。验证日志配置，优化存储策略，和最佳实践。"
license: MIT
---

# 日志聚合分析技能

## 概述
日志聚合是现代系统运维的核心组件。分散的日志难以管理和分析，而集中的日志聚合提供了统一查看、快速搜索和智能分析能力。在实施日志聚合前需要理解数据流和存储策略。

**核心原则**: 好的日志聚合应该实时、可靠、可扩展、可搜索。坏的日志聚合会导致日志丢失、查询困难和运维盲区。

## 何时使用

**始终:**
- 设计日志收集系统时
- 分析系统故障时
- 监控应用性能时
- 审计安全事件时
- 优化运维流程时
- 合规性检查时

**触发短语:**
- "日志聚合分析"
- "ELK Stack配置"
- "日志收集策略"
- "日志查询分析"
- "系统监控日志"
- "日志存储优化"

## 日志聚合功能

### 日志收集
- 多源日志采集
- 实时日志流处理
- 日志格式标准化
- 日志过滤和路由
- 日志缓冲和重试

### 日志存储
- 分布式存储架构
- 日志索引和检索
- 数据压缩优化
- 分层存储策略
- 数据生命周期管理

### 日志分析
- 实时日志分析
- 日志模式识别
- 异常检测告警
- 趋势分析报告
- 关联分析引擎

### 日志可视化
- 仪表板展示
- 实时监控视图
- 自定义图表
- 报告生成
- 移动端支持

## 常见日志聚合问题

### 日志丢失问题
```
问题:
高并发下日志丢失或延迟

错误示例:
- 缓冲区溢出
- 网络传输中断
- 存储空间不足
- 处理能力不足

解决方案:
1. 增加缓冲区大小
2. 实施重试机制
3. 监控存储使用
4. 水平扩展处理节点
```

### 查询性能问题
```
问题:
日志查询响应缓慢

错误示例:
- 索引配置不当
- 数据量过大
- 查询语句复杂
- 硬件资源不足

解决方案:
1. 优化索引策略
2. 分片存储数据
3. 简化查询逻辑
4. 升级硬件配置
```

### 存储成本问题
```
问题:
日志存储成本过高

错误示例:
- 数据保留期过长
- 存储层级不合理
- 压缩率低
- 冷热数据混存

解决方案:
1. 设置合理保留期
2. 实施分层存储
3. 优化压缩算法
4. 冷热数据分离
```

### 日志格式问题
```
问题:
日志格式不统一难以分析

错误示例:
- 格式混乱
- 缺少关键字段
- 时间戳不标准
- 编码不一致

解决方案:
1. 统一日志格式
2. 定义标准字段
3. 标准化时间戳
4. 统一字符编码
```

## 代码实现示例

### 日志收集器
```python
import json
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
import gzip
import hashlib

@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: str
    message: str
    source: str
    metadata: Dict[str, Any]
    tags: List[str]

@dataclass
class LogBuffer:
    """日志缓冲区"""
    entries: List[LogEntry]
    max_size: int
    flush_interval: float
    last_flush: float
    
class LogCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.buffer = LogBuffer(
            entries=[],
            max_size=config.get('buffer_size', 1000),
            flush_interval=config.get('flush_interval', 5.0),
            last_flush=time.time()
        )
        self.running = False
        self.flush_thread = None
        self.output_handlers = []
        
    def start(self) -> None:
        """启动日志收集器"""
        self.running = True
        self.flush_thread = threading.Thread(target=self._flush_loop)
        self.flush_thread.daemon = True
        self.flush_thread.start()
        logging.info("日志收集器已启动")
    
    def stop(self) -> None:
        """停止日志收集器"""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join()
        # 强制刷新剩余日志
        self._flush_buffer()
        logging.info("日志收集器已停止")
    
    def collect_log(self, log_entry: LogEntry) -> None:
        """收集日志条目"""
        try:
            # 验证日志格式
            self._validate_log_entry(log_entry)
            
            # 添加到缓冲区
            self.buffer.entries.append(log_entry)
            
            # 检查是否需要立即刷新
            if len(self.buffer.entries) >= self.buffer.max_size:
                self._flush_buffer()
        
        except Exception as e:
            logging.error(f"日志收集失败: {e}")
    
    def _validate_log_entry(self, log_entry: LogEntry) -> None:
        """验证日志条目格式"""
        if not log_entry.timestamp:
            raise ValueError("时间戳不能为空")
        
        if not log_entry.level:
            raise ValueError("日志级别不能为空")
        
        if not log_entry.message:
            raise ValueError("日志消息不能为空")
        
        if not log_entry.source:
            raise ValueError("日志来源不能为空")
        
        # 验证日志级别
        valid_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
        if log_entry.level not in valid_levels:
            raise ValueError(f"无效的日志级别: {log_entry.level}")
    
    def _flush_loop(self) -> None:
        """刷新循环"""
        while self.running:
            try:
                current_time = time.time()
                
                # 检查是否需要刷新
                if (current_time - self.buffer.last_flush >= self.buffer.flush_interval or
                    len(self.buffer.entries) >= self.buffer.max_size):
                    self._flush_buffer()
                
                time.sleep(0.1)
            
            except Exception as e:
                logging.error(f"刷新循环错误: {e}")
                time.sleep(1)
    
    def _flush_buffer(self) -> None:
        """刷新缓冲区"""
        if not self.buffer.entries:
            return
        
        try:
            # 复制并清空缓冲区
            entries_to_flush = self.buffer.entries.copy()
            self.buffer.entries.clear()
            self.buffer.last_flush = time.time()
            
            # 处理日志条目
            for handler in self.output_handlers:
                try:
                    handler.handle_batch(entries_to_flush)
                except Exception as e:
                    logging.error(f"处理器错误: {e}")
        
        except Exception as e:
            logging.error(f"缓冲区刷新失败: {e}")
    
    def add_output_handler(self, handler) -> None:
        """添加输出处理器"""
        self.output_handlers.append(handler)

class FileOutputHandler:
    def __init__(self, file_path: str, compress: bool = True):
        self.file_path = file_path
        self.compress = compress
        self.current_file = None
        self.current_size = 0
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self._open_file()
    
    def _open_file(self) -> None:
        """打开日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.file_path}_{timestamp}.log"
        
        if self.compress:
            filename += ".gz"
        
        self.current_file = open(filename, 'w', encoding='utf-8')
        self.current_size = 0
    
    def handle_batch(self, entries: List[LogEntry]) -> None:
        """处理日志批次"""
        for entry in entries:
            log_line = self._format_log_entry(entry)
            
            if self.compress:
                log_line = gzip.compress(log_line.encode('utf-8'))
            
            self.current_file.write(log_line.decode('utf-8') if isinstance(log_line, bytes) else log_line)
            self.current_size += len(log_line)
            
            # 检查文件大小
            if self.current_size >= self.max_file_size:
                self.current_file.close()
                self._open_file()
    
    def _format_log_entry(self, entry: LogEntry) -> str:
        """格式化日志条目"""
        log_data = {
            'timestamp': entry.timestamp.isoformat(),
            'level': entry.level,
            'message': entry.message,
            'source': entry.source,
            'metadata': entry.metadata,
            'tags': entry.tags
        }
        return json.dumps(log_data, ensure_ascii=False) + '\n'

class ElasticsearchOutputHandler:
    def __init__(self, es_config: Dict[str, Any]):
        self.es_config = es_config
        self.index_prefix = es_config.get('index_prefix', 'logs')
        self.batch_size = es_config.get('batch_size', 100)
        self.buffer = []
        
    def handle_batch(self, entries: List[LogEntry]) -> None:
        """处理日志批次"""
        for entry in entries:
            self.buffer.append(entry)
            
            # 批量提交
            if len(self.buffer) >= self.batch_size:
                self._flush_to_elasticsearch()
        
        # 刷新剩余条目
        if self.buffer:
            self._flush_to_elasticsearch()
    
    def _flush_to_elasticsearch(self) -> None:
        """刷新到Elasticsearch"""
        if not self.buffer:
            return
        
        try:
            # 这里应该使用实际的Elasticsearch客户端
            # 示例代码，需要安装elasticsearch-py
            from elasticsearch import Elasticsearch
            
            es = Elasticsearch([{
                'host': self.es_config.get('host', 'localhost'),
                'port': self.es_config.get('port', 9200)
            }])
            
            # 生成索引名
            index_name = f"{self.index_prefix}-{datetime.now().strftime('%Y.%m.%d')}"
            
            # 批量插入
            bulk_body = []
            for entry in self.buffer:
                # 索引操作
                bulk_body.append({
                    'index': {
                        '_index': index_name,
                        '_id': self._generate_doc_id(entry)
                    }
                })
                
                # 文档内容
                bulk_body.append({
                    'timestamp': entry.timestamp.isoformat(),
                    'level': entry.level,
                    'message': entry.message,
                    'source': entry.source,
                    'metadata': entry.metadata,
                    'tags': entry.tags
                })
            
            # 执行批量插入
            es.bulk(body=bulk_body)
            
            self.buffer.clear()
            
        except Exception as e:
            logging.error(f"Elasticsearch写入失败: {e}")
    
    def _generate_doc_id(self, entry: LogEntry) -> str:
        """生成文档ID"""
        content = f"{entry.timestamp.isoformat()}-{entry.source}-{entry.message}"
        return hashlib.md5(content.encode()).hexdigest()

# 使用示例
def main():
    # 配置日志收集器
    config = {
        'buffer_size': 1000,
        'flush_interval': 5.0
    }
    
    collector = LogCollector(config)
    
    # 添加文件输出处理器
    file_handler = FileOutputHandler('/var/log/app/logs')
    collector.add_output_handler(file_handler)
    
    # 添加Elasticsearch输出处理器
    es_config = {
        'host': 'localhost',
        'port': 9200,
        'index_prefix': 'application-logs',
        'batch_size': 100
    }
    es_handler = ElasticsearchOutputHandler(es_config)
    collector.add_output_handler(es_handler)
    
    # 启动收集器
    collector.start()
    
    try:
        # 模拟日志收集
        for i in range(100):
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level='INFO',
                message=f'测试日志消息 {i}',
                source='test-app',
                metadata={'request_id': f'req-{i}'},
                tags=['test', 'demo']
            )
            collector.collect_log(log_entry)
            time.sleep(0.1)
    
    finally:
        collector.stop()

if __name__ == '__main__':
    main()
```

### 日志分析器
```python
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

@dataclass
class LogPattern:
    """日志模式"""
    pattern: str
    count: int
    samples: List[str]
    first_seen: datetime
    last_seen: datetime

@dataclass
class LogAnomaly:
    """日志异常"""
    type: str
    severity: str
    description: str
    affected_logs: List[str]
    detected_at: datetime

class LogAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.patterns: Dict[str, LogPattern] = {}
        self.anomalies: List[LogAnomaly] = []
        self.statistics = defaultdict(int)
        
    def analyze_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析日志数据"""
        try:
            # 基础统计分析
            self._calculate_basic_stats(logs)
            
            # 模式识别
            self._identify_patterns(logs)
            
            # 异常检测
            self._detect_anomalies(logs)
            
            # 趋势分析
            trends = self._analyze_trends(logs)
            
            # 生成分析报告
            return self._generate_analysis_report(trends)
            
        except Exception as e:
            return {'error': f'日志分析失败: {e}'}
    
    def _calculate_basic_stats(self, logs: List[Dict[str, Any]]) -> None:
        """计算基础统计"""
        total_logs = len(logs)
        if total_logs == 0:
            return
        
        # 按级别统计
        level_counts = Counter()
        source_counts = Counter()
        hourly_counts = defaultdict(int)
        
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            source = log.get('source', 'unknown')
            timestamp = self._parse_timestamp(log.get('timestamp'))
            
            level_counts[level] += 1
            source_counts[source] += 1
            
            if timestamp:
                hour_key = timestamp.strftime('%Y-%m-%d %H:00')
                hourly_counts[hour_key] += 1
        
        self.statistics.update({
            'total_logs': total_logs,
            'level_distribution': dict(level_counts),
            'source_distribution': dict(source_counts),
            'hourly_distribution': dict(hourly_counts),
            'error_rate': level_counts.get('ERROR', 0) / total_logs * 100,
            'warning_rate': level_counts.get('WARN', 0) / total_logs * 100
        })
    
    def _identify_patterns(self, logs: List[Dict[str, Any]]) -> None:
        """识别日志模式"""
        message_patterns = defaultdict(list)
        
        for log in logs:
            message = log.get('message', '')
            if not message:
                continue
            
            # 提取消息模式（替换数字、UUID等为占位符）
            pattern = self._extract_message_pattern(message)
            message_patterns[pattern].append(message)
            
            timestamp = self._parse_timestamp(log.get('timestamp'))
            
            # 更新模式统计
            if pattern not in self.patterns:
                self.patterns[pattern] = LogPattern(
                    pattern=pattern,
                    count=0,
                    samples=[],
                    first_seen=timestamp or datetime.now(),
                    last_seen=timestamp or datetime.now()
                )
            
            pattern_obj = self.patterns[pattern]
            pattern_obj.count += 1
            
            # 保存样本（最多10个）
            if len(pattern_obj.samples) < 10:
                pattern_obj.samples.append(message)
            
            # 更新时间范围
            if timestamp:
                if timestamp < pattern_obj.first_seen:
                    pattern_obj.first_seen = timestamp
                if timestamp > pattern_obj.last_seen:
                    pattern_obj.last_seen = timestamp
        
        # 过滤低频模式
        min_pattern_count = self.config.get('min_pattern_count', 5)
        self.patterns = {
            k: v for k, v in self.patterns.items() 
            if v.count >= min_pattern_count
        }
    
    def _extract_message_pattern(self, message: str) -> str:
        """提取消息模式"""
        # 替换数字
        pattern = re.sub(r'\b\d+\b', '<NUM>', message)
        
        # 替换UUID
        pattern = re.sub(
            r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
            '<UUID>', pattern, flags=re.IGNORECASE
        )
        
        # 替换IP地址
        pattern = re.sub(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            '<IP>', pattern
        )
        
        # 替换时间戳
        pattern = re.sub(
            r'\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b',
            '<TIMESTAMP>', pattern
        )
        
        # 替换文件路径
        pattern = re.sub(
            r'\b[/\\][\w/\\.-]+\b',
            '<PATH>', pattern
        )
        
        return pattern
    
    def _detect_anomalies(self, logs: List[Dict[str, Any]]) -> None:
        """检测日志异常"""
        if not logs:
            return
        
        # 检测错误率异常
        self._detect_error_rate_anomaly(logs)
        
        # 检测日志量异常
        self._detect_volume_anomaly(logs)
        
        # 检测新错误模式
        self._detect_new_error_patterns(logs)
        
        # 检测重复错误
        self._detect_repeated_errors(logs)
    
    def _detect_error_rate_anomaly(self, logs: List[Dict[str, Any]]) -> None:
        """检测错误率异常"""
        # 按时间窗口统计错误率
        window_size = timedelta(minutes=5)
        error_windows = defaultdict(list)
        
        for log in logs:
            timestamp = self._parse_timestamp(log.get('timestamp'))
            if not timestamp:
                continue
            
            window_key = timestamp.replace(second=0, microsecond=0)
            error_windows[window_key].append(log)
        
        # 计算每个窗口的错误率
        error_rates = []
        for window_time, window_logs in error_windows.items():
            total = len(window_logs)
            errors = len([log for log in window_logs if log.get('level') == 'ERROR'])
            error_rate = errors / total if total > 0 else 0
            error_rates.append(error_rate)
        
        if len(error_rates) < 2:
            return
        
        # 计算平均值和标准差
        avg_error_rate = statistics.mean(error_rates)
        std_error_rate = statistics.stdev(error_rates) if len(error_rates) > 1 else 0
        
        # 检测异常窗口
        threshold = avg_error_rate + 2 * std_error_rate
        
        for window_time, window_logs in error_windows.items():
            total = len(window_logs)
            errors = len([log for log in window_logs if log.get('level') == 'ERROR'])
            error_rate = errors / total if total > 0 else 0
            
            if error_rate > threshold and error_rate > 0.1:  # 错误率超过10%
                self.anomalies.append(LogAnomaly(
                    type='error_rate_spike',
                    severity='high',
                    description=f'错误率异常: {error_rate:.2%} (正常: {avg_error_rate:.2%})',
                    affected_logs=[log.get('message', '') for log in window_logs if log.get('level') == 'ERROR'],
                    detected_at=window_time
                ))
    
    def _detect_volume_anomaly(self, logs: List[Dict[str, Any]]) -> None:
        """检测日志量异常"""
        # 按时间窗口统计日志量
        window_size = timedelta(minutes=5)
        volume_windows = defaultdict(int)
        
        for log in logs:
            timestamp = self._parse_timestamp(log.get('timestamp'))
            if not timestamp:
                continue
            
            window_key = timestamp.replace(second=0, microsecond=0)
            volume_windows[window_key] += 1
        
        if len(volume_windows) < 2:
            return
        
        # 计算平均值和标准差
        volumes = list(volume_windows.values())
        avg_volume = statistics.mean(volumes)
        std_volume = statistics.stdev(volumes) if len(volumes) > 1 else 0
        
        # 检测异常窗口
        threshold = avg_volume + 3 * std_volume
        
        for window_time, volume in volume_windows.items():
            if volume > threshold:
                self.anomalies.append(LogAnomaly(
                    type='volume_spike',
                    severity='medium',
                    description=f'日志量异常: {volume} (正常: {avg_volume:.0f})',
                    affected_logs=[],
                    detected_at=window_time
                ))
    
    def _detect_new_error_patterns(self, logs: List[Dict[str, Any]]) -> None:
        """检测新错误模式"""
        # 获取最近的错误日志
        recent_time = datetime.now() - timedelta(hours=1)
        recent_errors = [
            log for log in logs 
            if log.get('level') == 'ERROR' and 
            self._parse_timestamp(log.get('timestamp')) and
            self._parse_timestamp(log.get('timestamp')) > recent_time
        ]
        
        # 提取错误模式
        recent_patterns = set()
        for log in recent_errors:
            message = log.get('message', '')
            pattern = self._extract_message_pattern(message)
            recent_patterns.add(pattern)
        
        # 检查是否为新模式
        for pattern in recent_patterns:
            if pattern not in self.patterns:
                # 查找相关日志
                pattern_logs = [
                    log.get('message', '') for log in recent_errors
                    if self._extract_message_pattern(log.get('message', '')) == pattern
                ]
                
                self.anomalies.append(LogAnomaly(
                    type='new_error_pattern',
                    severity='high',
                    description=f'新错误模式: {pattern}',
                    affected_logs=pattern_logs[:5],  # 最多5个样本
                    detected_at=datetime.now()
                ))
    
    def _detect_repeated_errors(self, logs: List[Dict[str, Any]]) -> None:
        """检测重复错误"""
        error_counts = defaultdict(list)
        
        for log in logs:
            if log.get('level') == 'ERROR':
                message = log.get('message', '')
                pattern = self._extract_message_pattern(message)
                error_counts[pattern].append(log)
        
        # 检查高频错误
        for pattern, error_logs in error_counts.items():
            if len(error_logs) > 10:  # 重复超过10次
                self.anomalies.append(LogAnomaly(
                    type='repeated_error',
                    severity='medium',
                    description=f'重复错误: {pattern} (出现{len(error_logs)}次)',
                    affected_logs=[log.get('message', '') for log in error_logs[:3]],
                    detected_at=datetime.now()
                ))
    
    def _analyze_trends(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析趋势"""
        trends = {}
        
        # 错误率趋势
        error_trend = self._calculate_error_trend(logs)
        trends['error_trend'] = error_trend
        
        # 日志量趋势
        volume_trend = self._calculate_volume_trend(logs)
        trends['volume_trend'] = volume_trend
        
        # 热点模式趋势
        pattern_trend = self._calculate_pattern_trend(logs)
        trends['pattern_trend'] = pattern_trend
        
        return trends
    
    def _calculate_error_trend(self, logs: List[Dict[str, Any]]) -> str:
        """计算错误率趋势"""
        hourly_errors = defaultdict(int)
        hourly_total = defaultdict(int)
        
        for log in logs:
            timestamp = self._parse_timestamp(log.get('timestamp'))
            if not timestamp:
                continue
            
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            hourly_total[hour_key] += 1
            
            if log.get('level') == 'ERROR':
                hourly_errors[hour_key] += 1
        
        # 计算每小时错误率
        hourly_rates = []
        for hour in sorted(hourly_total.keys()):
            rate = hourly_errors[hour] / hourly_total[hour] if hourly_total[hour] > 0 else 0
            hourly_rates.append(rate)
        
        if len(hourly_rates) < 2:
            return 'insufficient_data'
        
        # 简单趋势分析
        recent_avg = statistics.mean(hourly_rates[-3:]) if len(hourly_rates) >= 3 else hourly_rates[-1]
        earlier_avg = statistics.mean(hourly_rates[:-3]) if len(hourly_rates) >= 6 else statistics.mean(hourly_rates[:-1])
        
        if recent_avg > earlier_avg * 1.2:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_volume_trend(self, logs: List[Dict[str, Any]]) -> str:
        """计算日志量趋势"""
        hourly_volumes = defaultdict(int)
        
        for log in logs:
            timestamp = self._parse_timestamp(log.get('timestamp'))
            if not timestamp:
                continue
            
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            hourly_volumes[hour_key] += 1
        
        volumes = [hourly_volumes[hour] for hour in sorted(hourly_volumes.keys())]
        
        if len(volumes) < 2:
            return 'insufficient_data'
        
        recent_avg = statistics.mean(volumes[-3:]) if len(volumes) >= 3 else volumes[-1]
        earlier_avg = statistics.mean(volumes[:-3]) if len(volumes) >= 6 else statistics.mean(volumes[:-1])
        
        if recent_avg > earlier_avg * 1.2:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_pattern_trend(self, logs: List[Dict[str, Any]]) -> Dict[str, str]:
        """计算模式趋势"""
        pattern_trends = {}
        
        for pattern_name, pattern in self.patterns.items():
            # 简单的趋势分析：比较最近和之前的频率
            time_threshold = datetime.now() - timedelta(hours=12)
            
            recent_count = 0
            total_count = pattern.count
            
            # 这里需要实际的日志数据来计算趋势
            # 简化实现
            if total_count > 50:
                pattern_trends[pattern_name] = 'stable'
            elif total_count > 20:
                pattern_trends[pattern_name] = 'increasing'
            else:
                pattern_trends[pattern_name] = 'decreasing'
        
        return pattern_trends
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """解析时间戳"""
        if not timestamp_str:
            return None
        
        try:
            # 尝试ISO格式
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # 尝试其他格式
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y/%m/%d %H:%M:%S'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except ValueError:
                        continue
            except Exception:
                pass
        
        return None
    
    def _generate_analysis_report(self, trends: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""
        return {
            'statistics': dict(self.statistics),
            'patterns': {
                name: {
                    'pattern': pattern.pattern,
                    'count': pattern.count,
                    'samples': pattern.samples[:3],
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat()
                }
                for name, pattern in self.patterns.items()
            },
            'anomalies': [
                {
                    'type': anomaly.type,
                    'severity': anomaly.severity,
                    'description': anomaly.description,
                    'affected_logs_count': len(anomaly.affected_logs),
                    'detected_at': anomaly.detected_at.isoformat()
                }
                for anomaly in self.anomalies
            ],
            'trends': trends,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成摘要"""
        total_anomalies = len(self.anomalies)
        high_severity = len([a for a in self.anomalies if a.severity == 'high'])
        medium_severity = len([a for a in self.anomalies if a.severity == 'medium'])
        
        return {
            'total_patterns': len(self.patterns),
            'total_anomalies': total_anomalies,
            'high_severity_anomalies': high_severity,
            'medium_severity_anomalies': medium_severity,
            'health_score': max(0, 100 - high_severity * 20 - medium_severity * 10),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于异常生成建议
        anomaly_types = [a.type for a in self.anomalies]
        
        if 'error_rate_spike' in anomaly_types:
            recommendations.append("错误率异常，建议检查应用健康状况")
        
        if 'volume_spike' in anomaly_types:
            recommendations.append("日志量异常，建议检查系统负载")
        
        if 'new_error_pattern' in anomaly_types:
            recommendations.append("发现新错误模式，建议及时处理")
        
        if 'repeated_error' in anomaly_types:
            recommendations.append("存在重复错误，建议修复根本原因")
        
        # 基于统计生成建议
        error_rate = self.statistics.get('error_rate', 0)
        if error_rate > 5:
            recommendations.append(f"错误率较高({error_rate:.1f}%)，建议优化代码质量")
        
        return recommendations

# 使用示例
def main():
    # 模拟日志数据
    sample_logs = [
        {
            'timestamp': '2024-01-15T10:00:00Z',
            'level': 'INFO',
            'message': 'User login successful for user_id: 12345',
            'source': 'auth-service',
            'metadata': {'user_id': '12345'}
        },
        {
            'timestamp': '2024-01-15T10:01:00Z',
            'level': 'ERROR',
            'message': 'Database connection failed to host: 192.168.1.100',
            'source': 'db-service',
            'metadata': {'host': '192.168.1.100'}
        },
        {
            'timestamp': '2024-01-15T10:02:00Z',
            'level': 'WARN',
            'message': 'High memory usage detected: 85%',
            'source': 'monitor-service',
            'metadata': {'memory_usage': 85}
        }
    ]
    
    # 配置分析器
    config = {
        'min_pattern_count': 2
    }
    
    analyzer = LogAnalyzer(config)
    report = analyzer.analyze_logs(sample_logs)
    
    print("日志分析报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

## 日志聚合最佳实践

### 收集策略
1. **实时收集**: 确保日志及时传输
2. **缓冲机制**: 防止数据丢失
3. **重试策略**: 处理网络故障
4. **格式标准化**: 统一日志格式
5. **元数据丰富**: 添加上下文信息

### 存储优化
1. **分层存储**: 热数据SSD，冷数据HDD
2. **数据压缩**: 减少存储空间
3. **索引优化**: 提升查询性能
4. **生命周期管理**: 自动清理过期数据
5. **副本策略**: 确保数据可靠性

### 分析策略
1. **模式识别**: 自动识别常见模式
2. **异常检测**: 及时发现异常情况
3. **趋势分析**: 分析长期趋势
4. **关联分析**: 关联不同日志源
5. **智能告警**: 基于分析的告警

### 监控告警
1. **实时监控**: 监控日志系统健康
2. **性能指标**: 监控处理性能
3. **容量规划**: 预测存储需求
4. **告警机制**: 及时通知问题
5. **仪表板**: 可视化监控状态

## 相关技能

- **monitoring-alerting** - 监控告警系统
- **infrastructure-as-code** - 基础设施即代码
- **security-best-practices** - 安全最佳实践
- **ci-cd-pipeline** - CI/CD流水线
