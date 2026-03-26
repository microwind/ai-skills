# 数据库分片技术参考

## 概述

数据库分片是将大型数据库水平分割成多个较小的数据库的过程，每个分片存储数据的一个子集。分片是解决大规模数据存储和高并发访问的关键技术，能够显著提升系统的可扩展性和性能。

## 分片策略

### 水平分片
水平分片将表中的行分布到不同的分片中。

```sql
-- 用户表分片示例
-- 分片1: users_0 (user_id % 4 = 0)
-- 分片2: users_1 (user_id % 4 = 1)  
-- 分片3: users_2 (user_id % 4 = 2)
-- 分片4: users_3 (user_id % 4 = 3)

CREATE TABLE users_0 (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    created_at TIMESTAMP
);

CREATE TABLE users_1 (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    created_at TIMESTAMP
);

-- 类似创建 users_2, users_3
```

### 垂直分片
垂直分片将表中的列分布到不同的分片中。

```sql
-- 用户基本信息分片
CREATE TABLE users_basic (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    created_at TIMESTAMP
);

-- 用户扩展信息分片
CREATE TABLE users_extended (
    user_id BIGINT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    address TEXT,
    updated_at TIMESTAMP
);

-- 用户偏好设置分片
CREATE TABLE users_preferences (
    user_id BIGINT PRIMARY KEY,
    theme VARCHAR(20),
    language VARCHAR(10),
    timezone VARCHAR(50),
    notifications JSON,
    created_at TIMESTAMP
);
```

## 分片算法

### 哈希分片
```java
// Java哈希分片实现
public class HashSharding {
    private final int shardCount;
    private final List<String> shardUrls;
    
    public HashSharding(List<String> shardUrls) {
        this.shardCount = shardUrls.size();
        this.shardUrls = shardUrls;
    }
    
    public int getShardId(String key) {
        return Math.abs(key.hashCode()) % shardCount;
    }
    
    public String getShardUrl(String key) {
        int shardId = getShardId(key);
        return shardUrls.get(shardId);
    }
    
    // 一致性哈希分片
    public int getConsistentHashShard(String key) {
        return ConsistentHash.getShard(key, shardCount);
    }
}

// 使用示例
List<String> shards = Arrays.asList(
    "jdbc:mysql://shard1:3306/db",
    "jdbc:mysql://shard2:3306/db", 
    "jdbc:mysql://shard3:3306/db",
    "jdbc:mysql://shard4:3306/db"
);

HashSharding sharding = new HashSharding(shards);

// 根据用户ID确定分片
String userId = "user12345";
int shardId = sharding.getShardId(userId);
String shardUrl = sharding.getShardUrl(userId);

System.out.println("User " + userId + " is in shard " + shardId);
```

### 范围分片
```python
# Python范围分片实现
class RangeSharding:
    def __init__(self, shard_ranges):
        """
        shard_ranges: [(start_range, end_range, shard_id), ...]
        """
        self.shard_ranges = sorted(shard_ranges, key=lambda x: x[0])
    
    def get_shard_id(self, key):
        """根据键值确定分片ID"""
        if isinstance(key, str):
            try:
                key = int(key)
            except ValueError:
                # 对于字符串键，可以计算哈希值
                key = hash(key) % 1000000
        
        for start_range, end_range, shard_id in self.shard_ranges:
            if start_range <= key < end_range:
                return shard_id
        
        # 如果不在任何范围内，返回默认分片
        return self.shard_ranges[-1][2]

# 使用示例
shard_ranges = [
    (0, 1000000, "shard_0"),      # 用户ID 0-999999
    (1000000, 2000000, "shard_1"), # 用户ID 1000000-1999999
    (2000000, 3000000, "shard_2"), # 用户ID 2000000-2999999
    (3000000, float('inf'), "shard_3") # 用户ID 3000000+
]

sharding = RangeSharding(shard_ranges)

# 测试分片
user_ids = [500000, 1500000, 2500000, 3500000]
for user_id in user_ids:
    shard_id = sharding.get_shard_id(user_id)
    print(f"User {user_id} -> {shard_id}")
```

