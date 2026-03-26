# 高并发系统设计技术参考

## 概述

高并发系统设计是现代互联网应用的核心挑战，涉及如何在大量并发请求下保持系统的性能、稳定性和可扩展性。通过合理的架构设计和技术选型，可以构建能够处理海量并发请求的系统。

## 并发模型

### 多线程并发
```java
// Java线程池实现
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ThreadPoolExample {
    private static final int CORE_POOL_SIZE = 10;
    private static final int MAX_POOL_SIZE = 50;
    private static final int QUEUE_CAPACITY = 100;
    private static final long KEEP_ALIVE_TIME = 60L;
    
    private static ThreadPoolExecutor executor = new ThreadPoolExecutor(
        CORE_POOL_SIZE,
        MAX_POOL_SIZE,
        KEEP_ALIVE_TIME,
        TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(QUEUE_CAPACITY),
        new ThreadFactory() {
            private final AtomicInteger threadNumber = new AtomicInteger(1);
            
            @Override
            public Thread newThread(Runnable r) {
                Thread t = new Thread(r, "pool-thread-" + threadNumber.getAndIncrement());
                t.setDaemon(false);
                return t;
            }
        },
        new RejectedExecutionHandler() {
            @Override
            public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
                // 拒绝策略：记录日志并执行
                System.err.println("Task rejected, executing in caller thread");
                r.run();
            }
        }
    );
    
    public static void submitTask(Runnable task) {
        executor.submit(task);
    }
    
    public static void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

// 使用示例
class Task implements Runnable {
    private final int taskId;
    
    public Task(int taskId) {
        this.taskId = taskId;
    }
    
    @Override
    public void run() {
        System.out.println("Executing task " + taskId + " in thread " + 
                          Thread.currentThread().getName());
        try {
            Thread.sleep(1000); // 模拟耗时操作
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

// 提交任务
for (int i = 0; i < 100; i++) {
    ThreadPoolExample.submitTask(new Task(i));
}
```

### 协程并发
```python
# Python协程实现
import asyncio
import aiohttp
import time
from typing import List

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """异步获取URL内容"""
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

async def process_data(data: str) -> str:
    """异步处理数据"""
    await asyncio.sleep(0.1)  # 模拟处理时间
    return data.upper()

async def worker(session: aiohttp.ClientSession, url: str) -> str:
    """工作协程"""
    content = await fetch_url(session, url)
    if content:
        return await process_data(content)
    return ""

async def main():
    """主协程"""
    urls = [
        "https://api.example.com/data1",
        "https://api.example.com/data2",
        "https://api.example.com/data3",
        "https://api.example.com/data4",
        "https://api.example.com/data5"
    ]
    
    # 创建会话
    async with aiohttp.ClientSession() as session:
        # 并发执行所有任务
        tasks = [worker(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i} failed: {result}")
            else:
                print(f"Task {i} completed: {len(result)} chars")

# 限制并发数量的协程池
class CoroutinePool:
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_limit(self, coro):
        async with self.semaphore:
            return await coro

# 使用示例
async def limited_main():
    urls = [f"https://api.example.com/data{i}" for i in range(100)]
    pool = CoroutinePool(max_concurrent=10)
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            pool.run_with_limit(worker(session, url)) 
            for url in urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Completed {len(results)} tasks")

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"Total time: {time.time() - start_time:.2f} seconds")
```

