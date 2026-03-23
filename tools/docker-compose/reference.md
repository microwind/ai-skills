# Docker Compose配置器参考文档

## Docker Compose配置器概述

### 什么是Docker Compose配置器
Docker Compose配置器是一个专门用于生成和管理Docker Compose配置文件的工具。该工具支持多种服务类型（Web应用、数据库、缓存、消息队列等），提供可视化配置界面、模板系统、环境管理、服务编排等功能，帮助开发者快速构建、部署和管理容器化应用程序。

### 主要功能
- **多服务支持**: 支持Web应用、数据库、缓存、消息队列等多种服务类型
- **可视化配置**: 提供直观的表单界面配置Docker Compose文件
- **模板系统**: 内置常用服务模板，快速生成配置
- **环境管理**: 支持多环境配置和部署
- **服务编排**: 提供服务依赖、扩展和负载均衡配置
- **安全配置**: 内置安全最佳实践和合规检查
- **资源管理**: 支持CPU、内存、磁盘等资源限制配置

## Docker Compose配置生成器

### 配置文件生成器
```python
# docker_compose_generator.py
import yaml
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

class ServiceType(Enum):
    WEB = "web"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    MONITORING = "monitoring"
    CUSTOM = "custom"

class NetworkMode(Enum):
    BRIDGE = "bridge"
    HOST = "host"
    NONE = "none"
    OVERLAY = "overlay"
    SERVICE = "service"
    CONTAINER = "container"

class RestartPolicy(Enum):
    NO = "no"
    ALWAYS = "always"
    ON_FAILURE = "on-failure"
    UNLESS_STOPPED = "unless-stopped"

@dataclass
class PortMapping:
    container_port: int
    host_port: Optional[int] = None
    protocol: str = "tcp"
    mode: Optional[str] = None

@dataclass
class VolumeMapping:
    source: str
    target: str
    type: str = "bind"  # bind, volume, tmpfs
    read_only: bool = False
    consistency: Optional[str] = None

@dataclass
class EnvironmentVariable:
    name: str
    value: str
    is_secret: bool = False

@dataclass
class HealthCheck:
    test: List[str]
    interval: Optional[str] = None
    timeout: Optional[str] = None
    retries: Optional[int] = None
    start_period: Optional[str] = None

@dataclass
class ResourceLimit:
    cpu_limit: Optional[str] = None
    cpu_reservation: Optional[str] = None
    memory_limit: Optional[str] = None
    memory_reservation: Optional[str] = None

@dataclass
class Service:
    name: str
    image: Optional[str] = None
    build: Optional[Dict[str, Any]] = None
    ports: List[PortMapping] = None
    volumes: List[VolumeMapping] = None
    environment: List[EnvironmentVariable] = None
    networks: List[str] = None
    depends_on: List[str] = None
    restart: RestartPolicy = RestartPolicy.NO
    health_check: Optional[HealthCheck] = None
    resources: Optional[ResourceLimit] = None
    user: Optional[str] = None
    working_dir: Optional[str] = None
    command: Optional[Union[str, List[str]]] = None
    entrypoint: Optional[Union[str, List[str]]] = None

@dataclass
class Network:
    name: str
    driver: str = "bridge"
    driver_opts: Dict[str, Any] = None
    ipam: Dict[str, Any] = None
    external: bool = False
    internal: bool = False

@dataclass
class Volume:
    name: str
    driver: str = "local"
    driver_opts: Dict[str, Any] = None
    external: bool = False
    labels: Dict[str, str] = None

@dataclass
class DockerComposeConfig:
    version: str = "3.8"
    services: List[Service] = None
    networks: Dict[str, Network] = None
    volumes: Dict[str, Volume] = None
    configs: Dict[str, Any] = None
    secrets: Dict[str, Any] = None

class DockerComposeGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[ServiceType, Dict[str, Any]]:
        """加载服务模板"""
        return {
            ServiceType.WEB: {
                "nginx": {
                    "image": "nginx:latest",
                    "ports": [PortMapping(container_port=80, host_port=80)],
                    "volumes": [VolumeMapping(source="./nginx.conf", target="/etc/nginx/nginx.conf")],
                    "restart": RestartPolicy.UNLESS_STOPPED
                },
                "apache": {
                    "image": "httpd:latest",
                    "ports": [PortMapping(container_port=80, host_port=80)],
                    "volumes": [VolumeMapping(source="./html", target="/usr/local/apache2/htdocs")],
                    "restart": RestartPolicy.UNLESS_STOPPED
                },
                "node": {
                    "image": "node:16-alpine",
                    "ports": [PortMapping(container_port=3000, host_port=3000)],
                    "working_dir": "/app",
                    "volumes": [VolumeMapping(source="./app", target="/app")],
                    "command": "npm start",
                    "restart": RestartPolicy.UNLESS_STOPPED
                }
            },
            ServiceType.DATABASE: {
                "mysql": {
                    "image": "mysql:8.0",
                    "environment": [
                        EnvironmentVariable("MYSQL_ROOT_PASSWORD", "rootpassword"),
                        EnvironmentVariable("MYSQL_DATABASE", "myapp"),
                        EnvironmentVariable("MYSQL_USER", "user"),
                        EnvironmentVariable("MYSQL_PASSWORD", "password")
                    ],
                    "ports": [PortMapping(container_port=3306, host_port=3306)],
                    "volumes": [VolumeMapping(source="mysql_data", target="/var/lib/mysql", type="volume")],
                    "restart": RestartPolicy.UNLESS_STOPPED
                },
                "postgresql": {
                    "image": "postgres:13",
                    "environment": [
                        EnvironmentVariable("POSTGRES_DB", "myapp"),
                        EnvironmentVariable("POSTGRES_USER", "user"),
                        EnvironmentVariable("POSTGRES_PASSWORD", "password")
                    ],
                    "ports": [PortMapping(container_port=5432, host_port=5432)],
                    "volumes": [VolumeMapping(source="postgres_data", target="/var/lib/postgresql/data", type="volume")],
                    "restart": RestartPolicy.UNLESS_STOPPED
                },
                "mongodb": {
                    "image": "mongo:5.0",
                    "environment": [
                        EnvironmentVariable("MONGO_INITDB_ROOT_USERNAME", "admin"),
                        EnvironmentVariable("MONGO_INITDB_ROOT_PASSWORD", "password")
                    ],
                    "ports": [PortMapping(container_port=27017, host_port=27017)],
                    "volumes": [VolumeMapping(source="mongo_data", target="/data/db", type="volume")],
                    "restart": RestartPolicy.UNLESS_STOPPED
                }
            },
            ServiceType.CACHE: {
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": [PortMapping(container_port=6379, host_port=6379)],
                    "volumes": [VolumeMapping(source="redis_data", target="/data", type="volume")],
                    "command": "redis-server --appendonly yes",
                    "restart": RestartPolicy.UNLESS_STOPPED
                },
                "memcached": {
                    "image": "memcached:1.6-alpine",
                    "ports": [PortMapping(container_port=11211, host_port=11211)],
                    "command": "memcached -m 64",
                    "restart": RestartPolicy.UNLESS_STOPPED
                }
            },
            ServiceType.QUEUE: {
                "rabbitmq": {
                    "image": "rabbitmq:3.9-management",
                    "environment": [
                        EnvironmentVariable("RABBITMQ_DEFAULT_USER", "admin"),
                        EnvironmentVariable("RABBITMQ_DEFAULT_PASS", "password")
                    ],
                    "ports": [
                        PortMapping(container_port=5672, host_port=5672),
                        PortMapping(container_port=15672, host_port=15672)
                    ],
                    "volumes": [VolumeMapping(source="rabbitmq_data", target="/var/lib/rabbitmq", type="volume")],
                    "restart": RestartPolicy.UNLESS_STOPPED
                },
                "kafka": {
                    "image": "confluentinc/cp-kafka:latest",
                    "environment": [
                        EnvironmentVariable("KAFKA_ZOOKEEPER_CONNECT", "zookeeper:2181"),
                        EnvironmentVariable("KAFKA_ADVERTISED_LISTENERS", "PLAINTEXT://localhost:9092"),
                        EnvironmentVariable("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1")
                    ],
                    "ports": [PortMapping(container_port=9092, host_port=9092)],
                    "depends_on": ["zookeeper"],
                    "restart": RestartPolicy.UNLESS_STOPPED
                }
            }
        }
    
    def create_service(self, service_type: ServiceType, template_name: str, 
                       service_name: str, **kwargs) -> Service:
        """创建服务"""
        if service_type not in self.templates:
            raise ValueError(f"不支持的服务类型: {service_type}")
        
        templates = self.templates[service_type]
        if template_name not in templates:
            raise ValueError(f"不存在的模板: {template_name}")
        
        template = templates[template_name]
        
        # 创建服务对象
        service = Service(
            name=service_name,
            image=template.get("image"),
            ports=template.get("ports", []),
            volumes=template.get("volumes", []),
            environment=template.get("environment", []),
            restart=template.get("restart", RestartPolicy.NO),
            **kwargs
        )
        
        return service
    
    def add_custom_service(self, service: Service):
        """添加自定义服务"""
        return service
    
    def create_network(self, name: str, driver: str = "bridge", 
                      external: bool = False, **kwargs) -> Network:
        """创建网络"""
        return Network(
            name=name,
            driver=driver,
            external=external,
            **kwargs
        )
    
    def create_volume(self, name: str, driver: str = "local", 
                     external: bool = False, **kwargs) -> Volume:
        """创建数据卷"""
        return Volume(
            name=name,
            driver=driver,
            external=external,
            **kwargs
        )
    
    def generate_compose_file(self, config: DockerComposeConfig, 
                            output_path: str = "docker-compose.yml") -> str:
        """生成Docker Compose文件"""
        compose_dict = {
            "version": config.version,
            "services": {}
        }
        
        # 转换服务
        for service in config.services or []:
            service_dict = self._service_to_dict(service)
            compose_dict["services"][service.name] = service_dict
        
        # 转换网络
        if config.networks:
            compose_dict["networks"] = {}
            for name, network in config.networks.items():
                network_dict = self._network_to_dict(network)
                compose_dict["networks"][name] = network_dict
        
        # 转换数据卷
        if config.volumes:
            compose_dict["volumes"] = {}
            for name, volume in config.volumes.items():
                volume_dict = self._volume_to_dict(volume)
                compose_dict["volumes"][name] = volume_dict
        
        # 生成YAML
        yaml_content = yaml.dump(compose_dict, default_flow_style=False, 
                               allow_unicode=True, sort_keys=False)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        self.logger.info(f"Docker Compose文件已生成: {output_path}")
        return yaml_content
    
    def _service_to_dict(self, service: Service) -> Dict[str, Any]:
        """将服务对象转换为字典"""
        service_dict = {}
        
        if service.image:
            service_dict["image"] = service.image
        
        if service.build:
            service_dict["build"] = service.build
        
        if service.ports:
            service_dict["ports"] = []
            for port in service.ports:
                port_mapping = f"{port.container_port}"
                if port.host_port:
                    port_mapping = f"{port.host_port}:{port_mapping}"
                if port.protocol != "tcp":
                    port_mapping += f"/{port.protocol}"
                if port.mode:
                    port_mapping += f":{port.mode}"
                service_dict["ports"].append(port_mapping)
        
        if service.volumes:
            service_dict["volumes"] = []
            for volume in service.volumes:
                volume_mapping = f"{volume.source}:{volume.target}"
                if volume.read_only:
                    volume_mapping += ":ro"
                service_dict["volumes"].append(volume_mapping)
        
        if service.environment:
            service_dict["environment"] = {}
            for env in service.environment:
                service_dict["environment"][env.name] = env.value
        
        if service.networks:
            service_dict["networks"] = service.networks
        
        if service.depends_on:
            service_dict["depends_on"] = service.depends_on
        
        if service.restart != RestartPolicy.NO:
            service_dict["restart"] = service.restart.value
        
        if service.health_check:
            health_dict = {
                "test": service.health_check.test
            }
            if service.health_check.interval:
                health_dict["interval"] = service.health_check.interval
            if service.health_check.timeout:
                health_dict["timeout"] = service.health_check.timeout
            if service.health_check.retries:
                health_dict["retries"] = service.health_check.retries
            if service.health_check.start_period:
                health_dict["start_period"] = service.health_check.start_period
            service_dict["healthcheck"] = health_dict
        
        if service.resources:
            deploy_dict = {}
            resources_dict = {}
            
            if service.resources.cpu_limit or service.resources.memory_limit:
                limits_dict = {}
                if service.resources.cpu_limit:
                    limits_dict["cpus"] = service.resources.cpu_limit
                if service.resources.memory_limit:
                    limits_dict["memory"] = service.resources.memory_limit
                resources_dict["limits"] = limits_dict
            
            if service.resources.cpu_reservation or service.resources.memory_reservation:
                reservations_dict = {}
                if service.resources.cpu_reservation:
                    reservations_dict["cpus"] = service.resources.cpu_reservation
                if service.resources.memory_reservation:
                    reservations_dict["memory"] = service.resources.memory_reservation
                resources_dict["reservations"] = reservations_dict
            
            if resources_dict:
                deploy_dict["resources"] = resources_dict
            
            if deploy_dict:
                service_dict["deploy"] = deploy_dict
        
        if service.user:
            service_dict["user"] = service.user
        
        if service.working_dir:
            service_dict["working_dir"] = service.working_dir
        
        if service.command:
            service_dict["command"] = service.command
        
        if service.entrypoint:
            service_dict["entrypoint"] = service.entrypoint
        
        return service_dict
    
    def _network_to_dict(self, network: Network) -> Dict[str, Any]:
        """将网络对象转换为字典"""
        network_dict = {
            "driver": network.driver
        }
        
        if network.driver_opts:
            network_dict["driver_opts"] = network.driver_opts
        
        if network.ipam:
            network_dict["ipam"] = network.ipam
        
        if network.external:
            network_dict["external"] = {"name": network.name}
        
        if network.internal:
            network_dict["internal"] = True
        
        return network_dict
    
    def _volume_to_dict(self, volume: Volume) -> Dict[str, Any]:
        """将数据卷对象转换为字典"""
        volume_dict = {
            "driver": volume.driver
        }
        
        if volume.driver_opts:
            volume_dict["driver_opts"] = volume.driver_opts
        
        if volume.external:
            volume_dict["external"] = {"name": volume.name}
        
        if volume.labels:
            volume_dict["labels"] = volume.labels
        
        return volume_dict
    
    def validate_config(self, config: DockerComposeConfig) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证服务
        service_names = set()
        for service in config.services or []:
            if not service.name:
                errors.append("服务名称不能为空")
                continue
            
            if service.name in service_names:
                errors.append(f"重复的服务名称: {service.name}")
            service_names.add(service.name)
            
            if not service.image and not service.build:
                errors.append(f"服务 {service.name} 必须指定image或build")
        
        # 验证依赖关系
        for service in config.services or []:
            if service.depends_on:
                for dep in service.depends_on:
                    if dep not in service_names:
                        errors.append(f"服务 {service.name} 依赖的服务 {dep} 不存在")
        
        # 验证网络
        for name, network in (config.networks or {}).items():
            if name != network.name and not network.external:
                errors.append(f"网络名称不一致: {name} vs {network.name}")
        
        # 验证数据卷
        for name, volume in (config.volumes or {}).items():
            if name != volume.name and not volume.external:
                errors.append(f"数据卷名称不一致: {name} vs {volume.name}")
        
        return errors

# 使用示例
generator = DockerComposeGenerator()

# 创建Web服务
web_service = generator.create_service(
    service_type=ServiceType.WEB,
    template_name="nginx",
    service_name="web"
)

# 创建数据库服务
db_service = generator.create_service(
    service_type=ServiceType.DATABASE,
    template_name="mysql",
    service_name="database"
)

# 创建缓存服务
cache_service = generator.create_service(
    service_type=ServiceType.CACHE,
    template_name="redis",
    service_name="cache"
)

# 创建自定义服务
custom_service = Service(
    name="app",
    build={"context": "./app", "dockerfile": "Dockerfile"},
    ports=[PortMapping(container_port=8000, host_port=8000)],
    volumes=[VolumeMapping(source="./app", target="/app")],
    environment=[
        EnvironmentVariable("DEBUG", "true"),
        EnvironmentVariable("DATABASE_URL", "mysql://user:password@database:3306/myapp")
    ],
    depends_on=["database", "cache"],
    restart=RestartPolicy.UNLESS_STOPPED,
    health_check=HealthCheck(
        test=["CMD", "curl", "-f", "http://localhost:8000/health"],
        interval="30s",
        timeout="10s",
        retries=3
    ),
    resources=ResourceLimit(
        cpu_limit="0.5",
        memory_limit="512M"
    )
)

# 创建网络
app_network = generator.create_network("app-network")
db_network = generator.create_network("db-network", driver="bridge")

# 创建数据卷
mysql_data = generator.create_volume("mysql_data")
redis_data = generator.create_volume("redis_data")

# 生成配置
config = DockerComposeConfig(
    version="3.8",
    services=[web_service, db_service, cache_service, custom_service],
    networks={
        "app-network": app_network,
        "db-network": db_network
    },
    volumes={
        "mysql_data": mysql_data,
        "redis_data": redis_data
    }
)

# 验证配置
errors = generator.validate_config(config)
if errors:
    print("配置错误:")
    for error in errors:
        print(f"  - {error}")
else:
    print("配置验证通过")

# 生成Docker Compose文件
generator.generate_compose_file(config, "docker-compose.yml")
print("Docker Compose文件已生成")
```