### 目录分片
```javascript
// JavaScript目录分片实现
class DirectorySharding {
    constructor() {
        this.directory = new Map(); // key -> shard_id
        this.shards = new Map();    // shard_id -> connection_info
    }
    
    addShard(shardId, connectionInfo) {
        this.shards.set(shardId, connectionInfo);
    }
    
    addMapping(key, shardId) {
        this.directory.set(key, shardId);
    }
    
    getShardId(key) {
        return this.directory.get(key);
    }
    
    getShardInfo(shardId) {
        return this.shards.get(shardId);
    }
    
    removeMapping(key) {
        const shardId = this.directory.get(key);
        this.directory.delete(key);
        return shardId;
    }
    
    moveKey(key, newShardId) {
        const oldShardId = this.directory.get(key);
        this.directory.set(key, newShardId);
        return oldShardId;
    }
    
    getShardStats() {
        const stats = {};
        for (const [key, shardId] of this.directory) {
            stats[shardId] = (stats[shardId] || 0) + 1;
        }
        return stats;
    }
}

// 使用示例
const directory = new DirectorySharding();

// 添加分片
directory.addShard('shard_1', { host: 'db1.example.com', port: 3306 });
directory.addShard('shard_2', { host: 'db2.example.com', port: 3306 });
directory.addShard('shard_3', { host: 'db3.example.com', port: 3306 });

// 添加键映射
directory.addMapping('user_123', 'shard_1');
directory.addMapping('user_456', 'shard_2');
directory.addMapping('user_789', 'shard_3');

// 获取分片信息
const shardId = directory.getShardId('user_123');
const shardInfo = directory.getShardInfo(shardId);

console.log(`User is in ${shardId}:`, shardInfo);

// 移动键到新分片
const oldShard = directory.moveKey('user_123', 'shard_2');
console.log(`Moved from ${oldShard} to shard_2`);

// 获取分片统计
console.log('Shard statistics:', directory.getShardStats());
```

## 分片路由

### 分片路由器实现
```go
// Go分片路由器实现
package sharding

import (
    "database/sql"
    "errors"
    "fmt"
    "hash/fnv"
    "sync"
)

type Shard struct {
    ID       int
    DB       *sql.DB
    Host     string
    Port     int
    Database string
}

type ShardRouter struct {
    shards      []*Shard
    shardCount  int
    algorithm   string // "hash", "range", "directory"
    directory   map[string]int // directory分片用
    mu          sync.RWMutex
}

func NewShardRouter(shards []*Shard, algorithm string) *ShardRouter {
    return &ShardRouter{
        shards:     shards,
        shardCount: len(shards),
        algorithm:  algorithm,
        directory:  make(map[string]int),
    }
}

func (sr *ShardRouter) GetShard(key string) (*Shard, error) {
    sr.mu.RLock()
    defer sr.mu.RUnlock()
    
    var shardIndex int
    
    switch sr.algorithm {
    case "hash":
        shardIndex = sr.hashShard(key)
    case "range":
        shardIndex = sr.rangeShard(key)
    case "directory":
        shardIndex = sr.directoryShard(key)
    default:
        return nil, errors.New("unsupported sharding algorithm")
    }
    
    if shardIndex >= sr.shardCount {
        return nil, errors.New("shard index out of range")
    }
    
    return sr.shards[shardIndex], nil
}

func (sr *ShardRouter) hashShard(key string) int {
    h := fnv.New32a()
    h.Write([]byte(key))
    return int(h.Sum32()) % sr.shardCount
}

func (sr *ShardRouter) rangeShard(key string) int {
    // 简化的范围分片实现
    // 实际应用中应该有更复杂的范围定义
    hash := sr.hashShard(key)
    return hash
}

func (sr *ShardRouter) directoryShard(key string) int {
    shardId, exists := sr.directory[key]
    if !exists {
        return 0 // 默认分片
    }
    return shardId
}

func (sr *ShardRouter) AddDirectoryMapping(key string, shardId int) {
    sr.mu.Lock()
    defer sr.mu.Unlock()
    sr.directory[key] = shardId
}

func (sr *ShardRouter) Query(key string, query string, args ...interface{}) (*sql.Rows, error) {
    shard, err := sr.GetShard(key)
    if err != nil {
        return nil, err
    }
    
    return shard.DB.Query(query, args...)
}

func (sr *ShardRouter) Execute(key string, query string, args ...interface{}) (sql.Result, error) {
    shard, err := sr.GetShard(key)
    if err != nil {
        return nil, err
    }
    
    return shard.DB.Exec(query, args...)
}

// 使用示例
func main() {
    // 初始化分片连接
    shards := []*Shard{
        {ID: 0, Host: "shard1", Port: 3306, Database: "db"},
        {ID: 1, Host: "shard2", Port: 3306, Database: "db"},
        {ID: 2, Host: "shard3", Port: 3306, Database: "db"},
        {ID: 3, Host: "shard4", Port: 3306, Database: "db"},
    }
    
    // 实际应用中需要建立数据库连接
    for _, shard := range shards {
        db, err := sql.Open("mysql", fmt.Sprintf("%s:%d@tcp(%s:%d)/%s", 
            "user", "password", shard.Host, shard.Port, shard.Database))
        if err != nil {
            panic(err)
        }
        shard.DB = db
    }
    
    router := NewShardRouter(shards, "hash")
    
    // 查询用户数据
    rows, err := router.Query("user123", "SELECT * FROM users WHERE id = ?", "user123")
    if err != nil {
        panic(err)
    }
    defer rows.Close()
    
    // 处理查询结果
    for rows.Next() {
        var id, username, email string
        var createdAt time.Time
        err := rows.Scan(&id, &username, &email, &createdAt)
        if err != nil {
            panic(err)
        }
        fmt.Printf("User: %s, %s, %s\n", id, username, email)
    }
}
```