### Actor模型
```scala
// Scala Akka Actor实现
import akka.actor.{Actor, ActorRef, ActorSystem, Props}
import akka.pattern.ask
import akka.util.Timeout
import scala.concurrent.duration._
import scala.concurrent.Future

// 定义消息
case class ProcessRequest(data: String)
case class ProcessResult(result: String)
case class GetStatus()

// Worker Actor
class WorkerActor extends Actor {
  def receive = {
    case ProcessRequest(data) =>
      // 处理请求
      val result = data.toUpperCase
      sender() ! ProcessResult(result)
      
    case GetStatus() =>
      sender() ! "Worker is running"
  }
}

// Master Actor
class MasterActor(workers: Int) extends Actor {
  private val workerPool = (1 to workers).map { i =>
    context.actorOf(Props[WorkerActor], s"worker-$i")
  }
  
  private var currentWorker = 0
  
  def receive = {
    case request: ProcessRequest =>
      val worker = workerPool(currentWorker % workers)
      worker.forward(request)
      currentWorker += 1
      
    case GetStatus() =>
      val status = s"Master managing $workers workers"
      sender() ! status
  }
}

// 使用示例
object ActorSystemExample {
  def main(args: Array[String]): Unit = {
    val system = ActorSystem("HighConcurrencySystem")
    val master = system.actorOf(Props(new MasterActor(10)), "master")
    
    implicit val timeout: Timeout = Timeout(5.seconds)
    
    // 发送请求
    val requests = (1 to 100).map { i =>
      master ? ProcessRequest(s"request-$i")
    }
    
    // 等待结果
    import system.dispatcher
    val results = Future.sequence(requests)
    
    results.foreach { resultList =>
      println(s"Processed ${resultList.size} requests")
      system.terminate()
    }
  }
}
```

## 缓存策略

### 多级缓存
```java
// Java多级缓存实现
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.data.redis.core.RedisTemplate;
import java.util.concurrent.TimeUnit;

public class MultiLevelCache<K, V> {
    private final Cache<K, V> localCache;
    private final RedisTemplate<K, V> redisTemplate;
    
    public MultiLevelCache(RedisTemplate<K, V> redisTemplate) {
        this.localCache = Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(10, TimeUnit.MINUTES)
            .build();
        this.redisTemplate = redisTemplate;
    }
    
    public V get(K key) {
        // 1. 检查本地缓存
        V value = localCache.getIfPresent(key);
        if (value != null) {
            return value;
        }
        
        // 2. 检查Redis缓存
        value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            localCache.put(key, value);
            return value;
        }
        
        // 3. 缓存未命中，返回null
        return null;
    }
    
    public void put(K key, V value) {
        // 同时写入本地缓存和Redis
        localCache.put(key, value);
        redisTemplate.opsForValue().set(key, value, 30, TimeUnit.MINUTES);
    }
    
    public void evict(K key) {
        // 从两级缓存中删除
        localCache.invalidate(key);
        redisTemplate.delete(key);
    }
    
    public void clear() {
        // 清空所有缓存
        localCache.invalidateAll();
        redisTemplate.getConnectionFactory().getConnection().flushDb();
    }
}

// 缓存预热
public class CacheWarmer {
    private final MultiLevelCache<String, Object> cache;
    private final DataLoader dataLoader;
    
    public CacheWarmer(MultiLevelCache<String, Object> cache, DataLoader dataLoader) {
        this.cache = cache;
        this.dataLoader = dataLoader;
    }
    
    @PostConstruct
    public void warmCache() {
        List<String> hotKeys = dataLoader.getHotKeys();
        
        hotKeys.parallelStream().forEach(key -> {
            Object value = dataLoader.loadFromDatabase(key);
            if (value != null) {
                cache.put(key, value);
            }
        });
    }
}
```

