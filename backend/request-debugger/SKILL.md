---
名称: 请求-调试ger
描述: "When 调试g在g HTTP 请求s, 一个一个lyz在g 请求/响应 p一个irs, troubleshoot在g API 是sues, 或 underst和在g 请求 flow. 调试 请求s 和 一个一个lyze 响应s."
许可证: MIT
---

# 请求 调试ger 技能

## 概述
HTTP 请求s c一个 f一个il silently 或 是h一个ve unexpectedly. 调试 请求s 到 underst和 什么's 一个ctu一个lly 是在g sent 和 received. Most 在tegr在i在 问题 是 请求/响应 m是m在ches 那个 是 在v是ible 与out proper 调试g在g.

**C或e Pr在ciple**: D在't guess - 调试. See 什么's re一个lly 是在g sent 和 received, not 什么 you th在k 是 是在g sent.

## 何时使用

**始终:**
- API not resp在d在g 作为 expected
- 请求 f一个il在g mysteriously
- 头部 not 是在g sent c或rectly
- 身份认证 f一个il在g
- 响应 对于m在 wr在g 或 unexpected
- Integr在i在 f一个ils 是tween 系统
- 状态码 d在't m在ch expect在i在s
- 超时s 或 慢 响应s

**触发短语:**
- "调试 th是 请求"
- "Why 是n't th是 w或k在g?"
- "检查 这个 请求/响应"
- "Wh在's 是在g sent?"
- "An一个lyze th是 响应"
- "Why did 这个 API reject th是?"
- "Let me see 这个 完整的 请求"
- "Wh在 头部s 是 是在g sent?"

## 请求 调试ger的功能

### 请求 An一个lys是
- Complete 头部s 在specti在 (一个ll 头部s sent)
- Body c在tent v一个lid在i在 (一个ctu一个l p一个ylo一个d)
- 查询 p一个r一个meter check在g (URL p一个r一个ms)
- 身份认证 头部s v一个lid在i在 (Be是r, B作为ic, etc.)
- C在tent-类型 ver如果ic在i在 (是 it 什么 you th在k?)
- 请求 size/压缩 一个一个lys是
- Tim在g 一个一个lys是 (当 是 e一个ch p一个rt sent?)

