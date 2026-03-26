---
name: 网络安全
description: "当保护网络基础设施、检测安全威胁、实施安全策略、进行漏洞评估或响应安全事件时，提供全面的网络安全防护指导。"
license: MIT
---

# 网络安全技能

## 概述
网络安全是保护计算机网络、系统和数据免受攻击、损坏或未授权访问的实践。它涵盖了从网络架构设计到实时威胁检测的全方位安全防护，确保信息系统的机密性、完整性和可用性。

**核心原则**: 纵深防御、最小权限、零信任架构、持续监控、快速响应。

## 何时使用

**始终:**
- 设计新的网络架构
- 部署安全设备和系统
- 进行安全评估和审计
- 响应安全事件和威胁
- 制定安全策略和规程
- 实施访问控制机制
- 监控网络流量和异常
- 进行员工安全培训

**触发短语:**
- "网络安全防护方案"
- "如何检测网络攻击"
- "防火墙配置最佳实践"
- "网络安全风险评估"
- "入侵检测系统部署"
- "网络安全事件响应"
- "网络访问控制策略"
- "安全监控和日志分析"

## 网络安全层次架构

### 1. 网络边界安全
- **防火墙**: 控制网络流量进出
- **入侵检测系统(IDS)**: 监控恶意活动
- **入侵防御系统(IPS)**: 主动阻止攻击
- **VPN网关**: 安全远程访问
- **DMZ区域**: 隔离公共服务

### 2. 网络内部安全
- **网络分段**: 限制横向移动
- **VLAN隔离**: 逻辑网络分离
- **内部防火墙**: 细粒度访问控制
- **网络访问控制(NAC)**: 设备准入控制
- **流量监控**: 异常行为检测

### 3. 终端安全
- **主机防火墙**: 终端级防护
- **终端检测响应(EDR)**: 高级威胁检测
- **反病毒软件**: 恶意软件防护
- **设备加密**: 数据保护
- **补丁管理**: 漏洞修复

### 4. 数据安全
- **数据加密**: 传输和存储加密
- **数据防泄漏(DLP)**: 敏感信息保护
- **数据库安全**: 访问控制和审计
- **备份加密**: 备份数据保护
- **密钥管理**: 加密密钥管理

## 常见网络攻击类型

### DDoS攻击
```
攻击类型:
分布式拒绝服务攻击，通过大量无效请求耗尽服务器资源

症状:
- 网络响应缓慢或不可用
- 服务器CPU和内存使用率极高
- 正常用户无法访问服务
- 网络带宽被占满

防护措施:
- 部署DDoS防护设备
- 使用CDN分散流量
- 配置流量清洗服务
- 实施速率限制
- 建立应急响应预案
```

### 中间人攻击
```
攻击类型:
攻击者拦截和篡改通信双方的数据传输

症状:
- 通信内容被窃取或篡改
- 证书验证异常
- 网络行为异常
- 数据完整性受损

防护措施:
- 使用SSL/TLS加密
- 实施证书固定
- 部署HSTS策略
- 使用VPN连接
- 监控证书异常
```

### SQL注入攻击
```
攻击类型:
通过输入恶意SQL代码攻击数据库

症状:
- 数据库异常查询
- 数据泄露或篡改
- 系统权限提升
- 服务异常中断

防护措施:
- 输入验证和过滤
- 参数化查询
- 最小权限原则
- 数据库审计
- Web应用防火墙
```

## 代码实现示例

