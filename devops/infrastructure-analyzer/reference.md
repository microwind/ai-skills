# 基础设施分析器参考文档

## 基础设施分析器概述

### 什么是基础设施分析器
基础设施分析器是一个综合性的基础设施评估和优化工具，用于分析系统架构、性能瓶颈、安全配置和成本效益。该工具支持多种基础设施类型（云、本地、混合），提供自动化发现、实时监控、智能分析和优化建议，帮助运维团队构建可扩展、高可用、安全可靠且成本效益的基础设施架构。

### 主要功能
- **架构分析**: 自动发现系统拓扑，分析组件依赖关系，评估架构合理性
- **性能监控**: 实时监控资源使用情况，识别性能瓶颈，提供优化建议
- **安全评估**: 全面检查安全配置，验证合规性，识别安全风险
- **成本分析**: 分析资源成本，识别优化机会，提供成本控制建议
- **扩展性评估**: 评估系统扩展能力，规划容量增长，设计扩展策略
- **可用性分析**: 评估系统可用性，设计冗余方案，制定灾难恢复计划
- **自动化运维**: 支持自动化发现、分析和优化流程
- **集成能力**: 与主流监控工具和云平台集成

## 核心分析引擎

### 架构分析器
```python
# architecture_analyzer.py
import json
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

class ComponentType(Enum):
    SERVER = "server"
    LOAD_BALANCER = "load_balancer"
    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    FIREWALL = "firewall"
    ROUTER = "router"
    CONTAINER = "container"
    FUNCTION = "function"

class InfrastructureType(Enum):
    CLOUD = "cloud"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"
    CONTAINERIZED = "containerized"
    SERVERLESS = "serverless"

@dataclass
class Component:
    id: str
    name: str
    type: ComponentType
    ip_address: str
    port: int
    status: str
    metadata: Dict[str, Any]
    dependencies: List[str] = None

@dataclass
class Connection:
    source: str
    target: str
    protocol: str
    port: int
    bandwidth: float
    latency: float

@dataclass
class ArchitectureAnalysis:
    components: List[Component]
    connections: List[Connection]
    topology_graph: nx.DiGraph
    single_points_of_failure: List[str]
    critical_paths: List[List[str]]
    redundancy_score: float
    complexity_score: float

class ArchitectureAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.components = []
        self.connections = []
        self.graph = nx.DiGraph()
    
    def add_component(self, component: Component):
        """添加组件"""
        self.components.append(component)
        self.graph.add_node(component.id, **component.__dict__)
    
    def add_connection(self, connection: Connection):
        """添加连接"""
        self.connections.append(connection)
        self.graph.add_edge(
            connection.source, 
            connection.target,
            protocol=connection.protocol,
            port=connection.port,
            bandwidth=connection.bandwidth,
            latency=connection.latency
        )
    
    def analyze_topology(self) -> Dict[str, Any]:
        """分析拓扑结构"""
        analysis = {
            'total_components': len(self.components),
            'total_connections': len(self.connections),
            'component_types': self._analyze_component_types(),
            'connectivity': self._analyze_connectivity(),
            'clusters': self._identify_clusters(),
            'hierarchy_levels': self._calculate_hierarchy_levels()
        }
        return analysis
    
    def _analyze_component_types(self) -> Dict[str, int]:
        """分析组件类型分布"""
        type_counts = {}
        for component in self.components:
            type_name = component.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        return type_counts
    
    def _analyze_connectivity(self) -> Dict[str, Any]:
        """分析连接性"""
        if not self.graph.nodes():
            return {}
        
        return {
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph.to_undirected()),
            'strongly_connected': nx.is_strongly_connected(self.graph),
            'average_clustering': nx.average_clustering(self.graph.to_undirected()),
            'diameter': nx.diameter(self.graph.to_undirected()) if nx.is_connected(self.graph.to_undirected()) else None
        }
    
    def _identify_clusters(self) -> List[List[str]]:
        """识别集群"""
        try:
            communities = nx.community.greedy_modularity_communities(self.graph.to_undirected())
            return [list(community) for community in communities]
        except:
            return []
    
    def _calculate_hierarchy_levels(self) -> int:
        """计算层级深度"""
        if not self.graph.nodes():
            return 0
        
        try:
            # 使用最长路径作为层级深度
            longest_path = nx.dag_longest_path(self.graph)
            return len(longest_path) if longest_path else 0
        except:
            return 0
    
    def identify_single_points_of_failure(self) -> List[str]:
        """识别单点故障"""
        spof = []
        
        # 检查每个节点是否为单点故障
        for node in self.graph.nodes():
            temp_graph = self.graph.copy()
            temp_graph.remove_node(node)
            
            # 检查移除该节点后图是否仍然连通
            if not nx.is_connected(temp_graph.to_undirected()):
                spof.append(node)
        
        return spof
    
    def calculate_redundancy_score(self) -> float:
        """计算冗余评分"""
        total_components = len(self.components)
        spof_count = len(self.identify_single_points_of_failure())
        
        if total_components == 0:
            return 0.0
        
        # 冗余评分 = (总组件数 - 单点故障数) / 总组件数
        redundancy_score = (total_components - spof_count) / total_components
        return redundancy_score
    
    def calculate_complexity_score(self) -> float:
        """计算复杂度评分"""
        if not self.graph.nodes():
            return 0.0
        
        # 基于图的复杂度指标
        node_count = len(self.graph.nodes())
        edge_count = len(self.graph.edges())
        
        # 复杂度评分基于边的数量与节点数量的比例
        if node_count <= 1:
            return 0.0
        
        complexity = edge_count / (node_count * (node_count - 1) / 2)
        return min(complexity, 1.0)
    
    def generate_topology_diagram(self, output_path: str = "topology.png"):
        """生成拓扑图"""
        plt.figure(figsize=(12, 8))
        
        # 设置布局
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # 绘制节点
        for component_type in ComponentType:
            nodes = [n for n in self.graph.nodes() 
                    if self.graph.nodes[n]['type'] == component_type]
            nx.draw_networkx_nodes(
                self.graph, pos, nodelist=nodes,
                node_color=self._get_color_for_type(component_type),
                node_size=1000, alpha=0.8
            )
        
        # 绘制边
        nx.draw_networkx_edges(self.graph, pos, alpha=0.6, arrows=True)
        
        # 绘制标签
        labels = {n: self.graph.nodes[n]['name'] for n in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title("Infrastructure Topology")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _get_color_for_type(self, component_type: ComponentType) -> str:
        """根据组件类型获取颜色"""
        color_map = {
            ComponentType.SERVER: '#3498db',
            ComponentType.LOAD_BALANCER: '#e74c3c',
            ComponentType.DATABASE: '#2ecc71',
            ComponentType.CACHE: '#f39c12',
            ComponentType.STORAGE: '#9b59b6',
            ComponentType.FIREWALL: '#34495e',
            ComponentType.ROUTER: '#16a085',
            ComponentType.CONTAINER: '#e67e22',
            ComponentType.FUNCTION: '#95a5a6'
        }
        return color_map.get(component_type, '#7f8c8d')
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """分析依赖关系"""
        dependency_analysis = {
            'dependency_matrix': self._create_dependency_matrix(),
            'circular_dependencies': self._find_circular_dependencies(),
            'dependency_depth': self._calculate_dependency_depth(),
            'critical_dependencies': self._identify_critical_dependencies()
        }
        return dependency_analysis
    
    def _create_dependency_matrix(self) -> Dict[str, Dict[str, bool]]:
        """创建依赖矩阵"""
        matrix = {}
        for source in self.graph.nodes():
            matrix[source] = {}
            for target in self.graph.nodes():
                matrix[source][target] = self.graph.has_edge(source, target)
        return matrix
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """查找循环依赖"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def _calculate_dependency_depth(self) -> Dict[str, int]:
        """计算依赖深度"""
        depth_map = {}
        
        # 计算每个节点的最长路径
        for node in self.graph.nodes():
            try:
                longest_path = nx.dag_longest_path_length(self.graph, source=node)
                depth_map[node] = longest_path
            except:
                depth_map[node] = 0
        
        return depth_map
    
    def _identify_critical_dependencies(self) -> List[str]:
        """识别关键依赖"""
        critical_deps = []
        
        # 基于介数中心性识别关键节点
        centrality = nx.betweenness_centrality(self.graph)
        threshold = sum(centrality.values()) / len(centrality) if centrality else 0
        
        for node, centrality_score in centrality.items():
            if centrality_score > threshold:
                critical_deps.append(node)
        
        return critical_deps

# 使用示例
analyzer = ArchitectureAnalyzer()

# 添加组件
web_server = Component(
    id="web-1", name="Web Server 1", 
    type=ComponentType.SERVER, ip_address="10.0.1.10", 
    port=80, status="running", metadata={}
)

db_server = Component(
    id="db-1", name="Database Server",
    type=ComponentType.DATABASE, ip_address="10.0.1.20",
    port=3306, status="running", metadata={}
)

analyzer.add_component(web_server)
analyzer.add_component(db_server)

# 添加连接
connection = Connection(
    source="web-1", target="db-1",
    protocol="tcp", port=3306,
    bandwidth=1000, latency=5.0
)
analyzer.add_connection(connection)

# 分析架构
topology_analysis = analyzer.analyze_topology()
spof = analyzer.identify_single_points_of_failure()
redundancy_score = analyzer.calculate_redundancy_score()

print(f"拓扑分析: {topology_analysis}")
print(f"单点故障: {spof}")
print(f"冗余评分: {redundancy_score}")
```

