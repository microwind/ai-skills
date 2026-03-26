# 数据流水线参考文档

## 数据流水线概述

### 什么是数据流水线
数据流水线是一系列数据处理步骤的集合，用于从多个数据源提取数据，经过转换和处理后，最终加载到目标系统中。

### 流水线类型
- **批处理流水线**: 定期处理大量数据
- **流处理流水线**: 实时处理连续数据流
- **混合流水线**: 结合批处理和流处理
- **ETL流水线**: 抽取、转换、加载的标准流程
- **ELT流水线**: 抽取、加载、转换的现代化流程

### 核心组件
- **数据源**: 各种数据输入源
- **数据抽取**: 从源系统获取数据
- **数据转换**: 清洗、转换、丰富数据
- **数据加载**: 将处理后的数据写入目标系统
- **监控**: 监控流水线运行状态
- **调度**: 控制流水线执行时机

## 数据源接入

### 关系型数据库接入

#### MySQL连接配置
```python
import mysql.connector
from mysql.connector import Error
import pandas as pd

class MySQLConnector:
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            print("MySQL连接成功")
            return True
        except Error as e:
            print(f"MySQL连接失败: {e}")
            return False
    
    def execute_query(self, query, params=None):
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                return pd.DataFrame(result)
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Error as e:
            print(f"查询执行失败: {e}")
            return None
        finally:
            cursor.close()
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL连接已关闭")

# 使用示例
mysql_connector = MySQLConnector(
    host="localhost",
    port=3306,
    database="test_db",
    username="root",
    password="password"
)

# 执行查询
df = mysql_connector.execute_query("SELECT * FROM users WHERE age > %s", (25,))
print(df.head())

# 执行更新
affected_rows = mysql_connector.execute_query(
    "UPDATE users SET status = %s WHERE id = %s", 
    ("active", 1)
)
print(f"影响行数: {affected_rows}")
```

#### PostgreSQL连接配置
```python
import psycopg2
from psycopg2 import sql
import pandas as pd

class PostgreSQLConnector:
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            print("PostgreSQL连接成功")
            return True
        except psycopg2.Error as e:
            print(f"PostgreSQL连接失败: {e}")
            return False
    
    def execute_query(self, query, params=None):
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=columns)
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except psycopg2.Error as e:
            print(f"查询执行失败: {e}")
            return None
        finally:
            cursor.close()
    
    def copy_from_csv(self, table_name, csv_file, delimiter=','):
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            with open(csv_file, 'r') as f:
                cursor.copy_expert(
                    f"COPY {table_name} FROM STDIN WITH DELIMITER '{delimiter}' CSV HEADER",
                    f
                )
            self.connection.commit()
            print("CSV数据导入成功")
        except psycopg2.Error as e:
            print(f"CSV导入失败: {e}")
        finally:
            cursor.close()

# 使用示例
pg_connector = PostgreSQLConnector(
    host="localhost",
    port=5432,
    database="test_db",
    username="postgres",
    password="password"
)

# 执行查询
df = pg_connector.execute_query("SELECT * FROM products WHERE price > %s", (100,))
print(df.head())
```

### NoSQL数据库接入

#### MongoDB连接配置
```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pandas as pd

class MongoDBConnector:
    def __init__(self, host, port, database, username=None, password=None):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.client = None
        self.db = None
    
    def connect(self):
        try:
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            else:
                connection_string = f"mongodb://{self.host}:{self.port}"
            
            self.client = MongoClient(connection_string)
            self.db = self.client[self.database]
            
            # 测试连接
            self.client.admin.command('ping')
            print("MongoDB连接成功")
            return True
        except ConnectionFailure as e:
            print(f"MongoDB连接失败: {e}")
            return False
    
    def find_documents(self, collection_name, query=None, projection=None):
        if not self.db:
            self.connect()
        
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query or {}, projection or {})
            documents = list(cursor)
            return pd.DataFrame(documents)
        except Exception as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()
    
    def insert_documents(self, collection_name, documents):
        if not self.db:
            self.connect()
        
        try:
            collection = self.db[collection_name]
            if isinstance(documents, list):
                result = collection.insert_many(documents)
                return len(result.inserted_ids)
            else:
                result = collection.insert_one(documents)
                return 1
        except Exception as e:
            print(f"插入失败: {e}")
            return 0
    
    def update_documents(self, collection_name, query, update, upsert=False):
        if not self.db:
            self.connect()
        
        try:
            collection = self.db[collection_name]
            result = collection.update_many(query, update, upsert=upsert)
            return result.modified_count
        except Exception as e:
            print(f"更新失败: {e}")
            return 0
    
    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB连接已关闭")

# 使用示例
mongo_connector = MongoDBConnector(
    host="localhost",
    port=27017,
    database="test_db",
    username="admin",
    password="password"
)

# 查询文档
df = mongo_connector.find_documents("users", {"age": {"$gt": 25}})
print(df.head())

# 插入文档
new_users = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "Los Angeles"}
]
inserted_count = mongo_connector.insert_documents("users", new_users)
print(f"插入文档数: {inserted_count}")
```