## 环境管理器

### 多环境配置管理
```python
# environment_manager.py
import os
import yaml
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging

class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class EnvironmentConfig:
    name: str
    type: EnvironmentType
    variables: Dict[str, str] = None
    networks: Dict[str, Any] = None
    volumes: Dict[str, Any] = None
    service_overrides: Dict[str, Any] = None
    deploy_config: Dict[str, Any] = None

class EnvironmentManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.environments = {}
        self.base_config = None
    
    def load_base_config(self, config_path: str):
        """加载基础配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    self.base_config = yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    self.base_config = json.load(f)
                else:
                    raise ValueError("不支持的配置文件格式")
            
            self.logger.info(f"基础配置已加载: {config_path}")
        
        except Exception as e:
            self.logger.error(f"加载基础配置失败: {e}")
            raise
    
    def add_environment(self, env_config: EnvironmentConfig):
        """添加环境配置"""
        self.environments[env_config.name] = env_config
        self.logger.info(f"环境配置已添加: {env_config.name}")
    
    def generate_environment_config(self, env_name: str, output_path: str = None) -> str:
        """生成特定环境的配置"""
        if env_name not in self.environments:
            raise ValueError(f"环境不存在: {env_name}")
        
        env_config = self.environments[env_name]
        
        # 合并基础配置和环境配置
        merged_config = self._merge_configs(self.base_config, env_config)
        
        # 生成配置文件
        if output_path is None:
            output_path = f"docker-compose.{env_name}.yml"
        
        yaml_content = yaml.dump(merged_config, default_flow_style=False, 
                               allow_unicode=True, sort_keys=False)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        self.logger.info(f"环境配置已生成: {output_path}")
        return yaml_content
    
    def _merge_configs(self, base_config: Dict[str, Any], 
                       env_config: EnvironmentConfig) -> Dict[str, Any]:
        """合并基础配置和环境配置"""
        if not base_config:
            base_config = {"version": "3.8", "services": {}}
        
        merged_config = base_config.copy()
        
        # 合并环境变量
        if env_config.variables:
            if "services" not in merged_config:
                merged_config["services"] = {}
            
            for service_name, service_config in merged_config["services"].items():
                if "environment" not in service_config:
                    service_config["environment"] = {}
                
                # 应用环境变量
                for var_name, var_value in env_config.variables.items():
                    service_config["environment"][var_name] = var_value
        
        # 合并网络配置
        if env_config.networks:
            if "networks" not in merged_config:
                merged_config["networks"] = {}
            merged_config["networks"].update(env_config.networks)
        
        # 合并数据卷配置
        if env_config.volumes:
            if "volumes" not in merged_config:
                merged_config["volumes"] = {}
            merged_config["volumes"].update(env_config.volumes)
        
        # 合并服务覆盖
        if env_config.service_overrides:
            if "services" not in merged_config:
                merged_config["services"] = {}
            
            for service_name, overrides in env_config.service_overrides.items():
                if service_name in merged_config["services"]:
                    # 深度合并服务配置
                    merged_config["services"][service_name] = self._deep_merge(
                        merged_config["services"][service_name],
                        overrides
                    )
                else:
                    merged_config["services"][service_name] = overrides
        
        # 合并部署配置
        if env_config.deploy_config:
            merged_config.update(env_config.deploy_config)
        
        return merged_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def generate_env_file(self, env_name: str, output_path: str = None) -> str:
        """生成环境变量文件"""
        if env_name not in self.environments:
            raise ValueError(f"环境不存在: {env_name}")
        
        env_config = self.environments[env_name]
        
        if output_path is None:
            output_path = f".env.{env_name}"
        
        # 生成环境变量文件
        env_lines = []
        if env_config.variables:
            for var_name, var_value in env_config.variables.items():
                env_lines.append(f"{var_name}={var_value}")
        
        env_content = "\n".join(env_lines)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.logger.info(f"环境变量文件已生成: {output_path}")
        return env_content
    
    def list_environments(self) -> List[str]:
        """列出所有环境"""
        return list(self.environments.keys())
    
    def get_environment(self, env_name: str) -> Optional[EnvironmentConfig]:
        """获取环境配置"""
        return self.environments.get(env_name)

# 使用示例
env_manager = EnvironmentManager()

# 加载基础配置
env_manager.load_base_config("docker-compose.yml")

# 创建开发环境配置
dev_env = EnvironmentConfig(
    name="development",
    type=EnvironmentType.DEVELOPMENT,
    variables={
        "DEBUG": "true",
        "LOG_LEVEL": "debug",
        "DATABASE_URL": "mysql://dev_user:dev_pass@database:3306/dev_db"
    },
    service_overrides={
        "web": {
            "ports": ["8080:80"]
        },
        "database": {
            "environment": {
                "MYSQL_ROOT_PASSWORD": "dev_root_password"
            }
        }
    }
)

# 创建生产环境配置
prod_env = EnvironmentConfig(
    name="production",
    type=EnvironmentType.PRODUCTION,
    variables={
        "DEBUG": "false",
        "LOG_LEVEL": "info",
        "DATABASE_URL": "mysql://prod_user:prod_pass@database:3306/prod_db"
    },
    service_overrides={
        "web": {
            "deploy": {
                "replicas": 3,
                "resources": {
                    "limits": {
                        "cpus": "0.5",
                        "memory": "512M"
                    }
                }
            }
        },
        "database": {
            "environment": {
                "MYSQL_ROOT_PASSWORD": "${MYSQL_ROOT_PASSWORD}"
            }
        }
    },
    deploy_config={
        "deploy": {
            "replicas": 2
        }
    }
)

# 添加环境配置
env_manager.add_environment(dev_env)
env_manager.add_environment(prod_env)

# 生成环境配置文件
env_manager.generate_environment_config("development")
env_manager.generate_environment_config("production")

# 生成环境变量文件
env_manager.generate_env_file("development")
env_manager.generate_env_file("production")

# 列出所有环境
environments = env_manager.list_environments()
print(f"可用环境: {environments}")
```

