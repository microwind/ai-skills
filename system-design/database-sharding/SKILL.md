---
name: 数据库分片策略
description: "当设计数据库分片时，分析分片算法，优化查询性能，解决数据分布。验证分片架构，设计扩展策略，和最佳实践。"
license: MIT
---

# 数据库分片策略技能

## 概述
数据库分片是将大型数据库水平分割成多个较小数据库的技术，用于解决单机数据库的性能瓶颈和存储限制。合理的分片策略可以显著提高系统的可扩展性和性能，但不当的分片设计会导致数据倾斜、查询复杂度增加等问题。

**核心原则**: 好的分片策略应该均匀分布数据、最小化跨分片查询、支持动态扩容、保证数据一致性。坏的分片会导致热点问题、性能下降、运维困难。

## 何时使用

**始终:**
- 数据量超过单机容量时
- 读写性能达到瓶颈时
- 需要水平扩展时
- 构建高可用系统时
- 优化查询性能时
- 处理大数据量时

**触发短语:**
- "如何设计分片策略？"
- "数据库水平扩展方案"
- "分片键选择原则"
- "跨分片查询优化"
- "分片数据迁移"
- "分片性能调优"

## 数据库分片策略技能功能

### 分片算法
- 哈希分片
- 范围分片
- 目录分片
- 地理位置
- 一致性哈希

### 数据分布
- 均匀分布
- 热点检测
- 负载均衡
- 动态调整
- 数据迁移

### 查询优化
- 分片路由
- 跨分片查询
- 结果合并
- 查询缓存
- 索引优化

### 运维管理
- 分片监控
- 扩容缩容
- 故障恢复
- 数据备份
- 性能调优

## 常见问题

### 数据倾斜问题
- **问题**: 某些分片数据过多
- **原因**: 分片键选择不当，数据分布不均
- **解决**: 重新选择分片键，使用复合分片

### 跨分片查询问题
- **问题**: 查询需要访问多个分片
- **原因**: 数据分布策略不当
- **解决**: 优化分片设计，使用查询路由

### 扩容困难问题
- **问题**: 增加分片困难
- **原因**: 分片算法不支持动态扩容
- **解决**: 使用一致性哈希，设计迁移策略

### 一致性问题
- **问题**: 跨分片事务难以保证
- **原因**: 分布式事务复杂性
- **解决**: 使用最终一致性，设计补偿机制

## 代码示例

