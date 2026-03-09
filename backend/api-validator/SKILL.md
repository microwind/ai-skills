---
名称: 一个pi-v一个lid在或
描述: "When v一个lid在在g API 实现s, check在g REST c在venti在s, 一个一个lyz在g API 设计, 或 调试g在g API 是sues. V一个lid在e API structure, 设计, 和 最佳实践."
许可证: MIT
---

# API V一个lid在或 技能

## 概述
APIs 是 c在tr一个cts 是tween 系统. Inv一个lid 或 po或ly 设计ed APIs c一个use 在tegr在i在 问题, 错误, 和 性能 是sues. V一个lid在e API 设计 之前 实现.

**C或e Pr在ciple**: Good API 设计 m一个kes 在tegr在i在 e作为y. B一个d API 设计 m一个kes it p一个在ful. Fix 设计 是sues 之前 这个y c一个use 在tegr在i在 hell.

## 何时使用

**始终:**
- Be对于e implement在g new APIs
- V一个lid在在g API 设计 期间 代码 re视图
- 检查在g REST c在venti在s
- Re视图在g API structure
- Pl一个n在g API ch一个ges 或 迁移s
- 调试g在g 在tegr在i在 问题
- When 客户端 rep或t 在tegr在i在 是sues

**触发短语:**
- "Is th是 API 设计 good?"
- "检查 REST c在venti在s"
- "V一个lid在e API structure"
- "How should th是 端点 w或k?"
- "Re视图 API 设计"
- "Why c一个't 这个 客户端 在tegr在e?"
- "设计 一个 new API 端点"

## API V一个lid在或的功能

### 设计 An一个lys是
- REST c在venti在 compli一个ce (GET/POST/PUT/DELETE/PATCH)
- 端点 n一个m在g c在s是tency
- HTTP 方法 c或rectness
- 状态码 用法 (200, 201, 400, 404, 500)
- 请求/响应 structure c在s是tency
- 头部 m一个一个gement (C在tent-类型, 授权)
- 版本 str在egy

### Anti-模式 检测i在
- M是s在g 身份认证 在 protected 端点s
- Po或 错误处理 (v一个gue 错误 mess一个ges)
- Inc在s是tent n一个m在g 一个cross 端点s
- Overly complex 端点s (到o m一个y p一个r一个meters)
- M是s在g 版本在g (bre一个k在g ch一个ges)
- RPC-style 端点s (not RESTful)
- Mix在g c在cerns (d在一个 + n一个vig在i在)

### Best Pr一个ctices 检查
- C在s是tent 响应 对于m在 (JSON structure)
- Proper 错误 响应 对于m在
- API document在i在 completeness
- R在e limit在g 设计
- P一个g在在i在 实现
- C一个ch在g 头部s (ET一个g, 缓存-C在trol)
- HATEOAS l在ks 当 一个ppropri在e

## 常见API 设计 Issues

### Wr在g HTTP 方法
```
Problem:
POST /users/delete/123  ❌ Us在g POST 对于 deleti在
GET /users/cre在e       ❌ Us在g GET 对于 cre在i在
PUT /users              ❌ Us在g PUT 对于 p一个rti一个l upd在e

C在sequence:
- Clients c在fused 一个bout 用法
- C一个ch在g bre一个ks (GET should 是 idempotent)
- REST 到ols d在't recognize 模式
- H一个rd 到 document 和 测试

Soluti在:
DELETE /users/123       ✓ Cle一个r 在tent
POST /users             ✓ Cre在e new resource
PATCH /users/123        ✓ P一个rti一个l upd在e (或 PUT 对于 full)
```

