---
name: 备份与恢复
description: "当处理数据备份时，设计备份策略，实现自动备份，验证数据完整性。管理存储空间，制定恢复计划，和灾难恢复。"
license: MIT
---

# 备份与恢复技能

## 概述
数据备份是数据安全的核心保障。不当的备份策略会导致数据丢失、恢复困难、业务中断。需要完善的备份策略和恢复机制。

**核心原则**: 好的备份策略应该数据完整、恢复快速、操作简单、成本合理。坏的备份策略会备份不完整、恢复失败、操作复杂、成本过高。

## 何时使用

**始终:**
- 生产环境数据保护
- 开发环境数据安全
- 数据迁移前准备
- 系统升级前保障
- 灾难恢复预案
- 合规性要求

**触发短语:**
- "备份与恢复"
- "数据备份策略"
- "自动备份实现"
- "数据恢复方案"
- "灾难恢复计划"
- "备份验证测试"

## 备份恢复功能

### 备份策略
- 全量备份
- 增量备份
- 差异备份
- 实时备份
- 定时备份

### 存储管理
- 本地存储
- 云端存储
- 混合存储
- 压缩存储
- 加密存储

### 恢复机制
- 完整恢复
- 部分恢复
- 时间点恢复
- 紧急恢复
- 自动恢复

### 监控告警
- 备份状态监控
- 存储空间监控
- 恢复测试监控
- 异常告警通知
- 性能指标监控

## 常见备份恢复问题

### 备份不完整
```
问题:
备份数据不完整，恢复时缺少关键数据

错误示例:
- 备份范围不全面
- 备份频率过低
- 备份验证不充分
- 备份存储空间不足

解决方案:
1. 制定全面的备份策略
2. 增加备份频率
3. 实施备份验证机制
4. 扩展存储空间
```

### 恢复失败
```
问题:
数据恢复失败，无法正常恢复业务

错误示例:
- 备份数据损坏
- 恢复流程不正确
- 恢复环境不匹配
- 缺少恢复测试

解决方案:
1. 定期验证备份完整性
2. 标准化恢复流程
3. 保持环境一致性
4. 定期进行恢复演练
```

### 性能问题
```
问题:
备份恢复性能差，影响业务正常运行

错误示例:
- 备份时间过长
- 恢复时间过长
- 占用系统资源过多
- 网络带宽不足

解决方案:
1. 优化备份策略
2. 使用增量备份
3. 合理安排备份时间
4. 优化网络配置
```

### 存储成本高
```
问题:
备份存储成本过高，超出预算

错误示例:
- 存储冗余过多
- 未使用压缩
- 存储层级不合理
- 数据保留策略不当

解决方案:
1. 实施存储分层
2. 使用数据压缩
3. 制定保留策略
4. 优化存储配置
```

## 代码实现示例

