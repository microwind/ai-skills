#!/usr/bin/env python3
"""
数据库备份与恢复演示 - 实现多种备份策略和恢复机制
"""

import os
import json
import time
import sqlite3
import shutil
import gzip
import hashlib
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import uuid
import subprocess

class BackupType(Enum):
    """备份类型"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupStatus(Enum):
    """备份状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CompressionType(Enum):
    """压缩类型"""
    NONE = "none"
    GZIP = "gzip"
    ZIP = "zip"

@dataclass
class BackupConfig:
    """备份配置"""
    backup_type: BackupType
    compression: CompressionType
    backup_path: str
    retention_days: int = 30
    encryption_enabled: bool = False
    schedule: str = "daily"  # daily, weekly, monthly
    max_parallel_jobs: int = 2

@dataclass
class BackupJob:
    """备份任务"""
    id: str
    name: str
    config: BackupConfig
    status: BackupStatus
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    file_size: int
    file_count: int
    error_message: Optional[str]
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = None
        if self.completed_at is None:
            self.completed_at = None
        if self.error_message is None:
            self.error_message = None

@dataclass
class DatabaseConfig:
    """数据库配置"""
    name: str
    type: str  # sqlite, mysql, postgresql
    host: str
    port: int
    username: str
    password: str
    database: str
    backup_path: str

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
    
    def connect(self):
        """连接数据库"""
        if self.config.type == "sqlite":
            self.connection = sqlite3.connect(self.config.database)
        elif self.config.type == "mysql":
            # 模拟MySQL连接
            print(f"🔗 连接MySQL数据库: {self.config.host}:{self.config.port}")
        elif self.config.type == "postgresql":
            # 模拟PostgreSQL连接
            print(f"🔗 连接PostgreSQL数据库: {self.config.host}:{self.config.port}")
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_tables(self) -> List[str]:
        """获取所有表名"""
        if self.config.type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
        else:
            # 模拟其他数据库
            return ["users", "orders", "products", "payments"]
    
    def get_table_data(self, table_name: str) -> List[dict]:
        """获取表数据"""
        if self.config.type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            # 模拟数据
            return [
                {"id": 1, "name": f"Item_{i}", "created_at": datetime.now().isoformat()}
                for i in range(10)
            ]
    
    def execute_sql(self, sql: str) -> Any:
        """执行SQL语句"""
        if self.config.type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            return cursor.fetchall()
        else:
            # 模拟执行
            print(f"🔧 执行SQL: {sql}")
            return []

