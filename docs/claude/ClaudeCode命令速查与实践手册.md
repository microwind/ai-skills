# Claude Code 命令速查与实践手册

> 面向开发者的 Claude Code CLI操作手册 ，覆盖命令、参数、快捷键、工作流和工程实践。

---

## 一、基本模型

Claude Code 基本操作：

- 输入：Prompt + 文件（--file / stdin）
- 上下文：session（--resume / --continue）
- 执行：单次 / 交互 / 后台
- 输出：文本 / JSON / 流式 JSON / 文件

核心原则：

1. 输入越准确细致，输出越稳定。但也不是越多越好，而是恰到好处。
2. 上下文越清晰，结果越一致。上下文无杂质干扰，一件事一件事处理。
3. 任务越可验证，风险越低。任务能通过Claude自身验证最好。

---

## 二、交互式斜杠命令（Slash Commands）

在交互模式中输入 `/` 开头的命令来控制会话行为。

### 会话控制

| 命令 | 功能 | 说明 |
|------|------|------|
| `/help` | 显示所有可用命令 | 包含内置命令、自定义命令和 MCP 命令 |
| `/clear` | 清除当前对话上下文 | 完全重置，适合切换任务 |
| `/compact [指令]` | 压缩对话历史 | 可指定保留重点，如 `/compact 保留错误处理模式` |
| `/undo` | 撤销最近一次文件更改 | 仅回退上一步，多步回退用 git |
| `/exit` | 退出会话 | 等同 Ctrl+D |

### 模式切换

| 命令 | 功能 | 说明 |
|------|------|------|
| `/plan` | 切换计划模式 | Claude 先给出方案等待确认后再执行 |
| `/fast` | 切换快速模式 | 同一模型的速度优化设置，约 2x 费用 |
| `/model [名称]` | 切换模型 | `/model opus` `/model sonnet` `/model haiku` |
| `/effort [级别]` | 设置推理深度 | `low` / `medium` / `high` / `max` |

### 模型选择策略

| 场景 | 推荐模型 |
|------|---------|
| 简单探索、机械任务 | `/model haiku` |
| 日常编码 | `/model sonnet` |
| 复杂推理、架构设计、安全分析 | `/model opus` |

### 会话管理

| 命令 | 功能 | 说明 |
|------|------|------|
| `/resume` | 恢复历史会话 | 打开会话选择器 |
| `/sessions` | 列出所有会话 | 查看会话历史 |
| `/tasks` | 查看后台任务 | `/tasks <id>` 查看详情 |
| `/name [名称]` | 命名当前会话 | 方便后续查找 |

### 工具与配置

| 命令 | 功能 | 说明 |
|------|------|------|
| `/config` | 查看/编辑配置 | 打开 settings.json |
| `/permissions` | 管理权限设置 | 查看和修改工具权限 |
| `/mcp` | 管理 MCP 服务器 | 添加、删除、查看 MCP 服务器 |
| `/cost` | 查看费用统计 | 当前会话 token 和费用 |
| `/keybindings` | 编辑快捷键配置 | 修改 `~/.claude/keybindings.json` |

### 项目与环境

| 命令 | 功能 | 说明 |
|------|------|------|
| `/init` | 初始化项目配置 | 创建 CLAUDE.md 等项目文件 |
| `/add-dir <路径>` | 添加工作目录 | 允许访问额外目录 |
| `/ide` | 连接 IDE | 自动连接 VS Code / JetBrains |
| `/doctor` | 健康检查 | 诊断 Claude Code 安装和配置问题 |
| `/status` | 查看状态 | 显示当前连接和配置状态 |

### 账户与安装

| 命令 | 功能 | 说明 |
|------|------|------|
| `/login` | 登录 | 认证 Anthropic 账户 |
| `/logout` | 登出 | 清除认证信息 |
| `/install-github-app` | 安装 GitHub App | 启用 PR 工作流集成 |
| `/bug` | 报告问题 | 提交 bug 报告 |

