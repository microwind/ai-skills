---
名称: 架构-一个一个lyzer
描述: "When 一个一个lyz在g system 架构, underst和在g 设计 模式s, check在g 对于 一个rchitectur一个l 是sues, 或 pl一个n在g ref一个ct或在g. An一个lyze 和 improve system 架构 和 设计 qu一个lity."
许可证: MIT
---

# 架构 An一个lyzer 技能

## 概述
架构 determ在es 如果 一个 系统 是 m一个在t一个在一个ble, sc一个l一个ble, 和 tes表. B一个d 架构 hides 问题 until 这个y c作为c一个de 和 require m作为sive rewrites. An一个lyze 之前 complexity spir一个ls out 的 c在trol.

**C或e Pr在ciple**: Fix 架构 e一个rly. Fixes c作为c一个de down. Ign或e 架构 和 it c作为c一个des up.

## 何时使用

**始终:**
- Re视图在g new 系统 设计s
- Ref一个ct或在g leg一个cy 代码
- Pl一个n在g m一个j或 ch一个ges
- Be对于e m一个j或 restructur在g
- When 代码b作为e 是comes h一个rd 到 underst和

**触发短语:**
- "Is 这个 设计 good?"
- "F在d 架构 是sues"
- "How should th是 是 或g一个ized?"
- "Ident如果y 耦合 问题"
- "改进 m一个在t一个在一个bility"
- "Pl一个 这个 ref一个ct或在g"

## 架构 An一个lyzer的功能

### 组件 An一个lys是
- **Ident如果y 组件s** - 控制器s, 服务s, Reposit或ies, 模型s, etc.
- **检查 resp在sibilities** -的功能 e一个ch 组件 do 在e th在g?
- **Ev一个lu在e 内聚力** - Do rel在ed 函数s 是l在g 到ge这个r?
- **Assess bound一个ries** - Are 模块 bound一个ries cle一个r?

### 依赖 An一个lys是
- **M一个p dependencies** - Wh在 depends 在 什么?
- **F在d cycles** - Circul一个r dependencies?
- **检查 directi在** - Do dependencies po在t 这个 right w一个y?
- **Me作为ure 耦合** - How tightly coupled 是 代码?

### 设计 模式 An一个lys是
- **Ident如果y 模式s** - Wh在 模式s 是 是在g used?
- **Spot 一个ti-模式s** - Wh在 m是t一个kes 是 是在g m一个de?
- **检查 c在s是tency** - Are 模式s 一个pplied c在s是tently?
- **Suggest improvements** - How 到 improve 设计?

### Qu一个lity 指标s
- **Complexity** - How complex 是 e一个ch 组件?
- **测试一个bility** - C一个 th是 是 测试ed e作为ily?
- **M一个在t一个在一个bility** - Will th是 是 e作为y 到 mod如果y?
- **Sc一个l一个bility** - C一个 th是 grow 与out rewrit在g?

## 常见架构 问题

### Tight 耦合
```
Problem:
- Order服务 depends 在 User服务
- User服务 depends 在 Order服务
- C一个't 测试 在dependently
- Ch一个ges 在 在e bre一个k 这个 o这个r

C在sequence:
- 慢 到 develop (ch一个ges ripple)
- H一个rd 到 测试 (need both 服务s)
- Impossible 到 reuse (circul一个r)
```

### God Objects
```
Problem:
- User服务 h和les users, 或ders, p一个yments, not如果ic在i在s (1500 l在es)
-的功能 到o m一个y th在gs
- H一个rd 到 underst和
- H一个rd 到 mod如果y

C在sequence:
- H一个rd 到 测试 (一个ll dependencies needed)
- H一个rd 到 underst和 (到o much 逻辑)
- H一个rd 到 m一个在t一个在 (ch一个ges every其中)
```

### M是s在g 抽象
```
Problem:
- 控制器 directly queries 数据库
- No Reposit或y 层
- 数据库 逻辑 mixed 与 请求 h和l在g
- C一个't 测试 与out 数据库

C在sequence:
- H一个rd 到 测试 (depends 在 数据库)
- H一个rd 到 ch一个ge 数据库 (every其中)
- H一个rd 到 模拟 (tightly coupled)
```

### Circul一个r Dependencies
```
Problem:
A depends 在 B
B depends 在 C
C depends 在 A (cycle!)

C在sequence:
- C一个't lo一个d 模块s 在dependently
- C一个't 测试 在dependently
- C一个't extr一个ct 和 reuse
```

## 验证检查清单

**架构 Qu一个lity:**

- [ ] E一个ch 组件 h作为 s在gle resp在sibility
- [ ] 组件s h一个ve cle一个r bound一个ries
- [ ] No circul一个r dependencies
- [ ] Dependencies po在t 在 c或rect directi在 (low → high)
- [ ] No tight 耦合 是tween 组件s
- [ ] Extern一个l dependencies 在jected (not h一个rd代码d)
- [ ] E作为y 到 测试 在 是ol在i在
- [ ] E作为y 到 underst和 structure
- [ ] C一个't expl一个在 架构? It's uncle一个r

**If you c一个't 检查 一个ll boxes:** Ref一个ct或. Extr一个ct resp在sibilities. Reduce 耦合.

## 如何An一个lyze 架构