### 缓存穿透保护
```python
# Python缓存穿透保护
import redis
import json
import time
from typing import Optional, Any
from functools import wraps

class CachePenetrationProtection:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.empty_cache_ttl = 60  # 空值缓存60秒
        self.lock_timeout = 10     # 分布式锁超时时间
    
    def get_with_protection(self, key: str, loader_func, ttl: int = 300) -> Any:
        """获取缓存值，带穿透保护"""
        
        # 1. 检查缓存
        cached_value = self.redis.get(key)
        if cached_value is not None:
            if cached_value == b'EMPTY':
                return None  # 空值缓存
            return json.loads(cached_value)
        
        # 2. 获取分布式锁
        lock_key = f"lock:{key}"
        if not self.acquire_lock(lock_key):
            # 获取锁失败，等待并重试
            time.sleep(0.1)
            return self.get_with_protection(key, loader_func, ttl)
        
        try:
            # 3. 双重检查缓存
            cached_value = self.redis.get(key)
            if cached_value is not None:
                if cached_value == b'EMPTY':
                    return None
                return json.loads(cached_value)
            
            # 4. 从数据源加载
            value = loader_func()
            
            if value is None:
                # 5. 缓存空值防止穿透
                self.redis.setex(key, self.empty_cache_ttl, 'EMPTY')
            else:
                # 6. 缓存正常值
                self.redis.setex(key, ttl, json.dumps(value))
            
            return value
            
        finally:
            # 7. 释放锁
            self.release_lock(lock_key)
    
    def acquire_lock(self, lock_key: str) -> bool:
        """获取分布式锁"""
        return self.redis.set(lock_key, '1', nx=True, ex=self.lock_timeout)
    
    def release_lock(self, lock_key: str):
        """释放分布式锁"""
        self.redis.delete(lock_key)

# 装饰器版本
def cache_protected(redis_client: redis.Redis, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            protection = CachePenetrationProtection(redis_client)
            return protection.get_with_protection(
                cache_key, 
                lambda: func(*args, **kwargs), 
                ttl
            )
        return wrapper
    return decorator

# 使用示例
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@cache_protected(redis_client, ttl=300)
def get_user_data(user_id: int) -> dict:
    """获取用户数据"""
    # 模拟数据库查询
    if user_id == 999:
        return None  # 不存在的用户
    return {"id": user_id, "name": f"User {user_id}"}

# 测试
print(get_user_data(1))  # 正常用户
print(get_user_data(999)) # 不存在的用户
print(get_user_data(999)) # 第二次查询，返回缓存空值
```

## 负载均衡

### 轮询负载均衡
```go
// Go轮询负载均衡实现
package main

import (
    "fmt"
    "net/http"
    "sync/atomic"
)

type Backend struct {
    URL    string
    Weight int
    Active bool
}

type RoundRobinBalancer struct {
    backends []Backend
    current  uint64
}

func NewRoundRobinBalancer(backends []Backend) *RoundRobinBalancer {
    return &RoundRobinBalancer{
        backends: backends,
        current:  0,
    }
}

func (rb *RoundRobinBalancer) NextBackend() *Backend {
    // 获取活跃的后端
    activeBackends := make([]Backend, 0)
    for _, backend := range rb.backends {
        if backend.Active {
            activeBackends = append(activeBackends, backend)
        }
    }
    
    if len(activeBackends) == 0 {
        return nil
    }
    
    // 轮询选择
    index := atomic.AddUint64(&rb.current, 1) - 1
    backend := &activeBackends[index%uint64(len(activeBackends))]
    
    return backend
}

func (rb *RoundRobinBalancer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    backend := rb.NextBackend()
    if backend == nil {
        http.Error(w, "No available backends", http.StatusServiceUnavailable)
        return
    }
    
    // 转发请求到后端
    proxyReq, err := http.NewRequest(r.Method, backend.URL+r.URL.Path, r.Body)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    // 复制头部
    for key, values := range r.Header {
        for _, value := range values {
            proxyReq.Header.Add(key, value)
        }
    }
    
    client := &http.Client{}
    resp, err := client.Do(proxyReq)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadGateway)
        return
    }
    defer resp.Body.Close()
    
    // 复制响应
    for key, values := range resp.Header {
        for _, value := range values {
            w.Header().Add(key, value)
        }
    }
    w.WriteHeader(resp.StatusCode)
    
    // 流式复制响应体
    _, err = io.Copy(w, resp.Body)
    if err != nil {
        fmt.Printf("Error copying response: %v\n", err)
    }
}

func main() {
    backends := []Backend{
        {URL: "http://localhost:8081", Weight: 1, Active: true},
        {URL: "http://localhost:8082", Weight: 1, Active: true},
        {URL: "http://localhost:8083", Weight: 1, Active: true},
    }
    
    balancer := NewRoundRobinBalancer(backends)
    
    fmt.Println("Load balancer starting on port 8080")
    http.ListenAndServe(":8080", balancer)
}
```

