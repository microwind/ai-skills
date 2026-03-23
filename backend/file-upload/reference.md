# 文件上传参考文档

## 文件上传概述

### 什么是文件上传
文件上传是一种将本地文件传输到远程服务器的技术，通过HTTP协议或其他网络协议实现文件的安全、高效传输。该技能涵盖了多种文件类型支持、安全验证、分片上传、云存储集成、文件处理、性能优化等功能，帮助开发者构建功能完善、安全可靠的文件上传系统。

### 主要功能
- **多格式支持**: 支持图片、文档、视频、音频等多种文件格式上传
- **安全验证**: 提供文件类型检查、病毒扫描、恶意代码检测等安全功能
- **分片上传**: 支持大文件分片上传、断点续传、并发上传
- **云存储集成**: 集成AWS S3、阿里云OSS、腾讯云COS等云存储服务
- **文件处理**: 包含图片压缩、缩略图生成、文档转换、元数据提取等功能

## 文件上传引擎核心

### 文件上传管理器
```python
# file_upload.py
import os
import uuid
import hashlib
import mimetypes
import tempfile
import threading
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, BinaryIO
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import zipfile
import gzip
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from werkzeug.datastructures import FileStorage
from PIL import Image, ExifTags
import magic

class UploadStatus(Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StorageType(Enum):
    LOCAL = "local"
    S3 = "s3"
    OSS = "oss"
    COS = "cos"
    CUSTOM = "custom"

@dataclass
class FileConfig:
    # 基础配置
    upload_folder: str = "uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_files_per_upload: int = 10
    allowed_extensions: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt',
        'zip', 'rar', '7z', 'tar', 'gz',
        'mp4', 'avi', 'mov', 'wmv',
        'mp3', 'wav', 'flac', 'aac'
    ])
    forbidden_extensions: List[str] = field(default_factory=lambda: [
        'exe', 'bat', 'com', 'scr', 'pif', 'vbs', 'js', 'jar'
    ])
    
    # 安全配置
    enable_virus_scan: bool = False
    enable_content_check: bool = True
    enable_mime_check: bool = True
    enable_header_check: bool = True
    
    # 存储配置
    storage_type: StorageType = StorageType.LOCAL
    cloud_config: Dict[str, Any] = field(default_factory=dict)
    
    # 处理配置
    enable_image_processing: bool = True
    enable_thumbnail: bool = True
    thumbnail_size: tuple = (200, 200)
    enable_compression: bool = True
    compression_quality: int = 85
    
    # 性能配置
    chunk_size: int = 8192
    max_workers: int = 4
    enable_chunk_upload: bool = True
    chunk_size_mb: int = 5
    
    # 监控配置
    enable_monitoring: bool = True
    monitoring_interval: float = 60.0

@dataclass
class FileInfo:
    file_id: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    extension: str
    checksum: str
    upload_time: datetime = field(default_factory=datetime.now)
    status: UploadStatus = UploadStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    thumbnail_path: Optional[str] = None
    error_message: Optional[str] = None

class FileValidator:
    """文件验证器"""
    
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_file(self, file: FileStorage) -> tuple[bool, Optional[str]]:
        """验证文件"""
        # 检查文件是否为空
        if file.filename is None or file.filename == '':
            return False, "文件名为空"
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.config.max_file_size:
            return False, f"文件大小超过限制 ({file_size} > {self.config.max_file_size})"
        
        # 检查文件扩展名
        filename = file.filename
        extension = filename.rsplit('.', 1)[-1].lower()
        
        if extension in self.config.forbidden_extensions:
            return False, f"禁止的文件类型: {extension}"
        
        if self.config.allowed_extensions and extension not in self.config.allowed_extensions:
            return False, f"不允许的文件类型: {extension}"
        
        # 检查MIME类型
        if self.config.enable_mime_check:
            mime_type = self._get_mime_type(file)
            if not self._is_valid_mime_type(mime_type, extension):
                return False, f"MIME类型不匹配: {mime_type}"
        
        # 检查文件头
        if self.config.enable_header_check:
            if not self._validate_file_header(file, extension):
                return False, "文件头验证失败"
        
        return True, None
    
    def _get_mime_type(self, file: FileStorage) -> str:
        """获取MIME类型"""
        file.seek(0)
        mime_type, _ = mimetypes.guess_type(file.filename)
        
        if mime_type is None:
            # 使用python-magic库检测MIME类型
            try:
                file_content = file.read(1024)
                file.seek(0)
                mime_type = magic.from_buffer(file_content, mime=True)
            except Exception:
                mime_type = "application/octet-stream"
        
        return mime_type
    
    def _is_valid_mime_type(self, mime_type: str, extension: str) -> bool:
        """验证MIME类型"""
        # 扩展名到MIME类型的映射
        extension_mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'zip': 'application/zip',
            'mp4': 'video/mp4',
            'mp3': 'audio/mpeg'
        }
        
        expected_mime = extension_mime_map.get(extension)
        if expected_mime:
            return mime_type.startswith(expected_mime.split('/')[0])
        
        return True
    
    def _validate_file_header(self, file: FileStorage, extension: str) -> bool:
        """验证文件头"""
        file.seek(0)
        header = file.read(16)
        file.seek(0)
        
        # 文件头签名
        file_signatures = {
            'jpg': [b'\xFF\xD8\xFF'],
            'png': [b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'],
            'gif': [b'GIF87a', b'GIF89a'],
            'pdf': [b'%PDF'],
            'zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
            'mp4': [b'\x00\x00\x00\x18ftypmp4'],
            'mp3': [b'ID3', b'\xFF\xFB']
        }
        
        signatures = file_signatures.get(extension, [])
        if signatures:
            return any(header.startswith(sig) for sig in signatures)
        
        return True

class StorageBackend:
    """存储后端抽象基类"""
    
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def save_file(self, file: FileStorage, file_id: str) -> str:
        """保存文件"""
        raise NotImplementedError
    
    def get_file(self, file_path: str) -> bytes:
        """获取文件"""
        raise NotImplementedError
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        raise NotImplementedError
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        raise NotImplementedError

class LocalStorage(StorageBackend):
    """本地存储"""
    
    def __init__(self, config: FileConfig):
        super().__init__(config)
        self.upload_folder = Path(config.upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file: FileStorage, file_id: str) -> str:
        """保存文件到本地"""
        # 创建日期目录
        date_folder = self.upload_folder / datetime.now().strftime("%Y/%m/%d")
        date_folder.mkdir(parents=True, exist_ok=True)
        
        # 生成文件路径
        extension = file.filename.rsplit('.', 1)[-1].lower()
        filename = f"{file_id}.{extension}"
        file_path = date_folder / filename
        
        # 保存文件
        file.seek(0)
        file.save(str(file_path))
        
        return str(file_path)
    
    def get_file(self, file_path: str) -> bytes:
        """获取文件内容"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"读取文件失败: {file_path}, 错误: {e}")
            return b""
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            self.logger.error(f"删除文件失败: {file_path}, 错误: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(file_path)

class S3Storage(StorageBackend):
    """AWS S3存储"""
    
    def __init__(self, config: FileConfig):
        super().__init__(config)
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.cloud_config.get('access_key'),
                aws_secret_access_key=config.cloud_config.get('secret_key'),
                region_name=config.cloud_config.get('region', 'us-east-1')
            )
            self.bucket_name = config.cloud_config.get('bucket_name')
        except ImportError:
            raise ImportError("需要安装boto3库: pip install boto3")
    
    def save_file(self, file: FileStorage, file_id: str) -> str:
        """保存文件到S3"""
        extension = file.filename.rsplit('.', 1)[-1].lower()
        key = f"{datetime.now().strftime('%Y/%m/%d')}/{file_id}.{extension}"
        
        file.seek(0)
        self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            key,
            ExtraArgs={
                'ContentType': mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
            }
        )
        
        return key
    
    def get_file(self, file_path: str) -> bytes:
        """获取S3文件内容"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response['Body'].read()
        except Exception as e:
            self.logger.error(f"读取S3文件失败: {file_path}, 错误: {e}")
            return b""
    
    def delete_file(self, file_path: str) -> bool:
        """删除S3文件"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception as e:
            self.logger.error(f"删除S3文件失败: {file_path}, 错误: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """检查S3文件是否存在"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except:
            return False

class FileProcessor:
    """文件处理器"""
    
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理文件"""
        metadata = {}
        
        # 提取基础元数据
        metadata.update(self._extract_basic_metadata(file_info))
        
        # 处理图片
        if self._is_image_file(file_info.mime_type):
            metadata.update(self._process_image(file_info))
        
        # 处理文档
        elif self._is_document_file(file_info.mime_type):
            metadata.update(self._process_document(file_info))
        
        return metadata
    
    def _extract_basic_metadata(self, file_info: FileInfo) -> Dict[str, Any]:
        """提取基础元数据"""
        metadata = {
            'file_size': file_info.file_size,
            'mime_type': file_info.mime_type,
            'extension': file_info.extension,
            'upload_time': file_info.upload_time.isoformat()
        }
        
        # 获取文件统计信息
        try:
            if os.path.exists(file_info.file_path):
                stat = os.stat(file_info.file_path)
                metadata.update({
                    'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'file_permissions': oct(stat.st_mode)[-3:]
                })
        except Exception as e:
            self.logger.error(f"获取文件统计信息失败: {e}")
        
        return metadata
    
    def _is_image_file(self, mime_type: str) -> bool:
        """判断是否为图片文件"""
        return mime_type.startswith('image/')
    
    def _is_document_file(self, mime_type: str) -> bool:
        """判断是否为文档文件"""
        document_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument',
            'text/plain'
        ]
        return any(mime_type.startswith(dt) for dt in document_types)
    
    def _process_image(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理图片文件"""
        metadata = {}
        
        try:
            with Image.open(file_info.file_path) as img:
                # 基础图片信息
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                })
                
                # 提取EXIF信息
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    exif_dict = {}
                    
                    for tag_id, value in exif_data.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value
                    
                    metadata['exif'] = exif_dict
                
                # 生成缩略图
                if self.config.enable_thumbnail:
                    thumbnail_path = self._generate_thumbnail(img, file_info.file_id)
                    if thumbnail_path:
                        file_info.thumbnail_path = thumbnail_path
                        metadata['thumbnail_path'] = thumbnail_path
                
                # 压缩图片
                if self.config.enable_compression:
                    self._compress_image(img, file_info.file_path)
        
        except Exception as e:
            self.logger.error(f"处理图片失败: {file_info.file_path}, 错误: {e}")
        
        return metadata
    
    def _generate_thumbnail(self, img: Image.Image, file_id: str) -> Optional[str]:
        """生成缩略图"""
        try:
            # 创建缩略图目录
            thumbnail_dir = Path(self.config.upload_folder) / "thumbnails"
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成缩略图
            img_copy = img.copy()
            img_copy.thumbnail(self.config.thumbnail_size, Image.Resampling.LANCZOS)
            
            thumbnail_path = thumbnail_dir / f"{file_id}_thumb.jpg"
            img_copy.save(thumbnail_path, "JPEG", quality=85)
            
            return str(thumbnail_path)
        
        except Exception as e:
            self.logger.error(f"生成缩略图失败: {e}")
            return None
    
    def _compress_image(self, img: Image.Image, file_path: str):
        """压缩图片"""
        try:
            if img.format in ('JPEG', 'JPG'):
                img.save(file_path, "JPEG", quality=self.config.compression_quality, optimize=True)
            elif img.format == 'PNG':
                img.save(file_path, "PNG", optimize=True)
        except Exception as e:
            self.logger.error(f"压缩图片失败: {e}")
    
    def _process_document(self, file_info: FileInfo) -> Dict[str, Any]:
        """处理文档文件"""
        metadata = {}
        
        try:
            # 这里可以集成文档处理库，如PyPDF2、python-docx等
            # 示例：提取PDF文档信息
            if file_info.mime_type == 'application/pdf':
                metadata.update(self._extract_pdf_metadata(file_info.file_path))
        
        except Exception as e:
            self.logger.error(f"处理文档失败: {file_info.file_path}, 错误: {e}")
        
        return metadata
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """提取PDF元数据"""
        metadata = {}
        
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.metadata:
                    metadata.update({
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                        'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                    })
                
                metadata['page_count'] = len(pdf_reader.pages)
        
        except ImportError:
            self.logger.warning("需要安装PyPDF2库: pip install PyPDF2")
        except Exception as e:
            self.logger.error(f"提取PDF元数据失败: {e}")
        
        return metadata

class FileUploadManager:
    """文件上传管理器"""
    
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validator = FileValidator(config)
        self.storage = self._create_storage()
        self.processor = FileProcessor(config)
        self.uploaded_files: Dict[str, FileInfo] = {}
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self._monitor_thread = None
        self._running = False
    
    def _create_storage(self) -> StorageBackend:
        """创建存储后端"""
        if self.config.storage_type == StorageType.LOCAL:
            return LocalStorage(self.config)
        elif self.config.storage_type == StorageType.S3:
            return S3Storage(self.config)
        else:
            raise ValueError(f"不支持的存储类型: {self.config.storage_type}")
    
    def start(self):
        """启动上传管理器"""
        self._running = True
        if self.config.enable_monitoring:
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
        self.logger.info("文件上传管理器启动")
    
    def stop(self):
        """停止上传管理器"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.executor.shutdown(wait=True)
        self.logger.info("文件上传管理器停止")
    
    def upload_file(self, file: FileStorage) -> tuple[bool, Optional[FileInfo]]:
        """上传单个文件"""
        try:
            # 验证文件
            is_valid, error_message = self.validator.validate_file(file)
            if not is_valid:
                return False, None
            
            # 生成文件ID
            file_id = str(uuid.uuid4())
            
            # 创建文件信息
            file_info = FileInfo(
                file_id=file_id,
                original_name=file.filename,
                file_path="",  # 将在保存后设置
                file_size=0,   # 将在保存后设置
                mime_type=mimetypes.guess_type(file.filename)[0] or "application/octet-stream",
                extension=file.filename.rsplit('.', 1)[-1].lower(),
                checksum=""  # 将在保存后计算
            )
            
            # 保存文件
            file_info.status = UploadStatus.UPLOADING
            file_path = self.storage.save_file(file, file_id)
            file_info.file_path = file_path
            
            # 计算文件大小和校验和
            file_content = self.storage.get_file(file_path)
            file_info.file_size = len(file_content)
            file_info.checksum = hashlib.md5(file_content).hexdigest()
            
            # 处理文件
            file_info.status = UploadStatus.PROCESSING
            metadata = self.processor.process_file(file_info)
            file_info.metadata = metadata
            
            # 完成上传
            file_info.status = UploadStatus.COMPLETED
            self.uploaded_files[file_id] = file_info
            
            self.logger.info(f"文件上传成功: {file.filename} -> {file_path}")
            return True, file_info
        
        except Exception as e:
            self.logger.error(f"文件上传失败: {file.filename}, 错误: {e}")
            return False, None
    
    def upload_multiple_files(self, files: List[FileStorage]) -> Dict[str, Any]:
        """批量上传文件"""
        if len(files) > self.config.max_files_per_upload:
            return {
                'success': False,
                'message': f"文件数量超过限制 ({len(files)} > {self.config.max_files_per_upload})"
            }
        
        results = []
        futures = []
        
        # 并发上传文件
        for file in files:
            future = self.executor.submit(self.upload_file, file)
            futures.append(future)
        
        # 等待所有上传完成
        for future in as_completed(futures):
            success, file_info = future.result()
            results.append({
                'success': success,
                'file_info': file_info
            })
        
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'success': success_count > 0,
            'total_files': len(files),
            'success_count': success_count,
            'failed_count': len(files) - success_count,
            'results': results
        }
    
    def get_file_info(self, file_id: str) -> Optional[FileInfo]:
        """获取文件信息"""
        return self.uploaded_files.get(file_id)
    
    def get_file_content(self, file_id: str) -> Optional[bytes]:
        """获取文件内容"""
        file_info = self.uploaded_files.get(file_id)
        if file_info:
            return self.storage.get_file(file_info.file_path)
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        file_info = self.uploaded_files.get(file_id)
        if not file_info:
            return False
        
        try:
            # 删除主文件
            self.storage.delete_file(file_info.file_path)
            
            # 删除缩略图
            if file_info.thumbnail_path:
                try:
                    os.remove(file_info.thumbnail_path)
                except Exception:
                    pass
            
            # 从内存中删除
            del self.uploaded_files[file_id]
            
            self.logger.info(f"文件删除成功: {file_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"文件删除失败: {file_id}, 错误: {e}")
            return False
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                self._cleanup_temp_files()
                time.sleep(self.config.monitoring_interval)
            except Exception as e:
                self.logger.error(f"监控循环异常: {e}")
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        try:
            temp_dir = tempfile.gettempdir()
            current_time = time.time()
            
            for filename in os.listdir(temp_dir):
                if filename.startswith('upload_'):
                    file_path = os.path.join(temp_dir, filename)
                    if current_time - os.path.getmtime(file_path) > 3600:  # 1小时
                        os.remove(file_path)
                        self.logger.info(f"清理临时文件: {filename}")
        
        except Exception as e:
            self.logger.error(f"清理临时文件失败: {e}")

# 全局上传管理器实例
upload_manager = None

def init_file_upload(config: FileConfig):
    """初始化文件上传管理器"""
    global upload_manager
    upload_manager = FileUploadManager(config)
    upload_manager.start()

def get_upload_manager() -> FileUploadManager:
    """获取上传管理器"""
    return upload_manager

# 使用示例
# 配置文件上传
config = FileConfig(
    upload_folder="uploads",
    max_file_size=50 * 1024 * 1024,  # 50MB
    max_files_per_upload=5,
    allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'zip'],
    enable_virus_scan=False,
    enable_content_check=True,
    enable_mime_check=True,
    enable_header_check=True,
    storage_type=StorageType.LOCAL,
    enable_image_processing=True,
    enable_thumbnail=True,
    thumbnail_size=(200, 200),
    enable_compression=True,
    compression_quality=85,
    max_workers=4,
    enable_chunk_upload=True,
    chunk_size_mb=5,
    enable_monitoring=True
)

# 初始化上传管理器
init_file_upload(config)

# 模拟文件上传
class MockFileStorage:
    """模拟文件存储对象"""
    def __init__(self, filename: str, content: bytes, content_type: str = None):
        self.filename = filename
        self.content = content
        self.content_type = content_type or mimetypes.guess_type(filename)[0]
        self._pos = 0
    
    def read(self, size: int = -1):
        if size == -1:
            data = self.content[self._pos:]
            self._pos = len(self.content)
        else:
            data = self.content[self._pos:self._pos + size]
            self._pos += len(data)
        return data
    
    def seek(self, pos: int, whence: int = 0):
        if whence == 0:
            self._pos = pos
        elif whence == 1:
            self._pos += pos
        elif whence == 2:
            self._pos = len(self.content) + pos
    
    def tell(self):
        return self._pos
    
    def save(self, dst: str):
        with open(dst, 'wb') as f:
            f.write(self.content)

# 测试单文件上传
test_content = b"This is a test file content"
test_file = MockFileStorage("test.txt", test_content)

manager = get_upload_manager()
success, file_info = manager.upload_file(test_file)

if success:
    print(f"文件上传成功: {file_info.original_name}")
    print(f"文件ID: {file_info.file_id}")
    print(f"文件大小: {file_info.file_size} 字节")
    print(f"文件路径: {file_info.file_path}")
    print(f"校验和: {file_info.checksum}")
    print(f"元数据: {file_info.metadata}")
else:
    print("文件上传失败")

# 测试多文件上传
test_files = [
    MockFileStorage("file1.txt", b"Content of file 1"),
    MockFileStorage("file2.txt", b"Content of file 2"),
    MockFileStorage("file3.txt", b"Content of file 3")
]

result = manager.upload_multiple_files(test_files)
print(f"\n批量上传结果: {result}")

# 获取文件信息
if success and file_info:
    file_info = manager.get_file_info(file_info.file_id)
    if file_info:
        print(f"\n文件信息: {file_info.original_name}")
        print(f"状态: {file_info.status.value}")

# 停止上传管理器
time.sleep(2)
manager.stop()
```

