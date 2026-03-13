---
name: 测试生成
description: "当生成测试时，分析代码结构，设计测试用例，编写单元测试、集成测试，提高测试覆盖率。验证测试质量，设计测试策略，和最佳实践。"
license: MIT
---

# 测试生成技能

## 概述
测试生成是保证软件质量的重要环节。好的测试应该全面、可靠、易维护。不当的测试会导致遗漏bug、维护困难和开发效率低下。

**核心原则**: 好的测试应该快速执行、独立运行、易于理解、可重复执行。坏的测试会导致测试套件脆弱、运行缓慢、难以维护。

## 何时使用

**始终:**
- 开发新功能时
- 修复bug后验证时
- 重构代码时
- 集成新组件时
- 发布版本前测试时
- 性能优化验证时

**触发短语:**
- "测试生成"
- "单元测试编写"
- "测试覆盖率"
- "测试用例设计"
- "如何测试这段代码"
- "验证代码正确性"

## 测试生成功能

### 单元测试
- 函数/方法独立测试
- 模拟外部依赖
- 分支覆盖测试
- 错误条件测试

### 集成测试
- 组件协作测试
- 数据库/API集成测试
- 端到端流程测试
- 错误场景测试

### 边界测试
- 空值/未定义输入
- 空集合处理
- 边界值测试
- 无效输入测试
- 并发访问测试
- 资源耗尽测试

### 性能测试
- 负载测试
- 压力测试
- 内存泄漏测试
- 响应时间测试

## 常见测试问题

### 测试覆盖率不足
```
问题:
测试覆盖率低，遗漏重要场景

错误示例:
- 只测试正常流程
- 忽略边界条件
- 缺少错误处理测试
- 跳过复杂逻辑

解决方案:
1. 提高覆盖率目标
2. 分析未覆盖代码
3. 添加边界测试
4. 测试异常情况
```

### 测试脆弱性问题
```
问题:
测试容易失败，维护成本高

错误示例:
- 依赖外部系统
- 硬编码测试数据
- 时间依赖测试
- 顺序依赖测试

解决方案:
1. 使用模拟对象
2. 生成测试数据
3. 避免时间依赖
4. 确保测试独立
```

### 测试性能问题
```
问题:
测试执行缓慢，影响开发效率

错误示例:
- 测试数据过大
- 网络调用过多
- 数据库操作频繁
- 同步等待时间

解决方案:
1. 使用内存数据库
2. 模拟外部调用
3. 并行执行测试
4. 优化测试数据
```

### 测试可读性问题
```
问题:
测试代码难以理解和维护

错误示例:
- 测试命名不清晰
- 测试逻辑复杂
- 缺少测试文档
- 断言信息不明确

解决方案:
1. 改进测试命名
2. 简化测试逻辑
3. 添加测试注释
4. 使用清晰断言
```

## 代码实现示例

