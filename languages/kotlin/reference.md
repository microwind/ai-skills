# Kotlin编程 技术参考文档

## 概述

Kotlin是JVM上的现代编程语言，融合了函数式编程和面向对象编程的特点。它以其简洁的语法、强大的null安全、丰富的扩展函数和协程支持而闻名，是Android官方推荐的开发语言。

## 语言特性对比：Kotlin vs Java

| 特性 | Kotlin | Java |
|------|--------|------|
| Null安全 | 原生支持 | 需要注解 |
| 扩展函数 | ✓ | ✗ |
| Lambda | ✓ | Java 8+ |
| 数据类 | ✓ | 需要Lombok |
| 密封类 | ✓ | Java 17+ |
| 协程 | ✓（一级特性） | 需要库 |
| 属性委托 | ✓ | ✗ |
| 作用域函数 | ✓ | ✗ |

## Null安全系统

### 非空和可空类型

```kotlin
// 非空类型
val name: String = "Alice"
name = null  // 编译错误！

// 可空类型
val nickname: String? = null  // OK
val length = nickname?.length  // 可空调用

// 非空断言（使用需谨慎）
val nonNullName: String = nickname!!  // 如果为null则抛异常
```

### 处理null的最佳方式

```kotlin
// 1. 安全调用操作符
val length = name?.length

// 2. Elvis操作符
val displayName = name ?: "Unknown"

// 3. let表达式（仅在非null时执行）
name?.let { n ->
    println("Name is $n")
}

// 4. if表达式和Smart Cast
if (name != null) {
    println("Length: ${name.length}")  // 自动转为非空类型
}

// 5. 组合
val message = name?.let { "Hello $it" } ?: "Hello Unknown"
```

## 函数式编程

### 高阶函数

```kotlin
// 函数作为参数
fun apply(x: Int, operation: (Int) -> Int): Int {
    return operation(x)
}

// 调用
val result = apply(5) { it * 2 }     // 10
val result2 = apply(5) { it + 10 }   // 15

// 函数作为返回值
fun makeAdder(x: Int): (Int) -> Int {
    return { y -> x + y }
}

val add5 = makeAdder(5)
println(add5(3))  // 8
```

### 作用域函数（Scope Functions）

| 函数 | 接收者 | 返回值 | 用途 |
|------|--------|--------|------|
| let | it | lambda结果 | 转换、链式 |
| also | it | 接收者 | 调试、打印 |
| apply | this | 接收者 | 初始化 |
| run | this | lambda结果 | 执行代码块 |
| with | this | lambda结果 | 执行代码块 |

```kotlin
// apply - 配置对象并返回自身
class Person(var name: String = "", var age: Int = 0)

val person = Person().apply {
    name = "Alice"
    age = 30
}

// let - 转换
val result = person.let { p ->
    "${p.name} is ${p.age} years old"
}

// also - 调试打印
person.also { p ->
    println("Processing: $p")
}.let { /* 继续处理 */ }

// run - 上下文切换
val value = run {
    val x = 10
    val y = 20
    x + y  // 返回
}

// with - 执行多个操作
with(person) {
    println(name)
    age++
}
```

### 集合操作

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)

// 链式操作
numbers.filter { it > 2 }
       .map { it * 2 }
       .sorted()
       .forEach { println(it) }

// fold - 累积操作
val sum = numbers.fold(0) { acc, value -> acc + value }

// 使用Sequence优化大数据集
val lazyResult = numbers.asSequence()
                       .filter { it > 2 }
                       .map { it * 2 }
                       .toList()

// groupBy
val grouped = numbers.groupBy { if (it % 2 == 0) "even" else "odd" }
// {odd=[1, 3, 5], even=[2, 4, 6]}

// associate
val numberToString = numbers.associateBy { it.toString() }
```

## 数据类和密封类

### 数据类（Data Class）

```kotlin
// 自动生成 equals, hashCode, toString, copy, componentN
data class Person(val name: String, val age: Int, val email: String?)

// 使用
val p1 = Person("Alice", 30, "alice@example.com")
val p2 = p1.copy(age = 31)  // 快速复制修改

// 解构
val (name, age, email) = p1

// 集合中使用
val people = listOf(
    Person("Alice", 30, "alice@example.com"),
    Person("Bob", 25, "bob@example.com")
)

