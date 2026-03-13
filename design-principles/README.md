# 设计原则 (Design Principles)

## 📋 概述

本目录将包含软件设计的核心原则，这些原则是构建高质量、可维护、可扩展软件系统的基础。理解这些原则有助于开发者做出更好的设计决策。

## 🎯 目标

- 介绍经典的设计原则和思想
- 解释原则背后的动机和价值
- 提供实际应用场景和代码示例
- 分析原则之间的关系和权衡

## 📚 计划包含的设计原则

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

## 🔍 每个原则将包含

每个设计原则子目录将包含：

```
principle-name/
├── SKILL.md              # 原则详细说明和应用指南
├── README.md             # 原则概览
├── scripts/              # 代码示例和反例对比
│   ├── good-examples/    # 遵循原则的例子
│   └── anti-patterns/    # 违反原则的反例
├── case-studies/         # 实际案例分析
├── exercises/            # 练习和思考题
└── references/           # 相关阅读资料
```

## 🎓 学习路径

1. **基础理解** - 从SOLID原则开始，建立基础认知
2. **实践应用** - 通过代码示例理解原则的实际应用
3. **深入分析** - 学习原则之间的关系和权衡
4. **综合运用** - 在实际项目中应用多个原则

## 💡 使用指南

- 每个SKILL.md文件将包含：
  - 原则定义和核心思想
  - 原则解决的问题
  - 正确和错误的应用示例
  - 实际项目应用案例
  - 与其他原则的关系
  - 常见误区和注意事项

## 🔗 相关内容

本目录内容与其他目录密切相关：
- **设计模式** - 模式是原则的具体实现
- **领域驱动设计** - DDD应用了许多设计原则
- **编程范式** - 不同范式体现不同设计原则

## 🚀 状态

**📝 计划中** - 本目录正在规划中，将逐步添加各个设计原则的详细内容。

---

*设计原则是软件工程的智慧结晶，它们指导我们写出更好的代码。*