### 性能分析器
```python
# performance_analyzer.py
import psutil
import time
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import logging

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    DISK = "disk"
    APPLICATION = "application"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Metric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    threshold: float
    alert_level: AlertLevel

@dataclass
class PerformanceIssue:
    component_id: str
    issue_type: str
    description: str
    severity: str
    recommendations: List[str]
    detected_at: datetime

class PerformanceAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history = []
        self.performance_issues = []
        self.is_monitoring = False
        self.monitoring_thread = None
        self.thresholds = self._init_thresholds()
    
    def _init_thresholds(self) -> Dict[str, Dict[str, float]]:
        """初始化阈值配置"""
        return {
            'cpu': {
                'warning': 70.0,
                'critical': 90.0
            },
            'memory': {
                'warning': 80.0,
                'critical': 95.0
            },
            'disk': {
                'warning': 85.0,
                'critical': 95.0
            },
            'network': {
                'warning': 80.0,
                'critical': 95.0
            }
        }
    
    def start_monitoring(self, interval: int = 60):
        """开始性能监控"""
        self.is_monitoring = True
        
        def monitoring_loop():
            while self.is_monitoring:
                try:
                    self._collect_metrics()
                    self._analyze_performance()
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"监控错误: {e}")
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info(f"性能监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        self.logger.info("性能监控已停止")
    
    def _collect_metrics(self):
        """收集性能指标"""
        timestamp = datetime.now()
        
        # CPU指标
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_metric = Metric(
            name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            timestamp=timestamp,
            threshold=self.thresholds['cpu']['warning'],
            alert_level=self._get_alert_level(cpu_percent, 'cpu')
        )
        self.metrics_history.append(cpu_metric)
        
        # 内存指标
        memory = psutil.virtual_memory()
        memory_metric = Metric(
            name="memory_usage",
            value=memory.percent,
            unit="percent",
            timestamp=timestamp,
            threshold=self.thresholds['memory']['warning'],
            alert_level=self._get_alert_level(memory.percent, 'memory')
        )
        self.metrics_history.append(memory_metric)
        
        # 磁盘指标
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_metric = Metric(
            name="disk_usage",
            value=disk_percent,
            unit="percent",
            timestamp=timestamp,
            threshold=self.thresholds['disk']['warning'],
            alert_level=self._get_alert_level(disk_percent, 'disk')
        )
        self.metrics_history.append(disk_metric)
        
        # 网络指标
        network = psutil.net_io_counters()
        network_metric = Metric(
            name="network_bytes",
            value=network.bytes_sent + network.bytes_recv,
            unit="bytes",
            timestamp=timestamp,
            threshold=0,  # 网络流量需要特殊处理
            alert_level=AlertLevel.INFO
        )
        self.metrics_history.append(network_metric)
        
        # 保持历史记录在合理范围内
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-5000:]
    
    def _get_alert_level(self, value: float, metric_type: str) -> AlertLevel:
        """获取告警级别"""
        thresholds = self.thresholds.get(metric_type, {})
        
        if value >= thresholds.get('critical', 95):
            return AlertLevel.CRITICAL
        elif value >= thresholds.get('warning', 80):
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO
    
    def _analyze_performance(self):
        """分析性能问题"""
        if len(self.metrics_history) < 10:
            return
        
        # 获取最近的指标
        recent_metrics = self.metrics_history[-100:]
        
        # 分析CPU问题
        cpu_issues = self._analyze_cpu_issues(recent_metrics)
        self.performance_issues.extend(cpu_issues)
        
        # 分析内存问题
        memory_issues = self._analyze_memory_issues(recent_metrics)
        self.performance_issues.extend(memory_issues)
        
        # 分析磁盘问题
        disk_issues = self._analyze_disk_issues(recent_metrics)
        self.performance_issues.extend(disk_issues)
        
        # 分析网络问题
        network_issues = self._analyze_network_issues(recent_metrics)
        self.performance_issues.extend(network_issues)
        
        # 保持问题列表在合理范围内
        if len(self.performance_issues) > 1000:
            self.performance_issues = self.performance_issues[-500:]
    
    def _analyze_cpu_issues(self, metrics: List[Metric]) -> List[PerformanceIssue]:
        """分析CPU问题"""
        issues = []
        cpu_metrics = [m for m in metrics if m.name == "cpu_usage"]
        
        if len(cpu_metrics) < 5:
            return issues
        
        # 检查CPU使用率过高
        avg_cpu = np.mean([m.value for m in cpu_metrics])
        max_cpu = np.max([m.value for m in cpu_metrics])
        
        if max_cpu >= self.thresholds['cpu']['critical']:
            issue = PerformanceIssue(
                component_id="system",
                issue_type="cpu_overload",
                description=f"CPU使用率过高，峰值: {max_cpu:.1f}%",
                severity="critical",
                recommendations=[
                    "检查CPU密集型进程",
                    "考虑水平扩展",
                    "优化应用程序性能",
                    "增加CPU资源"
                ],
                detected_at=datetime.now()
            )
            issues.append(issue)
        elif avg_cpu >= self.thresholds['cpu']['warning']:
            issue = PerformanceIssue(
                component_id="system",
                issue_type="cpu_high",
                description=f"CPU使用率偏高，平均值: {avg_cpu:.1f}%",
                severity="warning",
                recommendations=[
                    "监控CPU使用趋势",
                    "优化进程调度",
                    "检查后台任务"
                ],
                detected_at=datetime.now()
            )
            issues.append(issue)
        
        return issues
    
    def _analyze_memory_issues(self, metrics: List[Metric]) -> List[PerformanceIssue]:
        """分析内存问题"""
        issues = []
        memory_metrics = [m for m in metrics if m.name == "memory_usage"]
        
        if len(memory_metrics) < 5:
            return issues
        
        # 检查内存使用率过高
        avg_memory = np.mean([m.value for m in memory_metrics])
        max_memory = np.max([m.value for m in memory_metrics])
        
        if max_memory >= self.thresholds['memory']['critical']:
            issue = PerformanceIssue(
                component_id="system",
                issue_type="memory_overload",
                description=f"内存使用率过高，峰值: {max_memory:.1f}%",
                severity="critical",
                recommendations=[
                    "检查内存泄漏",
                    "增加内存容量",
                    "优化内存使用",
                    "重启占用内存过多的进程"
                ],
                detected_at=datetime.now()
            )
            issues.append(issue)
        elif avg_memory >= self.thresholds['memory']['warning']:
            issue = PerformanceIssue(
                component_id="system",
                issue_type="memory_high",
                description=f"内存使用率偏高，平均值: {avg_memory:.1f}%",
                severity="warning",
                recommendations=[
                    "监控内存使用趋势",
                    "检查内存泄漏",
                    "优化应用程序"
                ],
                detected_at=datetime.now()
            )
            issues.append(issue)
        
        return issues
    
    def _analyze_disk_issues(self, metrics: List[Metric]) -> List[PerformanceIssue]:
        """分析磁盘问题"""
        issues = []
        disk_metrics = [m for m in metrics if m.name == "disk_usage"]
        
        if len(disk_metrics) < 5:
            return issues
        
        # 检查磁盘使用率过高
        avg_disk = np.mean([m.value for m in disk_metrics])
        max_disk = np.max([m.value for m in disk_metrics])
        
        if max_disk >= self.thresholds['disk']['critical']:
            issue = PerformanceIssue(
                component_id="system",
                issue_type="disk_full",
                description=f"磁盘使用率过高，峰值: {max_disk:.1f}%",
                severity="critical",
                recommendations=[
                    "清理不必要的文件",
                    "压缩或归档数据",
                    "增加存储容量",
                    "设置自动清理策略"
                ],
                detected_at=datetime.now()
            )
            issues.append(issue)
        elif avg_disk >= self.thresholds['disk']['warning']:
            issue = PerformanceIssue(
                component_id="system",
                issue_type="disk_high",
                description=f"磁盘使用率偏高，平均值: {avg_disk:.1f}%",
                severity="warning",
                recommendations=[
                    "监控磁盘使用趋势",
                    "清理临时文件",
                    "规划存储扩容"
                ],
                detected_at=datetime.now()
            )
            issues.append(issue)
        
        return issues
    
    def _analyze_network_issues(self, metrics: List[Metric]) -> List[PerformanceIssue]:
        """分析网络问题"""
        issues = []
        network_metrics = [m for m in metrics if m.name == "network_bytes"]
        
        if len(network_metrics) < 10:
            return issues
        
        # 分析网络流量趋势
        values = [m.value for m in network_metrics]
        
        # 检查网络流量异常
        if len(values) > 1:
            recent_growth = (values[-1] - values[-10]) / values[-10] if values[-10] > 0 else 0
            
            if recent_growth > 0.5:  # 50%增长
                issue = PerformanceIssue(
                    component_id="system",
                    issue_type="network_spike",
                    description=f"网络流量异常增长: {recent_growth:.1%}",
                    severity="warning",
                    recommendations=[
                        "检查网络流量来源",
                        "监控带宽使用",
                        "检查是否有异常连接"
                    ],
                    detected_at=datetime.now()
                )
                issues.append(issue)
        
        return issues
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}
        
        # 获取最新指标
        latest_metrics = {}
        for metric in self.metrics_history[-10:]:
            latest_metrics[metric.name] = metric
        
        # 获取最近的问题
        recent_issues = [issue for issue in self.performance_issues 
                       if issue.detected_at > datetime.now() - timedelta(hours=1)]
        
        summary = {
            'current_metrics': {
                name: {
                    'value': metric.value,
                    'unit': metric.unit,
                    'alert_level': metric.alert_level.value
                }
                for name, metric in latest_metrics.items()
            },
            'recent_issues': [
                {
                    'type': issue.issue_type,
                    'description': issue.description,
                    'severity': issue.severity,
                    'recommendations': issue.recommendations
                }
                for issue in recent_issues
            ],
            'total_issues': len(self.performance_issues),
            'monitoring_status': 'active' if self.is_monitoring else 'inactive'
        }
        
        return summary
    
    def generate_performance_report(self, output_path: str = "performance_report.json"):
        """生成性能报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_performance_summary(),
            'metrics_history': [
                {
                    'name': metric.name,
                    'value': metric.value,
                    'unit': metric.unit,
                    'timestamp': metric.timestamp.isoformat(),
                    'alert_level': metric.alert_level.value
                }
                for metric in self.metrics_history[-100:]  # 最近100个指标
            ],
            'performance_issues': [
                {
                    'component_id': issue.component_id,
                    'issue_type': issue.issue_type,
                    'description': issue.description,
                    'severity': issue.severity,
                    'recommendations': issue.recommendations,
                    'detected_at': issue.detected_at.isoformat()
                }
                for issue in self.performance_issues[-50:]  # 最近50个问题
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

# 使用示例
if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    
    # 开始监控
    analyzer.start_monitoring(interval=30)
    
    # 监控一段时间
    time.sleep(300)  # 5分钟
    
    # 获取性能摘要
    summary = analyzer.get_performance_summary()
    print(f"性能摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    
    # 生成报告
    report = analyzer.generate_performance_report()
    
    # 停止监控
    analyzer.stop_monitoring()
```