### 网络安全监控系统
```python
import socket
import threading
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import ipaddress
from collections import defaultdict, deque

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    SUSPICIOUS_TRAFFIC = "suspicious_traffic"
    BRUTE_FORCE = "brute_force"
    DDOS_ATTACK = "ddos_attack"
    PORT_SCAN = "port_scan"
    MALICIOUS_IP = "malicious_ip"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"

@dataclass
class SecurityEvent:
    """安全事件"""
    timestamp: datetime
    event_type: AlertType
    source_ip: str
    target_ip: str
    target_port: int
    threat_level: ThreatLevel
    description: str
    raw_data: str = ""
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['threat_level'] = self.threat_level.value
        return data

@dataclass
class NetworkTraffic:
    """网络流量数据"""
    timestamp: datetime
    source_ip: str
    target_ip: str
    source_port: int
    target_port: int
    protocol: str
    packet_size: int
    flags: str = ""

class NetworkSecurityMonitor:
    """网络安全监控器"""
    
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.traffic_log: deque = deque(maxlen=10000)
        self.blocked_ips: set = set()
        self.whitelist_ips: set = set()
        self.threat_intelligence: Dict[str, ThreatLevel] = {}
        self.rate_limits: Dict[str, Dict] = defaultdict(dict)
        self.anomaly_thresholds = {
            'max_connections_per_minute': 100,
            'max_failed_logins_per_minute': 10,
            'max_ports_scanned_per_minute': 50,
            'max_bandwidth_per_minute': 1000000  # bytes
        }
        
    def add_threat_intelligence(self, ip: str, threat_level: ThreatLevel):
        """添加威胁情报"""
        self.threat_intelligence[ip] = threat_level
        
    def add_whitelist_ip(self, ip: str):
        """添加白名单IP"""
        self.whitelist_ips.add(ip)
        
    def is_ip_whitelisted(self, ip: str) -> bool:
        """检查IP是否在白名单中"""
        return ip in self.whitelist_ips
        
    def is_ip_blocked(self, ip: str) -> bool:
        """检查IP是否被阻止"""
        return ip in self.blocked_ips
        
    def block_ip(self, ip: str, duration_minutes: int = 60):
        """阻止IP访问"""
        self.blocked_ips.add(ip)
        # 在实际实现中，这里会调用防火墙API
        print(f"🚫 IP {ip} 已被阻止 {duration_minutes} 分钟")
        
        # 设置定时解除阻止
        threading.Timer(duration_minutes * 60, self.unblock_ip, args=[ip]).start()
        
    def unblock_ip(self, ip: str):
        """解除IP阻止"""
        self.blocked_ips.discard(ip)
        print(f"✅ IP {ip} 阻止已解除")
        
    def analyze_traffic(self, traffic: NetworkTraffic) -> Optional[SecurityEvent]:
        """分析网络流量"""
        # 检查威胁情报
        if traffic.source_ip in self.threat_intelligence:
            threat_level = self.threat_intelligence[traffic.source_ip]
            return SecurityEvent(
                timestamp=traffic.timestamp,
                event_type=AlertType.MALICIOUS_IP,
                source_ip=traffic.source_ip,
                target_ip=traffic.target_ip,
                target_port=traffic.target_port,
                threat_level=threat_level,
                description=f"检测到来自已知恶意IP {traffic.source_ip} 的流量"
            )
        
        # 检查DDoS攻击
        ddos_event = self._detect_ddos_attack(traffic)
        if ddos_event:
            return ddos_event
            
        # 检查端口扫描
        port_scan_event = self._detect_port_scan(traffic)
        if port_scan_event:
            return port_scan_event
            
        # 检查暴力破解
        brute_force_event = self._detect_brute_force(traffic)
        if brute_force_event:
            return brute_force_event
            
        # 检查异常行为
        anomaly_event = self._detect_anomalous_behavior(traffic)
        if anomaly_event:
            return anomaly_event
            
        return None
        
    def _detect_ddos_attack(self, traffic: NetworkTraffic) -> Optional[SecurityEvent]:
        """检测DDoS攻击"""
        current_time = traffic.timestamp
        minute_ago = current_time - timedelta(minutes=1)
        
        # 统计最近1分钟的连接数
        recent_connections = [
            t for t in self.traffic_log
            if minute_ago <= t.timestamp <= current_time
            and t.source_ip == traffic.source_ip
        ]
        
        connection_count = len(recent_connections)
        
        if connection_count > self.anomaly_thresholds['max_connections_per_minute']:
            return SecurityEvent(
                timestamp=traffic.timestamp,
                event_type=AlertType.DDOS_ATTACK,
                source_ip=traffic.source_ip,
                target_ip=traffic.target_ip,
                target_port=traffic.target_port,
                threat_level=ThreatLevel.HIGH,
                description=f"检测到可能的DDoS攻击，连接数: {connection_count}/分钟"
            )
            
        return None
        
    def _detect_port_scan(self, traffic: NetworkTraffic) -> Optional[SecurityEvent]:
        """检测端口扫描"""
        current_time = traffic.timestamp
        minute_ago = current_time - timedelta(minutes=1)
        
        # 统计最近1分钟扫描的不同端口数
        recent_scans = [
            t for t in self.traffic_log
            if minute_ago <= t.timestamp <= current_time
            and t.source_ip == traffic.source_ip
            and t.target_ip == traffic.target_ip
        ]
        
        unique_ports = len(set(t.target_port for t in recent_scans))
        
        if unique_ports > self.anomaly_thresholds['max_ports_scanned_per_minute']:
            return SecurityEvent(
                timestamp=traffic.timestamp,
                event_type=AlertType.PORT_SCAN,
                source_ip=traffic.source_ip,
                target_ip=traffic.target_ip,
                target_port=traffic.target_port,
                threat_level=ThreatLevel.MEDIUM,
                description=f"检测到端口扫描行为，扫描端口数: {unique_ports}/分钟"
            )
            
        return None
        
    def _detect_brute_force(self, traffic: NetworkTraffic) -> Optional[SecurityEvent]:
        """检测暴力破解攻击"""
        # 简化版本：检查SSH/FTP等服务的频繁连接
        if traffic.target_port not in [22, 21, 23, 3389]:
            return None
            
        current_time = traffic.timestamp
        minute_ago = current_time - timedelta(minutes=1)
        
        # 统计最近1分钟的失败连接尝试
        recent_attempts = [
            t for t in self.traffic_log
            if minute_ago <= t.timestamp <= current_time
            and t.source_ip == traffic.source_ip
            and t.target_ip == traffic.target_ip
            and t.target_port == traffic.target_port
        ]
        
        attempt_count = len(recent_attempts)
        
        if attempt_count > self.anomaly_thresholds['max_failed_logins_per_minute']:
            return SecurityEvent(
                timestamp=traffic.timestamp,
                event_type=AlertType.BRUTE_FORCE,
                source_ip=traffic.source_ip,
                target_ip=traffic.target_ip,
                target_port=traffic.target_port,
                threat_level=ThreatLevel.HIGH,
                description=f"检测到暴力破解攻击，尝试次数: {attempt_count}/分钟"
            )
            
        return None
        
    def _detect_anomalous_behavior(self, traffic: NetworkTraffic) -> Optional[SecurityEvent]:
        """检测异常行为"""
        # 检查异常时间段的活动
        hour = traffic.timestamp.hour
        if hour < 6 or hour > 22:  # 非工作时间
            # 检查是否有大量数据传输
            if traffic.packet_size > 1000000:  # 1MB
                return SecurityEvent(
                    timestamp=traffic.timestamp,
                    event_type=AlertType.ANOMALOUS_BEHAVIOR,
                    source_ip=traffic.source_ip,
                    target_ip=traffic.target_ip,
                    target_port=traffic.target_port,
                    threat_level=ThreatLevel.LOW,
                    description=f"异常时间大流量传输: {traffic.packet_size} bytes"
                )
                
        return None
        
    def process_traffic(self, traffic: NetworkTraffic):
        """处理网络流量"""
        # 记录流量
        self.traffic_log.append(traffic)
        
        # 跳过白名单IP
        if self.is_ip_whitelisted(traffic.source_ip):
            return
            
        # 跳过已阻止的IP
        if self.is_ip_blocked(traffic.source_ip):
            return
            
        # 分析流量
        event = self.analyze_traffic(traffic)
        
        if event:
            self.events.append(event)
            
            # 根据威胁级别采取行动
            if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                self.block_ip(event.source_ip)
                
            # 发送警报
            self.send_alert(event)
            
    def send_alert(self, event: SecurityEvent):
        """发送安全警报"""
        alert_message = f"""
🚨 安全警报 - {event.threat_level.value.upper()}
📅 时间: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
🎯 类型: {event.event_type.value}
📡 源IP: {event.source_ip}
🏠 目标IP: {event.target_ip}:{event.target_port}
📝 描述: {event.description}
"""
        print(alert_message)
        
        # 在实际实现中，这里会发送邮件、短信或推送到监控系统
        # self.send_email_alert(event)
        # self.send_slack_notification(event)
        
    def get_security_summary(self, hours: int = 24) -> Dict:
        """获取安全摘要"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.events
            if event.timestamp >= cutoff_time
        ]
        
        # 统计各类事件
        event_counts = defaultdict(int)
        threat_counts = defaultdict(int)
        top_attackers = defaultdict(int)
        
        for event in recent_events:
            event_counts[event.event_type.value] += 1
            threat_counts[event.threat_level.value] += 1
            top_attackers[event.source_ip] += 1
            
        return {
            'period_hours': hours,
            'total_events': len(recent_events),
            'event_types': dict(event_counts),
            'threat_levels': dict(threat_counts),
            'top_attackers': dict(sorted(top_attackers.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]),
            'blocked_ips_count': len(self.blocked_ips),
            'whitelisted_ips_count': len(self.whitelist_ips)
        }
        
    def export_events(self, file_path: str, hours: int = 24):
        """导出安全事件"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.events
            if event.timestamp >= cutoff_time
        ]
        
        data = {
            'export_time': datetime.now().isoformat(),
            'period_hours': hours,
            'events': [event.to_dict() for event in recent_events]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

class FirewallManager:
    """防火墙管理器"""
    
    def __init__(self):
        self.rules: List[Dict] = []
        self.blocked_ips: set = set()
        
    def add_rule(self, action: str, source_ip: str, target_ip: str, 
                 source_port: int, target_port: int, protocol: str):
        """添加防火墙规则"""
        rule = {
            'action': action,  # ALLOW, DENY, DROP
            'source_ip': source_ip,
            'target_ip': target_ip,
            'source_port': source_port,
            'target_port': target_port,
            'protocol': protocol,
            'created_time': datetime.now()
        }
        self.rules.append(rule)
        
    def block_ip_address(self, ip: str):
        """阻止IP地址"""
        self.blocked_ips.add(ip)
        self.add_rule('DENY', ip, '0.0.0.0', 0, 0, 'any')
        
    def allow_ip_address(self, ip: str):
        """允许IP地址"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
        # 移除相关规则
        self.rules = [rule for rule in self.rules 
                     if not (rule['source_ip'] == ip and rule['action'] == 'DENY')]
        
    def check_traffic_allowed(self, traffic: NetworkTraffic) -> bool:
        """检查流量是否被允许"""
        # 检查阻止列表
        if traffic.source_ip in self.blocked_ips:
            return False
            
        # 检查规则（简化版本）
        for rule in self.rules:
            if self._rule_matches(rule, traffic):
                return rule['action'] == 'ALLOW'
                
        return True  # 默认允许
        
    def _rule_matches(self, rule: Dict, traffic: NetworkTraffic) -> bool:
        """检查规则是否匹配流量"""
        return (rule['source_ip'] in ['0.0.0.0', traffic.source_ip] and
                rule['target_ip'] in ['0.0.0.0', traffic.target_ip] and
                (rule['source_port'] == 0 or rule['source_port'] == traffic.source_port) and
                (rule['target_port'] == 0 or rule['target_port'] == traffic.target_port) and
                (rule['protocol'] == 'any' or rule['protocol'] == traffic.protocol))

# 使用示例
def main():
    """示例使用"""
    print("🔐 网络安全监控系统启动")
    print("=" * 50)
    
    # 创建安全监控器
    monitor = NetworkSecurityMonitor()
    
    # 添加威胁情报
    monitor.add_threat_intelligence("192.168.1.100", ThreatLevel.HIGH)
    monitor.add_threat_intelligence("10.0.0.50", ThreatLevel.MEDIUM)
    
    # 添加白名单
    monitor.add_whitelist_ip("192.168.1.10")  # 管理员IP
    monitor.add_whitelist_ip("192.168.1.20")  # 服务器IP
    
    # 创建防火墙管理器
    firewall = FirewallManager()
    
    # 模拟网络流量
    test_traffic = [
        NetworkTraffic(
            timestamp=datetime.now(),
            source_ip="192.168.1.100",
            target_ip="192.168.1.1",
            source_port=12345,
            target_port=80,
            protocol="TCP",
            packet_size=1024
        ),
        NetworkTraffic(
            timestamp=datetime.now(),
            source_ip="192.168.1.200",
            target_ip="192.168.1.1",
            source_port=54321,
            target_port=22,
            protocol="TCP",
            packet_size=512
        ),
        NetworkTraffic(
            timestamp=datetime.now(),
            source_ip="10.0.0.50",
            target_ip="192.168.1.1",
            source_port=33333,
            target_port=443,
            protocol="TCP",
            packet_size=2048
        )
    ]
    
    # 处理流量
    for i, traffic in enumerate(test_traffic):
        print(f"\n📡 处理流量 {i+1}: {traffic.source_ip} -> {traffic.target_ip}:{traffic.target_port}")
        
        # 防火墙检查
        if firewall.check_traffic_allowed(traffic):
            print("✅ 流量通过防火墙")
            monitor.process_traffic(traffic)
        else:
            print("🚫 流量被防火墙阻止")
    
    # 获取安全摘要
    summary = monitor.get_security_summary(1)
    print(f"\n📊 安全摘要:")
    print(f"总事件数: {summary['total_events']}")
    print(f"威胁级别分布: {summary['threat_levels']}")
    print(f"事件类型分布: {summary['event_types']}")
    print(f"被阻止IP数: {summary['blocked_ips_count']}")
    
    print("\n✅ 网络安全监控系统演示完成!")

if __name__ == "__main__":
    main()
```

