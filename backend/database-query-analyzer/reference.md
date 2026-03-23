# 数据库查询分析器参考文档

## 数据库查询分析器概述

### 什么是数据库查询分析器
数据库查询分析器是一个专业的数据库性能监控和优化工具，用于捕获、分析、优化数据库查询语句。该工具支持多种数据库类型（MySQL、PostgreSQL、MongoDB、Redis等），提供实时查询监控、性能分析、索引优化建议、查询模式识别等功能，帮助数据库管理员和开发人员识别性能瓶颈、优化查询语句、提升数据库性能。

### 主要功能
- **查询捕获**: 支持从应用日志、数据库日志、网络流量等多种源头捕获查询语句
- **性能分析**: 提供执行时间、资源使用、锁等待等多维度性能分析
- **查询优化**: 包含索引分析、执行计划分析、查询重写建议等优化功能
- **模式识别**: 识别查询模式、异常查询、趋势分析等智能分析
- **报告生成**: 生成性能报告、优化报告、安全报告等多种报告类型
- **告警监控**: 提供实时告警、阈值监控、多渠道通知等监控功能

## 数据库查询分析器核心

### 查询分析引擎
```python
# database_query_analyzer.py
import json
import re
import time
import uuid
import logging
import threading
import queue
import hashlib
import sqlite3
import psycopg2
import pymongo
import redis
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import statistics
import math
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"

class QueryType(Enum):
    """查询类型枚举"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    INDEX = "INDEX"
    UNKNOWN = "UNKNOWN"

class AnalysisType(Enum):
    """分析类型枚举"""
    PERFORMANCE = "performance"
    OPTIMIZATION = "optimization"
    PATTERN = "pattern"
    SECURITY = "security"
    TREND = "trend"

@dataclass
class DatabaseConnection:
    """数据库连接配置"""
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    connection_timeout: int = 30
    max_connections: int = 10
    min_connections: int = 1
    idle_timeout: int = 300

@dataclass
class QueryMetrics:
    """查询指标"""
    query_id: str
    query_text: str
    query_type: QueryType
    execution_time: float
    rows_examined: int
    rows_returned: int
    cpu_usage: float
    memory_usage: float
    disk_io: float
    lock_wait_time: float
    timestamp: datetime
    database: str
    user: str
    host: str
    error_message: Optional[str] = None

@dataclass
class IndexRecommendation:
    """索引建议"""
    table_name: str
    column_names: List[str]
    index_type: str
    estimated_improvement: float
    reason: str
    priority: str

@dataclass
class QueryPattern:
    """查询模式"""
    pattern_id: str
    pattern_type: str
    query_template: str
    frequency: int
    avg_execution_time: float
    similarity_threshold: float
    queries: List[QueryMetrics] = field(default_factory=list)

@dataclass
class PerformanceAlert:
    """性能告警"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    query_id: str
    threshold: float
    actual_value: float
    timestamp: datetime
    resolved: bool = False

class DatabaseConnector:
    """数据库连接器"""
    
    def __init__(self, config: DatabaseConnection):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection_pool = []
        self.lock = threading.Lock()
    
    def get_connection(self):
        """获取数据库连接"""
        with self.lock:
            if self.connection_pool:
                return self.connection_pool.pop()
            return self._create_connection()
    
    def return_connection(self, connection):
        """归还数据库连接"""
        with self.lock:
            if len(self.connection_pool) < self.config.max_connections:
                self.connection_pool.append(connection)
            else:
                self._close_connection(connection)
    
    def _create_connection(self):
        """创建新连接"""
        try:
            if self.config.db_type == DatabaseType.MYSQL:
                import pymysql
                return pymysql.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    connect_timeout=self.config.connection_timeout
                )
            elif self.config.db_type == DatabaseType.POSTGRESQL:
                return psycopg2.connect(
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.username,
                    password=self.config.password,
                    connect_timeout=self.config.connection_timeout
                )
            elif self.config.db_type == DatabaseType.SQLITE:
                return sqlite3.connect(self.config.database)
            elif self.config.db_type == DatabaseType.MONGODB:
                return pymongo.MongoClient(
                    host=self.config.host,
                    port=self.config.port,
                    connectTimeoutMS=self.config.connection_timeout * 1000
                )[self.config.database]
            elif self.config.db_type == DatabaseType.REDIS:
                return redis.Redis(
                    host=self.config.host,
                    port=self.config.port,
                    password=self.config.password,
                    socket_timeout=self.config.connection_timeout
                )
            else:
                raise ValueError(f"不支持的数据库类型: {self.config.db_type}")
        except Exception as e:
            self.logger.error(f"创建数据库连接失败: {e}")
            raise
    
    def _close_connection(self, connection):
        """关闭连接"""
        try:
            if hasattr(connection, 'close'):
                connection.close()
        except Exception as e:
            self.logger.error(f"关闭数据库连接失败: {e}")
    
    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """执行查询"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if self.config.db_type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif self.config.db_type == DatabaseType.SQLITE:
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                results = []
            
            return results
        except Exception as e:
            self.logger.error(f"执行查询失败: {e}")
            raise
        finally:
            if connection:
                self.return_connection(connection)

class QueryCapture:
    """查询捕获器"""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self.logger = logging.getLogger(__name__)
        self.capture_queue = queue.Queue()
        self.running = False
        self.capture_thread = None
    
    def start_capture(self):
        """开始捕获查询"""
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_worker)
        self.capture_thread.start()
        self.logger.info("查询捕获已启动")
    
    def stop_capture(self):
        """停止捕获查询"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        self.logger.info("查询捕获已停止")
    
    def _capture_worker(self):
        """捕获工作线程"""
        while self.running:
            try:
                queries = self._capture_queries()
                for query in queries:
                    self.capture_queue.put(query)
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"捕获查询失败: {e}")
    
    def _capture_queries(self) -> List[QueryMetrics]:
        """捕获查询"""
        queries = []
        
        if self.db_connector.config.db_type == DatabaseType.MYSQL:
            queries = self._capture_mysql_queries()
        elif self.db_connector.config.db_type == DatabaseType.POSTGRESQL:
            queries = self._capture_postgresql_queries()
        elif self.db_connector.config.db_type == DatabaseType.MONGODB:
            queries = self._capture_mongodb_queries()
        
        return queries
    
    def _capture_mysql_queries(self) -> List[QueryMetrics]:
        """捕获MySQL查询"""
        queries = []
        
        try:
            # 获取慢查询
            slow_query_sql = """
            SELECT 
                query_time,
                lock_time,
                rows_sent,
                rows_examined,
                sql_text,
                db,
                user,
                host
            FROM mysql.slow_log 
            WHERE start_time >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)
            """
            
            results = self.db_connector.execute_query(slow_query_sql)
            
            for result in results:
                query_metrics = QueryMetrics(
                    query_id=str(uuid.uuid4()),
                    query_text=result['sql_text'],
                    query_type=self._detect_query_type(result['sql_text']),
                    execution_time=float(result['query_time']),
                    rows_examined=int(result['rows_examined']),
                    rows_returned=int(result['rows_sent']),
                    cpu_usage=0.0,  # 需要额外计算
                    memory_usage=0.0,  # 需要额外计算
                    disk_io=0.0,  # 需要额外计算
                    lock_wait_time=float(result['lock_time']),
                    timestamp=datetime.now(),
                    database=result['db'],
                    user=result['user'],
                    host=result['host']
                )
                queries.append(query_metrics)
        
        except Exception as e:
            self.logger.error(f"捕获MySQL查询失败: {e}")
        
        return queries
    
    def _capture_postgresql_queries(self) -> List[QueryMetrics]:
        """捕获PostgreSQL查询"""
        queries = []
        
        try:
            # 获取活动查询
            active_query_sql = """
            SELECT 
                query,
                datname,
                usename,
                client_addr,
                state,
                query_start,
                state_change
            FROM pg_stat_activity 
            WHERE state = 'active'
            AND query_start >= NOW() - INTERVAL '1 minute'
            """
            
            results = self.db_connector.execute_query(active_query_sql)
            
            for result in results:
                query_metrics = QueryMetrics(
                    query_id=str(uuid.uuid4()),
                    query_text=result['query'],
                    query_type=self._detect_query_type(result['query']),
                    execution_time=0.0,  # 需要计算
                    rows_examined=0,  # 需要额外获取
                    rows_returned=0,  # 需要额外获取
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    disk_io=0.0,
                    lock_wait_time=0.0,
                    timestamp=datetime.now(),
                    database=result['datname'],
                    user=result['usename'],
                    host=result['client_addr']
                )
                queries.append(query_metrics)
        
        except Exception as e:
            self.logger.error(f"捕获PostgreSQL查询失败: {e}")
        
        return queries
    
    def _capture_mongodb_queries(self) -> List[QueryMetrics]:
        """捕获MongoDB查询"""
        queries = []
        
        try:
            # 获取慢查询
            db = self.db_connector.get_connection()
            slow_queries = db.system.profile.find(
                {"millis": {"$gt": 100}}
            ).sort("ts", -1).limit(100)
            
            for query in slow_queries:
                query_metrics = QueryMetrics(
                    query_id=str(uuid.uuid4()),
                    query_text=str(query.get('command', {})),
                    query_type=QueryType.UNKNOWN,
                    execution_time=float(query.get('millis', 0)) / 1000,
                    rows_examined=int(query.get('nreturned', 0)),
                    rows_returned=int(query.get('nreturned', 0)),
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    disk_io=0.0,
                    lock_wait_time=0.0,
                    timestamp=query.get('ts', datetime.now()),
                    database=query.get('ns', '').split('.')[0],
                    user="",
                    host=""
                )
                queries.append(query_metrics)
        
        except Exception as e:
            self.logger.error(f"捕获MongoDB查询失败: {e}")
        
        return queries
    
    def _detect_query_type(self, query_text: str) -> QueryType:
        """检测查询类型"""
        query_upper = query_text.upper().strip()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE'):
            return QueryType.CREATE
        elif query_upper.startswith('DROP'):
            return QueryType.DROP
        elif query_upper.startswith('ALTER'):
            return QueryType.ALTER
        elif 'INDEX' in query_upper:
            return QueryType.INDEX
        else:
            return QueryType.UNKNOWN

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_performance(self, queries: List[QueryMetrics]) -> Dict[str, Any]:
        """分析性能"""
        if not queries:
            return {}
        
        analysis = {
            'execution_time_stats': self._analyze_execution_time(queries),
            'resource_usage_stats': self._analyze_resource_usage(queries),
            'query_frequency': self._analyze_query_frequency(queries),
            'slow_queries': self._identify_slow_queries(queries),
            'resource_intensive_queries': self._identify_resource_intensive_queries(queries)
        }
        
        return analysis
    
    def _analyze_execution_time(self, queries: List[QueryMetrics]) -> Dict[str, float]:
        """分析执行时间"""
        execution_times = [q.execution_time for q in queries]
        
        return {
            'mean': statistics.mean(execution_times),
            'median': statistics.median(execution_times),
            'min': min(execution_times),
            'max': max(execution_times),
            'std': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            'p95': np.percentile(execution_times, 95),
            'p99': np.percentile(execution_times, 99)
        }
    
    def _analyze_resource_usage(self, queries: List[QueryMetrics]) -> Dict[str, Dict[str, float]]:
        """分析资源使用"""
        cpu_usage = [q.cpu_usage for q in queries if q.cpu_usage > 0]
        memory_usage = [q.memory_usage for q in queries if q.memory_usage > 0]
        disk_io = [q.disk_io for q in queries if q.disk_io > 0]
        
        stats = {}
        
        if cpu_usage:
            stats['cpu'] = {
                'mean': statistics.mean(cpu_usage),
                'max': max(cpu_usage),
                'p95': np.percentile(cpu_usage, 95)
            }
        
        if memory_usage:
            stats['memory'] = {
                'mean': statistics.mean(memory_usage),
                'max': max(memory_usage),
                'p95': np.percentile(memory_usage, 95)
            }
        
        if disk_io:
            stats['disk_io'] = {
                'mean': statistics.mean(disk_io),
                'max': max(disk_io),
                'p95': np.percentile(disk_io, 95)
            }
        
        return stats
    
    def _analyze_query_frequency(self, queries: List[QueryMetrics]) -> Dict[str, int]:
        """分析查询频率"""
        query_templates = {}
        
        for query in queries:
            template = self._normalize_query(query.query_text)
            query_templates[template] = query_templates.get(template, 0) + 1
        
        return dict(sorted(query_templates.items(), key=lambda x: x[1], reverse=True))
    
    def _identify_slow_queries(self, queries: List[QueryMetrics], threshold: float = 1.0) -> List[QueryMetrics]:
        """识别慢查询"""
        return [q for q in queries if q.execution_time > threshold]
    
    def _identify_resource_intensive_queries(self, queries: List[QueryMetrics]) -> List[QueryMetrics]:
        """识别资源密集型查询"""
        return [q for q in queries if q.cpu_usage > 80 or q.memory_usage > 80]
    
    def _normalize_query(self, query: str) -> str:
        """标准化查询"""
        # 移除注释
        query = re.sub(r'--.*', '', query)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # 标准化空白字符
        query = re.sub(r'\s+', ' ', query).strip()
        
        # 替换字面量
        query = re.sub(r'\b\d+\b', '?', query)
        query = re.sub(r"'[^']*'", '?', query)
        query = re.sub(r'"[^"]*"', '?', query)
        
        return query

class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, db_connector: DatabaseConnector):
        self.db_connector = db_connector
        self.logger = logging.getLogger(__name__)
    
    def analyze_indexes(self, database: str, table: str) -> List[IndexRecommendation]:
        """分析索引"""
        recommendations = []
        
        try:
            if self.db_connector.config.db_type == DatabaseType.MYSQL:
                recommendations = self._analyze_mysql_indexes(database, table)
            elif self.db_connector.config.db_type == DatabaseType.POSTGRESQL:
                recommendations = self._analyze_postgresql_indexes(database, table)
        
        except Exception as e:
            self.logger.error(f"分析索引失败: {e}")
        
        return recommendations
    
    def _analyze_mysql_indexes(self, database: str, table: str) -> List[IndexRecommendation]:
        """分析MySQL索引"""
        recommendations = []
        
        try:
            # 获取表统计信息
            table_stats_sql = f"""
            SELECT 
                table_name,
                table_rows,
                avg_row_length,
                data_length,
                index_length
            FROM information_schema.tables 
            WHERE table_schema = '{database}' AND table_name = '{table}'
            """
            
            table_stats = self.db_connector.execute_query(table_stats_sql)
            
            if not table_stats:
                return recommendations
            
            stats = table_stats[0]
            row_count = stats['table_rows']
            
            # 获取索引信息
            index_stats_sql = f"""
            SELECT 
                index_name,
                column_name,
                cardinality
            FROM information_schema.statistics 
            WHERE table_schema = '{database}' AND table_name = '{table}'
            ORDER BY index_name, seq_in_index
            """
            
            index_stats = self.db_connector.execute_query(index_stats_sql)
            
            # 分析索引使用情况
            index_usage_sql = f"""
            SELECT 
                table_name,
                index_name,
                count_read,
                count_fetch,
                sum_timer_wait / 1000000000 as total_time
            FROM performance_schema.table_io_waits_summary_by_index_usage
            WHERE object_schema = '{database}' AND object_name = '{table}'
            """
            
            index_usage = self.db_connector.execute_query(index_usage_sql)
            
            # 生成索引建议
            if row_count > 10000:  # 大表需要索引
                # 检查是否有主键
                has_primary_key = any(idx['index_name'] == 'PRIMARY' for idx in index_stats)
                
                if not has_primary_key:
                    recommendations.append(IndexRecommendation(
                        table_name=table,
                        column_names=['id'],
                        index_type='PRIMARY',
                        estimated_improvement=50.0,
                        reason='大表缺少主键索引',
                        priority='HIGH'
                    ))
        
        except Exception as e:
            self.logger.error(f"分析MySQL索引失败: {e}")
        
        return recommendations
    
    def _analyze_postgresql_indexes(self, database: str, table: str) -> List[IndexRecommendation]:
        """分析PostgreSQL索引"""
        recommendations = []
        
        try:
            # 获取表统计信息
            table_stats_sql = f"""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins,
                n_tup_upd,
                n_tup_del,
                n_live_tup,
                n_dead_tup
            FROM pg_stat_user_tables 
            WHERE schemaname = 'public' AND tablename = '{table}'
            """
            
            table_stats = self.db_connector.execute_query(table_stats_sql)
            
            if not table_stats:
                return recommendations
            
            stats = table_stats[0]
            live_tuples = stats['n_live_tup']
            
            # 获取索引使用情况
            index_usage_sql = f"""
            SELECT 
                schemaname,
                tablename,
                indexrelname,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE schemaname = 'public' AND tablename = '{table}'
            """
            
            index_usage = self.db_connector.execute_query(index_usage_sql)
            
            # 生成索引建议
            if live_tuples > 10000:
                # 检查未使用的索引
                for idx in index_usage:
                    if idx['idx_tup_read'] == 0:
                        recommendations.append(IndexRecommendation(
                            table_name=table,
                            column_names=[idx['indexrelname']],
                            index_type='DROP',
                            estimated_improvement=10.0,
                            reason='索引未被使用，建议删除',
                            priority='MEDIUM'
                        ))
        
        except Exception as e:
            self.logger.error(f"分析PostgreSQL索引失败: {e}")
        
        return recommendations
    
    def suggest_query_rewrite(self, query: str) -> List[str]:
        """建议查询重写"""
        suggestions = []
        
        # 检查SELECT *
        if re.search(r'SELECT\s+\*\s+FROM', query, re.IGNORECASE):
            suggestions.append("避免使用SELECT *，明确指定需要的列")
        
        # 检查子查询优化
        if re.search(r'FROM\s+\(\s*SELECT', query, re.IGNORECASE):
            suggestions.append("考虑将子查询改为JOIN")
        
        # 检查WHERE条件
        if re.search(r'WHERE\s+\w+\s+LIKE\s+\'%.*%\'', query, re.IGNORECASE):
            suggestions.append("避免使用前导通配符的LIKE查询")
        
        # 检查ORDER BY
        if re.search(r'ORDER\s+BY\s+\w+', query, re.IGNORECASE):
            suggestions.append("确保ORDER BY字段有索引")
        
        return suggestions

class PatternAnalyzer:
    """模式分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
    
    def analyze_patterns(self, queries: List[QueryMetrics]) -> List[QueryPattern]:
        """分析查询模式"""
        if len(queries) < 2:
            return []
        
        patterns = []
        
        # 查询频率模式
        frequency_patterns = self._analyze_frequency_patterns(queries)
        patterns.extend(frequency_patterns)
        
        # 性能模式
        performance_patterns = self._analyze_performance_patterns(queries)
        patterns.extend(performance_patterns)
        
        # 异常检测
        anomaly_patterns = self._detect_anomalies(queries)
        patterns.extend(anomaly_patterns)
        
        return patterns
    
    def _analyze_frequency_patterns(self, queries: List[QueryMetrics]) -> List[QueryPattern]:
        """分析频率模式"""
        patterns = []
        
        # 按查询模板分组
        query_groups = defaultdict(list)
        for query in queries:
            template = self._normalize_query(query.query_text)
            query_groups[template].append(query)
        
        # 识别高频查询
        for template, group in query_groups.items():
            if len(group) >= 5:  # 至少出现5次
                pattern = QueryPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="frequency",
                    query_template=template,
                    frequency=len(group),
                    avg_execution_time=statistics.mean([q.execution_time for q in group]),
                    similarity_threshold=0.8,
                    queries=group
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_performance_patterns(self, queries: List[QueryMetrics]) -> List[QueryPattern]:
        """分析性能模式"""
        patterns = []
        
        # 按执行时间分组
        slow_queries = [q for q in queries if q.execution_time > 1.0]
        fast_queries = [q for q in queries if q.execution_time < 0.1]
        
        if slow_queries:
            pattern = QueryPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="slow_performance",
                query_template="slow_queries",
                frequency=len(slow_queries),
                avg_execution_time=statistics.mean([q.execution_time for q in slow_queries]),
                similarity_threshold=0.8,
                queries=slow_queries
            )
            patterns.append(pattern)
        
        if fast_queries:
            pattern = QueryPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="fast_performance",
                query_template="fast_queries",
                frequency=len(fast_queries),
                avg_execution_time=statistics.mean([q.execution_time for q in fast_queries]),
                similarity_threshold=0.8,
                queries=fast_queries
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_anomalies(self, queries: List[QueryMetrics]) -> List[QueryPattern]:
        """检测异常"""
        patterns = []
        
        if len(queries) < 10:
            return patterns
        
        # 准备特征数据
        features = []
        for query in queries:
            feature_vector = [
                query.execution_time,
                query.rows_examined,
                query.rows_returned,
                query.cpu_usage,
                query.memory_usage
            ]
            features.append(feature_vector)
        
        # 标准化特征
        features_scaled = self.scaler.fit_transform(features)
        
        # 异常检测
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(features_scaled)
        
        # 收集异常查询
        anomaly_queries = []
        for i, label in enumerate(anomaly_labels):
            if label == -1:  # 异常点
                anomaly_queries.append(queries[i])
        
        if anomaly_queries:
            pattern = QueryPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="anomaly",
                query_template="anomaly_queries",
                frequency=len(anomaly_queries),
                avg_execution_time=statistics.mean([q.execution_time for q in anomaly_queries]),
                similarity_threshold=0.8,
                queries=anomaly_queries
            )
            patterns.append(pattern)
        
        return patterns
    
    def _normalize_query(self, query: str) -> str:
        """标准化查询"""
        # 移除注释
        query = re.sub(r'--.*', '', query)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # 标准化空白字符
        query = re.sub(r'\s+', ' ', query).strip()
        
        # 替换字面量
        query = re.sub(r'\b\d+\b', '?', query)
        query = re.sub(r"'[^']*'", '?', query)
        query = re.sub(r'"[^"]*"', '?', query)
        
        return query

class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_rules = []
        self.alert_handlers = []
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """添加告警规则"""
        self.alert_rules.append(rule)
    
    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def check_alerts(self, queries: List[QueryMetrics]) -> List[PerformanceAlert]:
        """检查告警"""
        alerts = []
        
        for rule in self.alert_rules:
            rule_alerts = self._evaluate_rule(rule, queries)
            alerts.extend(rule_alerts)
        
        # 发送告警
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _evaluate_rule(self, rule: Dict[str, Any], queries: List[QueryMetrics]) -> List[PerformanceAlert]:
        """评估告警规则"""
        alerts = []
        
        rule_type = rule.get('type')
        threshold = rule.get('threshold')
        duration = rule.get('duration', 300)  # 5分钟
        
        if rule_type == 'slow_query':
            slow_queries = [q for q in queries if q.execution_time > threshold]
            for query in slow_queries:
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type='slow_query',
                    severity='WARNING',
                    message=f'慢查询检测: 执行时间 {query.execution_time:.2f}s 超过阈值 {threshold}s',
                    query_id=query.query_id,
                    threshold=threshold,
                    actual_value=query.execution_time,
                    timestamp=datetime.now()
                )
                alerts.append(alert)
        
        elif rule_type == 'high_cpu':
            high_cpu_queries = [q for q in queries if q.cpu_usage > threshold]
            for query in high_cpu_queries:
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type='high_cpu',
                    severity='WARNING',
                    message=f'高CPU使用率: {query.cpu_usage:.2f}% 超过阈值 {threshold}%',
                    query_id=query.query_id,
                    threshold=threshold,
                    actual_value=query.cpu_usage,
                    timestamp=datetime.now()
                )
                alerts.append(alert)
        
        return alerts
    
    def _send_alert(self, alert: PerformanceAlert):
        """发送告警"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"发送告警失败: {e}")

class DatabaseQueryAnalyzer:
    """数据库查询分析器"""
    
    def __init__(self, db_config: DatabaseConnection):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.db_connector = DatabaseConnector(db_config)
        self.query_capture = QueryCapture(self.db_connector)
        self.performance_analyzer = PerformanceAnalyzer()
        self.query_optimizer = QueryOptimizer(self.db_connector)
        self.pattern_analyzer = PatternAnalyzer()
        self.alert_manager = AlertManager()
        
        # 数据存储
        self.queries = []
        self.analysis_results = {}
        self.alerts = []
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def start(self):
        """启动分析器"""
        self.logger.info("启动数据库查询分析器")
        
        # 启动查询捕获
        self.query_capture.start_capture()
        
        # 启动分析线程
        analysis_thread = threading.Thread(target=self._analysis_worker)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def stop(self):
        """停止分析器"""
        self.logger.info("停止数据库查询分析器")
        
        # 停止查询捕获
        self.query_capture.stop_capture()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
    
    def _analysis_worker(self):
        """分析工作线程"""
        while True:
            try:
                # 获取捕获的查询
                captured_queries = []
                while not self.query_capture.capture_queue.empty():
                    query = self.query_capture.capture_queue.get()
                    captured_queries.append(query)
                
                if captured_queries:
                    self.queries.extend(captured_queries)
                    
                    # 执行分析
                    self._perform_analysis(captured_queries)
                
                time.sleep(10)  # 每10秒分析一次
                
            except Exception as e:
                self.logger.error(f"分析失败: {e}")
    
    def _perform_analysis(self, queries: List[QueryMetrics]):
        """执行分析"""
        try:
            # 性能分析
            performance_analysis = self.performance_analyzer.analyze_performance(queries)
            self.analysis_results['performance'] = performance_analysis
            
            # 模式分析
            patterns = self.pattern_analyzer.analyze_patterns(queries)
            self.analysis_results['patterns'] = patterns
            
            # 告警检查
            alerts = self.alert_manager.check_alerts(queries)
            self.alerts.extend(alerts)
            
            self.logger.info(f"分析完成: 处理了 {len(queries)} 个查询")
            
        except Exception as e:
            self.logger.error(f"执行分析失败: {e}")
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """获取分析报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_queries': len(self.queries),
            'analysis_results': self.analysis_results,
            'recent_alerts': self.alerts[-10:] if self.alerts else [],
            'slow_queries': self.performance_analyzer._identify_slow_queries(self.queries),
            'index_recommendations': self._get_index_recommendations()
        }
        
        return report
    
    def _get_index_recommendations(self) -> List[IndexRecommendation]:
        """获取索引建议"""
        recommendations = []
        
        # 获取所有表
        if self.db_config.db_type == DatabaseType.MYSQL:
            tables_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
        elif self.db_config.db_type == DatabaseType.POSTGRESQL:
            tables_sql = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        else:
            return recommendations
        
        try:
            tables = self.db_connector.execute_query(tables_sql)
            
            for table in tables:
                table_name = table['table_name'] if 'table_name' in table else table['tablename']
                table_recommendations = self.query_optimizer.analyze_indexes(
                    self.db_config.database, table_name
                )
                recommendations.extend(table_recommendations)
        
        except Exception as e:
            self.logger.error(f"获取索引建议失败: {e}")
        
        return recommendations
    
    def add_alert_rule(self, rule_type: str, threshold: float, severity: str = "WARNING"):
        """添加告警规则"""
        rule = {
            'type': rule_type,
            'threshold': threshold,
            'severity': severity,
            'enabled': True
        }
        self.alert_manager.add_alert_rule(rule)
    
    def add_email_alert_handler(self, smtp_config: Dict[str, str], recipients: List[str]):
        """添加邮件告警处理器"""
        def email_handler(alert: PerformanceAlert):
            # 实现邮件发送逻辑
            self.logger.info(f"发送邮件告警: {alert.message}")
        
        self.alert_manager.add_alert_handler(email_handler)

# 使用示例
# 配置数据库连接
db_config = DatabaseConnection(
    db_type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    database="test_db",
    username="root",
    password="password"
)

# 创建分析器
analyzer = DatabaseQueryAnalyzer(db_config)

# 添加告警规则
analyzer.add_alert_rule("slow_query", threshold=1.0, severity="WARNING")
analyzer.add_alert_rule("high_cpu", threshold=80.0, severity="CRITICAL")

# 添加邮件告警
analyzer.add_email_alert_handler(
    smtp_config={
        "host": "smtp.example.com",
        "port": 587,
        "username": "alert@example.com",
        "password": "password"
    },
    recipients=["admin@example.com"]
)

# 启动分析器
analyzer.start()

# 模拟运行一段时间
time.sleep(60)

# 获取分析报告
report = analyzer.get_analysis_report()
print(f"\n分析报告:")
print(json.dumps(report, indent=2, ensure_ascii=False, default=str))

# 停止分析器
analyzer.stop()
```

