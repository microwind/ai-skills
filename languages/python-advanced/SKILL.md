---
name: Python高级特性
description: "当应用Python高级特性时，分析高级语法，优化代码结构，解决复杂问题。验证特性应用，设计优雅架构，和最佳实践。"
license: MIT
---

# Python高级特性技能

## 概述
Python提供了丰富的高级特性，包括装饰器、生成器、元类、异步编程等，这些特性能够显著提升代码的表达力和性能。不当的高级特性使用会导致代码难以理解、性能下降、维护困难。

**核心原则**: 好的Python高级代码应该优雅简洁、性能优良、可读性强、易于维护。坏的高级代码会过度抽象、性能损耗、难以调试。

## 何时使用

**始终:**
- 构建复杂系统时
- 优化代码性能时
- 处理并发编程时
- 实现框架设计时
- 提升代码复用时
- 解决技术难题时

**触发短语:**
- "Python装饰器怎么用？"
- "生成器和迭代器区别"
- "Python异步编程最佳实践"
- "元类应用场景"
- "Python性能优化技巧"
- "高级数据结构应用"

## Python高级特性技能功能

### 函数式编程
- 装饰器模式
- 生成器和迭代器
- 闭包和高阶函数
- lambda表达式
- 函数式工具

### 面向对象高级
- 元类编程
- 描述符协议
- 抽象基类
- 多重继承
- 魔术方法

### 并发编程
- async/await语法
- 协程和事件循环
- 线程和进程
- 并发数据结构
- 异步上下文管理

### 元编程
- 动态类创建
- 属性访问控制
- 方法动态绑定
- 代码生成技术
- 反射机制

## 常见问题

### 性能问题
- **问题**: 过度使用装饰器导致性能下降
- **原因**: 装饰器增加了函数调用开销
- **解决**: 合理使用装饰器，避免嵌套过深

- **问题**: 生成器使用不当
- **原因**: 不理解生成器的惰性求值特性
- **解决**: 正确理解生成器的工作原理

### 可读性问题
- **问题**: 过度使用元编程
- **原因**: 代码逻辑过于隐晦
- **解决**: 保持代码简洁，避免过度抽象

- **问题**: 链式调用过长
- **原因**: 代码可读性差
- **解决**: 合理拆分链式调用

### 兼容性问题
- **问题**: 异步代码兼容性
- **原因**: 不同Python版本的异步特性差异
- **解决**: 检查目标Python版本，使用合适的异步模式

## 代码示例

### 装饰器高级应用
```python
# 基础装饰器
def timing_decorator(func):
    """计时装饰器"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 执行时间: {end_time - start_time:.4f}秒")
        return result
    return wrapper

# 带参数的装饰器
def retry(max_attempts=3, delay=1, exceptions=(Exception,)):
    """重试装饰器"""
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"第 {attempt + 1} 次尝试失败，{delay}秒后重试...")
                        time.sleep(delay)
                    else:
                        print(f"所有 {max_attempts} 次尝试都失败了")
            
            raise last_exception
        return wrapper
    return decorator

# 缓存装饰器
def cache(max_size=128):
    """LRU缓存装饰器"""
    import functools
    from collections import OrderedDict
    
    def decorator(func):
        cache_dict = OrderedDict()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存键
            key = str(args) + str(sorted(kwargs.items()))
            
            if key in cache_dict:
                # 移动到末尾（最近使用）
                cache_dict.move_to_end(key)
                return cache_dict[key]
            
            # 计算结果
            result = func(*args, **kwargs)
            
            # 添加到缓存
            cache_dict[key] = result
            
            # 限制缓存大小
            if len(cache_dict) > max_size:
                cache_dict.popitem(last=False)  # 移除最久未使用的项
            
            return result
        
        # 添加缓存管理方法
        def cache_clear():
            cache_dict.clear()
        
        def cache_info():
            return {
                'size': len(cache_dict),
                'max_size': max_size,
                'keys': list(cache_dict.keys())
            }
        
        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info
        
        return wrapper
    return decorator

# 权限检查装饰器
def permission_required(permission):
    """权限检查装饰器"""
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'user_permissions'):
                raise PermissionError("用户权限信息未设置")
            
            if permission not in self.user_permissions:
                raise PermissionError(f"需要权限: {permission}")
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

# 使用示例
class UserService:
    def __init__(self, user_permissions):
        self.user_permissions = user_permissions
    
    @timing_decorator
    @retry(max_attempts=3, delay=1)
    @cache(max_size=100)
    def get_user_data(self, user_id):
        """获取用户数据"""
        import random
        import time
        
        # 模拟数据库查询
        time.sleep(0.1)
        
        # 模拟随机失败
        if random.random() < 0.3:
            raise ConnectionError("数据库连接失败")
        
        return {
            'id': user_id,
            'name': f'用户{user_id}',
            'email': f'user{user_id}@example.com'
        }
    
    @permission_required('admin')
    def delete_user(self, user_id):
        """删除用户"""
        return f"用户 {user_id} 已删除"

# 装饰器工厂
def validate_types(**type_hints):
    """类型验证装饰器"""
    import functools
    inspect = __import__('inspect').inspect
    
    def decorator(func):
        signature = inspect.signature(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 绑定参数
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 验证类型
            for param_name, param_value in bound_args.arguments.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    if not isinstance(param_value, expected_type):
                        raise TypeError(
                            f"参数 {param_name} 应该是 {expected_type.__name__} 类型，"
                            f"但得到的是 {type(param_value).__name__}"
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int, email=str)
def create_user(name, age, email):
    return f"创建用户: {name}, {age}岁, {email}"
```