## 跨分片查询

### 跨分片查询处理器
```python
# Python跨分片查询实现
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional
import dataclasses

@dataclasses.dataclass
class QueryResult:
    shard_id: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None

class CrossShardQueryProcessor:
    def __init__(self, shard_router):
        self.shard_router = shard_router
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def execute_parallel_query(self, query: str, params: List = None) -> List[QueryResult]:
        """并行查询所有分片"""
        if params is None:
            params = []
            
        # 获取所有分片
        shards = self.shard_router.get_all_shards()
        
        # 创建异步任务
        tasks = []
        for shard in shards:
            task = asyncio.create_task(
                self._execute_shard_query(shard, query, params)
            )
            tasks.append(task)
        
        # 等待所有查询完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        query_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                query_results.append(QueryResult(
                    shard_id=shards[i].id,
                    data=[],
                    error=str(result)
                ))
            else:
                query_results.append(result)
        
        return query_results
    
    async def _execute_shard_query(self, shard, query: str, params: List) -> QueryResult:
        """在单个分片上执行查询"""
        loop = asyncio.get_event_loop()
        
        try:
            # 在线程池中执行同步数据库操作
            result = await loop.run_in_executor(
                self.executor,
                self._sync_query,
                shard,
                query,
                params
            )
            return QueryResult(shard_id=shard.id, data=result)
        except Exception as e:
            return QueryResult(shard_id=shard.id, data=[], error=str(e))
    
    def _sync_query(self, shard, query: str, params: List) -> List[Dict[str, Any]]:
        """同步执行数据库查询"""
        cursor = shard.connection.cursor()
        cursor.execute(query, params)
        
        # 获取列名
        columns = [desc[0] for desc in cursor.description]
        
        # 获取数据
        rows = cursor.fetchall()
        
        # 转换为字典列表
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        
        cursor.close()
        return result
    
    async def execute_aggregated_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """执行聚合查询"""
        if params is None:
            params = []
        
        # 并行查询所有分片
        results = await self.execute_parallel_query(query, params)
        
        # 聚合结果
        aggregated_data = []
        total_count = 0
        errors = []
        
        for result in results:
            if result.error:
                errors.append(f"Shard {result.shard_id}: {result.error}")
            else:
                aggregated_data.extend(result.data)
                total_count += len(result.data)
        
        return {
            'data': aggregated_data,
            'total_count': total_count,
            'shard_count': len(results),
            'error_count': len(errors),
            'errors': errors
        }
    
    async def execute_ordered_query(self, query: str, order_by: str, 
                                   limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """执行需要排序的跨分片查询"""
        # 获取所有分片数据
        aggregated_result = await self.execute_aggregated_query(query)
        
        if aggregated_result['errors']:
            print(f"Query errors: {aggregated_result['errors']}")
        
        # 排序
        sorted_data = sorted(
            aggregated_result['data'],
            key=lambda x: x.get(order_by, ''),
            reverse=True
        )
        
        # 分页
        if offset > 0:
            sorted_data = sorted_data[offset:]
        
        if limit is not None:
            sorted_data = sorted_data[:limit]
        
        return sorted_data

# 使用示例
async def main():
    # 假设已经配置好了分片路由器
    shard_router = ShardRouter()
    query_processor = CrossShardQueryProcessor(shard_router)
    
    # 并行查询所有用户
    query = "SELECT * FROM users WHERE status = 'active'"
    results = await query_processor.execute_parallel_query(query)
    
    print(f"Queried {len(results)} shards")
    for result in results:
        if result.error:
            print(f"Shard {result.shard_id} error: {result.error}")
        else:
            print(f"Shard {result.shard_id}: {len(result.data)} records")
    
    # 聚合查询
    aggregated = await query_processor.execute_aggregated_query(query)
    print(f"Total records: {aggregated['total_count']}")
    
    # 排序查询
    ordered_users = await query_processor.execute_ordered_query(
        query, 
        order_by='created_at',
        limit=10
    )
    print(f"Top 10 users: {len(ordered_users)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 分片管理

### 分片管理器
```java
// Java分片管理器实现
import java.util.*;
import java.util.concurrent.*;
import java.sql.*;

