# Python代码分析器参考文档

## 代码分析概述

### 什么是代码分析
代码分析是通过自动化工具对源代码进行检查、评估和优化的过程，旨在提高代码质量、安全性和性能。

### 分析维度
- **代码质量**: 编码规范、可读性、可维护性
- **安全性**: 漏洞检测、安全编码规范、依赖安全
- **性能**: 算法效率、资源使用、性能瓶颈
- **架构**: 设计模式、模块依赖、代码结构
- **测试**: 测试覆盖率、测试质量、测试策略

### 分析工具生态
- **静态分析**: 不运行代码，直接分析源代码
- **动态分析**: 运行时分析代码行为
- **混合分析**: 结合静态和动态分析
- **交互式分析**: IDE集成实时分析

## 代码质量分析

### 静态代码分析工具

#### Pylint配置
```python
# .pylintrc
[MASTER]
# 指定Python版本
python-version = 3.9

# 指定检查的文件或目录
ignore-paths = ^(\.git|\.venv|venv|__pycache__|build|dist)$

[MESSAGES CONTROL]
# 启用的检查器
enable = all
# 禁用的检查器
disable = 
    raw-checker-failed,
    bad-inline-option,
    locally-disabled,
    suppressed-message,
    useless-suppression,
    too-many-public-methods,
    too-few-public-methods,
    too-many-instance-attributes,
    too-many-arguments,
    too-many-locals,
    too-many-branches,
    too-many-statements,
    too-many-lines

# 设置最低评分
fail-under = 8.0

[BASIC]
# 命名规范
variable-name-rgx = ^[a-z_][a-z0-9_]{2,30}$
const-name-rgx = ^[A-Z_][A-Z0-9_]{2,30}$
class-name-rgx = ^[A-Z_][a-zA-Z0-9]+$
function-name-rgx = ^[a-z_][a-z0-9_]{2,30}$

[DESIGN]
# 复杂度限制
max-args = 7
max-locals = 15
max-returns = 6
max-branches = 12
max-statements = 50
max-parents = 7
max-attributes = 7
min-public-methods = 2
max-public-methods = 20

[FORMAT]
# 格式化设置
max-line-length = 88
indent-string = '    '
```

#### Flake8配置
```ini
# .flake8
[flake8]
max-line-length = 88
extend-ignore = 
    E203,  # whitespace before ':'
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
    C901,  # too complex (handled by mccabe)

exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    build,
    dist,
    *.egg-info

per-file-ignores =
    __init__.py:F401  # imported but unused
    tests/*:S101  # assert usage in tests

# McCabe复杂度检查
max-complexity = 10
```

#### Black配置
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### 代码复杂度分析

#### 圈复杂度分析
```python
# 复杂度示例 - 高复杂度
def process_order(order, user, payment_method, shipping_method, discount_code):
    complexity = 0
    
    # 条件1
    if not order:
        return None
    complexity += 1
    
    # 条件2
    if not user:
        return None
    complexity += 1
    
    # 条件3
    if not payment_method:
        return None
    complexity += 1
    
    # 条件4
    if not shipping_method:
        return None
    complexity += 1
    
    # 条件5
    if discount_code:
        if discount_code.startswith('SUMMER'):
            if user.is_vip:
                discount = 0.2
            else:
                discount = 0.1
        elif discount_code.startswith('WINTER'):
            if order.total > 1000:
                discount = 0.15
            else:
                discount = 0.05
        else:
            discount = 0.0
        complexity += 3  # 嵌套条件
    
    # 条件6
    if payment_method.type == 'credit_card':
        if payment_method.expired:
            return None
        complexity += 1
    
    # 条件7
    if shipping_method.international:
        if not user.address.international:
            return None
        complexity += 1
    
    # 总复杂度: 1 + 1 + 1 + 1 + 3 + 1 + 1 = 9 (过高)
    
    return process_payment(order, user, payment_method, shipping_method, discount)

# 重构后 - 低复杂度
def process_order(order, user, payment_method, shipping_method, discount_code):
    if not validate_order_data(order, user, payment_method, shipping_method):
        return None
    
    discount = calculate_discount(discount_code, user, order)
    
    if not validate_payment_method(payment_method):
        return None
    
    if not validate_shipping_method(shipping_method, user):
        return None
    
    return process_payment(order, user, payment_method, shipping_method, discount)

def validate_order_data(order, user, payment_method, shipping_method):
    return all([order, user, payment_method, shipping_method])

def calculate_discount(discount_code, user, order):
    if not discount_code:
        return 0.0
    
    discount_calculator = DiscountCalculator()
    return discount_calculator.calculate(discount_code, user, order)

def validate_payment_method(payment_method):
    if payment_method.type == 'credit_card':
        return not payment_method.expired
    return True

def validate_shipping_method(shipping_method, user):
    if shipping_method.international:
        return user.address.international
    return True
```