### 安全分析器
```python
# security_analyzer.py
import subprocess
import re
import json
import hashlib
import ssl
import socket
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO_27001 = "iso_27001"

@dataclass
class SecurityIssue:
    component_id: str
    issue_type: str
    description: str
    security_level: SecurityLevel
    recommendation: str
    detected_at: datetime
    cvss_score: Optional[float] = None

@dataclass
class ComplianceResult:
    standard: ComplianceStandard
    compliant: bool
    violations: List[str]
    recommendations: List[str]
    score: float

class SecurityAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_issues = []
        self.compliance_results = []
        self.security_checks = self._init_security_checks()
    
    def _init_security_checks(self) -> Dict[str, callable]:
        """初始化安全检查"""
        return {
            'firewall_config': self._check_firewall_config,
            'ssl_certificates': self._check_ssl_certificates,
            'open_ports': self._check_open_ports,
            'user_permissions': self._check_user_permissions,
            'password_policy': self._check_password_policy,
            'encryption_status': self._check_encryption_status,
            'access_logs': self._check_access_logs,
            'system_updates': self._check_system_updates
        }
    
    def run_security_scan(self, target: str = "localhost") -> Dict[str, Any]:
        """运行安全扫描"""
        scan_results = {
            'target': target,
            'scan_time': datetime.now().isoformat(),
            'security_issues': [],
            'compliance_results': [],
            'security_score': 0.0,
            'recommendations': []
        }
        
        # 运行所有安全检查
        for check_name, check_function in self.security_checks.items():
            try:
                result = check_function(target)
                scan_results['security_issues'].extend(result.get('issues', []))
                scan_results['recommendations'].extend(result.get('recommendations', []))
            except Exception as e:
                self.logger.error(f"安全检查 {check_name} 失败: {e}")
        
        # 计算安全评分
        scan_results['security_score'] = self._calculate_security_score(scan_results['security_issues'])
        
        # 运行合规性检查
        for standard in ComplianceStandard:
            compliance_result = self._check_compliance(standard, target)
            scan_results['compliance_results'].append(compliance_result)
        
        return scan_results
    
    def _check_firewall_config(self, target: str) -> Dict[str, Any]:
        """检查防火墙配置"""
        issues = []
        recommendations = []
        
        try:
            # 检查防火墙状态
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
            
            if 'inactive' in result.stdout:
                issue = SecurityIssue(
                    component_id="firewall",
                    issue_type="firewall_disabled",
                    description="防火墙未启用",
                    security_level=SecurityLevel.HIGH,
                    recommendation="启用防火墙并配置适当的规则",
                    detected_at=datetime.now()
                )
                issues.append(issue)
                recommendations.append("启用防火墙保护")
            
            # 检查开放端口
            port_result = subprocess.run(['netstat', -tuln'], capture_output=True, text=True)
            open_ports = self._parse_open_ports(port_result.stdout)
            
            for port_info in open_ports:
                if self._is_risky_port(port_info['port']):
                    issue = SecurityIssue(
                        component_id=f"port_{port_info['port']}",
                        issue_type="risky_port_open",
                        description=f"风险端口 {port_info['port']} 处于开放状态",
                        security_level=SecurityLevel.MEDIUM,
                        recommendation=f"考虑关闭端口 {port_info['port']} 或限制访问",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
                    recommendations.append(f"审查端口 {port_info['port']} 的必要性")
        
        except Exception as e:
            self.logger.error(f"防火墙检查失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_ssl_certificates(self, target: str) -> Dict[str, Any]:
        """检查SSL证书"""
        issues = []
        recommendations = []
        
        common_ports = [443, 8443]
        
        for port in common_ports:
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((target, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=target) as ssock:
                        cert = ssock.getpeercert()
                        
                        # 检查证书有效期
                        if cert:
                            expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                            if expiry_date < datetime.now() + timedelta(days=30):
                                issue = SecurityIssue(
                                    component_id=f"ssl_cert_{port}",
                                    issue_type="certificate_expiring",
                                    description=f"端口 {port} 的SSL证书将在30天内过期",
                                    security_level=SecurityLevel.MEDIUM,
                                    recommendation="续订SSL证书",
                                    detected_at=datetime.now()
                                )
                                issues.append(issue)
                                recommendations.append(f"续订端口 {port} 的SSL证书")
                            
                            # 检查证书强度
                            if cert.get('subjectAltNames'):
                                # 检查是否使用了强加密算法
                                pass  # 需要更详细的证书分析
            
            except Exception as e:
                self.logger.error(f"SSL证书检查失败 (端口 {port}): {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_open_ports(self, target: str) -> Dict[str, Any]:
        """检查开放端口"""
        issues = []
        recommendations = []
        
        try:
            result = subprocess.run(['nmap', '-sS', '-O', target], capture_output=True, text=True)
            
            if result.returncode == 0:
                open_ports = self._parse_nmap_results(result.stdout)
                
                for port_info in open_ports:
                    port = port_info['port']
                    service = port_info.get('service', '')
                    version = port_info.get('version', '')
                    
                    # 检查是否为不必要的开放端口
                    if self._is_unnecessary_port(port, service):
                        issue = SecurityIssue(
                            component_id=f"port_{port}",
                            issue_type="unnecessary_port",
                            description=f"不必要的端口 {port} ({service}) 处于开放状态",
                            security_level=SecurityLevel.MEDIUM,
                            recommendation=f"关闭不必要的端口 {port}",
                            detected_at=datetime.now()
                        )
                        issues.append(issue)
                        recommendations.append(f"关闭端口 {port} ({service})")
                    
                    # 检查服务版本是否存在已知漏洞
                    if version and self._has_known_vulnerabilities(service, version):
                        issue = SecurityIssue(
                            component_id=f"service_{port}",
                            issue_type="vulnerable_service",
                            description=f"服务 {service} {version} 存在已知漏洞",
                            security_level=SecurityLevel.HIGH,
                            recommendation=f"升级 {service} 到最新版本",
                            detected_at=datetime.now()
                        )
                        issues.append(issue)
                        recommendations.append(f"升级 {service} 到最新版本")
        
        except Exception as e:
            self.logger.error(f"端口扫描失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_user_permissions(self, target: str) -> Dict[str, Any]:
        """检查用户权限"""
        issues = []
        recommendations = []
        
        try:
            # 检查是否有过多sudo用户
            result = subprocess.run(['getent', 'group', 'sudo'], capture_output=True, text=True)
            
            if result.returncode == 0:
                sudo_users = result.stdout.strip().split(':')[2].split(',')
                
                if len(sudo_users) > 5:  # 超过5个sudo用户
                    issue = SecurityIssue(
                        component_id="user_permissions",
                        issue_type="excessive_sudo_users",
                        description=f"系统有 {len(sudo_users)} 个sudo用户，可能存在安全风险",
                        security_level=SecurityLevel.MEDIUM,
                        recommendation="审查sudo用户权限，移除不必要的权限",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
                    recommendations.append("定期审查用户权限")
            
            # 检查是否有空密码用户
            try:
                result = subprocess.run(['awk', '-F:', '($2 == "") {print $1}', '/etc/shadow'], 
                                      capture_output=True, text=True)
                
                if result.stdout.strip():
                    issue = SecurityIssue(
                        component_id="user_accounts",
                        issue_type="empty_password_users",
                        description="存在空密码用户账户",
                        security_level=SecurityLevel.CRITICAL,
                        recommendation="为所有用户设置强密码",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
                    recommendations.append("立即为空密码用户设置密码")
            
            except Exception as e:
                self.logger.error(f"用户密码检查失败: {e}")
        
        except Exception as e:
            self.logger.error(f"用户权限检查失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_password_policy(self, target: str) -> Dict[str, Any]:
        """检查密码策略"""
        issues = []
        recommendations = []
        
        try:
            # 检查PAM密码策略配置
            pam_files = ['/etc/pam.d/common-password', '/etc/pam.d/system-auth']
            
            for pam_file in pam_files:
                try:
                    with open(pam_file, 'r') as f:
                        content = f.read()
                        
                        if 'pam_pwquality.so' not in content and 'pam_cracklib.so' not in content:
                            issue = SecurityIssue(
                                component_id="password_policy",
                                issue_type="weak_password_policy",
                                description=f"密码策略配置文件 {pam_file} 缺少强度检查",
                                security_level=SecurityLevel.MEDIUM,
                                recommendation="配置强密码策略",
                                detected_at=datetime.now()
                            )
                            issues.append(issue)
                            recommendations.append("实施密码复杂度要求")
                
                except FileNotFoundError:
                    continue
        
        except Exception as e:
            self.logger.error(f"密码策略检查失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_encryption_status(self, target: str) -> Dict[str, Any]:
        """检查加密状态"""
        issues = []
        recommendations = []
        
        try:
            # 检查磁盘加密
            result = subprocess.run(['lsblk', '-f'], capture_output=True, text=True)
            
            if 'crypto' not in result.stdout:
                issue = SecurityIssue(
                    component_id="disk_encryption",
                    issue_type="unencrypted_disk",
                    description="磁盘未加密",
                    security_level=SecurityLevel.MEDIUM,
                    recommendation="考虑实施磁盘加密",
                    detected_at=datetime.now()
                )
                issues.append(issue)
                recommendations.append("实施磁盘加密保护敏感数据")
            
            # 检查网络服务加密配置
            services = ['ssh', 'apache2', 'nginx', 'mysql']
            
            for service in services:
                try:
                    result = subprocess.run(['systemctl', 'is-active', service], 
                                          capture_output=True, text=True)
                    
                    if result.stdout.strip() == 'active':
                        # 检查服务配置文件中的加密设置
                        config_files = {
                            'ssh': '/etc/ssh/sshd_config',
                            'apache2': '/etc/apache2/apache2.conf',
                            'nginx': '/etc/nginx/nginx.conf',
                            'mysql': '/etc/mysql/my.cnf'
                        }
                        
                        config_file = config_files.get(service)
                        if config_file:
                            encryption_issues = self._check_service_encryption(service, config_file)
                            issues.extend(encryption_issues)
                
                except Exception as e:
                    self.logger.error(f"服务 {service} 检查失败: {e}")
        
        except Exception as e:
            self.logger.error(f"加密状态检查失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_access_logs(self, target: str) -> Dict[str, Any]:
        """检查访问日志"""
        issues = []
        recommendations = []
        
        log_files = [
            '/var/log/auth.log',
            '/var/log/secure',
            '/var/log/messages'
        ]
        
        for log_file in log_files:
            try:
                if not os.path.exists(log_file):
                    continue
                
                # 检查最近的登录失败
                result = subprocess.run(['grep', '-i', 'failed', log_file], 
                                      capture_output=True, text=True)
                
                failed_attempts = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                # 统计最近1小时的失败登录
                recent_failures = 0
                one_hour_ago = datetime.now() - timedelta(hours=1)
                
                for attempt in failed_attempts:
                    if attempt:
                        # 简单的时间检查（实际需要解析日志时间戳）
                        recent_failures += 1
                
                if recent_failures > 10:  # 超过10次失败登录
                    issue = SecurityIssue(
                        component_id="access_logs",
                        issue_type="excessive_failed_logins",
                        description=f"检测到 {recent_failures} 次失败登录尝试",
                        security_level=SecurityLevel.HIGH,
                        recommendation="调查异常登录尝试，考虑实施账户锁定策略",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
                    recommendations.append("实施账户锁定策略")
            
            except Exception as e:
                self.logger.error(f"日志文件 {log_file} 检查失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_system_updates(self, target: str) -> Dict[str, Any]:
        """检查系统更新"""
        issues = []
        recommendations = []
        
        try:
            # 检查可用更新
            result = subprocess.run(['apt', 'list', '--upgradable'], capture_output=True, text=True)
            
            if result.stdout.strip():
                updates = result.stdout.strip().split('\n')
                update_count = len([line for line in updates if line.strip()])
                
                if update_count > 0:
                    issue = SecurityIssue(
                        component_id="system_updates",
                        issue_type="pending_security_updates",
                        description=f"系统有 {update_count} 个待安装更新",
                        security_level=SecurityLevel.MEDIUM,
                        recommendation="安装系统更新以修复安全漏洞",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
                    recommendations.append("定期安装系统安全更新")
        
        except Exception as e:
            self.logger.error(f"系统更新检查失败: {e}")
        
        return {'issues': issues, 'recommendations': recommendations}
    
    def _check_compliance(self, standard: ComplianceStandard, target: str) -> ComplianceResult:
        """检查合规性"""
        violations = []
        recommendations = []
        
        if standard == ComplianceStandard.GDPR:
            # GDPR合规检查
            violations.extend(self._check_gdpr_compliance())
            recommendations.extend(self._get_gdpr_recommendations())
        
        elif standard == ComplianceStandard.PCI_DSS:
            # PCI DSS合规检查
            violations.extend(self._check_pci_dss_compliance())
            recommendations.extend(self._get_pci_dss_recommendations())
        
        # 计算合规评分
        score = self._calculate_compliance_score(standard, violations)
        
        return ComplianceResult(
            standard=standard,
            compliant=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            score=score
        )
    
    def _calculate_security_score(self, issues: List[SecurityIssue]) -> float:
        """计算安全评分"""
        if not issues:
            return 100.0
        
        # 根据问题严重程度计算评分
        total_deduction = 0
        for issue in issues:
            if issue.security_level == SecurityLevel.CRITICAL:
                total_deduction += 25
            elif issue.security_level == SecurityLevel.HIGH:
                total_deduction += 15
            elif issue.security_level == SecurityLevel.MEDIUM:
                total_deduction += 10
            elif issue.security_level == SecurityLevel.LOW:
                total_deduction += 5
        
        score = max(0, 100 - total_deduction)
        return score
    
    def _parse_open_ports(self, netstat_output: str) -> List[Dict[str, Any]]:
        """解析开放端口"""
        ports = []
        lines = netstat_output.split('\n')
        
        for line in lines:
            if 'LISTEN' in line:
                parts = line.split()
                if len(parts) >= 4:
                    address = parts[3]
                    if ':' in address:
                        ip, port = address.rsplit(':', 1)
                        ports.append({
                            'port': int(port),
                            'address': ip,
                            'protocol': parts[0]
                        })
        
        return ports
    
    def _is_risky_port(self, port: int) -> bool:
        """检查是否为风险端口"""
        risky_ports = [23, 135, 139, 445, 1433, 3389]
        return port in risky_ports
    
    def _is_unnecessary_port(self, port: int, service: str) -> bool:
        """检查是否为不必要的端口"""
        unnecessary_services = ['telnet', 'ftp', 'rsh', 'rlogin']
        return any(svc in service.lower() for svc in unnecessary_services)
    
    def _has_known_vulnerabilities(self, service: str, version: str) -> bool:
        """检查是否有已知漏洞（简化实现）"""
        # 这里应该连接到漏洞数据库
        # 简化实现：检查旧版本
        vulnerable_versions = {
            'apache': ['2.2.', '2.4.29'],
            'nginx': ['1.14.', '1.15.'],
            'openssh': ['7.4', '7.6']
        }
        
        for vuln_service, vuln_versions in vulnerable_versions.items():
            if vuln_service in service.lower():
                return any(vuln_version in version for vuln_version in vuln_versions)
        
        return False
    
    def _parse_nmap_results(self, nmap_output: str) -> List[Dict[str, Any]]:
        """解析nmap结果"""
        ports = []
        lines = nmap_output.split('\n')
        
        for line in lines:
            if '/tcp' in line and 'open' in line:
                parts = line.split()
                if len(parts) >= 3:
                    port_service = parts[0]
                    state = parts[1]
                    service_info = parts[2] if len(parts) > 2 else ''
                    
                    if '/' in port_service:
                        port, protocol = port_service.split('/')
                        ports.append({
                            'port': int(port),
                            'protocol': protocol,
                            'state': state,
                            'service': service_info
                        })
        
        return ports
    
    def _check_service_encryption(self, service: str, config_file: str) -> List[SecurityIssue]:
        """检查服务加密配置"""
        issues = []
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            if service == 'ssh':
                if 'Protocol 2' not in content:
                    issue = SecurityIssue(
                        component_id="ssh_config",
                        issue_type="weak_ssh_protocol",
                        description="SSH配置允许弱协议",
                        security_level=SecurityLevel.MEDIUM,
                        recommendation="配置SSH仅使用Protocol 2",
                        detected_at=datetime.now()
                    )
                    issues.append(issue)
        
        except Exception as e:
            self.logger.error(f"服务配置检查失败: {e}")
        
        return issues
    
    def _check_gdpr_compliance(self) -> List[str]:
        """检查GDPR合规性"""
        violations = []
        
        # 简化的GDPR检查
        violations.append("需要实施数据保护影响评估")
        violations.append("需要指定数据保护官")
        
        return violations
    
    def _get_gdpr_recommendations(self) -> List[str]:
        """获取GDPR建议"""
        return [
            "实施隐私设计原则",
            "建立数据保护管理制度",
            "定期进行数据保护培训"
        ]
    
    def _check_pci_dss_compliance(self) -> List[str]:
        """检查PCI DSS合规性"""
        violations = []
        
        # 简化的PCI DSS检查
        violations.append("需要实施网络分段")
        violations.append("需要加强访问控制")
        
        return violations
    
    def _get_pci_dss_recommendations(self) -> List[str]:
        """获取PCI DSS建议"""
        return [
            "实施防火墙配置",
            "加密敏感数据传输",
            "定期安全测试"
        ]
    
    def _calculate_compliance_score(self, standard: ComplianceStandard, violations: List[str]) -> float:
        """计算合规评分"""
        if not violations:
            return 100.0
        
        # 简化的评分计算
        deduction_per_violation = 10
        total_deduction = len(violations) * deduction_per_violation
        
        score = max(0, 100 - total_deduction)
        return score

# 使用示例
if __name__ == "__main__":
    analyzer = SecurityAnalyzer()
    
    # 运行安全扫描
    scan_results = analyzer.run_security_scan("localhost")
    
    print(f"安全评分: {scan_results['security_score']}")
    print(f"发现安全问题: {len(scan_results['security_issues'])}")
    print(f"合规性结果: {len(scan_results['compliance_results'])}")
```