public class ShardManager {
    private final Map<Integer, Shard> shards;
    private final ShardRouter router;
    private final ExecutorService executor;
    private final ScheduledExecutorService scheduler;
    
    public ShardManager(List<ShardConfig> configs) {
        this.shards = new ConcurrentHashMap<>();
        this.router = new ShardRouter();
        this.executor = Executors.newFixedThreadPool(10);
        this.scheduler = Executors.newScheduledThreadPool(2);
        
        // 初始化分片
        for (ShardConfig config : configs) {
            Shard shard = createShard(config);
            shards.put(config.getId(), shard);
            router.addShard(config.getId(), shard);
        }
        
        // 启动健康检查
        startHealthCheck();
    }
    
    private Shard createShard(ShardConfig config) {
        try {
            Connection connection = DriverManager.getConnection(
                config.getJdbcUrl(),
                config.getUsername(),
                config.getPassword()
            );
            
            return new Shard(
                config.getId(),
                connection,
                config.getHost(),
                config.getPort(),
                config.getDatabase()
            );
        } catch (SQLException e) {
            throw new RuntimeException("Failed to create shard: " + config.getId(), e);
        }
    }
    
    public CompletableFuture<Void> addShard(ShardConfig config) {
        return CompletableFuture.runAsync(() -> {
            Shard shard = createShard(config);
            shards.put(config.getId(), shard);
            router.addShard(config.getId(), shard);
            
            // 重新平衡数据
            rebalanceData();
        }, executor);
    }
    
    public CompletableFuture<Void> removeShard(int shardId) {
        return CompletableFuture.runAsync(() -> {
            Shard shard = shards.remove(shardId);
            if (shard != null) {
                router.removeShard(shardId);
                
                try {
                    shard.getConnection().close();
                } catch (SQLException e) {
                    // 记录日志
                }
                
                // 重新平衡数据
                rebalanceData();
            }
        }, executor);
    }
    
    public CompletableFuture<ShardHealth> checkShardHealth(int shardId) {
        return CompletableFuture.supplyAsync(() -> {
            Shard shard = shards.get(shardId);
            if (shard == null) {
                return ShardHealth.DOWN;
            }
            
            try {
                Connection connection = shard.getConnection();
                if (connection.isValid(5)) {
                    return ShardHealth.HEALTHY;
                } else {
                    return ShardHealth.UNHEALTHY;
                }
            } catch (SQLException e) {
                return ShardHealth.DOWN;
            }
        }, executor);
    }
    
    private void startHealthCheck() {
        scheduler.scheduleAtFixedRate(() -> {
            List<CompletableFuture<ShardHealth>> healthChecks = new ArrayList<>();
            
            for (Integer shardId : shards.keySet()) {
                healthChecks.add(checkShardHealth(shardId));
            }
            
            // 等待所有健康检查完成
            CompletableFuture<Void> allChecks = CompletableFuture.allOf(
                healthChecks.toArray(new CompletableFuture[0])
            );
            
            allChecks.thenRun(() -> {
                for (int i = 0; i < shards.size(); i++) {
                    try {
                        ShardHealth health = healthChecks.get(i).get();
                        int shardId = (Integer) shards.keySet().toArray()[i];
                        
                        // 处理不健康的分片
                        if (health == ShardHealth.DOWN) {
                            handleShardFailure(shardId);
                        }
                    } catch (Exception e) {
                        // 记录日志
                    }
                }
            });
        }, 30, 30, TimeUnit.SECONDS);
    }
    
