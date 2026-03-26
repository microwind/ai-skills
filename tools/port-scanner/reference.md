# 端口扫描器参考文档

## 端口扫描器概述

### 什么是端口扫描器
端口扫描器是一个专门用于网络端口状态检测、服务识别和安全评估的工具。该工具支持多种扫描技术、端口范围、服务检测和漏洞扫描，提供TCP/UDP扫描、服务版本识别、操作系统检测和脚本扫描等功能，帮助安全专业人员评估网络安全状况、发现潜在威胁和优化网络配置。

### 主要功能
- **多扫描技术**: 支持TCP Connect、SYN、ACK、UDP、SCTP等多种扫描技术
- **服务检测**: 自动识别端口服务类型、版本信息和运行状态
- **安全评估**: 检测潜在漏洞、安全配置和风险等级
- **性能优化**: 支持并发扫描、负载均衡和资源管理
- **报告生成**: 生成详细的扫描报告和安全建议

## 端口扫描引擎

### 核心扫描器
```python
# port_scanner.py
import socket
import threading
import time
import ipaddress
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import csv
import os
import subprocess
import re

class ScanType(Enum):
    TCP_CONNECT = "tcp_connect"
    TCP_SYN = "tcp_syn"
    TCP_ACK = "tcp_ack"
    TCP_WINDOW = "tcp_window"
    TCP_MAIMON = "tcp_maimon"
    UDP = "udp"
    SCTP_INIT = "sctp_init"
    SCTP_COOKIE_ECHO = "sctp_cookie_echo"

class PortStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNFILTERED = "unfiltered"
    OPEN_FILTERED = "open_filtered"

class ServiceType(Enum):
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    SSH = "ssh"
    TELNET = "telnet"
    SMTP = "smtp"
    POP3 = "pop3"
    IMAP = "imap"
    DNS = "dns"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    MONGODB = "mongodb"
    UNKNOWN = "unknown"

@dataclass
class ScanTarget:
    ip: str
    hostname: str = ""
    ports: List[int] = field(default_factory=list)
    port_ranges: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class ScanResult:
    target: str
    port: int
    status: PortStatus
    service: ServiceType
    version: str = ""
    banner: str = ""
    response_time: float = 0.0
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScanConfig:
    # 扫描配置
    scan_type: ScanType = ScanType.TCP_CONNECT
    timeout: float = 3.0
    max_threads: int = 100
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # 端口配置
    ports: List[int] = field(default_factory=lambda: [80, 443, 22, 21, 25, 53, 110, 143, 3306, 5432])
    port_ranges: List[Tuple[int, int]] = field(default_factory=lambda: [(1, 1024)])
    scan_all_ports: bool = False
    
    # 服务检测
    enable_service_detection: bool = True
    enable_version_detection: bool = True
    enable_os_detection: bool = False
    
    # 输出配置
    output_format: str = "json"  # json, xml, csv, txt
    output_file: str = ""
    verbose: bool = False
    
    # 性能配置
    thread_pool_size: int = 50
    connection_limit: int = 1000
    rate_limit: float = 100.0  # connections per second

class PortScanner:
    def __init__(self, config: ScanConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.results: List[ScanResult] = []
        self.service_detector = ServiceDetector()
        self.rate_limiter = RateLimiter(config.rate_limit)
        
        # 常见端口服务映射
        self.port_service_map = {
            21: ServiceType.FTP,
            22: ServiceType.SSH,
            23: ServiceType.TELNET,
            25: ServiceType.SMTP,
            53: ServiceType.DNS,
            80: ServiceType.HTTP,
            110: ServiceType.POP3,
            143: ServiceType.IMAP,
            443: ServiceType.HTTPS,
            3306: ServiceType.MYSQL,
            5432: ServiceType.POSTGRESQL,
            6379: ServiceType.REDIS,
            27017: ServiceType.MONGODB,
        }
    
    def scan_targets(self, targets: List[ScanTarget]) -> List[ScanResult]:
        """扫描多个目标"""
        self.logger.info(f"开始扫描 {len(targets)} 个目标")
        start_time = time.time()
        
        all_results = []
        
        for target in targets:
            target_results = self.scan_target(target)
            all_results.extend(target_results)
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"扫描完成，耗时 {elapsed_time:.2f} 秒，发现 {len(all_results)} 个开放端口")
        
        return all_results
    
    def scan_target(self, target: ScanTarget) -> List[ScanResult]:
        """扫描单个目标"""
        self.logger.info(f"扫描目标: {target.ip}")
        
        # 收集所有要扫描的端口
        ports_to_scan = self._collect_ports(target)
        
        # 并发扫描端口
        results = self._scan_ports_concurrent(target.ip, ports_to_scan)
        
        # 服务检测
        if self.config.enable_service_detection:
            results = self._detect_services(results)
        
        # 版本检测
        if self.config.enable_version_detection:
            results = self._detect_versions(results)
        
        return results
    
    def _collect_ports(self, target: ScanTarget) -> Set[int]:
        """收集所有要扫描的端口"""
        ports = set()
        
        # 添加指定端口
        ports.update(target.ports)
        ports.update(self.config.ports)
        
        # 添加端口范围
        for start, end in target.port_ranges:
            ports.update(range(start, end + 1))
        
        for start, end in self.config.port_ranges:
            ports.update(range(start, end + 1))
        
        # 如果扫描所有端口
        if self.config.scan_all_ports:
            ports.update(range(1, 65536))
        
        return ports
    
    def _scan_ports_concurrent(self, target_ip: str, ports: Set[int]) -> List[ScanResult]:
        """并发扫描端口"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.thread_pool_size) as executor:
            # 提交扫描任务
            future_to_port = {
                executor.submit(self._scan_single_port, target_ip, port): port
                for port in ports
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        if result.status == PortStatus.OPEN:
                            self.logger.info(f"发现开放端口: {target_ip}:{port}")
                except Exception as e:
                    self.logger.error(f"扫描端口 {port} 失败: {e}")
                    results.append(ScanResult(
                        target=target_ip,
                        port=port,
                        status=PortStatus.CLOSED,
                        service=ServiceType.UNKNOWN,
                        error=str(e)
                    ))
        
        return results
    
    def _scan_single_port(self, target_ip: str, port: int) -> Optional[ScanResult]:
        """扫描单个端口"""
        # 速率限制
        self.rate_limiter.wait()
        
        start_time = time.time()
        
        try:
            if self.config.scan_type == ScanType.TCP_CONNECT:
                status = self._tcp_connect_scan(target_ip, port)
            elif self.config.scan_type == ScanType.TCP_SYN:
                status = self._tcp_syn_scan(target_ip, port)
            elif self.config.scan_type == ScanType.UDP:
                status = self._udp_scan(target_ip, port)
            else:
                status = self._tcp_connect_scan(target_ip, port)
            
            response_time = time.time() - start_time
            
            if status == PortStatus.OPEN:
                service = self.port_service_map.get(port, ServiceType.UNKNOWN)
                return ScanResult(
                    target=target_ip,
                    port=port,
                    status=status,
                    service=service,
                    response_time=response_time
                )
            
        except Exception as e:
            self.logger.debug(f"扫描端口 {target_ip}:{port} 异常: {e}")
            return ScanResult(
                target=target_ip,
                port=port,
                status=PortStatus.CLOSED,
                service=ServiceType.UNKNOWN,
                error=str(e),
                response_time=time.time() - start_time
            )
        
        return None
    
    def _tcp_connect_scan(self, target_ip: str, port: int) -> PortStatus:
        """TCP Connect扫描"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.config.timeout)
        
        try:
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                return PortStatus.OPEN
            else:
                return PortStatus.CLOSED
        except socket.timeout:
            return PortStatus.FILTERED
        except Exception:
            return PortStatus.CLOSED
        finally:
            sock.close()
    
    def _tcp_syn_scan(self, target_ip: str, port: int) -> PortStatus:
        """TCP SYN扫描（需要管理员权限）"""
        # 简化实现，实际需要使用原始套接字
        try:
            # 这里应该使用原始套接字发送SYN包
            # 由于需要管理员权限，这里使用TCP Connect作为替代
            return self._tcp_connect_scan(target_ip, port)
        except Exception:
            return PortStatus.CLOSED
    
    def _udp_scan(self, target_ip: str, port: int) -> PortStatus:
        """UDP扫描"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.config.timeout)
        
        try:
            # 发送UDP探测包
            sock.sendto(b"", (target_ip, port))
            
            try:
                data, _ = sock.recvfrom(1024)
                # 收到响应，端口开放
                return PortStatus.OPEN
            except socket.timeout:
                # 超时，可能开放或过滤
                return PortStatus.OPEN_FILTERED
        except Exception:
            return PortStatus.CLOSED
        finally:
            sock.close()
    
    def _detect_services(self, results: List[ScanResult]) -> List[ScanResult]:
        """检测服务"""
        for result in results:
            if result.status == PortStatus.OPEN and result.service == ServiceType.UNKNOWN:
                detected_service = self.service_detector.detect_service(result.target, result.port)
                result.service = detected_service
        
        return results
    
    def _detect_versions(self, results: List[ScanResult]) -> List[ScanResult]:
        """检测版本"""
        for result in results:
            if result.status == PortStatus.OPEN:
                version_info = self.service_detector.detect_version(result.target, result.port, result.service)
                result.version = version_info.get('version', '')
                result.banner = version_info.get('banner', '')
        
        return results
    
    def save_results(self, results: List[ScanResult]) -> bool:
        """保存扫描结果"""
        try:
            if self.config.output_format == "json":
                self._save_json(results)
            elif self.config.output_format == "xml":
                self._save_xml(results)
            elif self.config.output_format == "csv":
                self._save_csv(results)
            elif self.config.output_format == "txt":
                self._save_txt(results)
            
            return True
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return False
    
    def _save_json(self, results: List[ScanResult]):
        """保存为JSON格式"""
        data = {
            'scan_time': datetime.now().isoformat(),
            'config': asdict(self.config),
            'results': [asdict(result) for result in results]
        }
        
        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_xml(self, results: List[ScanResult]):
        """保存为XML格式"""
        root = ET.Element('scan_results')
        
        # 添加扫描信息
        scan_info = ET.SubElement(root, 'scan_info')
        ET.SubElement(scan_info, 'scan_time').text = datetime.now().isoformat()
        ET.SubElement(scan_info, 'total_results').text = str(len(results))
        
        # 添加结果
        results_elem = ET.SubElement(root, 'results')
        for result in results:
            result_elem = ET.SubElement(results_elem, 'result')
            ET.SubElement(result_elem, 'target').text = result.target
            ET.SubElement(result_elem, 'port').text = str(result.port)
            ET.SubElement(result_elem, 'status').text = result.status.value
            ET.SubElement(result_elem, 'service').text = result.service.value
            ET.SubElement(result_elem, 'version').text = result.version
            ET.SubElement(result_elem, 'response_time').text = str(result.response_time)
        
        tree = ET.ElementTree(root)
        tree.write(self.config.output_file, encoding='utf-8', xml_declaration=True)
    
    def _save_csv(self, results: List[ScanResult]):
        """保存为CSV格式"""
        with open(self.config.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Target', 'Port', 'Status', 'Service', 'Version', 'Banner', 'Response Time'])
            
            for result in results:
                writer.writerow([
                    result.target,
                    result.port,
                    result.status.value,
                    result.service.value,
                    result.version,
                    result.banner,
                    result.response_time
                ])
    
    def _save_txt(self, results: List[ScanResult]):
        """保存为文本格式"""
        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            f.write(f"Port Scan Results\n")
            f.write(f"Scan Time: {datetime.now().isoformat()}\n")
            f.write(f"Total Results: {len(results)}\n")
            f.write(f"{'='*60}\n\n")
            
            for result in results:
                f.write(f"Target: {result.target}\n")
                f.write(f"Port: {result.port}\n")
                f.write(f"Status: {result.status.value}\n")
                f.write(f"Service: {result.service.value}\n")
                f.write(f"Version: {result.version}\n")
                f.write(f"Banner: {result.banner}\n")
                f.write(f"Response Time: {result.response_time:.3f}s\n")
                f.write(f"{'-'*40}\n")

class ServiceDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service_patterns = {
            ServiceType.HTTP: [r'HTTP/[\d.]+'],
            ServiceType.HTTPS: [r'HTTP/[\d.]+'],
            ServiceType.FTP: [r'220.*FTP'],
            ServiceType.SSH: [r'SSH-[\d.]+'],
            ServiceType.SMTP: [r'220.*SMTP', r'EHLO'],
            ServiceType.POP3: [r'\+OK.*POP3'],
            ServiceType.IMAP: [r'\* OK.*IMAP'],
        }
    
    def detect_service(self, target_ip: str, port: int) -> ServiceType:
        """检测服务类型"""
        try:
            # 尝试连接并获取服务横幅
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            try:
                sock.connect((target_ip, port))
                
                # 读取服务横幅
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                
                # 根据横幅识别服务
                for service, patterns in self.service_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, banner, re.IGNORECASE):
                            return service
                
                # 特殊处理HTTP/HTTPS
                if port in [80, 8080, 8000]:
                    return ServiceType.HTTP
                elif port in [443, 8443]:
                    return ServiceType.HTTPS
                
            except Exception:
                pass
            finally:
                sock.close()
        
        except Exception as e:
            self.logger.debug(f"服务检测失败 {target_ip}:{port}: {e}")
        
        return ServiceType.UNKNOWN
    
    def detect_version(self, target_ip: str, port: int, service: ServiceType) -> Dict[str, str]:
        """检测服务版本"""
        version_info = {'version': '', 'banner': ''}
        
        try:
            if service in [ServiceType.HTTP, ServiceType.HTTPS]:
                version_info = self._detect_http_version(target_ip, port, service)
            elif service == ServiceType.SSH:
                version_info = self._detect_ssh_version(target_ip, port)
            elif service == ServiceType.FTP:
                version_info = self._detect_ftp_version(target_ip, port)
            else:
                version_info = self._detect_generic_version(target_ip, port)
        
        except Exception as e:
            self.logger.debug(f"版本检测失败 {target_ip}:{port}: {e}")
        
        return version_info
    
    def _detect_http_version(self, target_ip: str, port: int, service: ServiceType) -> Dict[str, str]:
        """检测HTTP版本"""
        try:
            import requests
            
            protocol = 'https' if service == ServiceType.HTTPS else 'http'
            url = f"{protocol}://{target_ip}:{port}/"
            
            response = requests.get(url, timeout=5, verify=False)
            
            server_header = response.headers.get('Server', '')
            powered_by = response.headers.get('X-Powered-By', '')
            
            version = f"{server_header} {powered_by}".strip()
            banner = f"HTTP {response.status_code} {response.reason}"
            
            return {'version': version, 'banner': banner}
        
        except Exception:
            return self._detect_generic_version(target_ip, port)
    
    def _detect_ssh_version(self, target_ip: str, port: int) -> Dict[str, str]:
        """检测SSH版本"""
        return self._detect_generic_version(target_ip, port)
    
    def _detect_ftp_version(self, target_ip: str, port: int) -> Dict[str, str]:
        """检测FTP版本"""
        return self._detect_generic_version(target_ip, port)
    
    def _detect_generic_version(self, target_ip: str, port: int) -> Dict[str, str]:
        """检测通用版本"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            try:
                sock.connect((target_ip, port))
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                return {'version': banner, 'banner': banner}
            except Exception:
                pass
            finally:
                sock.close()
        
        except Exception:
            pass
        
        return {'version': '', 'banner': ''}

class RateLimiter:
    def __init__(self, rate_limit: float):
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.last_time = 0
    
    def wait(self):
        """等待以符合速率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_time
        
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_time = time.time()

# 使用示例
config = ScanConfig(
    scan_type=ScanType.TCP_CONNECT,
    timeout=3.0,
    max_threads=50,
    ports=[80, 443, 22, 21, 25, 53, 110, 143, 3306, 5432, 6379],
    enable_service_detection=True,
    enable_version_detection=True,
    output_format="json",
    output_file="scan_results.json",
    thread_pool_size=100,
    rate_limit=50.0
)

scanner = PortScanner(config)

# 创建扫描目标
targets = [
    ScanTarget(ip="192.168.1.1", hostname="gateway"),
    ScanTarget(ip="192.168.1.100", hostname="server"),
    ScanTarget(ip="10.0.0.1", ports=[80, 443, 22])
]

# 执行扫描
results = scanner.scan_targets(targets)

# 保存结果
scanner.save_results(results)

# 显示结果
print(f"扫描完成，发现 {len(results)} 个开放端口:")
for result in results:
    if result.status == PortStatus.OPEN:
        print(f"  {result.target}:{result.port} - {result.service.value} ({result.version})")
```

