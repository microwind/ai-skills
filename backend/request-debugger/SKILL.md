---
name: HTTP请求调试器
description: "当调试HTTP请求时，分析请求/响应对，排查API问题，理解请求流程。调试请求并分析响应，解决网络通信问题。"
license: MIT
---

# HTTP请求调试器技能

## 概述
HTTP请求可能静默失败或表现异常。调试请求以理解实际发送和接收的内容，而不是你以为发送和接收的内容。大多数集成问题都是请求/响应不匹配，只有通过适当调试才能发现。

**核心原则**: 不要猜测 - 调试。查看实际发送和接收的内容，而不是你以为发送和接收的内容。

## 何时使用

**始终:**
- API没有按预期响应
- 请求神秘失败
- 头部没有正确发送
- 身份验证失败
- 响应格式不正确
- 网络连接问题

**触发短语:**
- "API调用失败了"
- "为什么请求不工作？"
- "检查这个HTTP请求"
- "调试API问题"
- "请求头部有问题"
- "响应格式错误"

## HTTP请求调试功能

### 请求分析
- 请求方法验证
- URL参数检查
- 请求头部分析
- 请求体内容检查
- 认证信息验证

### 响应分析
- 状态码分析
- 响应头检查
- 响应体解析
- 错误信息提取
- 性能指标分析

### 网络诊断
- 连接状态检查
- 超时问题诊断
- SSL/TLS验证
- 代理配置检查
- 防火墙问题排查

## 常见HTTP请求问题

### 请求头缺失
```
问题:
必要的请求头部没有发送

后果:
- 身份验证失败
- 服务器拒绝请求
- 内容类型错误
- 缓存问题

解决方案:
- 检查请求头设置
- 验证认证头部
- 确认内容类型
- 添加必要头部
```

### 请求体格式错误
```
问题:
请求体格式不正确或编码错误

后果:
- 服务器解析失败
- 4xx错误响应
- 数据丢失
- 集成失败

解决方案:
- 验证JSON格式
- 检查字符编码
- 确认内容长度
- 测试请求体
```

### 网络连接问题
```
问题:
网络连接不稳定或被阻止

后果:
- 请求超时
- 连接被拒绝
- DNS解析失败
- 代理问题

解决方案:
- 检查网络连接
- 验证DNS设置
- 测试代理配置
- 检查防火墙规则
```

## 请求调试策略

### 分层调试方法
```
网络层:
- 检查DNS解析
- 验证端口连通性
- 测试SSL连接
- 分析网络延迟

应用层:
- 验证HTTP方法
- 检查URL格式
- 分析请求头部
- 验证请求体

业务层:
- 检查认证信息
- 验证权限设置
- 分析业务逻辑
- 测试数据格式
```

### 调试工具使用
```
浏览器开发者工具:
- Network面板监控
- 请求/响应查看
- 性能分析
- 错误诊断

命令行工具:
- curl命令测试
- wget下载测试
- telnet连接测试
- ping网络测试

专业工具:
- Postman接口测试
- Fiddler抓包分析
- Wireshark网络分析
- Charles代理调试
```

## 代码实现示例

