---
name: 缓存失效策略
description: "当设计缓存失效时，分析失效模式，优化数据一致性，解决缓存雪崩。验证缓存架构，设计失效策略，和最佳实践。"
license: MIT
---

# 缓存失效策略技能

## 概述
缓存失效是缓存系统中的关键问题，决定了数据的一致性和系统的可用性。不当的失效策略会导致数据不一致、缓存雪崩、性能下降。选择合适的失效策略对系统性能和数据一致性至关重要。

**核心原则**: 好的失效策略应该保证数据一致性、避免缓存雪崩、提高命中率、减少性能影响。坏的失效策略会导致数据不一致或系统不稳定。

## 何时使用

**始终:**
- 设计缓存系统时
- 处理数据一致性时
- 优化缓存性能时
- 解决缓存雪崩时
- 实现分布式缓存时
- 处理热点数据时

**触发短语:**
- "如何设计缓存失效？"
- "缓存一致性问题"
- "避免缓存雪崩"
- "缓存失效策略选择"
- "分布式缓存失效"
- "热点数据处理"

## 缓存失效策略技能功能

### 失效模式
- 主动失效
- 被动失效
- 定时失效
- 版本失效
- 事件驱动失效

### 一致性保证
- 强一致性
- 最终一致性
- 写入失效
- 读取失效
- 双写一致性

### 性能优化
- 批量失效
- 异步失效
- 分级失效
- 预热策略
- 防雪崩机制

### 监控管理
- 命中率监控
- 失效率统计
- 性能指标
- 告警机制
- 容量规划

## 常见问题

### 一致性问题
- **问题**: 缓存与数据库不一致
- **原因**: 失效策略不当，并发更新
- **解决**: 使用合适的失效策略，保证一致性

- **问题**: 分布式缓存不一致
- **原因**: 网络延迟，失效传播失败
- **解决**: 使用分布式失效机制

### 性能问题
- **问题**: 缓存雪崩
- **原因**: 大量缓存同时失效
- **解决**: 使用随机过期时间，错峰失效

- **问题**: 缓存穿透
- **原因**: 查询不存在的数据
- **解决**: 缓存空值，使用布隆过滤器

### 可用性问题
- **问题**: 缓存故障影响系统
- **原因**: 过度依赖缓存
- **解决**: 降级策略，熔断机制

## 代码示例