#### 认知复杂度分析
```python
# 认知复杂度示例 - 高认知复杂度
def validate_user_input(data):
    result = True
    
    # 条件1
    if not data:
        result = False
    
    # 条件2
    if 'email' not in data:
        result = False
    elif '@' not in data['email']:
        result = False
    elif '.' not in data['email'].split('@')[1]:
        result = False
    
    # 条件3
    if 'age' not in data:
        result = False
    elif not isinstance(data['age'], int):
        result = False
    elif data['age'] < 18 or data['age'] > 120:
        result = False
    
    # 条件4
    if 'name' not in data:
        result = False
    elif len(data['name']) < 2:
        result = False
    elif not data['name'].replace(' ', '').isalpha():
        result = False
    
    # 条件5
    if 'phone' in data:
        if not data['phone'].isdigit():
            result = False
        elif len(data['phone']) != 10:
            result = False
    
    return result

# 重构后 - 低认知复杂度
class UserInputValidator:
    def __init__(self):
        self.validators = [
            self._validate_email,
            self._validate_age,
            self._validate_name,
            self._validate_phone
        ]
    
    def validate(self, data):
        if not data:
            return False
        
        return all(validator(data) for validator in self.validators)
    
    def _validate_email(self, data):
        if 'email' not in data:
            return False
        
        email = data['email']
        return '@' in email and '.' in email.split('@')[1]
    
    def _validate_age(self, data):
        if 'age' not in data:
            return False
        
        age = data['age']
        return isinstance(age, int) and 18 <= age <= 120
    
    def _validate_name(self, data):
        if 'name' not in data:
            return False
        
        name = data['name']
        return len(name) >= 2 and name.replace(' ', '').isalpha()
    
    def _validate_phone(self, data):
        if 'phone' not in data:
            return True
        
        phone = data['phone']
        return phone.isdigit() and len(phone) == 10
```

## 安全分析

### 安全漏洞扫描

#### Bandit配置
```yaml
# .bandit
[bandit]
exclude_dirs = tests,docs,build
skips = B101,B601

[bandit.assert_used]
skips = ['*_test.py', 'test_*.py']

[bandit.call_checks]
blacklist_calls = subprocess.Popen,subprocess.call,subprocess.run

[bandit.imports]
skips = hashlib,uuid
```

#### 安全漏洞示例
```python
# SQL注入漏洞
import sqlite3

# 不安全的代码
def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL注入风险
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

# 安全的代码
def get_user_safe(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # 使用参数化查询
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

# 硬编码密钥漏洞
import os

# 不安全的代码
def send_email(to, subject, body):
    api_key = "sk-1234567890abcdef"  # 硬编码密钥
    # 发送邮件逻辑
    pass

# 安全的代码
def send_email_safe(to, subject, body):
    api_key = os.getenv('EMAIL_API_KEY')
    if not api_key:
        raise ValueError("Email API key not configured")
    # 发送邮件逻辑
    pass

# 不安全的反序列化
import pickle

# 不安全的代码
def load_user_data(data):
    # 反序列化漏洞风险
    user = pickle.loads(data)
    return user

# 安全的代码
import json

def load_user_data_safe(data):
    # 使用JSON反序列化
    user = json.loads(data)
    return user
```

#### 安全检查规则
```python
# 自定义安全检查规则
import ast
import bandit
from bandit.core import issue

class HardcodedPasswordCheck(bandit.plugins.BasePlugin):
    def __init__(self):
        self.patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]
    
    def test(self, context, node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.lower()
                    if any(pattern in var_name for pattern in ['password', 'secret', 'key', 'token']):
                        if isinstance(node.value, ast.Constant):
                            value = node.value.value
                            if isinstance(value, str) and len(value) > 0:
                                return bandit.Issue(
                                    severity=bandit.HIGH,
                                    confidence=bandit.MEDIUM,
                                    text=f"Hardcoded {var_name} detected",
                                    lineno=node.lineno
                                )
        return None
```

### 依赖安全分析

#### Safety配置
```python
# requirements.txt
requests==2.28.1
django==4.1.0
numpy==1.21.0
```

```bash
# 运行安全扫描
safety check --json --output safety-report.json

# 检查特定文件
safety check --file requirements.txt

# 忽略特定漏洞
safety check --ignore 12345,67890
```

