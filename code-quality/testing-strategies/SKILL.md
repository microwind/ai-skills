---
name: 测试策略与覆盖
description: "当设计测试策略时，分析测试需求，制定测试计划，实现测试覆盖。验证测试质量，设计测试框架，和最佳实践。"
license: MIT
---

# 测试策略与覆盖技能

## 概述
测试策略是保证软件质量的重要手段。不当的测试策略会导致质量缺陷、维护困难、发布风险。需要系统化的测试方法和全面的覆盖策略。

**核心原则**: 好的测试策略应该全面覆盖、自动化执行、持续集成。坏的测试策略会导致遗漏缺陷、维护成本高、反馈延迟。

## 何时使用

**始终:**
- 开发新功能时
- 重构现有代码时
- 修复缺陷时
- 发布前验证时
- 代码审查时
- 性能优化时

**触发短语:**
- "测试策略"
- "测试覆盖率"
- "自动化测试"
- "测试框架"
- "质量保证"
- "测试计划"

## 测试策略功能

### 测试类型设计
- 单元测试策略
- 集成测试策略
- 系统测试策略
- 验收测试策略
- 性能测试策略

### 测试覆盖分析
- 代码覆盖率分析
- 分支覆盖率统计
- 功能覆盖率评估
- 风险覆盖率计算
- 回归覆盖率管理

### 测试自动化
- 自动化测试框架
- 持续集成集成
- 测试数据管理
- 测试环境配置
- 测试报告生成

### 测试质量管理
- 测试用例管理
- 缺陷跟踪管理
- 测试进度监控
- 测试风险评估
- 测试效果评估

## 常见测试问题

### 测试覆盖率不足
```
问题:
测试覆盖率低，无法有效保证代码质量

错误示例:
- 只测试正常流程
- 忽略边界条件
- 缺少异常处理测试
- 跳过复杂逻辑测试

解决方案:
1. 制定覆盖率目标
2. 实施分支覆盖
3. 添加边界测试
4. 包含异常场景
```

### 测试维护困难
```
问题:
测试代码难以维护，影响开发效率

错误示例:
- 测试代码重复
- 硬编码测试数据
- 缺少测试抽象
- 测试依赖复杂

解决方案:
1. 提取测试工具类
2. 使用测试数据工厂
3. 实现测试基类
4. 简化测试依赖
```

### 测试执行缓慢
```
问题:
测试执行时间过长，影响开发效率

错误示例:
- 重复数据库操作
- 不必要的网络请求
- 大量数据准备
- 缺少测试并行

解决方案:
1. 使用内存数据库
2. Mock外部依赖
3. 优化测试数据
4. 实现并行测试
```

### 测试环境不稳定
```
问题:
测试环境不稳定，导致测试结果不可靠

错误示例:
- 环境配置不一致
- 依赖服务不稳定
- 测试数据污染
- 并发测试冲突

解决方案:
1. 容器化测试环境
2. 使用服务Mock
3. 实现数据隔离
4. 避免并发冲突
```

## 代码实现示例

