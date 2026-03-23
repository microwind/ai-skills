# API测试器参考文档

## API测试器概述

### 什么是API测试器
API测试器是一个专门用于测试API接口的工具，支持多种API协议（REST、GraphQL、gRPC等），提供功能测试、性能测试、安全测试等多种测试类型。该工具支持测试用例管理、数据驱动测试、断言验证、报告生成等功能，帮助开发者和测试人员确保API的质量和可靠性。

### 主要功能
- **多协议支持**: 支持REST、GraphQL、gRPC、WebSocket等API协议
- **多种测试类型**: 功能测试、性能测试、安全测试、集成测试
- **测试用例管理**: 创建、组织、执行测试用例
- **断言验证**: 状态码、响应头、响应体、响应时间断言
- **数据驱动测试**: 支持CSV、Excel、数据库等数据源
- **性能测试**: 负载测试、压力测试、容量测试
- **安全测试**: 认证测试、输入验证、数据保护测试
- **报告生成**: 多格式测试报告和统计分析

## 核心测试引擎

### HTTP测试引擎
```python
# http_test_engine.py
import requests
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import threading

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

@dataclass
class TestRequest:
    method: HttpMethod
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Union[Dict, str, bytes]] = None
    json: Optional[Dict[str, Any]] = None
    files: Optional[Dict[str, Any]] = None
    timeout: Optional[tuple] = None
    auth: Optional[tuple] = None
    verify: bool = True

@dataclass
class TestResponse:
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    json_data: Optional[Dict[str, Any]]
    elapsed: float
    success: bool
    error: Optional[str] = None

class HTTPTestEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'API-Tester/1.0'
        })
    
    def execute_request(self, test_request: TestRequest) -> TestResponse:
        """执行HTTP请求"""
        try:
            start_time = time.time()
            
            # 准备请求参数
            request_kwargs = {
                'method': test_request.method.value,
                'url': test_request.url,
                'headers': test_request.headers,
                'params': test_request.params,
                'timeout': test_request.timeout,
                'verify': test_request.verify
            }
            
            # 根据数据类型设置请求体
            if test_request.json:
                request_kwargs['json'] = test_request.json
            elif test_request.data:
                request_kwargs['data'] = test_request.data
            elif test_request.files:
                request_kwargs['files'] = test_request.files
            
            if test_request.auth:
                request_kwargs['auth'] = test_request.auth
            
            # 执行请求
            response = self.session.request(**request_kwargs)
            elapsed_time = time.time() - start_time
            
            # 解析响应
            json_data = None
            try:
                json_data = response.json()
            except:
                pass
            
            return TestResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                text=response.text,
                json_data=json_data,
                elapsed=elapsed_time,
                success=True
            )
            
        except requests.exceptions.Timeout:
            return TestResponse(
                status_code=0,
                headers={},
                content=b'',
                text='',
                json_data=None,
                elapsed=0,
                success=False,
                error='Request timeout'
            )
        except requests.exceptions.ConnectionError:
            return TestResponse(
                status_code=0,
                headers={},
                content=b'',
                text='',
                json_data=None,
                elapsed=0,
                success=False,
                error='Connection error'
            )
        except Exception as e:
            return TestResponse(
                status_code=0,
                headers={},
                content=b'',
                text='',
                json_data=None,
                elapsed=0,
                success=False,
                error=str(e)
            )
    
    def execute_batch_requests(self, requests_list: List[TestRequest], 
                             max_workers: int = 10) -> List[TestResponse]:
        """批量执行HTTP请求"""
        responses = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_request = {
                executor.submit(self.execute_request, req): req 
                for req in requests_list
            }
            
            for future in concurrent.futures.as_completed(future_to_request):
                response = future.result()
                responses.append(response)
        
        return responses
    
    def set_global_headers(self, headers: Dict[str, str]):
        """设置全局请求头"""
        self.session.headers.update(headers)
    
    def set_auth(self, auth_type: str, **kwargs):
        """设置认证"""
        if auth_type == 'basic':
            self.session.auth = (kwargs.get('username'), kwargs.get('password'))
        elif auth_type == 'bearer':
            self.session.headers['Authorization'] = f"Bearer {kwargs.get('token')}"
        elif auth_type == 'api_key':
            key_name = kwargs.get('key_name', 'X-API-Key')
            key_value = kwargs.get('key_value')
            key_location = kwargs.get('key_location', 'header')
            
            if key_location == 'header':
                self.session.headers[key_name] = key_value
            elif key_location == 'query':
                # 查询参数需要在每个请求中设置
                pass
    
    def close(self):
        """关闭会话"""
        self.session.close()

# 使用示例
engine = HTTPTestEngine()

# 设置认证
engine.set_auth('bearer', token='your_bearer_token')

# 创建测试请求
request = TestRequest(
    method=HttpMethod.GET,
    url='https://api.example.com/users',
    params={'page': 1, 'limit': 10},
    headers={'Accept': 'application/json'},
    timeout=(10, 30)
)

# 执行请求
response = engine.execute_request(request)

print(f"状态码: {response.status_code}")
print(f"响应时间: {response.elapsed:.2f}秒")
print(f"响应内容: {response.text}")
```

