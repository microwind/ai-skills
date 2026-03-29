# Swift / SwiftUI 规范与项目校验配置表单

## 项目基本架构与生态系统

### 部署目标构建 (Deployment Targets)
- **支持操作系统版本**:
  - [ ] iOS 13 / macOS 11 (勉强支持初级 Combine 与残缺 SwiftUI，不推荐)
  - [ ] iOS 14 / macOS 12 (正式启用 `@StateObject`，主流遗留分水岭)
  - [ ] iOS 15 / macOS 13 (引进原生的 Swift 5.5 `async/await` 现代并发能力)
  - [ ] iOS 17 / macOS 14 (启用全新 Swift 5.9 Observation 框架，全量废除传统视图刷新机制)

### 架构模式导向 (Architecture Pattern)
- [ ] 传统 MVC (古老 UIKit 体系，存在严重的 Massive View Controller 膨胀隐患)
- [ ] MVVM (现代 SwiftUI/Combine 官方首选，通过绑定拆解状态池)
- [ ] VIPER / Clean Architecture (适用于拆分极度复杂且具有高度可交互独立组建的企业级航母项目)
- [ ] Redux / TCA (The Composable Architecture 为 SwiftUI 量身定制的状态重放流模式)

## 静态分析与内存审计安全 (Memory & Semantics)

### 强引用切断与 ARC (Automatic Reference Counting)
- [ ] 在单例 (Singleton) 中强引用的 `Delegate` 或 `DataSource` 必须修正为 `weak` 以防视图层锁死。
- [ ] 不可或缺地对网络层及动画函数产生的带有逃逸性质 (`@escaping`) 的闭包启用 `[weak self]` 断开。
- [ ] 对于 `Timer#scheduledTimer` (带 block 返回) 或者 `CADisplayLink` 务必确保能够安全中途 Invalidate 或使用自带打破循环包层的封装。

### 基础类型的误用惩罚 (Collections & Values)
- [ ] Swift 的 `Array` 和 `Dictionary` 等结构均为 Copy-On-Write 值体系，避免在大量迭代器修改中间传入外置函数导致深拷贝（Copy penalty）。
- [ ] 阻止所有的解包毒药行为 (`obj!` , `try!`, `as!`)，它们带来的并不是便捷而是必定出现的 FatalCrash 分析痛点。如果确定必存在，须给出解释说明（如 `URL(string: "https://..")!` 是静态构建常量）。

## SwiftUI UI 渲染与状态防腐规范

### ViewModel 与 @ObservedObject 爆炸问题
- **依赖声明**:
  - [ ] 绝不使用 `@ObservedObject` 声明和构造新的实例 (`= ViewModel()`)。这将在重绘时导致数据实例全部清零。替代品应为本视图自身管辖的 `@StateObject`。
  - [ ] 子视图深层引用依赖注入全部改造为 `@EnvironmentObject` 以避免钻透 (Prop Drilling)。

### NavigationView 重制策略
- [ ] iOS 16 及更高需强制替换已废弃的危险组件 `NavigationView` 与 `NavigationLink(isActive:)` 为现代声明型路由树 `NavigationStack(path)` 解决侧滑导致的重构泄漏问题。

### 主线程卡死侦探 (Main Actor Binding)
- [ ] 当网络回调的 `ViewModel` 操作了影响 UI 观察的 `@Published` 字段，需严格检查该操作所在线程！
- [ ] 无论在传统 GCD 还是新的 `await`，务必检查修饰了 `@MainActor`，否则会导致紫色的主线违规崩溃警告。

## 现代化并发与线程同步 (Actor Model)

### Race Condition 数据争夺
- [ ] 用 `actor MyClass {}` 替换基于传统类的手动锁定变量（如同一个数组在一个线程 `append`、另一线程被读取崩溃的问题 `Concurrent Modification`）。
- [ ] 检测编译器发出的 "送往主线程的数据不是可发送的 (`Non-Sendable` 警告)"。因为传递 `class` 的引用进出现代闭包边界极度危险。

### Dispatch 重构 (Async Refactor)
- [ ] 弃用大量的嵌套金字塔回调 `onComplete { onNext { onFinally {} } }`，直接将其迁移到直观串行的 `async throws -> Data` 模型。利用原生 `Task { ... }` 发起主函数级异步。
- [ ] 不遗留空洞捕获 (`catch { }`)。必须要求利用 `Swift.Error` 甚至 `Logger` （OSLog）向上抛出业务失败栈。

## 测试与交付集成 (CI/CD)

### Xcode 工具链防线 (Xcode Build Phases)
- [ ] (强烈推荐) 集成 SwiftLint，并设在构建之前插入脚本拦截所有隐性命名与格式低级错误。
- [ ] 启用 Xcode 自带警告升级为错误 ("Treat Warnings as Errors" 设为 Yes)。

### 质量排雷 (Instruments)
- [ ] 要求提交重大 PR 时必须贴附 Xcode **Memory Graph** 在闭包环节的强引用验证（未检测到紫黄双色叹号图）。
- [ ] 使用 **Time Profiler** 检测 List 滚动中由于过多使用 `AnyView` 进行类型擦除引起的重绘抖动。
