---
name: Docker容器化
description: "当实施Docker容器化时，分析容器架构设计，优化容器性能，解决容器相关问题。验证容器配置，设计微服务架构，和最佳实践。"
license: MIT
---

# Docker容器化技能

## 概述
Docker容器化是现代应用部署的核心技术。不当的容器化会导致资源浪费、性能问题和安全风险。在设计容器化方案前需要仔细分析应用需求。

**核心原则**: 好的容器化应该提升部署效率和可移植性，同时保证资源利用率。坏的容器化会增加运维复杂性，甚至影响应用性能。

## 何时使用

**始终:**
- 设计微服务架构时
- 实现应用容器化部署时
- 优化容器资源使用时
- 解决容器网络和存储问题时
- 建立容器编排策略时

**触发短语:**
- "Docker容器化"
- "容器性能优化"
- "Docker网络配置"
- "容器存储管理"
- "微服务容器化"
- "容器安全策略"

## Docker容器化功能

### 容器架构设计
- 单容器vs多容器架构
- 微服务拆分策略
- 容器依赖管理
- 服务发现机制
- 配置管理方案

### 容器资源管理
- CPU和内存限制
- 存储卷管理
- 网络配置优化
- 资源监控分析
- 自动扩缩容策略

### 容器网络管理
- 网络模式选择
- 服务网格配置
- 负载均衡设置
- 网络安全策略
- 跨主机通信

### 容器存储管理
- 数据卷类型选择
- 持久化存储方案
- 备份恢复策略
- 存储性能优化
- 数据迁移方案

## 常见Docker容器化问题

### 资源配置不当
```
问题:
容器资源配置不合理，导致性能问题

错误示例:
- CPU和内存限制过高或过低
- 没有设置资源限制
- 忽略资源使用监控
- 不合理的重启策略

解决方案:
1. 根据应用需求设置合理资源限制
2. 实施资源监控和告警
3. 优化容器启动参数
4. 配置合适的重启策略
```

### 网络配置错误
```
问题:
Docker网络配置不当导致通信问题

错误示例:
- 使用默认桥接网络
- 端口映射冲突
- DNS解析问题
- 网络安全配置缺失

解决方案:
1. 使用自定义网络
2. 合理规划端口映射
3. 配置DNS服务
4. 实施网络隔离和安全策略
```

### 存储管理问题
```
问题:
容器数据持久化和存储管理不当

错误示例:
- 数据存储在容器内部
- 没有备份策略
- 存储卷权限问题
- 存储空间不足

解决方案:
1. 使用数据卷持久化数据
2. 实施定期备份策略
3. 正确配置存储权限
4. 监控存储使用情况
```

## 代码实现示例

