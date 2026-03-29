# Kotlin 现代化语法与架构参考手册

## 概述

从 Android 应用的心脏到高性能微服务后端，Kotlin 以其极其优雅且不失 JVM 强类型的特质风靡。本指南提供关于协程挂起 (`suspend`)、扩展系统、空安全以及常见设计模式的深入架构级代码示例。

## 协程与并发：超越线程 (Coroutines)

协程是被设计出来的轻量级用户态线程（User-level threads）。挂起（Suspension）不阻塞底层的系统线程，这允许单个 JVM 轻松管理一万个挂起协程而不会 OOM。

### 挂起函数与底层状态机 (Suspend Function)

Kotlin 的 `suspend` 函数编译后，会被转化为带有一个额外 `Continuation` 参数的普通方法。通过强大的 CPS (Continuation-Passing Style) 和 `switch` 状态机实现上下文恢复：

```kotlin
import kotlinx.coroutines.*

// 这是一个挂起函数，只能被其他协程或挂起函数调用
suspend fun fetchCloudData(): String {
    // delay 不会阻塞宿主线程，只会将当前协程封装为任务推入延迟队列！
    delay(1000L) 
    return "{ data: '123' }"
}

fun launchExample(scope: CoroutineScope) {
    scope.launch(Dispatchers.IO) { // 切换到 IO 线程池工作
        val res = fetchCloudData()  // 这里协程挂起，线程离开去处理别人
        
        // 1秒后，通过 Dispatchers 恢复这个协程，打印下文：
        withContext(Dispatchers.Main) { 
            // 如果在 Android 或 UI 环境，强制将这行切回主线程进行更新
            println("UI Updated: $res")
        }
    }
}
```

### Flow 与通道 (Flow & Channels)

`Flow` 对应响应式流 (RxJava 的 Observable)，它是冷流（Cold Stream），只有在执行了末端操作符（如 `collect`）时才会触发元素的发射；而 `Channel` 是热流（Hot Stream），相当于多个协程之间通信的阻塞/非阻塞并发队列。

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

// 定义一个 Flow，冷启动
fun downloadProgressFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(200) // 模拟网络时间
        emit(i * 20) // 发送进度，在收集端打印 20, 40, 60...
    }
}

suspend fun usage() {
    // Flow 是响应式的，允许各种声明式高阶提取
    downloadProgressFlow()
        .filter { it > 30 } // 只收集 > 30% 之后的值
        .map { "Progress is $it%" }
        .catch { e -> println("Error: $e") } // 上游异常收口！
        .collect { value -> // 终端操作符，启动！
            println(value)
        }
}
```

## Kotlin 的空安全与模式匹配 (Null Safety & Pattern Matching)

### 逃离 `NullPointerException` (NPE)

Kotlin 变量严格区分 `String` (不可为空) 和 `String?` (可为空)。编译系统不让前者存 `null`，不让后者直接调用方法。

```kotlin
fun processName(name: String?) {
    // 1. 安全调用 (Safe Call)
    val length = name?.length // 返回 Int?，如果 name 为空直接给 length 赋 null。
    
    // 2. Elvis 操作符 (赋予默认值)
    val len = name?.length ?: 0 // 如果长或者为空，则返回极值兜底 0
    
    // 3. 智能推断 (Smart Cast)
    if (name != null) {
        // 在该块内，编译器已经将 name 视为 String (非空)，随意调用
        println(name.uppercase())
    }
    
    // 4. let 控制级
    name?.let { 
        // 只有不为空时，才会进入 block。it 代表非空 String。
        println(it.uppercase()) 
    }
}
```

> **致命毒药**：极度不推崇使用 `name!!.length`。这句代码的语义是告诉编译器："我知道它可能为空，但我向你发誓它此时绝不为空！如果为空，请立即崩溃抛出 NPE"。

### 密封接口极意 (Sealed Interface)

替代 `enum` 与 `if-else`，特别适合代表具有不同数据附带状态的有限集（穷尽判断）。在 Redux 或 MVI 架构经常遇到状态定义。

```kotlin
// UI的状态机模型
sealed interface ScreenState {
    data object Loading : ScreenState // 无需参数，做成 object 单例省内存
    data class Success(val articles: List<String>) : ScreenState // 携带数据
    data class Error(val cause: Throwable) : ScreenState // 携带异常原因
}

