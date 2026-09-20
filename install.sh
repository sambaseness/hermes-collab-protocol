#!/usr/bin/env bash
set -euo pipefail

echo "=== Hermes Collab Protocol Installer ==="
echo ""

# Detect platform
PLATFORM=""
HOSTNAME=$(hostname)
SCRIPTS_DIR="$HOME/.hermes/scripts"
SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
DEVICE_LABEL_FILE=""
DEVICE_ID=""
SCRIPT_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/project-collab.py"
SKILL_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/SKILL.md"
REF_URL="https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/reference-manifest.md"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
    DEVICE_LABEL_FILE="$HOME/.config/device-label"
    SCRIPTS_DIR="$HOME/.hermes/scripts"
    SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
    DEVICE_LABEL_FILE="$HOME/.config/device-label"
    SCRIPTS_DIR="$HOME/.hermes/scripts"
    SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    PLATFORM="windows"
    DEVICE_LABEL_FILE="$LOCALAPPDATA/hermes/device-label"
    SCRIPTS_DIR="$HOME/.hermes/scripts"
    SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
else
    # Try hermes config location as fallback
    if [ -f "$HOME/.hermes/config.yaml" ] || [ -d "$HOME/.hermes" ]; then
        PLATFORM="unknown"
        DEVICE_LABEL_FILE="$HOME/.config/device-label"
        SCRIPTS_DIR="$HOME/.hermes/scripts"
        SKILLS_DIR="$HOME/.hermes/skills/hermes-collab"
    else
        echo "Unsupported platform: $OSTYPE"
        echo "Try running: curl -fsSL https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/install.sh | bash"
        exit 1
    fi
fi

# Set device label
if [ ! -f "$DEVICE_LABEL_FILE" ]; then
    echo "Setting up device label at $DEVICE_LABEL_FILE"
    mkdir -p "$(dirname "$DEVICE_LABEL_FILE")"
    case "$PLATFORM" in
        linux)  echo "${HOSTNAME}-fedora"  > "$DEVICE_LABEL_FILE" ;;
        macos)  echo "${HOSTNAME}-macos"   > "$DEVICE_LABEL_FILE" ;;
        windows) echo "${HOSTNAME}-windows" > "$DEVICE_LABEL_FILE" ;;
        *)      echo "${HOSTNAME}-${PLATFORM}" > "$DEVICE_LABEL_FILE" ;;
    esac
fi

if [ -f "$DEVICE_LABEL_FILE" ]; then
    DEVICE_ID="${HOSTNAME}-$(cat "$DEVICE_LABEL_FILE")"
else
    DEVICE_ID="${HOSTNAME}-${PLATFORM}"
fi

echo "Platform: $PLATFORM"
echo "Device ID: $DEVICE_ID"
echo ""

# Create directories
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$SKILLS_DIR"
mkdir -p "$(dirname "$DEVICE_LABEL_FILE")"

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

# Create bootstrap reference so project-collab.py can find itself
mkdir -p "$SKILLS_DIR/references"
if [ ! -f "$SKILLS_DIR/references/manifest-template.md" ]; then
    curl -fsSL "$REF_URL" -o "$SKILLS_DIR/references/manifest-template.md"
    echo "  → $SKILLS_DIR/references/manifest-template.md"
fi

echo ""
echo "Checking dependencies..."

# Verify gh CLI
if command -v gh &> /dev/null; then
    echo "  ✓ gh CLI found"
    gh auth status 2>/dev/null || echo "  ⚠ gh not authenticated. Run: gh auth login"
else
    echo "  ✗ gh CLI not found. Install: https://cli.github.com/"
fi

# Check git
if command -v git &> /dev/null; then
    echo "  ✓ git found ($(git --version | awk '{print $3}'))"
else
    echo "  ✗ git not found"
fi

# Check python
if command -v python3 &> /dev/null; then
    echo "  ✓ python3 found"
else
    echo "  ✗ python3 not found"
fi

# Verify agent CLIs
echo ""
echo "Checking agent CLIs (optional — needed for task execution):"
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
echo "  2. Verify device label:         cat $DEVICE_LABEL_FILE"
echo "  3. Initialize in a repo:        cd your-repo && project-collab.py init"
echo "  4. Pull issues:                 project-collab.py pull"
echo "  5. Claim a task:                project-collab.py claim <number>"
echo ""
echo "No install script needed again — just clone any repo with .hermes-collab.md"
echo "and Hermes will auto-detect the protocol and bootstrap everything."
echo ""
echo "For cron automation:"
echo "  hermes cron create \"project sync\" --script project-collab.py --schedule \"every 30 minutes\""
echo ""
echo "Protocol documentation: https://github.com/sambaseness/hermes-collab-protocol"
