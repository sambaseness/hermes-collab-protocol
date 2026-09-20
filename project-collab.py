#!/usr/bin/env python3
"""
Hermes Collab Protocol — Multi-device AI agent collaboration via GitHub.

Reads .hermes-collab.md manifest in a GitHub repo, fetches issues/project/discussions,
divides work between devices, and manages development on the develop branch.

Features:
- Manifest detection and initialization
- GitHub Issues, Project items, and Discussions integration
- Task claiming and assignment between devices
- Develop branch management (never touches main)
- State sharing via .hermes-state.json
- Device metadata in commits (same pattern as vault-sync.py)
- Supports hermes, claude, codex, opencode agents

Usage:
  project-collab.py init          Initialize protocol in current repo
  project-collab.py status        Show team status and assignments
  project-collab.py pull          Pull latest issues and state
  project-collab.py claim <num>   Claim an issue
  project-collab.py work          Start working on claimed tasks
  project-collab.py sync          Push state and PR updates
  project-collab.py report        Generate team progress report
  project-collab.py discussions   List discussion topics
  project-collab.py project       List project board items

Cron usage:
  hermes cron create "project sync" --script project-collab.py --schedule "every 30 minutes"
"""

import subprocess
import sys
import json
import platform
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import re

# --- Configuration ---

SCRIPT_DIR = Path(__file__).parent
VAULT_PATH = Path("/home/sambasene/obsidian/Vault")  # Fallback for device-label

def get_device_id():
    """Get unique identifier for this OS installation (same pattern as vault-sync.py)."""
    hostname = platform.node()
    system = platform.system().lower()

    if system == "linux":
        label_file = Path.home() / ".config" / "device-label"
        if label_file.exists():
            return f"{hostname}-{label_file.read_text().strip()}"
        return f"{hostname}-fedora"
    elif system == "windows":
        label_file = Path.home() / "AppData" / "Local" / "hermes" / "device-label"
        if label_file.exists():
            return f"{hostname}-{label_file.read_text().strip()}"
        return f"{hostname}-windows"
    return f"{hostname}-{system}"

def get_device_label():
    """Get just the device label for display."""
    system = platform.system().lower()
    if system == "linux":
        label_file = Path.home() / ".config" / "device-label"
        if label_file.exists():
            return label_file.read_text().strip()
        return "fedora"
    return "unknown"

def run_git(args, cwd=None, capture=True):
    """Run git command and return result."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or Path.cwd(),
            capture_output=capture, text=True, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def run_gh(args, cwd=None):
    """Run gh CLI command."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            cwd=cwd or Path.cwd(),
            capture_output=True, text=True, timeout=30
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

# --- Manifest ---

def read_manifest(repo_path: Path) -> Optional[dict]:
    """Read .hermes-collab.md manifest file."""
    manifest_path = repo_path / ".hermes-collab.md"
    if not manifest_path.exists():
        return None

    content = manifest_path.read_text()
    manifest = {}

    # Parse YAML frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            frontmatter = content[3:end].strip()
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    manifest[key] = val

    manifest["_raw"] = content
    return manifest

