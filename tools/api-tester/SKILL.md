---
name: API测试器
description: "当测试API、发送HTTP请求、调试响应或验证端点时，在集成前测试HTTP API并验证响应。"
license: MIT
---

# API测试器技能

## 概述
API是系统之间的连接器。损坏的API会破坏应用程序。在集成前彻底测试端点。

**核心原则**: API契约必须在部署前验证。

## 何时使用

**始终:**
- 测试API端点
- 验证响应
- 检查状态码
- 验证头部
- 性能测试
- 安全测试

**触发短语:**
- "测试这个API"
- "API响应验证"
- "HTTP请求测试"
- "API端点检查"
- "API性能测试"
- "API调试"

## API测试功能

### 请求测试
- HTTP方法支持
- 请求头配置
- 请求体构建
- 认证处理
- 参数传递

### 响应验证
- 状态码检查
- 响应头验证
- 响应体解析
- JSON Schema验证
- 响应时间测量

### 性能测试
- 负载测试
- 压力测试
- 并发测试
- 响应时间分析
- 吞吐量测试

## 常见API问题

### 状态码错误
```
问题:
API返回不正确的HTTP状态码

错误示例:
POST /api/users → 200 OK (应该是 201 Created)
GET /api/users/999 → 200 OK (应该是 404 Not Found)
PUT /api/users/999 → 200 OK (应该是 404 Not Found)

解决方案:
- 201: 资源创建成功
- 400: 请求参数错误
- 401: 未认证
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误
```

### 响应格式不一致
```
问题:
API响应格式不统一

错误示例:
成功响应:
{
  "data": {"id": 1, "name": "John"}
}

错误响应:
{
  "error": "User not found",
  "code": 404
}

解决方案:
统一响应格式:
{
  "success": true,
  "data": {...},
  "message": "操作成功",
  "timestamp": "2023-01-01T10:00:00Z"
}
```

### 认证问题
```
问题:
API认证配置错误

错误示例:
- 缺少认证头
- Token过期处理不当
- 权限检查缺失

解决方案:
1. 实现标准的认证机制
2. 正确处理Token过期
3. 细粒度权限控制
4. 安全的Token生成
```

## 代码实现示例