### 哈希分片实现
```java
// 哈希分片路由器
@Component
public class HashShardingRouter {
    
    private final List<DataSource> dataSources;
    private final int shardCount;
    private final HashFunction hashFunction;
    
    public HashShardingRouter(List<DataSource> dataSources) {
        this.dataSources = dataSources;
        this.shardCount = dataSources.size();
        this.hashFunction = Hashing.murmur3_32_fixed();
    }
    
    // 根据分片键路由到对应的数据源
    public DataSource routeByShardKey(Object shardKey) {
        int shardIndex = getShardIndex(shardKey);
        return dataSources.get(shardIndex);
    }
    
    // 计算分片索引
    private int getShardIndex(Object shardKey) {
        String keyString = String.valueOf(shardKey);
        int hash = hashFunction.hashString(keyString, StandardCharsets.UTF_8).asInt();
        return Math.abs(hash % shardCount);
    }
    
    // 批量路由
    public Map<DataSource, List<Object>> batchRoute(List<Object> shardKeys) {
        Map<DataSource, List<Object>> routeMap = new HashMap<>();
        
        for (Object shardKey : shardKeys) {
            DataSource targetDataSource = routeByShardKey(shardKey);
            routeMap.computeIfAbsent(targetDataSource, k -> new ArrayList<>()).add(shardKey);
        }
        
        return routeMap;
    }
    
    // 获取所有分片
    public List<DataSource> getAllShards() {
        return new ArrayList<>(dataSources);
    }
    
    // 获取分片数量
    public int getShardCount() {
        return shardCount;
    }
}

// 哈希分片用户服务
@Service
public class HashShardingUserService {
    
    private final HashShardingRouter shardingRouter;
    private final JdbcTemplate jdbcTemplate;
    
    public HashShardingUserService(HashShardingRouter shardingRouter,
                                  JdbcTemplate jdbcTemplate) {
        this.shardingRouter = shardingRouter;
        this.jdbcTemplate = jdbcTemplate;
    }
    
    // 创建用户（根据用户ID分片）
    public User createUser(User user) {
        String userId = generateUserId();
        user.setId(userId);
        
        // 路由到对应分片
        DataSource targetDataSource = shardingRouter.routeByShardKey(userId);
        JdbcTemplate shardJdbcTemplate = new JdbcTemplate(targetDataSource);
        
        // 插入用户数据
        String sql = "INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, ?)";
        shardJdbcTemplate.update(sql, userId, user.getName(), user.getEmail(), new Date());
        
        return user;
    }
    
    // 根据用户ID获取用户
    public User getUserById(String userId) {
        // 路由到对应分片
        DataSource targetDataSource = shardingRouter.routeByShardKey(userId);
        JdbcTemplate shardJdbcTemplate = new JdbcTemplate(targetDataSource);
        
        // 查询用户数据
        String sql = "SELECT id, name, email, created_at FROM users WHERE id = ?";
        return shardJdbcTemplate.queryForObject(sql, new Object[]{userId}, new UserRowMapper());
    }
    
    // 更新用户
    public void updateUser(User user) {
        // 路由到对应分片
        DataSource targetDataSource = shardingRouter.routeByShardKey(user.getId());
        JdbcTemplate shardJdbcTemplate = new JdbcTemplate(targetDataSource);
        
        // 更新用户数据
        String sql = "UPDATE users SET name = ?, email = ? WHERE id = ?";
        shardJdbcTemplate.update(sql, user.getName(), user.getEmail(), user.getId());
    }
    
    // 删除用户
    public void deleteUser(String userId) {
        // 路由到对应分片
        DataSource targetDataSource = shardingRouter.routeByShardKey(userId);
        JdbcTemplate shardJdbcTemplate = new JdbcTemplate(targetDataSource);
        
        // 删除用户数据
        String sql = "DELETE FROM users WHERE id = ?";
        shardJdbcTemplate.update(sql, userId);
    }
    
    // 批量获取用户（跨分片查询）
    public Map<String, User> getUsersByIds(List<String> userIds) {
        // 按分片分组
        Map<DataSource, List<String>> shardGroups = shardingRouter.batchRoute(userIds);
        Map<String, User> result = new HashMap<>();
        
        // 并行查询各个分片
        List<CompletableFuture<Map<String, User>>> futures = shardGroups.entrySet().stream()
            .map(entry -> CompletableFuture.supplyAsync(() -> {
                DataSource dataSource = entry.getKey();
                List<String> shardUserIds = entry.getValue();
                JdbcTemplate shardJdbcTemplate = new JdbcTemplate(dataSource);
                
                return queryUsersFromShard(shardJdbcTemplate, shardUserIds);
            }))
            .collect(Collectors.toList());
        
        // 合并结果
        for (CompletableFuture<Map<String, User>> future : futures) {
            try {
                Map<String, User> shardResult = future.get();
                result.putAll(shardResult);
            } catch (Exception e) {
                log.error("Failed to query users from shard", e);
            }
        }
        
        return result;
    }
    
    // 从单个分片查询用户
    private Map<String, User> queryUsersFromShard(JdbcTemplate shardJdbcTemplate, List<String> userIds) {
        if (userIds.isEmpty()) {
            return Collections.emptyMap();
        }
        
        String sql = String.format("SELECT id, name, email, created_at FROM users WHERE id IN (%s)",
            userIds.stream().map(id -> "?").collect(Collectors.joining(",")));
        
        List<User> users = shardJdbcTemplate.query(sql, userIds.toArray(), new UserRowMapper());
        
        return users.stream().collect(Collectors.toMap(User::getId, user -> user));
    }
    
    private String generateUserId() {
        return UUID.randomUUID().toString();
    }
}

// 用户行映射器
public class UserRowMapper implements RowMapper<User> {
    
    @Override
    public User mapRow(ResultSet rs, int rowNum) throws SQLException {
        User user = new User();
        user.setId(rs.getString("id"));
        user.setName(rs.getString("name"));
        user.setEmail(rs.getString("email"));
        user.setCreatedAt(rs.getTimestamp("created_at"));
        return user;
    }
}
```

