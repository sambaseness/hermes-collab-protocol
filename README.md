# Hermes Collab Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Public](https://img.shields.io/badge/Visibility-Public-brightgreen)](https://github.com/sambaseness/hermes-collab-protocol)

Multi-device AI agent collaboration protocol. When any GitHub repo contains a `.hermes-collab.md` manifest file, Hermes agents running on different devices automatically divide work, communicate, and coordinate.

## No Install Script Required

After the first-time setup, **`.hermes-collab.md` alone is enough**. When Hermes clones a repo with this manifest:

1. The `hermes-collab` skill detects `.hermes-collab.md`
2. Skill activates the collaboration protocol
3. `project-collab.py` is automatically bootstrapped from this repo
4. Device is ready — `claim`, `work`, `sync`

The `install.sh` is only needed for the very first device that hasn't cached the skill yet.

## Quick Start

```bash
# First time (one-time setup)
curl -fsSL https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/install.sh | bash

# Or on any device that already has Hermes with the skill:
cd your-repo && project-collab.py init
project-collab.py pull
project-collab.py claim <number>
project-collab.py work
```

## How It Works — Full Workflow

### Phase 1: Initiation
When any device clones a repo with `.hermes-collab.md`:
- `project-collab.py init` reads the manifest to identify team members and roles
- Creates/ensures `develop` branch exists (never touches `main`)
- Creates `.hermes-state.json` if it doesn't exist
- Fetches open issues, project items, and discussions from GitHub

### Phase 2: Task Assignment
Each device:
- Reads `.hermes-state.json` for current assignments
- Picks unclaimed issues matching its capabilities
- Claims the issue by updating `.hermes-state.json` and commenting on the GitHub issue
- Creates a feature branch from `develop`: `feature/{issue-number}-{short-desc}`

### Phase 3: Work Execution
- Each device runs its agent (hermes, claude, codex, opencode) on the claimed task
- Commits to feature branch with device metadata
- Pushes feature branch to origin
- Creates PR from feature branch to `develop`
- Updates `.hermes-state.json` with completion status

### Phase 4: Communication
Devices communicate through:
- **`.hermes-state.json`** — shared state file (git-tracked)
- **GitHub Issues** — task tracking and comments
- **GitHub Discussions** — coordination and questions
- **GitHub Projects** — visual task board
- **Commit messages** — include `device:` metadata

### Status & Reporting
```bash
project-collab.py status        # Show team status and assignments
project-collab.py report        # Generate team progress report
project-collab.py pull          # Pull latest issues and reassign
project-collab.py sync          # Push state and PR updates
```

### Cron Automation
```bash
hermes cron create "project sync" --script project-collab.py --schedule "every 30 minutes"
```

## Commands

```bash
project-collab.py init          # Initialize protocol in current repo
project-collab.py status        # Show team status and assignments
project-collab.py pull          # Fetch latest issues and state
project-collab.py claim <num>   # Claim an issue
project-collab.py work          # Start working on claimed tasks
project-collab.py sync          # Push state and PR updates
project-collab.py report        # Generate team progress report
project-collab.py bootstrap     # Download project-collab.py
project-collab.py discussions   # List discussion topics
project-collab.py project       # List project board items
```

## Branch Policy

- **`main`**: Never committed to directly. Protected branch.
- **`develop`**: Integration branch. All devices push here.
- **`feature/*`**: Individual task branches branched from `develop`.
- Each PR must be reviewed by at least one other device before merging to `develop`.

## Agent Support

| Agent | Best For | When to Use |
|-------|----------|-------------|
| Hermes | Orchestration, full-stack coordination | Lead tasks, complex coordination |
| Claude Code | Complex multi-step reasoning | Architecture, security code |
| OpenCode | Lightweight coding tasks | PR checks, tests, quick fixes |
| Codex | Parallel issue fixing | Batch fixes, worktrees |

## Key Features

- **Self-bootstrapping**: `.hermes-collab.md` + skill auto-downloads `project-collab.py`
- **Develop-only policy**: Never commit to `main`, all work on `develop`
- **Device identification**: Auto-detects via hostname + `~/.config/device-label`
- **GitHub integration**: Issues, Discussions, Projects, PRs via `gh` CLI
- **Multi-agent**: Supports hermes, claude, codex, opencode
- **Cron-ready**: Automatic sync every 30 minutes

## Requirements

- `gh` CLI authenticated with GitHub
- `git` configured
- Python 3.8+
- Agent CLI (`hermes`, `claude`, `codex`, or `opencode`) for task execution

## Protocol Files

| File | Location | Description |
|------|----------|-------------|
| `.hermes-collab.md` | Repo root | Team manifest and rules |
| `.hermes-state.json` | Repo root | Shared state (git-tracked) |
| `project-collab.py` | `~/.hermes/scripts/` | Orchestration script |
| `SKILL.md` | `~/.hermes/skills/hermes-collab/` | Skill definition |
| `reference-manifest.md` | Protocol repo | `.hermes-collab.md` template |
| `install.sh` | Protocol repo | One-command device setup |

## Example: Bitiko

The [bitiko](https://github.com/biramth/bitiko) project uses this protocol:
- **Team**: sambaseness (hermes lead), biramth (claude contributor)
- **Branch**: `develop` with `feature/*` branches
- **Workflow**: `claim` → `work` → `sync` → PR to `develop`

## License

MIT — see [LICENSE](LICENSE)
