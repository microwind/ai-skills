---
name: RabbitAdvisors 知识付费案例研究
description: "以虚拟公司 RabbitTech 的知识付费产品 RabbitAdvisors 为例，完整演示从领域建模到微服务落地的全流程 DDD 实践。"
license: MIT
---

# RabbitAdvisors 知识付费案例研究

## 案例背景

**公司**：RabbitTech  
**产品**：RabbitAdvisors（知识付费 / 付费咨询平台）

**核心业务流程**：

1. 业界专家（**作者**）与平台签约，在 RabbitAdvisors 上开设**专栏**
2. 专栏由**编辑**审核并定价
3. **读者**在平台浏览专栏，付费订阅自己感兴趣的专栏
4. 读者在订阅期内阅读专栏文稿
5. RabbitTech 按合同约定的分成比例和账期向作者支付佣金

**核心问题**：作为 CTO，如何对 RabbitAdvisors 进行架构设计，如何给团队分工？

本案例贯穿战略设计 → 战术设计 → 架构落地全流程，展示 DDD 方法论在真实 B 端业务中的应用。

## 第一阶段：领域建模

### 步骤 1：用[四色建模](../four-color-modeling/)寻找业务脊梁

从**现金流**出发，识别两条关键现金往来：

- **读者付费**（Payment）
- **作者分成**（CommissionPayment）

```
[ColumnQuote 专栏报价]            [ContributorContract 撰写合同]
      │ (编辑定价)                        │ (签约时约定)
      ▼                                   ▼
[Order 订单] ──金额相等──▶ [Payment 支付]  [Commission 佣金]
                              │             │ (账期内 Σ Payment × percentage)
                              ▼             ▼
                        [Subscription 订阅]  [CommissionPayment 分成支付]
                          │
                          └─触发─▶ [积分增加等下游事件]
```

### 步骤 2：识别领域对象

通过凭证链可以提炼出关键的领域对象：

```
实体 / 聚合根：
  ▸ Reader 读者              ▸ Author 作者             ▸ Editor 编辑
  ▸ Column 专栏              ▸ ColumnQuote 报价       
  ▸ Order 订单               ▸ Payment 支付            
  ▸ Subscription 订阅        
  ▸ ContributorContract 合同 ▸ Commission 佣金
  ▸ CommissionPayment 分成支付

领域事件：
  ▸ ColumnQuoted 专栏已报价        ▸ OrderCreated 订单已创建
  ▸ PaymentCompleted 支付已完成    ▸ SubscriptionCreated 订阅已创建
  ▸ CommissionCalculated 佣金已计算 ▸ CommissionPaid 分成已支付

值对象：
  ▸ Money 金额（amount + currency）
  ▸ Period 账期（开始、结束）
  ▸ CommissionRate 分成比例
```

**关键设计决策**：读者、编辑、作者虽然都可以登录，但**在系统中从事的动作、拥有的能力差异巨大**，因此将它们视为**三个独立的领域模型**，而非一个"用户"基类。"用户"的共性仅体现在登录、个人信息等少数场景。

## 第二阶段：战略设计

### 步骤 3：[子域划分](../domain-partitioning/)

```
┌─────────────────────────────────────────────────────────────┐
│                       RabbitAdvisors 领域                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  核心域：                                                      │
│    ├── 订单域 (Order)            ← 决定交易质量                 │
│    └── 订阅域 (Subscription)      ← 核心交付能力                 │
│                                                             │
│  支撑域：                                                      │
│    ├── 专栏域 (Column)                                        │
│    ├── 专栏报价域 (ColumnQuote)                               │
│    ├── 金融域 (Payment)                                       │
│    ├── 签约域 (Contract)                                      │
│    ├── 佣金域 (Commission)                                    │
│    ├── 评论域 (Comment)                                       │
│    └── 公告域 (Announcement)                                  │
│                                                             │
│  通用域：                                                      │
│    ├── 读者域 (Reader)                                        │
│    ├── 编辑域 (Editor)                                        │
│    ├── 作者域 (Author)                                        │
│    ├── 消息通知域 (Notification)                              │
│    └── 登录鉴权域 (Auth)                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**[类型划分](../domain-types/)依据**：

- **核心域**：直接产生业务价值，构成竞争力的子域（订单、订阅）
- **支撑域**：业务必须但非竞争核心（专栏、金融、签约）
- **通用域**：可替换、可复用，多个子域共用（认证、通知）

### 步骤 4：[限界上下文](../bounded-context/)划分

限界上下文划分的关键技巧：**一个限界上下文必须支持一个完整的业务流程**。

```
限界上下文 1：专栏订阅上下文
  包含子域：订单域、订阅域、读者域
  业务流程：读者选择专栏 → 下单 → 支付 → 订阅 → 阅读

限界上下文 2：专栏信息上下文
  包含子域：专栏域、专栏报价域、评论域、公告域、编辑域
  业务流程：编辑创建专栏 → 定价 → 发布 → 读者浏览

