# Python高级编程参考文档

## Python高级特性

### 装饰器深入

#### 函数装饰器
```python
# 基础装饰器
def timing_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(1)
    return "Done"

# 带参数的装饰器
def repeat(n_times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(n_times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    return f"Hello, {name}!"

# 类装饰器
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hello():
    print("Hello!")
```

#### 属性装饰器
```python
# 属性装饰器
class Person:
    def __init__(self, name):
        self._name = name
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Name must be a non-empty string")
        self._name = value
    
    @name.deleter
    def name(self):
        print("Deleting name")
        del self._name

# 描述符协议
class ValidatedAttribute:
    def __init__(self, name, validator):
        self.name = name
        self.validator = validator
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"Invalid value for {self.name}")
        obj.__dict__[self.name] = value
    
    def __delete__(self, obj):
        del obj.__dict__[self.name]

class User:
    age = ValidatedAttribute('age', lambda x: isinstance(x, int) and x >= 0)
    email = ValidatedAttribute('email', lambda x: '@' in x)
```

### 元类编程

#### 自定义元类
```python
# 基础元类
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    def __init__(self):
        self.value = 0

# 属性验证元类
class ValidatedMeta(type):
    def __new__(cls, name, bases, namespace):
        # 添加验证方法
        if 'validate' not in namespace:
            def validate(self):
                return True
            namespace['validate'] = validate
        return super().__new__(cls, name, bases, namespace)

# ORM风格元类
class ModelMeta(type):
    def __new__(cls, name, bases, namespace):
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value
        namespace['_fields'] = fields
        return super().__new__(cls, name, bases, namespace)

class Field:
    def __init__(self, field_type, required=True):
        self.field_type = field_type
        self.required = required

class User(metaclass=ModelMeta):
    id = Field(int, required=True)
    name = Field(str, required=True)
    email = Field(str, required=False)
```

### 上下文管理器

#### 自定义上下文管理器
```python
# 基于类的上下文管理器
class DatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
    
    def __enter__(self):
        print(f"Connecting to {self.db_url}")
        self.connection = f"Connection to {self.db_url}"
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing connection")
        self.connection = None
        if exc_type:
            print(f"Error occurred: {exc_val}")
        return True  # 抑制异常

# 基于生成器的上下文管理器
from contextlib import contextmanager

@contextmanager
def temporary_file(content):
    import tempfile
    import os
    
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        yield path
    finally:
        os.unlink(path)

# 嵌套上下文管理器
class Timer:
    def __init__(self):
        self.start = None
        self.end = None
    
    def __enter__(self):
        import time
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end = time.time()
        print(f"Elapsed time: {self.end - self.start:.4f}s")

# 使用示例
with Timer() as timer:
    with temporary_file("Hello, World!") as path:
        print(f"Temporary file: {path}")
        # 处理文件
```

## 异步编程

### asyncio深入

#### 异步函数和协程
```python
import asyncio
import aiohttp

# 基础异步函数
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# 并发执行
async def fetch_multiple(urls):
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# 限制并发数
async def fetch_with_semaphore(urls, max_concurrent=5):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_fetch(url):
        async with semaphore:
            return await fetch_data(url)
    
    tasks = [bounded_fetch(url) for url in urls]
    return await asyncio.gather(*tasks)

# 超时控制
async def fetch_with_timeout(url, timeout=10):
    try:
        async with asyncio.timeout(timeout):
            return await fetch_data(url)
    except asyncio.TimeoutError:
        print(f"Timeout for {url}")
        return None
```

#### 异步上下文管理器
```python
# 异步上下文管理器
class AsyncDatabaseConnection:
    def __init__(self, db_url):
        self.db_url = db_url
        self.connection = None
    
    async def __aenter__(self):
        print(f"Async connecting to {self.db_url}")
        await asyncio.sleep(0.1)  # 模拟异步连接
        self.connection = f"Async connection to {self.db_url}"
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Async closing connection")
        await asyncio.sleep(0.1)  # 模拟异步关闭
        self.connection = None

# 异步迭代器
class AsyncCounter:
    def __init__(self, limit):
        self.limit = limit
        self.count = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.count >= self.limit:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.count += 1
        return self.count

# 使用示例
async def main():
    async with AsyncDatabaseConnection("postgresql://localhost/db") as conn:
        print(f"Connected: {conn}")
    
    async for number in AsyncCounter(5):
        print(f"Count: {number}")
```