### 漏洞扫描器
```python
import socket
import ssl
import subprocess
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class VulnerabilitySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Vulnerability:
    """漏洞信息"""
    name: str
    description: str
    severity: VulnerabilitySeverity
    cve_id: Optional[str] = None
    affected_service: str = ""
    port: int = 0
    recommendation: str = ""

class VulnerabilityScanner:
    """漏洞扫描器"""
    
    def __init__(self):
        self.vulnerabilities: List[Vulnerability] = []
        self.common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
        
    def scan_host(self, host: str, ports: List[int] = None) -> List[Vulnerability]:
        """扫描主机漏洞"""
        if ports is None:
            ports = self.common_ports
            
        found_vulns = []
        
        # 端口扫描
        open_ports = self._port_scan(host, ports)
        
        # 服务版本检测
        for port in open_ports:
            service_vulns = self._scan_service(host, port)
            found_vulns.extend(service_vulns)
            
        # SSL/TLS检查
        if 443 in open_ports or 8443 in open_ports:
            ssl_vulns = self._scan_ssl_tls(host)
            found_vulns.extend(ssl_vulns)
            
        # Web应用扫描
        if 80 in open_ports or 443 in open_ports:
            web_vulns = self._scan_web_application(host)
            found_vulns.extend(web_vulns)
            
        self.vulnerabilities.extend(found_vulns)
        return found_vulns
        
    def _port_scan(self, host: str, ports: List[int]) -> List[int]:
        """端口扫描"""
        open_ports = []
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            try:
                sock.connect((host, port))
                open_ports.append(port)
                sock.close()
            except:
                pass
                
        return open_ports
        
    def _scan_service(self, host: str, port: int) -> List[Vulnerability]:
        """扫描服务漏洞"""
        vulnerabilities = []
        
        try:
            # 获取服务banner
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host, port))
            
            if port in [80, 8080]:
                sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                banner = sock.recv(1024).decode()
            else:
                banner = sock.recv(1024).decode()
                
            sock.close()
            
            # 检查已知漏洞
            if "Apache/2.4.29" in banner:
                vulnerabilities.append(Vulnerability(
                    name="Apache 2.4.29 多个漏洞",
                    description="Apache 2.4.29版本存在多个已知安全漏洞",
                    severity=VulnerabilitySeverity.HIGH,
                    cve_id="CVE-2017-3167",
                    affected_service="Apache HTTP Server",
                    port=port,
                    recommendation="升级到最新版本的Apache"
                ))
                
        except Exception as e:
            pass
            
        return vulnerabilities
        
    def _scan_ssl_tls(self, host: str) -> List[Vulnerability]:
        """扫描SSL/TLS漏洞"""
        vulnerabilities = []
        
        try:
            # SSL连接测试
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    version = ssock.version()
                    
                    # 检查弱SSL版本
                    if version in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                        vulnerabilities.append(Vulnerability(
                            name="弱SSL/TLS版本",
                            description=f"使用不安全的SSL/TLS版本: {version}",
                            severity=VulnerabilitySeverity.HIGH,
                            affected_service="SSL/TLS",
                            port=443,
                            recommendation="禁用弱SSL/TLS版本，使用TLS 1.2或更高版本"
                        ))
                        
        except Exception as e:
            pass
            
        return vulnerabilities
        
    def _scan_web_application(self, host: str) -> List[Vulnerability]:
        """扫描Web应用漏洞"""
        vulnerabilities = []
        
        try:
            # 检查常见Web漏洞
            urls_to_test = [
                f"http://{host}/",
                f"https://{host}/",
                f"http://{host}/admin",
                f"https://{host}/admin"
            ]
            
            for url in urls_to_test:
                try:
                    response = requests.get(url, timeout=5, verify=False)
                    
                    # 检查服务器信息泄露
                    if 'Server' in response.headers:
                        server_info = response.headers['Server']
                        if any(version in server_info for version in ['Apache/2.2', 'nginx/1.0', 'IIS/6.0']):
                            vulnerabilities.append(Vulnerability(
                                name="过时的Web服务器",
                                description=f"检测到过时的Web服务器: {server_info}",
                                severity=VulnerabilitySeverity.MEDIUM,
                                affected_service="Web Server",
                                port=80 if url.startswith('http://') else 443,
                                recommendation="升级Web服务器到最新版本"
                            ))
                            
                    # 检查目录列表
                    if response.status_code == 200 and 'Index of' in response.text:
                        vulnerabilities.append(Vulnerability(
                            name="目录列表启用",
                            description="Web服务器启用了目录列表功能",
                            severity=VulnerabilitySeverity.LOW,
                            affected_service="Web Server",
                            port=80 if url.startswith('http://') else 443,
                            recommendation="禁用目录列表功能"
                        ))
                        
                except requests.RequestException:
                    pass
                    
        except Exception as e:
            pass
            
        return vulnerabilities
        
    def generate_report(self) -> str:
        """生成漏洞报告"""
        if not self.vulnerabilities:
            return "未发现漏洞"
            
        # 按严重程度分组
        by_severity = {
            VulnerabilitySeverity.CRITICAL: [],
            VulnerabilitySeverity.HIGH: [],
            VulnerabilitySeverity.MEDIUM: [],
            VulnerabilitySeverity.LOW: []
        }
        
        for vuln in self.vulnerabilities:
            by_severity[vuln.severity].append(vuln)
            
        report = "# 漏洞扫描报告\n\n"
        report += f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"发现漏洞总数: {len(self.vulnerabilities)}\n\n"
        
        for severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH, 
                        VulnerabilitySeverity.MEDIUM, VulnerabilitySeverity.LOW]:
            vulns = by_severity[severity]
            if vulns:
                report += f"## {severity.value.upper()} 级别漏洞 ({len(vulns)})\n\n"
                
                for vuln in vulns:
                    report += f"### {vuln.name}\n"
                    report += f"**描述**: {vuln.description}\n"
                    report += f"**影响服务**: {vuln.affected_service}\n"
                    report += f"**端口**: {vuln.port}\n"
                    if vuln.cve_id:
                        report += f"**CVE编号**: {vuln.cve_id}\n"
                    report += f"**修复建议**: {vuln.recommendation}\n\n"
                    
        return report

# 使用示例
def main():
    scanner = VulnerabilityScanner()
    print("漏洞扫描器已准备就绪!")

if __name__ == "__main__":
    main()
```