#### Redis连接配置
```python
import redis
from redis.exceptions import ConnectionError
import json
import pandas as pd

class RedisConnector:
    def __init__(self, host, port, password=None, db=0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client = None
    
    def connect(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True
            )
            
            # 测试连接
            self.client.ping()
            print("Redis连接成功")
            return True
        except ConnectionError as e:
            print(f"Redis连接失败: {e}")
            return False
    
    def set_value(self, key, value, ex=None):
        if not self.client:
            self.connect()
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            print(f"设置值失败: {e}")
            return False
    
    def get_value(self, key):
        if not self.client:
            self.connect()
        
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"获取值失败: {e}")
            return None
    
    def list_keys(self, pattern="*"):
        if not self.client:
            self.connect()
        
        try:
            return self.client.keys(pattern)
        except Exception as e:
            print(f"获取键列表失败: {e}")
            return []
    
    def delete_key(self, key):
        if not self.client:
            self.connect()
        
        try:
            return self.client.delete(key)
        except Exception as e:
            print(f"删除键失败: {e}")
            return 0
    
    def get_hash_data(self, key):
        if not self.client:
            self.connect()
        
        try:
            hash_data = self.client.hgetall(key)
            return pd.DataFrame(list(hash_data.items()), columns=['field', 'value'])
        except Exception as e:
            print(f"获取哈希数据失败: {e}")
            return pd.DataFrame()

# 使用示例
redis_connector = RedisConnector(
    host="localhost",
    port=6379,
    password="password",
    db=0
)

# 设置值
redis_connector.set_value("user:1", {"name": "Alice", "age": 30})
redis_connector.set_value("user:2", {"name": "Bob", "age": 25})

# 获取值
user_data = redis_connector.get_value("user:1")
print(f"用户数据: {user_data}")

# 列出所有键
keys = redis_connector.list_keys("user:*")
print(f"用户键: {keys}")
```

### 文件系统接入

#### 本地文件读取
```python
import pandas as pd
import os
from pathlib import Path
import json
import csv

class FileSystemConnector:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
    
    def read_csv(self, file_path, **kwargs):
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")
        
        try:
            return pd.read_csv(full_path, **kwargs)
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return pd.DataFrame()
    
    def read_json(self, file_path, **kwargs):
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")
        
        try:
            return pd.read_json(full_path, **kwargs)
        except Exception as e:
            print(f"读取JSON文件失败: {e}")
            return pd.DataFrame()
    
    def read_parquet(self, file_path, **kwargs):
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"文件不存在: {full_path}")
        
        try:
            return pd.read_parquet(full_path, **kwargs)
        except Exception as e:
            print(f"读取Parquet文件失败: {e}")
            return pd.DataFrame()
    
    def write_csv(self, df, file_path, **kwargs):
        full_path = self.base_path / file_path
        
        # 创建目录（如果不存在）
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            df.to_csv(full_path, **kwargs)
            print(f"CSV文件写入成功: {full_path}")
            return True
        except Exception as e:
            print(f"写入CSV文件失败: {e}")
            return False
    
    def write_parquet(self, df, file_path, **kwargs):
        full_path = self.base_path / file_path
        
        # 创建目录（如果不存在）
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            df.to_parquet(full_path, **kwargs)
            print(f"Parquet文件写入成功: {full_path}")
            return True
        except Exception as e:
            print(f"写入Parquet文件失败: {e}")
            return False
    
    def list_files(self, pattern="*"):
        try:
            return list(self.base_path.glob(pattern))
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []
    
    def get_file_info(self, file_path):
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            return None
        
        try:
            stat = full_path.stat()
            return {
                'name': full_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime
            }
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None

# 使用示例
fs_connector = FileSystemConnector("/data/files")

# 读取CSV文件
df = fs_connector.read_csv("users.csv", encoding='utf-8')
print(df.head())

# 读取JSON文件
df_json = fs_connector.read_json("products.json")
print(df_json.head())

# 写入Parquet文件
fs_connector.write_parquet(df, "processed/users.parquet")

# 列出所有CSV文件
csv_files = fs_connector.list_files("*.csv")
print(f"CSV文件: {csv_files}")
```

