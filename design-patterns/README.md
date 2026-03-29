# 设计模式 (Design Patterns)

## 概述

设计模式集合，涵盖 GoF 23 种设计模式及其在不同编程语言中的实现和应用。设计模式是软件设计中常见问题的经典解决方案，能够帮助开发者编写出更灵活、可维护的代码。

**核心理念**: 好的设计模式能够解决设计问题，提高代码质量，加速开发过程。

## 学习指南

每个设计模式目录包含：
- **SKILL.md** - 完整的技能说明、何时使用、优缺点分析
- **forms.md** - 应用检查清单和配置表单  
- **reference.md** - 多语言实现代码示例
- **scripts/** - 辅助脚本和工具

## 设计模式分类

### 创建型模式 (Creational Patterns) - 对象创建

创建型模式抽象了对象的创建过程，使得系统对所创建的对象的类型不依赖。

| 模式 | 说明 | 何时使用 |
|------|------|---------|
| [**单例模式**](./singleton-pattern/SKILL.md) | 确保类只有一个实例 | 全局配置、连接池、日志系统 |
| [**工厂模式**](./factory-pattern/SKILL.md) | 定义创建对象的接口 | 多个实现、灵活创建、驱动选择 |
| [**抽象工厂模式**](./abstract-factory-pattern/SKILL.md) | 创建相关对象族 | UI 主题、跨平台、产品族 |
| [**建造者模式**](./builder-pattern/SKILL.md) | 分步骤构建复杂对象 | 参数众多、可选参数、链式调用 |
| [**原型模式**](./prototype-pattern/SKILL.md) | 通过复制创建对象 | 创建成本高、保存状态、深复制 |

### 结构型模式 (Structural Patterns) - 对象组合

结构型模式用来处理类和对象之间的组合关系，使得这些类或对象能够组合成更大的结构。

| 模式 | 说明 | 何时使用 |
|------|------|---------|
| [**适配器模式**](./adapter-pattern/SKILL.md) | 将不兼容接口转换 | 库集成、格式转换、兼容性 |
| [**装饰器模式**](./decorator-pattern/SKILL.md) | 动态添加职责 | 功能组合、避免继承、扩展功能 |
| [**代理模式**](./proxy-pattern/SKILL.md) | 为对象提供代理 | 延迟加载、权限控制、监控 |
| [**外观模式**](./facade-pattern/SKILL.md) | 提供统一接口 | 系统复杂、简化接口、分层 |
| [**桥接模式**](./bridge-pattern/SKILL.md) | 分离抽象和实现 | 多维变化、避免爆炸、独立扩展 |
| [**组合模式**](./composite-pattern/SKILL.md) | 树形结构处理 | 文件系统、菜单、递归结构 |
| [**享元模式**](./flyweight-pattern/SKILL.md) | 共享对象减少内存 | 大量相似对象、内存优化、对象复用 |

### 行为型模式 (Behavioral Patterns) - 对象交互

行为型模式涉及对象间的通信，明确对象间的角色和职责分配。

| 模式 | 说明 | 何时使用 |
|------|------|---------|
| [**策略模式**](./strategy-pattern/SKILL.md) | 定义可互换算法族 | 多个算法、灵活切换、避免分支 |
| [**模板方法模式**](./template-method-pattern/SKILL.md) | 定义算法骨架 | 框架固定、细节多样、代码复用 |
| [**观察者模式**](./observer-pattern/SKILL.md) | 定义对象间一对多关系 | 事件通知、MVC、发布-订阅 |
| [**迭代器模式**](./iterator-pattern/SKILL.md) | 顺序访问聚合元素 | 遍历集合、隐藏结构、多种遍历 |
| [**责任链模式**](./chain-of-responsibility-pattern/SKILL.md) | 请求沿链传递 | 多级审批、日志处理、请求传递 |
| [**命令模式**](./command-pattern/SKILL.md) | 将请求封装为对象 | 撤销/重做、队列处理、异步执行 |
| [**状态模式**](./state-pattern/SKILL.md) | 对象状态改变行为 | 状态机、工作流、避免条件分支 |
| [**备忆录模式**](./memento-pattern/SKILL.md) | 保存和恢复状态 | 撤销/重做、快照、版本控制 |
| [**访问者模式**](./visitor-pattern/SKILL.md) | 为对象添加新操作 | 复杂结构、多操作、分离数据和操作 |
| [**中介者模式**](./mediator-pattern/SKILL.md) | 封装对象间交互 | 多对象通信、耦合度高、集中管理 |
| [**解释器模式**](./interpreter-pattern/SKILL.md) | 定义语言的语法表示 | 语言实现、DSL、表达式求值 |

## 快速查询

### 按问题分类

**创建问题**
- 需要灵活创建对象？[工厂模式](./factory-pattern/SKILL.md) 或 [抽象工厂模式](./abstract-factory-pattern/SKILL.md)
- 对象有很多参数？[建造者模式](./builder-pattern/SKILL.md)
- 需要唯一实例？[单例模式](./singleton-pattern/SKILL.md)

**结构问题**
- 需要统一接口？[外观模式](./facade-pattern/SKILL.md) 或 [适配器模式](./adapter-pattern/SKILL.md)
- 需要扩展功能？[装饰器模式](./decorator-pattern/SKILL.md) 或 [代理模式](./proxy-pattern/SKILL.md)
- 树形结构？[组合模式](./composite-pattern/SKILL.md)

**行为问题**
- 大量 if-else？[策略模式](./strategy-pattern/SKILL.md) 或 [状态模式](./state-pattern/SKILL.md)
- 多步骤流程？[模板方法模式](./template-method-pattern/SKILL.md) 或 [责任链模式](./chain-of-responsibility-pattern/SKILL.md)
- 事件通知？[观察者模式](./observer-pattern/SKILL.md)
- 撤销/重做？[备忘录模式](./memento-pattern/SKILL.md) 或 [命令模式](./command-pattern/SKILL.md)

## 最佳实践

1. **不要过度设计** - 只在真正需要时使用设计模式
2. **理解本质** - 理解问题而非机械应用模式
3. **优先考虑简单** - 简单的设计往往是最好的设计
4. **逐步演进** - 代码逐步演进到需要模式的地步
5. **文档清晰** - 使用模式时要清晰标注

## 反模式须知

- **过度工程** - 为不存在的问题应用模式
- **误用模式** - 选择不适合的模式解决问题
- **混合模式** - 过度混合多个模式导致复杂性
- **忽视性能** - 模式可能带来性能开销

## 参考资源

- **经典著作**: Gang of Four (GoF) 的 《设计模式：可复用面向对象软件的基础》
- **实践指南**: 每个模式的 SKILL.md 包含详细指导
- **代码示例**: reference.md 提供多语言实现
- **检查清单**: forms.md 提供应用检查表

## 贡献指南

欢迎扩展和改进设计模式内容：
1. 添加新的代码示例
2. 补充实战案例
3. 提供性能优化建议
4. 改进文档清晰度

### 架构模式
- [MVC模式](./mvc-pattern/) - 模型视图控制器
- [MVP模式](./mvp-pattern/) - 模型视图展示器
- [MVVM模式](./mvvm-pattern/) - 模型视图视图模型
- [分层架构](./layered-architecture/) - 分层设计模式

### 并发模式
- [生产者消费者](./producer-consumer/) - 生产消费模式
- [读写锁](./read-write-lock/) - 读写同步模式
- [线程池](./thread-pool/) - 线程复用模式

## 学习路径

1. **初学者** - 从简单模式开始：单例、工厂、适配器
2. **进阶学习** - 掌握常用模式：装饰器、策略、观察者
3. **高级应用** - 复杂模式组合：访问者、中介者、责任链
4. **架构设计** - 学习架构模式和并发模式

## 使用指南

- 每个SKILL.md文件将包含：
  - 模式定义和目的
  - 适用场景和问题
  - UML类图和结构
  - 代码实现步骤
  - 实际应用案例
  - 优缺点分析
  - 相关模式对比