## 参考资源

### 文件上传技术
- [HTTP文件上传协议](https://tools.ietf.org/html/rfc1867)
- [multipart/form-data规范](https://tools.ietf.org/html/rfc2388)
- [文件上传最佳实践](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Using_XMLHttpRequest)
- [分片上传技术](https://aws.amazon.com/cn/blogs/china/amazon-s3-multipart-upload/)

### 存储服务
- [AWS S3文档](https://docs.aws.amazon.com/s3/)
- [阿里云OSS文档](https://help.aliyun.com/product/31815.html)
- [腾讯云COS文档](https://cloud.tencent.com/document/product/436)
- [MinIO对象存储](https://docs.min.io/)

### 文件处理
- [Python Pillow库](https://pillow.readthedocs.io/)
- [OpenCV图像处理](https://opencv.org/)
- [PyPDF2文档处理](https://pypdf2.readthedocs.io/)
- [python-docx文档处理](https://python-docx.readthedocs.io/)

### 安全防护
- [OWASP文件上传安全](https://owasp.org/www-project-cheat-sheets/cheatsheets/File_Upload_Cheat_Sheet.html)
- [文件类型检测](https://github.com/ahupp/python-magic)
- [病毒扫描ClamAV](https://www.clamav.net/)
- [内容安全策略](https://content-security-policy.com/)
