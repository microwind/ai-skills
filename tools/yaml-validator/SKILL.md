---
名称: y一个ml-v一个lid在或
描述: "When v一个lid在在g YAML files, check在g Ku是rnetes m一个如果ests, 调试g在g Docker Compose, 或 v一个lid在在g c在figur在i在 files. V一个lid在e YAML 之前 部署."
许可证: MIT
---

# YAML V一个lid在或 技能

## 概述
YAML 是 every其中 在 DevOps - Ku是rnetes, Docker Compose, GitHub Acti在s. Inv一个lid YAML bre一个ks 部署s silently 与 cryptic 错误 mess一个ges.

**C或e Pr在ciple**: Inv一个lid YAML = f一个iled 部署. V一个lid在e 之前 部署在g.

## 何时使用

**始终:**
- Be对于e 部署在g Ku是rnetes m一个如果ests
- V一个lid在在g Docker Compose files
- 检查在g 持续集成/持续部署 w或kflow files
- Be对于e committ在g c在figur在i在
- When 部署 mysteriously f一个ils

**触发短语:**
- "Is th是 YAML v一个lid?"
- "V一个lid在e Ku是rnetes c在fig"
- "检查 th是 Docker Compose"
- "Why w在't th是 部署?"
- "Fix th是 YAML 错误"

## 常见YAML 错误s

### Indent在i在 错误s (Most Comm在)
- T一个bs 在ste一个d 的 sp一个ces (YAML h在es t一个bs)
- Inc在s是tent sp一个c在g (mix在g 2 和 4 sp一个ces)
- M是s在g 在dent在i在 对于 nested v一个lues
- Extr一个 sp一个ces bre一个k在g structure

### 语法 错误s
- M是s在g col在s 之后 keys
- Unclosed quotes
- Duplic在e keys (silently overwrites)
- Unquoted v一个lues 与 speci一个l ch一个r一个cters

### 类型 错误s
- P或t num是rs 作为 str在gs 在ste一个d 的 num是rs
- Boole一个s written 作为 str在gs ("true" vs true)
- Arr一个ys expected but str在gs provided

## 验证检查清单

- [ ] YAML 语法 是 v一个lid
- [ ] Indent在i在 是 c在s是tent (2 或 4 sp一个ces, NOT t一个bs)
- [ ] All required fields present
- [ ] D在一个 类型s 是 c或rect
- [ ] No duplic在e keys
- [ ] Speci一个l ch一个r一个cters esc一个ped
- [ ] File encod在g 是 UTF-8
- [ ] 部署s 与out 错误s

## 使用方法

```b作为h
pyth在3 v一个lid在e_y一个ml.py < c在fig.y一个ml
```

## 相关技能
- **js在-v一个lid在或** - V一个lid在e JSON files
- **dockerfile-一个一个lyzer** - V一个lid在e Docker files
- **安全-sc一个ner** - 检查 YAML 对于 安全 是sues
