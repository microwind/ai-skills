---
name: 分布式一致性
description: "当实现分布式一致性时，分析一致性算法，优化数据同步，解决冲突处理。验证一致性模型，设计协调机制，和最佳实践。"
license: MIT
---

# 分布式一致性技能

## 概述
分布式一致性是分布式系统中的核心挑战，确保多个节点上的数据副本在逻辑上保持一致。不同的一致性模型适用于不同的业务场景，需要在一致性、可用性和性能之间做出权衡。理解一致性模型和实现机制对构建可靠的分布式系统至关重要。

**核心原则**: 强一致性保证数据的绝对一致但影响可用性，最终一致性提供高可用性但允许暂时不一致。没有完美的一致性模型，只有适合特定场景的选择。

## 何时使用

**始终:**
- 设计分布式数据库时
- 实现分布式缓存时
- 处理分布式事务时
- 构建微服务架构时
- 设计消息队列时
- 实现分布式锁时

**触发短语:**
- "如何保证分布式一致性？"
- "一致性算法选择"
- "最终一致性实现"
- "分布式事务处理"
- "冲突解决策略"
- "数据同步机制"

## 分布式一致性技能功能

### 一致性模型
- 强一致性
- 最终一致性
- 因果一致性
- 会话一致性
- 单调一致性

### 一致性算法
- Raft算法
- Paxos算法
- PBFT算法
- Gossip协议
- 向量时钟

### 数据同步
- 主从复制
- 多主复制
- 同步复制
- 异步复制
- 增量同步

### 冲突处理
- 冲突检测
- 冲突解决
- 版本控制
- 合并策略
- 补偿事务

## 常见问题

### 一致性问题
- **问题**: 数据副本不一致
- **原因**: 网络分区，并发更新
- **解决**: 使用合适的一致性算法，实现冲突检测

- **问题**: 写入冲突
- **原因**: 多节点同时写入
- **解决**: 使用分布式锁，实现冲突解决机制

### 性能问题
- **问题**: 一致性协议开销大
- **原因**: 过多的协调通信
- **解决**: 优化协议，减少不必要的协调

- **问题**: 同步延迟高
- **原因**: 网络延迟，复制开销
- **解决**: 使用异步复制，优化网络拓扑

### 可用性问题
- **问题**: 分区时系统不可用
- **原因**: 强一致性要求
- **解决**: 使用最终一致性，实现降级策略

## 代码示例

