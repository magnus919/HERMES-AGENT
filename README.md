# HERMES-AGENT

Private backup and migration repository for this Hermes Agent environment.

## Purpose

This repo stores the important Hermes system state needed for:
- recovering from errors
- migrating Hermes from one device to another
- preserving memory, config, auth, skills, and key local integrations
- keeping a versioned history of system changes over time

## What gets backed up

The sync process snapshots selected high-value state into `snapshot/`, including:
- `~/.hermes/config.yaml`
- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/memories/`
- `~/.hermes/skills/`
- `~/.hermes/pairing/`
- optional Hermes state files such as gateway/channel/profile/cron/plugin directories when present
- `~/.config/himalaya/` Gmail CLI config used in this environment
- `/etc/apache2/sites-available/assetloan.my.id.conf` deployment vhost configuration
- `~/.gitconfig`
- `~/.git-credentials`
- `~/.local/bin/repliz-api`

## What is intentionally not backed up

To keep this repo useful for migration instead of noisy runtime history, the snapshot excludes ephemeral data such as:
- session transcripts
- logs
- caches
- lock files
- `__pycache__`
- `.pyc` files
- the local Hermes source checkout at `~/.hermes/hermes-agent/`

## Important

This repository contains sensitive data and credentials.
It is intended to remain private.

## Main scripts

- `scripts/sync_hermes_snapshot.py` — refresh the snapshot and system reports
- `scripts/auto_commit.sh` — sync, commit changes, and push to GitHub
- `scripts/restore_hermes_snapshot.py` — restore the snapshot onto another machine
- `scripts/cron_prompt.txt` — reusable prompt for recreating the Hermes auto-sync cron job on another machine

## Manual sync

```bash
cd ~/HERMES-AGENT
python3 scripts/sync_hermes_snapshot.py
```

## Manual commit + push

```bash
cd ~/HERMES-AGENT
bash scripts/auto_commit.sh
```

## Restore on another machine

1. Clone this private repo to the new machine.
2. Run Hermes installation normally if Hermes is not installed yet.
3. Run:

```bash
cd HERMES-AGENT
python3 scripts/restore_hermes_snapshot.py
```

4. Restart Hermes / gateway after restore.
5. Recreate the automatic backup cron job:

```bash
cd HERMES-AGENT
hermes cron create "every 30m" "$(cat scripts/cron_prompt.txt)" --name sync-hermes-agent-backup --deliver local
```

## Auto-sync status on this machine

An automatic Hermes cron job is enabled to run the backup every 30 minutes.
Current job name: `sync-hermes-agent-backup`

## Reports

Every sync refreshes `reports/` with inventory and manifest files to help troubleshooting and auditing.