### 测试框架设计器
```python
import unittest
import pytest
import coverage
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import json
import sqlite3
import tempfile
import os

class TestType(Enum):
    """测试类型"""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    ACCEPTANCE = "acceptance"
    PERFORMANCE = "performance"

class CoverageType(Enum):
    """覆盖类型"""
    LINE = "line"
    BRANCH = "branch"
    FUNCTION = "function"
    STATEMENT = "statement"

@dataclass
class TestCase:
    """测试用例"""
    name: str
    test_type: TestType
    description: str
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    timeout: float = 30.0
    tags: List[str] = None

@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    status: str
    duration: float
    error_message: Optional[str] = None
    coverage_data: Optional[Dict[str, Any]] = None

@dataclass
class CoverageReport:
    """覆盖报告"""
    total_lines: int
    covered_lines: int
    line_coverage: float
    total_branches: int
    covered_branches: int
    branch_coverage: float
    total_functions: int
    covered_functions: int
    function_coverage: float
    uncovered_files: List[str]

class TestDataProvider:
    """测试数据提供者"""
    
    @staticmethod
    def create_user_data():
        """创建用户测试数据"""
        return [
            {"id": 1, "name": "Alice", "email": "alice@test.com"},
            {"id": 2, "name": "Bob", "email": "bob@test.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@test.com"}
        ]
    
    @staticmethod
    def create_product_data():
        """创建产品测试数据"""
        return [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
            {"id": 2, "name": "Book", "price": 29.99, "category": "Books"},
            {"id": 3, "name": "Phone", "price": 699.99, "category": "Electronics"}
        ]
    
    @staticmethod
    def create_edge_cases():
        """创建边界测试数据"""
        return {
            "empty_string": "",
            "null_value": None,
            "zero_value": 0,
            "negative_value": -1,
            "max_value": 2**31 - 1,
            "min_value": -2**31
        }

class MockService:
    """Mock服务"""
    
    def __init__(self):
        self.responses = {}
        self.calls = []
    
    def set_response(self, method: str, response: Any):
        """设置响应"""
        self.responses[method] = response
    
    def call(self, method: str, *args, **kwargs):
        """模拟调用"""
        self.calls.append({"method": method, "args": args, "kwargs": kwargs})
        return self.responses.get(method, None)
    
    def get_call_count(self, method: str) -> int:
        """获取调用次数"""
        return len([call for call in self.calls if call["method"] == method])
    
    def reset(self):
        """重置调用记录"""
        self.calls.clear()

class TestFramework:
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestResult] = []
        self.coverage_collector = coverage.Coverage()
        self.mock_services: Dict[str, MockService] = {}
        self.test_data_provider = TestDataProvider()
        
        # 测试配置
        self.timeout_default = 30.0
        self.parallel_execution = True
        self.max_workers = 4
        
        # 覆盖率配置
        self.coverage_threshold = 80.0
        self.coverage_types = [CoverageType.LINE, CoverageType.BRANCH]
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def create_test_case(self, name: str, test_type: TestType, 
                        description: str, test_func: Callable,
                        setup: Optional[Callable] = None,
                        teardown: Optional[Callable] = None) -> TestCase:
        """创建测试用例"""
        test_case = TestCase(
            name=name,
            test_type=test_type,
            description=description,
            setup=setup,
            teardown=teardown
        )
        
        # 动态添加测试方法
        setattr(self, f"test_{name}", test_func)
        self.add_test_case(test_case)
        
        return test_case
    
    def run_tests(self, test_types: Optional[List[TestType]] = None) -> List[TestResult]:
        """运行测试"""
        self.test_results.clear()
        
        # 启动覆盖率收集
        self.coverage_collector.start()
        
        # 过滤测试用例
        filtered_tests = self._filter_tests(test_types)
        
        # 执行测试
        if self.parallel_execution:
            self._run_tests_parallel(filtered_tests)
        else:
            self._run_tests_sequential(filtered_tests)
        
        # 停止覆盖率收集
        self.coverage_collector.stop()
        
        # 生成覆盖率报告
        self._generate_coverage_report()
        
        return self.test_results
    
    def _filter_tests(self, test_types: Optional[List[TestType]]) -> List[TestCase]:
        """过滤测试用例"""
        if test_types is None:
            return self.test_cases
        
        return [test for test in self.test_cases if test.test_type in test_types]
    
    def _run_tests_sequential(self, test_cases: List[TestCase]):
        """顺序执行测试"""
        for test_case in test_cases:
            result = self._execute_single_test(test_case)
            self.test_results.append(result)
    
    def _run_tests_parallel(self, test_cases: List[TestCase]):
        """并行执行测试"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_test = {
                executor.submit(self._execute_single_test, test_case): test_case
                for test_case in test_cases
            }
            
            for future in concurrent.futures.as_completed(future_to_test):
                result = future.result()
                self.test_results.append(result)
    
    def _execute_single_test(self, test_case: TestCase) -> TestResult:
        """执行单个测试"""
        start_time = time.time()
        
        try:
            # 执行setup
            if test_case.setup:
                test_case.setup()
            
            # 执行测试
            test_func = getattr(self, f"test_{test_case.name}")
            
            # 使用超时控制
            if test_case.timeout > 0:
                result = self._execute_with_timeout(test_func, test_case.timeout)
            else:
                result = test_func()
            
            # 计算执行时间
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_case.name,
                status="PASSED",
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_case.name,
                status="FAILED",
                duration=duration,
                error_message=str(e)
            )
        
        finally:
            # 执行teardown
            if test_case.teardown:
                try:
                    test_case.teardown()
                except Exception as e:
                    print(f"Teardown failed for {test_case.name}: {e}")
    
    def _execute_with_timeout(self, func: Callable, timeout: float):
        """带超时执行函数"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Test execution timed out after {timeout} seconds")
        
        # 设置超时信号
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        try:
            result = func()
            signal.alarm(0)  # 取消超时
            return result
        except TimeoutError:
            raise
        finally:
            signal.alarm(0)  # 确保取消超时
    
    def _generate_coverage_report(self):
        """生成覆盖率报告"""
        # 获取覆盖率数据
        coverage_data = self.coverage_collector.get_data()
        
        # 生成报告
        report = coverage.CoverageReport()
        
        # 更新测试结果
        for result in self.test_results:
            result.coverage_data = {
                "lines_covered": len(coverage_data.lines()),
                "total_lines": coverage_data.line_count(),
                "coverage_percent": coverage_data.coverage()
            }
    
    def get_coverage_summary(self) -> CoverageReport:
        """获取覆盖率摘要"""
        total_lines = 0
        covered_lines = 0
        total_branches = 0
        covered_branches = 0
        total_functions = 0
        covered_functions = 0
        
        for result in self.test_results:
            if result.coverage_data:
                total_lines += result.coverage_data.get("total_lines", 0)
                covered_lines += result.coverage_data.get("lines_covered", 0)
        
        line_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        
        return CoverageReport(
            total_lines=total_lines,
            covered_lines=covered_lines,
            line_coverage=line_coverage,
            total_branches=total_branches,
            covered_branches=covered_branches,
            branch_coverage=0.0,
            total_functions=total_functions,
            covered_functions=covered_functions,
            function_coverage=0.0,
            uncovered_files=[]
        )
    
    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        passed_tests = [r for r in self.test_results if r.status == "PASSED"]
        failed_tests = [r for r in self.test_results if r.status == "FAILED"]
        
        coverage_summary = self.get_coverage_summary()
        
        return {
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len(passed_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(passed_tests) / len(self.test_results) * 100 if self.test_results else 0,
                "total_duration": sum(r.duration for r in self.test_results)
            },
            "coverage": {
                "line_coverage": coverage_summary.line_coverage,
                "branch_coverage": coverage_summary.branch_coverage,
                "function_coverage": coverage_summary.function_coverage
            },
            "failed_tests": [
                {
                    "name": result.test_name,
                    "error": result.error_message,
                    "duration": result.duration
                }
                for result in failed_tests
            ],
            "slow_tests": sorted(
                [
                    {
                        "name": result.test_name,
                        "duration": result.duration
                    }
                    for result in self.test_results
                ],
                key=lambda x: x["duration"],
                reverse=True
            )[:10]
        }
    
    def create_mock_service(self, name: str) -> MockService:
        """创建Mock服务"""
        mock_service = MockService()
        self.mock_services[name] = mock_service
        return mock_service
    
    def setup_test_database(self) -> sqlite3.Connection:
        """设置测试数据库"""
        # 创建临时数据库
        db_file = tempfile.mktemp(suffix='.db')
        conn = sqlite3.connect(db_file)
        
        # 创建测试表
        conn.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            );
            
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT NOT NULL
            );
        """)
        
        # 插入测试数据
        users = self.test_data_provider.create_user_data()
        products = self.test_data_provider.create_product_data()
        
        conn.executemany(
            "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
            [(u["id"], u["name"], u["email"]) for u in users]
        )
        
        conn.executemany(
            "INSERT INTO products (id, name, price, category) VALUES (?, ?, ?, ?)",
            [(p["id"], p["name"], p["price"], p["category"]) for p in products]
        )
        
        conn.commit()
        return conn

# 使用示例
def main():
    print("=== 测试框架设计器 ===")
    
    # 创建测试框架
    framework = TestFramework()
    
    # 示例1: 创建单元测试
    def test_user_creation():
        """测试用户创建"""
        user_data = {"name": "Test User", "email": "test@example.com"}
        
        # 模拟用户创建逻辑
        if not user_data.get("name"):
            raise ValueError("Name is required")
        
        if not user_data.get("email"):
            raise ValueError("Email is required")
        
        assert "@" in user_data["email"], "Invalid email format"
        return True
    
    def test_product_validation():
        """测试产品验证"""
        product_data = {"name": "Test Product", "price": 99.99, "category": "Test"}
        
        if product_data["price"] <= 0:
            raise ValueError("Price must be positive")
        
        assert len(product_data["name"]) > 0, "Name cannot be empty"
        return True
    
    # 添加测试用例
    framework.create_test_case(
        "user_creation",
        TestType.UNIT,
        "测试用户创建功能",
        test_user_creation
    )
    
    framework.create_test_case(
        "product_validation",
        TestType.UNIT,
        "测试产品验证功能",
        test_product_validation
    )
    
    # 示例2: 创建集成测试
    def setup_database_test():
        """设置数据库测试"""
        framework.test_db = framework.setup_test_database()
    
    def teardown_database_test():
        """清理数据库测试"""
        if hasattr(framework, 'test_db'):
            framework.test_db.close()
    
    def test_database_operations():
        """测试数据库操作"""
        cursor = framework.test_db.cursor()
        
        # 查询用户
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count == 3, f"Expected 3 users, got {user_count}"
        
        # 查询产品
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        assert product_count == 3, f"Expected 3 products, got {product_count}"
        
        return True
    
    framework.create_test_case(
        "database_operations",
        TestType.INTEGRATION,
        "测试数据库操作",
        test_database_operations,
        setup=setup_database_test,
        teardown=teardown_database_test
    )
    
    # 示例3: 创建Mock测试
    def setup_mock_test():
        """设置Mock测试"""
        framework.api_mock = framework.create_mock_service("api")
        framework.api_mock.set_response("get_user", {"id": 1, "name": "Mock User"})
    
    def test_api_integration():
        """测试API集成"""
        # 模拟API调用
        user = framework.api_mock.call("get_user", user_id=1)
        
        assert user is not None, "User should not be None"
        assert user["id"] == 1, "User ID should be 1"
        assert user["name"] == "Mock User", "User name should match"
        
        # 验证调用次数
        call_count = framework.api_mock.get_call_count("get_user")
        assert call_count == 1, f"Expected 1 call, got {call_count}"
        
        return True
    
    framework.create_test_case(
        "api_integration",
        TestType.INTEGRATION,
        "测试API集成",
        test_api_integration,
        setup=setup_mock_test
    )
    
    # 运行测试
    print("运行测试...")
    results = framework.run_tests()
    
    # 生成报告
    report = framework.generate_test_report()
    
    print(f"\n=== 测试报告 ===")
    print(f"总测试数: {report['summary']['total_tests']}")
    print(f"通过测试: {report['summary']['passed_tests']}")
    print(f"失败测试: {report['summary']['failed_tests']}")
    print(f"成功率: {report['summary']['success_rate']:.1f}%")
    print(f"总执行时间: {report['summary']['total_duration']:.2f}s")
    
    print(f"\n=== 覆盖率报告 ===")
    print(f"行覆盖率: {report['coverage']['line_coverage']:.1f}%")
    print(f"分支覆盖率: {report['coverage']['branch_coverage']:.1f}%")
    print(f"函数覆盖率: {report['coverage']['function_coverage']:.1f}%")
    
    if report['failed_tests']:
        print(f"\n=== 失败测试 ===")
        for failed_test in report['failed_tests']:
            print(f"- {failed_test['name']}: {failed_test['error']}")
    
    print(f"\n=== 最慢测试 ===")
    for slow_test in report['slow_tests'][:3]:
        print(f"- {slow_test['name']}: {slow_test['duration']:.3f}s")

if __name__ == '__main__':
    main()
```