### 高级功能

| 命令 | 功能 | 说明 |
|------|------|------|
| `/listen` | 监听模式 | 监听外部输入 |
| `/vim` | Vim 模式 | 启用 Vim 风格的键绑定 |
| `/review` | 代码审查 | 审查当前变更 |
| `/memory` | 管理记忆 | 查看/编辑 Claude 的持久记忆 |
| `/terminal-setup` | 终端设置 | 配置终端集成 |
| `!<命令>` | 执行 Shell 命令 | 如 `!git status`，在当前会话中运行 |

### 自定义斜杠命令

在项目目录 `.claude/commands/` 或全局 `~/.claude/commands/` 下创建 `.md` 文件：

```markdown
---
allowed-tools: Edit, Bash
model: sonnet
description: 审查当前分支的代码变更
---

审查当前分支相对于 main 的所有变更：
1. 检查代码质量
2. 发现潜在 bug
3. 给出改进建议

$ARGUMENTS
```

文件名即命令名，使用 `$ARGUMENTS` 捕获命令后的参数。

---

## 三、键盘快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| **Shift+Tab** | 切换权限/计划模式 | 循环：default → acceptEdits → auto → plan |
| **Ctrl+C** | 取消当前任务 | 停止执行但不退出会话 |
| **Ctrl+D** | 退出会话 | 等同 `/exit` |
| **Ctrl+L** | 清屏 | 清除终端显示，保留上下文 |
| **Ctrl+R** | 搜索历史 | 搜索当前会话的命令历史 |
| **Ctrl+S** | 暂存 Prompt | 暂存当前输入，提交其他内容后自动恢复 |
| **Escape** | 中断生成 | 第一次中断，输入 "go" 可继续 |
| **Escape×2** | 回溯模式 | 进入回溯模式，用方向键浏览历史 |

### 自定义快捷键

运行 `/keybindings` 编辑 `~/.claude/keybindings.json`，修改后即时生效无需重启。

---

## 四、CLI 启动参数

### 核心参数

| 参数 | 缩写 | 功能 | 示例 |
|------|------|------|------|
| `--print` | `-p` | 单次输出模式 | `claude -p "问题"` |
| `--continue` | `-c` | 继续最近会话 | `claude -c` |
| `--resume [id]` | `-r` | 恢复指定会话 | `claude -r abc123` |
| `--model <模型>` | | 指定模型 | `claude --model opus` |
| `--help` | `-h` | 显示帮助 | `claude -h` |
| `--version` | `-v` | 显示版本 | `claude -v` |

### 输入与输出

| 参数 | 功能 | 示例 |
|------|------|------|
| `--file <路径>` | 输入文件 | `claude --file src/api.ts "分析"` |
| `--output-format <格式>` | 输出格式 | `text` / `json` / `stream-json` |
| `--input-format <格式>` | 输入格式 | `text` / `stream-json` |
| `--json-schema <schema>` | 结构化输出验证 | 指定 JSON Schema |

### 会话与上下文

| 参数 | 功能 | 示例 |
|------|------|------|
| `--add-dir <目录>` | 添加工作目录 | `claude --add-dir ../lib` |
| `--name <名称>` | `-n` 命名会话 | `claude -n "feature-auth"` |
| `--fork-session` | 分叉会话 | 恢复时创建新会话 ID |
| `--from-pr [值]` | 从 PR 恢复 | `claude --from-pr 123` |
| `--session-id <uuid>` | 指定会话 ID | 使用特定 UUID |
| `--no-session-persistence` | 禁用会话持久化 | 仅与 `--print` 搭配 |
| `--worktree [名称]` | `-w` 创建 git worktree | 隔离工作环境 |
| `--tmux` | 创建 tmux 会话 | 需搭配 `--worktree` |

### 模型与行为

