---
name: 事务管理
description: "当处理数据库事务时，管理事务边界，处理并发冲突，实现死锁检测。优化事务性能，保证数据一致性，和实现分布式事务。"
license: MIT
---

# 事务管理技能

## 概述
事务管理是保证数据一致性和完整性的核心技术。不当的事务管理会导致数据不一致、死锁、性能问题。需要完善的事务控制机制。

**核心原则**: 好的事务管理应该原子性、一致性、隔离性、持久性。坏的事务管理会数据不一致、死锁频发、性能下降。

## 何时使用

**始终:**
- 需要数据一致性时
- 处理多个相关操作时
- 并发访问共享资源时
- 需要错误恢复时
- 处理金融交易时
- 分布式系统操作时

**触发短语:**
- "事务管理"
- "并发控制"
- "死锁处理"
- "分布式事务"
- "事务隔离级别"
- "锁机制"

## 事务管理功能

### 事务控制
- 事务开始和提交
- 事务回滚处理
- 保存点管理
- 嵌套事务处理
- 事务超时控制

### 并发控制
- 锁机制管理
- 乐观并发控制
- 悲观并发控制
- 多版本并发控制
- 死锁检测与预防

### 隔离级别
- 读未提交
- 读已提交
- 可重复读
- 串行化
- 自定义隔离级别

### 分布式事务
- 两阶段提交
- 三阶段提交
- 补偿事务
- 最终一致性
- 事务协调器

## 常见事务管理问题

### 死锁问题
```
问题:
多个事务相互等待对方释放资源，导致系统僵死

错误示例:
- 不一致的锁获取顺序
- 长时间持有锁
- 不必要的锁范围
- 缺少超时机制

解决方案:
1. 统一锁获取顺序
2. 减少锁持有时间
3. 设置锁超时
4. 实现死锁检测
```

### 脏读问题
```
问题:
事务读取到未提交的数据，导致数据不一致

错误示例:
- 使用读未提交隔离级别
- 缺少适当的锁机制
- 并发更新未控制
- 缓存与数据库不一致

解决方案:
1. 提高隔离级别
2. 实现适当的锁机制
3. 控制并发更新
4. 保持缓存一致性
```

### 幻读问题
```
问题:
事务中多次查询返回不同结果集

错误示例:
- 缺少范围锁
- 隔离级别过低
- 插入操作未控制
- 删除操作未同步

解决方案:
1. 使用串行化隔离级别
2. 实现范围锁
3. 控制插入删除操作
4. 使用乐观锁机制
```

### 长事务问题
```
问题:
事务执行时间过长，影响系统性能

错误示例:
- 事务范围过大
- 用户交互过长
- 网络延迟处理不当
- 资源竞争激烈

解决方案:
1. 拆分大事务
2. 减少用户交互
3. 优化网络处理
4. 减少资源竞争
```

## 代码实现示例