### 生成器和迭代器高级应用
```python
# 自定义迭代器
class FibonacciIterator:
    """斐波那契数列迭代器"""
    
    def __init__(self, max_count=None):
        self.max_count = max_count
        self.current = 0
        self.a, self.b = 0, 1
        self.count = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.max_count and self.count >= self.max_count:
            raise StopIteration
        
        if self.count == 0:
            self.count += 1
            return 0
        
        result = self.b
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return result

# 生成器函数
def prime_generator():
    """素数生成器"""
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    num = 2
    while True:
        if is_prime(num):
            yield num
        num += 1

# 管道生成器
def pipeline_generator():
    """数据处理管道生成器"""
    
    def read_numbers(filename):
        """读取数字"""
        with open(filename, 'r') as f:
            for line in f:
                yield int(line.strip())
    
    def filter_even(numbers):
        """过滤偶数"""
        for num in numbers:
            if num % 2 == 0:
                yield num
    
    def multiply_by_two(numbers):
        """乘以2"""
        for num in numbers:
            yield num * 2
    
    def sum_numbers(numbers):
        """求和"""
        total = 0
        for num in numbers:
            total += num
        return total
    
    # 组合管道
    numbers = read_numbers('numbers.txt')
    even_numbers = filter_even(numbers)
    doubled_numbers = multiply_by_two(even_numbers)
    result = sum_numbers(doubled_numbers)
    
    return result

# 协程生成器
def coroutine_example():
    """协程示例"""
    
    def accumulator():
        """累加器协程"""
        total = 0
        while True:
            value = yield total
            if value is None:
                break
            total += value
        return total
    
    def average_calculator():
        """平均值计算协程"""
        count = 0
        total = 0
        while True:
            value = yield
            if value is None:
                break
            count += 1
            total += value
        return total / count if count > 0 else 0
    
    # 使用协程
    acc = accumulator()
    next(acc)  # 启动协程
    
    print(acc.send(10))  # 10
    print(acc.send(20))  # 30
    print(acc.send(30))  # 60
    
    try:
        acc.send(None)  # 结束协程
    except StopIteration as e:
        print("累加器结果:", e.value)
    
    # 平均值计算
    avg = average_calculator()
    next(avg)
    
    for num in [10, 20, 30, 40, 50]:
        avg.send(num)
    
    try:
        avg.send(None)
    except StopIteration as e:
        print("平均值:", e.value)

# 上下文管理器生成器
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    """文件管理上下文"""
    try:
        f = open(filename, mode)
        yield f
    finally:
        f.close()

@contextmanager
def database_connection(connection_string):
    """数据库连接上下文"""
    import sqlite3
    conn = None
    try:
        conn = sqlite3.connect(connection_string)
        yield conn
    except Exception as e:
        print(f"数据库错误: {e}")
        raise
    finally:
        if conn:
            conn.close()

# 使用示例
def generator_examples():
    # 使用斐波那契迭代器
    fib_iter = FibonacciIterator(10)
    print("前10个斐波那契数:", list(fib_iter))
    
    # 使用素数生成器
    prime_gen = prime_generator()
    first_10_primes = [next(prime_gen) for _ in range(10)]
    print("前10个素数:", first_10_primes)
    
    # 使用上下文管理器
    with file_manager('test.txt', 'w') as f:
        f.write('Hello, World!')
    
    with file_manager('test.txt', 'r') as f:
        content = f.read()
        print("文件内容:", content)
    
    # 协程示例
    coroutine_example()
```

