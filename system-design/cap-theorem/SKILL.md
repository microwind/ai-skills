---
name: CAP定理应用
description: "当应用CAP定理时，分析一致性模型，优化可用性保证，解决分区容错。验证系统架构，设计权衡策略，和最佳实践。"
license: MIT
---

# CAP定理应用技能

## 概述
CAP定理是分布式系统设计的核心理论，指出分布式系统最多只能同时满足一致性（Consistency）、可用性（Availability）、分区容错性（Partition tolerance）中的两个特性。理解CAP定理有助于在系统设计中做出正确的权衡决策。

**核心原则**: 在分布式系统中，网络分区是必然发生的，必须在一致性和可用性之间做出选择。没有完美的解决方案，只有适合特定场景的权衡。

## 何时使用

**始终:**
- 设计分布式系统时
- 选择数据库系统时
- 设计微服务架构时
- 处理分布式事务时
- 评估系统可靠性时
- 制定故障恢复策略时

**触发短语:**
- "如何选择CAP策略？"
- "一致性vs可用性权衡"
- "分布式系统设计原则"
- "数据库选型标准"
- "微服务架构权衡"
- "分区容错处理"

## CAP定理应用技能功能

### 一致性模型
- 强一致性
- 最终一致性
- 因果一致性
- 会话一致性
- 单调一致性

### 可用性保证
- 高可用设计
- 故障转移
- 降级策略
- 熔断机制
- 负载均衡

### 分区容错
- 网络分区处理
- 数据复制
- 分片策略
- 故障检测
- 恢复机制

### 权衡策略
- CP系统设计
- AP系统设计
- CA系统限制
- 混合策略
- 场景适配

## 常见问题

### 一致性问题
- **问题**: 数据不一致导致业务错误
- **原因**: 分布式环境下数据同步延迟
- **解决**: 选择合适的一致性模型，实现补偿机制

- **问题**: 强一致性影响系统性能
- **原因**: 过于严格的一致性要求
- **解决**: 根据业务需求选择适当的一致性级别

### 可用性问题
- **问题**: 系统故障导致服务不可用
- **原因**: 缺乏高可用设计
- **解决**: 实现冗余部署，故障自动转移

- **问题**: 过度设计增加复杂性
- **原因**: 不必要的可用性保证
- **解决**: 根据业务重要性合理设计

### 分区容错问题
- **问题**: 网络分区导致数据分裂
- **原因**: 缺乏分区处理机制
- **解决**: 实现分区检测和恢复策略

## 代码示例