### 加权轮询负载均衡
```javascript
// JavaScript加权轮询负载均衡
class WeightedRoundRobinBalancer {
    constructor(backends) {
        this.backends = backends.map(backend => ({
            ...backend,
            currentWeight: 0,
            effectiveWeight: backend.weight
        }));
        this.totalWeight = this.backends.reduce((sum, b) => sum + b.weight, 0);
    }
    
    getNextBackend() {
        if (this.backends.length === 0) {
            return null;
        }
        
        // 过滤活跃的后端
        const activeBackends = this.backends.filter(b => b.active);
        if (activeBackends.length === 0) {
            return null;
        }
        
        // 选择权重最高的后端
        let selected = null;
        let maxCurrentWeight = -Infinity;
        
        for (const backend of activeBackends) {
            backend.currentWeight += backend.effectiveWeight;
            
            if (backend.currentWeight > maxCurrentWeight) {
                maxCurrentWeight = backend.currentWeight;
                selected = backend;
            }
        }
        
        if (selected) {
            selected.currentWeight -= this.totalWeight;
            return selected;
        }
        
        return activeBackends[0];
    }
    
    updateBackendHealth(url, healthy) {
        const backend = this.backends.find(b => b.url === url);
        if (backend) {
            backend.active = healthy;
            if (!healthy) {
                backend.effectiveWeight = Math.max(1, backend.effectiveWeight - 1);
            } else {
                backend.effectiveWeight = Math.min(backend.weight, backend.effectiveWeight + 1);
            }
        }
    }
    
    getStats() {
        return {
            totalBackends: this.backends.length,
            activeBackends: this.backends.filter(b => b.active).length,
            backends: this.backends.map(b => ({
                url: b.url,
                weight: b.weight,
                effectiveWeight: b.effectiveWeight,
                active: b.active
            }))
        };
    }
}

// 使用示例
const balancer = new WeightedRoundRobinBalancer([
    { url: 'http://server1:8080', weight: 3, active: true },
    { url: 'http://server2:8080', weight: 2, active: true },
    { url: 'http://server3:8080', weight: 1, active: true }
]);

// 模拟请求分发
for (let i = 0; i < 10; i++) {
    const backend = balancer.getNextBackend();
    console.log(`Request ${i + 1} -> ${backend.url}`);
}

// 健康检查
setInterval(() => {
    balancer.backends.forEach(backend => {
        // 模拟健康检查
        const healthy = Math.random() > 0.1; // 90%健康率
        balancer.updateBackendHealth(backend.url, healthy);
    });
    
    console.log('Backend stats:', balancer.getStats());
}, 5000);
```

## 限流策略

### 令牌桶限流
```python
# Python令牌桶限流实现
import time
import threading
from typing import Callable, Any

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        """
        初始化令牌桶
        :param capacity: 桶的容量
        :param refill_rate: 令牌补充速率（每秒）
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def refill(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        with self.lock:
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """消费令牌"""
        self.refill()
        
        with self.lock:
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class RateLimiter:
    def __init__(self):
        self.buckets = {}
    
    def get_bucket(self, key: str, capacity: int, refill_rate: float) -> TokenBucket:
        """获取或创建令牌桶"""
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(capacity, refill_rate)
        return self.buckets[key]
    
    def is_allowed(self, key: str, capacity: int, refill_rate: float, tokens: int = 1) -> bool:
        """检查是否允许请求"""
        bucket = self.get_bucket(key, capacity, refill_rate)
        return bucket.consume(tokens)

# 装饰器实现
def rate_limit(key_func: Callable, capacity: int, refill_rate: float, tokens: int = 1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成限流键
            key = key_func(*args, **kwargs)
            
            # 检查限流
            if not rate_limiter.is_allowed(key, capacity, refill_rate, tokens):
                raise Exception("Rate limit exceeded")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 全局限流器实例
rate_limiter = RateLimiter()

# 使用示例
@rate_limit(key_func=lambda user_id: f"user:{user_id}", capacity=10, refill_rate=1.0)
def api_call(user_id: int):
    print(f"API call for user {user_id} at {time.time()}")

# 测试
for i in range(15):
    try:
        api_call(1)
    except Exception as e:
        print(f"Request {i+1}: {e}")
    time.sleep(0.1)
```

