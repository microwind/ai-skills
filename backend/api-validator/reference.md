# API验证器参考文档

## REST API设计规范

### URL设计原则

#### 资源命名规范
- **使用名词而非动词**: 
  - ✅ `/users` (正确)
  - ❌ `/getUsers` (错误)
- **使用复数形式**:
  - ✅ `/products` (正确)
  - ❌ `/product` (错误)
- **使用小写字母和连字符**:
  - ✅ `/user-profiles` (正确)
  - ❌ `/userProfiles` (错误)
- **避免深层嵌套**:
  - ✅ `/users/123/orders` (推荐)
  - ❌ `/users/123/orders/456/items/789` (过深)

#### 资源关系表达
- **一对多关系**: `/users/{userId}/orders`
- **多对多关系**: `/users/{userId}/roles` 或 `/roles/{roleId}/users`
- **子资源**: `/orders/{orderId}/items`
- **集合操作**: `/users/batch`, `/orders/bulk`

### HTTP方法使用指南

#### 标准方法映射
| 方法 | 操作 | 幂等性 | 安全性 | 示例 |
|------|------|--------|--------|------|
| GET | 获取资源 | ✅ | ✅ | GET /users |
| POST | 创建资源 | ❌ | ❌ | POST /users |
| PUT | 完整更新 | ✅ | ❌ | PUT /users/123 |
| PATCH | 部分更新 | ❌ | ❌ | PATCH /users/123 |
| DELETE | 删除资源 | ✅ | ❌ | DELETE /users/123 |

#### 特殊场景处理
- **批量操作**: 
  - POST `/users/batch` (批量创建)
  - DELETE `/users/batch` (批量删除)
- **资源状态变更**:
  - POST `/orders/123/confirm` (确认订单)
  - POST `/users/123/activate` (激活用户)
- **查询和过滤**:
  - GET `/users?status=active&role=admin`
  - GET `/users?sort=name&order=asc`

### 状态码使用规范

#### 成功状态码 (2xx)
- **200 OK**: 请求成功，返回资源
- **201 Created**: 资源创建成功，返回新资源
- **202 Accepted**: 请求已接受，异步处理中
- **204 No Content**: 请求成功，无返回内容
- **206 Partial Content**: 部分内容返回 (分页)

#### 客户端错误 (4xx)
- **400 Bad Request**: 请求参数错误
- **401 Unauthorized**: 未认证
- **403 Forbidden**: 无权限
- **404 Not Found**: 资源不存在
- **405 Method Not Allowed**: 方法不支持
- **409 Conflict**: 资源冲突
- **422 Unprocessable Entity**: 请求格式正确但语义错误
- **429 Too Many Requests**: 请求频率限制

#### 服务器错误 (5xx)
- **500 Internal Server Error**: 服务器内部错误
- **502 Bad Gateway**: 网关错误
- **503 Service Unavailable**: 服务不可用
- **504 Gateway Timeout**: 网关超时

## 请求/响应格式标准

### 请求格式规范