#### 依赖安全检查脚本
```python
#!/usr/bin/env python3
import subprocess
import json
import sys
from pathlib import Path

class DependencySecurityChecker:
    def __init__(self, requirements_file="requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.vulnerabilities = []
    
    def check_safety(self):
        """使用safety检查依赖漏洞"""
        try:
            result = subprocess.run(
                ["safety", "check", "--json", "--file", str(self.requirements_file)],
                capture_output=True,
                text=True,
                check=True
            )
            self.vulnerabilities = json.loads(result.stdout)
            return len(self.vulnerabilities) == 0
        except subprocess.CalledProcessError as e:
            print(f"Safety check failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Failed to parse safety output: {e}")
            return False
    
    def check_bandit(self):
        """使用bandit检查代码安全问题"""
        try:
            result = subprocess.run(
                ["bandit", "-r", ".", "-f", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            bandit_results = json.loads(result.stdout)
            return bandit_results
        except subprocess.CalledProcessError as e:
            print(f"Bandit check failed: {e}")
            return None
    
    def generate_report(self):
        """生成安全报告"""
        report = {
            "dependencies": {
                "file": str(self.requirements_file),
                "vulnerabilities": self.vulnerabilities,
                "total": len(self.vulnerabilities)
            },
            "code_security": self.check_bandit()
        }
        
        return report
    
    def print_summary(self):
        """打印安全检查摘要"""
        if not self.requirements_file.exists():
            print(f"Requirements file {self.requirements_file} not found")
            return
        
        print("=== Dependency Security Check ===")
        if self.check_safety():
            print("✅ No vulnerabilities found")
        else:
            print(f"❌ Found {len(self.vulnerabilities)} vulnerabilities")
            for vuln in self.vulnerabilities:
                print(f"  - {vuln['package']}=={vuln['version']}: {vuln['advisory']}")
        
        print("\n=== Code Security Check ===")
        bandit_results = self.check_bandit()
        if bandit_results:
            issues = bandit_results.get("results", [])
            if not issues:
                print("✅ No security issues found")
            else:
                print(f"❌ Found {len(issues)} security issues")
                for issue in issues[:5]:  # 只显示前5个
                    print(f"  - {issue['test_name']}: {issue['issue_text']}")

if __name__ == "__main__":
    checker = DependencySecurityChecker()
    checker.print_summary()
    
    # 生成详细报告
    report = checker.generate_report()
    with open("security-report.json", "w") as f:
        json.dump(report, f, indent=2)
```

## 性能分析

### CPU性能分析

#### cProfile使用
```python
import cProfile
import pstats
import io
from functools import wraps

def profile_function(func):
    """函数性能分析装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        # 输出分析结果
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # 显示前10个最耗时的函数
        
        print(f"Profile for {func.__name__}:")
        print(s.getvalue())
        
        return result
    return wrapper

# 使用示例
@profile_function
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 批量性能分析
def profile_multiple_functions():
    """分析多个函数的性能"""
    functions_to_profile = [
        (fibonacci, 30),
        (sum, list(range(1000000))),
        (sorted, list(range(10000, 0, -1)))
    ]
    
    for func, args in functions_to_profile:
        if isinstance(args, (list, tuple)):
            result = func(*args)
        else:
            result = func(args)
        print(f"{func.__name__} result: {result}")
```

#### 行级性能分析
```python
# line_profiler使用
# 安装: pip install line_profiler

# 在函数上添加 @profile 装饰器
@profile
def process_data(data):
    """处理数据的函数"""
    result = []
    for i, item in enumerate(data):
        # 处理每个项目
        processed = item * 2
        result.append(processed)
    
    # 排序结果
    result.sort()
    
    # 计算总和
    total = sum(result)
    
    return total

# 运行行级分析
# kernprof -l -v script.py
```

### 内存分析

#### memory_profiler使用
```python
import memory_profiler
import psutil
import os

@memory_profiler.profile
def memory_intensive_function():
    """内存密集型函数"""
    data = []
    for i in range(100000):
        data.append([0] * 1000)  # 创建大量数据
    return len(data)

# 内存使用监控
class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self):
        """获取当前内存使用情况"""
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': self.process.memory_percent()
        }
    
    def monitor_function(self, func):
        """监控函数的内存使用"""
        def wrapper(*args, **kwargs):
            start_memory = self.get_memory_usage()
            result = func(*args, **kwargs)
            end_memory = self.get_memory_usage()
            
            print(f"Memory usage for {func.__name__}:")
            print(f"  Start: {start_memory['rss']:.2f} MB")
            print(f"  End: {end_memory['rss']:.2f} MB")
            print(f"  Peak: {end_memory['rss'] - start_memory['rss']:.2f} MB")
            
            return result
        return wrapper

# 使用示例
monitor = MemoryMonitor()

@monitor.monitor_function
def create_large_list():
    return [i for i in range(1000000)]
```

