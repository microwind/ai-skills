# 数据库连接池参考文档

## 数据库连接池概述

### 什么是数据库连接池
数据库连接池是一种数据库连接管理技术，通过预先创建并维护一组数据库连接，提供给应用程序复用，从而提高数据库访问性能和资源利用率。连接池管理连接的创建、分配、回收和销毁，避免频繁创建和销毁连接的开销，同时控制并发连接数，防止数据库过载。连接池是现代应用程序数据库访问层的核心组件，对系统性能和稳定性至关重要。

### 主要功能
- **连接复用**: 复用已建立的数据库连接，减少连接创建和销毁的开销
- **并发控制**: 控制同时活跃的连接数，防止数据库过载
- **自动管理**: 自动处理连接的创建、验证、回收和销毁
- **故障恢复**: 自动检测和处理连接故障，提供连接恢复机制
- **性能监控**: 监控连接池状态和性能指标，提供优化建议
- **负载均衡**: 支持多数据库服务器的负载均衡和故障转移

## 数据库连接池核心

### 连接池引擎
```python
# database_connection_pooling.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import socket
import ssl
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor
import statistics
import math
import weakref
import gc
import mysql.connector
import psycopg2
import pymongo
import redis
from contextlib import contextmanager

class PoolType(Enum):
    """连接池类型枚举"""
    GENERIC = "generic"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CUSTOM = "custom"

class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CUSTOM = "custom"

class ConnectionState(Enum):
    """连接状态枚举"""
    IDLE = "idle"
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    INVALID = "invalid"
    DESTROYED = "destroyed"

@dataclass
class DatabaseConfig:
    """数据库配置"""
    config_id: str
    name: str
    type: DatabaseType
    host: str
    port: int
    username: str
    password: str
    database: str
    charset: str = "utf8mb4"
    timezone: str = "UTC"
    ssl_config: Dict[str, Any] = field(default_factory=dict)
    connection_params: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    auto_reconnect: bool = True
    reconnect_attempts: int = 3
    reconnect_delay: float = 1.0

@dataclass
class PoolConfig:
    """连接池配置"""
    pool_id: str
    name: str
    description: str
    database_config: DatabaseConfig
    min_connections: int = 5
    max_connections: int = 20
    initial_connections: int = 5
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    max_lifetime: float = 3600.0
    validation_query: str = "SELECT 1"
    validation_interval: float = 30.0
    auto_extend: bool = True
    extend_factor: float = 1.5
    extend_max: int = 50
    shrink_idle: bool = True
    shrink_threshold: float = 0.8
    shrink_interval: float = 60.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ConnectionWrapper:
    """连接包装器"""
    connection_id: str
    raw_connection: Any
    state: ConnectionState
    created_at: datetime
    last_used_at: datetime
    last_validated_at: datetime
    usage_count: int = 0
    error_count: int = 0
    is_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PoolStatistics:
    """连接池统计"""
    pool_id: str
    timestamp: datetime
    total_connections: int
    active_connections: int
    idle_connections: int
    invalid_connections: int
    connections_created: int
    connections_destroyed: int
    checkout_count: int
    checkout_failures: int
    average_checkout_time: float
    average_connection_age: float
    peak_connections: int

class DatabaseConnection:
    """数据库连接"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.raw_connection = None
        self.last_activity = datetime.now()
    
    def connect(self):
        """建立连接"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                self._connect_mysql()
            elif self.config.type == DatabaseType.POSTGRESQL:
                self._connect_postgresql()
            elif self.config.type == DatabaseType.MONGODB:
                self._connect_mongodb()
            elif self.config.type == DatabaseType.REDIS:
                self._connect_redis()
            else:
                raise ValueError(f"不支持的数据库类型: {self.config.type}")
            
            self.last_activity = datetime.now()
            self.logger.debug(f"数据库连接成功: {self.config.name}")
        
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise
    
    def _connect_mysql(self):
        """连接MySQL"""
        connection_params = {
            'host': self.config.host,
            'port': self.config.port,
            'user': self.config.username,
            'password': self.config.password,
            'database': self.config.database,
            'charset': self.config.charset,
            'connect_timeout': self.config.timeout,
            'autocommit': True,
            **self.config.connection_params
        }
        
        if self.config.ssl_config:
            connection_params.update(self.config.ssl_config)
        
        self.raw_connection = mysql.connector.connect(**connection_params)
    
    def _connect_postgresql(self):
        """连接PostgreSQL"""
        connection_params = {
            'host': self.config.host,
            'port': self.config.port,
            'user': self.config.username,
            'password': self.config.password,
            'database': self.config.database,
            'connect_timeout': self.config.timeout,
            **self.config.connection_params
        }
        
        if self.config.ssl_config:
            connection_params.update(self.config.ssl_config)
        
        self.raw_connection = psycopg2.connect(**connection_params)
    
    def _connect_mongodb(self):
        """连接MongoDB"""
        connection_params = {
            'host': self.config.host,
            'port': self.config.port,
            'username': self.config.username,
            'password': self.config.password,
            **self.config.connection_params
        }
        
        if self.config.ssl_config:
            connection_params.update(self.config.ssl_config)
        
        client = pymongo.MongoClient(**connection_params)
        self.raw_connection = client[self.config.database]
    
    def _connect_redis(self):
        """连接Redis"""
        connection_params = {
            'host': self.config.host,
            'port': self.config.port,
            'password': self.config.password,
            'decode_responses': True,
            **self.config.connection_params
        }
        
        if self.config.ssl_config:
            connection_params.update(self.config.ssl_config)
        
        self.raw_connection = redis.Redis(**connection_params)
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.raw_connection:
                if self.config.type == DatabaseType.MYSQL:
                    self.raw_connection.close()
                elif self.config.type == DatabaseType.POSTGRESQL:
                    self.raw_connection.close()
                elif self.config.type == DatabaseType.MONGODB:
                    self.raw_connection.client.close()
                elif self.config.type == DatabaseType.REDIS:
                    self.raw_connection.close()
                
                self.raw_connection = None
                self.logger.debug(f"数据库连接断开: {self.config.name}")
        
        except Exception as e:
            self.logger.error(f"数据库连接断开失败: {e}")
    
    def is_valid(self) -> bool:
        """检查连接是否有效"""
        try:
            if not self.raw_connection:
                return False
            
            if self.config.type == DatabaseType.MYSQL:
                cursor = self.raw_connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            elif self.config.type == DatabaseType.POSTGRESQL:
                cursor = self.raw_connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            elif self.config.type == DatabaseType.MONGODB:
                self.raw_connection.command('ping')
            elif self.config.type == DatabaseType.REDIS:
                self.raw_connection.ping()
            
            self.last_activity = datetime.now()
            return True
        
        except Exception as e:
            self.logger.debug(f"连接验证失败: {e}")
            return False
    
    def execute_query(self, query: str, params: Any = None) -> Any:
        """执行查询"""
        try:
            if not self.raw_connection:
                self.connect()
            
            self.last_activity = datetime.now()
            
            if self.config.type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
                cursor = self.raw_connection.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                
                cursor.close()
                return result
            
            elif self.config.type == DatabaseType.MONGODB:
                return self.raw_connection.command(query)
            
            elif self.config.type == DatabaseType.REDIS:
                return self.raw_connection.execute_command(query)
        
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            raise

class ConnectionPool:
    """连接池"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 连接管理
        self.connections = deque()
        self.active_connections = set()
        self.lock = threading.RLock()
        
        # 统计信息
        self.statistics = {
            'total_created': 0,
            'total_destroyed': 0,
            'checkout_count': 0,
            'checkout_failures': 0,
            'checkout_times': deque(maxlen=1000),
            'peak_connections': 0
        }
        
        # 后台任务
        self.running = False
        self.maintenance_thread = None
        self.validation_thread = None
        
        # 初始化连接池
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        try:
            # 创建初始连接
            for _ in range(self.config.initial_connections):
                self._create_connection()
            
            # 启动后台任务
            self.start_maintenance()
            
            self.logger.info(f"连接池初始化完成: {self.config.name}")
        
        except Exception as e:
            self.logger.error(f"连接池初始化失败: {e}")
            raise
    
    def start_maintenance(self):
        """启动维护任务"""
        if not self.running:
            self.running = True
            
            # 启动连接维护线程
            self.maintenance_thread = threading.Thread(
                target=self._maintenance_worker,
                daemon=True
            )
            self.maintenance_thread.start()
            
            # 启动连接验证线程
            self.validation_thread = threading.Thread(
                target=self._validation_worker,
                daemon=True
            )
            self.validation_thread.start()
            
            self.logger.info("连接池维护任务启动")
    
    def stop_maintenance(self):
        """停止维护任务"""
        self.running = False
        
        if self.maintenance_thread:
            self.maintenance_thread.join()
        
        if self.validation_thread:
            self.validation_thread.join()
        
        self.logger.info("连接池维护任务停止")
    
    @contextmanager
    def get_connection(self, timeout: float = None):
        """获取连接上下文管理器"""
        connection = None
        try:
            connection = self.checkout_connection(timeout)
            yield connection
        finally:
            if connection:
                self.checkin_connection(connection)
    
    def checkout_connection(self, timeout: float = None) -> DatabaseConnection:
        """检出连接"""
        timeout = timeout or self.config.connection_timeout
        start_time = time.time()
        
        try:
            with self.lock:
                # 尝试获取空闲连接
                while time.time() - start_time < timeout:
                    # 清理无效连接
                    self._cleanup_invalid_connections()
                    
                    # 尝试获取空闲连接
                    if self.connections:
                        connection = self.connections.popleft()
                        if connection.is_valid():
                            connection.state = ConnectionState.ACTIVE
                            self.active_connections.add(connection)
                            self.statistics['checkout_count'] += 1
                            self.statistics['checkout_times'].append(time.time() - start_time)
                            
                            # 更新峰值连接数
                            current_total = len(self.active_connections) + len(self.connections)
                            if current_total > self.statistics['peak_connections']:
                                self.statistics['peak_connections'] = current_total
                            
                            self.logger.debug(f"连接检出成功: {connection.connection_id}")
                            return connection
                        else:
                            # 连接无效，销毁并继续
                            self._destroy_connection(connection)
                    
                    # 如果没有空闲连接，尝试创建新连接
                    if self._can_create_connection():
                        connection = self._create_connection()
                        connection.state = ConnectionState.ACTIVE
                        self.active_connections.add(connection)
                        self.statistics['checkout_count'] += 1
                        self.statistics['checkout_times'].append(time.time() - start_time)
                        
                        # 更新峰值连接数
                        current_total = len(self.active_connections) + len(self.connections)
                        if current_total > self.statistics['peak_connections']:
                            self.statistics['peak_connections'] = current_total
                        
                        self.logger.debug(f"新连接创建并检出: {connection.connection_id}")
                        return connection
                    
                    # 等待连接释放
                    time.sleep(0.1)
                
                # 超时
                self.statistics['checkout_failures'] += 1
                raise TimeoutError(f"获取连接超时: {timeout}秒")
        
        except Exception as e:
            self.logger.error(f"连接检出失败: {e}")
            raise
    
    def checkin_connection(self, connection: DatabaseConnection):
        """检入连接"""
        try:
            with self.lock:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
                    
                    if connection.is_valid():
                        connection.state = ConnectionState.IDLE
                        connection.last_used_at = datetime.now()
                        self.connections.append(connection)
                        self.logger.debug(f"连接检入成功: {connection.connection_id}")
                    else:
                        # 连接无效，销毁
                        self._destroy_connection(connection)
                        self.logger.debug(f"无效连接销毁: {connection.connection_id}")
                else:
                    self.logger.warning(f"连接不在活跃列表中: {connection.connection_id}")
        
        except Exception as e:
            self.logger.error(f"连接检入失败: {e}")
    
    def _can_create_connection(self) -> bool:
        """检查是否可以创建新连接"""
        total_connections = len(self.active_connections) + len(self.connections)
        return total_connections < self.config.max_connections
    
    def _create_connection(self) -> DatabaseConnection:
        """创建新连接"""
        try:
            db_connection = DatabaseConnection(self.config.database_config)
            db_connection.connect()
            
            wrapper = ConnectionWrapper(
                connection_id=str(uuid.uuid4()),
                raw_connection=db_connection,
                state=ConnectionState.IDLE,
                created_at=datetime.now(),
                last_used_at=datetime.now(),
                last_validated_at=datetime.now()
            )
            
            self.statistics['total_created'] += 1
            self.logger.debug(f"新连接创建: {wrapper.connection_id}")
            
            return wrapper
        
        except Exception as e:
            self.logger.error(f"连接创建失败: {e}")
            raise
    
    def _destroy_connection(self, connection: ConnectionWrapper):
        """销毁连接"""
        try:
            if connection.raw_connection:
                connection.raw_connection.disconnect()
            
            connection.state = ConnectionState.DESTROYED
            self.statistics['total_destroyed'] += 1
            self.logger.debug(f"连接销毁: {connection.connection_id}")
        
        except Exception as e:
            self.logger.error(f"连接销毁失败: {e}")
    
    def _cleanup_invalid_connections(self):
        """清理无效连接"""
        invalid_connections = []
        
        for connection in list(self.connections):
            if not connection.is_valid():
                invalid_connections.append(connection)
        
        for connection in invalid_connections:
            self.connections.remove(connection)
            self._destroy_connection(connection)
        
        if invalid_connections:
            self.logger.debug(f"清理了 {len(invalid_connections)} 个无效连接")
    
    def _maintenance_worker(self):
        """维护工作线程"""
        while self.running:
            try:
                self._perform_maintenance()
                time.sleep(self.config.shrink_interval)
            
            except Exception as e:
                self.logger.error(f"维护工作错误: {e}")
                time.sleep(10)
    
    def _perform_maintenance(self):
        """执行维护任务"""
        with self.lock:
            # 清理过期连接
            self._cleanup_expired_connections()
            
            # 自动收缩连接池
            if self.config.shrink_idle:
                self._shrink_pool()
            
            # 自动扩展连接池
            if self.config.auto_extend:
                self._extend_pool()
    
    def _cleanup_expired_connections(self):
        """清理过期连接"""
        current_time = datetime.now()
        expired_connections = []
        
        for connection in list(self.connections):
            # 检查连接是否超过最大生命周期
            if (current_time - connection.created_at).total_seconds() > self.config.max_lifetime:
                expired_connections.append(connection)
            # 检查连接是否空闲超时
            elif (current_time - connection.last_used_at).total_seconds() > self.config.idle_timeout:
                expired_connections.append(connection)
        
        for connection in expired_connections:
            if connection in self.connections:
                self.connections.remove(connection)
                self._destroy_connection(connection)
        
        if expired_connections:
            self.logger.debug(f"清理了 {len(expired_connections)} 个过期连接")
    
    def _shrink_pool(self):
        """收缩连接池"""
        total_connections = len(self.active_connections) + len(self.connections)
        idle_connections = len(self.connections)
        
        # 如果空闲连接数超过阈值，收缩连接池
        if (idle_connections > self.config.min_connections and 
            idle_connections / total_connections > self.config.shrink_threshold):
            
            # 计算要销毁的连接数
            target_idle = max(self.config.min_connections, 
                           int(total_connections * self.config.shrink_threshold))
            destroy_count = idle_connections - target_idle
            
            for _ in range(min(destroy_count, len(self.connections))):
                if self.connections:
                    connection = self.connections.popleft()
                    self._destroy_connection(connection)
            
            if destroy_count > 0:
                self.logger.debug(f"收缩连接池，销毁了 {destroy_count} 个连接")
    
    def _extend_pool(self):
        """扩展连接池"""
        total_connections = len(self.active_connections) + len(self.connections)
        
        # 如果连接数接近最大值且所有连接都在使用，扩展连接池
        if (total_connections < self.config.extend_max and 
            len(self.active_connections) == total_connections):
            
            # 计算扩展后的连接数
            new_max = min(self.config.extend_max, 
                         int(total_connections * self.config.extend_factor))
            create_count = new_max - total_connections
            
            for _ in range(create_count):
                if self._can_create_connection():
                    connection = self._create_connection()
                    self.connections.append(connection)
                else:
                    break
            
            if create_count > 0:
                self.logger.debug(f"扩展连接池，创建了 {create_count} 个连接")
    
    def _validation_worker(self):
        """验证工作线程"""
        while self.running:
            try:
                self._perform_validation()
                time.sleep(self.config.validation_interval)
            
            except Exception as e:
                self.logger.error(f"验证工作错误: {e}")
                time.sleep(10)
    
    def _perform_validation(self):
        """执行连接验证"""
        with self.lock:
            validated_connections = 0
            invalid_connections = []
            
            for connection in list(self.connections):
                try:
                    if connection.is_valid():
                        connection.last_validated_at = datetime.now()
                        validated_connections += 1
                    else:
                        invalid_connections.append(connection)
                
                except Exception as e:
                    self.logger.debug(f"连接验证异常: {e}")
                    invalid_connections.append(connection)
            
            # 销毁无效连接
            for connection in invalid_connections:
                if connection in self.connections:
                    self.connections.remove(connection)
                    self._destroy_connection(connection)
            
            if invalid_connections:
                self.logger.debug(f"验证发现 {len(invalid_connections)} 个无效连接")
    
    def get_statistics(self) -> PoolStatistics:
        """获取连接池统计信息"""
        with self.lock:
            total_connections = len(self.active_connections) + len(self.connections)
            active_connections = len(self.active_connections)
            idle_connections = len(self.connections)
            
            # 计算平均检出时间
            avg_checkout_time = 0.0
            if self.statistics['checkout_times']:
                avg_checkout_time = statistics.mean(self.statistics['checkout_times'])
            
            # 计算平均连接年龄
            avg_connection_age = 0.0
            all_connections = list(self.active_connections) + list(self.connections)
            if all_connections:
                ages = [(datetime.now() - conn.created_at).total_seconds() 
                        for conn in all_connections]
                avg_connection_age = statistics.mean(ages)
            
            return PoolStatistics(
                pool_id=self.config.pool_id,
                timestamp=datetime.now(),
                total_connections=total_connections,
                active_connections=active_connections,
                idle_connections=idle_connections,
                invalid_connections=0,  # 实时计算
                connections_created=self.statistics['total_created'],
                connections_destroyed=self.statistics['total_destroyed'],
                checkout_count=self.statistics['checkout_count'],
                checkout_failures=self.statistics['checkout_failures'],
                average_checkout_time=avg_checkout_time,
                average_connection_age=avg_connection_age,
                peak_connections=self.statistics['peak_connections']
            )
    
    def close(self):
        """关闭连接池"""
        try:
            # 停止维护任务
            self.stop_maintenance()
            
            # 销毁所有连接
            with self.lock:
                # 销毁活跃连接
                for connection in list(self.active_connections):
                    self._destroy_connection(connection)
                self.active_connections.clear()
                
                # 销毁空闲连接
                for connection in list(self.connections):
                    self._destroy_connection(connection)
                self.connections.clear()
            
            self.logger.info(f"连接池关闭: {self.config.name}")
        
        except Exception as e:
            self.logger.error(f"连接池关闭失败: {e}")

class ConnectionPoolManager:
    """连接池管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pools = {}
        self.lock = threading.RLock()
        self.statistics = defaultdict(list)
    
    def create_pool(self, config: PoolConfig) -> bool:
        """创建连接池"""
        try:
            with self.lock:
                if config.pool_id in self.pools:
                    self.logger.warning(f"连接池已存在: {config.pool_id}")
                    return False
                
                pool = ConnectionPool(config)
                self.pools[config.pool_id] = pool
                
                self.logger.info(f"连接池创建成功: {config.name}")
                return True
        
        except Exception as e:
            self.logger.error(f"连接池创建失败: {e}")
            return False
    
    def get_pool(self, pool_id: str) -> Optional[ConnectionPool]:
        """获取连接池"""
        with self.lock:
            return self.pools.get(pool_id)
    
    def remove_pool(self, pool_id: str) -> bool:
        """移除连接池"""
        try:
            with self.lock:
                pool = self.pools.get(pool_id)
                if pool:
                    pool.close()
                    del self.pools[pool_id]
                    self.logger.info(f"连接池移除成功: {pool_id}")
                    return True
                else:
                    self.logger.warning(f"连接池不存在: {pool_id}")
                    return False
        
        except Exception as e:
            self.logger.error(f"连接池移除失败: {e}")
            return False
    
    def list_pools(self) -> List[str]:
        """列出所有连接池ID"""
        with self.lock:
            return list(self.pools.keys())
    
    def get_all_statistics(self) -> Dict[str, PoolStatistics]:
        """获取所有连接池统计信息"""
        statistics = {}
        
        with self.lock:
            for pool_id, pool in self.pools.items():
                statistics[pool_id] = pool.get_statistics()
        
        return statistics
    
    def close_all(self):
        """关闭所有连接池"""
        with self.lock:
            for pool in self.pools.values():
                pool.close()
            self.pools.clear()
        
        self.logger.info("所有连接池已关闭")

class ConnectionPoolBuilder:
    """连接池构建器"""
    
    def __init__(self):
        self.config = PoolConfig(
            pool_id=str(uuid.uuid4()),
            name="",
            description="",
            database_config=None
        )
    
    def with_name(self, name: str) -> 'ConnectionPoolBuilder':
        """设置连接池名称"""
        self.config.name = name
        return self
    
    def with_description(self, description: str) -> 'ConnectionPoolBuilder':
        """设置连接池描述"""
        self.config.description = description
        return self
    
    def with_database_config(self, db_config: DatabaseConfig) -> 'ConnectionPoolBuilder':
        """设置数据库配置"""
        self.config.database_config = db_config
        return self
    
    def with_size(self, min_connections: int, max_connections: int, 
                  initial_connections: int = None) -> 'ConnectionPoolBuilder':
        """设置连接池大小"""
        self.config.min_connections = min_connections
        self.config.max_connections = max_connections
        if initial_connections is not None:
            self.config.initial_connections = initial_connections
        else:
            self.config.initial_connections = min_connections
        return self
    
    def with_timeout(self, connection_timeout: float, idle_timeout: float = None,
                     max_lifetime: float = None) -> 'ConnectionPoolBuilder':
        """设置超时配置"""
        self.config.connection_timeout = connection_timeout
        if idle_timeout is not None:
            self.config.idle_timeout = idle_timeout
        if max_lifetime is not None:
            self.config.max_lifetime = max_lifetime
        return self
    
    def with_validation(self, validation_query: str, 
                       validation_interval: float) -> 'ConnectionPoolBuilder':
        """设置验证配置"""
        self.config.validation_query = validation_query
        self.config.validation_interval = validation_interval
        return self
    
    def with_auto_scaling(self, auto_extend: bool, extend_factor: float,
                         extend_max: int) -> 'ConnectionPoolBuilder':
        """设置自动扩展配置"""
        self.config.auto_extend = auto_extend
        self.config.extend_factor = extend_factor
        self.config.extend_max = extend_max
        return self
    
    def build(self) -> PoolConfig:
        """构建连接池配置"""
        if not self.config.name:
            raise ValueError("连接池名称不能为空")
        
        if not self.config.database_config:
            raise ValueError("数据库配置不能为空")
        
        return self.config

# 使用示例
# 创建连接池管理器
manager = ConnectionPoolManager()

# 创建数据库配置
db_config = DatabaseConfig(
    config_id=str(uuid.uuid4()),
    name="test_mysql",
    type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    username="root",
    password="password",
    database="testdb",
    charset="utf8mb4",
    timeout=30,
    auto_reconnect=True
)

# 使用构建器创建连接池配置
pool_config = (ConnectionPoolBuilder()
               .with_name("main_pool")
               .with_description("主要数据库连接池")
               .with_database_config(db_config)
               .with_size(min_connections=5, max_connections=20)
               .with_timeout(connection_timeout=30.0, idle_timeout=300.0)
               .with_validation("SELECT 1", 30.0)
               .with_auto_scaling(True, 1.5, 50)
               .build())

# 创建连接池
if manager.create_pool(pool_config):
    print("连接池创建成功")
    
    # 获取连接池
    pool = manager.get_pool(pool_config.pool_id)
    
    # 使用连接
    with pool.get_connection() as connection:
        result = connection.execute_query("SELECT COUNT(*) FROM users")
        print(f"查询结果: {result}")
    
    # 获取统计信息
    stats = pool.get_statistics()
    print(f"连接池统计: {stats.total_connections} 总连接, "
          f"{stats.active_connections} 活跃连接, "
          f"{stats.idle_connections} 空闲连接")
    
    # 关闭连接池
    manager.remove_pool(pool_config.pool_id)
else:
    print("连接池创建失败")
```

