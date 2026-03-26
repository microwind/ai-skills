# 测试策略参考文档

## 测试策略概述

### 什么是测试策略
测试策略是指导测试活动的综合性计划，它定义了测试的目标、范围、方法、资源和时间安排。一个好的测试策略能够确保测试活动的高效性、有效性和系统性，从而提高软件质量并降低风险。

### 测试策略价值
- **质量保证**: 系统性地验证软件功能和性能
- **风险控制**: 识别和降低软件质量风险
- **效率提升**: 优化测试资源分配和执行效率
- **成本控制**: 减少后期缺陷修复成本
- **团队协作**: 统一测试标准和流程

### 测试策略层次
- **项目级策略**: 整个项目的测试总体规划
- **模块级策略**: 特定模块的测试详细计划
- **功能级策略**: 具体功能的测试实施方案
- **用例级策略**: 单个测试用例的执行策略

## 测试策略核心实现

### 测试计划引擎
```python
# testing_strategies.py
import os
import time
import json
import logging
import threading
import subprocess
import statistics
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
import unittest
import pytest
import concurrent.futures
import requests
import sqlite3
import pandas as pd

class TestType(Enum):
    """测试类型枚举"""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCEPTANCE = "acceptance"
    REGRESSION = "regression"

class TestFramework(Enum):
    """测试框架枚举"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    JUNIT = "junit"
    SELENIUM = "selenium"
    CYPRESS = "cypress"

class ExecutionMode(Enum):
    """执行模式枚举"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"
    SCHEDULED = "scheduled"

@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    test_type: TestType
    priority: str  # high, medium, low
    status: str  # pending, running, passed, failed, skipped
    execution_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    """测试套件"""
    id: str
    name: str
    description: str
    test_cases: List[TestCase]
    setup_commands: List[str] = field(default_factory=list)
    teardown_commands: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestResult:
    """测试结果"""
    test_case_id: str
    status: str  # passed, failed, skipped, error
    execution_time: float
    start_time: float
    end_time: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    coverage_data: Optional[Dict[str, Any]] = None
    performance_data: Optional[Dict[str, Any]] = None

@dataclass
class TestReport:
    """测试报告"""
    project_name: str
    test_suite_id: str
    execution_id: str
    start_time: float
    end_time: float
    total_duration: float
    test_results: List[TestResult]
    summary: Dict[str, Any]
    coverage_summary: Dict[str, Any]
    performance_summary: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class TestPlan:
    """测试计划"""
    
    def __init__(self, project_name: str):
        self.logger = logging.getLogger(__name__)
        self.project_name = project_name
        self.test_suites = []
        self.test_cases = []
        self.execution_history = []
        self.coverage_targets = {}
        self.performance_targets = {}
    
    def add_test_suite(self, test_suite: TestSuite):
        """添加测试套件"""
        self.test_suites.append(test_suite)
        self.test_cases.extend(test_suite.test_cases)
    
    def calculate_coverage_target(self, test_type: TestType) -> Dict[str, float]:
        """计算覆盖率目标"""
        targets = {
            TestType.UNIT: {
                'line_coverage': 80.0,
                'branch_coverage': 70.0,
                'function_coverage': 90.0
            },
            TestType.INTEGRATION: {
                'line_coverage': 60.0,
                'branch_coverage': 50.0,
                'function_coverage': 70.0
            },
            TestType.SYSTEM: {
                'line_coverage': 40.0,
                'branch_coverage': 30.0,
                'function_coverage': 50.0
            }
        }
        return targets.get(test_type, {'line_coverage': 50.0, 'branch_coverage': 40.0, 'function_coverage': 60.0})
    
    def calculate_performance_target(self, test_type: TestType) -> Dict[str, Any]:
        """计算性能目标"""
        targets = {
            TestType.UNIT: {
                'max_execution_time': 1.0,  # 秒
                'max_memory_usage': 10.0,   # MB
                'max_cpu_usage': 50.0       # %
            },
            TestType.INTEGRATION: {
                'max_execution_time': 5.0,
                'max_memory_usage': 50.0,
                'max_cpu_usage': 70.0
            },
            TestType.PERFORMANCE: {
                'max_response_time': 1000.0,  # ms
                'min_throughput': 100.0,      # req/s
                'max_error_rate': 1.0         # %
            }
        }
        return targets.get(test_type, {'max_execution_time': 10.0, 'max_memory_usage': 100.0, 'max_cpu_usage': 80.0})

class TestExecutor:
    """测试执行器"""
    
    def __init__(self, test_plan: TestPlan):
        self.logger = logging.getLogger(__name__)
        self.test_plan = test_plan
        self.execution_results = []
        self.current_execution_id = None
    
    def execute_test_suite(self, test_suite: TestSuite, 
                          execution_mode: ExecutionMode = ExecutionMode.AUTOMATIC) -> TestReport:
        """执行测试套件"""
        self.current_execution_id = f"exec_{int(time.time())}"
        start_time = time.time()
        
        self.logger.info(f"开始执行测试套件: {test_suite.name}")
        
        # 执行前置命令
        self._execute_setup_commands(test_suite.setup_commands)
        
        # 执行测试用例
        test_results = []
        
        if execution_mode == ExecutionMode.AUTOMATIC:
            test_results = self._execute_automatic(test_suite)
        elif execution_mode == ExecutionMode.MANUAL:
            test_results = self._execute_manual(test_suite)
        elif execution_mode == ExecutionMode.HYBRID:
            test_results = self._execute_hybrid(test_suite)
        
        # 执行后置命令
        self._execute_teardown_commands(test_suite.teardown_commands)
        
        end_time = time.time()
        
        # 生成测试报告
        report = self._generate_test_report(test_suite, test_results, start_time, end_time)
        
        self.logger.info(f"测试套件执行完成: {test_suite.name}")
        
        return report
    
    def _execute_automatic(self, test_suite: TestSuite) -> List[TestResult]:
        """自动执行测试"""
        results = []
        
        for test_case in test_suite.test_cases:
            result = self._execute_test_case(test_case)
            results.append(result)
        
        return results
    
    def _execute_manual(self, test_suite: TestSuite) -> List[TestResult]:
        """手动执行测试"""
        results = []
        
        for test_case in test_suite.test_cases:
            # 手动测试需要人工干预
            self.logger.info(f"请手动执行测试用例: {test_case.name}")
            input(f"执行完成后按回车键继续...")
            
            # 模拟手动测试结果
            result = TestResult(
                test_case_id=test_case.id,
                status="passed",  # 假设手动测试通过
                execution_time=0.0,
                start_time=time.time(),
                end_time=time.time()
            )
            results.append(result)
        
        return results
    
    def _execute_hybrid(self, test_suite: TestSuite) -> List[TestResult]:
        """混合执行测试"""
        results = []
        
        for test_case in test_suite.test_cases:
            if test_case.test_type in [TestType.UNIT, TestType.INTEGRATION]:
                # 自动执行单元测试和集成测试
                result = self._execute_test_case(test_case)
            else:
                # 手动执行系统测试和验收测试
                self.logger.info(f"请手动执行测试用例: {test_case.name}")
                input(f"执行完成后按回车键继续...")
                
                result = TestResult(
                    test_case_id=test_case.id,
                    status="passed",
                    execution_time=0.0,
                    start_time=time.time(),
                    end_time=time.time()
                )
            
            results.append(result)
        
        return results
    
    def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """执行单个测试用例"""
        start_time = time.time()
        test_case.status = "running"
        
        try:
            # 根据测试类型执行相应的测试逻辑
            if test_case.test_type == TestType.UNIT:
                execution_time = self._execute_unit_test(test_case)
            elif test_case.test_type == TestType.INTEGRATION:
                execution_time = self._execute_integration_test(test_case)
            elif test_case.test_type == TestType.PERFORMANCE:
                execution_time = self._execute_performance_test(test_case)
            elif test_case.test_type == TestType.SECURITY:
                execution_time = self._execute_security_test(test_case)
            else:
                execution_time = self._execute_generic_test(test_case)
            
            end_time = time.time()
            
            result = TestResult(
                test_case_id=test_case.id,
                status="passed",
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time
            )
            
            test_case.status = "passed"
            test_case.execution_time = execution_time
            
        except Exception as e:
            end_time = time.time()
            
            result = TestResult(
                test_case_id=test_case.id,
                status="failed",
                execution_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                stack_trace=str(e.__traceback__)
            )
            
            test_case.status = "failed"
            test_case.error_message = str(e)
        
        return result
    
    def _execute_unit_test(self, test_case: TestCase) -> float:
        """执行单元测试"""
        # 模拟单元测试执行
        time.sleep(0.1)  # 模拟测试执行时间
        
        # 模拟测试逻辑
        if "fail" in test_case.name.lower():
            raise Exception("模拟单元测试失败")
        
        return 0.1
    
    def _execute_integration_test(self, test_case: TestCase) -> float:
        """执行集成测试"""
        # 模拟集成测试执行
        time.sleep(0.5)
        
        # 模拟测试逻辑
        if "integration" in test_case.name.lower() and "fail" in test_case.name.lower():
            raise Exception("模拟集成测试失败")
        
        return 0.5
    
    def _execute_performance_test(self, test_case: TestCase) -> float:
        """执行性能测试"""
        # 模拟性能测试执行
        time.sleep(2.0)
        
        # 模拟性能测试逻辑
        if "performance" in test_case.name.lower() and "slow" in test_case.name.lower():
            time.sleep(5.0)  # 模拟慢性能测试
        
        return 2.0
    
    def _execute_security_test(self, test_case: TestCase) -> float:
        """执行安全测试"""
        # 模拟安全测试执行
        time.sleep(1.0)
        
        # 模拟安全测试逻辑
        if "security" in test_case.name.lower() and "vulnerable" in test_case.name.lower():
            raise Exception("模拟安全测试发现漏洞")
        
        return 1.0
    
    def _execute_generic_test(self, test_case: TestCase) -> float:
        """执行通用测试"""
        # 模拟通用测试执行
        time.sleep(0.3)
        
        # 模拟测试逻辑
        if "fail" in test_case.name.lower():
            raise Exception("模拟测试失败")
        
        return 0.3
    
    def _execute_setup_commands(self, commands: List[str]):
        """执行前置命令"""
        for command in commands:
            try:
                subprocess.run(command, shell=True, check=True, capture_output=True)
                self.logger.info(f"执行前置命令: {command}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"前置命令执行失败: {command}, 错误: {e}")
    
    def _execute_teardown_commands(self, commands: List[str]):
        """执行后置命令"""
        for command in commands:
            try:
                subprocess.run(command, shell=True, check=True, capture_output=True)
                self.logger.info(f"执行后置命令: {command}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"后置命令执行失败: {command}, 错误: {e}")
    
    def _generate_test_report(self, test_suite: TestSuite, 
                            test_results: List[TestResult],
                            start_time: float, 
                            end_time: float) -> TestReport:
        """生成测试报告"""
        # 计算汇总信息
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.status == "passed"])
        failed_tests = len([r for r in test_results if r.status == "failed"])
        skipped_tests = len([r for r in test_results if r.status == "skipped"])
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'fail_rate': (failed_tests / total_tests * 100) if total_tests > 0 else 0,
            'skip_rate': (skipped_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        # 计算覆盖率汇总
        coverage_summary = self._calculate_coverage_summary(test_results)
        
        # 计算性能汇总
        performance_summary = self._calculate_performance_summary(test_results)
        
        return TestReport(
            project_name=self.test_plan.project_name,
            test_suite_id=test_suite.id,
            execution_id=self.current_execution_id,
            start_time=start_time,
            end_time=end_time,
            total_duration=end_time - start_time,
            test_results=test_results,
            summary=summary,
            coverage_summary=coverage_summary,
            performance_summary=performance_summary,
            metadata={
                'test_suite_name': test_suite.name,
                'execution_mode': 'automatic',
                'environment': 'test'
            }
        )
    
    def _calculate_coverage_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """计算覆盖率汇总"""
        # 模拟覆盖率计算
        total_lines = 1000
        covered_lines = 850
        total_branches = 200
        covered_branches = 150
        total_functions = 100
        covered_functions = 90
        
        return {
            'line_coverage': (covered_lines / total_lines * 100),
            'branch_coverage': (covered_branches / total_branches * 100),
            'function_coverage': (covered_functions / total_functions * 100),
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'total_branches': total_branches,
            'covered_branches': covered_branches,
            'total_functions': total_functions,
            'covered_functions': covered_functions
        }
    
    def _calculate_performance_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """计算性能汇总"""
        execution_times = [r.execution_time for r in test_results]
        
        if execution_times:
            avg_execution_time = statistics.mean(execution_times)
            max_execution_time = max(execution_times)
            min_execution_time = min(execution_times)
            total_execution_time = sum(execution_times)
        else:
            avg_execution_time = max_execution_time = min_execution_time = total_execution_time = 0
        
        return {
            'avg_execution_time': avg_execution_time,
            'max_execution_time': max_execution_time,
            'min_execution_time': min_execution_time,
            'total_execution_time': total_execution_time,
            'throughput': len(test_results) / total_execution_time if total_execution_time > 0 else 0
        }

class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_data = {}
        self.data_generators = {}
    
    def generate_test_data(self, data_type: str, count: int, **kwargs) -> List[Dict[str, Any]]:
        """生成测试数据"""
        if data_type == "user":
            return self._generate_user_data(count, **kwargs)
        elif data_type == "product":
            return self._generate_product_data(count, **kwargs)
        elif data_type == "order":
            return self._generate_order_data(count, **kwargs)
        else:
            return self._generate_generic_data(count, **kwargs)
    
    def _generate_user_data(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """生成用户数据"""
        import random
        import string
        
        users = []
        for i in range(count):
            user = {
                'id': i + 1,
                'username': f"user_{i+1}",
                'email': f"user{i+1}@example.com",
                'password': ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
                'age': random.randint(18, 65),
                'active': random.choice([True, False])
            }
            users.append(user)
        
        return users
    
    def _generate_product_data(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """生成产品数据"""
        import random
        
        products = []
        categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
        
        for i in range(count):
            product = {
                'id': i + 1,
                'name': f"Product {i+1}",
                'category': random.choice(categories),
                'price': round(random.uniform(10.0, 1000.0), 2),
                'stock': random.randint(0, 100),
                'active': random.choice([True, False])
            }
            products.append(product)
        
        return products
    
    def _generate_order_data(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """生成订单数据"""
        import random
        from datetime import datetime, timedelta
        
        orders = []
        for i in range(count):
            order_date = datetime.now() - timedelta(days=random.randint(0, 365))
            order = {
                'id': i + 1,
                'user_id': random.randint(1, 100),
                'product_id': random.randint(1, 50),
                'quantity': random.randint(1, 10),
                'total_amount': round(random.uniform(50.0, 500.0), 2),
                'status': random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled']),
                'order_date': order_date.isoformat()
            }
            orders.append(order)
        
        return orders
    
    def _generate_generic_data(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """生成通用数据"""
        import random
        
        data = []
        for i in range(count):
            item = {
                'id': i + 1,
                'name': f"Item {i+1}",
                'value': random.randint(1, 100),
                'description': f"Description for item {i+1}"
            }
            data.append(item)
        
        return data
    
    def validate_test_data(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> Dict[str, Any]:
        """验证测试数据"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        if not data:
            validation_result['valid'] = False
            validation_result['errors'].append("数据为空")
            return validation_result
        
        # 验证数据结构
        required_fields = schema.get('required_fields', [])
        field_types = schema.get('field_types', {})
        
        for i, item in enumerate(data):
            # 检查必填字段
            for field in required_fields:
                if field not in item:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"第{i+1}项缺少必填字段: {field}")
            
            # 检查字段类型
            for field, expected_type in field_types.items():
                if field in item and not isinstance(item[field], expected_type):
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"第{i+1}项字段 {field} 类型错误，期望 {expected_type.__name__}")
        
        # 计算统计信息
        validation_result['statistics'] = {
            'total_count': len(data),
            'field_counts': {field: sum(1 for item in data if field in item) for field in schema.get('required_fields', [])}
        }
        
        return validation_result

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_html_report(self, report: TestReport, output_path: str):
        """生成HTML报告"""
        html_content = self._create_html_report(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已生成: {output_path}")
    
    def generate_json_report(self, report: TestReport, output_path: str):
        """生成JSON报告"""
        report_data = asdict(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"JSON报告已生成: {output_path}")
    
    def generate_csv_report(self, report: TestReport, output_path: str):
        """生成CSV报告"""
        # 创建测试结果DataFrame
        test_results_data = []
        for result in report.test_results:
            test_results_data.append({
                'test_case_id': result.test_case_id,
                'status': result.status,
                'execution_time': result.execution_time,
                'error_message': result.error_message or ''
            })
        
        df = pd.DataFrame(test_results_data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        self.logger.info(f"CSV报告已生成: {output_path}")
    
    def _create_html_report(self, report: TestReport) -> str:
        """创建HTML报告内容"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {project_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-item {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .summary-item h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .summary-item .value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .test-results {{
            margin-top: 30px;
        }}
        .test-results table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .test-results th, .test-results td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .test-results th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .status-passed {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-failed {{
            color: #dc3545;
            font-weight: bold;
        }}
        .status-skipped {{
            color: #ffc107;
            font-weight: bold;
        }}
        .coverage {{
            margin-top: 30px;
        }}
        .coverage-item {{
            margin-bottom: 15px;
        }}
        .coverage-label {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .progress-bar {{
            background-color: #e9ecef;
            border-radius: 4px;
            height: 20px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #007bff;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>测试报告</h1>
            <h2>{project_name}</h2>
            <p>执行时间: {execution_time}</p>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <h3>总测试数</h3>
                <div class="value">{total_tests}</div>
            </div>
            <div class="summary-item">
                <h3>通过</h3>
                <div class="value status-passed">{passed_tests}</div>
            </div>
            <div class="summary-item">
                <h3>失败</h3>
                <div class="value status-failed">{failed_tests}</div>
            </div>
            <div class="summary-item">
                <h3>跳过</h3>
                <div class="value status-skipped">{skipped_tests}</div>
            </div>
            <div class="summary-item">
                <h3>通过率</h3>
                <div class="value">{pass_rate:.1f}%</div>
            </div>
            <div class="summary-item">
                <h3>执行时间</h3>
                <div class="value">{total_duration:.2f}s</div>
            </div>
        </div>
        
        <div class="coverage">
            <h3>代码覆盖率</h3>
            <div class="coverage-item">
                <div class="coverage-label">行覆盖率: {line_coverage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {line_coverage:.1f}%"></div>
                </div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">分支覆盖率: {branch_coverage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {branch_coverage:.1f}%"></div>
                </div>
            </div>
            <div class="coverage-item">
                <div class="coverage-label">函数覆盖率: {function_coverage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {function_coverage:.1f}%"></div>
                </div>
            </div>
        </div>
        
        <div class="test-results">
            <h3>测试结果详情</h3>
            <table>
                <thead>
                    <tr>
                        <th>测试用例ID</th>
                        <th>状态</th>
                        <th>执行时间</th>
                        <th>错误信息</th>
                    </tr>
                </thead>
                <tbody>
                    {test_results_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
        """
        
        # 生成测试结果行
        test_results_rows = ""
        for result in report.test_results:
            status_class = f"status-{result.status}"
            error_message = result.error_message or ""
            
            test_results_rows += f"""
                    <tr>
                        <td>{result.test_case_id}</td>
                        <td class="{status_class}">{result.status}</td>
                        <td>{result.execution_time:.3f}s</td>
                        <td>{error_message}</td>
                    </tr>
            """
        
        # 填充模板
        return html_template.format(
            project_name=report.project_name,
            execution_time=datetime.fromtimestamp(report.start_time).strftime('%Y-%m-%d %H:%M:%S'),
            total_tests=report.summary['total_tests'],
            passed_tests=report.summary['passed_tests'],
            failed_tests=report.summary['failed_tests'],
            skipped_tests=report.summary['skipped_tests'],
            pass_rate=report.summary['pass_rate'],
            total_duration=report.total_duration,
            line_coverage=report.coverage_summary['line_coverage'],
            branch_coverage=report.coverage_summary['branch_coverage'],
            function_coverage=report.coverage_summary['function_coverage'],
            test_results_rows=test_results_rows
        )

# 使用示例
if __name__ == "__main__":
    # 创建测试计划
    test_plan = TestPlan("MyProject")
    
    # 创建测试用例
    test_cases = [
        TestCase(
            id="test_001",
            name="用户登录测试",
            description="测试用户登录功能",
            test_type=TestType.UNIT,
            priority="high",
            status="pending"
        ),
        TestCase(
            id="test_002",
            name="数据库连接测试",
            description="测试数据库连接功能",
            test_type=TestType.INTEGRATION,
            priority="high",
            status="pending"
        ),
        TestCase(
            id="test_003",
            name="性能测试",
            description="测试系统性能",
            test_type=TestType.PERFORMANCE,
            priority="medium",
            status="pending"
        )
    ]
    
    # 创建测试套件
    test_suite = TestSuite(
        id="suite_001",
        name="核心功能测试",
        description="测试系统核心功能",
        test_cases=test_cases,
        setup_commands=["echo '开始测试'"],
        teardown_commands=["echo '测试结束'"]
    )
    
    # 添加测试套件到计划
    test_plan.add_test_suite(test_suite)
    
    # 创建测试执行器
    executor = TestExecutor(test_plan)
    
    # 执行测试套件
    report = executor.execute_test_suite(test_suite, ExecutionMode.AUTOMATIC)
    
    # 生成报告
    report_generator = TestReportGenerator()
    report_generator.generate_html_report(report, "test_report.html")
    report_generator.generate_json_report(report, "test_report.json")
    report_generator.generate_csv_report(report, "test_report.csv")
    
    # 创建测试数据管理器
    data_manager = TestDataManager()
    
    # 生成测试数据
    user_data = data_manager.generate_test_data("user", 10)
    product_data = data_manager.generate_test_data("product", 5)
    
    # 验证测试数据
    schema = {
        'required_fields': ['id', 'username', 'email'],
        'field_types': {
            'id': int,
            'username': str,
            'email': str
        }
    }
    
    validation_result = data_manager.validate_test_data(user_data, schema)
    
    print(f"测试执行完成:")
    print(f"总测试数: {report.summary['total_tests']}")
    print(f"通过数: {report.summary['passed_tests']}")
    print(f"失败数: {report.summary['failed_tests']}")
    print(f"通过率: {report.summary['pass_rate']:.1f}%")
    print(f"代码覆盖率: {report.coverage_summary['line_coverage']:.1f}%")
    print(f"测试数据验证: {'通过' if validation_result['valid'] else '失败'}")
```

