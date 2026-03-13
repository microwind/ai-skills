---
name: API验证器
description: "当验证API实现、检查REST约定、分析API设计或调试API问题时使用。验证API结构、设计和最佳实践。"
license: MIT
---

# API验证器技能

## 概述
API是系统之间的契约。无效或设计不当的API会导致集成问题、错误和性能问题。在实施前验证API设计。

**核心原则**: 好的API设计让集成变得简单。坏的API设计让集成变得痛苦。在设计问题造成集成地狱之前修复它们。

## 何时使用

**始终:**
- 在实施新API之前
- 在代码审查期间验证API设计
- 检查REST约定
- 审查API结构
- 规划API变更或迁移
- 调试集成问题
- 当客户端报告集成问题时

**触发短语:**
- "这个API设计好吗？"
- "检查REST约定"
- "验证API结构"
- "这个端点应该如何工作？"
- "审查API设计"
- "为什么这个客户端无法集成？"
- "设计一个新的API端点"

## API验证器功能

### 设计分析
- REST约定合规性（GET/POST/PUT/DELETE/PATCH）
- 端点命名一致性
- HTTP方法正确性
- 状态码使用（200, 201, 400, 404, 500）
- 请求/响应结构一致性
- 头部管理（Content-Type, Authorization）
- 版本控制策略

### 反模式检测
- 受保护端点缺少身份验证
- 错误处理差（模糊的错误消息）
- 端点间命名不一致
- 过于复杂的端点（参数太多）
- 缺少版本控制（破坏性变更）
- RPC风格端点（非RESTful）
- 混合关注点（数据+导航）

### 最佳实践检查
- 一致的响应格式（JSON结构）
- 正确的错误响应格式
- API文档完整性
- 速率限制设计
- 分页实现
- 缓存头部（ETag, Cache-Control）
- 适当情况下的HATEOAS链接

## 常见API设计问题

### 错误的HTTP方法
```
问题:
POST /users/delete/123  ❌ 使用POST进行删除
GET /users/create       ❌ 使用GET进行创建
PUT /users              ❌ 使用PUT进行部分更新

后果:
- 客户端对用法感到困惑
- 缓存破坏（GET应该是幂等的）
- REST工具无法识别模式
- 难以文档化和测试

解决方案:
DELETE /users/123       ✓ 清晰的意图
POST /users             ✓ 创建新资源
PATCH /users/123        ✓ 部分更新（或PUT用于完整更新）
```

### 不一致的命名
```
问题:
GET /users              ✓
GET /all_products       ❌ 不一致的命名
POST /add_item          ❌ URL中的动词
GET /getUserById        ❌ 不一致的风格

后果:
- 难以记住端点结构
- 客户端必须不断查看文档
- 容易出错
- 不是自文档化的

解决方案:
GET /users              ✓ 一致
GET /products           ✓ 一致
POST /items             ✓ 一致
GET /users/123          ✓ ID的一致模式
```

### 缺少版本控制
```
问题:
/api/users              ❌ 没有版本 - 破坏性变更会破坏所有客户端
POST /users body: {name, email}  ❌ 后来添加必填字段，破坏旧客户端

后果:
- 无法演进API
- 破坏性变更影响所有人
- 无法保持向后兼容性
- 客户端困在旧版本

解决方案:
/api/v1/users           ✓ 清晰的版本
/api/v2/users           ✓ 用于不兼容变更的新版本
Accept: application/vnd.api+json;version=2  ✓ 基于头部的版本控制
```

### 差的错误响应
```
问题:
"error": "Something went wrong"        ❌ 模糊 - 出了什么问题？
HTTP 500 for validation error          ❌ 错误的状态码
No error codes / only message            ❌ 难以程序化处理

后果:
- 客户端无法正确处理错误
- 难以调试集成问题
- 用户体验差
- 无法智能重试

解决方案:
{
  "error": "validation_error",
  "message": "Email is required",
  "field": "email",
  "code": 400
}
✓ 清晰、具体、可操作
```

### 缺少身份验证/授权
```
问题:
GET /admin/users        ❌ 没有身份验证检查
POST /payments          ❌ 任何用户都可以访问
DELETE /users/123       ❌ 用户可以删除其他用户

后果:
- 安全漏洞
- 数据泄露
- 未授权访问
- 合规性违规

解决方案:
要求授权头部
检查用户权限
记录安全要求
使用OAuth/JWT令牌
```

