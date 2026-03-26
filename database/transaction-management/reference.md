# 数据库事务管理参考文档

## 事务管理概述

### 什么是事务管理
事务管理是数据库系统中确保数据一致性和完整性的核心机制。事务是一组原子性的操作序列，这些操作要么全部成功执行，要么全部失败回滚。事务管理器负责协调和控制事务的执行，包括事务的开始、提交、回滚等操作。在分布式系统中，事务管理还需要处理跨多个资源管理器的协调问题，确保分布式事务的ACID特性。

### 主要功能
- **事务生命周期管理**: 管理事务的开始、提交、回滚等生命周期
- **隔离级别控制**: 提供不同的事务隔离级别，控制并发事务之间的可见性
- **分布式事务协调**: 支持分布式事务的协调和管理
- **事务监控和日志**: 提供事务执行的监控、日志记录和分析功能
- **异常处理和回滚**: 处理事务执行过程中的异常，确保数据一致性
- **性能优化**: 优化事务执行性能，减少锁等待和死锁

## 事务管理核心

### 事务管理器
```python
# transaction_manager.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import datetime
import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import math
import mysql.connector
import psycopg2
import cx_Oracle
import pyodbc
from contextlib import contextmanager
import subprocess
import tempfile
import csv
import xml.etree.ElementTree as ET

class TransactionIsolationLevel(Enum):
    """事务隔离级别枚举"""
    READ_UNCOMMITTED = "READ_UNCOMMITTED"
    READ_COMMITTED = "READ_COMMITTED"
    REPEATABLE_READ = "REPEATABLE_READ"
    SERIALIZABLE = "SERIALIZABLE"

class PropagationBehavior(Enum):
    """事务传播行为枚举"""
    REQUIRED = "REQUIRED"
    REQUIRES_NEW = "REQUIRES_NEW"
    MANDATORY = "MANDATORY"
    SUPPORTS = "SUPPORTS"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    NEVER = "NEVER"
    NESTED = "NESTED"

class TransactionStatus(Enum):
    """事务状态枚举"""
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"

@dataclass
class TransactionDefinition:
    """事务定义"""
    transaction_id: str
    name: str
    isolation_level: TransactionIsolationLevel
    propagation_behavior: PropagationBehavior
    timeout: int = 30
    read_only: bool = False
    rollback_for: List[Type[Exception]] = field(default_factory=list)
    no_rollback_for: List[Type[Exception]] = field(default_factory=list)

@dataclass
class TransactionContext:
    """事务上下文"""
    transaction_id: str
    status: TransactionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    connection: Any = None
    savepoints: List[str] = field(default_factory=list)
    parent_transaction: Optional[str] = None
    child_transactions: List[str] = field(default_factory=list)

@dataclass
class TransactionLog:
    """事务日志"""
    log_id: str
    transaction_id: str
    operation: str
    timestamp: datetime
    details: Dict[str, Any]
    status: str
    error_message: Optional[str] = None

class DatabaseConnector:
    """数据库连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.database_type = DatabaseType(config.get('type', 'mysql'))
    
    def connect(self):
        """连接数据库"""
        try:
            if self.database_type == DatabaseType.MYSQL:
                self._connect_mysql()
            elif self.database_type == DatabaseType.POSTGRESQL:
                self._connect_postgresql()
            elif self.database_type == DatabaseType.ORACLE:
                self._connect_oracle()
            elif self.database_type == DatabaseType.SQLSERVER:
                self._connect_sqlserver()
            else:
                raise ValueError(f"不支持的数据库类型: {self.database_type}")
            
            self.logger.info(f"数据库连接成功")
        
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise
    
    def _connect_mysql(self):
        """连接MySQL"""
        self.connection = mysql.connector.connect(
            host=self.config.get('host'),
            port=self.config.get('port', 3306),
            user=self.config.get('username'),
            password=self.config.get('password'),
            database=self.config.get('database'),
            charset=self.config.get('charset', 'utf8mb4'),
            connect_timeout=self.config.get('timeout', 30)
        )
    
    def _connect_postgresql(self):
        """连接PostgreSQL"""
        self.connection = psycopg2.connect(
            host=self.config.get('host'),
            port=self.config.get('port', 5432),
            user=self.config.get('username'),
            password=self.config.get('password'),
            database=self.config.get('database'),
            connect_timeout=self.config.get('timeout', 30)
        )
    
    def _connect_oracle(self):
        """连接Oracle"""
        dsn = cx_Oracle.makedsn(
            self.config.get('host'), 
            self.config.get('port', 1521), 
            self.config.get('database')
        )
        self.connection = cx_Oracle.connect(
            user=self.config.get('username'),
            password=self.config.get('password'),
            dsn=dsn
        )
    
    def _connect_sqlserver(self):
        """连接SQL Server"""
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.get('host')},{self.config.get('port', 1433)};DATABASE={self.config.get('database')};UID={self.config.get('username')};PWD={self.config.get('password')}"
        self.connection = pyodbc.connect(connection_string)
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def begin_transaction(self, isolation_level: TransactionIsolationLevel):
        """开始事务"""
        try:
            if self.database_type == DatabaseType.MYSQL:
                self._mysql_begin_transaction(isolation_level)
            elif self.database_type == DatabaseType.POSTGRESQL:
                self._postgresql_begin_transaction(isolation_level)
            elif self.database_type == DatabaseType.ORACLE:
                self._oracle_begin_transaction(isolation_level)
            elif self.database_type == DatabaseType.SQLSERVER:
                self._sqlserver_begin_transaction(isolation_level)
            
            self.logger.info(f"事务开始，隔离级别: {isolation_level.value}")
        
        except Exception as e:
            self.logger.error(f"开始事务失败: {e}")
            raise
    
    def _mysql_begin_transaction(self, isolation_level: TransactionIsolationLevel):
        """MySQL开始事务"""
        isolation_mapping = {
            TransactionIsolationLevel.READ_UNCOMMITTED: "READ UNCOMMITTED",
            TransactionIsolationLevel.READ_COMMITTED: "READ COMMITTED",
            TransactionIsolationLevel.REPEATABLE_READ: "REPEATABLE READ",
            TransactionIsolationLevel.SERIALIZABLE: "SERIALIZABLE"
        }
        
        cursor = self.connection.cursor()
        cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_mapping[isolation_level]}")
        cursor.execute("START TRANSACTION")
        cursor.close()
    
    def _postgresql_begin_transaction(self, isolation_level: TransactionIsolationLevel):
        """PostgreSQL开始事务"""
        isolation_mapping = {
            TransactionIsolationLevel.READ_UNCOMMITTED: "READ UNCOMMITTED",
            TransactionIsolationLevel.READ_COMMITTED: "READ COMMITTED",
            TransactionIsolationLevel.REPEATABLE_READ: "REPEATABLE READ",
            TransactionIsolationLevel.SERIALIZABLE: "SERIALIZABLE"
        }
        
        cursor = self.connection.cursor()
        cursor.execute(f"BEGIN TRANSACTION ISOLATION LEVEL {isolation_mapping[isolation_level]}")
        cursor.close()
    
    def _oracle_begin_transaction(self, isolation_level: TransactionIsolationLevel):
        """Oracle开始事务"""
        # Oracle默认使用READ COMMITTED隔离级别
        cursor = self.connection.cursor()
        cursor.execute("SET TRANSACTION")
        cursor.close()
    
    def _sqlserver_begin_transaction(self, isolation_level: TransactionIsolationLevel):
        """SQL Server开始事务"""
        isolation_mapping = {
            TransactionIsolationLevel.READ_UNCOMMITTED: "READ UNCOMMITTED",
            TransactionIsolationLevel.READ_COMMITTED: "READ COMMITTED",
            TransactionIsolationLevel.REPEATABLE_READ: "REPEATABLE READ",
            TransactionIsolationLevel.SERIALIZABLE: "SERIALIZABLE"
        }
        
        cursor = self.connection.cursor()
        cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_mapping[isolation_level]}")
        cursor.execute("BEGIN TRANSACTION")
        cursor.close()
    
    def commit_transaction(self):
        """提交事务"""
        try:
            self.connection.commit()
            self.logger.info("事务提交成功")
        
        except Exception as e:
            self.logger.error(f"事务提交失败: {e}")
            raise
    
    def rollback_transaction(self):
        """回滚事务"""
        try:
            self.connection.rollback()
            self.logger.info("事务回滚成功")
        
        except Exception as e:
            self.logger.error(f"事务回滚失败: {e}")
            raise
    
    def create_savepoint(self, name: str):
        """创建保存点"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SAVEPOINT {name}")
            cursor.close()
            self.logger.info(f"保存点创建成功: {name}")
        
        except Exception as e:
            self.logger.error(f"创建保存点失败: {e}")
            raise
    
    def rollback_to_savepoint(self, name: str):
        """回滚到保存点"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")
            cursor.close()
            self.logger.info(f"回滚到保存点成功: {name}")
        
        except Exception as e:
            self.logger.error(f"回滚到保存点失败: {e}")
            raise
    
    def release_savepoint(self, name: str):
        """释放保存点"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"RELEASE SAVEPOINT {name}")
            cursor.close()
            self.logger.info(f"保存点释放成功: {name}")
        
        except Exception as e:
            self.logger.error(f"释放保存点失败: {e}")
            raise

class TransactionManager:
    """事务管理器"""
    
    def __init__(self, database_config: Dict[str, Any]):
        self.database_config = database_config
        self.logger = logging.getLogger(__name__)
        self.connector = DatabaseConnector(database_config)
        self.active_transactions: Dict[str, TransactionContext] = {}
        self.transaction_logs: List[TransactionLog] = []
        self.lock = threading.Lock()
        
    def initialize(self):
        """初始化事务管理器"""
        try:
            self.connector.connect()
            self.logger.info("事务管理器初始化成功")
        
        except Exception as e:
            self.logger.error(f"事务管理器初始化失败: {e}")
            raise
    
    def begin_transaction(self, definition: TransactionDefinition) -> str:
        """开始事务"""
        try:
            with self.lock:
                # 检查是否已有活动事务
                current_transaction = self._get_current_transaction()
                
                # 处理传播行为
                if current_transaction:
                    return self._handle_propagation(current_transaction, definition)
                else:
                    return self._create_new_transaction(definition)
        
        except Exception as e:
            self.logger.error(f"开始事务失败: {e}")
            raise
    
    def _get_current_transaction(self) -> Optional[TransactionContext]:
        """获取当前线程的事务"""
        current_thread = threading.current_thread()
        thread_id = current_thread.ident
        
        for transaction_id, context in self.active_transactions.items():
            if hasattr(context, 'thread_id') and context.thread_id == thread_id:
                return context
        
        return None
    
    def _handle_propagation(self, current_transaction: TransactionContext, 
                           definition: TransactionDefinition) -> str:
        """处理事务传播"""
        if definition.propagation_behavior == PropagationBehavior.REQUIRED:
            # 加入现有事务
            return current_transaction.transaction_id
        
        elif definition.propagation_behavior == PropagationBehavior.REQUIRES_NEW:
            # 创建新事务
            return self._create_new_transaction(definition)
        
        elif definition.propagation_behavior == PropagationBehavior.MANDATORY:
            # 必须在事务中
            return current_transaction.transaction_id
        
        elif definition.propagation_behavior == PropagationBehavior.NESTED:
            # 创建嵌套事务
            return self._create_nested_transaction(current_transaction, definition)
        
        else:
            # 其他传播行为
            return current_transaction.transaction_id
    
    def _create_new_transaction(self, definition: TransactionDefinition) -> str:
        """创建新事务"""
        transaction_id = str(uuid.uuid4())
        
        # 创建事务上下文
        context = TransactionContext(
            transaction_id=transaction_id,
            status=TransactionStatus.ACTIVE,
            start_time=datetime.now(),
            connection=self.connector.connection,
            thread_id=threading.current_thread().ident
        )
        
        # 开始数据库事务
        self.connector.begin_transaction(definition.isolation_level)
        
        # 添加到活动事务
        self.active_transactions[transaction_id] = context
        
        # 记录日志
        self._log_transaction_operation(transaction_id, "BEGIN", {
            'isolation_level': definition.isolation_level.value,
            'propagation_behavior': definition.propagation_behavior.value,
            'timeout': definition.timeout,
            'read_only': definition.read_only
        })
        
        self.logger.info(f"新事务创建成功: {transaction_id}")
        
        return transaction_id
    
    def _create_nested_transaction(self, parent_transaction: TransactionContext, 
                                 definition: TransactionDefinition) -> str:
        """创建嵌套事务"""
        transaction_id = str(uuid.uuid4())
        savepoint_name = f"sp_{transaction_id[:8]}"
        
        # 创建保存点
        self.connector.create_savepoint(savepoint_name)
        
        # 创建嵌套事务上下文
        context = TransactionContext(
            transaction_id=transaction_id,
            status=TransactionStatus.ACTIVE,
            start_time=datetime.now(),
            connection=parent_transaction.connection,
            parent_transaction=parent_transaction.transaction_id,
            thread_id=threading.current_thread().ident
        )
        
        # 添加保存点
        context.savepoints.append(savepoint_name)
        
        # 添加到活动事务
        self.active_transactions[transaction_id] = context
        
        # 更新父事务的子事务列表
        parent_transaction.child_transactions.append(transaction_id)
        
        # 记录日志
        self._log_transaction_operation(transaction_id, "BEGIN_NESTED", {
            'parent_transaction': parent_transaction.transaction_id,
            'savepoint': savepoint_name
        })
        
        self.logger.info(f"嵌套事务创建成功: {transaction_id}")
        
        return transaction_id
    
    def commit_transaction(self, transaction_id: str):
        """提交事务"""
        try:
            with self.lock:
                context = self.active_transactions.get(transaction_id)
                if not context:
                    raise ValueError(f"事务不存在: {transaction_id}")
                
                if context.parent_transaction:
                    # 嵌套事务：释放保存点
                    if context.savepoints:
                        savepoint_name = context.savepoints[-1]
                        self.connector.release_savepoint(savepoint_name)
                    
                    # 更新父事务
                    parent_context = self.active_transactions.get(context.parent_transaction)
                    if parent_context:
                        parent_context.child_transactions.remove(transaction_id)
                    
                    # 更新状态
                    context.status = TransactionStatus.COMMITTED
                    context.end_time = datetime.now()
                    
                    # 记录日志
                    self._log_transaction_operation(transaction_id, "COMMIT_NESTED", {
                        'parent_transaction': context.parent_transaction,
                        'savepoint': context.savepoints[-1] if context.savepoints else None
                    })
                    
                else:
                    # 根事务：提交数据库事务
                    self.connector.commit_transaction()
                    
                    # 更新状态
                    context.status = TransactionStatus.COMMITTED
                    context.end_time = datetime.now()
                    
                    # 记录日志
                    self._log_transaction_operation(transaction_id, "COMMIT_ROOT", {
                        'duration': (context.end_time - context.start_time).total_seconds()
                    })
                
                # 移除活动事务
                del self.active_transactions[transaction_id]
                
                self.logger.info(f"事务提交成功: {transaction_id}")
        
        except Exception as e:
            self.logger.error(f"事务提交失败: {transaction_id}, {e}")
            raise
    
    def rollback_transaction(self, transaction_id: str):
        """回滚事务"""
        try:
            with self.lock:
                context = self.active_transactions.get(transaction_id)
                if not context:
                    raise ValueError(f"事务不存在: {transaction_id}")
                
                if context.parent_transaction:
                    # 嵌套事务：回滚到保存点
                    if context.savepoints:
                        savepoint_name = context.savepoints[-1]
                        self.connector.rollback_to_savepoint(savepoint_name)
                    
                    # 更新父事务
                    parent_context = self.active_transactions.get(context.parent_transaction)
                    if parent_context:
                        parent_context.child_transactions.remove(transaction_id)
                    
                    # 更新状态
                    context.status = TransactionStatus.ROLLED_BACK
                    context.end_time = datetime.now()
                    
                    # 记录日志
                    self._log_transaction_operation(transaction_id, "ROLLBACK_NESTED", {
                        'parent_transaction': context.parent_transaction,
                        'savepoint': context.savepoints[-1] if context.savepoints else None
                    })
                    
                else:
                    # 根事务：回滚数据库事务
                    self.connector.rollback_transaction()
                    
                    # 更新状态
                    context.status = TransactionStatus.ROLLED_BACK
                    context.end_time = datetime.now()
                    
                    # 记录日志
                    self._log_transaction_operation(transaction_id, "ROLLBACK_ROOT", {
                        'duration': (context.end_time - context.start_time).total_seconds()
                    })
                
                # 移除活动事务
                del self.active_transactions[transaction_id]
                
                self.logger.info(f"事务回滚成功: {transaction_id}")
        
        except Exception as e:
            self.logger.error(f"事务回滚失败: {transaction_id}, {e}")
            raise
    
    def get_transaction_status(self, transaction_id: str) -> Optional[TransactionStatus]:
        """获取事务状态"""
        context = self.active_transactions.get(transaction_id)
        if context:
            return context.status
        
        # 检查日志中的历史事务
        for log in reversed(self.transaction_logs):
            if log.transaction_id == transaction_id:
                if log.operation == "COMMIT_ROOT" or log.operation == "COMMIT_NESTED":
                    return TransactionStatus.COMMITTED
                elif log.operation == "ROLLBACK_ROOT" or log.operation == "ROLLBACK_NESTED":
                    return TransactionStatus.ROLLED_BACK
        
        return None
    
    def get_active_transactions(self) -> List[str]:
        """获取活动事务列表"""
        return list(self.active_transactions.keys())
    
    def _log_transaction_operation(self, transaction_id: str, operation: str, 
                                  details: Dict[str, Any], error_message: Optional[str] = None):
        """记录事务操作日志"""
        log = TransactionLog(
            log_id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            operation=operation,
            timestamp=datetime.now(),
            details=details,
            status="SUCCESS" if not error_message else "ERROR",
            error_message=error_message
        )
        
        self.transaction_logs.append(log)
    
    def get_transaction_logs(self, transaction_id: Optional[str] = None, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> List[TransactionLog]:
        """获取事务日志"""
        logs = self.transaction_logs
        
        # 过滤事务ID
        if transaction_id:
            logs = [log for log in logs if log.transaction_id == transaction_id]
        
        # 过滤时间范围
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        return logs
    
    def cleanup(self):
        """清理资源"""
        try:
            # 回滚所有活动事务
            for transaction_id in list(self.active_transactions.keys()):
                try:
                    self.rollback_transaction(transaction_id)
                except Exception as e:
                    self.logger.error(f"清理事务失败: {transaction_id}, {e}")
            
            # 断开数据库连接
            self.connector.disconnect()
            
            self.logger.info("事务管理器清理完成")
        
        except Exception as e:
            self.logger.error(f"事务管理器清理失败: {e}")

class DistributedTransactionManager:
    """分布式事务管理器"""
    
    def __init__(self, participants: List[Dict[str, Any]]):
        self.participants = participants
        self.logger = logging.getLogger(__name__)
        self.coordinator = None
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def initialize(self):
        """初始化分布式事务管理器"""
        try:
            # 初始化参与者
            for participant in self.participants:
                participant['manager'] = TransactionManager(participant['config'])
                participant['manager'].initialize()
            
            self.logger.info("分布式事务管理器初始化成功")
        
        except Exception as e:
            self.logger.error(f"分布式事务管理器初始化失败: {e}")
            raise
    
    def begin_distributed_transaction(self, definition: TransactionDefinition) -> str:
        """开始分布式事务"""
        try:
            transaction_id = str(uuid.uuid4())
            
            with self.lock:
                # 在所有参与者上开始事务
                participant_transactions = {}
                
                for participant in self.participants:
                    participant_id = participant['id']
                    manager = participant['manager']
                    
                    # 开始本地事务
                    local_transaction_id = manager.begin_transaction(definition)
                    participant_transactions[participant_id] = local_transaction_id
                
                # 记录分布式事务
                self.active_transactions[transaction_id] = {
                    'status': 'ACTIVE',
                    'start_time': datetime.now(),
                    'participants': participant_transactions,
                    'phase': 'PREPARE'
                }
            
            self.logger.info(f"分布式事务开始成功: {transaction_id}")
            
            return transaction_id
        
        except Exception as e:
            self.logger.error(f"开始分布式事务失败: {e}")
            raise
    
    def commit_distributed_transaction(self, transaction_id: str):
        """提交分布式事务"""
        try:
            with self.lock:
                transaction_info = self.active_transactions.get(transaction_id)
                if not transaction_info:
                    raise ValueError(f"分布式事务不存在: {transaction_id}")
                
                # 两阶段提交
                if self._two_phase_commit(transaction_id, transaction_info):
                    # 提交成功
                    transaction_info['status'] = 'COMMITTED'
                    transaction_info['end_time'] = datetime.now()
                    del self.active_transactions[transaction_id]
                    
                    self.logger.info(f"分布式事务提交成功: {transaction_id}")
                else:
                    # 提交失败，回滚
                    self.rollback_distributed_transaction(transaction_id)
                    raise Exception("分布式事务提交失败")
        
        except Exception as e:
            self.logger.error(f"分布式事务提交失败: {transaction_id}, {e}")
            raise
    
    def rollback_distributed_transaction(self, transaction_id: str):
        """回滚分布式事务"""
        try:
            with self.lock:
                transaction_info = self.active_transactions.get(transaction_id)
                if not transaction_info:
                    raise ValueError(f"分布式事务不存在: {transaction_id}")
                
                # 回滚所有参与者
                participant_transactions = transaction_info['participants']
                
                for participant in self.participants:
                    participant_id = participant['id']
                    manager = participant['manager']
                    
                    if participant_id in participant_transactions:
                        local_transaction_id = participant_transactions[participant_id]
                        try:
                            manager.rollback_transaction(local_transaction_id)
                        except Exception as e:
                            self.logger.error(f"回滚参与者事务失败: {participant_id}, {e}")
                
                # 更新状态
                transaction_info['status'] = 'ROLLED_BACK'
                transaction_info['end_time'] = datetime.now()
                del self.active_transactions[transaction_id]
                
                self.logger.info(f"分布式事务回滚成功: {transaction_id}")
        
        except Exception as e:
            self.logger.error(f"分布式事务回滚失败: {transaction_id}, {e}")
            raise
    
    def _two_phase_commit(self, transaction_id: str, transaction_info: Dict[str, Any]) -> bool:
        """两阶段提交"""
        try:
            participant_transactions = transaction_info['participants']
            
            # 第一阶段：准备阶段
            prepared_participants = []
            
            for participant in self.participants:
                participant_id = participant['id']
                manager = participant['manager']
                
                if participant_id in participant_transactions:
                    local_transaction_id = participant_transactions[participant_id]
                    
                    try:
                        # 检查事务状态
                        status = manager.get_transaction_status(local_transaction_id)
                        if status == TransactionStatus.ACTIVE:
                            prepared_participants.append(participant_id)
                        else:
                            self.logger.error(f"参与者事务状态异常: {participant_id}, {status}")
                            return False
                    except Exception as e:
                        self.logger.error(f"检查参与者事务状态失败: {participant_id}, {e}")
                        return False
            
            # 第二阶段：提交阶段
            for participant in self.participants:
                participant_id = participant['id']
                manager = participant['manager']
                
                if participant_id in prepared_participants:
                    local_transaction_id = participant_transactions[participant_id]
                    
                    try:
                        manager.commit_transaction(local_transaction_id)
                    except Exception as e:
                        self.logger.error(f"提交参与者事务失败: {participant_id}, {e}")
                        return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"两阶段提交失败: {e}")
            return False
    
    def get_distributed_transaction_status(self, transaction_id: str) -> Optional[str]:
        """获取分布式事务状态"""
        transaction_info = self.active_transactions.get(transaction_id)
        if transaction_info:
            return transaction_info['status']
        
        return None
    
    def get_active_distributed_transactions(self) -> List[str]:
        """获取活动分布式事务列表"""
        return list(self.active_transactions.keys())
    
    def cleanup(self):
        """清理资源"""
        try:
            # 回滚所有活动分布式事务
            for transaction_id in list(self.active_transactions.keys()):
                try:
                    self.rollback_distributed_transaction(transaction_id)
                except Exception as e:
                    self.logger.error(f"清理分布式事务失败: {transaction_id}, {e}")
            
            # 清理参与者
            for participant in self.participants:
                manager = participant.get('manager')
                if manager:
                    manager.cleanup()
            
            self.logger.info("分布式事务管理器清理完成")
        
        except Exception as e:
            self.logger.error(f"分布式事务管理器清理失败: {e}")

class TransactionMonitor:
    """事务监控器"""
    
    def __init__(self, transaction_manager: Union[TransactionManager, DistributedTransactionManager]):
        self.transaction_manager = transaction_manager
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        self.metrics = defaultdict(int)
        self.metrics_lock = threading.Lock()
    
    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        try:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info("事务监控启动成功")
        
        except Exception as e:
            self.logger.error(f"事务监控启动失败: {e}")
            raise
    
    def stop_monitoring(self):
        """停止监控"""
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=10)
            
            self.logger.info("事务监控停止成功")
        
        except Exception as e:
            self.logger.error(f"事务监控停止失败: {e}")
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.monitoring:
            try:
                self._collect_metrics()
                time.sleep(interval)
            
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self):
        """收集指标"""
        try:
            with self.metrics_lock:
                # 获取活动事务数量
                if isinstance(self.transaction_manager, TransactionManager):
                    active_transactions = self.transaction_manager.get_active_transactions()
                else:
                    active_transactions = self.transaction_manager.get_active_distributed_transactions()
                
                self.metrics['active_transactions'] = len(active_transactions)
                
                # 获取事务日志统计
                if isinstance(self.transaction_manager, TransactionManager):
                    logs = self.transaction_manager.get_transaction_logs()
                    
                    # 统计事务操作
                    operation_counts = defaultdict(int)
                    for log in logs:
                        operation_counts[log.operation] += 1
                    
                    self.metrics['total_transactions'] = operation_counts.get('BEGIN', 0)
                    self.metrics['committed_transactions'] = operation_counts.get('COMMIT_ROOT', 0)
                    self.metrics['rolled_back_transactions'] = operation_counts.get('ROLLBACK_ROOT', 0)
                    self.metrics['failed_transactions'] = operation_counts.get('ERROR', 0)
                
                # 记录监控日志
                self.logger.info(f"事务监控指标: {dict(self.metrics)}")
        
        except Exception as e:
            self.logger.error(f"收集监控指标失败: {e}")
    
    def get_metrics(self) -> Dict[str, int]:
        """获取监控指标"""
        with self.metrics_lock:
            return dict(self.metrics)
    
    def get_transaction_statistics(self, start_time: Optional[datetime] = None,
                                  end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """获取事务统计信息"""
        try:
            if isinstance(self.transaction_manager, TransactionManager):
                logs = self.transaction_manager.get_transaction_logs(
                    start_time=start_time, end_time=end_time
                )
                
                # 统计分析
                total_transactions = len([log for log in logs if log.operation == 'BEGIN'])
                committed_transactions = len([log for log in logs if log.operation == 'COMMIT_ROOT'])
                rolled_back_transactions = len([log for log in logs if log.operation == 'ROLLBACK_ROOT'])
                failed_transactions = len([log for log in logs if log.status == 'ERROR'])
                
                # 计算执行时间统计
                execution_times = []
                for log in logs:
                    if log.operation in ['COMMIT_ROOT', 'ROLLBACK_ROOT']:
                        duration = log.details.get('duration', 0)
                        if duration > 0:
                            execution_times.append(duration)
                
                avg_execution_time = statistics.mean(execution_times) if execution_times else 0
                max_execution_time = max(execution_times) if execution_times else 0
                min_execution_time = min(execution_times) if execution_times else 0
                
                return {
                    'total_transactions': total_transactions,
                    'committed_transactions': committed_transactions,
                    'rolled_back_transactions': rolled_back_transactions,
                    'failed_transactions': failed_transactions,
                    'success_rate': (committed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
                    'avg_execution_time': avg_execution_time,
                    'max_execution_time': max_execution_time,
                    'min_execution_time': min_execution_time
                }
            
            return {}
        
        except Exception as e:
            self.logger.error(f"获取事务统计信息失败: {e}")
            return {}

# 使用示例
# 本地事务管理
database_config = {
    'type': 'mysql',
    'host': 'localhost',
    'port': 3306,
    'username': 'root',
    'password': 'password',
    'database': 'test_db'
}

# 创建事务管理器
transaction_manager = TransactionManager(database_config)
transaction_manager.initialize()

# 创建事务定义
transaction_def = TransactionDefinition(
    transaction_id=str(uuid.uuid4()),
    name="sample_transaction",
    isolation_level=TransactionIsolationLevel.READ_COMMITTED,
    propagation_behavior=PropagationBehavior.REQUIRED,
    timeout=30,
    read_only=False
)

# 开始事务
transaction_id = transaction_manager.begin_transaction(transaction_def)
print(f"事务开始: {transaction_id}")

try:
    # 执行业务逻辑
    # 这里可以执行数据库操作
    
    # 提交事务
    transaction_manager.commit_transaction(transaction_id)
    print("事务提交成功")
    
except Exception as e:
    # 回滚事务
    transaction_manager.rollback_transaction(transaction_id)
    print(f"事务回滚: {e}")

# 获取事务状态
status = transaction_manager.get_transaction_status(transaction_id)
print(f"事务状态: {status}")

# 获取事务统计
logs = transaction_manager.get_transaction_logs()
print(f"事务日志数量: {len(logs)}")

# 启动监控
monitor = TransactionMonitor(transaction_manager)
monitor.start_monitoring(interval=30)

# 获取监控指标
metrics = monitor.get_metrics()
print(f"监控指标: {metrics}")

# 获取统计信息
stats = monitor.get_transaction_statistics()
print(f"统计信息: {stats}")

# 清理资源
monitor.stop_monitoring()
transaction_manager.cleanup()

# 分布式事务管理
participants = [
    {
        'id': 'db1',
        'config': {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'username': 'root',
            'password': 'password',
            'database': 'db1'
        }
    },
    {
        'id': 'db2',
        'config': {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'username': 'postgres',
            'password': 'password',
            'database': 'db2'
        }
    }
]

# 创建分布式事务管理器
distributed_manager = DistributedTransactionManager(participants)
distributed_manager.initialize()

# 开始分布式事务
distributed_transaction_id = distributed_manager.begin_distributed_transaction(transaction_def)
print(f"分布式事务开始: {distributed_transaction_id}")

try:
    # 执行分布式业务逻辑
    # 这里可以在多个数据库上执行操作
    
    # 提交分布式事务
    distributed_manager.commit_distributed_transaction(distributed_transaction_id)
    print("分布式事务提交成功")
    
except Exception as e:
    # 回滚分布式事务
    distributed_manager.rollback_distributed_transaction(distributed_transaction_id)
    print(f"分布式事务回滚: {e}")

# 清理资源
distributed_manager.cleanup()
```

