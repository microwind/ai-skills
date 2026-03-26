#!/usr/bin/env python3
"""
缓存策略演示 - 实现多种缓存模式和策略
"""

import time
import json
import hashlib
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import random

class CacheType(Enum):
    """缓存类型"""
    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DISK = "disk"

class EvictionPolicy(Enum):
    """淘汰策略"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"   # 过期时间

@dataclass
class CacheItem:
    """缓存项"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    access_count: int = 0
    last_accessed: float = 0
    
    def __post_init__(self):
        if self.last_accessed == 0:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self):
        """记录访问"""
        self.access_count += 1
        self.last_accessed = time.time()

class MemoryCache:
    """内存缓存"""
    
    def __init__(self, max_size: int = 1000, eviction_policy: EvictionPolicy = EvictionPolicy.LRU):
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.cache: Dict[str, CacheItem] = {}
        self.access_order: List[str] = []
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0
        }
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                
                if item.is_expired():
                    del self.cache[key]
                    self.access_order.remove(key)
                    self.stats['misses'] += 1
                    return None
                
                item.access()
                self._update_access_order(key)
                self.stats['hits'] += 1
                return item.value
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        with self.lock:
            expires_at = None
            if ttl:
                expires_at = time.time() + ttl
            
            item = CacheItem(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=expires_at
            )
            
            # 如果缓存已满，执行淘汰
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_item()
            
            self.cache[key] = item
            self._update_access_order(key)
            self.stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.remove(key)
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def _update_access_order(self, key: str):
        """更新访问顺序"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_item(self):
        """淘汰缓存项"""
        if not self.cache:
            return
        
        if self.eviction_policy == EvictionPolicy.LRU:
            # 淘汰最近最少使用的
            key_to_evict = self.access_order[0]
        elif self.eviction_policy == EvictionPolicy.LFU:
            # 淘汰使用频率最低的
            key_to_evict = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
        elif self.eviction_policy == EvictionPolicy.FIFO:
            # 淘汰最先插入的
            key_to_evict = min(self.cache.keys(), key=lambda k: self.cache[k].created_at)
        else:  # TTL
            # 淘汰最先过期的
            key_to_evict = min(
                [k for k, v in self.cache.items() if v.expires_at],
                key=lambda k: self.cache[k].expires_at,
                default=None
            )
            if key_to_evict is None:
                key_to_evict = self.access_order[0]
        
        if key_to_evict in self.cache:
            del self.cache[key_to_evict]
            self.access_order.remove(key_to_evict)
            self.stats['evictions'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'sets': self.stats['sets'],
                'hit_rate': hit_rate,
                'eviction_policy': self.eviction_policy.value
            }
    
    def get_expired_items(self) -> List[str]:
        """获取过期的缓存项"""
        with self.lock:
            expired = []
            for key, item in self.cache.items():
                if item.is_expired():
                    expired.append(key)
            return expired
    
    def cleanup_expired(self):
        """清理过期项"""
        with self.lock:
            expired_keys = self.get_expired_items()
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
            return len(expired_keys)

class CacheDecorator:
    """缓存装饰器"""
    
    def __init__(self, cache: MemoryCache, ttl: Optional[int] = None, key_prefix: str = ""):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix
    
    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self._generate_cache_key(func.__name__, args, kwargs)
            
            # 尝试从缓存获取
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, self.ttl)
            
            return result
        
        wrapper.cache = self.cache
        wrapper.cache_key_prefix = self.key_prefix
        return wrapper
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        key_data = f"{self.key_prefix}:{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

class MultiLevelCache:
    """多级缓存"""
    
    def __init__(self, l1_cache: MemoryCache, l2_cache: MemoryCache):
        self.l1_cache = l1_cache  # L1缓存（内存）
        self.l2_cache = l2_cache  # L2缓存（可以是Redis等）
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值（多级查找）"""
        # 先查L1缓存
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats['l1_hits'] += 1
            return value
        
        # 再查L2缓存
        value = self.l2_cache.get(key)
        if value is not None:
            self.stats['l2_hits'] += 1
            # 提升到L1缓存
            self.l1_cache.set(key, value)
            return value
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值（同时写入多级）"""
        self.l1_cache.set(key, value, ttl)
        self.l2_cache.set(key, value, ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_requests = sum(self.stats.values())
        return {
            **self.stats,
            'l1_hit_rate': self.stats['l1_hits'] / total_requests if total_requests > 0 else 0,
            'l2_hit_rate': self.stats['l2_hits'] / total_requests if total_requests > 0 else 0,
            'total_hit_rate': (self.stats['l1_hits'] + self.stats['l2_hits']) / total_requests if total_requests > 0 else 0
        }

class CacheWarmer:
    """缓存预热器"""
    
    def __init__(self, cache: MemoryCache):
        self.cache = cache
    
    def warm_cache(self, data_generator: Callable[[], Dict[str, Any]], ttl: Optional[int] = None):
        """预热缓存"""
        print("🔥 开始缓存预热...")
        
        start_time = time.time()
        data = data_generator()
        
        for key, value in data.items():
            self.cache.set(key, value, ttl)
        
        end_time = time.time()
        
        print(f"✅ 缓存预热完成: {len(data)} 项，耗时 {end_time - start_time:.3f}s")
    
    def warm_popular_data(self, keys: List[str], data_fetcher: Callable[[str], Any], ttl: Optional[int] = None):
        """预热热门数据"""
        print("🔥 预热热门数据...")
        
        for key in keys:
            value = data_fetcher(key)
            self.cache.set(key, value, ttl)
        
        print(f"✅ 热门数据预热完成: {len(keys)} 项")

class CacheInvalidator:
    """缓存失效器"""
    
    def __init__(self, cache: MemoryCache):
        self.cache = cache
        self.invalidation_rules: Dict[str, List[str]] = {}  # 依赖关系
    
    def add_dependency(self, key: str, dependent_keys: List[str]):
        """添加依赖关系"""
        self.invalidation_rules[key] = dependent_keys
    
    def invalidate(self, key: str) -> int:
        """失效缓存项及其依赖项"""
        invalidated_count = 0
        
        # 直接失效
        if self.cache.delete(key):
            invalidated_count += 1
        
        # 失效依赖项
        if key in self.invalidation_rules:
            for dependent_key in self.invalidation_rules[key]:
                if self.cache.delete(dependent_key):
                    invalidated_count += 1
        
        print(f"🗑️  缓存失效: {key} 及其依赖项，共 {invalidated_count} 项")
        return invalidated_count
    
    def invalidate_pattern(self, pattern: str) -> int:
        """按模式失效缓存"""
        invalidated_count = 0
        
        keys_to_delete = []
        for key in self.cache.cache.keys():
            if pattern in key:  # 简单的包含匹配
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            if self.cache.delete(key):
                invalidated_count += 1
        
        print(f"🗑️  模式失效: '{pattern}'，共 {invalidated_count} 项")
        return invalidated_count

def demonstrate_basic_caching():
    """演示基础缓存"""
    print("\n💾 基础缓存演示")
    print("=" * 50)
    
    # 创建缓存
    cache = MemoryCache(max_size=100, eviction_policy=EvictionPolicy.LRU)
    
    # 设置缓存
    cache.set("user:1", {"name": "Alice", "age": 30}, ttl=60)
    cache.set("user:2", {"name": "Bob", "age": 25}, ttl=60)
    cache.set("product:1", {"name": "Laptop", "price": 999.99})
    
    # 获取缓存
    print("📖 获取缓存:")
    user1 = cache.get("user:1")
    print(f"  user:1 = {user1}")
    
    user2 = cache.get("user:2")
    print(f"  user:2 = {user2}")
    
    # 缓存未命中
    user3 = cache.get("user:3")
    print(f"  user:3 = {user3}")
    
    # 显示统计
    stats = cache.get_stats()
    print(f"\n📊 缓存统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

def demonstrate_eviction_policies():
    """演示淘汰策略"""
    print("\n🗑️  淘汰策略演示")
    print("=" * 50)
    
    policies = [EvictionPolicy.LRU, EvictionPolicy.LFU, EvictionPolicy.FIFO]
    
    for policy in policies:
        print(f"\n📋 测试策略: {policy.value}")
        cache = MemoryCache(max_size=3, eviction_policy=policy)
        
        # 添加超过容量的项
        for i in range(5):
            cache.set(f"key{i}", f"value{i}")
        
        # 访问某些项
        if policy == EvictionPolicy.LRU:
            cache.get("key1")  # 访问key1，使其不被淘汰
        elif policy == EvictionPolicy.LFU:
            for _ in range(3):
                cache.get("key1")  # 多次访问key1
        
        # 添加新项触发淘汰
        cache.set("key5", "value5")
        
        # 显示剩余项
        print(f"  剩余缓存项: {list(cache.cache.keys())}")
        print(f"  淘汰次数: {cache.stats['evictions']}")

def demonstrate_cache_decorator():
    """演示缓存装饰器"""
    print("\n🎯 缓存装饰器演示")
    print("=" * 50)
    
    cache = MemoryCache(max_size=100)
    decorator = CacheDecorator(cache, ttl=60, key_prefix="func")
    
    @decorator
    def expensive_function(x: int, y: int) -> int:
        """模拟耗时函数"""
        print(f"  🔨 执行计算: {x} + {y}")
        time.sleep(0.1)  # 模拟耗时
        return x + y
    
    print("🔄 第一次调用（执行计算）:")
    result1 = expensive_function(1, 2)
    print(f"  结果: {result1}")
    
    print("\n🔄 第二次调用（从缓存）:")
    result2 = expensive_function(1, 2)
    print(f"  结果: {result2}")
    
    print("\n🔄 不同参数调用（执行计算）:")
    result3 = expensive_function(2, 3)
    print(f"  结果: {result3}")
    
    # 显示缓存统计
    stats = cache.get_stats()
    print(f"\n📊 缓存统计:")
    print(f"  命中率: {stats['hit_rate']:.2%}")

def demonstrate_multilevel_cache():
    """演示多级缓存"""
    print("\n🏢 多级缓存演示")
    print("=" * 50)
    
    # 创建两级缓存
    l1_cache = MemoryCache(max_size=10, eviction_policy=EvictionPolicy.LRU)
    l2_cache = MemoryCache(max_size=50, eviction_policy=EvictionPolicy.LRU)
    
    multi_cache = MultiLevelCache(l1_cache, l2_cache)
    
    # 设置数据到L2缓存
    l2_cache.set("user:1", {"name": "Alice"})
    l2_cache.set("user:2", {"name": "Bob"})
    l2_cache.set("user:3", {"name": "Charlie"})
    
    print("📖 获取数据（应该从L2获取并提升到L1）:")
    user1 = multi_cache.get("user:1")
    print(f"  user:1 = {user1}")
    
    print("\n📖 再次获取（应该从L1获取）:")
    user1_again = multi_cache.get("user:1")
    print(f"  user:1 = {user1_again}")
    
    # 显示统计
    stats = multi_cache.get_stats()
    print(f"\n📊 多级缓存统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

def demonstrate_cache_warming():
    """演示缓存预热"""
    print("\n🔥 缓存预热演示")
    print("=" * 50)
    
    cache = MemoryCache(max_size=100)
    warmer = CacheWarmer(cache)
    
    # 数据生成器
    def generate_user_data():
        return {
            f"user:{i}": {"name": f"User{i}", "age": 20 + i}
            for i in range(1, 21)
        }
    
    # 预热缓存
    warmer.warm_cache(generate_user_data, ttl=300)
    
    # 测试预热效果
    print("\n📖 测试预热后的缓存:")
    for i in range(1, 6):
        user = cache.get(f"user:{i}")
        print(f"  user:{i} = {user}")
    
    # 显示统计
    stats = cache.get_stats()
    print(f"\n📊 预热后统计:")
    print(f"  缓存大小: {stats['size']}")
    print(f"  设置次数: {stats['sets']}")

def demonstrate_cache_invalidation():
    """演示缓存失效"""
    print("\n🗑️  缓存失效演示")
    print("=" * 50)
    
    cache = MemoryCache(max_size=100)
    invalidator = CacheInvalidator(cache)
    
    # 设置缓存
    cache.set("user:1", {"name": "Alice"})
    cache.set("user:1:profile", {"age": 30, "city": "Beijing"})
    cache.set("user:1:orders", [{"id": 1}, {"id": 2}])
    
    # 添加依赖关系
    invalidator.add_dependency("user:1", ["user:1:profile", "user:1:orders"])
    
    print("📋 初始缓存:")
    print(f"  缓存项: {list(cache.cache.keys())}")
    
    # 失效主数据
    print("\n🗑️  失效用户数据:")
    count = invalidator.invalidate("user:1")
    
    print(f"\n📋 失效后缓存:")
    print(f"  缓存项: {list(cache.cache.keys())}")
    print(f"  失效数量: {count}")

def main():
    """主函数"""
    print("💾 缓存策略演示")
    print("=" * 60)
    
    try:
        demonstrate_basic_caching()
        demonstrate_eviction_policies()
        demonstrate_cache_decorator()
        demonstrate_multilevel_cache()
        demonstrate_cache_warming()
        demonstrate_cache_invalidation()
        
        print("\n✅ 缓存策略演示完成!")
        print("\n📚 关键概念:")
        print("  - 内存缓存: 快速访问的内存存储")
        print("  - 淘汰策略: LRU、LFU、FIFO等")
        print("  - TTL: 生存时间，自动过期")
        print("  - 缓存装饰器: 函数结果缓存")
        print("  - 多级缓存: L1/L2缓存层次")
        print("  - 缓存预热: 提前加载热点数据")
        print("  - 缓存失效: 数据一致性保证")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == '__main__':
    main()