### 并发编程

#### 线程和进程
```python
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 线程池
def process_data(data):
    import time
    time.sleep(0.1)
    return data * 2

def thread_pool_example():
    data = range(10)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_data, data))
    return results

# 进程池
def cpu_intensive_task(n):
    import math
    return sum(math.sqrt(i) for i in range(n))

def process_pool_example():
    numbers = [1000000, 2000000, 3000000]
    with ProcessPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(cpu_intensive_task, numbers))
    return results

# 线程安全的单例
class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

#### 生产者消费者模式
```python
import queue
import threading

class ProducerConsumer:
    def __init__(self, max_size=10):
        self.queue = queue.Queue(maxsize=max_size)
        self.producer_threads = []
        self.consumer_threads = []
    
    def producer(self, items):
        for item in items:
            self.queue.put(item)
            print(f"Produced: {item}")
    
    def consumer(self, name):
        while True:
            try:
                item = self.queue.get(timeout=1)
                print(f"Consumer {name} consumed: {item}")
                self.queue.task_done()
            except queue.Empty:
                break
    
    def start(self, producers_data, consumer_names):
        # 启动生产者
        for data in producers_data:
            thread = threading.Thread(target=self.producer, args=(data,))
            thread.start()
            self.producer_threads.append(thread)
        
        # 启动消费者
        for name in consumer_names:
            thread = threading.Thread(target=self.consumer, args=(name,))
            thread.start()
            self.consumer_threads.append(thread)
        
        # 等待完成
        for thread in self.producer_threads:
            thread.join()
        
        self.queue.join()
        
        # 停止消费者
        for _ in self.consumer_threads:
            self.queue.put(None)  # 发送停止信号
        
        for thread in self.consumer_threads:
            thread.join()
```

## 性能优化

### 内存优化

#### 内存分析
```python
import tracemalloc
import gc
import sys

# 内存跟踪
def memory_intensive_function():
    tracemalloc.start()
    
    # 分配大量内存
    data = []
    for i in range(1000000):
        data.append(i * 2)
    
    # 获取内存使用情况
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
    return data

# 对象大小分析
def analyze_object_size():
    import sys
    
    class DataObject:
        def __init__(self):
            self.data = list(range(1000))
            self.name = "test"
    
    obj = DataObject()
    print(f"Object size: {sys.getsizeof(obj)} bytes")
    print(f"Data size: {sys.getsizeof(obj.data)} bytes")
    print(f"Name size: {sys.getsizeof(obj.name)} bytes")

# 内存泄漏检测
def detect_memory_leak():
    gc.collect()  # 强制垃圾回收
    
    # 获取垃圾回收统计
    print(f"GC counts: {gc.get_count()}")
    print(f"GC thresholds: {gc.get_threshold()}")
    
    # 手动触发垃圾回收
    collected = gc.collect()
    print(f"Objects collected: {collected}")
```

#### 内存优化技术
```python
# 使用生成器减少内存使用
def memory_efficient_processing(data):
    # 不好的方式：创建大列表
    # result = [x * 2 for x in data if x % 2 == 0]
    
    # 好的方式：使用生成器
    def process_items():
        for x in data:
            if x % 2 == 0:
                yield x * 2
    
    return process_items()

# 对象池模式
class ObjectPool:
    def __init__(self, create_func, max_size=10):
        self.create_func = create_func
        self.max_size = max_size
        self.pool = []
        self.lock = threading.Lock()
    
    def acquire(self):
        with self.lock:
            if self.pool:
                return self.pool.pop()
            return self.create_func()
    
    def release(self, obj):
        with self.lock:
            if len(self.pool) < self.max_size:
                self.pool.append(obj)

# 弱引用避免循环引用
import weakref

class Node:
    def __init__(self, value):
        self.value = value
        self.parent = None
        self.children = []
    
    def add_child(self, child):
        child.parent = weakref.ref(self)  # 使用弱引用
        self.children.append(child)
