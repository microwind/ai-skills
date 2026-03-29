# Kotlin 质量体系与架构校验配置表单

## 项目基本环境与生态定义

### Kotlin 版本与目标平台
- **Kotlin 编译器版本**:
  - [ ] Kotlin 1.7 / 1.8 (支持向下兼容旧项目)
  - [ ] Kotlin 1.9 (引入数据对象 Data Object 等)
  - [ ] Kotlin 2.0 (K2 全新革命性编译器，编译速度和类型推断巨幅提升)
- **目标平台定位 (Kotlin Multiplatform/JVM)**:
  - [ ] Android App (Jetpack Compose / View)
  - [ ] Backend Server (Spring Boot / Micronaut)
  - [ ] Ktor (Kotlin 官方轻量级高并发框架)
  - [ ] KMP (iOS + Android + JVM 共享代码逻辑库)

### 核心运行时依赖 (Coroutines)
- [ ] `kotlinx-coroutines-core` (协程基座，Channels, Flow)
- [ ] `kotlinx-coroutines-android` (携带 `Dispatchers.Main` 主线程分发器)
- [ ] `kotlinx-coroutines-reactor` / `reactive` (WebFlux, RxJava3 互操作)
- [ ] `kotlinx-serialization-json` (取代繁重的 Gson/Moshi)

## 静态分析与安全防腐机制 (Detekt)

### 空安全防线 (Null Safety)
- [ ] 禁止所有的运行时非空断言修饰 `!!` (UnsafeCallOnNullableType) 以防范 NPE。
- [ ] 阻止并用编译警告标注冗余的安全调用修饰 `?.` (UselessCallOnNotNull) 或猫王 Elvis `?:`，保持代码简洁。
- [ ] 在调用 Java 提供的无 `@Nullable`/`@NonNull` 注解接口时，必须通过显式声明类型 (而不是依赖 Kotlin 平台盲猜 `Type!`)。

### 代码复杂度与可读性 (Complexity & Idioms)
- **嵌套深度与广度**:
  - [ ] 函数最大行数控制 (默认 60 行以内)
  - [ ] 循环/条件分支的圈复杂度控制 (Cyclomatic Complexity < 15)
- **作用域函数 (Scope Functions) 的滥用**:
  - [ ] 阻止连续超过 2 层的 `let`, `apply`, `run`, `with`, `also` 的隐晦连击。
  - [ ] 检测将 `apply` 用作普通返回 (它会返回 `this` 原对象) 而非单纯配置场景。

### 潜在 Bug 与异常泄漏 (Potential Bugs)
- [ ] 禁止使用 `runBlocking` 在主线程或网络层挂起 (除了测试框架和 `main` 方法)。
- [ ] `GlobalScope` 及未托管的生命周期协程开启必须被视为高危，触发强制 Review。
- [ ] 禁止通过普通的 `try-catch(e: Exception)` 不经筛选地吞噬所有的异常，特别是导致 `CancellationException` 被错误吞噬使得协程取消链失效。

## 性能损耗审查 (Performance & Internals)

### 高级函数与内联优化 (High-Order Functions)
- [ ] 函数接受 lambda 参数时是否漏写了 `inline` 修饰符？（导致运行时产生大量的闭包堆对象分配，触发 GC）。
- [ ] 对于不应被内联过长导致字节码急剧膨胀的超长函数，或者被存下来的回调 lambda，使用了 `noinline` 和 `crossinline` 控制。
- [ ] 高频或长集合 (`>10,000` 元素) 处理的 `.map()`, `.filter()` 是否使用了 `.asSequence()` 进行懒计算？

### 反射与实例化 (Reflection & Instantiation)
- [ ] 在 Android/KMP 环境中避免引入重型的 `kotlin-reflect`，使用原生编译推断替代（例如限定 Moshi CodeGen）。
- [ ] 单例模式使用了内建的 `object Declarations`，避免通过 `class Factory` 重复造轮子。

## 风格规范与统一 (Ktlint)

### 强制缩进与换行
- [ ] `ktlint` (Kotlin Linter) 作为 Git Pre-Commit 拦截钩子。
- [ ] 所有类成员、函数参数列表在超过规定长度 (通常 120 字符) 时，强制一参换一行，尾随逗号 (Trailing Comma)。
- [ ] 当表达式体函数 (Expression Body Functions) 只返回一个结果时，使用 `=` 连接，无需包含大括号。
  `fun add(a: Int, b: Int) = a + b`

## 单元测试与 Mock 栈架构

### Mock 库与原生协程支持
- **框架选用**:
  - [ ] MockK (Kotlin 专属终极 Mock 框架，完美兼容扩展函数和协程挂起，替代 Mockito-Kotlin)
  - [ ] Kotest (提供极为丰富的 BDD/TDD DSL 断言语句如 `a shouldBe 5`)
- **测试环境协程调度**:
  - [ ] 注入 `TestCoroutineDispatcher` 以使单元测试中所有的 `delay(1000)` 时间片直接虚拟步进并零秒执行结束 (Time Travel)。