### 测试覆盖率分析器
```python
import ast
import inspect
from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import os

class CoverageLevel(Enum):
    """覆盖级别"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    COMPLETE = "complete"

@dataclass
class CoverageMetric:
    """覆盖指标"""
    file_path: str
    total_lines: int
    covered_lines: int
    total_branches: int
    covered_branches: int
    total_functions: int
    covered_functions: int

@dataclass
class UncoveredCode:
    """未覆盖代码"""
    file_path: str
    line_number: int
    code_snippet: str
    reason: str

class CoverageAnalyzer:
    def __init__(self):
        self.coverage_data: Dict[str, CoverageMetric] = {}
        self.uncovered_code: List[UncoveredCode] = []
        self.coverage_threshold = 80.0
    
    def analyze_file(self, file_path: str, executed_lines: Set[int]) -> CoverageMetric:
        """分析文件覆盖率"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 分析代码结构
            total_lines = len(content.split('\n'))
            executable_lines = self._get_executable_lines(tree)
            covered_lines = len(executed_lines.intersection(executable_lines))
            
            # 分析分支
            total_branches = self._count_branches(tree)
            covered_branches = self._estimate_covered_branches(executed_lines, tree)
            
            # 分析函数
            total_functions = self._count_functions(tree)
            covered_functions = self._estimate_covered_functions(executed_lines, tree)
            
            metric = CoverageMetric(
                file_path=file_path,
                total_lines=total_lines,
                covered_lines=covered_lines,
                total_branches=total_branches,
                covered_branches=covered_branches,
                total_functions=total_functions,
                covered_functions=covered_functions
            )
            
            self.coverage_data[file_path] = metric
            
            # 找出未覆盖的代码
            self._find_uncovered_code(file_path, content, executable_lines, executed_lines)
            
            return metric
            
        except Exception as e:
            print(f"分析文件失败 {file_path}: {e}")
            return CoverageMetric(file_path, 0, 0, 0, 0, 0, 0)
    
    def _get_executable_lines(self, tree: ast.AST) -> Set[int]:
        """获取可执行行号"""
        executable_lines = set()
        
        for node in ast.walk(tree):
            if hasattr(node, 'lineno'):
                # 排除某些非执行语句
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef)):
                    continue
                executable_lines.add(node.lineno)
        
        return executable_lines
    
    def _count_branches(self, tree: ast.AST) -> int:
        """计算分支数量"""
        branch_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                branch_count += 2  # if和else分支
            elif isinstance(node, ast.While):
                branch_count += 2  # 循环和跳出分支
            elif isinstance(node, ast.For):
                branch_count += 2  # 循环和跳出分支
            elif isinstance(node, ast.Try):
                branch_count += len(node.handlers) + (1 if node.orelse else 0) + (1 if node.finalbody else 0)
        
        return branch_count
    
    def _estimate_covered_branches(self, executed_lines: Set[int], tree: ast.AST) -> int:
        """估算覆盖的分支数"""
        covered_branches = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # 检查if分支是否覆盖
                if node.lineno in executed_lines:
                    covered_branches += 1
                
                # 检查else分支是否覆盖
                if node.orelse and hasattr(node.orelse[0], 'lineno'):
                    if node.orelse[0].lineno in executed_lines:
                        covered_branches += 1
                elif not node.orelse:
                    # 没有else分支，只算一个分支
                    pass
                else:
                    # 有else分支但未覆盖
                    pass
            
            elif isinstance(node, (ast.While, ast.For)):
                if node.lineno in executed_lines:
                    covered_branches += 1
        
        return covered_branches
    
    def _count_functions(self, tree: ast.AST) -> int:
        """计算函数数量"""
        function_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
        
        return function_count
    
    def _estimate_covered_functions(self, executed_lines: Set[int], tree: ast.AST) -> int:
        """估算覆盖的函数数"""
        covered_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数体是否被执行
                if node.body and hasattr(node.body[0], 'lineno'):
                    if node.body[0].lineno in executed_lines:
                        covered_functions += 1
        
        return covered_functions
    
    def _find_uncovered_code(self, file_path: str, content: str, 
                           executable_lines: Set[int], executed_lines: Set[int]):
        """找出未覆盖的代码"""
        lines = content.split('\n')
        uncovered_lines = executable_lines - executed_lines
        
        for line_num in uncovered_lines:
            if line_num <= len(lines):
                line_content = lines[line_num - 1].strip()
                
                if line_content and not line_content.startswith('#'):
                    uncovered = UncoveredCode(
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=line_content,
                        reason=self._determine_uncovered_reason(line_content)
                    )
                    self.uncovered_code.append(uncovered)
    
    def _determine_uncovered_reason(self, code_line: str) -> str:
        """确定未覆盖的原因"""
        code_line = code_line.strip()
        
        if 'raise' in code_line:
            return "异常路径未测试"
        elif 'return' in code_line:
            return "返回路径未测试"
        elif 'elif' in code_line or 'else' in code_line:
            return "条件分支未测试"
        elif 'except' in code_line:
            return "异常处理未测试"
        elif 'break' in code_line or 'continue' in code_line:
            return "循环控制未测试"
        else:
            return "代码路径未测试"
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """获取覆盖率摘要"""
        if not self.coverage_data:
            return {"status": "no_data"}
        
        total_lines = sum(metric.total_lines for metric in self.coverage_data.values())
        covered_lines = sum(metric.covered_lines for metric in self.coverage_data.values())
        total_branches = sum(metric.total_branches for metric in self.coverage_data.values())
        covered_branches = sum(metric.covered_branches for metric in self.coverage_data.values())
        total_functions = sum(metric.total_functions for metric in self.coverage_data.values())
        covered_functions = sum(metric.covered_functions for metric in self.coverage_data.values())
        
        line_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else 0
        function_coverage = (covered_functions / total_functions * 100) if total_functions > 0 else 0
        
        return {
            "total_files": len(self.coverage_data),
            "line_coverage": line_coverage,
            "branch_coverage": branch_coverage,
            "function_coverage": function_coverage,
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "total_branches": total_branches,
            "covered_branches": covered_branches,
            "total_functions": total_functions,
            "covered_functions": covered_functions,
            "uncovered_code_count": len(self.uncovered_code)
        }
    
    def get_coverage_recommendations(self) -> List[str]:
        """获取覆盖率改进建议"""
        recommendations = []
        summary = self.get_coverage_summary()
        
        if summary["line_coverage"] < self.coverage_threshold:
            recommendations.append(
                f"行覆盖率 {summary['line_coverage']:.1f}% 低于目标 {self.coverage_threshold}%，"
                "建议增加测试用例覆盖未执行的代码行"
            )
        
        if summary["branch_coverage"] < self.coverage_threshold:
            recommendations.append(
                f"分支覆盖率 {summary['branch_coverage']:.1f}% 低于目标，"
                "建议测试所有条件分支和异常处理路径"
            )
        
        if summary["function_coverage"] < self.coverage_threshold:
            recommendations.append(
                f"函数覆盖率 {summary['function_coverage']:.1f}% 低于目标，"
                "建议为每个函数编写测试用例"
            )
        
        # 分析未覆盖代码
        if self.uncovered_code:
            error_handling_uncovered = len([u for u in self.uncovered_code if "异常" in u.reason])
            if error_handling_uncovered > 0:
                recommendations.append(
                    f"发现 {error_handling_uncovered} 个未测试的异常处理路径，"
                    "建议添加异常测试用例"
                )
        
        return recommendations
    
    def generate_coverage_report(self) -> str:
        """生成覆盖率报告"""
        summary = self.get_coverage_summary()
        recommendations = self.get_coverage_recommendations()
        
        report_lines = [
            "# 测试覆盖率报告",
            "",
            "## 总体摘要",
            f"- 文件数量: {summary['total_files']}",
            f"- 行覆盖率: {summary['line_coverage']:.1f}%",
            f"- 分支覆盖率: {summary['branch_coverage']:.1f}%",
            f"- 函数覆盖率: {summary['function_coverage']:.1f}%",
            f"- 未覆盖代码片段: {summary['uncovered_code_count']}",
            "",
            "## 详细覆盖率"
        ]
        
        # 按文件显示覆盖率
        for file_path, metric in self.coverage_data.items():
            line_cov = (metric.covered_lines / metric.total_lines * 100) if metric.total_lines > 0 else 0
            branch_cov = (metric.covered_branches / metric.total_branches * 100) if metric.total_branches > 0 else 0
            func_cov = (metric.covered_functions / metric.total_functions * 100) if metric.total_functions > 0 else 0
            
            report_lines.extend([
                f"",
                f"### {file_path}",
                f"- 行覆盖: {line_cov:.1f}% ({metric.covered_lines}/{metric.total_lines})",
                f"- 分支覆盖: {branch_cov:.1f}% ({metric.covered_branches}/{metric.total_branches})",
                f"- 函数覆盖: {func_cov:.1f}% ({metric.covered_functions}/{metric.total_functions})"
            ])
        
        # 未覆盖代码
        if self.uncovered_code:
            report_lines.extend([
                "",
                "## 未覆盖代码",
                ""
            ])
            
            for uncovered in self.uncovered_code[:20]:  # 只显示前20个
                report_lines.append(
                    f"- {uncovered.file_path}:{uncovered.line_number} - {uncovered.reason}"
                )
                report_lines.append(f"  ```python")
                report_lines.append(f"  {uncovered.code_snippet}")
                report_lines.append(f"  ```")
                report_lines.append("")
        
        # 改进建议
        if recommendations:
            report_lines.extend([
                "",
                "## 改进建议",
                ""
            ])
            
            for i, recommendation in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {recommendation}")
        
        return "\n".join(report_lines)

