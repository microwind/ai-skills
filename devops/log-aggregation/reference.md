# 日志聚合参考文档

## 日志聚合概述

### 什么是日志聚合
日志聚合是一个集中化收集、处理、存储和分析分布式系统日志数据的解决方案。该工具支持多种日志源、实时处理、智能分析、可视化展示和告警通知，帮助运维团队快速定位问题、监控系统状态、优化性能和保障安全。

### 主要功能
- **多源日志收集**: 支持文件、API、消息队列、Syslog等多种日志源
- **实时日志处理**: 实时解析、过滤、丰富和转换日志数据
- **灵活存储策略**: 支持Elasticsearch、MongoDB等多种存储引擎
- **智能查询分析**: 提供强大的查询语言和可视化分析能力
- **自动告警通知**: 基于阈值、趋势和关键词的智能告警
- **性能优化**: 高并发处理、内存管理和存储优化
- **安全保障**: 访问控制、数据加密和权限管理
- **集成扩展**: 与监控工具、消息队列和云服务集成

## 核心组件架构

### 日志收集器
```python
# log_collector.py
import os
import time
import json
import re
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import threading
import queue
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CollectionType(Enum):
    FILE_MONITOR = "file_monitor"
    API_ENDPOINT = "api_endpoint"
    MESSAGE_QUEUE = "message_queue"
    SYSLOG = "syslog"
    CONTAINER_LOG = "container_log"

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    metadata: Dict[str, Any]
    raw_data: str

@dataclass
class CollectionConfig:
    collection_type: CollectionType
    source_path: str
    file_pattern: str
    encoding: str = "utf-8"
    multiline_pattern: Optional[str] = None
    exclude_patterns: List[str] = None

class FileLogHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None], file_pattern: str):
        self.callback = callback
        self.file_pattern = re.compile(file_pattern)
        self.file_positions = {}
        super().__init__()
    
    def on_modified(self, event):
        if not event.is_directory and self.file_pattern.match(event.src_path):
            self._read_new_lines(event.src_path)
    
    def _read_new_lines(self, file_path: str):
        try:
            current_pos = self.file_positions.get(file_path, 0)
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(current_pos)
                new_lines = f.readlines()
                self.file_positions[file_path] = f.tell()
                
                for line in new_lines:
                    if line.strip():
                        self.callback(line.strip())
        except Exception as e:
            logging.error(f"读取文件 {file_path} 失败: {e}")

class LogCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.observers = []
        self.processors = []
        self.output_queue = queue.Queue()
        self.is_running = False
        self.collection_threads = []
    
    def add_file_source(self, config: CollectionConfig):
        """添加文件日志源"""
        if config.collection_type != CollectionType.FILE_MONITOR:
            raise ValueError("配置类型必须为FILE_MONITOR")
        
        event_handler = FileLogHandler(self._process_log_line, config.file_pattern)
        observer = Observer()
        observer.schedule(event_handler, config.source_path, recursive=True)
        self.observers.append(observer)
    
    def add_api_source(self, config: CollectionConfig):
        """添加API日志源"""
        if config.collection_type != CollectionType.API_ENDPOINT:
            raise ValueError("配置类型必须为API_ENDPOINT")
        
        # 启动API服务器接收日志
        thread = threading.Thread(target=self._start_api_server, args=(config,))
        thread.daemon = True
        self.collection_threads.append(thread)
    
    def add_syslog_source(self, config: CollectionConfig):
        """添加Syslog日志源"""
        if config.collection_type != CollectionType.SYSLOG:
            raise ValueError("配置类型必须为SYSLOG")
        
        thread = threading.Thread(target=self._start_syslog_server, args=(config,))
        thread.daemon = True
        self.collection_threads.append(thread)
    
    def _process_log_line(self, line: str):
        """处理日志行"""
        try:
            # 基本解析
            log_entry = self._parse_log_line(line)
            
            # 应用处理器
            for processor in self.processors:
                log_entry = processor.process(log_entry)
            
            # 放入输出队列
            self.output_queue.put(log_entry)
            
        except Exception as e:
            self.logger.error(f"处理日志行失败: {e}")
    
    def _parse_log_line(self, line: str) -> LogEntry:
        """解析日志行"""
        # 尝试JSON解析
        try:
            data = json.loads(line)
            return LogEntry(
                timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                level=LogLevel(data.get('level', 'INFO')),
                message=data.get('message', ''),
                source=data.get('source', 'unknown'),
                metadata=data.get('metadata', {}),
                raw_data=line
            )
        except json.JSONDecodeError:
            # 尝试标准日志格式解析
            return self._parse_standard_log(line)
    
    def _parse_standard_log(self, line: str) -> LogEntry:
        """解析标准日志格式"""
        # 简化的标准日志格式解析
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        level_pattern = r'(DEBUG|INFO|WARNING|ERROR|CRITICAL)'
        
        timestamp_match = re.search(timestamp_pattern, line)
        level_match = re.search(level_pattern, line)
        
        timestamp = datetime.fromisoformat(timestamp_match.group(1)) if timestamp_match else datetime.now()
        level = LogLevel(level_match.group(1)) if level_match else LogLevel.INFO
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=line,
            source='unknown',
            metadata={},
            raw_data=line
        )
    
    def _start_api_server(self, config: CollectionConfig):
        """启动API服务器"""
        from flask import Flask, request
        
        app = Flask(__name__)
        
        @app.route('/logs', methods=['POST'])
        def receive_logs():
            try:
                logs = request.json
                if isinstance(logs, list):
                    for log in logs:
                        self._process_log_line(json.dumps(log))
                else:
                    self._process_log_line(json.dumps(logs))
                return {'status': 'success'}, 200
            except Exception as e:
                self.logger.error(f"API接收日志失败: {e}")
                return {'status': 'error', 'message': str(e)}, 500
        
        app.run(host='0.0.0.0', port=8080)
    
    def _start_syslog_server(self, config: CollectionConfig):
        """启动Syslog服务器"""
        import socketserver
        import struct
        
        class SyslogHandler(socketserver.BaseRequestHandler):
            def handle(self):
                data = self.request[0]
                try:
                    # 简化的syslog解析
                    message = data.decode('utf-8').strip()
                    collector._process_log_line(message)
                except Exception as e:
                    logging.error(f"Syslog处理失败: {e}")
        
        server = socketserver.UDPServer(('0.0.0.0', 514), SyslogHandler)
        server.serve_forever()
    
    def add_processor(self, processor):
        """添加日志处理器"""
        self.processors.append(processor)
    
    def start_collection(self):
        """开始日志收集"""
        self.is_running = True
        
        # 启动文件监控
        for observer in self.observers:
            observer.start()
        
        # 启动其他收集线程
        for thread in self.collection_threads:
            thread.start()
        
        self.logger.info("日志收集已启动")
    
    def stop_collection(self):
        """停止日志收集"""
        self.is_running = False
        
        # 停止文件监控
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.logger.info("日志收集已停止")
    
    def get_logs(self, timeout: float = 1.0) -> List[LogEntry]:
        """获取处理后的日志"""
        logs = []
        try:
            while True:
                log = self.output_queue.get(timeout=timeout)
                logs.append(log)
        except queue.Empty:
            pass
        return logs

# 使用示例
collector = LogCollector()

# 添加文件日志源
file_config = CollectionConfig(
    collection_type=CollectionType.FILE_MONITOR,
    source_path="/var/log",
    file_pattern=r".*\.log$"
)
collector.add_file_source(file_config)

# 启动收集
collector.start_collection()

# 获取日志
while True:
    logs = collector.get_logs()
    for log in logs:
        print(f"{log.timestamp} [{log.level}] {log.message}")
    time.sleep(1)
```