#### 云存储接入 (S3)
```python
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import pandas as pd
import io

class S3Connector:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name='us-east-1'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.client = None
        self.resource = None
    
    def connect(self):
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            self.resource = boto3.resource(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            print("S3连接成功")
            return True
        except NoCredentialsError:
            print("AWS凭证未找到")
            return False
        except Exception as e:
            print(f"S3连接失败: {e}")
            return False
    
    def read_csv_from_s3(self, bucket_name, file_path, **kwargs):
        if not self.client:
            self.connect()
        
        try:
            obj = self.client.get_object(Bucket=bucket_name, Key=file_path)
            df = pd.read_csv(obj['Body'], **kwargs)
            return df
        except ClientError as e:
            print(f"从S3读取CSV失败: {e}")
            return pd.DataFrame()
    
    def read_parquet_from_s3(self, bucket_name, file_path, **kwargs):
        if not self.client:
            self.connect()
        
        try:
            obj = self.client.get_object(Bucket=bucket_name, Key=file_path)
            df = pd.read_parquet(io.BytesIO(obj['Body'].read()), **kwargs)
            return df
        except ClientError as e:
            print(f"从S3读取Parquet失败: {e}")
            return pd.DataFrame()
    
    def write_csv_to_s3(self, df, bucket_name, file_path, **kwargs):
        if not self.client:
            self.connect()
        
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, **kwargs)
            
            self.client.put_object(
                Bucket=bucket_name,
                Key=file_path,
                Body=csv_buffer.getvalue()
            )
            print(f"CSV文件写入S3成功: {file_path}")
            return True
        except ClientError as e:
            print(f"写入CSV到S3失败: {e}")
            return False
    
    def write_parquet_to_s3(self, df, bucket_name, file_path, **kwargs):
        if not self.client:
            self.connect()
        
        try:
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, **kwargs)
            
            self.client.put_object(
                Bucket=bucket_name,
                Key=file_path,
                Body=parquet_buffer.getvalue()
            )
            print(f"Parquet文件写入S3成功: {file_path}")
            return True
        except ClientError as e:
            print(f"写入Parquet到S3失败: {e}")
            return False
    
    def list_objects(self, bucket_name, prefix=""):
        if not self.client:
            self.connect()
        
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            objects = response.get('Contents', [])
            return [obj['Key'] for obj in objects]
        except ClientError as e:
            print(f"列出S3对象失败: {e}")
            return []
    
    def delete_object(self, bucket_name, file_path):
        if not self.client:
            self.connect()
        
        try:
            self.client.delete_object(Bucket=bucket_name, Key=file_path)
            print(f"S3对象删除成功: {file_path}")
            return True
        except ClientError as e:
            print(f"删除S3对象失败: {e}")
            return False

# 使用示例
s3_connector = S3Connector(
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="us-west-2"
)

# 从S3读取CSV
df = s3_connector.read_csv_from_s3("my-bucket", "data/users.csv")
print(df.head())

# 写入Parquet到S3
s3_connector.write_parquet_to_s3(df, "my-bucket", "processed/users.parquet")

# 列出S3对象
objects = s3_connector.list_objects("my-bucket", "data/")
print(f"S3对象: {objects}")
```

## 数据处理

### 数据清洗

#### 数据质量检查
```python
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class DataQualityChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.quality_report = {}
    
    def check_missing_values(self) -> Dict[str, float]:
        """检查缺失值比例"""
        missing_ratio = self.df.isnull().mean()
        self.quality_report['missing_values'] = missing_ratio.to_dict()
        return missing_ratio
    
    def check_duplicates(self) -> int:
        """检查重复行数量"""
        duplicate_count = self.df.duplicated().sum()
        self.quality_report['duplicate_rows'] = duplicate_count
        return duplicate_count
    
    def check_data_types(self) -> Dict[str, str]:
        """检查数据类型"""
        dtype_info = self.df.dtypes.astype(str).to_dict()
        self.quality_report['data_types'] = dtype_info
        return dtype_info
    
    def check_value_ranges(self, numeric_columns: List[str] = None) -> Dict[str, Dict]:
        """检查数值范围"""
        if numeric_columns is None:
            numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        range_info = {}
        for col in numeric_columns:
            if col in self.df.columns:
                range_info[col] = {
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'mean': self.df[col].mean(),
                    'std': self.df[col].std()
                }
        
        self.quality_report['value_ranges'] = range_info
        return range_info
    
    def check_outliers(self, numeric_columns: List[str] = None, method: str = 'iqr') -> Dict[str, int]:
        """检查异常值"""
        if numeric_columns is None:
            numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        outlier_info = {}
        
        for col in numeric_columns:
            if col in self.df.columns:
                if method == 'iqr':
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)]
                    outlier_info[col] = len(outliers)
                elif method == 'zscore':
                    z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                    outliers = self.df[z_scores > 3]
                    outlier_info[col] = len(outliers)
        
        self.quality_report['outliers'] = outlier_info
        return outlier_info
    
    def generate_quality_report(self) -> Dict:
        """生成数据质量报告"""
        self.check_missing_values()
        self.check_duplicates()
        self.check_data_types()
        self.check_value_ranges()
        self.check_outliers()
        
        return self.quality_report
    
    def print_quality_report(self):
        """打印数据质量报告"""
        report = self.generate_quality_report()
        
        print("=== 数据质量报告 ===")
        print(f"数据形状: {self.df.shape}")
        print(f"重复行数: {report.get('duplicate_rows', 0)}")
        
        print("\n缺失值比例:")
        missing_values = report.get('missing_values', {})
        for col, ratio in missing_values.items():
            if ratio > 0:
                print(f"  {col}: {ratio:.2%}")
        
        print("\n异常值数量:")
        outliers = report.get('outliers', {})
        for col, count in outliers.items():
            if count > 0:
                print(f"  {col}: {count}")
        
        print("\n数据类型:")
        data_types = report.get('data_types', {})
        for col, dtype in data_types.items():
            print(f"  {col}: {dtype}")

# 使用示例
# 假设有一个DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Alice', None],
    'age': [25, 30, 35, 25, 1000],
    'salary': [50000, 60000, 70000, 50000, 80000],
    'email': ['alice@email.com', 'bob@email.com', 'charlie@email.com', 'alice@email.com', 'invalid']
}

df = pd.DataFrame(data)

# 数据质量检查
quality_checker = DataQualityChecker(df)
quality_checker.print_quality_report()
```

