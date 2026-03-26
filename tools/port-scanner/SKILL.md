---
name: 端口扫描器
description: "当扫描网络端口、检测服务状态、进行安全审计、网络发现或漏洞评估时，提供全面的端口扫描和网络安全检测解决方案。"
license: MIT
---

# 端口扫描器技能

## 概述
端口扫描器是网络安全和网络管理的重要工具，用于检测目标主机上开放的端口、运行的服务、潜在的安全漏洞和网络拓扑结构。它帮助网络管理员和安全专家了解网络状态、识别安全风险和优化网络配置。

**核心原则**: 全面扫描、准确检测、安全合规、高效执行、结果分析。

## 何时使用

**始终:**
- 网络安全审计
- 服务发现和映射
- 漏洞评估和检测
- 网络拓扑发现
- 防火墙规则验证
- 服务器配置检查
- 网络监控和告警
- 渗透测试

**触发短语:**
- "端口扫描工具"
- "网络服务发现"
- "安全漏洞扫描"
- "网络拓扑映射"
- "防火墙规则测试"
- "服务器端口检查"
- "网络安全审计"
- "主机发现扫描"

## 端口扫描技术

### 1. TCP扫描
- **TCP Connect**: 完整的三次握手连接
- **SYN扫描**: 半开扫描，隐蔽性好
- **ACK扫描**: 检测防火墙规则
- **Window扫描**: 基于窗口大小检测
- **FIN扫描**: FIN包探测

### 2. UDP扫描
- **UDP基本扫描**: 发送UDP包检测响应
- **UDP负载扫描**: 发送特定协议数据
- **UDP碎片扫描**: 绕过防火墙检测
- **递归DNS扫描**: DNS服务发现

### 3. 高级扫描
- **版本检测**: 识别服务版本信息
- **OS指纹识别**: 检测操作系统类型
- **脚本扫描**: 使用NSE脚本进行深度检测
- **IPv6扫描**: 支持IPv6网络扫描

## 常见端口和服务

### 知名端口
- **20/21**: FTP - 文件传输协议
- **22**: SSH - 安全外壳协议
- **23**: Telnet - 远程登录
- **25**: SMTP - 简单邮件传输
- **53**: DNS - 域名系统
- **80**: HTTP - 超文本传输
- **110**: POP3 - 邮局协议
- **143**: IMAP - 互联网消息访问
- **443**: HTTPS - 安全HTTP
- **993**: IMAPS - 安全IMAP
- **995**: POP3S - 安全POP3

### 数据库端口
- **3306**: MySQL数据库
- **5432**: PostgreSQL数据库
- **1433**: SQL Server数据库
- **1521**: Oracle数据库
- **27017**: MongoDB数据库
- **6379**: Redis数据库

### 应用服务端口
- **8080**: HTTP备用端口
- **8443**: HTTPS备用端口
- **3000**: Node.js应用
- **5000**: Flask应用
- **8000**: Django开发服务器
- **9000**: SonarQube

## 常见安全问题

### 未授权访问
```
问题:
开放端口提供未授权访问

症状:
- 敏感服务暴露
- 无需认证即可访问
- 配置文件泄露
- 管理接口暴露

解决方案:
- 关闭不必要的服务
- 配置访问控制
- 使用防火墙限制
- 实施身份认证
- 定期安全审计
```

### 弱认证机制
```
问题:
服务使用弱认证或默认凭据

症状:
- 默认密码未修改
- 简单易猜密码
- 无认证机制
- 明文传输凭据

解决方案:
- 修改默认密码
- 使用强密码策略
- 启用多因素认证
- 加密传输通道
- 实施账户锁定
```

### 版本漏洞
```
问题:
运行的服务版本存在已知漏洞

症状:
- 使用过时版本
- 未安装安全补丁
- 存在CVE漏洞
- 配置不当

解决方案:
- 及时更新版本
- 安装安全补丁
- 监控安全公告
- 使用漏洞扫描器
- 实施版本管理
```

