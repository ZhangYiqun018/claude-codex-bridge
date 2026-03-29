#!/usr/bin/env python3
"""Register Claude Code as an MCP server for Codex."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install or update the Claude Code MCP bridge for Codex."
    )
    parser.add_argument(
        "--name",
        default="claude-code",
        help="Name for the Codex MCP server entry.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing entry when its command differs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without changing Codex config.",
    )
    return parser.parse_args()


def run_json(cmd: list[str]) -> dict[str, Any] | None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def same_transport(existing: dict[str, Any], claude_bin: str) -> bool:
    transport = existing.get("transport", {})
    command = transport.get("command")
    args = transport.get("args", [])
    return command in {claude_bin, "claude"} and args == ["mcp", "serve"]


def main() -> int:
    args = parse_args()

    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise SystemExit("`codex` not found in PATH. Install Codex CLI first.")

    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise SystemExit("`claude` not found in PATH. Install Claude Code first.")

    existing = run_json([codex_bin, "mcp", "get", args.name, "--json"])
    if existing and same_transport(existing, claude_bin):
        print(f"Codex MCP server '{args.name}' is already configured for Claude Code.")
        print(json.dumps(existing, indent=2))
        return 0

    if existing and not args.force:
        print(
            f"Codex MCP server '{args.name}' already exists with a different command.",
            file=sys.stderr,
        )
        print("Rerun with --force to replace it.", file=sys.stderr)
        return 1

    add_cmd = [codex_bin, "mcp", "add", args.name, "--", claude_bin, "mcp", "serve"]

    if args.dry_run:
        print("Would run:")
        print(" ".join(add_cmd))
        return 0

    if existing:
        subprocess.run([codex_bin, "mcp", "remove", args.name], check=True)

    subprocess.run(add_cmd, check=True)

    installed = run_json([codex_bin, "mcp", "get", args.name, "--json"])
    print(f"Configured Codex MCP server '{args.name}' for Claude Code.")
    if installed:
        print(json.dumps(installed, indent=2))
    print("")
    print("Restart Codex to pick up the new MCP server.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