#### 数据清洗工具
```python
class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_shape = df.shape
    
    def remove_duplicates(self, subset: List[str] = None, keep: str = 'first') -> pd.DataFrame:
        """删除重复行"""
        original_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed_count = original_count - len(self.df)
        print(f"删除了 {removed_count} 行重复数据")
        return self.df
    
    def handle_missing_values(self, strategy: str = 'drop', **kwargs) -> pd.DataFrame:
        """处理缺失值"""
        if strategy == 'drop':
            # 删除包含缺失值的行
            self.df = self.df.dropna(**kwargs)
            print(f"删除缺失值后数据形状: {self.df.shape}")
        
        elif strategy == 'fill':
            # 填充缺失值
            fill_value = kwargs.get('value', 0)
            method = kwargs.get('method', None)
            
            if method:
                self.df = self.df.fillna(method=method)
            else:
                self.df = self.df.fillna(fill_value)
            
            print(f"使用策略 {strategy} 填充缺失值")
        
        elif strategy == 'interpolate':
            # 插值填充
            method = kwargs.get('method', 'linear')
            self.df = self.df.interpolate(method=method)
            print(f"使用 {method} 插值填充缺失值")
        
        return self.df
    
    def remove_outliers(self, columns: List[str] = None, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """移除异常值"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        original_count = len(self.df)
        
        for col in columns:
            if col in self.df.columns:
                if method == 'iqr':
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - threshold * IQR
                    upper_bound = Q3 + threshold * IQR
                    
                    self.df = self.df[(self.df[col] >= lower_bound) & (self.df[col] <= upper_bound)]
                
                elif method == 'zscore':
                    z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                    self.df = self.df[z_scores < threshold]
        
        removed_count = original_count - len(self.df)
        print(f"移除了 {removed_count} 行异常值")
        return self.df
    
    def standardize_text(self, columns: List[str] = None, operations: List[str] = None) -> pd.DataFrame:
        """标准化文本数据"""
        if columns is None:
            columns = self.df.select_dtypes(include=['object']).columns.tolist()
        
        if operations is None:
            operations = ['strip', 'lower']
        
        for col in columns:
            if col in self.df.columns:
                for operation in operations:
                    if operation == 'strip':
                        self.df[col] = self.df[col].astype(str).str.strip()
                    elif operation == 'lower':
                        self.df[col] = self.df[col].astype(str).str.lower()
                    elif operation == 'upper':
                        self.df[col] = self.df[col].astype(str).str.upper()
                    elif operation == 'title':
                        self.df[col] = self.df[col].astype(str).str.title()
        
        print(f"标准化了 {len(columns)} 列文本数据")
        return self.df
    
    def validate_email(self, email_column: str) -> pd.DataFrame:
        """验证邮箱格式"""
        import re
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if email_column in self.df.columns:
            self.df[f'{email_column}_valid'] = self.df[email_column].astype(str).str.match(email_pattern)
            
            invalid_emails = self.df[~self.df[f'{email_column}_valid']]
            print(f"发现 {len(invalid_emails)} 个无效邮箱")
        
        return self.df
    
    def convert_data_types(self, type_mapping: Dict[str, str]) -> pd.DataFrame:
        """转换数据类型"""
        for column, target_type in type_mapping.items():
            if column in self.df.columns:
                try:
                    if target_type == 'datetime':
                        self.df[column] = pd.to_datetime(self.df[column])
                    elif target_type == 'category':
                        self.df[column] = self.df[column].astype('category')
                    else:
                        self.df[column] = self.df[column].astype(target_type)
                    
                    print(f"列 {column} 转换为 {target_type}")
                except Exception as e:
                    print(f"列 {column} 类型转换失败: {e}")
        
        return self.df
    
    def get_cleaning_summary(self) -> Dict:
        """获取清洗摘要"""
        return {
            'original_shape': self.original_shape,
            'cleaned_shape': self.df.shape,
            'rows_removed': self.original_shape[0] - self.df.shape[0],
            'columns_removed': self.original_shape[1] - self.df.shape[1]
        }

# 使用示例
cleaner = DataCleaner(df)

# 数据清洗流程
cleaner.remove_duplicates()
cleaner.handle_missing_values(strategy='fill', value='Unknown')
cleaner.remove_outliers(columns=['age', 'salary'])
cleaner.standardize_text(columns=['name', 'email'])
cleaner.validate_email('email')

# 转换数据类型
type_mapping = {
    'age': 'int',
    'salary': 'float',
    'name': 'category'
}
cleaner.convert_data_types(type_mapping)

# 获取清洗摘要
summary = cleaner.get_cleaning_summary()
print(f"清洗摘要: {summary}")

# 获取清洗后的数据
cleaned_df = cleaner.df
print(f"清洗后数据形状: {cleaned_df.shape}")
```

### 数据转换

