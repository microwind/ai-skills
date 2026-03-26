# 缓存失效策略技术参考

## 概述

缓存失效策略是分布式系统中的核心概念，用于确保缓存数据与数据源的一致性。本文档详细介绍了各种缓存失效策略、实现方法和最佳实践。

## 核心概念

### 缓存一致性
- **强一致性**: 所有节点在同一时间看到相同的数据
- **最终一致性**: 系统保证在没有新更新的情况下，数据最终会一致
- **弱一致性**: 不保证数据的一致性，可能存在不一致窗口

### 失效策略分类
- **时间失效**: 基于时间的自动失效
- **事件失效**: 基于数据变更事件的失效
- **手动失效**: 人工触发的失效
- **混合失效**: 多种策略的组合使用

## 时间过期策略

### TTL (Time To Live)
```java
// Redis TTL示例
redis.setex("user:123", 3600, userData); // 1小时后过期
redis.expire("session:abc", 1800);       // 30分钟后过期

// 检查剩余时间
long ttl = redis.ttl("user:123");
if (ttl == -1) {
    // 永不过期
} else if (ttl == -2) {
    // 键不存在
}
```

### 滑动过期
```python
# 滑动过期实现
class SlidingExpiration:
    def __init__(self, ttl):
        self.ttl = ttl
        self.last_access = time.time()
    
    def access(self):
        self.last_access = time.time()
        return self.last_access + self.ttl
    
    def is_expired(self):
        return time.time() > self.last_access + self.ttl
```

### 延迟过期 (Lazy Expiration)
```javascript
// 延迟过期实现
class LazyExpiration {
    constructor(ttl) {
        this.ttl = ttl;
        this.cache = new Map();
    }
    
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (this.isExpired(item)) {
            this.cache.delete(key);
            return null;
        }
        
        return item.value;
    }
    
    isExpired(item) {
        return Date.now() - item.timestamp > this.ttl;
    }
}
```

## 事件驱动失效

### 数据库触发器失效
```sql
-- MySQL触发器示例
DELIMITER //
CREATE TRIGGER cache_invalidation_after_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    -- 发送失效消息到消息队列
    INSERT INTO cache_invalidation_queue (cache_key, operation)
    VALUES (CONCAT('user:', NEW.id), 'UPDATE');
END//
DELIMITER ;
```

### 应用层事件失效
```java
// Spring事件驱动失效
@Component
public class CacheInvalidationListener {
    
    @EventListener
    public void handleUserUpdateEvent(UserUpdatedEvent event) {
        String cacheKey = "user:" + event.getUserId();
        cacheManager.evict(cacheKey);
        
        // 批量失效相关缓存
        invalidateRelatedCaches(event.getUserId());
    }
    
    private void invalidateRelatedCaches(Long userId) {
        // 失效用户列表缓存
        cacheManager.evict("users:list");
        // 失效用户统计缓存
        cacheManager.evict("users:stats");
    }
}
```

### 消息队列失效
```python
# Kafka消息队列失效
import kafka
import json

class CacheInvalidationProducer:
    def __init__(self, bootstrap_servers):
        self.producer = kafka.KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def invalidate_cache(self, cache_key, operation='INVALIDATE'):
        message = {
            'key': cache_key,
            'operation': operation,
            'timestamp': time.time()
        }
        self.producer.send('cache-invalidation', message)
        self.producer.flush()

# 消费者处理失效消息
class CacheInvalidationConsumer:
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
    
    def process_invalidation(self, message):
        cache_key = message['key']
        operation = message['operation']
        
        if operation == 'INVALIDATE':
            self.cache_manager.delete(cache_key)
        elif operation == 'REFRESH':
            self.cache_manager.refresh(cache_key)
```

## 模式匹配失效

### 通配符失效
```java
// Redis通配符失效
public class WildcardInvalidation {
    private Jedis jedis;
    
    public void invalidateByPattern(String pattern) {
        Set<String> keys = jedis.keys(pattern);
        if (!keys.isEmpty()) {
            jedis.del(keys.toArray(new String[0]));
        }
    }
    
    // 使用示例
    public void invalidateUserCaches(Long userId) {
        invalidateByPattern("user:" + userId + ":*");
        invalidateByPattern("user:*:profile");
    }
}
```

### 正则表达式失效
```python
import re

class RegexInvalidation:
    def __init__(self, cache_store):
        self.cache = cache_store
    
    def invalidate_by_regex(self, pattern):
        compiled_pattern = re.compile(pattern)
        keys_to_delete = []
        
        for key in self.cache.keys():
            if compiled_pattern.match(key):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.cache.delete(key)
    
    # 使用示例
    def invalidate_session_caches(self):
        self.invalidate_by_regex(r'session:[a-f0-9]{32}')
```

