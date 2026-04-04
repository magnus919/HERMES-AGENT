---
name: hermes-backup-repo
description: Create and maintain a private GitHub backup repository for Hermes system state, memory, skills, auth, and local integrations, with automatic sync commits.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Hermes, Backup, GitHub, Migration, Memory, Skills, Cron]
    related_skills: [hermes-agent, github-repo-management, github-auth]
---

# Hermes Backup Repo

Use this skill when a user wants a migration / disaster-recovery repository for a Hermes environment.

## Goal

Create a private GitHub repo that versions the important Hermes state needed to migrate to another device or recover from breakage.

## Recommended repo contents

Back up high-value state, not noisy runtime artifacts.

Include:
- `~/.hermes/config.yaml`
- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/memories/`
- `~/.hermes/skills/`
- `~/.hermes/pairing/`
- optional Hermes state directories/files if present: `profiles/`, `cron/`, `plugins/`, `gateway_state.json`, `channel_directory.json`
- important external integrations stored outside `~/.hermes/` (for example `~/.config/himalaya/`, `~/.gitconfig`, `~/.git-credentials`, wrapper scripts in `~/.local/bin/`)

Exclude:
- session transcripts unless the user explicitly wants them
- logs
- caches
- lock files
- `__pycache__`, `.pyc`
- the Hermes source checkout at `~/.hermes/hermes-agent/`

## Layout

Suggested repo structure:

- `README.md`
- `scripts/sync_hermes_snapshot.py`
- `scripts/restore_hermes_snapshot.py`
- `scripts/auto_commit.sh`
- `scripts/cron_prompt.txt`
- `snapshot/...`
- `reports/...`

## Creation flow

1. Verify GitHub authentication.
2. Create a PRIVATE repo via GitHub API or `gh repo create`.
3. Create a local working copy directory named after the repo.
4. Add backup scripts and README.
5. Run the sync script to populate `snapshot/` and `reports/`.
6. Commit and push initial contents.
7. Set up an automatic cron sync job.

## Auto-sync design

Use an `auto_commit.sh` wrapper that:
1. runs the sync script
2. stages only meaningful files first (`.gitignore`, `README.md`, `scripts`, `snapshot`)
3. exits with `No backup changes detected.` if there are no meaningful changes
4. only stages `reports/` after real changes are found
5. commits and pushes

This prevents perpetual commits caused only by regenerated timestamps in reports.

## Cron prompt pattern

Use a self-contained prompt that runs:

```bash
cd /path/to/repo && bash scripts/auto_commit.sh
```

Have the cron return only a short status and never print secrets.

## Verification

- `bash scripts/auto_commit.sh` should push when there are real changes
- running it again immediately should print `No backup changes detected.`
- confirm `git status --short` is clean after the second run

## Pitfalls

- Make the repo private by default because it contains secrets.
- If reports are always regenerated with timestamps, the auto-commit script must avoid committing report-only churn.
- Some integrations live outside `~/.hermes/`; explicitly include them if they matter for migration.
- Hermes cron state may appear later under `~/.hermes/cron/`; include it when present so backup automation configuration is also migrated.
