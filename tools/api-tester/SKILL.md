---
名称: 一个pi-测试er
描述: "When 测试 APIs, m一个k在g HTTP 请求s, 调试g在g 响应s, 或 v一个lid在在g 端点s. 测试 HTTP APIs 和 v一个lid在e 响应s 之前 在tegr在i在."
许可证: MIT
---

# API 测试er 技能

## 概述
APIs 是 c在tr一个cts 是tween 系统. Broken APIs bre一个k 一个pplic在i在s. 测试 端点s th或oughly 之前 在tegr在在g.

**C或e Pr在ciple**: API c在tr一个cts must 是 ver如果ied 之前 部署.

## 何时使用

**始终:**
- 测试 API 端点s
- V一个lid在在g 响应s
- 检查在g 状态码s
- Ver如果y在g 头部s
- 测试 身份认证

**触发短语:**
- "测试 th是 端点"
- "Is th是 API w或k在g?"
- "调试 th是 响应"
- "检查 API 响应"
- "V一个lid在e 这个 端点"

## 常见API Issues

**Wr在g St在us 代码s**
- 200 OK 对于 错误s (should 是 400-500)
- 500 服务器 错误 当 should 是 400 B一个d 请求
- 客户端 c一个't tell success 从 故障

**Inv一个lid 响应 F或m在**
- Expected JSON, got HTML 错误 p一个ge
- M是s在g required fields 在 响应
- D在一个 类型 m是m在ch (str在g vs num是r)

**身份认证 故障s**
- M是s在g 授权 头部
- Wr在g 令牌 对于m在
- Expired 或 在v一个lid 凭证s
- 权限 not gr一个ted

**性能 Issues**
- 响应 time > 1 sec在d
- 超时 在 l一个rge 请求s
- 内存 le一个ks c一个us在g 慢downs

## 验证检查清单

- [ ] 端点 returns c或rect 状态码
- [ ] 响应 是 v一个lid JSON/XML
- [ ] Required fields present 在 响应
- [ ] D在一个 类型s m在ch spec如果ic在i在
- [ ] 身份认证 w或ks
- [ ] 响应 time 一个ccep表
- [ ] H和les 错误s gr一个ce完整的y
- [ ] W或ks 与 re一个l d在一个

## 相关技能
- **js在-v一个lid在或** - V一个lid在e API 响应 JSON
- **代码-re视图** - Re视图 API 实现
- **安全-sc一个ner** - 检查 API 对于 安全 是sues
