# Swift 现代语法与架构模式参考文档

## 概述

随着 Swift 版本的飙升（Swift 5.5 到 5.9），苹果重塑了极其庞大的底层基础设施。从早期对 GCD 闭包依赖的大面积逃跑，发展成为基于 `async/await`，`Actor` 数据竞态保护，以及基于宏指令 `Observation` 的跨代际飞跃。

本参考文档揭示日常重构和排雷最核心的写法模式与架构机制保障原理，以应对巨头工程和 SwiftUI 化生态。

## 内存管理革命 (ARC 与强引用破除)

无论您的硬件多强大，强引用泄漏都是导致 iOS App 后台退场 (Jetsam) 杀死的罪魁祸首。

### 危险捕获：闭包与属性分离 (Retain Cycles in Closures)

逃逸闭包 (`@escaping`) 意味着此块代码会在当前函数返回之后的将来某时去执行（常见于网络通讯）。它像黑洞一样强拉着它需要的一切变量活着。

```swift
class Downloader {
    var title = "Document"
    var didFinish: (() -> Void)?

    func start() {
        // 致死错误 (Fatal Mistake): 
        // 闭包截获了 self (隐式)，self 通过变量 didFinish 截获了闭包。
        // 对象形成 8 字死环，退出屏幕永远不析构（deinit不被调用）。
        didFinish = {
            print("Finished downloading: \(self.title)") 
        }
    }
    
    func startCorrectly() {
        // 完美方案：切断连带捕捉点，令闭包用一根极其虚弱的线吊着 self，
        // 如果 self 死了，线就断开成了 nil。
        didFinish = { [weak self] in
            guard let self = self else { return } // 第一句必解开并强拿，如果已死直接跳出
            print("Finished downloading: \(self.title)")
        }
    }
}
```

### Delegate 的声明规范
永远不要强连 Controller 间的代理结构，务必声明为 `weak`：
```swift
// 必须受属于 AnyObject 的约束，才可以将其变为 weak
protocol TaskDelegate: AnyObject {
    func didComplete()
}

class ChildView {
    weak var delegate: TaskDelegate? // weak 可选类型是黄金防御！
}
```

## 现代并发：结构化编程与 Actor (Structured Concurrency)

Swift 5.5 前，所有人都在 `DispatchQueue` 迷宫里摸黑，造成各种各样的 `Race Condition`（如多线程崩溃修改数组）。

### `async` / `await` 取代金字塔回调
线性阅读代码，原生支持 `try` / `catch` 的冒泡拦截：

```swift
// 从极力维护回调：
func fetch(id: Int, completion: @escaping (Result<User, Error>) -> Void) { ... }

// 到一句优雅的方法声明：
func fetch(id: Int) async throws -> User {
    // await 代表函数让出 CPU （挂起，让给其他人跑），当网络结束，再复活继续往下跑。
    let url = URL(string: "https://api.com/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// 调用异步的上下文 (在 SwiftUI)
Task {
    do {
        let user = try await fetch(id: 10)
        // 回到修饰过 @MainActor 或者刻意拉的主线程更新 UI
    } catch {
        print("Failed: \(error)")
    }
}
```

### Actor：内建的并发隔离
相比于传统 `class` 你可能在内部手动写极其昂贵的 `NSLock` 或 `os_unfair_lock` 来防止 `append` 越界崩溃；如今只需要改一个词就万事大吉：`actor`！

```swift
// 传统 class 会造成经典的 Data Race: 两个 CPU 同时调用 withdraw, 余额变成负数崩溃！
actor BankAccount {
    var balance: Double = 0.0
    
    func deposit(amount: Double) {
        balance += amount
    }
    
    func withdraw(amount: Double) throws {
        guard balance >= amount else { throw InsufficientFundsError() }
        balance -= amount
    }
}

// 对 actor 的方法的调用必须加上 await，编译器强制让对同一实例的所有访问串行排队！
Task {
    let account = BankAccount()
    await account.deposit(amount: 100)
    try await account.withdraw(amount: 50)
}
```

### 主线程之主：`@MainActor`

永远不要在非主线程尝试渲染 UI。如果异步逻辑最后要回到 UI 更新：

```swift
@MainActor // 把这个强效外挂挂在 ViewModel 级或者视图级别
class UserViewModel: ObservableObject {
    @Published var name = "Loading..."
    
    func load() async {
        // ... 在后台线程下载数据 ... (这部分会在后台进行)
        // 当你要给 `@Published` 赋值，由于加了 @MainActor，Swift 会自动把底层调用扔回 UI 主线程
        self.name = "John Doe" 
    }
}
```

## SwiftUI 全新数据响应链架构

SwiftUI 视图是短暂存在的映射树。

### 视图的局部变量 (`@State` 与 `@Binding`)

```swift
struct ToggleView: View {
    // 自身持有的变量，标记为 @State, 任何改变立即触发 View body 重载！
    @State private var isOn = false 
    
    var body: some View {
        // 用 $ 符传递内存引用，让子组件能够改变父组件的状态
        CustomSwitch(value: $isOn)
    }
}

struct CustomSwitch: View {
    @Binding var value: Bool // 它不持有状态，它只是一个指针引用
    var body: some View { ... }
}
```

### 状态持有者的存活 (StateObject)
这是 90% 新手入门最常犯、找不出内存漏和崩溃的究极问题：

```swift
// 如果在 View 内这样写：
// @ObservedObject var viewModel = ProfileModel() 
// ↑↑ 致命反模式！ SwiftUI 一刷新这玩意儿瞬间灰飞烟灭再重做一遍

// 正确做法：将生命周期根植到该视图绑定存在时
@StateObject var viewModel = ProfileModel()
// 对于非根传接手才使用 @ObservedObject：
// @ObservedObject var viewModel: ProfileModel
```

### SwiftUI / Swift 5.9 高阶大杀器：`@Observable`
如果项目针对 iOS 17 以上：连 `@Published` 都不用写了，底层直接依靠宏展开接管所有的 Getter 和 Setter 追踪变更，极其省开销，也没有重建崩溃的可能。

```swift
import Observation

@Observable class ModernViewModel {
    var count = 0
    var name = "Alice"
    // 甚至你不用 @StateObject，直接普通声明就起飞
}
```

## 面向协议与可复用设计 (POP - Protocol Oriented)

不要像 Java 那样深层继承 `Class A : Class B : Class C`。类应以 `final` 切断继承，然后横向注入 `protocol` 和拓展。

```swift
protocol Describable { func describe() -> String }

// 在拓展(extension)里给协议加一份"默认实现"，其他实现了该协议的类都有了这个能力（鸭子类型）！
extension Describable {
    func describe() -> String { return "This is a default description." }
}

struct Car: Describable {}
struct User: Describable {
    func describe() -> String { return "I can override this!" }
}

let c = Car()
print(c.describe()) // "This is a default description."
```

## 工具链拦截与验证

**SwiftLint 关键开启防线清单 (.swiftlint.yml):**
```yaml
opt_in_rules:
  - force_cast # 严惩 as! 
  - force_try  # 严惩 try!
  - weak_delegate # 揪出未标记 weak 的强持代理
  - redundant_optional_initialization # 优化多余的可选解包
  - empty_count # 使用 isEmpty 而不是 .count == 0 提升巨量性能

line_length: 120
function_parameter_count: 5 
```