    private void handleShardFailure(int shardId) {
        // 处理分片故障
        System.err.println("Shard " + shardId + " is down!");
        
        // 可以实现故障转移逻辑
        // 例如：将请求路由到备用分片
    }
    
    private void rebalanceData() {
        // 数据重新平衡逻辑
        System.out.println("Rebalancing data across shards...");
    }
    
    public Map<Integer, ShardStats> getShardStats() {
        Map<Integer, ShardStats> stats = new HashMap<>();
        
        for (Map.Entry<Integer, Shard> entry : shards.entrySet()) {
            int shardId = entry.getKey();
            Shard shard = entry.getValue();
            
            try {
                Connection connection = shard.getConnection();
                Statement stmt = connection.createStatement();
                ResultSet rs = stmt.executeQuery("SELECT COUNT(*) as count FROM information_schema.tables");
                
                int tableCount = 0;
                if (rs.next()) {
                    tableCount = rs.getInt("count");
                }
                
                stats.put(shardId, new ShardStats(
                    shardId,
                    shard.getHost(),
                    tableCount,
                    System.currentTimeMillis() - shard.getCreatedTime()
                ));
                
                rs.close();
                stmt.close();
            } catch (SQLException e) {
                stats.put(shardId, new ShardStats(shardId, shard.getHost(), 0, 0));
            }
        }
        
        return stats;
    }
    
    public void shutdown() {
        executor.shutdown();
        scheduler.shutdown();
        
        try {
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
        
        // 关闭所有数据库连接
        for (Shard shard : shards.values()) {
            try {
                shard.getConnection().close();
            } catch (SQLException e) {
                // 记录日志
            }
        }
    }
}

enum ShardHealth {
    HEALTHY, UNHEALTHY, DOWN
}

class ShardStats {
    private final int shardId;
    private final String host;
    private final int tableCount;
    private final long uptime;
    
    public ShardStats(int shardId, String host, int tableCount, long uptime) {
        this.shardId = shardId;
        this.host = host;
        this.tableCount = tableCount;
        this.uptime = uptime;
    }
    
    // Getters
    public int getShardId() { return shardId; }
    public String getHost() { return host; }
    public int getTableCount() { return tableCount; }
    public long getUptime() { return uptime; }
}
```

## 相关资源

### 官方文档
- [MySQL Partitioning](https://dev.mysql.com/doc/refman/8.0/en/partitioning.html)
- [PostgreSQL Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [MongoDB Sharding](https://docs.mongodb.com/manual/sharding/)

### 技术博客
- [Database Sharding at Scale](https://highscalability.com/database-sharding-scale)
- [Sharding at Pinterest](https://medium.com/pinterest-engineering/sharding-at-pinterest-2c2c3b5cd2c7)
- [How Sharding Works](https://www.citusdata.com/blog/2019/07/09/how-sharding-works/)

### 开源项目
- [Vitess](https://vitess.io/) - MySQL数据库分片解决方案
- [Citus](https://www.citusdata.com/) - PostgreSQL扩展，支持分布式查询
- [ShardingSphere](https://shardingsphere.apache.org/) - 分布式数据库中间件

### 学习资源
- [Designing Data-Intensive Applications](https://dataintensive.net/) - Martin Kleppmann
- [Database Systems: The Complete Book](https://www.cs.princeton.edu/courses/archive/fall10/cos597D/)

### 在线课程
- [CMU 15-445/645 Database Systems](https://15445.courses.cs.cmu.edu/fall2020/)
- [Stanford CS346 - Database Systems](https://web.stanford.edu/class/cs346/)

### 社区资源
- [Stack Overflow - Database Sharding](https://stackoverflow.com/questions/tagged/database-sharding)
- [Reddit - r/database](https://www.reddit.com/r/database/)
- [Database Administrators Stack Exchange](https://dba.stackexchange.com/)