### 事务管理器
```python
import threading
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import contextmanager
import queue

class TransactionState(Enum):
    """事务状态"""
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    PREPARING = "preparing"
    FAILED = "failed"

class IsolationLevel(Enum):
    """隔离级别"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"

class LockType(Enum):
    """锁类型"""
    SHARED = "shared"
    EXCLUSIVE = "exclusive"
    INTENT_SHARED = "intent_shared"
    INTENT_EXCLUSIVE = "intent_exclusive"

@dataclass
class Lock:
    """锁对象"""
    lock_id: str
    resource_id: str
    transaction_id: str
    lock_type: LockType
    acquired_at: float
    expires_at: Optional[float] = None

@dataclass
class SavePoint:
    """保存点"""
    savepoint_id: str
    transaction_id: str
    created_at: float
    operations: List[str]

@dataclass
class Transaction:
    """事务对象"""
    transaction_id: str
    state: TransactionState
    isolation_level: IsolationLevel
    start_time: float
    locks: List[Lock]
    savepoints: List[SavePoint]
    operations: List[str]
    timeout: float

class DeadlockDetector:
    def __init__(self):
        self.wait_graph: Dict[str, List[str]] = {}
        self.lock_graph: Dict[str, List[str]] = {}
    
    def add_wait_edge(self, waiting_tx: str, holding_tx: str):
        """添加等待边"""
        if waiting_tx not in self.wait_graph:
            self.wait_graph[waiting_tx] = []
        self.wait_graph[waiting_tx].append(holding_tx)
    
    def remove_wait_edge(self, waiting_tx: str, holding_tx: str):
        """移除等待边"""
        if waiting_tx in self.wait_graph:
            if holding_tx in self.wait_graph[waiting_tx]:
                self.wait_graph[waiting_tx].remove(holding_tx)
    
    def detect_deadlock(self) -> List[str]:
        """检测死锁"""
        visited = set()
        rec_stack = set()
        deadlocks = []
        
        for tx_id in self.wait_graph:
            if tx_id not in visited:
                cycle = self._dfs_cycle_detection(tx_id, visited, rec_stack)
                if cycle:
                    deadlocks.extend(cycle)
        
        return deadlocks
    
    def _dfs_cycle_detection(self, tx_id: str, visited: set, rec_stack: set) -> List[str]:
        """DFS检测环"""
        visited.add(tx_id)
        rec_stack.add(tx_id)
        
        if tx_id in self.wait_graph:
            for neighbor in self.wait_graph[tx_id]:
                if neighbor not in visited:
                    cycle = self._dfs_cycle_detection(neighbor, visited, rec_stack)
                    if cycle:
                        return [tx_id] + cycle
                elif neighbor in rec_stack:
                    return [tx_id, neighbor]
        
        rec_stack.remove(tx_id)
        return []

class LockManager:
    def __init__(self):
        self.locks: Dict[str, List[Lock]] = {}
        self.waiting_queue: Dict[str, List[tuple]] = {}
        self.deadlock_detector = DeadlockDetector()
        self.lock_timeout = 30.0
    
    def acquire_lock(self, transaction_id: str, resource_id: str, 
                    lock_type: LockType, timeout: Optional[float] = None) -> bool:
        """获取锁"""
        if timeout is None:
            timeout = self.lock_timeout
        
        # 检查是否存在冲突锁
        conflicting_locks = self._find_conflicting_locks(resource_id, lock_type, transaction_id)
        
        if not conflicting_locks:
            # 可以获取锁
            lock = Lock(
                lock_id=str(uuid.uuid4()),
                resource_id=resource_id,
                transaction_id=transaction_id,
                lock_type=lock_type,
                acquired_at=time.time(),
                expires_at=time.time() + timeout
            )
            
            if resource_id not in self.locks:
                self.locks[resource_id] = []
            self.locks[resource_id].append(lock)
            
            return True
        else:
            # 需要等待
            return self._wait_for_lock(transaction_id, resource_id, lock_type, timeout)
    
    def release_lock(self, transaction_id: str, resource_id: str) -> bool:
        """释放锁"""
        if resource_id not in self.locks:
            return False
        
        # 移除事务的锁
        original_count = len(self.locks[resource_id])
        self.locks[resource_id] = [
            lock for lock in self.locks[resource_id] 
            if lock.transaction_id != transaction_id
        ]
        
        if len(self.locks[resource_id]) == 0:
            del self.locks[resource_id]
        
        # 唤醒等待的事务
        self._notify_waiting_transactions(resource_id)
        
        return len(self.locks.get(resource_id, [])) < original_count
    
    def _find_conflicting_locks(self, resource_id: str, lock_type: LockType, 
                               transaction_id: str) -> List[Lock]:
        """查找冲突锁"""
        if resource_id not in self.locks:
            return []
        
        conflicting_locks = []
        
        for lock in self.locks[resource_id]:
            if lock.transaction_id == transaction_id:
                continue
            
            # 检查锁冲突
            if self._is_lock_conflicting(lock_type, lock.lock_type):
                conflicting_locks.append(lock)
        
        return conflicting_locks
    
    def _is_lock_conflicting(self, requested_type: LockType, held_type: LockType) -> bool:
        """检查锁冲突"""
        # 简化的锁冲突矩阵
        conflict_matrix = {
            (LockType.SHARED, LockType.EXCLUSIVE): True,
            (LockType.EXCLUSIVE, LockType.SHARED): True,
            (LockType.EXCLUSIVE, LockType.EXCLUSIVE): True,
        }
        
        return conflict_matrix.get((requested_type, held_type), False)
    
    def _wait_for_lock(self, transaction_id: str, resource_id: str, 
                       lock_type: LockType, timeout: float) -> bool:
        """等待锁"""
        # 添加到等待队列
        if resource_id not in self.waiting_queue:
            self.waiting_queue[resource_id] = []
        
        wait_event = threading.Event()
        self.waiting_queue[resource_id].append((transaction_id, lock_type, wait_event))
        
        # 添加到死锁检测图
        if resource_id in self.locks:
            for lock in self.locks[resource_id]:
                self.deadlock_detector.add_wait_edge(transaction_id, lock.transaction_id)
        
        # 等待锁释放
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 检查死锁
            deadlocks = self.deadlock_detector.detect_deadlock()
            if transaction_id in deadlocks:
                # 发生死锁，移除等待
                self._remove_from_waiting_queue(transaction_id, resource_id)
                return False
            
            # 检查是否可以获取锁
            conflicting_locks = self._find_conflicting_locks(resource_id, lock_type, transaction_id)
            if not conflicting_locks:
                # 可以获取锁
                self._remove_from_waiting_queue(transaction_id, resource_id)
                return self.acquire_lock(transaction_id, resource_id, lock_type, timeout)
            
            # 等待
            wait_event.wait(0.1)
        
        # 超时
        self._remove_from_waiting_queue(transaction_id, resource_id)
        return False
    
    def _remove_from_waiting_queue(self, transaction_id: str, resource_id: str):
        """从等待队列移除"""
        if resource_id in self.waiting_queue:
            self.waiting_queue[resource_id] = [
                item for item in self.waiting_queue[resource_id]
                if item[0] != transaction_id
            ]
    
    def _notify_waiting_transactions(self, resource_id: str):
        """通知等待事务"""
        if resource_id not in self.waiting_queue:
            return
        
        # 唤醒所有等待事务
        for transaction_id, lock_type, wait_event in self.waiting_queue[resource_id]:
            wait_event.set()
        
        # 清空等待队列
        self.waiting_queue[resource_id] = []

class TransactionManager:
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.lock_manager = LockManager()
        self.active_transaction = threading.local()
        self.default_timeout = 60.0
    
    @contextmanager
    def transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
                   timeout: Optional[float] = None):
        """事务上下文管理器"""
        if timeout is None:
            timeout = self.default_timeout
        
        tx_id = self.begin_transaction(isolation_level, timeout)
        
        try:
            yield tx_id
            self.commit_transaction(tx_id)
        except Exception as e:
            self.rollback_transaction(tx_id)
            raise e
    
    def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
                         timeout: Optional[float] = None) -> str:
        """开始事务"""
        if timeout is None:
            timeout = self.default_timeout
        
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            state=TransactionState.ACTIVE,
            isolation_level=isolation_level,
            start_time=time.time(),
            locks=[],
            savepoints=[],
            operations=[],
            timeout=timeout
        )
        
        self.transactions[transaction.transaction_id] = transaction
        self.active_transaction.transaction = transaction
        
        return transaction.transaction_id
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """提交事务"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        
        if transaction.state != TransactionState.ACTIVE:
            return False
        
        try:
            # 设置状态为准备提交
            transaction.state = TransactionState.PREPARING
            
            # 释放所有锁
            for lock in transaction.locks:
                self.lock_manager.release_lock(transaction_id, lock.resource_id)
            
            # 设置提交状态
            transaction.state = TransactionState.COMMITTED
            
            # 清理
            del self.transactions[transaction_id]
            
            return True
            
        except Exception as e:
            transaction.state = TransactionState.FAILED
            self.rollback_transaction(transaction_id)
            return False
    
    def rollback_transaction(self, transaction_id: str) -> bool:
        """回滚事务"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        
        if transaction.state == TransactionState.COMMITTED:
            return False
        
        try:
            # 释放所有锁
            for lock in transaction.locks:
                self.lock_manager.release_lock(transaction_id, lock.resource_id)
            
            # 设置回滚状态
            transaction.state = TransactionState.ROLLED_BACK
            
            # 清理
            del self.transactions[transaction_id]
            
            return True
            
        except Exception as e:
            transaction.state = TransactionState.FAILED
            return False
    
    def create_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """创建保存点"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        
        if transaction.state != TransactionState.ACTIVE:
            return False
        
        savepoint = SavePoint(
            savepoint_id=savepoint_name,
            transaction_id=transaction_id,
            created_at=time.time(),
            operations=transaction.operations.copy()
        )
        
        transaction.savepoints.append(savepoint)
        return True
    
    def rollback_to_savepoint(self, transaction_id: str, savepoint_name: str) -> bool:
        """回滚到保存点"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        
        if transaction.state != TransactionState.ACTIVE:
            return False
        
        # 查找保存点
        savepoint = None
        for sp in transaction.savepoints:
            if sp.savepoint_id == savepoint_name:
                savepoint = sp
                break
        
        if not savepoint:
            return False
        
        # 恢复操作列表
        transaction.operations = savepoint.operations.copy()
        
        # 移除之后的保存点
        index = transaction.savepoints.index(savepoint)
        transaction.savepoints = transaction.savepoints[:index + 1]
        
        return True
    
    def get_transaction_info(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """获取事务信息"""
        if transaction_id not in self.transactions:
            return None
        
        transaction = self.transactions[transaction_id]
        
        return {
            'transaction_id': transaction.transaction_id,
            'state': transaction.state.value,
            'isolation_level': transaction.isolation_level.value,
            'start_time': transaction.start_time,
            'duration': time.time() - transaction.start_time,
            'lock_count': len(transaction.locks),
            'savepoint_count': len(transaction.savepoints),
            'operation_count': len(transaction.operations)
        }
    
    def get_active_transactions(self) -> List[Dict[str, Any]]:
        """获取活跃事务列表"""
        active_transactions = []
        
        for transaction in self.transactions.values():
            if transaction.state == TransactionState.ACTIVE:
                info = self.get_transaction_info(transaction.transaction_id)
                if info:
                    active_transactions.append(info)
        
        return active_transactions
    
    def cleanup_expired_transactions(self):
        """清理过期事务"""
        current_time = time.time()
        expired_transactions = []
        
        for tx_id, transaction in self.transactions.items():
            if current_time - transaction.start_time > transaction.timeout:
                expired_transactions.append(tx_id)
        
        for tx_id in expired_transactions:
            self.rollback_transaction(tx_id)

# 使用示例
def main():
    print("=== 事务管理器 ===")
    
    # 创建事务管理器
    tx_manager = TransactionManager()
    
    # 示例1: 基本事务操作
    print("\n=== 基本事务操作 ===")
    
    with tx_manager.transaction() as tx_id:
        print(f"开始事务: {tx_id}")
        
        # 模拟数据库操作
        time.sleep(0.1)
        
        # 获取锁
        success = tx_manager.lock_manager.acquire_lock(tx_id, "resource1", LockType.EXCLUSIVE)
        print(f"获取锁: {success}")
        
        # 查看事务信息
        info = tx_manager.get_transaction_info(tx_id)
        print(f"事务信息: {info}")
    
    print("事务已提交")
    
    # 示例2: 并发事务测试
    print("\n=== 并发事务测试 ===")
    
    def worker_thread(worker_id: int):
        with tx_manager.transaction() as tx_id:
            print(f"Worker {worker_id} 开始事务: {tx_id}")
            
            # 尝试获取资源锁
            success = tx_manager.lock_manager.acquire_lock(tx_id, "shared_resource", LockType.SHARED)
            print(f"Worker {worker_id} 获取锁: {success}")
            
            if success:
                time.sleep(0.5)  # 模拟工作
                print(f"Worker {worker_id} 完成工作")
            else:
                print(f"Worker {worker_id} 获取锁失败")
    
    # 启动多个线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 示例3: 保存点操作
    print("\n=== 保存点操作 ===")
    
    with tx_manager.transaction() as tx_id:
        print(f"开始事务: {tx_id}")
        
        # 创建保存点
        tx_manager.create_savepoint(tx_id, "savepoint1")
        print("创建保存点: savepoint1")
        
        # 模拟一些操作
        time.sleep(0.1)
        
        # 创建第二个保存点
        tx_manager.create_savepoint(tx_id, "savepoint2")
        print("创建保存点: savepoint2")
        
        # 模拟更多操作
        time.sleep(0.1)
        
        # 回滚到第一个保存点
        success = tx_manager.rollback_to_savepoint(tx_id, "savepoint1")
        print(f"回滚到保存点: {success}")
    
    print("事务已提交")
    
    # 示例4: 查看活跃事务
    print("\n=== 活跃事务信息 ===")
    active_txs = tx_manager.get_active_transactions()
    print(f"活跃事务数量: {len(active_txs)}")
    
    for tx in active_txs:
        print(f"事务 {tx['transaction_id']}: {tx['state']}, 持续时间: {tx['duration']:.2f}s")

if __name__ == '__main__':
    main()
```

