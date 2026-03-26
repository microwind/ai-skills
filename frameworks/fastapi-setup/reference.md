# FastAPI高性能API参考文档

## FastAPI框架概述

### 什么是FastAPI
FastAPI是一个现代、快速（高性能）的Python Web框架，用于构建API。它基于标准Python类型提示，使用Pydantic进行数据验证，并自动生成交互式API文档。FastAPI是构建高性能异步API的理想选择。

### FastAPI核心特性
- **高性能**: 与Node.js和Go相当的性能
- **快速编码**: 将开发速度提高200-300%
- **更少的错误**: 减少约40%的人为错误
- **直观**: 优秀的编辑器支持，自动补全
- **易于使用**: 设计易于学习和使用
- **简短**: 最小化代码重复
- **健壮**: 生产就绪的代码
- **标准化**: 基于并完全兼容API开放标准

## FastAPI应用基础架构

### 基础应用结构
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="FastAPI Application",
    description="A high-performance API built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic模型
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None

# 内存数据库
items_db = []
next_id = 1

# 路由
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to FastAPI Application"}

@app.get("/items", response_model=List[Item], tags=["Items"])
async def get_items():
    return items_db

@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int):
    item = next((item for item in items_db if item.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=Item, tags=["Items"])
async def create_item(item: ItemCreate):
    global next_id
    new_item = Item(id=next_id, **item.dict())
    items_db.append(new_item)
    next_id += 1
    return new_item

@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item: ItemUpdate):
    item_index = next((i for i, existing_item in enumerate(items_db) 
                      if existing_item.id == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.dict(exclude_unset=True)
    items_db[item_index].dict().update(update_data)
    return items_db[item_index]

@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int):
    item_index = next((i for i, item in enumerate(items_db) 
                      if item.id == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    items_db.pop(item_index)
    return {"message": "Item deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 模块化应用架构
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, posts, auth
from core.config import settings
from core.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["authentication"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(posts.router, prefix=settings.API_V1_STR, tags=["posts"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
```

## 数据模型和验证

### Pydantic模型设计
```python
# models/user.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: UserRole = UserRole.USER

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username cannot exceed 50 characters')
        return v

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if v and len(v) > 50:
            raise ValueError('Name cannot exceed 50 characters')
        return v

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    role: UserRole
    created_at: datetime

    class Config:
        orm_mode = True
```

### SQLModel集成
```python
# models/database.py
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    username: str = Field(index=True, unique=True, max_length=50)
    hashed_password: str = Field(max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    is_active: bool = Field(default=True)
    role: str = Field(default="user", max_length=20)
    created_at: datetime = Field(default_factory=func.now())
    updated_at: datetime = Field(default_factory=func.now())
    
    # 关系
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str = Field(sa_column=Text)
    author_id: int = Field(foreign_key="users.id")
    is_published: bool = Field(default=False)
    created_at: datetime = Field(default_factory=func.now())
    updated_at: datetime = Field(default_factory=func.now())
    
    # 关系
    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")

class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Text)
    author_id: int = Field(foreign_key="users.id")
    post_id: int = Field(foreign_key="posts.id")
    created_at: datetime = Field(default_factory=func.now())
    
    # 关系
    author: User = Relationship(back_populates="comments")
    post: Post = Relationship(back_populates="comments")
```

## 异步处理和数据库

### 异步数据库操作
```python
# core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建异步会话
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### 异步CRUD操作
```python
# crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from models.user import User, UserCreate, UserUpdate
from core.security import get_password_hash

class UserCRUD:
    async def get(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """获取单个用户"""
        statement = select(User).where(User.id == user_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """获取用户列表"""
        statement = select(User).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """创建用户"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=obj_in.is_active,
            role=obj_in.role
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: User, 
        obj_in: UserUpdate
    ) -> User:
        """更新用户"""
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """删除用户"""
        user = await self.get(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
        return user

user_crud = UserCRUD()
```

## 认证和授权

### JWT认证实现
```python
# core/security.py
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

### 认证依赖
```python
# core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_session
from core.security import verify_token
from crud.user import user_crud
from models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await user_crud.get(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_roles(*allowed_roles: str):
    """角色权限装饰器"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# 使用示例
admin_required = require_roles("admin")
admin_or_moderator_required = require_roles("admin", "moderator")
```

## 路由和API端点

### 用户路由
```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_session
from core.deps import get_current_active_user, admin_required
from models.user import User, UserCreate, UserUpdate, UserResponse
from crud.user import user_crud

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(admin_required)
):
    """获取用户列表 - 仅管理员"""
    users = await user_crud.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户详情"""
    # 只有管理员或用户本人可以查看
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = await user_crud.get(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(admin_required)
):
    """创建用户 - 仅管理员"""
    # 检查用户是否已存在
    existing_user = await user_crud.get_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await user_crud.get_by_username(db, username=user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return await user_crud.create(db, obj_in=user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新用户"""
    # 权限检查
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_user = await user_crud.get(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查邮箱和用户名唯一性
    if user_update.email:
        existing_user = await user_crud.get_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if user_update.username:
        existing_username = await user_crud.get_by_username(db, username=user_update.username)
        if existing_username and existing_username.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    return await user_crud.update(db, db_obj=db_user, obj_in=user_update)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(admin_required)
):
    """删除用户 - 仅管理员"""
    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    user = await user_crud.delete(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}
```

## 中间件开发

### 自定义中间件
```python
# middleware/logging.py
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"- ID: {request_id} - IP: {request.client.host}"
        )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # 记录响应信息
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- ID: {request_id} - Status: {response.status_code} "
                f"- Time: {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            # 记录错误
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- ID: {request_id} - Error: {str(e)} - Time: {process_time:.4f}s"
            )
            
            # 返回错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id
                }
            )

# middleware/rate_limit.py
import asyncio
from collections import defaultdict
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # 获取客户端IP
        client_ip = request.client.host
        
        # 清理过期记录
        now = time.time()
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if now - timestamp < self.period
        ]
        
        # 检查是否超过限制
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "limit": self.calls,
                    "period": self.period
                }
            )
        
        # 记录当前请求
        self.clients[client_ip].append(now)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加限流头
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.calls - len(self.clients[client_ip]))
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(now + self.period)
        )
        
        return response
```

## 错误处理

### 全局异常处理
```python
# exceptions/handlers.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class APIException(Exception):
    """自定义API异常"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        extra: dict = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.extra = extra or {}

async def api_exception_handler(request: Request, exc: APIException):
    """API异常处理器"""
    logger.error(
        f"API Exception: {exc.status_code} - {exc.detail} "
        f"- Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            **exc.extra
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} "
        f"- Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证异常处理器"""
    logger.warning(
        f"Validation Exception: {exc.errors()} "
        f"- Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url.path)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(
        f"Unhandled Exception: {str(exc)} "
        f"- Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )
```

## 性能优化

### 缓存实现
```python
# core/cache.py
import json
import hashlib
from typing import Any, Optional, Union
import redis.asyncio as redis
from core.config import settings

class RedisCache:
    """Redis缓存客户端"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    def _make_key(self, prefix: str, key: Union[str, dict]) -> str:
        """生成缓存键"""
        if isinstance(key, dict):
            key_str = json.dumps(key, sort_keys=True)
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        return f"{prefix}:{key}"
    
    async def get(self, prefix: str, key: Union[str, dict]) -> Optional[Any]:
        """获取缓存"""
        cache_key = self._make_key(prefix, key)
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                return cached_data
        
        return None
    
    async def set(
        self, 
        prefix: str, 
        key: Union[str, dict], 
        value: Any, 
        expire: int = 3600
    ) -> bool:
        """设置缓存"""
        cache_key = self._make_key(prefix, key)
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis_client.setex(cache_key, expire, value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, prefix: str, key: Union[str, dict]) -> bool:
        """删除缓存"""
        cache_key = self._make_key(prefix, key)
        try:
            await self.redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> bool:
        """清除匹配模式的缓存"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False

cache = RedisCache()

# 装饰器缓存
def cache_result(prefix: str, expire: int = 3600):
    """缓存结果装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            
            # 尝试从缓存获取
            cached_result = await cache.get(prefix, cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await cache.set(prefix, cache_key, result, expire)
            
            return result
        return wrapper
    return decorator
```

## 测试实现

### 测试配置
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from main import app
from core.database import get_session
from core.config import settings

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 创建测试引擎
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_session():
    """创建测试会话"""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(test_session):
    """创建测试客户端"""
    async def override_get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    # 创建数据库表
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # 清理数据库
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user_data():
    """测试用户数据"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
```

### API测试示例
```python
# tests/test_users.py
import pytest
from httpx import AsyncClient
from core.security import create_access_token

class TestUsersAPI:
    """用户API测试"""
    
    async def test_create_user(self, client: AsyncClient, test_user_data: dict):
        """测试创建用户"""
        # 创建管理员用户
        admin_token = await self._create_admin_user(client)
        
        response = await client.post(
            "/api/v1/users/",
            json=test_user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "password" not in data
    
    async def test_get_users(self, client: AsyncClient):
        """测试获取用户列表"""
        admin_token = await self._create_admin_user(client)
        
        response = await client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_current_user(self, client: AsyncClient, test_user_data: dict):
        """测试获取当前用户"""
        # 创建用户
        user_token = await self._create_user(client, test_user_data)
        
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """测试未授权访问"""
        response = await client.get("/api/v1/users/")
        assert response.status_code == 401
    
    async def test_invalid_token(self, client: AsyncClient):
        """测试无效令牌"""
        response = await client.get(
            "/api/v1/users/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    async def _create_admin_user(self, client: AsyncClient) -> str:
        """创建管理员用户并返回令牌"""
        admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "AdminPassword123!",
            "role": "admin"
        }
        
        # 直接创建用户（绕过API认证）
        from crud.user import user_crud
        from models.user import UserCreate
        
        async with TestSessionLocal() as session:
            user = await user_crud.create(session, UserCreate(**admin_data))
        
        # 生成令牌
        return create_access_token(data={"sub": user.id})
    
    async def _create_user(self, client: AsyncClient, user_data: dict) -> str:
        """创建普通用户并返回令牌"""
        from crud.user import user_crud
        from models.user import UserCreate
        
        async with TestSessionLocal() as session:
            user = await user_crud.create(session, UserCreate(**user_data))
        
        # 生成令牌
        return create_access_token(data={"sub": user.id})
```

这个FastAPI参考文档提供了完整的高性能API开发指南，包括异步处理、数据验证、认证授权、中间件开发、性能优化和测试实现，帮助开发者构建现代化的FastAPI应用。