### API测试器
```python
import requests
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
import statistics
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import jwt

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class AuthType(Enum):
    NONE = "none"
    BASIC = "basic"
    DIGEST = "digest"
    BEARER = "bearer"
    API_KEY = "api_key"

@dataclass
class APIRequest:
    """API请求"""
    method: HTTPMethod
    url: str
    headers: Dict[str, str] = None
    params: Dict[str, Any] = None
    data: Dict[str, Any] = None
    json_data: Dict[str, Any] = None
    auth_type: AuthType = AuthType.NONE
    auth_credentials: Dict[str, str] = None
    timeout: int = 30

@dataclass
class APIResponse:
    """API响应"""
    status_code: int
    headers: Dict[str, str]
    content: str
    json_data: Optional[Dict[str, Any]] = None
    response_time: float = 0.0
    success: bool = False

@dataclass
class APITestResult:
    """API测试结果"""
    request: APIRequest
    response: APIResponse
    passed: bool
    errors: List[str]
    warnings: List[str]

@dataclass
class PerformanceTestResult:
    """性能测试结果"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    requests_per_second: float

class APITester:
    """API测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'APITester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def send_request(self, request: APIRequest) -> APIResponse:
        """发送API请求"""
        start_time = time.time()
        
        try:
            # 准备请求参数
            headers = {**self.default_headers, **(request.headers or {})}
            
            # 处理认证
            auth = self._prepare_auth(request.auth_type, request.auth_credentials)
            
            # 发送请求
            response = self.session.request(
                method=request.method.value,
                url=request.url,
                headers=headers,
                params=request.params,
                data=request.data,
                json=request.json_data,
                auth=auth,
                timeout=request.timeout
            )
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 解析响应
            json_data = None
            try:
                json_data = response.json()
            except:
                pass
            
            # 判断成功状态
            success = 200 <= response.status_code < 300
            
            return APIResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.text,
                json_data=json_data,
                response_time=response_time,
                success=success
            )
            
        except requests.exceptions.Timeout:
            return APIResponse(
                status_code=0,
                headers={},
                content="Request timeout",
                response_time=time.time() - start_time,
                success=False
            )
        except requests.exceptions.ConnectionError:
            return APIResponse(
                status_code=0,
                headers={},
                content="Connection error",
                response_time=time.time() - start_time,
                success=False
            )
        except Exception as e:
            return APIResponse(
                status_code=0,
                headers={},
                content=f"Request failed: {str(e)}",
                response_time=time.time() - start_time,
                success=False
            )
    
    def _prepare_auth(self, auth_type: AuthType, credentials: Dict[str, str]):
        """准备认证"""
        if auth_type == AuthType.BASIC:
            return HTTPBasicAuth(
                credentials['username'],
                credentials['password']
            )
        elif auth_type == AuthType.DIGEST:
            return HTTPDigestAuth(
                credentials['username'],
                credentials['password']
            )
        elif auth_type == AuthType.BEARER:
            # Bearer token会在headers中处理
            return None
        elif auth_type == AuthType.API_KEY:
            # API key会在headers中处理
            return None
        else:
            return None
    
    def test_api_endpoint(self, request: APIRequest, 
                        expected_status: int = 200,
                        expected_schema: Optional[Dict[str, Any]] = None) -> APITestResult:
        """测试API端点"""
        # 添加认证头
        headers = request.headers or {}
        if request.auth_type == AuthType.BEARER:
            headers['Authorization'] = f"Bearer {request.auth_credentials['token']}"
        elif request.auth_type == AuthType.API_KEY:
            key_name = request.auth_credentials.get('key_name', 'X-API-Key')
            headers[key_name] = request.auth_credentials['key']
        
        request.headers = headers
        
        # 发送请求
        response = self.send_request(request)
        
        # 验证结果
        errors = []
        warnings = []
        passed = True
        
        # 检查状态码
        if response.status_code != expected_status:
            errors.append(f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}")
            passed = False
        
        # 检查响应时间
        if response.response_time > 5.0:
            warnings.append(f"响应时间过长: {response.response_time:.2f}s")
        
        # 检查响应格式
        if expected_schema and response.json_data:
            schema_errors = self._validate_json_schema(response.json_data, expected_schema)
            if schema_errors:
                errors.extend(schema_errors)
                passed = False
        
        return APITestResult(
            request=request,
            response=response,
            passed=passed,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """验证JSON Schema"""
        errors = []
        
        # 简化的schema验证
        if 'required' in schema:
            for field in schema['required']:
                if field not in data:
                    errors.append(f"缺少必需字段: {field}")
        
        if 'properties' in schema:
            for field, field_schema in schema['properties'].items():
                if field in data:
                    value = data[field]
                    expected_type = field_schema.get('type')
                    
                    if expected_type == 'string' and not isinstance(value, str):
                        errors.append(f"字段 {field} 类型错误: 期望 string, 实际 {type(value).__name__}")
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        errors.append(f"字段 {field} 类型错误: 期望 number, 实际 {type(value).__name__}")
                    elif expected_type == 'boolean' and not isinstance(value, bool):
                        errors.append(f"字段 {field} 类型错误: 期望 boolean, 实际 {type(value).__name__}")
                    elif expected_type == 'array' and not isinstance(value, list):
                        errors.append(f"字段 {field} 类型错误: 期望 array, 实际 {type(value).__name__}")
                    elif expected_type == 'object' and not isinstance(value, dict):
                        errors.append(f"字段 {field} 类型错误: 期望 object, 实际 {type(value).__name__}")
        
        return errors
    
    def performance_test(self, request: APIRequest, 
                        concurrent_users: int = 10,
                        total_requests: int = 100) -> PerformanceTestResult:
        """性能测试"""
        results = []
        
        def send_single_request():
            return self.send_request(request)
        
        # 并发发送请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交所有请求
            futures = [executor.submit(send_single_request) for _ in range(total_requests)]
            
            # 收集结果
            for future in concurrent.futures.as_completed(futures):
                try:
                    response = future.result()
                    results.append(response)
                except Exception as e:
                    print(f"Request failed: {str(e)}")
        
        # 计算统计数据
        successful_requests = [r for r in results if r.success]
        failed_requests = len(results) - len(successful_requests)
        
        response_times = [r.response_time for r in successful_requests]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        # 计算总执行时间
        total_time = max(r.response_time for r in results) if results else 0
        requests_per_second = len(successful_requests) / total_time if total_time > 0 else 0
        
        return PerformanceTestResult(
            total_requests=total_requests,
            successful_requests=len(successful_requests),
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            requests_per_second=requests_per_second
        )
    
    def generate_test_report(self, test_results: List[APITestResult]) -> str:
        """生成测试报告"""
        if not test_results:
            return "没有测试结果"
        
        report = ["=== API测试报告 ===\n"]
        
        # 统计信息
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.passed])
        failed_tests = total_tests - passed_tests
        
        report.append("=== 测试统计 ===")
        report.append(f"总测试数: {total_tests}")
        report.append(f"通过: {passed_tests}")
        report.append(f"失败: {failed_tests}")
        report.append(f"成功率: {passed_tests/total_tests*100:.1f}%\n")
        
        # 详细结果
        report.append("=== 详细结果 ===")
        for i, result in enumerate(test_results, 1):
            status = "✅ 通过" if result.passed else "❌ 失败"
            report.append(f"{i}. {result.request.method.value} {result.request.url} - {status}")
            
            if result.response:
                report.append(f"   状态码: {result.response.status_code}")
                report.append(f"   响应时间: {result.response.response_time:.3f}s")
            
            if result.errors:
                report.append("   错误:")
                for error in result.errors:
                    report.append(f"     - {error}")
            
            if result.warnings:
                report.append("   警告:")
                for warning in result.warnings:
                    report.append(f"     - {warning}")
            
            report.append("")
        
        return '\n'.join(report)
    
    def generate_performance_report(self, result: PerformanceTestResult) -> str:
        """生成性能测试报告"""
        report = ["=== 性能测试报告 ===\n"]
        
        report.append("=== 测试配置 ===")
        report.append(f"总请求数: {result.total_requests}")
        report.append(f"并发用户数: {result.total_requests}\n")
        
        report.append("=== 测试结果 ===")
        report.append(f"成功请求: {result.successful_requests}")
        report.append(f"失败请求: {result.failed_requests}")
        report.append(f"成功率: {result.successful_requests/result.total_requests*100:.1f}%\n")
        
        report.append("=== 响应时间 ===")
        report.append(f"平均响应时间: {result.avg_response_time:.3f}s")
        report.append(f"最小响应时间: {result.min_response_time:.3f}s")
        report.append(f"最大响应时间: {result.max_response_time:.3f}s")
        report.append(f"95%响应时间: {result.p95_response_time:.3f}s\n")
        
        report.append("=== 吞吐量 ===")
        report.append(f"每秒请求数: {result.requests_per_second:.2f}")
        
        return '\n'.join(report)

# 使用示例
def main():
    tester = APITester()
    
    # 创建API请求
    request = APIRequest(
        method=HTTPMethod.GET,
        url="https://jsonplaceholder.typicode.com/posts/1",
        headers={"Accept": "application/json"}
    )
    
    # 测试API端点
    result = tester.test_api_endpoint(request, expected_status=200)
    
    # 生成报告
    report = tester.generate_test_report([result])
    print(report)
    
    # 性能测试
    perf_result = tester.performance_test(request, concurrent_users=5, total_requests=20)
    perf_report = tester.generate_performance_report(perf_result)
    print("\n" + perf_report)

if __name__ == "__main__":
    main()
```