### CP系统实现（一致性优先）
```java
// CP配置服务（一致性优先）
@Service
public class CPConfigurationService {
    
    private final List<ConfigNode> configNodes;
    private final ConsensusAlgorithm consensus;
    private final ConfigStorage storage;
    
    public CPConfigurationService(List<ConfigNode> configNodes,
                                ConsensusAlgorithm consensus,
                                ConfigStorage storage) {
        this.configNodes = configNodes;
        this.consensus = consensus;
        this.storage = storage;
    }
    
    // 获取配置（强一致性）
    public Config getConfig(String key) throws ConsensusException {
        // 通过共识算法获取最新配置
        ConfigValue value = consensus.get(key);
        if (value == null) {
            throw new ConfigNotFoundException("Config not found: " + key);
        }
        
        return new Config(key, value.getValue(), value.getVersion());
    }
    
    // 更新配置（需要共识）
    @Transactional
    public void updateConfig(String key, String value) throws ConsensusException {
        // 1. 通过共识算法达成一致
        ConfigValue newValue = new ConfigValue(key, value, System.currentTimeMillis());
        consensus.propose(newValue);
        
        // 2. 等待大多数节点确认
        if (!consensus.waitForQuorum(Duration.ofSeconds(5))) {
            throw new ConsensusException("Failed to achieve consensus");
        }
        
        // 3. 提交到存储
        storage.store(key, newValue);
    }
    
    // 删除配置（需要共识）
    @Transactional
    public void deleteConfig(String key) throws ConsensusException {
        // 1. 通过共识算法达成一致
        consensus.proposeDelete(key);
        
        // 2. 等待大多数节点确认
        if (!consensus.waitForQuorum(Duration.ofSeconds(5))) {
            throw new ConsensusException("Failed to achieve consensus");
        }
        
        // 3. 从存储删除
        storage.delete(key);
    }
    
    // 批量更新（原子操作）
    @Transactional
    public void batchUpdateConfigs(Map<String, String> configs) throws ConsensusException {
        // 1. 创建批量操作
        BatchOperation batch = new BatchOperation();
        configs.forEach((key, value) -> {
            ConfigValue configValue = new ConfigValue(key, value, System.currentTimeMillis());
            batch.addUpdate(configValue);
        });
        
        // 2. 通过共识算法达成一致
        consensus.proposeBatch(batch);
        
        // 3. 等待大多数节点确认
        if (!consensus.waitForQuorum(Duration.ofSeconds(10))) {
            throw new ConsensusException("Failed to achieve consensus for batch operation");
        }
        
        // 4. 提交到存储
        storage.batchStore(configs);
    }
}

// 共识算法实现（Raft）
@Component
public class RaftConsensus implements ConsensusAlgorithm {
    
    private final RaftNode raftNode;
    private final Map<String, ConfigValue> configCache = new ConcurrentHashMap<>();
    
    public RaftConsensus(RaftNode raftNode) {
        this.raftNode = raftNode;
    }
    
    @Override
    public ConfigValue get(String key) {
        // 从本地缓存获取
        ConfigValue cached = configCache.get(key);
        if (cached != null) {
            return cached;
        }
        
        // 从Raft状态机获取
        try {
            ConfigValue value = raftNode.getStateMachine().get(key);
            if (value != null) {
                configCache.put(key, value);
            }
            return value;
        } catch (RaftException e) {
            throw new ConsensusException("Failed to get config from Raft", e);
        }
    }
    
    @Override
    public void propose(ConfigValue configValue) throws ConsensusException {
        try {
            // 提交到Raft日志
            CompletableFuture<Boolean> future = raftNode.propose(configValue);
            
            // 等待提案被应用
            Boolean result = future.get(5, TimeUnit.SECONDS);
            if (!result) {
                throw new ConsensusException("Proposal rejected by Raft");
            }
            
            // 更新本地缓存
            configCache.put(configValue.getKey(), configValue);
            
        } catch (Exception e) {
            throw new ConsensusException("Failed to propose config to Raft", e);
        }
    }
    
    @Override
    public void proposeDelete(String key) throws ConsensusException {
        try {
            // 提交删除操作到Raft日志
            DeleteOperation deleteOp = new DeleteOperation(key);
            CompletableFuture<Boolean> future = raftNode.propose(deleteOp);
            
            // 等待提案被应用
            Boolean result = future.get(5, TimeUnit.SECONDS);
            if (!result) {
                throw new ConsensusException("Delete proposal rejected by Raft");
            }
            
            // 从本地缓存删除
            configCache.remove(key);
            
        } catch (Exception e) {
            throw new ConsensusException("Failed to propose delete to Raft", e);
        }
    }
    
    @Override
    public void proposeBatch(BatchOperation batch) throws ConsensusException {
        try {
            // 提交批量操作到Raft日志
            CompletableFuture<Boolean> future = raftNode.propose(batch);
            
            // 等待提案被应用
            Boolean result = future.get(10, TimeUnit.SECONDS);
            if (!result) {
                throw new ConsensusException("Batch proposal rejected by Raft");
            }
            
            // 更新本地缓存
            for (ConfigValue configValue : batch.getUpdates()) {
                configCache.put(configValue.getKey(), configValue);
            }
            
        } catch (Exception e) {
            throw new ConsensusException("Failed to propose batch to Raft", e);
        }
    }
    
    @Override
    public boolean waitForQuorum(Duration timeout) {
        try {
            // 等待Raft提交索引更新
            return raftNode.waitForCommitIndex(timeout);
        } catch (Exception e) {
            return false;
        }
    }
}
```

