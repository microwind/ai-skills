---
name: 核心域、支撑域、通用域
description: "按业务价值和差异化程度将子域分为核心域、支撑域和通用域，指导资源分配和技术决策。"
license: MIT
---

# 核心域、支撑域、通用域 (Domain Types)

## 概述

DDD将子域按**业务价值和差异化程度**分为三类，指导技术投资和人力分配。

## 三种域的对比

| 维度 | 核心域 | 支撑域 | 通用域 |
|------|--------|--------|--------|
| 业务价值 | 最高，竞争优势 | 必要，但非差异化 | 基础设施 |
| 复杂度 | 通常最复杂 | 中等 | 可简可繁 |
| 投资策略 | 最优人才，持续投入 | 适度投入 | 购买/外包 |
| 技术方案 | 自研，DDD深度建模 | 自研或轻度定制 | 用现成方案 |
| 变更频率 | 高（业务创新驱动） | 中 | 低 |
| 代码质量 | 最高标准 | 良好标准 | 够用即可 |

## 示例：在线教育平台

```
核心域（竞争优势）：
├── 自适应学习引擎    → 根据学生表现调整教学路径
├── 课程推荐系统      → 个性化推荐
└── 学习效果评估      → 独特的评估算法

支撑域（必须有但不是差异化因素）：
├── 课程管理          → 课程CRUD、章节管理
├── 学生管理          → 注册、信息维护
└── 订单管理          → 购买课程流程

通用域（所有同类平台都需要）：
├── 用户认证          → 登录注册（用Auth0）
├── 支付处理          → 支付网关（用Stripe）
├── 文件存储          → 视频/文档（用AWS S3）
└── 邮件通知          → 发送邮件（用SendGrid）
```

## 示例：RabbitAdvisors 知识付费平台

来自 [RabbitAdvisors 案例研究](../rabbitadvisors-case-study/)，展示一个真实 B 端业务的域分类：

```
核心域（决定平台竞争力）：
├── 订单域 (Order)          → 交易转化率、金额准确性
└── 订阅域 (Subscription)    → 核心交付能力，订阅状态管理

支撑域（业务必需但非差异化）：
├── 专栏域 (Column)          → 内容组织
├── 专栏报价域 (ColumnQuote)  → 定价管理
├── 金融域 (Payment)          → 支付对接
├── 签约域 (Contract)         → 作者签约流程
├── 佣金域 (Commission)       → 分成计算
├── 评论域 (Comment)         
└── 公告域 (Announcement)    

通用域（同类产品普遍需要）：
├── 读者域 (Reader)          
├── 编辑域 (Editor)          
├── 作者域 (Author)          
├── 消息通知域 (Notification) 
└── 登录鉴权域 (Auth)         
```

**设计洞察**：

- "用户"看起来是通用概念，但**读者 / 编辑 / 作者在业务行为上差异巨大**，更适合划分为 3 个独立领域模型，只在登录、个人信息等场景共享基础能力
- 订阅域是核心域：订阅状态决定用户能否阅读内容，是产品交付的核心
- 订单域是核心域：交易规则、支付失败补偿、优惠券等都是竞争力

## 子域到微服务的路径

```
业务价值分类        →   限界上下文划分      →    微服务拆分
(子域类型)              (一组相关子域)          (物理服务)

核心域 订阅           │                         │
核心域 订单           │─ 专栏订阅上下文  ──────▶ smart-classroom-subscription
通用域 读者           │

支撑域 专栏           │
支撑域 专栏报价       │─ 专栏信息上下文  ──────▶ smart-classroom-column
支撑域 评论/公告      │
通用域 编辑           │

支撑域 签约           │
支撑域 佣金           │─ 签约分佣上下文  ──────▶ smart-classroom-contract
通用域 作者           │

支撑域 金融           │─ 金融上下文      ──────▶ smart-classroom-finance

通用域 认证/通知      │─ 用户信息上下文  ──────▶ smart-classroom-user
```

## 技术决策指南

```java
// 核心域：深度DDD建模，充血模型
public class LearningPath {
    private List<Module> modules;
    private StudentProfile profile;

    public Module recommendNext() {
        // 复杂的自适应算法 — 这是竞争优势
        return adaptiveEngine.selectOptimal(profile, modules);
    }
}

// 支撑域：简洁实现，不过度设计
public class CourseService {
    public Course create(CreateCourseRequest req) {
        Course course = new Course(req.getTitle(), req.getInstructor());
        return courseRepo.save(course);
    }
}

// 通用域：直接用第三方
// 不自己写认证系统，用 Auth0 SDK
Auth0Client auth = new Auth0Client(domain, clientId);
```

## 域类型可能变化

```
注意：域的分类不是永久的

示例演变：
- 支付处理原是通用域 → 公司决定做自己的钱包功能 → 变成核心域
- 推荐引擎原是核心域 → 行业都有了 → 变成通用域
- 客服系统原是支撑域 → 发现是留存关键 → 升级为核心域

→ 定期重新评估域分类
```

## 与其他DDD概念的关系

| 概念 | 关系 |
|------|------|
| [领域划分](../domain-partitioning/) | 域类型是划分后的分类标签 |
| [限界上下文](../bounded-context/) | 核心域需要最精确的上下文边界 |
| [通用语言](../ubiquitous-language/) | 核心域需要最精确的通用语言 |

## 总结

**核心**：识别并保护核心域，这是你的竞争优势所在。

**实践**：核心域深度投入，支撑域适度投入，通用域买现成的。
