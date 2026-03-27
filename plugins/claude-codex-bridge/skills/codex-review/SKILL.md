---
name: codex-review
description: Use codex review for git-based diff review of uncommitted changes, changes against a base branch, or a specific commit. Use when the task is reviewing git changes rather than arbitrary files, and when Codex's default review behavior is sufficient without custom prompt steering.
---

# Codex Code Review

Use `codex review` for git-based code review tasks.

`codex review` uses the Codex CLI default model from `~/.codex/config.toml`, not the plugin `.mcp.json`. For consistency with this bridge, prefer `model = "gpt-5.4"` in `~/.codex/config.toml`.

## Decision Rules

- Use this skill when the review target is already defined by git state.
- Prefer `--uncommitted`, `--base`, or `--commit` over free-form prompt steering.
- If you need arbitrary files, custom review instructions, or architectural discussion, use the `codex-integration` agent instead.

## Use Cases

- Review uncommitted changes before commit
- Review PR diff against base branch
- Review specific commits

## Commands

### Review Uncommitted Changes
```bash
codex review --uncommitted
```

### Review Against Base Branch
```bash
codex review --base main
codex review --base develop
```

### Review Specific Commit
```bash
codex review --commit <SHA>
codex review --commit HEAD~1
```

### With Custom Title
```bash
codex review --uncommitted --title "Feature: Add user auth"
```

## Example Commands

```bash
# Review current worktree
codex review --uncommitted

# Review against a base branch
codex review --base main

# Review a specific commit
codex review --commit HEAD~1
```

## Known Issues

> **[2025-12-23] Bug: Prompt argument is not supported**
>
> The current `codex review` has a known bug: the prompt argument (e.g., `"Focus on security"`) is **NOT actually passed to the model**, although `codex review --help` documentation indicates this feature is supported.
>
> **Workaround**: Use commands without the prompt argument:
> ```bash
> codex review --uncommitted
> codex review --base main
> ```
>
> This document will be updated once the official fix is released.

## Limitations

- Requires git repository
- Reviews git diff only (not arbitrary files)
- May have usage limits
- For file-based review, use codex agent instead
- **[Bug]** Prompt argument currently not working, see Known Issues above

## Output

Codex review returns:
- Summary of changes
- Issues found (with file:line references)
- Suggestions for improvement
