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

## How It Works

1. **Manifest** — Place `.hermes-collab.md` at any repo root to activate collaboration
2. **Detect** — `project-collab.py` reads the manifest and identifies team members
3. **Assign** — Devices pull issues from GitHub and claim unassigned tasks
4. **Execute** — Each device runs its agent (hermes, claude, codex, opencode) on claimed work
5. **Sync** — State is shared via `.hermes-state.json` (git-tracked) and GitHub Issues/PRs

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
```

## Key Features

- **Self-bootstrapping**: `.hermes-collab.md` + skill auto-downloads `project-collab.py`
- **Develop-only policy**: Never commit to `main`, all work happens on `develop`
- **Device identification**: Auto-detects via hostname + `~/.config/device-label`
- **GitHub integration**: Issues, Discussions, Projects, PRs all via `gh` CLI
- **Multi-agent**: Supports hermes, claude, codex, opencode
- **Cron-ready**: Set up automatic sync every 30 minutes

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

## License

MIT — see [LICENSE](LICENSE)