### 基础缓存失效实现
```java
// 缓存管理器
@Component
public class CacheManager {
    
    private final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    public CacheManager() {
        // 定期清理过期缓存
        scheduler.scheduleAtFixedRate(this::cleanExpiredEntries, 1, 1, TimeUnit.MINUTES);
    }
    
    // 设置缓存
    public void put(String key, Object value, long ttlMillis) {
        CacheEntry entry = new CacheEntry(value, System.currentTimeMillis() + ttlMillis);
        cache.put(key, entry);
    }
    
    // 获取缓存
    public Object get(String key) {
        CacheEntry entry = cache.get(key);
        if (entry == null) {
            return null;
        }
        
        if (entry.isExpired()) {
            cache.remove(key);
            return null;
        }
        
        return entry.getValue();
    }
    
    // 主动失效
    public void invalidate(String key) {
        cache.remove(key);
    }
    
    // 批量失效
    public void invalidateBatch(Set<String> keys) {
        keys.forEach(cache::remove);
    }
    
    // 模式匹配失效
    public void invalidateByPattern(String pattern) {
        cache.keySet().removeIf(key -> matchesPattern(key, pattern));
    }
    
    // 清理过期条目
    private void cleanExpiredEntries() {
        long currentTime = System.currentTimeMillis();
        cache.entrySet().removeIf(entry -> entry.getValue().isExpired(currentTime));
    }
    
    private boolean matchesPattern(String key, String pattern) {
        // 简单的通配符匹配
        return key.matches(pattern.replace("*", ".*"));
    }
    
    @PreDestroy
    public void destroy() {
        scheduler.shutdown();
    }
    
    private static class CacheEntry {
        private final Object value;
        private final long expireTime;
        
        public CacheEntry(Object value, long expireTime) {
            this.value = value;
            this.expireTime = expireTime;
        }
        
        public Object getValue() {
            return value;
        }
        
        public boolean isExpired() {
            return isExpired(System.currentTimeMillis());
        }
        
        public boolean isExpired(long currentTime) {
            return currentTime > expireTime;
        }
    }
}

// 缓存失效策略
public enum InvalidationStrategy {
    IMMEDIATE,    // 立即失效
    DELAYED,      // 延迟失效
    BATCH,        // 批量失效
    EVENT_DRIVEN  // 事件驱动
}

// 缓存失效服务
@Service
public class CacheInvalidationService {
    
    private final CacheManager cacheManager;
    private final ApplicationEventPublisher eventPublisher;
    private final Queue<InvalidationTask> invalidationQueue = new ConcurrentLinkedQueue<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    
    public CacheInvalidationService(CacheManager cacheManager,
                                  ApplicationEventPublisher eventPublisher) {
        this.cacheManager = cacheManager;
        this.eventPublisher = eventPublisher;
        
        // 启动批量失效任务
        scheduler.scheduleAtFixedRate(this::processBatchInvalidation, 100, 100, TimeUnit.MILLISECONDS);
    }
    
    // 立即失效
    public void invalidateImmediately(String key) {
        cacheManager.invalidate(key);
        eventPublisher.publishEvent(new CacheInvalidatedEvent(key, InvalidationStrategy.IMMEDIATE));
    }
    
    // 延迟失效
    public void invalidateDelayed(String key, long delayMillis) {
        scheduler.schedule(() -> {
            cacheManager.invalidate(key);
            eventPublisher.publishEvent(new CacheInvalidatedEvent(key, InvalidationStrategy.DELAYED));
        }, delayMillis, TimeUnit.MILLISECONDS);
    }
    
    // 批量失效
    public void invalidateBatch(Set<String> keys) {
        keys.forEach(key -> invalidationQueue.offer(new InvalidationTask(key, System.currentTimeMillis())));
    }
    
    // 模式失效
    public void invalidateByPattern(String pattern) {
        cacheManager.invalidateByPattern(pattern);
        eventPublisher.publishEvent(new PatternInvalidationEvent(pattern));
    }
    
    // 处理批量失效
    private void processBatchInvalidation() {
        List<InvalidationTask> batch = new ArrayList<>();
        
        // 收集批量任务
        InvalidationTask task;
        while ((task = invalidationQueue.poll()) != null && batch.size() < 100) {
            batch.add(task);
        }
        
        if (!batch.isEmpty()) {
            Set<String> keys = batch.stream()
                .map(InvalidationTask::getKey)
                .collect(Collectors.toSet());
            
            cacheManager.invalidateBatch(keys);
            eventPublisher.publishEvent(new BatchInvalidationEvent(keys));
        }
    }
    
    @PreDestroy
    public void destroy() {
        scheduler.shutdown();
    }
    
    private static class InvalidationTask {
        private final String key;
        private final long timestamp;
        
        public InvalidationTask(String key, long timestamp) {
            this.key = key;
            this.timestamp = timestamp;
        }
        
        public String getKey() {
            return key;
        }
        
        public long getTimestamp() {
            return timestamp;
        }
    }
}
```