限界上下文 3：签约分佣上下文
  包含子域：签约域、佣金域、作者域
  业务流程：作者签约 → 按账期计算佣金 → 生成分成支付单

限界上下文 4：金融上下文
  包含子域：支付域、分成支付域
  业务流程：处理所有现金往来（对接支付网关）

限界上下文 5：用户信息上下文
  包含子域：读者域、编辑域、作者域的公共部分、认证域
  业务流程：登录、注册、个人信息维护
```

**⇒ 5 个限界上下文 = 5 个微服务**：

- `smart-classroom-subscription`（专栏订阅系统）
- `smart-classroom-column`（专栏信息系统）
- `smart-classroom-contract`（签约分佣系统）
- `smart-classroom-finance`（金融系统）
- `smart-classroom-user`（用户信息系统）

**团队分工**：5 个小组，每组负责一个限界上下文，形成 [康威定律](../bounded-context/) 的正向实践。

## 第三阶段：战术设计 —— 以"专栏订阅"为例

### 步骤 5：详细设计产出物

```
用例图：
  Actor "读者" --> (浏览专栏)
                 (查看专栏详情)
                 (订阅专栏)
                 (查看我的订阅)
                 (阅读专栏内容)

状态机 (Subscription)：
  ┌─────┐  create  ┌────────┐  cancel  ┌──────────┐
  │ 无  │ ───────▶ │ ACTIVE │ ───────▶ │ CANCELLED │
  └─────┘          └────┬───┘          └──────────┘
                        │ expire
                        ▼
                   ┌──────────┐
                   │ EXPIRED  │
                   └──────────┘

活动图（订阅）：
  读者 → 点击订阅 → [订单系统] 创建订单 → [金融系统] 支付
       → [订阅系统] 创建订阅 → 发送"订阅成功"事件 → 成长域增加积分

时序图（订阅）：
  Reader → Subscription/Facade → OrderApp → PaymentClient → SubscriptionDomain

ER 图（数据库建模）：
  t_subscription (id, reader_id, column_id, start_time, end_time, status, ...)
  t_order        (id, reader_id, column_id, amount, status, ...)
  t_payment      (id, order_id, amount, paid_at, status, ...)
```

### 步骤 6：聚合与聚合根设计

```java
// 聚合根 Subscription
public class Subscription {
    private final SubscriptionId id;          // 唯一标识
    private final ReaderId readerId;
    private final ColumnId columnId;
    private final Instant startTime;
    private final Instant endTime;
    private SubscriptionStatus status;

    // 工厂方法：从支付完成事件创建
    public static Subscription fromPayment(Payment payment, Column column) {
        if (!payment.isCompleted()) {
            throw new DomainException("支付未完成不能创建订阅");
        }
        return new Subscription(
            SubscriptionId.generate(),
            payment.getPayerId(),
            column.getId(),
            payment.getCompletedAt(),
            payment.getCompletedAt().plus(column.getDuration())
        );
    }

    // 业务行为
    public void cancel() {
        if (status != SubscriptionStatus.ACTIVE) {
            throw new DomainException("只有活跃订阅可以取消");
        }
        this.status = SubscriptionStatus.CANCELLED;
    }

    public boolean isActiveFor(Instant time) {
        return status == SubscriptionStatus.ACTIVE
            && !time.isBefore(startTime)
            && !time.isAfter(endTime);
    }
}
```

### 步骤 7：[领域服务](../domain-service/)——跨聚合编排

"订阅"这个动作涉及 **订单创建 + 支付 + 订阅创建** 等多个聚合，无法放到单一实体中，识别为**领域服务**：

```java
@Component
public class SubscriptionDomainService {

    private final OrderFactory orderFactory;
    private final PaymentClient paymentClient;   // 调用金融域（防腐层接口）
    private final ColumnFacadeClient columnClient;
    private final SubscriptionRepository subscriptionRepo;

    public Subscription subscribe(ReaderId readerId, ColumnId columnId) {
        // 1. 校验专栏可订阅、读者未重复订阅
        Column column = columnClient.getActive(columnId);
        if (subscriptionRepo.existsActive(readerId, columnId)) {
            throw new DomainException("已订阅过该专栏");
        }
        // 2. 创建订单
        Order order = orderFactory.create(readerId, column);
        // 3. 发起支付
        Payment payment = paymentClient.pay(order);
        // 4. 创建订阅（工厂方法）
        Subscription subscription = Subscription.fromPayment(payment, column);
        subscriptionRepo.save(subscription);
        return subscription;
    }
}
```

### 步骤 8：[应用服务](../application-service/)——事务和事件编排

```java
@Service
public class SubscribeAppService {

    @Autowired private SubscriptionDomainService subscriptionDomainService;
    @Autowired private DomainEventPublisher eventPublisher;

