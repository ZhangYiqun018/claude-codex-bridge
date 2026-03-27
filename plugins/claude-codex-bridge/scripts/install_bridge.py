#!/usr/bin/env python3
"""Install bridge files from this repository into a target project or globally."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the Claude-Codex bridge.")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--project", help="Install into the given project directory")
    scope.add_argument(
        "--global",
        action="store_true",
        dest="global_install",
        help="Install into the user's global Claude Code config",
    )
    parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "mcp", "subagent", "review-skill", "hook"],
        help="Which bridge component to install",
    )
    parser.add_argument(
        "--enable-hook",
        action="store_true",
        help="Touch .enable-copilot in the target project after installing the hook",
    )
    return parser.parse_args()


def copy_file(src: Path, dst: Path, written: list[str]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    written.append(str(dst))


def install_project_component(root: Path, project_dir: Path, mode: str, written: list[str]) -> None:
    if mode in {"full", "mcp"}:
        copy_file(root / ".mcp.json", project_dir / ".mcp.json", written)

    if mode in {"full", "subagent"}:
        copy_file(
            root / ".claude" / "agents" / "codex-integration.md",
            project_dir / ".claude" / "agents" / "codex-integration.md",
            written,
        )

    if mode in {"full", "review-skill"}:
        copy_file(
            root / ".claude" / "skills" / "codex-review" / "SKILL.md",
            project_dir / ".claude" / "skills" / "codex-review" / "SKILL.md",
            written,
        )

    if mode in {"full", "hook"}:
        subprocess.run(
            [str(root / "hooks" / "install-hook.sh"), "--project", str(project_dir)],
            check=True,
        )


def install_global_component(root: Path, mode: str, written: list[str]) -> None:
    home = Path.home()

    if mode in {"full", "mcp"}:
        try:
            subprocess.run(
                [
                    "claude",
                    "mcp",
                    "add",
                    "--transport",
                    "stdio",
                    "codex-server",
                    "--",
                    "codex",
                    "mcp-server",
                    "-c",
                    'model="gpt-5.4"',
                ],
                check=True,
            )
            written.append("claude mcp add codex-server")
        except FileNotFoundError:
            raise SystemExit(
                "Global MCP install requires the `claude` CLI. "
                "Run: claude mcp add --transport stdio codex-server -- codex mcp-server -c 'model=\"gpt-5.4\"'"
            )

    if mode in {"full", "subagent"}:
        copy_file(
            root / ".claude" / "agents" / "codex-integration.md",
            home / ".claude" / "agents" / "codex-integration.md",
            written,
        )

    if mode in {"full", "review-skill"}:
        copy_file(
            root / ".claude" / "skills" / "codex-review" / "SKILL.md",
            home / ".claude" / "skills" / "codex-review" / "SKILL.md",
            written,
        )

    if mode in {"full", "hook"}:
        subprocess.run([str(root / "hooks" / "install-hook.sh"), "--global"], check=True)


def main() -> int:
    args = parse_args()
    root = repo_root()
    written: list[str] = []

    if args.global_install:
        install_global_component(root, args.mode, written)
    else:
        project_dir = Path(args.project or ".").resolve()
        install_project_component(root, project_dir, args.mode, written)
        if args.enable_hook:
            flag = project_dir / ".enable-copilot"
            flag.touch(exist_ok=True)
            written.append(str(flag))

    print("Installed:")
    for item in written:
        print(f"- {item}")

    if not args.global_install and args.mode in {"full", "hook"} and not args.enable_hook:
        print("")
        print("Hook installed but not enabled in the target project.")
        print(f"Enable it with: touch {(Path(args.project or '.').resolve() / '.enable-copilot')}")

    print("")
    print("Restart Claude Code after installation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
