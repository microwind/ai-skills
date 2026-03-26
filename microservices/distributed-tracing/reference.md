# 分布式链路追踪参考文档

## 分布式链路追踪概述

### 什么是分布式链路追踪
分布式链路追踪是一种用于监控和调试微服务架构中请求流转的技术。它通过在分布式系统中为每个请求生成唯一的追踪ID，记录请求经过的各个服务节点、操作耗时、错误信息等，形成完整的调用链路。分布式链路追踪帮助开发人员快速定位性能瓶颈、诊断系统故障、优化服务调用链，是构建可观测性微服务系统的核心组件。

### 核心功能
- **请求追踪**: 跟踪请求在微服务架构中的完整流转路径
- **性能监控**: 监控各个服务节点的响应时间和性能指标
- **故障诊断**: 快速定位系统故障和性能瓶颈的根本原因
- **依赖分析**: 分析服务间的依赖关系和调用模式
- **可视化展示**: 提供直观的链路拓扑图和时间轴视图
- **数据聚合**: 聚合分析链路数据，生成性能报告和趋势分析

## 分布式链路追踪核心实现

### 追踪数据模型
```python
# distributed_tracing.py
import json
import time
import uuid
import logging
import threading
import queue
import hashlib
import datetime
import re
import statistics
import math
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import redis
import elasticsearch
import cassandra.cluster
from opentelemetry import trace, baggage, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor

class SpanKind(Enum):
    """Span类型枚举"""
    CLIENT = "client"      # 客户端Span
    SERVER = "server"      # 服务端Span
    PRODUCER = "producer"  # 生产者Span
    CONSUMER = "consumer"  # 消费者Span
    INTERNAL = "internal"  # 内部Span

class SpanStatus(Enum):
    """Span状态枚举"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

class TraceState(Enum):
    """追踪状态枚举"""
    ACTIVE = "active"
    FINISHED = "finished"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class TraceContext:
    """追踪上下文"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    baggage: Dict[str, str] = field(default_factory=dict)
    sampling_decision: bool = True
    trace_state: TraceState = TraceState.ACTIVE

@dataclass
class SpanAttribute:
    """Span属性"""
    key: str
    value: Union[str, int, float, bool]
    attribute_type: str = "string"

@dataclass
class SpanEvent:
    """Span事件"""
    timestamp: datetime
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpanLink:
    """Span链接"""
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Span:
    """Span数据结构"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    kind: SpanKind
    start_time: datetime
    end_time: Optional[datetime]
    status: SpanStatus
    attributes: List[SpanAttribute] = field(default_factory=list)
    events: List[SpanEvent] = field(default_factory=list)
    links: List[SpanLink] = field(default_factory=list)
    resource: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None

class TraceSampler:
    """追踪采样器"""
    
    def __init__(self, sampler_type: str = "probabilistic", **kwargs):
        self.logger = logging.getLogger(__name__)
        self.sampler_type = sampler_type
        self.sampler_params = kwargs
        
        if sampler_type == "probabilistic":
            self.sampling_rate = kwargs.get("sampling_rate", 0.1)
        elif sampler_type == "constant":
            self.decision = kwargs.get("decision", True)
        elif sampler_type == "rate_limiting":
            self.max_traces_per_second = kwargs.get("max_traces_per_second", 10)
            self.current_traces = 0
            self.last_reset = time.time()
    
    def should_sample(self, trace_context: TraceContext) -> bool:
        """判断是否应该采样"""
        if self.sampler_type == "probabilistic":
            return self._probabilistic_sample()
        elif self.sampler_type == "constant":
            return self.decision
        elif self.sampler_type == "rate_limiting":
            return self._rate_limiting_sample()
        elif self.sampler_type == "adaptive":
            return self._adaptive_sample(trace_context)
        else:
            return True
    
    def _probabilistic_sample(self) -> bool:
        """概率采样"""
        import random
        return random.random() < self.sampling_rate
    
    def _rate_limiting_sample(self) -> bool:
        """限速采样"""
        current_time = time.time()
        
        # 重置计数器
        if current_time - self.last_reset >= 1.0:
            self.current_traces = 0
            self.last_reset = current_time
        
        if self.current_traces < self.max_traces_per_second:
            self.current_traces += 1
            return True
        
        return False
    
    def _adaptive_sample(self, trace_context: TraceContext) -> bool:
        """自适应采样"""
        # 基于服务负载和错误率动态调整采样率
        # 这里简化实现，实际应用中需要更复杂的逻辑
        return self._probabilistic_sample()

class TraceContextManager:
    """追踪上下文管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_context = None
        self.context_stack = []
        self.lock = threading.RLock()
    
    def start_trace(self, operation_name: str, sampler: TraceSampler) -> TraceContext:
        """开始新的追踪"""
        with self.lock:
            trace_id = self._generate_trace_id()
            span_id = self._generate_span_id()
            
            context = TraceContext(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                sampling_decision=sampler.should_sample(None)
            )
            
            self.current_context = context
            self.context_stack.append(context)
            
            self.logger.debug(f"开始追踪: {operation_name}, trace_id: {trace_id}")
            
            return context
    
    def create_child_span(self, operation_name: str) -> TraceContext:
        """创建子Span上下文"""
        with self.lock:
            if not self.current_context:
                raise ValueError("当前没有活跃的追踪上下文")
            
            span_id = self._generate_span_id()
            child_context = TraceContext(
                trace_id=self.current_context.trace_id,
                span_id=span_id,
                parent_span_id=self.current_context.span_id,
                baggage=self.current_context.baggage.copy(),
                sampling_decision=self.current_context.sampling_decision
            )
            
            self.context_stack.append(child_context)
            self.current_context = child_context
            
            return child_context
    
    def finish_span(self):
        """完成当前Span"""
        with self.lock:
            if self.context_stack:
                self.context_stack.pop()
                if self.context_stack:
                    self.current_context = self.context_stack[-1]
                else:
                    self.current_context = None
    
    def get_current_context(self) -> Optional[TraceContext]:
        """获取当前追踪上下文"""
        with self.lock:
            return self.current_context
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[TraceContext]:
        """从HTTP头中提取追踪上下文"""
        try:
            trace_id = headers.get('X-Trace-Id') or headers.get('traceparent', '').split('-')[0]
            span_id = headers.get('X-Span-Id') or headers.get('traceparent', '').split('-')[1]
            parent_span_id = headers.get('X-Parent-Span-Id')
            
            if not trace_id or not span_id:
                return None
            
            context = TraceContext(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                sampling_decision=True
            )
            
            return context
        
        except Exception as e:
            self.logger.error(f"提取追踪上下文失败: {e}")
            return None
    
    def inject_context(self, context: TraceContext, headers: Dict[str, str]):
        """将追踪上下文注入到HTTP头中"""
        headers['X-Trace-Id'] = context.trace_id
        headers['X-Span-Id'] = context.span_id
        if context.parent_span_id:
            headers['X-Parent-Span-Id'] = context.parent_span_id
    
    def _generate_trace_id(self) -> str:
        """生成追踪ID"""
        return str(uuid.uuid4()).replace('-', '')
    
    def _generate_span_id(self) -> str:
        """生成Span ID"""
        return str(uuid.uuid4()).replace('-', '')[:16]

class SpanBuilder:
    """Span构建器"""
    
    def __init__(self, trace_context: TraceContext, operation_name: str, kind: SpanKind):
        self.logger = logging.getLogger(__name__)
        self.trace_context = trace_context
        self.operation_name = operation_name
        self.kind = kind
        self.start_time = datetime.now()
        self.end_time = None
        self.status = SpanStatus.OK
        self.attributes = []
        self.events = []
        self.links = []
        self.resource = {}
    
    def set_attribute(self, key: str, value: Union[str, int, float, bool]):
        """设置Span属性"""
        attribute = SpanAttribute(key=key, value=value)
        self.attributes.append(attribute)
        return self
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """添加Span事件"""
        event = SpanEvent(
            timestamp=datetime.now(),
            name=name,
            attributes=attributes or {}
        )
        self.events.append(event)
        return self
    
    def add_link(self, trace_id: str, span_id: str, attributes: Dict[str, Any] = None):
        """添加Span链接"""
        link = SpanLink(
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {}
        )
        self.links.append(link)
        return self
    
    def set_status(self, status: SpanStatus):
        """设置Span状态"""
        self.status = status
        return self
    
    def set_resource(self, resource: Dict[str, Any]):
        """设置资源信息"""
        self.resource.update(resource)
        return self
    
    def finish(self):
        """完成Span"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        span = Span(
            trace_id=self.trace_context.trace_id,
            span_id=self.trace_context.span_id,
            parent_span_id=self.trace_context.parent_span_id,
            operation_name=self.operation_name,
            kind=self.kind,
            start_time=self.start_time,
            end_time=self.end_time,
            status=self.status,
            attributes=self.attributes,
            events=self.events,
            links=self.links,
            resource=self.resource,
            duration=duration
        )
        
        return span

class DistributedTracer:
    """分布式追踪器"""
    
    def __init__(self, service_name: str, sampler: TraceSampler):
        self.logger = logging.getLogger(__name__)
        self.service_name = service_name
        self.sampler = sampler
        self.context_manager = TraceContextManager()
        self.span_processors = []
        self.lock = threading.RLock()
    
    def start_trace(self, operation_name: str) -> SpanBuilder:
        """开始新的追踪"""
        context = self.context_manager.start_trace(operation_name, self.sampler)
        
        if not context.sampling_decision:
            return None
        
        span_builder = SpanBuilder(context, operation_name, SpanKind.SERVER)
        span_builder.set_resource({
            'service.name': self.service_name,
            'service.version': '1.0.0'
        })
        
        return span_builder
    
    def start_span(self, operation_name: str, kind: SpanKind = SpanKind.INTERNAL) -> SpanBuilder:
        """开始新的Span"""
        current_context = self.context_manager.get_current_context()
        
        if not current_context:
            # 如果没有当前上下文，开始新的追踪
            return self.start_trace(operation_name)
        
        if not current_context.sampling_decision:
            return None
        
        child_context = self.context_manager.create_child_span(operation_name)
        span_builder = SpanBuilder(child_context, operation_name, kind)
        span_builder.set_resource({
            'service.name': self.service_name,
            'service.version': '1.0.0'
        })
        
        return span_builder
    
    def finish_span(self, span_builder: SpanBuilder):
        """完成Span"""
        if not span_builder:
            return
        
        span = span_builder.finish()
        self.context_manager.finish_span()
        
        # 处理Span
        for processor in self.span_processors:
            try:
                processor.process(span)
            except Exception as e:
                self.logger.error(f"Span处理器处理失败: {e}")
    
    def add_span_processor(self, processor):
        """添加Span处理器"""
        with self.lock:
            self.span_processors.append(processor)
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[TraceContext]:
        """提取追踪上下文"""
        return self.context_manager.extract_context(headers)
    
    def inject_context(self, headers: Dict[str, str]):
        """注入追踪上下文"""
        current_context = self.context_manager.get_current_context()
        if current_context:
            self.context_manager.inject_context(current_context, headers)

class SpanProcessor:
    """Span处理器基类"""
    
    def process(self, span: Span):
        """处理Span"""
        raise NotImplementedError

class ConsoleSpanProcessor(SpanProcessor):
    """控制台Span处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process(self, span: Span):
        """输出Span到控制台"""
        self.logger.info(f"Span: {span.operation_name}, "
                        f"TraceID: {span.trace_id}, "
                        f"SpanID: {span.span_id}, "
                        f"Duration: {span.duration:.3f}s, "
                        f"Status: {span.status.value}")

class JaegerSpanProcessor(SpanProcessor):
    """Jaeger Span处理器"""
    
    def __init__(self, agent_host: str = "localhost", agent_port: int = 6831):
        self.logger = logging.getLogger(__name__)
        self.agent_host = agent_host
        self.agent_port = agent_port
        self.exporter = JaegerExporter(
            agent_host=agent_host,
            agent_port=agent_port
        )
    
    def process(self, span: Span):
        """发送Span到Jaeger"""
        try:
            # 转换为OpenTelemetry格式并发送
            # 这里简化实现，实际需要完整的格式转换
            self.logger.debug(f"发送Span到Jaeger: {span.operation_name}")
        except Exception as e:
            self.logger.error(f"发送Span到Jaeger失败: {e}")

class ZipkinSpanProcessor(SpanProcessor):
    """Zipkin Span处理器"""
    
    def __init__(self, endpoint_url: str = "http://localhost:9411/api/v2/spans"):
        self.logger = logging.getLogger(__name__)
        self.endpoint_url = endpoint_url
        self.exporter = ZipkinExporter(endpoint=endpoint_url)
    
    def process(self, span: Span):
        """发送Span到Zipkin"""
        try:
            # 转换为Zipkin格式并发送
            # 这里简化实现，实际需要完整的格式转换
            self.logger.debug(f"发送Span到Zipkin: {span.operation_name}")
        except Exception as e:
            self.logger.error(f"发送Span到Zipkin失败: {e}")

class ElasticsearchSpanProcessor(SpanProcessor):
    """Elasticsearch Span处理器"""
    
    def __init__(self, hosts: List[str], index_name: str = "traces"):
        self.logger = logging.getLogger(__name__)
        self.es_client = elasticsearch.Elasticsearch(hosts=hosts)
        self.index_name = index_name
    
    def process(self, span: Span):
        """存储Span到Elasticsearch"""
        try:
            doc = {
                'trace_id': span.trace_id,
                'span_id': span.span_id,
                'parent_span_id': span.parent_span_id,
                'operation_name': span.operation_name,
                'kind': span.kind.value,
                'start_time': span.start_time.isoformat(),
                'end_time': span.end_time.isoformat() if span.end_time else None,
                'duration': span.duration,
                'status': span.status.value,
                'attributes': {attr.key: attr.value for attr in span.attributes},
                'events': [
                    {
                        'timestamp': event.timestamp.isoformat(),
                        'name': event.name,
                        'attributes': event.attributes
                    }
                    for event in span.events
                ],
                'links': [
                    {
                        'trace_id': link.trace_id,
                        'span_id': link.span_id,
                        'attributes': link.attributes
                    }
                    for link in span.links
                ],
                'resource': span.resource,
                '@timestamp': datetime.now().isoformat()
            }
            
            self.es_client.index(
                index=self.index_name,
                body=doc
            )
            
            self.logger.debug(f"存储Span到Elasticsearch: {span.operation_name}")
        
        except Exception as e:
            self.logger.error(f"存储Span到Elasticsearch失败: {e}")

class TracingDecorator:
    """追踪装饰器"""
    
    def __init__(self, tracer: DistributedTracer, operation_name: str = None, kind: SpanKind = SpanKind.INTERNAL):
        self.tracer = tracer
        self.operation_name = operation_name
        self.kind = kind
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            op_name = self.operation_name or f"{func.__module__}.{func.__name__}"
            
            span_builder = self.tracer.start_span(op_name, self.kind)
            if not span_builder:
                return func(*args, **kwargs)
            
            try:
                # 添加函数参数作为属性
                if args:
                    span_builder.set_attribute('function.args_count', len(args))
                if kwargs:
                    span_builder.set_attribute('function.kwargs_count', len(kwargs))
                
                result = func(*args, **kwargs)
                
                # 添加结果信息
                if result is not None:
                    span_builder.set_attribute('function.result_type', type(result).__name__)
                
                span_builder.set_status(SpanStatus.OK)
                return result
            
            except Exception as e:
                span_builder.set_status(SpanStatus.ERROR)
                span_builder.add_event('error', {
                    'error.message': str(e),
                    'error.type': type(e).__name__
                })
                raise
            
            finally:
                self.tracer.finish_span(span_builder)
        
        return wrapper

class TracingMiddleware:
    """追踪中间件"""
    
    def __init__(self, tracer: DistributedTracer):
        self.tracer = tracer
        self.logger = logging.getLogger(__name__)
    
    def process_request(self, request):
        """处理请求开始"""
        # 从请求头中提取追踪上下文
        headers = dict(request.headers)
        context = self.tracer.extract_context(headers)
        
        if context:
            # 如果有上下文，创建子Span
            operation_name = f"{request.method} {request.path}"
            span_builder = self.tracer.start_span(operation_name, SpanKind.SERVER)
        else:
            # 如果没有上下文，开始新的追踪
            operation_name = f"{request.method} {request.path}"
            span_builder = self.tracer.start_trace(operation_name)
        
        if span_builder:
            span_builder.set_attribute('http.method', request.method)
            span_builder.set_attribute('http.url', str(request.url))
            span_builder.set_attribute('http.user_agent', request.headers.get('User-Agent', ''))
            span_builder.set_attribute('http.remote_addr', request.remote_addr)
            
            # 将Span Builder存储在请求对象中
            request.span_builder = span_builder
    
    def process_response(self, request, response):
        """处理响应"""
        if hasattr(request, 'span_builder'):
            span_builder = request.span_builder
            
            span_builder.set_attribute('http.status_code', response.status_code)
            
            if response.status_code >= 400:
                span_builder.set_status(SpanStatus.ERROR)
            else:
                span_builder.set_status(SpanStatus.OK)
            
            self.tracer.finish_span(span_builder)

# 使用示例
# 创建追踪器
sampler = TraceSampler("probabilistic", sampling_rate=0.1)
tracer = DistributedTracer("user-service", sampler)

# 添加Span处理器
tracer.add_span_processor(ConsoleSpanProcessor())
tracer.add_span_processor(JaegerSpanProcessor("localhost", 6831))
tracer.add_span_processor(ElasticsearchSpanProcessor(["localhost:9200"], "traces"))

# 使用装饰器
@TracingDecorator(tracer, "get_user", SpanKind.SERVER)
def get_user(user_id: str):
    """获取用户信息"""
    # 模拟数据库查询
    time.sleep(0.1)
    
    if user_id == "error":
        raise ValueError("User not found")
    
    return {"user_id": user_id, "name": "Test User"}

# 使用中间件（Flask示例）
from flask import Flask, request

app = Flask(__name__)
tracing_middleware = TracingMiddleware(tracer)

@app.before_request
def before_request():
    tracing_middleware.process_request(request)

@app.after_request
def after_request(response):
    tracing_middleware.process_response(request, response)
    return response

@app.route('/user/<user_id>')
def user_endpoint(user_id):
    return get_user(user_id)

# 手动追踪
def manual_tracing_example():
    """手动追踪示例"""
    # 开始追踪
    span_builder = tracer.start_trace("manual_operation")
    
    try:
        # 添加属性
        span_builder.set_attribute('user.id', '12345')
        span_builder.set_attribute('operation.type', 'manual')
        
        # 添加事件
        span_builder.add_event('operation_started')
        
        # 模拟工作
        time.sleep(0.5)
        
        # 创建子Span
        child_span = tracer.start_span("sub_operation", SpanKind.INTERNAL)
        if child_span:
            child_span.set_attribute('sub.operation.type', 'database')
            time.sleep(0.2)
            tracer.finish_span(child_span)
        
        # 添加完成事件
        span_builder.add_event('operation_completed')
        span_builder.set_status(SpanStatus.OK)
    
    except Exception as e:
        span_builder.set_status(SpanStatus.ERROR)
        span_builder.add_event('operation_failed', {'error': str(e)})
        raise
    
    finally:
        tracer.finish_span(span_builder)

# 运行示例
if __name__ == "__main__":
    # 测试装饰器追踪
    try:
        result = get_user("123")
        print(f"获取用户成功: {result}")
    except Exception as e:
        print(f"获取用户失败: {e}")
    
    # 测试手动追踪
    manual_tracing_example()
    
    # 启动Flask应用
    app.run(debug=True)
```