def create_manifest(repo_path: Path) -> bool:
    """Create a .hermes-collab.md from existing repo metadata."""
    repo_path = Path(repo_path)
    device_id = get_device_id()

    # Get repo info from git
    code, remote_url, _ = run_git(["remote", "get-url", "origin"], cwd=repo_path)
    if code != 0:
        print("Error: No git remote found. Initialize git and add origin first.")
        return False

    # Extract owner/repo from GitHub URL
    repo_match = re.search(r'/([^/]+)/([^/.]+)', remote_url)
    if not repo_match:
        print("Error: Could not parse repo from remote URL.")
        return False

    owner, repo_name = repo_match.group(1), repo_match.group(2).replace('.git', '')

    # Get existing issues count via gh
    code, issues_out, _ = run_gh(["issue", "list", "--repo", f"{owner}/{repo_name}", "--limit", "1", "--json", "count"], cwd=repo_path)
    issues_count = 0
    if code == 0:
        try:
            issues_data = json.loads(issues_out)
            issues_count = issues_data.get("count", 0) if isinstance(issues_data, dict) else 0
        except:
            pass

    manifest_content = f"""---
protocol: hermes-collab
version: "1.0"
project-name: {repo_name}
owner: {owner}
team:
  - device-id: {device_id}
    agent: hermes
    role: lead
    capabilities: [all]
default-branch: develop
---

# {repo_name}

## Overview
Auto-generated collaboration manifest for {owner}/{repo_name}.

## Team
- **{device_id}** ({get_device_label()}): Lead agent

## Work Division
- [ ] {issues_count} open issues available for claiming

## Communication
- State file: .hermes-state.json
- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Project: GitHub Projects tab

## Rules
- Never commit to main directly
- All work on develop branch
- Each device pulls issues and claims them
- Update .hermes-state.json with progress
- Feature branches from develop: feature/{{issue-number}}-{{short-desc}}
"""

    manifest_path = repo_path / ".hermes-collab.md"
    manifest_path.write_text(manifest_content)
    print(f"Created {manifest_path}")
    return True

# --- State File ---

def get_state_path(repo_path: Path) -> Path:
    """Path to .hermes-state.json."""
    return repo_path / ".hermes-state.json"

def read_state(repo_path: Path) -> dict:
    """Read .hermes-state.json."""
    state_path = get_state_path(repo_path)
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except:
            pass
    return {"updated_at": None, "issues": [], "devices": {}}

def save_state(repo_path: Path, state: dict) -> bool:
    """Save .hermes-state.json."""
    state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    state_path = get_state_path(repo_path)
    state_path.write_text(json.dumps(state, indent=2))
    return True

# --- GitHub Integration ---

def get_repo_info(repo_path: Path) -> Optional[dict]:
    """Get GitHub repo info."""
    code, remote_url, _ = run_git(["remote", "get-url", "origin"], cwd=repo_path)
    if code != 0:
        return None

    match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote_url)
    if not match:
        return None

    return {"owner": match.group(1), "repo": match.group(2).replace('.git', '')}

def fetch_issues(repo_path: Path) -> list:
    """Fetch open issues from GitHub."""
    repo_info = get_repo_info(repo_path)
    if not repo_info:
        return []

    code, out, _ = run_gh([
        "issue", "list",
        "--repo", f"{repo_info['owner']}/{repo_info['repo']}",
        "--state", "open",
        "--limit", "50",
        "--json", "number,title,state,labels,assignees,createdAt,body"
    ], cwd=repo_path)

    if code != 0:
        print(f"Warning: Could not fetch issues: {out}")
        return []

    try:
        return json.loads(out) if out else []
    except:
        return []

def fetch_project_items(repo_path: Path) -> list:
    """Fetch project board items via gh CLI."""
    repo_info = get_repo_info(repo_path)
    if not repo_info:
        return []

    # Try to get project items — gh project list requires project number
    code, out, _ = run_gh(["project", "list", "--repo", f"{repo_info['owner']}/{repo_info['repo']}", "--json", "number,title,state"], cwd=repo_path)
    if code != 0:
        return []

    try:
        return json.loads(out) if out else []
    except:
        return []

def fetch_discussions(repo_path: Path) -> list:
    """Fetch discussion topics from GitHub."""
    repo_info = get_repo_info(repo_path)
    if not repo_info:
        return []

    code, out, _ = run_gh(["discussion", "list", "--repo", f"{repo_info['owner']}/{repo_info['repo']}", "--limit", "20", "--json", "number,title,category,author,createdAt"], cwd=repo_path)
    if code != 0:
        return []

    try:
        return json.loads(out) if out else []
    except:
        return []

