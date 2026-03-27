#!/usr/bin/env python3
"""
Claude Copilot Hook - Route AskUserQuestion to Codex CLI.

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

Zero dependencies - stdlib only, Python 3.8+.
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
    """Read session_id and cwd from a rollout jsonl file."""
    try:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                session_id = data.get("session_id")
                cwd = data.get("cwd")
                if session_id:
                    return session_id, Path(cwd) if cwd else None
    except OSError:
        return None, None

    return None, None


def format_questions(questions: List[dict]) -> str:
    """Format AskUserQuestion payload into readable text."""
    parts = []
    for i, q in enumerate(questions, 1):
        question = q.get("question", "").strip()
        options = q.get("options", [])
        parts.append(f"{i}. {question}")
        for j, opt in enumerate(options, 1):
            label = opt.get("label", "").strip()
            desc = opt.get("description", "").strip()
            if desc:
                parts.append(f"   {j}) {label} - {desc}")
            else:
                parts.append(f"   {j}) {label}")
    return "\n".join(parts)


def build_initial_prompt(system_prompt: str, question_text: str) -> str:
    """Build first-turn prompt with system framing."""
    return (
        f"{system_prompt}\n\n"
        "A user prompt has been intercepted from Claude Code.\n"
        "Choose the best answer autonomously. Be decisive.\n\n"
        f"{question_text}\n\n"
        "Return only the final answer text Claude should follow."
    )


def build_resume_prompt(question_text: str) -> str:
    """Build continuation prompt for an existing session."""
    return (
        "Continue making autonomous decisions for this project.\n\n"
        f"{question_text}\n\n"
        "Return only the final answer text Claude should follow."
    )


def load_system_prompt() -> str:
    """Load custom system prompt if configured, else default."""
    path = os.environ.get("COPILOT_SYSTEM_PROMPT", "").strip()
    if path:
        try:
            return Path(path).read_text()
        except OSError as e:
            log_debug(f"Failed to read COPILOT_SYSTEM_PROMPT={path!r}: {e}")

    return (
        "You are a Codex copilot acting as a digital twin for the human user. "
        "Answer operational questions the way a pragmatic senior engineer would. "
        "Prefer the safest low-friction option that keeps work moving. "
        "Avoid asking for clarification unless the choices are genuinely ambiguous."
    )


def collect_images(flag_file: Path) -> List[Path]:
    """Collect image paths from env or flag file line 3."""
    images: List[Path] = []

    env_images = os.environ.get("COPILOT_IMAGES", "").strip()
    if env_images:
        images.extend(_split_image_list(env_images))

    flag_images = read_flag_file_config(flag_file, "images", "")
    if flag_images:
        images.extend(_split_image_list(flag_images))

    unique: List[Path] = []
    seen = set()
    for img in images:
        if img in seen or not img.exists():
            continue
        seen.add(img)
        unique.append(img)
    return unique


def _split_image_list(raw: str) -> List[Path]:
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def read_flag_file_config(flag_file: Path, key: str, default: str) -> str:
    """
    Read optional config from .enable-copilot.

    Format:
      line 1: reserved / ignored
      line 2: model
      line 3: comma-separated image list
    """
    try:
        lines = flag_file.read_text().splitlines()
    except OSError:
        return default

    mapping = {
        "model": 1,
        "images": 2,
    }
    idx = mapping.get(key)
    if idx is None or idx >= len(lines):
        return default

    value = lines[idx].strip()
    return value or default


if __name__ == "__main__":
    main()