### 范围分片实现
```java
// 范围分片配置
@Configuration
public class RangeShardingConfig {
    
    @Bean
    public RangeShardingRule rangeShardingRule() {
        List<RangeShard> shards = Arrays.asList(
            new RangeShard(0, 999999, "shard_0"),
            new RangeShard(1000000, 1999999, "shard_1"),
            new RangeShard(2000000, 2999999, "shard_2"),
            new RangeShard(3000000, 3999999, "shard_3"),
            new RangeShard(4000000, Long.MAX_VALUE, "shard_4")
        );
        
        return new RangeShardingRule(shards);
    }
    
    @Bean
    public Map<String, DataSource> shardDataSources() {
        Map<String, DataSource> dataSources = new HashMap<>();
        
        // 配置各个分片的数据源
        for (int i = 0; i < 5; i++) {
            DataSource dataSource = createDataSource("shard_" + i);
            dataSources.put("shard_" + i, dataSource);
        }
        
        return dataSources;
    }
    
    private DataSource createDataSource(String shardName) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:mysql://localhost:3306/" + shardName);
        config.setUsername("root");
        config.setPassword("password");
        config.setMaximumPoolSize(10);
        
        return new HikariDataSource(config);
    }
}

// 范围分片路由器
@Component
public class RangeShardingRouter {
    
    private final RangeShardingRule shardingRule;
    private final Map<String, DataSource> dataSources;
    
    public RangeShardingRouter(RangeShardingRule shardingRule,
                               Map<String, DataSource> dataSources) {
        this.shardingRule = shardingRule;
        this.dataSources = dataSources;
    }
    
    // 根据分片键路由
    public DataSource routeByShardKey(Long shardKey) {
        String shardName = shardingRule.findShard(shardKey);
        return dataSources.get(shardName);
    }
    
    // 范围查询路由
    public List<DataSource> routeByRange(Long startKey, Long endKey) {
        Set<String> shardNames = shardingRule.findShardsInRange(startKey, endKey);
        return shardNames.stream()
            .map(dataSources::get)
            .filter(Objects::nonNull)
            .collect(Collectors.toList());
    }
    
    // 获取所有分片
    public List<DataSource> getAllShards() {
        return new ArrayList<>(dataSources.values());
    }
}

// 范围分片订单服务
@Service
public class RangeShardingOrderService {
    
    private final RangeShardingRouter shardingRouter;
    private final AtomicLong orderIdGenerator = new AtomicLong(1);
    
    public RangeShardingOrderService(RangeShardingRouter shardingRouter) {
        this.shardingRouter = shardingRouter;
    }
    
    // 创建订单
    public Order createOrder(Order order) {
        Long orderId = orderIdGenerator.getAndIncrement();
        order.setId(orderId);
        
        // 路由到对应分片
        DataSource targetDataSource = shardingRouter.routeByShardKey(orderId);
        JdbcTemplate shardJdbcTemplate = new JdbcTemplate(targetDataSource);
        
        // 插入订单数据
        String sql = "INSERT INTO orders (id, user_id, amount, status, created_at) VALUES (?, ?, ?, ?, ?)";
        shardJdbcTemplate.update(sql, orderId, order.getUserId(), 
            order.getAmount(), order.getStatus(), new Date());
        
        return order;
    }
    
    // 根据订单ID获取订单
    public Order getOrderById(Long orderId) {
        // 路由到对应分片
        DataSource targetDataSource = shardingRouter.routeByShardKey(orderId);
        JdbcTemplate shardJdbcTemplate = new JdbcTemplate(targetDataSource);
        
        // 查询订单数据
        String sql = "SELECT id, user_id, amount, status, created_at FROM orders WHERE id = ?";
        return shardJdbcTemplate.queryForObject(sql, new Object[]{orderId}, new OrderRowMapper());
    }
    
    // 范围查询订单
    public List<Order> getOrdersByIdRange(Long startId, Long endId) {
        // 确定需要查询的分片
        List<DataSource> targetShards = shardingRouter.routeByRange(startId, endId);
        
        List<Order> allOrders = new ArrayList<>();
        
        // 并行查询各个分片
        List<CompletableFuture<List<Order>>> futures = targetShards.stream()
            .map(dataSource -> CompletableFuture.supplyAsync(() -> {
                JdbcTemplate shardJdbcTemplate = new JdbcTemplate(dataSource);
                return queryOrdersFromShard(shardJdbcTemplate, startId, endId);
            }))
            .collect(Collectors.toList());
        
        // 合并结果
        for (CompletableFuture<List<Order>> future : futures) {
            try {
                List<Order> shardOrders = future.get();
                allOrders.addAll(shardOrders);
            } catch (Exception e) {
                log.error("Failed to query orders from shard", e);
            }
        }
        
        // 按订单ID排序
        return allOrders.stream()
            .sorted(Comparator.comparing(Order::getId))
            .collect(Collectors.toList());
    }
    
    // 从单个分片查询订单
    private List<Order> queryOrdersFromShard(JdbcTemplate shardJdbcTemplate, Long startId, Long endId) {
        String sql = "SELECT id, user_id, amount, status, created_at FROM orders WHERE id BETWEEN ? AND ? ORDER BY id";
        
        return shardJdbcTemplate.query(sql, new Object[]{startId, endId}, new OrderRowMapper());
    }
    
    // 根据用户ID查询订单（跨分片查询）
    public List<Order> getOrdersByUserId(String userId) {
        List<Order> allOrders = new ArrayList<>();
        
        // 查询所有分片
        List<DataSource> allShards = shardingRouter.getAllShards();
        
        List<CompletableFuture<List<Order>>> futures = allShards.stream()
            .map(dataSource -> CompletableFuture.supplyAsync(() -> {
                JdbcTemplate shardJdbcTemplate = new JdbcTemplate(dataSource);
                return queryOrdersByUserIdFromShard(shardJdbcTemplate, userId);
            }))
            .collect(Collectors.toList());
        
        // 合并结果
        for (CompletableFuture<List<Order>> future : futures) {
            try {
                List<Order> shardOrders = future.get();
                allOrders.addAll(shardOrders);
            } catch (Exception e) {
                log.error("Failed to query orders by user ID from shard", e);
            }
        }
        
        // 按创建时间排序
        return allOrders.stream()
            .sorted(Comparator.comparing(Order::getCreatedAt).reversed())
            .collect(Collectors.toList());
    }
    
    // 从单个分片根据用户ID查询订单
    private List<Order> queryOrdersByUserIdFromShard(JdbcTemplate shardJdbcTemplate, String userId) {
        String sql = "SELECT id, user_id, amount, status, created_at FROM orders WHERE user_id = ? ORDER BY created_at DESC";
        
        return shardJdbcTemplate.query(sql, new Object[]{userId}, new OrderRowMapper());
    }
}

// 范围分片规则
public class RangeShardingRule {
    
    private final List<RangeShard> shards;
    private final NavigableMap<Long, String> rangeMap = new TreeMap<>();
    
    public RangeShardingRule(List<RangeShard> shards) {
        this.shards = new ArrayList<>(shards);
        
        // 构建范围映射
        for (RangeShard shard : shards) {
            rangeMap.put(shard.getStartRange(), shard.getShardName());
        }
    }
    
    // 查找分片
    public String findShard(Long shardKey) {
        Map.Entry<Long, String> entry = rangeMap.floorEntry(shardKey);
        if (entry == null) {
            throw new IllegalArgumentException("Shard key is out of range: " + shardKey);
        }
        
        // 验证是否在范围内
        int index = shards.indexOf(new RangeShard(entry.getKey(), 0L, entry.getValue()));
        RangeShard shard = shards.get(index);
        
        if (shardKey < shard.getStartRange() || shardKey > shard.getEndRange()) {
            throw new IllegalArgumentException("Shard key is out of range: " + shardKey);
        }
        
        return shard.getShardName();
    }
    
    // 查找范围内的所有分片
    public Set<String> findShardsInRange(Long startKey, Long endKey) {
        Set<String> shardNames = new HashSet<>();
        
        for (RangeShard shard : shards) {
            if (shard.intersects(startKey, endKey)) {
                shardNames.add(shard.getShardName());
            }
        }
        
        return shardNames;
    }
    
    // 获取所有分片信息
    public List<RangeShard> getAllShards() {
        return new ArrayList<>(shards);
    }
}

// 范围分片定义
public class RangeShard {
    
    private final Long startRange;
    private final Long endRange;
    private final String shardName;
    
    public RangeShard(Long startRange, Long endRange, String shardName) {
        this.startRange = startRange;
        this.endRange = endRange;
        this.shardName = shardName;
    }
    
    public boolean intersects(Long start, Long end) {
        return !(end < startRange || start > endRange);
    }
    
    public boolean contains(Long value) {
        return value >= startRange && value <= endRange;
    }
    
    // Getters
    public Long getStartRange() { return startRange; }
    public Long getEndRange() { return endRange; }
    public String getShardName() { return shardName; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RangeShard that = (RangeShard) o;
        return Objects.equals(shardName, that.shardName);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(shardName);
    }
}
```

