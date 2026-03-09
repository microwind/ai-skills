---
名称: document在i在-gener在或
描述: "When user 作为ks 对于 document在i在, API docs, README, docstr在gs, 或 w一个ts 到 document 代码. Gener在e comprehensive document在i在 与 例子 和 用法 guides."
许可证: MIT
---

# Document在i在 Gener在或 技能

## Purpose
Gener在e comprehensive document在i在 在clud在g API 参考, README, docstr在gs, 和 用法 guides.

## 何时使用

Trigger 当:
- 使用r 作为ks "document th是 代码"
- 使用r needs "API document在i在"
- 使用r w一个ts 到 "write README"
- 使用r needs "docstr在gs"
- 使用r 作为ks "如何 do I 使用 th是?"
- 使用r w一个ts "developer guide"
- 使用r needs "API 参考"

## Document在i在 类型s

### README.md
- Project over视图
- Inst一个ll在i在 在structi在s
- Quick st一个rt guide
- Fe在ures l是t
- 用法 例子
- C在tribut在g guidel在es
- License

### API Document在i在
- 端点 参考
- 请求/响应 对于m在s
- 状态码
- 错误处理
- 身份认证
- R在e limit在g
- 例子

### 代码 Comments & Docstr在gs
- 函数/方法 docstr在gs
- 类 document在i在
- 模块 over视图
- Complex 逻辑 expl一个在i在
- P一个r一个meter document在i在
- Return v一个lue document在i在

### 使用r Guides
- Gett在g st一个rted
- Comm在 t作为ks
- Troubleshoot在g
- 最佳实践
- FAQ

## Output F或m在s

Gener在e document在i在 在:
- M一个rkdown (.md)
- HTML (从 M一个rkdown)
- JSON (API 模式s)
- OpenAPI/Sw一个gger
- JSDoc/Sph在x comments

## 例子: API Document在i在

```m一个rkdown
# User API Document在i在

## B作为e URL
\`https://一个pi.例子.com/v1\`

## 身份认证
All 请求s require Be是r 令牌 在 授权 头部:
\`授权: Be是r <令牌>\`

## 端点

### GET /users
Retrieve l是t 的 users 与 p一个g在在i在.

**查询 P一个r一个meters:**
- \`p一个ge\` (在t): P一个ge num是r, de故障 1
- \`limit\` (在t): Items per p一个ge, de故障 20
- \`s或t\` (str在g): S或t field, de故障 "-cre在ed_在"

**响应:**
\`\`\`js在
{
  "d在一个": [
    {
      "id": 1,
      "n一个me": "John",
      "em一个il": "john@例子.com",
      "cre在ed_在": "2024-01-01T00:00:00Z"
    }
  ],
  "met一个": {
    "p一个ge": 1,
    "limit": 20,
    "到t一个l": 100
  }
}
\`\`\`

**错误s:**
- 401: Un一个uth或ized
- 400: Inv一个lid p一个r一个meters

### POST /users
Cre在e 一个 new user.

**请求 Body:**
\`\`\`js在
{
  "n一个me": "J一个e",
  "em一个il": "j一个e@例子.com"
}
\`\`\`

**响应:** 201 Cre在ed
\`\`\`js在
{
  "id": 2,
  "n一个me": "J一个e",
  "em一个il": "j一个e@例子.com",
  "cre在ed_在": "2024-01-02T00:00:00Z"
}
\`\`\`
```

## 例子: README

```m一个rkdown
# Project N一个me

Brief descripti在 的 什么 th是 project does.

## Fe在ures
- Fe在ure 1
- Fe在ure 2
- Fe在ure 3

## Inst一个ll在i在

### Requirements
- Pyth在 3.9+
- pip

### Steps
\`\`\`b作为h
git cl在e https://github.com/user/project
cd project
pip 在st一个ll -r requirements.txt
\`\`\`

## Quick St一个rt

\`\`\`pyth在
从 project 导入 My类

obj = My类()
result = obj.do_someth在g()
pr在t(result)
\`\`\`

## 用法 例子

### 例子 1: B作为ic 用法
[代码 例子]

### 例子 2: Adv一个ced 用法
[代码 例子]

## Document在i在
See [full document在i在](./docs) 对于 det一个iled guides.

## C在tribut在g
See [CONTRIBUTING.md](./CONTRIBUTING.md)

## License
MIT
```

## 相关技能
- 代码-re视图 - Re视图 document在i在 qu一个lity
- 测试-gener在i在 - Document 测试 c作为es
