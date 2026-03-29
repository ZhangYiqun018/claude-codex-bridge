#!/usr/bin/env python3
"""Run Claude Code non-interactively for Codex-side bridge skills."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIRNAME = ".claude-codex-bridge"
SESSIONS_DIRNAME = "sessions"


def default_session_file(cwd: Path, session_name: str) -> Path:
    return cwd / STATE_DIRNAME / SESSIONS_DIRNAME / f"{session_name}.json"


def load_session_state(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def save_session_state(
    path: Path,
    *,
    session_id: str,
    cwd: Path,
    model: str | None,
    permission_mode: str,
    response: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "session_id": session_id,
        "cwd": str(cwd),
        "model": model,
        "permission_mode": permission_mode,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_stop_reason": response.get("stop_reason"),
        "last_result_uuid": response.get("uuid"),
    }
    path.write_text(json.dumps(state, indent=2) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask Claude Code a question from a Codex-side workflow."
    )
    parser.add_argument("prompt", nargs="?", help="Prompt text. Reads stdin if omitted.")
    parser.add_argument(
        "--prompt-file",
        type=Path,
        help="Read the prompt from a file instead of argv/stdin.",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="Working directory for the Claude run.",
    )
    parser.add_argument("--model", help="Optional Claude model override.")
    parser.add_argument(
        "--append-system-prompt",
        help="Append extra system guidance to Claude Code's default system prompt.",
    )
    parser.add_argument(
        "--permission-mode",
        default="default",
        choices=[
            "acceptEdits",
            "bypassPermissions",
            "default",
            "dontAsk",
            "plan",
            "auto",
        ],
        help="Claude Code permission mode.",
    )
    parser.add_argument(
        "--output-format",
        default="text",
        choices=["text", "json"],
        help="Output format from this wrapper.",
    )
    parser.add_argument(
        "--session-name",
        help=(
            "Logical Claude session name. Saves state under "
            "<cwd>/.claude-codex-bridge/sessions/<name>.json."
        ),
    )
    parser.add_argument(
        "--session-file",
        type=Path,
        help="Explicit path for persisted Claude session state.",
    )
    parser.add_argument(
        "--continue-session",
        action="store_true",
        help=(
            "Continue a previous Claude conversation. Prefer this with "
            "--session-name or --session-file for explicit session reuse."
        ),
    )
    parser.add_argument(
        "--resume",
        help="Resume a specific Claude session id instead of starting a new one.",
    )
    parser.add_argument(
        "--reset-session",
        action="store_true",
        help="Delete the persisted session file before running.",
    )
    parser.add_argument(
        "--show-session-id",
        action="store_true",
        help="Print the resolved Claude session id to stderr after a successful run.",
    )
    parser.add_argument(
        "--allowed-tool",
        action="append",
        default=[],
        help="Repeatable allow-list entry for Claude tools.",
    )
    parser.add_argument(
        "--tools",
        help="Explicit Claude built-in tools list, for example: Bash,Read,Grep,Glob",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the resolved Claude command to stderr before running it.",
    )
    return parser.parse_args()


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return args.prompt_file.read_text().strip()
    if args.prompt:
        return args.prompt.strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("A prompt is required via argv, --prompt-file, or stdin.")


def resolve_session_file(args: argparse.Namespace) -> Path | None:
    if args.session_file:
        return args.session_file
    if args.session_name:
        return default_session_file(args.cwd, args.session_name)
    return None


def main() -> int:
    args = parse_args()
    prompt = read_prompt(args)
    cwd = args.cwd.resolve()
    session_file = resolve_session_file(args)

    if args.reset_session and session_file and session_file.exists():
        session_file.unlink()

    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise SystemExit("`claude` not found in PATH. Install Claude Code first.")

    cmd = [
        claude_bin,
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        args.permission_mode,
    ]

    if args.model:
        cmd.extend(["--model", args.model])
    if args.append_system_prompt:
        cmd.extend(["--append-system-prompt", args.append_system_prompt])
    if args.tools:
        cmd.extend(["--tools", args.tools])
    if args.allowed_tool:
        cmd.extend(["--allowed-tools", ",".join(args.allowed_tool)])

    resume_id = args.resume
    if not resume_id and args.continue_session and session_file:
        state = load_session_state(session_file)
        if state:
            resume_id = state.get("session_id")

    if resume_id:
        cmd.extend(["--resume", resume_id])
    elif args.continue_session:
        cmd.append("--continue")

    cmd.append(prompt)

    if args.print_command:
        print("Running:", " ".join(cmd), file=sys.stderr)

    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.stdout:
            print(result.stdout, end="", file=sys.stderr)
        return result.returncode

    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print("Failed to parse Claude JSON response.", file=sys.stderr)
        if result.stdout:
            print(result.stdout, end="", file=sys.stderr)
        raise SystemExit(1) from exc

    session_id = response.get("session_id")
    if session_file and session_id:
        save_session_state(
            session_file,
            session_id=session_id,
            cwd=cwd,
            model=args.model,
            permission_mode=args.permission_mode,
            response=response,
        )

    if args.show_session_id and session_id:
        if session_file:
            print(f"Claude session id: {session_id} ({session_file})", file=sys.stderr)
        else:
            print(f"Claude session id: {session_id}", file=sys.stderr)

    if args.output_format == "json":
        print(json.dumps(response, indent=2))
        return 0

    output = response.get("result", "")
    if output:
        print(output.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
