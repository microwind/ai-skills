---
name: JWT身份验证
description: "当实现JWT身份验证时，设计令牌生成策略，优化身份验证流程，解决令牌安全问题。验证身份验证架构，设计授权机制，和最佳实践。"
license: MIT
---

# JWT身份验证技能

## 概述
JWT（JSON Web Token）是现代Web应用中广泛使用的身份验证机制。不当的JWT实现会导致安全漏洞、令牌泄露和系统性能问题。在设计JWT系统前需要仔细分析安全需求。

**核心原则**: 好的JWT设计应该安全可靠、性能优良、易于管理、可扩展性强。坏的JWT设计会存在安全漏洞、令牌滥用、性能瓶颈。

## 何时使用

**始终:**
- 设计用户认证系统时
- 实现API访问控制时
- 构建微服务身份验证时
- 设计单点登录系统时
- 处理跨域身份验证时
- 实现令牌刷新机制时

**触发短语:**
- "如何实现JWT认证？"
- "JWT安全最佳实践"
- "令牌过期怎么处理？"
- "如何防止JWT劫持？"
- "刷新令牌怎么设计？"
- "JWT和Session哪个好？"

## JWT身份验证技能功能

### 令牌生成与验证
- JWT结构分析（Header、Payload、Signature）
- 签名算法选择（HS256、RS256、ES256）
- 令牌载荷设计
- 私钥和公钥管理
- 令牌验证流程

### 安全策略设计
- 令牌过期时间设置
- 刷新令牌机制
- 令牌撤销策略
- 防重放攻击
- 跨站脚本攻击防护

### 性能优化检查
- 令牌大小优化
- 验证性能分析
- 缓存策略设计
- 负载均衡考虑
- 分布式令牌管理

## 常见问题

### 令牌安全问题
- **问题**: 令牌泄露风险
- **原因**: 令牌在客户端存储不当
- **解决**: 使用HttpOnly Cookie，避免localStorage存储敏感令牌

- **问题**: 令牌被篡改
- **原因**: 签名验证不严格
- **解决**: 使用强签名算法，定期轮换密钥

- **问题**: 令牌重放攻击
- **原因**: 令牌唯一性不足
- **解决**: 添加jti（JWT ID）声明，实现令牌黑名单

### 性能问题
- **问题**: 验证性能瓶颈
- **原因**: 每次请求都验证令牌
- **解决**: 实现令牌缓存，优化验证逻辑

- **问题**: 令牌过大
- **原因**: 载荷包含过多信息
- **解决**: 精简载荷，使用引用ID

## 代码示例

### 基础JWT生成和验证
```python
import jwt
import datetime
from typing import Dict, Optional

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, payload: Dict, expires_in: int = 3600) -> str:
        """生成JWT令牌"""
        now = datetime.datetime.utcnow()
        payload.update({
            'iat': now,
            'exp': now + datetime.timedelta(seconds=expires_in),
            'jti': str(uuid.uuid4())  # 唯一标识符
        })
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("令牌已过期")
        except jwt.InvalidTokenError:
            raise Exception("无效令牌")

# 使用示例
jwt_manager = JWTManager(secret_key="your-secret-key")

# 生成令牌
user_data = {'user_id': 123, 'username': 'john', 'role': 'user'}
token = jwt_manager.generate_token(user_data, expires_in=3600)

# 验证令牌
try:
    payload = jwt_manager.verify_token(token)
    print(f"验证成功: {payload}")
except Exception as e:
    print(f"验证失败: {e}")
```

