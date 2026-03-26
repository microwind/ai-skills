# SQL优化器参考文档

## SQL优化器概述

### 什么是SQL优化器
SQL优化器是一种用于分析和优化SQL查询性能的工具，它通过分析查询执行计划、索引使用情况、表结构等因素，提供优化建议和自动优化功能。SQL优化器能够帮助数据库管理员和开发人员识别性能瓶颈，优化查询语句，提升数据库整体性能。它支持多种数据库类型，包括MySQL、PostgreSQL、Oracle、SQL Server等，提供全面的性能分析和优化解决方案。

### 主要功能
- **查询分析**: 分析SQL查询的执行计划、性能指标和资源使用情况
- **索引优化**: 分析索引使用情况，建议新增、删除或重建索引
- **表结构优化**: 分析表结构，建议字段类型优化、约束优化和分区策略
- **执行计划优化**: 优化查询执行计划，提供查询重写和提示优化
- **统计信息管理**: 收集和维护数据库统计信息，支持查询优化决策
- **性能监控**: 实时监控数据库性能，提供告警和报告功能
- **自动化优化**: 基于机器学习的自动优化和部署功能

## SQL优化器核心

### 查询分析引擎
```python
# sql_query_analyzer.py
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

class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQLSERVER = "sqlserver"
    SQLITE = "sqlite"

class OptimizationType(Enum):
    """优化类型枚举"""
    QUERY = "query"
    INDEX = "index"
    TABLE = "table"
    EXECUTION_PLAN = "execution_plan"
    STATISTICS = "statistics"

class AnalysisLevel(Enum):
    """分析级别枚举"""
    BASIC = "basic"
    DETAILED = "detailed"
    DEEP = "deep"
    CUSTOM = "custom"

@dataclass
class DatabaseConfig:
    """数据库配置"""
    config_id: str
    name: str
    type: DatabaseType
    host: str
    port: int
    username: str
    password: str
    database: str
    charset: str = "utf8mb4"
    ssl_config: Dict[str, Any] = field(default_factory=dict)
    connection_params: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30

@dataclass
class QueryAnalysis:
    """查询分析结果"""
    query_id: str
    query_text: str
    database: str
    execution_time: float
    scan_rows: int
    return_rows: int
    index_usage: Dict[str, Any]
    execution_plan: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]
    analysis_time: datetime = field(default_factory=datetime.now)

@dataclass
class IndexAnalysis:
    """索引分析结果"""
    index_id: str
    table_name: str
    index_name: str
    index_type: str
    index_columns: List[str]
    usage_stats: Dict[str, Any]
    efficiency_score: float
    optimization_recommendations: List[Dict[str, Any]]
    analysis_time: datetime = field(default_factory=datetime.now)

@dataclass
class TableAnalysis:
    """表分析结果"""
    table_id: str
    table_name: str
    table_size: int
    row_count: int
    column_stats: List[Dict[str, Any]]
    partition_info: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]
    analysis_time: datetime = field(default_factory=datetime.now)

class DatabaseConnector:
    """数据库连接器"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection = None
    
    def connect(self):
        """连接数据库"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                self._connect_mysql()
            elif self.config.type == DatabaseType.POSTGRESQL:
                self._connect_postgresql()
            elif self.config.type == DatabaseType.ORACLE:
                self._connect_oracle()
            elif self.config.type == DatabaseType.SQLSERVER:
                self._connect_sqlserver()
            else:
                raise ValueError(f"不支持的数据库类型: {self.config.type}")
            
            self.logger.info(f"数据库连接成功: {self.config.name}")
        
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise
    
    def _connect_mysql(self):
        """连接MySQL"""
        self.connection = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.username,
            password=self.config.password,
            database=self.config.database,
            charset=self.config.charset,
            connect_timeout=self.config.timeout,
            **self.config.connection_params
        )
    
    def _connect_postgresql(self):
        """连接PostgreSQL"""
        self.connection = psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.username,
            password=self.config.password,
            database=self.config.database,
            connect_timeout=self.config.timeout,
            **self.config.connection_params
        )
    
    def _connect_oracle(self):
        """连接Oracle"""
        dsn = cx_Oracle.makedsn(self.config.host, self.config.port, self.config.database)
        self.connection = cx_Oracle.connect(
            user=self.config.username,
            password=self.config.password,
            dsn=dsn,
            encoding=self.config.charset
        )
    
    def _connect_sqlserver(self):
        """连接SQL Server"""
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.host},{self.config.port};DATABASE={self.config.database};UID={self.config.username};PWD={self.config.password}"
        self.connection = pyodbc.connect(connection_string)
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: Any = None) -> Any:
        """执行查询"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                result = cursor.rowcount
                self.connection.commit()
                cursor.close()
                return result
        
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            raise
    
    def get_execution_plan(self, query: str) -> Dict[str, Any]:
        """获取执行计划"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                return self._get_mysql_execution_plan(query)
            elif self.config.type == DatabaseType.POSTGRESQL:
                return self._get_postgresql_execution_plan(query)
            elif self.config.type == DatabaseType.ORACLE:
                return self._get_oracle_execution_plan(query)
            elif self.config.type == DatabaseType.SQLSERVER:
                return self._get_sqlserver_execution_plan(query)
            else:
                raise ValueError(f"不支持的数据库类型: {self.config.type}")
        
        except Exception as e:
            self.logger.error(f"获取执行计划失败: {e}")
            raise
    
    def _get_mysql_execution_plan(self, query: str) -> Dict[str, Any]:
        """获取MySQL执行计划"""
        try:
            explain_query = f"EXPLAIN FORMAT=JSON {query}"
            result = self.execute_query(explain_query)
            
            if result and result[0]:
                plan_json = result[0][0]
                plan_data = json.loads(plan_json)
                
                return {
                    'database': self.config.database,
                    'query': query,
                    'plan': plan_data,
                    'raw_output': plan_json
                }
            else:
                return {}
        
        except Exception as e:
            self.logger.error(f"获取MySQL执行计划失败: {e}")
            raise
    
    def _get_postgresql_execution_plan(self, query: str) -> Dict[str, Any]:
        """获取PostgreSQL执行计划"""
        try:
            explain_query = f"EXPLAIN (FORMAT JSON, ANALYZE, BUFFERS) {query}"
            result = self.execute_query(explain_query)
            
            if result and result[0]:
                plan_json = result[0][0]
                plan_data = json.loads(plan_json)
                
                return {
                    'database': self.config.database,
                    'query': query,
                    'plan': plan_data,
                    'raw_output': plan_json
                }
            else:
                return {}
        
        except Exception as e:
            self.logger.error(f"获取PostgreSQL执行计划失败: {e}")
            raise
    
    def _get_oracle_execution_plan(self, query: str) -> Dict[str, Any]:
        """获取Oracle执行计划"""
        try:
            explain_query = f"EXPLAIN PLAN FOR {query}"
            self.execute_query(explain_query)
            
            plan_query = "SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY)"
            result = self.execute_query(plan_query)
            
            plan_text = '\n'.join([row[0] for row in result if row[0]])
            
            return {
                'database': self.config.database,
                'query': query,
                'plan': plan_text,
                'raw_output': plan_text
            }
        
        except Exception as e:
            self.logger.error(f"获取Oracle执行计划失败: {e}")
            raise
    
    def _get_sqlserver_execution_plan(self, query: str) -> Dict[str, Any]:
        """获取SQL Server执行计划"""
        try:
            explain_query = f"SET SHOWPLAN_XML ON; GO; {query}"
            result = self.execute_query(explain_query)
            
            if result and result[0]:
                plan_xml = result[0][0]
                
                return {
                    'database': self.config.database,
                    'query': query,
                    'plan': plan_xml,
                    'raw_output': plan_xml
                }
            else:
                return {}
        
        except Exception as e:
            self.logger.error(f"获取SQL Server执行计划失败: {e}")
            raise

class QueryAnalyzer:
    """查询分析器"""
    
    def __init__(self, connector: DatabaseConnector):
        self.connector = connector
        self.logger = logging.getLogger(__name__)
    
    def analyze_query(self, query: str, analysis_level: AnalysisLevel = AnalysisLevel.BASIC) -> QueryAnalysis:
        """分析查询"""
        try:
            # 获取执行计划
            execution_plan = self.connector.get_execution_plan(query)
            
            # 分析查询性能
            performance_stats = self._analyze_query_performance(query, execution_plan)
            
            # 分析索引使用
            index_usage = self._analyze_index_usage(execution_plan)
            
            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(
                query, execution_plan, performance_stats, index_usage, analysis_level
            )
            
            # 创建分析结果
            analysis = QueryAnalysis(
                query_id=str(uuid.uuid4()),
                query_text=query,
                database=self.connector.config.database,
                execution_time=performance_stats.get('execution_time', 0),
                scan_rows=performance_stats.get('scan_rows', 0),
                return_rows=performance_stats.get('return_rows', 0),
                index_usage=index_usage,
                execution_plan=execution_plan,
                optimization_suggestions=optimization_suggestions
            )
            
            self.logger.info(f"查询分析完成: {analysis.query_id}")
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"查询分析失败: {e}")
            raise
    
    def _analyze_query_performance(self, query: str, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析查询性能"""
        try:
            performance_stats = {}
            
            if self.connector.config.type == DatabaseType.MYSQL:
                performance_stats = self._analyze_mysql_performance(execution_plan)
            elif self.connector.config.type == DatabaseType.POSTGRESQL:
                performance_stats = self._analyze_postgresql_performance(execution_plan)
            elif self.connector.config.type == DatabaseType.ORACLE:
                performance_stats = self._analyze_oracle_performance(execution_plan)
            elif self.connector.config.type == DatabaseType.SQLSERVER:
                performance_stats = self._analyze_sqlserver_performance(execution_plan)
            
            return performance_stats
        
        except Exception as e:
            self.logger.error(f"查询性能分析失败: {e}")
            return {}
    
    def _analyze_mysql_performance(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析MySQL查询性能"""
        try:
            plan = execution_plan.get('plan', {})
            query_block = plan.get('query_block', {})
            
            performance_stats = {
                'execution_time': 0,
                'scan_rows': 0,
                'return_rows': 0,
                'cost': 0
            }
            
            # 提取成本信息
            if 'cost_info' in query_block:
                cost_info = query_block['cost_info']
                performance_stats['cost'] = cost_info.get('query_cost', 0)
            
            # 提取行数信息
            if 'table' in query_block:
                table_info = query_block['table']
                performance_stats['scan_rows'] = table_info.get('rows_examined_per_scan', 0)
                performance_stats['return_rows'] = table_info.get('rows_produced_per_join', 0)
            
            return performance_stats
        
        except Exception as e:
            self.logger.error(f"MySQL性能分析失败: {e}")
            return {}
    
    def _analyze_postgresql_performance(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析PostgreSQL查询性能"""
        try:
            plan = execution_plan.get('plan', [])
            
            performance_stats = {
                'execution_time': 0,
                'scan_rows': 0,
                'return_rows': 0,
                'cost': 0
            }
            
            if plan and len(plan) > 0:
                plan_info = plan[0].get('Plan', {})
                
                # 提取执行时间
                execution_time = plan_info.get('Execution Time', 0)
                performance_stats['execution_time'] = execution_time
                
                # 提取行数信息
                actual_rows = plan_info.get('Actual Rows', 0)
                plan_rows = plan_info.get('Plan Rows', 0)
                performance_stats['scan_rows'] = plan_rows
                performance_stats['return_rows'] = actual_rows
                
                # 提取成本信息
                total_cost = plan_info.get('Total Cost', 0)
                performance_stats['cost'] = total_cost
            
            return performance_stats
        
        except Exception as e:
            self.logger.error(f"PostgreSQL性能分析失败: {e}")
            return {}
    
    def _analyze_oracle_performance(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析Oracle查询性能"""
        try:
            plan_text = execution_plan.get('plan', '')
            
            performance_stats = {
                'execution_time': 0,
                'scan_rows': 0,
                'return_rows': 0,
                'cost': 0
            }
            
            # 解析Oracle执行计划文本
            lines = plan_text.split('\n')
            for line in lines:
                if 'Cost' in line:
                    # 提取成本信息
                    cost_match = re.search(r'Cost:\s*(\d+)', line)
                    if cost_match:
                        performance_stats['cost'] = int(cost_match.group(1))
                
                if 'Rows' in line:
                    # 提取行数信息
                    rows_match = re.search(r'Rows:\s*(\d+)', line)
                    if rows_match:
                        performance_stats['scan_rows'] = int(rows_match.group(1))
            
            return performance_stats
        
        except Exception as e:
            self.logger.error(f"Oracle性能分析失败: {e}")
            return {}
    
    def _analyze_sqlserver_performance(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析SQL Server查询性能"""
        try:
            plan_xml = execution_plan.get('plan', '')
            
            performance_stats = {
                'execution_time': 0,
                'scan_rows': 0,
                'return_rows': 0,
                'cost': 0
            }
            
            # 解析SQL Server执行计划XML
            try:
                root = ET.fromstring(plan_xml)
                
                # 提取成本信息
                for stmt in root.findall('.//StmtSimple'):
                    cost = stmt.get('EstimatedTotalSubtreeCost', '0')
                    performance_stats['cost'] = float(cost)
                
                # 提取行数信息
                for rel_op in root.findall('.//RelOp'):
                    estimate_rows = rel_op.get('EstimateRows', '0')
                    actual_rows = rel_op.get('ActualRows', '0')
                    
                    if estimate_rows:
                        performance_stats['scan_rows'] += float(estimate_rows)
                    if actual_rows:
                        performance_stats['return_rows'] += float(actual_rows)
            
            except ET.ParseError as e:
                self.logger.error(f"SQL Server执行计划XML解析失败: {e}")
            
            return performance_stats
        
        except Exception as e:
            self.logger.error(f"SQL Server性能分析失败: {e}")
            return {}
    
    def _analyze_index_usage(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析索引使用情况"""
        try:
            index_usage = {
                'used_indexes': [],
                'missing_indexes': [],
                'inefficient_indexes': []
            }
            
            if self.connector.config.type == DatabaseType.MYSQL:
                index_usage = self._analyze_mysql_index_usage(execution_plan)
            elif self.connector.config.type == DatabaseType.POSTGRESQL:
                index_usage = self._analyze_postgresql_index_usage(execution_plan)
            elif self.connector.config.type == DatabaseType.ORACLE:
                index_usage = self._analyze_oracle_index_usage(execution_plan)
            elif self.connector.config.type == DatabaseType.SQLSERVER:
                index_usage = self._analyze_sqlserver_index_usage(execution_plan)
            
            return index_usage
        
        except Exception as e:
            self.logger.error(f"索引使用分析失败: {e}")
            return {}
    
    def _analyze_mysql_index_usage(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析MySQL索引使用"""
        try:
            plan = execution_plan.get('plan', {})
            query_block = plan.get('query_block', {})
            
            index_usage = {
                'used_indexes': [],
                'missing_indexes': [],
                'inefficient_indexes': []
            }
            
            # 分析表访问方式
            if 'table' in query_block:
                table_info = query_block['table']
                access_type = table_info.get('access_type', '')
                possible_keys = table_info.get('possible_keys', [])
                key = table_info.get('key', '')
                
                if key:
                    index_usage['used_indexes'].append({
                        'index_name': key,
                        'access_type': access_type,
                        'table': table_info.get('table_name', '')
                    })
                
                # 检查缺失索引
                if access_type == 'ALL' and possible_keys:
                    index_usage['missing_indexes'].extend(possible_keys)
            
            return index_usage
        
        except Exception as e:
            self.logger.error(f"MySQL索引使用分析失败: {e}")
            return {}
    
    def _analyze_postgresql_index_usage(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析PostgreSQL索引使用"""
        try:
            plan = execution_plan.get('plan', [])
            
            index_usage = {
                'used_indexes': [],
                'missing_indexes': [],
                'inefficient_indexes': []
            }
            
            if plan and len(plan) > 0:
                plan_info = plan[0].get('Plan', {})
                self._extract_postgresql_index_info(plan_info, index_usage)
            
            return index_usage
        
        except Exception as e:
            self.logger.error(f"PostgreSQL索引使用分析失败: {e}")
            return {}
    
    def _extract_postgresql_index_info(self, plan_info: Dict[str, Any], index_usage: Dict[str, Any]):
        """提取PostgreSQL索引信息"""
        try:
            node_type = plan_info.get('Node Type', '')
            
            if 'Index' in node_type:
                # 索引扫描
                index_name = plan_info.get('Index Name', '')
                if index_name:
                    index_usage['used_indexes'].append({
                        'index_name': index_name,
                        'scan_type': node_type,
                        'condition': plan_info.get('Index Cond', '')
                    })
            
            elif node_type == 'Seq Scan':
                # 全表扫描，可能需要索引
                relation_name = plan_info.get('Relation Name', '')
                alias = plan_info.get('Alias', '')
                condition = plan_info.get('Filter', '')
                
                if condition:
                    index_usage['missing_indexes'].append({
                        'table': relation_name,
                        'alias': alias,
                        'condition': condition
                    })
            
            # 递归处理子计划
            if 'Plans' in plan_info:
                for sub_plan in plan_info['Plans']:
                    self._extract_postgresql_index_info(sub_plan, index_usage)
        
        except Exception as e:
            self.logger.error(f"PostgreSQL索引信息提取失败: {e}")
    
    def _analyze_oracle_index_usage(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析Oracle索引使用"""
        try:
            plan_text = execution_plan.get('plan', '')
            
            index_usage = {
                'used_indexes': [],
                'missing_indexes': [],
                'inefficient_indexes': []
            }
            
            # 解析Oracle执行计划文本
            lines = plan_text.split('\n')
            for line in lines:
                if 'INDEX' in line:
                    # 索引访问
                    parts = line.split()
                    if len(parts) >= 3:
                        index_usage['used_indexes'].append({
                            'index_name': parts[2],
                            'operation': parts[1],
                            'full_line': line.strip()
                        })
                elif 'TABLE ACCESS' in line and 'FULL' in line:
                    # 全表扫描，可能需要索引
                    table_match = re.search(r'TABLE ACCESS FULL\s+(\w+)', line)
                    if table_match:
                        index_usage['missing_indexes'].append({
                            'table': table_match.group(1),
                            'operation': 'FULL TABLE SCAN',
                            'full_line': line.strip()
                        })
            
            return index_usage
        
        except Exception as e:
            self.logger.error(f"Oracle索引使用分析失败: {e}")
            return {}
    
    def _analyze_sqlserver_index_usage(self, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """分析SQL Server索引使用"""
        try:
            plan_xml = execution_plan.get('plan', '')
            
            index_usage = {
                'used_indexes': [],
                'missing_indexes': [],
                'inefficient_indexes': []
            }
            
            # 解析SQL Server执行计划XML
            try:
                root = ET.fromstring(plan_xml)
                
                # 查找索引操作
                for index_op in root.findall('.//IndexScan'):
                    index_name = index_op.get('IndexName', '')
                    table_name = index_op.get('Table', '')
                    
                    if index_name:
                        index_usage['used_indexes'].append({
                            'index_name': index_name,
                            'table': table_name,
                            'operation': 'IndexScan'
                        })
                
                # 查找表扫描
                for table_scan in root.findall('.//TableScan'):
                    table_name = table_scan.get('Table', '')
                    
                    index_usage['missing_indexes'].append({
                        'table': table_name,
                        'operation': 'TableScan'
                    })
            
            except ET.ParseError as e:
                self.logger.error(f"SQL Server执行计划XML解析失败: {e}")
            
            return index_usage
        
        except Exception as e:
            self.logger.error(f"SQL Server索引使用分析失败: {e}")
            return {}
    
    def _generate_optimization_suggestions(self, query: str, execution_plan: Dict[str, Any],
                                          performance_stats: Dict[str, Any], index_usage: Dict[str, Any],
                                          analysis_level: AnalysisLevel) -> List[Dict[str, Any]]:
        """生成优化建议"""
        try:
            suggestions = []
            
            # 基于性能的建议
            if performance_stats.get('execution_time', 0) > 10:
                suggestions.append({
                    'type': 'performance',
                    'priority': 'high',
                    'description': '查询执行时间过长，建议优化',
                    'details': f"执行时间: {performance_stats.get('execution_time', 0)}秒"
                })
            
            # 基于索引使用的建议
            missing_indexes = index_usage.get('missing_indexes', [])
            if missing_indexes:
                for missing_index in missing_indexes:
                    suggestions.append({
                        'type': 'index',
                        'priority': 'medium',
                        'description': '建议创建索引以提高查询性能',
                        'details': f"表: {missing_index.get('table', '')}, 条件: {missing_index.get('condition', '')}"
                    })
            
            # 基于扫描行数的建议
            scan_rows = performance_stats.get('scan_rows', 0)
            return_rows = performance_stats.get('return_rows', 0)
            
            if scan_rows > return_rows * 10:
                suggestions.append({
                    'type': 'efficiency',
                    'priority': 'medium',
                    'description': '扫描行数过多，建议优化查询条件或索引',
                    'details': f"扫描: {scan_rows}行, 返回: {return_rows}行"
                })
            
            # 基于查询文本的建议
            if 'SELECT *' in query.upper():
                suggestions.append({
                    'type': 'query',
                    'priority': 'low',
                    'description': '避免使用SELECT *，只查询需要的列',
                    'details': '明确指定需要的列名可以提高查询效率'
                })
            
            # 深度分析建议
            if analysis_level in [AnalysisLevel.DETAILED, AnalysisLevel.DEEP]:
                suggestions.extend(self._generate_detailed_suggestions(query, execution_plan, performance_stats))
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"生成优化建议失败: {e}")
            return []
    
    def _generate_detailed_suggestions(self, query: str, execution_plan: Dict[str, Any],
                                     performance_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成详细优化建议"""
        try:
            suggestions = []
            
            # 分析查询结构
            query_upper = query.upper()
            
            # 子查询优化
            if 'IN (SELECT' in query_upper or 'EXISTS' in query_upper:
                suggestions.append({
                    'type': 'query_structure',
                    'priority': 'medium',
                    'description': '考虑使用JOIN替代子查询以提高性能',
                    'details': '子查询可能影响性能，JOIN通常更高效'
                })
            
            # ORDER BY优化
            if 'ORDER BY' in query_upper and 'LIMIT' not in query_upper:
                suggestions.append({
                    'type': 'sorting',
                    'priority': 'low',
                    'description': '考虑添加LIMIT子句或创建排序索引',
                    'details': '排序操作可能消耗大量资源'
                })
            
            # GROUP BY优化
            if 'GROUP BY' in query_upper:
                suggestions.append({
                    'type': 'grouping',
                    'priority': 'low',
                    'description': '确保GROUP BY字段有适当的索引',
                    'details': 'GROUP BY操作可以通过索引优化'
                })
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"生成详细优化建议失败: {e}")
            return []

class IndexAnalyzer:
    """索引分析器"""
    
    def __init__(self, connector: DatabaseConnector):
        self.connector = connector
        self.logger = logging.getLogger(__name__)
    
    def analyze_indexes(self, table_name: str = None) -> List[IndexAnalysis]:
        """分析索引"""
        try:
            if table_name:
                # 分析单个表的索引
                return [self._analyze_table_indexes(table_name)]
            else:
                # 分析所有表的索引
                tables = self._get_all_tables()
                analyses = []
                
                for table in tables:
                    try:
                        analysis = self._analyze_table_indexes(table)
                        analyses.append(analysis)
                    except Exception as e:
                        self.logger.error(f"分析表 {table} 索引失败: {e}")
                
                return analyses
        
        except Exception as e:
            self.logger.error(f"索引分析失败: {e}")
            raise
    
    def _get_all_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            if self.connector.config.type == DatabaseType.MYSQL:
                query = "SHOW TABLES"
            elif self.connector.config.type == DatabaseType.POSTGRESQL:
                query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            elif self.connector.config.type == DatabaseType.ORACLE:
                query = "SELECT table_name FROM user_tables"
            elif self.connector.config.type == DatabaseType.SQLSERVER:
                query = "SELECT name FROM sys.tables"
            else:
                raise ValueError(f"不支持的数据库类型: {self.connector.config.type}")
            
            result = self.connector.execute_query(query)
            return [row[0] for row in result]
        
        except Exception as e:
            self.logger.error(f"获取表列表失败: {e}")
            raise
    
    def _analyze_table_indexes(self, table_name: str) -> IndexAnalysis:
        """分析单个表的索引"""
        try:
            # 获取索引信息
            index_info = self._get_table_indexes(table_name)
            
            # 分析索引使用情况
            usage_stats = self._get_index_usage_stats(table_name)
            
            # 计算效率分数
            efficiency_score = self._calculate_index_efficiency(index_info, usage_stats)
            
            # 生成优化建议
            recommendations = self._generate_index_recommendations(
                table_name, index_info, usage_stats, efficiency_score
            )
            
            # 创建分析结果
            analysis = IndexAnalysis(
                index_id=str(uuid.uuid4()),
                table_name=table_name,
                index_name=index_info.get('index_name', ''),
                index_type=index_info.get('index_type', ''),
                index_columns=index_info.get('columns', []),
                usage_stats=usage_stats,
                efficiency_score=efficiency_score,
                optimization_recommendations=recommendations
            )
            
            self.logger.info(f"表 {table_name} 索引分析完成")
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"表 {table_name} 索引分析失败: {e}")
            raise
    
    def _get_table_indexes(self, table_name: str) -> Dict[str, Any]:
        """获取表索引信息"""
        try:
            if self.connector.config.type == DatabaseType.MYSQL:
                return self._get_mysql_indexes(table_name)
            elif self.connector.config.type == DatabaseType.POSTGRESQL:
                return self._get_postgresql_indexes(table_name)
            elif self.connector.config.type == DatabaseType.ORACLE:
                return self._get_oracle_indexes(table_name)
            elif self.connector.config.type == DatabaseType.SQLSERVER:
                return self._get_sqlserver_indexes(table_name)
            else:
                raise ValueError(f"不支持的数据库类型: {self.connector.config.type}")
        
        except Exception as e:
            self.logger.error(f"获取表索引信息失败: {e}")
            return {}
    
    def _get_mysql_indexes(self, table_name: str) -> Dict[str, Any]:
        """获取MySQL索引信息"""
        try:
            query = f"SHOW INDEX FROM {table_name}"
            result = self.connector.execute_query(query)
            
            indexes = {}
            for row in result:
                index_name = row[2]
                column_name = row[4]
                seq_in_index = row[3]
                non_unique = row[1]
                index_type = row[10]
                
                if index_name not in indexes:
                    indexes[index_name] = {
                        'index_name': index_name,
                        'index_type': index_type or 'BTREE',
                        'unique': not non_unique,
                        'columns': []
                    }
                
                indexes[index_name]['columns'].append({
                    'column_name': column_name,
                    'seq_in_index': seq_in_index
                })
            
            # 按seq_in_index排序列
            for index in indexes.values():
                index['columns'].sort(key=lambda x: x['seq_in_index'])
                index['columns'] = [col['column_name'] for col in index['columns']]
            
            return indexes
        
        except Exception as e:
            self.logger.error(f"获取MySQL索引信息失败: {e}")
            return {}
    
    def _get_postgresql_indexes(self, table_name: str) -> Dict[str, Any]:
        """获取PostgreSQL索引信息"""
        try:
            query = f"""
                SELECT 
                    indexname, 
                    indexdef,
                    schemaname,
                    tablename
                FROM pg_indexes 
                WHERE tablename = '{table_name}' AND schemaname = 'public'
            """
            result = self.connector.execute_query(query)
            
            indexes = {}
            for row in result:
                index_name = row[0]
                index_def = row[1]
                
                # 解析索引定义
                columns = self._parse_postgresql_index_def(index_def)
                
                indexes[index_name] = {
                    'index_name': index_name,
                    'index_type': self._extract_postgresql_index_type(index_def),
                    'unique': 'UNIQUE' in index_def.upper(),
                    'columns': columns
                }
            
            return indexes
        
        except Exception as e:
            self.logger.error(f"获取PostgreSQL索引信息失败: {e}")
            return {}
    
    def _parse_postgresql_index_def(self, index_def: str) -> List[str]:
        """解析PostgreSQL索引定义"""
        try:
            # 简单解析索引列
            match = re.search(r'\((.*?)\)', index_def)
            if match:
                columns_str = match.group(1)
                # 移除引号并分割
                columns = [col.strip().strip('"') for col in columns_str.split(',')]
                return columns
            return []
        
        except Exception as e:
            self.logger.error(f"解析PostgreSQL索引定义失败: {e}")
            return []
    
    def _extract_postgresql_index_type(self, index_def: str) -> str:
        """提取PostgreSQL索引类型"""
        try:
            if 'USING btree' in index_def.lower():
                return 'BTREE'
            elif 'USING hash' in index_def.lower():
                return 'HASH'
            elif 'USING gist' in index_def.lower():
                return 'GIST'
            elif 'USING gin' in index_def.lower():
                return 'GIN'
            elif 'USING spgist' in index_def.lower():
                return 'SPGIST'
            elif 'USING brin' in index_def.lower():
                return 'BRIN'
            else:
                return 'BTREE'
        
        except Exception as e:
            self.logger.error(f"提取PostgreSQL索引类型失败: {e}")
            return 'BTREE'
    
    def _get_oracle_indexes(self, table_name: str) -> Dict[str, Any]:
        """获取Oracle索引信息"""
        try:
            query = f"""
                SELECT 
                    index_name,
                    index_type,
                    uniqueness,
                    column_name,
                    column_position
                FROM user_ind_columns 
                JOIN user_indexes USING (index_name)
                WHERE table_name = '{table_name.upper()}'
                ORDER BY index_name, column_position
            """
            result = self.connector.execute_query(query)
            
            indexes = {}
            for row in result:
                index_name = row[0]
                index_type = row[1]
                uniqueness = row[2]
                column_name = row[3]
                column_position = row[4]
                
                if index_name not in indexes:
                    indexes[index_name] = {
                        'index_name': index_name,
                        'index_type': index_type,
                        'unique': uniqueness == 'UNIQUE',
                        'columns': []
                    }
                
                indexes[index_name]['columns'].append(column_name)
            
            return indexes
        
        except Exception as e:
            self.logger.error(f"获取Oracle索引信息失败: {e}")
            return {}
    
    def _get_sqlserver_indexes(self, table_name: str) -> Dict[str, Any]:
        """获取SQL Server索引信息"""
        try:
            query = f"""
                SELECT 
                    i.name AS index_name,
                    i.type_desc AS index_type,
                    i.is_unique,
                    c.name AS column_name,
                    ic.key_ordinal AS column_position
                FROM sys.indexes i
                JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
                JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                JOIN sys.tables t ON i.object_id = t.object_id
                WHERE t.name = '{table_name}'
                ORDER BY i.name, ic.key_ordinal
            """
            result = self.connector.execute_query(query)
            
            indexes = {}
            for row in result:
                index_name = row[0]
                index_type = row[1]
                is_unique = row[2]
                column_name = row[3]
                column_position = row[4]
                
                if index_name not in indexes:
                    indexes[index_name] = {
                        'index_name': index_name,
                        'index_type': index_type,
                        'unique': is_unique,
                        'columns': []
                    }
                
                indexes[index_name]['columns'].append(column_name)
            
            return indexes
        
        except Exception as e:
            self.logger.error(f"获取SQL Server索引信息失败: {e}")
            return {}
    
    def _get_index_usage_stats(self, table_name: str) -> Dict[str, Any]:
        """获取索引使用统计"""
        try:
            if self.connector.config.type == DatabaseType.MYSQL:
                return self._get_mysql_index_usage(table_name)
            elif self.connector.config.type == DatabaseType.POSTGRESQL:
                return self._get_postgresql_index_usage(table_name)
            elif self.connector.config.type == DatabaseType.ORACLE:
                return self._get_oracle_index_usage(table_name)
            elif self.connector.config.type == DatabaseType.SQLSERVER:
                return self._get_sqlserver_index_usage(table_name)
            else:
                return {}
        
        except Exception as e:
            self.logger.error(f"获取索引使用统计失败: {e}")
            return {}
    
    def _get_mysql_index_usage(self, table_name: str) -> Dict[str, Any]:
        """获取MySQL索引使用统计"""
        try:
            query = f"""
                SELECT 
                    index_name,
                    table_name,
                    non_unique,
                    seq_in_index,
                    column_name,
                    cardinality
                FROM information_schema.statistics 
                WHERE table_schema = '{self.connector.config.database}' 
                AND table_name = '{table_name}'
            """
            result = self.connector.execute_query(query)
            
            usage_stats = {}
            for row in result:
                index_name = row[0]
                cardinality = row[5]
                
                if index_name not in usage_stats:
                    usage_stats[index_name] = {
                        'cardinality': 0,
                        'usage_count': 0,
                        'last_used': None
                    }
                
                usage_stats[index_name]['cardinality'] += cardinality or 0
            
            return usage_stats
        
        except Exception as e:
            self.logger.error(f"获取MySQL索引使用统计失败: {e}")
            return {}
    
    def _get_postgresql_index_usage(self, table_name: str) -> Dict[str, Any]:
        """获取PostgreSQL索引使用统计"""
        try:
            query = f"""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                WHERE tablename = '{table_name}'
            """
            result = self.connector.execute_query(query)
            
            usage_stats = {}
            for row in result:
                index_name = row[2]
                idx_scan = row[3]
                idx_tup_read = row[4]
                idx_tup_fetch = row[5]
                
                usage_stats[index_name] = {
                    'usage_count': idx_scan,
                    'tuples_read': idx_tup_read,
                    'tuples_fetched': idx_tup_fetch,
                    'last_used': None
                }
            
            return usage_stats
        
        except Exception as e:
            self.logger.error(f"获取PostgreSQL索引使用统计失败: {e}")
            return {}
    
    def _get_oracle_index_usage(self, table_name: str) -> Dict[str, Any]:
        """获取Oracle索引使用统计"""
        try:
            query = f"""
                SELECT 
                    index_name,
                    table_name,
                    used,
                    start_time,
                    end_time
                FROM v$object_usage 
                WHERE table_name = '{table_name.upper()}'
            """
            result = self.connector.execute_query(query)
            
            usage_stats = {}
            for row in result:
                index_name = row[0]
                used = row[2]
                start_time = row[3]
                end_time = row[4]
                
                usage_stats[index_name] = {
                    'used': used == 'YES',
                    'start_time': start_time,
                    'end_time': end_time,
                    'usage_count': 1 if used == 'YES' else 0
                }
            
            return usage_stats
        
        except Exception as e:
            self.logger.error(f"获取Oracle索引使用统计失败: {e}")
            return {}
    
    def _get_sqlserver_index_usage(self, table_name: str) -> Dict[str, Any]:
        """获取SQL Server索引使用统计"""
        try:
            query = f"""
                SELECT 
                    i.name AS index_name,
                    t.name AS table_name,
                    i.type_desc,
                    s.user_seeks,
                    s.user_scans,
                    s.user_lookups,
                    s.user_updates,
                    s.last_user_seek,
                    s.last_user_scan,
                    s.last_user_lookup,
                    s.last_user_update
                FROM sys.indexes i
                JOIN sys.tables t ON i.object_id = t.object_id
                LEFT JOIN sys.dm_db_index_usage_stats s ON i.object_id = s.object_id AND i.index_id = s.index_id
                WHERE t.name = '{table_name}'
            """
            result = self.connector.execute_query(query)
            
            usage_stats = {}
            for row in result:
                index_name = row[0]
                user_seeks = row[4]
                user_scans = row[5]
                user_lookups = row[6]
                user_updates = row[7]
                last_user_seek = row[8]
                last_user_scan = row[9]
                last_user_lookup = row[10]
                last_user_update = row[11]
                
                total_usage = (user_seeks or 0) + (user_scans or 0) + (user_lookups or 0)
                
                usage_stats[index_name] = {
                    'usage_count': total_usage,
                    'user_seeks': user_seeks,
                    'user_scans': user_scans,
                    'user_lookups': user_lookups,
                    'user_updates': user_updates,
                    'last_used': max(last_user_seek, last_user_scan, last_user_lookup, last_user_update)
                }
            
            return usage_stats
        
        except Exception as e:
            self.logger.error(f"获取SQL Server索引使用统计失败: {e}")
            return {}
    
    def _calculate_index_efficiency(self, index_info: Dict[str, Any], usage_stats: Dict[str, Any]) -> float:
        """计算索引效率分数"""
        try:
            if not index_info or not usage_stats:
                return 0.0
            
            efficiency_score = 0.0
            
            for index_name, index_data in index_info.items():
                stats = usage_stats.get(index_name, {})
                
                # 基础分数
                base_score = 50.0
                
                # 使用频率加分
                usage_count = stats.get('usage_count', 0)
                if usage_count > 100:
                    base_score += 30
                elif usage_count > 10:
                    base_score += 20
                elif usage_count > 0:
                    base_score += 10
                
                # 唯一索引加分
                if index_data.get('unique', False):
                    base_score += 10
                
                # 复合索引加分
                if len(index_data.get('columns', [])) > 1:
                    base_score += 5
                
                # 更新频率减分
                update_count = stats.get('user_updates', 0)
                if update_count > usage_count * 2:
                    base_score -= 20
                
                efficiency_score += max(0, min(100, base_score))
            
            # 平均分数
            if index_info:
                efficiency_score /= len(index_info)
            
            return round(efficiency_score, 2)
        
        except Exception as e:
            self.logger.error(f"计算索引效率分数失败: {e}")
            return 0.0
    
    def _generate_index_recommendations(self, table_name: str, index_info: Dict[str, Any],
                                       usage_stats: Dict[str, Any], efficiency_score: float) -> List[Dict[str, Any]]:
        """生成索引优化建议"""
        try:
            recommendations = []
            
            # 整体效率建议
            if efficiency_score < 50:
                recommendations.append({
                    'type': 'overall',
                    'priority': 'high',
                    'description': '索引整体效率较低，建议优化索引策略',
                    'details': f"当前效率分数: {efficiency_score}"
                })
            
            # 未使用索引建议
            for index_name, stats in usage_stats.items():
                usage_count = stats.get('usage_count', 0)
                if usage_count == 0:
                    recommendations.append({
                        'type': 'unused',
                        'priority': 'medium',
                        'description': '发现未使用的索引，建议考虑删除',
                        'details': f"索引: {index_name}"
                    })
            
            # 低效索引建议
            for index_name, stats in usage_stats.items():
                usage_count = stats.get('usage_count', 0)
                update_count = stats.get('user_updates', 0)
                
                if usage_count > 0 and update_count > usage_count * 3:
                    recommendations.append({
                        'type': 'inefficient',
                        'priority': 'medium',
                        'description': '索引维护成本过高，建议评估必要性',
                        'details': f"索引: {index_name}, 使用: {usage_count}, 更新: {update_count}"
                    })
            
            # 缺失索引建议（基于查询分析）
            # 这里可以结合查询分析结果来建议新索引
            
            return recommendations
        
        except Exception as e:
            self.logger.error(f"生成索引优化建议失败: {e}")
            return []

class SQLOptimizer:
    """SQL优化器主类"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connector = DatabaseConnector(config)
        self.query_analyzer = QueryAnalyzer(self.connector)
        self.index_analyzer = IndexAnalyzer(self.connector)
    
    def optimize_database(self, optimization_types: List[OptimizationType] = None) -> Dict[str, Any]:
        """优化数据库"""
        try:
            if optimization_types is None:
                optimization_types = [OptimizationType.QUERY, OptimizationType.INDEX, OptimizationType.TABLE]
            
            results = {}
            
            for opt_type in optimization_types:
                if opt_type == OptimizationType.QUERY:
                    results['query'] = self._optimize_queries()
                elif opt_type == OptimizationType.INDEX:
                    results['index'] = self._optimize_indexes()
                elif opt_type == OptimizationType.TABLE:
                    results['table'] = self._optimize_tables()
                elif opt_type == OptimizationType.EXECUTION_PLAN:
                    results['execution_plan'] = self._optimize_execution_plans()
                elif opt_type == OptimizationType.STATISTICS:
                    results['statistics'] = self._optimize_statistics()
            
            self.logger.info("数据库优化完成")
            
            return results
        
        except Exception as e:
            self.logger.error(f"数据库优化失败: {e}")
            raise
    
    def _optimize_queries(self) -> Dict[str, Any]:
        """优化查询"""
        try:
            # 获取慢查询
            slow_queries = self._get_slow_queries()
            
            query_results = []
            for query in slow_queries:
                analysis = self.query_analyzer.analyze_query(query['query_text'])
                query_results.append(analysis)
            
            return {
                'total_queries': len(query_results),
                'optimizations': [q.optimization_suggestions for q in query_results],
                'performance_improvement': self._calculate_performance_improvement(query_results)
            }
        
        except Exception as e:
            self.logger.error(f"查询优化失败: {e}")
            return {}
    
    def _optimize_indexes(self) -> Dict[str, Any]:
        """优化索引"""
        try:
            index_analyses = self.index_analyzer.analyze_indexes()
            
            return {
                'total_indexes': len(index_analyses),
                'optimizations': [ia.optimization_recommendations for ia in index_analyses],
                'efficiency_improvement': self._calculate_efficiency_improvement(index_analyses)
            }
        
        except Exception as e:
            self.logger.error(f"索引优化失败: {e}")
            return {}
    
    def _optimize_tables(self) -> Dict[str, Any]:
        """优化表结构"""
        try:
            tables = self._get_all_tables()
            table_results = []
            
            for table in tables:
                analysis = self._analyze_table_structure(table)
                table_results.append(analysis)
            
            return {
                'total_tables': len(table_results),
                'optimizations': [t.optimization_suggestions for t in table_results]
            }
        
        except Exception as e:
            self.logger.error(f"表结构优化失败: {e}")
            return {}
    
    def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """获取慢查询"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                query = """
                    SELECT 
                        query_time,
                        lock_time,
                        rows_sent,
                        rows_examined,
                        sql_text
                    FROM mysql.slow_log 
                    WHERE query_time > 5 
                    ORDER BY query_time DESC 
                    LIMIT 100
                """
            elif self.config.type == DatabaseType.POSTGRESQL:
                query = """
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements 
                    WHERE mean_time > 1000 
                    ORDER BY mean_time DESC 
                    LIMIT 100
                """
            else:
                return []
            
            result = self.connector.execute_query(query)
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    'query_text': row[0],
                    'execution_time': float(row[1]) if row[1] else 0,
                    'rows_examined': int(row[2]) if row[2] else 0
                })
            
            return slow_queries
        
        except Exception as e:
            self.logger.error(f"获取慢查询失败: {e}")
            return []
    
    def _get_all_tables(self) -> List[str]:
        """获取所有表名"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                query = "SHOW TABLES"
            elif self.config.type == DatabaseType.POSTGRESQL:
                query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            elif self.config.type == DatabaseType.ORACLE:
                query = "SELECT table_name FROM user_tables"
            elif self.config.type == DatabaseType.SQLSERVER:
                query = "SELECT name FROM sys.tables"
            else:
                return []
            
            result = self.connector.execute_query(query)
            return [row[0] for row in result]
        
        except Exception as e:
            self.logger.error(f"获取表列表失败: {e}")
            return []
    
    def _analyze_table_structure(self, table_name: str) -> Dict[str, Any]:
        """分析表结构"""
        try:
            # 获取表结构信息
            structure_info = self._get_table_structure(table_name)
            
            # 获取表统计信息
            stats_info = self._get_table_statistics(table_name)
            
            # 生成优化建议
            suggestions = self._generate_table_suggestions(structure_info, stats_info)
            
            return {
                'table_name': table_name,
                'structure_info': structure_info,
                'stats_info': stats_info,
                'optimization_suggestions': suggestions
            }
        
        except Exception as e:
            self.logger.error(f"分析表结构失败: {e}")
            return {}
    
    def _get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """获取表结构信息"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                query = f"DESCRIBE {table_name}"
            elif self.config.type == DatabaseType.POSTGRESQL:
                query = f"""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """
            else:
                return {}
            
            result = self.connector.execute_query(query)
            
            columns = []
            for row in result:
                columns.append({
                    'column_name': row[0],
                    'data_type': row[1],
                    'is_nullable': row[2],
                    'default_value': row[3]
                })
            
            return {'columns': columns}
        
        except Exception as e:
            self.logger.error(f"获取表结构信息失败: {e}")
            return {}
    
    def _get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """获取表统计信息"""
        try:
            if self.config.type == DatabaseType.MYSQL:
                query = f"""
                    SELECT 
                        table_rows,
                        data_length,
                        index_length,
                        data_free
                    FROM information_schema.tables 
                    WHERE table_schema = '{self.config.database}' 
                    AND table_name = '{table_name}'
                """
            elif self.config.type == DatabaseType.POSTGRESQL:
                query = f"""
                    SELECT 
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup
                    FROM pg_stat_user_tables 
                    WHERE tablename = '{table_name}'
                """
            else:
                return {}
            
            result = self.connector.execute_query(query)
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'row_count': row[0],
                    'data_size': row[1],
                    'index_size': row[2],
                    'free_space': row[3]
                }
            
            return {}
        
        except Exception as e:
            self.logger.error(f"获取表统计信息失败: {e}")
            return {}
    
    def _generate_table_suggestions(self, structure_info: Dict[str, Any], stats_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成表优化建议"""
        try:
            suggestions = []
            
            # 基于表大小的建议
            data_size = stats_info.get('data_size', 0)
            if data_size > 1024 * 1024 * 1024:  # 1GB
                suggestions.append({
                    'type': 'size',
                    'priority': 'medium',
                    'description': '表数据量较大，建议考虑分区',
                    'details': f"表大小: {data_size / 1024 / 1024:.2f}MB"
                })
            
            # 基于碎片空间的建议
            free_space = stats_info.get('free_space', 0)
            if free_space > data_size * 0.1:  # 碎片超过10%
                suggestions.append({
                    'type': 'fragmentation',
                    'priority': 'medium',
                    'description': '表碎片较多，建议进行优化',
                    'details': f"碎片空间: {free_space / 1024 / 1024:.2f}MB"
                })
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"生成表优化建议失败: {e}")
            return []
    
    def _calculate_performance_improvement(self, query_results: List[QueryAnalysis]) -> Dict[str, Any]:
        """计算性能改善"""
        try:
            total_improvement = 0
            optimized_queries = 0
            
            for result in query_results:
                if result.optimization_suggestions:
                    optimized_queries += 1
                    # 简单的性能改善估算
                    total_improvement += len(result.optimization_suggestions) * 10
            
            return {
                'optimized_queries': optimized_queries,
                'estimated_improvement': total_improvement,
                'improvement_percentage': (total_improvement / len(query_results)) if query_results else 0
            }
        
        except Exception as e:
            self.logger.error(f"计算性能改善失败: {e}")
            return {}
    
    def _calculate_efficiency_improvement(self, index_analyses: List[IndexAnalysis]) -> Dict[str, Any]:
        """计算效率改善"""
        try:
            total_efficiency = sum(ia.efficiency_score for ia in index_analyses)
            avg_efficiency = total_efficiency / len(index_analyses) if index_analyses else 0
            
            optimized_indexes = sum(1 for ia in index_analyses if ia.optimization_recommendations)
            
            return {
                'total_indexes': len(index_analyses),
                'optimized_indexes': optimized_indexes,
                'average_efficiency': avg_efficiency,
                'improvement_potential': 100 - avg_efficiency
            }
        
        except Exception as e:
            self.logger.error(f"计算效率改善失败: {e}")
            return {}

# 使用示例
# 数据库配置
db_config = DatabaseConfig(
    config_id=str(uuid.uuid4()),
    name="mysql_main",
    type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    username="root",
    password="password",
    database="test_db"
)

# 创建SQL优化器
optimizer = SQLOptimizer(db_config)
optimizer.connector.connect()

# 分析单个查询
query = "SELECT * FROM users WHERE age > 25 ORDER BY name"
query_analysis = optimizer.query_analyzer.analyze_query(query, AnalysisLevel.DETAILED)

print(f"查询分析结果:")
print(f"执行时间: {query_analysis.execution_time}秒")
print(f"扫描行数: {query_analysis.scan_rows}")
print(f"返回行数: {query_analysis.return_rows}")
print(f"优化建议: {len(query_analysis.optimization_suggestions)}条")

# 分析索引
index_analyses = optimizer.index_analyzer.analyze_indexes("users")
for analysis in index_analyses:
    print(f"索引: {analysis.index_name}, 效率分数: {analysis.efficiency_score}")
    print(f"优化建议: {len(analysis.optimization_recommendations)}条")

# 全面优化数据库
optimization_results = optimizer.optimize_database([
    OptimizationType.QUERY,
    OptimizationType.INDEX,
    OptimizationType.TABLE
])

print(f"优化结果:")
print(f"查询优化: {optimization_results.get('query', {}).get('total_queries', 0)}个查询")
print(f"索引优化: {optimization_results.get('index', {}).get('total_indexes', 0)}个索引")

# 断开连接
optimizer.connector.disconnect()
```

