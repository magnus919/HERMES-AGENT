# HERMES-AGENT

**Private backup dan migration repository untuk Hermes Agent — fully autonomous sync.**

---

## Konsep

Repo ini dirancang untuk **device-independent deployment**:

1. **Di device ini (source):** Setiap perubahan yang saya buat langsung auto-commit dan push ke GitHub
2. **Di device baru:** Tarik repo ini → jalanin satu script → langsung "engkau tahu siapa kamu"

Repositori ini adalah **source of truth** untuk:
- Identity & memory (siapa saya, siapa Master Faris)
- Skills (87+ skills siap pakai)
- Config (channel integrations, credentials)
- Cron jobs (auto-backup, daily digest, social scan)
- External integrations (ClawTeam, x-cli, repliz-api, dll)

---

## What Gets Backed Up

| Component | Path di Snapshot | Description |
|-----------|------------------|-------------|
| Memory | `snapshot/hermes/memories/` | Identity, user profile, learned facts |
| Skills | `snapshot/hermes/skills/` | 87+ skills (coding, AI, media, dll) |
| Config | `snapshot/hermes/config.yaml` | Hermes main config |
| Auth | `snapshot/hermes/auth.json` | Channel authentications |
| Env | `snapshot/hermes/.env` | API keys & secrets (masked) |
| Cron | `snapshot/hermes/cron/` | Scheduled jobs config |
| Pairing | `snapshot/hermes/pairing/` | Device pairing data |
| ClawTeam | GitHub (latest) | Installed via `restore_hermes_snapshot.py` |
| x-cli | `snapshot/config/x-cli/.env` | X/Twitter credentials |
| himalaya | `snapshot/config/himalaya/` | Email CLI config |

---

## Auto-Sync (Device Ini)

Setiap perubahan yang saya buat langsung di-commit dan di-push:

```
Cron Job: sync-hermes-agent-backup (every 30 min)
  → bash scripts/auto_commit.sh
    → sync_hermes_snapshot.py
    → git add + commit + push
```

**Apa yang trigger commit:**
- Skill diupdate/install
- Memory changed
- Config changed
- Cron job created/modified
- New integration configured

**Yang TIDAK di-commit (excluded):**
- Session transcripts
- Logs
- Caches
- `state.db` (Hermes runtime database)
- Files dengan secrets (`.git-credentials`, dll)

---

## Restore di Device Baru (Fully Autonomous)

### Prerequisites
- Python ≥3.10
- `git`
- `tmux` (untuk ClawTeam)
- `uv` (optional, untuk x-cli)

### Steps

**1. Clone repo ini:**
```bash
git clone https://github.com/azmiariffaris/HERMES-AGENT.git
cd HERMES-AGENT
```

**2. Jalankan setup script:**
```bash
python3 scripts/first_time_setup.py
```

Script ini akan:
- ✓ Restore semua files (memories, skills, config, auth)
- ✓ Install ClawTeam v0.3.0 dari GitHub
- ✓ Setup auto-backup cron job
- ✓ Print next steps

**3. Restart Hermes:**
```bash
hermes restart
# atau
sudo systemctl restart hermes
```

**4. Verify:**
```bash
clawteam --version   # Should show v0.3.0
oh team discover     # Should show teams
hermes ping          # Should respond
```

---

## Manual Commands

### Sync & Backup (device ini)
```bash
cd ~/HERMES-AGENT
bash scripts/auto_commit.sh
```

### Restore dari Snapshot
```bash
cd ~/HERMES-AGENT
python3 scripts/restore_hermes_snapshot.py
```

### Force Restore (device ini, timpa semua)
```bash
cd ~/HERMES-AGENT
python3 scripts/first_time_setup.py --force-restore
```

### Check Auto-Backup Status
```bash
hermes cron list | grep sync-hermes-agent-backup
```

---

## Repo Structure

```
HERMES-AGENT/
├── README.md                      # This file
├── .gitignore                     # Excludes sensitive/ephemeral files
├── scripts/
│   ├── first_time_setup.py        # NEW DEVICE: run this first
│   ├── restore_hermes_snapshot.py # Restore all Hermes state
│   ├── sync_hermes_snapshot.py    # Sync .hermes → snapshot/
│   ├── auto_commit.sh             # Commit & push changes
│   └── cron_prompt.txt            # Prompt for auto-backup cron
├── snapshot/                       # Synced Hermes state
│   └── hermes/
│       ├── memories/              # Identity & user profile
│       ├── skills/                # All skills
│       ├── config.yaml            # Main config
│       ├── .env                   # Secrets
│       ├── auth.json              # Channel auth
│       ├── cron/                  # Cron job configs
│       └── ...
├── config/                        # External configs
│   ├── x-cli/.env
│   └── himalaya/
├── reports/                       # System inventory (auto-generated)
└── system/                        # System-level configs
    └── apache2/sites-available/
```

---

## ClawTeam Integration

ClawTeam adalah **primary skill** untuk multi-agent coordination. Setiap tugas yang melibatkan banyak agent akan menggunakan ClawTeam terlebih dahulu.

- **Version:** v0.3.0 (latest dari GitHub)
- **Installed:** Di `~/clawteam-venv/`
- **Symlinked:** `/usr/local/bin/{clawteam, oh}`
- **Config:** `~/.clawteam/config.json`

Restore script otomatis menginstall ClawTeam dari GitHub.

---

## Cron Jobs (Auto-Synced)

| Job | Schedule | Purpose |
|-----|----------|---------|
| `sync-hermes-agent-backup` | Every 30 min | Auto-commit changes to GitHub |
| `morning-ai-digest-daily-0800-wib` | 08:00 WIB | Daily AI digest to Master Faris |
| `nightly-ai-social-scan` | 23:05 WIB | Indonesian AI social media scan |
| `nightly-ai-web-scan` | 23:20 WIB | Indonesian AI web scan |

---

## Security Notes

- Repo adalah **PRIVATE** — jangan di-push ke public
- `.env` dan `auth.json` berisi credentials yang sudah di-mask
- `~/.git-credentials` TIDAK di-backup (mengandung GitHub PAT)
- Selalu gunakan `chmod 600` untuk file credentials

---

## Device Switching Workflow

```
Device A (source)
  ↓ every change I make
  ↓ auto_commit.sh → GitHub
  ↓

GitHub: azmiariffaris/HERMES-AGENT

  ↓ pull
  ↓

Device B (new)
  ↓ first_time_setup.py
  ↓ restore + install ClawTeam
  ↓

Device B is now identical to Device A
  → Same identity (memory)
  → Same skills
  → Same config
  → Same cron jobs
  → Same integrations
```

---

## Troubleshooting

**Restore fails with permission error:**
```bash
sudo python3 scripts/first_time_setup.py
```

**ClawTeam not working after restore:**
```bash
clawteam --version
oh team discover
# Jika error, reinstall:
~/clawteam-venv/bin/pip install -e "git+https://github.com/HKUDS/ClawTeam.git#egg=clawteam"
```

**Cron job not running:**
```bash
hermes cron list
hermes cron run sync-hermes-agent-backup
```

---

**Last sync:** `2026-04-20T01:42:08Z` (commit `851257d`)
