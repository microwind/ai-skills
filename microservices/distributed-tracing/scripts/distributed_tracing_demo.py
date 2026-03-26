#!/usr/bin/env python3
"""
分布式链路追踪演示 - 实现微服务调用链追踪
"""

import asyncio
import json
import time
import uuid
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
from collections import defaultdict
import random

class SpanKind(Enum):
    """Span类型"""
    CLIENT = "client"
    SERVER = "server"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"

class SpanStatus(Enum):
    """Span状态"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class SpanTag:
    """Span标签"""
    key: str
    value: Any

@dataclass
class SpanLog:
    """Span日志"""
    timestamp: float
    level: str
    message: str

@dataclass
class Span:
    """追踪Span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    kind: SpanKind
    status: SpanStatus
    tags: List[SpanTag]
    logs: List[SpanLog]
    service_name: str
    resource: str
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.logs is None:
            self.logs = []
    
    def add_tag(self, key: str, value: Any):
        """添加标签"""
        self.tags.append(SpanTag(key, value))
    
    def add_log(self, level: str, message: str):
        """添加日志"""
        self.logs.append(SpanLog(time.time(), level, message))
    
    def finish(self, status: SpanStatus = SpanStatus.OK):
        """完成Span"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "kind": self.kind.value,
            "status": self.status.value,
            "tags": [{"key": tag.key, "value": tag.value} for tag in self.tags],
            "logs": [{"timestamp": log.timestamp, "level": log.level, "message": log.message} for log in self.logs],
            "service_name": self.service_name,
            "resource": self.resource
        }

class TraceContext:
    """追踪上下文"""
    
    def __init__(self, trace_id: str, span_id: str):
        self.trace_id = trace_id
        self.span_id = span_id
        self.baggage: Dict[str, str] = {}
    
    def add_baggage(self, key: str, value: str):
        """添加行李项"""
        self.baggage[key] = value
    
    def get_baggage(self, key: str) -> Optional[str]:
        """获取行李项"""
        return self.baggage.get(key)

class Tracer:
    """追踪器"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.active_spans: Dict[str, Span] = {}
        self.finished_spans: List[Span] = []
        self.sampler = Sampler(1.0)  # 100%采样率
    
    def start_span(self, operation_name: str, parent_span: Optional[Span] = None, 
                   kind: SpanKind = SpanKind.INTERNAL) -> Span:
        """开始Span"""
        trace_id = parent_span.trace_id if parent_span else str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        parent_span_id = parent_span.span_id if parent_span else None
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            end_time=None,
            duration=None,
            kind=kind,
            status=SpanStatus.OK,
            tags=[],
            logs=[],
            service_name=self.service_name,
            resource=operation_name
        )
        
        # 采样决策
        if not self.sampler.should_sample(trace_id):
            return span  # 不采样，但仍然创建span
        
        self.active_spans[span_id] = span
        
        # 添加默认标签
        span.add_tag("service.name", self.service_name)
        span.add_tag("span.kind", kind.value)
        
        return span
    
    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK):
        """完成Span"""
        span.finish(status)
        
        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]
            self.finished_spans.append(span)
    
    def get_active_span(self) -> Optional[Span]:
        """获取当前活跃的Span"""
        if self.active_spans:
            return list(self.active_spans.values())[-1]
        return None
    
    def get_trace_spans(self, trace_id: str) -> List[Span]:
        """获取指定trace的所有span"""
        return [span for span in self.finished_spans if span.trace_id == trace_id]

class Sampler:
    """采样器"""
    
    def __init__(self, sampling_rate: float = 1.0):
        self.sampling_rate = max(0.0, min(1.0, sampling_rate))
        self.sampled_traces: set = set()
    
    def should_sample(self, trace_id: str) -> bool:
        """决定是否采样"""
        if trace_id in self.sampleed_traces:
            return True
        
        if random.random() < self.sampling_rate:
            self.sampleed_traces.add(trace_id)
            return True
        
        return False

class SpanContext:
    """Span上下文管理器"""
    
    def __init__(self, tracer: Tracer, operation_name: str, parent_span: Optional[Span] = None, 
                 kind: SpanKind = SpanKind.INTERNAL):
        self.tracer = tracer
        self.operation_name = operation_name
        self.parent_span = parent_span
        self.kind = kind
        self.span: Optional[Span] = None
    
    def __enter__(self) -> Span:
        self.span = self.tracer.start_span(self.operation_name, self.parent_span, self.kind)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.tracer.finish_span(self.span, SpanStatus.ERROR)
        else:
            self.tracer.finish_span(self.span, SpanStatus.OK)