### 日志处理器
```python
# log_processor.py
import re
import json
import geoip2.database
import user_agents
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ProcessingRule:
    name: str
    pattern: str
    action: str
    target_field: str
    value_template: Optional[str] = None

class LogProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = []
        self.field_mappings = {}
        self.filters = []
        self.enrichers = []
        
        # 初始化外部数据源
        self._init_external_sources()
    
    def _init_external_sources(self):
        """初始化外部数据源"""
        try:
            # GeoIP数据库
            self.geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        except:
            self.geoip_reader = None
        
        try:
            # 用户代理解析器
            self.ua_parser = user_agents.UserAgent()
        except:
            self.ua_parser = None
    
    def add_parsing_rule(self, rule: ProcessingRule):
        """添加解析规则"""
        self.rules.append(rule)
    
    def add_field_mapping(self, source_field: str, target_field: str):
        """添加字段映射"""
        self.field_mappings[source_field] = target_field
    
    def add_filter(self, filter_func):
        """添加过滤器"""
        self.filters.append(filter_func)
    
    def add_enricher(self, enricher_func):
        """添加数据丰富器"""
        self.enrichers.append(enricher_func)
    
    def process(self, log_entry: LogEntry) -> LogEntry:
        """处理日志条目"""
        try:
            # 解析原始数据
            parsed_data = self._parse_raw_data(log_entry.raw_data)
            
            # 应用字段映射
            mapped_data = self._apply_field_mappings(parsed_data)
            
            # 应用过滤器
            if not self._apply_filters(mapped_data):
                return None
            
            # 数据丰富
            enriched_data = self._apply_enrichment(mapped_data)
            
            # 更新日志条目
            log_entry.metadata.update(enriched_data)
            
            return log_entry
            
        except Exception as e:
            self.logger.error(f"处理日志失败: {e}")
            return log_entry
    
    def _parse_raw_data(self, raw_data: str) -> Dict[str, Any]:
        """解析原始数据"""
        result = {}
        
        # 尝试JSON解析
        try:
            return json.loads(raw_data)
        except json.JSONDecodeError:
            pass
        
        # 应用解析规则
        for rule in self.rules:
            try:
                match = re.search(rule.pattern, raw_data)
                if match:
                    if rule.action == 'extract':
                        if rule.target_field and match.groups():
                            result[rule.target_field] = match.group(1)
                        elif rule.target_field:
                            result[rule.target_field] = match.group(0)
                    elif rule.action == 'replace' and rule.value_template:
                        result[rule.target_field] = match.expand(rule.value_template)
            except Exception as e:
                self.logger.error(f"应用解析规则失败: {e}")
        
        return result
    
    def _apply_field_mappings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用字段映射"""
        mapped_data = {}
        
        for source_field, target_field in self.field_mappings.items():
            if source_field in data:
                mapped_data[target_field] = data[source_field]
        
        # 保留未映射的字段
        for field, value in data.items():
            if field not in self.field_mappings:
                mapped_data[field] = value
        
        return mapped_data
    
    def _apply_filters(self, data: Dict[str, Any]) -> bool:
        """应用过滤器"""
        for filter_func in self.filters:
            try:
                if not filter_func(data):
                    return False
            except Exception as e:
                self.logger.error(f"应用过滤器失败: {e}")
                return False
        
        return True
    
    def _apply_enrichment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用数据丰富"""
        enriched_data = data.copy()
        
        for enricher_func in self.enrichers:
            try:
                enriched_data = enricher_func(enriched_data)
            except Exception as e:
                self.logger.error(f"应用数据丰富失败: {e}")
        
        return enriched_data
    
    def enrich_geoip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """GeoIP数据丰富"""
        if not self.geoip_reader:
            return data
        
        ip_address = data.get('client_ip') or data.get('remote_addr')
        if ip_address:
            try:
                response = self.geoip_reader.city(ip_address)
                data['geoip'] = {
                    'country': response.country.name,
                    'country_code': response.country.iso_code,
                    'city': response.city.name,
                    'latitude': response.location.latitude,
                    'longitude': response.location.longitude
                }
            except:
                pass
        
        return data
    
    def enrich_user_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """用户代理数据丰富"""
        if not self.ua_parser:
            return data
        
        user_agent = data.get('user_agent') or data.get('User-Agent')
        if user_agent:
            try:
                parsed_ua = self.ua_parser.parse(user_agent)
                data['user_agent_info'] = {
                    'browser': parsed_ua.browser.family,
                    'browser_version': parsed_ua.browser.version_string,
                    'os': parsed_ua.os.family,
                    'os_version': parsed_ua.os.version_string,
                    'device': parsed_ua.device.family
                }
            except:
                pass
        
        return data
    
    def enrich_timestamp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """时间戳数据丰富"""
        timestamp = data.get('timestamp')
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp)
                elif isinstance(timestamp, (int, float)):
                    dt = datetime.fromtimestamp(timestamp)
                else:
                    return data
                
                data['timestamp_enriched'] = {
                    'datetime': dt,
                    'date': dt.date().isoformat(),
                    'time': dt.time().isoformat(),
                    'hour': dt.hour,
                    'day_of_week': dt.weekday(),
                    'day_of_month': dt.day,
                    'month': dt.month,
                    'year': dt.year
                }
            except:
                pass
        
        return data

# 处理器示例
def create_web_log_processor() -> LogProcessor:
    """创建Web日志处理器"""
    processor = LogProcessor()
    
    # 添加解析规则
    processor.add_parsing_rule(ProcessingRule(
        name="apache_combined_log",
        pattern=r'(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+) "([^"]*)" "([^"]*)"',
        action="extract",
        target_field="apache_log"
    ))
    
    # 添加字段映射
    processor.add_field_mapping("client_ip", "ip_address")
    processor.add_field_mapping("timestamp", "log_time")
    processor.add_field_mapping("method", "http_method")
    processor.add_field_mapping("url", "request_url")
    processor.add_field_mapping("status", "http_status")
    processor.add_field_mapping("size", "response_size")
    
    # 添加过滤器
    def filter_health_checks(data):
        """过滤健康检查请求"""
        url = data.get('request_url', '')
        return '/health' not in url and '/ping' not in url
    
    processor.add_filter(filter_health_checks)
    
    # 添加数据丰富器
    processor.add_enricher(processor.enrich_geoip)
    processor.add_enricher(processor.enrich_user_agent)
    processor.add_enricher(processor.enrich_timestamp)
    
    return processor

# 使用示例
processor = create_web_log_processor()
collector.add_processor(processor)
```

