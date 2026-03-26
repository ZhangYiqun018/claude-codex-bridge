#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SCRIPT="claude_copilot_hook.py"
INSTALL_DIR="$HOME/.claude-codex-bridge"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

command -v python3 >/dev/null 2>&1 || error "python3 not found. Install Python 3.8+."
command -v codex >/dev/null 2>&1 || error "codex not found. Install Codex CLI first."

PY_VERSION=$(python3 -c 'import sys; print(sys.version_info >= (3, 8))')
[ "$PY_VERSION" = "True" ] || error "Python 3.8+ required."

GLOBAL=false
PROJECT_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        --global)
            GLOBAL=true
            shift
            ;;
        --project)
            [ $# -ge 2 ] || error "--project requires a directory"
            PROJECT_DIR="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./hooks/install-hook.sh [--global] [--project /path/to/project]"
            echo ""
            echo "  --global              Install hook into ~/.claude/settings.local.json"
            echo "  --project <DIR>       Install hook into <DIR>/.claude/settings.local.json"
            echo "                        Default when omitted: current working directory"
            exit 0
            ;;
        *)
            error "Unknown argument: $1"
            ;;
    esac
done

if [ "$GLOBAL" = true ] && [ -n "$PROJECT_DIR" ]; then
    error "Use either --global or --project, not both."
fi

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/$HOOK_SCRIPT" "$INSTALL_DIR/$HOOK_SCRIPT"
chmod +x "$INSTALL_DIR/$HOOK_SCRIPT"
info "Installed $HOOK_SCRIPT to $INSTALL_DIR/"

HOOK_CMD="python3 \"$INSTALL_DIR/$HOOK_SCRIPT\""

if [ "$GLOBAL" = true ]; then
    SETTINGS_DIR="$HOME/.claude"
    TARGET_LABEL="global Claude Code config"
else
    if [ -z "$PROJECT_DIR" ]; then
        PROJECT_DIR="$PWD"
    fi
    SETTINGS_DIR="$PROJECT_DIR/.claude"
    TARGET_LABEL="project config at $PROJECT_DIR"
fi

SETTINGS_FILE="$SETTINGS_DIR/settings.local.json"
mkdir -p "$SETTINGS_DIR"

HOOK_CONFIG=$(cat <<HOOKJSON
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "AskUserQuestion",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOK_CMD",
            "timeout": 300
          }
        ]
      }
    ]
  }
}
HOOKJSON
)

if [ -f "$SETTINGS_FILE" ]; then
    if SETTINGS_FILE="$SETTINGS_FILE" python3 - <<'PY' >/dev/null 2>&1
import json
import os
import sys

with open(os.environ["SETTINGS_FILE"]) as f:
    data = json.load(f)

for item in data.get("hooks", {}).get("PreToolUse", []):
    if item.get("matcher") != "AskUserQuestion":
        continue
    for hook in item.get("hooks", []):
        command = hook.get("command", "").lower()
        if "claude_copilot_hook.py" in command or "copilot" in command:
            sys.exit(0)
sys.exit(1)
PY
    then
        warn "Hook already configured in $SETTINGS_FILE - skipping"
    else
        SETTINGS_FILE="$SETTINGS_FILE" HOOK_CONFIG="$HOOK_CONFIG" python3 - <<'PY'
import json
import os

settings_file = os.environ["SETTINGS_FILE"]
hook_config = json.loads(os.environ["HOOK_CONFIG"])

with open(settings_file) as f:
    settings = json.load(f)

settings.setdefault("hooks", {})
settings["hooks"].setdefault("PreToolUse", [])
settings["hooks"]["PreToolUse"].extend(hook_config["hooks"]["PreToolUse"])

with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)
    f.write("\n")
PY
        info "Merged hook config into $SETTINGS_FILE"
    fi
else
    printf "%s\n" "$HOOK_CONFIG" > "$SETTINGS_FILE"
    info "Created $SETTINGS_FILE"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo "Target: $TARGET_LABEL"
echo ""
if [ "$GLOBAL" = false ]; then
    echo "To activate in the target project:"
    echo "  touch \"$PROJECT_DIR/.enable-copilot\""
    echo ""
    echo "To deactivate:"
    echo "  rm \"$PROJECT_DIR/.enable-copilot\""
else
    echo "To activate in any project:"
    echo "  touch /path/to/project/.enable-copilot"
    echo ""
    echo "To deactivate:"
    echo "  rm /path/to/project/.enable-copilot"
fi
echo ""
echo "Optional environment variables:"
echo "  COPILOT_MODEL=gpt-5.4"
echo "  COPILOT_TIMEOUT=300"
echo "  COPILOT_DEBUG=1"
echo "  COPILOT_IMAGES=a.png,b.jpg"
echo "  COPILOT_SYSTEM_PROMPT=/path/to/prompt.md"
echo ""
echo "Debug log: /tmp/claude-copilot-hook.log"