### 断言验证引擎
```python
# assertion_engine.py
import re
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import jsonpath

class AssertionType(Enum):
    STATUS_CODE = "status_code"
    HEADER = "header"
    BODY = "body"
    RESPONSE_TIME = "response_time"
    JSON_PATH = "json_path"

class MatchType(Enum):
    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"

@dataclass
class Assertion:
    assertion_type: AssertionType
    match_type: MatchType
    expected_value: Any
    actual_value: Any
    path: Optional[str] = None
    description: Optional[str] = None
    passed: bool = False
    error_message: Optional[str] = None

class AssertionEngine:
    def __init__(self):
        self.assertions = []
    
    def add_status_code_assertion(self, expected_code: Union[int, List[int]], 
                                 match_type: MatchType = MatchType.EXACT) -> Assertion:
        """添加状态码断言"""
        assertion = Assertion(
            assertion_type=AssertionType.STATUS_CODE,
            match_type=match_type,
            expected_value=expected_code,
            actual_value=None,
            description=f"状态码应为 {expected_code}"
        )
        self.assertions.append(assertion)
        return assertion
    
    def add_header_assertion(self, header_name: str, expected_value: str,
                           match_type: MatchType = MatchType.EXACT) -> Assertion:
        """添加响应头断言"""
        assertion = Assertion(
            assertion_type=AssertionType.HEADER,
            match_type=match_type,
            expected_value=expected_value,
            actual_value=None,
            path=header_name,
            description=f"响应头 {header_name} 应为 {expected_value}"
        )
        self.assertions.append(assertion)
        return assertion
    
    def add_body_assertion(self, expected_value: Any, 
                          match_type: MatchType = MatchType.CONTAINS) -> Assertion:
        """添加响应体断言"""
        assertion = Assertion(
            assertion_type=AssertionType.BODY,
            match_type=match_type,
            expected_value=expected_value,
            actual_value=None,
            description=f"响应体应包含 {expected_value}"
        )
        self.assertions.append(assertion)
        return assertion
    
    def add_json_path_assertion(self, json_path: str, expected_value: Any,
                               match_type: MatchType = MatchType.EXACT) -> Assertion:
        """添加JSON路径断言"""
        assertion = Assertion(
            assertion_type=AssertionType.JSON_PATH,
            match_type=match_type,
            expected_value=expected_value,
            actual_value=None,
            path=json_path,
            description=f"JSON路径 {json_path} 应为 {expected_value}"
        )
        self.assertions.append(assertion)
        return assertion
    
    def add_response_time_assertion(self, max_time: float,
                                  match_type: MatchType = MatchType.LESS_THAN) -> Assertion:
        """添加响应时间断言"""
        assertion = Assertion(
            assertion_type=AssertionType.RESPONSE_TIME,
            match_type=match_type,
            expected_value=max_time,
            actual_value=None,
            description=f"响应时间应小于 {max_time} 秒"
        )
        self.assertions.append(assertion)
        return assertion
    
    def validate_assertions(self, response: 'TestResponse') -> List[Assertion]:
        """验证所有断言"""
        results = []
        
        for assertion in self.assertions:
            try:
                if assertion.assertion_type == AssertionType.STATUS_CODE:
                    assertion.actual_value = response.status_code
                    assertion.passed = self._validate_value(
                        assertion.actual_value,
                        assertion.expected_value,
                        assertion.match_type
                    )
                
                elif assertion.assertion_type == AssertionType.HEADER:
                    actual_value = response.headers.get(assertion.path, '')
                    assertion.actual_value = actual_value
                    assertion.passed = self._validate_value(
                        actual_value,
                        assertion.expected_value,
                        assertion.match_type
                    )
                
                elif assertion.assertion_type == AssertionType.BODY:
                    actual_value = response.text
                    assertion.actual_value = actual_value
                    assertion.passed = self._validate_value(
                        actual_value,
                        assertion.expected_value,
                        assertion.match_type
                    )
                
                elif assertion.assertion_type == AssertionType.JSON_PATH:
                    if response.json_data:
                        actual_value = self._extract_json_path(response.json_data, assertion.path)
                        assertion.actual_value = actual_value
                        assertion.passed = self._validate_value(
                            actual_value,
                            assertion.expected_value,
                            assertion.match_type
                        )
                    else:
                        assertion.passed = False
                        assertion.error_message = "响应不是有效的JSON"
                
                elif assertion.assertion_type == AssertionType.RESPONSE_TIME:
                    assertion.actual_value = response.elapsed
                    assertion.passed = self._validate_value(
                        response.elapsed,
                        assertion.expected_value,
                        assertion.match_type
                    )
                
                if not assertion.passed and not assertion.error_message:
                    assertion.error_message = self._generate_error_message(assertion)
                
            except Exception as e:
                assertion.passed = False
                assertion.error_message = f"断言验证失败: {str(e)}"
            
            results.append(assertion)
        
        return results
    
    def _validate_value(self, actual: Any, expected: Any, match_type: MatchType) -> bool:
        """验证值"""
        if match_type == MatchType.EXACT:
            return actual == expected
        elif match_type == MatchType.CONTAINS:
            return str(expected) in str(actual)
        elif match_type == MatchType.REGEX:
            return bool(re.search(str(expected), str(actual)))
        elif match_type == MatchType.EXISTS:
            return actual is not None and actual != ''
        elif match_type == MatchType.NOT_EXISTS:
            return actual is None or actual == ''
        elif match_type == MatchType.GREATER_THAN:
            return float(actual) > float(expected)
        elif match_type == MatchType.LESS_THAN:
            return float(actual) < float(expected)
        elif match_type == MatchType.EQUALS:
            return str(actual) == str(expected)
        elif match_type == MatchType.NOT_EQUALS:
            return str(actual) != str(expected)
        
        return False
    
    def _extract_json_path(self, json_data: Dict[str, Any], path: str) -> Any:
        """提取JSON路径值"""
        try:
            return jsonpath.jsonpath(json_data, path)[0]
        except:
            return None
    
    def _generate_error_message(self, assertion: Assertion) -> str:
        """生成错误消息"""
        return f"期望 {assertion.expected_value}，实际 {assertion.actual_value}"
    
    def clear_assertions(self):
        """清空断言"""
        self.assertions.clear()

# 使用示例
engine = AssertionEngine()

# 添加断言
engine.add_status_code_assertion(200)
engine.add_header_assertion('Content-Type', 'application/json')
engine.add_json_path_assertion('$.users[0].name', 'John Doe')
engine.add_response_time_assertion(1.0)

# 假设有一个响应对象
# response = TestResponse(...)
# results = engine.validate_assertions(response)
# 
# for assertion in results:
#     print(f"断言: {assertion.description}")
#     print(f"结果: {'通过' if assertion.passed else '失败'}")
#     if not assertion.passed:
#         print(f"错误: {assertion.error_message}")
```