### API套件测试
```python
import yaml
from typing import List, Dict, Any
import json

class APITestSuite:
    """API测试套件"""
    
    def __init__(self):
        self.tester = APITester()
        self.test_cases = []
    
    def load_test_suite(self, suite_file: str) -> bool:
        """加载测试套件"""
        try:
            with open(suite_file, 'r', encoding='utf-8') as f:
                if suite_file.endswith('.yaml') or suite_file.endswith('.yml'):
                    suite_data = yaml.safe_load(f)
                else:
                    suite_data = json.load(f)
            
            # 解析测试用例
            for test_case in suite_data.get('test_cases', []):
                self.test_cases.append(self._parse_test_case(test_case))
            
            return True
        
        except Exception as e:
            print(f"加载测试套件失败: {str(e)}")
            return False
    
    def _parse_test_case(self, test_case_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析测试用例"""
        return {
            'name': test_case_data.get('name', ''),
            'description': test_case_data.get('description', ''),
            'request': APIRequest(
                method=HTTPMethod(test_case_data['request']['method']),
                url=test_case_data['request']['url'],
                headers=test_case_data['request'].get('headers'),
                params=test_case_data['request'].get('params'),
                data=test_case_data['request'].get('data'),
                json_data=test_case_data['request'].get('json'),
                auth_type=AuthType(test_case_data['request'].get('auth_type', 'none')),
                auth_credentials=test_case_data['request'].get('auth_credentials'),
                timeout=test_case_data['request'].get('timeout', 30)
            ),
            'expected_status': test_case_data.get('expected_status', 200),
            'expected_schema': test_case_data.get('expected_schema'),
            'setup': test_case_data.get('setup'),
            'teardown': test_case_data.get('teardown')
        }
    
    def run_test_suite(self) -> List[APITestResult]:
        """运行测试套件"""
        results = []
        
        for test_case in self.test_cases:
            print(f"运行测试: {test_case['name']}")
            
            # 执行setup
            if test_case.get('setup'):
                self._execute_setup(test_case['setup'])
            
            # 运行测试
            result = self.tester.test_api_endpoint(
                test_case['request'],
                test_case['expected_status'],
                test_case['expected_schema']
            )
            result.test_name = test_case['name']
            results.append(result)
            
            # 执行teardown
            if test_case.get('teardown'):
                self._execute_teardown(test_case['teardown'])
        
        return results
    
    def _execute_setup(self, setup_config: Dict[str, Any]):
        """执行setup"""
        # 这里可以实现setup逻辑，比如创建测试数据
        pass
    
    def _execute_teardown(self, teardown_config: Dict[str, Any]):
        """执行teardown"""
        # 这里可以实现teardown逻辑，比如清理测试数据
        pass
    
    def generate_suite_report(self, results: List[APITestResult]) -> str:
        """生成套件报告"""
        if not results:
            return "没有测试结果"
        
        report = ["=== API测试套件报告 ===\n"]
        
        # 统计信息
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = total_tests - passed_tests
        
        report.append("=== 套件统计 ===")
        report.append(f"总测试数: {total_tests}")
        report.append(f"通过: {passed_tests}")
        report.append(f"失败: {failed_tests}")
        report.append(f"成功率: {passed_tests/total_tests*100:.1f}%\n")
        
        # 按测试名称分组
        report.append("=== 测试结果 ===")
        for result in results:
            test_name = getattr(result, 'test_name', 'Unknown Test')
            status = "✅ 通过" if result.passed else "❌ 失败"
            
            report.append(f"测试: {test_name}")
            report.append(f"状态: {status}")
            report.append(f"请求: {result.request.method.value} {result.request.url}")
            report.append(f"状态码: {result.response.status_code}")
            report.append(f"响应时间: {result.response.response_time:.3f}s")
            
            if result.errors:
                report.append("错误:")
                for error in result.errors:
                    report.append(f"  - {error}")
            
            if result.warnings:
                report.append("警告:")
                for warning in result.warnings:
                    report.append(f"  - {warning}")
            
            report.append("")
        
        return '\n'.join(report)

# 使用示例
def main():
    suite = APITestSuite()
    
    # 加载测试套件
    if suite.load_test_suite("api_test_suite.yaml"):
        # 运行测试套件
        results = suite.run_test_suite()
        
        # 生成报告
        report = suite.generate_suite_report(results)
        print(report)

if __name__ == "__main__":
    main()
```

## API测试最佳实践

### 测试策略
1. **分层测试**: 单元测试、集成测试、端到端测试
2. **覆盖全面**: 测试正常流程和异常情况
3. **数据驱动**: 使用不同的测试数据
4. **环境隔离**: 测试环境与生产环境分离

### 测试用例设计
1. **正向测试**: 验证正常功能
2. **负向测试**: 验证错误处理
3. **边界测试**: 测试极限情况
4. **安全测试**: 验证安全性

### 性能测试
1. **基准测试**: 建立性能基准
2. **负载测试**: 测试预期负载
3. **压力测试**: 测试极限负载
4. **稳定性测试**: 长时间运行测试

## 相关技能

- **api-validator** - API验证
- **http-debugger** - HTTP调试
- **performance-testing** - 性能测试
- **security-testing** - 安全测试
