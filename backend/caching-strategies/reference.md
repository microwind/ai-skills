# 缓存策略参考文档

## 缓存策略概述

### 什么是缓存策略
缓存策略是一种用于提高系统性能的数据存储和管理技术，通过将频繁访问的数据存储在快速访问的存储介质中，减少对后端数据源的访问次数。该技能涵盖了多种缓存算法、分布式缓存、缓存一致性、性能优化和监控等功能，帮助开发者构建高效、可靠的缓存系统。

### 主要功能
- **多种缓存策略**: 支持LRU、LFU、FIFO、TTL等多种缓存淘汰策略
- **分布式缓存**: 支持Redis、Memcached等分布式缓存系统
- **缓存一致性**: 提供强一致性、最终一致性等多种一致性保证
- **性能优化**: 包含缓存预热、批量操作、压缩存储等优化技术
- **监控告警**: 实时监控缓存命中率、响应时间、内存使用等指标

## 缓存引擎核心

### 缓存管理器
```python
# cache_manager.py
import time
import threading
import hashlib
import json
import pickle
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from collections import OrderedDict
import redis
import memcache
from abc import ABC, abstractmethod

class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    RANDOM = "random"

class CacheStatus(Enum):
    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    EVICTED = "evicted"

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheConfig:
    # 基础配置
    max_size: int = 1000
    max_memory: int = 100 * 1024 * 1024  # 100MB
    default_ttl: int = 3600  # 1小时
    
    # 策略配置
    strategy: CacheStrategy = CacheStrategy.LRU
    eviction_policy: str = "auto"
    
    # 性能配置
    enable_compression: bool = False
    compression_threshold: int = 1024
    enable_serialization: bool = True
    serialization_format: str = "pickle"
    
    # 监控配置
    enable_monitoring: bool = True
    monitoring_interval: float = 60.0
    
    # 分布式配置
    distributed: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

class CacheBackend(ABC):
    """缓存后端抽象基类"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        pass
    
    @abstractmethod
    def size(self) -> int:
        pass

class MemoryCache(CacheBackend):
    """内存缓存实现"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats['misses'] += 1
                return None
            
            # 检查是否过期
            if entry.expires_at and datetime.now() > entry.expires_at:
                self._remove_entry(key)
                self._stats['misses'] += 1
                return None
            
            # 更新访问信息
            entry.accessed_at = datetime.now()
            entry.access_count += 1
            
            # 更新访问顺序（LRU）
            if self.config.strategy == CacheStrategy.LRU:
                self._access_order.move_to_end(key)
            
            self._stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                # 计算值大小
                serialized_value = self._serialize(value)
                size = len(serialized_value)
                
                # 检查内存限制
                if size > self.config.max_memory:
                    self.logger.warning(f"缓存值过大，无法存储: {key}")
                    return False
                
                # 检查是否需要淘汰
                self._ensure_capacity(size)
                
                # 创建缓存条目
                expires_at = None
                if ttl:
                    expires_at = datetime.now() + timedelta(seconds=ttl)
                elif self.config.default_ttl:
                    expires_at = datetime.now() + timedelta(seconds=self.config.default_ttl)
                
                entry = CacheEntry(
                    key=key,
                    value=value,
                    expires_at=expires_at,
                    size=size
                )
                
                # 存储缓存条目
                self._cache[key] = entry
                if self.config.strategy == CacheStrategy.LRU:
                    self._access_order[key] = True
                
                self._stats['sets'] += 1
                return True
            
            except Exception as e:
                self.logger.error(f"设置缓存失败: {key}, 错误: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                self._stats['deletes'] += 1
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            # 检查是否过期
            if entry.expires_at and datetime.now() > entry.expires_at:
                self._remove_entry(key)
                return False
            
            return True
    
    def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._stats['sets'] = 0
            return True
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def _ensure_capacity(self, required_size: int):
        """确保有足够容量"""
        current_size = sum(entry.size for entry in self._cache.values())
        
        while (len(self._cache) >= self.config.max_size or 
               current_size + required_size > self.config.max_memory):
            
            if not self._cache:
                break
            
            # 淘汰缓存条目
            evicted_key = self._select_eviction_key()
            if evicted_key:
                current_size -= self._cache[evicted_key].size
                self._remove_entry(evicted_key)
                self._stats['evictions'] += 1
            else:
                break
    
    def _select_eviction_key(self) -> Optional[str]:
        """选择淘汰的缓存键"""
        if not self._cache:
            return None
        
        if self.config.strategy == CacheStrategy.LRU:
            # LRU: 淘汰最近最少使用的
            return next(iter(self._access_order))
        
        elif self.config.strategy == CacheStrategy.LFU:
            # LFU: 淘汰访问次数最少的
            return min(self._cache.keys(), 
                      key=lambda k: self._cache[k].access_count)
        
        elif self.config.strategy == CacheStrategy.FIFO:
            # FIFO: 淘汰最早创建的
            return min(self._cache.keys(), 
                      key=lambda k: self._cache[k].created_at)
        
        elif self.config.strategy == CacheStrategy.TTL:
            # TTL: 淘汰最早过期的
            expired_keys = [k for k, v in self._cache.items() 
                           if v.expires_at and v.expires_at <= datetime.now()]
            if expired_keys:
                return expired_keys[0]
            return next(iter(self._cache))
        
        else:  # RANDOM
            import random
            return random.choice(list(self._cache.keys()))
    
    def _remove_entry(self, key: str):
        """移除缓存条目"""
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            del self._access_order[key]
    
    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        if not self.config.enable_serialization:
            return str(value).encode('utf-8')
        
        if self.config.serialization_format == "pickle":
            return pickle.dumps(value)
        elif self.config.serialization_format == "json":
            return json.dumps(value, default=str).encode('utf-8')
        else:
            return str(value).encode('utf-8')
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'hit_rate': hit_rate,
                'total_requests': total_requests,
                'cache_size': len(self._cache),
                'memory_usage': sum(entry.size for entry in self._cache.values()),
                'stats': self._stats.copy()
            }

class RedisCache(CacheBackend):
    """Redis缓存实现"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._redis = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            password=config.redis_password,
            decode_responses=False
        )
        self._key_prefix = "cache:"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            redis_key = self._key_prefix + key
            value = self._redis.get(redis_key)
            
            if value is None:
                return None
            
            return self._deserialize(value)
        
        except Exception as e:
            self.logger.error(f"Redis获取缓存失败: {key}, 错误: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            redis_key = self._key_prefix + key
            serialized_value = self._serialize(value)
            
            if ttl:
                return self._redis.setex(redis_key, ttl, serialized_value)
            else:
                return self._redis.set(redis_key, serialized_value)
        
        except Exception as e:
            self.logger.error(f"Redis设置缓存失败: {key}, 错误: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        try:
            redis_key = self._key_prefix + key
            return bool(self._redis.delete(redis_key))
        except Exception as e:
            self.logger.error(f"Redis删除缓存失败: {key}, 错误: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            redis_key = self._key_prefix + key
            return bool(self._redis.exists(redis_key))
        except Exception as e:
            self.logger.error(f"Redis检查缓存存在失败: {key}, 错误: {e}")
            return False
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            pattern = self._key_prefix + "*"
            keys = self._redis.keys(pattern)
            if keys:
                return bool(self._redis.delete(*keys))
            return True
        except Exception as e:
            self.logger.error(f"Redis清空缓存失败: {e}")
            return False
    
    def size(self) -> int:
        """获取缓存大小"""
        try:
            pattern = self._key_prefix + "*"
            keys = self._redis.keys(pattern)
            return len(keys)
        except Exception as e:
            self.logger.error(f"Redis获取缓存大小失败: {e}")
            return 0
    
    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        if self.config.serialization_format == "pickle":
            return pickle.dumps(value)
        elif self.config.serialization_format == "json":
            return json.dumps(value, default=str).encode('utf-8')
        else:
            return str(value).encode('utf-8')
    
    def _deserialize(self, value: bytes) -> Any:
        """反序列化值"""
        if self.config.serialization_format == "pickle":
            return pickle.loads(value)
        elif self.config.serialization_format == "json":
            return json.loads(value.decode('utf-8'))
        else:
            return value.decode('utf-8')

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._backend = self._create_backend()
        self._monitor_thread = None
        self._running = False
    
    def _create_backend(self) -> CacheBackend:
        """创建缓存后端"""
        if self.config.distributed:
            return RedisCache(self.config)
        else:
            return MemoryCache(self.config)
    
    def start(self):
        """启动缓存管理器"""
        self._running = True
        if self.config.enable_monitoring:
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self._monitor_thread.start()
        self.logger.info("缓存管理器启动")
    
    def stop(self):
        """停止缓存管理器"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.logger.info("缓存管理器停止")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        return self._backend.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        return self._backend.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """删除缓存条目"""
        return self._backend.delete(key)
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self._backend.exists(key)
    
    def clear(self) -> bool:
        """清空缓存"""
        return self._backend.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return self._backend.size()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if hasattr(self._backend, 'get_stats'):
            return self._backend.get_stats()
        else:
            return {'cache_size': self.size()}
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                stats = self.get_stats()
                self.logger.info(f"缓存统计: {stats}")
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"监控异常: {e}")

# 缓存装饰器
def cache(key_func: Optional[Callable] = None, ttl: Optional[int] = None):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存储到缓存
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 全局缓存管理器实例
cache_manager = None

def init_cache(config: CacheConfig):
    """初始化缓存管理器"""
    global cache_manager
    cache_manager = CacheManager(config)
    cache_manager.start()

def get_cache() -> CacheManager:
    """获取缓存管理器"""
    return cache_manager

# 使用示例
# 配置缓存
config = CacheConfig(
    max_size=1000,
    max_memory=100 * 1024 * 1024,  # 100MB
    default_ttl=3600,  # 1小时
    strategy=CacheStrategy.LRU,
    enable_compression=False,
    enable_serialization=True,
    serialization_format="pickle",
    enable_monitoring=True,
    monitoring_interval=60.0,
    distributed=False
)

# 初始化缓存
init_cache(config)

# 使用缓存装饰器
@cache(ttl=300)  # 缓存5分钟
def get_user_data(user_id: int):
    """获取用户数据"""
    print(f"从数据库获取用户数据: {user_id}")
    time.sleep(1)  # 模拟数据库查询
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

@cache(key_func=lambda x, y: f"add:{x}:{y}")
def add_numbers(x: int, y: int) -> int:
    """加法运算"""
    print(f"计算 {x} + {y}")
    time.sleep(0.5)  # 模拟计算
    return x + y

# 测试缓存
print("第一次调用:")
user_data = get_user_data(1)
print(f"用户数据: {user_data}")

print("\n第二次调用 (应该从缓存获取):")
user_data = get_user_data(1)
print(f"用户数据: {user_data}")

print("\n测试加法缓存:")
result1 = add_numbers(10, 20)
print(f"结果: {result1}")

result2 = add_numbers(10, 20)
print(f"结果: {result2}")

# 获取缓存统计
stats = cache_manager.get_stats()
print(f"\n缓存统计: {stats}")

# 停止缓存
cache_manager.stop()
```

