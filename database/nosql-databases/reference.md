# NoSQL数据库参考文档

## NoSQL数据库概述

### 什么是NoSQL数据库
NoSQL数据库（Not Only SQL）是一类非关系型数据库，旨在提供高可扩展性、高性能和灵活的数据模型。与传统的关系型数据库不同，NoSQL数据库不使用固定的表结构，而是采用更灵活的数据模型，如文档、键值、列族和图模型。NoSQL数据库特别适用于大数据应用、实时Web应用、内容管理系统、社交网络等需要处理大量非结构化数据的场景。

### 主要特点
- **灵活的数据模型**: 支持文档、键值、列族、图等多种数据模型
- **水平扩展**: 支持分布式架构，可以轻松扩展到多个节点
- **高性能**: 优化的读写性能，特别适合大数据量和高并发场景
- **高可用性**: 内置复制、故障转移和自动恢复机制
- **最终一致性**: 采用最终一致性模型，保证数据的可用性
- **无模式**: 不需要预定义严格的表结构

## NoSQL数据库核心

### MongoDB文档数据库
```python
# mongodb_manager.py
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
from typing import Dict, List, Any, Optional, Union, Callable, Type, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import math
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, DuplicateKeyError
from bson import ObjectId, json_util
from bson.binary import Binary
from bson.code import Code
from bson.dbref import DBRef
from bson.int64 import Int64
from bson.max_key import MaxKey
from bson.min_key import MinKey
from bson.objectid import ObjectId
from bson.regex import Regex
from bson.timestamp import Timestamp
from contextlib import contextmanager
import gridfs
import pymongo
from pymongo import ReadPreference, WriteConcern
from pymongo.read_concern import ReadConcern

class DatabaseType(Enum):
    """数据库类型枚举"""
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    COUCHBASE = "couchbase"
    NEO4J = "neo4j"

class DocumentModel(Enum):
    """文档模型枚举"""
    DOCUMENT = "document"
    KEY_VALUE = "key_value"
    COLUMN_FAMILY = "column_family"
    GRAPH = "graph"

class IndexType(Enum):
    """索引类型枚举"""
    SINGLE = "single"
    COMPOUND = "compound"
    TEXT = "text"
    GEOSPATIAL = "geospatial"
    HASH = "hash"

@dataclass
class MongoDBConfig:
    """MongoDB配置"""
    config_id: str
    name: str
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    replica_set: Optional[str] = None
    auth_source: str = "admin"
    ssl_enabled: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    ssl_ca_file: Optional[str] = None
    connection_timeout: int = 30
    socket_timeout: int = 30
    max_pool_size: int = 100
    min_pool_size: int = 0
    max_idle_time: int = 300

@dataclass
class CollectionConfig:
    """集合配置"""
    collection_name: str
    database_name: str
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    index_config: List[Dict[str, Any]] = field(default_factory=list)
    shard_key: Optional[str] = None
    capped: bool = False
    max_size: Optional[int] = None
    max_documents: Optional[int] = None

@dataclass
class DocumentSchema:
    """文档模式"""
    field_name: str
    field_type: str
    required: bool = False
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    index_config: Optional[Dict[str, Any]] = None

class MongoDBManager:
    """MongoDB管理器"""
    
    def __init__(self, config: MongoDBConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.database = None
        self.collections = {}
        
    def connect(self):
        """连接MongoDB"""
        try:
            # 构建连接字符串
            if self.config.username and self.config.password:
                auth_string = f"{self.config.username}:{self.config.password}@"
            else:
                auth_string = ""
            
            connection_string = f"mongodb://{auth_string}{self.config.host}:{self.config.port}/{self.config.database}"
            
            # 连接选项
            client_options = {
                'connectTimeoutMS': self.config.connection_timeout * 1000,
                'socketTimeoutMS': self.config.socket_timeout * 1000,
                'maxPoolSize': self.config.max_pool_size,
                'minPoolSize': self.config.min_pool_size,
                'maxIdleTimeMS': self.config.max_idle_time * 1000,
            }
            
            # SSL配置
            if self.config.ssl_enabled:
                client_options['ssl'] = True
                if self.config.ssl_cert_file:
                    client_options['ssl_certfile'] = self.config.ssl_cert_file
                if self.config.ssl_key_file:
                    client_options['ssl_keyfile'] = self.config.ssl_key_file
                if self.config.ssl_ca_file:
                    client_options['ssl_ca_file'] = self.config.ssl_ca_file
            
            # 副本集配置
            if self.config.replica_set:
                client_options['replicaSet'] = self.config.replica_set
            
            # 创建客户端连接
            self.client = MongoClient(connection_string, **client_options)
            self.database = self.client[self.config.database]
            
            # 测试连接
            self.database.command('ping')
            
            self.logger.info(f"MongoDB连接成功: {self.config.name}")
        
        except ConnectionFailure as e:
            self.logger.error(f"MongoDB连接失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"MongoDB连接异常: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.collections.clear()
    
    def create_collection(self, config: CollectionConfig):
        """创建集合"""
        try:
            collection_options = {}
            
            # 启用验证规则
            if config.validation_rules:
                collection_options['validator'] = {
                    '$jsonSchema': config.validation_rules
                }
            
            # 封顶集合配置
            if config.capped:
                collection_options['capped'] = True
                if config.max_size:
                    collection_options['size'] = config.max_size
                if config.max_documents:
                    collection_options['max'] = config.max_documents
            
            # 创建集合
            collection = self.database.create_collection(
                config.collection_name,
                **collection_options
            )
            
            # 创建索引
            for index_config in config.index_config:
                self._create_index(collection, index_config)
            
            # 设置分片键
            if config.shard_key:
                self._enable_sharding(config.database_name, config.collection_name, config.shard_key)
            
            self.collections[config.collection_name] = collection
            
            self.logger.info(f"集合创建成功: {config.collection_name}")
            
            return collection
        
        except OperationFailure as e:
            self.logger.error(f"集合创建失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"集合创建异常: {e}")
            raise
    
    def _create_index(self, collection, index_config: Dict[str, Any]):
        """创建索引"""
        try:
            index_keys = index_config['keys']
            index_options = index_config.get('options', {})
            
            collection.create_index(index_keys, **index_options)
            
            self.logger.info(f"索引创建成功: {index_keys}")
        
        except OperationFailure as e:
            self.logger.error(f"索引创建失败: {e}")
            raise
    
    def _enable_sharding(self, database_name: str, collection_name: str, shard_key: str):
        """启用分片"""
        try:
            # 启用数据库分片
            admin_db = self.client.admin
            admin_db.command('enableSharding', database_name)
            
            # 设置集合分片键
            shard_key_dict = {shard_key: 'hashed'}
            admin_db.command('shardCollection', f"{database_name}.{collection_name}", key=shard_key_dict)
            
            self.logger.info(f"分片启用成功: {collection_name} on {shard_key}")
        
        except OperationFailure as e:
            self.logger.error(f"分片启用失败: {e}")
            raise
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """插入文档"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 添加时间戳
            document['created_at'] = datetime.utcnow()
            document['updated_at'] = datetime.utcnow()
            
            # 插入文档
            result = collection.insert_one(document)
            
            self.logger.info(f"文档插入成功: {result.inserted_id}")
            
            return str(result.inserted_id)
        
        except DuplicateKeyError as e:
            self.logger.error(f"文档插入失败(重复键): {e}")
            raise
        except OperationFailure as e:
            self.logger.error(f"文档插入失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"文档插入异常: {e}")
            raise
    
    def find_documents(self, collection_name: str, query: Dict[str, Any] = None, 
                      projection: Dict[str, Any] = None, sort: List[Tuple] = None,
                      limit: int = None, skip: int = None) -> List[Dict[str, Any]]:
        """查找文档"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 构建查询参数
            find_params = {}
            if projection:
                find_params['projection'] = projection
            if sort:
                find_params['sort'] = sort
            if limit:
                find_params['limit'] = limit
            if skip:
                find_params['skip'] = skip
            
            # 执行查询
            cursor = collection.find(query or {}, **find_params)
            documents = list(cursor)
            
            # 转换ObjectId为字符串
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            self.logger.info(f"文档查询成功: {len(documents)} 条记录")
            
            return documents
        
        except OperationFailure as e:
            self.logger.error(f"文档查询失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"文档查询异常: {e}")
            raise
    
    def update_document(self, collection_name: str, query: Dict[str, Any], 
                       update: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
        """更新文档"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 添加更新时间
            update['$set']['updated_at'] = datetime.utcnow()
            
            # 执行更新
            result = collection.update_one(query, update, upsert=upsert)
            
            self.logger.info(f"文档更新成功: {result.modified_count} 条记录")
            
            return {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None
            }
        
        except OperationFailure as e:
            self.logger.error(f"文档更新失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"文档更新异常: {e}")
            raise
    
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> int:
        """删除文档"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 执行删除
            result = collection.delete_one(query)
            
            self.logger.info(f"文档删除成功: {result.deleted_count} 条记录")
            
            return result.deleted_count
        
        except OperationFailure as e:
            self.logger.error(f"文档删除失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"文档删除异常: {e}")
            raise
    
    def aggregate_documents(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """聚合文档"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 执行聚合
            cursor = collection.aggregate(pipeline)
            results = list(cursor)
            
            # 转换ObjectId为字符串
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            self.logger.info(f"聚合查询成功: {len(results)} 条记录")
            
            return results
        
        except OperationFailure as e:
            self.logger.error(f"聚合查询失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"聚合查询异常: {e}")
            raise
    
    def create_text_index(self, collection_name: str, fields: List[str], weights: Dict[str, int] = None):
        """创建文本索引"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 构建文本索引
            index_spec = {}
            for field in fields:
                index_spec[field] = 'text'
            
            # 设置权重
            index_options = {}
            if weights:
                index_options['weights'] = weights
            
            collection.create_index(index_spec, **index_options)
            
            self.logger.info(f"文本索引创建成功: {fields}")
        
        except OperationFailure as e:
            self.logger.error(f"文本索引创建失败: {e}")
            raise
    
    def create_geospatial_index(self, collection_name: str, field: str, index_type: str = '2dsphere'):
        """创建地理空间索引"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 创建地理空间索引
            collection.create_index([(field, index_type)])
            
            self.logger.info(f"地理空间索引创建成功: {field}")
        
        except OperationFailure as e:
            self.logger.error(f"地理空间索引创建失败: {e}")
            raise
    
    def full_text_search(self, collection_name: str, search_text: str, 
                        fields: List[str] = None, limit: int = None) -> List[Dict[str, Any]]:
        """全文搜索"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 构建搜索查询
            search_query = {
                '$text': {
                    '$search': search_text
                }
            }
            
            # 添加评分
            search_query['score'] = {'$meta': 'textScore'}
            
            # 执行搜索
            cursor = collection.find(search_query, {'score': {'$meta': 'textScore'}})
            cursor = cursor.sort([('score', {'$meta': 'textScore'})])
            
            if limit:
                cursor = cursor.limit(limit)
            
            results = list(cursor)
            
            # 转换ObjectId为字符串
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            self.logger.info(f"全文搜索成功: {len(results)} 条记录")
            
            return results
        
        except OperationFailure as e:
            self.logger.error(f"全文搜索失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"全文搜索异常: {e}")
            raise
    
    def geospatial_query(self, collection_name: str, field: str, 
                        geometry: Dict[str, Any], max_distance: float = None) -> List[Dict[str, Any]]:
        """地理空间查询"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            # 构建地理空间查询
            query = {
                field: {
                    '$near': {
                        '$geometry': geometry,
                        '$maxDistance': max_distance
                    }
                }
            } if max_distance else {
                field: {
                    '$near': {
                        '$geometry': geometry
                    }
                }
            }
            
            # 执行查询
            cursor = collection.find(query)
            results = list(cursor)
            
            # 转换ObjectId为字符串
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            self.logger.info(f"地理空间查询成功: {len(results)} 条记录")
            
            return results
        
        except OperationFailure as e:
            self.logger.error(f"地理空间查询失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"地理空间查询异常: {e}")
            raise
    
    def gridfs_upload(self, collection_name: str, file_data: bytes, filename: str, 
                     metadata: Dict[str, Any] = None) -> str:
        """GridFS上传文件"""
        try:
            fs = gridfs.GridFS(self.database, collection_name)
            
            # 上传文件
            file_id = fs.put(file_data, filename=filename, metadata=metadata or {})
            
            self.logger.info(f"文件上传成功: {filename} -> {file_id}")
            
            return str(file_id)
        
        except Exception as e:
            self.logger.error(f"文件上传失败: {e}")
            raise
    
    def gridfs_download(self, collection_name: str, file_id: str) -> bytes:
        """GridFS下载文件"""
        try:
            fs = gridfs.GridFS(self.database, collection_name)
            
            # 下载文件
            file_data = fs.get(ObjectId(file_id)).read()
            
            self.logger.info(f"文件下载成功: {file_id}")
            
            return file_data
        
        except Exception as e:
            self.logger.error(f"文件下载失败: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            stats = self.database.command('dbStats')
            
            return {
                'database': self.config.database,
                'collections': stats['collections'],
                'data_size': stats['dataSize'],
                'storage_size': stats['storageSize'],
                'indexes': stats['indexes'],
                'index_size': stats['indexSize'],
                'objects': stats['objects'],
                'avg_obj_size': stats['avgObjSize']
            }
        
        except OperationFailure as e:
            self.logger.error(f"获取数据库统计失败: {e}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            stats = collection.command('collStats', collection_name)
            
            return {
                'collection': collection_name,
                'count': stats['count'],
                'size': stats['size'],
                'avg_obj_size': stats['avgObjSize'],
                'storage_size': stats['storageSize'],
                'total_index_size': stats['totalIndexSize'],
                'index_sizes': stats.get('indexSizes', {}),
                'capped': stats.get('capped', False),
                'max_size': stats.get('maxSize', 0),
                'max_documents': stats.get('maxDocs', 0)
            }
        
        except OperationFailure as e:
            self.logger.error(f"获取集合统计失败: {e}")
            raise
    
    def explain_query(self, collection_name: str, query: Dict[str, Any], 
                     aggregation: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """查询执行计划"""
        try:
            collection = self.collections.get(collection_name) or self.database[collection_name]
            
            if aggregation:
                # 聚合查询执行计划
                explain_result = collection.aggregate(aggregation).explain()
            else:
                # 查找查询执行计划
                explain_result = collection.find(query).explain()
            
            return explain_result
        
        except OperationFailure as e:
            self.logger.error(f"查询执行计划失败: {e}")
            raise

class RedisManager:
    """Redis管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
    
    def connect(self):
        """连接Redis"""
        try:
            import redis
            
            self.client = redis.Redis(
                host=self.config['host'],
                port=self.config['port'],
                password=self.config.get('password'),
                db=self.config.get('db', 0),
                decode_responses=True,
                socket_timeout=self.config.get('timeout', 30),
                socket_connect_timeout=self.config.get('connect_timeout', 30),
                max_connections=self.config.get('max_connections', 100)
            )
            
            # 测试连接
            self.client.ping()
            
            self.logger.info(f"Redis连接成功: {self.config['host']}:{self.config['port']}")
        
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            self.client = None
    
    def set_string(self, key: str, value: str, ex: int = None, px: int = None) -> bool:
        """设置字符串值"""
        try:
            result = self.client.set(key, value, ex=ex, px=px)
            return result
        except Exception as e:
            self.logger.error(f"设置字符串值失败: {e}")
            raise
    
    def get_string(self, key: str) -> Optional[str]:
        """获取字符串值"""
        try:
            return self.client.get(key)
        except Exception as e:
            self.logger.error(f"获取字符串值失败: {e}")
            raise
    
    def set_hash(self, key: str, mapping: Dict[str, Any]) -> bool:
        """设置哈希值"""
        try:
            result = self.client.hset(key, mapping=mapping)
            return result > 0
        except Exception as e:
            self.logger.error(f"设置哈希值失败: {e}")
            raise
    
    def get_hash(self, key: str) -> Dict[str, str]:
        """获取哈希值"""
        try:
            return self.client.hgetall(key)
        except Exception as e:
            self.logger.error(f"获取哈希值失败: {e}")
            raise
    
    def set_list(self, key: str, values: List[str]) -> int:
        """设置列表值"""
        try:
            # 先删除现有列表
            self.client.delete(key)
            # 添加新值
            result = self.client.lpush(key, *values)
            return result
        except Exception as e:
            self.logger.error(f"设置列表值失败: {e}")
            raise
    
    def get_list(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """获取列表值"""
        try:
            return self.client.lrange(key, start, end)
        except Exception as e:
            self.logger.error(f"获取列表值失败: {e}")
            raise
    
    def set_set(self, key: str, values: Set[str]) -> int:
        """设置集合值"""
        try:
            # 先删除现有集合
            self.client.delete(key)
            # 添加新值
            result = self.client.sadd(key, *values)
            return result
        except Exception as e:
            self.logger.error(f"设置集合值失败: {e}")
            raise
    
    def get_set(self, key: str) -> Set[str]:
        """获取集合值"""
        try:
            return self.client.smembers(key)
        except Exception as e:
            self.logger.error(f"获取集合值失败: {e}")
            raise
    
    def set_sorted_set(self, key: str, mapping: Dict[str, float]) -> int:
        """设置有序集合值"""
        try:
            # 先删除现有有序集合
            self.client.delete(key)
            # 添加新值
            result = self.client.zadd(key, mapping)
            return result
        except Exception as e:
            self.logger.error(f"设置有序集合值失败: {e}")
            raise
    
    def get_sorted_set(self, key: str, start: int = 0, end: int = -1, withscores: bool = False) -> List[Union[str, Tuple[str, float]]]:
        """获取有序集合值"""
        try:
            return self.client.zrange(key, start, end, withscores=withscores)
        except Exception as e:
            self.logger.error(f"获取有序集合值失败: {e}")
            raise
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        try:
            return self.client.expire(key, seconds)
        except Exception as e:
            self.logger.error(f"设置键过期时间失败: {e}")
            raise
    
    def ttl(self, key: str) -> int:
        """获取键剩余生存时间"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            self.logger.error(f"获取键剩余生存时间失败: {e}")
            raise
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            self.logger.error(f"检查键存在失败: {e}")
            raise
    
    def delete(self, key: str) -> int:
        """删除键"""
        try:
            return self.client.delete(key)
        except Exception as e:
            self.logger.error(f"删除键失败: {e}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """获取Redis信息"""
        try:
            info = self.client.info()
            return info
        except Exception as e:
            self.logger.error(f"获取Redis信息失败: {e}")
            raise

class NoSQLDatabaseFactory:
    """NoSQL数据库工厂"""
    
    @staticmethod
    def create_manager(database_type: DatabaseType, config: Dict[str, Any]):
        """创建数据库管理器"""
        if database_type == DatabaseType.MONGODB:
            return MongoDBManager(config)
        elif database_type == DatabaseType.REDIS:
            return RedisManager(config)
        else:
            raise ValueError(f"不支持的数据库类型: {database_type}")

# 使用示例
# MongoDB配置
mongodb_config = MongoDBConfig(
    config_id=str(uuid.uuid4()),
    name="mongodb_main",
    host="localhost",
    port=27017,
    database="test_db",
    username="admin",
    password="password",
    replica_set="rs0"
)

# 创建MongoDB管理器
mongodb_manager = MongoDBManager(mongodb_config)
mongodb_manager.connect()

# 创建集合配置
collection_config = CollectionConfig(
    collection_name="users",
    database_name="test_db",
    validation_rules={
        "bsonType": "object",
        "required": ["name", "email"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "用户姓名"
            },
            "email": {
                "bsonType": "string",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "description": "邮箱地址"
            },
            "age": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 150,
                "description": "年龄"
            }
        }
    },
    index_config=[
        {
            "keys": [("email", 1)],
            "options": {"unique": True}
        },
        {
            "keys": [("name", 1), ("age", -1)],
            "options": {}
        }
    ]
)

# 创建集合
collection = mongodb_manager.create_collection(collection_config)

# 插入文档
document = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25,
    "address": {
        "city": "北京",
        "district": "朝阳区"
    },
    "hobbies": ["读书", "游泳", "编程"]
}
document_id = mongodb_manager.insert_document("users", document)

# 查询文档
query = {"age": {"$gte": 18}}
documents = mongodb_manager.find_documents("users", query, projection={"name": 1, "age": 1})

# 更新文档
update = {
    "$set": {"age": 26},
    "$push": {"hobbies": "旅游"}
}
result = mongodb_manager.update_document("users", {"_id": ObjectId(document_id)}, update)

# 聚合查询
pipeline = [
    {"$match": {"age": {"$gte": 18}}},
    {"$group": {"_id": "$address.city", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
aggregation_results = mongodb_manager.aggregate_documents("users", pipeline)

# Redis配置
redis_config = {
    "host": "localhost",
    "port": 6379,
    "password": "password",
    "db": 0,
    "timeout": 30,
    "connect_timeout": 30,
    "max_connections": 100
}

# 创建Redis管理器
redis_manager = RedisManager(redis_config)
redis_manager.connect()

# 字符串操作
redis_manager.set_string("user:1001", json.dumps(document), ex=3600)
user_data = redis_manager.get_string("user:1001")

# 哈希操作
user_hash = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": "25"
}
redis_manager.set_hash("user:1001:profile", user_hash)
profile = redis_manager.get_hash("user:1001:profile")

# 列表操作
user_activities = ["登录", "浏览商品", "下单", "支付"]
redis_manager.set_list("user:1001:activities", user_activities)
activities = redis_manager.get_list("user:1001:activities")

# 集合操作
user_tags = {"程序员", "北京", "技术爱好者"}
redis_manager.set_set("user:1001:tags", user_tags)
tags = redis_manager.get_set("user:1001:tags")

# 有序集合操作
user_scores = {"编程": 95, "设计": 80, "管理": 70}
redis_manager.set_sorted_set("user:1001:scores", user_scores)
scores = redis_manager.get_sorted_set("user:1001:scores", withscores=True)

print(f"MongoDB文档ID: {document_id}")
print(f"Redis用户数据: {user_data}")
print(f"Redis用户档案: {profile}")
print(f"Redis用户活动: {activities}")
print(f"Redis用户标签: {tags}")
print(f"Redis用户分数: {scores}")
```

