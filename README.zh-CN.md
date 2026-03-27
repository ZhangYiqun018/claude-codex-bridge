# Claude-Codex Bridge

[English](./README.md)

![Claude Code](https://img.shields.io/badge/Claude_Code-Bridge-111827?style=flat-square)
![Codex CLI](https://img.shields.io/badge/Codex_CLI-0.116.0-2563eb?style=flat-square)
![默认模型](https://img.shields.io/badge/Default-gpt--5.4-0f766e?style=flat-square)
![桥接形态](https://img.shields.io/badge/Modes-MCP%20%7C%20Subagent%20%7C%20Skill%20%7C%20Hook-7c3aed?style=flat-square)
![插件](https://img.shields.io/badge/Plugins-Claude%20%7C%20Codex-1d4ed8?style=flat-square)

通过 MCP、子代理、审查技能和自动化钩子，把 Claude Code 与 Codex 接到同一个工作流里。

- 适合已经在用 Claude Code、但不想为了接入 Codex 而频繁切换上下文或重复搭审查流程的人。
- 返回结构化交接结果、基于 git 的问题发现，或自动化的低风险日常决策。
- 现在同时提供两种插件形态：Claude Code 原生插件负责直接接入运行时，Codex 插件负责把 bridge 安装进 Claude 项目。

快速跳转：[最新进展](#whats-new) | [20 秒体验](#demo-20s) | [插件安装](#plugin-install) | [快速开始](#quick-start) | [如何选择桥接方式](#choose-a-bridge) | [最佳实践提示词](#best-practice-prompts) | [参考信息](#reference)

<a id="whats-new"></a>
## ✨ 最新进展

- 现在已经支持通过 Claude Code 原生插件安装这个仓库；在支持插件的环境里，不需要再手工复制 bridge 文件。
- Codex 侧也继续保留插件封装，但角色更清晰了：它负责安装和分发，而不是承载 Claude 运行时本身。
- 当前打包进去的 MCP 默认模型仍然固定为 `gpt-5.4`。

推荐优先使用插件安装：

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

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

<a id="plugin-install"></a>
## 🧩 插件安装

### 🤖 Claude Code 插件

现在推荐优先走这条路径。

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
- 以插件 hooks 方式提供的 AskUserQuestion 自动化钩子

安装后，Claude 可能会在 `/agents` 和 `/skills` 里按 `claude-codex-bridge` 插件命名空间展示这些能力；如果名字看起来多了一层前缀，这是正常的。

hook 仍然按项目显式启用：

```bash
touch /path/to/project/.enable-copilot
```

### 🧰 Codex 插件

Codex 插件依然有价值，但角色不一样，它更适合做安装器和分发器。

它擅长的事：
- 把 bridge 安装到当前项目，或者安装到全局 Claude Code 配置里。
- 把安装流程打包成一个可复用的 Codex skill，不用你再手动复制文件。

它不会替代的部分：
- Claude 运行时真正消费的仍然是 `.mcp.json`、`.claude/...` 和 hook 配置，所以 Codex 插件本质上还是在帮你把这些文件写到目标位置。

这个仓库现在已经包含：
- Codex marketplace：`.agents/plugins/marketplace.json`
- 插件目录：`plugins/claude-codex-bridge`
- 安装 skill：`install-claude-codex-bridge`

如果你在这个仓库里打开 Codex，可以先在 `/plugins` 里安装这个插件，然后直接说：

```text
使用 install-claude-codex-bridge skill，把完整 bridge 安装到当前项目。
```

如果你还想同时启用 hook：

```text
使用 install-claude-codex-bridge skill，把完整 bridge 安装到当前项目，并启用 hook。
```

<a id="quick-start"></a>
## 🚀 快速开始

### 🥇 优先使用 Claude 插件

如果你当前环境的 Claude Code 已经支持插件，优先用插件路径。

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

本地目录源不支持 `--sparse`；只有把 GitHub 仓库或其他 git 源作为 marketplace 时，才需要加 `--sparse .claude-plugin plugins`。

这样拿到的是原生 Claude 插件，而不是一组手工复制进去的 bridge 文件。

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

./hooks/install-hook.sh --global
```

</details>

安装完成后重启 Claude Code。

<a id="choose-a-bridge"></a>
## 🧭 如何选择桥接方式

| 如果你想... | 使用方式 | 为什么适合 | 配置位置 |
|-------------|----------|------------|----------|
| 发起一次明确的问题 | `MCP bridge` | 最快、最轻量 | `.mcp.json` |
| 委托一段紧凑工作流 | `Subagent bridge` | Claude 能收回结构化结果 | 继承 `.mcp.json` |
| 审查 git 已定义好的改动 | `Review skill` | 当 git 已经划清范围时最省事 | `~/.codex/config.toml` |
| 自动处理重复性决策提示 | `Hook bridge` | 自动处理低风险的日常决策 | 钩子默认值 -> 环境变量 -> 标记文件 |

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
- `./hooks/install-hook.sh --project /path/to/project` 会把钩子配置写入 `/path/to/project/.claude/settings.local.json`。
- `./hooks/install-hook.sh --global` 会把钩子配置写入 `~/.claude/settings.local.json`。
- Claude 插件入口是 `claude plugin marketplace add`；这个仓库已经提供 repo-local marketplace：`.claude-plugin/marketplace.json`。
- Codex 插件入口是 Codex CLI 里的 `/plugins`；这个仓库也提供 Codex marketplace：`.agents/plugins/marketplace.json`。

<details>
<summary>按需安装</summary>

- 只安装 MCP：把 `.mcp.json` 放进项目，或全局执行 `claude mcp add ...`。
- 只安装子代理：把 `.claude/agents/codex-integration.md` 复制到 `.claude/agents/` 或 `~/.claude/agents/`。
- 只安装审查技能：把 `.claude/skills/codex-review/SKILL.md` 复制到 `.claude/skills/codex-review/` 或 `~/.claude/skills/codex-review/`。
- 只安装钩子：运行 `./hooks/install-hook.sh --project /path/to/project` 或 `./hooks/install-hook.sh --global`。

</details>

<details>
<summary>插件打包结构</summary>

- Claude marketplace：`.claude-plugin/marketplace.json`
- Claude 插件清单：`plugins/claude-codex-bridge/.claude-plugin/plugin.json`
- Claude 插件组件：`plugins/claude-codex-bridge/agents`、`plugins/claude-codex-bridge/skills`、`plugins/claude-codex-bridge/hooks`、`plugins/claude-codex-bridge/.mcp.json`
- Codex marketplace：`.agents/plugins/marketplace.json`
- Codex 插件清单：`plugins/claude-codex-bridge/.codex-plugin/plugin.json`
- Codex 安装 skill：`plugins/claude-codex-bridge/skills/install-claude-codex-bridge/SKILL.md`
- Codex 安装脚本：`plugins/claude-codex-bridge/scripts/install_bridge.py`

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
- `codex review` 使用了错误模型：检查 `~/.codex/config.toml`，因为 review 路径不走 `.mcp.json`。
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