### 日志存储管理器
```python
# log_storage.py
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from elasticsearch import Elasticsearch
from pymongo import MongoClient
import redis

class StorageType(Enum):
    ELASTICSEARCH = "elasticsearch"
    MONGODB = "mongodb"
    REDIS = "redis"
    CUSTOM = "custom"

@dataclass
class StorageConfig:
    storage_type: StorageType
    connection_string: str
    index_name: str
    retention_days: int = 30
    shard_count: int = 1
    replica_count: int = 1

class LogStorage:
    def __init__(self, config: StorageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self._init_connection()
    
    def _init_connection(self):
        """初始化存储连接"""
        if self.config.storage_type == StorageType.ELASTICSEARCH:
            self.client = Elasticsearch([self.config.connection_string])
            self._create_elasticsearch_index()
        elif self.config.storage_type == StorageType.MONGODB:
            self.client = MongoClient(self.config.connection_string)
            self._create_mongodb_collection()
        elif self.config.storage_type == StorageType.REDIS:
            self.client = redis.from_url(self.config.connection_string)
    
    def _create_elasticsearch_index(self):
        """创建Elasticsearch索引"""
        if not self.client.indices.exists(index=self.config.index_name):
            index_mapping = {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {"type": "text"},
                        "source": {"type": "keyword"},
                        "metadata": {"type": "object"},
                        "raw_data": {"type": "text"}
                    }
                },
                "settings": {
                    "number_of_shards": self.config.shard_count,
                    "number_of_replicas": self.config.replica_count
                }
            }
            self.client.indices.create(index=self.config.index_name, body=index_mapping)
    
    def _create_mongodb_collection(self):
        """创建MongoDB集合"""
        db_name, collection_name = self.config.index_name.split('.', 1)
        db = self.client[db_name]
        collection = db[collection_name]
        
        # 创建索引
        collection.create_index([("timestamp", -1)])
        collection.create_index([("level", 1)])
        collection.create_index([("source", 1)])
    
    def store_log(self, log_entry: LogEntry):
        """存储日志条目"""
        try:
            doc = {
                "timestamp": log_entry.timestamp.isoformat(),
                "level": log_entry.level.value,
                "message": log_entry.message,
                "source": log_entry.source,
                "metadata": log_entry.metadata,
                "raw_data": log_entry.raw_data
            }
            
            if self.config.storage_type == StorageType.ELASTICSEARCH:
                self.client.index(
                    index=self.config.index_name,
                    body=doc
                )
            elif self.config.storage_type == StorageType.MONGODB:
                db_name, collection_name = self.config.index_name.split('.', 1)
                db = self.client[db_name]
                collection = db[collection_name]
                collection.insert_one(doc)
            elif self.config.storage_type == StorageType.REDIS:
                # Redis存储最近的日志（用于实时查询）
                key = f"{self.config.index_name}:recent"
                self.client.lpush(key, json.dumps(doc))
                self.client.ltrim(key, 0, 9999)  # 保留最近10000条
                
        except Exception as e:
            self.logger.error(f"存储日志失败: {e}")
    
    def query_logs(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """查询日志"""
        try:
            if self.config.storage_type == StorageType.ELASTICSEARCH:
                response = self.client.search(
                    index=self.config.index_name,
                    body=query,
                    size=limit
                )
                return [hit['_source'] for hit in response['hits']['hits']]
            
            elif self.config.storage_type == StorageType.MONGODB:
                db_name, collection_name = self.config.index_name.split('.', 1)
                db = self.client[db_name]
                collection = db[collection_name]
                
                cursor = collection.find(query).sort("timestamp", -1).limit(limit)
                return list(cursor)
            
            elif self.config.storage_type == StorageType.REDIS:
                key = f"{self.config.index_name}:recent"
                logs = self.client.lrange(key, 0, limit - 1)
                return [json.loads(log) for log in logs]
                
        except Exception as e:
            self.logger.error(f"查询日志失败: {e}")
            return []
    
    def cleanup_old_logs(self):
        """清理过期日志"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            
            if self.config.storage_type == StorageType.ELASTICSEARCH:
                delete_query = {
                    "query": {
                        "range": {
                            "timestamp": {
                                "lt": cutoff_date.isoformat()
                            }
                        }
                    }
                }
                self.client.delete_by_query(
                    index=self.config.index_name,
                    body=delete_query
                )
            
            elif self.config.storage_type == StorageType.MONGODB:
                db_name, collection_name = self.config.index_name.split('.', 1)
                db = self.client[db_name]
                collection = db[collection_name]
                
                collection.delete_many({"timestamp": {"$lt": cutoff_date}})
            
            self.logger.info(f"清理了 {cutoff_date} 之前的日志")
            
        except Exception as e:
            self.logger.error(f"清理过期日志失败: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            if self.config.storage_type == StorageType.ELASTICSEARCH:
                stats = self.client.indices.stats(index=self.config.index_name)
                return {
                    "doc_count": stats['indices'][self.config.index_name]['total']['docs']['count'],
                    "store_size": stats['indices'][self.config.index_name]['total']['store']['size_in_bytes']
                }
            
            elif self.config.storage_type == StorageType.MONGODB:
                db_name, collection_name = self.config.index_name.split('.', 1)
                db = self.client[db_name]
                collection = db[collection_name]
                
                stats = db.command("collstats", collection_name)
                return {
                    "doc_count": stats.get('count', 0),
                    "size": stats.get('size', 0)
                }
            
        except Exception as e:
            self.logger.error(f"获取存储统计失败: {e}")
            return {}

# 使用示例
# Elasticsearch配置
es_config = StorageConfig(
    storage_type=StorageType.ELASTICSEARCH,
    connection_string="http://localhost:9200",
    index_name="logs-2023",
    retention_days=90,
    shard_count=3,
    replica_count=1
)

storage = LogStorage(es_config)

# 存储日志
storage.store_log(log_entry)

# 查询日志
query = {
    "query": {
        "bool": {
            "must": [
                {"term": {"level": "ERROR"}},
                {"range": {"timestamp": {"gte": "now-1h"}}}
            ]
        }
    }
}
error_logs = storage.query_logs(query)
```

