---
name: install-claude-code-mcp
description: Register Claude Code as an MCP server for Codex. Use when Codex should be able to call `claude mcp serve` and access Claude Code's tool surface through a `claude-code` MCP entry.
---

# Install Claude Code MCP

Use this skill when the user wants Codex to call Claude Code through MCP.

## Default Behavior

- Register an MCP server named `claude-code`.
- Use the local `claude` binary resolved from `PATH`.
- If an entry with the same name already matches `claude mcp serve`, report success and stop.
- If an entry already exists with a different command, rerun with `--force`.

## Commands

Install the default `claude-code` MCP server:

```bash
python3 ../../scripts/install_claude_code_mcp.py
```

Replace an existing mismatched entry:

```bash
python3 ../../scripts/install_claude_code_mcp.py --force
```

Use a different Codex MCP server name:

```bash
python3 ../../scripts/install_claude_code_mcp.py --name claude-code-prod
```

## After Running

- Summarize the configured MCP server name.
- Tell the user to restart Codex.
- If installation fails, report whether `codex` or `claude` was missing from `PATH`.
