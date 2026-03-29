---
name: codex-debate
description: Run a multi-turn debate with Codex from Claude Code. Use when Claude should hold a structured point-by-point discussion with Codex over multiple rounds and then synthesize the outcome for the user.
---

# Codex Debate

Use `codex` for the first round and `codex-reply` for follow-up rounds.

This skill is the debate-specific counterpart to `codex-integration`.

## Routing Rules

- Prefer this skill when the user explicitly wants a debate, rebuttal, or point-by-point disagreement handling.
- Prefer `codex-integration` for general analysis or one-off second opinions.
- Prefer `codex-review` for plain git-diff review.

## Debate Protocol

Round 1:

```text
Tool: codex
Parameters:
  prompt: "Debate this question:
  Question: ...
  Shared facts:
  - ...
  Return exactly:
  1. Initial position
  2. Main arguments
  3. Risks
  4. File references"
  sandbox: "read-only"
```

Round 2+:

```text
Tool: codex-reply
Parameters:
  threadId: "<threadId from previous response>"
  prompt: "Continue the debate point-by-point.
  Shared facts:
  - ...

  Claude current view:
  - ...

  Codex previous view:
  - ...

  Specific disagreements:
  1. ...
  2. ...

  Return exactly:
  1. Point-by-point response
  2. Updated position
  3. Remaining disagreements
  4. File references"
```

## End Condition

- Prefer 2-4 rounds.
- Stop earlier if the disagreement is clearly about preference rather than factual tradeoffs.
- After the last round, synthesize:
  - Shared conclusions
  - Remaining disagreements
  - Recommended next step
  - File references
