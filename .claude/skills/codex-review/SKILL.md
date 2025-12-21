---
name: codex-review
description: Use codex review command for git-based code review. Use when reviewing uncommitted changes, PR diffs, or specific commits.
---

# Codex Code Review

Use `codex review` for git-based code review tasks.

## Use Cases

- Review uncommitted changes before commit
- Review PR diff against base branch
- Review specific commits

## Commands

### Review Uncommitted Changes
```bash
codex review --uncommitted "Focus on security and error handling"
```

### Review Against Base Branch
```bash
codex review --base main "Review for breaking changes"
codex review --base develop "Check API compatibility"
```

### Review Specific Commit
```bash
codex review --commit <SHA> "Analyze this change"
codex review --commit HEAD~1 "Review last commit"
```

### With Custom Title
```bash
codex review --uncommitted --title "Feature: Add user auth" "Review implementation"
```

## Review Focus Areas

When requesting review, specify focus:

1. **Security**: injection, auth, data exposure
2. **Correctness**: logic errors, edge cases
3. **Performance**: inefficiencies, scaling issues
4. **Breaking changes**: API compatibility, migrations

## Example Prompts

```bash
# Security-focused
codex review --uncommitted "Check for security vulnerabilities, injection risks, and auth issues"

# Performance-focused
codex review --base main "Identify performance bottlenecks and optimization opportunities"

# General review
codex review --uncommitted "Provide comprehensive review: code quality, potential bugs, improvements"
```

## Limitations

- Requires git repository
- Reviews git diff only (not arbitrary files)
- May have usage limits
- For file-based review, use codex agent instead

## Output

Codex review returns:
- Summary of changes
- Issues found (with file:line references)
- Suggestions for improvement