class TraceCollector:
    """追踪数据收集器"""
    
    def __init__(self):
        self.spans: List[Span] = []
        self.traces: Dict[str, List[Span]] = defaultdict(list)
    
    def collect_span(self, span: Span):
        """收集Span"""
        self.spans.append(span)
        self.traces[span.trace_id].append(span)
    
    def collect_tracer(self, tracer: Tracer):
        """收集Tracer的所有Span"""
        for span in tracer.finished_spans:
            self.collect_span(span)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """获取Trace"""
        return self.traces.get(trace_id, [])
    
    def get_all_traces(self) -> Dict[str, List[Span]]:
        """获取所有Trace"""
        return dict(self.traces)
    
    def clear(self):
        """清空数据"""
        self.spans.clear()
        self.traces.clear()

class TraceAnalyzer:
    """追踪数据分析器"""
    
    @staticmethod
    def analyze_trace(trace: List[Span]) -> dict:
        """分析单个Trace"""
        if not trace:
            return {}
        
        # 按时间排序
        trace_sorted = sorted(trace, key=lambda x: x.start_time)
        
        # 计算总耗时
        total_duration = max(span.end_time for span in trace) - min(span.start_time for span in trace)
        
        # 统计服务
        services = set(span.service_name for span in trace)
        
        # 统计错误
        error_spans = [span for span in trace if span.status == SpanStatus.ERROR]
        
        # 构建调用树
        call_tree = TraceAnalyzer._build_call_tree(trace_sorted)
        
        return {
            "trace_id": trace[0].trace_id,
            "total_duration": total_duration,
            "span_count": len(trace),
            "services": list(services),
            "error_count": len(error_spans),
            "call_tree": call_tree,
            "spans": [span.to_dict() for span in trace_sorted]
        }
    
    @staticmethod
    def _build_call_tree(spans: List[Span]) -> dict:
        """构建调用树"""
        span_dict = {span.span_id: span for span in spans}
        tree = {}
        
        for span in spans:
            if span.parent_span_id is None:
                # 根span
                tree[span.span_id] = TraceAnalyzer._span_to_node(span, span_dict)
        
        return tree
    
    @staticmethod
    def _span_to_node(span: Span, span_dict: Dict[str, Span]) -> dict:
        """将Span转换为树节点"""
        node = {
            "operation_name": span.operation_name,
            "service_name": span.service_name,
            "duration": span.duration,
            "status": span.status.value,
            "children": []
        }
        
        # 查找子span
        for child_span in span_dict.values():
            if child_span.parent_span_id == span.span_id:
                node["children"].append(TraceAnalyzer._span_to_node(child_span, span_dict))
        
        return node

class Instrumentation:
    """工具类"""
    
    @staticmethod
    def trace_function(tracer: Tracer, operation_name: str, kind: SpanKind = SpanKind.INTERNAL):
        """函数追踪装饰器"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                with SpanContext(tracer, operation_name, kind=kind) as span:
                    span.add_tag("function.name", func.__name__)
                    span.add_log("info", f"开始执行 {func.__name__}")
                    
                    try:
                        result = func(*args, **kwargs)
                        span.add_log("info", f"成功完成 {func.__name__}")
                        return result
                    except Exception as e:
                        span.add_tag("error", True)
                        span.add_tag("error.message", str(e))
                        span.add_log("error", f"执行失败 {func.__name__}: {e}")
                        raise
            return wrapper
        return decorator
    
    @staticmethod
    async def trace_async_function(tracer: Tracer, operation_name: str, kind: SpanKind = SpanKind.INTERNAL):
        """异步函数追踪装饰器"""
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                with SpanContext(tracer, operation_name, kind=kind) as span:
                    span.add_tag("function.name", func.__name__)
                    span.add_log("info", f"开始执行 {func.__name__}")
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.add_log("info", f"成功完成 {func.__name__}")
                        return result
                    except Exception as e:
                        span.add_tag("error", True)
                        span.add_tag("error.message", str(e))
                        span.add_log("error", f"执行失败 {func.__name__}: {e}")
                        raise
            return wrapper
        return decorator

class MicroService:
    """微服务基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.tracer = Tracer(name)
    
    @Instrumentation.trace_function(None, "service_call", SpanKind.CLIENT)
    def call_service(self, service_name: str, operation: str, data: dict) -> dict:
        """调用其他服务"""
        with SpanContext(self.tracer, f"call_{service_name}", kind=SpanKind.CLIENT) as span:
            span.add_tag("target.service", service_name)
            span.add_tag("operation", operation)
            span.add_tag("data.size", len(str(data)))
            
            # 模拟网络调用
            time.sleep(random.uniform(0.1, 0.3))
            
            # 模拟响应
            response = {
                "service": service_name,
                "operation": operation,
                "result": "success",
                "data": data
            }
            
            span.add_tag("response.size", len(str(response)))
            return response
    
    @Instrumentation.trace_async_function(None, "async_operation", SpanKind.INTERNAL)
    async def async_operation(self, operation_name: str, data: dict) -> dict:
        """异步操作"""
        with SpanContext(self.tracer, operation_name, kind=SpanKind.INTERNAL) as span:
            span.add_tag("operation.type", "async")
            span.add_tag("data.size", len(str(data)))
            
            # 模拟异步处理
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            result = {
                "operation": operation_name,
                "processed": True,
                "data": data
            }
            
            return result

