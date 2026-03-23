# JWT认证参考文档

## JWT认证概述

### 什么是JWT认证
JWT (JSON Web Token) 是一种开放标准 (RFC 7519)，用于在各方之间安全地传输信息作为JSON对象。JWT可以被验证和信任，因为它是数字签名的。该技能涵盖了JWT令牌生成、签名验证、时间管理、安全防护、多因子认证、联邦认证等功能，帮助开发者构建安全、可靠、高性能的身份认证系统。

### 主要功能
- **令牌生成**: 支持多种签名算法和自定义载荷的JWT令牌生成
- **签名验证**: 提供HMAC、RSA、ECDSA等多种签名算法的验证机制
- **时间管理**: 包含令牌过期、生效时间、时钟偏差等时间控制功能
- **安全防护**: 提供密钥管理、令牌黑名单、加密传输等安全功能
- **多租户支持**: 支持多租户环境下的身份隔离和权限管理

## JWT认证引擎核心

### JWT管理器
```python
# jwt_auth.py
import jwt
import time
import uuid
import hashlib
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend
import base64
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import redis
from functools import wraps

class JWTAlgorithm(Enum):
    """JWT算法枚举"""
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"

class TokenType(Enum):
    """令牌类型枚举"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"

class AuthResult(Enum):
    """认证结果枚举"""
    SUCCESS = "success"
    EXPIRED = "expired"
    INVALID = "invalid"
    BLACKLISTED = "blacklisted"
    REVOKED = "revoked"

@dataclass
class JWTConfig:
    """JWT配置"""
    # 基础配置
    algorithm: JWTAlgorithm = JWTAlgorithm.HS256
    secret_key: str = "your-secret-key"
    issuer: str = "your-app"
    audience: str = "your-users"
    
    # 时间配置
    access_token_expire: int = 3600  # 1小时
    refresh_token_expire: int = 86400 * 7  # 7天
    id_token_expire: int = 3600  # 1小时
    clock_skew_seconds: int = 60  # 时钟偏差容忍
    
    # 密钥配置
    private_key_path: Optional[str] = None
    public_key_path: Optional[str] = None
    key_rotation_enabled: bool = False
    key_rotation_interval: int = 86400  # 24小时
    
    # 安全配置
    blacklist_enabled: bool = True
    blacklist_storage: str = "redis"  # redis, memory, database
    encryption_enabled: bool = False
    encryption_key: Optional[str] = None
    
    # 缓存配置
    cache_enabled: bool = True
    cache_storage: str = "redis"
    cache_ttl: int = 300  # 5分钟
    
    # 审计配置
    audit_enabled: bool = True
    audit_storage: str = "database"
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

@dataclass
class TokenPayload:
    """令牌载荷"""
    iss: str  # 发行者
    sub: str  # 主题 (用户ID)
    aud: str  # 受众
    exp: int  # 过期时间
    nbf: int  # 生效时间
    iat: int  # 签发时间
    jti: str  # JWT ID
    type: str  # 令牌类型
    user_id: str  # 用户ID
    username: str  # 用户名
    email: str  # 邮箱
    roles: List[str] = field(default_factory=list)  # 角色
    permissions: List[str] = field(default_factory=list)  # 权限
    tenant_id: Optional[str] = None  # 租户ID
    custom_claims: Dict[str, Any] = field(default_factory=dict)  # 自定义声明

@dataclass
class AuthContext:
    """认证上下文"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    tenant_id: Optional[str] = None
    token_type: str = TokenType.ACCESS.value
    token_id: str = ""
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None

class JWTKeyManager:
    """JWT密钥管理器"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._private_key = None
        self._public_key = None
        self._key_cache = {}
        self._rotation_thread = None
        self._lock = threading.RLock()
        
        # 初始化密钥
        self._init_keys()
        
        # 启动密钥轮换
        if config.key_rotation_enabled:
            self._start_key_rotation()
    
    def _init_keys(self):
        """初始化密钥"""
        if self.config.algorithm in [JWTAlgorithm.HS256, JWTAlgorithm.HS384, JWTAlgorithm.HS512]:
            # 对称密钥
            self._private_key = self.config.secret_key.encode()
            self._public_key = self._private_key
        else:
            # 非对称密钥
            if self.config.private_key_path and self.config.public_key_path:
                # 从文件加载密钥
                self._load_keys_from_file()
            else:
                # 生成新密钥
                self._generate_keys()
    
    def _load_keys_from_file(self):
        """从文件加载密钥"""
        try:
            with open(self.config.private_key_path, 'rb') as f:
                self._private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            with open(self.config.public_key_path, 'rb') as f:
                self._public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            
            self.logger.info("密钥从文件加载成功")
        
        except Exception as e:
            self.logger.error(f"从文件加载密钥失败: {e}")
            raise
    
    def _generate_keys(self):
        """生成新密钥"""
        try:
            if self.config.algorithm in [JWTAlgorithm.RS256, JWTAlgorithm.RS384, JWTAlgorithm.RS512]:
                # RSA密钥
                self._private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
                self._public_key = self._private_key.public_key()
            
            elif self.config.algorithm in [JWTAlgorithm.ES256, JWTAlgorithm.ES384, JWTAlgorithm.ES512]:
                # ECDSA密钥
                curve_map = {
                    JWTAlgorithm.ES256: ec.SECP256R1(),
                    JWTAlgorithm.ES384: ec.SECP384R1(),
                    JWTAlgorithm.ES512: ec.SECP521R1()
                }
                curve = curve_map[self.config.algorithm]
                self._private_key = ec.generate_private_key(
                    curve=curve,
                    backend=default_backend()
                )
                self._public_key = self._private_key.public_key()
            
            self.logger.info("密钥生成成功")
        
        except Exception as e:
            self.logger.error(f"生成密钥失败: {e}")
            raise
    
    def _start_key_rotation(self):
        """启动密钥轮换"""
        self._rotation_thread = threading.Thread(target=self._key_rotation_loop, daemon=True)
        self._rotation_thread.start()
    
    def _key_rotation_loop(self):
        """密钥轮换循环"""
        while True:
            try:
                time.sleep(self.config.key_rotation_interval)
                self.rotate_keys()
            except Exception as e:
                self.logger.error(f"密钥轮换失败: {e}")
    
    def rotate_keys(self):
        """轮换密钥"""
        with self._lock:
            # 保存旧密钥到缓存
            old_key_id = self._get_key_id()
            self._key_cache[old_key_id] = {
                'private_key': self._private_key,
                'public_key': self._public_key,
                'created_at': time.time()
            }
            
            # 生成新密钥
            self._generate_keys()
            
            # 清理过期密钥缓存
            self._cleanup_key_cache()
            
            self.logger.info("密钥轮换完成")
    
    def _get_key_id(self) -> str:
        """获取密钥ID"""
        if self.config.algorithm in [JWTAlgorithm.HS256, JWTAlgorithm.HS384, JWTAlgorithm.HS512]:
            return hashlib.sha256(self._private_key).hexdigest()
        else:
            # 非对称密钥使用公钥指纹
            public_key_bytes = self._public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return hashlib.sha256(public_key_bytes).hexdigest()
    
    def _cleanup_key_cache(self):
        """清理密钥缓存"""
        current_time = time.time()
        expired_keys = [
            key_id for key_id, key_data in self._key_cache.items()
            if current_time - key_data['created_at'] > self.config.key_rotation_interval * 2
        ]
        
        for key_id in expired_keys:
            del self._key_cache[key_id]
    
    def get_private_key(self, key_id: Optional[str] = None):
        """获取私钥"""
        if key_id and key_id in self._key_cache:
            return self._key_cache[key_id]['private_key']
        return self._private_key
    
    def get_public_key(self, key_id: Optional[str] = None):
        """获取公钥"""
        if key_id and key_id in self._key_cache:
            return self._key_cache[key_id]['public_key']
        return self._public_key

class JWTBlacklist:
    """JWT黑名单管理器"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._storage = self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        if self.config.blacklist_storage == "redis":
            return RedisBlacklistStorage(config=self.config)
        elif self.config.blacklist_storage == "memory":
            return MemoryBlacklistStorage()
        elif self.config.blacklist_storage == "database":
            return DatabaseBlacklistStorage()
        else:
            raise ValueError(f"不支持的存储类型: {self.config.blacklist_storage}")
    
    def add_token(self, token_id: str, expires_at: datetime):
        """添加令牌到黑名单"""
        self._storage.add_token(token_id, expires_at)
        self.logger.info(f"令牌已添加到黑名单: {token_id}")
    
    def is_blacklisted(self, token_id: str) -> bool:
        """检查令牌是否在黑名单中"""
        return self._storage.is_blacklisted(token_id)
    
    def remove_token(self, token_id: str):
        """从黑名单移除令牌"""
        self._storage.remove_token(token_id)
        self.logger.info(f"令牌已从黑名单移除: {token_id}")
    
    def cleanup(self):
        """清理过期令牌"""
        self._storage.cleanup()

class RedisBlacklistStorage:
    """Redis黑名单存储"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            password=config.redis_password,
            decode_responses=True
        )
    
    def add_token(self, token_id: str, expires_at: datetime):
        """添加令牌到黑名单"""
        ttl = int((expires_at - datetime.now()).total_seconds())
        if ttl > 0:
            self.redis_client.setex(f"blacklist:{token_id}", ttl, "1")
    
    def is_blacklisted(self, token_id: str) -> bool:
        """检查令牌是否在黑名单中"""
        return self.redis_client.exists(f"blacklist:{token_id}")
    
    def remove_token(self, token_id: str):
        """从黑名单移除令牌"""
        self.redis_client.delete(f"blacklist:{token_id}")
    
    def cleanup(self):
        """Redis自动清理过期键"""

class MemoryBlacklistStorage:
    """内存黑名单存储"""
    
    def __init__(self):
        self.blacklisted_tokens = {}
        self.lock = threading.RLock()
    
    def add_token(self, token_id: str, expires_at: datetime):
        """添加令牌到黑名单"""
        with self.lock:
            self.blacklisted_tokens[token_id] = expires_at
    
    def is_blacklisted(self, token_id: str) -> bool:
        """检查令牌是否在黑名单中"""
        with self.lock:
            if token_id in self.blacklisted_tokens:
                expires_at = self.blacklisted_tokens[token_id]
                if datetime.now() > expires_at:
                    del self.blacklisted_tokens[token_id]
                    return False
                return True
            return False
    
    def remove_token(self, token_id: str):
        """从黑名单移除令牌"""
        with self.lock:
            self.blacklisted_tokens.pop(token_id, None)
    
    def cleanup(self):
        """清理过期令牌"""
        with self.lock:
            current_time = datetime.now()
            expired_tokens = [
                token_id for token_id, expires_at in self.blacklisted_tokens.items()
                if current_time > expires_at
            ]
            for token_id in expired_tokens:
                del self.blacklisted_tokens[token_id]

class DatabaseBlacklistStorage:
    """数据库黑名单存储"""
    
    def __init__(self):
        # 这里应该实现数据库连接和操作
        pass
    
    def add_token(self, token_id: str, expires_at: datetime):
        """添加令牌到黑名单"""
        # 实现数据库插入逻辑
        pass
    
    def is_blacklisted(self, token_id: str) -> bool:
        """检查令牌是否在黑名单中"""
        # 实现数据库查询逻辑
        return False
    
    def remove_token(self, token_id: str):
        """从黑名单移除令牌"""
        # 实现数据库删除逻辑
        pass
    
    def cleanup(self):
        """清理过期令牌"""
        # 实现数据库清理逻辑
        pass

class JWTAuthManager:
    """JWT认证管理器"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.key_manager = JWTKeyManager(config)
        self.blacklist = JWTBlacklist(config) if config.blacklist_enabled else None
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def generate_token(self, payload: TokenPayload, token_type: TokenType = TokenType.ACCESS) -> str:
        """生成JWT令牌"""
        try:
            # 设置令牌类型
            payload.type = token_type.value
            
            # 设置过期时间
            if token_type == TokenType.ACCESS:
                payload.exp = int(time.time()) + self.config.access_token_expire
            elif token_type == TokenType.REFRESH:
                payload.exp = int(time.time()) + self.config.refresh_token_expire
            elif token_type == TokenType.ID:
                payload.exp = int(time.time()) + self.config.id_token_expire
            
            # 设置标准声明
            payload.iss = payload.iss or self.config.issuer
            payload.aud = payload.aud or self.config.audience
            payload.iat = int(time.time())
            payload.nbf = payload.iat
            payload.jti = str(uuid.uuid4())
            
            # 转换为字典
            token_dict = asdict(payload)
            
            # 移除None值
            token_dict = {k: v for k, v in token_dict.items() if v is not None}
            
            # 获取密钥
            private_key = self.key_manager.get_private_key()
            
            # 生成令牌
            if self.config.algorithm in [JWTAlgorithm.HS256, JWTAlgorithm.HS384, JWTAlgorithm.HS512]:
                token = jwt.encode(
                    token_dict,
                    private_key,
                    algorithm=self.config.algorithm.value
                )
            else:
                token = jwt.encode(
                    token_dict,
                    private_key,
                    algorithm=self.config.algorithm.value
                )
            
            self.logger.info(f"令牌生成成功: {payload.jti}")
            return token
        
        except Exception as e:
            self.logger.error(f"令牌生成失败: {e}")
            raise
    
    def verify_token(self, token: str, token_type: TokenType = TokenType.ACCESS) -> tuple[AuthResult, Optional[TokenPayload]]:
        """验证JWT令牌"""
        try:
            # 解码令牌
            payload_dict = jwt.decode(
                token,
                options={
                    'verify_signature': False,
                    'verify_exp': False,
                    'verify_nbf': False,
                    'verify_iat': False,
                    'verify_iss': False,
                    'verify_aud': False
                }
            )
            
            # 检查令牌类型
            if payload_dict.get('type') != token_type.value:
                return AuthResult.INVALID, None
            
            # 检查黑名单
            if self.blacklist and self.blacklist.is_blacklisted(payload_dict.get('jti')):
                return AuthResult.BLACKLISTED, None
            
            # 获取公钥
            public_key = self.key_manager.get_public_key(payload_dict.get('kid'))
            
            # 验证令牌
            payload_dict = jwt.decode(
                token,
                key=public_key,
                algorithms=[self.config.algorithm.value],
                issuer=self.config.issuer,
                audience=self.config.audience,
                options={
                    'require': ['exp', 'iat', 'jti', 'type']
                }
            )
            
            # 转换为TokenPayload对象
            payload = TokenPayload(**payload_dict)
            
            # 检查时间
            current_time = time.time()
            
            # 检查过期时间
            if current_time > payload.exp + self.config.clock_skew_seconds:
                return AuthResult.EXPIRED, None
            
            # 检查生效时间
            if current_time < payload.nbf - self.config.clock_skew_seconds:
                return AuthResult.INVALID, None
            
            self.logger.info(f"令牌验证成功: {payload.jti}")
            return AuthResult.SUCCESS, payload
        
        except jwt.ExpiredSignatureError:
            return AuthResult.EXPIRED, None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"令牌验证失败: {e}")
            return AuthResult.INVALID, None
        except Exception as e:
            self.logger.error(f"令牌验证异常: {e}")
            return AuthResult.INVALID, None
    
    def refresh_token(self, refresh_token: str) -> tuple[AuthResult, Optional[str]]:
        """刷新令牌"""
        # 验证刷新令牌
        result, payload = self.verify_token(refresh_token, TokenType.REFRESH)
        
        if result != AuthResult.SUCCESS:
            return result, None
        
        try:
            # 生成新的访问令牌
            new_payload = TokenPayload(
                iss=payload.iss,
                sub=payload.sub,
                aud=payload.aud,
                exp=0,  # 将在generate_token中设置
                nbf=0,  # 将在generate_token中设置
                iat=0,  # 将在generate_token中设置
                jti="",  # 将在generate_token中设置
                type="",  # 将在generate_token中设置
                user_id=payload.user_id,
                username=payload.username,
                email=payload.email,
                roles=payload.roles,
                permissions=payload.permissions,
                tenant_id=payload.tenant_id,
                custom_claims=payload.custom_claims
            )
            
            new_access_token = self.generate_token(new_payload, TokenType.ACCESS)
            
            self.logger.info(f"令牌刷新成功: {payload.jti}")
            return AuthResult.SUCCESS, new_access_token
        
        except Exception as e:
            self.logger.error(f"令牌刷新失败: {e}")
            return AuthResult.INVALID, None
    
    def revoke_token(self, token: str):
        """撤销令牌"""
        try:
            # 解码令牌获取JTI
            payload_dict = jwt.decode(
                token,
                options={
                    'verify_signature': False,
                    'verify_exp': False,
                    'verify_nbf': False,
                    'verify_iat': False,
                    'verify_iss': False,
                    'verify_aud': False
                }
            )
            
            token_id = payload_dict.get('jti')
            expires_at = datetime.fromtimestamp(payload_dict.get('exp'))
            
            # 添加到黑名单
            if self.blacklist:
                self.blacklist.add_token(token_id, expires_at)
            
            self.logger.info(f"令牌撤销成功: {token_id}")
        
        except Exception as e:
            self.logger.error(f"令牌撤销失败: {e}")
            raise
    
    def get_auth_context(self, token: str) -> Optional[AuthContext]:
        """获取认证上下文"""
        result, payload = self.verify_token(token)
        
        if result != AuthResult.SUCCESS:
            return None
        
        return AuthContext(
            user_id=payload.user_id,
            username=payload.username,
            email=payload.email,
            roles=payload.roles,
            permissions=payload.permissions,
            tenant_id=payload.tenant_id,
            token_type=payload.type,
            token_id=payload.jti
        )

# 装饰器
def jwt_required(token_type: TokenType = TokenType.ACCESS):
    """JWT认证装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 这里应该从请求中提取令牌
            # 简化实现，实际应该从HTTP请求头中提取
            token = kwargs.get('token')
            if not token:
                raise ValueError("缺少认证令牌")
            
            # 验证令牌
            result, payload = jwt_auth_manager.verify_token(token, token_type)
            
            if result != AuthResult.SUCCESS:
                raise ValueError(f"认证失败: {result.value}")
            
            # 将认证上下文添加到kwargs
            context = jwt_auth_manager.get_auth_context(token)
            kwargs['auth_context'] = context
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_permission(permission: str):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_context = kwargs.get('auth_context')
            
            if not auth_context:
                raise ValueError("缺少认证上下文")
            
            if permission not in auth_context.permissions:
                raise ValueError(f"缺少权限: {permission}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_role(role: str):
    """角色检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_context = kwargs.get('auth_context')
            
            if not auth_context:
                raise ValueError("缺少认证上下文")
            
            if role not in auth_context.roles:
                raise ValueError(f"缺少角色: {role}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# 全局JWT认证管理器
jwt_auth_manager = None

def init_jwt_auth(config: JWTConfig):
    """初始化JWT认证管理器"""
    global jwt_auth_manager
    jwt_auth_manager = JWTAuthManager(config)

def get_jwt_auth_manager() -> JWTAuthManager:
    """获取JWT认证管理器"""
    return jwt_auth_manager

# 使用示例
# 配置JWT认证
config = JWTConfig(
    algorithm=JWTAlgorithm.HS256,
    secret_key="your-very-secure-secret-key",
    issuer="your-app",
    audience="your-users",
    access_token_expire=3600,  # 1小时
    refresh_token_expire=86400 * 7,  # 7天
    clock_skew_seconds=60,
    blacklist_enabled=True,
    blacklist_storage="redis",
    cache_enabled=True,
    cache_storage="redis",
    audit_enabled=True,
    redis_host="localhost",
    redis_port=6379,
    redis_db=0
)

# 初始化JWT认证管理器
init_jwt_auth(config)
manager = get_jwt_auth_manager()

# 示例用户数据
user_data = {
    'user_id': '12345',
    'username': 'john_doe',
    'email': 'john@example.com',
    'roles': ['user', 'admin'],
    'permissions': ['read', 'write', 'delete'],
    'tenant_id': 'tenant_001'
}

# 生成访问令牌
access_payload = TokenPayload(
    iss="",
    sub=user_data['user_id'],
    aud="",
    exp=0,
    nbf=0,
    iat=0,
    jti="",
    type="",
    user_id=user_data['user_id'],
    username=user_data['username'],
    email=user_data['email'],
    roles=user_data['roles'],
    permissions=user_data['permissions'],
    tenant_id=user_data['tenant_id']
)

access_token = manager.generate_token(access_payload, TokenType.ACCESS)
print(f"访问令牌: {access_token}")

# 生成刷新令牌
refresh_token = manager.generate_token(access_payload, TokenType.REFRESH)
print(f"刷新令牌: {refresh_token}")

# 验证令牌
result, payload = manager.verify_token(access_token, TokenType.ACCESS)
print(f"验证结果: {result.value}")
if payload:
    print(f"用户ID: {payload.user_id}")
    print(f"用户名: {payload.username}")
    print(f"角色: {payload.roles}")

# 刷新令牌
refresh_result, new_access_token = manager.refresh_token(refresh_token)
print(f"刷新结果: {refresh_result.value}")
if new_access_token:
    print(f"新访问令牌: {new_access_token}")

# 撤销令牌
manager.revoke_token(access_token)

# 验证已撤销的令牌
result, payload = manager.verify_token(access_token, TokenType.ACCESS)
print(f"撤销后验证结果: {result.value}")

# 使用装饰器示例
@jwt_required(TokenType.ACCESS)
@require_permission('read')
def get_user_data(auth_context: AuthContext):
    """获取用户数据"""
    return {
        'user_id': auth_context.user_id,
        'username': auth_context.username,
        'roles': auth_context.roles,
        'permissions': auth_context.permissions
    }

# 测试装饰器
try:
    user_data = get_user_data(token=access_token)
    print(f"装饰器测试成功: {user_data}")
except ValueError as e:
    print(f"装饰器测试失败: {e}")

# 清理资源
if jwt_auth_manager:
    jwt_auth_manager.executor.shutdown(wait=True)
```

## 参考资源

### JWT官方资源
- [JWT官方规范](https://tools.ietf.org/html/rfc7519)
- [JWT.io调试器](https://jwt.io/)
- [JWT最佳实践](https://auth0.com/blog/json-web-token-best-practices/)
- [JWT安全指南](https://owasp.org/www-project-cheat-sheets/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

### Python JWT库
- [PyJWT](https://pyjwt.readthedocs.io/)
- [Authlib](https://authlib.org/)
- [python-jose](https://python-jose.readthedocs.io/)
- [cryptography](https://cryptography.io/)

### 安全最佳实践
- [OWASP认证备忘录](https://owasp.org/www-project-cheat-sheets/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT安全威胁](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)
- [密钥管理最佳实践](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
- [OAuth 2.0安全最佳实践](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

### 性能优化
- [JWT性能优化](https://auth0.com/blog/json-web-token-jwt-vs-oauth-2-0/)
- [缓存策略](https://redis.io/)
- [负载均衡](https://nginx.org/en/docs/http/load_balancing.html)
- [数据库优化](https://www.postgresql.org/docs/)