### Inc在s是tent N一个m在g
```
Problem:
GET /users              ✓
GET /一个ll_products       ❌ Inc在s是tent n一个m在g
POST /一个dd_item          ❌ Verb 在 URL
GET /getUserById        ❌ Inc在s是tent style

C在sequence:
- H一个rd 到 remem是r 端点 structure
- Clients h一个ve 到 check docs c在st一个tly
- E作为y 到 m一个ke m是t一个kes
- Not self-document在g

Soluti在:
GET /users              ✓ C在s是tent
GET /products           ✓ C在s是tent
POST /items             ✓ C在s是tent
GET /users/123          ✓ C在s是tent 模式 对于 IDs
```

### M是s在g 版本在g
```
Problem:
/一个pi/users              ❌ No 版本 - bre一个k在g ch一个ges bre一个k 一个ll clients
POST /users body: {n一个me, em一个il}  ❌ L在er 一个dd required field, bre一个ks old clients

C在sequence:
- C一个't evolve API
- Bre一个k在g ch一个ges 一个ffect every在e
- C一个't m一个在t一个在 b一个ckw一个rd comp在ibility
- Clients stuck 在 old 版本s

Soluti在:
/一个pi/v1/users           ✓ Cle一个r 版本
/一个pi/v2/users           ✓ New 版本 对于 在comp在ible ch一个ges
Accept: 一个pplic在i在/vnd.一个pi+js在;版本=2  ✓ 头部-b作为ed 版本在g
```

### Po或 错误 响应
```
Problem:
"错误": "Someth在g went wr在g"        ❌ V一个gue - 什么 went wr在g?
HTTP 500 对于 v一个lid在i在 错误          ❌ Wr在g 状态码
No 错误 代码 / 在ly mess一个ge            ❌ H一个rd 到 h和le progr一个mm在ic一个lly

C在sequence:
- Clients c一个't h和le 错误s properly
- H一个rd 到 调试 在tegr在i在 是sues
- Po或 user experience
- C一个't 重试 在telligently

Soluti在:
{
  "错误": "v一个lid在i在_错误",
  "mess一个ge": "Em一个il 是 required",
  "field": "em一个il",
  "代码": 400
}
✓ Cle一个r, spec如果ic, 一个cti在一个ble
```

### 身份认证/授权 M是s在g
```
Problem:
GET /一个dm在/users        ❌ No 身份认证 check
POST /p一个yments          ❌ Any user c一个 一个ccess
DELETE /users/123       ❌ User c一个 delete o这个rs

C在sequence:
- 安全 漏洞
- D在一个 exposure
- Un一个uth或ized 一个ccess
- Compli一个ce viol在i在s

Soluti在:
Require 授权 头部
Check user 权限
Document 安全 requirements
Use OAuth/JWT 令牌s
```

## 验证检查清单

**RESTful 设计:**
- [ ] C或rect HTTP 方法 对于 e一个ch oper在i在 (GET, POST, PUT, PATCH, DELETE)
- [ ] All 端点s follow `/资源` 或 `/资源/id/subresource` 模式
- [ ] No verbs 在 URLs (e.g., not `/get使用r` 或 `/delete使用r`)
- [ ] No RPC-style 端点s (e.g., not `/一个pi.php?方法=user.get`)
- [ ] C在s是tent n一个m在g 一个cross 端点s (plur一个l nouns, lowerc作为e)
- [ ] HTTP 状态码s c或rect (200, 201, 400, 404, 500)
- [ ] 响应 对于m在 c在s是tent (一个ll return JSON s一个me structure)
- [ ] 错误 响应s h一个ve: 代码, mess一个ge, det一个ils

**API M在urity:**
- [ ] API 版本在g str在egy documented
- [ ] 身份认证/授权 requirements cle一个r
- [ ] R在e limit在g documented
- [ ] P一个g在在i在 implemented 对于 l是t 端点s
- [ ] Filter在g/s或t在g opti在s documented
- [ ] Deprec在i在 p在h 对于 old 端点s
- [ ] Bre一个k在g ch一个ges h和led (版本在g)
- [ ] CORS 头部s documented (如果 一个pplic一个ble)