### 分布式事务协调器
```python
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

class TransactionPhase(Enum):
    """事务阶段"""
    INITIATING = "initiating"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"

class ParticipantStatus(Enum):
    """参与者状态"""
    READY = "ready"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"
    FAILED = "failed"

@dataclass
class Participant:
    """参与者"""
    participant_id: str
    endpoint: str
    status: ParticipantStatus
    timeout: float
    last_heartbeat: float

@dataclass
class DistributedTransaction:
    """分布式事务"""
    transaction_id: str
    coordinator_id: str
    participants: List[Participant]
    phase: TransactionPhase
    start_time: float
    timeout: float
    operations: List[Dict[str, Any]]

class TwoPhaseCommitCoordinator:
    def __init__(self, coordinator_id: str):
        self.coordinator_id = coordinator_id
        self.transactions: Dict[str, DistributedTransaction] = {}
        self.participant_timeout = 30.0
        self.transaction_timeout = 120.0
    
    async def begin_transaction(self, participants: List[str], operations: List[Dict[str, Any]]) -> str:
        """开始分布式事务"""
        transaction_id = str(uuid.uuid4())
        
        # 创建参与者列表
        participant_objects = []
        for participant_id in participants:
            participant = Participant(
                participant_id=participant_id,
                endpoint=f"http://{participant_id}:8080",
                status=ParticipantStatus.READY,
                timeout=self.participant_timeout,
                last_heartbeat=time.time()
            )
            participant_objects.append(participant)
        
        # 创建分布式事务
        transaction = DistributedTransaction(
            transaction_id=transaction_id,
            coordinator_id=self.coordinator_id,
            participants=participant_objects,
            phase=TransactionPhase.INITIATING,
            start_time=time.time(),
            timeout=self.transaction_timeout,
            operations=operations
        )
        
        self.transactions[transaction_id] = transaction
        
        try:
            # 执行两阶段提交
            success = await self._execute_two_phase_commit(transaction_id)
            
            if success:
                print(f"分布式事务 {transaction_id} 提交成功")
            else:
                print(f"分布式事务 {transaction_id} 提交失败")
            
            return transaction_id
            
        except Exception as e:
            print(f"分布式事务 {transaction_id} 执行异常: {e}")
            await self._abort_transaction(transaction_id)
            return transaction_id
    
    async def _execute_two_phase_commit(self, transaction_id: str) -> bool:
        """执行两阶段提交"""
        transaction = self.transactions[transaction_id]
        
        # 阶段1: 准备阶段
        transaction.phase = TransactionPhase.PREPARING
        
        # 向所有参与者发送准备请求
        prepare_results = await self._send_prepare_requests(transaction_id)
        
        # 检查是否所有参与者都准备成功
        all_prepared = all(result for result in prepare_results)
        
        if all_prepared:
            # 阶段2: 提交阶段
            transaction.phase = TransactionPhase.COMMITTING
            
            # 向所有参与者发送提交请求
            commit_results = await self._send_commit_requests(transaction_id)
            
            # 检查是否所有参与者都提交成功
            all_committed = all(result for result in commit_results)
            
            if all_committed:
                transaction.phase = TransactionPhase.COMMITTED
                return True
            else:
                # 提交失败，需要回滚
                await self._send_abort_requests(transaction_id)
                transaction.phase = TransactionPhase.ABORTED
                return False
        else:
            # 准备失败，中止事务
            await self._send_abort_requests(transaction_id)
            transaction.phase = TransactionPhase.ABORTED
            return False
    
    async def _send_prepare_requests(self, transaction_id: str) -> List[bool]:
        """发送准备请求"""
        transaction = self.transactions[transaction_id]
        results = []
        
        for participant in transaction.participants:
            try:
                # 模拟发送准备请求
                success = await self._prepare_participant(participant, transaction.operations)
                participant.status = ParticipantStatus.PREPARED if success else ParticipantStatus.FAILED
                results.append(success)
                
                if not success:
                    print(f"参与者 {participant.participant_id} 准备失败")
                    
            except Exception as e:
                print(f"参与者 {participant.participant_id} 准备异常: {e}")
                participant.status = ParticipantStatus.FAILED
                results.append(False)
        
        return results
    
    async def _send_commit_requests(self, transaction_id: str) -> List[bool]:
        """发送提交请求"""
        transaction = self.transactions[transaction_id]
        results = []
        
        for participant in transaction.participants:
            try:
                # 模拟发送提交请求
                success = await self._commit_participant(participant)
                participant.status = ParticipantStatus.COMMITTED if success else ParticipantStatus.FAILED
                results.append(success)
                
                if not success:
                    print(f"参与者 {participant.participant_id} 提交失败")
                    
            except Exception as e:
                print(f"参与者 {participant.participant_id} 提交异常: {e}")
                participant.status = ParticipantStatus.FAILED
                results.append(False)
        
        return results
    
    async def _send_abort_requests(self, transaction_id: str):
        """发送中止请求"""
        transaction = self.transactions[transaction_id]
        
        for participant in transaction.participants:
            try:
                # 模拟发送中止请求
                await self._abort_participant(participant)
                participant.status = ParticipantStatus.ABORTED
                
            except Exception as e:
                print(f"参与者 {participant.participant_id} 中止异常: {e}")
                participant.status = ParticipantStatus.FAILED
    
    async def _prepare_participant(self, participant: Participant, operations: List[Dict[str, Any]]) -> bool:
        """准备参与者"""
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        # 模拟准备逻辑
        print(f"准备参与者 {participant.participant_id}")
        return True  # 简化实现，总是返回成功
    
    async def _commit_participant(self, participant: Participant) -> bool:
        """提交参与者"""
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        # 模拟提交逻辑
        print(f"提交参与者 {participant.participant_id}")
        return True  # 简化实现，总是返回成功
    
    async def _abort_participant(self, participant: Participant):
        """中止参与者"""
        # 模拟网络延迟
        await asyncio.sleep(0.1)
        
        # 模拟中止逻辑
        print(f"中止参与者 {participant.participant_id}")
    
    async def _abort_transaction(self, transaction_id: str):
        """中止事务"""
        await self._send_abort_requests(transaction_id)
        
        if transaction_id in self.transactions:
            self.transactions[transaction_id].phase = TransactionPhase.ABORTED
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """获取事务状态"""
        if transaction_id not in self.transactions:
            return None
        
        transaction = self.transactions[transaction_id]
        
        return {
            'transaction_id': transaction.transaction_id,
            'coordinator_id': transaction.coordinator_id,
            'phase': transaction.phase.value,
            'start_time': transaction.start_time,
            'duration': time.time() - transaction.start_time,
            'participant_count': len(transaction.participants),
            'participants': [
                {
                    'participant_id': p.participant_id,
                    'status': p.status.value,
                    'endpoint': p.endpoint
                }
                for p in transaction.participants
            ]
        }
    
    def cleanup_expired_transactions(self):
        """清理过期事务"""
        current_time = time.time()
        expired_transactions = []
        
        for tx_id, transaction in self.transactions.items():
            if current_time - transaction.start_time > transaction.timeout:
                expired_transactions.append(tx_id)
        
        for tx_id in expired_transactions:
            asyncio.create_task(self._abort_transaction(tx_id))

# 使用示例
async def main():
    print("=== 分布式事务协调器 ===")
    
    # 创建协调器
    coordinator = TwoPhaseCommitCoordinator("coordinator1")
    
    # 示例操作
    operations = [
        {"operation": "transfer", "from": "account1", "to": "account2", "amount": 100},
        {"operation": "update", "table": "inventory", "item": "item1", "quantity": -1}
    ]
    
    # 执行分布式事务
    participants = ["participant1", "participant2", "participant3"]
    
    print("开始分布式事务...")
    transaction_id = await coordinator.begin_transaction(participants, operations)
    
    # 查看事务状态
    status = coordinator.get_transaction_status(transaction_id)
    print(f"事务状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # 等待事务完成
    await asyncio.sleep(1)
    
    # 再次查看事务状态
    status = coordinator.get_transaction_status(transaction_id)
    print(f"最终事务状态: {json.dumps(status, indent=2, ensure_ascii=False)}")

if __name__ == '__main__':
    asyncio.run(main())
```