def claim_issue(repo_path: Path, issue_number: int, device_id: str) -> bool:
    """Claim an issue on GitHub and update state."""
    repo_info = get_repo_info(repo_path)
    if not repo_info:
        return False

    # Add assignee to issue
    code, out, err = run_gh(["issue", "edit", str(issue_number), "--repo", f"{repo_info['owner']}/{repo_info['repo']}", "--add-assignee", device_id], cwd=repo_path)
    if code != 0:
        print(f"Warning: Could not assign issue: {err}")

    # Comment on issue
    comment_msg = f"@{device_id} has claimed this issue via Hermes Collab Protocol."
    run_gh(["issue", "comment", str(issue_number), "--repo", f"{repo_info['owner']}/{repo_info['repo']}", "--body", comment_msg], cwd=repo_path)
    return True

# --- Branch Management ---

def ensure_develop(repo_path: Path) -> bool:
    """Ensure develop branch exists, never touch main."""
    # Check current branch
    code, current_branch, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)

    # Check if develop exists remotely
    code, _, _ = run_git(["branch", "-r", "--list", "origin/develop"], cwd=repo_path)
    develop_exists = code == 0 and "origin/develop" in _

    if not develop_exists:
        # Create develop from main or master
        code, _, _ = run_git(["checkout", "main" if run_git(["branch", "-a"], cwd=repo_path)[1].strip().split("\n")[0].strip().startswith("* main") else "master"], cwd=repo_path)
        if code == 0:
            run_git(["checkout", "-b", "develop"], cwd=repo_path)
            run_git(["push", "-u", "origin", "develop"], cwd=repo_path)
            # Switch back to main
            run_git(["checkout", "main" if run_git(["branch", "-a"], cwd=repo_path)[1].strip().split("\n")[0].strip().startswith("* main") else "master"], cwd=repo_path)
    return True

def create_feature_branch(repo_path: Path, issue_number: int, title: str) -> str:
    """Create a feature branch from develop."""
    short_desc = title.lower().replace(" ", "-")[:30].strip("-")
    branch_name = f"feature/{issue_number}-{short_desc}"

    # Make sure we're on develop first
    run_git(["checkout", "develop"], cwd=repo_path)
    run_git(["pull", "--rebase", "origin", "develop"], cwd=repo_path)

    # Create feature branch
    run_git(["checkout", "-b", branch_name], cwd=repo_path)
    run_git(["push", "-u", "origin", branch_name], cwd=repo_path)

    # Switch back to develop
    run_git(["checkout", "develop"], cwd=repo_path)
    return branch_name

# --- Agent Launcher ---

def launch_agent(agent_type: str, task: str, workdir: Path) -> bool:
    """Launch the appropriate agent for a task."""
    agent_map = {
        "claude": lambda: f"claude -p \"{task}\" --max-turns 10",
        "codex": lambda: f"codex exec \"{task}\"",
        "opencode": lambda: f"opencode run \"{task}\"",
        "hermes": lambda: "hermes",  # Hermes is the orchestrator itself
    }

    if agent_type not in agent_map:
        print(f"Unknown agent type: {agent_type}")
        return False

    print(f"Launching {agent_type} for task: {task[:80]}...")
    return True  # Actual launch would be done by the calling device

# --- Main Commands ---

def cmd_init(repo_path: Path):
    """Initialize the collab protocol in the current repo."""
    manifest = read_manifest(repo_path)

    if manifest:
        print(f"Protocol already initialized in {repo_path}")
        print(f"Project: {manifest.get('project-name', 'unknown')}")
        print(f"Team: {len(manifest.get('team', []))} members")
        # Offer to update
        create_manifest(repo_path)
        print("Updated manifest with current repo info.")
    else:
        if create_manifest(repo_path):
            print("Protocol initialized successfully!")
            print("Other devices running 'project-collab.py pull' will detect this manifest.")

    # Ensure develop branch
    ensure_develop(repo_path)

    # Create .hermes-state.json if it doesn't exist
    state = read_state(repo_path)
    if not state["updated_at"]:
        state["devices"] = {get_device_id(): {"agent": "hermes", "current_task": None, "completed": [], "last_sync": None}}
        save_state(repo_path, state)
        print("Created .hermes-state.json")