#### 数据转换工具
```python
class DataTransformer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def create_derived_columns(self, transformations: Dict[str, str]) -> pd.DataFrame:
        """创建派生列"""
        for new_col, expression in transformations.items():
            try:
                # 使用eval执行表达式
                self.df[new_col] = self.df.eval(expression)
                print(f"创建派生列: {new_col}")
            except Exception as e:
                print(f"创建派生列 {new_col} 失败: {e}")
        
        return self.df
    
    def apply_function_to_column(self, column: str, func, new_column: str = None) -> pd.DataFrame:
        """对列应用函数"""
        if new_column is None:
            new_column = f"{column}_transformed"
        
        try:
            self.df[new_column] = self.df[column].apply(func)
            print(f"对列 {column} 应用函数，创建新列 {new_column}")
        except Exception as e:
            print(f"对列 {column} 应用函数失败: {e}")
        
        return self.df
    
    def normalize_columns(self, columns: List[str] = None, method: str = 'minmax') -> pd.DataFrame:
        """标准化列"""
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        from sklearn.preprocessing import MinMaxScaler, StandardScaler
        
        for col in columns:
            if col in self.df.columns:
                if method == 'minmax':
                    scaler = MinMaxScaler()
                    self.df[f"{col}_normalized"] = scaler.fit_transform(self.df[[col]])
                elif method == 'zscore':
                    scaler = StandardScaler()
                    self.df[f"{col}_standardized"] = scaler.fit_transform(self.df[[col]])
                
                print(f"标准化列 {col} 使用 {method} 方法")
        
        return self.df
    
    def bin_column(self, column: str, bins: int = 5, labels: List[str] = None) -> pd.DataFrame:
        """分箱列"""
        if column in self.df.columns:
            try:
                self.df[f"{column}_binned"] = pd.cut(self.df[column], bins=bins, labels=labels)
                print(f"对列 {column} 进行分箱，分为 {bins} 组")
            except Exception as e:
                print(f"分箱列 {column} 失败: {e}")
        
        return self.df
    
    def encode_categorical_columns(self, columns: List[str] = None, method: str = 'onehot') -> pd.DataFrame:
        """编码分类列"""
        if columns is None:
            columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        for col in columns:
            if col in self.df.columns:
                if method == 'onehot':
                    # One-Hot编码
                    dummies = pd.get_dummies(self.df[col], prefix=col)
                    self.df = pd.concat([self.df, dummies], axis=1)
                    print(f"对列 {col} 进行One-Hot编码")
                
                elif method == 'label':
                    # 标签编码
                    from sklearn.preprocessing import LabelEncoder
                    le = LabelEncoder()
                    self.df[f"{col}_encoded"] = le.fit_transform(self.df[col].astype(str))
                    print(f"对列 {col} 进行标签编码")
        
        return self.df
    
    def aggregate_data(self, group_by: List[str], aggregations: Dict[str, str]) -> pd.DataFrame:
        """聚合数据"""
        try:
            agg_df = self.df.groupby(group_by).agg(aggregations).reset_index()
            print(f"按 {group_by} 聚合数据")
            return agg_df
        except Exception as e:
            print(f"聚合数据失败: {e}")
            return pd.DataFrame()
    
    def pivot_data(self, index: str, columns: str, values: str, aggfunc: str = 'sum') -> pd.DataFrame:
        """透视数据"""
        try:
            pivot_df = self.df.pivot_table(
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                fill_value=0
            )
            print(f"透视数据: index={index}, columns={columns}, values={values}")
            return pivot_df.reset_index()
        except Exception as e:
            print(f"透视数据失败: {e}")
            return pd.DataFrame()
    
    def melt_data(self, id_vars: List[str], value_vars: List[str], 
                  var_name: str = 'variable', value_name: str = 'value') -> pd.DataFrame:
        """熔化数据"""
        try:
            melted_df = pd.melt(
                self.df,
                id_vars=id_vars,
                value_vars=value_vars,
                var_name=var_name,
                value_name=value_name
            )
            print(f"熔化数据: id_vars={id_vars}, value_vars={value_vars}")
            return melted_df
        except Exception as e:
            print(f"熔化数据失败: {e}")
            return pd.DataFrame()

# 使用示例
transformer = DataTransformer(cleaned_df)

# 创建派生列
transformations = {
    'age_squared': 'age ** 2',
    'salary_per_age': 'salary / age',
    'age_group': 'age // 10 * 10'
}
transformer.create_derived_columns(transformations)

# 应用函数
transformer.apply_function_to_column('name', lambda x: len(str(x)), 'name_length')

# 标准化数值列
transformer.normalize_columns(columns=['age', 'salary'], method='minmax')

# 分箱
transformer.bin_column('age', bins=3, labels=['Young', 'Middle', 'Old'])

# 编码分类列
transformer.encode_categorical_columns(columns=['name'], method='label')

# 聚合数据
aggregated_df = transformer.aggregate_data(
    group_by=['age_group'],
    aggregations={'salary': 'mean', 'age': 'count'}
)

# 透视数据
pivot_df = transformer.pivot_data(
    index='age_group',
    columns='name',
    values='salary',
    aggfunc='mean'
)

# 获取转换后的数据
transformed_df = transformer.df
print(f"转换后数据形状: {transformed_df.shape}")
```

## 流处理

### Kafka流处理