### 元类编程
```python
# 基础元类
class SingletonMeta(type):
    """单例元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    """单例基类"""
    def __init__(self):
        self.value = 0

# 属性验证元类
class ValidatedMeta(type):
    """属性验证元类"""
    
    def __new__(cls, name, bases, namespace):
        # 创建类
        new_class = super().__new__(cls, name, bases, namespace)
        
        # 添加属性验证
        if hasattr(new_class, '_validators'):
            for attr_name, validator in new_class._validators.items():
                setattr(new_class, attr_name, 
                       ValidatedMeta.create_validated_property(attr_name, validator))
        
        return new_class
    
    @staticmethod
    def create_validated_property(attr_name, validator):
        """创建验证属性"""
        private_name = f'_{attr_name}'
        
        def getter(self):
            return getattr(self, private_name)
        
        def setter(self, value):
            if not validator(value):
                raise ValueError(f"属性 {attr_name} 验证失败")
            setattr(self, private_name, value)
        
        return property(getter, setter)

# ORM元类
class ORMMeta(type):
    """ORM元类"""
    
    def __new__(cls, name, bases, namespace):
        # 创建类
        new_class = super().__new__(cls, name, bases, namespace)
        
        # 如果有字段定义，创建表结构
        if hasattr(new_class, '_fields'):
            new_class._table_name = name.lower()
            new_class._field_definitions = {}
            
            for field_name, field_type in new_class._fields.items():
                new_class._field_definitions[field_name] = {
                    'type': field_type,
                    'column': field_name
                }
        
        return new_class

# 描述符
class ValidatedField:
    """验证字段描述符"""
    
    def __init__(self, field_type, min_value=None, max_value=None):
        self.field_type = field_type
        self.min_value = min_value
        self.max_value = max_value
        self.value = None
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.value
    
    def __set__(self, instance, value):
        if not isinstance(value, self.field_type):
            raise TypeError(f"期望 {self.field_type.__name__} 类型")
        
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"值不能小于 {self.min_value}")
        
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"值不能大于 {self.max_value}")
        
        self.value = value

# 抽象基类
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    """数据处理器抽象基类"""
    
    @abstractmethod
    def process(self, data):
        """处理数据"""
        pass
    
    @abstractmethod
    def validate(self, data):
        """验证数据"""
        pass
    
    def process_and_validate(self, data):
        """处理并验证数据"""
        if self.validate(data):
            return self.process(data)
        raise ValueError("数据验证失败")

# 具体实现
class User(DataProcessor):
    _validators = {
        'name': lambda x: isinstance(x, str) and len(x) > 0,
        'age': lambda x: isinstance(x, int) and 0 < x < 150,
        'email': lambda x: isinstance(x, str) and '@' in x
    }
    
    def __init__(self):
        self.name = ''
        self.age = 0
        self.email = ''
    
    def process(self, data):
        return f"处理用户数据: {data}"
    
    def validate(self, data):
        return isinstance(data, dict) and 'name' in data

# 使用元类的模型类
class UserModel(metaclass=ORMMeta):
    _fields = {
        'id': int,
        'name': str,
        'email': str,
        'age': int
    }
    
    def __init__(self, **kwargs):
        for field_name in self._fields:
            setattr(self, field_name, kwargs.get(field_name))

# 带描述符的模型
class Product:
    name = ValidatedField(str, min_value=1)
    price = ValidatedField((int, float), min_value=0)
    stock = ValidatedField(int, min_value=0)
    
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

# 元类示例
def metaclass_examples():
    # 单例模式
    s1 = Singleton()
    s2 = Singleton()
    print("单例测试:", s1 is s2)  # True
    
    # 验证字段
    product = Product("笔记本电脑", 5999.99, 100)
    print("产品信息:", product.name, product.price, product.stock)
    
    # ORM模型
    user = UserModel(id=1, name="张三", email="zhangsan@example.com", age=30)
    print("用户模型:", user._table_name, user._field_definitions)
```