### 算法复杂度分析

#### 时间复杂度分析
```python
import time
import random
import matplotlib.pyplot as plt
from functools import wraps

def time_complexity_analysis(func, sizes, trials=3):
    """分析函数的时间复杂度"""
    times = []
    
    for size in sizes:
        trial_times = []
        
        for _ in range(trials):
            # 生成测试数据
            data = random.sample(range(size * 10), size)
            
            # 测量执行时间
            start_time = time.perf_counter()
            func(data)
            end_time = time.perf_counter()
            
            trial_times.append(end_time - start_time)
        
        avg_time = sum(trial_times) / len(trial_times)
        times.append(avg_time)
    
    return sizes, times

# 测试不同算法的复杂度
def linear_search(arr, target):
    """线性搜索 - O(n)"""
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

def binary_search(arr, target):
    """二分搜索 - O(log n)"""
    left, right = 0, len(arr) - 1
    arr.sort()  # 确保数组已排序
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def bubble_sort(arr):
    """冒泡排序 - O(n²)"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# 复杂度分析示例
def analyze_algorithms():
    sizes = [100, 500, 1000, 2000, 5000]
    
    # 分析线性搜索
    linear_sizes, linear_times = time_complexity_analysis(
        lambda arr: linear_search(arr, arr[-1] if arr else -1),
        sizes
    )
    
    # 分析二分搜索
    binary_sizes, binary_times = time_complexity_analysis(
        lambda arr: binary_search(arr, arr[-1] if arr else -1),
        sizes
    )
    
    # 绘制结果
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.plot(linear_sizes, linear_times, 'b-o', label='Linear Search')
    plt.xlabel('Input Size')
    plt.ylabel('Time (seconds)')
    plt.title('Linear Search Complexity')
    plt.legend()
    
    plt.subplot(2, 2, 2)
    plt.plot(binary_sizes, binary_times, 'r-o', label='Binary Search')
    plt.xlabel('Input Size')
    plt.ylabel('Time (seconds)')
    plt.title('Binary Search Complexity')
    plt.legend()
    
    plt.tight_layout()
    plt.show()
```

## 依赖分析

### 依赖关系分析

#### 模块依赖分析
```python
import ast
import importlib.util
from pathlib import Path
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt

class DependencyAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.dependencies = defaultdict(set)
        self.import_graph = nx.DiGraph()
    
    def analyze_file(self, file_path):
        """分析单个Python文件的依赖"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return set()
        
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    
    def analyze_project(self):
        """分析整个项目的依赖关系"""
        python_files = list(self.project_root.rglob('*.py'))
        
        for file_path in python_files:
            if '__pycache__' in str(file_path):
                continue
            
            relative_path = file_path.relative_to(self.project_root)
            module_name = str(relative_path.with_suffix('')).replace('/', '.')
            
            imports = self.analyze_file(file_path)
            self.dependencies[module_name] = imports
            
            # 添加到依赖图
            self.import_graph.add_node(module_name)
            for imp in imports:
                self.import_graph.add_edge(module_name, imp)
        
        return self.dependencies
    
    def find_circular_dependencies(self):
        """查找循环依赖"""
        try:
            cycles = list(nx.simple_cycles(self.import_graph))
            return cycles
        except nx.NetworkXError:
            return []
    
    def get_dependency_depth(self, module):
        """获取模块的依赖深度"""
        if module not in self.import_graph:
            return 0
        
        return nx.shortest_path_length(self.import_graph, module, reverse=True)
    
    def get_most_dependent_modules(self, top_n=10):
        """获取被依赖最多的模块"""
        in_degrees = dict(self.import_graph.in_degree())
        return sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def visualize_dependencies(self, output_file='dependencies.png'):
        """可视化依赖关系"""
        plt.figure(figsize=(15, 10))
        
        # 使用spring布局
        pos = nx.spring_layout(self.import_graph, k=1, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(
            self.import_graph, pos,
            node_color='lightblue',
            node_size=1000,
            alpha=0.7
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.import_graph, pos,
            edge_color='gray',
            alpha=0.5,
            arrows=True,
            arrowsize=20
        )
        
        # 绘制标签
        nx.draw_networkx_labels(
            self.import_graph, pos,
            font_size=8,
            font_weight='bold'
        )
        
        plt.title('Project Dependency Graph')
        plt.axis('off')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self):
        """生成依赖分析报告"""
        cycles = self.find_circular_dependencies()
        most_dependent = self.get_most_dependent_modules()
        
        report = {
            'total_modules': len(self.import_graph.nodes()),
            'total_dependencies': len(self.import_graph.edges()),
            'circular_dependencies': cycles,
            'most_dependent_modules': most_dependent,
            'dependency_statistics': {
                'avg_in_degree': sum(dict(self.import_graph.in_degree()).values()) / len(self.import_graph.nodes()),
                'avg_out_degree': sum(dict(self.import_graph.out_degree()).values()) / len(self.import_graph.nodes()),
                'max_dependency_depth': max([self.get_dependency_depth(node) for node in self.import_graph.nodes()])
            }
        }
        
        return report

# 使用示例
if __name__ == "__main__":
    analyzer = DependencyAnalyzer('/path/to/your/project')
    dependencies = analyzer.analyze_project()
    
    print("=== Dependency Analysis Report ===")
    print(f"Total modules: {len(analyzer.import_graph.nodes())}")
    print(f"Total dependencies: {len(analyzer.import_graph.edges())}")
    
    cycles = analyzer.find_circular_dependencies()
    if cycles:
        print(f"Found {len(cycles)} circular dependencies:")
        for cycle in cycles:
            print(f"  -> {' -> '.join(cycle)}")
    else:
        print("No circular dependencies found")
    
    most_dependent = analyzer.get_most_dependent_modules(5)
    print("\nMost dependent modules:")
    for module, count in most_dependent:
        print(f"  {module}: {count} dependents")
    
    # 可视化依赖关系
    analyzer.visualize_dependencies()
    
    # 生成详细报告
    report = analyzer.generate_report()
    with open('dependency_report.json', 'w') as f:
        json.dump(report, f, indent=2)
```

