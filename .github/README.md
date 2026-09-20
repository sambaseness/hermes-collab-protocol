# GitHub Actions CI/CD

## Workflows

### CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

| Job | Trigger | Description |
|-----|---------|-------------|
| **validate** | Push/PR to main | Syntax check, lint, YAML validation |
| **build-windows-exe** | Push to main | Builds `hermes-collab-installer.exe` with PyInstaller |
| **build-linux-binary** | Push to main | Builds `hermes-collab-installer` Linux binary |
| **deploy** | Push to main | Verifies all protocol files are present |
| **release** | Tag push | Creates GitHub Release with binaries |
| **notify** | Always (main) | Summary of pipeline results |

## Building the Windows .exe

The CI/CD automatically builds a Windows `.exe` from `installer.py` using PyInstaller:

```bash
pyinstaller --name hermes-collab-installer --onefile --windowed installer.py
```

The `.exe` downloads `project-collab.py`, `SKILL.md`, and `reference-manifest.md` from GitHub — it does NOT install anything by itself. It just runs the install logic.

## Usage

**Windows**: Download `hermes-collab-installer.exe`, double-click to run.
**Linux/macOS**: Download `hermes-collab-installer`, run `chmod +x` then `./hermes-collab-installer`.

The installer:
1. Detects platform (Linux/macOS/Windows)
2. Creates `.config/device-label`
3. Downloads protocol files to `~/.hermes/`
4. Checks dependencies (gh, git, python3, hermes)
5. Offers to install Hermes if missing

## Manual Build

```bash
pip install pyinstaller
pyinstaller --name hermes-collab-installer --onefile --windowed installer.py
```

Output: `dist/hermes-collab-installer.exe`