### 异步编程
```python
import asyncio
import aiohttp
import time

# 基础异步函数
async def fetch_data(url):
    """获取数据"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def process_data(data):
    """处理数据"""
    # 模拟数据处理
    await asyncio.sleep(1)
    return f"处理后的数据: {data[:50]}..."

# 异步上下文管理器
class AsyncTimer:
    """异步计时器上下文管理器"""
    
    def __init__(self):
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        print(f"执行时间: {elapsed:.4f}秒")

# 异步迭代器
class AsyncCounter:
    """异步计数器"""
    
    def __init__(self, start, end, step=1):
        self.current = start
        self.end = end
        self.step = step
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.current >= self.end:
            raise StopAsyncIteration
        
        value = self.current
        self.current += self.step
        
        # 模拟异步操作
        await asyncio.sleep(0.1)
        return value

# 异步生成器
async def async_range(start, end, step=1):
    """异步范围生成器"""
    for i in range(start, end, step):
        await asyncio.sleep(0.1)  # 模拟异步操作
        yield i

# 并发任务管理
class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_concurrent=10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks = []
    
    async def add_task(self, coro):
        """添加任务"""
        async def limited_coro():
            async with self.semaphore:
                return await coro
        
        task = asyncio.create_task(limited_coro())
        self.tasks.append(task)
        return task
    
    async def wait_all(self):
        """等待所有任务完成"""
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        return results
    
    async def cancel_all(self):
        """取消所有任务"""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)

# 异步队列处理
async def queue_processor():
    """队列处理器"""
    queue = asyncio.Queue(maxsize=100)
    
    # 生产者
    async def producer(name, count):
        for i in range(count):
            item = f"{name}-item-{i}"
            await queue.put(item)
            print(f"{name} 生产了: {item}")
            await asyncio.sleep(0.1)
    
    # 消费者
    async def consumer(name):
        while True:
            item = await queue.get()
            print(f"{name} 消费了: {item}")
            await asyncio.sleep(0.2)
            queue.task_done()
    
    # 启动生产者和消费者
    producers = [asyncio.create_task(producer(f"Producer-{i}", 5)) 
                for i in range(2)]
    consumers = [asyncio.create_task(consumer(f"Consumer-{i}")) 
                for i in range(3)]
    
    # 等待生产者完成
    await asyncio.gather(*producers)
    
    # 等待队列清空
    await queue.join()
    
    # 取消消费者
    for consumer in consumers:
        consumer.cancel()

# 异步HTTP客户端
class AsyncHttpClient:
    """异步HTTP客户端"""
    
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, endpoint, params=None):
        """GET请求"""
        if not self.session:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")
        
        url = f"{self.base_url}{endpoint}"
        async with self.session.get(url, params=params) as response:
            return await response.json()
    
    async def post(self, endpoint, data=None):
        """POST请求"""
        if not self.session:
            raise RuntimeError("客户端未初始化，请使用 async with 语句")
        
        url = f"{self.base_url}{endpoint}"
        async with self.session.post(url, json=data) as response:
            return await response.json()

# 异步编程示例
async def async_examples():
    # 基础异步操作
    async with AsyncTimer():
        await asyncio.sleep(1)
        print("异步操作完成")
    
    # 异步迭代器
    print("异步计数器:")
    async for number in AsyncCounter(0, 5):
        print(f"计数: {number}")
    
    # 并发任务
    manager = AsyncTaskManager(max_concurrent=3)
    
    tasks = [
        manager.add_task(asyncio.sleep(1)),
        manager.add_task(asyncio.sleep(2)),
        manager.add_task(asyncio.sleep(1.5))
    ]
    
    results = await manager.wait_all()
    print("并发任务结果:", results)
    
    # 异步HTTP客户端
    async with AsyncHttpClient("https://jsonplaceholder.typicode.com") as client:
        try:
            posts = await client.get("/posts", params={"_limit": 5})
            print("获取文章:", len(posts))
        except Exception as e:
            print(f"HTTP请求失败: {e}")

# 运行异步示例
def run_async_examples():
    asyncio.run(async_examples())
```

