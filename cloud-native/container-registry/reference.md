# 容器镜像仓库参考文档

## 容器镜像仓库概述

### 什么是容器镜像仓库
容器镜像仓库是一个专门用于存储、管理和分发容器镜像的 centralized 系统。它提供了镜像的版本控制、访问控制、安全扫描、性能优化等功能，是容器化应用生命周期管理的重要组成部分。容器镜像仓库支持Docker、OCI等标准格式，能够与CI/CD流水线、容器编排平台等工具无缝集成。

### 主要功能
- **镜像存储**: 提供高效的镜像存储和检索服务，支持分层存储和压缩优化
- **访问控制**: 实现基于角色的访问控制(RBAC)，支持多种认证方式
- **安全扫描**: 集成安全扫描工具，自动检测镜像中的安全漏洞
- **镜像签名**: 支持镜像签名和验证，确保镜像的完整性和来源可信
- **性能优化**: 提供缓存、CDN、负载均衡等性能优化功能
- **监控告警**: 提供全面的监控指标和告警机制
- **备份恢复**: 支持镜像数据的备份和恢复，确保数据安全

## 容器镜像仓库核心

### 镜像仓库引擎
```python
# container_registry.py
import json
import yaml
import os
import time
import uuid
import logging
import threading
import queue
import hashlib
import shutil
import gzip
import requests
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import statistics
import sqlite3
import redis
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import docker
import trivy

class RegistryType(Enum):
    """仓库类型枚举"""
    DOCKER_HUB = "docker_hub"
    HARBOR = "harbor"
    NEXUS = "nexus"
    GITLAB = "gitlab"
    AWS_ECR = "aws_ecr"
    GOOGLE_GCR = "google_gcr"
    AZURE_ACR = "azure_acr"
    CUSTOM = "custom"

class ImageFormat(Enum):
    """镜像格式枚举"""
    DOCKER = "docker"
    OCI = "oci"
    MIXED = "mixed"

class ScanStatus(Enum):
    """扫描状态枚举"""
    PENDING = "pending"
    SCANNING = "scanning"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Repository:
    """仓库"""
    repo_id: str
    name: str
    description: str
    namespace: str
    visibility: str  # public, private
    created_at: datetime
    updated_at: datetime
    tags_count: int = 0
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImageTag:
    """镜像标签"""
    tag_id: str
    repo_id: str
    tag_name: str
    digest: str
    size_bytes: int
    created_at: datetime
    pushed_at: datetime
    pulled_count: int = 0
    scan_status: ScanStatus = ScanStatus.PENDING
    signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImageLayer:
    """镜像层"""
    layer_id: str
    tag_id: str
    digest: str
    size_bytes: int
    command: str
    created_at: datetime
    compressed_size: int = 0
    media_type: str = "application/vnd.docker.image.rootfs.diff.tar.gzip"

@dataclass
class SecurityVulnerability:
    """安全漏洞"""
    vuln_id: str
    tag_id: str
    cve_id: str
    severity: str  # Critical, High, Medium, Low
    title: str
    description: str
    package_name: str
    installed_version: str
    fixed_version: Optional[str]
    references: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.now)

@dataclass
class RegistryUser:
    """仓库用户"""
    user_id: str
    username: str
    email: str
    role: str  # admin, developer, guest
    permissions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    active: bool = True

@dataclass
class AccessLog:
    """访问日志"""
    log_id: str
    user_id: Optional[str]
    repo_id: str
    tag_name: str
    action: str  # push, pull, delete
    ip_address: str
    user_agent: str
    timestamp: datetime
    status_code: int
    size_bytes: int = 0
    duration_ms: int = 0

class ImageStorage:
    """镜像存储管理器"""
    
    def __init__(self, storage_path: str, compression: str = "gzip"):
        self.storage_path = storage_path
        self.compression = compression
        self.logger = logging.getLogger(__name__)
        self._ensure_storage_path()
    
    def _ensure_storage_path(self):
        """确保存储路径存在"""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "blobs"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "repositories"), exist_ok=True)
    
    def store_image_layer(self, layer: ImageLayer, data: bytes) -> str:
        """存储镜像层"""
        try:
            # 压缩数据
            if self.compression == "gzip":
                compressed_data = gzip.compress(data)
            else:
                compressed_data = data
            
            # 计算摘要
            digest = hashlib.sha256(compressed_data).hexdigest()
            
            # 存储到文件系统
            blob_path = os.path.join(self.storage_path, "blobs", digest[:2], digest)
            os.makedirs(os.path.dirname(blob_path), exist_ok=True)
            
            with open(blob_path, 'wb') as f:
                f.write(compressed_data)
            
            # 更新层信息
            layer.compressed_size = len(compressed_data)
            
            self.logger.info(f"存储镜像层: {layer.layer_id}, 大小: {len(compressed_data)} 字节")
            return digest
        
        except Exception as e:
            self.logger.error(f"存储镜像层失败: {e}")
            raise
    
    def retrieve_image_layer(self, digest: str) -> bytes:
        """检索镜像层"""
        try:
            blob_path = os.path.join(self.storage_path, "blobs", digest[:2], digest)
            
            if not os.path.exists(blob_path):
                raise FileNotFoundError(f"镜像层不存在: {digest}")
            
            with open(blob_path, 'rb') as f:
                compressed_data = f.read()
            
            # 解压缩
            if self.compression == "gzip":
                data = gzip.decompress(compressed_data)
            else:
                data = compressed_data
            
            return data
        
        except Exception as e:
            self.logger.error(f"检索镜像层失败: {e}")
            raise
    
    def delete_image_layer(self, digest: str) -> bool:
        """删除镜像层"""
        try:
            blob_path = os.path.join(self.storage_path, "blobs", digest[:2], digest)
            
            if os.path.exists(blob_path):
                os.remove(blob_path)
                self.logger.info(f"删除镜像层: {digest}")
                return True
            else:
                self.logger.warning(f"镜像层不存在: {digest}")
                return False
        
        except Exception as e:
            self.logger.error(f"删除镜像层失败: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计"""
        try:
            total_size = 0
            layer_count = 0
            
            for root, dirs, files in os.walk(os.path.join(self.storage_path, "blobs")):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    layer_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'layer_count': layer_count,
                'compression': self.compression
            }
        
        except Exception as e:
            self.logger.error(f"获取存储统计失败: {e}")
            return {}

class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self, scanner_type: str = "trivy"):
        self.scanner_type = scanner_type
        self.logger = logging.getLogger(__name__)
        self.scan_queue = queue.Queue()
        self.scan_results = {}
        self.scanning = False
        self.scan_thread = None
    
    def start_scanner(self):
        """启动扫描器"""
        self.scanning = True
        self.scan_thread = threading.Thread(target=self._scan_worker)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        self.logger.info("安全扫描器已启动")
    
    def stop_scanner(self):
        """停止扫描器"""
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join()
        self.logger.info("安全扫描器已停止")
    
    def queue_scan(self, tag: ImageTag):
        """队列扫描任务"""
        self.scan_queue.put(tag)
        self.logger.info(f"队列扫描任务: {tag.tag_name}")
    
    def _scan_worker(self):
        """扫描工作线程"""
        while self.scanning:
            try:
                if not self.scan_queue.empty():
                    tag = self.scan_queue.get()
                    self._scan_image(tag)
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"扫描工作线程错误: {e}")
    
    def _scan_image(self, tag: ImageTag) -> List[SecurityVulnerability]:
        """扫描镜像"""
        vulnerabilities = []
        
        try:
            # 更新扫描状态
            tag.scan_status = ScanStatus.SCANNING
            
            if self.scanner_type == "trivy":
                vulnerabilities = self._scan_with_trivy(tag)
            elif self.scanner_type == "clair":
                vulnerabilities = self._scan_with_clair(tag)
            elif self.scanner_type == "grype":
                vulnerabilities = self._scan_with_grype(tag)
            
            # 更新扫描结果
            tag.scan_status = ScanStatus.COMPLETED
            self.scan_results[tag.tag_id] = vulnerabilities
            
            self.logger.info(f"扫描完成: {tag.tag_name}, 发现 {len(vulnerabilities)} 个漏洞")
            
        except Exception as e:
            self.logger.error(f"扫描镜像失败: {e}")
            tag.scan_status = ScanStatus.FAILED
        
        return vulnerabilities
    
    def _scan_with_trivy(self, tag: ImageTag) -> List[SecurityVulnerability]:
        """使用Trivy扫描"""
        vulnerabilities = []
        
        try:
            # 构建Trivy命令
            cmd = [
                "trivy", "image",
                "--format", "json",
                "--quiet",
                f"{tag.repo_id}:{tag.tag_name}"
            ]
            
            # 执行扫描
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                scan_data = json.loads(result.stdout)
                
                for result in scan_data.get('Results', []):
                    for vuln in result.get('Vulnerabilities', []):
                        vulnerability = SecurityVulnerability(
                            vuln_id=str(uuid.uuid4()),
                            tag_id=tag.tag_id,
                            cve_id=vuln.get('VulnerabilityID', ''),
                            severity=vuln.get('Severity', 'Unknown'),
                            title=vuln.get('Title', ''),
                            description=vuln.get('Description', ''),
                            package_name=vuln.get('PkgName', ''),
                            installed_version=vuln.get('InstalledVersion', ''),
                            fixed_version=vuln.get('FixedVersion'),
                            references=vuln.get('References', [])
                        )
                        vulnerabilities.append(vulnerability)
        
        except Exception as e:
            self.logger.error(f"Trivy扫描失败: {e}")
        
        return vulnerabilities
    
    def _scan_with_clair(self, tag: ImageTag) -> List[SecurityVulnerability]:
        """使用Clair扫描"""
        # 简化实现
        return []
    
    def _scan_with_grype(self, tag: ImageTag) -> List[SecurityVulnerability]:
        """使用Grype扫描"""
        # 简化实现
        return []
    
    def get_scan_results(self, tag_id: str) -> List[SecurityVulnerability]:
        """获取扫描结果"""
        return self.scan_results.get(tag_id, [])

class ImageSigner:
    """镜像签名器"""
    
    def __init__(self, key_pair_path: str = None):
        self.key_pair_path = key_pair_path
        self.logger = logging.getLogger(__name__)
        self.private_key = None
        self.public_key = None
        
        if key_pair_path:
            self._load_keys()
    
    def _load_keys(self):
        """加载密钥对"""
        try:
            # 加载私钥
            with open(os.path.join(self.key_pair_path, "private_key.pem"), 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # 加载公钥
            with open(os.path.join(self.key_pair_path, "public_key.pem"), 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        
        except Exception as e:
            self.logger.error(f"加载密钥对失败: {e}")
    
    def generate_key_pair(self, key_size: int = 2048, save_path: str = None):
        """生成密钥对"""
        try:
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            # 获取公钥
            public_key = private_key.public_key()
            
            # 保存密钥对
            if save_path:
                os.makedirs(save_path, exist_ok=True)
                
                # 保存私钥
                with open(os.path.join(save_path, "private_key.pem"), 'wb') as f:
                    f.write(private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                
                # 保存公钥
                with open(os.path.join(save_path, "public_key.pem"), 'wb') as f:
                    f.write(public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
            
            self.private_key = private_key
            self.public_key = public_key
            
            self.logger.info(f"密钥对生成成功，密钥长度: {key_size}")
        
        except Exception as e:
            self.logger.error(f"生成密钥对失败: {e}")
    
    def sign_image(self, tag: ImageTag) -> str:
        """签名镜像"""
        try:
            if not self.private_key:
                raise ValueError("私钥未加载")
            
            # 构建签名数据
            signature_data = f"{tag.repo_id}:{tag.tag_name}:{tag.digest}".encode()
            
            # 生成签名
            signature = self.private_key.sign(
                signature_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # 编码签名
            signature_b64 = base64.b64encode(signature).decode()
            
            # 更新标签签名
            tag.signature = signature_b64
            
            self.logger.info(f"镜像签名成功: {tag.tag_name}")
            return signature_b64
        
        except Exception as e:
            self.logger.error(f"镜像签名失败: {e}")
            raise
    
    def verify_signature(self, tag: ImageTag, signature: str) -> bool:
        """验证签名"""
        try:
            if not self.public_key:
                raise ValueError("公钥未加载")
            
            # 解码签名
            signature_bytes = base64.b64decode(signature)
            
            # 构建签名数据
            signature_data = f"{tag.repo_id}:{tag.tag_name}:{tag.digest}".encode()
            
            # 验证签名
            self.public_key.verify(
                signature_bytes,
                signature_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            self.logger.info(f"签名验证成功: {tag.tag_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"签名验证失败: {e}")
            return False

class AccessController:
    """访问控制器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.users = {}
        self.roles = {
            'admin': ['read', 'write', 'delete', 'manage'],
            'developer': ['read', 'write'],
            'guest': ['read']
        }
    
    def add_user(self, user: RegistryUser):
        """添加用户"""
        self.users[user.user_id] = user
        self.logger.info(f"添加用户: {user.username}")
    
    def authenticate(self, username: str, password: str) -> Optional[RegistryUser]:
        """认证用户"""
        for user in self.users.values():
            if user.username == username and user.active:
                # 简化认证，实际应该验证密码
                return user
        return None
    
    def authorize(self, user: RegistryUser, action: str, resource: str) -> bool:
        """授权检查"""
        user_permissions = self.roles.get(user.role, [])
        return action in user_permissions
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """获取用户权限"""
        user = self.users.get(user_id)
        if user:
            return self.roles.get(user.role, [])
        return []

class ContainerRegistry:
    """容器镜像仓库"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.storage = ImageStorage(
            storage_path=config.get('storage_path', '/var/lib/registry'),
            compression=config.get('compression', 'gzip')
        )
        self.scanner = SecurityScanner(
            scanner_type=config.get('scanner_type', 'trivy')
        )
        self.signer = ImageSigner(
            key_pair_path=config.get('key_pair_path')
        )
        self.access_controller = AccessController()
        
        # 数据存储
        self.repositories = {}
        self.image_tags = {}
        self.access_logs = []
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 数据库连接
        self.db_conn = sqlite3.connect(config.get('db_path', 'registry.db'))
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        cursor = self.db_conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                repo_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                namespace TEXT NOT NULL,
                visibility TEXT NOT NULL,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                tags_count INTEGER DEFAULT 0,
                size_bytes INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_tags (
                tag_id TEXT PRIMARY KEY,
                repo_id TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                digest TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                created_at TIMESTAMP,
                pushed_at TIMESTAMP,
                pulled_count INTEGER DEFAULT 0,
                scan_status TEXT DEFAULT 'pending',
                signature TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                repo_id TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                action TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                timestamp TIMESTAMP,
                status_code INTEGER,
                size_bytes INTEGER DEFAULT 0,
                duration_ms INTEGER DEFAULT 0
            )
        ''')
        
        self.db_conn.commit()
    
    def start(self):
        """启动仓库"""
        self.logger.info("启动容器镜像仓库")
        
        # 启动安全扫描器
        self.scanner.start_scanner()
        
        # 启动Web服务（简化实现）
        self._start_web_server()
    
    def stop(self):
        """停止仓库"""
        self.logger.info("停止容器镜像仓库")
        
        # 停止安全扫描器
        self.scanner.stop_scanner()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 关闭数据库连接
        self.db_conn.close()
    
    def create_repository(self, name: str, namespace: str, visibility: str = "private") -> Repository:
        """创建仓库"""
        try:
            repo = Repository(
                repo_id=str(uuid.uuid4()),
                name=name,
                description="",
                namespace=namespace,
                visibility=visibility,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO repositories (repo_id, name, description, namespace, visibility, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (repo.repo_id, repo.name, repo.description, repo.namespace, repo.visibility, repo.created_at, repo.updated_at))
            self.db_conn.commit()
            
            self.repositories[repo.repo_id] = repo
            self.logger.info(f"创建仓库: {name}")
            
            return repo
        
        except Exception as e:
            self.logger.error(f"创建仓库失败: {e}")
            raise
    
    def push_image(self, repo_name: str, tag_name: str, image_data: bytes, user: RegistryUser = None) -> ImageTag:
        """推送镜像"""
        try:
            # 查找仓库
            repo = None
            for r in self.repositories.values():
                if r.name == repo_name:
                    repo = r
                    break
            
            if not repo:
                repo = self.create_repository(repo_name, "default")
            
            # 计算镜像摘要
            digest = hashlib.sha256(image_data).hexdigest()
            
            # 创建标签
            tag = ImageTag(
                tag_id=str(uuid.uuid4()),
                repo_id=repo.repo_id,
                tag_name=tag_name,
                digest=digest,
                size_bytes=len(image_data),
                created_at=datetime.now(),
                pushed_at=datetime.now()
            )
            
            # 存储镜像
            layer = ImageLayer(
                layer_id=str(uuid.uuid4()),
                tag_id=tag.tag_id,
                digest=digest,
                size_bytes=len(image_data),
                command="",
                created_at=datetime.now()
            )
            
            self.storage.store_image_layer(layer, image_data)
            
            # 保存到数据库
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO image_tags (tag_id, repo_id, tag_name, digest, size_bytes, created_at, pushed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (tag.tag_id, tag.repo_id, tag.tag_name, tag.digest, tag.size_bytes, tag.created_at, tag.pushed_at))
            self.db_conn.commit()
            
            # 签名镜像
            if self.signer.private_key:
                self.signer.sign_image(tag)
            
            # 队列安全扫描
            self.scanner.queue_scan(tag)
            
            # 记录访问日志
            self._log_access(user, repo.repo_id, tag_name, "push")
            
            self.logger.info(f"推送镜像成功: {repo_name}:{tag_name}")
            return tag
        
        except Exception as e:
            self.logger.error(f"推送镜像失败: {e}")
            raise
    
    def pull_image(self, repo_name: str, tag_name: str, user: RegistryUser = None) -> bytes:
        """拉取镜像"""
        try:
            # 查找标签
            tag = None
            for t in self.image_tags.values():
                if t.tag_name == tag_name:
                    tag = t
                    break
            
            if not tag:
                raise ValueError(f"镜像标签不存在: {repo_name}:{tag_name}")
            
            # 验证签名
            if tag.signature and self.signer.public_key:
                if not self.signer.verify_signature(tag, tag.signature):
                    raise ValueError("镜像签名验证失败")
            
            # 检索镜像
            image_data = self.storage.retrieve_image_layer(tag.digest)
            
            # 更新拉取计数
            tag.pulled_count += 1
            
            # 记录访问日志
            self._log_access(user, tag.repo_id, tag_name, "pull")
            
            self.logger.info(f"拉取镜像成功: {repo_name}:{tag_name}")
            return image_data
        
        except Exception as e:
            self.logger.error(f"拉取镜像失败: {e}")
            raise
    
    def _log_access(self, user: RegistryUser, repo_id: str, tag_name: str, action: str):
        """记录访问日志"""
        try:
            log = AccessLog(
                log_id=str(uuid.uuid4()),
                user_id=user.user_id if user else None,
                repo_id=repo_id,
                tag_name=tag_name,
                action=action,
                ip_address="127.0.0.1",  # 简化实现
                user_agent="registry-client",
                timestamp=datetime.now(),
                status_code=200
            )
            
            # 保存到数据库
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs (log_id, user_id, repo_id, tag_name, action, ip_address, user_agent, timestamp, status_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (log.log_id, log.user_id, log.repo_id, log.tag_name, log.action, log.ip_address, log.user_agent, log.timestamp, log.status_code))
            self.db_conn.commit()
            
            self.access_logs.append(log)
        
        except Exception as e:
            self.logger.error(f"记录访问日志失败: {e}")
    
    def _start_web_server(self):
        """启动Web服务"""
        # 简化实现，实际应该使用Flask或FastAPI
        self.logger.info("Web服务已启动")
    
    def get_repository_stats(self, repo_id: str) -> Dict[str, Any]:
        """获取仓库统计"""
        try:
            cursor = self.db_conn.cursor()
            
            # 获取标签数量
            cursor.execute('SELECT COUNT(*) FROM image_tags WHERE repo_id = ?', (repo_id,))
            tags_count = cursor.fetchone()[0]
            
            # 获取总大小
            cursor.execute('SELECT SUM(size_bytes) FROM image_tags WHERE repo_id = ?', (repo_id,))
            total_size = cursor.fetchone()[0] or 0
            
            # 获取拉取次数
            cursor.execute('SELECT SUM(pulled_count) FROM image_tags WHERE repo_id = ?', (repo_id,))
            pull_count = cursor.fetchone()[0] or 0
            
            return {
                'tags_count': tags_count,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'pull_count': pull_count
            }
        
        except Exception as e:
            self.logger.error(f"获取仓库统计失败: {e}")
            return {}
    
    def get_security_report(self, tag_id: str) -> Dict[str, Any]:
        """获取安全报告"""
        try:
            vulnerabilities = self.scanner.get_scan_results(tag_id)
            
            # 按严重性分组
            severity_count = defaultdict(int)
            for vuln in vulnerabilities:
                severity_count[vuln.severity] += 1
            
            return {
                'total_vulnerabilities': len(vulnerabilities),
                'severity_breakdown': dict(severity_count),
                'vulnerabilities': [asdict(vuln) for vuln in vulnerabilities]
            }
        
        except Exception as e:
            self.logger.error(f"获取安全报告失败: {e}")
            return {}

# 使用示例
# 配置
config = {
    'storage_path': '/var/lib/container-registry',
    'compression': 'gzip',
    'scanner_type': 'trivy',
    'key_pair_path': '/etc/registry/keys',
    'db_path': '/var/lib/registry/registry.db'
}

# 创建仓库
registry = ContainerRegistry(config)

# 生成密钥对
registry.signer.generate_key_pair(key_size=2048, save_path=config['key_pair_path'])

# 启动仓库
registry.start()

# 创建用户
admin_user = RegistryUser(
    user_id=str(uuid.uuid4()),
    username="admin",
    email="admin@example.com",
    role="admin"
)
registry.access_controller.add_user(admin_user)

# 创建仓库
repo = registry.create_repository("myapp", "development", "private")

# 推送镜像
with open('app-image.tar', 'rb') as f:
    image_data = f.read()

tag = registry.push_image("myapp", "v1.0.0", image_data, admin_user)

# 拉取镜像
pulled_image = registry.pull_image("myapp", "v1.0.0", admin_user)

# 获取仓库统计
stats = registry.get_repository_stats(repo.repo_id)
print(f"仓库统计: {stats}")

# 获取安全报告
time.sleep(5)  # 等待扫描完成
security_report = registry.get_security_report(tag.tag_id)
print(f"安全报告: {security_report}")

# 停止仓库
registry.stop()
```