### AP系统实现（可用性优先）
```java
// AP用户服务（可用性优先）
@Service
public class APUserService {
    
    private final List<UserDataStore> dataStores;
    private final ConflictResolver conflictResolver;
    private final EventPublisher eventPublisher;
    
    public APUserService(List<UserDataStore> dataStores,
                        ConflictResolver conflictResolver,
                        EventPublisher eventPublisher) {
        this.dataStores = dataStores;
        this.conflictResolver = conflictResolver;
        this.eventPublisher = eventPublisher;
    }
    
    // 获取用户（最终一致性）
    public User getUser(String userId) {
        // 尝试从本地数据存储获取
        for (UserDataStore store : dataStores) {
            try {
                User user = store.getUser(userId);
                if (user != null) {
                    return user;
                }
            } catch (Exception e) {
                // 忽略单个存储的故障，继续尝试其他存储
                log.warn("Failed to get user from store: {}", store.getClass().getSimpleName(), e);
            }
        }
        
        // 如果所有存储都失败，返回null而不是抛出异常
        return null;
    }
    
    // 创建用户（写入多个存储）
    public User createUser(User user) {
        User createdUser = user.withId(UUID.randomUUID().toString());
        UserVersioned versionedUser = new UserVersioned(createdUser, System.currentTimeMillis());
        
        // 并行写入多个存储
        List<CompletableFuture<Boolean>> futures = dataStores.stream()
            .map(store -> CompletableFuture.supplyAsync(() -> {
                try {
                    return store.createUser(versionedUser);
                } catch (Exception e) {
                    log.error("Failed to create user in store: {}", store.getClass().getSimpleName(), e);
                    return false;
                }
            }))
            .collect(Collectors.toList());
        
        // 等待至少一个存储成功
        try {
            CompletableFuture.anyOf(futures.toArray(new CompletableFuture[0]))
                .get(1, TimeUnit.SECONDS);
        } catch (Exception e) {
            // 即使超时也继续，因为至少有一个存储可能成功
            log.warn("Timeout waiting for user creation, but some stores may have succeeded");
        }
        
        // 发布用户创建事件
        eventPublisher.publishEvent(new UserCreatedEvent(createdUser));
        
        return createdUser;
    }
    
    // 更新用户（最终一致性）
    public User updateUser(String userId, UserUpdate update) {
        UserVersioned currentUser = getLatestUserVersion(userId);
        if (currentUser == null) {
            throw new UserNotFoundException("User not found: " + userId);
        }
        
        UserVersioned updatedUser = currentUser.withUpdate(update);
        
        // 并行更新多个存储
        List<CompletableFuture<Boolean>> futures = dataStores.stream()
            .map(store -> CompletableFuture.supplyAsync(() -> {
                try {
                    return store.updateUser(updatedUser);
                } catch (Exception e) {
                    log.error("Failed to update user in store: {}", store.getClass().getSimpleName(), e);
                    return false;
                }
            }))
            .collect(Collectors.toList());
        
        // 不等待所有存储完成，确保高可用性
        eventPublisher.publishEvent(new UserUpdatedEvent(updatedUser.getUser()));
        
        return updatedUser.getUser();
    }
    
    // 删除用户（最终一致性）
    public void deleteUser(String userId) {
        UserVersioned currentUser = getLatestUserVersion(userId);
        if (currentUser == null) {
            return; // 用户不存在，直接返回
        }
        
        // 并行删除多个存储
        List<CompletableFuture<Boolean>> futures = dataStores.stream()
            .map(store -> CompletableFuture.supplyAsync(() -> {
                try {
                    return store.deleteUser(userId);
                } catch (Exception e) {
                    log.error("Failed to delete user in store: {}", store.getClass().getSimpleName(), e);
                    return false;
                }
            }))
            .collect(Collectors.toList());
        
        // 发布用户删除事件
        eventPublisher.publishEvent(new UserDeletedEvent(userId));
    }
    
    // 获取最新用户版本（解决冲突）
    private UserVersioned getLatestUserVersion(String userId) {
        List<UserVersioned> versions = new ArrayList<>();
        
        // 从所有存储收集版本
        for (UserDataStore store : dataStores) {
            try {
                UserVersioned version = store.getUserVersion(userId);
                if (version != null) {
                    versions.add(version);
                }
            } catch (Exception e) {
                log.warn("Failed to get user version from store: {}", store.getClass().getSimpleName(), e);
            }
        }
        
        if (versions.isEmpty()) {
            return null;
        }
        
        // 使用冲突解决器选择最佳版本
        return conflictResolver.resolveConflict(versions);
    }
}

// 冲突解决器
@Component
public class ConflictResolver {
    
    // 基于时间戳的冲突解决
    public UserVersioned resolveConflict(List<UserVersioned> versions) {
        if (versions.size() == 1) {
            return versions.get(0);
        }
        
        // 选择最新时间戳的版本
        return versions.stream()
            .max(Comparator.comparing(UserVersioned::getTimestamp))
            .orElse(versions.get(0));
    }
    
    // 基于向量时钟的冲突解决
    public UserVersioned resolveConflictWithVectorClock(List<UserVersioned> versions) {
        if (versions.size() == 1) {
            return versions.get(0);
        }
        
        // 找到没有冲突的版本或合并版本
        UserVersioned merged = versions.get(0);
        for (int i = 1; i < versions.size(); i++) {
            merged = mergeVersions(merged, versions.get(i));
        }
        
        return merged;
    }
    
    private UserVersioned mergeVersions(UserVersioned v1, UserVersioned v2) {
        // 简单的合并策略：保留最新的字段值
        User mergedUser = v1.getUser();
        User user2 = v2.getUser();
        
        User.Builder builder = User.builder()
            .id(mergedUser.getId())
            .name(getNewerValue(mergedUser.getName(), user2.getName(), v1.getTimestamp(), v2.getTimestamp()))
            .email(getNewerValue(mergedUser.getEmail(), user2.getEmail(), v1.getTimestamp(), v2.getTimestamp()))
            .age(getNewerValue(mergedUser.getAge(), user2.getAge(), v1.getTimestamp(), v2.getTimestamp()));
        
        return new UserVersioned(builder.build(), Math.max(v1.getTimestamp(), v2.getTimestamp()));
    }
    
    private <T> T getNewerValue(T value1, T value2, long timestamp1, long timestamp2) {
        return timestamp1 > timestamp2 ? value1 : value2;
    }
}
```