# 使用示例
def main():
    print("=== 测试覆盖率分析器 ===")
    
    # 创建分析器
    analyzer = CoverageAnalyzer()
    
    # 模拟执行行号（实际应用中从测试框架获取）
    executed_lines = {5, 6, 7, 8, 12, 13, 14, 15, 19, 20, 21}
    
    # 分析当前文件
    current_file = __file__
    if os.path.exists(current_file):
        metric = analyzer.analyze_file(current_file, executed_lines)
        
        print(f"文件: {metric.file_path}")
        print(f"总行数: {metric.total_lines}")
        print(f"覆盖行数: {metric.covered_lines}")
        print(f"总分支数: {metric.total_branches}")
        print(f"覆盖分支数: {metric.covered_branches}")
        print(f"总函数数: {metric.total_functions}")
        print(f"覆盖函数数: {metric.covered_functions}")
    
    # 获取覆盖率摘要
    summary = analyzer.get_coverage_summary()
    print(f"\n=== 覆盖率摘要 ===")
    print(f"行覆盖率: {summary['line_coverage']:.1f}%")
    print(f"分支覆盖率: {summary['branch_coverage']:.1f}%")
    print(f"函数覆盖率: {summary['function_coverage']:.1f}%")
    
    # 获取改进建议
    recommendations = analyzer.get_coverage_recommendations()
    if recommendations:
        print(f"\n=== 改进建议 ===")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"{i}. {recommendation}")
    
    # 生成完整报告
    report = analyzer.generate_coverage_report()
    print(f"\n=== 完整报告 ===")
    print(report[:1000] + "..." if len(report) > 1000 else report)

if __name__ == '__main__':
    main()
```

## 测试策略最佳实践

### 测试金字塔
1. **单元测试**: 占比70%，快速反馈，隔离测试
2. **集成测试**: 占比20%，测试组件交互
3. **端到端测试**: 占比10%，验证用户场景

### 覆盖率策略
1. **行覆盖率**: 基础要求，确保代码被执行
2. **分支覆盖率**: 重要指标，测试所有逻辑分支
3. **函数覆盖率**: 必要检查，确保函数被调用
4. **路径覆盖率**: 高级目标，覆盖所有执行路径

### 自动化策略
1. **持续集成**: 每次提交自动运行测试
2. **测试并行**: 提高测试执行效率
3. **环境隔离**: 确保测试环境一致性
4. **数据管理**: 自动化测试数据准备

### 质量保证
1. **测试审查**: 定期审查测试用例质量
2. **覆盖率监控**: 持续监控覆盖率变化
3. **缺陷分析**: 分析测试漏掉的缺陷
4. **效果评估**: 评估测试投入产出比

## 相关技能

- **test-generation** - 测试生成
- **code-review** - 代码审查
- **code-optimization** - 代码优化
- **documentation-generator** - 文档生成