### 测试生成器
```python
import ast
import inspect
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class TestType(Enum):
    """测试类型"""
    UNIT = "unit"
    INTEGRATION = "integration"
    EDGE = "edge"
    PERFORMANCE = "performance"

@dataclass
class TestCase:
    """测试用例"""
    name: str
    description: str
    test_type: TestType
    setup: str
    input_data: Dict[str, Any]
    expected_output: Any
    assertions: List[str]

@dataclass
class TestSuite:
    """测试套件"""
    class_name: str
    test_cases: List[TestCase]
    imports: List[str]
    fixtures: List[str]

class TestGenerator:
    def __init__(self):
        self.test_suites: List[TestSuite] = []
        
    def generate_tests_from_code(self, code: str, file_path: str) -> List[TestSuite]:
        """从代码生成测试"""
        try:
            tree = ast.parse(code)
            
            # 分析类和函数
            classes = self._extract_classes(tree)
            functions = self._extract_functions(tree)
            
            # 为每个类生成测试套件
            for class_info in classes:
                test_suite = self._generate_class_tests(class_info, file_path)
                if test_suite:
                    self.test_suites.append(test_suite)
            
            # 为每个函数生成测试套件
            for func_info in functions:
                test_suite = self._generate_function_tests(func_info, file_path)
                if test_suite:
                    self.test_suites.append(test_suite)
            
        except SyntaxError as e:
            print(f"语法错误: {e}")
        
        return self.test_suites
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """提取类信息"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'args': [arg.arg for arg in item.args.args],
                            'returns': self._get_return_type(item),
                            'docstring': ast.get_docstring(item)
                        })
                
                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'docstring': ast.get_docstring(node)
                })
        
        return classes
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """提取函数信息"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 跳过类中的方法
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                    functions.append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'returns': self._get_return_type(node),
                        'docstring': ast.get_docstring(node)
                    })
        
        return functions
    
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """获取返回类型"""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        return "unknown"
    
    def _generate_class_tests(self, class_info: Dict[str, Any], file_path: str) -> Optional[TestSuite]:
        """为类生成测试"""
        test_cases = []
        
        # 为每个方法生成测试
        for method in class_info['methods']:
            if method['name'].startswith('_'):
                continue  # 跳过私有方法
            
            # 生成正常测试
            normal_test = self._generate_normal_test(method)
            if normal_test:
                test_cases.append(normal_test)
            
            # 生成边界测试
            edge_test = self._generate_edge_test(method)
            if edge_test:
                test_cases.append(edge_test)
            
            # 生成错误测试
            error_test = self._generate_error_test(method)
            if error_test:
                test_cases.append(error_test)
        
        if not test_cases:
            return None
        
        return TestSuite(
            class_name=f"Test{class_info['name']}",
            test_cases=test_cases,
            imports=["import pytest", f"from {file_path.replace('.py', '')} import {class_info['name']}"],
            fixtures=[f"@pytest.fixture\ndef {class_info['name'].lower()}():\n    return {class_info['name']}()"]
        )
    
    def _generate_function_tests(self, func_info: Dict[str, Any], file_path: str) -> Optional[TestSuite]:
        """为函数生成测试"""
        test_cases = []
        
        # 生成正常测试
        normal_test = self._generate_normal_test(func_info)
        if normal_test:
            test_cases.append(normal_test)
        
        # 生成边界测试
        edge_test = self._generate_edge_test(func_info)
        if edge_test:
            test_cases.append(edge_test)
        
        # 生成错误测试
        error_test = self._generate_error_test(func_info)
        if error_test:
            test_cases.append(error_test)
        
        if not test_cases:
            return None
        
        return TestSuite(
            class_name=f"Test{func_info['name'].capitalize()}",
            test_cases=test_cases,
            imports=["import pytest", f"from {file_path.replace('.py', '')} import {func_info['name']}"],
            fixtures=[]
        )
    
    def _generate_normal_test(self, method: Dict[str, Any]) -> Optional[TestCase]:
        """生成正常测试"""
        test_name = f"test_{method['name']}_normal"
        
        # 根据参数生成测试数据
        input_data = {}
        for arg in method['args']:
            if arg == 'self':
                continue
            input_data[arg] = self._generate_test_value(arg, "normal")
        
        # 生成期望输出
        expected_output = self._generate_expected_output(method, input_data)
        
        # 生成断言
        assertions = [f"assert result == {expected_output}"]
        
        return TestCase(
            name=test_name,
            description=f"测试 {method['name']} 正常情况",
            test_type=TestType.UNIT,
            setup="",
            input_data=input_data,
            expected_output=expected_output,
            assertions=assertions
        )
    
    def _generate_edge_test(self, method: Dict[str, Any]) -> Optional[TestCase]:
        """生成边界测试"""
        test_name = f"test_{method['name']}_edge"
        
        # 生成边界值测试数据
        input_data = {}
        for arg in method['args']:
            if arg == 'self':
                continue
            input_data[arg] = self._generate_test_value(arg, "edge")
        
        # 生成期望输出
        expected_output = self._generate_expected_output(method, input_data)
        
        # 生成断言
        assertions = [f"assert result == {expected_output}"]
        
        return TestCase(
            name=test_name,
            description=f"测试 {method['name']} 边界情况",
            test_type=TestType.EDGE,
            setup="",
            input_data=input_data,
            expected_output=expected_output,
            assertions=assertions
        )
    
    def _generate_error_test(self, method: Dict[str, Any]) -> Optional[TestCase]:
        """生成错误测试"""
        test_name = f"test_{method['name']}_error"
        
        # 生成错误测试数据
        input_data = {}
        for arg in method['args']:
            if arg == 'self':
                continue
            input_data[arg] = self._generate_test_value(arg, "error")
        
        # 生成断言
        assertions = ["with pytest.raises(Exception):"]
        assertions.append("    result = method(**input_data)")
        
        return TestCase(
            name=test_name,
            description=f"测试 {method['name']} 错误情况",
            test_type=TestType.UNIT,
            setup="",
            input_data=input_data,
            expected_output="Exception",
            assertions=assertions
        )
    
    def _generate_test_value(self, param_name: str, test_type: str) -> Any:
        """生成测试值"""
        # 根据参数名推测类型
        if 'id' in param_name.lower():
            if test_type == "normal":
                return 1
            elif test_type == "edge":
                return 0
            else:
                return -1
        elif 'name' in param_name.lower():
            if test_type == "normal":
                return "'test'"
            elif test_type == "edge":
                return "''"
            else:
                return None
        elif 'count' in param_name.lower() or 'amount' in param_name.lower():
            if test_type == "normal":
                return 10
            elif test_type == "edge":
                return 0
            else:
                return -1
        elif 'list' in param_name.lower() or 'items' in param_name.lower():
            if test_type == "normal":
                return "[1, 2, 3]"
            elif test_type == "edge":
                return "[]"
            else:
                return None
        else:
            # 默认值
            if test_type == "normal":
                return "'value'"
            elif test_type == "edge":
                return "''"
            else:
                return None
    
    def _generate_expected_output(self, method: Dict[str, Any], input_data: Dict[str, Any]) -> Any:
        """生成期望输出"""
        # 简化实现：根据方法名推测输出
        method_name = method['name'].lower()
        
        if 'get' in method_name:
            return input_data.get(list(input_data.keys())[0], "'result'")
        elif 'calculate' in method_name or 'compute' in method_name:
            return 42  # 示例值
        elif 'is' in method_name or 'has' in method_name:
            return True
        elif 'add' in method_name:
            return sum(1 for v in input_data.values() if isinstance(v, int))
        else:
            return "'expected_result'"
    
    def generate_test_code(self, test_suite: TestSuite) -> str:
        """生成测试代码"""
        code = []
        
        # 添加导入
        for import_stmt in test_suite.imports:
            code.append(import_stmt)
        code.append("")
        
        # 添加类定义
        code.append(f"class {test_suite.class_name}:")
        code.append('    """测试套件"""')
        code.append("")
        
        # 添加fixtures
        for fixture in test_suite.fixtures:
            for line in fixture.split('\n'):
                code.append(f"    {line}")
            code.append("")
        
        # 添加测试用例
        for test_case in test_suite.test_cases:
            code.append(f"    def {test_case.name}(self):")
            code.append(f'        """{test_case.description}"""')
            
            # 添加setup
            if test_case.setup:
                code.append(f"        {test_case.setup}")
            
            # 添加测试执行
            if test_case.input_data:
                args_str = ", ".join([f"{k}={v}" for k, v in test_case.input_data.items()])
                code.append(f"        result = self.target_method({args_str})")
            else:
                code.append("        result = self.target_method()")
            
            # 添加断言
            for assertion in test_case.assertions:
                code.append(f"        {assertion}")
            
            code.append("")
        
        return '\n'.join(code)

# 测试覆盖率分析器
class CoverageAnalyzer:
    def __init__(self):
        self.coverage_data = {}
        
    def analyze_coverage(self, test_file: str, source_file: str) -> Dict[str, Any]:
        """分析测试覆盖率"""
        # 简化实现
        return {
            'line_coverage': 85.5,
            'branch_coverage': 78.2,
            'function_coverage': 92.1,
            'uncovered_lines': [15, 23, 45],
            'recommendations': [
                "添加第15行的测试用例",
                "覆盖第23行的分支条件",
                "测试第45行的异常处理"
            ]
        }
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """生成覆盖率报告"""
        report = []
        report.append("# 测试覆盖率报告")
        report.append("")
        report.append(f"行覆盖率: {coverage_data['line_coverage']}%")
        report.append(f"分支覆盖率: {coverage_data['branch_coverage']}%")
        report.append(f"函数覆盖率: {coverage_data['function_coverage']}%")
        report.append("")
        report.append("未覆盖的行:")
        for line in coverage_data['uncovered_lines']:
            report.append(f"- 第{line}行")
        report.append("")
        report.append("改进建议:")
        for rec in coverage_data['recommendations']:
            report.append(f"- {rec}")
        
        return '\n'.join(report)

# 使用示例
def main():
    # 示例代码
    sample_code = '''
class Calculator:
    """简单的计算器类"""
    
    def add(self, a, b):
        """加法运算"""
        return a + b
    
    def divide(self, a, b):
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    def is_positive(self, number):
        """检查数字是否为正数"""
        return number > 0
'''
    
    # 创建测试生成器
    generator = TestGenerator()
    
    # 生成测试
    test_suites = generator.generate_tests_from_code(sample_code, "calculator.py")
    
    print("生成的测试套件:")
    for suite in test_suites:
        print(f"- {suite.class_name}")
        print(f"  测试用例数: {len(suite.test_cases)}")
        
        # 生成测试代码
        test_code = generator.generate_test_code(suite)
        print("\n测试代码:")
        print(test_code)
        print("\n" + "="*50 + "\n")
    
    # 分析覆盖率
    analyzer = CoverageAnalyzer()
    coverage_data = analyzer.analyze_coverage("test_calculator.py", "calculator.py")
    
    print("覆盖率分析:")
    coverage_report = analyzer.generate_coverage_report(coverage_data)
    print(coverage_report)

if __name__ == '__main__':
    main()
```