### Docker容器分析器
```python
import docker
import json
import time
import psutil
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ContainerMetrics:
    """容器指标"""
    container_id: str
    name: str
    status: str
    cpu_usage: float
    memory_usage: float
    memory_limit: float
    network_io: Dict[str, int]
    block_io: Dict[str, int]
    pid_count: int
    uptime: float

@dataclass
class ContainerIssue:
    """容器问题"""
    container_id: str
    severity: str  # critical, high, medium, low
    type: str
    message: str
    suggestion: str
    metric_value: Optional[float] = None

class DockerContainerAnalyzer:
    def __init__(self):
        self.client = docker.from_env()
        self.containers: List[ContainerMetrics] = []
        self.issues: List[ContainerIssue] = []
        
    def analyze_all_containers(self) -> Dict[str, Any]:
        """分析所有容器"""
        try:
            # 获取所有容器
            containers = self.client.containers.list(all=True)
            
            # 分析每个容器
            for container in containers:
                metrics = self.analyze_container(container.id)
                if metrics:
                    self.containers.append(metrics)
            
            # 生成分析报告
            report = {
                'total_containers': len(containers),
                'running_containers': len([c for c in containers if c.status == 'running']),
                'container_metrics': self.containers,
                'issues': self.issues,
                'resource_summary': self.generate_resource_summary(),
                'recommendations': self.generate_recommendations(),
                'health_score': self.calculate_health_score()
            }
            
            return report
            
        except Exception as e:
            return {'error': f'分析容器失败: {e}'}
    
    def analyze_container(self, container_id: str) -> Optional[ContainerMetrics]:
        """分析单个容器"""
        try:
            container = self.client.containers.get(container_id)
            
            # 获取容器统计信息
            stats = container.stats(stream=False)
            
            # 计算CPU使用率
            cpu_usage = self.calculate_cpu_usage(stats)
            
            # 计算内存使用
            memory_usage, memory_limit = self.calculate_memory_usage(stats)
            
            # 网络IO
            network_io = self.calculate_network_io(stats)
            
            # 块设备IO
            block_io = self.calculate_block_io(stats)
            
            # 进程数
            pid_count = stats.get('pids_stats', {}).get('current', 0)
            
            # 运行时间
            uptime = self.calculate_uptime(container)
            
            metrics = ContainerMetrics(
                container_id=container.id,
                name=container.name,
                status=container.status,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_limit=memory_limit,
                network_io=network_io,
                block_io=block_io,
                pid_count=pid_count,
                uptime=uptime
            )
            
            # 检查问题
            self.check_container_issues(metrics)
            
            return metrics
            
        except Exception as e:
            print(f'分析容器{container_id}失败: {e}')
            return None
    
    def calculate_cpu_usage(self, stats: Dict) -> float:
        """计算CPU使用率"""
        try:
            cpu_stats = stats.get('cpu_stats', {})
            precpu_stats = stats.get('precpu_stats', {})
            
            # CPU使用计算
            cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - \
                       precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
            
            system_cpu_delta = cpu_stats.get('system_cpu_usage', 0) - \
                              precpu_stats.get('system_cpu_usage', 0)
            
            if system_cpu_delta > 0:
                cpu_usage = (cpu_delta / system_cpu_delta) * \
                           len(cpu_stats.get('cpu_usage', {}).get('percpu_usage', [])) * 100
            else:
                cpu_usage = 0.0
            
            return round(cpu_usage, 2)
            
        except Exception:
            return 0.0
    
    def calculate_memory_usage(self, stats: Dict) -> Tuple[float, float]:
        """计算内存使用"""
        try:
            memory_stats = stats.get('memory_stats', {})
            
            memory_usage = memory_stats.get('usage', 0)
            memory_limit = memory_stats.get('limit', 0)
            
            return memory_usage, memory_limit
            
        except Exception:
            return 0.0, 0.0
    
    def calculate_network_io(self, stats: Dict) -> Dict[str, int]:
        """计算网络IO"""
        try:
            networks = stats.get('networks', {})
            
            total_rx = sum(net.get('rx_bytes', 0) for net in networks.values())
            total_tx = sum(net.get('tx_bytes', 0) for net in networks.values())
            
            return {
                'rx_bytes': total_rx,
                'tx_bytes': total_tx,
                'total_bytes': total_rx + total_tx
            }
            
        except Exception:
            return {'rx_bytes': 0, 'tx_bytes': 0, 'total_bytes': 0}
    
    def calculate_block_io(self, stats: Dict) -> Dict[str, int]:
        """计算块设备IO"""
        try:
            blkio_stats = stats.get('blkio_stats', {})
            io_service_bytes = blkio_stats.get('io_service_bytes_recursive', [])
            
            total_read = sum(item.get('value', 0) for item in io_service_bytes 
                           if item.get('op') == 'Read')
            total_write = sum(item.get('value', 0) for item in io_service_bytes 
                            if item.get('op') == 'Write')
            
            return {
                'read_bytes': total_read,
                'write_bytes': total_write,
                'total_bytes': total_read + total_write
            }
            
        except Exception:
            return {'read_bytes': 0, 'write_bytes': 0, 'total_bytes': 0}
    
    def calculate_uptime(self, container) -> float:
        """计算容器运行时间"""
        try:
            if container.status == 'running':
                # 获取容器启动时间
                info = container.attrs
                started_at = info.get('State', {}).get('StartedAt', '')
                if started_at:
                    start_time = time.strptime(started_at[:19], '%Y-%m-%dT%H:%M:%S')
                    uptime = time.time() - time.mktime(start_time)
                    return uptime
            return 0.0
            
        except Exception:
            return 0.0
    
    def check_container_issues(self, metrics: ContainerMetrics) -> None:
        """检查容器问题"""
        # 检查CPU使用率
        if metrics.cpu_usage > 80:
            self.issues.append(ContainerIssue(
                container_id=metrics.container_id,
                severity='high',
                type='cpu_high',
                message=f'容器CPU使用率过高: {metrics.cpu_usage}%',
                suggestion='检查容器内进程，考虑增加CPU限制或优化应用',
                metric_value=metrics.cpu_usage
            ))
        
        # 检查内存使用率
        if metrics.memory_limit > 0:
            memory_percent = (metrics.memory_usage / metrics.memory_limit) * 100
            if memory_percent > 85:
                self.issues.append(ContainerIssue(
                    container_id=metrics.container_id,
                    severity='high',
                    type='memory_high',
                    message=f'容器内存使用率过高: {memory_percent:.2f}%',
                    suggestion='检查内存泄漏，增加内存限制或优化应用',
                    metric_value=memory_percent
                ))
        
        # 检查容器状态
        if metrics.status == 'exited':
            self.issues.append(ContainerIssue(
                container_id=metrics.container_id,
                severity='medium',
                type='container_exited',
                message='容器已退出',
                suggestion='检查容器日志，确定退出原因并重启'
            ))
        
        # 检查进程数
        if metrics.pid_count > 100:
            self.issues.append(ContainerIssue(
                container_id=metrics.container_id,
                severity='medium',
                type='high_pid_count',
                message=f'容器进程数过多: {metrics.pid_count}',
                suggestion='检查是否有僵尸进程或进程泄漏',
                metric_value=metrics.pid_count
            ))
    
    def generate_resource_summary(self) -> Dict[str, Any]:
        """生成资源摘要"""
        if not self.containers:
            return {}
        
        total_cpu = sum(c.cpu_usage for c in self.containers)
        total_memory = sum(c.memory_usage for c in self.containers)
        total_memory_limit = sum(c.memory_limit for c in self.containers if c.memory_limit > 0)
        
        running_containers = [c for c in self.containers if c.status == 'running']
        
        return {
            'total_cpu_usage': total_cpu,
            'total_memory_usage': total_memory,
            'total_memory_limit': total_memory_limit,
            'memory_utilization': (total_memory / total_memory_limit * 100) if total_memory_limit > 0 else 0,
            'running_containers': len(running_containers),
            'average_cpu_per_container': total_cpu / len(running_containers) if running_containers else 0,
            'average_memory_per_container': total_memory / len(running_containers) if running_containers else 0
        }
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 基于问题生成建议
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue.type] += 1
        
        if issue_counts['cpu_high'] > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'resource_optimization',
                'message': f'{issue_counts["cpu_high"]}个容器CPU使用率过高',
                'suggestion': '检查CPU密集型应用，考虑水平扩展或优化算法'
            })
        
        if issue_counts['memory_high'] > 0:
            recommendations.append({
                'priority': 'high',
                'type': 'resource_optimization',
                'message': f'{issue_counts["memory_high"]}个容器内存使用率过高',
                'suggestion': '检查内存泄漏，增加内存限制或优化内存使用'
            })
        
        # 通用建议
        resource_summary = self.generate_resource_summary()
        if resource_summary.get('memory_utilization', 0) > 80:
            recommendations.append({
                'priority': 'medium',
                'type': 'capacity_planning',
                'message': '整体内存利用率过高',
                'suggestion': '考虑增加主机内存或优化容器资源分配'
            })
        
        return recommendations
    
    def calculate_health_score(self) -> int:
        """计算健康评分"""
        if not self.containers:
            return 0
        
        score = 100
        
        # 根据问题扣分
        for issue in self.issues:
            if issue.severity == 'critical':
                score -= 20
            elif issue.severity == 'high':
                score -= 10
            elif issue.severity == 'medium':
                score -= 5
            elif issue.severity == 'low':
                score -= 2
        
        # 根据容器状态调整
        running_containers = len([c for c in self.containers if c.status == 'running'])
        total_containers = len(self.containers)
        
        if total_containers > 0:
            running_ratio = running_containers / total_containers
            score = score * running_ratio
        
        return max(0, int(score))

# Docker网络管理器
class DockerNetworkManager:
    def __init__(self):
        self.client = docker.from_env()
        
    def analyze_networks(self) -> Dict[str, Any]:
        """分析Docker网络"""
        try:
            networks = self.client.networks.list()
            
            network_analysis = []
            for network in networks:
                analysis = {
                    'name': network.name,
                    'id': network.id,
                    'driver': network.attrs.get('Driver', 'unknown'),
                    'scope': network.attrs.get('Scope', 'local'),
                    'containers': len(network.attrs.get('Containers', {})),
                    'internal': network.attrs.get('Internal', False),
                    'issues': []
                }
                
                # 检查网络问题
                if analysis['driver'] == 'bridge' and analysis['name'] == 'bridge':
                    analysis['issues'].append({
                        'severity': 'medium',
                        'message': '使用默认bridge网络',
                        'suggestion': '创建自定义网络提高安全性'
                    })
                
                if analysis['containers'] > 50:
                    analysis['issues'].append({
                        'severity': 'low',
                        'message': '网络中容器数量较多',
                        'suggestion': '考虑拆分网络减少广播域'
                    })
                
                network_analysis.append(analysis)
            
            return {
                'total_networks': len(networks),
                'networks': network_analysis,
                'recommendations': self.generate_network_recommendations(network_analysis)
            }
            
        except Exception as e:
            return {'error': f'分析网络失败: {e}'}
    
    def generate_network_recommendations(self, networks: List[Dict]) -> List[Dict[str, str]]:
        """生成网络优化建议"""
        recommendations = []
        
        bridge_networks = len([n for n in networks if n['driver'] == 'bridge'])
        overlay_networks = len([n for n in networks if n['driver'] == 'overlay'])
        
        if bridge_networks > 5:
            recommendations.append({
                'priority': 'medium',
                'message': 'bridge网络数量较多',
                'suggestion': '考虑使用overlay网络实现跨主机通信'
            })
        
        if overlay_networks == 0 and len(networks) > 1:
            recommendations.append({
                'priority': 'low',
                'message': '没有使用overlay网络',
                'suggestion': '在多主机环境中考虑使用overlay网络'
            })
        
        return recommendations

# Docker存储管理器
class DockerStorageManager:
    def __init__(self):
        self.client = docker.from_env()
        
    def analyze_volumes(self) -> Dict[str, Any]:
        """分析Docker存储卷"""
        try:
            volumes = self.client.volumes.list()
            
            volume_analysis = []
            for volume in volumes:
                analysis = {
                    'name': volume.name,
                    'driver': volume.attrs.get('Driver', 'local'),
                    'mountpoint': volume.attrs.get('Mountpoint', ''),
                    'created': volume.attrs.get('CreatedAt', ''),
                    'labels': volume.attrs.get('Labels', {}),
                    'usage': self.estimate_volume_usage(volume),
                    'issues': []
                }
                
                # 检查存储卷问题
                if analysis['driver'] == 'local':
                    analysis['issues'].append({
                        'severity': 'low',
                        'message': '使用本地存储卷',
                        'suggestion': '考虑使用分布式存储提高可用性'
                    })
                
                volume_analysis.append(analysis)
            
            return {
                'total_volumes': len(volumes),
                'volumes': volume_analysis,
                'recommendations': self.generate_storage_recommendations(volume_analysis)
            }
            
        except Exception as e:
            return {'error': f'分析存储卷失败: {e}'}
    
    def estimate_volume_usage(self, volume) -> Dict[str, Any]:
        """估算存储卷使用情况"""
        try:
            mountpoint = volume.attrs.get('Mountpoint', '')
            if mountpoint and os.path.exists(mountpoint):
                stat = os.statvfs(mountpoint)
                total = stat.f_blocks * stat.f_frsize
                free = stat.f_bfree * stat.f_frsize
                used = total - free
                
                return {
                    'total': total,
                    'used': used,
                    'free': free,
                    'usage_percent': (used / total * 100) if total > 0 else 0
                }
        except Exception:
            pass
        
        return {'total': 0, 'used': 0, 'free': 0, 'usage_percent': 0}
    
    def generate_storage_recommendations(self, volumes: List[Dict]) -> List[Dict[str, str]]:
        """生成存储优化建议"""
        recommendations = []
        
        local_volumes = len([v for v in volumes if v['driver'] == 'local'])
        
        if local_volumes > 10:
            recommendations.append({
                'priority': 'medium',
                'message': '本地存储卷数量较多',
                'suggestion': '考虑使用网络存储提高数据可用性'
            })
        
        # 检查使用率高的存储卷
        high_usage_volumes = [v for v in volumes if v['usage'].get('usage_percent', 0) > 80]
        if high_usage_volumes:
            recommendations.append({
                'priority': 'high',
                'message': f'{len(high_usage_volumes)}个存储卷使用率过高',
                'suggestion': '清理无用数据或扩展存储容量'
            })
        
        return recommendations

# 使用示例
def main():
    # 容器分析
    container_analyzer = DockerContainerAnalyzer()
    container_report = container_analyzer.analyze_all_containers()
    
    print("容器分析报告:")
    print(f"总容器数: {container_report['total_containers']}")
    print(f"运行中容器: {container_report['running_containers']}")
    print(f"健康评分: {container_report['health_score']}")
    
    # 网络分析
    network_manager = DockerNetworkManager()
    network_report = network_manager.analyze_networks()
    
    print(f"\n网络分析报告:")
    print(f"总网络数: {network_report['total_networks']}")
    
    # 存储分析
    storage_manager = DockerStorageManager()
    storage_report = storage_manager.analyze_volumes()
    
    print(f"\n存储分析报告:")
    print(f"总存储卷数: {storage_report['total_volumes']}")

if __name__ == '__main__':
    main()
```