### 一致性哈希分片实现
```java
// 一致性哈希环
@Component
public class ConsistentHashRing {
    
    private final SortedMap<Integer, String> ring = new TreeMap<>();
    private final int virtualNodes;
    private final MessageDigest md5;
    
    public ConsistentHashRing(int virtualNodes) {
        this.virtualNodes = virtualNodes;
        try {
            this.md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not available", e);
        }
    }
    
    // 添加节点
    public void addNode(String nodeName) {
        for (int i = 0; i < virtualNodes; i++) {
            String virtualNodeName = nodeName + "#" + i;
            int hash = hash(virtualNodeName);
            ring.put(hash, nodeName);
        }
    }
    
    // 移除节点
    public void removeNode(String nodeName) {
        for (int i = 0; i < virtualNodes; i++) {
            String virtualNodeName = nodeName + "#" + i;
            int hash = hash(virtualNodeName);
            ring.remove(hash);
        }
    }
    
    // 获取目标节点
    public String getNode(String key) {
        if (ring.isEmpty()) {
            return null;
        }
        
        int hash = hash(key);
        
        // 顺时针查找第一个节点
        SortedMap<Integer, String> tailMap = ring.tailMap(hash);
        
        if (!tailMap.isEmpty()) {
            return tailMap.get(tailMap.firstKey());
        } else {
            // 环形结构，返回第一个节点
            return ring.get(ring.firstKey());
        }
    }
    
    // 获取多个节点（用于复制）
    public List<String> getNodes(String key, int count) {
        List<String> nodes = new ArrayList<>();
        String currentNode = getNode(key);
        
        // 添加起始节点
        nodes.add(currentNode);
        
        // 顺时针查找其他节点
        int hash = hash(key);
        SortedMap<Integer, String> tailMap = ring.tailMap(hash);
        Iterator<String> iterator = tailMap.values().iterator();
        
        while (iterator.hasNext() && nodes.size() < count) {
            String node = iterator.next();
            if (!nodes.contains(node)) {
                nodes.add(node);
            }
        }
        
        // 如果不够，从头开始继续查找
        if (nodes.size() < count) {
            Iterator<String> headIterator = ring.values().iterator();
            while (headIterator.hasNext() && nodes.size() < count) {
                String node = headIterator.next();
                if (!nodes.contains(node)) {
                    nodes.add(node);
                }
            }
        }
        
        return nodes;
    }
    
    // 获取所有节点
    public Set<String> getAllNodes() {
        return new HashSet<>(ring.values());
    }
    
    // MD5哈希
    private int hash(String key) {
        md5.reset();
        md5.update(key.getBytes(StandardCharsets.UTF_8));
        byte[] digest = md5.digest();
        
        int hash = ((int) digest[0] & 0xFF) << 24;
        hash |= ((int) digest[1] & 0xFF) << 16;
        hash |= ((int) digest[2] & 0xFF) << 8;
        hash |= (int) digest[3] & 0xFF;
        
        return hash & 0x7FFFFFFF; // 确保为正数
    }
}

// 一致性哈希分片路由器
@Component
public class ConsistentHashShardingRouter {
    
    private final ConsistentHashRing hashRing;
    private final Map<String, DataSource> dataSources;
    private final int replicaCount;
    
    public ConsistentHashShardingRouter(ConsistentHashRing hashRing,
                                       Map<String, DataSource> dataSources,
                                       @Value("${sharding.replica.count:3}") int replicaCount) {
        this.hashRing = hashRing;
        this.dataSources = dataSources;
        this.replicaCount = replicaCount;
        
        // 初始化哈希环
        initializeHashRing();
    }
    
    private void initializeHashRing() {
        for (String nodeName : dataSources.keySet()) {
            hashRing.addNode(nodeName);
        }
    }
    
    // 获取主分片
    public DataSource getPrimaryShard(String key) {
        String nodeName = hashRing.getNode(key);
        return dataSources.get(nodeName);
    }
    
    // 获取所有副本分片
    public List<DataSource> getReplicaShards(String key) {
        List<String> nodeNames = hashRing.getNodes(key, replicaCount);
        return nodeNames.stream()
            .map(dataSources::get)
            .filter(Objects::nonNull)
            .collect(Collectors.toList());
    }
    
    // 添加新分片
    public void addShard(String nodeName, DataSource dataSource) {
        dataSources.put(nodeName, dataSource);
        hashRing.addNode(nodeName);
        
        // 触发数据迁移
        triggerDataMigration(nodeName);
    }
    
    // 移除分片
    public void removeShard(String nodeName) {
        hashRing.removeNode(nodeName);
        dataSources.remove(nodeName);
        
        // 触发数据迁移
        triggerDataMigration(nodeName);
    }
    
    // 数据迁移
    private void triggerDataMigration(String nodeName) {
        // 实现数据迁移逻辑
        log.info("Triggering data migration for node: {}", nodeName);
    }
    
    // 获取所有分片
    public List<DataSource> getAllShards() {
        return new ArrayList<>(dataSources.values());
    }
    
    // 获取分片统计信息
    public Map<String, Integer> getShardStatistics() {
        Map<String, Integer> stats = new HashMap<>();
        
        // 这里可以统计每个分片的数据量
        // 实际实现中需要查询各个分片的数据量
        
        return stats;
    }
}

// 一致性哈希分片服务
@Service
public class ConsistentHashShardingService {
    
    private final ConsistentHashShardingRouter shardingRouter;
    private final DataMigrationService migrationService;
    
    public ConsistentHashShardingService(ConsistentHashShardingRouter shardingRouter,
                                        DataMigrationService migrationService) {
        this.shardingRouter = shardingRouter;
        this.migrationService = migrationService;
    }
    
    // 写入数据（主分片）
    public void writeData(String key, Object data) {
        DataSource primaryShard = shardingRouter.getPrimaryShard(key);
        JdbcTemplate jdbcTemplate = new JdbcTemplate(primaryShard);
        
        // 写入主分片
        String sql = "INSERT INTO data (key, value, created_at) VALUES (?, ?, ?)";
        jdbcTemplate.update(sql, key, serialize(data), new Date());
    }
    
    // 读取数据（主分片）
    public Object readData(String key) {
        DataSource primaryShard = shardingRouter.getPrimaryShard(key);
        JdbcTemplate jdbcTemplate = new JdbcTemplate(primaryShard);
        
        // 从主分片读取
        String sql = "SELECT value FROM data WHERE key = ?";
        String serializedData = jdbcTemplate.queryForObject(sql, new Object[]{key}, String.class);
        
        return deserialize(serializedData);
    }
    
    // 写入数据（多副本）
    public void writeDataWithReplication(String key, Object data) {
        List<DataSource> replicaShards = shardingRouter.getReplicaShards(key);
        
        // 并行写入所有副本
        List<CompletableFuture<Void>> futures = replicaShards.stream()
            .map(dataSource -> CompletableFuture.runAsync(() -> {
                JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
                String sql = "INSERT INTO data (key, value, created_at) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE value = ?";
                jdbcTemplate.update(sql, key, serialize(data), new Date(), serialize(data));
            }))
            .collect(Collectors.toList());
        
        // 等待所有写入完成
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
    }
    
    // 读取数据（任一副本）
    public Object readDataFromAnyReplica(String key) {
        List<DataSource> replicaShards = shardingRouter.getReplicaShards(key);
        
        // 并行读取所有副本，返回第一个成功的结果
        List<CompletableFuture<Object>> futures = replicaShards.stream()
            .map(dataSource -> CompletableFuture.supplyAsync(() -> {
                try {
                    JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
                    String sql = "SELECT value FROM data WHERE key = ?";
                    String serializedData = jdbcTemplate.queryForObject(sql, new Object[]{key}, String.class);
                    return deserialize(serializedData);
                } catch (Exception e) {
                    log.warn("Failed to read from replica", e);
                    return null;
                }
            }))
            .collect(Collectors.toList());
        
        // 等待第一个成功的结果
        for (CompletableFuture<Object> future : futures) {
            try {
                Object result = future.get(1, TimeUnit.SECONDS);
                if (result != null) {
                    return result;
                }
            } catch (Exception e) {
                // 继续尝试下一个副本
            }
        }
        
        throw new RuntimeException("Failed to read data from all replicas");
    }
    
    // 添加新分片
    public void addNewShard(String nodeName, DataSource dataSource) {
        shardingRouter.addShard(nodeName, dataSource);
        
        // 触发数据重分布
        migrationService.redistributeData();
    }
    
    // 移除分片
    public void removeShard(String nodeName) {
        shardingRouter.removeShard(nodeName);
        
        // 触发数据重分布
        migrationService.redistributeData();
    }
    
    // 序列化数据
    private String serialize(Object data) {
        // 实现序列化逻辑
        return data.toString();
    }
    
    // 反序列化数据
    private Object deserialize(String data) {
        // 实现反序列化逻辑
        return data;
    }
}
```

