# Claude-Codex Bridge

[简体中文](./README.zh-CN.md)

![Claude Code](https://img.shields.io/badge/Claude_Code-Bridge-111827?style=flat-square)
![Codex CLI](https://img.shields.io/badge/Codex_CLI-0.116.0-2563eb?style=flat-square)
![Default Model](https://img.shields.io/badge/Default-gpt--5.4-0f766e?style=flat-square)
![Modes](https://img.shields.io/badge/Modes-MCP%20%7C%20Subagent%20%7C%20Skill%20%7C%20Hook-7c3aed?style=flat-square)
![Plugins](https://img.shields.io/badge/Plugins-Claude%20%7C%20Codex-1d4ed8?style=flat-square)

Bridge Claude Code and Codex through MCP, subagents, review skills, and routine-decision hooks.

- For people already working in Claude Code who want Codex without leaving the session, context switching, or repeated review setup.
- Gives back structured handoffs, git-scoped findings, or automated low-risk decisions.
- Ships in two plugin forms: a Claude Code native plugin for direct runtime integration, and a Codex plugin for guided installation into Claude projects.

Jump to: [What's New](#whats-new) | [20-Second Demo](#demo-20s) | [Plugin Install](#plugin-install) | [Quick Start](#quick-start) | [Choose a Bridge](#choose-a-bridge) | [Best-Practice Prompts](#best-practice-prompts) | [Reference](#reference)

<a id="whats-new"></a>
## ✨ What's New

- Claude Code now has a native plugin install path for this repo. In plugin-enabled environments, you no longer need to copy the bridge files by hand.
- Codex still gets its own plugin packaging, but its role is now clearer: it acts as the bridge installer and rollout path.
- The bridge defaults remain pinned to `gpt-5.4`, including the packaged MCP server config.

Plugin-first install:

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

<a id="demo-20s"></a>
## ⚡ 20-Second Demo

1. Paste this into Claude Code:

```text
Use the codex-integration subagent to review the failing tests in my project and return exactly:
1. Root cause
2. Recommended fix direction
3. Risks or tradeoffs
4. File references
```

Expected shape:

> Root cause: shared test fixture leaks state between runs
> Recommended fix direction: isolate fixture setup in the target project's test harness
> Risks or tradeoffs: touches helpers used by 3 suites
> File references: `<target-test-file>`, `<target-service-file>`

2. For repetitive setup or migration prompts, enable the hook:

```bash
touch /path/to/project/.enable-copilot
```

Result: repeated `AskUserQuestion` prompts during setup or migration are auto-answered.

<a id="plugin-install"></a>
## 🧩 Plugin Install

### 🤖 Claude Code Plugin

This is now the preferred install path for the repo.

Why it fits:
- Claude plugins can bundle `agents/`, `skills/`, `hooks/hooks.json`, and `.mcp.json` directly.
- That maps almost exactly to this repository's bridge design.
- After install, Claude gets the bridge natively instead of requiring manual file copies.

Fastest session-only test:

```bash
claude --plugin-dir "$PWD/plugins/claude-codex-bridge"
```

Persistent project install from this repo:

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

Persistent user install from GitHub once the repo is published as a marketplace source:

```bash
claude plugin marketplace add https://github.com/ZhangYiqun018/claude-codex-bridge --scope user --sparse .claude-plugin plugins
claude plugin install claude-codex-bridge --scope user
```

What the Claude plugin provides directly:
- `codex-server` MCP server pinned to `gpt-5.4`
- `codex-integration` subagent
- `codex-review` skill
- AskUserQuestion hook packaged as plugin hooks

Claude may display the agent and skill under the `claude-codex-bridge` plugin namespace in `/agents` and `/skills`. When in doubt, refer to the plugin namespace explicitly.

The hook remains opt-in per project:

```bash
touch /path/to/project/.enable-copilot
```

### 🧰 Codex Plugin

The Codex plugin still matters, but for a different job: installation and rollout.

What it does well:
- Installs the bridge into the current project or into global Claude Code config.
- Wraps setup as a reusable Codex skill instead of asking users to copy files by hand.

What it does not replace:
- Claude-side runtime still lives in `.mcp.json`, `.claude/...`, and hook config written into the target project or home directory.

This repo includes:
- Codex marketplace: `.agents/plugins/marketplace.json`
- Codex plugin root: `plugins/claude-codex-bridge`
- Installer skill: `install-claude-codex-bridge`

If you open Codex in this repo, install the plugin from `/plugins`, then ask:

```text
Use the install-claude-codex-bridge skill to install the full bridge into this project.
```

To enable the hook immediately:

```text
Use the install-claude-codex-bridge skill to install the full bridge into this project and enable the hook.
```

<a id="quick-start"></a>
## 🚀 Quick Start

### 🥇 Claude Plugin First

If Claude Code already has plugin support in your environment, use the plugin path first.

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

Local directory sources do not support `--sparse`; use `--sparse .claude-plugin plugins` only when the marketplace source is GitHub or another git source.

That gives the project a native Claude plugin package instead of copied bridge files.

### 📁 Manual Project-Local Install

Use this fallback when you want the bridge as plain files in one repository.

```bash
git clone https://github.com/ZhangYiqun018/claude-codex-bridge.git
cd claude-codex-bridge

cp .mcp.json /path/to/your/project/
cp -r .claude /path/to/your/project/
./hooks/install-hook.sh --project /path/to/your/project
```

<details>
<summary>Global install</summary>

Use this when you want the same bridge available across projects.

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

Restart Claude Code after installation.

<a id="choose-a-bridge"></a>
## 🧭 Choose a Bridge

| If you want to... | Use | Why | Config |
|-------------------|-----|-----|--------|
| Ask one well-formed question | `MCP bridge` | Fastest path, smallest setup cost | `.mcp.json` |
| Hand off a compact workflow | `Subagent bridge` | Claude gets back a structured result | inherits `.mcp.json` |
| Review git-defined changes | `Review skill` | Cleanest path when git already defines scope | `~/.codex/config.toml` |
| Auto-answer routine decisions | `Hook bridge` | Automates routine low-risk decisions | hook default -> env -> flag |

<a id="best-practice-prompts"></a>
## 🗣️ Best-Practice Prompts

Name the bridge mode explicitly in your prompt. That keeps Claude from guessing the workflow.

### 🔌 MCP Bridge

Best for one external opinion, one comparison, or one focused technical question.

```text
Use the codex MCP tool to analyze the pros and cons of this migration plan and return exactly:
1. Main upside
2. Main downside
3. Recommendation
```

### 🧠 Subagent Bridge

Best for arbitrary file review, architecture work, multi-step synthesis, or anything that should come back as a compact handoff.

```text
Use the codex-integration subagent to review the auth subsystem and return exactly:
1. Key findings
2. Tradeoffs between the two refactor options
3. Recommended next step
4. File references
```

### 🔍 Review Skill

Best when git already defines the review scope.

```text
Use the codex-review skill to review my uncommitted changes and return exactly:
1. Critical findings
2. Missing tests
3. Risky assumptions
4. File references
```

<details>
<summary>Terminal equivalents</summary>

```bash
codex review --uncommitted
codex review --base main
codex review --commit HEAD~1
```

</details>

### 📏 Prompting Rules

- State the scope explicitly: `uncommitted changes`, `base main`, a commit SHA, a subsystem, or a file set.
- State the output shape explicitly: findings, tradeoffs, recommendations, next steps, or file references.
- Prefer `read-only` unless the task genuinely needs command execution.
- Use `codex-review` for git diffs and `codex-integration` for arbitrary files or custom review instructions.

<a id="reference"></a>
## 📚 Reference

### ✅ Requirements

- Requires Claude Code with MCP stdio support and hook support enabled, plus `codex-cli 0.116.0`.
- `./hooks/install-hook.sh --project /path/to/project` writes hook config to `/path/to/project/.claude/settings.local.json`.
- `./hooks/install-hook.sh --global` writes hook config to `~/.claude/settings.local.json`.
- Claude plugin marketplace entrypoint is `claude plugin marketplace add`; this repo exposes a local marketplace at `.claude-plugin/marketplace.json`.
- Codex plugin install entrypoint is `/plugins` inside the Codex CLI; this repo also exposes a Codex marketplace at `.agents/plugins/marketplace.json`.

<details>
<summary>Selective install</summary>

- MCP only: copy `.mcp.json` into the project or run `claude mcp add ...` globally.
- Subagent only: copy `.claude/agents/codex-integration.md` into `.claude/agents/` or `~/.claude/agents/`.
- Review skill only: copy `.claude/skills/codex-review/SKILL.md` into `.claude/skills/codex-review/` or `~/.claude/skills/codex-review/`.
- Hook only: run `./hooks/install-hook.sh --project /path/to/project` or `./hooks/install-hook.sh --global`.

</details>

<details>
<summary>Plugin packaging</summary>

- Claude marketplace: `.claude-plugin/marketplace.json`
- Claude plugin manifest: `plugins/claude-codex-bridge/.claude-plugin/plugin.json`
- Claude plugin components: `plugins/claude-codex-bridge/agents`, `plugins/claude-codex-bridge/skills`, `plugins/claude-codex-bridge/hooks`, `plugins/claude-codex-bridge/.mcp.json`
- Codex marketplace: `.agents/plugins/marketplace.json`
- Codex plugin manifest: `plugins/claude-codex-bridge/.codex-plugin/plugin.json`
- Codex installer skill: `plugins/claude-codex-bridge/skills/install-claude-codex-bridge/SKILL.md`
- Codex installer script: `plugins/claude-codex-bridge/scripts/install_bridge.py`

</details>

<details>
<summary>Hook overrides</summary>

Flag-file format:

```text
(line 1 reserved, leave empty)
gpt-5.4
/path/to/mockup.png,/path/to/screenshot.jpg
```

Optional environment variables:

```bash
export COPILOT_MODEL=gpt-5.4
export COPILOT_TIMEOUT=300
export COPILOT_DEBUG=1
export COPILOT_IMAGES=/path/to/mockup.png,/path/to/screenshot.jpg
export COPILOT_SYSTEM_PROMPT=/path/to/prompt.md
```

Reset one project's hook session:

```bash
rm /path/to/project/.copilot-session-id
```

</details>

<details>
<summary>Troubleshooting</summary>

- Claude cannot see `codex` MCP tools: confirm `.mcp.json` is present or the global MCP entry exists, then restart Claude Code.
- `codex review` uses the wrong model: check `~/.codex/config.toml`; the review path does not use `.mcp.json`.
- Hook does not trigger: confirm the hook is enabled and was installed into the target project's or global `settings.local.json`.
- Hook fails silently: set `COPILOT_DEBUG=1` and inspect `/tmp/claude-copilot-hook.log`.
- Codex auth errors: run `codex login`.

</details>

## 🛡️ Safety

- Never send secrets or credentials unless you intentionally want Codex to see them.
- Default to `read-only` whenever possible.
- Treat the hook as automation, not as the safe default for high-risk decisions.
- Keep `.claude/settings.local.json` local; this repository intentionally ignores it.

## 📄 License

MIT. See [LICENSE](./LICENSE).
