---
name: 关注点分离
description: "将程序分解为不同的部分，每个部分处理一个单独的关注点，减少耦合提高内聚。"
license: MIT
---

# 关注点分离 (Separation of Concerns, SoC)

## 概述

关注点分离由 Dijkstra 于1974年提出：**将系统分解为不同的部分，每个部分解决一个独立的关注点**。

**核心思想**：
- 每个模块/层/组件只负责一个关注点
- 不同关注点之间通过明确的接口交互
- 修改一个关注点不应该影响其他关注点

## 经典应用：MVC 模式

```java
// ✅ 关注点分离：Model-View-Controller

// Model：只关注数据和业务逻辑
public class User {
    private String name;
    private String email;

    public boolean isValid() {
        return name != null && !name.isEmpty()
            && email != null && email.contains("@");
    }
}

// Controller：只关注请求处理和流程协调
public class UserController {
    private final UserService service;
    private final UserView view;

    public Response handleCreate(Request request) {
        User user = service.create(request.getBody());
        return view.render(user);
    }
}

// View：只关注数据展示
public class UserView {
    public Response render(User user) {
        return Response.json(Map.of("name", user.getName()));
    }
}
```

## 违反 SoC 的示例

```python
# ❌ 混合关注点：业务逻辑 + 数据访问 + 展示
class OrderProcessor:
    def process(self, order_data: dict):
        # 关注点1：数据验证
        if not order_data.get("items"):
            print("错误：订单为空")  # 展示逻辑混入
            return

        # 关注点2：业务逻辑
        total = sum(i["price"] * i["qty"] for i in order_data["items"])
        if total > 10000:
            total *= 0.9

        # 关注点3：数据持久化
        import sqlite3
        conn = sqlite3.connect("orders.db")
        conn.execute("INSERT INTO orders VALUES (?, ?)",
                     (order_data["id"], total))
        conn.commit()

        # 关注点4：通知
        import smtplib
        server = smtplib.SMTP("smtp.example.com")
        server.sendmail("shop@example.com", order_data["email"],
                        f"订单已处理，总计: {total}")

# ✅ 关注点分离
class OrderValidator:
    def validate(self, order_data: dict) -> bool:
        return bool(order_data.get("items"))

class PricingService:
    def calculate(self, items: list) -> float:
        total = sum(i["price"] * i["qty"] for i in items)
        return total * 0.9 if total > 10000 else total

class OrderRepository:
    def save(self, order_id: str, total: float):
        # 数据库操作
        pass

class NotificationService:
    def notify(self, email: str, message: str):
        # 邮件发送
        pass

class OrderProcessor:
    def __init__(self, validator, pricing, repo, notifier):
        self.validator = validator
        self.pricing = pricing
        self.repo = repo
        self.notifier = notifier

    def process(self, order_data: dict):
        if not self.validator.validate(order_data):
            raise ValueError("无效订单")
        total = self.pricing.calculate(order_data["items"])
        self.repo.save(order_data["id"], total)
        self.notifier.notify(order_data["email"], f"总计: {total}")
```

## 分层架构中的 SoC

```
┌─────────────────────────┐
│   Presentation Layer    │  关注点：用户交互、数据展示
├─────────────────────────┤
│   Application Layer     │  关注点：用例编排、事务管理
├─────────────────────────┤
│   Domain Layer          │  关注点：业务规则、领域逻辑
├─────────────────────────┤
│   Infrastructure Layer  │  关注点：数据库、外部服务、框架
└─────────────────────────┘

规则：上层依赖下层，下层不知道上层的存在
```

## 前端中的 SoC

```typescript
// ❌ 关注点混合
function UserProfile() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        // 数据获取逻辑混在组件中
        fetch('/api/users/1')
            .then(res => res.json())
            .then(data => {
                // 业务逻辑混在组件中
                data.fullName = `${data.firstName} ${data.lastName}`;
                data.age = new Date().getFullYear() - data.birthYear;
                setUser(data);
            });
    }, []);

    // 展示逻辑
    return <div>{user?.fullName}, {user?.age}岁</div>;
}

// ✅ 关注点分离
// hooks/useUser.ts - 数据获取
function useUser(id: string) {
    const [user, setUser] = useState(null);
    useEffect(() => {
        fetch(`/api/users/${id}`).then(r => r.json()).then(setUser);
    }, [id]);
    return user;
}

// utils/userUtils.ts - 业务逻辑
function formatUser(user: RawUser): DisplayUser {
    return {
        fullName: `${user.firstName} ${user.lastName}`,
        age: new Date().getFullYear() - user.birthYear,
    };
}

// components/UserProfile.tsx - 展示
function UserProfile({ id }: { id: string }) {
    const user = useUser(id);
    if (!user) return <Loading />;
    const display = formatUser(user);
    return <div>{display.fullName}, {display.age}岁</div>;
}
```

## 最佳实践

### 常见的关注点划分

| 关注点 | 职责 | 示例 |
|--------|------|------|
| 业务逻辑 | 核心规则 | 价格计算、权限验证 |
| 数据访问 | 持久化 | Repository、DAO |
| 展示逻辑 | UI渲染 | View、Template |
| 基础设施 | 技术支撑 | 日志、缓存、消息队列 |
| 横切关注 | 跨层需求 | 认证、审计、事务 |

### 分离信号

```
需要分离的信号：
□ 一个类/方法混合了多种不同的操作（数据库 + 业务 + 展示）
□ 修改展示逻辑时需要修改业务代码
□ 同样的业务逻辑在 API 和 CLI 中重复
□ 单元测试需要启动数据库或 Web 服务器
```

## 与其他原则的关系

| 原则 | 关系 |
|------|------|
| [SRP](../single-responsibility-principle/) | SRP 是类级别的 SoC |
| [ISP](../interface-segregation-principle/) | ISP 是接口级别的 SoC |
| [DIP](../dependency-inversion-principle/) | DIP 通过抽象实现层间分离 |
| [封装](../encapsulation-principle/) | 封装隐藏内部实现，支持 SoC |

## 总结

**SoC 核心**：一个模块只处理一个关注点。

**实践要点**：
- 按关注点划分模块、层、组件
- 通过接口定义关注点之间的边界
- 横切关注点用 AOP 或中间件处理
- 修改一个关注点不应该影响其他关注点