### Raft一致性算法实现
```java
// Raft节点状态
public enum NodeState {
    FOLLOWER, CANDIDATE, LEADER
}

// Raft日志条目
public class LogEntry {
    private final long term;
    private final long index;
    private final Object command;
    
    public LogEntry(long term, long index, Object command) {
        this.term = term;
        this.index = index;
        this.command = command;
    }
    
    // Getters
    public long getTerm() { return term; }
    public long getIndex() { return index; }
    public Object getCommand() { return command; }
}

// Raft节点实现
@Component
public class RaftNode {
    
    private volatile NodeState state = NodeState.FOLLOWER;
    private volatile long currentTerm = 0;
    private volatile String votedFor = null;
    private volatile String leaderId = null;
    
    private final List<LogEntry> log = new ArrayList<>();
    private final Map<String, Long> nextIndex = new HashMap<>();
    private final Map<String, Long> matchIndex = new HashMap<>();
    
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(4);
    private final List<RaftNode> peers = new ArrayList<>();
    private final StateMachine stateMachine;
    
    // 选举超时
    private long electionTimeout = 5000 + new Random().nextInt(5000);
    private long lastHeartbeat = System.currentTimeMillis();
    
    public RaftNode(StateMachine stateMachine) {
        this.stateMachine = stateMachine;
        startElectionTimer();
    }
    
    // 启动选举定时器
    private void startElectionTimer() {
        scheduler.scheduleAtFixedRate(() -> {
            if (state == NodeState.FOLLOWER || state == NodeState.CANDIDATE) {
                long currentTime = System.currentTimeMillis();
                if (currentTime - lastHeartbeat > electionTimeout) {
                    startElection();
                }
            }
        }, 100, 100, TimeUnit.MILLISECONDS);
    }
    
    // 开始选举
    public void startElection() {
        state = NodeState.CANDIDATE;
        currentTerm++;
        votedFor = getNodeId();
        
        System.out.println("Node " + getNodeId() + " started election for term " + currentTerm);
        
        // 给自己投票
        int votes = 1;
        
        // 向其他节点请求投票
        List<CompletableFuture<Boolean>> voteFutures = peers.stream()
            .map(peer -> CompletableFuture.supplyAsync(() -> 
                requestVote(peer, currentTerm, getLog().size() - 1, getLogTerm(getLog().size() - 1))))
            .collect(Collectors.toList());
        
        // 等待投票结果
        for (CompletableFuture<Boolean> future : voteFutures) {
            try {
                if (future.get(1, TimeUnit.SECONDS)) {
                    votes++;
                }
            } catch (Exception e) {
                // 投票请求失败
            }
        }
        
        // 检查是否获得多数票
        if (votes > (peers.size() + 1) / 2) {
            becomeLeader();
        } else {
            state = NodeState.FOLLOWER;
        }
    }
    
    // 成为领导者
    private void becomeLeader() {
        state = NodeState.LEADER;
        leaderId = getNodeId();
        
        System.out.println("Node " + getNodeId() + " became leader for term " + currentTerm);
        
        // 初始化nextIndex和matchIndex
        for (RaftNode peer : peers) {
            nextIndex.put(peer.getNodeId(), (long) getLog().size());
            matchIndex.put(peer.getNodeId(), 0L);
        }
        
        // 开始心跳
        startHeartbeat();
    }
    
    // 开始心跳
    private void startHeartbeat() {
        scheduler.scheduleAtFixedRate(() -> {
            if (state == NodeState.LEADER) {
                sendHeartbeats();
            }
        }, 0, 100, TimeUnit.MILLISECONDS);
    }
    
    // 发送心跳
    private void sendHeartbeats() {
        for (RaftNode peer : peers) {
            long nextIdx = nextIndex.get(peer.getNodeId());
            List<LogEntry> entries = new ArrayList<>();
            
            if (nextIdx < getLog().size()) {
                entries = getLog().subList((int) nextIdx, getLog().size());
            }
            
            AppendEntriesResult result = sendAppendEntries(
                peer, currentTerm, getNodeId(), 
                nextIdx - 1, getLogTerm(nextIdx - 1), entries, getCommitIndex());
            
            if (result.isSuccess()) {
                nextIndex.put(peer.getNodeId(), nextIdx + entries.size());
                matchIndex.put(peer.getNodeId(), nextIdx + entries.size() - 1);
            } else {
                nextIndex.put(peer.getNodeId(), Math.max(nextIdx - 1, 0));
            }
        }
        
        // 更新commitIndex
        updateCommitIndex();
    }
    
    // 处理投票请求
    public boolean handleRequestVote(long term, String candidateId, long lastLogIndex, long lastLogTerm) {
        if (term < currentTerm) {
            return false;
        }
        
        if (term > currentTerm) {
            currentTerm = term;
            state = NodeState.FOLLOWER;
            votedFor = null;
        }
        
        if (votedFor != null && !votedFor.equals(candidateId)) {
            return false;
        }
        
        if (lastLogTerm < getLogTerm(getLog().size() - 1) || 
            (lastLogTerm == getLogTerm(getLog().size() - 1) && lastLogIndex < getLog().size() - 1)) {
            return false;
        }
        
        votedFor = candidateId;
        lastHeartbeat = System.currentTimeMillis();
        return true;
    }
    
    // 处理追加条目请求
    public AppendEntriesResult handleAppendEntries(long term, String leaderId, 
                                                long prevLogIndex, long prevLogTerm, 
                                                List<LogEntry> entries, long leaderCommit) {
        if (term < currentTerm) {
            return new AppendEntriesResult(false, currentTerm);
        }
        
        currentTerm = term;
        this.leaderId = leaderId;
        state = NodeState.FOLLOWER;
        lastHeartbeat = System.currentTimeMillis();
        
        // 检查日志一致性
        if (prevLogIndex >= 0 && 
            (getLog().size() <= prevLogIndex || getLogTerm(prevLogIndex) != prevLogTerm)) {
            return new AppendEntriesResult(false, currentTerm);
        }
        
        // 追加日志条目
        for (int i = 0; i < entries.size(); i++) {
            LogEntry entry = entries.get(i);
            long index = prevLogIndex + 1 + i;
            
            if (getLog().size() > index && getLogTerm(index) != entry.getTerm()) {
                // 冲突，删除该位置及之后的条目
                truncateLog(index);
            }
            
            if (getLog().size() <= index) {
                appendLog(entry);
            }
        }
        
        // 更新commitIndex
        if (leaderCommit > getCommitIndex()) {
            setCommitIndex(Math.min(leaderCommit, getLog().size() - 1));
            applyToStateMachine();
        }
        
        return new AppendEntriesResult(true, currentTerm);
    }
    
    // 提交命令到状态机
    public CompletableFuture<Object> submitCommand(Object command) {
        if (state != NodeState.LEADER) {
            return CompletableFuture.failedFuture(new RuntimeException("Not leader"));
        }
        
        CompletableFuture<Object> future = new CompletableFuture<>();
        
        // 添加到日志
        LogEntry entry = new LogEntry(currentTerm, getLog().size(), command);
        appendLog(entry);
        
        // 等待提交
        waitForCommit(entry.getIndex(), future);
        
        return future;
    }
    
    // 等待命令提交
    private void waitForCommit(long index, CompletableFuture<Object> future) {
        scheduler.schedule(() -> {
            if (getCommitIndex() >= index) {
                Object result = stateMachine.apply(entry.getCommand());
                future.complete(result);
            } else {
                waitForCommit(index, future);
            }
        }, 10, TimeUnit.MILLISECONDS);
    }
    
    // 更新commitIndex
    private void updateCommitIndex() {
        for (long i = getCommitIndex() + 1; i < getLog().size(); i++) {
            int count = 1; // leader自己
            
            for (RaftNode peer : peers) {
                if (matchIndex.get(peer.getNodeId()) >= i) {
                    count++;
                }
            }
            
            if (count > (peers.size() + 1) / 2 && getLogTerm(i) == currentTerm) {
                setCommitIndex(i);
                applyToStateMachine();
            }
        }
    }
    
    // 应用到状态机
    private void applyToStateMachine() {
        while (getLastApplied() < getCommitIndex()) {
            LogEntry entry = getLog().get((int) getLastApplied() + 1);
            stateMachine.apply(entry.getCommand());
            setLastApplied(getLastApplied() + 1);
        }
    }
    
    // 辅助方法
    private String getNodeId() {
        return "node-" + hashCode();
    }
    
    private List<LogEntry> getLog() {
        return log;
    }
    
    private long getLogTerm(long index) {
        if (index < 0 || index >= log.size()) {
            return 0;
        }
        return log.get((int) index).getTerm();
    }
    
    private void appendLog(LogEntry entry) {
        log.add(entry);
    }
    
    private void truncateLog(long index) {
        log.subList((int) index, log.size()).clear();
    }
    
    private long getCommitIndex() {
        return 0; // 简化实现
    }
    
    private void setCommitIndex(long index) {
        // 实现设置commitIndex
    }
    
    private long getLastApplied() {
        return 0; // 简化实现
    }
    
    private void setLastApplied(long index) {
        // 实现设置lastApplied
    }
    
    // 网络通信方法（简化）
    private boolean requestVote(RaftNode peer, long term, long lastLogIndex, long lastLogTerm) {
        return peer.handleRequestVote(term, getNodeId(), lastLogIndex, lastLogTerm);
    }
    
    private AppendEntriesResult sendAppendEntries(RaftNode peer, long term, String leaderId, 
                                               long prevLogIndex, long prevLogTerm, 
                                               List<LogEntry> entries, long leaderCommit) {
        return peer.handleAppendEntries(term, leaderId, prevLogIndex, prevLogTerm, entries, leaderCommit);
    }
}

// 追加条目结果
public class AppendEntriesResult {
    private final boolean success;
    private final long term;
    
    public AppendEntriesResult(boolean success, long term) {
        this.success = success;
        this.term = term;
    }
    
    public boolean isSuccess() { return success; }
    public long getTerm() { return term; }
}

// 状态机接口
public interface StateMachine {
    Object apply(Object command);
}
```