## 使用示例

### 完整分析流程
```python
# complete_infrastructure_analysis.py
from architecture_analyzer import ArchitectureAnalyzer
from performance_analyzer import PerformanceAnalyzer
from security_analyzer import SecurityAnalyzer
import json
from datetime import datetime

def run_complete_infrastructure_analysis(target: str = "localhost") -> Dict[str, Any]:
    """运行完整的基础设施分析"""
    
    analysis_results = {
        'target': target,
        'analysis_time': datetime.now().isoformat(),
        'architecture_analysis': {},
        'performance_analysis': {},
        'security_analysis': {},
        'overall_score': 0.0,
        'recommendations': []
    }
    
    # 1. 架构分析
    arch_analyzer = ArchitectureAnalyzer()
    # 这里需要根据实际情况添加组件和连接
    topology_analysis = arch_analyzer.analyze_topology()
    spof = arch_analyzer.identify_single_points_of_failure()
    redundancy_score = arch_analyzer.calculate_redundancy_score()
    
    analysis_results['architecture_analysis'] = {
        'topology': topology_analysis,
        'single_points_of_failure': spof,
        'redundancy_score': redundancy_score,
        'complexity_score': arch_analyzer.calculate_complexity_score()
    }
    
    # 2. 性能分析
    perf_analyzer = PerformanceAnalyzer()
    perf_analyzer.start_monitoring(interval=30)
    
    # 监控一段时间
    import time
    time.sleep(120)  # 2分钟
    
    performance_summary = perf_analyzer.get_performance_summary()
    perf_analyzer.stop_monitoring()
    
    analysis_results['performance_analysis'] = performance_summary
    
    # 3. 安全分析
    sec_analyzer = SecurityAnalyzer()
    security_scan = sec_analyzer.run_security_scan(target)
    
    analysis_results['security_analysis'] = security_scan
    
    # 4. 计算总体评分
    arch_score = redundancy_score * 100  # 架构评分
    perf_score = performance_summary.get('current_metrics', {}).get('system_health', 80)
    sec_score = security_scan.get('security_score', 80)
    
    analysis_results['overall_score'] = (arch_score + perf_score + sec_score) / 3
    
    # 5. 生成综合建议
    analysis_results['recommendations'] = generate_comprehensive_recommendations(analysis_results)
    
    return analysis_results

def generate_comprehensive_recommendations(results: Dict[str, Any]) -> List[str]:
    """生成综合建议"""
    recommendations = []
    
    # 架构建议
    arch_analysis = results.get('architecture_analysis', {})
    if arch_analysis.get('redundancy_score', 0) < 0.8:
        recommendations.append("提高系统冗余度，消除单点故障")
    
    if arch_analysis.get('complexity_score', 0) > 0.7:
        recommendations.append("简化架构复杂度，优化组件依赖关系")
    
    # 性能建议
    perf_analysis = results.get('performance_analysis', {})
    recent_issues = perf_analysis.get('recent_issues', [])
    if recent_issues:
        recommendations.append("解决当前性能问题，优化资源使用")
    
    # 安全建议
    sec_analysis = results.get('security_analysis', {})
    if sec_analysis.get('security_score', 100) < 80:
        recommendations.append("加强安全配置，修复安全漏洞")
    
    return recommendations

# 使用示例
if __name__ == "__main__":
    results = run_complete_infrastructure_analysis()
    
    print(f"基础设施分析完成")
    print(f"总体评分: {results['overall_score']:.1f}")
    print(f"建议数量: {len(results['recommendations'])}")
    
    # 保存详细报告
    with open('infrastructure_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
```

这个基础设施分析器提供了全面的架构分析、性能监控、安全评估和成本优化功能，帮助构建可靠、高效、安全的基础设施架构。