### 代码结构分析

#### 代码度量分析
```python
import ast
from pathlib import Path
from collections import defaultdict
import pandas as pd

class CodeMetricsAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.metrics = defaultdict(dict)
    
    def analyze_file_metrics(self, file_path):
        """分析文件的代码度量"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        
        metrics = {
            'lines_of_code': len(content.splitlines()),
            'blank_lines': content.count('\n') - len(content.replace('\n', '')),
            'comment_lines': self._count_comments(content),
            'functions': 0,
            'classes': 0,
            'max_function_length': 0,
            'max_class_length': 0,
            'cyclomatic_complexity': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['functions'] += 1
                func_length = len(ast.get_source_segment(content, node).splitlines())
                metrics['max_function_length'] = max(metrics['max_function_length'], func_length)
                metrics['cyclomatic_complexity'] += self._calculate_complexity(node)
            
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
                class_length = len(ast.get_source_segment(content, node).splitlines())
                metrics['max_class_length'] = max(metrics['max_class_length'], class_length)
        
        return metrics
    
    def _count_comments(self, content):
        """计算注释行数"""
        lines = content.splitlines()
        comment_count = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                comment_count += 1
        
        return comment_count
    
    def _calculate_complexity(self, node):
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
    
    def analyze_project(self):
        """分析整个项目的代码度量"""
        python_files = list(self.project_root.rglob('*.py'))
        
        for file_path in python_files:
            if '__pycache__' in str(file_path):
                continue
            
            relative_path = file_path.relative_to(self.project_root)
            metrics = self.analyze_file_metrics(file_path)
            
            if metrics:
                self.metrics[str(relative_path)] = metrics
        
        return self.metrics
    
    def generate_summary_report(self):
        """生成汇总报告"""
        if not self.metrics:
            return None
        
        df = pd.DataFrame.from_dict(self.metrics, orient='index')
        
        summary = {
            'total_files': len(df),
            'total_lines': df['lines_of_code'].sum(),
            'total_functions': df['functions'].sum(),
            'total_classes': df['classes'].sum(),
            'avg_file_size': df['lines_of_code'].mean(),
            'avg_functions_per_file': df['functions'].mean(),
            'avg_classes_per_file': df['classes'].mean(),
            'max_cyclomatic_complexity': df['cyclomatic_complexity'].max(),
            'avg_cyclomatic_complexity': df['cyclomatic_complexity'].mean(),
            'files_with_high_complexity': len(df[df['cyclomatic_complexity'] > 10])
        }
        
        return summary
    
    def identify_code_smells(self):
        """识别代码异味"""
        code_smells = []
        
        for file_path, metrics in self.metrics.items():
            smells = []
            
            # 长文件
            if metrics['lines_of_code'] > 500:
                smells.append("Long file")
            
            # 长函数
            if metrics['max_function_length'] > 50:
                smells.append("Long function")
            
            # 大类
            if metrics['max_class_length'] > 200:
                smells.append("Large class")
            
            # 高复杂度
            if metrics['cyclomatic_complexity'] > 10:
                smells.append("High complexity")
            
            # 函数过多
            if metrics['functions'] > 20:
                smells.append("Too many functions")
            
            if smells:
                code_smells.append({
                    'file': file_path,
                    'smells': smells,
                    'metrics': metrics
                })
        
        return code_smells

# 使用示例
if __name__ == "__main__":
    analyzer = CodeMetricsAnalyzer('/path/to/your/project')
    metrics = analyzer.analyze_project()
    
    summary = analyzer.generate_summary_report()
    print("=== Code Metrics Summary ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    code_smells = analyzer.identify_code_smells()
    print(f"\n=== Code Smells Found: {len(code_smells)} ===")
    for smell in code_smells:
        print(f"File: {smell['file']}")
        for issue in smell['smells']:
            print(f"  - {issue}")
```