### 混合CAP策略实现
```java
// 混合CAP配置管理器
@Service
public class HybridCAPConfigManager {
    
    private final CPConfigurationService cpService;  // 强一致性配置
    private final APConfigurationService apService;  // 高可用配置
    private final ConfigClassifier classifier;       // 配置分类器
    
    public HybridCAPConfigManager(CPConfigurationService cpService,
                                  APConfigurationService apService,
                                  ConfigClassifier classifier) {
        this.cpService = cpService;
        this.apService = apService;
        this.classifier = classifier;
    }
    
    // 获取配置（根据类型选择策略）
    public Config getConfig(String key) {
        ConfigType type = classifier.classify(key);
        
        switch (type) {
            case CRITICAL:
                // 关键配置使用CP策略
                try {
                    return cpService.getConfig(key);
                } catch (ConsensusException e) {
                    log.error("Failed to get critical config from CP service, falling back to AP", e);
                    return apService.getConfig(key);
                }
            case NON_CRITICAL:
                // 非关键配置使用AP策略
                return apService.getConfig(key);
            default:
                throw new IllegalArgumentException("Unknown config type: " + type);
        }
    }
    
    // 更新配置（根据类型选择策略）
    public void updateConfig(String key, String value) {
        ConfigType type = classifier.classify(key);
        
        switch (type) {
            case CRITICAL:
                // 关键配置使用CP策略
                try {
                    cpService.updateConfig(key, value);
                } catch (ConsensusException e) {
                    log.error("Failed to update critical config, retrying...", e);
                    // 重试机制
                    retryUpdate(key, value, type);
                }
                break;
            case NON_CRITICAL:
                // 非关键配置使用AP策略
                apService.updateConfig(key, value);
                break;
            default:
                throw new IllegalArgumentException("Unknown config type: " + type);
        }
    }
    
    // 批量更新配置
    public void batchUpdateConfigs(Map<String, String> configs) {
        // 分离关键和非关键配置
        Map<String, String> criticalConfigs = new HashMap<>();
        Map<String, String> nonCriticalConfigs = new HashMap<>();
        
        configs.forEach((key, value) -> {
            ConfigType type = classifier.classify(key);
            if (type == ConfigType.CRITICAL) {
                criticalConfigs.put(key, value);
            } else {
                nonCriticalConfigs.put(key, value);
            }
        });
        
        // 并行处理不同类型的配置
        CompletableFuture<Void> cpFuture = CompletableFuture.runAsync(() -> {
            if (!criticalConfigs.isEmpty()) {
                try {
                    cpService.batchUpdateConfigs(criticalConfigs);
                } catch (ConsensusException e) {
                    log.error("Failed to batch update critical configs", e);
                }
            }
        });
        
        CompletableFuture<Void> apFuture = CompletableFuture.runAsync(() -> {
            if (!nonCriticalConfigs.isEmpty()) {
                apService.batchUpdateConfigs(nonCriticalConfigs);
            }
        });
        
        // 等待完成
        CompletableFuture.allOf(cpFuture, apFuture).join();
    }
    
    // 重试更新
    private void retryUpdate(String key, String value, ConfigType type) {
        int maxRetries = 3;
        int retryDelay = 1000; // 1秒
        
        for (int i = 0; i < maxRetries; i++) {
            try {
                Thread.sleep(retryDelay * (i + 1)); // 指数退避
                
                if (type == ConfigType.CRITICAL) {
                    cpService.updateConfig(key, value);
                } else {
                    apService.updateConfig(key, value);
                }
                
                log.info("Successfully updated config after {} retries: {}", i + 1, key);
                return;
            } catch (Exception e) {
                log.warn("Retry {} failed for config: {}", i + 1, key, e);
            }
        }
        
        log.error("Failed to update config after {} retries: {}", maxRetries, key);
    }
}

// 配置分类器
@Component
public class ConfigClassifier {
    
    private final Set<String> criticalConfigPatterns;
    
    public ConfigClassifier() {
        // 定义关键配置模式
        criticalConfigPatterns = Set.of(
            "database.*",
            "security.*",
            "payment.*",
            "auth.*",
            "encryption.*"
        );
    }
    
    public ConfigType classify(String configKey) {
        // 检查是否匹配关键配置模式
        for (String pattern : criticalConfigPatterns) {
            if (configKey.matches(pattern.replace("*", ".*"))) {
                return ConfigType.CRITICAL;
            }
        }
        
        return ConfigType.NON_CRITICAL;
    }
    
    public enum ConfigType {
        CRITICAL,      // 需要强一致性
        NON_CRITICAL   // 可以最终一致性
    }
}
```

