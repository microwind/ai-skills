---
name: 一致性原则
description: "在整个系统中保持设计、命名、模式和行为的一致性，降低认知负担，提高可维护性。"
license: MIT
---

# 一致性原则 (Consistency Principle)

## 概述

一致性原则：**相似的问题用相似的方式解决，相同的概念用相同的名称表达**。一致性降低了认知负担，让开发者能凭直觉理解新代码。

**一致性维度**：
- **命名一致** - 相同概念用相同的词
- **模式一致** - 相似问题用相同的设计模式
- **风格一致** - 代码格式、结构统一
- **行为一致** - 相似的API有相似的行为

## 命名一致性

```java
// ❌ 不一致的命名
public class UserService {
    public User getUser(Long id);           // get
    public Order fetchOrder(Long id);       // fetch
    public Product retrieveProduct(Long id); // retrieve
    public Invoice findInvoice(Long id);    // find
    // 四个不同的词表达同一含义
}

// ✅ 一致命名
public class UserService {
    public User findById(Long id);
}
public class OrderService {
    public Order findById(Long id);
}
public class ProductService {
    public Product findById(Long id);
}
```

```python
# ❌ 不一致的错误处理
class UserService:
    def create_user(self, data):
        return None  # 失败返回 None

class OrderService:
    def create_order(self, data):
        raise ValueError("创建失败")  # 失败抛异常

class PaymentService:
    def create_payment(self, data):
        return {"success": False, "error": "失败"}  # 失败返回错误对象

# ✅ 一致的错误处理策略
# 团队约定：业务异常统一抛自定义异常
class UserService:
    def create_user(self, data):
        if not data.get("email"):
            raise ValidationError("邮箱不能为空")

class OrderService:
    def create_order(self, data):
        if not data.get("items"):
            raise ValidationError("订单项不能为空")
```

## 模式一致性

```typescript
// ✅ 所有 API 端点遵循相同的模式
// 请求格式一致
interface ApiResponse<T> {
    code: number;
    data: T;
    message: string;
}

// 错误处理一致
app.get('/api/users/:id', async (req, res) => {
    const user = await userService.findById(req.params.id);
    if (!user) return res.status(404).json({ code: 404, data: null, message: '用户不存在' });
    return res.json({ code: 200, data: user, message: 'ok' });
});

app.get('/api/orders/:id', async (req, res) => {
    const order = await orderService.findById(req.params.id);
    if (!order) return res.status(404).json({ code: 404, data: null, message: '订单不存在' });
    return res.json({ code: 200, data: order, message: 'ok' });
});
```

## 一致性检查清单

```
□ 相同操作在不同模块中用相同的方法名
□ 错误处理策略全项目统一
□ API 响应格式统一
□ 日志格式和级别使用规范一致
□ 目录结构在各模块间一致
□ 数据库命名规范一致（snake_case vs camelCase）
□ 时间格式统一（UTC vs 本地时区）
□ 配置方式统一（环境变量 vs 配置文件）
```

## 何时打破一致性

```
✅ 有充分理由时可以例外：
- 性能瓶颈要求特殊实现
- 第三方库强制了不同的模式
- 新的最佳实践明显优于现有惯例

⚠️ 打破一致性时：
- 记录原因（ADR 或代码注释）
- 通知团队
- 评估是否应该全局迁移到新模式
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [KISS](../kiss-principle/) | 一致性降低认知负担，保持简单 |
| [DRY](../dry-principle/) | 模式一致有助于发现和消除重复 |
| [最少知识](../least-knowledge-principle/) | 一致的接口减少需要了解的知识 |

## 总结

**一致性核心**：相似问题用相似方案，降低认知负担。

**实践要点**：
- 建立并遵循团队编码规范
- 命名、模式、错误处理全项目统一
- 新代码参考现有代码的模式
- 有充分理由时可以例外，但需记录
