#!/usr/bin/env python3
"""
Claude Copilot Hook — Route AskUserQuestion to Codex CLI.

Intercepts AskUserQuestion calls from Claude Code and routes them to a
"digital twin" Codex session that makes decisions autonomously.

Multi-turn support:
  First invocation creates a new Codex session; subsequent invocations
  resume it via `codex exec resume <session-id>`, giving Codex full
  memory of all previous decisions.

  Session ID is stored at $CLAUDE_PROJECT_DIR/.copilot-session-id

Activation:
  touch .enable-copilot          # in your project root
Deactivation:
  rm .enable-copilot

Environment variables:
  COPILOT_MODEL       Model to use (default: gpt-5.4)
  COPILOT_TIMEOUT     Codex timeout in seconds (default: 300)
  COPILOT_DEBUG       Set to 1 to enable debug logging
  COPILOT_IMAGES      Comma-separated image paths to pass via -i
  COPILOT_SYSTEM_PROMPT  Path to a custom system prompt file

Zero dependencies — stdlib only, Python 3.8+.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


DEFAULT_MODEL = "gpt-5.4"
DEFAULT_TIMEOUT = 300
LOG_FILE = "/tmp/claude-copilot-hook.log"
FLAG_FILENAME = ".enable-copilot"
SESSION_FILENAME = ".copilot-session-id"

DEBUG = os.environ.get("COPILOT_DEBUG", "")


def log_debug(msg: str) -> None:
    """Append debug line to log file when COPILOT_DEBUG is set."""
    if not DEBUG:
        return
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except OSError:
        pass


def main() -> None:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    flag_file = Path(project_dir) / FLAG_FILENAME

    if not flag_file.exists():
        sys.exit(0)

    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    try:
        if input_data.get("tool_name") != "AskUserQuestion":
            sys.exit(0)

        questions = input_data.get("tool_input", {}).get("questions", [])
        if not questions:
            sys.exit(0)

        question_text = format_questions(questions)
        log_debug(f"Intercepted AskUserQuestion: {question_text[:200]}...")

        model = os.environ.get("COPILOT_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
        timeout = parse_timeout(os.environ.get("COPILOT_TIMEOUT", str(DEFAULT_TIMEOUT)))
        model = read_flag_file_config(flag_file, "model", model)

        session_file = Path(project_dir) / SESSION_FILENAME
        session_id = None
        if session_file.exists():
            sid = session_file.read_text().strip()
            if sid:
                session_id = sid

        image_files = collect_images(flag_file)

        if session_id:
            prompt = build_resume_prompt(question_text)
        else:
            system_prompt = load_system_prompt()
            prompt = build_initial_prompt(system_prompt, question_text)

        output_file = None
        try:
            output_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            )
            output_file.close()

            if session_id:
                cmd = [
                    "codex",
                    "exec",
                    "resume",
                    session_id,
                    "--model",
                    model,
                    "--skip-git-repo-check",
                    "-o",
                    output_file.name,
                ]
            else:
                cmd = [
                    "codex",
                    "exec",
                    "--model",
                    model,
                    "--sandbox",
                    "read-only",
                    "--skip-git-repo-check",
                    "-o",
                    output_file.name,
                ]

            for img in image_files[:5]:
                cmd.extend(["-i", str(img)])

            cmd.append(prompt)

            log_debug(f"Running: {' '.join(cmd[:6])}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            log_debug(f"Codex returncode={result.returncode}")

            response_text = Path(output_file.name).read_text().strip()
            if not response_text:
                response_text = result.stdout.strip()

            if result.returncode != 0 or not response_text:
                log_debug(
                    f"Fail-open: returncode={result.returncode} "
                    f"response_empty={not response_text}"
                )
                if result.stderr:
                    log_debug(f"stderr: {result.stderr[:500]}")
                sys.exit(0)

            if not session_id:
                new_session_id = extract_session_id(
                    result.stderr + result.stdout, Path(project_dir)
                )
                if new_session_id:
                    session_file.write_text(new_session_id)
                    log_debug(f"Saved session ID: {new_session_id}")

            log_debug(f"Response: {response_text[:300]}...")

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            log_debug(f"Exception (fail-open): {e}")
            sys.exit(0)
        finally:
            if output_file:
                try:
                    os.unlink(output_file.name)
                except OSError:
                    pass

        decision_text = (
            f"[Copilot Decision via Codex]\n\n"
            f"{response_text}\n\n"
            f"Proceed based on this automated decision. "
            f"Do not ask the user again for this decision."
        )
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": decision_text,
            },
        }

        log_debug("Writing deny response to stdout")
        json.dump(output, sys.stdout)
        sys.stdout.flush()
        sys.exit(0)

    except Exception as e:
        log_debug(f"Unhandled exception (fail-open): {e}")
        sys.exit(0)


def parse_timeout(raw_value: str) -> int:
    """Parse COPILOT_TIMEOUT safely and fall back to default on bad values."""
    try:
        timeout = int(raw_value)
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        return timeout
    except (TypeError, ValueError) as e:
        log_debug(f"Invalid COPILOT_TIMEOUT={raw_value!r}; using default: {e}")
        return DEFAULT_TIMEOUT


def extract_session_id(output: str, project_dir: Optional[Path] = None) -> Optional[str]:
    """Extract session ID from codex exec output or the newest matching session."""
    for line in output.splitlines():
        if "session id:" in line.lower():
            return line.split(":", 1)[1].strip()

    return extract_session_id_from_disk(project_dir)


def extract_session_id_from_disk(project_dir: Optional[Path]) -> Optional[str]:
    """Find the newest session file, preferring sessions from this project."""
    sessions_dir = Path.home() / ".codex" / "sessions"
    if not sessions_dir.is_dir():
        return None

    all_files = sorted(
        sessions_dir.rglob("rollout-*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not all_files:
        return None

    preferred_dir = None
    if project_dir is not None:
        try:
            preferred_dir = project_dir.resolve()
        except OSError:
            preferred_dir = project_dir

    fallback_id = None
    for path in all_files:
        session_id, session_cwd = read_session_meta(path)
        if session_id and fallback_id is None:
            fallback_id = session_id

        if not session_id or preferred_dir is None or session_cwd is None:
            continue

        try:
            if session_cwd.resolve() == preferred_dir:
                return session_id
        except OSError:
            if session_cwd == preferred_dir:
                return session_id

    return fallback_id


def read_session_meta(path: Path) -> Tuple[Optional[str], Optional[Path]]:
    """Read session id and cwd from the session_meta event in a rollout file."""
    try:
        with path.open() as f:
            for line in f:
                event = json.loads(line)
                if event.get("type") != "session_meta":
                    continue
                payload = event.get("payload", {})
                session_id = payload.get("id")
                cwd = payload.get("cwd")
                return session_id, Path(cwd) if cwd else None
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass

    return None, None


def read_flag_lines(flag_file: Path) -> List[str]:
    """Preserve blank lines so line-indexed config matches the README."""
    try:
        return flag_file.read_text().splitlines()
    except OSError:
        return []


def format_questions(questions: list) -> str:
    """Format AskUserQuestion questions into readable text for Codex."""
    parts = []
    for q in questions:
        text = q.get("question", "")
        options = q.get("options", [])
        multi = q.get("multiSelect", False)
        header = q.get("header", "")

        if header:
            parts.append(f"[{header}]")
        parts.append(f"Question: {text}")
        if multi:
            parts.append("(Multiple selections allowed)")
        for i, opt in enumerate(options):
            label = opt.get("label", "")
            desc = opt.get("description", "")
            parts.append(f"  Option {i + 1}: {label} -- {desc}")
        parts.append("")

    return "\n".join(parts)


def read_flag_file_config(flag_file: Path, key: str, default: str) -> str:
    """Read optional config from flag file lines."""
    lines = read_flag_lines(flag_file)

    if key == "model" and len(lines) >= 2 and lines[1].strip():
        return lines[1].strip()
    return default


def collect_images(flag_file: Path) -> List[str]:
    """Collect image paths from COPILOT_IMAGES env var or flag file line 3."""
    images = []

    env_images = os.environ.get("COPILOT_IMAGES", "")
    if env_images:
        for p in env_images.split(","):
            p = p.strip()
            if p and Path(p).exists():
                images.append(p)

    lines = read_flag_lines(flag_file)
    if len(lines) >= 3 and lines[2].strip():
        for p in lines[2].strip().split(","):
            p = p.strip()
            if p and Path(p).exists() and p not in images:
                images.append(p)

    return images


def load_system_prompt() -> str:
    """Load custom system prompt from COPILOT_SYSTEM_PROMPT or use default."""
    custom_path = os.environ.get("COPILOT_SYSTEM_PROMPT", "")
    if custom_path and Path(custom_path).exists():
        try:
            return Path(custom_path).read_text()
        except OSError:
            pass

    return DEFAULT_SYSTEM_PROMPT


DEFAULT_SYSTEM_PROMPT = """\
You are an autonomous decision-making copilot for Claude Code.

When Claude Code encounters a decision point (AskUserQuestion), you receive
the question and its options. Your job:

1. Read the question and all options carefully.
2. Select the best option(s) based on:
   - Technical correctness and best practices
   - Safety (prefer conservative, reversible choices)
   - Simplicity (prefer the straightforward approach)
   - Consistency with previous decisions in this session
3. Respond with your selection and a brief justification.

Format your response as:
  Selected: <exact label text of chosen option(s), comma-separated if multiple>
  Reason: <1-2 sentence justification>

If you are uncertain between options, pick the safer / more conservative one.
Never refuse to answer - always select an option.\
"""


def build_initial_prompt(system_prompt: str, question_text: str) -> str:
    """First call: full system prompt + question."""
    return f"""{system_prompt}

---

# Decision Point

{question_text}

Select the best option and respond with:
  Selected: <option label>
  Reason: <brief justification>"""


def build_resume_prompt(question_text: str) -> str:
    """Subsequent calls: just the new question. Codex has full history."""
    return f"""# Next Decision Point

{question_text}

Same format - respond with Selected and Reason."""


if __name__ == "__main__":
    main()