for ((name, age) in people) {
    println("$name is $age")
}
```

### 密封类（Sealed Class）

```kotlin
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// when表达式穷举检查（编译器确保完整性）
fun handleResult(result: Result<String>) {
    when (result) {
        is Result.Success -> println("Success: ${result.value}")
        is Result.Error -> println("Error: ${result.exception.message}")
        is Result.Loading -> println("Loading...")
        // 无need for else，编译器检查穷举性
    }
}
```

## 委托和扩展

### 委托属性

```kotlin
// 延迟初始化
val lazyValue: String by lazy {
    println("Computing...")
    "Hello"  // 首次访问时计算
}

// Observable属性
var name: String by Delegates.observable("<no name>") { _, old, new ->
    println("Property changed from $old to $new")
}

// Vetoable属性（验证）
var age: Int by Delegates.vetoable(0) { _, _, newValue ->
    newValue >= 0  // 返回true允许，false拒绝
}
```

### 扩展函数

```kotlin
// 为String添加扩展函数
fun String.isEmailValid(): Boolean {
    return this.contains("@") && this.contains(".")
}

// 使用
val email = "user@example.com"
println(email.isEmailValid())  // true

// 为泛型扩展
fun <T> List<T>.middle(): T? {
    return if (isEmpty()) null else this[size / 2]
}

println(listOf(1, 2, 3, 4, 5).middle())  // 3
```

## 协程（Coroutines）

### 基础概念

```kotlin
import kotlinx.coroutines.*

// 启动协程
GlobalScope.launch {
    delay(2000)  // 挂起，不阻塞线程
    println("World!")
}
println("Hello")
Thread.sleep(3000)  // 只需等待演示

// 使用runBlocking进行测试
runBlocking {
    println("Start")
    delay(1000)
    println("End")
}
```

### launch vs async

```kotlin
// launch - 不返回结果，启动后即忘
GlobalScope.launch {
    println("Task completed")
}

// async - 返回Deferred，可获取结果
GlobalScope.async {
    delay(1000)
    42
}

// 实际使用应该指定Scope
suspend fun fetchData(): String {
    return withContext(Dispatchers.IO) {
        // 网络请求
        delay(1000)
        "data"
    }
}

// 并行执行多项任务
suspend fun loadUserAndPosts(userId: Int) {
    val userDeferred = async { fetchUser(userId) }
    val postsDeferred = async { fetchPosts(userId) }
    
    val user = userDeferred.await()
    val posts = postsDeferred.await()
}
```

### Flow - 响应式流

```kotlin
// 生产数据流
fun produceNumbers(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i)
    }
}

// 消费数据流
suspend fun main() {
    produceNumbers()
        .map { it * 2 }
        .filter { it > 4 }
        .collect { value ->
            println(value)
        }
}
```

## 与Java的互操作性

### Kotlin调用Java

```kotlin
// Kotlin自动处理Java的可null返回
val javaString: String? = javaFunction()

// 平台类型（String! 表示可null可不null）
// IDE会警告，但编译通过
```

### Java调用Kotlin

```kotlin
// 为Java提供友好的接口
@JvmStatic
fun staticMethod() { }

@JvmOverloads
fun method(a: Int, b: Int = 0) { }

// Java中调用
KotlinFile.staticMethod();
KotlinFile.method(5);       // 使用默认参数
KotlinFile.method(5, 10);   // 显式指定
```

## 性能优化建议

### 1. 避免过度链式操作
```kotlin
// 不好：多次中间对象
val result = list.filter { it > 0 }
                .map { it * 2 }
                .map { it + 1 }
                .take(10)

// 更好：使用Sequence
val result = list.asSequence()
                .filter { it > 0 }
                .map { it * 2 }
                .map { it + 1 }
                .take(10)
                .toList()
```

### 2. 避免过度使用非空断言
```kotlin
// 不好
val value = nullableValue!!
val list = nullableList!!.size

// 更好
nullableValue?.let { v ->
    // 使用v
}

val size = nullableList?.size ?: 0
```

### 3. 合理使用作用域函数
```kotlin
// 不好：过度嵌套
person?.let {
    it.name?.let { name ->
        // 使用name
    }
}

// 更好
person?.name?.let {
    // 使用it
}
```

## 编码规范清单

- [ ] 优先使用val而不是var
- [ ] 避免使用非空断言（!!）
- [ ] 使用Elvis操作符处理null
- [ ] 优先使用when而不是if-else
- [ ] 合理使用扩展函数
- [ ] 避免过度使用lambda
- [ ] 小心GlobalScope的使用
- [ ] 为公开函数提供文档
- [ ] 使用数据类简化代码
- [ ] 测试协程代码（使用TestDispatchers）