### 测试工具集成
```python
import subprocess
import json
from typing import Dict, Any, List
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.test_results = {}
        
    def run_pytest(self, test_path: str, options: List[str] = None) -> Dict[str, Any]:
        """运行pytest测试"""
        cmd = ['pytest', test_path, '--json-report', '--json-report-file=test_results.json']
        
        if options:
            cmd.extend(options)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # 读取测试结果
            with open('test_results.json', 'r') as f:
                results = json.load(f)
            
            return {
                'success': True,
                'summary': results.get('summary', {}),
                'tests': results.get('tests', []),
                'duration': results.get('duration', 0)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }
    
    def run_coverage(self, test_path: str, source_path: str) -> Dict[str, Any]:
        """运行覆盖率测试"""
        cmd = [
            'coverage', 'run', '-m', 'pytest', test_path,
            '&&', 'coverage', 'report', '--json', '--outfile=coverage.json'
        ]
        
        try:
            result = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True, check=True)
            
            # 读取覆盖率结果
            with open('coverage.json', 'r') as f:
                coverage_data = json.load(f)
            
            return {
                'success': True,
                'coverage': coverage_data,
                'percent_covered': coverage_data.get('totals', {}).get('percent_covered', 0)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': e.stderr,
                'return_code': e.returncode
            }

class MockGenerator:
    def __init__(self):
        self.mocks = {}
    
    def generate_mock(self, class_name: str, methods: List[str]) -> str:
        """生成模拟对象"""
        mock_code = []
        mock_code.append(f"class Mock{class_name}:")
        mock_code.append('    """模拟对象"""')
        mock_code.append("")
        
        for method in methods:
            mock_code.append(f"    def {method}(self, *args, **kwargs):")
            mock_code.append(f"        return 'mock_{method}_result'")
            mock_code.append("")
        
        return '\n'.join(mock_code)
    
    def generate_patch_decorator(self, module: str, target: str) -> str:
        """生成patch装饰器"""
        return f"@mock.patch('{module}.{target}')"

# 测试数据生成器
class TestDataGenerator:
    def __init__(self):
        self.data_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\d{10,11}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$'
        }
    
    def generate_test_data(self, data_type: str, count: int = 10) -> List[Any]:
        """生成测试数据"""
        if data_type == 'string':
            return [f'test_string_{i}' for i in range(count)]
        elif data_type == 'integer':
            return list(range(1, count + 1))
        elif data_type == 'email':
            return [f'user{i}@example.com' for i in range(count)]
        elif data_type == 'json':
            return [{'id': i, 'name': f'item_{i}'} for i in range(count)]
        else:
            return [f'data_{i}' for i in range(count)]
    
    def generate_edge_cases(self, data_type: str) -> List[Any]:
        """生成边界情况数据"""
        edge_cases = []
        
        if data_type == 'string':
            edge_cases = ['', ' ', 'a' * 1000, '特殊字符!@#$%', '中文测试']
        elif data_type == 'integer':
            edge_cases = [0, -1, 999999999, -999999999]
        elif data_type == 'list':
            edge_cases = [[], [None], [1, 2, 3] * 1000]
        elif data_type == 'dict':
            edge_cases = [{}, {'key': None}, {str(i): i for i in range(1000)}]
        
        return edge_cases

# 使用示例
def main():
    print("=== 测试工具集成 ===")
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 运行测试（示例）
    # test_results = runner.run_pytest("tests/")
    # print("测试结果:", test_results)
    
    # 运行覆盖率测试（示例）
    # coverage_results = runner.run_coverage("tests/", "src/")
    # print("覆盖率结果:", coverage_results)
    
    print("\n=== 模拟对象生成 ===")
    mock_generator = MockGenerator()
    
    mock_code = mock_generator.generate_mock("UserService", ["get_user", "create_user", "delete_user"])
    print("生成的模拟对象:")
    print(mock_code)
    
    print("\n=== 测试数据生成 ===")
    data_generator = TestDataGenerator()
    
    test_data = data_generator.generate_test_data("email", 5)
    print("生成的邮箱数据:", test_data)
    
    edge_cases = data_generator.generate_edge_cases("string")
    print("边界情况数据:", edge_cases)

if __name__ == '__main__':
    main()
```

