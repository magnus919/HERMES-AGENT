---
name: clawteam
description: >
  ClawTeam: Agent Swarm Intelligence — multi-agent coordination framework.
  Gunakan skill ini ketika: mengkoordinasikan tugas multi-agent, mengelola swarm,
  spawning worker agents, task management, dan inter-agent messaging.
  ClawTeam provides: team management, task delegation, inbox messaging,
  board monitoring, git worktree workspace isolation, dan P2P transport.
version: 0.2.0
---

# ClawTeam — Agent Swarm Intelligence

ClawTeam adalah framework multi-agent coordination berbasis CLI. Gunakan untuk mengkoordinasikan
banyak agent secara otonom.

## Setup Environment

```bash
# Commands tersedia sebagai 'clawteam' atau 'oh' (alias)
export PATH="/home/ubuntu/clawteam-venv/bin:$PATH"
export CLAWTEAM_DATA_DIR=/home/ubuntu/.clawteam

# Verifikasi installation
clawteam --version   # clawteam v0.2.0
oh --version
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Team** | Group of agents led by a leader |
| **Leader** | Main agent yang mengkoordinasikan swarm |
| **Worker** | Sub-agents yang ditugaskan tugas specific |
| **Task** | Unit kerja yang di-assign ke worker |
| **Inbox** | Message queue antar-agent |
| **Board** | Kanban-style monitoring dashboard |
| **Workspace** | Git worktree isolation per agent |

## Command Reference

### Team Management

```bash
# Create team
oh team spawn-team <team-name> -d "<description>"

# List all teams
oh team discover

# Team status
oh team status <team-name>

# Delete team
oh team cleanup <team-name>

# Save/restore team snapshot
oh team snapshot <team-name>
oh team restore <team-name> <snapshot-id>
```

### Task Management

```bash
# Create task
oh task create <team> "<subject>" -o <owner> -p <priority>

# List tasks
oh task list <team> --status pending --owner <owner>

# Update task
oh task update <team> <task-id> --status completed

# Wait for tasks
oh task wait <team> --timeout 300 --poll-interval 5
```

### Spawning Agents

```bash
# Spawn worker (default: tmux backend, claude command)
oh spawn --team <team> --agent-name <name> --task "<task description>"

# Spawn with subprocess backend (no GUI needed)
oh spawn subprocess --team <team> --agent-name <name> --task "<task>"

# Spawn with custom command
oh spawn tmux codex --team <team> --agent-name <name> --task "<task>"
```

### Inbox / Messaging

```bash
# Send message to agent
oh inbox send <team> <to-agent> "<message>"

# Broadcast to all
oh inbox broadcast <team> "<message>"

# Receive messages
oh inbox receive <team>

# Peek without consuming
oh inbox peek <team>
```

### Board / Monitoring

```bash
# Terminal kanban
oh board show <team>

# Auto-refresh
oh board live <team> --interval 3

# Attach to tmux view
oh board attach <team>

# Web UI
oh board serve --port 8080
```

### Workspace (Git Worktree)

```bash
# List workspaces
oh workspace list <team>

# Checkpoint (auto-commit)
oh workspace checkpoint <team> <agent>

# Merge back to main
oh workspace merge <team> <agent>

# Cleanup
oh workspace cleanup <team> <agent>
```

### Lifecycle / Shutdown

```bash
# Request shutdown
oh lifecycle request-shutdown <team> <agent> --reason "done"

# Approve shutdown
oh lifecycle approve-shutdown <team> <request-id> <agent>

# Check idle agents
oh lifecycle idle <team>
```

### Launch from Template

```bash
# Available templates: code-review, hedge-fund, research-paper, software-dev, strategy-room
oh launch <template> --goal "<project goal>" --team-name <team>

# Example
oh launch software-dev --goal "Build a REST API" --team dev-team
```

### Configuration

```bash
# Show config
oh config show

# Set option
oh config set <key> <value>

# Available options:
#   data_dir, default_team, transport (file/p2p), workspace (auto/always/never),
#   default_backend (tmux/subprocess), skip_permissions, timezone
```

## Workflow Pattern — Otomatis dari Goal

Ketika Master Faris memberikan goal tinggi-level:

1. **Analisa goal** → tentukan apakah perlu multi-agent atau single agent
2. **Jika multi-agent:**
   - `oh team spawn-team <team> -d "<goal>"`
   - `oh task create <team> "<subtask>" -o <worker> -p <priority>` (untuk setiap subtask)
   - `oh spawn --team <team> --agent-name <worker> --task "<task>"` (spawn workers)
   - `oh board show <team>` atau `oh task wait <team> --timeout <seconds>` (monitor)
3. **Report hasil** kembali ke Master Faris

## Default Configuration (Already Set)

```yaml
data_dir: /home/ubuntu/.clawteam
default_backend: tmux
skip_permissions: true
timezone: Asia/Jakarta
transport: file
workspace: auto
```

## Prerequisites

- Python ≥3.10
- tmux 3.4+ (installed at /usr/bin/tmux)
- clawteam v0.2.0 (installed at /home/ubuntu/clawteam-venv/bin/clawteam)
- Default agent command: claude (but can use any CLI agent or subprocess)

## Catatan Penting

- ClawTeam UI (board serve) jalan di port 8080
- Data disimpan di `/home/ubuntu/.clawteam/`
- Transport default: file-based (cocok untuk single machine)
- Untuk multi-machine, gunakan `oh config set transport p2p` (butuh pyzmq)