### 分片监控和管理
```java
// 分片监控服务
@Service
public class ShardingMonitoringService {
    
    private final ConsistentHashShardingRouter shardingRouter;
    private final MeterRegistry meterRegistry;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    public ShardingMonitoringService(ConsistentHashShardingRouter shardingRouter,
                                   MeterRegistry meterRegistry) {
        this.shardingRouter = shardingRouter;
        this.meterRegistry = meterRegistry;
    }
    
    @PostConstruct
    public void startMonitoring() {
        // 定期收集分片统计信息
        scheduler.scheduleAtFixedRate(this::collectShardMetrics, 30, 30, TimeUnit.SECONDS);
    }
    
    // 收集分片指标
    private void collectShardMetrics() {
        List<DataSource> allShards = shardingRouter.getAllShards();
        
        for (int i = 0; i < allShards.size(); i++) {
            DataSource dataSource = allShards.get(i);
            String shardName = "shard_" + i;
            
            try {
                JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
                
                // 收集数据量指标
                long dataCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM data", Long.class);
                meterRegistry.gauge("shard.data.count", Tags.of("shard", shardName), dataCount);
                
                // 收集连接池指标
                if (dataSource instanceof HikariDataSource) {
                    HikariDataSource hikariDataSource = (HikariDataSource) dataSource;
                    HikariPoolMXBean poolBean = hikariDataSource.getHikariPoolMXBean();
                    
                    meterRegistry.gauge("shard.pool.active", Tags.of("shard", shardName), 
                        poolBean.getActiveConnections());
                    meterRegistry.gauge("shard.pool.idle", Tags.of("shard", shardName), 
                        poolBean.getIdleConnections());
                    meterRegistry.gauge("shard.pool.total", Tags.of("shard", shardName), 
                        poolBean.getTotalConnections());
                }
                
                // 收集查询性能指标
                long queryTime = measureQueryPerformance(jdbcTemplate);
                meterRegistry.timer("shard.query.time", Tags.of("shard", shardName))
                    .record(queryTime, TimeUnit.MILLISECONDS);
                
            } catch (Exception e) {
                log.error("Failed to collect metrics for shard: {}", shardName, e);
                meterRegistry.counter("shard.error.count", Tags.of("shard", shardName)).increment();
            }
        }
    }
    
    // 测量查询性能
    private long measureQueryPerformance(JdbcTemplate jdbcTemplate) {
        long startTime = System.currentTimeMillis();
        
        try {
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
        } catch (Exception e) {
            log.warn("Query performance test failed", e);
        }
        
        return System.currentTimeMillis() - startTime;
    }
    
    // 获取分片健康状态
    public Map<String, ShardHealthStatus> getShardHealthStatus() {
        Map<String, ShardHealthStatus> healthStatus = new HashMap<>();
        List<DataSource> allShards = shardingRouter.getAllShards();
        
        for (int i = 0; i < allShards.size(); i++) {
            DataSource dataSource = allShards.get(i);
            String shardName = "shard_" + i;
            
            ShardHealthStatus status = checkShardHealth(dataSource, shardName);
            healthStatus.put(shardName, status);
        }
        
        return healthStatus;
    }
    
    // 检查分片健康状态
    private ShardHealthStatus checkShardHealth(DataSource dataSource, String shardName) {
        try {
            JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
            
            // 测试连接
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            
            // 检查数据量
            long dataCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM data", Long.class);
            
            // 检查最后更新时间
            Timestamp lastUpdate = jdbcTemplate.queryForObject(
                "SELECT MAX(created_at) FROM data", Timestamp.class);
            
            boolean isHealthy = true;
            String message = "OK";
            
            // 检查数据量是否异常
            if (dataCount > 1000000) {
                isHealthy = false;
                message = "Data count too high: " + dataCount;
            }
            
            // 检查是否长时间没有更新
            if (lastUpdate != null) {
                long timeDiff = System.currentTimeMillis() - lastUpdate.getTime();
                if (timeDiff > TimeUnit.HOURS.toMillis(1)) {
                    isHealthy = false;
                    message = "No recent updates";
                }
            }
            
            return new ShardHealthStatus(shardName, isHealthy, message, dataCount, lastUpdate);
            
        } catch (Exception e) {
            return new ShardHealthStatus(shardName, false, "Connection failed: " + e.getMessage(), 0, null);
        }
    }
    
    @PreDestroy
    public void stopMonitoring() {
        scheduler.shutdown();
    }
    
    // 分片健康状态
    public static class ShardHealthStatus {
        private final String shardName;
        private final boolean healthy;
        private final String message;
        private final long dataCount;
        private final Timestamp lastUpdate;
        
        public ShardHealthStatus(String shardName, boolean healthy, String message, 
                               long dataCount, Timestamp lastUpdate) {
            this.shardName = shardName;
            this.healthy = healthy;
            this.message = message;
            this.dataCount = dataCount;
            this.lastUpdate = lastUpdate;
        }
        
        // Getters
        public String getShardName() { return shardName; }
        public boolean isHealthy() { return healthy; }
        public String getMessage() { return message; }
        public long getDataCount() { return dataCount; }
        public Timestamp getLastUpdate() { return lastUpdate; }
    }
}

// 数据迁移服务
@Service
public class DataMigrationService {
    
    private final ConsistentHashShardingRouter shardingRouter;
    private final TaskExecutor taskExecutor;
    
    public DataMigrationService(ConsistentHashShardingRouter shardingRouter,
                               TaskExecutor taskExecutor) {
        this.shardingRouter = shardingRouter;
        this.taskExecutor = taskExecutor;
    }
    
    // 重分布数据
    @Async("taskExecutor")
    public void redistributeData() {
        log.info("Starting data redistribution");
        
        List<DataSource> allShards = shardingRouter.getAllShards();
        
        // 获取所有数据
        List<DataRecord> allData = new ArrayList<>();
        for (DataSource dataSource : allShards) {
            List<DataRecord> shardData = getAllDataFromShard(dataSource);
            allData.addAll(shardData);
        }
        
        // 重新分配数据
        for (DataRecord record : allData) {
            DataSource targetShard = shardingRouter.getPrimaryShard(record.getKey());
            
            // 如果数据不在正确的分片，则移动
            if (!isDataInCorrectShard(record, targetShard)) {
                moveDataToShard(record, targetShard);
            }
        }
        
        log.info("Data redistribution completed");
    }
    
    // 获取分片中的所有数据
    private List<DataRecord> getAllDataFromShard(DataSource dataSource) {
        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
        
        String sql = "SELECT key, value, created_at FROM data";
        return jdbcTemplate.query(sql, (rs, rowNum) -> new DataRecord(
            rs.getString("key"),
            rs.getString("value"),
            rs.getTimestamp("created_at")
        ));
    }
    
    // 检查数据是否在正确的分片
    private boolean isDataInCorrectShard(DataRecord record, DataSource targetShard) {
        // 这里可以通过查询目标分片来验证
        // 简化实现，假设需要移动
        return false;
    }
    
    // 移动数据到目标分片
    private void moveDataToShard(DataRecord record, DataSource targetShard) {
        JdbcTemplate targetJdbcTemplate = new JdbcTemplate(targetShard);
        
        String sql = "INSERT INTO data (key, value, created_at) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE value = ?";
        targetJdbcTemplate.update(sql, record.getKey(), record.getValue(), 
            record.getCreatedAt(), record.getValue());
        
        // 从原分片删除数据
        DataSource originalShard = findOriginalShard(record.getKey());
        if (originalShard != null && originalShard != targetShard) {
            JdbcTemplate originalJdbcTemplate = new JdbcTemplate(originalShard);
            originalJdbcTemplate.update("DELETE FROM data WHERE key = ?", record.getKey());
        }
        
        log.debug("Moved data {} to new shard", record.getKey());
    }
    
    // 查找原始分片
    private DataSource findOriginalShard(String key) {
        List<DataSource> allShards = shardingRouter.getAllShards();
        
        for (DataSource dataSource : allShards) {
            JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
            try {
                Integer count = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM data WHERE key = ?", new Object[]{key}, Integer.class);
                if (count > 0) {
                    return dataSource;
                }
            } catch (Exception e) {
                // 继续查找下一个分片
            }
        }
        
        return null;
    }
    
    // 数据记录
    public static class DataRecord {
        private final String key;
        private final String value;
        private final Timestamp createdAt;
        
        public DataRecord(String key, String value, Timestamp createdAt) {
            this.key = key;
            this.value = value;
            this.createdAt = createdAt;
        }
        
        // Getters
        public String getKey() { return key; }
        public String getValue() { return value; }
        public Timestamp getCreatedAt() { return createdAt; }
    }
}
```