async def demonstrate_basic_tracing():
    """演示基本追踪"""
    print("\n🔍 基本追踪演示")
    print("=" * 50)
    
    # 创建追踪器
    tracer = Tracer("user-service")
    
    # 创建根span
    with SpanContext(tracer, "user_registration", SpanKind.SERVER) as root_span:
        root_span.add_tag("user.id", "12345")
        root_span.add_tag("user.email", "user@example.com")
        root_span.add_log("info", "开始用户注册流程")
        
        # 验证用户
        with SpanContext(tracer, "validate_user", SpanKind.INTERNAL) as validate_span:
            validate_span.add_tag("validation.type", "email")
            await asyncio.sleep(0.1)
            validate_span.add_log("info", "用户验证通过")
        
        # 保存用户
        with SpanContext(tracer, "save_user", SpanKind.CLIENT) as save_span:
            save_span.add_tag("database", "postgresql")
            await asyncio.sleep(0.2)
            save_span.add_log("info", "用户保存成功")
        
        # 发送欢迎邮件
        with SpanContext(tracer, "send_welcome_email", SpanKind.PRODUCER) as email_span:
            email_span.add_tag("email.type", "welcome")
            await asyncio.sleep(0.15)
            email_span.add_log("info", "欢迎邮件发送成功")
        
        root_span.add_log("info", "用户注册流程完成")
    
    # 分析追踪结果
    collector = TraceCollector()
    collector.collect_tracer(tracer)
    
    traces = collector.get_all_traces()
    for trace_id, spans in traces.items():
        analysis = TraceAnalyzer.analyze_trace(spans)
        print(f"\n📊 Trace分析:")
        print(f"  Trace ID: {analysis['trace_id']}")
        print(f"  总耗时: {analysis['total_duration']:.3f}s")
        print(f"  Span数量: {analysis['span_count']}")
        print(f"  涉及服务: {', '.join(analysis['services'])}")
        print(f"  错误数量: {analysis['error_count']}")

async def demonstrate_distributed_tracing():
    """演示分布式追踪"""
    print("\n🌐 分布式追踪演示")
    print("=" * 50)
    
    # 创建多个服务的追踪器
    user_tracer = Tracer("user-service")
    order_tracer = Tracer("order-service")
    payment_tracer = Tracer("payment-service")
    
    # 创建服务实例
    user_service = MicroService("user-service")
    order_service = MicroService("order-service")
    payment_service = MicroService("payment-service")
    
    # 创建全局收集器
    collector = TraceCollector()
    
    # 模拟分布式调用链
    with SpanContext(user_tracer, "create_order_flow", SpanKind.SERVER) as root_span:
        root_span.add_tag("user.id", "12345")
        root_span.add_log("info", "开始创建订单流程")
        
        # 调用订单服务
        with SpanContext(user_tracer, "call_order_service", SpanKind.CLIENT) as call_span:
            call_span.add_tag("target.service", "order-service")
            
            # 在订单服务中处理
            with SpanContext(order_tracer, "process_order", SpanKind.SERVER) as order_span:
                order_span.add_tag("order.id", "67890")
                order_span.add_log("info", "开始处理订单")
                
                # 调用支付服务
                with SpanContext(order_tracer, "call_payment_service", SpanKind.CLIENT) as payment_call:
                    payment_call.add_tag("target.service", "payment-service")
                    
                    # 在支付服务中处理
                    with SpanContext(payment_tracer, "process_payment", SpanKind.SERVER) as payment_span:
                        payment_span.add_tag("payment.amount", 99.99)
                        payment_span.add_tag("payment.method", "credit_card")
                        await asyncio.sleep(0.2)
                        payment_span.add_log("info", "支付处理完成")
                
                order_span.add_log("info", "订单处理完成")
        
        root_span.add_log("info", "创建订单流程完成")
    
    # 收集所有追踪数据
    collector.collect_tracer(user_tracer)
    collector.collect_tracer(order_tracer)
    collector.collect_tracer(payment_tracer)
    
    # 分析分布式追踪结果
    traces = collector.get_all_traces()
    for trace_id, spans in traces.items():
        analysis = TraceAnalyzer.analyze_trace(spans)
        print(f"\n🌐 分布式Trace分析:")
        print(f"  Trace ID: {analysis['trace_id']}")
        print(f"  总耗时: {analysis['total_duration']:.3f}s")
        print(f"  Span数量: {analysis['span_count']}")
        print(f"  涉及服务: {', '.join(analysis['services'])}")
        print(f"  调用链: {' -> '.join(span['operation_name'] for span in analysis['spans'])}")

