---
name: DDD 分层架构 (COLA)
description: "以领域层为核心的应用分层架构，分为接口门面层、应用层、领域层、仓储层、基础设施层，保证高内聚低耦合和业务逻辑稳定。"
license: MIT
---

# DDD 分层架构 (Layered Architecture / COLA)

## 概述

DDD 只给出了分层思想（领域层要稳定、技术细节要隔离），并未规定具体模块划分。阿里巴巴 COLA 架构在经典 DDD 分层基础上结合工程实践，给出了**面向团队协作的可落地模块划分**。本文档融合了 COLA 的思想和互联网团队的实际经验。

**核心原则**：

- **领域层是核心**：最少对外依赖，只包含业务知识和规则，不掺杂技术细节
- **围绕领域层分层**：其他层要么被领域层使用，要么通过接口被领域层声明、由其他层实现
- **高内聚低耦合**：每一层有明确职责，层间依赖通过接口而非具体实现

## 应用模块分层全景

```
                        ┌─────────────────────┐
                        │   testsuite 测试套件  │ ── 依赖所有模块
                        └─────────────────────┘
                                  │
                        ┌─────────────────────┐
                        │    main 主程序入口    │ ── 启动入口、配置聚合
                        └──────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
          ┌─────────────────┐ ┌──────────┐ ┌──────────────────┐
          │ controller 控制层 │ │ facade-impl │ │  repository  │
          │  (HTTP 入口)     │ │ (RPC/SOA)  │ │ infrastructure │
          └────────┬────────┘ └─────┬────┘ └────────┬─────────┘
                   │                │               │
                   └────────┬───────┘               │
                            ▼                        │
                   ┌─────────────────┐               │
                   │ application 应用层 │──── 虚线依赖 ─┤
                   └────────┬────────┘               │
                            ▼                        │
                   ┌─────────────────┐               │
                   │  domain 领域层    │◀──────倒置依赖─┘
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │   utility 工具层   │
                   └─────────────────┘

                   ┌─────────────────┐
                   │    facade 接口包   │ ── 对外 API 声明，供其他应用依赖
                   └─────────────────┘
```

## 各层职责

### 测试套件层 (testsuite)

- 所有单测、集成测试的归宿
- 可访问所有其他模块（因为要测试它们）
- 代码生成工具（如 Saber / AliGenerator）通常也在这里

### 主程序层 (main)

- 应用的启动入口（Spring Boot 的 `Application.java`）
- Bean 装配、Profile 管理、全局配置
- **唯一能把所有模块"挂"起来的地方**

### 接口门面层 (facade)

- 对外发布的 **API 包**，包含 RPC/SOA 接口声明
- **只有接口定义和 DTO**，不含实现
- 外部应用依赖本应用时，只需依赖这个包

### 接口门面实现层 (facade-impl)

- 实现 facade 层声明的接口
- 职责：**协议转换**（入参校验、DTO → Info 转换、出参序列化）
- 不写业务逻辑，只做协议适配

### 控制器层 (controller, 可选)

- 直接提供 HTTP 服务时需要（Spring 的 `@Controller`）
- **只能调用 facade 声明的方法**，不能直接用 facade-impl 或 application
- 一般在微服务架构中，HTTP 由专门的网关应用提供，此层可以省略

### 应用层 (application)

应用层**编排**领域层的原子方法完成业务用例，但**不含业务规则**。

**允许的职责**：

- 事务控制（`@Transactional`）
- **仓储查询**（注意：只能查，不能写）
- 领域事件的触发和监听
- 操作日志
- 安全认证
- 多个领域服务的协调

**禁止的事情**：

- 写业务规则 / 条件判断
- 直接使用 Mapper / 具体仓储实现
- 直接调用中间件 SDK

```java
@Service
public class SubscribeAppService {

    @Autowired private SubscriptionDomainService subscriptionDomainService;
    @Autowired private PaymentDomainService paymentDomainService;
    @Autowired private DomainEventPublisher eventPublisher;

    @Transactional
    public SubscriptionInfo subscribe(SubscribeCommand cmd) {
        Payment payment = paymentDomainService.pay(cmd.getPaymentReq());
        Subscription subscription = subscriptionDomainService.subscribe(payment);
        eventPublisher.publish(new SubscriptionCreatedEvent(subscription));
        return Model2InfoConverter.toInfo(subscription);
    }
}
```

### 领域层 (domain)

**领域层是应用的心脏**，一个聚合一个 package。

**包含内容**：

```
domain/
  ├── subscription/             ← 一个聚合一个包
  │     ├── Subscription.java           (聚合根 / 实体)
  │     ├── SubscriptionId.java         (值对象)
  │     ├── SubscriptionStatus.java     (枚举)
  │     ├── SubscriptionDomainService.java
  │     ├── SubscriptionRepository.java (仓储接口)
  │     ├── SubscriptionFactory.java    (工厂)
  │     └── events/
  │          └── SubscriptionCreatedEvent.java
  └── shared/
        └── ...                         (共享值对象、基础类型)
```

**关键约束**：

- 实体建议采用**贫血模式**（平衡可维护性），实体 + 领域服务 = 完整领域模型
- 仓储接口定义在这里，但实现在仓储层（**倒置依赖**）
- 外部依赖（RPC 客户端、消息客户端）的接口定义在这里（**防腐层接口**）

