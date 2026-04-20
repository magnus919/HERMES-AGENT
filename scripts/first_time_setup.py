#!/usr/bin/env python3
"""
First-time setup script for HERMES-AGENT repo.

When a new Hermes Agent pulls this repo, run this script to:
1. Detect if Hermes is already installed
2. If not, restore from snapshot
3. Install ClawTeam
4. Set up auto-backup cron job
5. Print instructions for starting Hermes

Usage:
    python3 scripts/first_time_setup.py [--force-restore]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HERMES_DIR = Path.home() / ".hermes"


def run(cmd: list[str], capture=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, text=True)


def check_hermes_installed() -> bool:
    """Check if Hermes is already installed and configured."""
    return HERMES_DIR.exists() and (HERMES_DIR / "config.yaml").exists()


def run_restore() -> dict:
    """Run the restore script."""
    result = run([sys.executable, str(REPO_ROOT / "scripts" / "restore_hermes_snapshot.py")])
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout + result.stderr}


def setup_cron_job() -> dict:
    """Set up the auto-backup cron job."""
    cron_prompt_path = REPO_ROOT / "scripts" / "cron_prompt.txt"
    if not cron_prompt_path.exists():
        return {"status": "cron_prompt_missing"}

    cron_prompt = cron_prompt_path.read_text().strip()

    # Check if cron job already exists
    result = run(["hermes", "cron", "list"], capture=True)
    if "sync-hermes-agent-backup" in result.stdout:
        return {"status": "already_exists"}

    # Create the cron job
    cmd = [
        "hermes", "cron", "create",
        "every 30m",
        f'"{cron_prompt}"',
        "--name", "sync-hermes-agent-backup",
        "--deliver", "local"
    ]
    result = run(cmd)
    if result.returncode == 0:
        return {"status": "created"}
    else:
        return {"status": "failed", "error": result.stderr}


def main():
    force_restore = "--force-restore" in sys.argv
    hermes_installed = check_hermes_installed()

    print("=" * 60)
    print("HERMES-AGENT First-Time Setup")
    print("=" * 60)
    print()

    if hermes_installed and not force_restore:
        print("✓ Hermes is already installed.")
        print("  To force restore from snapshot, run with --force-restore")
        print()
        print("Running restore anyway to sync latest changes...")
        print()

    # Step 1: Restore from snapshot
    print("[1/3] Restoring Hermes state from snapshot...")
    restore_result = run_restore()
    print(f"    Restored: {restore_result.get('restored_count', 0)} items")
    if restore_result.get("clawteam_install"):
        ci = restore_result["clawteam_install"]
        print(f"    ClawTeam: {ci.get('version', ci.get('status', 'unknown'))}")
    print()

    # Step 2: Setup cron job
    print("[2/3] Setting up auto-backup cron job...")
    cron_result = setup_cron_job()
    print(f"    Cron: {cron_result.get('status')}")
    print()

    # Step 3: Instructions
    print("[3/3] Next steps:")
    print()
    if not hermes_installed or force_restore:
        print("    1. Restart Hermes gateway:")
        print("       hermes restart")
        print()
        print("    2. Or if Hermes is running as a service:")
        print("       sudo systemctl restart hermes")
        print()
    print("    To verify ClawTeam is working:")
    print("       clawteam --version")
    print("       oh team discover")
    print()
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)

    # Save result to file for debugging
    result_file = REPO_ROOT / "setup_result.json"
    result_file.write_text(json.dumps({
        "hermes_installed": hermes_installed,
        "restore": restore_result,
        "cron": cron_result,
    }, indent=2))
    print(f"\nSetup result saved to: {result_file}")


if __name__ == "__main__":
    main()