async def demonstrate_error_tracing():
    """演示错误追踪"""
    print("\n❌ 错误追踪演示")
    print("=" * 50)
    
    tracer = Tracer("error-service")
    
    # 模拟有错误的调用链
    with SpanContext(tracer, "error_prone_operation", SpanKind.SERVER) as root_span:
        root_span.add_log("info", "开始可能出错的操作")
        
        try:
            # 第一步成功
            with SpanContext(tracer, "step1", SpanKind.INTERNAL) as step1:
                await asyncio.sleep(0.1)
                step1.add_log("info", "步骤1完成")
            
            # 第二步失败
            with SpanContext(tracer, "step2", SpanKind.INTERNAL) as step2:
                await asyncio.sleep(0.05)
                step2.add_log("info", "步骤2开始")
                
                # 模拟错误
                raise ValueError("模拟的业务错误")
        
        except Exception as e:
            root_span.add_tag("error", True)
            root_span.add_tag("error.message", str(e))
            root_span.add_log("error", f"操作失败: {e}")
    
    # 分析错误追踪
    collector = TraceCollector()
    collector.collect_tracer(tracer)
    
    traces = collector.get_all_traces()
    for trace_id, spans in traces.items():
        analysis = TraceAnalyzer.analyze_trace(spans)
        print(f"\n❌ 错误Trace分析:")
        print(f"  Trace ID: {analysis['trace_id']}")
        print(f"  总耗时: {analysis['total_duration']:.3f}s")
        print(f"  Span数量: {analysis['span_count']}")
        print(f"  错误数量: {analysis['error_count']}")
        
        # 显示错误详情
        for span in analysis['spans']:
            if span['status'] == 'error':
                print(f"  错误Span: {span['operation_name']}")
                for tag in span['tags']:
                    if tag['key'].startswith('error'):
                        print(f"    {tag['key']}: {tag['value']}")

async def demonstrate_performance_analysis():
    """演示性能分析"""
    print("\n📈 性能分析演示")
    print("=" * 50)
    
    tracer = Tracer("performance-service")
    collector = TraceCollector()
    
    # 模拟多个请求
    for i in range(5):
        with SpanContext(tracer, f"request_{i}", SpanKind.SERVER) as root_span:
            root_span.add_tag("request.id", i)
            
            # 模拟不同性能的操作
            operations = [
                ("fast_operation", 0.05),
                ("medium_operation", 0.15),
                ("slow_operation", 0.3)
            ]
            
            for op_name, duration in operations:
                with SpanContext(tracer, op_name, SpanKind.INTERNAL) as span:
                    span.add_tag("operation.type", "cpu_intensive")
                    await asyncio.sleep(duration * random.uniform(0.8, 1.2))
    
    # 收集和分析数据
    collector.collect_tracer(tracer)
    traces = collector.get_all_traces()
    
    # 性能统计
    all_spans = []
    for spans in traces.values():
        all_spans.extend(spans)
    
    # 按操作名称分组统计
    operation_stats = defaultdict(list)
    for span in all_spans:
        if span.duration:
            operation_stats[span.operation_name].append(span.duration)
    
    print(f"\n📊 性能统计:")
    for operation, durations in operation_stats.items():
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print(f"  {operation}:")
        print(f"    平均耗时: {avg_duration:.3f}s")
        print(f"    最大耗时: {max_duration:.3f}s")
        print(f"    最小耗时: {min_duration:.3f}s")
        print(f"    调用次数: {len(durations)}")

async def main():
    """主函数"""
    print("🔍 分布式链路追踪演示")
    print("=" * 60)
    
    try:
        await demonstrate_basic_tracing()
        await demonstrate_distributed_tracing()
        await demonstrate_error_tracing()
        await demonstrate_performance_analysis()
        
        print("\n✅ 链路追踪演示完成!")
        print("\n📚 关键概念:")
        print("  - Trace: 追踪标识符，标识整个调用链")
        print("  - Span: 基本工作单元，表示一个操作")
        print("  - Span Context: 追踪上下文，传递追踪信息")
        print("  - 采样: 控制追踪数据收集的比例")
        print("  - 装饰器: 自动追踪函数执行")
        print("  - 分布式追踪: 跨服务的调用链追踪")
        print("  - 性能分析: 基于追踪数据的性能分析")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
