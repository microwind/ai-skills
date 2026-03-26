# Docker容器化参考文档

## Docker容器化概述

### 什么是Docker容器化
Docker容器化是一种轻量级的虚拟化技术，通过将应用程序及其依赖项打包到容器中，实现应用的快速部署、扩展和管理。Docker容器基于操作系统级别的虚拟化，共享主机内核，相比传统虚拟机具有更小的资源开销和更快的启动速度。容器化技术已成为现代云原生应用开发的核心基础设施。

### 主要优势
- **环境一致性**: 确保开发、测试、生产环境的一致性
- **快速部署**: 容器启动时间通常在秒级，大大提升部署效率
- **资源隔离**: 提供CPU、内存、网络、存储等资源的隔离
- **可移植性**: 容器可以在任何支持Docker的环境中运行
- **版本管理**: 支持镜像的版本控制和回滚
- **微服务支持**: 天然适合微服务架构的部署和管理

## Docker容器化核心

### Docker容器引擎
```python
# docker_containerizer.py
import os
import json
import yaml
import time
import uuid
import logging
import threading
import queue
import hashlib
import subprocess
import docker
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import requests
import tarfile
import tempfile
import shutil

class ContainerStatus(Enum):
    """容器状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    RESTARTING = "restarting"
    REMOVING = "removing"
    EXITED = "exited"
    DEAD = "dead"

class BuildStrategy(Enum):
    """构建策略枚举"""
    SINGLE_STAGE = "single_stage"
    MULTI_STAGE = "multi_stage"
    PARALLEL = "parallel"
    CUSTOM = "custom"

@dataclass
class ContainerImage:
    """容器镜像"""
    image_id: str
    name: str
    tag: str
    size_bytes: int
    created_at: datetime
    author: str = ""
    architecture: str = "amd64"
    os: str = "linux"
    layers: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    exposed_ports: List[str] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)
    working_dir: str = ""
    cmd: List[str] = field(default_factory=list)
    entrypoint: List[str] = field(default_factory=list)

@dataclass
class ContainerConfig:
    """容器配置"""
    container_id: str
    name: str
    image: str
    status: ContainerStatus
    created_at: datetime
    started_at: Optional[datetime]
    ports: Dict[str, Any] = field(default_factory=dict)
    volumes: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    restart_policy: str = "no"
    network_mode: str = "bridge"
    cpu_limit: Optional[float] = None
    memory_limit: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    health_check: Optional[Dict[str, Any]] = None

@dataclass
class BuildContext:
    """构建上下文"""
    context_id: str
    dockerfile_path: str
    build_context_path: str
    build_args: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    target: Optional[str] = None
    no_cache: bool = False
    pull: bool = False
    rm: bool = True

@dataclass
class NetworkConfig:
    """网络配置"""
    network_id: str
    name: str
    driver: str = "bridge"
    subnet: Optional[str] = None
    gateway: Optional[str] = None
    ip_range: Optional[str] = None
    internal: bool = False
    enable_ipv6: bool = False
    labels: Dict[str, str] = field(default_factory=dict)

class DockerfileGenerator:
    """Dockerfile生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.instructions = []
    
    def add_from(self, base_image: str, as_name: str = None):
        """添加FROM指令"""
        instruction = f"FROM {base_image}"
        if as_name:
            instruction += f" AS {as_name}"
        self.instructions.append(instruction)
    
    def add_workdir(self, path: str):
        """添加WORKDIR指令"""
        self.instructions.append(f"WORKDIR {path}")
    
    def add_copy(self, source: str, destination: str, from_stage: str = None):
        """添加COPY指令"""
        instruction = f"COPY {source} {destination}"
        if from_stage:
            instruction = f"COPY --from={from_stage} {source} {destination}"
        self.instructions.append(instruction)
    
    def add_add(self, source: str, destination: str):
        """添加ADD指令"""
        self.instructions.append(f"ADD {source} {destination}")
    
    def add_run(self, command: Union[str, List[str]], shell: bool = True):
        """添加RUN指令"""
        if isinstance(command, list):
            command_str = " && ".join(command)
        else:
            command_str = command
        
        if shell:
            self.instructions.append(f"RUN {command_str}")
        else:
            self.instructions.append(f"RUN {command_str}")
    
    def add_env(self, key: str, value: str):
        """添加ENV指令"""
        self.instructions.append(f"ENV {key}={value}")
    
    def add_expose(self, port: Union[int, str]):
        """添加EXPOSE指令"""
        self.instructions.append(f"EXPOSE {port}")
    
    def add_user(self, user: str):
        """添加USER指令"""
        self.instructions.append(f"USER {user}")
    
    def add_volume(self, path: str):
        """添加VOLUME指令"""
        self.instructions.append(f"VOLUME {path}")
    
    def add_cmd(self, command: Union[str, List[str]]):
        """添加CMD指令"""
        if isinstance(command, list):
            cmd_str = json.dumps(command)
        else:
            cmd_str = f'"{command}"'
        self.instructions.append(f"CMD {cmd_str}")
    
    def add_entrypoint(self, command: Union[str, List[str]]):
        """添加ENTRYPOINT指令"""
        if isinstance(command, list):
            entrypoint_str = json.dumps(command)
        else:
            entrypoint_str = f'"{command}"'
        self.instructions.append(f"ENTRYPOINT {entrypoint_str}")
    
    def add_label(self, key: str, value: str):
        """添加LABEL指令"""
        self.instructions.append(f"LABEL {key}={value}")
    
    def add_arg(self, key: str, default_value: str = None):
        """添加ARG指令"""
        if default_value:
            self.instructions.append(f"ARG {key}={default_value}")
        else:
            self.instructions.append(f"ARG {key}")
    
    def add_healthcheck(self, command: str, interval: str = None, timeout: str = None, 
                       retries: int = None, start_period: str = None):
        """添加HEALTHCHECK指令"""
        instruction = f"HEALTHCHECK CMD {command}"
        
        options = []
        if interval:
            options.append(f"--interval={interval}")
        if timeout:
            options.append(f"--timeout={timeout}")
        if retries:
            options.append(f"--retries={retries}")
        if start_period:
            options.append(f"--start-period={start_period}")
        
        if options:
            instruction = f"HEALTHCHECK {' '.join(options)} CMD {command}"
        
        self.instructions.append(instruction)
    
    def generate_dockerfile(self) -> str:
        """生成Dockerfile内容"""
        return "\n".join(self.instructions)
    
    def save_dockerfile(self, file_path: str):
        """保存Dockerfile到文件"""
        dockerfile_content = self.generate_dockerfile()
        
        with open(file_path, 'w') as f:
            f.write(dockerfile_content)
        
        self.logger.info(f"Dockerfile已保存到: {file_path}")

class DockerBuilder:
    """Docker构建器"""
    
    def __init__(self, docker_client=None):
        self.docker_client = docker_client or docker.from_env()
        self.logger = logging.getLogger(__name__)
    
    def build_image(self, build_context: BuildContext) -> ContainerImage:
        """构建镜像"""
        try:
            self.logger.info(f"开始构建镜像: {build_context.tags}")
            
            # 准备构建参数
            build_params = {
                'path': build_context.build_context_path,
                'dockerfile': build_context.dockerfile_path,
                'tag': ','.join(build_context.tags),
                'buildargs': build_context.build_args,
                'labels': build_context.labels,
                'nocache': build_context.no_cache,
                'pull': build_context.pull,
                'rm': build_context.rm
            }
            
            if build_context.target:
                build_params['target'] = build_context.target
            
            # 构建镜像
            image, build_logs = self.docker_client.images.build(**build_params)
            
            # 解析构建日志
            for log in build_logs:
                if 'stream' in log:
                    self.logger.info(log['stream'].strip())
            
            # 创建镜像对象
            container_image = ContainerImage(
                image_id=image.id,
                name=image.tags[0] if image.tags else "",
                tag=image.tags[0].split(':')[-1] if image.tags else "",
                size_bytes=image.attrs['Size'],
                created_at=datetime.strptime(image.attrs['Created'][:-4], '%Y-%m-%dT%H:%M:%S'),
                author=image.attrs.get('Author', ''),
                architecture=image.attrs.get('Architecture', 'amd64'),
                os=image.attrs.get('Os', 'linux'),
                layers=[layer['Id'] for layer in image.attrs.get('RootFS', {}).get('Layers', [])],
                labels=image.attrs.get('Config', {}).get('Labels', {}),
                environment=image.attrs.get('Config', {}).get('Env', []),
                exposed_ports=list(image.attrs.get('Config', {}).get('ExposedPorts', {}).keys()),
                volumes=list(image.attrs.get('Config', {}).get('Volumes', {}).keys()),
                working_dir=image.attrs.get('Config', {}).get('WorkingDir', ''),
                cmd=image.attrs.get('Config', {}).get('Cmd', []),
                entrypoint=image.attrs.get('Config', {}).get('Entrypoint', [])
            )
            
            self.logger.info(f"镜像构建完成: {container_image.name}")
            return container_image
        
        except Exception as e:
            self.logger.error(f"构建镜像失败: {e}")
            raise
    
    def build_multi_architecture(self, build_context: BuildContext, platforms: List[str]) -> List[ContainerImage]:
        """构建多架构镜像"""
        images = []
        
        try:
            for platform in platforms:
                self.logger.info(f"构建 {platform} 架构镜像")
                
                # 设置平台特定的构建参数
                platform_build_context = BuildContext(
                    context_id=str(uuid.uuid4()),
                    dockerfile_path=build_context.dockerfile_path,
                    build_context_path=build_context.build_context_path,
                    build_args=build_context.build_args.copy(),
                    labels=build_context.labels.copy(),
                    tags=[f"{tag}-{platform}" for tag in build_context.tags],
                    target=build_context.target,
                    no_cache=build_context.no_cache,
                    pull=build_context.pull,
                    rm=build_context.rm
                )
                
                # 添加平台特定的构建参数
                platform_build_context.build_args['TARGETPLATFORM'] = platform
                
                # 构建镜像
                image = self.build_image(platform_build_context)
                images.append(image)
            
            self.logger.info(f"多架构镜像构建完成，共 {len(images)} 个")
            return images
        
        except Exception as e:
            self.logger.error(f"构建多架构镜像失败: {e}")
            raise
    
    def push_image(self, image: ContainerImage, registry: str = None) -> bool:
        """推送镜像"""
        try:
            self.logger.info(f"推送镜像: {image.name}")
            
            # 构建完整的镜像名称
            full_image_name = image.name
            if registry:
                full_image_name = f"{registry}/{image.name}"
            
            # 推送镜像
            push_logs = self.docker_client.images.push(full_image_name, tag=image.tag)
            
            # 解析推送日志
            for log in push_logs:
                if 'status' in log:
                    self.logger.info(log['status'])
            
            self.logger.info(f"镜像推送完成: {full_image_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"推送镜像失败: {e}")
            return False
    
    def pull_image(self, image_name: str, tag: str = "latest") -> ContainerImage:
        """拉取镜像"""
        try:
            self.logger.info(f"拉取镜像: {image_name}:{tag}")
            
            # 拉取镜像
            image = self.docker_client.images.pull(image_name, tag=tag)
            
            # 创建镜像对象
            container_image = ContainerImage(
                image_id=image.id,
                name=f"{image_name}:{tag}",
                tag=tag,
                size_bytes=image.attrs['Size'],
                created_at=datetime.strptime(image.attrs['Created'][:-4], '%Y-%m-%dT%H:%M:%S'),
                author=image.attrs.get('Author', ''),
                architecture=image.attrs.get('Architecture', 'amd64'),
                os=image.attrs.get('Os', 'linux'),
                layers=[layer['Id'] for layer in image.attrs.get('RootFS', {}).get('Layers', [])],
                labels=image.attrs.get('Config', {}).get('Labels', {}),
                environment=image.attrs.get('Config', {}).get('Env', []),
                exposed_ports=list(image.attrs.get('Config', {}).get('ExposedPorts', {}).keys()),
                volumes=list(image.attrs.get('Config', {}).get('Volumes', {}).keys()),
                working_dir=image.attrs.get('Config', {}).get('WorkingDir', ''),
                cmd=image.attrs.get('Config', {}).get('Cmd', []),
                entrypoint=image.attrs.get('Config', {}).get('Entrypoint', [])
            )
            
            self.logger.info(f"镜像拉取完成: {image_name}:{tag}")
            return container_image
        
        except Exception as e:
            self.logger.error(f"拉取镜像失败: {e}")
            raise

class ContainerManager:
    """容器管理器"""
    
    def __init__(self, docker_client=None):
        self.docker_client = docker_client or docker.from_env()
        self.logger = logging.getLogger(__name__)
        self.containers = {}
    
    def create_container(self, image: str, name: str, **kwargs) -> ContainerConfig:
        """创建容器"""
        try:
            self.logger.info(f"创建容器: {name}")
            
            # 准备容器参数
            container_params = {
                'image': image,
                'name': name,
                'detach': True,
                'environment': kwargs.get('environment', {}),
                'ports': kwargs.get('ports', {}),
                'volumes': kwargs.get('volumes', {}),
                'restart_policy': kwargs.get('restart_policy', {'Name': 'no'}),
                'network_mode': kwargs.get('network_mode', 'bridge'),
                'labels': kwargs.get('labels', {})
            }
            
            # 添加资源限制
            if kwargs.get('cpu_limit'):
                container_params['nano_cpus'] = int(kwargs['cpu_limit'] * 1e9)
            
            if kwargs.get('memory_limit'):
                container_params['mem_limit'] = kwargs['memory_limit']
            
            # 添加健康检查
            if kwargs.get('health_check'):
                container_params['healthcheck'] = kwargs['health_check']
            
            # 创建容器
            container = self.docker_client.containers.create(**container_params)
            
            # 创建容器配置对象
            container_config = ContainerConfig(
                container_id=container.id,
                name=name,
                image=image,
                status=ContainerStatus.CREATED,
                created_at=datetime.now(),
                started_at=None,
                ports=container_params['ports'],
                volumes=container_params['volumes'],
                environment=container_params['environment'],
                restart_policy=container_params['restart_policy']['Name'],
                network_mode=container_params['network_mode'],
                cpu_limit=kwargs.get('cpu_limit'),
                memory_limit=kwargs.get('memory_limit'),
                labels=container_params['labels'],
                health_check=kwargs.get('health_check')
            )
            
            self.containers[container.id] = container_config
            self.logger.info(f"容器创建完成: {name}")
            
            return container_config
        
        except Exception as e:
            self.logger.error(f"创建容器失败: {e}")
            raise
    
    def start_container(self, container_id: str) -> bool:
        """启动容器"""
        try:
            container = self.docker_client.containers.get(container_id)
            container.start()
            
            # 更新容器状态
            if container_id in self.containers:
                self.containers[container_id].status = ContainerStatus.RUNNING
                self.containers[container_id].started_at = datetime.now()
            
            self.logger.info(f"容器启动成功: {container_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"启动容器失败: {e}")
            return False
    
    def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """停止容器"""
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop(timeout=timeout)
            
            # 更新容器状态
            if container_id in self.containers:
                self.containers[container_id].status = ContainerStatus.EXITED
            
            self.logger.info(f"容器停止成功: {container_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"停止容器失败: {e}")
            return False
    
    def restart_container(self, container_id: str, timeout: int = 10) -> bool:
        """重启容器"""
        try:
            container = self.docker_client.containers.get(container_id)
            container.restart(timeout=timeout)
            
            # 更新容器状态
            if container_id in self.containers:
                self.containers[container_id].status = ContainerStatus.RUNNING
                self.containers[container_id].started_at = datetime.now()
            
            self.logger.info(f"容器重启成功: {container_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"重启容器失败: {e}")
            return False
    
    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """删除容器"""
        try:
            container = self.docker_client.containers.get(container_id)
            container.remove(force=force)
            
            # 从内存中移除
            if container_id in self.containers:
                del self.containers[container_id]
            
            self.logger.info(f"容器删除成功: {container_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"删除容器失败: {e}")
            return False
    
    def get_container_logs(self, container_id: str, tail: int = 100, follow: bool = False) -> str:
        """获取容器日志"""
        try:
            container = self.docker_client.containers.get(container_id)
            logs = container.logs(tail=tail, follow=follow)
            return logs.decode('utf-8')
        
        except Exception as e:
            self.logger.error(f"获取容器日志失败: {e}")
            return ""
    
    def get_container_stats(self, container_id: str) -> Dict[str, Any]:
        """获取容器统计信息"""
        try:
            container = self.docker_client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # 解析统计信息
            cpu_stats = stats.get('cpu_stats', {})
            precpu_stats = stats.get('precpu_stats', {})
            memory_stats = stats.get('memory_stats', {})
            
            # 计算CPU使用率
            cpu_delta = cpu_stats.get('cpu_usage', {}).get('total_usage', 0) - \
                       precpu_stats.get('cpu_usage', {}).get('total_usage', 0)
            system_cpu_delta = cpu_stats.get('system_cpu_usage', 0) - \
                              precpu_stats.get('system_cpu_usage', 0)
            
            cpu_count = cpu_stats.get('online_cpus', 1)
            cpu_percent = (cpu_delta / system_cpu_delta) * cpu_count * 100.0 if system_cpu_delta > 0 else 0.0
            
            # 内存使用情况
            memory_usage = memory_stats.get('usage', 0)
            memory_limit = memory_stats.get('limit', 0)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_usage': memory_usage,
                'memory_limit': memory_limit,
                'memory_percent': memory_percent,
                'network_rx': stats.get('networks', {}).get('eth0', {}).get('rx_bytes', 0),
                'network_tx': stats.get('networks', {}).get('eth0', {}).get('tx_bytes', 0),
                'block_read': stats.get('blkio_stats', {}).get('io_service_bytes_recursive', [{}])[0].get('read', 0),
                'block_write': stats.get('blkio_stats', {}).get('io_service_bytes_recursive', [{}])[0].get('write', 0)
            }
        
        except Exception as e:
            self.logger.error(f"获取容器统计信息失败: {e}")
            return {}
    
    def list_containers(self, all_containers: bool = False) -> List[ContainerConfig]:
        """列出容器"""
        try:
            containers = self.docker_client.containers.list(all=all_containers)
            container_configs = []
            
            for container in containers:
                # 解析容器状态
                status_str = container.status
                if status_str == 'running':
                    status = ContainerStatus.RUNNING
                elif status_str == 'exited':
                    status = ContainerStatus.EXITED
                elif status_str == 'paused':
                    status = ContainerStatus.PAUSED
                else:
                    status = ContainerStatus.CREATED
                
                # 创建容器配置对象
                config = ContainerConfig(
                    container_id=container.id,
                    name=container.name,
                    image=container.image.tags[0] if container.image.tags else "",
                    status=status,
                    created_at=datetime.strptime(container.attrs['Created'][:-4], '%Y-%m-%dT%H:%M:%S'),
                    started_at=None,
                    ports=container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                    volumes=container.attrs.get('Mounts', []),
                    environment=[env.split('=', 1) for env in container.attrs.get('Config', {}).get('Env', [])],
                    restart_policy=container.attrs.get('HostConfig', {}).get('RestartPolicy', {}).get('Name', 'no'),
                    network_mode=container.attrs.get('HostConfig', {}).get('NetworkMode', 'bridge'),
                    labels=container.attrs.get('Config', {}).get('Labels', {})
                )
                
                container_configs.append(config)
            
            return container_configs
        
        except Exception as e:
            self.logger.error(f"列出容器失败: {e}")
            return []

class NetworkManager:
    """网络管理器"""
    
    def __init__(self, docker_client=None):
        self.docker_client = docker_client or docker.from_env()
        self.logger = logging.getLogger(__name__)
        self.networks = {}
    
    def create_network(self, name: str, driver: str = "bridge", **kwargs) -> NetworkConfig:
        """创建网络"""
        try:
            self.logger.info(f"创建网络: {name}")
            
            # 准备网络参数
            network_params = {
                'name': name,
                'driver': driver,
                'labels': kwargs.get('labels', {})
            }
            
            # 添加IPAM配置
            if kwargs.get('subnet') or kwargs.get('gateway'):
                ipam_config = {
                    'Config': []
                }
                
                config = {}
                if kwargs.get('subnet'):
                    config['Subnet'] = kwargs['subnet']
                if kwargs.get('gateway'):
                    config['Gateway'] = kwargs['gateway']
                if kwargs.get('ip_range'):
                    config['IPRange'] = kwargs['ip_range']
                
                if config:
                    ipam_config['Config'].append(config)
                    network_params['ipam'] = ipam_config
            
            # 添加其他选项
            if kwargs.get('internal'):
                network_params['internal'] = True
            if kwargs.get('enable_ipv6'):
                network_params['enable_ipv6'] = True
            
            # 创建网络
            network = self.docker_client.networks.create(**network_params)
            
            # 创建网络配置对象
            network_config = NetworkConfig(
                network_id=network.id,
                name=name,
                driver=driver,
                subnet=kwargs.get('subnet'),
                gateway=kwargs.get('gateway'),
                ip_range=kwargs.get('ip_range'),
                internal=kwargs.get('internal', False),
                enable_ipv6=kwargs.get('enable_ipv6', False),
                labels=kwargs.get('labels', {})
            )
            
            self.networks[network.id] = network_config
            self.logger.info(f"网络创建完成: {name}")
            
            return network_config
        
        except Exception as e:
            self.logger.error(f"创建网络失败: {e}")
            raise
    
    def remove_network(self, network_id: str) -> bool:
        """删除网络"""
        try:
            network = self.docker_client.networks.get(network_id)
            network.remove()
            
            # 从内存中移除
            if network_id in self.networks:
                del self.networks[network_id]
            
            self.logger.info(f"网络删除成功: {network_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"删除网络失败: {e}")
            return False
    
    def connect_container(self, network_id: str, container_id: str, **kwargs) -> bool:
        """连接容器到网络"""
        try:
            network = self.docker_client.networks.get(network_id)
            container = self.docker_client.containers.get(container_id)
            
            # 准备连接配置
            connect_config = {}
            if kwargs.get('ipv4_address'):
                connect_config['ipv4_address'] = kwargs['ipv4_address']
            if kwargs.get('ipv6_address'):
                connect_config['ipv6_address'] = kwargs['ipv6_address']
            if kwargs.get('aliases'):
                connect_config['aliases'] = kwargs['aliases']
            
            network.connect(container, **connect_config)
            
            self.logger.info(f"容器 {container_id} 已连接到网络 {network_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"连接容器到网络失败: {e}")
            return False
    
    def disconnect_container(self, network_id: str, container_id: str) -> bool:
        """断开容器与网络的连接"""
        try:
            network = self.docker_client.networks.get(network_id)
            container = self.docker_client.containers.get(container_id)
            
            network.disconnect(container)
            
            self.logger.info(f"容器 {container_id} 已断开与网络 {network_id} 的连接")
            return True
        
        except Exception as e:
            self.logger.error(f"断开容器与网络连接失败: {e}")
            return False

class DockerContainerizer:
    """Docker容器化器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.docker_client = docker.from_env()
        self.dockerfile_generator = DockerfileGenerator()
        self.docker_builder = DockerBuilder(self.docker_client)
        self.container_manager = ContainerManager(self.docker_client)
        self.network_manager = NetworkManager(self.docker_client)
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def containerize_application(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """容器化应用"""
        try:
            self.logger.info(f"开始容器化应用: {app_config.get('name', 'unknown')}")
            
            # 1. 生成Dockerfile
            dockerfile_path = self._generate_dockerfile(app_config)
            
            # 2. 构建镜像
            build_context = BuildContext(
                context_id=str(uuid.uuid4()),
                dockerfile_path=dockerfile_path,
                build_context_path=app_config.get('build_context', '.'),
                build_args=app_config.get('build_args', {}),
                labels=app_config.get('labels', {}),
                tags=app_config.get('image_tags', ['app:latest']),
                target=app_config.get('target'),
                no_cache=app_config.get('no_cache', False),
                pull=app_config.get('pull', False)
            )
            
            image = self.docker_builder.build_image(build_context)
            
            # 3. 创建网络（如果需要）
            network_id = None
            if app_config.get('network'):
                network_config = self.network_manager.create_network(
                    name=app_config['network'].get('name', 'app-network'),
                    driver=app_config['network'].get('driver', 'bridge'),
                    subnet=app_config['network'].get('subnet'),
                    gateway=app_config['network'].get('gateway')
                )
                network_id = network_config.network_id
            
            # 4. 创建容器
            container_config = self.container_manager.create_container(
                image=image.name,
                name=app_config.get('container_name', 'app-container'),
                environment=app_config.get('environment', {}),
                ports=app_config.get('ports', {}),
                volumes=app_config.get('volumes', {}),
                restart_policy=app_config.get('restart_policy', {'Name': 'no'}),
                network_mode=app_config.get('network_mode', 'bridge'),
                cpu_limit=app_config.get('cpu_limit'),
                memory_limit=app_config.get('memory_limit'),
                labels=app_config.get('labels', {}),
                health_check=app_config.get('health_check')
            )
            
            # 5. 连接网络（如果需要）
            if network_id and app_config.get('network'):
                self.network_manager.connect_container(
                    network_id=network_id,
                    container_id=container_config.container_id,
                    ipv4_address=app_config['network'].get('ipv4_address'),
                    aliases=app_config['network'].get('aliases', [])
                )
            
            # 6. 启动容器
            self.container_manager.start_container(container_config.container_id)
            
            result = {
                'image': asdict(image),
                'container': asdict(container_config),
                'network_id': network_id,
                'status': 'success'
            }
            
            self.logger.info(f"应用容器化完成: {app_config.get('name')}")
            return result
        
        except Exception as e:
            self.logger.error(f"应用容器化失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_dockerfile(self, app_config: Dict[str, Any]) -> str:
        """生成Dockerfile"""
        generator = DockerfileGenerator()
        
        # 基础镜像
        base_image = app_config.get('base_image', 'ubuntu:20.04')
        generator.add_from(base_image)
        
        # 维护者信息
        if app_config.get('maintainer'):
            generator.add_label('maintainer', app_config['maintainer'])
        
        # 工作目录
        if app_config.get('workdir'):
            generator.add_workdir(app_config['workdir'])
        
        # 环境变量
        if app_config.get('environment'):
            for key, value in app_config['environment'].items():
                generator.add_env(key, value)
        
        # 安装系统依赖
        if app_config.get('system_packages'):
            packages = ' '.join(app_config['system_packages'])
            generator.add_run(f"apt-get update && apt-get install -y {packages}")
        
        # 安装应用依赖
        if app_config.get('app_dependencies'):
            for dep in app_config['app_dependencies']:
                if dep.get('type') == 'pip':
                    generator.add_run(f"pip install {dep.get('package')}")
                elif dep.get('type') == 'npm':
                    generator.add_run(f"npm install {dep.get('package')}")
                elif dep.get('type') == 'apt':
                    generator.add_run(f"apt-get install -y {dep.get('package')}")
        
        # 复制应用代码
        if app_config.get('source_path'):
            generator.add_copy(app_config['source_path'], app_config.get('target_path', '.'))
        
        # 暴露端口
        if app_config.get('exposed_ports'):
            for port in app_config['exposed_ports']:
                generator.add_expose(port)
        
        # 创建用户
        if app_config.get('user'):
            generator.add_user(app_config['user'])
        
        # 设置卷
        if app_config.get('volumes'):
            for volume in app_config['volumes']:
                if isinstance(volume, str):
                    generator.add_volume(volume)
                elif isinstance(volume, dict):
                    generator.add_volume(volume.get('path'))
        
        # 健康检查
        if app_config.get('health_check'):
            health_cmd = app_config['health_check'].get('command')
            interval = app_config['health_check'].get('interval')
            timeout = app_config['health_check'].get('timeout')
            retries = app_config['health_check'].get('retries')
            
            generator.add_healthcheck(health_cmd, interval, timeout, retries)
        
        # 启动命令
        if app_config.get('cmd'):
            generator.add_cmd(app_config['cmd'])
        
        # 入口点
        if app_config.get('entrypoint'):
            generator.add_entrypoint(app_config['entrypoint'])
        
        # 保存Dockerfile
        dockerfile_path = app_config.get('dockerfile_path', 'Dockerfile')
        generator.save_dockerfile(dockerfile_path)
        
        return dockerfile_path
    
    def get_containerization_status(self, container_id: str) -> Dict[str, Any]:
        """获取容器化状态"""
        try:
            # 获取容器信息
            container = self.container_manager.containers.get(container_id)
            
            # 获取容器统计信息
            stats = self.container_manager.get_container_stats(container_id)
            
            # 获取容器日志
            logs = self.container_manager.get_container_logs(container_id, tail=50)
            
            return {
                'container_id': container_id,
                'status': container.status.value,
                'image': container.image.tags[0] if container.image.tags else "",
                'created_at': container.created_at.isoformat(),
                'started_at': container.started_at.isoformat() if container.started_at else None,
                'stats': stats,
                'logs': logs
            }
        
        except Exception as e:
            self.logger.error(f"获取容器化状态失败: {e}")
            return {'error': str(e)}
    
    def cleanup(self, container_id: str = None, network_id: str = None):
        """清理资源"""
        try:
            if container_id:
                # 停止并删除容器
                self.container_manager.stop_container(container_id)
                self.container_manager.remove_container(container_id, force=True)
            
            if network_id:
                # 删除网络
                self.network_manager.remove_network(network_id)
            
            self.logger.info("资源清理完成")
        
        except Exception as e:
            self.logger.error(f"清理资源失败: {e}")

# 使用示例
# 配置
app_config = {
    'name': 'web-app',
    'base_image': 'python:3.9-slim',
    'workdir': '/app',
    'system_packages': ['curl', 'wget'],
    'app_dependencies': [
        {'type': 'pip', 'package': 'flask'},
        {'type': 'pip', 'package': 'requests'}
    ],
    'source_path': '.',
    'target_path': '/app',
    'exposed_ports': ['5000'],
    'environment': {
        'FLASK_ENV': 'production',
        'PORT': '5000'
    },
    'ports': {'5000/tcp': 5000},
    'volumes': ['/app/data'],
    'user': 'nobody',
    'cmd': ['python', 'app.py'],
    'container_name': 'web-app-container',
    'image_tags': ['web-app:latest'],
    'restart_policy': {'Name': 'always'},
    'health_check': {
        'command': 'curl -f http://localhost:5000/health || exit 1',
        'interval': '30s',
        'timeout': '10s',
        'retries': 3
    }
}

# 创建容器化器
containerizer = DockerContainerizer()

# 容器化应用
result = containerizer.containerize_application(app_config)
print(f"容器化结果: {result}")

# 获取状态
if result['status'] == 'success':
    container_id = result['container']['container_id']
    status = containerizer.get_containerization_status(container_id)
    print(f"容器状态: {status}")

# 清理资源
if result['status'] == 'success':
    containerizer.cleanup(
        container_id=result['container']['container_id'],
        network_id=result.get('network_id')
    )
```