## 测试用例管理

### 测试用例管理器
```python
# test_case_manager.py
import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import os

@dataclass
class TestCase:
    id: str
    name: str
    description: str
    method: str
    url: str
    headers: Dict[str, str]
    params: Dict[str, Any]
    body: Optional[Dict[str, Any]]
    assertions: List[Dict[str, Any]]
    tags: List[str]
    priority: str
    enabled: bool
    created_at: str
    updated_at: str

@dataclass
class TestSuite:
    id: str
    name: str
    description: str
    test_cases: List[str]  # 测试用例ID列表
    setup: Optional[Dict[str, Any]]
    teardown: Optional[Dict[str, Any]]
    tags: List[str]
    created_at: str
    updated_at: str

class TestCaseManager:
    def __init__(self, storage_path: str = "./test_data"):
        self.storage_path = storage_path
        self.test_cases_file = os.path.join(storage_path, "test_cases.json")
        self.test_suites_file = os.path.join(storage_path, "test_suites.json")
        
        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)
        
        # 加载现有数据
        self.test_cases = self._load_test_cases()
        self.test_suites = self._load_test_suites()
    
    def create_test_case(self, name: str, description: str, method: str, url: str,
                        headers: Dict[str, str] = None, params: Dict[str, Any] = None,
                        body: Dict[str, Any] = None, assertions: List[Dict[str, Any]] = None,
                        tags: List[str] = None, priority: str = "medium") -> TestCase:
        """创建测试用例"""
        test_case = TestCase(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            method=method,
            url=url,
            headers=headers or {},
            params=params or {},
            body=body,
            assertions=assertions or [],
            tags=tags or [],
            priority=priority,
            enabled=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.test_cases[test_case.id] = test_case
        self._save_test_cases()
        
        return test_case
    
    def update_test_case(self, test_case_id: str, **kwargs) -> Optional[TestCase]:
        """更新测试用例"""
        if test_case_id not in self.test_cases:
            return None
        
        test_case = self.test_cases[test_case_id]
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(test_case, key):
                setattr(test_case, key, value)
        
        test_case.updated_at = datetime.now().isoformat()
        
        self._save_test_cases()
        
        return test_case
    
    def delete_test_case(self, test_case_id: str) -> bool:
        """删除测试用例"""
        if test_case_id not in self.test_cases:
            return False
        
        del self.test_cases[test_case_id]
        
        # 从测试套件中移除
        for suite in self.test_suites.values():
            if test_case_id in suite.test_cases:
                suite.test_cases.remove(test_case_id)
        
        self._save_test_cases()
        self._save_test_suites()
        
        return True
    
    def get_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """获取测试用例"""
        return self.test_cases.get(test_case_id)
    
    def list_test_cases(self, tags: List[str] = None, priority: str = None,
                       enabled_only: bool = False) -> List[TestCase]:
        """列出测试用例"""
        test_cases = list(self.test_cases.values())
        
        # 过滤条件
        if tags:
            test_cases = [tc for tc in test_cases if any(tag in tc.tags for tag in tags)]
        
        if priority:
            test_cases = [tc for tc in test_cases if tc.priority == priority]
        
        if enabled_only:
            test_cases = [tc for tc in test_cases if tc.enabled]
        
        return test_cases
    
    def create_test_suite(self, name: str, description: str,
                         test_case_ids: List[str] = None,
                         setup: Dict[str, Any] = None,
                         teardown: Dict[str, Any] = None,
                         tags: List[str] = None) -> TestSuite:
        """创建测试套件"""
        test_suite = TestSuite(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            test_cases=test_case_ids or [],
            setup=setup,
            teardown=teardown,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.test_suites[test_suite.id] = test_suite
        self._save_test_suites()
        
        return test_suite
    
    def add_test_case_to_suite(self, suite_id: str, test_case_id: str) -> bool:
        """向测试套件添加测试用例"""
        if suite_id not in self.test_suites or test_case_id not in self.test_cases:
            return False
        
        suite = self.test_suites[suite_id]
        if test_case_id not in suite.test_cases:
            suite.test_cases.append(test_case_id)
            suite.updated_at = datetime.now().isoformat()
            self._save_test_suites()
        
        return True
    
    def remove_test_case_from_suite(self, suite_id: str, test_case_id: str) -> bool:
        """从测试套件移除测试用例"""
        if suite_id not in self.test_suites:
            return False
        
        suite = self.test_suites[suite_id]
        if test_case_id in suite.test_cases:
            suite.test_cases.remove(test_case_id)
            suite.updated_at = datetime.now().isoformat()
            self._save_test_suites()
        
        return True
    
    def get_test_suite(self, suite_id: str) -> Optional[TestSuite]:
        """获取测试套件"""
        return self.test_suites.get(suite_id)
    
    def list_test_suites(self, tags: List[str] = None) -> List[TestSuite]:
        """列出测试套件"""
        suites = list(self.test_suites.values())
        
        if tags:
            suites = [suite for suite in suites if any(tag in suite.tags for tag in tags)]
        
        return suites
    
    def get_suite_test_cases(self, suite_id: str) -> List[TestCase]:
        """获取测试套件中的测试用例"""
        if suite_id not in self.test_suites:
            return []
        
        suite = self.test_suites[suite_id]
        test_cases = []
        
        for test_case_id in suite.test_cases:
            if test_case_id in self.test_cases:
                test_cases.append(self.test_cases[test_case_id])
        
        return test_cases
    
    def import_test_cases_from_file(self, file_path: str) -> int:
        """从文件导入测试用例"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            
            if 'test_cases' in data:
                for tc_data in data['test_cases']:
                    test_case = TestCase(**tc_data)
                    self.test_cases[test_case.id] = test_case
                    imported_count += 1
            
            if 'test_suites' in data:
                for ts_data in data['test_suites']:
                    test_suite = TestSuite(**ts_data)
                    self.test_suites[test_suite.id] = test_suite
            
            self._save_test_cases()
            self._save_test_suites()
            
            return imported_count
            
        except Exception as e:
            print(f"导入失败: {e}")
            return 0
    
    def export_test_cases_to_file(self, file_path: str, suite_ids: List[str] = None) -> bool:
        """导出测试用例到文件"""
        try:
            export_data = {
                'test_cases': [],
                'test_suites': []
            }
            
            if suite_ids:
                # 导出指定套件的测试用例
                test_case_ids = set()
                for suite_id in suite_ids:
                    if suite_id in self.test_suites:
                        suite = self.test_suites[suite_id]
                        test_case_ids.update(suite.test_cases)
                        export_data['test_suites'].append(asdict(suite))
                
                for tc_id in test_case_ids:
                    if tc_id in self.test_cases:
                        export_data['test_cases'].append(asdict(self.test_cases[tc_id]))
            else:
                # 导出所有测试用例和套件
                export_data['test_cases'] = [asdict(tc) for tc in self.test_cases.values()]
                export_data['test_suites'] = [asdict(ts) for ts in self.test_suites.values()]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def _load_test_cases(self) -> Dict[str, TestCase]:
        """加载测试用例"""
        if not os.path.exists(self.test_cases_file):
            return {}
        
        try:
            with open(self.test_cases_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_cases = {}
            for tc_data in data:
                test_case = TestCase(**tc_data)
                test_cases[test_case.id] = test_case
            
            return test_cases
            
        except Exception as e:
            print(f"加载测试用例失败: {e}")
            return {}
    
    def _load_test_suites(self) -> Dict[str, TestSuite]:
        """加载测试套件"""
        if not os.path.exists(self.test_suites_file):
            return {}
        
        try:
            with open(self.test_suites_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_suites = {}
            for ts_data in data:
                test_suite = TestSuite(**ts_data)
                test_suites[test_suite.id] = test_suite
            
            return test_suites
            
        except Exception as e:
            print(f"加载测试套件失败: {e}")
            return {}
    
    def _save_test_cases(self):
        """保存测试用例"""
        try:
            data = [asdict(tc) for tc in self.test_cases.values()]
            with open(self.test_cases_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存测试用例失败: {e}")
    
    def _save_test_suites(self):
        """保存测试套件"""
        try:
            data = [asdict(ts) for ts in self.test_suites.values()]
            with open(self.test_suites_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存测试套件失败: {e}")

# 使用示例
manager = TestCaseManager()

# 创建测试用例
test_case = manager.create_test_case(
    name="获取用户列表",
    description="测试获取用户列表API",
    method="GET",
    url="https://api.example.com/users",
    headers={"Accept": "application/json"},
    params={"page": 1, "limit": 10},
    assertions=[
        {
            "type": "status_code",
            "expected": 200,
            "match_type": "exact"
        },
        {
            "type": "json_path",
            "path": "$.users",
            "expected": "exists",
            "match_type": "exists"
        }
    ],
    tags=["用户管理", "基础功能"],
    priority="high"
)

print(f"创建测试用例: {test_case.name} (ID: {test_case.id})")

# 创建测试套件
test_suite = manager.create_test_suite(
    name="用户管理API测试",
    description="用户管理相关API的测试套件",
    test_case_ids=[test_case.id],
    tags=["用户管理", "回归测试"]
)

print(f"创建测试套件: {test_suite.name} (ID: {test_suite.id})")

# 获取测试套件中的测试用例
suite_test_cases = manager.get_suite_test_cases(test_suite.id)
print(f"测试套件包含 {len(suite_test_cases)} 个测试用例")
```