### Python请求调试器
```python
import requests
import json
import time
from typing import Dict, Any, Optional
import logging
from urllib.parse import urlparse

class HTTPRequestDebugger:
    """HTTP请求调试器"""
    
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.session = requests.Session()
        
        # 设置默认超时
        self.session.timeout = 30
        
        # 启用详细日志
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def debug_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """调试HTTP请求"""
        debug_info = {
            'request': {},
            'response': {},
            'timing': {},
            'errors': []
        }
        
        try:
            # 记录请求开始时间
            start_time = time.time()
            
            # 准备请求信息
            debug_info['request'] = {
                'method': method.upper(),
                'url': url,
                'headers': dict(kwargs.get('headers', {})),
                'params': kwargs.get('params', {}),
                'data': kwargs.get('data', {}),
                'json': kwargs.get('json', {}),
                'files': kwargs.get('files', {}),
                'timeout': kwargs.get('timeout', self.session.timeout)
            }
            
            # 记录请求详情
            self.logger.info(f"发送{method.upper()}请求到: {url}")
            self.logger.debug(f"请求头部: {debug_info['request']['headers']}")
            self.logger.debug(f"请求参数: {debug_info['request']['params']}")
            
            if debug_info['request']['json']:
                self.logger.debug(f"JSON数据: {json.dumps(debug_info['request']['json'], indent=2, ensure_ascii=False)}")
            
            # 执行请求
            response = self.session.request(method, url, **kwargs)
            
            # 记录响应时间
            end_time = time.time()
            debug_info['timing'] = {
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time
            }
            
            # 记录响应信息
            debug_info['response'] = {
                'status_code': response.status_code,
                'status_text': response.reason,
                'headers': dict(response.headers),
                'content_length': len(response.content),
                'encoding': response.encoding,
                'cookies': dict(response.cookies),
                'url': response.url,
                'history': response.history
            }
            
            # 尝试解析响应体
            try:
                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' in content_type:
                    debug_info['response']['body'] = response.json()
                elif 'text/' in content_type:
                    debug_info['response']['body'] = response.text
                else:
                    debug_info['response']['body'] = f"<二进制数据，长度: {len(response.content)}>"
            except Exception as e:
                debug_info['response']['body'] = f"<解析失败: {str(e)}>"
                debug_info['errors'].append(f"响应体解析失败: {str(e)}")
            
            # 记录响应详情
            self.logger.info(f"收到响应: {response.status_code} {response.reason}")
            self.logger.debug(f"响应头部: {debug_info['response']['headers']}")
            self.logger.debug(f"响应时间: {debug_info['timing']['duration']:.3f}秒")
            
            # 检查常见问题
            self._check_common_issues(debug_info)
            
            return debug_info
            
        except requests.exceptions.Timeout as e:
            debug_info['errors'].append(f"请求超时: {str(e)}")
            self.logger.error(f"请求超时: {url}")
        except requests.exceptions.ConnectionError as e:
            debug_info['errors'].append(f"连接错误: {str(e)}")
            self.logger.error(f"连接错误: {url} - {str(e)}")
        except requests.exceptions.RequestException as e:
            debug_info['errors'].append(f"请求异常: {str(e)}")
            self.logger.error(f"请求异常: {str(e)}")
        except Exception as e:
            debug_info['errors'].append(f"未知错误: {str(e)}")
            self.logger.error(f"未知错误: {str(e)}")
        
        return debug_info
    
    def _check_common_issues(self, debug_info: Dict[str, Any]):
        """检查常见问题"""
        response = debug_info.get('response', {})
        request = debug_info.get('request', {})
        
        # 检查状态码
        status_code = response.get('status_code')
        if status_code >= 400:
            if status_code == 401:
                debug_info['errors'].append("身份验证失败 - 检查认证头部")
            elif status_code == 403:
                debug_info['errors'].append("权限不足 - 检查用户权限")
            elif status_code == 404:
                debug_info['errors'].append("资源不存在 - 检查URL路径")
            elif status_code == 422:
                debug_info['errors'].append("请求参数验证失败 - 检查请求体格式")
            elif status_code >= 500:
                debug_info['errors'].append("服务器内部错误 - 检查服务器状态")
        
        # 检查响应时间
        duration = debug_info.get('timing', {}).get('duration', 0)
        if duration > 10:
            debug_info['errors'].append(f"响应时间过长: {duration:.3f}秒")
        
        # 检查内容类型
        content_type = response.get('headers', {}).get('content-type', '')
        if not content_type:
            debug_info['errors'].append("响应缺少Content-Type头部")
        
        # 检查请求头部
        headers = request.get('headers', {})
        if 'user-agent' not in headers:
            debug_info['errors'].append("请求缺少User-Agent头部")
    
    def compare_requests(self, debug_info1: Dict, debug_info2: Dict) -> Dict[str, Any]:
        """比较两个请求的差异"""
        comparison = {
            'request_differences': [],
            'response_differences': [],
            'timing_differences': [],
            'recommendations': []
        }
        
        # 比较请求
        req1 = debug_info1.get('request', {})
        req2 = debug_info2.get('request', {})
        
        if req1.get('method') != req2.get('method'):
            comparison['request_differences'].append({
                'field': 'method',
                'value1': req1.get('method'),
                'value2': req2.get('method')
            })
        
        if req1.get('url') != req2.get('url'):
            comparison['request_differences'].append({
                'field': 'url',
                'value1': req1.get('url'),
                'value2': req2.get('url')
            })
        
        # 比较响应
        resp1 = debug_info1.get('response', {})
        resp2 = debug_info2.get('response', {})
        
        if resp1.get('status_code') != resp2.get('status_code'):
            comparison['response_differences'].append({
                'field': 'status_code',
                'value1': resp1.get('status_code'),
                'value2': resp2.get('status_code')
            })
        
        # 比较时间
        time1 = debug_info1.get('timing', {})
        time2 = debug_info2.get('timing', {})
        
        if abs(time1.get('duration', 0) - time2.get('duration', 0)) > 1:
            comparison['timing_differences'].append({
                'field': 'duration',
                'value1': time1.get('duration'),
                'value2': time2.get('duration')
            })
        
        return comparison
    
    def test_endpoint(self, url: str, methods: list = None) -> Dict[str, Any]:
        """测试端点的不同HTTP方法"""
        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        
        results = {}
        
        for method in methods:
            try:
                debug_info = self.debug_request(method, url)
                results[method] = debug_info
            except Exception as e:
                results[method] = {'error': str(e)}
        
        return results
    
    def generate_curl_command(self, debug_info: Dict[str, Any]) -> str:
        """生成curl命令"""
        request = debug_info.get('request', {})
        method = request.get('method', 'GET')
        url = request.get('url', '')
        headers = request.get('headers', {})
        data = request.get('json', {}) or request.get('data', {})
        
        curl_parts = ['curl', '-X', method]
        
        # 添加头部
        for key, value in headers.items():
            curl_parts.extend(['-H', f'{key}: {value}'])
        
        # 添加数据
        if data:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            curl_parts.extend(['-d', data])
        
        # 添加URL
        curl_parts.append(url)
        
        return ' '.join(f'"{part}"' if ' ' in str(part) else str(part) for part in curl_parts)

# 使用示例
debugger = HTTPRequestDebugger()

# 调试GET请求
get_result = debugger.debug_request(
    'GET',
    'https://httpbin.org/get',
    params={'param1': 'value1'},
    headers={'User-Agent': 'HTTPDebugger/1.0'}
)

print("GET请求调试结果:")
print(json.dumps(get_result, indent=2, ensure_ascii=False))

# 调试POST请求
post_result = debugger.debug_request(
    'POST',
    'https://httpbin.org/post',
    json={'key': 'value'},
    headers={'Content-Type': 'application/json'}
)

print("\nPOST请求调试结果:")
print(json.dumps(post_result, indent=2, ensure_ascii=False))

# 生成curl命令
curl_command = debugger.generate_curl_command(post_result)
print(f"\n等效curl命令:\n{curl_command}")

# 测试端点
endpoint_test = debugger.test_endpoint('https://httpbin.org/status/200')
print(f"\n端点测试结果: {json.dumps(endpoint_test, indent=2, ensure_ascii=False)}")
```