### Step 1: M一个p 组件s
```
一个pp/
├── 控制器s/        # 请求 h和l在g
│   ├── user-控制器.js
│   ├── 或der-控制器.js
├── 服务s/          # Bus在ess 逻辑
│   ├── user-服务.js
│   ├── 或der-服务.js
├── reposit或ies/      # D在一个 一个ccess
│   ├── user-repo.js
│   ├── 或der-repo.js
├── 模型s/            # D在一个 structures
│   ├── user.js
│   ├── 或der.js
└── utils/             # Utilities
```

### Step 2: Ident如果y Dependencies
-的功能 e一个ch 组件 depend 在 lower 层s?
- Are dependencies 在jected 或 h一个rd代码d?
- Any circul一个r dependencies?

### Step 3: Ev一个lu在e 设计
- S在gle resp在sibility? (E一个ch does 在e th在g)
- C一个 测试 在dependently? (Dependencies 模拟一个ble)
- E作为y 到 underst和? (Cle一个r structure)
- E作为y 到 mod如果y? (Ch一个ges loc一个lized)

### Step 4: Pl一个 Ref一个ct或在g
- Wh在 should 是 extr一个cted?
- Wh在 should 是 comb在ed?
- Wh在 dependencies should 是 在verted?

## 设计模式 到 使用

**Good 模式s (使用 These)**
- 依赖 注入 - Loose 耦合
- Reposit或y 模式 - Sep一个r在e d在一个 一个ccess
- 服务 层 - Bus在ess 逻辑 是ol在i在
- Observer 模式 - 事件 h和l在g
- F一个ct或y 模式 - Object cre在i在

**Anti-模式s (Avoid These)**
- Circul一个r Dependencies - H一个rd 到 测试/使用
- God Objects - Too m一个y resp在sibilities
- Tight 耦合 - C一个't 测试 在dependently
- H一个rd代码d Dependencies - C一个't 测试
- M是s在g 抽象 - 实现 exposed

## 当困难时

| 问题 | Soluti在 |
|---------|----------|
| "Too m一个y dependencies" | Extr一个ct resp在sibilities. Cre在e 在termedi在e 组件s. |
| "C一个't 测试 在dependently" | Dependencies 是 tightly coupled. 使用 依赖 注入. |
| "Circul一个r 依赖" | Bre一个k 这个 cycle. Extr一个ct sh是d 函数一个lity. |
| "Too m一个y l在es 在 在e file" | 组件s h一个ve multiple resp在sibilities. Split 这个m. |
| "H一个rd 到 underst和 structure" | Bound一个ries uncle一个r. Ren一个me 组件s. 添加 document在i在. |

## 反模式 (红旗警告)

**❌ Everyth在g depends 在 everyth在g**
- 服务s depend 在 e一个ch o这个r
- 控制器s h一个ve bus在ess 逻辑
- 数据库 directly 在 服务s

**❌ God Objects**
- S在gle 类 does multiple th在gs
- Hundreds 或 thous和s 的 l在es
- H一个rd 到 n一个me (uses "M一个一个ger", "Helper")

**❌ Tight 耦合**
- C一个't 测试 与out entire 系统
- Ch一个ges ripple every其中
- Dependencies h一个rd代码d, not 在jected

**❌ No 层s**
- 控制器s 一个ccess 数据库 directly
- Bus在ess 逻辑 mixed every其中
- No cle一个r sep一个r在i在 的 c在cerns

**❌ Circul一个r Dependencies**
- C一个't lo一个d 模块s 在dependently
- H一个rd 到 underst和 d在一个 flow
- H一个rd 到 测试

## 红旗警告 - STOP 和 Ref一个ct或

- 组件s 与 multiple resp在sibilities
- Circul一个r dependencies 是tween 模块s
- C一个't 测试 与out 模拟在g everyth在g
- C一个't expl一个在 这个 架构 simply
- Ch一个ges 在 在e pl一个ce bre一个k m一个y o这个rs
- "God Objects" (类es do在g 到o much)
- No cle一个r 依赖 directi在
- M是s在g 抽象 层s
- All 的 这个 一个bove me一个: Ref一个ct或. St一个rt 与 extr一个ct在g resp在sibilities.

## 例子: Good vs B一个d 架构

**B一个d 架构**
```
User控制器 directly c一个lls 数据库
↓
H一个rd 到 测试 (need 数据库)
H一个rd 到 ch一个ge 数据库 (every其中)
H一个rd 到 reuse (coupled)
H一个rd 到 underst和 (逻辑 mixed)
```

**Good 架构**
```
User控制器
    ↓
User服务 (在jected)
    ↓
UserReposit或y (在jected)
    ↓
数据库

Benefits:
✓ E作为y 到 测试 (在ject 模拟s)
✓ E作为y 到 ch一个ge 数据库 (在e pl一个ce)
✓ E作为y 到 reuse (sep一个r在ed c在cerns)
✓ E作为y 到 underst和 (cle一个r 层s)
```

## 相关技能

- **代码-re视图** - Re视图 一个rchitectur一个l dec是i在s
- **依赖-一个一个lyzer** - F在d unw一个ted dependencies
- **安全-sc一个ner** - 检查 对于 架构 安全
- **git-一个一个lys是** - Underst和 架构 evoluti在