fun render(state: ScreenState) {
    // when 具有穷尽性 (Exhaustive)
    // 漏写一个条件将直接通不过编译，这是消除遗漏分支 Bug 的神器！
    val uiText = when(state) {
        ScreenState.Loading -> "spinner.gif"
        is ScreenState.Success -> "Showing ${state.articles.size} items"
        is ScreenState.Error -> "Failed: ${state.cause.message}"
    }
    println(uiText)
}
```

## 高阶函数、内联与作用域函数 (Inline & Scope Functions)

### 作用域函数五兄弟 (let, run, with, apply, also)

初学者往往分不清到底应该用哪个进行对象配置或串联；请务必记忆这张表格与示例：

| 函数 | 当前对象引用 (Context) | 返回值 (Return) | 主要使命语境 |
|---|---|---|---|
| `let` | `it` (可改名) | Lambda 的最后一行 | 对非空对象操作，或者局部映射变量转换 |
| `also` | `it` (可改名) | 对象本身（原物） | 补充额外行为 (如日志打印)，不打破链式调用 |
| `run` | `this` (可省略) | Lambda 的最后一行 | 初始化对象并在块末端并返回计算结果 |
| `apply` | `this` (可省略) | 对象本身（原物） | **新对象的初始化配置阶段** |
| `with` | `this` (可省略) | Lambda 的最后一行 | 聚合调用一个已有对象的多个方法 |

```kotlin
// 最典型的 apply 场景：配置复杂对象
val paint = Paint().apply {
    color = Color.RED
    strokeWidth = 2f
    style = Paint.Style.STROKE
}

// 最典型的 let 与 also：从字典拿值安全输出，并记录
val upperName = map["jarry"]?.let { 
    it.uppercase() // 转换为大写并返回
}?.also {
    println("Extracted: $it") // 源原输出，并附赠一行日志
}
```

### `inline` 与重构闭包惩罚 (Reified)

向函数传入普通 lambda 会将其在 Java 层面编译为匿名内部类（导致内存分配）。使用 `inline` 可将方法的主体硬塞到调用处！

```kotlin
// inline: 编译器在调用这行时，把两行底层代码粘贴过去，完全没有函数调用的栈损耗或内部类分配。
inline fun measureTime(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block() // 块
    println("Took ${System.currentTimeMillis() - start} ms")
}

// inline reified (具化泛型)
// Java 的泛型天生擦除(Type Erasure)，无法做 `if (item is T)`
// 只有通过 inline reified 才可以使得泛型真正在运行期保留以供判断：
inline fun <reified T> List<*>.filterIsInstanceExt(): List<T> {
    val result = mutableListOf<T>()
    for (item in this) {
        if (item is T) { // 在普通泛型函数这是非法的！在 reified 下就合法！
            result.add(item)
        }
    }
    return result
}
```

## 面向对象的解构与属性委托 (Delegation)

### `by` 关键字原生支持的代理模式
如果您正在重写另一个类的许多同名接口方法到子成员，使用 Kotlin 委托一步到位。

```kotlin
interface Printer { fun print() }
class LaserPrinter : Printer { override fun print() = println("Laser!") }

// 传统的 Decorator 或者代理需要手敲数十个覆盖。
// Kotlin 的类委托，只需在声明处把 Printer 丢给传递的 printEngine。
class Office(printEngine: Printer) : Printer by printEngine

fun useDelegate() {
    val myLaser = LaserPrinter()
    val office = Office(myLaser)
    office.print() // 直接打印 "Laser!"
}
```

### 属性懒加载 (Lazy) 与监控 (Observable)
不再需要手动通过双重检查锁 (DCL) 编写单例，利用委托机制原生完成：

```kotlin
class AppData {
    // 线程安全的懒加载。只有在首次调用 database.get 时才会开销耗时的初始化。
    val database: String by lazy {
        println("Connecting to Database...")
        "Opened DB Connection"
    }
    
    // 每次发生写操作均通知的回调代理属性
    var username: String by Delegates.observable("N/A") { prop, old, new ->
        println("${prop.name} changed from $old to $new")
    }
}
```

## 工具链与静态插件支持

- **Ktlint**: (https://ktlint.github.io/)。推荐使用 `./gradlew ktlintCheck` 命令绑定到 Git pre-commit 脚本中以拒绝所有的乱排版代码。
- **Detekt**: (https://detekt.dev/) 基于 Kotlin 语法树的高度企业级扩展插件分析。用来定位"太长的方法", "循环圈复杂度超标"及异常错误捕捉。