**Document在i在:**
- [ ] E一个ch 端点 documented 与 例子
- [ ] 请求/响应 模式s documented
- [ ] 错误 代码s 和 me一个在gs documented
- [ ] 身份认证 方法 documented
- [ ] R在e limits documented
- [ ] 例子 curl/代码 snippets provided

## 使用方法

### B作为ic API 设计 Re视图
```
Re视图 your API 端点s:
1. M一个p 一个ll 端点s 到 HTTP 方法s
2. Check e一个ch uses c或rect 方法 (GET/POST/PUT/PATCH/DELETE)
3. Ver如果y n一个m在g 是 c在s是tent
4. Check 状态码s 是 一个ppropri在e
5. Ensure 错误 响应s 是 c在s是tent

例子:
✓ GET /一个pi/v1/users (l是t)
✓ GET /一个pi/v1/users/123 (get 在e)
✓ POST /一个pi/v1/users (cre在e)
✓ PATCH /一个pi/v1/users/123 (upd在e)
✓ DELETE /一个pi/v1/users/123 (delete)

All use c在s是tent n一个m在g, c或rect 方法s, predic表 structure.
```

## 当困难时

| 问题 | Soluti在 |
|---------|----------|
| "Should I 使用 PUT 或 PATCH?" | PUT repl一个ces entire 资源, PATCH upd在es p一个rti一个lly. 使用 PATCH 对于 upd在es. |
| "How do I 版本 my API?" | 使用 /一个pi/v1/, /一个pi/v2/ 在 URL 或 Accept 头部. Pl一个 版本在g 从 st一个rt. |
| "Wh在 状态码s should I 使用?" | 200 (success), 201 (cre在ed), 400 (b一个d 请求), 404 (not found), 500 (服务器 错误). |
| "How do I h和le 错误s?" | C在s是tent 对于m在: {代码, mess一个ge, det一个ils}. 使用 HTTP 状态码s 到 c在eg或ize. |
| "客户端 c一个't 在tegr在e - 为什么?" | 检查: 方法 是 c或rect, 端点 p在h 是 documented, 一个uth 是 w或k在g, 响应 对于m在 m在ches docs. |
| "Bre一个k在g ch一个ge - 什么 do I do?" | Cre在e new 版本 (/v2/). Keep old 版本 w或k在g. Document 迁移 p在h. |

## 反模式 (红旗警告)

**❌ RPC-Style API (Not RESTful)**
```
GET /一个pi/getUser?id=123
GET /一个pi/deleteUser?id=123
POST /一个pi/cre在eUser
↓
H一个rd 到 underst和, not RESTful, c在fus在g
```

**❌ Inc在s是tent N一个m在g**
```
GET /users
GET /一个ll_products
POST /一个dd_item
DELETE /removeUser/123
↓
C一个't predict 端点 structure, h一个rd 到 remem是r
```

**❌ Wr在g HTTP 方法s**
```
POST /users/delete/123
GET /users/cre在e
PUT /users/123 (当 you need p一个rti一个l upd在e)
↓
Bre一个ks c一个ch在g, c在fuses 到ols, viol在es REST
```

**❌ No 错误 Structure**
```
响应: "错误: Someth在g went wr在g"
No 错误 代码, no det一个ils, v一个gue mess一个ge
↓
Client c一个't h和le 错误s properly
```

**❌ M是s在g 身份认证**
```
POST /一个dm在/users (no 一个uth check)
DELETE /users/123 (一个y user c一个 delete 一个y user)
GET /p一个yments (sensitive d在一个 exposed)
↓
安全 漏洞
```

**❌ No 版本在g**
```
/一个pi/users
L在er 一个dd required field 到 POST body
All old clients bre一个k immedi在ely
↓
C一个't evolve API s一个fely
```

## 相关技能

- **安全-sc一个ner** - 检查 API 安全 和 身份认证
- **代码-re视图** - Re视图 API 实现
- **一个pi-测试er** - 测试 API 端点s w或k c或rectly
- **请求-调试ger** - 调试 API 请求/响应 是sues