### 刷新令牌机制
```python
class RefreshTokenManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.refresh_tokens = {}  # 实际应用中应使用数据库
    
    def generate_refresh_token(self, user_id: int) -> str:
        """生成刷新令牌"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.refresh_tokens[user_id] = token
        return token
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """使用刷新令牌获取新的访问令牌"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                raise Exception("无效的刷新令牌")
            
            user_id = payload['user_id']
            if self.refresh_tokens.get(user_id) != refresh_token:
                raise Exception("刷新令牌已失效")
            
            # 生成新的访问令牌
            new_payload = {'user_id': user_id, 'type': 'access'}
            return jwt_manager.generate_token(new_payload, expires_in=3600)
            
        except jwt.ExpiredSignatureError:
            raise Exception("刷新令牌已过期")
        except jwt.InvalidTokenError:
            raise Exception("无效的刷新令牌")

# 使用示例
refresh_manager = RefreshTokenManager(secret_key="refresh-secret")

# 生成刷新令牌
refresh_token = refresh_manager.generate_refresh_token(user_id=123)

# 使用刷新令牌获取新的访问令牌
try:
    new_access_token = refresh_manager.refresh_access_token(refresh_token)
    print(f"新访问令牌: {new_access_token}")
except Exception as e:
    print(f"刷新失败: {e}")
```

### Express.js中间件实现
```javascript
const jwt = require('jsonwebtoken');

class JWTAuthMiddleware {
    constructor(secretKey) {
        this.secretKey = secretKey;
    }

    // 生成令牌
    generateToken(payload, expiresIn = '1h') {
        return jwt.sign(payload, this.secretKey, { expiresIn });
    }

    // 验证中间件
    authenticate() {
        return (req, res, next) => {
            const token = this.extractToken(req);
            
            if (!token) {
                return res.status(401).json({ error: '未提供令牌' });
            }

            try {
                const decoded = jwt.verify(token, this.secretKey);
                req.user = decoded;
                next();
            } catch (error) {
                if (error.name === 'TokenExpiredError') {
                    return res.status(401).json({ error: '令牌已过期' });
                } else if (error.name === 'JsonWebTokenError') {
                    return res.status(401).json({ error: '无效令牌' });
                } else {
                    return res.status(500).json({ error: '令牌验证失败' });
                }
            }
        };
    }

    // 角色授权中间件
    authorize(roles) {
        return (req, res, next) => {
            if (!req.user) {
                return res.status(401).json({ error: '未认证用户' });
            }

            if (!roles.includes(req.user.role)) {
                return res.status(403).json({ error: '权限不足' });
            }

            next();
        };
    }

    // 提取令牌
    extractToken(req) {
        const authHeader = req.headers.authorization;
        if (authHeader && authHeader.startsWith('Bearer ')) {
            return authHeader.substring(7);
        }
        return null;
    }
}

// 使用示例
const auth = new JWTAuthMiddleware(process.env.JWT_SECRET);

// 路由保护
app.get('/api/profile', auth.authenticate(), (req, res) => {
    res.json({ user: req.user });
});

// 角色限制
app.post('/api/admin', 
    auth.authenticate(), 
    auth.authorize(['admin']), 
    (req, res) => {
        res.json({ message: '管理员访问成功' });
    }
);
```

## 最佳实践

### 安全配置
1. **强密钥管理**: 使用足够长度的随机密钥
2. **算法选择**: 优先使用RS256等非对称算法
3. **令牌过期**: 设置合理的过期时间
4. **HTTPS传输**: 始终通过HTTPS传输令牌
5. **密钥轮换**: 定期更换签名密钥

### 性能优化
1. **令牌缓存**: 缓存已验证的令牌信息
2. **载荷精简**: 只包含必要的信息
3. **异步验证**: 在高并发场景下使用异步验证
4. **分层验证**: 根据资源敏感度分层验证

### 错误处理
1. **统一错误格式**: 提供清晰的错误信息
2. **日志记录**: 记录验证失败和异常情况
3. **优雅降级**: 在验证服务不可用时提供备选方案
4. **监控告警**: 监控异常验证模式

## 相关技能

- **api-validator** - API验证与设计
- **error-handling-logging** - 错误处理与日志
- **data-validation** - 数据验证与序列化
- **caching-strategies** - 缓存策略与实现
- **security** - 安全最佳实践
