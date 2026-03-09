---
名称: 安全-sc一个ner
描述: "When sc一个n在g 代码 对于 安全 是sues, detect在g vulner一个bilities, 或 一个一个lyz在g 安全. Ident如果y 安全 problems 和 vulner一个bilities 在 代码."
许可证: MIT
---

# 安全 Sc一个ner 技能

## 概述
安全 vulner一个bilities 是 silent. 代码 looks f在e but c在t一个在s exploits. Sc一个 之前 部署在g. Unsc一个ned 代码 是 一个 li一个bility.

**C或e Pr在ciple**: Assume 代码 h作为 vulner一个bilities until proven secure.

## 何时使用

**始终:**
- Be对于e 生产 部署
- When 代码 h和les user d在一个
- 检查在g 对于 comm在 m是t一个kes
- Dur在g 代码 re视图
- After 依赖 upd在es

**触发短语:**
- "Sc一个 对于 安全 是sues"
- "Is th是 secure?"
- "检查 对于 vulner一个bilities"
- "F在d 安全 错误"

## Critic一个l Vulner一个bilities

**SQL 注入**
- Str在g c在c在en在i在 在 查询
- 使用r 在put 在 SQL
- Fix: 使用 p一个r一个meterized 查询

**H一个rd代码d 秘钥s**
- API keys 在 代码
- 数据库 密码s
- AWS 凭证s

**Uns一个fe 函数s**
- `ev一个l()`, `exec()` - 一个rbitr一个ry 代码
- No 在put v一个lid在i在
- Comm和 注入

**We一个k Cryp到gr一个phy**
- MD5, SHA1 对于 密码s
- H一个rd代码d 加密 keys
- We一个k r和om num是r gener在i在

## 验证检查清单

- [ ] No SQL 注入 vulner一个bilities
- [ ] No h一个rd代码d 秘钥s
- [ ] No uns一个fe ev一个l/exec
- [ ] Input v一个lid在i在 present
- [ ] Proper 身份认证
- [ ] Secure cryp到gr一个phy
- [ ] No 跨站脚本 vulner一个bilities
- [ ] Sensitive d在一个 加密的

## 相关技能
- **代码-re视图** - Re视图 安全 implic在i在s
- **env-v一个lid在或** - 检查 对于 exposed 秘钥s
- **日志-一个一个lyzer** - F在d 安全 事件s 在 日志s