## 数据驱动测试

### 数据驱动测试引擎
```python
# data_driven_test.py
import csv
import json
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Optional, Iterator
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class TestDataRow:
    data: Dict[str, Any]
    row_number: int
    source: str

class DataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_data(self) -> Iterator[TestDataRow]:
        pass
    
    @abstractmethod
    def close(self):
        pass

class CSVDataSource(DataSource):
    """CSV数据源"""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8', delimiter: str = ','):
        self.file_path = file_path
        self.encoding = encoding
        self.delimiter = delimiter
        self.file = None
    
    def get_data(self) -> Iterator[TestDataRow]:
        """读取CSV数据"""
        with open(self.file_path, 'r', encoding=self.encoding, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            
            for row_number, row in enumerate(reader, 1):
                # 转换数据类型
                processed_row = {}
                for key, value in row.items():
                    processed_row[key] = self._convert_value(value.strip())
                
                yield TestDataRow(
                    data=processed_row,
                    row_number=row_number,
                    source=self.file_path
                )
    
    def _convert_value(self, value: str) -> Any:
        """转换值类型"""
        if not value:
            return None
        
        # 尝试转换为数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 尝试转换为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 尝试转换为JSON
        try:
            return json.loads(value)
        except ValueError:
            pass
        
        return value
    
    def close(self):
        """关闭资源"""
        if self.file:
            self.file.close()

class ExcelDataSource(DataSource):
    """Excel数据源"""
    
    def __init__(self, file_path: str, sheet_name: str = None):
        self.file_path = file_path
        self.sheet_name = sheet_name
    
    def get_data(self) -> Iterator[TestDataRow]:
        """读取Excel数据"""
        try:
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
            
            for row_number, row in df.iterrows():
                # 处理NaN值
                processed_row = {}
                for key, value in row.items():
                    if pd.isna(value):
                        processed_row[key] = None
                    else:
                        processed_row[key] = value
                
                yield TestDataRow(
                    data=processed_row,
                    row_number=row_number + 1,
                    source=self.file_path
                )
        
        except Exception as e:
            print(f"读取Excel文件失败: {e}")
    
    def close(self):
        """关闭资源"""
        pass

class JSONDataSource(DataSource):
    """JSON数据源"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def get_data(self) -> Iterator[TestDataRow]:
        """读取JSON数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for row_number, item in enumerate(data, 1):
                    yield TestDataRow(
                        data=item,
                        row_number=row_number,
                        source=self.file_path
                    )
            elif isinstance(data, dict):
                yield TestDataRow(
                    data=data,
                    row_number=1,
                    source=self.file_path
                )
        
        except Exception as e:
            print(f"读取JSON文件失败: {e}")
    
    def close(self):
        """关闭资源"""
        pass

class DatabaseDataSource(DataSource):
    """数据库数据源"""
    
    def __init__(self, connection_string: str, query: str):
        self.connection_string = connection_string
        self.query = query
        self.connection = None
    
    def get_data(self) -> Iterator[TestDataRow]:
        """读取数据库数据"""
        try:
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(self.query)
            
            columns = [description[0] for description in cursor.description]
            
            for row_number, row in enumerate(cursor.fetchall(), 1):
                row_data = dict(zip(columns, row))
                
                yield TestDataRow(
                    data=row_data,
                    row_number=row_number,
                    source="database"
                )
        
        except Exception as e:
            print(f"读取数据库数据失败: {e}")
    
    def close(self):
        """关闭资源"""
        if self.connection:
            self.connection.close()

class DataDrivenTestEngine:
    """数据驱动测试引擎"""
    
    def __init__(self):
        self.data_sources = []
        self.test_template = None
        self.parameter_mapping = {}
    
    def add_data_source(self, data_source: DataSource):
        """添加数据源"""
        self.data_sources.append(data_source)
    
    def set_test_template(self, test_template: Dict[str, Any]):
        """设置测试模板"""
        self.test_template = test_template
    
    def set_parameter_mapping(self, mapping: Dict[str, str]):
        """设置参数映射"""
        self.parameter_mapping = mapping
    
    def generate_test_cases(self) -> List[Dict[str, Any]]:
        """生成测试用例"""
        test_cases = []
        
        for data_source in self.data_sources:
            for data_row in data_source.get_data():
                test_case = self._create_test_case_from_data(data_row)
                if test_case:
                    test_cases.append(test_case)
        
        return test_cases
    
    def _create_test_case_from_data(self, data_row: TestDataRow) -> Optional[Dict[str, Any]]:
        """从数据行创建测试用例"""
        if not self.test_template:
            return None
        
        # 复制模板
        test_case = self.test_template.copy()
        
        # 映射参数
        for template_param, data_param in self.parameter_mapping.items():
            if data_param in data_row.data:
                self._set_nested_value(test_case, template_param, data_row.data[data_param])
        
        # 添加数据源信息
        test_case['_data_row'] = data_row
        
        return test_case
    
    def _set_nested_value(self, obj: Dict[str, Any], path: str, value: Any):
        """设置嵌套值"""
        keys = path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def close(self):
        """关闭所有数据源"""
        for data_source in self.data_sources:
            data_source.close()

# 使用示例
engine = DataDrivenTestEngine()

# 设置测试模板
test_template = {
    "name": "用户登录测试",
    "method": "POST",
    "url": "https://api.example.com/auth/login",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "username": "",
        "password": ""
    },
    "assertions": [
        {
            "type": "status_code",
            "expected": 200,
            "match_type": "exact"
        }
    ]
}

# 设置参数映射
parameter_mapping = {
    "body.username": "username",
    "body.password": "password",
    "name": "test_name"
}

engine.set_test_template(test_template)
engine.set_parameter_mapping(parameter_mapping)

# 添加CSV数据源
csv_source = CSVDataSource("test_data.csv")
engine.add_data_source(csv_source)

# 生成测试用例
test_cases = engine.generate_test_cases()

print(f"生成了 {len(test_cases)} 个测试用例")

for i, test_case in enumerate(test_cases[:3]):  # 显示前3个
    print(f"\n测试用例 {i+1}:")
    print(f"名称: {test_case['name']}")
    print(f"URL: {test_case['url']}")
    print(f"请求体: {test_case['body']}")
    print(f"数据源: {test_case['_data_row'].source}")
    print(f"行号: {test_case['_data_row'].row_number}")

# 关闭数据源
engine.close()
```