## 最佳实践

### 分片策略选择
1. **均匀分布**: 使用哈希分片确保数据均匀分布
2. **查询优化**: 根据查询模式选择合适的分片策略
3. **扩展性**: 选择支持动态扩容的分片算法
4. **一致性**: 考虑数据一致性和事务需求

### 分片键设计
1. **高基数**: 选择高基数的字段作为分片键
2. **均匀分布**: 确保分片键值均匀分布
3. **查询友好**: 分片键应该支持常见查询
4. **稳定性**: 分片键不应该频繁变更

### 性能优化
1. **连接池**: 为每个分片配置合适的连接池
2. **批量操作**: 使用批量操作减少网络开销
3. **并行查询**: 并行查询多个分片提高性能
4. **缓存策略**: 合理使用缓存减少分片查询

### 运维管理
1. **监控告警**: 监控各个分片的性能和健康状态
2. **数据迁移**: 设计平滑的数据迁移策略
3. **故障恢复**: 实现分片故障的自动恢复
4. **容量规划**: 提前规划分片扩容策略

## 相关技能

- **cap-theorem** - CAP定理应用
- **distributed-consistency** - 分布式一致性
- **cache-invalidation** - 缓存失效
- **high-concurrency** - 高并发系统设计
- **algorithm-advisor** - 算法顾问
