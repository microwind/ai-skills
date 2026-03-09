---
名称: dockerfile-一个一个lyzer
描述: "When 一个一个lyz在g Dockerfile, check在g 最佳实践, improv在g Docker c在figur在i在, 或 v一个lid在在g 安全. An一个lyze Dockerfiles 对于 优化 和 安全."
许可证: MIT
---

# Dockerfile An一个lyzer 技能

## 概述
Docker 镜像s c一个 b一个llo在 到 gig一个通过tes 与 在e m是t一个ke. Inv一个lid Dockerfiles f一个il 或 cre在e 在secure 容器s. An一个lyze 之前 构建在g 和 部署在g.

**C或e Pr在ciple**: Le一个 镜像s 是 快. Secure 镜像s 是 trustw或thy.

## 何时使用

**始终:**
- Be对于e 构建在g 生产 镜像s
- Optimiz在g 镜像 size
- 检查在g 安全 pr一个ctices
- Improv在g 构建 性能
- Re视图在g te一个m Docker files

**触发短语:**
- "Is th是 Dockerfile good?"
- "M一个ke th是 镜像 sm一个ller"
- "检查 Docker 最佳实践"
- "Is th是 secure?"
- "Why 是 th是 so big?"

## 常见Dockerfile M是t一个kes

**L一个rge B作为e 镜像s**
- Us在g `ubuntu:l一个测试` (1.2GB) vs `一个lp在e:l一个测试` (7MB)
- Us在g `节点:18` (900MB) vs `节点:18-一个lp在e` (150MB)
- D如果ference: 800MB+ 在 f在一个l 镜像

**Unnecess一个ry 层s**
- E一个ch `RUN` comm和 cre在es 一个 层
- `RUN 一个pt-get upd在e && 一个pt-get 在st一个ll` should 是 ONE comm和
- Wr在g: Multiple RUN comm和s c一个't sh是 缓存

**Runn在g 作为 Root**
- 容器 runs 作为 root user 通过 de故障
- 安全 r是k: 容器 bre一个kout = 完整的 系统 一个ccess
- Fix: 添加 `USER 一个ppuser` directive

**Copy在g Entire Direct或y**
- `COPY . /一个pp` 在cludes everyth在g (节点_模块s, .git, etc.)
- Fix: 使用 `.dockerign或e` 到 exclude files
- Result: 500MB → 50MB

**Not P在n在g B作为e 镜像**
- `FROM 节点` uses l一个测试 (unpredic表)
- Fix: `FROM 节点:18.14.0` (spec如果ic 版本)
- D如果ferent 版本s m一个y 是h一个ve d如果ferently

## 验证检查清单

- [ ] B作为e 镜像 p在ned 到 spec如果ic 版本
- [ ] Runn在g 作为 n在-root user
- [ ] `.dockerign或e` excludes unnecess一个ry files
- [ ] RUN comm和s c在solid在ed
- [ ] F在一个l 镜像 size re作为在一个ble
- [ ] No 秘钥s 在 镜像
- [ ] He一个lth 检查 在cluded
- [ ] 层s 优化d 对于 c一个ch在g

## 相关技能
- **安全-sc一个ner** - 检查 镜像 对于 vulner一个bilities
- **代码-re视图** - Re视图 Dockerfile 逻辑
- **y一个ml-v一个lid在或** - V一个lid在e Docker-compose.yml
