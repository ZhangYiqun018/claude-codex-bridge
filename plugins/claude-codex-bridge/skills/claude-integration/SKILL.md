---
name: claude-integration
description: Use Claude Code from Codex for file-based review, architecture analysis, brainstorming, or follow-up debate. Use when Codex should ask Claude for a second opinion with arbitrary file scope or custom prompt steering.
---

# Claude Integration

Use Claude Code directly from Codex through the bundled `ask_claude.py` wrapper.

This is the Codex-side counterpart to the Claude-side `codex-integration` agent: Codex remains the primary agent, and asks Claude for a second opinion when that is useful.

## Routing Rules

- Prefer this skill when you want Claude's view on arbitrary files, architecture tradeoffs, or a custom review prompt.
- Prefer `codex-review` when plain git-diff review by Codex is enough.
- Prefer `claude-debate` for a structured multi-round disagreement workflow.
- Prefer `install-claude-code-mcp` when you want Claude Code's MCP tool surface available inside Codex, not just a Claude answer.

## Commands

Single-shot consultation:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --prompt "Review the auth subsystem and return exactly:
1. Key findings
2. Tradeoffs between the two refactor options
3. Recommended next step
4. File references"
```

Continue the named Claude conversation in the same repository:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --session-name claude-integration --continue-session --prompt "Respond point-by-point to the disagreement on the caching layer."
```

Constrain Claude's tool access when needed:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" \
  --allowed-tool "Read" \
  --allowed-tool "Grep" \
  --allowed-tool "Glob" \
  --allowed-tool "LS" \
  --prompt "Inspect the migration files and summarize the rollback risks."
```

## Output Shape

Return a compact handoff back to the user:

```text
1. Key findings
2. Recommendations
3. Disagreements or caveats
4. File references
```

## Notes

- Claude CLI must be installed and authenticated locally.
- Prefer `--session-name` with `--continue-session` so Codex reuses an explicit Claude session instead of the repository's most recent session implicitly.
- Keep prompts structured. Explicit scope plus explicit output format produces the best Codex-to-Claude handoffs.
