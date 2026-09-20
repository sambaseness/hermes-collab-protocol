# Hermes Collab Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Multi-device AI agent collaboration protocol. When any GitHub repo contains a `.hermes-collab.md` manifest file, Hermes agents running on different devices automatically divide work, communicate, and coordinate.

## Quick Start

```bash
# On each device, run the installer
curl -fsSL https://raw.githubusercontent.com/sambaseness/hermes-collab-protocol/main/install.sh | bash

# Or clone and run manually
git clone https://github.com/sambaseness/hermes-collab-protocol.git
cd hermes-collab-protocol
./install.sh
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
```

## Key Features

- **Develop-only policy**: Never commit to `main`, all work happens on `develop`
- **Device identification**: Auto-detects via hostname + `~/.config/device-label`
- **GitHub integration**: Issues, Discussions, Projects, PRs all via `gh` CLI
- **Multi-agent**: Supports hermes, claude, codex, opencode
- **Cron-ready**: Set up automatic sync every 30 minutes

## Requirements

- `gh` CLI authenticated with GitHub
- `git` configured
- Agent CLI (`hermes`, `claude`, `codex`, or `opencode`) for task execution
- Python 3.8+

## Protocol Files

| File | Location | Description |
|------|----------|-------------|
| `.hermes-collab.md` | Repo root | Team manifest and rules |
| `.hermes-state.json` | Repo root | Shared state (git-tracked) |
| `project-collab.py` | `~/.hermes/scripts/` | Orchestration script |
| `SKILL.md` | `~/.hermes/skills/hermes-collab/` | Skill definition |

## License

MIT — see [LICENSE](LICENSE)