### 层次失效
```javascript
// 层次命名空间失效
class HierarchicalCache {
    constructor() {
        this.namespaces = new Map();
    }
    
    set(key, value, namespace = 'default') {
        if (!this.namespaces.has(namespace)) {
            this.namespaces.set(namespace, new Map());
        }
        this.namespaces.get(namespace).set(key, value);
    }
    
    invalidateNamespace(namespace) {
        this.namespaces.delete(namespace);
    }
    
    invalidateHierarchy(hierarchy) {
        // 失效所有子命名空间
        for (const [ns, cache] of this.namespaces) {
            if (ns.startsWith(hierarchy + ':')) {
                this.namespaces.delete(ns);
            }
        }
    }
}
```

## 分布式失效

### 两阶段提交失效
```java
// 两阶段提交实现
public class TwoPhaseInvalidation {
    private List<CacheNode> nodes;
    
    public boolean invalidateDistributed(String key) {
        // 阶段1：准备
        List<Boolean> prepared = new ArrayList<>();
        for (CacheNode node : nodes) {
            boolean success = node.prepareInvalidation(key);
            prepared.add(success);
            if (!success) {
                // 回滚所有已准备的节点
                rollback(prepared, key);
                return false;
            }
        }
        
        // 阶段2：提交
        for (CacheNode node : nodes) {
            node.commitInvalidation(key);
        }
        
        return true;
    }
    
    private void rollback(List<Boolean> prepared, String key) {
        // 实现回滚逻辑
    }
}
```

### Raft协议失效
```go
// Raft协议失效示例
type CacheInvalidationRequest struct {
    Key       string
    Term      int
    LeaderID  string
    Timestamp time.Time
}

type RaftCacheNode struct {
    state     State
    term      int
    log       []CacheInvalidationRequest
    commitIndex int
    cache     *Cache
}

func (n *RaftCacheNode) Invalidate(key string) error {
    // 提议失效请求
    request := CacheInvalidationRequest{
        Key:       key,
        Term:      n.term,
        LeaderID:  n.id,
        Timestamp: time.Now(),
    }
    
    // 发送给所有追随者
    for _, follower := range n.followers {
        follower.sendInvalidationRequest(request)
    }
    
    // 等待大多数确认
    return n.waitForCommit(request)
}
```

## 性能优化

### 批量失效
```python
class BatchInvalidation:
    def __init__(self, batch_size=100, flush_interval=5):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending = []
        self.last_flush = time.time()
    
    def add_invalidation(self, key):
        self.pending.append(key)
        
        if (len(self.pending) >= self.batch_size or 
            time.time() - self.last_flush > self.flush_interval):
            self.flush()
    
    def flush(self):
        if self.pending:
            # 批量删除
            self.cache.delete_many(self.pending)
            self.pending.clear()
            self.last_flush = time.time()
```

### 异步失效
```java
// 异步失效实现
@Component
public class AsyncCacheInvalidation {
    private ExecutorService executor;
    private BlockingQueue<InvalidationTask> queue;
    
    @PostConstruct
    public void init() {
        executor = Executors.newFixedThreadPool(10);
        queue = new LinkedBlockingQueue<>();
        
        // 启动消费者线程
        for (int i = 0; i < 5; i++) {
            executor.submit(this::processInvalidation);
        }
    }
    
    public void invalidateAsync(String key) {
        InvalidationTask task = new InvalidationTask(key, System.currentTimeMillis());
        queue.offer(task);
    }
    
    private void processInvalidation() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                InvalidationTask task = queue.take();
                cacheManager.evict(task.getKey());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
```

## 监控和诊断

### 失效监控指标
```python
from prometheus_client import Counter, Histogram, Gauge

# 监控指标
invalidation_counter = Counter('cache_invalidations_total', 
                              'Total cache invalidations', ['type', 'status'])
invalidation_duration = Histogram('cache_invalidation_duration_seconds',
                                 'Cache invalidation duration')
active_invalidations = Gauge('cache_active_invalidations',
                             'Number of active invalidations')

class MonitoredCacheInvalidation:
    def invalidate(self, key, invalidation_type='manual'):
        with invalidation_duration.time():
            active_invalidations.inc()
            try:
                # 执行失效逻辑
                self._do_invalidate(key)
                invalidation_counter.labels(type=invalidation_type, status='success').inc()
            except Exception as e:
                invalidation_counter.labels(type=invalidation_type, status='error').inc()
                raise
            finally:
                active_invalidations.dec()
```