```

### 算法优化

#### 算法复杂度分析
```python
import time
from functools import lru_cache

# 性能测试装饰器
def performance_test(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__}: {end - start:.6f} seconds")
        return result
    return wrapper

# 缓存优化
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 向量化操作
import numpy as np

def vectorized_operation(data):
    # 不好的方式：循环
    # result = []
    # for x in data:
    #     result.append(x * 2 + 1)
    # return result
    
    # 好的方式：向量化
    return np.array(data) * 2 + 1

# 批处理优化
def batch_processing(items, batch_size=100):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield process_batch(batch)

def process_batch(batch):
    # 批处理逻辑
    return [item * 2 for item in batch]
```

## 测试高级技术

### 测试框架深入

#### pytest高级特性
```python
import pytest
from unittest.mock import Mock, patch
import tempfile
import os

# 参数化测试
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input * input == expected

# Fixtures
@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_path = f.name
    
    yield temp_path
    
    os.unlink(temp_path)

def test_file_operations(temp_file):
    with open(temp_file, 'r') as f:
        content = f.read()
    assert content == "test content"

# Mock测试
class TestUserService:
    @patch('requests.get')
    def test_get_user(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'id': 1, 'name': 'John'}
        mock_get.return_value = mock_response
        
        from user_service import UserService
        service = UserService()
        user = service.get_user(1)
        
        assert user['name'] == 'John'
        mock_get.assert_called_once_with('http://api.example.com/users/1')

# 异步测试
@pytest.mark.asyncio
async def test_async_function():
    async def async_func():
        await asyncio.sleep(0.1)
        return "result"
    
    result = await async_func()
    assert result == "result"
```

#### 属性测试
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=100))
def test_square_properties(x):
    # 平方数总是非负的
    assert x * x >= 0
    
    # 平方函数满足交换律
    assert x * x == (-x) * (-x)

@given(st.lists(st.integers()))
def test_sort_properties(lst):
    sorted_lst = sorted(lst)
    
    # 排序后的列表长度不变
    assert len(sorted_lst) == len(lst)
    
    # 排序后的列表是有序的
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]

@given(st.text())
def test_string_properties(s):
    # 字符串长度属性
    assert len(s + s) == 2 * len(s)
    assert len(s * 3) == 3 * len(s)
    
    # 字符串连接属性
    assert s + "" == s
    assert "" + s == s
```

### 测试覆盖率

#### 覆盖率配置
```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = htmlcov
```

#### 覆盖率测试
```bash
# 运行覆盖率测试
coverage run -m pytest tests/
coverage report
coverage html

# 目标覆盖率
coverage run --source=src -m pytest tests/
coverage report --fail-under=80
```

## 数据处理高级技术

### Pandas高级操作

#### 数据处理优化
```python
import pandas as pd
import numpy as np

# 向量化操作
def vectorized_operations(df):
    # 不好的方式：逐行处理
    # for index, row in df.iterrows():
    #     df.loc[index, 'new_col'] = row['col1'] * 2
    
    # 好的方式：向量化操作
    df['new_col'] = df['col1'] * 2
    return df

# 分类数据优化
def optimize_memory(df):
    # 将字符串列转换为分类数据
    for col in df.select_dtypes(include=['object']):
        if df[col].nunique() / len(df) < 0.5:  # 唯一值比例小于50%
            df[col] = df[col].astype('category')
    return df

# 分组操作优化
def efficient_groupby(df):
    # 使用agg进行多列聚合
    result = df.groupby('category').agg({
        'value1': ['mean', 'sum'],
        'value2': ['max', 'min'],
        'count': 'size'
    })
    return result
```

### NumPy高级技术

#### 数组操作优化
```python
import numpy as np

# 广播机制
def broadcasting_example():
    a = np.array([[1, 2, 3], [4, 5, 6]])
    b = np.array([10, 20, 30])
    
    # 广播加法
    result = a + b
    return result

# 内存映射文件
def memory_mapping():
    # 创建大型数组的内存映射
    filename = 'large_array.dat'
    shape = (10000, 10000)
    
    # 创建内存映射数组
    mmap_array = np.memmap(filename, dtype='float32', mode='w+', shape=shape)
    
    # 使用数组
    mmap_array[0, 0] = 1.0
    
    # 刷新到磁盘
    mmap_array.flush()
    
    return mmap_array

# 结构化数组
def structured_arrays():
    # 创建结构化数组
    dtype = np.dtype([
        ('name', 'U10'),
        ('age', 'i4'),
        ('height', 'f4')
    ])
    
    data = np.array([
        ('Alice', 25, 1.65),
        ('Bob', 30, 1.80),
        ('Charlie', 35, 1.75)
    ], dtype=dtype)
    
    return data
```