## 高级扫描技术

### NMAP集成
```python
# nmap_integration.py
import subprocess
import xml.etree.ElementTree as ET
import json
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

@dataclass
class NmapConfig:
    targets: str
    ports: str = ""
    scan_type: str = "-sS"  # TCP SYN scan
    service_detection: bool = True
    version_detection: bool = True
    os_detection: bool = False
    script_scan: bool = False
    output_format: str = "xml"
    timing: str = "-T4"  # Timing template
    max_retries: int = 3
    host_timeout: str = "10m"

class NmapScanner:
    def __init__(self, config: NmapConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def scan(self) -> Dict[str, Any]:
        """执行NMAP扫描"""
        cmd = self._build_command()
        
        try:
            self.logger.info(f"执行NMAP扫描: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1小时超时
            )
            
            if result.returncode != 0:
                self.logger.error(f"NMAP扫描失败: {result.stderr}")
                return {}
            
            return self._parse_output(result.stdout)
        
        except subprocess.TimeoutExpired:
            self.logger.error("NMAP扫描超时")
            return {}
        except Exception as e:
            self.logger.error(f"NMAP扫描异常: {e}")
            return {}
    
    def _build_command(self) -> List[str]:
        """构建NMAP命令"""
        cmd = ["nmap"]
        
        # 基本参数
        cmd.extend(["-p", self.config.ports] if self.config.ports else [])
        cmd.append(self.config.scan_type)
        cmd.append(self.config.timing)
        
        # 检测选项
        if self.config.service_detection:
            cmd.append("-sV")
        if self.config.version_detection:
            cmd.append("--version-intensity")
            cmd.append("5")
        if self.config.os_detection:
            cmd.append("-O")
        if self.config.script_scan:
            cmd.append("-sC")
        
        # 输出格式
        if self.config.output_format == "xml":
            cmd.extend(["-oX", "-"])
        elif self.config.output_format == "json":
            cmd.extend(["-oJ", "-"])
        
        # 超时和重试
        cmd.extend(["--max-retries", str(self.config.max_retries)])
        cmd.extend(["--host-timeout", self.config.host_timeout])
        
        # 目标
        cmd.append(self.config.targets)
        
        return cmd
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """解析NMAP输出"""
        if self.config.output_format == "xml":
            return self._parse_xml(output)
        elif self.config.output_format == "json":
            return self._parse_json(output)
        else:
            return self._parse_text(output)
    
    def _parse_xml(self, output: str) -> Dict[str, Any]:
        """解析XML输出"""
        try:
            root = ET.fromstring(output)
            
            results = {
                'scan_info': {},
                'hosts': []
            }
            
            # 解析扫描信息
            nmaprun = root.find('nmaprun')
            if nmaprun is not None:
                results['scan_info'] = {
                    'scanner': nmaprun.get('scanner'),
                    'version': nmaprun.get('version'),
                    'start': nmaprun.get('start'),
                    'args': nmaprun.get('args')
                }
            
            # 解析主机信息
            for host in root.findall('host'):
                host_info = self._parse_host(host)
                results['hosts'].append(host_info)
            
            return results
        
        except ET.ParseError as e:
            self.logger.error(f"解析XML输出失败: {e}")
            return {}
    
    def _parse_host(self, host_elem) -> Dict[str, Any]:
        """解析主机信息"""
        host_info = {
            'status': '',
            'address': '',
            'hostname': '',
            'ports': []
        }
        
        # 状态
        status = host_elem.find('status')
        if status is not None:
            host_info['status'] = status.get('state')
        
        # 地址
        address = host_elem.find('address')
        if address is not None:
            host_info['address'] = address.get('addr')
        
        # 主机名
        hostnames = host_elem.find('hostnames')
        if hostnames is not None:
            hostname = hostnames.find('hostname')
            if hostname is not None:
                host_info['hostname'] = hostname.get('name')
        
        # 端口
        ports = host_elem.find('ports')
        if ports is not None:
            for port in ports.findall('port'):
                port_info = self._parse_port(port)
                host_info['ports'].append(port_info)
        
        return host_info
    
    def _parse_port(self, port_elem) -> Dict[str, Any]:
        """解析端口信息"""
        port_info = {
            'protocol': port_elem.get('protocol'),
            'port': int(port_elem.get('portid')),
            'state': '',
            'service': {}
        }
        
        # 状态
        state = port_elem.find('state')
        if state is not None:
            port_info['state'] = state.get('state')
        
        # 服务
        service = port_elem.find('service')
        if service is not None:
            port_info['service'] = {
                'name': service.get('name', ''),
                'product': service.get('product', ''),
                'version': service.get('version', ''),
                'extra_info': service.get('extrainfo', ''),
                'method': service.get('method', ''),
                'conf': service.get('conf', '')
            }
        
        return port_info
    
    def _parse_json(self, output: str) -> Dict[str, Any]:
        """解析JSON输出"""
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            self.logger.error(f"解析JSON输出失败: {e}")
            return {}
    
    def _parse_text(self, output: str) -> Dict[str, Any]:
        """解析文本输出"""
        # 简化的文本解析
        lines = output.split('\n')
        results = {'hosts': []}
        
        current_host = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'Nmap scan report for' in line:
                if current_host:
                    results['hosts'].append(current_host)
                
                # 提取主机信息
                parts = line.split()
                host = parts[-1]
                current_host = {
                    'address': host,
                    'ports': []
                }
            
            elif current_host and '/tcp' in line or '/udp' in line:
                # 解析端口信息
                parts = line.split()
                if len(parts) >= 2:
                    port_info = parts[0]
                    state = parts[1]
                    
                    port_parts = port_info.split('/')
                    if len(port_parts) == 2:
                        port_num = int(port_parts[0])
                        protocol = port_parts[1]
                        
                        current_host['ports'].append({
                            'port': port_num,
                            'protocol': protocol,
                            'state': state
                        })
        
        if current_host:
            results['hosts'].append(current_host)
        
        return results

# 使用示例
nmap_config = NmapConfig(
    targets="192.168.1.0/24",
    ports="80,443,22,21,25,53,110,143,3306,5432",
    scan_type="-sS",
    service_detection=True,
    version_detection=True,
    os_detection=False,
    script_scan=False,
    output_format="xml",
    timing="-T4"
)

nmap_scanner = NmapScanner(nmap_config)
results = nmap_scanner.scan()

print(f"NMAP扫描结果:")
for host in results.get('hosts', []):
    print(f"主机: {host.get('address', 'Unknown')}")
    for port in host.get('ports', []):
        if port.get('state') == 'open':
            service = port.get('service', {})
            print(f"  端口 {port.get('port')}/{port.get('protocol')}: {service.get('name', 'Unknown')} {service.get('version', '')}")
```