## 测试生成最佳实践

### 测试设计
1. **测试命名**: 使用清晰的测试名称
2. **测试结构**: 遵循AAA模式（Arrange-Act-Assert）
3. **测试独立**: 确保测试之间相互独立
4. **测试快速**: 保持测试执行速度
5. **测试可读**: 编写易于理解的测试

### 测试覆盖
1. **功能覆盖**: 覆盖所有功能路径
2. **边界覆盖**: 测试所有边界条件
3. **错误覆盖**: 测试所有异常情况
4. **集成覆盖**: 测试组件集成
5. **性能覆盖**: 验证性能要求

### 测试维护
1. **定期更新**: 随代码更新测试
2. **重构测试**: 保持测试代码质量
3. **监控覆盖率**: 持续监控测试覆盖率
4. **清理测试**: 移除过时的测试
5. **文档更新**: 更新测试文档

### 测试自动化
1. **CI集成**: 集成到持续集成流程
2. **自动运行**: 自动执行测试套件
3. **报告生成**: 自动生成测试报告
4. **失败通知**: 测试失败时自动通知
5. **性能监控**: 监控测试执行性能

## 相关技能

- **code-review** - 代码审查与标准
- **error-handling** - 错误处理与日志
- **refactoring-patterns** - 重构模式
- **documentation-generator** - 文档生成