### 失效追踪
```java
// 分布式追踪
@Component
public class TracedCacheInvalidation {
    private Tracer tracer;
    
    public void invalidateWithTracing(String key) {
        Span span = tracer.nextSpan()
            .name("cache-invalidation")
            .tag("cache.key", key)
            .start();
        
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(span)) {
            // 记录失效开始
            span.event("invalidation-start");
            
            // 执行失效
            cacheManager.evict(key);
            
            // 记录失效完成
            span.event("invalidation-complete");
            span.tag("status", "success");
        } catch (Exception e) {
            span.tag("status", "error");
            span.tag("error", e.getMessage());
            throw e;
        } finally {
            span.end();
        }
    }
}
```

## 最佳实践

### 失效策略选择
1. **读多写少场景**: 使用TTL失效
2. **写多读少场景**: 使用事件驱动失效
3. **高一致性要求**: 使用同步失效
4. **高性能要求**: 使用异步批量失效

### 避免缓存雪崩
```java
// 随机TTL避免缓存雪崩
public class RandomTTL {
    private Random random = new Random();
    
    public long calculateTTL(long baseTTL) {
        // 在基础TTL上添加随机偏移
        long jitter = (long) (baseTTL * 0.1 * random.nextDouble());
        return baseTTL + jitter;
    }
    
    public void setWithRandomTTL(String key, Object value, long baseTTL) {
        long actualTTL = calculateTTL(baseTTL);
        redis.setex(key, actualTTL, value);
    }
}
```

### 缓存预热策略
```python
class CacheWarmupStrategy:
    def __init__(self, cache, data_loader):
        self.cache = cache
        self.data_loader = data_loader
    
    def warmup_hot_data(self, hot_keys):
        """预热热点数据"""
        for key in hot_keys:
            if not self.cache.exists(key):
                data = self.data_loader.load(key)
                self.cache.set(key, data, ttl=3600)
    
    def warmup_on_invalidation(self, invalidated_key):
        """失效后立即预热"""
        data = self.data_loader.load(invalidated_key)
        self.cache.set(invalidated_key, data, ttl=3600)
```

## 故障处理

### 失效失败处理
```java
// 失效失败重试机制
@Component
public class ResilientCacheInvalidation {
    private RetryTemplate retryTemplate;
    
    @Retryable(value = {Exception.class}, 
               maxAttempts = 3,
               backoff = @Backoff(delay = 1000, multiplier = 2))
    public void invalidateWithRetry(String key) {
        try {
            cacheManager.evict(key);
        } catch (Exception e) {
            // 记录失败日志
            logger.error("Cache invalidation failed for key: {}", key, e);
            throw e;
        }
    }
    
    @Recover
    public void recoverInvalidation(Exception e, String key) {
        // 失败后的恢复策略
        fallbackInvalidation(key);
    }
}
```

### 网络分区处理
```go
// 网络分区处理
type PartitionAwareInvalidation struct {
    localCache    *Cache
    remoteNodes   []RemoteNode
    partitionMode bool
}

func (p *PartitionAwareInvalidation) Invalidate(key string) error {
    if p.partitionMode {
        // 分区模式下只失效本地缓存
        return p.localCache.Delete(key)
    }
    
    // 正常模式下失效所有节点
    var errors []error
    
    // 失效本地缓存
    if err := p.localCache.Delete(key); err != nil {
        errors = append(errors, err)
    }
    
    // 失效远程节点
    for _, node := range p.remoteNodes {
        if err := node.Invalidate(key); err != nil {
            errors = append(errors, err)
        }
    }
    
    if len(errors) > 0 {
        return fmt.Errorf("partial invalidation failed: %v", errors)
    }
    
    return nil
}
```

## 相关资源

### 官方文档
- [Redis Documentation](https://redis.io/documentation)
- [Memcached Documentation](https://memcached.org/)
- [Hazelcast Documentation](https://docs.hazelcast.org/)

### 学术论文
- "Cache Invalidation Strategies in Distributed Systems" - IEEE 2020
- "Consistent Cache Invalidation for Web Applications" - ACM 2019
- "Performance Analysis of Cache Invalidation Protocols" - USENIX 2021

### 开源项目
- [Spring Cache Abstraction](https://spring.io/projects/spring-framework)
- [Ehcache](https://www.ehcache.org/)
- [Apache Ignite](https://ignite.apache.org/)

### 工具和库
- Redis CLI和Redis Insight
- Memcached stats和监控工具
- 自定义缓存失效框架

### 社区资源
- [Stack Overflow - Cache Tags](https://stackoverflow.com/questions/tagged/cache)
- [Reddit - r/caching](https://www.reddit.com/r/caching)
- [缓存技术讨论组](https://groups.google.com/g/caching-tech)