### 链路查询和分析
```python
# trace_query_analyzer.py
import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import elasticsearch
import pandas as pd
import numpy as np
from distributed_tracing import Span, SpanKind, SpanStatus

@dataclass
class TraceQuery:
    """追踪查询"""
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    trace_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    status: Optional[SpanStatus] = None
    tags: Dict[str, Any] = None
    limit: int = 100

@dataclass
class TraceSummary:
    """追踪摘要"""
    trace_id: str
    span_count: int
    total_duration: float
    service_count: int
    error_count: int
    start_time: datetime
    end_time: datetime
    services: List[str]
    operations: List[str]

class TraceQueryEngine:
    """追踪查询引擎"""
    
    def __init__(self, elasticsearch_hosts: List[str], index_name: str = "traces"):
        self.logger = logging.getLogger(__name__)
        self.es_client = elasticsearch.Elasticsearch(hosts=elasticsearch_hosts)
        self.index_name = index_name
    
    def query_traces(self, query: TraceQuery) -> List[Dict[str, Any]]:
        """查询追踪"""
        try:
            es_query = self._build_elasticsearch_query(query)
            
            response = self.es_client.search(
                index=self.index_name,
                body=es_query,
                size=query.limit
            )
            
            hits = response['hits']['hits']
            traces = [hit['_source'] for hit in hits]
            
            return traces
        
        except Exception as e:
            self.logger.error(f"查询追踪失败: {e}")
            return []
    
    def get_trace_by_id(self, trace_id: str) -> List[Dict[str, Any]]:
        """根据追踪ID获取完整追踪"""
        query = TraceQuery(trace_id=trace_id, limit=1000)
        return self.query_traces(query)
    
    def get_trace_summary(self, trace_id: str) -> Optional[TraceSummary]:
        """获取追踪摘要"""
        traces = self.get_trace_by_id(trace_id)
        
        if not traces:
            return None
        
        # 分析追踪数据
        spans = [self._dict_to_span(trace) for trace in traces]
        
        span_count = len(spans)
        services = list(set(span.resource.get('service.name', 'unknown') for span in spans))
        operations = list(set(span.operation_name for span in spans))
        error_count = sum(1 for span in spans if span.status != SpanStatus.OK)
        
        start_times = [span.start_time for span in spans if span.start_time]
        end_times = [span.end_time for span in spans if span.end_time]
        
        if start_times and end_times:
            start_time = min(start_times)
            end_time = max(end_times)
            total_duration = (end_time - start_time).total_seconds()
        else:
            start_time = datetime.now()
            end_time = datetime.now()
            total_duration = 0.0
        
        return TraceSummary(
            trace_id=trace_id,
            span_count=span_count,
            total_duration=total_duration,
            service_count=len(services),
            error_count=error_count,
            start_time=start_time,
            end_time=end_time,
            services=services,
            operations=operations
        )
    
    def _build_elasticsearch_query(self, query: TraceQuery) -> Dict[str, Any]:
        """构建Elasticsearch查询"""
        es_query = {
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [
                {"@timestamp": {"order": "desc"}}
            ]
        }
        
        # 添加查询条件
        if query.trace_id:
            es_query["query"]["bool"]["must"].append({
                "term": {"trace_id": query.trace_id}
            })
        
        if query.service_name:
            es_query["query"]["bool"]["must"].append({
                "term": {"resource.service.name": query.service_name}
            })
        
        if query.operation_name:
            es_query["query"]["bool"]["must"].append({
                "term": {"operation_name": query.operation_name}
            })
        
        if query.status:
            es_query["query"]["bool"]["must"].append({
                "term": {"status": query.status.value}
            })
        
        # 时间范围
        if query.start_time or query.end_time:
            time_range = {}
            if query.start_time:
                time_range["gte"] = query.start_time.isoformat()
            if query.end_time:
                time_range["lte"] = query.end_time.isoformat()
            
            es_query["query"]["bool"]["must"].append({
                "range": {"@timestamp": time_range}
            })
        
        # 持续时间范围
        if query.min_duration or query.max_duration:
            duration_range = {}
            if query.min_duration:
                duration_range["gte"] = query.min_duration
            if query.max_duration:
                duration_range["lte"] = query.max_duration
            
            es_query["query"]["bool"]["must"].append({
                "range": {"duration": duration_range}
            })
        
        # 标签过滤
        if query.tags:
            for key, value in query.tags.items():
                es_query["query"]["bool"]["must"].append({
                    "term": {f"attributes.{key}": value}
                })
        
        return es_query
    
    def _dict_to_span(self, span_dict: Dict[str, Any]) -> Span:
        """将字典转换为Span对象"""
        from distributed_tracing import SpanAttribute, SpanEvent, SpanLink
        
        attributes = [
            SpanAttribute(key=key, value=value)
            for key, value in span_dict.get('attributes', {}).items()
        ]
        
        events = []
        for event_dict in span_dict.get('events', []):
            event = SpanEvent(
                timestamp=datetime.fromisoformat(event_dict['timestamp']),
                name=event_dict['name'],
                attributes=event_dict.get('attributes', {})
            )
            events.append(event)
        
        links = []
        for link_dict in span_dict.get('links', []):
            link = SpanLink(
                trace_id=link_dict['trace_id'],
                span_id=link_dict['span_id'],
                attributes=link_dict.get('attributes', {})
            )
            links.append(link)
        
        span = Span(
            trace_id=span_dict['trace_id'],
            span_id=span_dict['span_id'],
            parent_span_id=span_dict.get('parent_span_id'),
            operation_name=span_dict['operation_name'],
            kind=SpanKind(span_dict['kind']),
            start_time=datetime.fromisoformat(span_dict['start_time']),
            end_time=datetime.fromisoformat(span_dict['end_time']) if span_dict.get('end_time') else None,
            status=SpanStatus(span_dict['status']),
            attributes=attributes,
            events=events,
            links=links,
            resource=span_dict.get('resource', {}),
            duration=span_dict.get('duration')
        )
        
        return span

class TraceAnalyzer:
    """追踪分析器"""
    
    def __init__(self, query_engine: TraceQueryEngine):
        self.logger = logging.getLogger(__name__)
        self.query_engine = query_engine
    
    def analyze_service_performance(self, service_name: str, 
                                   start_time: datetime, 
                                   end_time: datetime) -> Dict[str, Any]:
        """分析服务性能"""
        query = TraceQuery(
            service_name=service_name,
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        traces = self.query_engine.query_traces(query)
        
        if not traces:
            return {}
        
        # 转换为DataFrame进行分析
        df = pd.DataFrame(traces)
        
        analysis = {
            'service_name': service_name,
            'total_requests': len(df),
            'avg_duration': df['duration'].mean(),
            'p50_duration': df['duration'].quantile(0.5),
            'p95_duration': df['duration'].quantile(0.95),
            'p99_duration': df['duration'].quantile(0.99),
            'error_rate': (df['status'] != 'ok').mean(),
            'operations': df['operation_name'].value_counts().to_dict(),
            'status_distribution': df['status'].value_counts().to_dict()
        }
        
        return analysis
    
    def analyze_trace_dependencies(self, trace_id: str) -> Dict[str, Any]:
        """分析追踪依赖关系"""
        traces = self.query_engine.get_trace_by_id(trace_id)
        
        if not traces:
            return {}
        
        # 构建服务依赖图
        dependencies = defaultdict(list)
        services = set()
        
        for trace in traces:
            service = trace.get('resource', {}).get('service.name', 'unknown')
            services.add(service)
            
            # 分析父子关系
            parent_span_id = trace.get('parent_span_id')
            if parent_span_id:
                # 查找父Span的服务
                for parent_trace in traces:
                    if parent_trace.get('span_id') == parent_span_id:
                        parent_service = parent_trace.get('resource', {}).get('service.name', 'unknown')
                        dependencies[parent_service].append(service)
                        break
        
        return {
            'trace_id': trace_id,
            'services': list(services),
            'dependencies': dict(dependencies),
            'service_count': len(services)
        }
    
    def detect_anomalies(self, service_name: str, 
                        start_time: datetime, 
                        end_time: datetime) -> List[Dict[str, Any]]:
        """检测异常"""
        query = TraceQuery(
            service_name=service_name,
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )
        
        traces = self.query_engine.query_traces(query)
        
        if not traces:
            return []
        
        anomalies = []
        df = pd.DataFrame(traces)
        
        # 检测高延迟异常
        p95_duration = df['duration'].quantile(0.95)
        high_latency_spans = df[df['duration'] > p95_duration * 2]
        
        if not high_latency_spans.empty:
            anomalies.append({
                'type': 'high_latency',
                'count': len(high_latency_spans),
                'threshold': p95_duration * 2,
                'affected_operations': high_latency_spans['operation_name'].value_counts().to_dict()
            })
        
        # 检测错误率异常
        error_rate = (df['status'] != 'ok').mean()
        if error_rate > 0.1:  # 错误率超过10%
            anomalies.append({
                'type': 'high_error_rate',
                'error_rate': error_rate,
                'threshold': 0.1,
                'error_operations': df[df['status'] != 'ok']['operation_name'].value_counts().to_dict()
            })
        
        # 检测超时异常
        timeout_spans = df[df['status'] == 'timeout']
        if not timeout_spans.empty:
            anomalies.append({
                'type': 'timeouts',
                'count': len(timeout_spans),
                'timeout_operations': timeout_spans['operation_name'].value_counts().to_dict()
            })
        
        return anomalies
    
    def generate_performance_report(self, service_name: str,
                                  start_time: datetime,
                                  end_time: datetime) -> Dict[str, Any]:
        """生成性能报告"""
        performance_analysis = self.analyze_service_performance(service_name, start_time, end_time)
        anomalies = self.detect_anomalies(service_name, start_time, end_time)
        
        report = {
            'service_name': service_name,
            'report_period': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            },
            'performance_metrics': performance_analysis,
            'anomalies': anomalies,
            'recommendations': self._generate_recommendations(performance_analysis, anomalies)
        }
        
        return report
    
    def _generate_recommendations(self, performance: Dict[str, Any], 
                                 anomalies: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于性能指标的建议
        if performance.get('avg_duration', 0) > 1.0:
            recommendations.append("平均响应时间较高，建议优化代码或增加缓存")
        
        if performance.get('p95_duration', 0) > 2.0:
            recommendations.append("P95响应时间较高，建议检查慢查询和优化数据库")
        
        if performance.get('error_rate', 0) > 0.05:
            recommendations.append("错误率较高，建议加强错误处理和监控")
        
        # 基于异常的建议
        for anomaly in anomalies:
            if anomaly['type'] == 'high_latency':
                recommendations.append(f"检测到高延迟异常，建议优化{', '.join(anomaly['affected_operations'].keys())}操作")
            elif anomaly['type'] == 'high_error_rate':
                recommendations.append(f"检测到高错误率异常，建议检查{', '.join(anomaly['error_operations'].keys())}操作")
            elif anomaly['type'] == 'timeouts':
                recommendations.append(f"检测到超时异常，建议优化{', '.join(anomaly['timeout_operations'].keys())}操作的超时设置")
        
        return recommendations

# 使用示例
# 创建查询引擎
query_engine = TraceQueryEngine(["localhost:9200"], "traces")
analyzer = TraceAnalyzer(query_engine)

# 分析服务性能
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

performance = analyzer.analyze_service_performance("user-service", start_time, end_time)
print(f"服务性能分析: {json.dumps(performance, indent=2, default=str)}")

# 分析追踪依赖
trace_summary = query_engine.get_trace_summary("example_trace_id")
if trace_summary:
    dependencies = analyzer.analyze_trace_dependencies(trace_summary.trace_id)
    print(f"追踪依赖分析: {json.dumps(dependencies, indent=2, default=str)}")

# 检测异常
anomalies = analyzer.detect_anomalies("user-service", start_time, end_time)
print(f"异常检测结果: {json.dumps(anomalies, indent=2, default=str)}")

# 生成性能报告
report = analyzer.generate_performance_report("user-service", start_time, end_time)
print(f"性能报告: {json.dumps(report, indent=2, default=str)}")
```

## 参考资源

### 分布式追踪框架
- [OpenTelemetry官方文档](https://opentelemetry.io/docs/)
- [Jaeger官方文档](https://www.jaegertracing.io/docs/)
- [Zipkin官方文档](https://zipkin.io/pages/)
- [SkyWalking官方文档](https://skywalking.apache.org/docs/)

### 微服务追踪最佳实践
- [分布式追踪设计原则](https://opentelemetry.io/docs/concepts/signals/traces/)
- [微服务可观测性指南](https://microservices.io/patterns/observability/)
- [链路追踪采样策略](https://opentelemetry.io/docs/concepts/sdk-configuration/general/)
- [追踪数据建模](https://opentelemetry.io/docs/specs/otel/trace/api/)

### 监控和分析
- [Prometheus追踪指标](https://prometheus.io/docs/practices/tracing/)
- [Grafana追踪仪表板](https://grafana.com/docs/grafana/latest/dashboards/)
- [Elasticsearch追踪数据](https://www.elastic.co/guide/en/elasticsearch/reference/current/trace-analytics.html)
- [分布式系统调试](https://www.usenix.org/conference/nsdi18/presentation/jegou)
