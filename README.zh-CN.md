# Claude-Codex Bridge

[English](./README.md)

![Claude Code](https://img.shields.io/badge/Claude_Code-Bridge-111827?style=flat-square)
![Codex CLI](https://img.shields.io/badge/Codex_CLI-0.117.0-2563eb?style=flat-square)
![默认模型](https://img.shields.io/badge/Default-gpt--5.4-0f766e?style=flat-square)
![桥接形态](https://img.shields.io/badge/Modes-MCP%20%7C%20Subagent%20%7C%20Skill%20%7C%20Hook-7c3aed?style=flat-square)
![插件](https://img.shields.io/badge/Plugins-Claude%20%7C%20Codex-1d4ed8?style=flat-square)

> 你正在用 Claude Code 写代码，突然想让 Codex 评估一下重构方案。
>
> **不用桥接**：切换终端、复制文件、丢失上下文、手动粘贴结果回来。
>
> **用了桥接**：一句话指令，Codex 的分析直接返回到你的 Claude 会话里。

这个仓库通过 **MCP**、**子代理**、**审查技能** 和 **钩子**，把两个 AI 编程助手接到同一个工作流——让你在不同场景用最好的工具，不用来回折腾。

**适合谁用：**
- 不想切换上下文就能调用 Codex 的 Claude 用户
- 不想手动复制粘贴就能调用 Claude 的 Codex 用户
- 希望决策可追溯、可审查、可自动化的团队

快速跳转：[最新进展](#whats-new) | [插件对照表](#plugin-matrix) | [20 秒体验](#demo-20s) | [插件安装](#plugin-install) | [快速开始](#quick-start) | [如何选择桥接方式](#choose-a-bridge) | [最佳实践提示词](#best-practice-prompts) | [参考信息](#reference)

<a id="whats-new"></a>
## ✨ 最新进展

- 现在已经支持通过 Claude Code 原生插件安装这个仓库；在支持插件的环境里，不需要再手工复制 bridge 文件。
- Codex 侧现在也有真正的运行时路径了：Codex 插件会直接提供 Claude 相关 skill，而不再只是一个 Claude 侧安装器。
- `Codex -> Claude` 的多轮对话现在有显式 session 持久化，保存在 `.claude-codex-bridge/sessions/*.json`，不再只依赖“当前仓库最近一次 Claude 会话”。
- 双向 debate 现在都已经有独立入口：Claude 侧是 `codex-debate`，Codex 侧是 `claude-debate`。
- 反向桥接现在分成两条 Codex 侧路径：直接用 `claude -p` 做咨询，以及通过 `codex mcp add` 注册 `claude mcp serve`。
- 当前打包进去的 MCP 默认模型仍然固定为 `gpt-5.4`。

Claude 侧安装：

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

Codex 侧安装：

```text
在 Codex 里打开 `/plugins`，把当前仓库作为 marketplace 加进去，然后安装 `claude-codex-bridge`。
```

<a id="plugin-matrix"></a>
## 🧭 插件对照表

这个仓库现在会打出两个不同的运行时插件。它们共用一个仓库，但职责不同。

| 如果你的主宿主是... | 安装哪个插件 | 方向 | 运行时能力 | 适合什么时候装 | 它不负责什么 |
|---|---|---|---|---|---|
| `Claude Code` | `Claude Code 插件` | `Claude -> Codex` | `codex-server` MCP、`codex-integration`、`codex-review`、`codex-debate`、可选 hook | 你的工作从 Claude 发起，希望把 Codex 接进来 | 不能让 Codex 反过来咨询 Claude；那是 Codex 插件的职责 |
| `Codex` | `Codex 插件` | `Codex -> Claude` | `claude-integration`、`claude-review`、`claude-debate`、`install-claude-code-mcp` | 你的工作从 Codex 发起，希望把 Claude 接进来 | 不提供反向 hook 自动化；它依赖本地 Claude CLI |

一句话总结：
- 如果 Claude 是主编排器，就装 Claude 插件。
- 如果 Codex 是主编排器，就装 Codex 插件。
- 只有你确实双向都在用时，才需要两个都装。

<a id="demo-20s"></a>
## ⚡ 20 秒体验

1. 先把这段提示词贴进 Claude Code：

```text
使用名为 `codex-integration` 的子代理排查我当前项目里的失败测试，并严格按以下结构返回：
1. 根因
2. 推荐修复方向
3. 风险或权衡点
4. 文件引用
```

预期结果形态：

> 根因：共享测试夹具在多次运行之间发生状态泄漏
> 推荐修复方向：把夹具初始化隔离到目标项目的测试框架层
> 风险或权衡点：会影响 3 组共用辅助函数的测试
> 文件引用：`<target-test-file>`、`<target-service-file>`

2. 如果你想减少初始化或迁移时的重复性提示，再启用钩子：

```bash
touch /path/to/project/.enable-copilot
```

结果：初始化或迁移时反复出现的 `AskUserQuestion` 会被自动处理。

3. 在 Codex 里安装好 `/plugins` 里的插件后，再说：

```text
使用 claude-integration skill 审查认证子系统，并严格按以下结构返回：
1. 关键发现
2. 权衡点
3. 推荐下一步
4. 文件引用
```

结果：Codex 可以直接咨询 Claude Code，而不再只是帮助 Claude 去连接 Codex。

<a id="plugin-install"></a>
## 🧩 插件安装

### 🤖 Claude Code 插件

当 Claude Code 是任务起点时，安装这个插件。

为什么适合：
- Claude 插件可以直接打包 `agents/`、`skills/`、`hooks/hooks.json` 和 `.mcp.json`。
- 这和本仓库的 bridge 结构几乎一一对应。
- 安装后是 Claude 原生接入，不再依赖手工复制一堆桥接文件。

最快的单次会话测试方式：

```bash
claude --plugin-dir "$PWD/plugins/claude-codex-bridge"
```

从当前仓库做项目级持久安装：

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

如果后续用 GitHub 仓库作为 marketplace 源，可以做用户级安装：

```bash
claude plugin marketplace add https://github.com/ZhangYiqun018/claude-codex-bridge --scope user --sparse .claude-plugin plugins
claude plugin install claude-codex-bridge --scope user
```

Claude 插件会直接提供：
- 固定为 `gpt-5.4` 的 `codex-server` MCP 服务
- `codex-integration` 子代理
- `codex-review` skill
- `codex-debate` skill
- 以插件 hooks 方式提供的 AskUserQuestion 自动化钩子

安装后，Claude 可能会在 `/agents` 和 `/skills` 里按 `claude-codex-bridge` 插件命名空间展示这些能力；如果名字看起来多了一层前缀，这是正常的。

hook 仍然按项目显式启用：

```bash
touch /path/to/project/.enable-copilot
```

### 🧰 Codex 插件

当 Codex 是任务起点时，安装这个插件。

它擅长的事：
- 让 Codex 通过 `claude -p` 直接向 Claude Code 要第二意见。
- 给 Codex 增加一条 Claude-backed review 路径，用来审未提交更改、base diff 或特定 commit。
- 给 Codex 增加一条结构化多轮 debate 路径，并显式保存 Claude session。
- 可选地把 `claude mcp serve` 注册成 Codex 里的 `claude-code` MCP 服务，让 Codex 也能调用 Claude Code 的工具面。

它不会替代的部分：
- Claude 插件仍然是 Claude -> Codex 的 MCP、子代理、review skill 和 hook 集成入口。
- Codex 的反向桥接仍然依赖本地安装并登录好的 Claude Code CLI。

这个仓库现在已经包含：
- Codex marketplace：`.agents/plugins/marketplace.json`
- 插件目录：`plugins/claude-codex-bridge`
- Claude 咨询 skill：`claude-integration`
- Claude debate skill：`claude-debate`
- Claude-backed review skill：`claude-review`
- Claude Code MCP 安装 skill：`install-claude-code-mcp`
- Codex 原生 git review skill：`codex-review`

如果你在这个仓库里打开 Codex，可以先在 `/plugins` 里安装这个插件，然后直接说：

```text
使用 claude-integration skill 审查认证子系统，并严格按以下结构返回：
1. 关键发现
2. 权衡点
3. 推荐下一步
4. 文件引用
```

如果你还想把 Claude Code 的 MCP 工具面也接进 Codex：

```text
使用 install-claude-code-mcp skill，把 Claude Code 作为 MCP server 加到 Codex。
```

如果你想在 Codex 里发起一段结构化多轮辩论：

```text
使用 claude-debate skill，围绕“要不要保留当前 migration layer”跟 Claude Code 做多轮辩论。
```

<a id="quick-start"></a>
## 🚀 快速开始

### 🤖 如果你从 Claude Code 开始

使用 Claude 插件。

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

本地目录源不支持 `--sparse`；只有把 GitHub 仓库或其他 git 源作为 marketplace 时，才需要加 `--sparse .claude-plugin plugins`。

这样拿到的是 `Claude -> Codex` 的原生运行时集成。

### 🧰 如果你从 Codex 开始

使用 Codex 插件。

在 `/plugins` 里安装后，可以直接说：

```text
使用 claude-integration skill 审查认证子系统。
使用 claude-review skill 审查我当前未提交的更改。
使用 claude-debate skill，让 Claude Code 跟我一起辩论这个设计方案。
```

这样拿到的是 `Codex -> Claude` 的原生运行时集成。

### 🔁 如果你想手工做 Codex 侧接线

只有你不想装 Codex 插件时，才用下面这组手工命令。

手工做 Codex 侧接线：

```bash
codex mcp add claude-code -- claude mcp serve
python3 plugins/claude-codex-bridge/scripts/ask_claude.py --cwd "$PWD" --prompt "审查认证子系统，并严格按以下结构返回：
1. 关键发现
2. 权衡点
3. 推荐下一步
4. 文件引用"
```

第一条命令把 Claude Code 的 MCP 工具面暴露给 Codex。第二条命令则是直接向 Claude Code 请求结构化意见。

### 📁 手工项目级安装

适合你明确希望把 bridge 作为普通文件放进某个仓库。

```bash
git clone https://github.com/ZhangYiqun018/claude-codex-bridge.git
cd claude-codex-bridge

cp .mcp.json /path/to/your/project/
cp -r .claude /path/to/your/project/
./hooks/install-hook.sh --project /path/to/your/project
```

<details>
<summary>全局安装</summary>

适合希望所有项目共用同一套桥接能力。

```bash
git clone https://github.com/ZhangYiqun018/claude-codex-bridge.git
cd claude-codex-bridge

claude mcp add --transport stdio codex-server -- codex mcp-server -c 'model="gpt-5.4"'

mkdir -p ~/.claude/agents
cp .claude/agents/codex-integration.md ~/.claude/agents/

mkdir -p ~/.claude/skills/codex-review
cp .claude/skills/codex-review/SKILL.md ~/.claude/skills/codex-review/

mkdir -p ~/.claude/skills/codex-debate
cp .claude/skills/codex-debate/SKILL.md ~/.claude/skills/codex-debate/

./hooks/install-hook.sh --global
```

</details>

安装完成后重启 Claude Code。

<a id="choose-a-bridge"></a>
## 🧭 如何选择桥接方式

| 如果你想... | 使用方式 | 为什么适合 | 配置位置 |
|-------------|----------|------------|----------|
| 从 Claude 向 Codex 发起一次明确的问题 | `MCP bridge` | 最快的 Claude -> Codex 路径 | `.mcp.json` |
| 从 Claude 委托一段紧凑工作流给 Codex | `Subagent bridge` | Claude 能收回结构化结果 | 继承 `.mcp.json` |
| 从 Claude 用 Codex 默认能力审 git 改动 | `Review skill` | git 已经定义好范围时最省事 | `~/.codex/config.toml` |
| 从 Claude 发起和 Codex 的结构化多轮辩论 | `codex-debate` | 显式 rebuttal 工作流，使用 `codex` + `codex-reply` | Claude 插件或手工 skill 安装 |
| 从 Claude 用 Codex 自动处理重复性决策提示 | `Hook bridge` | 自动处理低风险日常决策 | 钩子默认值 -> 环境变量 -> 标记文件 |
| 从 Codex 向 Claude 要第二意见 | `claude-integration` | 直接做 Claude 咨询，范围不受 git 限制 | `plugins/.../scripts/ask_claude.py` |
| 从 Codex 发起和 Claude 的结构化多轮辩论 | `claude-debate` | 用显式 Claude session 做逐轮辩论 | `.claude-codex-bridge/sessions/*.json` |
| 从 Codex 通过 Claude 审查改动 | `claude-review` | 保持 Codex 编排，同时增加 Claude 审查 | `plugins/.../scripts/ask_claude.py` |
| 从 Codex 暴露 Claude Code 的 MCP 工具 | `install-claude-code-mcp` | 给 Codex 增加 `claude-code` MCP 条目 | `codex mcp` 全局配置 |

<a id="best-practice-prompts"></a>
## 🗣️ 最佳实践提示词

在提示词里直接点名桥接方式，Claude 的执行路径会稳定很多。

### 🔌 MCP Bridge

适合一次外部意见、一次方案比较、一次聚焦的技术判断。

```text
使用 codex MCP 工具分析这个迁移方案的优缺点，并严格按以下结构返回：
1. 主要优势
2. 主要代价
3. 建议
```

### 🧠 Subagent Bridge

适合任意文件审查、架构分析、多步骤综合，以及希望结果以交接格式返回的任务。

```text
使用名为 `codex-integration` 的子代理审查认证子系统，并严格按以下结构返回：
1. 关键发现
2. 两个重构方案的权衡点
3. 推荐下一步
4. 文件引用
```

### 🔍 Review Skill

适合 git 已经定义好审查范围的场景。

```text
使用 `codex-review` 技能审查我当前未提交的更改，并严格按以下结构返回：
1. 严重问题
2. 缺失测试
3. 风险假设
4. 文件引用
```

<details>
<summary>对应终端命令</summary>

```bash
codex review --uncommitted
codex review --base main
codex review --commit HEAD~1
```

</details>

### 📏 提示词规则

- 明确范围：例如 `未提交更改`、`base main`、某个 commit SHA、某个子系统或某组文件。
- 明确输出结构：例如问题发现、权衡点、建议、下一步、文件引用。
- 权限从小开始：优先 `read-only`，确实需要执行命令再升级。
- git diff 审查优先用 `codex-review`，任意文件审查或自定义审查优先用 `codex-integration`。

<a id="reference"></a>
## 📚 参考信息

### ✅ 运行要求

- 需要使用支持 MCP stdio 和钩子的 Claude Code，并安装 `codex-cli 0.116.0`。
- Codex -> Claude 咨询需要本地 Claude Code CLI 支持 `-p/--print`。
- Codex -> Claude 的多轮续聊依赖 `.claude-codex-bridge/sessions/` 下的显式 session 文件。
- Codex -> Claude MCP 接线需要同时具备 `codex mcp add` 和 `claude mcp serve`。
- `./hooks/install-hook.sh --project /path/to/project` 会把钩子配置写入 `/path/to/project/.claude/settings.local.json`。
- `./hooks/install-hook.sh --global` 会把钩子配置写入 `~/.claude/settings.local.json`。
- Claude 插件入口是 `claude plugin marketplace add`；这个仓库已经提供 repo-local marketplace：`.claude-plugin/marketplace.json`。
- Codex 插件入口是 Codex CLI 里的 `/plugins`；这个仓库也提供 Codex marketplace：`.agents/plugins/marketplace.json`。

<details>
<summary>按需安装</summary>

- 只安装 MCP：把 `.mcp.json` 放进项目，或全局执行 `claude mcp add ...`。
- 只安装子代理：把 `.claude/agents/codex-integration.md` 复制到 `.claude/agents/` 或 `~/.claude/agents/`。
- 只安装审查技能：把 `.claude/skills/codex-review/SKILL.md` 复制到 `.claude/skills/codex-review/` 或 `~/.claude/skills/codex-review/`。
- 只安装 debate 技能：把 `.claude/skills/codex-debate/SKILL.md` 复制到 `.claude/skills/codex-debate/` 或 `~/.claude/skills/codex-debate/`。
- 只安装钩子：运行 `./hooks/install-hook.sh --project /path/to/project` 或 `./hooks/install-hook.sh --global`。

</details>

<details>
<summary>插件打包结构</summary>

- Claude marketplace：`.claude-plugin/marketplace.json`
- Claude 插件清单：`plugins/claude-codex-bridge/.claude-plugin/plugin.json`
- Claude 插件组件：`plugins/claude-codex-bridge/agents`、`plugins/claude-codex-bridge/skills`、`plugins/claude-codex-bridge/hooks`、`plugins/claude-codex-bridge/.mcp.json`
- Codex marketplace：`.agents/plugins/marketplace.json`
- Codex 插件清单：`plugins/claude-codex-bridge/.codex-plugin/plugin.json`
- Claude 侧 Codex debate skill：`.claude/skills/codex-debate/SKILL.md`
- 打包后的 Claude 侧 Codex debate skill：`plugins/claude-codex-bridge/skills/codex-debate/SKILL.md`
- Codex Claude 咨询 skill：`plugins/claude-codex-bridge/skills/claude-integration/SKILL.md`
- Codex Claude debate skill：`plugins/claude-codex-bridge/skills/claude-debate/SKILL.md`
- Codex Claude 审查 skill：`plugins/claude-codex-bridge/skills/claude-review/SKILL.md`
- Codex Claude MCP 安装 skill：`plugins/claude-codex-bridge/skills/install-claude-code-mcp/SKILL.md`
- Codex 辅助脚本：`plugins/claude-codex-bridge/scripts/ask_claude.py`、`plugins/claude-codex-bridge/scripts/install_claude_code_mcp.py`
- 旧的 Claude 侧文件安装脚本：`plugins/claude-codex-bridge/scripts/install_bridge.py`

</details>

<details>
<summary>能力矩阵</summary>

| 能力 | Claude -> Codex | Codex -> Claude | 说明 |
|---|---|---|---|
| 任意文件第二意见 | 完整支持 | 完整支持 | Claude 侧走 MCP/subagent；Codex 侧走 `ask_claude.py` |
| 基于 git 的代码审查 | 完整支持 | Prompt-driven | Codex 侧目前是通过结构化提示词驱动 Claude 审查，不是 Claude 原生 review 子命令 |
| Subagent 风格 sidecar | 完整支持 | 部分支持 | Codex 可以把 Claude 当 sidecar 工作流用，但还不是原生 Codex subagent 类型 |
| 多轮辩论 | 完整支持 | 完整支持 | Claude 侧走 `codex` + `codex-reply`；Codex 侧走显式 Claude session 文件 |
| 重复性决策 hook | 完整支持 | 不支持 | 反向方向不尝试自动化 Claude 的权限提示 |

按插件看：

| 插件 | 宿主运行时 | 方向 | 运行时入口 | 最适合 |
|---|---|---|---|---|
| Claude Code 插件 | Claude Code | Claude -> Codex | `codex-server`、`codex-integration`、`codex-review`、`codex-debate`、hook | Claude-centric 工作流 |
| Codex 插件 | Codex | Codex -> Claude | `claude-integration`、`claude-review`、`claude-debate`、`install-claude-code-mcp` | Codex-centric 工作流 |

</details>

<details>
<summary>Hook 覆盖项</summary>

标记文件格式：

```text
(第 1 行保留，留空)
gpt-5.4
/path/to/mockup.png,/path/to/screenshot.jpg
```

可选环境变量：

```bash
export COPILOT_MODEL=gpt-5.4
export COPILOT_TIMEOUT=300
export COPILOT_DEBUG=1
export COPILOT_IMAGES=/path/to/mockup.png,/path/to/screenshot.jpg
export COPILOT_SYSTEM_PROMPT=/path/to/prompt.md
```

重置某个项目的钩子会话：

```bash
rm /path/to/project/.copilot-session-id
```

</details>

<details>
<summary>故障排查</summary>

- Claude 看不到 `codex` MCP 工具：确认项目里有 `.mcp.json`，或已经完成全局 MCP 配置，然后重启 Claude Code。
- Codex 看不到 `claude-code` MCP 工具：运行 `codex mcp add claude-code -- claude mcp serve`，或使用 `install-claude-code-mcp` skill，然后重启 Codex。
- `codex review` 使用了错误模型：检查 `~/.codex/config.toml`，因为 review 路径不走 `.mcp.json`。
- `claude-integration` 或 `claude-review` 一启动就失败：确认 `claude` 已安装、已登录，并且支持 `-p`。
- `claude-debate` 接到了错误的旧会话：删除 `.claude-codex-bridge/sessions/` 里的对应 session 文件，或者重新执行时加 `--reset-session`。
- 钩子没有触发：确认钩子已经启用，且已安装进目标项目或全局的 `settings.local.json`。
- 钩子静默失败：设置 `COPILOT_DEBUG=1`，再查看 `/tmp/claude-copilot-hook.log`。
- Codex 认证报错：运行 `codex login`。

</details>

## 🛡️ 安全说明

- 不要把密钥或凭证发给 Codex，除非你明确希望它看到。
- 能用 `read-only` 就不要升级权限。
- 钩子是自动化能力，不是高风险场景下的安全默认选项。
- `.claude/settings.local.json` 应保持本地使用，这个仓库会忽略它。

## 📄 许可证

MIT，见 [LICENSE](./LICENSE)。