#### Kafka生产者和消费者
```python
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import time
from typing import Dict, Any

class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers: List[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # 等待所有副本确认
            retries=3,
            batch_size=16384,
            linger_ms=10,
            buffer_memory=33554432
        )
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None) -> bool:
        """发送消息"""
        try:
            future = self.producer.send(topic, value=message, key=key)
            record_metadata = future.get(timeout=10)
            
            print(f"消息发送成功: topic={record_metadata.topic}, "
                  f"partition={record_metadata.partition}, offset={record_metadata.offset}")
            return True
        except KafkaError as e:
            print(f"消息发送失败: {e}")
            return False
    
    def send_batch_messages(self, topic: str, messages: List[Dict[str, Any]]) -> int:
        """批量发送消息"""
        success_count = 0
        
        for i, message in enumerate(messages):
            key = message.get('key', f"msg_{i}")
            if self.send_message(topic, message, key):
                success_count += 1
            time.sleep(0.01)  # 避免过快发送
        
        print(f"批量发送完成: 成功 {success_count}/{len(messages)}")
        return success_count
    
    def close(self):
        """关闭生产者"""
        self.producer.close()
        print("Kafka生产者已关闭")

class KafkaConsumerWrapper:
    def __init__(self, bootstrap_servers: List[str], group_id: str):
        self.consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',  # 从最早的消息开始消费
            enable_auto_commit=True,  # 自动提交偏移量
            auto_commit_interval_ms=1000,
            session_timeout_ms=30000,
            heartbeat_interval_ms=3000
        )
    
    def subscribe_topics(self, topics: List[str]):
        """订阅主题"""
        self.consumer.subscribe(topics)
        print(f"订阅主题: {topics}")
    
    def consume_messages(self, timeout_ms: int = 1000, max_messages: int = None) -> List[Dict[str, Any]]:
        """消费消息"""
        messages = []
        message_count = 0
        
        try:
            for message in self.consumer:
                messages.append({
                    'topic': message.topic,
                    'partition': message.partition,
                    'offset': message.offset,
                    'key': message.key,
                    'value': message.value,
                    'timestamp': message.timestamp
                })
                
                message_count += 1
                
                if max_messages and message_count >= max_messages:
                    break
                    
        except KeyboardInterrupt:
            print("消费者被中断")
        
        return messages
    
    def process_messages_stream(self, process_func, timeout_ms: int = 1000):
        """流式处理消息"""
        try:
            for message in self.consumer:
                try:
                    process_func(message)
                except Exception as e:
                    print(f"处理消息失败: {e}")
                    
        except KeyboardInterrupt:
            print("消费者被中断")
    
    def close(self):
        """关闭消费者"""
        self.consumer.close()
        print("Kafka消费者已关闭")

# 使用示例
# 生产者示例
producer = KafkaProducerWrapper(['localhost:9092'])

# 发送单条消息
message = {
    'user_id': 123,
    'action': 'login',
    'timestamp': time.time(),
    'ip_address': '192.168.1.1'
}
producer.send_message('user_events', message, key='user_123')

# 批量发送消息
batch_messages = [
    {'user_id': i, 'action': 'click', 'timestamp': time.time()}
    for i in range(1, 11)
]
producer.send_batch_messages('user_events', batch_messages)

# 消费者示例
def process_user_event(message):
    """处理用户事件"""
    print(f"处理事件: {message.value}")
    # 这里可以添加具体的业务逻辑

consumer = KafkaConsumerWrapper(['localhost:9092'], 'user_event_processor')
consumer.subscribe_topics(['user_events'])

# 流式处理
consumer.process_messages_stream(process_user_event)

# 或者批量消费
messages = consumer.consume_messages(max_messages=5)
for msg in messages:
    print(f"消费消息: {msg}")

# 清理资源
producer.close()
consumer.close()
```

### Flink流处理

