# Hermes Collab Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Public](https://img.shields.io/badge/Visibility-Public-brightgreen)](https://github.com/sambaseness/hermes-collab-protocol)
[![CI/CD](https://github.com/sambaseness/hermes-collab-protocol/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/sambaseness/hermes-collab-protocol/actions/workflows/ci-cd.yml)

Multi-device AI agent collaboration protocol. When any GitHub repo contains a `.hermes-collab.md` manifest file, Hermes agents running on different devices automatically divide work, communicate, and coordinate.

## No Install Script Required

After the first-time setup, **`.hermes-collab.md` alone is enough**. When Hermes clones a repo with this manifest:

1. The `hermes-collab` skill detects `.hermes-collab.md`
2. Skill activates the collaboration protocol
3. `project-collab.py` is automatically bootstrapped from this repo
4. Device is ready — `claim`, `work`, `sync`

The `installer.py` is only needed for the very first device that hasn't cached the skill yet.

## Quick Start

### First Time (one-time setup)

```bash
# Option 1 — Auto-install (curl | bash)
curl -fsSL https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/installer.py | python3

# Option 2 — Run the .exe (Windows)
# Download hermes-collab-installer.exe from the CI/CD pipeline and double-click it

# Option 3 — Run the binary (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/dist/hermes-collab-installer -o install && chmod +x install && ./install
```

### Or on any device that already has Hermes with the skill:

```bash
cd your-repo && project-collab.py init
project-collab.py pull
project-collab.py claim <number>
project-collab.py work
```

## CI/CD Pipeline

Every push to `main` triggers an automated pipeline via GitHub Actions:

| Job | Description | Output |
|-----|-------------|--------|
| **Validate** | Python syntax, lint, YAML validation | Pass/Fail |
| **Build Windows .exe** | Compiles `installer.py` to `hermes-collab-installer.exe` via PyInstaller | `.exe` artifact |
| **Build Linux binary** | Compiles `installer.py` to `hermes-collab-installer` binary | Binary artifact |
| **Deploy** | Verifies all protocol files are present | Pass/Fail |
| **Release** | Creates GitHub Release on tag push | Release with binaries |
| **Notify** | Pipeline summary | Status |

### The Windows .exe

The CI/CD pipeline builds a standalone Windows `.exe` from `installer.py`:

- **Does not install anything by itself** — it just runs the install logic
- Downloads `project-collab.py`, `SKILL.md`, `reference-manifest.md` to `~/.hermes/`
- Detects platform, creates device-label, checks dependencies
- More user-friendly than a `.sh` script for Windows users

Built automatically by GitHub Actions → available as an artifact on every push to `main`.

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

## Claiming & Assignment

The claiming flow:
1. **Pull**: `project-collab.py pull` — fetch latest issues
2. **View**: `project-collab.py status` — see who has what
3. **Claim**: `project-collab.py claim <number>` — claim an unassigned issue
4. **Work**: `project-collab.py work` — start working on claimed tasks
5. **Sync**: `project-collab.py sync` — push state, create PRs

Only one device can claim an issue at a time. Unclaimed issues are available for any device.

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

## Branch Policy

- **`main`**: Never committed to directly. Protected branch. CI/CD runs here.
- **`develop`**: Integration branch. All devices push here.
- **`feature/*`**: Individual task branches branched from `develop`.
- Each PR must be reviewed by at least one other device before merging to `develop`.

## Agent Support

OpenCode is the primary agent. Hermes orchestrates; OpenCode and Codex execute tasks.

|| Agent | Best For | When to Use |
|-------|----------|-------------|
| Hermes | Orchestration, full-stack coordination | Lead tasks, complex coordination |
| OpenCode | Lightweight coding tasks | PR checks, tests, quick fixes |
| Codex | Parallel issue fixing | Batch fixes, worktrees |

## Key Features

- **Self-bootstrapping**: `.hermes-collab.md` + skill auto-downloads `project-collab.py`
- **Develop-only policy**: Never commit to `main`, all work on `develop`
- **Device identification**: Auto-detects via hostname + `~/.config/device-label`
- **GitHub integration**: Issues, Discussions, Projects, PRs via `gh` CLI
- **Multi-agent**: Supports hermes, opencode, codex
- **Cron-ready**: Automatic sync every 30 minutes
- **CI/CD**: Automated builds and releases via GitHub Actions
- **Cross-platform**: `.exe` for Windows, binary for Linux/macOS

## Requirements

- `gh` CLI authenticated with GitHub
- `git` configured
- Python 3.8+
- Agent CLI (`hermes`, `opencode`, `codex`) for task execution

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
| `.github/workflows/ci-cd.yml` | Protocol repo | CI/CD pipeline (builds .exe) |

## Example: Bitiko

The [bitiko](https://github.com/biramth/bitiko) project uses this protocol:
- **Team**: sambaseness (hermes co-author), biramth (opencode author)
- **Branch**: `develop` with `feature/*` branches
- **Workflow**: `claim` → `work` → `sync` → PR to `develop`

## License

MIT — see [LICENSE](LICENSE)