| 参数 | 功能 | 示例 |
|------|------|------|
| `--effort <级别>` | 推理深度 | `low` / `medium` / `high` / `max` |
| `--permission-mode <模式>` | 权限模式 | 见权限模式说明 |
| `--fallback-model <模型>` | 降级模型 | 主模型过载时自动切换 |
| `--max-budget-usd <金额>` | 费用上限 | 仅与 `--print` 搭配 |
| `--verbose` | 详细日志 | 显示更多运行信息 |
| `--debug [过滤]` | 调试模式 | `--debug "api,hooks"` |
| `--debug-file <路径>` | 调试日志文件 | 写入指定路径 |

### 工具与权限

| 参数 | 功能 | 示例 |
|------|------|------|
| `--allowedTools <工具>` | 允许的工具 | `"Bash(git:*) Edit"` |
| `--disallowedTools <工具>` | 禁止的工具 | `"Bash(rm:*)"` |
| `--tools <工具>` | 指定可用工具集 | `"Bash,Edit,Read"` 或 `""` 禁用所有 |
| `--dangerously-skip-permissions` | 跳过所有权限检查 | 仅用于沙箱环境 |
| `--allow-dangerously-skip-permissions` | 允许跳过权限选项 | 不默认跳过，仅开放选项 |

### Prompt 定制

| 参数 | 功能 | 示例 |
|------|------|------|
| `--system-prompt <提示>` | 自定义系统提示 | 替换默认系统提示 |
| `--append-system-prompt <提示>` | 追加系统提示 | 在默认提示后附加 |

### 集成与扩展

| 参数 | 功能 | 示例 |
|------|------|------|
| `--agent <代理>` | 指定代理 | 覆盖 settings 中的 agent |
| `--agents <json>` | 自定义代理 | JSON 定义多个代理 |
| `--mcp-config <配置>` | MCP 服务器配置 | 加载 MCP JSON 配置 |
| `--strict-mcp-config` | 严格 MCP 模式 | 仅使用指定的 MCP |
| `--plugin-dir <路径>` | 加载插件目录 | 指定插件路径 |
| `--settings <文件>` | 加载设置文件 | 额外的 settings.json |
| `--ide` | 连接 IDE | 自动连接可用的 IDE |
| `--chrome` | Chrome 集成 | 启用浏览器集成 |
| `--bare` | 最小模式 | 跳过 hooks、LSP、插件等 |
| `--disable-slash-commands` | 禁用斜杠命令 | 禁用所有 skills |

### 子命令

| 子命令 | 功能 |
|--------|------|
| `claude doctor` | 健康检查，诊断安装问题 |
| `claude auth` | 管理认证 |
| `claude mcp` | 管理 MCP 服务器 |
| `claude install [target]` | 安装指定版本（stable / latest / 版本号） |
| `claude update` | 检查并安装更新 |
| `claude agents` | 列出已配置的代理 |
| `claude auto-mode` | 查看 auto 模式分类器配置 |
| `claude setup-token` | 设置长期认证 token |
| `claude plugin` | 管理插件 |

---

## 五、权限模式

使用 `--permission-mode` 或 Shift+Tab 在会话中切换：

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| `default` | 每次操作需确认 | 谨慎操作，初次使用 |
| `acceptEdits` | 自动接受文件编辑 | 信任代码修改 |
| `plan` | 先计划再执行，修改需确认 | 复杂任务先审查方案 |
| `auto` | 自动执行所有操作 | 快速迭代，信任环境 |
| `dontAsk` | 不询问直接执行 | 自动化流水线 |
| `bypassPermissions` | 跳过所有权限检查 | 沙箱/测试环境 |

---

## 六、运行模式

### 1. 交互模式（默认）

```bash
claude
```

特点：持续上下文、适合探索和迭代。

### 2. 单次模式（Print）

```bash
claude -p "一个问题"
```

特点：无状态、适合自动化和管道。

### 3. 后台任务

```bash
claude --background "运行测试"

# 查看任务
/tasks

# 查看详情
/tasks <task-id>
```