## 参考资源

### 数据库性能优化
- [MySQL性能调优指南](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [PostgreSQL性能优化](https://www.postgresql.org/docs/current/performance-tips.html)
- [MongoDB性能优化](https://docs.mongodb.com/manual/administration/performance-indexing/)
- [Redis性能优化](https://redis.io/topics/memory-optimization)

### 查询分析工具
- [EXPLAIN命令详解](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
- [pg_stat_statements扩展](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [MongoDB性能分析](https://docs.mongodb.com/manual/tutorial/manage-the-query-profiler/)
- [慢查询日志配置](https://dev.mysql.com/doc/refman/8.0/en/slow-query-log.html)

### 索引优化
- [MySQL索引最佳实践](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
- [PostgreSQL索引类型](https://www.postgresql.org/docs/current/indexes-types.html)
- [MongoDB索引策略](https://docs.mongodb.com/manual/indexes/)
- [索引设计原则](https://use-the-index-luke.com/)

### 监控和告警
- [Prometheus数据库监控](https://prometheus.io/docs/instrumenting/writing_exporters/)
- [Grafana数据库仪表板](https://grafana.com/grafana/dashboards/)
- [数据库监控最佳实践](https://www.datadoghq.com/blog/database-monitoring/)
- [告警系统设计](https://www.oreilly.com/library/designing-data-intensive-applications/)
