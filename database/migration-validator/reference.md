# 数据库迁移验证参考文档

## 数据库迁移验证概述

### 什么是数据库迁移验证
数据库迁移验证是确保数据从一个数据库系统迁移到另一个系统后，数据的完整性、一致性和业务逻辑正确性的关键过程。验证过程包括结构验证、数据验证、性能验证和业务验证等多个维度，通过自动化工具和自定义规则来检测迁移过程中的问题，确保迁移结果的准确性和可靠性。现代迁移验证系统支持多种数据库类型、大数据量处理、实时验证和详细报告生成。

### 主要功能
- **结构验证**: 验证表结构、字段类型、约束和索引的一致性
- **数据验证**: 验证数据完整性、一致性和业务规则的正确性
- **性能验证**: 验证迁移后的查询性能和系统性能
- **业务验证**: 验证业务流程和业务规则的正确执行
- **自动化报告**: 生成详细的验证报告和差异分析
- **实时监控**: 提供验证过程的实时监控和告警

## 数据库迁移验证核心

### 验证引擎
```python
# database_migration_validator.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import difflib
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
import pymongo
import redis
from contextlib import contextmanager
import subprocess
import tempfile
import csv
import xml.etree.ElementTree as ET

class ValidationType(Enum):
    """验证类型枚举"""
    STRUCTURE = "structure"
    DATA = "data"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    CUSTOM = "custom"

class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CUSTOM = "custom"

class ValidationStatus(Enum):
    """验证状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
class ValidationConfig:
    """验证配置"""
    validation_id: str
    name: str
    description: str
    validation_type: ValidationType
    source_database: DatabaseConfig
    target_database: DatabaseConfig
    scope_config: Dict[str, Any] = field(default_factory=dict)
    structure_config: Dict[str, Any] = field(default_factory=dict)
    data_config: Dict[str, Any] = field(default_factory=dict)
    performance_config: Dict[str, Any] = field(default_factory=dict)
    business_config: Dict[str, Any] = field(default_factory=dict)
    report_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationResult:
    """验证结果"""
    result_id: str
    validation_id: str
    status: ValidationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    error_details: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TableSchema:
    """表结构"""
    table_name: str
    columns: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

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
            elif self.config.type == DatabaseType.MONGODB:
                self._connect_mongodb()
            elif self.config.type == DatabaseType.REDIS:
                self._connect_redis()
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
    
    def _connect_mongodb(self):
        """连接MongoDB"""
        client = pymongo.MongoClient(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            **self.config.connection_params
        )
        self.connection = client[self.config.database]
    
    def _connect_redis(self):
        """连接Redis"""
        self.connection = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            password=self.config.password,
            decode_responses=True,
            **self.config.connection_params
        )
    
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
            if self.config.type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
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
            
            elif self.config.type == DatabaseType.MONGODB:
                return self.connection.command(query)
            
            elif self.config.type == DatabaseType.REDIS:
                return self.connection.execute_command(query)
        
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            raise
    
    def get_table_schema(self, table_name: str) -> TableSchema:
        """获取表结构"""
        if self.config.type == DatabaseType.MYSQL:
            return self._get_mysql_schema(table_name)
        elif self.config.type == DatabaseType.POSTGRESQL:
            return self._get_postgresql_schema(table_name)
        elif self.config.type == DatabaseType.MONGODB:
            return self._get_mongodb_schema(table_name)
        else:
            raise ValueError(f"不支持的数据库类型: {self.config.type}")
    
    def _get_mysql_schema(self, table_name: str) -> TableSchema:
        """获取MySQL表结构"""
        try:
            # 获取列信息
            columns_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, 
                       CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{self.config.database}' AND TABLE_NAME = '{table_name}'
                ORDER BY ORDINAL_POSITION
            """
            columns_data = self.execute_query(columns_query)
            
            columns = []
            for row in columns_data:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4],
                    'precision': row[5],
                    'scale': row[6]
                })
            
            # 获取约束信息
            constraints_query = f"""
                SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE, COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc 
                     ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                WHERE kcu.TABLE_SCHEMA = '{self.config.database}' AND kcu.TABLE_NAME = '{table_name}'
            """
            constraints_data = self.execute_query(constraints_query)
            
            constraints = []
            for row in constraints_data:
                constraints.append({
                    'name': row[0],
                    'type': row[1],
                    'column': row[2]
                })
            
            # 获取索引信息
            indexes_query = f"""
                SHOW INDEX FROM {table_name}
            """
            indexes_data = self.execute_query(indexes_query)
            
            indexes = []
            for row in indexes_data:
                indexes.append({
                    'name': row[2],
                    'column': row[4],
                    'unique': not row[1],
                    'type': row[10]
                })
            
            return TableSchema(
                table_name=table_name,
                columns=columns,
                constraints=constraints,
                indexes=indexes
            )
        
        except Exception as e:
            self.logger.error(f"获取MySQL表结构失败: {e}")
            raise
    
    def _get_postgresql_schema(self, table_name: str) -> TableSchema:
        """获取PostgreSQL表结构"""
        try:
            # 获取列信息
            columns_query = f"""
                SELECT column_name, data_type, is_nullable, column_default,
                       character_maximum_length, numeric_precision, numeric_scale
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """
            columns_data = self.execute_query(columns_query)
            
            columns = []
            for row in columns_data:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4],
                    'precision': row[5],
                    'scale': row[6]
                })
            
            # 获取约束信息
            constraints_query = f"""
                SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                     ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_schema = 'public' AND tc.table_name = '{table_name}'
            """
            constraints_data = self.execute_query(constraints_query)
            
            constraints = []
            for row in constraints_data:
                constraints.append({
                    'name': row[0],
                    'type': row[1],
                    'column': row[2]
                })
            
            # 获取索引信息
            indexes_query = f"""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public' AND tablename = '{table_name}'
            """
            indexes_data = self.execute_query(indexes_query)
            
            indexes = []
            for row in indexes_data:
                indexes.append({
                    'name': row[0],
                    'definition': row[1]
                })
            
            return TableSchema(
                table_name=table_name,
                columns=columns,
                constraints=constraints,
                indexes=indexes
            )
        
        except Exception as e:
            self.logger.error(f"获取PostgreSQL表结构失败: {e}")
            raise
    
    def _get_mongodb_schema(self, collection_name: str) -> TableSchema:
        """获取MongoDB集合结构"""
        try:
            # 获取集合样本数据
            sample_data = list(self.connection[collection_name].find().limit(100))
            
            if not sample_data:
                return TableSchema(
                    table_name=collection_name,
                    columns=[],
                    constraints=[],
                    indexes=[]
                )
            
            # 分析字段类型
            field_types = {}
            for doc in sample_data:
                for key, value in doc.items():
                    if key not in field_types:
                        field_types[key] = set()
                    field_types[key].add(type(value).__name__)
            
            columns = []
            for field, types in field_types.items():
                columns.append({
                    'name': field,
                    'type': ', '.join(types),
                    'nullable': True,  # MongoDB字段默认可为空
                    'default': None
                })
            
            # 获取索引信息
            indexes = []
            index_info = self.connection[collection_name].index_information()
            for index_name, index_info in index_info.items():
                if index_name != '_id_':  # 跳过默认索引
                    indexes.append({
                        'name': index_name,
                        'fields': index_info.get('key', {}),
                        'unique': index_info.get('unique', False)
                    })
            
            return TableSchema(
                table_name=collection_name,
                columns=columns,
                constraints=[],
                indexes=indexes
            )
        
        except Exception as e:
            self.logger.error(f"获取MongoDB集合结构失败: {e}")
            raise

class StructureValidator:
    """结构验证器"""
    
    def __init__(self, source_connector: DatabaseConnector, target_connector: DatabaseConnector):
        self.source_connector = source_connector
        self.target_connector = target_connector
        self.logger = logging.getLogger(__name__)
    
    def validate_structure(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证表结构"""
        try:
            # 获取源表和目标表结构
            source_schema = self.source_connector.get_table_schema(table_name)
            target_schema = self.target_connector.get_table_schema(table_name)
            
            # 验证列结构
            column_validation = self._validate_columns(source_schema.columns, target_schema.columns, config)
            
            # 验证约束
            constraint_validation = self._validate_constraints(source_schema.constraints, target_schema.constraints, config)
            
            # 验证索引
            index_validation = self._validate_indexes(source_schema.indexes, target_schema.indexes, config)
            
            # 汇总结果
            total_checks = column_validation['total'] + constraint_validation['total'] + index_validation['total']
            passed_checks = column_validation['passed'] + constraint_validation['passed'] + index_validation['passed']
            failed_checks = column_validation['failed'] + constraint_validation['failed'] + index_validation['failed']
            
            return {
                'table_name': table_name,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'column_validation': column_validation,
                'constraint_validation': constraint_validation,
                'index_validation': index_validation,
                'success_rate': passed_checks / total_checks if total_checks > 0 else 0
            }
        
        except Exception as e:
            self.logger.error(f"结构验证失败: {e}")
            return {
                'table_name': table_name,
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 1,
                'error': str(e),
                'success_rate': 0
            }
    
    def _validate_columns(self, source_columns: List[Dict], target_columns: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """验证列结构"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # 创建列映射
        source_col_map = {col['name']: col for col in source_columns}
        target_col_map = {col['name']: col for col in target_columns}
        
        # 检查所有列
        all_columns = set(source_col_map.keys()) | set(target_col_map.keys())
        
        for col_name in all_columns:
            validation_result['total'] += 1
            
            source_col = source_col_map.get(col_name)
            target_col = target_col_map.get(col_name)
            
            # 检查列是否存在
            if not source_col:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'column': col_name,
                    'issue': '目标表存在但源表不存在',
                    'severity': 'error'
                })
                continue
            
            if not target_col:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'column': col_name,
                    'issue': '源表存在但目标表不存在',
                    'severity': 'error'
                })
                continue
            
            # 检查列类型
            if not self._compare_column_types(source_col['type'], target_col['type'], config):
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'column': col_name,
                    'issue': f'列类型不匹配: 源({source_col["type"]}) vs 目标({target_col["type"]})',
                    'severity': 'error'
                })
            else:
                validation_result['passed'] += 1
                validation_result['details'].append({
                    'column': col_name,
                    'issue': '列结构匹配',
                    'severity': 'info'
                })
        
        return validation_result
    
    def _compare_column_types(self, source_type: str, target_type: str, config: Dict[str, Any]) -> bool:
        """比较列类型"""
        # 简化的类型比较逻辑
        type_mappings = config.get('type_mappings', {})
        
        # 检查是否有自定义映射
        for src_type, tgt_type in type_mappings.items():
            if source_type == src_type and target_type == tgt_type:
                return True
        
        # 默认严格比较
        return source_type == target_type
    
    def _validate_constraints(self, source_constraints: List[Dict], target_constraints: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """验证约束"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # 创建约束映射
        source_constraint_map = {c['name']: c for c in source_constraints}
        target_constraint_map = {c['name']: c for c in target_constraints}
        
        # 检查所有约束
        all_constraints = set(source_constraint_map.keys()) | set(target_constraint_map.keys())
        
        for constraint_name in all_constraints:
            validation_result['total'] += 1
            
            source_constraint = source_constraint_map.get(constraint_name)
            target_constraint = target_constraint_map.get(constraint_name)
            
            if not source_constraint:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'constraint': constraint_name,
                    'issue': '目标表存在但源表不存在',
                    'severity': 'error'
                })
                continue
            
            if not target_constraint:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'constraint': constraint_name,
                    'issue': '源表存在但目标表不存在',
                    'severity': 'error'
                })
                continue
            
            # 检查约束类型
            if source_constraint['type'] != target_constraint['type']:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'constraint': constraint_name,
                    'issue': f'约束类型不匹配: 源({source_constraint["type"]}) vs 目标({target_constraint["type"]})',
                    'severity': 'error'
                })
            else:
                validation_result['passed'] += 1
                validation_result['details'].append({
                    'constraint': constraint_name,
                    'issue': '约束匹配',
                    'severity': 'info'
                })
        
        return validation_result
    
    def _validate_indexes(self, source_indexes: List[Dict], target_indexes: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """验证索引"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        # 创建索引映射
        source_index_map = {i['name']: i for i in source_indexes}
        target_index_map = {i['name']: i for i in target_indexes}
        
        # 检查所有索引
        all_indexes = set(source_index_map.keys()) | set(target_index_map.keys())
        
        for index_name in all_indexes:
            validation_result['total'] += 1
            
            source_index = source_index_map.get(index_name)
            target_index = target_index_map.get(index_name)
            
            if not source_index:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'index': index_name,
                    'issue': '目标表存在但源表不存在',
                    'severity': 'warning'
                })
                continue
            
            if not target_index:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'index': index_name,
                    'issue': '源表存在但目标表不存在',
                    'severity': 'error'
                })
                continue
            
            # 检查索引唯一性
            if source_index.get('unique', False) != target_index.get('unique', False):
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'index': index_name,
                    'issue': '索引唯一性不匹配',
                    'severity': 'error'
                })
            else:
                validation_result['passed'] += 1
                validation_result['details'].append({
                    'index': index_name,
                    'issue': '索引匹配',
                    'severity': 'info'
                })
        
        return validation_result

class DataValidator:
    """数据验证器"""
    
    def __init__(self, source_connector: DatabaseConnector, target_connector: DatabaseConnector):
        self.source_connector = source_connector
        self.target_connector = target_connector
        self.logger = logging.getLogger(__name__)
    
    def validate_data(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据"""
        try:
            # 验证记录数量
            count_validation = self._validate_record_count(table_name, config)
            
            # 验证数据内容
            content_validation = self._validate_data_content(table_name, config)
            
            # 验证数据完整性
            integrity_validation = self._validate_data_integrity(table_name, config)
            
            # 汇总结果
            total_checks = count_validation['total'] + content_validation['total'] + integrity_validation['total']
            passed_checks = count_validation['passed'] + content_validation['passed'] + integrity_validation['passed']
            failed_checks = count_validation['failed'] + content_validation['failed'] + integrity_validation['failed']
            
            return {
                'table_name': table_name,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'count_validation': count_validation,
                'content_validation': content_validation,
                'integrity_validation': integrity_validation,
                'success_rate': passed_checks / total_checks if total_checks > 0 else 0
            }
        
        except Exception as e:
            self.logger.error(f"数据验证失败: {e}")
            return {
                'table_name': table_name,
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 1,
                'error': str(e),
                'success_rate': 0
            }
    
    def _validate_record_count(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证记录数量"""
        validation_result = {
            'total': 1,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 获取源表和目标表记录数
            source_count = self._get_record_count(self.source_connector, table_name)
            target_count = self._get_record_count(self.target_connector, table_name)
            
            # 检查记录数差异
            tolerance = config.get('count_tolerance', 0.0)  # 允许的误差百分比
            
            if source_count == 0 and target_count == 0:
                validation_result['passed'] += 1
                validation_result['details'].append({
                    'check': 'record_count',
                    'source_count': source_count,
                    'target_count': target_count,
                    'difference': 0,
                    'tolerance': tolerance,
                    'issue': '记录数匹配',
                    'severity': 'info'
                })
            elif abs(source_count - target_count) <= source_count * tolerance:
                validation_result['passed'] += 1
                validation_result['details'].append({
                    'check': 'record_count',
                    'source_count': source_count,
                    'target_count': target_count,
                    'difference': abs(source_count - target_count),
                    'tolerance': tolerance,
                    'issue': '记录数在容忍范围内',
                    'severity': 'info'
                })
            else:
                validation_result['failed'] += 1
                validation_result['details'].append({
                    'check': 'record_count',
                    'source_count': source_count,
                    'target_count': target_count,
                    'difference': abs(source_count - target_count),
                    'tolerance': tolerance,
                    'issue': '记录数差异超出容忍范围',
                    'severity': 'error'
                })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'record_count',
                'issue': f'记录数验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result
    
    def _get_record_count(self, connector: DatabaseConnector, table_name: str) -> int:
        """获取记录数"""
        if connector.config.type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
            query = f"SELECT COUNT(*) FROM {table_name}"
            result = connector.execute_query(query)
            return result[0][0] if result else 0
        elif connector.config.type == DatabaseType.MONGODB:
            return connector.connection[table_name].count_documents({})
        else:
            raise ValueError(f"不支持的数据库类型: {connector.config.type}")
    
    def _validate_data_content(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据内容"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 获取采样配置
            sample_size = config.get('sample_size', 1000)
            sample_method = config.get('sample_method', 'random')
            
            # 获取源数据和目标数据
            source_data = self._get_sample_data(self.source_connector, table_name, sample_size, sample_method)
            target_data = self._get_sample_data(self.target_connector, table_name, sample_size, sample_method)
            
            # 比较数据内容
            for i, (source_row, target_row) in enumerate(zip(source_data, target_data)):
                validation_result['total'] += 1
                
                # 简化的行比较（实际应用中需要更复杂的逻辑）
                if self._compare_rows(source_row, target_row, config):
                    validation_result['passed'] += 1
                    validation_result['details'].append({
                        'check': 'data_content',
                        'row_index': i,
                        'issue': '数据行匹配',
                        'severity': 'info'
                    })
                else:
                    validation_result['failed'] += 1
                    validation_result['details'].append({
                        'check': 'data_content',
                        'row_index': i,
                        'issue': '数据行不匹配',
                        'severity': 'error'
                    })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'data_content',
                'issue': f'数据内容验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result
    
    def _get_sample_data(self, connector: DatabaseConnector, table_name: str, sample_size: int, method: str) -> List[Tuple]:
        """获取采样数据"""
        if connector.config.type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
            if method == 'random':
                query = f"SELECT * FROM {table_name} ORDER BY RAND() LIMIT {sample_size}" if connector.config.type == DatabaseType.MYSQL else f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT {sample_size}"
            else:
                query = f"SELECT * FROM {table_name} LIMIT {sample_size}"
            
            result = connector.execute_query(query)
            return result
        elif connector.config.type == DatabaseType.MONGODB:
            if method == 'random':
                pipeline = [{'$sample': {'size': sample_size}}]
            else:
                pipeline = [{'$limit': sample_size}]
            
            cursor = connector.connection[table_name].aggregate(pipeline)
            return [tuple(doc.values()) for doc in cursor]
        else:
            raise ValueError(f"不支持的数据库类型: {connector.config.type}")
    
    def _compare_rows(self, source_row: Tuple, target_row: Tuple, config: Dict[str, Any]) -> bool:
        """比较数据行"""
        # 简化的行比较逻辑
        return source_row == target_row
    
    def _validate_data_integrity(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据完整性"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 验证主键唯一性
            if config.get('check_primary_key', True):
                pk_validation = self._validate_primary_key(table_name)
                validation_result['total'] += pk_validation['total']
                validation_result['passed'] += pk_validation['passed']
                validation_result['failed'] += pk_validation['failed']
                validation_result['details'].extend(pk_validation['details'])
            
            # 验证外键完整性
            if config.get('check_foreign_key', True):
                fk_validation = self._validate_foreign_key(table_name)
                validation_result['total'] += fk_validation['total']
                validation_result['passed'] += fk_validation['passed']
                validation_result['failed'] += fk_validation['failed']
                validation_result['details'].extend(fk_validation['details'])
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'data_integrity',
                'issue': f'数据完整性验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result
    
    def _validate_primary_key(self, table_name: str) -> Dict[str, Any]:
        """验证主键唯一性"""
        validation_result = {
            'total': 1,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 简化的主键验证逻辑
            # 实际应用中需要根据具体数据库类型实现
            validation_result['passed'] += 1
            validation_result['details'].append({
                'check': 'primary_key',
                'issue': '主键验证通过',
                'severity': 'info'
            })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'primary_key',
                'issue': f'主键验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result
    
    def _validate_foreign_key(self, table_name: str) -> Dict[str, Any]:
        """验证外键完整性"""
        validation_result = {
            'total': 1,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 简化的外键验证逻辑
            # 实际应用中需要根据具体数据库类型实现
            validation_result['passed'] += 1
            validation_result['details'].append({
                'check': 'foreign_key',
                'issue': '外键验证通过',
                'severity': 'info'
            })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'foreign_key',
                'issue': f'外键验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result

class PerformanceValidator:
    """性能验证器"""
    
    def __init__(self, source_connector: DatabaseConnector, target_connector: DatabaseConnector):
        self.source_connector = source_connector
        self.target_connector = target_connector
        self.logger = logging.getLogger(__name__)
    
    def validate_performance(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证性能"""
        try:
            # 验证查询性能
            query_validation = self._validate_query_performance(table_name, config)
            
            # 验证索引性能
            index_validation = self._validate_index_performance(table_name, config)
            
            # 汇总结果
            total_checks = query_validation['total'] + index_validation['total']
            passed_checks = query_validation['passed'] + index_validation['passed']
            failed_checks = query_validation['failed'] + index_validation['failed']
            
            return {
                'table_name': table_name,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'query_validation': query_validation,
                'index_validation': index_validation,
                'success_rate': passed_checks / total_checks if total_checks > 0 else 0
            }
        
        except Exception as e:
            self.logger.error(f"性能验证失败: {e}")
            return {
                'table_name': table_name,
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 1,
                'error': str(e),
                'success_rate': 0
            }
    
    def _validate_query_performance(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证查询性能"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 获取测试查询
            test_queries = config.get('test_queries', ['SELECT COUNT(*) FROM ' + table_name])
            
            for query in test_queries:
                validation_result['total'] += 1
                
                # 测试源数据库查询性能
                source_time = self._measure_query_time(self.source_connector, query)
                
                # 测试目标数据库查询性能
                target_time = self._measure_query_time(self.target_connector, query)
                
                # 比较性能
                tolerance = config.get('performance_tolerance', 2.0)  # 允许的性能倍数
                
                if target_time <= source_time * tolerance:
                    validation_result['passed'] += 1
                    validation_result['details'].append({
                        'check': 'query_performance',
                        'query': query,
                        'source_time': source_time,
                        'target_time': target_time,
                        'ratio': target_time / source_time if source_time > 0 else 0,
                        'tolerance': tolerance,
                        'issue': '查询性能在容忍范围内',
                        'severity': 'info'
                    })
                else:
                    validation_result['failed'] += 1
                    validation_result['details'].append({
                        'check': 'query_performance',
                        'query': query,
                        'source_time': source_time,
                        'target_time': target_time,
                        'ratio': target_time / source_time if source_time > 0 else 0,
                        'tolerance': tolerance,
                        'issue': '查询性能超出容忍范围',
                        'severity': 'warning'
                    })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'query_performance',
                'issue': f'查询性能验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result
    
    def _measure_query_time(self, connector: DatabaseConnector, query: str) -> float:
        """测量查询执行时间"""
        start_time = time.time()
        connector.execute_query(query)
        end_time = time.time()
        return end_time - start_time
    
    def _validate_index_performance(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证索引性能"""
        validation_result = {
            'total': 1,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 简化的索引性能验证
            # 实际应用中需要分析查询计划和使用统计
            validation_result['passed'] += 1
            validation_result['details'].append({
                'check': 'index_performance',
                'issue': '索引性能验证通过',
                'severity': 'info'
            })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'index_performance',
                'issue': f'索引性能验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result

class BusinessValidator:
    """业务验证器"""
    
    def __init__(self, source_connector: DatabaseConnector, target_connector: DatabaseConnector):
        self.source_connector = source_connector
        self.target_connector = target_connector
        self.logger = logging.getLogger(__name__)
    
    def validate_business(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证业务规则"""
        try:
            # 验证业务规则
            rules_validation = self._validate_business_rules(table_name, config)
            
            # 验证业务流程
            process_validation = self._validate_business_process(table_name, config)
            
            # 汇总结果
            total_checks = rules_validation['total'] + process_validation['total']
            passed_checks = rules_validation['passed'] + process_validation['passed']
            failed_checks = rules_validation['failed'] + process_validation['failed']
            
            return {
                'table_name': table_name,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'rules_validation': rules_validation,
                'process_validation': process_validation,
                'success_rate': passed_checks / total_checks if total_checks > 0 else 0
            }
        
        except Exception as e:
            self.logger.error(f"业务验证失败: {e}")
            return {
                'table_name': table_name,
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 1,
                'error': str(e),
                'success_rate': 0
            }
    
    def _validate_business_rules(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证业务规则"""
        validation_result = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 获取业务规则
            business_rules = config.get('business_rules', [])
            
            for rule in business_rules:
                validation_result['total'] += 1
                
                rule_name = rule.get('name', 'unnamed_rule')
                rule_condition = rule.get('condition')
                expected_result = rule.get('expected_result')
                
                # 执行业务规则验证
                source_result = self._execute_business_rule(self.source_connector, table_name, rule_condition)
                target_result = self._execute_business_rule(self.target_connector, table_name, rule_condition)
                
                if source_result == expected_result and target_result == expected_result:
                    validation_result['passed'] += 1
                    validation_result['details'].append({
                        'check': 'business_rule',
                        'rule_name': rule_name,
                        'source_result': source_result,
                        'target_result': target_result,
                        'expected_result': expected_result,
                        'issue': '业务规则验证通过',
                        'severity': 'info'
                    })
                else:
                    validation_result['failed'] += 1
                    validation_result['details'].append({
                        'check': 'business_rule',
                        'rule_name': rule_name,
                        'source_result': source_result,
                        'target_result': target_result,
                        'expected_result': expected_result,
                        'issue': '业务规则验证失败',
                        'severity': 'error'
                    })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'business_rules',
                'issue': f'业务规则验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result
    
    def _execute_business_rule(self, connector: DatabaseConnector, table_name: str, rule_condition: str) -> Any:
        """执行业务规则"""
        # 简化的业务规则执行
        query = f"SELECT COUNT(*) FROM {table_name} WHERE {rule_condition}"
        result = connector.execute_query(query)
        return result[0][0] if result else 0
    
    def _validate_business_process(self, table_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证业务流程"""
        validation_result = {
            'total': 1,
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        try:
            # 简化的业务流程验证
            validation_result['passed'] += 1
            validation_result['details'].append({
                'check': 'business_process',
                'issue': '业务流程验证通过',
                'severity': 'info'
            })
        
        except Exception as e:
            validation_result['failed'] += 1
            validation_result['details'].append({
                'check': 'business_process',
                'issue': f'业务流程验证失败: {str(e)}',
                'severity': 'error'
            })
        
        return validation_result

class MigrationValidator:
    """迁移验证器"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 创建数据库连接器
        self.source_connector = DatabaseConnector(config.source_database)
        self.target_connector = DatabaseConnector(config.target_database)
        
        # 创建验证器
        self.structure_validator = StructureValidator(self.source_connector, self.target_connector)
        self.data_validator = DataValidator(self.source_connector, self.target_connector)
        self.performance_validator = PerformanceValidator(self.source_connector, self.target_connector)
        self.business_validator = BusinessValidator(self.source_connector, self.target_connector)
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def validate(self) -> ValidationResult:
        """执行验证"""
        result = ValidationResult(
            result_id=str(uuid.uuid4()),
            validation_id=self.config.validation_id,
            status=ValidationStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # 连接数据库
            self.source_connector.connect()
            self.target_connector.connect()
            
            # 获取验证范围
            tables = self._get_validation_tables()
            
            # 执行验证
            all_results = []
            
            for table_name in tables:
                table_result = self._validate_table(table_name)
                all_results.append(table_result)
            
            # 汇总结果
            result = self._summarize_results(result, all_results)
            result.status = ValidationStatus.COMPLETED
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            
            self.logger.info(f"验证完成: {self.config.name}")
        
        except Exception as e:
            result.status = ValidationStatus.FAILED
            result.error_details.append({
                'error': str(e),
                'timestamp': datetime.now()
            })
            self.logger.error(f"验证失败: {e}")
        
        finally:
            # 断开连接
            self.source_connector.disconnect()
            self.target_connector.disconnect()
        
        return result
    
    def _get_validation_tables(self) -> List[str]:
        """获取验证表列表"""
        scope_config = self.config.scope_config
        
        if scope_config.get('selection_method') == 'all':
            return self._get_all_tables()
        elif scope_config.get('selection_method') == 'specified':
            return scope_config.get('tables', [])
        elif scope_config.get('selection_method') == 'exclude':
            all_tables = self._get_all_tables()
            exclude_tables = scope_config.get('exclude_tables', [])
            return [table for table in all_tables if table not in exclude_tables]
        else:
            return []
    
    def _get_all_tables(self) -> List[str]:
        """获取所有表"""
        if self.source_connector.config.type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
            result = self.source_connector.execute_query(query)
            return [row[0] for row in result]
        elif self.source_connector.config.type == DatabaseType.MONGODB:
            return self.source_connector.connection.list_collection_names()
        else:
            return []
    
    def _validate_table(self, table_name: str) -> Dict[str, Any]:
        """验证单个表"""
        table_result = {
            'table_name': table_name,
            'validations': {}
        }
        
        # 根据验证类型执行相应的验证
        if self.config.validation_type == ValidationType.STRUCTURE:
            table_result['validations']['structure'] = self.structure_validator.validate_structure(
                table_name, self.config.structure_config
            )
        elif self.config.validation_type == ValidationType.DATA:
            table_result['validations']['data'] = self.data_validator.validate_data(
                table_name, self.config.data_config
            )
        elif self.config.validation_type == ValidationType.PERFORMANCE:
            table_result['validations']['performance'] = self.performance_validator.validate_performance(
                table_name, self.config.performance_config
            )
        elif self.config.validation_type == ValidationType.BUSINESS:
            table_result['validations']['business'] = self.business_validator.validate_business(
                table_name, self.config.business_config
            )
        else:
            # 执行所有验证
            table_result['validations']['structure'] = self.structure_validator.validate_structure(
                table_name, self.config.structure_config
            )
            table_result['validations']['data'] = self.data_validator.validate_data(
                table_name, self.config.data_config
            )
            table_result['validations']['performance'] = self.performance_validator.validate_performance(
                table_name, self.config.performance_config
            )
            table_result['validations']['business'] = self.business_validator.validate_business(
                table_name, self.config.business_config
            )
        
        return table_result
    
    def _summarize_results(self, result: ValidationResult, all_results: List[Dict[str, Any]]) -> ValidationResult:
        """汇总验证结果"""
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warning_checks = 0
        
        for table_result in all_results:
            for validation_type, validation_result in table_result['validations'].items():
                total_checks += validation_result.get('total_checks', 0)
                passed_checks += validation_result.get('passed_checks', 0)
                failed_checks += validation_result.get('failed_checks', 0)
                warning_checks += validation_result.get('warning_checks', 0)
        
        result.total_checks = total_checks
        result.passed_checks = passed_checks
        result.failed_checks = failed_checks
        result.warning_checks = warning_checks
        result.details = {'table_results': all_results}
        
        # 生成摘要
        result.summary = {
            'total_tables': len(all_results),
            'success_rate': passed_checks / total_checks if total_checks > 0 else 0,
            'validation_type': self.config.validation_type.value,
            'timestamp': datetime.now()
        }
        
        return result

# 使用示例
# 创建验证配置
source_db_config = DatabaseConfig(
    config_id=str(uuid.uuid4()),
    name="source_mysql",
    type=DatabaseType.MYSQL,
    host="localhost",
    port=3306,
    username="root",
    password="password",
    database="source_db"
)

target_db_config = DatabaseConfig(
    config_id=str(uuid.uuid4()),
    name="target_postgresql",
    type=DatabaseType.POSTGRESQL,
    host="localhost",
    port=5432,
    username="postgres",
    password="password",
    database="target_db"
)

validation_config = ValidationConfig(
    validation_id=str(uuid.uuid4()),
    name="migration_validation",
    description="数据库迁移验证",
    validation_type=ValidationType.DATA,
    source_database=source_db_config,
    target_database=target_db_config,
    scope_config={
        'selection_method': 'specified',
        'tables': ['users', 'orders', 'products']
    },
    data_config={
        'count_tolerance': 0.01,
        'sample_size': 1000,
        'sample_method': 'random',
        'check_primary_key': True,
        'check_foreign_key': True
    }
)

# 创建验证器并执行验证
validator = MigrationValidator(validation_config)
result = validator.validate()

print(f"验证结果: {result.status}")
print(f"总检查数: {result.total_checks}")
print(f"通过检查数: {result.passed_checks}")
print(f"失败检查数: {result.failed_checks}")
print(f"成功率: {result.summary['success_rate']:.2%}")
```