适用：测试、构建、长时间分析。

---

## 七、输入与输出

### 输入方式

```bash
# 文件输入
claude < prompt.txt

# 管道输入
cat diff.txt | claude -p "分析改动"

# 组合输入
git diff | claude -p "代码审查"

# 多文件分析
claude --file api.ts --file db.ts "分析依赖关系"

# 精确行范围
claude --file src/api.ts:40-80 "是否存在逻辑错误"
```

### 输出方式

```bash
# JSON 输出
claude -p --output-format json "生成接口定义"

# 流式 JSON
claude -p --output-format stream-json "生成代码"

# 结构化输出
claude -p --json-schema '{"type":"object","properties":{"name":{"type":"string"}}}' "提取信息"

# 重定向
claude -p "生成代码" > main.ts
```

---

## 八、工作流模板

### 1. 多步骤执行

```bash
claude "
1. 设计数据库
2. 实现 API
3. 编写测试
4. 生成文档
"
```

### 2. 验证型工作流

```bash
claude "
步骤1：实现功能
验证：是否可运行

步骤2：编写测试
验证：是否通过

步骤3：覆盖率检查
验证：是否 >80%
"
```

### 3. Bug 修复流程

```text
1. 描述问题
2. 分析日志
3. 定位代码
4. 修复问题
5. 编写测试
6. 回归验证
```

### 4. 重构流程

```text
1. 识别问题
2. 提出重构方案
3. 重写代码
4. 保持行为一致
5. 验证测试
```

---

## 九、命令组合实践

### 1. 代码审查

```bash
# 交互式审查
claude --file main.go "
1. 性能问题
2. 并发问题
3. 安全问题
4. 可维护性
"

# Git diff 审查
git diff main..HEAD | claude -p "审查代码变更，标注风险点"
```

### 2. Bug 定位

```bash
# 日志分析
claude --file logs.txt "找出错误原因"

# 代码定位
claude --file api.ts:40-80 "这里是否有问题"
```

### 3. Git 集成

```bash
git diff | claude -p "审查代码"
git log --oneline -20 | claude -p "分析变更趋势"
```

### 4. CI/CD 集成

```bash
# 自动审查（费用受控）
git diff main..HEAD | claude -p \
  --max-budget-usd 0.50 \
  --output-format json \
  "代码审查，输出 JSON 格式的问题列表"

# 降级策略
claude -p --model sonnet --fallback-model haiku "生成接口"
```

### 5. 批处理

```bash
for file in src/*.ts; do
  claude -p --file "$file" "检查问题"
done
```

---

## 十、Compact 与上下文管理

长会话中上下文会逐渐膨胀，影响性能和费用。

### 使用策略

| 场景 | 操作 |
|------|------|
| 上下文使用 >80% | `/compact` 压缩历史 |
| 切换完全不同的任务 | `/clear` 清空重来 |
| 需要保留特定信息 | `/compact 保留 API 设计决策` |
| 会话过长效果下降 | `/compact` 后继续 |

### 示例

```
/compact 保留错误处理的修复方案和测试结果
```

Claude 会压缩之前的对话，仅保留你指定的关键信息。

---

## 十一、Plan 模式实践

Plan 模式让 Claude 在执行前先给出方案。

### 启用方式

```bash
# 启动时指定
claude --permission-mode plan

# 会话中切换
/plan

# 快捷键
Shift+Tab  # 循环切换模式
```

### 适用场景

- 复杂重构：先看方案再执行
- 不熟悉的代码库：先探索再修改
- 高风险操作：数据库迁移、API 变更
- 团队协作：方案可以分享讨论

---

## 十二、环境变量

| 变量 | 功能 |
|------|------|
| `ANTHROPIC_API_KEY` | API 密钥 |
| `CLAUDE_CODE_SIMPLE` | 简单模式（`--bare` 自动设置） |
| `CLAUDE_FORMAT` | 默认输出格式 |