## 事务管理最佳实践

### 事务设计原则
1. **保持简短**: 事务应该尽可能短小，减少锁持有时间
2. **避免用户交互**: 事务中不应包含用户交互操作
3. **合理隔离级别**: 根据业务需求选择合适的隔离级别
4. **错误处理**: 完善的错误处理和回滚机制
5. **资源管理**: 及时释放事务占用的资源

### 并发控制策略
1. **乐观并发控制**: 适用于冲突较少的场景
2. **悲观并发控制**: 适用于冲突较多的场景
3. **混合策略**: 根据操作类型选择不同策略
4. **死锁预防**: 统一锁获取顺序，避免循环等待
5. **超时机制**: 设置合理的锁超时时间

### 分布式事务处理
1. **两阶段提交**: 保证强一致性
2. **三阶段提交**: 减少阻塞时间
3. **补偿事务**: 实现最终一致性
4. **Saga模式**: 长事务拆分为短事务
5. **消息队列**: 异步事务协调

### 性能优化方法
1. **批量操作**: 减少事务数量
2. **连接池**: 复用数据库连接
3. **读写分离**: 分散读写压力
4. **缓存策略**: 减少数据库访问
5. **监控调优**: 实时监控性能指标

## 相关技能

- **sql-optimization** - SQL优化与索引
- **nosql-databases** - NoSQL数据库应用
- **backup-recovery** - 备份与恢复
- **migration-validator** - 迁移验证
