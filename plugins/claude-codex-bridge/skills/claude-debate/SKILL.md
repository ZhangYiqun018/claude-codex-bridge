---
name: claude-debate
description: Run a multi-turn debate with Claude Code from Codex. Use when Codex should hold a structured point-by-point discussion with Claude, persist the Claude session explicitly, and then synthesize agreement and disagreement.
---

# Claude Debate

Use this skill when Codex should debate a design or implementation choice with Claude across multiple rounds.

This skill depends on explicit Claude session persistence through `ask_claude.py --session-name`.

## Debate Protocol

Round 1:
- State the question.
- State shared facts.
- Ask Claude for an initial opinion and request a concise position.

Round 2+:
- Reuse the same session with `--continue-session`.
- Pass:
  - Shared facts
  - Codex's current view
  - Claude's previous view
  - Specific disagreements
- Ask Claude to respond point-by-point.

Final round:
- Ask Claude for its final position.
- Then synthesize for the user:
  - Shared conclusions
  - Remaining disagreements
  - Recommended next step
  - File references

## Commands

Start a new debate:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --session-name claude-debate --show-session-id --prompt "Debate this question:

Question: Should we keep the current migration layer or replace it with direct service calls?
Shared facts:
- The current layer is used by 4 routes.
- Two recent bugs came from translation logic.

Return exactly:
1. Initial position
2. Main arguments
3. Risks
4. File references"
```

Continue the same debate:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --session-name claude-debate --continue-session --prompt "Continue the debate point-by-point.

Shared facts:
- The migration layer is still used by 4 routes.
- The bugs came from translation logic, not transport.

Codex current view:
- Keep the layer for now, but narrow its scope.

Claude previous view:
- Remove the layer and simplify the stack.

Specific disagreements:
1. Whether translation logic belongs in a dedicated layer
2. Whether near-term removal risk is acceptable

Return exactly:
1. Point-by-point response
2. Updated position
3. Remaining disagreements
4. File references"
```

Reset the saved debate session before starting over:

```bash
python3 ../../scripts/ask_claude.py --cwd "$PWD" --session-name claude-debate --reset-session --prompt "Start a new debate on ..."
```

## Notes

- The session file is stored under `.claude-codex-bridge/sessions/claude-debate.json` in the target repository.
- Prefer 2-4 rounds. Stop earlier if the disagreement is preference-based rather than factual.
- Always return a synthesis after the final Claude round instead of dumping raw back-and-forth.
