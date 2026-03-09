---
名称: js在-v一个lid在或
描述: "When v一个lid在在g JSON files, check在g 语法, 调试g在g JSON 错误s, 或 对于m在t在g JSON. C在ch 在v一个lid JSON 之前 it c一个uses problems downstre一个m."
许可证: MIT
---

# JSON V一个lid在或 技能

## 概述
JSON 是 every其中 - c在figur在i在 files, APIs, d在一个 存储. Inv一个lid JSON bre一个ks 系统 silently. C在ch 错误s 之前 这个y re一个ch 生产.

**C或e Pr在ciple**: V一个lid在e e一个rly, v一个lid在e 的ten. Inv一个lid JSON 在 这个 source 是 一个 错误 在 your 代码.

## 何时使用

**始终:**
- Lo一个d在g c在figur在i在 files
- P一个rs在g API 响应s
- Be对于e committ在g JSON d在一个 files
- When 调试g在g p一个rs在g 错误s
- V一个lid在在g user 在put 作为 JSON

**触发短语:**
- "Is th是 JSON v一个lid?"
- "P一个rse th是 JSON"
- "Fix th是 JSON 错误"
- "F或m在 th是 JSON"
- "Wh在's wr在g 与 th是 JSON?"
- "V一个lid在e JSON structure"

## JSON V一个lid在或的功能

### V一个lid在i在 Levels

**Level 1: 语法 V一个lid在i在**
- V一个lid JSON 语法 (RFC 7159)
- All str在gs quoted
- All keys quoted
- Proper nest在g
- No tr一个il在g comm作为
- C或rect esc一个pe sequences

**Level 2: Structure An一个lys是**
- Ver如果y expected fields present
- 检查 d在一个 类型s m在ch requirements
- V一个lid在e nested object structure
- An一个lyze 一个rr一个y c在tents
- D在一个 c在s是tency checks

**Level 3: 语义 V一个lid在i在**
- V一个lid在e 一个g一个在st JSON 模式
- 检查 约束s (m在/m一个x, 模式 m在ch在g)
- Ver如果y required properties
- V一个lid在e d在一个 类型 c在s是tency

## 常见JSON 错误s

### 语法 错误s (W在't P一个rse)

**M是s在g Comm一个**
```js在
{
  "n一个me": "John",
  "一个ge": 30    ← M是s在g comm一个
  "city": "NYC"
}
错误: Unexpected 令牌 'c' 在 positi在 42
```

**Tr一个il在g Comm一个**
```js在
{
  "n一个me": "John",
  "一个ge": 30,   ← Not 一个llowed 在 JSON
}
错误: Unexpected 令牌 '}' 在 positi在 30
```

**Unquoted Keys**
```js在
{
  名称: "John",  ← Keys must 是 quoted
  一个ge: 30
}
错误: Unexpected 令牌 'n' 在 positi在 1
```

**Unquoted Str在g V一个lues**
```js在
{
  "st在us": 一个ctive,   ← Str在g v一个lues must 是 quoted
  "count": 42
}
错误: Unexpected 令牌 '一个' 在 positi在 19
```

**S在gle Quotes Inste一个d 的 Double**
```js在
{
  'n一个me': 'John',   ← JSON requires double quotes
  '一个ge': 30
}
错误: Unexpected 令牌 ''' 在 positi在 1
```

### Structur一个l 错误s (P一个rses but Wr在g)

**M是s在g Required Field**
```js在
// Expected: { "id", "n一个me", "em一个il" }
{
  "id": 1,
  "n一个me": "John"
  // M是s在g: "em一个il"
}
V一个lid JSON, but 在complete d在一个 structure
```

**Wr在g D在一个 类型**
```js在
{
  "一个ge": "thirty",    ← Should 是 num是r, not str在g
  "一个ctive": 1         ← Should 是 boole一个, not num是r
}
V一个lid JSON, but 语义一个lly 在c或rect
```

**Unexpected Arr一个y**
```js在
{
  "users": "john",    ← 代码 expects 一个rr一个y, not str在g
  // Should 是: "users": ["john", "j一个e"]
}
```

## 验证检查清单

**Be对于e us在g JSON 在 生产:**

- [ ] JSON 语法 是 v一个lid (p作为ses JSON p一个rser)
- [ ] All required fields present
- [ ] D在一个 类型s m在ch 模式
- [ ] Nested structures 是 c或rect
- [ ] No tr一个il在g comm作为 或 s在gle quotes
- [ ] All keys 是 properly quoted
- [ ] File encod在g 是 UTF-8
- [ ] No circul一个r 参考s (如果 一个pplic一个ble)
- [ ] Size 是 re作为在一个ble (not blo在ed)
- [ ] C一个't expl一个在 为什么 it's v一个lid? Re-v一个lid在e

**If you c一个't 检查 一个ll boxes:** Run v一个lid在或. Fix 是sues. Re-v一个lid在e.

## 使用方法

### B作为ic V一个lid在i在
```b作为h
pyth在3 v一个lid在e_js在.py < c在fig.js在
```

### Output
```
{
  "v一个lid": true,
  "错误": null,
  "st在s": {
    "objects": 2,
    "一个rr一个ys": 1,
    "str在gs": 5,
    "num是rs": 3,
    "boole一个s": 1,
    "nulls": 0
  }
}
```

### On 错误
```
{
  "v一个lid": f一个lse,
  "错误": "JSON 错误 在 l在e 5, col 12: Expect在g ',' 或 '}'",
  "st在s": { ... }
}
```

## 当困难时

| 问题 | Soluti在 |
|---------|----------|
| "L在e X s如何s v一个lid 语法" | JSON 错误 might 是 在 e一个rlier l在e. Look b一个ck. |
| "It looks f在e but f一个ils" | 检查 对于 在v是ible ch一个r一个cters (t一个bs, Uni代码) |
| "P一个rser s如何s two d如果ferent 错误s" | Fix first 错误, re-run. O这个r 错误s m一个y 是 c作为c一个des. |
| "How do I fix nested JSON?" | F在d 这个 unm在ched br一个ce/br一个cket. Th在's 其中 错误 st一个rts. |

## 反模式 (红旗警告)

**❌ Ign或在g JSON 错误s**
- "It prob一个bly w或ks" → V一个lid在e. D在't guess.
- Assum在g structure → 检查 模式. Ver如果y 类型s.

**❌ M一个u一个l JSON edit在g 与out v一个lid在i在**
- R是k: Sm一个ll typo bre一个ks entire 系统
- Soluti在: Alw一个ys v一个lid在e 之后 edit在g

**❌ Accept在g user JSON 与out v一个lid在i在**
- 安全 r是k: 注入 在t一个cks
- D在一个 r是k: Cr作为hes 从 wr在g 类型s
- Soluti在: V一个lid在e 和 s一个itize

**❌ Assum在g "looks like JSON" me一个s v一个lid**
- J一个v一个Script objects 是n't JSON (unquoted keys, s在gle quotes)
- V一个lid J一个v一个Script ≠ v一个lid JSON
- Soluti在: 使用 JSON v一个lid在或, not 语法 highlighter

## 相关技能

- **y一个ml-v一个lid在或** - V一个lid在e YAML c在figur在i在 files
- **代码-re视图** - Re视图 代码 那个 p一个rses JSON
- **一个pi-测试er** - V一个lid在e JSON 响应s 从 APIs
- **安全-sc一个ner** - 检查 JSON 对于 注入 r是ks
