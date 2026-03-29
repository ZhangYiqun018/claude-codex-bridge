---
name: claude-review
description: Review git-defined changes through Claude Code from Codex. Use when Codex should ask Claude for an additional review of uncommitted changes, a base diff, or a specific commit, while Codex stays the orchestrator.
---

# Claude Review

Use Claude Code as a second reviewer from within Codex.

This skill is for Claude-backed review. If you only need Codex's own git review path, use `codex-review` instead.

## Commands

Review uncommitted changes:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --prompt "Review the uncommitted changes in this repository and return exactly:
1. Critical findings
2. Missing tests
3. Risky assumptions
4. File references"
```

Review against a base branch:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --prompt "Review the changes in this repository against base branch main and return exactly:
1. Critical findings
2. Missing tests
3. Risky assumptions
4. File references"
```

Review a specific commit:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --prompt "Review commit HEAD~1 in this repository and return exactly:
1. Critical findings
2. Missing tests
3. Risky assumptions
4. File references"
```

## Review Rules

- State the review scope explicitly: `uncommitted changes`, `base main`, or a commit reference.
- Ask for file references in the output so Codex can relay concrete findings.
- Narrow the scope first if the repository has too much unrelated churn.

## Limitations

- Requires local Claude Code auth.
- Depends on Claude Code being able to inspect the target repository from the current working directory.
- This is not a dedicated `git diff` subcommand like `codex review`; it is a structured Claude consultation driven by prompt scope.