def cmd_status(repo_path: Path):
    """Show team status and assignments."""
    manifest = read_manifest(repo_path)
    state = read_state(repo_path)
    device_id = get_device_id()

    if not manifest:
        print("No .hermes-collab.md found. Run 'project-collab.py init' first.")
        return

    print(f"\n{'='*60}")
    print(f"  Hermes Collab Protocol — {manifest.get('project-name', 'unknown')}")
    print(f"{'='*60}")
    print(f"  Protocol: {manifest.get('protocol')} v{manifest.get('version')}")
    print(f"  Default branch: {manifest.get('default-branch', 'develop')}")
    print(f"  Your device: {device_id}")
    print(f"  Team size: {len(manifest.get('team', []))}")
    print(f"\n  Team Members:")
    for member in manifest.get('team', []):
        marker = " ← YOU" if member.get('device-id') == device_id else ""
        print(f"    - {member.get('device-id')} ({member.get('agent', '?')}): {member.get('role', '?')}{marker}")

    print(f"\n  Issues ({len(state.get('issues', []))} tracked):")
    for issue in state.get('issues', []):
        status_icon = {"unclaimed": "○", "claimed": "◐", "in_progress": "◑", "done": "●"}.get(issue.get('status'), "?")
        assigned = issue.get('assigned_to', 'unassigned')
        print(f"    {status_icon} #{issue['number']}: {issue['title'][:50]} → {assigned}")

    print(f"\n  Last sync: {state.get('updated_at', 'never')}")
    print(f"{'='*60}\n")

def cmd_pull(repo_path: Path):
    """Pull latest issues, state, and reassign tasks."""
    device_id = get_device_id()
    manifest = read_manifest(repo_path)

    if not manifest:
        print("No .hermes-collab.md found. Run 'project-collab.py init' first.")
        return

    # Fetch latest issues
    issues = fetch_issues(repo_path)
    discussions = fetch_discussions(repo_path)
    project_items = fetch_project_items(repo_path)

    # Read existing state
    state = read_state(repo_path)

    # Update issues in state
    existing_numbers = {str(i.get('number')) for i in state.get('issues', [])}
    for issue in issues:
        num = str(issue.get('number', ''))
        if num not in existing_numbers:
            state.setdefault('issues', []).append({
                "number": issue.get('number'),
                "title": issue.get('title', ''),
                "status": "unclaimed",
                "assigned_to": None,
                "agent": None,
                "branch": None,
                "labels": issue.get('labels', []),
                "claimed_at": None,
                "completed_at": None
            })

    # Update discussions
    state['discussions'] = discussions
    state['project_items'] = project_items

    # Save state
    save_state(repo_path, state)

    # Pull latest from remote
    run_git(["checkout", "develop"], cwd=repo_path)
    run_git(["pull", "--rebase", "origin", "develop"], cwd=repo_path)

    # Pull .hermes-state.json from remote
    run_git(["pull"], cwd=repo_path)

    print(f"Pulled {len(issues)} issues, {len(discussions)} discussions, {len(project_items)} project items.")
    print(f"Device {device_id} sync complete.")