### 仓储层 (repository)

- 负责数据查询和持久化
- **DO 对象只存在于这一层**，通过内部 Converter 转为领域对象后暴露给上层
- 实现领域层声明的仓储接口

```java
@Repository
public class SubscriptionRepositoryImpl implements SubscriptionRepository {

    @Autowired private SubscriptionMapper subscriptionMapper;

    @Override
    public Subscription findById(SubscriptionId id) {
        SubscriptionDO data = subscriptionMapper.queryById(id.getValue());
        return DO2ModelConverter.toModel(data);
    }

    @Override
    public void save(Subscription subscription) {
        SubscriptionDO data = Model2DOConverter.toDO(subscription);
        if (data.getId() == null) {
            subscriptionMapper.insert(data);
        } else {
            subscriptionMapper.update(data);
        }
    }
}
```

### 基础设施层 (infrastructure)

- **倒置依赖领域层**，实现领域层声明的 Client / FacadeClient 接口
- RPC 服务调用、消息中间件、缓存等的具体实现
- 经典 DDD 的**防腐层 (Anti-Corruption Layer, ACL)** 在这里

### 工具层 (utility)

- 与业务完全无关的工具类
- 全局通用 Exception
- 被所有模块直接或间接依赖，**必须保证无业务语义**

## POJO 命名规范

| 后缀 | 含义 | 所在层 |
|------|------|--------|
| **DO** | Data Object，数据库模型，字段和表一一对应 | repository |
| **Model** | 领域模型，逻辑核心 | domain |
| **DTO** | 外部传输对象，对外交互用 | facade |
| **Info** | 内部传输对象，application ↔ domain | application / domain |
| **VO** | Value Object，值对象或 facade 接收的 DTO | facade / domain |
| **Query** | 仓储查询参数封装 | domain（定义）/ repository（使用） |
| **Request** | Facade 接口的请求参数封装 | facade |
| **Converter** | 类型转换器，建议逐字段手写（避免 BeanUtils 带来的字段变更盲点） | 各层 |

## Spring Bean 命名规范

| 后缀 | 角色 | 所在层 |
|------|------|--------|
| **Controller** | HTTP 控制器 | controller |
| **Facade** / **FacadeImpl** | RPC 门面服务（可细分 WriteFacade / ReadFacade） | facade / facade-impl |
| **AppService** | 应用层服务（可细分 WriteAppService / ReadAppService） | application |
| **DomainService** | 领域服务 | domain |
| **Repository** / **RepositoryImpl** | 仓储接口 / 实现 | domain / repository |
| **Mapper** | MyBatis 查询接口 | repository |
| **Client** / **ClientImpl** | 中间件服务依赖接口 / 实现（防腐） | domain / infrastructure |
| **FacadeClient** / **FacadeClientImpl** | 外部 RPC 服务依赖接口 / 实现（防腐） | domain / infrastructure |
| **Configuration** | 各层自己的 Spring 配置 | 各层 |

## 方法命名建议

```
Service / Repository / Client / DAO 方法前缀：
  query  → 查询单个对象
  list   → 查询多个，复数结尾：listOrders
  page   → 分页查询，复数结尾：pageOrders
  count  → 统计
  insert → 插入
  delete → 删除
  update → 修改
```

## 与经典 DDD 四层架构的对应

| 经典 DDD 层 | 本架构对应模块 |
|------------|---------------|
| 用户界面层 (UI) | controller + facade + facade-impl |
| 应用层 (Application) | application |
| 领域层 (Domain) | domain |
| 基础设施层 (Infrastructure) | repository + infrastructure + utility |

## 工程权衡

这套分层看起来繁琐（一个请求要经过 Controller → Facade → FacadeImpl → AppService → DomainService → Repository → Mapper），但**它是面向团队协作设计的**：

- **小项目 / 个人项目**：用 MVC 足够，不要强行套用
- **团队项目 / 复杂业务**：分层看似冗余，但每层职责清晰，团队协作时各司其职，大幅降低事故率和维护成本

**何时该上 DDD 分层**：

```
✓ 核心域，业务规则复杂，长期演进
✓ 5 人以上团队协作
✓ 微服务拆分需要清晰边界
✗ 工具类、通用域，简单 CRUD
✗ MVP / POC 快速验证阶段
```

## 与其他 DDD 概念的关系

| 概念 | 关系 |
|------|------|
| [领域模型](../domain-model/) | 领域层承载完整的领域模型 |
| [聚合](../aggregate/) | 领域层一个聚合一个包 |
| [仓储](../repository/) | 接口在 domain，实现在 repository（倒置依赖） |
| [应用服务](../application-service/) | 对应 application 模块 |
| [领域服务](../domain-service/) | 放在 domain 模块的聚合包下 |
| [六边形架构](../hexagonal-architecture/) / [清洁架构](../clean-architecture/) | 都体现"依赖指向领域层"原则，本分层是它们的工程落地 |

## 总结

**核心**：围绕领域层分层，外层依赖内层，技术细节通过倒置依赖与领域层解耦。

**实践**：六层 + 命名规范 + 方法前缀约定，保证团队代码质量下限。

**记住**：这套架构**为团队协作而生**，不是为单人项目设计。用规范的代价换来的是可维护性和业务可演进性。