### 滑动窗口限流
```java
// Java滑动窗口限流实现
import java.util.concurrent.*;
import java.util.*;

public class SlidingWindowRateLimiter {
    private final int maxRequests;
    private final long windowSizeMillis;
    private final Map<String, Queue<Long>> requestWindows;
    private final ScheduledExecutorService scheduler;
    
    public SlidingWindowRateLimiter(int maxRequests, long windowSizeMillis) {
        this.maxRequests = maxRequests;
        this.windowSizeMillis = windowSizeMillis;
        this.requestWindows = new ConcurrentHashMap<>();
        this.scheduler = Executors.newScheduledThreadPool(1);
        
        // 定期清理过期请求
        scheduler.scheduleAtFixedRate(this::cleanupExpiredRequests, 
                                     windowSizeMillis, windowSizeMillis, 
                                     TimeUnit.MILLISECONDS);
    }
    
    public boolean isAllowed(String key) {
        long currentTime = System.currentTimeMillis();
        long windowStart = currentTime - windowSizeMillis;
        
        // 获取或创建请求窗口
        Queue<Long> requests = requestWindows.computeIfAbsent(key, k -> new ConcurrentLinkedQueue<>());
        
        // 移除过期请求
        while (!requests.isEmpty() && requests.peek() < windowStart) {
            requests.poll();
        }
        
        // 检查是否超过限制
        if (requests.size() >= maxRequests) {
            return false;
        }
        
        // 记录新请求
        requests.offer(currentTime);
        return true;
    }
    
    private void cleanupExpiredRequests() {
        long currentTime = System.currentTimeMillis();
        long windowStart = currentTime - windowSizeMillis;
        
        requestWindows.forEach((key, requests) -> {
            while (!requests.isEmpty() && requests.peek() < windowStart) {
                requests.poll();
            }
            
            // 移除空队列以节省内存
            if (requests.isEmpty()) {
                requestWindows.remove(key);
            }
        });
    }
    
    public Map<String, Integer> getCurrentStats() {
        Map<String, Integer> stats = new HashMap<>();
        requestWindows.forEach((key, requests) -> {
            stats.put(key, requests.size());
        });
        return stats;
    }
    
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}

// 使用示例
class ApiController {
    private final SlidingWindowRateLimiter rateLimiter;
    
    public ApiController() {
        // 每分钟最多100个请求
        this.rateLimiter = new SlidingWindowRateLimiter(100, 60_000);
    }
    
    public void handleRequest(String userId) {
        String key = "user:" + userId;
        
        if (rateLimiter.isAllowed(key)) {
            System.out.println("Request allowed for user: " + userId);
            // 处理请求逻辑
        } else {
            System.out.println("Rate limit exceeded for user: " + userId);
            // 返回限流错误
        }
    }
    
    public void printStats() {
        System.out.println("Current stats: " + rateLimiter.getCurrentStats());
    }
}

// 测试代码
public class RateLimiterTest {
    public static void main(String[] args) throws InterruptedException {
        ApiController controller = new ApiController();
        
        // 模拟多个用户的并发请求
        ExecutorService executor = Executors.newFixedThreadPool(20);
        
        for (int i = 0; i < 200; i++) {
            final int requestNum = i;
            executor.submit(() -> {
                String userId = "user" + (requestNum % 5); // 5个用户
                controller.handleRequest(userId);
            });
        }
        
        Thread.sleep(1000);
        controller.printStats();
        
        executor.shutdown();
        controller.rateLimiter.shutdown();
    }
}
```

## 消息队列

