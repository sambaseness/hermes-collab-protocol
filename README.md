# Hermes Collab Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Public](https://img.shields.io/badge/Visibility-Public-brightgreen)](https://github.com/sambaseness/hermes-collab-protocol)
[![CI/CD](https://github.com/sambaseness/hermes-collab-protocol/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/sambaseness/hermes-collab-protocol/actions/workflows/ci-cd.yml)

Multi-device AI agent collaboration protocol. When any GitHub repo contains a `.hermes-collab.md` manifest file, Hermes agents running on different devices automatically divide work, communicate, and coordinate — on `develop`, never on `main`.

---

## What It Is

Hermes Collab Protocol is a collaboration framework for multi-device AI agent workflows. It enables teams to use Hermes, OpenCode, Codex, and other agents to work together on GitHub projects with structured task management, automatic work division, and transparent communication.

**Key concepts:**
- One manifest file (`.hermes-collab.md`) defines your team and workflow
- Devices automatically detect the protocol when cloning a repo
- Work happens on `develop` branch — `main` is never touched
- Agents claim tasks, work on feature branches, and create PRs
- Communication through GitHub Issues, Discussions, Projects, and shared state

**Supported agents:** Hermes (orchestrator), OpenCode (primary), Codex (parallel), and any agent with CLI access.

---

## How It Works

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
- Each device runs its agent (hermes, opencode, codex) on the claimed task
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

---

## Quick Start

### First-time setup (one-time):
```bash
curl -fsSL https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/installer.py | python3
```

### On any device that already has Hermes with the skill:
```bash
cd your-repo && project-collab.py init
project-collab.py pull
project-collab.py claim <number>
project-collab.py work
```

---

## Claiming & Assignment

The claiming flow:
1. **Pull**: `project-collab.py pull` — fetch latest issues
2. **View**: `project-collab.py status` — see who has what
3. **Claim**: `project-collab.py claim <number>` — claim an unassigned issue
4. **Work**: `project-collab.py work` — start working on claimed tasks
5. **Sync**: `project-collab.py sync` — push state, create PRs

Only one device can claim an issue at a time. Unclaimed issues are available for any device.

---

## Commands

```bash
project-collab.py init          # Initialize protocol in current repo
project-collab.py status        # Show team status and assignments
project-collab.py pull          # Fetch latest issues and state
project-collab.py claim <num>   # Claim an issue
project-collab.py work          # Start working on claimed tasks
project-collab.py sync          # Push state and PR updates
project-collab.py report        # Generate team progress report
project-collab.py bootstrap     # Download project-collab.py from GitHub
project-collab.py discussions   # List discussion topics
project-collab.py project       # List project board items
```

---

## Branch Policy

- **`main`**: Never committed to directly. Protected branch.
- **`develop`**: Integration branch. All devices push here.
- **`feature/*`**: Individual task branches branched from `develop`.
- Each PR must be reviewed by at least one other device before merging to `develop`.

---

## Agent Support

|| Agent | Best For | When to Use |
|-------|----------|-------------|
| Hermes | Orchestration, full-stack coordination | Lead tasks, complex coordination |
| OpenCode | Lightweight coding tasks | PR checks, tests, quick fixes |
| Codex | Parallel issue fixing | Batch fixes, worktrees |

---

## Key Features

- **Self-bootstrapping**: `.hermes-collab.md` + skill auto-downloads `project-collab.py`
- **Develop-only policy**: Never commit to `main`, all work on `develop`
- **Device identification**: Auto-detects via hostname + `~/.config/device-label`
- **GitHub integration**: Issues, Discussions, Projects, PRs via `gh` CLI
- **Multi-agent**: Supports hermes, opencode, codex
- **Cron-ready**: Automatic sync every 30 minutes

---

## Requirements

- `gh` CLI authenticated with GitHub
- `git` configured
- Python 3.8+
- Agent CLI (`hermes`, `opencode`, `codex`) for task execution

---

## Protocol Files

| File | Location | Description |
|------|----------|-------------|
| `.hermes-collab.md` | Repo root | Team manifest and rules |
| `.hermes-state.json` | Repo root | Shared state (git-tracked) |
| `project-collab.py` | `~/.hermes/scripts/` | Orchestration script |
| `SKILL.md` | `~/.hermes/skills/hermes-collab/` | Skill definition |
| `reference-manifest.md` | Protocol repo | `.hermes-collab.md` template |
| `installer.py` | Protocol repo | Cross-platform Python installer |
| `install.sh` | Protocol repo | Legacy curl|bash installer |

---

## CI/CD Pipeline

Every push to `main` triggers automated builds via GitHub Actions:

| Job | Runner | Output |
|-----|--------|--------|
| **Validate** | `ubuntu-latest` | Syntax, lint, website check |
| **Build Linux binary** | `ubuntu-latest` | `hermes-collab-installer` |
| **Build Mac binary** | `macos-latest` | `hermes-collab-installer` |
| **Build Windows .exe** | `windows-latest` | `hermes-collab-installer.exe` |
| **Release** | — | GitHub Release on tag push |
| **Notify** | — | Pipeline summary |

Binaries are uploaded as artifacts on every push. Releases are created automatically when pushing a tag.

---

## Downloads

| Platform | Format | Link |
|----------|--------|------|
| Windows | `.exe` | [Download](https://github.com/sambaseness/hermes-collab-protocol/releases/tag/v1.0.0) |
| Linux | Binary | [Download](https://github.com/sambaseness/hermes-collab-protocol/releases/tag/v1.0.0) |
| macOS | Binary | [Download](https://github.com/sambaseness/hermes-collab-protocol/releases/tag/v1.0.0) |
| Universal | `.py` | [installer.py](https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/installer.py) |

---

## Example: Bitiko

The [bitiko](https://github.com/biramth/bitiko) project uses this protocol:
- **Team**: sambaseness (hermes co-author), biramth (opencode author)
- **Branch**: `develop` with `feature/*` branches
- **Workflow**: `claim` → `work` → `sync` → PR to `develop`

---

## License

MIT — see [LICENSE](LICENSE)