## 代码实现示例

### 端口扫描器核心类
```python
import socket
import threading
import time
import concurrent.futures
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import json
import ssl
import subprocess
import re
from datetime import datetime
import ipaddress
import queue

class ScanType(Enum):
    TCP_CONNECT = "tcp_connect"
    TCP_SYN = "tcp_syn"
    UDP = "udp"
    TCP_ACK = "tcp_ack"
    TCP_FIN = "tcp_fin"

class PortStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNFILTERED = "unfiltered"
    OPEN_FILTERED = "open_filtered"

@dataclass
class PortResult:
    """端口扫描结果"""
    host: str
    port: int
    protocol: str
    status: PortStatus
    service: str = ""
    version: str = ""
    banner: str = ""
    response_time: float = 0.0
    error: str = ""

@dataclass
class HostResult:
    """主机扫描结果"""
    host: str
    is_up: bool
    os_fingerprint: str = ""
    open_ports: List[PortResult] = None
    scan_time: float = 0.0
    total_ports: int = 0
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []

class PortScanner:
    """端口扫描器"""
    
    def __init__(self, timeout: float = 3.0, max_threads: int = 100):
        self.timeout = timeout
        self.max_threads = max_threads
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995,
            1433, 1521, 3306, 5432, 6379, 27017,
            8080, 8443, 3000, 5000, 8000, 9000
        ]
        self.service_ports = self._load_service_ports()
        
    def _load_service_ports(self) -> Dict[int, str]:
        """加载端口服务映射"""
        return {
            20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
            53: "dns", 80: "http", 110: "pop3", 143: "imap", 443: "https",
            993: "imaps", 995: "pop3s", 1433: "mssql", 1521: "oracle",
            3306: "mysql", 5432: "postgresql", 6379: "redis", 27017: "mongodb",
            8080: "http-alt", 8443: "https-alt", 3000: "http-alt",
            5000: "http-alt", 8000: "http-alt", 9000: "http-alt"
        }
    
    def scan_host(self, host: str, ports: List[int] = None, 
                  scan_type: ScanType = ScanType.TCP_CONNECT) -> HostResult:
        """扫描单个主机"""
        if ports is None:
            ports = self.common_ports
        
        start_time = time.time()
        host_result = HostResult(host=host, is_up=False, total_ports=len(ports))
        
        # 首先检查主机是否在线
        if not self._is_host_up(host):
            host_result.scan_time = time.time() - start_time
            return host_result
        
        host_result.is_up = True
        
        # 扫描端口
        if scan_type == ScanType.TCP_CONNECT:
            host_result.open_ports = self._tcp_connect_scan(host, ports)
        elif scan_type == ScanType.UDP:
            host_result.open_ports = self._udp_scan(host, ports)
        else:
            host_result.open_ports = self._tcp_connect_scan(host, ports)
        
        # 尝试OS指纹识别
        host_result.os_fingerprint = self._os_fingerprint(host)
        
        host_result.scan_time = time.time() - start_time
        return host_result
    
    def _is_host_up(self, host: str) -> bool:
        """检查主机是否在线"""
        try:
            # 尝试ping
            result = subprocess.run(['ping', '-c', '1', '-W', '2', host], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # 如果ping失败，尝试连接常见端口
        for port in [22, 80, 443]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    return True
            except:
                continue
        
        return False
    
    def _tcp_connect_scan(self, host: str, ports: List[int]) -> List[PortResult]:
        """TCP连接扫描"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_port = {
                executor.submit(self._scan_tcp_port, host, port): port 
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(PortResult(
                        host=host,
                        port=port,
                        protocol="tcp",
                        status=PortStatus.CLOSED,
                        error=str(e)
                    ))
        
        return results
    
    def _scan_tcp_port(self, host: str, port: int) -> PortResult:
        """扫描单个TCP端口"""
        result = PortResult(host=host, port=port, protocol="tcp")
        
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            connection_result = sock.connect_ex((host, port))
            result.response_time = time.time() - start_time
            
            if connection_result == 0:
                result.status = PortStatus.OPEN
                result.service = self.service_ports.get(port, "unknown")
                
                # 尝试获取banner信息
                try:
                    sock.settimeout(2)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    result.banner = banner
                    
                    # 尝试版本检测
                    result.version = self._detect_service_version(port, banner)
                except:
                    pass
            else:
                result.status = PortStatus.CLOSED
            
            sock.close()
            
        except socket.timeout:
            result.status = PortStatus.FILTERED
        except Exception as e:
            result.status = PortStatus.CLOSED
            result.error = str(e)
        
        return result
    
    def _udp_scan(self, host: str, ports: List[int]) -> List[PortResult]:
        """UDP扫描"""
        results = []
        
        for port in ports:
            result = PortResult(host=host, port=port, protocol="udp")
            
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.timeout)
                
                # 发送UDP探测包
                if port == 53:  # DNS
                    probe = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01'
                elif port == 161:  # SNMP
                    probe = b'\x30\x26\x02\x01\x01\x04\x06public\xa0\x19\x02\x04\x00\x00\x00\x00\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00'
                else:
                    probe = b'\x00'  # 空探测包
                
                sock.sendto(probe, (host, port))
                
                try:
                    data, addr = sock.recvfrom(1024)
                    result.response_time = time.time() - start_time
                    result.status = PortStatus.OPEN
                    result.service = self.service_ports.get(port, "unknown")
                    result.banner = data.hex()
                except socket.timeout:
                    result.status = PortStatus.OPEN_FILTERED
                except:
                    result.status = PortStatus.CLOSED
                
                sock.close()
                
            except Exception as e:
                result.status = PortStatus.CLOSED
                result.error = str(e)
            
            results.append(result)
        
        return results
    
    def _detect_service_version(self, port: int, banner: str) -> str:
        """检测服务版本"""
        if not banner:
            return ""
        
        # 常见服务版本检测
        patterns = {
            22: r'SSH[_-][\d\.]+',
            25: r'ESMTP [\w\.]+',
            80: r'Apache/[\d\.]+|nginx/[\d\.]+',
            443: r'Apache/[\d\.]+|nginx/[\d\.]+',
            3306: r'[\d\.]+-mysql',
            5432: r'PostgreSQL [\d\.]+',
            6379: r'redis_version:[\d\.]+'
        }
        
        if port in patterns:
            match = re.search(patterns[port], banner, re.IGNORECASE)
            if match:
                return match.group()
        
        return ""
    
    def _os_fingerprint(self, host: str) -> str:
        """OS指纹识别"""
        try:
            # 使用p0f进行OS指纹识别（需要安装p0f）
            result = subprocess.run(['p0f', '-s', '/tmp/p0f.sock', host], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'OS:' in line:
                        return line.strip()
        except:
            pass
        
        # 简单的OS检测基于TTL值
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, 80))
            sock.close()
            
            # 获取TTL值需要更复杂的实现
            return "Unknown"
        except:
            pass
        
        return "Unknown"
    
    def scan_network(self, network: str, ports: List[int] = None) -> List[HostResult]:
        """扫描网络"""
        try:
            network_obj = ipaddress.ip_network(network, strict=False)
        except ValueError:
            return []
        
        hosts = [str(host) for host in network_obj.hosts()]
        return self.scan_multiple_hosts(hosts, ports)
    
    def scan_multiple_hosts(self, hosts: List[str], ports: List[int] = None) -> List[HostResult]:
        """扫描多个主机"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_host = {
                executor.submit(self.scan_host, host, ports): host 
                for host in hosts
            }
            
            for future in concurrent.futures.as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(HostResult(
                        host=host,
                        is_up=False,
                        total_ports=len(ports) if ports else 0,
                        scan_time=0
                    ))
        
        return results
    
    def port_range_scan(self, host: str, start_port: int, end_port: int) -> HostResult:
        """端口范围扫描"""
        ports = list(range(start_port, end_port + 1))
        return self.scan_host(host, ports)
    
    def service_detection(self, host: str, port: int) -> PortResult:
        """服务检测"""
        result = self._scan_tcp_port(host, port)
        
        if result.status == PortStatus.OPEN:
            # 更详细的服务检测
            result.version = self._detailed_service_detection(host, port)
        
        return result
    
    def _detailed_service_detection(self, host: str, port: int) -> str:
        """详细服务检测"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # 根据端口发送特定探测
            probes = {
                21: b'HELP\r\n',
                22: b'\x00',
                25: b'EHLO test\r\n',
                80: b'GET / HTTP/1.1\r\nHost: test\r\n\r\n',
                110: b'USER test\r\n',
                143: b'A001 CAPABILITY\r\n',
                443: self._create_ssl_probe(host, port),
                3306: b'',  # MySQL需要特殊处理
                5432: b'',  # PostgreSQL需要特殊处理
            }
            
            if port in probes:
                probe = probes[port]
                if isinstance(probe, bytes):
                    sock.send(probe)
                    response = sock.recv(1024).decode('utf-8', errors='ignore')
                    return self._parse_service_response(port, response)
            
            sock.close()
            
        except:
            pass
        
        return ""
    
    def _create_ssl_probe(self, host: str, port: int) -> bytes:
        """创建SSL探测"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    return f"SSL Certificate: {cert.get('subject', [])}".encode()
        except:
            return b'GET / HTTP/1.1\r\nHost: test\r\n\r\n'
    
    def _parse_service_response(self, port: int, response: str) -> str:
        """解析服务响应"""
        if not response:
            return ""
        
        # 根据端口解析响应
        if port == 21 and '220' in response:
            return f"FTP: {response.split('220 ')[1].strip()}"
        elif port == 25 and '220' in response:
            return f"SMTP: {response.split('220 ')[1].strip()}"
        elif port == 80 and 'Server:' in response:
            server_match = re.search(r'Server: ([^\r\n]+)', response)
            if server_match:
                return f"HTTP: {server_match.group(1)}"
        elif port == 110 and '+OK' in response:
            return f"POP3: {response.split('+OK ')[1].strip()}"
        elif port == 143 and '* CAPABILITY' in response:
            return f"IMAP: {response}"
        
        return response[:100]
    
    def generate_scan_report(self, results: List[HostResult]) -> str:
        """生成扫描报告"""
        total_hosts = len(results)
        live_hosts = sum(1 for r in results if r.is_up)
        total_open_ports = sum(len(r.open_ports) for r in results)
        
        report = f"""
# 端口扫描报告

**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**扫描主机数**: {total_hosts}
**在线主机数**: {live_hosts}
**开放端口总数**: {total_open_ports}

## 主机详情

"""
        
        for result in results:
            if not result.is_up:
                report += f"### {result.host} - 离线\n\n"
                continue
            
            report += f"### {result.host} - 在线\n"
            report += f"**扫描时间**: {result.scan_time:.2f}秒\n"
            report += f"**OS指纹**: {result.os_fingerprint}\n"
            report += f"**开放端口数**: {len(result.open_ports)}\n\n"
            
            if result.open_ports:
                report += "**端口详情**:\n\n"
                report += "| 端口 | 协议 | 状态 | 服务 | 版本 | 响应时间 |\n"
                report += "|------|------|------|------|------|----------|\n"
                
                for port_result in result.open_ports:
                    report += f"| {port_result.port} | {port_result.protocol} | "
                    report += f"{port_result.status.value} | {port_result.service} | "
                    report += f"{port_result.version} | {port_result.response_time:.3f}s |\n"
                
                report += "\n"
        
        # 统计信息
        open_ports_by_service = {}
        for result in results:
            for port_result in result.open_ports:
                service = port_result.service
                if service not in open_ports_by_service:
                    open_ports_by_service[service] = 0
                open_ports_by_service[service] += 1
        
        if open_ports_by_service:
            report += "## 服务统计\n\n"
            report += "| 服务 | 数量 |\n"
            report += "|------|------|\n"
            
            for service, count in sorted(open_ports_by_service.items(), key=lambda x: x[1], reverse=True):
                report += f"| {service} | {count} |\n"
        
        return report
    
    def export_results(self, results: List[HostResult], file_path: str, format_type: str = "json"):
        """导出扫描结果"""
        data = []
        
        for result in results:
            host_data = {
                'host': result.host,
                'is_up': result.is_up,
                'os_fingerprint': result.os_fingerprint,
                'scan_time': result.scan_time,
                'open_ports': []
            }
            
            for port_result in result.open_ports:
                port_data = {
                    'port': port_result.port,
                    'protocol': port_result.protocol,
                    'status': port_result.status.value,
                    'service': port_result.service,
                    'version': port_result.version,
                    'banner': port_result.banner,
                    'response_time': port_result.response_time
                }
                host_data['open_ports'].append(port_data)
            
            data.append(host_data)
        
        if format_type.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format_type.lower() == "csv":
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Host', 'Port', 'Protocol', 'Status', 'Service', 'Version', 'ResponseTime'])
                
                for result in results:
                    for port_result in result.open_ports:
                        writer.writerow([
                            result.host, port_result.port, port_result.protocol,
                            port_result.status.value, port_result.service,
                            port_result.version, port_result.response_time
                        ])
        
        print(f"扫描结果已导出到: {file_path}")

# 使用示例
def main():
    """示例使用"""
    print("🔍 端口扫描器启动")
    print("=" * 50)
    
    # 创建扫描器
    scanner = PortScanner(timeout=3.0, max_threads=50)
    
    # 扫描单个主机
    print("\n🎯 扫描单个主机:")
    target_host = "127.0.0.1"  # 本地测试
    host_result = scanner.scan_host(target_host, scanner.common_ports)
    
    print(f"主机: {host_result.host}")
    print(f"状态: {'在线' if host_result.is_up else '离线'}")
    print(f"扫描时间: {host_result.scan_time:.2f}秒")
    print(f"开放端口数: {len(host_result.open_ports)}")
    
    if host_result.open_ports:
        print("\n开放端口:")
        for port_result in host_result.open_ports:
            print(f"  {port_result.port}/{port_result.protocol} - {port_result.status.value} - {port_result.service}")
    
    # 服务检测
    print(f"\n🔍 服务检测:")
    for port in [22, 80, 443]:
        service_result = scanner.service_detection(target_host, port)
        print(f"  端口 {port}: {service_result.service} - {service_result.version}")
    
    # 扫描网络段（演示）
    print(f"\n🌐 扫描网络段:")
    network = "192.168.1.0/30"  # 小范围测试
    network_results = scanner.scan_network(network, [22, 80, 443])
    
    print(f"扫描了 {len(network_results)} 个主机")
    for result in network_results:
        status = "在线" if result.is_up else "离线"
        print(f"  {result.host}: {status}")
    
    # 生成报告
    print(f"\n📋 生成扫描报告:")
    all_results = [host_result] + network_results
    report = scanner.generate_scan_report(all_results)
    
    print(report[:500] + "..." if len(report) > 500 else report)
    
    # 导出结果
    print(f"\n💾 导出扫描结果:")
    scanner.export_results(all_results, "scan_results.json", "json")
    scanner.export_results(all_results, "scan_results.csv", "csv")
    
    print("\n✅ 端口扫描器演示完成!")
    print("⚠️  注意: 仅在授权网络中使用端口扫描工具")

if __name__ == "__main__":
    main()
```