### 最终一致性实现
```java
// 最终一致性存储
@Component
public class EventualConsistencyStore {
    
    private final Map<String, VersionedValue> store = new ConcurrentHashMap<>();
    private final List<ReplicaNode> replicas = new ArrayList<>();
    private final ConflictResolver conflictResolver;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    
    public EventualConsistencyStore(ConflictResolver conflictResolver) {
        this.conflictResolver = conflictResolver;
        startAntiEntropy();
    }
    
    // 写入数据
    public void write(String key, Object value, String nodeId) {
        VersionedValue existingValue = store.get(key);
        VectorClock newClock = existingValue != null ? 
            existingValue.getVectorClock().increment(nodeId) : 
            new VectorClock().increment(nodeId);
        
        VersionedValue newValue = new VersionedValue(value, newClock, System.currentTimeMillis());
        store.put(key, newValue);
        
        // 异步复制到其他副本
        replicateToOthers(key, newValue, nodeId);
    }
    
    // 读取数据
    public Object read(String key) {
        VersionedValue value = store.get(key);
        return value != null ? value.getValue() : null;
    }
    
    // 读取带版本信息
    public VersionedValue readWithVersion(String key) {
        return store.get(key);
    }
    
    // 复制到其他副本
    private void replicateToOthers(String key, VersionedValue value, String sourceNode) {
        for (ReplicaNode replica : replicas) {
            if (!replica.getNodeId().equals(sourceNode)) {
                CompletableFuture.runAsync(() -> {
                    try {
                        replica.replicate(key, value);
                    } catch (Exception e) {
                        log.error("Failed to replicate to replica: " + replica.getNodeId(), e);
                    }
                });
            }
        }
    }
    
    // 处理复制请求
    public void handleReplication(String key, VersionedValue value) {
        VersionedValue existingValue = store.get(key);
        
        if (existingValue == null) {
            store.put(key, value);
        } else {
            int comparison = existingValue.getVectorClock().compareTo(value.getVectorClock());
            
            if (comparison < 0) {
                // 新版本，直接替换
                store.put(key, value);
            } else if (comparison == 0) {
                // 相同版本，检查时间戳
                if (value.getTimestamp() > existingValue.getTimestamp()) {
                    store.put(key, value);
                }
            } else {
                // 冲突，需要解决
                VersionedValue resolved = conflictResolver.resolve(existingValue, value);
                store.put(key, resolved);
            }
        }
    }
    
    // 启动反熵过程
    private void startAntiEntropy() {
        scheduler.scheduleAtFixedRate(() -> {
            performAntiEntropy();
        }, 30, 30, TimeUnit.SECONDS);
    }
    
    // 执行反熵
    private void performAntiEntropy() {
        for (ReplicaNode replica : replicas) {
            try {
                Map<String, VersionedValue> replicaData = replica.getData();
                
                // 比较并同步差异
                for (Map.Entry<String, VersionedValue> entry : store.entrySet()) {
                    String key = entry.getKey();
                    VersionedValue localValue = entry.getValue();
                    VersionedValue remoteValue = replicaData.get(key);
                    
                    if (remoteValue == null) {
                        // 远程没有，发送本地数据
                        replica.replicate(key, localValue);
                    } else {
                        // 比较版本
                        int comparison = localValue.getVectorClock().compareTo(remoteValue.getVectorClock());
                        
                        if (comparison > 0) {
                            // 本地版本更新，发送到远程
                            replica.replicate(key, localValue);
                        } else if (comparison < 0) {
                            // 远程版本更新，更新本地
                            handleReplication(key, remoteValue);
                        }
                    }
                }
                
                // 检查远程独有的数据
                for (Map.Entry<String, VersionedValue> entry : replicaData.entrySet()) {
                    String key = entry.getKey();
                    if (!store.containsKey(key)) {
                        handleReplication(key, entry.getValue());
                    }
                }
                
            } catch (Exception e) {
                log.error("Anti-entropy failed for replica: " + replica.getNodeId(), e);
            }
        }
    }
    
    // 添加副本节点
    public void addReplica(ReplicaNode replica) {
        replicas.add(replica);
    }
    
    // 获取所有数据
    public Map<String, VersionedValue> getData() {
        return new HashMap<>(store);
    }
}

// 版本化值
public class VersionedValue {
    private final Object value;
    private final VectorClock vectorClock;
    private final long timestamp;
    
    public VersionedValue(Object value, VectorClock vectorClock, long timestamp) {
        this.value = value;
        this.vectorClock = vectorClock;
        this.timestamp = timestamp;
    }
    
    // Getters
    public Object getValue() { return value; }
    public VectorClock getVectorClock() { return vectorClock; }
    public long getTimestamp() { return timestamp; }
}

// 向量时钟
public class VectorClock {
    private final Map<String, Long> clock = new HashMap<>();
    
    public VectorClock increment(String nodeId) {
        VectorClock newClock = new VectorClock();
        newClock.clock.putAll(this.clock);
        newClock.clock.put(nodeId, newClock.clock.getOrDefault(nodeId, 0L) + 1);
        return newClock;
    }
    
    public int compareTo(VectorClock other) {
        // 比较两个向量时钟
        boolean thisGreater = false;
        boolean otherGreater = false;
        
        Set<String> allNodes = new HashSet<>();
        allNodes.addAll(this.clock.keySet());
        allNodes.addAll(other.clock.keySet());
        
        for (String node : allNodes) {
            long thisTime = this.clock.getOrDefault(node, 0L);
            long otherTime = other.clock.getOrDefault(node, 0L);
            
            if (thisTime > otherTime) {
                thisGreater = true;
            } else if (thisTime < otherTime) {
                otherGreater = true;
            }
        }
        
        if (thisGreater && !otherGreater) {
            return 1; // this > other
        } else if (!thisGreater && otherGreater) {
            return -1; // this < other
        } else if (!thisGreater && !otherGreater) {
            return 0; // this == other
        } else {
            return 2; // 并发
        }
    }
    
    // Getters
    public Map<String, Long> getClock() {
        return new HashMap<>(clock);
    }
}

// 冲突解决器
@Component
public class ConflictResolver {
    
    // 解决冲突
    public VersionedValue resolve(VersionedValue value1, VersionedValue value2) {
        // 简单的解决策略：选择时间戳较新的值
        if (value1.getTimestamp() > value2.getTimestamp()) {
            return value1;
        } else if (value2.getTimestamp() > value1.getTimestamp()) {
            return value2;
        } else {
            // 时间戳相同，合并值
            Object mergedValue = mergeValues(value1.getValue(), value2.getValue());
            VectorClock mergedClock = mergeVectorClocks(value1.getVectorClock(), value2.getVectorClock());
            
            return new VersionedValue(mergedValue, mergedClock, System.currentTimeMillis());
        }
    }
    
    // 合并值
    private Object mergeValues(Object value1, Object value2) {
        // 简化实现：返回其中一个值
        // 实际实现中应该根据具体业务逻辑进行合并
        return value1;
    }
    
    // 合并向量时钟
    private VectorClock mergeVectorClocks(VectorClock clock1, VectorClock clock2) {
        VectorClock merged = new VectorClock();
        
        Set<String> allNodes = new HashSet<>();
        allNodes.addAll(clock1.getClock().keySet());
        allNodes.addAll(clock2.getClock().keySet());
        
        for (String node : allNodes) {
            long time1 = clock1.getClock().getOrDefault(node, 0L);
            long time2 = clock2.getClock().getOrDefault(node, 0L);
            merged.getClock().put(node, Math.max(time1, time2));
        }
        
        return merged;
    }
}

// 副本节点接口
public interface ReplicaNode {
    String getNodeId();
    void replicate(String key, VersionedValue value) throws Exception;
    Map<String, VersionedValue> getData() throws Exception;
}
```

