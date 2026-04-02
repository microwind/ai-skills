---
name: 面向特征编程
description: "以特征（Feature）为基本单元组织软件，每个特征封装完整的端到端功能切片。"
license: MIT
---

# 面向特征编程 (Feature-Oriented Programming)

## 概述

面向特征编程以**功能特征**为基本单元组织代码：每个特征是一个完整的功能切片，包含该功能所需的所有层次的代码。

**核心思想**：
- 一个特征 = 一个完整的功能（模型 + 逻辑 + UI + 测试）
- 特征可以独立开发、测试、部署
- 通过特征组合构建完整应用

## 代码组织

```
❌ 按技术层组织
src/
├── controllers/    # 所有控制器
├── services/       # 所有服务
├── models/         # 所有模型
└── repositories/   # 所有仓储

✅ 按特征组织
src/
├── features/
│   ├── auth/                # 认证特征
│   │   ├── AuthController.ts
│   │   ├── AuthService.ts
│   │   ├── User.ts
│   │   ├── UserRepository.ts
│   │   └── auth.test.ts
│   ├── order/               # 订单特征
│   │   ├── OrderController.ts
│   │   ├── OrderService.ts
│   │   ├── Order.ts
│   │   ├── OrderRepository.ts
│   │   └── order.test.ts
│   └── payment/             # 支付特征
│       ├── PaymentController.ts
│       ├── PaymentService.ts
│       └── payment.test.ts
└── shared/                  # 共享基础设施
    ├── database.ts
    └── middleware.ts
```

## 特征切换 (Feature Toggle)

```typescript
// 特征可以独立开关
class FeatureFlags {
    private flags: Map<string, boolean>;

    isEnabled(feature: string): boolean {
        return this.flags.get(feature) ?? false;
    }
}

// 使用
if (featureFlags.isEnabled('new-checkout-flow')) {
    return newCheckoutService.process(cart);
} else {
    return legacyCheckoutService.process(cart);
}
```

## 应用场景

| 场景 | 说明 |
|------|------|
| 产品线工程 | 同一基础代码，不同特征组合 = 不同产品 |
| A/B 测试 | 特征开关控制用户看到的版本 |
| 微前端 | 每个特征是一个独立的微前端模块 |
| 渐进式发布 | 按特征逐步上线 |

## 与其他范式/概念的关系

| 概念 | 关系 |
|------|------|
| [模块化](../../design-principles/modularity-principle/) | 特征是更粗粒度的模块 |
| [关注点分离](../../design-principles/separation-of-concerns/) | 按功能而非技术分离 |
| 微服务 | 每个特征可以演进为微服务 |

## 总结

**核心**：以完整的功能特征为单元组织代码，而非按技术层。

**实践**：每个特征目录包含该功能的所有层次代码，支持特征组合和独立部署。