### Docker容器优化器
```python
import docker
import yaml
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class DockerContainerOptimizer:
    def __init__(self):
        self.client = docker.from_env()
        self.optimizations = []
        
    def optimize_container_config(self, container_name: str) -> Dict[str, Any]:
        """优化容器配置"""
        try:
            container = self.client.containers.get(container_name)
            
            # 获取当前配置
            current_config = self.get_container_config(container)
            
            # 分析优化建议
            optimization_plan = self.analyze_optimization_opportunities(current_config)
            
            # 生成优化后的配置
            optimized_config = self.generate_optimized_config(current_config, optimization_plan)
            
            return {
                'container_name': container_name,
                'current_config': current_config,
                'optimization_plan': optimization_plan,
                'optimized_config': optimized_config,
                'estimated_improvements': self.estimate_improvements(current_config, optimized_config)
            }
            
        except Exception as e:
            return {'error': f'优化容器配置失败: {e}'}
    
    def get_container_config(self, container) -> Dict[str, Any]:
        """获取容器配置"""
        try:
            info = container.attrs
            
            config = {
                'name': container.name,
                'image': info.get('Config', {}).get('Image', ''),
                'cmd': info.get('Config', {}).get('Cmd', []),
                'env': info.get('Config', {}).get('Env', []),
                'ports': info.get('NetworkSettings', {}).get('Ports', {}),
                'volumes': info.get('Mounts', []),
                'restart_policy': info.get('HostConfig', {}).get('RestartPolicy', {}),
                'resources': {
                    'cpu_limit': info.get('HostConfig', {}).get('CpuQuota', 0),
                    'memory_limit': info.get('HostConfig', {}).get('Memory', 0),
                    'cpu_shares': info.get('HostConfig', {}).get('CpuShares', 0)
                },
                'network_mode': info.get('HostConfig', {}).get('NetworkMode', ''),
                'privileged': info.get('HostConfig', {}).get('Privileged', False),
                'readonly': info.get('HostConfig', {}).get('ReadonlyRootfs', False)
            }
            
            return config
            
        except Exception as e:
            raise Exception(f'获取容器配置失败: {e}')
    
    def analyze_optimization_opportunities(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析优化机会"""
        opportunities = []
        
        # 检查资源限制
        if config['resources']['memory_limit'] == 0:
            opportunities.append({
                'type': 'resource_limit',
                'priority': 'high',
                'message': '没有设置内存限制',
                'suggestion': '设置合理的内存限制防止资源耗尽',
                'impact': 'security'
            })
        
        if config['resources']['cpu_limit'] == 0:
            opportunities.append({
                'type': 'resource_limit',
                'priority': 'medium',
                'message': '没有设置CPU限制',
                'suggestion': '设置CPU限制确保公平调度',
                'impact': 'performance'
            })
        
        # 检查安全配置
        if config['privileged']:
            opportunities.append({
                'type': 'security',
                'priority': 'critical',
                'message': '容器以特权模式运行',
                'suggestion': '避免使用特权模式，最小化权限',
                'impact': 'security'
            })
        
        if not config['readonly']:
            opportunities.append({
                'type': 'security',
                'priority': 'medium',
                'message': '根文件系统可写',
                'suggestion': '考虑使用只读根文件系统',
                'impact': 'security'
            })
        
        # 检查重启策略
        restart_policy = config.get('restart_policy', {})
        if restart_policy.get('Name') == 'no':
            opportunities.append({
                'type': 'reliability',
                'priority': 'high',
                'message': '没有设置重启策略',
                'suggestion': '设置合适的重启策略提高可用性',
                'impact': 'reliability'
            })
        
        # 检查网络配置
        if config['network_mode'] == 'bridge':
            opportunities.append({
                'type': 'network',
                'priority': 'medium',
                'message': '使用默认bridge网络',
                'suggestion': '使用自定义网络提高网络性能和安全性',
                'impact': 'network'
            })
        
        # 检查环境变量
        sensitive_env_vars = []
        for env in config['env']:
            if any(key in env.upper() for key in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
                sensitive_env_vars.append(env)
        
        if sensitive_env_vars:
            opportunities.append({
                'type': 'security',
                'priority': 'high',
                'message': '环境变量包含敏感信息',
                'suggestion': '使用Docker secrets或配置文件管理敏感信息',
                'impact': 'security'
            })
        
        return opportunities
    
    def generate_optimized_config(self, current_config: Dict[str, Any], 
                                opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成优化后的配置"""
        optimized_config = current_config.copy()
        
        # 应用优化建议
        for opportunity in opportunities:
            if opportunity['type'] == 'resource_limit':
                if opportunity['message'] == '没有设置内存限制':
                    optimized_config['resources']['memory_limit'] = 512 * 1024 * 1024  # 512MB
                elif opportunity['message'] == '没有设置CPU限制':
                    optimized_config['resources']['cpu_limit'] = 50000  # 0.5 core
            
            elif opportunity['type'] == 'security':
                if opportunity['message'] == '容器以特权模式运行':
                    optimized_config['privileged'] = False
                elif opportunity['message'] == '根文件系统可写':
                    optimized_config['readonly'] = True
            
            elif opportunity['type'] == 'reliability':
                if opportunity['message'] == '没有设置重启策略':
                    optimized_config['restart_policy'] = {
                        'Name': 'unless-stopped',
                        'MaximumRetryCount': 0
                    }
            
            elif opportunity['type'] == 'network':
                if opportunity['message'] == '使用默认bridge网络':
                    optimized_config['network_mode'] = 'custom_network'
        
        return optimized_config
    
    def estimate_improvements(self, current_config: Dict[str, Any], 
                            optimized_config: Dict[str, Any]) -> Dict[str, Any]:
        """估算改进效果"""
        improvements = {
            'security_score': 0,
            'performance_score': 0,
            'reliability_score': 0,
            'overall_score': 0
        }
        
        # 安全改进
        if current_config['privileged'] and not optimized_config['privileged']:
            improvements['security_score'] += 30
        
        if not current_config['readonly'] and optimized_config['readonly']:
            improvements['security_score'] += 15
        
        if current_config['resources']['memory_limit'] == 0 and optimized_config['resources']['memory_limit'] > 0:
            improvements['security_score'] += 20
            improvements['performance_score'] += 10
        
        # 可靠性改进
        restart_policy = current_config.get('restart_policy', {}).get('Name', 'no')
        optimized_restart_policy = optimized_config.get('restart_policy', {}).get('Name', 'no')
        if restart_policy == 'no' and optimized_restart_policy != 'no':
            improvements['reliability_score'] += 25
        
        # 性能改进
        if current_config['network_mode'] == 'bridge' and optimized_config['network_mode'] != 'bridge':
            improvements['performance_score'] += 15
        
        # 计算总体改进
        improvements['overall_score'] = (
            improvements['security_score'] + 
            improvements['performance_score'] + 
            improvements['reliability_score']
        ) // 3
        
        return improvements
    
    def generate_docker_compose_optimization(self, compose_file: str) -> Dict[str, Any]:
        """优化docker-compose文件"""
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                compose_content = yaml.safe_load(f)
            
            optimizations = []
            
            # 分析每个服务
            services = compose_content.get('services', {})
            for service_name, service_config in services.items():
                service_optimizations = self.analyze_service_config(service_name, service_config)
                optimizations.extend(service_optimizations)
            
            # 生成优化建议
            optimized_compose = self.generate_optimized_compose(compose_content, optimizations)
            
            return {
                'original_compose': compose_content,
                'optimizations': optimizations,
                'optimized_compose': optimized_compose,
                'summary': {
                    'total_optimizations': len(optimizations),
                    'critical_issues': len([o for o in optimizations if o['priority'] == 'critical']),
                    'high_issues': len([o for o in optimizations if o['priority'] == 'high'])
                }
            }
            
        except Exception as e:
            return {'error': f'优化docker-compose文件失败: {e}'}
    
    def analyze_service_config(self, service_name: str, service_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析服务配置"""
        optimizations = []
        
        # 检查部署配置
        deploy_config = service_config.get('deploy', {})
        if not deploy_config.get('resources'):
            optimizations.append({
                'service': service_name,
                'type': 'resources',
                'priority': 'high',
                'message': '没有设置资源限制',
                'suggestion': '在deploy配置中添加resources限制'
            })
        
        # 检查健康检查
        if not service_config.get('healthcheck'):
            optimizations.append({
                'service': service_name,
                'type': 'health',
                'priority': 'medium',
                'message': '没有设置健康检查',
                'suggestion': '添加healthcheck配置监控服务状态'
            })
        
        # 检查日志配置
        logging_config = service_config.get('logging', {})
        if not logging_config.get('driver'):
            optimizations.append({
                'service': service_name,
                'type': 'logging',
                'priority': 'low',
                'message': '没有配置日志驱动',
                'suggestion': '配置日志驱动和日志轮转策略'
            })
        
        return optimizations
    
    def generate_optimized_compose(self, original_compose: Dict[str, Any], 
                                 optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成优化后的compose文件"""
        optimized_compose = original_compose.copy()
        
        # 应用优化建议
        services = optimized_compose.get('services', {})
        
        for optimization in optimizations:
            service_name = optimization['service']
            service_config = services.get(service_name, {})
            
            if optimization['type'] == 'resources':
                if 'deploy' not in service_config:
                    service_config['deploy'] = {}
                service_config['deploy']['resources'] = {
                    'limits': {
                        'cpus': '0.5',
                        'memory': '512M'
                    },
                    'reservations': {
                        'cpus': '0.25',
                        'memory': '256M'
                    }
                }
            
            elif optimization['type'] == 'health':
                service_config['healthcheck'] = {
                    'test': ['CMD', 'curl', '-f', 'http://localhost/health'],
                    'interval': '30s',
                    'timeout': '10s',
                    'retries': 3
                }
            
            elif optimization['type'] == 'logging':
                service_config['logging'] = {
                    'driver': 'json-file',
                    'options': {
                        'max-size': '10m',
                        'max-file': '3'
                    }
                }
            
            services[service_name] = service_config
        
        optimized_compose['services'] = services
        
        return optimized_compose

# 使用示例
def main():
    optimizer = DockerContainerOptimizer()
    
    # 优化单个容器
    container_optimization = optimizer.optimize_container_config('my_container')
    print("容器优化建议:")
    for opt in container_optimization['optimization_plan']:
        print(f"- {opt['message']}: {opt['suggestion']}")
    
    # 优化docker-compose
    compose_optimization = optimizer.generate_docker_compose_optimization('docker-compose.yml')
    print(f"\nDocker Compose优化:")
    print(f"总优化项: {compose_optimization['summary']['total_optimizations']}")

if __name__ == '__main__':
    main()
```

## Docker容器化最佳实践

### 容器设计
1. **单一职责**: 每个容器运行单一进程
2. **无状态设计**: 避免在容器内存储状态
3. **配置外部化**: 使用环境变量或配置文件
4. **优雅关闭**: 处理SIGTERM信号

### 资源管理
1. **合理限制**: 设置CPU和内存限制
2. **监控告警**: 实施资源监控和告警
3. **自动扩缩**: 根据负载自动调整
4. **资源优化**: 定期优化资源配置

### 安全实践
1. **最小权限**: 使用非root用户运行
2. **镜像安全**: 使用可信基础镜像
3. **网络隔离**: 使用自定义网络
4. **扫描漏洞**: 定期扫描安全漏洞

### 运维管理
1. **健康检查**: 配置容器健康检查
2. **重启策略**: 设置合适的重启策略
3. **日志管理**: 配置日志收集和轮转
4. **备份恢复**: 制定备份恢复策略

## 相关技能

- **container-registry** - 容器镜像管理
- **kubernetes-basics** - Kubernetes基础
- **microservices** - 微服务架构
- **ci-cd-pipeline** - CI/CD流水线