## 网络安全最佳实践

### 网络架构安全
1. **分层防御**: 多层次安全控制
2. **网络分段**: 限制威胁传播范围
3. **最小权限**: 只授予必要的访问权限
4. **零信任**: 不信任任何网络流量

### 访问控制
1. **强认证**: 多因素身份认证
2. **最小权限**: 基于角色的访问控制
3. **定期审查**: 定期更新权限设置
4. **会话管理**: 安全的会话控制

### 监控和响应
1. **实时监控**: 24/7安全监控
2. **日志分析**: 完整的日志记录和分析
3. **事件响应**: 快速响应安全事件
4. **威胁情报**: 及时更新威胁信息

### 数据保护
1. **加密传输**: 所有敏感数据加密
2. **数据分类**: 按敏感度分类数据
3. **备份策略**: 定期备份和恢复测试
4. **数据防泄漏**: 防止敏感信息泄露

## 安全工具推荐

### 网络安全工具
- **Wireshark**: 网络协议分析器
- **Nmap**: 网络扫描和发现
- **Snort**: 入侵检测系统
- **Suricata**: 网络威胁检测
- **Zeek**: 网络安全监控

### 漏洞扫描工具
- **Nessus**: 漏洞扫描器
- **OpenVAS**: 开源漏洞扫描
- **Nikto**: Web服务器扫描
- **SQLMap**: SQL注入检测
- **Burp Suite**: Web应用安全测试

### 安全监控工具
- **OSSEC**: 主机入侵检测
- **Fail2ban**: 防暴力破解
- **MISP**: 威胁情报平台
- **ELK Stack**: 日志分析平台
- **Grafana**: 安全监控仪表板

## 相关技能

- **cybersecurity** - 网络安全基础
- **penetration-testing** - 渗透测试
- **incident-response** - 安全事件响应
- **threat-intelligence** - 威胁情报
- **cryptography** - 密码学
- **security-compliance** - 安全合规
