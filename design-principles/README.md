# Design Principles

## 概述

设计原则集合，涵盖SOLID、DRY、KISS等软件设计核心原则，指导开发者编写高质量代码。设计原则是软件工程的智慧结晶。

## 目标

- 介绍经典的设计原则和思想
- 解释原则背后的动机和价值
- 提供实际应用场景和代码示例
- 分析原则之间的关系和权衡

## 适用场景

- 软件架构设计
- 代码重构优化
- 技术方案评估
- 团队编码规范制定

## 主要内容

### SOLID原则
- [单一职责原则 (SRP)](./single-responsibility-principle/) - 一个类只有一个变化的理由
- [开闭原则 (OCP)](./open-closed-principle/) - 对扩展开放，对修改关闭
- [里氏替换原则 (LSP)](./liskov-substitution-principle/) - 子类可以替换父类
- [接口隔离原则 (ISP)](./interface-segregation-principle/) - 不应该强迫依赖不需要的接口
- [依赖倒置原则 (DIP)](./dependency-inversion-principle/) - 依赖抽象而非具体实现

### 其他核心原则
- [DRY原则](./dry-principle/) - 不要重复自己
- [KISS原则](./kiss-principle/) - 保持简单
- [YAGNI原则](./yagni-principle/) - 你不会需要它
- [关注点分离 (SoC)](./separation-of-concerns/) - 分离不同的关注点
- [组合优于继承](./composition-over-inheritance/) - 优先使用组合
- [最少知识原则](./least-knowledge-principle/) - 最小化对象间的依赖

### 架构原则
- [分层架构原则](./layered-architecture-principle/) - 清晰的层次结构
- [模块化原则](./modularity-principle/) - 高内聚低耦合
- [封装原则](./encapsulation-principle/) - 隐藏实现细节
- [抽象原则](./abstraction-principle/) - 简化复杂性
- [一致性原则](./consistency-principle/) - 保持设计一致性

### 性能原则
- [性能优先原则](./performance-first-principle/) - 性能考虑
- [可扩展性原则](./scalability-principle/) - 支持增长
- [可用性原则](./availability-principle/) - 系统可靠性
- [容错性原则](./fault-tolerance-principle/) - 错误处理

## 学习路径

1. **基础理解** - 从SOLID原则开始，建立基础认知
2. **实践应用** - 通过代码示例理解原则的实际应用
3. **深入分析** - 学习原则之间的关系和权衡
4. **综合运用** - 在实际项目中应用多个原则

## 使用指南

- 每个SKILL.md文件将包含：
  - 原则定义和核心思想
  - 原则解决的问题
  - 正确和错误的应用示例
  - 实际项目应用案例
  - 与其他原则的关系
  - 常见误区和注意事项
