---
name: 语言特性对比
description: "对比主流编程语言对各种范式特性的支持程度，帮助技术选型和跨语言学习。"
license: MIT
---

# 语言特性对比 (Language Features Comparison)

## 类型系统

| 特性 | Java | Python | TypeScript | Rust | Go | Kotlin |
|------|------|--------|------------|------|-----|--------|
| 静态类型 | ✅ | ❌ (可选) | ✅ | ✅ | ✅ | ✅ |
| 类型推断 | ✅ (var) | N/A | ✅ | ✅ | ✅ | ✅ |
| 泛型 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 代数数据类型 | ✅ (sealed) | ❌ | ✅ (union) | ✅ (enum) | ❌ | ✅ (sealed) |
| Null 安全 | ⚠️ (Optional) | ❌ | ✅ (strict) | ✅ (Option) | ❌ | ✅ |
| 模式匹配 | ✅ (switch) | ✅ (match) | ❌ | ✅ | ❌ | ✅ (when) |

## OOP 特性

| 特性 | Java | Python | TypeScript | Rust | Go | Kotlin |
|------|------|--------|------------|------|-----|--------|
| 类和对象 | ✅ | ✅ | ✅ | ⚠️ (struct) | ⚠️ (struct) | ✅ |
| 继承 | 单继承 | 多继承 | 单继承 | ❌ | ❌ | 单继承 |
| 接口 | ✅ | ✅ (ABC) | ✅ | ✅ (trait) | ✅ | ✅ |
| 访问控制 | ✅ | ⚠️ (约定) | ✅ | ✅ | ✅ (包级) | ✅ |
| 抽象类 | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| 数据类 | ✅ (record) | ✅ (dataclass) | ❌ | ✅ (derive) | ❌ | ✅ |

## FP 特性

| 特性 | Java | Python | TypeScript | Rust | Go | Kotlin |
|------|------|--------|------------|------|-----|--------|
| 一等函数 | ✅ (lambda) | ✅ | ✅ | ✅ (closure) | ✅ | ✅ |
| 高阶函数 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 不可变数据 | ✅ (final) | ✅ (frozen) | ✅ (readonly) | ✅ (默认) | ❌ | ✅ (val) |
| Stream/迭代器 | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| 函数组合 | ✅ (andThen) | ⚠️ | ⚠️ | ⚠️ | ❌ | ⚠️ |
| 柯里化 | ⚠️ | ⚠️ | ✅ | ⚠️ | ❌ | ✅ |
| 尾递归优化 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (tailrec) |

## 并发特性

| 特性 | Java | Python | TypeScript | Rust | Go | Kotlin |
|------|------|--------|------------|------|-----|--------|
| 线程 | ✅ | ✅ (GIL) | ❌ (单线程) | ✅ | ✅ (goroutine) | ✅ |
| 协程 | ✅ (虚拟线程) | ✅ (asyncio) | ✅ (async) | ✅ (tokio) | ✅ (goroutine) | ✅ (coroutine) |
| Channel | ❌ | ✅ (asyncio.Queue) | ❌ | ✅ (mpsc) | ✅ | ✅ |
| Actor | ⚠️ (Akka) | ⚠️ | ❌ | ⚠️ (actix) | ❌ | ⚠️ |
| 原子操作 | ✅ | ⚠️ | ❌ | ✅ | ✅ | ✅ |

## 内存管理

| 方式 | 语言 | 特点 |
|------|------|------|
| GC | Java, Python, Go, Kotlin | 自动，有暂停 |
| 所有权系统 | Rust | 编译时保证，零运行时开销 |
| 引用计数 | Swift, Python (部分) | 确定性释放 |
| 手动管理 | C, C++ | 最灵活，最危险 |
| GC + 值类型 | TypeScript (V8) | 引擎优化 |

## 错误处理

| 方式 | 语言 | 示例 |
|------|------|------|
| 异常 | Java, Python, TypeScript | try-catch |
| Result 类型 | Rust | `Result<T, E>` |
| 多返回值 | Go | `value, err := f()` |
| Optional | Java, Kotlin, Swift | `Optional<T>`, `T?` |
| 混合 | Kotlin | 异常 + `Result` + `?` |

## 代码对比：相同功能

```java
// Java：过滤活跃用户的邮箱
List<String> emails = users.stream()
    .filter(User::isActive)
    .map(User::getEmail)
    .sorted()
    .collect(Collectors.toList());
```

```python
# Python
emails = sorted(u.email for u in users if u.is_active)
```

```typescript
// TypeScript
const emails = users
    .filter(u => u.isActive)
    .map(u => u.email)
    .sort();
```

```rust
// Rust
let emails: Vec<&str> = users.iter()
    .filter(|u| u.is_active)
    .map(|u| u.email.as_str())
    .sorted()
    .collect();
```

```go
// Go
var emails []string
for _, u := range users {
    if u.IsActive {
        emails = append(emails, u.Email)
    }
}
sort.Strings(emails)
```

```kotlin
// Kotlin
val emails = users
    .filter { it.isActive }
    .map { it.email }
    .sorted()
```

## 选型建议

| 需求 | 推荐语言 |
|------|---------|
| 企业级后端 | Java / Kotlin / C# |
| 快速原型 | Python |
| Web 全栈 | TypeScript |
| 系统编程 | Rust / C++ |
| 高并发服务 | Go / Kotlin / Java |
| 移动开发 | Kotlin (Android) / Swift (iOS) |
| 数据科学 | Python |
| 嵌入式 | C / Rust |

## 总结

**核心**：了解语言的范式支持能力，在技术选型时做出更好的决策。

**趋势**：现代语言趋向多范式融合 — Kotlin、Rust、Swift 都同时支持 OOP 和 FP。