def cmd_claim(repo_path: Path, issue_number: int):
    """Claim an issue for this device."""
    device_id = get_device_id()
    state = read_state(repo_path)
    manifest = read_manifest(repo_path)

    if not manifest:
        print("No manifest found.")
        return

    # Find the issue
    issue = None
    for i in state.get('issues', []):
        if i.get('number') == issue_number:
            issue = i
            break

    if not issue:
        print(f"Issue #{issue_number} not found in state. Run 'project-collab.py pull' first.")
        return

    if issue.get('status') != 'unclaimed':
        print(f"Issue #{issue_number} is already {issue.get('status')} (assigned to {issue.get('assigned_to')}).")
        return

    # Claim it
    issue['status'] = 'claimed'
    issue['assigned_to'] = device_id
    issue['agent'] = manifest['team'][0].get('agent', 'hermes') if manifest.get('team') else 'hermes'
    issue['claimed_at'] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Create feature branch
    branch_name = create_feature_branch(repo_path, issue_number, issue.get('title', ''))
    issue['branch'] = branch_name

    # Update device state
    state['devices'].setdefault(device_id, {"current_task": None, "completed": [], "last_sync": None})
    state['devices'][device_id]['current_task'] = issue_number

    # Claim on GitHub
    claim_issue(repo_path, issue_number, device_id)

    # Save state
    save_state(repo_path, state)

    # Commit state update
    run_git(["add", ".hermes-state.json"], cwd=repo_path)
    run_git(["commit", "-m", f"collab: claim issue #{issue_number}\ndevice: {device_id}"], cwd=repo_path)
    run_git(["push", "origin", "develop"], cwd=repo_path)

    print(f"Claimed issue #{issue_number}: {issue['title'][:60]}")
    print(f"  Branch: {branch_name}")
    print(f"  Assigned to: {device_id}")
    print(f"  Run 'project-collab.py work' to start.")

def cmd_work(repo_path: Path):
    """Start working on claimed tasks."""
    device_id = get_device_id()
    state = read_state(repo_path)
    manifest = read_manifest(repo_path)

    device_info = state.get('devices', {}).get(device_id, {})
    current_task = device_info.get('current_task')

    if not current_task:
        # Find any claimed task
        for issue in state.get('issues', []):
            if issue.get('assigned_to') == device_id and issue.get('status') == 'claimed':
                current_task = issue['number']
                break

    if not current_task:
        print("No claimed tasks. Use 'project-collab.py claim <number>' first.")
        return

    # Find the issue
    issue = None
    for i in state.get('issues', []):
        if i.get('number') == current_task:
            issue = i
            break

    if not issue:
        print(f"Task #{current_task} not found.")
        return

    agent_type = issue.get('agent', 'hermes')
    task_desc = f"Implement: {issue['title']}\n\nDescription: {issue.get('body', issue.get('description', ''))}\n\nLabels: {', '.join(issue.get('labels', []))}"

    print(f"Starting {agent_type} for issue #{current_task}...")
    print(f"  Branch: {issue.get('branch')}")
    print(f"  Task: {issue['title']}")

    # Check for agent CLI availability
    agent_agents = {
        "claude": lambda: terminal("claude --version 2>/dev/null"),
        "codex": lambda: terminal("codex --version 2>/dev/null"),
        "opencode": lambda: terminal("opencode --version 2>/dev/null"),
    }

    if agent_type in agent_agents:
        code, version, _ = agent_agents[agent_type]()
        if code != 0:
            print(f"Warning: {agent_type} not installed or not in PATH.")
            print(f"  Install it first, then run: cd {repo_path} && git checkout {issue['branch']}")
            return

    # Mark as in progress
    issue['status'] = 'in_progress'
    issue['started_at'] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    save_state(repo_path, state)

    # Update device
    state['devices'][device_id]['current_task'] = current_task
    save_state(repo_path, state)

    print(f"Ready to work. Switch to branch {issue['branch']} and run your agent.")

def cmd_sync(repo_path: Path):
    """Sync state and push PR updates."""
    device_id = get_device_id()
    state = read_state(repo_path)

    # Pull latest state
    run_git(["checkout", "develop"], cwd=repo_path)
    run_git(["pull", "--rebase", "origin", "develop"], cwd=repo_path)

    # Push current state
    run_git(["add", ".hermes-state.json"], cwd=repo_path)

    # Check if there are changes to commit
    code, status, _ = run_git(["status", "--porcelain"], cwd=repo_path)
    if status.strip():
        run_git(["commit", "-m", f"collab: sync state\ndevice: {device_id}"], cwd=repo_path)
        run_git(["push", "origin", "develop"], cwd=repo_path)
        print("State synced to remote.")
    else:
        print("No state changes to sync.")

    # For each completed task, ensure PR exists
    for issue in state.get('issues', []):
        if issue.get('status') == 'done' and issue.get('branch') and not issue.get('pr_created'):
            repo_info = get_repo_info(repo_path)
            if repo_info:
                pr_code, _, _ = run_gh([
                    "pr", "create",
                    "--repo", f"{repo_info['owner']}/{repo_info['repo']}",
                    "--head", issue['branch'],
                    "--base", "develop",
                    "--title", f"Complete issue #{issue['number']}: {issue['title'][:60]}",
                    "--body", f"Completed by {device_id}\n\nDevice: {device_id}\nIssue: #{issue['number']}"
                ], cwd=repo_path)
                if pr_code == 0:
                    issue['pr_created'] = True
                    save_state(repo_path, state)
                    print(f"Created PR for issue #{issue['number']}")