### 分布式事务实现
```java
// 两阶段提交协调器
@Service
public class TwoPhaseCommitCoordinator {
    
    private final List<TransactionParticipant> participants;
    private final Map<String, TransactionContext> transactions = new ConcurrentHashMap<>();
    
    public TwoPhaseCommitCoordinator(List<TransactionParticipant> participants) {
        this.participants = participants;
    }
    
    // 开始事务
    public String beginTransaction() {
        String transactionId = generateTransactionId();
        TransactionContext context = new TransactionContext(transactionId, TransactionStatus.ACTIVE);
        transactions.put(transactionId, context);
        return transactionId;
    }
    
    // 提交事务
    public boolean commitTransaction(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null || context.getStatus() != TransactionStatus.ACTIVE) {
            return false;
        }
        
        // 第一阶段：准备阶段
        boolean allPrepared = true;
        List<TransactionParticipant> preparedParticipants = new ArrayList<>();
        
        for (TransactionParticipant participant : participants) {
            try {
                if (participant.prepare(transactionId)) {
                    preparedParticipants.add(participant);
                } else {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }
        
        // 第二阶段：提交或回滚
        if (allPrepared) {
            // 提交
            boolean allCommitted = true;
            for (TransactionParticipant participant : preparedParticipants) {
                try {
                    participant.commit(transactionId);
                } catch (Exception e) {
                    allCommitted = false;
                    log.error("Failed to commit transaction on participant: " + participant.getId(), e);
                }
            }
            
            context.setStatus(allCommitted ? TransactionStatus.COMMITTED : TransactionStatus.FAILED);
            return allCommitted;
        } else {
            // 回滚
            for (TransactionParticipant participant : preparedParticipants) {
                try {
                    participant.rollback(transactionId);
                } catch (Exception e) {
                    log.error("Failed to rollback transaction on participant: " + participant.getId(), e);
                }
            }
            
            context.setStatus(TransactionStatus.ABORTED);
            return false;
        }
    }
    
    // 回滚事务
    public boolean rollbackTransaction(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null || context.getStatus() != TransactionStatus.ACTIVE) {
            return false;
        }
        
        boolean allRolledBack = true;
        for (TransactionParticipant participant : participants) {
            try {
                participant.rollback(transactionId);
            } catch (Exception e) {
                allRolledBack = false;
                log.error("Failed to rollback transaction on participant: " + participant.getId(), e);
            }
        }
        
        context.setStatus(allRolledBack ? TransactionStatus.ABORTED : TransactionStatus.FAILED);
        return allRolledBack;
    }
    
    // 获取事务状态
    public TransactionStatus getTransactionStatus(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        return context != null ? context.getStatus() : null;
    }
    
    private String generateTransactionId() {
        return "tx-" + UUID.randomUUID().toString();
    }
}

// 事务上下文
public class TransactionContext {
    private final String transactionId;
    private volatile TransactionStatus status;
    private final long startTime;
    
    public TransactionContext(String transactionId, TransactionStatus status) {
        this.transactionId = transactionId;
        this.status = status;
        this.startTime = System.currentTimeMillis();
    }
    
    // Getters and setters
    public String getTransactionId() { return transactionId; }
    public TransactionStatus getStatus() { return status; }
    public void setStatus(TransactionStatus status) { this.status = status; }
    public long getStartTime() { return startTime; }
}

// 事务状态
public enum TransactionStatus {
    ACTIVE, PREPARING, COMMITTED, ABORTED, FAILED
}

// 事务参与者接口
public interface TransactionParticipant {
    String getId();
    boolean prepare(String transactionId) throws Exception;
    void commit(String transactionId) throws Exception;
    void rollback(String transactionId) throws Exception;
}

// 补偿事务管理器
@Service
public class CompensatingTransactionManager {
    
    private final Map<String, SagaTransaction> sagas = new ConcurrentHashMap<>();
    private final List<CompensableAction> actions;
    
    public CompensatingTransactionManager(List<CompensableAction> actions) {
        this.actions = actions;
    }
    
    // 执行Saga事务
    public String executeSaga(List<String> actionIds) {
        String sagaId = generateSagaId();
        SagaTransaction saga = new SagaTransaction(sagaId);
        sagas.put(sagaId, saga);
        
        List<CompensableAction> executedActions = new ArrayList<>();
        
        try {
            for (String actionId : actionIds) {
                CompensableAction action = findAction(actionId);
                
                // 执行动作
                ActionResult result = action.execute();
                saga.addExecution(actionId, result);
                executedActions.add(action);
                
                if (!result.isSuccess()) {
                    // 执行失败，开始补偿
                    executeCompensation(executedActions, saga);
                    saga.setStatus(SagaStatus.FAILED);
                    return sagaId;
                }
            }
            
            saga.setStatus(SagaStatus.COMPLETED);
            return sagaId;
            
        } catch (Exception e) {
            // 异常情况，执行补偿
            executeCompensation(executedActions, saga);
            saga.setStatus(SagaStatus.FAILED);
            return sagaId;
        }
    }
    
    // 执行补偿
    private void executeCompensation(List<CompensableAction> executedActions, SagaTransaction saga) {
        // 逆序执行补偿
        for (int i = executedActions.size() - 1; i >= 0; i--) {
            CompensableAction action = executedActions.get(i);
            
            try {
                action.compensate();
                saga.addCompensation(action.getId());
            } catch (Exception e) {
                log.error("Failed to compensate action: " + action.getId(), e);
                // 补偿失败，需要人工干预
                saga.setStatus(SagaStatus.COMPENSATION_FAILED);
            }
        }
    }
    
    // 重试失败的Saga
    public boolean retrySaga(String sagaId) {
        SagaTransaction saga = sagas.get(sagaId);
        if (saga == null || saga.getStatus() != SagaStatus.FAILED) {
            return false;
        }
        
        // 重新执行失败的动作
        List<String> failedActions = saga.getFailedActions();
        return executeSaga(failedActions).equals(sagaId);
    }
    
    private CompensableAction findAction(String actionId) {
        return actions.stream()
            .filter(action -> action.getId().equals(actionId))
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException("Action not found: " + actionId));
    }
    
    private String generateSagaId() {
        return "saga-" + UUID.randomUUID().toString();
    }
}

// Saga事务
public class SagaTransaction {
    private final String sagaId;
    private volatile SagaStatus status;
    private final List<ActionExecution> executions = new ArrayList<>();
    private final List<String> compensations = new ArrayList<>();
    
    public SagaTransaction(String sagaId) {
        this.sagaId = sagaId;
        this.status = SagaStatus.RUNNING;
    }
    
    public void addExecution(String actionId, ActionResult result) {
        executions.add(new ActionExecution(actionId, result));
    }
    
    public void addCompensation(String actionId) {
        compensations.add(actionId);
    }
    
    public List<String> getFailedActions() {
        return executions.stream()
            .filter(execution -> !execution.getResult().isSuccess())
            .map(ActionExecution::getActionId)
            .collect(Collectors.toList());
    }
    
    // Getters and setters
    public String getSagaId() { return sagaId; }
    public SagaStatus getStatus() { return status; }
    public void setStatus(SagaStatus status) { this.status = status; }
}

// Saga状态
public enum SagaStatus {
    RUNNING, COMPLETED, FAILED, COMPENSATION_FAILED
}

// 可补偿动作
public interface CompensableAction {
    String getId();
    ActionResult execute() throws Exception;
    void compensate() throws Exception;
}

// 动作结果
public class ActionResult {
    private final boolean success;
    private final Object result;
    private final String errorMessage;
    
    public ActionResult(boolean success, Object result, String errorMessage) {
        this.success = success;
        this.result = result;
        this.errorMessage = errorMessage;
    }
    
    // Getters
    public boolean isSuccess() { return success; }
    public Object getResult() { return result; }
    public String getErrorMessage() { return errorMessage; }
}

// 动作执行记录
public class ActionExecution {
    private final String actionId;
    private final ActionResult result;
    private final long timestamp;
    
    public ActionExecution(String actionId, ActionResult result) {
        this.actionId = actionId;
        this.result = result;
        this.timestamp = System.currentTimeMillis();
    }
    
    // Getters
    public String getActionId() { return actionId; }
    public ActionResult getResult() { return result; }
    public long getTimestamp() { return timestamp; }
}
```

## 最佳实践

### 一致性模型选择
1. **强一致性**: 金融交易、库存管理等关键业务
2. **最终一致性**: 社交网络、内容分发等非关键业务
3. **因果一致性**: 消息系统、事件驱动架构
4. **会话一致性**: 用户会话数据、购物车等

### 算法选择
1. **Raft**: 易于理解和实现，适合大多数场景
2. **Paxos**: 理论完备，实现复杂
3. **PBFT**: 恶意环境下的拜占庭容错
4. **Gossip**: 去中心化，适合大规模系统

### 性能优化
1. **批量操作**: 减少网络通信开销
2. **异步复制**: 提高写入性能
3. **本地缓存**: 减少远程访问
4. **连接复用**: 优化网络连接

### 故障处理
1. **超时机制**: 防止无限等待
2. **重试策略**: 处理临时故障
3. **降级策略**: 保证系统可用性
4. **监控告警**: 及时发现问题

## 相关技能

- **cap-theorem** - CAP定理应用
- **database-sharding** - 数据库分片
- **cache-invalidation** - 缓存失效
- **high-concurrency** - 高并发系统设计
- **algorithm-advisor** - 算法顾问
