# 领域驱动设计 (Domain-Driven Design)

## 📋 概述

本目录将包含领域驱动设计(DDD)的核心理念、战略设计和战术设计，帮助开发者构建复杂业务领域的软件系统。

## 🎯 目标

- 介绍DDD的核心概念和思想
- 提供战略设计和战术设计的实践指南
- 展示DDD在不同业务场景下的应用
- 分析DDD与其他架构方法的结合

## 📚 计划包含的DDD内容

### 核心概念
- [领域模型](./domain-model/) - 业务领域的抽象模型
- [限界上下文](./bounded-context/) - 明确的边界和上下文
- [通用语言](./ubiquitous-language/) - 团队共享的业务语言
- [上下文映射](./context-mapping/) - 上下文之间的关系

### 战略设计
- [领域划分](./domain-partitioning/) - 如何划分领域
- [核心域、支撑域、通用域](./domain-types/) - 领域重要性分类
- [聚合根设计](./aggregate-root-design/) - 聚合的设计原则
- [领域事件](./domain-events/) - 领域内的事件机制

### 战术设计
- [实体 (Entity)](./entity/) - 具有唯一标识的对象
- [值对象 (Value Object)](./value-object/) - 没有标识的不可变对象
- [聚合 (Aggregate)](./aggregate/) - 数据修改的单元
- [领域服务 (Domain Service)](./domain-service/) - 领域逻辑服务
- [应用服务 (Application Service)](./application-service/) - 应用层服务
- [仓储 (Repository)](./repository/) - 聚合的持久化抽象

### 实践模式
- [CQRS模式](./cqrs-pattern/) - 命令查询责任分离
- [事件溯源](./event-sourcing/) - 基于事件的持久化
- [读模型优化](./read-model-optimization/) - 查询性能优化
- [ Saga模式](./saga-pattern/) - 分布式事务处理

### 架构集成
- [六边形架构](./hexagonal-architecture/) - 端口适配器架构
- [清洁架构](./clean-architecture/) - 依赖倒置架构
- [微服务中的DDD](./ddd-in-microservices/) - 分布式DDD实践
- [事件驱动架构](./event-driven-architecture/) - 基于事件的架构

## 🔍 每个主题将包含

每个DDD主题子目录将包含：

```
ddd-topic/
├── SKILL.md              # 主题详细说明和实现指南
├── README.md             # 主题概览
├── scripts/              # 代码实现示例
│   ├── java/
│   ├── python/
│   ├── typescript/
│   └── go/
├── diagrams/             # 架构图和流程图
├── case-studies/         # 实际业务案例分析
├── exercises/            # 练习和思考题
└── references/           # 相关阅读资料
```

## 🎓 学习路径

1. **基础概念** - 理解领域模型、限界上下文、通用语言
2. **战略设计** - 学习领域划分和上下文映射
3. **战术设计** - 掌握实体、值对象、聚合等构建块
4. **实践应用** - 应用CQRS、事件溯源等模式
5. **架构集成** - 在实际项目中应用DDD

## 💡 使用指南

- 每个SKILL.md文件将包含：
  - 概念定义和核心思想
  - 适用场景和解决的问题
  - 实现步骤和最佳实践
  - 代码示例和架构图
  - 实际项目应用案例
  - 常见误区和注意事项
  - 与其他概念的关系

## 🔗 相关内容

本目录内容与其他目录密切相关：
- **设计原则** - DDD体现了许多设计原则
- **设计模式** - DDD使用多种设计模式
- **系统设计** - DDD是复杂系统设计的方法论

## 🚀 状态

**📝 计划中** - 本目录正在规划中，将逐步添加各个DDD主题的详细内容。

---

*领域驱动设计是处理复杂业务领域的强大工具，它帮助我们构建真正解决业务问题的软件系统。*