## 参考资源

### Docker官方文档
- [Docker官方文档](https://docs.docker.com/)
- [Dockerfile参考](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Docker网络文档](https://docs.docker.com/network/)
- [Docker存储文档](https://docs.docker.com/storage/)

### 容器化最佳实践
- [Docker最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [容器安全最佳实践](https://docs.docker.com/engine/security/)
- [多阶段构建指南](https://docs.docker.com/build/building/multi-stage/)

### 容器编排
- [Kubernetes文档](https://kubernetes.io/docs/)
- [Docker Swarm文档](https://docs.docker.com/engine/swarm/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Helm文档](https://helm.sh/docs/)

### 容器安全
- [Docker安全指南](https://docs.docker.com/engine/security/)
- [容器安全扫描](https://github.com/aquasecurity/trivy)
- [Docker Content Trust](https://docs.docker.com/engine/security/trust/)
- [容器运行时安全](https://github.com/opencontainers/runtime-spec)

### 监控和日志
- [Docker监控](https://docs.docker.com/config/daemon/logging/)
- [Prometheus Docker监控](https://prometheus.io/docs/guides/docker-monitoring/)
- [Grafana Docker监控](https://grafana.com/docs/grafana/latest/datasources/docker/)
- [ELK Stack日志收集](https://www.elastic.co/guide/en/elastic-stack/current/index.html)
