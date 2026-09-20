#!/usr/bin/env bash
set -euo pipefail

echo "=== Hermes Collab Protocol Installer ==="
echo ""

# Detect device and set label
HOSTNAME=$(hostname)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    DEVICE_LABEL_FILE="$HOME/.config/device-label"
    if [ ! -f "$DEVICE_LABEL_FILE" ]; then
        echo "Setting up device label at ~/.config/device-label"
        echo "${HOSTNAME}-fedora" > "$DEVICE_LABEL_FILE"
    fi
    DEVICE_ID="${HOSTNAME}-$(cat "$DEVICE_LABEL_FILE" 2>/dev/null || echo 'fedora')"
    SCRIPTS_DIR="$HOME/.hermes/scripts"
    SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
    SCRIPT_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/project-collab.py"
    SKILL_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/SKILL.md"
    REF_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/reference-manifest.md"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    DEVICE_LABEL_FILE="$LOCALAPPDATA/hermes/device-label"
    if [ ! -f "$DEVICE_LABEL_FILE" ]; then
        echo "Setting up device label at ~/AppData/Local/hermes/device-label"
        mkdir -p "$HOME/AppData/Local/hermes"
        echo "${HOSTNAME}-windows" > "$DEVICE_LABEL_FILE"
    fi
    DEVICE_ID="${HOSTNAME}-$(cat "$DEVICE_LABEL_FILE" 2>/dev/null || echo 'windows')"
    SCRIPTS_DIR="$HOME/.hermes/scripts"
    SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
    SCRIPT_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/project-collab.py"
    SKILL_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/SKILL.md"
    REF_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/reference-manifest.md"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Device ID: $DEVICE_ID"
echo ""

# Create directories
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$SKILLS_DIR"

# Download project-collab.py
echo "Downloading project-collab.py..."
curl -fsSL "$SCRIPT_URL" -o "$SCRIPTS_DIR/project-collab.py"
chmod +x "$SCRIPTS_DIR/project-collab.py"
echo "  → $SCRIPTS_DIR/project-collab.py"

# Download SKILL.md
echo "Downloading SKILL.md..."
curl -fsSL "$SKILL_URL" -o "$SKILLS_DIR/SKILL.md"
echo "  → $SKILLS_DIR/SKILL.md"

# Download reference-manifest.md
echo "Downloading reference-manifest.md..."
curl -fsSL "$REF_URL" -o "$SKILLS_DIR/reference-manifest.md"
echo "  → $SKILLS_DIR/reference-manifest.md"

# Verify gh CLI
echo ""
echo "Checking gh CLI..."
if command -v gh &> /dev/null; then
    echo "  ✓ gh CLI found"
    gh auth status 2>/dev/null || echo "  ⚠ gh not authenticated. Run: gh auth login"
else
    echo "  ✗ gh CLI not found. Install: https://cli.github.com/"
fi

# Check git
echo "Checking git..."
if command -v git &> /dev/null; then
    echo "  ✓ git found ($(git --version | awk '{print $3}'))"
else
    echo "  ✗ git not found"
fi

# Verify agent CLIs
echo ""
echo "Checking agent CLIs..."
for agent in hermes claude codex opencode; do
    if command -v "$agent" &> /dev/null; then
        echo "  ✓ $agent found"
    else
        echo "  ○ $agent not found (optional — needed for task execution)"
    fi
done

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "  1. Authenticate gh if needed:  gh auth login"
echo "  2. Verify device label:         cat ~/.config/device-label"
echo "  3. Initialize in a repo:        cd your-repo && project-collab.py init"
echo "  4. Pull issues:                 project-collab.py pull"
echo "  5. Claim a task:                project-collab.py claim <number>"
echo ""
echo "For cron automation:"
echo "  hermes cron create \"project sync\" --script project-collab.py --schedule \"every 30 minutes\""
echo ""
echo "Protocol documentation: https://github.com/sambaseness/hermes-collab-protocol"
