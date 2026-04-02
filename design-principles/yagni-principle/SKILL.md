---
name: YAGNI原则
description: "You Aren't Gonna Need It - 不要实现当前不需要的功能。专注于当前需求，避免推测性设计。"
license: MIT
---

# YAGNI 原则 (You Aren't Gonna Need It)

## 概述

YAGNI 源自极限编程(XP)：**永远不要因为"将来可能需要"而实现当前不需要的功能**。

**核心思想**：
- 只实现当前确定需要的功能
- 不要为假想的未来需求而设计
- 推测性代码的维护成本远大于它的价值
- 当需求真正出现时再实现，届时你会有更好的理解

**推测性代码的真实代价**：
- 编写时间：N 小时
- 测试时间：N 小时
- 维护成本：持续
- 实际被用到的概率：< 30%

## 过度设计示例

```java
// ❌ YAGNI 违反：当前只需要支持 MySQL
public interface DatabaseDriver {
    void connect(String url);
    void disconnect();
    ResultSet query(String sql);
}

public class MySQLDriver implements DatabaseDriver { /* ... */ }
public class PostgreSQLDriver implements DatabaseDriver { /* ... */ }  // 不需要
public class MongoDBDriver implements DatabaseDriver { /* ... */ }    // 不需要
public class OracleDriver implements DatabaseDriver { /* ... */ }     // 不需要

public class DatabaseDriverFactory {
    public static DatabaseDriver create(String type) { /* ... */ }
}

// ✅ YAGNI：只实现需要的
public class MySQLDatabase {
    public void connect(String url) { /* ... */ }
    public ResultSet query(String sql) { /* ... */ }
}
// 当真正需要支持 PostgreSQL 时再抽象接口
```

```python
# ❌ 过度设计：配置系统支持多种格式
class ConfigLoader:
    def load(self, path: str) -> dict:
        if path.endswith('.json'):
            return self._load_json(path)
        elif path.endswith('.yaml'):
            return self._load_yaml(path)
        elif path.endswith('.toml'):
            return self._load_toml(path)
        elif path.endswith('.xml'):
            return self._load_xml(path)
        elif path.endswith('.ini'):
            return self._load_ini(path)
        # 实际项目只用了 JSON...

# ✅ YAGNI
import json

def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
```

```typescript
// ❌ 过度设计：为了"灵活性"的过度抽象
interface EventBus {
    subscribe(event: string, handler: EventHandler): void;
    publish(event: string, data: any): void;
    unsubscribe(event: string, handler: EventHandler): void;
}

interface EventHandler {
    handle(data: any): void;
    priority(): number;
    filter(data: any): boolean;
}

interface EventMiddleware {
    before(event: string, data: any): any;
    after(event: string, result: any): void;
}

// 实际只需要：用户注册后发邮件

// ✅ YAGNI
class UserService {
    constructor(private emailService: EmailService) {}

    async register(data: CreateUserDTO) {
        const user = await this.createUser(data);
        await this.emailService.sendWelcome(user.email);
        return user;
    }
}
```

## 何时需要提前设计

```
YAGNI ≠ 不做设计。以下情况需要提前考虑：

✅ 需要提前设计的：
- 数据库 schema（后期迁移代价大）
- 公开 API 接口（发布后难以修改）
- 安全机制（事后补救代价大）
- 核心架构决策（推倒重来代价大）

❌ 不需要提前实现的：
- "可能需要"的功能
- "将来可能"的数据库切换
- "也许会用到"的导出格式
- "以防万一"的配置选项
```

## 判断方法

```
问自己：
1. 有明确的需求文档/用户故事要求这个功能吗？
   → 没有 = YAGNI

2. 如果不做这个，当前迭代的功能完整吗？
   → 完整 = YAGNI

3. 这个"提前设计"的成本是多少？不做的话将来补上的成本是多少？
   → 提前成本 > 将来成本 × 发生概率 = YAGNI

4. 团队成员都理解为什么需要这个吗？
   → 只有你觉得需要 = 很可能 YAGNI
```

## 优缺点分析

### ✅ 优点
1. **更快交付** - 只做必要的事
2. **更少代码** - 维护负担轻
3. **更少 bug** - 代码越少 bug 越少
4. **更灵活** - 没有错误抽象的负担
5. **需求更清晰** - 真正需要时理解更深

### ❌ 风险
1. **技术债务** - 可能需要后期重构
2. **架构限制** - 某些决策确实需要提前
3. **误解为偷懒** - 需要与过度简化区分

## 最佳实践

### 1. 迭代式开发

```
Sprint 1: 用户只能用邮箱密码登录
Sprint 2: 需求确认后，添加 OAuth 登录
Sprint 3: 需求确认后，添加 SSO 登录

而不是：
Sprint 1: 设计支持 N 种登录方式的通用认证框架
         （过度设计，3 种中可能只用到 1 种）
```

### 2. 推迟决策到最后责任时刻

```
"最后责任时刻"= 再不决定就会失去重要选项的时刻

示例：
- 数据库选型：在了解实际数据模式后决定
- 缓存策略：在性能测试暴露瓶颈后添加
- 微服务拆分：在单体遇到实际扩展问题后拆分
```

### 3. 区分复杂性类型

| 类型 | 示例 | 态度 |
|------|------|------|
| 必要复杂性 | 业务本身复杂 | 接受 |
| 偶然复杂性 | 技术选型引入 | 最小化 |
| 推测复杂性 | "将来可能需要" | 消除 |

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [KISS](../kiss-principle/) | KISS 关注怎么做简单，YAGNI 关注做不做 |
| [OCP](../open-closed-principle/) | OCP 提倡可扩展设计，YAGNI 提醒不要过度扩展 |
| [DRY](../dry-principle/) | 不要为了 DRY 而提前创建"将来可能用到"的抽象 |

## 总结

**YAGNI 核心**：不要实现当前不需要的功能。

**实践要点**：
- 只实现有明确需求的功能
- 推迟决策到信息最充分的时刻
- 区分"必须提前设计"和"可以推迟实现"
- 接受将来可能的重构，这通常比过度设计便宜
- "最好的代码是你不用写的代码"
