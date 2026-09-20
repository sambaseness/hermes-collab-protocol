#!/usr/bin/env python3
"""Hermes Collab Protocol Installer — cross-platform version of install.sh."""
import os
import sys
import platform
import subprocess
import urllib.request
import pathlib
import shutil
import getpass

PROTOCOL_REPO = "sambaseness/hermes-collab-protocol"
BASE_URL = f"https://raw.githubusercontent.com/{PROTOCOL_REPO}/main"

SCRIPTS_DIR = pathlib.Path.home() / ".hermes" / "scripts"
SKILLS_DIR = pathlib.Path.home() / ".hermes" / "skills" / "hermes-collab"
REFERENCES_DIR = SKILLS_DIR / "references"

def detect_platform():
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    return "unknown"

def get_device_label_file():
    plat = detect_platform()
    if plat == "windows":
        local = os.environ.get("LOCALAPPDATA", "")
        return pathlib.Path(local) / "hermes" / "device-label"
    else:
        return pathlib.Path.home() / ".config" / "device-label"

def get_hostname():
    try:
        return platform.node() or "unknown"
    except:
        return "unknown"

def set_device_label():
    label_file = get_device_label_file()
    if label_file.exists():
        return label_file.read_text().strip()
    label_file.parent.mkdir(parents=True, exist_ok=True)
    plat = detect_platform()
    hostname = get_hostname()
    label = f"{hostname}-{plat}"
    label_file.write_text(label)
    return label

def download_file(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    return dest

def check_command(cmd):
    try:
        result = subprocess.run(["which" if sys.platform != "win32" else "where", cmd],
                               capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_hermes():
    try:
        result = subprocess.run(["hermes", "--version"], capture_output=True, text=True, timeout=5)
        return True, result.stdout.strip() or "installed"
    except:
        return False, None

def main():
    print("=== Hermes Collab Protocol Installer ===")
    print()

    plat = detect_platform()
    hostname = get_hostname()
    label = set_device_label()
    device_id = f"{hostname}-{label}"

    print(f"Platform: {plat}")
    print(f"Device ID: {device_id}")
    print()

    # Create directories
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    get_device_label_file().parent.mkdir(parents=True, exist_ok=True)

    # Download project-collab.py
    print("Downloading project-collab.py...")
    download_file(f"{BASE_URL}/project-collab.py", SCRIPTS_DIR / "project-collab.py")
    os.chmod(SCRIPTS_DIR / "project-collab.py", 0o755)
    print(f"  → {SCRIPTS_DIR / 'project-collab.py'}")

    # Download SKILL.md
    print("Downloading SKILL.md...")
    download_file(f"{BASE_URL}/SKILL.md", SKILLS_DIR / "SKILL.md")
    print(f"  → {SKILLS_DIR / 'SKILL.md'}")

    # Download reference-manifest.md
    print("Downloading reference-manifest.md...")
    download_file(f"{BASE_URL}/reference-manifest.md", SKILLS_DIR / "reference-manifest.md")
    print(f"  → {SKILLS_DIR / 'reference-manifest.md'}")

    # Create bootstrap reference
    template = REFERENCES_DIR / "manifest-template.md"
    if not template.exists():
        download_file(f"{BASE_URL}/reference-manifest.md", template)
        print(f"  → {template}")

    # Check dependencies
    print()
    print("Checking dependencies...")
    for cmd, name in [("gh", "gh CLI"), ("git", "git"), ("python3", "python3")]:
        if check_command(cmd):
            print(f"  ✓ {name} found")
        else:
            print(f"  ✗ {name} not found")

    # Check agents
    print()
    print("Checking agent CLIs (optional):")
    for agent in ["hermes", "opencode", "codex"]:
        if check_command(agent):
            print(f"  ✓ {agent} found")
        else:
            print(f"  ○ {agent} not found (optional)")

    # Check Hermes
    hermes_ok, hermes_ver = check_hermes()
    if hermes_ok:
        print(f"  ✓ Hermes found ({hermes_ver})")
    else:
        print("  ○ Hermes not found.")
        print("    Install: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash")
        answer = input("    Install Hermes now? (y/N) ").strip().lower()
        if answer == "y":
            subprocess.run(["bash", "-c", "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"])
            print("  ✓ Hermes installed")

    print()
    print("=== Installation Complete ===")
    print()
    print("Next steps:")
    print(f"  1. Authenticate gh if needed:  gh auth login")
    print(f"  2. Verify device label:         cat {get_device_label_file()}")
    print(f"  3. Initialize in a repo:        cd your-repo && python3 {SCRIPTS_DIR / 'project-collab.py'} init")
    print(f"  4. Pull issues:                 python3 {SCRIPTS_DIR / 'project-collab.py'} pull")
    print(f"  5. Claim a task:                python3 {SCRIPTS_DIR / 'project-collab.py'} claim <number>")
    print()
    print("No install script needed again — just clone any repo with .hermes-collab.md")
    print("and Hermes will auto-detect the protocol and bootstrap everything.")
    print()
    print("Protocol documentation: https://github.com/sambaseness/hermes-collab-protocol")

if __name__ == "__main__":
    main()