## 测试分析

### 测试覆盖率分析

#### 覆盖率配置
```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
```

#### 覆盖率分析脚本
```python
import coverage
import json
from pathlib import Path

class CoverageAnalyzer:
    def __init__(self, source_dir='src'):
        self.source_dir = Path(source_dir)
        self.cov = coverage.Coverage()
    
    def run_coverage(self, test_command='python -m pytest tests/'):
        """运行测试并收集覆盖率"""
        # 启动覆盖率收集
        self.cov.start()
        
        # 运行测试
        import subprocess
        result = subprocess.run(test_command, shell=True)
        
        # 停止覆盖率收集
        self.cov.stop()
        self.cov.save()
        
        return result.returncode == 0
    
    def generate_report(self):
        """生成覆盖率报告"""
        # 生成文本报告
        text_report = self.cov.report()
        
        # 生成HTML报告
        html_report = self.cov.html_report()
        
        # 生成JSON报告
        json_data = self.cov.get_data()
        coverage_data = {
            'files': {},
            'summary': {}
        }
        
        for filename in json_data.measured_files():
            file_data = json_data.line_counts(filename)
            if file_data:
                total_lines = sum(file_data.values())
                covered_lines = sum(1 for covered in file_data.values() if covered)
                coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0
                
                coverage_data['files'][filename] = {
                    'total_lines': total_lines,
                    'covered_lines': covered_lines,
                    'coverage_percent': coverage_percent,
                    'missing_lines': [line for line, covered in file_data.items() if not covered]
                }
        
        # 计算总体覆盖率
        total_files = len(coverage_data['files'])
        if total_files > 0:
            avg_coverage = sum(data['coverage_percent'] for data in coverage_data['files'].values()) / total_files
            coverage_data['summary'] = {
                'total_files': total_files,
                'average_coverage': avg_coverage
            }
        
        return coverage_data
    
    def identify_uncovered_code(self, threshold=80):
        """识别覆盖率低于阈值的文件"""
        coverage_data = self.generate_report()
        uncovered_files = []
        
        for filename, data in coverage_data['files'].items():
            if data['coverage_percent'] < threshold:
                uncovered_files.append({
                    'file': filename,
                    'coverage': data['coverage_percent'],
                    'missing_lines': data['missing_lines']
                })
        
        return uncovered_files
    
    def suggest_tests(self):
        """建议需要添加的测试"""
        uncovered_files = self.identify_uncovered_code()
        suggestions = []
        
        for file_info in uncovered_files:
            file_path = Path(file_info['file'])
            test_path = file_path.with_name(f'test_{file_path.stem}.py')
            
            suggestions.append({
                'source_file': str(file_path),
                'suggested_test_file': str(test_path),
                'coverage': file_info['coverage'],
                'missing_lines': file_info['missing_lines'][:10]  # 只显示前10行
            })
        
        return suggestions

# 使用示例
if __name__ == "__main__":
    analyzer = CoverageAnalyzer()
    
    # 运行覆盖率分析
    success = analyzer.run_coverage()
    
    if success:
        # 生成报告
        coverage_data = analyzer.generate_report()
        
        print("=== Coverage Report ===")
        print(f"Average coverage: {coverage_data['summary']['average_coverage']:.2f}%")
        
        # 识别未覆盖的代码
        uncovered = analyzer.identify_uncovered_code(80)
        print(f"\nFiles with coverage < 80%: {len(uncovered)}")
        
        # 生成测试建议
        suggestions = analyzer.suggest_tests()
        print(f"\nSuggested tests: {len(suggestions)}")
        
        for suggestion in suggestions[:5]:
            print(f"\nFile: {suggestion['source_file']}")
            print(f"Test file: {suggestion['suggested_test_file']}")
            print(f"Coverage: {suggestion['coverage']:.2f}%")
```

