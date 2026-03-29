# Claude-Codex Bridge

[简体中文](./README.zh-CN.md)

![Claude Code](https://img.shields.io/badge/Claude_Code-Bridge-111827?style=flat-square)
![Codex CLI](https://img.shields.io/badge/Codex_CLI-0.117.0-2563eb?style=flat-square)
![Default Model](https://img.shields.io/badge/Default-gpt--5.4-0f766e?style=flat-square)
![Modes](https://img.shields.io/badge/Modes-MCP%20%7C%20Subagent%20%7C%20Skill%20%7C%20Hook-7c3aed?style=flat-square)
![Plugins](https://img.shields.io/badge/Plugins-Claude%20%7C%20Codex-1d4ed8?style=flat-square)

<p align="center">
  <img src="./assets/figure.png" alt="Claude-Codex Bridge" width="600">
</p>

> You already have Claude Code open. Now you need Codex's opinion on a migration plan.
>
> **Without this bridge**: Copy files, switch terminals, lose context, paste results back manually.
>
> **With this bridge**: Type one sentence, get Codex's structured analysis delivered right back to your Claude session.

This repo bridges the two AI coding assistants through **MCP**, **subagents**, **review skills**, and **hooks** — so you can use the best tool for each job without leaving your workflow.

**Who this is for:**
- Claude users who want Codex's perspective without context switching
- Codex users who want Claude's analysis without manual copy-paste
- Teams that want consistent, reviewable, automated decision-making

Jump to: [What's New](#whats-new) | [Plugin Matrix](#plugin-matrix) | [20-Second Demo](#demo-20s) | [Plugin Install](#plugin-install) | [Quick Start](#quick-start) | [Choose a Bridge](#choose-a-bridge) | [Best-Practice Prompts](#best-practice-prompts) | [Reference](#reference)

<a id="whats-new"></a>
## ✨ What's New

- Claude Code now has a native plugin install path for this repo. In plugin-enabled environments, you no longer need to copy the bridge files by hand.
- Codex now gets its own real runtime path too: the Codex plugin ships Claude-facing skills instead of acting only as a Claude-side installer.
- Codex -> Claude multi-turn conversations now have explicit session persistence through `.claude-codex-bridge/sessions/*.json` instead of relying only on repository-local "most recent session" behavior.
- Debate workflows now exist in both directions: `codex-debate` for Claude Code and `claude-debate` for Codex.
- The reverse bridge now has two Codex-side lanes: direct `claude -p` consultation and optional `claude mcp serve` registration through `codex mcp add`.
- The bridge defaults remain pinned to `gpt-5.4`, including the packaged MCP server config.

Claude-side install:

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

Codex-side install:

```text
Open `/plugins` in Codex, add this repo's marketplace, then install `claude-codex-bridge`.
```

<a id="plugin-matrix"></a>
## 🧭 Plugin Matrix

This repo now packages two different runtime plugins. They share one repository, but they do different jobs.

| If your primary host is... | Install this plugin | Direction | Main runtime capabilities | Use it when... | It does not do... |
|---|---|---|---|---|---|
| `Claude Code` | `Claude Code plugin` | `Claude -> Codex` | `codex-server` MCP, `codex-integration`, `codex-review`, `codex-debate`, optional hook | Your work starts in Claude and you want Codex inside that workflow | Let Codex consult Claude; that is the Codex plugin's job |
| `Codex` | `Codex plugin` | `Codex -> Claude` | `claude-integration`, `claude-review`, `claude-debate`, `install-claude-code-mcp` | Your work starts in Codex and you want Claude inside that workflow | Provide reverse hook automation; it depends on local Claude CLI instead |

Short version:
- Install the Claude plugin when Claude is the orchestrator and Codex is the external counterpart.
- Install the Codex plugin when Codex is the orchestrator and Claude is the external counterpart.
- Install both only if you actively use both directions.

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

3. In Codex, after installing the Codex plugin from `/plugins`, ask:

```text
Use the claude-integration skill to review the auth subsystem and return exactly:
1. Key findings
2. Tradeoffs
3. Recommended next step
4. File references
```

Result: Codex consults Claude Code directly instead of only helping Claude reach Codex.

<a id="plugin-install"></a>
## 🧩 Plugin Install

### 🤖 Claude Code Plugin

Install this when Claude Code is the place where you start the task.

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
- `codex-debate` skill
- AskUserQuestion hook packaged as plugin hooks

Claude may display the agent and skill under the `claude-codex-bridge` plugin namespace in `/agents` and `/skills`. When in doubt, refer to the plugin namespace explicitly.

The hook remains opt-in per project:

```bash
touch /path/to/project/.enable-copilot
```

### 🧰 Codex Plugin

Install this when Codex is the place where you start the task.

What it does well:
- Lets Codex ask Claude Code for a second opinion through `claude -p`.
- Adds a Claude-backed review path for uncommitted changes, base diffs, or specific commits.
- Adds a structured multi-round debate path with explicit Claude session persistence.
- Optionally registers `claude mcp serve` as `claude-code` inside Codex so Claude Code's MCP tools are available to Codex too.

What it does not replace:
- The Claude plugin is still the right path for Claude -> Codex MCP, subagent, review skill, and hook integration.
- The Codex reverse bridge depends on a local Claude Code CLI install and auth state.

This repo includes:
- Codex marketplace: `.agents/plugins/marketplace.json`
- Codex plugin root: `plugins/claude-codex-bridge`
- Claude consultation skill: `claude-integration`
- Claude debate skill: `claude-debate`
- Claude-backed review skill: `claude-review`
- Claude Code MCP install skill: `install-claude-code-mcp`
- Codex-native git review skill: `codex-review`

If you open Codex in this repo, install the plugin from `/plugins`, then ask:

```text
Use the claude-integration skill to review the auth subsystem and return exactly:
1. Key findings
2. Tradeoffs
3. Recommended next step
4. File references
```

To expose Claude Code tools inside Codex too:

```text
Use the install-claude-code-mcp skill to add Claude Code as an MCP server for Codex.
```

To run a structured multi-round debate from Codex:

```text
Use the claude-debate skill to debate whether we should keep the current migration layer or replace it with direct service calls.
```

<a id="quick-start"></a>
## 🚀 Quick Start

### 🤖 If You Start In Claude Code

Use the Claude plugin.

```bash
claude plugin marketplace add . --scope project
claude plugin install claude-codex-bridge --scope project
```

Local directory sources do not support `--sparse`; use `--sparse .claude-plugin plugins` only when the marketplace source is GitHub or another git source.

That gives you `Claude -> Codex` runtime integration.

### 🧰 If You Start In Codex

Use the Codex plugin.

Install it from `/plugins`, then use one of:

```text
Use the claude-integration skill to review the auth subsystem.
Use the claude-review skill to review my uncommitted changes.
Use the claude-debate skill to debate this design with Claude Code.
```

That gives you `Codex -> Claude` runtime integration.

### 🔁 If You Want Manual Codex-Side Wiring

Use this only if you do not want the Codex plugin and are wiring the reverse bridge by hand.

Manual Codex-side setup:

```bash
codex mcp add claude-code -- claude mcp serve
python3 plugins/claude-codex-bridge/scripts/ask_claude.py --cwd "$PWD" --prompt "Review the auth subsystem and return exactly:
1. Key findings
2. Tradeoffs
3. Recommended next step
4. File references"
```

The first command exposes Claude Code's MCP tool surface to Codex. The second asks Claude Code directly for a structured opinion.

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

mkdir -p ~/.claude/skills/codex-debate
cp .claude/skills/codex-debate/SKILL.md ~/.claude/skills/codex-debate/

./hooks/install-hook.sh --global
```

</details>

Restart Claude Code after installation.

<a id="choose-a-bridge"></a>
## 🧭 Choose a Bridge

| If you want to... | Use | Why | Config |
|-------------------|-----|-----|--------|
| From Claude, ask one well-formed question to Codex | `MCP bridge` | Fastest Claude -> Codex path | `.mcp.json` |
| From Claude, hand off a compact workflow to Codex | `Subagent bridge` | Claude gets back a structured result | inherits `.mcp.json` |
| From Claude, review git-defined changes with Codex defaults | `Review skill` | Cleanest Claude -> Codex path when git already defines scope | `~/.codex/config.toml` |
| From Claude, run a structured multi-round debate with Codex | `codex-debate` | Explicit rebuttal workflow using `codex` + `codex-reply` | Claude plugin/manual skill install |
| From Claude, auto-answer routine setup decisions with Codex | `Hook bridge` | Automates routine low-risk decisions | hook default -> env -> flag |
| From Codex, ask Claude for a second opinion | `claude-integration` | Direct Claude consultation with arbitrary file scope | `plugins/.../scripts/ask_claude.py` |
| From Codex, run a structured multi-round debate with Claude | `claude-debate` | Explicit Claude session persistence with point-by-point rounds | `.claude-codex-bridge/sessions/*.json` |
| From Codex, review changes through Claude | `claude-review` | Keeps Codex as orchestrator while adding Claude review | `plugins/.../scripts/ask_claude.py` |
| From Codex, expose Claude Code tools through MCP | `install-claude-code-mcp` | Adds `claude-code` MCP entry to Codex | `codex mcp` global config |

<a id="best-practice-prompts"></a>
## 🗣️ Best-Practice Prompts

Name the bridge mode explicitly in your prompt. That keeps both Claude and Codex from guessing the workflow.

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

### 🗣️ Debate Skill

Best when you want the two models to argue through the same question across multiple rounds and converge explicitly.

If the workflow starts in Claude:

```text
Use the `codex-debate` skill to run a 3-round debate with Codex on whether we should remove the current migration layer, and return exactly:
1. Rebuttal to the previous round
2. New evidence or risks
3. Current position
4. Final recommendation
```

If the workflow starts in Codex:

```text
Use the `claude-debate` skill to run a 3-round debate with Claude Code on whether we should remove the current migration layer, and return exactly:
1. Rebuttal to the previous round
2. New evidence or risks
3. Current position
4. Final recommendation
```

### 📏 Prompting Rules

- State the scope explicitly: `uncommitted changes`, `base main`, a commit SHA, a subsystem, or a file set.
- State the output shape explicitly: findings, tradeoffs, recommendations, next steps, or file references.
- For debate workflows, state the round count, debate topic, and convergence format so it does not collapse into a one-shot opinion.
- Prefer `read-only` unless the task genuinely needs command execution.
- Use `codex-review` for git diffs and `codex-integration` for arbitrary files or custom review instructions.

<a id="reference"></a>
## 📚 Reference

### ✅ Requirements

- Requires Claude Code with MCP stdio support and hook support enabled, plus `codex-cli 0.116.0`.
- Codex -> Claude consultation requires a local Claude Code CLI with `-p/--print` support.
- Codex -> Claude multi-turn continuation uses explicit session files under `.claude-codex-bridge/sessions/`.

### 📦 Installation & Configuration

<details>
<summary>Selective install</summary>

- MCP only: copy `.mcp.json` into the project or run `claude mcp add ...` globally.
- Subagent only: copy `.claude/agents/codex-integration.md` into `.claude/agents/` or `~/.claude/agents/`.
- Review skill only: copy `.claude/skills/codex-review/SKILL.md` into `.claude/skills/codex-review/` or `~/.claude/skills/codex-review/`.
- Debate skill only: copy `.claude/skills/codex-debate/SKILL.md` into `.claude/skills/codex-debate/` or `~/.claude/skills/codex-debate/`.
- Hook only: run `./hooks/install-hook.sh --project /path/to/project` or `./hooks/install-hook.sh --global`.

</details>

### 🏗️ Plugin Architecture

<details>
<summary>Plugin packaging structure</summary>

- Claude marketplace: `.claude-plugin/marketplace.json`
- Claude plugin manifest: `plugins/claude-codex-bridge/.claude-plugin/plugin.json`
- Claude plugin components: `plugins/claude-codex-bridge/agents`, `plugins/claude-codex-bridge/skills`, `plugins/claude-codex-bridge/hooks`, `plugins/claude-codex-bridge/.mcp.json`
- Codex marketplace: `.agents/plugins/marketplace.json`
- Codex plugin manifest: `plugins/claude-codex-bridge/.codex-plugin/plugin.json`
- Codex-side skills: `claude-integration`, `claude-review`, `claude-debate`, `install-claude-code-mcp`
- Helper scripts: `ask_claude.py`, `install_claude_code_mcp.py`

</details>

<details>
<summary>Capability matrix</summary>

| Capability | Claude -> Codex | Codex -> Claude | Notes |
|---|---|---|---|
| Arbitrary second opinion | Full | Full | Claude side uses MCP/subagent; Codex side uses `ask_claude.py` |
| Git-based review | Full | Prompt-driven | Codex side review is structured through Claude prompts |
| Multi-turn debate | Full | Full | Explicit session files for persistence |
| Routine decision hook | Full | Not supported | Reverse direction does not automate Claude prompts |

</details>

### ⚙️ Advanced Usage

<details>
<summary>Hook overrides</summary>

Flag-file format (`.enable-copilot`):

```text
(line 1 reserved, leave empty)
gpt-5.4
/path/to/mockup.png,/path/to/screenshot.jpg
```

Environment variables:

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

### 🔧 Troubleshooting

<details>
<summary>Common issues</summary>

- **Claude cannot see `codex` MCP tools**: confirm `.mcp.json` is present, then restart Claude Code.
- **Codex cannot see `claude-code` MCP tools**: run `codex mcp add claude-code -- claude mcp serve`, then restart Codex.
- **`codex review` uses wrong model**: check `~/.codex/config.toml`.
- **`claude-debate` resumes wrong conversation**: remove the saved file under `.claude-codex-bridge/sessions/`.
- **Hook does not trigger**: confirm the hook is installed in `settings.local.json`.
- **Hook fails silently**: set `COPILOT_DEBUG=1` and check `/tmp/claude-copilot-hook.log`.
- **Codex auth errors**: run `codex login`.

</details>

## 🛡️ Safety

- Never send secrets or credentials unless you intentionally want Codex to see them.
- Default to `read-only` whenever possible.
- Treat the hook as automation, not as the safe default for high-risk decisions.
- Keep `.claude/settings.local.json` local; this repository intentionally ignores it.

## 📄 License

MIT. See [LICENSE](./LICENSE).