### 备份管理器
```python
import os
import json
import time
import hashlib
import zipfile
import shutil
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class BackupType(Enum):
    """备份类型"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class StorageType(Enum):
    """存储类型"""
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"

class CompressionType(Enum):
    """压缩类型"""
    NONE = "none"
    ZIP = "zip"
    GZIP = "gzip"
    TAR = "tar"

@dataclass
class BackupConfig:
    """备份配置"""
    name: str
    source_path: str
    backup_type: BackupType
    storage_type: StorageType
    compression: CompressionType
    encryption: bool
    schedule: str
    retention_days: int
    max_backups: int

@dataclass
class BackupResult:
    """备份结果"""
    success: bool
    backup_id: str
    backup_type: BackupType
    file_count: int
    total_size: int
    compressed_size: int
    duration: float
    timestamp: datetime
    errors: List[str]

@dataclass
class RecoveryResult:
    """恢复结果"""
    success: bool
    backup_id: str
    recovered_files: List[str]
    failed_files: List[str]
    total_size: int
    duration: float
    timestamp: datetime
    errors: List[str]

class BackupManager:
    def __init__(self, config_dir: str = "./backup_configs"):
        self.config_dir = config_dir
        self.backup_history: List[BackupResult] = []
        self.storage_managers = {}
        self.encryption_key = None
        
    def create_backup_config(self, config: BackupConfig) -> bool:
        """创建备份配置"""
        try:
            config_file = os.path.join(self.config_dir, f"{config.name}.json")
            
            config_data = {
                'name': config.name,
                'source_path': config.source_path,
                'backup_type': config.backup_type.value,
                'storage_type': config.storage_type.value,
                'compression': config.compression.value,
                'encryption': config.encryption,
                'schedule': config.schedule,
                'retention_days': config.retention_days,
                'max_backups': config.max_backups
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"创建备份配置失败: {e}")
            return False
    
    def perform_backup(self, config_name: str) -> BackupResult:
        """执行备份"""
        config = self._load_backup_config(config_name)
        if not config:
            return BackupResult(
                success=False,
                backup_id="",
                backup_type=BackupType.FULL,
                file_count=0,
                total_size=0,
                compressed_size=0,
                duration=0,
                timestamp=datetime.now(),
                errors=["配置文件不存在"]
            )
        
        start_time = time.time()
        backup_id = self._generate_backup_id(config_name)
        
        try:
            # 创建备份目录
            backup_dir = self._create_backup_directory(config_name, backup_id)
            
            # 执行备份
            if config.backup_type == BackupType.FULL:
                result = self._perform_full_backup(config, backup_dir, backup_id)
            elif config.backup_type == BackupType.INCREMENTAL:
                result = self._perform_incremental_backup(config, backup_dir, backup_id)
            elif config.backup_type == BackupType.DIFFERENTIAL:
                result = self._perform_differential_backup(config, backup_dir, backup_id)
            else:
                raise ValueError(f"不支持的备份类型: {config.backup_type}")
            
            # 压缩备份
            if config.compression != CompressionType.NONE:
                result = self._compress_backup(result, config.compression)
            
            # 加密备份
            if config.encryption:
                result = self._encrypt_backup(result)
            
            # 存储备份
            storage_manager = self._get_storage_manager(config.storage_type)
            stored_success = storage_manager.store_backup(backup_dir, backup_id)
            
            if not stored_success:
                result.success = False
                result.errors.append("存储备份失败")
            
            # 记录备份历史
            result.duration = time.time() - start_time
            self.backup_history.append(result)
            
            # 清理过期备份
            self._cleanup_old_backups(config)
            
            return result
            
        except Exception as e:
            return BackupResult(
                success=False,
                backup_id=backup_id,
                backup_type=config.backup_type,
                file_count=0,
                total_size=0,
                compressed_size=0,
                duration=time.time() - start_time,
                timestamp=datetime.now(),
                errors=[str(e)]
            )
    
    def _perform_full_backup(self, config: BackupConfig, backup_dir: str, backup_id: str) -> BackupResult:
        """执行全量备份"""
        file_count = 0
        total_size = 0
        errors = []
        
        try:
            for root, dirs, files in os.walk(config.source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    relative_path = os.path.relpath(source_file, config.source_path)
                    backup_file = os.path.join(backup_dir, relative_path)
                    
                    # 创建目标目录
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    
                    try:
                        # 复制文件
                        shutil.copy2(source_file, backup_file)
                        file_count += 1
                        total_size += os.path.getsize(source_file)
                    except Exception as e:
                        errors.append(f"复制文件失败 {source_file}: {e}")
            
            return BackupResult(
                success=len(errors) == 0,
                backup_id=backup_id,
                backup_type=BackupType.FULL,
                file_count=file_count,
                total_size=total_size,
                compressed_size=total_size,
                duration=0,
                timestamp=datetime.now(),
                errors=errors
            )
            
        except Exception as e:
            return BackupResult(
                success=False,
                backup_id=backup_id,
                backup_type=BackupType.FULL,
                file_count=file_count,
                total_size=total_size,
                compressed_size=total_size,
                duration=0,
                timestamp=datetime.now(),
                errors=[str(e)]
            )
    
    def _perform_incremental_backup(self, config: BackupConfig, backup_dir: str, backup_id: str) -> BackupResult:
        """执行增量备份"""
        # 获取上次备份时间
        last_backup_time = self._get_last_backup_time(config.name)
        
        file_count = 0
        total_size = 0
        errors = []
        
        try:
            for root, dirs, files in os.walk(config.source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    
                    # 检查文件修改时间
                    file_mtime = os.path.getmtime(source_file)
                    if file_mtime <= last_backup_time:
                        continue
                    
                    relative_path = os.path.relpath(source_file, config.source_path)
                    backup_file = os.path.join(backup_dir, relative_path)
                    
                    # 创建目标目录
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    
                    try:
                        # 复制文件
                        shutil.copy2(source_file, backup_file)
                        file_count += 1
                        total_size += os.path.getsize(source_file)
                    except Exception as e:
                        errors.append(f"复制文件失败 {source_file}: {e}")
            
            return BackupResult(
                success=len(errors) == 0,
                backup_id=backup_id,
                backup_type=BackupType.INCREMENTAL,
                file_count=file_count,
                total_size=total_size,
                compressed_size=total_size,
                duration=0,
                timestamp=datetime.now(),
                errors=errors
            )
            
        except Exception as e:
            return BackupResult(
                success=False,
                backup_id=backup_id,
                backup_type=BackupType.INCREMENTAL,
                file_count=file_count,
                total_size=total_size,
                compressed_size=total_size,
                duration=0,
                timestamp=datetime.now(),
                errors=[str(e)]
            )
    
    def _perform_differential_backup(self, config: BackupConfig, backup_dir: str, backup_id: str) -> BackupResult:
        """执行差异备份"""
        # 获取上次全量备份时间
        last_full_backup_time = self._get_last_full_backup_time(config.name)
        
        file_count = 0
        total_size = 0
        errors = []
        
        try:
            for root, dirs, files in os.walk(config.source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    
                    # 检查文件修改时间
                    file_mtime = os.path.getmtime(source_file)
                    if file_mtime <= last_full_backup_time:
                        continue
                    
                    relative_path = os.path.relpath(source_file, config.source_path)
                    backup_file = os.path.join(backup_dir, relative_path)
                    
                    # 创建目标目录
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    
                    try:
                        # 复制文件
                        shutil.copy2(source_file, backup_file)
                        file_count += 1
                        total_size += os.path.getsize(source_file)
                    except Exception as e:
                        errors.append(f"复制文件失败 {source_file}: {e}")
            
            return BackupResult(
                success=len(errors) == 0,
                backup_id=backup_id,
                backup_type=BackupType.DIFFERENTIAL,
                file_count=file_count,
                total_size=total_size,
                compressed_size=total_size,
                duration=0,
                timestamp=datetime.now(),
                errors=errors
            )
            
        except Exception as e:
            return BackupResult(
                success=False,
                backup_id=backup_id,
                backup_type=BackupType.DIFFERENTIAL,
                file_count=file_count,
                total_size=total_size,
                compressed_size=total_size,
                duration=0,
                timestamp=datetime.now(),
                errors=[str(e)]
            )
    
    def recover_data(self, backup_id: str, target_path: str) -> RecoveryResult:
        """恢复数据"""
        start_time = time.time()
        
        try:
            # 查找备份记录
            backup_record = self._find_backup_record(backup_id)
            if not backup_record:
                return RecoveryResult(
                    success=False,
                    backup_id=backup_id,
                    recovered_files=[],
                    failed_files=[],
                    total_size=0,
                    duration=0,
                    timestamp=datetime.now(),
                    errors=["备份记录不存在"]
                )
            
            # 获取存储管理器
            storage_manager = self._get_storage_manager_for_backup(backup_id)
            
            # 下载备份
            temp_backup_dir = f"./temp_recovery_{backup_id}"
            download_success = storage_manager.download_backup(backup_id, temp_backup_dir)
            
            if not download_success:
                return RecoveryResult(
                    success=False,
                    backup_id=backup_id,
                    recovered_files=[],
                    failed_files=[],
                    total_size=0,
                    duration=0,
                    timestamp=datetime.now(),
                    errors=["下载备份失败"]
                )
            
            # 解压缩备份
            if backup_record.compressed_size < backup_record.total_size:
                temp_backup_dir = self._decompress_backup(temp_backup_dir)
            
            # 解密备份
            if backup_record.errors and "加密" in str(backup_record.errors):
                temp_backup_dir = self._decrypt_backup(temp_backup_dir)
            
            # 恢复文件
            recovered_files = []
            failed_files = []
            total_size = 0
            
            for root, dirs, files in os.walk(temp_backup_dir):
                for file in files:
                    source_file = os.path.join(root, file)
                    relative_path = os.path.relpath(source_file, temp_backup_dir)
                    target_file = os.path.join(target_path, relative_path)
                    
                    # 创建目标目录
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    try:
                        # 复制文件
                        shutil.copy2(source_file, target_file)
                        recovered_files.append(relative_path)
                        total_size += os.path.getsize(source_file)
                    except Exception as e:
                        failed_files.append(f"{relative_path}: {e}")
            
            # 清理临时文件
            shutil.rmtree(temp_backup_dir, ignore_errors=True)
            
            return RecoveryResult(
                success=len(failed_files) == 0,
                backup_id=backup_id,
                recovered_files=recovered_files,
                failed_files=failed_files,
                total_size=total_size,
                duration=time.time() - start_time,
                timestamp=datetime.now(),
                errors=failed_files
            )
            
        except Exception as e:
            return RecoveryResult(
                success=False,
                backup_id=backup_id,
                recovered_files=[],
                failed_files=[],
                total_size=0,
                duration=time.time() - start_time,
                timestamp=datetime.now(),
                errors=[str(e)]
            )
    
    def verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """验证备份完整性"""
        try:
            backup_record = self._find_backup_record(backup_id)
            if not backup_record:
                return {
                    'valid': False,
                    'errors': ['备份记录不存在']
                }
            
            # 计算备份文件哈希
            storage_manager = self._get_storage_manager_for_backup(backup_id)
            temp_dir = f"./temp_verify_{backup_id}"
            
            download_success = storage_manager.download_backup(backup_id, temp_dir)
            if not download_success:
                return {
                    'valid': False,
                    'errors': ['下载备份失败']
                }
            
            # 计算文件哈希
            file_hashes = {}
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, temp_dir)
                    
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_hashes[relative_path] = file_hash
            
            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                'valid': True,
                'file_count': len(file_hashes),
                'file_hashes': file_hashes,
                'backup_record': backup_record
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [str(e)]
            }
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """获取备份统计信息"""
        if not self.backup_history:
            return {
                'total_backups': 0,
                'successful_backups': 0,
                'failed_backups': 0,
                'total_size': 0,
                'average_duration': 0,
                'backup_types': {}
            }
        
        successful_backups = [b for b in self.backup_history if b.success]
        failed_backups = [b for b in self.backup_history if not b.success]
        
        total_size = sum(b.total_size for b in successful_backups)
        total_duration = sum(b.duration for b in successful_backups)
        
        backup_types = {}
        for backup in self.backup_history:
            backup_type = backup.backup_type.value
            backup_types[backup_type] = backup_types.get(backup_type, 0) + 1
        
        return {
            'total_backups': len(self.backup_history),
            'successful_backups': len(successful_backups),
            'failed_backups': len(failed_backups),
            'total_size': total_size,
            'average_duration': total_duration / len(successful_backups) if successful_backups else 0,
            'backup_types': backup_types,
            'latest_backup': self.backup_history[-1] if self.backup_history else None
        }
    
    def _load_backup_config(self, config_name: str) -> Optional[BackupConfig]:
        """加载备份配置"""
        config_file = os.path.join(self.config_dir, f"{config_name}.json")
        
        if not os.path.exists(config_file):
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return BackupConfig(
                name=config_data['name'],
                source_path=config_data['source_path'],
                backup_type=BackupType(config_data['backup_type']),
                storage_type=StorageType(config_data['storage_type']),
                compression=CompressionType(config_data['compression']),
                encryption=config_data['encryption'],
                schedule=config_data['schedule'],
                retention_days=config_data['retention_days'],
                max_backups=config_data['max_backups']
            )
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None
    
    def _generate_backup_id(self, config_name: str) -> str:
        """生成备份ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{config_name}_{timestamp}"
    
    def _create_backup_directory(self, config_name: str, backup_id: str) -> str:
        """创建备份目录"""
        backup_dir = os.path.join("./backups", config_name, backup_id)
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def _get_last_backup_time(self, config_name: str) -> float:
        """获取上次备份时间"""
        config_backups = [b for b in self.backup_history if b.backup_id.startswith(config_name)]
        if not config_backups:
            return 0
        
        latest_backup = max(config_backups, key=lambda b: b.timestamp)
        return latest_backup.timestamp.timestamp()
    
    def _get_last_full_backup_time(self, config_name: str) -> float:
        """获取上次全量备份时间"""
        config_backups = [
            b for b in self.backup_history 
            if b.backup_id.startswith(config_name) and b.backup_type == BackupType.FULL
        ]
        if not config_backups:
            return 0
        
        latest_backup = max(config_backups, key=lambda b: b.timestamp)
        return latest_backup.timestamp.timestamp()
    
    def _find_backup_record(self, backup_id: str) -> Optional[BackupResult]:
        """查找备份记录"""
        for backup in self.backup_history:
            if backup.backup_id == backup_id:
                return backup
        return None
    
    def _get_storage_manager(self, storage_type: StorageType):
        """获取存储管理器"""
        if storage_type not in self.storage_managers:
            if storage_type == StorageType.LOCAL:
                self.storage_managers[storage_type] = LocalStorageManager()
            elif storage_type == StorageType.CLOUD:
                self.storage_managers[storage_type] = CloudStorageManager()
            elif storage_type == StorageType.HYBRID:
                self.storage_managers[storage_type] = HybridStorageManager()
        
        return self.storage_managers[storage_type]
    
    def _get_storage_manager_for_backup(self, backup_id: str):
        """获取备份的存储管理器"""
        backup_record = self._find_backup_record(backup_id)
        if backup_record:
            # 简化实现，实际应该从配置中获取
            return self._get_storage_manager(StorageType.LOCAL)
        return None
    
    def _cleanup_old_backups(self, config: BackupConfig):
        """清理过期备份"""
        config_backups = [b for b in self.backup_history if b.backup_id.startswith(config.name)]
        
        # 按时间排序
        config_backups.sort(key=lambda b: b.timestamp, reverse=True)
        
        # 保留最新的max_backups个备份
        if len(config_backups) > config.max_backups:
            old_backups = config_backups[config.max_backups:]
            for old_backup in old_backups:
                # 删除备份文件
                storage_manager = self._get_storage_manager_for_backup(old_backup.backup_id)
                if storage_manager:
                    storage_manager.delete_backup(old_backup.backup_id)
                
                # 从历史记录中移除
                self.backup_history.remove(old_backup)

# 存储管理器
class LocalStorageManager:
    def __init__(self, storage_path: str = "./local_storage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def store_backup(self, backup_dir: str, backup_id: str) -> bool:
        """存储备份"""
        try:
            target_dir = os.path.join(self.storage_path, backup_id)
            shutil.copytree(backup_dir, target_dir)
            return True
        except Exception as e:
            print(f"存储备份失败: {e}")
            return False
    
    def download_backup(self, backup_id: str, target_dir: str) -> bool:
        """下载备份"""
        try:
            source_dir = os.path.join(self.storage_path, backup_id)
            if not os.path.exists(source_dir):
                return False
            
            shutil.copytree(source_dir, target_dir)
            return True
        except Exception as e:
            print(f"下载备份失败: {e}")
            return False
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        try:
            backup_dir = os.path.join(self.storage_path, backup_id)
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            return True
        except Exception as e:
            print(f"删除备份失败: {e}")
            return False

class CloudStorageManager:
    def __init__(self):
        # 简化实现，实际应该集成云存储API
        pass
    
    def store_backup(self, backup_dir: str, backup_id: str) -> bool:
        """存储备份到云端"""
        # 简化实现
        print(f"上传备份到云端: {backup_id}")
        return True
    
    def download_backup(self, backup_id: str, target_dir: str) -> bool:
        """从云端下载备份"""
        # 简化实现
        print(f"从云端下载备份: {backup_id}")
        return True
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除云端备份"""
        # 简化实现
        print(f"删除云端备份: {backup_id}")
        return True

class HybridStorageManager:
    def __init__(self):
        self.local_manager = LocalStorageManager()
        self.cloud_manager = CloudStorageManager()
    
    def store_backup(self, backup_dir: str, backup_id: str) -> bool:
        """混合存储备份"""
        # 本地存储
        local_success = self.local_manager.store_backup(backup_dir, backup_id)
        # 云端存储
        cloud_success = self.cloud_manager.store_backup(backup_dir, backup_id)
        
        return local_success and cloud_success
    
    def download_backup(self, backup_id: str, target_dir: str) -> bool:
        """从混合存储下载备份"""
        # 优先从本地下载
        if self.local_manager.download_backup(backup_id, target_dir):
            return True
        
        # 从云端下载
        return self.cloud_manager.download_backup(backup_id, target_dir)
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除混合存储备份"""
        local_success = self.local_manager.delete_backup(backup_id)
        cloud_success = self.cloud_manager.delete_backup(backup_id)
        
        return local_success and cloud_success

# 使用示例
def main():
    print("=== 备份管理器 ===")
    
    # 创建备份管理器
    backup_manager = BackupManager()
    
    # 创建备份配置
    backup_config = BackupConfig(
        name="database_backup",
        source_path="./data",
        backup_type=BackupType.FULL,
        storage_type=StorageType.LOCAL,
        compression=CompressionType.ZIP,
        encryption=False,
        schedule="0 2 * * *",  # 每天凌晨2点
        retention_days=30,
        max_backups=7
    )
    
    # 保存配置
    config_success = backup_manager.create_backup_config(backup_config)
    print(f"创建备份配置: {'成功' if config_success else '失败'}")
    
    # 执行备份
    print("\n执行备份:")
    backup_result = backup_manager.perform_backup("database_backup")
    
    print(f"备份结果: {'成功' if backup_result.success else '失败'}")
    print(f"备份ID: {backup_result.backup_id}")
    print(f"备份类型: {backup_result.backup_type.value}")
    print(f"文件数量: {backup_result.file_count}")
    print(f"总大小: {backup_result.total_size} bytes")
    print(f"压缩大小: {backup_result.compressed_size} bytes")
    print(f"耗时: {backup_result.duration:.2f} 秒")
    
    if backup_result.errors:
        print("错误信息:")
        for error in backup_result.errors:
            print(f"- {error}")
    
    # 验证备份
    print("\n验证备份:")
    verification = backup_manager.verify_backup(backup_result.backup_id)
    print(f"备份完整性: {'有效' if verification['valid'] else '无效'}")
    
    if verification['valid']:
        print(f"文件数量: {verification['file_count']}")
    
    if 'errors' in verification:
        print("验证错误:")
        for error in verification['errors']:
            print(f"- {error}")
    
    # 恢复数据
    print("\n恢复数据:")
    recovery_result = backup_manager.recover_data(backup_result.backup_id, "./recovered_data")
    
    print(f"恢复结果: {'成功' if recovery_result.success else '失败'}")
    print(f"恢复文件数: {len(recovery_result.recovered_files)}")
    print(f"失败文件数: {len(recovery_result.failed_files)}")
    print(f"总大小: {recovery_result.total_size} bytes")
    print(f"耗时: {recovery_result.duration:.2f} 秒")
    
    if recovery_result.failed_files:
        print("失败文件:")
        for failed_file in recovery_result.failed_files:
            print(f"- {failed_file}")
    
    # 获取统计信息
    print("\n备份统计:")
    stats = backup_manager.get_backup_statistics()
    
    print(f"总备份数: {stats['total_backups']}")
    print(f"成功备份数: {stats['successful_backups']}")
    print(f"失败备份数: {stats['failed_backups']}")
    print(f"总大小: {stats['total_size']} bytes")
    print(f"平均耗时: {stats['average_duration']:.2f} 秒")
    
    print("备份类型统计:")
    for backup_type, count in stats['backup_types'].items():
        print(f"- {backup_type}: {count}")

if __name__ == '__main__':
    main()
```

