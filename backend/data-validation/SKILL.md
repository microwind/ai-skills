---
name: 数据验证与序列化
description: "当处理数据验证和序列化时，分析验证策略，优化数据完整性，解决数据格式问题。验证数据架构，设计验证规则，和最佳实践。"
license: MIT
---

# 数据验证与序列化技能

## 概述
数据验证是保证系统数据完整性和安全性的重要环节。不当的验证策略会导致数据错误、安全漏洞和系统异常。在数据处理前需要建立完善的验证机制。

**核心原则**: 好的验证策略应该保证数据的正确性和完整性，同时提供清晰的错误信息。坏的验证策略会导致数据污染和安全问题。

## 何时使用

**始终:**
- 设计API接口时
- 处理用户输入数据时
- 数据库操作前验证时
- 配置文件解析时
- 文件上传处理时
- 第三方数据集成时

**触发短语:**
- "这个数据需要验证吗？"
- "如何验证用户输入？"
- "数据格式不对怎么办？"
- "序列化失败怎么处理？"
- "如何防止SQL注入？"
- "数据验证报错了"

## 数据验证技能功能

### 验证策略分析
- 输入验证（前端和后端）
- 数据类型验证
- 业务逻辑验证
- 安全性验证
- 数据完整性检查

### 序列化模式
- JSON序列化/反序列化
- XML数据处理
- 二进制数据编码
- 自定义序列化格式
- 版本兼容性处理

### 安全问题检测
- SQL注入漏洞
- XSS攻击防护
- CSRF令牌验证
- 数据泄露风险
- 恶意文件上传

## 常见验证问题

### 输入验证缺失
```
问题:
直接使用用户输入，未进行验证

后果:
- SQL注入攻击
- 数据格式错误
- 系统异常崩溃
- 安全漏洞

解决方案:
- 白名单验证
- 类型检查
- 长度限制
- 特殊字符过滤
```

### 序列化漏洞
```
问题:
不安全的反序列化操作

后果:
- 远程代码执行
- 数据泄露
- 拒绝服务攻击
- 权限提升

解决方案:
- 使用安全的序列化库
- 验证序列化数据
- 限制反序列化类
- 数字签名验证
```

### 数据类型错误
```
问题:
数据类型不匹配或转换错误

后果:
- 数据库操作失败
- 计算结果错误
- 业务逻辑异常
- 数据丢失

解决方案:
- 严格类型检查
- 安全的类型转换
- 默认值处理
- 异常捕获机制
```

## 验证策略选择

### Web API验证
**推荐策略**: 分层验证 + 统一错误处理
```
验证层次:
1. 参数类型验证
2. 数据格式验证  
3. 业务逻辑验证
4. 权限验证

实现要点:
- 使用验证框架
- 自定义验证规则
- 统一错误响应格式
- 详细的错误信息
```

### 数据库操作验证
**推荐策略**: ORM验证 + 数据库约束
```
验证内容:
- 主键外键约束
- 数据类型约束
- 唯一性约束
- 检查约束

实现要点:
- 模型层验证
- 数据库层约束
- 事务完整性
- 回滚机制
```

### 文件上传验证
**推荐策略**: 多重检查 + 安全扫描
```
检查项目:
- 文件类型验证
- 文件大小限制
- 文件内容扫描
- 病毒检测

实现要点:
- 扩展名白名单
- MIME类型检查
- 文件头验证
- 隔离存储
```

## 验证技术选型

### Python验证框架
| 框架 | 特点 | 适用场景 |
|------|------|----------|
| Pydantic | 类型注解、性能好 | FastAPI、数据模型 |
| Marshmallow | 灵活、功能丰富 | Django、复杂验证 |
| Cerberus | 轻量级、简单 | 小项目、基础验证 |
| Django Forms | 内置、集成度高 | Django项目 |

### JavaScript验证库
| 库 | 特点 | 适用场景 |
|------|------|----------|
| Joi | 功能强大、灵活 | Node.js后端 |
| Yup | 简单易用 | React前端 |
| Zod | TypeScript友好 | 全栈开发 |
| Validator.js | 轻量级 | 浏览器端 |

## 验证最佳实践

### 验证原则
1. **白名单优先**: 只允许已知安全的数据
2. **多层验证**: 前端、后端、数据库都要验证
3. **统一错误**: 提供一致的错误响应格式
4. **最小权限**: 验证通过后再授权操作
5. **日志记录**: 记录验证失败和异常情况

### 代码示例
```python
# 使用Pydantic进行数据验证
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re

class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('用户名至少3个字符')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少8个字符')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v

# 使用示例
try:
    user_data = UserCreateSchema(
        username="john_doe",
        email="john@example.com", 
        password="SecurePass123",
        age=25
    )
    print("验证通过:", user_data.dict())
except ValueError as e:
    print("验证失败:", e)

# SQL注入防护
def safe_query(user_id: int):
    """安全的数据库查询"""
    # 使用参数化查询
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))

# XSS防护
def sanitize_html(content: str) -> str:
    """清理HTML内容，防止XSS"""
    import bleach
    # 只允许安全的HTML标签
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
    return bleach.clean(content, tags=allowed_tags)
```

## 错误处理策略

### 错误分类
- **验证错误**: 400 Bad Request
- **权限错误**: 401/403 Forbidden  
- **资源错误**: 404 Not Found
- **服务器错误**: 500 Internal Server Error

### 错误响应格式
```json
{
  "error": "validation_error",
  "message": "输入数据验证失败",
  "details": {
    "username": ["用户名至少3个字符"],
    "email": ["邮箱格式不正确"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 性能优化

### 验证性能
- 使用编译的正则表达式
- 缓存验证规则
- 异步验证处理
- 批量验证优化

### 序列化性能
- 选择合适的序列化格式
- 压缩大数据
- 流式处理
- 缓存序列化结果

## 相关技能

- **api-validator** - API接口验证
- **security-scanner** - 安全漏洞扫描
- **error-handling-logging** - 错误处理和日志
- **file-upload** - 文件上传处理