---

## 十三、参数总览

| 参数 | 缩写 | 功能 |
|------|------|------|
| `--print` | `-p` | 单次输出 |
| `--continue` | `-c` | 继续最近会话 |
| `--resume` | `-r` | 恢复指定会话 |
| `--model` | | 指定模型 |
| `--file` | | 输入文件 |
| `--effort` | | 推理深度 |
| `--output-format` | | 输出格式 |
| `--permission-mode` | | 权限模式 |
| `--allowedTools` | | 允许的工具 |
| `--max-budget-usd` | | 费用上限 |
| `--worktree` | `-w` | 创建 worktree |
| `--verbose` | | 详细日志 |
| `--debug` | `-d` | 调试模式 |
| `--help` | `-h` | 帮助 |
| `--version` | `-v` | 版本 |

---

## 十四、场景速查

| 场景 | 命令 |
|------|------|
| 快速问答 | `claude "问题"` |
| 单次输出（管道） | `claude -p "问题"` |
| 分析代码 | `claude --file src/api.ts "分析"` |
| 精确分析 | `claude --file src/api.ts:40-80 "检查"` |
| 继续上次 | `claude -c` |
| 恢复会话 | `claude -r` |
| 切换模型 | `/model opus` |
| 压缩上下文 | `/compact` |
| 计划模式 | `/plan` 或 Shift+Tab |
| 快速模式 | `/fast` |
| 低推理 | `/effort low` |
| 后台任务 | `claude --background "任务"` |
| 费用控制 | `--max-budget-usd 1.00` |
| 自动化 | `-p --output-format json` |
| 沙箱执行 | `--dangerously-skip-permissions` |
| 健康检查 | `claude doctor` |
| 命名会话 | `claude -n "my-feature"` |
| 隔离开发 | `claude -w feature-x` |

---

## 十五、Prompt 编写规范

### 推荐结构

```text
目标：
约束：
输入：
输出：
验证：
```

示例：

```text
目标：实现缓存
约束：Go + 并发安全
输出：完整代码
验证：包含测试
```

---

## 十六、最佳实践

1. **Prompt 结构化** — 明确目标、约束、验证条件
2. **文件输入精确化** — 用行号范围而非整个文件
3. **善用会话管理** — `--continue` 和 `--resume` 保持上下文
4. **及时压缩上下文** — `/compact` 防止上下文膨胀
5. **按需选择模型** — Haiku 做简单任务，Opus 做复杂推理
6. **Plan 模式审查** — 复杂变更先看方案再执行
7. **费用控制** — `--max-budget-usd` 限制自动化场景的费用
8. **输出 JSON 用于自动化** — `--output-format json` 便于脚本处理
9. **强制验证步骤** — Prompt 中包含验证条件

---

## 十七、常见问题

### 1. 输出质量不稳定

原因：Prompt 模糊 / 输入过多

解决：限制范围、增加约束、使用 `/effort high`

### 2. 上下文丢失

原因：未使用 session

解决：使用 `--continue` 或 `--resume`

### 3. 分析结果不准确

原因：文件范围过大

解决：使用行号精确定位 `--file src/api.ts:40-80`

### 4. 上下文过长导致效果下降

原因：长会话积累过多历史

解决：使用 `/compact` 压缩，或 `/clear` 重新开始

### 5. 费用超出预期

原因：Opus 模型 + 长会话

解决：简单任务用 `/model haiku`，CI 中用 `--max-budget-usd`

---

## 总结

Claude Code 的核心能力：

- 准确的输入，尽量做细致清晰
- 上下文管理（`/compact` / `--resume` / `--continue`）
- 模式切换（`/plan` / `/fast` / `/model` / `/effort`）
- 可验证工作流
- 自动化集成（`-p` / `--output-format json`）

使用方式是从"提问"到"构建整体执行流程"。

## 参考来源
AI 编程核心知识库：https://microwind.github.io