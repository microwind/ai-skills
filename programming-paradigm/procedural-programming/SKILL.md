---
name: 过程式编程
description: "基于过程（函数）调用的编程范式，按照步骤顺序执行指令，是最直接的编程方式。"
license: MIT
---

# 过程式编程 (Procedural Programming)

## 概述

过程式编程是最基础的范式之一：**程序由一系列按顺序执行的过程（函数/子程序）组成**，数据和操作数据的函数是分离的。

**核心特征**：
- 自顶向下的程序结构
- 函数/过程是代码组织的基本单元
- 数据和函数分离
- 通过参数传递和返回值通信

## 代码示例

```c
// C 语言：典型的过程式编程
#include <stdio.h>
#include <string.h>

// 数据结构（只有数据，没有行为）
typedef struct {
    char name[50];
    double price;
    int quantity;
} Product;

typedef struct {
    Product items[100];
    int count;
    double total;
} Cart;

// 操作数据的函数
void cart_init(Cart *cart) {
    cart->count = 0;
    cart->total = 0;
}

void cart_add(Cart *cart, const char *name, double price, int qty) {
    Product *p = &cart->items[cart->count++];
    strcpy(p->name, name);
    p->price = price;
    p->quantity = qty;
    cart->total += price * qty;
}

void cart_print(const Cart *cart) {
    for (int i = 0; i < cart->count; i++) {
        printf("%s: %.2f x %d\n",
            cart->items[i].name, cart->items[i].price, cart->items[i].quantity);
    }
    printf("总计: %.2f\n", cart->total);
}

int main() {
    Cart cart;
    cart_init(&cart);
    cart_add(&cart, "键盘", 299.0, 1);
    cart_add(&cart, "鼠标", 99.0, 2);
    cart_print(&cart);
    return 0;
}
```

```python
# Python 过程式风格
def read_csv(file_path: str) -> list[dict]:
    """读取 CSV 文件"""
    import csv
    with open(file_path) as f:
        return list(csv.DictReader(f))

def filter_by_status(records: list, status: str) -> list:
    """按状态过滤"""
    return [r for r in records if r["status"] == status]

def calculate_total(records: list) -> float:
    """计算总金额"""
    return sum(float(r["amount"]) for r in records)

def generate_report(records: list) -> str:
    """生成报告"""
    total = calculate_total(records)
    return f"共 {len(records)} 条记录，总金额: {total:.2f}"

# 主流程：自顶向下
def main():
    records = read_csv("orders.csv")
    active = filter_by_status(records, "active")
    report = generate_report(active)
    print(report)
```

## 过程式 vs OOP

| 维度 | 过程式 | OOP |
|------|--------|-----|
| 组织方式 | 函数 + 数据结构 | 对象（数据+行为） |
| 数据封装 | 无，数据公开 | 有，数据隐藏 |
| 多态 | 函数指针 / switch | 继承和接口 |
| 代码复用 | 函数调用 | 继承和组合 |
| 适合规模 | 小到中型 | 中到大型 |

## 何时使用过程式

```
✅ 适合过程式的场景：
- 脚本和自动化任务
- 数据处理管道（ETL）
- 系统编程（内核、驱动）
- 简单的命令行工具
- 算法实现（排序、搜索）
- 数学计算

❌ 不适合的场景：
- 大型业务系统（缺乏封装）
- GUI 应用（需要事件驱动）
- 需要复杂继承层次的系统
```

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [OOP](../object-oriented-programming/) | OOP 将数据和行为封装在对象中 |
| [FP](../functional-programming/) | FP 强调纯函数和不可变性 |
| [AOP](../aspect-oriented-programming/) | AOP 处理过程式难以处理的横切关注点 |

## 总结

**核心**：数据结构 + 操作函数，自顶向下按步骤执行。

**适用**：脚本、工具、数据处理、算法实现。简单直接，是所有范式的基础。
