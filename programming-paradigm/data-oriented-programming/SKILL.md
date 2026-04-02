---
name: 面向数据编程
description: "以数据布局和访问模式为核心的编程范式，优化缓存利用率和内存访问性能。"
license: MIT
---

# 面向数据编程 (Data-Oriented Programming/Design)

## 概述

面向数据编程（DOP/DOD）以**数据的布局和访问模式**为核心进行设计，优化 CPU 缓存命中率和内存带宽。

**核心思想**：
- 数据布局决定性能
- 按访问模式组织数据，而非按对象组织
- AoS (Array of Structs) → SoA (Struct of Arrays)
- 数据和行为分离

## AoS vs SoA

```java
// ❌ AoS (Array of Structs)：OOP 风格
class Entity {
    float x, y, z;         // 位置
    float vx, vy, vz;      // 速度
    float health;           // 生命值
    String name;            // 名称
    Texture texture;        // 纹理
}
Entity[] entities = new Entity[10000];

// 更新位置时：遍历所有实体，但每个实体只用到 x,y,z,vx,vy,vz
// 缓存加载了 health, name, texture 但没有使用 → 缓存浪费

// ✅ SoA (Struct of Arrays)：面向数据
class EntityData {
    float[] x, y, z;        // 位置数组
    float[] vx, vy, vz;     // 速度数组
    float[] health;          // 生命值数组
    String[] name;           // 名称数组
}
EntityData data = new EntityData(10000);

// 更新位置时：只遍历 x,y,z,vx,vy,vz 数组
// 缓存行全部是需要的数据 → 缓存命中率高
void updatePositions(EntityData d, int count) {
    for (int i = 0; i < count; i++) {
        d.x[i] += d.vx[i];
        d.y[i] += d.vy[i];
        d.z[i] += d.vz[i];
    }
}
```

## 游戏开发中的 ECS 模式

```python
# Entity-Component-System：面向数据的游戏架构

# Component：纯数据
class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self, vx=0, vy=0):
        self.vx = vx
        self.vy = vy

class Health:
    def __init__(self, hp=100):
        self.hp = hp

# Entity：只是 ID
entity_id = 0

# System：纯逻辑，处理特定组件组合
class MovementSystem:
    def update(self, entities_with_position_and_velocity):
        for entity_id, (pos, vel) in entities_with_position_and_velocity:
            pos.x += vel.vx
            pos.y += vel.vy

class DamageSystem:
    def update(self, entities_with_health):
        for entity_id, health in entities_with_health:
            if health.hp <= 0:
                mark_for_removal(entity_id)
```

## 应用场景

| 场景 | 原因 |
|------|------|
| 游戏引擎 | 大量实体需要高频更新 |
| 物理模拟 | 密集数值计算 |
| 数据处理 | 列式存储优化查询 |
| 嵌入式系统 | 内存和性能受限 |
| 高频交易 | 每微秒都重要 |

## 优缺点

### ✅ 优点
- **高性能** — 缓存友好，向量化优化
- **可预测** — 性能特征容易分析
- **并行友好** — 数据独立，易于 SIMD

### ❌ 缺点
- **可读性差** — 数据和行为分离
- **抽象性低** — 不如 OOP 直观
- **适用面窄** — 主要用于性能关键场景

## 与其他范式的关系

| 范式 | 关系 |
|------|------|
| [OOP](../object-oriented-programming/) | OOP 按对象组织，DOD 按数据布局组织 |
| [FP](../functional-programming/) | FP 的不可变数据有助于数据布局优化 |
| [过程式](../procedural-programming/) | DOD 的系统层面接近过程式风格 |

## 总结

**核心**：按数据访问模式组织数据，优化缓存命中率。

**适用**：游戏引擎、物理模拟、高性能计算等性能关键场景。