## 性能测试

### 性能测试引擎
```python
# performance_test.py
import time
import threading
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class PerformanceMetrics:
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    response_times: List[float]

@dataclass
class LoadTestConfig:
    initial_users: int
    max_users: int
    step_users: int
    step_duration: int  # 秒
    test_duration: int  # 秒
    ramp_up_time: int  # 秒
    think_time: float  # 秒

class PerformanceTestEngine:
    def __init__(self):
        self.results = []
        self.is_running = False
        self.stop_event = threading.Event()
    
    def execute_load_test(self, test_request: Callable, config: LoadTestConfig) -> PerformanceMetrics:
        """执行负载测试"""
        self.is_running = True
        self.stop_event.clear()
        
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        def worker(user_id: int):
            nonlocal successful_requests, failed_requests
            
            while not self.stop_event.is_set() and (time.time() - start_time) < config.test_duration:
                request_start = time.time()
                
                try:
                    # 执行测试请求
                    response = test_request()
                    request_time = time.time() - request_start
                    
                    all_response_times.append(request_time)
                    successful_requests += 1
                    
                except Exception as e:
                    failed_requests += 1
                    print(f"用户 {user_id} 请求失败: {e}")
                
                # 思考时间
                if config.think_time > 0:
                    time.sleep(config.think_time)
        
        # 启动用户线程
        threads = []
        current_users = config.initial_users
        
        def ramp_up_users():
            nonlocal current_users
            step_start = time.time()
            
            while current_users < config.max_users and (time.time() - start_time) < config.test_duration:
                if time.time() - step_start >= config.step_duration:
                    # 增加用户
                    new_users = min(config.step_users, config.max_users - current_users)
                    
                    for i in range(new_users):
                        user_id = current_users + i
                        thread = threading.Thread(target=worker, args=(user_id,))
                        thread.start()
                        threads.append(thread)
                    
                    current_users += new_users
                    step_start = time.time()
                    print(f"当前用户数: {current_users}")
                
                time.sleep(1)
        
        # 启动初始用户
        for i in range(config.initial_users):
            thread = threading.Thread(target=worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # 启动渐进增加线程
        ramp_up_thread = threading.Thread(target=ramp_up_users)
        ramp_up_thread.start()
        
        # 等待测试完成
        ramp_up_thread.join()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        # 计算性能指标
        metrics = self._calculate_metrics(
            total_requests, successful_requests, failed_requests,
            total_time, all_response_times
        )
        
        self.is_running = False
        return metrics
    
    def execute_stress_test(self, test_request: Callable, max_users: int, 
                          duration: int = 300) -> List[PerformanceMetrics]:
        """执行压力测试"""
        results = []
        user_counts = [10, 25, 50, 75, 100, 150, 200]
        
        if max_users in user_counts:
            user_counts = [uc for uc in user_counts if uc <= max_users]
        else:
            user_counts.append(max_users)
            user_counts.sort()
        
        for users in user_counts:
            print(f"\n执行压力测试 - 用户数: {users}")
            
            config = LoadTestConfig(
                initial_users=users,
                max_users=users,
                step_users=0,
                step_duration=0,
                test_duration=duration,
                ramp_up_time=30,
                think_time=0
            )
            
            metrics = self.execute_load_test(test_request, config)
            results.append(metrics)
            
            print(f"平均响应时间: {metrics.avg_response_time:.2f}s")
            print(f"TPS: {metrics.requests_per_second:.2f}")
            print(f"错误率: {metrics.error_rate:.2f}%")
        
        return results
    
    def execute_spike_test(self, test_request: Callable, normal_users: int,
                          spike_users: int, spike_duration: int = 60) -> PerformanceMetrics:
        """执行峰值测试"""
        self.is_running = True
        self.stop_event.clear()
        
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        def worker(user_id: int, is_spike: bool = False):
            nonlocal successful_requests, failed_requests
            
            while not self.stop_event.is_set():
                request_start = time.time()
                
                try:
                    response = test_request()
                    request_time = time.time() - request_start
                    
                    all_response_times.append(request_time)
                    successful_requests += 1
                    
                except Exception as e:
                    failed_requests += 1
                
                time.sleep(0.1)  # 固定间隔
        
        # 启动正常用户
        normal_threads = []
        for i in range(normal_users):
            thread = threading.Thread(target=worker, args=(i, False))
            thread.start()
            normal_threads.append(thread)
        
        # 正常运行阶段
        time.sleep(60)
        
        # 峰值阶段
        print("开始峰值测试...")
        spike_threads = []
        for i in range(spike_users):
            thread = threading.Thread(target=worker, args=(i + normal_users, True))
            thread.start()
            spike_threads.append(thread)
        
        time.sleep(spike_duration)
        
        # 停止峰值用户
        self.stop_event.set()
        
        for thread in spike_threads:
            thread.join()
        
        # 继续正常用户
        self.stop_event.clear()
        time.sleep(60)
        
        # 停止所有用户
        self.stop_event.set()
        
        for thread in normal_threads:
            thread.join()
        
        total_time = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        metrics = self._calculate_metrics(
            total_requests, successful_requests, failed_requests,
            total_time, all_response_times
        )
        
        self.is_running = False
        return metrics
    
    def execute_endurance_test(self, test_request: Callable, users: int,
                             duration: int = 3600) -> PerformanceMetrics:
        """执行持久测试"""
        print(f"开始持久测试 - 用户数: {users}, 持续时间: {duration}秒")
        
        config = LoadTestConfig(
            initial_users=users,
            max_users=users,
            step_users=0,
            step_duration=0,
            test_duration=duration,
            ramp_up_time=60,
            think_time=1.0
        )
        
        return self.execute_load_test(test_request, config)
    
    def _calculate_metrics(self, total_requests: int, successful_requests: int,
                          failed_requests: int, total_time: float,
                          response_times: List[float]) -> PerformanceMetrics:
        """计算性能指标"""
        if not response_times:
            return PerformanceMetrics(
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                total_time=total_time,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                median_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                error_rate=100 if total_requests > 0 else 0,
                response_times=[]
            )
        
        sorted_times = sorted(response_times)
        
        return PerformanceMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_time=total_time,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=np.percentile(response_times, 95),
            p99_response_time=np.percentile(response_times, 99),
            requests_per_second=successful_requests / total_time if total_time > 0 else 0,
            error_rate=(failed_requests / total_requests * 100) if total_requests > 0 else 0,
            response_times=response_times
        )
    
    def stop_test(self):
        """停止测试"""
        self.stop_event.set()
    
    def generate_performance_report(self, metrics: PerformanceMetrics, 
                                  output_path: str = "performance_report.html"):
        """生成性能报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>性能测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>性能测试报告</h1>
    
    <div class="metrics">
        <div class="metric">
            <h3>总请求数</h3>
            <p>{metrics.total_requests}</p>
        </div>
        <div class="metric">
            <h3>成功请求</h3>
            <p>{metrics.successful_requests}</p>
        </div>
        <div class="metric">
            <h3>失败请求</h3>
            <p>{metrics.failed_requests}</p>
        </div>
        <div class="metric">
            <h3>TPS</h3>
            <p>{metrics.requests_per_second:.2f}</p>
        </div>
        <div class="metric">
            <h3>平均响应时间</h3>
            <p>{metrics.avg_response_time:.2f}s</p>
        </div>
        <div class="metric">
            <h3>95%响应时间</h3>
            <p>{metrics.p95_response_time:.2f}s</p>
        </div>
        <div class="metric">
            <h3>错误率</h3>
            <p>{metrics.error_rate:.2f}%</p>
        </div>
    </div>
    
    <div class="chart">
        <canvas id="responseTimeChart" width="400" height="200"></canvas>
    </div>
    
    <script>
        // 响应时间分布图
        const ctx = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(ctx, {{
            type: 'histogram',
            data: {{
                labels: {metrics.response_times},
                datasets: [{{
                    label: '响应时间分布',
                    data: {metrics.response_times},
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '响应时间分布'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"性能报告已生成: {output_path}")

# 使用示例
def mock_api_request():
    """模拟API请求"""
    time.sleep(0.1)  # 模拟网络延迟
    return {"status": "success"}

engine = PerformanceTestEngine()

# 负载测试配置
config = LoadTestConfig(
    initial_users=10,
    max_users=100,
    step_users=10,
    step_duration=30,
    test_duration=300,
    ramp_up_time=60,
    think_time=0.5
)

# 执行负载测试
print("开始负载测试...")
metrics = engine.execute_load_test(mock_api_request, config)

print(f"\n负载测试结果:")
print(f"总请求数: {metrics.total_requests}")
print(f"成功请求: {metrics.successful_requests}")
print(f"失败请求: {metrics.failed_requests}")
print(f"TPS: {metrics.requests_per_second:.2f}")
print(f"平均响应时间: {metrics.avg_response_time:.2f}s")
print(f"95%响应时间: {metrics.p95_response_time:.2f}s")
print(f"错误率: {metrics.error_rate:.2f}%")

# 生成性能报告
engine.generate_performance_report(metrics)
```

## 参考资源

### API测试框架
- [Requests Library](https://docs.python-requests.org/)
- [REST Assured](https://rest-assured.io/)
- [Postman](https://www.postman.com/)
- [Insomnia](https://insomnia.rest/)

### 性能测试工具
- [JMeter](https://jmeter.apache.org/)
- [Gatling](https://gatling.io/)
- [K6](https://k6.io/)
- [Locust](https://locust.io/)

### 安全测试工具
- [OWASP ZAP](https://www.zaproxy.org/)
- [Burp Suite](https://portswigger.net/burp)
- [SQLMap](http://sqlmap.org/)
- [Nikto](https://github.com/sullo/nikto)

### 测试数据管理
- [Faker](https://faker.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [TestContainers](https://www.testcontainers.org/)
- [WireMock](http://wiremock.org/)
