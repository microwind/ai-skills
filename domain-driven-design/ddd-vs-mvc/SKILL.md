---
name: DDD 与 MVC 对比
description: "对比 MVC 模式与 DDD 方法论的差异，分析 MVC 在复杂业务下的局限性，帮助团队判断何时应采用 DDD。"
license: MIT
---

# DDD 与 MVC 对比

## 概述

MVC（Model - View - Controller）是最广泛使用的应用分层模式。DDD（Domain-Driven Design）则是一种面向复杂业务的**软件工程方法论**。两者**不是同一层面的概念**，但在工程实践中经常被并列讨论，因为一个项目往往要在它们之间做选择。

**一句话区别**：

- **MVC**：**软件层面的架构模式**，关注"代码怎么分层"
- **DDD**：**业务面向的方法论**，关注"业务如何建模、团队如何拆分、系统如何演进"

## MVC 模式的结构

```
┌──────────────────┐
│      View        │  视图展示（JSP、前端页面、返回 JSON）
└────────┬─────────┘
         ▲
         │
┌────────┴─────────┐
│   Controller     │  接收请求、编排业务、返回响应
│                  │  通常辅以 Service 实现业务逻辑
└────────┬─────────┘
         │
┌────────┴─────────┐
│      Model       │  数据库模型（ORM 实体 / DO）
└──────────────────┘
```

**典型代码组织**：

```
src/
  ├── controller/    ← 接口入口
  ├── service/       ← 业务逻辑（但很容易变成"数据搬运工 + if/else"）
  ├── model/         ← 数据库实体
  ├── dao/           ← 数据访问
  └── util/
```

## MVC 在复杂业务下的三大问题

### 1. MVC 不含业务语言

```java
// ❌ MVC 风格：一看就是"技术语言"
@RestController
public class OrderController {
    @PostMapping("/orders/{id}/status")
    public void updateStatus(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Order order = orderDao.getById(id);
        order.setStatus((Integer) body.get("status"));
        orderDao.update(order);
    }
}
```

业务专家看不懂"updateStatus(2)"是什么意思。DDD 要求所有代码使用**[通用语言](../ubiquitous-language/)**，让代码直接表达业务。

### 2. 数据和行为被天然割裂

MVC 默认**数据放在 Model（数据库实体）里，行为放在 Service 里**，这会导致：

- Service 越来越厚，变成"万能神类"
- Model 变成纯 DTO，完全没有业务知识
- 业务规则散落在各个 Service 方法中，难以复用和维护

```java
// ❌ 贫血模型 + 胖 Service
public class Order {  // 只有 getter/setter
    private Long id;
    private Integer status;
}

public class OrderService {
    public void pay(Long orderId) {
        Order o = dao.get(orderId);
        if (o.getStatus() != 0) throw new RuntimeException("状态错误");
        // ...大量业务规则堆在这里
        o.setStatus(1);
        dao.update(o);
    }
    public void ship(Long orderId) { /* ... */ }
    public void cancel(Long orderId) { /* ... */ }
    // ... 50 个方法
}
```

DDD 则倡导 [**充血模型**](../domain-model/)：把业务规则放回领域对象，`order.pay()`、`order.ship()` 自己保护自己的状态。

### 3. 缺乏顶层边界划分

```
MVC 只规范"一个应用内部怎么分层"，不解决：
  ✗ 业务该拆几个服务？
  ✗ 服务之间的边界在哪？
  ✗ 团队怎么分工？
  ✗ 哪些是核心业务，哪些是通用能力？

→ 全靠技术负责人"看经验拍脑袋"
→ 大团队协作时容易职责不清、分工不明
```

DDD 通过**[领域](../domain-partitioning/)、[子域](../domain-types/)、[限界上下文](../bounded-context/)** 解决顶层边界问题，为微服务拆分、团队分工提供系统方法。

## MVC 与 DDD 的关系

```
MVC 是"战术"问题：代码怎么组织
DDD 既是"战略"问题（业务如何划分）
       也是"战术"问题（如何建模）

DDD 分层架构 ⊇ MVC + 更细的分层 + 领域建模 + 边界划分
```

换句话说，MVC 可以看作 DDD 分层架构的**极简版**。

## 对比表

| 维度 | MVC | DDD |
|------|-----|-----|
| 定位 | 分层模式 | 方法论 / 架构思想 |
| 驱动对象 | 技术分层 | 业务领域 |
| 核心概念 | Model / View / Controller | 领域、子域、限界上下文、聚合、实体、值对象… |
| 业务规则归属 | 多散落在 Service | 集中在领域层（[领域模型](../domain-model/) + [领域服务](../domain-service/)） |
| 数据模型 | 通常 = 数据库模型 | 领域模型 ≠ 数据模型，[仓储](../repository/)做转换 |
| 统一语言 | 无要求 | 核心要求 |
| 边界划分 | 无规范 | [限界上下文](../bounded-context/)明确边界 |
| 团队协作 | 靠规范 | 限界上下文即团队划分单元 |
| 学习成本 | 低 | 较高 |
| 适用场景 | 业务简单、项目小 | 业务复杂、长期演进、多团队 |

## 选型决策表

```
✅ 使用 MVC（或更轻量）：
  ▸ 业务简单：CRUD 为主，规则少
  ▸ 项目小：个人项目、内部工具
  ▸ 时效紧：MVP、POC、原型验证
  ▸ 团队小：1~3 人
  ▸ 典型：管理后台、数据报表、简单 API

✅ 使用 DDD：
  ▸ 业务复杂：规则多、流程长、分支多
  ▸ 长期演进：核心域，未来会持续迭代
  ▸ 多团队协作：需要明确边界分工
  ▸ 需要领域模型：业务知识值得沉淀
  ▸ 典型：SaaS 平台、B 端业务系统、金融系统、电商核心

❌ 常见误区：
  ▸ 为了"DDD 而 DDD"：把简单 CRUD 套上繁重分层，反而拖累开发效率
  ▸ "全盘 DDD 一把梭"：即使同一公司，通用域用 MVC、核心域用 DDD 是常见做法
  ▸ 把 DDD 当"银弹"：业务本身的复杂度靠设计规避不了，深刻理解业务才是关键
```

## 演进路径

实际项目中，**从 MVC 向 DDD 演进**是常见做法，而非一步到位：

```
Phase 1  MVC：快速验证业务可行性
          ↓
Phase 2  半 DDD：保留 MVC 骨架，在核心模块引入领域模型与聚合
          ↓
Phase 3  完整 DDD：核心域按限界上下文拆微服务，应用 [分层架构](../layered-architecture/)
          ↓
Phase 4  持续演进：根据业务理解加深，不断重构领域模型
```

## 与其他 DDD 概念的关系

| 概念 | 关系 |
|------|------|
| [领域模型](../domain-model/) | 充血模型是 DDD 对贫血 MVC Model 的回应 |
| [限界上下文](../bounded-context/) | 解决 MVC 无法回答的"系统如何拆分"问题 |
| [DDD 分层架构](../layered-architecture/) | DDD 下的工程落地分层，可视为 MVC 的演进 |
| [通用语言](../ubiquitous-language/) | DDD 对 MVC 缺乏业务语言的修正 |

## 总结

**核心**：MVC 解决代码分层问题，DDD 解决业务建模和系统边界问题。

**实践原则**：

- **简单业务用 MVC**，不要为了 DDD 而 DDD
- **复杂业务用 DDD**，但核心在于领域建模，而非模板化分层
- **深刻理解业务 > 任何设计方法论**——DDD 是工具，不是目标
