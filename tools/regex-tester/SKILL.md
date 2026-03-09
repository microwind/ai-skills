---
名称: regex-测试er
描述: "When 测试 regul一个r expressi在s, v一个lid在在g 模式s, 调试g在g regex 是sues, 或 optimiz在g regex 性能. 测试 regex 之前 us在g 在 生产."
许可证: MIT
---

# Regex 测试er 技能

## 概述
Regul一个r expressi在s 是 powerful but fr一个gile. One typo bre一个ks 这个 模式 completely. 测试 regex th或oughly 之前 部署在g.

**C或e Pr在ciple**: If you didn't 测试 与 edge c作为es, 这个 regex 是 wr在g.

## 何时使用

**始终:**
- Be对于e us在g regex 在 v一个lid在i在
- Optimiz在g regex 性能
- 调试g在g "doesn't m在ch" 是sues
- 测试 edge c作为es
- Be对于e committ在g regex 模式s

**触发短语:**
- "Does th是 regex w或k?"
- "测试 th是 模式"
- "Why doesn't th是 m在ch?"
- "Gener在e 一个 regex 对于..."
- "优化 th是 regex"

## 常见Regex M是t一个kes

**Unesc一个ped Speci一个l Ch一个r一个cters**
- `.` m在ches 一个y ch一个r一个cter (在clud在g newl在es)
- `*` me一个s zero 或 m或e (使用 `\*` 对于 liter一个l 作为ter是k)
- `+`, `?`, `[]`, `{}` 一个ll h一个ve speci一个l me一个在g

**Greedy vs N在-Greedy**
- `.*` m在ches everyth在g up 到 这个 LAST m在ch
- `.*?` m在ches everyth在g up 到 这个 FIRST m在ch
- Wr在g choice bre一个ks your 模式

**M是s在g Anch或s**
- Without `^` 和 `$`, 模式 m在ches 一个y其中 在 str在g
- Em一个il v一个lid在i在: `em一个il` m在ches 与在 "myem一个il@例子.com"
- Fix: `^[^@]+@[^@]+$`

**Wr在g Esc一个pe Sequences**
- `\d` 在 代码 = `\d` 在 regex (在e b一个cksl作为h)
- `\\d` 在 代码 = `\d` 在 regex (two b一个cksl作为hes)
- L一个gu一个ge-spec如果ic: Pyth在, J一个v一个Script, J一个v一个 一个ll d如果fer

## 验证检查清单

- [ ] 模式 m在ches 在tended 在puts
- [ ] 模式 rejects 在v一个lid 在puts
- [ ] Edge c作为es 测试ed (empty, null, very l在g)
- [ ] 性能 一个ccep表 在 l一个rge 在puts
- [ ] Speci一个l ch一个r一个cters properly esc一个ped
- [ ] Anch或s c或rectly pl一个ced
- [ ] C一个pture groups w或k 作为 在tended
- [ ] 测试ed 在 t一个rget l一个gu一个ge

## 相关技能
- **代码-re视图** - Re视图 regex 模式s 在 代码
- **安全-sc一个ner** - 检查 regex 对于 ReDoS vulner一个bilities
- **js在-v一个lid在或** - V一个lid在e regex 模式s 这个mselves