### JavaScript请求调试器
```javascript
class HTTPRequestDebugger {
    constructor(options = {}) {
        this.defaultHeaders = options.headers || {};
        this.timeout = options.timeout || 30000;
        this.logLevel = options.logLevel || 'info';
    }
    
    async debugRequest(method, url, options = {}) {
        const debugInfo = {
            request: {},
            response: {},
            timing: {},
            errors: []
        };
        
        try {
            const startTime = performance.now();
            
            // 准备请求信息
            debugInfo.request = {
                method: method.toUpperCase(),
                url: url,
                headers: { ...this.defaultHeaders, ...options.headers },
                params: options.params || {},
                body: options.body || null,
                timeout: options.timeout || this.timeout
            };
            
            // 构建完整URL
            const fullUrl = this.buildUrl(url, debugInfo.request.params);
            
            // 记录请求信息
            this.log(`发送${method.toUpperCase()}请求到: ${fullUrl}`);
            this.log('请求头部:', debugInfo.request.headers);
            
            if (debugInfo.request.body) {
                this.log('请求体:', debugInfo.request.body);
            }
            
            // 执行请求
            const response = await fetch(fullUrl, {
                method: method.toUpperCase(),
                headers: debugInfo.request.headers,
                body: debugInfo.request.body,
                signal: AbortSignal.timeout(debugInfo.request.timeout)
            });
            
            const endTime = performance.now();
            
            // 记录响应信息
            debugInfo.timing = {
                startTime: startTime,
                endTime: endTime,
                duration: endTime - startTime
            };
            
            debugInfo.response = {
                status: response.status,
                statusText: response.statusText,
                headers: this.headersToObject(response.headers),
                url: response.url,
                redirected: response.redirected,
                type: response.type
            };
            
            // 解析响应体
            try {
                const contentType = response.headers.get('content-type') || '';
                if (contentType.includes('application/json')) {
                    debugInfo.response.body = await response.json();
                } else if (contentType.includes('text/')) {
                    debugInfo.response.body = await response.text();
                } else {
                    const blob = await response.blob();
                    debugInfo.response.body = `<二进制数据，大小: ${blob.size}字节>`;
                }
            } catch (error) {
                debugInfo.response.body = `<解析失败: ${error.message}>`;
                debugInfo.errors.push(`响应体解析失败: ${error.message}`);
            }
            
            // 记录响应信息
            this.log(`收到响应: ${response.status} ${response.statusText}`);
            this.log('响应头部:', debugInfo.response.headers);
            this.log(`响应时间: ${debugInfo.timing.duration.toFixed(3)}毫秒`);
            
            // 检查常见问题
            this.checkCommonIssues(debugInfo);
            
            return debugInfo;
            
        } catch (error) {
            debugInfo.errors.push(`请求失败: ${error.message}`);
            this.error(`请求失败: ${error.message}`);
            return debugInfo;
        }
    }
    
    buildUrl(url, params) {
        const urlObj = new URL(url);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                urlObj.searchParams.append(key, params[key]);
            }
        });
        return urlObj.toString();
    }
    
    headersToObject(headers) {
        const obj = {};
        headers.forEach((value, key) => {
            obj[key] = value;
        });
        return obj;
    }
    
    checkCommonIssues(debugInfo) {
        const response = debugInfo.response || {};
        const request = debugInfo.request || {};
        
        // 检查状态码
        if (response.status >= 400) {
            if (response.status === 401) {
                debugInfo.errors.push("身份验证失败 - 检查认证头部");
            } else if (response.status === 403) {
                debugInfo.errors.push("权限不足 - 检查用户权限");
            } else if (response.status === 404) {
                debugInfo.errors.push("资源不存在 - 检查URL路径");
            } else if (response.status === 422) {
                debugInfo.errors.push("请求参数验证失败 - 检查请求体格式");
            } else if (response.status >= 500) {
                debugInfo.errors.push("服务器内部错误 - 检查服务器状态");
            }
        }
        
        // 检查响应时间
        if (debugInfo.timing && debugInfo.timing.duration > 10000) {
            debugInfo.errors.push(`响应时间过长: ${debugInfo.timing.duration.toFixed(3)}毫秒`);
        }
        
        // 检查请求头部
        if (!request.headers || !request.headers['User-Agent']) {
            debugInfo.errors.push("请求缺少User-Agent头部");
        }
    }
    
    async testEndpoint(url, methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']) {
        const results = {};
        
        for (const method of methods) {
            try {
                const debugInfo = await this.debugRequest(method, url);
                results[method] = debugInfo;
            } catch (error) {
                results[method] = { error: error.message };
            }
        }
        
        return results;
    }
    
    generateCurlCommand(debugInfo) {
        const request = debugInfo.request || {};
        const method = request.method || 'GET';
        const url = request.url || '';
        const headers = request.headers || {};
        const body = request.body;
        
        let curl = `curl -X ${method}`;
        
        // 添加头部
        Object.keys(headers).forEach(key => {
            curl += ` -H "${key}: ${headers[key]}"`;
        });
        
        // 添加数据
        if (body) {
            const data = typeof body === 'string' ? body : JSON.stringify(body);
            curl += ` -d '${data}'`;
        }
        
        // 添加URL
        curl += ` ${url}`;
        
        return curl;
    }
    
    log(...args) {
        if (this.logLevel === 'debug' || this.logLevel === 'info') {
            console.log(...args);
        }
    }
    
    error(...args) {
        console.error(...args);
    }
}

// 使用示例
const debugger = new HTTPRequestDebugger({
    headers: {
        'User-Agent': 'HTTPDebugger/1.0'
    }
});

// 调试请求
async function example() {
    try {
        // GET请求
        const getResult = await debugger.debugRequest('GET', 'https://httpbin.org/get', {
            params: { param1: 'value1' }
        });
        
        console.log('GET请求调试结果:', getResult);
        
        // POST请求
        const postResult = await debugger.debugRequest('POST', 'https://httpbin.org/post', {
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'value' })
        });
        
        console.log('POST请求调试结果:', postResult);
        
        // 生成curl命令
        const curlCommand = debugger.generateCurlCommand(postResult);
        console.log('等效curl命令:', curlCommand);
        
        // 测试端点
        const endpointTest = await debugger.testEndpoint('https://httpbin.org/status/200');
        console.log('端点测试结果:', endpointTest);
        
    } catch (error) {
        console.error('调试失败:', error);
    }
}

example();
```

## 调试最佳实践

### 系统化调试方法
1. **从简单开始**: 先测试基本连接
2. **逐步增加复杂性**: 添加头部、参数、数据
3. **记录每一步**: 详细记录请求和响应
4. **比较差异**: 对比工作和不工作的请求
5. **使用工具**: 利用专业调试工具

### 常见调试场景
1. **API集成问题**: 检查认证、格式、URL
2. **性能问题**: 分析响应时间、请求大小
3. **安全认证**: 验证令牌、签名、证书
4. **数据格式**: 检查JSON、XML、表单数据
5. **网络问题**: 测试连接、代理、防火墙

## 相关技能

- **api-validator** - API接口验证和设计
- **security-scanner** - 安全漏洞扫描
- **error-handling-logging** - 错误处理和日志记录
- **performance-profiler** - 性能分析和监控