### 魔术方法
```python
class Vector:
    """自定义向量类"""
    
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    # 字符串表示
    def __str__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z})"
    
    # 算术运算
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented
    
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
        return NotImplemented
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)) and scalar != 0:
            return Vector(self.x / scalar, self.y / scalar, self.z / scalar)
        return NotImplemented
    
    # 比较运算
    def __eq__(self, other):
        if isinstance(other, Vector):
            return (self.x == other.x and 
                   self.y == other.y and 
                   self.z == other.z)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    # 长度
    def __len__(self):
        return 3
    
    # 索引访问
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        else:
            raise IndexError("索引超出范围")
    
    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise IndexError("索引超出范围")
    
    # 迭代器
    def __iter__(self):
        return iter([self.x, self.y, self.z])
    
    # 哈希
    def __hash__(self):
        return hash((self.x, self.y, self.z))
    
    # 布尔值
    def __bool__(self):
        return self.x != 0 or self.y != 0 or self.z != 0
    
    # 绝对值
    def __abs__(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    # 取反
    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

class SmartDict:
    """智能字典"""
    
    def __init__(self, initial_data=None):
        self._data = initial_data or {}
        self._access_count = {}
    
    # 字典接口
    def __getitem__(self, key):
        self._access_count[key] = self._access_count.get(key, 0) + 1
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
        self._access_count[key] = 0
    
    def __delitem__(self, key):
        del self._data[key]
        if key in self._access_count:
            del self._access_count[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def __len__(self):
        return len(self._data)
    
    def __iter__(self):
        return iter(self._data)
    
    # 属性访问
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value
    
    def __delattr__(self, name):
        if name.startswith('_'):
            super().__delattr__(name)
        elif name in self._data:
            del self._data[name]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    # 字符串表示
    def __str__(self):
        return str(self._data)
    
    def __repr__(self):
        return f"SmartDict({self._data})"
    
    # 获取访问统计
    def get_access_stats(self):
        return self._access_count.copy()

# 上下文管理器
class DatabaseConnection:
    """数据库连接上下文管理器"""
    
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
    
    def __enter__(self):
        print("建立数据库连接...")
        # 模拟建立连接
        self.connection = f"连接到 {self.connection_string}"
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("关闭数据库连接...")
        if exc_type:
            print(f"发生异常: {exc_val}")
        self.connection = None
        return True  # 抑制异常

# 函数调用
class FunctionLogger:
    """函数调用日志器"""
    
    def __init__(self, func):
        self.func = func
        self.call_count = 0
    
    def __call__(self, *args, **kwargs):
        self.call_count += 1
        print(f"调用 {self.func.__name__} (第{self.call_count}次)")
        result = self.func(*args, **kwargs)
        print(f"返回结果: {result}")
        return result
    
    @property
    def call_statistics(self):
        return f"{self.func.__name__} 被调用了 {self.call_count} 次"

# 魔术方法示例
def magic_methods_examples():
    # 向量运算
    v1 = Vector(1, 2, 3)
    v2 = Vector(4, 5, 6)
    
    print("向量运算:")
    print(f"v1: {v1}")
    print(f"v2: {v2}")
    print(f"v1 + v2: {v1 + v2}")
    print(f"v1 * 2: {v1 * 2}")
    print(f"|v1|: {abs(v1)}")
    print(f"v1[0]: {v1[0]}")
    
    # 智能字典
    smart_dict = SmartDict({'name': '张三', 'age': 30})
    smart_dict.email = 'zhangsan@example.com'
    
    print(f"\n智能字典:")
    print(f"name: {smart_dict.name}")
    print(f"访问统计: {smart_dict.get_access_stats()}")
    
    # 上下文管理器
    with DatabaseConnection("mysql://localhost/mydb") as conn:
        print(f"使用连接: {conn}")
    
    # 函数调用日志
    @FunctionLogger
    def add(a, b):
        return a + b
    
    print(f"\n函数日志:")
    result = add(5, 3)
    print(add.call_statistics)
```

## 最佳实践

### 代码设计
1. **简洁优先**: 选择最简单有效的解决方案
2. **可读性**: 代码应该易于理解和维护
3. **性能考虑**: 在适当的时候使用高级特性提升性能
4. **测试友好**: 编写易于测试的高级代码

### 性能优化
1. **生成器优化**: 使用生成器处理大数据集
2. **缓存策略**: 合理使用缓存减少重复计算
3. **异步编程**: 使用异步处理I/O密集型任务
4. **内存管理**: 及时释放不需要的资源

### 安全考虑
1. **输入验证**: 使用装饰器验证输入参数
2. **错误处理**: 合理处理异常情况
3. **权限控制**: 实现适当的权限检查机制
4. **数据保护**: 保护敏感数据不被泄露

## 相关技能

- **golang-patterns** - Go语言设计模式
- **rust-systems** - 系统编程
- **javascript-es6** - 现代JavaScript
- **backend** - 后端开发
- **database** - 数据库编程
