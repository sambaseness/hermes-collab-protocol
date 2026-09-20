# .hermes-collab.md — Reference Manifest Template

This is the reference format for the Hermes Collab Protocol manifest file.
Place this at the root of any GitHub repo to enable multi-device AI agent collaboration.

## File Format

YAML frontmatter + Markdown body.

```markdown
---
protocol: hermes-collab
version: "1.0"
project-name: My Project
owner: username
team:
  - device-id: fedora-laptop
    agent: hermes
    role: lead
    capabilities: [all]
default-branch: develop
---

# My Project

## Overview
Brief description of the project.

## Team
- **fedora-laptop** (hermes): Lead agent

## Work Division
- [ ] Backend API → device-id or agent-type
- [ ] Frontend UI → device-id or agent-type

## Communication Channels
- State file: `.hermes-state.json` (git-tracked)
- GitHub Issues: Task tracking and comments
- GitHub Discussions: Coordination and questions
- GitHub Projects: Visual task board

## Rules
- Never commit to `main` directly
- All work happens on `develop` branch
- Each device pulls issues and claims unassigned ones
- Feature branches: `feature/{issue-number}-{short-description}`
- PRs must be reviewed by another device before merging to `develop`
- Update `.hermes-state.json` with progress after each session
- Commit messages include `device:` metadata

## Agent Preferences
- Preferred agent for this project: hermes
- Fallback agents: claude, codex, opencode
- Max parallel tasks per device: 2

## Onboarding
1. Clone the repo
2. Run `project-collab.py init`
3. Run `project-collab.py pull` to fetch issues
4. Run `project-collab.py claim <number>` to claim a task
5. Run `project-collab.py work` to start

## Device Labels
Each device must have a label file:
- Linux: `~/.config/device-label` (content: e.g., `fedora-laptop`)
- Windows: `AppData\Local\hermes\device-label` (content: e.g., `windows-laptop`)
```

## State File Schema

`.hermes-state.json` is git-tracked and updated by all devices:

```json
{
  "updated_at": "2026-09-20 12:00:00 UTC",
  "issues": [
    {
      "number": 1,
      "title": "Fix authentication bug",
      "status": "unclaimed|claimed|in_progress|done",
      "assigned_to": "fedora-laptop",
      "agent": "claude",
      "branch": "feature/1-fix-auth-bug",
      "labels": ["bug", "high-priority"],
      "claimed_at": "2026-09-20 11:30:00 UTC",
      "completed_at": null,
      "pr_created": false
    }
  ],
  "discussions": [],
  "project_items": [],
  "devices": {
    "fedora-laptop": {
      "agent": "hermes",
      "current_task": 1,
      "completed": [],
      "last_sync": "2026-09-20 12:00:00 UTC"
    }
  }
}
```