### 网络发现工具
```python
class NetworkDiscovery:
    """网络发现工具"""
    
    def __init__(self):
        self.discovered_hosts = []
        self.network_topology = {}
        
    def discover_network(self, network: str) -> List[str]:
        """发现网络中的主机"""
        try:
            network_obj = ipaddress.ip_network(network, strict=False)
        except ValueError:
            return []
        
        live_hosts = []
        
        # 使用ping发现主机
        for host in network_obj.hosts():
            if self._ping_host(str(host)):
                live_hosts.append(str(host))
        
        self.discovered_hosts = live_hosts
        return live_hosts
    
    def _ping_host(self, host: str) -> bool:
        """ping主机"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', host], 
                                  capture_output=True, text=True, timeout=3)
            return result.returncode == 0
        except:
            return False
    
    def map_network_topology(self, hosts: List[str]) -> Dict:
        """映射网络拓扑"""
        topology = {
            'nodes': [],
            'edges': []
        }
        
        for host in hosts:
            node_info = {
                'host': host,
                'hostname': self._get_hostname(host),
                'mac_address': self._get_mac_address(host),
                'open_ports': []
            }
            topology['nodes'].append(node_info)
        
        self.network_topology = topology
        return topology
    
    def _get_hostname(self, host: str) -> str:
        """获取主机名"""
        try:
            hostname = socket.gethostbyaddr(host)[0]
            return hostname
        except:
            return host
    
    def _get_mac_address(self, host: str) -> str:
        """获取MAC地址"""
        try:
            # 使用arp命令获取MAC地址
            result = subprocess.run(['arp', '-n', host], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if host in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        except:
            pass
        return "Unknown"

# 使用示例
def main():
    discovery = NetworkDiscovery()
    print("网络发现工具已准备就绪!")

if __name__ == "__main__":
    main()
```