### 告警管理器
```python
# alert_manager.py
import time
import threading
import smtplib
import requests
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class AlertRule:
    name: str
    condition: str
    threshold: float
    level: AlertLevel
    time_window: int  # 秒
    notification_channels: List[str]
    enabled: bool = True

@dataclass
class Alert:
    id: str
    rule_name: str
    level: AlertLevel
    message: str
    triggered_at: datetime
    status: AlertStatus
    metadata: Dict[str, Any]

class AlertManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = {}
        self.active_alerts = {}
        self.notification_handlers = {}
        self.query_handler = None
        self.is_running = False
        self.evaluation_thread = None
        
        # 初始化通知处理器
        self._init_notification_handlers()
    
    def _init_notification_handlers(self):
        """初始化通知处理器"""
        self.notification_handlers = {
            'email': self._send_email_notification,
            'slack': self._send_slack_notification,
            'webhook': self._send_webhook_notification,
            'sms': self._send_sms_notification
        }
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.name] = rule
        self.logger.info(f"添加告警规则: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"移除告警规则: {rule_name}")
    
    def set_query_handler(self, handler: Callable[[str], Dict[str, Any]]):
        """设置查询处理器"""
        self.query_handler = handler
    
    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        self.is_running = True
        self.evaluation_thread = threading.Thread(
            target=self._evaluation_loop,
            args=(interval,)
        )
        self.evaluation_thread.daemon = True
        self.evaluation_thread.start()
        self.logger.info("告警监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.evaluation_thread:
            self.evaluation_thread.join()
        self.logger.info("告警监控已停止")
    
    def _evaluation_loop(self, interval: int):
        """评估循环"""
        while self.is_running:
            try:
                self._evaluate_rules()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"告警评估失败: {e}")
                time.sleep(interval)
    
    def _evaluate_rules(self):
        """评估所有规则"""
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            try:
                self._evaluate_rule(rule)
            except Exception as e:
                self.logger.error(f"评估规则 {rule_name} 失败: {e}")
    
    def _evaluate_rule(self, rule: AlertRule):
        """评估单个规则"""
        if not self.query_handler:
            return
        
        # 构建查询
        query = self._build_query(rule)
        
        # 执行查询
        result = self.query_handler(query)
        
        # 检查是否触发告警
        should_alert = self._check_condition(result, rule)
        
        alert_id = f"{rule.name}_{int(time.time())}"
        
        if should_alert:
            # 检查是否已有活跃告警
            existing_alert = self._get_active_alert(rule_name)
            if not existing_alert:
                # 创建新告警
                alert = Alert(
                    id=alert_id,
                    rule_name=rule.name,
                    level=rule.level,
                    message=self._generate_alert_message(result, rule),
                    triggered_at=datetime.now(),
                    status=AlertStatus.ACTIVE,
                    metadata={'query_result': result}
                )
                
                self.active_alerts[rule_name] = alert
                self._send_notifications(alert)
                
                self.logger.warning(f"触发告警: {rule.name}")
        else:
            # 检查是否需要解决告警
            existing_alert = self._get_active_alert(rule_name)
            if existing_alert:
                existing_alert.status = AlertStatus.RESOLVED
                self._send_resolution_notification(existing_alert)
                del self.active_alerts[rule_name]
                
                self.logger.info(f"解决告警: {rule_name}")
    
    def _build_query(self, rule: AlertRule) -> str:
        """构建查询"""
        # 根据规则条件构建查询
        time_window = f"now-{rule.time_window}s"
        
        if "error_rate" in rule.condition:
            return f'level:ERROR AND timestamp:[{time_window} TO now]'
        elif "response_time" in rule.condition:
            return f'response_time:>1000 AND timestamp:[{time_window} TO now]'
        elif "disk_usage" in rule.condition:
            return f'metric:disk_usage AND timestamp:[{time_window} TO now]'
        else:
            return f'timestamp:[{time_window} TO now]'
    
    def _check_condition(self, result: Dict[str, Any], rule: AlertRule) -> bool:
        """检查条件"""
        count = result.get('count', 0)
        
        if "error_rate" in rule.condition:
            # 错误率告警
            total_logs = result.get('total', 1)
            error_rate = count / total_logs if total_logs > 0 else 0
            return error_rate > rule.threshold
        
        elif "count" in rule.condition:
            # 计数告警
            return count > rule.threshold
        
        elif "response_time" in rule.condition:
            # 响应时间告警
            avg_response_time = result.get('avg_response_time', 0)
            return avg_response_time > rule.threshold
        
        return False
    
    def _generate_alert_message(self, result: Dict[str, Any], rule: AlertRule) -> str:
        """生成告警消息"""
        count = result.get('count', 0)
        
        if "error_rate" in rule.condition:
            total_logs = result.get('total', 1)
            error_rate = (count / total_logs * 100) if total_logs > 0 else 0
            return f"错误率过高: {error_rate:.2f}% (阈值: {rule.threshold}%)"
        
        elif "count" in rule.condition:
            return f"日志数量异常: {count} (阈值: {rule.threshold})"
        
        elif "response_time" in rule.condition:
            avg_response_time = result.get('avg_response_time', 0)
            return f"响应时间过长: {avg_response_time:.2f}ms (阈值: {rule.threshold}ms)"
        
        return f"告警触发: {rule.name}"
    
    def _get_active_alert(self, rule_name: str) -> Optional[Alert]:
        """获取活跃告警"""
        return self.active_alerts.get(rule_name)
    
    def _send_notifications(self, alert: Alert):
        """发送通知"""
        for channel in alert.rule.notification_channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    handler(alert)
                except Exception as e:
                    self.logger.error(f"发送 {channel} 通知失败: {e}")
    
    def _send_resolution_notification(self, alert: Alert):
        """发送解决通知"""
        # 创建解决消息
        resolution_alert = Alert(
            id=alert.id + "_resolved",
            rule_name=alert.rule_name,
            level=AlertLevel.INFO,
            message=f"告警已解决: {alert.message}",
            triggered_at=datetime.now(),
            status=AlertStatus.RESOLVED,
            metadata={'original_alert': alert.id}
        )
        
        for channel in alert.rule.notification_channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    handler(resolution_alert)
                except Exception as e:
                    self.logger.error(f"发送 {channel} 解决通知失败: {e}")
    
    def _send_email_notification(self, alert: Alert):
        """发送邮件通知"""
        # 邮件配置需要根据实际情况设置
        smtp_server = "smtp.example.com"
        smtp_port = 587
        smtp_user = "alerts@example.com"
        smtp_password = "password"
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = "admin@example.com"
        msg['Subject'] = f"[{alert.level.value.upper()}] {alert.rule_name}"
        
        body = f"""
        告警级别: {alert.level.value}
        告警规则: {alert.rule_name}
        触发时间: {alert.triggered_at}
        告警消息: {alert.message}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
    
    def _send_slack_notification(self, alert: Alert):
        """发送Slack通知"""
        webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        
        payload = {
            "text": f"🚨 *{alert.level.value.upper()} Alert*",
            "attachments": [
                {
                    "color": self._get_color_for_level(alert.level),
                    "fields": [
                        {"title": "Rule", "value": alert.rule_name, "short": True},
                        {"title": "Level", "value": alert.level.value, "short": True},
                        {"title": "Message", "value": alert.message, "short": False},
                        {"title": "Time", "value": alert.triggered_at.isoformat(), "short": True}
                    ]
                }
            ]
        }
        
        requests.post(webhook_url, json=payload)
    
    def _send_webhook_notification(self, alert: Alert):
        """发送Webhook通知"""
        webhook_url = "https://your-webhook-endpoint.com/alerts"
        
        payload = {
            "alert_id": alert.id,
            "rule_name": alert.rule_name,
            "level": alert.level.value,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
            "status": alert.status.value,
            "metadata": alert.metadata
        }
        
        requests.post(webhook_url, json=payload)
    
    def _send_sms_notification(self, alert: Alert):
        """发送短信通知"""
        # 短信服务配置需要根据实际情况设置
        pass
    
    def _get_color_for_level(self, level: AlertLevel) -> str:
        """获取告警级别对应的颜色"""
        color_map = {
            AlertLevel.INFO: "good",
            AlertLevel.WARNING: "warning",
            AlertLevel.ERROR: "danger",
            AlertLevel.CRITICAL: "#ff0000"
        }
        return color_map.get(level, "good")

# 使用示例
alert_manager = AlertManager()

# 添加告警规则
error_rate_rule = AlertRule(
    name="high_error_rate",
    condition="error_rate",
    threshold=5.0,  # 5%
    level=AlertLevel.WARNING,
    time_window=300,  # 5分钟
    notification_channels=["email", "slack"]
)

alert_manager.add_rule(error_rate_rule)

# 设置查询处理器
def query_handler(query: str) -> Dict[str, Any]:
    # 这里应该调用实际的日志查询接口
    return {"count": 10, "total": 100}

alert_manager.set_query_handler(query_handler)

# 启动监控
alert_manager.start_monitoring(interval=60)
```