## 网络编程

### 异步网络编程

#### HTTP客户端
```python
import aiohttp
import asyncio

async def fetch_multiple_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = fetch_single_url(session, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def fetch_single_url(session, url):
    try:
        async with session.get(url) as response:
            return {
                'url': url,
                'status': response.status,
                'content': await response.text()
            }
    except Exception as e:
        return {'url': url, 'error': str(e)}

# 带重试的HTTP客户端
async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

### WebSocket编程

#### WebSocket服务器
```python
import asyncio
import websockets
import json

class WebSocketServer:
    def __init__(self):
        self.clients = set()
    
    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.send(json.dumps({
                'type': 'welcome',
                'message': 'Connected to server'
            }))
            
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            self.clients.remove(websocket)
    
    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            response = {
                'type': 'echo',
                'message': f"Received: {data.get('message', '')}"
            }
            await websocket.send(json.dumps(response))
        except json.JSONDecodeError:
            error_response = {
                'type': 'error',
                'message': 'Invalid JSON'
            }
            await websocket.send(json.dumps(error_response))
    
    async def broadcast(self, message):
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def start_server(self, host='localhost', port=8765):
        async with websockets.serve(self.register, host, port):
            print(f"WebSocket server started on {host}:{port}")
            await asyncio.Future()  # 保持服务器运行
```

## 部署和运维

### Docker部署

#### Dockerfile优化
```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 生产阶段
FROM python:3.11-slim

WORKDIR /app

# 复制安装的依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "app.py"]
```

### Kubernetes部署

#### 部署配置
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: python-app
  template:
    metadata:
      labels:
        app: python-app
    spec:
      containers:
      - name: python-app
        image: python-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: python-app-service
spec:
  selector:
    app: python-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 监控和日志

### 应用监控

#### Prometheus指标
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定义指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')

class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        start_time = time.time()
        
        def custom_start_response(status, headers, exc_info=None):
            REQUEST_COUNT.labels(method=environ['REQUEST_METHOD'], 
                               endpoint=environ['PATH_INFO']).inc()
            return start_response(status, headers, exc_info)
        
        response = self.app(environ, custom_start_response)
        
        REQUEST_DURATION.observe(time.time() - start_time)
        return response

# 启动指标服务器
def start_metrics_server(port=8001):
    start_http_server(port)
    print(f"Metrics server started on port {port}")
```

### 结构化日志

#### 日志配置
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 创建处理器
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_structured(self, level, message, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        getattr(self.logger, level.lower())(json.dumps(log_entry))
    
    def info(self, message, **kwargs):
        self.log_structured('INFO', message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log_structured('ERROR', message, **kwargs)

# 使用示例
logger = StructuredLogger('myapp')
logger.info('User login successful', user_id=123, ip='192.168.1.1')
logger.error('Database connection failed', error='Connection timeout', retry_count=3)
```

## 参考资源

### 官方文档
- [Python Documentation](https://docs.python.org/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)

### 高级编程资源
- [Effective Python](https://effectivepython.com/)
- [Fluent Python](https://www.oreilly.com/library/view/fluent-python/9781491946237/)
- [Python Cookbook](https://www.oreilly.com/library/view/python-cookbook-3rd/9781449360379/)

### 性能优化
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [High Performance Python](https://www.oreilly.com/library/view/high-performance-python/9781449361747/)

### 测试资源
- [pytest Documentation](https://docs.pytest.org/)
- [hypothesis Documentation](https://hypothesis.works/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

### 社区资源
- [Real Python](https://realpython.com/)
- [Python Weekly](https://www.pythonweekly.com/)
- [Reddit r/Python](https://www.reddit.com/r/Python/)