## 分布式缓存

### Redis集群配置
```python
# redis_cluster.py
import redis
from redis.sentinel import Sentinel
from typing import List, Dict, Any, Optional
import logging

class RedisCluster:
    """Redis集群管理"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._redis_client = None
        self._sentinel = None
        self._init_client()
    
    def _init_client(self):
        """初始化Redis客户端"""
        try:
            if self.config.get('use_sentinel', False):
                self._init_sentinel_client()
            elif self.config.get('use_cluster', False):
                self._init_cluster_client()
            else:
                self._init_single_client()
        except Exception as e:
            self.logger.error(f"初始化Redis客户端失败: {e}")
            raise
    
    def _init_single_client(self):
        """初始化单机Redis客户端"""
        self._redis_client = redis.Redis(
            host=self.config.get('host', 'localhost'),
            port=self.config.get('port', 6379),
            db=self.config.get('db', 0),
            password=self.config.get('password'),
            decode_responses=False,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def _init_sentinel_client(self):
        """初始化Sentinel客户端"""
        sentinel_hosts = self.config.get('sentinel_hosts', [])
        if not sentinel_hosts:
            raise ValueError("Sentinel hosts not configured")
        
        self._sentinel = Sentinel(sentinel_hosts)
        master_name = self.config.get('master_name', 'mymaster')
        self._redis_client = self._sentinel.master_for(
            master_name,
            socket_timeout=5,
            decode_responses=False,
            password=self.config.get('password')
        )
    
    def _init_cluster_client(self):
        """初始化集群客户端"""
        from rediscluster import RedisCluster
        startup_nodes = self.config.get('startup_nodes', [])
        if not startup_nodes:
            raise ValueError("Startup nodes not configured")
        
        self._redis_client = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=False,
            skip_full_coverage_check=True,
            max_connections_per_node=16
        )
    
    def get_client(self):
        """获取Redis客户端"""
        return self._redis_client
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            self._redis_client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Redis健康检查失败: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取Redis信息"""
        try:
            info = self._redis_client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory': info.get('used_memory'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except Exception as e:
            self.logger.error(f"获取Redis信息失败: {e}")
            return {}

# 使用示例
# Redis配置
redis_config = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'use_sentinel': False,
    'use_cluster': False
}

# 或者Sentinel配置
sentinel_config = {
    'use_sentinel': True,
    'sentinel_hosts': [
        ('sentinel1', 26379),
        ('sentinel2', 26379),
        ('sentinel3', 26379)
    ],
    'master_name': 'mymaster',
    'password': None
}

# 创建Redis集群
redis_cluster = RedisCluster(redis_config)

# 健康检查
if redis_cluster.health_check():
    print("Redis连接正常")
    info = redis_cluster.get_info()
    print(f"Redis信息: {info}")
else:
    print("Redis连接失败")
```

## 参考资源

### 缓存技术
- [Redis官方文档](https://redis.io/documentation)
- [Memcached文档](https://memcached.org/)
- [Python redis-py](https://redis-py.readthedocs.io/)
- [缓存设计模式](https://martinfowler.com/articles/patterns-of-distributed-systems/)

### 缓存算法
- [LRU算法详解](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU))
- [LFU算法详解](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_frequently_used_(LFU))
- [缓存一致性协议](https://en.wikipedia.org/wiki/Cache_coherence)
- [分布式缓存设计](https://dl.acm.org/doi/10.1145/3183440.3193490)

### 性能优化
- [缓存性能优化](https://redis.io/topics/memory-optimization)
- [缓存预热策略](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [缓存穿透解决方案](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)
- [缓存雪崩防护](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)

### 监控和运维
- [Redis监控](https://redis.io/topics/admin)
- [缓存监控指标](https://prometheus.io/docs/practices/instrumentation/)
- [性能调优指南](https://redis.io/topics/latency)
- [高可用配置](https://redis.io/topics/replication)
