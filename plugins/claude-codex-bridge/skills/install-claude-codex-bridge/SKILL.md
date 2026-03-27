---
name: install-claude-codex-bridge
description: Install or update the Claude-Codex bridge into the current project or globally. Supports full install and component-only install for MCP, subagent, review skill, or hook.
---

# Install Claude-Codex Bridge

Use this skill when the user wants to install or update the bridge from this plugin into a repository or into their global Claude Code config.

## Default behavior

- If the user says "install it here", treat that as a project-local install into the current working directory.
- If the user asks for all bridge components, use `--mode full`.
- If the user asks for only one component, map to one of:
  - `mcp`
  - `subagent`
  - `review-skill`
  - `hook`
- If the user wants the hook active immediately in the current project, add `--enable-hook`.

## Commands

Project-local full install into the current repo:

```bash
python3 ../../scripts/install_bridge.py --project "$PWD" --mode full
```

Project-local full install and immediately enable the hook:

```bash
python3 ../../scripts/install_bridge.py --project "$PWD" --mode full --enable-hook
```

Project-local component install:

```bash
python3 ../../scripts/install_bridge.py --project "$PWD" --mode mcp
python3 ../../scripts/install_bridge.py --project "$PWD" --mode subagent
python3 ../../scripts/install_bridge.py --project "$PWD" --mode review-skill
python3 ../../scripts/install_bridge.py --project "$PWD" --mode hook
```

Global install:

```bash
python3 ../../scripts/install_bridge.py --global --mode full
```

## After running

- Summarize which files were written or updated.
- Tell the user when Claude Code should be restarted.
- If the hook was installed but not enabled in a project, remind the user to create `.enable-copilot` in the target project.
- If global MCP installation fails because `claude` is unavailable, explain that the file-based parts were still installed and show the manual `claude mcp add ...` command.