#### 请求头设置
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
User-Agent: MyApp/1.0
```

#### 请求体结构
```json
{
  "data": {
    "type": "user",
    "attributes": {
      "name": "张三",
      "email": "zhangsan@example.com"
    },
    "relationships": {
      "profile": {
        "data": { "type": "profile", "id": "123" }
      }
    }
  }
}
```

#### 分页参数
```json
{
  "page": {
    "number": 1,
    "size": 20
  },
  "sort": "name,-createdAt",
  "filter": {
    "status": "active",
    "role": "admin"
  }
}
```

### 响应格式规范

#### 成功响应
```json
{
  "data": {
    "id": "123",
    "type": "user",
    "attributes": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "createdAt": "2024-01-01T00:00:00Z"
    },
    "relationships": {
      "profile": {
        "links": {
          "self": "/users/123/profile",
          "related": "/profiles/123"
        }
      }
    }
  },
  "meta": {
    "version": "1.0",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### 分页响应
```json
{
  "data": [...],
  "links": {
    "self": "/users?page[number]=1&page[size]=20",
    "first": "/users?page[number]=1&page[size]=20",
    "prev": null,
    "next": "/users?page[number]=2&page[size]=20",
    "last": "/users?page[number]=10&page[size]=20"
  },
  "meta": {
    "total": 200,
    "page": 1,
    "size": 20,
    "totalPages": 10
  }
}
```

#### 错误响应
```json
{
  "errors": [
    {
      "id": "error-123",
      "status": "400",
      "code": "VALIDATION_ERROR",
      "title": "请求参数验证失败",
      "detail": "邮箱格式不正确",
      "source": {
        "pointer": "/data/attributes/email"
      },
      "meta": {
        "field": "email",
        "value": "invalid-email"
      }
    }
  ],
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "req-456"
  }
}
```

## 安全性最佳实践

### 认证和授权

#### JWT Token格式
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "sub": "1234567890",
  "name": "张三",
  "role": "admin",
  "exp": 1516239022
}
```

#### 认证头格式
```http
Authorization: Bearer <jwt_token>
```

#### 权限控制
- **基于角色的访问控制 (RBAC)**:
  ```
  GET /users - admin, manager
  POST /users - admin
  PUT /users/{id} - admin, owner
  DELETE /users/{id} - admin
  ```
- **基于资源的访问控制**:
  ```
  GET /users/{id} - owner, admin
  PUT /users/{id} - owner
  ```

### 输入验证

#### 数据类型验证
- **字符串**: 长度限制、格式检查、特殊字符过滤
- **数字**: 范围检查、精度验证
- **日期**: 格式验证、范围检查
- **邮箱**: 正则表达式验证
- **URL**: 格式验证、域名检查

#### 安全检查项
- **SQL注入防护**: 使用参数化查询
- **XSS防护**: 输入过滤、输出编码
- **CSRF防护**: CSRF Token验证
- **文件上传**: 类型检查、大小限制、病毒扫描

## 版本控制策略

### 版本控制方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| URL路径版本 | 直观明确 | URL冗长 | 公共API |
| 查询参数版本 | 灵活可选 | 不够正式 | 内部API |
| 请求头版本 | URL简洁 | 不够直观 | 企业级API |
| 无版本控制 | 简单 | 兼容性差 | 简单API |

### 版本兼容性原则
- **向后兼容**: 新版本兼容旧版本客户端
- **渐进迁移**: 提供迁移期和废弃通知
- **明确生命周期**: 版本发布、维护、废弃时间表

## 性能优化指南

### 响应时间优化
- **数据库查询优化**: 索引使用、查询优化
- **缓存策略**: Redis缓存、CDN缓存
- **异步处理**: 长时间操作异步化
- **分页优化**: 游标分页、限制返回字段

### 资源使用优化
- **压缩**: Gzip压缩、响应体压缩
- **连接池**: 数据库连接池、HTTP连接池
- **批处理**: 批量操作、事务优化
- **监控**: 性能指标收集、告警设置

## 常见问题和解决方案

### 设计问题
- **过度嵌套**: 扁平化设计、资源分离
- **命名不一致**: 统一命名规范、术语表
- **状态码滥用**: 正确使用HTTP状态码
- **版本混乱**: 明确版本策略、迁移计划

### 实现问题
- **错误处理不统一**: 标准错误格式、错误码体系
- **安全性缺失**: 认证授权、输入验证
- **性能问题**: 缓存策略、查询优化
- **文档不完整**: 自动生成文档、示例代码

## 工具和资源

### API测试工具
- **Postman**: API测试和文档
- **Insomnia**: 轻量级API客户端
- **curl**: 命令行HTTP客户端
- **httpie**: 用户友好的HTTP客户端

### 验证工具
- **OpenAPI Specification**: API规范标准
- **Swagger Editor**: API设计工具
- **API Blueprint**: API文档格式
- **Dredd**: API文档测试工具

### 监控工具
- **Prometheus**: 指标收集
- **Grafana**: 可视化监控
- **ELK Stack**: 日志分析
- **New Relic**: APM监控

### 参考文档
- **REST API Design Guide**: Microsoft REST API指南
- **HTTP/1.1 RFC**: HTTP协议标准
- **JSON API**: JSON API规范
- **OpenAPI Specification**: API规范标准