## 参考资源

### 容器镜像仓库
- [Docker Registry官方文档](https://docs.docker.com/registry/)
- [Harbor官方文档](https://goharbor.io/docs/)
- [Nexus Repository文档](https://help.sonatype.com/repomanager3)
- [GitLab Container Registry](https://docs.gitlab.com/ee/user/packages/container_registry/)

### 云镜像仓库
- [AWS ECR文档](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [Google Container Registry](https://cloud.google.com/container-registry)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)
- [阿里云容器镜像服务](https://help.aliyun.com/product/60716.html)

### 安全扫描
- [Trivy安全扫描器](https://github.com/aquasecurity/trivy)
- [Clair安全扫描器](https://github.com/quay/clair)
- [Grype安全扫描器](https://github.com/anchore/grype)
- [Anchore安全分析](https://anchore.com/)

### 镜像签名
- [Docker Content Trust](https://docs.docker.com/engine/security/trust/)
- [Notary签名服务](https://github.com/theupdateframework/notary)
- [Sigstore签名服务](https://sigstore.dev/)
- [Cosign签名工具](https://github.com/sigstore/cosign)

### 性能优化
- [镜像缓存策略](https://docs.docker.com/registry/storage-drivers/)
- [CDN加速](https://docs.docker.com/registry/configuration/#proxy)
- [负载均衡](https://docs.docker.com/registry/recipes/mirror/)
- [存储优化](https://docs.docker.com/registry/storage-drivers/)
