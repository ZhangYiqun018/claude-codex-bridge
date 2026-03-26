# Claude-Codex Bridge

[English](./README.md)

![Claude Code](https://img.shields.io/badge/Claude_Code-Bridge-111827?style=flat-square)
![Codex CLI](https://img.shields.io/badge/Codex_CLI-0.116.0-2563eb?style=flat-square)
![默认模型](https://img.shields.io/badge/Default-gpt--5.4-0f766e?style=flat-square)
![桥接形态](https://img.shields.io/badge/Modes-MCP%20%7C%20Subagent%20%7C%20Skill%20%7C%20Hook-7c3aed?style=flat-square)

通过 MCP、子代理、审查技能和自动化钩子，把 Claude Code 与 Codex 接到同一个工作流里。

- 适合已经在用 Claude Code、但不想为了接入 Codex 而频繁切换上下文或重复搭审查流程的人。
- 返回结构化交接结果、基于 git 的问题发现，或自动化的低风险日常决策。

快速跳转：[20 秒体验](#demo-20s) | [快速开始](#快速开始) | [如何选择桥接方式](#如何选择桥接方式) | [最佳实践提示词](#最佳实践提示词) | [参考信息](#参考信息)

<a id="demo-20s"></a>
## 20 秒体验

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

## 快速开始

### 项目级安装

适合只想让某个仓库携带自己的桥接配置。

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

## 如何选择桥接方式

| 如果你想... | 使用方式 | 为什么适合 | 配置位置 |
|-------------|----------|------------|----------|
| 发起一次明确的问题 | `MCP bridge` | 最快、最轻量 | `.mcp.json` |
| 委托一段紧凑工作流 | `Subagent bridge` | Claude 能收回结构化结果 | 继承 `.mcp.json` |
| 审查 git 已定义好的改动 | `Review skill` | 当 git 已经划清范围时最省事 | `~/.codex/config.toml` |
| 自动处理重复性决策提示 | `Hook bridge` | 自动处理低风险的日常决策 | 钩子默认值 -> 环境变量 -> 标记文件 |

## 最佳实践提示词

在提示词里直接点名桥接方式，Claude 的执行路径会稳定很多。

### MCP Bridge

适合一次外部意见、一次方案比较、一次聚焦的技术判断。

```text
使用 codex MCP 工具分析这个迁移方案的优缺点，并严格按以下结构返回：
1. 主要优势
2. 主要代价
3. 建议
```

### Subagent Bridge

适合任意文件审查、架构分析、多步骤综合，以及希望结果以交接格式返回的任务。

```text
使用名为 `codex-integration` 的子代理审查认证子系统，并严格按以下结构返回：
1. 关键发现
2. 两个重构方案的权衡点
3. 推荐下一步
4. 文件引用
```

### Review Skill

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

### 提示词规则

- 明确范围：例如 `未提交更改`、`base main`、某个 commit SHA、某个子系统或某组文件。
- 明确输出结构：例如问题发现、权衡点、建议、下一步、文件引用。
- 权限从小开始：优先 `read-only`，确实需要执行命令再升级。
- git diff 审查优先用 `codex-review`，任意文件审查或自定义审查优先用 `codex-integration`。

## 参考信息

### 运行要求

- 需要使用支持 MCP stdio 和钩子的 Claude Code，并安装 `codex-cli 0.116.0`。
- `./hooks/install-hook.sh --project /path/to/project` 会把钩子配置写入 `/path/to/project/.claude/settings.local.json`。
- `./hooks/install-hook.sh --global` 会把钩子配置写入 `~/.claude/settings.local.json`。

<details>
<summary>按需安装</summary>

- 只安装 MCP：把 `.mcp.json` 放进项目，或全局执行 `claude mcp add ...`。
- 只安装子代理：把 `.claude/agents/codex-integration.md` 复制到 `.claude/agents/` 或 `~/.claude/agents/`。
- 只安装审查技能：把 `.claude/skills/codex-review/SKILL.md` 复制到 `.claude/skills/codex-review/` 或 `~/.claude/skills/codex-review/`。
- 只安装钩子：运行 `./hooks/install-hook.sh --project /path/to/project` 或 `./hooks/install-hook.sh --global`。

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

## 安全说明

- 不要把密钥或凭证发给 Codex，除非你明确希望它看到。
- 能用 `read-only` 就不要升级权限。
- 钩子是自动化能力，不是高风险场景下的安全默认选项。
- `.claude/settings.local.json` 应保持本地使用，这个仓库会忽略它。

## 许可证

MIT，见 [LICENSE](./LICENSE)。