### 备份调度器
```python
import schedule
import threading
import time
from typing import Dict, Any, List
from datetime import datetime

class BackupScheduler:
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.scheduled_jobs = {}
        self.running = False
        self.scheduler_thread = None
    
    def schedule_backup(self, config_name: str, cron_expression: str) -> bool:
        """调度备份任务"""
        try:
            # 解析cron表达式
            schedule_parts = cron_expression.split()
            if len(schedule_parts) != 5:
                raise ValueError("无效的cron表达式")
            
            minute, hour, day, month, weekday = schedule_parts
            
            # 创建调度任务
            job = None
            
            if minute == '*' and hour == '*' and day == '*' and month == '*' and weekday == '*':
                # 每分钟执行
                job = schedule.every().minute.do(self._run_backup, config_name)
            elif minute != '*' and hour == '*' and day == '*' and month == '*' and weekday == '*':
                # 每小时特定分钟执行
                job = schedule.every().hour.at(f":{minute}").do(self._run_backup, config_name)
            elif minute != '*' and hour != '*' and day == '*' and month == '*' and weekday == '*':
                # 每天特定时间执行
                job = schedule.every().day.at(f"{hour}:{minute}").do(self._run_backup, config_name)
            elif minute != '*' and hour != '*' and day != '*' and month == '*' and weekday == '*':
                # 每月特定日期和时间执行
                job = schedule.every().month.at(f"{hour}:{minute}").do(self._run_backup, config_name)
            else:
                # 自定义cron表达式
                job = schedule.every().day.at(f"{hour}:{minute}").do(self._run_backup, config_name)
            
            self.scheduled_jobs[config_name] = job
            return True
            
        except Exception as e:
            print(f"调度备份失败: {e}")
            return False
    
    def _run_backup(self, config_name: str):
        """运行备份任务"""
        print(f"开始执行调度备份: {config_name}")
        
        backup_result = self.backup_manager.perform_backup(config_name)
        
        if backup_result.success:
            print(f"调度备份成功: {config_name}, 备份ID: {backup_result.backup_id}")
        else:
            print(f"调度备份失败: {config_name}")
            for error in backup_result.errors:
                print(f"  错误: {error}")
    
    def start_scheduler(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        print("备份调度器已启动")
    
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("备份调度器已停止")
    
    def _run_scheduler(self):
        """运行调度器循环"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """获取已调度任务"""
        jobs = []
        for config_name, job in self.scheduled_jobs.items():
            jobs.append({
                'config_name': config_name,
                'next_run': job.next_run,
                'job': str(job)
            })
        return jobs

# 使用示例
def main():
    print("=== 备份调度器 ===")
    
    # 创建备份管理器和调度器
    backup_manager = BackupManager()
    scheduler = BackupScheduler(backup_manager)
    
    # 创建备份配置
    backup_config = BackupConfig(
        name="scheduled_backup",
        source_path="./data",
        backup_type=BackupType.INCREMENTAL,
        storage_type=StorageType.LOCAL,
        compression=CompressionType.GZIP,
        encryption=False,
        schedule="0 */6 * * *",  # 每6小时执行一次
        retention_days=7,
        max_backups=28
    )
    
    backup_manager.create_backup_config(backup_config)
    
    # 调度备份任务
    schedule_success = scheduler.schedule_backup("scheduled_backup", "*/1 * * * *")  # 每分钟执行（演示用）
    print(f"调度备份任务: {'成功' if schedule_success else '失败'}")
    
    # 启动调度器
    scheduler.start_scheduler()
    
    # 运行一段时间观察调度效果
    print("调度器运行中，等待备份任务执行...")
    time.sleep(65)  # 等待65秒，应该执行一次备份
    
    # 查看已调度任务
    scheduled_jobs = scheduler.get_scheduled_jobs()
    print("\n已调度任务:")
    for job in scheduled_jobs:
        print(f"- {job['config_name']}: {job['job']}")
    
    # 停止调度器
    scheduler.stop_scheduler()
    
    # 查看备份统计
    stats = backup_manager.get_backup_statistics()
    print(f"\n总备份数: {stats['total_backups']}")

if __name__ == '__main__':
    main()
```