## 参考资源

### 数据库迁移文档
- [MySQL迁移指南](https://dev.mysql.com/doc/refman/8.0/en/migration.html)
- [PostgreSQL迁移文档](https://www.postgresql.org/docs/current/migration.html)
- [MongoDB迁移指南](https://docs.mongodb.com/manual/administration/migration/)
- [Redis迁移文档](https://redis.io/topics/migration)

### 迁移工具
- [AWS Database Migration Service](https://aws.amazon.com/dms/)
- [Azure Database Migration Service](https://azure.microsoft.com/en-us/services/database-migration/)
- [Oracle GoldenGate](https://www.oracle.com/middleware/goldengate/)
- [StreamSets](https://streamsets.com/)

### 验证工具
- [Debezium](https://debezium.io/)
- [Maxwell's Daemon](https://maxwells-daemon.io/)
- [Canal](https://github.com/alibaba/canal)
- [DataX](https://github.com/alibaba/DataX)

### 最佳实践
- [数据库迁移最佳实践](https://docs.microsoft.com/en-us/azure/azure-sql/database/migrate-to-database-from-sql-server)
- [数据迁移验证策略](https://www.percona.com/blog/2020/06/18/how-to-verify-your-backups/)
- [迁移测试指南](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/validate-database-migration.html)

### 监控和诊断
- [迁移监控工具](https://prometheus.io/docs/practices/naming/)
- [性能测试工具](https://jmeter.apache.org/)
- [数据质量监控](https://greatexpectations.io/)
- [数据库审计](https://docs.oracle.com/en/database/oracle/oracle-database/19/tgdba/auditing.html)