## 验证检查清单

**RESTful设计:**
- [ ] 每个操作使用正确的HTTP方法（GET, POST, PUT, PATCH, DELETE）
- [ ] 所有端点遵循`/resource`或`/resource/id/subresource`模式
- [ ] URL中没有动词（例如，不是`/getUser`或`/deleteUser`）
- [ ] 没有RPC风格端点（例如，不是`/api.php?method=user.get`）
- [ ] 端点间命名一致（复数名词，小写）
- [ ] HTTP状态码正确（200, 201, 400, 404, 500）
- [ ] 响应格式一致（所有返回相同JSON结构）
- [ ] 错误响应包含：代码、消息、详情

**API成熟度:**
- [ ] API版本控制策略已记录
- [ ] 身份验证/授权要求清晰
- [ ] 速率限制已记录
- [ ] 列表端点已实现分页
- [ ] 过滤/排序选项已记录
- [ ] 旧端点的弃用路径
- [ ] 破坏性变更已处理（版本控制）
- [ ] CORS头部已记录（如适用）

**文档:**
- [ ] 每个端点都有示例记录
- [ ] 请求/响应模式已记录
- [ ] 错误代码和消息已记录
- [ ] 身份验证方法已记录
- [ ] 速率限制已记录
- [ ] 提供了示例curl/代码片段

## 如何使用

### 基础API设计审查
```
审查你的API端点：
1. 将所有端点映射到HTTP方法
2. 检查每个使用正确的方法（GET/POST/PUT/PATCH/DELETE）
3. 验证命名一致
4. 检查状态码是否适当
5. 确保错误响应一致

示例：
✓ GET /api/v1/users (列表)
✓ GET /api/v1/users/123 (获取一个)
✓ POST /api/v1/users (创建)
✓ PATCH /api/v1/users/123 (更新)
✓ DELETE /api/v1/users/123 (删除)

所有都使用一致的命名、正确的方法、可预测的结构。
```

## 遇到困难时

| 问题 | 解决方案 |
|---------|----------|
| "我应该使用PUT还是PATCH？" | PUT替换整个资源，PATCH部分更新。更新时使用PATCH。 |
| "如何为API版本控制？" | 在URL或Accept头部中使用/api/v1/、/api/v2/。从一开始就规划版本控制。 |
| "应该使用什么状态码？" | 200（成功）、201（已创建）、400（错误请求）、404（未找到）、500（服务器错误）。 |
| "如何处理错误？" | 一致格式：{代码、消息、详情}。使用HTTP状态码进行分类。 |
| "客户端无法集成 - 为什么？" | 检查：方法正确、端点路径已记录、身份验证正常工作、响应格式与文档匹配。 |
| "破坏性变更 - 怎么办？" | 创建新版本（/v2/）。保持旧版本正常工作。记录迁移路径。 |

## 反模式（红旗警告）

**❌ RPC风格API（非RESTful）**
```
GET /api/getUser?id=123
GET /api/deleteUser?id=123
POST /api/createUser
↓
难以理解、非RESTful、令人困惑
```

**❌ 不一致的命名**
```
GET /users
GET /all_products
POST /add_item
DELETE /removeUser/123
↓
无法预测端点结构，难以记住
```

**❌ 错误的HTTP方法**
```
POST /users/delete/123
GET /users/create
PUT /users/123 (当你需要部分更新时)
↓
破坏缓存、混淆工具、违反REST
```

**❌ 没有错误结构**
```
响应: "Error: Something went wrong"
没有错误代码、没有详情、模糊消息
↓
客户端无法正确处理错误
```

**❌ 缺少身份验证**
```
POST /admin/users (没有身份验证检查)
DELETE /users/123 (任何用户都可以删除任何用户)
GET /payments (敏感数据暴露)
↓
安全漏洞
```

**❌ 没有版本控制**
```
/api/users
后来在POST正文中添加必填字段
所有旧客户端立即破坏
↓
无法安全地演进API
```

## 相关技能

- **security-scanner** - 检查API安全和身份验证
- **code-review** - 审查API实现
- **api-tester** - 测试API端点正常工作
- **request-debugger** - 调试API请求/响应问题