## 安全检测模块

### 漏洞扫描
```python
# vulnerability_scanner.py
import requests
import json
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import re

@dataclass
class Vulnerability:
    cve_id: str
    severity: str
    description: str
    affected_service: str
    affected_version: str
    reference: str

class VulnerabilityScanner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cve_database = self._load_cve_database()
    
    def _load_cve_database(self) -> Dict[str, List[Vulnerability]]:
        """加载CVE数据库"""
        # 简化的CVE数据库
        return {
            'apache': [
                Vulnerability(
                    cve_id="CVE-2021-41773",
                    severity="HIGH",
                    description="Apache 2.4.49 path traversal and file disclosure vulnerability",
                    affected_service="Apache HTTP Server",
                    affected_version="2.4.49",
                    reference="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41773"
                ),
            ],
            'nginx': [
                Vulnerability(
                    cve_id="CVE-2021-23017",
                    severity="MEDIUM",
                    description="NGINX resolver vulnerability",
                    affected_service="NGINX",
                    affected_version="1.18.0",
                    reference="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-23017"
                ),
            ],
            'openssh': [
                Vulnerability(
                    cve_id="CVE-2021-41691",
                    severity="MEDIUM",
                    description="OpenSSH vulnerability",
                    affected_service="OpenSSH",
                    affected_version="8.8",
                    reference="https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41691"
                ),
            ]
        }
    
    def scan_vulnerabilities(self, scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """扫描漏洞"""
        vulnerability_results = []
        
        for host_result in scan_results:
            host_vulnerabilities = []
            
            for port in host_result.get('ports', []):
                if port.get('state') == 'open':
                    service = port.get('service', {})
                    service_name = service.get('name', '').lower()
                    version = service.get('version', '')
                    
                    # 检查已知漏洞
                    vulnerabilities = self._check_service_vulnerabilities(service_name, version)
                    
                    if vulnerabilities:
                        host_vulnerabilities.extend(vulnerabilities)
            
            if host_vulnerabilities:
                vulnerability_results.append({
                    'host': host_result.get('address', ''),
                    'vulnerabilities': host_vulnerabilities
                })
        
        return vulnerability_results
    
    def _check_service_vulnerabilities(self, service_name: str, version: str) -> List[Vulnerability]:
        """检查服务漏洞"""
        vulnerabilities = []
        
        # 检查服务特定漏洞
        for service_key, vulns in self.cve_database.items():
            if service_key in service_name:
                for vuln in vulns:
                    if self._is_version_affected(version, vuln.affected_version):
                        vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _is_version_affected(self, current_version: str, affected_version: str) -> bool:
        """检查版本是否受影响"""
        # 简化的版本比较
        try:
            current_parts = [int(x) for x in re.findall(r'\d+', current_version)]
            affected_parts = [int(x) for x in re.findall(r'\d+', affected_version)]
            
            if len(current_parts) >= 2 and len(affected_parts) >= 2:
                # 简单比较：如果主版本号相同且次版本号小于等于受影响版本
                return (current_parts[0] == affected_parts[0] and 
                       current_parts[1] <= affected_parts[1])
        except:
            pass
        
        return False

# 使用示例
vuln_scanner = VulnerabilityScanner()

# 假设的扫描结果
scan_results = [
    {
        'address': '192.168.1.100',
        'ports': [
            {
                'port': 80,
                'protocol': 'tcp',
                'state': 'open',
                'service': {
                    'name': 'Apache httpd',
                    'version': '2.4.49',
                    'product': 'Apache HTTP Server'
                }
            }
        ]
    }
]

# 扫描漏洞
vulnerability_results = vuln_scanner.scan_vulnerabilities(scan_results)

print(f"漏洞扫描结果:")
for host_vulns in vulnerability_results:
    print(f"主机: {host_vulns['host']}")
    for vuln in host_vulns['vulnerabilities']:
        print(f"  {vuln.cve_id}: {vuln.description}")
        print(f"    严重性: {vuln.severity}")
        print(f"    参考: {vuln.reference}")
```

## 参考资源

### 网络扫描
- [NMAP官方文档](https://nmap.org/docs.html)
- [NMAP脚本引擎](https://nmap.org/nsedoc/)
- [网络扫描技术](https://nmap.org/book/)
- [端口扫描原理](https://tools.ietf.org/html/rfc793)

### 安全检测
- [CVE数据库](https://cve.mitre.org/)
- [国家漏洞数据库](https://nvd.nist.gov/)
- [OWASP漏洞分类](https://owasp.org/www-project-top-ten/)
- [安全评估框架](https://www.first.org/)

### 网络协议
- [TCP协议规范](https://tools.ietf.org/html/rfc793)
- [UDP协议规范](https://tools.ietf.org/html/rfc768)
- [HTTP协议规范](https://tools.ietf.org/html/rfc2616)
- [SSH协议规范](https://tools.ietf.org/html/rfc4251)

### Python网络编程
- [Socket编程](https://docs.python.org/3/library/socket.html)
- [并发编程](https://docs.python.org/3/library/concurrent.futures.html)
- [多线程编程](https://docs.python.org/3/library/threading.html)
- [网络工具库](https://docs.python.org/3/library/socketserver.html)
