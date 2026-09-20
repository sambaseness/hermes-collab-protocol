---
name: hermes-collab
description: "Multi-device AI agent collaboration protocol. Detects .hermes-collab.md manifest in any GitHub repo and orchestrates team-based AI agent work across devices via Hermes."
version: 1.0.0
author: Sambasene
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Collaboration, Multi-Device, Team, Protocol, GitHub]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# Hermes Collab Protocol

Multi-device AI agent collaboration protocol. When a GitHub repo contains a `.hermes-collab.md` manifest file, this skill activates and coordinates distributed Hermes agents across devices.

## Detection

A repo is a collaboration target when:
1. It contains a `.hermes-collab.md` file at its root
2. The file contains a valid `protocol: hermes-collab` declaration

Detection is triggered automatically when:
- Cloning/fetching any GitHub repo
- `hermes collab init` is run in a repo directory
- The skill is loaded and `project-collab.py` detects the manifest

## Manifest File: `.hermes-collab.md`

Located at the repo root. Format:

```markdown
---
protocol: hermes-collab
version: "1.0"
project-name: string
team:
  - device-id: string
    agent: hermes|claude|codex|opencode
    role: string
    capabilities: [string]
default-branch: develop
---

# Project Name

## Overview
Project description.

## Work Division
- [ ] Area → device-id or agent-type

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
```

## References

- **Manifest template**: `references/manifest-template.md` — full `.hermes-collab.md` format spec with YAML frontmatter, team schema, and state file schema
- **Orchestration script**: `~/.hermes/scripts/project-collab.py` — all commands (init, status, pull, claim, work, sync, report)

## How It Works

### Phase 1: Initiation
When any device detects `.hermes-collab.md`:
1. Reads the manifest to identify team members and roles
2. Creates/ensures `develop` branch exists (never touches `main`)
3. Creates `.hermes-state.json` if it doesn't exist
4. Fetches open issues, project items, and discussions from GitHub
5. Prints the task board to all devices

### Phase 2: Task Assignment
Each device:
1. Reads `.hermes-state.json` for current assignments
2. Picks unclaimed issues matching its capabilities
3. Claims the issue by writing to `.hermes-state.json` and commenting on the GitHub issue
4. Creates a feature branch from `develop`: `feature/{issue-number}-{short-desc}`

### Phase 3: Work Execution
- Each device runs its agent (hermes, claude, codex, opencode) on the claimed task
- Commits to feature branch with device metadata
- Pushes feature branch to origin
- Creates PR from feature branch to `develop`
- Updates `.hermes-state.json` with completion status

### Phase 4: Communication
Devices communicate through:
- `.hermes-state.json` — shared state file (git-tracked)
- GitHub Issues — task tracking and comments
- GitHub Discussions — coordination and questions
- GitHub Projects — visual task board
- Commit messages — include `device:` metadata like `vault-sync.py` pattern

## Scripts

### `project-collab.py`
Located at `~/.hermes/scripts/project-collab.py`. Commands:
- `project-collab.py init` — Initialize protocol in current repo
- `project-collab.py status` — Show team status and assignments
- `project-collab.py pull` — Pull latest issues/state, reassign if needed
- `project-collab.py claim <issue-number>` — Claim an issue
- `project-collab.py work` — Start working on claimed tasks
- `project-collab.py sync` — Push state and PR updates
- `project-collab.py report` — Generate team progress report

### Cron Integration
Similar to `vault-sync.py`, set up via:
```
hermes cron create "project sync" --script project-collab.py --schedule "every 30 minutes"
```

## Branch Policy

- **`main`**: Never commit directly. Protected branch.
- **`develop`**: All integration happens here. Every device pushes to this.
- **`feature/*`**: Individual task branches branched from `develop`.
- Each PR must be reviewed by at least one other device before merging to `develop`.

## Device Identification

Same mechanism as `vault-sync.py`:
- Linux: `{hostname}-{device-label}` from `~/.config/device-label`
- Windows: `{hostname}-{device-label}` from `AppData\Local\hermes\device-label`
- Each device reads its label and registers in the manifest

## State File: `.hermes-state.json`

Git-tracked JSON structure:
```json
{
  "updated_at": "ISO timestamp",
  "issues": [
    {
      "number": 1,
      "title": "Issue title",
      "status": "unclaimed|claimed|in_progress|done",
      "assigned_to": "device-id",
      "agent": "claude|codex|opencode|hermes",
      "branch": "feature/1-short-desc",
      "claimed_at": "ISO timestamp",
      "completed_at": "ISO timestamp"
    }
  ],
  "devices": {
    "fedora-laptop": {
      "agent": "hermes",
      "current_task": null,
      "completed": [],
      "last_sync": "ISO timestamp"
    }
  }
}
```

## Integration with Existing Tools

- Uses `gh` CLI for GitHub API interactions (issues, discussions, projects)
- Uses `git` for branch management (same patterns as `vault-sync.py`)
- Uses `platform.node()` and `device-label` for device identification (same as `vault-sync.py`)
- Commits include `device:` metadata in commit messages (same pattern)
- Can trigger `claude`, `codex`, or `opencode` agents for actual work

## Setup

To enable collaboration on a repo:
1. Place `.hermes-collab.md` at repo root
2. Push to GitHub
3. On each device, run `project-collab.py init`
4. Devices automatically detect the manifest and begin collaborating

For existing repos:
1. Run `project-collab.py init` in the repo directory on any device
2. This creates the manifest from repo metadata (issues, team members from GitHub)
3. Other devices running `project-collab.py` will detect it on next pull

See `references/manifest-template.md` for the complete manifest format specification.