## 参考资源

### NoSQL数据库文档
- [MongoDB官方文档](https://docs.mongodb.com/)
- [Redis官方文档](https://redis.io/documentation)
- [Cassandra官方文档](https://cassandra.apache.org/doc/latest/)
- [Couchbase官方文档](https://docs.couchbase.com/)
- [Neo4j官方文档](https://neo4j.com/docs/)

### 数据模型设计
- [MongoDB数据建模指南](https://www.mongodb.com/docs/manual/core/data-modeling/)
- [Redis数据结构教程](https://redis.io/docs/data-types/)
- [Cassandra数据建模](https://cassandra.apache.org/doc/latest/data_modeling/)
- [图数据库建模](https://neo4j.com/docs/cypher-manual/current/introduction/)

### 性能优化
- [MongoDB性能优化](https://www.mongodb.com/docs/manual/administration/performance-indexing/)
- [Redis性能优化](https://redis.io/docs/operate/oss_and_stack/management/optimization/)
- [NoSQL数据库性能比较](https://db-engines.com/en/ranking)

### 最佳实践
- [NoSQL数据库选择指南](https://www.mongodb.com/nosql-explained)
- [MongoDB最佳实践](https://www.mongodb.com/docs/manual/administration/)
- [Redis最佳实践](https://redis.io/docs/operate/oss_and_stack/management/)
- [分布式数据库设计模式](https://www.datastax.com/blog/distributed-database-design-patterns)

### 监控和运维
- [MongoDB监控工具](https://www.mongodb.com/docs/manual/monitoring/)
- [Redis监控和诊断](https://redis.io/docs/operate/oss_and_stack/management/monitoring/)
- [NoSQL数据库运维指南](https://www.mongodb.com/docs/manual/administration/)