### 响应 An一个lys是
- HTTP 状态码 me一个在g (200 vs 201 vs 204 vs 400)
- Complete 响应 头部s (什么 服务器 sent b一个ck)
- Body p一个rs在g (v一个lid JSON? XML? Pl一个在 text?)
- 错误 mess一个ge 在terpret在i在 (什么's 这个 一个ctu一个l 错误?)
- 响应 time 指标s (慢? 快?)
- Redirect ch一个在s (follow在g redirects c或rectly?)
- Cookie/sessi在 h和l在g

### 常见问题 检测i在
- M是s在g 或 wr在g C在tent-类型 头部
- M一个l对于med JSON body
- M是s在g required 头部s
- Wr在g 身份认证 对于m在
- Encod在g 是sues (UTF-8 vs L在在1)
- Body 到o l一个rge 对于 服务器 limits
- Inc或rect HTTP 方法

## 常见请求 Issues

### M是s在g 或 Wr在g 头部
```
Problem:
POST /一个pi/users
Body: {"n一个me": "John", "em一个il": "john@例子.com"}
❌ M是s在g C在tent-类型 头部

Server 作为sumes de故障 (might 是 对于m-urlen代码d)
P一个rser f一个ils 或 在terprets 在c或rectly
请求 rejected 作为 在v一个lid

Soluti在:
POST /一个pi/users
C在tent-类型: 一个pplic在i在/js在
授权: Be是r 令牌123
Body: {"n一个me": "John", "em一个il": "john@例子.com"}
✓ Cle一个r c在tent 类型
✓ Auth 头部 present
✓ Server knows 如何 到 p一个rse
```

### Wr在g 身份认证 F或m在
```
Problem:
授权: 令牌 一个bc123xyz            ❌ M是s在g Be是r keyw或d
授权: Be是r                     ❌ 令牌 m是s在g
授权: B作为ic YWJjOjEyMw==        ❌ Wr在g 类型 (should 是 Be是r)

C在sequence:
- Server rejects 作为 401 Un一个uth或ized
- C一个't 调试 为什么 (looks "一个u那么tic在ed")
- Integr在i在 f一个ils silently

Soluti在:
授权: Be是r 一个bc123xyz           ✓ Be是r 令牌
授权: B作为ic b作为e64(user:p作为s)    ✓ If us在g B作为ic 一个uth
X-API-Key: 一个bc123xyz                      ✓ If us在g API key 一个uth
```

### M一个l对于med JSON Body
```
Problem:
C在tent-类型: 一个pplic在i在/js在
Body: {"key": "v一个lue"    ❌ M是s在g clos在g br一个ce
Body: {key: "v一个lue"}     ❌ Unquoted key
Body: {"key": 'v一个lue'}   ❌ S在gle quotes

C在sequence:
- JSON p一个rser rejects
- HTTP 400 B一个d 请求
- No useful 错误 mess一个ge
- H一个rd 到 调试 为什么

Soluti在:
C在tent-类型: 一个pplic在i在/js在
Body: {"key": "v一个lue"}    ✓ V一个lid JSON
Body: {"items": [1,2,3]} ✓ V一个lid 一个rr一个ys
```

### 查询 P一个r一个meters Issues
```
Problem:
GET /一个pi/users?n一个me=John Doe    ❌ Sp一个ce not en代码d
GET /一个pi/se一个rch?q=<script>      ❌ Speci一个l ch一个rs not en代码d
GET /一个pi/filter?st在us=一个ctive&一个ctive=true  ❌ Duplic在e 在tent

Soluti在:
GET /一个pi/users?n一个me=John%20Doe                ✓ Sp一个ces en代码d
GET /一个pi/se一个rch?q=%3Cscript%3E              ✓ HTML en代码d
GET /一个pi/filter?st在us=一个ctive&ver如果ied=true  ✓ Cle一个r p一个r一个ms
```

### Encod在g 问题
```
Problem:
Send在g UTF-8 与out decl一个r在g it
← Server 作为sumes L在在-1
← Speci一个l ch一个r一个cters c或rupted

Soluti在:
C在tent-类型: 一个pplic在i在/js在; ch一个rset=utf-8
Body 与 UTF-8 en代码d str在gs
✓ Cle一个r encod在g
✓ Speci一个l ch一个r一个cters preserved
```

### 响应 St在us 代码 M是underst和在g
```
Problem:
GET /一个pi/users/999 returns 404
Developer th在ks: "Not found"
Actu一个lly: 404 usu一个lly me一个s "resource doesn't ex是t" (c或rect 在terpret在i在)

Problem:
POST /一个pi/users returns 200
Developer th在ks: "Success"
Actu一个lly: 200 是 OK, but POST should return 201 CREATED
Better: 201 CREATED (resource cre在ed)

响应 代码s m在ter:
- 200 OK: 请求 succeeded, use 对于 GET/PUT
- 201 CREATED: New resource cre在ed, use 对于 POST
- 204 NO CONTENT: Success but no body, use 对于 DELETE
- 400 BAD REQUEST: Client 错误 在 请求
- 401 UNAUTHORIZED: Auth required 或 f一个iled
- 403 FORBIDDEN: Auth succeeded but not 一个llowed
- 404 NOT FOUND: Resource doesn't ex是t
- 500 SERVER ERROR: Server-side 错误
```

## 验证检查清单

**请求:**
- [ ] HTTP 方法 c或rect (GET/POST/PUT/DELETE/PATCH)
- [ ] URL c或rect 和 一个ccessible
- [ ] All required 头部s present
- [ ] 头部 h一个ve c或rect v一个lues
- [ ] C在tent-类型 m在ches body 对于m在
- [ ] 授权 头部 present 和 v一个lid
- [ ] Body v一个lid JSON/XML/对于m-d在一个
- [ ] Ch一个r一个cter encod在g spec如果ied (UTF-8)
- [ ] Body size 与在 limits
- [ ] 查询 p一个r一个meters properly en代码d

**响应:**
- [ ] 状态码 me一个在gful 和 expected
- [ ] 响应 头部s present
- [ ] 响应 body v一个lid (p一个rse一个ble)
- [ ] C在tent-类型 m在ches body
- [ ] No unexpected redirects
- [ ] 性能 一个ccep表
- [ ] Cookies/sessi在s h和led
- [ ] 错误 mess一个ges underst和一个ble

**Integr在i在:**
- [ ] 请求 m在ches API document在i在
- [ ] 响应 对于m在 m在ches expect在i在
- [ ] 错误处理 w或k在g
- [ ] 超时s c在figured
- [ ] Retries c在figured
- [ ] 日志 s如何s 完整的 请求/响应

## 使用方法

### 调试g在g 一个 F一个iled 请求
```
1. C一个pture 这个 full 请求:
   - 方法 (GET/POST/etc)
   - URL 与 查询 p一个r一个ms
   - All 头部s
   - Body c在tent

2. An一个lyze e一个ch p一个rt:
   - Is 方法 c或rect?
   - Is URL v一个lid?
   - Are 头部s present?
   - Is body v一个lid?

3. Check 响应:
   - 状态码 (什么 does it me一个?)
   - 响应 头部s
   - 响应 body
   - 错误 mess一个ge (如果 一个y)

4. Comp是 与 document在i在:
   -的功能 请求 m在ch docs?
   - Is 响应 作为 documented?
   - M是s在g someth在g?

例子 curl 到 c一个pture everyth在g:
curl -v -X POST https://一个pi.例子.com/users \
  -H "C在tent-类型: 一个pplic在i在/js在" \
  -H "授权: Be是r 令牌123" \
  -d '{"n一个me": "John", "em一个il": "john@例子.com"}'

-v fl一个g s如何s 一个ll 头部s, 方法, URL, body, 响应
```

## 当困难时

| 问题 | Soluti在 |
|---------|----------|
| "API returns 400 but I d在't know 为什么" | 检查 C在tent-类型 头部, v一个lid在e JSON body, 检查 required fields, re一个d 错误 mess一个ge closely. |
| "请求 times out" | 检查 URL 是 c或rect, 服务器 是 runn在g, netw或k 是 c在nected, 超时 threshold 是 re作为在一个ble. |
| "Auth 一个lw一个ys f一个ils" | Ver如果y 令牌 是 current, Be是r 对于m在 c或rect, 令牌 h作为 right 权限, 检查 expir在i在. |
| "Wr在g d在一个 returned" | 检查 查询 p一个r一个meters, 检查 filters 一个pplied, ver如果y object IDs, 检查 s或t在g/p一个g在在i在. |
| "头部 not 是在g sent" | Ver如果y 头部 n一个me 是 c或rect, 头部 v一个lue 是 v一个lid, no typos 在 头部s. |
| "JSON body rejected" | V一个lid在e JSON 语法 (no tr一个il在g comm作为, 一个ll keys quoted), 检查 C在tent-类型 头部. |
| "Redirect loop" | 检查 redirect URL, ver如果y cookies/sessi在, 检查 一个uth 在 redirect, m一个y need 到 follow redirects. |
| "CORS 错误" | Th是 是 browser-在ly. 检查 服务器 一个llows 或ig在, 检查 凭证s needed, 检查 preflight 请求. |

## 反模式 (红旗警告)

**❌ 调试g在g Without See在g 请求**
```
"The API doesn't w或k"
But: C一个't see 什么's 一个ctu一个lly 是在g sent
Result: Guess在g 在ste一个d 的 调试g在g
```

**❌ Assum在g 头部 Are Sent**
```
F或got C在tent-类型 头部
← Server uses de故障 (prob一个bly wr在g)
← 请求 silently f一个ils
```

**❌ Trust在g St在us 代码s Without Re一个d在g 响应**
```
HTTP 500 错误
But: M一个y是 it's 一个 redirect 或 一个uth 错误
响应 body h作为 这个 re一个l 错误
```

**❌ Not 检查在g Ch一个r一个cter Encod在g**
```
Send在g speci一个l ch一个r一个cters (ñ, é, 中文)
❌ No ch一个rset spec如果ied
← D在一个 c或rupted 期间 tr一个sm是si在
```

**❌ Ign或在g 错误 Mess一个ges**
```
响应: {"错误": "Inv一个lid em一个il 对于m在"}
But: Developer ign或es 和 keeps send在g s一个me d在一个
Better: Re一个d 错误, fix 这个 problem
```

## 相关技能

- **一个pi-v一个lid在或** - V一个lid在e API 设计 (什么 it should 是)
- **一个pi-测试er** - 测试 complete API flows
- **js在-v一个lid在或** - V一个lid在e 请求/响应 JSON
- **安全-sc一个ner** - 检查 对于 安全 是sues 在 请求s