### Redis分布式缓存失效
```java
// Redis缓存管理器
@Component
public class RedisCacheManager {
    
    private final RedisTemplate<String, Object> redisTemplate;
    private final StringRedisTemplate stringRedisTemplate;
    
    public RedisCacheManager(RedisTemplate<String, Object> redisTemplate,
                            StringRedisTemplate stringRedisTemplate) {
        this.redisTemplate = redisTemplate;
        this.stringRedisTemplate = stringRedisTemplate;
    }
    
    // 设置缓存
    public void set(String key, Object value, Duration ttl) {
        redisTemplate.opsForValue().set(key, value, ttl);
    }
    
    // 获取缓存
    public Object get(String key) {
        return redisTemplate.opsForValue().get(key);
    }
    
    // 删除缓存
    public void delete(String key) {
        redisTemplate.delete(key);
    }
    
    // 批量删除
    public void delete(Collection<String> keys) {
        redisTemplate.delete(keys);
    }
    
    // 模式删除
    public void deleteByPattern(String pattern) {
        Set<String> keys = stringRedisTemplate.keys(pattern);
        if (!keys.isEmpty()) {
            redisTemplate.delete(keys);
        }
    }
    
    // 检查是否存在
    public boolean exists(String key) {
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }
    
    // 设置过期时间
    public void expire(String key, Duration ttl) {
        redisTemplate.expire(key, ttl);
    }
    
    // 获取剩余过期时间
    public Duration getTtl(String key) {
        Long ttl = redisTemplate.getExpire(key);
        return ttl != null && ttl > 0 ? Duration.ofSeconds(ttl) : Duration.ZERO;
    }
}

// 分布式缓存失效服务
@Service
public class DistributedCacheInvalidationService {
    
    private final RedisCacheManager redisCacheManager;
    private final ApplicationEventPublisher eventPublisher;
    private final RedisTemplate<String, Object> redisTemplate;
    
    @Value("${cache.invalidation.channel:cache:invalidation}")
    private String invalidationChannel;
    
    public DistributedCacheInvalidationService(RedisCacheManager redisCacheManager,
                                             ApplicationEventPublisher eventPublisher,
                                             RedisTemplate<String, Object> redisTemplate) {
        this.redisCacheManager = redisCacheManager;
        this.eventPublisher = eventPublisher;
        this.redisTemplate = redisTemplate;
    }
    
    // 本地失效并广播
    public void invalidateAndBroadcast(String key) {
        // 本地失效
        redisCacheManager.delete(key);
        
        // 广播失效事件
        InvalidationMessage message = new InvalidationMessage(key, InvalidationType.SINGLE, System.currentTimeMillis());
        redisTemplate.convertAndSend(invalidationChannel, message);
        
        // 发布本地事件
        eventPublisher.publishEvent(new CacheInvalidatedEvent(key, InvalidationStrategy.IMMEDIATE));
    }
    
    // 批量失效并广播
    public void invalidateBatchAndBroadcast(Set<String> keys) {
        // 本地失效
        redisCacheManager.delete(keys);
        
        // 广播失效事件
        InvalidationMessage message = new InvalidationMessage(keys, InvalidationType.BATCH, System.currentTimeMillis());
        redisTemplate.convertAndSend(invalidationChannel, message);
        
        // 发布本地事件
        eventPublisher.publishEvent(new BatchInvalidationEvent(keys));
    }
    
    // 模式失效并广播
    public void invalidatePatternAndBroadcast(String pattern) {
        // 本地失效
        redisCacheManager.deleteByPattern(pattern);
        
        // 广播失效事件
        InvalidationMessage message = new InvalidationMessage(pattern, InvalidationType.PATTERN, System.currentTimeMillis());
        redisTemplate.convertAndSend(invalidationChannel, message);
        
        // 发布本地事件
        eventPublisher.publishEvent(new PatternInvalidationEvent(pattern));
    }
    
    // 监听失效消息
    @RedisMessageListener(topic = "${cache.invalidation.channel:cache:invalidation}")
    public void handleInvalidationMessage(InvalidationMessage message) {
        switch (message.getType()) {
            case SINGLE:
                redisCacheManager.delete(message.getKey());
                break;
            case BATCH:
                redisCacheManager.delete(message.getKeys());
                break;
            case PATTERN:
                redisCacheManager.deleteByPattern(message.getPattern());
                break;
        }
        
        // 发布本地事件
        eventPublisher.publishEvent(new RemoteInvalidationEvent(message));
    }
    
    // 失效消息
    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class InvalidationMessage implements Serializable {
        private String key;
        private Set<String> keys;
        private String pattern;
        private InvalidationType type;
        private long timestamp;
        
        // 单个key构造
        public InvalidationMessage(String key, InvalidationType type, long timestamp) {
            this.key = key;
            this.type = type;
            this.timestamp = timestamp;
        }
        
        // 批量keys构造
        public InvalidationMessage(Set<String> keys, InvalidationType type, long timestamp) {
            this.keys = keys;
            this.type = type;
            this.timestamp = timestamp;
        }
        
        // 模式构造
        public InvalidationMessage(String pattern, InvalidationType type, long timestamp) {
            this.pattern = pattern;
            this.type = type;
            this.timestamp = timestamp;
        }
    }
    
    public enum InvalidationType {
        SINGLE, BATCH, PATTERN
    }
}
```