#### Flink数据处理
```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction, FilterFunction
import json
import time

class EventProcessor(MapFunction):
    """事件处理器"""
    def map(self, value):
        try:
            event = json.loads(value)
            
            # 添加处理时间戳
            event['processed_at'] = time.time()
            
            # 计算事件类型
            if 'action' in event:
                event['event_type'] = self._classify_event(event['action'])
            
            return json.dumps(event)
        except Exception as e:
            print(f"处理事件失败: {e}")
            return None
    
    def _classify_event(self, action):
        """分类事件"""
        if action in ['login', 'logout']:
            return 'auth'
        elif action in ['click', 'view']:
            return 'interaction'
        elif action in ['purchase', 'refund']:
            return 'transaction'
        else:
            return 'other'

class EventFilter(FilterFunction):
    """事件过滤器"""
    def __init__(self, event_type=None):
        self.event_type = event_type
    
    def filter(self, value):
        try:
            event = json.loads(value)
            if self.event_type:
                return event.get('event_type') == self.event_type
            return True
        except:
            return False

class FlinkStreamProcessor:
    def __init__(self):
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.table_env = StreamTableEnvironment.create(self.env)
        
        # 设置并行度
        self.env.set_parallelism(4)
        
        # 设置检查点
        self.env.enable_checkpointing(60000)  # 60秒
    
    def create_kafka_consumer(self, topic: str, group_id: str, bootstrap_servers: str):
        """创建Kafka消费者"""
        properties = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': 'true'
        }
        
        consumer = FlinkKafkaConsumer(
            topics=topic,
            deserialization_schema=SimpleStringSchema(),
            properties=properties
        )
        
        return consumer
    
    def create_kafka_producer(self, topic: str, bootstrap_servers: str):
        """创建Kafka生产者"""
        properties = {
            'bootstrap.servers': bootstrap_servers
        }
        
        producer = FlinkKafkaProducer(
            topic=topic,
            serialization_schema=SimpleStringSchema(),
            producer_config=properties
        )
        
        return producer
    
    def process_user_events(self, input_topic: str, output_topic: str, 
                          bootstrap_servers: str, group_id: str):
        """处理用户事件流"""
        # 创建消费者
        consumer = self.create_kafka_consumer(input_topic, group_id, bootstrap_servers)
        
        # 创建数据流
        stream = self.env.add_source(consumer)
        
        # 处理数据流
        processed_stream = stream \
            .map(EventProcessor(), output_type=Types.STRING()) \
            .filter(EventFilter(), output_type=Types.STRING())
        
        # 创建生产者
        producer = self.create_kafka_producer(output_topic, bootstrap_servers)
        
        # 输出到Kafka
        processed_stream.add_sink(producer)
        
        # 执行作业
        self.env.execute("User Event Processing Job")
    
    def create_table_from_kafka(self, topic: str, bootstrap_servers: str):
        """从Kafka创建表"""
        table_source = f"""
        CREATE TABLE user_events (
            user_id BIGINT,
            action STRING,
            timestamp BIGINT,
            ip_address STRING,
            processed_at BIGINT,
            event_type STRING,
            proc_time AS PROCTIME()
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{topic}',
            'properties.bootstrap.servers' = '{bootstrap_servers}',
            'properties.group.id' = 'flink_table_group',
            'format' = 'json',
            'scan.startup.mode' = 'latest-offset'
        )
        """
        
        self.table_env.execute_sql(table_source)
        print(f"创建表: {topic}")
    
    def run_sql_query(self, query: str):
        """运行SQL查询"""
        result_table = self.table_env.sql_query(query)
        
        # 执行查询并打印结果
        result_table.execute().print()
    
    def aggregate_events_by_window(self, topic: str, bootstrap_servers: str):
        """按窗口聚合事件"""
        # 创建表
        self.create_table_from_kafka(topic, bootstrap_servers)
        
        # 窗口聚合查询
        window_query = """
        SELECT 
            TUMBLE_START(proc_time, INTERVAL '1' MINUTE) as window_start,
            event_type,
            COUNT(*) as event_count,
            COUNT(DISTINCT user_id) as unique_users
        FROM user_events
        GROUP BY 
            TUMBLE(proc_time, INTERVAL '1' MINUTE),
            event_type
        """
        
        self.run_sql_query(window_query)

# 使用示例
processor = FlinkStreamProcessor()

# 方式1: DataStream API
processor.process_user_events(
    input_topic='user_events',
    output_topic='processed_events',
    bootstrap_servers='localhost:9092',
    group_id='flink_processor'
)

# 方式2: Table API/SQL
processor.aggregate_events_by_window(
    topic='user_events',
    bootstrap_servers='localhost:9092'
)
```

## 监控和运维

### 流水线监控