## 参考资源

### 测试框架
- [pytest](https://docs.pytest.org/) - Python测试框架
- [unittest](https://docs.python.org/3/library/unittest.html) - Python标准测试框架
- [Jest](https://jestjs.io/) - JavaScript测试框架
- [JUnit](https://junit.org/junit5/) - Java测试框架
- [TestNG](https://testng.org/) - Java测试框架

### 自动化测试工具
- [Selenium](https://www.selenium.dev/) - Web应用自动化测试
- [Cypress](https://www.cypress.io/) - 现代Web应用测试
- [Playwright](https://playwright.dev/) - 跨浏览器自动化测试
- [Appium](https://appium.io/) - 移动应用自动化测试
- [Robot Framework](https://robotframework.org/) - 通用自动化测试框架

### 性能测试工具
- [JMeter](https://jmeter.apache.org/) - 性能测试工具
- [LoadRunner](https://www.microfocus.com/en-us/products/loadrunner-load-testing) - 企业级性能测试
- [Gatling](https://gatling.io/) - 高性能负载测试
- [k6](https://k6.io/) - 现代负载测试工具
- [Locust](https://locust.io/) - Python负载测试框架

### 安全测试工具
- [OWASP ZAP](https://www.zaproxy.org/) - Web应用安全扫描
- [Burp Suite](https://portswigger.net/burp) - Web安全测试平台
- [Nessus](https://www.tenable.com/products/nessus) - 漏洞扫描器
- [Metasploit](https://www.metasploit.com/) - 渗透测试框架
- [SonarQube](https://www.sonarqube.org/) - 代码质量和安全分析

### 测试策略指南
- [ISTQB](https://www.istqb.org/) - 国际软件测试资质认证
- [Testing Best Practices](https://martinfowler.com/articles/testing-strategies.html) - 测试策略最佳实践
- [Google Testing Blog](https://testing.googleblog.com/) - Google测试博客
- [Microsoft Testing](https://docs.microsoft.com/en-us/devops/testing/) - 微软测试指南