### 写入时失效策略
```java
// 写入时失效缓存服务
@Service
public class WriteThroughCacheService {
    
    private final UserRepository userRepository;
    private final RedisCacheManager cacheManager;
    private final DistributedCacheInvalidationService invalidationService;
    
    public WriteThroughCacheService(UserRepository userRepository,
                                   RedisCacheManager cacheManager,
                                   DistributedCacheInvalidationService invalidationService) {
        this.userRepository = userRepository;
        this.cacheManager = cacheManager;
        this.invalidationService = invalidationService;
    }
    
    // 更新用户（写入时失效）
    @Transactional
    public User updateUser(User user) {
        // 1. 更新数据库
        User updatedUser = userRepository.save(user);
        
        // 2. 失效相关缓存
        String userKey = "user:" + user.getId();
        String userCacheKey = "user:cache:" + user.getId();
        String userListKey = "user:list:*";
        
        // 批量失效
        Set<String> keysToInvalidate = new HashSet<>();
        keysToInvalidate.add(userKey);
        keysToInvalidate.add(userCacheKey);
        
        invalidationService.invalidateBatchAndBroadcast(keysToInvalidate);
        
        // 模式失效用户列表
        invalidationService.invalidatePatternAndBroadcast(userListKey);
        
        return updatedUser;
    }
    
    // 删除用户
    @Transactional
    public void deleteUser(String userId) {
        // 1. 删除数据库记录
        userRepository.deleteById(userId);
        
        // 2. 失效所有相关缓存
        String userPattern = "user:*:" + userId + "*";
        invalidationService.invalidatePatternAndBroadcast(userPattern);
        
        // 3. 失效用户列表缓存
        invalidationService.invalidatePatternAndBroadcast("user:list:*");
    }
    
    // 创建用户
    @Transactional
    public User createUser(User user) {
        // 1. 创建数据库记录
        User createdUser = userRepository.save(user);
        
        // 2. 失效用户列表缓存
        invalidationService.invalidatePatternAndBroadcast("user:list:*");
        
        return createdUser;
    }
    
    // 获取用户（缓存优先）
    public User getUser(String userId) {
        String cacheKey = "user:" + userId;
        
        // 尝试从缓存获取
        User cachedUser = (User) cacheManager.get(cacheKey);
        if (cachedUser != null) {
            return cachedUser;
        }
        
        // 从数据库获取
        Optional<User> userOptional = userRepository.findById(userId);
        if (!userOptional.isPresent()) {
            return null;
        }
        
        User user = userOptional.get();
        
        // 写入缓存
        cacheManager.set(cacheKey, user, Duration.ofMinutes(30));
        
        return user;
    }
}
```

### 延迟双删策略
```java
// 延迟双删缓存服务
@Service
public class DelayedDoubleDeleteCacheService {
    
    private final UserRepository userRepository;
    private final RedisCacheManager cacheManager;
    private final DistributedCacheInvalidationService invalidationService;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(10);
    
    public DelayedDoubleDeleteCacheService(UserRepository userRepository,
                                          RedisCacheManager cacheManager,
                                          DistributedCacheInvalidationService invalidationService) {
        this.userRepository = userRepository;
        this.cacheManager = cacheManager;
        this.invalidationService = invalidationService;
    }
    
    // 更新用户（延迟双删）
    @Transactional
    public User updateUserWithDelayedDoubleDelete(User user) {
        String cacheKey = "user:" + user.getId();
        
        // 1. 第一次删除缓存
        invalidationService.invalidateAndBroadcast(cacheKey);
        
        // 2. 更新数据库
        User updatedUser = userRepository.save(user);
        
        // 3. 延迟删除缓存（确保其他节点也删除了）
        scheduler.schedule(() -> {
            invalidationService.invalidateAndBroadcast(cacheKey);
        }, 500, TimeUnit.MILLISECONDS);
        
        return updatedUser;
    }
    
    // 删除用户（延迟双删）
    @Transactional
    public void deleteUserWithDelayedDoubleDelete(String userId) {
        String userPattern = "user:*:" + userId + "*";
        
        // 1. 第一次删除缓存
        invalidationService.invalidatePatternAndBroadcast(userPattern);
        
        // 2. 删除数据库
        userRepository.deleteById(userId);
        
        // 3. 延迟删除缓存
        scheduler.schedule(() -> {
            invalidationService.invalidatePatternAndBroadcast(userPattern);
        }, 500, TimeUnit.MILLISECONDS);
    }
    
    // 批量更新（延迟双删）
    @Transactional
    public List<User> updateUsersWithDelayedDoubleDelete(List<User> users) {
        List<String> cacheKeys = users.stream()
            .map(user -> "user:" + user.getId())
            .collect(Collectors.toList());
        
        // 1. 第一次批量删除缓存
        invalidationService.invalidateBatchAndBroadcast(new HashSet<>(cacheKeys));
        
        // 2. 批量更新数据库
        List<User> updatedUsers = userRepository.saveAll(users);
        
        // 3. 延迟批量删除缓存
        scheduler.schedule(() -> {
            invalidationService.invalidateBatchAndBroadcast(new HashSet<>(cacheKeys));
        }, 500, TimeUnit.MILLISECONDS);
        
        return updatedUsers;
    }
    
    @PreDestroy
    public void destroy() {
        scheduler.shutdown();
    }
}
```