## 端口扫描最佳实践

### 扫描策略
1. **分阶段扫描**: 先快速扫描，再详细扫描
2. **目标明确**: 明确扫描目标和范围
3. **权限确认**: 确保有扫描权限
4. **时间控制**: 避免在网络高峰期扫描
5. **隐蔽性**: 根据需要选择隐蔽扫描方式

### 安全考虑
1. **法律合规**: 确保扫描行为合法
2. **授权扫描**: 只扫描授权网络
3. **影响评估**: 评估扫描对网络的影响
4. **日志记录**: 记录扫描活动
5. **结果保护**: 保护扫描结果安全

### 结果分析
1. **风险评估**: 评估开放端口的安全风险
2. **服务识别**: 准确识别运行的服务
3. **版本检测**: 检测服务版本信息
4. **漏洞关联**: 关联已知漏洞信息
5. **修复建议**: 提供安全修复建议

## 端口扫描工具推荐

### 开源工具
- **Nmap**: 功能强大的网络扫描器
- **Masscan**: 高速端口扫描器
- **ZMap**: 互联网规模扫描器
- **Unicornscan**: 异步端口扫描器
- **hping3**: 网络探测工具

### 商业工具
- **Nessus**: 漏洞扫描器
- **OpenVAS**: 开源漏洞扫描
- **Rapid7**: 安全评估平台
- **Qualys**: 云安全平台
- **Tenable**: 网络安全解决方案

### 在线工具
- **Shodan**: 互联网设备搜索
- **Censys**: 互联网资产发现
- **ZoomEye**: 网络空间搜索引擎
- **BinaryEdge**: 网络威胁情报

## 相关技能

- **network-security** - 网络安全
- **vulnerability-assessment** - 漏洞评估
- **penetration-testing** - 渗透测试
- **network-discovery** - 网络发现
- **security-auditing** - 安全审计
- **threat-intelligence** - 威胁情报