## 报告生成

### 综合分析报告

#### 报告生成器
```python
import json
import datetime
from pathlib import Path
from jinja2 import Template

class AnalysisReportGenerator:
    def __init__(self, project_name):
        self.project_name = project_name
        self.report_data = {}
    
    def add_quality_metrics(self, metrics):
        """添加代码质量指标"""
        self.report_data['quality'] = metrics
    
    def add_security_metrics(self, metrics):
        """添加安全指标"""
        self.report_data['security'] = metrics
    
    def add_performance_metrics(self, metrics):
        """添加性能指标"""
        self.report_data['performance'] = metrics
    
    def add_dependency_metrics(self, metrics):
        """添加依赖指标"""
        self.report_data['dependencies'] = metrics
    
    def add_test_metrics(self, metrics):
        """添加测试指标"""
        self.report_data['testing'] = metrics
    
    def generate_html_report(self, output_file='analysis_report.html'):
        """生成HTML报告"""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ project_name }} - Code Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #e9ecef; border-radius: 3px; }
        .good { background: #d4edda; color: #155724; }
        .warning { background: #fff3cd; color: #856404; }
        .danger { background: #f8d7da; color: #721c24; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f2f2f2; }
        .progress-bar { width: 100%; background: #e9ecef; border-radius: 3px; }
        .progress-fill { height: 20px; background: #28a745; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ project_name }} - Code Analysis Report</h1>
        <p>Generated on: {{ timestamp }}</p>
    </div>
    
    {% if quality %}
    <div class="section">
        <h2>Code Quality</h2>
        <div class="metric">Lines of Code: {{ quality.total_lines }}</div>
        <div class="metric">Functions: {{ quality.total_functions }}</div>
        <div class="metric">Classes: {{ quality.total_classes }}</div>
        <div class="metric">Average Complexity: {{ quality.avg_complexity|round(2) }}</div>
        
        <h3>Quality Issues</h3>
        <table>
            <tr><th>Type</th><th>Count</th><th>Severity</th></tr>
            {% for issue in quality.issues %}
            <tr>
                <td>{{ issue.type }}</td>
                <td>{{ issue.count }}</td>
                <td class="{{ issue.severity }}">{{ issue.severity }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    {% if security %}
    <div class="section">
        <h2>Security Analysis</h2>
        <div class="metric">Total Vulnerabilities: {{ security.total_vulnerabilities }}</div>
        <div class="metric">Critical: {{ security.critical }}</div>
        <div class="metric">High: {{ security.high }}</div>
        <div class="metric">Medium: {{ security.medium }}</div>
        <div class="metric">Low: {{ security.low }}</div>
        
        {% if security.vulnerabilities %}
        <h3>Security Issues</h3>
        <table>
            <tr><th>Package</th><th>Version</th><th>Severity</th><th>Description</th></tr>
            {% for vuln in security.vulnerabilities %}
            <tr>
                <td>{{ vuln.package }}</td>
                <td>{{ vuln.version }}</td>
                <td class="{{ vuln.severity }}">{{ vuln.severity }}</td>
                <td>{{ vuln.description }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </div>
    {% endif %}
    
    {% if performance %}
    <div class="section">
        <h2>Performance Analysis</h2>
        <div class="metric">Average Execution Time: {{ performance.avg_execution_time }}ms</div>
        <div class="metric">Peak Memory Usage: {{ performance.peak_memory }}MB</div>
        <div class="metric">Slow Functions: {{ performance.slow_functions|length }}</div>
        
        <h3>Performance Bottlenecks</h3>
        <table>
            <tr><th>Function</th><th>Execution Time</th><th>Memory Usage</th></tr>
            {% for func in performance.bottlenecks %}
            <tr>
                <td>{{ func.name }}</td>
                <td>{{ func.time }}ms</td>
                <td>{{ func.memory }}MB</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    {% if testing %}
    <div class="section">
        <h2>Testing Analysis</h2>
        <div class="metric">Coverage: {{ testing.coverage }}%</div>
        <div class="metric">Test Files: {{ testing.test_files }}</div>
        <div class="metric">Test Cases: {{ testing.test_cases }}</div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ testing.coverage }}%"></div>
        </div>
        
        <h3>Uncovered Files</h3>
        <table>
            <tr><th>File</th><th>Coverage</th><th>Missing Lines</th></tr>
            {% for file in testing.uncovered_files %}
            <tr>
                <td>{{ file.name }}</td>
                <td>{{ file.coverage }}%</td>
                <td>{{ file.missing_lines|length }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    <div class="section">
        <h2>Summary</h2>
        <div class="metric">Overall Score: {{ overall_score }}/100</div>
        <div class="metric {{ grade.class }}">{{ grade.message }}</div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        
        # 计算总体评分
        overall_score = self._calculate_overall_score()
        grade = self._get_grade(overall_score)
        
        html_content = template.render(
            project_name=self.project_name,
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **self.report_data,
            overall_score=overall_score,
            grade=grade
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _calculate_overall_score(self):
        """计算总体评分"""
        scores = []
        
        if 'quality' in self.report_data:
            scores.append(self.report_data['quality'].get('score', 0))
        
        if 'security' in self.report_data:
            scores.append(self.report_data['security'].get('score', 0))
        
        if 'performance' in self.report_data:
            scores.append(self.report_data['performance'].get('score', 0))
        
        if 'testing' in self.report_data:
            scores.append(self.report_data['testing'].get('score', 0))
        
        return sum(scores) / len(scores) if scores else 0
    
    def _get_grade(self, score):
        """获取等级"""
        if score >= 90:
            return {'class': 'good', 'message': 'Excellent'}
        elif score >= 80:
            return {'class': 'good', 'message': 'Good'}
        elif score >= 70:
            return {'class': 'warning', 'message': 'Fair'}
        else:
            return {'class': 'danger', 'message': 'Needs Improvement'}
    
    def generate_json_report(self, output_file='analysis_report.json'):
        """生成JSON报告"""
        report_data = {
            'project_name': self.project_name,
            'timestamp': datetime.datetime.now().isoformat(),
            'overall_score': self._calculate_overall_score(),
            **self.report_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return output_file

# 使用示例
if __name__ == "__main__":
    generator = AnalysisReportGenerator("MyProject")
    
    # 添加各种指标
    generator.add_quality_metrics({
        'total_lines': 10000,
        'total_functions': 150,
        'total_classes': 25,
        'avg_complexity': 3.5,
        'score': 85,
        'issues': [
            {'type': 'Long Function', 'count': 5, 'severity': 'warning'},
            {'type': 'High Complexity', 'count': 2, 'severity': 'danger'}
        ]
    })
    
    generator.add_security_metrics({
        'total_vulnerabilities': 3,
        'critical': 0,
        'high': 1,
        'medium': 2,
        'low': 0,
        'score': 75,
        'vulnerabilities': [
            {
                'package': 'requests',
                'version': '2.25.0',
                'severity': 'high',
                'description': 'CVE-2021-33503'
            }
        ]
    })
    
    generator.add_test_metrics({
        'coverage': 78.5,
        'test_files': 25,
        'test_cases': 150,
        'score': 78,
        'uncovered_files': [
            {'name': 'utils.py', 'coverage': 45, 'missing_lines': [10, 15, 20]}
        ]
    })
    
    # 生成报告
    html_file = generator.generate_html_report()
    json_file = generator.generate_json_report()
    
    print(f"HTML report generated: {html_file}")
    print(f"JSON report generated: {json_file}")
```