### Kafka高并发处理
```scala
// Scala Kafka生产者实现
import java.util.{Properties, Collections}
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerRecord, ProducerConfig}
import org.apache.kafka.common.serialization.StringSerializer
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Future

class HighThroughputProducer(bootstrapServers: String) {
  private val props = new Properties()
  props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers)
  props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, classOf[StringSerializer].getName)
  props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, classOf[StringSerializer].getName)
  
  // 高吞吐量配置
  props.put(ProducerConfig.BATCH_SIZE_CONFIG, "16384")
  props.put(ProducerConfig.LINGER_MS_CONFIG, "5")
  props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy")
  props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, "33554432")
  props.put(ProducerConfig.ACKS_CONFIG, "1")
  props.put(ProducerConfig.RETRIES_CONFIG, "3")
  
  private val producer = new KafkaProducer[String, String](props)
  
  def sendMessage(topic: String, key: String, value: String): Future[Unit] = {
    val record = new ProducerRecord(topic, key, value)
    val future = producer.send(record)
    
    future.map { metadata =>
      println(s"Message sent to partition ${metadata.partition()}, offset ${metadata.offset()}")
    }.recover {
      case ex => println(s"Failed to send message: ${ex.getMessage}")
    }
  }
  
  def sendBatchMessages(topic: String, messages: List[(String, String)]): Future[Unit] = {
    val futures = messages.map { case (key, value) =>
      sendMessage(topic, key, value)
    }
    
    Future.sequence(futures).map(_ => ())
  }
  
  def close(): Unit = {
    producer.flush()
    producer.close()
  }
}

// Kafka消费者实现
import org.apache.kafka.clients.consumer.{ConsumerConfig, KafkaConsumer, ConsumerRecords}
import org.apache.kafka.common.serialization.StringDeserializer
import java.time.Duration
import java.util.{Collections, Properties}
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.ExecutionContext.Implicits.global

class HighThroughputConsumer(bootstrapServers: String, groupId: String, topic: String) {
  private val props = new Properties()
  props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers)
  props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId)
  props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, classOf[StringDeserializer].getName)
  props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, classOf[StringDeserializer].getName)
  
  // 高吞吐量配置
  props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, "1024")
  props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, "500")
  props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "500")
  props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false")
  props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest")
  
  private val consumer = new KafkaConsumer[String, String](props)
  consumer.subscribe(Collections.singletonList(topic))
  
  def startPolling(processor: String => Unit): Future[Unit] = {
    Future {
      while (true) {
        try {
          val records: ConsumerRecords[String, String] = consumer.poll(Duration.ofMillis(1000))
          
          records.forEach { record =>
            try {
              processor(record.value())
            } catch {
              case ex: Exception =>
                println(s"Error processing record: ${ex.getMessage}")
            }
          }
          
          // 手动提交偏移量
          consumer.commitSync()
          
        } catch {
          case ex: Exception =>
            println(s"Consumer error: ${ex.getMessage}")
            Thread.sleep(1000) // 等待后重试
        }
      }
    }
  }
  
  def close(): Unit = {
    consumer.close()
  }
}

// 使用示例
object KafkaExample {
  def main(args: Array[String]): Unit = {
    val bootstrapServers = "localhost:9092"
    val topic = "high-concurrency-topic"
    
    // 生产者
    val producer = new HighThroughputProducer(bootstrapServers)
    
    // 发送批量消息
    val messages = (1 to 1000).map(i => (s"key-$i", s"message-$i"))
    producer.sendBatchMessages(topic, messages)
    
    // 消费者
    val consumer = new HighThroughputConsumer(bootstrapServers, "test-group", topic)
    
    consumer.startPolling { message =>
      println(s"Processing: $message")
      // 模拟处理时间
      Thread.sleep(10)
    }
    
    // 等待一段时间后关闭
    Thread.sleep(10000)
    
    producer.close()
    consumer.close()
  }
}
```

## 相关资源

### 官方文档
- [Java Concurrency in Practice](https://jcip.net/)
- [Akka Documentation](https://akka.io/docs/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

### 技术博客
- [High Scalability](https://highscalability.com/)
- [Martin Fowler's Blog](https://martinfowler.com/)
- [Netflix Tech Blog](https://netflixtechblog.com/)

### 开源项目
- [Disruptor](https://github.com/LMAX-Exchange/disruptor) - 高性能并发框架
- [Netty](https://netty.io/) - 异步网络框架
- [Vert.x](https://vertx.io/) - 响应式编程框架

### 学习资源
- [Designing Data-Intensive Applications](https://dataintensive.net/)
- [Building Microservices](https://www.oreilly.com/library/view/building-microservices/9781491950340/)
- [The Art of Multiprocessor Programming](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0123973375)

### 在线课程
- [Coursera - High Performance Computing](https://www.coursera.org/specializations/high-performance-computing)
- [edX - Parallel Programming](https://www.edx.org/learn/parallel-programming)

### 社区资源
- [Stack Overflow - Concurrency](https://stackoverflow.com/questions/tagged/concurrency)
- [Reddit - r/programming](https://www.reddit.com/r/programming/)
- [InfoQ - Architecture](https://www.infoq.com/architecture/)