## 参考资源

### 数据库连接池文档
- [MySQL连接器文档](https://dev.mysql.com/doc/connector-python/en/)
- [PostgreSQL适配器文档](https://www.psycopg.org/docs/)
- [MongoDB驱动文档](https://pymongo.readthedocs.io/)
- [Redis客户端文档](https://redis-py.readthedocs.io/)

### 连接池实现
- [SQLAlchemy连接池](https://docs.sqlalchemy.org/en/14/core/pooling.html)
- [Django数据库连接池](https://docs.djangoproject.com/en/stable/ref/databases/)
- [Apache Commons DBCP](https://commons.apache.org/proper/commons-dbcp/)
- [HikariCP](https://github.com/brettwooldridge/HikariCP)

### 性能优化
- [数据库连接池最佳实践](https://docs.microsoft.com/en-us/azure/azure-sql/database/connection-pooling)
- [连接池性能调优](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [连接池监控和调优](https://dev.mysql.com/doc/refman/8.0/en/connection-pooling.html)

### 监控和诊断
- [连接池监控指标](https://prometheus.io/docs/practices/naming/)
- [数据库性能监控](https://www.percona.com/blog/mysql-connection-pooling-best-practices/)
- [连接池故障排除](https://stackoverflow.com/questions/28409120/connection-pooling-best-practices)

### 安全和可靠性
- [数据库连接安全](https://owasp.org/www-project-cheat-sheets/cheatsheets/Database_Security_Cheat_Sheet.html)
- [连接池故障恢复](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgdba/managing-connections.html)
- [高可用性连接池](https://docs.microsoft.com/en-us/azure/azure-sql/database/high-availability-strategy)