## 参考资源

### SQL优化文档
- [MySQL查询优化](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [PostgreSQL查询优化](https://www.postgresql.org/docs/current/query-optimization.html)
- [Oracle查询优化](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/)
- [SQL Server查询优化](https://docs.microsoft.com/en-us/sql/relational-databases/performance/query-tuning?)

### 执行计划分析
- [MySQL执行计划](https://dev.mysql.com/doc/refman/8.0/en/explain.html)
- [PostgreSQL执行计划](https://www.postgresql.org/docs/current/using-explain.html)
- [Oracle执行计划](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/understanding-execution-plans.html)
- [SQL Server执行计划](https://docs.microsoft.com/en-us/sql/relational-databases/performance/showplan-logical-and-physical-operators-reference)

### 索引优化
- [MySQL索引优化](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
- [PostgreSQL索引优化](https://www.postgresql.org/docs/current/indexes.html)
- [Oracle索引优化](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/optimizing-indexes.html)
- [SQL Server索引优化](https://docs.microsoft.com/en-us/sql/relational-databases/indexes/indexes)

### 性能监控
- [MySQL性能监控](https://dev.mysql.com/doc/refman/8.0/en/performance-schema.html)
- [PostgreSQL性能监控](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [Oracle性能监控](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/monitoring-database-performance.html)
- [SQL Server性能监控](https://docs.microsoft.com/en-us/sql/relational-databases/performance/monitoring-performance-by-using-the-query-store)

### 最佳实践
- [SQL优化最佳实践](https://www.sqlshack.com/sql-performance-tuning-best-practices/)
- [数据库设计规范](https://github.com/karlseguin/the-little-mongodb-book)
- [查询优化技术](https://use-the-index-luke.com/)
- [数据库性能调优](https://www.percona.com/blog/)