### 缓存雪崩防护
```java
// 缓存雪崩防护服务
@Service
public class CacheAvalancheProtectionService {
    
    private final RedisCacheManager cacheManager;
    private final UserRepository userRepository;
    private final Random random = new Random();
    
    public CacheAvalancheProtectionService(RedisCacheManager cacheManager,
                                          UserRepository userRepository) {
        this.cacheManager = cacheManager;
        this.userRepository = userRepository;
    }
    
    // 获取用户（防雪崩）
    public User getUserWithAvalancheProtection(String userId) {
        String cacheKey = "user:" + userId;
        
        // 尝试从缓存获取
        User cachedUser = (User) cacheManager.get(cacheKey);
        if (cachedUser != null) {
            return cachedUser;
        }
        
        // 使用分布式锁防止缓存击穿
        String lockKey = "lock:user:" + userId;
        try {
            if (tryLock(lockKey, Duration.ofSeconds(5))) {
                // 双重检查
                cachedUser = (User) cacheManager.get(cacheKey);
                if (cachedUser != null) {
                    return cachedUser;
                }
                
                // 从数据库获取
                Optional<User> userOptional = userRepository.findById(userId);
                if (!userOptional.isPresent()) {
                    // 缓存空值防止穿透
                    cacheManager.set(cacheKey, null, Duration.ofMinutes(5));
                    return null;
                }
                
                User user = userOptional.get();
                
                // 设置随机过期时间防止雪崩
                long randomTtl = 30 + random.nextInt(10); // 30-40分钟
                cacheManager.set(cacheKey, user, Duration.ofMinutes(randomTtl));
                
                return user;
            } else {
                // 获取锁失败，使用降级策略
                return getFromDatabaseWithFallback(userId);
            }
        } finally {
            releaseLock(lockKey);
        }
    }
    
    // 批量获取用户（防雪崩）
    public Map<String, User> getUsersWithAvalancheProtection(List<String> userIds) {
        Map<String, User> result = new HashMap<>();
        List<String> missedIds = new ArrayList<>();
        
        // 批量从缓存获取
        for (String userId : userIds) {
            String cacheKey = "user:" + userId;
            User cachedUser = (User) cacheManager.get(cacheKey);
            if (cachedUser != null) {
                result.put(userId, cachedUser);
            } else {
                missedIds.add(userId);
            }
        }
        
        // 批量从数据库获取未命中的数据
        if (!missedIds.isEmpty()) {
            List<User> users = userRepository.findAllById(missedIds);
            
            for (User user : users) {
                String cacheKey = "user:" + user.getId();
                
                // 设置随机过期时间
                long randomTtl = 30 + random.nextInt(10);
                cacheManager.set(cacheKey, user, Duration.ofMinutes(randomTtl));
                
                result.put(user.getId(), user);
            }
            
            // 缓存不存在的用户ID
            for (String userId : missedIds) {
                if (!result.containsKey(userId)) {
                    String cacheKey = "user:" + userId;
                    cacheManager.set(cacheKey, null, Duration.ofMinutes(5));
                }
            }
        }
        
        return result;
    }
    
    // 尝试获取分布式锁
    private boolean tryLock(String lockKey, Duration timeout) {
        return cacheManager.setIfAbsent(lockKey, "locked", timeout);
    }
    
    // 释放分布式锁
    private void releaseLock(String lockKey) {
        cacheManager.delete(lockKey);
    }
    
    // 降级策略：从数据库获取
    private User getFromDatabaseWithFallback(String userId) {
        try {
            Optional<User> userOptional = userRepository.findById(userId);
            return userOptional.orElse(null);
        } catch (Exception e) {
            // 记录错误并返回null
            log.error("Fallback failed for user: {}", userId, e);
            return null;
        }
    }
}
```

## 最佳实践

### 失效策略选择
1. **数据一致性要求高**: 使用写入时失效
2. **性能要求高**: 使用延迟失效或批量失效
3. **分布式环境**: 使用分布式失效机制
4. **热点数据**: 使用多级缓存和预失效

### 防雪崩措施
1. **随机过期时间**: 避免同时失效
2. **分布式锁**: 防止缓存击穿
3. **降级策略**: 缓存故障时的备选方案
4. **监控告警**: 及时发现异常

### 性能优化
1. **批量操作**: 减少网络开销
2. **异步失效**: 不阻塞主流程
3. **本地缓存**: 减少远程调用
4. **预热策略**: 提前加载热点数据

### 监控管理
1. **命中率监控**: 监控缓存效果
2. **失效延迟**: 监控失效传播时间
3. **容量监控**: 监控缓存使用情况
4. **错误监控**: 监控失效失败

## 相关技能

- **database-sharding** - 数据库分片
- **distributed-consistency** - 分布式一致性
- **cap-theorem** - CAP定理
- **high-concurrency** - 高并发系统设计
- **algorithm-advisor** - 算法顾问