## 参考资源

### 官方文档
- [Python Documentation](https://docs.python.org/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

### 静态分析工具
- [Bandit Security Scanner](https://bandit.readthedocs.io/)
- [Safety Dependency Checker](https://pyup.io/safety/)
- [Semgrep Static Analysis](https://semgrep.dev/)
- [SonarQube Python](https://docs.sonarqube.org/latest/analysis/languages/python/)

### 性能分析
- [cProfile Documentation](https://docs.python.org/3/library/profile.html)
- [memory_profiler Documentation](https://pypi.org/project/memory-profiler/)
- [line_profiler Documentation](https://github.com/rkern/line_profiler)
- [py-spy Documentation](https://github.com/benfred/py-spy)

### 测试工具
- [pytest Documentation](https://docs.pytest.org/)
- [hypothesis Property Testing](https://hypothesis.works/)
- [tox Testing Tool](https://tox.readthedocs.io/)
- [coverage.py Testing Coverage](https://coverage.readthedocs.io/)

### 代码质量
- [Code Climate](https://codeclimate.com/)
- [Codacy](https://www.codacy.com/)
- [CodeFactor](https://www.codefactor.io/)
- [Better Code Hub](https://bettercodehub.com/)

### 社区资源
- [Python Software Foundation](https://www.python.org/psf/)
- [Real Python](https://realpython.com/)
- [Python Weekly](https://www.pythonweekly.com/)
- [Reddit r/Python](https://www.reddit.com/r/Python/)