## 参考资源

### 事务管理文档
- [MySQL事务管理](https://dev.mysql.com/doc/refman/8.0/en/commit.html)
- [PostgreSQL事务管理](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [Oracle事务管理](https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/transactions.html)
- [SQL Server事务管理](https://docs.microsoft.com/en-us/sql/t-sql/language-elements/transactions-transact-sql)

### 分布式事务
- [两阶段提交协议](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
- [三阶段提交协议](https://en.wikipedia.org/wiki/Three-phase_commit_protocol)
- [TCC模式](https://www.infoq.cn/article/2019/09/tcc-transaction-pattern)
- [Saga模式](https://microservices.io/patterns/data/saga.html)

### 事务隔离级别
- [ACID特性](https://en.wikipedia.org/wiki/ACID)
- [隔离级别详解](https://en.wikipedia.org/wiki/Isolation_(database_systems))
- [并发控制](https://en.wikipedia.org/wiki/Concurrency_control)
- [锁机制](https://en.wikipedia.org/wiki/Lock_(database))

### 最佳实践
- [事务设计模式](https://martinfowler.com/eaaCatalog/unitOfWork.html)
- [分布式事务最佳实践](https://docs.microsoft.com/en-us/azure/architecture/patterns/category/data-consistency)
- [Spring事务管理](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction)
- [性能优化指南](https://www.percona.com/blog/2019/10/07/transaction-scope-and-performance/)