class BackupEngine:
    """备份引擎"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.running_jobs: Dict[str, threading.Thread] = {}
    
    def create_backup_job(self, name: str, db_manager: DatabaseManager) -> BackupJob:
        """创建备份任务"""
        job = BackupJob(
            id=str(uuid.uuid4()),
            name=name,
            config=self.config,
            status=BackupStatus.PENDING,
            created_at=time.time(),
            started_at=None,
            completed_at=None,
            file_size=0,
            file_count=0,
            error_message=None
        )
        
        self.backup_jobs[job.id] = job
        return job
    
    def start_backup(self, job_id: str, db_manager: DatabaseManager) -> bool:
        """开始备份"""
        if job_id not in self.backup_jobs:
            return False
        
        job = self.backup_jobs[job_id]
        
        if job.status != BackupStatus.PENDING:
            return False
        
        # 创建备份线程
        backup_thread = threading.Thread(
            target=self._execute_backup,
            args=(job, db_manager)
        )
        
        job.status = BackupStatus.RUNNING
        job.started_at = time.time()
        
        self.running_jobs[job_id] = backup_thread
        backup_thread.start()
        
        return True
    
    def _execute_backup(self, job: BackupJob, db_manager: DatabaseManager):
        """执行备份"""
        try:
            print(f"🔄 开始备份: {job.name}")
            
            # 创建备份目录
            backup_dir = os.path.join(self.config.backup_path, f"{job.name}_{job.id}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 连接数据库
            db_manager.connect()
            
            # 获取所有表
            tables = db_manager.get_tables()
            job.file_count = len(tables)
            
            total_size = 0
            
            for table in tables:
                # 备份表数据
                table_backup_path = os.path.join(backup_dir, f"{table}.json")
                
                # 获取表数据
                table_data = db_manager.get_table_data(table)
                
                # 保存为JSON
                with open(table_backup_path, 'w', encoding='utf-8') as f:
                    json.dump(table_data, f, indent=2, ensure_ascii=False, default=str)
                
                file_size = os.path.getsize(table_backup_path)
                total_size += file_size
                
                # 压缩文件
                if self.config.compression == CompressionType.GZIP:
                    self._compress_file(table_backup_path)
                    file_size = os.path.getsize(f"{table_backup_path}.gz")
                    total_size += file_size - os.path.getsize(table_backup_path)
                    os.remove(table_backup_path)
                
                print(f"  ✅ 备份表: {table} ({file_size} bytes)")
            
            # 创建备份清单
            manifest = {
                "backup_id": job.id,
                "backup_name": job.name,
                "backup_type": self.config.backup_type.value,
                "created_at": job.created_at,
                "completed_at": time.time(),
                "tables": tables,
                "file_size": total_size,
                "file_count": len(tables),
                "checksum": self._calculate_checksum(backup_dir)
            }
            
            manifest_path = os.path.join(backup_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
            
            job.file_size = total_size
            job.completed_at = time.time()
            job.status = BackupStatus.COMPLETED
            
            print(f"✅ 备份完成: {job.name}")
            print(f"   文件大小: {total_size} bytes")
            print(f"   文件数量: {len(tables)}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = time.time()
            print(f"❌ 备份失败: {job.name} - {e}")
        
        finally:
            db_manager.disconnect()
            
            # 清理运行中的任务
            if job.id in self.running_jobs:
                del self.running_jobs[job.id]
    
    def _compress_file(self, file_path: str):
        """压缩文件"""
        with open(file_path, 'rb') as f_in:
            with gzip.open(f"{file_path}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _calculate_checksum(self, directory: str) -> str:
        """计算目录校验和"""
        hash_md5 = hashlib.md5()
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    def get_backup_status(self, job_id: str) -> Optional[BackupJob]:
        """获取备份状态"""
        return self.backup_jobs.get(job_id)
    
    def list_backups(self) -> List[BackupJob]:
        """列出所有备份"""
        return list(self.backup_jobs.values())

class RecoveryEngine:
    """恢复引擎"""
    
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
    
    def list_available_backups(self) -> List[dict]:
        """列出可用的备份"""
        backups = []
        
        if not os.path.exists(self.backup_path):
            return backups
        
        for item in os.listdir(self.backup_path):
            item_path = os.path.join(self.backup_path, item)
            
            if os.path.isdir(item_path):
                manifest_path = os.path.join(item_path, "manifest.json")
                
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                            backups.append(manifest)
                    except Exception as e:
                        print(f"❌ 读取备份清单失败: {e}")
        
        return sorted(backups, key=lambda x: x['completed_at'], reverse=True)
    
    def restore_backup(self, backup_id: str, db_manager: DatabaseManager) -> bool:
        """恢复备份"""
        # 查找备份目录
        backup_dir = None
        for item in os.listdir(self.backup_path):
            if backup_id in item and os.path.isdir(os.path.join(self.backup_path, item)):
                backup_dir = os.path.join(self.backup_path, item)
                break
        
        if not backup_dir:
            print(f"❌ 备份不存在: {backup_id}")
            return False
        
        try:
            print(f"🔄 开始恢复: {backup_id}")
            
            # 读取备份清单
            manifest_path = os.path.join(backup_dir, "manifest.json")
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 连接数据库
            db_manager.connect()
            
            # 恢复每个表
            for table in manifest['tables']:
                table_file = os.path.join(backup_dir, f"{table}.json")
                
                if os.path.exists(table_file):
                    # 读取表数据
                    with open(table_file, 'r', encoding='utf-8') as f:
                        table_data = json.load(f)
                    
                    # 恢复数据
                    self._restore_table_data(db_manager, table, table_data)
                    print(f"  ✅ 恢复表: {table} ({len(table_data)} records)")
                
                elif os.path.exists(f"{table_file}.gz"):
                    # 读取压缩数据
                    with gzip.open(f"{table_file}.gz", 'rt', encoding='utf-8') as f:
                        table_data = json.load(f)
                    
                    # 恢复数据
                    self._restore_table_data(db_manager, table, table_data)
                    print(f"  ✅ 恢复表: {table} ({len(table_data)} records)")
            
            print(f"✅ 恢复完成: {backup_id}")
            return True
            
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False
        
        finally:
            db_manager.disconnect()
    
    def _restore_table_data(self, db_manager: DatabaseManager, table_name: str, data: List[dict]):
        """恢复表数据"""
        if db_manager.config.type == "sqlite":
            cursor = db_manager.connection.cursor()
            
            # 清空表
            cursor.execute(f"DELETE FROM {table_name}")
            
            if data:
                # 获取列名
                columns = list(data[0].keys())
                placeholders = ', '.join(['?' for _ in columns])
                
                # 插入数据
                for row in data:
                    values = [row.get(col) for col in columns]
                    cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
            
            db_manager.connection.commit()
        else:
            # 模拟其他数据库恢复
            print(f"🔧 恢复表 {table_name}: {len(data)} records")

class BackupScheduler:
    """备份调度器"""
    
    def __init__(self):
        self.schedules: Dict[str, dict] = {}
        self.running = False
        self.scheduler_thread = None
    
    def add_schedule(self, name: str, backup_engine: BackupEngine, db_manager: DatabaseManager, 
                     schedule_type: str, time_config: dict):
        """添加调度任务"""
        self.schedules[name] = {
            "backup_engine": backup_engine,
            "db_manager": db_manager,
            "schedule_type": schedule_type,  # daily, weekly, monthly
            "time_config": time_config,
            "last_run": None
        }
        
        print(f"📅 添加调度任务: {name} ({schedule_type})")
    
    def start_scheduler(self):
        """启动调度器"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.start()
            print("🚀 备份调度器启动")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("⏹️  备份调度器停止")
    
    def _scheduler_loop(self):
        """调度器循环"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for name, schedule in self.schedules.items():
                    if self._should_run(schedule, current_time):
                        self._run_scheduled_backup(name, schedule)
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                print(f"❌ 调度器错误: {e}")
                time.sleep(60)
    
    def _should_run(self, schedule: dict, current_time: datetime) -> bool:
        """检查是否应该运行"""
        schedule_type = schedule["schedule_type"]
        last_run = schedule["last_run"]
        time_config = schedule["time_config"]
        
        if schedule_type == "daily":
            target_time = current_time.replace(
                hour=time_config["hour"],
                minute=time_config["minute"],
                second=0,
                microsecond=0
            )
            
            if current_time >= target_time and (
                last_run is None or 
                current_time.date() > last_run.date()
            ):
                return True
        
        elif schedule_type == "weekly":
            # 简化实现：每周同一天同一时间
            target_day = time_config["day"]  # 0-6 (Monday-Sunday)
            if current_time.weekday() == target_day:
                target_time = current_time.replace(
                    hour=time_config["hour"],
                    minute=time_config["minute"],
                    second=0,
                    microsecond=0
                )
                
                if current_time >= target_time and (
                    last_run is None or 
                    (current_time - last_run).days >= 7
                ):
                    return True
        
        return False
    
    def _run_scheduled_backup(self, name: str, schedule: dict):
        """运行调度备份"""
        print(f"🔄 执行调度备份: {name}")
        
        backup_engine = schedule["backup_engine"]
        db_manager = schedule["db_manager"]
        
        # 创建备份任务
        job_name = f"scheduled_{name}_{int(time.time())}"
        job = backup_engine.create_backup_job(job_name, db_manager)
        
        # 启动备份
        backup_engine.start_backup(job.id, db_manager)
        
        # 更新最后运行时间
        schedule["last_run"] = datetime.now()

def create_sample_database():
    """创建示例数据库"""
    # 创建SQLite数据库
    db_path = "sample.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_name TEXT,
            amount REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # 插入示例数据
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'John Doe', 'john@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Jane Smith', 'jane@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (3, 'Bob Johnson', 'bob@example.com')")
    
    cursor.execute("INSERT OR IGNORE INTO orders (id, user_id, product_name, amount, status) VALUES (1, 1, 'Laptop', 999.99, 'completed')")
    cursor.execute("INSERT OR IGNORE INTO orders (id, user_id, product_name, amount, status) VALUES (2, 1, 'Mouse', 29.99, 'completed')")
    cursor.execute("INSERT OR IGNORE INTO orders (id, user_id, product_name, amount, status) VALUES (3, 2, 'Keyboard', 79.99, 'pending')")
    
    conn.commit()
    conn.close()
    
    print("✅ 示例数据库创建完成")
    return db_path

async def demonstrate_backup():
    """演示备份功能"""
    print("\n💾 数据库备份演示")
    print("=" * 50)
    
    # 创建示例数据库
    db_path = create_sample_database()
    
    # 创建数据库配置
    db_config = DatabaseConfig(
        name="sample_db",
        type="sqlite",
        host="localhost",
        port=3306,
        username="user",
        password="password",
        database=db_path,
        backup_path="./backups"
    )
    
    # 创建备份配置
    backup_config = BackupConfig(
        backup_type=BackupType.FULL,
        compression=CompressionType.GZIP,
        backup_path="./backups",
        retention_days=30
    )
    
    # 创建数据库管理器
    db_manager = DatabaseManager(db_config)
    
    # 创建备份引擎
    backup_engine = BackupEngine(backup_config)
    
    # 创建备份任务
    job = backup_engine.create_backup_job("full_backup_001", db_manager)
    print(f"📝 创建备份任务: {job.name}")
    
    # 启动备份
    success = backup_engine.start_backup(job.id, db_manager)
    if success:
        print("✅ 备份任务启动成功")
        
        # 等待备份完成
        while job.status == BackupStatus.RUNNING:
            await asyncio.sleep(0.5)
        
        if job.status == BackupStatus.COMPLETED:
            print(f"✅ 备份完成: {job.file_size} bytes, {job.file_count} files")
        else:
            print(f"❌ 备份失败: {job.error_message}")
    else:
        print("❌ 备份任务启动失败")

async def demonstrate_recovery():
    """演示恢复功能"""
    print("\n🔄 数据库恢复演示")
    print("=" * 50)
    
    # 创建恢复引擎
    recovery_engine = RecoveryEngine("./backups")
    
    # 列出可用备份
    backups = recovery_engine.list_available_backups()
    
    if not backups:
        print("❌ 没有可用的备份")
        return
    
    print("📋 可用备份:")
    for i, backup in enumerate(backups):
        print(f"  {i+1}. {backup['backup_name']} ({backup['backup_type']})")
        print(f"     创建时间: {datetime.fromtimestamp(backup['completed_at'])}")
        print(f"     文件大小: {backup['file_size']} bytes")
    
    # 恢复最新的备份
    latest_backup = backups[0]
    
    # 创建数据库配置
    db_config = DatabaseConfig(
        name="sample_db",
        type="sqlite",
        host="localhost",
        port=3306,
        username="user",
        password="password",
        database="restored_sample.db",
        backup_path="./backups"
    )
    
    db_manager = DatabaseManager(db_config)
    
    # 执行恢复
    success = recovery_engine.restore_backup(latest_backup['backup_id'], db_manager)
    
    if success:
        print("✅ 数据库恢复成功")
    else:
        print("❌ 数据库恢复失败")

async def demonstrate_scheduled_backup():
    """演示调度备份"""
    print("\n⏰ 调度备份演示")
    print("=" * 50)
    
    # 创建备份配置
    backup_config = BackupConfig(
        backup_type=BackupType.FULL,
        compression=CompressionType.GZIP,
        backup_path="./backups",
        retention_days=30
    )
    
    # 创建数据库配置
    db_config = DatabaseConfig(
        name="sample_db",
        type="sqlite",
        host="localhost",
        port=3306,
        username="user",
        password="password",
        database="sample.db",
        backup_path="./backups"
    )
    
    # 创建备份引擎和数据库管理器
    backup_engine = BackupEngine(backup_config)
    db_manager = DatabaseManager(db_config)
    
    # 创建调度器
    scheduler = BackupScheduler()
    
    # 添加调度任务（每分钟运行一次用于演示）
    scheduler.add_schedule(
        name="daily_backup",
        backup_engine=backup_engine,
        db_manager=db_manager,
        schedule_type="daily",
        time_config={"hour": datetime.now().hour, "minute": datetime.now().minute + 1}
    )
    
    # 启动调度器
    scheduler.start_scheduler()
    
    # 运行2分钟进行演示
    print("⏰ 调度器运行中（2分钟演示）...")
    await asyncio.sleep(120)
    
    # 停止调度器
    scheduler.stop_scheduler()
    
    # 显示备份结果
    backups = backup_engine.list_backups()
    print(f"\n📊 调度备份结果: {len(backups)} 个备份")
    for backup in backups:
        print(f"  {backup.name}: {backup.status.value}")

async def main():
    """主函数"""
    print("💾 数据库备份与恢复演示")
    print("=" * 60)
    
    # 创建备份目录
    os.makedirs("./backups", exist_ok=True)
    
    try:
        await demonstrate_backup()
        await demonstrate_recovery()
        await demonstrate_scheduled_backup()
        
        print("\n✅ 备份恢复演示完成!")
        print("\n📚 关键概念:")
        print("  - 全量备份: 备份所有数据")
        print("  - 增量备份: 只备份变化的数据")
        print("  - 差异备份: 备份自上次全量备份以来的变化")
        print("  - 压缩备份: 减少备份文件大小")
        print("  - 调度备份: 自动定时备份")
        print("  - 数据恢复: 从备份恢复数据")
        print("  - 备份验证: 校验备份数据完整性")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被中断")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
    finally:
        # 清理临时文件
        if os.path.exists("sample.db"):
            os.remove("sample.db")
        if os.path.exists("restored_sample.db"):
            os.remove("restored_sample.db")

if __name__ == '__main__':
    asyncio.run(main())