### 分区检测和恢复
```java
// 分区检测器
@Component
public class PartitionDetector {
    
    private final List<Node> clusterNodes;
    private final PartitionHandler partitionHandler;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    
    public PartitionDetector(List<Node> clusterNodes, PartitionHandler partitionHandler) {
        this.clusterNodes = clusterNodes;
        this.partitionHandler = partitionHandler;
    }
    
    @PostConstruct
    public void startDetection() {
        // 定期检测网络分区
        scheduler.scheduleAtFixedRate(this::detectPartitions, 5, 5, TimeUnit.SECONDS);
    }
    
    // 检测网络分区
    private void detectPartitions() {
        Map<Node, NodeStatus> nodeStatuses = new HashMap<>();
        
        // 检查所有节点状态
        for (Node node : clusterNodes) {
            try {
                NodeStatus status = checkNodeStatus(node);
                nodeStatuses.put(node, status);
            } catch (Exception e) {
                nodeStatuses.put(node, NodeStatus.UNREACHABLE);
            }
        }
        
        // 分析分区情况
        PartitionInfo partitionInfo = analyzePartitions(nodeStatuses);
        
        // 处理分区
        if (partitionInfo.hasPartition()) {
            partitionHandler.handlePartition(partitionInfo);
        }
    }
    
    // 检查节点状态
    private NodeStatus checkNodeStatus(Node node) {
        try {
            // 发送心跳
            HeartbeatResponse response = node.sendHeartbeat();
            
            if (response.isHealthy()) {
                return NodeStatus.HEALTHY;
            } else {
                return NodeStatus.UNHEALTHY;
            }
        } catch (Exception e) {
            return NodeStatus.UNREACHABLE;
        }
    }
    
    // 分析分区情况
    private PartitionInfo analyzePartitions(Map<Node, NodeStatus> nodeStatuses) {
        List<Node> healthyNodes = nodeStatuses.entrySet().stream()
            .filter(entry -> entry.getValue() == NodeStatus.HEALTHY)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
        
        List<Node> unhealthyNodes = nodeStatuses.entrySet().stream()
            .filter(entry -> entry.getValue() != NodeStatus.HEALTHY)
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
        
        // 检查是否存在分区
        boolean hasPartition = healthyNodes.size() > 0 && unhealthyNodes.size() > 0;
        
        return new PartitionInfo(healthyNodes, unhealthyNodes, hasPartition);
    }
    
    @PreDestroy
    public void stopDetection() {
        scheduler.shutdown();
    }
    
    public enum NodeStatus {
        HEALTHY, UNHEALTHY, UNREACHABLE
    }
}

// 分区处理器
@Component
public class PartitionHandler {
    
    private final Node currentNode;
    private final CAPStrategy capStrategy;
    
    public PartitionHandler(Node currentNode, CAPStrategy capStrategy) {
        this.currentNode = currentNode;
        this.capStrategy = capStrategy;
    }
    
    // 处理网络分区
    public void handlePartition(PartitionInfo partitionInfo) {
        List<Node> healthyNodes = partitionInfo.getHealthyNodes();
        List<Node> unhealthyNodes = partitionInfo.getUnhealthyNodes();
        
        // 判断当前节点在哪一边
        boolean currentInHealthy = healthyNodes.contains(currentNode);
        
        if (currentInHealthy) {
            // 当前节点在健康分区
            handleHealthyPartition(healthyNodes, unhealthyNodes);
        } else {
            // 当前节点在不健康分区
            handleUnhealthyPartition(healthyNodes, unhealthyNodes);
        }
    }
    
    // 处理健康分区
    private void handleHealthyPartition(List<Node> healthyNodes, List<Node> unhealthyNodes) {
        log.info("Node {} is in healthy partition with {} nodes", 
            currentNode.getId(), healthyNodes.size());
        
        // 根据CAP策略调整行为
        if (capStrategy == CAPStrategy.CP) {
            // CP策略：继续提供服务，拒绝写入
            enableReadOnlyMode();
        } else if (capStrategy == CAPStrategy.AP) {
            // AP策略：继续正常服务
            enableNormalMode();
        }
        
        // 记录分区事件
        logPartitionEvent("HEALTHY_PARTITION", healthyNodes, unhealthyNodes);
    }
    
    // 处理不健康分区
    private void handleUnhealthyPartition(List<Node> healthyNodes, List<Node> unhealthyNodes) {
        log.warn("Node {} is in unhealthy partition with {} nodes", 
            currentNode.getId(), unhealthyNodes.size());
        
        // 根据CAP策略调整行为
        if (capStrategy == CAPStrategy.CP) {
            // CP策略：停止服务，避免数据不一致
            enableMaintenanceMode();
        } else if (capStrategy == CAPStrategy.AP) {
            // AP策略：继续服务，接受数据不一致风险
            enableNormalMode();
        }
        
        // 记录分区事件
        logPartitionEvent("UNHEALTHY_PARTITION", healthyNodes, unhealthyNodes);
    }
    
    // 启用只读模式
    private void enableReadOnlyMode() {
        // 实现只读模式逻辑
        log.info("Enabling read-only mode due to network partition");
    }
    
    // 启用维护模式
    private void enableMaintenanceMode() {
        // 实现维护模式逻辑
        log.info("Enabling maintenance mode due to network partition");
    }
    
    // 启用正常模式
    private void enableNormalMode() {
        // 实现正常模式逻辑
        log.info("Enabling normal mode");
    }
    
    // 记录分区事件
    private void logPartitionEvent(String eventType, List<Node> healthyNodes, List<Node> unhealthyNodes) {
        PartitionEvent event = new PartitionEvent(
            eventType,
            currentNode.getId(),
            healthyNodes.stream().map(Node::getId).collect(Collectors.toList()),
            unhealthyNodes.stream().map(Node::getId).collect(Collectors.toList()),
            System.currentTimeMillis()
        );
        
        // 发布分区事件
        ApplicationEventPublisher publisher = getEventPublisher();
        if (publisher != null) {
            publisher.publishEvent(event);
        }
    }
    
    private ApplicationEventPublisher getEventPublisher() {
        // 获取事件发布器
        return null; // 实际实现中应该注入
    }
    
    public enum CAPStrategy {
        CP,  // 一致性优先
        AP   // 可用性优先
    }
}
```

## 最佳实践

### CAP策略选择
1. **金融系统**: 选择CP策略，确保数据一致性
2. **社交网络**: 选择AP策略，优先保证可用性
3. **电商系统**: 混合策略，核心数据CP，其他AP
4. **监控系统**: 选择AP策略，持续监控更重要

### 一致性保证
1. **强一致性**: 使用Raft、Paxos等共识算法
2. **最终一致性**: 使用异步复制、冲突解决
3. **因果一致性**: 使用向量时钟、版本向量
4. **会话一致性**: 会话内保证一致性

### 可用性设计
1. **冗余部署**: 多节点部署，避免单点故障
2. **故障转移**: 自动检测和切换
3. **降级策略**: 服务降级，保证核心功能
4. **负载均衡**: 分散负载，提高可用性

### 分区处理
1. **分区检测**: 定期心跳检测网络状态
2. **分区恢复**: 自动恢复和数据同步
3. **冲突解决**: 智能合并冲突数据
4. **事件记录**: 记录分区事件用于分析

## 相关技能

- **distributed-consistency** - 分布式一致性
- **database-sharding** - 数据库分片
- **cache-invalidation** - 缓存失效
- **high-concurrency** - 高并发系统设计
- **algorithm-advisor** - 算法顾问