## 服务编排器

### 服务依赖管理
```python
# service_orchestrator.py
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class DependencyType(Enum):
    STARTS_BEFORE = "starts_before"
    HEALTHY_BEFORE = "healthy_before"
    COMPLETE_BEFORE = "complete_before"

@dataclass
class ServiceDependency:
    service_name: str
    depends_on: str
    dependency_type: DependencyType
    condition: Optional[str] = None

@dataclass
class StartupOrder:
    stage: int
    services: List[str]

class ServiceOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependencies = []
        self.services = set()
    
    def add_dependency(self, service_name: str, depends_on: str, 
                      dependency_type: DependencyType = DependencyType.STARTS_BEFORE,
                      condition: Optional[str] = None):
        """添加服务依赖"""
        dependency = ServiceDependency(
            service_name=service_name,
            depends_on=depends_on,
            dependency_type=dependency_type,
            condition=condition
        )
        
        self.dependencies.append(dependency)
        self.services.add(service_name)
        self.services.add(depends_on)
        
        self.logger.info(f"添加依赖: {service_name} -> {depends_on} ({dependency_type.value})")
    
    def remove_dependency(self, service_name: str, depends_on: str):
        """移除服务依赖"""
        self.dependencies = [
            dep for dep in self.dependencies 
            if not (dep.service_name == service_name and dep.depends_on == depends_on)
        ]
        
        self.logger.info(f"移除依赖: {service_name} -> {depends_on}")
    
    def calculate_startup_order(self) -> List[StartupOrder]:
        """计算启动顺序"""
        # 构建依赖图
        dependency_graph = self._build_dependency_graph()
        
        # 拓扑排序
        startup_order = self._topological_sort(dependency_graph)
        
        # 分组启动阶段
        stages = self._group_into_stages(startup_order)
        
        return stages
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """构建依赖图"""
        graph = {service: set() for service in self.services}
        
        for dependency in self.dependencies:
            if dependency.dependency_type == DependencyType.STARTS_BEFORE:
                graph[dependency.service_name].add(dependency.depends_on)
        
        return graph
    
    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """拓扑排序"""
        in_degree = {node: 0 for node in graph}
        
        # 计算入度
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # 找到所有入度为0的节点
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # 减少邻居的入度
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # 检查是否有循环依赖
        if len(result) != len(graph):
            raise ValueError("检测到循环依赖")
        
        return result
    
    def _group_into_stages(self, startup_order: List[str]) -> List[StartupOrder]:
        """分组为启动阶段"""
        if not startup_order:
            return []
        
        stages = []
        current_stage = [startup_order[0]]
        current_dependencies = set()
        
        # 添加第一个服务的依赖
        for dep in self.dependencies:
            if dep.service_name == startup_order[0]:
                current_dependencies.add(dep.depends_on)
        
        for service in startup_order[1:]:
            service_dependencies = set()
            for dep in self.dependencies:
                if dep.service_name == service:
                    service_dependencies.add(dep.depends_on)
            
            # 检查是否可以与当前阶段并行启动
            if service_dependencies.issubset(current_dependencies.union(current_stage)):
                current_stage.append(service)
                current_dependencies.update(service_dependencies)
            else:
                # 创建新阶段
                stages.append(StartupOrder(stage=len(stages) + 1, services=current_stage))
                current_stage = [service]
                current_dependencies = service_dependencies
        
        # 添加最后一个阶段
        if current_stage:
            stages.append(StartupOrder(stage=len(stages) + 1, services=current_stage))
        
        return stages
    
    def validate_dependencies(self) -> List[str]:
        """验证依赖关系"""
        errors = []
        
        # 检查循环依赖
        try:
            self.calculate_startup_order()
        except ValueError as e:
            errors.append(str(e))
        
        # 检查自依赖
        for dep in self.dependencies:
            if dep.service_name == dep.depends_on:
                errors.append(f"服务 {dep.service_name} 不能依赖自己")
        
        # 检查不存在的服务
        for dep in self.dependencies:
            if dep.service_name not in self.services:
                errors.append(f"服务 {dep.service_name} 不存在")
            if dep.depends_on not in self.services:
                errors.append(f"依赖服务 {dep.depends_on} 不存在")
        
        return errors
    
    def get_service_dependencies(self, service_name: str) -> List[ServiceDependency]:
        """获取服务的所有依赖"""
        return [dep for dep in self.dependencies if dep.service_name == service_name]
    
    def get_dependent_services(self, service_name: str) -> List[str]:
        """获取依赖指定服务的所有服务"""
        return [dep.service_name for dep in self.dependencies if dep.depends_on == service_name]
    
    def generate_dependency_graph(self) -> str:
        """生成依赖图（DOT格式）"""
        dot_lines = ["digraph service_dependencies {"]
        dot_lines.append("  rankdir=LR;")
        dot_lines.append("  node [shape=box];")
        
        # 添加节点
        for service in self.services:
            dot_lines.append(f'  "{service}";')
        
        # 添加边
        for dep in self.dependencies:
            if dep.dependency_type == DependencyType.STARTS_BEFORE:
                style = "solid"
            elif dep.dependency_type == DependencyType.HEALTHY_BEFORE:
                style = "dashed"
            else:
                style = "dotted"
            
            label = dep.dependency_type.value
            dot_lines.append(f'  "{dep.depends_on}" -> "{dep.service_name}" [style={style}, label="{label}"];')
        
        dot_lines.append("}")
        
        return "\n".join(dot_lines)

# 使用示例
orchestrator = ServiceOrchestrator()

# 添加服务依赖
orchestrator.add_dependency("web", "database", DependencyType.STARTS_BEFORE)
orchestrator.add_dependency("web", "cache", DependencyType.STARTS_BEFORE)
orchestrator.add_dependency("worker", "database", DependencyType.HEALTHY_BEFORE)
orchestrator.add_dependency("worker", "queue", DependencyType.STARTS_BEFORE)
orchestrator.add_dependency("queue", "cache", DependencyType.STARTS_BEFORE)

# 验证依赖
errors = orchestrator.validate_dependencies()
if errors:
    print("依赖验证错误:")
    for error in errors:
        print(f"  - {error}")
else:
    print("依赖验证通过")

# 计算启动顺序
startup_order = orchestrator.calculate_startup_order()
print("启动顺序:")
for stage in startup_order:
    print(f"  阶段 {stage.stage}: {', '.join(stage.services)}")

# 生成依赖图
dependency_graph = orchestrator.generate_dependency_graph()
print("\n依赖图:")
print(dependency_graph)

# 获取服务依赖
web_deps = orchestrator.get_service_dependencies("web")
print(f"\nWeb服务的依赖: {[dep.depends_on for dep in web_deps]}")

# 获取依赖服务
db_dependents = orchestrator.get_dependent_services("database")
print(f"依赖数据库的服务: {db_dependents}")
```

## 参考资源

### Docker Compose文档
- [Docker Compose官方文档](https://docs.docker.com/compose/)
- [Docker Compose文件参考](https://docs.docker.com/compose/compose-file/)
- [Docker Compose最佳实践](https://docs.docker.com/compose/production/)

### 容器编排
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [Kubernetes](https://kubernetes.io/)
- [Docker Compose vs Kubernetes](https://www.docker.com/blog/docker-compose-vs-kubernetes/)

### 服务模板
- [Docker Hub官方镜像](https://hub.docker.com/)
- [Bitnami容器镜像](https://github.com/bitnami/containers)
- [Docker Compose示例](https://github.com/docker/awesome-compose)

### 环境管理
- [Docker环境变量](https://docs.docker.com/compose/environment-variables/)
- [Docker配置管理](https://docs.docker.com/compose/configuration/)
- [多环境部署](https://docs.docker.com/compose/production/)