## 使用示例

### 完整日志聚合系统
```python
# complete_log_aggregation.py
from log_collector import LogCollector, CollectionConfig, CollectionType
from log_processor import LogProcessor, create_web_log_processor
from log_storage import LogStorage, StorageConfig, StorageType
from alert_manager import AlertManager, AlertRule, AlertLevel
import threading
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogAggregationSystem:
    def __init__(self):
        self.collector = LogCollector()
        self.storage = None
        self.alert_manager = AlertManager()
        self.is_running = False
        
    def setup_collection(self):
        """设置日志收集"""
        # 文件日志源
        file_config = CollectionConfig(
            collection_type=CollectionType.FILE_MONITOR,
            source_path="/var/log",
            file_pattern=r".*\.log$"
        )
        self.collector.add_file_source(file_config)
        
        # API日志源
        api_config = CollectionConfig(
            collection_type=CollectionType.API_ENDPOINT,
            source_path="http://0.0.0.0:8080",
            file_pattern=".*"
        )
        self.collector.add_api_source(api_config)
        
        # 添加处理器
        processor = create_web_log_processor()
        self.collector.add_processor(processor)
    
    def setup_storage(self):
        """设置日志存储"""
        storage_config = StorageConfig(
            storage_type=StorageType.ELASTICSEARCH,
            connection_string="http://localhost:9200",
            index_name="logs-2023",
            retention_days=90
        )
        self.storage = LogStorage(storage_config)
    
    def setup_alerts(self):
        """设置告警"""
        # 错误率告警
        error_rate_rule = AlertRule(
            name="high_error_rate",
            condition="error_rate",
            threshold=5.0,
            level=AlertLevel.WARNING,
            time_window=300,
            notification_channels=["email"]
        )
        self.alert_manager.add_rule(error_rate_rule)
        
        # 设置查询处理器
        self.alert_manager.set_query_handler(self.query_logs_for_alerts)
    
    def query_logs_for_alerts(self, query: str) -> Dict[str, Any]:
        """为告警查询日志"""
        if not self.storage:
            return {"count": 0, "total": 0}
        
        # 构建Elasticsearch查询
        es_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-5m"}}}
                    ]
                }
            }
        }
        
        if "ERROR" in query:
            es_query["query"]["bool"]["must"].append({"term": {"level": "ERROR"}})
        
        try:
            results = self.storage.query_logs(es_query, limit=1000)
            count = len(results)
            
            # 获取总日志数
            total_query = {
                "query": {
                    "range": {"timestamp": {"gte": "now-5m"}}
                }
            }
            total_results = self.storage.query_logs(total_query, limit=10000)
            total = len(total_results)
            
            return {"count": count, "total": total}
            
        except Exception as e:
            logger.error(f"告警查询失败: {e}")
            return {"count": 0, "total": 0}
    
    def start(self):
        """启动系统"""
        self.is_running = True
        
        # 启动日志收集
        self.collector.start_collection()
        
        # 启动告警监控
        self.alert_manager.start_monitoring(interval=60)
        
        # 启动日志处理和存储线程
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        logger.info("日志聚合系统已启动")
    
    def stop(self):
        """停止系统"""
        self.is_running = False
        
        self.collector.stop_collection()
        self.alert_manager.stop_monitoring()
        
        logger.info("日志聚合系统已停止")
    
    def _processing_loop(self):
        """处理循环"""
        while self.is_running:
            try:
                # 获取处理后的日志
                logs = self.collector.get_logs(timeout=1.0)
                
                # 存储日志
                for log in logs:
                    if self.storage:
                        self.storage.store_log(log)
                
                # 定期清理过期日志
                if int(time.time()) % 3600 == 0:  # 每小时清理一次
                    if self.storage:
                        self.storage.cleanup_old_logs()
                
            except Exception as e:
                logger.error(f"处理日志失败: {e}")
                time.sleep(1)

# 使用示例
if __name__ == "__main__":
    system = LogAggregationSystem()
    
    # 设置各个组件
    system.setup_collection()
    system.setup_storage()
    system.setup_alerts()
    
    # 启动系统
    system.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        system.stop()
```

这个日志聚合系统提供了完整的日志收集、处理、存储、查询和告警功能，支持多种数据源、存储引擎和通知方式，可以满足不同规模和需求的日志管理场景。
