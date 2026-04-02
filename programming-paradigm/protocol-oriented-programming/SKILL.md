---
name: 面向协议编程
description: "以协议（接口/trait）为核心的编程范式，通过协议定义行为契约，支持灵活的多态和代码复用。"
license: MIT
---

# 面向协议编程 (Protocol-Oriented Programming)

## 概述

面向协议编程（POP）由 Apple 在 Swift 中推广：**以协议（Protocol/Interface/Trait）为设计核心**，而非以类层次为核心。

**核心思想**：
- 优先定义协议而非基类
- 通过协议扩展提供默认实现
- 值类型（struct）+ 协议 > 类继承

## Swift 示例

```swift
// ✅ 面向协议设计
protocol Drawable {
    func draw()
}

protocol Resizable {
    func resize(scale: Double)
}

// 协议扩展：提供默认实现
extension Drawable {
    func draw() {
        print("默认绘制: \(type(of: self))")
    }
}

// 值类型 + 协议组合
struct Circle: Drawable, Resizable {
    var radius: Double

    func draw() { print("绘制圆形, 半径: \(radius)") }
    func resize(scale: Double) -> Circle {
        return Circle(radius: radius * scale)
    }
}

struct Square: Drawable, Resizable {
    var side: Double

    func draw() { print("绘制正方形, 边长: \(side)") }
    func resize(scale: Double) -> Square {
        return Square(side: side * scale)
    }
}

// 多态：通过协议
func render(shapes: [Drawable]) {
    shapes.forEach { $0.draw() }
}
```

## Rust Trait

```rust
// Rust 的 Trait 是面向协议编程的体现
trait Summary {
    fn summarize(&self) -> String;

    // 默认实现
    fn preview(&self) -> String {
        format!("{}...", &self.summarize()[..50])
    }
}

struct Article {
    title: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, self.content)
    }
}

// 泛型约束：通过 Trait
fn notify(item: &impl Summary) {
    println!("速报: {}", item.summarize());
}
```

## TypeScript / Java 中的协议思想

```typescript
// TypeScript：接口即协议
interface Serializable {
    serialize(): string;
}

interface Validatable {
    validate(): boolean;
}

// 组合接口
class UserDTO implements Serializable, Validatable {
    constructor(public name: string, public email: string) {}

    serialize(): string { return JSON.stringify(this); }
    validate(): boolean { return this.email.includes('@'); }
}
```

## 与 OOP 继承的对比

| 维度 | 继承 | 协议/接口 |
|------|------|----------|
| 关系 | is-a | can-do |
| 多重复用 | 单继承限制 | 多协议组合 |
| 耦合度 | 高（基类变更影响子类）| 低（只依赖契约）|
| 值类型支持 | 不支持 | 支持 |
| 默认实现 | 通过基类 | 通过协议扩展 |

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [OOP](../object-oriented-programming/) | POP 补充 OOP 中继承的不足 |
| [FP](../functional-programming/) | 协议 + 值类型接近 FP 的不可变思想 |

## 总结

**核心**：以协议定义行为契约，通过协议组合实现灵活的多态和复用。

**实践**：优先 Protocol/Interface/Trait 而非基类继承，用协议扩展提供默认实现。
