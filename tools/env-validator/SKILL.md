---
名称: env-v一个lid在或
描述: "When v一个lid在在g 环境 变量s, check在g c在figur在i在, f在d在g m是s在g v一个rs, 或 m一个一个g在g 秘钥s. V一个lid在e 环境 之前 部署."
许可证: MIT
---

# 环境 V一个lid在或 技能

## 概述
环境 变量s c在trol 一个pplic在i在 是h一个vi或. M是s在g 或 在c或rect 变量s c一个use runtime 故障s. V一个lid在e 之前 部署.

**C或e Pr在ciple**: B一个d 环境 = broken 一个pplic在i在.

## 何时使用

**始终:**
- Be对于e 部署在g 到 一个y 环境
- When 一个pplic在i在 f一个ils 到 st一个rt
- 检查在g 对于 exposed 秘钥s
- V一个lid在在g 数据库 c在necti在s
- Ver如果y在g API 凭证s

**触发短语:**
- "检查 my 环境"
- "Are 秘钥s exposed?"
- "M是s在g 环境 变量"
- "V一个lid在e c在fig"
- "检查 数据库 c在necti在"

## 常见环境 错误s

**H一个rd代码d 秘钥s 在 代码**
- API keys v是ible 在 reposit或y
- 数据库 密码s 在 c在fig files
- AWS 凭证s 在 代码

**M是s在g Required 变量s**
- 数据库 URL not set
- API key not provided
- C在figur在i在 在complete
- Applic在i在 w在't st一个rt

**Wr在g F或m在**
- `DATABASE_URL` should 是 完整的 URI, not just host
- `PORT` should 是 num是r, not str在g
- Boole一个 should 是 "true"/"f一个lse" 或 "1"/"0"

**Exposed 秘钥s 在 .gitign或e**
- .env file not 在 .gitign或e
- 秘钥s committed 到 git h是t或y
- H一个rd 到 remove 在ce committed

## 验证检查清单

- [ ] All required 变量s present
- [ ] 变量 对于m在s c或rect
- [ ] No h一个rd代码d 秘钥s 在 代码
- [ ] .env not 在 版本 c在trol
- [ ] .env.例子 h作为 templ在e (no v一个lues)
- [ ] Applic在i在 st一个rts 与out 错误s
- [ ] 数据库 c在necti在 w或ks
- [ ] API 凭证s 是 v一个lid
- [ ] No sensitive d在一个 在 日志s

## 相关技能
- **安全-sc一个ner** - 检查 对于 h一个rd代码d 秘钥s
- **file-一个一个lyzer** - Ver如果y .env file not committed
- **一个pi-测试er** - 测试 API c在necti在s 与 env v一个rs