def cmd_report(repo_path: Path):
    """Generate team progress report."""
    state = read_state(repo_path)
    manifest = read_manifest(repo_path)

    if not manifest:
        print("No manifest found.")
        return

    print(f"\n{'='*60}")
    print(f"  Team Progress Report — {manifest.get('project-name', 'unknown')}")
    print(f"  Updated: {state.get('updated_at', 'never')}")
    print(f"{'='*60}")

    total = len(state.get('issues', []))
    done = sum(1 for i in state.get('issues', []) if i.get('status') == 'done')
    in_progress = sum(1 for i in state.get('issues', []) if i.get('status') == 'in_progress')
    claimed = sum(1 for i in state.get('issues', []) if i.get('status') == 'claimed')
    unclaimed = sum(1 for i in state.get('issues', []) if i.get('status') == 'unclaimed')

    print(f"\n  Progress: {done}/{total} done, {in_progress} in progress, {claimed} claimed, {unclaimed} unclaimed")
    print(f"\n  Device Status:")
    for dev_id, dev_info in state.get('devices', {}).items():
        current = dev_info.get('current_task', 'none')
        completed = len(dev_info.get('completed', []))
        print(f"    - {dev_id}: task={current}, completed={completed}")

    print(f"\n  Discussions: {len(state.get('discussions', []))}")
    print(f"  Project Items: {len(state.get('project_items', []))}")
    print(f"{'='*60}\n")

def cmd_discussions(repo_path: Path):
    """List discussion topics."""
    discussions = fetch_discussions(repo_path)
    print(f"\nDiscussions ({len(discussions)}):")
    for d in discussions:
        print(f"  #{d.get('number')}: {d.get('title')} — {d.get('category', '')} by {d.get('author', {}).get('login', 'unknown')}")
    print()

def cmd_project(repo_path: Path):
    """List project board items."""
    items = fetch_project_items(repo_path)
    print(f"\nProject Board ({len(items)} items):")
    for item in items:
        status = item.get('fieldByNameByName', {}).get('name', 'unknown')
        print(f"  #{item.get('number')}: {item.get('title')} [{status}]")
    print()

# --- Main ---

def main():
    if len(sys.argv) < 2:
        print("Usage: project-collab.py [command] [args]")
        print("Commands: init, status, pull, claim <num>, work, sync, report, discussions, project")
        sys.exit(1)

    repo_path = Path.cwd()
    cmd = sys.argv[1]

    # Find repo root
    while repo_path != repo_path.parent:
        if (repo_path / ".git").exists():
            break
        repo_path = repo_path.parent
    else:
        print("Error: Not in a git repository.")
        sys.exit(1)

    if cmd == "init":
        cmd_init(repo_path)
    elif cmd == "status":
        cmd_status(repo_path)
    elif cmd == "pull":
        cmd_pull(repo_path)
    elif cmd == "claim":
        if len(sys.argv) < 3:
            print("Usage: project-collab.py claim <issue-number>")
            sys.exit(1)
        cmd_claim(repo_path, int(sys.argv[2]))
    elif cmd == "work":
        cmd_work(repo_path)
    elif cmd == "sync":
        cmd_sync(repo_path)
    elif cmd == "report":
        cmd_report(repo_path)
    elif cmd == "discussions":
        cmd_discussions(repo_path)
    elif cmd == "project":
        cmd_project(repo_path)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
