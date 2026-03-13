# Design Patterns

## 概述

设计模式集合，涵盖GoF 23种设计模式及其在不同编程语言中的实现和应用。设计模式是软件设计中常见问题的经典解决方案。

## 目标

- 提供经典设计模式的详细说明
- 展示设计模式的实际应用场景
- 分析设计模式的优缺点和适用性
- 提供多语言的代码实现示例

## 适用场景

- 软件架构设计
- 代码重构优化
- 设计模式学习
- 最佳实践应用

## 主要内容

### 创建型模式 (Creational Patterns)
- [单例模式](./singleton-pattern/) - 确保类只有一个实例
- [工厂模式](./factory-pattern/) - 创建对象的接口
- [抽象工厂模式](./abstract-factory-pattern/) - 创建相关对象族
- [建造者模式](./builder-pattern/) - 分步骤构建复杂对象
- [原型模式](./prototype-pattern/) - 通过复制创建对象

### 结构型模式 (Structural Patterns)
- [适配器模式](./adapter-pattern/) - 接口转换
- [装饰器模式](./decorator-pattern/) - 动态添加功能
- [代理模式](./proxy-pattern/) - 控制对象访问
- [外观模式](./facade-pattern/) - 简化接口
- [桥接模式](./bridge-pattern/) - 分离抽象和实现
- [组合模式](./composite-pattern/) - 树形结构处理
- [享元模式](./flyweight-pattern/) - 共享对象减少内存

### 行为型模式 (Behavioral Patterns)
- [策略模式](./strategy-pattern/) - 算法族封装
- [模板方法模式](./template-method-pattern/) - 算法骨架
- [观察者模式](./observer-pattern/) - 事件通知
- [迭代器模式](./iterator-pattern/) - 遍历集合
- [责任链模式](./chain-of-responsibility-pattern/) - 请求传递
- [命令模式](./command-pattern/) - 请求封装
- [备忘录模式](./memento-pattern/) - 状态保存
- [状态模式](./state-pattern/) - 状态切换
- [访问者模式](./visitor-pattern/) - 操作分离
- [中介者模式](./mediator-pattern/) - 对象交互协调

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