    @Transactional
    public SubscriptionInfo subscribe(SubscribeCommand cmd) {
        Subscription subscription = subscriptionDomainService.subscribe(
            new ReaderId(cmd.getReaderId()),
            new ColumnId(cmd.getColumnId())
        );
        eventPublisher.publish(new SubscriptionCreatedEvent(
            subscription.getId(), subscription.getReaderId(), subscription.getColumnId()
        ));
        return Model2InfoConverter.toInfo(subscription);
    }
}
```

### 步骤 9：[领域事件](../domain-events/)——跨上下文解耦

```
[专栏订阅上下文]                    [成长体系上下文]（假想扩展）
  发布 SubscriptionCreated  ──MQ──▶  订阅 SubscriptionCreated
                                        └──▶ 为读者增加积分

[签约分佣上下文]
  订阅 PaymentCompleted     ──MQ──▶  累计到作者的佣金统计
```

## 第四阶段：工程落地

### 步骤 10：[应用分层](../layered-architecture/)

每个微服务内部按 DDD 分层：

```
smart-classroom-subscription/
  ├── subscription-main          (启动入口)
  ├── subscription-facade        (对外 RPC 接口声明)
  ├── subscription-facade-impl   (接口实现)
  ├── subscription-controller    (HTTP 入口，可选)
  ├── subscription-application   (用例编排、事务、事件)
  ├── subscription-domain        (核心：聚合、领域服务、仓储接口)
  │     ├── subscription/        ← 订阅聚合包
  │     ├── order/               ← 订单聚合包
  │     └── shared/              ← 共享值对象
  ├── subscription-repository    (仓储实现、Mapper、DO)
  ├── subscription-infrastructure (防腐层实现、MQ 客户端)
  ├── subscription-utility       (工具类)
  └── subscription-testsuite     (测试)
```

### 步骤 11：技术栈

```
后端：
  ▸ Spring Boot     (应用框架)
  ▸ MyBatis          (ORM)
  ▸ MySQL            (存储)
  ▸ Dubbo            (RPC)
  ▸ Nacos            (注册中心 / 配置中心)
  ▸ RocketMQ         (消息队列 / 领域事件)
  ▸ Maven            (构建)

前端：
  ▸ React / TypeScript / React Router / Antd / Less / Vite
```

## 核心收获

### 1. DDD 的全链路价值

```
业务侧：                    技术侧：
  ▸ 统一语言               → 代码、文档、沟通一致
  ▸ 子域识别               → 资源合理分配（核心域多投）
  ▸ 业务脊梁               → 稳定不变的业务骨架
                           ▼
架构侧：
  ▸ 限界上下文 → 微服务拆分依据
  ▸ 聚合       → 事务边界
  ▸ 分层架构    → 团队协作规范
```

### 2. 关键权衡

- **核心域**（订单、订阅）：充血模型 + 详尽领域服务 + 最严测试
- **支撑域**（专栏、报价）：贫血模型 + 适度封装
- **通用域**（认证、通知）：直接用第三方，不过度设计

### 3. 落地教训

- **不要全盘 DDD**：示例项目将多个上下文合并到 `smart-classroom-misc` 中以简化演示，真实项目也可根据团队规模权衡
- **从现金流切入最稳**：业务脊梁是最不易变的部分
- **让业务方玩"角色扮演"验证模型**：远比抽象讨论有效

## 与其他 DDD 概念的关系

| 概念 | 本案例体现 |
|------|-----------|
| [四色建模法](../four-color-modeling/) | 第一阶段从现金流推导凭证链 |
| [子域划分](../domain-partitioning/) / [域类型](../domain-types/) | 第三阶段识别核心/支撑/通用域 |
| [限界上下文](../bounded-context/) | 第四阶段划分 5 个微服务 |
| [聚合](../aggregate/) | Subscription / Order 聚合 |
| [领域服务](../domain-service/) | SubscriptionDomainService |
| [应用服务](../application-service/) | SubscribeAppService |
| [领域事件](../domain-events/) | SubscriptionCreated 跨上下文解耦 |
| [分层架构](../layered-architecture/) | 完整的 COLA 分层落地 |

## 参考项目

- 后端微服务 1：`https://github.com/eyebluecn/smart-classroom-misc`
- 后端微服务 2：`https://github.com/eyebluecn/smart-classroom-subscription`
- 前端项目：`https://github.com/eyebluecn/smart-classroom-front`

## 总结

**核心**：通过 RabbitAdvisors 这一完整案例，展示了 DDD 从**发现业务脊梁 → 划分域 → 设计聚合 → 编写代码**的全链路实践。

**精髓**：

1. **建模的是业务经营，不是软件结构** ——从现金流切入最稳定
2. **先战略后战术** ——先划清边界再雕琢模型
3. **边界决定分工** ——限界上下文就是团队协作单元
4. **分层是团队协作的护栏** ——不是为了完美的代码洁癖

DDD 不是银弹，深刻理解业务才是架构师的核心能力。