## 备份恢复最佳实践

### 备份策略设计
1. **3-2-1原则**: 3份副本，2种不同介质，1份异地存储
2. **分层备份**: 全量、增量、差异备份结合使用
3. **定期验证**: 定期测试备份完整性和可恢复性
4. **自动化**: 实现自动备份和监控告警
5. **文档化**: 详细记录备份策略和恢复流程

### 存储优化
1. **压缩存储**: 使用压缩算法减少存储空间
2. **去重技术**: 消除重复数据节省空间
3. **分层存储**: 热数据本地存储，冷数据云端存储
4. **加密保护**: 敏感数据加密存储
5. **生命周期管理**: 自动清理过期备份

### 恢复策略
1. **RTO/RPO**: 明确恢复时间和恢复点目标
2. **优先级**: 重要数据优先恢复
3. **测试演练**: 定期进行恢复演练
4. **快速恢复**: 准备快速恢复方案
5. **灾难恢复**: 制定完整的灾难恢复计划

### 监控告警
1. **状态监控**: 实时监控备份状态
2. **容量监控**: 监控存储空间使用情况
3. **性能监控**: 监控备份恢复性能
4. **异常告警**: 及时发现和报告异常
5. **报表分析**: 定期生成备份分析报表

## 相关技能

- **sql-optimization** - SQL优化
- **migration-validator** - 迁移验证
- **transaction-management** - 事务管理
- **nosql-databases** - NoSQL数据库