#### 监控指标收集
```python
import time
import psutil
import threading
from collections import defaultdict, deque
from typing import Dict, List, Any
import json

class PipelineMonitor:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.alerts = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 80.0,
            'disk_usage': 90.0,
            'error_rate': 5.0,
            'latency_p99': 1000.0  # 毫秒
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: int = 60):
        """启动监控"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("监控已停止")
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.monitoring:
            try:
                # 收集系统指标
                self._collect_system_metrics()
                
                # 检查告警
                self._check_alerts()
                
                time.sleep(interval)
            except Exception as e:
                print(f"监控循环错误: {e}")
    
    def _collect_system_metrics(self):
        """收集系统指标"""
        timestamp = time.time()
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics['cpu_usage'].append((timestamp, cpu_percent))
        
        # 内存使用率
        memory = psutil.virtual_memory()
        self.metrics['memory_usage'].append((timestamp, memory.percent))
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.metrics['disk_usage'].append((timestamp, disk_percent))
        
        # 网络IO
        network = psutil.net_io_counters()
        self.metrics['network_bytes_sent'].append((timestamp, network.bytes_sent))
        self.metrics['network_bytes_recv'].append((timestamp, network.bytes_recv))
    
    def record_pipeline_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """记录流水线指标"""
        timestamp = time.time()
        metric_data = {
            'timestamp': timestamp,
            'value': value,
            'tags': tags or {}
        }
        self.metrics[metric_name].append(metric_data)
    
    def record_throughput(self, count: int, duration: float):
        """记录吞吐量"""
        throughput = count / duration if duration > 0 else 0
        self.record_pipeline_metric('throughput', throughput)
    
    def record_latency(self, latency_ms: float):
        """记录延迟"""
        self.record_pipeline_metric('latency', latency_ms)
    
    def record_error(self, error_type: str, error_message: str):
        """记录错误"""
        timestamp = time.time()
        error_data = {
            'timestamp': timestamp,
            'type': error_type,
            'message': error_message
        }
        self.metrics['errors'].append(error_data)
    
    def _check_alerts(self):
        """检查告警"""
        current_time = time.time()
        
        # 检查CPU使用率
        if self.metrics['cpu_usage']:
            latest_cpu = self.metrics['cpu_usage'][-1][1]
            if latest_cpu > self.thresholds['cpu_usage']:
                self._create_alert('high_cpu_usage', f"CPU使用率过高: {latest_cpu:.1f}%")
        
        # 检查内存使用率
        if self.metrics['memory_usage']:
            latest_memory = self.metrics['memory_usage'][-1][1]
            if latest_memory > self.thresholds['memory_usage']:
                self._create_alert('high_memory_usage', f"内存使用率过高: {latest_memory:.1f}%")
        
        # 检查错误率
        if self.metrics['errors']:
            recent_errors = [e for e in self.metrics['errors'] 
                          if current_time - e['timestamp'] < 300]  # 5分钟内的错误
            error_rate = len(recent_errors) / 300 * 60  # 每分钟错误数
            if error_rate > self.thresholds['error_rate']:
                self._create_alert('high_error_rate', f"错误率过高: {error_rate:.1f}/min")
    
    def _create_alert(self, alert_type: str, message: str):
        """创建告警"""
        alert = {
            'timestamp': time.time(),
            'type': alert_type,
            'message': message,
            'severity': 'warning'
        }
        self.alerts.append(alert)
        print(f"告警: {alert}")
    
    def get_metric_summary(self, metric_name: str, duration_minutes: int = 60) -> Dict[str, float]:
        """获取指标摘要"""
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}
        
        current_time = time.time()
        cutoff_time = current_time - duration_minutes * 60
        
        # 过滤最近的数据
        recent_data = []
        for data in self.metrics[metric_name]:
            if isinstance(data, tuple):
                timestamp, value = data
                if timestamp >= cutoff_time:
                    recent_data.append(value)
            elif isinstance(data, dict):
                if data['timestamp'] >= cutoff_time:
                    recent_data.append(data['value'])
        
        if not recent_data:
            return {}
        
        return {
            'count': len(recent_data),
            'min': min(recent_data),
            'max': max(recent_data),
            'avg': sum(recent_data) / len(recent_data),
            'latest': recent_data[-1]
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {}
        
        # 系统指标
        status['cpu_usage'] = self.get_metric_summary('cpu_usage')
        status['memory_usage'] = self.get_metric_summary('memory_usage')
        status['disk_usage'] = self.get_metric_summary('disk_usage')
        
        # 流水线指标
        status['throughput'] = self.get_metric_summary('throughput')
        status['latency'] = self.get_metric_summary('latency')
        
        # 错误统计
        if self.metrics['errors']:
            recent_errors = [e for e in self.metrics['errors'] 
                           if time.time() - e['timestamp'] < 3600]  # 1小时内的错误
            status['errors'] = {
                'count': len(recent_errors),
                'types': list(set(e['type'] for e in recent_errors))
            }
        
        # 告警
        status['alerts'] = [alert for alert in self.alerts 
                          if time.time() - alert['timestamp'] < 3600]  # 1小时内的告警
        
        return status
    
    def export_metrics(self, filename: str):
        """导出指标数据"""
        export_data = {
            'metrics': {},
            'alerts': self.alerts,
            'thresholds': self.thresholds
        }
        
        for metric_name, values in self.metrics.items():
            export_data['metrics'][metric_name] = list(values)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"指标数据已导出到: {filename}")

# 使用示例
monitor = PipelineMonitor()

# 启动监控
monitor.start_monitoring(interval=30)

# 记录流水线指标
for i in range(100):
    monitor.record_throughput(1000, 60)  # 1000条记录/分钟
    monitor.record_latency(50.5)  # 50.5ms延迟
    time.sleep(0.1)

# 记录错误
monitor.record_error('data_validation', 'Invalid email format')
monitor.record_error('connection_error', 'Database connection failed')

# 获取系统状态
status = monitor.get_system_status()
print(f"系统状态: {json.dumps(status, indent=2)}")

# 获取特定指标摘要
cpu_summary = monitor.get_metric_summary('cpu_usage', duration_minutes=30)
print(f"CPU使用率摘要: {cpu_summary}")

# 导出指标数据
monitor.export_metrics('pipeline_metrics.json')

# 停止监控
monitor.stop_monitoring()
```

## 参考资源

### 官方文档
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink Documentation](https://flink.apache.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)

### 数据工程工具
- [Apache Beam](https://beam.apache.org/)
- [Apache NiFi](https://nifi.apache.org/)
- [Apache Sqoop](https://sqoop.apache.org/)
- [Apache Storm](https://storm.apache.org/)

### 云数据平台
- [AWS Data Pipeline](https://aws.amazon.com/datapipeline/)
- [Google Cloud Dataflow](https://cloud.google.com/dataflow)
- [Azure Data Factory](https://azure.microsoft.com/en-us/services/data-factory/)
- [Alibaba DataWorks](https://www.alibabacloud.com/product/maxcompute)

### 监控和运维
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [ELK Stack](https://www.elastic.co/)
- [Apache ZooKeeper](https://zookeeper.apache.org/)

### 社区资源
- [Data Engineering Podcast](https://www.dataengineeringpodcast.com/)
- [Data Engineering Weekly](https://www.dataengineeringweekly.com/)
- [Reddit r/dataengineering](https://www.reddit.com/r/dataengineering/)
- [Awesome Data Engineering](https://github.com/igorbarinov/awesome-data-engineering)
